# Sistema de Automatización de Soporte al Cliente / Tickets

Sistema completo para automatizar el procesamiento de tickets de soporte con chatbot para FAQs, priorización automática y enrutamiento inteligente.

## 📋 Descripción

Este sistema automatiza el procesamiento de tickets de soporte mediante:

1. **Chatbot para FAQs**: Responde automáticamente consultas frecuentes usando búsqueda en base de datos y LLM (OpenAI)
2. **Priorización Automática**: Calcula prioridad (low/medium/high/urgent/critical) basada en múltiples factores
3. **Enrutamiento Inteligente**: Dirige tickets a departamentos y agentes apropiados según reglas configurables

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Ticket Source  │  (Email, Web, Chat, API, WhatsApp)
│   (Webhook)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validación y   │
│  Normalización  │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
    ▼        ▼
┌─────────┐ ┌──────────────┐
│ Chatbot │ │ Priorización │
│ (FAQs)  │ │  Automática   │
└────┬────┘ └───────┬───────┘
     │              │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Enrutamiento │
     │  Inteligente │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Persistencia │
     │  (PostgreSQL) │
     └──────┬───────┘
            │
            ▼
     ┌──────────────┐
     │ Notificaciones│
     │ (Slack/Teams) │
     └──────────────┘
```

## 📁 Componentes

### 1. Esquema de Base de Datos

**Archivo**: `data/db/support_tickets_schema.sql`

Tablas principales:
- `support_tickets`: Tickets con toda la información
- `support_chatbot_interactions`: Historial de interacciones con chatbot
- `support_faq_articles`: Artículos de FAQ
- `support_ticket_history`: Historial de cambios
- `support_agents`: Agentes y su capacidad
- `support_routing_rules`: Reglas de enrutamiento configurables

### 2. Módulos Python

#### `support_chatbot.py`
- Búsqueda de FAQs en base de datos
- Integración con OpenAI para respuestas contextuales
- Detección de intenciones
- Escalación automática cuando no puede resolver

#### `support_priority.py`
- Cálculo de score de prioridad (0-100)
- Análisis de urgencia del contenido
- Consideración del tipo de cliente (VIP, Enterprise)
- Historial de tickets del cliente

#### `support_routing.py`
- Enrutamiento basado en reglas configurables
- Asignación automática a agentes disponibles
- Balanceo de carga entre agentes
- Matching de especialidades

### 3. Workflow de Kestra

**Archivo**: `workflow/kestra/flows/support_ticket_automation.yaml`

Fases:
1. Validación y normalización
2. Procesamiento con chatbot
3. Cálculo de prioridad
4. Enrutamiento inteligente
5. Persistencia en BD
6. Guardado de interacción con chatbot
7. Sincronización con HubSpot (opcional)
8. Notificaciones
9. Resumen final

## 🚀 Configuración

### 1. Crear Esquema de Base de Datos

```bash
psql -U postgres -d your_database -f data/db/support_tickets_schema.sql
```

### 2. Configurar Variables de Entorno

```bash
# Base de datos
export DB_HOST=postgres.example.com
export DB_NAME=support_db
export DB_USER=support_user
export DB_PASSWORD=your_password

# OpenAI (opcional, para chatbot avanzado)
export OPENAI_API_KEY=sk-...
```

### 3. Crear Artículos de FAQ

```sql
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords
) VALUES (
    'faq-001',
    '¿Cómo restablezco mi contraseña?',
    'Para restablecer tu contraseña, ve a la página de login y haz clic en "Olvidé mi contraseña"...',
    'Instrucciones para restablecer contraseña',
    'account',
    ARRAY['password', 'login', 'account'],
    ARRAY['contraseña', 'password', 'reset', 'olvidé']
);
```

### 4. Configurar Agentes

```sql
INSERT INTO support_agents (
    agent_id,
    agent_name,
    email,
    department,
    specialties,
    max_concurrent_tickets,
    is_available
) VALUES (
    'agent-001',
    'Juan Pérez',
    'juan@example.com',
    'technical',
    ARRAY['billing', 'technical'],
    5,
    true
);
```

### 5. Crear Reglas de Enrutamiento

```sql
INSERT INTO support_routing_rules (
    rule_name,
    priority_order,
    conditions,
    target_department,
    target_specialties,
    auto_assign,
    is_active
) VALUES (
    'Billing Issues',
    1,
    '{"category": "billing"}'::jsonb,
    'billing',
    ARRAY['billing'],
    false,
    true
);
```

## 📡 Uso del Webhook

### Endpoint

```
POST https://kestra.example.com/api/v1/executions/webhook/workflows/support_ticket_automation/support-ticket
```

### Payload Ejemplo

```json
{
  "ticket_id": "optional-uuid",
  "source": "web",
  "subject": "Problema con mi factura",
  "description": "No puedo descargar mi factura del mes pasado",
  "customer_email": "cliente@example.com",
  "customer_name": "Juan Pérez",
  "customer_id": "hubspot-contact-id",
  "category": "billing",
  "tags": ["factura", "descarga"],
  "metadata": {
    "browser": "Chrome",
    "ip": "192.168.1.1"
  }
}
```

### Respuesta

```json
{
  "ticket_id": "generated-uuid",
  "status": "chatbot_handled",
  "chatbot": {
    "attempted": true,
    "resolved": true,
    "confidence": 0.85
  },
  "priority": {
    "level": "medium",
    "score": 45.5
  },
  "routing": {
    "department": "billing",
    "agent_assigned": false
  }
}
```

## 🤖 Chatbot

El chatbot intenta resolver consultas automáticamente:

1. **Búsqueda de FAQs**: Busca en base de datos artículos relevantes
2. **Respuesta con LLM**: Si hay FAQs relevantes, usa OpenAI para formatear respuesta
3. **Sin FAQs**: Intenta responder con LLM directamente
4. **Escalación**: Si la confianza es baja, escalar a agente humano

### Configuración

```yaml
inputs:
  enable_chatbot: true
  openai_api_key: "sk-..."
  openai_model: "gpt-4o-mini"
  chatbot_confidence_threshold: 0.7
```

### Umbral de Confianza

- **≥ 0.7**: Resuelto por chatbot
- **< 0.7**: Escalar a agente humano

## 🎯 Priorización Automática

El sistema calcula un score de prioridad (0-100) basado en:

### Factores

1. **Urgencia del Contenido** (0-40 puntos)
   - Palabras críticas: "crash", "down", "emergencia"
   - Palabras urgentes: "urgente", "asap", "inmediato"
   - Problemas detectados: "error", "bug", "no funciona"

2. **Tier del Cliente** (0-15 puntos)
   - Cliente VIP: +15 puntos
   - Cliente Enterprise: +12 puntos
   - Cliente frecuente con tickets urgentes: +5 puntos

3. **Sensibilidad Temporal** (0-5 puntos)
   - Deadlines, fechas importantes

4. **Boost por Categoría**
   - Billing: +5 puntos
   - Technical: +3 puntos
   - Security: +15 puntos

5. **Boost por Fuente**
   - Phone: +5 puntos
   - Chat: +2 puntos

### Niveles de Prioridad

- **Critical**: Score ≥ 85
- **Urgent**: Score ≥ 70
- **High**: Score ≥ 55
- **Medium**: Score ≥ 40
- **Low**: Score < 40

## 🧭 Enrutamiento Inteligente

El sistema enruta tickets según:

1. **Reglas Configurables**: Se evalúan en orden de prioridad
2. **Categoría por Defecto**: Si no hay regla, usa mapeo de categorías
3. **Prioridad**: Fallback a enrutamiento por prioridad

### Asignación Automática de Agentes

Si `enable_auto_assign=true`:
- Busca agente disponible en el departamento
- Considera especialidades requeridas
- Balancea carga (menos tickets activos primero)
- Respeta límite de tickets concurrentes

## 📊 Métricas y Monitoreo

### Vistas Útiles

```sql
-- Tickets pendientes por prioridad
SELECT * FROM v_support_tickets_pending;

-- Estadísticas de chatbot
SELECT * FROM v_support_chatbot_stats;

-- Carga de trabajo por agente
SELECT * FROM v_support_agents_workload;
```

### KPIs Recomendados

- **Tasa de Resolución por Chatbot**: % de tickets resueltos automáticamente
- **Tiempo Promedio de Primera Respuesta**: Para tickets no resueltos por chatbot
- **Distribución de Prioridades**: Porcentaje de tickets por nivel
- **Carga de Agentes**: Tickets activos por agente

## 🔧 Integraciones

### HubSpot

Si `enable_hubspot_sync=true`:
- Crea ticket en HubSpot
- Asocia con contacto existente
- Sincroniza prioridad y estado

### Slack/Teams

Notificaciones opcionales cuando:
- Se crea nuevo ticket
- Ticket escalado a agente
- Ticket resuelto por chatbot

## 📝 Ejemplos de Uso

### Ticket Resuelto por Chatbot

```json
{
  "description": "¿Cómo restablezco mi contraseña?",
  "customer_email": "cliente@example.com"
}
```

Resultado:
- Chatbot encuentra FAQ relevante
- Responde con instrucciones
- Status: `chatbot_handled`
- No requiere enrutamiento

### Ticket Urgente

```json
{
  "subject": "URGENTE: Sistema caído",
  "description": "El sistema no funciona, necesito ayuda inmediata",
  "customer_email": "vip@example.com",
  "source": "phone"
}
```

Resultado:
- Prioridad: `critical` (score: 92)
- Enrutado a: `technical`
- Asignado a agente disponible automáticamente

### Ticket de Facturación

```json
{
  "subject": "Problema con factura",
  "description": "No puedo descargar mi factura",
  "category": "billing",
  "customer_email": "cliente@example.com"
}
```

Resultado:
- Enrutado a: `billing` (por categoría)
- Prioridad: `medium` (score: 45)
- Esperando asignación manual

## 🛠️ Troubleshooting

### Chatbot no responde

1. Verificar conexión a BD
2. Verificar que hay FAQs en la base de datos
3. Verificar API key de OpenAI
4. Revisar logs de Kestra

### Priorización incorrecta

1. Verificar factores calculados en `urgency_factors`
2. Ajustar pesos en `support_priority.py`
3. Revisar configuración de VIP/Enterprise customers

### Enrutamiento incorrecto

1. Verificar reglas en `support_routing_rules`
2. Verificar que hay agentes disponibles
3. Revisar especialidades requeridas

## 📊 Monitoreo y Alertas

### DAG de Airflow

**Archivo**: `data/airflow/dags/support_tickets_monitor.py`

El DAG se ejecuta cada 15 minutos y monitorea:
- Tickets pendientes por prioridad
- Tasa de resolución por chatbot
- Tiempo promedio de primera respuesta
- SLA compliance (tickets críticos > 24h)
- Carga de trabajo de agentes
- Alertas automáticas a Slack

**Métricas registradas:**
- `support_tickets.unassigned_critical`: Tickets críticos sin asignar
- `support_tickets.chatbot_resolution_rate`: % resuelto por chatbot
- `support_tickets.avg_first_response_minutes`: Tiempo promedio
- `support_tickets.sla_breaches_critical`: Violaciones de SLA

**Alertas automáticas:**
- Tickets críticos sin asignar > 5 minutos
- Tickets críticos abiertos > 24h (SLA breach)
- Tasa de resolución por chatbot < 50%
- Agentes con utilización > 90%
- Tiempo de primera respuesta > 60 minutos

## 🗄️ Datos de Ejemplo

### FAQs de Ejemplo

**Archivo**: `data/db/support_faq_seed.sql`

Contiene 6 artículos de FAQ de ejemplo:
- Restablecer contraseña
- Descargar facturas
- Problemas técnicos (sistema lento)
- Cambiar plan de suscripción
- Cancelar cuenta
- Política de reembolsos

Para cargar:
```bash
psql -U postgres -d your_db -f data/db/support_faq_seed.sql
```

### Script de Setup

**Archivo**: `scripts/support_setup_example.py`

Script Python para configurar:
- 5 agentes de soporte de ejemplo
- 5 reglas de enrutamiento
- Verificación del setup

Uso:
```bash
export DB_HOST=localhost
export DB_NAME=support_db
export DB_USER=postgres
export DB_PASSWORD=your_password
python scripts/support_setup_example.py
```

## 🔼 Escalación Automática

### Workflow de Escalación

**Archivo**: `workflow/kestra/flows/support_ticket_escalation.yaml`

Escala tickets automáticamente cuando:
- Tickets críticos/urgentes sin respuesta > 15-30 minutos
- Tickets abiertos > 24-48 horas
- Tickets en progreso sin actualización > 2 horas
- Cliente VIP con ticket sin resolver

**Acciones automáticas:**
- Aumentar prioridad (low → medium → high → urgent → critical)
- Reasignar a agente senior disponible
- Notificar a supervisores
- Registrar en historial

**Configuración:**
- Se ejecuta cada 10 minutos automáticamente
- Reglas de escalación configurables en BD

### Módulo de Escalación

**Archivo**: `workflow/kestra/flows/lib/support_escalation.py`

Funcionalidades:
- Búsqueda de agentes senior por departamento
- Aumento inteligente de prioridad
- Reasignación automática
- Registro de acciones en historial

## 📊 Reportes Automatizados

### DAG de Reportes

**Archivo**: `data/airflow/dags/support_tickets_reports.py`

Genera reportes semanales (lunes 9 AM) con:
- Métricas de rendimiento
- Tasa de resolución por chatbot
- Tiempos de respuesta promedio
- SLA compliance
- Distribución por prioridad/categoría
- Top agentes por rendimiento

**Envío:**
- Email a destinatarios configurados
- Notificación a Slack
- Formato HTML y texto plano

## 📧 Templates de Email

### Módulo de Templates

**Archivo**: `workflow/kestra/flows/lib/support_email_templates.py`

Templates disponibles:
1. **Confirmación de ticket**: Cuando se crea un ticket
2. **Respuesta del chatbot**: Cuando el chatbot resuelve
3. **Asignación a agente**: Cuando se asigna un agente
4. **Resolución de ticket**: Cuando se resuelve un ticket

**Características:**
- HTML responsive
- Versión texto plano
- Personalizable
- Listo para usar con APIs de email

## 📚 Referencias Completas

### Componentes Principales
- [Esquema de Base de Datos](data/db/support_tickets_schema.sql)
- [FAQs de Ejemplo](data/db/support_faq_seed.sql)
- [Módulo Chatbot](workflow/kestra/flows/lib/support_chatbot.py)
- [Módulo Priorización](workflow/kestra/flows/lib/support_priority.py)
- [Módulo Enrutamiento](workflow/kestra/flows/lib/support_routing.py)
- [Módulo Escalación](workflow/kestra/flows/lib/support_escalation.py)
- [Templates de Email](workflow/kestra/flows/lib/support_email_templates.py)

### Workflows y DAGs
- [Workflow Principal](workflow/kestra/flows/support_ticket_automation.yaml)
- [Workflow de Escalación](workflow/kestra/flows/support_ticket_escalation.yaml)
- [DAG de Monitoreo](data/airflow/dags/support_tickets_monitor.py)
- [DAG de Reportes](data/airflow/dags/support_tickets_reports.py)

### Scripts y Utilidades
- [Script de Setup](scripts/support_setup_example.py)
- [Health Check](scripts/support_health_check.py)
- [Quick Start Guide](SUPPORT_AUTOMATION_QUICK_START.md)

### Tests
- [Tests del Chatbot](workflow/kestra/flows/lib/tests/test_support_chatbot.py)
- [Tests de Priorización](workflow/kestra/flows/lib/tests/test_support_priority.py)

### Análisis Avanzado
- [Análisis de Sentimiento](workflow/kestra/flows/lib/support_sentiment.py)

### Documentación Adicional
- [Guía de Mejoras](README_SUPPORT_IMPROVEMENTS.md)
- [Funcionalidades Completas](SUPPORT_AUTOMATION_FEATURES.md)

## 🌐 API REST

### Endpoints Disponibles

**Base URL**: `/api/support`

#### Tickets
- `GET /api/support/tickets` - Listar tickets (con filtros y paginación)
- `POST /api/support/tickets` - Crear nuevo ticket
- `GET /api/support/tickets/stats` - Estadísticas de tickets

#### Feedback
- `POST /api/support/feedback` - Enviar feedback de un ticket
- `GET /api/support/feedback?ticket_id=XXX&customer_email=YYY` - Obtener feedback

### Ejemplos de Uso

```bash
# Crear ticket
curl -X POST http://localhost:3000/api/support/tickets \
  -H "Content-Type: application/json" \
  -d '{
    "subject": "Problema con factura",
    "description": "No puedo descargar mi factura",
    "customer_email": "cliente@example.com",
    "customer_name": "Juan Pérez",
    "category": "billing"
  }'

