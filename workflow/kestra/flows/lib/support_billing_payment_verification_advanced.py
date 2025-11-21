"""
Template Avanzado de Verificación de Pagos - Versión Mejorada.

Incluye:
- Soporte multi-idioma (i18n)
- Variantes según escenario (pago reciente, pago antiguo, múltiples facturas)
- Integración con sistemas de créditos
- Personalización según historial del cliente
- Analytics y métricas
- Respuestas adaptativas según urgencia
"""
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class PaymentScenario(Enum):
    """Escenarios de pago."""
    RECENT_PAYMENT = "recent_payment"  # Pago hace menos de 7 días
    OLD_PAYMENT = "old_payment"  # Pago hace más de 7 días
    MULTIPLE_INVOICES = "multiple_invoices"  # Múltiples facturas pendientes
    PARTIAL_PAYMENT = "partial_payment"  # Pago parcial
    RECURRING_ISSUE = "recurring_issue"  # Cliente con historial de problemas similares
    VIP_CUSTOMER = "vip_customer"  # Cliente VIP/Enterprise


class CustomerTier(Enum):
    """Niveles de cliente."""
    STANDARD = "standard"
    PREMIUM = "premium"
    VIP = "vip"
    ENTERPRISE = "enterprise"


def get_advanced_payment_verification_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str] = None,
    invoice_amount: Optional[float] = None,
    credit_amount: Optional[float] = None,
    payment_date: Optional[str] = None,
    transaction_id: Optional[str] = None,
    payment_method: Optional[str] = None,
    scenario: Optional[PaymentScenario] = None,
    customer_tier: CustomerTier = CustomerTier.STANDARD,
    customer_history: Optional[Dict[str, Any]] = None,
    language: str = "es",
    urgency_level: str = "normal"
) -> Dict[str, str]:
    """
    Genera respuesta avanzada con personalización según múltiples factores.
    
    Args:
        ticket_data: Datos del ticket
        invoice_number: Número de factura
        invoice_amount: Monto de la factura
        credit_amount: Monto del crédito temporal
        payment_date: Fecha del pago reportado
        transaction_id: ID de transacción
        payment_method: Método de pago (stripe, paypal, bank_transfer, etc.)
        scenario: Escenario de pago
        customer_tier: Nivel del cliente
        customer_history: Historial del cliente (previous_tickets, payment_history, etc.)
        language: Idioma (es, en, pt, fr)
        urgency_level: Nivel de urgencia (low, normal, high, urgent)
        
    Returns:
        Dict con subject, text_body, html_body, metadata
    """
    # Detectar escenario si no se proporciona
    if not scenario:
        scenario = _detect_scenario(payment_date, customer_history)
    
    # Calcular crédito si no se proporciona
    if not credit_amount and invoice_amount:
        credit_amount = _calculate_credit_amount(
            invoice_amount, customer_tier, scenario, customer_history
        )
    
    # Seleccionar template según escenario
    if scenario == PaymentScenario.RECENT_PAYMENT:
        return _get_recent_payment_template(
            ticket_data, invoice_number, invoice_amount, credit_amount,
            payment_date, transaction_id, payment_method, customer_tier,
            language, urgency_level
        )
    elif scenario == PaymentScenario.OLD_PAYMENT:
        return _get_old_payment_template(
            ticket_data, invoice_number, invoice_amount, credit_amount,
            payment_date, transaction_id, payment_method, customer_tier,
            language, urgency_level
        )
    elif scenario == PaymentScenario.MULTIPLE_INVOICES:
        return _get_multiple_invoices_template(
            ticket_data, invoice_number, invoice_amount, credit_amount,
            payment_date, transaction_id, customer_tier, language
        )
    elif scenario == PaymentScenario.RECURRING_ISSUE:
        return _get_recurring_issue_template(
            ticket_data, invoice_number, invoice_amount, credit_amount,
            payment_date, transaction_id, customer_tier, customer_history,
            language
        )
    else:
        # Template estándar mejorado
        return _get_standard_advanced_template(
            ticket_data, invoice_number, invoice_amount, credit_amount,
            payment_date, transaction_id, payment_method, customer_tier,
            language, urgency_level
        )


