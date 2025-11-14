# 🔗 Integraciones: Slack + Calendly

## Slack (Notificaciones de Eventos)
Eventos a notificar:
- DM Reply (positivo)
- Demo Booked
- Deal Won/Lost

Formato sugerido (mensaje):
- Título: Evento + Lead/Deal
- Cuerpo: canal, variante, lead_score, hora local, CTA interno (abrir en CRM)

Implementación (Make):
1) Añade módulo Slack → Incoming Webhook o Bot (OAuth).
2) En S3: después de crear Deal, envía mensaje a canal #sales.
3) En S2: al enviar Seguimiento 1, registra nota en hilo del lead (opcional).

Payload ejemplo (JSON):
```
{
  "text": "Demo Booked: Ana (Acme) — Mié 11:00",
  "blocks": [
    {"type":"section","text":{"type":"mrkdwn","text":"*Demo Booked* • Ana / Acme\nCanal: LinkedIn • Variante: A • Score: 8"}},
    {"type":"actions","elements":[
      {"type":"button","text":{"type":"plain_text","text":"Abrir en HubSpot"},"url":"https://app.hubspot.com/..."}
    ]}
  ]
}
```

## Calendly (Agendamiento)
Uso:
- En S3, tras clasificar reply positivo, generar link y proponer 2 horarios.

Implementación (Make):
1) Módulo Calendly: Create Scheduling Link (API key).
2) Variables: duración 15 min, timezone del lead, ventanas sugeridas.
3) Inyectar link en DM/Email de confirmación y registrar `demo_booked_at` al evento creado.

Buenas prácticas:
- Sincronizar timezone (propiedad `timezone`/`best_send_hour`).
- Enviar recordatorio 24h antes por el mismo canal del DM.
