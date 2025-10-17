# 📚 API Reference - SaaS de IA para Marketing

## 🔗 Base URL

```
Production: https://api.ia-marketing.com/v1
Staging: https://staging-api.ia-marketing.com/v1
Local: http://localhost:3000/api/v1
```

## 🔐 Autenticación

Todas las APIs requieren autenticación mediante JWT Bearer Token.

```bash
Authorization: Bearer <tu_jwt_token>
```

### Obtener Token
```http
POST /auth/login
Content-Type: application/json

{
  "email": "usuario@ejemplo.com",
  "password": "tu_password"
}
```

**Respuesta:**
```json
{
  "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expiresIn": 3600,
  "user": {
    "id": "uuid",
    "email": "usuario@ejemplo.com",
    "subscriptionPlan": "professional"
  }
}
```

## 📝 Copywriting APIs

### Generar Contenido

#### POST /copywriting/generate

Genera contenido de marketing usando IA.

**Parámetros:**
```json
{
  "type": "landing_page" | "email" | "ad" | "social_post" | "blog_post",
  "industry": "saas" | "ecommerce" | "fintech" | "healthcare" | "education",
  "targetAudience": "startups" | "enterprise" | "consumers" | "b2b",
  "tone": "professional" | "casual" | "friendly" | "authoritative",
  "length": "short" | "medium" | "long",
  "keywords": ["keyword1", "keyword2"],
  "prompt": "Descripción específica del contenido deseado",
  "model": "gpt-4" | "gpt-3.5-turbo" | "claude-3-opus" | "claude-3-sonnet"
}
```

**Ejemplo de Request:**
```json
{
  "type": "landing_page",
  "industry": "saas",
  "targetAudience": "startups",
  "tone": "professional",
  "length": "medium",
  "keywords": ["productivity", "automation", "efficiency"],
  "prompt": "Landing page para una plataforma de gestión de proyectos dirigida a startups",
  "model": "gpt-4"
}
```

**Respuesta:**
```json
{
  "id": "copy_123456",
  "content": {
    "headline": "Transforma tu startup en una máquina de productividad",
    "subheadline": "La plataforma de gestión de proyectos que usan 10,000+ startups para escalar",
    "body": "¿Cansado de perder proyectos por falta de organización? Descubre la solución que...",
    "cta": "Comenzar Gratis Ahora",
    "features": [
      "Gestión de tareas intuitiva",
      "Colaboración en tiempo real",
      "Reportes automáticos"
    ]
  },
  "metadata": {
    "wordCount": 245,
    "estimatedReadTime": "1 min",
    "confidence": 0.92,
    "model": "gpt-4",
    "tokensUsed": 1250,
    "cost": 0.0375
  },
  "createdAt": "2024-01-15T10:30:00Z"
}
```

### Obtener Historial de Contenido

#### GET /copywriting/history

Obtiene el historial de contenido generado.

**Query Parameters:**
- `page`: Número de página (default: 1)
- `limit`: Elementos por página (default: 20, max: 100)
- `type`: Filtrar por tipo de contenido
- `dateFrom`: Fecha de inicio (ISO 8601)
- `dateTo`: Fecha de fin (ISO 8601)

**Ejemplo:**
```http
GET /copywriting/history?page=1&limit=20&type=landing_page&dateFrom=2024-01-01
```

**Respuesta:**
```json
{
  "data": [
    {
      "id": "copy_123456",
      "type": "landing_page",
      "title": "Landing page para gestión de proyectos",
      "createdAt": "2024-01-15T10:30:00Z",
      "wordCount": 245,
      "cost": 0.0375
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 150,
    "totalPages": 8
  }
}
```

### Optimizar Contenido

#### POST /copywriting/optimize

Optimiza contenido existente para mejor conversión.

**Parámetros:**
```json
{
  "contentId": "copy_123456",
  "optimizationType": "conversion" | "seo" | "readability" | "engagement",
  "targetMetrics": {
    "conversionRate": 0.15,
    "bounceRate": 0.30
  }
}
```