# Obtener estadísticas
curl http://localhost:3000/api/support/tickets/stats?period=7d

# Enviar feedback
curl -X POST http://localhost:3000/api/support/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "TKT-123",
    "customer_email": "cliente@example.com",
    "satisfaction_score": 5,
    "feedback_text": "Excelente atención"
  }'
```

## 📝 Sistema de Feedback

### Esquema de Feedback

**Archivo**: `data/db/support_feedback_schema.sql`

Tablas:
- `support_ticket_feedback`: Feedback de clientes
- `support_satisfaction_surveys`: Encuestas enviadas

Vistas:
- `v_support_feedback_summary`: Resumen de feedback por fecha
- `v_support_agent_feedback`: Feedback por agente

### Workflow de Recolección

**Archivo**: `workflow/kestra/flows/support_feedback_collection.yaml`

Características:
- Envía encuestas 24 horas después de resolución
- Recordatorio si no responde en 3 días
- Análisis de feedback negativo
- Notificaciones automáticas a Slack

### Configuración

```yaml
# Variables requeridas
email_api_url: "https://api.email.com/send"
email_api_key: "your-key"
slack_webhook_url: "https://hooks.slack.com/..."
```

## ⚡ Sistema de Cache

### Módulo de Cache

**Archivo**: `workflow/kestra/flows/lib/support_cache.py`

Características:
- Cache en memoria (TTLCache)
- Cache en Redis (opcional)
- TTL configurable
- Invalidation inteligente
- Decorador para funciones

### Uso

```python
from support_cache import SupportCache, cached_result

# Inicializar cache
cache = SupportCache(cache_type="memory", default_ttl=3600)

# Usar directamente
cache.set("key", {"data": "value"}, ttl=1800)
value = cache.get("key")

# Usar como decorador
@cached_result(prefix="faq_search", ttl=3600)
def search_faq(query):
    # Búsqueda de FAQ
    return results
```

## 🔄 Procesamiento por Lotes

### Módulo de Batch Processing

**Archivo**: `workflow/kestra/flows/lib/support_batch.py`

Características:
- Procesamiento batch de múltiples tickets
- Paralelización opcional
- Rate limiting inteligente
- Retry automático
- Métricas de procesamiento

### Uso

```python
from support_batch import SupportBatchProcessor

processor = SupportBatchProcessor(
    batch_size=20,
    max_workers=5,
    rate_limit_per_second=10
)

# Procesar tickets en batch
results = processor.process_in_batches(
    tickets,
    process_func=lambda t: calculate_priority(t),
    parallel=True
)
```

## 📤 Exportación de Datos

### DAG de Exportación

**Archivo**: `data/airflow/dags/support_tickets_export.py`

Exporta diariamente:
- CSV de tickets (últimos 30 días)
- JSON de métricas
- CSV de feedback
- Preparado para data warehouse

### Ejecución

```bash
# Manual
airflow dags trigger support_tickets_export

# Los archivos se guardan en: /tmp/support_exports/
```

## 🔗 Sistema de Webhooks

### Módulo de Webhooks

**Archivo**: `workflow/kestra/flows/lib/support_webhooks.py`

Eventos disponibles:
- `ticket.created` - Ticket creado
- `ticket.resolved` - Ticket resuelto
- `ticket.assigned` - Ticket asignado
- `ticket.escalated` - Ticket escalado
- `ticket.updated` - Ticket actualizado
- `chatbot.resolved` - Resuelto por chatbot
- `feedback.received` - Feedback recibido

### Uso

```python
from support_webhooks import SupportWebhookManager, WebhookConfig, EVENT_TICKET_CREATED

webhooks = [
    WebhookConfig(
        url="https://external-system.com/webhook",
        secret="your-secret",
        events=[EVENT_TICKET_CREATED, EVENT_TICKET_RESOLVED],
        enabled=True
    )
]

manager = SupportWebhookManager(webhooks)
manager.trigger_event(
    EVENT_TICKET_CREATED,
    ticket_id="TKT-123",
    data={"priority": "high", "status": "open"}
)
```

## 🗄️ Migración de Datos

### Script de Migración

**Archivo**: `scripts/support_migrate_data.py`

Funcionalidades:
- Migración entre bases de datos
- Backup de tablas a CSV
- Limpieza de datos antiguos
- Procesamiento por lotes

### Uso

```bash
# Migrar tickets
python scripts/support_migrate_data.py migrate \
  --from-date 2024-01-01 \
  --to-date 2024-12-31

# Backup de tablas
python scripts/support_migrate_data.py backup \
  --tables support_tickets,support_feedback

# Limpieza de datos antiguos
python scripts/support_migrate_data.py cleanup \
  --retention-days 365
```

## 🤖 Machine Learning

### Módulo de ML

**Archivo**: `workflow/kestra/flows/lib/support_ml.py`

Predicciones disponibles:
- **Tiempo de Resolución**: Basado en datos históricos
- **Satisfacción del Cliente**: Basado en historial
- **Recomendación de Agente**: Basado en performance

### Uso

```python
from support_ml import SupportMLPredictor

predictor = SupportMLPredictor(db_connection=conn)

# Predecir tiempo de resolución
prediction = predictor.predict_resolution_time(
    category="billing",
    priority="high"
)
print(f"Tiempo estimado: {prediction.predicted_minutes} minutos")

# Recomendar agente
agent = predictor.recommend_agent(
    category="technical",
    priority="urgent"
)
```

## 🏷️ Tags Automáticos

### Sistema de Tags

**Archivo**: `workflow/kestra/flows/lib/support_auto_tags.py`

Genera tags automáticamente basado en:
- Keywords detectados
- Categoría del ticket
- Prioridad
- Sentimiento
- Urgencia emocional

### Uso

```python
from support_auto_tags import SupportAutoTagger

tagger = SupportAutoTagger()
result = tagger.generate_tags(
    subject="Problema urgente",
    description="El sistema no funciona",
    category="technical",
    priority="urgent"
)
```

## 📊 Dashboard

### API de Dashboard

**Endpoint**: `GET /api/support/dashboard?period=24h`

Proporciona datos para visualización:
- Métricas principales
- Tendencias por hora
- Distribución por prioridad
- Top categorías y agentes
- Feedback reciente

## 🔧 Optimización

### DAG de Optimización

**Archivo**: `data/airflow/dags/support_tickets_optimization.py`

Ejecuta semanalmente:
- Archivo de tickets antiguos
- Optimización de índices
- Refresh de vistas materializadas
- Actualización de estadísticas
- Limpieza de datos antiguos

## 🔗 Integraciones Externas

### Módulo de Integraciones

**Archivo**: `workflow/kestra/flows/lib/support_integrations.py`

Sistemas soportados:
- **Zendesk**: Sincronización bidireccional
- **Freshdesk**: Sincronización de tickets
- **Intercom**: Conversaciones
- **Salesforce Service Cloud**: Casos
- **Jira Service Management**: Issues

### Uso

```python
from support_integrations import SupportIntegrations, IntegrationConfig

integrations = [
    IntegrationConfig(
        system="zendesk",
        api_url="https://yourcompany.zendesk.com",
        api_key="your-api-key",
        api_secret="your-api-secret"
    )
]

manager = SupportIntegrations(integrations)
results = manager.sync_ticket(
    ticket_data={
        "subject": "Problema técnico",
        "description": "El sistema no funciona",
        "customer_email": "cliente@example.com",
        "priority": "high"
    },
    systems=["zendesk", "jira"]
)
```

## 🚨 Alertas Avanzadas

### DAG de Alertas Inteligentes

**Archivo**: `data/airflow/dags/support_tickets_alerts_advanced.py`

Detecta:
- **Anomalías**: Picos de volumen, degradación de performance
- **Violaciones de SLA**: Tickets sin respuesta
- **Alertas Predictivas**: Sobrecarga de agentes, aumento de volumen

### Ejecución

- Frecuencia: Cada 5 minutos
- Integración: Slack y PagerDuty
- Severidad: Crítica, Alta, Media

## 🚀 Deployment

### Script de Deployment

**Archivo**: `scripts/support_deploy.sh`

Automatiza:
- Creación de esquemas
- Carga de datos iniciales
- Configuración de agentes
- Health check
- Verificación de workflows

### Uso

```bash
export DB_HOST=localhost
export DB_NAME=support_db
export DB_USER=postgres
export DB_PASSWORD=your_password

./scripts/support_deploy.sh
```

### CI/CD

**Archivo**: `.github/workflows/support-system-ci.yml`

Pipeline automatizado:
- Tests unitarios
- Linting
- Validación de YAML
- Health check

Ver [Guía de Deployment](SUPPORT_AUTOMATION_DEPLOYMENT.md) para detalles completos.

## 🧪 A/B Testing

### Sistema de A/B Testing

**Archivo**: `workflow/kestra/flows/lib/support_ab_testing.py`

Permite testing de:
- Diferentes prompts de LLM
- Umbrales de confianza
- Estrategias de enrutamiento
- Variantes de priorización

### Uso

```python
from support_ab_testing import SupportABTesting, ABTestVariant, create_chatbot_prompt_test

ab_tester = SupportABTesting(db_connection=conn)

# Crear test
create_chatbot_prompt_test(ab_tester, "chatbot_prompt_v1")

# Asignar variante
variant_id = ab_tester.assign_variant("chatbot_prompt_v1", ticket_id)

# Obtener resultados
results = ab_tester.get_test_results("chatbot_prompt_v1", days=7)
```

## 📈 Forecasting

### Sistema de Forecasting

**Archivo**: `workflow/kestra/flows/lib/support_forecasting.py`

Predicciones disponibles:
- Volumen de tickets
- Carga de trabajo de agentes
- Detección de patrones estacionales

### Uso

```python
from support_forecasting import SupportForecaster

forecaster = SupportForecaster(db_connection=conn)

# Predecir volumen
forecast = forecaster.forecast_volume(days_ahead=7)
print(f"Volumen previsto: {forecast.forecast_value} tickets/día")
print(f"Tendencia: {forecast.trend}")

# Detectar patrones
patterns = forecaster.detect_seasonal_patterns()
```

## ⏱️ SLA Dinámicos

### Sistema de SLA Configurable

**Archivo**: `data/db/support_sla_dynamic.sql`

Características:
- SLAs personalizados por tipo de cliente
- SLAs por categoría y prioridad
- SLAs de horario laboral
- Tracking automático de compliance

### Configuración

```sql
-- Ejemplo: SLA para clientes VIP
INSERT INTO support_sla_rules (
    rule_name,
    priority_order,
    customer_tier,
    first_response_minutes,
    resolution_minutes
) VALUES (
    'VIP Standard',
    1,
    'vip',
    15,  -- 15 minutos primera respuesta
    120  -- 2 horas resolución
);
```

## 📊 Dashboard React

### Componente de Dashboard

**Archivo**: `web/kpis-next/components/support/TicketDashboard.tsx`

Componente React/Next.js con:
- Métricas en tiempo real
- Gráficos de tendencias
- Top agentes y categorías
- Feedback reciente
- Actualización automática

## 💾 Backup Automatizado

### DAG de Backup

**Archivo**: `data/airflow/dags/support_tickets_backup.py`

Realiza diariamente:
- Backup completo (pg_dump)
- Backup incremental
- Compresión automática
- Verificación de integridad
- Limpieza de backups antiguos

### Configuración

```bash
export SUPPORT_BACKUP_PATH="/backups/support"
export BACKUP_RETENTION_DAYS=30
```

## 📚 Knowledge Base Avanzado

### Sistema de Knowledge Base

**Archivo**: `workflow/kestra/flows/lib/support_knowledge_base.py`

Funcionalidades:
- Búsqueda semántica mejorada
- Identificación de gaps en conocimiento
- Sugerencias automáticas de FAQs
- Tracking de efectividad de FAQs

### Uso

```python
from support_knowledge_base import SupportKnowledgeBase

kb = SupportKnowledgeBase(db_connection=conn)

# Identificar gaps
gaps = kb.identify_knowledge_gaps(days=30)
for gap in gaps:
    print(f"Gap: {gap.query} (frecuencia: {gap.frequency})")
    print(f"Sugerencia: {gap.suggested_faq_title}")
```

## 📱 Notificaciones Multicanal

### Sistema de Notificaciones Avanzado

**Archivo**: `workflow/kestra/flows/lib/support_notifications_multi.py`

Canales soportados:
- **Email**: SMTP, SendGrid, Mailgun, etc.
- **SMS**: Twilio, AWS SNS
- **WhatsApp**: Business API
- **Slack**: Webhooks
- **Teams**: Webhooks
- **Push**: Notificaciones push
- **Webhooks**: Personalizados

### Uso

```python
from support_notifications_multi import (
    SupportNotificationManager,
    NotificationConfig,
    NotificationChannel,
    NotificationMessage
)

