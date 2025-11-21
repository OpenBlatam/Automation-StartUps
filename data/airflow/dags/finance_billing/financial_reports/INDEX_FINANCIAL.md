# Sistema Financiero Automatizado - Índice Ejecutivo

## Visión General

Sistema completo de automatización financiera que cubre facturación automática, transacciones recurrentes, recordatorios de pago, conciliación bancaria, reportes y análisis. Reduce errores manuales y ahorra horas de trabajo administrativo. Integración completa con Stripe y QuickBooks.

## Componentes Principales

### 1. Facturación Automática

#### `invoice_generate`
- **Archivo**: `data/airflow/dags/invoice_generate.py`
- **Schedule**: Diario a las 02:00 UTC
- **Función**: Genera facturas desde Stripe o DB, crea PDFs, sube a S3 y envía emails
- **Características**:
  - Integración con Stripe (opcional)
  - Generación HTML y PDF profesional
  - Subida a S3 con URLs firmadas
  - Soporte multi-moneda (USD, EUR, MXN, GBP)
  - Validaciones robustas (cantidad, precio, totales)
  - Persistencia en DB

#### `credit_notes`
- **Archivo**: `data/airflow/dags/credit_notes.py`
- **Schedule**: Manual (trigger con parámetros)
- **Función**: Genera notas de crédito para devoluciones
- **Características**:
  - Validación de factura
  - Numeración automática (CN-000001)
  - Actualización de estado de factura
  - Notificación por email

#### `recurring_billing`
- **Archivo**: `data/airflow/dags/recurring_billing.py`
- **Schedule**: Diario a las 01:00 UTC
- **Función**: Procesa transacciones recurrentes y suscripciones automáticamente
- **Características**:
  - Obtiene suscripciones activas de Stripe
  - Identifica suscripciones que necesitan facturación
  - Genera facturas automáticas para ciclos recurrentes
  - Procesa pagos automáticos
  - Maneja pagos fallidos y reintentos
  - Envía recordatorios de renovación de suscripciones
  - Sincronización opcional con QuickBooks
  - Tracking completo en base de datos
  - Prevención de facturas duplicadas
  - Notificaciones automáticas a clientes

### 2. Gestión de Pagos

#### `payment_reminders`
- **Archivo**: `data/airflow/dags/payment_reminders.py`
- **Schedule**: Diario a las 09:00 UTC
- **Función**: Envía recordatorios escalonados de pago
- **Características**:
  - Recordatorios configurables (-3, 1, 7, 14 días)
  - Cálculo automático de `due_date`
  - Tracking de recordatorios enviados
  - Email automático

#### `invoice_mark_paid`
- **Archivo**: `data/airflow/dags/invoice_mark_paid.py`
- **Schedule**: Cada 2 horas
- **Función**: Marca facturas como pagadas cuando llegan pagos
- **Características**:
  - Matching automático por monto y fecha
  - Tabla `invoice_payments` para tracking
  - Actualización de estado automática

#### `payment_partial`
- **Archivo**: `data/airflow/dags/payment_partial.py`
- **Schedule**: Cada 4 horas
- **Función**: Maneja pagos parciales
- **Características**:
  - Estado `partial` para facturas con pagos incompletos
  - Cálculo de monto pagado vs pendiente
  - Matching por moneda

#### `stripe_fees_to_quickbooks`
- **Archivo**: `data/airflow/dags/stripe_fees_to_quickbooks.py`
- **Schedule**: Diario a las 03:00 UTC
- **Función**: Crea gastos en QuickBooks para las tarifas de Stripe
- **Características**:
  - Obtiene pagos exitosos de Stripe del período configurado
  - Extrae las tarifas de cada pago desde balance_transactions
  - Crea gastos en QuickBooks en la cuenta "Tarifas Stripe"
  - Incluye referencia del pago Stripe para conciliación
  - Evita duplicados verificando gastos ya creados
  - Tracking en base de datos (`stripe_fees_quickbooks`)

### 3. Conciliación Bancaria

