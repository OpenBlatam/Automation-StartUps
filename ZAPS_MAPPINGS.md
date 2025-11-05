# Zaps — Pasos y Mapeos de Campos

## Webinar: Registro → Confirmación → Recordatorios → Replay → NPS
1. Trigger: Typeform/Google Forms — New Entry
   - Campos: email, nombre, webinar_id, fecha
2. Action: HubSpot/CRM — Create/Update Contact
   - email ← email, firstname ← nombre, tag/webinar ← webinar_id
3. Action: Zoom — Create Registrant
   - webinarId ← webinar_id, email ← email, first_name ← nombre
4. Action: Gmail — Send Email (Confirmación)
   - to ← email, subject/body con {LINK_ZOOM} y {LINK_CALENDAR}
5. Action: Delay Until (24h antes)
6. Action: Gmail — Send Email (Recordatorio 24h) / Twilio WhatsApp (opcional)
7. Action: Delay Until (1h antes)
8. Action: Twilio WhatsApp — Send Message (Recordatorio 1h)
9. Trigger: Zoom — Recording Completed
10. Action: Transcripción (AssemblyAI/Whisper)
11. Action: OpenAI — Resumen/FAQs (prompt base)
12. Action: Notion — Create Page (biblioteca)
13. Action: Gmail — Send Email (Replay + CTA)
14. Action: Google Forms — Prefilled NPS link (opcional)

## SaaS: Dunning + Suspensión/React. | Enriquecimiento + Scoring
1. Trigger: Stripe — Charge Failed
2. Action: Customer.io/HubSpot — Start Dunning Series
3. Action: Delay/Retry
4. Filter: retries ≥ 3
5. Action: Webhook — POST /suspend
6. Trigger: Stripe — Invoice Payment Succeeded
7. Action: Webhook — POST /reactivate
8. Action: Gmail — Send Email (Welcome Back)

Enriquecimiento + Scoring
1. Trigger: HubSpot — New Lead
2. Action: Clay/Clearbit — Enrich
3. Action: HubSpot — Update Properties (lead_score)
4. Action: Assign Owner (reglas)

## IA Bulk: Sheets → 3 Webhooks → Docs → Slack
1. Trigger: Google Sheets — New/Updated Row (estado = pendiente)
   - Campos: id, prompt
2. Action: Webhook — 3x POST (brief/articulo/post)
3. Action: Google Docs — Create Document (con contenido)
4. Action: Slack — Send Message (enlaces)

## Campos estándar sugeridos
- Contacto: email, nombre, empresa, cargo, fuente
- Webinar: webinar_id, fecha, link_zoom, link_calendar
- Dunning: customer_id, retries, estado
- Bulk: jobId, prompt, tipo_salida, enlace
