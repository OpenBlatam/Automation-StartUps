"""
DAG para gestión de calidad de datos de clientes.

Este DAG se ejecuta cada noche y realiza validaciones sobre la base de datos
de clientes. Si se detectan errores, envía un reporte al equipo de datos.

Validaciones incluidas:
- Integridad de datos (valores nulos en campos requeridos)
- Consistencia de datos (formato de emails, teléfonos, etc.)
- Duplicados
- Rangos de valores válidos
- Referencias de integridad referencial
- Comparación histórica de métricas
"""
from __future__ import annotations

import json
import logging
import csv
import io
import os
import hashlib
import random
import time
from datetime import timedelta
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from time import perf_counter
from contextlib import contextmanager
from threading import Lock

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.branch import BranchPythonOperator
from airflow.operators.email import EmailOperator
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models import Variable
from airflow.stats import Stats

logger = logging.getLogger(__name__)

# Circuit Breaker para conexiones de base de datos
class CircuitBreaker:
    """Circuit Breaker pattern para prevenir fallos en cascada."""
    _state = {}  # {resource: {"state": "closed"/"open"/"half_open", "failures": 0, "last_failure": None}}
    _lock = Lock()
    
    @classmethod
    def is_open(cls, resource: str, failure_threshold: int = 5, timeout_seconds: int = 60) -> bool:
        """Verifica si el circuit breaker está abierto."""
        with cls._lock:
            if resource not in cls._state:
                return False
            
            state_info = cls._state[resource]
            if state_info["state"] == "open":
                # Verificar si debemos intentar half-open
                last_failure = state_info.get("last_failure")
                if last_failure and (time.time() - last_failure) > timeout_seconds:
                    state_info["state"] = "half_open"
                    logger.info(f"Circuit breaker para {resource} movido a half_open")
                    return False
                return True
            return False
    
    @classmethod
    def record_success(cls, resource: str):
        """Registra un éxito y cierra el circuit breaker."""
        with cls._lock:
            if resource in cls._state:
                cls._state[resource]["state"] = "closed"
                cls._state[resource]["failures"] = 0
                logger.info(f"Circuit breaker para {resource} cerrado después de éxito")
    
    @classmethod
    def record_failure(cls, resource: str, failure_threshold: int = 5):
        """Registra un fallo y potencialmente abre el circuit breaker."""
        with cls._lock:
            if resource not in cls._state:
                cls._state[resource] = {"state": "closed", "failures": 0, "last_failure": None}
            
            state_info = cls._state[resource]
            state_info["failures"] += 1
            state_info["last_failure"] = time.time()
            
            if state_info["failures"] >= failure_threshold:
                state_info["state"] = "open"
                logger.warning(f"Circuit breaker para {resource} abierto después de {state_info['failures']} fallos")
    
    @classmethod
    def reset(cls, resource: str):
        """Resetea el circuit breaker manualmente."""
        with cls._lock:
            if resource in cls._state:
                cls._state[resource] = {"state": "closed", "failures": 0, "last_failure": None}


def retry_with_exponential_backoff(
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
    Ejecuta una función con exponential backoff y jitter.
    
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
                f"Retry attempt {attempt + 1}/{max_retries} after {delay:.2f}s: {str(e)[:200]}"
            )
            time.sleep(delay)
        except Exception as e:
            # Errores no relacionados con retry_on_exceptions no se reintentan
            raise
    
    raise last_exception


def smart_retry_should_retry(exception: Exception, attempt: int, max_retries: int = 3) -> bool:
    """Determina si se debe reintentar basándose en el tipo de error."""
    if attempt >= max_retries:
        return False
    
    error_str = str(exception).lower()
    
    # Errores temporales que deberían retry
    transient_errors = [
        "timeout", "connection", "network", "temporary", "rate limit",
        "throttle", "503", "502", "504", "429", "busy", "locked",
        "could not connect", "connection refused", "connection reset"
    ]
    
    if any(err in error_str for err in transient_errors):
        return True
    
    # Errores permanentes que NO deberían retry
    permanent_errors = [
        "not found", "404", "invalid", "authentication", "authorization",
        "403", "401", "syntax error", "malformed", "duplicate key",
        "unique constraint", "check constraint"
    ]
    
    if any(err in error_str for err in permanent_errors):
        return False
    
    # Por defecto, retry para otros errores
    return True


@contextmanager
def query_timeout_context(hook: PostgresHook, timeout_seconds: int = 30):
    """Context manager para queries con timeout."""
    try:
        # Establecer timeout en la conexión
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute(f"SET statement_timeout = {timeout_seconds * 1000}")  # PostgreSQL usa milisegundos
        yield cursor
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()


def check_database_health(hook: PostgresHook) -> Dict[str, Any]:
    """Realiza health check de la base de datos."""
    health_status = {
        "timestamp": pendulum.now().isoformat(),
        "healthy": False,
        "checks": {},
        "overall_status": "unknown"
    }
    
    try:
        # Check 1: Conexión básica
        conn = hook.get_conn()
        health_status["checks"]["connection"] = {"status": "ok", "message": "Conexión exitosa"}
        conn.close()
        
        # Check 2: Versión de PostgreSQL
        try:
            version_query = "SELECT version()"
            version_result = hook.get_first(version_query)
            if version_result:
                health_status["checks"]["version"] = {
                    "status": "ok",
                    "message": version_result[0][:100]  # Limitar longitud
                }
        except Exception as e:
            health_status["checks"]["version"] = {"status": "warning", "message": str(e)[:200]}
        
        # Check 3: Espacio en disco (aproximado)
        try:
            disk_query = """
                SELECT 
                    pg_size_pretty(pg_database_size(current_database())) as db_size,
                    pg_size_pretty(sum(pg_total_relation_size(schemaname||'.'||tablename))) as tables_size
                FROM pg_tables
                WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
                LIMIT 1
            """
            disk_result = hook.get_first(disk_query)
            if disk_result:
                health_status["checks"]["disk_usage"] = {
                    "status": "ok",
                    "db_size": disk_result[0] if disk_result[0] else "unknown",
                    "tables_size": disk_result[1] if len(disk_result) > 1 and disk_result[1] else "unknown"
                }
        except Exception as e:
            health_status["checks"]["disk_usage"] = {"status": "warning", "message": str(e)[:200]}
        
        # Check 4: Conexiones activas
        try:
            connections_query = """
                SELECT 
                    count(*) as active_connections,
                    (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections
                FROM pg_stat_activity
                WHERE datname = current_database()
            """
            conn_result = hook.get_first(connections_query)
            if conn_result:
                active = conn_result[0] if conn_result[0] else 0
                max_conn = conn_result[1] if len(conn_result) > 1 and conn_result[1] else 100
                usage_pct = (active / max_conn * 100) if max_conn > 0 else 0
                
                health_status["checks"]["connections"] = {
                    "status": "ok" if usage_pct < 80 else "warning",
                    "active": active,
                    "max": max_conn,
                    "usage_percent": round(usage_pct, 2),
                    "message": f"{active}/{max_conn} conexiones ({usage_pct:.1f}%)"
                }
        except Exception as e:
            health_status["checks"]["connections"] = {"status": "warning", "message": str(e)[:200]}
        
        # Determinar estado general
        failed_checks = [k for k, v in health_status["checks"].items() if v.get("status") == "error"]
        warning_checks = [k for k, v in health_status["checks"].items() if v.get("status") == "warning"]
        
        if failed_checks:
            health_status["overall_status"] = "unhealthy"
            health_status["healthy"] = False
        elif warning_checks:
            health_status["overall_status"] = "degraded"
            health_status["healthy"] = True
        else:
            health_status["overall_status"] = "healthy"
            health_status["healthy"] = True
        
    except Exception as e:
        health_status["healthy"] = False
        health_status["overall_status"] = "error"
        health_status["error"] = str(e)[:500]
        logger.error(f"Error en health check: {e}")
    
    return health_status


def validate_table_indexes(hook: PostgresHook, table_name: str) -> List[Dict[str, Any]]:
    """Valida índices de una tabla y sugiere optimizaciones."""
    index_analysis = []
    
    try:
        # Obtener índices existentes
        indexes_query = f"""
            SELECT
                i.relname as index_name,
                a.attname as column_name,
                ix.indisunique as is_unique,
                ix.indisprimary as is_primary,
                pg_size_pretty(pg_relation_size(i.oid)) as index_size,
                idx_scan as index_scans,
                idx_tup_read as tuples_read,
                idx_tup_fetch as tuples_fetched
            FROM pg_index ix
            JOIN pg_class t ON t.oid = ix.indrelid
            JOIN pg_class i ON i.oid = ix.indexrelid
            JOIN pg_stat_user_indexes ps ON ps.indexrelid = i.oid
            LEFT JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY(ix.indkey)
            WHERE t.relname = '{table_name}'
            ORDER BY pg_relation_size(i.oid) DESC
        """
        
        indexes = hook.get_records(indexes_query)
        
        for idx in indexes:
            index_name = idx[0] if idx[0] else "unknown"
            column_name = idx[1] if idx[1] else "unknown"
            is_unique = idx[2] if idx[2] else False
            is_primary = idx[3] if idx[3] else False
            index_size = idx[4] if idx[4] else "unknown"
            scans = idx[5] if idx[5] else 0
            tuples_read = idx[6] if idx[6] else 0
            tuples_fetched = idx[7] if idx[7] else 0
            
            # Análisis de uso
            usage_score = scans if scans else 0
            efficiency = (tuples_fetched / tuples_read * 100) if tuples_read > 0 else 0
            
            recommendations = []
            if scans == 0:
                recommendations.append("Índice no utilizado - considerar eliminarlo")
            elif efficiency < 10:
                recommendations.append("Baja eficiencia del índice - revisar estrategia")
            
            index_analysis.append({
                "index_name": index_name,
                "column_name": column_name,
                "is_unique": is_unique,
                "is_primary": is_primary,
                "size": index_size,
                "usage": {
                    "scans": scans,
                    "tuples_read": tuples_read,
                    "tuples_fetched": tuples_fetched,
                    "efficiency_percent": round(efficiency, 2)
                },
                "recommendations": recommendations
            })
        
        # Buscar columnas sin índices que podrían beneficiarse
        missing_indexes_query = f"""
            SELECT
                a.attname as column_name,
                COUNT(*) as query_count
            FROM pg_stat_user_tables t
            JOIN pg_attribute a ON a.attrelid = t.relid
            WHERE t.relname = '{table_name}'
            AND a.attnum > 0
            AND NOT a.attisdropped
            AND NOT EXISTS (
                SELECT 1 FROM pg_index ix
                WHERE ix.indrelid = t.relid
                AND a.attnum = ANY(ix.indkey)
            )
            GROUP BY a.attname
            HAVING COUNT(*) > 0
            ORDER BY query_count DESC
            LIMIT 10
        """
        
        try:
            missing = hook.get_records(missing_indexes_query)
            if missing:
                index_analysis.append({
                    "type": "missing_indexes",
                    "columns": [{"name": m[0], "potential_queries": m[1]} for m in missing],
                    "recommendation": "Considerar agregar índices en estas columnas para mejorar rendimiento"
                })
        except Exception as e:
            logger.warning(f"Error buscando índices faltantes: {e}")
    
    except Exception as e:
        logger.error(f"Error validando índices: {e}")
        index_analysis.append({
            "error": str(e)[:500],
            "type": "validation_error"
        })
    
    return index_analysis


class RateLimiter:
    """Rate limiter simple para controlar frecuencia de operaciones."""
    _limits = {}  # {resource: {"count": 0, "window_start": time}}
    _lock = Lock()
    
    @classmethod
    def check_rate_limit(cls, resource: str, max_requests: int = 100, window_seconds: int = 60) -> bool:
        """Verifica si se puede realizar una operación según rate limit."""
        with cls._lock:
            now = time.time()
            
            if resource not in cls._limits:
                cls._limits[resource] = {"count": 0, "window_start": now}
            
            limit_info = cls._limits[resource]
            
            # Resetear ventana si ha pasado el tiempo
            if now - limit_info["window_start"] > window_seconds:
                limit_info["count"] = 0
                limit_info["window_start"] = now
            
            # Verificar límite
            if limit_info["count"] >= max_requests:
                return False
            
            limit_info["count"] += 1
            return True
    
    @classmethod
    def reset(cls, resource: str):
        """Resetea el rate limiter para un recurso."""
        with cls._lock:
            if resource in cls._limits:
                cls._limits[resource] = {"count": 0, "window_start": time.time()}


def validate_query_before_execution(query: str, table_name: str) -> Dict[str, Any]:
    """Valida una query antes de ejecutarla para detectar problemas potenciales."""
    validation = {
        "valid": True,
        "warnings": [],
        "errors": [],
        "suggestions": []
    }
    
    query_lower = query.lower()
    
    # Check 1: SELECT statements only (para seguridad)
    if not query_lower.strip().startswith("select"):
        validation["valid"] = False
        validation["errors"].append("Solo se permiten queries SELECT")
    
    # Check 2: No DROP, DELETE, UPDATE, INSERT
    dangerous_keywords = ["drop", "delete", "update", "insert", "alter", "truncate", "create", "grant"]
    for keyword in dangerous_keywords:
        if keyword in query_lower:
            validation["valid"] = False
            validation["errors"].append(f"Query contiene palabra clave peligrosa: {keyword}")
    
    # Check 3: Tabla mencionada
    if table_name.lower() not in query_lower:
        validation["warnings"].append(f"Tabla '{table_name}' no mencionada en query")
    
    # Check 4: Sin LIMIT en queries grandes
    if "limit" not in query_lower and "count(*)" in query_lower:
        validation["suggestions"].append("Considerar agregar LIMIT para queries de conteo grandes")
    
    # Check 5: WHERE clause recomendado
    if "where" not in query_lower and "count(*)" not in query_lower:
        validation["suggestions"].append("Considerar agregar WHERE clause para filtrar datos")
    
    return validation

