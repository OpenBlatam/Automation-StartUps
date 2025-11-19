# Características Avanzadas del Gmail Processor

## Resumen de Mejoras Adicionales

Este documento describe las mejoras avanzadas implementadas en el DAG `gmail_processor`:

### 1. Circuit Breaker Pattern ✅

**Implementación:**
- Circuit breaker que se abre después de `CB_FAILURE_THRESHOLD` fallos (default: 10)
- Auto-reset después de `CB_RESET_MINUTES` (default: 15 minutos)
- Previene cascading failures cuando Gmail API está inestable

**Funciones:**
- `_cb_is_open()`: Verifica si el circuit breaker está abierto
- `_cb_record_failure()`: Registra un fallo
- `_cb_reset()`: Resetea el circuit breaker

**Métricas:**
- `gmail_processor.circuit_breaker.failures`: Contador de fallos
- `gmail_processor.circuit_breaker.opened`: Cuando se abre
- `gmail_processor.circuit_breaker.reset`: Cuando se resetea
- `gmail_processor.circuit_breaker.blocked`: Ejecuciones bloqueadas

**Configuración:**
```bash
export GMAIL_CB_FAILURE_THRESHOLD=10  # Fallos antes de abrir
export GMAIL_CB_RESET_MINUTES=15      # Minutos para reset
```

### 2. Rate Limiting Inteligente ✅

**Implementación:**
- Manejo automático de rate limits (429, 503)
- Respeta header `Retry-After` de Gmail API
- Delay configurable entre requests

**Funciones:**
- `_handle_gmail_rate_limit()`: Maneja rate limiting con Retry-After

**Métricas:**
- `gmail_processor.rate_limit.hit`: Hits de rate limit
- `gmail_processor.rate_limit.wait_seconds`: Tiempo de espera

**Configuración:**
```bash
export GMAIL_RATE_LIMIT_DELAY=0.2     # Delay base (segundos)
export GMAIL_MAX_RETRY_AFTER=300      # Máximo Retry-After (5 min)
```

### 3. Health Check Proactivo ✅

**Implementación:**
- Health check opcional antes de procesar
- Verifica conectividad y autenticación
- No bloquea ejecución si falla (warning)

**Función:**
- `_perform_health_check()`: Verifica perfil de usuario

**Métricas:**
- `gmail_processor.health_check.success`: Health checks exitosos
- `gmail_processor.health_check.failed`: Health checks fallidos

**Configuración:**
```bash
export GMAIL_HEALTH_CHECK_ENABLED=true
```

### 4. Batch Processing ✅

**Implementación:**
- Procesa emails en batches configurable
- Delay entre batches para respetar rate limits
- Logging detallado por batch

**Configuración:**
```bash
export GMAIL_BATCH_SIZE=10    # Emails por batch
export GMAIL_BATCH_DELAY=1.0  # Segundos entre batches
```

**Métricas:**
- `gmail_processor.batch.completed`: Batches completados
- `gmail_processor.batch.processed`: Procesados por batch
- `gmail_processor.batch.failed`: Fallidos por batch
- `gmail_processor.total_batches`: Total de batches

### 5. Métricas Avanzadas ✅

**Métricas por Operación:**
- `gmail_processor.api.list_calls`: Llamadas a list
- `gmail_processor.api.get_calls`: Llamadas a get
- `gmail_processor.api.list_duration_seconds`: Duración de list
- `gmail_processor.api.get_duration_seconds`: Duración de get

**Métricas por Email:**
- `gmail_processor.email.processed`: Emails procesados
- `gmail_processor.email.log_success`: Logs exitosos
- `gmail_processor.email.log_failed`: Logs fallidos
- `gmail_processor.email.label_success`: Labels exitosos
- `gmail_processor.email.label_failed`: Labels fallidos
- `gmail_processor.email.error`: Errores por tipo

**Métricas de Alertas:**
- `gmail_processor.alert.low_success_rate`: Tasa de éxito < 80%
- `gmail_processor.alert.high_failure_rate`: Más del 30% fallidos

