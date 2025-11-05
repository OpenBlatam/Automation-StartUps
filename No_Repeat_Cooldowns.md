## Reglas de No-Repetición y Cooldowns (per-contact)

### Objetivo
Evitar fatiga y spam: limitar frecuencia por contacto y no repetir CTA/texto.

### Reglas base (recomendadas)
- Envíos outbound: máx. 1 mensaje/24h y 3/7d por contacto.
- No repetir el mismo `cta_text` en 7 días.
- No repetir el mismo `variant_id` nunca en 7 días.
- Bumps: mínimo 24h entre bumps; 48h entre bump y cierre.

### Campos necesarios (CRM/Log)
- `last_sent_at`, `last_bump_at`, `last_variant_id`, `last_cta_text`, `messages_7d`.

### Lógica (Make/Zapier pseudo)
1) Fetch contacto → leer `last_sent_at`, `messages_7d`, `last_variant_id`, `last_cta_text`.
2) Si `now - last_sent_at < 24h` → STOP.
3) Si `messages_7d >= 3` → STOP.
4) Si `candidate.variant_id == last_variant_id` → rotar a siguiente.
5) Si `candidate.cta_text == last_cta_text` → rotar a siguiente.
6) Enviar → actualizar campos y sumar contador 7d.

### Fórmulas útiles (Sheets)
- Mensajes últimos 7 días: `=COUNTIF(FECHA_ENVIOS, ">=" & TODAY()-7)`
- Diferencia horas: `=24*(NOW()-last_sent_at)`

### Excepciones
- Si contacto responde/interactúa, se resetea cooldown de outbound y se prioriza respuesta humana.

