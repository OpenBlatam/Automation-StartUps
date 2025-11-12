#!/usr/bin/env python3
"""
Ejemplo de uso del template de verificación de pagos para facturas pendientes.

Este script demuestra cómo usar el template de respuesta empática y resolutiva
para casos donde un cliente afirma haber pagado pero la factura aparece pendiente.

Uso:
    python scripts/support_payment_verification_example.py
"""
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from workflow.kestra.flows.lib.support_billing_payment_verification_template import (
    get_payment_verification_response_template,
    get_payment_tracking_instructions
)


def example_basic_usage():
    """Ejemplo básico de uso del template."""
    print("=" * 80)
    print("EJEMPLO 1: Uso Básico del Template")
    print("=" * 80)
    
    # Datos del ticket
    ticket_data = {
        "ticket_id": "TKT-20241215-ABC123",
        "customer_name": "María González",
        "customer_email": "maria.gonzalez@example.com",
        "assigned_agent_name": "Carlos Rodríguez"
    }
    
    # Generar respuesta
    response = get_payment_verification_response_template(
        ticket_data=ticket_data,
        invoice_number="FAC-2024-001234",
        invoice_amount=299.99,
        credit_amount=299.99,  # Crédito temporal del mismo monto
        payment_date="10 de diciembre de 2024",
        transaction_id="txn_abc123xyz789"
    )
    
    print("\n📧 ASUNTO:")
    print(response["subject"])
    print("\n" + "-" * 80)
    
    print("\n📄 CUERPO DEL EMAIL (TEXTO):")
    print(response["text_body"])
    print("\n" + "-" * 80)
    
    print("\n💻 HTML generado (primeros 500 caracteres):")
    print(response["html_body"][:500] + "...")
    print("\n" + "=" * 80)


def example_with_partial_info():
    """Ejemplo con información parcial."""
    print("\n" + "=" * 80)
    print("EJEMPLO 2: Uso con Información Parcial")
    print("=" * 80)
    
    ticket_data = {
        "ticket_id": "TKT-20241215-XYZ789",
        "customer_name": "Juan Pérez",
        "customer_email": "juan.perez@example.com"
    }
    
    # Solo tenemos información básica
    response = get_payment_verification_response_template(
        ticket_data=ticket_data,
        invoice_amount=150.00,
        credit_amount=150.00
    )
    
    print("\n📧 ASUNTO:")
    print(response["subject"])
    print("\n" + "-" * 80)
    
    print("\n📄 CUERPO DEL EMAIL (primeros 800 caracteres):")
    print(response["text_body"][:800] + "...")
    print("\n" + "=" * 80)


def example_tracking_instructions():
    """Ejemplo de uso de las instrucciones de rastreo."""
    print("\n" + "=" * 80)
    print("EJEMPLO 3: Instrucciones de Rastreo de Pagos")
    print("=" * 80)
    
    instructions = get_payment_tracking_instructions()
    
    print(f"\n📋 {instructions['title']}")
    print("\n" + "-" * 80)
    
    for step in instructions["steps"]:
        print(f"\n{step['step']}. {step['title']}")
        print(f"   {step['description']}")
        if step.get("details"):
            for detail in step["details"]:
                print(f"   • {detail}")
    
    print("\n" + "-" * 80)
    print("\n⏱️  Retrasos Comunes por Método de Pago:")
    print("-" * 80)
    
    for delay_info in instructions["common_delays"]:
        print(f"\n{delay_info['method']}:")
        print(f"  Retraso: {delay_info['delay']}")
        print(f"  Razón: {delay_info['reason']}")
    
    print("\n" + "-" * 80)
    print("\n⚠️  Cuándo Contactar a Soporte:")
    print("-" * 80)
    
    for reason in instructions["when_to_contact"]:
        print(f"  • {reason}")
    
    print("\n" + "=" * 80)


