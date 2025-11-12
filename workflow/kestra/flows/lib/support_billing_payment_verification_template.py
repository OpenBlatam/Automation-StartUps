"""
Template de Respuesta para Verificación de Pagos y Facturas Pendientes.

Este módulo proporciona templates especializados para casos donde un cliente
afirma haber pagado pero la factura aún aparece como pendiente.

Útil para automatizar respuestas a quejas financieras, reduciendo escaladas
en un 30-50% según casos de estudio.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def get_payment_verification_response_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str] = None,
    invoice_amount: Optional[float] = None,
    credit_amount: Optional[float] = None,
    payment_date: Optional[str] = None,
    transaction_id: Optional[str] = None
) -> Dict[str, str]:
    """
    Genera una respuesta empática y resolutiva para casos de factura pendiente
    a pesar de pago reportado.
    
    Args:
        ticket_data: Datos del ticket (customer_name, ticket_id, etc.)
        invoice_number: Número de factura
        invoice_amount: Monto de la factura
        credit_amount: Monto del crédito temporal a ofrecer
        payment_date: Fecha del pago reportado
        transaction_id: ID de transacción si está disponible
        
    Returns:
        Dict con subject, text_body, html_body
    """
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    # Valores por defecto
    invoice_num = invoice_number or "tu factura"
    invoice_amt = f"${invoice_amount:.2f}" if invoice_amount else "el monto correspondiente"
    credit_amt = f"${credit_amount:.2f}" if credit_amount else "[monto]"
    pay_date = payment_date or "la semana pasada"
    trans_id = transaction_id or "tu transacción"
    
    subject = f"Verificación de pago - Ticket #{ticket_id}"
    
    text_body = f"""
Hola {customer_name},

Entiendo tu preocupación y lamento la confusión con el estado de {invoice_num}. 
Tu satisfacción es nuestra prioridad y vamos a resolver esto juntos.

PROCESO DE VERIFICACIÓN DE PAGOS
================================

Nuestro sistema verifica los pagos de la siguiente manera:

1. **Recepción del pago**: Cuando realizas un pago, nuestro procesador de pagos 
   (Stripe/PayPal/etc.) nos notifica inmediatamente.

2. **Procesamiento**: El pago puede tardar entre 1-3 días hábiles en reflejarse 
   completamente en nuestro sistema, especialmente si fue realizado:
   - En fin de semana o días festivos
   - Con transferencia bancaria
   - Con método de pago que requiere verificación adicional

3. **Actualización de estado**: Una vez procesado, la factura se marca 
   automáticamente como pagada y recibes una confirmación por email.

PASOS PARA RASTREAR TU TRANSACCIÓN
===================================

Para ayudarnos a localizar tu pago rápidamente, por favor comparte:

1. **Número de referencia de la transacción** (si lo tienes)
   - Puedes encontrarlo en el email de confirmación de pago
   - O en el extracto de tu tarjeta/bancario

2. **Fecha exacta del pago**: {pay_date}
   - Si recuerdas la hora aproximada, también ayuda

3. **Método de pago utilizado**:
   - Tarjeta de crédito/débito (últimos 4 dígitos)
   - Transferencia bancaria
   - PayPal u otro método

4. **Monto pagado**: {invoice_amt}

5. **Comprobante de pago** (si está disponible):
   - Captura de pantalla del comprobante
   - Email de confirmación del banco/procesador

COMPENSACIÓN TEMPORAL
=====================

Mientras verificamos tu pago, queremos asegurarnos de que no experimentes 
ninguna interrupción en el servicio. Por eso, te ofrecemos:

**Crédito temporal de {credit_amt}** aplicado a tu cuenta de inmediato.

Este crédito:
- Se aplicará automáticamente a tu próxima factura
- No expira
- Se ajustará automáticamente una vez confirmemos tu pago

PRÓXIMOS PASOS
==============

1. Nuestro equipo de facturación revisará tu caso en las próximas 24-48 horas
2. Te notificaremos por email tan pronto como confirmemos el pago
3. Si el crédito temporal no se ajusta automáticamente, lo haremos manualmente

Si tienes alguna pregunta adicional o información que compartir, puedes:
- Responder directamente a este email
- Acceder a tu portal de cliente: [enlace al portal]
- Contactarnos por teléfono: [número de soporte]

Agradecemos tu paciencia y comprensión. Estamos aquí para ayudarte.

