# Guía de Troubleshooting

## Problemas Comunes y Soluciones

### 1. Error: "Circuit breaker abierto"

**Síntoma:**
```
ValueError: Circuit breaker abierto para source: hubspot
```

**Causa:** Demasiados fallos consecutivos han activado el circuit breaker.

**Solución:**
1. Verificar logs para identificar el problema raíz
2. Verificar credenciales y conectividad
3. Esperar el timeout del circuit breaker (por defecto 60 segundos)
4. O resetear manualmente:
   ```python
   framework = SyncFramework(...)
   cb = framework._get_circuit_breaker("hubspot")
   cb.record_success()  # Resetear
   ```

### 2. Error: "Source/Target connector no saludable"

**Síntoma:**
```
ValueError: Source connector no saludable: {'status': 'unhealthy', 'error': '...'}
```

**Causa:** Problemas de conectividad o credenciales inválidas.

**Solución:**
1. Verificar credenciales:
   ```bash
   echo $HUBSPOT_API_TOKEN
   echo $QUICKBOOKS_ACCESS_TOKEN
   ```
2. Verificar conectividad de red
3. Probar health check manualmente:
   ```python
   from data.integrations.connectors import create_connector
   connector = create_connector("hubspot", {"api_token": "..."})
   health = connector.health_check()
   print(health)
   ```

### 3. Sincronización lenta

**Síntoma:** Sincronizaciones toman mucho tiempo.

**Soluciones:**
1. Reducir batch_size:
   ```python
   config = SyncConfig(..., batch_size=25)  # En lugar de 50
   ```
2. Aumentar caché TTL:
   ```python
   config = SyncConfig(..., cache_ttl_seconds=600)  # 10 minutos
   ```
3. Usar sincronización incremental:
   ```python
   config = SyncConfig(
       ...,
       filters={"createdAfter": "2025-01-01T00:00:00Z"}
   )
   ```

### 4. Conflictos frecuentes

**Síntoma:** Muchos registros marcados como "conflicted".

**Soluciones:**
1. Revisar estrategia de resolución:
   ```python
   config = SyncConfig(..., conflict_resolution="latest")
   ```
2. Sincronizar en una sola dirección:
   ```python
   config = SyncConfig(..., direction=SyncDirection.SOURCE_TO_TARGET)
   ```
3. Revisar conflictos pendientes:
   ```bash
   python3 cli.py conflicts
   ```

### 5. Error: "Tipo de conector desconocido"

**Síntoma:**
```
ValueError: Tipo de conector desconocido: xyz
```

**Solución:**
Verificar que el tipo de conector sea uno de los soportados:
- `hubspot`
- `quickbooks`
- `google_sheets`
- `database`
- `postgresql`
- `mysql`
- `salesforce`

### 6. Error de autenticación en Google Sheets

**Síntoma:**
```
Error conectando a Google Sheets: 403 Forbidden
```

**Solución:**
1. Verificar que el service account tenga acceso al spreadsheet
2. Compartir el spreadsheet con el email del service account
3. Verificar formato del JSON de credenciales

### 7. Timeouts en QuickBooks

**Síntoma:**
```
requests.exceptions.Timeout
```

**Solución:**
1. Verificar que QuickBooks API esté disponible
2. Reducir batch_size para evitar rate limits
3. Implementar retry logic más agresivo

### 8. Datos no se sincronizan

**Síntoma:** Sincronización completa pero sin cambios en destino.

**Diagnóstico:**
1. Verificar filtros:
   ```python
   config = SyncConfig(..., filters={"object_type": "contacts"})
   ```
2. Verificar que haya datos en source:
   ```python
   connector = create_connector(...)
   records = connector.read_records(filters={...})
   print(f"Encontrados {len(records)} registros")
   ```
3. Revisar logs de errores:
   ```bash
   python3 cli.py stats --days 1
   ```

### 9. Checksums inconsistentes

**Síntoma:** Mismos datos pero diferentes checksums.

**Causa:** Orden de campos o formato diferente.

**Solución:**
El framework calcula checksums automáticamente. Si hay problemas:
1. Verificar que los datos sean realmente diferentes
2. Normalizar datos antes de sincronizar usando transformaciones

### 10. Base de datos no inicializada

**Síntoma:**
```
relation "sync_history" does not exist
```

**Solución:**
Ejecutar el esquema SQL:
```bash
psql $SYNC_DB_CONNECTION_STRING < sync_schema.sql
```

O usar el script de setup:
```bash
./setup.sh
```

## Comandos Útiles de Diagnóstico

### Ver estadísticas recientes
```bash
python3 cli.py stats --days 1
```

### Ver conflictos pendientes
```bash
python3 cli.py conflicts --limit 50
```

### Exportar reporte de errores
```bash
python3 cli.py export --format json --output errors.json
```

### Verificar configuración
```bash
python3 cli.py validate --config-file config.json
```

### Health check manual
```python
from data.integrations.connectors import create_connector

connector = create_connector("hubspot", {"api_token": "..."})
health = connector.health_check()
print(health)
```

## Logs y Debugging

### Habilitar logs detallados
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Ver logs de sincronización específica
```sql
SELECT * FROM sync_history WHERE sync_id = 'sync_123';
SELECT * FROM sync_records WHERE sync_history_id = (SELECT id FROM sync_history WHERE sync_id = 'sync_123');
```

### Analizar errores comunes
```sql
SELECT error_message, COUNT(*) 
FROM sync_records 
WHERE status = 'failed' 
  AND synced_at >= NOW() - INTERVAL '7 days'
GROUP BY error_message 
ORDER BY COUNT(*) DESC;
```

## Mejores Prácticas para Evitar Problemas

1. **Siempre usar dry-run primero:**
   ```python
   result = framework.sync(config, dry_run=True)
   ```

2. **Validar configuración antes de ejecutar:**
   ```python
   from data.integrations.utils import validate_sync_config
   is_valid, error = validate_sync_config(config)
   ```

3. **Monitorear circuit breakers:**
   ```python
   cb_status = framework._get_circuit_breaker("hubspot").get_status()
   print(cb_status)
   ```

4. **Usar batch sizes apropiados:**
   - APIs rápidas: 50-100
   - APIs lentas: 10-25
   - Bases de datos: 100-500

5. **Configurar retry apropiado:**
   ```python
   config = SyncConfig(..., retry_attempts=5, retry_delay_seconds=10)
   ```

## Contacto y Soporte

Si el problema persiste:
1. Revisar logs completos
2. Verificar estado de APIs externas
3. Consultar documentación de APIs específicas
4. Revisar issues en el repositorio


