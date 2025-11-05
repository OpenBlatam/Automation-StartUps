# MANIFEST – Escalera de Valor (Curso / SaaS / IA Bulk)

Documentación principal
- ESCALERA_VALOR_3_PRODUCTOS_COMPLETA.md – Diseño de 4 pasos + automatizaciones + KPIs
- README_IMPLEMENTACION_ESCALERA.md – Pasos de implementación (import, zaps, landings)

Automatización y datos
- automation/zapier_blueprints.json – Blueprints Zapier
- automation/make_scenarios.json – Blueprints Make
- automation/utm_taxonomy.csv – Taxonomía UTM
- automation/webhook_examples.json – Payloads de Typeform/Stripe/Calendly
- automation/crm_field_mapping_hubspot.csv – Mapeo HubSpot
- automation/salesforce_objects.md – Objetos/fields Salesforce

Bases (CSV)
- Base: leads.csv, eventos.csv, ofertas.csv, compras.csv, tareas.csv, webinars.csv, demos.csv
- Muestras (10 filas): *_sample.csv
- Calculadora: automation/calculadora_precios_roi.csv

Contenido y plantillas
- Emails Markdown: automation/email_templates.md
- DMs Markdown: automation/dm_templates.md
- Emails HTML: automation/email_templates_html/*.html
- Emails TXT: automation/email_templates_text/*.txt
- A/B Matrix: automation/ab_test_matrix.md
- KPIs Dashboard: automation/dashboard_kpis.md
- Compliance/Onboarding: automation/checklist_compliance_onboarding.md

Cómo usar
1) Importa CSV base en Airtable/Notion
2) Activa blueprints (Zapier/Make)
3) Carga emails/DMs en tu ESP/CRM
4) Publica landings con UTM de utm_taxonomy.csv
5) Monitorea KPIs y ejecuta A/B tests
