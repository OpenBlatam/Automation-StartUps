# 📆 Integración Calendly / Zoom (Paso a Paso)

## Objetivo
- Confirmación automática (WF2) + .ics + link Zoom + evento en Calendar

## Calendly → Webhook
1) Crear tipo de evento (15-30 min)
2) Habilitar webhooks (invitee.created)
3) Payload → WF2 (Make/Zapier)

## Zoom
1) Crear reunión plantilla (espera habilitada)
2) Reutilizar link y actualizar topic/fecha

## Workflow
1) Trigger: IG/WA/Email confirma
2) Crear evento (Calendly)
3) Generar ICS (UTC) + hora local en DM
4) Enviar confirmación + recordatorios (WF3)

## Campos a propagar
- first_name, email, timezone, variant_id, utm_*
