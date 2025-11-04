# Framework de Integración y Sincronización de Datos

## Visión General

Este framework proporciona una solución completa y unificada para sincronizar datos entre múltiples sistemas:

- **CRM**: HubSpot, Salesforce, etc.
- **ERP**: QuickBooks, SAP, etc.
- **Hojas de Cálculo**: Google Sheets, Excel (vía APIs)
- **Bases de Datos**: PostgreSQL, MySQL, etc.

## Características Principales

✅ **Sincronización Bidireccional**: Sincroniza datos en ambas direcciones entre sistemas  
✅ **Múltiples Conectores**: Soporte extensible para diferentes sistemas  
✅ **Validación Robusta**: Validación de datos antes y después de sincronización  
✅ **Circuit Breaker**: Protección contra fallos en cascada  
✅ **Retry Logic**: Reintentos automáticos con exponential backoff  
✅ **Caché Inteligente**: Evita sincronizaciones innecesarias  
✅ **Resolución de Conflictos**: Múltiples estrategias (source_wins, target_wins, latest, manual)  
✅ **Auditoría Completa**: Tracking completo de todas las sincronizaciones  
✅ **Monitoreo y Alertas**: Métricas y notificaciones en tiempo real  
✅ **Transformación de Datos**: Funciones personalizadas para transformar datos  
✅ **Dry-Run Mode**: Modo de prueba sin escribir cambios  

## Arquitectura

```
┌─────────────────────────────────────────────────────────┐
│              Airflow DAG (data_sync_unified)             │
│  - Parse config                                          │
│  - Validate connections                                   │
│  - Execute sync                                          │
│  - Generate report                                       │
│  - Send notifications                                    │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              SyncFramework                               │
│  - Circuit breaker                                       │
│  - Caching                                               │
│  - Conflict resolution                                   │
│  - Batch processing                                      │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│   Source     │         │    Target    │
│  Connector   │         │  Connector   │
└──────────────┘         └──────────────┘
        │                         │
        ▼                         ▼
┌──────────────┐         ┌──────────────┐
│   HubSpot    │         │  QuickBooks  │
│ QuickBooks   │         │ Google Sheets│
│Google Sheets │         │  PostgreSQL  │
└──────────────┘         └──────────────┘
```

## Estructura de Archivos

```
data/integrations/
├── __init__.py              # Módulo principal
├── connectors.py            # Conectores para diferentes sistemas
├── sync_framework.py        # Framework principal de sincronización
├── sync_schema.sql         # Esquema de base de datos
└── README.md               # Esta documentación
```

## Uso

### 1. Configuración de Credenciales

Configurar variables de entorno para cada sistema:

**HubSpot:**
```bash
export HUBSPOT_API_TOKEN="your_token"
```

**QuickBooks:**
```bash
export QUICKBOOKS_ACCESS_TOKEN="your_token"
export QUICKBOOKS_REALM_ID="your_realm_id"
export QUICKBOOKS_BASE_URL="https://sandbox-quickbooks.api.intuit.com"  # o producción
```

**Google Sheets:**
```bash
export GOOGLE_SHEETS_CREDENTIALS_JSON='{"type": "service_account", ...}'
export GOOGLE_SHEETS_SPREADSHEET_ID="your_spreadsheet_id"
export GOOGLE_SHEETS_SHEET_NAME="Sheet1"
```

### 2. Ejecutar Sincronización desde Airflow

#### Opción A: Usando parámetros del DAG

1. Trigger del DAG `data_sync_unified`
2. Proporcionar parámetros:
   ```json
   {
     "source_type": "hubspot",
     "target_type": "quickbooks",
     "direction": "source_to_target",
     "batch_size": 50,
     "dry_run": false
   }
   ```

#### Opción B: Usando configuración JSON completa

```json
{
  "sync_config": {
    "source_type": "hubspot",
    "source_config": {
      "api_token": "your_token"
    },
    "target_type": "quickbooks",
    "target_config": {
      "access_token": "your_token",
      "realm_id": "your_realm_id"
    },
    "direction": "bidirectional",
    "batch_size": 50,
    "conflict_resolution": "source_wins",
    "filters": {
      "object_type": "contacts",
      "createdAfter": "2025-01-01T00:00:00Z"
    }
  }
}
```

### 3. Uso Programático

```python
from data.integrations.sync_framework import SyncFramework, SyncConfig, SyncDirection

# Crear framework
framework = SyncFramework(db_connection_string="postgresql://...")

# Configurar sincronización
config = SyncConfig(
    sync_id="sync_001",
    source_connector_type="hubspot",
    source_config={"api_token": "your_token"},
    target_connector_type="quickbooks",
    target_config={
        "access_token": "your_token",
        "realm_id": "your_realm_id"
    },
    direction=SyncDirection.BIDIRECTIONAL,
    batch_size=50,
    conflict_resolution="source_wins"
)

# Ejecutar sincronización
result = framework.sync(config, dry_run=False)

# Ver resultados
print(f"Status: {result.status}")
print(f"Successful: {result.successful}/{result.total_records}")
print(f"Failed: {result.failed}")
```

## Conectores Disponibles

### HubSpotConnector

Sincroniza contactos, deals y otros objetos de HubSpot.

**Configuración:**
```python
{
    "name": "hubspot",
    "api_token": "your_hubspot_token"
}
```

**Filtros soportados:**
- `object_type`: "contacts", "deals", "companies"
- `properties`: Lista de propiedades a obtener
- `createdAfter`: Filtrar por fecha de creación

### QuickBooksConnector

Sincroniza items, customers, invoices de QuickBooks Online.

