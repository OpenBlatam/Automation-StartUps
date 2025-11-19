# 🔧 Guía de Mantenimiento de DAGs

Guía para mantener y actualizar la organización de DAGs.

## Tareas de Mantenimiento Regular

### Semanal
- [ ] Revisar DAGs fallidos en Airflow UI
- [ ] Verificar logs de errores
- [ ] Actualizar documentación si hay cambios

### Mensual
- [ ] Ejecutar `./validate_structure.sh`
- [ ] Generar reporte: `./generate_report.sh`
- [ ] Revisar DAGs sin documentación
- [ ] Verificar dependencias entre DAGs
- [ ] Limpiar DAGs obsoletos o no utilizados

### Trimestral
- [ ] Revisar y actualizar BEST_PRACTICES.md
- [ ] Actualizar DAG_DEPENDENCIES.md
- [ ] Revisar y optimizar DAGs grandes (>1000 líneas)
- [ ] Consolidar DAGs similares si es posible
- [ ] Actualizar estadísticas en STATISTICS.md

## Agregar un Nuevo DAG

### Proceso Completo

1. **Identificar ubicación**
   ```bash
   # Usar find_dag.sh para encontrar DAGs similares
   ./find_dag.sh -c "funcionalidad_similar"
   ```

2. **Generar template**
   ```bash
   ./generate_dag_template.sh
   # Seguir las instrucciones interactivas
   ```

3. **Implementar lógica**
   - Seguir BEST_PRACTICES.md
   - Agregar docstrings
   - Implementar manejo de errores

4. **Documentar**
   - Agregar a QUICK_REFERENCE.md si es común
   - Actualizar README del área
   - Agregar a DAG_INDEX.md si es necesario

5. **Validar**
   ```bash
   ./validate_structure.sh
   ```

6. **Probar**
   - Probar en ambiente de desarrollo
   - Verificar logs
   - Validar dependencias

## Mover un DAG Existente

### Proceso

1. **Identificar nueva ubicación**
   - Verificar estructura en STRUCTURE.md
   - Confirmar área y subcarpeta

2. **Mover archivo**
   ```bash
   mv ruta_antigua/dag.py nueva_ruta/dag.py
   ```

3. **Actualizar referencias**
   - Buscar referencias en otros DAGs
   - Actualizar DAG_DEPENDENCIES.md
   - Actualizar documentación

4. **Validar**
   ```bash
   ./validate_structure.sh
   ```

## Eliminar un DAG

### Checklist Antes de Eliminar

- [ ] Verificar que no está en uso
- [ ] Revisar dependencias en DAG_DEPENDENCIES.md
- [ ] Confirmar con equipo responsable
- [ ] Hacer backup si es necesario
- [ ] Documentar razón de eliminación

### Proceso

1. **Verificar dependencias**
   ```bash
   ./find_dag.sh -c "nombre_dag"
   ```

2. **Eliminar archivo**
   ```bash
   rm ruta/dag.py
   ```

3. **Limpiar referencias**
   - Remover de QUICK_REFERENCE.md
   - Remover de DAG_INDEX.md
   - Actualizar DAG_DEPENDENCIES.md
   - Actualizar README del área

## Refactorizar un DAG

### Cuándo Refactorizar

- DAG tiene >1000 líneas
- Lógica duplicada con otros DAGs
- Múltiples responsabilidades
- Dificultad para mantener

### Proceso

1. **Analizar DAG actual**
   - Identificar responsabilidades
   - Encontrar código duplicado
   - Identificar dependencias

2. **Planificar refactorización**
   - Dividir en módulos si es necesario
   - Extraer funciones comunes
   - Simplificar lógica

3. **Implementar cambios**
   - Hacer cambios incrementales
   - Mantener funcionalidad existente
   - Agregar tests si es posible

4. **Validar**
   - Probar en desarrollo
   - Verificar que funcionalidad se mantiene
   - Actualizar documentación

## Actualizar Documentación

### Cuándo Actualizar

- Nuevo DAG agregado
- DAG movido o eliminado
- Cambios en dependencias
- Cambios en estructura

### Archivos a Actualizar

1. **README del área** - Si afecta área específica
2. **QUICK_REFERENCE.md** - Si es DAG común
3. **DAG_INDEX.md** - Si cambia ubicación
4. **DAG_DEPENDENCIES.md** - Si cambian dependencias
5. **STATISTICS.md** - Si afecta estadísticas

## Resolver Problemas Comunes

### DAG no aparece en Airflow UI

1. Verificar sintaxis Python
   ```bash
   python -m py_compile ruta/dag.py
   ```

2. Revisar logs de Airflow
3. Verificar imports
4. Verificar que está en carpeta correcta

### DAG falla consistentemente

1. Revisar logs del task
2. Verificar conexiones
3. Validar datos de entrada
4. Verificar variables de Airflow
5. Revisar dependencias

### Performance lenta

1. Revisar queries de base de datos
2. Verificar recursos asignados
3. Considerar paralelización
4. Revisar lógica de procesamiento

## Herramientas de Mantenimiento

### Scripts Disponibles

- `find_dag.sh` - Buscar DAGs
- `generate_dag_template.sh` - Generar templates
- `validate_structure.sh` - Validar estructura
- `generate_report.sh` - Generar reportes

### Comandos Útiles

```bash
# Contar DAGs por área
for area in */; do echo "$area: $(find "$area" -name '*.py' | wc -l)"; done

# Encontrar DAGs grandes
find . -name "*.py" -exec wc -l {} \; | sort -rn | head -10

# Encontrar DAGs modificados recientemente
find . -name "*.py" -mtime -7

# Buscar imports específicos
grep -r "import pandas" . --include="*.py"
```

## Mejores Prácticas de Mantenimiento

1. **Versionado**: Usar Git para cambios
2. **Documentación**: Mantener actualizada
3. **Testing**: Probar en desarrollo primero
4. **Comunicación**: Notificar cambios importantes
5. **Backup**: Hacer backup antes de cambios grandes
6. **Validación**: Ejecutar validate_structure.sh regularmente

## Checklist de Mantenimiento Mensual

- [ ] Ejecutar `./validate_structure.sh`
- [ ] Generar reporte: `./generate_report.sh`
- [ ] Revisar DAGs fallidos
- [ ] Actualizar documentación obsoleta
- [ ] Revisar y limpiar DAGs no utilizados
- [ ] Verificar dependencias
- [ ] Actualizar estadísticas si hay cambios significativos

---

*Mantener esta guía actualizada con nuevas prácticas y herramientas*

