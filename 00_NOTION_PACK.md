# 🗂️ Notion Pack — Sistema Operativo de Innovación

## Databases (crear 3)
1) Contacts
- email (Title)
- first_name (Text)
- last_name (Text)
- company (Text)
- industry (Select)
- channel (Select: LinkedIn, Email, WhatsApp)
- language (Select: es, en, pt)
- dm_variant (Select: A, B, C, D, E, F)
- lead_score (Number)
- best_send_hour (Number)
- primary_objection (Select)
- timezone (Text)

2) DMs
- dm_id (Title)
- contact (Relation → Contacts)
- channel (Select)
- variant (Select)
- sent_at (Date)
- opened (Checkbox)
- replied (Checkbox)
- reply_at (Date)
- time_to_reply_min (Formula: dateBetween(prop("reply_at"), prop("sent_at"), "minutes"))
- followup_count (Number)

3) Deals
- deal_name (Title)
- contact (Relation → Contacts)
- amount (Number)
- currency (Select)
- stage (Select: Lead, DM Sent, Demo Booked, Proposal Sent, Closed Won, Closed Lost)
- demo_booked_at (Date)
- outcome_pricing (Checkbox)
- package_tier (Select: Starter, Growth, Scale, Enterprise)
- mrr_delta_expected (Number)
- kpi_baseline (Number)
- kpi_target (Number)

## Relations & Rollups
- Contacts ↔ DMs (relation 1‑N)
- Contacts ↔ Deals (relation 1‑N)
- Deals rollups:
  - DMs enviados (count of related DMs)
  - Tiempo a demo (min dateBetween demo_booked_at vs first DM sent)

## Views sugeridas
- Contacts: "Prioritarios" (lead_score ≥ 6, orden desc)
- DMs: "Semana" (sent_at esta semana)
- DMs: "Variantes" (agrupado por variant, ordenar por replied desc)
- Deals: "Pipeline" (Board por stage)

## Templates (DMs)
- Template "DM Variante A": bloques con placeholders {hook} {beneficio} {prueba} {CTA}
- Template "Seguimiento 48h": bloque listo para duplicar

## Import rápido
- Importa `00_CSV_IMPORT_CONTACTS_SAMPLE.csv` a Contacts (mapear columnas)
- Importa `00_CSV_IMPORT_DEALS_SAMPLE.csv` a Deals (luego relaciona contact por email)

## Dashboard (Página)
- KPIs (linked views):
  - Reply Rate: filtro replied=true / total DMs
  - DM→Demo: deals stage="Demo Booked" / DMs con reply
  - Demo→Win: deals "Closed Won" / "Demo Booked"
- Tableros: Pipeline (Deals), Variantes Ganadoras (DMs)

## Automatización ligera (Notion Buttons)
- Botón "Crear Seguimiento" → duplica template y asocia al contact
- Botón "Marcar Demo" → set stage y demo_booked_at

## Estándares de datos
- Propiedades en inglés minúscula para integraciones (ej. lead_score)
- Títulos amigables en español para UX

## Siguientes pasos
- Conectar Make vía Notion API (si prefieres Notion como fuente)
- Sincronizar reportes con Google Sheets o BI si necesitas gráficos avanzados
