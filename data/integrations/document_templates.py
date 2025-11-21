"""
Sistema de Templates Personalizables para Extracción
=====================================================

Permite definir templates personalizados para extraer campos
específicos de documentos según necesidades del negocio.
"""

from typing import Dict, Any, List, Optional, Pattern
from dataclasses import dataclass, field
from enum import Enum
import re
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class ExtractionRule:
    """Regla de extracción"""
    field_name: str
    pattern: str  # Regex pattern
    regex_flags: int = re.IGNORECASE | re.MULTILINE
    required: bool = False
    transform: Optional[str] = None  # Función de transformación
    default_value: Optional[Any] = None
    validation: Optional[Dict[str, Any]] = None


@dataclass
class DocumentTemplate:
    """Template para un tipo de documento"""
    template_id: str
    name: str
    document_type: str
    description: str
    rules: List[ExtractionRule] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario"""
        return {
            "template_id": self.template_id,
            "name": self.name,
            "document_type": self.document_type,
            "description": self.description,
            "rules": [
                {
                    "field_name": r.field_name,
                    "pattern": r.pattern,
                    "regex_flags": r.regex_flags,
                    "required": r.required,
                    "transform": r.transform,
                    "default_value": r.default_value,
                    "validation": r.validation
                }
                for r in self.rules
            ],
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentTemplate":
        """Crea desde diccionario"""
        rules = [
            ExtractionRule(
                field_name=r.get("field_name"),
                pattern=r.get("pattern"),
                regex_flags=r.get("regex_flags", re.IGNORECASE | re.MULTILINE),
                required=r.get("required", False),
                transform=r.get("transform"),
                default_value=r.get("default_value"),
                validation=r.get("validation")
            )
            for r in data.get("rules", [])
        ]
        
        return cls(
            template_id=data.get("template_id"),
            name=data.get("name"),
            document_type=data.get("document_type"),
            description=data.get("description", ""),
            rules=rules,
            metadata=data.get("metadata", {})
        )


class TemplateManager:
    """Gestor de templates de documentos"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        self.templates_dir = Path(templates_dir) if templates_dir else Path("./templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.templates: Dict[str, DocumentTemplate] = {}
        self.logger = logging.getLogger(__name__)
        self._load_templates()
    
    def _load_templates(self):
        """Carga templates desde archivos"""
        if not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    template = DocumentTemplate.from_dict(data)
                    self.templates[template.template_id] = template
                    self.logger.info(f"Template cargado: {template.template_id}")
            except Exception as e:
                self.logger.error(f"Error cargando template {template_file}: {e}")
    
    def create_template(
        self,
        template_id: str,
        name: str,
        document_type: str,
        description: str,
        rules: List[ExtractionRule],
        metadata: Optional[Dict[str, Any]] = None
    ) -> DocumentTemplate:
        """Crea un nuevo template"""
        template = DocumentTemplate(
            template_id=template_id,
            name=name,
            document_type=document_type,
            description=description,
            rules=rules,
            metadata=metadata or {}
        )
        
        self.templates[template_id] = template
        self._save_template(template)
        
        return template
    
    def get_template(self, template_id: str) -> Optional[DocumentTemplate]:
        """Obtiene un template por ID"""
        return self.templates.get(template_id)
    
    def get_templates_by_type(self, document_type: str) -> List[DocumentTemplate]:
        """Obtiene templates por tipo de documento"""
        return [
            t for t in self.templates.values()
            if t.document_type == document_type
        ]
    
    def update_template(self, template_id: str, **updates) -> bool:
        """Actualiza un template existente"""
        if template_id not in self.templates:
            return False
        
        template = self.templates[template_id]
        
        if "name" in updates:
            template.name = updates["name"]
        if "description" in updates:
            template.description = updates["description"]
        if "rules" in updates:
            template.rules = updates["rules"]
        if "metadata" in updates:
            template.metadata.update(updates["metadata"])
        
        self._save_template(template)
        return True
    
    def delete_template(self, template_id: str) -> bool:
        """Elimina un template"""
        if template_id not in self.templates:
            return False
        
        template_file = self.templates_dir / f"{template_id}.json"
        if template_file.exists():
            template_file.unlink()
        
        del self.templates[template_id]
        return True
    
    def _save_template(self, template: DocumentTemplate):
        """Guarda un template en disco"""
        template_file = self.templates_dir / f"{template.template_id}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template.to_dict(), f, indent=2, ensure_ascii=False)
    
    def extract_with_template(
        self,
        text: str,
        template_id: str
    ) -> Dict[str, Any]:
        """Extrae campos usando un template específico"""
        template = self.get_template(template_id)
        if not template:
            raise ValueError(f"Template no encontrado: {template_id}")
        
        extracted = {}
        
        for rule in template.rules:
            try:
                # Buscar patrón
                pattern = re.compile(rule.pattern, rule.regex_flags)
                match = pattern.search(text)
                
                if match:
                    # Extraer valor
                    if match.groups():
                        value = match.group(1)  # Primer grupo capturado
                    else:
                        value = match.group(0)  # Match completo
                    
                    # Aplicar transformación si existe
                    if rule.transform:
                        value = self._apply_transform(value, rule.transform)
                    
                    extracted[rule.field_name] = value
                elif rule.required:
                    # Campo requerido no encontrado
                    if rule.default_value is not None:
                        extracted[rule.field_name] = rule.default_value
                    else:
                        self.logger.warning(
                            f"Campo requerido '{rule.field_name}' no encontrado"
                        )
            
            except Exception as e:
                self.logger.error(f"Error extrayendo campo {rule.field_name}: {e}")
                if rule.default_value is not None:
                    extracted[rule.field_name] = rule.default_value
        
        return extracted
    
    def _apply_transform(self, value: str, transform: str) -> Any:
        """Aplica transformación a un valor"""
        if transform == "uppercase":
            return value.upper()
        elif transform == "lowercase":
            return value.lower()
        elif transform == "strip":
            return value.strip()
        elif transform == "remove_spaces":
            return re.sub(r'\s+', '', value)
        elif transform == "remove_special_chars":
            return re.sub(r'[^\w\s]', '', value)
        elif transform.startswith("replace:"):
            # replace:old:new
            parts = transform.split(":", 2)
            if len(parts) == 3:
                return value.replace(parts[1], parts[2])
        elif transform == "float":
            try:
                return float(re.sub(r'[^\d,.-]', '', value.replace(',', '')))
            except:
                return value
        elif transform == "int":
            try:
                return int(re.sub(r'[^\d]', '', value))
            except:
                return value
        
        return value