def _detect_scenario(
    payment_date: Optional[str],
    customer_history: Optional[Dict[str, Any]]
) -> PaymentScenario:
    """Detecta el escenario basado en la fecha y el historial."""
    if customer_history:
        # Verificar si es un problema recurrente
        similar_tickets = customer_history.get("similar_tickets_count", 0)
        if similar_tickets >= 2:
            return PaymentScenario.RECURRING_ISSUE
        
        # Verificar múltiples facturas pendientes
        pending_invoices = customer_history.get("pending_invoices_count", 0)
        if pending_invoices > 1:
            return PaymentScenario.MULTIPLE_INVOICES
    
    # Verificar antigüedad del pago
    if payment_date:
        try:
            # Intentar parsear la fecha
            if "hace" in payment_date.lower() or "días" in payment_date.lower():
                # Extraer número de días
                days_ago = _extract_days_from_text(payment_date)
                if days_ago and days_ago > 7:
                    return PaymentScenario.OLD_PAYMENT
        except:
            pass
    
    return PaymentScenario.RECENT_PAYMENT


def _extract_days_from_text(text: str) -> Optional[int]:
    """Extrae número de días de un texto como 'hace 10 días'."""
    import re
    match = re.search(r'(\d+)\s*d[ií]as?', text.lower())
    if match:
        return int(match.group(1))
    return None


def _calculate_credit_amount(
    invoice_amount: float,
    customer_tier: CustomerTier,
    scenario: PaymentScenario,
    customer_history: Optional[Dict[str, Any]]
) -> float:
    """Calcula el monto del crédito según múltiples factores."""
    base_credit = invoice_amount
    
    # Ajustar según nivel del cliente
    tier_multipliers = {
        CustomerTier.STANDARD: 1.0,
        CustomerTier.PREMIUM: 1.0,
        CustomerTier.VIP: 1.0,  # VIP siempre recibe crédito completo
        CustomerTier.ENTERPRISE: 1.0  # Enterprise siempre recibe crédito completo
    }
    
    multiplier = tier_multipliers.get(customer_tier, 1.0)
    
    # Ajustar según escenario
    if scenario == PaymentScenario.RECURRING_ISSUE:
        # Crédito completo para problemas recurrentes
        multiplier = 1.0
    elif scenario == PaymentScenario.OLD_PAYMENT:
        # Crédito completo para pagos antiguos
        multiplier = 1.0
    
    # Ajustar según historial de pagos
    if customer_history:
        payment_reliability = customer_history.get("payment_reliability_score", 1.0)
        if payment_reliability > 0.9:
            # Cliente confiable, crédito completo
            multiplier = 1.0
    
    return round(base_credit * multiplier, 2)


