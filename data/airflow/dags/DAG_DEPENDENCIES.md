# 🔗 Mapa de Dependencias entre DAGs

Documentación de dependencias y relaciones entre DAGs.

## Dependencias por Área

### 📊 Sales & Marketing

#### Leads → CRM
- `sales_marketing/leads/lead_qualification.py` → `integrations/hubspot/leads_sync_hubspot.py`
- `sales_marketing/leads/organic_acquisition_nurturing.py` → `sales_marketing/leads/lead_nurturing.py`

#### Outreach → Leads
- `sales_marketing/outreach/outreach_multichannel.py` → `sales_marketing/leads/lead_segmentation.py`

#### Ads Reporting → Analytics
- `sales_marketing/ads_reporting/*.py` → `data_analytics/kpi/kpi_reports.py`

### 💰 Finance & Billing

#### Invoices → Payments
- `finance_billing/invoices/invoice_generate.py` → `finance_billing/payments/payment_reminders.py`

#### Stripe → QuickBooks
- `finance_billing/stripe_quickbooks/stripe_invoice_to_quickbooks.py` → `finance_billing/financial_reports/financial_reports.py`
- `finance_billing/stripe_quickbooks/stripe_product_to_quickbooks_item.py` → `finance_billing/stripe_quickbooks/stripe_invoice_to_quickbooks.py`

#### Billing → Reconciliation
- `finance_billing/billing_subscriptions/recurring_billing.py` → `finance_billing/reconciliation/bank_reconcile.py`

### 📈 Data & Analytics

#### ETL Pipeline
```
data_analytics/etl/source_producer.py
    ↓
data_analytics/etl/batch_ingestion_dag.py
    ↓
data_analytics/etl/etl_improved.py
    ↓
data_analytics/data_quality/data_quality_monitoring.py
    ↓
data_analytics/etl/post_etl_consumer.py
    ↓
data_analytics/kpi/kpi_aggregate_daily.py
```

#### Data Sync → ETL
- `data_analytics/data_sync/crm_bidirectional_sync.py` → `data_analytics/etl/data_integration_etl.py`

#### Airbyte → ETL
- `data_analytics/airbyte/airbyte_sync.py` → `data_analytics/etl/batch_ingestion_dag.py`

### 🔌 Integrations

#### Gmail → HubSpot
- `integrations/gmail/gmail_processor.py` → `integrations/gmail/gmail_classify_hubspot.py`
- `integrations/gmail/gmail_classify_hubspot.py` → `integrations/hubspot/hubspot_batch_update.py`

#### HubSpot → QuickBooks
- `integrations/hubspot/leads_sync_hubspot.py` → `finance_billing/stripe_quickbooks/hubspot_quickbooks_sync.py`

### 🎯 Customer Success

#### Onboarding → Contracts
- `customer_success/customer_onboarding/customer_onboarding.py` → `customer_success/contracts/contract_management.py`

#### Contracts → Billing
- `customer_success/contracts/contract_auto_renewal.py` → `finance_billing/billing_subscriptions/subscription_management.py`

### 👥 HR & Talent

#### Hiring → Onboarding
- `hr_talent/hiring/hiring_ats.py` → `hr_talent/employee_onboarding/employee_onboarding.py`

#### Time Tracking → Payroll
- `hr_talent/time_tracking/time_tracking_automation.py` → `hr_talent/payroll/payroll_processing.py`

## Dependencias Críticas (Business Critical)

### Flujo de Facturación Completo
```
1. customer_success/contracts/contract_management.py
   ↓
2. finance_billing/billing_subscriptions/subscription_management.py
   ↓
3. finance_billing/invoices/invoice_generate.py
   ↓
4. finance_billing/payments/payment_reminders.py
   ↓
5. finance_billing/stripe_quickbooks/stripe_invoice_to_quickbooks.py
   ↓
6. finance_billing/financial_reports/financial_reports.py
```

### Flujo de Lead a Cliente
```
1. sales_marketing/leads/web_lead_capture.py
   ↓
2. sales_marketing/leads/lead_qualification.py
   ↓
3. sales_marketing/leads/lead_nurturing.py
   ↓
4. customer_success/customer_onboarding/customer_onboarding.py
   ↓
5. customer_success/contracts/contract_management.py
```

### Flujo de Datos Completo
```
1. data_analytics/airbyte/airbyte_sync.py (Fuentes externas)
   ↓
2. data_analytics/etl/batch_ingestion_dag.py (Ingesta)
   ↓
3. data_analytics/etl/etl_improved.py (Transformación)
   ↓
4. data_analytics/data_quality/data_quality_monitoring.py (Validación)
   ↓
5. data_analytics/kpi/kpi_aggregate_daily.py (Agregación)
   ↓
6. data_analytics/kpi/kpi_reports.py (Reportes)
```

## Dependencias Externas

### Sistemas Externos que Requieren DAGs Previos
- **Stripe**: Requiere DAGs de sincronización antes de reportes
- **QuickBooks**: Requiere sincronización de productos antes de facturas
- **HubSpot**: Requiere procesamiento de leads antes de actualización
- **Gmail**: Requiere procesamiento antes de clasificación

## Orden de Ejecución Recomendado

### Diario (Cronológico)
1. **00:00** - Backups (`operations/backups/`)
2. **01:00** - ETL Ingesta (`data_analytics/etl/`)
3. **02:00** - Data Quality (`data_analytics/data_quality/`)
4. **03:00** - KPI Aggregation (`data_analytics/kpi/`)
5. **04:00** - Lead Processing (`sales_marketing/leads/`)
6. **05:00** - Invoice Generation (`finance_billing/invoices/`)
7. **06:00** - Payment Reminders (`finance_billing/payments/`)
8. **07:00** - Reports (`data_analytics/kpi/`, `finance_billing/financial_reports/`)

### Semanal
1. **Lunes 00:00** - Weekly Reports
2. **Lunes 02:00** - Budget Optimization
3. **Viernes 18:00** - Weekly Analytics

### Mensual
1. **Día 1, 00:00** - Monthly Reports
2. **Día 1, 02:00** - Budget Reconciliation
3. **Día 1, 04:00** - Market Research

## Notas Importantes

⚠️ **Dependencias Críticas**: No modificar sin revisar impacto
⚠️ **External Dependencies**: Algunos DAGs dependen de sistemas externos
⚠️ **Data Dependencies**: DAGs de reportes requieren datos procesados previamente

## Cómo Agregar Dependencias

1. Documenta la dependencia en este archivo
2. Usa `ExternalTaskSensor` en el código cuando sea apropiado
3. Actualiza el schedule para respetar dependencias
4. Comunica cambios a equipos afectados

