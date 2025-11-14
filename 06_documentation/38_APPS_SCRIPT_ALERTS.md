# 🔔 Google Apps Script — Slack/Email Alerts

## ✅ Requisitos
- Hoja `Config` con claves:
  - `reply_alert_threshold`
  - `no_show_alert_threshold`
- Hoja `Resumen` con métricas calculadas:
  - `reply_rate_dm_7d`
  - `no_show_rate_30d`
- Webhook Slack opcional

---

## 🧩 Variables de Configuración

```javascript
const CONFIG = {
  slackWebhook: 'https://hooks.slack.com/services/XXXX/XXXX/XXXX', // opcional
  emailRecipients: ['ops@tuempresa.com'],
  sheetNameResumen: 'Resumen',
  sheetNameConfig: 'Config'
};
```

---

## 🧠 Funciones Principales

```javascript
function getConfigMap_() {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(CONFIG.sheetNameConfig);
  const values = sh.getDataRange().getValues();
  const map = {};
  for (let i = 1; i < values.length; i++) {
    const [key, value] = values[i];
    if (key) map[key] = value;
  }
  return map;
}

function getResumenMap_() {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(CONFIG.sheetNameResumen);
  const values = sh.getDataRange().getValues();
  const map = {};
  for (let i = 1; i < values.length; i++) {
    const [metric, period, value] = values[i];
    if (metric) map[metric + '_' + (period || '')] = value;
  }
  return map;
}

function notifySlack_(text) {
  if (!CONFIG.slackWebhook) return;
  const payload = { text };
  UrlFetchApp.fetch(CONFIG.slackWebhook, {
    method: 'post',
    contentType: 'application/json',
    payload: JSON.stringify(payload)
  });
}

function notifyEmail_(subject, body) {
  if (!CONFIG.emailRecipients || CONFIG.emailRecipients.length === 0) return;
  GmailApp.sendEmail(CONFIG.emailRecipients.join(','), subject, body);
}

function checkAlerts() {
  const cfg = getConfigMap_();
  const res = getResumenMap_();

  const replyRate = Number(res['reply_rate_dm_7d_7d'] || res['reply_rate_dm_7d'] || 0);
  const replyThreshold = Number(cfg['reply_alert_threshold'] || 0.15);

  const noShow = Number(res['no_show_rate_30d_30d'] || res['no_show_rate_30d'] || 0);
  const noShowThreshold = Number(cfg['no_show_alert_threshold'] || 0.25);

  const messages = [];
  if (replyRate && replyRate < replyThreshold) {
    messages.push(`Alerta: Reply DM 7d (${(replyRate*100).toFixed(1)}%) < umbral (${(replyThreshold*100).toFixed(0)}%).`);
  }
  if (noShow && noShow > noShowThreshold) {
    messages.push(`Alerta: No-show 30d (${(noShow*100).toFixed(1)}%) > umbral (${(noShowThreshold*100).toFixed(0)}%).`);
  }

  if (messages.length) {
    const subject = 'Outreach Alerts — Google Sheets';
    const body = messages.join('\n');
    notifyEmail_(subject, body);
    notifySlack_(body);
  }
}
```

---

## ⏰ Programar (Triggers)
- En el editor de Apps Script → Triggers → `checkAlerts` → Every 6 hours (o diario)

### Referencia cruzada
- Para refrescar KPIs del Panel combinado automáticamente cada 6h (y menú en Sheets): `apps_script_panel_refresh.gs`

---

## 🧪 Prueba Rápida
- En `Resumen`, coloca temporalmente valores que disparen alertas
- Ejecuta `checkAlerts()` manualmente
- Verifica que lleguen email/Slack

---

**FIN DEL DOCUMENTO**



