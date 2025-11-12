# 🚀 Mejoras Avanzadas del Sistema de Troubleshooting - v3.0

## Nuevas Funcionalidades Implementadas

### 1. 🔗 Sistema de Webhooks

#### Características
- **Registro de webhooks** para eventos específicos
- **Firma HMAC** para seguridad
- **Retry automático** con configuración personalizable
- **Historial completo** de eventos disparados
- **Estadísticas** de éxito/fallo

#### Eventos Soportados
- `session_started` - Cuando se inicia una sesión
- `step_completed` - Cuando se completa un paso exitosamente
- `step_failed` - Cuando un paso falla
- `session_resolved` - Cuando la sesión se resuelve
- `session_escalated` - Cuando se escala un ticket
- `feedback_received` - Cuando se recibe feedback
- `problem_detected` - Cuando se detecta un problema

#### Uso

```python
from data.integrations.support_troubleshooting_webhooks import (
    TroubleshootingWebhookManager,
    WebhookConfig,
    WebhookEvent
)

# Crear manager
webhook_manager = TroubleshootingWebhookManager()

# Registrar webhook
config = WebhookConfig(
    url="https://tu-sistema.com/webhook",
    events=[
        WebhookEvent.SESSION_STARTED,
        WebhookEvent.SESSION_RESOLVED,
        WebhookEvent.SESSION_ESCALATED
    ],
    secret="tu-secret-key",
    timeout=10,
    retry_attempts=3
)

webhook_manager.register_webhook("mi-webhook", config)

# Los webhooks se disparan automáticamente desde el agente
```

#### API REST

```bash
# Registrar webhook
POST /api/support/troubleshooting/webhooks
{
  "url": "https://example.com/webhook",
  "events": ["session_started", "session_resolved"],
  "secret": "optional-secret-key",
  "timeout": 10,
  "retry_attempts": 3
}

# Listar webhooks
GET /api/support/troubleshooting/webhooks

# Obtener estadísticas
GET /api/support/troubleshooting/webhooks/{webhook_id}/stats
```

### 2. 📝 Sistema de Plantillas Personalizables

#### Características
- **Plantillas reutilizables** con variables
- **Renderizado dinámico** de contenido
- **Validación de variables** requeridas
- **Categorización** de plantillas
- **Fácil creación** de nuevas plantillas

#### Plantillas Incluidas
- `reset_password_template` - Restablecer contraseña
- `api_integration_template` - Configurar integración API

#### Uso

```python
from data.integrations.support_troubleshooting_templates import (
    TroubleshootingTemplateManager
)

# Crear manager
template_manager = TroubleshootingTemplateManager()

# Listar plantillas
templates = template_manager.list_templates(category="cuenta")

# Renderizar plantilla
rendered = template_manager.render_template(
    template_id="reset_password_template",
    variables={
        "product_name": "Mi Aplicación",
        "reset_url": "https://app.com/reset",
        "support_email": "soporte@app.com"
    }
)

# Usar la guía renderizada
print(rendered["problem_title"])
print(rendered["steps"])
```

#### API REST

```bash
# Listar plantillas
GET /api/support/troubleshooting/templates?category=cuenta

# Obtener plantilla específica
GET /api/support/troubleshooting/templates?template_id=reset_password_template

# Renderizar plantilla
PUT /api/support/troubleshooting/templates
{
  "template_id": "reset_password_template",
  "variables": {
    "product_name": "Mi App",
    "reset_url": "https://app.com/reset"
  }
}

# Crear nueva plantilla
POST /api/support/troubleshooting/templates
{
  "template_id": "mi_template",
  "name": "Mi Plantilla",
  "description": "Descripción",
  "category": "general",
  "variables": [...],
  "steps_template": [...]
}
```

### 3. 📊 Integración con el Agente Principal

El agente principal ahora integra automáticamente:

```python
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

# El agente ahora incluye webhooks y plantillas automáticamente
agent = TroubleshootingAgent(
    use_llm=True,
    openai_api_key="sk-..."
)

# Los webhooks se disparan automáticamente en eventos importantes
session = agent.start_troubleshooting(...)
# → Webhook "session_started" se dispara automáticamente

agent.complete_step(session.session_id, success=True)
# → Webhook "step_completed" se dispara automáticamente
```

### 4. 🗄️ Esquemas de Base de Datos

#### Nuevas Tablas

**support_webhooks**
- Registro de webhooks configurados
- Configuración de eventos, retry, timeout
- Estado habilitado/deshabilitado