configs = [
    NotificationConfig(
        channel=NotificationChannel.EMAIL,
        config={"api_url": "https://api.sendgrid.com/v3/mail/send", "api_key": "..."},
        priority=1
    ),
    NotificationConfig(
        channel=NotificationChannel.SLACK,
        config={"webhook_url": "https://hooks.slack.com/..."},
        priority=2
    )
]

manager = SupportNotificationManager(configs)
message = NotificationMessage(
    recipient="cliente@example.com",
    subject="Ticket resuelto",
    body="Tu ticket ha sido resuelto",
    html_body="<html>...</html>"
)

results = manager.send_notification(message, channels=[NotificationChannel.EMAIL, NotificationChannel.SLACK])
```

## ⚡ Optimizaciones SQL

### Esquema de Optimizaciones

**Archivo**: `data/db/support_optimizations.sql`

Contiene:
- Índices compuestos para queries frecuentes
- Índices GIN para búsqueda full-text
- Vistas materializadas para métricas
- Funciones optimizadas
- Triggers para actualización automática

### Aplicar Optimizaciones

```bash
psql -U postgres -d support_db -f data/db/support_optimizations.sql
```

## 📝 Versionado de FAQs

### Sistema de Versionado

**Archivo**: `data/db/support_faq_versioning.sql`

Características:
- Versionado automático de cambios
- Historial completo
- Rollback a versiones anteriores
- Tracking de cambios

### Uso

```sql
-- Rollback a versión anterior
SELECT rollback_faq_version('faq-001', 2);

-- Ver historial de versiones
SELECT * FROM support_faq_versions
WHERE article_id = 'faq-001'
ORDER BY version_number DESC;
```

## 💰 Análisis de ROI

### DAG de Análisis de ROI

**Archivo**: `data/airflow/dags/support_tickets_roi_analysis.py`

Analiza:
- Ahorros por automatización
- Costos de operación
- ROI del chatbot
- Costo por ticket
- Comparación manual vs. automatizado

### Configuración

Ajustar variables de costo según tu caso:
- `COST_PER_AGENT_HOUR`
- `COST_CHATBOT_API_CALL`
- `AVG_TICKETS_PER_HOUR`

## 🔧 Troubleshooting

### Guía de Troubleshooting

**Archivo**: `scripts/support_troubleshooting_guide.md`

Cubre:
- Problemas comunes y soluciones
- Comandos de diagnóstico
- Logs importantes
- Procedimientos de recuperación

Ver [Índice Completo](SUPPORT_AUTOMATION_INDEX.md) para navegación completa.

## 🎯 Motor de Reglas de Negocio

### Sistema de Reglas Dinámicas

**Archivo**: `workflow/kestra/flows/lib/support_business_rules.py`

Permite definir reglas complejas y dinámicas para procesamiento de tickets:
- **Tipos de reglas**: Prioridad, enrutamiento, escalación, notificaciones, tags, SLA, personalizadas
- **Operadores**: equals, contains, greater_than, regex, in, etc.
- **Condiciones múltiples**: AND lógico entre condiciones
- **Acciones**: set_priority, assign_to, add_tag, send_notification, etc.
- **Priorización**: Ejecución ordenada por prioridad

### Uso

```python
from support_business_rules import (
    BusinessRulesEngine,
    BusinessRule,
    RuleCondition,
    RuleAction,
    RuleType,
    Operator
)

# Crear regla
rule = BusinessRule(
    rule_id="vip_priority",
    name="VIP Priority Boost",
    rule_type=RuleType.PRIORITY,
    priority=10,
    conditions=[
        RuleCondition(
            field="customer.tier",
            operator=Operator.EQUALS,
            value="vip"
        )
    ],
    actions=[
        RuleAction(
            type="set_priority",
            params={"priority": "urgent"}
        )
    ]
)

# Ejecutar
engine = BusinessRulesEngine([rule])
results = engine.execute_rules(context)
```

## 📞 Integración con Voice (Call Center)

### Sistema de Transcripción y Análisis

**Archivo**: `workflow/kestra/flows/lib/support_voice_integration.py`

Características:
- **Transcripción**: OpenAI Whisper, AssemblyAI, Google Cloud Speech
- **Análisis de voz**: Sentimiento, urgencia, keywords, topics
- **Creación automática de tickets** desde llamadas
- **Detección de frustración** y satisfacción
- **Análisis de sentimiento** en transcripciones

### Uso

```python
from support_voice_integration import (
    VoiceTranscriptionProvider,
    VoiceAnalyzer,
    VoiceCallHandler,
    CallRecording
)

# Configurar
transcriber = VoiceTranscriptionProvider(provider="openai")
analyzer = VoiceAnalyzer()
handler = VoiceCallHandler(transcriber, analyzer)

# Procesar llamada
call = CallRecording(
    call_id="call-123",
    customer_phone="+1234567890",
    recording_url="https://...",
    duration_seconds=300
)

result = handler.process_call(call, auto_create_ticket=True)
# Crea ticket automáticamente si hay indicadores de urgencia
```

## 📊 Analytics Avanzado

### Sistema de Analytics y Visualizaciones

**Archivo**: `workflow/kestra/flows/lib/support_analytics_advanced.py`

Funcionalidades:
- **Tendencias**: Análisis de tendencias con cambios porcentuales
- **Correlaciones**: Correlación de Pearson entre métricas
- **Segmentación**: Por prioridad, categoría, status, departamento
- **Insights automáticos**: Detección de patrones y recomendaciones
- **Múltiples métricas**: Volumen, tiempo de resolución, satisfacción, etc.

### Uso

```python
from support_analytics_advanced import SupportAnalyticsEngine

engine = SupportAnalyticsEngine(db_connection)

# Tendencias
trends = engine.calculate_trends("ticket_volume", days=30)
for trend in trends:
    print(f"{trend.period}: {trend.value} ({trend.trend})")

# Correlaciones
correlations = engine.calculate_correlations(
    ["ticket_volume", "resolution_time", "customer_satisfaction"],
    days=30
)

# Segmentación
segments = engine.segment_tickets("priority", metric="avg_resolution_time")

# Insights automáticos
insights = engine.generate_insights(days=30)
```

## 🔍 Auditoría Avanzada

### Sistema de Auditoría Completo

**Archivo**: `data/db/support_audit_advanced.sql`

Tracking completo:
- **Auditoría de tickets**: Todos los cambios, creaciones, eliminaciones
- **Auditoría de accesos**: Tracking de accesos a recursos
- **Auditoría de configuración**: Cambios en reglas, agentes, SLA, etc.
- **Tracking de actores**: Usuario, sistema, agente, chatbot
- **Contexto**: IP, user agent, sesión
- **Campos JSONB** para cambios complejos

### Uso

```sql
-- Ver auditoría de un ticket
SELECT * FROM support_audit_tickets
WHERE ticket_id = 'ticket-123'
ORDER BY created_at DESC;

-- Registrar acceso
SELECT log_access(
    'user-123',
    'agent',
    'ticket',
    'ticket-456',
    'view',
    '192.168.1.1'::inet
);

-- Resumen de auditoría
SELECT * FROM v_support_audit_summary
WHERE audit_date >= CURRENT_DATE - INTERVAL '7 days';
```

## 🤖 Resumen Automático con IA

### Sistema de Resúmenes Inteligentes

**Archivo**: `workflow/kestra/flows/lib/support_ai_summarization.py`

Características:
- **Resúmenes de tickets**: Resúmenes cortos, medianos, largos, con puntos clave
- **Resúmenes de conversaciones**: Resúmenes de threads completos
- **Múltiples proveedores**: OpenAI GPT-4, Anthropic Claude
- **Análisis de sentimiento**: Incluido en resúmenes
- **Extracción de puntos clave**: Automática
- **Fallback simple**: Si no hay IA disponible

### Uso

```python
from support_ai_summarization import (
    AISummarizer,
    ConversationSummarizer,
    SummaryType
)

# Resumidor
summarizer = AISummarizer(provider="openai", model="gpt-4")

# Resumir ticket
summary = summarizer.summarize_ticket(
    ticket_data,
    SummaryType.MEDIUM
)
print(summary.content)
print(summary.key_points)

# Resumir conversación
messages = [{"sender": "Cliente", "content": "..."}, ...]
conv_summary = summarizer.summarize_conversation(messages)

# Resumidor especializado
conv_summarizer = ConversationSummarizer(summarizer)
thread_summary = conv_summarizer.summarize_thread("thread-123", messages)
```

## 🌐 Traducción Automática Multi-idioma

### Sistema de Traducción

**Archivo**: `workflow/kestra/flows/lib/support_translation.py`

Características:
- **Detección automática de idioma**
- **Múltiples proveedores**: Google Translate, OpenAI
- **Traducción de tickets completos**: Subject y description
- **Traducción de respuestas**: Al idioma del cliente
- **Soporte multi-idioma**: 10+ idiomas
- **Soporte multi-idioma completo**: Procesamiento automático

### Uso

```python
from support_translation import (
    SupportTranslator,
    MultiLanguageSupport,
    Language
)

# Traductor
translator = SupportTranslator(provider="google")

# Detectar idioma
lang = translator.detect_language("Hello, I need help")
print(lang)  # 'en'

# Traducir
translation = translator.translate(
    "Hello, I need help",
    target_language="es"
)
print(translation.translated_text)  # "Hola, necesito ayuda"

# Traducir ticket completo
translated_ticket = translator.translate_ticket(
    ticket_data,
    target_language="es"
)

# Soporte multi-idioma
ml_support = MultiLanguageSupport(translator)
processed_ticket = ml_support.process_ticket(ticket_data, agent_language="es")
response = ml_support.prepare_response("Gracias por contactarnos", customer_language="en")
```

## 👥 Colaboración entre Agentes

### Sistema de Colaboración

**Archivo**: `workflow/kestra/flows/lib/support_collaboration.py`

Características:
- **Solicitudes de colaboración**: Handoff, asistencia, consulta, pair work
- **Notas de agentes**: Notas internas y públicas
- **Tracking de actividades**: View, edit, comment, resolve
- **Historial de colaboración**: Completo por ticket
- **Gestión de estado**: Pending, active, completed, cancelled

### Uso

```python
from support_collaboration import (
    CollaborationManager,
    CollaborationType,
    CollaborationStatus
)

manager = CollaborationManager(db_connection)

# Crear solicitud de colaboración
request = manager.create_collaboration_request(
    ticket_id="ticket-123",
    from_agent_id="agent-1",
    from_agent_name="Juan",
    to_agent_id="agent-2",
    collaboration_type=CollaborationType.ASSISTANCE,
    reason="Necesito ayuda con integración técnica"
)

# Aceptar colaboración
manager.accept_collaboration(request.request_id, "agent-2", "María")

# Agregar nota
note = manager.add_note(
    ticket_id="ticket-123",
    agent_id="agent-2",
    agent_name="María",
    content="Revisé el código, el problema está en la línea 42",
    is_internal=True
)

# Registrar actividad
activity = manager.log_activity(
    ticket_id="ticket-123",
    agent_id="agent-1",
    agent_name="Juan",
    activity_type="view",
    description="Revisó el ticket para colaboración"
)

# Obtener historial
history = manager.get_collaboration_history("ticket-123")
notes = manager.get_notes("ticket-123", include_internal=True)
```

## 📝 Templates Inteligentes

### Sistema de Templates Dinámicos

**Archivo**: `workflow/kestra/flows/lib/support_templates_intelligent.py`

Características:
- **Variables dinámicas**: `{{variable}}` con notación de punto
- **Condicionales**: `{% if condition %}...{% endif %}` y `{% else %}`
- **Funciones**: upper, lower, date, currency, number
- **Múltiples tipos**: Email, respuesta, notificación, FAQ
- **Búsqueda y categorización**: Por categoría o búsqueda de texto
- **Tracking de uso**: Contador de usos por template

### Uso

```python
from support_templates_intelligent import (
    TemplateEngine,
    TemplateBuilder,
    TemplateType
)

engine = TemplateEngine()

# Crear template
template = TemplateBuilder.create_response_template(
    template_id="ticket-resolved",
    name="Ticket Resuelto",
    content="""
Hola {{customer.name}},

Tu ticket #{{ticket.id}} ha sido resuelto.

{% if ticket.satisfaction_score %}
Gracias por tu feedback: {{ticket.satisfaction_score}}/5
{% endif %}

{% if ticket.resolution_notes %}
Notas: {{ticket.resolution_notes}}
{% endif %}
    """,
    variables=["customer.name", "ticket.id", "ticket.satisfaction_score"]
)

engine.register_template(template)

# Renderizar
context = {
    "customer": {"name": "Juan Pérez"},
    "ticket": {
        "id": "T-12345",
        "satisfaction_score": 5,
        "resolution_notes": "Problema resuelto"
    }
}

rendered = engine.render("ticket-resolved", context)
```

## 🎮 Gamificación para Agentes

### Sistema de Puntos, Badges y Rankings

**Archivo**: `workflow/kestra/flows/lib/support_gamification.py`

Características:
- **Sistema de puntos**: Por resolver tickets, velocidad, satisfacción
- **Badges**: Resolución, velocidad, satisfacción, volumen, colaboración
- **Niveles**: Basados en puntos acumulados
- **Rankings**: Semanal, mensual, all-time
- **Reglas configurables**: Puntos por acción, cooldowns, límites diarios
- **Métricas**: Tickets resueltos, tiempo promedio, satisfacción promedio

### Uso

```python
from support_gamification import (
    GamificationEngine,
    ScoringRule
)

engine = GamificationEngine()

# Procesar evento (resolver ticket)
event = {
    "agent_id": "agent-123",
    "agent_name": "Juan",
    "action": "resolve",
    "ticket_id": "ticket-456",
    "resolution_time_minutes": 45,
    "satisfaction_score": 5,
    "timestamp": datetime.now()
}

engine.process_event(event)

# Obtener score
score = engine.get_agent_score("agent-123")
print(f"Puntos totales: {score.total_points}")
print(f"Nivel: {score.current_level}")
print(f"Badges: {score.badges}")

# Leaderboard
leaderboard = engine.get_leaderboard(period="weekly", limit=10)
for i, agent_score in enumerate(leaderboard, 1):
    print(f"{i}. {agent_score.agent_name}: {agent_score.total_points} puntos")

# Badges del agente
badges = engine.get_agent_badges("agent-123")
for badge in badges:
    print(f"{badge.name}: {badge.description}")
