# 🚀 Guía de Integración Completa - Launch Campaign Automation

## 📋 Resumen

Este documento describe cómo integrar y usar el sistema completo de automatización de campañas de lanzamiento de producto, que incluye:

- **Workflow n8n principal**: `n8n_workflow_launch_campaign.json`
- **Script Python helper**: `scripts/launch_campaign_helper.py`
- **Workflows complementarios**: Social Integration, Customer Journey, Real-time Personalization

---

## 🎯 Características Principales

✅ **Automatización completa** de campañas de 3 días (Teaser → Demo → Oferta)  
✅ **Soporte multi-plataforma**: Instagram, Facebook, LinkedIn  
✅ **Dual trigger**: Programado (cron) y manual/programático (webhook)  
✅ **Tracking automático** de engagement y customer journey  
✅ **Integración Python** para control programático  
✅ **Generación dinámica** de contenido según día de campaña  

---

## 📦 Componentes del Sistema

### 1. Workflow Principal: `n8n_workflow_launch_campaign.json`

**Ubicación**: `/Users/adan/IA/n8n/n8n_workflow_launch_campaign.json`

**Funcionalidades**:
- **Triggers**:
  - 3 Schedule Triggers (Lunes, Miércoles, Viernes a las 9 AM)
  - 1 Webhook Trigger (`/webhook/launch-campaign`) para llamadas desde Python
- **Generación de contenido**: Crea captions personalizados según día
- **Publicación multi-plataforma**: Instagram, Facebook, LinkedIn
- **Tracking automático**: Integración con workflows de engagement y journey

**Nodos principales**:
1. `Webhook Launch Campaign` - Recibe llamadas desde Python
2. `Schedule Day 1/2/3` - Triggers programados
3. `Prepare Campaign Content` - Genera contenido según día
4. `Split by Platform` - Divide por plataforma
5. `Post to Instagram/Facebook/LinkedIn` - Publica en cada plataforma
6. `Consolidate Results` - Consolida resultados
7. `Track Engagement` - Inicia tracking
8. `Track Journey Event` - Registra en journey mapping

### 2. Script Python Helper: `scripts/launch_campaign_helper.py`

**Ubicación**: `/Users/adan/IA/n8n/scripts/launch_campaign_helper.py`

**Clase principal**: `LaunchCampaignHelper`

**Métodos disponibles**:
- `trigger_day_1_teaser(product_config)` - Dispara Día 1
- `trigger_day_2_demo(product_config)` - Dispara Día 2
- `trigger_day_3_offer(product_config)` - Dispara Día 3
- `track_social_engagement(...)` - Track engagement manual
- `track_journey_event(...)` - Track journey manual
- `get_campaign_metrics(...)` - Obtiene métricas

### 3. Workflows Complementarios

#### `n8n_workflow_social_integration.json`
- **Webhook**: `/webhook/social-engagement`
- **Función**: Analiza engagement, extrae leads, calcula scores

#### `n8n_workflow_customer_journey_mapping.json`
- **Webhook**: `/webhook/journey-event`
- **Función**: Mapea customer journey, identifica fricciones

#### `n8n_workflow_realtime_personalization.json`
- **Webhook**: `/webhook/personalize`
- **Función**: Personaliza mensajes según segmento

---

## 🛠️ Instalación y Configuración

### Paso 1: Importar Workflows en n8n

1. **Importar workflow principal**:
   ```bash
   # En n8n, ve a Workflows > Import
   # Selecciona: n8n_workflow_launch_campaign.json
   ```

2. **Importar workflows complementarios**:
   - `n8n_workflow_social_integration.json`
   - `n8n_workflow_customer_journey_mapping.json`
   - `n8n_workflow_realtime_personalization.json` (opcional)

### Paso 2: Configurar Variables de Entorno

En n8n, configura las siguientes variables de entorno:

```bash
# Configuración del Producto
PRODUCT_NAME="Mi Nuevo Producto"
PRODUCT_BENEFITS='["Beneficio 1", "Beneficio 2", "Beneficio 3"]'
DISCOUNT_PERCENTAGE=20
PLATFORMS='["instagram", "facebook", "linkedin"]'
HASHTAGS='["#Lanzamiento", "#NuevoProducto"]'
CTA_LINK="https://yoursite.com/launch"

# URLs de APIs de Redes Sociales
INSTAGRAM_API_URL="https://graph.instagram.com"
FACEBOOK_API_URL="https://graph.facebook.com"
LINKEDIN_API_URL="https://api.linkedin.com"
LINKEDIN_PERSON_URN="urn:li:person:YOUR_PERSON_ID"

# URL base de n8n (para webhooks internos)
N8N_BASE_URL="http://localhost:5678"  # O tu URL pública

# Credenciales (configurar en n8n Credentials)
# - Instagram API Token
# - Facebook Access Token
# - LinkedIn Access Token
```

