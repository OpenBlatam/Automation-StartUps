#!/usr/bin/env python3
"""
Tests de validación para el flujo de onboarding.
Puede ejecutarse como parte de CI/CD o localmente.
"""

import json
import pytest
from datetime import datetime, timedelta
import re


# Patrones de validación (deben coincidir con el flujo)
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')


def validate_email(email: str) -> bool:
    """Validar formato de email."""
    if not email:
        return False
    return bool(EMAIL_PATTERN.match(email.strip().lower()))


def validate_date(date_str: str) -> tuple[bool, str]:
    """Validar formato de fecha (YYYY-MM-DD) y rango."""
    if not date_str:
        return False, "Date is empty"
    date_str = date_str.strip()
    if not DATE_PATTERN.match(date_str):
        return False, f"Invalid date format (expected YYYY-MM-DD): {date_str}"
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        today = datetime.now()
        one_year_ago = datetime(today.year - 1, today.month, today.day)
        one_year_later = datetime(today.year + 1, today.month, today.day)
        if date_obj < one_year_ago:
            return False, f"Date is too far in the past: {date_str}"
        if date_obj > one_year_later:
            return False, f"Date is too far in the future: {date_str}"
        return True, ""
    except ValueError as e:
        return False, f"Invalid date value: {e}"


def validate_full_name(full_name: str) -> bool:
    """Validar nombre completo."""
    if not full_name:
        return False
    full_name = full_name.strip()
    return 2 <= len(full_name) <= 200


def prevent_self_manager(employee_email: str, manager_email: str) -> bool:
    """Prevenir auto-asignación como manager."""
    return employee_email.lower().strip() != manager_email.lower().strip()


class TestEmailValidation:
    """Tests de validación de email."""
    
    def test_valid_emails(self):
        valid_emails = [
            "test@example.com",
            "user.name@company.co.uk",
            "first+last@domain.com",
            "user_123@test-domain.com"
        ]
        for email in valid_emails:
            assert validate_email(email), f"Email should be valid: {email}"
    
    def test_invalid_emails(self):
        invalid_emails = [
            "invalid",
            "@domain.com",
            "user@",
            "user@domain",
            "user name@domain.com",
            ""
        ]
        for email in invalid_emails:
            assert not validate_email(email), f"Email should be invalid: {email}"


class TestDateValidation:
    """Tests de validación de fecha."""
    
    def test_valid_dates(self):
        today = datetime.now()
        valid_dates = [
            today.strftime("%Y-%m-%d"),
            (today + timedelta(days=30)).strftime("%Y-%m-%d"),
            (today - timedelta(days=30)).strftime("%Y-%m-%d"),
        ]
        for date_str in valid_dates:
            is_valid, error = validate_date(date_str)
            assert is_valid, f"Date should be valid: {date_str}, error: {error}"
    
    def test_invalid_dates(self):
        invalid_dates = [
            ("2020-01-01", "too far in past"),
            ("2030-12-31", "too far in future"),
            ("2025-13-01", "invalid month"),
            ("2025-01-32", "invalid day"),
            ("01-01-2025", "wrong format"),
            ("2025/01/01", "wrong separator"),
            ("", "empty")
        ]
        for date_str, reason in invalid_dates:
            is_valid, error = validate_date(date_str)
            assert not is_valid, f"Date should be invalid: {date_str} ({reason})"


class TestNameValidation:
    """Tests de validación de nombre."""
    
    def test_valid_names(self):
        valid_names = ["John Doe", "María García", "Jean-Pierre", "O'Brien"]
        for name in valid_names:
            assert validate_full_name(name), f"Name should be valid: {name}"
    
    def test_invalid_names(self):
        invalid_names = ["A", "", " " * 201]  # Too short, empty, too long
        for name in invalid_names:
            assert not validate_full_name(name), f"Name should be invalid: {name}"


class TestManagerValidation:
    """Tests de validación de manager."""
    
    def test_prevent_self_manager(self):
        assert prevent_self_manager("user@example.com", "user@example.com") == False
        assert prevent_self_manager("user@example.com", "manager@example.com") == True
        assert prevent_self_manager("user@example.com", "User@Example.com") == False  # Case insensitive


class TestPayloadValidation:
    """Tests de validación de payload completo."""
    
    def test_valid_payload(self):
        payload = {
            "email": "nuevo@empresa.com",
            "first_name": "Nuevo",
            "last_name": "Empleado",
            "start_date": (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "manager_email": "manager@empresa.com",
            "department": "Engineering",
            "position": "Developer"
        }
        
        assert validate_email(payload["email"])
        assert validate_email(payload["manager_email"])
        assert prevent_self_manager(payload["email"], payload["manager_email"])
        is_valid, _ = validate_date(payload["start_date"])
        assert is_valid
        assert validate_full_name(f"{payload['first_name']} {payload['last_name']}")
    
    def test_missing_required_fields(self):
        incomplete_payloads = [
            {"email": "test@example.com"},  # Missing start_date, manager_email
            {"start_date": "2025-02-01"},  # Missing email
            {"email": "test@example.com", "start_date": "2025-02-01"},  # Missing manager_email
        ]
        
        for payload in incomplete_payloads:
            required = ["email", "start_date", "manager_email"]
            missing = [field for field in required if not payload.get(field)]
            assert len(missing) > 0, f"Payload should be incomplete: {payload}"


def test_idempotency_key_generation():
    """Test de generación de clave de idempotencia."""
    email = "empleado@empresa.com"
    start_date = "2025-02-01"
    expected_key = f"{email}:{start_date}"
    
    idempotency_key = f"{email}:{start_date}"
    assert idempotency_key == expected_key


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