#### `bank_reconcile`
- **Archivo**: `data/airflow/dags/bank_reconcile.py`
- **Schedule**: Diario a las 10:00 UTC
- **Función**: Concilia Stripe payouts con extractos bancarios
- **Características**:
  - Fetch de payouts desde Stripe
  - Lectura de extractos CSV
  - Fuzzy matching (monto + fecha + referencia)
  - Persistencia en `reconciliations` y `reconciliation_diffs`
  - Alertas si tasa < 95%

### 4. Reportes y Análisis

#### `financial_reports`
- **Archivo**: `data/airflow/dags/financial_reports.py`
- **Schedule**: Diario a las 01:00 UTC
- **Función**: Refresca vistas materializadas para KPIs
- **Características**:
  - `mv_revenue_daily` - Revenue diario
  - `mv_ar_aging` - A/R Aging por buckets
  - `mv_revenue_monthly` - Revenue mensual

#### `financial_export`
- **Archivo**: `data/airflow/dags/financial_export.py`
- **Schedule**: Semanal (lunes 08:00 UTC)
- **Función**: Exporta reportes a CSV
- **Características**:
  - A/R Aging export
  - Revenue export (últimos 90 días)
  - Email con resumen

#### `export_accounting`
- **Archivo**: `data/airflow/dags/export_accounting.py`
- **Schedule**: Mensual (día 1, 06:00 UTC)
- **Función**: Exporta transacciones a formato OFX
- **Características**:
  - Formato OFX estándar (compatible QuickBooks, Quicken)
  - Último mes completo
  - Pagos (CREDIT) y facturas (DEBIT)

#### `stripe_fees_to_quickbooks`
- **Archivo**: `data/airflow/dags/stripe_fees_to_quickbooks.py`
- **Schedule**: Diario a las 03:00 UTC
- **Función**: Crea gastos automáticos en QuickBooks para tarifas de Stripe
- **Características**:
  - Integración directa con QuickBooks Online API
  - Detección automática de tarifas desde balance_transactions
  - Soporte para sandbox y producción

#### `financial_summary`
- **Archivo**: `data/airflow/dags/financial_summary.py`
- **Schedule**: Semanal (lunes 09:00 UTC)
- **Función**: Resumen ejecutivo semanal por email
- **Características**:
  - Revenue 7d y 30d
  - Cuentas por cobrar
  - Métricas de pagos
  - Notas de crédito

### 5. Alertas y Validación

#### `invoice_alerts`
- **Archivo**: `data/airflow/dags/invoice_alerts.py`
- **Schedule**: Diario a las 10:00 UTC
- **Función**: Alertas de facturas críticas vencidas
- **Características**:
  - Detecta facturas >90 días vencidas, >$1000
  - Slack + Email
  - Top 5/10 facturas

#### `invoice_deduplication`
- **Archivo**: `data/airflow/dags/invoice_deduplication.py`
- **Schedule**: Diario a las 04:00 UTC
- **Función**: Detecta posibles facturas duplicadas
- **Características**:
  - Matching por monto, fecha, estado
  - Reporte por email
  - Últimos 30 días

#### `invoice_audit`
- **Archivo**: `data/airflow/dags/invoice_audit.py`
- **Schedule**: Diario a las 03:00 UTC
- **Función**: Setup y reportes de audit trail
- **Características**:
  - Trigger PostgreSQL para cambios
  - Historial completo en `invoice_audit_log`
  - Reporte de cambios recientes

### 6. Dashboard y APIs

#### Next.js Dashboard
- **Componente**: `web/kpis-next/components/Dashboard.tsx`
- **Funcionalidades**:
  - A/R Aging table
  - Revenue diario/mensual
  - Actualización automática

#### API Endpoints
- **`/api/kpi/aging`**: A/R Aging por buckets
- **`/api/kpi/revenue`**: Revenue diario/mensual
- **`/api/kpi/credit-notes`**: Lista notas de crédito
- **`/api/kpi/financial-metrics`**: Métricas avanzadas

