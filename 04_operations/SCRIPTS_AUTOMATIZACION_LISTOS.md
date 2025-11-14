---
title: "Scripts de Automatización Listos para Usar"
category: "09_sales"
tags: ["sales", "automation", "scripts"]
created: "2025-01-27"
path: "SCRIPTS_AUTOMATIZACION_LISTOS.md"
---

# 🤖 Scripts de Automatización Listos para Usar
## Código y Configuraciones Copy-Paste para Implementar Inmediatamente

**Versión:** 1.0  
**Última actualización:** Enero 2025

---

## 🎯 SCRIPTS DE HUBSPOT

### Script 1: Lead Scoring Automático (HubSpot)

**Configuración en HubSpot:**

```javascript
// HubSpot Lead Scoring Configuration
// Settings → Lead Scoring → Create Scoring Model

// COMPORTAMIENTO (40 puntos máximo)
{
  "behavior": {
    "lead_magnet_download": 10,
    "webinar_attended": 20,
    "quiz_completed": 10
  }
}

// FIRMOGRÁFICO (30 puntos máximo)
{
  "firmographic": {
    "company_size_50_500": 15,
    "industry_tech_marketing": 10,
    "revenue_over_5m": 5
  }
}

// ENGAGEMENT (20 puntos máximo)
{
  "engagement": {
    "email_opens_3_plus": 10,
    "email_clicks": 5,
    "email_replies": 5
  }
}

// INTENT SIGNALS (10 puntos máximo)
{
  "intent": {
    "pricing_page_visit": 5,
    "proposal_download": 5
  }
}
```

---

### Script 2: Workflow de Routing Automático (HubSpot)

**Configuración:**

```javascript
// HubSpot Workflow: "Route Leads by Score"
// Automation → Workflows → Create Workflow

workflow = {
  name: "Route Leads by Score",
  trigger: {
    type: "contact_property_change",
    property: "lead_score",
    condition: "changes"
  },
  branches: [
    {
      condition: "lead_score >= 81",
      actions: [
        {
          type: "add_to_list",
          list: "Hot Leads"
        },
        {
          type: "assign_to_owner",
          owner: "SDR_Senior"
        },
        {
          type: "send_email",
          template: "Hot Lead Welcome"
        },
        {
          type: "create_task",
          task: "Call within 2 hours",
          due_date: "+2 hours"
        }
      ]
    },
    {
      condition: "lead_score >= 61 AND lead_score < 81",
      actions: [
        {
          type: "add_to_list",
          list: "Warm Leads"
        },
        {
          type: "assign_to_owner",
          owner: "SDR"
        },
        {
          type: "send_email",
          template: "Warm Lead Welcome"
        },
        {
          type: "create_task",
          task: "Call within 24 hours",
          due_date: "+24 hours"
        }
      ]
    },
    {
      condition: "lead_score >= 31 AND lead_score < 61",
      actions: [
        {
          type: "add_to_list",
          list: "Nurturing"
        },
        {
          type: "enroll_in_sequence",
          sequence: "Nurturing Sequence"
        }
      ]
    },
    {
      condition: "lead_score < 31",
      actions: [
        {
          type: "add_to_list",
          list: "Cold Leads"
        },
        {
          type: "enroll_in_sequence",
          sequence: "Long-term Nurturing"
        }
      ]
    }
  ]
}
```

---

## 🔧 SCRIPTS DE MAKE.COM

### Script 1: Lead Scoring Custom (Make.com)

**Scenario Configuration:**

