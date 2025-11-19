# Orquestación de Integraciones para Fusiones y Adquisiciones

Este DAG (`merger_acquisition_integration`) orquesta la integración de múltiples sistemas durante procesos de fusiones o adquisiciones.

## 🚀 Mejoras Implementadas

### Características Avanzadas

1. **Retry Logic Inteligente**
   - Reintentos automáticos con exponential backoff
   - Soporte para tenacity (si está disponible)
   - Manejo de errores transitorios (conexión, timeout)

2. **Procesamiento por Chunks**
   - Procesamiento eficiente de grandes volúmenes de datos
   - Configurable via parámetro `chunk_size`
   - Logging de progreso para datasets grandes

3. **Sistema de Backups**
   - Creación automática de backups antes de cargar datos
   - Tablas de backup con timestamp
   - Restauración fácil en caso de problemas

4. **Soporte S3**
   - Lectura directa de archivos desde S3
   - Soporte para CSV, Excel, JSON
   - Parsing automático de paths S3

5. **Validación Mejorada**
   - Validación temprana de configuraciones
   - Estadísticas detalladas de extracción
   - Manejo robusto de errores por sistema

6. **Logging Estructurado**
   - Logs con emojis para fácil identificación (✓ éxito, ✗ error)
   - Progreso detallado por sistema
   - Estadísticas de rendimiento

7. **Manejo de Memoria**
   - Procesamiento por chunks para evitar problemas de memoria
   - Limpieza automática de recursos
   - Optimización para grandes datasets

8. **Sistema de Notificaciones**
   - Soporte para Slack, Webhooks y Email
   - Notificaciones automáticas basadas en estado
   - Configuración flexible de canales

9. **Exportación de Reportes**
   - Exportación a JSON, CSV y HTML
   - Reportes detallados con métricas
   - Archivos timestamped para trazabilidad

10. **Comparación de Datos**
    - Comparación antes/después de la carga
    - Identificación de registros nuevos, actualizados y eliminados
    - Análisis de cambios por categoría

11. **Rollback Automático**
    - Rollback automático en caso de errores críticos
    - Restauración desde backups
    - Configuración de umbral de error

12. **Sistema de Cache**
    - Cache de extracciones para evitar re-extracciones
    - Cache en PostgreSQL con TTL configurable
    - Reducción de carga en sistemas fuente

13. **Validación de Integridad Referencial**
    - Validación de relaciones entre tablas
    - Detección de registros huérfanos
    - Configuración flexible de reglas

14. **Enriquecimiento de Datos**
    - Enriquecimiento con APIs externas
    - Procesamiento en batches
    - Manejo robusto de errores

15. **Métricas Prometheus**
    - Métricas de extracción, carga y errores
    - Histogramas de duración
    - Contadores de cache hits
    - Integración con sistemas de monitoreo

16. **Sistema de Auditoría**
    - Registro completo de todas las operaciones
    - Trazabilidad de cambios
    - Logs con detalles de ejecución
    - Integración con sistemas de compliance

17. **Validación de Calidad Personalizada**
    - Reglas de completitud, unicidad y validez
    - Validación por campo y categoría
    - Umbrales configurables
    - Reportes de violaciones

18. **Detección de Drift de Datos**
    - Comparación con baseline
    - Identificación de cambios significativos
    - Alertas de drift
    - Análisis de tendencias

19. **Linaje de Datos**
    - Trazabilidad completa de datos
    - Mapeo de sistemas fuente a destino
    - Registro de transformaciones
    - ID único de linaje

20. **Verificación de Integridad con Hash**
    - Cálculo de hash SHA256 de datos
    - Verificación de integridad
    - Detección de corrupción
    - Validación de consistencia

21. **Procesamiento Paralelo**
    - Extracción paralela de múltiples sistemas
    - ThreadPoolExecutor para mejor rendimiento
    - Procesamiento concurrente hasta 5 workers
    - Reducción significativa de tiempo de ejecución

22. **Validación de Esquemas**
    - Validación de estructura de datos
    - Verificación de tipos de campos
    - Validación de restricciones (longitud, rangos)
    - Detección temprana de problemas de formato

23. **Health Checks de Sistemas**
    - Verificación de salud antes de extraer
    - Medición de tiempo de respuesta
    - Detección de sistemas no disponibles
    - Prevención de extracciones fallidas

