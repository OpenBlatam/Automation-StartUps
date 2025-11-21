# 🚀 Automatización de Adquisición Orgánica con Nurturing y Referidos

## 📋 Descripción General

Sistema completo automatizado para adquisición orgánica que incluye:
- ✅ Captura automática de leads orgánicos
- ✅ Workflow de nurturing segmentado
- ✅ Programa de referidos con incentivos
- ✅ Validación anti-fraude de referidos
- ✅ Sincronización con CRM
- ✅ Reportes automáticos
- ✅ Optimización automática

**Tecnología:** Apache Airflow (sin n8n)

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Formularios    │
│  Lead Magnets   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Capture Leads  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Segmentación  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Nurturing    │───► Contenido (Blog, Guías, Videos)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Engagement    │───► Tracking de consumo
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Invitación     │───► Programa de Referidos
│  Referidos      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validación     │───► Anti-fraude
│  Referidos      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Recompensas   │───► Generación automática
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Sync CRM       │───► Sincronización bidireccional
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Reportes      │───► Métricas y análisis
└─────────────────┘
```

---

## 📦 Componentes

### 1. DAG de Airflow
**Archivo:** `data/airflow/dags/organic_acquisition_nurturing.py`

**Frecuencia:** Cada 2 horas

**Tareas principales:**
- `capture_new_leads`: Captura nuevos leads orgánicos
- `segment_leads`: Segmenta por interés/comportamiento
- `start_nurturing_workflows`: Inicia secuencias de nurturing
- `send_nurturing_content`: Envía contenido programado
- `track_engagement`: Actualiza engagement de leads
- `invite_to_referral_program`: Invita leads enganchados
- `process_referrals`: Procesa y valida referidos
- `sync_with_crm`: Sincroniza con CRM
- `send_reminders`: Envía recordatorios
- `send_second_incentive`: Envía segundo incentivo
- `generate_reports`: Genera reportes automáticos
- `optimize_automatically`: Optimiza contenido/recompensas

### 2. Schema de Base de Datos
**Archivo:** `data/db/organic_acquisition_schema.sql`

**Tablas principales:**
- `organic_leads`: Leads orgánicos
- `nurturing_templates`: Templates de secuencias
- `nurturing_sequences`: Secuencias activas
- `content_engagement`: Engagement con contenido
- `referral_programs`: Programas de referidos
- `referrals`: Referidos registrados
- `referral_rewards`: Recompensas generadas
- `reminder_log`: Log de recordatorios
- `acquisition_metrics`: Métricas históricas

### 3. Validador de Referidos
**Archivo:** `data/integrations/referral_validator.py`

**Funcionalidades:**
- Validación de auto-referidos
- Detección de emails duplicados
- Análisis de riesgo por IP
- Detección de patrones sospechosos
- Validación de códigos de referido

---

## 🚀 Instalación y Configuración

### 1. Ejecutar Schema SQL

```bash
psql -U postgres -d tu_base_de_datos -f data/db/organic_acquisition_schema.sql
```

### 2. Configurar Variables de Airflow

```python
# En Airflow UI: Admin > Variables

# Conexión a Postgres
postgres_conn_id = "postgres_default"

# Webhook de Email
email_webhook_url = "https://tu-webhook-email.com/send"

# CRM (opcional)
crm_api_url = "https://tu-crm.com/api"
crm_api_key = "tu-api-key"

