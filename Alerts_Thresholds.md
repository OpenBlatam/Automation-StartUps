## Umbrales de Alertas (WA/Email)

### Email
- Alerta: bounce_rate > 3% o spam_rate > 0.3%
- Crítico: bounce_rate > 5% o spam_rate > 0.5%
- Acción: reducir volumen 30%, revisar dominios (`Email_Domains_Verified.csv`), ajustar copy/CTA.

### WhatsApp
- Alerta: template_fail_rate > 1%
- Crítico: template_fail_rate > 2%
- Acción: usar plantillas approved (`WA_Templates_Index.csv`), pausar pending/rejected, revisar segmentación.

### Delivery general
- Alerta: delivery_rate < 92%
- Crítico: delivery_rate < 88%
- Acción: mover horarios, aplicar backoff/caps (`Retries_RateLimits_Playbook.md`), rotar canal.

### Notificaciones
- Medio: Email/Slack
- Frecuencia: daily a las 09:00 tz operativa
- Payload mínimo: fecha, canal, métrica, valor, umbral, recomendación

