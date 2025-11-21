# Top 10 Conectores Más Útiles de Airbyte

Este documento lista los 10 conectores más útiles y populares de Airbyte, organizados por categoría y con casos de uso específicos para la plataforma.

**Versión**: 2.0  
**Última actualización**: 2025-01-15  
**Estado**: ✅ Mejorado con configuraciones avanzadas y ejemplos prácticos

## 📊 Top 10 Conectores

### 1. **PostgreSQL** (Source & Destination)
**Tipo**: Database  
**Categoría**: Base de datos relacional  
**Popularidad**: ⭐⭐⭐⭐⭐  
**Complejidad**: Media

**Casos de Uso**:
- ✅ Sincronizar datos entre bases de datos PostgreSQL
- ✅ Migración de datos entre entornos (dev → staging → prod)
- ✅ Consolidar datos de múltiples fuentes en un data warehouse
- ✅ Backup incremental automático
- ✅ CDC (Change Data Capture) para sincronización en tiempo real
- ✅ Multi-región replication
- ✅ Sincronización de esquemas específicos

**Configuración típica**:
```yaml
Source: PostgreSQL → Destination: PostgreSQL/Snowflake/BigQuery
```

**Configuración detallada**:

**Source (PostgreSQL)**:
```json
{
  "host": "postgres.example.com",
  "port": 5432,
  "database": "production_db",
  "schemas": ["public", "analytics"],
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "replication_method": {
    "method": "CDC",  // o "Standard" para full/incremental
    "replication_slot": "airbyte_slot",
    "publication": "airbyte_publication"
  },
  "ssl": true,
  "tunnel_method": null  // o SSH si requiere
}
```

**Destination (PostgreSQL)**:
```json
{
  "host": "warehouse.example.com",
  "port": 5432,
  "database": "data_warehouse",
  "schema": "staging",
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "ssl": true
}
```

**CDC Setup (Requisitos)**:
```sql
-- En PostgreSQL source
CREATE USER airbyte_user WITH REPLICATION PASSWORD 'secure_password';
GRANT SELECT ON ALL TABLES IN SCHEMA public TO airbyte_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO airbyte_user;

-- Crear publicación
CREATE PUBLICATION airbyte_publication FOR ALL TABLES;

-- Crear replication slot (Airbyte lo hace automáticamente)
-- SELECT pg_create_logical_replication_slot('airbyte_slot', 'pgoutput');
```

**Ventajas**:
- ✅ Soporte nativo para CDC (Logical Replication)
- ✅ Sincronización incremental automática
- ✅ Alta performance para grandes volúmenes (miles de tablas)
- ✅ Bajo overhead en source database
- ✅ Soporte para tipos de datos complejos (JSON, arrays, etc.)

**Limitaciones**:
- ⚠️ CDC requiere configuración adicional en PostgreSQL
- ⚠️ Requiere permisos de replicación
- ⚠️ Puede ser lento para full refresh en tablas muy grandes

**Recursos recomendados**:
- CPU: 2-4 cores para CDC
- Memoria: 4-8GB para workers
- Storage: Depende del volumen de datos

**Troubleshooting común**:
- **Error: "replication slot not found"**: Crear slot manualmente o verificar permisos
- **Error: "WAL retention"**: Aumentar `wal_keep_size` en PostgreSQL
- **Slow sync**: Verificar índices en source, usar CDC en lugar de full refresh

---

### 2. **Stripe** (Source)
**Tipo**: Payment Processing  
**Categoría**: E-commerce / Finanzas  
**Popularidad**: ⭐⭐⭐⭐⭐  
**Complejidad**: Baja

**Casos de Uso**:
- ✅ Sincronizar pagos, suscripciones y clientes a data warehouse
- ✅ Integración con sistemas contables (QuickBooks, Xero) - **Ya implementado en tu plataforma**
- ✅ Análisis de ingresos y métricas de negocio
- ✅ Reportes financieros automatizados
- ✅ Detección de anomalías en pagos
- ✅ Reconciliación de pagos
- ✅ Análisis de cohortes de suscripciones

**Datos sincronizados**:
- **Customers**: Información de clientes
- **Subscriptions**: Suscripciones activas y canceladas
- **Payments**: Pagos procesados (PaymentIntents)
- **Invoices**: Facturas emitidas
- **Charges**: Cargos individuales
- **Refunds**: Reembolsos
- **Disputes**: Disputas y chargebacks
- **Products**: Productos y servicios
- **Prices**: Precios y planes
- **Coupons**: Cupones y descuentos
- **Events**: Eventos de webhook (opcional)

**Configuración típica**:
```yaml
Source: Stripe → Destination: PostgreSQL/Snowflake/BigQuery
```

**Configuración detallada**:

**Source (Stripe)**:
```json
{
  "client_secret": "sk_live_...",  // API Key desde External Secrets
  "account_id": null,  // Para cuentas conectadas (Connect)
  "start_date": "2024-01-01T00:00:00Z",  // Fecha inicial para sync
  "lookback_window_days": 0,  // Días adicionales para lookback
  "slice_range": 365  // Días por slice para sincronización
}
```

**Integración con tu plataforma existente**:

Ya tienes integración Stripe → QuickBooks en `data/airflow/dags/stripe_product_to_quickbooks_item.py`. Puedes complementarla con Airbyte:

```python
# DAG mejorado: Airbyte sync + QuickBooks integration
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync
from data.airflow.dags.stripe_product_to_quickbooks_item import sync_to_quickbooks

with DAG("stripe_airbyte_to_quickbooks", ...) as dag:
    # 1. Sync desde Stripe a PostgreSQL (Airbyte)
    airbyte_sync = PythonOperator(
        task_id="sync_stripe_to_postgres",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID"),
        },
    )
    
    # 2. Procesar y sincronizar a QuickBooks (tu DAG existente)
    quickbooks_sync = PythonOperator(
        task_id="sync_to_quickbooks",
        python_callable=sync_to_quickbooks,
        # ... tus parámetros existentes
    )
    
    airbyte_sync >> quickbooks_sync
```

**Ventajas**:
- ✅ API completa de Stripe (100+ endpoints)
- ✅ Sincronización incremental por fecha (muy eficiente)
- ✅ Soporte para múltiples modos de sincronización
- ✅ Manejo automático de rate limits
- ✅ Soporte para Stripe Connect (multi-account)
- ✅ Sincronización de eventos históricos

**Limitaciones**:
- ⚠️ Rate limits de Stripe (100 requests/segundo)
- ⚠️ Algunos datos pueden tardar en sincronizarse (disputes)
- ⚠️ Requiere API key con permisos apropiados

**Configuración recomendada**:
- **Sync Frequency**: Cada 1-6 horas (depende del volumen)
- **Incremental Append**: Para pagos y transacciones
- **Full Refresh**: Para productos y precios (cambian menos)

