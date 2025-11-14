# ⏱️ Scheduler Spec (Config.send_windows)

Entrada (Sheets `Config`):
- `timezone`: tz base (ej.: America/Mexico_City)
- `send_windows`: "09:00-11:00;14:00-16:00"

Lógica:
1) Detectar tz del lead (campo o inferencia por país/estado)
2) Convertir `send_windows` al tz del lead
3) Respetar días hábiles y feriados locales (si hay tabla)
4) Aplicar reglas por canal (ver `playbook_horarios_zonas.md`)
5) No enviar fuera de 08:00–18:00 local

Prioridad:
- Leads nuevos primero, luego reintentos pendientes
- Respetar límites de volumen por cuenta

Salida:
- Próximo `send_at` por lead + canal
- Motivo si no programado (ventana cerrada/feriado)

Integración:
- Usa `utm_builder_template.csv` para URLs
- Loggea eventos en CRM (ver `crm_field_mapping_template.csv`)

