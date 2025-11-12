# API Documentation - Sistema de Troubleshooting

## Base URL
```
https://api.example.com/api/support/troubleshooting
```

## Autenticación
Todas las requests requieren autenticación mediante Bearer Token:
```
Authorization: Bearer YOUR_API_TOKEN
```

---

## Endpoints

### 1. Iniciar Sesión de Troubleshooting

**POST** `/start`

Inicia una nueva sesión de troubleshooting.

#### Request Body
```json
{
  "problem_description": "No puedo instalar el software",
  "customer_email": "cliente@example.com",
  "customer_name": "Juan Pérez",
  "ticket_id": "TKT-12345",
  "source": "web"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "session_id": "uuid-session-id",
  "ticket_id": "TKT-12345",
  "status": "started",
  "problem_detected": "instalacion_software",
  "problem_title": "Problemas con la instalación de software",
  "message": "Sesión iniciada correctamente",
  "first_step": {
    "step_number": 1,
    "title": "Verificar requisitos del sistema",
    "description": "...",
    "instructions": ["...", "..."],
    "warnings": ["..."],
    "resources": [{"title": "...", "url": "..."}],
    "expected_result": "...",
    "total_steps": 4,
    "current_step": 1,
    "estimated_time": "15-20 minutos",
    "difficulty": "fácil"
  }
}
```

---

### 2. Obtener Estado de Sesión

**GET** `/?session_id={session_id}`

Obtiene el estado actual de una sesión.

#### Query Parameters
- `session_id` (required): ID de la sesión

#### Response (200 OK)
```json
{
  "session": {
    "session_id": "uuid-session-id",
    "ticket_id": "TKT-12345",
    "customer_email": "cliente@example.com",
    "status": "in_progress",
    "current_step": 2,
    "total_steps": 4,
    "started_at": "2025-01-27T10:00:00Z"
  },
  "attempts": [
    {
      "id": 1,
      "step_number": 1,
      "success": true,
      "notes": "Completado correctamente",
      "attempted_at": "2025-01-27T10:05:00Z"
    }
  ],
  "summary": {
    "total_attempts": 1,
    "successful_attempts": 1,
    "failed_attempts": 0
  }
}
```

---

### 3. Completar Paso

**POST** `/{sessionId}/step`

Marca un paso como completado y avanza al siguiente.

#### Request Body
```json
{
  "success": true,
  "notes": "Paso completado exitosamente",
  "step_number": 1,
  "step_title": "Verificar requisitos del sistema"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "attempt": {
    "id": 1,
    "session_id": "uuid-session-id",
    "step_number": 1,
    "success": true,
    "notes": "Paso completado exitosamente"
  },
  "session": {
    "session_id": "uuid-session-id",
    "status": "in_progress",
    "current_step": 2
  },
  "next_action": "continue",
  "message": "Paso completado exitosamente. Continuando con el siguiente paso.",
  "suggest_escalation": false
}
```

---

### 4. Recolectar Feedback

**POST** `/{sessionId}/feedback`

Recolecta feedback del cliente sobre la sesión.

#### Request Body
```json
{
  "rating": 5,
  "feedback_text": "Muy útil, resolví mi problema",
  "was_helpful": true
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "feedback": {
    "id": 1,
    "session_id": "uuid-session-id",
    "rating": 5,
    "feedback_text": "Muy útil, resolví mi problema",
    "was_helpful": true,
    "collected_at": "2025-01-27T10:30:00Z"
  },
  "message": "Feedback recibido. ¡Gracias por tu opinión!"
}
```

---

### 5. Escalar Ticket

**POST** `/{sessionId}/escalate`

Escala un ticket a un agente humano.

#### Request Body
```json
{
  "reason": "Múltiples pasos fallidos después de seguir las instrucciones"
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "session_id": "uuid-session-id",
  "ticket_id": "TKT-12345",
  "status": "escalated",
  "escalation_info": {
    "reason": "Múltiples pasos fallidos",
    "attempted_steps": 3,
    "failed_steps": 2,
    "escalated_at": "2025-01-27T10:35:00Z"
  }
}
```

---

### 6. Obtener Analytics

**GET** `/analytics?days=30`

Obtiene métricas y estadísticas del sistema.

#### Query Parameters
- `days` (optional): Número de días hacia atrás (default: 30)

#### Response (200 OK)
```json
{
  "period_days": 30,
  "summary": {
    "total_sessions": 150,
    "resolved_sessions": 120,
    "escalated_sessions": 30,
    "resolution_rate": 80.0,
    "avg_duration_minutes": 18.5
  },
  "problem_distribution": [
    {
      "detected_problem_id": "instalacion_software",
      "detected_problem_title": "Problemas con la instalación",
      "total_sessions": 45,
      "resolved": 38,
      "escalated": 7,
      "resolution_rate": 84.44
    }
  ],
  "common_failed_steps": [
    {
      "step_number": 3,
      "step_title": "Ejecutar el instalador",
      "total_attempts": 50,
      "failed_attempts": 12,
      "failure_rate": 24.0
    }
  ],
  "feedback_summary": {
    "total_feedback": 100,
    "average_rating": 4.3,
    "helpful_percentage": 85.0
  }
}
```

---

### 7. Métricas en Tiempo Real

**GET** `/realtime`

Obtiene métricas en tiempo real del sistema.

