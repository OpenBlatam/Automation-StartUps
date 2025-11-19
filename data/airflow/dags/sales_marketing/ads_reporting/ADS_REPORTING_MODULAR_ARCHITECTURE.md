# Arquitectura Modular - Ads Reporting

## 🏗️ Estructura Modular

La arquitectura modular separa las responsabilidades en módulos independientes y reutilizables:

```
ads_reporting/
├── __init__.py              # Exports principales
├── base_client.py           # Cliente base con funcionalidades compartidas
├── facebook_client.py       # Cliente específico para Facebook
├── tiktok_client.py         # Cliente específico para TikTok
├── google_client.py         # Cliente específico para Google
├── extractors.py            # Extractores de datos por plataforma
├── storage.py               # Almacenadores (PostgreSQL, S3, etc.)
└── processors.py            # Procesadores de datos (futuro)

ads_reporting_utils.py      # Utilidades compartidas (health checks, DQ, etc.)
```

## 📦 Módulos Principales

### 1. Base Client (`base_client.py`)

**Responsabilidades:**
- Manejo de errores estándar
- Retry logic con exponential backoff
- Rate limiting automático
- Sesiones HTTP reutilizables
- Métricas y tracking

**Clases:**
- `BaseAdsClient`: Cliente base abstracto
- `APIConfig`: Configuración base
- Excepciones: `AdsAPIError`, `AdsAuthError`, `AdsRateLimitError`

**Uso:**
```python
from ads_reporting.base_client import BaseAdsClient, APIConfig

class MyClient(BaseAdsClient):
    def get_base_url(self) -> str:
        return "https://api.example.com"
    
    def get_default_headers(self) -> Dict[str, str]:
        return {"Authorization": f"Bearer {self.config.access_token}"}
```

### 2. Clientes Específicos

#### Facebook Client (`facebook_client.py`)
- Usa SDK oficial `facebook-business` cuando está disponible
- Fallback a API REST
- Manejo específico de insights y paginación

#### TikTok Client (`tiktok_client.py`)
- API REST directa (no hay SDK oficial)
- Manejo de reportes integrados
- Paginación manual

#### Google Client (`google_client.py`)
- Usa SDK oficial `google-ads`
- Soporte para queries GAQL
- Manejo de autenticación OAuth2

### 3. Extractores (`extractors.py`)

**Responsabilidades:**
- Extracción de datos de cada plataforma
- Normalización de datos
- Transformaciones básicas

**Clases:**
- `BaseExtractor`: Extractor base abstracto
- `FacebookExtractor`: Extracción de Facebook
- `TikTokExtractor`: Extracción de TikTok

**Uso:**
```python
from ads_reporting.extractors import FacebookExtractor

extractor = FacebookExtractor(client)
data = extractor.extract_campaign_performance(
    date_start="2024-01-01",
    date_stop="2024-01-31"
)
```

### 4. Almacenadores (`storage.py`)

**Responsabilidades:**
- Guardado de datos en diferentes backends
- Creación automática de tablas
- Validación de esquemas

**Clases:**
- `BaseStorage`: Almacenador base abstracto
- `PostgreSQLStorage`: Almacenamiento en PostgreSQL
- `S3Storage`: Almacenamiento en S3 (placeholder)

**Uso:**
```python
from ads_reporting.storage import get_storage

storage = get_storage("postgres", postgres_conn_id="postgres_default")
result = storage.save_campaign_performance(data, "table_name")
```

## 🔄 Flujo de Datos Modular

```
┌─────────────┐
│   Config    │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Client    │ (FacebookAdsClient, TikTokAdsClient, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  Extractor  │ (FacebookExtractor, TikTokExtractor, etc.)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│   Storage   │ (PostgreSQLStorage, S3Storage, etc.)
└─────────────┘
```

## ✅ Ventajas de la Arquitectura Modular

### 1. Separación de Responsabilidades
- Cada módulo tiene una responsabilidad única
- Fácil de testear individualmente
- Cambios en un módulo no afectan otros

### 2. Reutilización
- Clientes pueden usarse en múltiples contextos
- Extractores independientes de almacenamiento
- Almacenadores independientes de plataformas

### 3. Extensibilidad
- Fácil agregar nuevas plataformas
- Fácil agregar nuevos backends de almacenamiento
- Fácil agregar nuevos tipos de extractores

### 4. Testabilidad
- Cada módulo puede testearse de forma aislada
- Mocks fáciles de implementar
- Tests unitarios independientes

### 5. Mantenibilidad
- Código organizado y fácil de navegar
- Cambios localizados
- Documentación clara por módulo

## 📝 Ejemplo de Uso Completo

```python
from ads_reporting.facebook_client import FacebookAdsClient, FacebookAdsConfig
from ads_reporting.extractors import FacebookExtractor
from ads_reporting.storage import get_storage

# 1. Configuración
config = FacebookAdsConfig(
    access_token="token",
    ad_account_id="act_123",
    api_version="v18.0"
)

# 2. Cliente
with FacebookAdsClient(config) as client:
    # 3. Extractor
    extractor = FacebookExtractor(client)
    
    # 4. Extracción
    data = extractor.extract_campaign_performance(
        date_start="2024-01-01",
        date_stop="2024-01-31"
    )
    
    # 5. Almacenamiento
    storage = get_storage("postgres", postgres_conn_id="postgres_default")
    storage.save_campaign_performance(data, "facebook_ads_performance")
```

## 🎯 Comparación: Antes vs Después

### Antes (Monolítico)
```python
# Todo en un archivo
def extract_facebook_ads():
    # Configuración
    # Cliente
    # Extracción
    # Procesamiento
    # Almacenamiento
    # Todo mezclado
```

### Después (Modular)
```python
# Separado en módulos
config = FacebookAdsConfig(...)
client = FacebookAdsClient(config)
extractor = FacebookExtractor(client)
storage = get_storage("postgres")

data = extractor.extract(...)
storage.save(...)
```

## 🔧 Extensión a Nuevas Plataformas

Para agregar una nueva plataforma (ej: LinkedIn Ads):

1. **Crear cliente** (`linkedin_client.py`):
```python
class LinkedInAdsClient(BaseAdsClient):
    def get_base_url(self) -> str:
        return "https://api.linkedin.com"
```

2. **Crear extractor** (`extractors.py`):
```python
class LinkedInExtractor(BaseExtractor):
    def extract_campaign_performance(...):
        # Implementación
```

3. **Usar en DAG**:
```python
client = LinkedInAdsClient(config)
extractor = LinkedInExtractor(client)
```

## 📊 Próximas Mejoras

1. **Processors Module**: Transformaciones de datos
2. **Validators Module**: Validación de datos
3. **Caching Module**: Caché inteligente
4. **Monitoring Module**: Métricas y alertas avanzadas

