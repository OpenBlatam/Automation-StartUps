"""
Cliente específico para Google Ads API.

Usa el SDK oficial google-ads cuando está disponible.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

from ads_reporting.base_client import (
    BaseAdsClient,
    APIConfig,
    AdsAPIError
)

logger = logging.getLogger(__name__)

try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    GOOGLE_ADS_SDK_AVAILABLE = True
except ImportError:
    GOOGLE_ADS_SDK_AVAILABLE = False
    logger.warning("google-ads SDK no disponible")


class GoogleAdsConfig(APIConfig):
    """Configuración específica para Google Ads."""
    customer_id: str = ""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    developer_token: str = ""
    yaml_config_path: Optional[str] = None
    platform: str = "google"
    
    def validate(self) -> None:
        """Valida configuración de Google Ads."""
        if not self.customer_id:
            raise AdsAPIError("GOOGLE_ADS_CUSTOMER_ID es requerido")
        if not self.developer_token:
            raise AdsAPIError("GOOGLE_ADS_DEVELOPER_TOKEN es requerido")
        # Para OAuth2, necesitamos client_id, client_secret y refresh_token
        # O un archivo YAML de configuración
        if not self.yaml_config_path:
            if not all([self.client_id, self.client_secret, self.refresh_token]):
                raise AdsAPIError(
                    "GOOGLE_ADS requiere YAML config o "
                    "(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)"
                )


class GoogleAdsClient(BaseAdsClient):
    """Cliente para Google Ads API."""
    
    def __init__(self, config: GoogleAdsConfig):
        """Inicializa el cliente de Google Ads."""
        super().__init__(config)
        self.config: GoogleAdsConfig = config
        self._google_client: Optional[GoogleAdsClient] = None
    
    def get_base_url(self) -> str:
        """Retorna la URL base (no se usa con SDK)."""
        return "https://googleads.googleapis.com"
    
    def get_default_headers(self) -> Dict[str, str]:
        """Retorna headers por defecto (no se usa con SDK)."""
        return {}
    
    def _get_sdk_client(self) -> Optional[GoogleAdsClient]:
        """Obtiene el cliente SDK de Google Ads."""
        if not GOOGLE_ADS_SDK_AVAILABLE:
            return None
        
        if self._google_client is None:
            try:
                # Intentar cargar desde YAML
                if self.config.yaml_config_path and os.path.exists(self.config.yaml_config_path):
                    self._google_client = GoogleAdsClient.load_from_storage(
                        self.config.yaml_config_path
                    )
                else:
                    # Crear desde credenciales
                    credentials = {
                        "developer_token": self.config.developer_token,
                        "client_id": self.config.client_id,
                        "client_secret": self.config.client_secret,
                        "refresh_token": self.config.refresh_token,
                        "use_proto_plus": True
                    }
                    self._google_client = GoogleAdsClient.load_from_dict(credentials)
            except Exception as e:
                logger.error(f"Error creando cliente de Google Ads: {str(e)}")
                return None
        
        return self._google_client
    
    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Ejecuta una query GAQL usando el SDK.
        
        Args:
            query: Query GAQL (Google Ads Query Language)
            
        Returns:
            Lista de resultados como diccionarios
        """
        client = self._get_sdk_client()
        if not client:
            raise AdsAPIError("Google Ads SDK no disponible")
        
        try:
            ga_service = client.get_service("GoogleAdsService")
            customer_id = self.config.customer_id.replace("-", "")
            
            response = ga_service.search(customer_id=customer_id, query=query)
            
            results = []
            for row in response:
                # Convertir row a diccionario básico
                result = {}
                # Nota: La conversión completa depende de la estructura del query
                # Esto es un placeholder - debería expandirse según necesidades
                results.append(result)
            
            return results
            
        except GoogleAdsException as e:
            logger.error(f"Error en Google Ads SDK: {str(e)}")
            raise AdsAPIError(f"Google Ads SDK Error: {str(e)}")
        except Exception as e:
            logger.error(f"Error ejecutando query: {str(e)}")
            raise AdsAPIError(f"Error ejecutando query: {str(e)}")