**External Secrets** (ya configurado en tu plataforma):
```yaml
# security/secrets/externalsecrets-airbyte.yaml
- secretKey: stripe_api_key
  remoteRef:
    key: payments/stripe/api_key  # Ya existe en tu vault
```

**Troubleshooting común**:
- **Error: "Invalid API key"**: Verificar que la key tenga permisos de lectura
- **Error: "Rate limit exceeded"**: Reducir frecuencia de sync o usar lookback_window
- **Missing data**: Verificar que `start_date` no sea muy reciente

---

### 3. **HubSpot** (Source)
**Tipo**: CRM / Marketing Automation  
**Categoría**: Sales & Marketing  
**Popularidad**: ⭐⭐⭐⭐  
**Complejidad**: Media

**Casos de Uso**:
- ✅ Sincronizar contactos, deals y empresas a data warehouse
- ✅ Integración con sistemas de email marketing
- ✅ Análisis de funnel de ventas
- ✅ Reportes de ROI de marketing
- ✅ Segmentación de clientes
- ✅ **Integración con ManyChat** (ya tienes workflows en Kestra)
- ✅ Análisis de engagement y conversión

**Datos sincronizados**:
- **Contacts**: Contactos con propiedades personalizadas
- **Companies**: Empresas y organizaciones
- **Deals**: Oportunidades de venta
- **Tickets**: Tickets de soporte
- **Products**: Productos
- **Line Items**: Líneas de productos
- **Quotes**: Cotizaciones
- **Engagements**: Emails, calls, meetings, notes, tasks
- **Marketing Emails**: Emails de marketing
- **Campaigns**: Campañas de marketing
- **Forms**: Formularios y submissions
- **Workflows**: Workflows de automatización

**Configuración típica**:
```yaml
Source: HubSpot → Destination: PostgreSQL/Snowflake/BigQuery
```

**Configuración detallada**:

**Source (HubSpot)**:
```json
{
  "credentials": {
    "credentials_title": "API Key",
    "api_key": "{{ from_external_secrets }}"  // Ya configurado: crm/hubspot/token
  },
  "start_date": "2024-01-01T00:00:00Z",
  "credentials_title": "API Key"
}
```

**Integración con tu plataforma existente**:

Ya tienes integraciones HubSpot en Kestra (`workflow/kestra/flows/hubspot_lead_to_manychat.yaml`). Complementa con Airbyte:

```python
# DAG: HubSpot sync + procesamiento
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync

with DAG("hubspot_analytics_pipeline", ...) as dag:
    # 1. Sync desde HubSpot a PostgreSQL
    hubspot_sync = PythonOperator(
        task_id="sync_hubspot_to_postgres",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_HUBSPOT_POSTGRES_CONNECTION_ID"),
        },
    )
    
    # 2. Procesar datos para analytics (opcional)
    process_analytics = PythonOperator(
        task_id="process_hubspot_analytics",
        python_callable=process_hubspot_data,
    )
    
    hubspot_sync >> process_analytics
```

**Propiedades personalizadas** (ya usas en tu plataforma):
- `interés_producto`: Producto de interés
- `manychat_user_id`: ID de ManyChat
- Cualquier propiedad personalizada se sincroniza automáticamente

**Ventajas**:
- ✅ Acceso completo a API de HubSpot (todos los objetos)
- ✅ Sincronización incremental eficiente
- ✅ Soporte para objetos y propiedades personalizadas
- ✅ Manejo automático de rate limits
- ✅ Sincronización de relaciones (contact → company → deal)
- ✅ Soporte para marketing analytics

**Limitaciones**:
- ⚠️ Rate limits estrictos (100 requests/10 segundos)
- ⚠️ Sincronización inicial puede ser lenta (miles de contactos)
- ⚠️ Algunos objetos requieren API específica (engagements)

**Configuración recomendada**:
- **Sync Frequency**: Cada 6-12 horas (depende de volumen)
- **Incremental Append**: Para contactos, deals, companies
- **Full Refresh**: Para productos y precios
- **Selective Sync**: Sincronizar solo streams necesarios para mejor performance

**External Secrets** (ya configurado):
```yaml
# Ya existe en tu plataforma:
# security/secrets/externalsecrets-hubspot-db.yaml
# crm/hubspot/token en AWS Secrets Manager
```

**Troubleshooting común**:
- **Error: "Rate limit exceeded"**: Aumentar intervalo entre syncs
- **Error: "Invalid API key"**: Verificar token en External Secrets
- **Missing custom properties**: Verificar que existan en HubSpot
- **Slow sync**: Reducir streams sincronizados o usar incremental

---

### 4. **Snowflake** (Destination)
**Tipo**: Data Warehouse  
**Categoría**: Analytics  
**Popularidad**: ⭐⭐⭐⭐⭐  
**Complejidad**: Media-Alta

**Casos de Uso**:
- ✅ Consolidar datos de múltiples fuentes en Snowflake
- ✅ Crear data lake estructurado
- ✅ Alimentar dashboards y BI tools (Grafana, Tableau, Looker)
- ✅ Preparar datos para ML/AI
- ✅ Data warehouse unificado
- ✅ Análisis de grandes volúmenes de datos históricos
- ✅ Compartir datos entre organizaciones (Data Sharing)

**Configuración típica**:
```yaml
Source: Stripe/HubSpot/PostgreSQL → Destination: Snowflake
```

**Configuración detallada**:

**Destination (Snowflake)**:
```json
{
  "host": "xy12345.us-east-1.snowflakecomputing.com",
  "role": "AIRBYTE_ROLE",
  "warehouse": "AIRBYTE_WAREHOUSE",
  "database": "ANALYTICS",
  "schema": "STAGING",
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "jdbc_url_params": "?warehouse=AIRBYTE_WAREHOUSE&role=AIRBYTE_ROLE",
  "loading_method": {
    "method": "S3 Staging",  // o "Internal Staging"
    "s3_bucket_name": "airbyte-staging",
    "s3_bucket_region": "us-east-1",
    "access_key_id": "{{ from_external_secrets }}",
    "secret_access_key": "{{ from_external_secrets }}"
  }
}
```

**Setup en Snowflake**:
```sql
-- Crear usuario y rol
CREATE USER airbyte_user PASSWORD='secure_password';
CREATE ROLE airbyte_role;
GRANT ROLE airbyte_role TO USER airbyte_user;

-- Crear warehouse
CREATE WAREHOUSE airbyte_warehouse
  WITH WAREHOUSE_SIZE = 'XSMALL'
  AUTO_SUSPEND = 60
  AUTO_RESUME = TRUE;

-- Dar permisos
GRANT USAGE ON WAREHOUSE airbyte_warehouse TO ROLE airbyte_role;
GRANT CREATE DATABASE ON ACCOUNT TO ROLE airbyte_role;
GRANT CREATE SCHEMA ON DATABASE ANALYTICS TO ROLE airbyte_role;

-- Crear schema staging
USE DATABASE ANALYTICS;
CREATE SCHEMA IF NOT EXISTS STAGING;
GRANT ALL ON SCHEMA STAGING TO ROLE airbyte_role;
```