```

## 📚 Documentación Automática de Soluciones

### Generador de Documentos desde Tickets Resueltos

**Archivo**: `workflow/kestra/flows/lib/support_solution_docs.py`

Características:
- **Generación automática**: Desde tickets resueltos
- **Múltiples tipos**: How-To, Troubleshooting, FAQ, Best Practices
- **Extracción de keywords**: Automática
- **Categorización**: Por categoría y tags
- **Sistema de feedback**: Útil/No útil
- **Publicación y verificación**: Control de calidad
- **Búsqueda**: Por query, categoría, tipo

### Uso

```python
from support_solution_docs import (
    SolutionDocumentGenerator,
    SolutionType
)

generator = SolutionDocumentGenerator(db_connection)

# Generar desde ticket resuelto
ticket_data = {
    "ticket_id": "ticket-123",
    "subject": "Error al conectar API",
    "description": "No puedo conectar con la API",
    "resolution_notes": "Solución: Actualizar la API key en configuración",
    "category": "technical",
    "tags": ["api", "connection"],
    "resolved_by": "agent-456"
}

document = generator.generate_from_ticket(
    ticket_data,
    solution_type=SolutionType.HOW_TO
)

print(f"Documento: {document.title}")
print(f"Keywords: {document.keywords}")

# Publicar
generator.publish_document(document.document_id)

# Buscar
results = generator.search_documents("API", category="technical")
for doc in results:
    print(f"{doc.title}: {doc.description}")

# Registrar feedback
generator.record_view(document.document_id)
generator.record_feedback(document.document_id, helpful=True)
```

## ✅ Evaluación de Calidad Automática

### Sistema de Quality Assurance

**Archivo**: `workflow/kestra/flows/lib/support_quality_assurance.py`

Características:
- **Evaluación automática**: 6 criterios de calidad
- **Scoring**: 0-100 con niveles (Excellent, Good, Fair, Poor)
- **Criterios evaluados**: Tiempo de respuesta, calidad de respuesta, profesionalismo, completitud, documentación, satisfacción
- **Feedback automático**: Fortalezas y áreas de mejora
- **Reportes de agente**: Promedios, distribución, recomendaciones
- **Pesos configurables**: Por criterio

### Uso

```python
from support_quality_assurance import (
    QualityAssuranceEngine,
    QualityScore
)

engine = QualityAssuranceEngine()

# Evaluar ticket
ticket_data = {
    "ticket_id": "ticket-123",
    "assigned_agent_id": "agent-456",
    "status": "resolved",
    "created_at": datetime.now() - timedelta(hours=2),
    "first_response_at": datetime.now() - timedelta(hours=1.5),
    "resolution_notes": "Problema resuelto actualizando configuración.",
    "customer_satisfaction_score": 5,
    "tags": ["technical", "api"]
}

evaluation = engine.evaluate_ticket(ticket_data)

print(f"Score: {evaluation.overall_score:.1f}")
print(f"Nivel: {evaluation.quality_level.value}")
print(f"Fortalezas: {evaluation.strengths}")
print(f"Mejoras: {evaluation.improvements}")

# Reporte de agente
evaluations = [evaluation]  # Lista de evaluaciones
report = engine.get_agent_quality_report("agent-456", evaluations)
print(f"Promedio: {report['average_score']:.1f}")
print(f"Recomendaciones: {report['recommendations']}")
```

## 🧠 Sistema de Aprendizaje y Recomendaciones

### Motor de Aprendizaje Inteligente

**Archivo**: `workflow/kestra/flows/lib/support_learning_engine.py`

Características:
- **Recomendaciones inteligentes**: Soluciones similares, templates, escalación, conocimiento
- **Aprendizaje continuo**: Aprende de cada resolución
- **Patrones de éxito**: Identifica patrones que funcionan
- **Insights de agente**: Métricas y recomendaciones personalizadas
- **Búsqueda de similitud**: Encuentra soluciones relacionadas
- **Priorización**: Recomendaciones ordenadas por relevancia

### Uso

```python
from support_learning_engine import LearningEngine

engine = LearningEngine(db_connection)

# Obtener recomendaciones
ticket_data = {
    "ticket_id": "ticket-123",
    "subject": "Error al conectar API",
    "description": "No puedo conectar con la API de pago",
    "category": "technical",
    "tags": ["api", "connection"],
    "priority": "high",
    "status": "open",
    "created_at": datetime.now() - timedelta(hours=3)
}

recommendations = engine.get_recommendations(
    ticket_data,
    agent_id="agent-456"
)

for rec in recommendations:
    print(f"{rec.priority.upper()}: {rec.title}")
    print(f"  Confianza: {rec.confidence:.2f}")
    print(f"  {rec.description}")

# Aprender de resolución
resolution_data = {
    "notes": "Solución: Actualizar API key en configuración avanzada"
}

engine.learn_from_resolution(ticket_data, resolution_data)

# Insights de agente
insights = engine.get_agent_insights("agent-456")
print(f"Total soluciones: {insights['total_solutions']}")
print(f"Satisfacción promedio: {insights['average_satisfaction']:.2f}")
print(f"Categorías top: {insights['top_categories']}")
```

## 🔄 Workflow Builder Visual

### Sistema de Workflows Personalizados

**Archivo**: `workflow/kestra/flows/lib/support_workflow_builder.py`

Características:
- **Nodos visuales**: Trigger, Action, Condition, Delay, Webhook, Notification
- **Conexiones**: Workflows dirigidos con múltiples rutas
- **Acciones**: Set priority, assign agent, send email, update status, add tag
- **Condiciones**: Evaluación de condiciones para flujo condicional
- **Handlers personalizados**: Registro de acciones personalizadas
- **Ejecución**: Motor de ejecución de workflows

### Uso

```python
from support_workflow_builder import (
    WorkflowEngine,
    WorkflowBuilder,
    NodeType,
    ActionType
)

engine = WorkflowEngine()

# Crear workflow simple
workflow = WorkflowBuilder.create_simple_workflow(
    workflow_id="workflow-vip",
    name="VIP Customer Workflow",
    actions=[
        {
            "label": "Set Priority",
            "action_type": "set_priority",
            "params": {"priority": "urgent"}
        },
        {
            "label": "Assign to VIP Team",
            "action_type": "assign_agent",
            "params": {"agent_id": "vip-team-lead"}
        },
        {
            "label": "Send Notification",
            "action_type": "send_email",
            "params": {
                "recipient": "vip-team@example.com",
                "subject": "VIP Ticket Created"
            }
        }
    ]
)

engine.register_workflow(workflow)

# Ejecutar workflow
context = {
    "ticket": {
        "ticket_id": "ticket-123",
        "customer": {"tier": "vip"},
        "priority": "normal"
    }
}

result = engine.execute_workflow("workflow-vip", context)
print(f"Workflow ejecutado: {result['executed']}")
print(f"Resultados: {result['results']}")

# Registrar handler personalizado
def custom_handler(node, context, params):
    # Lógica personalizada
    return {"status": "success", "custom": True}

engine.register_handler("custom_action", custom_handler)
```

## 📊 Métricas en Tiempo Real

### Sistema de Monitoreo en Tiempo Real

**Archivo**: `workflow/kestra/flows/lib/support_realtime_metrics.py`

Características:
- **Recolección automática**: Cada 60 segundos (configurable)
- **Métricas clave**: Tickets abiertos, críticos sin respuesta, tiempo de respuesta, tasa de chatbot, agentes activos
- **Alertas automáticas**: Basadas en umbrales configurables
- **Tendencias**: Análisis de tendencias en tiempo real
- **Dashboard data**: Datos listos para visualización
- **Callbacks**: Sistema de callbacks para alertas
- **Historial**: Mantiene hasta 1000 valores históricos por métrica

### Uso

```python
from support_realtime_metrics import RealtimeMetricsCollector

collector = RealtimeMetricsCollector(db_connection)

# Iniciar recolección automática
collector.start_collection(interval_seconds=60)

# Registrar callback para alertas
def on_alert(alert):
    print(f"ALERTA {alert.severity}: {alert.message}")

collector.register_alert_callback(on_alert)

# Obtener métricas
tickets_open = collector.get_metric_value("tickets_open")
print(f"Tickets abiertos: {tickets_open}")

# Obtener tendencia
trend = collector.get_metric_trend("tickets_open", minutes=60)
print(f"Tendencia: {trend['trend']}, Cambio: {trend['change_percentage']:.1f}%")

# Dashboard completo
dashboard_data = collector.get_dashboard_data()
print(dashboard_data)

# Detener recolección
collector.stop_collection()
```

## 🤖 Copilot para Agentes

### Asistente Inteligente para Agentes

**Archivo**: `workflow/kestra/flows/lib/support_agent_copilot.py`

Características:
- **Sugerencias inteligentes**: Respuestas, acciones, escalación, conocimiento
- **Generación de respuestas**: Con IA (OpenAI) o basadas en historial
- **Feedback de calidad**: Análisis de respuestas antes de enviar
- **Integración con learning engine**: Usa recomendaciones aprendidas
- **Contexto del agente**: Considera historial y preferencias
- **Múltiples tipos**: Response, action, escalation, knowledge

### Uso

```python
from support_agent_copilot import AgentCopilot

copilot = AgentCopilot(
    learning_engine=learning_engine,
    quality_engine=quality_engine,
    api_key="openai-api-key"
)

# Obtener sugerencias
ticket_data = {
    "ticket_id": "ticket-123",
    "subject": "Error al conectar API",
    "description": "No puedo conectar con la API",
    "category": "technical",
    "priority": "high",
    "status": "open",
    "created_at": datetime.now() - timedelta(hours=3)
}

agent_context = {
    "agent_id": "agent-456",
    "experience_level": "senior",
    "specialties": ["technical", "api"]
}

suggestions = copilot.get_suggestions(
    ticket_data,
    agent_context,
    conversation_history=None
)

for suggestion in suggestions:
    print(f"{suggestion.type.upper()}: {suggestion.title}")
    print(f"  Confianza: {suggestion.confidence:.2f}")
    print(f"  {suggestion.content}")
    if suggestion.reasoning:
        print(f"  Razón: {suggestion.reasoning}")

# Feedback de calidad
response_text = "Hola, gracias por contactarnos. El problema está resuelto."
feedback = copilot.get_quality_feedback(response_text, ticket_data)
print(f"Score: {feedback['score']:.1f}")
print(f"Fortalezas: {feedback['strengths']}")
print(f"Mejoras: {feedback['improvements']}")
```

## 🔄 Auto-optimización del Sistema

### Sistema de Optimización Automática

**Archivo**: `workflow/kestra/flows/lib/support_auto_optimization.py`

Características:
- **Análisis automático**: Detecta áreas de optimización
- **Tipos de optimización**: Routing, prioridad, SLAs, asignación de recursos
- **Recomendaciones**: Sugerencias con impacto esperado
- **Aplicación automática**: Opción de aplicar optimizaciones
- **Tracking**: Historial de optimizaciones aplicadas
- **Reportes**: Reportes de optimizaciones por período

### Uso

```python
from support_auto_optimization import AutoOptimizer, OptimizationType

optimizer = AutoOptimizer(db_connection)

# Analizar y generar optimizaciones
optimizations = optimizer.analyze_and_optimize()

for opt in optimizations:
    print(f"{opt.optimization_type.value}: {opt.description}")
    print(f"  Confianza: {opt.confidence:.2f}")
    print(f"  Impacto esperado: {opt.expected_impact}")
    print(f"  Cambios: {opt.changes}")

# Aplicar optimización
if optimizations:
    optimizer.apply_optimization(optimizations[0])

# Reporte
report = optimizer.get_optimization_report(days=30)
print(f"Total optimizaciones: {report['total_optimizations']}")
print(f"Aplicadas: {report['applied_optimizations']}")
print(f"Por tipo: {report['by_type']}")
```

## 📈 Predicción de Carga de Trabajo

### Sistema de Predicción de Volumen

**Archivo**: `workflow/kestra/flows/lib/support_workload_prediction.py`

Características:
- **Predicciones múltiples**: Horaria, diaria, semanal
- **Análisis histórico**: Usa datos históricos para predecir
- **Tendencias**: Identifica tendencias y ajusta predicciones
- **Carga por agente**: Estima carga de trabajo por agente
- **Recomendaciones**: Sugerencias basadas en predicciones
- **Confianza**: Nivel de confianza de cada predicción

### Uso

```python
from support_workload_prediction import WorkloadPredictor
from datetime import datetime, timedelta

predictor = WorkloadPredictor(db_connection)

# Predicción horaria
target_hour = datetime.now() + timedelta(hours=2)
hourly_pred = predictor.predict_hourly(target_hour)
print(f"Tickets previstos en {target_hour}: {hourly_pred.predicted_ticket_count:.1f}")
print(f"Confianza: {hourly_pred.confidence:.2f}")
print(f"Recomendaciones: {hourly_pred.recommendations}")

# Predicción diaria
target_date = datetime.now() + timedelta(days=1)
daily_pred = predictor.predict_daily(target_date)
print(f"Tickets previstos mañana: {daily_pred.predicted_ticket_count:.1f}")
print(f"Carga por agente: {daily_pred.predicted_agent_load}")

# Predicción semanal
week_start = datetime.now() + timedelta(days=7)
weekly_pred = predictor.predict_weekly(week_start)
print(f"Tickets previstos la próxima semana: {weekly_pred.predicted_ticket_count:.1f}")

# Evaluar precisión
accuracy = predictor.get_prediction_accuracy(days_back=7)
print(f"Precisión: {accuracy}")
```

## 🔍 Detección de Anomalías

### Sistema de Detección Automática de Anomalías

**Archivo**: `workflow/kestra/flows/lib/support_anomaly_detection.py`

Características:
- **Múltiples tipos**: Picos de volumen, caídas, tiempo de respuesta, satisfacción, cambios de categoría
- **Detección estadística**: Usa desviaciones estándar y comparaciones históricas
- **Severidad**: Low, Medium, High, Critical
- **Recomendaciones**: Sugerencias automáticas para cada anomalía
- **Contexto**: Información detallada de cada anomalía
- **Resúmenes**: Resúmenes por tipo y severidad

### Uso

```python
from support_anomaly_detection import (
    AnomalyDetector,
    AnomalyType,
    AnomalySeverity
)

detector = AnomalyDetector(db_connection)

# Detectar anomalías
anomalies = detector.detect_anomalies()

for anomaly in anomalies:
    print(f"{anomaly.severity.value.upper()}: {anomaly.description}")
    print(f"  Tipo: {anomaly.anomaly_type.value}")
    print(f"  Valor actual: {anomaly.current_value}")
    print(f"  Valor esperado: {anomaly.expected_value}")
    print(f"  Desviación: {anomaly.deviation_percentage:.1f}%")
    print(f"  Recomendaciones: {anomaly.recommendations}")