def _get_recent_payment_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str],
    invoice_amount: Optional[float],
    credit_amount: Optional[float],
    payment_date: Optional[str],
    transaction_id: Optional[str],
    payment_method: Optional[str],
    customer_tier: CustomerTier,
    language: str,
    urgency_level: str
) -> Dict[str, str]:
    """Template para pagos recientes (menos de 7 días)."""
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    # Mensaje optimista para pagos recientes
    if language == "es":
        subject = f"Verificando tu pago reciente - Ticket #{ticket_id}"
        
        greeting = f"""Hola {customer_name},

Gracias por contactarnos. Hemos recibido tu consulta sobre el pago de {invoice_number or 'tu factura'} 
y estamos verificándolo activamente.

Como el pago fue realizado recientemente ({payment_date or 'hace poco'}), es normal que aún esté 
en proceso de verificación. Nuestro sistema tarda entre 1-3 días hábiles en actualizar el estado 
de las facturas, especialmente si el pago fue realizado:
- En fin de semana o días festivos
- Con transferencia bancaria
- Con método de pago que requiere verificación adicional

**Buenas noticias**: Mientras verificamos tu pago, hemos aplicado un crédito temporal de 
${credit_amount:.2f if credit_amount else 0:.2f} a tu cuenta para asegurar que no experimentes 
ninguna interrupción en el servicio.

**¿Qué necesitamos de ti?**
Para acelerar la verificación, sería útil si pudieras compartir:
1. Número de referencia de la transacción: {transaction_id or 'Si lo tienes disponible'}
2. Comprobante de pago (captura de pantalla o email de confirmación)
3. Últimos 4 dígitos de la tarjeta o método de pago utilizado

**Próximos pasos:**
- Nuestro equipo revisará tu caso en las próximas 24 horas
- Te notificaremos por email tan pronto como confirmemos el pago
- El crédito temporal se ajustará automáticamente una vez confirmado

Si tienes alguna pregunta, no dudes en responder a este email.

Ticket ID: #{ticket_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos cordiales,
Equipo de Soporte al Cliente"""
    else:
        # English version
        subject = f"Verifying your recent payment - Ticket #{ticket_id}"
        greeting = f"""Hello {customer_name},

Thank you for contacting us. We have received your inquiry about the payment for {invoice_number or 'your invoice'} 
and we are actively verifying it.

Since the payment was made recently ({payment_date or 'recently'}), it's normal that it's still 
being processed. Our system takes 1-3 business days to update invoice status, especially if the payment was made:
- On weekends or holidays
- Via bank transfer
- With a payment method that requires additional verification

**Good news**: While we verify your payment, we have applied a temporary credit of 
${credit_amount:.2f if credit_amount else 0:.2f} to your account to ensure you don't experience 
any service interruption.

**What we need from you:**
To speed up verification, it would be helpful if you could share:
1. Transaction reference number: {transaction_id or 'If available'}
2. Payment receipt (screenshot or confirmation email)
3. Last 4 digits of the card or payment method used

**Next steps:**
- Our team will review your case within the next 24 hours
- We'll notify you by email as soon as we confirm the payment
- The temporary credit will be automatically adjusted once confirmed

If you have any questions, please don't hesitate to reply to this email.

Ticket ID: #{ticket_id}
Date: {datetime.now().strftime('%m/%d/%Y %H:%M')}

Best regards,
Customer Support Team"""
    
    return {
        "subject": subject,
        "text_body": greeting,
        "html_body": _generate_html_body(greeting, subject, ticket_id, customer_name, language),
        "metadata": {
            "scenario": "recent_payment",
            "urgency": urgency_level,
            "customer_tier": customer_tier.value,
            "language": language
        }
    }


