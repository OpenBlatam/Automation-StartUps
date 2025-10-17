# Documentación de API - Blatam Platform

## 🔌 API Overview

### Información General
- **Base URL**: `https://api.blatam.com/v1`
- **Autenticación**: Bearer Token
- **Formato**: JSON
- **Rate Limiting**: 1000 requests/hour
- **Versión**: v1.0

### Autenticación
```bash
# Obtener token de acceso
curl -X POST https://api.blatam.com/v1/auth/token \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@empresa.com",
    "password": "tu_password"
  }'

# Usar token en requests
curl -X GET https://api.blatam.com/v1/courses \
  -H "Authorization: Bearer tu_token_aqui"
```

## 🎓 Curso de IA - API Endpoints

### Estudiantes

#### Obtener Lista de Estudiantes
```bash
GET /courses/students
```

**Parámetros**:
- `page` (opcional): Número de página (default: 1)
- `limit` (opcional): Elementos por página (default: 50)
- `status` (opcional): Estado del estudiante (active, completed, paused)

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "students": [
      {
        "id": "stu_123",
        "name": "Juan Pérez",
        "email": "juan@empresa.com",
        "status": "active",
        "progress": 75,
        "enrollment_date": "2024-12-01",
        "last_activity": "2024-12-15T10:30:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 150,
      "pages": 3
    }
  }
}
```

#### Obtener Detalles de Estudiante
```bash
GET /courses/students/{student_id}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "stu_123",
    "name": "Juan Pérez",
    "email": "juan@empresa.com",
    "status": "active",
    "progress": {
      "overall": 75,
      "modules": {
        "module_1": 100,
        "module_2": 80,
        "module_3": 60,
        "module_4": 0
      }
    },
    "grades": {
      "average": 87,
      "quizzes": [
        {
          "id": "quiz_1",
          "score": 92,
          "date": "2024-12-10"
        }
      ]
    },
    "enrollment_date": "2024-12-01",
    "last_activity": "2024-12-15T10:30:00Z"
  }
}
```

#### Crear Nuevo Estudiante
```bash
POST /courses/students
```

**Body**:
```json
{
  "name": "María García",
  "email": "maria@empresa.com",
  "company": "TechCorp",
  "plan": "professional"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "stu_124",
    "name": "María García",
    "email": "maria@empresa.com",
    "status": "active",
    "enrollment_date": "2024-12-15",
    "access_token": "token_para_estudiante"
  }
}
```

### Progreso y Calificaciones

#### Obtener Progreso de Estudiante
```bash
GET /courses/students/{student_id}/progress
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "student_id": "stu_123",
    "overall_progress": 75,
    "modules": [
      {
        "id": "module_1",
        "name": "Fundamentos de IA",
        "progress": 100,
        "completed_at": "2024-12-10"
      },
      {
        "id": "module_2",
        "name": "Machine Learning",
        "progress": 80,
        "current_lesson": "lesson_15"
      }
    ],
    "estimated_completion": "2025-02-15"
  }
}
```

#### Obtener Calificaciones
```bash
GET /courses/students/{student_id}/grades
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "student_id": "stu_123",
    "overall_average": 87,
    "grades": [
      {
        "id": "quiz_1",
        "name": "Quiz Semana 1",
        "score": 92,
        "max_score": 100,
        "date": "2024-12-10",
        "module": "module_1"
      }
    ]
  }
}
```

## 🚀 SaaS Marketing AI - API Endpoints

### Campañas

#### Obtener Lista de Campañas
```bash
GET /marketing/campaigns
```

**Parámetros**:
- `status` (opcional): Estado de campaña (active, paused, completed)
- `type` (opcional): Tipo de campaña (awareness, conversion, retention)

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "campaigns": [
      {
        "id": "camp_123",
        "name": "Holiday Sale 2024",
        "type": "conversion",
        "status": "active",
        "budget": 5000,
        "spent": 3200,
        "roi": 1456,
        "start_date": "2024-12-01",
        "end_date": "2024-12-31"
      }
    ]
  }
}
```

#### Crear Nueva Campaña
```bash
POST /marketing/campaigns
```

**Body**:
```json
{
  "name": "Q1 Lead Generation",
  "type": "conversion",
  "budget": 3000,
  "objectives": ["leads", "conversions"],
  "audiences": ["lookalike_1", "retargeting"],
  "channels": ["facebook", "google", "linkedin"],
  "start_date": "2025-01-01",
  "end_date": "2025-03-31"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "camp_124",
    "name": "Q1 Lead Generation",
    "status": "active",
    "created_at": "2024-12-15T10:30:00Z"
  }
}
```

#### Obtener Métricas de Campaña
```bash
GET /marketing/campaigns/{campaign_id}/metrics
```