#### Response (200 OK)
```json
{
  "timestamp": "2025-01-27T10:40:00Z",
  "metrics": {
    "active_sessions": 5,
    "resolved_last_hour": 12,
    "escalated_last_hour": 2,
    "avg_resolution_time_minutes": 18.5,
    "unique_problems_24h": 8,
    "avg_rating_24h": 4.3
  },
  "top_problems": [
    {
      "detected_problem_id": "instalacion_software",
      "detected_problem_title": "Problemas con la instalación",
      "count": 15,
      "resolved_count": 12
    }
  ],
  "active_sessions": [
    {
      "session_id": "uuid-1",
      "customer_email": "cliente1@example.com",
      "detected_problem_title": "Problemas con la instalación",
      "current_step": 2,
      "total_steps": 4,
      "status": "in_progress"
    }
  ]
}
```

---

### 8. Registrar Webhook

**POST** `/webhooks`

Registra un nuevo webhook para recibir eventos.

#### Request Body
```json
{
  "url": "https://example.com/webhook",
  "events": ["session_started", "session_resolved", "session_escalated"],
  "secret": "optional-secret-key",
  "timeout": 10,
  "retry_attempts": 3
}
```

#### Response (200 OK)
```json
{
  "success": true,
  "webhook_id": "wh_1234567890_abc123",
  "webhook": {
    "webhook_id": "wh_1234567890_abc123",
    "url": "https://example.com/webhook",
    "events": ["session_started", "session_resolved", "session_escalated"],
    "enabled": true,
    "created_at": "2025-01-27T10:00:00Z"
  },
  "message": "Webhook registrado exitosamente"
}
```

---

### 9. Listar Plantillas

**GET** `/templates?category=cuenta`

Lista plantillas disponibles.

#### Query Parameters
- `category` (optional): Filtrar por categoría
- `template_id` (optional): Obtener plantilla específica

#### Response (200 OK)
```json
{
  "templates": [
    {
      "template_id": "reset_password_template",
      "name": "Restablecer Contraseña",
      "description": "Guía para restablecer contraseña",
      "category": "cuenta",
      "variables_count": 3,
      "steps_count": 4
    }
  ]
}
```

---

### 10. Renderizar Plantilla

**PUT** `/templates`

Renderiza una plantilla con variables específicas.

#### Request Body
```json
{
  "template_id": "reset_password_template",
  "variables": {
    "product_name": "Mi Aplicación",
    "reset_url": "https://app.com/reset",
    "support_email": "soporte@app.com"
  }
}
```

#### Response (200 OK)
```json
{
  "rendered_template": {
    "problem_title": "Restablecer Contraseña - Mi Aplicación",
    "problem_description": "Guía paso a paso...",
    "category": "cuenta",
    "steps": [
      {
        "step_number": 1,
        "title": "Ir a la página de restablecimiento",
        "description": "Abre tu navegador y ve a https://app.com/reset",
        "instructions": ["...", "..."]
      }
    ]
  }
}
```

---

## Códigos de Error

### 400 Bad Request
Solicitud inválida o faltan parámetros requeridos.

```json
{
  "error": "problem_description and customer_email are required"
}
```

### 404 Not Found
Recurso no encontrado.

```json
{
  "error": "Session not found"
}
```

### 500 Internal Server Error
Error interno del servidor.

```json
{
  "error": "Internal server error",
  "details": "Error message here"
}
```

---

## Rate Limiting

El API tiene límites de rate:
- **100 requests/minuto** por IP
- **1000 requests/hora** por API key

Headers de respuesta incluyen información de límites:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1643209200
```

---

## Webhooks

### Payload de Webhook

```json
{
  "event": "session_started",
  "timestamp": "2025-01-27T10:00:00Z",
  "data": {
    "session_id": "uuid-session-id",
    "ticket_id": "TKT-12345",
    "customer_email": "cliente@example.com",
    "problem_description": "No puedo instalar el software",
    "detected_problem": "instalacion_software"
  },
  "signature": "hmac-sha256-signature-if-secret-configured"
}
```

### Eventos Disponibles

- `session_started` - Nueva sesión iniciada
- `step_completed` - Paso completado exitosamente
- `step_failed` - Paso falló
- `session_resolved` - Sesión resuelta
- `session_escalated` - Sesión escalada
- `feedback_received` - Feedback recibido
- `problem_detected` - Problema detectado

---

## Ejemplos de Uso

### Python

```python
import requests

BASE_URL = "https://api.example.com/api/support/troubleshooting"
HEADERS = {"Authorization": "Bearer YOUR_TOKEN"}

# Iniciar sesión
response = requests.post(
    f"{BASE_URL}/start",
    json={
        "problem_description": "No puedo instalar el software",
        "customer_email": "cliente@example.com"
    },
    headers=HEADERS
)
session = response.json()

# Completar paso
requests.post(
    f"{BASE_URL}/{session['session_id']}/step",
    json={"success": True, "step_number": 1},
    headers=HEADERS
)
```

### cURL

```bash
# Iniciar sesión
curl -X POST https://api.example.com/api/support/troubleshooting/start \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "problem_description": "No puedo instalar el software",
    "customer_email": "cliente@example.com"
  }'

# Obtener estado
curl https://api.example.com/api/support/troubleshooting/?session_id=UUID \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Changelog

### v4.0.0
- Agregado sistema de webhooks
- Agregado sistema de plantillas
- Agregado analytics avanzado
- Agregado métricas en tiempo real

### v3.0.0
- Agregado sistema de feedback
- Mejoras en detección con LLM
- Respuestas personalizadas

### v2.0.0
- Sistema base de troubleshooting
- Guía paso a paso
- Integración con tickets



