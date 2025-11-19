"""
Módulo para comparar ingresos netos de Stripe con ingresos registrados en QuickBooks.

Compara la suma de ingresos netos de Stripe en un período con los ingresos registrados
en QuickBooks para la cuenta 'Ventas Stripe'. Si la diferencia absoluta es mayor que
un umbral configurado, genera una alerta.

**Características mejoradas con librerías modernas:**
- ✅ Caché de búsquedas de cuentas (TTLCache, 1 hora TTL)
- ✅ Retry automático con exponential backoff y jitter (tenacity)
- ✅ Rate limiting inteligente con manejo de 429
- ✅ Circuit breaker para protección contra fallos en cascada
- ✅ Health checks integrados para Stripe y QuickBooks
- ✅ Batch operations con procesamiento paralelo (ThreadPoolExecutor)
- ✅ Métricas y observabilidad (Stats, logging estructurado)
- ✅ Validación robusta con Pydantic (opcional)
- ✅ Soporte para httpx con HTTP/2 y session pooling
- ✅ Context managers para gestión de recursos
- ✅ Manejo de errores mejorado con excepciones personalizadas
- ✅ Guard clauses y early returns
- ✅ Cliente avanzado con sesiones HTTP optimizadas
- ✅ Procesamiento paralelo opcional para reducir latencia
- ✅ Reportes en múltiples formatos (texto, JSON, HTML)
- ✅ Métodos especiales (__str__, __repr__) para debugging
- ✅ Funciones helper puras para reutilización
- ✅ Validación de configuración integrada
- ✅ Control de timeouts SQL para queries largas
- ✅ RORO pattern para parámetros de Airflow
- ✅ Persistencia en base de datos con UPSERT
- ✅ Análisis de tendencias históricas
- ✅ Detección de anomalías usando z-score
- ✅ Estadísticas agregadas y análisis estadístico
- ✅ Serialización/deserialización JSON de resultados
- ✅ Normalización de resultados para almacenamiento
- ✅ Logging de progreso estructurado
- ✅ Validación de entrada para batch processing
- ✅ Configuración centralizada desde variables de entorno
- ✅ Feature flags configurables para todas las funcionalidades
- ✅ Clase RevenueCompareGlobalConfig con patrón singleton
- ✅ Factory methods para crear configs desde env vars
- ✅ Constantes configurables con defaults sensatos
- ✅ Separación de configuración global vs específica por comparación
- ✅ Clases de resultado estructuradas (ComparisonResult, BatchComparisonResult)
- ✅ Propiedades de conveniencia (is_ok, is_alerta, exceeds_threshold)
- ✅ Métodos to_json() para serialización fácil
- ✅ Factory methods from_dict() para deserialización
- ✅ Propiedades calculadas (success_rate, failure_rate, alert_rate)
- ✅ Métodos __str__ y __repr__ mejorados con emojis y formato legible
- ✅ Context managers para comparaciones (comparison_context, batch_comparison_context)
- ✅ Tracking de performance mejorado con tags y métricas de éxito/error
- ✅ Limpieza automática de recursos en context managers
- ✅ Métodos de comparación (__eq__, __lt__, __le__, __gt__, __ge__) para ordenamiento
- ✅ Métodos __hash__ para usar en sets y dicts
- ✅ Comparación por diferencia absoluta para ordenamiento lógico
- ✅ Comparación por success_rate para batch results
- ✅ Funciones de filtrado avanzadas (filter_results)
- ✅ Agrupación por período (group_results_by_period)
- ✅ Búsqueda por rango de fechas (find_results_by_date_range)
- ✅ Top N resultados ordenados (get_top_results)
- ✅ Resumen estadístico de resultados (summarize_results)
- ✅ Exportación a CSV y JSON (export_results_to_csv, export_results_to_json)
- ✅ Importación desde JSON (load_results_from_json)
- ✅ Validación de múltiples configuraciones (validate_comparison_configs)
- ✅ Generación automática de períodos (create_comparison_periods)
- ✅ Funciones helper para testing (create_test_result, create_test_batch_result)
- ✅ Comparación lado a lado de resultados (compare_results_side_by_side)
- ✅ Validación de consistencia interna (validate_result_consistency)
- ✅ Combinación y deduplicación de resultados (merge_results)
- ✅ Análisis de tendencias con regresión lineal (calculate_trend)
- ✅ Reconciliación de períodos (reconcile_periods)
- ✅ Verificación de reconciliación matemática (verify_reconciliation)
- ✅ Detección de períodos faltantes (find_missing_periods)
- ✅ Generación de reportes de reconciliación (generate_reconciliation_report)
- ✅ Verificación de consistencia de balance (check_balance_consistency)
- ✅ Agregación de métricas para dashboards (aggregate_metrics)
- ✅ Generación de datos para dashboard (generate_dashboard_data)
- ✅ Optimización automática de umbral (optimize_threshold)
- ✅ Auditoría completa de historial (audit_comparison_history)
- ✅ Health check completo del sistema (perform_system_health_check)
- ✅ Auto-corrección de problemas comunes (auto_fix_common_issues)

**Variables de entorno requeridas:**
- STRIPE_API_KEY: API Key de Stripe
- QUICKBOOKS_ACCESS_TOKEN: Token de acceso OAuth2 de QuickBooks
- QUICKBOOKS_REALM_ID: ID de la compañía en QuickBooks
- QUICKBOOKS_BASE: URL base de la API (default: sandbox)

**Variables de entorno opcionales - Feature Flags:**
- REVENUE_COMPARE_ENABLE_PARALLEL: Habilitar procesamiento paralelo (default: false)
- REVENUE_COMPARE_ENABLE_CB: Habilitar circuit breaker (default: true)
- REVENUE_COMPARE_ENABLE_METRICS: Habilitar métricas de Stats (default: true)
- REVENUE_COMPARE_ENABLE_ANOMALY_DETECTION: Habilitar detección de anomalías (default: false)
- REVENUE_COMPARE_ENABLE_TREND_ANALYSIS: Habilitar análisis de tendencias (default: true)
- REVENUE_COMPARE_ENABLE_NOTIFICATIONS: Habilitar notificaciones (default: true)
- REVENUE_COMPARE_ENABLE_PERSISTENCE: Habilitar persistencia en BD (default: true)
- REVENUE_COMPARE_ENABLE_CACHE: Habilitar caché de cuentas (default: true)

**Variables de entorno opcionales - Configuración:**
- REVENUE_COMPARE_DEFAULT_TIMEOUT: Timeout por defecto en segundos (default: 30)
- REVENUE_COMPARE_RETRY_DELAY: Delay base para retries en segundos (default: 1.0)
- REVENUE_COMPARE_MAX_RETRIES: Número máximo de retries (default: 3)
- REVENUE_COMPARE_RETRY_JITTER_MAX: Jitter máximo para retries en segundos (default: 1.0)
- REVENUE_COMPARE_CB_FAILURE_THRESHOLD: Umbral de fallos para circuit breaker (default: 10)
- REVENUE_COMPARE_CB_RESET_MINUTES: Minutos para resetear circuit breaker (default: 15)
- REVENUE_COMPARE_MAX_BATCH_WORKERS: Workers máximos para batch (default: 5)
- REVENUE_COMPARE_MAX_BATCH_SIZE: Tamaño máximo de batch (default: 100)
- REVENUE_COMPARE_PROGRESS_INTERVAL: Intervalo para reportar progreso (default: 10)
- REVENUE_COMPARE_DEFAULT_THRESHOLD: Umbral por defecto en dólares (default: 100.0)
- REVENUE_COMPARE_CRITICAL_THRESHOLD: Umbral para discrepancias críticas (default: 1000.0)
- REVENUE_COMPARE_ANOMALY_Z_THRESHOLD: Umbral de z-score para anomalías (default: 2.0)
- REVENUE_COMPARE_DEFAULT_ACCOUNT: Cuenta de QuickBooks por defecto (default: "Ventas Stripe")
- REVENUE_COMPARE_STATEMENT_TIMEOUT_MS: Timeout para queries SQL (default: sin timeout)

**Ejemplo de uso básico:**
    resultado = comparar_ingresos_stripe_quickbooks(
        fecha_inicio="2024-01-01",
        fecha_fin="2024-01-31",
        umbral=100.00
    )
    print(resultado["estado"])  # "Ok" o "Alerta"
    print(resultado["detalles"])  # Detalles de la comparación

**Ejemplo con cliente avanzado:**
    with RevenueComparisonClient(use_httpx=True) as client:
        health = client.health_check()
        if health["status"] == "ok":
            resultado = comparar_ingresos_stripe_quickbooks(
                fecha_inicio="2024-01-01",
                fecha_fin="2024-01-31",
                umbral=100.00
            )

**Ejemplo con procesamiento paralelo:**
    resultado = comparar_ingresos_stripe_quickbooks(
        fecha_inicio="2024-01-01",
        fecha_fin="2024-01-31",
        umbral=100.00,
        enable_parallel=True  # Obtiene Stripe y QuickBooks en paralelo
    )

**Ejemplo batch para múltiples períodos:**
    periodos = [
        {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"},
        {"fecha_inicio": "2024-02-01", "fecha_fin": "2024-02-28"},
    ]
    batch_result = comparar_ingresos_batch(
        periodos=periodos,
        umbral=100.00,
        max_workers=3  # Procesa 3 períodos en paralelo
    )
    print(f"Exitosos: {batch_result['exitosos']}/{batch_result['total']}")

**Ejemplo de reporte:**
    resultados = [resultado1, resultado2, resultado3]
    reporte_html = generate_comparison_report(resultados, formato="html")
    print(reporte_html)

**Ejemplo de análisis de tendencias:**
    tendencias = analizar_tendencias(dias=90)
    print(f"Promedio de diferencia: ${tendencias['promedio_diferencia']:.2f}")
    print(f"Total de alertas: {tendencias['total_alertas']}")

**Ejemplo de detección de anomalías:**
    resultados = [resultado1, resultado2, resultado3, ...]
    anomalias = detect_anomalies(resultados, z_score_threshold=2.0)
    for anomalia in anomalias:
        print(f"Anomalía detectada: diferencia=${anomalia['difference']}, z-score={anomalia['z_score']:.2f}")

**Ejemplo de estadísticas agregadas:**
    resultados = [resultado1, resultado2, resultado3, ...]
    stats = compute_statistics(resultados)
    print(f"Total: {stats['total']}, Exitosos: {stats['exitosos']}, Alertas: {stats['alertas']}")
    print(f"Promedio diferencia: ${stats['promedio_diferencia']:.2f}")

**Ejemplo de serialización:**
    resultado = comparar_ingresos_stripe_quickbooks(...)
    json_str = serialize_comparison_result(resultado)
    # Guardar o enviar por red
    resultado_recuperado = deserialize_comparison_result(json_str)

**Ejemplo con configuración global:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        get_global_config,
        ComparisonConfig
    )
    
    # Obtener configuración global (lee desde env vars)
    config = get_global_config()
    print(f"Circuit breaker habilitado: {config.enable_circuit_breaker}")
    
    # Crear ComparisonConfig usando valores globales
    comp_config = ComparisonConfig.from_global_config(
        fecha_inicio="2024-01-01",
        fecha_fin="2024-01-31"
        # umbral y cuenta_quickbooks usan defaults de config global
    )

**Ejemplo con clases de resultado estructuradas:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        ComparisonResult,
        BatchComparisonResult,
        comparar_ingresos_stripe_quickbooks,
        comparar_ingresos_batch
    )
    
    # Usar clase ComparisonResult
    resultado_dict = comparar_ingresos_stripe_quickbooks(...)
    resultado = ComparisonResult.from_dict(resultado_dict)
    
    if resultado.is_ok:
        print(f"✅ Comparación OK: diferencia ${resultado.diferencia:.2f}")
    elif resultado.is_alerta:
        print(f"⚠️ ALERTA: diferencia ${resultado.diferencia:.2f} excede umbral")
    
    # Usar propiedades
    print(f"Excede umbral: {resultado.exceeds_threshold}")
    print(f"Porcentaje diferencia: {resultado.difference_percentage:.2f}%")
    
    # Serializar a JSON
    json_str = resultado.to_json()
    
    # Batch results
    batch_dict = comparar_ingresos_batch(...)
    batch = BatchComparisonResult.from_dict(batch_dict)
    print(f"Tasa de éxito: {batch.success_rate:.2f}%")
    print(f"Tasa de alertas: {batch.alert_rate:.2f}%")
    print(f"Throughput: {batch.throughput:.2f} comparaciones/seg")

**Ejemplo con context managers:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        comparison_context,
        batch_comparison_context
    )
    
    # Comparación simple con context manager
    with comparison_context("2024-01-01", "2024-01-31") as result:
        if result.is_alerta:
            print(f"⚠️ ALERTA: diferencia ${result.diferencia:.2f}")
        elif result.is_ok:
            print(f"✅ OK: diferencia ${result.diferencia:.2f}")
    
    # Batch con context manager
    periodos = [
        {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"},
        {"fecha_inicio": "2024-02-01", "fecha_fin": "2024-02-28"}
    ]
    with batch_comparison_context(periodos) as batch:
        print(f"Total: {batch.total}, Exitosos: {batch.exitosos}")
        print(f"Tasa de éxito: {batch.success_rate:.2f}%")
        for resultado in batch.resultados:
            if resultado.is_alerta:
                print(f"  ⚠️ {resultado.fecha_inicio}: diferencia ${resultado.diferencia:.2f}")

**Ejemplo con métodos de comparación y ordenamiento:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        ComparisonResult,
        BatchComparisonResult
    )
    
    # Crear varios resultados
    result1 = ComparisonResult.from_dict(...)
    result2 = ComparisonResult.from_dict(...)
    result3 = ComparisonResult.from_dict(...)
    
    # Comparar igualdad
    if result1 == result2:
        print("Los resultados son iguales")
    
    # Ordenar por diferencia (mayor a menor)
    resultados = [result1, result2, result3]
    resultados_ordenados = sorted(resultados, reverse=True)
    
    # Obtener el resultado con mayor diferencia
    mayor_diferencia = max(resultados)
    print(f"Mayor diferencia: ${mayor_diferencia.diferencia:.2f}")
    
    # Usar en sets (gracias a __hash__)
    resultados_unicos = {result1, result2, result3}
    print(f"Resultados únicos: {len(resultados_unicos)}")
    
    # Comparar batches por success_rate
    batch1 = BatchComparisonResult.from_dict(...)
    batch2 = BatchComparisonResult.from_dict(...)
    if batch1 > batch2:
        print(f"Batch 1 tiene mejor tasa de éxito: {batch1.success_rate:.2f}%")

**Ejemplo con funciones utilitarias:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        filter_results,
        group_results_by_period,
        find_results_by_date_range,
        get_top_results,
        summarize_results
    )
    
    resultados = [result1, result2, result3, ...]
    
    # Filtrar solo alertas con diferencia > $500
    alertas_grandes = filter_results(
        resultados,
        estado="Alerta",
        min_diferencia=500.0
    )
    
    # Agrupar por mes
    por_mes = group_results_by_period(resultados, group_by="month")
    for mes, resultados_mes in por_mes.items():
        print(f"{mes}: {len(resultados_mes)} comparaciones")
    
    # Encontrar resultados en un rango
    en_enero = find_results_by_date_range(
        resultados, "2024-01-01", "2024-01-31"
    )
    
    # Top 10 por diferencia
    top_10 = get_top_results(resultados, n=10, by="diferencia")
    
    # Resumen estadístico
    resumen = summarize_results(resultados)
    print(f"Total: {resumen['total']}, Alertas: {resumen['alertas']}")
    print(f"Tasa de alertas: {resumen['tasa_alertas']:.2f}%")

**Ejemplo con exportación e importación:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        export_results_to_csv,
        export_results_to_json,
        load_results_from_json,
        create_comparison_periods
    )
    
    resultados = [result1, result2, result3, ...]
    
    # Exportar a CSV
    csv_path = export_results_to_csv(resultados, "/tmp/comparaciones.csv")
    
    # Exportar a JSON
    json_path = export_results_to_json(resultados, "/tmp/comparaciones.json")
    
    # Cargar desde JSON
    resultados_cargados = load_results_from_json(json_path)
    
    # Crear períodos automáticamente
    periodos = create_comparison_periods(
        "2024-01-01", "2024-12-31", periodo="month"
    )
    # Retorna períodos mensuales para todo el año

**Ejemplo con funciones de testing y análisis:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        create_test_result,
        create_test_batch_result,
        compare_results_side_by_side,
        validate_result_consistency,
        merge_results,
        calculate_trend
    )
    
    # Crear resultado de prueba
    test_result = create_test_result(
        estado="Alerta",
        diferencia=150.0,
        ingreso_stripe=1000.0,
        ingreso_quickbooks=850.0
    )
    
    # Crear batch de prueba
    test_batch = create_test_batch_result(n_results=10, n_alertas=2)
    
    # Comparar dos resultados
    comparacion = compare_results_side_by_side(result1, result2)
    print(f"Diferencias: {comparacion['diferencias']}")
    
    # Validar consistencia
    es_valido, errores = validate_result_consistency(test_result)
    
    # Combinar resultados
    todos = merge_results(resultados_enero, resultados_febrero, deduplicate=True)
    
    # Calcular tendencia
    tendencia = calculate_trend(resultados, metric="diferencia")
    print(f"Tendencia: {tendencia['direction']} (R²={tendencia['r_squared']:.2f})")

**Ejemplo con reconciliación y verificación:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        reconcile_periods,
        verify_reconciliation,
        find_missing_periods,
        generate_reconciliation_report,
        check_balance_consistency
    )
    
    resultados = [result1, result2, result3, ...]
    
    # Reconciliar períodos
    reconciliacion = reconcile_periods(resultados, tolerance=1.0)
    print(f"Tasa de reconciliación: {reconciliacion['tasa_reconciliacion']:.2f}%")
    
    # Verificar reconciliación matemática
    verificacion = verify_reconciliation(1000.0, 950.0, 50.0, umbral=100.0)
    if verificacion['es_correcta']:
        print("✅ Reconciliación matemáticamente correcta")
    
    # Encontrar períodos faltantes
    periodos_esperados = create_comparison_periods("2024-01-01", "2024-12-31", "month")
    faltantes = find_missing_periods(periodos_esperados, resultados)
    if faltantes:
        print(f"⚠️ {len(faltantes)} períodos faltantes")
    
    # Generar reporte de reconciliación
    reporte = generate_reconciliation_report(resultados, format="html")
    
    # Verificar consistencia de balance
    consistencia = check_balance_consistency(resultados)
    if not consistencia['es_consistente']:
        print(f"❌ {len(consistencia['inconsistencias'])} inconsistencias encontradas")

**Ejemplo con métricas y optimización:**
    from data.airflow.dags.stripe_quickbooks_revenue_compare import (
        aggregate_metrics,
        generate_dashboard_data,
        optimize_threshold,
        audit_comparison_history
    )
    
    resultados = [result1, result2, result3, ...]
    
    # Agregar métricas por mes
    metricas = aggregate_metrics(resultados, group_by="month")
    print(f"Total ingresos: ${metricas['totales']['total_ingreso_stripe']:,.2f}")
    
    # Generar datos para dashboard
    dashboard_data = generate_dashboard_data(resultados, window_days=30)
    # Usar en dashboard frontend
    
    # Optimizar umbral automáticamente
    optimizacion = optimize_threshold(resultados, target_alert_rate=5.0)
    umbral_optimizado = optimizacion['umbral_recomendado']
    print(f"Umbral recomendado: ${umbral_optimizado:.2f}")
    
    # Auditoría completa
    auditoria = audit_comparison_history(resultados, lookback_days=90)
    print(f"Hallazgos: {auditoria['total_hallazgos']} ({auditoria['hallazgos_altos']} altos)")
    
    # Health check del sistema
    health = perform_system_health_check(
        test_period=("2024-01-01", "2024-01-31"),
        umbral_test=100.0
    )
    print(f"Estado del sistema: {health['status']}")
    
    # Auto-corrección de problemas
    fixes = auto_fix_common_issues(resultados, dry_run=True)
    if fixes['issues_detected']:
        print(f"Problemas detectados: {len(fixes['issues_detected'])}")
        # Ejecutar con dry_run=False para aplicar correcciones
"""
import os
import logging
import time
import random
import hashlib
import json
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple, Callable, TypeVar, Union
from decimal import Decimal, ROUND_HALF_UP
from contextlib import contextmanager
from dataclasses import dataclass, field
from enum import Enum

# Intentar importar librerías opcionales
try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except ImportError:
    STATS_AVAILABLE = False

try:
    from tenacity import (
        retry,
        stop_after_attempt,
        wait_exponential,
        retry_if_exception_type,
        RetryError
    )
    TENACITY_AVAILABLE = True
except ImportError:
    TENACITY_AVAILABLE = False

try:
    from pydantic import BaseModel, Field, ValidationError
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

try:
    from cachetools import TTLCache
    CACHETOOLS_AVAILABLE = True
except ImportError:
    CACHETOOLS_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False

try:
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry
    REQUESTS_ADAPTERS_AVAILABLE = True
except ImportError:
    REQUESTS_ADAPTERS_AVAILABLE = False

# Configurar logging
logger = logging.getLogger(__name__)

STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")
QUICKBOOKS_ACCESS_TOKEN = os.environ.get("QUICKBOOKS_ACCESS_TOKEN", "")
QUICKBOOKS_REALM_ID = os.environ.get("QUICKBOOKS_REALM_ID", "")
QUICKBOOKS_BASE = os.environ.get("QUICKBOOKS_BASE", "https://sandbox-quickbooks.api.intuit.com")

# Configuración de retry para peticiones
DEFAULT_MAX_RETRIES = 3
DEFAULT_RETRY_DELAY = 1.0  # segundos
DEFAULT_TIMEOUT = 30

# Cache para búsquedas de cuentas de QuickBooks
_account_cache: Optional[Any] = None
if CACHETOOLS_AVAILABLE:
    _account_cache = TTLCache(maxsize=50, ttl=3600)  # 1 hora TTL

# Constantes de configuración por defecto
# Estas pueden ser sobrescritas por variables de entorno

# Circuit breaker
CIRCUIT_BREAKER_FAILURE_THRESHOLD = int(os.getenv("REVENUE_COMPARE_CB_FAILURE_THRESHOLD", "10"))
CIRCUIT_BREAKER_RESET_MINUTES = int(os.getenv("REVENUE_COMPARE_CB_RESET_MINUTES", "15"))

# Jitter para retries (evitar thundering herd)
RETRY_JITTER_MAX = float(os.getenv("REVENUE_COMPARE_RETRY_JITTER_MAX", "1.0"))  # segundos

# Progress reporting
PROGRESS_REPORT_INTERVAL = int(os.getenv("REVENUE_COMPARE_PROGRESS_INTERVAL", "10"))  # reportar cada N comparaciones

# Feature flags desde variables de entorno
FEATURE_ENABLE_PARALLEL = os.getenv("REVENUE_COMPARE_ENABLE_PARALLEL", "false").lower() == "true"
FEATURE_ENABLE_CIRCUIT_BREAKER = os.getenv("REVENUE_COMPARE_ENABLE_CB", "true").lower() == "true"
FEATURE_ENABLE_METRICS = os.getenv("REVENUE_COMPARE_ENABLE_METRICS", "true").lower() == "true"
FEATURE_ENABLE_ANOMALY_DETECTION = os.getenv("REVENUE_COMPARE_ENABLE_ANOMALY_DETECTION", "false").lower() == "true"
FEATURE_ENABLE_TREND_ANALYSIS = os.getenv("REVENUE_COMPARE_ENABLE_TREND_ANALYSIS", "true").lower() == "true"
FEATURE_ENABLE_NOTIFICATIONS = os.getenv("REVENUE_COMPARE_ENABLE_NOTIFICATIONS", "true").lower() == "true"
FEATURE_ENABLE_PERSISTENCE = os.getenv("REVENUE_COMPARE_ENABLE_PERSISTENCE", "true").lower() == "true"
FEATURE_ENABLE_CACHE = os.getenv("REVENUE_COMPARE_ENABLE_CACHE", "true").lower() == "true"

# Timeouts configurables
DEFAULT_TIMEOUT = int(os.getenv("REVENUE_COMPARE_DEFAULT_TIMEOUT", "30"))
DEFAULT_RETRY_DELAY = float(os.getenv("REVENUE_COMPARE_RETRY_DELAY", "1.0"))
DEFAULT_MAX_RETRIES = int(os.getenv("REVENUE_COMPARE_MAX_RETRIES", "3"))

# Límites de batch processing
MAX_BATCH_WORKERS = int(os.getenv("REVENUE_COMPARE_MAX_BATCH_WORKERS", "5"))
MAX_BATCH_SIZE = int(os.getenv("REVENUE_COMPARE_MAX_BATCH_SIZE", "100"))

# Umbrales por defecto
DEFAULT_THRESHOLD = float(os.getenv("REVENUE_COMPARE_DEFAULT_THRESHOLD", "100.0"))
CRITICAL_DISCREPANCY_THRESHOLD = float(os.getenv("REVENUE_COMPARE_CRITICAL_THRESHOLD", "1000.0"))

# Anomaly detection
ANOMALY_Z_SCORE_THRESHOLD = float(os.getenv("REVENUE_COMPARE_ANOMALY_Z_THRESHOLD", "2.0"))

