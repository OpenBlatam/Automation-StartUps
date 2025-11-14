## Validación de Opt-in y Plantillas (WhatsApp/Email)

### Objetivo
Asegurar que el canal elegido (WA/Email) cumple requisitos antes de enviar.

### Campos requeridos (CRM/Sheet)
- `has_wa_optin` (boolean)
- `wa_template_name` (string)
- `email_consent` (boolean: soft/hard)
- `email_verified_domain` (boolean)
- `country`, `niche`, `language`, `timezone_local`

### Reglas de validación
- WhatsApp: `has_wa_optin == true` AND `wa_template_name` en `WA_Templates_Index.csv` con `status=approved`
- Email: `email_consent == true` AND dominio en `Email_Domains_Verified.csv` con `verified=true`
- Si falla canal 1 → intentar siguiente en `Channel_Priority_Router.csv`

### Make/Zapier (pseudo)
1) Fetch contacto (CRM/Sheet)
2) Canal candidato = salida del Router (WF9)
3) Validar:
   - Si WA: chequear opt-in + plantilla activa en `WA_Templates_Index.csv`
   - Si Email: consentimiento + dominio verificado en `Email_Domains_Verified.csv`
4) Si falla → tomar siguiente canal en prioridad
5) Log: `validation_channel`, `reason`

### Sheets (validaciones rápidas)
- WA listo: `=AND(A2=TRUE, NOT(ISBLANK(B2)))`
- Email listo: `=AND(C2=TRUE, D2=TRUE)`

### Notas
- Mantener un registro de plantillas WA por idioma/uso: `WA_Templates_Index.csv`

