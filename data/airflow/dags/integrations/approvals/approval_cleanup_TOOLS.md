# Herramientas de Refactorización - Approval Cleanup

## 🛠️ Scripts Disponibles

### 1. `migrate_approval_cleanup.py`

**Propósito**: Análisis y reporte de migración

**Uso**:
```bash
python data/airflow/scripts/migrate_approval_cleanup.py
python data/airflow/scripts/migrate_approval_cleanup.py approval_cleanup.py
```

**Qué hace**:
- Analiza el archivo DAG
- Identifica funciones auxiliares
- Cuenta tareas y queries SQL
- Verifica plugins disponibles
- Genera reporte de migración

**Output**: `approval_cleanup_MIGRATION_REPORT.txt`

### 2. `validate_approval_cleanup.py`

**Propósito**: Validación de plugins

**Uso**:
```bash
python data/airflow/scripts/validate_approval_cleanup.py
```

**Qué hace**:
- Valida que todos los plugins pueden importarse
- Verifica que las funciones esperadas existen
- Valida sintaxis de los archivos
- Genera reporte de estado

**Output**: Mensaje en consola con estado de cada plugin

### 3. `analyze_approval_cleanup.py` ⭐ NUEVO

**Propósito**: Análisis avanzado de complejidad

**Uso**:
```bash
python data/airflow/scripts/analyze_approval_cleanup.py
python data/airflow/scripts/analyze_approval_cleanup.py approval_cleanup.py
```

**Qué hace**:
- Analiza complejidad ciclomática de funciones
- Identifica funciones complejas (> 10 complejidad)
- Identifica funciones largas (> 100 líneas)
- Encuentra funciones anidadas
- Detecta posibles funciones duplicadas
- Analiza queries SQL en el código
- Identifica imports no usados
- Genera sugerencias de refactorización

**Output**: 
- `approval_cleanup_ANALYSIS_REPORT.txt`
- Reporte detallado en consola

**Ejemplo de output**:
```
🔴 FUNCIONES COMPLEJAS (complejidad > 10)
  • _analyze_complex_function          Complejidad:  25  Líneas:  350

⚠️  FUNCIONES LARGAS (> 100 líneas)
  • _process_large_function           Líneas:  450  Complejidad:  15

💡 SUGERENCIAS DE REFACTORIZACIÓN
  🔴 5 funciones con complejidad > 10. Considerar dividir...
```

### 4. `extract_to_plugin.py` ⭐ NUEVO

**Propósito**: Extraer funciones automáticamente a plugins

**Uso**:
```bash
# Extraer función (sin remover del DAG)
python data/airflow/scripts/extract_to_plugin.py \
    approval_cleanup.py \
    _log_with_context \
    approval_cleanup_utils.py

# Extraer y remover del DAG
python data/airflow/scripts/extract_to_plugin.py \
    approval_cleanup.py \
    _log_with_context \
    approval_cleanup_utils.py \
    --remove
```

**Qué hace**:
- Extrae el código de una función del DAG
- Identifica dependencias de la función
- Agrega la función al plugin especificado
- Opcionalmente comenta la función en el DAG original
- Mantiene indentación y formato

**Ejemplo**:
```bash
# Extraer función de logging
python data/airflow/scripts/extract_to_plugin.py \
    approval_cleanup.py \
    _log_with_context \
    approval_cleanup_utils.py \
    --remove
```

**Output**:
```
📄 Extrayendo función '_log_with_context' de approval_cleanup.py
📦 Agregando a approval_cleanup_utils.py
📋 Dependencias encontradas: get_current_context, logger
✅ Función '_log_with_context' agregada a approval_cleanup_utils.py
✅ Función '_log_with_context' comentada en el DAG
```

## 📊 Workflow Recomendado

### Paso 1: Análisis Inicial

```bash
# Analizar el DAG
python data/airflow/scripts/analyze_approval_cleanup.py

# Ver reporte
cat data/airflow/dags/approval_cleanup_ANALYSIS_REPORT.txt
```

### Paso 2: Identificar Funciones a Extraer

```bash
# Generar reporte de migración
python data/airflow/scripts/migrate_approval_cleanup.py

# Identificar funciones auxiliares (empiezan con _)
grep -n "^    def _" approval_cleanup.py | head -20
```

### Paso 3: Extraer Funciones

```bash
# Extraer función de utilidades
python data/airflow/scripts/extract_to_plugin.py \
    approval_cleanup.py \
    _log_with_context \
    approval_cleanup_utils.py \
    --remove

# Extraer función de queries
python data/airflow/scripts/extract_to_plugin.py \
    approval_cleanup.py \
    _get_old_requests \
    approval_cleanup_queries.py \
    --remove
```

