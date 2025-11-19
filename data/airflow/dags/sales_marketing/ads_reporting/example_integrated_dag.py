"""
Ejemplo de DAG integrado usando toda la arquitectura modular.

Este DAG demuestra:
- Health checks
- Extracción con caché
- Validación de datos
- Procesamiento y transformación
- Almacenamiento
- Data quality checks
"""

from __future__ import annotations

import os
import logging
from datetime import datetime, timedelta
from typing import Any, Dict

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

# Imports modulares
from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
from ads_reporting.extractors import FacebookExtractor
from ads_reporting.storage import get_storage
from ads_reporting.processors import CampaignProcessor
from ads_reporting.validators import validate_campaign_data
from ads_reporting.cache import get_cache
from ads_reporting.config import get_config

# Utilidades
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


@dag(
    dag_id="facebook_ads_reporting_integrated",
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
        "use_cache": Param(True, type="boolean"),
        "enable_validation": Param(True, type="boolean"),
        "enable_processing": Param(True, type="boolean"),
    },
    tags=["marketing", "facebook-ads", "integrated", "modular"],
)
def facebook_ads_reporting_integrated():
    """
    DAG integrado que demuestra toda la arquitectura modular.
    
    Pipeline completo:
    1. Health checks
    2. Extracción (con caché)
    3. Validación
    4. Procesamiento
    5. Data quality
    6. Almacenamiento
    """
    
    # Cargar configuración global
    global_config = get_config()
    
    # Cargar configuración de Facebook
    fb_config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
        api_version=os.environ.get("FACEBOOK_API_VERSION", "v18.0"),
        max_retries=global_config.default_max_retries,
        retry_backoff=global_config.default_retry_backoff,
        rate_limit_delay=global_config.default_rate_limit_delay,
        request_timeout=global_config.default_request_timeout,
    )
    
    @task(task_id="health_check")
    def health_check_task(**context) -> Dict[str, Any]:
        """Health checks completos."""
        if not UTILS_AVAILABLE:
            logger.warning("Utilidades no disponibles")
            return {"status": "skipped"}
        
        checks = []
        
        # Verificar credenciales
        checks.append(check_api_credentials(
            "facebook",
            access_token=fb_config.access_token,
            account_id=fb_config.ad_account_id
        ))
        
        # Verificar base de datos
        if global_config.default_storage == "postgres":
            checks.append(check_database_connection(global_config.postgres_conn_id))
        
        result = aggregate_health_checks(checks)
        
        if result.status == "error":
            raise ValueError(f"Health check failed: {result.message}")
        
        return {"status": result.status, "details": result.details}
    
    @task(task_id="extract_with_cache")
    def extract_with_cache_task(**context) -> Dict[str, Any]:
        """Extrae datos con caché inteligente."""
        params = context.get("params", {})
        use_cache = params.get("use_cache", True)
        
        date_start = params.get("date_start") or (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        date_stop = params.get("date_stop") or datetime.now().strftime("%Y-%m-%d")
        
        # Validar fechas
        if UTILS_AVAILABLE:
            is_valid, error_msg = validate_date_range(date_start, date_stop)
            if not is_valid:
                raise ValueError(f"Rango de fechas inválido: {error_msg}")
        
        # Inicializar caché si está habilitado
        cache = None
        if use_cache and global_config.cache_enabled:
            cache = get_cache(
                maxsize=global_config.cache_maxsize,
                ttl=global_config.cache_ttl
            )
            
            # Intentar obtener del caché
            cached_data = cache.get(
                "facebook",
                "campaign_performance",
                {"date_start": date_start, "date_stop": date_stop}
            )
            
            if cached_data is not None:
                logger.info("Datos obtenidos del caché")
                return {
                    "records_extracted": len(cached_data),
                    "date_start": date_start,
                    "date_stop": date_stop,
                    "data": cached_data,
                    "from_cache": True
                }
        
        # Extraer datos
        with FacebookAdsClient(fb_config) as client:
            extractor = FacebookExtractor(client)
            data = extractor.extract_campaign_performance(
                date_start, date_stop,
                breakdowns=["audience_type", "region"]
            )
        
        # Guardar en caché
        if cache:
            cache.set(
                "facebook",
                "campaign_performance",
                {"date_start": date_start, "date_stop": date_stop},
                data
            )
            logger.info("Datos guardados en caché")
        
        return {
            "records_extracted": len(data),
            "date_start": date_start,
            "date_stop": date_stop,
            "data": data,
            "from_cache": False
        }
    
    @task(task_id="validate_data")
    def validate_data_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Valida datos extraídos."""
        if extraction_result.get("skipped"):
            return {"skipped": True}
        
        params = context.get("params", {})
        if not params.get("enable_validation", True):
            return {"skipped": True}
        
        data = extraction_result.get("data", [])
        if not data:
            return {"valid": False, "errors": ["No hay datos para validar"]}
        
        # Validación completa
        result = validate_campaign_data(
            data,
            strict=global_config.strict_validation
        )
        
        if not result.valid:
            logger.warning(f"Validación falló: {result.errors}")
            if global_config.strict_validation:
                raise ValueError(f"Validación estricta falló: {result.errors}")
        
        if result.warnings:
            logger.info(f"Advertencias de validación: {result.warnings}")
        
        return {
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings,
            "metrics": result.metrics
        }
    
    @task(task_id="process_data")
    def process_data_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Procesa y transforma datos."""
        if extraction_result.get("skipped"):
            return {"skipped": True}
        
        params = context.get("params", {})
        if not params.get("enable_processing", True):
            return {"skipped": True}
        
        data = extraction_result.get("data", [])
        if not data:
            return {"skipped": True}
        
        # Normalizar datos
        processor = CampaignProcessor()
        normalized_data = processor.normalize(data)
        
        # Calcular métricas agregadas
        metrics = processor.calculate_metrics(normalized_data)
        
        # Agrupar por campaña
        grouped_by_campaign = processor.group_by_campaign(normalized_data)
        
        # Filtrar top performers
        top_performers = processor.filter_by_performance(
            normalized_data,
            min_ctr=1.0,  # CTR mínimo 1%
            max_cpc=10.0  # CPC máximo $10
        )
        
        return {
            "normalized_records": len(normalized_data),
            "total_campaigns": len(grouped_by_campaign),
            "top_performers": len(top_performers),
            "metrics": {
                "total_impressions": metrics.total_impressions,
                "total_clicks": metrics.total_clicks,
                "total_spend": metrics.total_spend,
                "total_conversions": metrics.total_conversions,
                "avg_ctr": metrics.avg_ctr,
                "avg_cpc": metrics.avg_cpc,
                "avg_cpa": metrics.avg_cpa,
                "roas": metrics.roas,
            }
        }
    
    @task(task_id="data_quality_check")
    def data_quality_check_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Data quality checks."""
        if extraction_result.get("skipped"):
            return {"skipped": True}
        
        if not global_config.enable_dq_checks or not UTILS_AVAILABLE:
            return {"skipped": True}
        
        data = extraction_result.get("data", [])
        if not data:
            return {"skipped": True}
        
        dq_check = check_data_quality_campaigns(data, "facebook")
        
        return {
            "passed": dq_check.passed,
            "issues": dq_check.issues,
            "metrics": dq_check.metrics
        }
    
    @task(task_id="save_to_storage")
    def save_to_storage_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Guarda datos en storage."""
        if extraction_result.get("skipped"):
            return {"skipped": True}
        
        data = extraction_result.get("data", [])
        if not data:
            return {"saved": 0, "errors": 0}
        
        storage = get_storage(
            global_config.default_storage,
            postgres_conn_id=global_config.postgres_conn_id
        )
        
        result = storage.save_campaign_performance(
            data,
            "facebook_ads_performance"
        )
        
        logger.info(f"Guardados {result['saved']} registros, {result['errors']} errores")
        
        return result
    
    # Pipeline
    health = health_check_task()
    extracted = extract_with_cache_task()
    validated = validate_data_task(extracted)
    processed = process_data_task(extracted)
    dq_check = data_quality_check_task(extracted)
    saved = save_to_storage_task(extracted)
    
    # Dependencias
    extracted.set_upstream(health)
    validated.set_upstream(extracted)
    processed.set_upstream(extracted)
    dq_check.set_upstream(extracted)
    saved.set_upstream([validated, dq_check])


dag = facebook_ads_reporting_integrated()