#### Grafana Dashboard
- **Archivo**: `observability/grafana/dashboards/kpi.json`
- **Paneles**:
  - A/R Aging (bargauge)
  - Facturas pendientes/vencidas
  - Revenue diario/mensual
  - Tabla facturas vencidas

### 7. Base de Datos

#### Tablas Principales
- **`invoices`**: Facturas
  - Campos: id, serie, company_tax_id, currency, subtotal, taxes, total, status, due_date, payment_reminder_count, created_at, updated_at
- **`invoice_items`**: Items de factura
- **`invoice_payments`**: Relación pagos ↔ facturas
- **`payments`**: Pagos recibidos (Stripe/otros)
- **`credit_notes`**: Notas de crédito
- **`reconciliations`**: Conciliaciones bancarias
- **`reconciliation_diffs`**: Diferencias no conciliadas
- **`invoice_audit_log`**: Historial de cambios

#### Vistas Materializadas
- **`mv_revenue_daily`**: Revenue diario (90 días)
- **`mv_ar_aging`**: A/R Aging por buckets
- **`mv_revenue_monthly`**: Revenue mensual (12 meses)

### 8. Templates y Assets

#### Plantilla HTML
- **Archivo**: `data/airflow/plugins/templates/invoice.html`
- **Características**:
  - Diseño profesional con CSS
  - Soporte multi-moneda con símbolos
  - Formato de números mejorado

## Flujo de Datos

```
Stripe Subscriptions (Recurring)
    │
    ▼
recurring_billing (daily 01:00)
    ├─→ Fetch active subscriptions
    ├─→ Identify billing needed
    ├─→ Generate invoices
    ├─→ Process payments
    ├─→ Handle failed payments
    ├─→ Send renewal reminders
    └─→ Sync to QuickBooks (optional)

Stripe/DB Sales
    │
    ▼
invoice_generate (daily 02:00)
    ├─→ Build invoice rows
    ├─→ Persist in DB
    ├─→ Render HTML + PDF
    ├─→ Upload to S3
    └─→ Email customer

Invoices (status='issued')
    │
    ├─→ payment_reminders (daily 09:00)
    │   └─→ Send escalated reminders
    │
    ├─→ invoice_mark_paid (every 2h)
    │   └─→ Match payments → mark paid
    │
    └─→ payment_partial (every 4h)
        └─→ Handle partial payments

Stripe Payments + Fees
    │
    ├─→ stripe_fees_to_quickbooks (daily 03:00)
    │   └─→ Create expenses in QuickBooks
    │
Stripe Payouts + Bank Statements
    │
    ▼
bank_reconcile (daily 10:00)
    ├─→ Match transactions
    └─→ Alert if <95% match rate

Daily Reports
    ├─→ financial_reports (01:00) - Refresh MVs
    ├─→ invoice_alerts (10:00) - Critical alerts
    └─→ invoice_deduplication (04:00) - Duplicate detection

Weekly/Monthly
    ├─→ financial_export (Mon 08:00) - CSV exports
    ├─→ financial_summary (Mon 09:00) - Executive summary
    └─→ export_accounting (1st 06:00) - OFX export
```

## Monitoreo

```
PostgreSQL
    │
    ├─→ Materialized Views → Grafana Dashboard
    ├─→ Next.js API → Dashboard Web
    └─→ Airflow Metrics → Statsd/Prometheus
```

## Configuración Requerida

### Variables de Airflow

#### Facturación
- `INVOICE_SERIE` - Serie de facturación (default: "A")
- `COMPANY_TAX_ID` - RFC/NIF de la empresa
- `TAX_RATE` - Tasa de impuestos (default: "0.21")
- `DEFAULT_CURRENCY` - Moneda por defecto (default: "USD")

#### Storage
- `S3_BUCKET` - Bucket S3 para facturas
- `AWS_DEFAULT_REGION` - Región AWS
- `INVOICE_HTML_OUT` - Directorio HTML (default: "/tmp/invoices")
- `INVOICE_PDF_OUT` - Directorio PDF (default: "/tmp/invoices")
- `INVOICE_URL_TTL_SECONDS` - TTL URLs firmadas (default: "604800")

