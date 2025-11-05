# Plan de Contingencia – Automatizaciones (Zapier/Make/ESP)

Detección (monitoring)
- [ ] Dashboards de errores Zapier/Make abiertos durante Go‑Live
- [ ] Alertas por email/Slack si: error rate > 5% o colas detenidas > 10 min
- [ ] Vistas “Eventos sin siguiente paso” en Airtable/Notion

Triage (prioridad)
1) Compras/Checkout (impacto directo en ingresos)
2) Captura LM/Emails de entrega (onboarding)
3) Reminders de webinar/Demo (oportunidad)

Fixes rápidos
- [ ] Reejecutar tareas fallidas (Zap replay / Make queue)
- [ ] Cambiar credenciales/API keys expiradas
- [ ] Reducir tasa/envíos (ESP) si hay rebotes/spam alerts
- [ ] Desactivar temporalmente steps opcionales (branch no crítico)

Fallbacks
- LM: enviar manual Email 0 (plantillas TXT) a leads del período afectado
- Webinar: reenviar reminder T‑2/T+1 manualmente desde ESP
- Tripwire/Core: enviar checkout links directos por email/DM
- Demo: usar Calendly link directo + crear Task manual en CRM

Post‑mortem (24–48h)
- [ ] Registrar incidente (causa raíz, impacto, tiempo de resolución)
- [ ] Añadir test automático/regla para evitar repetición
- [ ] Actualizar README y SOPs si aplica
