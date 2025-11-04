"""
Tests unitarios para el módulo de priorización de tickets.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime, timedelta

import sys
sys.path.insert(0, '.')

from support_priority import SupportPriorityCalculator, PriorityScore


class TestSupportPriorityCalculator:
    """Tests para SupportPriorityCalculator."""
    
    def test_init(self):
        """Test inicialización."""
        calculator = SupportPriorityCalculator()
        assert calculator.db_connection is None
        assert len(calculator.vip_customers) == 0
    
    def test_init_with_vip(self):
        """Test inicialización con clientes VIP."""
        calculator = SupportPriorityCalculator(
            vip_customers=["vip@example.com"],
            enterprise_customers=["enterprise@example.com"]
        )
        assert len(calculator.vip_customers) == 1
        assert len(calculator.enterprise_customers) == 1
    
    def test_calculate_urgency_from_content_critical(self):
        """Test cálculo de urgencia con palabras críticas."""
        calculator = SupportPriorityCalculator()
        
        result = calculator.calculate_urgency_from_content(
            "URGENTE",
            "El sistema está caído, es crítico, necesito ayuda inmediata"
        )
        
        assert result["score"] > 0
        assert "critical" in str(result["factors"]).lower() or result["matches"]["critical"] > 0
    
    def test_calculate_urgency_from_content_urgent(self):
        """Test cálculo de urgencia con palabras urgentes."""
        calculator = SupportPriorityCalculator()
        
        result = calculator.calculate_urgency_from_content(
            "Urgente",
            "Necesito ayuda urgente, es importante"
        )
        
        assert result["score"] > 0
    
    def test_calculate_urgency_from_content_high(self):
        """Test cálculo de urgencia con problemas detectados."""
        calculator = SupportPriorityCalculator()
        
        result = calculator.calculate_urgency_from_content(
            "Problema",
            "Hay un error en el sistema, no funciona correctamente"
        )
        
        assert result["score"] > 0
    
    def test_calculate_customer_tier_vip(self):
        """Test cálculo de tier para cliente VIP."""
        calculator = SupportPriorityCalculator(
            vip_customers=["vip@example.com"]
        )
        
        result = calculator.calculate_customer_tier_score("vip@example.com")
        
        assert result["tier"] == "vip"
        assert result["score"] > 0
    
    def test_calculate_customer_tier_enterprise(self):
        """Test cálculo de tier para cliente Enterprise."""
        calculator = SupportPriorityCalculator(
            enterprise_customers=["enterprise@example.com"]
        )
        
        result = calculator.calculate_customer_tier_score("enterprise@example.com")
        
        assert result["tier"] == "enterprise"
        assert result["score"] > 0
    
    def test_calculate_customer_tier_standard(self):
        """Test cálculo de tier para cliente estándar."""
        calculator = SupportPriorityCalculator()
        
        result = calculator.calculate_customer_tier_score("standard@example.com")
        
        assert result["tier"] == "standard"
        assert result["score"] == 0.0
    
    def test_calculate_time_sensitivity(self):
        """Test cálculo de sensibilidad temporal."""
        calculator = SupportPriorityCalculator()
        
        result = calculator.calculate_time_sensitivity(
            "Urgente para hoy",
            "Necesito esto antes del deadline"
        )
        
        assert result["score"] >= 0
    
    def test_calculate_priority_low(self):
        """Test cálculo de prioridad baja."""
        calculator = SupportPriorityCalculator()
        
        priority = calculator.calculate_priority(
            subject="Consulta general",
            description="Tengo una pregunta",
            customer_email="standard@example.com"
        )
        
        assert priority.priority in ["low", "medium"]
        assert 0 <= priority.score <= 100
    
    def test_calculate_priority_high(self):
        """Test cálculo de prioridad alta."""
        calculator = SupportPriorityCalculator(
            vip_customers=["vip@example.com"]
        )
        
        priority = calculator.calculate_priority(
            subject="URGENTE: Sistema caído",
            description="El sistema está completamente caído, es crítico",
            customer_email="vip@example.com",
            source="phone"
        )
        
        assert priority.priority in ["high", "urgent", "critical"]
        assert priority.score >= 50
    
    def test_calculate_priority_with_category(self):
        """Test cálculo de prioridad con categoría."""
        calculator = SupportPriorityCalculator()
        
        priority = calculator.calculate_priority(
            subject="Problema de seguridad",
            description="Hay un problema de seguridad",
            customer_email="user@example.com",
            category="security"
        )
        
        # Security debería dar boost
        assert priority.score > 30  # Más que base score
    
    def test_priority_score_structure(self):
        """Test estructura del PriorityScore."""
        calculator = SupportPriorityCalculator()
        
        priority = calculator.calculate_priority(
            subject="Test",
            description="Test description",
            customer_email="test@example.com"
        )
        
        assert isinstance(priority, PriorityScore)
        assert priority.priority in ["low", "medium", "high", "urgent", "critical"]
        assert 0 <= priority.score <= 100
        assert isinstance(priority.factors, dict)
        assert len(priority.reasoning) > 0


class TestPriorityScore:
    """Tests para PriorityScore."""
    
    def test_priority_score_creation(self):
        """Test creación de PriorityScore."""
        score = PriorityScore(
            score=75.5,
            priority="urgent",
            factors={"test": "value"},
            reasoning="Test reasoning"
        )
        
        assert score.score == 75.5
        assert score.priority == "urgent"
        assert score.factors["test"] == "value"
        assert score.reasoning == "Test reasoning"

