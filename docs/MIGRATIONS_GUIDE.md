# 🎯 Guía de Migraciones - Sistema de Troubleshooting

## Sistema de Migraciones

El sistema incluye un gestor de migraciones para gestionar cambios en el esquema de base de datos de forma versionada y controlada.

## Uso Básico

### Crear Nueva Migración

```python
from data.integrations.support_troubleshooting_migrator import DatabaseMigrator

migrator = DatabaseMigrator(db_url="postgresql://...")

# Crear migración
sql_content = """
ALTER TABLE support_troubleshooting_sessions 
ADD COLUMN new_field VARCHAR(255);
"""

migration_name = migrator.create_migration(
    "add_new_field_to_sessions",
    sql_content
)
```

### Aplicar Migraciones Pendientes

```python
# Ver migraciones pendientes
pending = migrator.get_pending_migrations()
print(f"Migraciones pendientes: {pending}")

# Aplicar todas (dry-run primero)
results = migrator.apply_all_pending(dry_run=True)
for result in results:
    print(f"{result['migration']}: {result.get('message', 'OK')}")

# Aplicar realmente
results = migrator.apply_all_pending(dry_run=False)
```

### Rollback de Migración

```python
# Crear migración de rollback primero
rollback_sql = """
ALTER TABLE support_troubleshooting_sessions 
DROP COLUMN IF EXISTS new_field;
"""

migrator.create_migration(
    "add_new_field_to_sessions_rollback",
    rollback_sql
)

# Revertir migración
result = migrator.rollback_migration("20250127_120000_add_new_field_to_sessions.sql")
```

## Migraciones Incluidas

### Migración Inicial
- `001_initial_schema.sql` - Esquema base completo

### Migraciones de Mejoras
- `002_add_feedback_schema.sql` - Sistema de feedback
- `003_add_webhooks_schema.sql` - Sistema de webhooks
- `004_add_advanced_features.sql` - Características avanzadas
- `005_add_performance_optimizations.sql` - Optimizaciones
- `006_add_error_tracking.sql` - Tracking de errores

## Versionado de Base de Conocimiento

### Crear Versión

```python
from data.integrations.support_troubleshooting_kb_versioner import KnowledgeBaseVersioner

versioner = KnowledgeBaseVersioner("data/integrations/support_troubleshooting_kb.json")

version_id = versioner.create_version(
    description="Agregado problema de integración API",
    author="dev@example.com",
    tags=["api", "integration"]
)
```

### Listar Versiones

```python
versions = versioner.list_versions()
for version in versions:
    print(f"{version['version_id']}: {version['description']}")
```

### Restaurar Versión

```python
# Restaurar versión anterior
success = versioner.restore_version("v3_20250127_120000")
if success:
    print("Versión restaurada exitosamente")
```

### Comparar Versiones

```python
comparison = versioner.compare_versions("v2_20250126", "v3_20250127")
print(f"Agregados: {comparison['added']}")
print(f"Eliminados: {comparison['removed']}")
print(f"Modificados: {comparison['modified']}")
```

## Health Check Avanzado

### Ejecutar Health Check

```bash
# Desde línea de comandos
python3 scripts/troubleshooting_health_check.py

# O con script bash
./scripts/troubleshooting_health_check.sh
```

### Health Check Programático

```python
from scripts.troubleshooting_health_check import TroubleshootingHealthCheck

health_check = TroubleshootingHealthCheck()
results = health_check.run_all_checks()

if results["overall_status"] == "healthy":
    print("✅ Sistema saludable")
else:
    print(f"⚠️ Sistema con problemas: {results['overall_status']}")
    for check_name, check_result in results["checks"].items():
        if check_result["status"] != "healthy":
            print(f"  - {check_name}: {check_result['message']}")
```

### Integrar en Monitoreo

```python
# Health check periódico
import time
from scripts.troubleshooting_health_check import TroubleshootingHealthCheck

health_check = TroubleshootingHealthCheck()

while True:
    results = health_check.run_all_checks()
    
    if results["overall_status"] != "healthy":
        # Enviar alerta
        send_alert(f"Sistema unhealthy: {results['overall_status']}")
    
    time.sleep(300)  # Cada 5 minutos
```

## Mejores Prácticas

### Migraciones

1. **Siempre hacer backup** antes de aplicar migraciones
2. **Probar en desarrollo** primero
3. **Crear rollback** para migraciones destructivas
4. **Aplicar en horarios de bajo tráfico**
5. **Monitorear** después de aplicar

### Versionado de KB

1. **Versionar antes** de hacer cambios grandes
2. **Documentar cambios** en descripción
3. **Usar tags** para categorizar versiones
4. **Mantener historial** completo
5. **Probar restauración** periódicamente

### Health Checks

1. **Ejecutar regularmente** (cada 5-15 minutos)
2. **Configurar alertas** para estados unhealthy
3. **Revisar logs** de checks degradados
4. **Documentar** acciones correctivas
5. **Automatizar** respuestas cuando sea posible

## Troubleshooting de Migraciones

### Problema: Migración falla a mitad

**Solución**:
1. Verificar logs de error
2. Revertir cambios manualmente si es necesario
3. Corregir SQL de migración
4. Crear nueva migración corregida

### Problema: Migración aplicada pero tabla no existe

**Solución**:
```sql
-- Verificar migraciones aplicadas
SELECT * FROM schema_migrations ORDER BY applied_at DESC;

-- Verificar si la migración realmente se aplicó
-- Revisar logs de la migración
```

### Problema: Versión de KB corrupta

**Solución**:
```python
# Restaurar desde backup
versioner.restore_version("v_previous_stable")

# O restaurar manualmente desde archivo de versión
```

---

**Versión**: 1.0.0  
**Última actualización**: 2025-01-27



