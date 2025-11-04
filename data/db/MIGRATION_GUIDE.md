# 🔄 Guía de Migración y Actualización

Guía para actualizar el sistema de automatización de ventas a nuevas versiones.

## 📋 Versiones

- **v1.0**: Sistema inicial (schema básico)
- **v1.1**: Scoring avanzado con factores adicionales
- **v1.2**: Queries optimizadas y vistas

## 🔄 Migración a v1.1

### Cambios en `calculate_lead_score()`

La función ahora acepta parámetros adicionales:

```sql
-- Ejecutar actualización
\i data/db/sales_tracking_schema.sql
```

La función se actualizará automáticamente con los nuevos parámetros opcionales:
- `p_company_domain`
- `p_website_visited`
- `p_demo_requested`
- `p_pricing_page_viewed`

**Compatibilidad:** Los parámetros son opcionales, código existente sigue funcionando.

## 🔄 Migración a v1.2

### Agregar Queries Optimizadas

```sql
-- Ejecutar queries optimizadas
\i data/db/sales_queries_optimized.sql
```

Esto creará:
- 5 vistas nuevas
- 3 funciones nuevas
- Índices adicionales
- Triggers automáticos

**Nota:** No afecta datos existentes, solo agrega funcionalidad.

## 📊 Backup Antes de Migrar

### Backup Completo

```bash
# Backup de schema
pg_dump -U postgres -d tu_database --schema-only > sales_schema_backup.sql

# Backup de datos
pg_dump -U postgres -d tu_database --data-only > sales_data_backup.sql

# Backup completo
pg_dump -U postgres -d tu_database > sales_full_backup.sql
```

### Backup Selectivo

```sql
-- Backup de tablas críticas
COPY sales_pipeline TO '/tmp/sales_pipeline_backup.csv' CSV HEADER;
COPY sales_followup_tasks TO '/tmp/sales_followup_tasks_backup.csv' CSV HEADER;
COPY lead_score_history TO '/tmp/lead_score_history_backup.csv' CSV HEADER;
```

## ✅ Validación Post-Migración

### Ejecutar Validación

```bash
# Validar sistema completo
python scripts/validate_sales_system.py \
  --db "postgresql://user:pass@host/db" \
  --all

# Health check
python scripts/sales_health_check.py \
  --db "postgresql://user:pass@host/db"
```

### Verificar Funciones

```sql
-- Verificar función de scoring
SELECT calculate_lead_score(
    'test_lead',
    2,  -- replies
    3,  -- clicks
    5,  -- opens
    true,  -- has_email
    true,  -- has_phone
    true,  -- has_name
    5,  -- source_score
    2,  -- utm_score
    5,  -- days_since_created
    'example.com',  -- company_domain (nuevo)
    true,  -- website_visited (nuevo)
    false,  -- demo_requested (nuevo)
    true   -- pricing_page_viewed (nuevo)
);
```

### Verificar Vistas

```sql
-- Probar vistas nuevas
SELECT COUNT(*) FROM v_sales_dashboard;
SELECT COUNT(*) FROM v_leads_requires_attention;
SELECT COUNT(*) FROM v_sales_rep_performance;
SELECT COUNT(*) FROM v_sales_forecast;
SELECT COUNT(*) FROM v_conversion_funnel;
```

## 🔧 Rollback

Si necesitas revertir cambios:

### Revertir Función

```sql
-- Restaurar función anterior (guardar antes de migrar)
CREATE OR REPLACE FUNCTION calculate_lead_score(...) 
-- [código anterior]
```

### Eliminar Vistas

```sql
DROP VIEW IF EXISTS v_sales_dashboard;
DROP VIEW IF EXISTS v_leads_requires_attention;
DROP VIEW IF EXISTS v_sales_rep_performance;
DROP VIEW IF EXISTS v_sales_forecast;
DROP VIEW IF EXISTS v_conversion_funnel;
```

### Eliminar Funciones

```sql
DROP FUNCTION IF EXISTS get_top_opportunities(INT, DECIMAL);
DROP FUNCTION IF EXISTS get_leads_at_risk(INT, DECIMAL);
DROP FUNCTION IF EXISTS update_rep_stats(VARCHAR);
```

## 📝 Checklist de Migración

- [ ] Backup completo de base de datos
- [ ] Backup de código existente
- [ ] Ejecutar scripts de migración
- [ ] Validar sistema con `validate_sales_system.py`
- [ ] Health check con `sales_health_check.py`
- [ ] Verificar que DAGs funcionen correctamente
- [ ] Monitorear primera ejecución de DAGs
- [ ] Documentar cambios en changelog

## 🚨 Troubleshooting

### Error: función ya existe

```sql
-- Forzar recreación
DROP FUNCTION IF EXISTS calculate_lead_score(...);
\i data/db/sales_tracking_schema.sql
```

### Error: vista ya existe

```sql
-- Eliminar y recrear
DROP VIEW IF EXISTS v_sales_dashboard CASCADE;
\i data/db/sales_queries_optimized.sql
```

### Índices duplicados

```sql
-- Verificar índices
SELECT indexname FROM pg_indexes WHERE tablename = 'sales_pipeline';

-- Eliminar duplicados si es necesario
DROP INDEX IF EXISTS idx_pipeline_stage_priority_score;
\i data/db/sales_queries_optimized.sql
```

## 📚 Referencias

- Schema principal: `/data/db/sales_tracking_schema.sql`
- Queries optimizadas: `/data/db/sales_queries_optimized.sql`
- Validación: `/scripts/validate_sales_system.py`
- Health check: `/scripts/sales_health_check.py`