# Templates predefinidos comunes
def create_default_invoice_template() -> DocumentTemplate:
    """Crea template por defecto para facturas"""
    rules = [
        ExtractionRule(
            field_name="invoice_number",
            pattern=r"factura\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
            required=True
        ),
        ExtractionRule(
            field_name="date",
            pattern=r"fecha\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            required=True
        ),
        ExtractionRule(
            field_name="total",
            pattern=r"total\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            required=True,
            transform="float"
        ),
        ExtractionRule(
            field_name="customer_name",
            pattern=r"cliente\s*:?\s*([^\n]+)",
            transform="strip"
        ),
        ExtractionRule(
            field_name="customer_email",
            pattern=r"email\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            transform="lowercase"
        ),
        ExtractionRule(
            field_name="due_date",
            pattern=r"vencimiento\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        )
    ]
    
    return DocumentTemplate(
        template_id="default_invoice",
        name="Factura Estándar",
        document_type="invoice",
        description="Template por defecto para facturas",
        rules=rules
    )


def create_default_contract_template() -> DocumentTemplate:
    """Crea template por defecto para contratos"""
    rules = [
        ExtractionRule(
            field_name="contract_number",
            pattern=r"contrato\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
            required=True
        ),
        ExtractionRule(
            field_name="start_date",
            pattern=r"fecha\s*de\s*inicio\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
            required=True
        ),
        ExtractionRule(
            field_name="end_date",
            pattern=r"fecha\s*de\s*termino\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})"
        ),
        ExtractionRule(
            field_name="parties",
            pattern=r"partes?\s*:?\s*([^\n]+)",
            transform="strip"
        ),
        ExtractionRule(
            field_name="amount",
            pattern=r"monto\s*:?\s*\$?\s*([\d,]+\.?\d*)",
            transform="float"
        )
    ]
    
    return DocumentTemplate(
        template_id="default_contract",
        name="Contrato Estándar",
        document_type="contract",
        description="Template por defecto para contratos",
        rules=rules
    )

