"""
DAG modular mejorado para Facebook Ads usando la arquitectura modular.

Este DAG usa:
- FacebookAdsClient para comunicación con la API
- FacebookExtractor para extracción de datos
- PostgreSQLStorage para almacenamiento
- ads_reporting_utils para health checks y validaciones
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
from ads_reporting.extractors import FacebookExtractor
from ads_reporting.storage import get_storage

# Utilidades compartidas
try:
    from ads_reporting_utils import (
        check_api_credentials,
        check_database_connection,
        validate_date_range,
        check_data_quality_campaigns,
        aggregate_health_checks,
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

logger = logging.getLogger(__name__)


def _load_config() -> FacebookAdsConfig:
    """Carga configuración desde variables de entorno."""
    return FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        app_id=os.environ.get("FACEBOOK_APP_ID"),
        app_secret=os.environ.get("FACEBOOK_APP_SECRET"),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
        api_version=os.environ.get("FACEBOOK_API_VERSION", "v18.0"),
        max_retries=int(os.environ.get("FACEBOOK_MAX_RETRIES", "3")),
        retry_backoff=float(os.environ.get("FACEBOOK_RETRY_BACKOFF", "1.0")),
        rate_limit_delay=float(os.environ.get("FACEBOOK_RATE_LIMIT_DELAY", "0.5")),
        request_timeout=int(os.environ.get("FACEBOOK_REQUEST_TIMEOUT", "30")),
    )


@dag(
    dag_id="facebook_ads_reporting_modular",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 6 * * *",
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
    },
    params={
        "date_start": Param("", type="string"),
        "date_stop": Param("", type="string"),
        "extract_performance": Param(True, type="boolean"),
        "compare_audiences": Param(True, type="boolean"),
    },
    tags=["marketing", "facebook-ads", "reporting", "modular"],
)
def facebook_ads_reporting_modular():
    """DAG modular para reporting de Facebook Ads."""
    
    config = _load_config()
    
    @task(task_id="health_check")
    def health_check_task(**context) -> Dict[str, Any]:
        """Health check antes de ejecutar."""
        if not UTILS_AVAILABLE:
            logger.warning("Utilidades no disponibles, saltando health checks")
            return {"status": "skipped"}
        
        checks = []
        
        # Verificar credenciales
        checks.append(check_api_credentials(
            "facebook",
            access_token=config.access_token,
            account_id=config.ad_account_id
        ))
        
        # Verificar base de datos
        storage_type = os.environ.get("FACEBOOK_REPORT_DESTINATION", "postgres")
        if storage_type == "postgres":
            checks.append(check_database_connection(
                os.environ.get("POSTGRES_CONN_ID", "postgres_default")
            ))
        
        result = aggregate_health_checks(checks)
        
        if result.status == "error":
            raise ValueError(f"Health check failed: {result.message}")
        
        return {"status": result.status, "checks": result.details}
    
    @task(task_id="extract_campaign_performance")
    def extract_campaign_performance_task(**context) -> Dict[str, Any]:
        """Extrae datos de rendimiento de campañas."""
        params = context.get("params", {})
        
        if not params.get("extract_performance", True):
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        # Validar fechas
        if UTILS_AVAILABLE:
            is_valid, error_msg = validate_date_range(date_start, date_stop)
            if not is_valid:
                raise ValueError(f"Rango de fechas inválido: {error_msg}")
        
        # Usar cliente y extractor
        with FacebookAdsClient(config) as client:
            extractor = FacebookExtractor(client)
            data = extractor.extract_campaign_performance(
                date_start, date_stop,
                breakdowns=["audience_type", "region"]
            )
        
        # Data quality check
        if UTILS_AVAILABLE:
            dq_check = check_data_quality_campaigns(data, "facebook")
            if not dq_check.passed:
                logger.warning(f"Data quality issues: {dq_check.issues}")
        
        return {
            "records_extracted": len(data),
            "date_start": date_start,
            "date_stop": date_stop,
            "data": data
        }
    
    @task(task_id="save_to_storage")
    def save_to_storage_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Guarda datos en el almacenamiento configurado."""
        if extraction_result.get("skipped"):
            return {"skipped": True}
        
        data = extraction_result.get("data", [])
        if not data:
            return {"saved": 0, "errors": 0}
        
        storage_type = os.environ.get("FACEBOOK_REPORT_DESTINATION", "postgres")
        
        if storage_type == "postgres":
            storage = get_storage(
                "postgres",
                postgres_conn_id=os.environ.get("POSTGRES_CONN_ID", "postgres_default")
            )
            result = storage.save_campaign_performance(
                data,
                "facebook_ads_performance"
            )
        else:
            logger.warning(f"Storage type {storage_type} no implementado completamente")
            result = {"saved": 0, "errors": 0}
        
        return result
    
    @task(task_id="extract_audience_comparison")
    def extract_audience_comparison_task(**context) -> Dict[str, Any]:
        """Extrae y compara rendimiento por audiencia."""
        params = context.get("params", {})
        
        if not params.get("compare_audiences", True):
            return {"skipped": True}
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        with FacebookAdsClient(config) as client:
            extractor = FacebookExtractor(client)
            data = extractor.extract_audience_performance(date_start, date_stop)
        
        # Guardar en storage
        storage_type = os.environ.get("FACEBOOK_REPORT_DESTINATION", "postgres")
        if storage_type == "postgres":
            storage = get_storage(
                "postgres",
                postgres_conn_id=os.environ.get("POSTGRES_CONN_ID", "postgres_default")
            )
            storage.save_audience_performance(data, "facebook_ads_audience_comparison")
        
        return {
            "total_audiences": len(data.get("audiences", [])),
            "average_cpa": data.get("average_cpa", 0)
        }
    
    # Pipeline
    health = health_check_task()
    performance = extract_campaign_performance_task()
    saved = save_to_storage_task(performance)
    audiences = extract_audience_comparison_task()
    
    # Dependencias
    performance.set_upstream(health)
    saved.set_upstream(performance)
    audiences.set_upstream(health)


dag = facebook_ads_reporting_modular()