24. **Circuit Breaker Pattern**
    - Protección contra fallos en cascada
    - Estados: closed, open, half-open
    - Recuperación automática
    - Configuración de umbrales

25. **Encriptación de Datos Sensibles**
    - Encriptación de campos sensibles
    - Hash SHA256 para protección
    - Marcado de campos encriptados
    - Preparado para encriptación real

26. **Compresión de Datos**
    - Soporte para gzip y zlib
    - Reducción de tamaño de almacenamiento
    - Compresión/descompresión automática
    - Optimización de transferencia

27. **Detección de Anomalías**
    - Análisis estadístico de datos numéricos
    - Detección usando desviación estándar
    - Identificación de valores atípicos
    - Estadísticas por campo

28. **Carga Incremental**
    - Procesamiento solo de cambios
    - Identificación de registros nuevos/actualizados
    - Reducción de tiempo de procesamiento
    - Optimización de recursos

29. **Resolución de Conflictos**
    - Múltiples estrategias de resolución
    - Merge inteligente de datos
    - Priorización por timestamp
    - Configuración flexible

30. **Dead Letter Queue (DLQ)**
    - Almacenamiento de registros con errores
    - Reintento posterior
    - Análisis de errores
    - Trazabilidad de fallos

31. **Reglas de Negocio**
    - Aplicación de reglas personalizadas
    - Transformaciones condicionales
    - Cálculos dinámicos
    - Validación de lógica de negocio

## Flujo del Proceso

```
Health Checks (opcional)
    ↓
Extracción Empresa A ──┐
                      ├─→ Transformación → Validación Esquema (opcional)
Extracción Empresa B ──┘                    ↓
                                    Validación Datos
                                    ↓
                    ┌───────────────────┴───────────────────┐
                    │                                       │
        Validación Calidad (opcional)          Detección Anomalías (opcional)
                    │                                       │
                    └───────────────────┬───────────────────┘
                                    ↓
                                 Carga Sistema Unificado
                                    ↓
                                 Reporte de Estado
                                    ↓
        ┌───────────────────────────┴───────────────────────────┐
        │                                                         │
Comparación (opcional)                          Exportación (opcional)
        │                                                         │
Integridad Referencial (opcional)          Notificaciones (opcional)
        │                                                         │
Rollback (si error)                                    Linaje de Datos
```

## Componentes

### 1. Extracción de Datos
- **Empresa A**: Extrae datos de todos los sistemas configurados
- **Empresa B**: Extrae datos de todos los sistemas configurados
- **Sistemas soportados**:
  - PostgreSQL
  - MySQL
  - APIs REST
  - Archivos CSV/Excel (S3)

### 2. Transformación
- Normaliza datos de ambas empresas a formato común
- Aplica reglas de mapeo de campos
- Deduplicación
- Enriquecimiento de datos

### 3. Validación
- Valida campos requeridos
- Validación de formatos (email, números, fechas)
- Validación de rangos y longitudes
- Modo estricto o permisivo

### 4. Carga
- Carga datos validados al sistema unificado
- Soporta PostgreSQL, MySQL, APIs REST
- Manejo de errores y reintentos

### 5. Reporte
- Genera reporte completo del estado de la integración
- Métricas de calidad y tasa de éxito
- Detalles por categoría

## Uso

### Ejecución Manual desde UI

1. Ir a Airflow UI → DAGs → `merger_acquisition_integration`
2. Click en "Trigger DAG w/ config"
3. Proporcionar parámetros en formato JSON

### Ejecución vía CLI

```bash
airflow dags trigger merger_acquisition_integration \
  --conf '{
    "company_a_config": {...},
    "company_b_config": {...},
    "unified_system_config": {...},
    "transformation_rules": {...}
  }'
```

### Ejecución vía API

```python
import requests
from airflow.api.client.local_client import Client

client = Client(None, None)
client.trigger_dag(
    dag_id="merger_acquisition_integration",
    conf={
        "company_a_config": {...},
        "company_b_config": {...},
        "unified_system_config": {...},
        "transformation_rules": {...}
    }
)
```

## Configuración de Parámetros

### company_a_config

Configuración para extraer datos de la empresa A:

