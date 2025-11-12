"""
Templates de Respuesta para Troubleshooting - Versión Mejorada.

Proporciona templates empáticos y resolutivos para guiar a clientes
a través de procesos de troubleshooting paso a paso.

Características:
- Respuestas claras y accesibles para no técnicos
- Instrucciones paso a paso con verificaciones
- Precauciones y advertencias de seguridad
- Enlaces a recursos y documentación
- Sugerencias de escalación cuando es necesario
- Personalización según nivel técnico del cliente
- Soporte multi-idioma
"""
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class TechnicalLevel(Enum):
    """Nivel técnico del cliente."""
    BEGINNER = "beginner"  # No técnico, necesita guía detallada
    INTERMEDIATE = "intermediate"  # Conocimiento básico
    ADVANCED = "advanced"  # Conocimiento técnico avanzado
    EXPERT = "expert"  # Experto técnico


class ProblemComplexity(Enum):
    """Complejidad del problema."""
    SIMPLE = "simple"  # Resolución rápida, pasos básicos
    MODERATE = "moderate"  # Requiere varios pasos
    COMPLEX = "complex"  # Múltiples pasos, posible escalación
    CRITICAL = "critical"  # Requiere escalación inmediata


def get_troubleshooting_start_template(
    ticket_data: Dict[str, Any],
    problem_description: str,
    detected_problem: Optional[Dict[str, Any]] = None,
    technical_level: TechnicalLevel = TechnicalLevel.BEGINNER,
    complexity: ProblemComplexity = ProblemComplexity.MODERATE,
    language: str = "es"
) -> Dict[str, str]:
    """
    Genera template para iniciar sesión de troubleshooting.
    
    Args:
        ticket_data: Datos del ticket
        problem_description: Descripción del problema
        detected_problem: Problema detectado (si aplica)
        technical_level: Nivel técnico del cliente
        complexity: Complejidad del problema
        language: Idioma
        
    Returns:
        Dict con subject, text_body, html_body, metadata
    """
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    session_id = ticket_data.get("session_id", "N/A")
    
    problem_title = detected_problem.get("title", "tu problema") if detected_problem else "tu problema"
    estimated_steps = detected_problem.get("estimated_steps", 3) if detected_problem else 3
    estimated_time = detected_problem.get("estimated_time_minutes", 10) if detected_problem else 10
    
    if language == "es":
        subject = f"Guía de solución paso a paso - Ticket #{ticket_id}"
        
        greeting = f"""Hola {customer_name},

Gracias por contactarnos. Hemos analizado tu problema y hemos preparado una guía 
personalizada para ayudarte a resolverlo paso a paso.

**Problema identificado:**
{problem_title}

**Nuestra guía incluye:**
✅ Instrucciones claras y fáciles de seguir
✅ Verificaciones en cada paso para asegurar que todo funcione
✅ Precauciones de seguridad cuando sea necesario
✅ Enlaces a recursos útiles y documentación
✅ Opción de escalar si necesitas ayuda adicional

**Tiempo estimado:** {estimated_time} minutos
**Pasos estimados:** {estimated_steps}

**¿Cómo funciona?**
1. Te guiaremos paso a paso con instrucciones claras
2. En cada paso, verificarás que todo funcione correctamente
3. Si algo no funciona, te ayudaremos a diagnosticar el problema
4. Si después de todos los pasos el problema persiste, escalaremos tu caso a un especialista

**Para comenzar:**
Accede a tu sesión de troubleshooting en:
[Enlace a la sesión: /troubleshooting/{session_id}]

O responde a este email y te guiaremos directamente.

**¿Necesitas ayuda inmediata?**
Si prefieres hablar directamente con nuestro equipo, puedes:
- Responder a este email
- Contactarnos por teléfono: [número de soporte]
- Acceder a chat en vivo: [enlace al chat]

Estamos aquí para ayudarte. ¡Empecemos!

Ticket ID: #{ticket_id}
Sesión ID: {session_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos cordiales,
Equipo de Soporte Técnico"""
    else:
        # English version
        subject = f"Step-by-step solution guide - Ticket #{ticket_id}"
        greeting = f"""Hello {customer_name},

Thank you for contacting us. We've analyzed your problem and prepared a personalized 
guide to help you resolve it step by step.

**Problem identified:**
{problem_title}

**Our guide includes:**
✅ Clear and easy-to-follow instructions
✅ Verifications at each step to ensure everything works
✅ Safety precautions when necessary
✅ Links to useful resources and documentation
✅ Option to escalate if you need additional help

**Estimated time:** {estimated_time} minutes
**Estimated steps:** {estimated_steps}

**How it works:**
1. We'll guide you step by step with clear instructions
2. At each step, you'll verify that everything works correctly
3. If something doesn't work, we'll help you diagnose the problem
4. If after all steps the problem persists, we'll escalate your case to a specialist

**To get started:**
Access your troubleshooting session at:
[Session link: /troubleshooting/{session_id}]

Or reply to this email and we'll guide you directly.

**Need immediate help?**
If you prefer to speak directly with our team, you can:
- Reply to this email
- Contact us by phone: [support number]
- Access live chat: [chat link]

We're here to help. Let's get started!

Ticket ID: #{ticket_id}
Session ID: {session_id}
Date: {datetime.now().strftime('%m/%d/%Y %H:%M')}

Best regards,
Technical Support Team"""
    
    return {
        "subject": subject,
        "text_body": greeting,
        "html_body": _generate_troubleshooting_html(greeting, subject, ticket_id, session_id, language),
        "metadata": {
            "template_type": "troubleshooting_start",
            "technical_level": technical_level.value,
            "complexity": complexity.value,
            "language": language,
            "estimated_steps": estimated_steps,
            "estimated_time_minutes": estimated_time
        }
    }


