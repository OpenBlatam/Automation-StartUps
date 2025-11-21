"""
Cliente específico para Facebook Ads API.

Usa el SDK oficial facebook-business cuando está disponible,
con fallback a requests.
"""

from __future__ import annotations

import logging
import time
from typing import Any, Dict, List, Optional

from ads_reporting.base_client import (
    BaseAdsClient,
    APIConfig,
    AdsAPIError
)

logger = logging.getLogger(__name__)

try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adsinsights import AdsInsights
    from facebook_business.exceptions import FacebookRequestError
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FACEBOOK_SDK_AVAILABLE = False
    logger.warning("facebook_business SDK no disponible")


class FacebookAdsConfig(APIConfig):
    """Configuración específica para Facebook Ads."""
    ad_account_id: str = ""
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    platform: str = "facebook"
    
    def validate(self) -> None:
        """Valida configuración de Facebook Ads."""
        super().validate()
        if not self.ad_account_id:
            raise AdsAPIError("FACEBOOK_AD_ACCOUNT_ID es requerido")
        if not (self.ad_account_id.startswith("act_") or self.ad_account_id.isdigit()):
            raise AdsAPIError(
                "FACEBOOK_AD_ACCOUNT_ID debe ser 'act_XXXXX' o solo números"
            )


class FacebookAdsClient(BaseAdsClient):
    """Cliente para Facebook Ads API."""
    
    def __init__(self, config: FacebookAdsConfig):
        """Inicializa el cliente de Facebook Ads."""
        super().__init__(config)
        self.config: FacebookAdsConfig = config
        self._sdk_initialized = False
    
    def get_base_url(self) -> str:
        """Retorna la URL base de Facebook Graph API."""
        return f"https://graph.facebook.com/{self.config.api_version}"
    
    def get_default_headers(self) -> Dict[str, str]:
        """Retorna headers por defecto."""
        return {
            "Authorization": f"Bearer {self.config.access_token}",
            "Content-Type": "application/json"
        }
    
    def _init_sdk_if_available(self) -> bool:
        """
        Inicializa el SDK de Facebook si está disponible.
        
        Returns:
            True si el SDK está disponible y se inicializó, False en caso contrario
        """
        if FACEBOOK_SDK_AVAILABLE and not self._sdk_initialized:
            try:
                FacebookAdsApi.init(
                    access_token=self.config.access_token,
                    api_version=self.config.api_version
                )
                self._sdk_initialized = True
                return True
            except Exception as e:
                logger.warning(f"Error inicializando Facebook SDK: {str(e)}")
                return False
        return FACEBOOK_SDK_AVAILABLE and self._sdk_initialized
    
    def get_account(self) -> Optional[AdAccount]:
        """
        Obtiene el objeto AdAccount usando el SDK.
        
        Returns:
            AdAccount object o None si el SDK no está disponible
        """
        if not self._init_sdk_if_available():
            return None
        
        try:
            account_id = self.config.ad_account_id.replace('act_', '')
            return AdAccount(f"act_{account_id}")
        except Exception as e:
            logger.error(f"Error obteniendo cuenta de Facebook: {str(e)}")
            return None
    
    def get_insights(
        self,
        fields: List[str],
        params: Dict[str, Any],
        use_sdk: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene insights usando SDK o API REST.
        
        Args:
            fields: Lista de campos a obtener
            params: Parámetros de la query
            use_sdk: Si intentar usar SDK primero (default: True)
            
        Returns:
            Lista de insights
        """
        if use_sdk and self._init_sdk_if_available():
            return self._get_insights_sdk(fields, params)
        else:
            return self._get_insights_rest(fields, params)
    
    def _get_insights_sdk(
        self,
        fields: List[str],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Obtiene insights usando el SDK oficial."""
        account = self.get_account()
        if not account:
            return []
        
        try:
            # Convertir fields a objetos del SDK
            sdk_fields = [
                getattr(AdsInsights.Field, field) if hasattr(AdsInsights.Field, field)
                else field
                for field in fields
            ]
            
            insights = account.get_insights(fields=sdk_fields, params=params)
            results = []
            
            for insight in insights:
                # Convertir insight a diccionario
                result = {}
                for field in fields:
                    value = insight.get(field) if hasattr(insight, 'get') else getattr(insight, field, None)
                    result[field] = value
                results.append(result)
            
            return results
            
        except FacebookRequestError as e:
            logger.error(f"Error en Facebook SDK: {str(e)}")
            raise AdsAPIError(f"Facebook SDK Error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Error obteniendo insights con SDK: {str(e)}")
            raise AdsAPIError(f"Error obteniendo insights: {str(e)}") from e
    
    def _get_insights_rest(
        self,
        fields: List[str],
        params: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Obtiene insights usando la API REST."""
        account_id = self.config.ad_account_id.replace('act_', '')
        endpoint = f"/act_{account_id}/insights"
        url = f"{self.get_base_url()}{endpoint}"
        
        # Agregar fields a params
        request_params = {**params, "fields": ",".join(fields)}
        request_params["access_token"] = self.config.access_token
        
        all_results = []
        next_url = None
        page = 0
        max_pages = 100
        
        while page < max_pages:
            try:
                if next_url:
                    response = self.session.get(next_url, timeout=self.config.request_timeout)
                else:
                    response = self._execute_request_with_retry(
                        "GET", url, self.get_default_headers(), params=request_params
                    )
                
                data = response.json()
                
                if 'error' in data:
                    raise AdsAPIError(
                        f"Facebook API Error: {data['error'].get('message', 'Unknown')}",
                        status_code=data['error'].get('code'),
                        error_data=data['error']
                    )
                
                page_data = data.get("data", [])
                all_results.extend(page_data)
                
                # Paginación
                paging = data.get("paging", {})
                next_url = paging.get("next")
                
                if not next_url or not page_data:
                    break
                
                page += 1
                time.sleep(self.config.rate_limit_delay)
                
            except Exception as e:
                logger.error(f"Error en paginación: {str(e)}")
                break
        
        return all_results


