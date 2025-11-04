# Dashboards de Grafana

Coloque aquí JSONs de dashboards. Puede montarlos con sidecar (kube-prometheus-stack) o como ConfigMaps.

## Dashboards Disponibles

- **kpi.json**: KPIs en tiempo real (ingresos, leads, pagos)
- **etl_improved.json**: Métricas del ETL mejorado (ratios, corridas, alertas)

El dashboard `etl_improved` requiere:
- Datasource PostgreSQL configurado con UID `KPIs-Postgres`
- Materialized views: `mv_etl_metrics_daily` y `mv_etl_alerts_daily` (ver `data/db/etl_metrics_views.sql`)