```json
{
  "systems": [
    {
      "type": "postgres",
      "name": "crm_company_a",
      "conn_id": "postgres_company_a",
      "tables": ["customers", "orders", "products"],
      "where_clause": "created_at >= '2020-01-01'"
    },
    {
      "type": "mysql",
      "name": "erp_company_a",
      "conn_id": "mysql_company_a",
      "tables": ["clients", "transactions"],
      "where_clause": "status = 'active'"
    },
    {
      "type": "api",
      "name": "salesforce_company_a",
      "conn_id": "http_salesforce_a",
      "endpoint": "/services/data/v52.0/query/?q=SELECT+Id,Name+FROM+Account",
      "headers": {
        "Authorization": "Bearer {{token}}"
      },
      "data_key": "records"
    }
  ]
}
```

### company_b_config

Similar a `company_a_config` pero para empresa B:

```json
{
  "systems": [
    {
      "type": "postgres",
      "name": "crm_company_b",
      "conn_id": "postgres_company_b",
      "tables": ["clients", "orders", "items"]
    }
  ]
}
```

### unified_system_config

Configuración del sistema unificado destino:

```json
{
  "type": "postgres",
  "conn_id": "postgres_unified",
  "schema": "unified"
}
```

O para API:

```json
{
  "type": "api",
  "conn_id": "http_unified_api",
  "endpoint": "/api/v1/data/load",
  "headers": {
    "Content-Type": "application/json",
    "Authorization": "Bearer {{token}}"
  }
}
```

### transformation_rules

Reglas de transformación y mapeo:

```json
{
  "mappings": {
    "customers": {
      "company_a": ["customers", "customer_data"],
      "company_b": ["clients", "customers"],
      "field_mapping": {
        "email": ["email", "e_mail", "email_address"],
        "name": ["name", "full_name", "customer_name"],
        "phone": ["phone", "phone_number"],
        "address": ["address", "street_address"]
      }
    },
    "orders": {
      "company_a": ["orders"],
      "company_b": ["transactions", "orders"],
      "field_mapping": {
        "order_id": ["order_id", "id", "transaction_id"],
        "customer_id": ["customer_id", "client_id"],
        "amount": ["amount", "total", "order_total"],
        "date": ["date", "order_date", "created_at"]
      }
    }
  },
  "transformations": [
    {
      "type": "deduplicate",
      "key_fields": ["email", "order_id"]
    },
    {
      "type": "enrich",
      "rules": {
        "integration_date": "{{current_date}}",
        "source": "merger_acquisition"
      }
    }
  ]
}
```

## Ejemplo Completo

### Escenario: Fusión de dos empresas de e-commerce

**Empresa A** usa:
- PostgreSQL para CRM
- MySQL para ERP
- Salesforce para ventas

**Empresa B** usa:
- PostgreSQL para CRM
- API REST para inventario

**Sistema Unificado**: PostgreSQL con schema `unified`

```json
{
  "company_a_config": {
    "systems": [
      {
        "type": "postgres",
        "name": "crm_a",
        "conn_id": "postgres_a",
        "tables": ["customers", "orders"]
      },
      {
        "type": "mysql",
        "name": "erp_a",
        "conn_id": "mysql_a",
        "tables": ["products", "inventory"]
      },
      {
        "type": "api",
        "name": "salesforce_a",
        "conn_id": "http_salesforce",
        "endpoint": "/services/data/v52.0/query/?q=SELECT+Id,Name,Email+FROM+Contact",
        "data_key": "records"
      }
    ]
  },
  "company_b_config": {
    "systems": [
      {
        "type": "postgres",
        "name": "crm_b",
        "conn_id": "postgres_b",
        "tables": ["clients", "transactions"]
      },
      {
        "type": "api",
        "name": "inventory_b",
        "conn_id": "http_inventory_b",
        "endpoint": "/api/inventory/items",
        "data_key": "items"
      }
    ]
  },
  "unified_system_config": {
    "type": "postgres",
    "conn_id": "postgres_unified",
    "schema": "unified"
  },
  "transformation_rules": {
    "mappings": {
      "customers": {
        "company_a": ["customers"],
        "company_b": ["clients"],
        "field_mapping": {
          "email": ["email", "e_mail"],
          "name": ["name", "full_name", "customer_name"],
          "phone": ["phone", "phone_number"]
        }
      },
      "orders": {
        "company_a": ["orders"],
        "company_b": ["transactions"],
        "field_mapping": {
          "order_id": ["order_id", "id", "transaction_id"],
          "customer_id": ["customer_id", "client_id"],
          "amount": ["amount", "total"],
          "date": ["date", "order_date"]
        }
      },
      "products": {
        "company_a": ["products"],
        "company_b": ["items"],
        "field_mapping": {
          "product_id": ["product_id", "id", "item_id"],
          "name": ["name", "product_name", "item_name"],
          "price": ["price", "unit_price"]
        }
      }
    },
    "transformations": [
      {
        "type": "deduplicate",
        "key_fields": ["email"]
      }
    ]
  },
  "dry_run": false,
  "validation_strict": true,
  "generate_detailed_report": true
}
```

