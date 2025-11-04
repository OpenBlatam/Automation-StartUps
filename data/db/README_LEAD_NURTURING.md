# Secuencias de Nutrición de Leads - Documentación Completa

## 🎯 Objetivo

Sistema automatizado que **aumenta la tasa de conversión de leads fríos a calificados** mediante secuencias de nutrición inteligentes basadas en comportamiento.

## 📋 Componentes del Sistema

### 1. Schema de Base de Datos (`lead_nurturing_schema.sql`)

#### Tablas Principales

**`nurturing_sequence_templates`**
- Templates reutilizables de secuencias
- Configuración de pasos, timing y contenido
- Filtros por prioridad y score de leads

**`lead_nurturing_sequences`**
- Secuencias activas de nutrición por lead
- Tracking de progreso (paso actual, estado, timing)
- Estados: `active`, `paused`, `completed`, `stopped`, `qualified`

**`lead_nurturing_events`**
- Eventos individuales (emails enviados)
- Tracking completo de engagement: opens, clicks, replies
- Metadata en JSONB para información adicional

**`lead_nurturing_engagement_summary`**
- Resumen agregado de engagement por secuencia
- Optimizado para queries rápidas
- Actualizado automáticamente vía función SQL

**`mv_nurturing_conversion_metrics`**
- Vista materializada con métricas diarias
- Tasa de conversión, open rate, click rate, reply rate
- Refrescar periódicamente

#### Instalación

```sql
-- Ejecutar en Postgres
\i data/db/lead_nurturing_schema.sql
```

### 2. DAG de Airflow (`lead_nurturing.py`)

**Schedule**: Cada 4 horas (`0 */4 * * *`)

#### Tareas del Pipeline

1. **`ensure_schema`** - Verifica que el schema esté creado
2. **`identify_cold_leads`** - Encuentra leads fríos que necesitan nutrición
3. **`get_or_create_sequence_template`** - Obtiene/crea template por defecto
4. **`start_nurturing_sequences`** - Inicia nuevas secuencias
5. **`send_scheduled_emails`** - Envía emails programados
6. **`update_engagement`** - Actualiza engagement y califica leads
7. **`auto_pause_inactive_sequences`** - Pausa secuencias sin actividad
8. **`refresh_conversion_metrics`** - Refresca vista de métricas
9. **`notify_summary`** - Envía resumen a Slack (opcional)

## ⚙️ Configuración

### Parámetros del DAG

| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `postgres_conn_id` | string | `postgres_default` | Connection ID de Airflow |
| `email_webhook_url` | string | (requerido) | Webhook para envío de emails |
| `engagement_api_url` | string | `""` | API para verificar engagement |
| `max_leads_per_run` | integer | `100` | Máx leads a procesar por ejecución |
| `min_score_to_qualify` | integer | `50` | Score mínimo para calificar |
| `enable_auto_pause` | boolean | `true` | Pausar secuencias sin engagement |
| `pause_after_days` | integer | `30` | Días sin engagement para pausar |
| `dry_run` | boolean | `false` | Solo simular sin enviar |
| `email_from` | string | `marketing@...` | Remitente de emails |
| `slack_webhook_url` | string | `""` | Webhook de Slack |
| `request_timeout` | integer | `30` | Timeout para requests (segundos) |
| `max_retry_attempts` | integer | `3` | Intentos de retry |

### Webhook de Email

Formato esperado:

```json
POST {email_webhook_url}
{
  "from": "marketing@tu-dominio.com",
  "to": "lead@example.com",
  "subject": "Asunto personalizado",
  "text": "Cuerpo del email",
  "metadata": {
    "sequence_id": 123,
    "lead_ext_id": "lead_123",
    "step_number": 1,
    "sequence_name": "default_cold_lead_nurturing"
  }
}
```

### API de Engagement (Opcional)

Si proporcionas `engagement_api_url`:

```
GET {engagement_api_url}?email={email}
```

Respuesta esperada:

```json
{
  "opened": true,
  "clicked": false,
  "replied": false
}
```

## 📊 Uso y Consultas

### Ver Secuencias Activas

