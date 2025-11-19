# Guía Completa - Ads Reporting Modular

## 🏗️ Arquitectura Completa

### Estructura de Módulos

```
ads_reporting/
├── __init__.py                    # Exports principales
├── base_client.py                 # Cliente base con funcionalidades compartidas
├── facebook_client.py              # Cliente Facebook Ads
├── tiktok_client.py                # Cliente TikTok Ads
├── google_client.py                # Cliente Google Ads
├── extractors.py                   # Extractores de datos
├── storage.py                      # Almacenadores (PostgreSQL, S3)
├── processors.py                   # Procesadores y transformaciones
├── validators.py                   # Validadores de datos
├── cache.py                        # Sistema de caché
├── config.py                       # Configuración centralizada
├── modular_dag_facebook.py         # DAG modular simple
└── example_integrated_dag.py      # DAG integrado completo

ads_reporting_utils.py              # Utilidades compartidas
```

## 📦 Módulos y Funcionalidades

### 1. Base Client (`base_client.py`)

**Responsabilidades:**
- ✅ Retry logic con exponential backoff
- ✅ Rate limiting automático
- ✅ Sesiones HTTP reutilizables
- ✅ Métricas y tracking
- ✅ Manejo de errores estandarizado
- ✅ Context managers

**Clases principales:**
- `BaseAdsClient`: Cliente base abstracto
- `APIConfig`: Configuración base
- Excepciones: `AdsAPIError`, `AdsAuthError`, `AdsRateLimitError`

### 2. Clientes Específicos

#### Facebook Client
- SDK oficial con fallback a REST
- Soporte completo de insights

#### TikTok Client
- API REST directa
- Manejo de reportes integrados

#### Google Client
- SDK oficial
- Soporte para queries GAQL

### 3. Extractores (`extractors.py`)

**Funcionalidades:**
- ✅ Normalización de datos entre plataformas
- ✅ Extracción estructurada
- ✅ Procesamiento básico

**Extractores disponibles:**
- `FacebookExtractor`
- `TikTokExtractor`
- `GoogleExtractor` (futuro)

### 4. Almacenadores (`storage.py`)

**Backends:**
- ✅ PostgreSQL (implementado)
- 🔄 S3 (placeholder)

**Características:**
- Creación automática de tablas
- Validación de esquemas
- Manejo de errores por registro

### 5. Procesadores (`processors.py`)

**Funcionalidades:**
- ✅ Normalización de datos
- ✅ Cálculo de métricas agregadas
- ✅ Agrupación (por campaña, fecha, etc.)
- ✅ Filtrado por rendimiento
- ✅ Identificación de bajo rendimiento

**Procesadores:**
- `CampaignProcessor`: Para datos de campañas
- `AudienceProcessor`: Para datos de audiencias
- `GeographicProcessor`: Para datos geográficos

### 6. Validadores (`validators.py`)

**Tipos de validación:**
- ✅ Schema validation (campos requeridos)
- ✅ Value validation (rangos, valores permitidos)
- ✅ Consistency validation (relaciones entre campos)
- ✅ Completeness validation (completitud de datos)

**Funciones:**
- `validate_campaign_data()`: Validación completa de campañas

### 7. Caché (`cache.py`)

**Características:**
- ✅ Caché en memoria con TTL
- ✅ Prevención de requests duplicados
- ✅ Estadísticas de uso
- ✅ Invalidación manual

**Uso:**
```python
cache = get_cache(maxsize=100, ttl=300)
data = cache.get("facebook", "campaign_performance", params)
if not data:
    data = extract(...)
    cache.set("facebook", "campaign_performance", params, data)
```

### 8. Configuración (`config.py`)

**Configuración centralizada:**
- Caché (habilitado, tamaño, TTL)
- Almacenamiento (tipo, connection IDs)
- Retry (intentos, backoff, timeouts)
- Validación (habilitado, estricto)
- Data quality (umbrales)

## 🔄 Flujo Completo de Datos

```
┌─────────────────────────────────────────────────┐
│         1. Health Checks (utils)               │
│  - Credenciales API                            │
│  - Base de datos                               │
│  - Validación de fechas                        │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│         2. Caché Check (cache.py)               │
│  - Verificar si datos existen                  │
│  - Retornar si disponibles                     │
└────────────────────┬────────────────────────────┘
                     │ (si no en caché)
                     ▼
┌─────────────────────────────────────────────────┐
│      3. Cliente (base_client.py)                │
│  - FacebookAdsClient / TikTokAdsClient         │
│  - Retry, rate limiting, métricas              │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│      4. Extractor (extractors.py)               │
│  - FacebookExtractor / TikTokExtractor         │
│  - Normalización, transformación               │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│      5. Validación (validators.py)              │
│  - Schema, valores, consistencia               │
│  - Completitud                                  │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│      6. Procesamiento (processors.py)           │
│  - Normalización final                         │
│  - Métricas agregadas                          │
│  - Agrupación y filtrado                       │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│      7. Data Quality (utils)                    │
│  - Validación de calidad                       │
│  - Detección de anomalías                      │
└────────────────────┬────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────┐
│      8. Almacenamiento (storage.py)             │
│  - PostgreSQLStorage                           │
│  - Guardado con validación                     │
└─────────────────────────────────────────────────┘
```

