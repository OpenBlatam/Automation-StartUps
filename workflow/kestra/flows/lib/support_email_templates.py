"""
Templates de Email para Notificaciones de Soporte.

Provee templates HTML y texto para:
- Confirmación de ticket recibido
- Respuesta del chatbot
- Asignación a agente
- Resolución de ticket
- Solicitud de feedback
"""
from typing import Dict, Any, Optional
from datetime import datetime


def get_ticket_confirmation_template(ticket_data: Dict[str, Any]) -> Dict[str, str]:
    """
    Template para confirmación de ticket recibido.
    
    Args:
        ticket_data: Datos del ticket
        
    Returns:
        Dict con subject, text_body, html_body
    """
    ticket_id = ticket_data.get("ticket_id", "N/A")
    subject_ticket = ticket_data.get("subject", "Sin asunto")
    customer_name = ticket_data.get("customer_name", "Cliente")
    
    subject = f"Ticket #{ticket_id} - Hemos recibido tu consulta"
    
    text_body = f"""
Hola {customer_name},

Hemos recibido tu consulta y hemos creado el ticket #{ticket_id}.

Asunto: {subject_ticket}

Nuestro equipo revisará tu consulta y te responderá pronto. Si tienes información adicional, puedes responder a este email.

Sigue el estado de tu ticket en: [enlace al portal]

Gracias por contactarnos.

Saludos,
Equipo de Soporte
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .ticket-info {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ticket Recibido</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Hemos recibido tu consulta y hemos creado el ticket <strong>#{ticket_id}</strong>.</p>
            
            <div class="ticket-info">
                <p><strong>Asunto:</strong> {subject_ticket}</p>
                <p><strong>Ticket ID:</strong> {ticket_id}</p>
            </div>
            
            <p>Nuestro equipo revisará tu consulta y te responderá pronto. Si tienes información adicional, puedes responder a este email.</p>
            
            <p>Gracias por contactarnos.</p>
            
            <p>Saludos,<br>Equipo de Soporte</p>
        </div>
        <div class="footer">
            <p>Este es un email automático. Por favor, no respondas directamente a este mensaje.</p>
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


def get_chatbot_response_template(ticket_data: Dict[str, Any], chatbot_response: str) -> Dict[str, str]:
    """
    Template para respuesta del chatbot.
    
    Args:
        ticket_data: Datos del ticket
        chatbot_response: Respuesta del chatbot
        
    Returns:
        Dict con subject, text_body, html_body
    """
    ticket_id = ticket_data.get("ticket_id", "N/A")
    customer_name = ticket_data.get("customer_name", "Cliente")
    
    subject = f"Respuesta a tu consulta - Ticket #{ticket_id}"
    
    text_body = f"""
Hola {customer_name},

Hemos procesado tu consulta y aquí está la respuesta:

{chatbot_response}

Si esta respuesta no resuelve tu consulta, puedes responder a este email y nuestro equipo te ayudará.

Ticket ID: #{ticket_id}

