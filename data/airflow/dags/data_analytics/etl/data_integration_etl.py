"""
DAG de Integración de Datos ETL
=================================

Automatiza la integración de datos entre sistemas:
- Extrae datos de CRM, Google Sheets y sistema de facturación
- Transforma y valida los datos
- Carga en data warehouse (PostgreSQL)
- Detecta inconsistencias y dispara alertas

Autor: Data Engineering Team
Fecha: 2025-01-01
"""

from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional, Callable, Tuple
from contextlib import contextmanager
from collections import defaultdict
from dataclasses import dataclass, field
import json
import logging
import os
import re
import time
import random
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor, as_completed
import statistics
import hashlib
from datetime import date
import gzip
import base64
import pickle
from difflib import SequenceMatcher

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)

# Intentar importar funciones de notificación
try:
    from data.airflow.plugins.etl_notifications import notify_slack, notify_email
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False
    logger.warning("Notificaciones no disponibles")

# Intentar importar Stats para métricas
try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False
    logger.warning("Stats no disponible, métricas deshabilitadas")


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def _retry_with_exponential_backoff(
    func: Callable,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
    retry_on_exceptions: tuple = (Exception,),
    *args,
    **kwargs
) -> Any:
    """
    Ejecuta una función con exponential backoff y jitter opcional.
    
    Args:
        func: Función a ejecutar
        max_retries: Número máximo de reintentos
        base_delay: Delay base en segundos
        max_delay: Delay máximo en segundos
        jitter: Si agregar jitter aleatorio
        retry_on_exceptions: Tupla de excepciones para retry
        *args, **kwargs: Argumentos para la función
    
    Returns:
        Resultado de la función
    """
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return func(*args, **kwargs)
        except retry_on_exceptions as e:
            last_exception = e
            if attempt == max_retries:
                break
            
            # Calcular delay con exponential backoff
            delay = min(base_delay * (2 ** attempt), max_delay)
            
            # Agregar jitter si está habilitado
            if jitter:
                jitter_amount = delay * 0.1 * random.random()
                delay = delay + jitter_amount
            
            logger.warning(
                f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s",
                extra={"error": str(e)[:200], "attempt": attempt + 1}
            )
            time.sleep(delay)
        except Exception as e:
            # Errores no relacionados con retry_on_exceptions no se reintentan
            raise
    
    raise last_exception


@contextmanager
def _track_metric(metric_name: str, tags: Optional[Dict[str, str]] = None):
    """Context manager para trackear métricas."""
    start_time = time.time()
    if STATS_AVAILABLE:
        try:
            Stats.incr(f"data_integration_etl.{metric_name}.start", tags=tags or {})
        except Exception:
            pass
    
    try:
        yield
        if STATS_AVAILABLE:
            try:
                duration_ms = (time.time() - start_time) * 1000
                Stats.incr(f"data_integration_etl.{metric_name}.success", tags=tags or {})
                Stats.timing(f"data_integration_etl.{metric_name}.duration_ms", int(duration_ms), tags=tags or {})
            except Exception:
                pass
    except Exception as e:
        if STATS_AVAILABLE:
            try:
                Stats.incr(
                    f"data_integration_etl.{metric_name}.error",
                    tags={**(tags or {}), "error_type": type(e).__name__}
                )
            except Exception:
                pass
        raise


def _log_progress(current: int, total: int, operation: str, interval: int = 10):
    """Log progreso de operaciones largas."""
    if current % interval == 0 or current == total:
        pct = (current / total * 100) if total > 0 else 0
        logger.info(
            f"Progress {operation}: {current}/{total} ({pct:.1f}%)",
            extra={"current": current, "total": total, "percentage": pct}
        )


# ============================================================================
# CIRCUIT BREAKER PATTERN
# ============================================================================

class CircuitBreaker:
    """Circuit breaker simple usando Airflow Variables."""
    
    @staticmethod
    def _get_key(dag_id: str) -> str:
        return f"circuit_breaker:{dag_id}"
    
    @staticmethod
    def is_open(dag_id: str, threshold: int = 5, reset_minutes: int = 15) -> bool:
        """Verifica si el circuit breaker está abierto."""
        try:
            from airflow.models import Variable
            key = CircuitBreaker._get_key(dag_id)
            data_str = Variable.get(key, default_var="{}")
            data = json.loads(data_str) if data_str else {}
            
            failures = data.get("failures", 0)
            last_failure = data.get("last_failure")
            
            if failures >= threshold:
                if last_failure:
                    last_failure_dt = pendulum.parse(last_failure)
                    if pendulum.now("UTC") - last_failure_dt < timedelta(minutes=reset_minutes):
                        return True
                    else:
                        # Reset automático
                        CircuitBreaker.reset(dag_id)
                        return False
            
            return False
        except Exception:
            return False
    
    @staticmethod
    def record_failure(dag_id: str) -> None:
        """Registra un fallo."""
        try:
            from airflow.models import Variable
            key = CircuitBreaker._get_key(dag_id)
            data_str = Variable.get(key, default_var="{}")
            data = json.loads(data_str) if data_str else {}
            
            data["failures"] = data.get("failures", 0) + 1
            data["last_failure"] = pendulum.now("UTC").isoformat()
            
            Variable.set(key, json.dumps(data))
        except Exception:
            pass
    
    @staticmethod
    def reset(dag_id: str) -> None:
        """Resetea el circuit breaker."""
        try:
            from airflow.models import Variable
            key = CircuitBreaker._get_key(dag_id)
            Variable.delete(key)
        except Exception:
            pass


# ============================================================================
# DEAD LETTER QUEUE (DLQ)
# ============================================================================

def _save_to_dlq(
    record: Dict[str, Any],
    error: str,
    source: str,
    dlq_table: str = "data_integration_dlq"
) -> None:
    """Guarda un registro fallido en Dead Letter Queue."""
    try:
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla DLQ si no existe
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {dlq_table} (
                        id SERIAL PRIMARY KEY,
                        source_id VARCHAR(255),
                        source_type VARCHAR(100),
                        source VARCHAR(50),
                        error_message TEXT,
                        record_data JSONB,
                        retry_count INTEGER DEFAULT 0,
                        last_retry_at TIMESTAMP,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        resolved_at TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_dlq_source_type 
                        ON {dlq_table}(source_type);
                    CREATE INDEX IF NOT EXISTS idx_dlq_resolved 
                        ON {dlq_table}(resolved_at) WHERE resolved_at IS NULL;
                """)
                
                # Insertar registro fallido
                cur.execute(f"""
                    INSERT INTO {dlq_table} (
                        source_id, source_type, source, error_message, record_data
                    ) VALUES (
                        %s, %s, %s, %s, %s
                    )
                    ON CONFLICT DO NOTHING
                """, (
                    record.get("source_id"),
                    record.get("source_type"),
                    source,
                    error[:1000],  # Limitar tamaño
                    json.dumps(record)
                ))
                
                conn.commit()
                
        if STATS_AVAILABLE:
            try:
                Stats.incr("data_integration_etl.dlq.saved", tags={"source": source})
            except Exception:
                pass
        
        logger.warning(f"Saved to DLQ: {error[:200]}", extra={"source": source})
    except Exception as e:
        logger.error(f"Failed to save to DLQ: {e}", exc_info=True)


# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Rate limiter simple usando tiempo de espera."""
    
    def __init__(self, max_calls: int = 100, period_seconds: float = 60.0):
        self.max_calls = max_calls
        self.period_seconds = period_seconds
        self.calls = []
    
    def wait_if_needed(self) -> None:
        """Espera si es necesario para respetar rate limit."""
        now = time.time()
        # Limpiar calls antiguos
        self.calls = [c for c in self.calls if now - c < self.period_seconds]
        
        if len(self.calls) >= self.max_calls:
            # Esperar hasta que haya espacio
            oldest_call = min(self.calls)
            wait_time = self.period_seconds - (now - oldest_call) + 0.1
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f}s")
                time.sleep(wait_time)
                # Limpiar de nuevo
                self.calls = [c for c in self.calls if now + wait_time - c < self.period_seconds]
        
        self.calls.append(time.time())


# ============================================================================
# CACHÉ SIMPLE
# ============================================================================

class SimpleCache:
    """Caché simple en memoria con TTL."""
    
    def __init__(self, maxsize: int = 1000, ttl: int = 3600):
        self.maxsize = maxsize
        self.ttl = ttl
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def _generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Genera clave de caché."""
        import hashlib
        key_parts = [prefix]
        for arg in args:
            key_parts.append(str(arg))
        for k, v in sorted(kwargs.items()):
            key_parts.append(f"{k}={v}")
        key_string = "|".join(key_parts)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Obtiene valor del caché."""
        if key not in self._cache:
            return None
        
        entry = self._cache[key]
        if time.time() > entry["expires_at"]:
            del self._cache[key]
            return None
        
        entry["hits"] = entry.get("hits", 0) + 1
        return entry["value"]
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Almacena valor en caché."""
        if len(self._cache) >= self.maxsize:
            # Limpiar entrada más antigua
            oldest_key = min(self._cache.keys(), key=lambda k: self._cache[k]["created_at"])
            del self._cache[oldest_key]
        
        ttl = ttl or self.ttl
        self._cache[key] = {
            "value": value,
            "created_at": time.time(),
            "expires_at": time.time() + ttl,
            "hits": 0
        }
    
    def clear(self) -> None:
        """Limpia todo el caché."""
        self._cache.clear()
    
    def stats(self) -> Dict[str, Any]:
        """Retorna estadísticas del caché."""
        total_hits = sum(e.get("hits", 0) for e in self._cache.values())
        return {
            "size": len(self._cache),
            "maxsize": self.maxsize,
            "total_hits": total_hits,
            "entries": len(self._cache)
        }


# ============================================================================
# DATA PROFILING
# ============================================================================

def _profile_data(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Genera perfil de datos."""
    if not records:
        return {
            "total_records": 0,
            "fields": {},
            "completeness": {},
            "data_types": {}
        }
    
    profile = {
        "total_records": len(records),
        "fields": {},
        "completeness": {},
        "data_types": {},
        "unique_values": {}
    }
    
    # Recopilar todos los campos
    all_fields = set()
    for record in records:
        all_fields.update(record.keys())
    
    # Analizar cada campo
    for field in all_fields:
        values = [r.get(field) for r in records]
        non_null = [v for v in values if v is not None]
        
        profile["fields"][field] = {
            "count": len(non_null),
            "null_count": len(values) - len(non_null),
            "completeness": len(non_null) / len(records) if records else 0
        }
        
        profile["completeness"][field] = profile["fields"][field]["completeness"]
        
        # Inferir tipo de dato
        if non_null:
            sample_value = non_null[0]
            if isinstance(sample_value, (int, float)):
                profile["data_types"][field] = "numeric"
            elif isinstance(sample_value, str):
                profile["data_types"][field] = "string"
            elif isinstance(sample_value, bool):
                profile["data_types"][field] = "boolean"
            elif isinstance(sample_value, dict):
                profile["data_types"][field] = "object"
            else:
                profile["data_types"][field] = "unknown"
        
        # Valores únicos (solo para campos pequeños)
        unique_vals = set(non_null)
        if len(unique_vals) <= 20:
            profile["unique_values"][field] = sorted(list(unique_vals))
    
    return profile


# ============================================================================
# CHECKPOINTING
# ============================================================================

def _save_checkpoint(
    checkpoint_name: str,
    data: Dict[str, Any],
    conn_id: str
) -> None:
    """Guarda checkpoint para procesamiento resumible."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_checkpoints (
                        id SERIAL PRIMARY KEY,
                        checkpoint_name VARCHAR(255) UNIQUE NOT NULL,
                        data JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_checkpoints_name 
                        ON data_integration_checkpoints(checkpoint_name);
                """)
                
                cur.execute("""
                    INSERT INTO data_integration_checkpoints (
                        checkpoint_name, data, updated_at
                    ) VALUES (
                        %s, %s, CURRENT_TIMESTAMP
                    )
                    ON CONFLICT (checkpoint_name) 
                    DO UPDATE SET
                        data = EXCLUDED.data,
                        updated_at = CURRENT_TIMESTAMP
                """, (checkpoint_name, json.dumps(data)))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error saving checkpoint: {e}", exc_info=True)


def _load_checkpoint(checkpoint_name: str, conn_id: str) -> Optional[Dict[str, Any]]:
    """Carga checkpoint."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT data FROM data_integration_checkpoints
                    WHERE checkpoint_name = %s
                """, (checkpoint_name,))
                
                result = cur.fetchone()
                if result:
                    return json.loads(result[0])
    except Exception as e:
        logger.error(f"Error loading checkpoint: {e}", exc_info=True)
    
    return None


# ============================================================================
# INCREMENTAL PROCESSING
# ============================================================================

def _get_last_sync_timestamp(conn_id: str, source: str) -> Optional[str]:
    """Obtiene timestamp de última sincronización."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_sync_log (
                        id SERIAL PRIMARY KEY,
                        source VARCHAR(100) NOT NULL,
                        last_sync_timestamp TIMESTAMP NOT NULL,
                        records_processed INTEGER DEFAULT 0,
                        status VARCHAR(50) DEFAULT 'success',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(source)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_sync_log_source 
                        ON data_integration_sync_log(source);
                """)
                
                cur.execute("""
                    SELECT last_sync_timestamp 
                    FROM data_integration_sync_log
                    WHERE source = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                """, (source,))
                
                result = cur.fetchone()
                if result:
                    return result[0].isoformat()
    except Exception as e:
        logger.error(f"Error getting last sync timestamp: {e}", exc_info=True)
    
    return None


def _save_sync_timestamp(conn_id: str, source: str, timestamp: str, records_count: int = 0) -> None:
    """Guarda timestamp de sincronización."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO data_integration_sync_log (
                        source, last_sync_timestamp, records_processed, status
                    ) VALUES (
                        %s, %s, %s, 'success'
                    )
                    ON CONFLICT (source) 
                    DO UPDATE SET
                        last_sync_timestamp = EXCLUDED.last_sync_timestamp,
                        records_processed = EXCLUDED.records_processed,
                        status = EXCLUDED.status,
                        created_at = CURRENT_TIMESTAMP
                """, (source, timestamp, records_count))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error saving sync timestamp: {e}", exc_info=True)


# ============================================================================
# PARALLEL PROCESSING HELPERS
# ============================================================================

def _chunk_list(data: List[Any], chunk_size: int) -> List[List[Any]]:
    """Divide una lista en chunks."""
    return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]


def _process_chunk_parallel(
    chunks: List[List[Dict[str, Any]]],
    processor_func: Callable[[List[Dict[str, Any]]], List[Dict[str, Any]]],
    max_workers: int = 4
) -> List[Dict[str, Any]]:
    """Procesa chunks en paralelo."""
    results = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_chunk = {
            executor.submit(processor_func, chunk): idx
            for idx, chunk in enumerate(chunks)
        }
        
        for future in as_completed(future_to_chunk):
            chunk_idx = future_to_chunk[future]
            try:
                chunk_result = future.result()
                results.extend(chunk_result)
                logger.debug(f"Chunk {chunk_idx + 1}/{len(chunks)} procesado")
            except Exception as e:
                logger.error(f"Error procesando chunk {chunk_idx}: {e}", exc_info=True)
                raise
    
    return results


# ============================================================================
# SCHEMA VALIDATION
# ============================================================================

@dataclass
class SchemaRule:
    """Regla de validación de esquema."""
    field: str
    required: bool = True
    field_type: Optional[type] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[Any]] = None
    custom_validator: Optional[Callable[[Any], bool]] = None


class SchemaValidator:
    """Validador de esquemas robusto."""
    
    def __init__(self, rules: List[SchemaRule]):
        self.rules = {rule.field: rule for rule in rules}
    
    def validate_record(self, record: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """Valida un registro contra las reglas."""
        errors = []
        
        for field_name, rule in self.rules.items():
            value = record.get(field_name)
            
            # Verificar campo requerido
            if rule.required and (value is None or value == ""):
                errors.append(f"Campo requerido '{field_name}' faltante o vacío")
                continue
            
            # Si no está presente y no es requerido, continuar
            if value is None:
                continue
            
            # Validar tipo
            if rule.field_type and not isinstance(value, rule.field_type):
                try:
                    # Intentar conversión
                    value = rule.field_type(value)
                except (ValueError, TypeError):
                    errors.append(f"Campo '{field_name}' debe ser de tipo {rule.field_type.__name__}")
                    continue
            
            # Validar rango numérico
            if rule.min_value is not None or rule.max_value is not None:
                try:
                    num_value = float(value)
                    if rule.min_value is not None and num_value < rule.min_value:
                        errors.append(f"Campo '{field_name}' debe ser >= {rule.min_value}")
                    if rule.max_value is not None and num_value > rule.max_value:
                        errors.append(f"Campo '{field_name}' debe ser <= {rule.max_value}")
                except (ValueError, TypeError):
                    errors.append(f"Campo '{field_name}' debe ser numérico para validación de rango")
            
            # Validar patrón regex
            if rule.pattern and isinstance(value, str):
                if not re.match(rule.pattern, value):
                    errors.append(f"Campo '{field_name}' no cumple con el patrón requerido")
            
            # Validar valores permitidos
            if rule.allowed_values and value not in rule.allowed_values:
                errors.append(f"Campo '{field_name}' debe ser uno de: {rule.allowed_values}")
            
            # Validador personalizado
            if rule.custom_validator and not rule.custom_validator(value):
                errors.append(f"Campo '{field_name}' falló validación personalizada")
        
        return len(errors) == 0, errors


# ============================================================================
# CURRENCY CONVERSION
# ============================================================================

def _convert_currency(amount: float, from_currency: str, to_currency: str, exchange_rates: Dict[str, float]) -> float:
    """Convierte una cantidad de una moneda a otra."""
    if from_currency == to_currency:
        return amount
    
    # Usar tasa de cambio si está disponible
    if from_currency in exchange_rates and to_currency in exchange_rates:
        # Convertir a USD primero (o moneda base)
        base_rate = exchange_rates.get("USD", 1.0)
        from_rate = exchange_rates.get(from_currency, 1.0)
        to_rate = exchange_rates.get(to_currency, 1.0)
        
        # Convertir: amount -> USD -> target currency
        usd_amount = amount / from_rate if from_rate != 0 else amount
        converted = usd_amount * to_rate
        return round(converted, 2)
    
    # Fallback: retornar original si no hay tasas
    logger.warning(f"No se encontraron tasas de cambio para {from_currency} -> {to_currency}")
    return amount


def _normalize_currency(records: List[Dict[str, Any]], target_currency: str = "USD") -> List[Dict[str, Any]]:
    """Normaliza todas las cantidades a una moneda objetivo."""
    # Tasas de cambio básicas (en producción, estas vendrían de una API o base de datos)
    exchange_rates = {
        "USD": 1.0,
        "EUR": 0.92,
        "GBP": 0.79,
        "MXN": 17.0,
        "CAD": 1.35,
        "AUD": 1.52,
    }
    
    normalized = []
    for record in records:
        if "amount" in record and "currency" in record:
            original_amount = record.get("amount", 0)
            original_currency = record.get("currency", target_currency)
            
            if original_currency != target_currency:
                converted_amount = _convert_currency(
                    float(original_amount),
                    original_currency,
                    target_currency,
                    exchange_rates
                )
                record["amount"] = converted_amount
                record["original_amount"] = original_amount
                record["original_currency"] = original_currency
                record["currency"] = target_currency
                record["currency_converted"] = True
            else:
                record["currency_converted"] = False
        
        normalized.append(record)
    
    return normalized


# ============================================================================
# OUTLIER DETECTION
# ============================================================================

def _detect_outliers(values: List[float], method: str = "iqr", threshold: float = 1.5) -> List[int]:
    """Detecta outliers en una lista de valores."""
    if len(values) < 3:
        return []
    
    outliers = []
    
    if method == "iqr":
        # Método IQR (Interquartile Range)
        q1 = statistics.quantiles(values, n=4)[0]
        q3 = statistics.quantiles(values, n=4)[2]
        iqr = q3 - q1
        
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        
        for idx, value in enumerate(values):
            if value < lower_bound or value > upper_bound:
                outliers.append(idx)
    
    elif method == "zscore":
        # Método Z-Score
        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0
        
        if stdev == 0:
            return []
        
        for idx, value in enumerate(values):
            z_score = abs((value - mean) / stdev)
            if z_score > threshold:
                outliers.append(idx)
    
    return outliers


def _analyze_outliers(records: List[Dict[str, Any]], field: str) -> Dict[str, Any]:
    """Analiza outliers en un campo numérico."""
    values = []
    valid_indices = []
    
    for idx, record in enumerate(records):
        value = record.get(field)
        if value is not None:
            try:
                values.append(float(value))
                valid_indices.append(idx)
            except (ValueError, TypeError):
                pass
    
    if len(values) < 3:
        return {
            "field": field,
            "outliers": [],
            "outlier_count": 0,
            "method": "insufficient_data"
        }
    
    outlier_indices = _detect_outliers(values, method="iqr")
    outlier_record_indices = [valid_indices[i] for i in outlier_indices]
    
    return {
        "field": field,
        "outliers": outlier_record_indices,
        "outlier_count": len(outlier_record_indices),
        "outlier_percentage": (len(outlier_record_indices) / len(values)) * 100,
        "method": "iqr",
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0,
    }


# ============================================================================
# TEMPORAL TREND ANALYSIS
# ============================================================================

def _analyze_temporal_trends(
    records: List[Dict[str, Any]],
    date_field: str = "created_at",
    value_field: str = "amount"
) -> Dict[str, Any]:
    """Analiza tendencias temporales en los datos."""
    # Agrupar por día
    daily_totals = defaultdict(float)
    daily_counts = defaultdict(int)
    
    for record in records:
        date_str = record.get(date_field)
        value = record.get(value_field)
        
        if date_str and value is not None:
            try:
                # Parsear fecha
                if isinstance(date_str, str):
                    date_obj = pendulum.parse(date_str).date()
                else:
                    date_obj = date_str
                
                day_key = date_obj.isoformat()
                daily_totals[day_key] += float(value)
                daily_counts[day_key] += 1
            except Exception:
                pass
    
    if not daily_totals:
        return {
            "trend": "insufficient_data",
            "daily_stats": {},
            "growth_rate": 0.0
        }
    
    # Ordenar por fecha
    sorted_days = sorted(daily_totals.keys())
    daily_values = [daily_totals[day] for day in sorted_days]
    
    # Calcular tasa de crecimiento
    growth_rate = 0.0
    if len(daily_values) > 1:
        first_value = daily_values[0]
        last_value = daily_values[-1]
        if first_value > 0:
            growth_rate = ((last_value - first_value) / first_value) * 100
    
    # Determinar tendencia
    if len(daily_values) >= 3:
        if daily_values[-1] > daily_values[0]:
            trend = "increasing"
        elif daily_values[-1] < daily_values[0]:
            trend = "decreasing"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "trend": trend,
        "daily_stats": {
            day: {
                "total": daily_totals[day],
                "count": daily_counts[day],
                "average": daily_totals[day] / daily_counts[day] if daily_counts[day] > 0 else 0
            }
            for day in sorted_days
        },
        "growth_rate": growth_rate,
        "period_days": len(sorted_days),
        "first_day": sorted_days[0] if sorted_days else None,
        "last_day": sorted_days[-1] if sorted_days else None,
    }


