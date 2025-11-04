"""
Helpers para migrar de variables de entorno a Vault y viceversa.
"""

from __future__ import annotations

import os
import logging
from typing import Dict, Any, Optional
from data.airflow.plugins.vault_integration import get_secret

logger = logging.getLogger(__name__)


def get_config_with_fallback(
    vault_path: str,
    vault_key: Optional[str],
    env_var: str,
    default: Optional[str] = None,
    required: bool = False
) -> Optional[str]:
    """
    Obtiene configuración desde Vault con fallback a variable de entorno.
    
    Útil para migración gradual de variables de entorno a Vault.
    
    Args:
        vault_path: Ruta en Vault (ej: "airflow/config/slack_webhook_url")
        vault_key: Clave dentro del secreto (ej: "url")
        env_var: Nombre de variable de entorno como fallback
        default: Valor por defecto si no se encuentra en ningún lado
        required: Si True, lanza excepción si no se encuentra
    
    Returns:
        Valor de configuración o None
    
    Example:
        webhook = get_config_with_fallback(
            "notifications/slack/webhook",
            "url",
            "SLACK_WEBHOOK_URL",
            required=True
        )
    """
    # Intentar desde Vault primero
    vault_value = get_secret(vault_path, vault_key, fallback_env=None, required=False)
    if vault_value:
        logger.debug(f"Configuración obtenida desde Vault: {vault_path}")
        return str(vault_value)
    
    # Fallback a variable de entorno
    env_value = os.getenv(env_var)
    if env_value:
        logger.info(f"Usando variable de entorno {env_var} (Vault no disponible o secreto no encontrado)")
        return env_value
    
    # Usar default
    if default is not None:
        logger.debug(f"Usando valor por defecto para {vault_path}/{env_var}")
        return default
    
    # Required pero no encontrado
    if required:
        raise ValueError(f"Configuración requerida no encontrada: Vault path '{vault_path}' o env var '{env_var}'")
    
    return None


def get_secrets_mapping() -> Dict[str, Dict[str, Any]]:
    """
    Mapeo de variables de entorno comunes a rutas de Vault.
    
    Returns:
        Dict con mapeo env_var -> {vault_path, vault_key}
    """
    return {
        "SLACK_WEBHOOK_URL": {
            "vault_path": "notifications/slack/webhook",
            "vault_key": "url"
        },
        "ALERT_EMAILS": {
            "vault_path": "notifications/email/alert-list",
            "vault_key": "emails"
        },
        "HRIS_API_TOKEN": {
            "vault_path": "integrations/hris/token",
            "vault_key": "token"
        },
        "IDP_API_TOKEN": {
            "vault_path": "integrations/idp/token",
            "vault_key": "token"
        },
        "ISSUE_TRACKER_TOKEN": {
            "vault_path": "integrations/jira/token",
            "vault_key": "token"
        },
        "HUBSPOT_TOKEN": {
            "vault_path": "crm/hubspot/token",
            "vault_key": "token"
        },
        "OPENAI_API_KEY": {
            "vault_path": "ai/openai/api_key",
            "vault_key": "key"
        },
        "STRIPE_API_KEY": {
            "vault_path": "payments/stripe/api_key",
            "vault_key": "key"
        },
    }


def migrate_env_to_vault_format(env_var: str) -> Dict[str, Any]:
    """
    Devuelve la configuración de Vault para una variable de entorno conocida.
    
    Args:
        env_var: Nombre de variable de entorno
    
    Returns:
        Dict con vault_path y vault_key, o None si no está mapeada
    """
    mapping = get_secrets_mapping()
    return mapping.get(env_var, {})


