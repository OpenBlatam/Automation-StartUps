# 🛡️ Hardening Checklist (Antes de Escalar Volumen)

## Privacidad y Cumplimiento
- [ ] Base legal y consentimiento documentados (fuente y fecha)
- [ ] Lista de exclusión (do-not-contact) activa por canal
- [ ] Retención de datos brutos: ≤ 90 días; anonimización en logs
- [ ] Minimización: solo propiedades necesarias en CRM/flows
- [ ] Auditoría mensual de datos y accesos (roles/keys)

## Límites de Envío y Ventanas Horarias
- [ ] Rate limit por canal/día (p. ej. LI: 40, Email: 150, WA: 60)
- [ ] Ventanas locales por timezone (9–11 y 14–16)
- [ ] Backoff exponencial ante bloqueos/errores 429
- [ ] Circuit breaker si reply rate < umbral por 48h

## Logging y Trazabilidad
- [ ] Log de eventos mínimo: DM_SENT/REPLY/DEMO/ WON/LOST con variant, canal, hora local, score
- [ ] Correlación de IDs (leadId/dealId/eventId)
- [ ] Redacción de PII en logs (emails ofuscados)

## Monitorización y Alertas
- [ ] Alertas: tasa de rebote, reply < 10%, errores > 2%/h, 429 consecutivos
- [ ] Notificación a Slack (#sales-ops) con enlaces a CRM
- [ ] Dashboard de salud (últimas 24/72h) con tendencias

## Calidad y Marca
- [ ] QA muestreo 10% (25% tras cambios de prompt)
- [ ] Validación de estilo con `00_BRAND_STYLE_GUIDE.md`
- [ ] Aprobaciones para nuevas variantes antes de rollout > 20%

## Manejo de Fallos
- [ ] Reintentos con jitter; DLQ (dead-letter) para casos manuales
- [ ] Reprocesamiento seguro idempotente (no duplicar envíos)
- [ ] Fallback de canal (p. ej. LI→Email) tras 2 fallos

## Seguridad Operativa
- [ ] Rotación trimestral de API keys; `.env` cifrado/secret manager
- [ ] Accesos mínimos necesarios en CRM/Make
- [ ] Revisión de permisos de webhooks y scopes

## Go/No-Go para Escalar
- [ ] Reply ≥ 20%, DM→Demo ≥ 8%, errores < 2%/h por 2 semanas
- [ ] Sin alertas críticas 7 días
- [ ] Documentación actualizada (`00_README_INNOVACION.md`)
