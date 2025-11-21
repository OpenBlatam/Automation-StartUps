"""
Módulo de Enrutamiento Inteligente Basado en Expertise.

Características:
- Matching de expertise específico de agentes
- Análisis de historial de resolución por categoría
- Score de expertise por agente
- Asignación balanceada considerando expertise
"""
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ExpertiseMatch:
    """Resultado de matching de expertise."""
    agent_id: str
    agent_name: str
    expertise_score: float
    category_match: bool
    subcategory_match: bool
    historical_performance: float
    current_load: int
    max_load: int
    total_score: float
    reasoning: str


class SupportExpertiseRouter:
    """Enrutador basado en expertise de agentes."""
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el enrutador de expertise.
        
        Args:
            db_connection: Conexión a BD
        """
        self.db_connection = db_connection
    
    def get_agent_expertise(
        self,
        agent_id: str
    ) -> Dict[str, Any]:
        """
        Obtiene expertise de un agente.
        
        Args:
            agent_id: ID del agente
            
        Returns:
            Dict con información de expertise
        """
        if not self.db_connection:
            return {}
        
        try:
            cursor = self.db_connection.cursor()
            
            # Obtener especialidades del agente
            cursor.execute("""
                SELECT 
                    specialties,
                    department,
                    max_concurrent_tickets,
                    current_active_tickets
                FROM support_agents
                WHERE agent_id = %s
            """, (agent_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                return {}
            
            specialties, department, max_load, current_load = row
            
            # Obtener historial de resolución por categoría
            cursor.execute("""
                SELECT 
                    category,
                    COUNT(*) as resolved_count,
                    AVG(time_to_resolution_minutes) as avg_resolution_time,
                    AVG(customer_satisfaction_score) as avg_satisfaction
                FROM support_tickets
                WHERE assigned_agent_id = %s
                AND status = 'resolved'
                GROUP BY category
                ORDER BY resolved_count DESC
            """, (agent_id,))
            
            category_performance = {}
            for cat_row in cursor.fetchall():
                category, count, avg_time, avg_sat = cat_row
                category_performance[category] = {
                    "resolved_count": count,
                    "avg_resolution_time": avg_time or 0,
                    "avg_satisfaction": avg_sat or 0
                }
            
            cursor.close()
            
            return {
                "specialties": specialties or [],
                "department": department,
                "max_load": max_load,
                "current_load": current_load,
                "category_performance": category_performance
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo expertise de agente {agent_id}: {e}")
            return {}
    
    def calculate_expertise_score(
        self,
        agent_expertise: Dict[str, Any],
        category: str,
        subcategory: Optional[str] = None
    ) -> float:
        """
        Calcula score de expertise para una categoría.
        
        Args:
            agent_expertise: Expertise del agente
            category: Categoría del ticket
            subcategory: Subcategoría del ticket
            
        Returns:
            Score de expertise (0.0 a 1.0)
        """
        score = 0.0
        
        # Match por especialidades
        specialties = agent_expertise.get("specialties", [])
        if category in specialties:
            score += 0.4
        if subcategory and subcategory in specialties:
            score += 0.2
        
        # Match por historial de resolución
        category_perf = agent_expertise.get("category_performance", {})
        if category in category_perf:
            perf = category_perf[category]
            resolved_count = perf.get("resolved_count", 0)
            avg_satisfaction = perf.get("avg_satisfaction", 0)
            
            # Más tickets resueltos = más experiencia
            if resolved_count > 10:
                score += 0.2
            elif resolved_count > 5:
                score += 0.1
            
            # Alta satisfacción = mejor expertise
            if avg_satisfaction >= 4.5:
                score += 0.2
            elif avg_satisfaction >= 4.0:
                score += 0.1
        
        # Match por departamento
        department = agent_expertise.get("department", "")
        if category == department:
            score += 0.1
        
        return min(1.0, score)
    
    def find_best_agent(
        self,
        category: str,
        subcategory: Optional[str] = None,
        department: Optional[str] = None,
        priority: str = "medium",
        exclude_agent_id: Optional[str] = None
    ) -> Optional[ExpertiseMatch]:
        """
        Encuentra el mejor agente para un ticket basado en expertise.
        
        Args:
            category: Categoría del ticket
            subcategory: Subcategoría del ticket
            department: Departamento requerido
            priority: Prioridad del ticket
            exclude_agent_id: ID de agente a excluir
            
        Returns:
            ExpertiseMatch con mejor agente o None
        """
        if not self.db_connection:
            return None
        
        try:
            cursor = self.db_connection.cursor()
            
            # Construir query base
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
            """
            params = []
            
            # Filtrar por departamento si se especifica
            if department:
                query += " AND department = %s"
                params.append(department)
            
            # Excluir agente si se especifica
            if exclude_agent_id:
                query += " AND agent_id != %s"
                params.append(exclude_agent_id)
            
            # Filtrar por especialidades si hay
            if category:
                query += " AND (specialties && %s OR department = %s)"
                params.append([category])
                params.append(category)
            
            cursor.execute(query, params)
            
            candidates = []
            for row in cursor.fetchall():
                agent_id, agent_name, email, dept, specialties, max_load, current_load = row
                
                # Obtener expertise completo
                agent_expertise = self.get_agent_expertise(agent_id)
                if not agent_expertise:
                    # Si no hay datos, usar valores básicos
                    agent_expertise = {
                        "specialties": specialties or [],
                        "department": dept,
                        "max_load": max_load,
                        "current_load": current_load,
                        "category_performance": {}
                    }
                
                # Calcular score de expertise
                expertise_score = self.calculate_expertise_score(
                    agent_expertise,
                    category,
                    subcategory
                )
                
                # Calcular score de carga de trabajo
                load_ratio = current_load / max_load if max_load > 0 else 1.0
                load_score = 1.0 - load_ratio  # Menos carga = mejor score
                
                # Calcular performance histórica
                cat_perf = agent_expertise.get("category_performance", {})
                perf_score = 0.5  # Base
                if category in cat_perf:
                    perf = cat_perf[category]
                    # Más tickets resueltos y mejor satisfacción = mejor score
                    if perf.get("resolved_count", 0) > 5:
                        perf_score += 0.3
                    if perf.get("avg_satisfaction", 0) >= 4.0:
                        perf_score += 0.2
                
                # Score total (ponderado)
                # Expertise: 50%, Load: 30%, Performance: 20%
                total_score = (
                    expertise_score * 0.5 +
                    load_score * 0.3 +
                    perf_score * 0.2
                )
                
                # Verificar matches
                category_match = category in (specialties or []) or category == dept
                subcategory_match = subcategory in (specialties or []) if subcategory else False
                
                # Construir reasoning
                reasoning_parts = []
                if category_match:
                    reasoning_parts.append(f"Match de categoría: {category}")
                if subcategory_match:
                    reasoning_parts.append(f"Match de subcategoría: {subcategory}")
                if expertise_score > 0.5:
                    reasoning_parts.append(f"Alta expertise: {expertise_score:.2f}")
                if load_ratio < 0.5:
                    reasoning_parts.append(f"Baja carga: {current_load}/{max_load}")
                
                reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Asignación general"
                
                candidates.append(ExpertiseMatch(
                    agent_id=agent_id,
                    agent_name=agent_name,
                    expertise_score=expertise_score,
                    category_match=category_match,
                    subcategory_match=subcategory_match,
                    historical_performance=perf_score,
                    current_load=current_load,
                    max_load=max_load,
                    total_score=total_score,
                    reasoning=reasoning
                ))
            
            cursor.close()
            
            # Ordenar por score total y seleccionar mejor
            if candidates:
                candidates.sort(key=lambda x: x.total_score, reverse=True)
                return candidates[0]
            
            return None
            
        except Exception as e:
            logger.error(f"Error buscando mejor agente: {e}")
            return None
    
    def assign_by_expertise(
        self,
        ticket_id: str,
        category: str,
        subcategory: Optional[str] = None,
        department: Optional[str] = None,
        priority: str = "medium"
    ) -> Optional[ExpertiseMatch]:
        """
        Asigna un ticket a un agente basado en expertise.
        
        Args:
            ticket_id: ID del ticket
            category: Categoría del ticket
            subcategory: Subcategoría del ticket
            department: Departamento requerido
            priority: Prioridad del ticket
            
        Returns:
            ExpertiseMatch con agente asignado o None
        """
        # Buscar mejor agente
        best_match = self.find_best_agent(
            category=category,
            subcategory=subcategory,
            department=department,
            priority=priority
        )
        
        if not best_match:
            return None
        
        # Asignar ticket
        if self.db_connection:
            try:
                cursor = self.db_connection.cursor()
                
                cursor.execute("""
                    UPDATE support_tickets
                    SET assigned_agent_id = %s,
                        assigned_agent_name = %s,
                        assigned_department = %s,
                        routing_reason = %s,
                        status = CASE WHEN status = 'open' THEN 'assigned' ELSE status END,
                        updated_at = NOW()
                    WHERE ticket_id = %s
                """, (
                    best_match.agent_id,
                    best_match.agent_name,
                    department or best_match.category_match,
                    best_match.reasoning,
                    ticket_id
                ))
                
                # Actualizar carga del agente
                cursor.execute("""
                    UPDATE support_agents
                    SET current_active_tickets = current_active_tickets + 1,
                        updated_at = NOW()
                    WHERE agent_id = %s
                """, (best_match.agent_id,))
                
                # Registrar en historial
                cursor.execute("""
                    INSERT INTO support_ticket_history (
                        ticket_id,
                        field_changed,
                        old_value,
                        new_value,
                        changed_by,
                        change_reason
                    ) VALUES (
                        %s,
                        'assigned_agent_id',
                        NULL,
                        %s,
                        'system',
                        %s
                    )
                """, (ticket_id, best_match.agent_id, best_match.reasoning))
                
                self.db_connection.commit()
                cursor.close()
                
                return best_match
                
            except Exception as e:
                logger.error(f"Error asignando ticket {ticket_id}: {e}")
                if self.db_connection:
                    self.db_connection.rollback()
                return None
        
        return best_match

