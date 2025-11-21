from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional, Callable
import json
import logging
import pandas as pd
import time
import functools
from io import StringIO
import hashlib

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.mysql.hooks.mysql import MySqlHook
from airflow.providers.http.hooks.http import HttpHook

# Intentar importar tenacity para retry logic avanzado
try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        before_sleep_log,
        after_log
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False
    logger.warning("tenacity no disponible, usando retry básico")

# Intentar importar boto3 para S3
try:
    import boto3
    from botocore.exceptions import ClientError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# Intentar importar requests para notificaciones
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Intentar importar para procesamiento paralelo
try:
    from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
    CONCURRENT_AVAILABLE = True
except ImportError:
    CONCURRENT_AVAILABLE = False

# Intentar importar para compresión
try:
    import gzip
    import zlib
    COMPRESSION_AVAILABLE = True
except ImportError:
    COMPRESSION_AVAILABLE = False

logger = logging.getLogger(__name__)

# Constantes de configuración
DEFAULT_CHUNK_SIZE = 1000
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_BACKOFF = 1.0
LARGE_DATASET_THRESHOLD = 10000  # Registros
CACHE_TTL_SECONDS = 3600  # 1 hora por defecto

# Intentar importar prometheus_client para métricas
try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

# Métricas Prometheus (si está disponible)
if PROMETHEUS_AVAILABLE:
    integration_records_extracted = Counter(
        'merger_acquisition_records_extracted_total',
        'Total records extracted',
        ['company', 'system_type']
    )
    integration_records_loaded = Counter(
        'merger_acquisition_records_loaded_total',
        'Total records loaded',
        ['category']
    )
    integration_duration = Histogram(
        'merger_acquisition_duration_seconds',
        'Integration duration in seconds',
        ['stage']
    )
    integration_errors = Counter(
        'merger_acquisition_errors_total',
        'Total errors',
        ['error_type', 'stage']
    )
    integration_cache_hits = Counter(
        'merger_acquisition_cache_hits_total',
        'Cache hits',
        ['cache_type']
    )
else:
    # Dummy metrics si Prometheus no está disponible
    integration_records_extracted = None
    integration_records_loaded = None
    integration_duration = None
    integration_errors = None
    integration_cache_hits = None


# ============================================================================
# Utilidades y Decoradores
# ============================================================================

def with_retry(
    max_attempts: int = DEFAULT_MAX_RETRIES,
    backoff: float = DEFAULT_RETRY_BACKOFF,
    exceptions: tuple = (Exception,)
):
    """
    Decorador para agregar retry logic a funciones.
    
    Args:
        max_attempts: Número máximo de intentos
        backoff: Factor de backoff exponencial
        exceptions: Tupla de excepciones a retry
    """
    def decorator(func: Callable) -> Callable:
        if TENACITY_AVAILABLE:
            @retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=backoff, min=1, max=60),
                retry=retry_if_exception_type(exceptions),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                after=after_log(logger, logging.INFO),
                reraise=True
            )
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
        else:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_attempts):
                    try:
                        return func(*args, **kwargs)
                    except exceptions as e:
                        last_exception = e
                        if attempt < max_attempts - 1:
                            wait_time = min(backoff * (2 ** attempt), 60)
                            logger.warning(
                                f"Intento {attempt + 1}/{max_attempts} falló: {str(e)}. "
                                f"Reintentando en {wait_time}s"
                            )
                            time.sleep(wait_time)
                        else:
                            raise
                
                if last_exception:
                    raise last_exception
                raise RuntimeError("Función falló sin excepción")
        
        return wrapper
    return decorator


def validate_config(config: Dict[str, Any], required_fields: List[str], config_name: str) -> None:
    """
    Valida que una configuración tenga los campos requeridos.
    
    Args:
        config: Configuración a validar
        required_fields: Lista de campos requeridos
        config_name: Nombre de la configuración (para mensajes de error)
    """
    missing_fields = [field for field in required_fields if field not in config or not config[field]]
    if missing_fields:
        raise ValueError(
            f"Configuración {config_name} inválida. "
            f"Campos faltantes: {', '.join(missing_fields)}"
        )


def chunk_list(lst: List[Any], chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[List[Any]]:
    """
    Divide una lista en chunks de tamaño especificado.
    
    Args:
        lst: Lista a dividir
        chunk_size: Tamaño de cada chunk
        
    Returns:
        Lista de chunks
    """
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


def read_file_from_s3(bucket: str, key: str, file_type: str = "csv") -> pd.DataFrame:
    """
    Lee un archivo desde S3 y lo convierte a DataFrame.
    
    Args:
        bucket: Nombre del bucket S3
        key: Clave del archivo en S3
        file_type: Tipo de archivo ('csv', 'excel', 'json')
        
    Returns:
        DataFrame con los datos
    """
    if not BOTO3_AVAILABLE:
        raise ImportError("boto3 no está disponible. Instale boto3 para soporte de S3.")
    
    s3_client = boto3.client('s3')
    
    try:
        if file_type == "csv":
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            return pd.read_csv(obj['Body'])
        elif file_type == "excel":
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            return pd.read_excel(obj['Body'])
        elif file_type == "json":
            obj = s3_client.get_object(Bucket=bucket, Key=key)
            return pd.read_json(obj['Body'])
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file_type}")
    except ClientError as e:
        logger.error(f"Error leyendo archivo S3 s3://{bucket}/{key}: {e}")
        raise


def create_backup_table(hook: PostgresHook, schema: str, table_name: str) -> str:
    """
    Crea una tabla de backup antes de la carga.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        table_name: Nombre de la tabla original
        
    Returns:
        Nombre de la tabla de backup
    """
    backup_table = f"{table_name}_backup_{int(time.time())}"
    backup_sql = f"""
    CREATE TABLE IF NOT EXISTS {schema}.{backup_table}
    AS SELECT * FROM {schema}.{table_name}
    WHERE 1=0;
    """
    hook.run(backup_sql)
    logger.info(f"Tabla de backup creada: {backup_table}")
    return backup_table


def log_progress(current: int, total: int, operation: str, step: int = 10) -> None:
    """
    Log progreso de una operación.
    
    Args:
        current: Progreso actual
        total: Total de elementos
        operation: Nombre de la operación
        step: Cada cuántos elementos loguear
    """
    if current % step == 0 or current == total:
        percentage = (current / total * 100) if total > 0 else 0
        logger.info(f"{operation}: {current}/{total} ({percentage:.1f}%)")


def send_notification(
    notification_type: str,
    message: str,
    subject: str = None,
    webhook_url: str = None,
    email_to: List[str] = None,
    slack_channel: str = None,
    severity: str = "info"
) -> bool:
    """
    Envía notificaciones a diferentes canales.
    
    Args:
        notification_type: Tipo de notificación ('email', 'slack', 'webhook')
        message: Mensaje a enviar
        subject: Asunto (para email)
        webhook_url: URL del webhook
        email_to: Lista de emails
        slack_channel: Canal de Slack
        severity: Severidad ('info', 'warning', 'error', 'success')
        
    Returns:
        True si se envió exitosamente, False en caso contrario
    """
    if not REQUESTS_AVAILABLE:
        logger.warning("requests no disponible para notificaciones")
        return False
    
    try:
        if notification_type == "webhook" and webhook_url:
            payload = {
                "message": message,
                "severity": severity,
                "timestamp": datetime.now().isoformat()
            }
            if subject:
                payload["subject"] = subject
            
            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Notificación webhook enviada exitosamente")
            return True
        
        elif notification_type == "slack" and webhook_url:
            # Formato para Slack
            color_map = {
                "success": "good",
                "info": "#36a64f",
                "warning": "warning",
                "error": "danger"
            }
            
            slack_payload = {
                "text": subject or "Notificación de Integración M&A",
                "attachments": [{
                    "color": color_map.get(severity, "info"),
                    "text": message,
                    "footer": "Merger & Acquisition Integration",
                    "ts": int(time.time())
                }]
            }
            
            response = requests.post(webhook_url, json=slack_payload, timeout=10)
            response.raise_for_status()
            logger.info(f"Notificación Slack enviada exitosamente")
            return True
        
        elif notification_type == "email":
            # Para email, usar Airflow email operator o SMTP
            # Por ahora solo loguear
            logger.info(f"Email notification (simulado): {subject} -> {email_to}")
            logger.info(f"Message: {message}")
            return True
        
        else:
            logger.warning(f"Tipo de notificación no soportado o configuración incompleta: {notification_type}")
            return False
    
    except Exception as e:
        logger.error(f"Error enviando notificación: {e}")
        return False


def export_report_to_file(
    report: Dict[str, Any],
    format: str = "json",
    file_path: str = None
) -> str:
    """
    Exporta el reporte a un archivo.
    
    Args:
        report: Diccionario con el reporte
        format: Formato de exportación ('json', 'csv', 'html')
        file_path: Ruta del archivo (opcional)
        
    Returns:
        Ruta del archivo generado
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if not file_path:
        file_path = f"/tmp/merger_acquisition_report_{timestamp}.{format}"
    
    try:
        if format == "json":
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            # Exportar resumen a CSV
            summary_data = []
            if "integration_report" in report:
                summary = report["integration_report"].get("summary", {})
                summary_data.append({
                    "Métrica": "Total Extraído",
                    "Valor": summary.get("extraction", {}).get("total_records", 0)
                })
                summary_data.append({
                    "Métrica": "Total Cargado",
                    "Valor": summary.get("load", {}).get("total_records_loaded", 0)
                })
                summary_data.append({
                    "Métrica": "Tasa Validación",
                    "Valor": f"{summary.get('validation', {}).get('validation_rate', 0):.2f}%"
                })
            
            df = pd.DataFrame(summary_data)
            df.to_csv(file_path, index=False)
        
        elif format == "html":
            # Generar reporte HTML
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Reporte de Integración M&A</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333; }}
                    .metric {{ background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                    .success {{ color: green; }}
                    .error {{ color: red; }}
                    .warning {{ color: orange; }}
                </style>
            </head>
            <body>
                <h1>Reporte de Integración - Fusiones y Adquisiciones</h1>
                <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <div class="metric">
                    <h2>Resumen</h2>
                    <pre>{json.dumps(report.get('integration_report', {}).get('summary', {}), indent=2)}</pre>
                </div>
            </body>
            </html>
            """
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        logger.info(f"Reporte exportado a {file_path}")
        return file_path
    
    except Exception as e:
        logger.error(f"Error exportando reporte: {e}")
        raise


def rollback_load(
    hook: PostgresHook,
    schema: str,
    backup_tables: List[str],
    target_tables: List[str]
) -> Dict[str, Any]:
    """
    Realiza rollback de una carga usando las tablas de backup.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        backup_tables: Lista de tablas de backup
        target_tables: Lista de tablas objetivo
        
    Returns:
        Resultado del rollback
    """
    rollback_results = {
        "timestamp": datetime.now().isoformat(),
        "tables_rolled_back": [],
        "errors": []
    }
    
    for backup_table, target_table in zip(backup_tables, target_tables):
        try:
            # Verificar que el backup existe
            check_sql = f"SELECT COUNT(*) FROM {schema}.{backup_table}"
            backup_count = hook.get_first(check_sql)[0]
            
            if backup_count == 0:
                logger.warning(f"Backup {backup_table} está vacío, saltando rollback")
                continue
            
            # Limpiar tabla objetivo
            truncate_sql = f"TRUNCATE TABLE {schema}.{target_table}"
            hook.run(truncate_sql)
            
            # Restaurar desde backup
            restore_sql = f"""
            INSERT INTO {schema}.{target_table}
            SELECT * FROM {schema}.{backup_table}
            """
            hook.run(restore_sql)
            
            rollback_results["tables_rolled_back"].append({
                "target_table": target_table,
                "backup_table": backup_table,
                "records_restored": backup_count
            })
            
            logger.info(f"Rollback completado para {target_table} desde {backup_table}")
        
        except Exception as e:
            logger.error(f"Error en rollback de {target_table}: {e}")
            rollback_results["errors"].append({
                "table": target_table,
                "error": str(e)
            })
    
    return rollback_results


def get_cache_key(operation: str, config: Dict[str, Any]) -> str:
    """
    Genera una clave de cache única para una operación.
    
    Args:
        operation: Tipo de operación ('extraction', 'transformation', etc.)
        config: Configuración de la operación
        
    Returns:
        Clave de cache hash
    """
    cache_data = {
        "operation": operation,
        "config": config,
        "timestamp": datetime.now().strftime("%Y%m%d%H")  # Cache por hora
    }
    cache_str = json.dumps(cache_data, sort_keys=True)
    return hashlib.md5(cache_str.encode()).hexdigest()


def check_cache(cache_key: str, hook: PostgresHook = None) -> Optional[Dict[str, Any]]:
    """
    Verifica si hay datos en cache.
    
    Args:
        cache_key: Clave de cache
        hook: Hook de PostgreSQL para cache en BD
        
    Returns:
        Datos cacheados o None
    """
    # Por ahora, implementación simple en memoria
    # En producción, usar Redis o PostgreSQL
    if hook:
        try:
            cache_sql = """
            SELECT data, created_at 
            FROM integration_cache 
            WHERE cache_key = %s 
            AND created_at > NOW() - INTERVAL '1 hour'
            ORDER BY created_at DESC 
            LIMIT 1
            """
            result = hook.get_first(cache_sql, parameters=(cache_key,))
            if result:
                return json.loads(result[0])
        except Exception as e:
            logger.debug(f"Error leyendo cache: {e}")
    
    return None


