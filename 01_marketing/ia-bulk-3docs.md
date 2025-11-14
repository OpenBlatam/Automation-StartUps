# IA Bulk — 3 documentos desde una sola consulta

Versión: v1.0.3  ·  Última actualización: 2025-10-30

## Tabla de contenido
- Resumen ejecutivo
- Prioridades Top
- OKRs, DoD
- Automatizaciones clave
- Recetas y Snippets
- Esquemas, Métricas y Checklists
- Anexos (prompts, Kanban, costos, seguridad)
- Operación (SOP, RACI, UAT, Rollback, KPIs)
- SLAs, Riesgos, Pre‑prod, Despliegue
- Retención, Idempotencia, Rate limit, QA, ROI

## Resumen ejecutivo
- Objetivo: generar 3 salidas estandarizadas por consulta con calidad consistente.
- Resultado esperado (90 días): ≥90% éxito, T95 ≤ 10 min, costo/doc ≤ $0.12.
- Alcance: ingesta por lotes, validaciones, post‑proceso, QA, distribución y costos.

## Prioridades Top (Impacto/Escenario/Esfuerzo)
- Lotes desde Sheets (3 docs por fila) — Alto / 14 días / Medio
- QA semántico + compliance — Alto / 14 días / Medio
- Cost tracking por job/cliente — Medio / 3 días / Bajo

## OKRs Trimestrales
- O1: ≥90% de lotes completados sin intervención
- O2: Costo/doc ≤ $0.12 promedio
- O3: Tiempo a entrega T95 ≤ 10 min por lote

## Definición de Listo (DoD)
- Casos: 1 feliz, 2 errores, 1 edge (timeout/duplicado)
- Observabilidad: JobID, tiempos, tokens, costo, enlaces
- Reintentos: 3x backoff exponencial + marcas de estado
- Idempotencia por hash de parámetros

---

## 10 Automatizaciones Clave (mini‑blueprints + KPI)

1) Ingesta por lotes desde Sheets
- Stack: Sheets, Apps Script, API IA, Drive
- Flujo: Estado “pendiente” → generar 3 docs → “completado” + enlaces
- KPI: docs/h, éxito job
- Ahorro/mes: 10–20 h

2) Validación de prompts/campos
- Stack: Apps Script
- Flujo: Reglas de longitud, variables obligatorias, ejemplos
- KPI: tasa de error previo
- Ahorro/mes: 2–3 h

3) Post‑procesado y estilos de marca
- Stack: Docs/Slides API, Apps Script
- Flujo: Estilos, cabeceras, CTA, disclaimers
- KPI: revisiones por doc
- Ahorro/mes: 4–6 h

4) QA semántico y compliance
- Stack: OpenAI + reglas
- Flujo: Tono/keywords/CTA/compliance → score semáforo
- KPI: fallos QA
- Ahorro/mes: 3–5 h

5) Distribución multicanal
- Stack: Gmail, Slack, Notion/Confluence
- Flujo: Enviar según tipo; registrar destinatarios
- KPI: tiempo a entrega
- Ahorro/mes: 2–3 h

6) Cost tracking por job/cliente
- Stack: Sheets (CostosIA), Looker Studio
- Flujo: Guardar tokens, costo, tiempos; dashboard
- KPI: costo/doc, margen
- Ahorro/mes: 1–2 h

7) Reintentos con backoff + colas
- Stack: Triggers Apps Script
- Flujo: Reintentos 1s/2s/4s; marcar fallidos
- KPI: ratio recuperación
- Ahorro/mes: 1–2 h

8) Indexado vectorial para búsqueda
- Stack: Embeddings, vector DB
- Flujo: Guardar embeddings por doc para RAG
- KPI: tiempo de hallazgo
- Ahorro/mes: 1–2 h

9) Auditoría y trazabilidad
- Stack: Logs firmados
- Flujo: prompt, modelo, costos, enlaces, duración
- KPI: MTTR soporte
- Ahorro/mes: 1–2 h

10) One‑pager ejecutivo cross‑doc
- Stack: OpenAI
- Flujo: Con 3 docs → resumen ejecutivo con insights/acciones
- KPI: tiempo decisión
- Ahorro/mes: 2–3 h