**Optimización de Performance**:

1. **Clustering**:
```sql
-- Crear tabla con clustering automático
CREATE TABLE stripe_customers (
  id VARCHAR,
  created TIMESTAMP,
  email VARCHAR,
  ...
) CLUSTER BY (created);
```

2. **File Format Optimization**:
- Usar Parquet para mejor compresión
- Particionar por fecha para queries más rápidas
- Usar VARIANT para JSON flexible

3. **Warehouse Sizing**:
- XSMALL para desarrollo
- SMALL/MEDIUM para producción
- Multi-cluster para alta concurrencia

**Ventajas**:
- ✅ Escalabilidad infinita (separación compute/storage)
- ✅ Particionamiento automático
- ✅ Soporte para múltiples formatos (JSON, Parquet, CSV)
- ✅ Clustering automático
- ✅ Time Travel (historial de datos)
- ✅ Zero-copy cloning (copias instantáneas)
- ✅ Data Sharing entre cuentas

**Limitaciones**:
- ⚠️ Costos pueden ser altos con mucho compute
- ⚠️ Requiere configuración de staging (S3 o interno)
- ⚠️ Setup inicial más complejo que otros destinos

**Costos estimados**:
- Storage: ~$40/TB/mes
- Compute: Basado en warehouse size y tiempo de uso
- **Tip**: Usar auto-suspend para ahorrar costos

**Troubleshooting común**:
- **Error: "Warehouse not found"**: Verificar que el warehouse existe y está activo
- **Slow syncs**: Aumentar warehouse size o usar multi-cluster
- **S3 staging errors**: Verificar permisos de S3 y credenciales

---

### 5. **Google Sheets** (Source)
**Tipo**: Spreadsheet  
**Categoría**: Colaboración  
**Popularidad**: ⭐⭐⭐⭐  
**Complejidad**: Baja

**Casos de Uso**:
- ✅ Sincronizar datos de hojas de cálculo a bases de datos
- ✅ Automatizar reportes manuales
- ✅ Integrar datos de equipos no técnicos
- ✅ Migración de datos desde Excel/Sheets
- ✅ Consolidar datos de múltiples hojas
- ✅ Sincronización de datos de ventas/operaciones manuales
- ✅ Integración con procesos de onboarding

**Configuración típica**:
```yaml
Source: Google Sheets → Destination: PostgreSQL/Snowflake
```

**Configuración detallada**:

**Source (Google Sheets)**:
```json
{
  "spreadsheet_id": "1abc123def456...",
  "credentials": {
    "auth_type": "Service Account",
    "service_account_info": "{{ from_external_secrets }}"
  },
  "names_conversion": true,  // Convertir nombres a snake_case
  "header_row": 1  // Fila de headers
}
```

**Setup de Google Service Account**:

1. **Crear Service Account en Google Cloud**:
```bash
# En Google Cloud Console
# IAM & Admin → Service Accounts → Create Service Account
# Nombre: airbyte-sheets-reader
# Rol: Viewer (mínimo necesario)
```

2. **Crear Key y compartir Sheet**:
```bash
# Crear key JSON
# Descargar y guardar en External Secrets como:
# google/service-account/airbyte-sheets

# Compartir Sheet con email del service account:
# airbyte-sheets-reader@project.iam.gserviceaccount.com
```

3. **Configurar External Secrets**:
```yaml
# security/secrets/externalsecrets-airbyte.yaml
- secretKey: google_service_account_json
  remoteRef:
    key: google/service-account/airbyte-sheets
```

**Estructura de Sheet recomendada**:
- Primera fila: Headers (nombres de columnas)
- Columnas con tipos consistentes
- Sin filas vacías en medio de datos
- Fechas en formato ISO (YYYY-MM-DD)

**Ventajas**:
- ✅ Fácil de usar para usuarios no técnicos
- ✅ Actualización automática cuando cambia la hoja
- ✅ Soporte para múltiples hojas en un spreadsheet
- ✅ No requiere API keys de usuarios finales
- ✅ Soporte para rangos específicos (si es necesario)

**Limitaciones**:
- ⚠️ Rate limits de Google Sheets API (100 requests/100 segundos)
- ⚠️ Sheets muy grandes pueden ser lentos
- ⚠️ Tipos de datos inferidos automáticamente (puede requerir ajustes)
- ⚠️ No soporta cambios incrementales (siempre full refresh)

**Configuración recomendada**:
- **Sync Frequency**: Cada 1-6 horas (depende de frecuencia de cambios)
- **Full Refresh**: Siempre (Sheets no soporta incremental)
- **Validation**: Validar datos después de sync para detectar errores

**Troubleshooting común**:
- **Error: "Permission denied"**: Verificar que el service account tenga acceso al Sheet
- **Error: "Rate limit exceeded"**: Reducir frecuencia de sync
- **Datos incorrectos**: Verificar formato de datos en Sheet (fechas, números, etc.)
- **Missing rows**: Verificar que no haya filas vacías en medio de datos

---

### 6. **MySQL** (Source & Destination)
**Tipo**: Database  
**Categoría**: Base de datos relacional  
**Popularidad**: ⭐⭐⭐⭐  
**Complejidad**: Media

**Casos de Uso**:
- ✅ Migración de datos desde/a MySQL
- ✅ Sincronización entre MySQL y PostgreSQL
- ✅ Consolidación de bases de datos MySQL
- ✅ Backup incremental
- ✅ CDC para sincronización en tiempo real
- ✅ Migración desde sistemas legacy
- ✅ Sincronización multi-región

**Configuración típica**:
```yaml
Source: MySQL → Destination: PostgreSQL/Snowflake/BigQuery
```

**Configuración detallada**:

**Source (MySQL)**:
```json
{
  "host": "mysql.example.com",
  "port": 3306,
  "database": "production_db",
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "replication_method": {
    "method": "CDC",  // o "STANDARD" para full/incremental
    "initial_waiting_seconds": 300,
    "server_timezone": "UTC"
  },
  "ssl": true,
  "tunnel_method": null  // o SSH si requiere
}
```

**CDC Setup (Requisitos)**:
```sql
-- En MySQL source
-- 1. Habilitar binlog
SET GLOBAL binlog_format = 'ROW';
SET GLOBAL binlog_row_image = 'FULL';

-- 2. Crear usuario con permisos de replicación
CREATE USER 'airbyte_user'@'%' IDENTIFIED BY 'secure_password';
GRANT SELECT, RELOAD, SHOW DATABASES, REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'airbyte_user'@'%';
FLUSH PRIVILEGES;

-- 3. Verificar configuración
SHOW VARIABLES LIKE 'log_bin';
SHOW VARIABLES LIKE 'binlog_format';
```

