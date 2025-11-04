"""
Integración con HashiCorp Vault para gestión de secretos en Airflow.

Este módulo proporciona funciones para acceder a secretos almacenados en Vault
desde tareas de Airflow de forma segura usando autenticación Kubernetes.

Mejoras implementadas:
- Caché de cliente Vault para reducir autenticaciones
- Retry logic con exponential backoff
- Métricas de acceso a secretos
- Fallback a variables de entorno si Vault no está disponible
"""

from __future__ import annotations

import os
import logging
import time
import threading
from typing import Dict, Any, Optional
from functools import lru_cache
import hvac
from hvac.exceptions import VaultError

logger = logging.getLogger(__name__)

# Configuración por defecto
DEFAULT_VAULT_ADDR = os.getenv("VAULT_ADDR", "http://vault.security.svc.cluster.local:8200")
DEFAULT_VAULT_ROLE = os.getenv("VAULT_K8S_ROLE", "airflow-worker")
DEFAULT_VAULT_MOUNT_PATH = os.getenv("VAULT_K8S_MOUNT_PATH", "kubernetes")
DEFAULT_SECRET_PATH = "secret/data"

# Configuración de retry
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2
CACHE_TTL_SECONDS = 300  # 5 minutos de caché para tokens

# Thread-local storage para cliente Vault
_vault_client_lock = threading.Lock()
_vault_client_cache: Optional[hvac.Client] = None
_vault_client_expiry: float = 0


def get_vault_client(force_refresh: bool = False) -> Optional[hvac.Client]:
    """
    Crea un cliente de Vault autenticado mediante Kubernetes Service Account.
    Usa caché para evitar múltiples autenticaciones.
    
    Args:
        force_refresh: Si True, fuerza una nueva autenticación incluso si hay caché
    
    Returns:
        Cliente de Vault autenticado o None si falla la autenticación
    """
    global _vault_client_cache, _vault_client_expiry
    
    with _vault_client_lock:
        # Verificar caché
        if not force_refresh and _vault_client_cache and time.time() < _vault_client_expiry:
            return _vault_client_cache
        
        try:
            client = hvac.Client(url=DEFAULT_VAULT_ADDR)
            
            # Autenticación mediante Kubernetes Service Account
            sa_token_path = "/var/run/secrets/kubernetes.io/serviceaccount/token"
            
            if not os.path.exists(sa_token_path):
                logger.warning("Service Account token no encontrado, intentando autenticación fallback")
                # En desarrollo local o fuera de Kubernetes, usar token directo
                vault_token = os.getenv("VAULT_TOKEN")
                if vault_token:
                    client.token = vault_token
                    _vault_client_cache = client
                    _vault_client_expiry = time.time() + CACHE_TTL_SECONDS
                    return client
                return None
            
            with open(sa_token_path, "r") as f:
                jwt_token = f.read().strip()
            
            # Autenticar con Vault usando el JWT del Service Account
            auth_response = client.auth.kubernetes.login(
                role=DEFAULT_VAULT_ROLE,
                jwt=jwt_token,
                mount_point=DEFAULT_VAULT_MOUNT_PATH,
            )
            
            if auth_response and "auth" in auth_response:
                client.token = auth_response["auth"]["client_token"]
                # Calcular expiración (usar TTL del token o caché por defecto)
                ttl = auth_response["auth"].get("lease_duration", CACHE_TTL_SECONDS)
                _vault_client_cache = client
                _vault_client_expiry = time.time() + min(ttl - 60, CACHE_TTL_SECONDS)  # Renovar antes de expirar
                logger.info("Autenticación con Vault exitosa")
                return client
            else:
                logger.error("Falló la autenticación con Vault")
                return None
                
        except VaultError as e:
            logger.error(f"Error de Vault: {e}")
            # Limpiar caché en caso de error
            _vault_client_cache = None
            return None
        except Exception as e:
            logger.error(f"Error inesperado al conectar con Vault: {e}")
            _vault_client_cache = None
            return None


