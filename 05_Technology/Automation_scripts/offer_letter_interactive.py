#!/usr/bin/env python3
"""
Modo Interactivo para Generación de Cartas de Oferta
Permite crear cartas de oferta mediante un asistente interactivo
"""

import sys
from typing import Dict, Optional
from generate_offer_letter import generate_offer_letter
from offer_letter_extras import generate_html_offer_letter, validate_offer_data


def prompt_input(prompt: str, default: Optional[str] = None, required: bool = False) -> str:
    """Solicita entrada al usuario con valor por defecto."""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        value = input(full_prompt).strip()
        if value:
            return value
        elif default:
            return default
        elif not required:
            return ""
        else:
            print("  ⚠ Este campo es requerido. Por favor ingrese un valor.")


def prompt_yes_no(prompt: str, default: bool = True) -> bool:
    """Solicita confirmación sí/no."""
    default_str = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_str}]: ").strip().lower()
    
    if not response:
        return default
    return response in ['y', 'yes', 's', 'si', 'sí']


def prompt_list(prompt: str) -> list:
    """Solicita una lista de elementos."""
    print(f"\n{prompt}")
    print("  (Ingrese un elemento por línea, línea vacía para terminar)")
    items = []
    while True:
        item = input(f"  Item {len(items) + 1}: ").strip()
        if not item:
            break
        items.append(item)
    return items


def collect_offer_data() -> Dict:
    """Recopila datos de la oferta de forma interactiva."""
    print("\n" + "="*70)
    print("  GENERADOR INTERACTIVO DE CARTAS DE OFERTA")
    print("="*70)
    print("\nPor favor complete la siguiente información:\n")
    
    data = {}
    
    # Información básica requerida
    print("📋 INFORMACIÓN BÁSICA (Requerida)")
    print("-" * 70)
    data['position_title'] = prompt_input("Título del puesto", required=True)
    data['salary_amount'] = prompt_input("Salario anual", required=True)
    data['start_date'] = prompt_input("Fecha de inicio (YYYY-MM-DD)", required=True)
    data['location'] = prompt_input("Ubicación de trabajo", required=True)
    
    # Beneficios
    print("\n💼 BENEFICIOS")
    print("-" * 70)
    use_list = prompt_yes_no("¿Desea ingresar una lista de beneficios?", default=True)
    if use_list:
        data['benefits'] = prompt_list("Ingrese los beneficios:")
    else:
        benefits_str = prompt_input("Beneficios (separados por comas)")
        data['benefits'] = [b.strip() for b in benefits_str.split(',') if b.strip()] if benefits_str else []
    
    # Información de la empresa
    print("\n🏢 INFORMACIÓN DE LA EMPRESA")
    print("-" * 70)
    data['company_name'] = prompt_input("Nombre de la empresa", default="[Company Name]")
    data['company_address'] = prompt_input("Dirección de la empresa", default="")
    data['company_details'] = prompt_input("Descripción de la empresa (opcional)", default="")
    
    # Información del candidato
    print("\n👤 INFORMACIÓN DEL CANDIDATO")
    print("-" * 70)
    data['candidate_name'] = prompt_input("Nombre del candidato", default="[Candidate Name]")
    
    # Detalles de la posición
    print("\n📌 DETALLES ADICIONALES DE LA POSICIÓN")
    print("-" * 70)
    include_details = prompt_yes_no("¿Desea incluir detalles adicionales?", default=False)
    if include_details:
        data['department'] = prompt_input("Departamento", default="")
        data['manager_name'] = prompt_input("Nombre del manager", default="")
        data['manager_title'] = prompt_input("Título del manager", default="")
        data['employment_type'] = prompt_input("Tipo de empleo", default="Full-time")
        data['pay_frequency'] = prompt_input("Frecuencia de pago", default="Bi-weekly")
    
    # Compensación adicional
    print("\n💰 COMPENSACIÓN ADICIONAL")
    print("-" * 70)
    include_bonus = prompt_yes_no("¿Desea incluir bonos o equity?", default=False)
    if include_bonus:
        bonus_type = prompt_input("Tipo: (1) Bono porcentaje, (2) Bono cantidad, (3) Ambos, (4) Equity", default="1")
        if bonus_type in ['1', '3']:
            data['bonus_percentage'] = prompt_input("Porcentaje de bono anual", default="")
        if bonus_type in ['2', '3']:
            data['bonus_amount'] = prompt_input("Cantidad de bono anual", default="")
        if bonus_type == '4' or prompt_yes_no("¿Incluir equity/stock options?", default=False):
            data['equity_details'] = prompt_input("Detalles de equity/stock options", default="")
        
        data['sign_on_bonus'] = prompt_input("Sign-on bonus (opcional)", default="")
    
    # Contacto HR
    print("\n📞 INFORMACIÓN DE CONTACTO HR")
    print("-" * 70)
    include_hr = prompt_yes_no("¿Desea incluir información de contacto HR?", default=False)
    if include_hr:
        data['hr_name'] = prompt_input("Nombre del contacto HR", default="[HR Manager Name]")
        data['hr_title'] = prompt_input("Título del contacto HR", default="[HR Manager Title]")
        data['hr_phone'] = prompt_input("Teléfono", default="[Phone Number]")
        data['hr_email'] = prompt_input("Email", default="[Email Address]")
    
    # Configuración de la oferta
    print("\n⚙️ CONFIGURACIÓN DE LA OFERTA")
    print("-" * 70)
    data['offer_validity_days'] = int(prompt_input("Días de validez de la oferta", default="7") or "7")
    data['format_style'] = prompt_input("Estilo de formato (professional/simple)", default="professional")
    
    # Formato de salida
    print("\n📄 FORMATO DE SALIDA")
    print("-" * 70)
    output_format = prompt_input("Formato: (1) Texto, (2) HTML, (3) Ambos", default="1")
    data['output_format'] = output_format
    
    data['output_file'] = prompt_input("Nombre del archivo de salida (sin extensión)", default="offer_letter")
    
    return data