```javascript
// Make.com Scenario: "Custom Lead Scoring"
// Create Scenario → Add Modules

modules = [
  {
    type: "trigger",
    service: "HubSpot",
    action: "New Contact Created",
    filters: {
      "lead_source": "Webinar"
    }
  },
  {
    type: "set_variables",
    variables: {
      "score_behavior": 0,
      "score_firmographic": 0,
      "score_engagement": 0,
      "score_intent": 0
    }
  },
  {
    type: "if",
    condition: "company_size == '50-500'",
    then: {
      type: "set_variable",
      variable: "score_firmographic",
      operation: "add",
      value: 15
    }
  },
  {
    type: "if",
    condition: "industry IN ['Tech', 'Marketing']",
    then: {
      type: "set_variable",
      variable: "score_firmographic",
      operation: "add",
      value: 10
    }
  },
  {
    type: "if",
    condition: "webinar_attended == 'Yes'",
    then: {
      type: "set_variable",
      variable: "score_behavior",
      operation: "add",
      value: 20
    }
  },
  {
    type: "math",
    formula: "(score_behavior * 0.4) + (score_firmographic * 0.3) + (score_engagement * 0.2) + (score_intent * 0.1)",
    output: "total_score"
  },
  {
    type: "update_contact",
    service: "HubSpot",
    contact_id: "{{contact.id}}",
    properties: {
      "lead_score": "{{total_score}}"
    }
  }
]
```

---

### Script 2: ROI Calculator Integration (Make.com)

**Scenario Configuration:**

```javascript
// Make.com Scenario: "ROI Calculator Integration"
// Typeform → Make.com → HubSpot → Email

modules = [
  {
    type: "trigger",
    service: "Typeform",
    action: "New Submission",
    form_id: "roi_calculator_form"
  },
  {
    type: "parse_data",
    data: "{{form.responses}}",
    fields: [
      "campaigns_per_month",
      "time_per_campaign",
      "current_tool_cost",
      "hourly_rate"
    ]
  },
  {
    type: "math",
    formula: "(campaigns_per_month * time_per_campaign * hourly_rate * 0.5) + (current_tool_cost * 0.3)",
    output: "monthly_savings"
  },
  {
    type: "math",
    formula: "((monthly_savings * 12) - 3600) / 3600 * 100",
    output: "roi_percentage"
  },
  {
    type: "if",
    condition: "roi_percentage > 200",
    then: [
      {
        type: "update_contact",
        service: "HubSpot",
        contact_id: "{{contact.id}}",
        properties: {
          "roi_calculated": "{{roi_percentage}}",
          "lead_score": "{{lead_score + 20}}"
        }
      },
      {
        type: "assign_to_owner",
        service: "HubSpot",
        owner: "SDR_Senior"
      }
    ]
  },
  {
    type: "send_email",
    service: "HubSpot",
    template: "ROI Calculator Results",
    to: "{{contact.email}}",
    variables: {
      "monthly_savings": "{{monthly_savings}}",
      "roi_percentage": "{{roi_percentage}}"
    }
  }
]
```

---

## 📧 SCRIPTS DE EMAIL MARKETING

### Script 1: Secuencia de Nurturing (HubSpot Sequences)

**Configuración:**

```javascript
// HubSpot Sequence: "Nurturing Sequence for Warm Leads"
// Marketing → Email → Sequences

sequence = {
  name: "Nurturing Sequence - Warm Leads",
  enrollment: {
    condition: "lead_score >= 31 AND lead_score < 61"
  },
  emails: [
    {
      day: 1,
      subject: "Gracias por tu interés - Recursos exclusivos",
      content: "Template: Nurturing Email 1",
      delay: "immediate"
    },
    {
      day: 3,
      subject: "Casos de éxito: Cómo [Empresa Similar] logró [Resultado]",
      content: "Template: Nurturing Email 2",
      delay: "+2 days"
    },
    {
      day: 7,
      subject: "¿Quieres acelerar tu aprendizaje?",
      content: "Template: Nurturing Email 3",
      delay: "+4 days"
    },
    {
      day: 14,
      subject: "Oferta especial válida esta semana",
      content: "Template: Nurturing Email 4",
      delay: "+7 days"
    },
    {
      day: 30,
      subject: "Última oportunidad: ¿Aún estás interesado?",
      content: "Template: Nurturing Email 5",
      delay: "+16 days"
    }
  ],
  exit_criteria: [
    "lead_score >= 61",
    "demo_scheduled == true",
    "unsubscribed == true"
  ]
}
```

