# Mejoras V8 - Sistemas Inteligentes Avanzados

## 📋 Resumen

Nuevas funcionalidades inteligentes agregadas al sistema de sincronización Stripe-QuickBooks: alertas adaptativas, auto-scaling, detección de anomalías, y más.

## 🚀 Nuevas Funcionalidades V8

### 1. Sistema de Alertas Inteligentes

**Clase**: `IntelligentAlertSystem`

- Alertas con thresholds adaptativos
- Cooldown automático para evitar spam
- Múltiples niveles de severidad (info, warning, critical)
- Historial completo de alertas

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_alert_system

# Verificar y alertar automáticamente
_global_alert_system.check_and_alert(
    metric_name="error_rate",
    value=15.5,  # 15.5% de errores
    severity="critical"
)

# Ajustar threshold dinámicamente
_global_alert_system.adjust_threshold("error_rate", 12.0)
```

### 2. Auto-Scaling de Workers

**Clase**: `AutoScalingWorkerManager`

- Ajuste automático de workers basado en carga
- Cálculo inteligente basado en throughput objetivo
- Ajuste dinámico según performance histórico

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_worker_manager

# Calcular workers óptimos
optimal_workers = _global_worker_manager.calculate_optimal_workers(
    queue_size=500,
    avg_processing_time=0.5,  # 0.5 segundos por item
    target_throughput=10.0  # 10 items/segundo objetivo
)

# Registrar performance para mejorar cálculos futuros
_global_worker_manager.record_performance(
    items_processed=100,
    duration=10.0,
    workers_used=5
)
```

### 3. Detección de Anomalías

**Clase**: `AnomalyDetector`

- Detección automática usando Z-score
- Tracking histórico de métricas
- Identificación de valores anómalos

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_anomaly_detector

# Detectar anomalía en una métrica
anomaly = _global_anomaly_detector.detect_anomaly(
    metric_name="sync_duration",
    value=8000.0,  # 8 segundos
    window_size=100
)

if anomaly:
    print(f"Anomalía detectada! Z-score: {anomaly['z_score']:.2f}")

# Obtener estadísticas de métrica
stats = _global_anomaly_detector.get_metric_stats("sync_duration")
print(f"Media: {stats['mean']:.2f}, Std Dev: {stats['std_dev']:.2f}")
```

### 4. Batch Sizing Adaptativo

**Clase**: `AdaptiveBatchSizer`

- Ajuste automático del tamaño de batch
- Optimización basada en success rate, duración, y error rate
- Ajuste dinámico según performance

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_batch_sizer

# Calcular tamaño óptimo después de procesar batch
optimal_size = _global_batch_sizer.calculate_optimal_size(
    success_rate=97.5,  # 97.5% éxito
    avg_duration=800.0,  # 800ms promedio
    error_rate=2.5  # 2.5% errores
)

print(f"Tamaño óptimo de batch: {optimal_size}")
```

### 5. Circuit Breaker Mejorado

**Clase**: `EnhancedCircuitBreaker`

- Circuit breaker con estados: closed, open, half_open
- Recovery automático con health checks
- Thresholds configurables

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_circuit_breaker

# Usar circuit breaker para proteger llamadas
try:
    result = _global_circuit_breaker.call(
        sync_stripe_product_to_quickbooks,
        stripe_product_id="prod_123",
        nombre_producto="Test",
        precio=99.99
    )
except Exception as e:
    print(f"Circuit breaker bloqueó la llamada: {e}")

# Verificar estado
health = _global_circuit_breaker.health_check()
print(f"Estado: {health['state']}, Healthy: {health['is_healthy']}")
```

### 6. Compresión de Datos para Batches

**Funciones**: `compress_batch_data()`, `decompress_batch_data()`

- Compresión gzip para reducir uso de memoria
- Útil para batches grandes
- Fallback a JSON sin comprimir si gzip no está disponible

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    compress_batch_data,
    decompress_batch_data
)

# Comprimir batch grande
products = [...]  # Lista grande de productos
compressed = compress_batch_data(products)
print(f"Original: {len(str(products))} bytes, Comprimido: {len(compressed)} bytes")

# Descomprimir
decompressed = decompress_batch_data(compressed)
```

### 7. Dashboard de Métricas en Tiempo Real

**Clase**: `MetricsDashboard`

- Dashboard centralizado de métricas
- Integración con todos los sistemas
- Datos agregados para visualización

**Ejemplo de uso**:
```python
from stripe_product_to_quickbooks_item_v6_improvements import _global_dashboard

# Actualizar métricas
_global_dashboard.update_metric("total_synced", 1000)
_global_dashboard.update_metric("error_rate", 2.5)

# Obtener datos completos para dashboard
dashboard_data = _global_dashboard.get_dashboard_data()
print(f"Métricas: {dashboard_data['metrics']}")
print(f"Alertas activas: {dashboard_data['alert_system']['active_alerts']}")
print(f"Anomalías: {len(dashboard_data['anomalies'])}")
```

