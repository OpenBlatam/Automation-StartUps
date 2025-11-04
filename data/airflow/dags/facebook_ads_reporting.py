"""
Módulo para extraer datos de rendimiento de Facebook Ads.

Funcionalidades:
1. Extracción de datos de rendimiento (impresiones, clics, CTR, CPC, conversiones, ROAS)
2. Comparación de CPA y valor por conversión entre audiencias
3. Análisis de remarketing (frecuencia, CPM, tasa de conversión)
4. Análisis histórico de creatividades (conversiones y coste incremental)

Variables de entorno requeridas:
- FACEBOOK_ACCESS_TOKEN: Token de acceso de Facebook Marketing API
- FACEBOOK_APP_ID: ID de la aplicación de Facebook
- FACEBOOK_APP_SECRET: Secret de la aplicación de Facebook
- FACEBOOK_AD_ACCOUNT_ID: ID de la cuenta de anuncios

Variables de entorno opcionales:
- FACEBOOK_API_VERSION: Versión de la API (default: v18.0)
- FACEBOOK_REPORT_DESTINATION: Destino para guardar reportes (s3 | postgres | local)
"""

from __future__ import annotations

import os
import json
import logging
import time
import hashlib
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from decimal import Decimal
from contextlib import contextmanager

import pendulum
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# Intentar importar librerías opcionales
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.adsinsights import AdsInsights
    from facebook_business.exceptions import FacebookRequestError
    FACEBOOK_SDK_AVAILABLE = True
except ImportError:
    FACEBOOK_SDK_AVAILABLE = False
    logger.warning("facebook_business SDK no disponible, usando requests directo")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log,
        after_log,
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    from circuitbreaker import circuit
    CIRCUITBREAKER_AVAILABLE = True
except ImportError:
    CIRCUITBREAKER_AVAILABLE = False

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

# Constantes de configuración
FACEBOOK_MAX_RETRIES = int(os.environ.get("FACEBOOK_MAX_RETRIES", "3"))
FACEBOOK_RETRY_BACKOFF = float(os.environ.get("FACEBOOK_RETRY_BACKOFF", "1.0"))
FACEBOOK_RATE_LIMIT_DELAY = float(os.environ.get("FACEBOOK_RATE_LIMIT_DELAY", "0.5"))
FACEBOOK_REQUEST_TIMEOUT = int(os.environ.get("FACEBOOK_REQUEST_TIMEOUT", "30"))
FACEBOOK_MAX_PAGES = int(os.environ.get("FACEBOOK_MAX_PAGES", "100"))


# Excepciones personalizadas
class FacebookAdsError(Exception):
    """Excepción base para errores de Facebook Ads."""
    pass


class FacebookAdsAuthError(FacebookAdsError):
    """Error de autenticación con Facebook Ads."""
    pass


class FacebookAdsAPIError(FacebookAdsError):
    """Error en la respuesta de la API de Facebook Ads."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class FacebookAdsRateLimitError(FacebookAdsError):
    """Error de rate limiting de Facebook Ads."""
    pass


@dataclass
class FacebookAdsConfig:
    """Configuración para Facebook Ads API."""
    access_token: str
    app_id: Optional[str] = None
    app_secret: Optional[str] = None
    ad_account_id: str = ""
    api_version: str = "v18.0"
    report_destination: str = "postgres"
    postgres_conn_id: str = "postgres_default"
    
    def validate(self) -> None:
        """Valida que la configuración sea correcta."""
        if not self.access_token:
            raise FacebookAdsAuthError("FACEBOOK_ACCESS_TOKEN es requerido")
        if not self.ad_account_id:
            raise FacebookAdsAuthError("FACEBOOK_AD_ACCOUNT_ID es requerido")
        if not self.ad_account_id.startswith("act_") and not self.ad_account_id.isdigit():
            raise FacebookAdsAuthError("FACEBOOK_AD_ACCOUNT_ID debe ser 'act_XXXXX' o solo números")


@dataclass
class CampaignPerformanceData:
    """Datos de rendimiento de campaña."""
    date_start: str
    date_stop: str
    campaign_id: str
    campaign_name: str
    adset_id: str
    adset_name: str
    ad_id: str
    ad_name: str
    impressions: int
    clicks: int
    ctr: float
    cpc: float
    conversions: float
    roas: float
    spend: float
    audience_type: Optional[str] = None
    geographic_location: Optional[str] = None


def _load_facebook_config() -> FacebookAdsConfig:
    """Carga y valida configuración desde variables de entorno."""
    config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        app_id=os.environ.get("FACEBOOK_APP_ID"),
        app_secret=os.environ.get("FACEBOOK_APP_SECRET"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
        api_version=os.environ.get("FACEBOOK_API_VERSION", "v18.0"),
        report_destination=os.environ.get("FACEBOOK_REPORT_DESTINATION", "postgres"),
        postgres_conn_id=os.environ.get("POSTGRES_CONN_ID", "postgres_default")
    )
    
    try:
        config.validate()
    except FacebookAdsAuthError as e:
        logger.error(f"Error de validación de configuración: {str(e)}")
        raise
    
    return config


@contextmanager
def _track_metric(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager para trackear métricas."""
    start_time = time.time()
    if STATS_AVAILABLE:
        try:
            stats = Stats()
            stats.incr(f"facebook_ads.{metric_name}.start", tags=tags or {})
        except Exception:
            pass
    
    try:
        yield
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                duration_ms = (time.time() - start_time) * 1000
                stats.incr(f"facebook_ads.{metric_name}.success", tags=tags or {})
                stats.timing(f"facebook_ads.{metric_name}.duration_ms", int(duration_ms), tags=tags or {})
            except Exception:
                pass
    except Exception as e:
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.incr(f"facebook_ads.{metric_name}.error", tags={**(tags or {}), "error_type": type(e).__name__})
            except Exception:
                pass
        raise