# Resumen
summary = detector.get_anomaly_summary(hours=24)
print(f"Total anomalías: {summary['total_anomalies']}")
print(f"Por tipo: {summary['by_type']}")
print(f"Por severidad: {summary['by_severity']}")
```

## 🔒 Seguridad y Compliance

### Sistema de Seguridad y Cumplimiento

**Archivo**: `workflow/kestra/flows/lib/support_security_compliance.py`

Características:
- **Verificaciones de seguridad**: Acceso a datos sensibles, encriptación, contraseñas, auditoría
- **Retención de datos**: Reglas configurables por tipo de dato
- **Compliance**: GDPR, CCPA, HIPAA, PCI-DSS, SOC2
- **Enmascaramiento**: Enmascara datos sensibles automáticamente
- **Reportes de compliance**: Reportes por tipo de compliance
- **Aplicación automática**: Aplica reglas de retención automáticamente

### Uso

```python
from support_security_compliance import (
    SecurityComplianceManager,
    ComplianceType,
    DataRetentionRule
)

manager = SecurityComplianceManager(db_connection)

# Ejecutar verificaciones de seguridad
security_checks = manager.run_security_checks()

for check in security_checks:
    print(f"{check.status.upper()}: {check.description}")
    print(f"  Severidad: {check.severity.value}")
    if check.details:
        print(f"  Detalles: {check.details}")

# Aplicar retención de datos
retention_results = manager.apply_data_retention()
print(f"Archivados: {retention_results['archived']}")
print(f"Eliminados: {retention_results['deleted']}")

# Enmascarar datos sensibles
text = "Mi tarjeta es 1234-5678-9012-3456 y mi SSN es 123-45-6789"
masked = manager.mask_sensitive_data(text)
print(f"Enmascarado: {masked}")

# Reporte de compliance
gdpr_report = manager.get_compliance_report(ComplianceType.GDPR)
print(f"Compliance Score: {gdpr_report['compliance_score']:.1f}%")
print(f"Checks: {gdpr_report['security_checks']}")

# Agregar regla de retención personalizada
custom_rule = DataRetentionRule(
    rule_id="custom-rule-1",
    data_type="custom_data",
    retention_days=180,
    compliance_type=ComplianceType.CUSTOM,
    auto_delete=True
)
manager.retention_rules.append(custom_rule)
```

## 📊 Integración con Métricas Externas

### Sistema de Exportación de Métricas

**Archivo**: `workflow/kestra/flows/lib/support_metrics_integration.py`

Características:
- **Prometheus**: Exporta métricas en formato Prometheus
- **Grafana**: Genera dashboards de Grafana automáticamente
- **Múltiples tipos**: Counters, Gauges, Histograms, Summaries
- **Métricas clave**: Tickets, tiempos, satisfacción, agentes, chatbot
- **API de métricas**: Exporta a diccionario para APIs
- **Servidor HTTP**: Servidor Prometheus integrado

### Uso

```python
from support_metrics_integration import MetricsExporter, GrafanaIntegration

# Inicializar exportador
exporter = MetricsExporter(enable_prometheus=True, port=8000)

# Registrar eventos
ticket_data = {
    "status": "open",
    "priority": "high",
    "category": "technical"
}
exporter.record_ticket_created(ticket_data)

# Registrar resolución
resolved_data = {
    "category": "technical",
    "chatbot_resolved": False,
    "time_to_resolution_minutes": 45
}
exporter.record_ticket_resolved(resolved_data)

# Actualizar gauges
exporter.update_gauge("tickets_open", 25, labels={"priority": "high"})
exporter.update_gauge("avg_response_time_minutes", 12.5)

# Exportar a diccionario
metrics_dict = exporter.export_to_dict(db_connection)
print(f"Tickets abiertos: {metrics_dict['tickets_open']}")
print(f"Satisfacción: {metrics_dict['customer_satisfaction_score']:.2f}")

# URL de métricas Prometheus
print(f"Métricas disponibles en: {exporter.get_prometheus_metrics_url()}")

# Generar dashboard de Grafana
grafana = GrafanaIntegration()
dashboard_json = grafana.generate_dashboard_json([
    "support_tickets_open",
    "support_avg_response_time_minutes",
    "support_customer_satisfaction_score"
])
```

## 📈 Benchmarking y Comparación

### Sistema de Comparación con Estándares de la Industria

**Archivo**: `workflow/kestra/flows/lib/support_benchmarking.py`

Características:
- **6 categorías de benchmark**: Tiempo de respuesta, tiempo de resolución, satisfacción, efectividad del chatbot, productividad de agentes, resolución en primer contacto
- **Comparación con la industria**: Promedio, top 10%, top 1%
- **Cálculo de percentiles**: Posición relativa en la industria
- **Ratings automáticos**: Excellent, Good, Average, Below Average
- **Recomendaciones**: Prioridades de mejora
- **Reportes completos**: Evaluación general y áreas de mejora

### Uso

```python
from support_benchmarking import (
    BenchmarkingEngine,
    BenchmarkCategory
)

engine = BenchmarkingEngine(db_connection)

# Comparar con benchmarks
comparisons = engine.compare_with_benchmarks(days=30)

for comp in comparisons:
    print(f"{comp.benchmark.metric_name}:")
    print(f"  Tu valor: {comp.your_value:.2f} {comp.benchmark.unit}")
    print(f"  Promedio industria: {comp.benchmark.industry_average:.2f}")
    print(f"  Percentil: {comp.percentile:.1f}%")
    print(f"  Rating: {comp.rating}")
    print(f"  vs Promedio: {comp.vs_average:+.2f}")
    print(f"  Recomendaciones: {comp.recommendations}")

# Reporte completo
report = engine.get_benchmark_report(days=30)
print(f"Percentil promedio: {report['average_percentile']:.1f}%")
print(f"Evaluación: {report['overall_assessment']}")
print(f"Distribución: {report['rating_distribution']}")

# Prioridades de mejora
for priority in report['improvement_priorities']:
    print(f"\nMejorar: {priority['metric']}")
    print(f"  Percentil actual: {priority['current_percentile']:.1f}%")
    print(f"  Recomendaciones: {priority['recommendations']}")
```

## 🧪 Simulaciones y Testing

### Sistema de Simulación y Pruebas

**Archivo**: `workflow/kestra/flows/lib/support_simulation_testing.py`

Características:
- **Pruebas de volumen**: Simula grandes volúmenes de tickets
- **Pruebas de estrés**: Simula picos de carga
- **Escenarios predefinidos**: VIP spike, technical outbreak, billing peak
- **Escenarios personalizados**: Configuración flexible
- **Métricas completas**: Tiempos, tasas de resolución, errores
- **Reportes**: Reportes detallados de simulaciones

### Uso

```python
from support_simulation_testing import (
    SimulationEngine,
    SimulationType
)

engine = SimulationEngine(db_connection)

# Prueba de volumen
volume_result = engine.simulate_volume_test(
    ticket_count=1000,
    duration_minutes=60,
    use_chatbot=True
)

print(f"Tickets procesados: {volume_result.tickets_processed}")
print(f"Tickets resueltos: {volume_result.tickets_resolved}")
print(f"Tiempo promedio respuesta: {volume_result.average_response_time:.1f} min")
print(f"Tasa chatbot: {volume_result.chatbot_resolution_rate:.1f}%")
print(f"Errores: {len(volume_result.errors)}")

# Prueba de estrés
stress_result = engine.simulate_stress_test(
    peak_tickets_per_minute=50,
    duration_minutes=10
)

# Escenario específico
scenario_result = engine.simulate_scenario(
    scenario_name="vip_customer_spike",
    scenario_config={}
)

# Escenario personalizado
custom_result = engine.simulate_scenario(
    scenario_name="custom",
    scenario_config={
        "ticket_count": 200,
        "priority_distribution": {"critical": 0.5, "urgent": 0.5},
        "category": "technical"
    }
)

# Reporte de simulaciones
report = engine.get_simulation_report()
print(f"Total simulaciones: {report['total_simulations']}")
print(f"Total tickets: {report['total_tickets_created']}")
print(f"Métricas promedio: {report['average_metrics']}")
```

## 🛡️ Disaster Recovery y Backup

### Sistema de Backup y Recuperación

**Archivo**: `workflow/kestra/flows/lib/support_disaster_recovery.py`

Características:
- **Múltiples tipos de backup**: Full, incremental, differential, snapshot
- **Backup automatizado**: Programable y automático
- **Recuperación**: Restauración de backups completos o parciales
- **Recovery points**: Puntos de recuperación verificados
- **Limpieza automática**: Limpia backups expirados
- **Verificación de integridad**: Tests de integridad de backups
- **Plan de recuperación**: Plan de recuperación generado automáticamente

### Uso

```python
from support_disaster_recovery import (
    DisasterRecoveryManager,
    BackupType,
    BackupStatus
)

manager = DisasterRecoveryManager(
    db_connection=db_conn,
    backup_location="/backups/support"
)

# Crear backup completo
backup = manager.create_backup(
    backup_type=BackupType.FULL,
    retention_days=30
)

print(f"Backup ID: {backup.backup_id}")
print(f"Estado: {backup.status.value}")
print(f"Tamaño: {backup.size_bytes / 1024 / 1024:.2f} MB")

# Backup incremental
incremental = manager.create_backup(
    backup_type=BackupType.INCREMENTAL,
    retention_days=7
)

# Restaurar backup
restore_result = manager.restore_backup(
    backup_id=backup.backup_id,
    target_tables=["support_tickets", "support_faq_articles"]
)

# Verificar integridad
integrity = manager.test_backup_integrity(backup.backup_id)
print(f"Integridad: {integrity['integrity_check']}")

# Estado de backups
status = manager.get_backup_status()
print(f"Backups completados: {status['completed']}")
print(f"Último backup: {status['last_backup']}")

# Plan de recuperación
recovery_plan = manager.get_recovery_plan()
print(f"Puntos de recuperación: {recovery_plan['available_recovery_points']}")
print(f"Recomendado: {recovery_plan['recommended_recovery_point']}")

# Limpiar backups antiguos
cleanup_result = manager.cleanup_old_backups()
print(f"Backups limpiados: {cleanup_result['cleaned_backups']}")
print(f"Espacio liberado: {cleanup_result['size_freed_bytes'] / 1024 / 1024:.2f} MB")
```

## 🚦 Rate Limiting Inteligente

### Sistema de Control de Tasa

**Archivo**: `workflow/kestra/flows/lib/support_rate_limiting.py`

Características:
- **4 estrategias**: Fixed window, sliding window, token bucket, leaky bucket
- **Múltiples identificadores**: Por IP, usuario, endpoint, etc.
- **Bloqueo temporal**: Bloqueo automático de abusadores
- **Estado en tiempo real**: Consulta estado de límites
- **Reset manual**: Reseteo de límites cuando sea necesario
- **Métricas**: Tracking de requests y límites

### Uso

```python
from support_rate_limiting import (
    RateLimiter,
    RateLimitStrategy
)

limiter = RateLimiter()

# Verificar rate limit (sliding window)
result = limiter.check_rate_limit(
    identifier="192.168.1.1",
    max_requests=100,
    window_seconds=60,
    strategy=RateLimitStrategy.SLIDING_WINDOW
)

if result.allowed:
    print(f"Request permitido. Quedan {result.remaining_requests} requests")
else:
    print(f"Rate limit excedido. Reintentar en {result.retry_after_seconds} segundos")

# Token bucket
result = limiter.check_rate_limit(
    identifier="user-123",
    max_requests=50,
    window_seconds=60,
    strategy=RateLimitStrategy.TOKEN_BUCKET
)

# Bloquear identificador
limiter.block_identifier("192.168.1.100", duration_seconds=3600)  # 1 hora

# Estado de rate limit
status = limiter.get_rate_limit_status("user-123")
if status:
    print(f"Estrategia: {status['strategy']}")
    print(f"Bloqueado: {status['is_blocked']}")
    if 'token_bucket' in status:
        print(f"Tokens: {status['token_bucket']['tokens']:.2f}")

# Reset
limiter.reset_limit("user-123")
```

## 🔔 Alertas Inteligentes Avanzadas

### Sistema de Alertas Contextuales y Predictivas

**Archivo**: `workflow/kestra/flows/lib/support_smart_alerts.py`

Características:
- **7 tipos de alertas**: Volumen, performance, calidad, SLA, anomalía, seguridad, predictivas
- **4 niveles de severidad**: Info, Warning, Critical, Emergency
- **Alertas contextuales**: Con contexto y métricas relevantes
- **Confianza ML**: Nivel de confianza para alertas predictivas
- **Reconocimiento y resolución**: Tracking de quién reconoce/resuelve
- **Reglas personalizables**: Agregar reglas de alerta personalizadas
- **Resúmenes**: Resúmenes por severidad, tipo y período

### Uso

```python
from support_smart_alerts import (
    SmartAlertEngine,
    AlertSeverity,
    AlertType
)

engine = SmartAlertEngine(db_connection)

# Evaluar métricas y generar alertas
metrics = {
    "tickets_per_hour": 150,
    "increase": 50,
    "critical_unanswered": 8,
    "satisfaction_score": 2.8,
    "drop": 20,
    "avg_response_time": 200
}

alerts = engine.evaluate_alerts(metrics)

for alert in alerts:
    print(f"{alert.severity.value.upper()}: {alert.title}")
    print(f"  {alert.message}")
    print(f"  Confianza: {alert.confidence:.2f}")
    print(f"  Contexto: {alert.context}")

# Obtener alertas activas
active = engine.get_active_alerts(severity=AlertSeverity.CRITICAL)
print(f"Alertas críticas activas: {len(active)}")

# Reconocer alerta
engine.acknowledge_alert(active[0].alert_id, "user-123")

# Resolver alerta
engine.resolve_alert(active[0].alert_id, actions_taken=["Escalado a equipo senior"])

# Resumen
summary = engine.get_alert_summary(hours=24)
print(f"Total alertas: {summary['total_alerts']}")
print(f"Activas: {summary['active_alerts']}")
print(f"Por severidad: {summary['by_severity']}")