## 📊 Casos de Uso Integrados

### Sistema Completo con Todas las Mejoras

```python
from stripe_product_to_quickbooks_item_v6_improvements import (
    _global_alert_system,
    _global_worker_manager,
    _global_anomaly_detector,
    _global_batch_sizer,
    _global_circuit_breaker,
    _global_dashboard,
    sync_stripe_products_batch
)

def sync_with_intelligent_features(products):
    # 1. Calcular workers óptimos
    optimal_workers = _global_worker_manager.calculate_optimal_workers(
        queue_size=len(products),
        avg_processing_time=0.5
    )
    
    # 2. Calcular tamaño de batch óptimo
    batch_size = _global_batch_sizer.current_size
    
    # 3. Procesar con circuit breaker
    try:
        result = _global_circuit_breaker.call(
            sync_stripe_products_batch,
            products=products,
            max_workers=optimal_workers
        )
        
        # 4. Detectar anomalías en duración
        duration_anomaly = _global_anomaly_detector.detect_anomaly(
            "batch_duration",
            result.duration_ms
        )
        
        # 5. Calcular error rate y alertar si es necesario
        error_rate = (result.failed / result.total * 100) if result.total > 0 else 0
        _global_alert_system.check_and_alert(
            "error_rate",
            error_rate,
            severity="critical" if error_rate > 10 else "warning"
        )
        
        # 6. Actualizar dashboard
        _global_dashboard.update_metric("total_synced", result.total)
        _global_dashboard.update_metric("success_rate", result.success_rate)
        _global_dashboard.update_metric("error_rate", error_rate)
        
        # 7. Ajustar batch size para próxima vez
        _global_batch_sizer.calculate_optimal_size(
            success_rate=result.success_rate,
            avg_duration=result.duration_ms,
            error_rate=error_rate
        )
        
        return result
        
    except Exception as e:
        _global_alert_system.check_and_alert(
            "consecutive_failures",
            1,
            severity="critical"
        )
        raise
```

## 🎯 Beneficios Clave

### Auto-Optimización
- **Workers**: Se ajustan automáticamente según carga
- **Batch Size**: Se optimiza según performance
- **Thresholds**: Se ajustan dinámicamente

### Protección
- **Circuit Breaker**: Previene fallos en cascada
- **Anomaly Detection**: Identifica problemas temprano
- **Alertas**: Notifican antes de que sea crítico

### Eficiencia
- **Compresión**: Reduce uso de memoria en batches grandes
- **Dashboard**: Visibilidad completa del sistema
- **Tracking**: Mejora continua basada en datos

## 📈 Métricas Disponibles

- **Error Rate**: Tasa de errores (%)
- **Duration P95**: Percentil 95 de duración (ms)
- **Cache Miss Rate**: Tasa de misses del cache (%)
- **Consecutive Failures**: Fallos consecutivos
- **Throughput**: Items procesados por segundo
- **Z-Score**: Score de anomalía

## 🔧 Configuración

### Thresholds por Defecto

```python
{
    "error_rate": 10.0,  # 10% de errores
    "duration_p95": 5000.0,  # 5 segundos
    "cache_miss_rate": 50.0,  # 50% miss rate
    "consecutive_failures": 5.0
}
```

### Ajustar Thresholds

```python
_global_alert_system.adjust_threshold("error_rate", 15.0)
_global_alert_system.adjust_threshold("duration_p95", 3000.0)
```

## 🚀 Integración con Código Existente

Todas las funcionalidades son opcionales y no afectan el código existente. Se pueden integrar gradualmente:

1. **Fase 1**: Activar alertas y detección de anomalías
2. **Fase 2**: Implementar auto-scaling de workers
3. **Fase 3**: Activar batch sizing adaptativo
4. **Fase 4**: Usar circuit breaker para protección
5. **Fase 5**: Activar dashboard completo

## 📝 Resumen de Todas las Mejoras

### V6.0 + V6.1: Funcionalidades Base (16)
- Event Sourcing, Idempotency, Observability, Webhooks, etc.

### V7: Performance (5)
- Profiling, Cache Stats, Batch Optimizado, etc.

### V8: Sistemas Inteligentes (7)
- ✅ Alertas Inteligentes
- ✅ Auto-Scaling Workers
- ✅ Detección de Anomalías
- ✅ Batch Sizing Adaptativo
- ✅ Circuit Breaker Mejorado
- ✅ Compresión de Datos
- ✅ Dashboard de Métricas

**Total: 28 funcionalidades avanzadas**

## 🎯 Próximos Pasos

1. **Monitorear**: Usar dashboard para ver estado del sistema
2. **Ajustar**: Configurar thresholds según necesidades
3. **Optimizar**: Dejar que auto-scaling y batch sizing trabajen
4. **Alertar**: Configurar integración con Slack/Email
5. **Iterar**: Ajustar parámetros basado en métricas

