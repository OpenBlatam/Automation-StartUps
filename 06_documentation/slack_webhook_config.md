# 🔔 Slack Webhook: Configuración Rápida

## 1) Crear Webhook
- Slack > App > Incoming Webhooks > activar y copiar URL
- Canal sugerido: #dm-alertas

## 2) Probar
```bash
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Test alert ✅"}' \
  https://hooks.slack.com/services/XXX/YYY/ZZZ
```

## 3) Formato recomendado
```json
{ "text": "ALERTA: Reply 7d < 15% | Cuenta: MX-SaaS | Acción: pausar y revisar" }
```

## 4) Seguridad
- Guardar URL fuera del repositorio (Secret Manager / Sheet Protegida)
- Rotar periódicamente y limitar a canal específico

Integra con `38_APPS_SCRIPT_ALERTS.md` usando `UrlFetchApp.fetch`.