**support_webhook_events**
- Historial completo de eventos disparados
- Respuestas y códigos de estado
- Errores y mensajes

**Vistas**
- `vw_webhook_stats` - Estadísticas agregadas de webhooks

### 5. 🔐 Seguridad

#### Firma HMAC
Los webhooks pueden incluir firma HMAC para verificar autenticidad:

```python
config = WebhookConfig(
    url="https://example.com/webhook",
    secret="mi-secret-key",  # Para firma HMAC
    events=[...]
)
```

El payload incluye:
```json
{
  "event": "session_started",
  "timestamp": "2025-01-27T...",
  "data": {...},
  "signature": "hmac-sha256-signature"
}
```

### 6. 📈 Monitoreo y Estadísticas

#### Métricas de Webhooks
- Total de eventos disparados
- Tasa de éxito/fallo
- Último evento disparado
- Errores más comunes

#### Consultas SQL Útiles

```sql
-- Estadísticas de webhooks
SELECT * FROM vw_webhook_stats;

-- Eventos recientes de un webhook
SELECT * FROM support_webhook_events
WHERE webhook_id = 'wh_123'
ORDER BY triggered_at DESC
LIMIT 10;

-- Webhooks con mayor tasa de fallo
SELECT 
    webhook_id,
    url,
    success_rate,
    failed_events
FROM vw_webhook_stats
WHERE success_rate < 90
ORDER BY failed_events DESC;
```

## Ejemplos de Uso Completo

### Ejemplo 1: Integración con Slack

```python
# Registrar webhook para Slack
webhook_config = WebhookConfig(
    url="https://hooks.slack.com/services/YOUR/WEBHOOK/URL",
    events=[
        WebhookEvent.SESSION_ESCALATED,
        WebhookEvent.SESSION_RESOLVED
    ],
    headers={"Content-Type": "application/json"}
)

webhook_manager.register_webhook("slack-notifications", webhook_config)

# Los eventos se enviarán automáticamente a Slack
```

### Ejemplo 2: Crear Plantilla Personalizada

```python
# Crear plantilla para tu producto específico
template_manager.create_template(
    template_id="mi_producto_reset",
    name="Restablecer Contraseña - Mi Producto",
    description="Guía para restablecer contraseña en Mi Producto",
    category="cuenta",
    variables=[
        {
            "name": "product_name",
            "description": "Nombre del producto",
            "required": True,
            "type": "string"
        },
        {
            "name": "reset_url",
            "description": "URL de restablecimiento",
            "required": True,
            "type": "string"
        }
    ],
    steps_template=[
        {
            "step_number": 1,
            "title": "Ir a {{reset_url}}",
            "description": "Abre tu navegador y ve a {{reset_url}}",
            "instructions": [
                "Abre tu navegador",
                "Ve a {{reset_url}}",
                "Haz clic en 'Olvidé mi contraseña'"
            ],
            "expected_result": "Ves el formulario de restablecimiento",
            "warnings": [],
            "resources": []
        }
    ]
)

# Usar la plantilla
rendered = template_manager.render_template(
    "mi_producto_reset",
    {
        "product_name": "Mi Producto",
        "reset_url": "https://miproducto.com/reset"
    }
)
```

## Instalación

### 1. Ejecutar Esquemas SQL

```bash
psql $DATABASE_URL < data/db/support_webhooks_schema.sql
```

### 2. Configurar Variables de Entorno

```bash
# Para webhooks con firma
WEBHOOK_SECRET=tu-secret-key-aqui
```

### 3. Usar en el Código

```python
# Los módulos se importan automáticamente si están disponibles
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

agent = TroubleshootingAgent()
# Webhooks y plantillas están disponibles automáticamente
```

## Próximos Pasos

1. ✅ **Configurar webhooks** para tus sistemas externos
2. ✅ **Crear plantillas** personalizadas para tus productos
3. ✅ **Monitorear estadísticas** de webhooks
4. ✅ **Integrar con** Slack, Teams, Discord, etc.
5. ✅ **Personalizar respuestas** usando plantillas

## Beneficios

- 🔗 **Integración fácil** con sistemas externos
- 📝 **Reutilización** de guías comunes
- 🔐 **Seguridad** con firma HMAC
- 📊 **Visibilidad** completa de eventos
- ⚡ **Automatización** completa del flujo

---

**Versión**: 3.0.0  
**Última actualización**: 2025-01-27



