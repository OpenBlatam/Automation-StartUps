---
title: "Scripts Automatizacion Avanzada"
category: "08_ai_artificial_intelligence"
tags: ["ai", "artificial-intelligence", "script"]
created: "2025-10-29"
path: "08_ai_artificial_intelligence/Automation/scripts_automatizacion_avanzada.md"
---

# Scripts de Automatización Avanzada (Zapier/Make.com)

Workflows completos listos para copiar y configurar en tu automatizador favorito.

---

## WORKFLOW 1: Curso IA - Automatización Completa

### Trigger: Respuesta DM "RESERVA" / "SÍ" / "SI"

```
IF Instagram DM contains ["RESERVA", "SÍ", "SI", "LINK", "QUIERO"]
THEN:
```

#### Step 1: Enviar confirmación DM
```
Action: Send Instagram DM
To: {{dm_sender_username}}
Message: "¡Perfecto, {{first_name}}! 🎉

Link de acceso: {{zoom_link}}

📅 {{date}}
⏰ {{time}} ({{timezone}})
📝 60 minutos

¿Prefieres recordatorio 10 min antes?
(Sí/No)"

Wait for reply: Yes
Timeout: 24 hours
```

#### Step 2: Agregar a Google Sheets (tracking)
```
Action: Create Google Sheets Row
Spreadsheet: "Webinar_IA_Tracking"
Row data:
- timestamp: {{now}}
- nombre: {{dm_sender_name}}
- username: {{dm_sender_username}}
- email: {{dm_sender_email}} (si está disponible)
- status: "confirmed"
- recordatorio_10min: {{pending}}
- source: "instagram_dm"
- utm_campaign: "webinar_ia"
```

#### Step 3: Agregar a Calendly/Google Calendar
```
Action: Create Google Calendar Event
OR
Action: Add to Calendly (si usas Calendly)

Event:
- Title: "Webinar IA aplicada - {{dm_sender_name}}"
- Date: {{webinar_date}}
- Time: {{webinar_time}}
- Link: {{zoom_link}}
- Attendees: {{dm_sender_email}}
```

#### Step 4: Email de confirmación (opcional)
```
Action: Send Email (Gmail/SendGrid)
To: {{dm_sender_email}}
Subject: "Confirmación: Webinar IA aplicada - {{date}}"
Body: [Plantilla de email de confirmación]
```

#### Step 5: Crear recordatorio 24h antes
```
Action: Schedule Task (Delay)
Delay: {{webinar_datetime}} - 24 hours

Then: Send Instagram DM
Message: "{{first_name}}, empezamos en 24 horas. 

Link: {{zoom_link}}

Prepárate con:
- Lápiz y papel
- Tu stack actual
- 1 caso específico

¿Confirmas asistencia?"
```

#### Step 6: Recordatorio 10 min antes
```
Action: Schedule Task (Delay)
Delay: {{webinar_datetime}} - 10 minutes

Then: Send Instagram DM
Message: "{{first_name}}, empezamos en 10 min 🚀

Link: {{zoom_link}}

Nos vemos ahí 👋"
```

#### Step 7: Tracking post-webinar (automático)
```
Action: Wait (Delay)
Delay: 2 hours after {{webinar_datetime}}

Then:
- Check Zoom attendance (si se unió)
- If attended:
  → Send DM: "Gracias por asistir. Aquí tu checklist: [LINK]"
  → Update Sheets: status = "attended"
- If NOT attended:
  → Send DM: "Tienes el replay privado. ¿Lo quieres? (REPLAY)"
  → Update Sheets: status = "not_attended"
```

---

## WORKFLOW 2: SaaS IA - Automatización B2B

### Trigger: Respuesta DM "DEMO" / "AGENDA" / "CALENDARIO"

```
IF Instagram DM contains ["DEMO", "AGENDA", "CALENDARIO", "CALENDAR"]
THEN:
```

