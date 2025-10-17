# 🔌 API Reference - FRONTIER

> **Documentación completa de todas las APIs disponibles en la plataforma FRONTIER**

## 📋 Tabla de Contenidos

- [🎯 Introducción](#-introducción)
- [🔐 Autenticación](#-autenticación)
- [👤 Usuarios](#-usuarios)
- [📢 Campañas](#-campañas)
- [🤖 IA y Machine Learning](#-ia-y-machine-learning)
- [📊 Analytics](#-analytics)
- [📧 Email Marketing](#-email-marketing)
- [📱 Social Media](#-social-media)
- [🎨 Visual Marketing](#-visual-marketing)
- [🔔 Notificaciones](#-notificaciones)
- [📈 Reportes](#-reportes)
- [❌ Códigos de Error](#-códigos-de-error)

## 🎯 Introducción

La API de FRONTIER es una API RESTful que permite integrar todas las funcionalidades de la plataforma en tus aplicaciones. Todas las respuestas están en formato JSON y utilizan códigos de estado HTTP estándar.

### 🌐 Base URL
```
Production: https://api.frontier-ai.com/v1
Staging: https://staging-api.frontier-ai.com/v1
```

### 📝 Formato de Respuesta
```json
{
  "success": true,
  "data": {
    // Datos de respuesta
  },
  "meta": {
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
  }
}
```

### 🔄 Rate Limiting
- **Límite**: 1000 requests por hora por API key
- **Headers**: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

## 🔐 Autenticación

### Obtener API Key
```http
POST /auth/api-key
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "api_key": "fk_live_1234567890abcdef",
    "expires_at": "2024-12-31T23:59:59Z"
  }
}
```

### Usar API Key
```http
Authorization: Bearer fk_live_1234567890abcdef
```

### Refresh API Key
```http
POST /auth/refresh-api-key
Authorization: Bearer fk_live_1234567890abcdef
```

## 👤 Usuarios

### Obtener Perfil de Usuario
```http
GET /users/profile
Authorization: Bearer {api_key}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "id": "user_123",
    "email": "user@example.com",
    "name": "John Doe",
    "company": "Acme Corp",
    "role": "admin",
    "created_at": "2024-01-01T00:00:00Z",
    "subscription": {
      "plan": "pro",
      "status": "active",
      "expires_at": "2024-12-31T23:59:59Z"
    }
  }
}
```

### Actualizar Perfil
```http
PUT /users/profile
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "John Smith",
  "company": "New Company"
}
```

### Obtener Configuración
```http
GET /users/settings
Authorization: Bearer {api_key}
```

### Actualizar Configuración
```http
PUT /users/settings
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "notifications": {
    "email": true,
    "push": false,
    "sms": false
  },
  "preferences": {
    "timezone": "UTC",
    "language": "en",
    "currency": "USD"
  }
}
```

## 📢 Campañas

### Listar Campañas
```http
GET /campaigns?page=1&limit=10&status=active
Authorization: Bearer {api_key}
```

**Parámetros de Query:**
- `page` (int): Número de página (default: 1)
- `limit` (int): Elementos por página (default: 10, max: 100)
- `status` (string): Filtro por estado (draft, active, paused, completed)
- `type` (string): Filtro por tipo (social_media, email, display, search)
- `platform` (string): Filtro por plataforma (facebook, instagram, google, etc.)

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "camp_123",
      "name": "Summer Sale Campaign",
      "type": "social_media",
      "status": "active",
      "budget": 1000.00,
      "spent": 250.50,
      "start_date": "2024-06-01",
      "end_date": "2024-08-31",
      "platforms": ["facebook", "instagram"],
      "metrics": {
        "impressions": 50000,
        "clicks": 2500,
        "conversions": 125,
        "ctr": 5.0,
        "cpc": 0.10,
        "cpa": 2.00
      },
      "created_at": "2024-05-15T10:30:00Z"
    }
  ],
  "meta": {
    "pagination": {
      "page": 1,
      "limit": 10,
      "total": 25,
      "pages": 3
    }
  }
}
```

### Crear Campaña
```http
POST /campaigns
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "New Campaign",
  "type": "social_media",
  "platforms": ["facebook", "instagram"],
  "budget": 1000.00,
  "start_date": "2024-06-01",
  "end_date": "2024-08-31",
  "target_audience": {
    "age_range": [25, 45],
    "interests": ["fashion", "lifestyle"],
    "locations": ["US", "CA"],
    "gender": "all"
  },
  "settings": {
    "bid_strategy": "cost_per_click",
    "optimization_goal": "conversions",
    "budget_distribution": "daily"
  }
}
```

### Obtener Campaña
```http
GET /campaigns/{campaign_id}
Authorization: Bearer {api_key}
```

### Actualizar Campaña
```http
PUT /campaigns/{campaign_id}
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "Updated Campaign Name",
  "budget": 1500.00,
  "status": "paused"
}
```

### Eliminar Campaña
```http
DELETE /campaigns/{campaign_id}
Authorization: Bearer {api_key}
```

### Duplicar Campaña
```http
POST /campaigns/{campaign_id}/duplicate
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "Duplicated Campaign",
  "start_date": "2024-07-01"
}
```

## 🤖 IA y Machine Learning

### Generar Contenido
```http
POST /ai/generate-content
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "type": "social_media_post",
  "topic": "summer fashion",
  "tone": "casual",
  "platform": "instagram",
  "target_audience": "fashion enthusiasts",
  "length": "short",
  "include_hashtags": true,
  "include_cta": true
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "content": "☀️ Summer vibes are here! 🌸 Discover our latest collection of breezy dresses and lightweight fabrics perfect for those warm sunny days. ✨ #SummerFashion #Style #Fashion",
    "hashtags": ["#SummerFashion", "#Style", "#Fashion", "#SummerVibes", "#Dresses"],
    "cta": "Shop now and embrace the summer season!",
    "engagement_score": 8.5,
    "readability_score": 9.2
  }
}
```

### Análisis de Sentimientos
```http
POST /ai/sentiment-analysis
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "text": "I love this new product! It's amazing and exactly what I needed.",
  "language": "en"
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "sentiment": "positive",
    "confidence": 0.95,
    "emotions": {
      "joy": 0.8,
      "excitement": 0.7,
      "satisfaction": 0.9
    },
    "keywords": ["love", "amazing", "needed"]
  }
}
```

### Optimización de Imágenes
```http
POST /ai/optimize-image
Authorization: Bearer {api_key}
Content-Type: multipart/form-data

{
  "image": <file>,
  "optimization_type": "social_media",
  "platform": "instagram",
  "format": "square",
  "quality": "high"
}
```

### Predicción de Conversión
```http
POST /ai/predict-conversion
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "campaign_id": "camp_123",
  "audience_segment": "fashion_enthusiasts",
  "content_type": "video",
  "platform": "instagram",
  "budget": 500.00
}
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "conversion_probability": 0.75,
    "predicted_conversions": 45,
    "confidence_interval": [35, 55],
    "recommendations": [
      "Increase budget by 20% for better reach",
      "Use video content for higher engagement",
      "Target audience during peak hours (7-9 PM)"
    ]
  }
}
```

### Generar Hashtags
```http
POST /ai/generate-hashtags
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "content": "New summer collection is here!",
  "platform": "instagram",
  "industry": "fashion",
  "count": 10
}
```

### Análisis de Competencia
```http
POST /ai/competitor-analysis
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "competitor_handles": ["@competitor1", "@competitor2"],
  "analysis_type": "content_performance",
  "time_period": "30_days"
}
```

## 📊 Analytics

### Métricas de Campaña
```http
GET /analytics/campaigns/{campaign_id}/metrics
Authorization: Bearer {api_key}
```

**Parámetros de Query:**
- `start_date` (string): Fecha de inicio (YYYY-MM-DD)
- `end_date` (string): Fecha de fin (YYYY-MM-DD)
- `granularity` (string): daily, weekly, monthly
- `metrics` (array): Lista de métricas a incluir

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "campaign_id": "camp_123",
    "period": {
      "start_date": "2024-06-01",
      "end_date": "2024-06-30"
    },
    "summary": {
      "impressions": 50000,
      "clicks": 2500,
      "conversions": 125,
      "spend": 250.50,
      "ctr": 5.0,
      "cpc": 0.10,
      "cpa": 2.00,
      "roas": 4.0
    },
    "daily_breakdown": [
      {
        "date": "2024-06-01",
        "impressions": 1500,
        "clicks": 75,
        "conversions": 4,
        "spend": 8.50
      }
    ],
    "platform_breakdown": {
      "facebook": {
        "impressions": 30000,
        "clicks": 1500,
        "conversions": 75
      },
      "instagram": {
        "impressions": 20000,
        "clicks": 1000,
        "conversions": 50
      }
    }
  }
}
```