# Type hints para mejor tipado
T = TypeVar('T')
# Nota: ComparisonResult y BatchComparisonResult ahora son clases dataclass,
# pero mantenemos los aliases para compatibilidad con código existente
ComparisonResultDict = Dict[str, Any]
BatchComparisonResultDict = Dict[str, Any]


# Excepciones personalizadas
class RevenueCompareError(Exception):
    """Excepción base para errores de comparación de ingresos."""
    pass


class StripeAPIError(RevenueCompareError):
    """Error en la API de Stripe."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class QuickBooksAPIError(RevenueCompareError):
    """Error en la API de QuickBooks."""
    def __init__(self, message: str, status_code: Optional[int] = None, error_data: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data


class ValidationError(RevenueCompareError):
    """Error de validación de parámetros."""
    pass


class ComparisonState(Enum):
    """Estados posibles de la comparación."""
    OK = "Ok"
    ALERTA = "Alerta"
    ERROR = "Error"


@dataclass
class RevenueCompareGlobalConfig:
    """
    Configuración global para el módulo de comparación de ingresos.
    Lee valores desde variables de entorno con defaults sensatos.
    """
    # Feature flags
    enable_parallel: bool = FEATURE_ENABLE_PARALLEL
    enable_circuit_breaker: bool = FEATURE_ENABLE_CIRCUIT_BREAKER
    enable_metrics: bool = FEATURE_ENABLE_METRICS
    enable_anomaly_detection: bool = FEATURE_ENABLE_ANOMALY_DETECTION
    enable_trend_analysis: bool = FEATURE_ENABLE_TREND_ANALYSIS
    enable_notifications: bool = FEATURE_ENABLE_NOTIFICATIONS
    enable_persistence: bool = FEATURE_ENABLE_PERSISTENCE
    enable_cache: bool = FEATURE_ENABLE_CACHE
    
    # Timeouts y retries
    default_timeout: int = DEFAULT_TIMEOUT
    default_retry_delay: float = DEFAULT_RETRY_DELAY
    default_max_retries: int = DEFAULT_MAX_RETRIES
    retry_jitter_max: float = RETRY_JITTER_MAX
    
    # Circuit breaker
    circuit_breaker_failure_threshold: int = CIRCUIT_BREAKER_FAILURE_THRESHOLD
    circuit_breaker_reset_minutes: int = CIRCUIT_BREAKER_RESET_MINUTES
    
    # Batch processing
    max_batch_workers: int = MAX_BATCH_WORKERS
    max_batch_size: int = MAX_BATCH_SIZE
    progress_report_interval: int = PROGRESS_REPORT_INTERVAL
    
    # Umbrales
    default_threshold: float = DEFAULT_THRESHOLD
    critical_discrepancy_threshold: float = CRITICAL_DISCREPANCY_THRESHOLD
    
    # Anomaly detection
    anomaly_z_score_threshold: float = ANOMALY_Z_SCORE_THRESHOLD
    
    # APIs
    stripe_api_key: Optional[str] = None
    qb_access_token: Optional[str] = None
    qb_realm_id: Optional[str] = None
    qb_base: Optional[str] = None
    
    # Cuenta por defecto
    default_quickbooks_account: str = "Ventas Stripe"
    
    @classmethod
    def from_env(cls) -> 'RevenueCompareGlobalConfig':
        """
        Crea una instancia desde variables de entorno.
        
        Returns:
            Instancia de RevenueCompareGlobalConfig con valores desde env vars
        """
        return cls(
            enable_parallel=FEATURE_ENABLE_PARALLEL,
            enable_circuit_breaker=FEATURE_ENABLE_CIRCUIT_BREAKER,
            enable_metrics=FEATURE_ENABLE_METRICS,
            enable_anomaly_detection=FEATURE_ENABLE_ANOMALY_DETECTION,
            enable_trend_analysis=FEATURE_ENABLE_TREND_ANALYSIS,
            enable_notifications=FEATURE_ENABLE_NOTIFICATIONS,
            enable_persistence=FEATURE_ENABLE_PERSISTENCE,
            enable_cache=FEATURE_ENABLE_CACHE,
            default_timeout=DEFAULT_TIMEOUT,
            default_retry_delay=DEFAULT_RETRY_DELAY,
            default_max_retries=DEFAULT_MAX_RETRIES,
            retry_jitter_max=RETRY_JITTER_MAX,
            circuit_breaker_failure_threshold=CIRCUIT_BREAKER_FAILURE_THRESHOLD,
            circuit_breaker_reset_minutes=CIRCUIT_BREAKER_RESET_MINUTES,
            max_batch_workers=MAX_BATCH_WORKERS,
            max_batch_size=MAX_BATCH_SIZE,
            progress_report_interval=PROGRESS_REPORT_INTERVAL,
            default_threshold=DEFAULT_THRESHOLD,
            critical_discrepancy_threshold=CRITICAL_DISCREPANCY_THRESHOLD,
            anomaly_z_score_threshold=ANOMALY_Z_SCORE_THRESHOLD,
            stripe_api_key=os.getenv("STRIPE_API_KEY"),
            qb_access_token=os.getenv("QUICKBOOKS_ACCESS_TOKEN"),
            qb_realm_id=os.getenv("QUICKBOOKS_REALM_ID"),
            qb_base=os.getenv("QUICKBOOKS_BASE", "https://sandbox-quickbooks.api.intuit.com"),
            default_quickbooks_account=os.getenv("REVENUE_COMPARE_DEFAULT_ACCOUNT", "Ventas Stripe")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario (sin secrets)."""
        return {
            "enable_parallel": self.enable_parallel,
            "enable_circuit_breaker": self.enable_circuit_breaker,
            "enable_metrics": self.enable_metrics,
            "enable_anomaly_detection": self.enable_anomaly_detection,
            "enable_trend_analysis": self.enable_trend_analysis,
            "enable_notifications": self.enable_notifications,
            "enable_persistence": self.enable_persistence,
            "enable_cache": self.enable_cache,
            "default_timeout": self.default_timeout,
            "default_retry_delay": self.default_retry_delay,
            "default_max_retries": self.default_max_retries,
            "retry_jitter_max": self.retry_jitter_max,
            "circuit_breaker_failure_threshold": self.circuit_breaker_failure_threshold,
            "circuit_breaker_reset_minutes": self.circuit_breaker_reset_minutes,
            "max_batch_workers": self.max_batch_workers,
            "max_batch_size": self.max_batch_size,
            "progress_report_interval": self.progress_report_interval,
            "default_threshold": self.default_threshold,
            "critical_discrepancy_threshold": self.critical_discrepancy_threshold,
            "anomaly_z_score_threshold": self.anomaly_z_score_threshold,
            "default_quickbooks_account": self.default_quickbooks_account,
            "has_stripe_api_key": bool(self.stripe_api_key),
            "has_qb_access_token": bool(self.qb_access_token),
            "has_qb_realm_id": bool(self.qb_realm_id),
            "qb_base": self.qb_base
        }
    
    def __str__(self) -> str:
        """Representación legible de la configuración."""
        return f"RevenueCompareGlobalConfig(features={sum([self.enable_parallel, self.enable_circuit_breaker, self.enable_metrics])}/7 enabled)"
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return f"RevenueCompareGlobalConfig.from_env()"


# Instancia global de configuración (singleton pattern)
_global_config: Optional[RevenueCompareGlobalConfig] = None


def get_global_config() -> RevenueCompareGlobalConfig:
    """
    Obtiene la configuración global (singleton).
    
    Returns:
        Instancia de RevenueCompareGlobalConfig
    """
    global _global_config
    if _global_config is None:
        _global_config = RevenueCompareGlobalConfig.from_env()
    return _global_config


def reset_global_config() -> None:
    """Resetea la configuración global (útil para tests)."""
    global _global_config
    _global_config = None