## Modo Dry-Run

Para probar el flujo sin cargar datos:

```json
{
  "dry_run": true,
  ...
}
```

En modo dry-run:
- Se extraen los datos
- Se transforman
- Se validan
- **NO se cargan** al sistema unificado
- Se genera reporte de lo que se cargaría

## Validación

### Modo Estricto (default)

- Falla si hay registros inválidos
- Requiere todos los campos obligatorios
- Valida formatos estrictamente

### Modo Permisivo

```json
{
  "validation_strict": false,
  ...
}
```

- Continúa aunque haya registros inválidos
- Genera warnings en lugar de errores
- Útil para análisis de calidad de datos

## Reporte de Estado

El reporte incluye:

- **Resumen ejecutivo**:
  - Total de registros extraídos (A + B)
  - Total transformados y cargados
  - Tasa de validación
  - Estado general

- **Detalles por etapa**:
  - Extracción: sistemas procesados, registros por sistema
  - Transformación: registros por categoría
  - Validación: registros válidos/inválidos, errores
  - Carga: registros cargados, tablas, errores

- **Métricas**:
  - Tasa de extracción → carga
  - Score de calidad de datos
  - Tasa de éxito general

## Configuración de Notificaciones

### notification_config

Configuración para enviar notificaciones:

```json
{
  "slack": {
    "enabled": true,
    "webhook_url": "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
  },
  "webhook": {
    "enabled": true,
    "url": "https://your-webhook-endpoint.com/notify"
  },
  "email": {
    "enabled": true,
    "to": ["team@company.com", "manager@company.com"]
  }
}
```

Las notificaciones se envían automáticamente al completar la integración con el estado y métricas.

## Exportación de Reportes

Para exportar reportes a archivo:

```json
{
  "export_report": true,
  "export_format": "html"
}
```

Formatos disponibles:
- `json`: Formato JSON completo (máquina)
- `csv`: Resumen en CSV (Excel)
- `html`: Reporte visual HTML (humano)

## Comparación de Datos

Para comparar datos antes y después de la carga:

```json
{
  "enable_comparison": true
}
```

La comparación muestra:
- Registros antes y después
- Registros nuevos agregados
- Registros actualizados
- Registros eliminados

## Rollback Automático

Para habilitar rollback automático en caso de errores:

```json
{
  "enable_rollback_on_error": true
}
```

El rollback se ejecuta automáticamente si:
- La tasa de error es > 50%
- Hay backups disponibles
- El sistema destino es PostgreSQL

## Sistema de Cache

Para habilitar cache de extracciones:

```json
{
  "enable_cache": true
}
```

El cache:
- Reduce carga en sistemas fuente
- Acelera re-ejecuciones
- TTL de 1 hora por defecto
- Almacenado en PostgreSQL

## Validación de Integridad Referencial

Para validar relaciones entre tablas:

```json
{
  "enable_referential_integrity_check": true,
  "referential_integrity_rules": [
    {
      "parent_category": "customers",
      "child_category": "orders",
      "parent_key": "customer_id",
      "child_key": "customer_id"
    }
  ]
}
```

La validación detecta:
- Registros huérfanos (orders sin customer)
- Relaciones rotas
- Problemas de integridad

## Enriquecimiento de Datos

Para enriquecer datos con APIs externas:

```json
{
  "enable_data_enrichment": true,
  "enrichment_config": {
    "enabled": true,
    "api_url": "https://api.example.com/enrich",
    "api_key": "your-api-key",
    "batch_size": 100,
    "field_mapping": {
      "email": "email_address",
      "name": "full_name"
    }
  }
}
```

## Métricas Prometheus

Las métricas están habilitadas por defecto y exponen:

- `merger_acquisition_records_extracted_total`: Total de registros extraídos
- `merger_acquisition_records_loaded_total`: Total de registros cargados
- `merger_acquisition_duration_seconds`: Duración por etapa
- `merger_acquisition_errors_total`: Total de errores
- `merger_acquisition_cache_hits_total`: Cache hits

