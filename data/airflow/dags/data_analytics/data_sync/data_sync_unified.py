"""
DAG de Airflow para sincronización unificada de datos entre CRM, ERP y hojas de cálculo
=======================================================================================

Este DAG proporciona una solución completa para sincronizar datos entre:
- CRM (HubSpot, Salesforce, etc.)
- ERP (QuickBooks, SAP, etc.)  
- Hojas de Cálculo (Google Sheets, Excel)
- Bases de Datos

Características:
- Sincronización bidireccional configurable
- Múltiples conectores soportados
- Validación y transformación de datos
- Circuit breaker y retry logic
- Auditoría completa
- Monitoreo y alertas
"""
from __future__ import annotations

from datetime import timedelta, datetime
import logging
import os
import json
from typing import Dict, Any, List, Optional

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.param import Param
from airflow.exceptions import AirflowFailException

# Importar framework de integración
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'integrations'))

from sync_framework import SyncFramework, SyncConfig, SyncDirection, SyncStatus
from connectors import SyncRecord

logger = logging.getLogger(__name__)

# Configuración de conexiones
POSTGRES_CONN_ID = os.getenv("SYNC_POSTGRES_CONN_ID", "postgres_default")
DB_CONNECTION_STRING = os.getenv(
    "SYNC_DB_CONNECTION_STRING",
    None  # Se construye desde Airflow connection si no se proporciona
)

# Configuración por defecto
DEFAULT_BATCH_SIZE = int(os.getenv("SYNC_BATCH_SIZE", "50"))
DEFAULT_RETRY_ATTEMPTS = int(os.getenv("SYNC_RETRY_ATTEMPTS", "3"))
DEFAULT_CIRCUIT_BREAKER_THRESHOLD = int(os.getenv("SYNC_CB_THRESHOLD", "5"))