**Parámetros**:
- `start_date` (opcional): Fecha de inicio
- `end_date` (opcional): Fecha de fin
- `granularity` (opcional): daily, weekly, monthly

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "campaign_id": "camp_123",
    "period": {
      "start_date": "2024-12-01",
      "end_date": "2024-12-15"
    },
    "metrics": {
      "impressions": 2300000,
      "clicks": 87400,
      "conversions": 3670,
      "spent": 3200,
      "roi": 1456,
      "roas": 4.8,
      "ctr": 3.8,
      "cvr": 4.2
    },
    "daily_breakdown": [
      {
        "date": "2024-12-01",
        "impressions": 150000,
        "clicks": 5800,
        "conversions": 245,
        "spent": 210
      }
    ]
  }
}
```

### Audiencias

#### Obtener Lista de Audiencias
```bash
GET /marketing/audiences
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "audiences": [
      {
        "id": "aud_123",
        "name": "Lookalike 1%",
        "type": "lookalike",
        "size": 45000,
        "performance": {
          "ctr": 4.2,
          "cvr": 5.1,
          "roas": 4.8
        }
      }
    ]
  }
}
```

#### Crear Nueva Audiencia
```bash
POST /marketing/audiences
```

**Body**:
```json
{
  "name": "High Value Customers",
  "type": "custom",
  "criteria": {
    "lifetime_value": ">500",
    "purchase_frequency": ">3",
    "last_purchase": "<30_days"
  }
}
```

### Automatizaciones

#### Obtener Lista de Automatizaciones
```bash
GET /marketing/automations
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "automations": [
      {
        "id": "auto_123",
        "name": "Lead Nurturing",
        "type": "email",
        "status": "active",
        "efficiency": 94,
        "conversion_rate": 12
      }
    ]
  }
}
```

#### Crear Nueva Automatización
```bash
POST /marketing/automations
```

**Body**:
```json
{
  "name": "Welcome Series",
  "type": "email",
  "trigger": "new_lead",
  "actions": [
    {
      "type": "send_email",
      "template": "welcome_1",
      "delay": "immediate"
    },
    {
      "type": "send_email",
      "template": "welcome_2",
      "delay": "1_day"
    }
  ]
}
```

## 📄 AI Bulk Documents - API Endpoints

### Documentos

#### Generar Documento
```bash
POST /documents/generate
```

**Body**:
```json
{
  "type": "proposal",
  "title": "Propuesta de Servicios",
  "content": {
    "company": "TechCorp",
    "services": ["desarrollo", "consultoría"],
    "budget": 50000,
    "timeline": "3 meses"
  },
  "format": "pdf",
  "style": "professional",
  "length": "medium"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "doc_123",
    "title": "Propuesta de Servicios",
    "type": "proposal",
    "status": "completed",
    "content": "Contenido del documento...",
    "download_url": "https://api.blatam.com/v1/documents/doc_123/download",
    "created_at": "2024-12-15T10:30:00Z",
    "processing_time": 2.3
  }
}
```

#### Obtener Lista de Documentos
```bash
GET /documents
```

**Parámetros**:
- `type` (opcional): Tipo de documento
- `status` (opcional): Estado (processing, completed, failed)
- `date_from` (opcional): Fecha de inicio
- `date_to` (opcional): Fecha de fin

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "documents": [
      {
        "id": "doc_123",
        "title": "Propuesta de Servicios",
        "type": "proposal",
        "status": "completed",
        "created_at": "2024-12-15T10:30:00Z",
        "processing_time": 2.3,
        "quality_score": 9.4
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 50,
      "total": 150,
      "pages": 3
    }
  }
}
```

#### Obtener Detalles de Documento
```bash
GET /documents/{document_id}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "id": "doc_123",
    "title": "Propuesta de Servicios",
    "type": "proposal",
    "status": "completed",
    "content": "Contenido completo del documento...",
    "metadata": {
      "word_count": 1250,
      "page_count": 3,
      "quality_score": 9.4,
      "processing_time": 2.3
    },
    "download_url": "https://api.blatam.com/v1/documents/doc_123/download",
    "created_at": "2024-12-15T10:30:00Z"
  }
}
```

### Templates

#### Obtener Lista de Templates
```bash
GET /documents/templates
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "templates": [
      {
        "id": "tpl_123",
        "name": "Propuesta Comercial",
        "type": "proposal",
        "category": "business",
        "description": "Template para propuestas comerciales",
        "usage_count": 456,
        "rating": 9.6
      }
    ]
  }
}
```

#### Crear Template Personalizado
```bash
POST /documents/templates
```

**Body**:
```json
{
  "name": "Reporte Ejecutivo",
  "type": "report",
  "category": "business",
  "description": "Template para reportes ejecutivos",
  "content": "Estructura del template...",
  "variables": ["company", "period", "metrics"]
}
```

## 📊 Métricas y Analytics - API Endpoints

### Métricas Generales

#### Obtener Métricas del Ecosistema
```bash
GET /analytics/ecosystem
```