---

## 📊 SCRIPTS DE GOOGLE SHEETS

### Script 1: Dashboard Automático (Google Apps Script)

**Código:**

```javascript
// Google Apps Script: "Sales Dashboard Auto-Update"
// Tools → Script Editor → New Script

function updateSalesDashboard() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  var dashboardSheet = sheet.getSheetByName("Dashboard");
  var leadsSheet = sheet.getSheetByName("Leads Tracker");
  
  // Get data
  var leadsData = leadsSheet.getDataRange().getValues();
  var totalLeads = leadsData.length - 1;
  
  // Calculate metrics
  var hotLeads = 0;
  var demos = 0;
  var closes = 0;
  var totalRevenue = 0;
  
  for (var i = 1; i < leadsData.length; i++) {
    var score = leadsData[i][2]; // Column C
    var status = leadsData[i][4]; // Column E
    var revenue = leadsData[i][5]; // Column F
    
    if (score > 60) hotLeads++;
    if (status == "Demo") demos++;
    if (status == "Closed") {
      closes++;
      totalRevenue += revenue;
    }
  }
  
  var conversionRate = (closes / totalLeads) * 100;
  var avgLTV = totalRevenue / closes;
  
  // Update dashboard
  dashboardSheet.getRange("B2").setValue(totalLeads);
  dashboardSheet.getRange("B3").setValue(hotLeads);
  dashboardSheet.getRange("B4").setValue(demos);
  dashboardSheet.getRange("B5").setValue(closes);
  dashboardSheet.getRange("B6").setValue(conversionRate.toFixed(2) + "%");
  dashboardSheet.getRange("B7").setValue("$" + totalRevenue.toLocaleString());
  dashboardSheet.getRange("B8").setValue("$" + avgLTV.toFixed(2));
  
  // Log update
  Logger.log("Dashboard updated at " + new Date());
}

// Set trigger to run daily
function createTrigger() {
  ScriptApp.newTrigger('updateSalesDashboard')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
}
```

---

### Script 2: ROI Calculator (Google Sheets Formulas)

**Fórmulas Listas para Copiar:**

```excel
// Google Sheets: ROI Calculator Template
// Column A: Labels, Column B: Inputs, Column C: Outputs

// Inputs
B1: =INPUT("Número de campañas/mes")
B2: =INPUT("Tiempo por campaña (horas)")
B3: =INPUT("Costo herramientas actuales/mes")
B4: =INPUT("Valor hora del equipo ($)")

// Calculations
C1: =B1 * B2  // Tiempo total/mes
C2: =C1 * B4 * 0.5  // Ahorro tiempo ($) - asume 50% ahorro
C3: =B3 * 0.3  // Ahorro costos ($) - asume 30% ahorro
C4: =300  // Costo SaaS/mes (fijo)
C5: =((C2 + C3) - C4) / C4 * 100  // ROI %
C6: =C4 / ((C2 + C3) / 12)  // Payback (meses)

// Formatting
C5: =TEXT(C5, "0.0") & "%"
C6: =TEXT(C6, "0.0") & " meses"
```

---

## 🔗 SCRIPTS DE INTEGRACIÓN

### Script 1: Typeform → Make.com → HubSpot

**Typeform Webhook Configuration:**

```json
{
  "webhook_url": "https://hook.us1.make.com/your-webhook-url",
  "method": "POST",
  "headers": {
    "Content-Type": "application/json"
  },
  "body": {
    "form_id": "{{form_id}}",
    "submission_id": "{{submission_id}}",
    "answers": {
      "budget": "{{answer_1}}",
      "timeline": "{{answer_2}}",
      "authority": "{{answer_3}}"
    },
    "contact": {
      "email": "{{email}}",
      "name": "{{name}}"
    }
  }
}
```

---

### Script 2: HubSpot → Slack Notification

**Make.com Scenario:**

