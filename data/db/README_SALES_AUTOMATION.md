# 🎯 Sistema de Automatización de Calificación de Leads y Seguimiento de Ventas

Sistema completo automatizado para calificar leads, asignar scores y gestionar el seguimiento de ventas con tareas y campañas automáticas.

## 📋 Componentes del Sistema

### 1. **Lead Scoring Automation** (`lead_scoring_automation.py`)
DAG que calcula y actualiza scores de leads automáticamente basándose en múltiples factores.

### 2. **Sales Follow-up Automation** (`sales_followup_automation.py`)
DAG que gestiona el seguimiento de leads calificados: asignación, tareas y campañas.

### 3. **Schema de Base de Datos** (`sales_tracking_schema.sql`)
Tablas y funciones para gestionar el pipeline de ventas y seguimiento.

---

## 🗄️ Schema de Base de Datos

### Tablas Principales

#### `lead_score_history`
Historial completo de cambios de score de cada lead. Permite análisis de tendencias.

**Campos clave:**
- `lead_ext_id`: ID del lead
- `score`: Score calculado
- `previous_score`: Score anterior
- `score_change`: Diferencia automática
- `scoring_factors`: JSONB con factores que contribuyeron
- `calculated_at`: Timestamp del cálculo
- `calculated_by`: Origen del cálculo ('automated_scoring', 'manual', 'ml_model')

#### `sales_pipeline`
Leads calificados que están en el proceso de ventas.

**Campos clave:**
- `lead_ext_id`: ID único del lead
- `stage`: Etapa del pipeline ('qualified', 'contacted', 'meeting_scheduled', 'proposal_sent', 'negotiating', 'closed_won', 'closed_lost')
- `assigned_to`: Email del vendedor asignado
- `estimated_value`: Valor estimado del deal
- `probability_pct`: Probabilidad de cierre (0-100%)
- `next_followup_at`: Próxima fecha de seguimiento programada

#### `sales_followup_tasks`
Tareas de seguimiento (emails, llamadas, reuniones, etc.).

**Campos clave:**
- `task_type`: Tipo de tarea ('email', 'call', 'meeting', 'proposal', 'custom')
- `status`: Estado ('pending', 'in_progress', 'completed', 'skipped', 'cancelled')
- `priority`: Prioridad ('low', 'medium', 'high', 'urgent')
- `due_date`: Fecha de vencimiento
- `assigned_to`: Vendedor responsable

#### `sales_campaigns`
Plantillas de campañas automatizadas de ventas.

**Campos clave:**
- `campaign_type`: Tipo ('email_sequence', 'call_campaign', 'multichannel', 'nurturing')
- `trigger_criteria`: JSONB con criterios para activar (ej: `{"stage": "qualified", "score_min": 50}`)
- `steps_config`: JSONB con array de pasos de la campaña

#### `sales_campaign_executions`
Ejecuciones activas de campañas para leads específicos.

#### `sales_campaign_events`
Eventos individuales dentro de ejecuciones (emails enviados, llamadas, etc.).

### Funciones SQL

#### `calculate_lead_score()`
Calcula score de lead basado en múltiples factores:
- Información de contacto (email, teléfono, nombre)
- Engagement (replies, clicks, opens)
- Fuente y atribución (UTM, source)
- Antigüedad del lead

**Parámetros:**
- `p_lead_ext_id`: ID del lead
- `p_engagement_replies`: Número de respuestas
- `p_engagement_clicks`: Número de clicks
- `p_engagement_opens`: Número de aperturas
- `p_has_email`: Tiene email válido
- `p_has_phone`: Tiene teléfono
- `p_has_name`: Tiene nombre
- `p_source_score`: Score de la fuente (0-5)
- `p_utm_score`: Score de UTM (0-2)
- `p_days_since_created`: Días desde creación

**Retorna:** Score (0-100)

#### `auto_assign_sales_rep()`
Asigna automáticamente leads a vendedores usando round-robin basado en carga.

**Parámetros:**
- `p_lead_ext_id`: ID del lead

**Retorna:** Email del vendedor asignado

---

## ⚙️ DAGs de Automatización

### Lead Scoring Automation

**Schedule:** Cada 6 horas (`0 */6 * * *`)

