# 🔍 Referencia Rápida de DAGs

Índice rápido para encontrar DAGs por funcionalidad específica.

## Por Funcionalidad

### 📥 Captura y Gestión de Leads
- `sales_marketing/leads/web_lead_capture.py` - Captura de leads desde web
- `sales_marketing/leads/organic_acquisition_nurturing.py` - Adquisición orgánica y nurturing
- `sales_marketing/leads/lead_qualification.py` - Calificación de leads
- `sales_marketing/leads/lead_scoring_automation.py` - Scoring automático
- `sales_marketing/leads/lead_enrichment.py` - Enriquecimiento de datos

### 💰 Facturación y Pagos
- `finance_billing/invoices/invoice_generate.py` - Generación de facturas
- `finance_billing/payments/payment_reminders.py` - Recordatorios de pago
- `finance_billing/billing_subscriptions/recurring_billing.py` - Facturación recurrente
- `finance_billing/billing_subscriptions/subscription_management.py` - Gestión de suscripciones

### 🔄 Integraciones Stripe/QuickBooks
- `finance_billing/stripe_quickbooks/stripe_product_to_quickbooks_item.py` - Sincronización productos
- `finance_billing/stripe_quickbooks/stripe_invoice_to_quickbooks.py` - Sincronización facturas
- `finance_billing/stripe_quickbooks/stripe_refund_to_quickbooks.py` - Procesamiento de reembolsos
- `finance_billing/stripe_quickbooks/stripe_reconcile.py` - Conciliación

### 📊 Reportes y Analytics
- `sales_marketing/ads_reporting/facebook_ads_reporting.py` - Reportes Facebook Ads
- `sales_marketing/ads_reporting/google_ads_reporting.py` - Reportes Google Ads
- `finance_billing/financial_reports/financial_reports.py` - Reportes financieros
- `data_analytics/kpi/kpi_reports.py` - Reportes de KPIs

### 🔄 ETL y Procesamiento de Datos
- `data_analytics/etl/etl_improved.py` - ETL mejorado
- `data_analytics/etl/data_integration_etl.py` - Integración de datos
- `data_analytics/data_quality/data_quality_monitoring.py` - Monitoreo de calidad
- `data_analytics/etl/batch_ingestion_dag.py` - Ingesta por lotes

### 👥 Recursos Humanos
- `hr_talent/employee_onboarding/employee_onboarding.py` - Onboarding empleados
- `hr_talent/job_descriptions/job_description_ai_generator.py` - Generador AI de descripciones
- `hr_talent/hiring/hiring_ats.py` - Sistema ATS
- `hr_talent/time_tracking/time_tracking_automation.py` - Automatización de tiempo
- `hr_talent/payroll/payroll_processing.py` - Procesamiento de nómina

### 🛍️ Producto y E-commerce
- `product_ecommerce/product_descriptions/product_description_generator.py` - Generador de descripciones
- `product_ecommerce/inventory/inventory_monitor.py` - Monitoreo de inventario
- `product_ecommerce/inventory/inventory_reorder.py` - Reorden automático
- `product_ecommerce/ab_testing/ab_testing_automation.py` - Automatización A/B testing

### 🎯 Customer Success
- `customer_success/support_tickets/support_ticket_automation.py` - Automatización de tickets
- `customer_success/contracts/contract_management.py` - Gestión de contratos
- `customer_success/contracts/contract_auto_renewal.py` - Renovación automática
- `customer_success/customer_onboarding/customer_onboarding.py` - Onboarding clientes

### 🔌 Integraciones
- `integrations/gmail/gmail_processor.py` - Procesamiento de Gmail
- `integrations/hubspot/hubspot_batch_update.py` - Actualización masiva HubSpot
- `integrations/hubspot/hubspot_quickbooks_sync.py` - Sincronización HubSpot-QuickBooks
- `integrations/approvals/approval_cleanup.py` - Limpieza de aprobaciones

### ⚙️ Operaciones
- `operations/backups/automated_backups.py` - Backups automatizados
- `operations/cloud_cost/cloud_cost_optimization.py` - Optimización de costos
- `operations/security_monitoring/security_monitoring.py` - Monitoreo de seguridad
- `operations/market_research/market_research_automation.py` - Investigación de mercado

## Por Frecuencia de Uso

### DAGs Diarios
- ETL processes (`data_analytics/etl/`)
- KPI reports (`data_analytics/kpi/`)
- Lead processing (`sales_marketing/leads/`)
- Invoice generation (`finance_billing/invoices/`)

### DAGs Semanales
- Financial reports (`finance_billing/financial_reports/`)
- Sales analytics (`sales_marketing/sales_automation/`)
- Data quality checks (`data_analytics/data_quality/`)

### DAGs Mensuales
- Monthly KPI reports (`data_analytics/kpi/kpi_reports_monthly.py`)
- Budget optimization (`finance_billing/budget_price/`)
- Market research (`operations/market_research/`)

## Por Prioridad

### 🔴 Críticos (Business Critical)
- Invoice generation
- Payment processing
- Customer onboarding
- Contract management

### 🟡 Importantes (High Priority)
- Lead processing
- ETL pipelines
- Financial reporting
- Support ticket automation

### 🟢 Operacionales (Operational)
- Backups
- Monitoring
- Data quality checks
- Analytics reports

## Búsqueda por Palabra Clave

| Palabra Clave | Ubicación |
|---------------|-----------|
| `invoice` | `finance_billing/invoices/` |
| `payment` | `finance_billing/payments/` |
| `lead` | `sales_marketing/leads/` |
| `stripe` | `finance_billing/stripe_quickbooks/` |
| `etl` | `data_analytics/etl/` |
| `kpi` | `data_analytics/kpi/` |
| `contract` | `customer_success/contracts/` |
| `job_description` | `hr_talent/job_descriptions/` |
| `inventory` | `product_ecommerce/inventory/` |
| `backup` | `operations/backups/` |
| `gmail` | `integrations/gmail/` |
| `hubspot` | `integrations/hubspot/` |

