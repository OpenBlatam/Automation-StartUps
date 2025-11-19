#!/usr/bin/env python3
"""
Utilidad para cargar configuración centralizada de DAGs.

Uso en tus DAGs:
    from load_config import get_dag_config
    
    config = get_dag_config('sales_marketing')
    default_args = {
        'owner': config['owner'],
        'retries': config['retries'],
        ...
    }
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

# Ruta al archivo de configuración
CONFIG_FILE = Path(__file__).parent / "dag_config.yaml"


def load_config() -> Dict[str, Any]:
    """
    Carga la configuración completa desde dag_config.yaml.
    
    Returns:
        Dict con toda la configuración
    """
    if not CONFIG_FILE.exists():
        # Retornar configuración por defecto si no existe el archivo
        return get_default_config()
    
    with open(CONFIG_FILE, 'r') as f:
        return yaml.safe_load(f) or {}


def get_default_config() -> Dict[str, Any]:
    """Retorna configuración por defecto."""
    return {
        'general': {
            'default_owner': 'data-team',
            'default_retries': 2,
            'default_retry_delay_minutes': 5,
        },
        'areas': {}
    }


def get_dag_config(area: str) -> Dict[str, Any]:
    """
    Obtiene configuración para un área específica.
    
    Args:
        area: Nombre del área (ej: 'sales_marketing')
        
    Returns:
        Dict con configuración del área o defaults
    """
    config = load_config()
    general = config.get('general', {})
    area_config = config.get('areas', {}).get(area, {})
    
    # Combinar configuración general con específica del área
    return {
        'owner': area_config.get('owner', general.get('default_owner', 'data-team')),
        'retries': area_config.get('retries', general.get('default_retries', 2)),
        'retry_delay_minutes': area_config.get('retry_delay_minutes', 
                                               general.get('default_retry_delay_minutes', 5)),
        'email_on_failure': area_config.get('email_on_failure', 
                                           general.get('default_email_on_failure', True)),
        'email_on_retry': area_config.get('email_on_retry', 
                                         general.get('default_email_on_retry', False)),
        'tags': area_config.get('tags', []),
        'priority': area_config.get('priority', 'medium'),
    }


def get_schedule(schedule_name: str) -> Optional[str]:
    """
    Obtiene un schedule predefinido.
    
    Args:
        schedule_name: Nombre del schedule (ej: 'daily', 'business_days')
        
    Returns:
        String con el schedule o None si no existe
    """
    config = load_config()
    schedules = config.get('schedules', {})
    return schedules.get(schedule_name)


def get_resource_config(resource_size: str) -> Dict[str, str]:
    """
    Obtiene configuración de recursos.
    
    Args:
        resource_size: Tamaño ('small', 'medium', 'large', 'xlarge')
        
    Returns:
        Dict con configuración de recursos
    """
    config = load_config()
    resources = config.get('resources', {})
    return resources.get(resource_size, {})


if __name__ == "__main__":
    # Ejemplo de uso
    print("Configuración de ejemplo:")
    print(f"Sales Marketing: {get_dag_config('sales_marketing')}")
    print(f"Schedule diario: {get_schedule('daily')}")
    print(f"Recursos medianos: {get_resource_config('medium')}")

