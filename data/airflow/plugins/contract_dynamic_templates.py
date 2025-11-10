"""
Sistema de Plantillas Dinámicas Inteligentes
Plantillas condicionales, lógica de negocio y generación inteligente
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List
import re

logger = logging.getLogger("airflow.task")


def process_conditional_template(
    template_content: str,
    variables: Dict[str, Any],
    context: Dict[str, Any] = None
) -> str:
    """
    Procesa plantilla con condicionales y lógica.
    
    Soporta:
    - {% if condition %} ... {% endif %}
    - {% for item in list %} ... {% endfor %}
    - {% include template_id %}
    - {{ variable | filter }}
    
    Args:
        template_content: Contenido de la plantilla
        variables: Variables disponibles
        context: Contexto adicional
        
    Returns:
        Contenido procesado
    """
    context = context or {}
    all_vars = {**variables, **context}
    
    result = template_content
    
    # Procesar includes primero
    include_pattern = r'\{%\s*include\s+(\w+)\s*%\}'
    includes = re.findall(include_pattern, result)
    for template_id in includes:
        # TODO: Cargar template incluido desde BD
        included_content = f"[Template {template_id} incluido]"
        result = re.sub(
            f'\\{{\\%\\s*include\\s+{template_id}\\s*%\\}}',
            included_content,
            result
        )
    
    # Procesar condicionales {% if %}
    result = process_conditionals(result, all_vars)
    
    # Procesar loops {% for %}
    result = process_loops(result, all_vars)
    
    # Reemplazar variables simples {{ variable }}
    result = replace_variables(result, all_vars)
    
    return result


def process_conditionals(content: str, variables: Dict[str, Any]) -> str:
    """Procesa bloques condicionales {% if %}"""
    pattern = r'\{%\s*if\s+(\w+)\s*%\}(.*?)\{%\s*endif\s*%\}'
    
    def replace_conditional(match):
        condition = match.group(1)
        block_content = match.group(2)
        
        # Evaluar condición
        condition_value = variables.get(condition, False)
        
        # Convertir a booleano
        if isinstance(condition_value, bool):
            is_true = condition_value
        elif isinstance(condition_value, str):
            is_true = condition_value.lower() in ('true', 'yes', '1', 'on')
        elif isinstance(condition_value, (int, float)):
            is_true = condition_value != 0
        else:
            is_true = bool(condition_value)
        
        return block_content if is_true else ""
    
    while re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replace_conditional, content, flags=re.DOTALL)
    
    return content


def process_loops(content: str, variables: Dict[str, Any]) -> str:
    """Procesa loops {% for %}"""
    pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?)\{%\s*endfor\s*%\}'
    
    def replace_loop(match):
        item_var = match.group(1)
        list_var = match.group(2)
        block_content = match.group(3)
        
        # Obtener lista
        items = variables.get(list_var, [])
        if not isinstance(items, list):
            return ""
        
        # Generar contenido para cada item
        result_items = []
        for item in items:
            item_vars = {**variables, item_var: item}
            item_content = replace_variables(block_content, item_vars)
            result_items.append(item_content)
        
        return "\n".join(result_items)
    
    while re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, replace_loop, content, flags=re.DOTALL)
    
    return content


def replace_variables(content: str, variables: Dict[str, Any]) -> str:
    """Reemplaza variables {{ variable }} con valores"""
    pattern = r'\{\{\s*(\w+)(?:\s*\|\s*(\w+))?\s*\}\}'
    
    def replace_var(match):
        var_name = match.group(1)
        filter_name = match.group(2)
        
        value = variables.get(var_name, f"{{{{{var_name}}}}}")
        
        # Aplicar filtros
        if filter_name:
            value = apply_filter(value, filter_name)
        
        return str(value)
    
    return re.sub(pattern, replace_var, content)


def apply_filter(value: Any, filter_name: str) -> str:
    """Aplica filtros a valores"""
    if filter_name == "upper":
        return str(value).upper()
    elif filter_name == "lower":
        return str(value).lower()
    elif filter_name == "title":
        return str(value).title()
    elif filter_name == "currency":
        return f"${value:,.2f}" if isinstance(value, (int, float)) else str(value)
    elif filter_name == "date":
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d')
        return str(value)
    elif filter_name == "datetime":
        if hasattr(value, 'strftime'):
            return value.strftime('%Y-%m-%d %H:%M:%S')
        return str(value)
    else:
        return str(value)


def generate_smart_template(
    template_id: str,
    variables: Dict[str, Any],
    context: Dict[str, Any] = None,
    postgres_conn_id: str = "postgres_default"
) -> str:
    """
    Genera contrato desde plantilla inteligente con lógica condicional.
    
    Args:
        template_id: ID de la plantilla
        variables: Variables para la plantilla
        context: Contexto adicional
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Contenido generado
    """
    from data.airflow.plugins.contract_integrations import get_template
    
    template = get_template(template_id, postgres_conn_id)
    if not template:
        raise ValueError(f"Template {template_id} no encontrado")
    
    template_content = template.get("template_content", "")
    
    # Procesar plantilla dinámica
    processed_content = process_conditional_template(
        template_content,
        variables,
        context
    )
    
    return processed_content