def get_troubleshooting_step_template(
    ticket_data: Dict[str, Any],
    step_number: int,
    step_title: str,
    step_instructions: str,
    step_verification: Optional[str] = None,
    warnings: Optional[List[str]] = None,
    resources: Optional[List[Dict[str, str]]] = None,
    language: str = "es"
) -> Dict[str, str]:
    """
    Genera template para un paso específico de troubleshooting.
    
    Args:
        ticket_data: Datos del ticket
        step_number: Número del paso
        step_title: Título del paso
        step_instructions: Instrucciones del paso
        step_verification: Cómo verificar que el paso funcionó
        warnings: Lista de advertencias/precauciones
        resources: Lista de recursos relacionados
        language: Idioma
        
    Returns:
        Dict con subject, text_body, html_body, metadata
    """
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    session_id = ticket_data.get("session_id", "N/A")
    
    if language == "es":
        subject = f"Paso {step_number}: {step_title} - Ticket #{ticket_id}"
        
        body = f"""Hola {customer_name},

Continuemos con el paso {step_number} de la solución.

**Paso {step_number}: {step_title}**

{step_instructions}

"""
        
        if step_verification:
            body += f"""**Verificación:**
{step_verification}

Por favor, confirma que este paso funcionó correctamente antes de continuar.

"""
        
        if warnings:
            body += "**⚠️ Precauciones importantes:**\n"
            for warning in warnings:
                body += f"• {warning}\n"
            body += "\n"
        
        if resources:
            body += "**📚 Recursos útiles:**\n"
            for resource in resources:
                title = resource.get("title", "Recurso")
                url = resource.get("url", "#")
                body += f"• {title}: {url}\n"
            body += "\n"
        
        body += f"""**¿Funcionó este paso?**
- ✅ Sí, funcionó correctamente → Continuar al siguiente paso
- ❌ No, no funcionó → Te ayudaremos a diagnosticar el problema
- ❓ No estoy seguro → Te guiaremos para verificar

**Siguiente paso:**
Accede a tu sesión para continuar: [Enlace a la sesión]

O responde a este email indicando si el paso funcionó o no.

Ticket ID: #{ticket_id}
Sesión ID: {session_id}

Saludos,
Equipo de Soporte Técnico"""
    else:
        # English version
        subject = f"Step {step_number}: {step_title} - Ticket #{ticket_id}"
        body = f"""Hello {customer_name},

Let's continue with step {step_number} of the solution.

**Step {step_number}: {step_title}**

{step_instructions}

"""
        
        if step_verification:
            body += f"""**Verification:**
{step_verification}

Please confirm that this step worked correctly before continuing.

"""
        
        if warnings:
            body += "**⚠️ Important precautions:**\n"
            for warning in warnings:
                body += f"• {warning}\n"
            body += "\n"
        
        if resources:
            body += "**📚 Useful resources:**\n"
            for resource in resources:
                title = resource.get("title", "Resource")
                url = resource.get("url", "#")
                body += f"• {title}: {url}\n"
            body += "\n"
        
        body += f"""**Did this step work?**
- ✅ Yes, it worked correctly → Continue to next step
- ❌ No, it didn't work → We'll help you diagnose the problem
- ❓ I'm not sure → We'll guide you to verify

**Next step:**
Access your session to continue: [Session link]

Or reply to this email indicating whether the step worked or not.

Ticket ID: #{ticket_id}
Session ID: {session_id}

Best regards,
Technical Support Team"""
    
    return {
        "subject": subject,
        "text_body": body,
        "html_body": _generate_step_html(body, subject, ticket_id, session_id, step_number, language),
        "metadata": {
            "template_type": "troubleshooting_step",
            "step_number": step_number,
            "language": language
        }
    }