#### Recordatorios
- `REMINDER_DAYS` - Días de recordatorio (default: "-3,1,7,14")
- `PAYMENT_TERMS_DAYS` - Plazo de pago (default: "30")

#### Conciliación
- `BANK_STATEMENTS_PATH` - Path a extractos CSV (default: "/tmp/bank_statements")
- `RECONCILE_AMOUNT_TOLERANCE` - Tolerancia monto (default: "0.01")
- `RECONCILE_MAX_DATE_DIFF_DAYS` - Max diferencia días (default: "7")

#### Alertas
- `CRITICAL_OVERDUE_DAYS` - Días para alerta crítica (default: "90")
- `CRITICAL_MIN_AMOUNT` - Monto mínimo crítico (default: "1000.0")

#### Exportaciones
- `FINANCIAL_EXPORT_DIR` - Directorio exports (default: "/tmp/exports")
- `ACCOUNTING_EXPORT_DIR` - Directorio contable (default: "/tmp/accounting")

#### Notas de Crédito
- `CREDIT_NOTE_PREFIX` - Prefijo numeración (default: "CN")

#### QuickBooks Integration
- `QUICKBOOKS_EXPENSE_ACCOUNT` - Nombre de la cuenta de gastos (default: "Tarifas Stripe")
- `QUICKBOOKS_USE_SANDBOX` - Usar sandbox de QuickBooks (default: "true")
- `STRIPE_FEES_LOOKBACK_DAYS` - Días hacia atrás para buscar pagos (default: "1")

#### Recurring Billing
- `RECURRING_BILLING_LOOKAHEAD_DAYS` - Días de anticipación para facturación (default: "1")
- `RECURRING_BILLING_MAX_RETRIES` - Máximo de reintentos para pagos fallidos (default: "3")
- `RECURRING_BILLING_SYNC_QUICKBOOKS` - Sincronizar con QuickBooks (default: "false")

### Variables de Entorno

- `STRIPE_API_KEY` - API key Stripe (opcional)
- `QUICKBOOKS_ACCESS_TOKEN` - Access token OAuth2 de QuickBooks
- `QUICKBOOKS_REALM_ID` - Company ID (Realm ID) de QuickBooks
- `KPIS_PG_DSN` - Connection string PostgreSQL
- `SLACK_WEBHOOK_URL` - Webhook Slack (para alertas)

### Setup Inicial

1. **Base de Datos**: Las tablas se crean automáticamente en los DAGs
2. **S3**: Configurar bucket y credenciales AWS
3. **Email**: Configurar backend de email en Airflow
4. **Grafana**: Importar dashboard actualizado
5. **Stripe**: Configurar API key si se usa integración

## Quick Start

```bash
# 1. Configurar variables de Airflow
airflow variables set INVOICE_SERIE "A"
airflow variables set COMPANY_TAX_ID "RFC123456789"
airflow variables set TAX_RATE "0.21"
airflow variables set S3_BUCKET "my-invoices-bucket"
airflow variables set REMINDER_DAYS "-3,1,7,14"

# 2. Trigger facturación manual (si no hay schedule)
airflow dags trigger invoice_generate

# 3. Ver dashboard
# Navegar a http://your-app (Dashboard incluye sección Finanzas)

# 4. Generar nota de crédito
airflow dags trigger credit_notes \
  --conf '{"invoice_id": 123, "reason": "Customer refund"}'
```

## Archivos Creados