### Paso 3: Configurar Credenciales en n8n

1. **Instagram**:
   - Tipo: HTTP Header Auth
   - Header: `Authorization: Bearer YOUR_INSTAGRAM_TOKEN`

2. **Facebook**:
   - Tipo: HTTP Header Auth
   - Header: `Authorization: Bearer YOUR_FACEBOOK_TOKEN`

3. **LinkedIn**:
   - Tipo: HTTP Header Auth
   - Header: `Authorization: Bearer YOUR_LINKEDIN_TOKEN`

### Paso 4: Instalar Dependencias Python

```bash
cd /Users/adan/IA/n8n/scripts
pip install requests
```

---

## 🚀 Uso

### Opción 1: Automatización Programada (Cron)

El workflow se ejecutará automáticamente:
- **Lunes 9 AM**: Día 1 (Teaser)
- **Miércoles 9 AM**: Día 2 (Demo)
- **Viernes 9 AM**: Día 3 (Oferta)

**No requiere acción manual** - solo asegúrate de que:
1. El workflow esté activado en n8n
2. Las variables de entorno estén configuradas
3. Las credenciales de APIs estén válidas

### Opción 2: Trigger Manual desde Python

```python
from scripts.launch_campaign_helper import LaunchCampaignHelper

# Inicializar helper
helper = LaunchCampaignHelper(
    n8n_base_url="https://your-n8n.com",  # URL de tu instancia n8n
    api_key="your_api_key"  # Opcional, si configuraste autenticación
)

# Configurar producto
product_config = {
    "name": "Mi Nuevo Producto",
    "benefits": [
        "Ahorra 10 horas semanales",
        "Aumenta productividad en 300%",
        "Fácil de usar"
    ],
    "problem": "Gestión de tareas complicada",
    "pain": "Pérdida de tiempo en tareas repetitivas",
    "result": "Automatización completa",
    "area": "productividad",
    "discount_percentage": 25,
    "normal_price": 199,
    "special_price": 149,
    "bonuses": ["Bonus 1", "Bonus 2"],
    "units_available": 50,
    "cta_link": "https://yoursite.com/launch",
    "platforms": ["instagram", "facebook", "linkedin"],
    "hashtags": ["#Productividad", "#Automatización", "#NuevoProducto"]
}

# Disparar Día 1
result = helper.trigger_day_1_teaser(product_config)
print(f"Resultado: {result}")

# Disparar Día 2
result = helper.trigger_day_2_demo(product_config)
print(f"Resultado: {result}")

# Disparar Día 3
result = helper.trigger_day_3_offer(product_config)
print(f"Resultado: {result}")
```

### Opción 3: Trigger Manual desde cURL

```bash
# Día 1: Teaser
curl -X POST https://your-n8n.com/webhook/launch-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "campaignDay": 1,
    "campaignType": "teaser",
    "productName": "Mi Nuevo Producto",
    "productBenefits": ["Beneficio 1", "Beneficio 2"],
    "problem": "Problema específico",
    "pain": "Dolor específico",
    "result": "Resultado deseado",
    "area": "Área",
    "platforms": ["instagram", "facebook", "linkedin"],
    "hashtags": ["#Lanzamiento"]
  }'

# Día 2: Demo
curl -X POST https://your-n8n.com/webhook/launch-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "campaignDay": 2,
    "campaignType": "demo",
    "productName": "Mi Nuevo Producto",
    "productBenefits": ["Beneficio 1", "Beneficio 2"],
    "ctaLink": "https://yoursite.com/launch",
    "platforms": ["instagram", "facebook", "linkedin"]
  }'

# Día 3: Oferta
curl -X POST https://your-n8n.com/webhook/launch-campaign \
  -H "Content-Type: application/json" \
  -d '{
    "campaignDay": 3,
    "campaignType": "offer",
    "productName": "Mi Nuevo Producto",
    "discountPercentage": 25,
    "unitsAvailable": 50,
    "ctaLink": "https://yoursite.com/launch",
    "platforms": ["instagram", "facebook", "linkedin"]
  }'
```

---

## 📊 Tracking y Métricas

### Tracking Automático

El workflow automáticamente:
1. **Registra posts** en el workflow de Social Integration
2. **Mapea eventos** en Customer Journey Mapping
3. **Consolida resultados** de todas las plataformas

### Obtener Métricas

```python
# Desde Python
metrics = helper.get_campaign_metrics(
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 1, 7)
)
print(metrics)
```

### Tracking Manual de Engagement