**Funcionalidades:**
1. Obtiene leads que necesitan scoring/recálculo
2. Calcula scores usando función SQL + ML opcional
3. Actualiza scores en tabla `leads`
4. Guarda historial en `lead_score_history`
5. Auto-califica leads para ventas (si score >= 50)
6. Analiza tendencias de scoring
7. Notifica resumen a Slack

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `postgres_conn_id` | string | `postgres_default` | Connection ID de Postgres |
| `max_leads_per_run` | integer | `500` | Máx leads a procesar |
| `min_score_to_qualify` | integer | `50` | Score mínimo para calificar |
| `enable_ml_scoring` | boolean | `false` | Usar modelo ML predictivo |
| `ml_model_endpoint` | string | `""` | Endpoint del modelo ML |
| `include_engagement_data` | boolean | `true` | Incluir datos de nurturing |
| `update_priority_auto` | boolean | `true` | Actualizar prioridad automáticamente |
| `auto_qualify_for_sales` | boolean | `true` | Auto-calificar para ventas |
| `slack_webhook_url` | string | `""` | Webhook de Slack |

**Instalación:**
```sql
-- Ejecutar en Postgres
\i data/db/sales_tracking_schema.sql
```

### Sales Follow-up Automation

**Schedule:** Cada 2 horas (`0 */2 * * *`)

**Funcionalidades:**
1. Auto-asigna leads calificados sin asignar a vendedores
2. Identifica leads que necesitan seguimiento
3. Crea tareas automáticas basadas en etapa del pipeline
4. Ejecuta campañas automáticas según criterios
5. Procesa acciones programadas de campañas
6. Actualiza etapas del pipeline basado en actividad
7. Notifica resumen a Slack

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `postgres_conn_id` | string | `postgres_default` | Connection ID de Postgres |
| `email_webhook_url` | string | `""` | Webhook para envío de emails (requerido) |
| `call_api_url` | string | `""` | API para realizar llamadas (opcional) |
| `task_manager_api_url` | string | `""` | API para crear tareas externas (opcional) |
| `auto_assign_enabled` | boolean | `true` | Auto-asignar leads |
| `max_leads_per_run` | integer | `100` | Máx leads a procesar |
| `enable_auto_tasks` | boolean | `true` | Crear tareas automáticas |
| `enable_campaigns` | boolean | `true` | Ejecutar campañas |
| `default_followup_days` | integer | `3` | Días por defecto para seguimiento |
| `slack_webhook_url` | string | `""` | Webhook de Slack |
| `dry_run` | boolean | `false` | Solo simular sin ejecutar |
| `request_timeout` | integer | `30` | Timeout para requests (segundos) |

**Flujo:**
```
1. Auto-asignar leads sin asignar
   ↓
2. Identificar leads que necesitan seguimiento
   ↓
3. Crear tareas automáticas por etapa
   ↓
4. Ejecutar campañas activas
   ↓
5. Procesar acciones programadas
   ↓
6. Actualizar etapas del pipeline
   ↓
7. Notificar resumen
```

---

## 📊 Cálculo de Scores

### Factores de Scoring

| Factor | Puntos | Descripción |
|--------|--------|-------------|
| **Base** | 20 | Score base para todos los leads |
| **Email válido** | +10 | Lead tiene email válido |
| **Teléfono** | +5 | Lead tiene teléfono |
| **Nombre** | +5 | Lead tiene nombre completo |
| **Reply (1)** | +15 | Lead respondió 1 email |
| **Reply (2+)** | +25 | Lead respondió 2+ emails |
| **Click (1)** | +8 | Lead hizo click en 1 email |
| **Click (2+)** | +12 | Lead hizo click en 2+ emails |
| **Open (2)** | +5 | Lead abrió 2 emails |
| **Open (3)** | +10 | Lead abrió 3 emails |
| **Open (4+)** | +15 | Lead abrió 4+ emails |
| **Source Quality** | +1-5 | Basado en calidad de fuente |
| **UTM** | +2 | Lead tiene UTM parameters |
| **Recency (<7 días)** | +10 | Lead creado hace <7 días |
| **Recency (7-30 días)** | +5 | Lead creado hace 7-30 días |
| **Company Domain (.edu/.gov)** | +5 | Dominio educativo/gobierno |
| **Company Domain (corto)** | +3 | Dominio de empresa establecida |
| **Website Visited** | +3 | Visitó el sitio web |
| **Demo Requested** | +10 | Solicitó demo (alta intención) |
| **Pricing Page Viewed** | +5 | Visitó página de precios |

