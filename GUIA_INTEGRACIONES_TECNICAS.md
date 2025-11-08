---
title: "Guía de Integraciones Técnicas - Automatización"
category: "09_sales"
tags: ["sales", "integrations", "technical"]
created: "2025-01-27"
path: "GUIA_INTEGRACIONES_TECNICAS.md"
---

# 🔌 Guía de Integraciones Técnicas
## Configuraciones Paso a Paso para Automatización Completa

**Versión:** 1.0  
**Última actualización:** Enero 2025

---

## 🔗 INTEGRACIÓN 1: HUBSPOT + MAKE.COM

### Configuración Completa

**Paso 1: Conectar HubSpot en Make.com**

```
1. Ir a Make.com → Create Scenario
2. Click en "Add module" → Search "HubSpot"
3. Seleccionar "HubSpot CRM"
4. Click "Create a connection"
5. Ingresar API Key de HubSpot
   - Obtener en: HubSpot → Settings → Private Apps → Create
6. Autorizar conexión
```

**API Key Setup en HubSpot:**
```
1. Settings → Integrations → Private Apps
2. Create Private App
3. Nombre: "Make.com Integration"
4. Scopes necesarios:
   - crm.objects.contacts.read
   - crm.objects.contacts.write
   - crm.objects.deals.read
   - crm.objects.deals.write
   - marketing.email.read
   - marketing.email.send
5. Create → Copy API Key
```

---

**Paso 2: Crear Webhook en Make.com**

```
1. En Make.com scenario, agregar "Webhooks" module
2. Seleccionar "Custom webhook"
3. Click "Add" → Copiar URL generada
4. Esta URL se usará para recibir datos de HubSpot
```

**Paso 3: Configurar HubSpot Workflow**

```
1. HubSpot → Automation → Workflows
2. Create Workflow
3. Trigger: "Contact property changes"
4. Condition: "lead_score > 60"
5. Action: "Send webhook"
   - URL: [URL del webhook de Make.com]
   - Method: POST
   - Body:
     {
       "contact_id": "{{contact.id}}",
       "email": "{{contact.email}}",
       "lead_score": "{{contact.lead_score}}",
       "company": "{{contact.company}}"
     }
```

---

## 🔗 INTEGRACIÓN 2: TYPEFORM → MAKE.COM → HUBSPOT

### Configuración Completa

**Paso 1: Crear Typeform**

```
1. Crear nuevo Typeform
2. Agregar preguntas:
   - Budget (Multiple choice)
   - Timeline (Multiple choice)
   - Authority (Yes/No)
   - Need (Short text)
3. Guardar form
```

**Paso 2: Configurar Webhook en Typeform**

```
1. Typeform → Settings → Integrations
2. Webhooks → Add webhook
3. URL: [URL del webhook de Make.com]
4. Events: Form responses
5. Save
```

**Paso 3: Configurar Make.com Scenario**

```
Modules:
1. Webhook (Trigger)
   - URL: [URL del webhook]
   - Method: POST

2. Set Variables
   Variables:
   - email: {{webhook.body.answers.email}}
   - budget: {{webhook.body.answers.budget}}
   - timeline: {{webhook.body.answers.timeline}}
   - authority: {{webhook.body.answers.authority}}

3. Calculate Score
   - IF budget = "$1,000-5,000" → score = +30
   - IF timeline = "30 days" → score = +20
   - IF authority = "Yes" → score = +20
   - Total score = sum of all

4. HubSpot - Create/Update Contact
   - Email: {{email}}
   - Lead Score: {{total_score}}
   - Budget: {{budget}}
   - Timeline: {{timeline}}
   - Authority: {{authority}}

5. IF score > 60
   THEN:
   - HubSpot - Add to List: "Hot Leads"
   - HubSpot - Assign to Owner: "SDR_Senior"
   - HubSpot - Create Task: "Call within 24h"
```

---

## 🔗 INTEGRACIÓN 3: GOOGLE SHEETS → MAKE.COM → HUBSPOT

### Configuración Completa

**Paso 1: Configurar Google Sheets**

```
1. Crear Google Sheet
2. Columnas:
   A: Email
   B: Name
   C: Company
   D: Score
   E: Status
3. Agregar datos de prueba
```

**Paso 2: Configurar Make.com Scenario**

```
Modules:
1. Google Sheets - Watch Rows
   - Spreadsheet: [Tu sheet]
   - Sheet: "Sheet1"
   - Trigger: When row is added

2. HubSpot - Create/Update Contact
   - Email: {{row.email}}
   - First Name: {{row.name}}
   - Company: {{row.company}}
   - Lead Score: {{row.score}}

3. IF score > 60
   THEN:
   - HubSpot - Add to List: "Hot Leads"
   - HubSpot - Assign to Owner: "SDR"
```

---

## 🔗 INTEGRACIÓN 4: SLACK → HUBSPOT

### Configuración Completa

**Paso 1: Configurar Slack App**

