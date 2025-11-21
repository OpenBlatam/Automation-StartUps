"""
Módulo de Enrutamiento Inteligente de Tickets.

Características:
- Enrutamiento basado en reglas configurables
- Asignación automática a agentes disponibles
- Balanceo de carga entre agentes
- Matching de especialidades
"""
import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class RoutingResult:
    """Resultado del enrutamiento."""
    department: str
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    reason: str = ""
    auto_assign: bool = False


class SupportRouter:
    """Enrutador inteligente de tickets de soporte."""
    
    # Mapeo de categorías a departamentos por defecto
    DEFAULT_CATEGORY_DEPARTMENTS = {
        "billing": "billing",
        "payment": "billing",
        "refund": "billing",
        "technical": "technical",
        "bug": "technical",
        "error": "technical",
        "sales": "sales",
        "demo": "sales",
        "pricing": "sales",
        "account": "support",
        "general": "support",
        "security": "security",
    }
    
    # Mapeo de prioridades a departamentos (para escalación)
    PRIORITY_DEPARTMENTS = {
        "critical": "technical",  # Criticales suelen ser técnicos
        "urgent": "support",
        "high": "support",
        "medium": "support",
        "low": "support",
    }
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el enrutador.
        
        Args:
            db_connection: Conexión a BD para consultar reglas y agentes
        """
        self.db_connection = db_connection
    
    def get_routing_rules(self) -> List[Dict[str, Any]]:
        """
        Obtiene las reglas de enrutamiento activas desde la BD.
        
        Returns:
            Lista de reglas ordenadas por priority_order
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            cursor.execute("""
                SELECT 
                    rule_name,
                    priority_order,
                    conditions,
                    target_department,
                    target_specialties,
                    auto_assign
                FROM support_routing_rules
                WHERE is_active = true
                ORDER BY priority_order ASC
            """)
            
            rules = []
            for row in cursor.fetchall():
                rules.append({
                    "name": row[0],
                    "priority": row[1],
                    "conditions": row[2],
                    "department": row[3],
                    "specialties": row[4] if row[4] else [],
                    "auto_assign": row[5]
                })
            
            cursor.close()
            return rules
            
        except Exception as e:
            logger.error(f"Error obteniendo reglas de enrutamiento: {e}", exc_info=True)
            return []
    
    def evaluate_routing_rule(
        self,
        rule: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> bool:
        """
        Evalúa si un ticket cumple con las condiciones de una regla.
        
        Args:
            rule: Regla a evaluar
            ticket_data: Datos del ticket
            
        Returns:
            True si la regla aplica
        """
        conditions = rule.get("conditions", {})
        
        # Evaluar cada condición
        for key, value in conditions.items():
            ticket_value = ticket_data.get(key)
            
            # Si la condición es una lista, verificar si el valor está en la lista
            if isinstance(value, list):
                if ticket_value not in value:
                    return False
            # Si es un string, verificar igualdad (case-insensitive)
            elif isinstance(value, str):
                if str(ticket_value).lower() != value.lower():
                    return False
            # Si es un dict, puede tener operadores (contains, starts_with, etc.)
            elif isinstance(value, dict):
                if not self._evaluate_condition_dict(key, value, ticket_data):
                    return False
            else:
                if ticket_value != value:
                    return False
        
        return True
    
    def _evaluate_condition_dict(
        self,
        field: str,
        condition: Dict[str, Any],
        ticket_data: Dict[str, Any]
    ) -> bool:
        """Evalúa condiciones complejas."""
        ticket_value = str(ticket_data.get(field, "")).lower()
        
        # Contains
        if "contains" in condition:
            return condition["contains"].lower() in ticket_value
        
        # Starts with
        if "starts_with" in condition:
            return ticket_value.startswith(condition["starts_with"].lower())
        
        # In array
        if "in" in condition:
            return ticket_value in [str(v).lower() for v in condition["in"]]
        
        return False
    
    def find_available_agent(
        self,
        department: str,
        specialties: Optional[List[str]] = None,
        exclude_agent_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Encuentra un agente disponible en el departamento.
        
        Args:
            department: Departamento requerido
            specialties: Especialidades requeridas
            exclude_agent_id: ID de agente a excluir
            
        Returns:
            Dict con información del agente o None
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Construir query
            query = """
                SELECT 
                    agent_id,
                    agent_name,
                    email,
                    department,
                    specialties,
                    max_concurrent_tickets,
                    current_active_tickets
                FROM support_agents
                WHERE is_available = true
                AND department = %s
            """
            params = [department]
            
            if exclude_agent_id:
                query += " AND agent_id != %s"
                params.append(exclude_agent_id)
            
            # Si hay especialidades requeridas, filtrar por ellas
            if specialties:
                query += " AND specialties && %s"
                params.append(specialties)
            
            # Ordenar por carga de trabajo (menos tickets activos primero)
            query += """
                ORDER BY 
                    CASE 
                        WHEN current_active_tickets < max_concurrent_tickets THEN 0
                        ELSE 1
                    END,
                    current_active_tickets ASC,
                    agent_id ASC
                LIMIT 1
            """
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row:
                agent = {
                    "agent_id": row[0],
                    "agent_name": row[1],
                    "email": row[2],
                    "department": row[3],
                    "specialties": row[4] if row[4] else [],
                    "max_concurrent_tickets": row[5],
                    "current_active_tickets": row[6]
                }
                cursor.close()
                return agent
            
            cursor.close()
            return None
            
        except Exception as e:
            logger.error(f"Error buscando agente disponible: {e}", exc_info=True)
            return None
    
    def route_ticket(
        self,
        category: Optional[str],
        priority: str,
        tags: Optional[List[str]],
        subject: Optional[str],
        description: str,
        customer_email: str,
        customer_id: Optional[str] = None
    ) -> RoutingResult:
        """
        Enruta un ticket a un departamento y posiblemente a un agente.
        
        Args:
            category: Categoría del ticket
            priority: Prioridad del ticket
            tags: Tags del ticket
            subject: Asunto
            description: Descripción
            customer_email: Email del cliente
            customer_id: ID del cliente
            
        Returns:
            RoutingResult con departamento y agente asignado
        """
        # Preparar datos del ticket para evaluación
        ticket_data = {
            "category": category or "general",
            "priority": priority,
            "tags": tags or [],
            "subject": subject or "",
            "description": description,
            "customer_email": customer_email,
        }
        
        # Intentar aplicar reglas de enrutamiento
        rules = self.get_routing_rules()
        matched_rule = None
        
        for rule in rules:
            if self.evaluate_routing_rule(rule, ticket_data):
                matched_rule = rule
                break
        
        # Determinar departamento
        if matched_rule:
            department = matched_rule["department"]
            auto_assign = matched_rule.get("auto_assign", False)
            specialties = matched_rule.get("specialties", [])
            reason = f"Regla: {matched_rule['name']}"
        elif category and category in self.DEFAULT_CATEGORY_DEPARTMENTS:
            department = self.DEFAULT_CATEGORY_DEPARTMENTS[category]
            auto_assign = False
            specialties = None
            reason = f"Categoría por defecto: {category}"
        else:
            department = self.PRIORITY_DEPARTMENTS.get(priority, "support")
            auto_assign = False
            specialties = None
            reason = f"Enrutamiento por prioridad: {priority}"
        
        # Intentar asignar agente si auto_assign está habilitado
        agent_id = None
        agent_name = None
        
        if auto_assign:
            agent = self.find_available_agent(department, specialties)
            if agent:
                agent_id = agent["agent_id"]
                agent_name = agent["agent_name"]
                reason += f" | Agente asignado automáticamente: {agent_name}"
            else:
                reason += " | No hay agentes disponibles para asignación automática"
        
        return RoutingResult(
            department=department,
            agent_id=agent_id,
            agent_name=agent_name,
            reason=reason,
            auto_assign=auto_assign
        )