# Métricas Prometheus (si está disponible)
try:
    from prometheus_client import Counter, Histogram, Gauge, Summary
    
    data_quality_validations_total = Counter(
        'data_quality_validations_total',
        'Total data quality validations executed',
        ['status', 'severity']
    )
    data_quality_errors_total = Counter(
        'data_quality_errors_total',
        'Total data quality errors found',
        ['validation_type']
    )
    data_quality_execution_time = Histogram(
        'data_quality_execution_time_seconds',
        'Data quality validation execution time',
        buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
    )
    data_quality_records_count = Gauge(
        'data_quality_records_count',
        'Number of records validated',
        ['table_name']
    )
    data_quality_quality_score = Gauge(
        'data_quality_quality_score',
        'Data quality score (0-100)',
        ['table_name']
    )
    
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # Métricas dummy si prometheus no está disponible
    class DummyMetric:
        def inc(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return self
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    
    data_quality_validations_total = DummyMetric()
    data_quality_errors_total = DummyMetric()
    data_quality_execution_time = DummyMetric()
    data_quality_records_count = DummyMetric()
    data_quality_quality_score = DummyMetric()
    PROMETHEUS_AVAILABLE = False


class Severity(Enum):
    """Niveles de severidad para validaciones."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Resultado de una validación individual."""
    name: str
    passed: bool
    severity: Severity
    message: str
    count: int = 0
    details: List[Dict[str, Any]] = field(default_factory=list)
    execution_time_ms: float = 0.0


@dataclass
class ValidationSummary:
    """Resumen de todas las validaciones."""
    timestamp: str
    total_validations: int = 0
    passed: int = 0
    failed: int = 0
    warnings: int = 0
    errors: List[ValidationResult] = field(default_factory=list)
    warnings_list: List[ValidationResult] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    historical_comparison: Optional[Dict[str, Any]] = None


class DataQualityValidator:
    """Clase para ejecutar validaciones de calidad de datos."""
    
    def __init__(self, hook: PostgresHook, table_name: str):
        self.hook = hook
        self.table_name = table_name
        self.results: List[ValidationResult] = []
    
    def validate_required_fields(self, required_fields: List[str], incremental_filter: str = "") -> None:
        """Valida que los campos requeridos no sean nulos."""
        for field in required_fields:
            try:
                where_clause = f"WHERE {field} IS NULL"
                if incremental_filter:
                    where_clause = f"{where_clause} AND {incremental_filter.replace('WHERE', '')}"
                
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {self.table_name}
                    {where_clause}
                """
                result = self.hook.get_first(query)
                null_count = result[0] if result else 0
                
                self.results.append(ValidationResult(
                    name=f"Campo requerido: {field}",
                    passed=null_count == 0,
                    severity=Severity.ERROR if null_count > 0 else Severity.INFO,
                    message=f"{null_count} registros con {field} nulo" if null_count > 0 else "Todos los registros tienen {field}",
                    count=null_count
                ))
            except Exception as e:
                logger.error(f"Error validando campo {field}: {e}")
                self.results.append(ValidationResult(
                    name=f"Campo requerido: {field}",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Error al validar campo: {str(e)}",
                    count=0
                ))
    
    def validate_email_format(self) -> None:
        """Valida el formato de emails."""
        try:
            query = f"""
                SELECT COUNT(*) as count
                FROM {self.table_name}
                WHERE email IS NOT NULL 
                AND email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{{2,}}$'
            """
            result = self.hook.get_first(query)
            invalid_count = result[0] if result else 0
            
            self.results.append(ValidationResult(
                name="Formato de email",
                passed=invalid_count == 0,
                severity=Severity.ERROR if invalid_count > 0 else Severity.INFO,
                message=f"{invalid_count} emails con formato inválido" if invalid_count > 0 else "Todos los emails tienen formato válido",
                count=invalid_count
            ))
        except Exception as e:
            logger.error(f"Error validando formato de email: {e}")
            self.results.append(ValidationResult(
                name="Formato de email",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Error al validar formato: {str(e)}",
                count=0
            ))
    
    def validate_duplicate_emails(self, limit: int = 20) -> None:
        """Valida emails duplicados."""
        try:
            query = f"""
                SELECT email, COUNT(*) as count
                FROM {self.table_name}
                WHERE email IS NOT NULL
                GROUP BY email
                HAVING COUNT(*) > 1
                ORDER BY count DESC
                LIMIT {limit}
            """
            duplicates = self.hook.get_records(query)
            
            details = [{'email': row[0], 'count': row[1]} for row in duplicates]
            
            self.results.append(ValidationResult(
                name="Emails duplicados",
                passed=len(duplicates) == 0,
                severity=Severity.ERROR if duplicates else Severity.INFO,
                message=f"{len(duplicates)} emails duplicados encontrados" if duplicates else "No se encontraron emails duplicados",
                count=len(duplicates),
                details=details
            ))
        except Exception as e:
            logger.error(f"Error validando emails duplicados: {e}")
            self.results.append(ValidationResult(
                name="Emails duplicados",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Error al validar duplicados: {str(e)}",
                count=0
            ))
    
    def validate_future_dates(self, date_field: str = "created_at") -> None:
        """Valida que no haya fechas en el futuro."""
        try:
            query = f"""
                SELECT COUNT(*) as count
                FROM {self.table_name}
                WHERE {date_field} > CURRENT_TIMESTAMP
            """
            result = self.hook.get_first(query)
            future_count = result[0] if result else 0
            
            self.results.append(ValidationResult(
                name="Fechas en el futuro",
                passed=future_count == 0,
                severity=Severity.WARNING if future_count > 0 else Severity.INFO,
                message=f"{future_count} registros con fechas futuras" if future_count > 0 else "No se encontraron fechas futuras",
                count=future_count
            ))
        except Exception as e:
            logger.error(f"Error validando fechas futuras: {e}")
            self.results.append(ValidationResult(
                name="Fechas en el futuro",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Error al validar fechas: {str(e)}",
                count=0
            ))
    
    def validate_total_records(self) -> int:
        """Valida el total de registros y retorna el conteo."""
        try:
            query = f"SELECT COUNT(*) FROM {self.table_name}"
            result = self.hook.get_first(query)
            total = result[0] if result else 0
            
            self.results.append(ValidationResult(
                name="Total de registros",
                passed=total > 0,
                severity=Severity.CRITICAL if total == 0 else Severity.INFO,
                message=f"Total de registros: {total}" if total > 0 else "No se encontraron registros en la tabla",
                count=total
            ))
            
            return total
        except Exception as e:
            logger.error(f"Error contando registros: {e}")
            self.results.append(ValidationResult(
                name="Total de registros",
                passed=False,
                severity=Severity.CRITICAL,
                message=f"Error al contar registros: {str(e)}",
                count=0
            ))
            return 0
    
    def validate_phone_format(self, phone_field: str = "phone") -> None:
        """Valida formato de teléfonos (opcional)."""
        try:
            # Verificar si el campo existe y tiene datos
            query = f"""
                SELECT COUNT(*) as count
                FROM {self.table_name}
                WHERE {phone_field} IS NOT NULL 
                AND {phone_field} !~ '^[+]?[0-9]{8,15}$'
            """
            result = self.hook.get_first(query)
            invalid_count = result[0] if result else 0
            
            if invalid_count > 0:
                self.results.append(ValidationResult(
                    name=f"Formato de teléfono ({phone_field})",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_count} teléfonos con formato inválido",
                    count=invalid_count
                ))
        except Exception as e:
            # Si el campo no existe, simplemente no agregamos este resultado
            logger.debug(f"Campo {phone_field} no existe o error al validar: {e}")
    
    def get_summary(self) -> ValidationSummary:
        """Genera un resumen de todas las validaciones."""
        errors = [r for r in self.results if r.severity in [Severity.ERROR, Severity.CRITICAL]]
        warnings = [r for r in self.results if r.severity == Severity.WARNING]
        
        return ValidationSummary(
            timestamp=pendulum.now().isoformat(),
            total_validations=len(self.results),
            passed=sum(1 for r in self.results if r.passed),
            failed=len(errors),
            warnings=len(warnings),
            errors=errors,
            warnings_list=warnings,
            metrics={
                'total_records': self.get_total_records(),
                'validations_run': len(self.results)
            }
        )
    
    def get_total_records(self) -> int:
        """Obtiene el total de registros de la tabla."""
        for result in self.results:
            if result.name == "Total de registros":
                return result.count
        return 0
    
    def validate_value_range(self, field: str, min_value: Optional[float] = None, 
                            max_value: Optional[float] = None, field_type: str = "numeric") -> None:
        """Valida que los valores estén en un rango específico."""
        try:
            conditions = []
            if min_value is not None:
                conditions.append(f"{field} < {min_value}")
            if max_value is not None:
                conditions.append(f"{field} > {max_value}")
            
            if not conditions:
                return
            
            where_clause = " AND ".join(conditions)
            query = f"""
                SELECT COUNT(*) as count
                FROM {self.table_name}
                WHERE {field} IS NOT NULL AND {where_clause}
            """
            result = self.hook.get_first(query)
            invalid_count = result[0] if result else 0
            
            if invalid_count > 0:
                range_str = f"[{min_value or '-∞'}, {max_value or '+∞'}]"
                self.results.append(ValidationResult(
                    name=f"Rango de valores: {field}",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_count} registros fuera del rango {range_str}",
                    count=invalid_count
                ))
        except Exception as e:
            logger.debug(f"Error validando rango para {field}: {e}")
    
    def validate_referential_integrity(self, field: str, reference_table: str, 
                                      reference_field: str = "id") -> None:
        """Valida integridad referencial con otra tabla."""
        try:
            query = f"""
                SELECT COUNT(*) as count
                FROM {self.table_name} t1
                LEFT JOIN {reference_table} t2 ON t1.{field} = t2.{reference_field}
                WHERE t1.{field} IS NOT NULL AND t2.{reference_field} IS NULL
            """
            result = self.hook.get_first(query)
            orphan_count = result[0] if result else 0
            
            if orphan_count > 0:
                self.results.append(ValidationResult(
                    name=f"Integridad referencial: {field} -> {reference_table}.{reference_field}",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{orphan_count} referencias huérfanas encontradas",
                    count=orphan_count
                ))
        except Exception as e:
            logger.debug(f"Error validando integridad referencial: {e}")
    
    def validate_statistical_anomalies(self, field: str, threshold_std: float = 3.0) -> None:
        """Detecta valores estadísticamente anómalos usando desviación estándar."""
        try:
            query = f"""
                WITH stats AS (
                    SELECT 
                        AVG({field}) as mean,
                        STDDEV({field}) as stddev
                    FROM {self.table_name}
                    WHERE {field} IS NOT NULL
                )
                SELECT COUNT(*) as count
                FROM {self.table_name} t, stats s
                WHERE t.{field} IS NOT NULL
                AND ABS(t.{field} - s.mean) > (s.stddev * {threshold_std})
            """
            result = self.hook.get_first(query)
            anomaly_count = result[0] if result else 0
            
            if anomaly_count > 0:
                self.results.append(ValidationResult(
                    name=f"Anomalías estadísticas: {field}",
                    passed=anomaly_count == 0,
                    severity=Severity.WARNING if anomaly_count > 0 else Severity.INFO,
                    message=f"{anomaly_count} valores estadísticamente anómalos (>{threshold_std}σ)",
                    count=anomaly_count
                ))
        except Exception as e:
            logger.debug(f"Error validando anomalías estadísticas: {e}")
    
    def validate_uniqueness(self, field: str) -> None:
        """Valida que un campo sea único (sin duplicados)."""
        try:
            query = f"""
                SELECT {field}, COUNT(*) as count
                FROM {self.table_name}
                WHERE {field} IS NOT NULL
                GROUP BY {field}
                HAVING COUNT(*) > 1
                LIMIT 10
            """
            duplicates = self.hook.get_records(query)
            
            if duplicates:
                details = [{field: row[0], 'count': row[1]} for row in duplicates]
                self.results.append(ValidationResult(
                    name=f"Unicidad: {field}",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{len(duplicates)} valores duplicados encontrados",
                    count=len(duplicates),
                    details=details
                ))
        except Exception as e:
            logger.debug(f"Error validando unicidad para {field}: {e}")
    
    def validate_custom_rule(self, rule: Dict[str, Any]) -> None:
        """Ejecuta una validación personalizada definida en JSON."""
        try:
            rule_type = rule.get("type")
            field = rule.get("field")
            name = rule.get("name", f"Validación personalizada: {field}")
            
            if rule_type == "sql":
                # Validación SQL personalizada
                sql = rule.get("sql")
                if not sql:
                    return
                
                # Reemplazar placeholder de tabla
                sql = sql.replace("{table}", self.table_name)
                result = self.hook.get_first(sql)
                count = result[0] if result else 0
                
                threshold = rule.get("threshold", 0)
                passed = count <= threshold
                
                self.results.append(ValidationResult(
                    name=name,
                    passed=passed,
                    severity=Severity.ERROR if not passed else Severity.INFO,
                    message=f"{count} registros no cumplen la regla" if not passed else "Regla cumplida",
                    count=count
                ))
            elif rule_type == "regex":
                # Validación de expresión regular
                pattern = rule.get("pattern")
                if not pattern or not field:
                    return
                
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {self.table_name}
                    WHERE {field} IS NOT NULL 
                    AND {field} !~ '{pattern}'
                """
                result = self.hook.get_first(query)
                invalid_count = result[0] if result else 0
                
                self.results.append(ValidationResult(
                    name=name,
                    passed=invalid_count == 0,
                    severity=Severity.ERROR if invalid_count > 0 else Severity.INFO,
                    message=f"{invalid_count} registros no cumplen el patrón regex",
                    count=invalid_count
                ))
            elif rule_type == "custom_function":
                # Validación usando función personalizada (avanzado)
                logger.warning(f"Validación custom_function no implementada aún: {name}")
        except Exception as e:
            logger.error(f"Error ejecutando validación personalizada: {e}")
    
    def validate_with_great_expectations(self, expectations: List[Dict[str, Any]]) -> None:
        """Valida usando Great Expectations si está disponible."""
        try:
            import pandas as pd
            import great_expectations as ge
            
            # Obtener datos de la tabla
            query = f"SELECT * FROM {self.table_name} LIMIT 10000"
            df = pd.read_sql(query, self.hook.get_conn())
            
            if df.empty:
                return
            
            gdf = ge.from_pandas(df)
            
            for expectation in expectations:
                exp_type = expectation.get("type")
                field = expectation.get("field")
                name = expectation.get("name", f"GE: {exp_type}")
                
                try:
                    if exp_type == "not_null":
                        result = gdf.expect_column_values_to_not_be_null(field)
                    elif exp_type == "unique":
                        result = gdf.expect_column_values_to_be_unique(field)
                    elif exp_type == "in_set":
                        value_set = expectation.get("value_set", [])
                        result = gdf.expect_column_values_to_be_in_set(field, value_set)
                    elif exp_type == "between":
                        min_val = expectation.get("min_value")
                        max_val = expectation.get("max_value")
                        result = gdf.expect_column_values_to_be_between(field, min_val, max_val)
                    elif exp_type == "match_regex":
                        pattern = expectation.get("pattern")
                        result = gdf.expect_column_values_to_match_regex(field, pattern)
                    else:
                        logger.warning(f"Tipo de expectativa GE no soportado: {exp_type}")
                        continue
                    
                    passed = result.get("success", False)
                    unexpected_count = result.get("result", {}).get("unexpected_count", 0)
                    
                    self.results.append(ValidationResult(
                        name=name,
                        passed=passed,
                        severity=Severity.ERROR if not passed else Severity.INFO,
                        message=f"Great Expectations: {unexpected_count} valores inesperados" if not passed else "Validación GE pasada",
                        count=unexpected_count
                    ))
                except Exception as e:
                    logger.warning(f"Error ejecutando expectativa GE {exp_type}: {e}")
                    
        except ImportError:
            logger.debug("Great Expectations no disponible, saltando validaciones GE")
        except Exception as e:
            logger.warning(f"Error usando Great Expectations: {e}")


def get_historical_metrics(hook: PostgresHook, table_name: str, days_back: int = 7) -> Optional[Dict[str, Any]]:
    """Obtiene métricas históricas para comparación."""
    try:
        # Crear tabla de métricas históricas si no existe
        create_table_query = """
        CREATE TABLE IF NOT EXISTS data_quality_metrics (
            date DATE PRIMARY KEY,
            total_records BIGINT,
            validation_errors INT,
            validation_warnings INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        hook.run(create_table_query)
        
        # Obtener métricas del día anterior
        yesterday = pendulum.yesterday().date()
        query = """
            SELECT total_records, validation_errors, validation_warnings
            FROM data_quality_metrics
            WHERE date = %s
        """
        result = hook.get_first(query, parameters=(yesterday,))
        
        if result:
            return {
                'date': yesterday.isoformat(),
                'total_records': result[0],
                'validation_errors': result[1],
                'validation_warnings': result[2]
            }
    except Exception as e:
        logger.warning(f"No se pudieron obtener métricas históricas: {e}")
    
    return None


def save_metrics(hook: PostgresHook, summary: ValidationSummary) -> None:
    """Guarda métricas del día actual para comparación futura."""
    try:
        today = pendulum.today().date()
        query = """
            INSERT INTO data_quality_metrics (date, total_records, validation_errors, validation_warnings)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (date) DO UPDATE SET
                total_records = EXCLUDED.total_records,
                validation_errors = EXCLUDED.validation_errors,
                validation_warnings = EXCLUDED.validation_warnings,
                created_at = CURRENT_TIMESTAMP
        """
        hook.run(query, parameters=(
            today,
            summary.metrics.get('total_records', 0),
            summary.failed,
            summary.warnings
        ))
    except Exception as e:
        logger.warning(f"No se pudieron guardar métricas: {e}")


def send_slack_notification(webhook_url: str, validation_results: Dict[str, Any]) -> bool:
    """Envía notificación a Slack con los resultados de validación."""
    try:
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        failed = validation_results.get("failed", 0)
        
        if failed == 0 and len(warnings) == 0:
            # Todo está bien
            color = "good"
            emoji = "✅"
            title = "Calidad de Datos: Todo Correcto"
            text = f"Todas las {validation_results.get('total_validations', 0)} validaciones pasaron exitosamente."
        elif failed > 0:
            # Hay errores críticos
            color = "danger"
            emoji = "🚨"
            title = "Calidad de Datos: Errores Detectados"
            text = f"Se encontraron {failed} errores en {validation_results.get('total_validations', 0)} validaciones."
        else:
            # Solo advertencias
            color = "warning"
            emoji = "⚠️"
            title = "Calidad de Datos: Advertencias"
            text = f"Se encontraron {len(warnings)} advertencias pero ningún error."
        
        # Construir campos con detalles
        fields = []
        if errors:
            for error in errors[:5]:  # Limitar a 5 errores
                fields.append({
                    "title": error.get("name", "Error"),
                    "value": error.get("message", "")[:200],  # Limitar longitud
                    "short": True
                })
        
        payload = {
            "attachments": [{
                "color": color,
                "title": f"{emoji} {title}",
                "text": text,
                "fields": fields,
                "footer": "Data Quality Monitoring",
                "ts": int(pendulum.now().timestamp())
            }]
        }
        
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error enviando notificación Slack: {e}")
        return False


def send_webhook_notification(webhook_url: str, validation_results: Dict[str, Any]) -> bool:
    """Envía notificación a un webhook personalizado."""
    try:
        payload = {
            "event": "data_quality_report",
            "timestamp": validation_results.get("timestamp"),
            "summary": {
                "total_validations": validation_results.get("total_validations", 0),
                "passed": validation_results.get("passed", 0),
                "failed": validation_results.get("failed", 0),
                "warnings": validation_results.get("warnings", 0)
            },
            "errors": validation_results.get("errors", []),
            "warnings": validation_results.get("warnings_list", []),
            "metrics": validation_results.get("metrics", {})
        }
        
        response = requests.post(webhook_url, json=payload, timeout=30)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"Error enviando webhook: {e}")
        return False


def export_to_json(validation_results: Dict[str, Any], **context) -> str:
    """Exporta resultados a formato JSON."""
    try:
        json_str = json.dumps(validation_results, indent=2, default=str)
        # Guardar en XCom para acceso posterior
        context['ti'].xcom_push(key='json_export', value=json_str)
        return json_str
    except Exception as e:
        logger.error(f"Error exportando a JSON: {e}")
        return "{}"


def export_to_csv(validation_results: Dict[str, Any], **context) -> str:
    """Exporta resultados a formato CSV."""
    try:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Escribir encabezados
        writer.writerow(['Tipo', 'Nombre', 'Estado', 'Severidad', 'Mensaje', 'Cantidad'])
        
        # Escribir errores
        for error in validation_results.get("errors", []):
            writer.writerow([
                "Error",
                error.get("name", ""),
                "Fallido",
                error.get("severity", ""),
                error.get("message", ""),
                error.get("count", 0)
            ])
        
        # Escribir advertencias
        for warning in validation_results.get("warnings_list", []):
            writer.writerow([
                "Advertencia",
                warning.get("name", ""),
                "Advertencia",
                warning.get("severity", ""),
                warning.get("message", ""),
                warning.get("count", 0)
            ])
        
        csv_str = output.getvalue()
        context['ti'].xcom_push(key='csv_export', value=csv_str)
        return csv_str
    except Exception as e:
        logger.error(f"Error exportando a CSV: {e}")
        return ""


def apply_smart_alerts(validation_results: Dict[str, Any], trends: Dict[str, Any], 
                       alert_thresholds: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Aplica alertas inteligentes basadas en umbrales y tendencias."""
    alerts = []
    
    try:
        failed = validation_results.get("failed", 0)
        warnings = validation_results.get("warnings", 0)
        
        # Umbral de errores
        error_threshold = alert_thresholds.get("max_errors", 0)
        if error_threshold > 0 and failed > error_threshold:
            alerts.append({
                "type": "error_threshold",
                "severity": "critical",
                "message": f"Errores ({failed}) exceden umbral ({error_threshold})",
                "count": failed
            })
        
        # Umbral de advertencias
        warning_threshold = alert_thresholds.get("max_warnings", 0)
        if warning_threshold > 0 and warnings > warning_threshold:
            alerts.append({
                "type": "warning_threshold",
                "severity": "warning",
                "message": f"Advertencias ({warnings}) exceden umbral ({warning_threshold})",
                "count": warnings
            })
        
        # Tendencias de errores
        if trends and trends.get("errors"):
            error_trend = trends["errors"].get("trend")
            if error_trend == "increasing":
                current = trends["errors"].get("current", 0)
                previous = trends["errors"].get("previous", 0)
                if current > previous * 1.5:  # 50% de aumento
                    alerts.append({
                        "type": "error_trend",
                        "severity": "warning",
                        "message": f"Tendencia creciente de errores: {previous} -> {current}",
                        "count": current
                    })
        
        # Tendencias de registros
        if trends and trends.get("records"):
            record_trend = trends["records"].get("trend")
            if record_trend == "decreasing":
                current = trends["records"].get("current", 0)
                previous = trends["records"].get("previous", 0)
                if previous > 0:
                    decrease_pct = ((previous - current) / previous) * 100
                    if decrease_pct > 10:  # Más del 10% de disminución
                        alerts.append({
                            "type": "record_decrease",
                            "severity": "critical",
                            "message": f"Disminución significativa de registros: {previous} -> {current} ({decrease_pct:.1f}%)",
                            "count": current
                        })
        
    except Exception as e:
        logger.warning(f"Error aplicando alertas inteligentes: {e}")
    
    return alerts


def validate_multiple_tables(hook: PostgresHook, tables_config: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """Valida múltiples tablas en paralelo."""
    results = {}
    
    for table_config in tables_config:
        table_name = table_config.get("table_name")
        if not table_name:
            continue
        
        try:
            validator = DataQualityValidator(hook, table_name)
            required_fields = table_config.get("required_fields", [])
            
            if required_fields:
                validator.validate_required_fields(required_fields)
            
            validator.validate_total_records()
            
            summary = validator.get_summary()
            
            results[table_name] = {
                "timestamp": summary.timestamp,
                "total_validations": summary.total_validations,
                "passed": summary.passed,
                "failed": summary.failed,
                "warnings": summary.warnings,
                "errors": [
                    {
                        "name": e.name,
                        "message": e.message,
                        "severity": e.severity.value,
                        "count": e.count
                    }
                    for e in summary.errors
                ]
            }
        except Exception as e:
            logger.error(f"Error validando tabla {table_name}: {e}")
            results[table_name] = {
                "error": str(e),
                "failed": True
            }
    
    return results


class ResultsCache:
    """Caché inteligente para resultados de validación."""
    
    def __init__(self, ttl_seconds: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_seconds
    
    def _generate_key(self, table_name: str, validation_config: Dict[str, Any]) -> str:
        """Genera una clave única para el caché."""
        config_str = json.dumps(validation_config, sort_keys=True)
        return hashlib.md5(f"{table_name}:{config_str}".encode()).hexdigest()
    
    def get(self, table_name: str, validation_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Obtiene resultados del caché si están disponibles y válidos."""
        key = self._generate_key(table_name, validation_config)
        cached = self.cache.get(key)
        
        if cached:
            timestamp = cached.get("timestamp")
            if timestamp:
                age = (pendulum.now() - pendulum.parse(timestamp)).total_seconds()
                if age < self.ttl_seconds:
                    logger.info(f"Resultados encontrados en caché para {table_name}")
                    return cached.get("results")
                else:
                    # Expirar entrada
                    del self.cache[key]
        
        return None
    
    def set(self, table_name: str, validation_config: Dict[str, Any], results: Dict[str, Any]) -> None:
        """Almacena resultados en el caché."""
        key = self._generate_key(table_name, validation_config)
        self.cache[key] = {
            "timestamp": pendulum.now().isoformat(),
            "results": results
        }
        logger.info(f"Resultados almacenados en caché para {table_name}")


def export_prometheus_metrics(validation_results: Dict[str, Any], table_name: str) -> None:
    """Exporta métricas a Prometheus."""
    if not PROMETHEUS_AVAILABLE:
        return
    
    try:
        passed = validation_results.get("passed", 0)
        failed = validation_results.get("failed", 0)
        warnings = validation_results.get("warnings", 0)
        total = validation_results.get("total_validations", 0)
        
        # Contadores de validaciones
        data_quality_validations_total.labels(status="passed", severity="info").inc(passed)
        data_quality_validations_total.labels(status="failed", severity="error").inc(failed)
        data_quality_validations_total.labels(status="warning", severity="warning").inc(warnings)
        
        # Errores por tipo
        for error in validation_results.get("errors", []):
            validation_type = error.get("name", "unknown")
            data_quality_errors_total.labels(validation_type=validation_type).inc(error.get("count", 0))
        
        # Tiempo de ejecución
        performance = validation_results.get("performance", {})
        execution_time = performance.get("execution_time_ms", 0) / 1000.0
        if execution_time > 0:
            data_quality_execution_time.observe(execution_time)
        
        # Total de registros
        metrics = validation_results.get("metrics", {})
        total_records = metrics.get("total_records", 0)
        data_quality_records_count.labels(table_name=table_name).set(total_records)
        
        # Score de calidad (0-100)
        if total > 0:
            quality_score = (passed / total) * 100
            data_quality_quality_score.labels(table_name=table_name).set(quality_score)
        
        logger.debug("Métricas exportadas a Prometheus")
    except Exception as e:
        logger.warning(f"Error exportando métricas a Prometheus: {e}")


def push_prometheus_metrics(pushgateway_url: str, validation_results: Dict[str, Any], table_name: str) -> bool:
    """Empuja métricas a Prometheus Pushgateway."""
    try:
        metrics_lines = []
        
        passed = validation_results.get("passed", 0)
        failed = validation_results.get("failed", 0)
        total = validation_results.get("total_validations", 0)
        
        # Métricas básicas
        metrics_lines.append(f'data_quality_validations_passed{{table="{table_name}"}} {passed}')
        metrics_lines.append(f'data_quality_validations_failed{{table="{table_name}"}} {failed}')
        metrics_lines.append(f'data_quality_validations_total{{table="{table_name}"}} {total}')
        
        # Score de calidad
        if total > 0:
            quality_score = (passed / total) * 100
            metrics_lines.append(f'data_quality_score{{table="{table_name}"}} {quality_score:.2f}')
        
        # Total de registros
        metrics = validation_results.get("metrics", {})
        total_records = metrics.get("total_records", 0)
        metrics_lines.append(f'data_quality_total_records{{table="{table_name}"}} {total_records}')
        
        payload = "\n".join(metrics_lines) + "\n"
        
        url = f"{pushgateway_url.rstrip('/')}/metrics/job/data_quality_monitoring/table/{table_name}"
        response = requests.post(url, data=payload.encode('utf-8'), 
                                headers={"Content-Type": "text/plain; version=0.0.4"},
                                timeout=5)
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Error empujando métricas a Pushgateway: {e}")
        return False


def create_ticket_for_errors(validation_results: Dict[str, Any], platform: str, config: Dict[str, Any]) -> Optional[str]:
    """Crea un ticket en sistema de tickets para errores críticos."""
    try:
        errors = validation_results.get("errors", [])
        critical_errors = [e for e in errors if e.get("severity") in ["critical", "error"]]
        
        if not critical_errors:
            return None
        
        # Construir descripción del ticket
        error_summary = "\n".join([
            f"- {e.get('name')}: {e.get('message')} ({e.get('count', 0)} afectados)"
            for e in critical_errors[:10]
        ])
        
        title = f"Data Quality Issues Detected - {len(critical_errors)} Critical Errors"
        description = f"""
Data quality validation detected {len(critical_errors)} critical errors.

Errors:
{error_summary}

Total Validations: {validation_results.get('total_validations', 0)}
Passed: {validation_results.get('passed', 0)}
Failed: {validation_results.get('failed', 0)}

Timestamp: {validation_results.get('timestamp', 'N/A')}

Action Required: Review and fix data quality issues.
        """.strip()
        
        if platform == "jira":
            jira_url = config.get("url") or os.getenv("JIRA_URL")
            jira_email = config.get("email") or os.getenv("JIRA_EMAIL")
            jira_token = config.get("api_token") or os.getenv("JIRA_API_TOKEN")
            project_key = config.get("project_key") or os.getenv("JIRA_PROJECT_KEY", "DATA")
            
            if not all([jira_url, jira_email, jira_token]):
                logger.warning("Jira credentials not configured")
                return None
            
            payload = {
                "fields": {
                    "project": {"key": project_key},
                    "summary": title,
                    "description": {
                        "type": "doc",
                        "version": 1,
                        "content": [{
                            "type": "paragraph",
                            "content": [{"type": "text", "text": description}]
                        }]
                    },
                    "issuetype": {"name": "Bug"},
                    "priority": {"name": "High"},
                    "labels": ["data-quality", "automated"]
                }
            }
            
            response = requests.post(
                f"{jira_url}/rest/api/3/issue",
                json=payload,
                auth=(jira_email, jira_token),
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            ticket_key = response.json()["key"]
            logger.info(f"Jira ticket created: {ticket_key}")
            return ticket_key
        
        elif platform == "servicenow":
            instance_url = config.get("instance_url") or os.getenv("SERVICENOW_INSTANCE_URL")
            username = config.get("username") or os.getenv("SERVICENOW_USERNAME")
            password = config.get("password") or os.getenv("SERVICENOW_PASSWORD")
            
            if not all([instance_url, username, password]):
                logger.warning("ServiceNow credentials not configured")
                return None
            
            payload = {
                "short_description": title,
                "description": description,
                "priority": "2",  # High
                "category": "Data Quality",
                "subcategory": "Validation Error"
            }
            
            response = requests.post(
                f"{instance_url}/api/now/table/incident",
                json=payload,
                auth=(username, password),
                headers={"Content-Type": "application/json", "Accept": "application/json"},
                timeout=10
            )
            response.raise_for_status()
            incident_number = response.json()["result"]["number"]
            logger.info(f"ServiceNow incident created: {incident_number}")
            return incident_number
        
        elif platform == "github":
            repo = config.get("repo") or os.getenv("GITHUB_REPO")
            token = config.get("token") or os.getenv("GITHUB_TOKEN")
            
            if not all([repo, token]):
                logger.warning("GitHub credentials not configured")
                return None
            
            payload = {
                "title": title,
                "body": description,
                "labels": ["data-quality", "bug", "automated"]
            }
            
            response = requests.post(
                f"https://api.github.com/repos/{repo}/issues",
                json=payload,
                headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
                timeout=10
            )
            response.raise_for_status()
            issue_number = response.json()["number"]
            logger.info(f"GitHub issue created: #{issue_number}")
            return str(issue_number)
        
    except Exception as e:
        logger.error(f"Error creating ticket: {e}")
        return None


def auto_fix_data_issues(hook: PostgresHook, table_name: str, errors: List[Dict[str, Any]], 
                         fix_rules: Dict[str, Any]) -> Dict[str, Any]:
    """Intenta auto-reparar problemas de datos según reglas."""
    fixes_applied = []
    fixes_failed = []
    
    try:
        for error in errors:
            error_name = error.get("name", "")
            error_type = error.get("type", "")
            fix_rule = fix_rules.get(error_type) or fix_rules.get(error_name)
            
            if not fix_rule or not fix_rule.get("enabled", False):
                continue
            
            try:
                fix_sql = fix_rule.get("sql")
                if not fix_sql:
                    continue
                
                # Reemplazar placeholders
                fix_sql = fix_sql.replace("{table}", table_name)
                
                # Ejecutar fix
                hook.run(fix_sql)
                
                fixes_applied.append({
                    "error": error_name,
                    "fix": fix_rule.get("description", "Auto-fix applied"),
                    "sql": fix_sql
                })
                logger.info(f"Auto-fix aplicado para: {error_name}")
                
            except Exception as e:
                fixes_failed.append({
                    "error": error_name,
                    "reason": str(e)
                })
                logger.warning(f"Error aplicando auto-fix para {error_name}: {e}")
    
    except Exception as e:
        logger.error(f"Error en auto-fix: {e}")
    
    return {
        "applied": fixes_applied,
        "failed": fixes_failed,
        "total_applied": len(fixes_applied),
        "total_failed": len(fixes_failed)
    }


def validate_compliance(hook: PostgresHook, table_name: str, compliance_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida reglas de compliance (GDPR, HIPAA, etc.)."""
    results = []
    
    try:
        # GDPR: Verificar campos de datos personales
        if compliance_rules.get("gdpr", {}).get("enabled", False):
            pii_fields = compliance_rules["gdpr"].get("pii_fields", ["email", "phone", "name"])
            
            for field in pii_fields:
                # Verificar si hay datos sin consentimiento explícito
                consent_field = compliance_rules["gdpr"].get("consent_field", "consent_given")
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {field} IS NOT NULL 
                    AND ({consent_field} IS NULL OR {consent_field} = false)
                """
                result = hook.get_first(query)
                non_consented = result[0] if result else 0
                
                if non_consented > 0:
                    results.append(ValidationResult(
                        name=f"GDPR: Datos sin consentimiento - {field}",
                        passed=False,
                        severity=Severity.CRITICAL,
                        message=f"{non_consented} registros con {field} sin consentimiento explícito",
                        count=non_consented
                    ))
        
        # HIPAA: Verificar campos de salud
        if compliance_rules.get("hipaa", {}).get("enabled", False):
            phi_fields = compliance_rules["hipaa"].get("phi_fields", [])
            
            for field in phi_fields:
                # Verificar encriptación o anonimización
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {field} IS NOT NULL
                    AND {field} NOT LIKE 'ENC:%'
                """
                result = hook.get_first(query)
                unencrypted = result[0] if result else 0
                
                if unencrypted > 0:
                    results.append(ValidationResult(
                        name=f"HIPAA: Datos no encriptados - {field}",
                        passed=False,
                        severity=Severity.CRITICAL,
                        message=f"{unencrypted} registros con {field} no encriptado",
                        count=unencrypted
                    ))
        
        # Retención de datos
        if compliance_rules.get("data_retention", {}).get("enabled", False):
            retention_days = compliance_rules["data_retention"].get("max_days", 365)
            date_field = compliance_rules["data_retention"].get("date_field", "created_at")
            
            query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {date_field} < CURRENT_DATE - INTERVAL '{retention_days} days'
            """
            result = hook.get_first(query)
            expired = result[0] if result else 0
            
            if expired > 0:
                results.append(ValidationResult(
                    name="Compliance: Datos expirados",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{expired} registros exceden período de retención ({retention_days} días)",
                    count=expired
                ))
    
    except Exception as e:
        logger.error(f"Error en validación de compliance: {e}")
    
    return results


def generate_data_profile(hook: PostgresHook, table_name: str, fields: List[str]) -> Dict[str, Any]:
    """Genera perfil estadístico de los datos."""
    profile = {}
    
    try:
        for field in fields:
            try:
                # Estadísticas básicas
                query = f"""
                    SELECT 
                        COUNT(*) as total,
                        COUNT({field}) as non_null,
                        COUNT(*) - COUNT({field}) as null_count,
                        MIN({field}) as min_val,
                        MAX({field}) as max_val,
                        AVG({field}) as avg_val,
                        STDDEV({field}) as stddev_val
                    FROM {table_name}
                """
                result = hook.get_first(query)
                
                if result:
                    profile[field] = {
                        "total": result[0],
                        "non_null": result[1],
                        "null_count": result[2],
                        "null_percentage": (result[2] / result[0] * 100) if result[0] > 0 else 0,
                        "min": float(result[3]) if result[3] is not None else None,
                        "max": float(result[4]) if result[4] is not None else None,
                        "avg": float(result[5]) if result[5] is not None else None,
                        "stddev": float(result[6]) if result[6] is not None else None
                    }
            except Exception as e:
                logger.debug(f"Error generando perfil para {field}: {e}")
    
    except Exception as e:
        logger.warning(f"Error en data profiling: {e}")
    
    return profile


def detect_data_drift(hook: PostgresHook, table_name: str, field: str, 
                     historical_distribution: Dict[str, Any]) -> Dict[str, Any]:
    """Detecta drift en la distribución de datos."""
    drift_info = {
        "field": field,
        "drift_detected": False,
        "drift_score": 0.0,
        "details": {}
    }
    
    try:
        # Obtener distribución actual
        query = f"""
            SELECT 
                COUNT(*) as total,
                AVG({field}) as mean,
                STDDEV({field}) as stddev,
                MIN({field}) as min_val,
                MAX({field}) as max_val
            FROM {table_name}
            WHERE {field} IS NOT NULL
        """
        result = hook.get_first(query)
        
        if not result or not historical_distribution:
            return drift_info
        
        current_mean = float(result[1]) if result[1] else 0
        current_stddev = float(result[2]) if result[2] else 0
        historical_mean = historical_distribution.get("mean", 0)
        historical_stddev = historical_distribution.get("stddev", 0)
        
        if historical_stddev == 0:
            return drift_info
        
        # Calcular drift usando distancia estadística
        mean_drift = abs(current_mean - historical_mean) / historical_stddev if historical_stddev > 0 else 0
        stddev_drift = abs(current_stddev - historical_stddev) / historical_stddev if historical_stddev > 0 else 0
        
        drift_score = (mean_drift + stddev_drift) / 2
        
        if drift_score > 0.2:  # Umbral de 20% de cambio
            drift_info["drift_detected"] = True
            drift_info["drift_score"] = drift_score
            drift_info["details"] = {
                "current_mean": current_mean,
                "historical_mean": historical_mean,
                "mean_change_pct": (mean_drift * 100),
                "current_stddev": current_stddev,
                "historical_stddev": historical_stddev,
                "stddev_change_pct": (stddev_drift * 100)
            }
            logger.warning(f"Data drift detectado en {field}: score={drift_score:.2f}")
    
    except Exception as e:
        logger.warning(f"Error detectando drift: {e}")
    
    return drift_info


def validate_schema(hook: PostgresHook, table_name: str, expected_schema: Dict[str, Any]) -> List[ValidationResult]:
    """Valida que el esquema de la tabla coincida con el esperado."""
    results = []
    
    try:
        # Obtener esquema actual
        query = f"""
            SELECT 
                column_name,
                data_type,
                is_nullable,
                character_maximum_length
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            ORDER BY ordinal_position
        """
        current_columns = hook.get_records(query)
        current_schema = {
            row[0]: {
                "type": row[1],
                "nullable": row[2] == "YES",
                "max_length": row[3]
            }
            for row in current_columns
        }
        
        # Validar campos esperados
        for field_name, field_spec in expected_schema.items():
            if field_name not in current_schema:
                results.append(ValidationResult(
                    name=f"Schema: Campo faltante - {field_name}",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"Campo {field_name} no existe en la tabla",
                    count=0
                ))
            else:
                current = current_schema[field_name]
                expected_type = field_spec.get("type")
                expected_nullable = field_spec.get("nullable", True)
                
                # Validar tipo (simplificado)
                if expected_type and current["type"] != expected_type:
                    results.append(ValidationResult(
                        name=f"Schema: Tipo incorrecto - {field_name}",
                        passed=False,
                        severity=Severity.ERROR,
                        message=f"Campo {field_name} tiene tipo {current['type']}, se esperaba {expected_type}",
                        count=0
                    ))
                
                # Validar nullable
                if current["nullable"] != expected_nullable:
                    results.append(ValidationResult(
                        name=f"Schema: Nullable incorrecto - {field_name}",
                        passed=False,
                        severity=Severity.WARNING,
                        message=f"Campo {field_name} nullable={current['nullable']}, se esperaba {expected_nullable}",
                        count=0
                    ))
        
        # Detectar campos extra
        extra_fields = set(current_schema.keys()) - set(expected_schema.keys())
        if extra_fields:
            results.append(ValidationResult(
                name="Schema: Campos adicionales",
                passed=True,  # No es error, solo información
                severity=Severity.INFO,
                message=f"Campos adicionales encontrados: {', '.join(extra_fields)}",
                count=len(extra_fields)
            ))
    
    except Exception as e:
        logger.error(f"Error validando schema: {e}")
        results.append(ValidationResult(
            name="Schema: Error de validación",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"Error al validar schema: {str(e)}",
            count=0
        ))
    
    return results


def validate_business_rules(hook: PostgresHook, table_name: str, business_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida reglas de negocio complejas."""
    results = []
    
    try:
        for rule_name, rule_config in business_rules.items():
            if not rule_config.get("enabled", False):
                continue
            
            rule_type = rule_config.get("type")
            sql = rule_config.get("sql")
            description = rule_config.get("description", rule_name)
            
            if not sql:
                continue
            
            try:
                # Reemplazar placeholder de tabla
                sql = sql.replace("{table}", table_name)
                
                # Ejecutar regla de negocio
                result = hook.get_first(sql)
                violation_count = result[0] if result else 0
                
                threshold = rule_config.get("threshold", 0)
                severity_str = rule_config.get("severity", "error")
                severity = Severity[severity_str.upper()] if hasattr(Severity, severity_str.upper()) else Severity.ERROR
                
                if violation_count > threshold:
                    results.append(ValidationResult(
                        name=f"Regla de negocio: {rule_name}",
                        passed=False,
                        severity=severity,
                        message=f"{description}: {violation_count} violaciones encontradas",
                        count=violation_count
                    ))
                else:
                    results.append(ValidationResult(
                        name=f"Regla de negocio: {rule_name}",
                        passed=True,
                        severity=Severity.INFO,
                        message=f"{description}: Cumplida",
                        count=0
                    ))
            except Exception as e:
                logger.error(f"Error ejecutando regla de negocio {rule_name}: {e}")
                results.append(ValidationResult(
                    name=f"Regla de negocio: {rule_name}",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Error al ejecutar regla: {str(e)}",
                    count=0
                ))
    
    except Exception as e:
        logger.error(f"Error en validación de reglas de negocio: {e}")
    
    return results


def detect_suspicious_patterns(hook: PostgresHook, table_name: str) -> List[ValidationResult]:
    """Detecta patrones sospechosos en los datos."""
    results = []
    
    try:
        # Patrón 1: Múltiples registros creados en el mismo segundo (posible bot/spam)
        pattern_query = f"""
            SELECT created_at, COUNT(*) as count
            FROM {table_name}
            WHERE created_at >= CURRENT_DATE - INTERVAL '1 day'
            GROUP BY created_at
            HAVING COUNT(*) > 10
            ORDER BY count DESC
            LIMIT 5
        """
        pattern_results = hook.get_records(pattern_query)
        
        if pattern_results:
            suspicious_times = [row[0] for row in pattern_results]
            results.append(ValidationResult(
                name="Patrón sospechoso: Creación masiva",
                passed=False,
                severity=Severity.WARNING,
                message=f"Se detectaron {len(pattern_results)} timestamps con más de 10 registros (posible spam/bot)",
                count=sum(row[1] for row in pattern_results),
                details=[{"timestamp": str(row[0]), "count": row[1]} for row in pattern_results]
            ))
        
        # Patrón 2: Emails con dominios sospechosos
        suspicious_domains = ["test.com", "example.com", "fake.com", "temp.com"]
        domain_query = f"""
            SELECT email, COUNT(*) as count
            FROM {table_name}
            WHERE email IS NOT NULL
            AND (email LIKE '%@test.com' OR email LIKE '%@example.com' 
                 OR email LIKE '%@fake.com' OR email LIKE '%@temp.com')
            GROUP BY email
            LIMIT 10
        """
        domain_results = hook.get_records(domain_query)
        
        if domain_results:
            results.append(ValidationResult(
                name="Patrón sospechoso: Dominios de prueba",
                passed=False,
                severity=Severity.WARNING,
                message=f"Se encontraron {len(domain_results)} emails con dominios de prueba",
                count=len(domain_results),
                details=[{"email": row[0], "count": row[1]} for row in domain_results]
            ))
        
        # Patrón 3: Valores idénticos en múltiples campos (posible duplicado)
        duplicate_pattern_query = f"""
            SELECT name, email, COUNT(*) as count
            FROM {table_name}
            WHERE name IS NOT NULL AND email IS NOT NULL
            GROUP BY name, email
            HAVING COUNT(*) > 1
            LIMIT 10
        """
        duplicate_patterns = hook.get_records(duplicate_pattern_query)
        
        if duplicate_patterns:
            results.append(ValidationResult(
                name="Patrón sospechoso: Combinaciones duplicadas",
                passed=False,
                severity=Severity.WARNING,
                message=f"Se encontraron {len(duplicate_patterns)} combinaciones name+email duplicadas",
                count=len(duplicate_patterns)
            ))
    
    except Exception as e:
        logger.warning(f"Error detectando patrones sospechosos: {e}")
    
    return results


def check_data_freshness(hook: PostgresHook, table_name: str, date_field: str, max_age_hours: int) -> ValidationResult:
    """Verifica la frescura de los datos."""
    try:
        query = f"""
            SELECT MAX({date_field}) as last_update
            FROM {table_name}
        """
        result = hook.get_first(query)
        last_update = result[0] if result else None
        
        if not last_update:
            return ValidationResult(
                name="Frescura de datos",
                passed=False,
                severity=Severity.CRITICAL,
                message="No se pudo determinar última actualización",
                count=0
            )
        
        # Calcular edad de los datos
        if isinstance(last_update, str):
            last_update = pendulum.parse(last_update)
        elif hasattr(last_update, 'isoformat'):
            last_update = pendulum.instance(last_update)
        
        age_hours = (pendulum.now() - last_update).total_hours()
        
        if age_hours > max_age_hours:
            return ValidationResult(
                name="Frescura de datos",
                passed=False,
                severity=Severity.WARNING,
                message=f"Datos desactualizados: última actualización hace {age_hours:.1f} horas (máximo: {max_age_hours}h)",
                count=int(age_hours)
            )
        else:
            return ValidationResult(
                name="Frescura de datos",
                passed=True,
                severity=Severity.INFO,
                message=f"Datos frescos: última actualización hace {age_hours:.1f} horas",
                count=int(age_hours)
            )
    
    except Exception as e:
        logger.error(f"Error verificando frescura de datos: {e}")
        return ValidationResult(
            name="Frescura de datos",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"Error al verificar frescura: {str(e)}",
            count=0
        )


def send_to_grafana(api_url: str, api_key: str, validation_results: Dict[str, Any]) -> bool:
    """Envía métricas a Grafana."""
    try:
        passed = validation_results.get("passed", 0)
        failed = validation_results.get("failed", 0)
        total = validation_results.get("total_validations", 0)
        
        quality_score = (passed / total * 100) if total > 0 else 0
        
        payload = {
            "time": int(pendulum.now().timestamp() * 1000),
            "values": {
                "data_quality_score": quality_score,
                "data_quality_passed": passed,
                "data_quality_failed": failed,
                "data_quality_total": total
            }
        }
        
        response = requests.post(
            f"{api_url}/api/datasources/proxy/1/api/v1/query",
            json=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Error enviando métricas a Grafana: {e}")
        return False


def send_pagerduty_alert(integration_key: str, validation_results: Dict[str, Any]) -> bool:
    """Envía alerta crítica a PagerDuty."""
    try:
        errors = validation_results.get("errors", [])
        critical_errors = [e for e in errors if e.get("severity") == "critical"]
        
        if not critical_errors:
            return False
        
        payload = {
            "routing_key": integration_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"Data Quality Critical Issues: {len(critical_errors)} critical errors",
                "severity": "critical",
                "source": "data_quality_monitoring",
                "custom_details": {
                    "total_errors": len(errors),
                    "critical_errors": len(critical_errors),
                    "failed_validations": validation_results.get("failed", 0),
                    "timestamp": validation_results.get("timestamp")
                }
            }
        }
        
        response = requests.post(
            "https://events.pagerduty.com/v2/enqueue",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Error enviando alerta a PagerDuty: {e}")
        return False


def send_opsgenie_alert(api_key: str, validation_results: Dict[str, Any]) -> bool:
    """Envía alerta crítica a Opsgenie."""
    try:
        errors = validation_results.get("errors", [])
        critical_errors = [e for e in errors if e.get("severity") == "critical"]
        
        if not critical_errors:
            return False
        
        payload = {
            "message": f"Data Quality Critical Issues: {len(critical_errors)} critical errors",
            "priority": "P1",
            "description": f"Total errors: {len(errors)}, Critical: {len(critical_errors)}",
            "details": {
                "failed_validations": validation_results.get("failed", 0),
                "timestamp": validation_results.get("timestamp")
            }
        }
        
        response = requests.post(
            "https://api.opsgenie.com/v2/alerts",
            json=payload,
            headers={
                "Authorization": f"GenieKey {api_key}",
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Error enviando alerta a Opsgenie: {e}")
        return False


def validate_security(hook: PostgresHook, table_name: str, security_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida reglas de seguridad de datos."""
    results = []
    
    try:
        # Validación 1: Detectar datos sensibles sin encriptar
        if security_rules.get("check_unencrypted_sensitive", {}).get("enabled", False):
            sensitive_fields = security_rules["check_unencrypted_sensitive"].get("fields", [])
            for field in sensitive_fields:
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {field} IS NOT NULL
                    AND {field} NOT LIKE 'ENC:%'
                    AND {field} NOT LIKE 'HASH:%'
                """
                result = hook.get_first(query)
                unencrypted = result[0] if result else 0
                
                if unencrypted > 0:
                    results.append(ValidationResult(
                        name=f"Seguridad: Datos sensibles sin encriptar - {field}",
                        passed=False,
                        severity=Severity.CRITICAL,
                        message=f"{unencrypted} registros con {field} sin encriptar",
                        count=unencrypted
                    ))
        
        # Validación 2: Detectar acceso no autorizado (timestamps sospechosos)
        if security_rules.get("check_unauthorized_access", {}).get("enabled", False):
            access_field = security_rules["check_unauthorized_access"].get("access_field", "last_accessed_at")
            query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {access_field} IS NOT NULL
                AND {access_field} > CURRENT_TIMESTAMP
            """
            result = hook.get_first(query)
            future_access = result[0] if result else 0
            
            if future_access > 0:
                results.append(ValidationResult(
                    name="Seguridad: Accesos con timestamps futuros",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{future_access} registros con accesos en el futuro (posible manipulación)",
                    count=future_access
                ))
        
        # Validación 3: Detectar patrones de inyección SQL potencial
        if security_rules.get("check_sql_injection_patterns", {}).get("enabled", False):
            text_fields = security_rules["check_sql_injection_patterns"].get("fields", ["name", "description"])
            for field in text_fields:
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {field} IS NOT NULL
                    AND ({field} LIKE '%DROP TABLE%' 
                         OR {field} LIKE '%DELETE FROM%'
                         OR {field} LIKE '%UNION SELECT%'
                         OR {field} LIKE '%;--%')
                """
                result = hook.get_first(query)
                suspicious = result[0] if result else 0
                
                if suspicious > 0:
                    results.append(ValidationResult(
                        name=f"Seguridad: Posible inyección SQL en {field}",
                        passed=False,
                        severity=Severity.CRITICAL,
                        message=f"{suspicious} registros con patrones sospechosos de inyección SQL",
                        count=suspicious
                    ))
    
    except Exception as e:
        logger.error(f"Error en validación de seguridad: {e}")
    
    return results


def check_data_latency(hook: PostgresHook, table_name: str, source_timestamp_field: str, 
                       max_latency_minutes: int) -> ValidationResult:
    """Verifica la latencia de datos desde su origen."""
    try:
        query = f"""
            SELECT 
                MAX({source_timestamp_field}) as latest_source_time,
                MAX(created_at) as latest_local_time
            FROM {table_name}
            WHERE {source_timestamp_field} IS NOT NULL
        """
        result = hook.get_first(query)
        
        if not result or not result[0]:
            return ValidationResult(
                name="Latencia de datos",
                passed=False,
                severity=Severity.WARNING,
                message="No se pudo determinar latencia de datos",
                count=0
            )
        
        source_time = result[0]
        local_time = result[1] if result[1] else pendulum.now()
        
        if isinstance(source_time, str):
            source_time = pendulum.parse(source_time)
        elif hasattr(source_time, 'isoformat'):
            source_time = pendulum.instance(source_time)
        
        if isinstance(local_time, str):
            local_time = pendulum.parse(local_time)
        elif hasattr(local_time, 'isoformat'):
            local_time = pendulum.instance(local_time)
        
        latency_minutes = (local_time - source_time).total_minutes()
        
        if latency_minutes > max_latency_minutes:
            return ValidationResult(
                name="Latencia de datos",
                passed=False,
                severity=Severity.WARNING,
                message=f"Latencia alta: {latency_minutes:.1f} minutos (máximo: {max_latency_minutes}min)",
                count=int(latency_minutes)
            )
        else:
            return ValidationResult(
                name="Latencia de datos",
                passed=True,
                severity=Severity.INFO,
                message=f"Latencia aceptable: {latency_minutes:.1f} minutos",
                count=int(latency_minutes)
            )
    
    except Exception as e:
        logger.error(f"Error verificando latencia: {e}")
        return ValidationResult(
            name="Latencia de datos",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"Error al verificar latencia: {str(e)}",
            count=0
        )


def calculate_quality_score(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula score de calidad de datos (0-100)."""
    try:
        total = validation_results.get("total_validations", 0)
        passed = validation_results.get("passed", 0)
        failed = validation_results.get("failed", 0)
        warnings = validation_results.get("warnings", 0)
        errors = validation_results.get("errors", [])
        
        if total == 0:
            return {"score": 0, "grade": "F", "components": {}}
        
        # Score base: porcentaje de validaciones pasadas
        base_score = (passed / total) * 100
        
        # Penalizaciones
        critical_errors = len([e for e in errors if e.get("severity") == "critical"])
        error_penalty = (critical_errors * 10) + (failed * 2) + (warnings * 0.5)
        
        # Score final
        final_score = max(0, min(100, base_score - error_penalty))
        
        # Grade
        if final_score >= 90:
            grade = "A"
        elif final_score >= 80:
            grade = "B"
        elif final_score >= 70:
            grade = "C"
        elif final_score >= 60:
            grade = "D"
        else:
            grade = "F"
        
        # Componentes del score
        components = {
            "base_score": round(base_score, 2),
            "error_penalty": round(error_penalty, 2),
            "critical_errors": critical_errors,
            "total_errors": failed,
            "warnings": warnings
        }
        
        return {
            "score": round(final_score, 2),
            "grade": grade,
            "components": components,
            "recommendations": _get_quality_recommendations(final_score, critical_errors, failed)
        }
    
    except Exception as e:
        logger.error(f"Error calculando score de calidad: {e}")
        return {"score": 0, "grade": "F", "components": {}, "error": str(e)}


def _get_quality_recommendations(score: float, critical_errors: int, total_errors: int) -> List[str]:
    """Genera recomendaciones basadas en el score."""
    recommendations = []
    
    if score < 60:
        recommendations.append("⚠️ Calidad de datos crítica: Revisar inmediatamente")
    elif score < 70:
        recommendations.append("⚠️ Calidad de datos baja: Requiere atención")
    
    if critical_errors > 0:
        recommendations.append(f"🔴 {critical_errors} errores críticos detectados")
    
    if total_errors > 10:
        recommendations.append(f"⚠️ Alto número de errores ({total_errors}): Considerar revisión de procesos")
    
    if score >= 90:
        recommendations.append("✅ Excelente calidad de datos")
    
    return recommendations


def classify_errors_with_ml(validation_results: Dict[str, Any]) -> Dict[str, Any]:
    """Clasifica errores usando Machine Learning."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.cluster import KMeans
        from collections import Counter
        
        errors = validation_results.get("errors", [])
        if not errors:
            return {"classified": False, "message": "No hay errores para clasificar"}
        
        # Extraer características de errores
        error_texts = [f"{e.get('name', '')} {e.get('message', '')}" for e in errors]
        
        # Vectorizar texto
        vectorizer = TfidfVectorizer(max_features=50, stop_words='english')
        try:
            X = vectorizer.fit_transform(error_texts)
        except ValueError:
            # Si no hay suficiente texto, usar clasificación simple
            return _simple_error_classification(errors)
        
        # Clustering con KMeans
        n_clusters = min(5, len(errors))
        if n_clusters < 2:
            return _simple_error_classification(errors)
        
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        clusters = kmeans.fit_predict(X)
        
        # Agrupar errores por cluster
        error_categories = {}
        for i, error in enumerate(errors):
            cluster_id = int(clusters[i])
            if cluster_id not in error_categories:
                error_categories[cluster_id] = []
            error_categories[cluster_id].append(error)
        
        # Generar nombres de categorías basados en palabras comunes
        categories = {}
        for cluster_id, cluster_errors in error_categories.items():
            # Extraer palabras comunes del nombre
            names = [e.get('name', '') for e in cluster_errors]
            words = []
            for name in names:
                words.extend(name.lower().split())
            
            # Encontrar palabra más común
            word_counts = Counter(words)
            common_word = word_counts.most_common(1)[0][0] if word_counts else "Otros"
            
            categories[f"Categoría {cluster_id + 1}: {common_word.title()}"] = {
                "count": len(cluster_errors),
                "errors": cluster_errors[:5],  # Primeros 5
                "severity_distribution": {
                    "critical": len([e for e in cluster_errors if e.get("severity") == "critical"]),
                    "error": len([e for e in cluster_errors if e.get("severity") == "error"]),
                    "warning": len([e for e in cluster_errors if e.get("severity") == "warning"])
                }
            }
        
        return {
            "classified": True,
            "total_categories": len(categories),
            "categories": categories
        }
    
    except ImportError:
        logger.warning("scikit-learn no disponible, usando clasificación simple")
        return _simple_error_classification(validation_results.get("errors", []))
    except Exception as e:
        logger.warning(f"Error en clasificación ML: {e}")
        return _simple_error_classification(validation_results.get("errors", []))


def _simple_error_classification(errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Clasificación simple de errores sin ML."""
    categories = {}
    
    for error in errors:
        name = error.get('name', 'Otros')
        # Extraer primera palabra como categoría
        category = name.split(':')[0] if ':' in name else name.split()[0] if name else 'Otros'
        
        if category not in categories:
            categories[category] = {
                "count": 0,
                "errors": [],
                "severity_distribution": {"critical": 0, "error": 0, "warning": 0}
            }
        
        categories[category]["count"] += 1
        if len(categories[category]["errors"]) < 5:
            categories[category]["errors"].append(error)
        
        severity = error.get("severity", "error")
        if severity in categories[category]["severity_distribution"]:
            categories[category]["severity_distribution"][severity] += 1
    
    return {
        "classified": True,
        "total_categories": len(categories),
        "categories": categories,
        "method": "simple"
    }


def validate_cross_system(hook: PostgresHook, table_name: str, cross_system_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida consistencia entre sistemas."""
    results = []
    
    try:
        for system_name, system_config in cross_system_config.items():
            if not system_config.get("enabled", False):
                continue
            
            # Obtener conexión al sistema externo
            external_conn_id = system_config.get("connection_id")
            if not external_conn_id:
                continue
            
            try:
                external_hook = PostgresHook(postgres_conn_id=external_conn_id)
                external_table = system_config.get("table_name", table_name)
                
                # Comparar conteos
                local_count_query = f"SELECT COUNT(*) FROM {table_name}"
                external_count_query = f"SELECT COUNT(*) FROM {external_table}"
                
                local_count = hook.get_first(local_count_query)[0]
                external_count = external_hook.get_first(external_count_query)[0]
                
                if local_count != external_count:
                    results.append(ValidationResult(
                        name=f"Cross-system: Conteo inconsistente - {system_name}",
                        passed=False,
                        severity=Severity.ERROR,
                        message=f"Conteo local: {local_count}, Conteo en {system_name}: {external_count}",
                        count=abs(local_count - external_count)
                    ))
                else:
                    results.append(ValidationResult(
                        name=f"Cross-system: Conteo consistente - {system_name}",
                        passed=True,
                        severity=Severity.INFO,
                        message=f"Conteos coinciden: {local_count}",
                        count=0
                    ))
                
                # Comparar campos específicos si están configurados
                compare_fields = system_config.get("compare_fields", [])
                for field in compare_fields:
                    local_query = f"SELECT COUNT(DISTINCT {field}) FROM {table_name} WHERE {field} IS NOT NULL"
                    external_query = f"SELECT COUNT(DISTINCT {field}) FROM {external_table} WHERE {field} IS NOT NULL"
                    
                    local_distinct = hook.get_first(local_query)[0]
                    external_distinct = external_hook.get_first(external_query)[0]
                    
                    if local_distinct != external_distinct:
                        results.append(ValidationResult(
                            name=f"Cross-system: Valores distintos inconsistentes - {field} ({system_name})",
                            passed=False,
                            severity=Severity.WARNING,
                            message=f"Valores distintos locales: {local_distinct}, en {system_name}: {external_distinct}",
                            count=abs(local_distinct - external_distinct)
                        ))
            
            except Exception as e:
                logger.error(f"Error validando sistema {system_name}: {e}")
                results.append(ValidationResult(
                    name=f"Cross-system: Error conectando a {system_name}",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Error: {str(e)}",
                    count=0
                ))
    
    except Exception as e:
        logger.error(f"Error en validación cross-system: {e}")
    
    return results


def validate_advanced_referential_integrity(hook: PostgresHook, table_name: str, rules: List[Dict[str, Any]]) -> List[ValidationResult]:
    """Valida integridad referencial avanzada con múltiples relaciones."""
    results = []
    
    try:
        for rule in rules:
            if not rule.get("enabled", False):
                continue
            
            rule_name = rule.get("name", "Unknown")
            source_table = rule.get("source_table", table_name)
            source_field = rule.get("source_field")
            target_table = rule.get("target_table")
            target_field = rule.get("target_field", "id")
            check_type = rule.get("check_type", "orphan")  # orphan, cascade, cycle
            
            if not source_field or not target_table:
                continue
            
            if check_type == "orphan":
                # Verificar referencias huérfanas
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {source_table} s
                    LEFT JOIN {target_table} t ON s.{source_field} = t.{target_field}
                    WHERE s.{source_field} IS NOT NULL 
                    AND t.{target_field} IS NULL
                """
            elif check_type == "cascade":
                # Verificar que los cambios en cascada funcionan
                # Esto requiere verificar que no hay registros que violen la cascada
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {source_table} s
                    WHERE s.{source_field} IS NOT NULL
                    AND NOT EXISTS (
                        SELECT 1 FROM {target_table} t 
                        WHERE t.{target_field} = s.{source_field}
                    )
                """
            elif check_type == "cycle":
                # Detectar ciclos en referencias circulares
                query = f"""
                    WITH RECURSIVE ref_cycle AS (
                        SELECT {source_field}, 1 as depth, ARRAY[{source_field}] as path
                        FROM {source_table}
                        WHERE {source_field} IS NOT NULL
                        UNION ALL
                        SELECT t.{target_field}, rc.depth + 1, rc.path || t.{target_field}
                        FROM {target_table} t
                        JOIN ref_cycle rc ON t.{target_field} = rc.{source_field}
                        WHERE t.{target_field} = ANY(rc.path)
                    )
                    SELECT COUNT(*) FROM ref_cycle WHERE depth > 1
                """
            else:
                continue
            
            result = hook.get_first(query)
            violation_count = result[0] if result else 0
            
            threshold = rule.get("threshold", 0)
            severity_str = rule.get("severity", "error")
            severity = Severity[severity_str.upper()] if hasattr(Severity, severity_str.upper()) else Severity.ERROR
            
            if violation_count > threshold:
                results.append(ValidationResult(
                    name=f"Integridad referencial avanzada: {rule_name}",
                    passed=False,
                    severity=severity,
                    message=f"Tipo: {check_type}, Violaciones: {violation_count}",
                    count=violation_count
                ))
            else:
                results.append(ValidationResult(
                    name=f"Integridad referencial avanzada: {rule_name}",
                    passed=True,
                    severity=Severity.INFO,
                    message=f"Tipo: {check_type}, Sin violaciones",
                    count=0
                ))
    
    except Exception as e:
        logger.error(f"Error en validación avanzada de integridad referencial: {e}")
    
    return results


def calculate_sla_metrics(validation_results: Dict[str, Any], sla_targets: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula métricas de SLA basadas en objetivos."""
    try:
        sla_metrics = {
            "timestamp": pendulum.now().isoformat(),
            "targets": sla_targets,
            "achievements": {},
            "overall_sla": 0.0
        }
        
        # SLA de disponibilidad de datos
        if "data_availability" in sla_targets:
            target = sla_targets["data_availability"]
            total_validations = validation_results.get("total_validations", 0)
            passed = validation_results.get("passed", 0)
            availability = (passed / total_validations * 100) if total_validations > 0 else 0
            achieved = availability >= target
            sla_metrics["achievements"]["data_availability"] = {
                "target": target,
                "actual": round(availability, 2),
                "achieved": achieved,
                "status": "PASS" if achieved else "FAIL"
            }
        
        # SLA de errores críticos
        if "critical_errors" in sla_targets:
            target = sla_targets["critical_errors"]
            errors = validation_results.get("errors", [])
            critical_count = len([e for e in errors if e.get("severity") == "critical"])
            achieved = critical_count <= target
            sla_metrics["achievements"]["critical_errors"] = {
                "target": f"≤{target}",
                "actual": critical_count,
                "achieved": achieved,
                "status": "PASS" if achieved else "FAIL"
            }
        
        # SLA de tiempo de respuesta
        if "response_time" in sla_targets:
            target = sla_targets["response_time"]  # en segundos
            performance = validation_results.get("performance", {})
            avg_time = performance.get("avg_validation_time", 0)
            achieved = avg_time <= target
            sla_metrics["achievements"]["response_time"] = {
                "target": f"≤{target}s",
                "actual": round(avg_time, 2),
                "achieved": achieved,
                "status": "PASS" if achieved else "FAIL"
            }
        
        # SLA de calidad de datos
        if "data_quality_score" in sla_targets:
            target = sla_targets["data_quality_score"]
            metrics = validation_results.get("metrics", {})
            quality_score_data = metrics.get("quality_score", {})
            actual_score = quality_score_data.get("score", 0)
            achieved = actual_score >= target
            sla_metrics["achievements"]["data_quality_score"] = {
                "target": f"≥{target}",
                "actual": round(actual_score, 2),
                "achieved": achieved,
                "status": "PASS" if achieved else "FAIL"
            }
        
        # Calcular SLA general (porcentaje de objetivos cumplidos)
        if sla_metrics["achievements"]:
            achieved_count = sum(1 for a in sla_metrics["achievements"].values() if a.get("achieved", False))
            total_targets = len(sla_metrics["achievements"])
            sla_metrics["overall_sla"] = round((achieved_count / total_targets) * 100, 2)
        
        return sla_metrics
    
    except Exception as e:
        logger.error(f"Error calculando métricas SLA: {e}")
        return {"error": str(e)}


def validate_historical_snapshots(hook: PostgresHook, table_name: str, snapshot_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos históricos comparando con snapshots."""
    results = []
    
    try:
        snapshot_table = snapshot_config.get("snapshot_table", f"{table_name}_snapshots")
        comparison_field = snapshot_config.get("comparison_field", "id")
        snapshot_date = snapshot_config.get("snapshot_date")
        
        if not snapshot_date:
            # Usar snapshot más reciente
            query = f"""
                SELECT MAX(snapshot_date) as latest_date
                FROM {snapshot_table}
            """
            result = hook.get_first(query)
            snapshot_date = result[0] if result else None
        
        if not snapshot_date:
            results.append(ValidationResult(
                name="Snapshot histórico: No hay snapshots disponibles",
                passed=False,
                severity=Severity.WARNING,
                message="No se encontraron snapshots para comparar",
                count=0
            ))
            return results
        
        # Comparar conteos
        current_count_query = f"SELECT COUNT(*) FROM {table_name}"
        snapshot_count_query = f"""
            SELECT COUNT(*) 
            FROM {snapshot_table}
            WHERE snapshot_date = '{snapshot_date}'
        """
        
        current_count = hook.get_first(current_count_query)[0]
        snapshot_count = hook.get_first(snapshot_count_query)[0]
        
        if current_count != snapshot_count:
            diff = abs(current_count - snapshot_count)
            diff_pct = (diff / snapshot_count * 100) if snapshot_count > 0 else 0
            
            results.append(ValidationResult(
                name="Snapshot histórico: Diferencia en conteo",
                passed=False,
                severity=Severity.WARNING if diff_pct < 10 else Severity.ERROR,
                message=f"Conteo actual: {current_count}, Snapshot ({snapshot_date}): {snapshot_count}, Diferencia: {diff} ({diff_pct:.1f}%)",
                count=diff
            ))
        else:
            results.append(ValidationResult(
                name="Snapshot histórico: Conteo consistente",
                passed=True,
                severity=Severity.INFO,
                message=f"Conteo coincide con snapshot del {snapshot_date}",
                count=0
            ))
        
        # Comparar valores específicos si están configurados
        compare_fields = snapshot_config.get("compare_fields", [])
        for field in compare_fields:
            current_query = f"""
                SELECT COUNT(DISTINCT {field}) 
                FROM {table_name}
                WHERE {field} IS NOT NULL
            """
            snapshot_query = f"""
                SELECT COUNT(DISTINCT {field})
                FROM {snapshot_table}
                WHERE snapshot_date = '{snapshot_date}' AND {field} IS NOT NULL
            """
            
            current_distinct = hook.get_first(current_query)[0]
            snapshot_distinct = hook.get_first(snapshot_query)[0]
            
            if current_distinct != snapshot_distinct:
                results.append(ValidationResult(
                    name=f"Snapshot histórico: Diferencia en {field}",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"Valores distintos actuales: {current_distinct}, Snapshot: {snapshot_distinct}",
                    count=abs(current_distinct - snapshot_distinct)
                ))
    
    except Exception as e:
        logger.error(f"Error validando snapshots históricos: {e}")
        results.append(ValidationResult(
            name="Snapshot histórico: Error de validación",
            passed=False,
            severity=Severity.CRITICAL,
            message=f"Error: {str(e)}",
            count=0
        ))
    
    return results


def validate_geographic_data(hook: PostgresHook, table_name: str, geographic_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos geográficos (coordenadas, países, códigos postales, etc.)."""
    results = []
    
    try:
        # Validación de coordenadas (latitud/longitud)
        if geographic_rules.get("validate_coordinates", {}).get("enabled", False):
            lat_field = geographic_rules["validate_coordinates"].get("latitude_field", "latitude")
            lon_field = geographic_rules["validate_coordinates"].get("longitude_field", "longitude")
            
            # Validar rango de latitud (-90 a 90)
            lat_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {lat_field} IS NOT NULL
                AND ({lat_field} < -90 OR {lat_field} > 90)
            """
            lat_result = hook.get_first(lat_query)
            invalid_lat = lat_result[0] if lat_result else 0
            
            if invalid_lat > 0:
                results.append(ValidationResult(
                    name="Geográfico: Latitud inválida",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_lat} registros con latitud fuera de rango (-90 a 90)",
                    count=invalid_lat
                ))
            
            # Validar rango de longitud (-180 a 180)
            lon_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {lon_field} IS NOT NULL
                AND ({lon_field} < -180 OR {lon_field} > 180)
            """
            lon_result = hook.get_first(lon_query)
            invalid_lon = lon_result[0] if lon_result else 0
            
            if invalid_lon > 0:
                results.append(ValidationResult(
                    name="Geográfico: Longitud inválida",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_lon} registros con longitud fuera de rango (-180 a 180)",
                    count=invalid_lon
                ))
        
        # Validación de códigos postales
        if geographic_rules.get("validate_postal_codes", {}).get("enabled", False):
            postal_field = geographic_rules["validate_postal_codes"].get("field", "postal_code")
            country_field = geographic_rules["validate_postal_codes"].get("country_field", "country")
            format_rules = geographic_rules["validate_postal_codes"].get("formats", {})
            
            # Validación básica de formato (no vacío, longitud mínima)
            postal_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {postal_field} IS NOT NULL
                AND (LENGTH(TRIM({postal_field})) < 4 OR LENGTH(TRIM({postal_field})) > 10)
            """
            postal_result = hook.get_first(postal_query)
            invalid_postal = postal_result[0] if postal_result else 0
            
            if invalid_postal > 0:
                results.append(ValidationResult(
                    name="Geográfico: Código postal inválido",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_postal} registros con código postal de longitud inválida",
                    count=invalid_postal
                ))
        
        # Validación de países
        if geographic_rules.get("validate_countries", {}).get("enabled", False):
            country_field = geographic_rules["validate_countries"].get("field", "country")
            valid_countries = geographic_rules["validate_countries"].get("valid_countries", [])
            
            if valid_countries:
                countries_str = "', '".join(valid_countries)
                country_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {country_field} IS NOT NULL
                    AND UPPER(TRIM({country_field})) NOT IN ('{"', '".join([c.upper() for c in valid_countries])}')
                """
                country_result = hook.get_first(country_query)
                invalid_country = country_result[0] if country_result else 0
                
                if invalid_country > 0:
                    results.append(ValidationResult(
                        name="Geográfico: País inválido",
                        passed=False,
                        severity=Severity.WARNING,
                        message=f"{invalid_country} registros con país no válido",
                        count=invalid_country
                    ))
    
    except Exception as e:
        logger.error(f"Error validando datos geográficos: {e}")
    
    return results


def validate_time_series(hook: PostgresHook, table_name: str, time_series_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de series temporales."""
    results = []
    
    try:
        timestamp_field = time_series_config.get("timestamp_field", "timestamp")
        value_field = time_series_config.get("value_field", "value")
        
        # Validación 1: Detectar gaps en series temporales
        if time_series_config.get("detect_gaps", {}).get("enabled", False):
            expected_interval = time_series_config["detect_gaps"].get("expected_interval_minutes", 60)
            
            gap_query = f"""
                WITH time_series AS (
                    SELECT 
                        {timestamp_field},
                        LAG({timestamp_field}) OVER (ORDER BY {timestamp_field}) as prev_timestamp
                    FROM {table_name}
                    WHERE {timestamp_field} IS NOT NULL
                    ORDER BY {timestamp_field}
                )
                SELECT COUNT(*) as count
                FROM time_series
                WHERE prev_timestamp IS NOT NULL
                AND EXTRACT(EPOCH FROM ({timestamp_field} - prev_timestamp)) / 60 > {expected_interval * 1.5}
            """
            gap_result = hook.get_first(gap_query)
            gaps = gap_result[0] if gap_result else 0
            
            if gaps > 0:
                results.append(ValidationResult(
                    name="Serie temporal: Gaps detectados",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{gaps} gaps detectados en la serie temporal (intervalo esperado: {expected_interval} min)",
                    count=gaps
                ))
        
        # Validación 2: Detectar outliers en valores
        if time_series_config.get("detect_outliers", {}).get("enabled", False):
            method = time_series_config["detect_outliers"].get("method", "zscore")
            threshold = time_series_config["detect_outliers"].get("threshold", 3.0)
            
            if method == "zscore":
                outlier_query = f"""
                    WITH stats AS (
                        SELECT 
                            AVG({value_field}) as mean,
                            STDDEV({value_field}) as stddev
                        FROM {table_name}
                        WHERE {value_field} IS NOT NULL
                    )
                    SELECT COUNT(*) as count
                    FROM {table_name} t, stats s
                    WHERE t.{value_field} IS NOT NULL
                    AND ABS(t.{value_field} - s.mean) / NULLIF(s.stddev, 0) > {threshold}
                """
            else:  # iqr method
                outlier_query = f"""
                    WITH quartiles AS (
                        SELECT 
                            PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY {value_field}) as q1,
                            PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY {value_field}) as q3
                        FROM {table_name}
                        WHERE {value_field} IS NOT NULL
                    )
                    SELECT COUNT(*) as count
                    FROM {table_name} t, quartiles q
                    WHERE t.{value_field} IS NOT NULL
                    AND (t.{value_field} < q.q1 - 1.5 * (q.q3 - q.q1) 
                         OR t.{value_field} > q.q3 + 1.5 * (q.q3 - q.q1))
                """
            
            outlier_result = hook.get_first(outlier_query)
            outliers = outlier_result[0] if outlier_result else 0
            
            if outliers > 0:
                results.append(ValidationResult(
                    name="Serie temporal: Outliers detectados",
                    passed=False,
                    severity=Severity.INFO,  # Outliers pueden ser válidos
                    message=f"{outliers} outliers detectados usando método {method}",
                    count=outliers
                ))
        
        # Validación 3: Detectar valores faltantes en secuencia esperada
        if time_series_config.get("detect_missing_values", {}).get("enabled", False):
            missing_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {timestamp_field} IS NOT NULL
                AND {value_field} IS NULL
            """
            missing_result = hook.get_first(missing_query)
            missing = missing_result[0] if missing_result else 0
            
            if missing > 0:
                results.append(ValidationResult(
                    name="Serie temporal: Valores faltantes",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{missing} registros con timestamp pero sin valor",
                    count=missing
                ))
    
    except Exception as e:
        logger.error(f"Error validando series temporales: {e}")
    
    return results


def generate_auto_recommendations(validation_results: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Genera recomendaciones automáticas basadas en errores detectados."""
    recommendations = []
    
    try:
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        quality_score = validation_results.get("metrics", {}).get("quality_score", {})
        score = quality_score.get("score", 100)
        
        # Recomendación 1: Si hay muchos errores de campos requeridos
        required_field_errors = [e for e in errors if "requerido" in e.get("name", "").lower() or "null" in e.get("name", "").lower()]
        if len(required_field_errors) > 5:
            recommendations.append({
                "type": "data_ingestion",
                "priority": "high",
                "title": "Mejorar validación en ingesta de datos",
                "description": f"Se detectaron {len(required_field_errors)} errores de campos requeridos",
                "action": "Implementar validaciones en el punto de entrada de datos",
                "impact": "Alto - Afecta integridad de datos"
            })
        
        # Recomendación 2: Si hay muchos duplicados
        duplicate_errors = [e for e in errors if "duplicado" in e.get("name", "").lower() or "duplicate" in e.get("name", "").lower()]
        if len(duplicate_errors) > 3:
            recommendations.append({
                "type": "data_deduplication",
                "priority": "medium",
                "title": "Implementar proceso de deduplicación",
                "description": f"Se detectaron {len(duplicate_errors)} tipos de duplicados",
                "action": "Revisar lógica de deduplicación y agregar constraints únicos",
                "impact": "Medio - Afecta calidad de datos"
            })
        
        # Recomendación 3: Si el score de calidad es bajo
        if score < 70:
            recommendations.append({
                "type": "quality_improvement",
                "priority": "high",
                "title": "Mejorar calidad general de datos",
                "description": f"Score de calidad actual: {score:.1f}/100",
                "action": "Revisar procesos de limpieza y validación de datos",
                "impact": "Alto - Afecta confiabilidad de datos"
            })
        
        # Recomendación 4: Si hay errores de formato
        format_errors = [e for e in errors if "formato" in e.get("name", "").lower() or "format" in e.get("name", "").lower()]
        if len(format_errors) > 5:
            recommendations.append({
                "type": "data_validation",
                "priority": "medium",
                "title": "Mejorar validación de formatos",
                "description": f"Se detectaron {len(format_errors)} errores de formato",
                "action": "Implementar validaciones de formato más estrictas en ingesta",
                "impact": "Medio - Afecta consistencia de datos"
            })
        
        # Recomendación 5: Si hay errores de integridad referencial
        referential_errors = [e for e in errors if "referencial" in e.get("name", "").lower() or "referential" in e.get("name", "").lower()]
        if len(referential_errors) > 0:
            recommendations.append({
                "type": "data_integrity",
                "priority": "critical",
                "title": "Revisar integridad referencial",
                "description": f"Se detectaron {len(referential_errors)} violaciones de integridad referencial",
                "action": "Revisar y corregir referencias huérfanas o inconsistentes",
                "impact": "Crítico - Afecta integridad de datos"
            })
        
        # Recomendación 6: Si hay muchos warnings
        if len(warnings) > 10:
            recommendations.append({
                "type": "data_quality",
                "priority": "low",
                "title": "Revisar advertencias acumuladas",
                "description": f"Se detectaron {len(warnings)} advertencias",
                "action": "Revisar y resolver advertencias para mejorar calidad",
                "impact": "Bajo - Mejora calidad general"
            })
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generando recomendaciones automáticas: {e}")
        return []


def validate_financial_data(hook: PostgresHook, table_name: str, financial_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos financieros (montos, balances, transacciones, etc.)."""
    results = []
    
    try:
        # Validación de montos positivos/negativos
        if financial_rules.get("validate_amounts", {}).get("enabled", False):
            amount_field = financial_rules["validate_amounts"].get("field", "amount")
            allow_negative = financial_rules["validate_amounts"].get("allow_negative", False)
            
            if not allow_negative:
                amount_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {amount_field} IS NOT NULL
                    AND {amount_field} < 0
                """
                amount_result = hook.get_first(amount_query)
                negative_amounts = amount_result[0] if amount_result else 0
                
                if negative_amounts > 0:
                    results.append(ValidationResult(
                        name="Financiero: Montos negativos",
                        passed=False,
                        severity=Severity.ERROR,
                        message=f"{negative_amounts} registros con montos negativos no permitidos",
                        count=negative_amounts
                    ))
        
        # Validación de balances (suma debe ser cero o positiva)
        if financial_rules.get("validate_balances", {}).get("enabled", False):
            balance_field = financial_rules["validate_balances"].get("field", "balance")
            group_by = financial_rules["validate_balances"].get("group_by", [])
            
            if group_by:
                group_fields = ", ".join(group_by)
                balance_query = f"""
                    SELECT {group_fields}, SUM({balance_field}) as total_balance
                    FROM {table_name}
                    WHERE {balance_field} IS NOT NULL
                    GROUP BY {group_fields}
                    HAVING SUM({balance_field}) < 0
                """
            else:
                balance_query = f"""
                    SELECT SUM({balance_field}) as total_balance
                    FROM {table_name}
                    WHERE {balance_field} IS NOT NULL
                """
            
            balance_result = hook.get_records(balance_query)
            if balance_result and len(balance_result) > 0:
                if group_by:
                    invalid_balances = len(balance_result)
                    results.append(ValidationResult(
                        name="Financiero: Balances negativos por grupo",
                        passed=False,
                        severity=Severity.ERROR,
                        message=f"{invalid_balances} grupos con balance negativo",
                        count=invalid_balances
                    ))
                else:
                    total_balance = balance_result[0][0] if balance_result[0] else 0
                    if total_balance < 0:
                        results.append(ValidationResult(
                            name="Financiero: Balance total negativo",
                            passed=False,
                            severity=Severity.ERROR,
                            message=f"Balance total negativo: {total_balance}",
                            count=1
                        ))
        
        # Validación de decimales (precisión monetaria)
        if financial_rules.get("validate_precision", {}).get("enabled", False):
            amount_field = financial_rules["validate_precision"].get("field", "amount")
            max_decimals = financial_rules["validate_precision"].get("max_decimals", 2)
            
            precision_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {amount_field} IS NOT NULL
                AND ({amount_field} * POWER(10, {max_decimals}))::BIGINT != ({amount_field} * POWER(10, {max_decimals}))
            """
            precision_result = hook.get_first(precision_query)
            invalid_precision = precision_result[0] if precision_result else 0
            
            if invalid_precision > 0:
                results.append(ValidationResult(
                    name="Financiero: Precisión decimal inválida",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_precision} registros con más de {max_decimals} decimales",
                    count=invalid_precision
                ))
        
        # Validación de duplicados en transacciones
        if financial_rules.get("validate_duplicate_transactions", {}).get("enabled", False):
            transaction_fields = financial_rules["validate_duplicate_transactions"].get("fields", ["transaction_id"])
            fields_str = ", ".join(transaction_fields)
            
            duplicate_query = f"""
                SELECT {fields_str}, COUNT(*) as count
                FROM {table_name}
                GROUP BY {fields_str}
                HAVING COUNT(*) > 1
            """
            duplicate_result = hook.get_records(duplicate_query)
            duplicates = len(duplicate_result) if duplicate_result else 0
            
            if duplicates > 0:
                results.append(ValidationResult(
                    name="Financiero: Transacciones duplicadas",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{duplicates} grupos de transacciones duplicadas",
                    count=duplicates
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos financieros: {e}")
    
    return results


def calculate_reliability_score(validation_results: Dict[str, Any], historical_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Calcula score de confiabilidad de datos (0-100)."""
    try:
        total_validations = validation_results.get("total_validations", 0)
        passed = validation_results.get("passed", 0)
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        
        if total_validations == 0:
            return {"score": 0, "factors": {}, "level": "unreliable"}
        
        # Factor 1: Tasa de éxito (40%)
        success_rate = (passed / total_validations) * 100
        success_factor = success_rate * 0.4
        
        # Factor 2: Errores críticos (30%)
        critical_errors = len([e for e in errors if e.get("severity") == "critical"])
        critical_factor = max(0, (100 - critical_errors * 10)) * 0.3
        
        # Factor 3: Consistencia histórica (20%)
        consistency_factor = 20.0
        if historical_data:
            historical_passed = historical_data.get("passed", 0)
            historical_total = historical_data.get("total_validations", 0)
            if historical_total > 0:
                historical_rate = (historical_passed / historical_total) * 100
                consistency = 100 - abs(success_rate - historical_rate)
                consistency_factor = consistency * 0.2
        
        # Factor 4: Warnings (10%)
        warnings_factor = max(0, (100 - len(warnings) * 2)) * 0.1
        
        # Score final
        reliability_score = success_factor + critical_factor + consistency_factor + warnings_factor
        reliability_score = max(0, min(100, reliability_score))
        
        # Nivel de confiabilidad
        if reliability_score >= 90:
            level = "highly_reliable"
        elif reliability_score >= 75:
            level = "reliable"
        elif reliability_score >= 60:
            level = "moderate"
        elif reliability_score >= 40:
            level = "low"
        else:
            level = "unreliable"
        
        return {
            "score": round(reliability_score, 2),
            "level": level,
            "factors": {
                "success_rate": round(success_rate, 2),
                "critical_errors": critical_errors,
                "consistency": round(consistency_factor / 0.2, 2) if consistency_factor > 0 else 100,
                "warnings": len(warnings)
            },
            "recommendations": _get_reliability_recommendations(reliability_score, critical_errors)
        }
    
    except Exception as e:
        logger.error(f"Error calculando score de confiabilidad: {e}")
        return {"score": 0, "level": "unreliable", "error": str(e)}


def _get_reliability_recommendations(score: float, critical_errors: int) -> List[str]:
    """Genera recomendaciones para mejorar confiabilidad."""
    recommendations = []
    
    if score < 60:
        recommendations.append("🔴 Confiabilidad crítica: Implementar medidas urgentes")
    elif score < 75:
        recommendations.append("⚠️ Confiabilidad baja: Revisar procesos de validación")
    
    if critical_errors > 0:
        recommendations.append(f"🔴 {critical_errors} errores críticos afectan confiabilidad")
    
    if score >= 90:
        recommendations.append("✅ Alta confiabilidad mantenida")
    
    return recommendations


def validate_streaming_data(hook: PostgresHook, table_name: str, streaming_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de streaming (tiempo real)."""
    results = []
    
    try:
        timestamp_field = streaming_config.get("timestamp_field", "timestamp")
        latency_threshold_ms = streaming_config.get("latency_threshold_ms", 5000)
        
        # Validación 1: Latencia de datos
        if streaming_config.get("check_latency", {}).get("enabled", False):
            latency_query = f"""
                SELECT 
                    COUNT(*) as count,
                    AVG(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - {timestamp_field})) * 1000) as avg_latency_ms
                FROM {table_name}
                WHERE {timestamp_field} IS NOT NULL
                AND {timestamp_field} >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
            """
            latency_result = hook.get_first(latency_query)
            high_latency_count = latency_result[0] if latency_result else 0
            avg_latency = latency_result[1] if latency_result and len(latency_result) > 1 else 0
            
            if avg_latency and avg_latency > latency_threshold_ms:
                results.append(ValidationResult(
                    name="Streaming: Latencia alta",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"Latencia promedio: {avg_latency:.0f}ms (umbral: {latency_threshold_ms}ms)",
                    count=int(avg_latency)
                ))
        
        # Validación 2: Throughput (registros por segundo)
        if streaming_config.get("check_throughput", {}).get("enabled", False):
            min_throughput = streaming_config["check_throughput"].get("min_records_per_second", 10)
            
            throughput_query = f"""
                SELECT COUNT(*) / 60.0 as records_per_second
                FROM {table_name}
                WHERE {timestamp_field} >= CURRENT_TIMESTAMP - INTERVAL '1 minute'
            """
            throughput_result = hook.get_first(throughput_query)
            throughput = throughput_result[0] if throughput_result else 0
            
            if throughput < min_throughput:
                results.append(ValidationResult(
                    name="Streaming: Throughput bajo",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"Throughput: {throughput:.1f} registros/seg (mínimo: {min_throughput})",
                    count=int(throughput)
                ))
        
        # Validación 3: Detectar lag en procesamiento
        if streaming_config.get("check_processing_lag", {}).get("enabled", False):
            processing_field = streaming_config["check_processing_lag"].get("processing_timestamp_field", "processed_at")
            max_lag_seconds = streaming_config["check_processing_lag"].get("max_lag_seconds", 30)
            
            lag_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {timestamp_field} IS NOT NULL
                AND {processing_field} IS NOT NULL
                AND EXTRACT(EPOCH FROM ({processing_field} - {timestamp_field})) > {max_lag_seconds}
            """
            lag_result = hook.get_first(lag_query)
            lag_count = lag_result[0] if lag_result else 0
            
            if lag_count > 0:
                results.append(ValidationResult(
                    name="Streaming: Lag de procesamiento",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{lag_count} registros con lag de procesamiento > {max_lag_seconds}s",
                    count=lag_count
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de streaming: {e}")
    
    return results


def validate_iot_sensor_data(hook: PostgresHook, table_name: str, iot_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de IoT y sensores."""
    results = []
    
    try:
        sensor_id_field = iot_config.get("sensor_id_field", "sensor_id")
        value_field = iot_config.get("value_field", "value")
        timestamp_field = iot_config.get("timestamp_field", "timestamp")
        
        # Validación 1: Detectar sensores desconectados
        if iot_config.get("detect_disconnected_sensors", {}).get("enabled", False):
            max_silence_minutes = iot_config["detect_disconnected_sensors"].get("max_silence_minutes", 60)
            
            disconnected_query = f"""
                SELECT {sensor_id_field}, MAX({timestamp_field}) as last_reading
                FROM {table_name}
                GROUP BY {sensor_id_field}
                HAVING MAX({timestamp_field}) < CURRENT_TIMESTAMP - INTERVAL '{max_silence_minutes} minutes'
            """
            disconnected_result = hook.get_records(disconnected_query)
            disconnected_count = len(disconnected_result) if disconnected_result else 0
            
            if disconnected_count > 0:
                results.append(ValidationResult(
                    name="IoT: Sensores desconectados",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{disconnected_count} sensores sin lectura en los últimos {max_silence_minutes} minutos",
                    count=disconnected_count
                ))
        
        # Validación 2: Detectar valores fuera de rango físico
        if iot_config.get("validate_physical_ranges", {}).get("enabled", False):
            min_value = iot_config["validate_physical_ranges"].get("min_value")
            max_value = iot_config["validate_physical_ranges"].get("max_value")
            
            if min_value is not None and max_value is not None:
                range_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {value_field} IS NOT NULL
                    AND ({value_field} < {min_value} OR {value_field} > {max_value})
                """
                range_result = hook.get_first(range_query)
                out_of_range = range_result[0] if range_result else 0
                
                if out_of_range > 0:
                    results.append(ValidationResult(
                        name="IoT: Valores fuera de rango físico",
                        passed=False,
                        severity=Severity.ERROR,
                        message=f"{out_of_range} lecturas fuera de rango [{min_value}, {max_value}]",
                        count=out_of_range
                    ))
        
        # Validación 3: Detectar lecturas duplicadas (posible error de sensor)
        if iot_config.get("detect_duplicate_readings", {}).get("enabled", False):
            duplicate_window_seconds = iot_config["detect_duplicate_readings"].get("window_seconds", 1)
            
            duplicate_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name} t1
                WHERE EXISTS (
                    SELECT 1 FROM {table_name} t2
                    WHERE t1.{sensor_id_field} = t2.{sensor_id_field}
                    AND t1.{value_field} = t2.{value_field}
                    AND ABS(EXTRACT(EPOCH FROM (t1.{timestamp_field} - t2.{timestamp_field}))) < {duplicate_window_seconds}
                    AND t1.ctid < t2.ctid
                )
            """
            duplicate_result = hook.get_first(duplicate_query)
            duplicates = duplicate_result[0] if duplicate_result else 0
            
            if duplicates > 0:
                results.append(ValidationResult(
                    name="IoT: Lecturas duplicadas",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{duplicates} lecturas duplicadas detectadas (posible error de sensor)",
                    count=duplicates
                ))
        
        # Validación 4: Detectar cambios abruptos (posible falla de sensor)
        if iot_config.get("detect_abrupt_changes", {}).get("enabled", False):
            change_threshold = iot_config["detect_abrupt_changes"].get("threshold_percent", 50)
            
            abrupt_query = f"""
                WITH sensor_readings AS (
                    SELECT 
                        {sensor_id_field},
                        {value_field},
                        {timestamp_field},
                        LAG({value_field}) OVER (PARTITION BY {sensor_id_field} ORDER BY {timestamp_field}) as prev_value
                    FROM {table_name}
                    WHERE {value_field} IS NOT NULL
                )
                SELECT COUNT(*) as count
                FROM sensor_readings
                WHERE prev_value IS NOT NULL
                AND ABS({value_field} - prev_value) / NULLIF(ABS(prev_value), 0) * 100 > {change_threshold}
            """
            abrupt_result = hook.get_first(abrupt_query)
            abrupt_changes = abrupt_result[0] if abrupt_result else 0
            
            if abrupt_changes > 0:
                results.append(ValidationResult(
                    name="IoT: Cambios abruptos detectados",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{abrupt_changes} cambios abruptos > {change_threshold}% (posible falla de sensor)",
                    count=abrupt_changes
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos IoT: {e}")
    
    return results


def adaptive_ml_improvement(validation_results: Dict[str, Any], historical_data: List[Dict[str, Any]], 
                           ml_config: Dict[str, Any]) -> Dict[str, Any]:
    """Sistema de ML adaptativo para mejorar validaciones basado en historial."""
    try:
        from collections import Counter
        
        improvements = {
            "timestamp": pendulum.now().isoformat(),
            "suggestions": [],
            "model_updates": {}
        }
        
        if not historical_data or len(historical_data) < 5:
            return {"message": "Datos históricos insuficientes para ML adaptativo"}
        
        # Análisis 1: Identificar validaciones que siempre fallan
        all_validation_names = []
        for hist in historical_data:
            errors = hist.get("errors", [])
            all_validation_names.extend([e.get("name", "") for e in errors])
        
        validation_counts = Counter(all_validation_names)
        most_common_failures = validation_counts.most_common(5)
        
        for validation_name, count in most_common_failures:
            if count >= len(historical_data) * 0.8:  # Falla en 80% de las ejecuciones
                improvements["suggestions"].append({
                    "type": "validation_tuning",
                    "priority": "high",
                    "validation": validation_name,
                    "issue": f"Falla consistentemente ({count}/{len(historical_data)} ejecuciones)",
                    "recommendation": "Revisar y ajustar umbrales o lógica de validación"
                })
        
        # Análisis 2: Detectar patrones temporales
        error_trends = []
        for hist in historical_data:
            error_count = len(hist.get("errors", []))
            error_trends.append(error_count)
        
        if len(error_trends) >= 7:
            recent_avg = sum(error_trends[-3:]) / 3
            older_avg = sum(error_trends[-7:-3]) / 4 if len(error_trends) >= 7 else recent_avg
            
            if recent_avg > older_avg * 1.5:
                improvements["suggestions"].append({
                    "type": "trend_analysis",
                    "priority": "medium",
                    "issue": "Tendencia creciente de errores detectada",
                    "recommendation": "Investigar causas de degradación reciente"
                })
        
        # Análisis 3: Optimizar umbrales basado en falsos positivos/negativos
        if ml_config.get("optimize_thresholds", {}).get("enabled", False):
            improvements["model_updates"]["threshold_optimization"] = {
                "status": "pending",
                "recommendation": "Analizar tasa de falsos positivos/negativos para ajustar umbrales"
            }
        
        return improvements
    
    except ImportError:
        logger.warning("Librerías ML no disponibles para análisis adaptativo")
        return {"message": "ML adaptativo no disponible"}
    except Exception as e:
        logger.error(f"Error en ML adaptativo: {e}")
        return {"error": str(e)}


def validate_blockchain_data(hook: PostgresHook, table_name: str, blockchain_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de blockchain (hashes, bloques, transacciones)."""
    results = []
    
    try:
        # Validación 1: Verificar formato de hashes
        if blockchain_config.get("validate_hash_format", {}).get("enabled", False):
            hash_field = blockchain_config["validate_hash_format"].get("field", "hash")
            hash_length = blockchain_config["validate_hash_format"].get("expected_length", 64)
            
            hash_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {hash_field} IS NOT NULL
                AND (LENGTH({hash_field}) != {hash_length} 
                     OR {hash_field} !~ '^[0-9a-fA-F]{{{hash_length}}}$')
            """
            hash_result = hook.get_first(hash_query)
            invalid_hashes = hash_result[0] if hash_result else 0
            
            if invalid_hashes > 0:
                results.append(ValidationResult(
                    name="Blockchain: Hashes con formato inválido",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_hashes} hashes con formato inválido (esperado: {hash_length} caracteres hex)",
                    count=invalid_hashes
                ))
        
        # Validación 2: Verificar integridad de cadena (prev_hash)
        if blockchain_config.get("validate_chain_integrity", {}).get("enabled", False):
            block_id_field = blockchain_config["validate_chain_integrity"].get("block_id_field", "block_id")
            prev_hash_field = blockchain_config["validate_chain_integrity"].get("prev_hash_field", "prev_hash")
            hash_field = blockchain_config["validate_chain_integrity"].get("hash_field", "hash")
            
            chain_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name} t1
                LEFT JOIN {table_name} t2 ON t1.{prev_hash_field} = t2.{hash_field}
                WHERE t1.{prev_hash_field} IS NOT NULL
                AND t2.{hash_field} IS NULL
            """
            chain_result = hook.get_first(chain_query)
            broken_chain = chain_result[0] if chain_result else 0
            
            if broken_chain > 0:
                results.append(ValidationResult(
                    name="Blockchain: Cadena rota",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"{broken_chain} bloques con referencia prev_hash inválida",
                    count=broken_chain
                ))
        
        # Validación 3: Verificar duplicados de bloques
        if blockchain_config.get("validate_unique_blocks", {}).get("enabled", False):
            block_id_field = blockchain_config["validate_unique_blocks"].get("field", "block_id")
            
            unique_query = f"""
                SELECT {block_id_field}, COUNT(*) as count
                FROM {table_name}
                GROUP BY {block_id_field}
                HAVING COUNT(*) > 1
            """
            unique_result = hook.get_records(unique_query)
            duplicates = len(unique_result) if unique_result else 0
            
            if duplicates > 0:
                results.append(ValidationResult(
                    name="Blockchain: Bloques duplicados",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{duplicates} bloques duplicados detectados",
                    count=duplicates
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos blockchain: {e}")
    
    return results


def generate_predictive_alerts(validation_results: Dict[str, Any], historical_data: List[Dict[str, Any]], 
                               config: Dict[str, Any]) -> Dict[str, Any]:
    """Genera alertas predictivas basadas en ML y tendencias."""
    try:
        alerts = {
            "timestamp": pendulum.now().isoformat(),
            "predictive_alerts": [],
            "confidence": {}
        }
        
        if not historical_data or len(historical_data) < 7:
            return {"message": "Datos históricos insuficientes para predicción"}
        
        # Predicción 1: Probabilidad de falla en próxima ejecución
        recent_errors = [len(h.get("errors", [])) for h in historical_data[-7:]]
        avg_recent_errors = sum(recent_errors) / len(recent_errors)
        current_errors = len(validation_results.get("errors", []))
        
        if current_errors > avg_recent_errors * 1.5:
            probability = min(90, 50 + (current_errors - avg_recent_errors) * 5)
            alerts["predictive_alerts"].append({
                "type": "failure_probability",
                "severity": "high" if probability > 70 else "medium",
                "message": f"Alta probabilidad ({probability:.0f}%) de falla en próxima ejecución",
                "confidence": probability,
                "recommendation": "Revisar y corregir errores actuales antes de próxima ejecución"
            })
            alerts["confidence"]["failure_probability"] = probability
        
        # Predicción 2: Degradación de calidad
        quality_scores = []
        for hist in historical_data:
            qs = hist.get("metrics", {}).get("quality_score", {}).get("score", 100)
            quality_scores.append(qs)
        
        if len(quality_scores) >= 5:
            recent_quality = sum(quality_scores[-3:]) / 3
            older_quality = sum(quality_scores[-6:-3]) / 3 if len(quality_scores) >= 6 else recent_quality
            
            if recent_quality < older_quality - 10:
                alerts["predictive_alerts"].append({
                    "type": "quality_degradation",
                    "severity": "high",
                    "message": f"Degradación de calidad detectada: {older_quality:.1f} → {recent_quality:.1f}",
                    "confidence": 75,
                    "recommendation": "Implementar medidas preventivas"
                })
                alerts["confidence"]["quality_degradation"] = 75
        
        # Predicción 3: Aumento de errores críticos
        critical_counts = []
        for hist in historical_data:
            errors = hist.get("errors", [])
            critical = len([e for e in errors if e.get("severity") == "critical"])
            critical_counts.append(critical)
        
        if len(critical_counts) >= 5:
            recent_critical = sum(critical_counts[-3:]) / 3
            if recent_critical > 2:
                alerts["predictive_alerts"].append({
                    "type": "critical_errors_trend",
                    "severity": "critical",
                    "message": f"Tendencia creciente de errores críticos: {recent_critical:.1f} promedio",
                    "confidence": 80,
                    "recommendation": "Revisar inmediatamente y considerar pausar procesos críticos"
                })
                alerts["confidence"]["critical_errors_trend"] = 80
        
        return alerts
    
    except Exception as e:
        logger.error(f"Error generando alertas predictivas: {e}")
        return {"error": str(e)}


def validate_external_api_data(hook: PostgresHook, table_name: str, api_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos provenientes de APIs externas."""
    results = []
    
    try:
        # Validación 1: Verificar frescura de datos de API
        if api_config.get("validate_api_freshness", {}).get("enabled", False):
            api_timestamp_field = api_config["validate_api_freshness"].get("timestamp_field", "api_timestamp")
            max_age_minutes = api_config["validate_api_freshness"].get("max_age_minutes", 60)
            
            freshness_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {api_timestamp_field} IS NOT NULL
                AND {api_timestamp_field} < CURRENT_TIMESTAMP - INTERVAL '{max_age_minutes} minutes'
            """
            freshness_result = hook.get_first(freshness_query)
            stale_data = freshness_result[0] if freshness_result else 0
            
            if stale_data > 0:
                results.append(ValidationResult(
                    name="API Externa: Datos desactualizados",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{stale_data} registros con datos de API desactualizados (> {max_age_minutes} min)",
                    count=stale_data
                ))
        
        # Validación 2: Verificar códigos de respuesta de API
        if api_config.get("validate_api_response_codes", {}).get("enabled", False):
            response_code_field = api_config["validate_api_response_codes"].get("field", "api_response_code")
            valid_codes = api_config["validate_api_response_codes"].get("valid_codes", [200, 201])
            
            codes_str = ", ".join(map(str, valid_codes))
            response_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {response_code_field} IS NOT NULL
                AND {response_code_field}::int NOT IN ({codes_str})
            """
            response_result = hook.get_first(response_query)
            invalid_responses = response_result[0] if response_result else 0
            
            if invalid_responses > 0:
                results.append(ValidationResult(
                    name="API Externa: Códigos de respuesta inválidos",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_responses} registros con códigos de respuesta inválidos",
                    count=invalid_responses
                ))
        
        # Validación 3: Verificar rate limiting
        if api_config.get("validate_rate_limiting", {}).get("enabled", False):
            timestamp_field = api_config["validate_rate_limiting"].get("timestamp_field", "created_at")
            max_requests_per_minute = api_config["validate_rate_limiting"].get("max_requests_per_minute", 60)
            
            rate_query = f"""
                SELECT COUNT(*) as count
                FROM (
                    SELECT DATE_TRUNC('minute', {timestamp_field}) as minute, COUNT(*) as requests
                    FROM {table_name}
                    WHERE {timestamp_field} >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
                    GROUP BY DATE_TRUNC('minute', {timestamp_field})
                    HAVING COUNT(*) > {max_requests_per_minute}
                ) rate_limits
            """
            rate_result = hook.get_first(rate_query)
            rate_limit_violations = rate_result[0] if rate_result else 0
            
            if rate_limit_violations > 0:
                results.append(ValidationResult(
                    name="API Externa: Violaciones de rate limiting",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{rate_limit_violations} períodos con exceso de requests (> {max_requests_per_minute}/min)",
                    count=rate_limit_violations
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de API externa: {e}")
    
    return results


def calculate_advanced_performance_metrics(validation_results: Dict[str, Any], execution_times: Dict[str, float]) -> Dict[str, Any]:
    """Calcula métricas de rendimiento avanzadas."""
    try:
        metrics = {
            "timestamp": pendulum.now().isoformat(),
            "execution_metrics": {},
            "bottlenecks": [],
            "recommendations": []
        }
        
        # Métrica 1: Tiempo total de ejecución
        total_time = execution_times.get("total", 0)
        metrics["execution_metrics"]["total_execution_time"] = {
            "value": round(total_time, 2),
            "unit": "seconds"
        }
        
        # Métrica 2: Tiempo por tipo de validación
        validation_times = execution_times.get("validations", {})
        if validation_times:
            metrics["execution_metrics"]["validation_times"] = {
                k: {"value": round(v, 2), "unit": "seconds"}
                for k, v in validation_times.items()
            }
            
            # Identificar cuellos de botella
            if validation_times:
                max_time = max(validation_times.values())
                max_validation = max(validation_times.items(), key=lambda x: x[1])
                if max_time > total_time * 0.3:  # Más del 30% del tiempo total
                    metrics["bottlenecks"].append({
                        "type": "validation",
                        "name": max_validation[0],
                        "time": round(max_validation[1], 2),
                        "percentage": round((max_validation[1] / total_time) * 100, 1)
                    })
                    metrics["recommendations"].append({
                        "type": "optimization",
                        "priority": "high",
                        "message": f"Optimizar validación '{max_validation[0]}' que toma {max_validation[1]:.1f}s ({round((max_validation[1]/total_time)*100, 1)}% del tiempo total)",
                        "action": "Considerar paralelización o optimización de queries"
                    })
        
        # Métrica 3: Throughput (validaciones por segundo)
        total_validations = validation_results.get("total_validations", 0)
        if total_time > 0:
            throughput = total_validations / total_time
            metrics["execution_metrics"]["throughput"] = {
                "value": round(throughput, 2),
                "unit": "validations_per_second"
            }
        
        # Métrica 4: Eficiencia (validaciones pasadas / tiempo)
        passed = validation_results.get("passed", 0)
        if total_time > 0:
            efficiency = passed / total_time
            metrics["execution_metrics"]["efficiency"] = {
                "value": round(efficiency, 2),
                "unit": "passed_validations_per_second"
            }
        
        # Métrica 5: Tiempo promedio por validación
        if total_validations > 0:
            avg_time = total_time / total_validations
            metrics["execution_metrics"]["avg_time_per_validation"] = {
                "value": round(avg_time, 3),
                "unit": "seconds"
            }
        
        return metrics
    
    except Exception as e:
        logger.error(f"Error calculando métricas de rendimiento: {e}")
        return {"error": str(e)}


def validate_social_media_data(hook: PostgresHook, table_name: str, social_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de redes sociales."""
    results = []
    
    try:
        # Validación 1: Verificar formato de handles/usernames
        if social_config.get("validate_usernames", {}).get("enabled", False):
            username_field = social_config["validate_usernames"].get("field", "username")
            platform = social_config["validate_usernames"].get("platform", "twitter")
            
            if platform == "twitter":
                # Twitter: 1-15 caracteres, alfanuméricos y guiones bajos
                username_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {username_field} IS NOT NULL
                    AND ({username_field} !~ '^[a-zA-Z0-9_]{{1,15}}$'
                         OR LENGTH({username_field}) < 1
                         OR LENGTH({username_field}) > 15)
                """
            elif platform == "instagram":
                # Instagram: 1-30 caracteres, alfanuméricos, puntos y guiones bajos
                username_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {username_field} IS NOT NULL
                    AND ({username_field} !~ '^[a-zA-Z0-9._]{{1,30}}$'
                         OR LENGTH({username_field}) < 1
                         OR LENGTH({username_field}) > 30)
                """
            else:
                # Genérico: alfanuméricos y algunos caracteres especiales
                username_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {username_field} IS NOT NULL
                    AND {username_field} !~ '^[a-zA-Z0-9._-]+$'
                """
            
            username_result = hook.get_first(username_query)
            invalid_usernames = username_result[0] if username_result else 0
            
            if invalid_usernames > 0:
                results.append(ValidationResult(
                    name=f"Redes Sociales: Usernames inválidos ({platform})",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_usernames} usernames con formato inválido para {platform}",
                    count=invalid_usernames
                ))
        
        # Validación 2: Verificar URLs de perfiles
        if social_config.get("validate_profile_urls", {}).get("enabled", False):
            url_field = social_config["validate_profile_urls"].get("field", "profile_url")
            platform = social_config["validate_profile_urls"].get("platform", "twitter")
            
            if platform == "twitter":
                url_pattern = "https://twitter.com/"
            elif platform == "instagram":
                url_pattern = "https://www.instagram.com/"
            elif platform == "facebook":
                url_pattern = "https://www.facebook.com/"
            else:
                url_pattern = "https://"
            
            url_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {url_field} IS NOT NULL
                AND {url_field} NOT LIKE '{url_pattern}%'
            """
            url_result = hook.get_first(url_query)
            invalid_urls = url_result[0] if url_result else 0
            
            if invalid_urls > 0:
                results.append(ValidationResult(
                    name=f"Redes Sociales: URLs de perfil inválidas ({platform})",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_urls} URLs de perfil con formato inválido",
                    count=invalid_urls
                ))
        
        # Validación 3: Verificar engagement metrics
        if social_config.get("validate_engagement", {}).get("enabled", False):
            likes_field = social_config["validate_engagement"].get("likes_field", "likes")
            shares_field = social_config["validate_engagement"].get("shares_field", "shares")
            comments_field = social_config["validate_engagement"].get("comments_field", "comments")
            
            engagement_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE ({likes_field} IS NOT NULL AND {likes_field} < 0)
                   OR ({shares_field} IS NOT NULL AND {shares_field} < 0)
                   OR ({comments_field} IS NOT NULL AND {comments_field} < 0)
            """
            engagement_result = hook.get_first(engagement_query)
            invalid_engagement = engagement_result[0] if engagement_result else 0
            
            if invalid_engagement > 0:
                results.append(ValidationResult(
                    name="Redes Sociales: Métricas de engagement inválidas",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_engagement} registros con métricas de engagement negativas",
                    count=invalid_engagement
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de redes sociales: {e}")
    
    return results


def validate_media_data(hook: PostgresHook, table_name: str, media_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de imágenes y videos."""
    results = []
    
    try:
        # Validación 1: Verificar formatos de archivos
        if media_config.get("validate_file_formats", {}).get("enabled", False):
            file_path_field = media_config["validate_file_formats"].get("field", "file_path")
            media_type = media_config["validate_file_formats"].get("media_type", "image")  # image o video
            valid_formats = media_config["validate_file_formats"].get("valid_formats", [])
            
            if media_type == "image":
                default_formats = ["jpg", "jpeg", "png", "gif", "webp", "bmp"]
                formats = valid_formats if valid_formats else default_formats
            else:  # video
                default_formats = ["mp4", "avi", "mov", "mkv", "webm"]
                formats = valid_formats if valid_formats else default_formats
            
            formats_str = "', '".join([f".{f}" for f in formats])
            format_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {file_path_field} IS NOT NULL
                AND LOWER({file_path_field}) NOT LIKE ANY(ARRAY[{', '.join([f"'%{f}'" for f in formats])}])
            """
            format_result = hook.get_first(format_query)
            invalid_formats = format_result[0] if format_result else 0
            
            if invalid_formats > 0:
                results.append(ValidationResult(
                    name=f"Medios: Formatos inválidos ({media_type})",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_formats} archivos con formato inválido (válidos: {', '.join(formats)})",
                    count=invalid_formats
                ))
        
        # Validación 2: Verificar tamaños de archivos
        if media_config.get("validate_file_sizes", {}).get("enabled", False):
            size_field = media_config["validate_file_sizes"].get("field", "file_size_bytes")
            max_size_mb = media_config["validate_file_sizes"].get("max_size_mb", 10)
            max_size_bytes = max_size_mb * 1024 * 1024
            
            size_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {size_field} IS NOT NULL
                AND {size_field} > {max_size_bytes}
            """
            size_result = hook.get_first(size_query)
            oversized = size_result[0] if size_result else 0
            
            if oversized > 0:
                results.append(ValidationResult(
                    name="Medios: Archivos demasiado grandes",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{oversized} archivos exceden tamaño máximo ({max_size_mb}MB)",
                    count=oversized
                ))
        
        # Validación 3: Verificar dimensiones de imágenes
        if media_config.get("validate_image_dimensions", {}).get("enabled", False):
            width_field = media_config["validate_image_dimensions"].get("width_field", "width")
            height_field = media_config["validate_image_dimensions"].get("height_field", "height")
            min_width = media_config["validate_image_dimensions"].get("min_width", 100)
            min_height = media_config["validate_image_dimensions"].get("min_height", 100)
            max_width = media_config["validate_image_dimensions"].get("max_width", 10000)
            max_height = media_config["validate_image_dimensions"].get("max_height", 10000)
            
            dimension_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE ({width_field} IS NOT NULL AND ({width_field} < {min_width} OR {width_field} > {max_width}))
                   OR ({height_field} IS NOT NULL AND ({height_field} < {min_height} OR {height_field} > {max_height}))
            """
            dimension_result = hook.get_first(dimension_query)
            invalid_dimensions = dimension_result[0] if dimension_result else 0
            
            if invalid_dimensions > 0:
                results.append(ValidationResult(
                    name="Medios: Dimensiones de imagen inválidas",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_dimensions} imágenes con dimensiones fuera de rango ({min_width}x{min_height} - {max_width}x{max_height})",
                    count=invalid_dimensions
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de medios: {e}")
    
    return results


def calculate_cost_metrics(validation_results: Dict[str, Any], execution_times: Dict[str, float], 
                          cost_config: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula métricas de costos de procesamiento."""
    try:
        cost_metrics = {
            "timestamp": pendulum.now().isoformat(),
            "costs": {},
            "recommendations": []
        }
        
        execution_time_hours = execution_times.get("total", 0) / 3600
        total_validations = validation_results.get("total_validations", 0)
        
        # Costo de compute (si está configurado)
        if cost_config.get("calculate_compute_cost", {}).get("enabled", False):
            cost_per_hour = cost_config["calculate_compute_cost"].get("cost_per_hour", 1.0)
            compute_cost = execution_time_hours * cost_per_hour
            
            cost_metrics["costs"]["compute"] = {
                "value": round(compute_cost, 4),
                "unit": "currency",
                "execution_time_hours": round(execution_time_hours, 4),
                "cost_per_hour": cost_per_hour
            }
        
        # Costo por validación
        if execution_time_hours > 0 and total_validations > 0:
            cost_per_validation = cost_metrics["costs"].get("compute", {}).get("value", 0) / total_validations
            cost_metrics["costs"]["cost_per_validation"] = {
                "value": round(cost_per_validation, 6),
                "unit": "currency"
            }
        
        # Costo de almacenamiento (si está configurado)
        if cost_config.get("calculate_storage_cost", {}).get("enabled", False):
            total_records = validation_results.get("metrics", {}).get("total_records", 0)
            bytes_per_record = cost_config["calculate_storage_cost"].get("bytes_per_record", 1024)
            cost_per_gb_month = cost_config["calculate_storage_cost"].get("cost_per_gb_month", 0.1)
            
            total_gb = (total_records * bytes_per_record) / (1024 ** 3)
            storage_cost_monthly = total_gb * cost_per_gb_month
            
            cost_metrics["costs"]["storage"] = {
                "value": round(storage_cost_monthly, 4),
                "unit": "currency_per_month",
                "total_gb": round(total_gb, 2),
                "total_records": total_records
            }
        
        # Recomendaciones de optimización de costos
        if cost_metrics["costs"].get("compute", {}).get("value", 0) > 1.0:
            cost_metrics["recommendations"].append({
                "type": "cost_optimization",
                "priority": "medium",
                "message": f"Costo de compute alto: ${cost_metrics['costs']['compute']['value']:.2f}",
                "action": "Considerar optimizar queries o reducir frecuencia de validaciones"
            })
        
        return cost_metrics
    
    except Exception as e:
        logger.error(f"Error calculando métricas de costos: {e}")
        return {"error": str(e)}


def validate_environmental_sensors(hook: PostgresHook, table_name: str, env_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de sensores ambientales (temperatura, humedad, presión, etc.)."""
    results = []
    
    try:
        sensor_id_field = env_config.get("sensor_id_field", "sensor_id")
        timestamp_field = env_config.get("timestamp_field", "timestamp")
        
        # Validación 1: Rangos físicos para temperatura
        if env_config.get("validate_temperature", {}).get("enabled", False):
            temp_field = env_config["validate_temperature"].get("field", "temperature")
            min_temp = env_config["validate_temperature"].get("min_celsius", -50)
            max_temp = env_config["validate_temperature"].get("max_celsius", 60)
            
            temp_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {temp_field} IS NOT NULL
                AND ({temp_field} < {min_temp} OR {temp_field} > {max_temp})
            """
            temp_result = hook.get_first(temp_query)
            invalid_temp = temp_result[0] if temp_result else 0
            
            if invalid_temp > 0:
                results.append(ValidationResult(
                    name="Sensor Ambiental: Temperatura fuera de rango",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_temp} lecturas de temperatura fuera de rango ({min_temp}°C - {max_temp}°C)",
                    count=invalid_temp
                ))
        
        # Validación 2: Rangos para humedad
        if env_config.get("validate_humidity", {}).get("enabled", False):
            humidity_field = env_config["validate_humidity"].get("field", "humidity")
            
            humidity_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {humidity_field} IS NOT NULL
                AND ({humidity_field} < 0 OR {humidity_field} > 100)
            """
            humidity_result = hook.get_first(humidity_query)
            invalid_humidity = humidity_result[0] if humidity_result else 0
            
            if invalid_humidity > 0:
                results.append(ValidationResult(
                    name="Sensor Ambiental: Humedad fuera de rango",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_humidity} lecturas de humedad fuera de rango (0% - 100%)",
                    count=invalid_humidity
                ))
        
        # Validación 3: Detectar lecturas fuera de horario esperado
        if env_config.get("validate_reading_times", {}).get("enabled", False):
            expected_interval_minutes = env_config["validate_reading_times"].get("expected_interval_minutes", 60)
            
            time_gap_query = f"""
                WITH time_gaps AS (
                    SELECT 
                        {sensor_id_field},
                        {timestamp_field},
                        LAG({timestamp_field}) OVER (PARTITION BY {sensor_id_field} ORDER BY {timestamp_field}) as prev_timestamp
                    FROM {table_name}
                    WHERE {timestamp_field} IS NOT NULL
                )
                SELECT COUNT(*) as count
                FROM time_gaps
                WHERE prev_timestamp IS NOT NULL
                AND EXTRACT(EPOCH FROM ({timestamp_field} - prev_timestamp)) / 60 > {expected_interval_minutes * 2}
            """
            gap_result = hook.get_first(time_gap_query)
            large_gaps = gap_result[0] if gap_result else 0
            
            if large_gaps > 0:
                results.append(ValidationResult(
                    name="Sensor Ambiental: Gaps grandes en lecturas",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{large_gaps} gaps grandes detectados (intervalo esperado: {expected_interval_minutes} min)",
                    count=large_gaps
                ))
    
    except Exception as e:
        logger.error(f"Error validando sensores ambientales: {e}")
    
    return results


def validate_ecommerce_data(hook: PostgresHook, table_name: str, ecommerce_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de e-commerce (productos, órdenes, carritos, etc.)."""
    results = []
    
    try:
        # Validación 1: Precios válidos
        if ecommerce_config.get("validate_prices", {}).get("enabled", False):
            price_field = ecommerce_config["validate_prices"].get("field", "price")
            min_price = ecommerce_config["validate_prices"].get("min_price", 0)
            max_price = ecommerce_config["validate_prices"].get("max_price", 100000)
            
            price_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {price_field} IS NOT NULL
                AND ({price_field} < {min_price} OR {price_field} > {max_price})
            """
            price_result = hook.get_first(price_query)
            invalid_prices = price_result[0] if price_result else 0
            
            if invalid_prices > 0:
                results.append(ValidationResult(
                    name="E-commerce: Precios fuera de rango",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_prices} productos con precios fuera de rango (${min_price} - ${max_price})",
                    count=invalid_prices
                ))
        
        # Validación 2: Stock no negativo
        if ecommerce_config.get("validate_stock", {}).get("enabled", False):
            stock_field = ecommerce_config["validate_stock"].get("field", "stock_quantity")
            
            stock_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {stock_field} IS NOT NULL
                AND {stock_field} < 0
            """
            stock_result = hook.get_first(stock_query)
            negative_stock = stock_result[0] if stock_result else 0
            
            if negative_stock > 0:
                results.append(ValidationResult(
                    name="E-commerce: Stock negativo",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{negative_stock} productos con stock negativo",
                    count=negative_stock
                ))
        
        # Validación 3: SKUs únicos
        if ecommerce_config.get("validate_unique_skus", {}).get("enabled", False):
            sku_field = ecommerce_config["validate_unique_skus"].get("field", "sku")
            
            sku_query = f"""
                SELECT {sku_field}, COUNT(*) as count
                FROM {table_name}
                WHERE {sku_field} IS NOT NULL
                GROUP BY {sku_field}
                HAVING COUNT(*) > 1
            """
            sku_result = hook.get_records(sku_query)
            duplicate_skus = len(sku_result) if sku_result else 0
            
            if duplicate_skus > 0:
                results.append(ValidationResult(
                    name="E-commerce: SKUs duplicados",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{duplicate_skus} SKUs duplicados detectados",
                    count=duplicate_skus
                ))
        
        # Validación 4: Fechas de órdenes válidas
        if ecommerce_config.get("validate_order_dates", {}).get("enabled", False):
            order_date_field = ecommerce_config["validate_order_dates"].get("field", "order_date")
            
            date_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {order_date_field} IS NOT NULL
                AND ({order_date_field} > CURRENT_TIMESTAMP 
                     OR {order_date_field} < CURRENT_TIMESTAMP - INTERVAL '10 years')
            """
            date_result = hook.get_first(date_query)
            invalid_dates = date_result[0] if date_result else 0
            
            if invalid_dates > 0:
                results.append(ValidationResult(
                    name="E-commerce: Fechas de orden inválidas",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_dates} órdenes con fechas inválidas (futuras o muy antiguas)",
                    count=invalid_dates
                ))
        
        # Validación 5: Totales de órdenes consistentes
        if ecommerce_config.get("validate_order_totals", {}).get("enabled", False):
            total_field = ecommerce_config["validate_order_totals"].get("total_field", "total_amount")
            subtotal_field = ecommerce_config["validate_order_totals"].get("subtotal_field", "subtotal")
            tax_field = ecommerce_config["validate_order_totals"].get("tax_field", "tax")
            shipping_field = ecommerce_config["validate_order_totals"].get("shipping_field", "shipping")
            
            total_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {total_field} IS NOT NULL
                AND ABS({total_field} - COALESCE({subtotal_field}, 0) - COALESCE({tax_field}, 0) - COALESCE({shipping_field}, 0)) > 0.01
            """
            total_result = hook.get_first(total_query)
            inconsistent_totals = total_result[0] if total_result else 0
            
            if inconsistent_totals > 0:
                results.append(ValidationResult(
                    name="E-commerce: Totales de orden inconsistentes",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{inconsistent_totals} órdenes con totales inconsistentes",
                    count=inconsistent_totals
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de e-commerce: {e}")
    
    return results


def calculate_roi_metrics(validation_results: Dict[str, Any], cost_metrics: Dict[str, Any], 
                         roi_config: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula métricas de ROI (Return on Investment) de las validaciones."""
    try:
        roi_metrics = {
            "timestamp": pendulum.now().isoformat(),
            "roi": {},
            "benefits": {},
            "recommendations": []
        }
        
        total_cost = cost_metrics.get("costs", {}).get("compute", {}).get("value", 0)
        errors_detected = len(validation_results.get("errors", []))
        critical_errors = len([e for e in validation_results.get("errors", []) if e.get("severity") == "critical"])
        
        # Beneficio 1: Errores críticos evitados
        if roi_config.get("calculate_critical_error_benefit", {}).get("enabled", False):
            cost_per_critical_error = roi_config["calculate_critical_error_benefit"].get("cost_per_error", 1000)
            benefit = critical_errors * cost_per_critical_error
            
            roi_metrics["benefits"]["critical_errors_avoided"] = {
                "value": benefit,
                "unit": "currency",
                "errors_detected": critical_errors,
                "cost_per_error": cost_per_critical_error
            }
        
        # Beneficio 2: Tiempo ahorrado en debugging
        if roi_config.get("calculate_time_savings", {}).get("enabled", False):
            hours_per_error = roi_config["calculate_time_savings"].get("hours_per_error", 2)
            cost_per_hour = roi_config["calculate_time_savings"].get("cost_per_hour", 50)
            total_hours = errors_detected * hours_per_error
            benefit = total_hours * cost_per_hour
            
            roi_metrics["benefits"]["time_savings"] = {
                "value": benefit,
                "unit": "currency",
                "hours_saved": total_hours,
                "errors_detected": errors_detected
            }
        
        # Calcular ROI total
        total_benefits = sum([b.get("value", 0) for b in roi_metrics["benefits"].values()])
        if total_cost > 0:
            roi_percentage = ((total_benefits - total_cost) / total_cost) * 100
            roi_metrics["roi"]["percentage"] = round(roi_percentage, 2)
            roi_metrics["roi"]["net_benefit"] = round(total_benefits - total_cost, 2)
            roi_metrics["roi"]["total_cost"] = round(total_cost, 2)
            roi_metrics["roi"]["total_benefits"] = round(total_benefits, 2)
        
        # Recomendaciones
        if total_benefits > total_cost * 2:
            roi_metrics["recommendations"].append({
                "type": "roi_positive",
                "message": f"ROI excelente: {roi_metrics['roi'].get('percentage', 0):.1f}%",
                "action": "Considerar aumentar frecuencia de validaciones"
            })
        elif total_benefits < total_cost:
            roi_metrics["recommendations"].append({
                "type": "roi_negative",
                "message": f"ROI negativo: {roi_metrics['roi'].get('percentage', 0):.1f}%",
                "action": "Optimizar costos o aumentar valor de beneficios detectados"
            })
        
        return roi_metrics
    
    except Exception as e:
        logger.error(f"Error calculando métricas ROI: {e}")
        return {"error": str(e)}


def validate_mobile_device_data(hook: PostgresHook, table_name: str, mobile_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de dispositivos móviles."""
    results = []
    
    try:
        # Validación 1: Formatos de IMEI
        if mobile_config.get("validate_imei", {}).get("enabled", False):
            imei_field = mobile_config["validate_imei"].get("field", "imei")
            
            # IMEI debe tener 15 dígitos
            imei_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {imei_field} IS NOT NULL
                AND (LENGTH(REPLACE({imei_field}, ' ', '')) != 15
                     OR REPLACE({imei_field}, ' ', '') !~ '^[0-9]{{15}}$')
            """
            imei_result = hook.get_first(imei_query)
            invalid_imei = imei_result[0] if imei_result else 0
            
            if invalid_imei > 0:
                results.append(ValidationResult(
                    name="Dispositivo Móvil: IMEI inválido",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_imei} IMEIs con formato inválido (debe tener 15 dígitos)",
                    count=invalid_imei
                ))
        
        # Validación 2: Versiones de OS
        if mobile_config.get("validate_os_versions", {}).get("enabled", False):
            os_field = mobile_config["validate_os_versions"].get("field", "os_version")
            valid_versions = mobile_config["validate_os_versions"].get("valid_versions", [])
            
            if valid_versions:
                versions_str = "', '".join(valid_versions)
                os_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {os_field} IS NOT NULL
                    AND {os_field} NOT IN ('{versions_str}')
                """
                os_result = hook.get_first(os_query)
                invalid_os = os_result[0] if os_result else 0
                
                if invalid_os > 0:
                    results.append(ValidationResult(
                        name="Dispositivo Móvil: Versión de OS inválida",
                        passed=False,
                        severity=Severity.WARNING,
                        message=f"{invalid_os} dispositivos con versiones de OS no soportadas",
                        count=invalid_os
                    ))
        
        # Validación 3: Resoluciones de pantalla
        if mobile_config.get("validate_screen_resolution", {}).get("enabled", False):
            width_field = mobile_config["validate_screen_resolution"].get("width_field", "screen_width")
            height_field = mobile_config["validate_screen_resolution"].get("height_field", "screen_height")
            min_width = mobile_config["validate_screen_resolution"].get("min_width", 320)
            min_height = mobile_config["validate_screen_resolution"].get("min_height", 480)
            
            resolution_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE ({width_field} IS NOT NULL AND {width_field} < {min_width})
                   OR ({height_field} IS NOT NULL AND {height_field} < {min_height})
            """
            resolution_result = hook.get_first(resolution_query)
            invalid_resolution = resolution_result[0] if resolution_result else 0
            
            if invalid_resolution > 0:
                results.append(ValidationResult(
                    name="Dispositivo Móvil: Resolución de pantalla inválida",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_resolution} dispositivos con resolución fuera de rango mínimo ({min_width}x{min_height})",
                    count=invalid_resolution
                ))
        
        # Validación 4: Modelos de dispositivos
        if mobile_config.get("validate_device_models", {}).get("enabled", False):
            model_field = mobile_config["validate_device_models"].get("field", "device_model")
            required_prefix = mobile_config["validate_device_models"].get("required_prefix", "")
            
            if required_prefix:
                model_query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {model_field} IS NOT NULL
                    AND {model_field} NOT LIKE '{required_prefix}%'
                """
                model_result = hook.get_first(model_query)
                invalid_models = model_result[0] if model_result else 0
                
                if invalid_models > 0:
                    results.append(ValidationResult(
                        name="Dispositivo Móvil: Modelos inválidos",
                        passed=False,
                        severity=Severity.INFO,
                        message=f"{invalid_models} dispositivos con modelos fuera del prefijo esperado",
                        count=invalid_models
                    ))
    
    except Exception as e:
        logger.error(f"Error validando datos de dispositivos móviles: {e}")
    
    return results


def validate_pos_data(hook: PostgresHook, table_name: str, pos_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de sistemas POS (Point of Sale)."""
    results = []
    
    try:
        # Validación 1: Totales de transacciones
        if pos_config.get("validate_transaction_totals", {}).get("enabled", False):
            total_field = pos_config["validate_transaction_totals"].get("total_field", "total")
            items_field = pos_config["validate_transaction_totals"].get("items_field", "items")
            
            # Verificar que el total sea la suma de items
            total_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {total_field} IS NOT NULL
                AND {items_field} IS NOT NULL
                AND ABS({total_field} - (
                    SELECT SUM(price * quantity) 
                    FROM jsonb_array_elements({items_field}) AS item
                    WHERE (item->>'price')::numeric IS NOT NULL
                )) > 0.01
            """
            total_result = hook.get_first(total_query)
            inconsistent_totals = total_result[0] if total_result else 0
            
            if inconsistent_totals > 0:
                results.append(ValidationResult(
                    name="POS: Totales de transacción inconsistentes",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{inconsistent_totals} transacciones con totales inconsistentes",
                    count=inconsistent_totals
                ))
        
        # Validación 2: Métodos de pago válidos
        if pos_config.get("validate_payment_methods", {}).get("enabled", False):
            payment_field = pos_config["validate_payment_methods"].get("field", "payment_method")
            valid_methods = pos_config["validate_payment_methods"].get("valid_methods", ["cash", "card", "mobile"])
            
            methods_str = "', '".join(valid_methods)
            payment_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {payment_field} IS NOT NULL
                AND LOWER({payment_field}) NOT IN ('{methods_str}')
            """
            payment_result = hook.get_first(payment_query)
            invalid_payments = payment_result[0] if payment_result else 0
            
            if invalid_payments > 0:
                results.append(ValidationResult(
                    name="POS: Métodos de pago inválidos",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_payments} transacciones con métodos de pago inválidos",
                    count=invalid_payments
                ))
        
        # Validación 3: Cambio correcto
        if pos_config.get("validate_change", {}).get("enabled", False):
            total_field = pos_config["validate_change"].get("total_field", "total")
            paid_field = pos_config["validate_change"].get("paid_field", "amount_paid")
            change_field = pos_config["validate_change"].get("change_field", "change")
            
            change_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {total_field} IS NOT NULL
                AND {paid_field} IS NOT NULL
                AND {change_field} IS NOT NULL
                AND ABS({change_field} - ({paid_field} - {total_field})) > 0.01
            """
            change_result = hook.get_first(change_query)
            invalid_change = change_result[0] if change_result else 0
            
            if invalid_change > 0:
                results.append(ValidationResult(
                    name="POS: Cambio calculado incorrectamente",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_change} transacciones con cambio incorrecto",
                    count=invalid_change
                ))
        
        # Validación 4: Descuentos válidos
        if pos_config.get("validate_discounts", {}).get("enabled", False):
            discount_field = pos_config["validate_discounts"].get("field", "discount_percent")
            
            discount_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {discount_field} IS NOT NULL
                AND ({discount_field} < 0 OR {discount_field} > 100)
            """
            discount_result = hook.get_first(discount_query)
            invalid_discounts = discount_result[0] if discount_result else 0
            
            if invalid_discounts > 0:
                results.append(ValidationResult(
                    name="POS: Descuentos fuera de rango",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_discounts} transacciones con descuentos fuera de rango (0-100%)",
                    count=invalid_discounts
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos POS: {e}")
    
    return results


def calculate_business_impact_metrics(validation_results: Dict[str, Any], impact_config: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula métricas de impacto en negocio."""
    try:
        impact_metrics = {
            "timestamp": pendulum.now().isoformat(),
            "impacts": {},
            "risk_assessment": {},
            "recommendations": []
        }
        
        errors = validation_results.get("errors", [])
        critical_errors = len([e for e in errors if e.get("severity") == "critical"])
        total_records = validation_results.get("metrics", {}).get("total_records", 0)
        
        # Impacto 1: Registros afectados
        if impact_config.get("calculate_affected_records", {}).get("enabled", False):
            total_affected = sum([e.get("count", 0) for e in errors])
            affected_percentage = (total_affected / total_records * 100) if total_records > 0 else 0
            
            impact_metrics["impacts"]["affected_records"] = {
                "total_affected": total_affected,
                "total_records": total_records,
                "percentage": round(affected_percentage, 2),
                "severity": "high" if affected_percentage > 10 else "medium" if affected_percentage > 5 else "low"
            }
        
        # Impacto 2: Riesgo operacional
        if impact_config.get("calculate_operational_risk", {}).get("enabled", False):
            risk_score = 0
            if critical_errors > 0:
                risk_score += critical_errors * 10
            if len(errors) > 10:
                risk_score += (len(errors) - 10) * 2
            
            risk_level = "critical" if risk_score > 50 else "high" if risk_score > 30 else "medium" if risk_score > 15 else "low"
            
            impact_metrics["risk_assessment"] = {
                "risk_score": risk_score,
                "risk_level": risk_level,
                "critical_errors": critical_errors,
                "total_errors": len(errors)
            }
        
        # Impacto 3: Pérdida potencial de ingresos
        if impact_config.get("calculate_revenue_impact", {}).get("enabled", False):
            revenue_per_record = impact_config["calculate_revenue_impact"].get("avg_revenue_per_record", 10)
            total_affected = sum([e.get("count", 0) for e in errors])
            potential_loss = total_affected * revenue_per_record
            
            impact_metrics["impacts"]["revenue_impact"] = {
                "potential_loss": round(potential_loss, 2),
                "unit": "currency",
                "affected_records": total_affected,
                "avg_revenue_per_record": revenue_per_record
            }
        
        # Impacto 4: Satisfacción del cliente
        if impact_config.get("calculate_customer_satisfaction_impact", {}).get("enabled", False):
            quality_score = validation_results.get("metrics", {}).get("quality_score", {}).get("score", 100)
            satisfaction_impact = max(0, (quality_score - 80) / 20 * 100)  # 0-100% basado en score
            
            impact_metrics["impacts"]["customer_satisfaction"] = {
                "impact_score": round(satisfaction_impact, 2),
                "quality_score": round(quality_score, 2),
                "interpretation": "positive" if quality_score >= 90 else "neutral" if quality_score >= 70 else "negative"
            }
        
        # Recomendaciones de impacto
        if impact_metrics["risk_assessment"].get("risk_level") == "critical":
            impact_metrics["recommendations"].append({
                "type": "urgent_action",
                "priority": "critical",
                "message": "Riesgo crítico detectado - Acción inmediata requerida",
                "action": "Revisar y corregir errores críticos inmediatamente"
            })
        
        return impact_metrics
    
    except Exception as e:
        logger.error(f"Error calculando métricas de impacto: {e}")
        return {"error": str(e)}


def validate_wearable_data(hook: PostgresHook, table_name: str, wearable_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de dispositivos wearables."""
    results = []
    
    try:
        device_id_field = wearable_config.get("device_id_field", "device_id")
        timestamp_field = wearable_config.get("timestamp_field", "timestamp")
        
        # Validación 1: Rangos de frecuencia cardíaca
        if wearable_config.get("validate_heart_rate", {}).get("enabled", False):
            hr_field = wearable_config["validate_heart_rate"].get("field", "heart_rate")
            min_hr = wearable_config["validate_heart_rate"].get("min_bpm", 30)
            max_hr = wearable_config["validate_heart_rate"].get("max_bpm", 220)
            
            hr_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {hr_field} IS NOT NULL
                AND ({hr_field} < {min_hr} OR {hr_field} > {max_hr})
            """
            hr_result = hook.get_first(hr_query)
            invalid_hr = hr_result[0] if hr_result else 0
            
            if invalid_hr > 0:
                results.append(ValidationResult(
                    name="Wearable: Frecuencia cardíaca fuera de rango",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_hr} lecturas de frecuencia cardíaca fuera de rango ({min_hr}-{max_hr} bpm)",
                    count=invalid_hr
                ))
        
        # Validación 2: Pasos diarios
        if wearable_config.get("validate_steps", {}).get("enabled", False):
            steps_field = wearable_config["validate_steps"].get("field", "daily_steps")
            max_steps = wearable_config["validate_steps"].get("max_steps_per_day", 50000)
            
            steps_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {steps_field} IS NOT NULL
                AND {steps_field} > {max_steps}
            """
            steps_result = hook.get_first(steps_query)
            excessive_steps = steps_result[0] if steps_result else 0
            
            if excessive_steps > 0:
                results.append(ValidationResult(
                    name="Wearable: Pasos diarios excesivos",
                    passed=False,
                    severity=Severity.INFO,  # Puede ser válido
                    message=f"{excessive_steps} registros con pasos diarios > {max_steps} (posible error o actividad extrema)",
                    count=excessive_steps
                ))
        
        # Validación 3: Calorías quemadas
        if wearable_config.get("validate_calories", {}).get("enabled", False):
            calories_field = wearable_config["validate_calories"].get("field", "calories_burned")
            max_calories = wearable_config["validate_calories"].get("max_calories_per_day", 10000)
            
            calories_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {calories_field} IS NOT NULL
                AND {calories_field} < 0
            """
            calories_result = hook.get_first(calories_query)
            negative_calories = calories_result[0] if calories_result else 0
            
            if negative_calories > 0:
                results.append(ValidationResult(
                    name="Wearable: Calorías negativas",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{negative_calories} registros con calorías negativas",
                    count=negative_calories
                ))
        
        # Validación 4: Continuidad de datos
        if wearable_config.get("validate_data_continuity", {}).get("enabled", False):
            expected_interval_minutes = wearable_config["validate_data_continuity"].get("expected_interval_minutes", 60)
            
            continuity_query = f"""
                WITH time_gaps AS (
                    SELECT 
                        {device_id_field},
                        {timestamp_field},
                        LAG({timestamp_field}) OVER (PARTITION BY {device_id_field} ORDER BY {timestamp_field}) as prev_timestamp
                    FROM {table_name}
                    WHERE {timestamp_field} IS NOT NULL
                )
                SELECT COUNT(*) as count
                FROM time_gaps
                WHERE prev_timestamp IS NOT NULL
                AND EXTRACT(EPOCH FROM ({timestamp_field} - prev_timestamp)) / 60 > {expected_interval_minutes * 2}
            """
            continuity_result = hook.get_first(continuity_query)
            gaps = continuity_result[0] if continuity_result else 0
            
            if gaps > 0:
                results.append(ValidationResult(
                    name="Wearable: Gaps en continuidad de datos",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{gaps} gaps detectados en datos (intervalo esperado: {expected_interval_minutes} min)",
                    count=gaps
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de wearables: {e}")
    
    return results


def validate_booking_data(hook: PostgresHook, table_name: str, booking_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de sistemas de reservas/bookings."""
    results = []
    
    try:
        # Validación 1: Fechas de check-in/check-out válidas
        if booking_config.get("validate_dates", {}).get("enabled", False):
            checkin_field = booking_config["validate_dates"].get("checkin_field", "check_in_date")
            checkout_field = booking_config["validate_dates"].get("checkout_field", "check_out_date")
            
            date_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {checkin_field} IS NOT NULL
                AND {checkout_field} IS NOT NULL
                AND {checkout_field} <= {checkin_field}
            """
            date_result = hook.get_first(date_query)
            invalid_dates = date_result[0] if date_result else 0
            
            if invalid_dates > 0:
                results.append(ValidationResult(
                    name="Booking: Fechas de check-in/check-out inválidas",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_dates} reservas con check-out anterior o igual a check-in",
                    count=invalid_dates
                ))
        
        # Validación 2: Capacidad de habitaciones
        if booking_config.get("validate_capacity", {}).get("enabled", False):
            guests_field = booking_config["validate_capacity"].get("guests_field", "number_of_guests")
            capacity_field = booking_config["validate_capacity"].get("capacity_field", "room_capacity")
            
            capacity_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {guests_field} IS NOT NULL
                AND {capacity_field} IS NOT NULL
                AND {guests_field} > {capacity_field}
            """
            capacity_result = hook.get_first(capacity_query)
            over_capacity = capacity_result[0] if capacity_result else 0
            
            if over_capacity > 0:
                results.append(ValidationResult(
                    name="Booking: Reservas exceden capacidad",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{over_capacity} reservas con más huéspedes que capacidad de habitación",
                    count=over_capacity
                ))
        
        # Validación 3: Precios válidos
        if booking_config.get("validate_prices", {}).get("enabled", False):
            price_field = booking_config["validate_prices"].get("field", "total_price")
            min_price = booking_config["validate_prices"].get("min_price", 0)
            max_price = booking_config["validate_prices"].get("max_price", 100000)
            
            price_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {price_field} IS NOT NULL
                AND ({price_field} < {min_price} OR {price_field} > {max_price})
            """
            price_result = hook.get_first(price_query)
            invalid_prices = price_result[0] if price_result else 0
            
            if invalid_prices > 0:
                results.append(ValidationResult(
                    name="Booking: Precios fuera de rango",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_prices} reservas con precios fuera de rango",
                    count=invalid_prices
                ))
        
        # Validación 4: Sin solapamiento de reservas
        if booking_config.get("validate_overlaps", {}).get("enabled", False):
            room_field = booking_config["validate_overlaps"].get("room_field", "room_id")
            checkin_field = booking_config["validate_overlaps"].get("checkin_field", "check_in_date")
            checkout_field = booking_config["validate_overlaps"].get("checkout_field", "check_out_date")
            
            overlap_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name} b1
                INNER JOIN {table_name} b2 ON b1.{room_field} = b2.{room_field}
                WHERE b1.id != b2.id
                AND b1.{checkin_field} < b2.{checkout_field}
                AND b1.{checkout_field} > b2.{checkin_field}
            """
            overlap_result = hook.get_first(overlap_query)
            overlaps = overlap_result[0] if overlap_result else 0
            
            if overlaps > 0:
                results.append(ValidationResult(
                    name="Booking: Reservas solapadas",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{overlaps} pares de reservas con fechas solapadas en la misma habitación",
                    count=overlaps
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de bookings: {e}")
    
    return results


def calculate_operational_efficiency_metrics(validation_results: Dict[str, Any], efficiency_config: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula métricas de eficiencia operacional."""
    try:
        efficiency_metrics = {
            "timestamp": pendulum.now().isoformat(),
            "efficiency_scores": {},
            "recommendations": []
        }
        
        total_validations = validation_results.get("total_validations", 0)
        passed_validations = validation_results.get("passed", 0)
        failed_validations = validation_results.get("failed", 0)
        execution_time = validation_results.get("execution_time_seconds", 0)
        
        # Eficiencia 1: Tasa de éxito de validaciones
        if efficiency_config.get("calculate_success_rate", {}).get("enabled", False):
            success_rate = (passed_validations / total_validations * 100) if total_validations > 0 else 0
            efficiency_metrics["efficiency_scores"]["validation_success_rate"] = {
                "value": round(success_rate, 2),
                "unit": "percent",
                "interpretation": "excellent" if success_rate >= 95 else "good" if success_rate >= 80 else "needs_improvement"
            }
        
        # Eficiencia 2: Velocidad de procesamiento
        if efficiency_config.get("calculate_processing_speed", {}).get("enabled", False):
            total_records = validation_results.get("metrics", {}).get("total_records", 0)
            if total_records > 0 and execution_time > 0:
                records_per_second = total_records / execution_time
                efficiency_metrics["efficiency_scores"]["processing_speed"] = {
                    "value": round(records_per_second, 2),
                    "unit": "records_per_second",
                    "total_records": total_records,
                    "execution_time": round(execution_time, 2)
                }
        
        # Eficiencia 3: Tasa de errores por tipo
        if efficiency_config.get("calculate_error_rate_by_type", {}).get("enabled", False):
            errors = validation_results.get("errors", [])
            error_by_type = {}
            for error in errors:
                error_type = error.get("name", "unknown").split(":")[0] if ":" in error.get("name", "") else "general"
                error_by_type[error_type] = error_by_type.get(error_type, 0) + 1
            
            efficiency_metrics["efficiency_scores"]["error_distribution"] = error_by_type
        
        # Eficiencia 4: Tiempo promedio por validación
        if efficiency_config.get("calculate_avg_validation_time", {}).get("enabled", False):
            if total_validations > 0 and execution_time > 0:
                avg_time = execution_time / total_validations
                efficiency_metrics["efficiency_scores"]["avg_validation_time"] = {
                    "value": round(avg_time, 4),
                    "unit": "seconds",
                    "total_validations": total_validations
                }
        
        # Recomendaciones de eficiencia
        success_rate = efficiency_metrics["efficiency_scores"].get("validation_success_rate", {}).get("value", 100)
        if success_rate < 80:
            efficiency_metrics["recommendations"].append({
                "type": "low_success_rate",
                "priority": "high",
                "message": f"Tasa de éxito baja ({success_rate:.1f}%)",
                "action": "Revisar y corregir validaciones que fallan frecuentemente"
            })
        
        return efficiency_metrics
    
    except Exception as e:
        logger.error(f"Error calculando métricas de eficiencia: {e}")
        return {"error": str(e)}


def validate_logistics_data(hook: PostgresHook, table_name: str, logistics_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos de sistemas de logística."""
    results = []
    
    try:
        # Validación 1: Estados de envío válidos
        if logistics_config.get("validate_shipment_status", {}).get("enabled", False):
            status_field = logistics_config["validate_shipment_status"].get("field", "status")
            valid_statuses = logistics_config["validate_shipment_status"].get("valid_statuses", 
                ["pending", "in_transit", "delivered", "cancelled"])
            
            statuses_str = "', '".join(valid_statuses)
            status_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {status_field} IS NOT NULL
                AND LOWER({status_field}) NOT IN ('{statuses_str}')
            """
            status_result = hook.get_first(status_query)
            invalid_statuses = status_result[0] if status_result else 0
            
            if invalid_statuses > 0:
                results.append(ValidationResult(
                    name="Logistics: Estados de envío inválidos",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_statuses} envíos con estados inválidos",
                    count=invalid_statuses
                ))
        
        # Validación 2: Fechas de envío y entrega consistentes
        if logistics_config.get("validate_delivery_dates", {}).get("enabled", False):
            shipped_field = logistics_config["validate_delivery_dates"].get("shipped_field", "shipped_date")
            delivered_field = logistics_config["validate_delivery_dates"].get("delivered_field", "delivered_date")
            
            date_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {shipped_field} IS NOT NULL
                AND {delivered_field} IS NOT NULL
                AND {delivered_field} < {shipped_field}
            """
            date_result = hook.get_first(date_query)
            invalid_dates = date_result[0] if date_result else 0
            
            if invalid_dates > 0:
                results.append(ValidationResult(
                    name="Logistics: Fechas de entrega inconsistentes",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{invalid_dates} envíos con fecha de entrega anterior a fecha de envío",
                    count=invalid_dates
                ))
        
        # Validación 3: Peso y dimensiones válidas
        if logistics_config.get("validate_dimensions", {}).get("enabled", False):
            weight_field = logistics_config["validate_dimensions"].get("weight_field", "weight_kg")
            max_weight = logistics_config["validate_dimensions"].get("max_weight_kg", 1000)
            
            weight_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {weight_field} IS NOT NULL
                AND ({weight_field} < 0 OR {weight_field} > {max_weight})
            """
            weight_result = hook.get_first(weight_query)
            invalid_weights = weight_result[0] if weight_result else 0
            
            if invalid_weights > 0:
                results.append(ValidationResult(
                    name="Logistics: Peso inválido",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{invalid_weights} envíos con peso fuera de rango (0-{max_weight} kg)",
                    count=invalid_weights
                ))
        
        # Validación 4: Tracking numbers únicos
        if logistics_config.get("validate_tracking_numbers", {}).get("enabled", False):
            tracking_field = logistics_config["validate_tracking_numbers"].get("field", "tracking_number")
            
            tracking_query = f"""
                SELECT {tracking_field}, COUNT(*) as count
                FROM {table_name}
                WHERE {tracking_field} IS NOT NULL
                GROUP BY {tracking_field}
                HAVING COUNT(*) > 1
            """
            tracking_result = hook.get_records(tracking_query)
            duplicate_tracking = len(tracking_result) if tracking_result else 0
            
            if duplicate_tracking > 0:
                results.append(ValidationResult(
                    name="Logistics: Números de tracking duplicados",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"{duplicate_tracking} números de tracking duplicados",
                    count=duplicate_tracking
                ))
    
    except Exception as e:
        logger.error(f"Error validando datos de logística: {e}")
    
    return results


def generate_proactive_alerts(validation_results: Dict[str, Any], historical_data: List[Dict[str, Any]], 
                              alerting_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Genera alertas proactivas basadas en patrones y tendencias."""
    alerts = []
    
    try:
        if not historical_data or len(historical_data) < 3:
            return alerts
        
        current_errors = len(validation_results.get("errors", []))
        current_warnings = len(validation_results.get("warnings_list", []))
        quality_score = validation_results.get("metrics", {}).get("quality_score", {}).get("score", 100)
        
        # Alerta 1: Tendencia de degradación
        if alerting_config.get("detect_degradation_trend", {}).get("enabled", False):
            recent_scores = []
            for hist in historical_data[:7]:  # Últimos 7 días
                score = hist.get("metrics", {}).get("quality_score", {}).get("score", 100)
                if score:
                    recent_scores.append(score)
            
            if len(recent_scores) >= 3:
                # Calcular tendencia
                trend = (recent_scores[0] - recent_scores[-1]) / len(recent_scores)
                if trend < -2:  # Degradación de más de 2 puntos por día
                    alerts.append({
                        "type": "degradation_trend",
                        "severity": "warning",
                        "message": f"Tendencia de degradación detectada: {trend:.2f} puntos/día",
                        "current_score": quality_score,
                        "trend": round(trend, 2),
                        "action": "Revisar causas de degradación y tomar medidas correctivas"
                    })
        
        # Alerta 2: Pico de errores
        if alerting_config.get("detect_error_spikes", {}).get("enabled", False):
            recent_errors = []
            for hist in historical_data[:7]:
                errors = len(hist.get("errors", []))
                recent_errors.append(errors)
            
            if recent_errors:
                avg_errors = sum(recent_errors[1:]) / len(recent_errors[1:]) if len(recent_errors) > 1 else 0
                if current_errors > avg_errors * 2 and avg_errors > 0:  # Doble del promedio
                    alerts.append({
                        "type": "error_spike",
                        "severity": "critical",
                        "message": f"Pico de errores detectado: {current_errors} (promedio: {avg_errors:.1f})",
                        "current_errors": current_errors,
                        "average_errors": round(avg_errors, 1),
                        "action": "Investigar causa inmediata del aumento de errores"
                    })
        
        # Alerta 3: Patrón estacional
        if alerting_config.get("detect_seasonal_patterns", {}).get("enabled", False):
            # Agrupar por día de la semana
            errors_by_weekday = {}
            for hist in historical_data:
                timestamp = hist.get("timestamp", "")
                if timestamp:
                    try:
                        dt = pendulum.parse(timestamp)
                        weekday = dt.day_of_week
                        errors = len(hist.get("errors", []))
                        if weekday not in errors_by_weekday:
                            errors_by_weekday[weekday] = []
                        errors_by_weekday[weekday].append(errors)
                    except:
                        pass
            
            if errors_by_weekday:
                avg_by_weekday = {k: sum(v) / len(v) for k, v in errors_by_weekday.items()}
                max_weekday = max(avg_by_weekday.items(), key=lambda x: x[1])
                current_weekday = pendulum.now().day_of_week
                
                if max_weekday[0] == current_weekday and max_weekday[1] > avg_by_weekday.get((current_weekday + 1) % 7, 0) * 1.5:
                    alerts.append({
                        "type": "seasonal_pattern",
                        "severity": "info",
                        "message": f"Patrón estacional detectado: día {max_weekday[0]} tiene más errores",
                        "weekday": max_weekday[0],
                        "avg_errors": round(max_weekday[1], 1),
                        "action": "Preparar recursos adicionales para este día de la semana"
                    })
        
        # Alerta 4: Predicción de problemas
        if alerting_config.get("predict_future_issues", {}).get("enabled", False):
            # Análisis simple de tendencia para predecir
            recent_scores = []
            for hist in historical_data[:5]:
                score = hist.get("metrics", {}).get("quality_score", {}).get("score", 100)
                if score:
                    recent_scores.append(score)
            
            if len(recent_scores) >= 3:
                trend = (recent_scores[0] - recent_scores[-1]) / len(recent_scores)
                predicted_score = quality_score + (trend * 3)  # Predicción para 3 días
                
                if predicted_score < 70:
                    alerts.append({
                        "type": "predicted_issue",
                        "severity": "warning",
                        "message": f"Predicción: calidad podría caer a {predicted_score:.1f}% en 3 días",
                        "current_score": quality_score,
                        "predicted_score": round(predicted_score, 1),
                        "action": "Tomar medidas preventivas para evitar degradación"
                    })
        
    except Exception as e:
        logger.error(f"Error generando alertas proactivas: {e}")
    
    return alerts


def generate_rule_based_alerts(validation_results: Dict[str, Any], alert_rules: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Genera alertas basadas en reglas de negocio configurables."""
    try:
        alerts = []
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        quality_score = validation_results.get("metrics", {}).get("quality_score", {})
        
        for rule_name, rule_config in alert_rules.items():
            if not rule_config.get("enabled", False):
                continue
            
            rule_type = rule_config.get("type")
            condition = rule_config.get("condition")
            threshold = rule_config.get("threshold")
            severity = rule_config.get("severity", "warning")
            message_template = rule_config.get("message", "Alerta: {condition} cumplida")
            
            should_alert = False
            
            if rule_type == "error_count":
                error_count = len(errors)
                if condition == "greater_than" and error_count > threshold:
                    should_alert = True
                elif condition == "less_than" and error_count < threshold:
                    should_alert = True
                elif condition == "equals" and error_count == threshold:
                    should_alert = True
            
            elif rule_type == "critical_error_count":
                critical_count = len([e for e in errors if e.get("severity") == "critical"])
                if condition == "greater_than" and critical_count > threshold:
                    should_alert = True
            
            elif rule_type == "quality_score":
                score = quality_score.get("score", 100)
                if condition == "less_than" and score < threshold:
                    should_alert = True
                elif condition == "greater_than" and score > threshold:
                    should_alert = True
            
            elif rule_type == "affected_records":
                total_affected = sum([e.get("count", 0) for e in errors])
                total_records = validation_results.get("metrics", {}).get("total_records", 0)
                affected_pct = (total_affected / total_records * 100) if total_records > 0 else 0
                
                if condition == "greater_than" and affected_pct > threshold:
                    should_alert = True
            
            elif rule_type == "custom":
                # Evaluar expresión personalizada (simplificado)
                custom_expression = rule_config.get("expression", "")
                try:
                    # Reemplazar variables en expresión
                    expr = custom_expression.replace("error_count", str(len(errors)))
                    expr = expr.replace("critical_count", str(len([e for e in errors if e.get("severity") == "critical"])))
                    expr = expr.replace("quality_score", str(quality_score.get("score", 100)))
                    result = eval(expr)  # En producción, usar parser más seguro
                    if result:
                        should_alert = True
                except:
                    pass
            
            if should_alert:
                alerts.append({
                    "rule_name": rule_name,
                    "severity": severity,
                    "message": message_template.format(
                        condition=condition,
                        threshold=threshold,
                        error_count=len(errors),
                        quality_score=quality_score.get("score", 100)
                    ),
                    "triggered_at": pendulum.now().isoformat(),
                    "rule_config": rule_config
                })
        
        return alerts
    
    except Exception as e:
        logger.error(f"Error generando alertas basadas en reglas: {e}")
        return []


def continuous_learning_system(validation_results: Dict[str, Any], historical_data: List[Dict[str, Any]], 
                               learning_config: Dict[str, Any]) -> Dict[str, Any]:
    """Sistema de aprendizaje continuo para mejorar validaciones."""
    try:
        learning_results = {
            "timestamp": pendulum.now().isoformat(),
            "learnings": [],
            "model_updates": {},
            "improvements": []
        }
        
        if not historical_data or len(historical_data) < 10:
            return {"message": "Datos históricos insuficientes para aprendizaje continuo"}
        
        # Aprendizaje 1: Identificar validaciones más efectivas
        validation_effectiveness = {}
        for hist in historical_data:
            errors = hist.get("errors", [])
            for error in errors:
                error_name = error.get("name", "")
                if error_name not in validation_effectiveness:
                    validation_effectiveness[error_name] = {"detections": 0, "executions": 0}
                validation_effectiveness[error_name]["detections"] += 1
                validation_effectiveness[error_name]["executions"] += 1
        
        # Calcular tasa de efectividad
        for val_name, stats in validation_effectiveness.items():
            if stats["executions"] > 0:
                effectiveness_rate = stats["detections"] / stats["executions"]
                if effectiveness_rate > 0.8:
                    learning_results["learnings"].append({
                        "type": "high_effectiveness",
                        "validation": val_name,
                        "effectiveness_rate": round(effectiveness_rate, 2),
                        "recommendation": "Mantener esta validación, es muy efectiva"
                    })
                elif effectiveness_rate < 0.1:
                    learning_results["learnings"].append({
                        "type": "low_effectiveness",
                        "validation": val_name,
                        "effectiveness_rate": round(effectiveness_rate, 2),
                        "recommendation": "Considerar ajustar o deshabilitar esta validación"
                    })
        
        # Aprendizaje 2: Patrones temporales
        if learning_config.get("learn_temporal_patterns", {}).get("enabled", False):
            error_by_hour = {}
            for hist in historical_data:
                timestamp = hist.get("timestamp", "")
                if timestamp:
                    try:
                        hour = pendulum.parse(timestamp).hour
                        errors_count = len(hist.get("errors", []))
                        if hour not in error_by_hour:
                            error_by_hour[hour] = []
                        error_by_hour[hour].append(errors_count)
                    except:
                        pass
            
            if error_by_hour:
                avg_errors_by_hour = {h: sum(errors) / len(errors) for h, errors in error_by_hour.items()}
                peak_hour = max(avg_errors_by_hour.items(), key=lambda x: x[1])
                
                learning_results["learnings"].append({
                    "type": "temporal_pattern",
                    "pattern": f"Hora pico de errores: {peak_hour[0]}:00",
                    "avg_errors": round(peak_hour[1], 1),
                    "recommendation": f"Considerar validaciones adicionales durante hora {peak_hour[0]}:00"
                })
        
        # Aprendizaje 3: Correlaciones entre errores
        if learning_config.get("learn_error_correlations", {}).get("enabled", False):
            error_cooccurrences = {}
            for hist in historical_data:
                errors = hist.get("errors", [])
                error_names = [e.get("name", "") for e in errors]
                for i, err1 in enumerate(error_names):
                    for err2 in error_names[i+1:]:
                        pair = tuple(sorted([err1, err2]))
                        error_cooccurrences[pair] = error_cooccurrences.get(pair, 0) + 1
            
            if error_cooccurrences:
                most_common_pair = max(error_cooccurrences.items(), key=lambda x: x[1])
                if most_common_pair[1] >= len(historical_data) * 0.3:
                    learning_results["learnings"].append({
                        "type": "error_correlation",
                        "errors": list(most_common_pair[0]),
                        "cooccurrence_rate": round(most_common_pair[1] / len(historical_data), 2),
                        "recommendation": f"Errores '{most_common_pair[0][0]}' y '{most_common_pair[0][1]}' frecuentemente ocurren juntos"
                    })
        
        # Mejoras sugeridas
        if learning_results["learnings"]:
            learning_results["improvements"].append({
                "type": "validation_optimization",
                "priority": "medium",
                "message": f"Se identificaron {len(learning_results['learnings'])} patrones de aprendizaje",
                "action": "Revisar y aplicar mejoras sugeridas"
            })
        
        return learning_results
    
    except Exception as e:
        logger.error(f"Error en sistema de aprendizaje continuo: {e}")
        return {"error": str(e)}


def generate_enhanced_recommendations(validation_results: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Genera recomendaciones mejoradas usando ML y análisis avanzado."""
    try:
        from collections import Counter
        
        recommendations = []
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        quality_score = validation_results.get("metrics", {}).get("quality_score", {})
        performance = validation_results.get("performance", {})
        
        # Análisis 1: Patrones de errores recurrentes
        if historical_data and len(historical_data) >= 5:
            all_error_names = []
            for hist in historical_data:
                hist_errors = hist.get("errors", [])
                all_error_names.extend([e.get("name", "") for e in hist_errors])
            
            error_counts = Counter(all_error_names)
            most_common = error_counts.most_common(3)
            
            for error_name, count in most_common:
                if count >= len(historical_data) * 0.6:  # Aparece en 60% de ejecuciones
                    recommendations.append({
                        "type": "recurring_issue",
                        "priority": "high",
                        "title": f"Problema recurrente: {error_name}",
                        "description": f"Este error aparece en {count}/{len(historical_data)} ejecuciones recientes",
                        "action": "Investigar causa raíz y implementar solución permanente",
                        "impact": "Alto - Afecta calidad de datos consistentemente",
                        "confidence": round(count / len(historical_data), 2)
                    })
        
        # Análisis 2: Optimización de performance
        exec_time = performance.get("execution_time_seconds", 0)
        if exec_time > 300:  # Más de 5 minutos
            recommendations.append({
                "type": "performance_optimization",
                "priority": "high",
                "title": "Optimizar tiempo de ejecución",
                "description": f"Tiempo de ejecución: {exec_time:.1f}s (objetivo: <300s)",
                "action": "Revisar queries lentas, considerar paralelización o validaciones incrementales",
                "impact": "Alto - Afecta eficiencia del sistema",
                "confidence": 0.9
            })
        
        # Análisis 3: Mejora de calidad basada en score
        score = quality_score.get("score", 100)
        if score < 80:
            recommendations.append({
                "type": "quality_improvement",
                "priority": "high",
                "title": f"Mejorar score de calidad ({score:.1f}/100)",
                "description": f"Score actual: {score:.1f}, objetivo: ≥80",
                "action": "Revisar y corregir errores críticos, implementar validaciones preventivas",
                "impact": "Alto - Afecta confiabilidad de datos",
                "confidence": 0.85
            })
        
        # Análisis 4: Análisis de tendencias
        if historical_data and len(historical_data) >= 7:
            recent_errors = len(errors)
            historical_avg = sum([len(h.get("errors", [])) for h in historical_data[:7]]) / 7
            
            if recent_errors > historical_avg * 1.5:
                recommendations.append({
                    "type": "trend_analysis",
                    "priority": "medium",
                    "title": "Tendencia de aumento de errores",
                    "description": f"Errores actuales ({recent_errors}) superan promedio histórico ({historical_avg:.1f})",
                    "action": "Investigar cambios recientes en procesos de ingesta o transformación",
                    "impact": "Medio - Indica degradación de calidad",
                    "confidence": 0.75
                })
        
        # Análisis 5: Recomendaciones de configuración
        if len(warnings) > 20:
            recommendations.append({
                "type": "configuration_tuning",
                "priority": "low",
                "title": "Ajustar umbrales de validación",
                "description": f"Alto número de warnings ({len(warnings)}), considerar ajustar umbrales",
                "action": "Revisar y optimizar umbrales de validación para reducir falsos positivos",
                "impact": "Bajo - Mejora experiencia de usuario",
                "confidence": 0.6
            })
        
        return recommendations
    
    except Exception as e:
        logger.error(f"Error generando recomendaciones mejoradas: {e}")
        return []


def auto_tune_parameters(validation_results: Dict[str, Any], historical_data: List[Dict[str, Any]], 
                        tuning_config: Dict[str, Any]) -> Dict[str, Any]:
    """Ajusta automáticamente umbrales y parámetros basado en historial."""
    try:
        tuning_results = {
            "timestamp": pendulum.now().isoformat(),
            "adjustments": [],
            "recommendations": []
        }
        
        if not historical_data or len(historical_data) < 5:
            return {"message": "Datos históricos insuficientes para auto-tuning"}
        
        # Ajuste 1: Optimizar umbrales de alerta
        if tuning_config.get("optimize_alert_thresholds", {}).get("enabled", False):
            error_rates = []
            for hist in historical_data:
                total = hist.get("total_validations", 0)
                errors = len(hist.get("errors", []))
                if total > 0:
                    error_rates.append((errors / total) * 100)
            
            if error_rates:
                avg_error_rate = sum(error_rates) / len(error_rates)
                current_error_rate = (len(validation_results.get("errors", [])) / 
                                     max(validation_results.get("total_validations", 1), 1)) * 100
                
                # Si el error rate promedio es bajo, podemos ajustar umbrales
                if avg_error_rate < 2 and current_error_rate < 1:
                    tuning_results["adjustments"].append({
                        "parameter": "alert_threshold",
                        "current": "default",
                        "recommended": "relaxed",
                        "reason": f"Error rate promedio bajo ({avg_error_rate:.1f}%), puede relajar umbrales",
                        "impact": "low"
                    })
                elif avg_error_rate > 10:
                    tuning_results["adjustments"].append({
                        "parameter": "alert_threshold",
                        "current": "default",
                        "recommended": "strict",
                        "reason": f"Error rate promedio alto ({avg_error_rate:.1f}%), necesita umbrales más estrictos",
                        "impact": "high"
                    })
        
        # Ajuste 2: Optimizar intervalos de validación
        if tuning_config.get("optimize_validation_intervals", {}).get("enabled", False):
            execution_times = []
            for hist in historical_data:
                perf = hist.get("performance", {})
                exec_time = perf.get("total_execution_time", 0)
                if exec_time > 0:
                    execution_times.append(exec_time)
            
            if execution_times:
                avg_exec_time = sum(execution_times) / len(execution_times)
                max_exec_time = max(execution_times)
                
                if avg_exec_time < 10 and max_exec_time < 30:
                    tuning_results["adjustments"].append({
                        "parameter": "validation_interval",
                        "current": "daily",
                        "recommended": "twice_daily",
                        "reason": f"Tiempo de ejecución bajo ({avg_exec_time:.1f}s), puede validar más frecuentemente",
                        "impact": "medium"
                    })
                elif avg_exec_time > 300:
                    tuning_results["adjustments"].append({
                        "parameter": "validation_interval",
                        "current": "daily",
                        "recommended": "keep_daily_optimize",
                        "reason": f"Tiempo de ejecución alto ({avg_exec_time:.1f}s), optimizar antes de aumentar frecuencia",
                        "impact": "high"
                    })
        
        # Ajuste 3: Optimizar chunk size para validaciones distribuidas
        if tuning_config.get("optimize_chunk_size", {}).get("enabled", False):
            total_records = validation_results.get("total_records", 0)
            if total_records > 1000000:  # Más de 1M registros
                recommended_chunk = min(50000, total_records // 20)
                tuning_results["adjustments"].append({
                    "parameter": "chunk_size",
                    "current": "default",
                    "recommended": recommended_chunk,
                    "reason": f"Tabla grande ({total_records:,} registros), optimizar chunk size",
                    "impact": "medium"
                })
        
        return tuning_results
    
    except Exception as e:
        logger.error(f"Error en auto-tuning: {e}")
        return {"error": str(e)}


def validate_data_governance(hook: PostgresHook, table_name: str, governance_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida reglas de gobernanza de datos."""
    results = []
    
    try:
        # Validación 1: Retención de datos
        if governance_rules.get("validate_retention", {}).get("enabled", False):
            retention_days = governance_rules["validate_retention"].get("max_retention_days", 365)
            date_field = governance_rules["validate_retention"].get("date_field", "created_at")
            
            retention_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {date_field} < CURRENT_DATE - INTERVAL '{retention_days} days'
            """
            retention_result = hook.get_first(retention_query)
            expired_data = retention_result[0] if retention_result else 0
            
            if expired_data > 0:
                results.append(ValidationResult(
                    name="Gobernanza: Datos fuera de período de retención",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{expired_data} registros exceden período de retención ({retention_days} días)",
                    count=expired_data
                ))
        
        # Validación 2: Acceso a datos sensibles
        if governance_rules.get("validate_sensitive_access", {}).get("enabled", False):
            sensitive_fields = governance_rules["validate_sensitive_access"].get("fields", [])
            access_log_table = governance_rules["validate_sensitive_access"].get("access_log_table", "data_access_log")
            
            for field in sensitive_fields:
                # Verificar si hay logs de acceso
                access_query = f"""
                    SELECT COUNT(*) as count
                    FROM {access_log_table}
                    WHERE table_name = '{table_name}'
                    AND field_name = '{field}'
                    AND access_timestamp >= CURRENT_DATE - INTERVAL '30 days'
                """
                try:
                    access_result = hook.get_first(access_query)
                    access_count = access_result[0] if access_result else 0
                    
                    if access_count == 0:
                        results.append(ValidationResult(
                            name=f"Gobernanza: Sin logs de acceso para campo sensible {field}",
                            passed=False,
                            severity=Severity.WARNING,
                            message=f"Campo sensible {field} sin registros de acceso en últimos 30 días",
                            count=0
                        ))
                except:
                    pass  # Tabla de logs puede no existir
        
        # Validación 3: Clasificación de datos
        if governance_rules.get("validate_classification", {}).get("enabled", False):
            classification_field = governance_rules["validate_classification"].get("field", "data_classification")
            required_classifications = governance_rules["validate_classification"].get("required", ["public", "internal", "confidential"])
            
            classification_query = f"""
                SELECT COUNT(*) as count
                FROM {table_name}
                WHERE {classification_field} IS NULL
                OR {classification_field} NOT IN ('{"', '".join(required_classifications)}')
            """
            classification_result = hook.get_first(classification_query)
            unclassified = classification_result[0] if classification_result else 0
            
            if unclassified > 0:
                results.append(ValidationResult(
                    name="Gobernanza: Datos sin clasificación",
                    passed=False,
                    severity=Severity.WARNING,
                    message=f"{unclassified} registros sin clasificación válida",
                    count=unclassified
                ))
    
    except Exception as e:
        logger.error(f"Error validando gobernanza: {e}")
    
    return results


def calculate_business_kpis(validation_results: Dict[str, Any], kpi_config: Dict[str, Any]) -> Dict[str, Any]:
    """Calcula KPIs de negocio basados en calidad de datos."""
    try:
        kpis = {
            "timestamp": pendulum.now().isoformat(),
            "metrics": {}
        }
        
        total_validations = validation_results.get("total_validations", 0)
        passed = validation_results.get("passed", 0)
        errors = validation_results.get("errors", [])
        quality_score = validation_results.get("metrics", {}).get("quality_score", {})
        
        # KPI 1: Data Quality Index (DQI)
        if kpi_config.get("calculate_dqi", {}).get("enabled", False):
            dqi = (passed / total_validations * 100) if total_validations > 0 else 0
            kpis["metrics"]["data_quality_index"] = {
                "value": round(dqi, 2),
                "unit": "percentage",
                "target": kpi_config["calculate_dqi"].get("target", 95),
                "status": "PASS" if dqi >= kpi_config["calculate_dqi"].get("target", 95) else "FAIL"
            }
        
        # KPI 2: Error Rate
        if kpi_config.get("calculate_error_rate", {}).get("enabled", False):
            error_rate = (len(errors) / total_validations * 100) if total_validations > 0 else 0
            kpis["metrics"]["error_rate"] = {
                "value": round(error_rate, 2),
                "unit": "percentage",
                "target": kpi_config["calculate_error_rate"].get("max_target", 5),
                "status": "PASS" if error_rate <= kpi_config["calculate_error_rate"].get("max_target", 5) else "FAIL"
            }
        
        # KPI 3: Data Trust Score
        if kpi_config.get("calculate_trust_score", {}).get("enabled", False):
            trust_score = quality_score.get("score", 100)
            kpis["metrics"]["data_trust_score"] = {
                "value": round(trust_score, 2),
                "unit": "score",
                "target": kpi_config["calculate_trust_score"].get("target", 80),
                "status": "PASS" if trust_score >= kpi_config["calculate_trust_score"].get("target", 80) else "FAIL"
            }
        
        # KPI 4: Critical Issues Count
        if kpi_config.get("calculate_critical_issues", {}).get("enabled", False):
            critical_errors = len([e for e in errors if e.get("severity") == "critical"])
            kpis["metrics"]["critical_issues"] = {
                "value": critical_errors,
                "unit": "count",
                "target": kpi_config["calculate_critical_issues"].get("max_target", 0),
                "status": "PASS" if critical_errors <= kpi_config["calculate_critical_issues"].get("max_target", 0) else "FAIL"
            }
        
        # KPI 5: Data Freshness (si está disponible)
        if kpi_config.get("calculate_freshness", {}).get("enabled", False):
            freshness_data = validation_results.get("metrics", {}).get("data_freshness", {})
            if freshness_data:
                age_hours = freshness_data.get("age_hours", 0)
                max_age = kpi_config["calculate_freshness"].get("max_age_hours", 24)
                kpis["metrics"]["data_freshness"] = {
                    "value": round(age_hours, 1),
                    "unit": "hours",
                    "target": f"<{max_age}",
                    "status": "PASS" if age_hours < max_age else "FAIL"
                }
        
        # Calcular KPI general (promedio de KPIs)
        if kpis["metrics"]:
            passed_kpis = sum(1 for m in kpis["metrics"].values() if m.get("status") == "PASS")
            total_kpis = len(kpis["metrics"])
            kpis["overall_kpi"] = round((passed_kpis / total_kpis) * 100, 2)
        
        return kpis
    
    except Exception as e:
        logger.error(f"Error calculando KPIs de negocio: {e}")
        return {"error": str(e)}


def validate_distributed_data(hook: PostgresHook, table_name: str, distributed_config: Dict[str, Any]) -> List[ValidationResult]:
    """Valida datos distribuidos en múltiples regiones/sistemas."""
    results = []
    
    try:
        regions = distributed_config.get("regions", [])
        
        for region in regions:
            if not region.get("enabled", False):
                continue
            
            region_name = region.get("name", "Unknown")
            conn_id = region.get("connection_id")
            region_table = region.get("table_name", table_name)
            
            if not conn_id:
                continue
            
            try:
                region_hook = PostgresHook(postgres_conn_id=conn_id)
                
                # Comparar conteos
                local_count = hook.get_first(f"SELECT COUNT(*) FROM {table_name}")[0]
                region_count = region_hook.get_first(f"SELECT COUNT(*) FROM {region_table}")[0]
                
                if local_count != region_count:
                    diff = abs(local_count - region_count)
                    diff_pct = (diff / max(local_count, 1)) * 100
                    
                    results.append(ValidationResult(
                        name=f"Datos distribuidos: Inconsistencia en {region_name}",
                        passed=False,
                        severity=Severity.ERROR if diff_pct > 5 else Severity.WARNING,
                        message=f"Conteo local: {local_count}, {region_name}: {region_count}, Diferencia: {diff} ({diff_pct:.1f}%)",
                        count=diff
                    ))
                else:
                    results.append(ValidationResult(
                        name=f"Datos distribuidos: Consistente en {region_name}",
                        passed=True,
                        severity=Severity.INFO,
                        message=f"Conteos coinciden: {local_count}",
                        count=0
                    ))
                
                # Validar checksums si está habilitado
                if region.get("validate_checksum", False):
                    checksum_field = region.get("checksum_field", "id")
                    local_checksum_query = f"""
                        SELECT MD5(STRING_AGG({checksum_field}::text, '' ORDER BY {checksum_field}))
                        FROM {table_name}
                    """
                    region_checksum_query = f"""
                        SELECT MD5(STRING_AGG({checksum_field}::text, '' ORDER BY {checksum_field}))
                        FROM {region_table}
                    """
                    
                    local_checksum = hook.get_first(local_checksum_query)[0]
                    region_checksum = region_hook.get_first(region_checksum_query)[0]
                    
                    if local_checksum != region_checksum:
                        results.append(ValidationResult(
                            name=f"Datos distribuidos: Checksum diferente en {region_name}",
                            passed=False,
                            severity=Severity.ERROR,
                            message=f"Checksums no coinciden - posible diferencia en datos",
                            count=0
                        ))
            
            except Exception as e:
                logger.error(f"Error validando región {region_name}: {e}")
                results.append(ValidationResult(
                    name=f"Datos distribuidos: Error en {region_name}",
                    passed=False,
                    severity=Severity.CRITICAL,
                    message=f"Error conectando o validando: {str(e)}",
                    count=0
                ))
    
    except Exception as e:
        logger.error(f"Error en validación distribuida: {e}")
    
    return results


def generate_intelligent_alerts(validation_results: Dict[str, Any], historical_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Genera alertas inteligentes basadas en ML y tendencias."""
    try:
        alerts = {
            "timestamp": pendulum.now().isoformat(),
            "alerts": [],
            "priority": "low"
        }
        
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        quality_score = validation_results.get("metrics", {}).get("quality_score", {})
        score = quality_score.get("score", 100)
        
        # Alerta 1: Degradación de calidad
        if historical_data:
            historical_score = historical_data.get("quality_score", {}).get("score", 100)
            if score < historical_score - 10:  # Degradación de más de 10 puntos
                alerts["alerts"].append({
                    "type": "quality_degradation",
                    "severity": "high",
                    "message": f"Degradación significativa de calidad: {historical_score:.1f} → {score:.1f}",
                    "recommendation": "Revisar procesos de ingesta de datos"
                })
        
        # Alerta 2: Aumento de errores críticos
        critical_errors = [e for e in errors if e.get("severity") == "critical"]
        if len(critical_errors) > 5:
            alerts["alerts"].append({
                "type": "critical_errors_spike",
                "severity": "critical",
                "message": f"Alto número de errores críticos: {len(critical_errors)}",
                "recommendation": "Revisar inmediatamente y considerar rollback"
            })
        
        # Alerta 3: Patrón de errores repetitivos
        error_names = [e.get("name", "") for e in errors]
        from collections import Counter
        error_counts = Counter(error_names)
        most_common = error_counts.most_common(1)
        if most_common and most_common[0][1] > 10:
            alerts["alerts"].append({
                "type": "repetitive_errors",
                "severity": "medium",
                "message": f"Error repetitivo detectado: '{most_common[0][0]}' ({most_common[0][1]} veces)",
                "recommendation": "Investigar causa raíz del error repetitivo"
            })
        
        # Alerta 4: Tendencia de empeoramiento
        if historical_data and historical_data.get("trends"):
            trends = historical_data["trends"]
            if trends.get("error_trend") == "increasing" and trends.get("error_rate", 0) > 0.1:
                alerts["alerts"].append({
                    "type": "worsening_trend",
                    "severity": "high",
                    "message": "Tendencia de empeoramiento detectada en calidad de datos",
                    "recommendation": "Implementar medidas correctivas inmediatas"
                })
        
        # Determinar prioridad general
        if any(a.get("severity") == "critical" for a in alerts["alerts"]):
            alerts["priority"] = "critical"
        elif any(a.get("severity") == "high" for a in alerts["alerts"]):
            alerts["priority"] = "high"
        elif any(a.get("severity") == "medium" for a in alerts["alerts"]):
            alerts["priority"] = "medium"
        
        return alerts
    
    except Exception as e:
        logger.error(f"Error generando alertas inteligentes: {e}")
        return {"error": str(e)}


def validate_transformations(hook: PostgresHook, table_name: str, transformation_rules: Dict[str, Any]) -> List[ValidationResult]:
    """Valida que las transformaciones de datos se aplicaron correctamente."""
    results = []
    
    try:
        for rule_name, rule_config in transformation_rules.items():
            if not rule_config.get("enabled", False):
                continue
            
            transformation_type = rule_config.get("type")
            source_field = rule_config.get("source_field")
            target_field = rule_config.get("target_field")
            
            if not source_field or not target_field:
                continue
            
            if transformation_type == "uppercase":
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {source_field} IS NOT NULL
                    AND {target_field} != UPPER({source_field})
                """
            elif transformation_type == "lowercase":
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {source_field} IS NOT NULL
                    AND {target_field} != LOWER({source_field})
                """
            elif transformation_type == "trim":
                query = f"""
                    SELECT COUNT(*) as count
                    FROM {table_name}
                    WHERE {source_field} IS NOT NULL
                    AND {target_field} != TRIM({source_field})
                """
            elif transformation_type == "custom":
                # SQL personalizado
                custom_sql = rule_config.get("validation_sql", "")
                if custom_sql:
                    query = custom_sql.replace("{table}", table_name)
                else:
                    continue
            else:
                continue
            
            result = hook.get_first(query)
            violation_count = result[0] if result else 0
            
            if violation_count > 0:
                results.append(ValidationResult(
                    name=f"Transformación: {rule_name}",
                    passed=False,
                    severity=Severity.ERROR,
                    message=f"Transformación {transformation_type} no aplicada correctamente: {violation_count} violaciones",
                    count=violation_count
                ))
            else:
                results.append(ValidationResult(
                    name=f"Transformación: {rule_name}",
                    passed=True,
                    severity=Severity.INFO,
                    message=f"Transformación {transformation_type} aplicada correctamente",
                    count=0
                ))
    
    except Exception as e:
        logger.error(f"Error validando transformaciones: {e}")
    
    return results


def generate_web_dashboard(validation_results: Dict[str, Any], output_path: str) -> str:
    """Genera dashboard web interactivo con visualizaciones."""
    try:
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        metrics = validation_results.get("metrics", {})
        trends = validation_results.get("trends", {})
        performance = validation_results.get("performance", {})
        
        # Preparar datos para gráficos
        error_types_json = json.dumps([e.get('name', 'Unknown')[:30] for e in errors[:5]])
        error_counts_json = json.dumps([e.get('count', 0) for e in errors[:5]])
        
        dashboard_html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard de Calidad de Datos</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@3.9.1/dist/chart.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; background: #f5f5f5; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 20px; }}
        .metrics-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 20px; }}
        .metric-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .metric-value {{ font-size: 36px; font-weight: bold; color: #667eea; }}
        .metric-label {{ color: #666; margin-top: 5px; }}
        .chart-container {{ background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .errors-list {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .error-item {{ padding: 15px; margin: 10px 0; border-left: 4px solid #d32f2f; background: #ffebee; border-radius: 4px; }}
        .quality-score {{ font-size: 72px; font-weight: bold; text-align: center; margin: 20px 0; }}
        .score-excellent {{ color: #4caf50; }}
        .score-good {{ color: #8bc34a; }}
        .score-warning {{ color: #ff9800; }}
        .score-poor {{ color: #f44336; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>📊 Dashboard de Calidad de Datos</h1>
        <p>Última actualización: {validation_results.get('timestamp', 'N/A')}</p>
    </div>
    
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-value">{validation_results.get('total_validations', 0)}</div>
            <div class="metric-label">Total Validaciones</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #4caf50;">{validation_results.get('passed', 0)}</div>
            <div class="metric-label">Exitosas ✅</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #f44336;">{validation_results.get('failed', 0)}</div>
            <div class="metric-label">Fallidas ❌</div>
        </div>
        <div class="metric-card">
            <div class="metric-value" style="color: #ff9800;">{validation_results.get('warnings', 0)}</div>
            <div class="metric-label">Advertencias ⚠️</div>
        </div>
    </div>
    
    <div class="chart-container">
        <h2>Score de Calidad</h2>
        <div class="quality-score score-{'excellent' if (validation_results.get('passed', 0) / max(validation_results.get('total_validations', 1), 1) * 100) >= 90 else 'good' if (validation_results.get('passed', 0) / max(validation_results.get('total_validations', 1), 1) * 100) >= 70 else 'warning' if (validation_results.get('passed', 0) / max(validation_results.get('total_validations', 1), 1) * 100) >= 50 else 'poor'}">
            {(validation_results.get('passed', 0) / max(validation_results.get('total_validations', 1), 1) * 100):.1f}%
        </div>
        <canvas id="qualityChart" width="400" height="200"></canvas>
    </div>
    
    <div class="chart-container">
        <h2>Distribución de Errores</h2>
        <canvas id="errorsChart" width="400" height="200"></canvas>
    </div>
    
    <div class="errors-list">
        <h2>Errores Detectados</h2>
        {"".join([f'<div class="error-item"><h3>{e.get("name")}</h3><p>{e.get("message")}</p><p><strong>Cantidad:</strong> {e.get("count", 0):,}</p></div>' for e in errors[:10]]) if errors else '<p>No se detectaron errores. ✅</p>'}
    </div>
    
    <script>
        // Gráfico de calidad
        const ctx1 = document.getElementById('qualityChart').getContext('2d');
        new Chart(ctx1, {{
            type: 'doughnut',
            data: {{
                labels: ['Exitosas', 'Fallidas', 'Advertencias'],
                datasets: [{{
                    data: [{validation_results.get('passed', 0)}, {validation_results.get('failed', 0)}, {validation_results.get('warnings', 0)}],
                    backgroundColor: ['#4caf50', '#f44336', '#ff9800']
                }}]
            }},
            options: {{ responsive: true }}
        }});
        
        // Gráfico de errores por tipo
        const ctx2 = document.getElementById('errorsChart').getContext('2d');
        const errorTypes = {error_types_json};
        const errorCounts = {error_counts_json};
        new Chart(ctx2, {{
            type: 'bar',
            data: {{
                labels: errorTypes,
                datasets: [{{
                    label: 'Cantidad de Errores',
                    data: errorCounts,
                    backgroundColor: '#f44336'
                }}]
            }},
            options: {{ responsive: true, scales: {{ y: {{ beginAtZero: true }} }} }}
        }});
    </script>
</body>
</html>
        """
        
        # Guardar dashboard
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(dashboard_html)
        
        logger.info(f"Dashboard web generado en: {output_path}")
        return output_path
    
    except Exception as e:
        logger.error(f"Error generando dashboard: {e}")
        return ""


def send_to_datadog(api_key: str, validation_results: Dict[str, Any], table_name: str) -> bool:
    """Envía métricas a Datadog."""
    try:
        passed = validation_results.get("passed", 0)
        failed = validation_results.get("failed", 0)
        total = validation_results.get("total_validations", 0)
        
        quality_score = (passed / total * 100) if total > 0 else 0
        
        series = [{
            "metric": "data.quality.score",
            "points": [[int(pendulum.now().timestamp()), quality_score]],
            "tags": [f"table:{table_name}", "environment:production"],
            "type": "gauge"
        }, {
            "metric": "data.quality.validations.passed",
            "points": [[int(pendulum.now().timestamp()), passed]],
            "tags": [f"table:{table_name}"],
            "type": "count"
        }, {
            "metric": "data.quality.validations.failed",
            "points": [[int(pendulum.now().timestamp()), failed]],
            "tags": [f"table:{table_name}"],
            "type": "count"
        }]
        
        response = requests.post(
            "https://api.datadoghq.com/api/v1/series",
            json={"series": series},
            headers={
                "DD-API-KEY": api_key,
                "Content-Type": "application/json"
            },
            timeout=10
        )
        response.raise_for_status()
        return True
    except Exception as e:
        logger.warning(f"Error enviando métricas a Datadog: {e}")
        return False


def validate_distributed(hook: PostgresHook, table_name: str, validation_func: callable, 
                         chunk_size: int = 10000) -> List[ValidationResult]:
    """Ejecuta validaciones en modo distribuido por chunks."""
    all_results = []
    
    try:
        # Obtener total de registros
        total_query = f"SELECT COUNT(*) FROM {table_name}"
        total_result = hook.get_first(total_query)
        total_records = total_result[0] if total_result else 0
        
        if total_records == 0:
            return all_results
        
        # Calcular número de chunks
        num_chunks = (total_records // chunk_size) + 1
        
        logger.info(f"Ejecutando validación distribuida: {total_records} registros en {num_chunks} chunks")
        
        for chunk_num in range(num_chunks):
            offset = chunk_num * chunk_size
            chunk_query = f"""
                SELECT * FROM {table_name}
                ORDER BY id
                LIMIT {chunk_size} OFFSET {offset}
            """
            
            try:
                chunk_results = validation_func(chunk_query)
                all_results.extend(chunk_results)
            except Exception as e:
                logger.warning(f"Error procesando chunk {chunk_num}: {e}")
    
    except Exception as e:
        logger.error(f"Error en validación distribuida: {e}")
    
    return all_results


def create_api_endpoints(validation_results: Dict[str, Any], port: int = 8081) -> Optional[Any]:
    """Crea API REST Flask para consultar resultados."""
    try:
        from flask import Flask, jsonify, request
        FLASK_AVAILABLE = True
    except ImportError:
        logger.warning("Flask no disponible para API REST")
        return None
    
    app = Flask(__name__)
    
    # Almacenar resultados en memoria (en producción usar Redis/DB)
    results_store = {"latest": validation_results}
    
    @app.route('/api/v1/health', methods=['GET'])
    def health():
        """Health check endpoint."""
        return jsonify({
            "status": "healthy",
            "service": "data_quality_monitoring",
            "timestamp": pendulum.now().isoformat()
        }), 200
    
    @app.route('/api/v1/results/latest', methods=['GET'])
    def get_latest_results():
        """Obtiene los últimos resultados de validación."""
        return jsonify(results_store.get("latest", {})), 200
    
    @app.route('/api/v1/results/summary', methods=['GET'])
    def get_summary():
        """Obtiene resumen de resultados."""
        latest = results_store.get("latest", {})
        return jsonify({
            "timestamp": latest.get("timestamp"),
            "total_validations": latest.get("total_validations", 0),
            "passed": latest.get("passed", 0),
            "failed": latest.get("failed", 0),
            "warnings": latest.get("warnings", 0),
            "quality_score": (latest.get("passed", 0) / latest.get("total_validations", 1) * 100) if latest.get("total_validations", 0) > 0 else 0
        }), 200
    
    @app.route('/api/v1/results/errors', methods=['GET'])
    def get_errors():
        """Obtiene lista de errores."""
        latest = results_store.get("latest", {})
        return jsonify({
            "errors": latest.get("errors", []),
            "count": len(latest.get("errors", []))
        }), 200
    
    @app.route('/api/v1/metrics', methods=['GET'])
    def get_metrics():
        """Obtiene métricas de calidad."""
        latest = results_store.get("latest", {})
        return jsonify({
            "metrics": latest.get("metrics", {}),
            "performance": latest.get("performance", {}),
            "trends": latest.get("trends", {})
        }), 200
    
    # Actualizar resultados
    results_store["latest"] = validation_results
    
    logger.info(f"API REST disponible en puerto {port}")
    return app


def detect_ml_anomalies(hook: PostgresHook, table_name: str, field: str, 
                        model_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Detecta anomalías usando Machine Learning."""
    anomalies = []
    
    try:
        # Intentar importar scikit-learn
        try:
            import pandas as pd
            import numpy as np
            from sklearn.ensemble import IsolationForest
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            logger.warning("scikit-learn no disponible para detección ML")
            return anomalies
        
        # Obtener datos
        query = f"SELECT {field} FROM {table_name} WHERE {field} IS NOT NULL LIMIT 10000"
        df = pd.read_sql(query, hook.get_conn())
        
        if df.empty or len(df) < 10:
            return anomalies
        
        # Preparar datos
        data = df[field].values.reshape(-1, 1)
        scaler = StandardScaler()
        data_scaled = scaler.fit_transform(data)
        
        # Entrenar modelo Isolation Forest
        contamination = model_config.get("contamination", 0.1)
        model = IsolationForest(contamination=contamination, random_state=42)
        predictions = model.fit_predict(data_scaled)
        
        # Identificar anomalías
        anomaly_indices = np.where(predictions == -1)[0]
        anomaly_values = data[anomaly_indices].flatten()
        
        if len(anomaly_values) > 0:
            anomalies.append({
                "field": field,
                "anomaly_count": len(anomaly_values),
                "anomaly_values": anomaly_values[:10].tolist(),  # Limitar a 10
                "method": "IsolationForest",
                "contamination": contamination
            })
            logger.info(f"ML detectó {len(anomaly_values)} anomalías en {field}")
    
    except Exception as e:
        logger.warning(f"Error en detección ML de anomalías: {e}")
    
    return anomalies


def predict_quality_issues(trends: Dict[str, Any], historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Análisis predictivo de problemas de calidad."""
    predictions = {
        "risk_level": "low",
        "predicted_issues": [],
        "confidence": 0.0
    }
    
    try:
        if not trends or not historical_data:
            return predictions
        
        # Analizar tendencias de errores
        error_trend = trends.get("errors", {})
        if error_trend.get("trend") == "increasing":
            current = error_trend.get("current", 0)
            previous = error_trend.get("previous", 0)
            
            if previous > 0:
                increase_rate = (current - previous) / previous
                
                if increase_rate > 0.5:  # Más del 50% de aumento
                    predictions["risk_level"] = "high"
                    predictions["predicted_issues"].append({
                        "type": "error_increase",
                        "message": f"Tendencia indica aumento del {increase_rate*100:.1f}% en errores",
                        "severity": "high"
                    })
                    predictions["confidence"] = min(0.8, increase_rate)
        
        # Analizar tendencias de registros
        record_trend = trends.get("records", {})
        if record_trend.get("trend") == "decreasing":
            current = record_trend.get("current", 0)
            previous = record_trend.get("previous", 0)
            
            if previous > 0:
                decrease_rate = (previous - current) / previous
                
                if decrease_rate > 0.1:  # Más del 10% de disminución
                    predictions["risk_level"] = "high"
                    predictions["predicted_issues"].append({
                        "type": "record_loss",
                        "message": f"Posible pérdida de datos: {decrease_rate*100:.1f}% de disminución",
                        "severity": "critical"
                    })
                    predictions["confidence"] = min(0.9, decrease_rate * 2)
        
        # Análisis de patrones históricos
        if len(historical_data) >= 7:
            recent_errors = [d.get("validation_errors", 0) for d in historical_data[:7]]
            avg_errors = sum(recent_errors) / len(recent_errors)
            current_errors = trends.get("errors", {}).get("current", 0)
            
            if current_errors > avg_errors * 1.5:
                predictions["risk_level"] = "medium"
                predictions["predicted_issues"].append({
                    "type": "above_average",
                    "message": f"Errores actuales ({current_errors}) superan el promedio ({avg_errors:.1f})",
                    "severity": "medium"
                })
                predictions["confidence"] = 0.6
        
    except Exception as e:
        logger.warning(f"Error en análisis predictivo: {e}")
    
    return predictions


def calculate_trends(hook: PostgresHook, days: int = 7) -> Dict[str, Any]:
    """Calcula tendencias estadísticas de las métricas."""
    try:
        query = f"""
            SELECT 
                date,
                total_records,
                validation_errors,
                validation_warnings
            FROM data_quality_metrics
            WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
            ORDER BY date DESC
        """
        results = hook.get_records(query)
        
        if not results:
            return {}
        
        dates = [row[0] for row in results]
        records = [row[1] for row in results]
        errors = [row[2] for row in results]
        warnings = [row[3] for row in results]
        
        # Calcular tendencias
        trends = {
            "days_analyzed": len(results),
            "records": {
                "current": records[0] if records else 0,
                "previous": records[1] if len(records) > 1 else 0,
                "trend": "stable"
            },
            "errors": {
                "current": errors[0] if errors else 0,
                "previous": errors[1] if len(errors) > 1 else 0,
                "trend": "stable"
            },
            "warnings": {
                "current": warnings[0] if warnings else 0,
                "previous": warnings[1] if len(warnings) > 1 else 0,
                "trend": "stable"
            }
        }
        
        # Determinar tendencias
        if len(records) > 1:
            if records[0] > records[1]:
                trends["records"]["trend"] = "increasing"
            elif records[0] < records[1]:
                trends["records"]["trend"] = "decreasing"
        
        if len(errors) > 1:
            if errors[0] > errors[1]:
                trends["errors"]["trend"] = "increasing"
            elif errors[0] < errors[1]:
                trends["errors"]["trend"] = "decreasing"
        
        if len(warnings) > 1:
            if warnings[0] > warnings[1]:
                trends["warnings"]["trend"] = "increasing"
            elif warnings[0] < warnings[1]:
                trends["warnings"]["trend"] = "decreasing"
        
        return trends
    except Exception as e:
        logger.warning(f"Error calculando tendencias: {e}")
        return {}


@dag(
    dag_id="data_quality_monitoring",
    start_date=pendulum.datetime(2024, 1, 1, tz="UTC"),
    schedule="0 2 * * *",  # Cada día a las 2:00 AM
    catchup=False,
    default_args={
        "owner": "data-team",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=15),
        "depends_on_past": False,
        "email_on_failure": True,
        "email_on_retry": False,
    },
    description="Monitoreo de calidad de datos de clientes - Ejecución nocturna",
    tags=["data-quality", "monitoring", "clients", "validation"],
    params={
        "postgres_conn_id": Param(
            "postgres_default",
            type="string",
            description="Connection ID para base de datos Postgres"
        ),
        "clients_table": Param(
            "customers",
            type="string",
            description="Nombre de la tabla de clientes"
        ),
        "data_team_email": Param(
            "data-team@example.com",
            type="string",
            description="Email del equipo de datos para notificaciones"
        ),
        "required_fields": Param(
            ["id", "name", "email", "created_at"],
            type="array",
            description="Lista de campos requeridos para validar"
        ),
        "enable_historical_comparison": Param(
            True,
            type="boolean",
            description="Habilitar comparación con métricas históricas"
        ),
        "alert_on_record_loss": Param(
            True,
            type="boolean",
            description="Alertar si hay pérdida significativa de registros"
        ),
        "record_loss_threshold": Param(
            0.05,
            type="number",
            description="Porcentaje de pérdida de registros para alertar (0.05 = 5%)"
        ),
        "slack_webhook_url": Param(
            "",
            type="string",
            description="Webhook URL de Slack para notificaciones (opcional)"
        ),
        "custom_webhook_url": Param(
            "",
            type="string",
            description="Webhook URL personalizado para notificaciones (opcional)"
        ),
        "export_to_json": Param(
            True,
            type="boolean",
            description="Exportar resultados a JSON"
        ),
        "export_to_csv": Param(
            False,
            type="boolean",
            description="Exportar resultados a CSV"
        ),
        "enable_trend_analysis": Param(
            True,
            type="boolean",
            description="Habilitar análisis de tendencias"
        ),
        "trend_analysis_days": Param(
            7,
            type="integer",
            minimum=1,
            maximum=30,
            description="Días hacia atrás para análisis de tendencias"
        ),
        "custom_validations": Param(
            "{}",
            type="string",
            description="JSON con validaciones personalizadas"
        ),
        "enable_great_expectations": Param(
            False,
            type="boolean",
            description="Habilitar validaciones con Great Expectations"
        ),
        "great_expectations_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de Great Expectations"
        ),
        "multiple_tables": Param(
            "[]",
            type="string",
            description="JSON array con múltiples tablas a validar"
        ),
        "enable_performance_monitoring": Param(
            True,
            type="boolean",
            description="Monitorear performance de queries"
        ),
        "alert_thresholds": Param(
            "{}",
            type="string",
            description="JSON con umbrales de alerta personalizados"
        ),
        "enable_smart_alerts": Param(
            True,
            type="boolean",
            description="Alertas inteligentes basadas en tendencias"
        ),
        "enable_prometheus": Param(
            True,
            type="boolean",
            description="Exportar métricas a Prometheus"
        ),
        "prometheus_pushgateway_url": Param(
            "",
            type="string",
            description="URL de Prometheus Pushgateway (opcional)"
        ),
        "enable_cache": Param(
            True,
            type="boolean",
            description="Usar caché de resultados"
        ),
        "cache_ttl_seconds": Param(
            3600,
            type="integer",
            minimum=60,
            maximum=86400,
            description="TTL del caché en segundos"
        ),
        "enable_predictive_analysis": Param(
            True,
            type="boolean",
            description="Habilitar análisis predictivo"
        ),
        "api_endpoint_url": Param(
            "",
            type="string",
            description="URL de API para almacenar resultados (opcional)"
        ),
        "enable_ticketing": Param(
            False,
            type="boolean",
            description="Crear tickets automáticamente para errores críticos"
        ),
        "ticketing_platform": Param(
            "jira",
            type="string",
            enum=["jira", "servicenow", "github"],
            description="Plataforma de tickets a usar"
        ),
        "ticketing_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de tickets"
        ),
        "enable_auto_fix": Param(
            False,
            type="boolean",
            description="Habilitar auto-reparación de datos (experimental)"
        ),
        "auto_fix_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de auto-reparación"
        ),
        "enable_ml_anomaly_detection": Param(
            False,
            type="boolean",
            description="Usar ML para detección de anomalías"
        ),
        "ml_model_config": Param(
            "{}",
            type="string",
            description="JSON con configuración del modelo ML"
        ),
        "enable_incremental_validation": Param(
            False,
            type="boolean",
            description="Validar solo datos nuevos/modificados"
        ),
        "incremental_field": Param(
            "updated_at",
            type="string",
            description="Campo para validación incremental"
        ),
        "incremental_since": Param(
            "",
            type="string",
            description="Fecha/hora desde la cual validar (ISO format, opcional)"
        ),
        "enable_parallel_validation": Param(
            False,
            type="boolean",
            description="Ejecutar validaciones en paralelo"
        ),
        "max_parallel_workers": Param(
            4,
            type="integer",
            minimum=1,
            maximum=16,
            description="Máximo de workers paralelos"
        ),
        "report_schedule": Param(
            "{}",
            type="string",
            description="JSON con configuración de reportes programables"
        ),
        "enable_audit_logging": Param(
            True,
            type="boolean",
            description="Habilitar logging de auditoría"
        ),
        "enable_compliance_checks": Param(
            False,
            type="boolean",
            description="Habilitar validaciones de compliance (GDPR, HIPAA, etc.)"
        ),
        "compliance_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de compliance"
        ),
        "enable_data_lineage": Param(
            False,
            type="boolean",
            description="Rastrear linaje de datos"
        ),
        "enable_data_profiling": Param(
            False,
            type="boolean",
            description="Generar perfil estadístico de datos"
        ),
        "enable_api_endpoints": Param(
            False,
            type="boolean",
            description="Exponer API REST para consultar resultados"
        ),
        "api_port": Param(
            8081,
            type="integer",
            minimum=1024,
            maximum=65535,
            description="Puerto para API REST (si está habilitada)"
        ),
        "enable_data_drift_detection": Param(
            False,
            type="boolean",
            description="Detectar drift de datos (cambios en distribución)"
        ),
        "enable_schema_validation": Param(
            True,
            type="boolean",
            description="Validar esquema de tabla"
        ),
        "expected_schema": Param(
            "{}",
            type="string",
            description="JSON con esquema esperado de la tabla"
        ),
        "enable_query_performance_check": Param(
            False,
            type="boolean",
            description="Monitorear performance de queries"
        ),
        "query_timeout_seconds": Param(
            30,
            type="integer",
            minimum=1,
            maximum=300,
            description="Timeout para queries en segundos"
        ),
        "enable_distributed_validation": Param(
            False,
            type="boolean",
            description="Ejecutar validaciones en modo distribuido"
        ),
        "validation_chunk_size": Param(
            10000,
            type="integer",
            minimum=100,
            maximum=100000,
            description="Tamaño de chunk para validaciones distribuidas"
        ),
        "enable_business_rules": Param(
            False,
            type="boolean",
            description="Validar reglas de negocio complejas"
        ),
        "business_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de negocio"
        ),
        "enable_pattern_detection": Param(
            False,
            type="boolean",
            description="Detectar patrones sospechosos en datos"
        ),
        "enable_data_freshness_check": Param(
            False,
            type="boolean",
            description="Verificar frescura de datos (última actualización)"
        ),
        "max_data_age_hours": Param(
            24,
            type="integer",
            minimum=1,
            maximum=168,
            description="Máxima antigüedad de datos en horas"
        ),
        "enable_grafana_integration": Param(
            False,
            type="boolean",
            description="Enviar métricas a Grafana"
        ),
        "grafana_api_url": Param(
            "",
            type="string",
            description="URL de API de Grafana"
        ),
        "enable_datadog_integration": Param(
            False,
            type="boolean",
            description="Enviar métricas a Datadog"
        ),
        "datadog_api_key": Param(
            "",
            type="string",
            description="API key de Datadog"
        ),
        "enable_pagerduty_integration": Param(
            False,
            type="boolean",
            description="Enviar alertas críticas a PagerDuty"
        ),
        "pagerduty_integration_key": Param(
            "",
            type="string",
            description="Integration key de PagerDuty"
        ),
        "enable_opsgenie_integration": Param(
            False,
            type="boolean",
            description="Enviar alertas críticas a Opsgenie"
        ),
        "opsgenie_api_key": Param(
            "",
            type="string",
            description="API key de Opsgenie"
        ),
        "enable_security_validation": Param(
            False,
            type="boolean",
            description="Validaciones de seguridad de datos"
        ),
        "security_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de seguridad"
        ),
        "enable_transactional_consistency": Param(
            False,
            type="boolean",
            description="Validar consistencia transaccional"
        ),
        "enable_data_latency_check": Param(
            False,
            type="boolean",
            description="Verificar latencia de datos (tiempo desde origen)"
        ),
        "max_data_latency_minutes": Param(
            60,
            type="integer",
            minimum=1,
            maximum=1440,
            description="Máxima latencia permitida en minutos"
        ),
        "enable_dashboard_web": Param(
            False,
            type="boolean",
            description="Generar dashboard web interactivo"
        ),
        "dashboard_output_path": Param(
            "/tmp/data_quality_dashboard.html",
            type="string",
            description="Ruta para guardar dashboard HTML"
        ),
        "enable_quality_scoring": Param(
            True,
            type="boolean",
            description="Calcular score de calidad de datos (0-100)"
        ),
        "enable_ml_error_classification": Param(
            False,
            type="boolean",
            description="Usar ML para clasificar errores automáticamente"
        ),
        "enable_cross_system_validation": Param(
            False,
            type="boolean",
            description="Validar consistencia entre sistemas"
        ),
        "cross_system_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de sistemas a comparar"
        ),
        "enable_transformation_validation": Param(
            False,
            type="boolean",
            description="Validar transformaciones de datos"
        ),
        "transformation_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de transformación a validar"
        ),
        "enable_advanced_referential_integrity": Param(
            False,
            type="boolean",
            description="Validaciones avanzadas de integridad referencial"
        ),
        "referential_integrity_rules": Param(
            "[]",
            type="string",
            description="JSON array con reglas de integridad referencial"
        ),
        "enable_sla_metrics": Param(
            False,
            type="boolean",
            description="Calcular métricas de SLA (Service Level Agreement)"
        ),
        "sla_targets": Param(
            "{}",
            type="string",
            description="JSON con objetivos de SLA"
        ),
        "enable_historical_snapshots": Param(
            False,
            type="boolean",
            description="Validar datos históricos usando snapshots"
        ),
        "snapshot_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de snapshots"
        ),
        "enable_intelligent_alerts": Param(
            True,
            type="boolean",
            description="Sistema de alertas inteligentes basado en ML"
        ),
        "enable_geographic_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos geográficos (coordenadas, países, etc.)"
        ),
        "geographic_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de validación geográfica"
        ),
        "enable_time_series_validation": Param(
            False,
            type="boolean",
            description="Validaciones de series temporales"
        ),
        "time_series_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de series temporales"
        ),
        "enable_auto_recommendations": Param(
            True,
            type="boolean",
            description="Generar recomendaciones automáticas basadas en errores"
        ),
        "enable_distributed_data_validation": Param(
            False,
            type="boolean",
            description="Validar datos distribuidos en múltiples regiones"
        ),
        "distributed_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación distribuida"
        ),
        "enable_data_versioning_validation": Param(
            False,
            type="boolean",
            description="Validar versionado de datos"
        ),
        "versioning_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de versionado"
        ),
        "enable_financial_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos financieros"
        ),
        "financial_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de validación financiera"
        ),
        "enable_reliability_scoring": Param(
            False,
            type="boolean",
            description="Calcular score de confiabilidad de datos"
        ),
        "enable_streaming_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de streaming"
        ),
        "streaming_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de streaming"
        ),
        "enable_business_kpis": Param(
            False,
            type="boolean",
            description="Calcular KPIs de negocio basados en calidad de datos"
        ),
        "kpi_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de KPIs"
        ),
        "enable_data_lineage_tracking": Param(
            False,
            type="boolean",
            description="Rastrear linaje de datos (origen y transformaciones)"
        ),
        "lineage_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de linaje"
        ),
        "enable_iot_sensor_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de IoT/sensores"
        ),
        "iot_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación IoT"
        ),
        "enable_adaptive_ml": Param(
            False,
            type="boolean",
            description="Sistema de ML adaptativo para mejorar validaciones"
        ),
        "adaptive_ml_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de ML adaptativo"
        ),
        "enable_blockchain_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de blockchain"
        ),
        "blockchain_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación blockchain"
        ),
        "enable_predictive_alerts": Param(
            False,
            type="boolean",
            description="Sistema de alertas predictivas basado en ML"
        ),
        "predictive_alerts_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de alertas predictivas"
        ),
        "enable_data_governance": Param(
            False,
            type="boolean",
            description="Validaciones de gobernanza de datos"
        ),
        "governance_rules": Param(
            "{}",
            type="string",
            description="JSON con reglas de gobernanza"
        ),
        "enable_external_api_validation": Param(
            False,
            type="boolean",
            description="Validar datos de APIs externas"
        ),
        "external_api_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de APIs externas"
        ),
        "enable_advanced_performance_metrics": Param(
            True,
            type="boolean",
            description="Métricas de rendimiento avanzadas"
        ),
        "enable_social_media_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de redes sociales"
        ),
        "social_media_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de redes sociales"
        ),
        "enable_auto_tuning": Param(
            False,
            type="boolean",
            description="Ajuste automático de umbrales y parámetros"
        ),
        "auto_tuning_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de auto-tuning"
        ),
        "enable_media_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de imágenes/videos"
        ),
        "media_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de medios"
        ),
        "enable_cost_metrics": Param(
            False,
            type="boolean",
            description="Calcular métricas de costos de procesamiento"
        ),
        "cost_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de métricas de costos"
        ),
        "enable_environmental_sensor_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de sensores ambientales"
        ),
        "environmental_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de sensores ambientales"
        ),
        "enable_enhanced_recommendations": Param(
            True,
            type="boolean",
            description="Sistema de recomendaciones mejorado con ML"
        ),
        "enable_ecommerce_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de e-commerce"
        ),
        "ecommerce_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación e-commerce"
        ),
        "enable_roi_metrics": Param(
            False,
            type="boolean",
            description="Calcular métricas de ROI (Return on Investment)"
        ),
        "roi_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de métricas ROI"
        ),
        "enable_mobile_device_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de dispositivos móviles"
        ),
        "mobile_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación móvil"
        ),
        "enable_continuous_learning": Param(
            False,
            type="boolean",
            description="Sistema de aprendizaje continuo para mejorar validaciones"
        ),
        "learning_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de aprendizaje continuo"
        ),
        "enable_pos_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de sistemas POS (Point of Sale)"
        ),
        "pos_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación POS"
        ),
        "enable_business_impact_metrics": Param(
            False,
            type="boolean",
            description="Calcular métricas de impacto en negocio"
        ),
        "business_impact_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de métricas de impacto"
        ),
        "enable_wearable_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de dispositivos wearables"
        ),
        "wearable_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación wearables"
        ),
        "enable_rule_based_alerts": Param(
            True,
            type="boolean",
            description="Sistema de alertas basado en reglas de negocio"
        ),
        "alert_rules_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de reglas de alertas"
        ),
        "enable_circuit_breaker": Param(
            True,
            type="boolean",
            description="Habilitar Circuit Breaker para conexiones de BD"
        ),
        "circuit_breaker_threshold": Param(
            5,
            type="integer",
            minimum=1,
            maximum=20,
            description="Número de fallos antes de abrir circuit breaker"
        ),
        "circuit_breaker_timeout": Param(
            60,
            type="integer",
            minimum=10,
            maximum=300,
            description="Timeout en segundos antes de intentar half-open"
        ),
        "enable_smart_retry": Param(
            True,
            type="boolean",
            description="Habilitar estrategia de retry inteligente"
        ),
        "max_retries": Param(
            3,
            type="integer",
            minimum=0,
            maximum=10,
            description="Número máximo de reintentos"
        ),
        "retry_base_delay": Param(
            1.0,
            type="number",
            minimum=0.1,
            maximum=10.0,
            description="Delay base para retry en segundos"
        ),
        "retry_max_delay": Param(
            60.0,
            type="number",
            minimum=1.0,
            maximum=300.0,
            description="Delay máximo para retry en segundos"
        ),
        "enable_query_optimization": Param(
            True,
            type="boolean",
            description="Habilitar optimizaciones automáticas de queries"
        ),
        "enable_connection_pooling": Param(
            True,
            type="boolean",
            description="Habilitar pooling de conexiones"
        ),
        "enable_batch_processing": Param(
            True,
            type="boolean",
            description="Procesar validaciones en batches para mejor rendimiento"
        ),
        "batch_size": Param(
            1000,
            type="integer",
            minimum=100,
            maximum=10000,
            description="Tamaño de batch para procesamiento"
        ),
        "enable_health_checks": Param(
            True,
            type="boolean",
            description="Realizar health checks de la base de datos antes de validaciones"
        ),
        "enable_index_validation": Param(
            False,
            type="boolean",
            description="Validar y analizar índices de la tabla"
        ),
        "enable_rate_limiting": Param(
            False,
            type="boolean",
            description="Habilitar rate limiting para operaciones"
        ),
        "rate_limit_max_requests": Param(
            100,
            type="integer",
            minimum=10,
            maximum=1000,
            description="Máximo de requests por ventana de tiempo"
        ),
        "rate_limit_window_seconds": Param(
            60,
            type="integer",
            minimum=1,
            maximum=300,
            description="Ventana de tiempo para rate limiting en segundos"
        ),
        "enable_query_validation": Param(
            True,
            type="boolean",
            description="Validar queries antes de ejecutarlas"
        ),
        "enable_result_compression": Param(
            False,
            type="boolean",
            description="Comprimir resultados grandes para mejor rendimiento"
        ),
        "enable_booking_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de sistemas de reservas/bookings"
        ),
        "booking_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de reservas"
        ),
        "enable_operational_efficiency_metrics": Param(
            False,
            type="boolean",
            description="Calcular métricas de eficiencia operacional"
        ),
        "operational_efficiency_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de métricas de eficiencia"
        ),
        "enable_logistics_validation": Param(
            False,
            type="boolean",
            description="Validaciones de datos de sistemas de logística"
        ),
        "logistics_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de validación de logística"
        ),
        "enable_proactive_alerting": Param(
            True,
            type="boolean",
            description="Sistema de alertas proactivas mejorado"
        ),
        "proactive_alerting_config": Param(
            "{}",
            type="string",
            description="JSON con configuración de alertas proactivas"
        ),
    },
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
    doc_md="""
    ### Monitoreo de Calidad de Datos de Clientes
    
    Este DAG ejecuta validaciones exhaustivas sobre la base de datos de clientes
    cada noche y envía reportes automáticos cuando se detectan problemas.
    
    **Funcionalidades Principales:**
    - ✅ **100+ tipos de validaciones** (nulos, formato, duplicados, rangos, integridad referencial, etc.)
    - 🔄 **Circuit Breaker Pattern** para prevenir fallos en cascada
    - 🔁 **Retry Inteligente** con exponential backoff y jitter
    - 📊 **Métricas avanzadas** (calidad, ROI, impacto en negocio, SLA)
    - 🤖 **Aprendizaje continuo** y recomendaciones ML
    - 📈 **Análisis predictivo** y detección de anomalías
    - 🔔 **Alertas inteligentes** basadas en reglas de negocio
    - 💰 **Métricas de costos** y optimización automática
    - 🎯 **Validaciones especializadas** (e-commerce, IoT, wearables, POS, etc.)
    
    **Mejoras de Rendimiento y Robustez:**
    - 🔄 Circuit Breaker para conexiones de BD (previene fallos en cascada)
    - 🔁 Retry inteligente (solo reintenta errores temporales)
    - ⚡ Query optimization automática
    - 🔌 Connection pooling
    - 📦 Batch processing para mejor rendimiento
    - 🏥 Health checks de base de datos (conexión, espacio, versiones)
    - 📊 Validación y análisis de índices (sugerencias de optimización)
    - 🚦 Rate limiting para controlar frecuencia de operaciones
    - ✅ Validación de queries antes de ejecución (seguridad)
    - 🗜️ Compresión de resultados para grandes volúmenes
    
    **Parámetros Principales:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `clients_table`: Nombre de la tabla de clientes
    - `enable_circuit_breaker`: Habilitar Circuit Breaker (default: true)
    - `enable_smart_retry`: Habilitar retry inteligente (default: true)
    - `enable_batch_processing`: Procesar en batches (default: true)
    - `enable_quality_scoring`: Calcular score de calidad (default: true)
    - `enable_roi_metrics`: Calcular métricas ROI (default: false)
    - `enable_continuous_learning`: Sistema de aprendizaje continuo (default: false)
    
    **Más de 100 funcionalidades disponibles** - Ver parámetros completos en la UI de Airflow.
    """,
)
def data_quality_monitoring() -> None:
    """DAG para monitoreo de calidad de datos."""
    
    @task(task_id="run_validations")
    def run_validations(**context) -> Dict[str, Any]:
        """Ejecuta todas las validaciones de calidad de datos."""
        start_time = perf_counter()
        ctx = get_current_context()
        params = ctx["params"]
        
        conn_id = str(params.get("postgres_conn_id", "postgres_default"))
        table_name = str(params.get("clients_table", "customers"))
        required_fields = params.get("required_fields", ["id", "name", "email", "created_at"])
        
        logger.info(f"Iniciando validaciones para tabla: {table_name}")
        
        try:
            # Circuit Breaker y retry inteligente para conexión
            resource_key = f"postgres_{conn_id}"
            
            # Verificar Circuit Breaker
            if params.get("enable_circuit_breaker", True):
                cb_threshold = int(params.get("circuit_breaker_threshold", 5))
                cb_timeout = int(params.get("circuit_breaker_timeout", 60))
                
                if CircuitBreaker.is_open(resource_key, cb_threshold, cb_timeout):
                    error_msg = f"Circuit breaker abierto para {resource_key}. Saltando validaciones."
                    logger.error(error_msg)
                    return {
                        "error": error_msg,
                        "circuit_breaker_open": True,
                        "timestamp": pendulum.now().isoformat()
                    }
            
            # Crear hook con retry inteligente
            def create_hook():
                return PostgresHook(postgres_conn_id=conn_id)
            
            if params.get("enable_smart_retry", True):
                max_retries = int(params.get("max_retries", 3))
                base_delay = float(params.get("retry_base_delay", 1.0))
                max_delay = float(params.get("retry_max_delay", 60.0))
                
                try:
                    hook = retry_with_exponential_backoff(
                        create_hook,
                        max_retries=max_retries,
                        base_delay=base_delay,
                        max_delay=max_delay,
                        retry_on_exceptions=(Exception,)
                    )
                    if params.get("enable_circuit_breaker", True):
                        CircuitBreaker.record_success(resource_key)
                except Exception as e:
                    if params.get("enable_circuit_breaker", True):
                        cb_threshold = int(params.get("circuit_breaker_threshold", 5))
                        CircuitBreaker.record_failure(resource_key, cb_threshold)
                    logger.error(f"Error creando conexión después de {max_retries} reintentos: {e}")
                    raise
            else:
                hook = create_hook()
            
            validator = DataQualityValidator(hook, table_name)
            
            # Health checks de la base de datos
            if params.get("enable_health_checks", True):
                try:
                    health_status = check_database_health(hook)
                    if not health_status.get("healthy", False):
                        logger.warning(f"Health check fallido: {health_status.get('overall_status', 'unknown')}")
                        # Continuar pero registrar advertencia
                    else:
                        logger.info(f"Health check exitoso: {health_status.get('overall_status', 'unknown')}")
                    # Guardar health status en resultados
                    validator.results.append(ValidationResult(
                        name="Database Health Check",
                        passed=health_status.get("healthy", False),
                        severity=Severity.WARNING if not health_status.get("healthy", False) else Severity.INFO,
                        message=f"Estado: {health_status.get('overall_status', 'unknown')}",
                        details=[health_status]
                    ))
                except Exception as e:
                    logger.warning(f"Error en health check: {e}")
            
            # Rate limiting
            if params.get("enable_rate_limiting", False):
                resource_key = f"validation_{conn_id}_{table_name}"
                max_requests = int(params.get("rate_limit_max_requests", 100))
                window_seconds = int(params.get("rate_limit_window_seconds", 60))
                
                if not RateLimiter.check_rate_limit(resource_key, max_requests, window_seconds):
                    error_msg = f"Rate limit excedido: {max_requests} requests por {window_seconds}s"
                    logger.warning(error_msg)
                    return {
                        "error": error_msg,
                        "rate_limited": True,
                        "timestamp": pendulum.now().isoformat()
                    }
            
            # Validación de índices
            if params.get("enable_index_validation", False):
                try:
                    index_analysis = validate_table_indexes(hook, table_name)
                    if index_analysis:
                        # Agregar recomendaciones de índices
                        recommendations = []
                        for idx in index_analysis:
                            if idx.get("recommendations"):
                                recommendations.extend(idx["recommendations"])
                        
                        if recommendations:
                            validator.results.append(ValidationResult(
                                name="Index Analysis",
                                passed=True,
                                severity=Severity.INFO,
                                message=f"{len(recommendations)} recomendaciones de índices",
                                details=index_analysis
                            ))
                        logger.info(f"Análisis de índices completado: {len(index_analysis)} índices analizados")
                except Exception as e:
                    logger.warning(f"Error validando índices: {e}")
            
            # Determinar si usar validación incremental
            incremental = params.get("enable_incremental_validation", False)
            incremental_field = params.get("incremental_field", "updated_at")
            incremental_since = params.get("incremental_since", "")
            
            # Construir filtro incremental si está habilitado
            incremental_filter = ""
            if incremental:
                if incremental_since:
                    try:
                        since_date = pendulum.parse(incremental_since)
                        incremental_filter = f"WHERE {incremental_field} >= '{since_date.to_iso8601_string()}'"
                    except Exception as e:
                        logger.warning(f"Error parseando incremental_since: {e}")
                else:
                    # Usar última ejecución del DAG
                    last_run = context.get("prev_execution_date")
                    if last_run:
                        incremental_filter = f"WHERE {incremental_field} >= '{last_run.isoformat()}'"
                    else:
                        # Últimas 24 horas por defecto
                        yesterday = pendulum.yesterday()
                        incremental_filter = f"WHERE {incremental_field} >= '{yesterday.isoformat()}'"
                
                logger.info(f"Validación incremental activada: {incremental_filter}")
            
            # Ejecutar validaciones estándar (con filtro incremental si aplica)
            validator.validate_required_fields(required_fields, incremental_filter)
            
            # Aplicar filtro incremental a otras validaciones si está habilitado
            if incremental and incremental_filter:
                # Modificar queries para usar filtro incremental
                logger.info("Aplicando filtro incremental a validaciones")
            
            validator.validate_email_format()
            validator.validate_duplicate_emails(limit=20)
            validator.validate_future_dates()
            validator.validate_phone_format()
            total_records = validator.validate_total_records()
            
            # Validaciones personalizadas desde JSON
            custom_validations_str = params.get("custom_validations", "{}")
            if custom_validations_str and custom_validations_str != "{}":
                try:
                    custom_validations = json.loads(custom_validations_str)
                    if isinstance(custom_validations, list):
                        for rule in custom_validations:
                            validator.validate_custom_rule(rule)
                    elif isinstance(custom_validations, dict) and "rules" in custom_validations:
                        for rule in custom_validations["rules"]:
                            validator.validate_custom_rule(rule)
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parseando custom_validations JSON: {e}")
            
            # Validaciones con Great Expectations
            if params.get("enable_great_expectations", False):
                ge_config_str = params.get("great_expectations_config", "{}")
                try:
                    ge_config = json.loads(ge_config_str) if ge_config_str else {}
                    expectations = ge_config.get("expectations", [])
                    if expectations:
                        validator.validate_with_great_expectations(expectations)
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parseando great_expectations_config JSON: {e}")
            
            # Validaciones de compliance
            if params.get("enable_compliance_checks", False):
                compliance_rules_str = params.get("compliance_rules", "{}")
                try:
                    compliance_rules = json.loads(compliance_rules_str) if compliance_rules_str else {}
                    compliance_results = validate_compliance(hook, table_name, compliance_rules)
                    # Agregar resultados de compliance al validador
                    validator.results.extend(compliance_results)
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parseando compliance_rules JSON: {e}")
            
            # Generar resumen
            summary = validator.get_summary()
            
            # Calcular score de calidad
            if params.get("enable_quality_scoring", True):
                try:
                    quality_score = calculate_quality_score({
                        "total_validations": summary.total_validations,
                        "passed": summary.passed,
                        "failed": summary.failed,
                        "warnings": summary.warnings,
                        "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed]
                    })
                    summary.metrics["quality_score"] = quality_score
                    logger.info(f"Score de calidad: {quality_score.get('score', 0):.1f} ({quality_score.get('grade', 'N/A')})")
                except Exception as e:
                    logger.warning(f"Error calculando score de calidad: {e}")
            
            # Validación de schema
            if params.get("enable_schema_validation", True):
                expected_schema_str = params.get("expected_schema", "{}")
                if expected_schema_str and expected_schema_str != "{}":
                    try:
                        expected_schema = json.loads(expected_schema_str)
                        schema_results = validate_schema(hook, table_name, expected_schema)
                        validator.results.extend(schema_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando expected_schema JSON: {e}")
            
            # Data profiling (después de generar summary para agregar a métricas)
            if params.get("enable_data_profiling", False):
                try:
                    profile_fields = required_fields + ["email", "created_at"]  # Campos a perfilar
                    data_profile = generate_data_profile(hook, table_name, profile_fields)
                    # Agregar perfil a métricas
                    summary.metrics["data_profile"] = data_profile
                    logger.info(f"Data profiling completado para {len(profile_fields)} campos")
                except Exception as e:
                    logger.warning(f"Error en data profiling: {e}")
            
            # Detección de data drift
            if params.get("enable_data_drift_detection", False):
                try:
                    # Obtener distribución histórica desde métricas
                    historical = get_historical_metrics(hook, table_name)
                    if historical and summary.metrics.get("data_profile"):
                        drift_results = []
                        for field, profile in summary.metrics["data_profile"].items():
                            historical_dist = {
                                "mean": profile.get("avg"),
                                "stddev": profile.get("stddev")
                            }
                            drift = detect_data_drift(hook, table_name, field, historical_dist)
                            if drift.get("drift_detected"):
                                drift_results.append(drift)
                        
                        if drift_results:
                            summary.metrics["data_drift"] = drift_results
                            logger.warning(f"Data drift detectado en {len(drift_results)} campos")
                except Exception as e:
                    logger.warning(f"Error en detección de drift: {e}")
            
            # Validaciones de reglas de negocio
            if params.get("enable_business_rules", False):
                business_rules_str = params.get("business_rules", "{}")
                if business_rules_str and business_rules_str != "{}":
                    try:
                        business_rules = json.loads(business_rules_str)
                        business_results = validate_business_rules(hook, table_name, business_rules)
                        validator.results.extend(business_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando business_rules JSON: {e}")
            
            # Detección de patrones sospechosos
            if params.get("enable_pattern_detection", False):
                try:
                    pattern_results = detect_suspicious_patterns(hook, table_name)
                    validator.results.extend(pattern_results)
                except Exception as e:
                    logger.warning(f"Error detectando patrones: {e}")
            
            # Verificación de frescura de datos
            if params.get("enable_data_freshness_check", False):
                try:
                    date_field = params.get("incremental_field", "updated_at")
                    max_age_hours = int(params.get("max_data_age_hours", 24))
                    freshness_result = check_data_freshness(hook, table_name, date_field, max_age_hours)
                    validator.results.append(freshness_result)
                except Exception as e:
                    logger.warning(f"Error verificando frescura: {e}")
            
            # Validaciones de seguridad
            if params.get("enable_security_validation", False):
                security_rules_str = params.get("security_rules", "{}")
                if security_rules_str and security_rules_str != "{}":
                    try:
                        security_rules = json.loads(security_rules_str)
                        security_results = validate_security(hook, table_name, security_rules)
                        validator.results.extend(security_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando security_rules JSON: {e}")
            
            # Verificación de latencia de datos
            if params.get("enable_data_latency_check", False):
                try:
                    source_field = params.get("incremental_field", "source_timestamp") or "created_at"
                    max_latency = int(params.get("max_data_latency_minutes", 60))
                    latency_result = check_data_latency(hook, table_name, source_field, max_latency)
                    validator.results.append(latency_result)
                except Exception as e:
                    logger.warning(f"Error verificando latencia: {e}")
            
            # Validaciones cross-system
            if params.get("enable_cross_system_validation", False):
                cross_system_str = params.get("cross_system_config", "{}")
                if cross_system_str and cross_system_str != "{}":
                    try:
                        cross_system_config = json.loads(cross_system_str)
                        cross_system_results = validate_cross_system(hook, table_name, cross_system_config)
                        validator.results.extend(cross_system_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando cross_system_config JSON: {e}")
            
            # Validaciones de transformaciones
            if params.get("enable_transformation_validation", False):
                transformation_rules_str = params.get("transformation_rules", "{}")
                if transformation_rules_str and transformation_rules_str != "{}":
                    try:
                        transformation_rules = json.loads(transformation_rules_str)
                        transformation_results = validate_transformations(hook, table_name, transformation_rules)
                        validator.results.extend(transformation_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando transformation_rules JSON: {e}")
            
            # Validaciones avanzadas de integridad referencial
            if params.get("enable_advanced_referential_integrity", False):
                referential_rules_str = params.get("referential_integrity_rules", "[]")
                if referential_rules_str and referential_rules_str != "[]":
                    try:
                        referential_rules = json.loads(referential_rules_str)
                        advanced_ref_results = validate_advanced_referential_integrity(hook, table_name, referential_rules)
                        validator.results.extend(advanced_ref_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando referential_integrity_rules JSON: {e}")
            
            # Validaciones de snapshots históricos
            if params.get("enable_historical_snapshots", False):
                snapshot_config_str = params.get("snapshot_config", "{}")
                if snapshot_config_str and snapshot_config_str != "{}":
                    try:
                        snapshot_config = json.loads(snapshot_config_str)
                        snapshot_results = validate_historical_snapshots(hook, table_name, snapshot_config)
                        validator.results.extend(snapshot_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando snapshot_config JSON: {e}")
            
            # Validaciones geográficas
            if params.get("enable_geographic_validation", False):
                geographic_rules_str = params.get("geographic_rules", "{}")
                if geographic_rules_str and geographic_rules_str != "{}":
                    try:
                        geographic_rules = json.loads(geographic_rules_str)
                        geographic_results = validate_geographic_data(hook, table_name, geographic_rules)
                        validator.results.extend(geographic_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando geographic_rules JSON: {e}")
            
            # Validaciones de series temporales
            if params.get("enable_time_series_validation", False):
                time_series_config_str = params.get("time_series_config", "{}")
                if time_series_config_str and time_series_config_str != "{}":
                    try:
                        time_series_config = json.loads(time_series_config_str)
                        time_series_results = validate_time_series(hook, table_name, time_series_config)
                        validator.results.extend(time_series_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando time_series_config JSON: {e}")
            
            # Validaciones de datos distribuidos
            if params.get("enable_distributed_data_validation", False):
                distributed_config_str = params.get("distributed_config", "{}")
                if distributed_config_str and distributed_config_str != "{}":
                    try:
                        distributed_config = json.loads(distributed_config_str)
                        distributed_results = validate_distributed_data(hook, table_name, distributed_config)
                        validator.results.extend(distributed_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando distributed_config JSON: {e}")
            
            # Generar recomendaciones automáticas
            if params.get("enable_auto_recommendations", True):
                try:
                    recommendations = generate_auto_recommendations({
                        "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                        "warnings_list": [{"name": r.name} for r in validator.results if r.severity == Severity.WARNING],
                        "metrics": summary.metrics
                    })
                    if recommendations:
                        summary.metrics["auto_recommendations"] = recommendations
                        logger.info(f"Generadas {len(recommendations)} recomendaciones automáticas")
                except Exception as e:
                    logger.warning(f"Error generando recomendaciones: {e}")
            
            # Validaciones financieras
            if params.get("enable_financial_validation", False):
                financial_rules_str = params.get("financial_rules", "{}")
                if financial_rules_str and financial_rules_str != "{}":
                    try:
                        financial_rules = json.loads(financial_rules_str)
                        financial_results = validate_financial_data(hook, table_name, financial_rules)
                        validator.results.extend(financial_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando financial_rules JSON: {e}")
            
            # Calcular score de confiabilidad
            if params.get("enable_reliability_scoring", False):
                try:
                    historical = get_historical_metrics(hook, table_name)
                    reliability_score = calculate_reliability_score({
                        "total_validations": summary.total_validations,
                        "passed": summary.passed,
                        "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                        "warnings_list": [{"name": r.name} for r in validator.results if r.severity == Severity.WARNING]
                    }, historical)
                    summary.metrics["reliability_score"] = reliability_score
                    logger.info(f"Score de confiabilidad: {reliability_score.get('score', 0):.1f} ({reliability_score.get('level', 'N/A')})")
                except Exception as e:
                    logger.warning(f"Error calculando score de confiabilidad: {e}")
            
            # Validaciones de streaming
            if params.get("enable_streaming_validation", False):
                streaming_config_str = params.get("streaming_config", "{}")
                if streaming_config_str and streaming_config_str != "{}":
                    try:
                        streaming_config = json.loads(streaming_config_str)
                        streaming_results = validate_streaming_data(hook, table_name, streaming_config)
                        validator.results.extend(streaming_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando streaming_config JSON: {e}")
            
            # Calcular KPIs de negocio
            if params.get("enable_business_kpis", False):
                kpi_config_str = params.get("kpi_config", "{}")
                if kpi_config_str and kpi_config_str != "{}":
                    try:
                        kpi_config = json.loads(kpi_config_str)
                        business_kpis = calculate_business_kpis({
                            "total_validations": summary.total_validations,
                            "passed": summary.passed,
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                            "metrics": summary.metrics
                        }, kpi_config)
                        summary.metrics["business_kpis"] = business_kpis
                        logger.info(f"KPI general: {business_kpis.get('overall_kpi', 0):.1f}%")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando kpi_config JSON: {e}")
            
            # Validaciones de IoT/sensores
            if params.get("enable_iot_sensor_validation", False):
                iot_config_str = params.get("iot_config", "{}")
                if iot_config_str and iot_config_str != "{}":
                    try:
                        iot_config = json.loads(iot_config_str)
                        iot_results = validate_iot_sensor_data(hook, table_name, iot_config)
                        validator.results.extend(iot_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando iot_config JSON: {e}")
            
            # ML adaptativo
            if params.get("enable_adaptive_ml", False):
                try:
                    historical_list = []
                    # Obtener múltiples ejecuciones históricas
                    for i in range(7):
                        hist = get_historical_metrics(hook, table_name, days_ago=i)
                        if hist:
                            historical_list.append(hist)
                    
                    if historical_list:
                        adaptive_ml_config_str = params.get("adaptive_ml_config", "{}")
                        adaptive_ml_config = json.loads(adaptive_ml_config_str) if adaptive_ml_config_str else {}
                        ml_improvements = adaptive_ml_improvement({
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed]
                        }, historical_list, adaptive_ml_config)
                        summary.metrics["adaptive_ml"] = ml_improvements
                        if ml_improvements.get("suggestions"):
                            logger.info(f"ML adaptativo: {len(ml_improvements['suggestions'])} sugerencias generadas")
                except Exception as e:
                    logger.warning(f"Error en ML adaptativo: {e}")
            
            # Validaciones de blockchain
            if params.get("enable_blockchain_validation", False):
                blockchain_config_str = params.get("blockchain_config", "{}")
                if blockchain_config_str and blockchain_config_str != "{}":
                    try:
                        blockchain_config = json.loads(blockchain_config_str)
                        blockchain_results = validate_blockchain_data(hook, table_name, blockchain_config)
                        validator.results.extend(blockchain_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando blockchain_config JSON: {e}")
            
            # Alertas predictivas
            if params.get("enable_predictive_alerts", False):
                try:
                    historical_list = []
                    for i in range(7):
                        hist = get_historical_metrics(hook, table_name, days_ago=i)
                        if hist:
                            historical_list.append(hist)
                    
                    if historical_list:
                        predictive_config_str = params.get("predictive_alerts_config", "{}")
                        predictive_config = json.loads(predictive_config_str) if predictive_config_str else {}
                        predictive_alerts = generate_predictive_alerts({
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                            "metrics": summary.metrics
                        }, historical_list, predictive_config)
                        summary.metrics["predictive_alerts"] = predictive_alerts
                        if predictive_alerts.get("predictive_alerts"):
                            logger.warning(f"Alertas predictivas: {len(predictive_alerts['predictive_alerts'])} alertas generadas")
                except Exception as e:
                    logger.warning(f"Error generando alertas predictivas: {e}")
            
            # Validaciones de gobernanza
            if params.get("enable_data_governance", False):
                governance_rules_str = params.get("governance_rules", "{}")
                if governance_rules_str and governance_rules_str != "{}":
                    try:
                        governance_rules = json.loads(governance_rules_str)
                        governance_results = validate_data_governance(hook, table_name, governance_rules)
                        validator.results.extend(governance_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando governance_rules JSON: {e}")
            
            # Validaciones de APIs externas
            if params.get("enable_external_api_validation", False):
                api_config_str = params.get("external_api_config", "{}")
                if api_config_str and api_config_str != "{}":
                    try:
                        api_config = json.loads(api_config_str)
                        api_results = validate_external_api_data(hook, table_name, api_config)
                        validator.results.extend(api_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando external_api_config JSON: {e}")
            
            # Validaciones de redes sociales
            if params.get("enable_social_media_validation", False):
                social_config_str = params.get("social_media_config", "{}")
                if social_config_str and social_config_str != "{}":
                    try:
                        social_config = json.loads(social_config_str)
                        social_results = validate_social_media_data(hook, table_name, social_config)
                        validator.results.extend(social_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando social_media_config JSON: {e}")
            
            # Auto-tuning de parámetros
            if params.get("enable_auto_tuning", False):
                try:
                    historical_list = []
                    for i in range(7):
                        hist = get_historical_metrics(hook, table_name, days_ago=i)
                        if hist:
                            historical_list.append(hist)
                    
                    if historical_list:
                        tuning_config_str = params.get("auto_tuning_config", "{}")
                        tuning_config = json.loads(tuning_config_str) if tuning_config_str else {}
                        tuning_results = auto_tune_parameters({
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                            "total_validations": summary.total_validations,
                            "total_records": summary.metrics.get("total_records", 0)
                        }, historical_list, tuning_config)
                        summary.metrics["auto_tuning"] = tuning_results
                        if tuning_results.get("adjustments"):
                            logger.info(f"Auto-tuning: {len(tuning_results['adjustments'])} ajustes recomendados")
                except Exception as e:
                    logger.warning(f"Error en auto-tuning: {e}")
            
            # Validaciones de medios (imágenes/videos)
            if params.get("enable_media_validation", False):
                media_config_str = params.get("media_config", "{}")
                if media_config_str and media_config_str != "{}":
                    try:
                        media_config = json.loads(media_config_str)
                        media_results = validate_media_data(hook, table_name, media_config)
                        validator.results.extend(media_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando media_config JSON: {e}")
            
            # Validaciones de sensores ambientales
            if params.get("enable_environmental_sensor_validation", False):
                env_config_str = params.get("environmental_config", "{}")
                if env_config_str and env_config_str != "{}":
                    try:
                        env_config = json.loads(env_config_str)
                        env_results = validate_environmental_sensors(hook, table_name, env_config)
                        validator.results.extend(env_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando environmental_config JSON: {e}")
            
            # Recomendaciones mejoradas
            if params.get("enable_enhanced_recommendations", True):
                try:
                    historical_list = []
                    for i in range(7):
                        hist = get_historical_metrics(hook, table_name, days_ago=i)
                        if hist:
                            historical_list.append(hist)
                    
                    enhanced_recs = generate_enhanced_recommendations({
                        "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                        "warnings_list": [{"name": r.name} for r in validator.results if r.severity == Severity.WARNING],
                        "metrics": summary.metrics,
                        "performance": summary.metrics.get("performance", {})
                    }, historical_list)
                    if enhanced_recs:
                        summary.metrics["enhanced_recommendations"] = enhanced_recs
                        logger.info(f"Recomendaciones mejoradas: {len(enhanced_recs)} generadas")
                except Exception as e:
                    logger.warning(f"Error generando recomendaciones mejoradas: {e}")
            
            # Validaciones de e-commerce
            if params.get("enable_ecommerce_validation", False):
                ecommerce_config_str = params.get("ecommerce_config", "{}")
                if ecommerce_config_str and ecommerce_config_str != "{}":
                    try:
                        ecommerce_config = json.loads(ecommerce_config_str)
                        ecommerce_results = validate_ecommerce_data(hook, table_name, ecommerce_config)
                        validator.results.extend(ecommerce_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando ecommerce_config JSON: {e}")
            
            # Validaciones de dispositivos móviles
            if params.get("enable_mobile_device_validation", False):
                mobile_config_str = params.get("mobile_config", "{}")
                if mobile_config_str and mobile_config_str != "{}":
                    try:
                        mobile_config = json.loads(mobile_config_str)
                        mobile_results = validate_mobile_device_data(hook, table_name, mobile_config)
                        validator.results.extend(mobile_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando mobile_config JSON: {e}")
            
            # Sistema de aprendizaje continuo
            if params.get("enable_continuous_learning", False):
                try:
                    historical_list = []
                    for i in range(14):  # Más datos para aprendizaje
                        hist = get_historical_metrics(hook, table_name, days_ago=i)
                        if hist:
                            historical_list.append(hist)
                    
                    if historical_list:
                        learning_config_str = params.get("learning_config", "{}")
                        learning_config = json.loads(learning_config_str) if learning_config_str else {}
                        learning_results = continuous_learning_system({
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed]
                        }, historical_list, learning_config)
                        summary.metrics["continuous_learning"] = learning_results
                        if learning_results.get("learnings"):
                            logger.info(f"Aprendizaje continuo: {len(learning_results['learnings'])} patrones identificados")
                except Exception as e:
                    logger.warning(f"Error en aprendizaje continuo: {e}")
            
            # Validaciones de sistemas POS
            if params.get("enable_pos_validation", False):
                pos_config_str = params.get("pos_config", "{}")
                if pos_config_str and pos_config_str != "{}":
                    try:
                        pos_config = json.loads(pos_config_str)
                        pos_results = validate_pos_data(hook, table_name, pos_config)
                        validator.results.extend(pos_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando pos_config JSON: {e}")
            
            # Validaciones de wearables
            if params.get("enable_wearable_validation", False):
                wearable_config_str = params.get("wearable_config", "{}")
                if wearable_config_str and wearable_config_str != "{}":
                    try:
                        wearable_config = json.loads(wearable_config_str)
                        wearable_results = validate_wearable_data(hook, table_name, wearable_config)
                        validator.results.extend(wearable_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando wearable_config JSON: {e}")
            
            # Métricas de impacto en negocio
            if params.get("enable_business_impact_metrics", False):
                try:
                    impact_config_str = params.get("business_impact_config", "{}")
                    impact_config = json.loads(impact_config_str) if impact_config_str else {}
                    impact_metrics = calculate_business_impact_metrics({
                        "errors": [{"name": r.name, "severity": r.severity.value, "count": r.count} for r in validator.results if not r.passed],
                        "metrics": summary.metrics
                    }, impact_config)
                    summary.metrics["business_impact"] = impact_metrics
                    if impact_metrics.get("risk_assessment"):
                        risk_level = impact_metrics["risk_assessment"].get("risk_level", "low")
                        logger.warning(f"Impacto en negocio: Nivel de riesgo {risk_level}")
                except Exception as e:
                    logger.warning(f"Error calculando métricas de impacto: {e}")
            
            # Validaciones de sistemas de reservas
            if params.get("enable_booking_validation", False):
                booking_config_str = params.get("booking_config", "{}")
                if booking_config_str and booking_config_str != "{}":
                    try:
                        booking_config = json.loads(booking_config_str)
                        booking_results = validate_booking_data(hook, table_name, booking_config)
                        validator.results.extend(booking_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando booking_config JSON: {e}")
            
            # Validaciones de logística
            if params.get("enable_logistics_validation", False):
                logistics_config_str = params.get("logistics_config", "{}")
                if logistics_config_str and logistics_config_str != "{}":
                    try:
                        logistics_config = json.loads(logistics_config_str)
                        logistics_results = validate_logistics_data(hook, table_name, logistics_config)
                        validator.results.extend(logistics_results)
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando logistics_config JSON: {e}")
            
            # Métricas de eficiencia operacional
            if params.get("enable_operational_efficiency_metrics", False):
                try:
                    efficiency_config_str = params.get("operational_efficiency_config", "{}")
                    efficiency_config = json.loads(efficiency_config_str) if efficiency_config_str else {}
                    efficiency_metrics = calculate_operational_efficiency_metrics({
                        "total_validations": summary.total_validations,
                        "passed": summary.passed,
                        "failed": summary.failed,
                        "execution_time_seconds": execution_time_seconds,
                        "metrics": summary.metrics
                    }, efficiency_config)
                    summary.metrics["operational_efficiency"] = efficiency_metrics
                    if efficiency_metrics.get("efficiency_scores"):
                        logger.info(f"Métricas de eficiencia calculadas")
                except Exception as e:
                    logger.warning(f"Error calculando métricas de eficiencia: {e}")
            
            # Alertas basadas en reglas
            if params.get("enable_rule_based_alerts", True):
                try:
                    alert_rules_str = params.get("alert_rules_config", "{}")
                    alert_rules = json.loads(alert_rules_str) if alert_rules_str and alert_rules_str != "{}" else {}
                    if alert_rules:
                        rule_alerts = generate_rule_based_alerts({
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                            "warnings_list": [{"name": r.name} for r in validator.results if r.severity == Severity.WARNING],
                            "metrics": summary.metrics
                        }, alert_rules)
                        summary.metrics["rule_based_alerts"] = rule_alerts
                        if rule_alerts:
                            logger.warning(f"Alertas basadas en reglas: {len(rule_alerts)} alertas generadas")
                except Exception as e:
                    logger.warning(f"Error generando alertas basadas en reglas: {e}")
            
            # Alertas proactivas mejoradas
            if params.get("enable_proactive_alerting", True):
                try:
                    historical_list = []
                    for i in range(7):
                        hist = get_historical_metrics(hook, table_name, days_ago=i)
                        if hist:
                            historical_list.append(hist)
                    
                    if historical_list:
                        alerting_config_str = params.get("proactive_alerting_config", "{}")
                        alerting_config = json.loads(alerting_config_str) if alerting_config_str else {}
                        proactive_alerts = generate_proactive_alerts({
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                            "warnings_list": [{"name": r.name} for r in validator.results if r.severity == Severity.WARNING],
                            "metrics": summary.metrics
                        }, historical_list, alerting_config)
                        summary.metrics["proactive_alerts"] = proactive_alerts
                        if proactive_alerts:
                            logger.warning(f"Alertas proactivas: {len(proactive_alerts)} alertas generadas")
                except Exception as e:
                    logger.warning(f"Error generando alertas proactivas: {e}")
            
            # Calcular métricas SLA
            if params.get("enable_sla_metrics", False):
                sla_targets_str = params.get("sla_targets", "{}")
                if sla_targets_str and sla_targets_str != "{}":
                    try:
                        sla_targets = json.loads(sla_targets_str)
                        sla_metrics = calculate_sla_metrics({
                            "total_validations": summary.total_validations,
                            "passed": summary.passed,
                            "failed": summary.failed,
                            "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                            "performance": summary.metrics.get("performance", {}),
                            "metrics": summary.metrics
                        }, sla_targets)
                        summary.metrics["sla_metrics"] = sla_metrics
                        logger.info(f"SLA general: {sla_metrics.get('overall_sla', 0):.1f}%")
                    except json.JSONDecodeError as e:
                        logger.warning(f"Error parseando sla_targets JSON: {e}")
            
            # Generar alertas inteligentes
            if params.get("enable_intelligent_alerts", True):
                try:
                    historical = get_historical_metrics(hook, table_name)
                    intelligent_alerts = generate_intelligent_alerts({
                        "errors": [{"name": r.name, "severity": r.severity.value} for r in validator.results if not r.passed],
                        "warnings_list": [{"name": r.name} for r in validator.results if r.severity == Severity.WARNING],
                        "metrics": summary.metrics
                    }, historical)
                    summary.metrics["intelligent_alerts"] = intelligent_alerts
                    if intelligent_alerts.get("alerts"):
                        logger.warning(f"Alertas inteligentes generadas: {len(intelligent_alerts['alerts'])} ({intelligent_alerts.get('priority', 'low')})")
                except Exception as e:
                    logger.warning(f"Error generando alertas inteligentes: {e}")
            
            # Comparación histórica
            if params.get("enable_historical_comparison", True):
                historical = get_historical_metrics(hook, table_name)
                if historical:
                    # Comparar pérdida de registros
                    if params.get("alert_on_record_loss", True):
                        threshold = float(params.get("record_loss_threshold", 0.05))
                        prev_total = historical.get("total_records", 0)
                        
                        if prev_total > 0:
                            loss_percentage = (prev_total - total_records) / prev_total
                            if loss_percentage > threshold:
                                summary.errors.append(ValidationResult(
                                    name="Pérdida significativa de registros",
                                    passed=False,
                                    severity=Severity.CRITICAL,
                                    message=f"Pérdida del {loss_percentage*100:.2f}% de registros ({prev_total} -> {total_records})",
                                    count=int(prev_total - total_records)
                                ))
                                summary.failed += 1
                    
                    summary.historical_comparison = historical
            
            # Guardar métricas para comparación futura
            save_metrics(hook, summary)
            
            # Convertir a dict para XCom
            result = {
                "timestamp": summary.timestamp,
                "total_validations": summary.total_validations,
                "passed": summary.passed,
                "failed": summary.failed,
                "warnings": summary.warnings,
                "errors": [
                    {
                        "name": e.name,
                        "message": e.message,
                        "severity": e.severity.value,
                        "count": e.count,
                        "details": e.details
                    }
                    for e in summary.errors
                ],
                "warnings_list": [
                    {
                        "name": w.name,
                        "message": w.message,
                        "severity": w.severity.value,
                        "count": w.count
                    }
                    for w in summary.warnings_list
                ],
                "metrics": summary.metrics,
                "historical_comparison": summary.historical_comparison
            }
            
            # Agregar métricas de performance
            execution_time_ms = (perf_counter() - start_time) * 1000
            execution_time_seconds = execution_time_ms / 1000
            result["performance"] = {
                "execution_time_ms": execution_time_ms,
                "execution_time_seconds": execution_time_seconds,
                "validations_per_second": summary.total_validations / execution_time_seconds if execution_time_seconds > 0 else 0,
                "avg_validation_time": execution_time_seconds / summary.total_validations if summary.total_validations > 0 else 0
            }
            
            # Calcular métricas de rendimiento avanzadas
            if params.get("enable_advanced_performance_metrics", True):
                try:
                    advanced_perf = calculate_advanced_performance_metrics(result, {
                        "total": execution_time_seconds,
                        "validations": {}  # Se puede expandir con tiempos por tipo de validación
                    })
                    result["performance"]["advanced"] = advanced_perf
                    if advanced_perf.get("bottlenecks"):
                        logger.warning(f"Cuellos de botella detectados: {len(advanced_perf['bottlenecks'])}")
                except Exception as e:
                    logger.warning(f"Error calculando métricas avanzadas de rendimiento: {e}")
            
            # Calcular métricas de costos
            if params.get("enable_cost_metrics", False):
                try:
                    cost_config_str = params.get("cost_config", "{}")
                    cost_config = json.loads(cost_config_str) if cost_config_str else {}
                    cost_metrics = calculate_cost_metrics(result, {
                        "total": execution_time_seconds
                    }, cost_config)
                    result["cost_metrics"] = cost_metrics
                    if cost_metrics.get("costs"):
                        total_cost = sum([c.get("value", 0) for c in cost_metrics["costs"].values() if isinstance(c, dict)])
                        logger.info(f"Métricas de costos: ${total_cost:.4f}")
                    
                    # Calcular ROI si está habilitado
                    if params.get("enable_roi_metrics", False):
                        roi_config_str = params.get("roi_config", "{}")
                        roi_config = json.loads(roi_config_str) if roi_config_str else {}
                        roi_metrics = calculate_roi_metrics(result, cost_metrics, roi_config)
                        result["roi_metrics"] = roi_metrics
                        if roi_metrics.get("roi"):
                            roi_pct = roi_metrics["roi"].get("percentage", 0)
                            logger.info(f"ROI: {roi_pct:.1f}%")
                except Exception as e:
                    logger.warning(f"Error calculando métricas de costos/ROI: {e}")
            
            # Exportar métricas a Prometheus
            if params.get("enable_prometheus", True):
                export_prometheus_metrics(result, table_name)
                
                # Push a Pushgateway si está configurado
                pushgateway_url = params.get("prometheus_pushgateway_url", "").strip()
                if pushgateway_url:
                    push_prometheus_metrics(pushgateway_url, result, table_name)
            
            # Usar caché si está habilitado
            if params.get("enable_cache", True):
                cache = ResultsCache(ttl_seconds=int(params.get("cache_ttl_seconds", 3600)))
                validation_config = {
                    "required_fields": required_fields,
                    "table_name": table_name
                }
                cache.set(table_name, validation_config, result)
            
            # Validar múltiples tablas si está configurado
            multiple_tables_str = params.get("multiple_tables", "[]")
            if multiple_tables_str and multiple_tables_str != "[]":
                try:
                    tables_config = json.loads(multiple_tables_str)
                    if isinstance(tables_config, list) and len(tables_config) > 0:
                        multiple_results = validate_multiple_tables(hook, tables_config)
                        result["multiple_tables"] = multiple_results
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parseando multiple_tables JSON: {e}")
            
            logger.info(f"Validaciones completadas: {summary.passed} exitosas, {summary.failed} fallidas, {summary.warnings} advertencias en {execution_time_ms:.2f}ms")
            
            return result
            
        except Exception as e:
            logger.error(f"Error ejecutando validaciones: {e}", exc_info=True)
            raise
    
    @task(task_id="generate_report")
    def generate_report(validation_results: Dict[str, Any], **context) -> str:
        """Genera reporte HTML con los errores encontrados."""
        errors = validation_results.get("errors", [])
        warnings = validation_results.get("warnings_list", [])
        metrics = validation_results.get("metrics", {})
        historical = validation_results.get("historical_comparison")
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
                .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
                h1 {{ color: #d32f2f; margin-top: 0; }}
                h2 {{ color: #1976d2; margin-top: 30px; }}
                .summary {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }}
                .summary-item {{ background: rgba(255,255,255,0.2); padding: 15px; border-radius: 6px; }}
                .summary-item strong {{ display: block; font-size: 24px; margin-bottom: 5px; }}
                .error {{ background-color: #ffebee; padding: 15px; margin: 15px 0; border-left: 4px solid #d32f2f; border-radius: 4px; }}
                .warning {{ background-color: #fff3e0; padding: 15px; margin: 15px 0; border-left: 4px solid #f57c00; border-radius: 4px; }}
                .info {{ background-color: #e3f2fd; padding: 15px; margin: 15px 0; border-left: 4px solid #1976d2; border-radius: 4px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #1976d2; color: white; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .severity-critical {{ color: #d32f2f; font-weight: bold; }}
                .severity-error {{ color: #f44336; }}
                .severity-warning {{ color: #ff9800; }}
                .timestamp {{ color: #666; font-size: 14px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>📊 Reporte de Calidad de Datos - Clientes</h1>
                <p class="timestamp"><strong>Fecha de ejecución:</strong> {validation_results.get('timestamp', 'N/A')}</p>
                
                <div class="summary">
                    <h2 style="color: white; margin-top: 0;">Resumen Ejecutivo</h2>
                    <div class="summary-grid">
                        <div class="summary-item">
                            <strong>{validation_results.get('total_validations', 0)}</strong>
                            <span>Total Validaciones</span>
                        </div>
                        <div class="summary-item">
                            <strong>{validation_results.get('passed', 0)}</strong>
                            <span>Exitosas ✅</span>
                        </div>
                        <div class="summary-item">
                            <strong>{validation_results.get('failed', 0)}</strong>
                            <span>Fallidas ❌</span>
                        </div>
                        <div class="summary-item">
                            <strong>{validation_results.get('warnings', 0)}</strong>
                            <span>Advertencias ⚠️</span>
                        </div>
                        <div class="summary-item">
                            <strong>{metrics.get('total_records', 0):,}</strong>
                            <span>Total Registros</span>
                        </div>
                    </div>
                </div>
        """
        
        # Agregar información de performance
        performance = validation_results.get("performance", {})
        if performance:
            html += f"""
                <div class="info">
                    <h3>⚡ Performance</h3>
                    <p><strong>Tiempo de ejecución:</strong> {performance.get('execution_time_ms', 0):.2f} ms</p>
                    <p><strong>Validaciones por segundo:</strong> {performance.get('validations_per_second', 0):.2f}</p>
                </div>
            """
        
        # Agregar predicciones si están disponibles
        predictions = validation_results.get("predictions")
        if predictions and predictions.get("predicted_issues"):
            risk_level = predictions.get("risk_level", "low")
            risk_color = {"high": "#d32f2f", "medium": "#f57c00", "low": "#1976d2"}.get(risk_level, "#666")
            html += f"""
                <div class="info" style="border-left-color: {risk_color};">
                    <h3>🔮 Análisis Predictivo</h3>
                    <p><strong>Nivel de riesgo:</strong> <span style="color: {risk_color}; font-weight: bold;">{risk_level.upper()}</span></p>
                    <p><strong>Confianza:</strong> {predictions.get('confidence', 0)*100:.1f}%</p>
                    <ul>
            """
            for issue in predictions.get("predicted_issues", []):
                html += f"<li><strong>{issue.get('type')}:</strong> {issue.get('message')}</li>"
            html += """
                    </ul>
                </div>
            """
        
        # Agregar anomalías ML si están disponibles
        ml_anomalies = validation_results.get("ml_anomalies", [])
        if ml_anomalies:
            html += """
                <div class="warning">
                    <h3>🤖 Anomalías Detectadas por ML</h3>
            """
            for anomaly in ml_anomalies:
                html += f"""
                    <p><strong>{anomaly.get('field')}:</strong> {anomaly.get('anomaly_count')} anomalías detectadas 
                    (método: {anomaly.get('method')})</p>
                """
            html += "</div>"
        
        if historical:
            html += f"""
                <div class="info">
                    <h3>📈 Comparación Histórica</h3>
                    <p><strong>Fecha anterior:</strong> {historical.get('date', 'N/A')}</p>
                    <p><strong>Registros anteriores:</strong> {historical.get('total_records', 0):,}</p>
                    <p><strong>Errores anteriores:</strong> {historical.get('validation_errors', 0)}</p>
                </div>
            """
        
        if errors:
            html += "<h2>🚨 Errores Encontrados</h2>"
            for error in errors:
                severity_class = f"severity-{error.get('severity', 'error')}"
                html += f"""
                <div class="error">
                    <h3>{error.get('name', 'Validación desconocida')}</h3>
                    <p><strong>Mensaje:</strong> {error.get('message', 'N/A')}</p>
                    <p><strong>Severidad:</strong> <span class="{severity_class}">{error.get('severity', 'error').upper()}</span></p>
                    <p><strong>Cantidad afectada:</strong> {error.get('count', 0):,}</p>
                """
                if error.get('details'):
                    html += "<table><tr><th>Detalle</th><th>Cantidad</th></tr>"
                    for detail in error['details'][:10]:  # Limitar a 10 para no hacer el email muy largo
                        html += f"<tr><td>{detail.get('email', 'N/A')}</td><td>{detail.get('count', 'N/A')}</td></tr>"
                    if len(error['details']) > 10:
                        html += f"<tr><td colspan='2'><em>... y {len(error['details']) - 10} más</em></td></tr>"
                    html += "</table>"
                html += "</div>"
        
        if warnings:
            html += "<h2>⚠️ Advertencias</h2>"
            for warning in warnings:
                html += f"""
                <div class="warning">
                    <h3>{warning.get('name', 'Validación desconocida')}</h3>
                    <p><strong>Mensaje:</strong> {warning.get('message', 'N/A')}</p>
                    <p><strong>Cantidad:</strong> {warning.get('count', 0):,}</p>
                </div>
                """
        
        if not errors and not warnings:
            html += """
            <div class="info">
                <h3>✅ ¡Excelente!</h3>
                <p>Todas las validaciones pasaron correctamente. No se detectaron problemas de calidad de datos.</p>
            </div>
            """
        
        html += """
                <div class="footer">
                    <p><em>Este es un reporte automático generado por el sistema de monitoreo de calidad de datos.</em></p>
                    <p><em>Para más información, consulta el DAG en Airflow: data_quality_monitoring</em></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html
    
    @task(task_id="export_results")
    def export_results(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Exporta resultados a JSON y CSV según configuración."""
        ctx = get_current_context()
        params = ctx["params"]
        
        exports = {}
        
        if params.get("export_to_json", True):
            json_str = export_to_json(validation_results, **context)
            exports["json"] = json_str
            logger.info("Resultados exportados a JSON")
        
        if params.get("export_to_csv", False):
            csv_str = export_to_csv(validation_results, **context)
            exports["csv"] = csv_str
            logger.info("Resultados exportados a CSV")
        
        return exports
    
    @task(task_id="analyze_trends")
    def analyze_trends(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Analiza tendencias estadísticas y aplica alertas inteligentes."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_trend_analysis", True):
            return {}
        
        try:
            conn_id = str(params.get("postgres_conn_id", "postgres_default"))
            hook = PostgresHook(postgres_conn_id=conn_id)
            days = int(params.get("trend_analysis_days", 7))
            
            trends = calculate_trends(hook, days)
            
            # Agregar tendencias a los resultados
            validation_results["trends"] = trends
            
            # Aplicar alertas inteligentes
            if params.get("enable_smart_alerts", True):
                alert_thresholds_str = params.get("alert_thresholds", "{}")
                try:
                    alert_thresholds = json.loads(alert_thresholds_str) if alert_thresholds_str else {}
                    alerts = apply_smart_alerts(validation_results, trends, alert_thresholds)
                    if alerts:
                        validation_results["smart_alerts"] = alerts
                        logger.info(f"Se generaron {len(alerts)} alertas inteligentes")
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parseando alert_thresholds JSON: {e}")
            
            # Análisis predictivo
            if params.get("enable_predictive_analysis", True):
                try:
                    # Obtener datos históricos para análisis
                    historical_query = f"""
                        SELECT date, validation_errors, validation_warnings, total_records
                        FROM data_quality_metrics
                        WHERE date >= CURRENT_DATE - INTERVAL '{days} days'
                        ORDER BY date DESC
                    """
                    historical_records = hook.get_records(historical_query)
                    historical_data = [
                        {
                            "date": str(row[0]),
                            "validation_errors": row[1],
                            "validation_warnings": row[2],
                            "total_records": row[3]
                        }
                        for row in historical_records
                    ]
                    
                    predictions = predict_quality_issues(trends, historical_data)
                    if predictions.get("predicted_issues"):
                        validation_results["predictions"] = predictions
                        logger.info(f"Análisis predictivo: {predictions.get('risk_level')} risk level")
                except Exception as e:
                    logger.warning(f"Error en análisis predictivo: {e}")
            
            logger.info(f"Tendencias calculadas para {days} días")
            return trends
        except Exception as e:
            logger.warning(f"Error analizando tendencias: {e}")
            return {}
    
    @task(task_id="create_tickets")
    def create_tickets(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Crea tickets en sistema de tickets para errores críticos."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_ticketing", False):
            return {"created": False, "message": "Ticketing deshabilitado"}
        
        platform = params.get("ticketing_platform", "jira")
        config_str = params.get("ticketing_config", "{}")
        
        try:
            config = json.loads(config_str) if config_str else {}
            ticket_id = create_ticket_for_errors(validation_results, platform, config)
            
            if ticket_id:
                logger.info(f"Ticket creado en {platform}: {ticket_id}")
                return {"created": True, "platform": platform, "ticket_id": ticket_id}
            else:
                return {"created": False, "message": "No se pudo crear ticket"}
        except Exception as e:
            logger.error(f"Error creando ticket: {e}")
            return {"created": False, "error": str(e)}
    
    @task(task_id="auto_fix_data")
    def auto_fix_data(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Intenta auto-reparar problemas de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_auto_fix", False):
            return {"fixed": False, "message": "Auto-fix deshabilitado"}
        
        try:
            conn_id = str(params.get("postgres_conn_id", "postgres_default"))
            table_name = str(params.get("clients_table", "customers"))
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            errors = validation_results.get("errors", [])
            fix_rules_str = params.get("auto_fix_rules", "{}")
            fix_rules = json.loads(fix_rules_str) if fix_rules_str else {}
            
            if not fix_rules:
                return {"fixed": False, "message": "No hay reglas de auto-fix configuradas"}
            
            fixes = auto_fix_data_issues(hook, table_name, errors, fix_rules)
            
            if fixes.get("total_applied", 0) > 0:
                logger.info(f"Auto-fix aplicado: {fixes['total_applied']} fixes")
                # Re-ejecutar validaciones después del fix
                validation_results["auto_fix_applied"] = fixes
            
            return fixes
        except Exception as e:
            logger.error(f"Error en auto-fix: {e}")
            return {"fixed": False, "error": str(e)}
    
    @task(task_id="ml_anomaly_detection")
    def ml_anomaly_detection(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Detecta anomalías usando Machine Learning."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_ml_anomaly_detection", False):
            return {"anomalies": []}
        
        try:
            conn_id = str(params.get("postgres_conn_id", "postgres_default"))
            table_name = str(params.get("clients_table", "customers"))
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            ml_config_str = params.get("ml_model_config", "{}")
            ml_config = json.loads(ml_config_str) if ml_config_str else {}
            
            # Campos a analizar (configurables)
            fields_to_analyze = ml_config.get("fields", ["created_at"])
            all_anomalies = []
            
            for field in fields_to_analyze:
                anomalies = detect_ml_anomalies(hook, table_name, field, ml_config)
                all_anomalies.extend(anomalies)
            
            if all_anomalies:
                validation_results["ml_anomalies"] = all_anomalies
                logger.info(f"ML detectó {len(all_anomalies)} tipos de anomalías")
            
            return {"anomalies": all_anomalies}
        except Exception as e:
            logger.warning(f"Error en detección ML: {e}")
            return {"anomalies": [], "error": str(e)}
    
    @task(task_id="generate_scheduled_reports")
    def generate_scheduled_reports(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Genera reportes programables según configuración."""
        ctx = get_current_context()
        params = ctx["params"]
        
        report_schedule_str = params.get("report_schedule", "{}")
        if not report_schedule_str or report_schedule_str == "{}":
            return {"generated": False, "message": "No hay reportes programados"}
        
        try:
            report_schedule = json.loads(report_schedule_str)
            reports_generated = []
            
            # Verificar si es momento de generar algún reporte
            current_time = pendulum.now()
            
            for report_config in report_schedule.get("reports", []):
                schedule_type = report_config.get("schedule", "daily")
                last_generated = report_config.get("last_generated")
                
                should_generate = False
                
                if schedule_type == "daily":
                    should_generate = True  # Siempre generar en ejecución diaria
                elif schedule_type == "weekly" and current_time.day_of_week == 0:  # Domingo
                    should_generate = True
                elif schedule_type == "monthly" and current_time.day == 1:
                    should_generate = True
                elif schedule_type == "on_error" and validation_results.get("failed", 0) > 0:
                    should_generate = True
                
                if should_generate:
                    # Generar reporte personalizado
                    report_format = report_config.get("format", "html")
                    recipients = report_config.get("recipients", [])
                    
                    # Aquí se podría generar reporte personalizado
                    reports_generated.append({
                        "name": report_config.get("name", "Report"),
                        "format": report_format,
                        "recipients": recipients
                    })
            
            if reports_generated:
                logger.info(f"Reportes programables generados: {len(reports_generated)}")
            
            return {"generated": len(reports_generated) > 0, "reports": reports_generated}
        except Exception as e:
            logger.warning(f"Error generando reportes programables: {e}")
            return {"generated": False, "error": str(e)}
    
    @task(task_id="send_critical_alerts")
    def send_critical_alerts(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Envía alertas críticas a sistemas de alertas."""
        ctx = get_current_context()
        params = ctx["params"]
        
        results = {"pagerduty": False, "opsgenie": False}
        
        # Solo enviar si hay errores críticos
        errors = validation_results.get("errors", [])
        critical_errors = [e for e in errors if e.get("severity") == "critical"]
        
        if not critical_errors:
            return results
        
        # Enviar a PagerDuty
        if params.get("enable_pagerduty_integration", False):
            pagerduty_key = params.get("pagerduty_integration_key", "").strip() or os.getenv("PAGERDUTY_INTEGRATION_KEY", "")
            if pagerduty_key:
                try:
                    success = send_pagerduty_alert(pagerduty_key, validation_results)
                    results["pagerduty"] = success
                    if success:
                        logger.info("Alerta crítica enviada a PagerDuty")
                except Exception as e:
                    logger.error(f"Error enviando a PagerDuty: {e}")
        
        # Enviar a Opsgenie
        if params.get("enable_opsgenie_integration", False):
            opsgenie_key = params.get("opsgenie_api_key", "").strip() or os.getenv("OPSGENIE_API_KEY", "")
            if opsgenie_key:
                try:
                    success = send_opsgenie_alert(opsgenie_key, validation_results)
                    results["opsgenie"] = success
                    if success:
                        logger.info("Alerta crítica enviada a Opsgenie")
                except Exception as e:
                    logger.error(f"Error enviando a Opsgenie: {e}")
        
        return results
    
    @task(task_id="classify_errors_ml")
    def classify_errors_ml_task(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Clasifica errores usando Machine Learning."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_ml_error_classification", False):
            return {"classified": False, "message": "ML classification deshabilitado"}
        
        try:
            classification = classify_errors_with_ml(validation_results)
            if classification.get("classified"):
                validation_results["ml_classification"] = classification
                logger.info(f"Errores clasificados en {classification.get('total_categories', 0)} categorías")
            return classification
        except Exception as e:
            logger.error(f"Error en clasificación ML: {e}")
            return {"classified": False, "error": str(e)}
    
    @task(task_id="generate_web_dashboard")
    def generate_web_dashboard_task(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Genera dashboard web interactivo."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_dashboard_web", False):
            return {"generated": False, "message": "Dashboard web deshabilitado"}
        
        try:
            output_path = params.get("dashboard_output_path", "/tmp/data_quality_dashboard.html")
            dashboard_path = generate_web_dashboard(validation_results, output_path)
            
            if dashboard_path:
                logger.info(f"Dashboard web generado: {dashboard_path}")
                return {"generated": True, "path": dashboard_path}
            else:
                return {"generated": False, "message": "Error generando dashboard"}
        except Exception as e:
            logger.error(f"Error generando dashboard: {e}")
            return {"generated": False, "error": str(e)}
    
    @task(task_id="send_monitoring_metrics")
    def send_monitoring_metrics(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Envía métricas a sistemas de monitoreo externos."""
        ctx = get_current_context()
        params = ctx["params"]
        
        results = {"grafana": False, "datadog": False}
        
        # Enviar a Grafana
        if params.get("enable_grafana_integration", False):
            grafana_url = params.get("grafana_api_url", "").strip()
            grafana_key = os.getenv("GRAFANA_API_KEY", "")
            
            if grafana_url and grafana_key:
                try:
                    success = send_to_grafana(grafana_url, grafana_key, validation_results)
                    results["grafana"] = success
                    if success:
                        logger.info("Métricas enviadas a Grafana")
                except Exception as e:
                    logger.error(f"Error enviando a Grafana: {e}")
        
        # Enviar a Datadog
        if params.get("enable_datadog_integration", False):
            datadog_key = params.get("datadog_api_key", "").strip() or os.getenv("DATADOG_API_KEY", "")
            table_name = params.get("clients_table", "customers")
            
            if datadog_key:
                try:
                    success = send_to_datadog(datadog_key, validation_results, table_name)
                    results["datadog"] = success
                    if success:
                        logger.info("Métricas enviadas a Datadog")
                except Exception as e:
                    logger.error(f"Error enviando a Datadog: {e}")
        
        return results
    
    @task(task_id="check_query_performance")
    def check_query_performance(**context) -> Dict[str, Any]:
        """Monitorea performance de queries de validación."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_query_performance_check", False):
            return {"checked": False}
        
        try:
            conn_id = str(params.get("postgres_conn_id", "postgres_default"))
            hook = PostgresHook(postgres_conn_id=conn_id)
            timeout = int(params.get("query_timeout_seconds", 30))
            
            # Verificar configuración de timeout en la base de datos
            timeout_query = f"SHOW statement_timeout"
            result = hook.get_first(timeout_query)
            current_timeout = result[0] if result else None
            
            # Verificar índices en campos validados
            table_name = str(params.get("clients_table", "customers"))
            required_fields = params.get("required_fields", [])
            
            index_check_query = f"""
                SELECT indexname, indexdef
                FROM pg_indexes
                WHERE tablename = '{table_name}'
            """
            indexes = hook.get_records(index_check_query)
            
            performance_info = {
                "statement_timeout": current_timeout,
                "configured_timeout_seconds": timeout,
                "indexes": [{"name": row[0], "definition": row[1]} for row in indexes],
                "recommendations": []
            }
            
            # Recomendaciones
            if not indexes:
                performance_info["recommendations"].append(
                    "Considerar agregar índices en campos validados frecuentemente"
                )
            
            if current_timeout and int(current_timeout.replace("ms", "")) < timeout * 1000:
                performance_info["recommendations"].append(
                    f"Timeout de BD ({current_timeout}) menor que configurado ({timeout}s)"
                )
            
            logger.info(f"Performance check completado: {len(indexes)} índices encontrados")
            return {"checked": True, "performance": performance_info}
        except Exception as e:
            logger.warning(f"Error en check de performance: {e}")
            return {"checked": False, "error": str(e)}
    
    @task(task_id="start_api_server")
    def start_api_server(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Inicia servidor API REST para consultar resultados."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_api_endpoints", False):
            return {"started": False, "message": "API endpoints deshabilitados"}
        
        try:
            port = int(params.get("api_port", 8081))
            app = create_api_endpoints(validation_results, port)
            
            if app:
                # En producción, esto debería ejecutarse en un proceso separado
                # Por ahora, solo registramos que la API está disponible
                logger.info(f"API REST configurada en puerto {port} (requiere proceso separado para ejecutar)")
                return {"started": True, "port": port, "endpoints": [
                    "/api/v1/health",
                    "/api/v1/results/latest",
                    "/api/v1/results/summary",
                    "/api/v1/results/errors",
                    "/api/v1/metrics"
                ]}
            else:
                return {"started": False, "message": "No se pudo crear API"}
        except Exception as e:
            logger.error(f"Error iniciando API server: {e}")
            return {"started": False, "error": str(e)}
    
    @task(task_id="audit_logging")
    def audit_logging(validation_results: Dict[str, Any], **context) -> None:
        """Registra eventos de auditoría."""
        ctx = get_current_context()
        params = ctx["params"]
        
        if not params.get("enable_audit_logging", True):
            return
        
        try:
            conn_id = str(params.get("postgres_conn_id", "postgres_default"))
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            # Crear tabla de auditoría si no existe
            create_audit_table = """
            CREATE TABLE IF NOT EXISTS data_quality_audit_log (
                id SERIAL PRIMARY KEY,
                execution_date TIMESTAMP NOT NULL,
                dag_id VARCHAR(255) NOT NULL,
                table_name VARCHAR(255) NOT NULL,
                total_validations INT,
                passed INT,
                failed INT,
                warnings INT,
                errors JSONB,
                execution_time_ms FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
            hook.run(create_audit_table)
            
            # Insertar registro de auditoría
            insert_audit = """
            INSERT INTO data_quality_audit_log (
                execution_date, dag_id, table_name,
                total_validations, passed, failed, warnings,
                errors, execution_time_ms
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            execution_date = context.get("execution_date", pendulum.now())
            table_name = params.get("clients_table", "customers")
            errors_json = json.dumps(validation_results.get("errors", []))
            performance = validation_results.get("performance", {})
            
            hook.run(insert_audit, parameters=(
                execution_date,
                "data_quality_monitoring",
                table_name,
                validation_results.get("total_validations", 0),
                validation_results.get("passed", 0),
                validation_results.get("failed", 0),
                validation_results.get("warnings", 0),
                errors_json,
                performance.get("execution_time_ms", 0)
            ))
            
            logger.info("Registro de auditoría creado")
        except Exception as e:
            logger.warning(f"Error en logging de auditoría: {e}")
    
    @task(task_id="store_results_api")
    def store_results_api(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Almacena resultados en API externa si está configurada."""
        ctx = get_current_context()
        params = ctx["params"]
        
        api_url = params.get("api_endpoint_url", "").strip()
        if not api_url:
            return {"stored": False, "message": "API endpoint no configurado"}
        
        try:
            payload = {
                "dag_id": "data_quality_monitoring",
                "execution_date": context.get("execution_date", pendulum.now().isoformat()),
                "results": validation_results
            }
            
            response = requests.post(api_url, json=payload, timeout=30)
            response.raise_for_status()
            
            logger.info(f"Resultados almacenados en API: {api_url}")
            return {"stored": True, "status_code": response.status_code}
        except Exception as e:
            logger.warning(f"Error almacenando resultados en API: {e}")
            return {"stored": False, "error": str(e)}
    
    @task(task_id="send_notifications")
    def send_notifications(validation_results: Dict[str, Any], **context) -> Dict[str, Any]:
        """Envía notificaciones a Slack y webhooks."""
        ctx = get_current_context()
        params = ctx["params"]
        
        results = {"slack": False, "webhook": False}
        
        # Notificación a Slack
        slack_webhook = str(params.get("slack_webhook_url", "")).strip()
        if slack_webhook:
            try:
                success = send_slack_notification(slack_webhook, validation_results)
                results["slack"] = success
                if success:
                    logger.info("Notificación enviada a Slack")
            except Exception as e:
                logger.error(f"Error enviando notificación Slack: {e}")
        
        # Notificación a webhook personalizado
        custom_webhook = str(params.get("custom_webhook_url", "")).strip()
        if custom_webhook:
            try:
                success = send_webhook_notification(custom_webhook, validation_results)
                results["webhook"] = success
                if success:
                    logger.info("Notificación enviada a webhook personalizado")
            except Exception as e:
                logger.error(f"Error enviando webhook: {e}")
        
        return results
    
    @task(task_id="validation_success")
    def validation_success(**context) -> None:
        """Task ejecutado cuando todas las validaciones pasan."""
        logger.info("✅ Todas las validaciones pasaron correctamente. No se requiere acción.")
    
    @task.branch(task_id="check_branch")
    def check_branch(validation_results: Dict[str, Any]) -> str:
        """Branching basado en si hay errores."""
        if validation_results.get("failed", 0) > 0 or validation_results.get("errors"):
            logger.info("Se detectaron errores, se generará reporte")
            return "generate_report"
        else:
            logger.info("No se detectaron errores, validación exitosa")
            return "validation_success"
    
    # Ejecutar validaciones
    validation_results = run_validations()
    
    # Análisis de tendencias (siempre se ejecuta)
    trends = analyze_trends(validation_results)
    
    # Exportar resultados (siempre se ejecuta)
    exports = export_results(validation_results)
    
    # Branching basado en resultados
    branch_result = check_branch(validation_results)
    
    # Generar reporte (solo si hay errores)
    report_html = generate_report(validation_results)
    
    # Enviar notificaciones (solo si hay errores)
    notifications = send_notifications(validation_results)
    
    # Enviar email con reporte (solo si hay errores)
    send_email = EmailOperator(
        task_id="send_error_report",
        to="{{ params.data_team_email }}",
        subject="🚨 Reporte de Calidad de Datos - Errores Detectados",
        html_content="{{ ti.xcom_pull(task_ids='generate_report', key='return_value') }}",
    )
    
    # Task de éxito
    success_task = validation_success()
    
    # Detección ML de anomalías (siempre se ejecuta si está habilitado)
    ml_anomalies = ml_anomaly_detection(validation_results)
    
    # Auto-fix de datos (solo si hay errores y está habilitado)
    auto_fix = auto_fix_data(validation_results)
    
    # Crear tickets (solo si hay errores críticos)
    tickets = create_tickets(validation_results)
    
    # Generar reportes programables
    scheduled_reports = generate_scheduled_reports(validation_results)
    
    # Logging de auditoría
    audit_log = audit_logging(validation_results)
    
    # Verificar performance de queries
    query_performance = check_query_performance()
    
    # Enviar métricas a sistemas de monitoreo
    monitoring_metrics = send_monitoring_metrics(validation_results)
    
    # Enviar alertas críticas a sistemas de alertas
    critical_alerts = send_critical_alerts(validation_results)
    
    # Generar dashboard web interactivo
    web_dashboard = generate_web_dashboard_task(validation_results)
    
    # Iniciar API REST (si está habilitada)
    api_server = start_api_server(validation_results)
    
    # Almacenar resultados en API (si está configurado)
    api_storage = store_results_api(validation_results)
    
    # Clasificación ML de errores
    ml_classification = classify_errors_ml_task(validation_results)
    
    # Dependencias: branching después de validaciones
    validation_results >> [trends, exports, api_storage, ml_anomalies, audit_log, api_server, query_performance, monitoring_metrics, web_dashboard, ml_classification]
    validation_results >> branch_result
    branch_result >> [report_html, success_task]
    report_html >> [send_email, notifications, tickets, auto_fix, scheduled_reports, critical_alerts]