#### Step 1: Enviar link de calendario
```
Action: Send Instagram DM
Message: "¡Listo, {{first_name}}! 🎯

Reservé tu slot:
📅 {{date}}
⏰ {{time}} ({{timezone}})
📝 30 minutos

Link: {{calendly_link}}

¿Necesitas NDA antes?
(Sí/No)"

Wait for reply: Yes
```

#### Step 2: Agregar a CRM (HubSpot/Salesforce)
```
Action: Create/Update Contact in HubSpot
Fields:
- First Name: {{first_name}}
- Company: {{company}} (extraer del perfil si disponible)
- Lead Source: "Instagram DM"
- Lifecycle Stage: "Marketing Qualified Lead"
- Lead Status: "Demo Booked"
- Custom Field "Instagram Username": {{dm_sender_username}}
- Tags: ["demo_booked", "saas_ia", "instagram"]
```

#### Step 3: Si responde "Sí" a NDA
```
IF reply contains ["SÍ", "SI", "YES", "SEND"]
THEN:
  Action: Send Instagram DM with NDA attachment
  Message: "Perfecto, {{first_name}}. NDA adjunto. Una vez firmado, te contacto para agendar."
  
  Action: Send Email with NDA
  Attachment: [NDA_PDF]
  
  Update Sheets: nda_sent = "yes", nda_status = "pending"
```

#### Step 4: Recordatorio 2h antes
```
Action: Schedule Task
Delay: {{demo_datetime}} - 2 hours

Then: Send Instagram DM
Message: "{{first_name}}, nuestro demo es en 2 horas 🔥

Prepárate preguntas sobre {{company}} y tu stack actual.

Link: {{meeting_link}}

Nos vemos ahí 👋"
```

#### Step 5: Post-demo tracking
```
Action: Wait
Delay: 2 hours after {{demo_datetime}}

Then:
- Check Zoom/Calendly attendance
- If attended:
  → Send Email: Propuesta personalizada
  → Update CRM: Stage = "Demo Completed"
  → Update Sheets: show_rate = "yes"
  → Schedule follow-up: +24h
- If NOT attended:
  → Send DM: "¿Reprogramamos? Link: {{calendly_link}}"
  → Update CRM: Notes = "No-show, reprogramar"
```

---

## WORKFLOW 3: IA Bulk - Automatización con ejemplo PDF

### Trigger: Respuesta DM "SÍ" / "QUIERO" / "LINK"

```
IF Instagram DM contains ["SÍ", "SI", "QUIERO", "LINK", "YES"]
THEN:
```

#### Step 1: Confirmación + pregunta sobre ejemplo
```
Action: Send Instagram DM
Message: "¡Hecho, {{first_name}}! 🎉

Demo: {{date}} {{time}} ({{timezone}})

Link: {{zoom_link}}

En el demo generaremos:
📄 {{ejemplo_documento}} para {{industry}}

¿Prefieres recibirlo en PDF o Google Docs?
(PDF/Docs)"

Wait for reply: Yes
```

#### Step 2: Preparar ejemplo según industria
```
Action: Conditional Logic
IF {{industry}} = "ecommerce":
  → Documento ejemplo: "Ficha producto SEO"
IF {{industry}} = "consultoria":
  → Documento ejemplo: "Propuesta comercial"
IF {{industry}} = "B2B":
  → Documento ejemplo: "Reporte ejecutivo"

Store: {{ejemplo_documento_seleccionado}}
```

#### Step 3: Si piden ejemplo previo ("PDF" / "EJEMPLO")
```
IF reply contains ["PDF", "EJEMPLO", "EXAMPLE", "MUESTRA"]
THEN:
  Action: Send Instagram DM
  Message: "Perfecto, {{first_name}}!

  Ejemplo real:
  [LINK_EJEMPLO_PDF]

  Esto es lo que generaremos personalizado para {{industry}}."
  
  Action: Send Email with PDF attachment
  Attachment: {{ejemplo_pdf_path}}
```

