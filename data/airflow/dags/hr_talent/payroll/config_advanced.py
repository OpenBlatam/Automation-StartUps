"""
Configuración Avanzada para Nómina
Gestión de configuración con validación y override
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from decimal import Decimal
import json

logger = logging.getLogger(__name__)


@dataclass
class PayrollAdvancedConfig:
    """Configuración avanzada del sistema de nómina"""
    # Cálculos
    regular_hours_per_week: Decimal = Decimal("40.0")
    overtime_multiplier: Decimal = Decimal("1.5")
    double_time_multiplier: Decimal = Decimal("2.0")
    max_hours_per_day: Decimal = Decimal("16.0")
    max_hours_per_week: Decimal = Decimal("80.0")
    
    # Deducciones
    default_tax_rate: Decimal = Decimal("0.25")
    default_benefits_rate: Decimal = Decimal("0.10")
    minimum_wage: Decimal = Decimal("7.25")
    
    # Aprobaciones
    auto_approve_expenses_threshold: Decimal = Decimal("50.00")
    high_value_approval_threshold: Decimal = Decimal("5000.00")
    
    # OCR
    ocr_confidence_threshold: float = 0.7
    ocr_retry_attempts: int = 3
    
    # Rate Limiting
    payroll_calc_rate_limit: int = 50  # per minute
    ocr_rate_limit: int = 20  # per minute
    db_query_rate_limit: int = 100  # per second
    
    # Circuit Breakers
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_timeout: int = 60  # seconds
    
    # Compliance
    compliance_check_enabled: bool = True
    compliance_min_withholding_rate: Decimal = Decimal("0.10")
    
    # Notifications
    notification_enabled: bool = True
    slack_notifications_enabled: bool = True
    email_notifications_enabled: bool = True
    
    # Cache
    cache_enabled: bool = True
    cache_ttl_seconds: int = 1800
    
    # Feature Flags
    feature_flags: Dict[str, bool] = field(default_factory=dict)
    
    # Overrides
    overrides: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_env(cls) -> "PayrollAdvancedConfig":
        """Carga configuración desde variables de entorno"""
        config = cls()
        
        # Cálculos
        if os.getenv("PAYROLL_REGULAR_HOURS_PER_WEEK"):
            config.regular_hours_per_week = Decimal(
                os.getenv("PAYROLL_REGULAR_HOURS_PER_WEEK")
            )
        
        if os.getenv("PAYROLL_OVERTIME_MULTIPLIER"):
            config.overtime_multiplier = Decimal(
                os.getenv("PAYROLL_OVERTIME_MULTIPLIER")
            )
        
        if os.getenv("PAYROLL_DOUBLE_TIME_MULTIPLIER"):
            config.double_time_multiplier = Decimal(
                os.getenv("PAYROLL_DOUBLE_TIME_MULTIPLIER")
            )
        
        # Deducciones
        if os.getenv("PAYROLL_DEFAULT_TAX_RATE"):
            config.default_tax_rate = Decimal(
                os.getenv("PAYROLL_DEFAULT_TAX_RATE")
            )
        
        if os.getenv("PAYROLL_MINIMUM_WAGE"):
            config.minimum_wage = Decimal(os.getenv("PAYROLL_MINIMUM_WAGE"))
        
        # Aprobaciones
        if os.getenv("PAYROLL_AUTO_APPROVE_THRESHOLD"):
            config.auto_approve_expenses_threshold = Decimal(
                os.getenv("PAYROLL_AUTO_APPROVE_THRESHOLD")
            )
        
        # OCR
        if os.getenv("PAYROLL_OCR_CONFIDENCE_THRESHOLD"):
            config.ocr_confidence_threshold = float(
                os.getenv("PAYROLL_OCR_CONFIDENCE_THRESHOLD")
            )
        
        # Rate Limiting
        if os.getenv("PAYROLL_RATE_LIMIT_CALC"):
            config.payroll_calc_rate_limit = int(
                os.getenv("PAYROLL_RATE_LIMIT_CALC")
            )
        
        # Feature Flags
        for flag_name in [
            "ADVANCED_OCR", "AUTO_APPROVAL", "ANOMALY_DETECTION",
            "PREDICTIONS", "COMPLIANCE_CHECKS", "CIRCUIT_BREAKERS",
            "RATE_LIMITING", "WEBHOOKS", "SYNC_ENABLED", "VERSIONING"
        ]:
            env_var = f"PAYROLL_FEATURE_{flag_name}"
            if os.getenv(env_var):
                config.feature_flags[flag_name.lower()] = (
                    os.getenv(env_var).lower() in ("true", "1", "yes", "on")
                )
        
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte configuración a diccionario"""
        return {
            "regular_hours_per_week": float(self.regular_hours_per_week),
            "overtime_multiplier": float(self.overtime_multiplier),
            "double_time_multiplier": float(self.double_time_multiplier),
            "max_hours_per_day": float(self.max_hours_per_day),
            "max_hours_per_week": float(self.max_hours_per_week),
            "default_tax_rate": float(self.default_tax_rate),
            "default_benefits_rate": float(self.default_benefits_rate),
            "minimum_wage": float(self.minimum_wage),
            "auto_approve_expenses_threshold": float(self.auto_approve_expenses_threshold),
            "high_value_approval_threshold": float(self.high_value_approval_threshold),
            "ocr_confidence_threshold": self.ocr_confidence_threshold,
            "ocr_retry_attempts": self.ocr_retry_attempts,
            "payroll_calc_rate_limit": self.payroll_calc_rate_limit,
            "ocr_rate_limit": self.ocr_rate_limit,
            "db_query_rate_limit": self.db_query_rate_limit,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "circuit_breaker_timeout": self.circuit_breaker_timeout,
            "compliance_check_enabled": self.compliance_check_enabled,
            "compliance_min_withholding_rate": float(self.compliance_min_withholding_rate),
            "notification_enabled": self.notification_enabled,
            "slack_notifications_enabled": self.slack_notifications_enabled,
            "email_notifications_enabled": self.email_notifications_enabled,
            "cache_enabled": self.cache_enabled,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "feature_flags": self.feature_flags,
            "overrides": self.overrides
        }
    
    def validate(self) -> tuple[bool, Optional[str]]:
        """Valida la configuración"""
        errors = []
        
        # Validar valores numéricos
        if self.regular_hours_per_week <= 0:
            errors.append("regular_hours_per_week must be positive")
        
        if self.overtime_multiplier < 1.0:
            errors.append("overtime_multiplier must be >= 1.0")
        
        if self.default_tax_rate < 0 or self.default_tax_rate > 1:
            errors.append("default_tax_rate must be between 0 and 1")
        
        if self.ocr_confidence_threshold < 0 or self.ocr_confidence_threshold > 1:
            errors.append("ocr_confidence_threshold must be between 0 and 1")
        
        if self.payroll_calc_rate_limit <= 0:
            errors.append("payroll_calc_rate_limit must be positive")
        
        if errors:
            return False, "; ".join(errors)
        
        return True, None
    
    def apply_overrides(self, overrides: Dict[str, Any]) -> None:
        """Aplica overrides a la configuración"""
        for key, value in overrides.items():
            if hasattr(self, key):
                # Convertir a Decimal si es necesario
                if isinstance(getattr(self, key), Decimal):
                    setattr(self, key, Decimal(str(value)))
                else:
                    setattr(self, key, value)
                
                # Guardar en overrides
                self.overrides[key] = value
            else:
                logger.warning(f"Unknown config key: {key}")

