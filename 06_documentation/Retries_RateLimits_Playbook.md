# 🔁 Reintentos y Rate Limits (Playbook)

## Backoff sugerido
- 1er fallo: 60s
- 2do fallo: 120s
- 3er fallo: 300s
- Luego: exponencial (x2) hasta 30 min

### Backoff por canal (orientativo)
- Instagram: start 45-60s; cap 30 min; jitter ±20%
- WhatsApp Business: start 30-45s; cap 15 min; respetar plantillas
- Email: start 120s; cap 60 min; SMTP 421/450 tratar como TEMP_UNAVAILABLE
- LinkedIn: start 90s; cap 30 min; pausas entre acciones 30-60s

## Códigos comunes
- RATE_LIMIT → reducir a 50% el ritmo, cambiar copy/CTA
- TEMP_UNAVAILABLE → reintentar con backoff
- INVALID_PAYLOAD → corregir y no reintentar

### Matriz rápida
- 429/420/RATE_LIMIT → backoff + rotación `cta_group` + alternar horario
- 5xx → backoff + reintentar hasta 3 veces
- 4xx (except 429/420) → no reintentar; corregir

## Rotación en picos
- CTA: alternar `cta_group` (A/B/C)
- Horarios: alternar franja (mañana/tarde)
- Canal: mover a WA/Email (si opt-in)

## Caps por canal (diario y horario)
- Instagram: nuevas 20-30/día; maduras 60-80/día; 6-8/hora; 30-60s entre envíos
- WhatsApp: 200-500/día según plantilla; 10-20/hora; 20-40s entre envíos
- Email: 30-50/día por inbox calentada; 2-5/min; 12-30s entre envíos
- LinkedIn: 20-40 invitaciones/día; 40-60 mensajes/día; 45-90s entre envíos

## Monitoreo
- Usar `Monitor_Salud_Campana.md`
- Alertar si 3 fallos consecutivos en 15 min

## Config JSON de backoff (ejemplo)
```
{
  "channel": "instagram",
  "base_delay_seconds": 60,
  "multiplier": 2.0,
  "max_delay_seconds": 1800,
  "jitter_ratio": 0.2,
  "max_retries": 5,
  "retry_on": ["RATE_LIMIT", "TEMP_UNAVAILABLE", "5xx"],
  "no_retry_on": ["INVALID_PAYLOAD", "4xx_except_429"],
  "rotate": {"cta_group": true, "hook": true, "time_block": true}
}
```

## Caps por sender (JSON listo para copiar)
```
{
  "senders": {
    "acct_ig_1": {"daily_cap": 70, "hourly_cap": 8, "sleep_seconds_between": [30,60]},
    "acct_ig_2": {"daily_cap": 70, "hourly_cap": 8, "sleep_seconds_between": [30,60]},
    "acct_ig_3": {"daily_cap": 60, "hourly_cap": 8, "sleep_seconds_between": [30,60]},
    "acct_ig_7": {"daily_cap": 60, "hourly_cap": 6, "sleep_seconds_between": [45,75]},
    "acct_ig_9": {"daily_cap": 60, "hourly_cap": 6, "sleep_seconds_between": [45,75]}
  },
  "fallback": {"daily_cap": 50, "hourly_cap": 6, "sleep_seconds_between": [30,60]}
}
```

## Reglas de parada
- Si reply_rate < 8% tras 100 envíos → cambiar hooks (ver `Hooks_Testing_Matrix.md`).
- Si optout > 2% en 24h → activar `Compliance_Consent_Templates.md` y reducir 30% volumen.
- Si bloqueos > 3 en 1h → pausar 60 min y rotar canal/horario.