def get_troubleshooting_resolved_template(
    ticket_data: Dict[str, Any],
    resolution_summary: str,
    steps_completed: int,
    total_duration_minutes: Optional[int] = None,
    language: str = "es"
) -> Dict[str, str]:
    """
    Genera template cuando el problema se resuelve.
    
    Args:
        ticket_data: Datos del ticket
        resolution_summary: Resumen de la solución
        steps_completed: Número de pasos completados
        total_duration_minutes: Duración total en minutos
        language: Idioma
        
    Returns:
        Dict con subject, text_body, html_body, metadata
    """
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    if language == "es":
        subject = f"¡Problema resuelto! - Ticket #{ticket_id}"
        
        body = f"""Hola {customer_name},

¡Excelente! Hemos resuelto tu problema juntos.

**Resumen de la solución:**
{resolution_summary}

**Estadísticas:**
• Pasos completados: {steps_completed}
{f"• Tiempo total: {total_duration_minutes} minutos" if total_duration_minutes else ""}

**¿Qué sigue?**
Tu problema debería estar completamente resuelto. Si experimentas algún problema 
adicional o el problema vuelve a aparecer, no dudes en contactarnos.

**¿Cómo fue tu experiencia?**
Nos encantaría conocer tu opinión sobre el proceso de troubleshooting. Tu 
feedback nos ayuda a mejorar nuestros servicios.

**Recursos adicionales:**
• Documentación completa: [enlace]
• Preguntas frecuentes: [enlace]
• Portal de soporte: [enlace]

**¿Necesitas más ayuda?**
Si tienes alguna pregunta adicional, puedes:
- Responder a este email
- Acceder a tu portal de cliente
- Contactarnos por teléfono: [número]

¡Gracias por tu paciencia y por trabajar con nosotros para resolver esto!

Ticket ID: #{ticket_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos cordiales,
Equipo de Soporte Técnico"""
    else:
        # English version
        subject = f"Problem resolved! - Ticket #{ticket_id}"
        body = f"""Hello {customer_name},

Excellent! We've resolved your problem together.

**Solution summary:**
{resolution_summary}

**Statistics:**
• Steps completed: {steps_completed}
{f"• Total time: {total_duration_minutes} minutes" if total_duration_minutes else ""}

**What's next?**
Your problem should be completely resolved. If you experience any additional 
issues or the problem reappears, don't hesitate to contact us.

**How was your experience?**
We'd love to hear your feedback on the troubleshooting process. Your feedback 
helps us improve our services.

**Additional resources:**
• Complete documentation: [link]
• Frequently asked questions: [link]
• Support portal: [link]

**Need more help?**
If you have any additional questions, you can:
- Reply to this email
- Access your customer portal
- Contact us by phone: [number]

Thank you for your patience and for working with us to resolve this!

Ticket ID: #{ticket_id}
Date: {datetime.now().strftime('%m/%d/%Y %H:%M')}

Best regards,
Technical Support Team"""
    
    return {
        "subject": subject,
        "text_body": body,
        "html_body": _generate_resolved_html(body, subject, ticket_id, language),
        "metadata": {
            "template_type": "troubleshooting_resolved",
            "steps_completed": steps_completed,
            "language": language
        }
    }


