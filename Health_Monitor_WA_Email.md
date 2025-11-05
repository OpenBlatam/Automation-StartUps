## Health Monitor (WhatsApp / Email)

### KPIs diarios (por canal)
- sends, delivered, bounces, spam_reports, template_failures (WA), hard_bounces (Email), soft_bounces (Email)
- delivery_rate = delivered / sends
- bounce_rate = (hard_bounces + soft_bounces) / sends (Email)
- spam_rate = spam_reports / sends (Email)
- template_fail_rate = template_failures / sends (WA)

### Umbrales sugeridos
- Email: bounce_rate > 3% (alerta), > 5% (crítico)
- Email: spam_rate > 0.3% (alerta), > 0.5% (crítico)
- WA: template_fail_rate > 1% (alerta), > 2% (crítico)
- Cualquier canal: delivery_rate < 92% (alerta), < 88% (crítico)

### Remediaciones rápidas
- Email bounces altos: pausar dominios no verificados, revisar `Email_Domains_Verified.csv`, reducir volumen 30%, limpiar lista.
- Email spam alto: ajustar copy/CTA, reducir cadencia, añadir opt-out claro; revisar warmup.
- WA template fails: usar plantillas `status=approved` en `WA_Templates_Index.csv`, solicitar revisión de plantillas rechazadas.
- Delivery bajo: mover franja horaria, rotar `cta_group`, reducir velocidad desde `Retries_RateLimits_Playbook.md`.

### Fuentes de datos
- Logs: `CTA_Experimentos_Log.csv` (sends) + proveedores (WA/Email) → consolidar en Sheets.
- Índices: `WA_Templates_Index.csv`, `Email_Domains_Verified.csv`.

### Fórmulas Sheets (ejemplo columnas: A:date, B:channel, C:sends, D:delivered, E:hard_bounces, F:soft_bounces, G:spam_reports, H:template_failures)
- delivery_rate (I): `=IFERROR(D2/C2,0)`
- bounce_rate (J): `=IF(B2="email", IFERROR((E2+F2)/C2,0), 0)`
- spam_rate (K): `=IF(B2="email", IFERROR(G2/C2,0), 0)`
- template_fail_rate (L): `=IF(B2="whatsapp", IFERROR(H2/C2,0), 0)`

### Alertas (QUERY ejemplo)
```
=QUERY(A1:L, "select A,B,I,J,K,L where I<0.92 or J>0.03 or K>0.003 or L>0.01", 1)
```

### Notificación
- Enviar email/Slack si hay filas en alertas; adjuntar CSV del día y acciones sugeridas.