### Métricas de Audiencia
```http
GET /analytics/audience/insights
Authorization: Bearer {api_key}
```

### Métricas de Contenido
```http
GET /analytics/content/performance
Authorization: Bearer {api_key}
```

### Métricas de Competencia
```http
GET /analytics/competitors/benchmark
Authorization: Bearer {api_key}
```

### Predicciones
```http
POST /analytics/predictions
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "campaign_id": "camp_123",
  "prediction_type": "performance",
  "forecast_period": "30_days"
}
```

## 📧 Email Marketing

### Listar Listas de Contactos
```http
GET /email/lists
Authorization: Bearer {api_key}
```

### Crear Lista de Contactos
```http
POST /email/lists
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "Newsletter Subscribers",
  "description": "Monthly newsletter subscribers",
  "tags": ["newsletter", "monthly"]
}
```

### Agregar Contacto
```http
POST /email/contacts
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "list_ids": ["list_123"],
  "tags": ["vip", "customer"],
  "custom_fields": {
    "company": "Acme Corp",
    "industry": "technology"
  }
}
```

### Crear Campaña de Email
```http
POST /email/campaigns
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "Welcome Series",
  "subject": "Welcome to our platform!",
  "list_id": "list_123",
  "template_id": "template_456",
  "schedule": {
    "type": "immediate"
  }
}
```

