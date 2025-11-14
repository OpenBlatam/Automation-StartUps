# 📊 Dashboard Template (Airtable/Notion)

## Tablas y Campos

### 1) Contacts
- email (Primary)
- first_name (Single line)
- last_name (Single line)
- company (Single line)
- industry (Single select)
- channel (Single select: LinkedIn, Email, WhatsApp)
- language (Single select: es, en, pt)
- dm_variant (Single select: A, B, C, D, E, F)
- lead_score (Number 0-10)
- best_send_hour (Number 0-23)
- primary_objection (Single select: timing, presupuesto, competidor, tono, otros)
- last_dm_sent_at (Date)

### 2) DMs
- dm_id (Primary, Autonumber)
- email (Link to Contacts)
- channel (Single select)
- variant (Single select)
- sent_at (Date)
- opened (Checkbox)
- replied (Checkbox)
- reply_at (Date)
- time_to_reply_min (Formula: DATETIME_DIFF({reply_at},{sent_at},'minutes'))
- followup_count (Number)

### 3) Deals
- deal_name (Primary)
- associated_email (Link to Contacts)
- amount (Currency)
- currency (Single select)
- stage (Single select: Lead, DM Sent, Demo Booked, Proposal Sent, Closed Won, Closed Lost)
- demo_booked_at (Date)
- outcome_pricing (Checkbox)
- package_tier (Single select: Starter, Growth, Scale, Enterprise)
- mrr_delta_expected (Currency)
- kpi_baseline (Number)
- kpi_target (Number)

### 4) Metrics (Views/Reports)
- Reply Rate (Rollup sobre DMs: AVG({replied}) )
- DM→Demo (Rollup: COUNT(demos) / COUNT(replies))
- Demo→Win (Rollup: COUNT(Closed Won) / COUNT(Demo Booked))
- ROI por Variante (Fórmula externa BI con inputs: amount, tiempo, costo hora)

## Vistas Sugeridas
- DMs Semana (filtro por fecha)
- Variantes Ganadoras (orden por reply rate desc)
- Horarios Top (agrupado por best_send_hour)
- Pipeline (Kanban por stage)

## Notion (Propiedades Equivalentes)
- Usar databases con las mismas propiedades y relations (Contacts ↔ DMs ↔ Deals).
- Crear vistas: Board por stage, Calendar por sent_at, Table por variantes.

## Métricas Semanales (Checklist)
- [ ] DMs enviados
- [ ] Reply rate
- [ ] DM→Demo
- [ ] Demo→Win
- [ ] Variantes top 3
- [ ] Horarios top 2 por industria

