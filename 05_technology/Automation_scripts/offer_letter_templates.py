#!/usr/bin/env python3
"""
Sistema de Plantillas Personalizables para Cartas de Oferta
Permite crear y usar plantillas personalizadas
"""

import json
import os
from typing import Dict, Optional, List
from pathlib import Path


TEMPLATES_DIR = "offer_letter_templates"


def ensure_templates_dir():
    """Asegura que el directorio de plantillas existe."""
    os.makedirs(TEMPLATES_DIR, exist_ok=True)


def create_template(name: str, description: str = "", data: Optional[Dict] = None) -> str:
    """Crea una nueva plantilla."""
    ensure_templates_dir()
    
    template = {
        'name': name,
        'description': description,
        'created': str(Path(__file__).stat().st_mtime),
        'data': data or {}
    }
    
    filename = f"{name.lower().replace(' ', '_')}.json"
    filepath = os.path.join(TEMPLATES_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(template, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Plantilla creada: {filepath}")
    return filepath


def list_templates() -> List[Dict]:
    """Lista todas las plantillas disponibles."""
    ensure_templates_dir()
    
    templates = []
    for filename in os.listdir(TEMPLATES_DIR):
        if filename.endswith('.json'):
            filepath = os.path.join(TEMPLATES_DIR, filename)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    template = json.load(f)
                    templates.append({
                        'file': filename,
                        'name': template.get('name', filename),
                        'description': template.get('description', ''),
                        'path': filepath
                    })
            except Exception as e:
                print(f"⚠ Error leyendo {filename}: {e}")
    
    return templates


def load_template(name: str) -> Optional[Dict]:
    """Carga una plantilla por nombre."""
    templates = list_templates()
    
    # Buscar por nombre exacto o parcial
    for template in templates:
        if name.lower() in template['name'].lower() or name.lower() in template['file'].lower():
            try:
                with open(template['path'], 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"❌ Error cargando plantilla: {e}")
                return None
    
    return None


def create_default_templates():
    """Crea plantillas por defecto."""
    ensure_templates_dir()
    
    # Plantilla para startup
    startup_template = {
        'position_title': 'Software Engineer',
        'salary_amount': '120000',
        'start_date': '2024-03-15',
        'benefits': [
            'Health insurance - 100% company-paid',
            'Dental and vision coverage',
            '401k matching',
            'Unlimited PTO',
            'Home office stipend',
            'Learning and development budget'
        ],
        'location': 'Remote',
        'company_name': '[Company Name]',
        'employment_type': 'Full-time',
        'pay_frequency': 'Bi-weekly',
        'format_style': 'professional'
    }
    create_template('startup', 'Plantilla para startups con equity y beneficios flexibles', startup_template)
    
    # Plantilla para empresa grande
    enterprise_template = {
        'position_title': 'Senior Engineer',
        'salary_amount': '150000',
        'start_date': '2024-03-15',
        'benefits': [
            'Premium health insurance',
            'Dental and vision coverage',
            '401k with 6% matching',
            '20 days PTO',
            'Life insurance',
            'Disability insurance',
            'Professional development budget'
        ],
        'location': '[City, State]',
        'company_name': '[Company Name]',
        'employment_type': 'Full-time',
        'pay_frequency': 'Bi-weekly',
        'bonus_percentage': '15%',
        'format_style': 'professional'
    }
    create_template('enterprise', 'Plantilla para empresas grandes con beneficios completos', enterprise_template)
    
    # Plantilla ejecutiva
    executive_template = {
        'position_title': 'VP of Engineering',
        'salary_amount': '200000',
        'start_date': '2024-04-01',
        'benefits': [
            'Premium health insurance - 100% company-paid',
            'Dental and vision coverage',
            '401k with 6% matching',
            'Unlimited PTO',
            'Life insurance',
            'Disability insurance',
            'Executive benefits package'
        ],
        'location': '[City, State]',
        'company_name': '[Company Name]',
        'employment_type': 'Full-time',
        'pay_frequency': 'Bi-weekly',
        'bonus_percentage': '20%',
        'sign_on_bonus': '25000',
        'equity_details': 'Equity package with 4-year vesting',
        'format_style': 'professional'
    }
    create_template('executive', 'Plantilla para posiciones ejecutivas con bonos altos', executive_template)
    
    print("\n✓ Plantillas por defecto creadas:")
    print("  - startup: Para startups")
    print("  - enterprise: Para empresas grandes")
    print("  - executive: Para posiciones ejecutivas")


def main():
    """Función principal."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Gestiona plantillas de cartas de oferta')
    parser.add_argument('--list', action='store_true',
                       help='Listar todas las plantillas')
    parser.add_argument('--create-defaults', action='store_true',
                       help='Crear plantillas por defecto')
    parser.add_argument('--create', dest='template_name',
                       help='Crear nueva plantilla')
    parser.add_argument('--load', dest='template_to_load',
                       help='Cargar y mostrar plantilla')
    parser.add_argument('--use', dest='template_to_use',
                       help='Usar plantilla para generar oferta (requiere --json o parámetros)')
    
    args = parser.parse_args()
    
    if args.create_defaults:
        create_default_templates()
    elif args.list:
        templates = list_templates()
        if templates:
            print("\n📋 Plantillas disponibles:\n")
            for template in templates:
                print(f"  • {template['name']}")
                if template['description']:
                    print(f"    {template['description']}")
                print(f"    Archivo: {template['file']}\n")
        else:
            print("No hay plantillas disponibles. Use --create-defaults para crear plantillas por defecto.")
    elif args.template_to_load:
        template = load_template(args.template_to_load)
        if template:
            print(f"\n📄 Plantilla: {template.get('name', 'N/A')}")
            print(f"   Descripción: {template.get('description', 'N/A')}")
            print(f"\n   Datos:")
            print(json.dumps(template.get('data', {}), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Plantilla '{args.template_to_load}' no encontrada")
    elif args.template_to_use:
        template = load_template(args.template_to_use)
        if template:
            # Guardar como JSON para usar con --json
            output_file = f"offer_from_template_{args.template_to_use}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(template.get('data', {}), f, indent=2, ensure_ascii=False)
            print(f"✓ Plantilla cargada y guardada en: {output_file}")
            print(f"  Usa: python generate_offer_letter.py --json {output_file}")
        else:
            print(f"❌ Plantilla '{args.template_to_use}' no encontrada")
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

