# Implementación en 7 pasos – Escalera de Valor (Curso / SaaS / IA Bulk)

Prerequisitos
- Cuentas: Airtable/Notion, Zapier o Make, ESP (MailerLite/Sendgrid), Calendly, Stripe
- Archivos en esta carpeta: ver `ESCALERA_VALOR_3_PRODUCTOS_COMPLETA.md`

Paso 1) Bases de datos
- Importa CSVs base: `automation/leads.csv`, `eventos.csv`, `ofertas.csv`, `compras.csv`, `tareas.csv`, `webinars.csv`, `demos.csv`
- (Opcional) Importa CSVs de muestra `*_sample.csv` para test

Paso 2) Landings + Capturas
- Publica 3 landings (LM por producto) con formularios Typeform/Webflow
- Asegura UTM y campos clave (nombre, email, producto)

Paso 3) Automatizaciones
- Zapier: importa `automation/zapier_blueprints.json`
- Make: importa `automation/make_scenarios.json`
- Activa: LM capture, webinar reminders, tripwire purchase, demo flow

Paso 4) Contenido y Emails
- Carga plantillas: `automation/email_templates.md` y `automation/dm_templates.md`
- Usa HTML en `automation/email_templates_html/*` y texto plano en `automation/email_templates_text/*`

Paso 5) Ofertas y Checkout
- Crea productos/precios en Stripe según `ofertas.csv`
- Conecta checkout a los Zaps/Scenarios de compra

Paso 6) Dashboards y KPIs
- Configura vistas en Airtable/Notion
- Guía: `automation/dashboard_kpis.md` y UTM: `automation/utm_taxonomy.csv`

Paso 7) Compliance + QA
- Revisa `automation/checklist_compliance_onboarding.md`
- Ejecuta un flujo E2E con `*_sample.csv`

Anexos
- A/B tests: `automation/ab_test_matrix.md`
- Calculadora ROI: `automation/calculadora_precios_roi.csv`
- CRM mappings: `automation/crm_field_mapping_hubspot.csv`, `automation/salesforce_objects.md`
- Webhooks ejemplos: `automation/webhook_examples.json`