def _get_old_payment_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str],
    invoice_amount: Optional[float],
    credit_amount: Optional[float],
    payment_date: Optional[str],
    transaction_id: Optional[str],
    payment_method: Optional[str],
    customer_tier: CustomerTier,
    language: str,
    urgency_level: str
) -> Dict[str, str]:
    """Template para pagos antiguos (más de 7 días)."""
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    if language == "es":
        subject = f"Investigación prioritaria de pago - Ticket #{ticket_id}"
        
        greeting = f"""Hola {customer_name},

Entendemos tu preocupación y nos disculpamos por la demora. Hemos marcado tu caso como 
prioritario ya que el pago fue realizado hace más tiempo ({payment_date or 'varios días'}).

**Acción inmediata tomada:**
1. ✅ Hemos aplicado un crédito temporal de ${credit_amount:.2f if credit_amount else 0:.2f} a tu cuenta
2. ✅ Hemos escalado tu caso al equipo de facturación para investigación prioritaria
3. ✅ Hemos creado una tarea de seguimiento para resolver esto en las próximas 24 horas

**Para ayudarnos a resolver esto rápidamente, necesitamos:**
1. Número de referencia de la transacción: {transaction_id or 'Por favor compártelo'}
2. Comprobante de pago completo (captura de pantalla o PDF)
3. Extracto bancario o de tarjeta mostrando el cargo
4. Fecha exacta y hora del pago (si la recuerdas)
5. Método de pago utilizado: {payment_method or 'Por favor especifica'}

**Nuestro compromiso:**
- Investigación completa en las próximas 24 horas
- Actualización por email con los hallazgos
- Resolución inmediata una vez confirmado el pago
- Si no encontramos el pago, trabajaremos contigo para encontrar una solución

**Contacto directo:**
Si prefieres hablar directamente con nuestro equipo, puedes contactarnos en [número de teléfono] 
o responder a este email y te conectaremos con un especialista.

Agradecemos tu paciencia y nos disculpamos por cualquier inconveniente.

Ticket ID: #{ticket_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos cordiales,
Equipo de Soporte al Cliente - Prioridad Alta"""
    else:
        subject = f"Priority payment investigation - Ticket #{ticket_id}"
        greeting = f"""Hello {customer_name},

We understand your concern and apologize for the delay. We have marked your case as 
priority since the payment was made some time ago ({payment_date or 'several days ago'}).

**Immediate action taken:**
1. ✅ We have applied a temporary credit of ${credit_amount:.2f if credit_amount else 0:.2f} to your account
2. ✅ We have escalated your case to the billing team for priority investigation
3. ✅ We have created a follow-up task to resolve this within the next 24 hours

**To help us resolve this quickly, we need:**
1. Transaction reference number: {transaction_id or 'Please share it'}
2. Complete payment receipt (screenshot or PDF)
3. Bank or card statement showing the charge
4. Exact date and time of payment (if you remember)
5. Payment method used: {payment_method or 'Please specify'}

**Our commitment:**
- Complete investigation within the next 24 hours
- Email update with findings
- Immediate resolution once payment is confirmed
- If we don't find the payment, we'll work with you to find a solution

**Direct contact:**
If you prefer to speak directly with our team, you can contact us at [phone number] 
or reply to this email and we'll connect you with a specialist.

We appreciate your patience and apologize for any inconvenience.

Ticket ID: #{ticket_id}
Date: {datetime.now().strftime('%m/%d/%Y %H:%M')}

Best regards,
Customer Support Team - High Priority"""
    
    return {
        "subject": subject,
        "text_body": greeting,
        "html_body": _generate_html_body(greeting, subject, ticket_id, customer_name, language, urgent=True),
        "metadata": {
            "scenario": "old_payment",
            "urgency": "high",
            "customer_tier": customer_tier.value,
            "language": language,
            "escalated": True
        }
    }


def _get_multiple_invoices_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str],
    invoice_amount: Optional[float],
    credit_amount: Optional[float],
    payment_date: Optional[str],
    transaction_id: Optional[str],
    customer_tier: CustomerTier,
    language: str
) -> Dict[str, str]:
    """Template para múltiples facturas pendientes."""
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    if language == "es":
        subject = f"Revisión de múltiples facturas - Ticket #{ticket_id}"
        greeting = f"""Hola {customer_name},

Hemos notado que tienes múltiples facturas pendientes en tu cuenta. Entendemos que esto 
puede ser confuso y queremos ayudarte a resolverlo.

**Situación actual:**
Hemos identificado que tienes varias facturas que aparecen como pendientes. Estamos 
revisando cada una de ellas para determinar su estado real.

**Acción tomada:**
1. ✅ Hemos aplicado un crédito temporal de ${credit_amount:.2f if credit_amount else 0:.2f} a tu cuenta
2. ✅ Hemos iniciado una revisión completa de todas tus facturas pendientes
3. ✅ Hemos asignado un especialista para coordinar la resolución

**Para ayudarnos:**
Por favor, comparte información sobre los pagos que realizaste:
- Números de factura afectadas
- Fechas de pago
- Montos pagados
- Comprobantes de pago (si están disponibles)

**Próximos pasos:**
- Revisión completa en las próximas 48 horas
- Actualización con el estado de cada factura
- Ajuste automático de créditos según corresponda

Ticket ID: #{ticket_id}

Saludos,
Equipo de Facturación"""
    else:
        subject = f"Multiple invoices review - Ticket #{ticket_id}"
        greeting = f"""Hello {customer_name},

We have noticed that you have multiple pending invoices in your account. We understand this 
can be confusing and we want to help you resolve it.

**Current situation:**
We have identified that you have several invoices that appear as pending. We are 
reviewing each one to determine their actual status.

**Action taken:**
1. ✅ We have applied a temporary credit of ${credit_amount:.2f if credit_amount else 0:.2f} to your account
2. ✅ We have initiated a complete review of all your pending invoices
3. ✅ We have assigned a specialist to coordinate the resolution

**To help us:**
Please share information about the payments you made:
- Affected invoice numbers
- Payment dates
- Amounts paid
- Payment receipts (if available)

**Next steps:**
- Complete review within the next 48 hours
- Update with the status of each invoice
- Automatic credit adjustment as appropriate

Ticket ID: #{ticket_id}

Best regards,
Billing Team"""
    
    return {
        "subject": subject,
        "text_body": greeting,
        "html_body": _generate_html_body(greeting, subject, ticket_id, customer_name, language),
        "metadata": {
            "scenario": "multiple_invoices",
            "customer_tier": customer_tier.value,
            "language": language
        }
    }