**Respuesta:**
```json
{
  "originalContent": "...",
  "optimizedContent": "...",
  "improvements": [
    {
      "type": "headline",
      "change": "Añadido beneficio específico",
      "impact": "Aumento estimado de conversión: +12%"
    }
  ],
  "confidence": 0.88
}
```

## 📊 Análisis de Propuestas APIs

### Analizar Propuesta

#### POST /analysis/proposal

Analiza una propuesta comercial para determinar factores de éxito/fracaso.

**Parámetros:**
```json
{
  "clientName": "TechCorp",
  "industry": "saas",
  "proposalValue": 150000,
  "timeline": 6,
  "proposalText": "Texto completo de la propuesta...",
  "clientFeedback": "Feedback del cliente...",
  "competitorInfo": {
    "name": "CompetitorX",
    "proposalValue": 120000,
    "timeline": 4
  },
  "outcome": "lost" | "won" | "pending"
}
```

**Ejemplo de Request:**
```json
{
  "clientName": "TechCorp",
  "industry": "saas",
  "proposalValue": 150000,
  "timeline": 6,
  "proposalText": "Propuesta para implementación de sistema CRM personalizado...",
  "clientFeedback": "La propuesta es sólida pero el timeline es muy largo...",
  "competitorInfo": {
    "name": "CompetitorX",
    "proposalValue": 120000,
    "timeline": 4
  },
  "outcome": "lost"
}
```

**Respuesta:**
```json
{
  "analysisId": "analysis_789012",
  "successProbability": 0.35,
  "mainIssues": [
    {
      "category": "Timeline",
      "problem": "8 meses vs 4 meses del competidor",
      "impact": "Alto",
      "recommendation": "Reducir timeline a 5-6 meses máximo"
    },
    {
      "category": "Pricing",
      "problem": "Estructura de pago poco flexible",
      "impact": "Medio",
      "recommendation": "Ofrecer pago mensual o por hitos"
    }
  ],
  "competitiveAnalysis": {
    "priceAdvantage": 0.15,
    "timelineAdvantage": 0.30,
    "experienceAdvantage": 0.25
  },
  "recommendations": [
    "Acortar timeline de implementación a 5-6 meses",
    "Implementar estructura de pago mensual",
    "Crear case studies específicos para industria software"
  ],
  "metadata": {
    "analysisTime": "2.3s",
    "model": "gpt-4",
    "confidence": 0.89,
    "tokensUsed": 2100,
    "cost": 0.063
  },
  "createdAt": "2024-01-15T11:45:00Z"
}
```

### Análisis Comparativo

#### POST /analysis/compare

Realiza análisis comparativo de múltiples propuestas.

**Parámetros:**
```json
{
  "dateRange": {
    "start": "2024-01-01",
    "end": "2024-03-31"
  },
  "industries": ["saas", "ecommerce", "fintech"],
  "minValue": 50000,
  "maxValue": 500000,
  "includeCompetitors": true
}
```

**Respuesta:**
```json
{
  "summary": {
    "totalProposals": 25,
    "wonProposals": 10,
    "lostProposals": 15,
    "winRate": 0.40,
    "averageValue": 125000
  },
  "industryBreakdown": {
    "saas": {
      "total": 10,
      "won": 6,
      "winRate": 0.60,
      "averageValue": 150000
    },
    "ecommerce": {
      "total": 8,
      "won": 2,
      "winRate": 0.25,
      "averageValue": 95000
    }
  },
  "successFactors": [
    "Timeline de 3-5 meses",
    "Pricing competitivo vs mercado",
    "Casos de éxito específicos en la industria"
  ],
  "recurringIssues": [
    "Timeline muy largo (>6 meses)",
    "Pricing superior al mercado (>15%)",
    "Falta de casos de éxito específicos"
  ],
  "recommendations": [
    "Enfocar esfuerzos en industrias con mayor tasa de éxito",
    "Desarrollar metodología estándar de 4-5 meses máximo",
    "Crear library de casos de éxito por industria"
  ]
}
```

### Generar Reporte

#### GET /analysis/reports/{reportId}

Genera reporte detallado de análisis.

**Query Parameters:**
- `format`: `json` | `pdf` | `excel`
- `includeCharts`: `true` | `false`
- `includeRecommendations`: `true` | `false`