**Score máximo:** 100 puntos

### Factores Avanzados (Nuevos)

El sistema ahora incluye factores adicionales para scoring más preciso:
- **Señales de alta intención:** Demo solicitado, página de precios vista
- **Calidad de empresa:** Dominio educativo/gobierno, empresas establecidas
- **Engagement web:** Visitas al sitio web

Estos factores ayudan a identificar leads con mayor probabilidad de conversión.

### Prioridad Basada en Score

- **High (Alta):** Score >= 50
- **Medium (Media):** Score 35-49
- **Low (Baja):** Score < 35

---

## 🎪 Campañas Automatizadas

### Crear Campaña

```sql
INSERT INTO sales_campaigns 
(name, description, campaign_type, trigger_criteria, steps_config, enabled)
VALUES (
    'email_sequence_qualified',
    'Secuencia de emails para leads calificados',
    'email_sequence',
    '{"stage": "qualified", "score_min": 50}'::jsonb,
    '[
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
    ]'::jsonb,
    true
);
```

### Tipos de Campañas

1. **email_sequence**: Secuencia de emails automatizados
2. **call_campaign**: Campaña de llamadas
3. **multichannel**: Combinación de canales
4. **nurturing**: Nutrición continua

### Trigger Criteria

```json
{
    "stage": "qualified",        // Etapa requerida
    "score_min": 50,              // Score mínimo
    "priority": "high",           // Prioridad requerida
    "source": "organic"           // Fuente específica
}
```

---

## 📋 Tareas Automáticas por Etapa

El sistema crea automáticamente tareas según la etapa del pipeline:

| Etapa | Tarea | Tipo | Prioridad | Delay |
|-------|-------|------|-----------|-------|
| `qualified` | Primer contacto - Introducción | email | high | 0 horas |
| `contacted` | Llamada de seguimiento | call | medium | 24 horas |
| `meeting_scheduled` | Preparación para reunión | email | high | -24 horas (antes) |
| `proposal_sent` | Seguimiento de propuesta | call | high | 48 horas |
| `negotiating` | Seguimiento de negociación | email | urgent | 24 horas |

---

## 🔄 Flujo Completo del Sistema

```
1. Lead Scoring Automation (cada 6h)
   ├─ Identifica leads para scoring
   ├─ Calcula scores automáticamente
   ├─ Actualiza prioridades
   └─ Auto-califica leads (score >= 50) → sales_pipeline
   
2. Sales Follow-up Automation (cada 2h)
   ├─ Auto-asigna leads a vendedores
   ├─ Crea tareas de seguimiento
   ├─ Ejecuta campañas automáticas
   ├─ Procesa acciones programadas
   └─ Actualiza etapas del pipeline
   
3. Eventos de Engagement
   └─ Actualizan scores automáticamente
```

---

## 📈 Consultas Útiles

### Ver Leads Calificados Recientes

```sql
SELECT 
    p.lead_ext_id,
    p.email,
    p.first_name,
    p.score,
    p.priority,
    p.stage,
    p.assigned_to,
    p.qualified_at,
    p.next_followup_at
FROM sales_pipeline p
WHERE p.qualified_at >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY p.priority DESC, p.score DESC;
```

### Ver Tareas Pendientes

```sql
SELECT 
    t.task_title,
    t.task_type,
    t.priority,
    t.due_date,
    p.email,
    p.stage,
    t.assigned_to
FROM sales_followup_tasks t
JOIN sales_pipeline p ON t.pipeline_id = p.id
WHERE t.status = 'pending'
ORDER BY t.priority DESC, t.due_date ASC;
```

### Ver Historial de Scores

```sql
SELECT 
    h.lead_ext_id,
    l.email,
    h.previous_score,
    h.score,
    h.score_change,
    h.priority,
    h.calculated_at,
    h.scoring_factors
FROM lead_score_history h
JOIN leads l ON h.lead_ext_id = l.ext_id
WHERE h.lead_ext_id = 'lead_123'
ORDER BY h.calculated_at DESC;
```

### Métricas de Pipeline

