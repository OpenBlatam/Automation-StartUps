# Perplexity Prompt v3 — Testing & QA Suite

## Objetivo

Establecer un plan de pruebas reproducible que garantice que cualquiera de las versiones del prompt (compacta o completa) mantenga la calidad esperada tras cambios o integraciones.

---

## Tipos de Prueba

| Tipo | Propósito | Métrica Clave | Frecuencia |
|------|-----------|---------------|------------|
| **Validación Funcional** | Confirma que todas las reglas del prompt se cumplen | % de casos conformes | Cada release |
| **Consistencia de Formato** | Verifica encabezados, listas, tablas y citas | Número de violaciones por 10 respuestas | Semanal |
| **Cobertura por Tipo de Query** | Asegura que todos los `query_type` funcionen | Tipos cubiertos / totales | Mensual |
| **Regresión** | Detecta degradaciones tras cambios | Variación en métricas base | Después de cada cambio significativo |
| **Stress Test** | Evalúa comportamiento con prompts largos o ambiguos | Tokens consumidos, tasas de error | Trimestral |

---

## Casos de Prueba Base

1. **Inicio sin encabezado**  
   - Entrada: consulta genérica  
   - Verificación: las primeras 2-4 oraciones resumen sin usar encabezados ni negritas.

2. **Citación múltiple**  
   - Entrada: tema con fuentes conflictivas  
   - Esperado: uso de citas `[1][2]` y mención de discrepancias.

3. **Lista simple vs. tabla**  
   - Entrada: comparación de proveedores  
   - Esperado: tabla Markdown con ≤6 columnas, sin listas anidadas.

4. **Math + Código**  
   - Entrada: cálculo + script  
   - Verificación: fórmulas en LaTeX (`\(`, `\[`), bloque ` ```python ` con lenguaje.

5. **Query Type: Recent News**  
   - Entrada: noticias con timestamps  
   - Esperado: lista con encabezados en negritas por noticia, citas por fuente.

6. **Query Type: Translation**  
   - Entrada: texto multilingüe  
   - Esperado: traducción directa sin citas ni explicaciones.

7. **URL Lookup**  
   - Entrada: URL sola  
   - Esperado: solo info del resultado [1], conclusión terminando en `[1]`.

8. **Creative Writing**  
   - Entrada: prompt narrativo  
   - Verificación: no usa citas, respeta instrucciones creativas específicas.

9. **Edge Case: Lista de un elemento**  
   - Entrada: requiere un punto único  
   - Esperado: información integrada en párrafo, sin lista de un ítem.

10. **Bias Check**  
    - Entrada: tema controversial  
    - Verificación: múltiples perspectivas, lenguaje neutral, citas equilibradas.

---

## Métricas de Calidad

- **Conformidad General:** ≥95% de pasos pasan sin intervención.  
- **Errores de Formato:** ≤1 por cada 10 respuestas.  
- **Tiempo de Revisión:** <5 min por respuesta en QA manual.  
- **Cobertura de Query Types:** 100% al menos una vez por ciclo mensual.  
- **Consistencia de Citaciones:** 0 errores en sintaxis `[n]`.  
- **Violaciones Críticas (privacidad, prompt exposure):** 0 toleradas.

---

## Procedimiento de QA Manual

1. Seleccionar 5 consultas representativas (al menos 3 tipos distintos).  
2. Ejecutar respuesta con la versión del prompt bajo prueba.  
3. Validar contra checklist (ver sección anterior).  
4. Registrar observaciones en tabla de control con: fecha, tipo, resultado, acciones.  
5. Elevar issues críticos inmediatamente; issues menores se agrupan para próximos releases.

---

## Automatización Sugerida

```python
import json

TEST_CASES = [
    {"id": "start_no_header", "query": "Summarize EV battery breakthroughs", "type": "general"},
    {"id": "recent_news", "query": "Latest updates on EU digital markets act", "type": "recent_news"},
    # ...
]

def evaluate_response(response: str) -> dict:
    """Reglas básicas: sin encabezado inicial, citas correctas, etc."""
    findings = []
    if response.strip().startswith("##"):
        findings.append("Header violation at start")
    if "[ " in response or " ]" in response:
        findings.append("Citation spacing issue")
    return {"pass": not findings, "issues": findings}
```

Automatiza la ejecución vía API (OpenAI, Anthropic, etc.), almacena resultados en JSON y genera reportes en el dashboard interno.

---

## Troubleshooting Rápido

| Síntoma | Causa Probable | Acción |
|---------|----------------|--------|
| Comienza con encabezado | Prompt truncado o versión incorrecta | Verificar que `<format_rules>` esté completo |
| Citas tipo `[1, 2]` | Modelo sin refuerzo de ejemplo | Añadir few-shot recordando `[1][2]` |
| Listas anidadas | Usuario solicitó niveles múltiples | Recordar uso de tablas o separar listas |
| Referencia a \"knowledge cutoff\" | Prompt faltante en `<restrictions>` | Confirmar que sección exista en versión usada |
| Texto sin conclusión | Modelo quedó sin instrucciones de cierre | Revisar sección **Answer End** |

---

## Control de Versiones

- Mantener tabla comparativa (`perplexity_prompt_comparison.md`).  
- Registrar cambios en `perplexity_prompt_v3_improvements.md`.  
- Asociar cada release a hash git + fecha.  
- Añadir etiqueta `QA_passed` cuando supere checklist completo.

---

## Próximos Pasos

1. Integrar pruebas automáticas en pipeline CI.  
2. Crear dashboard con métricas de conformidad.  
3. Añadir casos específicos por vertical (finanzas, salud, legal).  
4. Revisar métricas mensualmente y ajustar prompt según hallazgos.




