## Módulos Listos (Make/Zapier) – Copiar/Pegar

IG Watch → Rate-Limit Guard → Classify → Variant Select → Send → Log

Make: Iterator + Sleep (Rate-Limit Guard)
- Config: desired_rate_per_hour = 8 (IG madura), 4 (IG nueva)
- Sleep: 30–60s (random) por item; si uso_hora >= cap → Sleep 120–180s

Router (Buckets)
- Opt-out: text ~ "(?i)(baja|stop|no molestar|remove|retire)"
- Interested: text ~ "(?i)(si|sí|reserva|agenda|book|link)"
- Objection: text ~ "(?i)(precio|cost|caro|budget)"
- Not now: text ~ "(?i)(luego|después|not now|próxima semana)"

Búsqueda CSV (Variantes)
- File: `dm_variants_master.csv`
- Filter: language == msg.lang AND niche == lead.niche AND cta_group ROTATE(C1..C4)

Módulo listo (Make): CSV > Search Rows
- Input: `file=DM_Variants_Master.csv`, `query=language={{msg.lang}} AND niche={{lead.niche}}`
- Post-proceso: seleccionar por `cta_group` alternando A/B con Data Store

Composer Mensaje
- Template: "{{hook}} {{benefit}} {{proof}} {{cta_text}}"
- Merge: first_name/company/industry + UTM de `UTM_Builder.md`

Módulo listo (Make): Text aggregator
- Input: campos `hook`, `benefit`, `proof`, `cta_text`
- Output: `message`

Send DM (Instagram)
- Input: message, thread_id
- Guard: length <= 220c si 2 líneas; <= 140c si ultra-corto

Módulo listo (Make): Instagram > Send Message
- Input: `thread_id={{lead.thread_id}}`, `message={{message}}`

Append Row (Google Sheets)
- Sheet: `KPI_Dashboard_Template_Enhanced.csv`
- Campos: date, offer, channel, variant_id, cta_group, sent=1

Módulo listo (Make): Google Sheets > Add row
- Campos: `timestamp`, `offer`, `channel=instagram`, `variant_id`, `cta_group`, `sent=1`

Zapier Filtros (equivalentes)
- Zap Filter Opt-out: Text Contains (baja|stop|remove)
- Storage by Zap: set/get `rate_usage:{account_id}:{hour}`

Paso listo (Zapier): Rate usage guard
- Storage by Zap: Get `rate_usage:{account_id}:{YYYYMMDDHH}` → default 0
- Filter: Continue if `< cap`
- Storage by Zap: Set incrementado con TTL 3600
Notas
- Usar `Reply_Classifier_TestSet.csv` para validar filtros.
- Ver `Retries_RateLimits_Playbook.md` para backoff y caps por canal.
 - Ver `Filters_Expressions_Library.md` para regex y fórmulas útiles.