# Agregar regla personalizada
custom_rule = {
    "rule_id": "custom_rule_1",
    "type": AlertType.PERFORMANCE,
    "condition": lambda data: data.get("avg_resolution_time", 0) > 480,
    "severity": AlertSeverity.WARNING,
    "title": "Tiempo de Resolución Alto",
    "message_template": "Tiempo promedio de resolución: {avg_resolution_time} minutos"
}
engine.add_alert_rule(custom_rule)
```

## 🌐 API Gateway y Gestión de APIs

### Sistema de API Gateway

**Archivo**: `workflow/kestra/flows/lib/support_api_gateway.py`

Características:
- **Versionado de APIs**: Soporte para múltiples versiones (v1, v2, v3, beta, alpha)
- **Routing inteligente**: Routing automático por versión y método
- **Autenticación**: Verificación de autenticación por endpoint
- **Rate limiting integrado**: Integración con rate limiter
- **Tracking de requests**: Historial completo de requests
- **Estadísticas**: Estadísticas de uso por endpoint, método y versión

### Uso

```python
from support_api_gateway import (
    APIGateway,
    APIEndpoint,
    RequestMethod,
    APIVersion
)

gateway = APIGateway()

# Registrar endpoint
def get_tickets_handler(params, body, headers, user_id):
    # Lógica del handler
    return {"tickets": []}

endpoint = APIEndpoint(
    endpoint_id="get-tickets-v1",
    path="/api/support/tickets",
    method=RequestMethod.GET,
    version=APIVersion.V1,
    handler=get_tickets_handler,
    rate_limit=100,  # 100 requests/minuto
    requires_auth=True
)

gateway.register_endpoint(endpoint)

# Manejar request
response = gateway.handle_request(
    path="/api/support/tickets",
    method="GET",
    version=APIVersion.V1,
    headers={"Authorization": "Bearer token123"},
    params={"status": "open"},
    client_ip="192.168.1.1",
    user_id="user-123"
)

print(f"Status: {response['status_code']}")
print(f"Data: {response.get('data')}")

# Listar endpoints
endpoints = gateway.get_endpoints(version=APIVersion.V1)
for ep in endpoints:
    print(f"{ep['method']} {ep['path']} ({ep['version']})")

# Estadísticas
stats = gateway.get_api_stats(hours=24)
print(f"Total requests: {stats['total_requests']}")
print(f"Por método: {stats['by_method']}")
```

## ⚖️ Load Balancing Inteligente

### Sistema de Distribución de Carga

**Archivo**: `workflow/kestra/flows/lib/support_load_balancer.py`

Características:
- **6 estrategias**: Round robin, least connections, least load, weighted, random, IP hash
- **Health checks**: Verificación de salud de recursos
- **Distribución de carga**: Tracking de carga y conexiones
- **Auto-scaling**: Preparado para escalado automático
- **Métricas**: Distribución de carga en tiempo real

### Uso

```python
from support_load_balancer import (
    LoadBalancer,
    Resource,
    LoadBalanceStrategy
)

balancer = LoadBalancer(strategy=LoadBalanceStrategy.LEAST_LOAD)

# Agregar recursos
agent1 = Resource(
    resource_id="agent-1",
    name="Agent Pool 1",
    weight=3,
    max_capacity=100
)

agent2 = Resource(
    resource_id="agent-2",
    name="Agent Pool 2",
    weight=2,
    max_capacity=80
)

balancer.add_resource(agent1)
balancer.add_resource(agent2)

# Seleccionar recurso
selected = balancer.select_resource(
    context={"client_ip": "192.168.1.1"}
)
print(f"Recurso seleccionado: {selected}")

# Asignar carga
balancer.allocate_load(selected, load=1)

# Liberar carga
balancer.release_load(selected, load=1)

# Actualizar salud
balancer.update_resource_health("agent-1", is_healthy=True)

# Distribución de carga
distribution = balancer.get_load_distribution()
print(f"Estrategia: {distribution['strategy']}")
print(f"Recursos saludables: {distribution['healthy_resources']}")
for res_id, info in distribution['distribution'].items():
    print(f"{info['name']}: {info['load_percentage']:.1f}% carga")
```

## 📊 Reportes Ejecutivos Avanzados

### Sistema de Reportes para Ejecutivos

**Archivo**: `workflow/kestra/flows/lib/support_executive_reports.py`

Características:
- **Múltiples períodos**: Semanal, mensual, trimestral, anual
- **Métricas clave**: KPIs principales del sistema
- **Insights automáticos**: Insights generados automáticamente
- **Tendencias**: Análisis de tendencias
- **Recomendaciones**: Recomendaciones estratégicas
- **Comparaciones**: vs período anterior y vs industria
- **Exportación**: JSON, HTML, PDF

### Uso

```python
from support_executive_reports import ExecutiveReportGenerator

generator = ExecutiveReportGenerator(db_connection)

# Generar reporte semanal
weekly_report = generator.generate_weekly_report()

print(f"Reporte: {weekly_report.report_id}")
print(f"Período: {weekly_report.period_start.date()} a {weekly_report.period_end.date()}")

print("\nMétricas Clave:")
for key, value in weekly_report.key_metrics.items():
    print(f"  {key}: {value}")

print("\nInsights:")
for insight in weekly_report.insights:
    print(f"  • {insight}")

print("\nRecomendaciones:")
for rec in weekly_report.recommendations:
    print(f"  • {rec}")

print("\nComparación con Período Anterior:")
for key, comp in weekly_report.vs_previous_period.items():
    change = comp.get('change_percentage', 0)
    print(f"  {key}: {change:+.1f}%")

# Reporte mensual
monthly_report = generator.generate_monthly_report()

# Exportar reporte
exported = generator.export_report(weekly_report, format="json")
print(f"\nReporte exportado (JSON): {len(str(exported))} caracteres")

# Exportar HTML
html_report = generator.export_report(weekly_report, format="html")
```

## 💰 Costos y Facturación

### Sistema de Gestión de Costos

**Archivo**: `workflow/kestra/flows/lib/support_cost_billing.py`

Características:
- **Cálculo de costos operativos**: Agentes, chatbot, infraestructura, terceros
- **Facturación por cliente**: Generación automática de facturas
- **Desglose de costos**: Por categoría con porcentajes
- **Historial de facturación**: Tracking por cliente
- **Configuración flexible**: Tarifas personalizables

### Uso

```python
from support_cost_billing import CostBillingManager
from datetime import datetime, timedelta

manager = CostBillingManager(db_connection)

# Calcular costos operativos
period_start = datetime.now() - timedelta(days=30)
period_end = datetime.now()

costs = manager.calculate_operational_costs(period_start, period_end)
print(f"Costo total: ${costs['total_cost']:.2f}")
print(f"Agentes: ${costs['categories']['agent_time']['total_cost']:.2f}")
print(f"Chatbot: ${costs['categories']['chatbot']['total_cost']:.2f}")

# Desglose de costos
breakdown = manager.get_cost_breakdown(period_start, period_end)
for category, data in breakdown['breakdown'].items():
    print(f"{category}: ${data['total_cost']:.2f} ({data['percentage']:.1f}%)")

# Generar facturación para cliente
billing = manager.generate_customer_billing(
    customer_id="customer@example.com",
    customer_name="Cliente ABC",
    period_start=period_start,
    period_end=period_end,
    billing_rate=15.0  # $15 por ticket
)

print(f"Factura: ${billing.total_cost:.2f}")
print(f"Tickets: {billing.tickets_handled}")

# Historial de facturación
history = manager.get_customer_billing_history("customer@example.com", months=6)
for bill in history:
    print(f"{bill.period_end.date()}: ${bill.total_cost:.2f}")
```

## ⏱️ Tracking Avanzado de SLA

### Sistema de Monitoreo de SLA

**Archivo**: `workflow/kestra/flows/lib/support_sla_tracking.py`

Características:
- **Tracking en tiempo real**: Monitoreo continuo de cumplimiento
- **5 estados de SLA**: On track, at risk, breached, met, missed
- **SLAs configurables**: Por prioridad, categoría, customer tier
- **Alertas proactivas**: Detecta tickets en riesgo
- **Reportes de cumplimiento**: Por período y prioridad
- **Métricas de compliance**: Porcentaje de cumplimiento y scores

### Uso

```python
from support_sla_tracking import (
    SLATracker,
    SLA,
    SLAStatus
)

tracker = SLATracker(db_connection)

# Trackear ticket
ticket_data = {
    "ticket_id": "ticket-123",
    "priority": "critical",
    "customer_tier": "vip",
    "created_at": datetime.now()
}

sla_tracking = tracker.track_ticket("ticket-123", ticket_data)
print(f"Estado: {sla_tracking.current_status.value}")
print(f"Horas restantes: {sla_tracking.hours_remaining:.1f}")
print(f"Compliance: {sla_tracking.compliance_percentage:.1f}%")

# Actualizar tracking
tracker.update_tracking("ticket-123", {"status": "in_progress"})

# Tickets en riesgo
at_risk = tracker.get_at_risk_tickets()
print(f"Tickets en riesgo: {len(at_risk)}")

# Tickets que incumplieron
breached = tracker.get_breached_tickets()
print(f"Tickets incumplidos: {len(breached)}")

# Reporte de cumplimiento
report = tracker.get_sla_compliance_report(period_start, period_end)
print(f"Tasa de cumplimiento: {report['summary']['compliance_rate']:.1f}%")
print(f"Por prioridad: {report['by_priority']}")

# Registrar SLA personalizado
custom_sla = SLA(
    sla_id="sla-custom",
    name="Custom SLA",
    description="SLA personalizado",
    target_hours=12.0,
    priority="high",
    category="technical"
)
tracker.register_sla(custom_sla)
```

## 🌍 Internacionalización (i18n)

### Sistema Multi-idioma Completo

**Archivo**: `workflow/kestra/flows/lib/support_i18n.py`

Características:
- **10+ locales**: Español (ES, MX, AR), Inglés (US, GB), Portugués (BR, PT), Francés, Alemán, Italiano
- **Traducciones completas**: Sistema, emails, notificaciones, dashboard, chatbot
- **Detección automática**: Desde headers HTTP (Accept-Language)
- **Formateo localizado**: Fechas y monedas según locale
- **Carga desde archivos**: JSON
- **Interpolación**: Variables en traducciones

### Uso

```python
from support_i18n import I18nManager, Locale

i18n = I18nManager(default_locale=Locale.ES_ES)

# Traducir
text = i18n.translate("ticket.resolved")
print(text)  # "Ticket resuelto"

# Con variables
text = i18n.translate(
    "email.ticket_resolved.body",
    customer_name="Juan Pérez",
    ticket_id="T-12345"
)
print(text)  # "Hola Juan Pérez, tu ticket #T-12345 ha sido resuelto."

# Usar alias corto
text = i18n.t("notification.new_ticket", subject="Error en API")

# Detectar locale desde request
locale = i18n.detect_locale_from_request({"Accept-Language": "es-MX,es;q=0.9"})
i18n.set_locale(locale)

# Formatear fecha
formatted_date = i18n.format_date(datetime.now(), locale=Locale.EN_US)
print(formatted_date)  # "01/15/2024 02:30 PM"

# Formatear moneda
formatted_currency = i18n.format_currency(1234.56, locale=Locale.ES_MX)
print(formatted_currency)  # "$1,234.56"

# Cargar traducciones desde archivo
i18n.load_translations_from_file("translations/es_MX.json", Locale.ES_MX)

# Agregar traducción personalizada
i18n.add_translation("custom.key", "Traducción personalizada", Locale.ES_ES)
```

## 📅 Integración con Calendario

### Sistema de Programación y Calendario

**Archivo**: `workflow/kestra/flows/lib/support_calendar_integration.py`

Características:
- **Múltiples proveedores**: Google Calendar, Outlook, iCal, custom
- **Eventos de seguimiento**: Follow-ups automáticos
- **Recordatorios**: Recordatorios para tickets
- **Reuniones de equipo**: Programación de reuniones
- **Horarios de agentes**: Gestión de disponibilidad
- **Exportación iCal**: Exporta a formato estándar
- **Eventos relacionados**: Vinculados a tickets

### Uso

```python
from support_calendar_integration import (
    CalendarIntegration,
    CalendarProvider,
    CalendarEvent
)

calendar = CalendarIntegration(provider=CalendarProvider.GOOGLE)

# Crear evento de seguimiento
follow_up = calendar.create_follow_up_event(
    ticket_id="ticket-123",
    customer_email="cliente@example.com",
    follow_up_date=datetime.now() + timedelta(days=3),
    description="Verificar que el problema se mantiene resuelto"
)

# Crear recordatorio
reminder = calendar.create_reminder(
    ticket_id="ticket-456",
    reminder_time=datetime.now() + timedelta(hours=2),
    message="Revisar ticket crítico"
)

# Programar reunión
meeting = calendar.schedule_agent_meeting(
    agent_ids=["agent-1", "agent-2", "agent-3"],
    meeting_time=datetime.now() + timedelta(days=1),
    duration_minutes=60,
    topic="Revisión de tickets críticos"
)

# Establecer disponibilidad de agente
calendar.set_agent_availability(
    agent_id="agent-123",
    agent_name="Juan",
    date=datetime.now().date(),
    shifts=[
        {"start": "09:00", "end": "13:00"},
        {"start": "14:00", "end": "18:00"}
    ],
    availability_hours=8.0
)

# Obtener horario
schedule = calendar.get_agent_schedule("agent-123", datetime.now().date())

# Eventos próximos
upcoming = calendar.get_upcoming_events(hours=24, event_type="follow_up")
for event in upcoming:
    print(f"{event.title} a las {event.start_time}")

# Eventos de un ticket
ticket_events = calendar.get_events_for_ticket("ticket-123")

# Exportar a iCal
ical_content = calendar.export_to_ical(calendar.events)
print(ical_content)
```

## 📊 Métricas de Negocio Avanzadas

### Sistema de Análisis de Métricas de Negocio

**Archivo**: `workflow/kestra/flows/lib/support_business_metrics.py`

Características:
- **Customer Lifetime Value (CLV)**: Cálculo de valor de cliente
- **Costo por Ticket**: Análisis de costos operativos
- **First Contact Resolution (FCR)**: Tasa de resolución en primer contacto
- **Net Promoter Score (NPS)**: Medición de satisfacción y recomendación
- **Productividad de Agentes**: Métricas individuales de rendimiento
- **Reportes completos**: Con insights y recomendaciones automáticas
- **Tracking de tendencias**: Comparación con períodos anteriores

### Uso

```python
from support_business_metrics import BusinessMetricsAnalyzer, MetricType
from datetime import datetime, timedelta

analyzer = BusinessMetricsAnalyzer(db_connection)

# Customer Lifetime Value
clv = analyzer.calculate_customer_lifetime_value(
    customer_id="customer@example.com",
    period_months=12
)
print(f"CLV: ${clv:.2f}")

# Costo por ticket
period_start = datetime.now() - timedelta(days=30)
period_end = datetime.now()

cost_per_ticket = analyzer.calculate_cost_per_ticket(period_start, period_end)
print(f"Costo por ticket: ${cost_per_ticket:.2f}")

