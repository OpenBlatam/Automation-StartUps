# 📊 Queries SQL Optimizadas - Sistema de Ventas

Colección de vistas, funciones y queries optimizadas para análisis y reportes del sistema de ventas.

## 🎯 Vistas Disponibles

### 1. `v_sales_dashboard`
Vista completa del pipeline con toda la información necesaria para dashboards.

**Uso:**
```sql
SELECT * FROM v_sales_dashboard
WHERE assigned_to = 'vendedor@empresa.com'
ORDER BY priority DESC, expected_value DESC;
```

**Campos principales:**
- Información del lead (email, nombre, score)
- Estado del pipeline (stage, priority)
- Valor y probabilidad
- Tareas pendientes/vencidas
- Predicciones ML
- Días en pipeline

### 2. `v_leads_requires_attention`
Leads que requieren atención inmediata basado en múltiples criterios.

**Uso:**
```sql
SELECT * FROM v_leads_requires_attention
LIMIT 20;
```

**Criterios:**
- Alto valor sin contacto reciente (7+ días)
- Tareas vencidas
- Alto riesgo según ML (score > 0.7)
- Sin contacto en 14+ días

### 3. `v_sales_rep_performance`
Performance agregada de vendedores con métricas clave.

**Uso:**
```sql
SELECT * FROM v_sales_rep_performance
ORDER BY total_revenue DESC;
```

**Métricas:**
- Leads activos
- Won/Lost último mes
- Win rate
- Revenue total
- Tiempo promedio a cierre
- Tareas vencidas
- Pipeline ponderado

### 4. `v_sales_forecast`
Forecast mensual de ventas con diferentes niveles de confianza.

**Uso:**
```sql
SELECT * FROM v_sales_forecast
ORDER BY forecast_month DESC;
```

### 5. `v_conversion_funnel`
Análisis de embudo de conversión por etapa.

**Uso:**
```sql
SELECT * FROM v_conversion_funnel;
```

**Incluye:**
- Total de leads por etapa
- Desglose por prioridad
- Score promedio
- Valor total
- Tiempo promedio en etapa
- Conversión desde etapa anterior

## 🔧 Funciones Disponibles

### `get_top_opportunities(limit, min_value)`
Obtiene top oportunidades por valor esperado.

**Parámetros:**
- `limit`: Número de resultados (default: 20)
- `min_value`: Valor mínimo del deal (default: 0)

**Ejemplo:**
```sql
-- Top 20 oportunidades de $10k+
SELECT * FROM get_top_opportunities(20, 10000);
```

### `get_leads_at_risk(min_days, min_risk_score)`
Obtiene leads en riesgo basado en múltiples factores.

**Parámetros:**
- `min_days_without_contact`: Días sin contacto mínimo (default: 7)
- `min_risk_score`: Score de riesgo mínimo ML (default: 0.6)

**Ejemplo:**
```sql
-- Leads críticos (14+ días sin contacto o riesgo alto)
SELECT * FROM get_leads_at_risk(14, 0.7);
```

**Niveles de riesgo:**
- `CRITICAL`: ML risk score > 0.8
- `HIGH`: ML risk score > 0.6
- `MEDIUM`: 14+ días sin contacto
- `LOW`: Otros casos

### `update_rep_stats(rep_email)`
Actualiza estadísticas de un vendedor específico.

**Ejemplo:**
```sql
SELECT update_rep_stats('vendedor@empresa.com');
```

## 📈 Queries de Ejemplo

### Top 10 Leads por Valor Esperado
```sql
SELECT 
    email,
    stage,
    estimated_value,
    probability_pct,
    estimated_value * probability_pct / 100.0 AS expected_value,
    assigned_to
FROM sales_pipeline
WHERE stage NOT IN ('closed_won', 'closed_lost')
AND estimated_value IS NOT NULL
ORDER BY expected_value DESC
LIMIT 10;
```

### Leads Sin Seguimiento Reciente
```sql
SELECT 
    p.email,
    p.stage,
    p.estimated_value,
    EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
    COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks
FROM sales_pipeline p
LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
WHERE p.stage NOT IN ('closed_won', 'closed_lost')
AND (
    p.last_contact_at IS NULL
    OR p.last_contact_at <= NOW() - INTERVAL '7 days'
)
GROUP BY p.id
HAVING COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) > 0
ORDER BY days_since_contact DESC;
```