#### Step 4: Recordatorio 2h antes con contexto
```
Action: Schedule Task
Delay: {{demo_datetime}} - 2 hours

Then: Send Instagram DM
Message: "{{first_name}}, empezamos en 2 horas 📄

Preparamos un ejemplo de {{use_case}} para {{industry}}.

Link: {{demo_link}}

¿Tienes alguna pregunta específica?"
```

#### Step 5: Post-demo: enviar documento generado
```
Action: Wait
Delay: 2 hours after {{demo_datetime}}

Then:
- Check attendance
- If attended:
  → Retrieve generated document from demo
  → Send via email (formato preferido: PDF/Docs)
  → Update Sheets: documento_enviado = "yes"
- If NOT attended:
  → Send replay + ejemplo estándar
```

---

## WORKFLOW 4: Clasificador Inteligente de Respuestas

### Trigger: Cualquier DM en Instagram

```
Action: Text Analysis (AI/Regex)
Classify message into categories:

Category Detection:
- "Interested": /(reserva|sí|si|link|voy|me interesa|demo|agenda|quiero)/i
- "Alternative time": /(no puedo|otro horario|otra hora|mañana|tarde|friday|monday)/i
- "Info first": /(info|información|checklist|material|replay|video|ejemplo|pdf)/i
- "Pricing": /(cuánto|cuesta|precio|price|cost|pricing)/i
- "NDA needed": /(nda|confidencial|confidential)/i
- "Not interested": /(no gracias|stop|baja|unsubscribe|no me interesa)/i
```

#### Then: Route to appropriate workflow
```
IF Category = "Interested":
  → Trigger Workflow 1, 2, or 3 (según oferta)

IF Category = "Alternative time":
  → Send DM: "Tengo {{date_alt}} {{time_alt}}. ¿Te sirve?"

IF Category = "Info first":
  → Send info email + DM con teaser

IF Category = "Pricing":
  → Route to pricing response script

IF Category = "NDA needed":
  → Send NDA + pause until signed

IF Category = "Not interested":
  → Mark as opt-out + send resource gratis
```

---

## WORKFLOW 5: Escalación Automática (Ghosting)

### Trigger: No reply after 24h desde DM inicial

```
Action: Conditional Logic
IF last_dm_sent > 24h ago AND status != "confirmed" AND status != "opt_out"
THEN:
```

#### Step 1: Día 2 - Oferta de checklist/ejemplo
```
Send Instagram DM:
"¿Quieres la checklist sin asistir? Te la envío gratis.

[LINK_CHECKLIST]"
```

#### Step 2: Día 4 - Urgencia real
```
Send Instagram DM:
"Cerramos inscripciones hoy. Puedo reservarte un replay privado. ¿Lo quieres?

(REPLAY)"
```

#### Step 3: Día 7 - Último intento
```
Send Instagram DM:
"Último mensaje: te dejo el resumen en 5 bullets. ¿Te lo comparto?

Si no respondes, no te molestaré más 👋"
```

#### Step 4: Si sigue sin responder
```
Action: Update Sheets
- status = "inactive"
- last_contact = {{today}}
- notes = "No response after 7 days, archived"

Action: Remove from active outreach list
```

---

## WORKFLOW 6: Sync Multi-Canal

### Trigger: Cualquier interacción (DM, Email, WhatsApp)

```
Action: Universal Contact Sync

Update in all systems:
- CRM (HubSpot/Salesforce): Latest interaction
- Google Sheets: All touchpoints
- Email marketing (Mailchimp/Klaviyo): Engagement score
- WhatsApp Business API: Conversation status
```

#### Sync Fields:
```
- Last Contact Date: {{interaction_timestamp}}
- Last Contact Channel: {{source_channel}}
- Last Message Sent: {{message_sent}}
- Response Rate: {{calculate}}
- Engagement Score: {{score}}
```

---

## WORKFLOW 7: Envío de variantes ultra‑cortas por palabra clave

Objetivo: responder en segundos con mensajes de 140–180 caracteres según oferta/nicho.

