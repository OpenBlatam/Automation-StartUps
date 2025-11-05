# Airtable – Fórmulas de KPIs y Campos Calculados

Leads
- full_name (si tienes nombre/apellido): CONCATENATE({nombre}, " ", {apellido})
- high_intent (checkbox): IF({score}>=6, 1, 0)

Eventos
- last_event_at (rollup desde Eventos.timestamp): MAX(values)
- last_event_type (linked + latest): usar automatización/Script si necesitas último tipo

Webinars
- asistencia_rate: IF({registrados}>0, {asistentes}/{registrados}, 0)

Funnel (en Leads con lookups a Compras/Ofertas)
- has_tripwire: IF(COUNTALL({compras_tripwire})>0, 1, 0)
- has_core: IF(COUNTALL({compras_core})>0, 1, 0)
- has_ht: IF(COUNTALL({compras_ht})>0, 1, 0)
- funnel_stage: IF({has_ht}, "HT", IF({has_core}, "CORE", IF({has_tripwire}, "TRP", "LM")))

KPIs por Lead (ingresos atribuibles)
- ingresos_tripwire: SUM(values) en rollup de montos donde escalón = "tripwire"
- ingresos_core: SUM(values) en rollup donde escalón = "core"
- ingresos_ht: SUM(values) en rollup donde escalón = "high_ticket"
- ingresos_total: {ingresos_tripwire}+{ingresos_core}+{ingresos_ht}

Derivados de Email
- open_rate_bucket: IF({open_rate}>=0.5, ">=50%", IF({open_rate}>=0.3, "30–49%", "<30%"))

Fecha/Timers
- days_since_last_event: DATETIME_DIFF(NOW(), {last_event_at}, 'days')
- recent_activity (checkbox): IF({days_since_last_event}<=7, 1, 0)

Notas
- Para last_event_type real, usa Automation: on new Evento → set campo en Lead.
- Para segmentaciones complejas, crea vistas guardadas (High‑intent, No‑show, Post‑webinar).