```sql
SELECT 
    s.id,
    l.email,
    l.first_name,
    s.current_step,
    s.total_steps,
    s.status,
    s.next_send_at,
    s.completion_rate,
    s.qualified_at
FROM lead_nurturing_sequences s
JOIN leads l ON s.lead_ext_id = l.ext_id
WHERE s.status = 'active'
ORDER BY s.next_send_at ASC;
```

### Ver Métricas de Conversión

```sql
SELECT 
    date,
    total_sequences_started,
    leads_qualified,
    conversion_rate_pct,
    open_rate_pct,
    reply_rate_pct,
    avg_days_to_qualify
FROM mv_nurturing_conversion_metrics
ORDER BY date DESC
LIMIT 30;
```

### Ver Engagement por Secuencia

```sql
SELECT 
    s.id,
    l.email,
    es.total_emails_sent,
    es.total_emails_opened,
    es.total_emails_replied,
    es.open_rate,
    es.reply_rate,
    es.engagement_score
FROM lead_nurturing_sequences s
JOIN leads l ON s.lead_ext_id = l.ext_id
LEFT JOIN lead_nurturing_engagement_summary es ON s.id = es.sequence_id
WHERE s.status IN ('active', 'qualified')
ORDER BY es.engagement_score DESC;
```

### Crear Template Personalizado

```sql
INSERT INTO nurturing_sequence_templates 
(name, description, priority_filter, min_score, max_score, total_steps, steps_config, enabled)
VALUES (
    'vip_nurturing',
    'Secuencia para leads VIP',
    'high',
    0,
    100,
    3,
    '[
        {
            "step": 1,
            "delay_days": 0,
            "subject_template": "{{first_name}}, acceso VIP",
            "body_template": "Contenido personalizado para VIP..."
        },
        {
            "step": 2,
            "delay_days": 2,
            "subject_template": "{{first_name}}, seguimiento VIP",
            "body_template": "..."
        }
    ]'::jsonb,
    true
);
```

## 🔄 Flujo del Sistema

```
1. Identificar Leads Fríos
   ↓
2. Iniciar Secuencias
   ↓
3. Enviar Emails Programados
   ↓
4. Actualizar Engagement
   ↓
5. Calificar Leads (si alcanzan score mínimo)
   ↓
6. Pausar Secuencias Inactivas
   ↓
7. Refrescar Métricas
```

## 📈 Métricas y KPIs

El sistema rastrea automáticamente:

- **Tasa de conversión**: % de leads que se califican desde fríos
- **Open rate**: % de emails abiertos
- **Click rate**: % de emails con clicks
- **Reply rate**: % de emails con respuesta
- **Tiempo promedio a calificación**: Días desde inicio hasta qualified_at
- **Engagement score**: Score calculado basado en opens/clicks/replies

## 🎯 Cálculo de Scores

### Score de Engagement

- **Reply**: +15 puntos (1 reply), +25 puntos (2+ replies)
- **Click**: +8 puntos (1 click), +12 puntos (2+ clicks)
- **Open**: +5 puntos (2 opens), +10 puntos (3 opens), +15 puntos (4+ opens)

### Calificación Automática

Un lead se califica automáticamente cuando:
- Su score total alcanza `min_score_to_qualify` (default: 50)
- Ha mostrado engagement significativo (reply o click)

## 🚨 Troubleshooting

### Leads no se identifican como fríos

```sql
SELECT ext_id, email, score, priority 
FROM leads 
WHERE email IS NOT NULL 
  AND (score IS NULL OR score < 50)
  AND (priority IS NULL OR priority = 'low')
  AND created_at >= CURRENT_DATE - INTERVAL '90 days';
```

### Emails no se envían

1. Verificar `email_webhook_url` está configurado
2. Revisar logs del task `send_scheduled_emails`
3. Verificar `next_send_at <= NOW()` en secuencias activas:

```sql
SELECT id, email, current_step, next_send_at, status
FROM lead_nurturing_sequences
WHERE status = 'active' AND next_send_at <= NOW();
```

### Engagement no se actualiza

1. Verificar `engagement_api_url` si está configurado
2. Revisar logs del task `update_engagement`
3. Verificar eventos tienen `status = 'sent'`:

```sql
SELECT id, email, status, sent_at, opened_at, replied_at
FROM lead_nurturing_events
WHERE status = 'sent' 
  AND sent_at >= CURRENT_DATE - INTERVAL '7 days'
  AND opened_at IS NULL;
```

## 🔗 Integración con Otros Sistemas

### Outreach Multicanal

Este módulo complementa `outreach_multichannel`:
- **Outreach**: Campañas activas a leads calientes/manuales
- **Nurturing**: Automatización para leads fríos, conversión pasiva

Los leads calificados por nurturing pueden luego recibir outreach directo.

### HubSpot/Salesforce

Sincronizar leads calificados:
- Cuando `qualified_at IS NOT NULL`, exportar a CRM
- Actualizar lifecycle stage en CRM
- Trigger workflows de sales en CRM

## 📝 Próximas Mejoras

- [ ] Secuencias condicionales basadas en UTM source/campaign
- [ ] A/B testing de templates de secuencia
- [ ] Integración directa con CRM (HubSpot/Salesforce API)
- [ ] Machine Learning para optimizar timing de emails
- [ ] Soporte nativo para múltiples canales (SMS, LinkedIn, WhatsApp)
- [ ] Dashboard de métricas en tiempo real
- [ ] Recomendaciones automáticas de templates basadas en performance

## 🔌 Webhook API

### DAG: `lead_nurturing_webhook_handler`

Permite actualizar engagement desde sistemas externos vía webhook/API.

**Trigger manual con parámetros:**

```json
{
  "email": "lead@example.com",
  "event_type": "opened",
  "timestamp": "2025-01-15T10:30:00Z",
  "sequence_id": 123,
  "metadata": "{\"campaign_id\": \"abc123\", \"user_agent\": \"...\"}"
}
```

**Event Types soportados:**
- `opened`: Email abierto
- `clicked`: Link clickeado
- `replied`: Respuesta recibida
- `bounced`: Email rebotado
- `delivered`: Email entregado

**Ejemplo de integración:**

```python
# Desde sistema externo
import requests

webhook_url = "https://airflow.example.com/api/v1/dags/lead_nurturing_webhook_handler/dagRuns"
payload = {
    "conf": {
        "email": "lead@example.com",
        "event_type": "opened",
        "timestamp": "2025-01-15T10:30:00Z"
    }
}
requests.post(webhook_url, json=payload, auth=("user", "password"))
```

## 📤 Exportación de Datos

El sistema puede exportar métricas a S3 para análisis externo:

**Habilitar:**
- `export_metrics_to_s3`: true
- `s3_bucket`: nombre del bucket
- `s3_path`: ruta dentro del bucket (default: `lead_nurturing/metrics`)

**Formato exportado:**
```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "run_id": "manual__2025-01-15T10:30:00",
  "performance_report": { ... },
  "export_version": "1.0"
}
```

## 📊 Reportes Automáticos

### Reportes Semanales (`lead_nurturing_reports`)

**Schedule**: Lunes 09:00 UTC

Genera:
- CSV con métricas diarias de la semana
- HTML ejecutivo con comparativas semana anterior
- Exportación opcional a S3
- Resumen en Slack

### Reportes Mensuales (`lead_nurturing_reports_monthly`)

**Schedule**: Día 1 de cada mes, 09:00 UTC

Genera:
- CSV con métricas mensuales y comparativas
- Análisis de top templates y pasos por performance
- Tendencias mes sobre mes
- Resumen ejecutivo en Slack

**Ejemplo de métricas incluidas:**
- Leads calificados totales
- Tasa de conversión
- Reply rate promedio
- Tiempo promedio a calificar
- Top 5 templates por conversion rate
- Top 5 pasos por reply rate

## 📚 Referencias

- Schema: `/data/db/lead_nurturing_schema.sql`
- DAG Principal: `/data/airflow/dags/lead_nurturing.py`
- DAG Webhook: `/data/airflow/dags/lead_nurturing_webhook.py`
- DAG Reportes Semanales: `/data/airflow/dags/lead_nurturing_reports.py`
- DAG Reportes Mensuales: `/data/airflow/dags/lead_nurturing_reports_monthly.py`
- Tabla leads: `/data/db/schema.sql`
- DAG relacionado: `outreach_multichannel.py`

