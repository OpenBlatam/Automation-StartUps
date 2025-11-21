# 🚀 Guía de Inicio Rápido

Guía rápida para navegar y trabajar con los DAGs organizados.

## 📖 Navegación Rápida

### ¿Dónde está mi DAG?
1. **Por funcionalidad**: Usa [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. **Por búsqueda**: Ejecuta `./find_dag.sh -n nombre_dag`
3. **Por área**: Navega a la carpeta del área (ej: `sales_marketing/`)

### Script de Búsqueda
```bash
# Buscar por nombre
./find_dag.sh -n invoice

# Buscar en contenido
./find_dag.sh -c "stripe"

# Filtrar por área
./find_dag.sh -n lead -a sales_marketing

# Listar todos
./find_dag.sh -l
```

## 🎯 Casos de Uso Comunes

### Necesito generar facturas
→ `finance_billing/invoices/invoice_generate.py`

### Necesito procesar leads
→ `sales_marketing/leads/web_lead_capture.py`

### Necesito sincronizar Stripe con QuickBooks
→ `finance_billing/stripe_quickbooks/stripe_invoice_to_quickbooks.py`

### Necesito ejecutar ETL
→ `data_analytics/etl/etl_improved.py`

### Necesito reportes de KPIs
→ `data_analytics/kpi/kpi_reports.py`

### Necesito procesar Gmail
→ `integrations/gmail/gmail_processor.py`

## 📝 Crear un Nuevo DAG

### Paso 1: Identificar Ubicación
```bash
# ¿A qué área pertenece?
# Sales, HR, Finance, Product, Customer Success, Data, Operations, Integrations
```

### Paso 2: Crear el Archivo
```bash
# Ejemplo: Nuevo DAG de facturación
cd finance_billing/invoices/
touch nuevo_invoice_dag.py
```

### Paso 3: Usar Template
Ver [BEST_PRACTICES.md](BEST_PRACTICES.md) para template y mejores prácticas.

### Paso 4: Documentar
- Agregar docstrings
- Actualizar README del área si es necesario
- Agregar a QUICK_REFERENCE.md si es común

## 🔍 Encontrar DAGs Relacionados

### Por Integración
- **Stripe**: `finance_billing/stripe_quickbooks/`
- **QuickBooks**: `finance_billing/stripe_quickbooks/` y `finance_billing/financial_reports/`
- **HubSpot**: `integrations/hubspot/`
- **Gmail**: `integrations/gmail/`

### Por Tipo de Proceso
- **ETL**: `data_analytics/etl/`
- **Reportes**: `data_analytics/kpi/` y `finance_billing/financial_reports/`
- **Sincronización**: `data_analytics/data_sync/` y `integrations/`
- **Automatización**: Ver subcarpetas `*_automation/`

## 📊 Estructura de Carpetas (Resumen)

```
dags/
├── sales_marketing/      → Leads, outreach, ads, ventas
├── hr_talent/            → Onboarding, hiring, nómina, tiempo
├── finance_billing/      → Facturas, pagos, presupuesto, Stripe/QuickBooks
├── product_ecommerce/    → Productos, inventario, A/B testing
├── customer_success/     → Soporte, contratos, onboarding clientes
├── data_analytics/       → ETL, KPIs, calidad de datos, ML
├── operations/           → Backups, seguridad, costos, investigación
└── integrations/         → Gmail, HubSpot, CRM, aprobaciones
```

## 🆘 Ayuda y Soporte

### Documentación
- **General**: [README.md](README.md)
- **Estructura**: [STRUCTURE.md](STRUCTURE.md)
- **Referencia**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
- **Prácticas**: [BEST_PRACTICES.md](BEST_PRACTICES.md)
- **Dependencias**: [DAG_DEPENDENCIES.md](DAG_DEPENDENCIES.md)

### READMEs por Área
Cada área tiene su README con detalles específicos:
- `sales_marketing/README.md`
- `hr_talent/README.md`
- `finance_billing/README.md`
- `product_ecommerce/README.md`
- `customer_success/README.md`
- `data_analytics/README.md`
- `operations/README.md`
- `integrations/README.md`

## ✅ Checklist Rápido

Antes de crear/modificar un DAG:
- [ ] ¿Está en la carpeta correcta?
- [ ] ¿Sigue las convenciones de nombres?
- [ ] ¿Tiene documentación básica?
- [ ] ¿Está en QUICK_REFERENCE.md si es común?
- [ ] ¿Dependencias documentadas?

## 📈 Estadísticas del Proyecto

- **Total DAGs**: 329 archivos Python
- **Áreas organizadas**: 8
- **Subcarpetas**: 40+
- **Documentación**: 70+ archivos Markdown

---

💡 **Tip**: Usa `./find_dag.sh -l` para ver todos los DAGs organizados