**Ejemplo:**
```http
GET /analysis/reports/analysis_789012?format=pdf&includeCharts=true
```

**Respuesta (JSON):**
```json
{
  "reportId": "report_345678",
  "analysisId": "analysis_789012",
  "format": "pdf",
  "url": "https://reports.ia-marketing.com/report_345678.pdf",
  "expiresAt": "2024-01-22T11:45:00Z",
  "metadata": {
    "generatedAt": "2024-01-15T12:00:00Z",
    "pages": 8,
    "fileSize": "2.3MB"
  }
}
```

## 📈 Analytics APIs

### Métricas de Uso

#### GET /analytics/usage

Obtiene métricas de uso de la plataforma.

**Query Parameters:**
- `period`: `day` | `week` | `month` | `year`
- `dateFrom`: Fecha de inicio (ISO 8601)
- `dateTo`: Fecha de fin (ISO 8601)

**Ejemplo:**
```http
GET /analytics/usage?period=month&dateFrom=2024-01-01&dateTo=2024-01-31
```

**Respuesta:**
```json
{
  "period": "month",
  "dateRange": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": {
    "totalRequests": 15420,
    "copywritingRequests": 12350,
    "analysisRequests": 3070,
    "totalTokensUsed": 1250000,
    "totalCost": 375.50,
    "averageResponseTime": 2.3
  },
  "breakdown": {
    "byDay": [
      {
        "date": "2024-01-01",
        "requests": 450,
        "cost": 12.50
      }
    ],
    "byService": {
      "copywriting": {
        "requests": 12350,
        "cost": 300.25,
        "averageTokens": 95
      },
      "analysis": {
        "requests": 3070,
        "cost": 75.25,
        "averageTokens": 180
      }
    }
  }
}
```

### Métricas de Conversión

#### GET /analytics/conversion

Obtiene métricas de conversión de contenido generado.

**Query Parameters:**
- `contentType`: Tipo de contenido
- `dateFrom`: Fecha de inicio
- `dateTo`: Fecha de fin

**Respuesta:**
```json
{
  "contentType": "landing_page",
  "dateRange": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": {
    "totalGenerated": 150,
    "totalViews": 12500,
    "totalConversions": 1875,
    "conversionRate": 0.15,
    "averageBounceRate": 0.32,
    "averageTimeOnPage": 145
  },
  "topPerformers": [
    {
      "id": "copy_123456",
      "title": "Landing page para SaaS",
      "conversionRate": 0.22,
      "views": 850,
      "conversions": 187
    }
  ]
}
```

## 👥 User Management APIs

### Perfil de Usuario

#### GET /users/profile

Obtiene información del perfil del usuario.

**Respuesta:**
```json
{
  "id": "user_123456",
  "email": "usuario@ejemplo.com",
  "firstName": "Juan",
  "lastName": "Pérez",
  "subscriptionPlan": "professional",
  "subscriptionStatus": "active",
  "subscriptionExpiresAt": "2024-12-31T23:59:59Z",
  "usage": {
    "copywritingRequests": 150,
    "analysisRequests": 25,
    "tokensUsed": 50000,
    "cost": 150.00
  },
  "limits": {
    "copywritingRequests": 1000,
    "analysisRequests": 100,
    "tokensPerMonth": 100000
  },
  "createdAt": "2024-01-01T00:00:00Z"
}
```

### Actualizar Perfil

#### PUT /users/profile

Actualiza información del perfil del usuario.

**Parámetros:**
```json
{
  "firstName": "Juan",
  "lastName": "Pérez",
  "company": "Mi Empresa",
  "industry": "saas",
  "notifications": {
    "email": true,
    "push": false,
    "sms": false
  }
}
```

### Cambiar Plan de Suscripción

#### POST /users/subscription/change

Cambia el plan de suscripción del usuario.

**Parámetros:**
```json
{
  "plan": "enterprise",
  "billingCycle": "monthly" | "yearly",
  "paymentMethod": "card_1234567890"
}
```

**Respuesta:**
```json
{
  "subscriptionId": "sub_789012",
  "plan": "enterprise",
  "billingCycle": "monthly",
  "status": "active",
  "nextBillingDate": "2024-02-15T00:00:00Z",
  "amount": 299.00,
  "currency": "USD"
}
```