### Paso 4: Actualizar Imports

Después de extraer, actualizar el DAG:

```python
# Antes
def approval_cleanup():
    def _log_with_context(...):
        ...
    
    @task
    def my_task():
        _log_with_context('info', 'message')

# Después
from data.airflow.plugins.approval_cleanup_utils import log_with_context

@dag(...)
def approval_cleanup():
    @task
    def my_task():
        log_with_context('info', 'message')
```

### Paso 5: Validar

```bash
# Validar plugins
python data/airflow/scripts/validate_approval_cleanup.py

# Validar sintaxis
python -m py_compile data/airflow/plugins/approval_cleanup_*.py

# Probar DAG
airflow dags list | grep approval_cleanup
```

## 🎯 Casos de Uso

### Caso 1: Identificar Funciones Problemáticas

```bash
# Analizar complejidad
python data/airflow/scripts/analyze_approval_cleanup.py

# Buscar funciones con complejidad > 15
# Buscar funciones con > 200 líneas
```

### Caso 2: Extraer Múltiples Funciones

```bash
# Crear script de extracción en lote
cat > extract_functions.sh << 'EOF'
#!/bin/bash
FUNCTIONS=(
    "_log_with_context:approval_cleanup_utils.py"
    "_get_pg_hook:approval_cleanup_ops.py"
    "_execute_query:approval_cleanup_ops.py"
    "_get_old_requests:approval_cleanup_queries.py"
)

for func_plugin in "${FUNCTIONS[@]}"; do
    func="${func_plugin%%:*}"
    plugin="${func_plugin#*:}"
    python data/airflow/scripts/extract_to_plugin.py \
        approval_cleanup.py \
        "$func" \
        "$plugin" \
        --remove
done
EOF

chmod +x extract_functions.sh
./extract_functions.sh
```

### Caso 3: Análisis Comparativo

```bash
# Antes de refactorizar
python data/airflow/scripts/analyze_approval_cleanup.py > before_analysis.txt

# Después de refactorizar
python data/airflow/scripts/analyze_approval_cleanup.py > after_analysis.txt

# Comparar
diff before_analysis.txt after_analysis.txt
```

## ⚠️ Precauciones

### Antes de Extraer

1. **Hacer backup**:
   ```bash
   cp approval_cleanup.py approval_cleanup.py.backup
   ```

2. **Verificar dependencias**:
   - El script muestra dependencias, pero revisar manualmente
   - Funciones que llaman otras funciones necesitan ambas

3. **Revisar imports**:
   - La función puede necesitar imports adicionales en el plugin

### Después de Extraer

1. **Validar sintaxis**:
   ```bash
   python -m py_compile data/airflow/plugins/approval_cleanup_utils.py
   ```

2. **Actualizar imports en DAG**:
   - Reemplazar llamadas a función local con import del plugin

3. **Ejecutar tests**:
   ```bash
   pytest data/airflow/plugins/tests/
   ```

4. **Probar DAG**:
   ```bash
   airflow dags test approval_cleanup --conf '{"dry_run": true}'
   ```

## 📈 Métricas de Progreso

### Monitorear Progreso

```bash
# Antes
python data/airflow/scripts/analyze_approval_cleanup.py | grep "Líneas totales"

# Después de cada extracción
python data/airflow/scripts/analyze_approval_cleanup.py | grep "Líneas totales"
```

### Objetivos

- [ ] Líneas totales < 2,000
- [ ] Funciones complejas < 5
- [ ] Funciones largas < 10
- [ ] Funciones anidadas = 0
- [ ] Funciones auxiliares en DAG = 0

## 🔗 Integración con CI/CD

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Validar plugins
python data/airflow/scripts/validate_approval_cleanup.py || exit 1

# Validar sintaxis
python -m py_compile data/airflow/plugins/approval_cleanup_*.py || exit 1

# Ejecutar tests
pytest data/airflow/plugins/tests/ || exit 1
```

### GitHub Actions

```yaml
- name: Validate plugins
  run: python data/airflow/scripts/validate_approval_cleanup.py

- name: Run tests
  run: pytest data/airflow/plugins/tests/
```

## 📚 Recursos Relacionados

- `approval_cleanup_REFACTORING.md` - Guía de refactorización
- `approval_cleanup_BEST_PRACTICES.md` - Mejores prácticas
- `README_APPROVAL_CLEANUP.md` - Documentación principal

---

**Última actualización**: 2025-01-15


