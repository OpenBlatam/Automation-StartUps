# Librerías Optimizadas para Ads Reporting

Este documento describe las librerías oficiales y mejores prácticas utilizadas en los DAGs de reporting de Facebook Ads, TikTok Ads y Google Ads.

## 📚 Librerías Oficiales por Plataforma

### Facebook Ads - `facebook-business`

**SDK Oficial:** `facebook-business` (>=19.0.0)

```python
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adsinsights import AdsInsights
```

**Ventajas:**
- ✅ SDK oficial mantenido por Meta
- ✅ Manejo automático de autenticación y rate limiting
- ✅ Tipos y validaciones integradas
- ✅ Soporte completo para todas las funcionalidades de la API
- ✅ Paginación automática
- ✅ Manejo de errores robusto

**Instalación:**
```bash
pip install facebook-business>=19.0.0
```

**Uso en código:**
```python
# Inicializar API
FacebookAdsApi.init(access_token=token, api_version="v18.0")
account = AdAccount("act_123456789")

# Obtener insights
insights = account.get_insights(
    fields=[AdsInsights.Field.impressions, AdsInsights.Field.clicks],
    params={'time_range': {'since': '2024-01-01', 'until': '2024-01-31'}}
)
```

### Google Ads - `google-ads`

**SDK Oficial:** `google-ads` (>=24.0.0)

```python
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
```

**Ventajas:**
- ✅ SDK oficial mantenido por Google
- ✅ Query builder tipo SQL (GAQL)
- ✅ Manejo automático de autenticación OAuth2
- ✅ Soporte completo para atribución multicanal
- ✅ Validación de queries antes de ejecutar
- ✅ Paginación automática

**Instalación:**
```bash
pip install google-ads>=24.0.0
```

**Uso en código:**
```python
# Inicializar cliente
client = GoogleAdsClient.load_from_storage("google-ads.yaml")
ga_service = client.get_service("GoogleAdsService")

# Query tipo SQL
query = """
SELECT campaign.id, metrics.impressions, metrics.clicks
FROM campaign
WHERE segments.date >= '2024-01-01'
"""

response = ga_service.search(customer_id="1234567890", query=query)
```

### TikTok Ads - No hay SDK oficial en Python

**Solución:** Usar `requests` con la API REST oficial

TikTok no proporciona un SDK Python oficial, por lo que usamos `requests` directamente con:
- ✅ Autenticación OAuth2 manual
- ✅ Manejo de rate limiting manual
- ✅ Parsing de respuestas JSON

**Mejores prácticas implementadas:**
- Retry logic con exponential backoff
- Rate limiting respetado (pausas entre requests)
- Manejo robusto de errores
- Validación de respuestas

## 🔄 Estrategia de Fallback

Todos los DAGs implementan una estrategia de fallback:

1. **Intento con SDK oficial** (si está disponible)
2. **Fallback a requests** (si el SDK falla o no está disponible)
3. **Logging detallado** de qué método se está usando

Esto garantiza que los DAGs funcionen incluso si:
- El SDK no está instalado
- Hay problemas con el SDK
- Se prefiere usar requests por razones de control

## 📦 Dependencias Completas

Archivo: `REQUIREMENTS_ads_reporting.txt`

```
facebook-business>=19.0.0    # Facebook Ads SDK oficial
google-ads>=24.0.0           # Google Ads SDK oficial
pandas>=2.0.0                 # Para análisis de datos
requests>=2.31.0              # Para TikTok y fallback
pendulum>=3.0.0               # Manejo de fechas
psycopg2-binary>=2.9.0        # PostgreSQL
python-dateutil>=2.8.0       # Utilidades de fecha
```

## 🚀 Mejores Prácticas Implementadas

### 1. Inicialización Lazy
Los SDKs se inicializan solo cuando se necesitan, no al importar el módulo.

### 2. Manejo de Errores Robusto
- Try/except específicos por tipo de error
- Logging detallado de errores
- Fallback automático a método alternativo

### 3. Rate Limiting
- Respeto de límites de API
- Pausas automáticas entre requests
- Retry con exponential backoff

### 4. Paginación Automática
- Los SDKs manejan paginación automáticamente
- Fallback manual con tracking de `next_url`

### 5. Validación de Datos
- Type hints completos
- Validación de campos requeridos
- Manejo de valores None/defaults

## 🔧 Configuración Recomendada

### Variables de Entorno

**Facebook:**
```bash
FACEBOOK_ACCESS_TOKEN=your_token
FACEBOOK_AD_ACCOUNT_ID=act_123456789
FACEBOOK_API_VERSION=v18.0
```

**Google:**
```bash
GOOGLE_ADS_CUSTOMER_ID=123-456-7890
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_DEVELOPER_TOKEN=your_dev_token
```

**TikTok:**
```bash
TIKTOK_ACCESS_TOKEN=your_token
TIKTOK_ADVERTISER_ID=your_advertiser_id
TIKTOK_API_VERSION=v1.3
```

## 📊 Comparación de Métodos

| Plataforma | SDK Oficial | Método Alternativo | Recomendado |
|------------|------------|-------------------|-------------|
| Facebook Ads | ✅ `facebook-business` | `requests` | **SDK Oficial** |
| Google Ads | ✅ `google-ads` | `requests` (complejo) | **SDK Oficial** |
| TikTok Ads | ❌ No existe | `requests` | **requests** |

## 🔍 Monitoreo y Logging

Todos los DAGs incluyen logging detallado:
- Método usado (SDK vs requests)
- Número de registros extraídos
- Errores con contexto completo
- Tiempo de ejecución
- Rate limiting detectado

## 📝 Notas Importantes

1. **Facebook SDK:** Requiere tokens con permisos adecuados
2. **Google SDK:** Requiere Developer Token activado en la cuenta
3. **TikTok API:** No tiene SDK, requiere implementación manual de OAuth2
4. **Versiones:** Mantener SDKs actualizados para nuevas funcionalidades

## 🛠️ Troubleshooting

### Error: "SDK no disponible"
```bash
pip install facebook-business google-ads
```

### Error: "Rate limit exceeded"
- Aumentar delays entre requests
- Reducir tamaño de queries
- Usar filtros de fecha más cortos

### Error: "Authentication failed"
- Verificar tokens en variables de entorno
- Verificar permisos de tokens
- Verificar fechas de expiración