# First Contact Resolution
fcr = analyzer.calculate_first_contact_resolution_rate(period_start, period_end)
print(f"FCR: {fcr:.1f}%")

# Net Promoter Score
nps = analyzer.calculate_net_promoter_score(period_start, period_end)
print(f"NPS: {nps:.1f}")

# Productividad de agente
productivity = analyzer.calculate_agent_productivity(
    agent_id="agent-123",
    period_start=period_start,
    period_end=period_end
)
print(f"Productividad: {productivity['productivity_score']:.1f}")
print(f"Tickets: {productivity['tickets_handled']}")
print(f"Satisfacción promedio: {productivity['avg_satisfaction']:.1f}")

# Reporte completo
report = analyzer.generate_business_metrics_report(period_start, period_end)

print(f"\nReporte de Métricas de Negocio")
print(f"Período: {report.period_start.date()} - {report.period_end.date()}")
print(f"\nMétricas:")
for metric in report.metrics:
    trend_symbol = "📈" if metric.trend == "up" else "📉" if metric.trend == "down" else "➡️"
    print(f"  {trend_symbol} {metric.name}: {metric.value:.2f} {metric.unit}")

print(f"\nInsights:")
for insight in report.insights:
    print(f"  • {insight}")

print(f"\nRecomendaciones:")
for recommendation in report.recommendations:
    print(f"  • {recommendation}")
```

## 🔮 Predicción de Churn

### Sistema de Predicción de Churn de Clientes

**Archivo**: `workflow/kestra/flows/lib/support_churn_prediction.py`

Características:
- **Análisis predictivo**: Calcula riesgo de churn basado en múltiples factores
- **Factores de riesgo**: Días sin contacto, satisfacción, tickets urgentes, tiempo de resolución
- **Niveles de riesgo**: Low, Medium, High, Critical
- **Recomendaciones automáticas**: Sugerencias de acciones preventivas
- **Tracking de acciones**: Registro de acciones preventivas tomadas
- **Predicción de días**: Estimación de días hasta posible churn

### Uso

```python
from support_churn_prediction import ChurnPredictor, ChurnRiskLevel
from datetime import datetime

predictor = ChurnPredictor(db_connection)

# Predecir churn para un cliente
prediction = predictor.predict_churn("customer@example.com", days_lookback=90)

print(f"Riesgo: {prediction.risk_level.value}")
print(f"Score: {prediction.risk_score:.1f}/100")
print(f"Confianza: {prediction.confidence:.1%}")
print(f"Días estimados: {prediction.predicted_churn_days}")

print(f"\nFactores:")
for factor_name, value in prediction.factors.items():
    print(f"  {factor_name}: {value:.1f}")

print(f"\nRecomendaciones:")
for rec in prediction.recommendations:
    print(f"  • {rec}")

# Obtener clientes en riesgo
at_risk = predictor.get_at_risk_customers(
    risk_level=ChurnRiskLevel.HIGH,
    limit=50
)

print(f"\nClientes en riesgo alto: {len(at_risk)}")
for p in at_risk[:5]:
    print(f"  {p.customer_id}: {p.risk_score:.1f}")

# Registrar acción preventiva
predictor.track_churn_prevention_action(
    customer_id="customer@example.com",
    action="outreach_call",
    agent_id="agent-123",
    notes="Llamada de seguimiento realizada"
)

# Historial de acciones
history = predictor.get_churn_prevention_history("customer@example.com")
for action in history:
    print(f"{action['created_at']}: {action['action_type']}")
```

## 📱 Integración con Redes Sociales

### Sistema de Gestión de Tickets desde Redes Sociales

**Archivo**: `workflow/kestra/flows/lib/support_social_media.py`

Características:
- **Multiplataforma**: Soporte para Twitter, Facebook, Instagram, LinkedIn, YouTube, TikTok, Reddit
- **Detección automática**: Crea tickets desde menciones, mensajes directos, comentarios
- **Análisis de prioridad**: Detecta urgencia en mensajes sociales
- **Respuestas integradas**: Permite responder desde el sistema
- **Tracking completo**: Guarda mensajes originales y respuestas
- **Monitoreo**: Sistema de monitoreo de menciones (requiere APIs)

### Uso

```python
from support_social_media import (
    SocialMediaIntegration,
    SocialPlatform,
    SocialMessage,
    SocialMessageType
)
from datetime import datetime

integration = SocialMediaIntegration(db_connection)

# Crear ticket desde mensaje de Twitter
message = SocialMessage(
    platform=SocialPlatform.TWITTER,
    message_id="1234567890",
    message_type=SocialMessageType.MENTION,
    author_id="user123",
    author_name="Juan Pérez",
    author_username="@juanperez",
    content="@support Necesito ayuda urgente con mi cuenta",
    url="https://twitter.com/status/1234567890",
    created_at=datetime.now(),
    metadata={"retweet_count": 5}
)

ticket = integration.create_ticket_from_social_message(
    message,
    customer_email="juan@example.com"
)

print(f"Ticket creado: {ticket.ticket_id}")
print(f"Prioridad: {ticket.priority}")
print(f"Plataforma: {ticket.platform.value}")

# Responder a mensaje social
response = integration.respond_to_social_message(
    ticket_id=ticket.ticket_id,
    response_text="Hola @juanperez, estamos revisando tu caso. Te contactaremos pronto.",
    agent_id="agent-123"
)

print(f"Respuesta enviada a {response['to_username']}")

# Obtener tickets de redes sociales
social_tickets = integration.get_social_tickets(
    platform=SocialPlatform.TWITTER,
    status="open",
    limit=20
)

print(f"\nTickets de Twitter: {len(social_tickets)}")
for t in social_tickets:
    print(f"  {t.ticket_id}: {t.customer_username} - {t.priority}")
```

## 🔐 Autenticación y Autorización

### Sistema de Seguridad y Control de Acceso

**Archivo**: `workflow/kestra/flows/lib/support_auth_authorization.py`

Características:
- **Gestión de usuarios**: Creación y administración de usuarios
- **Roles y permisos**: Sistema granular de permisos
- **Autenticación**: Login con email/contraseña y tokens JWT
- **API Keys**: Generación y gestión de claves API
- **Control de acceso**: Verificación de permisos por operación
- **Seguridad**: Hash de contraseñas, tokens seguros, expiración

### Uso

```python
from support_auth_authorization import (
    AuthManager,
    Role,
    Permission
)

auth = AuthManager(db_connection, secret_key="tu-clave-secreta")

# Crear usuario
user = auth.create_user(
    email="agent@example.com",
    username="agent01",
    password="password123",
    role=Role.AGENT,
    metadata={"department": "support"}
)

print(f"Usuario creado: {user.user_id}")

# Autenticar
token = auth.authenticate("agent@example.com", "password123")
if token:
    print(f"Token: {token.token[:20]}...")
    print(f"Expira: {token.expires_at}")

# Verificar token
user = auth.verify_token(token.token)
if user:
    print(f"Usuario autenticado: {user.username}")
    
    # Verificar permisos
    can_edit = auth.check_permission(user, Permission.EDIT_TICKET)
    can_delete = auth.check_permission(user, Permission.DELETE_TICKET)
    
    print(f"Puede editar: {can_edit}")
    print(f"Puede eliminar: {can_delete}")

# Crear API Key
api_key, key_obj = auth.create_api_key(
    user_id=user.user_id,
    name="Production API Key",
    permissions={
        Permission.CREATE_TICKET,
        Permission.VIEW_TICKET,
        Permission.USE_API
    },
    expires_days=365
)

print(f"\nAPI Key creada: {api_key}")
print(f"Permisos: {[p.value for p in key_obj.permissions]}")

# Verificar API Key
verified_key = auth.verify_api_key(api_key)
if verified_key:
    print(f"API Key válida: {verified_key.name}")
    print(f"Último uso: {verified_key.last_used}")

# Revocar API Key
auth.revoke_api_key(key_obj.key_id)
print("API Key revocada")
```

## 😊 Satisfacción del Cliente Avanzada

### Sistema de Análisis de Satisfacción Profundo

**Archivo**: `workflow/kestra/flows/lib/support_customer_satisfaction.py`

Características:
- **Análisis de satisfacción**: Calcula scores por componente (tiempo, calidad, agente, chatbot)
- **Tendencias**: Identifica mejoras o declinaciones en satisfacción
- **Insights automáticos**: Detecta problemas y genera recomendaciones
- **Perfiles de clientes**: Análisis individual de satisfacción por cliente
- **Clientes en riesgo**: Identifica clientes con satisfacción baja
- **Reportes completos**: Genera reportes detallados con métricas y recomendaciones

### Uso

```python
from support_customer_satisfaction import (
    CustomerSatisfactionAnalyzer,
    SatisfactionTrend
)

analyzer = CustomerSatisfactionAnalyzer(db_connection)

# Calcular score de satisfacción
score = analyzer.calculate_satisfaction_score(days=30)

print(f"Score general: {score.overall_score:.2f}/5.0")
print(f"Tiempo de respuesta: {score.response_time_score:.2f}/5.0")
print(f"Calidad: {score.resolution_quality_score:.2f}/5.0")
print(f"Tendencia: {score.trend.value}")
print(f"Confianza: {score.confidence:.1%}")
print(f"Muestra: {score.sample_size} tickets")

# Analizar insights
insights = analyzer.analyze_satisfaction_insights(days=30)

print(f"\nInsights encontrados: {len(insights)}")
for insight in insights:
    print(f"\n{insight.title}")
    print(f"  Severidad: {insight.severity}")
    print(f"  {insight.description}")
    print(f"  Recomendación: {insight.recommendation}")

# Perfil de satisfacción de un cliente
profile = analyzer.get_customer_satisfaction_profile(
    "customer@example.com",
    days=90
)

print(f"\nPerfil de Cliente:")
print(f"  Score promedio: {profile.average_score:.2f}/5.0")
print(f"  Total tickets: {profile.total_tickets}")
print(f"  Tendencia: {profile.sentiment_trend.value}")
print(f"  Nivel de riesgo: {profile.risk_level}")
print(f"  Recomendaciones:")
for rec in profile.recommendations:
    print(f"    • {rec}")

# Clientes en riesgo
at_risk = analyzer.get_at_risk_customers(threshold=3.0, limit=20)

print(f"\nClientes en riesgo: {len(at_risk)}")
for customer in at_risk[:5]:
    print(f"  {customer.customer_email}: {customer.average_score:.2f}")

# Reporte completo
report = analyzer.generate_satisfaction_report(days=30)

print(f"\nReporte de Satisfacción:")
print(f"  Score general: {report['overall_score']:.2f}")
print(f"  Tendencia: {report['trend']}")
print(f"  Insights: {len(report['insights'])}")
print(f"  Clientes en riesgo: {report['at_risk_customers']}")
```

## 🎓 Capacitación Automática de Agentes

### Sistema de Identificación y Gestión de Capacitación

**Archivo**: `workflow/kestra/flows/lib/support_agent_training.py`

Características:
- **Identificación automática**: Detecta necesidades de capacitación basadas en métricas
- **Módulos de capacitación**: Crea y gestiona contenido de capacitación
- **Asignación inteligente**: Asigna capacitación según necesidades identificadas
- **Seguimiento de progreso**: Monitorea el avance de cada agente
- **Gaps de habilidades**: Identifica áreas de mejora
- **Reportes de capacitación**: Genera reportes de estado y necesidades

### Uso

```python
from support_agent_training import (
    AgentTrainingManager,
    TrainingTopic,
    TrainingStatus
)

manager = AgentTrainingManager(db_connection)

# Identificar necesidades de capacitación
needs = manager.identify_training_needs(days=30)

print(f"Necesidades identificadas: {len(needs)}")
for need in needs:
    print(f"\nAgente: {need.agent_id}")
    print(f"  Tema: {need.topic.value}")
    print(f"  Prioridad: {need.priority}")
    print(f"  Razón: {need.reason}")
    print(f"  Módulos recomendados: {need.recommended_modules}")

# Crear módulo de capacitación
module = manager.create_training_module(
    module_id="time_management_basics",
    title="Gestión de Tiempo Básica",
    description="Aprende a gestionar tu tiempo eficientemente",
    topic=TrainingTopic.TIME_MANAGEMENT,
    content="# Contenido del módulo...",
    duration_minutes=60,
    prerequisites=["intro_to_support"],
    assessment_questions=[
        {
            "question": "¿Cuál es el tiempo objetivo de resolución?",
            "options": ["30 min", "60 min", "120 min"],
            "correct": 1
        }
    ]
)

print(f"Módulo creado: {module.module_id}")

# Asignar capacitación
assignment = manager.assign_training(
    agent_id="agent-123",
    module_id="time_management_basics",
    due_date=datetime.now() + timedelta(days=7)
)

print(f"Capacitación asignada: {assignment['assignment_id']}")

# Obtener progreso de agente
progress = manager.get_agent_progress("agent-123")

print(f"\nProgreso del Agente:")
print(f"  Módulos completados: {progress.completed_modules}/{progress.total_modules}")
print(f"  Tasa de completación: {progress.completion_rate:.1f}%")
print(f"  Entrenamiento actual: {progress.current_training}")
print(f"  Gaps identificados: {len(progress.skill_gaps)}")
print(f"  Próximos recomendados: {progress.next_recommended}")

# Completar capacitación
completion = manager.complete_training(
    agent_id="agent-123",
    module_id="time_management_basics",
    score=85.5
)

print(f"\nCapacitación completada: {completion['success']}")

# Reporte de capacitación
report = manager.generate_training_report(days=30)

print(f"\nReporte de Capacitación:")
print(f"  Completadas: {report['statistics']['completed']}")
print(f"  En progreso: {report['statistics']['in_progress']}")
print(f"  Pendientes: {report['statistics']['pending']}")
print(f"  Score promedio: {report['statistics']['avg_score']:.1f}")
print(f"  Necesidades totales: {report['training_needs']['total']}")
```

## 📊 Métricas de Agentes Avanzadas

### Sistema de Análisis de Rendimiento de Agentes

**Archivo**: `workflow/kestra/flows/lib/support_agent_metrics.py`

Características:
- **Métricas completas**: Volumen, tiempos, calidad, eficiencia
- **Score de performance**: Calcula score 0-100 basado en múltiples factores
- **Niveles de rendimiento**: Clasifica agentes (Excellent, Good, Average, etc.)
- **Métricas de equipo**: Análisis a nivel de equipo/departamento
- **Leaderboards**: Rankings de mejor rendimiento
- **Recomendaciones**: Sugerencias de mejora personalizadas
- **Tendencias**: Compara períodos para identificar mejoras/declinaciones

### Uso

```python
from support_agent_metrics import (
    AgentMetricsAnalyzer,
    PerformanceLevel
)