def example_integration_with_support_system():
    """Ejemplo de integración con el sistema de soporte."""
    print("\n" + "=" * 80)
    print("EJEMPLO 4: Integración con Sistema de Soporte")
    print("=" * 80)
    
    # Simular datos de un ticket real
    ticket_data = {
        "ticket_id": "TKT-20241215-DEF456",
        "customer_name": "Ana Martínez",
        "customer_email": "ana.martinez@example.com",
        "subject": "Factura pendiente a pesar de pago",
        "description": "Pagué la factura FAC-2024-001234 la semana pasada pero aún aparece como pendiente",
        "category": "billing",
        "subcategory": "payment_issue",
        "priority": "high",
        "assigned_agent_name": "Laura Sánchez"
    }
    
    # Extraer información de la factura (simulado)
    invoice_number = "FAC-2024-001234"
    invoice_amount = 450.00
    
    # Calcular crédito temporal (mismo monto o porcentaje)
    credit_amount = invoice_amount  # O podría ser un porcentaje: invoice_amount * 0.1
    
    # Generar respuesta
    response = get_payment_verification_response_template(
        ticket_data=ticket_data,
        invoice_number=invoice_number,
        invoice_amount=invoice_amount,
        credit_amount=credit_amount,
        payment_date="8 de diciembre de 2024"
    )
    
    print("\n✅ Template generado exitosamente")
    print(f"   Ticket ID: {ticket_data['ticket_id']}")
    print(f"   Cliente: {ticket_data['customer_name']}")
    print(f"   Factura: {invoice_number}")
    print(f"   Monto: ${invoice_amount:.2f}")
    print(f"   Crédito temporal: ${credit_amount:.2f}")
    
    print("\n📧 Email listo para enviar:")
    print(f"   Asunto: {response['subject']}")
    print(f"   Tamaño del cuerpo (texto): {len(response['text_body'])} caracteres")
    print(f"   Tamaño del cuerpo (HTML): {len(response['html_body'])} caracteres")
    
    # Aquí normalmente enviarías el email usando tu sistema de email
    # Ejemplo:
    # send_email(
    #     to=ticket_data["customer_email"],
    #     subject=response["subject"],
    #     text_body=response["text_body"],
    #     html_body=response["html_body"]
    # )
    
    print("\n💡 Próximos pasos:")
    print("   1. Enviar email al cliente")
    print("   2. Aplicar crédito temporal a la cuenta")
    print("   3. Crear tarea de seguimiento para verificar el pago en 24-48 horas")
    print("   4. Actualizar el ticket con la respuesta enviada")
    
    print("\n" + "=" * 80)


def example_automated_response_workflow():
    """Ejemplo de flujo automatizado para respuestas."""
    print("\n" + "=" * 80)
    print("EJEMPLO 5: Flujo Automatizado de Respuesta")
    print("=" * 80)
    
    print("""
Este template está diseñado para integrarse con sistemas de automatización
como Kestra, Airflow, o n8n para reducir escaladas en un 30-50%.

FLUJO AUTOMATIZADO:
==================

1. DETECCIÓN AUTOMÁTICA
   - Sistema detecta ticket con categoría "billing" y subcategoría "payment_issue"
   - Palabras clave: "pagado", "pago", "pendiente", "factura"
   
2. EXTRACCIÓN DE INFORMACIÓN
   - Número de factura (si está en el mensaje)
   - Monto (si está mencionado)
   - Fecha de pago (si está mencionada)
   
3. GENERACIÓN DE RESPUESTA
   - Usa este template para generar respuesta personalizada
   - Calcula crédito temporal (mismo monto o porcentaje)
   
4. APLICACIÓN DE CRÉDITO
   - Aplica crédito temporal a la cuenta del cliente
   - Registra la acción en el sistema de facturación
   
5. ENVÍO DE EMAIL
   - Envía email con respuesta empática y resolutiva
   - Actualiza ticket con estado "chatbot_handled" o "waiting_customer"
   
6. SEGUIMIENTO
   - Crea tarea de seguimiento para verificar pago en 24-48 horas
   - Notifica al equipo de facturación si no se resuelve automáticamente

BENEFICIOS:
==========
- Reduce escaladas en 30-50% según casos de estudio
- Mejora tiempo de respuesta (inmediato vs horas/días)
- Proporciona compensación proactiva (mejora satisfacción)
- Libera tiempo del equipo para casos más complejos
""")
    
    print("=" * 80)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("EJEMPLOS DE USO: Template de Verificación de Pagos")
    print("=" * 80)
    
    # Ejecutar ejemplos
    example_basic_usage()
    example_with_partial_info()
    example_tracking_instructions()
    example_integration_with_support_system()
    example_automated_response_workflow()
    
    print("\n✅ Todos los ejemplos completados")
    print("\n💡 Para usar este template en producción:")
    print("   1. Importa la función en tu workflow de Kestra/Airflow")
    print("   2. Configura los datos del ticket y factura")
    print("   3. Genera la respuesta usando get_payment_verification_response_template()")
    print("   4. Envía el email usando tu sistema de email")
    print("   5. Aplica el crédito temporal a la cuenta del cliente")
    print("\n")