def generate_interactive():
    """Genera carta de oferta en modo interactivo."""
    try:
        data = collect_offer_data()
        
        # Validar datos
        print("\n🔍 Validando datos...")
        validation_data = {
            'position_title': data.get('position_title'),
            'salary_amount': data.get('salary_amount'),
            'start_date': data.get('start_date'),
            'location': data.get('location'),
            'hr_email': data.get('hr_email', ''),
            'offer_validity_days': data.get('offer_validity_days', 7)
        }
        
        is_valid, errors = validate_offer_data(validation_data)
        if not is_valid:
            print("\n❌ Errores de validación encontrados:")
            for error in errors:
                print(f"  - {error}")
            if not prompt_yes_no("\n¿Desea continuar de todas formas?", default=False):
                print("Operación cancelada.")
                return
        
        # Generar carta de texto
        output_format = data.pop('output_format', '1')
        output_file = data.pop('output_file', 'offer_letter')
        
        if output_format in ['1', '3']:
            print("\n📝 Generando carta de oferta en formato texto...")
            text_output = output_file + '.txt'
            generate_offer_letter(
                position_title=data['position_title'],
                salary_amount=data['salary_amount'],
                start_date=data['start_date'],
                benefits=data.get('benefits', []),
                location=data['location'],
                company_name=data.get('company_name'),
                company_details=data.get('company_details'),
                company_address=data.get('company_address'),
                candidate_name=data.get('candidate_name'),
                department=data.get('department'),
                manager_name=data.get('manager_name'),
                manager_title=data.get('manager_title'),
                employment_type=data.get('employment_type', 'Full-time'),
                pay_frequency=data.get('pay_frequency', 'Bi-weekly'),
                offer_validity_days=data.get('offer_validity_days', 7),
                hr_name=data.get('hr_name'),
                hr_title=data.get('hr_title'),
                hr_phone=data.get('hr_phone'),
                hr_email=data.get('hr_email'),
                format_style=data.get('format_style', 'professional'),
                bonus_amount=data.get('bonus_amount'),
                bonus_percentage=data.get('bonus_percentage'),
                equity_details=data.get('equity_details'),
                sign_on_bonus=data.get('sign_on_bonus'),
                output_file=text_output
            )
        
        # Generar carta HTML
        if output_format in ['2', '3']:
            print("🌐 Generando carta de oferta en formato HTML...")
            html_output = output_file + '.html'
            html_content = generate_html_offer_letter(
                position_title=data['position_title'],
                salary_amount=data['salary_amount'],
                start_date=data['start_date'],
                benefits=data.get('benefits', []),
                location=data['location'],
                company_name=data.get('company_name', '[Company Name]'),
                company_details=data.get('company_details'),
                company_address=data.get('company_address'),
                candidate_name=data.get('candidate_name', '[Candidate Name]'),
                department=data.get('department'),
                manager_name=data.get('manager_name'),
                manager_title=data.get('manager_title'),
                employment_type=data.get('employment_type', 'Full-time'),
                pay_frequency=data.get('pay_frequency', 'Bi-weekly'),
                offer_validity_days=data.get('offer_validity_days', 7),
                hr_name=data.get('hr_name', '[HR Manager Name]'),
                hr_title=data.get('hr_title', '[HR Manager Title]'),
                hr_phone=data.get('hr_phone', '[Phone Number]'),
                hr_email=data.get('hr_email', '[Email Address]'),
                bonus_amount=data.get('bonus_amount'),
                bonus_percentage=data.get('bonus_percentage'),
                equity_details=data.get('equity_details'),
                sign_on_bonus=data.get('sign_on_bonus')
            )
            with open(html_output, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print(f"✓ HTML offer letter saved to: {html_output}")
        
        print("\n✅ ¡Carta de oferta generada exitosamente!")
        print(f"   Archivos creados:")
        if output_format in ['1', '3']:
            print(f"   - {output_file}.txt")
        if output_format in ['2', '3']:
            print(f"   - {output_file}.html")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Operación cancelada por el usuario.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    generate_interactive()