Para deshabilitar:
```json
{
  "enable_metrics": false
}
```

## Sistema de Auditoría

El sistema de auditoría está habilitado por defecto y registra:

- Todas las operaciones realizadas
- Detalles de ejecución
- Usuario y timestamp
- Resultados y errores

Para deshabilitar:
```json
{
  "enable_audit_log": false
}
```

Los registros se almacenan en `integration_audit_log` con índices para búsqueda rápida.

## Validación de Calidad Personalizada

Para definir reglas de calidad personalizadas:

```json
{
  "enable_data_quality_rules": true,
  "data_quality_rules": [
    {
      "name": "completeness_email",
      "type": "completeness",
      "field": "email",
      "threshold": 95.0
    },
    {
      "name": "uniqueness_customer_id",
      "type": "uniqueness",
      "field": "customer_id",
      "threshold": 100.0
    },
    {
      "name": "validity_email_format",
      "type": "validity",
      "field": "email",
      "condition": "regex",
      "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$",
      "threshold": 98.0
    }
  ]
}
```

Tipos de reglas:
- `completeness`: Porcentaje de campos no nulos
- `uniqueness`: Porcentaje de valores únicos
- `validity`: Porcentaje de valores válidos (regex o range)

## Detección de Drift

Para detectar drift de datos:

```json
{
  "enable_drift_detection": true
}
```

La detección compara:
- Registros agregados
- Registros eliminados
- Registros modificados
- Porcentaje de drift total

## Linaje de Datos

El linaje está habilitado por defecto y genera:

- ID único de linaje
- Sistemas fuente
- Transformaciones aplicadas
- Sistema destino
- Timestamp

Para deshabilitar:
```json
{
  "enable_data_lineage": false
}
```

## Procesamiento Paralelo

Para habilitar extracción paralela de sistemas:

```json
{
  "enable_parallel_extraction": true
}
```

Beneficios:
- Reducción de tiempo de ejecución
- Hasta 5 workers paralelos
- Mejor utilización de recursos
- Fallos aislados por sistema

## Validación de Esquemas

Para validar estructura de datos:

```json
{
  "enable_schema_validation": true,
  "expected_schema": {
    "required_fields": ["email", "name", "customer_id"],
    "field_types": {
      "email": "string",
      "customer_id": "integer",
      "amount": "float",
      "active": "boolean"
    },
    "field_constraints": {
      "email": {
        "min_length": 5,
        "max_length": 255
      },
      "amount": {
        "min_value": 0,
        "max_value": 1000000
      }
    }
  }
}
```

## Health Checks

Para verificar salud de sistemas antes de extraer:

```json
{
  "enable_health_checks": true
}
```

Los health checks verifican:
- Disponibilidad de sistemas
- Tiempo de respuesta
- Estado de conexiones
- APIs y endpoints

## Circuit Breaker

Para proteger contra fallos en cascada:

```json
{
  "enable_circuit_breaker": true
}
```

El circuit breaker:
- Abre el circuito después de N fallos
- Bloquea llamadas cuando está abierto
- Intenta recuperación después de timeout
- Transición a half-open para testing

## Encriptación de Datos Sensibles

Para encriptar campos sensibles:

```json
{
  "enable_encryption": true,
  "sensitive_fields": ["ssn", "credit_card", "password", "api_key"]
}
```

Los campos sensibles se marcan y protegen antes de almacenar.

## Detección de Anomalías

Para detectar anomalías en datos numéricos:

```json
{
  "enable_anomaly_detection": true,
  "anomaly_threshold": 3.0
}
```

La detección:
- Analiza campos numéricos (amount, price, quantity, etc.)
- Usa desviación estándar (default: 3σ)
- Identifica valores atípicos
- Proporciona estadísticas (mean, std, min, max)

## Carga Incremental

Para procesar solo cambios:

```json
{
  "enable_incremental_load": true,
  "incremental_key": "id"
}
```

La carga incremental:
- Identifica registros nuevos o actualizados
- Compara con último timestamp
- Reduce tiempo de procesamiento
- Optimiza uso de recursos

## Resolución de Conflictos

Para manejar conflictos entre empresas:

```json
{
  "conflict_resolution_strategy": "latest"
}
```

Estrategias disponibles:
- `latest`: Usar registro más reciente (por timestamp)
- `company_a`: Priorizar empresa A
- `company_b`: Priorizar empresa B
- `merge`: Combinar campos de ambas empresas