# Slack (opcional)
slack_webhook_url = "https://hooks.slack.com/services/..."
```

### 3. Configurar Parámetros del DAG

En Airflow UI, al ejecutar el DAG, puedes configurar:

```python
{
    "max_leads_per_run": 200,
    "engagement_threshold": 3,
    "referral_incentive": 10.0,
    "enable_fraud_detection": true,
    "report_frequency": "daily",
    "nurturing_enabled": true,
    "nurturing_reminder_days": 3,
    "enable_auto_optimization": true
}
```

### 4. Activar el DAG

```bash
# En Airflow UI: DAGs > organic_acquisition_nurturing > Toggle ON
```

---

## 📊 Flujo de Trabajo Detallado

### Fase 1: Captura de Leads

1. **Formularios/Webhooks** capturan nuevos leads
2. Leads se insertan en `organic_leads` con `status = 'new'`
3. DAG detecta leads nuevos cada 2 horas

### Fase 2: Segmentación

1. Leads se segmentan por:
   - **Interés**: marketing, sales, general, etc.
   - **Fuente**: organic, referral, social, etc.
   - **Engagement inicial**: high (descargó magnet), medium

### Fase 3: Nurturing

1. Se inicia secuencia de nurturing según interés
2. Contenido programado se envía automáticamente:
   - Blog posts
   - Guías descargables
   - Videos tutoriales
   - Ebooks
3. Se trackea engagement (opens, clicks, completions)

### Fase 4: Etiquetado "Enganchado"

1. Cuando lead consume ≥3 contenidos → `status = 'engaged'`
2. Se registra `engaged_at` timestamp

### Fase 5: Invitación a Referidos

1. Leads enganchados reciben invitación automática
2. Se genera código único: `REF-XXXXXXXXXXXX`
3. Se genera enlace: `https://tu-dominio.com/refer/REF-XXXXXXXXXXXX`
4. Email con incentivo inicial

### Fase 6: Validación de Referidos

1. Cuando alguien se registra con código de referido:
   - Validación anti-fraude:
     - ✅ No auto-referido
     - ✅ Email no existe previamente
     - ✅ No múltiples referidos desde misma IP
     - ✅ Patrones de email válidos
     - ✅ Código válido y pertenece al referidor
2. Si válido → `status = 'validated'`
3. Si fraude → `status = 'fraud'` + razones

### Fase 7: Generación de Recompensas

1. Referido validado → se crea `referral_rewards`
2. Notificación automática al referidor
3. Recompensa pendiente de pago

### Fase 8: Sincronización CRM

1. Leads y referidos se sincronizan con CRM
2. Campos personalizados incluyen:
   - `referral_code`
   - `referrer_lead_id`
   - `engagement_score`

### Fase 9: Recordatorios y Optimización

1. **Recordatorios**: Leads sin engagement en 3 días
2. **Segundo incentivo**: Leads sin referidos en 7 días → incentivo +20%
3. **Optimización automática**:
   - Si tasa de conversión < 5% → aumentar incentivo 15%
   - Analizar contenido más efectivo
   - Ajustar secuencias

### Fase 10: Reportes

1. **Diarios/Semanales** automáticos con:
   - Total de leads
   - Leads enganchados
   - Referidos validados
   - Recompensas generadas
   - Tasas de conversión
2. Envío a Slack (opcional)

---

## 🔍 Validación Anti-Fraude

### Reglas de Validación

1. **Auto-referido**: Referidor y referido mismo email → ❌
2. **Email duplicado**: Email ya existe como lead previo → ❌
3. **IP sospechosa**: >10 referidos desde misma IP en 1 hora → ❌
4. **Patrón de referidor**: >20 referidos del mismo referidor en 1 hora → ❌
5. **Email desechable**: Dominios temporales detectados → ⚠️
6. **Código inválido**: Código no pertenece al referidor → ❌

### Scoring de Riesgo

- **0-4**: Bajo riesgo ✅
- **5-6**: Riesgo medio ⚠️ (warnings)
- **7-9**: Alto riesgo ❌ (rechazado)
- **10**: Crítico ❌ (rechazado automático)

---

## 📈 Métricas y Reportes

### Métricas Principales

1. **Leads**:
   - Total de leads
   - Nuevos
   - En nurturing
   - Enganchados
   - Score promedio de engagement

2. **Referidos**:
   - Total de referidos
   - Validados
   - Fraude detectado
   - Referidores únicos

3. **Recompensas**:
   - Total de recompensas
   - Monto total
   - Pagadas

4. **Conversión**:
   - Tasa: Enganchados → Invitados
   - Tasa: Invitados → Referidos validados
   - Tasa: Referidos → Recompensas pagadas

### Vistas SQL Útiles

```sql
-- Leads con engagement
SELECT * FROM v_leads_with_engagement;

-- Estadísticas de referidos
SELECT * FROM v_referrals_stats;

-- Métricas de conversión
SELECT * FROM v_conversion_metrics;
```

---

## 🔧 Personalización

### Agregar Nuevos Templates de Nurturing

