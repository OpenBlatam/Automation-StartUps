"""
Utilidades compartidas para los DAGs de Ads Reporting.

Incluye:
- Health checks comunes
- Data quality checks
- Utilidades de validación
- Helpers de métricas
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from contextlib import contextmanager

logger = logging.getLogger(__name__)

try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False


@dataclass
class HealthCheckResult:
    """Resultado de un health check."""
    status: str  # "ok", "warning", "error"
    component: str
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: Optional[str] = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class DataQualityCheck:
    """Resultado de un data quality check."""
    check_name: str
    passed: bool
    message: str
    metrics: Optional[Dict[str, Any]] = None
    issues: Optional[List[str]] = None


def check_api_credentials(
    platform: str,
    access_token: Optional[str] = None,
    account_id: Optional[str] = None,
    **kwargs
) -> HealthCheckResult:
    """
    Verifica que las credenciales de API estén configuradas.
    
    Args:
        platform: Nombre de la plataforma (facebook, tiktok, google)
        access_token: Token de acceso
        account_id: ID de cuenta
        **kwargs: Otros campos requeridos
        
    Returns:
        HealthCheckResult
    """
    issues = []
    
    if not access_token or not access_token.strip():
        issues.append(f"{platform}_access_token no configurado")
    
    if account_id and not account_id.strip():
        issues.append(f"{platform}_account_id no configurado")
    
    # Verificar campos adicionales requeridos
    for key, value in kwargs.items():
        if value is None or (isinstance(value, str) and not value.strip()):
            issues.append(f"{key} no configurado")
    
    if issues:
        return HealthCheckResult(
            status="error",
            component=f"{platform}_credentials",
            message=f"Credenciales incompletas: {', '.join(issues)}",
            details={"missing_fields": issues}
        )
    
    return HealthCheckResult(
        status="ok",
        component=f"{platform}_credentials",
        message="Credenciales configuradas correctamente"
    )


def check_database_connection(
    postgres_conn_id: str = "postgres_default"
) -> HealthCheckResult:
    """
    Verifica la conexión a la base de datos.
    
    Args:
        postgres_conn_id: Connection ID de PostgreSQL
        
    Returns:
        HealthCheckResult
    """
    if not POSTGRES_AVAILABLE:
        return HealthCheckResult(
            status="warning",
            component="database",
            message="PostgresHook no disponible",
            details={"available": False}
        )
    
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        conn = hook.get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        conn.close()
        
        return HealthCheckResult(
            status="ok",
            component="database",
            message="Conexión a base de datos exitosa",
            details={"connection_id": postgres_conn_id}
        )
    except Exception as e:
        return HealthCheckResult(
            status="error",
            component="database",
            message=f"Error de conexión a base de datos: {str(e)}",
            details={"error": str(e), "connection_id": postgres_conn_id}
        )


def check_table_exists(
    table_name: str,
    postgres_conn_id: str = "postgres_default"
) -> HealthCheckResult:
    """
    Verifica que una tabla exista en la base de datos.
    
    Args:
        table_name: Nombre de la tabla
        postgres_conn_id: Connection ID de PostgreSQL
        
    Returns:
        HealthCheckResult
    """
    if not POSTGRES_AVAILABLE:
        return HealthCheckResult(
            status="warning",
            component="database_table",
            message="PostgresHook no disponible",
            details={"table": table_name}
        )
    
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        query = """
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = %s
        )
        """
        exists = hook.get_first(query, parameters=(table_name,))[0]
        
        if exists:
            return HealthCheckResult(
                status="ok",
                component="database_table",
                message=f"Tabla {table_name} existe",
                details={"table": table_name, "exists": True}
            )
        else:
            return HealthCheckResult(
                status="warning",
                component="database_table",
                message=f"Tabla {table_name} no existe (se creará automáticamente)",
                details={"table": table_name, "exists": False}
            )
    except Exception as e:
        return HealthCheckResult(
            status="error",
            component="database_table",
            message=f"Error verificando tabla {table_name}: {str(e)}",
            details={"table": table_name, "error": str(e)}
        )


def validate_date_range(
    date_start: str,
    date_stop: str,
    max_days: int = 365
) -> Tuple[bool, Optional[str]]:
    """
    Valida un rango de fechas.
    
    Args:
        date_start: Fecha inicio (YYYY-MM-DD)
        date_stop: Fecha fin (YYYY-MM-DD)
        max_days: Máximo de días permitido en el rango
        
    Returns:
        Tuple[bool, Optional[str]] - (es_válido, mensaje_error)
    """
    try:
        start = datetime.strptime(date_start, "%Y-%m-%d")
        stop = datetime.strptime(date_stop, "%Y-%m-%d")
        
        if start > stop:
            return False, "date_start debe ser anterior a date_stop"
        
        days_diff = (stop - start).days
        if days_diff > max_days:
            return False, f"Rango de fechas excede máximo de {max_days} días"
        
        if days_diff < 0:
            return False, "Rango de fechas inválido"
        
        # Verificar que no sea futuro muy lejano
        if stop > datetime.now() + timedelta(days=1):
            return False, "date_stop no puede ser más de 1 día en el futuro"
        
        return True, None
        
    except ValueError as e:
        return False, f"Formato de fecha inválido: {str(e)}"
    except Exception as e:
        return False, f"Error validando fechas: {str(e)}"


def check_data_quality_campaigns(
    data: List[Dict[str, Any]],
    platform: str
) -> DataQualityCheck:
    """
    Verifica la calidad de datos de campañas extraídos.
    
    Args:
        data: Lista de datos de campañas
        platform: Nombre de la plataforma
        
    Returns:
        DataQualityCheck
    """
    issues = []
    metrics = {
        "total_records": len(data),
        "records_with_impressions": 0,
        "records_with_clicks": 0,
        "records_with_conversions": 0,
        "zero_impressions_count": 0,
        "negative_values_count": 0,
        "invalid_ctr_count": 0,
    }
    
    required_fields = {
        "facebook": ["campaign_id", "impressions", "clicks", "spend"],
        "tiktok": ["campaign_id", "impressions", "clicks", "spend"],
        "google": ["campaign_id", "impressions", "clicks", "avg_cpc"],
    }
    
    required = required_fields.get(platform, [])
    
    for record in data:
        # Verificar campos requeridos
        for field in required:
            if field not in record or record[field] is None:
                issues.append(f"Campo requerido '{field}' faltante en registro")
        
        # Verificar métricas
        impressions = record.get("impressions", 0) or 0
        clicks = record.get("clicks", 0) or 0
        spend = record.get("spend", 0) or 0
        
        if impressions > 0:
            metrics["records_with_impressions"] += 1
        else:
            metrics["zero_impressions_count"] += 1
        
        if clicks > 0:
            metrics["records_with_clicks"] += 1
        
        if record.get("conversions", 0) or 0 > 0:
            metrics["records_with_conversions"] += 1
        
        # Verificar valores negativos
        if impressions < 0 or clicks < 0 or spend < 0:
            metrics["negative_values_count"] += 1
            issues.append(f"Valores negativos encontrados en registro")
        
        # Verificar CTR válido (0-100%)
        ctr = record.get("ctr", 0) or 0
        if ctr < 0 or ctr > 100:
            metrics["invalid_ctr_count"] += 1
            issues.append(f"CTR inválido: {ctr}%")
    
    # Reglas de calidad
    if metrics["total_records"] == 0:
        issues.append("No se encontraron registros")
    
    if metrics["zero_impressions_count"] > metrics["total_records"] * 0.5:
        issues.append(f"Demasiados registros sin impresiones: {metrics['zero_impressions_count']}/{metrics['total_records']}")
    
    if metrics["negative_values_count"] > 0:
        issues.append(f"Se encontraron valores negativos: {metrics['negative_values_count']}")
    
    passed = len(issues) == 0
    
    return DataQualityCheck(
        check_name=f"{platform}_campaigns_quality",
        passed=passed,
        message="Data quality check passed" if passed else f"Found {len(issues)} issues",
        metrics=metrics,
        issues=issues if not passed else None
    )


def check_data_freshness(
    table_name: str,
    date_column: str = "date_start",
    expected_days_behind: int = 1,
    postgres_conn_id: str = "postgres_default"
) -> DataQualityCheck:
    """
    Verifica que los datos estén actualizados.
    
    Args:
        table_name: Nombre de la tabla
        date_column: Columna de fecha
        expected_days_behind: Días esperados de retraso (default: 1)
        postgres_conn_id: Connection ID de PostgreSQL
        
    Returns:
        DataQualityCheck
    """
    if not POSTGRES_AVAILABLE:
        return DataQualityCheck(
            check_name="data_freshness",
            passed=False,
            message="PostgresHook no disponible",
            issues=["Database connection not available"]
        )
    
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        # Obtener fecha máxima
        query = f"SELECT MAX({date_column}) FROM {table_name}"
        max_date = hook.get_first(query)
        
        if not max_date or not max_date[0]:
            return DataQualityCheck(
                check_name="data_freshness",
                passed=False,
                message="No data found in table",
                issues=["Table is empty"]
            )
        
        max_date_value = max_date[0]
        if isinstance(max_date_value, str):
            max_date_value = datetime.strptime(max_date_value, "%Y-%m-%d")
        
        days_behind = (datetime.now().date() - max_date_value).days
        
        passed = days_behind <= expected_days_behind
        message = (
            f"Data is {days_behind} days behind (max: {expected_days_behind})"
            if not passed
            else f"Data is fresh ({days_behind} days behind)"
        )
        
        issues = None if passed else [message]
        
        return DataQualityCheck(
            check_name="data_freshness",
            passed=passed,
            message=message,
            metrics={
                "max_date": str(max_date_value),
                "days_behind": days_behind,
                "expected_max_days": expected_days_behind
            },
            issues=issues
        )
        
    except Exception as e:
        return DataQualityCheck(
            check_name="data_freshness",
            passed=False,
            message=f"Error checking data freshness: {str(e)}",
            issues=[str(e)]
        )


@contextmanager
def track_operation(operation_name: str, platform: str, tags: Optional[Dict[str, str]] = None):
    """Context manager para trackear operaciones con métricas."""
    start_time = time.time()
    full_tags = {**(tags or {}), "platform": platform}
    
    if STATS_AVAILABLE:
        try:
            stats = Stats()
            stats.incr(f"ads_reporting.{operation_name}.start", tags=full_tags)
        except Exception:
            pass
    
    try:
        yield
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                duration_ms = (time.time() - start_time) * 1000
                stats.incr(f"ads_reporting.{operation_name}.success", tags=full_tags)
                stats.timing(f"ads_reporting.{operation_name}.duration_ms", int(duration_ms), tags=full_tags)
            except Exception:
                pass
    except Exception as e:
        if STATS_AVAILABLE:
            try:
                stats = Stats()
                stats.incr(
                    f"ads_reporting.{operation_name}.error",
                    tags={**full_tags, "error_type": type(e).__name__}
                )
            except Exception:
                pass
        raise


def aggregate_health_checks(checks: List[HealthCheckResult]) -> HealthCheckResult:
    """
    Agrega múltiples health checks en un resultado general.
    
    Args:
        checks: Lista de health checks
        
    Returns:
        HealthCheckResult agregado
    """
    errors = [c for c in checks if c.status == "error"]
    warnings = [c for c in checks if c.status == "warning"]
    
    if errors:
        status = "error"
        message = f"{len(errors)} error(s), {len(warnings)} warning(s)"
    elif warnings:
        status = "warning"
        message = f"{len(warnings)} warning(s)"
    else:
        status = "ok"
        message = "All checks passed"
    
    return HealthCheckResult(
        status=status,
        component="aggregated",
        message=message,
        details={
            "total_checks": len(checks),
            "errors": len(errors),
            "warnings": len(warnings),
            "checks": [{"component": c.component, "status": c.status, "message": c.message} for c in checks]
        }
    )


def aggregate_data_quality_checks(checks: List[DataQualityCheck]) -> Dict[str, Any]:
    """
    Agrega múltiples data quality checks.
    
    Args:
        checks: Lista de data quality checks
        
    Returns:
        Diccionario con resumen agregado
    """
    total = len(checks)
    passed = sum(1 for c in checks if c.passed)
    failed = total - passed
    
    all_issues = []
    for check in checks:
        if check.issues:
            all_issues.extend([f"{check.check_name}: {issue}" for issue in check.issues])
    
    return {
        "total_checks": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": (passed / total * 100) if total > 0 else 0,
        "all_issues": all_issues,
        "checks": [
            {
                "name": c.check_name,
                "passed": c.passed,
                "message": c.message,
                "metrics": c.metrics
            }
            for c in checks
        ]
    }