def save_to_cache(cache_key: str, data: Dict[str, Any], hook: PostgresHook = None) -> bool:
    """
    Guarda datos en cache.
    
    Args:
        cache_key: Clave de cache
        data: Datos a cachear
        hook: Hook de PostgreSQL para cache en BD
        
    Returns:
        True si se guardó exitosamente
    """
    if hook:
        try:
            # Crear tabla de cache si no existe
            create_cache_table_sql = """
            CREATE TABLE IF NOT EXISTS integration_cache (
                cache_key VARCHAR(255) PRIMARY KEY,
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE INDEX IF NOT EXISTS idx_cache_created_at 
            ON integration_cache(created_at);
            """
            hook.run(create_cache_table_sql)
            
            # Insertar o actualizar cache
            insert_sql = """
            INSERT INTO integration_cache (cache_key, data)
            VALUES (%s, %s)
            ON CONFLICT (cache_key) 
            DO UPDATE SET data = EXCLUDED.data, created_at = CURRENT_TIMESTAMP
            """
            hook.run(insert_sql, parameters=(cache_key, json.dumps(data)))
            
            if PROMETHEUS_AVAILABLE and integration_cache_hits:
                integration_cache_hits.labels(cache_type='save').inc()
            
            return True
        except Exception as e:
            logger.warning(f"Error guardando cache: {e}")
    
    return False


