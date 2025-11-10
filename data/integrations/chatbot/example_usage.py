"""
Ejemplos de Uso del Sistema de Chatbot
"""

import asyncio
from datetime import datetime
from chatbot_engine import (
    ChatbotEngine, ChatMessage, ChatResponse, 
    Channel, Language
)
from integrations import (
    WhatsAppBusinessIntegration,
    CRMIntegration,
    ZapierIntegration,
    EmailServiceIntegration,
    DialogflowIntegration,
    IntercomIntegration
)
from dashboard_metrics import MetricsDashboard, generate_html_dashboard


async def ejemplo_basico():
    """Ejemplo básico de uso del chatbot"""
    print("=" * 60)
    print("EJEMPLO 1: Uso Básico del Chatbot")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    # Crear mensaje
    message = ChatMessage(
        user_id="user_123",
        message="¿Cómo exportar reportes?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    # Procesar mensaje
    response = await chatbot.process_message(message)
    
    print(f"\nUsuario: {message.message}")
    print(f"Chatbot: {response.message}")
    print(f"Confianza: {response.confidence:.2f}")
    print(f"Acción: {response.action}")
    if response.suggested_actions:
        print(f"Acciones sugeridas: {', '.join(response.suggested_actions)}")


async def ejemplo_escalamiento():
    """Ejemplo de escalamiento automático"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Escalamiento Automático")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    # Mensaje que requiere escalamiento
    message = ChatMessage(
        user_id="user_456",
        message="Tengo un error crítico, el sistema no funciona",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    
    print(f"\nUsuario: {message.message}")
    print(f"Chatbot: {response.message}")
    print(f"Ticket ID: {response.ticket_id}")
    print(f"Prioridad: {response.metadata.get('priority', 'N/A')}")


async def ejemplo_multilenguaje():
    """Ejemplo con diferentes idiomas"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Soporte Multilingüe")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    # Mensaje en español
    message_es = ChatMessage(
        user_id="user_789",
        message="¿Cuál es el precio del plan Pro?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response_es = await chatbot.process_message(message_es)
    print(f"\n[ES] Usuario: {message_es.message}")
    print(f"[ES] Chatbot: {response_es.message[:100]}...")
    
    # Mensaje en inglés
    message_en = ChatMessage(
        user_id="user_789",
        message="What is the cost of the Pro plan?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.EN
    )
    
    response_en = await chatbot.process_message(message_en)
    print(f"\n[EN] User: {message_en.message}")
    print(f"[EN] Chatbot: {response_en.message[:100]}...")


async def ejemplo_whatsapp():
    """Ejemplo de integración con WhatsApp"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Integración WhatsApp")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    whatsapp = WhatsAppBusinessIntegration(
        phone_number_id="tu_phone_id",
        access_token="tu_token"
    )
    
    # Simular mensaje de WhatsApp
    user_message = "Hola, necesito ayuda con mi cuenta"
    
    chat_message = ChatMessage(
        user_id="whatsapp_+1234567890",
        message=user_message,
        timestamp=datetime.now(),
        channel=Channel.WHATSAPP,
        language=Language.ES
    )
    
    response = await chatbot.process_message(chat_message)
    
    # Enviar respuesta por WhatsApp
    whatsapp_result = await whatsapp.send_message(
        to="+1234567890",
        message=user_message,
        chatbot_response=response.message
    )
    
    print(f"\nUsuario (WhatsApp): {user_message}")
    print(f"Chatbot: {response.message[:100]}...")
    print(f"Enviado: {whatsapp_result.get('success', False)}")


async def ejemplo_crm():
    """Ejemplo de integración con CRM"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Integración CRM")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    crm = CRMIntegration(
        crm_type="salesforce",
        api_key="tu_api_key"
    )
    
    # Procesar mensaje
    message = ChatMessage(
        user_id="user_999",
        message="Estoy interesado en el plan Enterprise",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    
    # Crear lead en CRM
    lead_data = {
        "email": "cliente@ejemplo.com",
        "first_name": "Juan",
        "last_name": "Pérez",
        "company": "Empresa Ejemplo",
        "source": "Chatbot",
        "message": message.message
    }
    
    lead_id = await crm.create_lead(lead_data)
    
    print(f"\nMensaje: {message.message}")
    print(f"Lead creado en CRM: {lead_id}")
    print(f"Respuesta chatbot: {response.message[:100]}...")


async def ejemplo_metricas():
    """Ejemplo de dashboard de métricas"""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: Dashboard de Métricas")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    dashboard = MetricsDashboard()
    
    # Simular algunas interacciones
    messages = [
        "¿Cómo exportar reportes?",
        "¿Cuál es el precio?",
        "Error crítico en el sistema",
        "¿Cómo restablecer contraseña?",
        "Necesito ayuda con integraciones"
    ]
    
    for i, msg in enumerate(messages):
        message = ChatMessage(
            user_id=f"user_{i}",
            message=msg,
            timestamp=datetime.now(),
            channel=Channel.WEB,
            language=Language.ES
        )
        await chatbot.process_message(message)
    
    # Registrar satisfacción
    chatbot.record_satisfaction(5, "session_1")
    chatbot.record_satisfaction(4, "session_2")
    chatbot.record_satisfaction(5, "session_3")
    
    # Obtener métricas
    metrics = chatbot.get_metrics()
    dashboard.save_snapshot(metrics)
    
    # Generar reporte
    report = dashboard.generate_report(metrics, period="daily")
    print(report)
    
    # Exportar a JSON
    json_data = dashboard.export_to_json(metrics)
    print(f"\nMétricas exportadas: {len(json_data)} campos")


async def ejemplo_zapier():
    """Ejemplo de integración con Zapier"""
    print("\n" + "=" * 60)
    print("EJEMPLO 7: Integración Zapier")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    zapier = ZapierIntegration(webhook_url="https://hooks.zapier.com/...")
    
    message = ChatMessage(
        user_id="user_zapier",
        message="Quiero una demo del producto",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    
    # Sincronizar con CRM a través de Zapier
    await zapier.sync_to_crm(
        user_data={
            "email": "lead@ejemplo.com",
            "name": "Lead Ejemplo"
        },
        interaction_data={
            "message": message.message,
            "response": response.message,
            "timestamp": datetime.now().isoformat()
        }
    )
    
    print(f"\nMensaje: {message.message}")
    print(f"Respuesta: {response.message[:100]}...")
    print("Sincronizado con CRM vía Zapier ✅")


async def ejemplo_completo():
    """Ejemplo completo con múltiples integraciones"""
    print("\n" + "=" * 60)
    print("EJEMPLO 8: Flujo Completo")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    dashboard = MetricsDashboard()
    crm = CRMIntegration(crm_type="salesforce", api_key="demo")
    zapier = ZapierIntegration(webhook_url="demo")
    
    # Simular flujo completo
    scenarios = [
        {
            "message": "¿Cómo exportar reportes?",
            "channel": Channel.WEB,
            "language": Language.ES
        },
        {
            "message": "What is the Pro plan price?",
            "channel": Channel.WEB,
            "language": Language.EN
        },
        {
            "message": "Error crítico, sistema caído",
            "channel": Channel.WHATSAPP,
            "language": Language.ES
        }
    ]
    
    for i, scenario in enumerate(scenarios):
        msg = ChatMessage(
            user_id=f"user_{i}",
            message=scenario["message"],
            timestamp=datetime.now(),
            channel=scenario["channel"],
            language=scenario["language"]
        )
        
        response = await chatbot.process_message(msg)
        
        # Si se escaló, crear caso en CRM
        if response.ticket_id:
            await crm.create_case({
                "subject": "Consulta Chatbot",
                "description": msg.message,
                "ticket_id": response.ticket_id
            })
        
        # Sincronizar con Zapier
        await zapier.trigger_webhook("chatbot_interaction", {
            "user_id": msg.user_id,
            "message": msg.message,
            "response": response.message
        })
        
        print(f"\n[{scenario['channel'].value}] {msg.message}")
        print(f"→ {response.message[:80]}...")
        if response.ticket_id:
            print(f"  Ticket: {response.ticket_id}")
    
    # Generar reporte final
    metrics = chatbot.get_metrics()
    dashboard.save_snapshot(metrics)
    report = dashboard.generate_report(metrics)
    print("\n" + "=" * 60)
    print("REPORTE FINAL")
    print("=" * 60)
    print(report)


async def main():
    """Ejecutar todos los ejemplos"""
    await ejemplo_basico()
    await ejemplo_escalamiento()
    await ejemplo_multilenguaje()
    await ejemplo_whatsapp()
    await ejemplo_crm()
    await ejemplo_metricas()
    await ejemplo_zapier()
    await ejemplo_completo()


if __name__ == "__main__":
    asyncio.run(main())

