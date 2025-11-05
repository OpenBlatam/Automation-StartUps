# Scripts de Automatización WhatsApp & Email

Workflows complementarios para multi-canal (WhatsApp Business API + Email marketing).

---

## WORKFLOW WA1: WhatsApp - Trigger por Instagram DM

### Si responde "RESERVA"/"DEMO"/"SÍ" en Instagram
```
THEN:
  Action: Send WhatsApp Message
  To: {{phone_number}} (extraer de perfil si disponible, o preguntar)
  Message: [Versión WhatsApp de Templates_MultiCanal.md]
  
  + Link de calendario/acceso
  + Pregunta: "¿Prefieres continuar aquí o por IG?" (opcional)
```

### Integración con Zapier/Make
```
IF Instagram DM contains ["RESERVA", "DEMO", "SÍ"]
THEN:
  1. Extract phone from CRM/profile (si disponible)
  2. Send WhatsApp message (via WhatsApp Business API)
  3. Mark in CRM: "confirmed_via_whatsapp"
  4. Continue flow igual que Instagram
```

---

## WORKFLOW WA2: WhatsApp - Bump Automático

### Si no responde en IG después de 24h
```
Delay: 24h after Instagram DM
  
IF phone_number available:
  Send WhatsApp: "{{first_name}}, vi en IG que te escribí sobre el webinar.
  
¿Te interesa? Quedan pocos cupos.
  
Link: {{link}}"
  
IF no phone_number:
  Send Instagram bump (Workflow 7b)
```

---

## WORKFLOW EMAIL1: Email - Seguimiento de DM

### Si responde "RESERVA" en IG
```
THEN:
  Action: Send Email (Gmail/SendGrid/Mailchimp)
  Subject: "Confirmación: Webinar IA aplicada - {{date}}"
  
  Body: [Versión Email de Templates_MultiCanal.md]
  
  Attachments:
  - Calendar .ics file
  - Checklist PDF (si aplica)
  
  Track: Open rate, click rate (UTM)
```

### Integración
```
IF Instagram DM contains "RESERVA"
THEN:
  1. Extract email from CRM/Instagram profile
  2. Send confirmation email
  3. Add to email sequence (Mailchimp/Klaviyo)
  4. Track engagement score
```

---

## WORKFLOW EMAIL2: Email - Secuencia Post-No-Respuesta

### Si no responde en 48h (3 emails max)
```
Day 2: Email 1 - "Te escribí por IG..."
Subject: "¿Viste mi mensaje sobre el webinar?"

Day 4: Email 2 - Alternativa
Subject: "Alternativa: Replay privado del webinar"

Day 7: Email 3 - Último intento + recurso gratis
Subject: "Último mensaje + Checklist gratis"
```

### Cada email incluye:
- Link de opt-out claro
- Recurso gratuito como valor
- CTA único y claro

---

## WORKFLOW EMAIL3: Email - Post-Evento (Cierre)

### Si asistió al webinar/demo
```
+2 hours: Email de agradecimiento + recurso
+24 hours: Follow-up con propuesta (si aplica)
+48 hours: Oferta especial/pricing

Cada email trackeado para:
- Open rate
- Click rate  
- Conversión a venta
```

**Template base:**
```
Subject: "Gracias por asistir, {{first_name}}"

Body:
- Recurso entregado (checklist/documento)
- Propuesta/pricing personalizado
- CTA claro para siguiente paso
```

---

## CONFIGURACIÓN WHATSAPP BUSINESS API

### Setup básico
1. **Cuenta Business verificada**
2. **Phone number verificada**
3. **Template messages aprobadas** (para fuera de ventana 24h)

### Templates aprobadas (requeridas para automatización)
```
Template 1: "confirmacion_webinar"
- Variables: {{first_name}}, {{date}}, {{time}}, {{link}}

Template 2: "recordatorio_demo"  
- Variables: {{first_name}}, {{date}}, {{link}}

Template 3: "bump_seguimiento"
- Variables: {{first_name}}, {{link}}
```

### Rate Limits WhatsApp
- **Mensajes iniciados por ti:** 1,000 conversaciones/24h
- **Respuestas dentro ventana 24h:** Ilimitado
- **Template messages (fuera 24h):** Requieren aprobación previa

---

## CONFIGURACIÓN EMAIL MARKETING

### Plataformas recomendadas
- **Gmail/SendGrid:** Para transactional (confirmaciones)
- **Mailchimp/Klaviyo:** Para sequences (nurturing)
- **ActiveCampaign:** Para avanzado (automation compleja)

### Segmentación sugerida
```
Segment 1: "Responded_IG_DM" → Email confirmación + recursos
Segment 2: "Attended_Event" → Email cierre con propuesta
Segment 3: "No_Response_48h" → Secuencia de reactivación
Segment 4: "Opted_Out" → No enviar más (compliance)
```

---

## INTEGRACIÓN MULTI-CANAL

### Workflow maestro (coordina todos los canales)
```
Trigger: Instagram DM response

THEN (paralelo):
  → Instagram: Confirmación DM
  → WhatsApp: Confirmación (si phone disponible)
  → Email: Confirmación email + .ics
  → CRM: Update stage + tags
  → Calendar: Agregar evento
```

### Tracking unificado
```
All channels → Same UTM parameters
- utm_source: [instagram|whatsapp|email]
- utm_medium: [dm|wa|email]
- utm_campaign: [webinar_ia|saas_demo|iabulk_demo]
- utm_content: {{first_name}}

Track in Google Analytics/Sheets:
- Source attribution
- Multi-touch attribution
- Channel effectiveness
```

---

## MEJORES PRÁCTICAS MULTI-CANAL

### ✅ HACER
- Consistencia de mensaje entre canales
- Timing coordinado (no bombardear)
- Trackear source attribution
- Respetar preferencia del contacto

### ❌ EVITAR
- Enviar mismo mensaje en 3 canales simultáneamente
- No trackear origen (perdés datos)
- Ignorar opt-out de un canal cuando aplica a otros

---

## TEMPLATES RÁPIDOS WA/Email

### WhatsApp - Confirmación
```
{{first_name}}, confirmado tu lugar para el webinar 🎉

📅 {{date}}
⏰ {{time}}
🔗 {{link}}

¿Prefieres que te avise 10 min antes?
```

### Email - Seguimiento Tibio
```
Asunto: ¿Viste mi mensaje sobre el webinar?

Hola {{first_name}},

Te escribí por Instagram sobre el webinar gratuito de IA aplicada.

Si no lo viste, aquí va el resumen:
- 60 minutos con casos reales
- Ahorra 10+ horas semanales
- Checklist lista para aplicar

¿Te interesa? Quedan pocos cupos.

[RESERVAR AHORA] → {{link}}
```

---

**Integra estos workflows con los de Instagram para outreach 360°.**

