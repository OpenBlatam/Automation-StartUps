"""
Sistema de Feature Flags para Nómina
Feature flags para habilitar/deshabilitar funcionalidades
"""

import logging
import os
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)


class FeatureFlag(str, Enum):
    """Feature flags disponibles"""
    ADVANCED_OCR = "advanced_ocr"
    AUTO_APPROVAL = "auto_approval"
    ANOMALY_DETECTION = "anomaly_detection"
    PREDICTIONS = "predictions"
    COMPLIANCE_CHECKS = "compliance_checks"
    CIRCUIT_BREAKERS = "circuit_breakers"
    RATE_LIMITING = "rate_limiting"
    WEBHOOKS = "webhooks"
    SYNC_ENABLED = "sync_enabled"
    VERSIONING = "versioning"


@dataclass
class FeatureFlagConfig:
    """Configuración de feature flag"""
    name: str
    enabled: bool
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class PayrollFeatureFlags:
    """Sistema de feature flags para nómina"""
    
    def __init__(self):
        """Inicializa feature flags desde variables de entorno"""
        self.flags: Dict[str, bool] = {}
        self._load_from_env()
    
    def _load_from_env(self) -> None:
        """Carga feature flags desde variables de entorno"""
        for flag in FeatureFlag:
            env_var = f"PAYROLL_FEATURE_{flag.value.upper()}"
            value = os.getenv(env_var, "false").lower()
            self.flags[flag.value] = value in ("true", "1", "yes", "on")
    
    def is_enabled(self, flag: FeatureFlag) -> bool:
        """Verifica si un feature flag está habilitado"""
        return self.flags.get(flag.value, False)
    
    def enable(self, flag: FeatureFlag) -> None:
        """Habilita un feature flag"""
        self.flags[flag.value] = True
    
    def disable(self, flag: FeatureFlag) -> None:
        """Deshabilita un feature flag"""
        self.flags[flag.value] = False
    
    def get_all_flags(self) -> Dict[str, bool]:
        """Obtiene todos los feature flags"""
        return self.flags.copy()
    
    def get_flag_config(self, flag: FeatureFlag) -> FeatureFlagConfig:
        """Obtiene configuración de un feature flag"""
        return FeatureFlagConfig(
            name=flag.value,
            enabled=self.is_enabled(flag),
            description=self._get_description(flag)
        )
    
    def _get_description(self, flag: FeatureFlag) -> str:
        """Obtiene descripción de un feature flag"""
        descriptions = {
            FeatureFlag.ADVANCED_OCR: "Advanced OCR processing with ML",
            FeatureFlag.AUTO_APPROVAL: "Automatic approval for low-value expenses",
            FeatureFlag.ANOMALY_DETECTION: "Anomaly detection in payroll calculations",
            FeatureFlag.PREDICTIONS: "Payroll predictions based on historical data",
            FeatureFlag.COMPLIANCE_CHECKS: "Automatic compliance checks",
            FeatureFlag.CIRCUIT_BREAKERS: "Circuit breakers for external services",
            FeatureFlag.RATE_LIMITING: "Rate limiting for API calls",
            FeatureFlag.WEBHOOKS: "Webhook notifications",
            FeatureFlag.SYNC_ENABLED: "Synchronization with external systems",
            FeatureFlag.VERSIONING: "Data versioning system"
        }
        return descriptions.get(flag, "No description available")


# Instancia global
feature_flags = PayrollFeatureFlags()

