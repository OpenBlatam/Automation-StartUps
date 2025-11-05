# Dashboard KPIs – Guía rápida

Definiciones (por producto y etapa)
- CVR Lead Magnet = leads_capturados / visitas_landing
- Asistencia Webinar = asistentes / registrados
- Demo Rate = demos_agendadas / leads_calificados
- CR Tripwire = compras_tripwire / leads_LM
- CR Core = compras_core / leads_LM
- CR High‑Ticket = cierres_HT / invitaciones_HT
- ROAS (SaaS) = ingresos_atr / gasto_ads
- Payback (meses) = CAC / margen_mensual

Umbrales sugeridos
- CVR LM ≥ 30–40%
- Asistencia webinar ≥ 30–35%
- Demo rate ≥ 12–20%
- CR Tripwire ≥ 5–10%
- CR Core ≥ 2–4%
- CR High‑Ticket ≥ 15–30%
- Payback ≤ 2 meses (SaaS/Servicios)

Segmentos útiles
- Fuente (utm_source/medium/campaign)
- Producto (curso/saas/bulk) y escalón (LM/TRP/CORE/HT)
- Región/idioma
- Fecha (cohortes semanales/mensuales)

Gráficas recomendadas
- Funnel por producto (LM→TRP→CORE→HT)
- Cohortes 30/60/90 días (retención/ingresos)
- Heatmap por variante (open/CTR/CR)
- ROAS por plataforma (Meta/Google/TikTok)

Queries base (pseudo‑SQL)
- Compras por escalón:
  SELECT producto, escalon, COUNT(*) compras, SUM(monto) ingresos FROM Compras JOIN Ofertas USING(oferta_id) GROUP BY 1,2;
- Funnel LM→TRP→CORE:
  WITH lm AS (...), trp AS (...), core AS (...) SELECT ...
- ROAS:
  SELECT plataforma, SUM(ingresos)/NULLIF(SUM(gasto),0) roas FROM Ads GROUP BY 1;

Alertas
- Si asistencia < 25% → activar warming extra
- Si no‑show demo > 20% → doble reminder SMS/WA
- Si CR Tripwire < 4% → test precio/valor