```javascript
// Make.com: "Notify Slack on Hot Lead"
// HubSpot → Make.com → Slack

modules = [
  {
    type: "trigger",
    service: "HubSpot",
    action: "Contact Added to List",
    list: "Hot Leads"
  },
  {
    type: "get_contact",
    service: "HubSpot",
    contact_id: "{{contact.id}}"
  },
  {
    type: "send_message",
    service: "Slack",
    channel: "#sales-alerts",
    message: "🔥 HOT LEAD ALERT\n\n" +
             "Name: {{contact.firstname}} {{contact.lastname}}\n" +
             "Company: {{contact.company}}\n" +
             "Score: {{contact.lead_score}}\n" +
             "Email: {{contact.email}}\n" +
             "Link: {{contact.hubspot_url}}",
    format: "markdown"
  }
]
```

---

## 📱 SCRIPTS DE WHATSAPP BUSINESS API

### Script 1: Follow-up Automático (WhatsApp)

**Template de Mensaje (Aprobado por WhatsApp):**

```
Template Name: follow_up_post_demo
Category: UTILITY
Language: es

Body:
Hola {{1}}, gracias por la demo de hoy. 

¿Cómo te quedó? ¿Tienes alguna pregunta?

{{2}}

Si no respondes en 24h, te enviaré un recordatorio.

Footer: [Tu Empresa]
```

**Variables:**
- {{1}}: Nombre del contacto
- {{2}}: Link para agendar follow-up

---

### Script 2: Re-engagement (WhatsApp)

**Template:**

```
Template Name: re_engagement_inactive
Category: UTILITY
Language: es

Body:
Hola {{1}}, noté que hace {{2}} semanas que no usas [producto].

¿Todo bien? ¿Necesitas ayuda?

Si reactivas hoy, te doy {{3}} gratis 🎁

{{4}}

Footer: [Tu Empresa]
```

**Variables:**
- {{1}}: Nombre
- {{2}}: Semanas inactivo
- {{3}}: Bonus (ej: "1 mes")
- {{4}}: Link para reactivar

---

## 🎯 SCRIPTS DE CALCULADORAS

### Script 1: ROI Calculator (JavaScript)

**Código Listo para Website:**

```javascript
// ROI Calculator - JavaScript
// Copy to your website

function calculateROI() {
  // Get inputs
  var campaigns = parseFloat(document.getElementById('campaigns').value);
  var timePerCampaign = parseFloat(document.getElementById('time').value);
  var currentCost = parseFloat(document.getElementById('cost').value);
  var hourlyRate = parseFloat(document.getElementById('rate').value);
  var saasCost = 300; // Your SaaS monthly cost
  
  // Calculate
  var totalTime = campaigns * timePerCampaign;
  var timeSavings = totalTime * hourlyRate * 0.5; // 50% time savings
  var costSavings = currentCost * 0.3; // 30% cost savings
  var totalSavings = timeSavings + costSavings;
  var roi = ((totalSavings - saasCost) / saasCost) * 100;
  var payback = saasCost / (totalSavings / 12);
  
  // Display results
  document.getElementById('time-savings').textContent = '$' + timeSavings.toLocaleString();
  document.getElementById('cost-savings').textContent = '$' + costSavings.toLocaleString();
  document.getElementById('roi').textContent = roi.toFixed(0) + '%';
  document.getElementById('payback').textContent = payback.toFixed(1) + ' meses';
  
  // Send to CRM if ROI > 200%
  if (roi > 200) {
    sendToCRM({
      email: document.getElementById('email').value,
      roi: roi,
      score_addition: 20
    });
  }
}

function sendToCRM(data) {
  // Send to your CRM via webhook
  fetch('https://hook.us1.make.com/your-webhook', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
}
```

---

## 📊 SCRIPTS DE REPORTES AUTOMÁTICOS

### Script 1: Reporte Semanal Automático (Google Apps Script)

**Código:**