**Destination (MySQL)**:
```json
{
  "host": "mysql-warehouse.example.com",
  "port": 3306,
  "database": "data_warehouse",
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "ssl": true
}
```

**Ventajas**:
- ✅ Soporte para binlog (CDC en tiempo real)
- ✅ Sincronización incremental eficiente
- ✅ Alta compatibilidad con aplicaciones legacy
- ✅ Soporte para múltiples motores (InnoDB, MyISAM)
- ✅ Bajo overhead en source database

**Limitaciones**:
- ⚠️ CDC requiere configuración de binlog
- ⚠️ Requiere permisos de replicación
- ⚠️ Puede ser lento para full refresh en tablas grandes
- ⚠️ Algunos tipos de datos pueden requerir transformación

**Recursos recomendados**:
- CPU: 2-4 cores para CDC
- Memoria: 4-8GB para workers
- Storage: Depende del volumen de datos

**Troubleshooting común**:
- **Error: "Binlog not enabled"**: Habilitar binlog en MySQL
- **Error: "Access denied for replication"**: Verificar permisos de replicación
- **Error: "Binlog format not ROW"**: Cambiar a ROW format
- **Slow sync**: Verificar índices, usar CDC en lugar de full refresh
- **Connection timeout**: Verificar `wait_timeout` y `interactive_timeout` en MySQL

**Migración desde MySQL Legacy**:
```python
# DAG: Migración MySQL → PostgreSQL
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync

with DAG("mysql_migration", ...) as dag:
    # 1. Sync inicial (full)
    initial_sync = PythonOperator(
        task_id="initial_mysql_sync",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_MYSQL_PG_CONNECTION_ID"),
            "timeout_minutes": 480,  # 8 horas para migración completa
        },
    )
    
    # 2. Validar datos
    validate = PythonOperator(
        task_id="validate_migration",
        python_callable=validate_migration_data,
    )
    
    initial_sync >> validate
```

---

### 7. **Salesforce** (Source)
**Tipo**: CRM  
**Categoría**: Sales & Marketing  
**Popularidad**: ⭐⭐⭐⭐  
**Complejidad**: Media-Alta

**Casos de Uso**:
- ✅ Sincronizar Leads, Opportunities, Accounts
- ✅ Integración con sistemas de BI
- ✅ Análisis de pipeline de ventas
- ✅ Reportes de gestión de clientes
- ✅ Integración con sistemas contables
- ✅ Consolidación con otros CRMs (HubSpot, etc.)
- ✅ Análisis de conversión de leads

**Datos sincronizados**:
- **Standard Objects**: Leads, Contacts, Accounts, Opportunities, Cases, Tasks, Events, Campaigns
- **Custom Objects**: Cualquier objeto personalizado (SOQL)
- **Relationships**: Relaciones entre objetos (Lookup, Master-Detail)
- **History**: History tracking (Field History, Account History)
- **Attachments**: Attachments y Files (opcional)

**Configuración típica**:
```yaml
Source: Salesforce → Destination: PostgreSQL/Snowflake
```

**Configuración detallada**:

**Source (Salesforce)**:
```json
{
  "client_id": "{{ from_external_secrets }}",
  "client_secret": "{{ from_external_secrets }}",
  "refresh_token": "{{ from_external_secrets }}",
  "auth_type": "Client",
  "is_sandbox": false,  // true para sandbox
  "start_date": "2024-01-01T00:00:00Z",
  "api_type": "REST",  // o "BULK" para grandes volúmenes
  "streams_criteria": [
    {
      "criteria": "starts with",
      "value": "Account"
    }
  ]
}
```

**Setup de Salesforce OAuth**:

1. **Crear Connected App en Salesforce**:
```
Setup → App Manager → New Connected App
- Name: Airbyte Integration
- API Name: Airbyte_Integration
- Enable OAuth Settings: Yes
- Callback URL: https://airbyte.example.com/oauth/callback
- Selected OAuth Scopes:
  - Access and manage your data (api)
  - Perform requests on your behalf at any time (refresh_token, offline_access)
```

2. **Obtener Refresh Token**:
```bash
# Usar OAuth flow o Postman para obtener refresh token
# Guardar en External Secrets como: crm/salesforce/refresh_token
```

3. **Configurar External Secrets**:
```yaml
# security/secrets/externalsecrets-airbyte.yaml
- secretKey: salesforce_client_id
  remoteRef:
    key: crm/salesforce/client_id
- secretKey: salesforce_client_secret
  remoteRef:
    key: crm/salesforce/client_secret
- secretKey: salesforce_refresh_token
  remoteRef:
    key: crm/salesforce/refresh_token
```

**API Types**:
- **REST API**: Para objetos pequeños/medianos (hasta 10K records)
- **Bulk API**: Para objetos grandes (más de 10K records, más rápido)

**Custom Objects**:
```json
// Configurar en streams_criteria para incluir objetos personalizados
{
  "streams_criteria": [
    {
      "criteria": "starts with",
      "value": "Custom__c"  // Todos los objetos que empiecen con "Custom"
    }
  ]
}
```

**Ventajas**:
- ✅ Acceso completo a objetos y campos personalizados
- ✅ Sincronización incremental eficiente
- ✅ Soporte para Bulk API (alta performance)
- ✅ Manejo automático de rate limits
- ✅ Soporte para relaciones entre objetos
- ✅ Sincronización de field history

**Limitaciones**:
- ⚠️ Rate limits estrictos (REST: 15K/day, Bulk: 10K/hour)
- ⚠️ Setup de OAuth más complejo
- ⚠️ Sincronización inicial puede ser muy lenta (miles de objetos)
- ⚠️ Algunos objetos requieren permisos especiales

**Configuración recomendada**:
- **Sync Frequency**: Cada 6-12 horas (depende de volumen)
- **API Type**: BULK para objetos grandes, REST para pequeños
- **Incremental Append**: Para objetos que cambian frecuentemente
- **Full Refresh**: Para objetos de referencia (cambian poco)

**Troubleshooting común**:
- **Error: "Invalid refresh token"**: Regenerar refresh token
- **Error: "Rate limit exceeded"**: Reducir frecuencia o usar Bulk API
- **Error: "Insufficient access"**: Verificar permisos del usuario OAuth
- **Missing custom objects**: Verificar streams_criteria y permisos
- **Slow sync**: Usar Bulk API para objetos grandes

---

### 8. **Amazon S3** (Destination)
**Tipo**: Object Storage  
**Categoría**: Data Lake  
**Popularidad**: ⭐⭐⭐⭐⭐  
**Complejidad**: Baja

