# Perplexity Prompt v3 — Mejores Prácticas Operativas

## Propósito

Establecer lineamientos accionables para equipos que usan la versión 3 del prompt de Perplexity en entornos de producción, soporte y entrenamiento. Este documento se complementa con:

- `perplexity_prompt_enhanced_v3.md` (definición completa del sistema)
- `perplexity_prompt_compact_v3.md` (versión lista para usar)
- `perplexity_prompt_v3_examples.md` (casuística por tipo de consulta)
- `perplexity_prompt_v3_testing_suite.md` (aseguramiento de calidad)

---

## Flujo de Trabajo Recomendado

1. **Preparación de la Consulta**
   - Clarificar tipo de query (usar sección `<query_type>` como checklist).
   - Identificar datos obligatorios (fechas, ubicaciones, unidades).
   - Reunir resultados de búsqueda relevantes y ordenarlos por autoridad.

2. **Ejecución con el Prompt v3**
   - Cargar versión compacta para entornos operativos.
   - Verificar que el sistema_prompt incluya secciones completas (sin truncamiento).
   - Activar ejemplos de referencia (`few-shot`) si el modelo tiende a olvidar citas.

3. **Revisión Post-Respuesta**
   - Aplicar checklist rápido (inicio sin encabezado, citas correctas, conclusión presente).
   - Confirmar que cada afirmación citada tenga fuente válida.
   - Guardar hallazgos para retroalimentar al equipo (usar tabla definida en testing suite).

---

## Checklist Express (Sí / No)

| Paso | Pregunta | Sí | No |
|------|----------|----|----|
| Inicio | ¿La respuesta abre con 2-4 oraciones sin encabezado? | ☐ | ☐ |
| Formato | ¿Se usaron encabezados `##` solo después del resumen inicial? | ☐ | ☐ |
| Listas | ¿No hay listas con un único ítem o anidadas? | ☐ | ☐ |
| Tablas | ¿Las comparaciones usaron tabla con ≤6 columnas? | ☐ | ☐ |
| Código/Math | ¿Los bloques tienen lenguaje y LaTeX correcto? | ☐ | ☐ |
| Citas | ¿Todas las oraciones con datos externos tienen `[n]`? | ☐ | ☐ |
| Neutralidad | ¿Se presentan múltiples perspectivas si aplica? | ☐ | ☐ |
| Cierre | ¿Concluye con 2-3 oraciones sin pregunta final? | ☐ | ☐ |

Imprime o integra este checklist en la herramienta de QA para revisiones rápidas.

---

## Dos y No Hacer

| Dos | No Hacer |
|-----|---------|
| Usar `perplexity_prompt_compact_v3.md` en producción para minimizar tokens. | Mezclar directrices de versiones anteriores; genera inconsistencias. |
| Mantener registros de consultas representativas para comparar regresiones. | Insertar contexto adicional dentro del prompt sin documentarlo. |
| Activar modo de razonamiento explícito solo cuando el caso lo requiera. | Forzar listas numeradas cuando el prompt indica tabla para comparaciones. |
| Reentrenar al equipo trimestralmente usando `perplexity_prompt_v3_examples.md`. | Permitir respuestas sin citas cuando haya fuentes disponibles. |
| Escalar incidentes críticos con referencia cruzada al Testing Suite. | Modificar secciones `<restrictions>` sin revisar impactos legales. |

---

## Entrenamiento de Equipos

1. **Sesión Teórica (1 hora)**
   - Repasar secciones `<goal>`, `<format_rules>`, `<restrictions>`.
   - Analizar casos reales de incumplimiento.

2. **Laboratorio Guiado (2 horas)**
   - Usar ejemplos de `perplexity_prompt_v3_examples.md`.
   - Revisar respuestas con el Checklist Express.

3. **Evaluación**
   - 5 consultas mixtas (académica, noticias, coding, URL, creativa).
   - 90% de conformidad para certificación interna.

4. **Refrescos Mensuales**
   - Nuevos casos edge (multilenguaje, datos faltantes, fuentes conflictivas).
   - Actualizar documentación según hallazgos.

---

## Integración Técnica

| Entorno | Recomendación |
|---------|---------------|
| **APIs (OpenAI/Anthropic)** | Insertar prompt completo en `system`. Usar control de versiones (hash). |
| **Runners locales** | Montar prompt desde archivo para evitar errores de copy-paste. Automatizar verificación de longitud. |
| **Pipelines CI/CD** | Incluir `perplexity_prompt_v3_testing_suite.md` como job de validación. Guardar reportes JSON. |
| **Dashboards internos** | Mostrar métricas de conformidad (ver Testing Suite) + incidentes abiertos. |

---

## Manejo de Excepciones

1. **Consultas con datos insuficientes**
   - Indicar explícitamente qué parte carece de evidencia.
   - Usar lenguaje de incertidumbre permitido (“datos sugieren”).

2. **Solicitudes fuera de alcance**
   - Referenciar sección `<restrictions>` para justificar negativa.
   - Redirigir a equipo legal/ética si aplica.

3. **Instrucciones conflictivas del usuario**
   - Priorizar el prompt del sistema.
   - Documentar la decisión y compartir con el owner del proceso.

---

## Métricas Sugeridas

- **Conformidad semanal:** % de respuestas que pasan checklist sin correcciones.
- **Tiempo promedio de revisión:** objetivo <4 minutos.
- **Alertas críticas:** número de violaciones a privacidad o exposición de prompt (objetivo 0).
- **Adopción de ejemplos:** % de equipo certificado que usa la librería de casos.

---

## Actualización y Gobernanza

- Responsable: Equipo AI Ops (nombrar owner).  
- Cadencia de revisión: mensual o tras cambios de modelo.  
- Cambios mayores: documentar en `perplexity_prompt_v3_improvements.md`.  
- Comunicación: changelog interno + sesión de alineación.

---

## Próximas Iteraciones Sugeridas

1. Integrar checklist en la herramienta de edición (via extensión o botón QA).  
2. Automatizar alertas cuando el modelo introduzca frases prohibidas.  
3. Crear versión multilingüe del prompt (es/en) con sección de compatibilidad.  
4. Publicar playbook breve para stakeholders no técnicos.




