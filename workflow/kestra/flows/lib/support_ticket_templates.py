"""
Sistema de Templates de Tickets y Respuestas Reutilizables.

Permite crear y gestionar templates de respuestas comunes,
con variables dinámicas y categorización.
"""
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import re

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Tipos de template."""
    RESPONSE = "response"
    INITIAL_REPLY = "initial_reply"
    FOLLOW_UP = "follow_up"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"
    CLOSURE = "closure"


class TemplateCategory(Enum):
    """Categorías de templates."""
    TECHNICAL = "technical"
    BILLING = "billing"
    GENERAL = "general"
    PRODUCT = "product"
    ACCOUNT = "account"
    FEATURE_REQUEST = "feature_request"


@dataclass
class TicketTemplate:
    """Template de ticket/respuesta."""
    template_id: str
    title: str
    description: str
    template_type: TemplateType
    category: TemplateCategory
    content: str  # Contenido con variables {{variable_name}}
    variables: List[str]  # Lista de variables usadas
    tags: List[str]
    usage_count: int = 0
    success_rate: float = 0.0  # % de satisfacción cuando se usa
    is_active: bool = True
    created_by: Optional[str] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        # Extraer variables del contenido
        if not self.variables:
            self.variables = self._extract_variables()
    
    def _extract_variables(self) -> List[str]:
        """Extraer variables del contenido."""
        pattern = r'\{\{(\w+)\}\}'
        return list(set(re.findall(pattern, self.content)))


class TemplateManager:
    """Gestor de templates."""
    
    def __init__(self, db_connection):
        """Inicializar gestor."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
    
    def create_template(
        self,
        template_id: str,
        title: str,
        description: str,
        template_type: TemplateType,
        category: TemplateCategory,
        content: str,
        tags: Optional[List[str]] = None,
        created_by: Optional[str] = None
    ) -> TicketTemplate:
        """Crear nuevo template."""
        template = TicketTemplate(
            template_id=template_id,
            title=title,
            description=description,
            template_type=template_type,
            category=category,
            content=content,
            variables=[],
            tags=tags or [],
            created_by=created_by
        )
        
        # Guardar en BD
        query = """
            INSERT INTO support_ticket_templates (
                template_id, title, description, template_type, category,
                content, variables, tags, created_by, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (template_id) DO UPDATE SET
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                content = EXCLUDED.content,
                variables = EXCLUDED.variables,
                tags = EXCLUDED.tags,
                updated_at = NOW()
        """
        
        import json
        with self.db.cursor() as cur:
            cur.execute(query, [
                template_id, title, description, template_type.value, category.value,
                content, json.dumps(template.variables), json.dumps(template.tags),
                created_by, template.created_at
            ])
            self.db.commit()
        
        return template
    
    def get_template(self, template_id: str) -> Optional[TicketTemplate]:
        """Obtener template por ID."""
        query = """
            SELECT template_id, title, description, template_type, category,
                   content, variables, tags, usage_count, success_rate,
                   is_active, created_by, created_at, updated_at
            FROM support_ticket_templates
            WHERE template_id = %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [template_id])
            row = cur.fetchone()
        
        if not row:
            return None
        
        import json
        return TicketTemplate(
            template_id=row[0],
            title=row[1],
            description=row[2],
            template_type=TemplateType(row[3]),
            category=TemplateCategory(row[4]),
            content=row[5],
            variables=json.loads(row[6]) if row[6] else [],
            tags=json.loads(row[7]) if row[7] else [],
            usage_count=row[8] or 0,
            success_rate=float(row[9]) if row[9] else 0.0,
            is_active=row[10],
            created_by=row[11],
            created_at=row[12],
            updated_at=row[13]
        )
    
    def search_templates(
        self,
        template_type: Optional[TemplateType] = None,
        category: Optional[TemplateCategory] = None,
        tags: Optional[List[str]] = None,
        search_text: Optional[str] = None,
        limit: int = 20
    ) -> List[TicketTemplate]:
        """Buscar templates."""
        query = """
            SELECT template_id, title, description, template_type, category,
                   content, variables, tags, usage_count, success_rate,
                   is_active, created_by, created_at, updated_at
            FROM support_ticket_templates
            WHERE is_active = true
        """
        params = []
        
        if template_type:
            query += " AND template_type = %s"
            params.append(template_type.value)
        
        if category:
            query += " AND category = %s"
            params.append(category.value)
        
        if tags:
            query += " AND tags && %s"
            import json
            params.append(json.dumps(tags))
        
        if search_text:
            query += " AND (title ILIKE %s OR description ILIKE %s OR content ILIKE %s)"
            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])
        
        query += " ORDER BY usage_count DESC, success_rate DESC LIMIT %s"
        params.append(limit)
        
        with self.db.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()
        
        import json
        templates = []
        for row in rows:
            templates.append(TicketTemplate(
                template_id=row[0],
                title=row[1],
                description=row[2],
                template_type=TemplateType(row[3]),
                category=TemplateCategory(row[4]),
                content=row[5],
                variables=json.loads(row[6]) if row[6] else [],
                tags=json.loads(row[7]) if row[7] else [],
                usage_count=row[8] or 0,
                success_rate=float(row[9]) if row[9] else 0.0,
                is_active=row[10],
                created_by=row[11],
                created_at=row[12],
                updated_at=row[13]
            ))
        
        return templates
    
    def render_template(
        self,
        template_id: str,
        variables: Dict[str, Any]
    ) -> str:
        """Renderizar template con variables."""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template {template_id} no encontrado")
        
        content = template.content
        
        # Reemplazar variables
        for var_name, var_value in variables.items():
            placeholder = f"{{{{{var_name}}}}}"
            content = content.replace(placeholder, str(var_value))
        
        # Verificar variables no reemplazadas
        remaining_vars = re.findall(r'\{\{(\w+)\}\}', content)
        if remaining_vars:
            self.logger.warning(f"Variables no reemplazadas: {remaining_vars}")
        
        return content
    
    def suggest_templates(
        self,
        ticket_category: str,
        ticket_subject: str,
        ticket_description: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Sugerir templates relevantes para un ticket."""
        # Buscar por categoría
        category_map = {
            "technical": TemplateCategory.TECHNICAL,
            "billing": TemplateCategory.BILLING,
            "product": TemplateCategory.PRODUCT,
            "account": TemplateCategory.ACCOUNT
        }
        
        category = category_map.get(ticket_category, TemplateCategory.GENERAL)
        
        # Buscar templates
        templates = self.search_templates(
            category=category,
            search_text=ticket_subject,
            limit=limit * 2
        )
        
        # Calcular relevancia
        scored = []
        for template in templates:
            score = 0.0
            
            # Score por categoría
            if template.category == category:
                score += 10.0
            
            # Score por palabras clave en título
            subject_lower = ticket_subject.lower()
            if any(word in subject_lower for word in template.title.lower().split()):
                score += 5.0
            
            # Score por uso
            score += template.usage_count * 0.1
            
            # Score por éxito
            score += template.success_rate * 0.5
            
            scored.append({
                "template": template,
                "score": score,
                "relevance": "high" if score > 15 else "medium" if score > 10 else "low"
            })
        
        # Ordenar por score
        scored.sort(key=lambda x: x["score"], reverse=True)
        
        return [
            {
                "template_id": item["template"].template_id,
                "title": item["template"].title,
                "description": item["template"].description,
                "preview": item["template"].content[:200] + "...",
                "score": item["score"],
                "relevance": item["relevance"]
            }
            for item in scored[:limit]
        ]
    
    def record_template_usage(
        self,
        template_id: str,
        ticket_id: str,
        satisfaction_score: Optional[float] = None
    ):
        """Registrar uso de template."""
        query = """
            UPDATE support_ticket_templates
            SET usage_count = usage_count + 1,
                updated_at = NOW()
            WHERE template_id = %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [template_id])
            
            # Actualizar success rate si hay satisfacción
            if satisfaction_score is not None:
                update_query = """
                    UPDATE support_ticket_templates
                    SET success_rate = (
                        (success_rate * (usage_count - 1) + %s) / usage_count
                    )
                    WHERE template_id = %s
                """
                cur.execute(update_query, [satisfaction_score, template_id])
            
            self.db.commit()
        
        # Registrar en tabla de uso
        usage_query = """
            INSERT INTO support_template_usage (
                template_id, ticket_id, satisfaction_score, used_at
            ) VALUES (%s, %s, %s, %s)
        """
        
        with self.db.cursor() as cur:
            cur.execute(usage_query, [
                template_id, ticket_id, satisfaction_score, datetime.now()
            ])
            self.db.commit()
    
    def get_template_statistics(self, template_id: str) -> Dict[str, Any]:
        """Obtener estadísticas de un template."""
        template = self.get_template(template_id)
        if not template:
            return {}
        
        # Estadísticas de uso reciente
        query = """
            SELECT 
                COUNT(*) as total_uses,
                AVG(satisfaction_score) as avg_satisfaction,
                COUNT(*) FILTER (WHERE used_at >= NOW() - INTERVAL '30 days') as uses_last_30d
            FROM support_template_usage
            WHERE template_id = %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [template_id])
            row = cur.fetchone()
        
        return {
            "template_id": template_id,
            "title": template.title,
            "usage_count": template.usage_count,
            "success_rate": template.success_rate,
            "total_uses": row[0] or 0,
            "avg_satisfaction": float(row[1]) if row[1] else 0.0,
            "uses_last_30d": row[2] or 0,
            "variables": template.variables,
            "tags": template.tags
        }