**Casos de Uso**:
- ✅ Crear data lake en S3
- ✅ Almacenar datos en formato Parquet/JSON
- ✅ Preparar datos para procesamiento con Spark/Athena
- ✅ Backup de datos a largo plazo
- ✅ Integración con AWS Glue
- ✅ Alimentar Databricks (ya tienes en tu plataforma)
- ✅ Data lake para ML/AI pipelines

**Configuración típica**:
```yaml
Source: Cualquier fuente → Destination: S3
```

**Configuración detallada**:

**Destination (S3)**:
```json
{
  "s3_bucket_name": "biz-datalake-dev",  // Ya configurado en platform.yaml
  "s3_bucket_path": "airbyte/{source}/{stream}/",
  "s3_bucket_region": "us-east-1",
  "access_key_id": "{{ from_external_secrets }}",
  "secret_access_key": "{{ from_external_secrets }}",
  "s3_path_format": "${NAMESPACE}/${STREAM_NAME}/${YEAR}_${MONTH}_${DAY}_${EPOCH}",
  "format": {
    "format_type": "Parquet",
    "compression_codec": "snappy",
    "block_size_mb": 128,
    "max_padding_size_mb": 8,
    "page_size_kb": 1024,
    "dictionary_page_size_kb": 1024,
    "dictionary_encoding": true
  },
  "part_size": 10
}
```

**Estructura de archivos recomendada**:
```
s3://biz-datalake-dev/
  airbyte/
    stripe/
      customers/
        2025/01/15/1234567890_00001.parquet
        2025/01/15/1234567891_00002.parquet
      payments/
        2025/01/15/1234567892_00001.parquet
    hubspot/
      contacts/
        2025/01/15/1234567893_00001.parquet
```

**Integración con tu plataforma**:

Ya tienes `dataLake.type: s3` y `bucketName: biz-datalake-dev` en `platform.yaml`. Configuración:

```python
# DAG: S3 Data Lake Pipeline
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync

with DAG("s3_datalake_pipeline", ...) as dag:
    # Sync múltiples fuentes a S3
    stripe_to_s3 = PythonOperator(
        task_id="sync_stripe_to_s3",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_S3_CONNECTION_ID"),
        },
    )
    
    hubspot_to_s3 = PythonOperator(
        task_id="sync_hubspot_to_s3",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_HUBSPOT_S3_CONNECTION_ID"),
        },
    )
    
    # Procesar con Spark/Databricks (ya tienes Databricks configurado)
    process_with_databricks = DatabricksRunNowOperator(
        task_id="process_datalake",
        job_id=Variable.get("DATABRICKS_DATALAKE_JOB_ID"),
    )
    
    [stripe_to_s3, hubspot_to_s3] >> process_with_databricks
```

**Formatos soportados**:
- **Parquet**: Recomendado para analytics (mejor compresión, columnar)
- **JSON**: Flexible pero menos eficiente
- **CSV**: Simple pero sin tipos de datos
- **Avro**: Bueno para streaming

**Optimización de S3**:

1. **Particionamiento**:
```json
"s3_path_format": "${NAMESPACE}/${STREAM_NAME}/${YEAR}/${MONTH}/${DAY}"
```

2. **Compresión**:
- Parquet con Snappy: Balance entre velocidad y tamaño
- Gzip: Mejor compresión pero más lento
- Sin compresión: Más rápido pero más costoso

3. **Lifecycle Policies**:
```json
// En AWS S3, configurar lifecycle para mover a Glacier después de 90 días
{
  "Rules": [{
    "Id": "Move to Glacier",
    "Status": "Enabled",
    "Transitions": [{
      "Days": 90,
      "StorageClass": "GLACIER"
    }]
  }]
}
```

**Ventajas**:
- ✅ Costo muy bajo para almacenamiento (~$0.023/GB/mes)
- ✅ Escalabilidad ilimitada
- ✅ Integración nativa con ecosistema AWS
- ✅ Soporte para múltiples formatos
- ✅ Integración con Athena para queries SQL
- ✅ Compatible con Databricks (ya tienes configurado)

**Limitaciones**:
- ⚠️ Solo append (no soporta updates/deletes)
- ⚠️ Queries directas requieren herramientas adicionales (Athena, Spark)
- ⚠️ Costos de transferencia si se accede frecuentemente

**Costos estimados**:
- Storage: $0.023/GB/mes (Standard)
- Requests: $0.005/1000 PUT requests
- Transfer: $0.09/GB (outbound)
- **Tip**: Usar Intelligent-Tiering para ahorrar

**External Secrets** (ya configurado):
```yaml
# Usar credenciales AWS existentes
# security/secrets/externalsecrets-aws.yaml
```

**Troubleshooting común**:
- **Error: "Access Denied"**: Verificar IAM permissions del bucket
- **Error: "Bucket not found"**: Verificar nombre y región
- **Slow uploads**: Aumentar `part_size` o usar multipart upload
- **High costs**: Verificar lifecycle policies y usar compression

---

### 9. **MongoDB** (Source & Destination)
**Tipo**: NoSQL Database  
**Categoría**: Document Database  
**Popularidad**: ⭐⭐⭐  
**Complejidad**: Media-Alta

**Casos de Uso**:
- ✅ Sincronizar colecciones de MongoDB
- ✅ Migración a bases de datos relacionales
- ✅ Consolidar datos de múltiples colecciones
- ✅ Backup incremental
- ✅ CDC usando Oplog
- ✅ Sincronización de documentos anidados
- ✅ Flattening de estructuras JSON complejas

**Configuración típica**:
```yaml
Source: MongoDB → Destination: PostgreSQL/Snowflake
```

**Configuración detallada**:

**Source (MongoDB)**:
```json
{
  "instance_type": "standalone",  // o "replica", "atlas"
  "host": "mongodb.example.com",
  "port": 27017,
  "database": "production_db",
  "auth_type": "login/password",
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "replication_method": {
    "method": "CDC",  // o "STANDARD" para full/incremental
    "replication_slot": "airbyte_slot"
  },
  "ssl": true,
  "tunnel_method": null
}
```

**CDC Setup (Requisitos)**:

1. **Habilitar Replica Set** (requerido para CDC):
```javascript
// MongoDB debe estar en modo replica set (aunque sea de 1 nodo)
// Iniciar con: mongod --replSet rs0

// En mongo shell:
rs.initiate({
  _id: "rs0",
  members: [{ _id: 0, host: "localhost:27017" }]
});
```

2. **Crear Usuario con Permisos**:
```javascript
use admin;
db.createUser({
  user: "airbyte_user",
  pwd: "secure_password",
  roles: [
    { role: "read", db: "production_db" },
    { role: "readAnyDatabase", db: "admin" }
  ]
});
```

3. **Verificar Oplog**:
```javascript
// Verificar que oplog está habilitado
use local;
db.oplog.rs.find().limit(1);
```

**Destination (PostgreSQL con JSON)**:
```json
{
  "host": "postgres.example.com",
  "port": 5432,
  "database": "analytics",
  "schema": "mongodb_raw",
  "username": "airbyte_user",
  "password": "{{ from_external_secrets }}",
  "ssl": true
}
```