@dag(
    'data_sync_unified',
    default_args={
        'owner': 'data-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
        'retry_exponential_backoff': True,
        'max_retry_delay': timedelta(minutes=15),
    },
    description='Sincronización unificada de datos entre CRM, ERP y hojas de cálculo',
    schedule=None,  # Manual trigger o schedule desde configuración
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['integration', 'sync', 'crm', 'erp', 'sheets'],
    params={
        'sync_config': Param(
            {},
            type='object',
            description='Configuración JSON de sincronización'
        ),
        'dry_run': Param(
            False,
            type='boolean',
            description='Ejecutar en modo dry-run (sin escribir cambios)'
        ),
        'source_type': Param(
            'hubspot',
            type='string',
            description='Tipo de conector fuente (hubspot, quickbooks, google_sheets)'
        ),
        'target_type': Param(
            'quickbooks',
            type='string',
            description='Tipo de conector destino'
        ),
        'direction': Param(
            'bidirectional',
            type='string',
            description='Dirección de sincronización (source_to_target, target_to_source, bidirectional)'
        ),
        'batch_size': Param(
            DEFAULT_BATCH_SIZE,
            type='integer',
            minimum=1,
            maximum=1000,
            description='Tamaño de batch para procesamiento'
        ),
    },
    max_active_runs=3,
    dagrun_timeout=timedelta(hours=2),
)
def data_sync_unified():
    """Pipeline de sincronización unificada de datos"""
    
    @task
    def get_db_connection_string() -> str:
        """Obtiene string de conexión a base de datos"""
        if DB_CONNECTION_STRING:
            return DB_CONNECTION_STRING
        
        try:
            hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = hook.get_conn()
            
            # Construir connection string
            db_info = conn.get_dsn_parameters()
            conn_str = (
                f"postgresql://{db_info.get('user')}:{db_info.get('password')}@"
                f"{db_info.get('host')}:{db_info.get('port')}/{db_info.get('dbname')}"
            )
            conn.close()
            return conn_str
        except Exception as e:
            logger.warning(f"No se pudo obtener conexión desde Airflow: {e}")
            # Retornar string vacío si no hay conexión
            return ""
    
    @task
    def parse_sync_config(**context) -> Dict[str, Any]:
        """Parsea y valida configuración de sincronización"""
        params = context.get('params', {})
        sync_config = params.get('sync_config', {})
        
        # Si sync_config está vacío, construir desde parámetros individuales
        if not sync_config:
            sync_config = {
                'source_type': params.get('source_type', 'hubspot'),
                'target_type': params.get('target_type', 'quickbooks'),
                'direction': params.get('direction', 'bidirectional'),
                'batch_size': params.get('batch_size', DEFAULT_BATCH_SIZE),
            }
        
        # Validar configuración requerida
        required_fields = ['source_type', 'target_type']
        for field in required_fields:
            if field not in sync_config:
                raise ValueError(f"Campo requerido faltante: {field}")
        
        # Obtener credenciales desde variables de entorno o Airflow connections
        source_type = sync_config['source_type']
        target_type = sync_config['target_type']
        
        # Configurar source
        source_config = sync_config.get('source_config', {})
        if not source_config:
            source_config = _get_connector_config(source_type)
        
        # Configurar target
        target_config = sync_config.get('target_config', {})
        if not target_config:
            target_config = _get_connector_config(target_type)
        
        sync_config['source_config'] = source_config
        sync_config['target_config'] = target_config
        
        logger.info(f"Configuración parseada: {json.dumps(sync_config, indent=2)}")
        return sync_config
    
    @task
    def validate_connections(sync_config: Dict[str, Any]) -> Dict[str, Any]:
        """Valida que las conexiones a los sistemas estén funcionando"""
        from connectors import create_connector
        
        results = {}
        
        # Validar source
        try:
            source_connector = create_connector(
                sync_config['source_type'],
                sync_config['source_config']
            )
            source_health = source_connector.health_check()
            results['source'] = source_health
            logger.info(f"Source health check: {source_health}")
        except Exception as e:
            results['source'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error(f"Error en health check de source: {e}")
        
        # Validar target
        try:
            target_connector = create_connector(
                sync_config['target_type'],
                sync_config['target_config']
            )
            target_health = target_connector.health_check()
            results['target'] = target_health
            logger.info(f"Target health check: {target_health}")
        except Exception as e:
            results['target'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
            logger.error(f"Error en health check de target: {e}")
        
        # Verificar si ambos están saludables
        if results['source'].get('status') != 'healthy':
            raise AirflowFailException(f"Source connector no saludable: {results['source']}")
        if results['target'].get('status') != 'healthy':
            raise AirflowFailException(f"Target connector no saludable: {results['target']}")
        
        return results
    
    @task
    def execute_sync(
        db_connection_string: str,
        sync_config: Dict[str, Any],
        **context
    ) -> Dict[str, Any]:
        """Ejecuta la sincronización de datos"""
        params = context.get('params', {})
        dry_run = params.get('dry_run', False)
        
        # Crear framework de sincronización
        framework = SyncFramework(db_connection_string=db_connection_string)
        
        # Mapear dirección
        direction_map = {
            'source_to_target': SyncDirection.SOURCE_TO_TARGET,
            'target_to_source': SyncDirection.TARGET_TO_SOURCE,
            'bidirectional': SyncDirection.BIDIRECTIONAL,
        }
        direction = direction_map.get(
            sync_config.get('direction', 'bidirectional'),
            SyncDirection.BIDIRECTIONAL
        )
        
        # Crear configuración de sincronización
        config = SyncConfig(
            sync_id=f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            source_connector_type=sync_config['source_type'],
            source_config=sync_config['source_config'],
            target_connector_type=sync_config['target_type'],
            target_config=sync_config['target_config'],
            direction=direction,
            batch_size=sync_config.get('batch_size', DEFAULT_BATCH_SIZE),
            retry_attempts=DEFAULT_RETRY_ATTEMPTS,
            enable_circuit_breaker=True,
            circuit_breaker_threshold=DEFAULT_CIRCUIT_BREAKER_THRESHOLD,
            enable_caching=True,
            enable_validation=True,
            enable_audit=True,
            conflict_resolution=sync_config.get('conflict_resolution', 'source_wins'),
            filters=sync_config.get('filters'),
            metadata=sync_config.get('metadata', {})
        )
        
        # Ejecutar sincronización
        logger.info(f"Iniciando sincronización: {config.sync_id}")
        result = framework.sync(config, dry_run=dry_run)
        
        # Convertir resultado a diccionario para XCom
        result_dict = result.to_dict()
        
        logger.info(f"Sincronización completada: {result_dict}")
        
        # Verificar si hubo errores críticos
        if result.status == SyncStatus.FAILED and result.successful == 0:
            raise AirflowFailException(f"Sincronización falló completamente: {result_dict}")
        
        return result_dict
    
    @task
    def generate_report(sync_result: Dict[str, Any], **context) -> Dict[str, Any]:
        """Genera reporte de sincronización"""
        report = {
            'sync_id': sync_result.get('sync_id'),
            'status': sync_result.get('status'),
            'summary': {
                'total': sync_result.get('total_records', 0),
                'successful': sync_result.get('successful', 0),
                'failed': sync_result.get('failed', 0),
                'conflicted': sync_result.get('conflicted', 0),
                'skipped': sync_result.get('skipped', 0),
            },
            'performance': {
                'duration_seconds': sync_result.get('duration_seconds', 0),
                'records_per_second': (
                    sync_result.get('total_records', 0) / sync_result.get('duration_seconds', 1)
                    if sync_result.get('duration_seconds', 0) > 0 else 0
                ),
            },
            'errors': sync_result.get('errors', []),
            'timestamp': datetime.now().isoformat(),
        }
        
        # Log del reporte
        logger.info(f"Reporte de sincronización: {json.dumps(report, indent=2)}")
        
        return report
    
    @task
    def send_notifications(
        sync_result: Dict[str, Any],
        report: Dict[str, Any],
        **context
    ) -> Dict[str, Any]:
        """Envía notificaciones sobre el resultado de la sincronización"""
        try:
            from data.airflow.plugins.etl_notifications import notify_slack
            
            status = sync_result.get('status')
            summary = report.get('summary', {})
            
            if status == 'completed':
                message = (
                    f":white_check_mark: Sincronización completada exitosamente\n"
                    f"Total: {summary.get('total', 0)}, "
                    f"Exitosos: {summary.get('successful', 0)}, "
                    f"Fallidos: {summary.get('failed', 0)}"
                )
            elif status == 'partial':
                message = (
                    f":warning: Sincronización completada parcialmente\n"
                    f"Total: {summary.get('total', 0)}, "
                    f"Exitosos: {summary.get('successful', 0)}, "
                    f"Fallidos: {summary.get('failed', 0)}"
                )
            else:
                message = (
                    f":x: Sincronización falló\n"
                    f"Total: {summary.get('total', 0)}, "
                    f"Exitosos: {summary.get('successful', 0)}, "
                    f"Fallidos: {summary.get('failed', 0)}"
                )
            
            notify_slack(message)
            logger.info("Notificación enviada")
            
            return {'notified': True, 'message': message}
        except Exception as e:
            logger.warning(f"No se pudo enviar notificación: {e}")
            return {'notified': False, 'error': str(e)}
    
    # Pipeline
    db_conn_str = get_db_connection_string()
    config = parse_sync_config()
    health_checks = validate_connections(config)
    sync_result = execute_sync(db_conn_str, config)
    report = generate_report(sync_result)
    notifications = send_notifications(sync_result, report)


def _get_connector_config(connector_type: str) -> Dict[str, Any]:
    """Obtiene configuración de conector desde variables de entorno"""
    config = {}
    
    if connector_type == 'hubspot':
        config = {
            'name': 'hubspot',
            'api_token': os.getenv('HUBSPOT_API_TOKEN', ''),
        }
    
    elif connector_type == 'quickbooks':
        config = {
            'name': 'quickbooks',
            'access_token': os.getenv('QUICKBOOKS_ACCESS_TOKEN', ''),
            'realm_id': os.getenv('QUICKBOOKS_REALM_ID', ''),
            'base_url': os.getenv(
                'QUICKBOOKS_BASE_URL',
                'https://sandbox-quickbooks.api.intuit.com'
            ),
        }
    
    elif connector_type == 'google_sheets':
        config = {
            'name': 'google_sheets',
            'credentials_json': os.getenv('GOOGLE_SHEETS_CREDENTIALS_JSON', ''),
            'credentials_path': os.getenv('GOOGLE_SHEETS_CREDENTIALS_PATH', ''),
            'spreadsheet_id': os.getenv('GOOGLE_SHEETS_SPREADSHEET_ID', ''),
            'sheet_name': os.getenv('GOOGLE_SHEETS_SHEET_NAME', 'Sheet1'),
        }
    
    return config


# Crear instancia del DAG
dag_instance = data_sync_unified()


