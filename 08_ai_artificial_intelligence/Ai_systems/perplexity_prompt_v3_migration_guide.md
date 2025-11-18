# Guía de Migración: Versiones Anteriores a v3

## Resumen

Esta guía proporciona instrucciones paso a paso para migrar desde versiones anteriores del prompt Perplexity (v1, v2, compact, improved, ultimate) a la versión 3 mejorada.

---

## Comparación de Versiones

### Cambios Principales v2 → v3

| Aspecto | v2 | v3 |
|---------|----|----|
| **Estructura** | 7 secciones | 8 secciones (+core_capabilities) |
| **Capacidades** | Implícitas | Explícitas y detalladas |
| **Evaluación de Fuentes** | Básica | Criterios claros |
| **Manejo de Incertidumbre** | Mencionado | Sección dedicada |
| **Restricciones** | Básicas | Expandidas con neutralidad |
| **Tipos de Consulta** | 10 tipos | 11 tipos (+Definition) |
| **Citación** | Básica | Detallada con ejemplos |
| **Formato** | General | Específico y optimizado |

---

## Plan de Migración

### Fase 1: Preparación (1-2 días)

**Tareas:**
- [ ] Revisar documentación de v3
- [ ] Identificar diferencias con versión actual
- [ ] Preparar ambiente de testing
- [ ] Documentar casos de uso actuales

**Checklist:**
```
□ Leer perplexity_prompt_v3_improvements.md
□ Revisar perplexity_prompt_enhanced_v3.md
□ Identificar queries problemáticas actuales
□ Preparar dataset de pruebas
□ Configurar ambiente de staging
```

---

### Fase 2: Implementación en Staging (3-5 días)

**Tareas:**
- [ ] Implementar prompt v3 en ambiente de staging
- [ ] Ejecutar suite de pruebas
- [ ] Comparar resultados v2 vs v3
- [ ] Ajustar según resultados

**Proceso:**

**Paso 1: Reemplazar Prompt**
```python
# Antes (v2)
old_prompt = load_prompt('perplexity_prompt_compact.md')

# Después (v3)
new_prompt = load_prompt('perplexity_prompt_compact_v3.md')
```

**Paso 2: Ejecutar Pruebas**
```python
from perplexity_prompt_v3_testing_suite import run_test_suite

results = run_test_suite(
    prompt_version='v3',
    test_cases='all',
    compare_with='v2'
)
```

**Paso 3: Comparar Resultados**
```python
comparison = compare_versions(
    v2_results=old_results,
    v3_results=new_results,
    metrics=['quality', 'format', 'citations', 'tone']
)
```

---

### Fase 3: Validación (2-3 días)

**Tareas:**
- [ ] Validar calidad de respuestas
- [ ] Verificar formato correcto
- [ ] Confirmar mejoras esperadas
- [ ] Documentar issues encontrados

**Métricas a Validar:**

| Métrica | Objetivo v3 | Cómo Medir |
|---------|-------------|------------|
| **Formato Correcto** | >95% | Validación automática |
| **Citaciones Apropiadas** | >90% | Revisión manual muestra |
| **Tono Consistente** | >95% | Análisis de texto |
| **Longitud Apropiada** | >85% | Por tipo de consulta |
| **Satisfacción Usuario** | >4.5/5 | Encuestas |

---

### Fase 4: Rollout Gradual (5-7 días)

**Estrategia de Rollout:**

**Día 1-2: 10% del tráfico**
- Monitorear métricas de cerca
- Revisar respuestas de muestra
- Ajustar si es necesario

**Día 3-4: 50% del tráfico**
- Comparar métricas v2 vs v3
- Validar mejoras esperadas
- Documentar aprendizajes

**Día 5-7: 100% del tráfico**
- Completar migración
- Desactivar versión anterior
- Documentar resultados finales

---

## Checklist de Migración

### Pre-Migración
- [ ] Backup de configuración actual
- [ ] Documentación de casos edge actuales
- [ ] Métricas baseline establecidas
- [ ] Plan de rollback preparado

### Durante Migración
- [ ] Prompt v3 implementado correctamente
- [ ] Todas las secciones presentes
- [ ] Validación automática activa
- [ ] Monitoreo configurado
- [ ] Alertas configuradas

### Post-Migración
- [ ] Métricas comparadas
- [ ] Mejoras confirmadas
- [ ] Issues documentados
- [ ] Feedback recopilado
- [ ] Optimizaciones aplicadas

---

## Diferencias Específicas por Sección

### 1. Goal Section
**Cambios:** Ninguno significativo
**Acción:** Reemplazo directo

### 2. Core Capabilities (NUEVO)
**Cambios:** Sección completamente nueva
**Acción:** Añadir sección completa
**Impacto:** Mejor razonamiento y evaluación

### 3. Format Rules
**Cambios:**
- Especificaciones más claras (2-4 oraciones inicio)
- Instrucciones para móviles
- Citación más detallada
- Sección Content Density nueva

**Acción:** Reemplazar sección completa
**Impacto:** Mejor formato y legibilidad

### 4. Restrictions
**Cambios:**
- Sección Bias and Neutrality nueva
- Lista expandida de frases prohibidas
- Mejor organización

**Acción:** Reemplazar sección completa
**Impacto:** Mejor neutralidad y objetividad

### 5. Query Type
**Cambios:**
- Nuevo tipo: Definition/Explanation
- Instrucciones más detalladas por tipo
- Mejores ejemplos

