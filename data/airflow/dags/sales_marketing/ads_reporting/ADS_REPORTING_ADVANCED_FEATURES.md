# Funcionalidades Avanzadas - Ads Reporting

## 🎯 Nuevas Funcionalidades

### 1. Monitoreo y Alertas (`monitoring.py`)

#### PerformanceMonitor
Monitor de rendimiento de extracciones:
- Registra historial de extracciones
- Detecta disminución en registros extraídos
- Detecta aumento en tiempo de ejecución
- Detecta errores frecuentes

**Ejemplo:**
```python
from ads_reporting.monitoring import monitor_extraction

alerts = monitor_extraction(
    platform="facebook",
    records_extracted=1000,
    duration_ms=5000,
    errors=0
)

# Alertas automáticas si detecta problemas
```

#### DataQualityMonitor
Monitor de calidad de datos:
- Verifica número mínimo de registros
- Detecta valores negativos
- Detecta CTR anormalmente alto
- Detecta falta de conversiones

**Ejemplo:**
```python
from ads_reporting.monitoring import DataQualityMonitor

monitor = DataQualityMonitor("facebook")
alerts = monitor.check_data_quality(data, expected_min_records=100)

# Genera alertas automáticas
```

#### AlertManager
Gestor centralizado de alertas:
- Envía alertas a Slack (configurable)
- Historial de alertas
- Agrupación de alertas
- Niveles: INFO, WARNING, ERROR, CRITICAL

**Ejemplo:**
```python
from ads_reporting.monitoring import AlertManager, AlertLevel, Alert

alert_manager = AlertManager(enable_notifications=True)

alert = Alert(
    level=AlertLevel.ERROR,
    title="Error en extracción",
    message="Fallo al conectar con API",
    platform="facebook"
)

alert_manager.send_alert(alert)
```

### 2. Batch Processing (`batch_processor.py`)

#### BatchProcessor
Procesador optimizado para grandes volúmenes:
- Chunking inteligente
- Procesamiento paralelo (threading/multiprocessing)
- Progress tracking
- Manejo de errores por chunk

**Ejemplo:**
```python
from ads_reporting.batch_processor import BatchProcessor

processor = BatchProcessor(
    chunk_size=100,
    max_workers=5,
    use_multiprocessing=False
)

def process_chunk(chunk):
    return [normalize(item) for item in chunk]

result = processor.process_in_chunks(data, process_chunk)

print(f"Procesados: {result.processed}/{result.total}")
print(f"Throughput: {result.throughput:.2f} items/s")
print(f"Success rate: {result.success_rate:.2f}%")
```

#### process_campaign_batch()
Función helper para procesar campañas:
```python
from ads_reporting.batch_processor import process_campaign_batch

result = process_campaign_batch(
    data,
    processor_func=lambda x: normalize(x),
    chunk_size=100,
    max_workers=5
)
```

### 3. Testing Helpers (`tests/test_helpers.py`)

#### Funciones Mock

**create_mock_campaign_data():**
```python
from ads_reporting.tests.test_helpers import create_mock_campaign_data

mock_data = create_mock_campaign_data(
    count=100,
    platform="facebook",
    date_start="2024-01-01",
    date_stop="2024-01-31"
)
```

**create_mock_audience_data():**
```python
from ads_reporting.tests.test_helpers import create_mock_audience_data

mock_audiences = create_mock_audience_data(
    audience_types=["custom", "lookalike", "interest"]
)
```

#### Clases Mock

**MockClient:**
```python
from ads_reporting.tests.test_helpers import MockClient

client = MockClient(platform="facebook")
# Usar en tests sin hacer requests reales
```

**MockStorage:**
```python
from ads_reporting.tests.test_helpers import MockStorage

storage = MockStorage()
storage.save_campaign_performance(data, "table")
saved = storage.get_saved_data("table")
```

### 4. Async Support (`async_support.py`)

Preparado para async/await (implementación futura):

```python
from ads_reporting.async_support import AsyncAdsClient

async with AsyncAdsClient(config) as client:
    data = await client.get(url, params)
```

## 📊 Casos de Uso Avanzados

### Caso 1: Pipeline Completo con Monitoreo

```python
from ads_reporting import (
    FacebookAdsClient, FacebookExtractor,
    monitor_extraction, DataQualityMonitor,
    get_alert_manager
)
import time

start_time = time.time()

# Extracción
with FacebookAdsClient(config) as client:
    extractor = FacebookExtractor(client)
    data = extractor.extract_campaign_performance(...)

duration_ms = (time.time() - start_time) * 1000

# Monitoreo automático
alerts = monitor_extraction(
    "facebook",
    len(data),
    duration_ms,
    errors=0
)

# Data quality monitoring
dq_monitor = DataQualityMonitor("facebook")
dq_alerts = dq_monitor.check_data_quality(data)

# Enviar todas las alertas
alert_manager = get_alert_manager()
alert_manager.send_batch_alerts(alerts + dq_alerts)
```