def get_secret(
    path: str, 
    key: Optional[str] = None, 
    fallback_env: Optional[str] = None,
    required: bool = False
) -> Any:
    """
    Obtiene un secreto de Vault con retry logic y fallback a variables de entorno.
    
    Args:
        path: Ruta del secreto en Vault (ej: "crm/hubspot/token")
        key: Clave específica dentro del secreto (opcional, retorna todo si no se especifica)
        fallback_env: Nombre de variable de entorno como fallback (ej: "HUBSPOT_TOKEN")
        required: Si True, lanza excepción si no se encuentra el secreto
    
    Returns:
        Valor del secreto o dict completo si key es None
    
    Example:
        token = get_secret("crm/hubspot/token", "token", fallback_env="HUBSPOT_TOKEN")
        all_data = get_secret("crm/hubspot/token")
    """
    last_exception = None
    
    # Intentar con retry
    for attempt in range(MAX_RETRIES):
        try:
            client = get_vault_client(force_refresh=(attempt > 0))
            if not client:
                if attempt < MAX_RETRIES - 1:
                    delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                    logger.warning(f"No se pudo obtener cliente de Vault, reintentando en {delay}s (intento {attempt + 1}/{MAX_RETRIES})")
                    time.sleep(delay)
                    continue
                else:
                    logger.error("No se pudo obtener cliente de Vault después de todos los intentos")
                    break
            
            response = client.secrets.kv.v2.read_secret_version(path=path)
            
            if not response or "data" not in response:
                logger.error(f"No se encontró secreto en {path}")
                break
            
            data = response["data"]["data"]
            result = data.get(key) if key else data
            
            # Emitir métrica de éxito (si Stats está disponible)
            try:
                from airflow.stats import Stats
                Stats.incr("vault.secret.access.success", 1, tags={"path": path})
            except Exception:
                pass
            
            logger.debug(f"Secreto obtenido exitosamente: {path}")
            return result
            
        except VaultError as e:
            last_exception = e
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY_SECONDS * (2 ** attempt)
                logger.warning(f"Error al leer secreto {path}, reintentando en {delay}s: {e}")
                time.sleep(delay)
                # Forzar refresh del cliente en el siguiente intento
                get_vault_client(force_refresh=True)
            else:
                logger.error(f"Error al leer secreto {path} después de {MAX_RETRIES} intentos: {e}")
        except Exception as e:
            last_exception = e
            logger.error(f"Error inesperado al leer secreto {path}: {e}")
            break
    
    # Fallback a variable de entorno
    if fallback_env:
        env_value = os.getenv(fallback_env)
        if env_value:
            logger.info(f"Usando variable de entorno {fallback_env} como fallback para {path}")
            return env_value
    
    # Emitir métrica de error
    try:
        from airflow.stats import Stats
        Stats.incr("vault.secret.access.error", 1, tags={"path": path})
    except Exception:
        pass
    
    if required:
        error_msg = f"Secreto requerido no encontrado: {path}"
        if fallback_env:
            error_msg += f" (ni variable de entorno {fallback_env})"
        raise ValueError(error_msg)
    
    logger.warning(f"No se pudo obtener secreto {path} y no hay fallback disponible")
    return None


def get_secrets_batch(paths: Dict[str, str]) -> Dict[str, Any]:
    """
    Obtiene múltiples secretos de Vault en un solo llamado.
    
    Args:
        paths: Dict donde key es el nombre del secreto local y value es la ruta en Vault
    
    Returns:
        Dict con los secretos obtenidos
    
    Example:
        secrets = get_secrets_batch({
            "hubspot_token": "crm/hubspot/token",
            "db_url": "databases/leads/url"
        })
    """
    result = {}
    client = get_vault_client()
    
    if not client:
        logger.error("No se pudo obtener cliente de Vault")
        return result
    
    for local_key, vault_path in paths.items():
        try:
            data = get_secret(vault_path)
            if data:
                result[local_key] = data
        except Exception as e:
            logger.warning(f"No se pudo obtener secreto {vault_path}: {e}")
    
    return result


def get_connection_uri(connection_name: str) -> Optional[str]:
    """
    Obtiene una URI de conexión de Airflow desde Vault.
    
    Args:
        connection_name: Nombre de la conexión (ej: "snowflake", "databricks")
    
    Returns:
        URI de conexión en formato Airflow
    """
    path = f"airflow/connections/{connection_name}"
    return get_secret(path, "uri")


class VaultSecret:
    """
    Context manager para obtener secretos de Vault de forma segura.
    
    Example:
        with VaultSecret("crm/hubspot/token") as token:
            # usar token
    """
    
    def __init__(self, path: str, key: Optional[str] = None):
        self.path = path
        self.key = key
        self.value = None
    
    def __enter__(self):
        self.value = get_secret(self.path, self.key)
        return self.value
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Limpiar el valor de memoria (aunque Python lo hará automáticamente)
        self.value = None
        return False

