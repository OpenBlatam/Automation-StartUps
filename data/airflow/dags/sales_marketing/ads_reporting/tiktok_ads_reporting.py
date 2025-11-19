"""
Módulo para extraer datos de rendimiento de TikTok Ads.

Funcionalidades:
1. Extracción de datos de campañas con métricas completas
2. Análisis por ubicación geográfica y demografía
3. Análisis de engagement y correlación con conversiones

Variables de entorno requeridas:
- TIKTOK_ACCESS_TOKEN: Token de acceso de TikTok Marketing API
- TIKTOK_APP_ID: ID de la aplicación
- TIKTOK_SECRET: Secret de la aplicación
- TIKTOK_ADVERTISER_ID: ID del anunciante

Variables de entorno opcionales:
- TIKTOK_API_VERSION: Versión de la API (default: v1.3)
- TIKTOK_REPORT_DESTINATION: Destino para guardar reportes (s3 | postgres | local)
"""

from __future__ import annotations

import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
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
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from ads_reporting_utils import (
        check_api_credentials,
        check_database_connection,
        validate_date_range,
        check_data_quality_campaigns,
        track_operation,
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    logger.warning("ads_reporting_utils no disponible")

# Constantes de configuración
TIKTOK_MAX_RETRIES = int(os.environ.get("TIKTOK_MAX_RETRIES", "3"))
TIKTOK_RETRY_BACKOFF = float(os.environ.get("TIKTOK_RETRY_BACKOFF", "1.0"))
TIKTOK_RATE_LIMIT_DELAY = float(os.environ.get("TIKTOK_RATE_LIMIT_DELAY", "0.5"))
TIKTOK_REQUEST_TIMEOUT = int(os.environ.get("TIKTOK_REQUEST_TIMEOUT", "30"))


# Excepciones personalizadas
class TikTokAdsError(Exception):
    """Excepción base para errores de TikTok Ads."""
    pass


class TikTokAdsAuthError(TikTokAdsError):
    """Error de autenticación con TikTok Ads."""
    pass


class TikTokAdsAPIError(TikTokAdsError):
    """Error en la respuesta de la API de TikTok Ads."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class TikTokAdsRateLimitError(TikTokAdsError):
    """Error de rate limiting de TikTok Ads."""
    pass


@dataclass
class TikTokAdsConfig:
    """Configuración para TikTok Ads API."""
    access_token: str
    app_id: Optional[str] = None
    secret: Optional[str] = None
    advertiser_id: str = ""
    api_version: str = "v1.3"
    report_destination: str = "postgres"
    postgres_conn_id: str = "postgres_default"
    
    def validate(self) -> None:
        """Valida que la configuración sea correcta."""
        if not self.access_token:
            raise TikTokAdsAuthError("TIKTOK_ACCESS_TOKEN es requerido")
        if not self.advertiser_id:
            raise TikTokAdsAuthError("TIKTOK_ADVERTISER_ID es requerido")


@dataclass
class TikTokCampaignData:
    """Datos de campaña de TikTok."""
    date_start: str
    date_stop: str
    campaign_id: str
    campaign_name: str
    ad_group_id: str
    ad_group_name: str
    ad_id: str
    ad_name: str
    ad_format: str
    impressions: int
    reach: int
    clicks: int
    ctr: float
    cpc: float
    cpi: Optional[float] = None
    conversions: float
    conversion_rate: float
    spend: float


def _load_tiktok_config() -> TikTokAdsConfig:
    """Carga y valida configuración desde variables de entorno."""
    config = TikTokAdsConfig(
        access_token=os.environ.get("TIKTOK_ACCESS_TOKEN", ""),
        app_id=os.environ.get("TIKTOK_APP_ID"),
        secret=os.environ.get("TIKTOK_SECRET"),
        advertiser_id=os.environ.get("TIKTOK_ADVERTISER_ID", ""),
        api_version=os.environ.get("TIKTOK_API_VERSION", "v1.3"),
        report_destination=os.environ.get("TIKTOK_REPORT_DESTINATION", "postgres"),
        postgres_conn_id=os.environ.get("POSTGRES_CONN_ID", "postgres_default")
    )
    
    try:
        config.validate()
    except TikTokAdsAuthError as e:
        logger.error(f"Error de validación de configuración: {str(e)}")
        raise
    
    return config


def _create_tiktok_session() -> requests.Session:
    """Crea una sesión HTTP con retry strategy para TikTok API."""
    session = requests.Session()
    
    retry_strategy = Retry(
        total=TIKTOK_MAX_RETRIES,
        backoff_factor=TIKTOK_RETRY_BACKOFF,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["POST"],
        raise_on_status=False
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


@contextmanager
def _track_metric(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager para trackear métricas."""
    start_time = time.time()
    if STATS_AVAILABLE:
        try:
            stats = Stats()
            stats.incr(f"tiktok_ads.{metric_name}.start", tags=tags or {})
        except Exception:
            pass
    
    try:
        yield
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                duration_ms = (time.time() - start_time) * 1000
                stats.incr(f"tiktok_ads.{metric_name}.success", tags=tags or {})
                stats.timing(f"tiktok_ads.{metric_name}.duration_ms", int(duration_ms), tags=tags or {})
            except Exception:
                pass
    except Exception as e:
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.incr(f"tiktok_ads.{metric_name}.error", tags={**(tags or {}), "error_type": type(e).__name__})
            except Exception:
                pass
        raise


def _make_tiktok_api_request(
    access_token: str,
    endpoint: str,
    params: Dict[str, Any],
    api_version: str = "v1.3",
    session: Optional[requests.Session] = None
) -> Dict[str, Any]:
    """
    Realiza una petición a la TikTok Marketing API con retry logic.
    
    Args:
        access_token: Token de acceso de TikTok
        endpoint: Endpoint de la API (ej: "/report/integrated/get/")
        params: Parámetros de la petición
        api_version: Versión de la API
        session: Sesión HTTP reutilizable (opcional)
        
    Returns:
        Respuesta JSON parseada
        
    Raises:
        TikTokAdsAPIError: Si hay error en la petición
        TikTokAdsRateLimitError: Si hay rate limiting
    """
    base_url = f"https://business-api.tiktok.com/open_api/{api_version}"
    url = f"{base_url}{endpoint}"
    
    headers = {
        "Access-Token": access_token,
        "Content-Type": "application/json"
    }
    
    if session is None:
        session = _create_tiktok_session()
    
    def _execute_request():
        response = session.post(url, headers=headers, json=params, timeout=TIKTOK_REQUEST_TIMEOUT)
        
        # Manejar rate limiting
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', TIKTOK_RATE_LIMIT_DELAY))
            logger.warning(f"Rate limit alcanzado, esperando {retry_after}s")
            time.sleep(min(retry_after, 300))  # Máximo 5 minutos
            raise TikTokAdsRateLimitError(f"Rate limit: {response.text}")
        
        response.raise_for_status()
        
        data = response.json()
        
        # Verificar errores en la respuesta de TikTok
        if data.get('code') and data.get('code') != 0:
            error_code = data.get('code', 0)
            error_msg = data.get('message', 'Unknown error')
            raise TikTokAdsAPIError(
                f"TikTok API Error: {error_msg}",
                status_code=error_code,
                error_data=data
            )
        
        return data
    
    # Usar tenacity para retry si está disponible
    if TENACITY_AVAILABLE:
        @retry(
            stop=stop_after_attempt(TIKTOK_MAX_RETRIES + 1),
            wait=wait_exponential(multiplier=TIKTOK_RETRY_BACKOFF, min=1, max=10),
            retry=retry_if_exception_type((
                requests.exceptions.Timeout,
                requests.exceptions.ConnectionError,
                TikTokAdsRateLimitError
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
            if isinstance(e, (TikTokAdsAPIError, TikTokAdsAuthError)):
                raise
            raise TikTokAdsAPIError(f"Error en petición a TikTok API: {str(e)}")
    else:
        try:
            return _execute_request()
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 429:
                raise TikTokAdsRateLimitError(f"Rate limit: {str(e)}")
            raise TikTokAdsAPIError(f"HTTP Error: {str(e)}", status_code=getattr(e.response, 'status_code', None))
        except requests.exceptions.RequestException as e:
            raise TikTokAdsAPIError(f"Request Error: {str(e)}")


def extract_tiktok_campaign_data(
    access_token: str,
    advertiser_id: str,
    date_start: str,
    date_stop: str,
    api_version: str = "v1.3"
) -> List[TikTokCampaignData]:
    """
    Extrae datos de campañas de TikTok Ads.
    
    Args:
        access_token: Token de acceso
        advertiser_id: ID del anunciante
        date_start: Fecha inicio (YYYY-MM-DD)
        date_stop: Fecha fin (YYYY-MM-DD)
        api_version: Versión de la API
        
    Returns:
        Lista de datos de campañas
    """
    results = []
    
    # Campos a extraer
    dimensions = ["campaign_id", "adgroup_id", "ad_id", "stat_time_day"]
    metrics = [
        "impressions", "reach", "clicks",
        "ctr", "cpc", "cpi",
        "conversion", "conversion_rate", "spend",
        "ad_format", "campaign_name", "adgroup_name", "ad_name"
    ]
    
    params = {
        "advertiser_id": advertiser_id,
        "service_type": "AUCTION",
        "report_type": "BASIC",
        "data_level": "AUCTION_AD",
        "dimensions": json.dumps(dimensions),
        "metrics": json.dumps(metrics),
        "start_date": date_start,
        "end_date": date_stop,
        "page_size": 1000
    }
    
    endpoint = "/report/integrated/get/"
    
    try:
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            params["page"] = page
            
            response_data = _make_tiktok_api_request(
                access_token, endpoint, params, api_version
            )
            
            data_list = response_data.get("data", {}).get("list", [])
            
            if page == 1:
                pagination = response_data.get("data", {}).get("page_info", {})
                total_pages = pagination.get("total_page", 1)
            
            for item in data_list:
                try:
                    metrics_data = item.get("metrics", {})
                    
                    impressions = int(metrics_data.get("impressions", 0))
                    reach = int(metrics_data.get("reach", 0))
                    clicks = int(metrics_data.get("clicks", 0))
                    ctr = float(metrics_data.get("ctr", 0))
                    cpc = float(metrics_data.get("cpc", 0))
                    cpi = float(metrics_data.get("cpi", 0)) if metrics_data.get("cpi") else None
                    
                    # Conversiones
                    conversions = float(metrics_data.get("conversion", 0))
                    conversion_rate = float(metrics_data.get("conversion_rate", 0))
                    
                    spend = float(metrics_data.get("spend", 0))
                    
                    campaign_data = TikTokCampaignData(
                        date_start=date_start,
                        date_stop=date_stop,
                        campaign_id=str(item.get("campaign_id", "")),
                        campaign_name=item.get("campaign_name", ""),
                        ad_group_id=str(item.get("adgroup_id", "")),
                        ad_group_name=item.get("adgroup_name", ""),
                        ad_id=str(item.get("ad_id", "")),
                        ad_name=item.get("ad_name", ""),
                        ad_format=item.get("ad_format", "unknown"),
                        impressions=impressions,
                        reach=reach,
                        clicks=clicks,
                        ctr=ctr,
                        cpc=cpc,
                        cpi=cpi,
                        conversions=conversions,
                        conversion_rate=conversion_rate,
                        spend=spend
                    )
                    results.append(campaign_data)
                except Exception as e:
                    logger.warning(f"Error procesando item: {str(e)}")
                    continue
            
            page += 1
        
        logger.info(f"Extraídos {len(results)} registros de campañas de TikTok")
        return results
        
    except Exception as e:
        logger.error(f"Error extrayendo datos de campañas: {str(e)}")
        raise


def extract_tiktok_geographic_demographic_performance(
    access_token: str,
    advertiser_id: str,
    date_start: str,
    date_stop: str,
    api_version: str = "v1.3"
) -> Dict[str, Any]:
    """
    Extrae rendimiento por ubicación geográfica y demografía.
    
    Args:
        access_token: Token de acceso
        advertiser_id: ID del anunciante
        date_start: Fecha inicio
        date_stop: Fecha fin
        api_version: Versión de la API
        
    Returns:
        Diccionario con análisis por ubicación y demografía
    """
    # Análisis por ubicación geográfica
    location_dimensions = ["stat_time_day", "country_code", "region_code"]
    location_metrics = ["impressions", "clicks", "conversion", "spend", "cpc"]
    
    params_location = {
        "advertiser_id": advertiser_id,
        "service_type": "AUCTION",
        "report_type": "BASIC",
        "data_level": "AUCTION_CAMPAIGN",
        "dimensions": json.dumps(location_dimensions),
        "metrics": json.dumps(location_metrics),
        "start_date": date_start,
        "end_date": date_stop,
        "page_size": 1000
    }
    
    endpoint = "/report/integrated/get/"
    
    try:
        # Obtener datos por ubicación
        location_response = _make_tiktok_api_request(
            access_token, endpoint, params_location, api_version
        )
        
        location_data = location_response.get("data", {}).get("list", [])
        
        # Agrupar por país/región
        location_stats = {}
        for item in location_data:
            country = item.get("country_code", "unknown")
            region = item.get("region_code", "unknown")
            key = f"{country}_{region}"
            
            metrics_data = item.get("metrics", {})
            spend = float(metrics_data.get("spend", 0))
            conversions = float(metrics_data.get("conversion", 0))
            cpc = float(metrics_data.get("cpc", 0))
            
            if key not in location_stats:
                location_stats[key] = {
                    "country": country,
                    "region": region,
                    "spend": 0,
                    "conversions": 0,
                    "cpc_sum": 0,
                    "cpc_count": 0
                }
            
            location_stats[key]["spend"] += spend
            location_stats[key]["conversions"] += conversions
            location_stats[key]["cpc_sum"] += cpc
            location_stats[key]["cpc_count"] += 1
        
        # Calcular métricas por ubicación
        location_analysis = []
        for key, stats in location_stats.items():
            conversions = stats["conversions"]
            spend = stats["spend"]
            avg_cpc = (stats["cpc_sum"] / stats["cpc_count"]) if stats["cpc_count"] > 0 else 0
            cpa = (spend / conversions) if conversions > 0 else 0
            
            location_analysis.append({
                "country": stats["country"],
                "region": stats["region"],
                "spend": spend,
                "conversions": conversions,
                "avg_cpc": avg_cpc,
                "cpa": cpa,
                "conversion_rate": (conversions / (spend / avg_cpc * 1000)) if avg_cpc > 0 else 0
            })
        
        # Análisis por edad y género
        demographic_dimensions = ["stat_time_day", "age", "gender"]
        demographic_metrics = ["impressions", "clicks", "conversion", "spend"]
        
        params_demographic = {
            "advertiser_id": advertiser_id,
            "service_type": "AUCTION",
            "report_type": "BASIC",
            "data_level": "AUCTION_CAMPAIGN",
            "dimensions": json.dumps(demographic_dimensions),
            "metrics": json.dumps(demographic_metrics),
            "start_date": date_start,
            "end_date": date_stop,
            "page_size": 1000
        }
        
        demographic_response = _make_tiktok_api_request(
            access_token, endpoint, params_demographic, api_version
        )
        
        demographic_data = demographic_response.get("data", {}).get("list", [])
        
        # Agrupar por edad/género
        demographic_stats = {}
        for item in demographic_data:
            age = item.get("age", "unknown")
            gender = item.get("gender", "unknown")
            key = f"{age}_{gender}"
            
            metrics_data = item.get("metrics", {})
            spend = float(metrics_data.get("spend", 0))
            conversions = float(metrics_data.get("conversion", 0))
            
            if key not in demographic_stats:
                demographic_stats[key] = {
                    "age": age,
                    "gender": gender,
                    "spend": 0,
                    "conversions": 0
                }
            
            demographic_stats[key]["spend"] += spend
            demographic_stats[key]["conversions"] += conversions
        
        # Calcular métricas por demografía
        demographic_analysis = []
        for key, stats in demographic_stats.items():
            conversions = stats["conversions"]
            spend = stats["spend"]
            cpa = (spend / conversions) if conversions > 0 else 0
            
            demographic_analysis.append({
                "age": stats["age"],
                "gender": stats["gender"],
                "spend": spend,
                "conversions": conversions,
                "cpa": cpa
            })
        
        # Identificar mejores y peores ubicaciones
        location_analysis.sort(key=lambda x: (x["conversions"], -x["cpa"]), reverse=True)
        best_locations = location_analysis[:5]
        worst_locations = sorted(location_analysis[-5:], key=lambda x: x["cpa"]) if len(location_analysis) > 5 else []
        
        # Identificar mejores demografías
        demographic_analysis.sort(key=lambda x: (x["conversions"], -x["cpa"]), reverse=True)
        best_demographics = demographic_analysis[:5]
        
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "locations": location_analysis,
            "best_locations": best_locations,
            "worst_locations": worst_locations,
            "demographics": demographic_analysis,
            "best_demographics": best_demographics
        }
        
    except Exception as e:
        logger.error(f"Error extrayendo datos geográficos/demográficos: {str(e)}")
        raise


def extract_tiktok_engagement_performance(
    access_token: str,
    advertiser_id: str,
    date_start: str,
    date_stop: str,
    api_version: str = "v1.3"
) -> Dict[str, Any]:
    """
    Extrae datos de engagement y correlaciona con conversiones.
    
    Args:
        access_token: Token de acceso
        advertiser_id: ID del anunciante
        date_start: Fecha inicio
        date_stop: Fecha fin
        api_version: Versión de la API
        
    Returns:
        Diccionario con análisis de engagement y conversiones
    """
    dimensions = ["stat_time_day", "ad_id"]
    metrics = [
        "impressions", "clicks",
        "likes", "comments", "shares",
        "conversion", "spend", "cpa"
    ]
    
    params = {
        "advertiser_id": advertiser_id,
        "service_type": "AUCTION",
        "report_type": "BASIC",
        "data_level": "AUCTION_AD",
        "dimensions": json.dumps(dimensions),
        "metrics": json.dumps(metrics),
        "start_date": date_start,
        "end_date": date_stop,
        "page_size": 1000
    }
    
    endpoint = "/report/integrated/get/"
    
    try:
        response_data = _make_tiktok_api_request(
            access_token, endpoint, params, api_version
        )
        
        data_list = response_data.get("data", {}).get("list", [])
        
        ad_engagement = {}
        
        for item in data_list:
            ad_id = str(item.get("ad_id", ""))
            metrics_data = item.get("metrics", {})
            
            likes = int(metrics_data.get("likes", 0))
            comments = int(metrics_data.get("comments", 0))
            shares = int(metrics_data.get("shares", 0))
            conversions = float(metrics_data.get("conversion", 0))
            spend = float(metrics_data.get("spend", 0))
            cpa = float(metrics_data.get("cpa", 0))
            
            total_engagement = likes + comments + shares
            
            if ad_id not in ad_engagement:
                ad_engagement[ad_id] = {
                    "ad_id": ad_id,
                    "total_likes": 0,
                    "total_comments": 0,
                    "total_shares": 0,
                    "total_engagement": 0,
                    "total_conversions": 0,
                    "total_spend": 0,
                    "cpa_sum": 0,
                    "cpa_count": 0
                }
            
            ad_engagement[ad_id]["total_likes"] += likes
            ad_engagement[ad_id]["total_comments"] += comments
            ad_engagement[ad_id]["total_shares"] += shares
            ad_engagement[ad_id]["total_engagement"] += total_engagement
            ad_engagement[ad_id]["total_conversions"] += conversions
            ad_engagement[ad_id]["total_spend"] += spend
            ad_engagement[ad_id]["cpa_sum"] += cpa
            ad_engagement[ad_id]["cpa_count"] += 1
        
        # Calcular correlación
        engagement_analysis = []
        for ad_id, stats in ad_engagement.items():
            engagement = stats["total_engagement"]
            conversions = stats["total_conversions"]
            spend = stats["total_spend"]
            avg_cpa = (stats["cpa_sum"] / stats["cpa_count"]) if stats["cpa_count"] > 0 else 0
            
            engagement_per_dollar = (engagement / spend) if spend > 0 else 0
            conversion_per_engagement = (conversions / engagement) if engagement > 0 else 0
            
            engagement_analysis.append({
                "ad_id": ad_id,
                "total_engagement": engagement,
                "total_conversions": conversions,
                "total_spend": spend,
                "avg_cpa": avg_cpa,
                "engagement_per_dollar": engagement_per_dollar,
                "conversion_per_engagement": conversion_per_engagement,
                "engagement_to_conversion_ratio": conversion_per_engagement * 100  # Porcentaje
            })
        
        # Ordenar por engagement y por conversiones
        engagement_analysis.sort(key=lambda x: x["total_engagement"], reverse=True)
        top_engagement = engagement_analysis[:10]
        
        engagement_analysis.sort(key=lambda x: x["total_conversions"], reverse=True)
        top_conversions = engagement_analysis[:10]
        
        # Calcular correlación general
        total_engagement_all = sum(a["total_engagement"] for a in engagement_analysis)
        total_conversions_all = sum(a["total_conversions"] for a in engagement_analysis)
        overall_ratio = (total_conversions_all / total_engagement_all * 100) if total_engagement_all > 0 else 0
        
        # Identificar creatividades con alto engagement pero bajo conversiones
        high_engagement_low_conversion = [
            a for a in engagement_analysis
            if a["total_engagement"] > (total_engagement_all / len(engagement_analysis) * 2)  # 2x promedio
            and a["conversion_per_engagement"] < (overall_ratio / 100 * 0.5)  # Menos de 50% del promedio
        ]
        
        return {
            "date_start": date_start,
            "date_stop": date_stop,
            "total_ads": len(engagement_analysis),
            "total_engagement": total_engagement_all,
            "total_conversions": total_conversions_all,
            "overall_engagement_to_conversion_ratio": overall_ratio,
            "ads_analysis": engagement_analysis,
            "top_engagement_ads": top_engagement,
            "top_conversion_ads": top_conversions,
            "high_engagement_low_conversion_ads": high_engagement_low_conversion,
            "correlation": {
                "engagement_high_conversions_high": len([a for a in top_engagement[:5] if a in top_conversions[:5]]),
                "engagement_not_correlating": len(high_engagement_low_conversion)
            }
        }
        
    except Exception as e:
        logger.error(f"Error extrayendo datos de engagement: {str(e)}")
        raise


@dag(
    dag_id="tiktok_ads_reporting",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 7 * * *",  # Diario a las 7 AM
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    doc_md="""
    ### TikTok Ads Reporting
    
    Extrae y analiza datos de rendimiento de campañas de TikTok Ads.
    
    **Funcionalidades:**
    1. Extracción de datos de campañas con métricas completas
    2. Análisis por ubicación geográfica y demografía
    3. Análisis de engagement y correlación con conversiones
    
    **Parámetros:**
    - `date_start`: Fecha inicio (YYYY-MM-DD)
    - `date_stop`: Fecha fin (YYYY-MM-DD)
    - `extract_campaigns`: Extraer datos de campañas (default: true)
    - `analyze_geographic`: Analizar por ubicación (default: true)
    - `analyze_engagement`: Analizar engagement (default: true)
    """,
    params={
        "date_start": Param("", type="string"),
        "date_stop": Param("", type="string"),
        "extract_campaigns": Param(True, type="boolean"),
        "analyze_geographic": Param(True, type="boolean"),
        "analyze_engagement": Param(True, type="boolean"),
    },
    tags=["marketing", "tiktok-ads", "reporting"],
)
def tiktok_ads_reporting():
    """DAG principal para reporting de TikTok Ads."""
    
    config = _load_tiktok_config()
    
    @task(task_id="extract_campaign_data")
    def extract_campaign_data(**context):
        """Extrae datos de campañas."""
        params = context.get("params", {})
        
        if not params.get("extract_campaigns", True):
            logger.info("Extracción de campañas deshabilitada")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Extrayendo datos de campañas desde {date_start} hasta {date_stop}")
        
        campaign_data = extract_tiktok_campaign_data(
            access_token=config.access_token,
            advertiser_id=config.advertiser_id,
            date_start=date_start,
            date_stop=date_stop,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS tiktok_ads_campaigns (
                date_start DATE,
                date_stop DATE,
                campaign_id VARCHAR(255),
                campaign_name TEXT,
                ad_group_id VARCHAR(255),
                ad_group_name TEXT,
                ad_id VARCHAR(255),
                ad_name TEXT,
                ad_format VARCHAR(50),
                impressions INTEGER,
                reach INTEGER,
                clicks INTEGER,
                ctr DECIMAL(10, 4),
                cpc DECIMAL(10, 4),
                cpi DECIMAL(10, 4),
                conversions DECIMAL(10, 2),
                conversion_rate DECIMAL(10, 4),
                spend DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_date ON tiktok_ads_campaigns(date_start, date_stop);
            CREATE INDEX IF NOT EXISTS idx_tiktok_campaign_id ON tiktok_ads_campaigns(campaign_id);
            """
            hook.run(create_table_sql)
            
            for camp in campaign_data:
                insert_sql = """
                INSERT INTO tiktok_ads_campaigns
                (date_start, date_stop, campaign_id, campaign_name, ad_group_id, ad_group_name,
                 ad_id, ad_name, ad_format, impressions, reach, clicks, ctr, cpc, cpi,
                 conversions, conversion_rate, spend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    camp.date_start, camp.date_stop, camp.campaign_id, camp.campaign_name,
                    camp.ad_group_id, camp.ad_group_name, camp.ad_id, camp.ad_name,
                    camp.ad_format, camp.impressions, camp.reach, camp.clicks, camp.ctr,
                    camp.cpc, camp.cpi, camp.conversions, camp.conversion_rate, camp.spend
                ))
        
        logger.info(f"Extraídos {len(campaign_data)} registros de campañas")
        return {"records_extracted": len(campaign_data)}
    
    @task(task_id="analyze_geographic_demographic")
    def analyze_geographic_demographic(**context):
        """Analiza rendimiento por ubicación y demografía."""
        params = context.get("params", {})
        
        if not params.get("analyze_geographic", True):
            logger.info("Análisis geográfico/demográfico deshabilitado")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Analizando ubicación y demografía desde {date_start} hasta {date_stop}")
        
        geo_demo_analysis = extract_tiktok_geographic_demographic_performance(
            access_token=config.access_token,
            advertiser_id=config.advertiser_id,
            date_start=date_start,
            date_stop=date_stop,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            # Tabla para ubicaciones
            create_location_table_sql = """
            CREATE TABLE IF NOT EXISTS tiktok_ads_locations (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                country VARCHAR(10),
                region VARCHAR(100),
                spend DECIMAL(10, 2),
                conversions DECIMAL(10, 2),
                avg_cpc DECIMAL(10, 4),
                cpa DECIMAL(10, 2),
                conversion_rate DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tiktok_location_date ON tiktok_ads_locations(date_start);
            CREATE INDEX IF NOT EXISTS idx_tiktok_location_country ON tiktok_ads_locations(country);
            """
            hook.run(create_location_table_sql)
            
            for location in geo_demo_analysis.get("locations", []):
                insert_sql = """
                INSERT INTO tiktok_ads_locations
                (date_start, date_stop, country, region, spend, conversions, avg_cpc, cpa, conversion_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    geo_demo_analysis["date_start"], geo_demo_analysis["date_stop"],
                    location["country"], location["region"], location["spend"],
                    location["conversions"], location["avg_cpc"], location["cpa"],
                    location["conversion_rate"]
                ))
            
            # Tabla para demografía
            create_demo_table_sql = """
            CREATE TABLE IF NOT EXISTS tiktok_ads_demographics (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                age VARCHAR(50),
                gender VARCHAR(20),
                spend DECIMAL(10, 2),
                conversions DECIMAL(10, 2),
                cpa DECIMAL(10, 2),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tiktok_demo_date ON tiktok_ads_demographics(date_start);
            """
            hook.run(create_demo_table_sql)
            
            for demo in geo_demo_analysis.get("demographics", []):
                insert_sql = """
                INSERT INTO tiktok_ads_demographics
                (date_start, date_stop, age, gender, spend, conversions, cpa)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    geo_demo_analysis["date_start"], geo_demo_analysis["date_stop"],
                    demo["age"], demo["gender"], demo["spend"],
                    demo["conversions"], demo["cpa"]
                ))
        
        logger.info(f"Analizadas {len(geo_demo_analysis.get('locations', []))} ubicaciones")
        logger.info(f"Analizadas {len(geo_demo_analysis.get('demographics', []))} demografías")
        
        return {
            "locations_analyzed": len(geo_demo_analysis.get("locations", [])),
            "demographics_analyzed": len(geo_demo_analysis.get("demographics", [])),
            "best_locations_count": len(geo_demo_analysis.get("best_locations", []))
        }
    
    @task(task_id="analyze_engagement_conversions")
    def analyze_engagement_conversions(**context):
        """Analiza engagement y correlación con conversiones."""
        params = context.get("params", {})
        
        if not params.get("analyze_engagement", True):
            logger.info("Análisis de engagement deshabilitado")
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        logger.info(f"Analizando engagement desde {date_start} hasta {date_stop}")
        
        engagement_analysis = extract_tiktok_engagement_performance(
            access_token=config.access_token,
            advertiser_id=config.advertiser_id,
            date_start=date_start,
            date_stop=date_stop,
            api_version=config.api_version
        )
        
        # Guardar en PostgreSQL
        if config.report_destination == "postgres":
            hook = PostgresHook(postgres_conn_id=config.postgres_conn_id)
            
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS tiktok_ads_engagement (
                id SERIAL PRIMARY KEY,
                date_start DATE,
                date_stop DATE,
                ad_id VARCHAR(255),
                total_engagement INTEGER,
                total_conversions DECIMAL(10, 2),
                total_spend DECIMAL(10, 2),
                avg_cpa DECIMAL(10, 2),
                engagement_per_dollar DECIMAL(10, 4),
                conversion_per_engagement DECIMAL(10, 6),
                engagement_to_conversion_ratio DECIMAL(10, 4),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_tiktok_engagement_date ON tiktok_ads_engagement(date_start);
            CREATE INDEX IF NOT EXISTS idx_tiktok_engagement_ad ON tiktok_ads_engagement(ad_id);
            """
            hook.run(create_table_sql)
            
            for ad in engagement_analysis.get("ads_analysis", []):
                insert_sql = """
                INSERT INTO tiktok_ads_engagement
                (date_start, date_stop, ad_id, total_engagement, total_conversions, total_spend,
                 avg_cpa, engagement_per_dollar, conversion_per_engagement, engagement_to_conversion_ratio)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                hook.run(insert_sql, parameters=(
                    engagement_analysis["date_start"], engagement_analysis["date_stop"],
                    ad["ad_id"], ad["total_engagement"], ad["total_conversions"],
                    ad["total_spend"], ad["avg_cpa"], ad["engagement_per_dollar"],
                    ad["conversion_per_engagement"], ad["engagement_to_conversion_ratio"]
                ))
        
        correlation = engagement_analysis.get("correlation", {})
        logger.info(f"Análisis completado: {correlation.get('engagement_high_conversions_high', 0)} ads con alto engagement y conversiones")
        
        return {
            "total_ads": engagement_analysis.get("total_ads", 0),
            "total_engagement": engagement_analysis.get("total_engagement", 0),
            "overall_ratio": engagement_analysis.get("overall_engagement_to_conversion_ratio", 0),
            "high_engagement_high_conversions": correlation.get("engagement_high_conversions_high", 0)
        }
    
    # Ejecutar tasks
    campaigns = extract_campaign_data()
    geo_demo = analyze_geographic_demographic()
    engagement = analyze_engagement_conversions()


dag = tiktok_ads_reporting()