**Parámetros**:
- `period` (opcional): daily, weekly, monthly, yearly
- `start_date` (opcional): Fecha de inicio
- `end_date` (opcional): Fecha de fin

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "period": {
      "start_date": "2024-12-01",
      "end_date": "2024-12-15"
    },
    "metrics": {
      "total_revenue": 2400000,
      "active_users": 15847,
      "satisfaction": 9.3,
      "roi_average": 1247
    },
    "breakdown": {
      "course_ia": {
        "revenue": 812000,
        "users": 3247,
        "satisfaction": 9.4
      },
      "saas_marketing": {
        "revenue": 1200000,
        "users": 1247,
        "satisfaction": 9.2
      },
      "ai_bulk": {
        "revenue": 388000,
        "users": 11353,
        "satisfaction": 9.4
      }
    }
  }
}
```

### Reportes

#### Generar Reporte Personalizado
```bash
POST /analytics/reports
```

**Body**:
```json
{
  "name": "Reporte Q4 2024",
  "type": "executive",
  "services": ["course_ia", "saas_marketing", "ai_bulk"],
  "metrics": ["revenue", "users", "satisfaction", "roi"],
  "period": {
    "start_date": "2024-10-01",
    "end_date": "2024-12-31"
  },
  "format": "pdf"
}
```

**Respuesta**:
```json
{
  "success": true,
  "data": {
    "report_id": "rpt_123",
    "name": "Reporte Q4 2024",
    "status": "processing",
    "estimated_completion": "2024-12-15T11:00:00Z"
  }
}
```

## 🔧 Webhooks

### Configurar Webhook
```bash
POST /webhooks
```

**Body**:
```json
{
  "url": "https://tu-servidor.com/webhook",
  "events": ["student_completed", "campaign_optimized", "document_generated"],
  "secret": "tu_secreto_webhook"
}
```

### Eventos Disponibles

#### Curso de IA
- `student_enrolled`: Estudiante se inscribió
- `student_completed`: Estudiante completó módulo
- `student_certified`: Estudiante obtuvo certificación

#### SaaS Marketing
- `campaign_created`: Campaña creada
- `campaign_optimized`: Campaña optimizada
- `automation_triggered`: Automatización activada

#### AI Bulk Documents
- `document_generated`: Documento generado
- `document_downloaded`: Documento descargado
- `template_created`: Template creado

### Payload de Webhook
```json
{
  "event": "student_completed",
  "timestamp": "2024-12-15T10:30:00Z",
  "data": {
    "student_id": "stu_123",
    "module_id": "module_2",
    "completion_date": "2024-12-15T10:30:00Z"
  }
}
```

## 🚨 Códigos de Error

### Códigos HTTP
- `200`: Éxito
- `400`: Bad Request - Parámetros inválidos
- `401`: Unauthorized - Token inválido
- `403`: Forbidden - Sin permisos
- `404`: Not Found - Recurso no encontrado
- `429`: Too Many Requests - Rate limit excedido
- `500`: Internal Server Error - Error del servidor

### Códigos de Error Personalizados
```json
{
  "success": false,
  "error": {
    "code": "INVALID_PARAMETERS",
    "message": "Los parámetros proporcionados son inválidos",
    "details": {
      "field": "email",
      "reason": "Formato de email inválido"
    }
  }
}
```

## 📚 SDKs y Librerías

### Python SDK
```bash
pip install blatam-sdk
```

```python
from blatam import BlatamClient

client = BlatamClient(api_key="tu_api_key")

# Obtener estudiantes
students = client.courses.get_students()

# Generar documento
document = client.documents.generate(
    type="proposal",
    title="Propuesta de Servicios",
    content={"company": "TechCorp"}
)
```

### JavaScript SDK
```bash
npm install blatam-sdk
```

```javascript
const BlatamClient = require('blatam-sdk');

const client = new BlatamClient('tu_api_key');

// Obtener campañas
const campaigns = await client.marketing.getCampaigns();

// Generar documento
const document = await client.documents.generate({
  type: 'proposal',
  title: 'Propuesta de Servicios',
  content: { company: 'TechCorp' }
});
```

### PHP SDK
```bash
composer require blatam/sdk
```

```php
use Blatam\BlatamClient;

$client = new BlatamClient('tu_api_key');

// Obtener métricas
$metrics = $client->analytics->getEcosystemMetrics();

// Crear campaña
$campaign = $client->marketing->createCampaign([
    'name' => 'Q1 Lead Generation',
    'type' => 'conversion',
    'budget' => 3000
]);
```

## 🔒 Seguridad

### Autenticación
- **Bearer Token**: Incluir en header `Authorization`
- **API Key**: Incluir en header `X-API-Key`
- **Rate Limiting**: 1000 requests/hour por API key

### Encriptación
- **HTTPS**: Todas las comunicaciones encriptadas
- **TLS 1.3**: Protocolo de encriptación
- **JWT**: Tokens de autenticación firmados

### Permisos
- **Read**: Lectura de datos
- **Write**: Escritura de datos
- **Admin**: Acceso completo

---

*Documentación de API actualizada: Diciembre 2024*