analyzer = AgentMetricsAnalyzer(db_connection)

# Calcular métricas de un agente
metrics = analyzer.calculate_agent_metrics("agent-123", days=30)

print(f"Métricas del Agente:")
print(f"  Tickets asignados: {metrics.tickets_assigned}")
print(f"  Tickets resueltos: {metrics.tickets_resolved}")
print(f"  Tasa de resolución: {metrics.resolution_rate:.1f}%")
print(f"  Tiempo promedio: {metrics.avg_resolution_time_minutes:.0f} min")
print(f"  Satisfacción: {metrics.avg_satisfaction_score:.2f}/5.0")
print(f"  Performance score: {metrics.performance_score:.1f}/100")
print(f"  Nivel: {metrics.performance_level.value}")

# Métricas de equipo
team = analyzer.get_team_metrics(department="support", days=30)

print(f"\nMétricas del Equipo:")
print(f"  Agentes activos: {team.active_agents}/{team.total_agents}")
print(f"  Tickets totales: {team.total_tickets}")
print(f"  Resueltos: {team.total_resolved}")
print(f"  Score del equipo: {team.team_performance_score:.1f}/100")
print(f"\n  Top Performers:")
for performer in team.top_performers:
    print(f"    {performer['agent_name']}: {performer['score']:.1f}")
print(f"\n  Necesitan Apoyo:")
for agent in team.agents_needing_support:
    print(f"    {agent['agent_name']}: {agent['score']:.1f}")

# Reporte completo de agente
report = analyzer.generate_agent_report("agent-123", days=30)

print(f"\nReporte Completo:")
print(f"  Performance: {report['performance']['score']:.1f}")
print(f"  vs Promedio del equipo: {report['performance']['vs_team_average']:+.1f}")
print(f"\n  Tendencias:")
for metric, trend in report['trends'].items():
    print(f"    {metric}: {trend}")
print(f"\n  Recomendaciones:")
for rec in report['recommendations']:
    print(f"    • {rec}")

# Leaderboard
leaderboard = analyzer.get_leaderboard(department="support", days=30, limit=10)

print(f"\nLeaderboard (Top 10):")
for i, agent in enumerate(leaderboard, 1):
    print(f"{i}. {agent['agent_name']}: {agent['performance_score']:.1f} "
          f"({agent['performance_level']})")
```

## 📝 Templates de Tickets y Respuestas

### Sistema de Templates Reutilizables

**Archivo**: `workflow/kestra/flows/lib/support_ticket_templates.py`

Características:
- **Templates dinámicos**: Respuestas con variables reutilizables
- **Búsqueda inteligente**: Sugerencias basadas en categoría y contenido
- **Estadísticas de uso**: Tracking de uso y satisfacción
- **Múltiples tipos**: Respuestas, seguimientos, escalaciones, cierres
- **Categorización**: Organización por categorías y tags
- **Relevancia**: Scoring de templates por relevancia

### Uso

```python
from support_ticket_templates import (
    TemplateManager,
    TemplateType,
    TemplateCategory
)

manager = TemplateManager(db_connection)

# Crear template
template = manager.create_template(
    template_id="billing_refund_template",
    title="Reembolso de Facturación",
    description="Template para solicitudes de reembolso",
    template_type=TemplateType.RESPONSE,
    category=TemplateCategory.BILLING,
    content="""
Hola {{customer_name}},

Gracias por contactarnos sobre tu solicitud de reembolso.

Hemos procesado tu solicitud para el ticket {{ticket_id}}.
El reembolso de {{amount}} será procesado en los próximos {{days}} días hábiles.

Si tienes alguna pregunta adicional, no dudes en contactarnos.

Saludos,
{{agent_name}}
    """,
    tags=["billing", "refund"],
    created_by="admin"
)

print(f"Template creado: {template.template_id}")

# Buscar templates
templates = manager.search_templates(
    template_type=TemplateType.RESPONSE,
    category=TemplateCategory.BILLING,
    search_text="reembolso"
)

print(f"\nTemplates encontrados: {len(templates)}")
for t in templates:
    print(f"  {t.title}: usado {t.usage_count} veces")

# Sugerir templates para un ticket
suggestions = manager.suggest_templates(
    ticket_category="billing",
    ticket_subject="Necesito un reembolso",
    ticket_description="Quiero reembolsar mi suscripción",
    limit=5
)

print(f"\nTemplates sugeridos:")
for sug in suggestions:
    print(f"  {sug['title']} (relevancia: {sug['relevance']})")

# Renderizar template con variables
response = manager.render_template(
    template_id="billing_refund_template",
    variables={
        "customer_name": "Juan Pérez",
        "ticket_id": "TICK-123",
        "amount": "$50.00",
        "days": "5-7",
        "agent_name": "María"
    }
)

print(f"\nRespuesta generada:\n{response}")

# Registrar uso
manager.record_template_usage(
    template_id="billing_refund_template",
    ticket_id="TICK-123",
    satisfaction_score=4.5
)

# Estadísticas
stats = manager.get_template_statistics("billing_refund_template")
print(f"\nEstadísticas del template:")
print(f"  Uso total: {stats['total_uses']}")
print(f"  Satisfacción promedio: {stats['avg_satisfaction']:.2f}")
```

## 🔍 Detección de Tickets Duplicados

### Sistema de Identificación de Duplicados

**Archivo**: `workflow/kestra/flows/lib/support_duplicate_detection.py`

Características:
- **Detección inteligente**: Múltiples algoritmos de similitud
- **Análisis de texto**: Comparación de subject y description
- **Factores múltiples**: Email, categoría, tags, contenido
- **Niveles de similitud**: Exact, Very High, High, Medium, Low
- **Agrupación**: Identifica grupos de tickets duplicados
- **Merge automático**: Fusión de tickets duplicados

### Uso

```python
from support_duplicate_detection import (
    DuplicateDetector,
    SimilarityLevel
)

detector = DuplicateDetector(db_connection)

# Detectar duplicados para un ticket
matches = detector.detect_duplicates(
    ticket_id="TICK-123",
    days_back=30,
    min_similarity=0.7
)

print(f"Duplicados encontrados: {len(matches)}")
for match in matches:
    print(f"\n  Ticket: {match.similar_ticket_id}")
    print(f"  Similitud: {match.similarity_score:.1%}")
    print(f"  Nivel: {match.similarity_level.value}")
    print(f"  Campos coincidentes: {match.matching_fields}")
    print(f"  Confianza: {match.confidence:.1%}")

# Encontrar grupos de duplicados
groups = detector.find_duplicate_groups(
    days_back=30,
    min_similarity=0.7
)

print(f"\nGrupos de duplicados: {len(groups)}")
for group in groups[:5]:
    print(f"\n  Grupo {group.group_id}:")
    print(f"  Tickets: {len(group.ticket_ids)}")
    print(f"  Ticket principal: {group.primary_ticket_id}")

# Mergear duplicados
merge_result = detector.merge_duplicates(
    primary_ticket_id="TICK-123",
    duplicate_ticket_ids=["TICK-456", "TICK-789"],
    merge_notes="Tickets duplicados mergeados automáticamente"
)

print(f"\nMerge completado:")
print(f"  Tickets mergeados: {merge_result['merged_count']}")
print(f"  Ticket principal: {merge_result['primary_ticket_id']}")
```

## 💚 Health Score de Clientes

### Sistema de Monitoreo de Salud de Clientes

**Archivo**: `workflow/kestra/flows/lib/support_customer_health.py`

Características:
- **Health score 0-100**: Score compuesto de múltiples factores
- **Estados de salud**: Excellent, Good, Fair, At Risk, Critical
- **Factores múltiples**: Volumen de tickets, satisfacción, engagement, churn risk
- **Recomendaciones**: Acciones sugeridas basadas en score
- **Factores de riesgo**: Identificación de problemas
- **Reportes**: Análisis de salud de clientes

### Uso

```python
from support_customer_health import (
    CustomerHealthAnalyzer,
    HealthStatus
)

analyzer = CustomerHealthAnalyzer(db_connection)

# Calcular health score
health = analyzer.calculate_health_score("customer@example.com", days=90)

print(f"Health Score: {health.health_score:.1f}/100")
print(f"Estado: {health.health_status.value}")
print(f"\nComponentes:")
print(f"  Volumen de tickets: {health.ticket_volume_score:.1f}")
print(f"  Satisfacción: {health.satisfaction_score:.1f}")
print(f"  Engagement: {health.engagement_score:.1f}")
print(f"  Churn risk: {health.churn_risk_score:.1f}")
print(f"  Tiempo de respuesta: {health.response_time_score:.1f}")

print(f"\nMétricas:")
print(f"  Total tickets: {health.total_tickets}")
print(f"  Satisfacción promedio: {health.avg_satisfaction:.2f}/5.0")
print(f"  Días desde último ticket: {health.days_since_last_ticket}")
print(f"  Probabilidad de churn: {health.churn_probability:.1%}")

print(f"\nFactores de riesgo:")
for factor in health.risk_factors:
    print(f"  • {factor}")

print(f"\nRecomendaciones:")
for rec in health.recommendations:
    print(f"  • {rec}")

# Clientes en riesgo
at_risk = analyzer.get_at_risk_customers(health_threshold=40.0, limit=20)

print(f"\nClientes en riesgo: {len(at_risk)}")
for customer in at_risk[:5]:
    print(f"  {customer.customer_email}: {customer.health_score:.1f} "
          f"({customer.health_status.value})")

# Reporte de salud
report = analyzer.generate_health_report(days=90)

print(f"\nReporte de Salud:")
print(f"  Clientes analizados: {report['total_customers_analyzed']}")
print(f"  Score promedio: {report['average_health_score']:.1f}")
print(f"  Score mediano: {report['median_health_score']:.1f}")
print(f"  En riesgo: {report['at_risk_count']}")
print(f"\nDistribución:")
for status, count in report['status_distribution'].items():
    print(f"  {status}: {count}")
```

## 🚀 Resolución Proactiva

### Sistema de Identificación y Ejecución de Acciones Preventivas

**Archivo**: `workflow/kestra/flows/lib/support_proactive_resolution.py`

Características:
- **Detección de patrones**: Identifica problemas antes de que escalen
- **Acciones preventivas**: Múltiples tipos de acciones proactivas
- **Priorización**: Critical, High, Medium, Low
- **Impacto estimado**: Predicción de impacto de acciones
- **Tracking**: Seguimiento de ejecución de acciones
- **Reportes**: Análisis de oportunidades proactivas

### Uso

```python
from support_proactive_resolution import (
    ProactiveResolutionEngine,
    ProactiveActionType,
    ActionPriority
)

engine = ProactiveResolutionEngine(db_connection)

# Identificar acciones proactivas
actions = engine.identify_proactive_actions(days_back=30)

print(f"Acciones proactivas identificadas: {len(actions)}")
for action in actions[:10]:
    print(f"\n{action.title}")
    print(f"  Tipo: {action.action_type.value}")
    print(f"  Prioridad: {action.priority.value}")
    print(f"  Confianza: {action.confidence:.1%}")
    print(f"  Impacto: {action.predicted_impact}")
    print(f"  Recomendación: {action.recommended_action}")

# Ejecutar acción
result = engine.execute_action(
    action_id="recurring_technical_api_errors",
    executed_by="agent-123",
    notes="FAQ creada y documentación actualizada"
)

print(f"\nAcción ejecutada: {result['success']}")

# Reporte proactivo
report = engine.generate_proactive_report(days=30)

print(f"\nReporte Proactivo:")
print(f"  Total acciones: {report['total_actions']}")
print(f"\nPor tipo:")
for type_name, count in report['by_type'].items():
    print(f"  {type_name}: {count}")
print(f"\nPor prioridad:")
for priority, count in report['by_priority'].items():
    print(f"  {priority}: {count}")
print(f"\nTop acciones:")
for action in report['top_actions']:
    print(f"  {action['title']} ({action['priority']})")
```

---

## 📊 Resumen del Sistema

### Estadísticas del Sistema

- **58 Módulos Python** - Funcionalidades completas y especializadas
- **22 Tablas de Base de Datos** - Esquema completo y normalizado
- **3 Workflows Kestra** - Automatización de procesos
- **7 DAGs Airflow** - Tareas programadas y monitoreo
- **6+ Endpoints API REST** - Integración completa
- **Múltiples Integraciones** - HubSpot, ManyChat, Redes Sociales, Calendarios

### Funcionalidades Principales

#### 🤖 Automatización Inteligente
- Chatbot con LLM para FAQs
- Priorización automática basada en ML
- Enrutamiento inteligente
- Escalación automática
- Workflow builder visual

#### 📊 Análisis y Métricas
- Métricas en tiempo real
- Analytics avanzado
- Forecasting y predicciones
- Detección de anomalías
- Métricas de negocio (CLV, NPS, FCR)
- Predicción de churn

#### 🔐 Seguridad y Compliance
- Autenticación y autorización
- Control de acceso granular
- API Keys gestionadas
- Seguridad y compliance (GDPR, HIPAA)
- Rate limiting inteligente
- Disaster recovery

#### 🌐 Integraciones
- Redes sociales (Twitter, Facebook, Instagram, etc.)
- Calendarios (Google, Outlook)
- CRM (HubSpot)
- Mensajería (ManyChat, WhatsApp)
- Métricas externas (Prometheus/Grafana)

#### 🎯 Optimización y Eficiencia
- Auto-optimización del sistema
- Caching inteligente
- Load balancing
- Batch processing
- Predicción de carga de trabajo
- Gestión de costos

#### 👥 Colaboración
- Colaboración entre agentes
- Copilot para agentes
- Gamificación
- Learning engine
- Quality assurance automático

#### 📈 Reportes y Analytics
- Reportes ejecutivos
- Dashboard en tiempo real
- Benchmarking con industria
- ROI analysis
- SLA tracking avanzado

---

## 🚀 Próximos Pasos

1. **Configurar Base de Datos**: Ejecutar `support_tickets_schema.sql`
2. **Instalar Dependencias**: `pip install -r requirements.txt`
3. **Configurar Variables**: Ajustar configuraciones en `config.py`
4. **Desplegar Workflows**: Configurar Kestra y Airflow
5. **Probar Integraciones**: Verificar conexiones con servicios externos

---

## 📝 Notas

- El sistema es modular y extensible
- Cada módulo puede funcionar de forma independiente
- Todas las funcionalidades están documentadas con ejemplos
- Las tablas de base de datos incluyen índices optimizados
- El sistema soporta escalamiento horizontal

---

**Versión**: 3.1  
**Última actualización**: 2024  
**Módulos**: 54  
**Estado**: ✅ Producción Ready

