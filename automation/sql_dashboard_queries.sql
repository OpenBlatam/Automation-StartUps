-- Leads capturados por fuente/campaña
SELECT utm_source, utm_campaign, COUNT(*) leads
FROM Leads
GROUP BY 1,2
ORDER BY leads DESC;

-- Funnel LM -> Tripwire -> Core -> High-Ticket (conteos)
WITH lm AS (
  SELECT DISTINCT email FROM Leads
), trp AS (
  SELECT c.lead_id FROM Compras c JOIN Ofertas o ON c.oferta_id=o.id WHERE o.escalon='tripwire'
), core AS (
  SELECT c.lead_id FROM Compras c JOIN Ofertas o ON c.oferta_id=o.id WHERE o.escalon='core'
), ht AS (
  SELECT c.lead_id FROM Compras c JOIN Ofertas o ON c.oferta_id=o.id WHERE o.escalon='high_ticket'
)
SELECT
  (SELECT COUNT(*) FROM lm) AS lm,
  (SELECT COUNT(DISTINCT lead_id) FROM trp) AS tripwire,
  (SELECT COUNT(DISTINCT lead_id) FROM core) AS core,
  (SELECT COUNT(DISTINCT lead_id) FROM ht) AS high_ticket;

-- Asistencia a webinar (por evento)
SELECT w.id webinar_id, w.titulo, w.fecha,
       w.registrados, w.asistentes,
       SAFE_DIVIDE(w.asistentes, NULLIF(w.registrados,0)) AS asistencia_rate
FROM Webinars w
ORDER BY w.fecha DESC;

-- ROAS por plataforma (si tienes tabla Ads)
SELECT plataforma, SUM(ingresos) / NULLIF(SUM(gasto),0) AS roas
FROM Ads
GROUP BY 1
ORDER BY roas DESC;

-- No-show demo
SELECT COUNTIF(resultado='no_show')/NULLIF(COUNT(*),0) AS no_show_rate
FROM Demos;