```sql
SELECT 
    stage,
    COUNT(*) AS count,
    AVG(score) AS avg_score,
    SUM(estimated_value) AS total_value,
    AVG(probability_pct) AS avg_probability
FROM sales_pipeline
WHERE stage NOT IN ('closed_won', 'closed_lost')
GROUP BY stage
ORDER BY 
    CASE stage
        WHEN 'qualified' THEN 1
        WHEN 'contacted' THEN 2
        WHEN 'meeting_scheduled' THEN 3
        WHEN 'proposal_sent' THEN 4
        WHEN 'negotiating' THEN 5
    END;
```

### Refrescar Vista de Métricas

```sql
REFRESH MATERIALIZED VIEW mv_sales_metrics;

SELECT * FROM mv_sales_metrics
ORDER BY date DESC
LIMIT 30;
```

---

## 🔧 Configuración

### 1. Configurar Equipo de Ventas

Editar función `auto_assign_sales_rep()` en `sales_tracking_schema.sql`:

```sql
CREATE OR REPLACE FUNCTION auto_assign_sales_rep(...)
...
v_sales_team TEXT[] := ARRAY[
    'sales1@tu-dominio.com',
    'sales2@tu-dominio.com',
    'sales3@tu-dominio.com'
];
```

### 2. Configurar Webhook de Email

En Airflow Variables o DAG params:
- `email_webhook_url`: URL del webhook que envía emails

Formato esperado:
```json
POST {email_webhook_url}
{
  "from": "sales@tu-dominio.com",
  "to": "lead@example.com",
  "subject": "Asunto",
  "text": "Cuerpo del email",
  "metadata": {
    "lead_ext_id": "lead_123",
    "campaign_step": 1
  }
}
```

### 3. Configurar API de Llamadas (Opcional)

En DAG params:
- `call_api_url`: URL de API para realizar llamadas

---

## 🚨 Troubleshooting

### Leads no se califican automáticamente

1. Verificar que `auto_qualify_for_sales = true` en DAG params
2. Verificar que `min_score_to_qualify <= score del lead`
3. Revisar logs del task `update_scores_and_history`

```sql
-- Ver leads que deberían calificarse
SELECT ext_id, email, score, priority
FROM leads
WHERE score >= 50
AND ext_id NOT IN (SELECT lead_ext_id FROM sales_pipeline);
```

### Tareas no se crean automáticamente

1. Verificar que `enable_auto_tasks = true`
2. Verificar que lead tiene `assigned_to` no nulo
3. Revisar logs del task `create_followup_tasks`

```sql
-- Ver leads que necesitan tareas
SELECT p.*, COUNT(t.id) FILTER (WHERE t.status = 'pending') AS pending_tasks
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND p.assigned_to IS NOT NULL
GROUP BY p.id
HAVING COUNT(t.id) FILTER (WHERE t.status = 'pending') = 0;
```

### Campañas no se ejecutan

1. Verificar que `enable_campaigns = true`
2. Verificar que campaña tiene `enabled = true`
3. Verificar que lead cumple `trigger_criteria`
4. Revisar logs del task `execute_campaigns`

```sql
-- Ver campañas activas
SELECT id, name, campaign_type, trigger_criteria, enabled
FROM sales_campaigns
WHERE enabled = true;

-- Ver ejecuciones de campañas
SELECT 
    ce.*,
    c.name AS campaign_name,
    p.email
FROM sales_campaign_executions ce
JOIN sales_campaigns c ON ce.campaign_id = c.id
JOIN sales_pipeline p ON ce.pipeline_id = p.id
WHERE ce.status = 'active';
```

---

## 📊 DAGs Adicionales

### Sales Analytics Reports (`sales_analytics_reports.py`)

**Schedule:** Lunes 09:00 UTC (semanal)

**Funcionalidades:**
- Genera reportes automáticos semanales/mensuales
- Métricas de conversión por etapa
- Performance de vendedores
- Análisis de fuentes de leads
- Tendencias de scoring
- Forecast de ventas
- Exportación a CSV/S3
- Envío a Slack/Email

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `report_type` | string | `weekly` | Tipo de reporte (weekly/monthly) |
| `export_to_s3` | boolean | `false` | Exportar a S3 |
| `s3_bucket` | string | `""` | Bucket de S3 |
| `s3_path` | string | `sales_reports` | Ruta en S3 |
| `slack_webhook_url` | string | `""` | Webhook de Slack |
| `email_recipients` | string | `""` | Emails para reporte |