def _create_facebook_session() -> requests.Session:
    """Crea una sesión HTTP con retry strategy para Facebook API."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=FACEBOOK_MAX_RETRIES,
        backoff_factor=FACEBOOK_RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["GET", "POST"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def _make_facebook_api_request(
    access_token: str,
    endpoint: str,
    params: Dict[str, Any],
    api_version: str = "v18.0",
    session: Optional[requests.Session] = None
) -> Dict[str, Any]:
    """
    Realiza una petición a la Facebook Marketing API usando requests con retry logic.
    
    Args:
        access_token: Token de acceso de Facebook
        endpoint: Endpoint de la API (ej: "/act_{account_id}/insights")
        params: Parámetros de la petición
        api_version: Versión de la API
        session: Sesión HTTP reutilizable (opcional)
        
    Returns:
        Respuesta JSON parseada
        
    Raises:
        FacebookAdsAPIError: Si hay error en la petición
        FacebookAdsRateLimitError: Si hay rate limiting
    """
    base_url = f"https://graph.facebook.com/{api_version}"
    url = f"{base_url}{endpoint}"
    
    params["access_token"] = access_token
    
    if session is None:
        session = _create_facebook_session()
    
    def _execute_request():
        response = session.get(url, params=params, timeout=FACEBOOK_REQUEST_TIMEOUT)
        
        # Manejar rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', FACEBOOK_RATE_LIMIT_DELAY))
            logger.warning(f"Rate limit alcanzado, esperando {retry_after}s")
            time.sleep(min(retry_after, 300))  # Máximo 5 minutos
            raise FacebookAdsRateLimitError(f"Rate limit: {response.text}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # Verificar errores en la respuesta de Facebook
        if 'error' in data:
            error = data['error']
            error_code = error.get('code', 0)
            error_msg = error.get('message', 'Unknown error')
            raise FacebookAdsAPIError(
                f"Facebook API Error: {error_msg}",
                status_code=error_code,
                error_data=error
            )
        
        return data
    
    # Usar tenacity para retry si está disponible
    if TENACITY_AVAILABLE:
        @retry(
            stop=stop_after_attempt(FACEBOOK_MAX_RETRIES + 1),
            wait=wait_exponential(multiplier=FACEBOOK_RETRY_BACKOFF, min=1, max=10),
            retry=retry_if_exception_type((
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                FacebookAdsRateLimitError
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING),
            after=after_log(logger, logging.INFO),
            reraise=True
        )
        def _retry_request():
            return _execute_request()
        
        try:
            return _retry_request()
        except Exception as e:
            if isinstance(e, (FacebookAdsAPIError, FacebookAdsAuthError)):
                raise
            raise FacebookAdsAPIError(f"Error en petición a Facebook API: {str(e)}")
    else:
        try:
            return _execute_request()
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429:
                raise FacebookAdsRateLimitError(f"Rate limit: {str(e)}")
            raise FacebookAdsAPIError(f"HTTP Error: {str(e)}", status_code=getattr(e.response, 'status_code', None))
        except requests.exceptions.RequestException as e:
            raise FacebookAdsAPIError(f"Request Error: {str(e)}")


def extract_campaign_performance_data(
    access_token: str,
    ad_account_id: str,
    date_start: str,
    date_stop: str,
    api_version: str = "v18.0"
) -> List[CampaignPerformanceData]:
    """
    Extrae datos de rendimiento de campañas de Facebook.
    Usa el SDK oficial facebook-business si está disponible, sino usa requests.
    
    Args:
        access_token: Token de acceso de Facebook
        ad_account_id: ID de la cuenta de anuncios (ej: "act_123456789")
        date_start: Fecha inicio (YYYY-MM-DD)
        date_stop: Fecha fin (YYYY-MM-DD)
        api_version: Versión de la API
        
    Returns:
        Lista de datos de rendimiento
        
    Raises:
        FacebookAdsAPIError: Si hay error en la API
        FacebookAdsAuthError: Si hay error de autenticación
    """
    results = []
    
    with _track_metric("extract_campaign_performance", tags={"api_version": api_version}):
        # Intentar usar SDK oficial primero
        if FACEBOOK_SDK_AVAILABLE:
            try:
                FacebookAdsApi.init(access_token=access_token, api_version=api_version)
            account = AdAccount(f"act_{ad_account_id.replace('act_', '')}")
            
            # Campos a extraer usando el SDK
            fields = [
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.campaign_name,
                AdsInsights.Field.adset_id,
                AdsInsights.Field.adset_name,
                AdsInsights.Field.ad_id,
                AdsInsights.Field.ad_name,
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.actions,
                AdsInsights.Field.spend,
                AdsInsights.Field.action_values,
            ]
            
            params = {
                'time_range': {
                    'since': date_start,
                    'until': date_stop
                },
                'breakdowns': [AdsInsights.Breakdowns.audience_type, AdsInsights.Breakdowns.region],
                'level': AdsInsights.Level.ad,
                'limit': 1000
            }
            
            insights = account.get_insights(fields=fields, params=params)
            
            for insight in insights:
                try:
                    impressions = int(insight.get(AdsInsights.Field.impressions, 0) or 0)
                    clicks = int(insight.get(AdsInsights.Field.clicks, 0) or 0)
                    ctr = float(insight.get(AdsInsights.Field.ctr, 0) or 0)
                    cpc = float(insight.get(AdsInsights.Field.cpc, 0) or 0)
                    spend = float(insight.get(AdsInsights.Field.spend, 0) or 0)
                    
                    # Procesar acciones (conversiones)
                    actions = insight.get(AdsInsights.Field.actions, [])
                    conversions = 0.0
                    for action in actions or []:
                        if isinstance(action, dict) and action.get('action_type') in ['purchase', 'complete_registration', 'lead']:
                            conversions += float(action.get('value', 0) or 0)
                    
                    # Calcular ROAS
                    action_values = insight.get(AdsInsights.Field.action_values, [])
                    revenue = sum(
                        float(av.get('value', 0) or 0) 
                        for av in (action_values or [])
                        if isinstance(av, dict) and av.get('action_type') == 'purchase'
                    )
                    roas = (revenue / spend) if spend > 0 else 0.0
                    
                    performance = CampaignPerformanceData(
                        date_start=date_start,
                        date_stop=date_stop,
                        campaign_id=str(insight.get(AdsInsights.Field.campaign_id, "") or ""),
                        campaign_name=str(insight.get(AdsInsights.Field.campaign_name, "") or ""),
                        adset_id=str(insight.get(AdsInsights.Field.adset_id, "") or ""),
                        adset_name=str(insight.get(AdsInsights.Field.adset_name, "") or ""),
                        ad_id=str(insight.get(AdsInsights.Field.ad_id, "") or ""),
                        ad_name=str(insight.get(AdsInsights.Field.ad_name, "") or ""),
                        impressions=impressions,
                        clicks=clicks,
                        ctr=ctr,
                        cpc=cpc,
                        conversions=conversions,
                        roas=roas,
                        spend=spend,
                        audience_type=insight.get('audience_type'),
                        geographic_location=insight.get('region')
                    )
                    results.append(performance)
                except Exception as e:
                    logger.warning(f"Error procesando insight con SDK: {str(e)}")
                    continue
            
            logger.info(f"Extraídos {len(results)} registros usando Facebook SDK oficial")
            return results
            
        except Exception as e:
            logger.warning(f"Error usando Facebook SDK, usando método alternativo: {str(e)}")
            # Continuar con método alternativo
    
    # Método alternativo usando requests (fallback)
    # Campos a extraer
    fields = [
        "campaign_id", "campaign_name",
        "adset_id", "adset_name",
        "ad_id", "ad_name",
        "impressions", "clicks",
        "ctr", "cpc",
        "actions", "spend",
        "action_values"
    ]
    
    # Break down por audiencia y ubicación
    breakdowns = ["audience_type", "region"]
    
    params = {
        "fields": ",".join(fields),
        "time_range": json.dumps({
            "since": date_start,
            "until": date_stop
        }),
        "breakdowns": json.dumps(breakdowns),
        "level": "ad",
        "limit": 1000
    }
    
    endpoint = f"/act_{ad_account_id.replace('act_', '')}/insights"
    
    try:
        all_data = []
        next_url = None
        page = 0
        
        # Usar sesión reutilizable para mejor rendimiento
        session = _create_facebook_session()
        
        while page < FACEBOOK_MAX_PAGES:
            if next_url:
                # Seguir paginación usando la URL completa
                response = session.get(next_url, timeout=FACEBOOK_REQUEST_TIMEOUT)
                response.raise_for_status()
                response_data = response.json()
                
                # Verificar errores de Facebook
                if 'error' in response_data:
                    error = response_data['error']
                    raise FacebookAdsAPIError(
                        f"Facebook API Error: {error.get('message', 'Unknown')}",
                        status_code=error.get('code'),
                        error_data=error
                    )
            else:
                # Primera página
                response_data = _make_facebook_api_request(
                    access_token, endpoint, params, api_version, session=session
                )
            
            # Agregar datos de esta página
            page_data = response_data.get("data", [])
            all_data.extend(page_data)
            
            # Manejar paginación
            paging = response_data.get("paging", {})
            next_url = paging.get("next")
            
            if not next_url or not page_data:
                break
            
            page += 1
            time.sleep(0.5)  # Pequeño delay para evitar rate limiting
        
        # Procesar todos los datos después de obtener todas las páginas
        for item in all_data:
                try:
                    # Calcular CTR
                    impressions = int(item.get("impressions", 0))
                    clicks = int(item.get("clicks", 0))
                    ctr = (clicks / impressions * 100) if impressions > 0 else 0.0
                    
                    # Obtener CPC
                    cpc = float(item.get("cpc", 0))
                    
                    # Obtener conversiones
                    actions = item.get("actions", [])
                    conversions = 0.0
                    for action in actions:
                        if action.get("action_type") in ["purchase", "complete_registration", "lead"]:
                            conversions += float(action.get("value", 0))
                    
                    # Calcular ROAS
                    spend = float(item.get("spend", 0))
                    action_values = item.get("action_values", [])
                    revenue = sum(float(av.get("value", 0)) for av in action_values if av.get("action_type") == "purchase")
                    roas = (revenue / spend) if spend > 0 else 0.0
                    
                    performance = CampaignPerformanceData(
                        date_start=date_start,
                        date_stop=date_stop,
                        campaign_id=item.get("campaign_id", ""),
                        campaign_name=item.get("campaign_name", ""),
                        adset_id=item.get("adset_id", ""),
                        adset_name=item.get("adset_name", ""),
                        ad_id=item.get("ad_id", ""),
                        ad_name=item.get("ad_name", ""),
                        impressions=impressions,
                        clicks=clicks,
                        ctr=ctr,
                        cpc=cpc,
                        conversions=conversions,
                        roas=roas,
                        spend=spend,
                        audience_type=item.get("audience_type"),
                        geographic_location=item.get("region")
                    )
                    results.append(performance)
                except Exception as e:
                    logger.warning(f"Error procesando item: {str(e)}")
                    continue
        
        logger.info(f"Extraídos {len(results)} registros de rendimiento")
        return results
        
    except Exception as e:
        logger.error(f"Error extrayendo datos de rendimiento: {str(e)}")
        raise


def extract_audience_performance_comparison(
    access_token: str,
    ad_account_id: str,
    days_back: int = 30,
    api_version: str = "v18.0"
) -> Dict[str, Any]:
    """
    Genera reporte comparativo de CPA y valor por conversión entre audiencias.
    Usa el SDK oficial facebook-business si está disponible.
    
    Args:
        access_token: Token de acceso
        ad_account_id: ID de cuenta de anuncios
        days_back: Días hacia atrás para el análisis (default: 30)
        api_version: Versión de la API
        
    Returns:
        Diccionario con comparación de audiencias
    """
    date_stop = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    
    params = {
        "fields": "campaign_id,adset_id,actions,action_values,spend",
        "time_range": json.dumps({
            "since": date_start,
            "until": date_stop
        }),
        "breakdowns": json.dumps(["audience_type"]),
        "level": "adset",
        "limit": 1000
    }
    
    endpoint = f"/act_{ad_account_id.replace('act_', '')}/insights"
    
    try:
        response_data = _make_facebook_api_request(
            access_token, endpoint, params, api_version
        )
        
        data = response_data.get("data", [])
        
        # Agrupar por tipo de audiencia
        audience_stats = {}
        total_spend = 0
        total_conversions = 0
        total_revenue = 0
        
        for item in data:
            audience_type = item.get("audience_type", "unknown")
            spend = float(item.get("spend", 0))
            total_spend += spend
            
            actions = item.get("actions", [])
            conversions = 0.0
            for action in actions:
                if action.get("action_type") in ["purchase", "complete_registration", "lead"]:
                    conversions += float(action.get("value", 0))
            
            action_values = item.get("action_values", [])
            revenue = sum(float(av.get("value", 0)) for av in action_values if av.get("action_type") == "purchase")
            
            total_conversions += conversions
            total_revenue += revenue
            
            if audience_type not in audience_stats:
                audience_stats[audience_type] = {
                    "spend": 0,
                    "conversions": 0,
                    "revenue": 0
                }
            
            audience_stats[audience_type]["spend"] += spend
            audience_stats[audience_type]["conversions"] += conversions
            audience_stats[audience_type]["revenue"] += revenue
        
        # Calcular métricas por audiencia
        avg_cpa = (total_spend / total_conversions) if total_conversions > 0 else 0
        avg_conversion_value = (total_revenue / total_conversions) if total_conversions > 0 else 0
        
        audience_comparison = []
        for audience_type, stats in audience_stats.items():
            conversions = stats["conversions"]
            spend = stats["spend"]
            revenue = stats["revenue"]
            
            cpa = (spend / conversions) if conversions > 0 else 0
            conversion_value = (revenue / conversions) if conversions > 0 else 0
            
            performance_vs_avg = {
                "cpa_vs_avg": ((cpa - avg_cpa) / avg_cpa * 100) if avg_cpa > 0 else 0,
                "value_vs_avg": ((conversion_value - avg_conversion_value) / avg_conversion_value * 100) if avg_conversion_value > 0 else 0
            }
            
            is_significantly_worse = (
                cpa > avg_cpa * 1.5 or  # CPA 50% más alto que promedio
                conversion_value < avg_conversion_value * 0.75  # Valor 25% menor que promedio
            )
            
            audience_comparison.append({
                "audience_type": audience_type,
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "cpa": cpa,
                "conversion_value": conversion_value,
                "performance_vs_avg": performance_vs_avg,
                "is_significantly_worse": is_significantly_worse
            })
        
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "average_cpa": avg_cpa,
            "average_conversion_value": avg_conversion_value,
            "audiences": audience_comparison,
            "underperforming_audiences": [
                a for a in audience_comparison if a["is_significantly_worse"]
            ]
        }
        
    except Exception as e:
        logger.error(f"Error en comparación de audiencias: {str(e)}")
        raise


def extract_remarketing_performance(
    access_token: str,
    ad_account_id: str,
    date_start: str,
    date_stop: str,
    api_version: str = "v18.0"
) -> List[Dict[str, Any]]:
    """
    Extrae datos de frecuencia, CPM y tasa de conversión para campañas de remarketing.
    
    Args:
        access_token: Token de acceso
        ad_account_id: ID de cuenta de anuncios
        date_start: Fecha inicio
        date_stop: Fecha fin
        api_version: Versión de la API
        
    Returns:
        Lista de datos de remarketing
    """
    params = {
        "fields": "campaign_id,adset_id,frequency,cpm,actions,spend,device_platform,day_of_week",
        "time_range": json.dumps({
            "since": date_start,
            "until": date_stop
        }),
        "breakdowns": json.dumps(["device_platform", "day_of_week"]),
        "level": "adset",
        "filtering": json.dumps([{
            "field": "objective",
            "operator": "IN",
            "value": ["RETARGETING", "CONVERSIONS"]
        }]),
        "limit": 1000
    }
    
    endpoint = f"/act_{ad_account_id.replace('act_', '')}/insights"
    
    try:
        response_data = _make_facebook_api_request(
            access_token, endpoint, params, api_version
        )
        
        data = response_data.get("data", [])
        results = []
        
        for item in data:
            frequency = float(item.get("frequency", 0))
            cpm = float(item.get("cpm", 0))
            spend = float(item.get("spend", 0))
            
            actions = item.get("actions", [])
            conversions = 0.0
            for action in actions:
                if action.get("action_type") in ["purchase", "complete_registration", "lead"]:
                    conversions += float(action.get("value", 0))
            
            conversion_rate = (conversions / (spend / cpm * 1000)) if cpm > 0 else 0  # Conversiones por mil impresiones
            
            results.append({
                "campaign_id": item.get("campaign_id"),
                "adset_id": item.get("adset_id"),
                "device": item.get("device_platform", "unknown"),
                "day_of_week": item.get("day_of_week", "unknown"),
                "frequency": frequency,
                "cpm": cpm,
                "conversions": conversions,
                "conversion_rate": conversion_rate,
                "spend": spend
            })
        
        logger.info(f"Extraídos {len(results)} registros de remarketing")
        return results
        
    except Exception as e:
        logger.error(f"Error extrayendo datos de remarketing: {str(e)}")
        raise


def extract_creative_performance_historical(
    access_token: str,
    ad_account_id: str,
    months_back: int = 3,
    api_version: str = "v18.0"
) -> Dict[str, Any]:
    """
    Extrae análisis histórico de creatividades.
    
    Args:
        access_token: Token de acceso
        ad_account_id: ID de cuenta de anuncios
        months_back: Meses hacia atrás (default: 3)
        api_version: Versión de la API
        
    Returns:
        Diccionario con análisis de creatividades
    """
    date_stop = datetime.now().strftime("%Y-%m-%d")
    date_start = (datetime.now() - timedelta(days=months_back * 30)).strftime("%Y-%m-%d")
    
    params = {
        "fields": "ad_id,ad_name,adset_id,campaign_id,actions,action_values,spend,creative_id",
        "time_range": json.dumps({
            "since": date_start,
            "until": date_stop
        }),
        "level": "ad",
        "limit": 1000
    }
    
    endpoint = f"/act_{ad_account_id.replace('act_', '')}/insights"
    
    try:
        response_data = _make_facebook_api_request(
            access_token, endpoint, params, api_version
        )
        
        data = response_data.get("data", [])
        
        # Agrupar por creatividad
        creative_stats = {}
        
        for item in data:
            creative_id = item.get("creative_id") or item.get("ad_id")
            spend = float(item.get("spend", 0))
            
            actions = item.get("actions", [])
            conversions = 0.0
            for action in actions:
                if action.get("action_type") in ["purchase", "complete_registration", "lead"]:
                    conversions += float(action.get("value", 0))
            
            action_values = item.get("action_values", [])
            revenue = sum(float(av.get("value", 0)) for av in action_values if av.get("action_type") == "purchase")
            
            if creative_id not in creative_stats:
                creative_stats[creative_id] = {
                    "creative_id": creative_id,
                    "ad_name": item.get("ad_name", ""),
                    "total_spend": 0,
                    "total_conversions": 0,
                    "total_revenue": 0,
                    "ads": []
                }
            
            creative_stats[creative_id]["total_spend"] += spend
            creative_stats[creative_id]["total_conversions"] += conversions
            creative_stats[creative_id]["total_revenue"] += revenue
            creative_stats[creative_id]["ads"].append(item.get("ad_id"))
        
        # Calcular métricas por creatividad
        creatives_analysis = []
        for creative_id, stats in creative_stats.items():
            spend = stats["total_spend"]
            conversions = stats["total_conversions"]
            revenue = stats["total_revenue"]
            
            conversion_rate = (conversions / (spend / 100)) if spend > 0 else 0  # Conversiones por $100 gastado
            roas = (revenue / spend) if spend > 0 else 0
            cost_per_conversion = (spend / conversions) if conversions > 0 else 0
            
            creatives_analysis.append({
                "creative_id": creative_id,
                "ad_name": stats["ad_name"],
                "spend": spend,
                "conversions": conversions,
                "revenue": revenue,
                "conversion_rate": conversion_rate,
                "roas": roas,
                "cost_per_conversion": cost_per_conversion,
                "num_ads": len(stats["ads"])
            })
        
        # Ordenar por tasa de conversión
        creatives_analysis.sort(key=lambda x: x["conversion_rate"], reverse=True)
        
        # Calcular coste incremental (promedio de los mejores vs promedio general)
        if len(creatives_analysis) > 0:
            top_10_percent = max(1, len(creatives_analysis) // 10)
            top_creatives = creatives_analysis[:top_10_percent]
            avg_top_cpc = sum(c["cost_per_conversion"] for c in top_creatives) / len(top_creatives)
            avg_all_cpc = sum(c["cost_per_conversion"] for c in creatives_analysis if c["conversions"] > 0) / max(1, sum(1 for c in creatives_analysis if c["conversions"] > 0))
            incremental_cost = avg_top_cpc - avg_all_cpc
        else:
            incremental_cost = 0
        
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "total_creatives": len(creatives_analysis),
            "creatives": creatives_analysis,
            "top_performers": creatives_analysis[:10],
            "incremental_cost_vs_average": incremental_cost
        }
        
    except Exception as e:
        logger.error(f"Error extrayendo análisis de creatividades: {str(e)}")
        raise


@dag(
    dag_id="facebook_ads_reporting",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 6 * * *",  # Diario a las 6 AM
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    doc_md="""
    ### Facebook Ads Reporting
    
    Extrae y analiza datos de rendimiento de campañas de Facebook Ads.
    
    **Funcionalidades:**
    1. Extracción de datos de rendimiento segmentado por adset, audiencia y ubicación
    2. Comparación de CPA y valor por conversión entre audiencias
    3. Análisis de remarketing por dispositivo y día de semana
    4. Análisis histórico de creatividades
    
    **Parámetros:**
    - `date_start`: Fecha inicio (YYYY-MM-DD)
    - `date_stop`: Fecha fin (YYYY-MM-DD)
    - `extract_performance`: Extraer datos de rendimiento (default: true)
    - `compare_audiences`: Comparar audiencias (default: true)
    - `analyze_remarketing`: Analizar remarketing (default: true)
    - `analyze_creatives`: Analizar creatividades (default: true)
    - `audience_comparison_days`: Días para comparación de audiencias (default: 30)
    - `creative_analysis_months`: Meses para análisis de creatividades (default: 3)
    """,
    params={
        "date_start": Param("", type="string"),
        "date_stop": Param("", type="string"),
        "extract_performance": Param(True, type="boolean"),
        "compare_audiences": Param(True, type="boolean"),
        "analyze_remarketing": Param(True, type="boolean"),
        "analyze_creatives": Param(True, type="boolean"),
        "audience_comparison_days": Param(30, type="integer", minimum=1, maximum=365),
        "creative_analysis_months": Param(3, type="integer", minimum=1, maximum=12),
    },
    tags=["marketing", "facebook-ads", "reporting"],
)
def facebook_ads_reporting():
    """DAG principal para reporting de Facebook Ads."""
    
    config = _load_facebook_config()
    
    @task(task_id="extract_campaign_performance")
    def extract_campaign_performance(**context):
        """Extrae datos de rendimiento de campañas."""
        params = context.get("params", {})
        
        if not params.get("extract_performance", True):
            logger.info("Extracción de rendimiento deshabilitada")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Extrayendo datos de rendimiento desde {date_start} hasta {date_stop}")
        
        performance_data = extract_campaign_performance_data(
            access_token=config.access_token,
            ad_account_id=config.ad_account_id,
            date_start=date_start,
            date_stop=date_stop,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            # Crear tabla si no existe
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS facebook_ads_performance (
                date_start DATE,
                date_stop DATE,
                campaign_id VARCHAR(255),
                campaign_name TEXT,
                adset_id VARCHAR(255),
                adset_name TEXT,
                ad_id VARCHAR(255),
                ad_name TEXT,
                impressions INTEGER,
                clicks INTEGER,
                ctr DECIMAL(10, 4),
                cpc DECIMAL(10, 4),
                conversions DECIMAL(10, 2),
                roas DECIMAL(10, 4),
                spend DECIMAL(10, 2),
                audience_type VARCHAR(100),
                geographic_location VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_fb_perf_date ON facebook_ads_performance(date_start, date_stop);
            CREATE INDEX IF NOT EXISTS idx_fb_perf_campaign ON facebook_ads_performance(campaign_id);
            """
            hook.run(create_table_sql)
            
            # Insertar datos
            for perf in performance_data:
                insert_sql = """
                INSERT INTO facebook_ads_performance 
                (date_start, date_stop, campaign_id, campaign_name, adset_id, adset_name,
                 ad_id, ad_name, impressions, clicks, ctr, cpc, conversions, roas, spend,
                 audience_type, geographic_location)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    perf.date_start, perf.date_stop, perf.campaign_id, perf.campaign_name,
                    perf.adset_id, perf.adset_name, perf.ad_id, perf.ad_name,
                    perf.impressions, perf.clicks, perf.ctr, perf.cpc, perf.conversions,
                    perf.roas, perf.spend, perf.audience_type, perf.geographic_location
                ))
        
        logger.info(f"Extraídos {len(performance_data)} registros de rendimiento")
        return {"records_extracted": len(performance_data)}
    
    @task(task_id="compare_audience_performance")
    def compare_audience_performance(**context):
        """Compara rendimiento entre audiencias."""
        params = context.get("params", {})
        
        if not params.get("compare_audiences", True):
            logger.info("Comparación de audiencias deshabilitada")
            return {"skipped": True}
        
        days_back = params.get("audience_comparison_days", 30)
        
        logger.info(f"Comparando audiencias para últimos {days_back} días")
        
        comparison = extract_audience_performance_comparison(
            access_token=config.access_token,
            ad_account_id=config.ad_account_id,
            days_back=days_back,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS facebook_ads_audience_comparison (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                audience_type VARCHAR(100),
                spend DECIMAL(10, 2),
                conversions DECIMAL(10, 2),
                revenue DECIMAL(10, 2),
                cpa DECIMAL(10, 2),
                conversion_value DECIMAL(10, 2),
                cpa_vs_avg_percent DECIMAL(10, 2),
                value_vs_avg_percent DECIMAL(10, 2),
                is_significantly_worse BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_fb_audience_date ON facebook_ads_audience_comparison(date_start);
            """
            hook.run(create_table_sql)
            
            for audience in comparison.get("audiences", []):
                insert_sql = """
                INSERT INTO facebook_ads_audience_comparison
                (date_start, date_stop, audience_type, spend, conversions, revenue,
                 cpa, conversion_value, cpa_vs_avg_percent, value_vs_avg_percent, is_significantly_worse)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    comparison["date_start"], comparison["date_stop"],
                    audience["audience_type"], audience["spend"], audience["conversions"],
                    audience["revenue"], audience["cpa"], audience["conversion_value"],
                    audience["performance_vs_avg"]["cpa_vs_avg"],
                    audience["performance_vs_avg"]["value_vs_avg"],
                    audience["is_significantly_worse"]
                ))
        
        underperforming = comparison.get("underperforming_audiences", [])
        logger.info(f"Encontradas {len(underperforming)} audiencias con rendimiento inferior")
        
        return {
            "total_audiences": len(comparison.get("audiences", [])),
            "underperforming_audiences": len(underperforming),
            "average_cpa": comparison.get("average_cpa", 0)
        }
    
    @task(task_id="analyze_remarketing_performance")
    def analyze_remarketing_performance(**context):
        """Analiza rendimiento de remarketing."""
        params = context.get("params", {})
        
        if not params.get("analyze_remarketing", True):
            logger.info("Análisis de remarketing deshabilitado")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Analizando remarketing desde {date_start} hasta {date_stop}")
        
        remarketing_data = extract_remarketing_performance(
            access_token=config.access_token,
            ad_account_id=config.ad_account_id,
            date_start=date_start,
            date_stop=date_stop,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS facebook_ads_remarketing (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                campaign_id VARCHAR(255),
                adset_id VARCHAR(255),
                device VARCHAR(50),
                day_of_week VARCHAR(20),
                frequency DECIMAL(10, 2),
                cpm DECIMAL(10, 2),
                conversions DECIMAL(10, 2),
                conversion_rate DECIMAL(10, 4),
                spend DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_fb_remarketing_date ON facebook_ads_remarketing(date_start);
            CREATE INDEX IF NOT EXISTS idx_fb_remarketing_device ON facebook_ads_remarketing(device);
            """
            hook.run(create_table_sql)
            
            for item in remarketing_data:
                insert_sql = """
                INSERT INTO facebook_ads_remarketing
                (date_start, date_stop, campaign_id, adset_id, device, day_of_week,
                 frequency, cpm, conversions, conversion_rate, spend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    date_start, date_stop, item["campaign_id"], item["adset_id"],
                    item["device"], item["day_of_week"], item["frequency"], item["cpm"],
                    item["conversions"], item["conversion_rate"], item["spend"]
                ))
        
        logger.info(f"Analizados {len(remarketing_data)} registros de remarketing")
        return {"records_analyzed": len(remarketing_data)}
    
    @task(task_id="analyze_creative_performance")
    def analyze_creative_performance(**context):
        """Analiza rendimiento histórico de creatividades."""
        params = context.get("params", {})
        
        if not params.get("analyze_creatives", True):
            logger.info("Análisis de creatividades deshabilitado")
            return {"skipped": True}
        
        months_back = params.get("creative_analysis_months", 3)
        
        logger.info(f"Analizando creatividades para últimos {months_back} meses")
        
        creative_analysis = extract_creative_performance_historical(
            access_token=config.access_token,
            ad_account_id=config.ad_account_id,
            months_back=months_back,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS facebook_ads_creative_performance (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                creative_id VARCHAR(255),
                ad_name TEXT,
                spend DECIMAL(10, 2),
                conversions DECIMAL(10, 2),
                revenue DECIMAL(10, 2),
                conversion_rate DECIMAL(10, 4),
                roas DECIMAL(10, 4),
                cost_per_conversion DECIMAL(10, 2),
                num_ads INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_fb_creative_date ON facebook_ads_creative_performance(date_start);
            CREATE INDEX IF NOT EXISTS idx_fb_creative_id ON facebook_ads_creative_performance(creative_id);
            """
            hook.run(create_table_sql)
            
            for creative in creative_analysis.get("creatives", []):
                insert_sql = """
                INSERT INTO facebook_ads_creative_performance
                (date_start, date_stop, creative_id, ad_name, spend, conversions,
                 revenue, conversion_rate, roas, cost_per_conversion, num_ads)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    creative_analysis["date_start"], creative_analysis["date_stop"],
                    creative["creative_id"], creative["ad_name"], creative["spend"],
                    creative["conversions"], creative["revenue"], creative["conversion_rate"],
                    creative["roas"], creative["cost_per_conversion"], creative["num_ads"]
                ))
        
        top_performers = creative_analysis.get("top_performers", [])
        logger.info(f"Analizadas {len(creative_analysis.get('creatives', []))} creatividades")
        logger.info(f"Coste incremental vs promedio: {creative_analysis.get('incremental_cost_vs_average', 0)}")
        
        return {
            "total_creatives": len(creative_analysis.get("creatives", [])),
            "top_performers_count": len(top_performers),
            "incremental_cost": creative_analysis.get("incremental_cost_vs_average", 0)
        }
    
    # Ejecutar tasks
    performance = extract_campaign_performance()
    audience_comparison = compare_audience_performance()
    remarketing = analyze_remarketing_performance()
    creatives = analyze_creative_performance()


dag = facebook_ads_reporting()

