#!/bin/sh
set -e
OUT=automatizaciones_entregables.zip
ZIPLIST="curso-ia-webinars.md saas-ia-marketing.md ia-bulk-3docs.md README-automatizaciones.md CHANGELOG-automatizaciones.md CREDENTIALS_CHECKLIST.md QUICKSTART.md SHEETS_SETUP.md ENV-PLANTILLA.env asistencia.csv pedidos.csv costosIA.csv leads.csv kanban_automatizaciones.csv ia_automation_collection.postman_collection.json runbook-curso-webinars.md runbook-saas-marketing.md runbook-ia-bulk.md onepager-curso-webinars.md onepager-saas-marketing.md onepager-ia-bulk.md PLANTILLAS_COMUNICACION.md PROMPTS_BASE.md APPS_SCRIPT_TEMPLATE.gs ZAPS_MAPPINGS.md zap_webinar.json zap_dunning.json zap_bulk.json"
rm -f "$OUT"
zip -9 "$OUT" $ZIPLIST >/dev/null
echo "Paquete generado: $OUT"
