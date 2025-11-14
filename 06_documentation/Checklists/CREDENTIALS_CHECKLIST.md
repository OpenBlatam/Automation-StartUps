# Checklist de Credenciales y Scopes

## Google (Drive/Docs/Sheets/Calendar)
- Cuenta de servicio (recomendada)
  - Scopes mínimos:
    - https://www.googleapis.com/auth/drive.file
    - https://www.googleapis.com/auth/documents
    - https://www.googleapis.com/auth/spreadsheets
    - https://www.googleapis.com/auth/calendar.events
  - Compartir carpetas/hojas con `client_email` de la cuenta de servicio

## Zoom
- OAuth App (Server-to-Server o OAuth)
  - Permisos: `meeting:read`, `meeting:write`, `recording:read`

## Gmail
- Emisor verificado, DKIM/SPF configurados
- Límite diario revisado (evitar bloqueos)

## Stripe
- Secret Key (live/test) y Webhook Secret
- Eventos: `charge.failed`, `invoice.payment_succeeded`

## Twilio (WhatsApp)
- SID + Auth Token
- Número remitente WhatsApp aprobado

## OpenAI
- API Key y modelo aprobado
- Presupuestos y alertas por uso

## Slack
- Webhook o Bot con permisos `chat:write`
- Canal de alertas definido

## CRM (HubSpot/Customer.io)
- API Key/Private App
- Campos: `lead_score`, `owner`, `lifecycle_stage`

## Notion
- API Key y `parent_page_id`
- Permisos a la integración sobre la página

## GitHub/CMS
- Token con `repo:read` (mínimo) o acceso a releases
- Acceso de publicación al CMS si aplica

## Buenas prácticas
- Rotar claves trimestralmente
- Guardar en vault seguro (no en repositorios)
- Separar credenciales prod/staging