---

## Recetas Zapier/Apps Script
- Sheets (New/Updated Row estado=pending) → 3x Webhook (IA prompts) → Google Docs (create) → Slack (notify)
- Webhook job=error → Delay+Retry (exponencial) → If fail → Create Asana Task

---

## Snippets de Apps Script

Procesar 3 documentos por fila:

```javascript
function generarTresDocsPorFila() {
  const sh = SpreadsheetApp.getActive().getSheetByName('Pedidos');
  const rows = sh.getDataRange().getValues();
  for (let i = 1; i < rows.length; i++) {
    const [id, prompt, estado] = rows[i];
    if (estado !== 'pendiente' || !prompt) continue;
    const jobId = Utilities.getUuid();
    try {
      const tipos = ['brief', 'articulo', 'post'];
      const enlaces = tipos.map(t => crearDocIAConPostProceso(prompt, t, jobId)); // implementa
      sh.getRange(i + 1, 3).setValue('completado');
      sh.getRange(i + 1, 4, 1, 3).setValues([enlaces]);
      logCosto(jobId, id, calcularCosto(enlaces)); // implementa
    } catch (e) {
      sh.getRange(i + 1, 3).setValue('error');
    }
  }
}
```

Reintentos exponenciales simples:

```javascript
function retry(fn, max = 3) {
  for (let i = 0; i < max; i++) {
    try { return fn(); } catch(e) { Utilities.sleep(2 ** i * 1000); }
  }
  throw new Error('Max retries reached');
}
```

---

## Esquemas de Sheets
- Pedidos: ID | Prompt | Estado(pendiente/completado/error) | EnlaceBrief | EnlaceArticulo | EnlacePost
- CostosIA: JobID | Cliente | Tokens | CostoUSD | Fecha

## Plantillas e IDs requeridos
- Docs/Slides: plantillas de marca (nombres y IDs)
- Cuenta de servicio con acceso a Drive y Sheets
- API IA: clave y modelo definidos; límites por cliente

---

## Métricas y Fórmulas
- Tasa éxito lotes: =COUNTIF(Pedidos!C:C,"completado")/COUNTA(Pedidos!C:C)
- Costo promedio/doc: =SUM(CostosIA!D:D)/COUNT(Pedidos!A:A)
- T95 de entrega ≤ 10 min

---

## Checklist por automatización
- Setup: accesos, plantillas Docs, IDs, límites de cuota
- Pruebas: 1 feliz, 1 error forzado, 1 timeout
- Métricas: fuente, fórmula, objetivo
- Operación: dueño, SLO, fallback manual
- Riesgos: alucinaciones, costos, duplicados, PII

---

## Anexos prácticos

### Prompts por industria (ejemplos)
- Marketing: "Genera 3 salidas: brief, artículo 1500 palabras, 5 posts LinkedIn sobre {tema}, tono marca {guía}."
- Educación: "Crea guía docente, resumen para alumnos y cuestionario de 10 preguntas a partir de {contenido}."
- Legal: "Produce contrato base, resumen ejecutivo y checklist de riesgos para {caso}, sin asesoría legal."

### Checklist Kanban
- Backlog: definición de 3 docs por consulta, SLAs, costos objetivo
- Ready: plantillas y estilos, validaciones de prompts
- Doing: logs de JobID, tokens y tiempos; alertas de error
- Review: QA semántico y compliance; pruebas idempotencia
- Done: dashboard de costos/éxito, runbook, propietario

### Plantilla de costos (Sheets)
- Columnas: JobID | Cliente | Modelo | TokensPrompt | TokensOutput | CostoUSD | DuracionSeg | Fecha
- Fórmulas: costo/doc y costo/lote; umbrales de alerta (condicionales)

### Seguridad mínima
- Idempotencia por hash de parámetros; evitar reprocesos
- No persistir texto sensible; usar referencias/IDs

---

## SOP de Operación (diario/semanal)
- Diario
  - Revisar hoja `Pedidos`: errores, tiempos, cuellos de botella
  - Validar costos por JobID en `CostosIA`
  - Atender alertas de fallos y reintentar con backoff