# ============================================================================
# DATA LINEAGE TRACKING
# ============================================================================

def _generate_data_lineage(
    record: Dict[str, Any],
    source_type: str,
    transformation_steps: List[str]
) -> Dict[str, Any]:
    """Genera información de lineage para un registro."""
    return {
        "source_type": source_type,
        "source_id": record.get("source_id"),
        "extracted_at": datetime.utcnow().isoformat(),
        "transformation_steps": transformation_steps,
        "lineage_id": hashlib.md5(
            f"{source_type}_{record.get('source_id')}_{datetime.utcnow().isoformat()}".encode()
        ).hexdigest(),
    }


def _save_data_lineage(conn_id: str, lineage_data: List[Dict[str, Any]]) -> None:
    """Guarda información de lineage en la base de datos."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_lineage (
                        id SERIAL PRIMARY KEY,
                        lineage_id VARCHAR(255) UNIQUE NOT NULL,
                        source_type VARCHAR(100) NOT NULL,
                        source_id VARCHAR(255),
                        extracted_at TIMESTAMP NOT NULL,
                        transformation_steps JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_lineage_source 
                        ON data_integration_lineage(source_type, source_id);
                    CREATE INDEX IF NOT EXISTS idx_lineage_lineage_id 
                        ON data_integration_lineage(lineage_id);
                """)
                
                for lineage in lineage_data:
                    cur.execute("""
                        INSERT INTO data_integration_lineage (
                            lineage_id, source_type, source_id, extracted_at, transformation_steps
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                        ON CONFLICT (lineage_id) DO NOTHING
                    """, (
                        lineage["lineage_id"],
                        lineage["source_type"],
                        lineage.get("source_id"),
                        lineage["extracted_at"],
                        json.dumps(lineage["transformation_steps"])
                    ))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error guardando data lineage: {e}", exc_info=True)


# ============================================================================
# DATA DEDUPLICATION
# ============================================================================

def _generate_record_hash(record: Dict[str, Any], fields: List[str]) -> str:
    """Genera un hash único para un registro basado en campos específicos."""
    hash_data = []
    for field in fields:
        value = record.get(field)
        if value is not None:
            hash_data.append(f"{field}:{str(value).lower().strip()}")
    
    if not hash_data:
        # Si no hay campos, usar todos los campos
        hash_data = [f"{k}:{str(v)}" for k, v in sorted(record.items()) if v is not None]
    
    hash_string = "|".join(sorted(hash_data))
    return hashlib.md5(hash_string.encode()).hexdigest()


def _deduplicate_records(
    records: List[Dict[str, Any]],
    dedup_fields: List[str] = ["email", "customer_id"],
    keep_strategy: str = "latest"
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Deduplica registros basándose en campos específicos.
    
    Args:
        records: Lista de registros a deduplicar
        dedup_fields: Campos a usar para deduplicación
        keep_strategy: Estrategia para mantener duplicados ("latest", "first", "most_complete")
    
    Returns:
        Tuple de (registros únicos, duplicados detectados)
    """
    seen_hashes = {}
    unique_records = []
    duplicates = []
    
    for record in records:
        record_hash = _generate_record_hash(record, dedup_fields)
        
        if record_hash in seen_hashes:
            # Duplicado detectado
            existing_record = seen_hashes[record_hash]["record"]
            existing_idx = seen_hashes[record_hash]["index"]
            
            # Decidir qué registro mantener según estrategia
            if keep_strategy == "latest":
                # Mantener el más reciente
                if record.get("updated_at") and existing_record.get("updated_at"):
                    if record["updated_at"] > existing_record["updated_at"]:
                        # Reemplazar el existente
                        unique_records[existing_idx] = record
                        duplicates.append(existing_record)
                    else:
                        duplicates.append(record)
                else:
                    # Si no hay timestamp, mantener el primero
                    duplicates.append(record)
            
            elif keep_strategy == "most_complete":
                # Mantener el que tiene más campos completos
                existing_completeness = sum(1 for v in existing_record.values() if v is not None)
                record_completeness = sum(1 for v in record.values() if v is not None)
                
                if record_completeness > existing_completeness:
                    unique_records[existing_idx] = record
                    duplicates.append(existing_record)
                else:
                    duplicates.append(record)
            
            else:  # "first"
                # Mantener el primero
                duplicates.append(record)
        else:
            # Nuevo registro único
            unique_records.append(record)
            seen_hashes[record_hash] = {
                "record": record,
                "index": len(unique_records) - 1
            }
    
    return unique_records, duplicates


# ============================================================================
# DATA ENRICHMENT
# ============================================================================

def _enrich_record(record: Dict[str, Any], enrichment_config: Dict[str, Any]) -> Dict[str, Any]:
    """ Enriquece un registro con información adicional."""
    enriched = record.copy()
    
    # Enriquecer email con dominio
    email = record.get("email")
    if email and "@" in email:
        domain = email.split("@")[1]
        enriched["email_domain"] = domain
        
        # Detectar si es email corporativo común
        common_domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
        enriched["is_corporate_email"] = domain not in common_domains
    
    # Enriquecer nombre completo
    first_name = record.get("first_name")
    last_name = record.get("last_name")
    if first_name or last_name:
        enriched["full_name"] = f"{first_name or ''} {last_name or ''}".strip()
    
    # Enriquecer con información de moneda si aplica
    if "amount" in record and "currency" in record:
        amount = record.get("amount", 0)
        currency = record.get("currency", "USD")
        enriched["amount_formatted"] = f"{currency} {amount:,.2f}"
    
    # Enriquecer con timestamp de procesamiento
    enriched["enriched_at"] = datetime.utcnow().isoformat()
    enriched["enrichment_version"] = enrichment_config.get("version", "1.0")
    
    return enriched


# ============================================================================
# DATA COMPRESSION
# ============================================================================

def _compress_data(data: bytes) -> bytes:
    """Comprime datos usando gzip."""
    return gzip.compress(data)


def _decompress_data(compressed_data: bytes) -> bytes:
    """Descomprime datos usando gzip."""
    return gzip.decompress(compressed_data)


def _serialize_and_compress(data: Dict[str, Any]) -> str:
    """Serializa y comprime datos para almacenamiento eficiente."""
    serialized = pickle.dumps(data)
    compressed = _compress_data(serialized)
    return base64.b64encode(compressed).decode('utf-8')


def _decompress_and_deserialize(compressed_str: str) -> Dict[str, Any]:
    """Descomprime y deserializa datos."""
    compressed = base64.b64decode(compressed_str.encode('utf-8'))
    decompressed = _decompress_data(compressed)
    return pickle.loads(decompressed)


# ============================================================================
# TABLE PARTITIONING
# ============================================================================

def _create_partitioned_table(conn_id: str, table_name: str, partition_column: str = "created_at") -> None:
    """Crea una tabla particionada por fecha."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla particionada si no existe
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {table_name} (
                        id SERIAL,
                        source_id VARCHAR(255) NOT NULL,
                        source_type VARCHAR(100) NOT NULL,
                        customer_id VARCHAR(255),
                        email VARCHAR(255),
                        first_name VARCHAR(255),
                        last_name VARCHAR(255),
                        phone VARCHAR(50),
                        company VARCHAR(255),
                        amount DECIMAL(15, 2),
                        currency VARCHAR(10),
                        status VARCHAR(50),
                        raw_data JSONB,
                        validation_errors JSONB,
                        validation_warnings JSONB,
                        {partition_column} TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        PRIMARY KEY (id, {partition_column})
                    ) PARTITION BY RANGE ({partition_column});
                """)
                
                # Crear partición para el mes actual y siguiente
                current_date = datetime.utcnow().date()
                next_month = (current_date.replace(day=1) + timedelta(days=32)).replace(day=1)
                
                # Partición actual
                partition_name = f"{table_name}_{current_date.strftime('%Y_%m')}"
                start_date = current_date.replace(day=1)
                end_date = next_month
                
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {partition_name} PARTITION OF {table_name}
                    FOR VALUES FROM (%s) TO (%s)
                """, (start_date, end_date))
                
                # Partición siguiente
                next_partition_name = f"{table_name}_{next_month.strftime('%Y_%m')}"
                next_end_date = (next_month + timedelta(days=32)).replace(day=1)
                
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {next_partition_name} PARTITION OF {table_name}
                    FOR VALUES FROM (%s) TO (%s)
                """, (next_month, next_end_date))
                
                conn.commit()
                logger.info(f"Tabla particionada {table_name} creada/actualizada")
    except Exception as e:
        logger.error(f"Error creando tabla particionada: {e}", exc_info=True)


# ============================================================================
# BACKUP AND ROLLBACK
# ============================================================================

def _create_backup(conn_id: str, table_name: str, backup_name: Optional[str] = None) -> str:
    """Crea un backup de una tabla antes de operaciones críticas."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        if not backup_name:
            backup_name = f"{table_name}_backup_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de backup
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {backup_name} AS
                    SELECT * FROM {table_name}
                    WHERE updated_at >= CURRENT_DATE - INTERVAL '7 days'
                """)
                
                # Crear índices en backup
                cur.execute(f"""
                    CREATE INDEX IF NOT EXISTS idx_{backup_name}_source_id 
                        ON {backup_name}(source_id, source_type);
                    CREATE INDEX IF NOT EXISTS idx_{backup_name}_customer_id 
                        ON {backup_name}(customer_id);
                """)
                
                # Obtener conteo
                cur.execute(f"SELECT COUNT(*) FROM {backup_name}")
                count = cur.fetchone()[0]
                
                conn.commit()
                
                logger.info(f"Backup creado: {backup_name} con {count} registros")
                return backup_name
    except Exception as e:
        logger.error(f"Error creando backup: {e}", exc_info=True)
        return ""


def _rollback_from_backup(
    conn_id: str,
    table_name: str,
    backup_name: str,
    condition: Optional[str] = None
) -> bool:
    """Restaura datos desde un backup."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Verificar que backup existe
                cur.execute(f"""
                    SELECT COUNT(*) FROM information_schema.tables 
                    WHERE table_name = %s
                """, (backup_name,))
                
                if cur.fetchone()[0] == 0:
                    logger.error(f"Backup {backup_name} no existe")
                    return False
                
                # Restaurar datos
                if condition:
                    restore_sql = f"""
                        UPDATE {table_name} t
                        SET 
                            customer_id = b.customer_id,
                            email = b.email,
                            first_name = b.first_name,
                            last_name = b.last_name,
                            phone = b.phone,
                            company = b.company,
                            amount = b.amount,
                            currency = b.currency,
                            status = b.status,
                            raw_data = b.raw_data,
                            updated_at = CURRENT_TIMESTAMP
                        FROM {backup_name} b
                        WHERE t.source_id = b.source_id 
                        AND t.source_type = b.source_type
                        AND {condition}
                    """
                else:
                    restore_sql = f"""
                        UPDATE {table_name} t
                        SET 
                            customer_id = b.customer_id,
                            email = b.email,
                            first_name = b.first_name,
                            last_name = b.last_name,
                            phone = b.phone,
                            company = b.company,
                            amount = b.amount,
                            currency = b.currency,
                            status = b.status,
                            raw_data = b.raw_data,
                            updated_at = CURRENT_TIMESTAMP
                        FROM {backup_name} b
                        WHERE t.source_id = b.source_id 
                        AND t.source_type = b.source_type
                    """
                
                cur.execute(restore_sql)
                restored_count = cur.rowcount
                
                conn.commit()
                
                logger.info(f"Rollback completado: {restored_count} registros restaurados desde {backup_name}")
                return True
    except Exception as e:
        logger.error(f"Error en rollback: {e}", exc_info=True)
        return False


# ============================================================================
# DATA RECONCILIATION
# ============================================================================

def _similarity_score(str1: str, str2: str) -> float:
    """Calcula similitud entre dos strings (0-1)."""
    if not str1 or not str2:
        return 0.0
    return SequenceMatcher(None, str1.lower().strip(), str2.lower().strip()).ratio()


def _reconcile_records(
    records: List[Dict[str, Any]],
    match_fields: List[str] = ["email", "customer_id"],
    similarity_threshold: float = 0.85
) -> Dict[str, Any]:
    """
    Reconcilia registros entre diferentes fuentes.
    
    Args:
        records: Lista de registros a reconciliar
        match_fields: Campos a usar para matching
        similarity_threshold: Umbral de similitud (0-1)
    
    Returns:
        Dict con resultados de reconciliación
    """
    reconciliation_results = {
        "matched_pairs": [],
        "unmatched": [],
        "conflicts": [],
        "total_records": len(records)
    }
    
    # Agrupar por fuente
    by_source = defaultdict(list)
    for record in records:
        source_type = record.get("source_type", "unknown")
        by_source[source_type].append(record)
    
    # Comparar entre fuentes
    sources = list(by_source.keys())
    for i, source1 in enumerate(sources):
        for source2 in sources[i+1:]:
            for record1 in by_source[source1]:
                best_match = None
                best_score = 0.0
                
                for record2 in by_source[source2]:
                    # Calcular score de matching
                    scores = []
                    for field in match_fields:
                        val1 = record1.get(field, "")
                        val2 = record2.get(field, "")
                        if val1 and val2:
                            scores.append(_similarity_score(str(val1), str(val2)))
                    
                    if scores:
                        avg_score = sum(scores) / len(scores)
                        if avg_score > best_score:
                            best_score = avg_score
                            best_match = record2
                
                if best_match and best_score >= similarity_threshold:
                    # Verificar conflictos
                    conflicts = []
                    for field in ["email", "amount", "status"]:
                        val1 = record1.get(field)
                        val2 = best_match.get(field)
                        if val1 and val2 and val1 != val2:
                            conflicts.append({
                                "field": field,
                                "source1_value": val1,
                                "source2_value": val2
                            })
                    
                    reconciliation_results["matched_pairs"].append({
                        "source1": source1,
                        "source1_id": record1.get("source_id"),
                        "source2": source2,
                        "source2_id": best_match.get("source_id"),
                        "similarity_score": best_score,
                        "conflicts": conflicts
                    })
                    
                    if conflicts:
                        reconciliation_results["conflicts"].append({
                            "pair": (record1.get("source_id"), best_match.get("source_id")),
                            "conflicts": conflicts
                        })
                else:
                    reconciliation_results["unmatched"].append({
                        "source_type": source1,
                        "source_id": record1.get("source_id")
                    })
    
    return reconciliation_results


# ============================================================================
# PII DETECTION
# ============================================================================