def _get_recurring_issue_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str],
    invoice_amount: Optional[float],
    credit_amount: Optional[float],
    payment_date: Optional[str],
    transaction_id: Optional[str],
    customer_tier: CustomerTier,
    customer_history: Optional[Dict[str, Any]],
    language: str
) -> Dict[str, str]:
    """Template para problemas recurrentes."""
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    if language == "es":
        subject = f"Revisión especial - Problema recurrente - Ticket #{ticket_id}"
        greeting = f"""Hola {customer_name},

Hemos notado que este es un problema que has experimentado anteriormente. Queremos 
asegurarnos de resolverlo de manera definitiva esta vez.

**Nuestro compromiso:**
1. ✅ Crédito inmediato de ${credit_amount:.2f if credit_amount else 0:.2f} aplicado
2. ✅ Revisión profunda del sistema para identificar la causa raíz
3. ✅ Implementación de medidas preventivas para evitar que esto vuelva a ocurrir
4. ✅ Asignación de un gestor de cuenta dedicado para seguimiento

**Investigación:**
Estamos revisando:
- Historial de pagos anteriores
- Configuración de tu cuenta
- Procesos de sincronización con procesadores de pago
- Posibles problemas técnicos

**Solución a largo plazo:**
Una vez identificada la causa, implementaremos una solución permanente para evitar 
que este problema se repita.

**Contacto directo:**
Hemos asignado un especialista que se pondrá en contacto contigo en las próximas 24 horas 
para coordinar la resolución y discutir medidas preventivas.

Ticket ID: #{ticket_id}

Saludos,
Equipo de Soporte Especializado"""
    else:
        subject = f"Special review - Recurring issue - Ticket #{ticket_id}"
        greeting = f"""Hello {customer_name},

We have noticed that this is an issue you have experienced before. We want to 
make sure we resolve it definitively this time.

**Our commitment:**
1. ✅ Immediate credit of ${credit_amount:.2f if credit_amount else 0:.2f} applied
2. ✅ Deep system review to identify the root cause
3. ✅ Implementation of preventive measures to avoid this happening again
4. ✅ Assignment of a dedicated account manager for follow-up

**Investigation:**
We are reviewing:
- Previous payment history
- Your account configuration
- Synchronization processes with payment processors
- Possible technical issues

**Long-term solution:**
Once the cause is identified, we will implement a permanent solution to prevent 
this problem from recurring.

**Direct contact:**
We have assigned a specialist who will contact you within the next 24 hours 
to coordinate the resolution and discuss preventive measures.

Ticket ID: #{ticket_id}

Best regards,
Specialized Support Team"""
    
    return {
        "subject": subject,
        "text_body": greeting,
        "html_body": _generate_html_body(greeting, subject, ticket_id, customer_name, language),
        "metadata": {
            "scenario": "recurring_issue",
            "customer_tier": customer_tier.value,
            "language": language,
            "requires_root_cause_analysis": True
        }
    }