**Ejemplo de uso:**
```python
# Trigger manual con parámetros
{
    "report_type": "monthly",
    "export_to_s3": true,
    "s3_bucket": "my-bucket",
    "slack_webhook_url": "https://hooks.slack.com/..."
}
```

### Sales CRM Sync (`sales_crm_sync.py`)

**Schedule:** Cada 4 horas (`0 */4 * * *`)

**Funcionalidades:**
- Sincroniza leads calificados con CRM (HubSpot/Salesforce)
- Exporta nuevos leads automáticamente
- Actualiza etapas y campos en CRM
- Crea deals/opportunities automáticamente
- Sincronización bidireccional (futuro)

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `crm_type` | string | `hubspot` | Tipo de CRM (hubspot/salesforce) |
| `crm_api_key` | string | `""` | API key del CRM |
| `crm_api_url` | string | `""` | URL base de la API |
| `sync_direction` | string | `export` | Dirección (export/import/bidirectional) |
| `max_leads_per_run` | integer | `100` | Máx leads a sincronizar |
| `dry_run` | boolean | `false` | Solo simular |

**Configuración HubSpot:**
1. Obtener API key desde HubSpot Settings > Integrations > Private Apps
2. Configurar en DAG params:
   - `crm_api_url`: `https://api.hubapi.com`
   - `crm_api_key`: Tu API key

**Configuración Salesforce:**
1. Configurar OAuth2 o API credentials
2. Configurar en DAG params:
   - `crm_api_url`: `https://your-instance.salesforce.com`
   - `crm_api_key`: Tu access token

---

## 🤖 DAGs de Machine Learning e Inteligencia

### Sales ML Predictions (`sales_ml_predictions.py`)

**Schedule:** Cada 6 horas (`0 */6 * * *`)

**Funcionalidades:**
- Predice probabilidad de cierre usando ML
- Estima valor esperado del deal
- Predice tiempo hasta cierre
- Identifica leads de alto riesgo
- Recomienda acciones óptimas
- Actualiza probability_pct automáticamente

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `ml_model_endpoint` | string | `""` | Endpoint del modelo ML |
| `ml_model_type` | string | `probability` | Tipo: probability/value/time_to_close/all |
| `enable_ml_predictions` | boolean | `true` | Habilitar predicciones ML |
| `update_probability_auto` | boolean | `true` | Actualizar probability_pct automáticamente |
| `min_probability_threshold` | integer | `20` | Probabilidad mínima para actualizar |
| `max_leads_per_run` | integer | `200` | Máx leads a procesar |

**Formato del Modelo ML:**

El endpoint debe aceptar:
```json
{
  "features": {
    "lead_score": 75,
    "priority": "high",
    "stage": "negotiating",
    "days_in_pipeline": 15,
    "days_since_contact": 2,
    "completed_tasks": 5,
    "pending_tasks": 2,
    "email_events": 10,
    "call_events": 3,
    "estimated_value": 50000,
    "current_probability": 60,
    "source": "organic"
  },
  "model_type": "probability"
}
```

Y retornar:
```json
{
  "probability": 72,
  "expected_value": 36000,
  "time_to_close_days": 12,
  "risk_score": 0.3,
  "recommendations": ["send_proposal", "schedule_call"],
  "confidence": 0.85
}
```

### Sales Timing Optimizer (`sales_timing_optimizer.py`)

**Schedule:** Lunes 00:00 (semanal)

**Funcionalidades:**
- Analiza patrones de éxito por timing
- Identifica mejores días/horas para contactar
- Optimiza intervalos entre seguimientos
- Ajusta automáticamente next_followup_at
- Actualiza delays en campañas

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `analysis_days` | integer | `90` | Días de datos para análisis |
| `enable_auto_optimization` | boolean | `true` | Habilitar optimización automática |
| `min_data_points` | integer | `10` | Mínimo de puntos de datos |

**Análisis que realiza:**
1. **Por día de la semana:** Identifica días con mayor win rate
2. **Por hora del día:** Identifica horas óptimas para contactar
3. **Por intervalo:** Optimiza días entre seguimientos