## 🔔 Notification APIs

### Enviar Notificación

#### POST /notifications/send

Envía notificación al usuario.

**Parámetros:**
```json
{
  "type": "email" | "push" | "sms",
  "template": "welcome" | "usage_limit" | "payment_failed",
  "recipient": "usuario@ejemplo.com",
  "data": {
    "name": "Juan",
    "usage": 85
  }
}
```

### Obtener Notificaciones

#### GET /notifications

Obtiene notificaciones del usuario.

**Query Parameters:**
- `page`: Número de página
- `limit`: Elementos por página
- `type`: Tipo de notificación
- `read`: `true` | `false` | `all`

**Respuesta:**
```json
{
  "data": [
    {
      "id": "notif_123456",
      "type": "email",
      "title": "Bienvenido a IA Marketing",
      "message": "Gracias por unirte a nuestra plataforma...",
      "read": false,
      "createdAt": "2024-01-15T10:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 45,
    "totalPages": 3
  }
}
```

## 🚨 Códigos de Error

### Códigos HTTP
- `200` - OK
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `429` - Too Many Requests
- `500` - Internal Server Error

### Códigos de Error Específicos
```json
{
  "error": {
    "code": "INVALID_API_KEY",
    "message": "API key inválida o expirada",
    "details": "Verifica que tu API key sea correcta y esté activa"
  }
}
```

**Códigos comunes:**
- `INVALID_API_KEY` - API key inválida
- `RATE_LIMIT_EXCEEDED` - Límite de requests excedido
- `INSUFFICIENT_CREDITS` - Créditos insuficientes
- `INVALID_REQUEST` - Request inválido
- `SERVICE_UNAVAILABLE` - Servicio no disponible

## 📝 Ejemplos de Uso

### JavaScript/Node.js
```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://api.ia-marketing.com/v1',
  headers: {
    'Authorization': 'Bearer tu_jwt_token',
    'Content-Type': 'application/json'
  }
});

// Generar contenido
async function generateContent() {
  try {
    const response = await api.post('/copywriting/generate', {
      type: 'landing_page',
      industry: 'saas',
      targetAudience: 'startups',
      tone: 'professional',
      prompt: 'Landing page para gestión de proyectos'
    });
    
    console.log(response.data);
  } catch (error) {
    console.error('Error:', error.response.data);
  }
}
```

### Python
```python
import requests

API_BASE = 'https://api.ia-marketing.com/v1'
HEADERS = {
    'Authorization': 'Bearer tu_jwt_token',
    'Content-Type': 'application/json'
}

def generate_content():
    url = f'{API_BASE}/copywriting/generate'
    data = {
        'type': 'landing_page',
        'industry': 'saas',
        'targetAudience': 'startups',
        'tone': 'professional',
        'prompt': 'Landing page para gestión de proyectos'
    }
    
    response = requests.post(url, json=data, headers=HEADERS)
    return response.json()
```

### cURL
```bash
curl -X POST https://api.ia-marketing.com/v1/copywriting/generate \
  -H "Authorization: Bearer tu_jwt_token" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "landing_page",
    "industry": "saas",
    "targetAudience": "startups",
    "tone": "professional",
    "prompt": "Landing page para gestión de proyectos"
  }'
```

## 🔄 Rate Limits

### Límites por Plan
- **Starter**: 100 requests/hora
- **Professional**: 500 requests/hora
- **Enterprise**: 2000 requests/hora

### Headers de Rate Limit
```http
X-RateLimit-Limit: 500
X-RateLimit-Remaining: 450
X-RateLimit-Reset: 1640995200
```

## 📞 Soporte

### Contacto
- **Email**: api-support@ia-marketing.com
- **Documentación**: https://docs.ia-marketing.com
- **Status Page**: https://status.ia-marketing.com

### Horarios
- **Lunes a Viernes**: 9:00 AM - 6:00 PM (GMT-5)
- **Respuesta promedio**: <2 horas
- **SLA**: 99.9% uptime

---

*"APIs que entienden tu negocio y escalan con tu crecimiento."* 🚀✨

