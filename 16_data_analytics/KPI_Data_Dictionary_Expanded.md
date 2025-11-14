## KPI Data Dictionary (Expanded)

Campos mínimos (envíos)
- send_id: id único del envío
- timestamp_sent: ISO8601
- channel: instagram|whatsapp|email|linkedin
- variant_id: referencia a `dm_variants_master.csv`
- cta_group: C1|C2|C3|C4
- utm_campaign / utm_medium / utm_source
- risk_level: low|med|high

Interacciones
- replied (bool), reply_timestamp
- reply_bucket: interested|objection|not_now|optout|other (ver `Reply_Classifier_Regex.md`)
- clicked (bool), click_url, click_timestamp
- booked (bool), calendly_event_id, booked_timestamp
- attended (bool), show_timestamp
- converted (bool), deal_value

Derivados (cálculo)
- reply_rate = replied/sent
- click_rate = clicked/sent
- booked_rate = booked/sent
- show_rate = attended/booked
- win_rate = converted/sent
- revenue_per_send = sum(deal_value)/sent

Objetivos por oferta (referencia)
- Curso IA: reply ≥ 12%, booked ≥ 3%, show ≥ 70%, win ≥ 1.2%
- SaaS IA Mkt: reply ≥ 10%, booked ≥ 4%, show ≥ 65%, win ≥ 1.5%
- Bulk Docs: reply ≥ 9%, booked ≥ 3%, show ≥ 60%, win ≥ 1.0%