```python
# Track engagement manual
engagement = helper.track_social_engagement(
    platform="instagram",
    post_id="post_123",
    engagement_type="comment",
    content="SÍ, quiero ser de los primeros",
    user_id="user_456"
)
```

---

## 🔧 Troubleshooting

### Problema: Webhook no responde

**Solución**:
1. Verifica que el workflow esté activado
2. Verifica la URL del webhook: `https://your-n8n.com/webhook/launch-campaign`
3. Verifica que el nodo "Webhook Launch Campaign" esté configurado correctamente

### Problema: Publicación falla en alguna plataforma

**Solución**:
1. Verifica credenciales de la API
2. Verifica que el token tenga permisos de publicación
3. Revisa los logs del nodo específico (Instagram/Facebook/LinkedIn)
4. El workflow continúa aunque una plataforma falle (`continueOnFail: true`)

### Problema: Contenido no se genera correctamente

**Solución**:
1. Verifica variables de entorno en n8n
2. Si usas webhook, verifica que envíes todos los campos requeridos
3. Revisa el nodo "Prepare Campaign Content" para ver qué datos recibe

### Problema: Tracking no funciona

**Solución**:
1. Verifica que los workflows complementarios estén activos:
   - `n8n_workflow_social_integration.json`
   - `n8n_workflow_customer_journey_mapping.json`
2. Verifica que `N8N_BASE_URL` esté configurado correctamente
3. Verifica que los webhooks internos estén accesibles

---

## 📝 Estructura de Datos

### Payload del Webhook (desde Python)

```json
{
  "campaignDay": 1,
  "campaignType": "teaser",
  "productName": "Mi Nuevo Producto",
  "productBenefits": ["Beneficio 1", "Beneficio 2"],
  "problem": "Problema específico",
  "pain": "Dolor específico",
  "result": "Resultado deseado",
  "area": "Área",
  "discountPercentage": 20,
  "normalPrice": 199,
  "specialPrice": 149,
  "bonuses": ["Bonus 1"],
  "unitsAvailable": 100,
  "ctaLink": "https://yoursite.com/launch",
  "platforms": ["instagram", "facebook", "linkedin"],
  "hashtags": ["#Lanzamiento"],
  "timestamp": "2024-01-01T09:00:00Z"
}
```

### Respuesta del Webhook

```json
{
  "success": true,
  "message": "Campaign posts published successfully",
  "results": {
    "results": [
      {
        "platform": "instagram",
        "postId": "post_123",
        "success": true,
        "campaignDay": 1,
        "campaignType": "teaser"
      },
      {
        "platform": "facebook",
        "postId": "post_456",
        "success": true,
        "campaignDay": 1,
        "campaignType": "teaser"
      }
    ],
    "totalPlatforms": 2,
    "successful": 2,
    "failed": 0
  },
  "timestamp": "2024-01-01T09:00:05Z"
}
```

---

## 🔗 Integración con Otros Workflows

### Social Integration Workflow

El workflow principal automáticamente envía eventos a:
- **Webhook**: `/webhook/social-engagement`
- **Payload**: `{ platform, postId, campaignDay, campaignType, engagementType: "post_created" }`

### Customer Journey Mapping Workflow

El workflow principal automáticamente envía eventos a:
- **Webhook**: `/webhook/journey-event`
- **Payload**: `{ eventType: "campaign_post", campaignDay, campaignType, pageCategory: "campaign_launch", pageUrl }`

---

## 📚 Documentación Adicional

- **Guía completa de campaña**: `CAMPAÑA_LANZAMIENTO_PRODUCTO.md`
- **Workflow Social Integration**: Ver `n8n_workflow_social_integration.json`
- **Workflow Customer Journey**: Ver `n8n_workflow_customer_journey_mapping.json`

---

## ✅ Checklist de Integración

- [ ] Workflow principal importado y activado
- [ ] Workflows complementarios importados y activados
- [ ] Variables de entorno configuradas
- [ ] Credenciales de APIs configuradas (Instagram, Facebook, LinkedIn)
- [ ] Webhook accesible desde Python/externo
- [ ] Script Python instalado y funcionando
- [ ] Prueba de trigger manual exitosa
- [ ] Prueba de trigger programado exitosa
- [ ] Tracking funcionando correctamente
- [ ] Integración con workflows complementarios verificada

---

## 🆘 Soporte

Para problemas o preguntas:
1. Revisa los logs en n8n
2. Verifica la documentación en `CAMPAÑA_LANZAMIENTO_PRODUCTO.md`
3. Revisa los workflows complementarios para entender la integración completa

---

**Última actualización**: 2024-01-01  
**Versión**: 1.0.0