## Dead Letter Queue

Para capturar registros con errores:

```json
{
  "enable_dead_letter_queue": true
}
```

La DLQ:
- Almacena registros que fallaron
- Permite reintento posterior
- Facilita análisis de errores
- Tabla: `integration_dlq`

## Reglas de Negocio

Para aplicar reglas personalizadas:

```json
{
  "enable_business_rules": true,
  "business_rules": [
    {
      "name": "calculate_total",
      "type": "field_comparison",
      "field1": "quantity",
      "field2": "price",
      "operator": ">",
      "action": "calculate",
      "target_field": "total",
      "formula": "record['quantity'] * record['price']"
    },
    {
      "name": "set_status",
      "type": "value_check",
      "field": "amount",
      "expected_value": 0,
      "action": "set_value",
      "target_field": "status",
      "value": "inactive"
    }
  ]
}
```

## Monitoreo

### Logs

Revisar logs de cada task:
- `extract_company_a_data`: Extracción empresa A
- `extract_company_b_data`: Extracción empresa B
- `transform_to_common_format`: Transformación
- `validate_transformed_data`: Validación
- `load_to_unified_system`: Carga
- `generate_status_report`: Reporte
- `compare_data_changes`: Comparación (opcional)
- `export_report_file`: Exportación (opcional)
- `send_notifications`: Notificaciones (opcional)
- `rollback_on_error`: Rollback (opcional, solo en errores)

### Métricas Airflow

El DAG expone métricas que se pueden monitorear en:
- Airflow UI → DAG Runs
- Grafana (si está configurado)
- Prometheus (si está configurado)

## Troubleshooting

### Error: "No se pueden conectar a la base de datos"

- Verificar que las conexiones estén configuradas en Airflow
- Verificar credenciales en Admin → Connections

### Error: "Validación falló"

- Revisar logs de `validate_transformed_data`
- Verificar reglas de validación
- Considerar usar `validation_strict: false` para análisis

### Error: "No se encontraron datos"

- Verificar configuración de sistemas
- Verificar permisos de acceso
- Verificar cláusulas WHERE

### Datos duplicados

- Ajustar reglas de deduplicación en `transformation_rules`
- Verificar campos clave en `field_mapping`

## Extensión

### Agregar nuevos tipos de sistemas

Editar `extract_company_a_data` y `extract_company_b_data`:

```python
elif system_type == "sap":
    # Implementar extracción SAP
    pass
elif system_type == "oracle":
    # Implementar extracción Oracle
    pass
```

### Agregar nuevas transformaciones

Editar `transform_to_common_format`:

```python
elif transform_type == "normalize_currency":
    # Normalizar monedas
    pass
elif transform_type == "geocode_addresses":
    # Geocodificar direcciones
    pass
```

### Agregar nuevas validaciones

Editar `validate_transformed_data`:

```python
# Agregar reglas de validación personalizadas
if "custom_validation" in rules:
    # Aplicar validación personalizada
    pass
```

## Mejores Prácticas

1. **Siempre probar en dry-run primero**
   - Usar `dry_run: true` para validar el flujo completo sin cargar datos
   - Revisar los registros que se cargarían

2. **Configurar chunking para grandes volúmenes**
   - Para datasets > 10,000 registros, ajustar `chunk_size`
   - Monitorear uso de memoria durante la ejecución

3. **Habilitar backups en producción**
   - Siempre usar `enable_backup: true` en producción
   - Las tablas de backup se crean automáticamente con timestamp

4. **Validar configuraciones antes de ejecutar**
   - El DAG valida automáticamente las configuraciones
   - Errores de configuración se detectan temprano

5. **Monitorear logs durante la ejecución**
   - Buscar símbolos ✓ (éxito) y ✗ (error)
   - Revisar estadísticas de extracción por sistema

6. **Revisar reportes después de cada ejecución**
   - El reporte incluye métricas detalladas
   - Identificar sistemas con problemas

7. **Documentar reglas de transformación específicas**
   - Mantener mapeos de campos actualizados
   - Documentar transformaciones personalizadas

8. **Usar versionado de configuraciones**
   - Guardar configuraciones en control de versiones
   - Etiquetar configuraciones por ejecución

9. **Ejecutar en horarios de bajo tráfico**
   - Para minimizar impacto en sistemas fuente
   - Coordinar con equipos de operaciones

