#!/usr/bin/env python3
"""
Ejemplos de Integración de Chatbots
Muestra diferentes formas de integrar los chatbots en aplicaciones
"""

import sys
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from chatbot_curso_ia_webinars import CursoIAWebinarChatbot


# Ejemplo 1: Integración Básica
def ejemplo_basico():
    """Ejemplo básico de uso"""
    print("=" * 60)
    print("Ejemplo 1: Integración Básica")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot()
    
    mensajes = [
        "¿Cuánto cuesta el curso?",
        "¿Qué incluye?",
        "¿Cómo me inscribo?"
    ]
    
    for mensaje in mensajes:
        response = chatbot.process_message(mensaje)
        print(f"\nUsuario: {mensaje}")
        print(f"Chatbot: {response['response'][:100]}...")
        print(f"Confianza: {response['confidence']:.2f}")


# Ejemplo 2: Con Historial de Conversación
def ejemplo_con_historial():
    """Ejemplo con historial de conversación"""
    print("\n" + "=" * 60)
    print("Ejemplo 2: Con Historial de Conversación")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot()
    conversation_history = []
    
    # Primera pregunta
    response1 = chatbot.process_message("¿Cuánto cuesta el curso?")
    conversation_history.append({"role": "user", "content": "¿Cuánto cuesta el curso?"})
    conversation_history.append({"role": "assistant", "content": response1['response']})
    
    # Segunda pregunta (usa contexto)
    response2 = chatbot.process_message(
        "¿Y qué incluye?",
        conversation_history=conversation_history
    )
    
    print(f"\nUsuario: ¿Cuánto cuesta el curso?")
    print(f"Chatbot: {response1['response'][:80]}...")
    print(f"\nUsuario: ¿Y qué incluye?")
    print(f"Chatbot: {response2['response'][:80]}...")
    print(f"\n✅ El chatbot usó el contexto de la conversación anterior")


# Ejemplo 3: Con Métricas y Monitoreo
def ejemplo_con_metricas():
    """Ejemplo con métricas y monitoreo"""
    print("\n" + "=" * 60)
    print("Ejemplo 3: Con Métricas y Monitoreo")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot()
    
    # Procesar varios mensajes
    for i in range(5):
        chatbot.process_message(f"Pregunta de prueba {i+1}")
    
    # Obtener métricas
    metrics = chatbot.get_metrics()
    
    print(f"\n📊 Métricas:")
    print(f"   • Total mensajes: {metrics['total_messages']}")
    print(f"   • Confianza promedio: {metrics['average_confidence']:.2f}")
    print(f"   • Tiempo promedio: {metrics['average_processing_time']:.3f}s")
    print(f"   • Tasa de match FAQ: {metrics['faq_match_rate']:.1%}")
    
    # Health check
    health = chatbot.health_check()
    print(f"\n🏥 Health Check:")
    print(f"   • Estado: {health['status']}")
    if health.get('issues'):
        for issue in health['issues']:
            print(f"   • ⚠️  {issue}")


# Ejemplo 4: Con Feedback
def ejemplo_con_feedback():
    """Ejemplo con sistema de feedback"""
    print("\n" + "=" * 60)
    print("Ejemplo 4: Con Sistema de Feedback")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot(enable_feedback=True)
    
    # Procesar mensaje
    response = chatbot.process_message("¿Cuánto cuesta el curso?")
    conversation_id = response['conversation_id']
    
    # Agregar feedback positivo
    chatbot.add_feedback(
        conversation_id=conversation_id,
        message_id="msg_1",
        feedback_type="positive",
        comment="Muy útil, gracias!"
    )
    
    # Obtener estadísticas de feedback
    feedback_stats = chatbot.get_feedback_stats()
    
    if feedback_stats:
        print(f"\n📊 Estadísticas de Feedback:")
        print(f"   • Total: {feedback_stats['total']}")
        print(f"   • Positivo: {feedback_stats['positive']} ({feedback_stats['positive_rate']:.1%})")
        print(f"   • Útil: {feedback_stats['helpful']} ({feedback_stats['helpful_rate']:.1%})")


# Ejemplo 5: Análisis de Tendencias
def ejemplo_tendencias():
    """Ejemplo de análisis de tendencias"""
    print("\n" + "=" * 60)
    print("Ejemplo 5: Análisis de Tendencias")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot(enable_feedback=True)
    
    # Procesar varios mensajes para generar datos
    intenciones = ["precio", "contenido", "inscripción", "webinar"]
    for intent in intenciones:
        chatbot.process_message(f"Información sobre {intent}")
    
    # Obtener tendencias
    trends = chatbot.get_trends(days=7)
    
    if 'error' not in trends:
        print(f"\n📈 Tendencias (últimos 7 días):")
        print(f"   • Intención más común: {trends['intent_trends'].get('most_common_intent', 'N/A')}")
        print(f"   • Escalaciones promedio/día: {trends['escalation_trends'].get('average_per_day', 0):.1f}")
        print(f"   • Hora pico: {trends['peak_hours'].get('peak_hour', 'N/A')}:00")


# Ejemplo 6: Exportación de Datos
def ejemplo_exportacion():
    """Ejemplo de exportación de métricas"""
    print("\n" + "=" * 60)
    print("Ejemplo 6: Exportación de Métricas")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot()
    
    # Procesar algunos mensajes
    for i in range(3):
        chatbot.process_message(f"Test {i+1}")
    
    # Exportar a JSON
    json_file = chatbot.export_metrics(format="json")
    print(f"\n✅ Métricas exportadas a: {json_file}")
    
    # Exportar a CSV
    csv_file = chatbot.export_metrics(format="csv")
    print(f"✅ Métricas exportadas a: {csv_file}")


# Ejemplo 7: Integración con Webhook
def ejemplo_webhook():
    """Ejemplo de integración con webhook (simulado)"""
    print("\n" + "=" * 60)
    print("Ejemplo 7: Integración con Webhook")
    print("=" * 60)
    
    chatbot = CursoIAWebinarChatbot()
    
    def webhook_handler(message: str, user_id: str = None):
        """Simula un handler de webhook"""
        response = chatbot.process_message(message, user_id=user_id)
        
        # Formatear respuesta para webhook
        webhook_response = {
            "success": True,
            "message": response['response'],
            "confidence": response['confidence'],
            "intent": response['intent'],
            "requires_escalation": response['requires_escalation'],
            "suggested_actions": response.get('suggested_actions', [])
        }
        
        return webhook_response
    
    # Simular llamada de webhook
    result = webhook_handler("¿Cuánto cuesta el curso?", user_id="webhook_user_123")
    
    print(f"\n📨 Respuesta del Webhook:")
    print(f"   • Success: {result['success']}")
    print(f"   • Intent: {result['intent']}")
    print(f"   • Confidence: {result['confidence']:.2f}")
    print(f"   • Message: {result['message'][:80]}...")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🤖 Ejemplos de Integración de Chatbots")
    print("=" * 60)
    
    try:
        ejemplo_basico()
        ejemplo_con_historial()
        ejemplo_con_metricas()
        ejemplo_con_feedback()
        ejemplo_tendencias()
        ejemplo_exportacion()
        ejemplo_webhook()
        
        print("\n" + "=" * 60)
        print("✅ Todos los ejemplos ejecutados correctamente")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error ejecutando ejemplos: {e}")
        import traceback
        traceback.print_exc()