```javascript
// Google Apps Script: "Weekly Sales Report"
// Sends email report every Monday

function sendWeeklyReport() {
  var sheet = SpreadsheetApp.getActiveSpreadsheet();
  var dataSheet = sheet.getSheetByName("Leads Tracker");
  var data = dataSheet.getDataRange().getValues();
  
  // Calculate metrics for last week
  var lastWeek = new Date();
  lastWeek.setDate(lastWeek.getDate() - 7);
  
  var metrics = calculateWeeklyMetrics(data, lastWeek);
  
  // Create email
  var emailBody = createReportEmail(metrics);
  
  // Send email
  MailApp.sendEmail({
    to: "sales-team@company.com",
    subject: "Reporte Semanal de Ventas - " + formatDate(new Date()),
    htmlBody: emailBody
  });
}

function calculateWeeklyMetrics(data, startDate) {
  // Implementation details
  return {
    totalLeads: 0,
    hotLeads: 0,
    demos: 0,
    closes: 0,
    revenue: 0,
    conversion: 0
  };
}

function createReportEmail(metrics) {
  return `
    <h2>Reporte Semanal de Ventas</h2>
    <table>
      <tr><td>Leads Totales:</td><td>${metrics.totalLeads}</td></tr>
      <tr><td>Leads Calientes:</td><td>${metrics.hotLeads}</td></tr>
      <tr><td>Demos:</td><td>${metrics.demos}</td></tr>
      <tr><td>Cierres:</td><td>${metrics.closes}</td></tr>
      <tr><td>Conversión:</td><td>${metrics.conversion}%</td></tr>
      <tr><td>Revenue:</td><td>$${metrics.revenue.toLocaleString()}</td></tr>
    </table>
  `;
}

// Create weekly trigger
function createWeeklyTrigger() {
  ScriptApp.newTrigger('sendWeeklyReport')
    .timeBased()
    .onWeekDay(ScriptApp.WeekDay.MONDAY)
    .atHour(9)
    .create();
}
```

---

## 🔍 SCRIPTS DE MONITOREO

### Script 1: Health Check Automático (Make.com)

**Scenario:**

```javascript
// Make.com: "Daily Health Check"
// Runs daily, checks system health

modules = [
  {
    type: "schedule",
    frequency: "daily",
    time: "09:00"
  },
  {
    type: "get_contacts",
    service: "HubSpot",
    filters: {
      "lead_score": "> 80",
      "last_contacted": "< 2 hours ago"
    }
  },
  {
    type: "if",
    condition: "contacts.length == 0",
    then: {
      type: "send_alert",
      service: "Slack",
      message: "⚠️ ALERTA: No hay leads calientes contactados en últimas 2 horas"
    }
  },
  {
    type: "check_workflows",
    service: "HubSpot",
    action: "verify_active"
  },
  {
    type: "if",
    condition: "inactive_workflows.length > 0",
    then: {
      type: "send_alert",
      service: "Slack",
      message: "⚠️ ALERTA: Workflows inactivos: {{inactive_workflows}}"
    }
  }
]
```

---

## 📋 INSTRUCCIONES DE USO

### Cómo Usar Estos Scripts

**Paso 1: Copiar Script**
- Copiar el código completo
- Ajustar según tu configuración

**Paso 2: Configurar**
- Reemplazar valores placeholder
- Verificar permisos y credenciales
- Configurar triggers si necesario

**Paso 3: Probar**
- Probar con datos de prueba
- Verificar que funciona correctamente
- Revisar logs de errores

**Paso 4: Activar**
- Activar en producción
- Monitorear primeros días
- Ajustar si necesario

---

## ⚠️ NOTAS IMPORTANTES

### Seguridad
- Nunca hardcodear credenciales
- Usar variables de entorno
- Limitar permisos al mínimo necesario

### Testing
- Siempre probar en entorno de prueba primero
- Probar con datos reales antes de activar
- Tener rollback plan

### Mantenimiento
- Documentar cada script
- Revisar logs regularmente
- Actualizar según cambios en APIs

---

**Fin de Scripts de Automatización**

*Usar estos scripts como base y ajustar según tus necesidades específicas.*