def _get_standard_advanced_template(
    ticket_data: Dict[str, Any],
    invoice_number: Optional[str],
    invoice_amount: Optional[float],
    credit_amount: Optional[float],
    payment_date: Optional[str],
    transaction_id: Optional[str],
    payment_method: Optional[str],
    customer_tier: CustomerTier,
    language: str,
    urgency_level: str
) -> Dict[str, str]:
    """Template estándar mejorado."""
    # Usar el template original pero con mejoras
    from .support_billing_payment_verification_template import (
        get_payment_verification_response_template
    )
    
    response = get_payment_verification_response_template(
        ticket_data=ticket_data,
        invoice_number=invoice_number,
        invoice_amount=invoice_amount,
        credit_amount=credit_amount,
        payment_date=payment_date,
        transaction_id=transaction_id
    )
    
    # Agregar metadata
    response["metadata"] = {
        "scenario": "standard",
        "urgency": urgency_level,
        "customer_tier": customer_tier.value,
        "language": language
    }
    
    return response


def _generate_html_body(
    text_body: str,
    subject: str,
    ticket_id: str,
    customer_name: str,
    language: str,
    urgent: bool = False
) -> str:
    """Genera HTML a partir del texto."""
    # Convertir texto a HTML básico
    html_content = text_body.replace("\n\n", "</p><p>").replace("\n", "<br>")
    html_content = f"<p>{html_content}</p>"
    
    # Estilos según urgencia
    header_color = "#f5576c" if urgent else "#667eea"
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
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
            background: linear-gradient(135deg, {header_color} 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
            text-align: center;
        }}
        .content {{
            padding: 20px 0;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            text-align: center;
            color: #666;
            font-size: 13px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{subject}</h1>
        </div>
        <div class="content">
            {html_content}
        </div>
        <div class="footer">
            <p>Ticket ID: #{ticket_id}</p>
        </div>
    </div>
</body>
</html>
"""


def apply_credit_to_account(
    customer_id: str,
    amount: float,
    reason: str,
    invoice_id: Optional[str] = None,
    db_connection = None
) -> Dict[str, Any]:
    """
    Aplica crédito a la cuenta del cliente.
    
    Integra con sistemas de facturación existentes.
    """
    if not db_connection:
        logger.warning("No database connection provided, credit not applied")
        return {"status": "skipped", "reason": "no_db_connection"}
    
    try:
        with db_connection.cursor() as cur:
            # Insertar crédito
            cur.execute("""
                INSERT INTO customer_credits 
                (customer_id, amount, reason, invoice_id, created_at)
                VALUES (%s, %s, %s, %s, NOW())
                RETURNING id
            """, (customer_id, amount, reason, invoice_id))
            
            credit_id = cur.fetchone()[0]
            db_connection.commit()
            
            logger.info(f"Credit applied: {credit_id} for customer {customer_id}")
            
            return {
                "status": "success",
                "credit_id": credit_id,
                "amount": amount,
                "customer_id": customer_id
            }
    except Exception as e:
        logger.error(f"Failed to apply credit: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


def track_payment_verification_metrics(
    ticket_id: str,
    scenario: PaymentScenario,
    customer_tier: CustomerTier,
    resolution_time: Optional[float] = None,
    customer_satisfaction: Optional[float] = None
) -> None:
    """Registra métricas para análisis."""
    metrics = {
        "ticket_id": ticket_id,
        "scenario": scenario.value,
        "customer_tier": customer_tier.value,
        "timestamp": datetime.now().isoformat(),
        "resolution_time_hours": resolution_time,
        "customer_satisfaction": customer_satisfaction
    }
    
    logger.info(f"Payment verification metrics: {metrics}")
    # Aquí se podría integrar con sistemas de analytics como Prometheus, Datadog, etc.



