"""
Sistema de Plantillas Personalizables para Troubleshooting
Permite crear y usar plantillas personalizadas para diferentes casos
"""

import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class TemplateVariable:
    """Variable en una plantilla"""
    name: str
    description: str
    default_value: Optional[str] = None
    required: bool = True
    type: str = "string"  # string, number, boolean, list


@dataclass
class TroubleshootingTemplate:
    """Plantilla personalizada de troubleshooting"""
    template_id: str
    name: str
    description: str
    category: str
    variables: List[TemplateVariable]
    steps_template: List[Dict]
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class TroubleshootingTemplateManager:
    """Gestiona plantillas personalizables de troubleshooting"""
    
    def __init__(self, templates_path: Optional[str] = None):
        if templates_path is None:
            templates_path = Path(__file__).parent / "troubleshooting_templates.json"
        else:
            templates_path = Path(templates_path)
        
        self.templates_path = templates_path
        self.templates: Dict[str, TroubleshootingTemplate] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carga plantillas desde archivo JSON"""
        try:
            if self.templates_path.exists():
                with open(self.templates_path, 'r', encoding='utf-8') as f:
                    templates_data = json.load(f)
                
                for template_id, template_data in templates_data.items():
                    variables = [
                        TemplateVariable(**v) for v in template_data.get("variables", [])
                    ]
                    template = TroubleshootingTemplate(
                        template_id=template_id,
                        name=template_data["name"],
                        description=template_data["description"],
                        category=template_data.get("category", "general"),
                        variables=variables,
                        steps_template=template_data.get("steps_template", []),
                        metadata=template_data.get("metadata", {})
                    )
                    self.templates[template_id] = template
                
                logger.info(f"Cargadas {len(self.templates)} plantillas")
            else:
                logger.warning(f"Archivo de plantillas no encontrado: {self.templates_path}")
        except Exception as e:
            logger.error(f"Error cargando plantillas: {e}")
    
    def get_template(self, template_id: str) -> Optional[TroubleshootingTemplate]:
        """Obtiene una plantilla por ID"""
        return self.templates.get(template_id)
    
    def list_templates(self, category: Optional[str] = None) -> List[Dict]:
        """Lista todas las plantillas, opcionalmente filtradas por categoría"""
        templates = []
        for template_id, template in self.templates.items():
            if category is None or template.category == category:
                templates.append({
                    "template_id": template_id,
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "variables_count": len(template.variables),
                    "steps_count": len(template.steps_template)
                })
        return templates
    
    def render_template(
        self,
        template_id: str,
        variables: Dict[str, any]
    ) -> Dict:
        """
        Renderiza una plantilla con variables
        
        Args:
            template_id: ID de la plantilla
            variables: Diccionario con valores de variables
            
        Returns:
            Diccionario con la guía de troubleshooting renderizada
        """
        template = self.get_template(template_id)
        if not template:
            return {"error": f"Template {template_id} not found"}
        
        # Validar variables requeridas
        missing_vars = []
        for var in template.variables:
            if var.required and var.name not in variables:
                if var.default_value is None:
                    missing_vars.append(var.name)
                else:
                    variables[var.name] = var.default_value
        
        if missing_vars:
            return {
                "error": f"Missing required variables: {', '.join(missing_vars)}"
            }
        
        # Renderizar pasos
        rendered_steps = []
        for step_template in template.steps_template:
            rendered_step = self._render_step(step_template, variables)
            rendered_steps.append(rendered_step)
        
        return {
            "problem_title": self._render_text(template.name, variables),
            "problem_description": self._render_text(template.description, variables),
            "category": template.category,
            "steps": rendered_steps,
            "metadata": template.metadata
        }
    
    def _render_step(self, step_template: Dict, variables: Dict) -> Dict:
        """Renderiza un paso individual"""
        rendered = {}
        for key, value in step_template.items():
            if isinstance(value, str):
                rendered[key] = self._render_text(value, variables)
            elif isinstance(value, list):
                rendered[key] = [
                    self._render_text(item, variables) if isinstance(item, str) else item
                    for item in value
                ]
            else:
                rendered[key] = value
        return rendered
    
    def _render_text(self, text: str, variables: Dict) -> str:
        """Reemplaza variables en texto usando sintaxis {{variable}}"""
        def replace_var(match):
            var_name = match.group(1).strip()
            if var_name in variables:
                return str(variables[var_name])
            return match.group(0)  # Mantener original si no existe
        
        return re.sub(r'\{\{(\w+)\}\}', replace_var, text)
    
    def create_template(
        self,
        template_id: str,
        name: str,
        description: str,
        category: str,
        variables: List[Dict],
        steps_template: List[Dict],
        metadata: Optional[Dict] = None
    ) -> TroubleshootingTemplate:
        """Crea una nueva plantilla"""
        template_vars = [TemplateVariable(**v) for v in variables]
        template = TroubleshootingTemplate(
            template_id=template_id,
            name=name,
            description=description,
            category=category,
            variables=template_vars,
            steps_template=steps_template,
            metadata=metadata or {}
        )
        
        self.templates[template_id] = template
        self._save_templates()
        
        logger.info(f"Plantilla creada: {template_id}")
        return template
    
    def _save_templates(self):
        """Guarda plantillas en archivo JSON"""
        try:
            templates_data = {}
            for template_id, template in self.templates.items():
                templates_data[template_id] = {
                    "name": template.name,
                    "description": template.description,
                    "category": template.category,
                    "variables": [asdict(v) for v in template.variables],
                    "steps_template": template.steps_template,
                    "metadata": template.metadata
                }
            
            with open(self.templates_path, 'w', encoding='utf-8') as f:
                json.dump(templates_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Plantillas guardadas en {self.templates_path}")
        except Exception as e:
            logger.error(f"Error guardando plantillas: {e}")



