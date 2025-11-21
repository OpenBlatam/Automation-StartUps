"""
Ejemplos de Uso del Sistema de Chatbot
Versión: 2.0.0
"""

import asyncio
from datetime import datetime
from chatbot_engine import (
    ChatbotEngine, ChatMessage, Channel, Language,
    Sentiment, Intent
)


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
    
    print(f"\n👤 Usuario: {message.message}")
    print(f"\n🤖 Chatbot: {response.message}")
    print(f"\n📊 Confianza: {response.confidence:.2%}")
    print(f"🎯 Acción: {response.action}")
    print(f"😊 Sentimiento: {response.sentiment.value if response.sentiment else 'N/A'}")
    print(f"💭 Intención: {response.intent.value if response.intent else 'N/A'}")


async def ejemplo_escalamiento():
    """Ejemplo de escalamiento automático"""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Escalamiento Automático")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    # Mensaje que requiere escalamiento
    message = ChatMessage(
        user_id="user_456",
        message="¡ERROR CRÍTICO! El sistema no funciona y perdí todos mis datos",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    
    print(f"\n👤 Usuario: {message.message}")
    print(f"\n🤖 Chatbot: {response.message}")
    print(f"\n🎫 Ticket ID: {response.ticket_id}")
    print(f"⚠️ Prioridad: {response.metadata.get('priority', 'N/A')}")
    print(f"📋 Acciones sugeridas: {', '.join(response.suggested_actions)}")


async def ejemplo_conversacion():
    """Ejemplo de conversación con contexto"""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Conversación con Contexto")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    user_id = "user_789"
    session_id = None
    
    # Primera interacción
    message1 = ChatMessage(
        user_id=user_id,
        message="Hola",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES,
        session_id=session_id or ""
    )
    
    response1 = await chatbot.process_message(message1)
    session_id = message1.session_id
    
    print(f"\n👤 Usuario: {message1.message}")
    print(f"🤖 Chatbot: {response1.message}")
    
    # Segunda interacción (con contexto)
    message2 = ChatMessage(
        user_id=user_id,
        message="¿Cuál es el precio del plan Pro?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES,
        session_id=session_id
    )
    
    response2 = await chatbot.process_message(message2)
    
    print(f"\n👤 Usuario: {message2.message}")
    print(f"🤖 Chatbot: {response2.message}")
    
    # Ver contexto de conversación
    if session_id in chatbot.conversations:
        conv = chatbot.conversations[session_id]
        print(f"\n📝 Historial de conversación:")
        print(f"   - Mensajes: {len(conv.messages)}")
        print(f"   - Sentimientos: {[s.value for s in conv.sentiment_history]}")
        print(f"   - Intenciones: {[i.value for i in conv.intents_history]}")


async def ejemplo_multilenguaje():
    """Ejemplo de soporte multilingüe"""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Soporte Multilingüe")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    # Mensaje en español
    message_es = ChatMessage(
        user_id="user_es",
        message="¿Cómo puedo cancelar mi suscripción?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=None  # Se detecta automáticamente
    )
    
    response_es = await chatbot.process_message(message_es)
    print(f"\n🇪🇸 Español:")
    print(f"   Usuario: {message_es.message}")
    print(f"   Chatbot: {response_es.message[:100]}...")
    
    # Mensaje en inglés
    message_en = ChatMessage(
        user_id="user_en",
        message="How can I cancel my subscription?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=None
    )
    
    response_en = await chatbot.process_message(message_en)
    print(f"\n🇬🇧 English:")
    print(f"   User: {message_en.message}")
    print(f"   Chatbot: {response_en.message[:100]}...")


async def ejemplo_metricas():
    """Ejemplo de obtención de métricas"""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Métricas del Chatbot")
    print("=" * 60)
    
    chatbot = ChatbotEngine()
    
    # Simular algunas interacciones
    messages = [
        "¿Cómo exportar reportes?",
        "¿Cuál es el precio?",
        "Error crítico en el sistema",
        "Gracias por la ayuda"
    ]
    
    for i, msg in enumerate(messages, 1):
        message = ChatMessage(
            user_id=f"user_{i}",
            message=msg,
            timestamp=datetime.now(),
            channel=Channel.WEB,
            language=Language.ES
        )
        await chatbot.process_message(message)
    
    # Registrar algunas satisfacciones
    chatbot.record_satisfaction(5, "session_1")
    chatbot.record_satisfaction(4, "session_2")
    chatbot.record_satisfaction(5, "session_3")
    
    # Obtener métricas
    metrics = chatbot.get_metrics()
    
    print("\n📊 Métricas del Chatbot:")
    print(f"   • Interacciones totales: {metrics['total_interactions']}")
    print(f"   • Resueltas en primera interacción: {metrics['resolved_first_contact']}")
    print(f"   • Tasa de resolución: {metrics['resolution_rate']}%")
    print(f"   • Escalamientos: {metrics['escalated']}")
    print(f"   • Tasa de escalamiento: {metrics['escalation_rate']}%")
    print(f"   • Satisfacción promedio: {metrics['avg_satisfaction']}/5")
    print(f"   • Tiempo promedio de respuesta: {metrics['avg_response_time']:.2f}s")
    print(f"\n   📈 Distribución de sentimientos:")
    for sentiment, percentage in metrics['sentiment_percentages'].items():
        print(f"      - {sentiment}: {percentage}%")
    print(f"\n   🎯 Objetivos:")
    print(f"      - Resolución: {metrics['targets']['resolution_rate']['current']}% "
          f"(Objetivo: {metrics['targets']['resolution_rate']['target']}%) "
          f"{'✅' if metrics['targets']['resolution_rate']['met'] else '❌'}")
    print(f"      - Satisfacción: {metrics['targets']['satisfaction']['current']}/5 "
          f"(Objetivo: {metrics['targets']['satisfaction']['target']}/5) "
          f"{'✅' if metrics['targets']['satisfaction']['met'] else '❌'}")
    print(f"      - Tiempo de respuesta: {metrics['targets']['response_time']['current']}s "
          f"(Objetivo: <{metrics['targets']['response_time']['target']}s) "
          f"{'✅' if metrics['targets']['response_time']['met'] else '❌'}")


async def main():
    """Ejecutar todos los ejemplos"""
    print("\n" + "🤖" * 30)
    print("SISTEMA DE CHATBOT AVANZADO - EJEMPLOS DE USO")
    print("🤖" * 30)
    
    await ejemplo_basico()
    await ejemplo_escalamiento()
    await ejemplo_conversacion()
    await ejemplo_multilenguaje()
    await ejemplo_metricas()
    
    print("\n" + "=" * 60)
    print("✅ Todos los ejemplos completados")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())






