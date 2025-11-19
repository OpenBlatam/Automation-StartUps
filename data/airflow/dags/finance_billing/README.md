# 💰 Finance & Billing DAGs

DAGs relacionados con facturación, pagos, presupuestos, integraciones financieras y reportes.

## Estructura

### 🧾 **invoices/** - Facturas
- **Generación**: `invoice_generate.py`
- **Recordatorios**: `invoice_billing_reminders.py`
- **Alertas**: `invoice_alerts.py`
- **Auditoría**: `invoice_audit.py`
- **Deduplicación**: `invoice_deduplication.py`
- **Marcar como pagado**: `invoice_mark_paid.py`

### 💳 **payments/** - Pagos
- **Recordatorios**: `payment_reminders.py`
- **Pagos parciales**: `payment_partial.py`

### 🔄 **billing_subscriptions/** - Facturación Recurrente
- **Facturación recurrente**: `recurring_billing.py`
- **Gestión de suscripciones**: `subscription_management.py`

### 💵 **budget_price/** - Presupuesto y Precios
- **Optimización de presupuesto**: `budget_optimization_automation.py`
- **Automatización de precios**: `price_automation.py`
- **Documentación**: 
  - `BUDGET_OPTIMIZATION_GUIDE.md`
  - `QUICK_START_PRICE_AUTOMATION.md`
  - `README_PRICE_AUTOMATION.md`
  - `RESUMEN_AUTOMATIZACIONES_PRESUPUESTO.md`

### 🔗 **stripe_quickbooks/** - Integraciones Stripe/QuickBooks
- **Sincronización de productos**: `stripe_product_to_quickbooks_item.py`
- **Sincronización de clientes**: `stripe_customer_to_quickbooks.py`
- **Sincronización de facturas**: `stripe_invoice_to_quickbooks.py`, `stripe_invoice_sync_quickbooks.py`
- **Sincronización de fees**: `stripe_fees_to_quickbooks.py`
- **Reembolsos**: `stripe_refund_to_quickbooks.py`, `stripe_refund_email_detector.py`, `stripe_refund_monitor.py`, `stripe_refund_reports.py`
- **Reconciliación**: `stripe_reconcile.py`, `stripe_to_quickbooks.py`, `stripe_quickbooks_sync.py`
- **Reportes**: `stripe_quickbooks_report.py`, `stripe_quickbooks_revenue_compare.py`, `stripe_quickbooks_revenue_compare_dag.py`
- **HubSpot sync**: `hubspot_quickbooks_sync.py`

### 📈 **financial_reports/** - Reportes Financieros
- **Reportes financieros**: `financial_reports.py`, `financial_summary.py`
- **Exportación contable**: `export_accounting.py`
- **Índice**: `INDEX_FINANCIAL.md`

### 🔍 **reconciliation/** - Conciliación
- **Conciliación bancaria**: `bank_reconcile.py`
- **Notas de crédito**: `credit_notes.py`

## Estadísticas
- **Total de DAGs**: 34 archivos Python
- **Documentación**: 6 archivos Markdown