**Resultado:**
- Actualiza `next_followup_at` basado en patrones óptimos
- Ajusta delays en campañas automáticamente
- Guarda optimizaciones en metadata

---

## 🛠️ Scripts de Utilidad

### Gestionar Campañas (`scripts/manage_sales_campaigns.py`)

Script CLI para gestionar campañas desde la línea de comandos.

**Instalación:**
```bash
chmod +x scripts/manage_sales_campaigns.py
```

**Uso:**

```bash
# Listar campañas
python scripts/manage_sales_campaigns.py --db "postgresql://user:pass@host/db" list

# Crear campaña
python scripts/manage_sales_campaigns.py --db "..." create \
  --name "Email Sequence Qualified" \
  --type "email_sequence" \
  --trigger-file trigger.json \
  --steps-file steps.json

# Mostrar campaña
python scripts/manage_sales_campaigns.py --db "..." show --id 1

# Activar/Desactivar
python scripts/manage_sales_campaigns.py --db "..." toggle --id 1 --enabled
python scripts/manage_sales_campaigns.py --db "..." toggle --id 1 --disabled

# Eliminar
python scripts/manage_sales_campaigns.py --db "..." delete --id 1
```

**Ejemplo de trigger.json:**
```json
{
  "stage": "qualified",
  "score_min": 50,
  "priority": "high"
}
```

**Ejemplo de steps.json:**
```json
[
  {
    "step": 1,
    "type": "email",
    "delay_hours": 0,
    "subject_template": "Hola {{first_name}}, conoce nuestro producto",
    "body_template": "Cuerpo del email..."
  },
  {
    "step": 2,
    "type": "email",
    "delay_hours": 48,
    "subject_template": "{{first_name}}, seguimiento",
    "body_template": "..."
  }
]
```

---

## 🧠 DAGs Avanzados de Inteligencia

### Sales Intelligent Routing (`sales_intelligent_routing.py`)

**Schedule:** Cada 3 horas (`0 */3 * * *`)

**Funcionalidades:**
- Asignación inteligente basada en múltiples factores
- Balanceo automático de carga entre vendedores
- Re-asignación de leads abandonados
- Considera performance histórica de cada vendedor
- Especialización por industria/producto (futuro)

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `max_reassignments_per_run` | integer | `20` | Máx re-asignaciones por ejecución |
| `enable_load_balancing` | boolean | `true` | Balancear carga entre vendedores |
| `enable_specialization` | boolean | `true` | Considerar especialización |
| `min_active_leads_per_rep` | integer | `5` | Mínimo de leads activos por rep |
| `max_active_leads_per_rep` | integer | `50` | Máximo de leads activos por rep |
| `reassign_stale_days` | integer | `7` | Días sin contacto para re-asignar |

**Algoritmo de Asignación:**
1. Calcula carga de trabajo de cada vendedor
2. Evalúa performance (win rate)
3. Considera especialización (futuro)
4. Penaliza tareas vencidas
5. Asigna al vendedor con mejor score

### Sales Intelligent Alerts (`sales_alerts_intelligent.py`)

**Schedule:** Cada 2 horas (`0 */2 * * *`)

**Funcionalidades:**
- Detecta leads de alto valor sin seguimiento
- Identifica tareas vencidas críticas
- Alerta sobre leads estancados
- Detecta caídas en tasa de conversión
- Identifica vendedores sobrecargados
- Notificaciones a Slack/Email

**Parámetros:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `enable_high_value_alerts` | boolean | `true` | Alertar leads alto valor |
| `high_value_threshold` | number | `10000` | Valor mínimo para alerta |
| `enable_stale_lead_alerts` | boolean | `true` | Alertar leads estancados |
| `stale_lead_days` | integer | `7` | Días sin actividad |
| `enable_overdue_task_alerts` | boolean | `true` | Alertar tareas vencidas |
| `enable_conversion_drop_alerts` | boolean | `true` | Alertar caídas de conversión |
| `conversion_drop_threshold` | number | `10` | % de caída para alertar |

**Tipos de Alertas:**
- 🚨 **Críticas:** Leads alto valor sin seguimiento, tareas urgentes vencidas
- ⚠️ **Advertencias:** Leads estancados, caídas de conversión
- 📊 **Informativas:** Vendedores sobrecargados, tendencias