```
1. Slack → Apps → Create App
2. Nombre: "HubSpot Sales Notifications"
3. Scopes:
   - chat:write
   - channels:read
   - users:read
4. Install to Workspace
5. Copy Bot Token
```

**Paso 2: Configurar Make.com Scenario**

```
Modules:
1. HubSpot - Watch Contacts
   - Trigger: When contact is added to list "Hot Leads"

2. Slack - Create a Message
   - Channel: #sales-alerts
   - Text: "🔥 HOT LEAD ALERT\n\nName: {{contact.firstname}} {{contact.lastname}}\nCompany: {{contact.company}}\nScore: {{contact.lead_score}}\nEmail: {{contact.email}}\nLink: {{contact.hubspot_url}}"
```

---

## 🔗 INTEGRACIÓN 5: ZOOM → HUBSPOT

### Configuración Completa

**Paso 1: Conectar Zoom en Make.com**

```
1. Make.com → Add Module → Zoom
2. Create Connection
3. Autorizar con Zoom account
```

**Paso 2: Configurar Make.com Scenario**

```
Modules:
1. HubSpot - Watch Deals
   - Trigger: When deal stage changes to "Demo Scheduled"

2. Zoom - Create Meeting
   - Topic: "Demo: {{deal.name}}"
   - Start Time: {{deal.demo_date}}
   - Duration: 30 minutes
   - Type: Scheduled

3. HubSpot - Update Deal
   - Meeting Link: {{zoom.meeting_url}}
   - Meeting ID: {{zoom.meeting_id}}
```

---

## 🔗 INTEGRACIÓN 6: CALENDLY → HUBSPOT

### Configuración Completa

**Paso 1: Conectar Calendly en HubSpot**

```
1. HubSpot → Settings → Integrations
2. Search "Calendly"
3. Connect Calendly
4. Autorizar conexión
```

**Paso 2: Configurar Workflow**

```
1. HubSpot → Automation → Workflows
2. Create Workflow
3. Trigger: "Calendly event scheduled"
4. Actions:
   - Update contact: "Demo Scheduled" = Yes
   - Create deal: "Demo Scheduled"
   - Send email: "Demo Confirmation"
   - Create task: "Prepare demo for [contact]"
```

---

## 📊 INTEGRACIÓN 7: GOOGLE ANALYTICS → HUBSPOT

### Configuración Completa

**Paso 1: Configurar Google Analytics**

```
1. Google Analytics → Admin → Data Streams
2. Create Stream
3. Copy Measurement ID
```

**Paso 2: Configurar Make.com Scenario**

```
Modules:
1. Google Analytics - Track Event
   - Measurement ID: [Tu ID]
   - Event Name: "Lead Generated"
   - Parameters:
     - email: {{contact.email}}
     - source: {{contact.lead_source}}
     - score: {{contact.lead_score}}

2. HubSpot - Update Contact
   - Last Activity: {{timestamp}}
   - Engagement Score: +10
```

---

## 🔧 CONFIGURACIONES AVANZADAS

### Error Handling

**En Make.com:**
```
1. Agregar "Error Handler" module
2. Configurar:
   - IF error occurs
   - THEN: Send email notification
   - Log error details
   - Continue execution
```

### Rate Limiting

**Para evitar límites de API:**
```
1. Agregar "Sleep" module entre calls
2. Configurar delay: 1-2 segundos
3. Usar batch processing cuando posible
```

### Data Validation

**Validar datos antes de enviar:**
```
1. Agregar "Filter" module
2. Validar:
   - Email format
   - Required fields
   - Data types
3. IF invalid → Skip or notify
```

---

## 📋 CHECKLIST DE INTEGRACIÓN

### Antes de Configurar
- [ ] Tener acceso a todas las herramientas
- [ ] Tener API keys necesarios
- [ ] Entender flujo deseado
- [ ] Documentar requisitos

### Durante Configuración
- [ ] Conectar cada herramienta
- [ ] Probar cada módulo individualmente
- [ ] Validar datos
- [ ] Manejar errores

### Después de Configurar
- [ ] Probar end-to-end
- [ ] Verificar con datos reales
- [ ] Documentar integración
- [ ] Monitorear primeros días

---

## 🚨 TROUBLESHOOTING COMÚN

### Problema: Webhook no recibe datos

**Solución:**
```
1. Verificar que URL es correcta
2. Verificar que webhook está activo
3. Verificar permisos en herramienta origen
4. Revisar logs en Make.com
```

### Problema: API rate limit alcanzado

**Solución:**
```
1. Agregar delays entre calls
2. Usar batch processing
3. Reducir frecuencia de syncs
4. Upgrade plan si necesario
```

### Problema: Datos no se actualizan

**Solución:**
```
1. Verificar que módulo está activo
2. Verificar permisos de escritura
3. Verificar formato de datos
4. Revisar logs de errores
```

---

**Fin de Guía de Integraciones Técnicas**

*Usar esta guía para configurar integraciones automáticas entre herramientas.*

