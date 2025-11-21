"""
DAG avanzado que demuestra todas las funcionalidades mejoradas:

- Monitoreo y alertas
- Batch processing
- Validación avanzada
- Data quality checks
- Performance tracking
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
from ads_reporting.processors import CampaignProcessor
from ads_reporting.validators import validate_campaign_data
from ads_reporting.monitoring import (
    monitor_extraction,
    DataQualityMonitor,
    get_alert_manager,
)
from ads_reporting.batch_processor import BatchProcessor
from ads_reporting.integration import extract_and_store
from ads_reporting.config import get_config
from ads_reporting.helpers import get_date_range

logger = logging.getLogger(__name__)

try:
    from ads_reporting_utils import (
        check_api_credentials,
        check_database_connection,
        check_data_quality_campaigns,
    )
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False


@dag(
    dag_id="facebook_ads_reporting_advanced",
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
        "enable_monitoring": Param(True, type="boolean"),
        "enable_batch_processing": Param(True, type="boolean"),
        "chunk_size": Param(100, type="integer"),
    },
    tags=["marketing", "facebook-ads", "advanced", "monitoring"],
)
def facebook_ads_reporting_advanced():
    """
    DAG avanzado con todas las funcionalidades mejoradas.
    
    Características:
    - Health checks
    - Extracción con métricas
    - Monitoreo de rendimiento
    - Validación completa
    - Batch processing optimizado
    - Data quality monitoring
    - Alertas automáticas
    """
    
    global_config = get_config()
    
    fb_config = FacebookAdsConfig(
        access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN", ""),
        ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID", ""),
        api_version=os.environ.get("FACEBOOK_API_VERSION", "v18.0"),
    )
    
    @task(task_id="health_check")
    def health_check_task(**context) -> Dict[str, Any]:
        """Health checks completos."""
        if not UTILS_AVAILABLE:
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
        
        all_passed = all(c.status == "ok" for c in checks)
        
        if not all_passed:
            alert_manager = get_alert_manager()
            alert_manager.send_alert({
                "level": "error",
                "title": "Health Check Failed",
                "message": "Uno o más health checks fallaron",
                "platform": "facebook"
            })
        
        return {"status": "ok" if all_passed else "error", "checks": checks}
    
    @task(task_id="extract_with_monitoring")
    def extract_with_monitoring_task(**context) -> Dict[str, Any]:
        """Extrae datos con monitoreo de rendimiento."""
        import time
        
        params = context.get("params", {})
        enable_monitoring = params.get("enable_monitoring", True)
        
        date_start, date_stop = get_date_range(
            days_back=7,
            date_start=params.get("date_start"),
            date_stop=params.get("date_stop")
        )
        
        start_time = time.time()
        
        with FacebookAdsClient(fb_config) as client:
            extractor = FacebookExtractor(client)
            data = extractor.extract_campaign_performance(
                date_start, date_stop,
                breakdowns=["audience_type", "region"]
            )
        
        duration_ms = (time.time() - start_time) * 1000
        
        # Monitoreo automático
        alerts = []
        if enable_monitoring:
            alerts = monitor_extraction(
                platform="facebook",
                records_extracted=len(data),
                duration_ms=duration_ms,
                errors=0
            )
        
        return {
            "records_extracted": len(data),
            "duration_ms": duration_ms,
            "date_start": date_start,
            "date_stop": date_stop,
            "data": data,
            "alerts_generated": len(alerts)
        }
    
    @task(task_id="validate_data")
    def validate_data_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Validación completa de datos."""
        data = extraction_result.get("data", [])
        if not data:
            return {"valid": False, "errors": ["No hay datos"]}
        
        # Validación completa
        result = validate_campaign_data(
            data,
            strict=global_config.strict_validation
        )
        
        # Si hay errores críticos, generar alerta
        if not result.valid and result.errors:
            alert_manager = get_alert_manager()
            alert_manager.send_alert({
                "level": "error",
                "title": "Validación Fallida",
                "message": f"{len(result.errors)} errores de validación encontrados",
                "platform": "facebook",
                "details": {"error_count": len(result.errors)}
            })
        
        return {
            "valid": result.valid,
            "errors": result.errors[:10],  # Limitar a 10
            "warnings": result.warnings[:10],
            "metrics": result.metrics
        }
    
    @task(task_id="data_quality_monitoring")
    def data_quality_monitoring_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Monitoreo de calidad de datos."""
        data = extraction_result.get("data", [])
        if not data:
            return {"alerts": []}
        
        monitor = DataQualityMonitor("facebook")
        alerts = monitor.check_data_quality(data, expected_min_records=1)
        
        # Enviar alertas
        if alerts:
            alert_manager = get_alert_manager()
            alert_manager.send_batch_alerts(alerts)
        
        return {
            "alerts_generated": len(alerts),
            "alerts": [a.to_dict() for a in alerts[:5]]
        }
    
    @task(task_id="batch_process")
    def batch_process_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Procesamiento por lotes optimizado."""
        import time
        
        params = context.get("params", {})
        enable_batch = params.get("enable_batch_processing", True)
        chunk_size = params.get("chunk_size", 100)
        
        data = extraction_result.get("data", [])
        if not data or not enable_batch:
            return {"processed": len(data), "skipped": True}
        
        start_time = time.time()
        
        processor = CampaignProcessor()
        
        def process_chunk(chunk: list) -> list:
            """Procesa un chunk de datos."""
            normalized = processor.normalize(chunk)
            return normalized
        
        batch_processor = BatchProcessor(
            chunk_size=chunk_size,
            max_workers=5
        )
        
        result = batch_processor.process_in_chunks(data, process_chunk)
        
        duration_ms = (time.time() - start_time) * 1000
        
        logger.info(
            f"Batch processing: {result.successful}/{len(data)} procesados, "
            f"throughput: {result.throughput:.2f} items/s"
        )
        
        return {
            "total": result.total,
            "processed": result.processed,
            "successful": result.successful,
            "failed": result.failed,
            "duration_ms": duration_ms,
            "throughput": result.throughput,
            "success_rate": result.success_rate
        }
    
    @task(task_id="save_to_storage")
    def save_to_storage_task(extraction_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Guarda datos en storage."""
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
        
        # Si hay muchos errores, generar alerta
        if result.get("errors", 0) > len(data) * 0.1:  # Más del 10%
            alert_manager = get_alert_manager()
            alert_manager.send_alert({
                "level": "warning",
                "title": "Errores en almacenamiento",
                "message": f"{result['errors']} errores al guardar {len(data)} registros",
                "platform": "facebook"
            })
        
        return result
    
    # Pipeline
    health = health_check_task()
    extracted = extract_with_monitoring_task()
    validated = validate_data_task(extracted)
    dq_monitored = data_quality_monitoring_task(extracted)
    batch_processed = batch_process_task(extracted)
    saved = save_to_storage_task(extracted)
    
    # Dependencias
    extracted.set_upstream(health)
    validated.set_upstream(extracted)
    dq_monitored.set_upstream(extracted)
    batch_processed.set_upstream(extracted)
    saved.set_upstream([validated, dq_monitored])


dag = facebook_ads_reporting_advanced()

