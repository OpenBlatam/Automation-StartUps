# Import Airtable – Instrucciones rápidas

1) Crea base nueva: "Escalera de Valor"
2) Importa CSVs (en este orden):
   - leads.csv → Tabla Leads (Primary key: email)
   - eventos.csv → Tabla Eventos (Primary: id)
   - ofertas.csv → Tabla Ofertas (Primary: id)
   - compras.csv → Tabla Compras (Primary: id)
   - tareas.csv → Tabla Tareas (Primary: id)
   - webinars.csv → Tabla Webinars (Primary: id)
   - demos.csv → Tabla Demos (Primary: id)
3) Crea enlaces (linked records):
   - Eventos.lead_id → Leads
   - Compras.lead_id → Leads, Compras.oferta_id → Ofertas
   - Tareas.lead_id → Leads
   - Demos.lead_id → Leads
4) Campos calculados sugeridos:
   - Leads.funnel_stage (formula) basado en último evento
   - Ofertas.escalon (single select: lm/tripwire/core/ht)
5) Vistas útiles:
   - Leads Hoy (tareas pendientes)
   - No-asistentes webinar
   - High-intent (score ≥ 6 y evento en 7 días)
6) Prueba con *_sample.csv si quieres validar primero.