**Configuración:**
```python
{
    "name": "quickbooks",
    "access_token": "your_access_token",
    "realm_id": "your_realm_id",
    "base_url": "https://sandbox-quickbooks.api.intuit.com"
}
```

**Filtros soportados:**
- `entity_type`: "Item", "Customer", "Invoice"
- `updatedSince`: Filtrar por última actualización

### GoogleSheetsConnector

Lee y escribe en Google Sheets.

**Configuración:**
```python
{
    "name": "google_sheets",
    "credentials_json": "{...}",  # JSON de service account
    "spreadsheet_id": "your_spreadsheet_id",
    "sheet_name": "Sheet1"
}
```

**Filtros soportados:**
- `range`: Rango de celdas a leer (ej: "Sheet1!A1:Z100")

## Resolución de Conflictos

El framework soporta múltiples estrategias de resolución:

- **source_wins**: Los datos del source siempre ganan
- **target_wins**: Los datos del target siempre ganan
- **latest**: Usa el registro más reciente (basado en `synced_at`)
- **manual**: Marca como conflicto para resolución manual

## Base de Datos

El framework crea automáticamente las siguientes tablas:

- `sync_history`: Historial de sincronizaciones
- `sync_records`: Registros individuales sincronizados
- `field_mappings`: Mapeo de campos entre sistemas
- `sync_schedules`: Configuración de sincronizaciones programadas
- `sync_conflicts`: Conflictos pendientes de resolución
- `sync_metrics`: Métricas de performance

### Vistas Útiles

- `sync_summary`: Resumen diario de sincronizaciones
- `sync_conflicts_view`: Conflictos pendientes
- `sync_performance_view`: Métricas de performance por hora

## Monitoreo y Alertas

El framework incluye:

- **Métricas en tiempo real**: Latencia, tasa de éxito, errores
- **Circuit breaker status**: Estado de protección contra fallos
- **Notificaciones Slack**: Alertas automáticas de éxito/fallo
- **Auditoría completa**: Todos los cambios son registrados

## Extensión

### Agregar Nuevo Conector

1. Crear clase que herede de `BaseConnector`:

```python
from data.integrations.connectors import BaseConnector, SyncRecord

class MyCustomConnector(BaseConnector):
    def connect(self) -> bool:
        # Implementar conexión
        pass
    
    def read_records(self, filters, limit):
        # Implementar lectura
        pass
    
    def write_records(self, records):
        # Implementar escritura
        pass
    
    # ... otros métodos requeridos
```

2. Registrar en `create_connector()`:

```python
def create_connector(connector_type: str, config: Dict[str, Any]):
    connectors = {
        "my_custom": MyCustomConnector,
        # ... otros conectores
    }
    # ...
```

### Agregar Transformación Personalizada

```python
def my_transform_function(data: Dict[str, Any]) -> Dict[str, Any]:
    """Transforma datos antes de sincronizar"""
    transformed = data.copy()
    transformed['custom_field'] = data.get('old_field', '').upper()
    return transformed

config = SyncConfig(
    # ...
    transform_function=my_transform_function
)
```

## Mejores Prácticas

1. **Siempre usar dry-run primero**: Prueba en modo dry-run antes de ejecutar en producción
2. **Configurar conflict resolution**: Define estrategia clara para conflictos
3. **Monitorear circuit breaker**: Verifica estado de circuit breakers regularmente
4. **Revisar auditoría**: Usa las tablas de auditoría para debugging y análisis
5. **Validar datos**: Habilita validación para detectar problemas temprano
6. **Batch size apropiado**: Ajusta batch size según capacidad de los sistemas
7. **Credenciales seguras**: Usa External Secrets o variables de entorno, nunca hardcodees

## Troubleshooting

### Error: "Circuit breaker abierto"

**Causa**: Demasiados fallos consecutivos  
**Solución**: Revisar logs, verificar credenciales, esperar timeout

### Error: "Source/Target connector no saludable"

**Causa**: Problemas de conectividad o credenciales  
**Solución**: Verificar credenciales, network connectivity, API status

### Sincronización lenta

**Causa**: Batch size muy grande o problemas de red  
**Solución**: Reducir batch size, verificar latencia de APIs

### Conflictos frecuentes

**Causa**: Datos modificados en ambos sistemas  
**Solución**: Revisar estrategia de resolución de conflictos, considerar sincronización unidireccional

## Ejemplos de Uso

### Ejemplo 1: Sincronizar contactos de HubSpot a Google Sheets

```python
config = SyncConfig(
    sync_id="hubspot_to_sheets",
    source_connector_type="hubspot",
    source_config={"api_token": "..."},
    target_connector_type="google_sheets",
    target_config={
        "credentials_json": "{...}",
        "spreadsheet_id": "...",
        "sheet_name": "Contacts"
    },
    direction=SyncDirection.SOURCE_TO_TARGET,
    filters={"object_type": "contacts"}
)
```

### Ejemplo 2: Sincronización bidireccional QuickBooks ↔ HubSpot

```python
config = SyncConfig(
    sync_id="qb_hubspot_bidirectional",
    source_connector_type="quickbooks",
    source_config={"access_token": "...", "realm_id": "..."},
    target_connector_type="hubspot",
    target_config={"api_token": "..."},
    direction=SyncDirection.BIDIRECTIONAL,
    conflict_resolution="latest"
)
```

## Soporte

Para problemas o preguntas:
1. Revisar logs de Airflow
2. Consultar tablas de auditoría en base de datos
3. Verificar estado de circuit breakers
4. Revisar documentación de APIs de sistemas externos


