---
title: "Integraciones Tecnicas Especificas"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/integraciones_tecnicas_especificas.md"
---

# 🔌 Integraciones Técnicas Específicas
## Configuraciones listas para copiar y pegar

---

## 📧 INTEGRACIÓN 1: ActiveCampaign Setup Completo

### **Configuración Básica**

```
AUTOMATION 1: Welcome Sequence
Trigger: Tag added "Lead_Magnet_Downloaded"
Actions:
  1. Wait 0 hours
  2. Send email: Email 1
  3. Wait 72 hours
  4. Send email: Email 2
  5. Wait 168 hours
  6. Send email: Email 3

CONDITIONS:
- If email opened within 24h → Add tag "Hot_Lead"
- If email not opened in 72h → Add tag "Re_engage_Needed"
- If link clicked → Add tag "High_Interest"
```

### **Código de API Integration**

```javascript
// Integración ActiveCampaign API
const ActiveCampaign = require('activecampaign');

const ac = new ActiveCampaign(apiUrl, apiKey);

// Agregar lead a secuencia
function addToSequence(email, sequenceId) {
    return ac.api('contact/add', {
        email: email,
        tags: ['Lead_Magnet_Downloaded'],
        p: [sequenceId] // Agregar a secuencia automática
    });
}

// Trackear evento personalizado
function trackEvent(email, eventName, eventData) {
    return ac.api('contact/track', {
        email: email,
        actid: accountId,
        event: eventName,
        eventdata: JSON.stringify(eventData)
    });
}
```

---

## 📧 INTEGRACIÓN 2: Mailchimp Automation

### **Workflow Setup**

```
AUTOMATION 1: Lead Magnet Sequence
Trigger: Subscriber added to list "Lead_Magnet_Downloaders"
Delay: 0 hours
Send: Email 1 (Welcome + Webinar Invite)

AUTOMATION 2: Re-engagement
Trigger: Subscriber hasn't opened last 3 emails
Delay: 90 days
Send: Re-engagement email series

SEGMENTATION:
- Hot: Opened 3+ emails in last 30 days
- Warm: Opened 1-2 emails in last 30 days
- Cold: No opens in 60 days
```

### **Integración Mailchimp API**

```javascript
const mailchimp = require('@mailchimp/mailchimp_marketing');

mailchimp.setConfig({
  apiKey: 'your-api-key',
  server: 'usX' // e.g., us1
});

// Agregar a secuencia automática
async function subscribeToSequence(email, firstName) {
    try {
        const response = await mailchimp.lists.addListMember(listId, {
            email_address: email,
            status: 'subscribed',
            merge_fields: {
                FNAME: firstName
            },
            tags: ['Lead_Magnet_Downloader']
        });
        
        // Agregar a workflow automático
        await mailchimp.automations.addWorkflowEmailSubscriber(workflowId, {
            email_address: email
        });
        
        return response;
    } catch (error) {
        console.error('Error:', error);
    }
}
```

---

## 🔗 INTEGRACIÓN 3: Zapier Workflows

### **Zap 1: Lead Magnet Download → Email Sequence**

```
Trigger: Form submitted (Google Forms/Typeform)
Action 1: Add to ActiveCampaign/Mailchimp list
Action 2: Tag as "Lead_Magnet_Downloaded"
Action 3: Start automation sequence
Action 4: Send confirmation email
Action 5: Update CRM (HubSpot/Salesforce) with lead data
```

### **Zap 2: Email Opened → Update Engagement Score**

```
Trigger: Email opened (Mailchimp/ActiveCampaign webhook)
Action 1: Update engagement score in Google Sheets
Action 2: If score > 15, add tag "VIP_Lead"
Action 3: Send Slack notification to team
Action 4: Update CRM field "Last Email Engagement"
```

### **Zap 3: Form Abandonment Recovery**

```
Trigger: Form started but not completed (Tracking pixel)
Delay: 1 hour
Condition: Form not completed
Action 1: Send recovery email with link directo
Action 2: Add to retargeting audience (Facebook Pixel)
```

---

## 📊 INTEGRACIÓN 4: Google Analytics 4 (GA4) Eventos

### **Eventos Personalizados a Trackear**

```javascript
// Eventos de email marketing
gtag('event', 'email_opened', {
    'email_id': 'email_1_webinar',
    'user_id': userId,
    'timestamp': Date.now()
});

gtag('event', 'email_link_clicked', {
    'email_id': 'email_1_webinar',
    'link_url': clickedUrl,
    'cta_type': 'primary' // or 'secondary'
});

gtag('event', 'webinar_registered', {
    'email_id': 'email_1_webinar',
    'registration_source': 'email',
    'user_id': userId
});

gtag('event', 'trial_started', {
    'email_id': 'email_2_saas',
    'trial_source': 'email_sequence',
    'user_id': userId
});
```

