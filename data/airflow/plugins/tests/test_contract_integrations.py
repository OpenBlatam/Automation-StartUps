"""
Tests para el Sistema de Gestión de Contratos
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Importar funciones a testear
from data.airflow.plugins.contract_integrations import (
    generate_contract_from_template,
    calculate_document_hash,
    create_contract_from_template,
    get_template,
    send_contract_for_signature,
    check_contract_signature_status
)


class TestContractGeneration:
    """Tests para generación de contratos"""
    
    def test_generate_contract_from_template(self):
        """Test de generación de contrato desde template"""
        template = "Hola {{name}}, tu salario es {{salary}}"
        variables = {"name": "Juan", "salary": "$5000"}
        
        result = generate_contract_from_template(template, variables)
        
        assert "Juan" in result
        assert "$5000" in result
        assert "{{name}}" not in result
        assert "{{salary}}" not in result
    
    def test_generate_contract_missing_variables(self):
        """Test con variables faltantes"""
        template = "Hola {{name}}, tu salario es {{salary}}"
        variables = {"name": "Juan"}
        
        result = generate_contract_from_template(template, variables)
        
        # Las variables faltantes deben quedar sin reemplazar
        assert "Juan" in result
        assert "{{salary}}" in result
    
    def test_calculate_document_hash(self):
        """Test de cálculo de hash"""
        content = b"test document content"
        hash1 = calculate_document_hash(content)
        hash2 = calculate_document_hash(content)
        
        # Mismo contenido debe dar mismo hash
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produce hash de 64 caracteres hex
        
        # Contenido diferente debe dar hash diferente
        content2 = b"different content"
        hash3 = calculate_document_hash(content2)
        assert hash1 != hash3


class TestContractValidation:
    """Tests para validación de contratos"""
    
    def test_validate_template_variables(self):
        """Test de validación de variables de template"""
        from data.airflow.plugins.contract_validation import ContractValidator
        
        validator = ContractValidator()
        template = "Contrato para {{employee_name}} en posición {{position}}"
        variables = {"employee_name": "Juan", "position": "Engineer"}
        
        is_valid, errors = validator.validate_template(template, variables)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_template_missing_variables(self):
        """Test con variables faltantes"""
        from data.airflow.plugins.contract_validation import ContractValidator
        
        validator = ContractValidator()
        template = "Contrato para {{employee_name}} en posición {{position}}"
        variables = {"employee_name": "Juan"}
        
        is_valid, errors = validator.validate_template(template, variables)
        
        assert not is_valid
        assert len(errors) > 0
        assert "position" in errors[0]
    
    def test_validate_contract_data(self):
        """Test de validación de datos de contrato"""
        from data.airflow.plugins.contract_validation import ContractValidator
        
        validator = ContractValidator()
        contract_data = {
            "primary_party_email": "test@example.com",
            "start_date": "2024-01-01",
            "expiration_days": 365,
            "signers_required": [
                {"email": "signer@example.com", "name": "Signer", "role": "signer", "order": 1}
            ]
        }
        
        is_valid, errors = validator.validate_contract_data(contract_data)
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_invalid_email(self):
        """Test con email inválido"""
        from data.airflow.plugins.contract_validation import ContractValidator
        
        validator = ContractValidator()
        contract_data = {
            "primary_party_email": "invalid-email",
            "start_date": "2024-01-01"
        }
        
        is_valid, errors = validator.validate_contract_data(contract_data)
        
        assert not is_valid
        assert any("email" in error.lower() for error in errors)


class TestContractBusinessRules:
    """Tests para reglas de negocio"""
    
    def test_validate_contract_duration(self):
        """Test de validación de duración"""
        from data.airflow.plugins.contract_validation import ContractBusinessRulesValidator
        
        validator = ContractBusinessRulesValidator()
        
        # Contrato laboral con duración válida
        is_valid, error = validator.validate_contract_duration("employment", 365)
        assert is_valid
        assert error is None
        
        # Contrato laboral con duración muy corta
        is_valid, error = validator.validate_contract_duration("employment", 10)
        assert not is_valid
        assert error is not None
    
    def test_validate_signers_order(self):
        """Test de validación de orden de firmantes"""
        from data.airflow.plugins.contract_validation import ContractBusinessRulesValidator
        
        validator = ContractBusinessRulesValidator()
        
        # Orden válido
        signers = [
            {"email": "signer1@example.com", "order": 1},
            {"email": "signer2@example.com", "order": 2}
        ]
        is_valid, error = validator.validate_signers_order(signers)
        assert is_valid
        
        # Orden inválido
        signers = [
            {"email": "signer1@example.com", "order": 1},
            {"email": "signer2@example.com", "order": 3}  # Falta el 2
        ]
        is_valid, error = validator.validate_signers_order(signers)
        assert not is_valid


class TestCircuitBreaker:
    """Tests para Circuit Breaker"""
    
    def test_circuit_breaker_closed_state(self):
        """Test de circuit breaker en estado CLOSED"""
        from data.airflow.plugins.contract_circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        
        breaker = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
        
        # Estado inicial debe ser CLOSED
        assert breaker.state.value == "closed"
        
        # Ejecutar función exitosa
        def success_func():
            return "success"
        
        result = breaker.call(success_func)
        assert result == "success"
        assert breaker.state.value == "closed"
    
    def test_circuit_breaker_opens_after_failures(self):
        """Test de circuit breaker abriéndose después de fallos"""
        from data.airflow.plugins.contract_circuit_breaker import CircuitBreaker, CircuitBreakerConfig
        
        breaker = CircuitBreaker("test", CircuitBreakerConfig(failure_threshold=3))
        
        # Ejecutar función que falla
        def fail_func():
            raise Exception("Test error")
        
        # Debe fallar pero no abrir aún
        with pytest.raises(Exception):
            breaker.call(fail_func)
        
        # Después de 3 fallos, debe abrir
        for _ in range(2):
            with pytest.raises(Exception):
                breaker.call(fail_func)
        
        assert breaker.state.value == "open"
        
        # Intentar ejecutar cuando está abierto debe fallar inmediatamente
        with pytest.raises(Exception) as exc_info:
            breaker.call(fail_func)
        assert "OPEN" in str(exc_info.value)


class TestRateLimiter:
    """Tests para Rate Limiter"""
    
    def test_rate_limiter_allows_requests(self):
        """Test de rate limiter permitiendo requests"""
        from data.airflow.plugins.contract_rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=10, window_seconds=60)
        
        # Primeros 10 requests deben ser permitidos
        for i in range(10):
            is_allowed, info = limiter.is_allowed("test_key")
            assert is_allowed
            assert info["remaining"] == 10 - i - 1
    
    def test_rate_limiter_blocks_after_limit(self):
        """Test de rate limiter bloqueando después del límite"""
        from data.airflow.plugins.contract_rate_limiter import RateLimiter
        
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        
        # Primeros 5 requests permitidos
        for _ in range(5):
            is_allowed, _ = limiter.is_allowed("test_key")
            assert is_allowed
        
        # El 6to request debe ser bloqueado
        is_allowed, info = limiter.is_allowed("test_key")
        assert not is_allowed
        assert info["remaining"] == 0


class TestContractML:
    """Tests para Machine Learning"""
    
    @patch('data.airflow.plugins.contract_ml.PostgresHook')
    def test_predict_contract_signature_time(self, mock_hook):
        """Test de predicción de tiempo de firma"""
        from data.airflow.plugins.contract_ml import predict_contract_signature_time
        
        # Mock de hook
        mock_instance = MagicMock()
        mock_instance.get_first.return_value = (7.0, 2.0, 50)  # avg, stddev, count
        mock_hook.return_value = mock_instance
        
        result = predict_contract_signature_time(
            contract_type="employment",
            signers_count=2
        )
        
        assert "predicted_days" in result
        assert "confidence" in result
        assert result["predicted_days"] > 0
    
    @patch('data.airflow.plugins.contract_ml.PostgresHook')
    def test_get_contract_health_score(self, mock_hook):
        """Test de health score"""
        from data.airflow.plugins.contract_ml import get_contract_health_score
        
        # Mock de hook
        mock_instance = MagicMock()
        mock_instance.get_first.return_value = (
            "fully_signed",  # status
            datetime.now(),  # created_at
            datetime.now(),  # signed_date
            datetime.now() + timedelta(days=365),  # expiration_date
            "employment",  # contract_type
            True,  # auto_renew
            5,  # events_count
            2,  # signers_count
            1  # has_version
        )
        mock_hook.return_value = mock_instance
        
        result = get_contract_health_score("CONTRACT-123")
        
        assert "health_score" in result
        assert "health_level" in result
        assert 0 <= result["health_score"] <= 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

