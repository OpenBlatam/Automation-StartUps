# 🚀 Despliegue en 5 Pasos (Innovación SO)

1) Preparar entorno
- Duplicar `00_ENV_EXAMPLE.env` → `.env` y completar claves.
- Crear propiedades en HubSpot usando `00_HUBSPOT_PROPERTY_DEFINITIONS.json`.

2) CRM y datos
- Importar `00_CRM_PROPERTIES_SCHEMA.yaml` (referencia) y cargar CSVs:
  - `00_CSV_IMPORT_CONTACTS_SAMPLE.csv`
  - `00_CSV_IMPORT_DEALS_SAMPLE.csv`
- Validar vistas en tu CRM/Dashboard (ver `00_DASHBOARD_TEMPLATE_AIRTABLE.md`).

3) Automatizaciones
- En Make: seguir `00_MAKE_IMPLEMENTATION_GUIDE.md`.
- Importar `00_MAKE_SCENARIO_BLUEPRINT.json` y setear variables de entorno.
- Probar Escenario 1 con 1 lead de prueba (QA de marca activo).

4) Mensajería y prompts
- Usar prompts de `00_PROMPTS_BLOCKS_FOR_MAKE.md` y variantes de
  - `00_DM_STARTER_*` (industria)
  - `00_MICRO_DMS_WHATSAPP_LINKEDIN.md` (micro‑DMs ES/EN/PT)

5) Medir y iterar (cadencia semanal)
- Seguir `00_CHECKLIST_OPERATIVO_SEMANAL.md`.
- Reportar KPIs y tomar decisiones en `00_ESTRATEGIA_INNOVACION_PALANCAS_ALTO_IMPACTO.md`.