### **Configuración GA4**

```
EVENTS CUSTOM:
1. email_opened
2. email_link_clicked
3. email_form_started
4. email_form_completed
5. webinar_registered
6. trial_started
7. trial_converted

CONVERSION EVENTS:
- webinar_registered (conversión)
- trial_started (conversión)
- trial_converted (conversión)
```

---

## 🔐 INTEGRACIÓN 5: Configuración SPF/DKIM/DMARC

### **SPF Record (DNS)**

```
TXT Record:
@  IN  TXT  "v=spf1 include:_spf.google.com include:mail.zendesk.com include:sendgrid.net ~all"
```

### **DKIM Record (DNS)**

```
TXT Record (generado por tu plataforma):
mail._domainkey  IN  TXT  "v=DKIM1; k=rsa; p=[PUBLIC_KEY]"
```

### **DMARC Record (DNS)**

```
TXT Record:
_dmarc  IN  TXT  "v=DMARC1; p=quarantine; rua=mailto:dmarc@yourdomain.com; ruf=mailto:dmarc@yourdomain.com; pct=100"
```

### **Verificación de Configuración**

```bash
# Verificar SPF
dig TXT yourdomain.com

# Verificar DKIM
dig TXT mail._domainkey.yourdomain.com

# Verificar DMARC
dig TXT _dmarc.yourdomain.com

# Herramientas online:
# - mxtoolbox.com
# - mail-tester.com
# - dmarcian.com
```

---

## 📱 INTEGRACIÓN 6: Facebook Pixel para Retargeting

### **Eventos a Trackear**

```javascript
// Pixel base
fbq('init', 'YOUR_PIXEL_ID');
fbq('track', 'PageView');

// Eventos de email
fbq('trackCustom', 'EmailOpened', {
    email_id: 'email_1_webinar'
});

fbq('trackCustom', 'EmailClicked', {
    email_id: 'email_1_webinar',
    link_url: clickedUrl
});

fbq('trackCustom', 'WebinarRegistered', {
    email_id: 'email_1_webinar',
    value: 0, // Gratis
    currency: 'USD'
});

fbq('track', 'Lead', {
    content_name: 'Webinar Registration',
    value: 0,
    currency: 'USD'
});
```

### **Audiencias Personalizadas**

```
AUDIENCIA 1: Email Opened but Not Registered
- Custom Event: EmailOpened
- Exclusion: WebinarRegistered
- Duration: 30 days

AUDIENCIA 2: Form Started but Not Completed
- Custom Event: FormStarted
- Exclusion: FormCompleted
- Duration: 7 days

AUDIENCIA 3: Webinar Registered but Not Attended
- Custom Event: WebinarRegistered
- Exclusion: WebinarAttended
- Duration: 60 days
```

---

## 🔄 INTEGRACIÓN 7: CRM Sync (HubSpot/Salesforce)

### **HubSpot Integration**

```javascript
const hubspot = require('@hubspot/api-client');

const hubspotClient = new hubspot.Client({
    accessToken: process.env.HUBSPOT_TOKEN
});

// Sincronizar email engagement con HubSpot
async function syncEmailEngagement(email, engagementData) {
    try {
        // Buscar contacto
        const searchResult = await hubspotClient.crm.contacts.searchApi.doSearch({
            query: email,
            limit: 1,
            properties: ['email']
        });
        
        if (searchResult.results.length > 0) {
            const contactId = searchResult.results[0].id;
            
            // Actualizar propiedades
            await hubspotClient.crm.contacts.basicApi.update(contactId, {
                properties: {
                    'last_email_opened': engagementData.openedAt,
                    'email_engagement_score': engagementData.score,
                    'last_email_clicked': engagementData.lastClickAt
                }
            });
            
            // Crear actividad
            await hubspotClient.crm.timeline.eventsApi.create({
                eventTypeId: 'email_engagement',
                email: email,
                extraData: engagementData
            });
        }
    } catch (error) {
        console.error('HubSpot sync error:', error);
    }
}
```

---

## 📊 INTEGRACIÓN 8: Dashboard en Google Sheets

### **Sincronización Automática de Métricas**

```javascript
// Google Sheets API para dashboard
const { GoogleSpreadsheet } = require('google-spreadsheet');

async function updateEmailMetrics(date, metrics) {
    const doc = new GoogleSpreadsheet(spreadsheetId);
    await doc.useServiceAccountAuth(creds);
    await doc.loadInfo();
    
    const sheet = doc.sheetsByIndex[0];
    
    await sheet.addRow({
        Date: date,
        'Open Rate': metrics.openRate,
        'Click Rate': metrics.clickRate,
        'Conversion Rate': metrics.conversionRate,
        'Emails Sent': metrics.sent,
        'Leads Generated': metrics.leads,
        'Revenue': metrics.revenue
    });
}
```