@dataclass
class ComparisonResult:
    """
    Resultado estructurado de una comparación de ingresos.
    
    Attributes:
        estado: Estado de la comparación ("Ok", "Alerta", "Error")
        diferencia: Diferencia absoluta entre ingresos
        diferencia_porcentual: Diferencia porcentual
        ingreso_stripe: Ingreso neto de Stripe
        ingreso_quickbooks: Ingreso de QuickBooks
        detalles: Diccionario con detalles adicionales
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha de fin del período
        umbral: Umbral configurado
        cuenta_quickbooks: Cuenta de QuickBooks usada
        timestamp: Timestamp de cuando se realizó la comparación
        duration_ms: Duración de la comparación en milisegundos
    
    Example:
        >>> result = ComparisonResult.from_dict(comparar_ingresos_stripe_quickbooks(...))
        >>> if result.is_ok:
        ...     print(f"Comparación OK: diferencia ${result.diferencia:.2f}")
        >>> elif result.is_alerta:
        ...     print(f"ALERTA: diferencia ${result.diferencia:.2f} excede umbral ${result.umbral:.2f}")
    """
    estado: str
    diferencia: float
    diferencia_porcentual: float
    ingreso_stripe: float
    ingreso_quickbooks: float
    detalles: Dict[str, Any]
    fecha_inicio: str
    fecha_fin: str
    umbral: float
    cuenta_quickbooks: str
    timestamp: Optional[float] = None
    duration_ms: Optional[float] = None
    
    @property
    def is_ok(self) -> bool:
        """Retorna True si la comparación está OK (sin alertas)."""
        return self.estado == "Ok"
    
    @property
    def is_alerta(self) -> bool:
        """Retorna True si hay una alerta."""
        return self.estado == "Alerta"
    
    @property
    def is_error(self) -> bool:
        """Retorna True si hubo un error."""
        return self.estado == "Error"
    
    @property
    def exceeds_threshold(self) -> bool:
        """Retorna True si la diferencia excede el umbral."""
        return abs(self.diferencia) > self.umbral
    
    @property
    def difference_percentage(self) -> float:
        """Retorna el porcentaje de diferencia."""
        return self.diferencia_porcentual
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "estado": self.estado,
            "diferencia": self.diferencia,
            "diferencia_porcentual": self.diferencia_porcentual,
            "ingreso_stripe": self.ingreso_stripe,
            "ingreso_quickbooks": self.ingreso_quickbooks,
            "detalles": self.detalles,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "umbral": self.umbral,
            "cuenta_quickbooks": self.cuenta_quickbooks,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms
        }
    
    def to_json(self) -> str:
        """Convierte el resultado a JSON string."""
        return serialize_comparison_result(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonResult':
        """
        Crea una instancia desde un diccionario.
        
        Args:
            data: Diccionario con el resultado de comparación
        
        Returns:
            Instancia de ComparisonResult
        """
        detalles = data.get("detalles", {})
        return cls(
            estado=data.get("estado", "Error"),
            diferencia=float(detalles.get("diferencia", 0.0)),
            diferencia_porcentual=float(detalles.get("diferencia_porcentual", 0.0)),
            ingreso_stripe=float(detalles.get("ingreso_stripe", 0.0)),
            ingreso_quickbooks=float(detalles.get("ingreso_quickbooks", 0.0)),
            detalles=detalles,
            fecha_inicio=detalles.get("fecha_inicio", data.get("fecha_inicio", "")),
            fecha_fin=detalles.get("fecha_fin", data.get("fecha_fin", "")),
            umbral=float(detalles.get("umbral", 0.0)),
            cuenta_quickbooks=detalles.get("cuenta_quickbooks", ""),
            timestamp=data.get("timestamp"),
            duration_ms=data.get("duration_ms")
        )
    
    def __str__(self) -> str:
        """Representación string legible."""
        status_emoji = "✅" if self.is_ok else "⚠️" if self.is_alerta else "❌"
        return (
            f"{status_emoji} {self.estado} | "
            f"Diferencia: ${self.diferencia:,.2f} ({self.diferencia_porcentual:.2f}%) | "
            f"Período: {self.fecha_inicio} - {self.fecha_fin}"
        )
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return (
            f"ComparisonResult(estado={self.estado}, "
            f"diferencia={self.diferencia:.2f}, "
            f"umbral={self.umbral:.2f})"
        )
    
    def __eq__(self, other: Any) -> bool:
        """Compara dos ComparisonResult por igualdad."""
        if not isinstance(other, ComparisonResult):
            return False
        return (
            self.estado == other.estado
            and abs(self.diferencia - other.diferencia) < 0.01
            and self.fecha_inicio == other.fecha_inicio
            and self.fecha_fin == other.fecha_fin
        )
    
    def __lt__(self, other: Any) -> bool:
        """Compara por diferencia (para ordenamiento)."""
        if not isinstance(other, ComparisonResult):
            return NotImplemented
        return abs(self.diferencia) < abs(other.diferencia)
    
    def __le__(self, other: Any) -> bool:
        """Compara por diferencia (para ordenamiento)."""
        if not isinstance(other, ComparisonResult):
            return NotImplemented
        return abs(self.diferencia) <= abs(other.diferencia)
    
    def __gt__(self, other: Any) -> bool:
        """Compara por diferencia (para ordenamiento)."""
        if not isinstance(other, ComparisonResult):
            return NotImplemented
        return abs(self.diferencia) > abs(other.diferencia)
    
    def __ge__(self, other: Any) -> bool:
        """Compara por diferencia (para ordenamiento)."""
        if not isinstance(other, ComparisonResult):
            return NotImplemented
        return abs(self.diferencia) >= abs(other.diferencia)
    
    def __hash__(self) -> int:
        """Hash para usar en sets y dicts."""
        return hash((
            self.estado,
            round(self.diferencia, 2),
            self.fecha_inicio,
            self.fecha_fin,
            round(self.umbral, 2)
        ))


@dataclass
class BatchComparisonResult:
    """
    Resultado de comparación en batch para múltiples períodos.
    
    Attributes:
        total: Número total de comparaciones
        exitosos: Número de comparaciones exitosas
        fallidos: Número de comparaciones fallidas
        alertas: Número de alertas generadas
        resultados: Lista de resultados individuales
        duration_ms: Duración total en milisegundos
        throughput: Throughput en comparaciones por segundo
    
    Example:
        >>> batch = BatchComparisonResult.from_dict(comparar_ingresos_batch(...))
        >>> print(f"Éxito: {batch.success_rate:.2f}%")
        >>> print(f"Alertas: {batch.alertas}")
    """
    total: int
    exitosos: int
    fallidos: int
    alertas: int
    resultados: List[ComparisonResult]
    duration_ms: float
    throughput: Optional[float] = None
    
    @property
    def success_rate(self) -> float:
        """Tasa de éxito en porcentaje."""
        if self.total == 0:
            return 0.0
        return (self.exitosos / self.total) * 100.0
    
    @property
    def failure_rate(self) -> float:
        """Tasa de fallo en porcentaje."""
        if self.total == 0:
            return 0.0
        return (self.fallidos / self.total) * 100.0
    
    @property
    def alert_rate(self) -> float:
        """Tasa de alertas en porcentaje."""
        if self.total == 0:
            return 0.0
        return (self.alertas / self.total) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el resultado a diccionario."""
        return {
            "total": self.total,
            "exitosos": self.exitosos,
            "fallidos": self.fallidos,
            "alertas": self.alertas,
            "success_rate": self.success_rate,
            "failure_rate": self.failure_rate,
            "alert_rate": self.alert_rate,
            "duration_ms": self.duration_ms,
            "duration_formatted": format_duration(self.duration_ms),
            "throughput": self.throughput,
            "resultados": [r.to_dict() for r in self.resultados]
        }
    
    def to_json(self) -> str:
        """Convierte el resultado a JSON string."""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False, indent=2)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchComparisonResult':
        """
        Crea una instancia desde un diccionario.
        
        Args:
            data: Diccionario con el resultado de batch
        
        Returns:
            Instancia de BatchComparisonResult
        """
        resultados = [
            ComparisonResult.from_dict(r) if isinstance(r, dict) else r
            for r in data.get("resultados", [])
        ]
        
        return cls(
            total=data.get("total", 0),
            exitosos=data.get("exitosos", 0),
            fallidos=data.get("fallidos", 0),
            alertas=data.get("alertas", 0),
            resultados=resultados,
            duration_ms=float(data.get("duration_ms", 0.0)),
            throughput=data.get("throughput")
        )
    
    def __str__(self) -> str:
        """Representación string legible."""
        return (
            f"BatchComparisonResult: {self.exitosos}/{self.total} exitosos "
            f"({self.success_rate:.1f}%), {self.alertas} alertas, "
            f"{format_duration(self.duration_ms)}"
        )
    
    def __repr__(self) -> str:
        """Representación técnica."""
        return (
            f"BatchComparisonResult(total={self.total}, "
            f"exitosos={self.exitosos}, alertas={self.alertas}, "
            f"success_rate={self.success_rate:.2f}%)"
        )
    
    def __eq__(self, other: Any) -> bool:
        """Compara dos BatchComparisonResult por igualdad."""
        if not isinstance(other, BatchComparisonResult):
            return False
        return (
            self.total == other.total
            and self.exitosos == other.exitosos
            and self.fallidos == other.fallidos
            and self.alertas == other.alertas
        )
    
    def __lt__(self, other: Any) -> bool:
        """Compara por success_rate (para ordenamiento)."""
        if not isinstance(other, BatchComparisonResult):
            return NotImplemented
        return self.success_rate < other.success_rate
    
    def __hash__(self) -> int:
        """Hash para usar en sets y dicts."""
        return hash((
            self.total,
            self.exitosos,
            self.fallidos,
            self.alertas,
            round(self.duration_ms, 2)
        ))


@dataclass
class ComparisonConfig:
    """Configuración para la comparación de ingresos."""
    fecha_inicio: str
    fecha_fin: str
    umbral: float = 100.0
    cuenta_quickbooks: str = "Ventas Stripe"
    stripe_api_key: Optional[str] = None
    qb_access_token: Optional[str] = None
    qb_realm_id: Optional[str] = None
    qb_base: Optional[str] = None
    enable_stats: bool = True
    enable_logging: bool = True
    
    def __post_init__(self):
        """Normaliza y valida la configuración después de la inicialización."""
        # Normalizar fechas
        try:
            self.fecha_inicio = _normalize_date_string(self.fecha_inicio)
            self.fecha_fin = _normalize_date_string(self.fecha_fin)
        except ValueError as e:
            raise ValidationError(f"Error normalizando fechas: {str(e)}")
        
        # Normalizar umbral
        try:
            self.umbral = float(_normalize_amount(self.umbral))
        except (ValueError, TypeError) as e:
            raise ValidationError(f"Error normalizando umbral: {str(e)}")
        
        # Sanitizar nombre de cuenta
        self.cuenta_quickbooks = _sanitize_account_name(self.cuenta_quickbooks)
        if not self.cuenta_quickbooks:
            raise ValidationError("cuenta_quickbooks no puede estar vacío después de sanitización")
    
    def __str__(self) -> str:
        """Representación string legible de la configuración."""
        return (
            f"ComparisonConfig("
            f"periodo={self.fecha_inicio} a {self.fecha_fin}, "
            f"umbral=${self.umbral:.2f}, "
            f"cuenta={self.cuenta_quickbooks})"
        )
    
    def __repr__(self) -> str:
        """Representación técnica de la configuración."""
        return (
            f"ComparisonConfig("
            f"fecha_inicio='{self.fecha_inicio}', "
            f"fecha_fin='{self.fecha_fin}', "
            f"umbral={self.umbral}, "
            f"cuenta_quickbooks='{self.cuenta_quickbooks}', "
            f"enable_stats={self.enable_stats})"
        )
    
    def validate(self) -> Optional[ValidationError]:
        """
        Valida la configuración.
        
        Returns:
            ValidationError si hay problemas, None si es válida
        """
        error, _, _ = _validate_date_range(self.fecha_inicio, self.fecha_fin)
        if error:
            return error
        
        if self.umbral < 0:
            return ValidationError("umbral debe ser mayor o igual a 0")
        
        if not self.cuenta_quickbooks or not self.cuenta_quickbooks.strip():
            return ValidationError("cuenta_quickbooks no puede estar vacío")
        
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "umbral": self.umbral,
            "cuenta_quickbooks": self.cuenta_quickbooks,
            "enable_stats": self.enable_stats,
            "enable_logging": self.enable_logging
        }
    
    def to_json(self) -> str:
        """Convierte la configuración a JSON string."""
        return json.dumps(self.to_dict(), default=str, ensure_ascii=False, indent=2)
    
    @property
    def period_days(self) -> int:
        """Retorna el número de días en el período."""
        try:
            inicio = datetime.strptime(self.fecha_inicio, "%Y-%m-%d")
            fin = datetime.strptime(self.fecha_fin, "%Y-%m-%d")
            return (fin - inicio).days + 1
        except ValueError:
            return 0
    
    @property
    def is_valid(self) -> bool:
        """Retorna True si la configuración es válida."""
        return self.validate() is None
    
    def __eq__(self, other: Any) -> bool:
        """Compara dos ComparisonConfig por igualdad."""
        if not isinstance(other, ComparisonConfig):
            return False
        return (
            self.fecha_inicio == other.fecha_inicio
            and self.fecha_fin == other.fecha_fin
            and abs(self.umbral - other.umbral) < 0.01
            and self.cuenta_quickbooks == other.cuenta_quickbooks
        )
    
    def __hash__(self) -> int:
        """Hash para usar en sets y dicts."""
        return hash((
            self.fecha_inicio,
            self.fecha_fin,
            round(self.umbral, 2),
            self.cuenta_quickbooks
        ))
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ComparisonConfig':
        """
        Crea una instancia desde un diccionario.
        
        Args:
            data: Diccionario con los datos de configuración
        
        Returns:
            Instancia de ComparisonConfig
        """
        return cls(**data)
    
    @classmethod
    def from_global_config(
        cls,
        fecha_inicio: str,
        fecha_fin: str,
        umbral: Optional[float] = None,
        cuenta_quickbooks: Optional[str] = None
    ) -> 'ComparisonConfig':
        """
        Crea una instancia usando valores de la configuración global.
        
        Args:
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
            umbral: Umbral (usa default de global config si None)
            cuenta_quickbooks: Cuenta de QuickBooks (usa default de global config si None)
        
        Returns:
            Instancia de ComparisonConfig
        """
        global_cfg = get_global_config()
        return cls(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            umbral=umbral if umbral is not None else global_cfg.default_threshold,
            cuenta_quickbooks=cuenta_quickbooks or global_cfg.default_quickbooks_account,
            stripe_api_key=global_cfg.stripe_api_key,
            qb_access_token=global_cfg.qb_access_token,
            qb_realm_id=global_cfg.qb_realm_id,
            qb_base=global_cfg.qb_base,
            enable_stats=global_cfg.enable_metrics,
            enable_logging=True
        )


if PYDANTIC_AVAILABLE:
    class ComparisonResultModel(BaseModel):
        """Modelo Pydantic para resultados de comparación."""
        estado: str = Field(..., description="Estado de la comparación")
        detalles: Dict[str, Any] = Field(..., description="Detalles de la comparación")
        
        class Config:
            """Configuración del modelo."""
            json_encoders = {Decimal: lambda v: float(v)}
    
    class StripeRevenueResult(BaseModel):
        """Modelo para resultados de ingresos de Stripe."""
        ingreso_neto: Decimal = Field(..., ge=0, description="Ingreso neto total")
        cantidad_transacciones: int = Field(..., ge=0, description="Cantidad de transacciones")
        estado: str = Field(..., description="Estado de la operación")
        
        class Config:
            json_encoders = {Decimal: lambda v: float(v)}
    
    class QuickBooksRevenueResult(BaseModel):
        """Modelo para resultados de ingresos de QuickBooks."""
        ingreso_total: Decimal = Field(..., ge=0, description="Ingreso total")
        cantidad_transacciones: int = Field(..., ge=0, description="Cantidad de transacciones")
        estado: str = Field(..., description="Estado de la operación")
        
        class Config:
            json_encoders = {Decimal: lambda v: float(v)}


@dataclass
class RevenueComparisonClient:
    """
    Cliente para realizar comparaciones de ingresos con características avanzadas.
    
    Incluye:
    - Caching de búsquedas de cuentas
    - Health checks
    - Sessions mejoradas con retry
    - Soporte para httpx
    - Circuit breaker
    """
    stripe_api_key: Optional[str] = None
    qb_access_token: Optional[str] = None
    qb_realm_id: Optional[str] = None
    qb_base: Optional[str] = None
    use_httpx: bool = False
    enable_cache: bool = True
    timeout: int = DEFAULT_TIMEOUT
    
    def __post_init__(self):
        """Inicializa sesiones y recursos después de crear el dataclass."""
        self.stripe_api_key = self.stripe_api_key or STRIPE_API_KEY
        self.qb_access_token = self.qb_access_token or QUICKBOOKS_ACCESS_TOKEN
        self.qb_realm_id = self.qb_realm_id or QUICKBOOKS_REALM_ID
        self.qb_base = self.qb_base or QUICKBOOKS_BASE
        
        # Crear sesiones HTTP
        if self.use_httpx and HTTPX_AVAILABLE:
            self._stripe_session = self._create_httpx_session()
            self._qb_session = self._create_httpx_session()
            self._use_httpx = True
        else:
            self._stripe_session = self._create_requests_session()
            self._qb_session = self._create_requests_session()
            self._use_httpx = False
    
    def _create_requests_session(self) -> requests.Session:
        """Crea una sesión de requests con retry strategy mejorada."""
        session = requests.Session()
        
        if REQUESTS_ADAPTERS_AVAILABLE:
            retry_strategy = Retry(
                total=DEFAULT_MAX_RETRIES,
                backoff_factor=DEFAULT_RETRY_DELAY,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST"],
                raise_on_status=False
            )
            adapter = HTTPAdapter(max_retries=retry_strategy)
            session.mount("http://", adapter)
            session.mount("https://", adapter)
        
        return session
    
    def _create_httpx_session(self):
        """Crea una sesión httpx con configuración mejorada."""
        if not HTTPX_AVAILABLE:
            raise RuntimeError("httpx no está disponible")
        
        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        timeout = httpx.Timeout(self.timeout, connect=10.0)
        
        return httpx.Client(
            limits=limits,
            timeout=timeout,
            follow_redirects=True,
            http2=True
        )
    
    def health_check(self) -> Dict[str, Any]:
        """
        Realiza un health check de las conexiones con Stripe y QuickBooks.
        
        Returns:
            Dict con el estado de salud de ambos servicios.
        """
        health_status = {
            "status": "ok",
            "timestamp": time.time(),
            "checks": {}
        }
        
        # Check Stripe
        if not self.stripe_api_key:
            health_status["checks"]["stripe"] = {
                "status": "error",
                "error": "STRIPE_API_KEY no configurado"
            }
            health_status["status"] = "error"
        else:
            try:
                # Test simple de conectividad con Stripe
                headers = {"Authorization": f"Bearer {self.stripe_api_key}"}
                if self._use_httpx:
                    response = self._stripe_session.get(
                        "https://api.stripe.com/v1/charges",
                        headers=headers,
                        params={"limit": 1},
                        timeout=5
                    )
                else:
                    response = self._stripe_session.get(
                        "https://api.stripe.com/v1/charges",
                        headers=headers,
                        params={"limit": 1},
                        timeout=5
                    )
                
                if response.status_code in [200, 401]:  # 401 es válido (solo verifica conectividad)
                    health_status["checks"]["stripe"] = {"status": "ok"}
                else:
                    health_status["checks"]["stripe"] = {
                        "status": "warning",
                        "status_code": response.status_code
                    }
                    if health_status["status"] == "ok":
                        health_status["status"] = "degraded"
            except Exception as e:
                health_status["checks"]["stripe"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["status"] = "error"
        
        # Check QuickBooks
        if not self.qb_access_token or not self.qb_realm_id:
            health_status["checks"]["quickbooks"] = {
                "status": "error",
                "error": "QUICKBOOKS_ACCESS_TOKEN o QUICKBOOKS_REALM_ID no configurado"
            }
            health_status["status"] = "error"
        else:
            try:
                url = f"{self.qb_base}/v3/company/{self.qb_realm_id}/query"
                headers = {
                    "Authorization": f"Bearer {self.qb_access_token}",
                    "Accept": "application/json",
                    "Content-Type": "application/text"
                }
                params = {"minorversion": "65", "query": "SELECT COUNT(*) FROM Account MAXRESULTS 1"}
                
                if self._use_httpx:
                    response = self._qb_session.get(url, headers=headers, params=params, timeout=10)
                else:
                    response = self._qb_session.get(url, headers=headers, params=params, timeout=10)
                
                if response.status_code == 200:
                    health_status["checks"]["quickbooks"] = {"status": "ok"}
                elif response.status_code == 401:
                    health_status["checks"]["quickbooks"] = {
                        "status": "error",
                        "error": "Autenticación fallida"
                    }
                    health_status["status"] = "error"
                else:
                    health_status["checks"]["quickbooks"] = {
                        "status": "warning",
                        "status_code": response.status_code
                    }
                    if health_status["status"] == "ok":
                        health_status["status"] = "degraded"
            except Exception as e:
                health_status["checks"]["quickbooks"] = {
                    "status": "error",
                    "error": str(e)
                }
                health_status["status"] = "error"
        
        # Check cache
        if self.enable_cache and CACHETOOLS_AVAILABLE and _account_cache:
            health_status["checks"]["cache"] = {
                "status": "ok",
                "size": len(_account_cache),
                "maxsize": _account_cache.maxsize
            }
        else:
            health_status["checks"]["cache"] = {"status": "disabled"}
        
        return health_status
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cierra las sesiones."""
        try:
            if self._use_httpx and HTTPX_AVAILABLE:
                self._stripe_session.close()
                self._qb_session.close()
            elif hasattr(self._stripe_session, 'close'):
                self._stripe_session.close()
                self._qb_session.close()
        except Exception as e:
            logger.debug(f"Error closing sessions: {e}")
        return False
    
    def __str__(self) -> str:
        """Representación string legible del cliente."""
        return (
            f"RevenueComparisonClient("
            f"stripe={bool(self.stripe_api_key)}, "
            f"quickbooks={bool(self.qb_access_token)}, "
            f"httpx={self._use_httpx}, "
            f"cache={self.enable_cache})"
        )
    
    def __repr__(self) -> str:
        """Representación técnica del cliente."""
        return (
            f"RevenueComparisonClient("
            f"use_httpx={self.use_httpx}, "
            f"enable_cache={self.enable_cache}, "
            f"timeout={self.timeout})"
        )


def _escape_query_string(value: str) -> str:
    """
    Escapa comillas simples en strings para queries de QuickBooks.
    Previene SQL injection en queries.
    
    Args:
        value: String a escapar
    
    Returns:
        String escapado
    """
    if not value:
        return ""
    return value.replace("'", "''")


def _normalize_date_string(date_str: str) -> str:
    """
    Normaliza una cadena de fecha al formato YYYY-MM-DD.
    
    Args:
        date_str: String de fecha en cualquier formato
    
    Returns:
        String normalizado en formato YYYY-MM-DD
    
    Raises:
        ValueError: Si la fecha no puede ser parseada
    """
    if not date_str or not date_str.strip():
        raise ValueError("Fecha no puede estar vacía")
    
    date_str = date_str.strip()
    
    # Intentar parsear con datetime
    try:
        # Formato YYYY-MM-DD
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    try:
        # Formato YYYY/MM/DD
        dt = datetime.strptime(date_str, "%Y/%m/%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    try:
        # Formato DD-MM-YYYY o DD/MM/YYYY
        for sep in ["-", "/"]:
            try:
                dt = datetime.strptime(date_str, f"%d{sep}%m{sep}%Y")
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
    except ValueError:
        pass
    
    # Si todo falla, lanzar error
    raise ValueError(f"No se pudo parsear la fecha: {date_str}")


def _normalize_amount(amount: Any) -> Decimal:
    """
    Normaliza un valor a Decimal para cálculos precisos.
    
    Args:
        amount: Valor numérico (int, float, Decimal, str)
    
    Returns:
        Decimal normalizado
    
    Raises:
        ValueError: Si el valor no puede ser convertido
    """
    if amount is None:
        return Decimal("0.0")
    
    if isinstance(amount, Decimal):
        return amount
    
    if isinstance(amount, (int, float)):
        return Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    if isinstance(amount, str):
        # Remover símbolos de moneda y espacios
        cleaned = amount.replace("$", "").replace(",", "").replace(" ", "").strip()
        try:
            return Decimal(cleaned).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        except (ValueError, TypeError):
            raise ValueError(f"No se pudo convertir a Decimal: {amount}")
    
    raise ValueError(f"Tipo no soportado para conversión a Decimal: {type(amount)}")


def _sanitize_account_name(name: str) -> str:
    """
    Sanitiza el nombre de una cuenta de QuickBooks.
    
    Args:
        name: Nombre de la cuenta
    
    Returns:
        Nombre sanitizado
    """
    if not name:
        return ""
    
    # Remover espacios al inicio y fin
    name = name.strip()
    
    # Remover caracteres especiales peligrosos
    # Mantener solo alfanuméricos, espacios y algunos caracteres especiales seguros
    import re
    name = re.sub(r'[^\w\s\-_&]', '', name)
    
    # Normalizar espacios múltiples
    name = re.sub(r'\s+', ' ', name)
    
    return name[:100]  # QuickBooks tiene límites de longitud


def _validate_date_range(
    fecha_inicio: str, 
    fecha_fin: str
) -> Tuple[Optional[ValidationError], Optional[datetime], Optional[datetime]]:
    """
    Valida el rango de fechas usando guard clauses.
    Función pura helper.
    
    Args:
        fecha_inicio: Fecha de inicio en formato YYYY-MM-DD
        fecha_fin: Fecha de fin en formato YYYY-MM-DD
    
    Returns:
        Tupla (ValidationError si hay error, fecha_inicio_dt, fecha_fin_dt)
    """
    if not fecha_inicio or not fecha_fin:
        return ValidationError("fecha_inicio y fecha_fin son requeridos"), None, None
    
    try:
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        
        if fecha_fin_dt < fecha_inicio_dt:
            return ValidationError("fecha_fin debe ser mayor o igual a fecha_inicio"), None, None
        
        return None, fecha_inicio_dt, fecha_fin_dt
    except ValueError as e:
        return ValidationError(f"fecha_inicio y fecha_fin deben estar en formato YYYY-MM-DD: {str(e)}"), None, None


def _extract_quickbooks_error(response_data: Dict[str, Any], status_code: int) -> str:
    """
    Extrae mensaje de error desde la estructura Fault de QuickBooks.
    Función pura helper.
    
    Args:
        response_data: Datos de la respuesta JSON
        status_code: Código de estado HTTP
    
    Returns:
        Mensaje de error extraído
    """
    fault = response_data.get("Fault", {})
    errors = fault.get("Error", [])
    
    if errors:
        error = errors[0] if isinstance(errors, list) else errors
        detail = error.get("Detail", "")
        message = error.get("Message", "")
        
        if detail:
            return f"{message}. {detail}".strip()
        return message or f"Error {status_code}"
    
    return f"Error {status_code}: {response_data.get('message', 'Error desconocido')}"


def _create_error_result(
    estado: str,
    motivo: str,
    ingreso_stripe: float = 0.0,
    ingreso_quickbooks: float = 0.0,
    diferencia: float = 0.0,
    umbral: float = 100.0,
    error_details: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Crea un resultado de error estructurado. Función pura helper.
    
    Args:
        estado: Estado del error
        motivo: Motivo del error
        ingreso_stripe: Ingreso de Stripe (default: 0.0)
        ingreso_quickbooks: Ingreso de QuickBooks (default: 0.0)
        diferencia: Diferencia calculada (default: 0.0)
        umbral: Umbral configurado (default: 100.0)
        error_details: Detalles adicionales del error (opcional)
    
    Returns:
        Dict con estructura de error
    """
    detalles = {
        "motivo": motivo,
        "ingreso_stripe": ingreso_stripe,
        "ingreso_quickbooks": ingreso_quickbooks,
        "diferencia": diferencia,
        "diferencia_absoluta": diferencia,
        "umbral": umbral
    }
    
    if error_details:
        detalles.update(error_details)
    
    return {
        "estado": estado,
        "detalles": detalles
    }


@contextmanager
def track_performance(operation_name: str, tags: Optional[Dict[str, str]] = None):
    """
    Context manager para trackear el performance de operaciones.
    
    Args:
        operation_name: Nombre de la operación
        tags: Tags adicionales para métricas
    
    Example:
        >>> with track_performance("fetch_stripe_data"):
        ...     data = fetch_stripe_data()
    """
    start_time = time.time()
    duration_ms = 0.0
    
    if STATS_AVAILABLE:
        try:
            Stats.incr(f"revenue_compare.{operation_name}.start", 1, tags=tags or {})
        except Exception:
            pass
    
    try:
        yield
        duration_ms = (time.time() - start_time) * 1000
        if STATS_AVAILABLE:
            try:
                Stats.timing(f"revenue_compare.{operation_name}.duration_ms", duration_ms, tags=tags or {})
                Stats.incr(f"revenue_compare.{operation_name}.success", 1, tags=tags or {})
            except Exception:
                pass
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        if STATS_AVAILABLE:
            try:
                Stats.timing(f"revenue_compare.{operation_name}.duration_ms", duration_ms, tags=tags or {})
                Stats.incr(f"revenue_compare.{operation_name}.error", 1, tags=tags or {})
            except Exception:
                pass
        logger.debug(f"{operation_name} failed after {duration_ms:.2f}ms: {e}")
        raise
    finally:
        if duration_ms > 0:
            logger.debug(f"{operation_name} took {duration_ms:.2f}ms")


@contextmanager
def comparison_context(
    fecha_inicio: str,
    fecha_fin: str,
    umbral: Optional[float] = None,
    cuenta_quickbooks: Optional[str] = None,
    auto_cleanup: bool = True
):
    """
    Context manager para realizar una comparación con limpieza automática.
    
    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        umbral: Umbral (usa default si None)
        cuenta_quickbooks: Cuenta de QuickBooks (usa default si None)
        auto_cleanup: Si True, limpia recursos automáticamente
    
    Yields:
        ComparisonResult: Resultado de la comparación
    
    Example:
        >>> with comparison_context("2024-01-01", "2024-01-31") as result:
        ...     if result.is_alerta:
        ...         print(f"Alerta: {result.diferencia}")
    """
    global_cfg = get_global_config()
    config = ComparisonConfig.from_global_config(
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        umbral=umbral,
        cuenta_quickbooks=cuenta_quickbooks
    )
    
    resultado_dict = None
    try:
        with track_performance("comparison_context.total"):
            resultado_dict = comparar_ingresos_stripe_quickbooks(
                fecha_inicio=config.fecha_inicio,
                fecha_fin=config.fecha_fin,
                umbral=config.umbral,
                cuenta_quickbooks=config.cuenta_quickbooks,
                enable_parallel=global_cfg.enable_parallel
            )
        
        resultado = ComparisonResult.from_dict(resultado_dict)
        yield resultado
        
    finally:
        if auto_cleanup:
            # Limpiar cache si es necesario
            if global_cfg.enable_cache and CACHETOOLS_AVAILABLE and _account_cache:
                # El cache se limpia automáticamente por TTL
                pass


@contextmanager
def batch_comparison_context(
    periodos: List[Dict[str, str]],
    umbral: Optional[float] = None,
    cuenta_quickbooks: Optional[str] = None,
    max_workers: Optional[int] = None
):
    """
    Context manager para realizar comparaciones en batch.
    
    Args:
        periodos: Lista de períodos con 'fecha_inicio' y 'fecha_fin'
        umbral: Umbral (usa default si None)
        cuenta_quickbooks: Cuenta de QuickBooks (usa default si None)
        max_workers: Workers máximos (usa default si None)
    
    Yields:
        BatchComparisonResult: Resultado del batch
    
    Example:
        >>> periodos = [
        ...     {"fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"},
        ...     {"fecha_inicio": "2024-02-01", "fecha_fin": "2024-02-28"}
        ... ]
        >>> with batch_comparison_context(periodos) as batch:
        ...     print(f"Éxito: {batch.success_rate:.2f}%")
    """
    global_cfg = get_global_config()
    
    if umbral is None:
        umbral = global_cfg.default_threshold
    if cuenta_quickbooks is None:
        cuenta_quickbooks = global_cfg.default_quickbooks_account
    if max_workers is None:
        max_workers = global_cfg.max_batch_workers
    
    resultado_dict = None
    try:
        with track_performance("batch_comparison_context.total"):
            resultado_dict = comparar_ingresos_batch(
                periodos=periodos,
                umbral=umbral,
                cuenta_quickbooks=cuenta_quickbooks,
                max_workers=max_workers
            )
        
        resultado = BatchComparisonResult.from_dict(resultado_dict)
        yield resultado
        
    finally:
        # Cleanup si es necesario
        pass


def _realizar_peticion_con_retry(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json_data: Optional[Dict[str, Any]] = None,
    max_retries: int = DEFAULT_MAX_RETRIES,
    retry_delay: float = DEFAULT_RETRY_DELAY,
    timeout: int = DEFAULT_TIMEOUT,
    operation_name: str = "http_request"
) -> requests.Response:
    """
    Realiza una petición HTTP con retry automático, circuit breaker y tracking de métricas.
    """
    headers = headers or {}
    last_exception = None
    
    # Verificar circuit breaker
    if not _check_circuit_breaker(operation_name):
        raise QuickBooksAPIError(
            f"Circuit breaker abierto para {operation_name}. Intenta más tarde.",
            status_code=503
        ) if "quickbooks" in operation_name.lower() else StripeAPIError(
            f"Circuit breaker abierto para {operation_name}. Intenta más tarde.",
            status_code=503
        )
    
    # Usar tenacity si está disponible para mejor manejo de retries
    if TENACITY_AVAILABLE:
        @retry(
            stop=stop_after_attempt(max_retries),
            wait=wait_exponential(multiplier=retry_delay, min=1, max=60),
            retry=retry_if_exception_type((requests.exceptions.Timeout, requests.exceptions.ConnectionError)),
            reraise=True
        )
        def _make_request():
            if method.upper() == "GET":
                return requests.get(url, headers=headers, params=params, timeout=timeout)
            elif method.upper() == "POST":
                return requests.post(url, headers=headers, json=json_data, params=params, timeout=timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        try:
            with track_performance(f"{operation_name}.request"):
                response = _make_request()
                
                # Manejar rate limits y errores 5xx
                if response.status_code == 429:
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr(f"revenue_compare.{operation_name}.rate_limit", 1)
                        except Exception:
                            pass
                    retry_after = int(response.headers.get("Retry-After", retry_delay))
                    logger.warning(f"Rate limit hit, waiting {retry_after}s")
                    time.sleep(min(retry_after, 300))  # Max 5 minutos
                    return _make_request()  # Retry una vez más
                
                if 500 <= response.status_code < 600:
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr(f"revenue_compare.{operation_name}.server_error", 1, tags={"status_code": str(response.status_code)})
                        except Exception:
                            pass
                    response.raise_for_status()
                
                response.raise_for_status()
                return response
        except RetryError as e:
            if STATS_AVAILABLE:
                try:
                    Stats.incr(f"revenue_compare.{operation_name}.retry_exhausted", 1)
                except Exception:
                    pass
            raise
    else:
        # Fallback a implementación manual
        for attempt in range(max_retries):
            try:
                with track_performance(f"{operation_name}.attempt_{attempt + 1}"):
                    if method.upper() == "GET":
                        response = requests.get(url, headers=headers, params=params, timeout=timeout)
                    elif method.upper() == "POST":
                        response = requests.post(url, headers=headers, json=json_data, params=params, timeout=timeout)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")
                
                # Si es 429 (rate limit) o 5xx, reintentar
                if response.status_code == 429:
                    if STATS_AVAILABLE:
                        try:
                            Stats.incr(f"revenue_compare.{operation_name}.rate_limit", 1)
                        except Exception:
                            pass
                    if attempt < max_retries - 1:
                        retry_after = int(response.headers.get("Retry-After", retry_delay * (2 ** attempt)))
                        logger.warning(f"Rate limit hit, retry {attempt + 1}/{max_retries} after {retry_after}s")
                        time.sleep(min(retry_after, 300))
                        continue
                
                if 500 <= response.status_code < 600:
                    if STATS_AVAILABLE and attempt == max_retries - 1:
                        try:
                            Stats.incr(f"revenue_compare.{operation_name}.server_error", 1, tags={"status_code": str(response.status_code)})
                        except Exception:
                            pass
                    if attempt < max_retries - 1:
                        wait_time = retry_delay * (2 ** attempt)
                        logger.warning(f"Server error, retry {attempt + 1}/{max_retries} after {wait_time:.1f}s")
                        time.sleep(wait_time)
                        continue
                    else:
                        response.raise_for_status()
                
                # Si llegamos aquí, la respuesta fue exitosa
                response.raise_for_status()
                
                # Registrar éxito en circuit breaker
                _record_circuit_breaker_success(operation_name)
                
                if STATS_AVAILABLE:
                    try:
                        Stats.incr(f"revenue_compare.{operation_name}.success", 1)
                    except Exception:
                        pass
                return response
                
            except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                last_exception = e
                if STATS_AVAILABLE:
                    try:
                        Stats.incr(f"revenue_compare.{operation_name}.error", 1, tags={"error_type": type(e).__name__})
                    except Exception:
                        pass
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    jittered_wait = _add_retry_jitter(wait_time)
                    logger.warning(f"Connection error, retry {attempt + 1}/{max_retries} after {jittered_wait:.1f}s")
                    time.sleep(jittered_wait)
                else:
                    # Registrar fallo en circuit breaker
                    _record_circuit_breaker_failure(operation_name)
                    raise
    
    if last_exception:
        raise last_exception
    
    raise RuntimeError(f"Failed to get successful response after {max_retries} attempts")


def obtener_ingresos_netos_stripe(
    fecha_inicio: str,
    fecha_fin: str,
    stripe_api_key: Optional[str] = None,
    enable_stats: bool = True
) -> Dict[str, Any]:
    """
    Obtiene la suma de ingresos netos de Stripe para un período.
    Usa balance_transactions para obtener fees de manera eficiente.
    
    Args:
        fecha_inicio: Fecha de inicio en formato YYYY-MM-DD
        fecha_fin: Fecha de fin en formato YYYY-MM-DD
        stripe_api_key: API Key de Stripe (opcional, usa env var si no se proporciona)
    
    Returns:
        Dict con:
            - ingreso_neto: Suma de ingresos netos (float)
            - cantidad_transacciones: Número de transacciones (int)
            - estado: Estado de la operación
    """
    api_key = stripe_api_key or STRIPE_API_KEY
    
    if not api_key:
        if enable_stats and STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.stripe.missing_api_key", 1)
            except Exception:
                pass
        return {
            "ingreso_neto": 0.0,
            "cantidad_transacciones": 0,
            "estado": "ERROR: STRIPE_API_KEY no configurado"
        }
    
    try:
        if enable_stats and STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.stripe.fetch_started", 1)
            except Exception:
                pass
        # Convertir fechas a timestamps
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
        # Agregar un día a fecha_fin para incluir todo el día
        fecha_fin_dt = fecha_fin_dt + timedelta(days=1)
        
        inicio_timestamp = int(fecha_inicio_dt.timestamp())
        fin_timestamp = int(fecha_fin_dt.timestamp())
        
        s = requests.Session()
        s.headers.update({"Authorization": f"Bearer {api_key}"})
        
        ingreso_neto_total = Decimal("0.0")
        cantidad_transacciones = 0
        balance_transactions_seen = set()
        
        # Usar balance_transactions directamente para obtener fees de manera más eficiente
        # balance_transactions contiene la información de fees para todos los tipos de transacciones
        params = {
            "limit": 100,
            "created[gte]": inicio_timestamp,
            "created[lt]": fin_timestamp,
            "expand[]": "data.source"  # Expandir source para obtener detalles del charge
        }
        
        starting_after = None
        while True:
            p = dict(params)
            if starting_after:
                p["starting_after"] = starting_after
            
            try:
                response = _realizar_peticion_con_retry(
                    "https://api.stripe.com/v1/balance_transactions",
                    method="GET",
                    params=p
                )
                response.raise_for_status()
                data = response.json()
                balance_transactions = data.get("data", [])
                
                for bt in balance_transactions:
                    bt_id = bt.get("id")
                    if bt_id in balance_transactions_seen:
                        continue
                    balance_transactions_seen.add(bt_id)
                    
                    # Filtrar solo transacciones de tipo 'charge' que sean exitosas
                    source_type = bt.get("type", "")
                    if source_type != "charge":
                        continue
                    
                    # Obtener el charge asociado
                    source = bt.get("source")
                    if not source or isinstance(source, str):
                        # Si es un ID, obtener el charge
                        charge_id = source if isinstance(source, str) else None
                        if not charge_id:
                            continue
                        try:
                            charge_response = s.get(
                                f"https://api.stripe.com/v1/charges/{charge_id}",
                                timeout=15
                            )
                            charge_response.raise_for_status()
                            charge = charge_response.json()
                        except Exception:
                            logger.debug(f"No se pudo obtener charge {charge_id}")
                            continue
                    else:
                        charge = source
                    
                    # Solo considerar charges pagados y exitosos
                    if not charge.get("paid") or charge.get("status") != "succeeded":
                        continue
                    
                    # Monto bruto del balance transaction (ya en la moneda base)
                    amount = Decimal(str(bt.get("amount", 0))) / Decimal("100")
                    # Fee del balance transaction
                    fee = Decimal(str(bt.get("fee", 0))) / Decimal("100")
                    
                    # Ingreso neto = amount - fee
                    ingreso_neto = amount - fee
                    ingreso_neto_total += ingreso_neto
                    cantidad_transacciones += 1
                
                if data.get("has_more") and balance_transactions:
                    starting_after = balance_transactions[-1].get("id")
                else:
                    break
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Error obteniendo balance transactions de Stripe: {e}")
                # Fallback: intentar con charges directamente
                logger.info("Fallback a método de charges individuales")
                return _obtener_ingresos_stripe_fallback(s, inicio_timestamp, fin_timestamp)
        
        logger.info(
            f"Ingresos netos Stripe obtenidos: ${float(ingreso_neto_total):.2f} "
            f"({cantidad_transacciones} transacciones)"
        )
        
        if enable_stats and STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.stripe.fetch_success", 1)
                Stats.gauge("revenue_compare.stripe.ingreso_neto", float(ingreso_neto_total))
                Stats.gauge("revenue_compare.stripe.transacciones", cantidad_transacciones)
            except Exception:
                pass
        
        return {
            "ingreso_neto": float(ingreso_neto_total),
            "cantidad_transacciones": cantidad_transacciones,
            "estado": "Éxito"
        }
        
    except ValueError as e:
        logger.error(f"Error de formato de fecha: {e}")
        return {
            "ingreso_neto": 0.0,
            "cantidad_transacciones": 0,
            "estado": f"ERROR_FORMATO: {str(e)}"
        }
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en petición a Stripe: {e}")
        if enable_stats and STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.stripe.fetch_error", 1, tags={"error_type": type(e).__name__})
            except Exception:
                pass
        return {
            "ingreso_neto": 0.0,
            "cantidad_transacciones": 0,
            "estado": f"ERROR_REQUEST: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error inesperado obteniendo ingresos Stripe: {e}", exc_info=True)
        return {
            "ingreso_neto": 0.0,
            "cantidad_transacciones": 0,
            "estado": f"ERROR_INESPERADO: {str(e)}"
        }


def _obtener_ingresos_stripe_fallback(
    session: requests.Session,
    inicio_timestamp: int,
    fin_timestamp: int
) -> Dict[str, Any]:
    """
    Método fallback para obtener ingresos de Stripe usando charges individuales.
    Se usa cuando balance_transactions no está disponible.
    """
    ingreso_neto_total = Decimal("0.0")
    cantidad_transacciones = 0
    
    params = {
        "limit": 100,
        "created[gte]": inicio_timestamp,
        "created[lt]": fin_timestamp,
    }
    
    starting_after = None
    while True:
        p = dict(params)
        if starting_after:
            p["starting_after"] = starting_after
        
        response = session.get("https://api.stripe.com/v1/charges", params=p, timeout=30)
        response.raise_for_status()
        data = response.json()
        charges = data.get("data", [])
        
        for charge in charges:
            if charge.get("paid") and charge.get("status") == "succeeded":
                amount = Decimal(str(charge.get("amount", 0))) / Decimal("100")
                balance_txn_id = charge.get("balance_transaction")
                fee = Decimal("0.0")
                
                if balance_txn_id:
                    try:
                        bt_response = session.get(
                            f"https://api.stripe.com/v1/balance_transactions/{balance_txn_id}",
                            timeout=15
                        )
                        bt_response.raise_for_status()
                        bt_data = bt_response.json()
                        fee = Decimal(str(bt_data.get("fee", 0))) / Decimal("100")
                    except Exception:
                        pass
                
                ingreso_neto = amount - fee
                ingreso_neto_total += ingreso_neto
                cantidad_transacciones += 1
        
        if data.get("has_more") and charges:
            starting_after = charges[-1].get("id")
        else:
            break
    
    return {
        "ingreso_neto": float(ingreso_neto_total),
        "cantidad_transacciones": cantidad_transacciones,
        "estado": "Éxito"
    }


def _get_account_id_cached(
    cuenta_ingresos: str,
    access_token: str,
    realm_id: str,
    base_url: str
) -> Optional[str]:
    """
    Obtiene el ID de cuenta de QuickBooks usando cache.
    
    Args:
        cuenta_ingresos: Nombre de la cuenta
        access_token: Token de acceso
        realm_id: ID de la compañía
        base_url: URL base de QuickBooks
    
    Returns:
        ID de la cuenta o None si no se encuentra
    """
    # Check cache first
    if CACHETOOLS_AVAILABLE and _account_cache:
        cache_key = f"{realm_id}:{cuenta_ingresos}"
        if cache_key in _account_cache:
            logger.debug(f"Account ID found in cache: {cache_key}")
            return _account_cache[cache_key]
    
    # Query QuickBooks
    cuenta_escaped = _escape_query_string(cuenta_ingresos)
    account_query = f"SELECT * FROM Account WHERE Name = '{cuenta_escaped}' MAXRESULTS 1"
    account_url = f"{base_url}/v3/company/{realm_id}/query"
    account_headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
        "Content-Type": "application/text"
    }
    
    try:
        account_response = _realizar_peticion_con_retry(
            account_url,
            method="GET",
            headers=account_headers,
            params={"minorversion": "65", "query": account_query},
            operation_name="get_account_id"
        )
        
        if account_response.status_code == 200:
            account_data = account_response.json()
            account_query_response = account_data.get("QueryResponse", {})
            accounts = account_query_response.get("Account", [])
            if accounts:
                account = accounts[0] if isinstance(accounts, list) else accounts
                account_id = account.get("Id")
                
                # Store in cache
                if CACHETOOLS_AVAILABLE and _account_cache and account_id:
                    cache_key = f"{realm_id}:{cuenta_ingresos}"
                    _account_cache[cache_key] = account_id
                    logger.debug(f"Account ID cached: {cache_key} -> {account_id}")
                
                return account_id
    except Exception as e:
        logger.warning(f"Error obteniendo account ID: {e}")
    
    return None


def obtener_ingresos_quickbooks(
    fecha_inicio: str,
    fecha_fin: str,
    cuenta_ingresos: str = "Ventas Stripe",
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    enable_cache: bool = True
) -> Dict[str, Any]:
    """
    Obtiene la suma de ingresos registrados en QuickBooks para una cuenta en un período.
    
    Args:
        fecha_inicio: Fecha de inicio en formato YYYY-MM-DD
        fecha_fin: Fecha de fin en formato YYYY-MM-DD
        cuenta_ingresos: Nombre de la cuenta de ingresos (default: "Ventas Stripe")
        qb_access_token: Token de acceso de QuickBooks (opcional, usa env var si no se proporciona)
        qb_realm_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        qb_base: URL base de la API de QuickBooks (opcional, usa env var si no se proporciona)
    
    Returns:
        Dict con:
            - ingreso_total: Suma de ingresos (float)
            - cantidad_transacciones: Número de transacciones (int)
            - estado: Estado de la operación
    """
    access_token = qb_access_token or QUICKBOOKS_ACCESS_TOKEN
    realm_id = qb_realm_id or QUICKBOOKS_REALM_ID
    base_url = qb_base or QUICKBOOKS_BASE
    
    if not access_token:
        return {
            "ingreso_total": 0.0,
            "cantidad_transacciones": 0,
            "estado": "ERROR: QUICKBOOKS_ACCESS_TOKEN no configurado"
        }
    
    if not realm_id:
        return {
            "ingreso_total": 0.0,
            "cantidad_transacciones": 0,
            "estado": "ERROR: QUICKBOOKS_REALM_ID no configurado"
        }
    
    try:
        # Escapar el nombre de la cuenta para prevenir SQL injection
        cuenta_escaped = _escape_query_string(cuenta_ingresos)
        
        # Buscar la cuenta por nombre para obtener su ID (con cache si está habilitado)
        account_id = None
        if enable_cache:
            account_id = _get_account_id_cached(cuenta_ingresos, access_token, realm_id, base_url)
        else:
            # Sin cache, buscar directamente
            account_query = f"SELECT * FROM Account WHERE Name = '{cuenta_escaped}' MAXRESULTS 1"
            account_url = f"{base_url}/v3/company/{realm_id}/query"
            account_headers = {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
                "Content-Type": "application/text"
            }
            account_params = {"minorversion": "65", "query": account_query}
            
            try:
                account_response = _realizar_peticion_con_retry(
                    account_url,
                    method="GET",
                    headers=account_headers,
                    params=account_params,
                    operation_name="get_account_id"
                )
                if account_response.status_code == 200:
                    account_data = account_response.json()
                    account_query_response = account_data.get("QueryResponse", {})
                    accounts = account_query_response.get("Account", [])
                    if accounts:
                        account = accounts[0] if isinstance(accounts, list) else accounts
                        account_id = account.get("Id")
                        logger.debug(f"Cuenta QuickBooks encontrada: ID={account_id}, Name={cuenta_ingresos}")
            except Exception as e:
                logger.warning(f"No se pudo obtener account ID, usando búsqueda por nombre: {e}")
        
        if account_id:
            logger.debug(f"Usando account ID desde cache/búsqueda: {account_id}")
        
        # Query para obtener Sales Receipts en el período
        fecha_inicio_escaped = _escape_query_string(fecha_inicio)
        fecha_fin_escaped = _escape_query_string(fecha_fin)
        
        query = (
            f"SELECT * FROM SalesReceipt "
            f"WHERE TxnDate >= '{fecha_inicio_escaped}' "
            f"AND TxnDate <= '{fecha_fin_escaped}' "
            f"MAXRESULTS 1000"
        )
        
        url = f"{base_url}/v3/company/{realm_id}/query"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/text"
        }
        
        ingreso_total = Decimal("0.0")
        cantidad_transacciones = 0
        start_position = 0
        
        # QuickBooks puede requerir paginación
        while True:
            current_params = {"minorversion": "65", "query": query}
            
            try:
                response = _realizar_peticion_con_retry(
                    url,
                    method="GET",
                    headers=headers,
                    params=current_params
                )
            except requests.exceptions.RequestException as e:
                logger.error(f"Error en petición a QuickBooks: {e}")
                raise
            
            if response.status_code == 200:
                data = response.json()
                query_response = data.get("QueryResponse", {})
                
                # QuickBooks puede devolver un array o un objeto único
                receipts = query_response.get("SalesReceipt", [])
                if not isinstance(receipts, list):
                    receipts = [receipts] if receipts else []
                
                if not receipts:
                    break
                
                for receipt in receipts:
                    # Verificar si alguna línea está asociada con la cuenta objetivo
                    line_items = receipt.get("Line", [])
                    if not isinstance(line_items, list):
                        line_items = [line_items] if line_items else []
                    
                    receipt_matched = False
                    
                    for line in line_items:
                        detail = line.get("SalesItemLineDetail", {})
                        if not detail:
                            continue
                        
                        item_ref = detail.get("ItemRef", {})
                        item_name = item_ref.get("name", "") or ""
                        
                        # Verificar si la línea está asociada con la cuenta objetivo
                        account_ref = detail.get("AccountRef", {})
                        account_ref_id = account_ref.get("value", "")
                        account_ref_name = account_ref.get("name", "") or ""
                        
                        matches_account = False
                        if account_id and account_ref_id == account_id:
                            matches_account = True
                        elif cuenta_ingresos.lower() in account_ref_name.lower():
                            matches_account = True
                        elif cuenta_ingresos.lower() in item_name.lower():
                            matches_account = True
                        
                        if matches_account:
                            amount = Decimal(str(line.get("Amount", 0)))
                            ingreso_total += amount
                            receipt_matched = True
                    
                    # Si no se encontró match en líneas específicas pero el receipt menciona Stripe
                    if not receipt_matched:
                        private_note = receipt.get("PrivateNote", "") or ""
                        doc_number = receipt.get("DocNumber", "") or ""
                        if "stripe" in private_note.lower() or "stripe" in doc_number.lower():
                            # Sumar el TotalAmt si menciona Stripe
                            total_amt = Decimal(str(receipt.get("TotalAmt", 0)))
                            ingreso_total += total_amt
                            cantidad_transacciones += 1
                    else:
                        cantidad_transacciones += 1
                
                # Verificar si hay más resultados (paginación)
                max_results = query_response.get("maxResults", 0)
                total_count = query_response.get("totalCount", 0)
                
                if not receipts or len(receipts) < max_results or start_position + len(receipts) >= total_count:
                    break
                
                # Actualizar para siguiente página
                start_position += len(receipts)
                fecha_inicio_escaped = _escape_query_string(fecha_inicio)
                fecha_fin_escaped = _escape_query_string(fecha_fin)
                query = (
                    f"SELECT * FROM SalesReceipt "
                    f"WHERE TxnDate >= '{fecha_inicio_escaped}' "
                    f"AND TxnDate <= '{fecha_fin_escaped}' "
                    f"STARTPOSITION {start_position} "
                    f"MAXRESULTS 1000"
                )
            elif response.status_code == 400:
                # No hay resultados o error en query
                error_data = response.json() if response.headers.get("Content-Type", "").startswith("application/json") else {}
                error_msg = _extract_quickbooks_error(error_data, response.status_code)
                
                # Si es "No results", es normal
                if "no results" in error_msg.lower() or "no entity found" in error_msg.lower():
                    logger.info("No se encontraron Sales Receipts en QuickBooks para el período")
                    break
                
                logger.warning(f"Error en query de QuickBooks: {error_msg}")
                break
            else:
                response.raise_for_status()
        
        logger.info(
            f"Ingresos QuickBooks obtenidos: ${float(ingreso_total):.2f} "
            f"({cantidad_transacciones} transacciones)"
        )
        
        return {
            "ingreso_total": float(ingreso_total),
            "cantidad_transacciones": cantidad_transacciones,
            "estado": "Éxito"
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error en petición a QuickBooks: {e}")
        return {
            "ingreso_total": 0.0,
            "cantidad_transacciones": 0,
            "estado": f"ERROR_REQUEST: {str(e)}"
        }
    except Exception as e:
        logger.error(f"Error inesperado obteniendo ingresos QuickBooks: {e}", exc_info=True)
        return {
            "ingreso_total": 0.0,
            "cantidad_transacciones": 0,
            "estado": f"ERROR_INESPERADO: {str(e)}"
        }


def comparar_ingresos_stripe_quickbooks(
    fecha_inicio: str,
    fecha_fin: str,
    umbral: float = 100.0,
    cuenta_quickbooks: str = "Ventas Stripe",
    stripe_api_key: Optional[str] = None,
    qb_access_token: Optional[str] = None,
    qb_realm_id: Optional[str] = None,
    qb_base: Optional[str] = None,
    enable_parallel: bool = False
) -> ComparisonResult:
    """
    Compara la suma de ingresos netos de Stripe con los ingresos registrados en QuickBooks.
    
    Args:
        fecha_inicio: Fecha de inicio en formato YYYY-MM-DD
        fecha_fin: Fecha de fin en formato YYYY-MM-DD
        umbral: Umbral de diferencia para generar alerta (default: 100.0)
        cuenta_quickbooks: Nombre de la cuenta en QuickBooks (default: "Ventas Stripe")
        stripe_api_key: API Key de Stripe (opcional, usa env var si no se proporciona)
        qb_access_token: Token de acceso de QuickBooks (opcional, usa env var si no se proporciona)
        qb_realm_id: ID de la compañía en QuickBooks (opcional, usa env var si no se proporciona)
        qb_base: URL base de la API de QuickBooks (opcional, usa env var si no se proporciona)
    
    Returns:
        Dict con:
            - estado: "Ok" si la diferencia está dentro del umbral, "Alerta" si excede el umbral
            - detalles: Dict con información detallada de la comparación
    """
    # Validar parámetros usando función helper
    validation_error, fecha_inicio_dt, fecha_fin_dt = _validate_date_range(fecha_inicio, fecha_fin)
    
    if validation_error:
        return _create_error_result(
            estado="Error",
            motivo=str(validation_error),
            umbral=umbral
        )
    
    logger.info(f"Iniciando comparación de ingresos para período {fecha_inicio} - {fecha_fin}")
    
    # Obtener ingresos en paralelo si está habilitado y disponible
    if enable_parallel and CONCURRENT_FUTURES_AVAILABLE:
        logger.info("Usando procesamiento paralelo para obtener ingresos")
        with track_performance("comparison_parallel"):
            with ThreadPoolExecutor(max_workers=2) as executor:
                stripe_future = executor.submit(
                    obtener_ingresos_netos_stripe,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    stripe_api_key=stripe_api_key
                )
                qb_future = executor.submit(
                    obtener_ingresos_quickbooks,
                    fecha_inicio=fecha_inicio,
                    fecha_fin=fecha_fin,
                    cuenta_ingresos=cuenta_quickbooks,
                    qb_access_token=qb_access_token,
                    qb_realm_id=qb_realm_id,
                    qb_base=qb_base
                )
                
                stripe_result = stripe_future.result()
                qb_result = qb_future.result()
    else:
        # Secuencial (default)
        stripe_result = obtener_ingresos_netos_stripe(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            stripe_api_key=stripe_api_key
        )
        qb_result = obtener_ingresos_quickbooks(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            cuenta_ingresos=cuenta_quickbooks,
            qb_access_token=qb_access_token,
            qb_realm_id=qb_realm_id,
            qb_base=qb_base
        )
    
    ingreso_stripe = stripe_result.get("ingreso_neto", 0.0)
    
    if stripe_result.get("estado") != "Éxito":
        logger.error(f"Error obteniendo ingresos Stripe: {stripe_result.get('estado')}")
        return _create_error_result(
            estado="Error",
            motivo=f"Error al obtener ingresos de Stripe: {stripe_result.get('estado')}",
            umbral=umbral,
            error_details={"error_stripe": stripe_result.get("estado")}
        )
    
    ingreso_quickbooks = qb_result.get("ingreso_total", 0.0)
    
    if qb_result.get("estado") != "Éxito":
        logger.error(f"Error obteniendo ingresos QuickBooks: {qb_result.get('estado')}")
        return _create_error_result(
            estado="Error",
            motivo=f"Error al obtener ingresos de QuickBooks: {qb_result.get('estado')}",
            ingreso_stripe=ingreso_stripe,
            umbral=umbral,
            error_details={"error_quickbooks": qb_result.get("estado")}
        )
    
    # Calcular diferencia
    diferencia = abs(ingreso_stripe - ingreso_quickbooks)
    diferencia_porcentual = (diferencia / max(ingreso_stripe, ingreso_quickbooks, 1)) * 100
    
    # Trackear métricas básicas
    if STATS_AVAILABLE:
        try:
            Stats.gauge("revenue_compare.ingreso_stripe", ingreso_stripe)
            Stats.gauge("revenue_compare.ingreso_quickbooks", ingreso_quickbooks)
            Stats.gauge("revenue_compare.diferencia", diferencia)
            Stats.gauge("revenue_compare.diferencia_porcentual", diferencia_porcentual)
        except Exception:
            pass
    
    # Determinar estado
    if diferencia > umbral:
        estado = "Alerta"
        motivo = f"Ingresos no coinciden, diferencia ${diferencia:.2f}"
        logger.warning(
            f"ALERTA: Diferencia de ingresos excede umbral",
            extra={
                "ingreso_stripe": ingreso_stripe,
                "ingreso_quickbooks": ingreso_quickbooks,
                "diferencia": diferencia,
                "umbral": umbral
            }
        )
        if STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.alertas_generadas", 1)
            except Exception:
                pass
    else:
        estado = "Ok"
        motivo = f"Ingresos coinciden dentro del umbral (diferencia: ${diferencia:.2f})"
        logger.info(
            f"Comparación exitosa: diferencia dentro del umbral",
            extra={"diferencia": diferencia, "umbral": umbral}
        )
        if STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.comparaciones_ok", 1)
            except Exception:
                pass
    
    detalles = {
        "motivo": motivo,
        "ingreso_stripe": ingreso_stripe,
        "ingreso_quickbooks": ingreso_quickbooks,
        "diferencia": diferencia,
        "diferencia_absoluta": diferencia,
        "diferencia_porcentual": diferencia_porcentual,
        "umbral": umbral,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "cuenta_quickbooks": cuenta_quickbooks,
        "cantidad_transacciones_stripe": stripe_result.get("cantidad_transacciones", 0),
        "cantidad_transacciones_quickbooks": qb_result.get("cantidad_transacciones", 0)
    }
    
    return {
        "estado": estado,
        "detalles": detalles
    }


# Función auxiliar para uso en DAGs de Airflow
def comparar_ingresos_stripe_quickbooks_task(**context):
    """
    Wrapper para usar la función en DAGs de Airflow.
    Espera los siguientes parámetros en context['params']:
    - fecha_inicio: Fecha de inicio en formato YYYY-MM-DD
    - fecha_fin: Fecha de fin en formato YYYY-MM-DD
    - umbral: Umbral de diferencia para alerta (opcional, default 100.0)
    - cuenta_quickbooks: Nombre de la cuenta en QuickBooks (opcional, default "Ventas Stripe")
    - enable_parallel: Habilitar procesamiento paralelo (opcional, default False)
    
    Implementa RORO pattern y validación robusta.
    """
    # Cargar y validar parámetros usando función helper
    task_params = _load_comparison_params_from_context(context)
    
    fecha_inicio = task_params["fecha_inicio"]
    fecha_fin = task_params["fecha_fin"]
    umbral = task_params["umbral"]
    cuenta_quickbooks = task_params["cuenta_quickbooks"]
    enable_parallel = task_params["enable_parallel"]
    
    # Trackear inicio
    if STATS_AVAILABLE:
        try:
            Stats.incr("revenue_compare.task.started", 1)
        except Exception:
            pass
    
    start_time = time.time()
    
    try:
        resultado = comparar_ingresos_stripe_quickbooks(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            umbral=umbral,
            cuenta_quickbooks=cuenta_quickbooks,
            enable_parallel=enable_parallel
        )
        
        duration_ms = (time.time() - start_time) * 1000
        
        if STATS_AVAILABLE:
            try:
                Stats.timing("revenue_compare.task.duration_ms", duration_ms)
                Stats.incr("revenue_compare.task.completed", 1, tags={"estado": resultado.get("estado", "unknown")})
            except Exception:
                pass
        
        estado = resultado["estado"]
        detalles = resultado["detalles"]
        
        if estado == "Ok":
            print(f"✓ Comparación exitosa: {detalles['motivo']}")
            print(f"  - Ingreso Stripe: ${detalles['ingreso_stripe']:.2f}")
            print(f"  - Ingreso QuickBooks: ${detalles['ingreso_quickbooks']:.2f}")
            print(f"  - Diferencia: ${detalles['diferencia']:.2f} ({detalles.get('diferencia_porcentual', 0):.2f}%)")
            print(f"  - Duración: {duration_ms:.0f}ms")
        elif estado == "Alerta":
            print(f"⚠ ALERTA: {detalles['motivo']}")
            print(f"  - Ingreso Stripe: ${detalles['ingreso_stripe']:.2f}")
            print(f"  - Ingreso QuickBooks: ${detalles['ingreso_quickbooks']:.2f}")
            print(f"  - Diferencia: ${detalles['diferencia']:.2f} (umbral: ${umbral:.2f})")
            print(f"  - Duración: {duration_ms:.0f}ms")
        else:
            print(f"✗ Error en la comparación: {detalles.get('motivo', 'Error desconocido')}")
            print(f"  - Duración: {duration_ms:.0f}ms")
        
        return resultado
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        if STATS_AVAILABLE:
            try:
                Stats.incr("revenue_compare.task.error", 1, tags={"error_type": type(e).__name__})
                Stats.timing("revenue_compare.task.duration_ms", duration_ms)
            except Exception:
                pass
        logger.error(f"Error en comparación de ingresos: {e}", exc_info=True)
        raise


def persistir_comparacion(
    resultado: Dict[str, Any],
    fecha_inicio: str,
    fecha_fin: str,
    db_conn=None
) -> Optional[int]:
    """
    Persiste el resultado de la comparación en la base de datos.
    
    Args:
        resultado: Resultado de comparar_ingresos_stripe_quickbooks
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha de fin del período
        db_conn: Conexión a la base de datos (opcional, usa get_conn si no se proporciona)
    
    Returns:
        ID del registro insertado o None si falla
    """
    try:
        if not db_conn:
            from data.airflow.plugins.db import get_conn
            with get_conn() as conn:
                return persistir_comparacion(resultado, fecha_inicio, fecha_fin, conn)
        
        detalles = resultado.get("detalles", {})
        estado = resultado.get("estado", "Error")

        with db_conn.cursor() as cur:
            # Aplicar timeout si está configurado
            if statement_timeout_ms and statement_timeout_ms > 0:
                try:
                    from psycopg import sql
                    cur.execute(sql.SQL("SET LOCAL statement_timeout = %s;"), (statement_timeout_ms,))
                except Exception as e:
                    logger.warning(f"No se pudo configurar statement_timeout: {e}")
            
            # Crear tabla si no existe
            cur.execute("""
                CREATE TABLE IF NOT EXISTS stripe_quickbooks_revenue_comparisons (
                    id SERIAL PRIMARY KEY,
                    fecha_inicio DATE NOT NULL,
                    fecha_fin DATE NOT NULL,
                    estado TEXT NOT NULL,
                    ingreso_stripe NUMERIC(14,2) NOT NULL,
                    ingreso_quickbooks NUMERIC(14,2) NOT NULL,
                    diferencia NUMERIC(14,2) NOT NULL,
                    diferencia_porcentual NUMERIC(5,2),
                    umbral NUMERIC(14,2) NOT NULL,
                    cuenta_quickbooks TEXT,
                    cantidad_transacciones_stripe INTEGER,
                    cantidad_transacciones_quickbooks INTEGER,
                    motivo TEXT,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(fecha_inicio, fecha_fin)
                )
            """)
            
            # Insertar o actualizar comparación
            cur.execute("""
                INSERT INTO stripe_quickbooks_revenue_comparisons 
                    (fecha_inicio, fecha_fin, estado, ingreso_stripe, ingreso_quickbooks,
                     diferencia, diferencia_porcentual, umbral, cuenta_quickbooks,
                     cantidad_transacciones_stripe, cantidad_transacciones_quickbooks, motivo)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (fecha_inicio, fecha_fin) DO UPDATE SET
                    estado = EXCLUDED.estado,
                    ingreso_stripe = EXCLUDED.ingreso_stripe,
                    ingreso_quickbooks = EXCLUDED.ingreso_quickbooks,
                    diferencia = EXCLUDED.diferencia,
                    diferencia_porcentual = EXCLUDED.diferencia_porcentual,
                    umbral = EXCLUDED.umbral,
                    cuenta_quickbooks = EXCLUDED.cuenta_quickbooks,
                    cantidad_transacciones_stripe = EXCLUDED.cantidad_transacciones_stripe,
                    cantidad_transacciones_quickbooks = EXCLUDED.cantidad_transacciones_quickbooks,
                    motivo = EXCLUDED.motivo,
                    created_at = NOW()
                RETURNING id
            """, (
                fecha_inicio,
                fecha_fin,
                estado,
                detalles.get("ingreso_stripe", 0.0),
                detalles.get("ingreso_quickbooks", 0.0),
                detalles.get("diferencia", 0.0),
                detalles.get("diferencia_porcentual", 0.0),
                detalles.get("umbral", 0.0),
                detalles.get("cuenta_quickbooks", ""),
                detalles.get("cantidad_transacciones_stripe", 0),
                detalles.get("cantidad_transacciones_quickbooks", 0),
                detalles.get("motivo", "")
            ))
            
            record_id = cur.fetchone()[0]
            db_conn.commit()
            
            logger.info(f"Comparación persistida con ID: {record_id}")
            return record_id
            
    except Exception as e:
        logger.error(f"Error persistiendo comparación: {e}", exc_info=True)
        if db_conn:
            db_conn.rollback()
        return None


def enviar_alerta(
    resultado: Dict[str, Any],
    detalles: Dict[str, Any],
    fecha_inicio: str,
    fecha_fin: str
) -> None:
    """
    Envía alertas via Slack y Email si el estado es "Alerta".
    
    Args:
        resultado: Resultado completo de la comparación
        detalles: Detalles de la comparación
        fecha_inicio: Fecha de inicio del período
        fecha_fin: Fecha de fin del período
    """
    estado = resultado.get("estado")
    
    if estado != "Alerta":
        logger.debug("No se requiere alerta, estado es Ok")
        return
    
    try:
        from data.airflow.plugins.etl_notifications import notify_slack, notify_email
        
        ingreso_stripe = detalles.get("ingreso_stripe", 0.0)
        ingreso_quickbooks = detalles.get("ingreso_quickbooks", 0.0)
        diferencia = detalles.get("diferencia", 0.0)
        umbral = detalles.get("umbral", 100.0)
        diferencia_pct = detalles.get("diferencia_porcentual", 0.0)
        
        # Slack alert
        slack_msg = (
            f"⚠️ *ALERTA: Ingresos no coinciden entre Stripe y QuickBooks*\n\n"
            f"*Período:* {fecha_inicio} - {fecha_fin}\n"
            f"*Ingreso Stripe:* ${ingreso_stripe:,.2f}\n"
            f"*Ingreso QuickBooks:* ${ingreso_quickbooks:,.2f}\n"
            f"*Diferencia:* ${diferencia:,.2f} ({diferencia_pct:.2f}%)\n"
            f"*Umbral configurado:* ${umbral:,.2f}\n"
            f"*Motivo:* {detalles.get('motivo', 'N/A')}"
        )
        
        try:
            notify_slack(
                slack_msg,
                extra_context={
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "diferencia": diferencia,
                    "umbral": umbral
                }
            )
            logger.info("Alerta enviada a Slack")
        except Exception as e:
            logger.warning(f"Error enviando alerta a Slack: {e}")
        
        # Email alert
        email_subject = f"ALERTA: Diferencia de ingresos Stripe vs QuickBooks ({fecha_inicio} - {fecha_fin})"
        email_body = f"""
        <h2>Alerta de Comparación de Ingresos</h2>
        <p>Se detectó una diferencia significativa entre los ingresos de Stripe y QuickBooks.</p>
        
        <table border="1" cellpadding="10" style="border-collapse: collapse;">
            <tr>
                <th style="background-color: #f0f0f0;">Concepto</th>
                <th style="background-color: #f0f0f0;">Valor</th>
            </tr>
            <tr>
                <td><strong>Período</strong></td>
                <td>{fecha_inicio} - {fecha_fin}</td>
            </tr>
            <tr>
                <td><strong>Ingreso Stripe</strong></td>
                <td>${ingreso_stripe:,.2f}</td>
            </tr>
            <tr>
                <td><strong>Ingreso QuickBooks</strong></td>
                <td>${ingreso_quickbooks:,.2f}</td>
            </tr>
            <tr>
                <td><strong>Diferencia</strong></td>
                <td><span style="color: red; font-weight: bold;">${diferencia:,.2f} ({diferencia_pct:.2f}%)</span></td>
            </tr>
            <tr>
                <td><strong>Umbral</strong></td>
                <td>${umbral:,.2f}</td>
            </tr>
            <tr>
                <td><strong>Motivo</strong></td>
                <td>{detalles.get('motivo', 'N/A')}</td>
            </tr>
            <tr>
                <td><strong>Transacciones Stripe</strong></td>
                <td>{detalles.get('cantidad_transacciones_stripe', 0)}</td>
            </tr>
            <tr>
                <td><strong>Transacciones QuickBooks</strong></td>
                <td>{detalles.get('cantidad_transacciones_quickbooks', 0)}</td>
            </tr>
        </table>
        
        <p><em>Esta es una alerta automática del sistema de comparación de ingresos.</em></p>
        """
        
        try:
            notify_email(
                to=None,  # Usará ALERT_EMAILS de env vars
                subject=email_subject,
                html=email_body
            )
            logger.info("Alerta enviada por email")
        except Exception as e:
            logger.warning(f"Error enviando alerta por email: {e}")
            
    except ImportError:
        logger.warning("Módulos de notificación no disponibles")
    except Exception as e:
        logger.error(f"Error enviando alertas: {e}", exc_info=True)


def obtener_historial_comparaciones(
    dias: int = 30,
    db_conn=None
) -> List[Dict[str, Any]]:
    """
    Obtiene el historial de comparaciones recientes.
    
    Args:
        dias: Número de días hacia atrás para obtener historial (default: 30)
        db_conn: Conexión a la base de datos (opcional)
    
    Returns:
        Lista de diccionarios con el historial de comparaciones
    """
    try:
        if not db_conn:
            from data.airflow.plugins.db import get_conn
            with get_conn() as conn:
                # Recursión con la conexión provista
                return _obtener_historial_impl(dias, conn)
        
        return _obtener_historial_impl(dias, db_conn)
            
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}", exc_info=True)
        return []


def _obtener_historial_impl(dias: int, db_conn) -> List[Dict[str, Any]]:
    """Implementación interna para obtener historial."""
    with db_conn.cursor() as cur:
        cur.execute("""
            SELECT 
                id, fecha_inicio, fecha_fin, estado,
                ingreso_stripe, ingreso_quickbooks, diferencia,
                diferencia_porcentual, umbral, cuenta_quickbooks,
                cantidad_transacciones_stripe, cantidad_transacciones_quickbooks,
                motivo, created_at
            FROM stripe_quickbooks_revenue_comparisons
            WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
            ORDER BY created_at DESC
            LIMIT 100
        """, (dias,))
        
        columns = [desc[0] for desc in cur.description]
        results = []
        for row in cur.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
            
    except Exception as e:
        logger.error(f"Error obteniendo historial: {e}", exc_info=True)
        return []


def analizar_tendencias(
    dias: int = 90,
    db_conn=None
) -> Dict[str, Any]:
    """
    Analiza tendencias de las comparaciones históricas.
    
    Args:
        dias: Número de días hacia atrás para el análisis (default: 90)
        db_conn: Conexión a la base de datos (opcional)
    
    Returns:
        Dict con estadísticas de tendencias
    """
    try:
        if not db_conn:
            from data.airflow.plugins.db import get_conn
            with get_conn() as conn:
                return _analizar_tendencias_impl(dias, conn)
        
        return _analizar_tendencias_impl(dias, db_conn)
            
    except Exception as e:
        logger.error(f"Error analizando tendencias: {e}", exc_info=True)
        return {}


def comparar_ingresos_batch(
    periodos: List[Dict[str, str]],
    umbral: float = 100.0,
    cuenta_quickbooks: str = "Ventas Stripe",
    max_workers: int = 3,
    continue_on_error: bool = True
) -> BatchComparisonResult:
    """
    Compara ingresos para múltiples períodos en batch con procesamiento paralelo.
    
    Args:
        periodos: Lista de diccionarios con 'fecha_inicio' y 'fecha_fin'
        umbral: Umbral de diferencia para alerta (default: 100.0)
        cuenta_quickbooks: Nombre de la cuenta en QuickBooks (default: "Ventas Stripe")
        max_workers: Número máximo de workers para procesamiento paralelo (default: 3)
        continue_on_error: Continuar procesando si hay errores (default: True)
    
    Returns:
        Dict con resultados de todas las comparaciones
    """
    if not periodos:
        return {
            "total": 0,
            "exitosos": 0,
            "fallidos": 0,
            "alertas": 0,
            "resultados": []
        }
    
    start_time = time.time()
    resultados: List[Dict[str, Any]] = []
    exitosos = 0
    fallidos = 0
    alertas = 0
    processed_count = 0
    
    if CONCURRENT_FUTURES_AVAILABLE and max_workers > 1:
        logger.info(f"Procesando {len(periodos)} períodos en paralelo con {max_workers} workers")
        
        def process_periodo(periodo: Dict[str, str]) -> Dict[str, Any]:
            """Procesa un período individual."""
            try:
                resultado = comparar_ingresos_stripe_quickbooks(
                    fecha_inicio=periodo["fecha_inicio"],
                    fecha_fin=periodo["fecha_fin"],
                    umbral=umbral,
                    cuenta_quickbooks=cuenta_quickbooks,
                    enable_parallel=False  # Ya estamos en paralelo
                )
                resultado["periodo"] = periodo
                return resultado
            except Exception as e:
                if not continue_on_error:
                    raise
                logger.error(f"Error procesando período {periodo}: {e}")
                return {
                    "estado": "Error",
                    "detalles": {"motivo": str(e)},
                    "periodo": periodo
                }
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(process_periodo, p): p for p in periodos}
            
            for future in as_completed(futures):
                periodo = futures[future]
                processed_count += 1
                try:
                    resultado = future.result()
                    resultados.append(resultado)
                    
                    if resultado.get("estado") == "Ok":
                        exitosos += 1
                    elif resultado.get("estado") == "Alerta":
                        alertas += 1
                        exitosos += 1  # También cuenta como exitoso
                        # Notificar discrepancias críticas
                        _notify_critical_discrepancy(resultado)
                    else:
                        fallidos += 1
                    
                    # Reportar progreso periódicamente usando log_progress
                    log_progress(
                        processed_count,
                        len(periodos),
                        "Procesamiento batch paralelo",
                        {
                            "exitosos": exitosos,
                            "fallidos": fallidos,
                            "alertas": alertas
                        }
                    )
                        
                except Exception as e:
                    if not continue_on_error:
                        raise
                    logger.error(f"Error en future para período {periodo}: {e}")
                    fallidos += 1
    else:
        # Procesamiento secuencial
        logger.info(f"Procesando {len(periodos)} períodos secuencialmente")
        for i, periodo in enumerate(periodos):
            processed_count += 1
            try:
                resultado = comparar_ingresos_stripe_quickbooks(
                    fecha_inicio=periodo["fecha_inicio"],
                    fecha_fin=periodo["fecha_fin"],
                    umbral=umbral,
                    cuenta_quickbooks=cuenta_quickbooks,
                    enable_parallel=False
                )
                resultado["periodo"] = periodo
                resultados.append(resultado)
                
                if resultado.get("estado") == "Ok":
                    exitosos += 1
                elif resultado.get("estado") == "Alerta":
                    alertas += 1
                    exitosos += 1
                    # Notificar discrepancias críticas
                    _notify_critical_discrepancy(resultado)
                else:
                    fallidos += 1
                
                # Reportar progreso periódicamente usando log_progress
                log_progress(
                    processed_count,
                    len(periodos),
                    "Procesamiento batch",
                    {
                        "exitosos": exitosos,
                        "fallidos": fallidos,
                        "alertas": alertas
                    }
                )
            except Exception as e:
                if not continue_on_error:
                    raise
                logger.error(f"Error procesando período {periodo}: {e}")
                fallidos += 1
                resultados.append({
                    "estado": "Error",
                    "detalles": {"motivo": str(e)},
                    "periodo": periodo
                })
    
    duration_ms = (time.time() - start_time) * 1000
    duration_seconds = duration_ms / 1000
    throughput = calculate_throughput(len(periodos), duration_seconds)
    
    if STATS_AVAILABLE:
        try:
            Stats.incr("revenue_compare.batch.processed", len(periodos))
            Stats.incr("revenue_compare.batch.successful", exitosos)
            Stats.incr("revenue_compare.batch.failed", fallidos)
            Stats.incr("revenue_compare.batch.alertas", alertas)
            Stats.timing("revenue_compare.batch.duration_ms", duration_ms)
            if throughput:
                Stats.gauge("revenue_compare.batch.throughput", throughput)
        except Exception:
            pass
    
    logger.info(
        f"Batch completado: {exitosos}/{len(periodos)} exitosos ({format_duration(duration_ms)})",
        extra={
            "total": len(periodos),
            "exitosos": exitosos,
            "fallidos": fallidos,
            "alertas": alertas,
            "duration": format_duration(duration_ms),
            "throughput": f"{throughput:.2f}/s" if throughput else None
        }
    )
    
    return {
        "total": len(periodos),
        "exitosos": exitosos,
        "fallidos": fallidos,
        "alertas": alertas,
        "duration_ms": duration_ms,
        "duration_formatted": format_duration(duration_ms),
        "throughput": throughput,
        "resultados": resultados
    }


def get_cached_quickbooks_account_id(
    cuenta_ingresos: str,
    realm_id: str
) -> Optional[str]:
    """
    Obtiene el ID de cuenta de QuickBooks con cache TTLCache.
    Cachea los resultados para reducir llamadas API.
    
    Args:
        cuenta_ingresos: Nombre de la cuenta
        realm_id: ID de la compañía
    
    Returns:
        ID de la cuenta o None si no se encuentra
    """
    if not CACHETOOLS_AVAILABLE or not _account_cache:
        return None
    
    cache_key = f"{realm_id}:{cuenta_ingresos}"
    return _account_cache.get(cache_key) if cache_key in _account_cache else None


# Versión con lru_cache si está disponible (para funciones sin estado)
if LRU_CACHE_AVAILABLE:
    @lru_cache(maxsize=10)
    def _get_quickbooks_account_id_lru(cuenta_ingresos: str, realm_id: str) -> Optional[str]:
        """Versión con lru_cache para casos simples."""
        # Esta función no se usa directamente, es un ejemplo
        return None


def format_comparison_summary(resultado: Dict[str, Any]) -> str:
    """
    Formatea un resultado de comparación en un resumen legible.
    
    Args:
        resultado: Resultado de comparar_ingresos_stripe_quickbooks
    
    Returns:
        String con resumen formateado
    """
    estado = resultado.get("estado", "Unknown")
    detalles = resultado.get("detalles", {})
    
    ingreso_stripe = detalles.get("ingreso_stripe", 0.0)
    ingreso_quickbooks = detalles.get("ingreso_quickbooks", 0.0)
    diferencia = detalles.get("diferencia", 0.0)
    diferencia_pct = detalles.get("diferencia_porcentual", 0.0)
    umbral = detalles.get("umbral", 0.0)
    
    lines = [
        f"Estado: {estado}",
        f"Período: {detalles.get('fecha_inicio', 'N/A')} - {detalles.get('fecha_fin', 'N/A')}",
        f"Ingreso Stripe: ${ingreso_stripe:,.2f}",
        f"Ingreso QuickBooks: ${ingreso_quickbooks:,.2f}",
        f"Diferencia: ${diferencia:,.2f} ({diferencia_pct:.2f}%)",
        f"Umbral: ${umbral:,.2f}",
        f"Transacciones Stripe: {detalles.get('cantidad_transacciones_stripe', 0)}",
        f"Transacciones QuickBooks: {detalles.get('cantidad_transacciones_quickbooks', 0)}"
    ]
    
    return "\n".join(lines)


def validate_comparison_result(resultado: Dict[str, Any]) -> bool:
    """
    Valida que un resultado de comparación tenga la estructura correcta.
    
    Args:
        resultado: Resultado a validar
    
    Returns:
        True si es válido, False en caso contrario
    """
    if not isinstance(resultado, dict):
        return False
    
    if "estado" not in resultado or "detalles" not in resultado:
        return False
    
    estado = resultado.get("estado")
    if estado not in ["Ok", "Alerta", "Error"]:
        return False
    
    detalles = resultado.get("detalles", {})
    required_fields = ["motivo", "ingreso_stripe", "ingreso_quickbooks", "diferencia", "umbral"]
    
    for field in required_fields:
        if field not in detalles:
            return False
    
    # Validar tipos
    try:
        float(detalles.get("ingreso_stripe", 0))
        float(detalles.get("ingreso_quickbooks", 0))
        float(detalles.get("diferencia", 0))
        float(detalles.get("umbral", 0))
    except (ValueError, TypeError):
        return False
    
    return True


def generate_comparison_report(
    resultados: List[Dict[str, Any]],
    formato: str = "text"
) -> str:
    """
    Genera un reporte consolidado de múltiples comparaciones.
    
    Args:
        resultados: Lista de resultados de comparación
        formato: Formato del reporte ('text', 'json', 'html')
    
    Returns:
        String con el reporte formateado
    """
    if not resultados:
        return "No hay resultados para reportar"
    
    total = len(resultados)
    exitosos = sum(1 for r in resultados if r.get("estado") == "Ok")
    alertas = sum(1 for r in resultados if r.get("estado") == "Alerta")
    errores = sum(1 for r in resultados if r.get("estado") == "Error")
    
    if formato == "json":
        import json
        return json.dumps({
            "resumen": {
                "total": total,
                "exitosos": exitosos,
                "alertas": alertas,
                "errores": errores
            },
            "resultados": resultados
        }, indent=2, default=str)
    
    elif formato == "html":
        html = f"""
        <html>
        <head><title>Reporte de Comparación de Ingresos</title></head>
        <body>
            <h1>Reporte de Comparación de Ingresos</h1>
            <h2>Resumen</h2>
            <ul>
                <li>Total: {total}</li>
                <li>Exitosos: {exitosos}</li>
                <li>Alertas: {alertas}</li>
                <li>Errores: {errores}</li>
            </ul>
            <h2>Resultados</h2>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Período</th>
                    <th>Estado</th>
                    <th>Ingreso Stripe</th>
                    <th>Ingreso QuickBooks</th>
                    <th>Diferencia</th>
                </tr>
        """
        for resultado in resultados:
            detalles = resultado.get("detalles", {})
            html += f"""
                <tr>
                    <td>{detalles.get('fecha_inicio', 'N/A')} - {detalles.get('fecha_fin', 'N/A')}</td>
                    <td>{resultado.get('estado', 'N/A')}</td>
                    <td>${detalles.get('ingreso_stripe', 0):,.2f}</td>
                    <td>${detalles.get('ingreso_quickbooks', 0):,.2f}</td>
                    <td>${detalles.get('diferencia', 0):,.2f}</td>
                </tr>
            """
        html += """
            </table>
        </body>
        </html>
        """
        return html
    
    else:  # text
        lines = [
            "=" * 60,
            "REPORTE DE COMPARACIÓN DE INGRESOS",
            "=" * 60,
            f"Total de comparaciones: {total}",
            f"Exitosos: {exitosos}",
            f"Alertas: {alertas}",
            f"Errores: {errores}",
            "",
            "Detalles por período:",
            "-" * 60
        ]
        
        for i, resultado in enumerate(resultados, 1):
            lines.append(f"\n{i}. {format_comparison_summary(resultado)}")
        
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)


def normalize_comparison_config(
    fecha_inicio: str,
    fecha_fin: str,
    umbral: Any = 100.0,
    cuenta_quickbooks: str = "Ventas Stripe",
    **kwargs
) -> ComparisonConfig:
    """
    Crea y normaliza una configuración de comparación.
    Función helper para facilitar la creación de configuraciones.
    
    Args:
        fecha_inicio: Fecha de inicio (cualquier formato soportado)
        fecha_fin: Fecha de fin (cualquier formato soportado)
        umbral: Umbral de diferencia (puede ser string con $ o formato numérico)
        cuenta_quickbooks: Nombre de la cuenta
        **kwargs: Parámetros adicionales para ComparisonConfig
    
    Returns:
        ComparisonConfig normalizado y validado
    
    Raises:
        ValidationError: Si los datos no son válidos
    """
    try:
        # Normalizar fechas
        fecha_inicio_norm = _normalize_date_string(fecha_inicio)
        fecha_fin_norm = _normalize_date_string(fecha_fin)
        
        # Normalizar umbral
        umbral_decimal = _normalize_amount(umbral)
        umbral_float = float(umbral_decimal)
        
        # Sanitizar cuenta
        cuenta_sanitizada = _sanitize_account_name(cuenta_quickbooks)
        
        return ComparisonConfig(
            fecha_inicio=fecha_inicio_norm,
            fecha_fin=fecha_fin_norm,
            umbral=umbral_float,
            cuenta_quickbooks=cuenta_sanitizada,
            **kwargs
        )
    except (ValueError, TypeError) as e:
        raise ValidationError(f"Error normalizando configuración: {str(e)}")


def calculate_difference_percentage(
    valor1: Any,
    valor2: Any,
    precision: int = 2
) -> float:
    """
    Calcula el porcentaje de diferencia entre dos valores.
    
    Args:
        valor1: Primer valor
        valor2: Segundo valor
        precision: Precisión decimal (default: 2)
    
    Returns:
        Porcentaje de diferencia (0-100)
    """
    try:
        v1 = _normalize_amount(valor1)
        v2 = _normalize_amount(valor2)
        
        if v1 == Decimal("0") and v2 == Decimal("0"):
            return 0.0
        
        max_valor = max(abs(v1), abs(v2))
        if max_valor == Decimal("0"):
            return 0.0
        
        diferencia = abs(v1 - v2)
        porcentaje = (diferencia / max_valor) * Decimal("100")
        
        return float(porcentaje.quantize(Decimal(f"0.{'0' * precision}")))
    except (ValueError, TypeError, ZeroDivisionError):
        return 0.0


def format_currency(amount: Any, currency: str = "USD") -> str:
    """
    Formatea un monto como moneda.
    
    Args:
        amount: Monto a formatear
        currency: Código de moneda (default: USD)
    
    Returns:
        String formateado como moneda
    """
    try:
        amount_decimal = _normalize_amount(amount)
        amount_float = float(amount_decimal)
        
        if currency == "USD":
            return f"${amount_float:,.2f}"
        elif currency == "EUR":
            return f"€{amount_float:,.2f}"
        elif currency == "GBP":
            return f"£{amount_float:,.2f}"
        else:
            return f"{amount_float:,.2f} {currency}"
    except (ValueError, TypeError):
        return f"${0.0:,.2f}" if currency == "USD" else f"0.00 {currency}"


def is_within_threshold(
    diferencia: Any,
    umbral: Any
) -> bool:
    """
    Verifica si una diferencia está dentro del umbral.
    
    Args:
        diferencia: Diferencia a verificar
        umbral: Umbral permitido
    
    Returns:
        True si está dentro del umbral, False en caso contrario
    """
    try:
        diff_decimal = _normalize_amount(diferencia)
        threshold_decimal = _normalize_amount(umbral)
        
        return abs(diff_decimal) <= threshold_decimal
    except (ValueError, TypeError):
        return False


def _compute_comparison_checksum(
    fecha_inicio: str,
    fecha_fin: str,
    cuenta_quickbooks: str
) -> str:
    """
    Calcula un checksum único para una comparación (para idempotencia).
    
    Args:
        fecha_inicio: Fecha de inicio
        fecha_fin: Fecha de fin
        cuenta_quickbooks: Nombre de la cuenta
    
    Returns:
        Checksum SHA256 como string hexadecimal
    """
    # Normalizar datos
    fecha_inicio_norm = _normalize_date_string(fecha_inicio)
    fecha_fin_norm = _normalize_date_string(fecha_fin)
    cuenta_norm = _sanitize_account_name(cuenta_quickbooks)
    
    # Crear string único basado en campos clave
    key_fields = (
        fecha_inicio_norm,
        fecha_fin_norm,
        cuenta_norm
    )
    unique_str = "|".join(key_fields)
    
    # Calcular SHA256 hash
    return hashlib.sha256(unique_str.encode('utf-8')).hexdigest()[:16]  # 16 chars para legibilidad


def _add_retry_jitter(base_delay: float, max_jitter: float = RETRY_JITTER_MAX) -> float:
    """
    Agrega jitter aleatorio a un delay de retry para evitar thundering herd.
    
    Args:
        base_delay: Delay base en segundos
        max_jitter: Jitter máximo a agregar en segundos
    
    Returns:
        Delay con jitter aplicado
    """
    jitter = random.uniform(0, max_jitter)
    return base_delay + jitter


def calculate_throughput(
    comparisons: int,
    duration_seconds: float
) -> Optional[float]:
    """
    Calcula el throughput de comparaciones por segundo.
    
    Args:
        comparisons: Número de comparaciones procesadas
        duration_seconds: Duración en segundos
    
    Returns:
        Throughput en comparaciones/segundo, o None si el cálculo es inválido
    """
    if duration_seconds <= 0 or comparisons <= 0:
        return None
    return comparisons / duration_seconds


def format_duration(milliseconds: float) -> str:
    """
    Formatea una duración en milisegundos a string legible.
    
    Args:
        milliseconds: Duración en milisegundos
    
    Returns:
        String formateado (ej: "1.5s", "2m 30s", "1h 15m")
    """
    if milliseconds < 1000:
        return f"{milliseconds:.0f}ms"
    
    seconds = milliseconds / 1000
    
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"
    
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    
    return f"{hours}h {remaining_minutes}m"


def _notify_critical_discrepancy(
    resultado: Union[ComparisonResult, ComparisonResultDict],
    threshold: float = 1000.0
) -> None:
    """
    Notifica discrepancias críticas (por ejemplo, a Slack).
    
    Args:
        resultado: Resultado de la comparación (puede ser ComparisonResult o dict)
        threshold: Umbral mínimo de diferencia para notificar (default: $1000)
    """
    try:
        # Normalizar resultado a dict si es ComparisonResult
        if isinstance(resultado, ComparisonResult):
            resultado_dict = resultado.to_dict()
            detalles = resultado.detalles
            diferencia = resultado.diferencia
            estado = resultado.estado
            diferencia_pct = resultado.diferencia_porcentual
            ingreso_stripe = resultado.ingreso_stripe
            ingreso_quickbooks = resultado.ingreso_quickbooks
            periodo = f"{resultado.fecha_inicio} - {resultado.fecha_fin}"
            motivo = detalles.get("motivo", "N/A")
        else:
            # Es un dict
            detalles = resultado.get("detalles", {})
            diferencia = detalles.get("diferencia", 0.0)
            estado = resultado.get("estado", "Unknown")
            diferencia_pct = detalles.get("diferencia_porcentual", 0.0)
            ingreso_stripe = detalles.get("ingreso_stripe", 0.0)
            ingreso_quickbooks = detalles.get("ingreso_quickbooks", 0.0)
            periodo = f"{detalles.get('fecha_inicio', 'N/A')} - {detalles.get('fecha_fin', 'N/A')}"
            motivo = detalles.get("motivo", "N/A")
        
        # Solo notificar si la diferencia es significativa
        if abs(diferencia) < threshold:
            return
        
        if estado != "Alerta":
            return
        
        # Intentar importar notificaciones
        try:
            from data.airflow.plugins.etl_notifications import notify_slack
            NOTIFICATIONS_AVAILABLE = True
        except ImportError:
            NOTIFICATIONS_AVAILABLE = False
        
        if NOTIFICATIONS_AVAILABLE:
            message = (
                f"⚠️ DISCREPANCIA CRÍTICA DE INGRESOS\n"
                f"Período: {periodo}\n"
                f"Diferencia: {format_currency(abs(diferencia))} ({diferencia_pct:.2f}%)\n"
                f"Ingreso Stripe: {format_currency(ingreso_stripe)}\n"
                f"Ingreso QuickBooks: {format_currency(ingreso_quickbooks)}\n"
                f"Motivo: {motivo}"
            )
            
            try:
                notify_slack(message)
            except Exception as e:
                logger.debug(f"No se pudo enviar notificación: {e}")
    
    except Exception as e:
        logger.debug(f"Error en notificación de discrepancia: {e}")


def _adaptive_batch_size(
    total_periods: int,
    max_workers: int = 5,
    base_batch_size: int = 3
) -> int:
    """
    Calcula un tamaño de batch adaptativo para procesamiento paralelo.
    
    Args:
        total_periods: Número total de períodos a procesar
        max_workers: Número máximo de workers disponibles
        base_batch_size: Tamaño base de batch
    
    Returns:
        Tamaño de batch calculado
    """
    if total_periods <= 0:
        return base_batch_size
    
    # Calcular batch size ideal basado en workers
    ideal_batch_size = max(base_batch_size, total_periods // max_workers)
    
    # Asegurar que no sea demasiado grande
    max_safe_batch = max_workers * 2
    ideal_batch_size = min(ideal_batch_size, max_safe_batch)
    
    return ideal_batch_size


def _analizar_tendencias_impl(dias: int, db_conn) -> Dict[str, Any]:
    """Implementación interna para analizar tendencias."""
    with db_conn.cursor() as cur:
        cur.execute("""
                SELECT 
                    COUNT(*) as total_comparaciones,
                    COUNT(*) FILTER (WHERE estado = 'Alerta') as total_alertas,
                    COUNT(*) FILTER (WHERE estado = 'Ok') as total_ok,
                    AVG(diferencia) as promedio_diferencia,
                    MAX(diferencia) as max_diferencia,
                    MIN(diferencia) as min_diferencia,
                    AVG(diferencia_porcentual) as promedio_diferencia_pct,
                    AVG(ingreso_stripe) as promedio_ingreso_stripe,
                    AVG(ingreso_quickbooks) as promedio_ingreso_quickbooks
                FROM stripe_quickbooks_revenue_comparisons
                WHERE created_at >= CURRENT_DATE - INTERVAL '%s days'
                  AND estado != 'Error'
            """, (dias,))
        
        row = cur.fetchone()
        if not row:
            return {
                "total_comparaciones": 0,
                "total_alertas": 0,
                "total_ok": 0,
                "promedio_diferencia": 0.0,
                "max_diferencia": 0.0,
                "min_diferencia": 0.0,
                "promedio_diferencia_porcentual": 0.0,
                "promedio_ingreso_stripe": 0.0,
                "promedio_ingreso_quickbooks": 0.0
            }
        
        columns = [desc[0] for desc in cur.description]
        return dict(zip(columns, row))


def compute_statistics(results: List[ComparisonResult]) -> Dict[str, Any]:
    """
    Calcula estadísticas agregadas de una lista de resultados de comparación.
    
    Args:
        results: Lista de resultados de comparación
    
    Returns:
        Dict con estadísticas: total, exitosos, fallidos, alertas, diferencias, etc.
    """
    if not results:
        return {
            "total": 0,
            "exitosos": 0,
            "fallidos": 0,
            "alertas": 0,
            "promedio_diferencia": 0.0,
            "max_diferencia": 0.0,
            "min_diferencia": 0.0,
            "promedio_diferencia_pct": 0.0,
            "total_ingreso_stripe": 0.0,
            "total_ingreso_quickbooks": 0.0
        }
    
    exitosos = sum(1 for r in results if r.get("estado") == "Ok")
    fallidos = sum(1 for r in results if r.get("estado") == "Error")
    alertas = sum(1 for r in results if r.get("estado") == "Alerta")
    
    diferencias = []
    diferencias_pct = []
    ingresos_stripe = []
    ingresos_quickbooks = []
    
    for r in results:
        if r.get("estado") == "Error":
            continue
        
        detalles = r.get("detalles", {})
        diff = detalles.get("diferencia", 0.0)
        diff_pct = detalles.get("diferencia_porcentual", 0.0)
        ing_stripe = detalles.get("ingreso_stripe", 0.0)
        ing_qb = detalles.get("ingreso_quickbooks", 0.0)
        
        if diff is not None:
            diferencias.append(float(diff))
        if diff_pct is not None:
            diferencias_pct.append(float(diff_pct))
        if ing_stripe is not None:
            ingresos_stripe.append(float(ing_stripe))
        if ing_qb is not None:
            ingresos_quickbooks.append(float(ing_qb))
    
    return {
        "total": len(results),
        "exitosos": exitosos,
        "fallidos": fallidos,
        "alertas": alertas,
        "promedio_diferencia": sum(diferencias) / len(diferencias) if diferencias else 0.0,
        "max_diferencia": max(diferencias) if diferencias else 0.0,
        "min_diferencia": min(diferencias) if diferencias else 0.0,
        "promedio_diferencia_pct": sum(diferencias_pct) / len(diferencias_pct) if diferencias_pct else 0.0,
        "total_ingreso_stripe": sum(ingresos_stripe),
        "total_ingreso_quickbooks": sum(ingresos_quickbooks),
        "promedio_ingreso_stripe": sum(ingresos_stripe) / len(ingresos_stripe) if ingresos_stripe else 0.0,
        "promedio_ingreso_quickbooks": sum(ingresos_quickbooks) / len(ingresos_quickbooks) if ingresos_quickbooks else 0.0
    }


def log_progress(
    current: int,
    total: int,
    step_name: str = "Procesamiento",
    extra_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Logea el progreso de un proceso de manera estructurada.
    
    Args:
        current: Índice actual (1-indexed o 0-indexed)
        total: Total de items
        step_name: Nombre de la operación
        extra_context: Contexto adicional para el log
    """
    if total <= 0:
        return
    
    progress_pct = (current / total) * 100
    
    # Solo loguear en intervalos o en el último item
    if current % PROGRESS_REPORT_INTERVAL == 0 or current == total:
        context = {
            "current": current,
            "total": total,
            "progress_pct": f"{progress_pct:.1f}%",
            "step": step_name,
            **(extra_context or {})
        }
        
        logger.info(
            f"{step_name}: {current}/{total} ({progress_pct:.1f}%)",
            extra=context
        )


# Circuit breaker simple en memoria
_circuit_breaker_state: Dict[str, Dict[str, Any]] = {}


def _check_circuit_breaker(operation: str) -> bool:
    """
    Verifica si el circuit breaker está abierto para una operación.
    
    Args:
        operation: Nombre de la operación (ej: "stripe_api", "quickbooks_api")
    
    Returns:
        True si el circuit breaker está cerrado (permite la operación),
        False si está abierto (bloquea la operación)
    """
    if operation not in _circuit_breaker_state:
        _circuit_breaker_state[operation] = {
            "failures": 0,
            "last_failure": None,
            "state": "closed"  # closed, open, half_open
        }
        return True
    
    state = _circuit_breaker_state[operation]
    current_time = time.time()
    
    # Si está abierto, verificar si es hora de intentar de nuevo (half-open)
    if state["state"] == "open":
        reset_time = CIRCUIT_BREAKER_RESET_MINUTES * 60
        if state["last_failure"] and (current_time - state["last_failure"]) >= reset_time:
            state["state"] = "half_open"
            state["failures"] = 0
            logger.info(f"Circuit breaker para {operation} movido a half-open")
            return True
        return False
    
    # Si está cerrado o half-open, permitir
    return True


def _record_circuit_breaker_success(operation: str) -> None:
    """
    Registra un éxito en el circuit breaker.
    
    Args:
        operation: Nombre de la operación
    """
    if operation not in _circuit_breaker_state:
        return
    
    state = _circuit_breaker_state[operation]
    
    # Si estaba en half-open, cerrarlo
    if state["state"] == "half_open":
        state["state"] = "closed"
        state["failures"] = 0
        logger.info(f"Circuit breaker para {operation} cerrado después de éxito")


def _record_circuit_breaker_failure(operation: str) -> None:
    """
    Registra un fallo en el circuit breaker.
    
    Args:
        operation: Nombre de la operación
    """
    if operation not in _circuit_breaker_state:
        _circuit_breaker_state[operation] = {
            "failures": 0,
            "last_failure": None,
            "state": "closed"
        }
    
    state = _circuit_breaker_state[operation]
    state["failures"] += 1
    state["last_failure"] = time.time()
    
    # Si excede el umbral, abrir el circuit breaker
    if state["failures"] >= CIRCUIT_BREAKER_FAILURE_THRESHOLD:
        state["state"] = "open"
        logger.warning(
            f"Circuit breaker para {operation} ABIERTO después de {state['failures']} fallos",
            extra={
                "operation": operation,
                "failures": state["failures"],
                "threshold": CIRCUIT_BREAKER_FAILURE_THRESHOLD
            }
        )


def detect_anomalies(
    results: List[ComparisonResult],
    z_score_threshold: float = 2.0
) -> List[Dict[str, Any]]:
    """
    Detecta anomalías en los resultados usando z-score.
    
    Args:
        results: Lista de resultados de comparación
        z_score_threshold: Umbral de z-score para considerar una anomalía (default: 2.0)
    
    Returns:
        Lista de resultados marcados como anomalías con sus z-scores
    """
    if len(results) < 3:  # Necesitamos al menos 3 puntos para calcular estadísticas
        return []
    
    # Extraer diferencias
    diferencias = []
    for r in results:
        if r.get("estado") != "Error":
            detalles = r.get("detalles", {})
            diff = detalles.get("diferencia", 0.0)
            if diff is not None:
                diferencias.append(float(diff))
    
    if len(diferencias) < 3:
        return []
    
    # Calcular media y desviación estándar
    import statistics
    mean_diff = statistics.mean(diferencias)
    stdev_diff = statistics.stdev(diferencias) if len(diferencias) > 1 else 0.0
    
    if stdev_diff == 0:
        return []
    
    # Detectar anomalías
    anomalies = []
    for i, r in enumerate(results):
        if r.get("estado") == "Error":
            continue
        
        detalles = r.get("detalles", {})
        diff = detalles.get("diferencia", 0.0)
        
        if diff is not None:
            z_score = abs((float(diff) - mean_diff) / stdev_diff)
            
            if z_score >= z_score_threshold:
                anomalies.append({
                    "result": r,
                    "z_score": z_score,
                    "difference": diff,
                    "mean": mean_diff,
                    "std_dev": stdev_diff
                })
    
    return anomalies


def serialize_comparison_result(result: ComparisonResult) -> str:
    """
    Serializa un resultado de comparación a JSON string.
    
    Args:
        result: Resultado de comparación
    
    Returns:
        String JSON serializado
    """
    try:
        # Convertir Decimal a float para JSON
        def decimal_default(obj):
            if isinstance(obj, Decimal):
                return float(obj)
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        return json.dumps(result, default=decimal_default, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error serializando resultado: {e}", extra={"error": str(e)})
        return json.dumps({"error": "Serialization failed", "message": str(e)})


def deserialize_comparison_result(json_str: str) -> ComparisonResult:
    """
    Deserializa un resultado de comparación desde JSON string.
    
    Args:
        json_str: String JSON
    
    Returns:
        Diccionario con el resultado de comparación
    """
    try:
        return json.loads(json_str)
    except Exception as e:
        logger.error(f"Error deserializando resultado: {e}", extra={"error": str(e)})
        return _create_error_result(
            f"Error deserializando: {str(e)}",
            {"json_str_length": len(json_str)}
        )


def normalize_result_for_storage(result: ComparisonResult) -> Dict[str, Any]:
    """
    Normaliza un resultado para almacenamiento en base de datos.
    Convierte Decimal a float y asegura tipos compatibles.
    
    Args:
        result: Resultado de comparación
    
    Returns:
        Resultado normalizado con tipos compatibles con PostgreSQL
    """
    normalized = result.copy()
    
    # Normalizar detalles
    if "detalles" in normalized and isinstance(normalized["detalles"], dict):
        detalles = normalized["detalles"].copy()
        
        for key, value in detalles.items():
            if isinstance(value, Decimal):
                detalles[key] = float(value)
            elif isinstance(value, (int, float)) and (isinstance(value, float) or abs(value) > 2147483647):
                # Asegurar que los números grandes sean float
                detalles[key] = float(value)
        
        normalized["detalles"] = detalles
    
    return normalized


def validate_batch_input(periods: List[Dict[str, str]]) -> Tuple[bool, Optional[str]]:
    """
    Valida una lista de períodos para batch processing.
    
    Args:
        periods: Lista de dicts con 'fecha_inicio' y 'fecha_fin'
    
    Returns:
        Tuple de (es_válido, mensaje_error)
    """
    if not periods:
        return False, "Lista de períodos vacía"
    
    if not isinstance(periods, list):
        return False, "periods debe ser una lista"
    
    for i, period in enumerate(periods):
        if not isinstance(period, dict):
            return False, f"Período {i} debe ser un diccionario"
        
        if "fecha_inicio" not in period or "fecha_fin" not in period:
            return False, f"Período {i} debe tener 'fecha_inicio' y 'fecha_fin'"
        
        error, _, _ = _validate_date_range(period["fecha_inicio"], period["fecha_fin"])
        if error:
            return False, f"Período {i}: {str(error)}"
    
    return True, None


def filter_results(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    estado: Optional[str] = None,
    min_diferencia: Optional[float] = None,
    max_diferencia: Optional[float] = None,
    fecha_desde: Optional[str] = None,
    fecha_hasta: Optional[str] = None
) -> List[ComparisonResult]:
    """
    Filtra una lista de resultados según criterios específicos.
    
    Args:
        results: Lista de resultados (puede ser ComparisonResult o dict)
        estado: Filtrar por estado ("Ok", "Alerta", "Error")
        min_diferencia: Diferencia mínima (absoluta)
        max_diferencia: Diferencia máxima (absoluta)
        fecha_desde: Fecha de inicio mínima (YYYY-MM-DD)
        fecha_hasta: Fecha de fin máxima (YYYY-MM-DD)
    
    Returns:
        Lista de ComparisonResult filtrados
    
    Example:
        >>> resultados = [result1, result2, result3]
        >>> alertas = filter_results(resultados, estado="Alerta", min_diferencia=100.0)
    """
    filtered = []
    
    for r in results:
        # Normalizar a ComparisonResult si es dict
        if isinstance(r, dict):
            result = ComparisonResult.from_dict(r)
        else:
            result = r
        
        # Filtrar por estado
        if estado and result.estado != estado:
            continue
        
        # Filtrar por diferencia
        diff_abs = abs(result.diferencia)
        if min_diferencia is not None and diff_abs < min_diferencia:
            continue
        if max_diferencia is not None and diff_abs > max_diferencia:
            continue
        
        # Filtrar por fecha
        if fecha_desde and result.fecha_inicio < fecha_desde:
            continue
        if fecha_hasta and result.fecha_fin > fecha_hasta:
            continue
        
        filtered.append(result)
    
    return filtered


def group_results_by_period(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    group_by: str = "month"
) -> Dict[str, List[ComparisonResult]]:
    """
    Agrupa resultados por período (mes, trimestre, año).
    
    Args:
        results: Lista de resultados
        group_by: Criterio de agrupación ("month", "quarter", "year")
    
    Returns:
        Dict con claves de período y listas de resultados
    
    Example:
        >>> resultados = [result1, result2, result3]
        >>> por_mes = group_results_by_period(resultados, group_by="month")
        >>> print(por_mes["2024-01"])  # Resultados de enero 2024
    """
    grouped: Dict[str, List[ComparisonResult]] = {}
    
    for r in results:
        # Normalizar a ComparisonResult si es dict
        if isinstance(r, dict):
            result = ComparisonResult.from_dict(r)
        else:
            result = r
        
        # Determinar la clave de agrupación
        fecha_inicio = result.fecha_inicio
        try:
            fecha = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            
            if group_by == "month":
                key = fecha.strftime("%Y-%m")
            elif group_by == "quarter":
                quarter = (fecha.month - 1) // 3 + 1
                key = f"{fecha.year}-Q{quarter}"
            elif group_by == "year":
                key = str(fecha.year)
            else:
                key = fecha_inicio  # Fallback a fecha completa
        except ValueError:
            key = fecha_inicio  # Fallback si no se puede parsear
        
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(result)
    
    return grouped


def find_results_by_date_range(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    fecha_inicio: str,
    fecha_fin: str
) -> List[ComparisonResult]:
    """
    Encuentra resultados que se superponen con un rango de fechas.
    
    Args:
        results: Lista de resultados
        fecha_inicio: Fecha de inicio del rango (YYYY-MM-DD)
        fecha_fin: Fecha de fin del rango (YYYY-MM-DD)
    
    Returns:
        Lista de resultados que se superponen con el rango
    
    Example:
        >>> resultados = [result1, result2, result3]
        >>> en_rango = find_results_by_date_range(
        ...     resultados, "2024-01-01", "2024-01-31"
        ... )
    """
    normalized_inicio = _normalize_date_string(fecha_inicio)
    normalized_fin = _normalize_date_string(fecha_fin)
    
    matching = []
    for r in results:
        if isinstance(r, dict):
            result = ComparisonResult.from_dict(r)
        else:
            result = r
        
        # Verificar superposición de rangos
        # Los rangos se superponen si: inicio1 <= fin2 AND fin1 >= inicio2
        if (result.fecha_inicio <= normalized_fin and 
            result.fecha_fin >= normalized_inicio):
            matching.append(result)
    
    return matching


def get_top_results(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    n: int = 10,
    by: str = "diferencia"
) -> List[ComparisonResult]:
    """
    Obtiene los top N resultados ordenados por un criterio.
    
    Args:
        results: Lista de resultados
        n: Número de resultados a retornar
        by: Criterio de ordenamiento ("diferencia", "diferencia_porcentual", "ingreso_stripe", "ingreso_quickbooks")
    
    Returns:
        Lista de los top N ComparisonResult
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> top_10 = get_top_results(resultados, n=10, by="diferencia")
    """
    # Normalizar a ComparisonResult
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    # Ordenar según criterio
    if by == "diferencia":
        sorted_results = sorted(normalized, key=lambda x: abs(x.diferencia), reverse=True)
    elif by == "diferencia_porcentual":
        sorted_results = sorted(normalized, key=lambda x: abs(x.diferencia_porcentual), reverse=True)
    elif by == "ingreso_stripe":
        sorted_results = sorted(normalized, key=lambda x: x.ingreso_stripe, reverse=True)
    elif by == "ingreso_quickbooks":
        sorted_results = sorted(normalized, key=lambda x: x.ingreso_quickbooks, reverse=True)
    else:
        # Default: por diferencia absoluta
        sorted_results = sorted(normalized, key=lambda x: abs(x.diferencia), reverse=True)
    
    return sorted_results[:n]


def summarize_results(
    results: List[Union[ComparisonResult, ComparisonResultDict]]
) -> Dict[str, Any]:
    """
    Genera un resumen estadístico de una lista de resultados.
    
    Args:
        results: Lista de resultados
    
    Returns:
        Dict con estadísticas agregadas
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> resumen = summarize_results(resultados)
        >>> print(f"Total alertas: {resumen['alertas']}")
    """
    if not results:
        return {
            "total": 0,
            "ok": 0,
            "alertas": 0,
            "errores": 0,
            "promedio_diferencia": 0.0,
            "max_diferencia": 0.0,
            "min_diferencia": 0.0
        }
    
    # Normalizar a ComparisonResult
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    ok = sum(1 for r in normalized if r.is_ok)
    alertas = sum(1 for r in normalized if r.is_alerta)
    errores = sum(1 for r in normalized if r.is_error)
    
    diferencias = [abs(r.diferencia) for r in normalized if not r.is_error]
    
    return {
        "total": len(normalized),
        "ok": ok,
        "alertas": alertas,
        "errores": errores,
        "promedio_diferencia": sum(diferencias) / len(diferencias) if diferencias else 0.0,
        "max_diferencia": max(diferencias) if diferencias else 0.0,
        "min_diferencia": min(diferencias) if diferencias else 0.0,
        "tasa_ok": (ok / len(normalized) * 100) if normalized else 0.0,
        "tasa_alertas": (alertas / len(normalized) * 100) if normalized else 0.0,
        "tasa_errores": (errores / len(normalized) * 100) if normalized else 0.0
    }


def export_results_to_csv(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    filepath: str,
    include_details: bool = True
) -> str:
    """
    Exporta resultados de comparación a un archivo CSV.
    
    Args:
        results: Lista de resultados a exportar
        filepath: Ruta del archivo CSV a crear
        include_details: Si True, incluye columnas adicionales de detalles
    
    Returns:
        Ruta del archivo CSV creado
    
    Example:
        >>> resultados = [result1, result2, result3]
        >>> csv_path = export_results_to_csv(resultados, "/tmp/comparaciones.csv")
    """
    import csv
    
    if not results:
        raise ValueError("Lista de resultados vacía")
    
    # Normalizar a ComparisonResult
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    # Determinar columnas
    fieldnames = [
        "fecha_inicio",
        "fecha_fin",
        "estado",
        "diferencia",
        "diferencia_porcentual",
        "ingreso_stripe",
        "ingreso_quickbooks",
        "umbral",
        "cuenta_quickbooks"
    ]
    
    if include_details:
        fieldnames.extend([
            "cantidad_transacciones_stripe",
            "cantidad_transacciones_quickbooks",
            "timestamp",
            "duration_ms"
        ])
    
    # Escribir CSV
    with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in normalized:
            row = {
                "fecha_inicio": result.fecha_inicio,
                "fecha_fin": result.fecha_fin,
                "estado": result.estado,
                "diferencia": f"{result.diferencia:.2f}",
                "diferencia_porcentual": f"{result.diferencia_porcentual:.2f}",
                "ingreso_stripe": f"{result.ingreso_stripe:.2f}",
                "ingreso_quickbooks": f"{result.ingreso_quickbooks:.2f}",
                "umbral": f"{result.umbral:.2f}",
                "cuenta_quickbooks": result.cuenta_quickbooks
            }
            
            if include_details:
                detalles = result.detalles
                row.update({
                    "cantidad_transacciones_stripe": str(detalles.get("cantidad_transacciones_stripe", 0)),
                    "cantidad_transacciones_quickbooks": str(detalles.get("cantidad_transacciones_quickbooks", 0)),
                    "timestamp": str(result.timestamp) if result.timestamp else "",
                    "duration_ms": str(result.duration_ms) if result.duration_ms else ""
                })
            
            writer.writerow(row)
    
    logger.info(f"Exportados {len(normalized)} resultados a {filepath}")
    return filepath


def export_results_to_json(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    filepath: str,
    indent: int = 2
) -> str:
    """
    Exporta resultados de comparación a un archivo JSON.
    
    Args:
        results: Lista de resultados a exportar
        filepath: Ruta del archivo JSON a crear
        indent: Indentación del JSON (default: 2)
    
    Returns:
        Ruta del archivo JSON creado
    
    Example:
        >>> resultados = [result1, result2, result3]
        >>> json_path = export_results_to_json(resultados, "/tmp/comparaciones.json")
    """
    if not results:
        raise ValueError("Lista de resultados vacía")
    
    # Normalizar a dicts
    data = [
        (r.to_dict() if isinstance(r, ComparisonResult) else r)
        for r in results
    ]
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, default=str, ensure_ascii=False, indent=indent)
    
    logger.info(f"Exportados {len(data)} resultados a {filepath}")
    return filepath


def load_results_from_json(filepath: str) -> List[ComparisonResult]:
    """
    Carga resultados de comparación desde un archivo JSON.
    
    Args:
        filepath: Ruta del archivo JSON
    
    Returns:
        Lista de ComparisonResult
    
    Example:
        >>> resultados = load_results_from_json("/tmp/comparaciones.json")
    """
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in data
    ]


def validate_comparison_configs(
    configs: List[Union[ComparisonConfig, Dict[str, Any]]]
) -> Tuple[List[ComparisonConfig], List[str]]:
    """
    Valida una lista de configuraciones de comparación.
    
    Args:
        configs: Lista de configuraciones (puede ser ComparisonConfig o dict)
    
    Returns:
        Tuple de (configuraciones_válidas, errores)
    
    Example:
        >>> configs = [config1, config2, config3]
        >>> validas, errores = validate_comparison_configs(configs)
    """
    valid_configs = []
    errors = []
    
    for i, config in enumerate(configs):
        try:
            # Normalizar a ComparisonConfig
            if isinstance(config, dict):
                comp_config = ComparisonConfig.from_dict(config)
            else:
                comp_config = config
            
            # Validar
            error = comp_config.validate()
            if error:
                errors.append(f"Configuración {i}: {str(error)}")
            else:
                valid_configs.append(comp_config)
        except Exception as e:
            errors.append(f"Configuración {i}: Error procesando - {str(e)}")
    
    return valid_configs, errors


def create_comparison_periods(
    fecha_inicio: str,
    fecha_fin: str,
    periodo: str = "month"
) -> List[Dict[str, str]]:
    """
    Crea una lista de períodos desde una fecha de inicio hasta una fecha de fin.
    
    Args:
        fecha_inicio: Fecha de inicio (YYYY-MM-DD)
        fecha_fin: Fecha de fin (YYYY-MM-DD)
        periodo: Tipo de período ("day", "week", "month", "quarter", "year")
    
    Returns:
        Lista de dicts con 'fecha_inicio' y 'fecha_fin' para cada período
    
    Example:
        >>> periodos = create_comparison_periods("2024-01-01", "2024-03-31", "month")
        >>> # Retorna períodos mensuales para el trimestre
    """
    inicio = datetime.strptime(_normalize_date_string(fecha_inicio), "%Y-%m-%d")
    fin = datetime.strptime(_normalize_date_string(fecha_fin), "%Y-%m-%d")
    
    if inicio > fin:
        raise ValueError("fecha_inicio debe ser anterior a fecha_fin")
    
    periods = []
    current = inicio
    
    while current <= fin:
        if periodo == "day":
            period_end = current
        elif periodo == "week":
            # Semana: lunes a domingo
            days_ahead = 6 - current.weekday()
            period_end = current + timedelta(days=days_ahead)
        elif periodo == "month":
            # Primer día del mes siguiente menos un día
            if current.month == 12:
                period_end = datetime(current.year + 1, 1, 1) - timedelta(days=1)
            else:
                period_end = datetime(current.year, current.month + 1, 1) - timedelta(days=1)
        elif periodo == "quarter":
            # Fin del trimestre
            quarter_end_month = ((current.month - 1) // 3 + 1) * 3
            if quarter_end_month > 12:
                quarter_end_month = 12
                year = current.year + 1
            else:
                year = current.year
            period_end = datetime(year, quarter_end_month + 1, 1) - timedelta(days=1)
        elif periodo == "year":
            period_end = datetime(current.year, 12, 31)
        else:
            raise ValueError(f"Período no soportado: {periodo}")
        
        # Asegurar que no exceda la fecha fin
        if period_end > fin:
            period_end = fin
        
        periods.append({
            "fecha_inicio": current.strftime("%Y-%m-%d"),
            "fecha_fin": period_end.strftime("%Y-%m-%d")
        })
        
        # Avanzar al siguiente período
        if periodo == "day":
            current = current + timedelta(days=1)
        elif periodo == "week":
            current = period_end + timedelta(days=1)
        elif periodo == "month":
            if current.month == 12:
                current = datetime(current.year + 1, 1, 1)
            else:
                current = datetime(current.year, current.month + 1, 1)
        elif periodo == "quarter":
            if current.month <= 3:
                current = datetime(current.year, 4, 1)
            elif current.month <= 6:
                current = datetime(current.year, 7, 1)
            elif current.month <= 9:
                current = datetime(current.year, 10, 1)
            else:
                current = datetime(current.year + 1, 1, 1)
        elif periodo == "year":
            current = datetime(current.year + 1, 1, 1)
        
        if period_end >= fin:
            break
    
    return periods


def create_test_result(
    estado: str = "Ok",
    diferencia: float = 0.0,
    ingreso_stripe: float = 1000.0,
    ingreso_quickbooks: float = 1000.0,
    fecha_inicio: Optional[str] = None,
    fecha_fin: Optional[str] = None,
    umbral: float = 100.0,
    cuenta_quickbooks: str = "Ventas Stripe",
    **kwargs
) -> ComparisonResult:
    """
    Crea un resultado de prueba para testing.
    
    Args:
        estado: Estado del resultado ("Ok", "Alerta", "Error")
        diferencia: Diferencia entre ingresos
        ingreso_stripe: Ingreso de Stripe
        ingreso_quickbooks: Ingreso de QuickBooks
        fecha_inicio: Fecha de inicio (default: hoy - 30 días)
        fecha_fin: Fecha de fin (default: hoy)
        umbral: Umbral configurado
        cuenta_quickbooks: Cuenta de QuickBooks
        **kwargs: Parámetros adicionales para detalles
    
    Returns:
        ComparisonResult de prueba
    
    Example:
        >>> # Crear resultado OK
        >>> result_ok = create_test_result(estado="Ok", diferencia=10.0)
        
        >>> # Crear alerta
        >>> result_alerta = create_test_result(
        ...     estado="Alerta",
        ...     diferencia=150.0,
        ...     umbral=100.0
        ... )
    """
    if fecha_inicio is None:
        fecha_inicio = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    if fecha_fin is None:
        fecha_fin = datetime.now().strftime("%Y-%m-%d")
    
    # Calcular diferencia porcentual
    ingreso_promedio = (ingreso_stripe + ingreso_quickbooks) / 2
    diferencia_porcentual = (diferencia / ingreso_promedio * 100) if ingreso_promedio > 0 else 0.0
    
    detalles = {
        "motivo": kwargs.get("motivo", "Comparación de prueba"),
        "ingreso_stripe": ingreso_stripe,
        "ingreso_quickbooks": ingreso_quickbooks,
        "diferencia": diferencia,
        "diferencia_absoluta": abs(diferencia),
        "diferencia_porcentual": diferencia_porcentual,
        "umbral": umbral,
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin,
        "cuenta_quickbooks": cuenta_quickbooks,
        "cantidad_transacciones_stripe": kwargs.get("cantidad_transacciones_stripe", 10),
        "cantidad_transacciones_quickbooks": kwargs.get("cantidad_transacciones_quickbooks", 10),
        **kwargs
    }
    
    return ComparisonResult(
        estado=estado,
        diferencia=diferencia,
        diferencia_porcentual=diferencia_porcentual,
        ingreso_stripe=ingreso_stripe,
        ingreso_quickbooks=ingreso_quickbooks,
        detalles=detalles,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        umbral=umbral,
        cuenta_quickbooks=cuenta_quickbooks,
        timestamp=kwargs.get("timestamp", time.time()),
        duration_ms=kwargs.get("duration_ms", 100.0)
    )


def create_test_batch_result(
    n_results: int = 5,
    n_alertas: int = 1,
    n_errores: int = 0,
    **kwargs
) -> BatchComparisonResult:
    """
    Crea un resultado de batch de prueba para testing.
    
    Args:
        n_results: Número total de resultados
        n_alertas: Número de alertas
        n_errores: Número de errores
        **kwargs: Parámetros adicionales
    
    Returns:
        BatchComparisonResult de prueba
    
    Example:
        >>> batch = create_test_batch_result(n_results=10, n_alertas=2)
        >>> assert batch.total == 10
        >>> assert batch.alertas == 2
    """
    resultados = []
    
    for i in range(n_results):
        if i < n_errores:
            estado = "Error"
            diferencia = 0.0
        elif i < n_errores + n_alertas:
            estado = "Alerta"
            diferencia = 200.0  # Mayor que umbral default
        else:
            estado = "Ok"
            diferencia = 10.0  # Menor que umbral default
        
        resultado = create_test_result(
            estado=estado,
            diferencia=diferencia,
            fecha_inicio=(datetime.now() - timedelta(days=n_results - i)).strftime("%Y-%m-%d"),
            fecha_fin=(datetime.now() - timedelta(days=n_results - i - 1)).strftime("%Y-%m-%d") if i < n_results - 1 else datetime.now().strftime("%Y-%m-%d"),
            **kwargs
        )
        resultados.append(resultado)
    
    exitosos = n_results - n_errores
    fallidos = n_errores
    alertas = n_alertas
    
    return BatchComparisonResult(
        total=n_results,
        exitosos=exitosos,
        fallidos=fallidos,
        alertas=alertas,
        resultados=resultados,
        duration_ms=kwargs.get("duration_ms", 1000.0),
        throughput=kwargs.get("throughput", n_results / 1.0)
    )


def compare_results_side_by_side(
    result1: Union[ComparisonResult, ComparisonResultDict],
    result2: Union[ComparisonResult, ComparisonResultDict]
) -> Dict[str, Any]:
    """
    Compara dos resultados lado a lado y muestra las diferencias.
    
    Args:
        result1: Primer resultado
        result2: Segundo resultado
    
    Returns:
        Dict con comparación detallada
    
    Example:
        >>> result1 = ComparisonResult.from_dict(...)
        >>> result2 = ComparisonResult.from_dict(...)
        >>> comparacion = compare_results_side_by_side(result1, result2)
        >>> print(comparacion['diferencias'])
    """
    # Normalizar a ComparisonResult
    if isinstance(result1, dict):
        r1 = ComparisonResult.from_dict(result1)
    else:
        r1 = result1
    
    if isinstance(result2, dict):
        r2 = ComparisonResult.from_dict(result2)
    else:
        r2 = result2
    
    diferencias = []
    
    # Comparar cada campo
    if r1.estado != r2.estado:
        diferencias.append(f"Estado: {r1.estado} vs {r2.estado}")
    
    if abs(r1.diferencia - r2.diferencia) > 0.01:
        diferencias.append(f"Diferencia: ${r1.diferencia:.2f} vs ${r2.diferencia:.2f}")
    
    if abs(r1.ingreso_stripe - r2.ingreso_stripe) > 0.01:
        diferencias.append(f"Ingreso Stripe: ${r1.ingreso_stripe:.2f} vs ${r2.ingreso_stripe:.2f}")
    
    if abs(r1.ingreso_quickbooks - r2.ingreso_quickbooks) > 0.01:
        diferencias.append(f"Ingreso QuickBooks: ${r1.ingreso_quickbooks:.2f} vs ${r2.ingreso_quickbooks:.2f}")
    
    if r1.fecha_inicio != r2.fecha_inicio:
        diferencias.append(f"Fecha inicio: {r1.fecha_inicio} vs {r2.fecha_inicio}")
    
    if r1.fecha_fin != r2.fecha_fin:
        diferencias.append(f"Fecha fin: {r1.fecha_fin} vs {r2.fecha_fin}")
    
    return {
        "resultado1": r1.to_dict(),
        "resultado2": r2.to_dict(),
        "diferencias": diferencias,
        "son_iguales": len(diferencias) == 0,
        "diferencia_diferencia": r1.diferencia - r2.diferencia,
        "diferencia_ingreso_stripe": r1.ingreso_stripe - r2.ingreso_stripe,
        "diferencia_ingreso_quickbooks": r1.ingreso_quickbooks - r2.ingreso_quickbooks
    }


def validate_result_consistency(
    result: Union[ComparisonResult, ComparisonResultDict]
) -> Tuple[bool, List[str]]:
    """
    Valida la consistencia interna de un resultado.
    
    Args:
        result: Resultado a validar
    
    Returns:
        Tuple de (es_consistente, lista_de_errores)
    
    Example:
        >>> result = ComparisonResult.from_dict(...)
        >>> es_valido, errores = validate_result_consistency(result)
        >>> if not es_valido:
        ...     print(f"Errores: {errores}")
    """
    errors = []
    
    # Normalizar a ComparisonResult
    if isinstance(result, dict):
        r = ComparisonResult.from_dict(result)
    else:
        r = result
    
    # Validar que la diferencia sea consistente
    diferencia_calculada = r.ingreso_stripe - r.ingreso_quickbooks
    if abs(diferencia_calculada - r.diferencia) > 0.01:
        errors.append(f"Diferencia inconsistente: calculada={diferencia_calculada:.2f}, reportada={r.diferencia:.2f}")
    
    # Validar diferencia porcentual
    ingreso_promedio = (r.ingreso_stripe + r.ingreso_quickbooks) / 2
    if ingreso_promedio > 0:
        diferencia_pct_calculada = (r.diferencia / ingreso_promedio) * 100
        if abs(diferencia_pct_calculada - r.diferencia_porcentual) > 0.01:
            errors.append(f"Diferencia porcentual inconsistente: calculada={diferencia_pct_calculada:.2f}%, reportada={r.diferencia_porcentual:.2f}%")
    
    # Validar estado vs diferencia vs umbral
    if r.estado == "Ok" and abs(r.diferencia) > r.umbral:
        errors.append(f"Estado 'Ok' pero diferencia ${abs(r.diferencia):.2f} > umbral ${r.umbral:.2f}")
    
    if r.estado == "Alerta" and abs(r.diferencia) <= r.umbral:
        errors.append(f"Estado 'Alerta' pero diferencia ${abs(r.diferencia):.2f} <= umbral ${r.umbral:.2f}")
    
    # Validar fechas
    try:
        inicio = datetime.strptime(r.fecha_inicio, "%Y-%m-%d")
        fin = datetime.strptime(r.fecha_fin, "%Y-%m-%d")
        if inicio > fin:
            errors.append(f"Fecha inicio ({r.fecha_inicio}) es posterior a fecha fin ({r.fecha_fin})")
    except ValueError as e:
        errors.append(f"Formato de fecha inválido: {str(e)}")
    
    # Validar valores no negativos donde aplica
    if r.ingreso_stripe < 0:
        errors.append(f"Ingreso Stripe negativo: ${r.ingreso_stripe:.2f}")
    
    if r.ingreso_quickbooks < 0:
        errors.append(f"Ingreso QuickBooks negativo: ${r.ingreso_quickbooks:.2f}")
    
    return len(errors) == 0, errors


def merge_results(
    results1: List[Union[ComparisonResult, ComparisonResultDict]],
    results2: List[Union[ComparisonResult, ComparisonResultDict]],
    deduplicate: bool = True
) -> List[ComparisonResult]:
    """
    Combina dos listas de resultados, opcionalmente deduplicando.
    
    Args:
        results1: Primera lista de resultados
        results2: Segunda lista de resultados
        deduplicate: Si True, elimina duplicados basado en __eq__
    
    Returns:
        Lista combinada de ComparisonResult
    
    Example:
        >>> resultados_enero = [result1, result2]
        >>> resultados_febrero = [result3, result4]
        >>> todos = merge_results(resultados_enero, resultados_febrero)
    """
    # Normalizar ambas listas
    normalized1 = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results1
    ]
    normalized2 = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results2
    ]
    
    # Combinar
    merged = normalized1 + normalized2
    
    # Deduplicar si se solicita
    if deduplicate:
        seen = set()
        unique = []
        for r in merged:
            # Usar hash para deduplicación rápida
            r_hash = hash(r)
            if r_hash not in seen:
                seen.add(r_hash)
                unique.append(r)
        return unique
    
    return merged


def calculate_trend(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    metric: str = "diferencia"
) -> Dict[str, Any]:
    """
    Calcula la tendencia de una métrica a lo largo del tiempo.
    
    Args:
        results: Lista de resultados ordenados por fecha
        metric: Métrica a analizar ("diferencia", "diferencia_porcentual", "ingreso_stripe", "ingreso_quickbooks")
    
    Returns:
        Dict con análisis de tendencia
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> tendencia = calculate_trend(resultados, metric="diferencia")
        >>> print(f"Tendencia: {tendencias['direction']} ({tendencias['slope']:.2f})")
    """
    if not results or len(results) < 2:
        return {
            "direction": "insufficient_data",
            "slope": 0.0,
            "r_squared": 0.0,
            "data_points": len(results) if results else 0
        }
    
    # Normalizar y ordenar por fecha
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    normalized.sort(key=lambda x: x.fecha_inicio)
    
    # Extraer valores según métrica
    values = []
    for r in normalized:
        if metric == "diferencia":
            values.append(abs(r.diferencia))
        elif metric == "diferencia_porcentual":
            values.append(abs(r.diferencia_porcentual))
        elif metric == "ingreso_stripe":
            values.append(r.ingreso_stripe)
        elif metric == "ingreso_quickbooks":
            values.append(r.ingreso_quickbooks)
        else:
            raise ValueError(f"Métrica no soportada: {metric}")
    
    # Calcular regresión lineal simple
    n = len(values)
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(values) / n
    
    numerator = sum((x[i] - x_mean) * (values[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    
    if denominator == 0:
        slope = 0.0
    else:
        slope = numerator / denominator
    
    # Calcular R²
    y_pred = [y_mean + slope * (x[i] - x_mean) for i in range(n)]
    ss_res = sum((values[i] - y_pred[i]) ** 2 for i in range(n))
    ss_tot = sum((values[i] - y_mean) ** 2 for i in range(n))
    
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    
    # Determinar dirección
    if abs(slope) < 0.001:
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"
    
    return {
        "direction": direction,
        "slope": slope,
        "r_squared": r_squared,
        "data_points": n,
        "first_value": values[0],
        "last_value": values[-1],
        "change": values[-1] - values[0],
        "change_percent": ((values[-1] - values[0]) / values[0] * 100) if values[0] > 0 else 0.0
    }


def reconcile_periods(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    tolerance: float = 1.0
) -> Dict[str, Any]:
    """
    Realiza una reconciliación completa de períodos analizando discrepancias.
    
    Args:
        results: Lista de resultados a reconciliar
        tolerance: Tolerancia para considerar una diferencia como aceptable (default: $1.0)
    
    Returns:
        Dict con reporte de reconciliación detallado
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> reconciliacion = reconcile_periods(resultados)
        >>> print(f"Períodos reconciliados: {reconciliacion['reconciliados']}")
    """
    if not results:
        return {
            "total_periodos": 0,
            "reconciliados": 0,
            "no_reconciliados": 0,
            "total_diferencia": 0.0,
            "periodos_con_discrepancias": []
        }
    
    # Normalizar
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    reconciliados = 0
    no_reconciliados = 0
    total_diferencia = 0.0
    periodos_con_discrepancias = []
    
    for result in normalized:
        diff_abs = abs(result.diferencia)
        total_diferencia += diff_abs
        
        if diff_abs <= tolerance:
            reconciliados += 1
        else:
            no_reconciliados += 1
            periodos_con_discrepancias.append({
                "periodo": f"{result.fecha_inicio} - {result.fecha_fin}",
                "diferencia": result.diferencia,
                "diferencia_absoluta": diff_abs,
                "diferencia_porcentual": result.diferencia_porcentual,
                "ingreso_stripe": result.ingreso_stripe,
                "ingreso_quickbooks": result.ingreso_quickbooks,
                "estado": result.estado
            })
    
    return {
        "total_periodos": len(normalized),
        "reconciliados": reconciliados,
        "no_reconciliados": no_reconciliados,
        "tasa_reconciliacion": (reconciliados / len(normalized) * 100) if normalized else 0.0,
        "total_diferencia": total_diferencia,
        "promedio_diferencia": total_diferencia / len(normalized) if normalized else 0.0,
        "periodos_con_discrepancias": periodos_con_discrepancias,
        "tolerance_usado": tolerance
    }


def verify_reconciliation(
    ingreso_stripe: float,
    ingreso_quickbooks: float,
    diferencia_reportada: float,
    umbral: float = 100.0
) -> Dict[str, Any]:
    """
    Verifica que una reconciliación sea matemáticamente correcta.
    
    Args:
        ingreso_stripe: Ingreso reportado de Stripe
        ingreso_quickbooks: Ingreso reportado de QuickBooks
        diferencia_reportada: Diferencia reportada
        umbral: Umbral para alertas
    
    Returns:
        Dict con resultado de verificación
    
    Example:
        >>> verificacion = verify_reconciliation(1000.0, 950.0, 50.0, umbral=100.0)
        >>> assert verificacion['es_correcta']
    """
    diferencia_calculada = ingreso_stripe - ingreso_quickbooks
    diferencia_abs_calculada = abs(diferencia_calculada)
    diferencia_abs_reportada = abs(diferencia_reportada)
    
    # Verificar que la diferencia calculada coincida con la reportada
    diferencia_coincide = abs(diferencia_calculada - diferencia_reportada) < 0.01
    
    # Verificar que la diferencia absoluta coincida
    diferencia_abs_coincide = abs(diferencia_abs_calculada - diferencia_abs_reportada) < 0.01
    
    # Determinar estado esperado
    estado_esperado = "Ok" if diferencia_abs_calculada <= umbral else "Alerta"
    
    return {
        "es_correcta": diferencia_coincide and diferencia_abs_coincide,
        "ingreso_stripe": ingreso_stripe,
        "ingreso_quickbooks": ingreso_quickbooks,
        "diferencia_calculada": diferencia_calculada,
        "diferencia_reportada": diferencia_reportada,
        "diferencia_coincide": diferencia_coincide,
        "diferencia_abs_calculada": diferencia_abs_calculada,
        "diferencia_abs_reportada": diferencia_abs_reportada,
        "diferencia_abs_coincide": diferencia_abs_coincide,
        "estado_esperado": estado_esperado,
        "excede_umbral": diferencia_abs_calculada > umbral,
        "umbral_usado": umbral
    }


def find_missing_periods(
    expected_periods: List[Dict[str, str]],
    actual_results: List[Union[ComparisonResult, ComparisonResultDict]]
) -> List[Dict[str, str]]:
    """
    Encuentra períodos que se esperaban pero no están en los resultados.
    
    Args:
        expected_periods: Lista de períodos esperados
        actual_results: Lista de resultados obtenidos
    
    Returns:
        Lista de períodos faltantes
    
    Example:
        >>> periodos_esperados = create_comparison_periods("2024-01-01", "2024-12-31", "month")
        >>> periodos_faltantes = find_missing_periods(periodos_esperados, resultados)
    """
    if not expected_periods:
        return []
    
    # Normalizar resultados
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in actual_results
    ]
    
    # Crear set de períodos presentes
    periodos_presentes = set()
    for result in normalized:
        periodo_key = f"{result.fecha_inicio}|{result.fecha_fin}"
        periodos_presentes.add(periodo_key)
    
    # Encontrar faltantes
    faltantes = []
    for periodo in expected_periods:
        periodo_key = f"{periodo['fecha_inicio']}|{periodo['fecha_fin']}"
        if periodo_key not in periodos_presentes:
            faltantes.append(periodo)
    
    return faltantes


def generate_reconciliation_report(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    format: str = "text"
) -> str:
    """
    Genera un reporte detallado de reconciliación.
    
    Args:
        results: Lista de resultados
        format: Formato del reporte ("text", "json", "html")
    
    Returns:
        Reporte en el formato especificado
    
    Example:
        >>> resultados = [result1, result2, result3]
        >>> reporte = generate_reconciliation_report(resultados, format="html")
    """
    if not results:
        return "No hay resultados para reportar"
    
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    reconciliacion = reconcile_periods(normalized)
    resumen = summarize_results(normalized)
    
    if format == "json":
        return json.dumps({
            "reconciliacion": reconciliacion,
            "resumen": resumen,
            "resultados": [r.to_dict() for r in normalized]
        }, default=str, indent=2)
    
    elif format == "html":
        html = f"""
        <html>
        <head><title>Reporte de Reconciliación</title></head>
        <body>
            <h1>Reporte de Reconciliación de Ingresos</h1>
            
            <h2>Resumen</h2>
            <ul>
                <li>Total de períodos: {reconciliacion['total_periodos']}</li>
                <li>Reconciliados: {reconciliacion['reconciliados']} ({reconciliacion['tasa_reconciliacion']:.2f}%)</li>
                <li>No reconciliados: {reconciliacion['no_reconciliados']}</li>
                <li>Total diferencia: ${reconciliacion['total_diferencia']:,.2f}</li>
                <li>Promedio diferencia: ${reconciliacion['promedio_diferencia']:,.2f}</li>
            </ul>
            
            <h2>Períodos con Discrepancias</h2>
            <table border="1" cellpadding="5">
                <tr>
                    <th>Período</th>
                    <th>Diferencia</th>
                    <th>Diferencia %</th>
                    <th>Ingreso Stripe</th>
                    <th>Ingreso QuickBooks</th>
                    <th>Estado</th>
                </tr>
        """
        
        for discrepancia in reconciliacion['periodos_con_discrepancias'][:20]:  # Limitar a 20
            html += f"""
                <tr>
                    <td>{discrepancia['periodo']}</td>
                    <td>${discrepancia['diferencia']:,.2f}</td>
                    <td>{discrepancia['diferencia_porcentual']:.2f}%</td>
                    <td>${discrepancia['ingreso_stripe']:,.2f}</td>
                    <td>${discrepancia['ingreso_quickbooks']:,.2f}</td>
                    <td>{discrepancia['estado']}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        return html
    
    else:  # text
        lines = [
            "=" * 80,
            "REPORTE DE RECONCILIACIÓN DE INGRESOS",
            "=" * 80,
            "",
            "RESUMEN:",
            f"  Total de períodos: {reconciliacion['total_periodos']}",
            f"  Reconciliados: {reconciliacion['reconciliados']} ({reconciliacion['tasa_reconciliacion']:.2f}%)",
            f"  No reconciliados: {reconciliacion['no_reconciliados']}",
            f"  Total diferencia: ${reconciliacion['total_diferencia']:,.2f}",
            f"  Promedio diferencia: ${reconciliacion['promedio_diferencia']:,.2f}",
            "",
            "PERÍODOS CON DISCREPANCIAS:",
            "-" * 80
        ]
        
        for discrepancia in reconciliacion['periodos_con_discrepancias']:
            lines.append(
                f"{discrepancia['periodo']}: "
                f"Diferencia=${discrepancia['diferencia']:,.2f} "
                f"({discrepancia['diferencia_porcentual']:.2f}%) | "
                f"Stripe=${discrepancia['ingreso_stripe']:,.2f} | "
                f"QB=${discrepancia['ingreso_quickbooks']:,.2f} | "
                f"Estado={discrepancia['estado']}"
            )
        
        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


def check_balance_consistency(
    results: List[Union[ComparisonResult, ComparisonResultDict]]
) -> Dict[str, Any]:
    """
    Verifica la consistencia del balance a lo largo de múltiples períodos.
    
    Args:
        results: Lista de resultados ordenados por fecha
    
    Returns:
        Dict con análisis de consistencia de balance
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> consistencia = check_balance_consistency(resultados)
        >>> print(f"Inconsistencias encontradas: {len(consistencia['inconsistencias'])}")
    """
    if not results or len(results) < 2:
        return {
            "es_consistente": True,
            "inconsistencias": [],
            "total_verificaciones": 0
        }
    
    # Normalizar y ordenar
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    normalized.sort(key=lambda x: x.fecha_inicio)
    
    inconsistencias = []
    
    # Verificar cada resultado
    for i, result in enumerate(normalized):
        es_valido, errores = validate_result_consistency(result)
        if not es_valido:
            inconsistencias.append({
                "indice": i,
                "periodo": f"{result.fecha_inicio} - {result.fecha_fin}",
                "errores": errores
            })
    
    # Verificar consistencia entre períodos consecutivos
    for i in range(len(normalized) - 1):
        r1 = normalized[i]
        r2 = normalized[i + 1]
        
        # Verificar que las fechas sean consecutivas (no hay gaps)
        try:
            fin_r1 = datetime.strptime(r1.fecha_fin, "%Y-%m-%d")
            inicio_r2 = datetime.strptime(r2.fecha_inicio, "%Y-%m-%d")
            
            gap_days = (inicio_r2 - fin_r1).days
            if gap_days > 1:
                inconsistencias.append({
                    "tipo": "gap_temporal",
                    "periodo1": f"{r1.fecha_inicio} - {r1.fecha_fin}",
                    "periodo2": f"{r2.fecha_inicio} - {r2.fecha_fin}",
                    "gap_dias": gap_days,
                    "mensaje": f"Gap de {gap_days} días entre períodos consecutivos"
                })
        except ValueError:
            pass
    
    return {
        "es_consistente": len(inconsistencias) == 0,
        "inconsistencias": inconsistencias,
        "total_verificaciones": len(normalized),
        "total_periodos": len(normalized),
        "periodos_con_errores": len([inc for inc in inconsistencias if "indice" in inc])
    }


def aggregate_metrics(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    group_by: Optional[str] = None
) -> Dict[str, Any]:
    """
    Agrega métricas de resultados para dashboards y reporting.
    
    Args:
        results: Lista de resultados
        group_by: Agrupar por ("day", "week", "month", "quarter", "year") o None
    
    Returns:
        Dict con métricas agregadas
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> metricas = aggregate_metrics(resultados, group_by="month")
        >>> print(f"Total ingresos Stripe: ${metricas['total_ingreso_stripe']:,.2f}")
    """
    if not results:
        return {
            "total_periodos": 0,
            "total_ingreso_stripe": 0.0,
            "total_ingreso_quickbooks": 0.0,
            "total_diferencia": 0.0,
            "promedio_diferencia": 0.0,
            "ok_count": 0,
            "alerta_count": 0,
            "error_count": 0
        }
    
    # Normalizar
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    # Agrupar si se solicita
    if group_by:
        grouped = group_results_by_period(normalized, group_by=group_by)
        metricas_por_periodo = {}
        
        for periodo, resultados_periodo in grouped.items():
            metricas_por_periodo[periodo] = {
                "periodos": len(resultados_periodo),
                "total_ingreso_stripe": sum(r.ingreso_stripe for r in resultados_periodo),
                "total_ingreso_quickbooks": sum(r.ingreso_quickbooks for r in resultados_periodo),
                "total_diferencia": sum(r.diferencia for r in resultados_periodo),
                "ok_count": sum(1 for r in resultados_periodo if r.is_ok),
                "alerta_count": sum(1 for r in resultados_periodo if r.is_alerta),
                "error_count": sum(1 for r in resultados_periodo if r.is_error)
            }
        
        return {
            "total_periodos": len(normalized),
            "periodos_agrupados": len(grouped),
            "group_by": group_by,
            "metricas_por_periodo": metricas_por_periodo,
            "totales": {
                "total_ingreso_stripe": sum(r.ingreso_stripe for r in normalized),
                "total_ingreso_quickbooks": sum(r.ingreso_quickbooks for r in normalized),
                "total_diferencia": sum(r.diferencia for r in normalized),
                "ok_count": sum(1 for r in normalized if r.is_ok),
                "alerta_count": sum(1 for r in normalized if r.is_alerta),
                "error_count": sum(1 for r in normalized if r.is_error)
            }
        }
    
    # Métricas totales sin agrupación
    diferencias = [abs(r.diferencia) for r in normalized if not r.is_error]
    
    return {
        "total_periodos": len(normalized),
        "total_ingreso_stripe": sum(r.ingreso_stripe for r in normalized),
        "total_ingreso_quickbooks": sum(r.ingreso_quickbooks for r in normalized),
        "total_diferencia": sum(r.diferencia for r in normalized),
        "promedio_diferencia": sum(diferencias) / len(diferencias) if diferencias else 0.0,
        "max_diferencia": max(diferencias) if diferencias else 0.0,
        "min_diferencia": min(diferencias) if diferencias else 0.0,
        "ok_count": sum(1 for r in normalized if r.is_ok),
        "alerta_count": sum(1 for r in normalized if r.is_alerta),
        "error_count": sum(1 for r in normalized if r.is_error),
        "tasa_ok": (sum(1 for r in normalized if r.is_ok) / len(normalized) * 100) if normalized else 0.0,
        "tasa_alertas": (sum(1 for r in normalized if r.is_alerta) / len(normalized) * 100) if normalized else 0.0,
        "tasa_errores": (sum(1 for r in normalized if r.is_error) / len(normalized) * 100) if normalized else 0.0
    }


def generate_dashboard_data(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    window_days: int = 30
) -> Dict[str, Any]:
    """
    Genera datos agregados para un dashboard de monitoreo.
    
    Args:
        results: Lista de resultados
        window_days: Ventana de días para filtrar resultados recientes
    
    Returns:
        Dict con datos estructurados para dashboard
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> dashboard_data = generate_dashboard_data(resultados, window_days=30)
        >>> # Usar para visualización en dashboard
    """
    if not results:
        return {
            "summary": {},
            "trends": {},
            "alerts": [],
            "periods": []
        }
    
    # Normalizar y filtrar por ventana
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    cutoff_date = (datetime.now() - timedelta(days=window_days)).strftime("%Y-%m-%d")
    recent_results = [r for r in normalized if r.fecha_fin >= cutoff_date]
    
    # Resumen
    summary = summarize_results(recent_results)
    
    # Tendencias
    trends = calculate_trend(recent_results, metric="diferencia")
    
    # Alertas recientes
    alerts = [
        {
            "periodo": f"{r.fecha_inicio} - {r.fecha_fin}",
            "diferencia": r.diferencia,
            "diferencia_porcentual": r.diferencia_porcentual,
            "ingreso_stripe": r.ingreso_stripe,
            "ingreso_quickbooks": r.ingreso_quickbooks,
            "timestamp": r.timestamp
        }
        for r in recent_results if r.is_alerta
    ]
    alerts.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    # Agrupar por período
    by_period = group_results_by_period(recent_results, group_by="month")
    
    periods_data = []
    for periodo, resultados_periodo in sorted(by_period.items()):
        periods_data.append({
            "periodo": periodo,
            "count": len(resultados_periodo),
            "ok": sum(1 for r in resultados_periodo if r.is_ok),
            "alertas": sum(1 for r in resultados_periodo if r.is_alerta),
            "errores": sum(1 for r in resultados_periodo if r.is_error),
            "promedio_diferencia": sum(abs(r.diferencia) for r in resultados_periodo) / len(resultados_periodo) if resultados_periodo else 0.0
        })
    
    return {
        "summary": summary,
        "trends": trends,
        "alerts": alerts[:20],  # Top 20 más recientes
        "periods": periods_data,
        "window_days": window_days,
        "total_results": len(recent_results),
        "timestamp": time.time()
    }


def optimize_threshold(
    historical_results: List[Union[ComparisonResult, ComparisonResultDict]],
    target_alert_rate: float = 5.0
) -> Dict[str, Any]:
    """
    Optimiza el umbral basándose en resultados históricos para alcanzar una tasa de alertas objetivo.
    
    Args:
        historical_results: Resultados históricos
        target_alert_rate: Tasa de alertas objetivo en porcentaje (default: 5.0%)
    
    Returns:
        Dict con umbral recomendado y análisis
    
    Example:
        >>> resultados_historicos = [result1, result2, result3, ...]
        >>> optimizacion = optimize_threshold(resultados_historicos, target_alert_rate=5.0)
        >>> umbral_recomendado = optimizacion['umbral_recomendado']
    """
    if not historical_results or len(historical_results) < 10:
        return {
            "umbral_recomendado": 100.0,
            "razon": "insufficient_data",
            "data_points": len(historical_results) if historical_results else 0
        }
    
    # Normalizar
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in historical_results
    ]
    
    # Extraer diferencias absolutas
    diferencias = [abs(r.diferencia) for r in normalized if not r.is_error]
    diferencias.sort()
    
    if not diferencias:
        return {
            "umbral_recomendado": 100.0,
            "razon": "no_valid_differences",
            "data_points": len(normalized)
        }
    
    # Encontrar umbral que dé la tasa de alertas objetivo
    target_count = int(len(diferencias) * (target_alert_rate / 100.0))
    
    if target_count >= len(diferencias):
        umbral_recomendado = diferencias[-1] if diferencias else 100.0
    elif target_count <= 0:
        umbral_recomendado = diferencias[0] if diferencias else 100.0
    else:
        # Usar percentil para encontrar el umbral
        umbral_recomendado = diferencias[-(target_count + 1)] if target_count < len(diferencias) else diferencias[-1]
    
    # Calcular estadísticas
    current_alert_rate = (sum(1 for r in normalized if r.is_alerta) / len(normalized) * 100) if normalized else 0.0
    
    # Proyectar tasa con nuevo umbral
    projected_alerts = sum(1 for diff in diferencias if diff > umbral_recomendado)
    projected_alert_rate = (projected_alerts / len(diferencias) * 100) if diferencias else 0.0
    
    return {
        "umbral_recomendado": round(umbral_recomendado, 2),
        "umbral_actual_promedio": sum(r.umbral for r in normalized) / len(normalized) if normalized else 100.0,
        "tasa_alertas_actual": current_alert_rate,
        "tasa_alertas_proyectada": projected_alert_rate,
        "tasa_alertas_objetivo": target_alert_rate,
        "diferencia_vs_objetivo": projected_alert_rate - target_alert_rate,
        "data_points": len(diferencias),
        "percentil_90": diferencias[int(len(diferencias) * 0.9)] if len(diferencias) > 0 else 0.0,
        "percentil_95": diferencias[int(len(diferencias) * 0.95)] if len(diferencias) > 0 else 0.0,
        "percentil_99": diferencias[int(len(diferencias) * 0.99)] if len(diferencias) > 0 else 0.0
    }


def audit_comparison_history(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    lookback_days: int = 90
) -> Dict[str, Any]:
    """
    Realiza una auditoría completa del historial de comparaciones.
    
    Args:
        results: Lista de resultados históricos
        lookback_days: Días hacia atrás para analizar (default: 90)
    
    Returns:
        Dict con reporte de auditoría completo
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> auditoria = audit_comparison_history(resultados, lookback_days=90)
        >>> print(f"Periodos auditados: {auditoria['total_periodos']}")
    """
    if not results:
        return {
            "total_periodos": 0,
            "periodos_auditados": 0,
            "hallazgos": [],
            "resumen": {}
        }
    
    # Normalizar y filtrar
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    cutoff_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")
    recent_results = [r for r in normalized if r.fecha_fin >= cutoff_date]
    
    hallazgos = []
    
    # Verificar consistencia de cada resultado
    for r in recent_results:
        es_valido, errores = validate_result_consistency(r)
        if not es_valido:
            hallazgos.append({
                "tipo": "inconsistencia_interna",
                "periodo": f"{r.fecha_inicio} - {r.fecha_fin}",
                "errores": errores,
                "severidad": "alta"
            })
    
    # Verificar gaps temporales
    recent_results.sort(key=lambda x: x.fecha_inicio)
    for i in range(len(recent_results) - 1):
        r1 = recent_results[i]
        r2 = recent_results[i + 1]
        
        try:
            fin_r1 = datetime.strptime(r1.fecha_fin, "%Y-%m-%d")
            inicio_r2 = datetime.strptime(r2.fecha_inicio, "%Y-%m-%d")
            
            gap_days = (inicio_r2 - fin_r1).days
            if gap_days > 1:
                hallazgos.append({
                    "tipo": "gap_temporal",
                    "periodo1": f"{r1.fecha_inicio} - {r1.fecha_fin}",
                    "periodo2": f"{r2.fecha_inicio} - {r2.fecha_fin}",
                    "gap_dias": gap_days,
                    "severidad": "media"
                })
        except ValueError:
            pass
    
    # Detectar anomalías
    anomalias = detect_anomalies(recent_results)
    for anomalia in anomalias:
        hallazgos.append({
            "tipo": "anomalia_estadistica",
            "periodo": f"{anomalia['result'].fecha_inicio} - {anomalia['result'].fecha_fin}",
            "z_score": anomalia['z_score'],
            "diferencia": anomalia['difference'],
            "severidad": "alta" if anomalia['z_score'] > 3.0 else "media"
        })
    
    # Resumen
    resumen = summarize_results(recent_results)
    reconciliacion = reconcile_periods(recent_results)
    consistencia = check_balance_consistency(recent_results)
    
    return {
        "total_periodos": len(normalized),
        "periodos_auditados": len(recent_results),
        "lookback_days": lookback_days,
        "hallazgos": hallazgos,
        "total_hallazgos": len(hallazgos),
        "hallazgos_altos": len([h for h in hallazgos if h.get("severidad") == "alta"]),
        "hallazgos_medios": len([h for h in hallazgos if h.get("severidad") == "media"]),
        "resumen": resumen,
        "reconciliacion": {
            "tasa_reconciliacion": reconciliacion.get("tasa_reconciliacion", 0.0),
            "periodos_no_reconciliados": reconciliacion.get("no_reconciliados", 0)
        },
        "consistencia": {
            "es_consistente": consistencia.get("es_consistente", True),
            "inconsistencias": len(consistencia.get("inconsistencias", []))
        },
        "timestamp": time.time()
    }


def _get_circuit_breaker_state(operation: str) -> Dict[str, Any]:
    """
    Obtiene el estado actual del circuit breaker para una operación.
    
    Args:
        operation: Nombre de la operación
    
    Returns:
        Dict con el estado del circuit breaker
    """
    if operation not in _circuit_breaker_state:
        return {
            "state": "closed",
            "failures": 0,
            "last_failure": None
        }
    return _circuit_breaker_state[operation].copy()


def perform_system_health_check(
    test_period: Optional[Tuple[str, str]] = None,
    umbral_test: float = 100.0
) -> Dict[str, Any]:
    """
    Realiza un health check completo del sistema de comparación de ingresos.
    
    Args:
        test_period: Periodo de prueba opcional (fecha_inicio, fecha_fin)
        umbral_test: Umbral para prueba opcional
    
    Returns:
        Dict con estado de salud de todos los componentes
    
    Example:
        >>> health = perform_system_health_check()
        >>> if health['status'] == 'healthy':
        ...     print("Sistema operativo")
        ... else:
        ...     print(f"Issues: {health['issues']}")
    """
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "components": {},
        "issues": [],
        "recommendations": []
    }
    
    # Health check de configuración
    try:
        config = get_global_config()
        health_status["components"]["config"] = {
            "status": "ok",
            "parallel_enabled": config.enable_parallel,
            "circuit_breaker_enabled": config.enable_circuit_breaker
        }
    except Exception as e:
        health_status["components"]["config"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["issues"].append(f"Config error: {e}")
        health_status["status"] = "degraded"
    
    # Health check de conectividad
    try:
        with RevenueComparisonClient() as client:
            connectivity = client.health_check()
            health_status["components"]["connectivity"] = connectivity
            
            if not connectivity.get("stripe", {}).get("ok", False):
                health_status["issues"].append("Stripe API no responde")
                health_status["status"] = "degraded"
            
            if not connectivity.get("quickbooks", {}).get("ok", False):
                health_status["issues"].append("QuickBooks API no responde")
                health_status["status"] = "degraded"
    except Exception as e:
        health_status["components"]["connectivity"] = {
            "status": "error",
            "error": str(e)
        }
        health_status["issues"].append(f"Connectivity check failed: {e}")
        health_status["status"] = "unhealthy"
    
    # Health check de base de datos
    if get_conn:
        try:
            with get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'stripe_quickbooks_revenue_comparisons'
                        )
                    """)
                    table_exists = cur.fetchone()[0]
                    health_status["components"]["database"] = {
                        "status": "ok" if table_exists else "warning",
                        "table_exists": table_exists
                    }
                    
                    if not table_exists:
                        health_status["issues"].append("Tabla de comparaciones no existe")
                        health_status["recommendations"].append("Ejecutar persistir_comparacion para crear la tabla")
        except Exception as e:
            health_status["components"]["database"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["issues"].append(f"Database check failed: {e}")
            health_status["status"] = "degraded"
    else:
        health_status["components"]["database"] = {
            "status": "not_available",
            "reason": "get_conn not available"
        }
    
    # Health check de caché
    try:
        cache_size = len(_account_cache) if _account_cache else 0
        health_status["components"]["cache"] = {
            "status": "ok",
            "size": cache_size,
            "max_size": _account_cache.maxsize if _account_cache else 0
        }
    except Exception as e:
        health_status["components"]["cache"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Health check de circuit breaker
    try:
        circuit_breaker_status = {}
        for operation in ["stripe_api", "quickbooks_api"]:
            state = _get_circuit_breaker_state(operation)
            circuit_breaker_status[operation] = {
                "state": state.get("state", "closed"),
                "failures": state.get("failures", 0),
                "last_failure": state.get("last_failure")
            }
        
        health_status["components"]["circuit_breaker"] = circuit_breaker_status
    except Exception as e:
        health_status["components"]["circuit_breaker"] = {
            "status": "error",
            "error": str(e)
        }
    
    # Test de comparación si se proporciona período
    if test_period:
        try:
            fecha_inicio, fecha_fin = test_period
            test_result = comparar_ingresos_stripe_quickbooks(
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                umbral=umbral_test
            )
            
            health_status["components"]["test_comparison"] = {
                "status": "ok" if not test_result.get("error") else "error",
                "result": test_result.get("estado"),
                "diferencia": test_result.get("diferencia", 0.0)
            }
            
            if test_result.get("error"):
                health_status["issues"].append(f"Test comparison failed: {test_result.get('error')}")
                health_status["status"] = "degraded"
        except Exception as e:
            health_status["components"]["test_comparison"] = {
                "status": "error",
                "error": str(e)
            }
            health_status["issues"].append(f"Test comparison exception: {e}")
            health_status["status"] = "degraded"
    
    # Determinar status final
    if len([issue for issue in health_status["issues"] if "failed" in issue.lower()]) > 0:
        health_status["status"] = "unhealthy"
    
    return health_status


def auto_fix_common_issues(
    results: List[Union[ComparisonResult, ComparisonResultDict]],
    dry_run: bool = True
) -> Dict[str, Any]:
    """
    Intenta corregir automáticamente problemas comunes detectados en resultados.
    
    Args:
        results: Lista de resultados con posibles problemas
        dry_run: Si True, solo reporta problemas sin corregirlos
    
    Returns:
        Dict con acciones realizadas y recomendaciones
    
    Example:
        >>> resultados = [result1, result2, result3, ...]
        >>> fixes = auto_fix_common_issues(resultados, dry_run=False)
        >>> print(f"Problemas corregidos: {fixes['fixed_count']}")
    """
    fixes_applied = {
        "dry_run": dry_run,
        "issues_detected": [],
        "fixes_applied": [],
        "recommendations": [],
        "fixed_count": 0,
        "timestamp": time.time()
    }
    
    if not results:
        return fixes_applied
    
    # Normalizar
    normalized = [
        ComparisonResult.from_dict(r) if isinstance(r, dict) else r
        for r in results
    ]
    
    # Detectar y corregir gaps temporales
    missing_periods = find_missing_periods(normalized)
    if missing_periods:
        fixes_applied["issues_detected"].append({
            "tipo": "missing_periods",
            "count": len(missing_periods),
            "periods": missing_periods
        })
        
        if not dry_run:
            fixes_applied["recommendations"].append(
                f"Ejecutar comparación para {len(missing_periods)} períodos faltantes"
            )
    
    # Detectar inconsistencias internas
    for i, result in enumerate(normalized):
        es_valido, errores = validate_result_consistency(result)
        if not es_valido:
            fixes_applied["issues_detected"].append({
                "tipo": "inconsistency",
                "indice": i,
                "periodo": f"{result.fecha_inicio} - {result.fecha_fin}",
                "errores": errores
            })
            
            if not dry_run:
                # Intentar recalcular diferencias si es posible
                if "diferencia" in str(errores).lower():
                    diferencia_calculada = result.ingreso_stripe - result.ingreso_quickbooks
                    if abs(diferencia_calculada - result.diferencia) > 0.01:
                        fixes_applied["fixes_applied"].append({
                            "tipo": "recalcular_diferencia",
                            "indice": i,
                            "diferencia_anterior": result.diferencia,
                            "diferencia_calculada": diferencia_calculada
                        })
                        fixes_applied["fixed_count"] += 1
    
    # Detectar umbrales subóptimos
    alert_rate = (sum(1 for r in normalized if r.is_alerta) / len(normalized) * 100) if normalized else 0.0
    
    if alert_rate > 20.0:
        fixes_applied["issues_detected"].append({
            "tipo": "high_alert_rate",
            "tasa_actual": alert_rate,
            "umbral_recomendado": optimize_threshold(normalized, target_alert_rate=5.0).get("umbral_recomendado", 100.0)
        })
        
        fixes_applied["recommendations"].append(
            f"Tasa de alertas muy alta ({alert_rate:.1f}%). Considerar optimizar umbral."
        )
    elif alert_rate < 1.0:
        fixes_applied["issues_detected"].append({
            "tipo": "low_alert_rate",
            "tasa_actual": alert_rate
        })
        
        fixes_applied["recommendations"].append(
            "Tasa de alertas muy baja. Posible que el umbral sea muy alto."
        )
    
    # Detectar tendencias preocupantes
    trends = calculate_trend(normalized, metric="diferencia")
    if trends.get("slope", 0) > 10.0:
        fixes_applied["issues_detected"].append({
            "tipo": "increasing_trend",
            "slope": trends.get("slope"),
            "interpretation": trends.get("interpretation")
        })
        
        fixes_applied["recommendations"].append(
            "Tendencia creciente en diferencias detectada. Investigar causas."
        )
    
    return fixes_applied
