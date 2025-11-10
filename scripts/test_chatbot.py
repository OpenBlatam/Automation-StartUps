#!/usr/bin/env python3
"""
Tests Unitarios para los Chatbots
Ejecuta tests básicos de funcionalidad
"""

import unittest
import sys
from pathlib import Path

# Agregar el directorio de scripts al path
sys.path.insert(0, str(Path(__file__).parent))

from chatbot_curso_ia_webinars import CursoIAWebinarChatbot, IntentType


class TestChatbotBasic(unittest.TestCase):
    """Tests básicos del chatbot"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.chatbot = CursoIAWebinarChatbot(
            enable_logging=False,
            persist_conversations=False,
            enable_rate_limiting=False,
            enable_feedback=False
        )
    
    def test_initialization(self):
        """Test de inicialización"""
        self.assertIsNotNone(self.chatbot)
        self.assertGreater(len(self.chatbot.faqs), 0)
        self.assertGreater(len(self.chatbot.webinars), 0)
    
    def test_detect_intent_precio(self):
        """Test de detección de intención de precio"""
        intent = self.chatbot.detect_intent("¿Cuánto cuesta el curso?")
        self.assertEqual(intent, IntentType.PRECIO_CURSO)
    
    def test_detect_intent_webinar(self):
        """Test de detección de intención de webinar"""
        intent = self.chatbot.detect_intent("¿Cuándo son los próximos webinars?")
        self.assertEqual(intent, IntentType.WEBINAR_PROXIMOS)
    
    def test_search_faq(self):
        """Test de búsqueda de FAQ"""
        faq = self.chatbot.search_faq("¿Cuánto cuesta el curso?")
        self.assertIsNotNone(faq)
        self.assertIn("precio", faq['category'].lower() or faq['question'].lower())
    
    def test_process_message(self):
        """Test de procesamiento de mensaje"""
        response = self.chatbot.process_message("¿Cuánto cuesta el curso?")
        self.assertIsNotNone(response)
        self.assertIn("response", response)
        self.assertIn("confidence", response)
        self.assertIn("intent", response)
        self.assertGreater(response["confidence"], 0)
    
    def test_empty_message(self):
        """Test de mensaje vacío"""
        response = self.chatbot.process_message("")
        self.assertIn("error", response)
    
    def test_escalation_detection(self):
        """Test de detección de escalación"""
        needs_escalation, reason = self.chatbot.check_escalation_needed(
            "Necesito un reembolso urgente",
            IntentType.OTRO
        )
        self.assertTrue(needs_escalation)
    
    def test_metrics(self):
        """Test de métricas"""
        # Procesar algunos mensajes
        self.chatbot.process_message("¿Cuánto cuesta?")
        self.chatbot.process_message("¿Qué incluye?")
        
        metrics = self.chatbot.get_metrics()
        self.assertEqual(metrics["total_messages"], 2)
        self.assertGreater(metrics["average_confidence"], 0)
    
    def test_cache(self):
        """Test de cache"""
        message = "¿Cuánto cuesta el curso?"
        
        # Primera vez (sin cache)
        response1 = self.chatbot.process_message(message)
        time1 = response1.get("processing_time", 0)
        
        # Segunda vez (con cache)
        response2 = self.chatbot.process_message(message)
        time2 = response2.get("processing_time", 0)
        
        # El tiempo debería ser menor o igual (cache es más rápido)
        self.assertLessEqual(time2, time1)
        self.assertEqual(response1["response"], response2["response"])


class TestChatbotAdvanced(unittest.TestCase):
    """Tests de funcionalidades avanzadas"""
    
    def setUp(self):
        """Configuración antes de cada test"""
        self.chatbot = CursoIAWebinarChatbot(
            enable_logging=False,
            persist_conversations=True,
            enable_rate_limiting=True,
            enable_feedback=True
        )
    
    def test_rate_limiting(self):
        """Test de rate limiting"""
        if not self.chatbot.enable_rate_limiting:
            self.skipTest("Rate limiting no disponible")
        
        user_id = "test_user"
        
        # Hacer muchas requests rápidamente
        for i in range(65):  # Más del límite de 60
            response = self.chatbot.process_message(
                f"Mensaje de prueba {i}",
                user_id=user_id
            )
            
            if i >= 60:
                # Después del límite, debería estar rate limited
                if "rate_limited" in response:
                    self.assertTrue(response["rate_limited"])
                    break
    
    def test_feedback_system(self):
        """Test del sistema de feedback"""
        if not self.chatbot.enable_feedback:
            self.skipTest("Sistema de feedback no disponible")
        
        # Agregar feedback
        success = self.chatbot.add_feedback(
            conversation_id="test_conv",
            message_id="test_msg",
            feedback_type="positive",
            comment="Test feedback"
        )
        self.assertTrue(success)
        
        # Obtener estadísticas
        stats = self.chatbot.get_feedback_stats()
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats["total"], 1)
    
    def test_health_check(self):
        """Test de health check"""
        health = self.chatbot.health_check()
        self.assertIn("status", health)
        self.assertIn("timestamp", health)
        self.assertIn("metrics", health)
        self.assertIn(health["status"], ["healthy", "warning"])
    
    def test_export_metrics(self):
        """Test de exportación de métricas"""
        # Procesar algunos mensajes
        self.chatbot.process_message("Test 1")
        self.chatbot.process_message("Test 2")
        
        # Exportar
        json_file = self.chatbot.export_metrics(format="json")
        self.assertTrue(Path(json_file).exists())
        
        # Limpiar
        Path(json_file).unlink()


def run_tests():
    """Ejecuta todos los tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Agregar tests básicos
    suite.addTests(loader.loadTestsFromTestCase(TestChatbotBasic))
    
    # Agregar tests avanzados
    suite.addTests(loader.loadTestsFromTestCase(TestChatbotAdvanced))
    
    # Ejecutar
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)