**Flattening de Documentos**:
- Airbyte automáticamente "aplana" documentos anidados
- Arrays se convierten en tablas separadas
- Nested objects se convierten en columnas con prefijo

**Ejemplo de Transformación**:
```javascript
// Documento MongoDB original:
{
  _id: ObjectId("..."),
  name: "John",
  address: {
    street: "123 Main",
    city: "NYC"
  },
  orders: [
    { id: 1, amount: 100 },
    { id: 2, amount: 200 }
  ]
}

// Se convierte en PostgreSQL:
// Tabla: users
// _id, name, address_street, address_city

// Tabla: users_orders (array flattening)
// _id, orders_id, orders_amount
```

**Ventajas**:
- ✅ Soporte para CDC usando Oplog (cambio en tiempo real)
- ✅ Sincronización incremental eficiente
- ✅ Manejo de documentos anidados
- ✅ Flattening automático de estructuras complejas
- ✅ Soporte para MongoDB Atlas (cloud)

**Limitaciones**:
- ⚠️ CDC requiere Replica Set (no funciona con standalone)
- ⚠️ Flattening puede crear muchas tablas para documentos complejos
- ⚠️ Pérdida de estructura original en algunos casos
- ⚠️ Arrays grandes pueden causar problemas de performance

**Configuración recomendada**:
- **Sync Frequency**: Cada 1-6 horas (depende de volumen)
- **CDC**: Usar si necesitas cambios en tiempo real
- **Selective Sync**: Sincronizar solo colecciones necesarias
- **Flattening**: Revisar estructura resultante antes de producción

**Recursos recomendados**:
- CPU: 2-4 cores para CDC
- Memoria: 4-8GB (depende de tamaño de documentos)
- Storage: Variable según colecciones

**Troubleshooting común**:
- **Error: "Not a replica set"**: Configurar replica set (aunque sea de 1 nodo)
- **Error: "Oplog not found"**: Verificar que oplog está habilitado
- **Error: "Too many tables"**: Reducir colecciones sincronizadas
- **Slow sync**: Verificar índices en MongoDB, usar selective sync
- **Memory issues**: Reducir tamaño de batch o documentos sincronizados

---

### 10. **REST API** (Source)
**Tipo**: Generic API  
**Categoría**: Custom Integration  
**Popularidad**: ⭐⭐⭐⭐  
**Complejidad**: Media-Alta

**Casos de Uso**:
- ✅ Sincronizar datos de cualquier API REST
- ✅ Integrar APIs personalizadas
- ✅ Sincronizar datos de servicios SaaS
- ✅ Crear conectores personalizados sin código
- ✅ Integración con sistemas legacy
- ✅ Webhooks a base de datos
- ✅ Consolidador de múltiples APIs

**Configuración típica**:
```yaml
Source: REST API → Destination: PostgreSQL/Snowflake/S3
```

**Configuración detallada**:

**Source (REST API)**:
```json
{
  "url_base": "https://api.example.com/v1",
  "http_method": "GET",
  "headers": {
    "Authorization": "Bearer {{ from_external_secrets }}",
    "Content-Type": "application/json"
  },
  "authenticator": {
    "type": "Bearer Token",
    "api_token": "{{ from_external_secrets }}"
  },
  "request_params": {
    "page": "{{ page_number }}",
    "per_page": 100
  },
  "pagination": {
    "type": "page",
    "page_size": 100,
    "page_size_param": "per_page",
    "page_number_param": "page"
  },
  "streams": [
    {
      "name": "customers",
      "path": "/customers",
      "primary_key": ["id"],
      "cursor_field": "updated_at"
    },
    {
      "name": "orders",
      "path": "/orders",
      "primary_key": ["id"],
      "cursor_field": "created_at"
    }
  ]
}
```

**Tipos de Autenticación**:
- **Bearer Token**: `Authorization: Bearer <token>`
- **API Key**: En header o query params
- **Basic Auth**: `Authorization: Basic <base64>`
- **OAuth 2.0**: Client credentials flow
- **Custom**: Headers personalizados

**Tipos de Paginación**:
- **Page-based**: `/items?page=1&per_page=100`
- **Offset-based**: `/items?offset=0&limit=100`
- **Cursor-based**: `/items?cursor=abc123`
- **Header-based**: Links en headers (RFC 5988)

**Ejemplo: API con OAuth**:
```json
{
  "url_base": "https://api.example.com",
  "authenticator": {
    "type": "OAuth2.0",
    "client_id": "{{ from_external_secrets }}",
    "client_secret": "{{ from_external_secrets }}",
    "token_refresh_endpoint": "https://api.example.com/oauth/token",
    "access_token": "{{ auto_refreshed }}",
    "refresh_token": "{{ from_external_secrets }}"
  },
  "streams": [
    {
      "name": "data",
      "path": "/api/data",
      "primary_key": ["id"]
    }
  ]
}
```

**Ejemplo: API con Paginación Cursor**:
```json
{
  "pagination": {
    "type": "cursor",
    "cursor_value": "{{ response.next_cursor }}",
    "cursor_field": "cursor",
    "stop_condition": "{{ response.next_cursor == null }}"
  }
}
```

**Transformación de Datos**:
```json
{
  "streams": [
    {
      "name": "customers",
      "path": "/customers",
      "schema": {
        "properties": {
          "id": {"type": "string"},
          "name": {"type": "string"},
          "created_at": {"type": "string", "format": "date-time"}
        }
      },
      "transform": {
        "rename": {
          "created_at": "created_date"
        },
        "cast": {
          "created_date": "timestamp"
        }
      }
    }
  ]
}
```

**Ventajas**:
- ✅ Flexibilidad máxima (cualquier API REST)
- ✅ Configuración mediante JSON (no requiere código)
- ✅ Soporte para múltiples tipos de autenticación
- ✅ Paginación automática
- ✅ Transformación de datos básica
- ✅ Soporte para múltiples streams en una conexión

**Limitaciones**:
- ⚠️ Requiere conocimiento de la API específica
- ⚠️ Transformaciones complejas pueden requerir código
- ⚠️ Rate limits dependen de la API
- ⚠️ Cambios en la API pueden romper la sincronización
- ⚠️ No todos los tipos de APIs son soportados

**Configuración recomendada**:
- **Sync Frequency**: Depende de la API (cada 1-24 horas)
- **Pagination**: Configurar correctamente para evitar datos faltantes
- **Error Handling**: Configurar retries y backoff
- **Validation**: Validar estructura de respuesta después de sync

**Troubleshooting común**:
- **Error: "Authentication failed"**: Verificar credenciales y tipo de auth
- **Error: "Pagination not working"**: Verificar configuración de paginación
- **Error: "Rate limit exceeded"**: Reducir frecuencia o implementar backoff
- **Missing data**: Verificar que paginación capture todos los datos
- **Schema errors**: Verificar estructura de respuesta de la API

