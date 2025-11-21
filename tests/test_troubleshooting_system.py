"""
Tests Automatizados para el Sistema de Troubleshooting
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Agregar path para imports
sys.path.insert(0, str(Path(__file__).parent))

from support_troubleshooting_agent import (
    TroubleshootingAgent,
    TroubleshootingStatus,
    ProblemCategory
)


class TestTroubleshootingAgent:
    """Tests para TroubleshootingAgent"""
    
    @pytest.fixture
    def agent(self):
        """Fixture para crear agente de prueba"""
        return TroubleshootingAgent()
    
    @pytest.fixture
    def sample_session(self, agent):
        """Fixture para crear sesión de prueba"""
        return agent.start_troubleshooting(
            problem_description="No puedo instalar el software",
            customer_email="test@example.com",
            customer_name="Test User"
        )
    
    def test_agent_initialization(self, agent):
        """Test que el agente se inicializa correctamente"""
        assert agent is not None
        assert agent.knowledge_base is not None
        assert len(agent.knowledge_base) > 0
    
    def test_problem_detection(self, agent):
        """Test detección de problemas"""
        # Problema conocido
        guide = agent.detect_problem("No puedo instalar el software en mi computadora")
        assert guide is not None
        assert guide.problem_id == "instalacion_software"
        
        # Problema desconocido
        guide = agent.detect_problem("Mi gato tiene hambre")
        assert guide is None
    
    def test_start_troubleshooting(self, agent):
        """Test inicio de sesión"""
        session = agent.start_troubleshooting(
            problem_description="Problema de conexión a internet",
            customer_email="test@example.com"
        )
        
        assert session is not None
        assert session.session_id is not None
        assert session.customer_email == "test@example.com"
        assert session.status in [TroubleshootingStatus.STARTED, TroubleshootingStatus.NEEDS_ESCALATION]
    
    def test_get_current_step(self, agent, sample_session):
        """Test obtener paso actual"""
        step = agent.get_current_step(sample_session.session_id)
        
        assert step is not None
        if step.get("status") != "no_problem_detected":
            assert "step_number" in step
            assert "title" in step
            assert "instructions" in step
    
    def test_complete_step_success(self, agent, sample_session):
        """Test completar paso exitosamente"""
        result = agent.complete_step(
            session_id=sample_session.session_id,
            success=True,
            notes="Paso completado correctamente"
        )
        
        assert result is not None
        assert result.get("status") in ["next_step", "resolved"]
    
    def test_complete_step_failure(self, agent, sample_session):
        """Test completar paso con fallo"""
        result = agent.complete_step(
            session_id=sample_session.session_id,
            success=False,
            notes="No pude completar el paso"
        )
        
        assert result is not None
        assert result.get("status") in ["step_failed", "needs_escalation"]
    
    def test_escalation(self, agent, sample_session):
        """Test escalación de ticket"""
        escalation_info = agent.escalate_ticket(
            session_id=sample_session.session_id,
            reason="Múltiples pasos fallidos"
        )
        
        assert escalation_info is not None
        assert "session_id" in escalation_info
        assert "reason" in escalation_info
    
    def test_feedback_collection(self, agent, sample_session):
        """Test recolección de feedback"""
        feedback = agent.collect_feedback(
            session_id=sample_session.session_id,
            rating=5,
            feedback_text="Muy útil",
            was_helpful=True
        )
        
        assert feedback is not None
        assert feedback["rating"] == 5
        assert feedback["was_helpful"] is True
    
    def test_session_summary(self, agent, sample_session):
        """Test resumen de sesión"""
        summary = agent.get_session_summary(sample_session.session_id)
        
        assert summary is not None
        assert "session_id" in summary
        assert "status" in summary
        assert "current_step" in summary
    
    def test_format_step_response(self, agent, sample_session):
        """Test formateo de respuesta"""
        step = agent.get_current_step(sample_session.session_id)
        if step and step.get("status") != "no_problem_detected":
            formatted = agent.format_step_response(step)
            
            assert formatted is not None
            assert len(formatted) > 0
            assert "Paso" in formatted or "paso" in formatted.lower()


class TestTroubleshootingWebhooks:
    """Tests para sistema de webhooks"""
    
    @pytest.fixture
    def webhook_manager(self):
        """Fixture para crear webhook manager"""
        from support_troubleshooting_webhooks import (
            TroubleshootingWebhookManager,
            WebhookConfig,
            WebhookEvent
        )
        return TroubleshootingWebhookManager()
    
    def test_register_webhook(self, webhook_manager):
        """Test registro de webhook"""
        from support_troubleshooting_webhooks import WebhookConfig, WebhookEvent
        
        config = WebhookConfig(
            url="https://example.com/webhook",
            events=[WebhookEvent.SESSION_STARTED],
            secret="test-secret"
        )
        
        webhook_manager.register_webhook("test-webhook", config)
        
        assert "test-webhook" in webhook_manager.webhooks
    
    def test_trigger_webhook(self, webhook_manager):
        """Test disparar webhook"""
        from support_troubleshooting_webhooks import WebhookConfig, WebhookEvent
        
        config = WebhookConfig(
            url="https://httpbin.org/post",  # Servicio de prueba
            events=[WebhookEvent.SESSION_STARTED]
        )
        
        webhook_manager.register_webhook("test", config)
        
        result = webhook_manager.trigger_webhook(
            WebhookEvent.SESSION_STARTED,
            {"test": "data"}
        )
        
        assert result is not None
        assert "webhooks_triggered" in result


class TestTroubleshootingTemplates:
    """Tests para sistema de plantillas"""
    
    @pytest.fixture
    def template_manager(self):
        """Fixture para crear template manager"""
        from support_troubleshooting_templates import TroubleshootingTemplateManager
        return TroubleshootingTemplateManager()
    
    def test_list_templates(self, template_manager):
        """Test listar plantillas"""
        templates = template_manager.list_templates()
        
        assert isinstance(templates, list)
        assert len(templates) > 0
    
    def test_render_template(self, template_manager):
        """Test renderizar plantilla"""
        rendered = template_manager.render_template(
            "reset_password_template",
            {
                "product_name": "Test App",
                "reset_url": "https://test.com/reset",
                "support_email": "support@test.com"
            }
        )
        
        assert rendered is not None
        assert "problem_title" in rendered
        assert "steps" in rendered
        assert "Test App" in rendered["problem_title"]


class TestIntegration:
    """Tests de integración end-to-end"""
    
    def test_full_troubleshooting_flow(self):
        """Test flujo completo de troubleshooting"""
        agent = TroubleshootingAgent()
        
        # 1. Iniciar sesión
        session = agent.start_troubleshooting(
            problem_description="No puedo conectarme a internet",
            customer_email="test@example.com",
            customer_name="Test User"
        )
        
        assert session is not None
        
        # 2. Obtener primer paso
        step = agent.get_current_step(session.session_id)
        assert step is not None
        
        # 3. Completar pasos
        if step.get("status") != "no_problem_detected":
            for i in range(min(3, len(session.detected_problem.steps) if session.detected_problem else 0)):
                result = agent.complete_step(
                    session.session_id,
                    success=True
                )
                
                if result.get("status") == "resolved":
                    break
        
        # 4. Recolectar feedback
        feedback = agent.collect_feedback(
            session.session_id,
            rating=5,
            was_helpful=True
        )
        
        assert feedback is not None
        
        # 5. Obtener resumen
        summary = agent.get_session_summary(session.session_id)
        assert summary is not None


# Configuración de pytest
if __name__ == "__main__":
    pytest.main([__file__, "-v"])