### Caso 2: Batch Processing de Grandes Volúmenes

```python
from ads_reporting.batch_processor import BatchProcessor
from ads_reporting.processors import CampaignProcessor

processor = CampaignProcessor()
batch_processor = BatchProcessor(
    chunk_size=500,
    max_workers=10,
    use_multiprocessing=True  # Para procesamiento CPU-intensivo
)

def process_chunk(chunk):
    normalized = processor.normalize(chunk)
    metrics = processor.calculate_metrics(normalized)
    return metrics

result = batch_processor.process_in_chunks(large_data, process_chunk)

print(f"Throughput: {result.throughput:.2f} items/s")
print(f"Success: {result.success_rate:.2f}%")
```

### Caso 3: Testing Completo

```python
import pytest
from ads_reporting.tests.test_helpers import (
    create_mock_campaign_data,
    MockClient,
    MockStorage
)
from ads_reporting.processors import CampaignProcessor
from ads_reporting.validators import validate_campaign_data

def test_campaign_processing():
    # Datos mock
    mock_data = create_mock_campaign_data(count=100)
    
    # Validación
    result = validate_campaign_data(mock_data)
    assert result.valid
    
    # Procesamiento
    processor = CampaignProcessor()
    normalized = processor.normalize(mock_data)
    metrics = processor.calculate_metrics(normalized)
    
    assert metrics.total_impressions > 0
    assert metrics.total_clicks > 0
    assert metrics.roas >= 0

def test_with_mock_client():
    client = MockClient(platform="facebook")
    # Usar cliente mock en tests
    assert client.get_base_url() == "https://api.mock-facebook.com"
    
    # Verificar llamadas
    assert client.get_call_count() == 0
    # ... hacer llamadas ...
    assert client.get_call_count() > 0
```

## 🔔 Sistema de Alertas

### Niveles de Alerta

- **INFO**: Información general
- **WARNING**: Advertencias que requieren atención
- **ERROR**: Errores que necesitan acción
- **CRITICAL**: Errores críticos que requieren acción inmediata

### Alertas Automáticas

El sistema genera alertas automáticamente para:
- Disminución significativa en registros extraídos
- Aumento en tiempo de ejecución
- Errores frecuentes en extracciones
- Valores negativos en datos
- CTR anormalmente alto
- Falta de conversiones

### Integración con Slack

```python
# En ads_reporting_utils.py
def notify_slack(message: str, level: str = "info"):
    # Implementación de notificación a Slack
    pass
```

## ⚡ Optimización de Performance

### Batch Processing

**Ventajas:**
- Procesamiento paralelo
- Mejor uso de recursos
- Manejo de memoria optimizado
- Progress tracking

**Cuando usar:**
- Grandes volúmenes de datos (>1000 registros)
- Procesamiento CPU-intensivo
- Necesidad de throughput alto

### Chunking Adaptativo

```python
processor = BatchProcessor(chunk_size=100)

# Calcular chunk size óptimo
optimal_size = processor.adaptive_chunk_size(
    total_items=10000,
    target_chunks=20
)
# Retorna tamaño calculado basado en total y chunks deseados
```

## 📈 Métricas Disponibles

### Performance Metrics
- `ads_reporting.{platform}.extraction.records`
- `ads_reporting.{platform}.extraction.duration_ms`
- `ads_reporting.{platform}.extraction.errors`

### Batch Metrics
- `ads_reporting.batch.total`
- `ads_reporting.batch.successful`
- `ads_reporting.batch.failed`
- `ads_reporting.batch.duration_ms`
- `ads_reporting.batch.throughput`

## ✅ Estado de Funcionalidades Avanzadas

- ✅ Monitoreo de rendimiento
- ✅ Detección de anomalías
- ✅ Sistema de alertas
- ✅ Batch processing optimizado
- ✅ Helpers para testing
- ✅ Async support (preparado)
- ⏳ Tests unitarios completos (pendiente)
- ⏳ Dashboard de métricas (pendiente)

## 📚 Documentación Relacionada

- `ADS_REPORTING_COMPLETE_GUIDE.md` - Guía completa
- `ADS_REPORTING_FINAL_IMPROVEMENTS.md` - Mejoras finales
- `ADS_REPORTING_README.md` - README principal