**Ejemplo: Integrar API Interna**:
```python
# DAG: Sync desde API interna
with DAG("internal_api_sync", ...) as dag:
    sync = PythonOperator(
        task_id="sync_internal_api",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_INTERNAL_API_CONNECTION_ID"),
        },
    )
```

---

## 📈 Tabla Comparativa

| Conector | Tipo | Popularidad | Casos de Uso Comunes |
|----------|------|-------------|---------------------|
| PostgreSQL | Database | ⭐⭐⭐⭐⭐ | Migración, CDC, Consolidación |
| Stripe | Payment | ⭐⭐⭐⭐⭐ | Finanzas, E-commerce, Analytics |
| HubSpot | CRM | ⭐⭐⭐⭐ | Sales, Marketing, Analytics |
| Snowflake | Data Warehouse | ⭐⭐⭐⭐⭐ | Analytics, BI, ML |
| Google Sheets | Spreadsheet | ⭐⭐⭐⭐ | Colaboración, Reportes |
| MySQL | Database | ⭐⭐⭐⭐ | Migración, Legacy Systems |
| Salesforce | CRM | ⭐⭐⭐⭐ | Sales, Customer Management |
| S3 | Storage | ⭐⭐⭐⭐⭐ | Data Lake, Backup |
| MongoDB | NoSQL | ⭐⭐⭐ | Document Sync, Migration |
| REST API | Generic | ⭐⭐⭐⭐ | Custom Integration |

## 🎯 Casos de Uso Comunes para tu Plataforma

### 1. **Sincronización Financiera**
```
Stripe → PostgreSQL → QuickBooks Integration
```
- Sincronizar pagos de Stripe
- Procesar en PostgreSQL
- Integrar con QuickBooks (ya tienes DAG para esto)

### 2. **CRM Analytics**
```
HubSpot + Salesforce → Snowflake → BI Tools
```
- Consolidar datos de múltiples CRMs
- Analizar pipeline unificado
- Dashboards en Grafana

### 3. **Data Lake Pipeline**
```
Stripe + HubSpot + PostgreSQL → S3 → Databricks/Spark
```
- Almacenar datos en S3
- Procesar con Spark/Databricks
- Preparar para ML

### 4. **Real-time Sync**
```
PostgreSQL (Source) → PostgreSQL (Destination)
```
- CDC para sincronización en tiempo real
- Multi-región replication
- Backup automático

### 5. **Legacy Migration**
```
MySQL → PostgreSQL → Snowflake
```
- Migrar desde MySQL legacy
- Transformar en PostgreSQL
- Cargar en Snowflake para analytics

## 🔧 Configuración Rápida y Avanzada

### Ejemplo Completo: Stripe → PostgreSQL → QuickBooks

**Paso 1: Crear Source (Stripe) en Airbyte UI**

1. Ir a **Sources** → **New Source** → **Stripe**
2. Configurar:
   - **API Key**: Desde External Secrets (`payments/stripe/api_key`)
   - **Start Date**: `2024-01-01T00:00:00Z` (o fecha inicial)
   - **Account ID**: Dejar vacío (o para Connect accounts)
3. **Test Connection** → Verificar que funciona
4. **Save** con nombre: `Stripe Production`

**Paso 2: Crear Destination (PostgreSQL) en Airbyte UI**

1. Ir a **Destinations** → **New Destination** → **PostgreSQL**
2. Configurar:
   ```json
   {
     "host": "postgres.data.svc.cluster.local",
     "port": 5432,
     "database": "analytics",
     "schema": "stripe_raw",
     "username": "airbyte_user",
     "password": "{{ from_external_secrets }}",
     "ssl": true,
     "tunnel_method": null
   }
   ```
3. **Test Connection** → Verificar
4. **Save** con nombre: `PostgreSQL Analytics`

**Paso 3: Crear Connection en Airbyte UI**

1. Ir a **Connections** → **New Connection**
2. Seleccionar:
   - **Source**: `Stripe Production`
   - **Destination**: `PostgreSQL Analytics`
3. Configurar **Streams**:
   - Seleccionar streams necesarios:
     - ✅ `customers`
     - ✅ `subscriptions`
     - ✅ `payment_intents` (payments)
     - ✅ `invoices`
     - ✅ `charges`
     - ✅ `refunds`
     - ✅ `products`
     - ✅ `prices`
   - **Namespace**: `stripe_raw` (o el schema que prefieras)
   - **Stream Prefix**: (opcional) `stripe_`
4. Configurar **Sync Mode**:
   - **Customers**: Incremental Append (por `created`)
   - **Payment Intents**: Incremental Append (por `created`)
   - **Products**: Full Refresh (cambian poco)
   - **Invoices**: Incremental Append
5. Configurar **Frequency**:
   - **Schedule Type**: Scheduled
   - **Cron Expression**: `0 */6 * * *` (cada 6 horas)
   - O usar **Manual** y trigger desde Airflow
6. **Save & Run** para primera sincronización

**Paso 4: Obtener Connection ID**

```bash
# Desde API
curl -u username:password \
  http://airbyte-server.integration.svc.cluster.local:8000/api/v1/connections/list \
  | jq '.data[] | select(.name=="Stripe to PostgreSQL") | .connectionId'

# O desde UI: URL contiene el connection ID
```

**Paso 5: Integrar con Airflow**

```python
# data/airflow/dags/stripe_airbyte_quickbooks.py
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from data.airflow.dags.airbyte_sync import trigger_airbyte_sync
from data.airflow.dags.stripe_product_to_quickbooks_item import sync_to_quickbooks

with DAG(
    dag_id="stripe_airbyte_to_quickbooks",
    description="Sync Stripe → PostgreSQL (Airbyte) → QuickBooks",
    schedule_interval=timedelta(hours=6),
    default_args={
        "owner": "data-engineering",
        "retries": 2,
    },
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["stripe", "airbyte", "quickbooks", "finance"],
) as dag:
    
    # 1. Sync desde Stripe a PostgreSQL usando Airbyte
    airbyte_sync = PythonOperator(
        task_id="sync_stripe_to_postgres",
        python_callable=trigger_airbyte_sync,
        op_kwargs={
            "connection_id": Variable.get("AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID"),
            "timeout_minutes": 180,
            "validate_connection": True,
        },
    )
    
    # 2. Procesar y sincronizar a QuickBooks
    # (Usar tu lógica existente de stripe_product_to_quickbooks_item.py)
    quickbooks_sync = PythonOperator(
        task_id="sync_to_quickbooks",
        python_callable=sync_to_quickbooks,
        op_kwargs={
            # Tus parámetros existentes
        },
    )
    
    # Dependencias
    airbyte_sync >> quickbooks_sync
```