- Semanal
  - Auditar muestras de calidad (QA semántico)
  - Revisar plantillas y prompts versionados
  - Optimizar costos (modelo, temperatura, longitud)

## RACI (resumen)
- Responsable (R): Content Ops
- Aprobador (A): Marketing Lead
- Consultados (C): Legal, Ingeniería
- Informados (I): Ventas

## Plan de Pruebas (UAT)
- Casos: fila válida (completado); prompt inválido (bloqueo); timeout; duplicado (idempotencia)
- Criterios: éxito ≥ 90%; T95 ≤ 10 min; costo/doc ≤ $0.12

## Rollback rápido
- Pausar trigger time‑driven
- Revertir última versión de plantillas Docs/Slides
- Despublicar entregas automáticas si el QA falla masivamente

## Plantilla de KPIs (Sheets)
- Columnas: Fecha | Lotes | Éxito% | T95(min) | Tokens | CostoUSD | Costo/Doc | Reintentos

---

## SLAs/SLOs sugeridos
- Éxito de lotes: SLO ≥ 90%
- Tiempo de entrega: SLO T95 ≤ 10 min
- Costo por doc: SLO ≤ umbral definido por cliente

## Matriz de riesgos (resumen)
- Timeouts por cuotas → Mitigación: scheduling fuera de pico
- Alucinaciones/errores de hecho → Mitigación: checks y fuentes
- Duplicados por reintentos → Mitigación: idempotencia con hash

## Checklist pre‑producción
- Validaciones de prompt activas
- Plantillas de Docs/Slides probadas
- Triggers y cuotas confirmados
- Dashboards de costos/éxito listos

## Guía de despliegue
1) Configurar hojas `Pedidos` y `CostosIA`
2) Cargar plantillas y estilos de marca
3) Programar trigger time‑driven (cron)
4) Correr piloto de 10–20 filas y ajustar

---

## Retención de datos
- Logs IA (tokens/costos): 180 días
- Outputs sensibles: 30 días o según contrato; preferir enlaces
- Prompts: no guardar texto con PII, usar referencias

## Idempotencia (Apps Script)
```javascript
function computeHash(parts) {
  const str = JSON.stringify(parts);
  return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, str));
}
```

## Rate limit y cuotas
```javascript
function withRateLimit(fn, pauseMs=1100, tries=3) {
  for (let i=0;i<tries;i++){ try{ return fn(); }catch(e){ Utilities.sleep(pauseMs*(i+1)); } }
  throw new Error('Rate limit exceeded');
}
```

## QA IA (reglas mínimas)
- Chequeos: tono marca, keywords, CTA, claims con fuente
- Semáforo de calidad y revisión humana si “rojo”

## ROI y límites de costo
- Costo/doc objetivo ≤ $0.12; alerta si > $0.15
- Éxito ≥ 90%; T95 ≤ 10 min; reintentos ≤ 3

## Gobierno y Accesos
- Roles: Marketing Lead (A), Content Ops (R), Ingeniería/Legal (C), Ventas (I)
- Accesos: cuenta de servicio para Drive/Docs, claves IA en secret manager
- Revisión trimestral de plantillas y versiones

## Respuesta a Incidentes
- P0 (costos fuera de control): pausar trigger, bajar tamaño de salida o modelo, notificar; ETA ≤ 1 h
- P1 (outputs con riesgo legal): detener distribución, marcar confidencial, revisión Legal; ETA ≤ 24 h

## Plan de Formación
- S1 Operativo (60’): flujos, cuotas, KPIs
- S2 Técnico (90’): Apps Script avanzado, idempotencia, QA IA

## Estimador de Presupuesto
- Tokens prompt/output x tarifa modelo + almacenamiento Drive
- Slack/Notion automations (si aplica)

## Ejemplos técnicos
- Payload de job IA (JSON):
```json
{ "jobId": "J-001", "prompt": "...", "outputs": ["brief", "articulo", "post"], "metadata": {"cliente": "ACME"} }
```

---

## Recursos útiles
- Plantillas de comunicación: `PLANTILLAS_COMUNICACION.md`
- Prompts base por industria: `PROMPTS_BASE.md`