### Trigger: Mensaje entrante clasificado como "Interested" o "Bump"
```
IF Category IN ["Interested", "Bump"]
THEN:
  LookupRow in "DM_Variants_Short.csv" WHERE (dm_type={{offer}} AND language={{lang}} AND niche={{niche}})
  Take top result OR random among top 3
  Send Instagram DM: {{short_text}}
```

### Palabras clave sugeridas para activar
- Webinar/Curso: ["RESERVA", "RESERVE", "RESERVAR"]
- SaaS/Demo: ["DEMO", "AGENDA", "CALENDARIO"]
- IA Bulk: ["SÍ", "SI", "YES", "QUIERO"]

### Notas
- Añade fallback si no hay match: usar variante genérica del idioma
- Respeta rate limits; agrupa en lotes
- Loguea id de la variante enviada para A/B tracking

### Integración con Bumps (Workflow 7b)
Para automatizar bumps 24h/48h después del mensaje inicial:
```
Delay: 24h after {{initial_dm_timestamp}}
LookupRow in "DM_Variants_Short.csv" WHERE (id LIKE "B-%" AND niche={{niche}} AND language={{lang}})
Send Instagram DM: {{short_text}} (reemplaza {{first_name}}, {{date}}, {{time}})
Update Sheets: bump_sent = "yes", bump_timestamp = {{now}}
```

**Palabras clave para activar bumps:**
- Si no responde después de 24h → enviar bump
- Si responde "INFO" o "VIDEO" → enviar bump informativo
- Si menciona horario alterno → enviar bump con opciones

**Lógica de selección:**
1. Busca bump específico por `niche` y `language`
2. Si no hay match por nicho, usa bump genérico del idioma
3. Randomiza entre 2-3 bumps del mismo tipo para evitar repetición
4. Loguea `bump_variant_id` para tracking A/B

**Ejemplo práctico:**
```
Contacto: ecommerce, español, no respondió en 24h
→ Busca en CSV: B-ES-ECOM-* 
→ Selecciona random entre B-ES-ECOM-1, B-ES-ECOM-2, B-ES-ECOM-3
→ Envía: "{{first_name}}, ¿te reservo 1 lugar? Quedan 8. \"RESERVA\""
→ Update tracking: bump_sent = "yes", variant = "B-ES-ECOM-1"
```

---

## Configuración Recomendada

### Zapier
- Plan: Professional o higher (para delays avanzados)
- Apps necesarias: Instagram, Gmail, Google Sheets, Google Calendar, HubSpot/Salesforce, Zoom
- Webhooks para lógica custom

### Make.com (Integromat)
- Ventaja: Más operaciones incluidas en planes base
- Mejor para workflows complejos con múltiples condiciones
- Escenario: Nodos ilimitados

### Rate Limits a considerar
- Instagram DM: 15–25/hora máx.
- Email: 100/día sin warming up
- WhatsApp: 1000 conversaciones/24h (Business API)

---

## Testing Sugerido

1. **Test en modo sandbox primero**
   - Envía a tu propio número/email
   - Verifica merge‑tags
   - Confirma delays funcionan

2. **Test con 5–10 contactos reales**
   - Monitorea cada step
   - Ajusta mensajes según respuestas
   - Optimiza timing

3. **Escala gradualmente**
   - Semana 1: 50 contactos/día
   - Semana 2: 100 contactos/día
   - Semana 3+: Máximo según rate limits

---

## Troubleshooting Común

### Problema: Merge‑tags no se reemplazan
**Solución:** Verifica que el campo existe en el trigger (Instagram user data) y usa formato correcto: {{field_name}}

### Problema: Delays no funcionan
**Solución:** En Zapier usa "Delay by Schedule", en Make usa "Sleep" module

### Problema: Respuestas se pierden
**Solución:** Configura "Wait for reply" con timeout adecuado o usa webhook para capturar respuestas

### Problema: Rate limits
**Solución:** Agrega "Queue" modules o distribuye workflows en múltiples horas del día