**Métricas de Circuit Breaker:**
- `gmail_processor.circuit_breaker.*`: Estado y eventos

### 6. Manejo de Errores Mejorado ✅

**Características:**
- Tracking detallado por tipo de error
- Registro en circuit breaker para errores críticos (5xx)
- Reset automático de circuit breaker en éxito
- Continuación del procesamiento aunque algunos emails fallen

**Tipos de Errores Trackeados:**
- `log_send_failed`: Fallo al enviar a log externo
- `label_add_failed`: Fallo al añadir etiqueta
- `HttpError`: Errores de API
- Tipos específicos de excepciones

### 7. Configuración por Variables de Entorno ✅

Todas las características avanzadas son configurables:

```bash
# Rate Limiting
GMAIL_RATE_LIMIT_DELAY=0.2
GMAIL_MAX_RETRY_AFTER=300

# Circuit Breaker
GMAIL_CB_FAILURE_THRESHOLD=10
GMAIL_CB_RESET_MINUTES=15

# Batch Processing
GMAIL_BATCH_SIZE=10
GMAIL_BATCH_DELAY=1.0

# Health Check
GMAIL_HEALTH_CHECK_ENABLED=true
```

### 8. Logging Estructurado Mejorado ✅

**Contexto en Todos los Logs:**
- `run_id`: ID de la ejecución del DAG
- `email_id`: ID del email procesado
- `email_index`: Índice en el batch
- `batch_num`: Número de batch
- `duration_seconds`: Duración de operaciones
- `error_type`: Tipo de error
- `subject`: Asunto del email (primeros 50 caracteres)

### 9. Idempotencia Mejorada ✅

- Tracking de emails procesados por `dag_run_id`
- Skip automático de emails ya procesados
- Métrica `gmail_processor.emails_skipped`

### 10. Performance Tracking ✅

**Métricas de Rendimiento:**
- Throughput: emails procesados por segundo
- Duración promedio por email
- Duración total del procesamiento
- Duración por operación API (list, get, modify)

## Ejemplos de Uso

### Verificar Circuit Breaker

```bash
# Ver estado
airflow variables get cb:failures:gmail_processor:gmail_processor

# Reset manual
airflow variables delete cb:failures:gmail_processor:gmail_processor
```

### Monitorear Métricas en Grafana

```promql
# Tasa de éxito
gmail_processor_success_rate

# Throughput
rate(gmail_processor_emails_processed[5m])

# Rate limit hits
rate(gmail_processor_rate_limit_hit[5m])

# Circuit breaker estado
gmail_processor_circuit_breaker_count
```

### Alertas Recomendadas

1. **Circuit Breaker Abierto:**
   ```
   gmail_processor_circuit_breaker_opened > 0
   ```

2. **Tasa de Éxito Baja:**
   ```
   gmail_processor_success_rate < 80
   ```

3. **Alta Tasa de Fallos:**
   ```
   rate(gmail_processor_emails_failed[5m]) > rate(gmail_processor_emails_processed[5m]) * 0.3
   ```

4. **Rate Limit Hits:**
   ```
   rate(gmail_processor_rate_limit_hit[1h]) > 10
   ```

## Beneficios

✅ **Resiliencia**: Circuit breaker previene cascading failures
✅ **Rate Limiting**: Respeta límites de Gmail API automáticamente
✅ **Observabilidad**: Métricas detalladas para debugging
✅ **Performance**: Batch processing optimiza throughput
✅ **Robustez**: Manejo de errores granular y continuidad
✅ **Configurabilidad**: Todo configurable vía variables de entorno

## Próximas Mejoras Potenciales

- [ ] Async processing con `httpx.AsyncClient`
- [ ] Backpressure basado en quota de Gmail API
- [ ] Retry inteligente con exponential backoff mejorado
- [ ] Cache de emails recientes para reducir API calls
- [ ] Procesamiento paralelo de batches (con límites)
- [ ] Dashboard de Grafana pre-configurado
- [ ] Alertas automáticas en Prometheus Alertmanager