---

## 📊 Queries y Vistas Optimizadas

### Queries SQL (`sales_queries_optimized.sql`)

Incluye vistas, funciones y queries optimizadas para análisis:

**Vistas:**
- `v_sales_dashboard` - Vista completa para dashboards
- `v_leads_requires_attention` - Leads que requieren atención
- `v_sales_rep_performance` - Performance de vendedores
- `v_sales_forecast` - Forecast mensual
- `v_conversion_funnel` - Embudo de conversión

**Funciones:**
- `get_top_opportunities(limit, min_value)` - Top oportunidades
- `get_leads_at_risk(min_days, min_risk)` - Leads en riesgo
- `update_rep_stats(rep_email)` - Actualizar stats de vendedor

**Optimizaciones:**
- Índices compuestos para búsquedas frecuentes
- Índices GIN para metadata JSONB
- Triggers automáticos para consistencia

Ver documentación completa: `/data/db/README_SALES_QUERIES.md`

---

## 📚 Referencias

- **Schema:** `/data/db/sales_tracking_schema.sql`
- **Queries Optimizadas:** `/data/db/sales_queries_optimized.sql`
- **Documentación de Queries:** `/data/db/README_SALES_QUERIES.md`
- **Quick Start:** `/data/db/QUICK_START_SALES.md`
- **Migración:** `/data/db/MIGRATION_GUIDE.md`
- **Mejores Prácticas:** `/data/db/BEST_PRACTICES.md`
- **Índice Completo:** `/data/db/INDEX_SALES_SYSTEM.md`
- **Resumen Ejecutivo:** `/data/db/EXECUTIVE_SUMMARY.md`
- **Configuración Producción:** `/data/db/examples/production_config.yaml`
- **Ejemplos de Campañas:** `/data/db/examples/campaign_examples.json`
- **Changelog:** `/data/db/CHANGELOG.md`
- **Ejemplos de Integración:** `/data/db/INTEGRATION_EXAMPLES.md`
- **Queries para Dashboards:** `/data/db/examples/dashboard_queries.sql`
- **Tests:** `/tests/test_sales_system.py`
- **Validación:** `/scripts/validate_sales_system.py`
- **Monitoreo:** `/scripts/monitor_sales_system.sh`
- **Health Check:** `/scripts/sales_health_check.py`
- **Lead Scoring DAG:** `/data/airflow/dags/lead_scoring_automation.py`
- **Sales Follow-up DAG:** `/data/airflow/dags/sales_followup_automation.py`
- **Sales Analytics DAG:** `/data/airflow/dags/sales_analytics_reports.py`
- **CRM Sync DAG:** `/data/airflow/dags/sales_crm_sync.py`
- **Intelligent Routing DAG:** `/data/airflow/dags/sales_intelligent_routing.py`
- **Intelligent Alerts DAG:** `/data/airflow/dags/sales_alerts_intelligent.py`
- **ML Predictions DAG:** `/data/airflow/dags/sales_ml_predictions.py`
- **Timing Optimizer DAG:** `/data/airflow/dags/sales_timing_optimizer.py`
- **Campaign Manager:** `/scripts/manage_sales_campaigns.py`
- **Insights CLI:** `/scripts/sales_insights_cli.py`
- **Lead Nurturing:** `/data/airflow/dags/lead_nurturing.py` (sistema complementario)
- **Tabla leads:** `/data/db/schema.sql`

---

## 🎯 Próximas Mejoras

- [x] Integración con CRM (HubSpot/Salesforce) ✅
- [x] Reportes automáticos de analytics ✅
- [x] Routing inteligente de leads ✅
- [x] Sistema de alertas inteligentes ✅
- [x] Scoring avanzado con más factores ✅
- [x] Machine Learning para predecir probabilidad de cierre ✅
- [x] Optimización automática de timing de seguimiento ✅
- [x] Script CLI para insights ✅
- [ ] Dashboard de métricas en tiempo real
- [ ] Integración con calendario para scheduling automático
- [ ] Soporte para WhatsApp y SMS
- [ ] A/B testing de campañas
- [ ] Recomendaciones automáticas de próximos pasos
- [ ] Sincronización bidireccional completa con CRM
- [ ] Especialización de vendedores por industria/producto

