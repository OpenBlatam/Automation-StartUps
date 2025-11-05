# Looker Studio – Especificación de Dashboard

Fuentes de datos (conector CSV o Airtable Connector)
- Leads: fields → email, nombre, utm_source, utm_campaign, score, created_at
- Eventos: id, lead_id, tipo, producto, timestamp
- Ofertas: id, producto, escalon, precio
- Compras: id, lead_id, oferta_id, monto, fecha
- Webinars: id, titulo, fecha, registrados, asistentes
- Demos: id, lead_id, fecha, resultado

Campos calculados (en Looker Studio)
- Asistencia Webinar = asistentes / registrados
- CR Tripwire = ComprasTripwire / LeadsLM
- CR Core = ComprasCore / LeadsLM
- CR High‑Ticket = ComprasHT / InvitacionesHT
- AOV = SUM(monto) / COUNT_DISTINCT(lead_id)

Páginas y gráficos
1) Overview
   - Scorecards: Leads, CVR LM, Tripwire CR, Core CR, HT CR
   - Serie temporal: Leads por día
   - Tabla: Ingresos por producto (curso/saas/bulk)
2) Funnel por producto
   - Embudo (LM → TRP → CORE → HT) por producto
   - Tabla por campaña: utm_source/utm_campaign y tasas
3) Webinars
   - Tabla: título, fecha, registrados, asistentes, Asistencia
   - Serie temporal: Asistencia por evento
4) Demos y Ventas
   - KPI: Demo rate, No‑show
   - Tabla: resultado demo, conversiones a piloto/core/HT
5) ROAS (si hay Ads)
   - Tabla: plataforma, gasto, ingresos, ROAS

Filtros/controles
- Rango de fechas, Producto (curso/saas/bulk), Escalón (lm/trp/core/ht)
- Fuente (utm_source), Campaña (utm_campaign), Región/País

Métricas objetivo (líneas de referencia)
- CVR LM: 30–40% | Asistencia: 30–35% | TRP: 5–10% | CORE: 2–4% | HT: 15–30%

Notas de implementación
- Si usas CSV: programa actualización diaria; si Airtable: conector oficial o sync via Google Sheets
- Normaliza nombres de campos según `automation/utm_taxonomy.csv`