def get_troubleshooting_escalation_template(
    ticket_data: Dict[str, Any],
    escalation_reason: str,
    steps_attempted: int,
    next_steps: Optional[List[str]] = None,
    language: str = "es"
) -> Dict[str, str]:
    """
    Genera template cuando se necesita escalar el problema.
    
    Args:
        ticket_data: Datos del ticket
        escalation_reason: Razón de la escalación
        steps_attempted: Número de pasos intentados
        next_steps: Próximos pasos que tomará el equipo
        language: Idioma
        
    Returns:
        Dict con subject, text_body, html_body, metadata
    """
    customer_name = ticket_data.get("customer_name", "Estimado cliente")
    ticket_id = ticket_data.get("ticket_id", "N/A")
    
    if language == "es":
        subject = f"Escalando tu caso a un especialista - Ticket #{ticket_id}"
        
        body = f"""Hola {customer_name},

Hemos intentado resolver tu problema con los pasos de troubleshooting, pero 
necesitamos la ayuda de un especialista para resolverlo completamente.

**Razón de la escalación:**
{escalation_reason}

**Lo que hemos intentado:**
• Pasos de troubleshooting completados: {steps_attempted}
• Hemos recopilado información detallada sobre el problema
• Hemos documentado todos los intentos de solución

**¿Qué sigue?**
Un especialista de nuestro equipo revisará tu caso y se pondrá en contacto 
contigo en las próximas 24 horas.

"""
        
        if next_steps:
            body += "**Próximos pasos que tomará nuestro equipo:**\n"
            for i, step in enumerate(next_steps, 1):
                body += f"{i}. {step}\n"
            body += "\n"
        
        body += f"""**Información importante:**
• Tu ticket ha sido marcado como prioridad alta
• Un especialista se pondrá en contacto contigo pronto
• Mientras tanto, no necesitas hacer nada adicional

**¿Tienes información adicional?**
Si tienes información adicional que pueda ayudar a resolver el problema, 
puedes responder a este email y la agregaremos a tu caso.

**Contacto directo:**
Si necesitas hablar urgentemente con nuestro equipo, puedes:
- Responder a este email
- Contactarnos por teléfono: [número de soporte]
- Acceder a chat en vivo: [enlace al chat]

Gracias por tu paciencia mientras trabajamos para resolver esto.

Ticket ID: #{ticket_id}
Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}

Saludos cordiales,
Equipo de Soporte Técnico"""
    else:
        # English version
        subject = f"Escalating your case to a specialist - Ticket #{ticket_id}"
        body = f"""Hello {customer_name},

We've attempted to resolve your problem with troubleshooting steps, but we need 
the help of a specialist to resolve it completely.

**Escalation reason:**
{escalation_reason}

**What we've attempted:**
• Troubleshooting steps completed: {steps_attempted}
• We've collected detailed information about the problem
• We've documented all solution attempts

**What's next?**
A specialist from our team will review your case and contact you within the 
next 24 hours.

"""
        
        if next_steps:
            body += "**Next steps our team will take:**\n"
            for i, step in enumerate(next_steps, 1):
                body += f"{i}. {step}\n"
            body += "\n"
        
        body += f"""**Important information:**
• Your ticket has been marked as high priority
• A specialist will contact you soon
• In the meantime, you don't need to do anything additional

**Do you have additional information?**
If you have additional information that might help resolve the problem, you can 
reply to this email and we'll add it to your case.

**Direct contact:**
If you need to speak urgently with our team, you can:
- Reply to this email
- Contact us by phone: [support number]
- Access live chat: [chat link]

Thank you for your patience as we work to resolve this.

Ticket ID: #{ticket_id}
Date: {datetime.now().strftime('%m/%d/%Y %H:%M')}

Best regards,
Technical Support Team"""
    
    return {
        "subject": subject,
        "text_body": body,
        "html_body": _generate_escalation_html(body, subject, ticket_id, language),
        "metadata": {
            "template_type": "troubleshooting_escalation",
            "steps_attempted": steps_attempted,
            "language": language
        }
    }


