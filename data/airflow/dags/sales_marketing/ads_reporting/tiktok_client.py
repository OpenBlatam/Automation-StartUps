"""
Cliente específico para TikTok Ads API.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from ads_reporting.base_client import (
    BaseAdsClient,
    APIConfig,
    AdsAPIError
)

logger = logging.getLogger(__name__)


class TikTokAdsConfig(APIConfig):
    """Configuración específica para TikTok Ads."""
    advertiser_id: str = ""
    app_id: Optional[str] = None
    secret: Optional[str] = None
    platform: str = "tiktok"
    
    def validate(self) -> None:
        """Valida configuración de TikTok Ads."""
        super().validate()
        if not self.advertiser_id:
            raise AdsAPIError("TIKTOK_ADVERTISER_ID es requerido")


class TikTokAdsClient(BaseAdsClient):
    """Cliente para TikTok Ads API."""
    
    def __init__(self, config: TikTokAdsConfig):
        """Inicializa el cliente de TikTok Ads."""
        super().__init__(config)
        self.config: TikTokAdsConfig = config
    
    def get_base_url(self) -> str:
        """Retorna la URL base de TikTok Business API."""
        return f"https://business-api.tiktok.com/open_api/{self.config.api_version}"
    
    def get_default_headers(self) -> Dict[str, str]:
        """Retorna headers por defecto."""
        return {
            "Access-Token": self.config.access_token,
            "Content-Type": "application/json"
        }
    
    def get_report(
        self,
        dimensions: List[str],
        metrics: List[str],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Obtiene un reporte de TikTok Ads.
        
        Args:
            dimensions: Lista de dimensiones
            metrics: Lista de métricas
            params: Parámetros adicionales
            
        Returns:
            Respuesta del reporte
        """
        endpoint = "/report/integrated/get/"
        url = f"{self.get_base_url()}{endpoint}"
        
        payload = {
            "advertiser_id": self.config.advertiser_id,
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "dimensions": dimensions,
            "metrics": metrics,
            **params
        }
        
        response = self._execute_request_with_retry(
            "POST", url, self.get_default_headers(), json_data=payload
        )
        
        return response.json()


