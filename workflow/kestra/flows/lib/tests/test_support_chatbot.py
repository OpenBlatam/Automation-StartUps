"""
Tests unitarios para el módulo de chatbot de soporte.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
import json

# Importar módulo a testear
import sys
sys.path.insert(0, '.')

from support_chatbot import SupportChatbot, ChatbotResponse, FAQArticle


@pytest.fixture
def mock_db_connection():
    """Mock de conexión a base de datos."""
    mock_conn = Mock()
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


@pytest.fixture
def sample_faq_articles():
    """Artículos de FAQ de ejemplo."""
    return [
        FAQArticle(
            article_id="faq-001",
            title="¿Cómo restablezco mi contraseña?",
            content="Para restablecer tu contraseña...",
            summary="Instrucciones para restablecer contraseña",
            category="account",
            tags=["password", "login"],
            keywords=["contraseña", "password", "reset"]
        ),
        FAQArticle(
            article_id="faq-002",
            title="Problemas de facturación",
            content="Para descargar tu factura...",
            summary="Guía de facturación",
            category="billing",
            tags=["factura", "billing"],
            keywords=["factura", "invoice", "pago"]
        )
    ]


class TestSupportChatbot:
    """Tests para SupportChatbot."""
    
    def test_init_without_db(self):
        """Test inicialización sin BD."""
        chatbot = SupportChatbot()
        assert chatbot.db_connection is None
        assert chatbot.enable_llm is False
    
    def test_init_with_openai(self):
        """Test inicialización con OpenAI."""
        chatbot = SupportChatbot(
            openai_api_key="test-key",
            enable_llm=True
        )
        assert chatbot.openai_api_key == "test-key"
        assert chatbot.enable_llm is True
    
    def test_search_faq_no_connection(self):
        """Test búsqueda de FAQ sin conexión."""
        chatbot = SupportChatbot()
        results = chatbot.search_faq("password reset")
        assert results == []
    
    @patch('support_chatbot.SupportChatbot')
    def test_search_faq_with_results(self, mock_chatbot_class, mock_db_connection, sample_faq_articles):
        """Test búsqueda de FAQ con resultados."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock de resultados de BD
        mock_cursor.fetchall.return_value = [
            ("faq-001", "¿Cómo restablezco mi contraseña?", "Para restablecer...", 
             "Instrucciones", "account", ["password"], ["contraseña", "password"])
        ]
        
        chatbot = SupportChatbot(db_connection=mock_conn)
        results = chatbot.search_faq("password reset")
        
        assert len(results) > 0
        assert results[0].article_id == "faq-001"
    
    def test_detect_intent_billing(self):
        """Test detección de intención de facturación."""
        chatbot = SupportChatbot()
        intent, confidence = chatbot.detect_intent("Tengo un problema con mi factura")
        assert intent == "billing"
        assert confidence > 0
    
    def test_detect_intent_technical(self):
        """Test detección de intención técnica."""
        chatbot = SupportChatbot()
        intent, confidence = chatbot.detect_intent("El sistema no funciona, hay un error")
        assert intent == "technical"
        assert confidence > 0
    
    def test_detect_intent_general(self):
        """Test detección de intención general."""
        chatbot = SupportChatbot()
        intent, confidence = chatbot.detect_intent("Hola, necesito ayuda")
        assert intent == "general"
    
    @patch('support_chatbot.requests.Session.post')
    def test_call_llm_success(self, mock_post):
        """Test llamada exitosa a LLM."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "choices": [{
                "message": {
                    "content": "Aquí está la respuesta"
                }
            }],
            "usage": {"total_tokens": 100}
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        chatbot = SupportChatbot(
            openai_api_key="test-key",
            enable_llm=True
        )
        
        response, confidence = chatbot._call_llm("¿Cómo restablezco mi contraseña?")
        
        assert len(response) > 0
        assert confidence > 0
    
    def test_process_message_without_llm(self):
        """Test procesamiento de mensaje sin LLM."""
        chatbot = SupportChatbot(enable_llm=False)
        
        # Sin BD ni LLM, debería escalar
        response = chatbot.process_message("Necesito ayuda")
        
        assert response.chatbot_attempted is True
        assert response.resolved is False
        assert response.escalation_reason is not None
    
    def test_process_message_resolved(self, mock_db_connection, sample_faq_articles):
        """Test procesamiento que resuelve con FAQ."""
        mock_conn, mock_cursor = mock_db_connection
        
        # Mock de búsqueda de FAQ exitosa
        mock_cursor.fetchall.return_value = [
            ("faq-001", "¿Cómo restablezco mi contraseña?", "Para restablecer...", 
             "Instrucciones", "account", ["password"], ["contraseña", "password"])
        ]
        
        chatbot = SupportChatbot(
            db_connection=mock_conn,
            enable_llm=False
        )
        
        response = chatbot.process_message("¿Cómo restablezco mi contraseña?")
        
        assert response.faq_matched is True
        assert response.faq_article_id == "faq-001"


class TestChatbotResponse:
    """Tests para ChatbotResponse."""
    
    def test_chatbot_response_creation(self):
        """Test creación de respuesta."""
        response = ChatbotResponse(
            response_text="Respuesta",
            confidence=0.8,
            faq_matched=True,
            resolved=True
        )
        
        assert response.response_text == "Respuesta"
        assert response.confidence == 0.8
        assert response.faq_matched is True
        assert response.resolved is True


class TestFAQArticle:
    """Tests para FAQArticle."""
    
    def test_faq_article_creation(self):
        """Test creación de artículo FAQ."""
        article = FAQArticle(
            article_id="faq-001",
            title="Test FAQ",
            content="Content",
            category="test",
            tags=["tag1", "tag2"],
            keywords=["keyword1"]
        )
        
        assert article.article_id == "faq-001"
        assert article.title == "Test FAQ"
        assert len(article.tags) == 2

