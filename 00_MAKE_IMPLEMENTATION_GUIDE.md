# 🔧 Guía Rápida de Implementación en Make (Step-by-step)

## Escenario 1: Nueva conexión → DM + CRM + Follow-up
- Módulos:
  1) Webhooks/LinkedIn Source → New Connection
  2) Clearbit/Hunter → Enrichment (email/industry/companySize)
  3) Iterator → Scoring (set variable lead_score)
  4) Router (por industria/score) → asignar dm_variant
  5) OpenAI/Claude → Generate DM (input: nombre, empresa, industry, variant)
  6) Delay Until → ventana horaria local (best_send_hour)
  7) LinkedIn/Email → Send Message
  8) HubSpot/Salesforce → Create/Update Contact (propiedades del YAML)
  9) HubSpot Task → Follow-up +48h

- Variables sugeridas: lead_score, dm_variant, best_send_hour, language.
- Reintentos: exponencial 1-5-15 min; dead-letter para errores.

## Escenario 2: 48h sin respuesta → Seguimiento y cambio de canal
- Módulos: Scheduler (cada hora) → Buscar contactos sin DM_REPLY → OpenAI → Seguimiento 1 → Canal alternativo → Update CRM → Reprogramar 5 días.

## Escenario 3: Respuesta positiva → Demo y Deal
- Módulos: Webhook Reply → Intent Classifier → Calendly Create Link → HubSpot Create Deal (stage Demo Booked) → Notificación Slack/Email → Checklist pre-demo.

## Escenario 4: Post-Demo → Propuesta y Cierre
- Módulos: Calendar/Events → On Demo Completed → Generar Propuesta (merge Contract + ROI) → Enviar → Task de Cierre 7 días → Recordatorio.

## Guardarraíles
- Rate limit por canal, stop-list global, horario laboral local, muestreo QA 10%.
- Logs a BI: variant, canal, hora local, lead_score, opened, replied, time_to_reply, demo, win.

## Entornos
- Usar variables de entorno (keys) y duplicar escenarios por entorno: dev/stage/prod.

## Checklist de Validación
- [ ] Campos CRM existen (ver `00_CRM_PROPERTIES_SCHEMA.yaml` / `00_HUBSPOT_PROPERTY_DEFINITIONS.json`).
- [ ] Envíos respetan ventanas horarias.
- [ ] Seguimientos solo a leads con score ≥ umbral.
- [ ] Logs llegan al dashboard (Airtable/Notion/BI).