### Enviar Email de Prueba
```http
POST /email/campaigns/{campaign_id}/test
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "test_emails": ["test@example.com"]
}
```

### Programar Campaña
```http
POST /email/campaigns/{campaign_id}/schedule
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "send_at": "2024-06-01T10:00:00Z"
}
```

## 📱 Social Media

### Conectar Cuenta
```http
POST /social/connect
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "platform": "facebook",
  "access_token": "user_access_token",
  "page_id": "page_123"
}
```

### Listar Cuentas Conectadas
```http
GET /social/accounts
Authorization: Bearer {api_key}
```

### Publicar Contenido
```http
POST /social/publish
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "platform": "instagram",
  "account_id": "account_123",
  "content": {
    "text": "Check out our new product!",
    "image_url": "https://example.com/image.jpg",
    "hashtags": ["#newproduct", "#innovation"]
  },
  "schedule": {
    "type": "immediate"
  }
}
```

### Programar Publicación
```http
POST /social/schedule
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "platform": "facebook",
  "account_id": "account_123",
  "content": {
    "text": "Scheduled post content",
    "image_url": "https://example.com/image.jpg"
  },
  "schedule": {
    "type": "scheduled",
    "publish_at": "2024-06-01T15:00:00Z"
  }
}
```

### Obtener Métricas de Red Social
```http
GET /social/accounts/{account_id}/metrics
Authorization: Bearer {api_key}
```

## 🎨 Visual Marketing