**Paso 6: Configurar Variables en Airflow**

```python
# En Airflow UI → Admin → Variables
AIRBYTE_STRIPE_POSTGRES_CONNECTION_ID = "abc-123-def-456"
```

**Paso 7: Verificar y Monitorear**

```bash
# Ver logs de sincronización en Airbyte UI
# Ver logs en Airflow
# Verificar datos en PostgreSQL
psql -h postgres.data.svc.cluster.local -d analytics -c \
  "SELECT COUNT(*) FROM stripe_raw.customers;"
```

## 📚 Recursos Adicionales

- **Lista completa de conectores**: https://docs.airbyte.com/integrations/
- **Documentación de cada conector**: https://docs.airbyte.com/integrations/sources/
- **Guías de configuración**: https://docs.airbyte.com/operator-guides/
- **Troubleshooting**: https://docs.airbyte.com/troubleshooting/

## 🚀 Próximos Pasos Recomendados

### Para tu Plataforma

1. **Configurar Stripe → PostgreSQL**:
   - ✅ Ya tienes Stripe API key configurado
   - ✅ Ya tienes integración QuickBooks
   - 🔄 Crear conexión Airbyte para sincronizar datos históricos
   - 🔄 Integrar con tu DAG existente

2. **Configurar HubSpot → PostgreSQL**:
   - ✅ Ya tienes HubSpot token configurado
   - ✅ Ya tienes workflows en Kestra
   - 🔄 Crear conexión Airbyte para analytics
   - 🔄 Consolidar datos de HubSpot para análisis

3. **Configurar PostgreSQL CDC**:
   - 🔄 Para sincronización en tiempo real
   - 🔄 Para backup incremental
   - 🔄 Para multi-región replication

4. **Monitorear**:
   - 🔄 Configurar dashboards en Grafana
   - 🔄 Alertas en Prometheus
   - 🔄 Logs estructurados en Loki

## 📊 Métricas y Monitoreo

### Métricas Clave por Conector

**Stripe**:
- Número de registros sincronizados (customers, payments)
- Tiempo de sincronización
- Errores de rate limit
- Lag de datos (diferencia entre creación y sync)

**HubSpot**:
- Número de contactos/deals sincronizados
- Tiempo de sincronización
- Errores de rate limit
- Actualización de propiedades personalizadas

**PostgreSQL**:
- Velocidad de sincronización (records/segundo)
- Lag de CDC (para replicación)
- Tamaño de WAL logs
- Uso de replication slots

### Dashboard de Grafana

Crear dashboard con:
- Tasa de éxito de sincronizaciones
- Tiempo promedio de sincronización
- Volumen de datos sincronizados
- Errores y retries
- Uso de recursos (CPU/memoria)

## ⚠️ Troubleshooting Avanzado

### Problemas Comunes y Soluciones

**1. Rate Limits (Stripe/HubSpot)**:
```python
# Solución: Reducir frecuencia o usar lookback window
# En Airbyte: Configurar lookback_window_days
# En Airflow: Aumentar intervalo entre syncs
```

**2. Timeout en Sincronizaciones Grandes**:
```python
# Solución: Aumentar timeout en Airflow
trigger_airbyte_sync(
    connection_id="...",
    timeout_minutes=360,  # 6 horas para syncs grandes
)
```

**3. Datos Faltantes**:
- Verificar `start_date` en source
- Verificar filtros en streams
- Verificar permisos de API key
- Verificar logs de Airbyte para errores específicos

**4. CDC No Funciona (PostgreSQL)**:
```sql
-- Verificar replication slot
SELECT * FROM pg_replication_slots;

-- Verificar WAL retention
SHOW wal_keep_size;

-- Verificar permisos
\du airbyte_user
```

## 💰 Costos y Recursos

### Estimación de Recursos por Conector

| Conector | Workers | CPU | Memoria | Storage |
|----------|---------|-----|---------|---------|
| Stripe | 1-2 | 1-2 cores | 2-4GB | N/A |
| HubSpot | 1-2 | 1-2 cores | 2-4GB | N/A |
| PostgreSQL (Source) | 1 | 2-4 cores | 4-8GB | N/A |
| PostgreSQL (Dest) | 1 | 2-4 cores | 4-8GB | Variable |
| Snowflake | 1 | 1-2 cores | 2-4GB | N/A |
| S3 | 1 | 1 core | 2GB | Variable |

**Nota**: Los recursos dependen del volumen de datos. Ajustar según necesidades.

### Costos de Destinos

- **PostgreSQL**: Costo de instancia (si es managed)
- **Snowflake**: Basado en compute credits y storage
- **S3**: Muy bajo (~$0.023/GB/mes)
- **BigQuery**: Basado en queries y storage

## 🔐 Seguridad y Mejores Prácticas

### Mejores Prácticas

1. **Credenciales**:
   - ✅ Usar External Secrets siempre
   - ✅ Rotar credenciales regularmente
   - ✅ Usar permisos mínimos necesarios
   - ✅ No hardcodear en código

2. **NetworkPolicies**:
   - ✅ Ya configuradas en `security/networkpolicies/airbyte.yaml`
   - ✅ Restringir acceso solo a servicios necesarios

3. **Monitoreo**:
   - ✅ Alertas en fallos de sincronización
   - ✅ Alertas en rate limits
   - ✅ Alertas en timeouts
   - ✅ Dashboard de métricas

4. **Backup**:
   - ✅ Backup de configuración de Airbyte
   - ✅ Backup de metadata de conexiones
   - ✅ Backup de datos en destinos

## 📚 Referencias Adicionales

- **Documentación oficial**: https://docs.airbyte.com/
- **Guías de conectores**: https://docs.airbyte.com/integrations/sources/
- **API Reference**: https://airbyte-public-api-docs.s3.us-east-2.amazonaws.com/rapidoc-api-docs.html
- **Troubleshooting**: https://docs.airbyte.com/troubleshooting/
- **Comunidad**: https://airbyte.com/community

---

**Nota**: Estos conectores son los más populares según la comunidad de Airbyte y casos de uso comunes en empresas. La elección final depende de tus necesidades específicas.

**Última actualización**: 2025-01-15  
**Versión del documento**: 2.0

## 📖 Documentación Relacionada

- **Arquitecturas y Ejemplos Avanzados**: Ver `AIRBYTE_ARCHITECTURE_EXAMPLES.md`
  - Diagramas de arquitectura completos
  - Patterns de integración (fan-out, fan-in, pipeline en cadena)
  - Casos de uso avanzados con código
  - Performance tuning
  - Ejemplos de ETL con validación
  - Sincronización condicional y event-driven

- **Guía Completa de Airbyte**: `README_AIRBYTE.md`
- **Mejoras Implementadas**: `IMPROVEMENTS_AIRBYTE.md`
- **Quick Start**: `QUICK_START_AIRBYTE.md`

