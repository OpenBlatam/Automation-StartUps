# Guía de Monitoreo

## Métricas Clave

### 1. Tasa de Éxito
```sql
SELECT 
    ROUND(
        COUNT(CASE WHEN status = 'completed' THEN 1 END)::numeric / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) as success_rate_percent
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '24 hours';
```

**Umbrales:**
- ✅ > 95%: Excelente
- ⚠️ 80-95%: Aceptable
- ❌ < 80%: Requiere atención

### 2. Throughput
```sql
SELECT 
    ROUND(
        SUM(total_records) / NULLIF(SUM(duration_seconds), 0),
        2
    ) as records_per_second
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '24 hours'
    AND duration_seconds > 0;
```

### 3. Latencia de APIs
```python
# Health check incluye latency_ms
connector = create_connector(...)
health = connector.health_check()
print(f"Latency: {health['latency_ms']}ms")
```

**Umbrales:**
- ✅ < 500ms: Excelente
- ⚠️ 500-2000ms: Aceptable
- ❌ > 2000ms: Requiere optimización

### 4. Errores por Categoría
```sql
SELECT 
    CASE 
        WHEN error_message LIKE '%timeout%' THEN 'Timeout'
        WHEN error_message LIKE '%auth%' THEN 'Authentication'
        WHEN error_message LIKE '%rate limit%' THEN 'Rate Limit'
        ELSE 'Other'
    END as error_category,
    COUNT(*) as count
FROM sync_records
WHERE status = 'failed'
    AND synced_at >= NOW() - INTERVAL '24 hours'
GROUP BY error_category;
```

## Alertas Recomendadas

### Alert 1: Tasa de Éxito Baja
```yaml
alert: SyncSuccessRateLow
expr: |
  SELECT 
    COUNT(CASE WHEN status = 'completed' THEN 1 END)::float / 
    NULLIF(COUNT(*), 0) * 100 < 80
  FROM sync_history
  WHERE started_at >= NOW() - INTERVAL '1 hour'
for: 15m
labels:
  severity: warning
annotations:
  summary: "Tasa de éxito de sincronización baja"
  description: "Tasa de éxito < 80% en la última hora"
```

### Alert 2: Sincronización Fallida
```yaml
alert: SyncFailed
expr: |
  SELECT COUNT(*) > 0
  FROM sync_history
  WHERE status = 'failed'
    AND started_at >= NOW() - INTERVAL '1 hour'
for: 5m
labels:
  severity: critical
```

### Alert 3: Circuit Breaker Abierto
```python
# Verificar en código
cb = framework._get_circuit_breaker("hubspot")
if cb.state == "open":
    send_alert("Circuit breaker abierto para HubSpot")
```

### Alert 4: Conflictos Pendientes
```sql
SELECT COUNT(*) > 10
FROM sync_conflicts
WHERE resolved_at IS NULL;
```

## Dashboard de Grafana

Importar el dashboard desde `grafana_dashboard.json`:

1. Acceder a Grafana
2. Dashboards → Import
3. Cargar `grafana_dashboard.json`
4. Configurar datasource de PostgreSQL

## Monitoreo en Tiempo Real

### Usando CLI
```bash
# Watch estadísticas cada 30 segundos
watch -n 30 'python3 cli.py stats --days 1'
```

### Script de monitoreo
```python
#!/usr/bin/env python3
import time
from data.integrations.utils import get_sync_stats

while True:
    stats = get_sync_stats(db_connection_string, days=1)
    print(f"Success rate: {stats.get('success_rate', 0)}%")
    print(f"Total syncs: {stats.get('total_syncs', 0)}")
    time.sleep(60)
```

## Logs Estructurados

El framework genera logs estructurados:

```json
{
  "timestamp": "2025-01-15T10:30:00Z",
  "level": "INFO",
  "sync_id": "sync_123",
  "source_type": "hubspot",
  "target_type": "quickbooks",
  "records_processed": 50,
  "successful": 48,
  "failed": 2
}
```

## Integración con Prometheus

Exponer métricas:

```python
from prometheus_client import Counter, Histogram, Gauge

sync_total = Counter('sync_total', 'Total syncs', ['source', 'target', 'status'])
sync_duration = Histogram('sync_duration_seconds', 'Sync duration')
sync_records = Gauge('sync_records_total', 'Total records synced', ['source', 'target'])
```

## Health Checks

### Endpoint de Health Check
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    framework = SyncFramework(...)
    
    # Verificar circuit breakers
    cb_status = {}
    for connector_type in ['hubspot', 'quickbooks']:
        cb = framework._get_circuit_breaker(connector_type)
        cb_status[connector_type] = cb.get_status()
    
    return jsonify({
        "status": "healthy" if all(cb['state'] == 'closed' for cb in cb_status.values()) else "degraded",
        "circuit_breakers": cb_status
    })
```

## Métricas de Negocio

### Registros Sincronizados por Día
```sql
SELECT 
    DATE_TRUNC('day', started_at) as day,
    SUM(total_records) as total_records
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '30 days'
GROUP BY day
ORDER BY day DESC;
```

### Tiempo Promedio de Sincronización
```sql
SELECT 
    source_type,
    target_type,
    AVG(duration_seconds) as avg_duration,
    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY duration_seconds) as p95_duration
FROM sync_history
WHERE started_at >= NOW() - INTERVAL '7 days'
GROUP BY source_type, target_type;
```

## Recomendaciones

1. **Monitorear diariamente:** Revisar dashboard cada día
2. **Alertas proactivas:** Configurar alertas antes de que sean críticas
3. **Logs centralizados:** Enviar logs a ELK/Loki
4. **Métricas de negocio:** Trackear KPIs relevantes
5. **Revisiones semanales:** Analizar tendencias y patrones


