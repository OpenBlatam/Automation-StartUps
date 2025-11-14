---
title: "Dm Linkedin Orchestrator Readme"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_orchestrator_readme.md"
---

# 🧭 Orquestador de DMs (Node + Google Sheets)

## Opción A: Node Sender (local/servidor)

### Requisitos
- Node 18+
- Archivos en `01_Marketing/`
  - `dm_linkedin_sender_node.js`
  - `dm_linkedin_export_json_examples.json`
  - `dm_linkedin_recipients.csv` (encabezados: name,profileUrl,variantId)

### Instalar y ejecutar
```bash
cd 01_Marketing
node dm_linkedin_sender_node.js
```

### Configurar
- Edita `messagesPerMinute`, `dryRun` y `logFile` dentro del script.
- Integra tu capa de envío real en `sendLinkedInDM()`.
- Logs se guardan en `dm_linkedin_logs.csv`.
- Selector inteligente: ajusta reglas en `dm_linkedin_variant_rules.json`.
- Compliance: ajusta `scanMessageCompliance()` y revisa `dm_linkedin_compliance_scanner.md`.
 - Supresión por perfil: `dm_linkedin_suppression_list.csv` (profileUrl, until_iso)
 - Supresión por empresa: `dm_linkedin_company_suppression.csv` (company, until_iso)
 - Recipients CSV ahora soporta columna `company` (opcional)

---

## Opción B: Google Apps Script (desde Sheets)

### Estructura de hojas
- Hoja `Recipients`: columnas `name`, `profileUrl`, `variantId` (opcional), `industry`, `seniority`, `hourLocal`, `locale`
- Hoja `Variants`: columnas `variant_id`, `message_A`, `message_B`, `link`, `opt_out`, `campaign`
- Hoja `Rules` (opcional): celda A1 con JSON de reglas (puedes pegar `dm_linkedin_variant_rules_localized.json`)
- Hoja `Logs`: creada automáticamente
 - Hoja `Suppression` (opcional): columnas `profileUrl`, `until_iso` (respeta opt-out/pausas hasta esa fecha)
 - (Opcional) Hoja `CompaniesSuppression`: columnas `company`, `until_iso` (para pausar por empresa)

### Pasos
1) Crea un Google Sheet y pega pestañas.
2) Copia el contenido de `dm_linkedin_sender_apps_script.gs` en el editor Apps Script.
3) Ajusta `messagesPerMinute` y `dryRun` en `CONFIG_()`.
4) Pega reglas en hoja `Rules` (A1) si usarás selección automática.
5) Conecta tu método real de envío en `sendDm_()`.
6) Ejecuta `sendBatch()`.

### Hoja `Variants` (ejemplo)
- Puedes importar `dm_linkedin_variants_sheet_example.csv` (incluye `message_es_mx`, `message_es_es`, `message_en_us`).

---

## Buenas prácticas de operación
- Comienza con `dryRun: true` y 5-8 msgs/min.
- Agrega delays y retries antes de producción.
- Siempre registra `variantId` y `utm_content`.
- Revisa `dm_linkedin_QA_checklist.md` y `dm_linkedin_brand_voice_compliance.md`.
 - Mantén `Suppression` al día (opt-out 90 días recomendado)
 - Si usas supresión por empresa, evita contacto a múltiples roles durante pausas de negociación

---

## Seguridad y límites
- Respeta límites de LinkedIn; evita envíos masivos.
- Nunca compartas credenciales en repos.
- Monitorea bloqueos/opt-outs y reduce volumen si suben.

---

## Extras: Alertas y Scoring
### Alertas desde logs (Node)
```bash
export SLACK_WEBHOOK="https://hooks.slack.com/services/..."
node dm_linkedin_alerts_from_logs.js
```
- Umbrales: ERROR >5%, SKIPPED_COMPLIANCE >10%, SKIPPED_SUPPRESSED >25%

### Lead Scoring
```bash
node dm_linkedin_score_from_logs.js
```
- Ver `dm_linkedin_lead_scoring.md`

---

## QA y Validación Pre-Envío
```bash
node dm_linkedin_qa_pre_send.js
```
- Valida estructura de Recipients y Variants
- Revisa antes de cada envío masivo

## Limpieza de Datos
```bash
node dm_linkedin_recipients_cleaner.js
```
- Genera `dm_linkedin_recipients_clean.csv`
- Normaliza, valida URLs y dedupe

## Export a CRM
```bash
node dm_linkedin_export_crm.js
```
- Genera `dm_linkedin_crm_export.csv` desde logs
- Formato compatible con HubSpot/Salesforce

## Troubleshooting
- Faltan variantes → Completa hoja `Variants` (coteja headers) o usa `dm_linkedin_variants_localized_completo.json`
- Mensajes vacíos → Revisa tokens `[Nombre]` y campos `message_A/B` o mensajes localizados
- Sin envíos → Asegura `dryRun: false` y método de envío implementado
- Alertas Slack no llegan → coloca webhook en `slackWebhook` (Apps Script/Node) y prueba manual con un payload simple
- Limpieza de Recipients → usa `dm_linkedin_recipients_cleaner.js` para generar `dm_linkedin_recipients_clean.csv` antes de enviar
