#!/usr/bin/env python3
"""
Motor de Plantillas Avanzado para Testimonios
Sistema de plantillas con variables dinámicas y lógica condicional
"""

import re
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path
import json

logger = logging.getLogger(__name__)


class TemplateEngine:
    """Motor de plantillas avanzado con variables y lógica"""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Inicializa el motor de plantillas
        
        Args:
            templates_dir: Directorio con plantillas personalizadas
        """
        self.templates_dir = Path(templates_dir) if templates_dir else None
        self.templates: Dict[str, str] = {}
        self._load_templates()
    
    def _load_templates(self):
        """Carga plantillas desde directorio"""
        if not self.templates_dir or not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.glob("*.json"):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_name = template_file.stem
                    self.templates[template_name] = template_data.get('template', '')
                logger.debug(f"Plantilla cargada: {template_name}")
            except Exception as e:
                logger.warning(f"Error al cargar plantilla {template_file}: {e}")
    
    def render_template(
        self,
        template: str,
        context: Dict[str, Any],
        post_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Renderiza una plantilla con contexto
        
        Args:
            template: Plantilla con variables {{variable}}
            context: Contexto con valores para variables
            post_data: Datos del post (opcional, para variables especiales)
        
        Returns:
            Plantilla renderizada
        """
        result = template
        
        # Combinar contextos
        full_context = context.copy()
        if post_data:
            full_context.update(self._extract_post_variables(post_data))
        
        # Reemplazar variables simples {{variable}}
        for key, value in full_context.items():
            placeholder = f"{{{{{key}}}}}"
            result = result.replace(placeholder, str(value))
        
        # Procesar condicionales {% if condition %}...{% endif %}
        result = self._process_conditionals(result, full_context)
        
        # Procesar loops {% for item in items %}...{% endfor %}
        result = self._process_loops(result, full_context)
        
        # Procesar funciones {{ function(arg) }}
        result = self._process_functions(result, full_context)
        
        return result
    
    def _extract_post_variables(self, post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae variables especiales del post_data"""
        variables = {
            'post_content': post_data.get('post_content', ''),
            'hashtags': ', '.join(post_data.get('hashtags', [])),
            'hashtags_count': len(post_data.get('hashtags', [])),
            'platform': post_data.get('platform', ''),
            'length': post_data.get('length', 0),
            'cta': post_data.get('call_to_action', ''),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        }
        
        # Variables de engagement
        if 'engagement_prediction' in post_data:
            pred = post_data['engagement_prediction']
            variables.update({
                'engagement_score': pred.get('predicted_score', 0),
                'engagement_rate': pred.get('predicted_engagement_rate', 0),
                'confidence': pred.get('confidence', 0),
            })
        
        # Variables de ROI
        if 'roi_calculation' in post_data:
            roi = post_data['roi_calculation']
            variables.update({
                'roi_percentage': roi.get('roi_percentage', 0),
                'estimated_revenue': roi.get('estimated_revenue', 0),
                'estimated_reach': roi.get('estimated_reach', 0),
            })
        
        return variables
    
    def _process_conditionals(self, template: str, context: Dict[str, Any]) -> str:
        """Procesa condicionales {% if %}...{% endif %}"""
        pattern = r'{%\s*if\s+(\w+)\s*%}(.*?){%\s*endif\s*%}'
        
        def replace_conditional(match):
            condition = match.group(1)
            content = match.group(2)
            
            # Evaluar condición
            if condition in context and context[condition]:
                return content
            return ''
        
        result = re.sub(pattern, replace_conditional, template, flags=re.DOTALL)
        return result
    
    def _process_loops(self, template: str, context: Dict[str, Any]) -> str:
        """Procesa loops {% for item in items %}...{% endfor %}"""
        pattern = r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}(.*?){%\s*endfor\s*%}'
        
        def replace_loop(match):
            item_var = match.group(1)
            items_var = match.group(2)
            content = match.group(3)
            
            if items_var in context:
                items = context[items_var]
                if isinstance(items, list):
                    result_parts = []
                    for item in items:
                        item_context = context.copy()
                        item_context[item_var] = item
                        # Renderizar contenido con contexto del item
                        rendered = self.render_template(content, item_context)
                        result_parts.append(rendered)
                    return ''.join(result_parts)
            
            return ''
        
        result = re.sub(pattern, replace_loop, template, flags=re.DOTALL)
        return result
    
    def _process_functions(self, template: str, context: Dict[str, Any]) -> str:
        """Procesa funciones {{ function(arg) }}"""
        pattern = r'{{\s*(\w+)\(([^)]+)\)\s*}}'
        
        def replace_function(match):
            func_name = match.group(1)
            arg = match.group(2).strip().strip('"\'')
            
            if func_name == 'upper':
                return arg.upper()
            elif func_name == 'lower':
                return arg.lower()
            elif func_name == 'capitalize':
                return arg.capitalize()
            elif func_name == 'format_number':
                try:
                    num = float(arg)
                    return f"{num:,.2f}"
                except:
                    return arg
            elif func_name == 'format_percent':
                try:
                    num = float(arg)
                    return f"{num:.1f}%"
                except:
                    return arg
            
            return match.group(0)
        
        result = re.sub(pattern, replace_function, template)
        return result
    
    def generate_from_template(
        self,
        template_name: str,
        post_data: Dict[str, Any],
        custom_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Genera contenido desde una plantilla nombrada
        
        Args:
            template_name: Nombre de la plantilla
            post_data: Datos del post
            custom_context: Contexto personalizado adicional
        
        Returns:
            Contenido generado
        """
        template = self.templates.get(template_name)
        if not template:
            logger.warning(f"Plantilla '{template_name}' no encontrada")
            return ""
        
        context = custom_context or {}
        return self.render_template(template, context, post_data)
    
    def create_custom_template(
        self,
        name: str,
        template: str,
        description: Optional[str] = None
    ):
        """
        Crea una plantilla personalizada
        
        Args:
            name: Nombre de la plantilla
            template: Contenido de la plantilla
            description: Descripción opcional
        """
        self.templates[name] = template
        
        # Guardar en archivo si hay directorio configurado
        if self.templates_dir:
            self.templates_dir.mkdir(parents=True, exist_ok=True)
            template_file = self.templates_dir / f"{name}.json"
            template_data = {
                'name': name,
                'description': description,
                'template': template,
                'created_at': datetime.now().isoformat()
            }
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Plantilla '{name}' creada")
    
    def list_templates(self) -> List[str]:
        """Lista todas las plantillas disponibles"""
        return list(self.templates.keys())