```sql
INSERT INTO nurturing_templates (
    template_id,
    template_name,
    interest_area,
    sequence_name,
    content_items,
    active
) VALUES (
    'template_custom',
    'Template Personalizado',
    'custom',
    'Secuencia Personalizada',
    '[
        {"type": "blog", "id": "blog_1", "title": "Título", "url": "https://..."},
        {"type": "guide", "id": "guide_1", "title": "Guía", "url": "https://..."}
    ]'::jsonb,
    true
);
```

### Modificar Thresholds de Engagement

En parámetros del DAG:
```python
"engagement_threshold": 5  # Cambiar de 3 a 5
```

### Ajustar Incentivos

```python
"referral_incentive": 15.0  # Cambiar de 10.0 a 15.0
```

---

## 🐛 Troubleshooting

### Problema: Leads no se capturan

**Solución:**
1. Verificar que formularios inserten en `organic_leads` con `status = 'new'`
2. Verificar logs del DAG: `capture_new_leads`
3. Verificar conexión a Postgres

### Problema: Emails no se envían

**Solución:**
1. Verificar `email_webhook_url` en parámetros
2. Verificar que webhook responda correctamente
3. Revisar logs de `send_nurturing_content`

### Problema: Referidos marcados como fraude incorrectamente

**Solución:**
1. Revisar `fraud_reasons` en tabla `referrals`
2. Ajustar thresholds en `ReferralValidator`
3. Revisar manualmente casos específicos

### Problema: CRM sync falla

**Solución:**
1. Verificar `crm_api_url` y `crm_api_key`
2. Verificar formato de payload
3. Revisar logs de `sync_with_crm`

---

## 📚 Ejemplos de Uso

### Capturar Lead Manualmente

```sql
INSERT INTO organic_leads (
    lead_id,
    email,
    first_name,
    last_name,
    source,
    interest_area,
    status
) VALUES (
    'lead_test_123',
    'test@example.com',
    'Juan',
    'Pérez',
    'organic',
    'marketing',
    'new'
);
```

### Ver Leads en Nurturing

```sql
SELECT 
    ol.email,
    ol.first_name,
    ns.sequence_name,
    ns.current_step,
    COUNT(ce.engagement_id) as content_sent
FROM organic_leads ol
JOIN nurturing_sequences ns ON ol.lead_id = ns.lead_id
LEFT JOIN content_engagement ce ON ns.sequence_id = ce.sequence_id
WHERE ol.status = 'nurturing'
GROUP BY ol.email, ol.first_name, ns.sequence_name, ns.current_step;
```

### Ver Referidos por Referidor

```sql
SELECT 
    ol.email as referrer_email,
    COUNT(r.referral_id) as total_referrals,
    COUNT(CASE WHEN r.status = 'validated' THEN 1 END) as validated,
    SUM(rr.reward_amount) as total_earned
FROM organic_leads ol
JOIN referral_programs rp ON ol.lead_id = rp.lead_id
LEFT JOIN referrals r ON rp.referral_code = r.referral_code
LEFT JOIN referral_rewards rr ON r.referral_id = rr.referral_id
WHERE ol.status = 'engaged'
GROUP BY ol.email;
```

---

## 🔐 Seguridad

### Buenas Prácticas

1. **API Keys**: Nunca hardcodear en código, usar variables de Airflow
2. **Validación**: Siempre validar referidos antes de otorgar recompensas
3. **Logs**: Mantener logs de todas las acciones
4. **Rate Limiting**: Implementar límites en webhooks
5. **Encriptación**: Encriptar datos sensibles en base de datos

---

## 📞 Soporte

Para problemas o preguntas:
1. Revisar logs del DAG en Airflow
2. Consultar documentación de tablas SQL
3. Revisar código de validación en `referral_validator.py`

---

## 🎯 Próximos Pasos

1. ✅ Configurar webhook de email
2. ✅ Ejecutar schema SQL
3. ✅ Configurar variables de Airflow
4. ✅ Activar DAG
5. ✅ Probar con lead de prueba
6. ✅ Monitorear métricas
7. ✅ Ajustar thresholds según resultados

---

**¡Sistema listo para automatizar tu adquisición orgánica! 🚀**

