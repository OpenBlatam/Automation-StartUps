# 📊 Looker Studio — Especificación de Dashboard (KPIs Plug‑and‑Play)

## Fuentes de Datos (sugeridas)
1) CRM DMs (Google Sheets/HubSpot export)
- Campos: sent_at, replied (bool), channel, variant, language, lead_score, timezone, contact_email

2) CRM Deals (Google Sheets/HubSpot export)
- Campos: stage, demo_booked_at, amount, currency, outcome_pricing, contact_email

3) Eventos/Logs (opcional)
- Campos: event_name, timestamp, error_code, channel

## Campos Calculados (DMs)
- date (Date): DATE(sent_at)
- reply_int (Number): CASE WHEN replied THEN 1 ELSE 0 END
- reply_rate (Percent): SUM(reply_int)/COUNT(contact_email)
- hour_local (Number): EXTRACT(HOUR FROM sent_at)
- score_bucket (Text): CASE WHEN lead_score>=8 THEN "8‑10" WHEN lead_score>=6 THEN "6‑7" ELSE "0‑5" END

## Campos Calculados (Deals)
- demo_booked_int: CASE WHEN stage="Demo Booked" THEN 1 ELSE 0 END
- won_int: CASE WHEN stage="Closed Won" THEN 1 ELSE 0 END

## Mezclas (Blends)
- DMs ↔ Deals por contact_email (Left join)
- Campos resultantes para funnel:
  - replies = SUM(DMs.reply_int)
  - demos = SUM(Deals.demo_booked_int)
  - wins = SUM(Deals.won_int)
  - dm_to_demo = demos / NULLIF(replies,0)
  - demo_to_win = wins / NULLIF(demos,0)

## Gráficos/Recomendados
1) Scorecard (arriba)
- Reply Rate (24h / 7d)
- DM→Demo (7d)
- Demo→Win (30d)
- MRR Nuevo (sum amount últimos 30d, stage=Closed Won)

2) Serie Temporal
- Reply rate por día (últimos 14/30)
- DMs enviados por día

3) Tabla por Variante
- Columnas: variant, channel, replies, reply_rate, demos, dm_to_demo, wins, demo_to_win
- Orden por reply_rate desc

4) Heatmap Horario
- Eje X: hour_local; Eje Y: día de la semana; Métrica: reply_rate

5) Filtro Lateral
- Fecha (rango)
- Canal (LinkedIn/Email/WhatsApp)
- Variante (A‑F)
- Idioma (es/en/pt)
- Score bucket (0‑5/6‑7/8‑10)

## Segmentaciones
- Industria (si está disponible): tabla comparativa por industria
- Outcome pricing: filtro booleano para cohortes

## Configuración
- Zona horaria: del negocio
- Moneda: estándar (USD/EUR) con conversión opcional
- Controles: comparativo vs periodo anterior

## Ingesta Rápida (sin API)
- Exporta de HubSpot/CRM a Google Sheets dos hojas: DMs y Deals
- Conecta ambas a Looker Studio y aplica esta especificación

## KPI Definitions (para tooltips)
- Reply Rate = replies / DMs
- DM→Demo = demos / replies
- Demo→Win = wins / demos

## Alertas Manuales (opcional)
- Marca en rojo Reply < 10% (últimos 7d)
- Marca en rojo errores > 2%/h si se ingiere Logs