Ticket ID: #{ticket_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos cordiales,
{get_agent_signature(ticket_data)}
Equipo de Soporte al Cliente
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: 600;
        }}
        .greeting {{
            font-size: 16px;
            margin-bottom: 20px;
            color: #555;
        }}
        .section {{
            margin: 25px 0;
            padding: 20px;
            background-color: #f9f9f9;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .section h2 {{
            color: #667eea;
            margin-top: 0;
            font-size: 18px;
            font-weight: 600;
        }}
        .section h3 {{
            color: #764ba2;
            margin-top: 15px;
            font-size: 16px;
            font-weight: 600;
        }}
        .section ul {{
            margin: 10px 0;
            padding-left: 25px;
        }}
        .section li {{
            margin: 8px 0;
            color: #555;
        }}
        .highlight-box {{
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 25px 0;
            text-align: center;
        }}
        .highlight-box h3 {{
            color: white;
            margin-top: 0;
            font-size: 20px;
        }}
        .highlight-box .amount {{
            font-size: 32px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .info-box {{
            background-color: #e3f2fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            border-radius: 4px;
        }}
        .steps-list {{
            counter-reset: step-counter;
            list-style: none;
            padding-left: 0;
        }}
        .steps-list li {{
            counter-increment: step-counter;
            margin: 15px 0;
            padding-left: 40px;
            position: relative;
        }}
        .steps-list li::before {{
            content: counter(step-counter);
            position: absolute;
            left: 0;
            top: 0;
            background-color: #667eea;
            color: white;
            width: 28px;
            height: 28px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
        .ticket-info {{
            background-color: #f5f5f5;
            padding: 10px;
            border-radius: 4px;
            font-size: 12px;
            color: #666;
            margin-top: 20px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px 5px;
            font-weight: 600;
        }}
        .button:hover {{
            background-color: #5568d3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Verificación de Pago</h1>
        </div>
        
        <div class="greeting">
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Entiendo tu preocupación y lamento la confusión con el estado de <strong>{invoice_num}</strong>. 
            Tu satisfacción es nuestra prioridad y vamos a resolver esto juntos.</p>
        </div>
        
        <div class="section">
            <h2>📋 Proceso de Verificación de Pagos</h2>
            <p>Nuestro sistema verifica los pagos de la siguiente manera:</p>
            <ol>
                <li><strong>Recepción del pago</strong>: Cuando realizas un pago, nuestro procesador de pagos 
                    (Stripe/PayPal/etc.) nos notifica inmediatamente.</li>
                <li><strong>Procesamiento</strong>: El pago puede tardar entre 1-3 días hábiles en reflejarse 
                    completamente en nuestro sistema, especialmente si fue realizado:
                    <ul>
                        <li>En fin de semana o días festivos</li>
                        <li>Con transferencia bancaria</li>
                        <li>Con método de pago que requiere verificación adicional</li>
                    </ul>
                </li>
                <li><strong>Actualización de estado</strong>: Una vez procesado, la factura se marca 
                    automáticamente como pagada y recibes una confirmación por email.</li>
            </ol>
        </div>
        
        <div class="section">
            <h2>🔎 Pasos para Rastrear tu Transacción</h2>
            <p>Para ayudarnos a localizar tu pago rápidamente, por favor comparte:</p>
            <ol class="steps-list">
                <li><strong>Número de referencia de la transacción</strong> (si lo tienes)
                    <br><small>Puedes encontrarlo en el email de confirmación de pago o en el extracto de tu tarjeta/bancario</small></li>
                <li><strong>Fecha exacta del pago</strong>: {pay_date}
                    <br><small>Si recuerdas la hora aproximada, también ayuda</small></li>
                <li><strong>Método de pago utilizado</strong>:
                    <br><small>Tarjeta de crédito/débito (últimos 4 dígitos), Transferencia bancaria, PayPal u otro método</small></li>
                <li><strong>Monto pagado</strong>: {invoice_amt}</li>
                <li><strong>Comprobante de pago</strong> (si está disponible):
                    <br><small>Captura de pantalla del comprobante o email de confirmación del banco/procesador</small></li>
            </ol>
        </div>
        
        <div class="highlight-box">
            <h3>💳 Compensación Temporal</h3>
            <p>Mientras verificamos tu pago, queremos asegurarnos de que no experimentes ninguna interrupción en el servicio.</p>
            <div class="amount">{credit_amt}</div>
            <p style="margin-bottom: 0;"><strong>Crédito temporal aplicado a tu cuenta de inmediato</strong></p>
            <div style="margin-top: 15px; font-size: 14px;">
                <p style="margin: 5px 0;">✓ Se aplicará automáticamente a tu próxima factura</p>
                <p style="margin: 5px 0;">✓ No expira</p>
                <p style="margin: 5px 0;">✓ Se ajustará automáticamente una vez confirmemos tu pago</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📅 Próximos Pasos</h2>
            <ol>
                <li>Nuestro equipo de facturación revisará tu caso en las próximas <strong>24-48 horas</strong></li>
                <li>Te notificaremos por email tan pronto como confirmemos el pago</li>
                <li>Si el crédito temporal no se ajusta automáticamente, lo haremos manualmente</li>
            </ol>
        </div>
        
        <div class="info-box">
            <p><strong>¿Necesitas más ayuda?</strong></p>
            <p style="margin-bottom: 10px;">Puedes:</p>
            <ul style="margin-top: 5px;">
                <li>Responder directamente a este email</li>
                <li>Acceder a tu portal de cliente: <a href="[enlace al portal]" style="color: #2196F3;">[enlace al portal]</a></li>
                <li>Contactarnos por teléfono: <strong>[número de soporte]</strong></li>
            </ul>
        </div>
        
        <p style="margin-top: 25px;">Agradecemos tu paciencia y comprensión. Estamos aquí para ayudarte.</p>
        
        <div class="ticket-info">
            <strong>Ticket ID:</strong> #{ticket_id}<br>
            <strong>Fecha:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M')}
        </div>
        
        <div class="footer">
            <p>Saludos cordiales,<br>
            <strong>{get_agent_signature(ticket_data)}</strong><br>
            Equipo de Soporte al Cliente</p>
            <p style="font-size: 11px; color: #999; margin-top: 20px;">
                Este es un email automático. Puedes responder directamente si necesitas más ayuda.
            </p>
        </div>
    </div>
</body>
</html>
"""
    
    return {
        "subject": subject,
        "text_body": text_body,
        "html_body": html_body
    }


def get_agent_signature(ticket_data: Dict[str, Any]) -> str:
    """Obtiene la firma del agente asignado o una genérica."""
    agent_name = ticket_data.get("assigned_agent_name")
    if agent_name:
        return agent_name
    return "Equipo de Soporte"


def get_payment_tracking_instructions() -> Dict[str, Any]:
    """
    Retorna instrucciones detalladas para rastrear pagos.
    Útil para incluir en FAQs o documentación.
    """
    return {
        "title": "Cómo rastrear un pago pendiente",
        "steps": [
            {
                "step": 1,
                "title": "Revisa tu email de confirmación",
                "description": "Busca el email de confirmación del procesador de pagos (Stripe, PayPal, etc.) que recibiste al realizar el pago.",
                "details": [
                    "El email generalmente llega inmediatamente después del pago",
                    "Contiene el número de referencia de la transacción",
                    "Incluye la fecha y hora exacta del pago"
                ]
            },
            {
                "step": 2,
                "title": "Verifica tu extracto bancario",
                "description": "Revisa tu extracto de tarjeta o cuenta bancaria para confirmar que el cargo fue procesado.",
                "details": [
                    "El cargo puede aparecer con un nombre diferente al de nuestra empresa",
                    "Puede tardar 1-3 días hábiles en aparecer",
                    "Anota el monto exacto y la fecha del cargo"
                ]
            },
            {
                "step": 3,
                "title": "Revisa el portal de cliente",
                "description": "Accede a tu portal de cliente para ver el historial de pagos y facturas.",
                "details": [
                    "Algunos pagos pueden estar en estado 'procesando'",
                    "Las transferencias bancarias pueden tardar más en reflejarse"
                ]
            },
            {
                "step": 4,
                "title": "Contacta a soporte con la información",
                "description": "Comparte toda la información recopilada con nuestro equipo de soporte.",
                "details": [
                    "Número de referencia de transacción",
                    "Fecha y hora del pago",
                    "Monto pagado",
                    "Método de pago utilizado",
                    "Comprobante o captura de pantalla si está disponible"
                ]
            }
        ],
        "common_delays": [
            {
                "method": "Transferencia bancaria",
                "delay": "3-5 días hábiles",
                "reason": "Requiere verificación manual del banco"
            },
            {
                "method": "Tarjeta de crédito/débito",
                "delay": "1-3 días hábiles",
                "reason": "Procesamiento estándar del banco emisor"
            },
            {
                "method": "PayPal",
                "delay": "1-2 días hábiles",
                "reason": "Procesamiento interno de PayPal"
            },
            {
                "method": "Cheque",
                "delay": "5-10 días hábiles",
                "reason": "Requiere depósito y verificación física"
            }
        ],
        "when_to_contact": [
            "Han pasado más de 5 días hábiles desde el pago",
            "El monto no coincide con el de la factura",
            "Recibiste un error durante el proceso de pago",
            "El pago fue rechazado pero se descontó de tu cuenta"
        ]
    }


def create_payment_verification_template_for_db(
    template_manager,
    db_connection
) -> str:
    """
    Crea y guarda el template en la base de datos usando TemplateManager.
    
    Returns:
        template_id del template creado
    """
    template_id = "billing_payment_verification_pending"
    
    template_content = """Hola {{customer_name}},

Entiendo tu preocupación y lamento la confusión con el estado de {{invoice_number}}. 
Tu satisfacción es nuestra prioridad y vamos a resolver esto juntos.

PROCESO DE VERIFICACIÓN DE PAGOS
================================

Nuestro sistema verifica los pagos de la siguiente manera:

1. **Recepción del pago**: Cuando realizas un pago, nuestro procesador de pagos 
   (Stripe/PayPal/etc.) nos notifica inmediatamente.

2. **Procesamiento**: El pago puede tardar entre 1-3 días hábiles en reflejarse 
   completamente en nuestro sistema, especialmente si fue realizado:
   - En fin de semana o días festivos
   - Con transferencia bancaria
   - Con método de pago que requiere verificación adicional

3. **Actualización de estado**: Una vez procesado, la factura se marca 
   automáticamente como pagada y recibes una confirmación por email.

PASOS PARA RASTREAR TU TRANSACCIÓN
===================================

Para ayudarnos a localizar tu pago rápidamente, por favor comparte:

1. **Número de referencia de la transacción** (si lo tienes)
   - Puedes encontrarlo en el email de confirmación de pago
   - O en el extracto de tu tarjeta/bancario

2. **Fecha exacta del pago**: {{payment_date}}
   - Si recuerdas la hora aproximada, también ayuda

3. **Método de pago utilizado**:
   - Tarjeta de crédito/débito (últimos 4 dígitos)
   - Transferencia bancaria
   - PayPal u otro método

4. **Monto pagado**: {{invoice_amount}}

5. **Comprobante de pago** (si está disponible):
   - Captura de pantalla del comprobante
   - Email de confirmación del banco/procesador

COMPENSACIÓN TEMPORAL
=====================

Mientras verificamos tu pago, queremos asegurarnos de que no experimentes 
ninguna interrupción en el servicio. Por eso, te ofrecemos:

**Crédito temporal de {{credit_amount}}** aplicado a tu cuenta de inmediato.

Este crédito:
- Se aplicará automáticamente a tu próxima factura
- No expira
- Se ajustará automáticamente una vez confirmemos tu pago

PRÓXIMOS PASOS
==============

1. Nuestro equipo de facturación revisará tu caso en las próximas 24-48 horas
2. Te notificaremos por email tan pronto como confirmemos el pago
3. Si el crédito temporal no se ajusta automáticamente, lo haremos manualmente

Si tienes alguna pregunta adicional o información que compartir, puedes:
- Responder directamente a este email
- Acceder a tu portal de cliente: [enlace al portal]
- Contactarnos por teléfono: [número de soporte]

Agradecemos tu paciencia y comprensión. Estamos aquí para ayudarte.

Ticket ID: #{{ticket_id}}
"""
    
    from .support_ticket_templates import TemplateManager, TemplateType, TemplateCategory
    
    manager = TemplateManager(db_connection)
    
    template = manager.create_template(
        template_id=template_id,
        title="Verificación de Pago - Factura Pendiente",
        description="Template para casos donde cliente afirma haber pagado pero factura aparece pendiente",
        template_type=TemplateType.RESPONSE,
        category=TemplateCategory.BILLING,
        content=template_content,
        tags=["billing", "payment", "verification", "pending", "invoice", "credit"],
        created_by="system"
    )
    
    logger.info(f"Created payment verification template: {template_id}")
    
    return template_id



