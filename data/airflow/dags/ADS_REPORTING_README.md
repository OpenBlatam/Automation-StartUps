# Ads Reporting - Documentación Completa

## 📋 Índice

1. [Arquitectura Modular](#arquitectura-modular)
2. [Módulos Disponibles](#módulos-disponibles)
3. [Guía Rápida](#guía-rápida)
4. [Ejemplos](#ejemplos)
5. [Configuración](#configuración)
6. [Mejores Prácticas](#mejores-prácticas)

## 🏗️ Arquitectura Modular

Sistema completamente modular con separación de responsabilidades:

```
ads_reporting/
├── base_client.py          # Cliente base con funcionalidades compartidas
├── facebook_client.py      # Cliente Facebook Ads
├── tiktok_client.py        # Cliente TikTok Ads
├── google_client.py        # Cliente Google Ads
├── extractors.py           # Extractores de datos
├── storage.py              # Almacenadores (PostgreSQL, S3)
├── processors.py           # Procesadores y transformaciones
├── validators.py           # Validadores de datos
├── cache.py                # Sistema de caché
├── config.py               # Configuración centralizada
├── decorators.py           # Decoradores útiles
├── helpers.py              # Funciones de utilidad
└── integration.py          # Funciones de integración de alto nivel
```

## 📦 Módulos Disponibles

### Clientes (`base_client.py`, `*_client.py`)

**BaseAdsClient**: Cliente base con:
- Retry logic automático
- Rate limiting
- Sesiones HTTP reutilizables
- Métricas y tracking

**Clientes específicos:**
- `FacebookAdsClient`: Facebook Ads API
- `TikTokAdsClient`: TikTok Ads API
- `GoogleAdsClient`: Google Ads API

### Extractores (`extractors.py`)

**BaseExtractor**: Extractor base abstracto

**Extractores implementados:**
- `FacebookExtractor`
- `TikTokExtractor`

**Funciones:**
- `extract_campaign_performance()`: Extracción de rendimiento
- `extract_audience_performance()`: Extracción por audiencia

### Almacenadores (`storage.py`)

**BaseStorage**: Almacenador base abstracto

**Implementaciones:**
- `PostgreSQLStorage`: PostgreSQL (implementado)
- `S3Storage`: Amazon S3 (placeholder)

**Factory:**
- `get_storage()`: Factory para obtener almacenador

### Procesadores (`processors.py`)

**Procesadores disponibles:**
- `CampaignProcessor`: Para datos de campañas
- `AudienceProcessor`: Para datos de audiencias
- `GeographicProcessor`: Para datos geográficos

**Funciones:**
- `normalize()`: Normalización de datos
- `calculate_metrics()`: Métricas agregadas
- `group_by_campaign()`, `group_by_date()`: Agrupación
- `filter_by_performance()`: Filtrado

### Validadores (`validators.py`)

**Validadores:**
- `SchemaValidator`: Validación de esquemas
- `ValueValidator`: Validación de valores
- `ConsistencyValidator`: Validación de consistencia
- `CompletenessValidator`: Validación de completitud

**Función principal:**
- `validate_campaign_data()`: Validación completa

### Caché (`cache.py`)

**AdsCache**: Sistema de caché con:
- TTL configurable
- Prevención de duplicados
- Estadísticas de uso

**Función:**
- `get_cache()`: Obtener instancia del caché

### Configuración (`config.py`)

**AdsReportingConfig**: Configuración centralizada desde variables de entorno

**Función:**
- `get_config()`: Obtener configuración global

### Decoradores (`decorators.py`)

**Decoradores disponibles:**
- `@with_retry`: Retry automático
- `@with_cache`: Caché automático
- `@with_validation`: Validación automática
- `@track_metrics`: Tracking de métricas
- `@handle_errors`: Manejo de errores
- `@timeout`: Timeout automático
- `@log_execution`: Logging automático

### Helpers (`helpers.py`)

**Funciones de utilidad:**
- Fechas: `normalize_date()`, `get_date_range()`
- Cálculos: `calculate_ctr()`, `calculate_cpc()`, `calculate_roas()`
- Formato: `format_currency()`, `format_percentage()`, `format_large_number()`
- Transformación: `normalize_platform_data()`, `merge_campaign_data()`
- Análisis: `detect_anomalies()`, `calculate_performance_score()`

### Integraciones (`integration.py`)

**Funciones de alto nivel:**
- `extract_and_store()`: Pipeline completo
- `compare_platforms()`: Comparación multi-plataforma
- `generate_performance_report()`: Reporte completo

## 🚀 Guía Rápida

### Instalación

```bash
pip install -r REQUIREMENTS_ads_reporting.txt
```

### Uso Básico

```python
from ads_reporting import (
    FacebookAdsClient, FacebookAdsConfig,
    FacebookExtractor,
    get_storage
)

# Configuración
config = FacebookAdsConfig(
    access_token=os.environ.get("FACEBOOK_ACCESS_TOKEN"),
    ad_account_id=os.environ.get("FACEBOOK_AD_ACCOUNT_ID")
)

# Extracción
with FacebookAdsClient(config) as client:
    extractor = FacebookExtractor(client)
    data = extractor.extract_campaign_performance(
        date_start="2024-01-01",
        date_stop="2024-01-31"
    )

# Almacenamiento
storage = get_storage("postgres")
storage.save_campaign_performance(data, "facebook_ads_performance")
```

### Uso Avanzado

```python
from ads_reporting.integration import extract_and_store
from ads_reporting.decorators import with_retry, track_metrics

@with_retry(max_attempts=3)
@track_metrics("facebook_extraction")
def extract_with_retry():
    return extract_and_store(
        client, extractor, storage,
        date_start, date_stop,
        use_cache=True,
        validate=True,
        process=True
    )
```

## 📝 Ejemplos

### Ejemplo 1: Extracción Simple

Ver `modular_dag_facebook.py`

### Ejemplo 2: Pipeline Completo

Ver `example_integrated_dag.py`

## ⚙️ Configuración

### Variables de Entorno Requeridas

**Facebook:**
```bash
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_AD_ACCOUNT_ID=act_123456789
```

**TikTok:**
```bash
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_ADVERTISER_ID=your_advertiser_id
```

**Google:**
```bash
GOOGLE_ADS_CUSTOMER_ID=123-456-7890
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
```

### Variables Opcionales

```bash
# Configuración global
ADS_CACHE_ENABLED=true
ADS_CACHE_TTL=300
ADS_ENABLE_VALIDATION=true
ADS_ENABLE_DQ_CHECKS=true

# Retry configuration
FACEBOOK_MAX_RETRIES=3
FACEBOOK_RETRY_BACKOFF=1.0
FACEBOOK_RATE_LIMIT_DELAY=0.5
```

## 📚 Documentación Completa

- `ADS_REPORTING_COMPLETE_GUIDE.md` - Guía completa
- `ADS_REPORTING_MODULAR_ARCHITECTURE.md` - Arquitectura detallada
- `ADS_REPORTING_MODULAR_SUMMARY.md` - Resumen ejecutivo
- `ADS_REPORTING_IMPROVEMENTS.md` - Mejoras implementadas
- `ADS_REPORTING_LIBRARIES.md` - Librerías y mejores prácticas
- `ADS_REPORTING_ADDITIONAL_FEATURES.md` - Funcionalidades adicionales
- `ADS_REPORTING_FINAL_IMPROVEMENTS.md` - Mejoras finales

## ✅ Estado del Proyecto

- ✅ **13 módulos modulares** implementados
- ✅ **Decoradores reutilizables** disponibles
- ✅ **Helpers de utilidad** completos
- ✅ **Funciones de integración** de alto nivel
- ✅ **Documentación completa** disponible
- ✅ **Ejemplos de uso** incluidos
- ✅ **Mejores prácticas** aplicadas

**Listo para producción** 🚀

