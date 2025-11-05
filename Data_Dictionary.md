# 📚 Data Dictionary (CSV/Sheets)

## DM_Variants_Master.csv
- id: identificador único (DMx-xx)
- dm_type: curso | saas | bulk
- language: ES | EN | PT
- tone: tuteo | usted | vos | neutral
- niche: ecom | B2B | real_estate | educacion | general
- hook, benefit, proof, scarcity: bloques de copy
- cta, cta_keyword, link_base, utm_campaign
- merge_first_name, merge_company, merge_industry
- notes: contexto
- cta_group, cta_text, experiment_id: A/B/C y ensayo
- message_len, tone_formality, risk_level, optout_copy, variant_status, last_updated

## DM_Variants_Short.csv
- text: mensaje 140-180 chars
- cta: 1-2 palabras

## KPIs_Dashboard_Template.csv
- envios, respuestas, clicks, agendas, asistencias, ventas
- fórmulas derivadas: reply_rate, ctr, etc.

## CTA_Experimentos_Log.csv
- fecha, oferta, niche, idioma, tone, variant_id, cta_group, cta_text, métricas