### **Fórmulas Útiles en Sheets**

```
CÁLCULO DE ROI:
=(Ingresos-Costos)/Costos*100

TASA DE CONVERSIÓN:
=Conversiones/Leads*100

COSTO POR LEAD:
=Costos_Total/Leads_Generados

LTV:CAC RATIO:
=LTV/CAC
```

---

## 🎯 INTEGRACIÓN 9: Slack Notifications

### **Alertas Automáticas al Team**

```javascript
const { WebClient } = require('@slack/web-api');

const slack = new WebClient(process.env.SLACK_TOKEN);

// Notificación de conversión
async function notifyConversion(leadData) {
    await slack.chat.postMessage({
        channel: '#sales-team',
        text: `🎉 Nueva conversión desde email marketing!`,
        blocks: [
            {
                type: 'section',
                text: {
                    type: 'mrkdwn',
                    text: `*Nueva Conversión:*\n` +
                          `Nombre: ${leadData.name}\n` +
                          `Email: ${leadData.email}\n` +
                          `Producto: ${leadData.product}\n` +
                          `Valor: $${leadData.value}`
                }
            }
        ]
    });
}

// Alerta de métricas bajas
async function alertLowMetrics(metrics) {
    if (metrics.openRate < 0.20) {
        await slack.chat.postMessage({
            channel: '#marketing-alerts',
            text: `⚠️ Open rate cayó a ${metrics.openRate * 100}%`,
            attachments: [{
                color: 'warning',
                fields: [
                    { title: 'Open Rate', value: `${metrics.openRate * 100}%`, short: true },
                    { title: 'Benchmark', value: '25%', short: true }
                ]
            }]
        });
    }
}
```

---

## 🔧 INTEGRACIÓN 10: Webhooks Personalizados

### **Webhook de Email Marketing Platform**

```javascript
// Express.js endpoint para recibir webhooks
const express = require('express');
const app = express();

app.use(express.json());

// Webhook de Mailchimp/ActiveCampaign
app.post('/webhook/email-event', (req, res) => {
    const event = req.body;
    
    switch (event.type) {
        case 'email_opened':
            handleEmailOpened(event.data);
            break;
        case 'email_clicked':
            handleEmailClicked(event.data);
            break;
        case 'email_bounced':
            handleEmailBounced(event.data);
            break;
        case 'email_unsubscribed':
            handleUnsubscribed(event.data);
            break;
    }
    
    res.status(200).send('OK');
});

function handleEmailOpened(data) {
    // Actualizar engagement score
    updateEngagementScore(data.email, 1);
    
    // Si es primera apertura, iniciar secuencia
    if (isFirstOpen(data.email)) {
        startSequence(data.email, 'post_open_sequence');
    }
    
    // Si es hot lead, notificar sales
    if (getEngagementScore(data.email) > 15) {
        notifySalesTeam(data.email);
    }
}
```

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN DE INTEGRACIONES

### **Fase 1: Setup Básico (Semana 1)**
- [ ] Configurar SPF/DKIM/DMARC
- [ ] Setup de plataforma email marketing
- [ ] Configurar tracking básico (GA4)
- [ ] Testing de envíos

### **Fase 2: Automatizaciones (Semana 2)**
- [ ] Configurar workflows básicos
- [ ] Setup de segmentación automática
- [ ] Configurar re-envíos
- [ ] Testing de automatizaciones

### **Fase 3: Integraciones (Semana 3)**
- [ ] Integración con CRM
- [ ] Setup de retargeting (pixels)
- [ ] Webhooks básicos
- [ ] Notificaciones al equipo

### **Fase 4: Optimización (Semana 4+)**
- [ ] Dashboard de métricas
- [ ] Alertas automáticas
- [ ] Integraciones avanzadas
- [ ] Análisis predictivo básico

---

## 🛠️ HERRAMIENTAS Y RECURSOS

### **Herramientas de Testing**
- **Email on Acid:** Testing de rendering
- **Litmus:** Preview en múltiples clientes
- **Mail-Tester:** Test de deliverability
- **MXToolbox:** Verificación DNS

### **Herramientas de Automatización**
- **Zapier:** Integraciones sin código
- **Make.com (Integromat):** Automatizaciones avanzadas
- **n8n:** Open source automation
- **Google Apps Script:** Automatizaciones personalizadas

### **Documentación de APIs**
- ActiveCampaign API: https://developers.activecampaign.com/
- Mailchimp API: https://mailchimp.com/developer/
- HubSpot API: https://developers.hubspot.com/
- Google Sheets API: https://developers.google.com/sheets/api

---

**Todas las integraciones están diseñadas para ser implementables paso a paso, empezando por lo básico.**