Saludos,
Equipo de Soporte
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .response-box {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #2196F3; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Respuesta a tu Consulta</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Hemos procesado tu consulta y aquí está la respuesta:</p>
            
            <div class="response-box">
                <p>{chatbot_response.replace(chr(10), '<br>')}</p>
            </div>
            
            <p>Si esta respuesta no resuelve tu consulta, puedes responder a este email y nuestro equipo te ayudará.</p>
            
            <p><strong>Ticket ID:</strong> #{ticket_id}</p>
            
            <p>Saludos,<br>Equipo de Soporte</p>
        </div>
        <div class="footer">
            <p>Esta respuesta fue generada automáticamente. Si necesitas más ayuda, responde a este email.</p>
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


def get_agent_assigned_template(ticket_data: Dict[str, Any], agent_name: str) -> Dict[str, str]:
    """
    Template para notificación de asignación a agente.
    
    Args:
        ticket_data: Datos del ticket
        agent_name: Nombre del agente asignado
        
    Returns:
        Dict con subject, text_body, html_body
    """
    ticket_id = ticket_data.get("ticket_id", "N/A")
    customer_name = ticket_data.get("customer_name", "Cliente")
    
    subject = f"Tu ticket #{ticket_id} ha sido asignado a un agente"
    
    text_body = f"""
Hola {customer_name},

Tu ticket #{ticket_id} ha sido asignado a {agent_name}, quien se encargará de ayudarte.

Te responderemos pronto. Si tienes información adicional, puedes responder a este email.

Ticket ID: #{ticket_id}

Saludos,
Equipo de Soporte
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #FF9800; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .info-box {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #FF9800; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Ticket Asignado</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Tu ticket <strong>#{ticket_id}</strong> ha sido asignado a <strong>{agent_name}</strong>, quien se encargará de ayudarte.</p>
            
            <div class="info-box">
                <p><strong>Agente asignado:</strong> {agent_name}</p>
                <p><strong>Ticket ID:</strong> #{ticket_id}</p>
            </div>
            
            <p>Te responderemos pronto. Si tienes información adicional, puedes responder a este email.</p>
            
            <p>Saludos,<br>Equipo de Soporte</p>
        </div>
        <div class="footer">
            <p>Este es un email automático. Por favor, no respondas directamente a este mensaje.</p>
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


def get_resolution_template(ticket_data: Dict[str, Any], resolution_notes: Optional[str] = None) -> Dict[str, str]:
    """
    Template para notificación de resolución de ticket.
    
    Args:
        ticket_data: Datos del ticket
        resolution_notes: Notas de resolución (opcional)
        
    Returns:
        Dict con subject, text_body, html_body
    """
    ticket_id = ticket_data.get("ticket_id", "N/A")
    customer_name = ticket_data.get("customer_name", "Cliente")
    
    subject = f"Tu ticket #{ticket_id} ha sido resuelto"
    
    resolution_text = resolution_notes or "Tu consulta ha sido resuelta. Si necesitas más ayuda, no dudes en contactarnos."
    
    text_body = f"""
Hola {customer_name},

Tu ticket #{ticket_id} ha sido marcado como resuelto.

{resolution_text}

Si tienes alguna otra consulta, puedes crear un nuevo ticket o responder a este email.

¿Cómo fue tu experiencia? Nos encantaría conocer tu opinión.

Ticket ID: #{ticket_id}

Saludos,
Equipo de Soporte
"""
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; background-color: #f9f9f9; }}
        .resolution-box {{ background-color: white; padding: 15px; margin: 15px 0; border-left: 4px solid #4CAF50; }}
        .footer {{ text-align: center; padding: 20px; color: #666; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✓ Ticket Resuelto</h1>
        </div>
        <div class="content">
            <p>Hola <strong>{customer_name}</strong>,</p>
            <p>Tu ticket <strong>#{ticket_id}</strong> ha sido marcado como resuelto.</p>
            
            <div class="resolution-box">
                <p>{resolution_text.replace(chr(10), '<br>')}</p>
            </div>
            
            <p>Si tienes alguna otra consulta, puedes crear un nuevo ticket o responder a este email.</p>
            
            <p><strong>¿Cómo fue tu experiencia?</strong> Nos encantaría conocer tu opinión.</p>
            
            <p><strong>Ticket ID:</strong> #{ticket_id}</p>
            
            <p>Saludos,<br>Equipo de Soporte</p>
        </div>
        <div class="footer">
            <p>Este es un email automático. Puedes responder si necesitas más ayuda.</p>
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


def get_payment_verification_template(ticket_data: Dict[str, Any], **kwargs) -> Dict[str, str]:
    """
    Wrapper para el template de verificación de pagos.
    
    Para casos donde un cliente afirma haber pagado pero la factura aparece pendiente.
    Ver: support_billing_payment_verification_template.py para la implementación completa.
    
    Args:
        ticket_data: Datos del ticket
        **kwargs: Argumentos adicionales (invoice_number, invoice_amount, credit_amount, etc.)
        
    Returns:
        Dict con subject, text_body, html_body
    """
    from .support_billing_payment_verification_template import (
        get_payment_verification_response_template
    )
    return get_payment_verification_response_template(ticket_data, **kwargs)