**Acción:** Reemplazar sección completa
**Impacto:** Mejor manejo de diferentes consultas

### 6. Planning Rules
**Cambios:**
- Mejor estructuración
- Subsecciones más claras
- Instrucciones más específicas

**Acción:** Reemplazar sección completa
**Impacto:** Mejor planificación y razonamiento

### 7. Output
**Cambios:**
- Directrices expandidas
- Énfasis en consistencia
- Balance comprehensividad/concisión

**Acción:** Reemplazar sección completa
**Impacto:** Mejor calidad de salida

### 8. Personalization
**Cambios:** Ninguno significativo
**Acción:** Reemplazo directo

---

## Script de Migración Automatizada

```python
def migrate_to_v3(old_prompt_path, new_prompt_path):
    """Migra prompt a versión v3"""
    
    # Cargar prompts
    old_prompt = load_file(old_prompt_path)
    new_prompt = load_file(new_prompt_path)
    
    # Validar estructura v3
    required_sections = [
        '<goal>',
        '<core_capabilities>',
        '<format_rules>',
        '<restrictions>',
        '<query_type>',
        '<planning_rules>',
        '<output>',
        '<personalization>'
    ]
    
    for section in required_sections:
        if section not in new_prompt:
            raise ValueError(f"Falta sección requerida: {section}")
    
    # Comparar secciones
    comparison = compare_sections(old_prompt, new_prompt)
    
    # Generar reporte
    report = {
        'sections_added': comparison['added'],
        'sections_modified': comparison['modified'],
        'sections_unchanged': comparison['unchanged'],
        'migration_complexity': calculate_complexity(comparison)
    }
    
    return new_prompt, report

def validate_migration(new_prompt):
    """Valida prompt migrado"""
    validator = PerplexityV3Validator()
    
    # Validar estructura
    structure_valid = validator.validate_structure(new_prompt)
    
    # Validar contenido
    content_valid = validator.validate_content(new_prompt)
    
    return {
        'structure_valid': structure_valid,
        'content_valid': content_valid,
        'ready_for_production': structure_valid and content_valid
    }
```

---

## Plan de Rollback

### Condiciones para Rollback

1. **Métricas Críticas Degradadas**
   - Tasa de error >5%
   - Satisfacción usuario <3.5/5
   - Formato correcto <80%

2. **Issues Críticos**
   - Errores de sistema
   - Respuestas incorrectas frecuentes
   - Problemas de seguridad

### Proceso de Rollback

**Paso 1: Detener Tráfico v3**
```python
def rollback_to_v2():
    """Revertir a versión anterior"""
    # Cambiar prompt
    current_prompt = load_prompt('perplexity_prompt_compact_v3.md')
    previous_prompt = load_prompt('perplexity_prompt_compact.md')
    
    # Activar versión anterior
    activate_prompt(previous_prompt)
    
    # Notificar equipo
    notify_team('Rollback ejecutado - revisar issues')
```

**Paso 2: Documentar Issues**
- Registrar problemas encontrados
- Analizar causas raíz
- Preparar correcciones

**Paso 3: Re-planificar Migración**
- Corregir issues identificados
- Actualizar prompt si es necesario
- Re-ejecutar pruebas

---

## Métricas de Éxito de Migración

### Métricas Técnicas

| Métrica | Baseline v2 | Objetivo v3 | Cómo Medir |
|---------|-------------|-------------|------------|
| Formato Correcto | 85% | >95% | Validación automática |
| Citaciones Apropiadas | 80% | >90% | Revisión manual |
| Tono Consistente | 90% | >95% | Análisis NLP |
| Longitud Apropiada | 75% | >85% | Por tipo consulta |
| Latencia | 2.5s | <2.5s | Tiempo respuesta |

### Métricas de Negocio

| Métrica | Baseline v2 | Objetivo v3 | Cómo Medir |
|---------|-------------|-------------|------------|
| Satisfacción Usuario | 4.2/5 | >4.5/5 | Encuestas |
| Tasa de Re-uso | 60% | >65% | Analytics |
| Tiempo Resolución | 3min | <2.5min | Tiempo promedio |
| Tasa de Error | 5% | <3% | Logs de errores |

---

## Recursos de Apoyo

### Documentación
- `perplexity_prompt_v3_improvements.md` - Cambios detallados
- `perplexity_prompt_enhanced_v3.md` - Prompt completo
- `perplexity_prompt_v3_examples.md` - Ejemplos de uso
- `perplexity_prompt_v3_testing_suite.md` - Suite de pruebas
- `perplexity_prompt_v3_troubleshooting.md` - Solución de problemas

### Herramientas
- Scripts de validación
- Comparadores de versión
- Generadores de reportes
- Monitoreo de métricas

---

## Preguntas Frecuentes

**P: ¿Puedo usar v3 parcialmente?**
R: No recomendado. El prompt está diseñado como sistema completo. Usar partes puede causar inconsistencias.

**P: ¿Cuánto tiempo toma la migración?**
R: 1-2 semanas típicamente, dependiendo de la complejidad del sistema.

**P: ¿Hay breaking changes?**
R: No hay breaking changes, pero hay mejoras significativas que requieren validación.

**P: ¿Puedo mantener ambas versiones?**
R: Sí, para comparación, pero no recomendado para producción.

---

**Última actualización:** 2025-05-13  
**Versión:** 1.0