def _generate_troubleshooting_html(
    text_body: str,
    subject: str,
    ticket_id: str,
    session_id: str,
    language: str
) -> str:
    """Genera HTML para inicio de troubleshooting."""
    html_content = text_body.replace("\n\n", "</p><p>").replace("\n", "<br>")
    html_content = f"<p>{html_content}</p>"
    
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
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 25px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
            text-align: center;
        }}
        .content {{
            padding: 20px 0;
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
            <h1>🔧 Guía de Solución</h1>
        </div>
        <div class="content">
            {html_content}
        </div>
        <div class="footer">
            <p>Ticket ID: #{ticket_id} | Session ID: {session_id}</p>
        </div>
    </div>
</body>
</html>
"""


def _generate_step_html(
    text_body: str,
    subject: str,
    ticket_id: str,
    session_id: str,
    step_number: int,
    language: str
) -> str:
    """Genera HTML para un paso de troubleshooting."""
    html_content = text_body.replace("\n\n", "</p><p>").replace("\n", "<br>")
    html_content = f"<p>{html_content}</p>"
    
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
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 8px 8px 0 0;
            margin: -30px -30px 30px -30px;
            text-align: center;
        }}
        .step-badge {{
            display: inline-block;
            background-color: rgba(255,255,255,0.3);
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .content {{
            padding: 20px 0;
        }}
        .button {{
            display: inline-block;
            padding: 12px 24px;
            background-color: #f5576c;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            margin: 10px 5px;
            font-weight: 600;
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
            <div class="step-badge">Paso {step_number}</div>
            <h1>🔧 {subject.replace(f'Paso {step_number}: ', '')}</h1>
        </div>
        <div class="content">
            {html_content}
        </div>
        <div class="footer">
            <p>Ticket ID: #{ticket_id} | Session ID: {session_id}</p>
        </div>
    </div>
</body>
</html>
"""


def _generate_resolved_html(
    text_body: str,
    subject: str,
    ticket_id: str,
    language: str
) -> str:
    """Genera HTML para problema resuelto."""
    html_content = text_body.replace("\n\n", "</p><p>").replace("\n", "<br>")
    html_content = f"<p>{html_content}</p>"
    
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
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
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
            <h1>✅ Problema Resuelto</h1>
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


def _generate_escalation_html(
    text_body: str,
    subject: str,
    ticket_id: str,
    language: str
) -> str:
    """Genera HTML para escalación."""
    html_content = text_body.replace("\n\n", "</p><p>").replace("\n", "<br>")
    html_content = f"<p>{html_content}</p>"
    
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
            background: linear-gradient(135deg, #FF9800 0%, #F57C00 100%);
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
            <h1>🚀 Escalando a Especialista</h1>
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