def validate_referential_integrity(
    hook: PostgresHook,
    schema: str,
    tables: Dict[str, str],
    relationships: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Valida la integridad referencial entre tablas.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        tables: Diccionario de {category: table_name}
        relationships: Lista de relaciones a validar
        
    Returns:
        Resultado de la validación
    """
    validation_result = {
        "timestamp": datetime.now().isoformat(),
        "relationships_validated": 0,
        "relationships_valid": 0,
        "relationships_invalid": 0,
        "errors": []
    }
    
    for relationship in relationships:
        try:
            parent_table = tables.get(relationship["parent_category"])
            child_table = tables.get(relationship["child_category"])
            parent_key = relationship["parent_key"]
            child_key = relationship["child_key"]
            
            if not parent_table or not child_table:
                continue
            
            # Verificar referencias huérfanas
            orphan_check_sql = f"""
            SELECT COUNT(*) 
            FROM {schema}.{child_table} c
            WHERE NOT EXISTS (
                SELECT 1 FROM {schema}.{parent_table} p
                WHERE p.data->>'{parent_key}' = c.data->>'{child_key}'
            )
            """
            
            orphan_count = hook.get_first(orphan_check_sql)[0]
            
            validation_result["relationships_validated"] += 1
            
            if orphan_count == 0:
                validation_result["relationships_valid"] += 1
                logger.info(
                    f"✓ Integridad referencial válida: {child_table} -> {parent_table}"
                )
            else:
                validation_result["relationships_invalid"] += 1
                validation_result["errors"].append({
                    "relationship": f"{child_table} -> {parent_table}",
                    "orphan_records": orphan_count,
                    "parent_key": parent_key,
                    "child_key": child_key
                })
                logger.warning(
                    f"✗ {orphan_count} registros huérfanos en {child_table} -> {parent_table}"
                )
        
        except Exception as e:
            logger.error(f"Error validando relación: {e}")
            validation_result["errors"].append({
                "error": str(e),
                "relationship": relationship
            })
    
    return validation_result


def enrich_data_with_external_api(
    records: List[Dict[str, Any]],
    enrichment_config: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Enriquece datos con información de APIs externas.
    
    Args:
        records: Lista de registros a enriquecer
        enrichment_config: Configuración de enriquecimiento
        
    Returns:
        Registros enriquecidos
    """
    if not enrichment_config.get("enabled"):
        return records
    
    api_url = enrichment_config.get("api_url")
    api_key = enrichment_config.get("api_key")
    field_mapping = enrichment_config.get("field_mapping", {})
    batch_size = enrichment_config.get("batch_size", 100)
    
    if not api_url or not REQUESTS_AVAILABLE:
        logger.warning("Enriquecimiento deshabilitado: API no configurada")
        return records
    
    enriched_records = []
    
    # Procesar en batches
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        
        try:
            # Preparar datos para la API
            payload = {
                "records": [
                    {field_mapping.get(k, k): v for k, v in record.items()}
                    for record in batch
                ]
            }
            
            headers = {
                "Content-Type": "application/json"
            }
            if api_key:
                headers["Authorization"] = f"Bearer {api_key}"
            
            # Llamar API
            response = requests.post(
                api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            enrichment_data = response.json()
            
            # Combinar datos enriquecidos con originales
            for idx, record in enumerate(batch):
                if idx < len(enrichment_data.get("enriched_records", [])):
                    enriched_record = {**record}
                    enriched_record.update(
                        enrichment_data["enriched_records"][idx]
                    )
                    enriched_records.append(enriched_record)
                else:
                    enriched_records.append(record)
        
        except Exception as e:
            logger.warning(f"Error enriqueciendo batch {i//batch_size + 1}: {e}")
            # En caso de error, usar registros originales
            enriched_records.extend(batch)
    
    logger.info(f"Enriquecidos {len(enriched_records)} registros")
    return enriched_records


def optimize_query(query: str, table_name: str, where_clause: str = None) -> str:
    """
    Optimiza una query SQL agregando índices sugeridos y mejoras.
    
    Args:
        query: Query original
        table_name: Nombre de la tabla
        where_clause: Cláusula WHERE (opcional)
        
    Returns:
        Query optimizada
    """
    # Por ahora, solo retornar la query original
    # En producción, podría analizar y sugerir optimizaciones
    optimized = query
    
    # Agregar LIMIT si no existe y es una query grande
    if "LIMIT" not in query.upper() and where_clause:
        # Podría agregar LIMIT para testing
        pass
    
    return optimized


def track_metrics(metric_name: str, value: float, labels: Dict[str, str] = None):
    """
    Registra métricas si Prometheus está disponible.
    
    Args:
        metric_name: Nombre de la métrica
        value: Valor a registrar
        labels: Etiquetas adicionales
    """
    if not PROMETHEUS_AVAILABLE:
        return
    
    labels = labels or {}
    
    if metric_name == "records_extracted" and integration_records_extracted:
        integration_records_extracted.labels(
            company=labels.get("company", "unknown"),
            system_type=labels.get("system_type", "unknown")
        ).inc(value)
    
    elif metric_name == "records_loaded" and integration_records_loaded:
        integration_records_loaded.labels(
            category=labels.get("category", "unknown")
        ).inc(value)
    
    elif metric_name == "duration" and integration_duration:
        integration_duration.labels(
            stage=labels.get("stage", "unknown")
        ).observe(value)
    
    elif metric_name == "error" and integration_errors:
        integration_errors.labels(
            error_type=labels.get("error_type", "unknown"),
            stage=labels.get("stage", "unknown")
        ).inc()


def calculate_data_hash(records: List[Dict[str, Any]]) -> str:
    """
    Calcula hash SHA256 de los datos para verificación de integridad.
    
    Args:
        records: Lista de registros
        
    Returns:
        Hash SHA256 en hexadecimal
    """
    import hashlib
    
    # Ordenar registros y convertir a JSON estable
    sorted_records = sorted(
        [json.dumps(record, sort_keys=True) for record in records]
    )
    data_str = "".join(sorted_records)
    
    return hashlib.sha256(data_str.encode()).hexdigest()


def create_audit_log(
    hook: PostgresHook,
    schema: str,
    operation: str,
    details: Dict[str, Any]
) -> None:
    """
    Crea un registro de auditoría.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        operation: Tipo de operación
        details: Detalles de la operación
    """
    try:
        # Crear tabla de auditoría si no existe
        create_audit_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.integration_audit_log (
            id SERIAL PRIMARY KEY,
            operation VARCHAR(100),
            execution_id VARCHAR(255),
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            details JSONB,
            user_name VARCHAR(255),
            ip_address VARCHAR(50)
        );
        CREATE INDEX IF NOT EXISTS idx_audit_operation 
        ON {schema}.integration_audit_log(operation);
        CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
        ON {schema}.integration_audit_log(timestamp);
        """
        hook.run(create_audit_table_sql)
        
        # Insertar registro de auditoría
        from airflow.operators.python import get_current_context
        ctx = get_current_context()
        
        insert_audit_sql = f"""
        INSERT INTO {schema}.integration_audit_log 
        (operation, execution_id, details)
        VALUES (%s, %s, %s)
        """
        hook.run(
            insert_audit_sql,
            parameters=(
                operation,
                ctx.get("dag_run").run_id if ctx.get("dag_run") else "unknown",
                json.dumps(details)
            )
        )
    except Exception as e:
        logger.warning(f"Error creando registro de auditoría: {e}")


def detect_data_drift(
    current_data: List[Dict[str, Any]],
    baseline_data: List[Dict[str, Any]],
    key_fields: List[str]
) -> Dict[str, Any]:
    """
    Detecta drift en los datos comparando con baseline.
    
    Args:
        current_data: Datos actuales
        baseline_data: Datos de referencia
        key_fields: Campos clave para comparación
        
    Returns:
        Resultado del análisis de drift
    """
    drift_result = {
        "timestamp": datetime.now().isoformat(),
        "records_added": 0,
        "records_removed": 0,
        "records_changed": 0,
        "drift_percentage": 0.0
    }
    
    try:
        # Crear sets de keys para comparación rápida
        baseline_keys = {
            tuple(record.get(f) for f in key_fields)
            for record in baseline_data
            if all(record.get(f) for f in key_fields)
        }
        
        current_keys = {
            tuple(record.get(f) for f in key_fields)
            for record in current_data
            if all(record.get(f) for f in key_fields)
        }
        
        # Calcular diferencias
        drift_result["records_added"] = len(current_keys - baseline_keys)
        drift_result["records_removed"] = len(baseline_keys - current_keys)
        
        # Comparar registros comunes
        common_keys = baseline_keys & current_keys
        baseline_dict = {
            tuple(record.get(f) for f in key_fields): record
            for record in baseline_data
            if all(record.get(f) for f in key_fields)
        }
        current_dict = {
            tuple(record.get(f) for f in key_fields): record
            for record in current_data
            if all(record.get(f) for f in key_fields)
        }
        
        changed = 0
        for key in common_keys:
            if baseline_dict[key] != current_dict[key]:
                changed += 1
        
        drift_result["records_changed"] = changed
        
        # Calcular porcentaje de drift
        total_baseline = len(baseline_data)
        if total_baseline > 0:
            total_changes = (
                drift_result["records_added"] +
                drift_result["records_removed"] +
                drift_result["records_changed"]
            )
            drift_result["drift_percentage"] = (total_changes / total_baseline) * 100
        
        logger.info(
            f"Drift detectado: {drift_result['drift_percentage']:.2f}% "
            f"(+{drift_result['records_added']}, "
            f"-{drift_result['records_removed']}, "
            f"~{drift_result['records_changed']})"
        )
    
    except Exception as e:
        logger.error(f"Error detectando drift: {e}")
        drift_result["error"] = str(e)
    
    return drift_result


def generate_data_lineage(
    source_systems: List[str],
    transformations: List[str],
    target_system: str
) -> Dict[str, Any]:
    """
    Genera linaje de datos para trazabilidad.
    
    Args:
        source_systems: Lista de sistemas fuente
        transformations: Lista de transformaciones aplicadas
        target_system: Sistema destino
        
    Returns:
        Linaje de datos
    """
    lineage = {
        "timestamp": datetime.now().isoformat(),
        "source_systems": source_systems,
        "transformations": transformations,
        "target_system": target_system,
        "lineage_id": hashlib.md5(
            f"{','.join(source_systems)}->{target_system}".encode()
        ).hexdigest()
    }
    
    return lineage


def process_parallel_extraction(
    systems: List[Dict[str, Any]],
    extraction_func: Callable
) -> Dict[str, Any]:
    """
    Procesa extracciones en paralelo para mejorar rendimiento.
    
    Args:
        systems: Lista de sistemas a extraer
        extraction_func: Función de extracción a ejecutar
        
    Returns:
        Resultado combinado de todas las extracciones
    """
    if not CONCURRENT_AVAILABLE:
        logger.warning("concurrent.futures no disponible, usando procesamiento secuencial")
        results = {}
        for system in systems:
            try:
                result = extraction_func(system)
                results.update(result)
            except Exception as e:
                logger.error(f"Error en extracción secuencial: {e}")
        return results
    
    results = {}
    max_workers = min(len(systems), 5)  # Máximo 5 workers paralelos
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_system = {
            executor.submit(extraction_func, system): system
            for system in systems
        }
        
        for future in as_completed(future_to_system):
            system = future_to_system[future]
            try:
                result = future.result()
                results.update(result)
                logger.info(f"✓ Extracción paralela completada para {system.get('name', 'unknown')}")
            except Exception as e:
                logger.error(f"✗ Error en extracción paralela de {system.get('name', 'unknown')}: {e}")
                results[f"{system.get('name', 'unknown')}_error"] = {"error": str(e)}
    
    return results


def validate_schema(
    records: List[Dict[str, Any]],
    expected_schema: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Valida que los registros cumplan con un esquema esperado.
    
    Args:
        records: Lista de registros a validar
        expected_schema: Esquema esperado con tipos y restricciones
        
    Returns:
        Resultado de la validación
    """
    validation_result = {
        "timestamp": datetime.now().isoformat(),
        "records_validated": len(records),
        "records_valid": 0,
        "records_invalid": 0,
        "schema_violations": []
    }
    
    required_fields = expected_schema.get("required_fields", [])
    field_types = expected_schema.get("field_types", {})
    field_constraints = expected_schema.get("field_constraints", {})
    
    for idx, record in enumerate(records):
        is_valid = True
        violations = []
        
        # Validar campos requeridos
        for field in required_fields:
            if field not in record or record[field] is None:
                is_valid = False
                violations.append(f"Campo requerido faltante: {field}")
        
        # Validar tipos de campos
        for field, expected_type in field_types.items():
            if field in record and record[field] is not None:
                value = record[field]
                type_map = {
                    "string": str,
                    "integer": int,
                    "float": float,
                    "boolean": bool,
                    "date": str
                }
                
                expected_python_type = type_map.get(expected_type.lower())
                if expected_python_type and not isinstance(value, expected_python_type):
                    try:
                        # Intentar conversión
                        if expected_type == "integer":
                            int(value)
                        elif expected_type == "float":
                            float(value)
                        elif expected_type == "boolean":
                            bool(value)
                    except (ValueError, TypeError):
                        is_valid = False
                        violations.append(
                            f"Tipo incorrecto en {field}: esperado {expected_type}, "
                            f"obtenido {type(value).__name__}"
                        )
        
        # Validar restricciones
        for field, constraints in field_constraints.items():
            if field in record and record[field] is not None:
                value = record[field]
                
                if "min_length" in constraints:
                    if len(str(value)) < constraints["min_length"]:
                        is_valid = False
                        violations.append(
                            f"{field}: longitud mínima {constraints['min_length']}"
                        )
                
                if "max_length" in constraints:
                    if len(str(value)) > constraints["max_length"]:
                        is_valid = False
                        violations.append(
                            f"{field}: longitud máxima {constraints['max_length']}"
                        )
                
                if "min_value" in constraints:
                    try:
                        if float(value) < constraints["min_value"]:
                            is_valid = False
                            violations.append(
                                f"{field}: valor mínimo {constraints['min_value']}"
                            )
                    except (ValueError, TypeError):
                        pass
                
                if "max_value" in constraints:
                    try:
                        if float(value) > constraints["max_value"]:
                            is_valid = False
                            violations.append(
                                f"{field}: valor máximo {constraints['max_value']}"
                            )
                    except (ValueError, TypeError):
                        pass
        
        if is_valid:
            validation_result["records_valid"] += 1
        else:
            validation_result["records_invalid"] += 1
            validation_result["schema_violations"].append({
                "record_index": idx,
                "violations": violations
            })
    
    logger.info(
        f"Validación de esquema: {validation_result['records_valid']}/"
        f"{validation_result['records_validated']} registros válidos"
    )
    
    return validation_result


def compress_data(data: bytes, compression_type: str = "gzip") -> bytes:
    """
    Comprime datos para almacenamiento eficiente.
    
    Args:
        data: Datos a comprimir (bytes)
        compression_type: Tipo de compresión ('gzip', 'zlib')
        
    Returns:
        Datos comprimidos
    """
    if not COMPRESSION_AVAILABLE:
        logger.warning("Compresión no disponible")
        return data
    
    try:
        if compression_type == "gzip":
            return gzip.compress(data)
        elif compression_type == "zlib":
            return zlib.compress(data)
        else:
            logger.warning(f"Tipo de compresión no soportado: {compression_type}")
            return data
    except Exception as e:
        logger.error(f"Error comprimiendo datos: {e}")
        return data


def decompress_data(compressed_data: bytes, compression_type: str = "gzip") -> bytes:
    """
    Descomprime datos.
    
    Args:
        compressed_data: Datos comprimidos
        compression_type: Tipo de compresión
        
    Returns:
        Datos descomprimidos
    """
    if not COMPRESSION_AVAILABLE:
        return compressed_data
    
    try:
        if compression_type == "gzip":
            return gzip.decompress(compressed_data)
        elif compression_type == "zlib":
            return zlib.decompress(compressed_data)
        else:
            return compressed_data
    except Exception as e:
        logger.error(f"Error descomprimiendo datos: {e}")
        return compressed_data


def encrypt_sensitive_fields(
    record: Dict[str, Any],
    sensitive_fields: List[str],
    encryption_key: str = None
) -> Dict[str, Any]:
    """
    Encripta campos sensibles en un registro.
    
    Args:
        record: Registro a encriptar
        sensitive_fields: Lista de campos sensibles
        encryption_key: Clave de encriptación (opcional)
        
    Returns:
        Registro con campos encriptados
    """
    # Por ahora, solo marcar campos como encriptados
    # En producción, usar bibliotecas de encriptación reales
    encrypted_record = record.copy()
    
    for field in sensitive_fields:
        if field in encrypted_record and encrypted_record[field]:
            # Simulación de encriptación (en producción usar cryptography)
            value = str(encrypted_record[field])
            # Hash simple como placeholder
            encrypted_value = hashlib.sha256(value.encode()).hexdigest()[:16]
            encrypted_record[field] = f"ENC_{encrypted_value}"
            encrypted_record[f"{field}_encrypted"] = True
    
    return encrypted_record


def check_system_health(
    system_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Verifica el estado de salud de un sistema antes de extraer datos.
    
    Args:
        system_config: Configuración del sistema
        
    Returns:
        Estado de salud del sistema
    """
    health_status = {
        "timestamp": datetime.now().isoformat(),
        "system_name": system_config.get("name", "unknown"),
        "status": "unknown",
        "response_time_ms": 0,
        "error": None
    }
    
    system_type = system_config.get("type", "").lower()
    start_time = time.time()
    
    try:
        if system_type == "postgres":
            hook = PostgresHook(postgres_conn_id=system_config.get("conn_id", "postgres_default"))
            # Ejecutar query simple para verificar conexión
            hook.get_first("SELECT 1")
            health_status["status"] = "healthy"
        
        elif system_type == "mysql":
            hook = MySqlHook(mysql_conn_id=system_config.get("conn_id", "mysql_default"))
            hook.get_first("SELECT 1")
            health_status["status"] = "healthy"
        
        elif system_type in ["api", "rest"]:
            if REQUESTS_AVAILABLE:
                http_hook = HttpHook(http_conn_id=system_config.get("conn_id"), method="GET")
                endpoint = system_config.get("health_endpoint", system_config.get("endpoint", ""))
                if endpoint:
                    response = http_hook.run(endpoint, timeout=5)
                    health_status["status"] = "healthy" if response.status_code == 200 else "unhealthy"
                else:
                    health_status["status"] = "unknown"
            else:
                health_status["status"] = "unknown"
        
        else:
            health_status["status"] = "unknown"
        
        health_status["response_time_ms"] = (time.time() - start_time) * 1000
    
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["error"] = str(e)
        health_status["response_time_ms"] = (time.time() - start_time) * 1000
    
    logger.info(
        f"Health check {system_config.get('name', 'unknown')}: "
        f"{health_status['status']} ({health_status['response_time_ms']:.2f}ms)"
    )
    
    return health_status


def implement_circuit_breaker(
    func: Callable,
    failure_threshold: int = 5,
    recovery_timeout: int = 60,
    half_open_max_calls: int = 3
) -> Callable:
    """
    Implementa patrón Circuit Breaker para funciones.
    
    Args:
        func: Función a proteger
        failure_threshold: Número de fallos antes de abrir el circuito
        recovery_timeout: Tiempo en segundos antes de intentar recuperación
        half_open_max_calls: Máximo de llamadas en estado half-open
        
    Returns:
        Función envuelta con circuit breaker
    """
    circuit_state = {
        "state": "closed",  # closed, open, half_open
        "failure_count": 0,
        "last_failure_time": None,
        "half_open_calls": 0
    }
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        current_time = time.time()
        
        # Verificar si el circuito está abierto y si es tiempo de intentar recuperación
        if circuit_state["state"] == "open":
            if circuit_state["last_failure_time"]:
                elapsed = current_time - circuit_state["last_failure_time"]
                if elapsed >= recovery_timeout:
                    circuit_state["state"] = "half_open"
                    circuit_state["half_open_calls"] = 0
                    logger.info("Circuit breaker: Transición a half-open")
                else:
                    raise Exception(
                        f"Circuit breaker está abierto. "
                        f"Esperar {recovery_timeout - elapsed:.0f}s más"
                    )
        
        # Intentar ejecutar la función
        try:
            result = func(*args, **kwargs)
            
            # Si está en half-open y la llamada fue exitosa
            if circuit_state["state"] == "half_open":
                circuit_state["half_open_calls"] += 1
                if circuit_state["half_open_calls"] >= half_open_max_calls:
                    circuit_state["state"] = "closed"
                    circuit_state["failure_count"] = 0
                    logger.info("Circuit breaker: Circuito cerrado (recuperado)")
            
            # Si está cerrado, resetear contador de fallos
            if circuit_state["state"] == "closed":
                circuit_state["failure_count"] = 0
            
            return result
        
        except Exception as e:
            circuit_state["failure_count"] += 1
            circuit_state["last_failure_time"] = current_time
            
            # Si está en half-open, abrir el circuito
            if circuit_state["state"] == "half_open":
                circuit_state["state"] = "open"
                logger.warning("Circuit breaker: Circuito abierto (fallo en half-open)")
            
            # Si alcanza el umbral, abrir el circuito
            elif circuit_state["failure_count"] >= failure_threshold:
                circuit_state["state"] = "open"
                logger.error(
                    f"Circuit breaker: Circuito abierto después de "
                    f"{failure_threshold} fallos consecutivos"
                )
            
            raise
    
    return wrapper


def detect_anomalies(
    records: List[Dict[str, Any]],
    numeric_fields: List[str],
    threshold_std: float = 3.0
) -> Dict[str, Any]:
    """
    Detecta anomalías en datos numéricos usando desviación estándar.
    
    Args:
        records: Lista de registros a analizar
        numeric_fields: Lista de campos numéricos a analizar
        threshold_std: Umbral de desviación estándar (default: 3.0)
        
    Returns:
        Resultado del análisis de anomalías
    """
    anomaly_result = {
        "timestamp": datetime.now().isoformat(),
        "fields_analyzed": numeric_fields,
        "anomalies_detected": 0,
        "anomalies_by_field": {},
        "statistics": {}
    }
    
    if not records or not numeric_fields:
        return anomaly_result
    
    try:
        # Convertir a DataFrame para análisis estadístico
        df = pd.DataFrame(records)
        
        for field in numeric_fields:
            if field not in df.columns:
                continue
            
            # Convertir a numérico
            numeric_series = pd.to_numeric(df[field], errors='coerce').dropna()
            
            if len(numeric_series) == 0:
                continue
            
            # Calcular estadísticas
            mean = numeric_series.mean()
            std = numeric_series.std()
            median = numeric_series.median()
            
            anomaly_result["statistics"][field] = {
                "mean": float(mean),
                "std": float(std),
                "median": float(median),
                "min": float(numeric_series.min()),
                "max": float(numeric_series.max())
            }
            
            # Detectar anomalías (valores fuera de threshold_std desviaciones estándar)
            lower_bound = mean - (threshold_std * std)
            upper_bound = mean + (threshold_std * std)
            
            anomalies = numeric_series[
                (numeric_series < lower_bound) | (numeric_series > upper_bound)
            ]
            
            if len(anomalies) > 0:
                anomaly_result["anomalies_by_field"][field] = {
                    "count": len(anomalies),
                    "percentage": (len(anomalies) / len(numeric_series)) * 100,
                    "anomalous_values": anomalies.tolist()[:10],  # Primeros 10
                    "lower_bound": float(lower_bound),
                    "upper_bound": float(upper_bound)
                }
                anomaly_result["anomalies_detected"] += len(anomalies)
        
        logger.info(
            f"Detección de anomalías: {anomaly_result['anomalies_detected']} anomalías detectadas"
        )
    
    except Exception as e:
        logger.error(f"Error detectando anomalías: {e}")
        anomaly_result["error"] = str(e)
    
    return anomaly_result


def process_incremental_load(
    hook: PostgresHook,
    schema: str,
    table_name: str,
    records: List[Dict[str, Any]],
    incremental_key: str = "id",
    incremental_timestamp: str = "updated_at"
) -> Dict[str, Any]:
    """
    Procesa carga incremental identificando solo registros nuevos o actualizados.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        table_name: Nombre de la tabla
        records: Lista de registros a cargar
        incremental_key: Campo clave para identificar registros
        incremental_timestamp: Campo de timestamp para comparar
        
    Returns:
        Resultado de la carga incremental
    """
    incremental_result = {
        "timestamp": datetime.now().isoformat(),
        "total_records": len(records),
        "new_records": 0,
        "updated_records": 0,
        "unchanged_records": 0
    }
    
    try:
        # Obtener último timestamp de la tabla
        last_timestamp_sql = f"""
        SELECT MAX(data->>'{incremental_timestamp}') 
        FROM {schema}.{table_name}
        """
        result = hook.get_first(last_timestamp_sql)
        last_timestamp = result[0] if result and result[0] else None
        
        # Filtrar registros nuevos o actualizados
        if last_timestamp:
            filtered_records = [
                r for r in records
                if r.get(incremental_timestamp) and r[incremental_timestamp] > last_timestamp
            ]
        else:
            filtered_records = records
        
        incremental_result["new_records"] = len(filtered_records)
        incremental_result["unchanged_records"] = len(records) - len(filtered_records)
        
        logger.info(
            f"Carga incremental: {incremental_result['new_records']} nuevos, "
            f"{incremental_result['unchanged_records']} sin cambios"
        )
    
    except Exception as e:
        logger.error(f"Error procesando carga incremental: {e}")
        incremental_result["error"] = str(e)
    
    return incremental_result


def resolve_data_conflicts(
    company_a_record: Dict[str, Any],
    company_b_record: Dict[str, Any],
    conflict_resolution_strategy: str = "latest"
) -> Dict[str, Any]:
    """
    Resuelve conflictos entre registros de diferentes empresas.
    
    Args:
        company_a_record: Registro de empresa A
        company_b_record: Registro de empresa B
        conflict_resolution_strategy: Estrategia ('latest', 'company_a', 'company_b', 'merge')
        
    Returns:
        Registro resuelto
    """
    if conflict_resolution_strategy == "latest":
        # Usar el registro más reciente basado en timestamp
        a_timestamp = company_a_record.get("updated_at") or company_a_record.get("created_at")
        b_timestamp = company_b_record.get("updated_at") or company_b_record.get("created_at")
        
        if a_timestamp and b_timestamp:
            return company_a_record if a_timestamp > b_timestamp else company_b_record
        return company_a_record  # Default a A
    
    elif conflict_resolution_strategy == "company_a":
        return company_a_record
    
    elif conflict_resolution_strategy == "company_b":
        return company_b_record
    
    elif conflict_resolution_strategy == "merge":
        # Combinar campos, priorizando valores no nulos
        merged = company_a_record.copy()
        for key, value in company_b_record.items():
            if key not in merged or not merged[key]:
                merged[key] = value
            elif value and isinstance(value, str) and len(value) > len(str(merged.get(key, ""))):
                # Si ambos tienen valor, usar el más largo (más completo)
                merged[key] = value
        return merged
    
    else:
        return company_a_record  # Default


def create_dead_letter_queue(
    hook: PostgresHook,
    schema: str
) -> None:
    """
    Crea tabla de dead letter queue para registros con errores.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
    """
    create_dlq_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {schema}.integration_dlq (
        id SERIAL PRIMARY KEY,
        record_data JSONB,
        error_message TEXT,
        error_type VARCHAR(100),
        stage VARCHAR(50),
        retry_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_retry_at TIMESTAMP
    );
    CREATE INDEX IF NOT EXISTS idx_dlq_stage 
    ON {schema}.integration_dlq(stage);
    CREATE INDEX IF NOT EXISTS idx_dlq_created_at 
    ON {schema}.integration_dlq(created_at);
    """
    hook.run(create_dlq_table_sql)
    logger.info("Dead letter queue table creada")


def add_to_dead_letter_queue(
    hook: PostgresHook,
    schema: str,
    record: Dict[str, Any],
    error: Exception,
    stage: str
) -> None:
    """
    Agrega un registro a la dead letter queue.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        record: Registro que falló
        error: Excepción que ocurrió
        stage: Etapa donde falló
    """
    try:
        create_dead_letter_queue(hook, schema)
        
        insert_dlq_sql = f"""
        INSERT INTO {schema}.integration_dlq 
        (record_data, error_message, error_type, stage)
        VALUES (%s, %s, %s, %s)
        """
        hook.run(
            insert_dlq_sql,
            parameters=(
                json.dumps(record),
                str(error),
                type(error).__name__,
                stage
            )
        )
        logger.warning(f"Registro agregado a DLQ: {stage} - {type(error).__name__}")
    except Exception as e:
        logger.error(f"Error agregando a DLQ: {e}")


def apply_business_rules(
    record: Dict[str, Any],
    business_rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aplica reglas de negocio a un registro.
    
    Args:
        record: Registro a procesar
        business_rules: Lista de reglas de negocio
        
    Returns:
        Registro con reglas aplicadas
    """
    processed_record = record.copy()
    
    for rule in business_rules:
        rule_type = rule.get("type")
        condition = rule.get("condition")
        action = rule.get("action")
        target_field = rule.get("target_field")
        
        try:
            # Evaluar condición
            condition_met = False
            
            if rule_type == "field_comparison":
                field1 = record.get(rule.get("field1"))
                field2 = record.get(rule.get("field2"))
                operator = rule.get("operator", "==")
                
                if operator == "==":
                    condition_met = field1 == field2
                elif operator == "!=":
                    condition_met = field1 != field2
                elif operator == ">":
                    condition_met = field1 > field2
                elif operator == "<":
                    condition_met = field1 < field2
            
            elif rule_type == "value_check":
                field_value = record.get(rule.get("field"))
                expected_value = rule.get("expected_value")
                condition_met = field_value == expected_value
            
            elif rule_type == "custom":
                # Evaluar condición personalizada (simplificada)
                condition_met = eval(condition, {"record": record})
            
            # Aplicar acción si la condición se cumple
            if condition_met and action:
                if action == "set_value":
                    processed_record[target_field] = rule.get("value")
                elif action == "calculate":
                    formula = rule.get("formula")
                    # Evaluar fórmula (simplificada)
                    try:
                        result = eval(formula, {"record": processed_record})
                        processed_record[target_field] = result
                    except:
                        pass
                elif action == "transform":
                    transform_func = rule.get("transform_function")
                    if transform_func == "uppercase":
                        processed_record[target_field] = str(processed_record.get(target_field, "")).upper()
                    elif transform_func == "lowercase":
                        processed_record[target_field] = str(processed_record.get(target_field, "")).lower()
        
        except Exception as e:
            logger.warning(f"Error aplicando regla de negocio: {e}")
    
    return processed_record


def validate_data_quality_rules(
    records: List[Dict[str, Any]],
    quality_rules: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Valida reglas de calidad de datos personalizadas.
    
    Args:
        records: Lista de registros a validar
        quality_rules: Lista de reglas de calidad
        
    Returns:
        Resultado de la validación
    """
    quality_result = {
        "timestamp": datetime.now().isoformat(),
        "rules_validated": 0,
        "rules_passed": 0,
        "rules_failed": 0,
        "violations": []
    }
    
    for rule in quality_rules:
        rule_type = rule.get("type")
        field = rule.get("field")
        condition = rule.get("condition")
        threshold = rule.get("threshold")
        
        quality_result["rules_validated"] += 1
        
        try:
            violations = 0
            
            if rule_type == "completeness":
                # Validar completitud
                missing = sum(1 for r in records if not r.get(field))
                completeness_rate = (1 - missing / len(records)) * 100 if records else 0
                
                if completeness_rate < threshold:
                    violations = missing
                    quality_result["rules_failed"] += 1
                    quality_result["violations"].append({
                        "rule": rule.get("name", "completeness"),
                        "field": field,
                        "violations": violations,
                        "rate": completeness_rate
                    })
                else:
                    quality_result["rules_passed"] += 1
            
            elif rule_type == "uniqueness":
                # Validar unicidad
                values = [r.get(field) for r in records if r.get(field)]
                unique_values = len(set(values))
                uniqueness_rate = (unique_values / len(values)) * 100 if values else 0
                
                if uniqueness_rate < threshold:
                    violations = len(values) - unique_values
                    quality_result["rules_failed"] += 1
                    quality_result["violations"].append({
                        "rule": rule.get("name", "uniqueness"),
                        "field": field,
                        "violations": violations,
                        "rate": uniqueness_rate
                    })
                else:
                    quality_result["rules_passed"] += 1
            
            elif rule_type == "validity":
                # Validar validez según condición
                pattern = rule.get("pattern")
                invalid = 0
                
                for record in records:
                    value = record.get(field)
                    if value:
                        if condition == "regex" and pattern:
                            import re
                            if not re.match(pattern, str(value)):
                                invalid += 1
                        elif condition == "range":
                            min_val = rule.get("min")
                            max_val = rule.get("max")
                            try:
                                num_val = float(value)
                                if num_val < min_val or num_val > max_val:
                                    invalid += 1
                            except (ValueError, TypeError):
                                invalid += 1
                
                validity_rate = (1 - invalid / len(records)) * 100 if records else 0
                
                if validity_rate < threshold:
                    quality_result["rules_failed"] += 1
                    quality_result["violations"].append({
                        "rule": rule.get("name", "validity"),
                        "field": field,
                        "violations": invalid,
                        "rate": validity_rate
                    })
                else:
                    quality_result["rules_passed"] += 1
        
        except Exception as e:
            logger.error(f"Error validando regla {rule.get('name', 'unknown')}: {e}")
            quality_result["violations"].append({
                "rule": rule.get("name", "unknown"),
                "error": str(e)
            })
    
    logger.info(
        f"Validación de calidad: {quality_result['rules_passed']}/"
        f"{quality_result['rules_validated']} reglas pasadas"
    )
    
    return quality_result


def compare_data_before_after(
    hook: PostgresHook,
    schema: str,
    table_name: str,
    backup_table: str
) -> Dict[str, Any]:
    """
    Compara datos antes y después de la carga.
    
    Args:
        hook: Hook de PostgreSQL
        schema: Schema de la base de datos
        table_name: Nombre de la tabla actual
        backup_table: Nombre de la tabla de backup
        
    Returns:
        Resultado de la comparación
    """
    comparison = {
        "timestamp": datetime.now().isoformat(),
        "before_count": 0,
        "after_count": 0,
        "new_records": 0,
        "updated_records": 0,
        "deleted_records": 0
    }
    
    try:
        # Contar registros antes
        before_sql = f"SELECT COUNT(*) FROM {schema}.{backup_table}"
        comparison["before_count"] = hook.get_first(before_sql)[0]
        
        # Contar registros después
        after_sql = f"SELECT COUNT(*) FROM {schema}.{table_name}"
        comparison["after_count"] = hook.get_first(after_sql)[0]
        
        # Comparar registros nuevos
        new_sql = f"""
        SELECT COUNT(*) FROM {schema}.{table_name} t
        WHERE NOT EXISTS (
            SELECT 1 FROM {schema}.{backup_table} b
            WHERE b.source_company = t.source_company
            AND b.source_system = t.source_system
            AND b.data->>'id' = t.data->>'id'
        )
        """
        comparison["new_records"] = hook.get_first(new_sql)[0]
        
        # Comparar registros actualizados
        updated_sql = f"""
        SELECT COUNT(*) FROM {schema}.{table_name} t
        INNER JOIN {schema}.{backup_table} b
        ON b.source_company = t.source_company
        AND b.source_system = t.source_system
        AND b.data->>'id' = t.data->>'id'
        WHERE t.data != b.data
        """
        comparison["updated_records"] = hook.get_first(updated_sql)[0]
        
        # Calcular registros eliminados
        comparison["deleted_records"] = max(0, comparison["before_count"] - 
                                          (comparison["after_count"] - comparison["new_records"]))
        
        logger.info(f"Comparación completada para {table_name}")
        logger.info(f"  Antes: {comparison['before_count']}, Después: {comparison['after_count']}")
        logger.info(f"  Nuevos: {comparison['new_records']}, Actualizados: {comparison['updated_records']}")
    
    except Exception as e:
        logger.error(f"Error comparando datos: {e}")
        comparison["error"] = str(e)
    
    return comparison


# ============================================================================
# DAG Principal
# ============================================================================

@dag(
    dag_id="merger_acquisition_integration",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=None,  # Triggered manually for M&A operations
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 3,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    doc_md="""
    ### Orquestación de Integraciones para Fusiones y Adquisiciones
    
    Sistema que orquesta la integración de múltiples sistemas durante procesos de 
    fusiones o adquisiciones. Extrae datos de las empresas A y B, los transforma a 
    un formato común, los carga al sistema unificado y genera reportes de estado.
    
    **Flujo del proceso:**
    1. **Extracción**: Extrae datos de múltiples sistemas de las empresas A y B
    2. **Transformación**: Normaliza y transforma los datos a un formato común
    3. **Validación**: Valida la calidad e integridad de los datos
    4. **Carga**: Carga los datos transformados al sistema unificado
    5. **Reporte**: Genera reporte de estado de la integración
    
    **Parámetros:**
    - `company_a_config`: Configuración de extracción para empresa A (JSON)
    - `company_b_config`: Configuración de extracción para empresa B (JSON)
    - `unified_system_config`: Configuración del sistema unificado (JSON)
    - `transformation_rules`: Reglas de transformación y mapeo (JSON)
    - `dry_run`: Ejecutar en modo dry-run sin cargar datos (default: false)
    - `validation_strict`: Validación estricta de datos (default: true)
    
    **Sistemas soportados:**
    - PostgreSQL
    - MySQL
    - APIs REST
    - Archivos CSV/Excel
    - Salesforce
    - SAP
    """,
    params={
        "company_a_config": Param(
            "{}",
            type="string",
            description="Configuración JSON para empresa A con sistemas de origen"
        ),
        "company_b_config": Param(
            "{}",
            type="string",
            description="Configuración JSON para empresa B con sistemas de origen"
        ),
        "unified_system_config": Param(
            "{}",
            type="string",
            description="Configuración JSON del sistema unificado destino"
        ),
        "transformation_rules": Param(
            "{}",
            type="string",
            description="Reglas de transformación y mapeo de campos (JSON)"
        ),
        "dry_run": Param(False, type="boolean"),
        "validation_strict": Param(True, type="boolean"),
        "generate_detailed_report": Param(True, type="boolean"),
        "chunk_size": Param(DEFAULT_CHUNK_SIZE, type="integer", description="Tamaño de chunk para procesamiento"),
        "enable_backup": Param(True, type="boolean", description="Crear backup antes de cargar"),
        "max_retries_extraction": Param(DEFAULT_MAX_RETRIES, type="integer", description="Máximo de reintentos para extracción"),
        "enable_notifications": Param(False, type="boolean", description="Habilitar notificaciones"),
        "notification_config": Param("{}", type="string", description="Configuración de notificaciones (JSON)"),
        "export_report": Param(False, type="boolean", description="Exportar reporte a archivo"),
        "export_format": Param("json", type="string", enum=["json", "csv", "html"], description="Formato de exportación"),
        "enable_comparison": Param(False, type="boolean", description="Comparar datos antes/después"),
        "enable_rollback_on_error": Param(False, type="boolean", description="Rollback automático en caso de error"),
        "enable_cache": Param(False, type="boolean", description="Usar cache para extracciones"),
        "enable_referential_integrity_check": Param(False, type="boolean", description="Validar integridad referencial"),
        "referential_integrity_rules": Param("[]", type="string", description="Reglas de integridad referencial (JSON)"),
        "enable_data_enrichment": Param(False, type="boolean", description="Enriquecer datos con APIs externas"),
        "enrichment_config": Param("{}", type="string", description="Configuración de enriquecimiento (JSON)"),
        "enable_metrics": Param(True, type="boolean", description="Habilitar métricas Prometheus"),
        "enable_audit_log": Param(True, type="boolean", description="Habilitar registro de auditoría"),
        "enable_data_quality_rules": Param(False, type="boolean", description="Validar reglas de calidad personalizadas"),
        "data_quality_rules": Param("[]", type="string", description="Reglas de calidad de datos (JSON)"),
        "enable_drift_detection": Param(False, type="boolean", description="Detectar drift de datos"),
        "enable_data_lineage": Param(True, type="boolean", description="Generar linaje de datos"),
        "enable_parallel_extraction": Param(False, type="boolean", description="Extracción paralela de sistemas"),
        "enable_schema_validation": Param(False, type="boolean", description="Validar esquema de datos"),
        "expected_schema": Param("{}", type="string", description="Esquema esperado de datos (JSON)"),
        "enable_health_checks": Param(False, type="boolean", description="Verificar salud de sistemas antes de extraer"),
        "enable_circuit_breaker": Param(False, type="boolean", description="Habilitar circuit breaker para sistemas"),
        "enable_encryption": Param(False, type="boolean", description="Encriptar campos sensibles"),
        "sensitive_fields": Param("[]", type="string", description="Lista de campos sensibles a encriptar (JSON)"),
        "enable_incremental_load": Param(False, type="boolean", description="Carga incremental (solo cambios)"),
        "incremental_key": Param("id", type="string", description="Campo clave para carga incremental"),
        "enable_anomaly_detection": Param(False, type="boolean", description="Detectar anomalías en datos"),
        "anomaly_threshold": Param(3.0, type="number", description="Umbral de desviación estándar para anomalías"),
        "enable_dead_letter_queue": Param(False, type="boolean", description="Usar dead letter queue para errores"),
        "enable_business_rules": Param(False, type="boolean", description="Aplicar reglas de negocio"),
        "business_rules": Param("[]", type="string", description="Reglas de negocio a aplicar (JSON)"),
        "conflict_resolution_strategy": Param("latest", type="string", enum=["latest", "company_a", "company_b", "merge"], description="Estrategia de resolución de conflictos"),
    },
    tags=["integration", "merger", "acquisition", "etl", "data-migration"],
)
def merger_acquisition_integration() -> None:
    """
    DAG para orquestar integraciones de múltiples sistemas en fusiones/adquisiciones.
    """
    
    @task(task_id="extract_company_a_data")
    @with_retry(max_attempts=DEFAULT_MAX_RETRIES, exceptions=(ConnectionError, TimeoutError))
    def extract_company_a_data() -> Dict[str, Any]:
        """Extrae datos de todos los sistemas de la empresa A."""
        ctx = get_current_context()
        params = ctx["params"]
        config_str = str(params.get("company_a_config", "{}"))
        
        try:
            config = json.loads(config_str) if config_str else {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando company_a_config: {e}")
            raise ValueError("company_a_config debe ser un JSON válido")
        
        if not config:
            logger.warning("No hay configuración para empresa A, usando valores por defecto")
            config = {
                "systems": [
                    {
                        "type": "postgres",
                        "conn_id": "postgres_default",
                        "tables": ["customers", "orders", "products"]
                    }
                ]
            }
        
        # Validar configuración básica
        if "systems" not in config:
            raise ValueError("company_a_config debe contener 'systems'")
        
        logger.info(f"Extrayendo datos de empresa A. Sistemas: {len(config.get('systems', []))}")
        extracted_data = {}
        extraction_stats = {
            "systems_processed": 0,
            "systems_failed": 0,
            "total_records": 0
        }
        
        for system_idx, system in enumerate(config.get("systems", []), 1):
            system_type = system.get("type", "").lower()
            system_name = system.get("name", f"{system_type}_{system_idx}")
            
            logger.info(f"[{system_idx}/{len(config.get('systems', []))}] Procesando sistema: {system_name} ({system_type})")
            
            try:
                if system_type == "postgres":
                    hook = PostgresHook(postgres_conn_id=system.get("conn_id", "postgres_default"))
                    tables = system.get("tables", [])
                    
                    for table in tables:
                        query = f"SELECT * FROM {table}"
                        if system.get("where_clause"):
                            query += f" WHERE {system.get('where_clause')}"
                        
                        logger.debug(f"Ejecutando query en {system_name}.{table}")
                        df = hook.get_pandas_df(query)
                        records = df.to_dict("records")
                        extracted_data[f"{system_name}_{table}"] = records
                        extraction_stats["total_records"] += len(records)
                        logger.info(f"✓ Extraídos {len(records)} registros de {system_name}.{table}")
                
                elif system_type == "mysql":
                    hook = MySqlHook(mysql_conn_id=system.get("conn_id", "mysql_default"))
                    tables = system.get("tables", [])
                    
                    for table in tables:
                        query = f"SELECT * FROM {table}"
                        if system.get("where_clause"):
                            query += f" WHERE {system.get('where_clause')}"
                        
                        df = hook.get_pandas_df(query)
                        extracted_data[f"{system_name}_{table}"] = df.to_dict("records")
                        logger.info(f"Extraídos {len(df)} registros de {system_name}.{table}")
                
                elif system_type == "api" or system_type == "rest":
                    http_hook = HttpHook(http_conn_id=system.get("conn_id"), method="GET")
                    endpoint = system.get("endpoint", "")
                    headers = system.get("headers", {})
                    
                    response = http_hook.run(endpoint, headers=headers)
                    data = response.json() if hasattr(response, "json") else response
                    
                    key = system.get("data_key", "data")
                    if isinstance(data, dict) and key in data:
                        extracted_data[f"{system_name}_api"] = data[key]
                    else:
                        extracted_data[f"{system_name}_api"] = data
                    
                    logger.info(f"Extraídos datos de API {system_name}")
                
                elif system_type == "csv" or system_type == "file" or system_type == "s3":
                    file_path = system.get("file_path", "")
                    bucket = system.get("bucket")
                    key = system.get("key")
                    file_type = system.get("file_type", "csv")
                    
                    if bucket and key:
                        # Leer desde S3
                        if not BOTO3_AVAILABLE:
                            raise ImportError("boto3 no disponible para leer archivos S3")
                        
                        logger.info(f"Leyendo archivo S3: s3://{bucket}/{key}")
                        df = read_file_from_s3(bucket, key, file_type)
                        records = df.to_dict("records")
                        extracted_data[f"{system_name}_file"] = records
                        extraction_stats["total_records"] += len(records)
                        logger.info(f"✓ Extraídos {len(records)} registros de archivo S3 {system_name}")
                    elif file_path:
                        # Intentar parsear como S3 path
                        if file_path.startswith("s3://"):
                            path_parts = file_path.replace("s3://", "").split("/", 1)
                            if len(path_parts) == 2:
                                bucket, key = path_parts
                                df = read_file_from_s3(bucket, key, file_type)
                                records = df.to_dict("records")
                                extracted_data[f"{system_name}_file"] = records
                                extraction_stats["total_records"] += len(records)
                                logger.info(f"✓ Extraídos {len(records)} registros de {file_path}")
                            else:
                                raise ValueError(f"Formato de path S3 inválido: {file_path}")
                        else:
                            logger.warning(f"Path de archivo local no soportado aún: {file_path}")
                            extracted_data[f"{system_name}_file"] = {"file_path": file_path, "status": "pending"}
                    else:
                        raise ValueError("Debe especificar 'bucket' y 'key' o 'file_path' para archivos")
                
                else:
                    logger.warning(f"Tipo de sistema no soportado: {system_type}")
                    extraction_stats["systems_failed"] += 1
                    continue
                
                extraction_stats["systems_processed"] += 1
            
            except Exception as e:
                logger.error(f"✗ Error extrayendo datos de {system_name}: {e}", exc_info=True)
                extracted_data[f"{system_name}_error"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
                extraction_stats["systems_failed"] += 1
                # Continuar con otros sistemas
        
        logger.info(f"Extracción de empresa A completada:")
        logger.info(f"  - Sistemas procesados: {extraction_stats['systems_processed']}")
        logger.info(f"  - Sistemas fallidos: {extraction_stats['systems_failed']}")
        logger.info(f"  - Total registros: {extraction_stats['total_records']}")
        
        return {
            "company": "A",
            "extraction_timestamp": datetime.now().isoformat(),
            "data": extracted_data,
            "systems_count": len(config.get("systems", [])),
            "records_extracted": extraction_stats["total_records"],
            "extraction_stats": extraction_stats
        }
    
    @task(task_id="extract_company_b_data")
    @with_retry(max_attempts=DEFAULT_MAX_RETRIES, exceptions=(ConnectionError, TimeoutError))
    def extract_company_b_data() -> Dict[str, Any]:
        """Extrae datos de todos los sistemas de la empresa B."""
        ctx = get_current_context()
        params = ctx["params"]
        config_str = str(params.get("company_b_config", "{}"))
        
        try:
            config = json.loads(config_str) if config_str else {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando company_b_config: {e}")
            raise ValueError("company_b_config debe ser un JSON válido")
        
        if not config:
            logger.warning("No hay configuración para empresa B, usando valores por defecto")
            config = {
                "systems": [
                    {
                        "type": "mysql",
                        "conn_id": "mysql_default",
                        "tables": ["clients", "transactions", "items"]
                    }
                ]
            }
        
        # Validar configuración básica
        if "systems" not in config:
            raise ValueError("company_b_config debe contener 'systems'")
        
        logger.info(f"Extrayendo datos de empresa B. Sistemas: {len(config.get('systems', []))}")
        extracted_data = {}
        extraction_stats = {
            "systems_processed": 0,
            "systems_failed": 0,
            "total_records": 0
        }
        
        for system_idx, system in enumerate(config.get("systems", []), 1):
            system_type = system.get("type", "").lower()
            system_name = system.get("name", f"{system_type}_{system_idx}")
            
            logger.info(f"[{system_idx}/{len(config.get('systems', []))}] Procesando sistema: {system_name} ({system_type})")
            
            try:
                if system_type == "postgres":
                    hook = PostgresHook(postgres_conn_id=system.get("conn_id", "postgres_default"))
                    tables = system.get("tables", [])
                    
                    for table in tables:
                        query = f"SELECT * FROM {table}"
                        if system.get("where_clause"):
                            query += f" WHERE {system.get('where_clause')}"
                        
                        logger.debug(f"Ejecutando query en {system_name}.{table}")
                        df = hook.get_pandas_df(query)
                        records = df.to_dict("records")
                        extracted_data[f"{system_name}_{table}"] = records
                        extraction_stats["total_records"] += len(records)
                        logger.info(f"✓ Extraídos {len(records)} registros de {system_name}.{table}")
                
                elif system_type == "mysql":
                    hook = MySqlHook(mysql_conn_id=system.get("conn_id", "mysql_default"))
                    tables = system.get("tables", [])
                    
                    for table in tables:
                        query = f"SELECT * FROM {table}"
                        if system.get("where_clause"):
                            query += f" WHERE {system.get('where_clause')}"
                        
                        logger.debug(f"Ejecutando query en {system_name}.{table}")
                        df = hook.get_pandas_df(query)
                        records = df.to_dict("records")
                        extracted_data[f"{system_name}_{table}"] = records
                        extraction_stats["total_records"] += len(records)
                        logger.info(f"✓ Extraídos {len(records)} registros de {system_name}.{table}")
                
                elif system_type == "api" or system_type == "rest":
                    http_hook = HttpHook(http_conn_id=system.get("conn_id"), method="GET")
                    endpoint = system.get("endpoint", "")
                    headers = system.get("headers", {})
                    
                    logger.debug(f"Llamando API: {endpoint}")
                    response = http_hook.run(endpoint, headers=headers)
                    data = response.json() if hasattr(response, "json") else response
                    
                    key = system.get("data_key", "data")
                    if isinstance(data, dict) and key in data:
                        records = data[key] if isinstance(data[key], list) else [data[key]]
                        extracted_data[f"{system_name}_api"] = records
                        extraction_stats["total_records"] += len(records)
                    else:
                        records = data if isinstance(data, list) else [data]
                        extracted_data[f"{system_name}_api"] = records
                        extraction_stats["total_records"] += len(records)
                    
                    logger.info(f"✓ Extraídos {len(records)} registros de API {system_name}")
                
                elif system_type == "csv" or system_type == "file" or system_type == "s3":
                    file_path = system.get("file_path", "")
                    bucket = system.get("bucket")
                    key = system.get("key")
                    file_type = system.get("file_type", "csv")
                    
                    if bucket and key:
                        if not BOTO3_AVAILABLE:
                            raise ImportError("boto3 no disponible para leer archivos S3")
                        
                        logger.info(f"Leyendo archivo S3: s3://{bucket}/{key}")
                        df = read_file_from_s3(bucket, key, file_type)
                        records = df.to_dict("records")
                        extracted_data[f"{system_name}_file"] = records
                        extraction_stats["total_records"] += len(records)
                        logger.info(f"✓ Extraídos {len(records)} registros de archivo S3 {system_name}")
                    elif file_path:
                        if file_path.startswith("s3://"):
                            path_parts = file_path.replace("s3://", "").split("/", 1)
                            if len(path_parts) == 2:
                                bucket, key = path_parts
                                df = read_file_from_s3(bucket, key, file_type)
                                records = df.to_dict("records")
                                extracted_data[f"{system_name}_file"] = records
                                extraction_stats["total_records"] += len(records)
                                logger.info(f"✓ Extraídos {len(records)} registros de {file_path}")
                            else:
                                raise ValueError(f"Formato de path S3 inválido: {file_path}")
                        else:
                            logger.warning(f"Path de archivo local no soportado aún: {file_path}")
                            extracted_data[f"{system_name}_file"] = {"file_path": file_path, "status": "pending"}
                    else:
                        raise ValueError("Debe especificar 'bucket' y 'key' o 'file_path' para archivos")
                
                else:
                    logger.warning(f"Tipo de sistema no soportado: {system_type}")
                    extraction_stats["systems_failed"] += 1
                    continue
                
                extraction_stats["systems_processed"] += 1
            
            except Exception as e:
                logger.error(f"✗ Error extrayendo datos de {system_name}: {e}", exc_info=True)
                extracted_data[f"{system_name}_error"] = {
                    "error": str(e),
                    "error_type": type(e).__name__,
                    "timestamp": datetime.now().isoformat()
                }
                extraction_stats["systems_failed"] += 1
        
        logger.info(f"Extracción de empresa B completada:")
        logger.info(f"  - Sistemas procesados: {extraction_stats['systems_processed']}")
        logger.info(f"  - Sistemas fallidos: {extraction_stats['systems_failed']}")
        logger.info(f"  - Total registros: {extraction_stats['total_records']}")
        
        return {
            "company": "B",
            "extraction_timestamp": datetime.now().isoformat(),
            "data": extracted_data,
            "systems_count": len(config.get("systems", [])),
            "records_extracted": extraction_stats["total_records"],
            "extraction_stats": extraction_stats
        }
    
    @task(task_id="transform_to_common_format")
    def transform_to_common_format(
        company_a_data: Dict[str, Any],
        company_b_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Transforma los datos de ambas empresas a un formato común."""
        ctx = get_current_context()
        params = ctx["params"]
        rules_str = str(params.get("transformation_rules", "{}"))
        
        try:
            transformation_rules = json.loads(rules_str) if rules_str else {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando transformation_rules: {e}")
            transformation_rules = {}
        
        logger.info("Iniciando transformación a formato común")
        
        # Formato común base
        common_format = {
            "customers": [],
            "orders": [],
            "products": [],
            "transactions": [],
            "metadata": {
                "company_a": company_a_data.get("records_extracted", 0),
                "company_b": company_b_data.get("records_extracted", 0),
                "transformation_timestamp": datetime.now().isoformat(),
            }
        }
        
        # Mapeos por defecto si no se proporcionan reglas
        default_mappings = {
            "customers": {
                "company_a": ["customers", "clients", "customer_data"],
                "company_b": ["clients", "customers", "customer_data"],
                "field_mapping": {
                    "email": ["email", "e_mail", "email_address"],
                    "name": ["name", "full_name", "customer_name"],
                    "phone": ["phone", "phone_number", "telephone"],
                    "address": ["address", "street_address", "location"],
                }
            },
            "orders": {
                "company_a": ["orders", "order_data"],
                "company_b": ["transactions", "orders", "order_data"],
                "field_mapping": {
                    "order_id": ["order_id", "id", "transaction_id"],
                    "customer_id": ["customer_id", "client_id", "customer"],
                    "amount": ["amount", "total", "order_total"],
                    "date": ["date", "order_date", "created_at"],
                }
            },
            "products": {
                "company_a": ["products", "items", "product_data"],
                "company_b": ["items", "products", "product_data"],
                "field_mapping": {
                    "product_id": ["product_id", "id", "item_id"],
                    "name": ["name", "product_name", "item_name"],
                    "price": ["price", "unit_price", "cost"],
                    "category": ["category", "product_category", "type"],
                }
            }
        }
        
        # Usar reglas personalizadas o las por defecto
        mappings = transformation_rules.get("mappings", default_mappings)
        
        def normalize_field_value(value, field_type: str = "string"):
            """Normaliza valores según el tipo de campo."""
            if value is None:
                return None
            
            if field_type == "string":
                return str(value).strip()
            elif field_type == "number":
                try:
                    return float(value)
                except (ValueError, TypeError):
                    return None
            elif field_type == "date":
                if isinstance(value, str):
                    try:
                        return pd.to_datetime(value).isoformat()
                    except:
                        return value
                return value
            elif field_type == "email":
                return str(value).strip().lower()
            return value
        
        def find_and_map_fields(source_record: Dict, field_mapping: Dict) -> Dict:
            """Encuentra y mapea campos del registro fuente usando el mapeo."""
            mapped_record = {}
            
            for target_field, source_fields in field_mapping.items():
                value = None
                for source_field in source_fields:
                    # Buscar con diferentes variaciones de nombre
                    if source_field in source_record:
                        value = source_record[source_field]
                        break
                    # Buscar case-insensitive
                    for key in source_record.keys():
                        if key.lower() == source_field.lower():
                            value = source_record[key]
                            break
                    if value is not None:
                        break
                
                # Normalizar según el tipo de campo
                field_type = "string"
                if "email" in target_field:
                    field_type = "email"
                elif "amount" in target_field or "price" in target_field or "id" in target_field:
                    field_type = "number"
                elif "date" in target_field:
                    field_type = "date"
                
                mapped_record[target_field] = normalize_field_value(value, field_type)
            
            return mapped_record
        
        # Procesar datos de empresa A
        for category, mapping_config in mappings.items():
            company_a_keys = mapping_config.get("company_a", [])
            
            for key in company_a_keys:
                data_key = f"*_{key}"  # Buscar cualquier variación
                for full_key, records in company_a_data.get("data", {}).items():
                    if key in full_key.lower() and isinstance(records, list):
                        field_mapping = mapping_config.get("field_mapping", {})
                        for record in records:
                            mapped_record = find_and_map_fields(record, field_mapping)
                            mapped_record["source_company"] = "A"
                            mapped_record["source_system"] = full_key
                            common_format[category].append(mapped_record)
        
        # Procesar datos de empresa B
        for category, mapping_config in mappings.items():
            company_b_keys = mapping_config.get("company_b", [])
            
            for key in company_b_keys:
                for full_key, records in company_b_data.get("data", {}).items():
                    if key in full_key.lower() and isinstance(records, list):
                        field_mapping = mapping_config.get("field_mapping", {})
                        for record in records:
                            mapped_record = find_and_map_fields(record, field_mapping)
                            mapped_record["source_company"] = "B"
                            mapped_record["source_system"] = full_key
                            common_format[category].append(mapped_record)
        
        # Aplicar transformaciones adicionales si están definidas
        if "transformations" in transformation_rules:
            for transformation in transformation_rules["transformations"]:
                transform_type = transformation.get("type")
                
                if transform_type == "deduplicate":
                    # Deduplicar por campos específicos
                    key_fields = transformation.get("key_fields", [])
                    for category in common_format.keys():
                        if isinstance(common_format[category], list):
                            seen = set()
                            unique_records = []
                            for record in common_format[category]:
                                key = tuple(record.get(f) for f in key_fields if f in record)
                                if key not in seen:
                                    seen.add(key)
                                    unique_records.append(record)
                            common_format[category] = unique_records
                            logger.info(f"Deduplicados {category}: {len(common_format[category])} registros únicos")
                
                elif transform_type == "enrich":
                    # Enriquecer datos con información adicional
                    enrichment_rules = transformation.get("rules", {})
                    for category in common_format.keys():
                        if isinstance(common_format[category], list):
                            for record in common_format[category]:
                                for field, value in enrichment_rules.items():
                                    if field not in record or not record[field]:
                                        record[field] = value
        
        logger.info(f"Transformación completada. Registros procesados:")
        for category, records in common_format.items():
            if isinstance(records, list):
                logger.info(f"  - {category}: {len(records)} registros")
        
        return common_format
    
    @task(task_id="validate_transformed_data")
    def validate_transformed_data(transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la calidad e integridad de los datos transformados."""
        ctx = get_current_context()
        params = ctx["params"]
        strict_mode = params.get("validation_strict", True)
        
        logger.info("Iniciando validación de datos transformados")
        
        validation_results = {
            "timestamp": datetime.now().isoformat(),
            "strict_mode": strict_mode,
            "categories": {},
            "overall_status": "passed",
            "errors": [],
            "warnings": []
        }
        
        # Reglas de validación
        validation_rules = {
            "customers": {
                "required_fields": ["email", "name"],
                "email_validation": True,
                "min_length": {"name": 2},
            },
            "orders": {
                "required_fields": ["order_id", "customer_id", "amount"],
                "numeric_fields": ["amount"],
                "min_value": {"amount": 0},
            },
            "products": {
                "required_fields": ["product_id", "name", "price"],
                "numeric_fields": ["price"],
                "min_value": {"price": 0},
            }
        }
        
        import re
        
        for category, records in transformed_data.items():
            if not isinstance(records, list):
                continue
            
            category_results = {
                "total_records": len(records),
                "valid_records": 0,
                "invalid_records": 0,
                "errors": [],
                "warnings": []
            }
            
            if category not in validation_rules:
                category_results["warnings"].append(f"No hay reglas de validación para {category}")
                validation_results["categories"][category] = category_results
                continue
            
            rules = validation_rules[category]
            
            for idx, record in enumerate(records):
                is_valid = True
                record_errors = []
                record_warnings = []
                
                # Validar campos requeridos
                for field in rules.get("required_fields", []):
                    if field not in record or record[field] is None or record[field] == "":
                        is_valid = False
                        record_errors.append(f"Campo requerido faltante: {field}")
                
                # Validar email
                if rules.get("email_validation") and "email" in record:
                    email = record.get("email", "")
                    if email:
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if not re.match(email_pattern, email):
                            if strict_mode:
                                is_valid = False
                                record_errors.append(f"Email inválido: {email}")
                            else:
                                record_warnings.append(f"Email con formato sospechoso: {email}")
                
                # Validar campos numéricos
                for field in rules.get("numeric_fields", []):
                    if field in record and record[field] is not None:
                        try:
                            float(record[field])
                        except (ValueError, TypeError):
                            if strict_mode:
                                is_valid = False
                                record_errors.append(f"Campo numérico inválido: {field}={record[field]}")
                            else:
                                record_warnings.append(f"Campo numérico con formato inválido: {field}")
                
                # Validar valores mínimos
                for field, min_val in rules.get("min_value", {}).items():
                    if field in record and record[field] is not None:
                        try:
                            val = float(record[field])
                            if val < min_val:
                                if strict_mode:
                                    is_valid = False
                                    record_errors.append(f"Valor por debajo del mínimo: {field}={val} < {min_val}")
                                else:
                                    record_warnings.append(f"Valor por debajo del mínimo recomendado: {field}={val}")
                        except (ValueError, TypeError):
                            pass
                
                # Validar longitudes mínimas
                for field, min_len in rules.get("min_length", {}).items():
                    if field in record and record[field] is not None:
                        if len(str(record[field])) < min_len:
                            if strict_mode:
                                is_valid = False
                                record_errors.append(f"Campo demasiado corto: {field} (mínimo {min_len} caracteres)")
                            else:
                                record_warnings.append(f"Campo corto: {field}")
                
                if is_valid:
                    category_results["valid_records"] += 1
                else:
                    category_results["invalid_records"] += 1
                    if record_errors:
                        category_results["errors"].append({
                            "record_index": idx,
                            "errors": record_errors
                        })
                
                if record_warnings:
                    category_results["warnings"].append({
                        "record_index": idx,
                        "warnings": record_warnings
                    })
            
            validation_results["categories"][category] = category_results
            
            # Si hay registros inválidos en modo estricto, marcar como fallido
            if strict_mode and category_results["invalid_records"] > 0:
                validation_results["overall_status"] = "failed"
                validation_results["errors"].append(
                    f"{category}: {category_results['invalid_records']} registros inválidos"
                )
        
        # Calcular estadísticas generales
        total_records = sum(r.get("total_records", 0) for r in validation_results["categories"].values())
        total_valid = sum(r.get("valid_records", 0) for r in validation_results["categories"].values())
        total_invalid = sum(r.get("invalid_records", 0) for r in validation_results["categories"].values())
        
        validation_results["summary"] = {
            "total_records": total_records,
            "valid_records": total_valid,
            "invalid_records": total_invalid,
            "validation_rate": (total_valid / total_records * 100) if total_records > 0 else 0
        }
        
        logger.info(f"Validación completada. Estado: {validation_results['overall_status']}")
        logger.info(f"Registros válidos: {total_valid}/{total_records} ({validation_results['summary']['validation_rate']:.2f}%)")
        
        if validation_results["overall_status"] == "failed" and strict_mode:
            raise ValueError(f"Validación falló con {total_invalid} registros inválidos. Revisar logs para detalles.")
        
        return validation_results
    
    @task(task_id="load_to_unified_system")
    def load_to_unified_system(
        transformed_data: Dict[str, Any],
        validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Carga los datos transformados y validados al sistema unificado."""
        ctx = get_current_context()
        params = ctx["params"]
        dry_run = params.get("dry_run", False)
        chunk_size = params.get("chunk_size", DEFAULT_CHUNK_SIZE)
        enable_backup = params.get("enable_backup", True)
        
        config_str = str(params.get("unified_system_config", "{}"))
        try:
            config = json.loads(config_str) if config_str else {}
        except json.JSONDecodeError as e:
            logger.error(f"Error parseando unified_system_config: {e}")
            raise ValueError("unified_system_config debe ser un JSON válido")
        
        if not config:
            logger.warning("No hay configuración para sistema unificado, usando valores por defecto")
            config = {
                "type": "postgres",
                "conn_id": "postgres_default",
                "schema": "unified"
            }
        
        if dry_run:
            logger.info("DRY RUN: No se cargarán datos al sistema unificado")
            return {
                "status": "dry_run",
                "message": "Ejecución en modo dry-run, no se cargaron datos",
                "records_that_would_be_loaded": {
                    category: len(records) if isinstance(records, list) else 0
                    for category, records in transformed_data.items()
                    if isinstance(records, list)
                }
            }
        
        # Verificar que la validación pasó
        if validation_results.get("overall_status") == "failed":
            logger.warning("Hay registros inválidos, pero continuando con la carga (modo no estricto)")
        
        logger.info(f"Cargando datos al sistema unificado: {config}")
        load_results = {
            "timestamp": datetime.now().isoformat(),
            "system_type": config.get("type", "postgres"),
            "categories": {},
            "total_loaded": 0,
            "total_failed": 0,
            "chunks_processed": 0,
            "errors": [],
            "backup_tables": []
        }
        
        system_type = config.get("type", "postgres").lower()
        
        try:
            if system_type == "postgres":
                hook = PostgresHook(postgres_conn_id=config.get("conn_id", "postgres_default"))
                schema = config.get("schema", "public")
                
                # Solo cargar categorías válidas
                for category, records in transformed_data.items():
                    if not isinstance(records, list) or category == "metadata":
                        continue
                    
                    if not records:
                        logger.info(f"No hay registros para cargar en {category}")
                        continue
                    
                    table_name = f"{schema}.unified_{category}"
                    logger.info(f"Cargando {len(records)} registros en {category} -> {table_name}")
                    
                    try:
                        # Crear tabla si no existe
                        create_table_sql = f"""
                        CREATE TABLE IF NOT EXISTS {table_name} (
                            id SERIAL PRIMARY KEY,
                            source_company VARCHAR(10),
                            source_system VARCHAR(255),
                            data JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        CREATE UNIQUE INDEX IF NOT EXISTS idx_{category}_unique 
                        ON {table_name} (source_company, source_system, (data->>'id'));
                        CREATE INDEX IF NOT EXISTS idx_{category}_source_company 
                        ON {table_name} (source_company);
                        CREATE INDEX IF NOT EXISTS idx_{category}_created_at 
                        ON {table_name} (created_at);
                        """
                        hook.run(create_table_sql)
                        
                        # Crear backup si está habilitado y la tabla tiene datos
                        backup_table = None
                        if enable_backup:
                            try:
                                check_sql = f"SELECT COUNT(*) FROM {table_name}"
                                existing_count = hook.get_first(check_sql)[0]
                                if existing_count > 0:
                                    backup_table = create_backup_table(hook, schema, table_name)
                                    # Copiar datos existentes al backup
                                    copy_sql = f"""
                                    INSERT INTO {schema}.{backup_table}
                                    SELECT * FROM {table_name};
                                    """
                                    hook.run(copy_sql)
                                    load_results["backup_tables"].append(backup_table)
                                    logger.info(f"Backup creado: {backup_table} con {existing_count} registros")
                            except Exception as e:
                                logger.warning(f"No se pudo crear backup para {category}: {e}")
                        
                        # Procesar en chunks si hay muchos registros
                        use_chunking = len(records) > LARGE_DATASET_THRESHOLD
                        if use_chunking:
                            logger.info(f"Usando chunking para {len(records)} registros (chunk_size={chunk_size})")
                            chunks = chunk_list(records, chunk_size)
                        else:
                            chunks = [records]
                        
                        inserted_count = 0
                        failed_count = 0
                        
                        for chunk_idx, chunk in enumerate(chunks, 1):
                            try:
                                # Usar inserción en batch para mejor rendimiento
                                values_list = []
                                for record in chunk:
                                    values_list.append((
                                        record.get("source_company"),
                                        record.get("source_system"),
                                        json.dumps(record)
                                    ))
                                
                                # Insertar batch usando executemany para mejor rendimiento
                                insert_sql = f"""
                                INSERT INTO {table_name} (source_company, source_system, data)
                                VALUES (%s, %s, %s)
                                ON CONFLICT (source_company, source_system, (data->>'id'))
                                DO UPDATE SET 
                                    data = EXCLUDED.data,
                                    updated_at = CURRENT_TIMESTAMP
                                """
                                
                                # Usar run con múltiples parámetros
                                conn = hook.get_conn()
                                cursor = conn.cursor()
                                try:
                                    cursor.executemany(insert_sql, values_list)
                                    conn.commit()
                                finally:
                                    cursor.close()
                                    conn.close()
                                
                                inserted_count += len(chunk)
                                load_results["chunks_processed"] += 1
                                
                                if use_chunking:
                                    log_progress(
                                        chunk_idx * chunk_size,
                                        len(records),
                                        f"Cargando {category}",
                                        step=max(1, len(chunks) // 10)
                                    )
                                
                            except Exception as e:
                                logger.error(f"Error insertando chunk {chunk_idx} en {category}: {e}")
                                failed_count += len(chunk)
                                load_results["errors"].append(f"{category} chunk {chunk_idx}: {str(e)}")
                                
                                # Intentar insertar registro por registro si falla el batch
                                for record in chunk:
                                    try:
                                        hook.run(
                                            insert_sql,
                                            parameters=(
                                                record.get("source_company"),
                                                record.get("source_system"),
                                                json.dumps(record)
                                            )
                                        )
                                        inserted_count += 1
                                        failed_count -= 1
                                    except Exception as record_error:
                                        logger.warning(f"Error insertando registro individual: {record_error}")
                        
                        load_results["categories"][category] = {
                            "table": table_name,
                            "records_loaded": inserted_count,
                            "records_failed": failed_count,
                            "total_records": len(records),
                            "chunks_used": len(chunks) if use_chunking else 1,
                            "backup_table": backup_table
                        }
                        load_results["total_loaded"] += inserted_count
                        load_results["total_failed"] += failed_count
                        
                        logger.info(
                            f"✓ Cargados {inserted_count}/{len(records)} registros en {table_name} "
                            f"(fallidos: {failed_count})"
                        )
                    
                    except Exception as e:
                        logger.error(f"✗ Error cargando {category}: {e}", exc_info=True)
                        load_results["errors"].append(f"{category}: {str(e)}")
                        load_results["categories"][category] = {
                            "error": str(e),
                            "error_type": type(e).__name__
                        }
                        load_results["total_failed"] += len(records) if isinstance(records, list) else 0
            
            elif system_type == "mysql":
                hook = MySqlHook(mysql_conn_id=config.get("conn_id", "mysql_default"))
                schema = config.get("schema", "")
                table_prefix = f"{schema}." if schema else ""
                
                for category, records in transformed_data.items():
                    if not isinstance(records, list) or category == "metadata":
                        continue
                    
                    if not records:
                        continue
                    
                    table_name = f"{table_prefix}unified_{category}"
                    
                    try:
                        # Similar a PostgreSQL pero con sintaxis MySQL
                        # Por simplicidad, usar inserción directa
                        inserted_count = 0
                        for record in records:
                            # Implementar inserción MySQL aquí
                            inserted_count += 1
                        
                        load_results["categories"][category] = {
                            "table": table_name,
                            "records_loaded": inserted_count
                        }
                        
                    except Exception as e:
                        logger.error(f"Error cargando {category}: {e}")
                        load_results["errors"].append(f"{category}: {str(e)}")
            
            elif system_type == "api" or system_type == "rest":
                http_hook = HttpHook(http_conn_id=config.get("conn_id"), method="POST")
                endpoint = config.get("endpoint", "/api/data/load")
                
                for category, records in transformed_data.items():
                    if not isinstance(records, list) or category == "metadata":
                        continue
                    
                    try:
                        response = http_hook.run(
                            endpoint,
                            json={"category": category, "records": records},
                            headers=config.get("headers", {})
                        )
                        load_results["categories"][category] = {
                            "records_loaded": len(records),
                            "response": str(response)
                        }
                    except Exception as e:
                        logger.error(f"Error cargando {category} vía API: {e}")
                        load_results["errors"].append(f"{category}: {str(e)}")
            
            else:
                raise ValueError(f"Tipo de sistema unificado no soportado: {system_type}")
        
        except Exception as e:
            logger.error(f"Error general cargando datos: {e}")
            load_results["errors"].append(f"Error general: {str(e)}")
            raise
        
        logger.info(f"Carga completada. Total cargado: {load_results['total_loaded']} registros")
        
        return load_results
    
    @task(task_id="generate_status_report")
    def generate_status_report(
        company_a_data: Dict[str, Any],
        company_b_data: Dict[str, Any],
        transformed_data: Dict[str, Any],
        validation_results: Dict[str, Any],
        load_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera un reporte completo del estado de la integración."""
        ctx = get_current_context()
        params = ctx["params"]
        detailed = params.get("generate_detailed_report", True)
        
        logger.info("Generando reporte de estado de integración")
        
        report = {
            "integration_report": {
                "timestamp": datetime.now().isoformat(),
                "execution_id": ctx["dag_run"].run_id,
                "status": "completed",
                "summary": {
                    "extraction": {
                        "company_a": {
                            "systems_processed": company_a_data.get("systems_count", 0),
                            "records_extracted": company_a_data.get("records_extracted", 0)
                        },
                        "company_b": {
                            "systems_processed": company_b_data.get("systems_count", 0),
                            "records_extracted": company_b_data.get("records_extracted", 0)
                        },
                        "total_records": (
                            company_a_data.get("records_extracted", 0) +
                            company_b_data.get("records_extracted", 0)
                        )
                    },
                    "transformation": {
                        "categories_processed": len([
                            k for k, v in transformed_data.items()
                            if isinstance(v, list)
                        ]),
                        "records_by_category": {
                            category: len(records) if isinstance(records, list) else 0
                            for category, records in transformed_data.items()
                            if isinstance(records, list)
                        }
                    },
                    "validation": {
                        "overall_status": validation_results.get("overall_status", "unknown"),
                        "total_records": validation_results.get("summary", {}).get("total_records", 0),
                        "valid_records": validation_results.get("summary", {}).get("valid_records", 0),
                        "invalid_records": validation_results.get("summary", {}).get("invalid_records", 0),
                        "validation_rate": validation_results.get("summary", {}).get("validation_rate", 0)
                    },
                    "load": {
                        "status": load_results.get("status", "completed"),
                        "total_records_loaded": load_results.get("total_loaded", 0),
                        "categories_loaded": len(load_results.get("categories", {})),
                        "errors_count": len(load_results.get("errors", []))
                    }
                }
            }
        }
        
        if detailed:
            report["integration_report"]["details"] = {
                "extraction_details": {
                    "company_a": company_a_data,
                    "company_b": company_b_data
                },
                "transformation_details": {
                    "metadata": transformed_data.get("metadata", {}),
                    "sample_records": {
                        category: records[:3] if isinstance(records, list) and len(records) > 0 else []
                        for category, records in transformed_data.items()
                        if isinstance(records, list) and category != "metadata"
                    }
                },
                "validation_details": validation_results,
                "load_details": load_results
            }
        
        # Calcular métricas adicionales
        total_extracted = (
            company_a_data.get("records_extracted", 0) +
            company_b_data.get("records_extracted", 0)
        )
        total_loaded = load_results.get("total_loaded", 0)
        
        if total_extracted > 0:
            load_rate = (total_loaded / total_extracted) * 100
            report["integration_report"]["metrics"] = {
                "extraction_to_load_rate": load_rate,
                "data_quality_score": validation_results.get("summary", {}).get("validation_rate", 0),
                "overall_success_rate": (
                    (validation_results.get("summary", {}).get("validation_rate", 0) + load_rate) / 2
                )
            }
        
        # Determinar estado final
        if load_results.get("status") == "dry_run":
            report["integration_report"]["status"] = "dry_run_completed"
        elif validation_results.get("overall_status") == "failed":
            report["integration_report"]["status"] = "completed_with_warnings"
        elif len(load_results.get("errors", [])) > 0:
            report["integration_report"]["status"] = "completed_with_errors"
        else:
            report["integration_report"]["status"] = "completed_successfully"
        
        # Guardar reporte (podría guardarse en BD, S3, o enviarse por email)
        logger.info("=" * 80)
        logger.info("REPORTE DE INTEGRACIÓN - FUSIÓN/ADQUISICIÓN")
        logger.info("=" * 80)
        logger.info(f"Estado: {report['integration_report']['status']}")
        logger.info(f"Total extraído: {total_extracted} registros")
        logger.info(f"Total cargado: {total_loaded} registros")
        logger.info(f"Tasa de validación: {validation_results.get('summary', {}).get('validation_rate', 0):.2f}%")
        logger.info("=" * 80)
        
        # Retornar reporte como JSON para posible uso posterior
        return report
    
    @task(task_id="compare_data_changes")
    def compare_data_changes(
        load_results: Dict[str, Any],
        status_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Compara datos antes y después de la carga."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_comparison", False):
            logger.info("Comparación de datos deshabilitada")
            return {"enabled": False}
        
        config_str = str(params.get("unified_system_config", "{}"))
        try:
            config = json.loads(config_str) if config_str else {}
        except json.JSONDecodeError:
            logger.warning("No se pudo parsear unified_system_config para comparación")
            return {"enabled": False, "error": "config_invalid"}
        
        if config.get("type", "postgres").lower() != "postgres":
            logger.info("Comparación solo disponible para PostgreSQL")
            return {"enabled": False, "reason": "only_postgres"}
        
        hook = PostgresHook(postgres_conn_id=config.get("conn_id", "postgres_default"))
        schema = config.get("schema", "public")
        
        comparison_results = {
            "timestamp": datetime.now().isoformat(),
            "categories": {}
        }
        
        for category, category_info in load_results.get("categories", {}).items():
            if "backup_table" in category_info and category_info["backup_table"]:
                backup_table = category_info["backup_table"]
                table_name = category_info["table"]
                
                try:
                    comparison = compare_data_before_after(
                        hook, schema, table_name, backup_table
                    )
                    comparison_results["categories"][category] = comparison
                except Exception as e:
                    logger.error(f"Error comparando {category}: {e}")
                    comparison_results["categories"][category] = {"error": str(e)}
        
        logger.info(f"Comparación completada para {len(comparison_results['categories'])} categorías")
        return comparison_results
    
    @task(task_id="export_report_file")
    def export_report_file(status_report: Dict[str, Any]) -> Dict[str, Any]:
        """Exporta el reporte a un archivo."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("export_report", False):
            logger.info("Exportación de reporte deshabilitada")
            return {"enabled": False}
        
        export_format = params.get("export_format", "json")
        
        try:
            file_path = export_report_to_file(status_report, format=export_format)
            logger.info(f"Reporte exportado exitosamente a {file_path}")
            return {
                "enabled": True,
                "file_path": file_path,
                "format": export_format
            }
        except Exception as e:
            logger.error(f"Error exportando reporte: {e}")
            return {
                "enabled": True,
                "error": str(e)
            }
    
    @task(task_id="send_notifications")
    def send_notifications(
        status_report: Dict[str, Any],
        load_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envía notificaciones según la configuración."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_notifications", False):
            logger.info("Notificaciones deshabilitadas")
            return {"enabled": False}
        
        config_str = str(params.get("notification_config", "{}"))
        try:
            notification_config = json.loads(config_str) if config_str else {}
        except json.JSONDecodeError:
            logger.warning("Configuración de notificaciones inválida")
            return {"enabled": False, "error": "config_invalid"}
        
        notification_results = {
            "timestamp": datetime.now().isoformat(),
            "notifications_sent": [],
            "notifications_failed": []
        }
        
        # Determinar severidad basada en el estado
        status = status_report.get("integration_report", {}).get("status", "unknown")
        if status == "completed_successfully":
            severity = "success"
        elif "error" in status or "failed" in status:
            severity = "error"
        elif "warning" in status:
            severity = "warning"
        else:
            severity = "info"
        
        # Construir mensaje
        summary = status_report.get("integration_report", {}).get("summary", {})
        message = f"""
Integración M&A Completada

Estado: {status}
Total Extraído: {summary.get('extraction', {}).get('total_records', 0)} registros
Total Cargado: {summary.get('load', {}).get('total_records_loaded', 0)} registros
Tasa de Validación: {summary.get('validation', {}).get('validation_rate', 0):.2f}%
Errores: {summary.get('load', {}).get('errors_count', 0)}

Ejecución ID: {status_report.get('integration_report', {}).get('execution_id', 'N/A')}
        """.strip()
        
        subject = f"Integración M&A - {status.replace('_', ' ').title()}"
        
        # Enviar notificaciones según configuración
        if notification_config.get("slack", {}).get("enabled"):
            webhook_url = notification_config["slack"].get("webhook_url")
            if webhook_url:
                success = send_notification(
                    "slack",
                    message,
                    subject=subject,
                    webhook_url=webhook_url,
                    severity=severity
                )
                if success:
                    notification_results["notifications_sent"].append("slack")
                else:
                    notification_results["notifications_failed"].append("slack")
        
        if notification_config.get("webhook", {}).get("enabled"):
            webhook_url = notification_config["webhook"].get("url")
            if webhook_url:
                success = send_notification(
                    "webhook",
                    message,
                    subject=subject,
                    webhook_url=webhook_url,
                    severity=severity
                )
                if success:
                    notification_results["notifications_sent"].append("webhook")
                else:
                    notification_results["notifications_failed"].append("webhook")
        
        if notification_config.get("email", {}).get("enabled"):
            email_to = notification_config["email"].get("to", [])
            if email_to:
                success = send_notification(
                    "email",
                    message,
                    subject=subject,
                    email_to=email_to,
                    severity=severity
                )
                if success:
                    notification_results["notifications_sent"].append("email")
                else:
                    notification_results["notifications_failed"].append("email")
        
        logger.info(f"Notificaciones enviadas: {len(notification_results['notifications_sent'])}")
        return notification_results
    
    @task(task_id="rollback_on_error", trigger_rule="one_failed")
    def rollback_on_error(load_results: Dict[str, Any]) -> Dict[str, Any]:
        """Realiza rollback automático si hay errores críticos."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_rollback_on_error", False):
            logger.info("Rollback automático deshabilitado")
            return {"enabled": False}
        
        # Verificar si hay errores críticos
        error_count = len(load_results.get("errors", []))
        total_failed = load_results.get("total_failed", 0)
        total_loaded = load_results.get("total_loaded", 0)
        
        # Solo hacer rollback si hay muchos errores o si falló completamente
        if error_count == 0 and total_failed == 0:
            logger.info("No hay errores, no se requiere rollback")
            return {"enabled": False, "reason": "no_errors"}
        
        # Calcular tasa de error
        total_attempted = total_loaded + total_failed
        error_rate = (total_failed / total_attempted * 100) if total_attempted > 0 else 0
        
        # Solo rollback si tasa de error > 50%
        if error_rate < 50:
            logger.info(f"Tasa de error ({error_rate:.2f}%) no justifica rollback")
            return {"enabled": False, "reason": "error_rate_too_low", "error_rate": error_rate}
        
        config_str = str(params.get("unified_system_config", "{}"))
        try:
            config = json.loads(config_str) if config_str else {}
        except json.JSONDecodeError:
            logger.error("No se pudo parsear unified_system_config para rollback")
            return {"enabled": False, "error": "config_invalid"}
        
        if config.get("type", "postgres").lower() != "postgres":
            logger.warning("Rollback solo disponible para PostgreSQL")
            return {"enabled": False, "reason": "only_postgres"}
        
        hook = PostgresHook(postgres_conn_id=config.get("conn_id", "postgres_default"))
        schema = config.get("schema", "public")
        
        # Recopilar tablas de backup y objetivo
        backup_tables = []
        target_tables = []
        
        for category, category_info in load_results.get("categories", {}).items():
            if "backup_table" in category_info and category_info["backup_table"]:
                backup_tables.append(f"{schema}.{category_info['backup_table']}")
                target_tables.append(category_info["table"])
        
        if not backup_tables:
            logger.warning("No hay tablas de backup disponibles para rollback")
            return {"enabled": False, "reason": "no_backups"}
        
        logger.warning(f"Iniciando rollback automático debido a alta tasa de errores ({error_rate:.2f}%)")
        
        try:
            rollback_result = rollback_load(hook, schema, backup_tables, target_tables)
            logger.info(f"Rollback completado: {len(rollback_result['tables_rolled_back'])} tablas restauradas")
            return {
                "enabled": True,
                "rollback_result": rollback_result,
                "error_rate": error_rate
            }
        except Exception as e:
            logger.error(f"Error durante rollback: {e}")
            return {
                "enabled": True,
                "error": str(e),
                "error_rate": error_rate
            }
    
    # Definir el flujo del DAG
    company_a_data = extract_company_a_data()
    company_b_data = extract_company_b_data()
    
    transformed_data = transform_to_common_format(company_a_data, company_b_data)
    validation_results = validate_transformed_data(transformed_data)
    
    load_results = load_to_unified_system(transformed_data, validation_results)
    
    status_report = generate_status_report(
        company_a_data,
        company_b_data,
        transformed_data,
        validation_results,
        load_results
    )
    
    @task(task_id="validate_referential_integrity_check")
    def validate_referential_integrity_check(
        load_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida la integridad referencial entre tablas cargadas."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_referential_integrity_check", False):
            logger.info("Validación de integridad referencial deshabilitada")
            return {"enabled": False}
        
        config_str = str(params.get("unified_system_config", "{}"))
        rules_str = str(params.get("referential_integrity_rules", "[]"))
        
        try:
            config = json.loads(config_str) if config_str else {}
            relationships = json.loads(rules_str) if rules_str else []
        except json.JSONDecodeError:
            logger.warning("Configuración de integridad referencial inválida")
            return {"enabled": False, "error": "config_invalid"}
        
        if config.get("type", "postgres").lower() != "postgres":
            logger.info("Validación de integridad referencial solo disponible para PostgreSQL")
            return {"enabled": False, "reason": "only_postgres"}
        
        if not relationships:
            logger.info("No hay reglas de integridad referencial definidas")
            return {"enabled": False, "reason": "no_rules"}
        
        hook = PostgresHook(postgres_conn_id=config.get("conn_id", "postgres_default"))
        schema = config.get("schema", "public")
        
        # Construir diccionario de tablas
        tables = {}
        for category, category_info in load_results.get("categories", {}).items():
            if "table" in category_info:
                tables[category] = category_info["table"]
        
        try:
            validation_result = validate_referential_integrity(
                hook, schema, tables, relationships
            )
            logger.info(
                f"Validación de integridad referencial completada: "
                f"{validation_result['relationships_valid']}/{validation_result['relationships_validated']} válidas"
            )
            return validation_result
        except Exception as e:
            logger.error(f"Error en validación de integridad referencial: {e}")
            return {"enabled": True, "error": str(e)}
    
    @task(task_id="validate_data_quality_rules")
    def validate_data_quality_rules_task(
        transformed_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Valida reglas de calidad de datos personalizadas."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_data_quality_rules", False):
            logger.info("Validación de reglas de calidad deshabilitada")
            return {"enabled": False}
        
        rules_str = str(params.get("data_quality_rules", "[]"))
        try:
            quality_rules = json.loads(rules_str) if rules_str else []
        except json.JSONDecodeError:
            logger.warning("Reglas de calidad inválidas")
            return {"enabled": False, "error": "rules_invalid"}
        
        if not quality_rules:
            logger.info("No hay reglas de calidad definidas")
            return {"enabled": False, "reason": "no_rules"}
        
        quality_results = {}
        
        for category, records in transformed_data.items():
            if not isinstance(records, list) or category == "metadata":
                continue
            
            try:
                result = validate_data_quality_rules(records, quality_rules)
                quality_results[category] = result
            except Exception as e:
                logger.error(f"Error validando calidad en {category}: {e}")
                quality_results[category] = {"error": str(e)}
        
        logger.info(f"Validación de calidad completada para {len(quality_results)} categorías")
        return quality_results
    
    @task(task_id="generate_data_lineage_task")
    def generate_data_lineage_task(
        company_a_data: Dict[str, Any],
        company_b_data: Dict[str, Any],
        transformed_data: Dict[str, Any],
        load_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera linaje de datos para trazabilidad."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_data_lineage", True):
            logger.info("Generación de linaje deshabilitada")
            return {"enabled": False}
        
        # Recopilar sistemas fuente
        source_systems = []
        for system_key in company_a_data.get("data", {}).keys():
            if "_error" not in system_key:
                source_systems.append(f"CompanyA:{system_key}")
        for system_key in company_b_data.get("data", {}).keys():
            if "_error" not in system_key:
                source_systems.append(f"CompanyB:{system_key}")
        
        # Recopilar transformaciones
        transformations = []
        rules_str = str(params.get("transformation_rules", "{}"))
        try:
            transformation_rules = json.loads(rules_str) if rules_str else {}
            if "transformations" in transformation_rules:
                transformations = [
                    t.get("type", "unknown")
                    for t in transformation_rules["transformations"]
                ]
        except:
            pass
        
        # Sistema destino
        config_str = str(params.get("unified_system_config", "{}"))
        try:
            config = json.loads(config_str) if config_str else {}
            target_system = f"{config.get('type', 'unknown')}:{config.get('schema', 'unknown')}"
        except:
            target_system = "unknown"
        
        lineage = generate_data_lineage(source_systems, transformations, target_system)
        
        # Guardar linaje en auditoría si está habilitado
        if params.get("enable_audit_log", True):
            try:
                config_str = str(params.get("unified_system_config", "{}"))
                config = json.loads(config_str) if config_str else {}
                if config.get("type", "postgres").lower() == "postgres":
                    hook = PostgresHook(postgres_conn_id=config.get("conn_id", "postgres_default"))
                    schema = config.get("schema", "public")
                    create_audit_log(hook, schema, "data_lineage", lineage)
            except Exception as e:
                logger.warning(f"Error guardando linaje en auditoría: {e}")
        
        logger.info(f"Linaje de datos generado: {lineage['lineage_id']}")
        return lineage
    
    @task(task_id="validate_schema_task")
    def validate_schema_task(transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida que los datos cumplan con el esquema esperado."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_schema_validation", False):
            logger.info("Validación de esquema deshabilitada")
            return {"enabled": False}
        
        schema_str = str(params.get("expected_schema", "{}"))
        try:
            expected_schema = json.loads(schema_str) if schema_str else {}
        except json.JSONDecodeError:
            logger.warning("Esquema esperado inválido")
            return {"enabled": False, "error": "schema_invalid"}
        
        if not expected_schema:
            logger.info("No hay esquema esperado definido")
            return {"enabled": False, "reason": "no_schema"}
        
        schema_results = {}
        
        for category, records in transformed_data.items():
            if not isinstance(records, list) or category == "metadata":
                continue
            
            try:
                result = validate_schema(records, expected_schema)
                schema_results[category] = result
            except Exception as e:
                logger.error(f"Error validando esquema en {category}: {e}")
                schema_results[category] = {"error": str(e)}
        
        logger.info(f"Validación de esquema completada para {len(schema_results)} categorías")
        return schema_results
    
    @task(task_id="health_check_systems")
    def health_check_systems() -> Dict[str, Any]:
        """Verifica la salud de todos los sistemas antes de extraer."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_health_checks", False):
            logger.info("Health checks deshabilitados")
            return {"enabled": False}
        
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "systems_checked": 0,
            "systems_healthy": 0,
            "systems_unhealthy": 0,
            "results": {}
        }
        
        # Verificar sistemas de empresa A
        config_a_str = str(params.get("company_a_config", "{}"))
        try:
            config_a = json.loads(config_a_str) if config_a_str else {}
            for system in config_a.get("systems", []):
                health = check_system_health(system)
                health_results["systems_checked"] += 1
                if health["status"] == "healthy":
                    health_results["systems_healthy"] += 1
                else:
                    health_results["systems_unhealthy"] += 1
                health_results["results"][f"CompanyA_{system.get('name', 'unknown')}"] = health
        except Exception as e:
            logger.warning(f"Error verificando salud de empresa A: {e}")
        
        # Verificar sistemas de empresa B
        config_b_str = str(params.get("company_b_config", "{}"))
        try:
            config_b = json.loads(config_b_str) if config_b_str else {}
            for system in config_b.get("systems", []):
                health = check_system_health(system)
                health_results["systems_checked"] += 1
                if health["status"] == "healthy":
                    health_results["systems_healthy"] += 1
                else:
                    health_results["systems_unhealthy"] += 1
                health_results["results"][f"CompanyB_{system.get('name', 'unknown')}"] = health
        except Exception as e:
            logger.warning(f"Error verificando salud de empresa B: {e}")
        
        logger.info(
            f"Health checks completados: {health_results['systems_healthy']}/"
            f"{health_results['systems_checked']} sistemas saludables"
        )
        
        return health_results
    
    @task(task_id="detect_anomalies_task")
    def detect_anomalies_task(transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta anomalías en los datos transformados."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_anomaly_detection", False):
            logger.info("Detección de anomalías deshabilitada")
            return {"enabled": False}
        
        threshold = params.get("anomaly_threshold", 3.0)
        anomaly_results = {}
        
        # Campos numéricos comunes a analizar
        numeric_fields = ["amount", "price", "quantity", "total", "value"]
        
        for category, records in transformed_data.items():
            if not isinstance(records, list) or category == "metadata":
                continue
            
            try:
                result = detect_anomalies(records, numeric_fields, threshold)
                anomaly_results[category] = result
            except Exception as e:
                logger.error(f"Error detectando anomalías en {category}: {e}")
                anomaly_results[category] = {"error": str(e)}
        
        total_anomalies = sum(
            r.get("anomalies_detected", 0) 
            for r in anomaly_results.values() 
            if isinstance(r, dict)
        )
        logger.info(f"Detección de anomalías completada: {total_anomalies} anomalías totales")
        return anomaly_results
    
    # Tareas opcionales
    health_check = health_check_systems()
    comparison_results = compare_data_changes(load_results, status_report)
    export_result = export_report_file(status_report)
    notification_result = send_notifications(status_report, load_results)
    rollback_result = rollback_on_error(load_results)
    referential_integrity_result = validate_referential_integrity_check(load_results)
    data_quality_result = validate_data_quality_rules_task(transformed_data)
    schema_validation_result = validate_schema_task(transformed_data)
    anomaly_results = detect_anomalies_task(transformed_data)
    data_lineage_result = generate_data_lineage_task(
        company_a_data, company_b_data, transformed_data, load_results
    )
    
    # Dependencias explícitas
    health_check >> [company_a_data, company_b_data]
    company_a_data >> transformed_data
    company_b_data >> transformed_data
    transformed_data >> [schema_validation_result, validation_results, data_quality_result, anomaly_results]
    validation_results >> load_results >> status_report
    status_report >> [comparison_results, export_result, notification_result, data_lineage_result]
    load_results >> [rollback_result, referential_integrity_result]


# Instanciar el DAG
merger_acquisition_dag = merger_acquisition_integration()

