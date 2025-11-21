# Funcionalidades Adicionales - Ads Reporting

Este documento describe las funcionalidades adicionales implementadas en los DAGs de reporting de ads.

## 🛠️ Módulo de Utilidades Compartidas

### `ads_reporting_utils.py`

Módulo centralizado con utilidades compartidas para todos los DAGs de ads reporting.

#### Health Checks

**1. `check_api_credentials()`**
- Verifica que todas las credenciales necesarias estén configuradas
- Soporta múltiples plataformas (facebook, tiktok, google)
- Valida campos requeridos dinámicamente

**2. `check_database_connection()`**
- Verifica conectividad con PostgreSQL
- Prueba conexión real antes de ejecutar el DAG
- Manejo de errores detallado

**3. `check_table_exists()`**
- Verifica existencia de tablas en la base de datos
- Útil para validar esquema antes de insertar datos
- Retorna warning si no existe (se creará automáticamente)

#### Data Quality Checks

**1. `check_data_quality_campaigns()`**
- Valida calidad de datos extraídos
- Verifica campos requeridos
- Detecta valores negativos o inválidos
- Calcula métricas de calidad

**2. `check_data_freshness()`**
- Verifica que los datos estén actualizados
- Detecta retrasos en la actualización
- Configurable con días esperados de retraso

#### Utilidades de Validación

**1. `validate_date_range()`**
- Valida formato de fechas (YYYY-MM-DD)
- Verifica que start < stop
- Limita rango máximo de días
- Previene fechas futuras inválidas

#### Utilidades de Tracking

**1. `track_operation()`**
- Context manager para trackear operaciones
- Métricas automáticas de duración y éxito/error
- Tags por plataforma y operación

#### Agregación de Checks

**1. `aggregate_health_checks()`**
- Combina múltiples health checks
- Genera resultado agregado con status general
- Detalles de todos los checks individuales

**2. `aggregate_data_quality_checks()`**
- Agrega múltiples DQ checks
- Calcula tasa de éxito
- Lista todos los issues encontrados

## 🔧 Mejoras Aplicadas a TikTok Ads

### 1. Manejo de Errores Robusto
- Excepciones personalizadas: `TikTokAdsError`, `TikTokAdsAuthError`, `TikTokAdsAPIError`, `TikTokAdsRateLimitError`
- Retry automático con exponential backoff
- Manejo específico de rate limiting

### 2. Validación de Configuración
- Método `validate()` en `TikTokAdsConfig`
- Validación temprana de credenciales
- Mensajes de error claros

### 3. Sesiones HTTP Reutilizables
- `_create_tiktok_session()` con retry strategy
- Mejor rendimiento y manejo de conexiones
- Timeouts configurables

### 4. Métricas y Telemetría
- Tracking estructurado con Airflow Stats
- Métricas de duración, éxito y errores
- Context manager `_track_metric()`

### 5. Retry Logic Mejorado
- Detección de errores de TikTok API
- Manejo de códigos de error específicos
- Respeto de headers de rate limiting

## 📊 Estructura de Health Checks

### Ejemplo de Uso

```python
from ads_reporting_utils import (
    check_api_credentials,
    check_database_connection,
    aggregate_health_checks
)

@task
def health_check_task(**context):
    checks = []
    
    # Verificar credenciales
    checks.append(check_api_credentials(
        "tiktok",
        access_token=config.access_token,
        account_id=config.advertiser_id
    ))
    
    # Verificar base de datos
    checks.append(check_database_connection(config.postgres_conn_id))
    
    # Agregar resultados
    result = aggregate_health_checks(checks)
    
    if result.status == "error":
        raise ValueError(f"Health check failed: {result.message}")
    
    return result
```

## 🔍 Data Quality Checks

### Ejemplo de Uso

```python
from ads_reporting_utils import (
    check_data_quality_campaigns,
    check_data_freshness,
    aggregate_data_quality_checks
)

@task
def data_quality_check_task(campaign_data, **context):
    checks = []
    
    # Verificar calidad de datos
    checks.append(check_data_quality_campaigns(campaign_data, "tiktok"))
    
    # Verificar frescura de datos
    checks.append(check_data_freshness(
        "tiktok_ads_campaigns",
        date_column="date_start",
        expected_days_behind=1
    ))
    
    # Agregar resultados
    summary = aggregate_data_quality_checks(checks)
    
    if summary["failed"] > 0:
        logger.warning(f"Data quality issues found: {summary['all_issues']}")
    
    return summary
```

## 🎯 Beneficios de las Mejoras

### 1. Detección Temprana de Problemas
- Health checks antes de ejecutar extracciones costosas
- Validación de configuración al inicio
- Ahorro de tiempo y recursos

### 2. Calidad de Datos Garantizada
- Validaciones automáticas de datos extraídos
- Detección de anomalías y valores inválidos
- Métricas de calidad disponibles

### 3. Monitoreo Completo
- Métricas estructuradas para todas las operaciones
- Tracking de éxito/error con contexto
- Facilita debugging y análisis

### 4. Código Reutilizable
- Utilidades compartidas entre plataformas
- Consistencia en implementación
- Mantenimiento simplificado

## 📈 Próximas Mejoras Sugeridas

1. **Circuit Breakers Completos**
   - Implementación de circuit breakers por plataforma
   - Aislamiento de fallos
   - Recuperación automática

2. **Caché Inteligente**
   - Caché de requests para evitar duplicados
   - TTL configurable
   - Invalidación automática

3. **Batch Processing Optimizado**
   - Procesamiento en lotes para grandes volúmenes
   - Paralelización controlada
   - Progress tracking

4. **Alertas Automáticas**
   - Notificaciones cuando health checks fallan
   - Alertas de data quality issues
   - Integración con Slack/Email

5. **Análisis de Anomalías**
   - Detección automática de cambios significativos
   - Alertas de métricas fuera de rango
   - Análisis de tendencias

## 🔗 Integración con DAGs Existentes

Los DAGs mejorados pueden usar estas utilidades de dos formas:

1. **Importación directa**
```python
from ads_reporting_utils import check_api_credentials
```

2. **Como tasks de Airflow**
```python
@task
def health_check():
    return check_api_credentials("facebook", ...)
```

## 📝 Notas de Implementación

- Todas las utilidades son opcionales (graceful degradation)
- Logging estructurado en todas las funciones
- Type hints completos para mejor IDE support
- Documentación inline completa


