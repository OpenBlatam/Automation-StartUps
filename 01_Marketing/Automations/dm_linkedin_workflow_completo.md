---
title: "Dm Linkedin Workflow Completo"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Automations/dm_linkedin_workflow_completo.md"
---

# 🔄 Flujo de Trabajo Completo: LinkedIn DMs

## 📋 Proceso End-to-End (Pre-Envío → Envío → Post-Envío)

### FASE 1: Preparación de Datos

```bash
# 1. Limpieza de Recipients
node dm_linkedin_recipients_cleaner.js
# → Genera: dm_linkedin_recipients_clean.csv

# 2. QA Pre-Envío
node dm_linkedin_qa_pre_send.js
# → Valida: Recipients + Variants
# → Salida: ✅ Pass / ❌ Errores

# 3. Verificación Manual (Opcional)
# Revisa dm_linkedin_QA_checklist.md antes de continuar
```

**Archivos necesarios:**
- `dm_linkedin_recipients.csv` (input)
- `dm_linkedin_export_json_examples.json` o hoja `Variants` en Google Sheets
- `dm_linkedin_variant_rules.json` (opcional, para selección inteligente)

---

### FASE 2: Envío

#### Opción A: Node.js (Local/Servidor)
```bash
# Configura CONFIG en dm_linkedin_sender_node.js:
# - messagesPerMinute: 10
# - dryRun: true (prueba primero)
# - suppressionFile: path a suppression list
# - slackWebhook: (opcional)

node dm_linkedin_sender_node.js
```

#### Opción B: Google Apps Script (Sheets)
1. Importa `dm_linkedin_sender_apps_script.gs` a Google Apps Script
2. Configura hojas: `Recipients`, `Variants`, `Rules`, `Suppression`
3. Ejecuta `sendBatch()` con throttling automático

**Archivos generados:**
- `dm_linkedin_logs.csv` (registro de todos los envíos)
- Alerts Slack (si configurado)

---

### FASE 3: Post-Envío

```bash
# 1. Lead Scoring
node dm_linkedin_score_from_logs.js
# → Genera: dm_linkedin_lead_scores.csv
# → Prioriza follow-ups

# 2. Alertas Dinámicas
node dm_linkedin_alerts_from_logs.js
# → Analiza logs por campaña/variante
# → Envía Slack si hay anomalías

# 3. Export a CRM
node dm_linkedin_export_crm.js
# → Genera: dm_linkedin_crm_export.csv
# → Importa a HubSpot/Salesforce
```

---

## 🎯 Flujo Típico Semanal

### Lunes: Preparación
- **09:00** → Limpieza de Recipients (`recipients_cleaner.js`)
- **09:30** → QA Pre-Envío (`qa_pre_send.js`)
- **10:00** → Revisión manual + ajustes

### Martes-Viernes: Envío
- **09:00-17:00** → Envío programado (throttling automático)
- **18:00** → Revisión diaria de logs

### Viernes PM: Análisis
- **16:00** → Lead Scoring (`score_from_logs.js`)
- **17:00** → Export a CRM (`export_crm.js`)
- **17:30** → Revisión de métricas y optimización

---

## 🛡️ Protecciones Integradas

1. **Deduplicación:** Evita envíos duplicados a mismo `profileUrl`
2. **Suppression Lists:** Perfil y empresa (90 días por defecto)
3. **Compliance Scan:** Valida longitud, claims riesgosos, opt-out
4. **Throttling:** Respeta límites de LinkedIn (10 DMs/min recomendado)
5. **Dry-Run Mode:** Prueba sin enviar antes de producción
6. **Retries con Backoff:** Maneja errores temporales automáticamente

---

## 📊 Tracking y Analytics

### Métricas Clave (desde logs)
- **Tasa de Envío:** `SENT / TOTAL`
- **Tasa de Respuesta:** Manual (trackear en CRM)
- **Tasa de Conversión:** Link clicks + respuestas positivas
- **Errores:** `ERROR / TOTAL`
- **Opt-outs:** `STOP` recibidos

### Herramientas
- **Google Sheets:** `dm_linkedin_sheets_template_formulas.md`
- **CRM:** Import `dm_linkedin_crm_export.csv`
- **UTM Tracking:** `dm_linkedin_utm_tracking.md`

---

## 🚨 Troubleshooting Rápido

| Problema | Solución |
|----------|----------|
| QA falla | Revisa headers de CSV (name, profileUrl requeridos) |
| Sin envíos | Verifica `dryRun: false` y método de envío implementado |
| Duplicados | Usa `recipients_cleaner.js` antes de enviar |
| Errores altos | Revisa logs, puede ser throttling o bloqueo temporal |
| Alertas Slack no llegan | Verifica webhook en CONFIG |
| Variantes no se seleccionan | Revisa `variant_rules.json` y campos en Recipients (industry, seniority, locale) |

---

## 📚 Referencias Rápidas

- **Setup Completo:** `dm_linkedin_orchestrator_readme.md`
- **Variantes Localizadas:** `dm_linkedin_variants_localized_completo.json`
- **Reglas de Variantes:** `dm_linkedin_variant_rules_localized.json`
- **Analytics:** `dm_linkedin_analytics_optimization.md`
- **Compliance:** `dm_linkedin_compliance_scanner.md`

---

**🎯 Objetivo:** Automatizar el 80% del proceso, mantener control humano en decisiones clave.

