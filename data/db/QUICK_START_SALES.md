# 🚀 Quick Start - Sistema de Automatización de Ventas

Guía rápida para poner en marcha el sistema completo de automatización de calificación de leads y seguimiento de ventas.

## 📋 Paso 1: Instalar Schema

```bash
# Conectar a PostgreSQL
psql -U postgres -d tu_database

# Ejecutar schema
\i data/db/sales_tracking_schema.sql
```

## 📋 Paso 2: Configurar Vendedores

Editar función `auto_assign_sales_rep()` en el schema:

```sql
CREATE OR REPLACE FUNCTION auto_assign_sales_rep(...)
...
v_sales_team TEXT[] := ARRAY[
    'vendedor1@tu-empresa.com',
    'vendedor2@tu-empresa.com',
    'vendedor3@tu-empresa.com'
];
```

## 📋 Paso 3: Configurar DAGs en Airflow

### Lead Scoring Automation

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `max_leads_per_run`: `500`
- `min_score_to_qualify`: `50`
- `auto_qualify_for_sales`: `true`

### Sales Follow-up Automation

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `email_webhook_url`: URL de tu webhook de email
- `auto_assign_enabled`: `true`
- `enable_auto_tasks`: `true`
- `enable_campaigns`: `true`

### Sales Intelligent Routing

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `max_active_leads_per_rep`: `50`
- `enable_load_balancing`: `true`

### Sales Intelligent Alerts

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `slack_webhook_url`: (opcional) URL de Slack
- `enable_high_value_alerts`: `true`
- `enable_stale_lead_alerts`: `true`

### Sales Analytics Reports

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `slack_webhook_url`: (opcional) URL de Slack

### Sales CRM Sync (Opcional)

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `crm_type`: `hubspot` o `salesforce`
- `crm_api_key`: Tu API key
- `crm_api_url`: URL de la API

### Sales ML Predictions (Opcional)

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `ml_model_endpoint`: URL de tu modelo ML
- `enable_ml_predictions`: `true`

### Sales Timing Optimizer (Opcional)

**Parámetros mínimos:**
- `postgres_conn_id`: `postgres_default`
- `enable_auto_optimization`: `true`

## 📋 Paso 4: Crear Primera Campaña

```bash
# Crear archivo trigger.json
cat > trigger.json << EOF
{
  "stage": "qualified",
  "score_min": 50,
  "priority": "high"
}
EOF

# Crear archivo steps.json
cat > steps.json << EOF
[
  {
    "step": 1,
    "type": "email",
    "delay_hours": 0,
    "subject_template": "Hola {{first_name}}, conoce nuestro producto",
    "body_template": "Cuerpo del email personalizado..."
  },
  {
    "step": 2,
    "type": "email",
    "delay_hours": 48,
    "subject_template": "{{first_name}}, seguimiento",
    "body_template": "..."
  }
]
EOF

# Crear campaña
python scripts/manage_sales_campaigns.py \
  --db "postgresql://user:pass@host/db" \
  create \
  --name "Email Sequence Qualified" \
  --type "email_sequence" \
  --trigger-file trigger.json \
  --steps-file steps.json \
  --enabled
```

## 📋 Paso 5: Verificar Funcionamiento

### Ver Leads Calificados

```sql
SELECT 
    lead_ext_id,
    email,
    score,
    priority,
    stage,
    assigned_to,
    qualified_at
FROM sales_pipeline
WHERE qualified_at >= NOW() - INTERVAL '7 days'
ORDER BY priority DESC, score DESC;
```

### Ver Tareas Pendientes

```sql
SELECT 
    t.task_title,
    t.task_type,
    t.priority,
    t.due_date,
    p.email,
    t.assigned_to
FROM sales_followup_tasks t
JOIN sales_pipeline p ON t.pipeline_id = p.id
WHERE t.status = 'pending'
ORDER BY t.priority DESC, t.due_date ASC;
```

### Usar CLI de Insights

```bash
# Ver resumen completo
python scripts/sales_insights_cli.py \
  --db "postgresql://user:pass@host/db" \
  --all
```

## 🔧 Configuración de Webhooks

### Email Webhook

Tu webhook debe aceptar:
```json
POST /webhook/email
{
  "from": "sales@tu-empresa.com",
  "to": "lead@example.com",
  "subject": "Asunto",
  "text": "Cuerpo del email",
  "metadata": {
    "lead_ext_id": "lead_123",
    "campaign_step": 1
  }
}
```

### Slack Webhook

1. Crear webhook en Slack: https://api.slack.com/messaging/webhooks
2. Configurar URL en parámetros de DAGs

## 📊 Monitoreo

### Ver Métricas

```sql
REFRESH MATERIALIZED VIEW mv_sales_metrics;

SELECT * FROM mv_sales_metrics
ORDER BY date DESC
LIMIT 30;
```

### Ver Historial de Scores

```sql
SELECT 
    lead_ext_id,
    previous_score,
    score,
    score_change,
    calculated_at
FROM lead_score_history
WHERE calculated_at >= NOW() - INTERVAL '7 days'
ORDER BY calculated_at DESC
LIMIT 20;
```

## 🎯 Flujo Completo

```
1. Lead Scoring (cada 6h)
   → Calcula scores
   → Auto-califica leads (score >= 50)
   → Actualiza prioridades

2. Intelligent Routing (cada 3h)
   → Asigna leads a vendedores
   → Re-asigna leads abandonados
   → Balancea carga

3. Follow-up Automation (cada 2h)
   → Crea tareas automáticas
   → Ejecuta campañas
   → Procesa acciones programadas

4. Intelligent Alerts (cada 2h)
   → Detecta situaciones críticas
   → Notifica a Slack

5. ML Predictions (cada 6h, opcional)
   → Predice probabilidad de cierre
   → Actualiza probability_pct

6. Timing Optimizer (semanal, opcional)
   → Optimiza timing de seguimiento
   → Ajusta delays en campañas

7. Analytics Reports (semanal)
   → Genera reportes
   → Envía a Slack
```

## 🚨 Troubleshooting Rápido

### Leads no se califican

```sql
-- Verificar leads que deberían calificarse
SELECT ext_id, email, score, priority
FROM leads
WHERE score >= 50
AND ext_id NOT IN (SELECT lead_ext_id FROM sales_pipeline);
```

### Tareas no se crean

```sql
-- Verificar leads que necesitan tareas
SELECT p.*, COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND p.assigned_to IS NOT NULL
GROUP BY p.id
HAVING COUNT(t.id) FILTER (WHERE t.status = 'pending') = 0;
```

### Campañas no se ejecutan

```sql
-- Verificar campañas activas
SELECT id, name, enabled, trigger_criteria
FROM sales_campaigns
WHERE enabled = true;
```

## 📚 Documentación Completa

Ver `/data/db/README_SALES_AUTOMATION.md` para documentación completa.

## ✅ Checklist de Inicio

- [ ] Schema ejecutado en PostgreSQL
- [ ] Vendedores configurados en función SQL
- [ ] DAGs configurados en Airflow
- [ ] Webhook de email configurado
- [ ] Slack webhook configurado (opcional)
- [ ] Primera campaña creada
- [ ] Verificación de funcionamiento
- [ ] Monitoreo configurado

¡Listo para empezar! 🎉



