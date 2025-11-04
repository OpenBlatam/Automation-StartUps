"""
Sistema de Templates Inteligentes y Dinámicos.

Permite crear templates con variables, condicionales y lógica.
"""
import logging
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class TemplateType(Enum):
    """Tipos de templates."""
    EMAIL = "email"
    RESPONSE = "response"
    NOTIFICATION = "notification"
    FAQ = "faq"
    CUSTOM = "custom"


@dataclass
class TemplateVariable:
    """Variable de template."""
    name: str
    value: Any
    format: Optional[str] = None  # 'date', 'currency', 'number', etc.


@dataclass
class IntelligentTemplate:
    """Template inteligente."""
    template_id: str
    name: str
    description: str
    template_type: TemplateType
    content: str  # Template con variables {{variable}} y condicionales {% if %}
    variables: List[str]  # Lista de variables usadas
    is_active: bool = True
    category: Optional[str] = None
    created_by: Optional[str] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TemplateEngine:
    """Motor de templates inteligentes."""
    
    def __init__(self):
        """Inicializa motor de templates."""
        self.templates: Dict[str, IntelligentTemplate] = {}
        self.functions: Dict[str, callable] = {
            "upper": str.upper,
            "lower": str.lower,
            "title": str.title,
            "capitalize": str.capitalize,
            "date": self._format_date,
            "currency": self._format_currency,
            "number": self._format_number
        }
    
    def register_template(self, template: IntelligentTemplate):
        """Registra un template."""
        self.templates[template.template_id] = template
    
    def render(
        self,
        template_id: str,
        context: Dict[str, Any],
        strict: bool = False
    ) -> str:
        """
        Renderiza un template.
        
        Args:
            template_id: ID del template
            context: Contexto con variables
            strict: Si True, falla si falta una variable
            
        Returns:
            Template renderizado
        """
        if template_id not in self.templates:
            raise ValueError(f"Template {template_id} not found")
        
        template = self.templates[template_id]
        
        if not template.is_active:
            raise ValueError(f"Template {template_id} is not active")
        
        # Renderizar template
        rendered = self._render_content(template.content, context, strict)
        
        # Incrementar contador de uso
        template.usage_count += 1
        
        return rendered
    
    def render_with_template(
        self,
        template_content: str,
        context: Dict[str, Any],
        strict: bool = False
    ) -> str:
        """
        Renderiza contenido de template directamente.
        
        Args:
            template_content: Contenido del template
            context: Contexto con variables
            strict: Si True, falla si falta una variable
            
        Returns:
            Contenido renderizado
        """
        return self._render_content(template_content, context, strict)
    
    def _render_content(
        self,
        content: str,
        context: Dict[str, Any],
        strict: bool
    ) -> str:
        """Renderiza contenido con variables y condicionales."""
        # Procesar condicionales primero
        content = self._process_conditionals(content, context, strict)
        
        # Procesar variables
        content = self._process_variables(content, context, strict)
        
        # Procesar funciones
        content = self._process_functions(content, context)
        
        return content
    
    def _process_variables(
        self,
        content: str,
        context: Dict[str, Any],
        strict: bool
    ) -> str:
        """Procesa variables {{variable}}."""
        pattern = r'\{\{(\w+(?:\.\w+)*)(?:\|\s*(\w+))?\}\}'
        
        def replace_var(match):
            var_path = match.group(1)
            function_name = match.group(2)
            
            # Obtener valor de contexto
            value = self._get_nested_value(context, var_path)
            
            if value is None:
                if strict:
                    raise ValueError(f"Variable {var_path} not found in context")
                return match.group(0)  # Mantener original
            
            # Aplicar función si existe
            if function_name and function_name in self.functions:
                value = self.functions[function_name](value)
            
            return str(value)
        
        return re.sub(pattern, replace_var, content)
    
    def _process_conditionals(
        self,
        content: str,
        context: Dict[str, Any],
        strict: bool
    ) -> str:
        """Procesa condicionales {% if condition %}...{% endif %}."""
        pattern = r'\{%\s*if\s+(\w+(?:\.\w+)*)\s*%\}\s*(.*?)\s*\{%\s*endif\s*%\}'  # Simplificado
        pattern_else = r'\{%\s*if\s+(\w+(?:\.\w+)*)\s*%\}\s*(.*?)\s*\{%\s*else\s*%\}\s*(.*?)\s*\{%\s*endif\s*%\}'  # Con else
        
        def replace_conditional(match):
            var_path = match.group(1)
            true_content = match.group(2)
            false_content = match.group(3) if len(match.groups()) > 2 else ""
            
            value = self._get_nested_value(context, var_path)
            
            # Evaluar condición
            if value:
                return true_content
            else:
                return false_content if false_content else ""
        
        # Procesar if/else primero
        content = re.sub(
            r'\{%\s*if\s+(\w+(?:\.\w+)*)\s*%\}\s*(.*?)\s*\{%\s*else\s*%\}\s*(.*?)\s*\{%\s*endif\s*%\}',
            replace_conditional,
            content,
            flags=re.DOTALL
        )
        
        # Procesar if sin else
        content = re.sub(
            r'\{%\s*if\s+(\w+(?:\.\w+)*)\s*%\}\s*(.*?)\s*\{%\s*endif\s*%\}',
            replace_conditional,
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _process_functions(self, content: str, context: Dict[str, Any]) -> str:
        """Procesa funciones especiales."""
        # Implementar funciones adicionales si es necesario
        return content
    
    def _get_nested_value(self, context: Dict[str, Any], path: str) -> Any:
        """Obtiene valor anidado usando notación de punto."""
        parts = path.split(".")
        value = context
        
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            elif hasattr(value, part):
                value = getattr(value, part)
            else:
                return None
            
            if value is None:
                return None
        
        return value
    
    def _format_date(self, value: Any) -> str:
        """Formatea fecha."""
        from datetime import datetime
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d")
        return str(value)
    
    def _format_currency(self, value: Any) -> str:
        """Formatea moneda."""
        try:
            amount = float(value)
            return f"${amount:,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def _format_number(self, value: Any) -> str:
        """Formatea número."""
        try:
            num = float(value)
            return f"{num:,.2f}"
        except (ValueError, TypeError):
            return str(value)
    
    def get_template_by_category(self, category: str) -> List[IntelligentTemplate]:
        """Obtiene templates por categoría."""
        return [
            t for t in self.templates.values()
            if t.category == category and t.is_active
        ]
    
    def search_templates(self, query: str) -> List[IntelligentTemplate]:
        """Busca templates por nombre o descripción."""
        query_lower = query.lower()
        return [
            t for t in self.templates.values()
            if query_lower in t.name.lower() or query_lower in (t.description or "").lower()
        ]


class TemplateBuilder:
    """Constructor de templates."""
    
    @staticmethod
    def create_email_template(
        template_id: str,
        name: str,
        subject: str,
        body: str,
        variables: List[str] = None
    ) -> IntelligentTemplate:
        """Crea template de email."""
        content = f"Subject: {subject}\n\n{body}"
        
        return IntelligentTemplate(
            template_id=template_id,
            name=name,
            description=f"Email template: {name}",
            template_type=TemplateType.EMAIL,
            content=content,
            variables=variables or [],
            category="email"
        )
    
    @staticmethod
    def create_response_template(
        template_id: str,
        name: str,
        content: str,
        variables: List[str] = None
    ) -> IntelligentTemplate:
        """Crea template de respuesta."""
        return IntelligentTemplate(
            template_id=template_id,
            name=name,
            description=f"Response template: {name}",
            template_type=TemplateType.RESPONSE,
            content=content,
            variables=variables or [],
            category="response"
        )


# Ejemplo de uso
if __name__ == "__main__":
    engine = TemplateEngine()
    
    # Crear template
    template = TemplateBuilder.create_response_template(
        template_id="ticket-resolved",
        name="Ticket Resuelto",
        content="""
Hola {{customer.name}},

Tu ticket #{{ticket.id}} ha sido resuelto.

{% if ticket.satisfaction_score %}
Gracias por tu feedback. Tu satisfacción fue: {{ticket.satisfaction_score}}/5
{% endif %}

{% if ticket.resolution_notes %}
Notas de resolución:
{{ticket.resolution_notes}}
{% endif %}

Saludos,
{{agent.name}}
        """,
        variables=["customer.name", "ticket.id", "ticket.satisfaction_score", "ticket.resolution_notes", "agent.name"]
    )
    
    engine.register_template(template)
    
    # Renderizar
    context = {
        "customer": {"name": "Juan Pérez"},
        "ticket": {
            "id": "T-12345",
            "satisfaction_score": 5,
            "resolution_notes": "Problema resuelto actualizando la configuración."
        },
        "agent": {"name": "María García"}
    }
    
    rendered = engine.render("ticket-resolved", context)
    print(rendered)