## 💡 Ejemplo de Uso Completo

### DAG Simple

```python
from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
from ads_reporting.extractors import FacebookExtractor
from ads_reporting.storage import get_storage

config = FacebookAdsConfig(...)
with FacebookAdsClient(config) as client:
    extractor = FacebookExtractor(client)
    data = extractor.extract_campaign_performance(...)
    
storage = get_storage("postgres")
storage.save_campaign_performance(data, "table_name")
```

### DAG Completo con Todas las Funcionalidades

Ver `example_integrated_dag.py` para ejemplo completo con:
- Health checks
- Caché
- Validación
- Procesamiento
- Data quality
- Almacenamiento

## 🎯 Casos de Uso

### 1. Extracción Simple
```python
extractor = FacebookExtractor(client)
data = extractor.extract_campaign_performance(...)
```

### 2. Extracción con Caché
```python
cache = get_cache()
cached = cache.get("facebook", "campaign_performance", params)
if not cached:
    data = extractor.extract_campaign_performance(...)
    cache.set("facebook", "campaign_performance", params, data)
```

### 3. Validación
```python
from ads_reporting.validators import validate_campaign_data

result = validate_campaign_data(data, strict=True)
if not result.valid:
    raise ValueError(result.errors)
```

### 4. Procesamiento
```python
from ads_reporting.processors import CampaignProcessor

processor = CampaignProcessor()
normalized = processor.normalize(data)
metrics = processor.calculate_metrics(normalized)
top_performers = processor.filter_by_performance(normalized, min_ctr=2.0)
```

### 5. Almacenamiento
```python
from ads_reporting.storage import get_storage

storage = get_storage("postgres", postgres_conn_id="...")
result = storage.save_campaign_performance(data, "table_name")
```

## 📊 Configuración

### Variables de Entorno

```bash
# Configuración Global
ADS_CACHE_ENABLED=true
ADS_CACHE_MAXSIZE=100
ADS_CACHE_TTL=300
ADS_DEFAULT_STORAGE=postgres
ADS_ENABLE_VALIDATION=true
ADS_ENABLE_DQ_CHECKS=true

# Facebook
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_AD_ACCOUNT_ID=act_123456789
FACEBOOK_API_VERSION=v18.0
FACEBOOK_MAX_RETRIES=3

# TikTok
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_ADVERTISER_ID=your_id

# Google
GOOGLE_ADS_CUSTOMER_ID=123-456-7890
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_DEVELOPER_TOKEN=your_dev_token
```

## 🔍 Monitoreo y Métricas

### Métricas Disponibles

- `ads_reporting.{platform}.{operation}.start`
- `ads_reporting.{platform}.{operation}.success`
- `ads_reporting.{platform}.{operation}.error`
- `ads_reporting.{platform}.{operation}.duration_ms`

### Logging Estructurado

Todos los módulos usan logging estructurado con contexto:
- Plataforma
- Operación
- Parámetros
- Errores con detalles

## ✅ Ventajas de la Arquitectura Completa

1. **Modularidad Total**
   - Cada componente es independiente
   - Fácil de testear
   - Fácil de extender

2. **Reutilización Máxima**
   - Componentes usables en múltiples contextos
   - Sin duplicación de código

3. **Mantenibilidad**
   - Código organizado y documentado
   - Cambios localizados
   - Testing simplificado

4. **Escalabilidad**
   - Fácil agregar nuevas plataformas
   - Fácil agregar nuevos backends
   - Sin impacto en código existente

5. **Robustez**
   - Validación completa
   - Manejo de errores robusto
   - Caché para eficiencia

## 📚 Documentación Relacionada

- `ADS_REPORTING_MODULAR_ARCHITECTURE.md` - Arquitectura detallada
- `ADS_REPORTING_MODULAR_SUMMARY.md` - Resumen ejecutivo
- `ADS_REPORTING_IMPROVEMENTS.md` - Mejoras implementadas
- `ADS_REPORTING_LIBRARIES.md` - Librerías y mejores prácticas
- `ADS_REPORTING_ADDITIONAL_FEATURES.md` - Funcionalidades adicionales

## 🚀 Próximos Pasos

1. Agregar tests unitarios para cada módulo
2. Implementar S3Storage completamente
3. Agregar más procesadores (CreativeProcessor, etc.)
4. Implementar circuit breakers completos
5. Agregar alertas automáticas
6. Crear dashboard de métricas