### DAGs Financieros (15 total)
1. `invoice_generate.py` - Generación de facturas
2. `recurring_billing.py` - **NUEVO** Procesamiento de transacciones recurrentes
3. `payment_reminders.py` - Recordatorios de pago
4. `invoice_mark_paid.py` - Marcado automático
5. `payment_partial.py` - Pagos parciales
6. `stripe_fees_to_quickbooks.py` - Tarifas Stripe → QuickBooks
7. `bank_reconcile.py` - Conciliación bancaria
8. `financial_reports.py` - Refrescar vistas
9. `financial_export.py` - Exportación CSV
10. `export_accounting.py` - Exportación OFX
11. `invoice_alerts.py` - Alertas críticas
12. `credit_notes.py` - Notas de crédito
13. `invoice_audit.py` - Audit trail
14. `financial_summary.py` - Resumen semanal
15. `invoice_deduplication.py` - Detección duplicados

### Next.js
- `web/kpis-next/components/Dashboard.tsx` (actualizado)
- `web/kpis-next/app/api/kpi/aging/route.ts`
- `web/kpis-next/app/api/kpi/revenue/route.ts`
- `web/kpis-next/app/api/kpi/credit-notes/route.ts`
- `web/kpis-next/app/api/kpi/financial-metrics/route.ts`
- `web/kpis-next/lib/kpi.ts` (actualizado)

### Templates
- `data/airflow/plugins/templates/invoice.html`

### Observabilidad
- `observability/grafana/dashboards/kpi.json` (actualizado)

## Características Técnicas

### Multi-moneda
- Detección automática desde Stripe
- Símbolos correctos ($, €, £)
- Validación de moneda en matching

### Validaciones
- Email format
- Cantidad > 0
- Precio unitario >= 0
- Total >= 0
- Subtotal > 0
- Nombre con al menos una letra
- Fecha no muy antigua

### Formatos de Exportación
- **CSV**: A/R Aging, Revenue
- **OFX**: Transacciones contables
- **PDF**: Facturas profesionales
- **HTML**: Facturas con estilos

### Matching Inteligente
- Por monto (tolerancia configurable)
- Por fecha (proximidad configurable)
- Por referencia (fuzzy matching)
- Por moneda

## Próximos Pasos

1. ✅ Facturación automática completa
2. ✅ **Transacciones recurrentes y suscripciones** (NUEVO)
3. ✅ Recordatorios escalonados
4. ✅ Conciliación bancaria
5. ✅ Reportes financieros
6. ✅ Exportaciones (CSV, OFX)
7. ✅ Alertas y validaciones
8. ✅ Dashboard interactivo
9. ✅ Soporte multi-moneda
10. ✅ Pagos parciales
11. ✅ Notas de crédito
12. ✅ Audit trail
13. ✅ Métricas avanzadas
14. ✅ Integración QuickBooks (tarifas Stripe)
15. ✅ Recordatorios de renovación de suscripciones (NUEVO)

**El sistema financiero está completo y listo para producción.**

## Troubleshooting

### Facturas no se generan
- Verificar `STRIPE_API_KEY` si se usa Stripe
- Verificar `KPIS_PG_DSN`
- Revisar logs de `load_sales` task

### Recordatorios no se envían
- Verificar configuración de email en Airflow
- Verificar `REMINDER_DAYS` y `PAYMENT_TERMS_DAYS`
- Verificar que facturas tengan `due_date` calculado

### Conciliación baja (<95%)
- Verificar formato CSV de extractos bancarios
- Ajustar `RECONCILE_AMOUNT_TOLERANCE`
- Verificar `RECONCILE_MAX_DATE_DIFF_DAYS`

### PDFs no se generan
- Verificar que `reportlab` esté instalado
- Verificar permisos en `INVOICE_PDF_OUT`
- Revisar logs de `render_pdf` task

### Gastos QuickBooks no se crean
- Verificar `QUICKBOOKS_ACCESS_TOKEN` y `QUICKBOOKS_REALM_ID`
- Verificar que la cuenta "Tarifas Stripe" exista en QuickBooks (o cambiar `QUICKBOOKS_EXPENSE_ACCOUNT`)
- Verificar `STRIPE_API_KEY` si se usa integración con Stripe
- Revisar logs de `create_quickbooks_expenses` task para errores de API
- Verificar que `QUICKBOOKS_USE_SANDBOX` esté configurado correctamente


