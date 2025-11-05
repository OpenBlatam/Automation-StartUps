# Playbook de Automatización (Zapier / Make) — Outreach DM

Objetivo: minimizar tareas manuales y mantener tracking consistente.

## Flujos recomendados

### 1) Enriquecimiento y CRM
- Trigger: Nueva fila en `CRM_OUTREACH_FIELDS.csv` (Google Sheets)
- Steps:
  1. Enriquecer LinkedIn/empresa (Clearbit/Similar)
  2. Generar UTM (si falta) con fórmula en Sheets
  3. Crear/actualizar contacto en CRM (HubSpot/ActiveCampaign)
  4. Añadir etiquetas: industria, producto, versión DM

### 2) Envío secuencial LinkedIn + Email
- Trigger: Contacto con status = "ready_to_outreach"
- Steps:
  1. Crear tarea en LinkedIn (Sales Navigator) o notificación Slack
  2. Enviar Email Toque 1 (si hay email)
  3. Espera 5 días → Toque 2 (canal alterno)
  4. Espera 10 días → Toque 3 + recurso

### 3) Registro de interacciones
- Trigger: Respuesta o clic (Mailchimp/ActiveCampaign/Webhooks)
- Steps:
  1. Actualizar CRM con evento y fecha
  2. Cambiar status: responded / booked / not_interested
  3. Crear evento de calendario si booked

### 4) UTM + Analytics
- Trigger: Clic en enlace UTM (GA4/Segment)
- Steps:
  1. Enviar evento a CRM (via Segment/HubSpot)
  2. Actualizar lead score

## Buenas prácticas
- 1 flujo por objetivo, nombra Zaps/Scenarios con convención
- Registra errores en canal Slack #outreach-alerts
- Revisa logs semanalmente, iterar por KPIs

## Campos mínimos por sistema
- CRM: email, nombre, empresa, industria, tags, UTM
- Email: listas/etiquetas por industria y producto
- Sheets: estado, timestamps, owner

## Seguridad y cumplimiento
- Minimiza PII, usa roles y 2FA
- Revisa DPA de herramientas y ubicación de datos



