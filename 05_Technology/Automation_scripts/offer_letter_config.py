#!/usr/bin/env python3
"""
Sistema de Configuración para el Sistema de Cartas de Oferta
Permite cargar configuración desde archivos YAML o JSON
"""

import json
import os
import sys
from typing import Dict, Optional
from pathlib import Path


CONFIG_FILE = "offer_letter_config.json"
CONFIG_DIR = Path.home() / ".offer_letter"


def load_config(config_file: Optional[str] = None) -> Dict:
    """Carga configuración desde archivo."""
    config = {}
    
    # Buscar archivo de configuración
    config_paths = []
    
    if config_file:
        config_paths.append(Path(config_file))
    
    # Buscar en directorio actual
    config_paths.append(Path(CONFIG_FILE))
    
    # Buscar en directorio home
    config_paths.append(CONFIG_DIR / CONFIG_FILE)
    
    # Buscar en variables de entorno
    env_config = os.getenv('OFFER_LETTER_CONFIG')
    if env_config:
        config_paths.append(Path(env_config))
    
    for config_path in config_paths:
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                print(f"✓ Configuración cargada desde: {config_path}")
                return config
            except Exception as e:
                print(f"⚠ Error cargando configuración desde {config_path}: {e}")
    
    return config


def save_config(config: Dict, config_file: Optional[str] = None):
    """Guarda configuración en archivo."""
    if config_file:
        config_path = Path(config_file)
    else:
        # Crear directorio si no existe
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        config_path = CONFIG_DIR / CONFIG_FILE
    
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"✓ Configuración guardada en: {config_path}")
    except Exception as e:
        print(f"❌ Error guardando configuración: {e}", file=sys.stderr)


def create_default_config():
    """Crea archivo de configuración por defecto."""
    default_config = {
        "api": {
            "port": 8000,
            "host": "",
            "auth_enabled": False,
            "rate_limit_requests": 100,
            "rate_limit_window_seconds": 3600
        },
        "email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "smtp_user": "",
            "smtp_password": ""
        },
        "defaults": {
            "format_style": "professional",
            "employment_type": "Full-time",
            "pay_frequency": "Bi-weekly",
            "offer_validity_days": 7
        },
        "company": {
            "name": "[Company Name]",
            "address": "",
            "details": ""
        },
        "hr": {
            "name": "[HR Manager Name]",
            "title": "[HR Manager Title]",
            "phone": "[Phone Number]",
            "email": "[Email Address]"
        }
    }
    
    save_config(default_config)
    return default_config


def get_config_value(config: Dict, key_path: str, default=None):
    """Obtiene un valor de configuración usando path (ej: 'api.port')."""
    keys = key_path.split('.')
    value = config
    
    for key in keys:
        if isinstance(value, dict):
            value = value.get(key)
            if value is None:
                return default
        else:
            return default
    
    return value if value is not None else default


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestiona configuración del sistema de cartas de oferta')
    parser.add_argument('--create', action='store_true',
                       help='Crear archivo de configuración por defecto')
    parser.add_argument('--show', action='store_true',
                       help='Mostrar configuración actual')
    parser.add_argument('--file', dest='config_file',
                       help='Archivo de configuración específico')
    parser.add_argument('--get', dest='get_key',
                       help='Obtener valor específico (ej: api.port)')
    
    args = parser.parse_args()
    
    if args.create:
        config = create_default_config()
        print("\n✓ Archivo de configuración por defecto creado")
        print(f"  Ubicación: {CONFIG_DIR / CONFIG_FILE}")
    elif args.get_key:
        config = load_config(args.config_file)
        value = get_config_value(config, args.get_key)
        print(value if value is not None else "")
    elif args.show:
        config = load_config(args.config_file)
        if config:
            print("\n📋 Configuración actual:\n")
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print("No se encontró archivo de configuración.")
            print("Usa --create para crear uno por defecto.")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()



