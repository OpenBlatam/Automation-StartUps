# Organización de DAGs por Área de Negocio

Este directorio contiene todos los DAGs de Airflow organizados por área de la empresa y funcionalidad.

📋 **Documentación disponible**:
- 🚀 [QUICK_START.md](QUICK_START.md) - **Empieza aquí** - Guía de inicio rápido
- 📁 [STRUCTURE.md](STRUCTURE.md) - Estructura visual completa
- 🔍 [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Referencia rápida de DAGs
- 📑 [DAG_INDEX.md](DAG_INDEX.md) - Índice alfabético completo de DAGs
- 📚 [BEST_PRACTICES.md](BEST_PRACTICES.md) - Mejores prácticas y guías
- 🔗 [DAG_DEPENDENCIES.md](DAG_DEPENDENCIES.md) - Mapa de dependencias entre DAGs
- 📊 [STATISTICS.md](STATISTICS.md) - Estadísticas detalladas

🛠️ **Scripts de utilidad**:
- [find_dag.sh](find_dag.sh) - Buscar DAGs rápidamente
- [generate_dag_template.sh](generate_dag_template.sh) - Generar template para nuevo DAG
- [validate_structure.sh](validate_structure.sh) - Validar estructura y organización
- [generate_report.sh](generate_report.sh) - Generar reporte de DAGs
- [load_config.py](load_config.py) - Cargar configuración centralizada

⚙️ **Configuración y Mantenimiento**:
- [dag_config.yaml](dag_config.yaml) - Configuración centralizada
- [MAINTENANCE.md](MAINTENANCE.md) - Guía de mantenimiento
- [CHANGELOG.md](CHANGELOG.md) - Registro de cambios

## Estructura de Carpetas

### 📊 **sales_marketing/** - Ventas y Marketing
- **leads/** - Captura y gestión de leads
  - `web_lead_capture.py`, `organic_acquisition_nurturing.py`, `lead_*.py`
- **outreach/** - Campañas de outreach y seguimiento
  - `outreach_multichannel.py`, `post_event_followup.py`
- **social_media/** - Automatización de redes sociales
  - `social_media_automation.py`
- **content_marketing/** - Automatización de contenido
  - `content_marketing_automation.py`
- **ads_reporting/** - Reportes de publicidad
  - `ads_reporting*.py`, `facebook_ads_reporting.py`, `google_ads_reporting.py`, `tiktok_ads_reporting.py`
- **sales_automation/** - Automatización de ventas
  - `sales_*.py`, `abandoned_cart_recovery.py`

### 👥 **hr_talent/** - Recursos Humanos y Talento
- **employee_onboarding/** - Onboarding de empleados
  - `employee_onboarding.py`
- **job_descriptions/** - Gestión de descripciones de trabajo
  - `job_description_*.py`
- **hiring/** - Procesos de contratación
  - `hiring_*.py`
- **time_tracking/** - Seguimiento de tiempo
  - `time_tracking_*.py`
- **payroll/** - Procesamiento de nómina
  - `payroll_*.py`

### 💰 **finance_billing/** - Finanzas y Facturación
- **invoices/** - Generación y gestión de facturas
  - `invoice_*.py`
- **payments/** - Gestión de pagos
  - `payment_*.py`
- **billing_subscriptions/** - Facturación recurrente y suscripciones
  - `recurring_billing.py`, `subscription_management.py`
- **budget_price/** - Optimización de presupuesto y precios
  - `budget_optimization_automation.py`, `price_automation.py`
- **stripe_quickbooks/** - Integraciones Stripe y QuickBooks
  - `stripe_*.py`, `hubspot_quickbooks_sync.py`
- **financial_reports/** - Reportes financieros
  - `financial_*.py`, `export_accounting.py`
- **reconciliation/** - Conciliación bancaria
  - `bank_reconcile.py`, `credit_notes.py`

### 🛍️ **product_ecommerce/** - Producto y E-commerce
- **product_descriptions/** - Gestión de descripciones de productos
  - `product_description_*.py`
- **ab_testing/** - Pruebas A/B
  - `ab_testing_*.py`
- **inventory/** - Gestión de inventario
  - `inventory_*.py`

### 🎯 **customer_success/** - Éxito del Cliente
- **support_tickets/** - Gestión de tickets de soporte
  - `support_ticket*.py`
- **contracts/** - Gestión de contratos
  - `contract_*.py`, `automated_customer_contract.py`
- **customer_onboarding/** - Onboarding de clientes
  - `customer_onboarding*.py`

### 📈 **data_analytics/** - Datos y Analítica
- **etl/** - Procesos ETL
  - `etl_*.py`, `data_integration_etl.py`, `post_etl_*.py`, `batch_ingestion_dag.py`
- **data_quality/** - Monitoreo de calidad de datos
  - `data_quality_monitoring.py`
- **kpi/** - Reportes y KPIs
  - `kpi_*.py`, `refresh_kpi_materialized.py`
- **data_sync/** - Sincronización de datos
  - `data_sync_unified.py`, `crm_bidirectional_sync.py`
- **airbyte/** - Integraciones Airbyte
  - `airbyte_*.py`
- **ml/** - Machine Learning
  - `mlflow_*.py`

### ⚙️ **operations/** - Operaciones e Infraestructura
- **backups/** - Automatización de backups
  - `*_backups.py`, `backup_*.py`
- **cloud_cost/** - Optimización de costos en la nube
  - `cloud_cost_optimization.py`
- **security_monitoring/** - Monitoreo de seguridad
  - `security_monitoring.py`, `streaming_monitoring_dag.py`, `dependency_update_automation.py`
- **market_research/** - Investigación de mercado
  - `market_research_automation.py`
- **merger_acquisition/** - Integración de fusiones y adquisiciones
  - `merger_acquisition_integration.py`

### 🔌 **integrations/** - Integraciones
- **gmail/** - Procesamiento de Gmail
  - `gmail_*.py`
- **hubspot/** - Integraciones con HubSpot
  - `hubspot_*.py`, `leads_sync_hubspot.py`
- **crm/** - Sincronización con CRM
  - Archivos de sincronización CRM
- **approvals/** - Gestión de aprobaciones
  - `approval_*.py`

### 📁 **Carpetas Especiales**
- **_shared/** - Archivos compartidos y utilidades
  - `constants_and_helpers.py`
- **_documentation/** - Documentación general
  - Archivos README y guías generales
- **examples/** - Ejemplos de DAGs
  - `example_improved_dag.py`
- **tests/** - Tests y pruebas
  - Archivos de testing

## Cómo Agregar Nuevos DAGs

1. Identifica el área de negocio principal del DAG
2. Selecciona la carpeta correspondiente (ej: `sales_marketing/leads/`)
3. Si la funcionalidad específica no tiene subcarpeta, créala o colócala en la subcarpeta más cercana
4. Mantén nombres descriptivos que indiquen la funcionalidad

## Estadísticas por Área

| Área | DAGs Python | Documentación |
|------|-------------|---------------|
| **Sales & Marketing** | 71 | 11 |
| **HR & Talent** | 101 | 25 |
| **Finance & Billing** | 34 | 6 |
| **Product & E-commerce** | 30 | 0 |
| **Customer Success** | 24 | 4 |
| **Data & Analytics** | 31 | 5 |
| **Operations** | 13 | 3 |
| **Integrations** | 14 | 12 |
| **TOTAL** | **318** | **66** |

## READMEs por Área

Cada área principal tiene su propio README con detalles específicos:
- 📊 [Sales & Marketing](sales_marketing/README.md)
- 👥 [HR & Talent](hr_talent/README.md)
- 💰 [Finance & Billing](finance_billing/README.md)
- 🛍️ [Product & E-commerce](product_ecommerce/README.md)
- 🎯 [Customer Success](customer_success/README.md)
- 📈 [Data & Analytics](data_analytics/README.md)
- ⚙️ [Operations](operations/README.md)
- 🔌 [Integrations](integrations/README.md)

## Notas

- Los archivos de documentación (README, guías) están en las mismas carpetas que los DAGs relacionados
- Los archivos de backup (`.backup`, `.bak`) están en las carpetas correspondientes
- La estructura permite escalar fácilmente agregando nuevas subcarpetas según sea necesario
- Cada área tiene un README detallado con la lista completa de DAGs y su propósito