10. **Configurar retries apropiados**
    - Ajustar `max_retries_extraction` según la confiabilidad de los sistemas
    - Monitorear tasa de éxito de reintentos

11. **Configurar notificaciones**
    - Habilitar notificaciones para monitoreo en tiempo real
    - Configurar canales apropiados (Slack, Email, Webhooks)
    - Ajustar severidad según necesidades

12. **Exportar reportes regularmente**
    - Habilitar exportación de reportes para auditoría
    - Elegir formato apropiado (JSON para máquinas, HTML para humanos)
    - Almacenar reportes históricos

13. **Usar comparación de datos**
    - Habilitar comparación para validar cambios
    - Revisar métricas de nuevos/actualizados/eliminados
    - Usar para auditoría y compliance

14. **Configurar rollback automático**
    - Habilitar solo en producción con backups confiables
    - Ajustar umbral de error según tolerancia al riesgo
    - Monitorear ejecuciones de rollback

15. **Usar cache para optimización**
    - Habilitar cache para extracciones repetitivas
    - Configurar TTL apropiado según frecuencia de cambios
    - Monitorear tasa de cache hits

16. **Validar integridad referencial**
    - Definir reglas de relaciones entre tablas
    - Validar después de cada carga
    - Corregir registros huérfanos antes de producción

17. **Enriquecer datos cuando sea necesario**
    - Usar APIs externas para datos adicionales
    - Configurar batch size apropiado
    - Manejar rate limits de APIs

18. **Monitorear con Prometheus**
    - Habilitar métricas para observabilidad
    - Configurar dashboards en Grafana
    - Establecer alertas basadas en métricas

19. **Mantener auditoría completa**
    - Habilitar logs de auditoría para compliance
    - Revisar registros regularmente
    - Usar para troubleshooting y análisis

20. **Definir reglas de calidad personalizadas**
    - Establecer umbrales de calidad
    - Validar completitud, unicidad y validez
    - Corregir violaciones antes de producción

21. **Monitorear drift de datos**
    - Establecer baseline de referencia
    - Detectar cambios significativos
    - Investigar causas de drift

22. **Usar linaje de datos**
    - Habilitar para trazabilidad completa
    - Documentar transformaciones
    - Usar para análisis de impacto

23. **Usar procesamiento paralelo**
    - Habilitar para múltiples sistemas
    - Mejorar tiempo de ejecución
    - Monitorear uso de recursos

24. **Validar esquemas de datos**
    - Definir esquemas esperados
    - Validar antes de transformar
    - Detectar problemas temprano

25. **Verificar salud de sistemas**
    - Habilitar health checks antes de extraer
    - Evitar extracciones fallidas
    - Monitorear tiempo de respuesta

26. **Usar circuit breaker para sistemas críticos**
    - Proteger contra fallos en cascada
    - Configurar umbrales apropiados
    - Monitorear estados del circuito

27. **Encriptar datos sensibles**
    - Identificar campos sensibles
    - Habilitar encriptación
    - Verificar que campos estén protegidos

28. **Detectar anomalías en datos**
    - Habilitar detección para campos numéricos
    - Revisar valores atípicos
    - Investigar causas de anomalías
    - Ajustar umbral según necesidades

29. **Usar carga incremental**
    - Habilitar para optimizar tiempo
    - Configurar campo de timestamp
    - Monitorear registros procesados
    - Reducir carga en sistemas

30. **Configurar resolución de conflictos**
    - Elegir estrategia apropiada
    - Probar diferentes estrategias
    - Documentar decisiones
    - Monitorear conflictos resueltos

31. **Usar Dead Letter Queue**
    - Habilitar para capturar errores
    - Revisar registros en DLQ regularmente
    - Reintentar procesamiento
    - Analizar patrones de errores

32. **Aplicar reglas de negocio**
    - Definir reglas específicas del dominio
    - Validar lógica de negocio
    - Aplicar transformaciones condicionales
    - Documentar reglas aplicadas

## Seguridad

- Las conexiones de base de datos se manejan vía Airflow Connections
- No hardcodear credenciales en configuraciones
- Usar secretos de Kubernetes/Vault para producción
- Validar permisos de acceso antes de ejecutar

## Soporte

Para problemas o preguntas:
1. Revisar logs del DAG
2. Verificar configuración de parámetros
3. Consultar documentación de Airflow
4. Contactar al equipo de Data Engineering


