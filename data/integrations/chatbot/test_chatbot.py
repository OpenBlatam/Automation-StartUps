"""
Tests Automatizados para el Sistema de Chatbot
Versión: 2.0.0
"""

import pytest
import asyncio
from datetime import datetime
from chatbot_engine import (
    ChatbotEngine, ChatMessage, Channel, Language,
    Sentiment, Intent, Priority
)


@pytest.fixture
def chatbot():
    """Fixture para crear instancia del chatbot"""
    return ChatbotEngine()


@pytest.fixture
def sample_message():
    """Fixture para crear mensaje de ejemplo"""
    return ChatMessage(
        user_id="test_user",
        message="Test message",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )


@pytest.mark.asyncio
async def test_chatbot_initialization(chatbot):
    """Test de inicialización del chatbot"""
    assert chatbot is not None
    assert chatbot.config is not None
    assert chatbot.faqs is not None
    assert chatbot.responses is not None


@pytest.mark.asyncio
async def test_process_message(chatbot, sample_message):
    """Test de procesamiento de mensaje"""
    response = await chatbot.process_message(sample_message)
    
    assert response is not None
    assert response.message is not None
    assert isinstance(response.confidence, float)
    assert response.action in ["answer", "escalate", "request_info"]


@pytest.mark.asyncio
async def test_faq_matching(chatbot):
    """Test de matching de FAQs"""
    message = ChatMessage(
        user_id="test_user",
        message="¿Cómo exportar reportes?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    
    # Debería encontrar una FAQ
    assert response.confidence > 0.5
    assert response.action == "answer"


@pytest.mark.asyncio
async def test_escalation_detection(chatbot):
    """Test de detección de escalamiento"""
    message = ChatMessage(
        user_id="test_user",
        message="ERROR CRÍTICO: El sistema no funciona",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    
    # Debería escalar
    assert response.action == "escalate"
    assert response.ticket_id is not None
    assert response.metadata.get("priority") in ["critical", "high"]


@pytest.mark.asyncio
async def test_sentiment_analysis(chatbot):
    """Test de análisis de sentimientos"""
    # Mensaje positivo
    positive_msg = ChatMessage(
        user_id="test_user",
        message="¡Excelente servicio! Muchas gracias",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(positive_msg)
    assert response.sentiment == Sentiment.POSITIVE
    
    # Mensaje negativo
    negative_msg = ChatMessage(
        user_id="test_user",
        message="Terrible servicio, muy malo",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(negative_msg)
    assert response.sentiment in [Sentiment.NEGATIVE, Sentiment.FRUSTRATED]


@pytest.mark.asyncio
async def test_language_detection(chatbot):
    """Test de detección de idioma"""
    # Español
    spanish_msg = ChatMessage(
        user_id="test_user",
        message="¿Cómo puedo ayudarte?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=None  # Se detecta automáticamente
    )
    
    response = await chatbot.process_message(spanish_msg)
    assert response is not None
    
    # Inglés
    english_msg = ChatMessage(
        user_id="test_user",
        message="How can I help you?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=None
    )
    
    response = await chatbot.process_message(english_msg)
    assert response is not None


@pytest.mark.asyncio
async def test_conversation_context(chatbot):
    """Test de contexto de conversación"""
    user_id = "test_user_context"
    session_id = None
    
    # Primera mensaje
    msg1 = ChatMessage(
        user_id=user_id,
        message="Hola",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES,
        session_id=session_id or ""
    )
    
    response1 = await chatbot.process_message(msg1)
    session_id = msg1.session_id
    
    # Segundo mensaje (debe mantener contexto)
    msg2 = ChatMessage(
        user_id=user_id,
        message="¿Cuál es el precio?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES,
        session_id=session_id
    )
    
    response2 = await chatbot.process_message(msg2)
    
    # Verificar que la conversación se mantiene
    assert session_id in chatbot.conversations
    conversation = chatbot.conversations[session_id]
    assert len(conversation.messages) >= 2


def test_metrics_calculation(chatbot):
    """Test de cálculo de métricas"""
    metrics = chatbot.get_metrics()
    
    assert "total_interactions" in metrics
    assert "resolution_rate" in metrics
    assert "avg_satisfaction" in metrics
    assert "avg_response_time" in metrics
    assert isinstance(metrics["resolution_rate"], (int, float))
    assert isinstance(metrics["avg_satisfaction"], (int, float))


def test_satisfaction_recording(chatbot):
    """Test de registro de satisfacción"""
    initial_count = len(chatbot.metrics["satisfaction_scores"])
    
    chatbot.record_satisfaction(5, "test_session")
    chatbot.record_satisfaction(4, "test_session_2")
    
    assert len(chatbot.metrics["satisfaction_scores"]) == initial_count + 2
    assert chatbot.metrics["satisfaction_scores"][-1] == 4


@pytest.mark.asyncio
async def test_multiple_channels(chatbot):
    """Test de múltiples canales"""
    channels = [Channel.WEB, Channel.WHATSAPP, Channel.EMAIL]
    
    for channel in channels:
        message = ChatMessage(
            user_id=f"test_user_{channel.value}",
            message="Test message",
            timestamp=datetime.now(),
            channel=channel,
            language=Language.ES
        )
        
        response = await chatbot.process_message(message)
        assert response is not None
        assert response.message is not None


@pytest.mark.asyncio
async def test_intent_detection(chatbot):
    """Test de detección de intención"""
    # Saludo
    greeting_msg = ChatMessage(
        user_id="test_user",
        message="Hola, buenos días",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(greeting_msg)
    assert response.intent == Intent.GREETING
    
    # Pregunta
    question_msg = ChatMessage(
        user_id="test_user",
        message="¿Cómo funciona esto?",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(question_msg)
    assert response.intent == Intent.QUESTION


@pytest.mark.asyncio
async def test_response_time(chatbot):
    """Test de tiempo de respuesta"""
    import time
    
    start = time.time()
    message = ChatMessage(
        user_id="test_user",
        message="Test message",
        timestamp=datetime.now(),
        channel=Channel.WEB,
        language=Language.ES
    )
    
    response = await chatbot.process_message(message)
    elapsed = time.time() - start
    
    # El tiempo de respuesta debe ser razonable (< 5 segundos para test)
    assert elapsed < 5.0
    assert response is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])






