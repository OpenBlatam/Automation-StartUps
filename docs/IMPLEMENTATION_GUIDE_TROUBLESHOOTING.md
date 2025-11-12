# 🎯 Guía Completa de Implementación - Sistema de Troubleshooting

## Tabla de Contenidos

1. [Instalación](#instalación)
2. [Configuración](#configuración)
3. [Uso Básico](#uso-básico)
4. [Integraciones](#integraciones)
5. [Personalización](#personalización)
6. [Monitoreo](#monitoreo)
7. [Troubleshooting](#troubleshooting)

---

## Instalación

### Requisitos Previos

- Python 3.11+
- PostgreSQL 12+
- Node.js 18+ (para API REST)
- OpenAI API Key (opcional, para mejoras con LLM)

### Paso 1: Instalar Dependencias

```bash
# Python
pip install -r requirements.txt

# Node.js
cd web/kpis-next
npm install
```

### Paso 2: Configurar Base de Datos

```bash
# Ejecutar todos los esquemas en orden
psql $DATABASE_URL < data/db/support_troubleshooting_schema.sql
psql $DATABASE_URL < data/db/support_troubleshooting_feedback_schema.sql
psql $DATABASE_URL < data/db/support_webhooks_schema.sql
psql $DATABASE_URL < data/db/support_troubleshooting_advanced_schema.sql
psql $DATABASE_URL < data/db/support_troubleshooting_performance_schema.sql
```

### Paso 3: Configurar Variables de Entorno

```bash
# .env
DATABASE_URL=postgresql://user:pass@host:5432/dbname
OPENAI_API_KEY=sk-...  # Opcional
KESTRA_WEBHOOK_URL=https://kestra.example.com/...
SLACK_WEBHOOK_URL=https://hooks.slack.com/...  # Opcional
```

---

## Configuración

### Configuración Básica

```python
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

agent = TroubleshootingAgent(
    use_llm=True,  # Habilitar mejoras con LLM
    openai_api_key=os.getenv("OPENAI_API_KEY")
)
```

### Configuración Avanzada

```python
# Con webhooks
from data.integrations.support_troubleshooting_webhooks import (
    TroubleshootingWebhookManager,
    WebhookConfig,
    WebhookEvent
)

webhook_manager = TroubleshootingWebhookManager()
config = WebhookConfig(
    url="https://tu-sistema.com/webhook",
    events=[WebhookEvent.SESSION_STARTED, WebhookEvent.SESSION_RESOLVED],
    secret="tu-secret-key"
)
webhook_manager.register_webhook("mi-webhook", config)

# Con plantillas
from data.integrations.support_troubleshooting_templates import TroubleshootingTemplateManager

template_manager = TroubleshootingTemplateManager()
```

---

## Uso Básico

### Ejemplo 1: Flujo Completo

```python
from data.integrations.support_troubleshooting_agent import TroubleshootingAgent

# Inicializar
agent = TroubleshootingAgent()

# Iniciar sesión
session = agent.start_troubleshooting(
    problem_description="No puedo instalar el software",
    customer_email="cliente@example.com",
    customer_name="Juan Pérez",
    ticket_id="TKT-12345"
)

# Obtener primer paso
step = agent.get_current_step(session.session_id)
print(agent.format_step_response(step))

# Completar pasos
for i in range(3):
    result = agent.complete_step(
        session.session_id,
        success=True,
        notes=f"Paso {i+1} completado"
    )
    
    if result.get("status") == "resolved":
        break
    
    step = agent.get_current_step(session.session_id)
    print(agent.format_step_response(step))

# Recolectar feedback
feedback = agent.collect_feedback(
    session.session_id,
    rating=5,
    feedback_text="Muy útil",
    was_helpful=True
)
```

### Ejemplo 2: Integración con API REST

```python
import requests

BASE_URL = "http://localhost:3000/api/support/troubleshooting"

# Iniciar troubleshooting
response = requests.post(f"{BASE_URL}/start", json={
    "problem_description": "Error al conectarme",
    "customer_email": "cliente@example.com"
})
session = response.json()

# Completar paso
requests.post(
    f"{BASE_URL}/{session['session_id']}/step",
    json={"success": True, "step_number": 1}
)

# Obtener analytics
analytics = requests.get(f"{BASE_URL}/analytics?days=30").json()
print(f"Tasa de resolución: {analytics['summary']['resolution_rate']}%")
```

---

## Integraciones

### Integración con Sistema de Tickets

```python
# Cuando se crea un ticket
def on_ticket_created(ticket):
    agent = TroubleshootingAgent()
    
    session = agent.start_troubleshooting(
        problem_description=ticket.description,
        customer_email=ticket.customer_email,
        ticket_id=ticket.id
    )
    
    # Enviar primer paso al cliente
    step = agent.get_current_step(session.session_id)
    send_notification(ticket.customer_email, agent.format_step_response(step))
```

### Integración con Slack

```python
from data.integrations.support_troubleshooting_notifications import (
    TroubleshootingNotificationManager,
    NotificationConfig,
    NotificationChannel
)

manager = TroubleshootingNotificationManager()

# Notificar cuando se escala
config = NotificationConfig(
    channel=NotificationChannel.SLACK,
    recipient="#support-team",
    template="session_escalated",
    metadata={"webhook_url": os.getenv("SLACK_WEBHOOK_URL")}
)

manager.send_notification(config, {
    "customer_name": "Juan Pérez",
    "ticket_id": "TKT-12345",
    "problem_description": "Error crítico"
})
```

### Integración con Kestra Workflow

```yaml
# workflow/kestra/flows/support_troubleshooting_automation.yaml
# Ya está configurado para usar el agente automáticamente
# Solo necesitas llamar al webhook:

POST /api/v1/executions/webhook/workflows/workflows/support-troubleshooting-automation/support-troubleshooting
{
  "problem_description": "...",
  "customer_email": "..."
}
```

---

## Personalización

### Agregar Nuevo Problema a la Base de Conocimiento

Edita `data/integrations/support_troubleshooting_kb.json`:

```json
{
  "mi_nuevo_problema": {
    "problem_title": "Título del Problema",
    "problem_description": "Descripción del problema",
    "category": "categoría",
    "estimated_time": "15 minutos",
    "difficulty": "medio",
    "steps": [
      {
        "step_number": 1,
        "title": "Paso 1",
        "description": "Descripción del paso",
        "instructions": ["Instrucción 1", "Instrucción 2"],
        "expected_result": "Resultado esperado",
        "warnings": ["Precaución importante"],
        "resources": [
          {"title": "Recurso", "url": "https://..."}
        ]
      }
    ],
    "common_issues": ["Problema común 1"],
    "escalation_criteria": ["Cuándo escalar"]
  }
}
```

### Crear Plantilla Personalizada

```python
template_manager.create_template(
    template_id="mi_template",
    name="Mi Plantilla",
    description="Descripción",
    category="general",
    variables=[
        {
            "name": "variable1",
            "description": "Descripción de variable",
            "required": True,
            "type": "string"
        }
    ],
    steps_template=[
        {
            "step_number": 1,
            "title": "Paso con {{variable1}}",
            "description": "Descripción",
            "instructions": ["Instrucción 1"],
            "expected_result": "Resultado",
            "warnings": [],
            "resources": []
        }
    ]
)
```

---

## Monitoreo

### Métricas en Tiempo Real

```python
# Desde Python
analytics = agent.get_analytics(days=30)
print(f"Tasa de resolución: {analytics['resolution_rate']:.2f}%")
print(f"Rating promedio: {analytics['average_rating']:.2f}")

# Desde API REST
curl http://localhost:3000/api/support/troubleshooting/realtime
```

### Consultas SQL Útiles

```sql
-- Resumen diario
SELECT * FROM mv_daily_troubleshooting_summary
WHERE date >= CURRENT_DATE - INTERVAL '7 days';

-- Top problemas
SELECT * FROM mv_top_problems
ORDER BY total_sessions DESC
LIMIT 10;

-- Feedback por problema
SELECT * FROM mv_feedback_summary
ORDER BY avg_rating DESC;
```

### Mantenimiento Automático

```sql
-- Ejecutar mantenimiento diario
SELECT * FROM maintenance_troubleshooting_tables();

-- Refresh vistas materializadas
SELECT refresh_troubleshooting_views();

-- Limpiar cache expirado
SELECT cleanup_expired_cache();
```

---

## Troubleshooting

### Problema: No se detecta ningún problema

**Solución:**
1. Verifica que el problema existe en `support_troubleshooting_kb.json`
2. Revisa los logs: `logger.info` mostrará el score de matching
3. Ajusta el umbral de confianza si es necesario
4. Activa LLM para mejor detección: `use_llm=True`

### Problema: Webhooks no se disparan

**Solución:**
1. Verifica que el webhook está registrado: `GET /api/support/troubleshooting/webhooks`
2. Revisa los logs del webhook manager
3. Verifica la URL del webhook es accesible
4. Revisa la tabla `support_webhook_events` para ver intentos

### Problema: Performance lenta

**Solución:**
1. Ejecuta `REFRESH MATERIALIZED VIEW` en las vistas materializadas
2. Verifica índices: `SELECT * FROM pg_stat_user_indexes`
3. Ejecuta `VACUUM ANALYZE` en tablas grandes
4. Revisa queries lentas con `pg_stat_statements`

### Problema: Vistas materializadas desactualizadas

**Solución:**
```sql
-- Refresh manual
SELECT refresh_troubleshooting_views();

-- Configurar automático con pg_cron
SELECT cron.schedule(
    'refresh-views',
    '0 * * * *',
    'SELECT refresh_troubleshooting_views();'
);
```

---

## Mejores Prácticas

1. **Mantén la base de conocimiento actualizada**
   - Agrega problemas comunes que encuentres
   - Actualiza pasos basado en feedback

2. **Monitorea métricas regularmente**
   - Revisa tasa de resolución semanalmente
   - Identifica problemas que necesitan mejoras

3. **Usa webhooks para integraciones**
   - No hagas polling constante
   - Configura retry apropiado

4. **Optimiza performance**
   - Refresh vistas materializadas regularmente
   - Limpia datos antiguos
   - Monitorea índices

5. **Recolecta feedback**
   - Pide feedback después de resolver
   - Usa feedback para mejorar guías

---

## Recursos Adicionales

- [Documentación API](./API_TROUBLESHOOTING.md)
- [Optimizaciones de Performance](./TROUBLESHOOTING_PERFORMANCE_OPTIMIZATION.md)
- [Características Avanzadas](./TROUBLESHOOTING_ADVANCED_FEATURES.md)
- [Sistema Completo](./TROUBLESHOOTING_COMPLETE_SYSTEM.md)

---

**Versión**: 5.0.0  
**Última actualización**: 2025-01-27