### Generar Diseño
```http
POST /visual/generate
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "type": "social_media_post",
  "platform": "instagram",
  "style": "modern",
  "content": {
    "title": "Summer Sale",
    "subtitle": "Up to 50% off",
    "cta": "Shop Now"
  },
  "brand_guidelines": {
    "primary_color": "#FF6B6B",
    "secondary_color": "#4ECDC4",
    "font_family": "Montserrat"
  }
}
```

### Optimizar Imagen
```http
POST /visual/optimize
Authorization: Bearer {api_key}
Content-Type: multipart/form-data

{
  "image": <file>,
  "optimization_type": "social_media",
  "platform": "facebook",
  "format": "landscape"
}
```

### Crear Template
```http
POST /visual/templates
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "Product Launch Template",
  "category": "product",
  "platform": "instagram",
  "elements": [
    {
      "type": "text",
      "content": "New Product",
      "position": {"x": 100, "y": 100}
    }
  ]
}
```

## 🔔 Notificaciones

### Configurar Webhooks
```http
POST /webhooks
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "url": "https://your-app.com/webhook",
  "events": ["campaign.completed", "campaign.paused"],
  "secret": "webhook_secret"
}
```

### Listar Webhooks
```http
GET /webhooks
Authorization: Bearer {api_key}
```

### Probar Webhook
```http
POST /webhooks/{webhook_id}/test
Authorization: Bearer {api_key}
```

### Eventos Disponibles
- `campaign.created`
- `campaign.updated`
- `campaign.paused`
- `campaign.completed`
- `campaign.budget_exceeded`
- `email.sent`
- `email.delivered`
- `email.opened`
- `email.clicked`
- `social.post_published`
- `social.post_failed`

## 📈 Reportes

### Crear Reporte Personalizado
```http
POST /reports
Authorization: Bearer {api_key}
Content-Type: application/json

{
  "name": "Monthly Performance Report",
  "type": "campaign_performance",
  "date_range": {
    "start": "2024-06-01",
    "end": "2024-06-30"
  },
  "filters": {
    "campaign_ids": ["camp_123", "camp_456"],
    "platforms": ["facebook", "instagram"]
  },
  "metrics": ["impressions", "clicks", "conversions", "spend"],
  "group_by": ["campaign", "platform"],
  "schedule": {
    "frequency": "monthly",
    "day_of_month": 1
  }
}
```

### Generar Reporte
```http
POST /reports/{report_id}/generate
Authorization: Bearer {api_key}
```

### Descargar Reporte
```http
GET /reports/{report_id}/download
Authorization: Bearer {api_key}
```

### Listar Reportes
```http
GET /reports
Authorization: Bearer {api_key}
```

## ❌ Códigos de Error

### Códigos HTTP
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error

### Códigos de Error Personalizados
```json
{
  "success": false,
  "error": {
    "code": "INVALID_CAMPAIGN_BUDGET",
    "message": "Campaign budget must be greater than 0",
    "details": {
      "field": "budget",
      "value": -100,
      "constraint": "minimum_value"
    }
  }
}
```

### Códigos de Error Comunes
- `INVALID_API_KEY` - API key inválida o expirada
- `RATE_LIMIT_EXCEEDED` - Límite de requests excedido
- `INVALID_CAMPAIGN_DATA` - Datos de campaña inválidos
- `INSUFFICIENT_BUDGET` - Presupuesto insuficiente
- `PLATFORM_CONNECTION_FAILED` - Error de conexión con plataforma
- `CONTENT_GENERATION_FAILED` - Error en generación de contenido
- `ANALYTICS_DATA_UNAVAILABLE` - Datos de analytics no disponibles

---

<div align="center">

**🔌 ¿Necesitas ayuda con la API?**

[Documentación Interactiva](https://api-docs.frontier-ai.com) | [SDKs Disponibles](https://github.com/frontier-ai/sdks) | [Soporte Técnico](mailto:api-support@frontier-ai.com)

</div>