def _detect_pii(record: Dict[str, Any]) -> Dict[str, Any]:
    """Detecta información personal identificable (PII) en un registro."""
    pii_fields = {
        "email": False,
        "phone": False,
        "ssn": False,
        "credit_card": False,
        "ip_address": False
    }
    
    # Detectar email
    email = record.get("email", "")
    if email and "@" in email:
        pii_fields["email"] = True
    
    # Detectar teléfono
    phone = record.get("phone", "")
    if phone:
        # Patrones comunes de teléfono
        phone_patterns = [
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # US format
            r'\+?\d{1,3}[-.\s]?\d{1,4}[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        ]
        for pattern in phone_patterns:
            if re.search(pattern, str(phone)):
                pii_fields["phone"] = True
                break
    
    # Detectar SSN (US)
    for field in record.values():
        if isinstance(field, str):
            if re.search(r'\b\d{3}-\d{2}-\d{4}\b', field):
                pii_fields["ssn"] = True
                break
    
    # Detectar tarjeta de crédito
    for field in record.values():
        if isinstance(field, str):
            # Patrón simplificado (no detecta todos los formatos)
            if re.search(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b', field):
                pii_fields["credit_card"] = True
                break
    
    # Detectar IP
    for field in record.values():
        if isinstance(field, str):
            if re.search(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', field):
                pii_fields["ip_address"] = True
                break
    
    return {
        "has_pii": any(pii_fields.values()),
        "pii_fields": [k for k, v in pii_fields.items() if v],
        "pii_details": pii_fields
    }


def _mask_pii(record: Dict[str, Any], fields_to_mask: List[str] = ["email", "phone"]) -> Dict[str, Any]:
    """Enmascara campos PII en un registro."""
    masked = record.copy()
    
    for field in fields_to_mask:
        value = masked.get(field)
        if value:
            # Enmascarar email: user@domain.com -> u***@d***.com
            if field == "email" and "@" in str(value):
                parts = str(value).split("@")
                if len(parts) == 2:
                    user = parts[0]
                    domain = parts[1].split(".")
                    masked[field] = f"{user[0]}***@{domain[0][0]}***.{domain[-1]}" if domain else f"{user[0]}***@{domain[0][0]}***"
            
            # Enmascarar teléfono: 123-456-7890 -> ***-***-7890
            elif field == "phone":
                phone_str = str(value).replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
                if len(phone_str) >= 4:
                    masked[field] = f"***-***-{phone_str[-4:]}"
                else:
                    masked[field] = "***-***-****"
            
            else:
                masked[field] = "***"
    
    masked["pii_masked"] = True
    masked["pii_masked_at"] = datetime.utcnow().isoformat()
    
    return masked


# ============================================================================
# COST TRACKING
# ============================================================================

def _track_operation_cost(
    operation: str,
    duration_seconds: float,
    records_processed: int,
    resource_type: str = "compute"
) -> Dict[str, Any]:
    """Calcula y trackea el costo estimado de una operación."""
    # Costos estimados (en producción vendrían de configuración)
    cost_per_second = {
        "compute": 0.0001,  # $0.0001 por segundo
        "storage": 0.000023,  # $0.000023 por GB por segundo
        "network": 0.00001,  # $0.00001 por GB transferido
    }
    
    base_cost = cost_per_second.get(resource_type, 0.0001) * duration_seconds
    cost_per_record = base_cost / records_processed if records_processed > 0 else 0
    
    return {
        "operation": operation,
        "duration_seconds": duration_seconds,
        "records_processed": records_processed,
        "resource_type": resource_type,
        "estimated_cost_usd": round(base_cost, 6),
        "cost_per_record": round(cost_per_record, 8),
        "timestamp": datetime.utcnow().isoformat()
    }


def _save_cost_tracking(conn_id: str, cost_data: Dict[str, Any]) -> None:
    """Guarda información de costos en la base de datos."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_cost_tracking (
                        id SERIAL PRIMARY KEY,
                        operation VARCHAR(100) NOT NULL,
                        duration_seconds NUMERIC(10, 3),
                        records_processed INTEGER,
                        resource_type VARCHAR(50),
                        estimated_cost_usd NUMERIC(10, 6),
                        cost_per_record NUMERIC(12, 8),
                        timestamp TIMESTAMP NOT NULL,
                        dag_run_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_cost_operation 
                        ON data_integration_cost_tracking(operation);
                    CREATE INDEX IF NOT EXISTS idx_cost_timestamp 
                        ON data_integration_cost_tracking(timestamp DESC);
                """)
                
                cur.execute("""
                    INSERT INTO data_integration_cost_tracking (
                        operation, duration_seconds, records_processed, resource_type,
                        estimated_cost_usd, cost_per_record, timestamp, dag_run_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    cost_data["operation"],
                    cost_data["duration_seconds"],
                    cost_data["records_processed"],
                    cost_data["resource_type"],
                    cost_data["estimated_cost_usd"],
                    cost_data["cost_per_record"],
                    cost_data["timestamp"],
                    cost_data.get("dag_run_id")
                ))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error guardando cost tracking: {e}", exc_info=True)


# ============================================================================
# DATA QUALITY SCORING
# ============================================================================

def _calculate_data_quality_score(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calcula un score de calidad de datos para un registro (0-100).
    
    Criterios:
    - Completeness: Campos obligatorios presentes
    - Validity: Valores dentro de rangos esperados
    - Consistency: Valores consistentes entre campos relacionados
    - Accuracy: Formato y estructura correctos
    """
    score = 100.0
    deductions = []
    
    # 1. Completeness (40 puntos)
    required_fields = ["email", "customer_id", "source_id", "source_type"]
    missing_fields = [f for f in required_fields if not record.get(f)]
    
    if missing_fields:
        completeness_deduction = (len(missing_fields) / len(required_fields)) * 40
        score -= completeness_deduction
        deductions.append({
            "aspect": "completeness",
            "deduction": completeness_deduction,
            "reason": f"Missing fields: {', '.join(missing_fields)}"
        })
    
    # 2. Validity (30 puntos)
    validity_issues = []
    
    # Email válido
    email = record.get("email", "")
    if email and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        validity_issues.append("invalid_email")
    
    # Monto positivo si existe
    amount = record.get("amount")
    if amount is not None and float(amount) < 0:
        validity_issues.append("negative_amount")
    
    # Status válido
    status = record.get("status", "")
    valid_statuses = ["active", "inactive", "pending", "cancelled", "completed"]
    if status and status.lower() not in valid_statuses:
        validity_issues.append("invalid_status")
    
    if validity_issues:
        validity_deduction = (len(validity_issues) / 3) * 30
        score -= validity_deduction
        deductions.append({
            "aspect": "validity",
            "deduction": validity_deduction,
            "reason": f"Validity issues: {', '.join(validity_issues)}"
        })
    
    # 3. Consistency (20 puntos)
    consistency_issues = []
    
    # Email y customer_id deben ser consistentes
    email_domain = email.split("@")[1] if "@" in email else None
    company = record.get("company", "").lower()
    if email_domain and company:
        domain_match = company.replace(" ", "") in email_domain.replace(".", "")
        if not domain_match and len(company) > 3:
            consistency_issues.append("email_company_mismatch")
    
    # Nombre completo debe tener al menos first_name o last_name
    first_name = record.get("first_name", "")
    last_name = record.get("last_name", "")
    if not first_name and not last_name:
        consistency_issues.append("missing_name")
    
    if consistency_issues:
        consistency_deduction = (len(consistency_issues) / 2) * 20
        score -= consistency_deduction
        deductions.append({
            "aspect": "consistency",
            "deduction": consistency_deduction,
            "reason": f"Consistency issues: {', '.join(consistency_issues)}"
        })
    
    # 4. Accuracy (10 puntos)
    accuracy_issues = []
    
    # Teléfono debe tener formato razonable
    phone = record.get("phone", "")
    if phone and len(phone.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")) < 10:
        accuracy_issues.append("invalid_phone_format")
    
    if accuracy_issues:
        accuracy_deduction = (len(accuracy_issues) / 1) * 10
        score -= accuracy_deduction
        deductions.append({
            "aspect": "accuracy",
            "deduction": accuracy_deduction,
            "reason": f"Accuracy issues: {', '.join(accuracy_issues)}"
        })
    
    # Asegurar score entre 0 y 100
    score = max(0.0, min(100.0, score))
    
    # Determinar nivel de calidad
    if score >= 90:
        quality_level = "excellent"
    elif score >= 75:
        quality_level = "good"
    elif score >= 60:
        quality_level = "fair"
    elif score >= 40:
        quality_level = "poor"
    else:
        quality_level = "critical"
    
    return {
        "score": round(score, 2),
        "quality_level": quality_level,
        "deductions": deductions,
        "total_deductions": sum(d["deduction"] for d in deductions),
        "calculated_at": datetime.utcnow().isoformat()
    }


def _calculate_dataset_quality_score(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calcula score de calidad para todo el dataset."""
    if not records:
        return {
            "average_score": 0.0,
            "quality_distribution": {},
            "total_records": 0
        }
    
    scores = []
    quality_levels = defaultdict(int)
    
    for record in records:
        quality_result = _calculate_data_quality_score(record)
        record["quality_score"] = quality_result
        scores.append(quality_result["score"])
        quality_levels[quality_result["quality_level"]] += 1
    
    avg_score = sum(scores) / len(scores) if scores else 0.0
    
    return {
        "average_score": round(avg_score, 2),
        "quality_distribution": dict(quality_levels),
        "total_records": len(records),
        "excellent_count": quality_levels.get("excellent", 0),
        "good_count": quality_levels.get("good", 0),
        "fair_count": quality_levels.get("fair", 0),
        "poor_count": quality_levels.get("poor", 0),
        "critical_count": quality_levels.get("critical", 0),
        "calculated_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# AUTOMATED DATA QUALITY RULES
# ============================================================================

@dataclass
class DataQualityRule:
    """Regla de calidad de datos."""
    name: str
    description: str
    check_function: Callable[[Dict[str, Any]], bool]
    severity: str = "warning"  # warning, error, critical
    auto_fix: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None


class DataQualityRuleEngine:
    """Motor de reglas de calidad de datos."""
    
    def __init__(self):
        self.rules: List[DataQualityRule] = []
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Registra reglas de calidad por defecto."""
        
        # Regla 1: Email requerido
        self.rules.append(DataQualityRule(
            name="email_required",
            description="Email field is required",
            check_function=lambda r: bool(r.get("email")),
            severity="error"
        ))
        
        # Regla 2: Email válido
        self.rules.append(DataQualityRule(
            name="email_valid_format",
            description="Email must be in valid format",
            check_function=lambda r: not r.get("email") or bool(re.match(
                r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
                r.get("email", "")
            )),
            severity="error"
        ))
        
        # Regla 3: Monto no negativo
        self.rules.append(DataQualityRule(
            name="amount_non_negative",
            description="Amount must be non-negative",
            check_function=lambda r: r.get("amount") is None or float(r.get("amount", 0)) >= 0,
            severity="warning"
        ))
        
        # Regla 4: Nombre completo
        self.rules.append(DataQualityRule(
            name="name_completeness",
            description="Either first_name or last_name should be present",
            check_function=lambda r: bool(r.get("first_name") or r.get("last_name")),
            severity="warning"
        ))
        
        # Regla 5: Customer ID consistente
        self.rules.append(DataQualityRule(
            name="customer_id_format",
            description="Customer ID should be alphanumeric",
            check_function=lambda r: not r.get("customer_id") or bool(re.match(
                r'^[a-zA-Z0-9_-]+$',
                r.get("customer_id", "")
            )),
            severity="warning"
        ))
    
    def validate_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Valida un registro contra todas las reglas."""
        results = {
            "passed": [],
            "failed": [],
            "auto_fixed": []
        }
        
        for rule in self.rules:
            try:
                if rule.check_function(record):
                    results["passed"].append(rule.name)
                else:
                    results["failed"].append({
                        "rule": rule.name,
                        "description": rule.description,
                        "severity": rule.severity
                    })
                    
                    # Intentar auto-fix si está disponible
                    if rule.auto_fix:
                        try:
                            fixed_record = rule.auto_fix(record)
                            if fixed_record != record:
                                record.update(fixed_record)
                                results["auto_fixed"].append(rule.name)
                        except Exception as e:
                            logger.warning(f"Auto-fix failed for rule {rule.name}: {e}")
            except Exception as e:
                logger.error(f"Error evaluating rule {rule.name}: {e}")
                results["failed"].append({
                    "rule": rule.name,
                    "description": rule.description,
                    "severity": "error",
                    "error": str(e)
                })
        
        return results
    
    def validate_dataset(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Valida un dataset completo."""
        results = {
            "total_records": len(records),
            "records_passed": 0,
            "records_failed": 0,
            "rule_violations": defaultdict(int),
            "severity_counts": defaultdict(int)
        }
        
        for record in records:
            validation = self.validate_record(record)
            
            if len(validation["failed"]) == 0:
                results["records_passed"] += 1
            else:
                results["records_failed"] += 1
                for failure in validation["failed"]:
                    results["rule_violations"][failure["rule"]] += 1
                    results["severity_counts"][failure["severity"]] += 1
        
        results["rule_violations"] = dict(results["rule_violations"])
        results["severity_counts"] = dict(results["severity_counts"])
        results["pass_rate"] = (
            results["records_passed"] / results["total_records"] * 100
            if results["total_records"] > 0 else 0.0
        )
        
        return results


# ============================================================================
# INTELLIGENT ALERTING
# ============================================================================

class AlertRule:
    """Regla de alerta inteligente."""
    
    def __init__(
        self,
        name: str,
        condition: Callable[[Dict[str, Any]], bool],
        severity: str = "warning",
        message_template: str = "",
        notify_slack: bool = True,
        notify_email: bool = False
    ):
        self.name = name
        self.condition = condition
        self.severity = severity
        self.message_template = message_template
        self.notify_slack = notify_slack
        self.notify_email = notify_email


class IntelligentAlerting:
    """Sistema de alertas inteligentes."""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Registra reglas de alerta por defecto."""
        
        # Regla 1: Alta tasa de errores
        self.rules.append(AlertRule(
            name="high_error_rate",
            condition=lambda data: (
                data.get("stats", {}).get("errors", 0) / 
                max(data.get("stats", {}).get("total", 1), 1) > 0.1
            ),
            severity="critical",
            message_template="Alta tasa de errores: {error_rate:.2%}",
            notify_slack=True,
            notify_email=True
        ))
        
        # Regla 2: Calidad de datos baja
        self.rules.append(AlertRule(
            name="low_data_quality",
            condition=lambda data: (
                data.get("quality_scoring", {}).get("average_score", 100) < 60
            ),
            severity="warning",
            message_template="Calidad de datos baja: score promedio {avg_score}/100",
            notify_slack=True
        ))
        
        # Regla 3: Muchos conflictos en reconciliación
        self.rules.append(AlertRule(
            name="many_reconciliation_conflicts",
            condition=lambda data: (
                data.get("reconciliation", {}).get("conflicts", 0) > 10
            ),
            severity="warning",
            message_template="Muchos conflictos en reconciliación: {conflicts} conflictos",
            notify_slack=True
        ))
        
        # Regla 4: PII detectado y no enmascarado
        self.rules.append(AlertRule(
            name="pii_detected_not_masked",
            condition=lambda data: (
                data.get("pii_detection", {}).get("total_with_pii", 0) > 0 and
                not data.get("pii_detection", {}).get("masking_enabled", False)
            ),
            severity="warning",
            message_template="PII detectado pero no enmascarado: {pii_count} registros",
            notify_slack=True
        ))
        
        # Regla 5: Tasa de validación baja
        self.rules.append(AlertRule(
            name="low_validation_rate",
            condition=lambda data: (
                data.get("quality_rules", {}).get("pass_rate", 100) < 80
            ),
            severity="error",
            message_template="Tasa de validación baja: {pass_rate:.2f}%",
            notify_slack=True,
            notify_email=True
        ))
    
    def evaluate(
        self,
        data: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Evalúa todas las reglas y genera alertas."""
        alerts = []
        
        for rule in self.rules:
            try:
                if rule.condition(data):
                    # Formatear mensaje
                    message = rule.message_template.format(**data)
                    
                    alert = {
                        "rule": rule.name,
                        "severity": rule.severity,
                        "message": message,
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": data,
                        "notify_slack": rule.notify_slack,
                        "notify_email": rule.notify_email
                    }
                    
                    alerts.append(alert)
                    
                    # Enviar notificaciones si está disponible
                    if rule.notify_slack and NOTIFICATIONS_AVAILABLE:
                        try:
                            notify_slack(f"⚠️ {rule.severity.upper()}: {message}")
                        except Exception as e:
                            logger.warning(f"Error enviando alerta a Slack: {e}")
                    
                    if rule.notify_email and NOTIFICATIONS_AVAILABLE:
                        try:
                            notify_email(
                                subject=f"Data Integration Alert: {rule.name}",
                                body=message
                            )
                        except Exception as e:
                            logger.warning(f"Error enviando alerta por email: {e}")
            except Exception as e:
                logger.error(f"Error evaluando regla {rule.name}: {e}", exc_info=True)
        
        return alerts


# ============================================================================
# REAL-TIME MONITORING
# ============================================================================

def _track_operation_metrics(
    operation: str,
    metrics: Dict[str, Any],
    conn_id: str
) -> None:
    """Guarda métricas de operación en tiempo real."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_metrics (
                        id SERIAL PRIMARY KEY,
                        operation VARCHAR(100) NOT NULL,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_value NUMERIC(15, 3),
                        metric_type VARCHAR(50),
                        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                        dag_run_id VARCHAR(255),
                        metadata JSONB
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_metrics_operation 
                        ON data_integration_metrics(operation, timestamp DESC);
                    CREATE INDEX IF NOT EXISTS idx_metrics_name 
                        ON data_integration_metrics(metric_name);
                """)
                
                for metric_name, metric_value in metrics.items():
                    cur.execute("""
                        INSERT INTO data_integration_metrics (
                            operation, metric_name, metric_value, timestamp, dag_run_id
                        ) VALUES (
                            %s, %s, %s, CURRENT_TIMESTAMP, %s
                        )
                    """, (
                        operation,
                        metric_name,
                        float(metric_value) if isinstance(metric_value, (int, float)) else None,
                        metrics.get("dag_run_id")
                    ))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error guardando métricas: {e}", exc_info=True)


def _calculate_health_score(
    extracted_data: Dict[str, Any],
    transformed_data: Dict[str, Any],
    validated_data: Dict[str, Any],
    loaded_data: Dict[str, Any]
) -> Dict[str, Any]:
    """Calcula un score de salud general del pipeline."""
    health_score = 100.0
    components = {}
    
    # 1. Extracción (30 puntos)
    extraction_total = (
        extracted_data.get("crm", {}).get("count", 0) +
        extracted_data.get("sheets", {}).get("count", 0) +
        extracted_data.get("billing", {}).get("count", 0)
    )
    extraction_score = min(30.0, (extraction_total / 1000) * 30) if extraction_total > 0 else 0
    components["extraction"] = extraction_score
    health_score = min(100.0, extraction_score)
    
    # 2. Transformación (25 puntos)
    transform_stats = transformed_data.get("stats", {})
    transform_total = sum(s.get("input", 0) for s in transform_stats.values())
    transform_output = sum(s.get("output", 0) for s in transform_stats.values())
    transform_success_rate = (transform_output / transform_total * 100) if transform_total > 0 else 0
    transform_score = (transform_success_rate / 100) * 25
    components["transformation"] = transform_score
    health_score = min(100.0, health_score + transform_score)
    
    # 3. Validación (25 puntos)
    validation_results = validated_data.get("validation", {}).get("results", {})
    validation_total = validation_results.get("total", 0)
    validation_valid = validation_results.get("valid", 0)
    validation_rate = (validation_valid / validation_total * 100) if validation_total > 0 else 0
    validation_score = (validation_rate / 100) * 25
    components["validation"] = validation_score
    health_score = min(100.0, health_score + validation_score)
    
    # 4. Carga (20 puntos)
    load_stats = loaded_data.get("load", {})
    load_total = load_stats.get("loaded_count", 0) + load_stats.get("error_count", 0)
    load_success = load_stats.get("loaded_count", 0)
    load_rate = (load_success / load_total * 100) if load_total > 0 else 0
    load_score = (load_rate / 100) * 20
    components["load"] = load_score
    health_score = min(100.0, health_score + load_score)
    
    # Determinar estado de salud
    if health_score >= 90:
        health_status = "excellent"
    elif health_score >= 75:
        health_status = "good"
    elif health_score >= 60:
        health_status = "fair"
    elif health_score >= 40:
        health_status = "poor"
    else:
        health_status = "critical"
    
    return {
        "health_score": round(health_score, 2),
        "health_status": health_status,
        "components": components,
        "calculated_at": datetime.utcnow().isoformat()
    }


# ============================================================================
# DATA DRIFT DETECTION
# ============================================================================

def _detect_data_drift(
    current_data: List[Dict[str, Any]],
    baseline_data: Optional[List[Dict[str, Any]]],
    fields: List[str],
    conn_id: str,
    threshold: float = 0.05
) -> Dict[str, Any]:
    """
    Detecta deriva de datos comparando distribución actual con baseline.
    
    Args:
        current_data: Datos actuales
        baseline_data: Datos de referencia (baseline)
        fields: Campos a analizar
        conn_id: Connection ID para PostgreSQL
        threshold: Umbral de significancia (p-value)
    
    Returns:
        Dict con resultados de detección de deriva
    """
    drift_results = {
        "drift_detected": False,
        "fields_analyzed": fields,
        "drift_details": {},
        "overall_drift_score": 0.0,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if not baseline_data:
        # Obtener baseline desde base de datos
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS data_drift_baseline (
                            id SERIAL PRIMARY KEY,
                            field_name VARCHAR(100) NOT NULL,
                            field_type VARCHAR(50),
                            mean_value NUMERIC(15, 3),
                            std_value NUMERIC(15, 3),
                            min_value NUMERIC(15, 3),
                            max_value NUMERIC(15, 3),
                            unique_values JSONB,
                            value_counts JSONB,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(field_name)
                        );
                    """)
                    
                    # Obtener baseline
                    baseline_stats = {}
                    for field in fields:
                        cur.execute("""
                            SELECT field_type, mean_value, std_value, min_value, max_value,
                                   unique_values, value_counts
                            FROM data_drift_baseline
                            WHERE field_name = %s
                            ORDER BY created_at DESC
                            LIMIT 1
                        """, (field,))
                        row = cur.fetchone()
                        if row:
                            baseline_stats[field] = {
                                "type": row[0],
                                "mean": float(row[1]) if row[1] else None,
                                "std": float(row[2]) if row[2] else None,
                                "min": float(row[3]) if row[3] else None,
                                "max": float(row[4]) if row[4] else None,
                                "unique_values": row[5],
                                "value_counts": row[6]
                            }
                    
                    baseline_data = baseline_stats
        except Exception as e:
            logger.warning(f"Error obteniendo baseline: {e}")
            baseline_data = None
    
    if not baseline_data:
        # Crear baseline desde datos actuales
        logger.info("Creando baseline desde datos actuales")
        baseline_data = {}
        for field in fields:
            values = [r.get(field) for r in current_data if r.get(field) is not None]
            if not values:
                continue
            
            if isinstance(values[0], (int, float)):
                baseline_data[field] = {
                    "type": "numeric",
                    "mean": statistics.mean(values),
                    "std": statistics.stdev(values) if len(values) > 1 else 0,
                    "min": min(values),
                    "max": max(values)
                }
            else:
                value_counts = defaultdict(int)
                for v in values:
                    value_counts[str(v)] += 1
                baseline_data[field] = {
                    "type": "categorical",
                    "value_counts": dict(value_counts),
                    "unique_count": len(value_counts)
                }
        
        # Guardar baseline
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    for field, stats in baseline_data.items():
                        cur.execute("""
                            INSERT INTO data_drift_baseline (
                                field_name, field_type, mean_value, std_value,
                                min_value, max_value, unique_values, value_counts
                            ) VALUES (
                                %s, %s, %s, %s, %s, %s, %s, %s
                            )
                            ON CONFLICT (field_name) 
                            DO UPDATE SET
                                field_type = EXCLUDED.field_type,
                                mean_value = EXCLUDED.mean_value,
                                std_value = EXCLUDED.std_value,
                                min_value = EXCLUDED.min_value,
                                max_value = EXCLUDED.max_value,
                                unique_values = EXCLUDED.unique_values,
                                value_counts = EXCLUDED.value_counts,
                                created_at = CURRENT_TIMESTAMP
                        """, (
                            field,
                            stats.get("type"),
                            stats.get("mean"),
                            stats.get("std"),
                            stats.get("min"),
                            stats.get("max"),
                            json.dumps(stats.get("unique_values", [])),
                            json.dumps(stats.get("value_counts", {}))
                        ))
                    conn.commit()
        except Exception as e:
            logger.warning(f"Error guardando baseline: {e}")
    
    # Comparar datos actuales con baseline
    drift_scores = []
    for field in fields:
        current_values = [r.get(field) for r in current_data if r.get(field) is not None]
        if not current_values or field not in baseline_data:
            continue
        
        baseline = baseline_data[field]
        drift_detail = {
            "field": field,
            "drift_detected": False,
            "drift_score": 0.0,
            "method": None,
            "p_value": None
        }
        
        if baseline.get("type") == "numeric":
            # Test estadístico para datos numéricos (KS test)
            try:
                current_mean = statistics.mean(current_values)
                current_std = statistics.stdev(current_values) if len(current_values) > 1 else 0
                
                # Calcular drift score basado en diferencia de medias y desviaciones
                mean_diff = abs(current_mean - baseline.get("mean", 0))
                std_diff = abs(current_std - baseline.get("std", 0))
                
                # Normalizar
                baseline_std = baseline.get("std", 1) or 1
                drift_score = (mean_diff / baseline_std) + (std_diff / baseline_std)
                
                drift_detail["drift_score"] = drift_score
                drift_detail["method"] = "statistical_comparison"
                drift_detail["current_mean"] = current_mean
                drift_detail["baseline_mean"] = baseline.get("mean")
                drift_detail["current_std"] = current_std
                drift_detail["baseline_std"] = baseline.get("std")
                
                if drift_score > 2.0:  # Más de 2 desviaciones estándar
                    drift_detail["drift_detected"] = True
                    drift_results["drift_detected"] = True
                
                drift_scores.append(drift_score)
            except Exception as e:
                logger.warning(f"Error analizando drift numérico para {field}: {e}")
        
        elif baseline.get("type") == "categorical":
            # Comparar distribuciones categóricas
            try:
                current_counts = defaultdict(int)
                for v in current_values:
                    current_counts[str(v)] += 1
                
                baseline_counts = baseline.get("value_counts", {})
                
                # Calcular diferencia en distribución
                all_keys = set(list(current_counts.keys()) + list(baseline_counts.keys()))
                total_current = sum(current_counts.values())
                total_baseline = sum(baseline_counts.values()) or 1
                
                drift_score = 0.0
                for key in all_keys:
                    current_pct = (current_counts.get(key, 0) / total_current) if total_current > 0 else 0
                    baseline_pct = (baseline_counts.get(key, 0) / total_baseline) if total_baseline > 0 else 0
                    drift_score += abs(current_pct - baseline_pct)
                
                drift_detail["drift_score"] = drift_score
                drift_detail["method"] = "distribution_comparison"
                drift_detail["current_distribution"] = dict(current_counts)
                drift_detail["baseline_distribution"] = baseline_counts
                
                if drift_score > threshold:
                    drift_detail["drift_detected"] = True
                    drift_results["drift_detected"] = True
                
                drift_scores.append(drift_score)
            except Exception as e:
                logger.warning(f"Error analizando drift categórico para {field}: {e}")
        
        drift_results["drift_details"][field] = drift_detail
    
    # Calcular score general de deriva
    if drift_scores:
        drift_results["overall_drift_score"] = statistics.mean(drift_scores)
    
    return drift_results


# ============================================================================
# ADVANCED ANOMALY DETECTION
# ============================================================================

def _detect_advanced_anomalies(
    records: List[Dict[str, Any]],
    numeric_fields: List[str],
    categorical_fields: List[str],
    methods: List[str] = ["isolation_forest", "statistical", "clustering"]
) -> Dict[str, Any]:
    """
    Detecta anomalías usando múltiples métodos avanzados.
    
    Args:
        records: Registros a analizar
        numeric_fields: Campos numéricos para análisis
        categorical_fields: Campos categóricos para análisis
        methods: Métodos a usar (isolation_forest, statistical, clustering)
    
    Returns:
        Dict con anomalías detectadas
    """
    anomaly_results = {
        "anomalies_detected": [],
        "anomaly_count": 0,
        "methods_used": methods,
        "scores": {},
        "timestamp": datetime.utcnow().isoformat()
    }
    
    if not records:
        return anomaly_results
    
    # Método 1: Statistical (Z-score y IQR)
    if "statistical" in methods:
        try:
            for field in numeric_fields:
                values = [r.get(field) for r in records if r.get(field) is not None and isinstance(r.get(field), (int, float))]
                if len(values) < 3:
                    continue
                
                mean = statistics.mean(values)
                std = statistics.stdev(values) if len(values) > 1 else 0
                
                if std == 0:
                    continue
                
                # Z-score
                z_scores = [(v - mean) / std for v in values]
                z_threshold = 3.0
                
                # IQR
                sorted_values = sorted(values)
                q1_idx = len(sorted_values) // 4
                q3_idx = (3 * len(sorted_values)) // 4
                q1 = sorted_values[q1_idx] if q1_idx < len(sorted_values) else sorted_values[0]
                q3 = sorted_values[q3_idx] if q3_idx < len(sorted_values) else sorted_values[-1]
                iqr = q3 - q1
                lower_bound = q1 - 1.5 * iqr
                upper_bound = q3 + 1.5 * iqr
                
                for idx, (record, value, z_score) in enumerate(zip(records, values, z_scores)):
                    is_anomaly = False
                    anomaly_reasons = []
                    
                    if abs(z_score) > z_threshold:
                        is_anomaly = True
                        anomaly_reasons.append(f"Z-score extremo: {z_score:.2f}")
                    
                    if value < lower_bound or value > upper_bound:
                        is_anomaly = True
                        anomaly_reasons.append(f"Fuera de IQR: [{lower_bound:.2f}, {upper_bound:.2f}]")
                    
                    if is_anomaly:
                        anomaly_results["anomalies_detected"].append({
                            "record_index": idx,
                            "field": field,
                            "value": value,
                            "method": "statistical",
                            "reasons": anomaly_reasons,
                            "z_score": z_score,
                            "is_outlier": True
                        })
        except Exception as e:
            logger.warning(f"Error en detección estadística de anomalías: {e}")
    
    # Método 2: Isolation Forest (simplificado)
    if "isolation_forest" in methods:
        try:
            # Implementación simplificada basada en distancia
            for field in numeric_fields:
                values = [r.get(field) for r in records if r.get(field) is not None and isinstance(r.get(field), (int, float))]
                if len(values) < 5:
                    continue
                
                mean = statistics.mean(values)
                std = statistics.stdev(values) if len(values) > 1 else 0
                
                if std == 0:
                    continue
                
                # Calcular "isolation score" basado en distancia a la media
                for idx, (record, value) in enumerate(zip(records, values)):
                    distance = abs(value - mean) / std
                    
                    # Considerar anomalía si está muy lejos
                    if distance > 2.5:
                        anomaly_results["anomalies_detected"].append({
                            "record_index": idx,
                            "field": field,
                            "value": value,
                            "method": "isolation_forest",
                            "isolation_score": distance,
                            "is_outlier": True
                        })
        except Exception as e:
            logger.warning(f"Error en isolation forest: {e}")
    
    # Método 3: Clustering (simplificado - detecta valores únicos raros)
    if "clustering" in methods:
        try:
            for field in categorical_fields:
                values = [str(r.get(field, "")) for r in records]
                value_counts = defaultdict(int)
                for v in values:
                    value_counts[v] += 1
                
                total = len(values)
                threshold = 0.01  # Menos del 1% de ocurrencias
                
                for idx, (record, value) in enumerate(zip(records, values)):
                    count = value_counts.get(value, 0)
                    frequency = count / total if total > 0 else 0
                    
                    if frequency < threshold and count < 3:
                        anomaly_results["anomalies_detected"].append({
                            "record_index": idx,
                            "field": field,
                            "value": value,
                            "method": "clustering",
                            "frequency": frequency,
                            "count": count,
                            "is_outlier": True
                        })
        except Exception as e:
            logger.warning(f"Error en clustering: {e}")
    
    # Consolidar anomalías por registro
    anomalies_by_record = defaultdict(list)
    for anomaly in anomaly_results["anomalies_detected"]:
        record_idx = anomaly["record_index"]
        anomalies_by_record[record_idx].append(anomaly)
    
    # Calcular scores
    anomaly_results["anomaly_count"] = len(anomalies_by_record)
    anomaly_results["scores"] = {
        "total_anomalies": len(anomaly_results["anomalies_detected"]),
        "unique_records_with_anomalies": len(anomalies_by_record),
        "anomaly_rate": len(anomalies_by_record) / len(records) if records else 0
    }
    
    return anomaly_results


# ============================================================================
# PERFORMANCE AUTO-TUNING
# ============================================================================

class PerformanceAutoTuner:
    """Autoajuste de parámetros de rendimiento basado en métricas históricas."""
    
    def __init__(self, conn_id: str):
        self.conn_id = conn_id
        self.recommendations = {}
    
    def analyze_performance(
        self,
        current_params: Dict[str, Any],
        execution_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Analiza métricas de ejecución y genera recomendaciones.
        
        Args:
            current_params: Parámetros actuales del DAG
            execution_metrics: Métricas de la ejecución actual
        
        Returns:
            Dict con recomendaciones de optimización
        """
        recommendations = {
            "recommendations": [],
            "current_performance": {},
            "optimization_score": 0.0,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        try:
            hook = PostgresHook(postgres_conn_id=self.conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Crear tabla de métricas de rendimiento
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS performance_metrics (
                            id SERIAL PRIMARY KEY,
                            execution_date TIMESTAMP NOT NULL,
                            dag_run_id VARCHAR(255),
                            batch_size INTEGER,
                            max_workers INTEGER,
                            chunk_size INTEGER,
                            execution_time_seconds NUMERIC(10, 2),
                            records_processed INTEGER,
                            throughput_records_per_sec NUMERIC(10, 2),
                            memory_usage_mb NUMERIC(10, 2),
                            error_rate NUMERIC(5, 2),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_perf_exec_date 
                            ON performance_metrics(execution_date DESC);
                    """)
                    
                    # Guardar métricas actuales
                    execution_time = execution_metrics.get("execution_time", 0)
                    records_processed = execution_metrics.get("records_processed", 0)
                    throughput = records_processed / execution_time if execution_time > 0 else 0
                    
                    cur.execute("""
                        INSERT INTO performance_metrics (
                            execution_date, dag_run_id, batch_size, max_workers,
                            chunk_size, execution_time_seconds, records_processed,
                            throughput_records_per_sec, error_rate
                        ) VALUES (
                            CURRENT_TIMESTAMP, %s, %s, %s, %s, %s, %s, %s, %s
                        )
                    """, (
                        execution_metrics.get("dag_run_id"),
                        current_params.get("batch_size", 1000),
                        current_params.get("max_workers", 4),
                        current_params.get("chunk_size", 500),
                        execution_time,
                        records_processed,
                        throughput,
                        execution_metrics.get("error_rate", 0)
                    ))
                    
                    # Analizar métricas históricas
                    cur.execute("""
                        SELECT 
                            AVG(execution_time_seconds) as avg_time,
                            AVG(throughput_records_per_sec) as avg_throughput,
                            AVG(error_rate) as avg_error_rate,
                            COUNT(*) as sample_size
                        FROM performance_metrics
                        WHERE execution_date >= CURRENT_TIMESTAMP - INTERVAL '7 days'
                    """)
                    row = cur.fetchone()
                    
                    if row and row[3] and row[3] > 5:  # Al menos 5 muestras
                        avg_time = float(row[0]) if row[0] else 0
                        avg_throughput = float(row[1]) if row[1] else 0
                        avg_error_rate = float(row[2]) if row[2] else 0
                        
                        recommendations["current_performance"] = {
                            "avg_execution_time": avg_time,
                            "avg_throughput": avg_throughput,
                            "avg_error_rate": avg_error_rate
                        }
                        
                        # Generar recomendaciones
                        current_batch_size = current_params.get("batch_size", 1000)
                        current_max_workers = current_params.get("max_workers", 4)
                        current_chunk_size = current_params.get("chunk_size", 500)
                        
                        # Recomendación 1: Ajustar batch_size
                        if throughput < 100 and current_batch_size < 5000:
                            recommendations["recommendations"].append({
                                "parameter": "batch_size",
                                "current_value": current_batch_size,
                                "recommended_value": min(current_batch_size * 2, 10000),
                                "reason": "Throughput bajo, aumentar batch_size puede mejorar rendimiento",
                                "expected_improvement": "10-20% más throughput"
                            })
                        elif throughput > 1000 and current_batch_size > 2000:
                            recommendations["recommendations"].append({
                                "parameter": "batch_size",
                                "current_value": current_batch_size,
                                "recommended_value": max(current_batch_size // 2, 500),
                                "reason": "Throughput alto, reducir batch_size puede mejorar latencia",
                                "expected_improvement": "Menor latencia por batch"
                            })
                        
                        # Recomendación 2: Ajustar max_workers
                        if avg_time > 300 and current_max_workers < 8:  # Más de 5 minutos
                            recommendations["recommendations"].append({
                                "parameter": "max_workers",
                                "current_value": current_max_workers,
                                "recommended_value": min(current_max_workers + 2, 16),
                                "reason": "Tiempo de ejecución alto, más workers pueden paralelizar mejor",
                                "expected_improvement": "20-30% reducción en tiempo"
                            })
                        elif avg_time < 60 and current_max_workers > 2:  # Menos de 1 minuto
                            recommendations["recommendations"].append({
                                "parameter": "max_workers",
                                "current_value": current_max_workers,
                                "recommended_value": max(current_max_workers - 1, 1),
                                "reason": "Tiempo de ejecución bajo, reducir workers puede ahorrar recursos",
                                "expected_improvement": "Menor uso de recursos"
                            })
                        
                        # Recomendación 3: Ajustar chunk_size
                        if avg_error_rate > 5 and current_chunk_size > 1000:
                            recommendations["recommendations"].append({
                                "parameter": "chunk_size",
                                "current_value": current_chunk_size,
                                "recommended_value": max(current_chunk_size // 2, 100),
                                "reason": "Tasa de errores alta, chunks más pequeños pueden mejorar estabilidad",
                                "expected_improvement": "Menor tasa de errores"
                            })
                        
                        # Calcular score de optimización
                        optimization_score = 100.0
                        if throughput < 50:
                            optimization_score -= 30
                        if avg_time > 600:
                            optimization_score -= 20
                        if avg_error_rate > 10:
                            optimization_score -= 25
                        
                        recommendations["optimization_score"] = max(0, optimization_score)
                    
                    conn.commit()
        except Exception as e:
            logger.warning(f"Error en auto-tuning de rendimiento: {e}")
        
        return recommendations


# ============================================================================
# DATA CATALOG INTEGRATION
# ============================================================================

def _register_to_data_catalog(
    conn_id: str,
    table_name: str,
    schema: Dict[str, Any],
    metadata: Dict[str, Any]
) -> bool:
    """
    Registra tabla y metadatos en catálogo de datos.
    
    Args:
        conn_id: Connection ID para PostgreSQL
        table_name: Nombre de la tabla
        schema: Esquema de la tabla
        metadata: Metadatos adicionales
    
    Returns:
        True si se registró exitosamente
    """
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_catalog (
                        id SERIAL PRIMARY KEY,
                        table_name VARCHAR(255) NOT NULL,
                        schema_name VARCHAR(100) DEFAULT 'public',
                        table_schema JSONB NOT NULL,
                        description TEXT,
                        tags JSONB,
                        owner VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(table_name, schema_name)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_catalog_table_name 
                        ON data_catalog(table_name);
                    CREATE INDEX IF NOT EXISTS idx_catalog_tags 
                        ON data_catalog USING GIN(tags);
                """)
                
                cur.execute("""
                    INSERT INTO data_catalog (
                        table_name, schema_name, table_schema, description, tags, owner
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (table_name, schema_name)
                    DO UPDATE SET
                        table_schema = EXCLUDED.table_schema,
                        description = EXCLUDED.description,
                        tags = EXCLUDED.tags,
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    table_name,
                    metadata.get("schema_name", "public"),
                    json.dumps(schema),
                    metadata.get("description", ""),
                    json.dumps(metadata.get("tags", [])),
                    metadata.get("owner", "data_integration_etl")
                ))
                
                conn.commit()
                logger.info(f"Tabla {table_name} registrada en catálogo de datos")
                return True
    except Exception as e:
        logger.warning(f"Error registrando en catálogo: {e}")
        return False


# ============================================================================
# DATA CONTRACTS
# ============================================================================

@dataclass
class DataContract:
    """Contrato de datos que define expectativas sobre los datos."""
    
    name: str
    table_name: str
    rules: List[Dict[str, Any]]
    severity: str = "error"  # error, warning
    enabled: bool = True


class DataContractValidator:
    """Validador de contratos de datos."""
    
    def __init__(self, contracts: List[DataContract]):
        self.contracts = {c.table_name: c for c in contracts if c.enabled}
    
    def validate(
        self,
        table_name: str,
        records: List[Dict[str, Any]],
        conn_id: str
    ) -> Dict[str, Any]:
        """
        Valida registros contra contratos de datos.
        
        Args:
            table_name: Nombre de la tabla
            records: Registros a validar
            conn_id: Connection ID para PostgreSQL
        
        Returns:
            Dict con resultados de validación
        """
        if table_name not in self.contracts:
            return {"valid": True, "contract_applied": False}
        
        contract = self.contracts[table_name]
        violations = []
        
        for rule in contract.rules:
            rule_type = rule.get("type")
            field = rule.get("field")
            condition = rule.get("condition")
            
            if rule_type == "not_null":
                null_count = sum(1 for r in records if r.get(field) is None)
                if null_count > 0:
                    violations.append({
                        "rule": rule.get("name", "not_null"),
                        "type": "not_null",
                        "field": field,
                        "violations": null_count,
                        "message": f"Campo {field} tiene {null_count} valores nulos"
                    })
            
            elif rule_type == "unique":
                values = [r.get(field) for r in records if r.get(field) is not None]
                unique_values = set(values)
                if len(values) != len(unique_values):
                    duplicates = len(values) - len(unique_values)
                    violations.append({
                        "rule": rule.get("name", "unique"),
                        "type": "unique",
                        "field": field,
                        "violations": duplicates,
                        "message": f"Campo {field} tiene {duplicates} duplicados"
                    })
            
            elif rule_type == "range":
                min_val = rule.get("min")
                max_val = rule.get("max")
                out_of_range = sum(
                    1 for r in records
                    if r.get(field) is not None and (
                        (min_val is not None and r.get(field) < min_val) or
                        (max_val is not None and r.get(field) > max_val)
                    )
                )
                if out_of_range > 0:
                    violations.append({
                        "rule": rule.get("name", "range"),
                        "type": "range",
                        "field": field,
                        "violations": out_of_range,
                        "message": f"Campo {field} tiene {out_of_range} valores fuera de rango [{min_val}, {max_val}]"
                    })
            
            elif rule_type == "custom":
                # Regla personalizada con función lambda o expresión
                condition_func = condition
                if callable(condition_func):
                    violations_count = sum(1 for r in records if not condition_func(r))
                    if violations_count > 0:
                        violations.append({
                            "rule": rule.get("name", "custom"),
                            "type": "custom",
                            "field": field,
                            "violations": violations_count,
                            "message": rule.get("message", f"Regla personalizada violada {violations_count} veces")
                        })
        
        is_valid = len(violations) == 0
        
        # Guardar violaciones si hay
        if violations and contract.severity == "error":
            try:
                hook = PostgresHook(postgres_conn_id=conn_id)
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS data_contract_violations (
                                id SERIAL PRIMARY KEY,
                                contract_name VARCHAR(255) NOT NULL,
                                table_name VARCHAR(255) NOT NULL,
                                rule_name VARCHAR(255),
                                rule_type VARCHAR(100),
                                field_name VARCHAR(255),
                                violations_count INTEGER,
                                message TEXT,
                                violation_data JSONB,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );
                            
                            CREATE INDEX IF NOT EXISTS idx_contract_violations_contract 
                                ON data_contract_violations(contract_name, created_at DESC);
                        """)
                        
                        for violation in violations:
                            cur.execute("""
                                INSERT INTO data_contract_violations (
                                    contract_name, table_name, rule_name, rule_type,
                                    field_name, violations_count, message
                                ) VALUES (
                                    %s, %s, %s, %s, %s, %s, %s
                                )
                            """, (
                                contract.name,
                                table_name,
                                violation.get("rule"),
                                violation.get("type"),
                                violation.get("field"),
                                violation.get("violations"),
                                violation.get("message")
                            ))
                        
                        conn.commit()
            except Exception as e:
                logger.warning(f"Error guardando violaciones de contrato: {e}")
        
        return {
            "valid": is_valid,
            "contract_applied": True,
            "contract_name": contract.name,
            "violations": violations,
            "violations_count": len(violations),
            "severity": contract.severity
        }


# ============================================================================
# AUTOMATED TESTING
# ============================================================================

class DataPipelineTester:
    """Suite de pruebas automatizadas para el pipeline."""
    
    def __init__(self, conn_id: str):
        self.conn_id = conn_id
        self.test_results = []
    
    def run_tests(
        self,
        extracted_data: Dict[str, Any],
        transformed_data: Dict[str, Any],
        validated_data: Dict[str, Any],
        loaded_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Ejecuta suite completa de pruebas.
        
        Args:
            extracted_data: Datos extraídos
            transformed_data: Datos transformados
            validated_data: Datos validados
            loaded_data: Datos cargados
        
        Returns:
            Dict con resultados de todas las pruebas
        """
        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "tests": [],
            "overall_status": "unknown"
        }
        
        # Test 1: Completitud de extracción
        test_results["total_tests"] += 1
        extraction_test = self._test_extraction_completeness(extracted_data)
        test_results["tests"].append(extraction_test)
        if extraction_test["status"] == "passed":
            test_results["passed"] += 1
        elif extraction_test["status"] == "failed":
            test_results["failed"] += 1
        else:
            test_results["warnings"] += 1
        
        # Test 2: Integridad de transformación
        test_results["total_tests"] += 1
        transformation_test = self._test_transformation_integrity(transformed_data)
        test_results["tests"].append(transformation_test)
        if transformation_test["status"] == "passed":
            test_results["passed"] += 1
        elif transformation_test["status"] == "failed":
            test_results["failed"] += 1
        else:
            test_results["warnings"] += 1
        
        # Test 3: Calidad de validación
        test_results["total_tests"] += 1
        validation_test = self._test_validation_quality(validated_data)
        test_results["tests"].append(validation_test)
        if validation_test["status"] == "passed":
            test_results["passed"] += 1
        elif validation_test["status"] == "failed":
            test_results["failed"] += 1
        else:
            test_results["warnings"] += 1
        
        # Test 4: Consistencia de carga
        test_results["total_tests"] += 1
        load_test = self._test_load_consistency(loaded_data)
        test_results["tests"].append(load_test)
        if load_test["status"] == "passed":
            test_results["passed"] += 1
        elif load_test["status"] == "failed":
            test_results["failed"] += 1
        else:
            test_results["warnings"] += 1
        
        # Test 5: End-to-end data flow
        test_results["total_tests"] += 1
        e2e_test = self._test_end_to_end_flow(extracted_data, loaded_data)
        test_results["tests"].append(e2e_test)
        if e2e_test["status"] == "passed":
            test_results["passed"] += 1
        elif e2e_test["status"] == "failed":
            test_results["failed"] += 1
        else:
            test_results["warnings"] += 1
        
        # Determinar estado general
        if test_results["failed"] == 0:
            test_results["overall_status"] = "passed"
        elif test_results["failed"] > 0 and test_results["passed"] > 0:
            test_results["overall_status"] = "partial"
        else:
            test_results["overall_status"] = "failed"
        
        # Guardar resultados
        try:
            hook = PostgresHook(postgres_conn_id=self.conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS pipeline_test_results (
                            id SERIAL PRIMARY KEY,
                            test_run_id VARCHAR(255) NOT NULL,
                            test_name VARCHAR(255) NOT NULL,
                            status VARCHAR(50) NOT NULL,
                            message TEXT,
                            details JSONB,
                            execution_time_seconds NUMERIC(10, 2),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                        
                        CREATE INDEX IF NOT EXISTS idx_test_results_run 
                            ON pipeline_test_results(test_run_id, created_at DESC);
                    """)
                    
                    import uuid
                    test_run_id = str(uuid.uuid4())
                    
                    for test in test_results["tests"]:
                        cur.execute("""
                            INSERT INTO pipeline_test_results (
                                test_run_id, test_name, status, message, details
                            ) VALUES (
                                %s, %s, %s, %s, %s
                            )
                        """, (
                            test_run_id,
                            test["name"],
                            test["status"],
                            test.get("message", ""),
                            json.dumps(test.get("details", {}))
                        ))
                    
                    conn.commit()
        except Exception as e:
            logger.warning(f"Error guardando resultados de pruebas: {e}")
        
        return test_results
    
    def _test_extraction_completeness(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba de completitud de extracción."""
        total_sources = 3
        sources_with_data = sum(
            1 for source in ["crm", "sheets", "billing"]
            if extracted_data.get(source, {}).get("count", 0) > 0
        )
        
        completeness_rate = sources_with_data / total_sources
        
        return {
            "name": "extraction_completeness",
            "status": "passed" if completeness_rate >= 0.67 else "warning",
            "message": f"{sources_with_data}/{total_sources} fuentes con datos",
            "details": {
                "sources_with_data": sources_with_data,
                "total_sources": total_sources,
                "completeness_rate": completeness_rate
            }
        }
    
    def _test_transformation_integrity(self, transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba de integridad de transformación."""
        records = transformed_data.get("records", [])
        required_fields = ["source_id", "source_type"]
        
        missing_fields = []
        for record in records:
            for field in required_fields:
                if field not in record:
                    missing_fields.append(field)
                    break
        
        return {
            "name": "transformation_integrity",
            "status": "passed" if not missing_fields else "failed",
            "message": f"Campos requeridos presentes" if not missing_fields else f"Faltan campos: {set(missing_fields)}",
            "details": {
                "total_records": len(records),
                "missing_fields": list(set(missing_fields)) if missing_fields else []
            }
        }
    
    def _test_validation_quality(self, validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba de calidad de validación."""
        validation = validated_data.get("validation", {})
        results = validation.get("results", {})
        
        total = results.get("total", 0)
        valid = results.get("valid", 0)
        invalid = results.get("invalid", 0)
        
        if total == 0:
            return {
                "name": "validation_quality",
                "status": "warning",
                "message": "No hay datos para validar",
                "details": {"total": 0}
            }
        
        validation_rate = valid / total if total > 0 else 0
        
        return {
            "name": "validation_quality",
            "status": "passed" if validation_rate >= 0.95 else "warning",
            "message": f"Tasa de validación: {validation_rate:.2%}",
            "details": {
                "total": total,
                "valid": valid,
                "invalid": invalid,
                "validation_rate": validation_rate
            }
        }
    
    def _test_load_consistency(self, loaded_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba de consistencia de carga."""
        load_info = loaded_data.get("load", {})
        loaded_count = load_info.get("loaded_count", 0)
        error_count = load_info.get("error_count", 0)
        total = loaded_count + error_count
        
        if total == 0:
            return {
                "name": "load_consistency",
                "status": "warning",
                "message": "No hay datos para cargar",
                "details": {"total": 0}
            }
        
        success_rate = loaded_count / total if total > 0 else 0
        
        return {
            "name": "load_consistency",
            "status": "passed" if success_rate >= 0.99 else "failed",
            "message": f"Tasa de éxito de carga: {success_rate:.2%}",
            "details": {
                "loaded": loaded_count,
                "errors": error_count,
                "total": total,
                "success_rate": success_rate
            }
        }
    
    def _test_end_to_end_flow(self, extracted_data: Dict[str, Any], loaded_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prueba end-to-end del flujo de datos."""
        # Contar registros extraídos
        extracted_count = sum(
            extracted_data.get(source, {}).get("count", 0)
            for source in ["crm", "sheets", "billing"]
        )
        
        # Contar registros cargados
        loaded_count = loaded_data.get("load", {}).get("loaded_count", 0)
        
        # Calcular tasa de retención
        retention_rate = loaded_count / extracted_count if extracted_count > 0 else 0
        
        return {
            "name": "end_to_end_flow",
            "status": "passed" if retention_rate >= 0.90 else "warning",
            "message": f"Tasa de retención end-to-end: {retention_rate:.2%}",
            "details": {
                "extracted": extracted_count,
                "loaded": loaded_count,
                "retention_rate": retention_rate
            }
        }


# ============================================================================
# SMART RETRY STRATEGIES
# ============================================================================

class SmartRetryStrategy:
    """Estrategia de retry inteligente basada en tipo de error."""
    
    @staticmethod
    def should_retry(exception: Exception, attempt: int, max_retries: int = 3) -> bool:
        """Determina si se debe reintentar basándose en el tipo de error."""
        if attempt >= max_retries:
            return False
        
        error_str = str(exception).lower()
        
        # Errores temporales que deberían retry
        transient_errors = [
            "timeout", "connection", "network", "temporary", "rate limit",
            "throttle", "503", "502", "504", "429", "busy", "locked"
        ]
        
        if any(err in error_str for err in transient_errors):
            return True
        
        # Errores permanentes que NO deberían retry
        permanent_errors = [
            "not found", "404", "invalid", "authentication", "authorization",
            "403", "401", "syntax error", "malformed"
        ]
        
        if any(err in error_str for err in permanent_errors):
            return False
        
        # Por defecto, retry para otros errores
        return True
    
    @staticmethod
    def calculate_delay(attempt: int, base_delay: float = 1.0, max_delay: float = 60.0) -> float:
        """Calcula delay para retry con exponential backoff."""
        delay = min(base_delay * (2 ** attempt), max_delay)
        return delay


# ============================================================================
# DATA ARCHIVING
# ============================================================================

def _archive_old_data(
    conn_id: str,
    table_name: str,
    archive_table_name: str,
    archive_older_than_days: int = 90
) -> Dict[str, Any]:
    """Archiva datos antiguos a una tabla de archivo."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Crear tabla de archivo si no existe
                cur.execute(f"""
                    CREATE TABLE IF NOT EXISTS {archive_table_name} (
                        LIKE {table_name} INCLUDING ALL
                    );
                """)
                
                # Mover datos antiguos
                cur.execute(f"""
                    INSERT INTO {archive_table_name}
                    SELECT * FROM {table_name}
                    WHERE created_at < CURRENT_DATE - INTERVAL '%s days'
                """, (archive_older_than_days,))
                
                archived_count = cur.rowcount
                
                # Eliminar datos archivados de tabla original
                if archived_count > 0:
                    cur.execute(f"""
                        DELETE FROM {table_name}
                        WHERE created_at < CURRENT_DATE - INTERVAL '%s days'
                    """, (archive_older_than_days,))
                
                conn.commit()
                
                return {
                    "archived_count": archived_count,
                    "archive_table": archive_table_name,
                    "success": True
                }
    except Exception as e:
        logger.error(f"Error archivando datos: {e}", exc_info=True)
        return {
            "archived_count": 0,
            "archive_table": archive_table_name,
            "success": False,
            "error": str(e)
        }


# ============================================================================
# DATA VERSIONING
# ============================================================================

def _create_data_version(
    conn_id: str,
    version_name: str,
    description: str,
    records_count: int,
    metadata: Dict[str, Any]
) -> str:
    """Crea una versión de los datos."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_versions (
                        id SERIAL PRIMARY KEY,
                        version_name VARCHAR(255) UNIQUE NOT NULL,
                        description TEXT,
                        records_count INTEGER,
                        metadata JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        created_by VARCHAR(255) DEFAULT 'system'
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_versions_name 
                        ON data_integration_versions(version_name);
                    CREATE INDEX IF NOT EXISTS idx_versions_created_at 
                        ON data_integration_versions(created_at DESC);
                """)
                
                cur.execute("""
                    INSERT INTO data_integration_versions (
                        version_name, description, records_count, metadata
                    ) VALUES (
                        %s, %s, %s, %s
                    )
                    ON CONFLICT (version_name) DO UPDATE SET
                        description = EXCLUDED.description,
                        records_count = EXCLUDED.records_count,
                        metadata = EXCLUDED.metadata,
                        created_at = CURRENT_TIMESTAMP
                """, (
                    version_name,
                    description,
                    records_count,
                    json.dumps(metadata)
                ))
                
                conn.commit()
                return version_name
    except Exception as e:
        logger.error(f"Error creando versión de datos: {e}", exc_info=True)
        return ""


def _get_latest_version(conn_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene la última versión de datos."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT version_name, description, records_count, metadata, created_at
                    FROM data_integration_versions
                    ORDER BY created_at DESC
                    LIMIT 1
                """)
                
                result = cur.fetchone()
                if result:
                    return {
                        "version_name": result[0],
                        "description": result[1],
                        "records_count": result[2],
                        "metadata": json.loads(result[3]) if result[3] else {},
                        "created_at": result[4].isoformat() if result[4] else None
                    }
    except Exception as e:
        logger.error(f"Error obteniendo última versión: {e}", exc_info=True)
    
    return None


# ============================================================================
# AUDIT LOGGING
# ============================================================================

def _create_audit_log(
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    user: Optional[str] = None
) -> Dict[str, Any]:
    """Crea un registro de auditoría."""
    return {
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details or {},
        "user": user or "system",
        "timestamp": datetime.utcnow().isoformat(),
        "dag_run_id": None,  # Se completará en el contexto
    }


def _save_audit_log(conn_id: str, audit_log: Dict[str, Any]) -> None:
    """Guarda un registro de auditoría en la base de datos."""
    try:
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS data_integration_audit_log (
                        id SERIAL PRIMARY KEY,
                        action VARCHAR(100) NOT NULL,
                        entity_type VARCHAR(100) NOT NULL,
                        entity_id VARCHAR(255),
                        details JSONB,
                        user_name VARCHAR(255),
                        timestamp TIMESTAMP NOT NULL,
                        dag_run_id VARCHAR(255),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_audit_action 
                        ON data_integration_audit_log(action);
                    CREATE INDEX IF NOT EXISTS idx_audit_entity 
                        ON data_integration_audit_log(entity_type, entity_id);
                    CREATE INDEX IF NOT EXISTS idx_audit_timestamp 
                        ON data_integration_audit_log(timestamp DESC);
                """)
                
                cur.execute("""
                    INSERT INTO data_integration_audit_log (
                        action, entity_type, entity_id, details, user_name, timestamp, dag_run_id
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    audit_log["action"],
                    audit_log["entity_type"],
                    audit_log["entity_id"],
                    json.dumps(audit_log["details"]),
                    audit_log["user"],
                    audit_log["timestamp"],
                    audit_log["dag_run_id"]
                ))
                
                conn.commit()
    except Exception as e:
        logger.error(f"Error guardando audit log: {e}", exc_info=True)


# ============================================================================
# REPORT GENERATION
# ============================================================================

def _generate_executive_report(
    extracted_data: Dict[str, Any],
    transformed_data: Dict[str, Any],
    validated_data: Dict[str, Any],
    loaded_data: Dict[str, Any],
    quality_analysis: Dict[str, Any],
    inconsistencies: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Genera reporte ejecutivo del proceso."""
    
    report = {
        "execution_summary": {
            "timestamp": datetime.utcnow().isoformat(),
            "status": "success",
            "duration_seconds": None,  # Se calculará si hay timestamps
        },
        "extraction": {
            "crm": extracted_data.get("crm", {}).get("count", 0),
            "sheets": extracted_data.get("sheets", {}).get("count", 0),
            "billing": extracted_data.get("billing", {}).get("count", 0),
            "total": 0
        },
        "transformation": {
            "total_input": sum(
                stats.get("input", 0) 
                for stats in transformed_data.get("stats", {}).values()
            ),
            "total_output": sum(
                stats.get("output", 0) 
                for stats in transformed_data.get("stats", {}).values()
            ),
            "total_errors": sum(
                stats.get("errors", 0) 
                for stats in transformed_data.get("stats", {}).values()
            ),
            "success_rate": 0.0
        },
        "validation": {
            "total": validated_data.get("validation", {}).get("results", {}).get("total", 0),
            "valid": validated_data.get("validation", {}).get("results", {}).get("valid", 0),
            "invalid": validated_data.get("validation", {}).get("results", {}).get("invalid", 0),
            "validation_rate": 0.0
        },
        "load": {
            "loaded": loaded_data.get("load", {}).get("loaded_count", 0),
            "errors": loaded_data.get("load", {}).get("error_count", 0),
            "success_rate": 0.0
        },
        "quality_analysis": {
            "total_records": quality_analysis.get("quality_analysis", {}).get("total_records", 0),
            "completeness": {},
            "anomalies_count": len(quality_analysis.get("quality_analysis", {}).get("anomalies", []))
        },
        "inconsistencies": {
            "total": len(inconsistencies),
            "by_severity": defaultdict(int),
            "top_issues": []
        },
        "recommendations": []
    }
    
    # Calcular totales
    report["extraction"]["total"] = (
        report["extraction"]["crm"] +
        report["extraction"]["sheets"] +
        report["extraction"]["billing"]
    )
    
    # Calcular tasas de éxito
    if report["transformation"]["total_input"] > 0:
        report["transformation"]["success_rate"] = (
            report["transformation"]["total_output"] / 
            report["transformation"]["total_input"] * 100
        )
    
    if report["validation"]["total"] > 0:
        report["validation"]["validation_rate"] = (
            report["validation"]["valid"] / 
            report["validation"]["total"] * 100
        )
    
    if report["load"]["loaded"] + report["load"]["errors"] > 0:
        report["load"]["success_rate"] = (
            report["load"]["loaded"] / 
            (report["load"]["loaded"] + report["load"]["errors"]) * 100
        )
    
    # Completitud por campo
    completeness = quality_analysis.get("quality_analysis", {}).get("completeness", {})
    for field, metrics in completeness.items():
        report["quality_analysis"]["completeness"][field] = metrics.get("completeness_pct", 0)
    
    # Inconsistencias por severidad
    for inc in inconsistencies:
        severity = inc.get("severity", "unknown")
        report["inconsistencies"]["by_severity"][severity] += 1
    
    # Top issues
    report["inconsistencies"]["top_issues"] = sorted(
        inconsistencies,
        key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x.get("severity", "low"), 0),
        reverse=True
    )[:5]
    
    # Recomendaciones
    if report["transformation"]["total_errors"] > 0:
        report["recommendations"].append({
            "type": "transformation_errors",
            "message": f"Revisar {report['transformation']['total_errors']} errores de transformación",
            "priority": "high"
        })
    
    if report["validation"]["invalid"] > 0:
        report["recommendations"].append({
            "type": "validation_errors",
            "message": f"{report['validation']['invalid']} registros inválidos requieren atención",
            "priority": "medium"
        })
    
    if report["inconsistencies"]["total"] > 0:
        high_severity = report["inconsistencies"]["by_severity"].get("high", 0)
        if high_severity > 0:
            report["recommendations"].append({
                "type": "inconsistencies",
                "message": f"{high_severity} inconsistencias de alta severidad detectadas",
                "priority": "high"
            })
    
    return report


@dag(
    dag_id="data_integration_etl",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 2 * * *",  # Diario a las 2 AM UTC
    catchup=False,
    default_args={
        "owner": "data-engineering",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Integración de Datos ETL
    
    DAG que automatiza la integración de datos entre sistemas:
    
    **Fuentes de Datos:**
    - CRM (Salesforce/Pipedrive): Contactos, leads, oportunidades
    - Google Sheets: Datos manuales, reportes, configuraciones
    - Sistema de Facturación: Facturas, pagos, transacciones
    
    **Proceso:**
    1. Extracción de datos de todas las fuentes
    2. Transformación y normalización
    3. Validación de calidad de datos
    4. Carga en data warehouse
    5. Detección de inconsistencias
    6. Alertas automáticas si hay problemas
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para PostgreSQL
    - `crm_type`: Tipo de CRM ('salesforce' o 'pipedrive')
    - `crm_config`: Configuración del CRM (JSON string)
    - `sheets_spreadsheet_id`: ID de Google Spreadsheet
    - `sheets_credentials_json`: Credenciales de Google Service Account (JSON string)
    - `billing_source`: Fuente de facturación ('database' o 'api')
    - `enable_validation`: Habilitar validación de datos (default: true)
    - `enable_alerts`: Habilitar alertas (default: true)
    - `dry_run`: Modo dry-run sin escribir cambios (default: false)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "crm_type": Param("salesforce", type="string", enum=["salesforce", "pipedrive"]),
        "crm_config": Param("{}", type="string"),
        "sheets_spreadsheet_id": Param("", type="string"),
        "sheets_credentials_json": Param("{}", type="string"),
        "sheets_range": Param("Sheet1!A:Z", type="string"),
        "billing_source": Param("database", type="string", enum=["database", "api"]),
        "enable_validation": Param(True, type="boolean"),
        "enable_alerts": Param(True, type="boolean"),
        "enable_dlq": Param(True, type="boolean"),
        "enable_circuit_breaker": Param(True, type="boolean"),
        "enable_rate_limiting": Param(False, type="boolean"),
        "enable_cache": Param(True, type="boolean"),
        "enable_checkpointing": Param(True, type="boolean"),
        "enable_data_profiling": Param(True, type="boolean"),
        "enable_parallel_processing": Param(True, type="boolean"),
        "enable_incremental": Param(False, type="boolean"),
        "enable_reports": Param(True, type="boolean"),
        "enable_schema_validation": Param(True, type="boolean"),
        "enable_currency_conversion": Param(False, type="boolean"),
        "target_currency": Param("USD", type="string"),
        "enable_outlier_detection": Param(True, type="boolean"),
        "enable_temporal_analysis": Param(True, type="boolean"),
        "enable_audit_logging": Param(True, type="boolean"),
        "enable_data_lineage": Param(True, type="boolean"),
        "enable_deduplication": Param(True, type="boolean"),
        "deduplication_fields": Param("email,customer_id", type="string"),
        "deduplication_strategy": Param("latest", type="string", enum=["latest", "first", "most_complete"]),
        "enable_data_enrichment": Param(True, type="boolean"),
        "enable_data_versioning": Param(False, type="boolean"),
        "enable_table_partitioning": Param(False, type="boolean"),
        "enable_backup": Param(True, type="boolean"),
        "enable_auto_rollback": Param(False, type="boolean"),
        "enable_data_archiving": Param(False, type="boolean"),
        "archive_older_than_days": Param(90, type="integer", minimum=30, maximum=365),
        "enable_data_reconciliation": Param(True, type="boolean"),
        "reconciliation_threshold": Param(0.85, type="number", minimum=0.5, maximum=1.0),
        "enable_pii_detection": Param(True, type="boolean"),
        "enable_pii_masking": Param(False, type="boolean"),
        "enable_cost_tracking": Param(True, type="boolean"),
        "enable_smart_retry": Param(True, type="boolean"),
        "enable_quality_scoring": Param(True, type="boolean"),
        "enable_quality_rules": Param(True, type="boolean"),
        "quality_threshold": Param(60.0, type="number", minimum=0, maximum=100),
        "enable_intelligent_alerting": Param(True, type="boolean"),
        "enable_realtime_monitoring": Param(True, type="boolean"),
        "enable_data_drift_detection": Param(True, type="boolean"),
        "enable_advanced_anomaly_detection": Param(True, type="boolean"),
        "enable_performance_autotuning": Param(True, type="boolean"),
        "drift_detection_threshold": Param(0.05, type="number", minimum=0.01, maximum=0.5),
        "enable_data_catalog": Param(True, type="boolean"),
        "enable_data_contracts": Param(True, type="boolean"),
        "enable_automated_testing": Param(True, type="boolean"),
        "dry_run": Param(False, type="boolean"),
        "batch_size": Param(1000, type="integer", minimum=1, maximum=10000),
        "circuit_breaker_threshold": Param(5, type="integer", minimum=1, maximum=20),
        "circuit_breaker_reset_minutes": Param(15, type="integer", minimum=5, maximum=60),
        "cache_ttl_seconds": Param(3600, type="integer", minimum=60, maximum=86400),
        "max_workers": Param(4, type="integer", minimum=1, maximum=16),
        "chunk_size": Param(500, type="integer", minimum=10, maximum=5000),
    },
    tags=["etl", "integration", "data-warehouse", "crm", "billing"],
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=2),
    on_success_callback=lambda context: (
        CircuitBreaker.reset(context.get("dag").dag_id if context.get("dag") else "data_integration_etl"),
        notify_slack(":white_check_mark: data_integration_etl DAG succeeded") if NOTIFICATIONS_AVAILABLE else None
    ),
    on_failure_callback=lambda context: (
        CircuitBreaker.record_failure(context.get("dag").dag_id if context.get("dag") else "data_integration_etl"),
        notify_slack(":x: data_integration_etl DAG failed") if NOTIFICATIONS_AVAILABLE else None
    ),
)
def data_integration_etl() -> None:
    """
    DAG principal de integración de datos ETL.
    """
    
    @task(task_id="health_check", execution_timeout=timedelta(minutes=2))
    def health_check() -> Dict[str, Any]:
        """Health check pre-vuelo de sistemas y dependencias."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_circuit_breaker = bool(params.get("enable_circuit_breaker", True))
        
        checks = {
            "status": "ok",
            "checks": {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check circuit breaker
        if enable_circuit_breaker:
            dag_id = ctx.get("dag").dag_id if ctx.get("dag") else "data_integration_etl"
            threshold = int(params.get("circuit_breaker_threshold", 5))
            reset_minutes = int(params.get("circuit_breaker_reset_minutes", 15))
            
            cb_open = CircuitBreaker.is_open(dag_id, threshold=threshold, reset_minutes=reset_minutes)
            checks["checks"]["circuit_breaker"] = {
                "status": "warning" if cb_open else "ok",
                "open": cb_open,
            }
            if cb_open:
                checks["status"] = "degraded"
                logger.warning("Circuit breaker is open - DAG may have recent failures")
        
        # Check PostgreSQL connection
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
            checks["checks"]["postgres"] = {"status": "ok"}
        except Exception as e:
            checks["status"] = "error"
            checks["checks"]["postgres"] = {
                "status": "error",
                "message": str(e)[:200]
            }
        
        # Check CRM config (si está configurado)
        crm_config_str = str(params.get("crm_config", "{}"))
        if crm_config_str and crm_config_str != "{}":
            try:
                crm_config = json.loads(crm_config_str)
                crm_type = str(params.get("crm_type", "salesforce"))
                
                if crm_type == "salesforce":
                    required = ["username", "password", "security_token"]
                else:
                    required = ["api_token", "company_domain"]
                
                missing = [f for f in required if not crm_config.get(f)]
                if missing:
                    checks["checks"]["crm_config"] = {
                        "status": "error",
                        "message": f"Missing required fields: {', '.join(missing)}"
                    }
                    checks["status"] = "error"
                else:
                    checks["checks"]["crm_config"] = {"status": "ok"}
            except Exception as e:
                checks["checks"]["crm_config"] = {
                    "status": "warning",
                    "message": f"Error parsing config: {str(e)[:200]}"
                }
        
        # Check Google Sheets config (si está configurado)
        sheets_id = str(params.get("sheets_spreadsheet_id", ""))
        if sheets_id:
            checks["checks"]["sheets_config"] = {"status": "ok"}
        else:
            checks["checks"]["sheets_config"] = {
                "status": "warning",
                "message": "Google Sheets not configured"
            }
        
        logger.info(f"Health check completed: {checks['status']}")
        
        if STATS_AVAILABLE:
            try:
                Stats.gauge("data_integration_etl.health_check.status", 
                           1 if checks["status"] == "ok" else 0)
            except Exception:
                pass
        
        if checks["status"] == "error":
            raise Exception(f"Health check failed: {checks['checks']}")
        
        return checks
    
    @task(task_id="prepare_extraction")
    def prepare_extraction() -> Dict[str, Any]:
        """Prepara contexto y configuración para la extracción."""
        ctx = get_current_context()
        params = ctx["params"]
        data_interval_end = ctx.get("data_interval_end")
        
        # Calcular fechas para el período de extracción
        if data_interval_end:
            end_date = data_interval_end.to_date_string()
            start_date = (data_interval_end - timedelta(days=1)).to_date_string()
        else:
            end_date = datetime.utcnow().date().isoformat()
            start_date = (datetime.utcnow().date() - timedelta(days=1)).isoformat()
        
        config = {
            "start_date": start_date,
            "end_date": end_date,
            "crm_type": str(params["crm_type"]),
            "crm_config": json.loads(str(params["crm_config"])),
            "sheets_spreadsheet_id": str(params["sheets_spreadsheet_id"]),
            "sheets_credentials_json": json.loads(str(params["sheets_credentials_json"])),
            "sheets_range": str(params["sheets_range"]),
            "billing_source": str(params["billing_source"]),
            "postgres_conn_id": str(params["postgres_conn_id"]),
            "batch_size": int(params["batch_size"]),
            "dry_run": bool(params["dry_run"]),
            "enable_validation": bool(params["enable_validation"]),
            "enable_alerts": bool(params["enable_alerts"]),
            "enable_dlq": bool(params.get("enable_dlq", True)),
            "enable_rate_limiting": bool(params.get("enable_rate_limiting", False)),
            "enable_cache": bool(params.get("enable_cache", True)),
            "enable_checkpointing": bool(params.get("enable_checkpointing", True)),
            "enable_data_profiling": bool(params.get("enable_data_profiling", True)),
            "enable_parallel_processing": bool(params.get("enable_parallel_processing", True)),
            "enable_incremental": bool(params.get("enable_incremental", False)),
            "enable_reports": bool(params.get("enable_reports", True)),
            "enable_schema_validation": bool(params.get("enable_schema_validation", True)),
            "enable_currency_conversion": bool(params.get("enable_currency_conversion", False)),
            "target_currency": str(params.get("target_currency", "USD")),
            "enable_outlier_detection": bool(params.get("enable_outlier_detection", True)),
            "enable_temporal_analysis": bool(params.get("enable_temporal_analysis", True)),
            "enable_audit_logging": bool(params.get("enable_audit_logging", True)),
            "enable_data_lineage": bool(params.get("enable_data_lineage", True)),
            "enable_deduplication": bool(params.get("enable_deduplication", True)),
            "deduplication_fields": str(params.get("deduplication_fields", "email,customer_id")).split(","),
            "deduplication_strategy": str(params.get("deduplication_strategy", "latest")),
            "enable_data_enrichment": bool(params.get("enable_data_enrichment", True)),
            "enable_data_versioning": bool(params.get("enable_data_versioning", False)),
            "enable_table_partitioning": bool(params.get("enable_table_partitioning", False)),
            "enable_backup": bool(params.get("enable_backup", True)),
            "enable_auto_rollback": bool(params.get("enable_auto_rollback", False)),
            "enable_data_archiving": bool(params.get("enable_data_archiving", False)),
            "archive_older_than_days": int(params.get("archive_older_than_days", 90)),
            "enable_data_reconciliation": bool(params.get("enable_data_reconciliation", True)),
            "reconciliation_threshold": float(params.get("reconciliation_threshold", 0.85)),
            "enable_pii_detection": bool(params.get("enable_pii_detection", True)),
            "enable_pii_masking": bool(params.get("enable_pii_masking", False)),
            "enable_cost_tracking": bool(params.get("enable_cost_tracking", True)),
            "enable_smart_retry": bool(params.get("enable_smart_retry", True)),
            "enable_quality_scoring": bool(params.get("enable_quality_scoring", True)),
            "enable_quality_rules": bool(params.get("enable_quality_rules", True)),
            "quality_threshold": float(params.get("quality_threshold", 60.0)),
            "enable_intelligent_alerting": bool(params.get("enable_intelligent_alerting", True)),
            "enable_realtime_monitoring": bool(params.get("enable_realtime_monitoring", True)),
            "enable_data_drift_detection": bool(params.get("enable_data_drift_detection", True)),
            "enable_advanced_anomaly_detection": bool(params.get("enable_advanced_anomaly_detection", True)),
            "enable_performance_autotuning": bool(params.get("enable_performance_autotuning", True)),
            "drift_detection_threshold": float(params.get("drift_detection_threshold", 0.05)),
            "enable_data_catalog": bool(params.get("enable_data_catalog", True)),
            "enable_data_contracts": bool(params.get("enable_data_contracts", True)),
            "enable_automated_testing": bool(params.get("enable_automated_testing", True)),
            "cache_ttl_seconds": int(params.get("cache_ttl_seconds", 3600)),
            "max_workers": int(params.get("max_workers", 4)),
            "chunk_size": int(params.get("chunk_size", 500)),
        }
        
        # Si es incremental, obtener último timestamp
        if config["enable_incremental"]:
            conn_id = config["postgres_conn_id"]
            for source in ["crm", "sheets", "billing"]:
                last_sync = _get_last_sync_timestamp(conn_id, source)
                if last_sync:
                    config[f"{source}_last_sync"] = last_sync
                    logger.info(f"Última sincronización {source}: {last_sync}")
        
        logger.info(f"Preparación completada. Período: {start_date} - {end_date}")
        return config
    
    @task(task_id="extract_crm_data", execution_timeout=timedelta(minutes=15))
    def extract_crm_data(config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos del CRM (Salesforce o Pipedrive)."""
        crm_type = config["crm_type"]
        crm_config = config["crm_config"]
        start_date = config["start_date"]
        end_date = config["end_date"]
        
        tags = {"crm_type": crm_type, "source": "crm"}
        
        with _track_metric("extract_crm_data", tags=tags):
            logger.info(f"Extrayendo datos de CRM: {crm_type}")
            
            try:
                from data.integrations.connectors import create_connector
                
                # Crear conector según tipo con retry
                def _create_and_connect():
                    if crm_type == "salesforce":
                        connector_config = {
                            "username": crm_config.get("username"),
                            "password": crm_config.get("password"),
                            "security_token": crm_config.get("security_token"),
                            "client_id": crm_config.get("client_id"),
                            "client_secret": crm_config.get("client_secret"),
                            "sandbox": crm_config.get("sandbox", False),
                        }
                    elif crm_type == "pipedrive":
                        connector_config = {
                            "api_token": crm_config.get("api_token"),
                            "company_domain": crm_config.get("company_domain"),
                        }
                    else:
                        raise ValueError(f"Tipo de CRM no soportado: {crm_type}")
                    
                    connector = create_connector(crm_type, connector_config)
                    
                    if not connector.connect():
                        raise Exception(f"No se pudo conectar al CRM {crm_type}")
                    
                    return connector
                
                connector = _retry_with_exponential_backoff(
                    _create_and_connect,
                    max_retries=3,
                    base_delay=2.0,
                    retry_on_exceptions=(Exception,)
                )
                
                # Extraer contactos/leads
                filters = {
                    "since": start_date,
                    "until": end_date,
                }
                
                if crm_type == "salesforce":
                    filters["sobject_type"] = "Contact"
                    filters["where"] = f"LastModifiedDate >= {start_date}T00:00:00Z AND LastModifiedDate < {end_date}T23:59:59Z"
                else:  # pipedrive
                    filters["resource_type"] = "persons"
                
                def _read_records():
                    return connector.read_records(filters=filters, limit=10000)
                
                records = _retry_with_exponential_backoff(
                    _read_records,
                    max_retries=2,
                    base_delay=1.0,
                    retry_on_exceptions=(Exception,)
                )
                
                connector.disconnect()
                
                # Convertir a formato estándar
                crm_data = []
                total = len(records)
                for idx, record in enumerate(records):
                    crm_data.append({
                        "source_id": record.source_id,
                        "source_type": f"crm_{crm_type}",
                        "data": record.data,
                        "metadata": record.metadata,
                    })
                    _log_progress(idx + 1, total, "extract_crm_data", interval=100)
                
                if STATS_AVAILABLE:
                    try:
                        Stats.incr("data_integration_etl.extract_crm_data.records", len(crm_data), tags=tags)
                        Stats.gauge("data_integration_etl.extract_crm_data.count", len(crm_data), tags=tags)
                    except Exception:
                        pass
                
                logger.info(f"Extraídos {len(crm_data)} registros del CRM")
                
                return {
                    "source": "crm",
                    "records": crm_data,
                    "count": len(crm_data),
                    "extracted_at": datetime.utcnow().isoformat(),
                }
                
            except Exception as e:
                logger.error(f"Error extrayendo datos del CRM: {e}", exc_info=True)
                if config["enable_alerts"] and NOTIFICATIONS_AVAILABLE:
                    notify_slack(
                        f"⚠️ Error extrayendo datos del CRM {crm_type}: {str(e)}",
                        extra_context={"crm_type": crm_type, "error": str(e)}
                    )
                raise
    
    @task(task_id="extract_sheets_data")
    def extract_sheets_data(config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos de Google Sheets."""
        spreadsheet_id = config["sheets_spreadsheet_id"]
        credentials_json = config["sheets_credentials_json"]
        range_name = config["sheets_range"]
        
        if not spreadsheet_id:
            logger.warning("No se proporcionó spreadsheet_id, saltando extracción de Sheets")
            return {
                "source": "sheets",
                "records": [],
                "count": 0,
                "extracted_at": datetime.utcnow().isoformat(),
            }
        
        logger.info(f"Extrayendo datos de Google Sheets: {spreadsheet_id}")
        
        try:
            from data.integrations.connectors import create_connector
            
            # Crear conector de Google Sheets
            connector_config = {
                "credentials_json": credentials_json if credentials_json else None,
                "credentials_path": os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH"),
                "spreadsheet_id": spreadsheet_id,
            }
            
            connector = create_connector("google_sheets", connector_config)
            
            if not connector.connect():
                raise Exception("No se pudo conectar a Google Sheets")
            
            # Extraer datos
            filters = {"range": range_name}
            records = connector.read_records(filters=filters)
            
            connector.disconnect()
            
            # Convertir a formato estándar
            sheets_data = []
            for record in records:
                sheets_data.append({
                    "source_id": record.source_id,
                    "source_type": "google_sheets",
                    "data": record.data,
                    "metadata": record.metadata,
                })
            
            logger.info(f"Extraídos {len(sheets_data)} registros de Google Sheets")
            
            return {
                "source": "sheets",
                "records": sheets_data,
                "count": len(sheets_data),
                "extracted_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de Google Sheets: {e}", exc_info=True)
            if config["enable_alerts"] and NOTIFICATIONS_AVAILABLE:
                notify_slack(
                    f"⚠️ Error extrayendo datos de Google Sheets: {str(e)}",
                    extra_context={"spreadsheet_id": spreadsheet_id, "error": str(e)}
                )
            # No fallar el DAG si Sheets falla, solo loguear
            return {
                "source": "sheets",
                "records": [],
                "count": 0,
                "error": str(e),
                "extracted_at": datetime.utcnow().isoformat(),
            }
    
    @task(task_id="extract_billing_data")
    def extract_billing_data(config: Dict[str, Any]) -> Dict[str, Any]:
        """Extrae datos del sistema de facturación."""
        billing_source = config["billing_source"]
        start_date = config["start_date"]
        end_date = config["end_date"]
        conn_id = config["postgres_conn_id"]
        
        logger.info(f"Extrayendo datos de facturación desde {billing_source}")
        
        try:
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Extraer facturas y pagos
                    cur.execute("""
                        SELECT 
                            'invoice' as source_type,
                            i.id::text as source_id,
                            jsonb_build_object(
                                'invoice_number', i.serie,
                                'customer_id', i.customer_id,
                                'amount', i.total,
                                'subtotal', i.subtotal,
                                'taxes', i.taxes,
                                'currency', i.currency,
                                'status', i.status,
                                'created_at', i.created_at,
                                'due_date', i.due_date
                            ) as data,
                            jsonb_build_object(
                                'table', 'invoices',
                                'id', i.id
                            ) as metadata
                        FROM invoices i
                        WHERE i.created_at >= %s::date
                        AND i.created_at < (%s::date + INTERVAL '1 day')
                        
                        UNION ALL
                        
                        SELECT 
                            'payment' as source_type,
                            p.payment_id::text as source_id,
                            jsonb_build_object(
                                'payment_id', p.payment_id,
                                'customer_id', p.customer_id,
                                'amount', p.amount,
                                'currency', p.currency,
                                'status', p.status,
                                'payment_method', p.payment_method,
                                'created_at', p.created_at
                            ) as data,
                            jsonb_build_object(
                                'table', 'payments',
                                'payment_id', p.payment_id
                            ) as metadata
                        FROM payments p
                        WHERE p.created_at >= %s::date
                        AND p.created_at < (%s::date + INTERVAL '1 day')
                        ORDER BY created_at DESC
                    """, (start_date, end_date, start_date, end_date))
                    
                    rows = cur.fetchall()
            
            billing_data = []
            for row in rows:
                billing_data.append({
                    "source_id": row[1],
                    "source_type": f"billing_{row[0]}",
                    "data": row[2],
                    "metadata": row[3],
                })
            
            logger.info(f"Extraídos {len(billing_data)} registros de facturación")
            
            return {
                "source": "billing",
                "records": billing_data,
                "count": len(billing_data),
                "extracted_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error extrayendo datos de facturación: {e}", exc_info=True)
            if config["enable_alerts"] and NOTIFICATIONS_AVAILABLE:
                notify_slack(
                    f"⚠️ Error extrayendo datos de facturación: {str(e)}",
                    extra_context={"billing_source": billing_source, "error": str(e)}
                )
            raise
    
    @task_group(group_id="extract_data")
    def extract_data(config: Dict[str, Any]) -> Dict[str, Any]:
        """Grupo de tareas para extraer datos de todas las fuentes."""
        crm_result = extract_crm_data(config)
        sheets_result = extract_sheets_data(config)
        billing_result = extract_billing_data(config)
        
        return {
            "crm": crm_result,
            "sheets": sheets_result,
            "billing": billing_result,
        }
    
    @task(task_id="profile_data", execution_timeout=timedelta(minutes=10))
    def profile_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Genera perfil de datos extraídos."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_profiling = bool(params.get("enable_data_profiling", True))
        
        if not enable_profiling:
            logger.info("Data profiling deshabilitado")
            return {
                **extracted_data,
                "profiling": {"enabled": False}
            }
        
        with _track_metric("profile_data"):
            logger.info("Iniciando data profiling")
            
            profiles = {}
            
            # Profilar cada fuente
            for source_name in ["crm", "sheets", "billing"]:
                source_data = extracted_data.get(source_name, {})
                records = source_data.get("records", [])
                
                if records:
                    profile = _profile_data(records)
                    profiles[source_name] = profile
                    
                    logger.info(
                        f"Profiling {source_name}: {profile['total_records']} registros, "
                        f"{len(profile.get('fields', {}))} campos"
                    )
            
            # Registrar métricas
            if STATS_AVAILABLE:
                try:
                    for source, profile in profiles.items():
                        Stats.gauge(
                            f"data_integration_etl.profile_data.{source}.total_records",
                            profile.get("total_records", 0)
                        )
                        Stats.gauge(
                            f"data_integration_etl.profile_data.{source}.fields_count",
                            len(profile.get("fields", {}))
                        )
                except Exception:
                    pass
            
            return {
                **extracted_data,
                "profiling": {
                    "enabled": True,
                    "profiles": profiles,
                    "profiled_at": datetime.utcnow().isoformat()
                }
            }
    
    @task(task_id="transform_data", execution_timeout=timedelta(minutes=30))
    def transform_data(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Transforma y normaliza los datos de todas las fuentes."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_checkpointing = bool(params.get("enable_checkpointing", True))
        enable_parallel = bool(params.get("enable_parallel_processing", True))
        conn_id = str(params["postgres_conn_id"])
        max_workers = int(params.get("max_workers", 4))
        chunk_size = int(params.get("chunk_size", 500))
        
        with _track_metric("transform_data"):
            logger.info("Iniciando transformación de datos")
            
            # Intentar cargar checkpoint si está habilitado
            checkpoint_data = None
            if enable_checkpointing:
                checkpoint_data = _load_checkpoint("transform_data", conn_id)
                if checkpoint_data:
                    logger.info("Checkpoint encontrado, continuando desde último punto")
            
            transformed_records = []
            transformation_stats = {
                "crm": {"input": 0, "output": 0, "errors": 0},
                "sheets": {"input": 0, "output": 0, "errors": 0},
                "billing": {"input": 0, "output": 0, "errors": 0},
            }
            
            # Obtener config para DLQ
            enable_dlq = bool(params.get("enable_dlq", True))
            
            # Función de transformación para un registro
            def _transform_record(record: Dict[str, Any], source_type: str) -> Optional[Dict[str, Any]]:
                """Transforma un registro individual."""
                try:
                    source_data = record["data"]
                    
                    if "crm" in source_type:
                        transformed = {
                            "source_id": record["source_id"],
                            "source_type": source_type,
                            "customer_id": source_data.get("Id") or source_data.get("id"),
                            "email": source_data.get("Email") or source_data.get("email"),
                            "first_name": source_data.get("FirstName") or source_data.get("first_name"),
                            "last_name": source_data.get("LastName") or source_data.get("last_name"),
                            "phone": source_data.get("Phone") or source_data.get("phone"),
                            "company": source_data.get("Company") or source_data.get("org_name"),
                            "status": source_data.get("Status") or source_data.get("status"),
                            "created_at": source_data.get("CreatedDate") or source_data.get("add_time"),
                            "updated_at": source_data.get("LastModifiedDate") or source_data.get("update_time"),
                            "raw_data": source_data,
                        }
                    elif "sheets" in source_type:
                        transformed = {
                            "source_id": record["source_id"],
                            "source_type": "google_sheets",
                            "customer_id": source_data.get("customer_id") or source_data.get("Customer ID"),
                            "email": source_data.get("email") or source_data.get("Email"),
                            "first_name": source_data.get("first_name") or source_data.get("First Name"),
                            "last_name": source_data.get("last_name") or source_data.get("Last Name"),
                            "phone": source_data.get("phone") or source_data.get("Phone"),
                            "company": source_data.get("company") or source_data.get("Company"),
                            "amount": source_data.get("amount") or source_data.get("Amount"),
                            "notes": source_data.get("notes") or source_data.get("Notes"),
                            "raw_data": source_data,
                        }
                    elif "billing" in source_type:
                        transformed = {
                            "source_id": record["source_id"],
                            "source_type": source_type,
                            "customer_id": source_data.get("customer_id"),
                            "amount": float(source_data.get("amount", 0)),
                            "subtotal": float(source_data.get("subtotal", 0)) if source_data.get("subtotal") else None,
                            "taxes": float(source_data.get("taxes", 0)) if source_data.get("taxes") else None,
                            "currency": source_data.get("currency", "USD"),
                            "status": source_data.get("status"),
                            "created_at": source_data.get("created_at"),
                            "due_date": source_data.get("due_date"),
                            "payment_method": source_data.get("payment_method"),
                            "raw_data": source_data,
                        }
                    else:
                        return None
                    
                    return transformed
                except Exception as e:
                    logger.error(f"Error transformando registro: {e}", exc_info=True)
                    if enable_dlq:
                        try:
                            _save_to_dlq(record, str(e), f"transform_{source_type}")
                        except Exception:
                            pass
                    return None
            
            # Transformar datos del CRM
            crm_data = extracted_data.get("crm", {}).get("records", [])
            transformation_stats["crm"]["input"] = len(crm_data)
            
            if enable_parallel and len(crm_data) > chunk_size:
                # Procesamiento paralelo
                chunks = _chunk_list(crm_data, chunk_size)
                logger.info(f"Procesando {len(crm_data)} registros CRM en {len(chunks)} chunks paralelos")
                
                def process_crm_chunk(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                    results = []
                    for record in chunk:
                        transformed = _transform_record(record, record.get("source_type", ""))
                        if transformed:
                            results.append(transformed)
                    return results
                
                crm_transformed = _process_chunk_parallel(chunks, process_crm_chunk, max_workers)
                transformed_records.extend(crm_transformed)
                transformation_stats["crm"]["output"] = len(crm_transformed)
                transformation_stats["crm"]["errors"] = len(crm_data) - len(crm_transformed)
            else:
                # Procesamiento secuencial
                for idx, record in enumerate(crm_data):
                    transformed = _transform_record(record, record.get("source_type", ""))
                    if transformed:
                        transformed_records.append(transformed)
                        transformation_stats["crm"]["output"] += 1
                    else:
                        transformation_stats["crm"]["errors"] += 1
                    _log_progress(idx + 1, len(crm_data), "transform_crm", interval=100)
        
        # Transformar datos de Google Sheets
        sheets_data = extracted_data.get("sheets", {}).get("records", [])
        transformation_stats["sheets"]["input"] = len(sheets_data)
        
        if enable_parallel and len(sheets_data) > chunk_size:
            chunks = _chunk_list(sheets_data, chunk_size)
            logger.info(f"Procesando {len(sheets_data)} registros Sheets en {len(chunks)} chunks paralelos")
            
            def process_sheets_chunk(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                results = []
                for record in chunk:
                    transformed = _transform_record(record, "google_sheets")
                    if transformed:
                        results.append(transformed)
                return results
            
            sheets_transformed = _process_chunk_parallel(chunks, process_sheets_chunk, max_workers)
            transformed_records.extend(sheets_transformed)
            transformation_stats["sheets"]["output"] = len(sheets_transformed)
            transformation_stats["sheets"]["errors"] = len(sheets_data) - len(sheets_transformed)
        else:
            for record in sheets_data:
                transformed = _transform_record(record, "google_sheets")
                if transformed:
                    transformed_records.append(transformed)
                    transformation_stats["sheets"]["output"] += 1
                else:
                    transformation_stats["sheets"]["errors"] += 1
        
        # Transformar datos de facturación
        billing_data = extracted_data.get("billing", {}).get("records", [])
        transformation_stats["billing"]["input"] = len(billing_data)
        
        if enable_parallel and len(billing_data) > chunk_size:
            chunks = _chunk_list(billing_data, chunk_size)
            logger.info(f"Procesando {len(billing_data)} registros Billing en {len(chunks)} chunks paralelos")
            
            def process_billing_chunk(chunk: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
                results = []
                for record in chunk:
                    transformed = _transform_record(record, record.get("source_type", ""))
                    if transformed:
                        results.append(transformed)
                return results
            
            billing_transformed = _process_chunk_parallel(chunks, process_billing_chunk, max_workers)
            transformed_records.extend(billing_transformed)
            transformation_stats["billing"]["output"] = len(billing_transformed)
            transformation_stats["billing"]["errors"] = len(billing_data) - len(billing_transformed)
        else:
            for record in billing_data:
                transformed = _transform_record(record, record.get("source_type", ""))
                if transformed:
                    transformed_records.append(transformed)
                    transformation_stats["billing"]["output"] += 1
                else:
                    transformation_stats["billing"]["errors"] += 1
        
        logger.info(f"Transformación completada. Registros: {len(transformed_records)}")
        logger.info(f"Estadísticas: {transformation_stats}")
        
        # Detectar PII si está habilitado
        pii_detection_info = {}
        if bool(params.get("enable_pii_detection", True)):
            logger.info("Detectando información PII")
            pii_stats = {
                "total_with_pii": 0,
                "pii_fields_found": defaultdict(int)
            }
            
            for record in transformed_records:
                pii_result = _detect_pii(record)
                record["pii_detection"] = pii_result
                
                if pii_result["has_pii"]:
                    pii_stats["total_with_pii"] += 1
                    for field in pii_result["pii_fields"]:
                        pii_stats["pii_fields_found"][field] += 1
            
            pii_detection_info = {
                "enabled": True,
                "total_with_pii": pii_stats["total_with_pii"],
                "pii_fields_found": dict(pii_stats["pii_fields_found"])
            }
            
            logger.info(f"PII detectado en {pii_stats['total_with_pii']} registros")
            
            # Enmascarar PII si está habilitado
            if bool(params.get("enable_pii_masking", False)):
                logger.info("Enmascarando información PII")
                transformed_records = [
                    _mask_pii(record, ["email", "phone"]) if record.get("pii_detection", {}).get("has_pii") else record
                    for record in transformed_records
                ]
                pii_detection_info["masking_enabled"] = True
        else:
            pii_detection_info = {"enabled": False}
        
        # Enriquecer datos si está habilitado
        if bool(params.get("enable_data_enrichment", True)):
            enrichment_config = {
                "version": "1.0",
                "enabled_features": ["email_domain", "full_name", "amount_formatted"]
            }
            logger.info("Enriqueciendo datos")
            transformed_records = [
                _enrich_record(record, enrichment_config) 
                for record in transformed_records
            ]
        
        # Deduplicar si está habilitado
        deduplication_info = {}
        if bool(params.get("enable_deduplication", True)):
            dedup_fields = params.get("deduplication_fields", ["email", "customer_id"])
            dedup_strategy = params.get("deduplication_strategy", "latest")
            
            if isinstance(dedup_fields, str):
                dedup_fields = [f.strip() for f in dedup_fields.split(",")]
            
            logger.info(f"Deduplicando registros usando campos: {dedup_fields}")
            unique_records, duplicates = _deduplicate_records(
                transformed_records,
                dedup_fields,
                dedup_strategy
            )
            
            deduplication_info = {
                "enabled": True,
                "original_count": len(transformed_records),
                "unique_count": len(unique_records),
                "duplicates_count": len(duplicates),
                "dedup_fields": dedup_fields,
                "strategy": dedup_strategy
            }
            
            logger.info(
                f"Deduplicación completada: {len(unique_records)} únicos, "
                f"{len(duplicates)} duplicados detectados"
            )
            
            transformed_records = unique_records
        else:
            deduplication_info = {"enabled": False}
        
        # Registrar métricas
        if STATS_AVAILABLE:
            try:
                Stats.gauge("data_integration_etl.transform_data.total_records", len(transformed_records))
                for source, stats in transformation_stats.items():
                    Stats.gauge(f"data_integration_etl.transform_data.{source}.input", stats["input"])
                    Stats.gauge(f"data_integration_etl.transform_data.{source}.output", stats["output"])
                    Stats.gauge(f"data_integration_etl.transform_data.{source}.errors", stats["errors"])
            except Exception:
                pass
        
        # Reconciliación de datos si está habilitada
        reconciliation_info = {}
        if bool(params.get("enable_data_reconciliation", True)) and len(transformed_records) > 1:
            reconciliation_threshold = float(params.get("reconciliation_threshold", 0.85))
            logger.info(f"Reconciliando datos (threshold: {reconciliation_threshold})")
            
            reconciliation_result = _reconcile_records(
                transformed_records,
                ["email", "customer_id"],
                reconciliation_threshold
            )
            
            reconciliation_info = {
                "enabled": True,
                "matched_pairs": len(reconciliation_result["matched_pairs"]),
                "unmatched": len(reconciliation_result["unmatched"]),
                "conflicts": len(reconciliation_result["conflicts"]),
                "total_records": reconciliation_result["total_records"]
            }
            
            logger.info(
                f"Reconciliación: {reconciliation_info['matched_pairs']} pares encontrados, "
                f"{reconciliation_info['conflicts']} conflictos detectados"
            )
        else:
            reconciliation_info = {"enabled": False}
        
        # Calcular scores de calidad si está habilitado
        quality_scoring_info = {}
        if bool(params.get("enable_quality_scoring", True)):
            logger.info("Calculando scores de calidad de datos")
            dataset_quality = _calculate_dataset_quality_score(transformed_records)
            quality_scoring_info = {
                "enabled": True,
                "average_score": dataset_quality["average_score"],
                "quality_distribution": dataset_quality["quality_distribution"],
                "total_records": dataset_quality["total_records"]
            }
            logger.info(f"Score promedio de calidad: {dataset_quality['average_score']}/100")
        else:
            quality_scoring_info = {"enabled": False}
        
        # Validar con reglas de calidad si está habilitado
        quality_rules_info = {}
        if bool(params.get("enable_quality_rules", True)):
            logger.info("Validando datos con reglas de calidad")
            rule_engine = DataQualityRuleEngine()
            rules_validation = rule_engine.validate_dataset(transformed_records)
            quality_rules_info = {
                "enabled": True,
                "total_records": rules_validation["total_records"],
                "records_passed": rules_validation["records_passed"],
                "records_failed": rules_validation["records_failed"],
                "pass_rate": rules_validation["pass_rate"],
                "rule_violations": rules_validation["rule_violations"],
                "severity_counts": rules_validation["severity_counts"]
            }
            logger.info(
                f"Reglas de calidad: {rules_validation['records_passed']}/{rules_validation['total_records']} "
                f"registros pasaron ({rules_validation['pass_rate']:.2f}%)"
            )
        else:
            quality_rules_info = {"enabled": False}
        
        result = {
            "records": transformed_records,
            "stats": transformation_stats,
            "transformed_at": datetime.utcnow().isoformat(),
            "deduplication": deduplication_info,
            "pii_detection": pii_detection_info,
            "reconciliation": reconciliation_info,
            "quality_scoring": quality_scoring_info,
            "quality_rules": quality_rules_info,
        }
        
        # Guardar checkpoint si está habilitado
        if enable_checkpointing:
            try:
                _save_checkpoint("transform_data", {
                    "last_processed": len(transformed_records),
                    "stats": transformation_stats,
                    "timestamp": datetime.utcnow().isoformat()
                }, conn_id)
            except Exception as e:
                logger.warning(f"Error saving checkpoint: {e}")
        
        return result
    
    @task(task_id="validate_data", execution_timeout=timedelta(minutes=15))
    def validate_data(transformed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida la calidad de los datos transformados."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_validation = bool(params["enable_validation"])
        enable_schema_validation = bool(params.get("enable_schema_validation", True))
        
        if not enable_validation:
            logger.info("Validación deshabilitada, saltando validación")
            return {
                **transformed_data,
                "validation": {
                    "enabled": False,
                    "passed": True,
                }
            }
        
        with _track_metric("validate_data"):
            logger.info("Iniciando validación de datos")
        
        records = transformed_data["records"]
        validation_results = {
            "total": len(records),
            "valid": 0,
            "invalid": 0,
            "errors": [],
            "warnings": [],
            "schema_validation": {"enabled": False} if not enable_schema_validation else {},
        }
        
        # Configurar validación de esquema si está habilitada
        schema_validator = None
        if enable_schema_validation:
            schema_rules = [
                SchemaRule("email", required=True, field_type=str, pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"),
                SchemaRule("customer_id", required=False, field_type=str),
                SchemaRule("amount", required=False, field_type=(int, float), min_value=0),
                SchemaRule("currency", required=False, field_type=str, allowed_values=["USD", "EUR", "GBP", "MXN", "CAD", "AUD"]),
            ]
            schema_validator = SchemaValidator(schema_rules)
            validation_results["schema_validation"]["enabled"] = True
            validation_results["schema_validation"]["schema_errors"] = []
        
        for idx, record in enumerate(records):
            errors = []
            warnings = []
            
            # Validación de esquema
            if schema_validator:
                is_valid, schema_errors = schema_validator.validate_record(record)
                if not is_valid:
                    errors.extend(schema_errors)
                    validation_results["schema_validation"]["schema_errors"].extend([
                        f"Registro #{idx+1}: {e}" for e in schema_errors
                    ])
            
            # Validar campos requeridos según tipo
            source_type = record.get("source_type", "")
            
            if "crm" in source_type or "sheets" in source_type:
                # Validar email
                email = record.get("email")
                if email:
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if not re.match(email_pattern, email):
                        errors.append(f"Email inválido: {email}")
                else:
                    warnings.append("Email faltante")
            
            if "billing" in source_type:
                # Validar montos
                amount = record.get("amount")
                if amount is None or amount < 0:
                    errors.append(f"Monto inválido: {amount}")
                
                # Validar currency
                currency = record.get("currency")
                if currency and currency not in ["USD", "EUR", "MXN", "ARS"]:
                    warnings.append(f"Moneda no estándar: {currency}")
            
            # Validar customer_id
            customer_id = record.get("customer_id")
            if not customer_id:
                warnings.append("customer_id faltante")
            
            if errors:
                validation_results["invalid"] += 1
                validation_results["errors"].extend(errors)
                record["validation_errors"] = errors
            else:
                validation_results["valid"] += 1
                if warnings:
                    validation_results["warnings"].extend(warnings)
                    record["validation_warnings"] = warnings
        
        logger.info(
            f"Validación completada. Válidos: {validation_results['valid']}, "
            f"Inválidos: {validation_results['invalid']}"
        )
        
        # Normalizar monedas si está habilitado
        normalized_records = transformed_data["records"]
        currency_conversion_info = {}
        
        if bool(params.get("enable_currency_conversion", False)):
            target_currency = str(params.get("target_currency", "USD"))
            logger.info(f"Normalizando monedas a {target_currency}")
            normalized_records = _normalize_currency(transformed_data["records"], target_currency)
            currency_conversion_info = {
                "enabled": True,
                "target_currency": target_currency,
                "converted_count": sum(1 for r in normalized_records if r.get("currency_converted", False))
            }
        else:
            currency_conversion_info = {"enabled": False}
        
        # Detectar outliers si está habilitado
        outlier_analysis = {}
        if bool(params.get("enable_outlier_detection", True)):
            logger.info("Analizando outliers")
            outlier_analysis = _analyze_outliers(normalized_records, "amount")
            if outlier_analysis.get("outlier_count", 0) > 0:
                logger.warning(
                    f"Detectados {outlier_analysis['outlier_count']} outliers en campo 'amount' "
                    f"({outlier_analysis.get('outlier_percentage', 0):.2f}%)"
                )
        
        # Análisis temporal si está habilitado
        temporal_analysis = {}
        if bool(params.get("enable_temporal_analysis", True)):
            logger.info("Analizando tendencias temporales")
            temporal_analysis = _analyze_temporal_trends(normalized_records, "created_at", "amount")
            if temporal_analysis.get("trend") != "insufficient_data":
                logger.info(
                    f"Tendencia detectada: {temporal_analysis['trend']}, "
                    f"tasa de crecimiento: {temporal_analysis.get('growth_rate', 0):.2f}%"
                )
        
        # Detección de deriva de datos si está habilitada
        drift_detection = {}
        if bool(params.get("enable_data_drift_detection", True)):
            logger.info("Detectando deriva de datos")
            try:
                conn_id = str(params["postgres_conn_id"])
                drift_fields = ["amount", "customer_id", "status", "currency"]
                drift_detection = _detect_data_drift(
                    current_data=normalized_records,
                    baseline_data=None,
                    fields=drift_fields,
                    conn_id=conn_id,
                    threshold=float(params.get("drift_detection_threshold", 0.05))
                )
                if drift_detection.get("drift_detected", False):
                    logger.warning(
                        f"Deriva de datos detectada. Score: {drift_detection.get('overall_drift_score', 0):.2f}"
                    )
                else:
                    logger.info("No se detectó deriva de datos")
            except Exception as e:
                logger.warning(f"Error en detección de deriva: {e}")
        
        # Detección avanzada de anomalías si está habilitada
        advanced_anomalies = {}
        if bool(params.get("enable_advanced_anomaly_detection", True)):
            logger.info("Detectando anomalías avanzadas")
            try:
                numeric_fields = ["amount"]
                categorical_fields = ["status", "currency", "source_type"]
                advanced_anomalies = _detect_advanced_anomalies(
                    records=normalized_records,
                    numeric_fields=numeric_fields,
                    categorical_fields=categorical_fields,
                    methods=["statistical", "isolation_forest", "clustering"]
                )
                if advanced_anomalies.get("anomaly_count", 0) > 0:
                    logger.warning(
                        f"Anomalías detectadas: {advanced_anomalies['anomaly_count']} registros "
                        f"({advanced_anomalies.get('scores', {}).get('anomaly_rate', 0):.2%})"
                    )
                else:
                    logger.info("No se detectaron anomalías avanzadas")
            except Exception as e:
                logger.warning(f"Error en detección avanzada de anomalías: {e}")
        
        # Registrar métricas
        if STATS_AVAILABLE:
            try:
                Stats.gauge("data_integration_etl.validate_data.total", validation_results["total"])
                Stats.gauge("data_integration_etl.validate_data.valid", validation_results["valid"])
                Stats.gauge("data_integration_etl.validate_data.invalid", validation_results["invalid"])
                Stats.gauge("data_integration_etl.validate_data.errors_count", len(validation_results["errors"]))
                Stats.gauge("data_integration_etl.validate_data.warnings_count", len(validation_results["warnings"]))
                if outlier_analysis:
                    Stats.gauge("data_integration_etl.validate_data.outliers", outlier_analysis.get("outlier_count", 0))
            except Exception:
                pass
        
        return {
            **transformed_data,
            "records": normalized_records,
            "validation": {
                "enabled": True,
                "passed": validation_results["invalid"] == 0,
                "results": validation_results,
                "validated_at": datetime.utcnow().isoformat(),
            },
            "currency_conversion": currency_conversion_info,
            "outlier_analysis": outlier_analysis,
            "temporal_analysis": temporal_analysis,
            "drift_detection": drift_detection,
            "advanced_anomalies": advanced_anomalies,
        }
    
    @task(task_id="load_to_warehouse", execution_timeout=timedelta(minutes=45))
    def load_to_warehouse(validated_data: Dict[str, Any]) -> Dict[str, Any]:
        """Carga los datos transformados en el data warehouse."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        batch_size = int(params["batch_size"])
        enable_audit_logging = bool(params.get("enable_audit_logging", True))
        dag_run = ctx.get("dag_run")
        dag_run_id = dag_run.run_id if dag_run else None
        
        start_time = time.time()
        
        with _track_metric("load_to_warehouse"):
            logger.info("Iniciando carga en data warehouse")
        
        records = validated_data["records"]
        hook = PostgresHook(postgres_conn_id=conn_id)
        enable_partitioning = bool(params.get("enable_table_partitioning", False))
        enable_backup = bool(params.get("enable_backup", True))
        table_name = "data_warehouse_integration"
        
        # Crear tabla (particionada o normal)
        if not dry_run:
            if enable_partitioning:
                _create_partitioned_table(conn_id, table_name, "created_at")
            else:
                create_table_sql = """
                    CREATE TABLE IF NOT EXISTS data_warehouse_integration (
                        id SERIAL PRIMARY KEY,
                        source_id VARCHAR(255) NOT NULL,
                        source_type VARCHAR(100) NOT NULL,
                        customer_id VARCHAR(255),
                        email VARCHAR(255),
                        first_name VARCHAR(255),
                        last_name VARCHAR(255),
                        phone VARCHAR(50),
                        company VARCHAR(255),
                        amount DECIMAL(15, 2),
                        currency VARCHAR(10),
                        status VARCHAR(50),
                        raw_data JSONB,
                        validation_errors JSONB,
                        validation_warnings JSONB,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(source_id, source_type)
                    );
                    
                    CREATE INDEX IF NOT EXISTS idx_dw_integration_customer_id 
                        ON data_warehouse_integration(customer_id);
                    CREATE INDEX IF NOT EXISTS idx_dw_integration_email 
                        ON data_warehouse_integration(email);
                    CREATE INDEX IF NOT EXISTS idx_dw_integration_source_type 
                        ON data_warehouse_integration(source_type);
                    CREATE INDEX IF NOT EXISTS idx_dw_integration_created_at 
                        ON data_warehouse_integration(created_at);
                """
                
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute(create_table_sql)
                        conn.commit()
            
            # Crear backup si está habilitado
            backup_name = None
            if enable_backup:
                backup_name = _create_backup(conn_id, table_name)
                if backup_name:
                    logger.info(f"Backup creado antes de carga: {backup_name}")
                else:
                    logger.warning("No se pudo crear backup")
        
            # Insertar datos en batches
            loaded_count = 0
            error_count = 0
            total_batches = (len(records) + batch_size - 1) // batch_size
            
            for i in range(0, len(records), batch_size):
                batch = records[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                if dry_run:
                    logger.info(f"[DRY RUN] Procesando batch {batch_num}/{total_batches} con {len(batch)} registros")
                    loaded_count += len(batch)
                    continue
                
                try:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            for record in batch:
                                try:
                                    cur.execute("""
                                        INSERT INTO data_warehouse_integration (
                                            source_id, source_type, customer_id, email,
                                            first_name, last_name, phone, company,
                                            amount, currency, status, raw_data,
                                            validation_errors, validation_warnings,
                                            updated_at
                                        ) VALUES (
                                            %s, %s, %s, %s, %s, %s, %s, %s,
                                            %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP
                                        )
                                        ON CONFLICT (source_id, source_type) 
                                        DO UPDATE SET
                                            customer_id = EXCLUDED.customer_id,
                                            email = EXCLUDED.email,
                                            first_name = EXCLUDED.first_name,
                                            last_name = EXCLUDED.last_name,
                                            phone = EXCLUDED.phone,
                                            company = EXCLUDED.company,
                                            amount = EXCLUDED.amount,
                                            currency = EXCLUDED.currency,
                                            status = EXCLUDED.status,
                                            raw_data = EXCLUDED.raw_data,
                                            validation_errors = EXCLUDED.validation_errors,
                                            validation_warnings = EXCLUDED.validation_warnings,
                                            updated_at = CURRENT_TIMESTAMP
                                    """, (
                                        record.get("source_id"),
                                        record.get("source_type"),
                                        record.get("customer_id"),
                                        record.get("email"),
                                        record.get("first_name"),
                                        record.get("last_name"),
                                        record.get("phone"),
                                        record.get("company"),
                                        record.get("amount"),
                                        record.get("currency"),
                                        record.get("status"),
                                        json.dumps(record.get("raw_data", {})),
                                        json.dumps(record.get("validation_errors", [])),
                                        json.dumps(record.get("validation_warnings", [])),
                                    ))
                                    loaded_count += 1
                                    
                                except Exception as e:
                                    logger.error(f"Error insertando registro: {e}", exc_info=True)
                                    error_count += 1
                                    
                                    # Guardar en DLQ si está habilitado
                                    ctx = get_current_context()
                                    params = ctx["params"]
                                    if bool(params.get("enable_dlq", True)):
                                        try:
                                            _save_to_dlq(record, str(e), "load_warehouse")
                                        except Exception:
                                            pass
                            
                            conn.commit()
                            
                            # Auditoría por batch si está habilitada
                            if enable_audit_logging:
                                try:
                                    audit_log = _create_audit_log(
                                        action="load_batch",
                                        entity_type="data_integration",
                                        entity_id=f"batch_{batch_num}",
                                        details={
                                            "batch_size": len(batch),
                                            "batch_num": batch_num,
                                            "total_batches": total_batches,
                                            "loaded_in_batch": loaded_count,
                                            "source_types": list(set(r.get("source_type") for r in batch if r.get("source_type")))
                                        },
                                        user="data_integration_etl"
                                    )
                                    audit_log["dag_run_id"] = dag_run_id
                                    _save_audit_log(conn_id, audit_log)
                                except Exception as e:
                                    logger.warning(f"Error guardando audit log: {e}")
                            
                            # Log progreso
                            _log_progress(batch_num, total_batches, "load_to_warehouse", interval=5)
                            
                except Exception as e:
                    logger.error(f"Error procesando batch: {e}", exc_info=True)
                    error_count += len(batch)
                    
                    # Auto-rollback si está habilitado y hay muchos errores
                    if bool(params.get("enable_auto_rollback", False)) and backup_name:
                        error_rate = error_count / len(records) if records else 0
                        if error_rate > 0.5:  # Más del 50% de errores
                            logger.warning(f"Tasa de errores alta ({error_rate:.2%}), iniciando rollback")
                            _rollback_from_backup(conn_id, table_name, backup_name)
                            raise Exception(f"Rollback ejecutado debido a alta tasa de errores ({error_rate:.2%})")
        
            logger.info(
                f"Carga completada. Cargados: {loaded_count}, Errores: {error_count}"
            )
            
            # Archivar datos antiguos si está habilitado
            archive_info = {}
            if bool(params.get("enable_data_archiving", False)):
                archive_days = int(params.get("archive_older_than_days", 90))
                archive_table = f"{table_name}_archive"
                
                logger.info(f"Archivando datos más antiguos de {archive_days} días")
                archive_result = _archive_old_data(
                    conn_id,
                    table_name,
                    archive_table,
                    archive_days
                )
                
                archive_info = {
                    "enabled": True,
                    "archived_count": archive_result.get("archived_count", 0),
                    "archive_table": archive_table,
                    "success": archive_result.get("success", False)
                }
                
                if archive_info["success"]:
                    logger.info(f"Archivados {archive_info['archived_count']} registros en {archive_table}")
                else:
                    logger.warning(f"Error archivando datos: {archive_result.get('error', 'Unknown')}")
            else:
                archive_info = {"enabled": False}
            
            # Crear versión de datos si está habilitado
            version_info = {}
            if bool(params.get("enable_data_versioning", False)):
                dag_run = ctx.get("dag_run")
                run_id = dag_run.run_id if dag_run else "unknown"
                version_name = f"v_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
                
                version_metadata = {
                    "dag_run_id": run_id,
                    "loaded_count": loaded_count,
                    "error_count": error_count,
                    "source_types": list(set(r.get("source_type") for r in records if r.get("source_type")))
                }
                
                version_id = _create_data_version(
                    conn_id,
                    version_name,
                    f"Data integration run {run_id}",
                    loaded_count,
                    version_metadata
                )
                
                if version_id:
                    version_info = {
                        "enabled": True,
                        "version_name": version_id,
                        "created_at": datetime.utcnow().isoformat()
                    }
                    logger.info(f"Versión de datos creada: {version_id}")
                else:
                    version_info = {"enabled": True, "version_name": None, "error": "Failed to create version"}
            else:
                version_info = {"enabled": False}
            
            # Guardar data lineage si está habilitado
            if bool(params.get("enable_data_lineage", True)):
                try:
                    lineage_data = []
                    for record in records[:100]:  # Limitar para no sobrecargar
                        lineage = _generate_data_lineage(
                            record,
                            record.get("source_type", "unknown"),
                            ["extract", "transform", "validate", "load"]
                        )
                        lineage_data.append(lineage)
                    
                    if lineage_data:
                        _save_data_lineage(conn_id, lineage_data)
                        logger.info(f"Data lineage guardado para {len(lineage_data)} registros")
                except Exception as e:
                    logger.warning(f"Error guardando data lineage: {e}")
            
            # Trackear costos si está habilitado
            if bool(params.get("enable_cost_tracking", True)):
                try:
                    duration = time.time() - start_time
                    cost_data = _track_operation_cost(
                        "load_to_warehouse",
                        duration,
                        loaded_count,
                        "compute"
                    )
                    cost_data["dag_run_id"] = dag_run_id
                    _save_cost_tracking(conn_id, cost_data)
                    
                    logger.info(
                        f"Costo estimado de carga: ${cost_data['estimated_cost_usd']:.6f} "
                        f"(${cost_data['cost_per_record']:.8f} por registro)"
                    )
                except Exception as e:
                    logger.warning(f"Error trackeando costos: {e}")
            
            # Registrar en catálogo de datos si está habilitado
            if bool(params.get("enable_data_catalog", True)):
                try:
                    table_schema = {
                        "fields": [
                            {"name": "source_id", "type": "VARCHAR(255)", "nullable": False},
                            {"name": "source_type", "type": "VARCHAR(100)", "nullable": False},
                            {"name": "customer_id", "type": "VARCHAR(255)", "nullable": True},
                            {"name": "email", "type": "VARCHAR(255)", "nullable": True},
                            {"name": "amount", "type": "DECIMAL(15,2)", "nullable": True},
                            {"name": "currency", "type": "VARCHAR(10)", "nullable": True},
                        ]
                    }
                    metadata = {
                        "description": "Tabla de integración de datos de múltiples fuentes",
                        "tags": ["etl", "integration", "warehouse"],
                        "owner": "data_integration_etl",
                        "schema_name": "public"
                    }
                    _register_to_data_catalog(conn_id, table_name, table_schema, metadata)
                except Exception as e:
                    logger.warning(f"Error registrando en catálogo: {e}")
            
            # Validar contratos de datos si está habilitado
            contract_validation = {}
            if bool(params.get("enable_data_contracts", True)):
                try:
                    # Definir contratos por defecto
                    default_contracts = [
                        DataContract(
                            name="data_warehouse_integration_contract",
                            table_name=table_name,
                            rules=[
                                {
                                    "name": "source_id_not_null",
                                    "type": "not_null",
                                    "field": "source_id"
                                },
                                {
                                    "name": "source_type_not_null",
                                    "type": "not_null",
                                    "field": "source_type"
                                },
                                {
                                    "name": "amount_positive",
                                    "type": "range",
                                    "field": "amount",
                                    "min": 0
                                }
                            ],
                            severity="error",
                            enabled=True
                        )
                    ]
                    
                    validator = DataContractValidator(default_contracts)
                    contract_validation = validator.validate(table_name, records[:1000], conn_id)  # Validar muestra
                    
                    if not contract_validation.get("valid", True):
                        logger.warning(
                            f"Contrato de datos violado: {contract_validation.get('violations_count', 0)} violaciones"
                        )
                    else:
                        logger.info("Contratos de datos validados exitosamente")
                except Exception as e:
                    logger.warning(f"Error validando contratos: {e}")
            
            # Registrar métricas
            if STATS_AVAILABLE:
                try:
                    Stats.gauge("data_integration_etl.load_to_warehouse.loaded", loaded_count)
                    Stats.gauge("data_integration_etl.load_to_warehouse.errors", error_count)
                    Stats.gauge("data_integration_etl.load_to_warehouse.total", len(records))
                    if len(records) > 0:
                        success_rate = (loaded_count / len(records)) * 100
                        Stats.gauge("data_integration_etl.load_to_warehouse.success_rate", success_rate)
                except Exception:
                    pass
            
            return {
                **validated_data,
                "load": {
                    "loaded_count": loaded_count,
                    "error_count": error_count,
                    "loaded_at": datetime.utcnow().isoformat(),
                },
                "versioning": version_info,
                "archiving": archive_info,
            }
        
        else:
            # Modo dry-run
            return {
                **validated_data,
                "load": {
                    "loaded_count": len(records),
                    "error_count": 0,
                    "loaded_at": datetime.utcnow().isoformat(),
                },
                "versioning": {"enabled": False, "dry_run": True},
                "archiving": {"enabled": False, "dry_run": True},
            }
    
    @task(task_id="analyze_data_quality", execution_timeout=timedelta(minutes=10))
    def analyze_data_quality(loaded_data: Dict[str, Any]) -> Dict[str, Any]:
        """Análisis profundo de calidad de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        with _track_metric("analyze_data_quality"):
            logger.info("Analizando calidad de datos")
            
            hook = PostgresHook(postgres_conn_id=conn_id)
            quality_metrics = {
                "total_records": 0,
                "completeness": {},
                "duplicates": {},
                "data_freshness": {},
                "anomalies": []
            }
            
            try:
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        # Total de registros
                        cur.execute("SELECT COUNT(*) FROM data_warehouse_integration")
                        quality_metrics["total_records"] = cur.fetchone()[0]
                        
                        # Completitud por campo
                        fields = ["email", "customer_id", "first_name", "last_name", "phone", "company"]
                        for field in fields:
                            cur.execute(f"""
                                SELECT 
                                    COUNT(*) as total,
                                    COUNT({field}) as non_null,
                                    ROUND(COUNT({field})::numeric / COUNT(*) * 100, 2) as completeness_pct
                                FROM data_warehouse_integration
                            """)
                            result = cur.fetchone()
                            quality_metrics["completeness"][field] = {
                                "total": result[0],
                                "non_null": result[1],
                                "completeness_pct": float(result[2]) if result[2] else 0
                            }
                        
                        # Duplicados por email
                        cur.execute("""
                            SELECT email, COUNT(*) as count
                            FROM data_warehouse_integration
                            WHERE email IS NOT NULL
                            GROUP BY email
                            HAVING COUNT(*) > 1
                            ORDER BY count DESC
                            LIMIT 10
                        """)
                        duplicates = cur.fetchall()
                        quality_metrics["duplicates"]["email"] = [
                            {"email": row[0], "count": row[1]} for row in duplicates
                        ]
                        
                        # Freshness (última actualización)
                        cur.execute("""
                            SELECT 
                                MAX(updated_at) as last_update,
                                MIN(updated_at) as first_update,
                                COUNT(*) FILTER (WHERE updated_at > NOW() - INTERVAL '24 hours') as last_24h
                            FROM data_warehouse_integration
                        """)
                        freshness = cur.fetchone()
                        quality_metrics["data_freshness"] = {
                            "last_update": freshness[0].isoformat() if freshness[0] else None,
                            "first_update": freshness[1].isoformat() if freshness[1] else None,
                            "updated_last_24h": freshness[2]
                        }
                        
                        # Anomalías: registros sin customer_id pero con email
                        cur.execute("""
                            SELECT COUNT(*) 
                            FROM data_warehouse_integration
                            WHERE customer_id IS NULL 
                            AND email IS NOT NULL
                            AND source_type NOT LIKE 'sheets%'
                        """)
                        anomaly_count = cur.fetchone()[0]
                        if anomaly_count > 0:
                            quality_metrics["anomalies"].append({
                                "type": "missing_customer_id_with_email",
                                "count": anomaly_count,
                                "severity": "medium"
                            })
            
            except Exception as e:
                logger.error(f"Error analizando calidad de datos: {e}", exc_info=True)
            
            # Registrar métricas
            if STATS_AVAILABLE:
                try:
                    Stats.gauge("data_integration_etl.analyze_data_quality.total_records", 
                               quality_metrics["total_records"])
                    for field, metrics in quality_metrics["completeness"].items():
                        Stats.gauge(
                            f"data_integration_etl.analyze_data_quality.completeness.{field}",
                            metrics["completeness_pct"]
                        )
                    Stats.gauge("data_integration_etl.analyze_data_quality.anomalies_count",
                               len(quality_metrics["anomalies"]))
                except Exception:
                    pass
            
            logger.info(f"Análisis de calidad completado. Anomalías: {len(quality_metrics['anomalies'])}")
            
            return {
                **loaded_data,
                "quality_analysis": quality_metrics,
                "analyzed_at": datetime.utcnow().isoformat(),
            }
    
    @task(task_id="detect_inconsistencies", execution_timeout=timedelta(minutes=10))
    def detect_inconsistencies(loaded_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detecta inconsistencias entre las diferentes fuentes de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        with _track_metric("detect_inconsistencies"):
            logger.info("Detectando inconsistencias")
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        inconsistencies = []
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Detectar emails duplicados con datos diferentes
                    cur.execute("""
                        SELECT 
                            email,
                            COUNT(DISTINCT customer_id) as customer_count,
                            COUNT(DISTINCT first_name) as name_variations,
                            COUNT(DISTINCT source_type) as source_count,
                            array_agg(DISTINCT source_type) as sources
                        FROM data_warehouse_integration
                        WHERE email IS NOT NULL
                        GROUP BY email
                        HAVING COUNT(DISTINCT customer_id) > 1
                        OR COUNT(DISTINCT first_name) > 1
                    """)
                    
                    duplicate_emails = cur.fetchall()
                    for row in duplicate_emails:
                        inconsistencies.append({
                            "type": "duplicate_email",
                            "severity": "high",
                            "description": f"Email {row[0]} aparece con múltiples customer_id o nombres",
                            "details": {
                                "email": row[0],
                                "customer_count": row[1],
                                "name_variations": row[2],
                                "sources": row[4],
                            }
                        })
                    
                    # Detectar montos inconsistentes entre facturación y CRM
                    cur.execute("""
                        SELECT 
                            dw1.customer_id,
                            dw1.amount as billing_amount,
                            dw2.status as crm_status,
                            dw1.source_type,
                            dw2.source_type as crm_source
                        FROM data_warehouse_integration dw1
                        INNER JOIN data_warehouse_integration dw2
                            ON dw1.customer_id = dw2.customer_id
                        WHERE dw1.source_type LIKE 'billing%'
                        AND dw2.source_type LIKE 'crm%'
                        AND dw1.amount IS NOT NULL
                        AND dw1.amount > 0
                        AND dw2.status IN ('closed-lost', 'lost')
                    """)
                    
                    inconsistent_amounts = cur.fetchall()
                    for row in inconsistent_amounts:
                        inconsistencies.append({
                            "type": "inconsistent_amount_status",
                            "severity": "medium",
                            "description": f"Cliente {row[0]} tiene facturas pero el CRM indica 'closed-lost'",
                            "details": {
                                "customer_id": row[0],
                                "billing_amount": float(row[1]),
                                "crm_status": row[2],
                            }
                        })
                    
                    # Detectar registros sin customer_id
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM data_warehouse_integration
                        WHERE customer_id IS NULL
                        AND source_type NOT LIKE 'sheets%'
                    """)
                    
                    missing_customer_id = cur.fetchone()[0]
                    if missing_customer_id > 0:
                        inconsistencies.append({
                            "type": "missing_customer_id",
                            "severity": "low",
                            "description": f"{missing_customer_id} registros sin customer_id",
                            "details": {
                                "count": missing_customer_id,
                            }
                        })
                    
                    # Detectar registros con errores de validación
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM data_warehouse_integration
                        WHERE validation_errors IS NOT NULL
                        AND jsonb_array_length(validation_errors) > 0
                    """)
                    
                    validation_errors_count = cur.fetchone()[0]
                    if validation_errors_count > 0:
                        inconsistencies.append({
                            "type": "validation_errors",
                            "severity": "medium",
                            "description": f"{validation_errors_count} registros con errores de validación",
                            "details": {
                                "count": validation_errors_count,
                            }
                        })
        
        except Exception as e:
            logger.error(f"Error detectando inconsistencias: {e}", exc_info=True)
            inconsistencies.append({
                "type": "detection_error",
                "severity": "high",
                "description": f"Error detectando inconsistencias: {str(e)}",
                "details": {"error": str(e)}
            })
        
            logger.info(f"Detectadas {len(inconsistencies)} inconsistencias")
            
            # Registrar métricas
            if STATS_AVAILABLE:
                try:
                    Stats.gauge("data_integration_etl.detect_inconsistencies.total", len(inconsistencies))
                    severity_counts = {"high": 0, "medium": 0, "low": 0}
                    for inc in inconsistencies:
                        severity = inc.get("severity", "unknown")
                        if severity in severity_counts:
                            severity_counts[severity] += 1
                    for severity, count in severity_counts.items():
                        Stats.gauge(f"data_integration_etl.detect_inconsistencies.{severity}", count)
                except Exception:
                    pass
            
            return {
                **loaded_data,
                "inconsistencies": inconsistencies,
                "detected_at": datetime.utcnow().isoformat(),
            }
    
    @task(task_id="generate_report")
    def generate_report(
        extracted_data: Dict[str, Any],
        transformed_data: Dict[str, Any],
        validated_data: Dict[str, Any],
        loaded_data: Dict[str, Any],
        quality_analysis: Dict[str, Any],
        inconsistencies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera reporte ejecutivo del proceso."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_reports = bool(params.get("enable_reports", True))
        
        if not enable_reports:
            logger.info("Generación de reportes deshabilitada")
            return inconsistencies
        
        with _track_metric("generate_report"):
            logger.info("Generando reporte ejecutivo")
            
            # Generar reporte con datos reales
            report = _generate_executive_report(
                extracted_data=extracted_data,
                transformed_data=transformed_data,
                validated_data=validated_data,
                loaded_data=loaded_data,
                quality_analysis=quality_analysis,
                inconsistencies=inconsistencies.get("inconsistencies", [])
            )
            
            # Guardar reporte en base de datos
            try:
                conn_id = str(params["postgres_conn_id"])
                hook = PostgresHook(postgres_conn_id=conn_id)
                
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS data_integration_reports (
                                id SERIAL PRIMARY KEY,
                                report_date DATE NOT NULL,
                                report_data JSONB NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                                UNIQUE(report_date)
                            );
                            
                            CREATE INDEX IF NOT EXISTS idx_reports_date 
                                ON data_integration_reports(report_date DESC);
                        """)
                        
                        cur.execute("""
                            INSERT INTO data_integration_reports (
                                report_date, report_data
                            ) VALUES (
                                CURRENT_DATE, %s
                            )
                            ON CONFLICT (report_date) 
                            DO UPDATE SET
                                report_data = EXCLUDED.report_data,
                                created_at = CURRENT_TIMESTAMP
                        """, (json.dumps(report),))
                        
                        conn.commit()
                
                logger.info("Reporte ejecutivo guardado en base de datos")
            except Exception as e:
                logger.error(f"Error guardando reporte: {e}", exc_info=True)
            
            # Registrar métricas
            if STATS_AVAILABLE:
                try:
                    Stats.gauge("data_integration_etl.report.total_records", 
                               report["extraction"]["total"])
                    Stats.gauge("data_integration_etl.report.transformation_success_rate",
                               report["transformation"]["success_rate"])
                    Stats.gauge("data_integration_etl.report.load_success_rate",
                               report["load"]["success_rate"])
                    Stats.gauge("data_integration_etl.report.inconsistencies_count",
                               report["inconsistencies"]["total"])
                except Exception:
                    pass
            
            # Calcular health score si está habilitado
            health_score_info = {}
            if bool(params.get("enable_realtime_monitoring", True)):
                try:
                    conn_id = str(params["postgres_conn_id"])
                    health_score = _calculate_health_score(
                        extracted_data,
                        transformed_data,
                        validated_data,
                        loaded_data
                    )
                    health_score_info = health_score
                    
                    # Guardar métricas en tiempo real
                    dag_run = ctx.get("dag_run")
                    dag_run_id = dag_run.run_id if dag_run else None
                    _track_operation_metrics(
                        "pipeline_health",
                        {
                            "health_score": health_score["health_score"],
                            "extraction_score": health_score["components"].get("extraction", 0),
                            "transformation_score": health_score["components"].get("transformation", 0),
                            "validation_score": health_score["components"].get("validation", 0),
                            "load_score": health_score["components"].get("load", 0),
                            "dag_run_id": dag_run_id
                        },
                        conn_id
                    )
                    
                    logger.info(f"Health score calculado: {health_score['health_score']}/100 ({health_score['health_status']})")
                except Exception as e:
                    logger.warning(f"Error calculando health score: {e}")
            
            # Evaluar alertas inteligentes si está habilitado
            alerts_info = []
            if bool(params.get("enable_intelligent_alerting", True)):
                try:
                    alerting = IntelligentAlerting()
                    
                    # Combinar todos los datos para evaluación
                    alert_data = {
                        **transformed_data,
                        **validated_data,
                        **loaded_data,
                        "quality_scoring": transformed_data.get("quality_scoring", {}),
                        "quality_rules": transformed_data.get("quality_rules", {}),
                        "reconciliation": transformed_data.get("reconciliation", {}),
                        "pii_detection": transformed_data.get("pii_detection", {}),
                        "stats": {
                            "total": len(transformed_data.get("records", [])),
                            "errors": sum(s.get("errors", 0) for s in transformed_data.get("stats", {}).values())
                        }
                    }
                    
                    alerts = alerting.evaluate(alert_data, ctx)
                    alerts_info = alerts
                    
                    if alerts:
                        logger.warning(f"{len(alerts)} alertas inteligentes generadas")
                    else:
                        logger.info("No se generaron alertas inteligentes")
                except Exception as e:
                    logger.warning(f"Error evaluando alertas inteligentes: {e}")
            
            # Auto-tuning de rendimiento si está habilitado
            performance_recommendations = {}
            if bool(params.get("enable_performance_autotuning", True)):
                try:
                    conn_id = str(params["postgres_conn_id"])
                    tuner = PerformanceAutoTuner(conn_id)
                    
                    # Calcular métricas de ejecución
                    dag_run = ctx.get("dag_run")
                    dag_run_id = dag_run.run_id if dag_run else None
                    
                    # Obtener tiempo de ejecución aproximado (usar tiempo actual como aproximación)
                    execution_time = 300  # Default 5 minutos, se ajustará con métricas históricas
                    records_processed = len(transformed_data.get("records", []))
                    
                    validation_results_data = validated_data.get("validation", {}).get("results", {})
                    invalid_count = validation_results_data.get("invalid", 0)
                    total_count = validation_results_data.get("total", 1)
                    
                    execution_metrics = {
                        "dag_run_id": dag_run_id,
                        "execution_time": execution_time,
                        "records_processed": records_processed,
                        "error_rate": (invalid_count / max(total_count, 1)) * 100
                    }
                    
                    performance_recommendations = tuner.analyze_performance(params, execution_metrics)
                    
                    if performance_recommendations.get("recommendations"):
                        logger.info(
                            f"Auto-tuning generó {len(performance_recommendations['recommendations'])} recomendaciones"
                        )
                        for rec in performance_recommendations["recommendations"]:
                            logger.info(
                                f"Recomendación: {rec['parameter']} = {rec['recommended_value']} "
                                f"(actual: {rec['current_value']}) - {rec['reason']}"
                            )
                    else:
                        logger.info("No se generaron recomendaciones de auto-tuning")
                except Exception as e:
                    logger.warning(f"Error en auto-tuning de rendimiento: {e}")
            
            return {
                **inconsistencies,
                "report": report,
                "report_generated_at": datetime.utcnow().isoformat(),
                "health_score": health_score_info,
                "alerts": alerts_info,
                "performance_recommendations": performance_recommendations,
            }
    
    @task(task_id="send_alerts")
    def send_alerts(report_data: Dict[str, Any]) -> None:
        """Envía alertas si hay inconsistencias detectadas."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_alerts = bool(params["enable_alerts"])
        
        if not enable_alerts or not NOTIFICATIONS_AVAILABLE:
            logger.info("Alertas deshabilitadas o no disponibles")
            return
        
        inconsistencies = report_data.get("inconsistencies", [])
        alerts = report_data.get("alerts", [])
        health_score = report_data.get("health_score", {})
        
        if not inconsistencies:
            logger.info("No hay inconsistencias, no se envían alertas")
            return
        
        # Filtrar inconsistencias por severidad
        high_severity = [inc for inc in inconsistencies if inc.get("severity") == "high"]
        medium_severity = [inc for inc in inconsistencies if inc.get("severity") == "medium"]
        low_severity = [inc for inc in inconsistencies if inc.get("severity") == "low"]
        
        # Construir mensaje de alerta
        alert_message = f"⚠️ *Inconsistencias detectadas en integración de datos*\n\n"
        
        # Agregar health score si está disponible
        if health_score:
            health_status_emoji = {
                "excellent": "✅",
                "good": "✅",
                "fair": "⚠️",
                "poor": "⚠️",
                "critical": "🔴"
            }
            emoji = health_status_emoji.get(health_score.get("health_status", "unknown"), "⚠️")
            alert_message += f"{emoji} *Health Score:* {health_score.get('health_score', 0)}/100 ({health_score.get('health_status', 'unknown')})\n\n"
        
        alert_message += f"Total de inconsistencias: {len(inconsistencies)}\n"
        alert_message += f"- Alta severidad: {len(high_severity)}\n"
        alert_message += f"- Media severidad: {len(medium_severity)}\n"
        alert_message += f"- Baja severidad: {len(low_severity)}\n\n"
        
        # Agregar alertas inteligentes si hay
        if alerts:
            alert_message += f"*Alertas Inteligentes:* {len(alerts)}\n"
            for alert in alerts[:3]:  # Top 3 alertas
                alert_message += f"• [{alert['severity'].upper()}] {alert['message']}\n"
            if len(alerts) > 3:
                alert_message += f"  ... y {len(alerts) - 3} más\n"
            alert_message += "\n"
        
        # Detalles de inconsistencias de alta severidad
        if high_severity:
            alert_message += "*Inconsistencias de Alta Severidad:*\n"
            for inc in high_severity[:5]:  # Top 5
                alert_message += f"• {inc['description']}\n"
            if len(high_severity) > 5:
                alert_message += f"  ... y {len(high_severity) - 5} más\n"
            alert_message += "\n"
        
        # Detalles de inconsistencias de media severidad
        if medium_severity and len(high_severity) < 5:
            alert_message += "*Inconsistencias de Media Severidad:*\n"
            for inc in medium_severity[:3]:
                alert_message += f"• {inc['description']}\n"
            alert_message += "\n"
        
        # Enviar alerta a Slack
        try:
            notify_slack(
                alert_message,
                extra_context={
                    "total_inconsistencies": len(inconsistencies),
                    "high_severity": len(high_severity),
                    "medium_severity": len(medium_severity),
                    "low_severity": len(low_severity),
                }
            )
            logger.info("Alerta enviada a Slack")
        except Exception as e:
            logger.error(f"Error enviando alerta a Slack: {e}", exc_info=True)
        
        # Si hay inconsistencias de alta severidad, enviar email también
        if high_severity:
            try:
                email_subject = f"Alerta: {len(high_severity)} inconsistencias de alta severidad detectadas"
                email_body = alert_message.replace("*", "").replace("_", "")
                
                # Obtener email de notificación desde variables de entorno
                alert_email = os.getenv("DATA_ALERT_EMAIL", "")
                if alert_email:
                    notify_email(
                        to=alert_email,
                        subject=email_subject,
                        body=email_body,
                    )
                    logger.info(f"Alerta enviada por email a {alert_email}")
            except Exception as e:
                logger.error(f"Error enviando alerta por email: {e}", exc_info=True)
    
    @task(task_id="run_automated_tests")
    def run_automated_tests(
        extracted_data: Dict[str, Any],
        transformed_data: Dict[str, Any],
        validated_data: Dict[str, Any],
        loaded_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Ejecuta suite de pruebas automatizadas."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_testing = bool(params.get("enable_automated_testing", True))
        
        if not enable_testing:
            logger.info("Pruebas automatizadas deshabilitadas")
            return {"enabled": False}
        
        with _track_metric("run_automated_tests"):
            logger.info("Ejecutando suite de pruebas automatizadas")
            
            conn_id = str(params["postgres_conn_id"])
            tester = DataPipelineTester(conn_id)
            
            test_results = tester.run_tests(
                extracted_data,
                transformed_data,
                validated_data,
                loaded_data
            )
            
            logger.info(
                f"Pruebas completadas: {test_results['passed']}/{test_results['total_tests']} pasaron, "
                f"estado: {test_results['overall_status']}"
            )
            
            return {
                "enabled": True,
                "test_results": test_results
            }
    
    # Pipeline principal
    health = health_check()
    config = prepare_extraction()
    health >> config  # Health check debe pasar antes de continuar
    extracted = extract_data(config)
    profiled = profile_data(extracted)
    transformed = transform_data(profiled)
    validated = validate_data(transformed)
    loaded = load_to_warehouse(validated)
    quality_analyzed = analyze_data_quality(loaded)
    inconsistencies = detect_inconsistencies(quality_analyzed)
    
    # Ejecutar pruebas automatizadas
    test_results = run_automated_tests(
        extracted_data=extracted,
        transformed_data=transformed,
        validated_data=validated,
        loaded_data=loaded
    )
    
    # Generar reporte con datos de todas las etapas
    report = generate_report(
        extracted_data=extracted,
        transformed_data=transformed,
        validated_data=validated,
        loaded_data=loaded,
        quality_analysis=quality_analyzed,
        inconsistencies=inconsistencies
    )
    send_alerts(report)


dag = data_integration_etl()