### Performance por Fuente
```sql
SELECT 
    source,
    COUNT(*) AS total_leads,
    COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
    ROUND(
        COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC / 
        NULLIF(COUNT(*), 0) * 100,
        2
    ) AS conversion_rate,
    AVG(score) AS avg_score,
    SUM(estimated_value) FILTER (WHERE stage = 'closed_won') AS total_revenue
FROM sales_pipeline
WHERE qualified_at >= NOW() - INTERVAL '90 days'
GROUP BY source
ORDER BY conversion_rate DESC;
```

### Tendencias de Scoring
```sql
SELECT 
    DATE_TRUNC('day', calculated_at) AS date,
    COUNT(*) AS score_updates,
    AVG(score) AS avg_score,
    AVG(score_change) AS avg_change,
    COUNT(*) FILTER (WHERE score_change > 0) AS increases,
    COUNT(*) FILTER (WHERE score_change < 0) AS decreases
FROM lead_score_history
WHERE calculated_at >= NOW() - INTERVAL '30 days'
GROUP BY DATE_TRUNC('day', calculated_at)
ORDER BY date DESC;
```

### Campañas Más Efectivas
```sql
SELECT 
    c.name,
    c.campaign_type,
    COUNT(DISTINCT ce.id) AS total_executions,
    COUNT(DISTINCT ce.lead_ext_id) AS unique_leads,
    COUNT(DISTINCT CASE WHEN ce.status = 'completed' THEN ce.id END) AS completed,
    COUNT(DISTINCT CASE WHEN p.stage = 'closed_won' THEN p.id END) AS won,
    ROUND(
        COUNT(DISTINCT CASE WHEN ce.status = 'completed' THEN ce.id END)::NUMERIC /
        NULLIF(COUNT(DISTINCT ce.id), 0) * 100,
        2
    ) AS completion_rate,
    ROUND(
        COUNT(DISTINCT CASE WHEN p.stage = 'closed_won' THEN p.id END)::NUMERIC /
        NULLIF(COUNT(DISTINCT ce.lead_ext_id), 0) * 100,
        2
    ) AS win_rate
FROM sales_campaigns c
LEFT JOIN sales_campaign_executions ce ON c.id = ce.campaign_id
LEFT JOIN sales_pipeline p ON ce.lead_ext_id = p.lead_ext_id
WHERE c.enabled = true
GROUP BY c.id, c.name, c.campaign_type
ORDER BY win_rate DESC, completion_rate DESC;
```

## ⚡ Optimizaciones

Las siguientes optimizaciones están incluidas:

1. **Índices compuestos** para búsquedas frecuentes
2. **Índices GIN** para búsquedas en metadata JSONB
3. **Vistas materializadas** para consultas complejas
4. **Funciones optimizadas** con parámetros configurables
5. **Triggers automáticos** para mantener consistencia

## 📊 Dashboard Completo

Para un dashboard completo, combina múltiples vistas:

```sql
-- Resumen ejecutivo
SELECT 
    (SELECT COUNT(*) FROM v_sales_dashboard) AS total_active_leads,
    (SELECT SUM(expected_value) FROM v_sales_dashboard) AS total_expected_value,
    (SELECT COUNT(*) FROM v_leads_requires_attention) AS leads_need_attention,
    (SELECT SUM(total_revenue) FROM v_sales_rep_performance) AS total_revenue_30d;
```

## 🔄 Actualización de Vistas Materializadas

```sql
-- Refrescar métricas
REFRESH MATERIALIZED VIEW mv_sales_metrics;

-- Ver últimas métricas
SELECT * FROM mv_sales_metrics
ORDER BY date DESC
LIMIT 30;
```

## 📚 Referencias

- Schema principal: `/data/db/sales_tracking_schema.sql`
- Queries optimizadas: `/data/db/sales_queries_optimized.sql`
- Documentación completa: `/data/db/README_SALES_AUTOMATION.md`


