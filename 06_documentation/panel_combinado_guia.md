# Guía – Panel Combinado (Sequences + ROI)

Objetivo: integrar en una sola vista KPIs de ejecución (tareas) y de negocio (ROI) en Google Sheets.

## Requisitos
- Hoja de tareas "Origen" (desde `checklist_lanzamiento_10_pasos_google_sheets.csv`)
- Hojas `ROI_Variables` y `ROI_Snapshot` creadas según `roi_snapshot_guia.md`

## Pasos
1) Importar `panel_combinado.csv` como nueva hoja "Panel_Combinado".
2) Verifica que las fórmulas referencien `Origen` y `ROI_Snapshot`; si tus hojas tienen otros nombres, reemplaza los prefijos.
3) Formatos sugeridos:
   - Tarjetas KPI: Total, Completadas, Vencidas, ROI mensual, Payback meses.
   - Gráfico 1: Donut por status (Done/In Progress/Blocked/Todo).
   - Gráfico 2: Barras por owner.
   - Gráfico 3 (opcional): Serie temporal si añades una columna de fecha de actualización.
4) Resaltados condicionales:
   - Vencidas: texto rojo si due_date < HOY y status ≠ Done.
   - ROI mensual > 0: verde; ≤ 0: rojo.
5) Compartir y seguimiento:
   - Crea una vista filtrada por owner para cada responsable.
   - Programa un recordatorio semanal con snapshot PDF.

## Notas
- El panel toma valores de `ROI_Snapshot`; asegúrate de recalcular al actualizar `ROI_Variables`.
- Para escenarios, duplica `ROI_Variables` y usa un selector (celda) con INDIRECT.

---

## How‑to (60 segundos)

1) Importar CSV
   - Archivo → Importar → `panel_combinado.csv` → Insertar hoja nueva (Panel_Combinado)
2) Vincular ROI
   - Asegura que existen `ROI_Variables` y `ROI_Snapshot` (ver `roi_snapshot_guia.md`)
3) Tarjetas KPI
   - Selecciona celdas KPI → Insertar → Tarjeta (o formato destacado)
   - KPI mínimos: Completadas, Vencidas, ROI mensual, Payback
4) Gráficos
   - Insertar → Gráfico → Dona (status) y Barras (owner)
5) Auto‑refresh (opcional)
   - Copia `apps_script_panel_refresh.gs` → Ejecuta `createRefreshTrigger()` (cada 6h)

ASCII (layout sugerido)
```
┌────────────────────────────── Panel_Combinado ──────────────────────────────┐
│  KPI: Total  KPI: Completadas  KPI: Vencidas  KPI: ROI mensual  Payback     │
│                                                                              │
│  [ Donut por status ]                             [ Barras por owner ]       │
│                                                                              │
│  Notas/Alertas: ROI<=0 → revisar variables | Vencidas ↑ → reasignar          │
└──────────────────────────────────────────────────────────────────────────────┘
```

Atajos
- Menú Panel (Apps Script): Refrescar ahora / Programar cada 6h
- Import rápido: `panel_combinado.csv` + `panel_combinado_guia.md`

## Versión Lite (4 KPIs)
- CSV: `panel_combinado_lite.csv`
- KPIs incluidos: Total_tareas, Completadas, Vencidas, ROI_mensual
- Uso recomendado: equipos que necesitan una vista mínima en 1 minuto
- Gráfico sugerido: Dona por status + Tarjetas de ROI y Payback

## Vista Ejecutiva (opcional)
- CSV: `panel_ejecutivo.csv`
- KPIs: Reply_rate_DM, DM_a_Demo_rate, Demo_a_Cierre_rate, ROI_mensual
- Pasos:
  1) Archivo → Importar → `panel_ejecutivo.csv` → Insertar hoja nueva (Ejecutivo)
  2) Inserta 4 tarjetas KPI con esas celdas
  3) Gráfico sugerido: Línea semanal de ROI o barras por canal (si tienes `canal` en Resumen)
  4) Opcional: crea un slicer por `canal` o `stack_detected`

## Versión Enterprise (multi-equipo / región / stack)
- CSV: `panel_combinado_enterprise.csv`
- Qué incluye:
  - KPIs por `region` (Total, Completadas, Vencidas)
  - KPIs por `stack` (Total, Completadas)
  - ROI global (ROI_mensual, Payback_meses)
- Pasos:
  1) Archivo → Importar → `panel_combinado_enterprise.csv` → Insertar hoja nueva (Enterprise)
  2) Inserta 2 gráficos de barras: por región y por stack
  3) Inserta slicers de `region` y `stack` para filtrar paneles
  4) Mantén ROI global visible con tarjeta KPI
  5) Opcional: crea vistas guardadas por región (AMER/EU/LATAM) y stack (HubSpot/GA4/Ads)

## Versión Enterprise (multi-equipo/segmentos)
- CSV: `panel_combinado_enterprise.csv`
- Incluye KPIs segmentables por `region` (columna en Origen) y `stack` (columna en Origen)
- Pasos:
  1) Importa el CSV como "Enterprise"
  2) Crea gráficos por región y por stack a partir de las tablas QUERY incluidas
  3) Añade slicers para `region` y `stack` y aplica a los gráficos/tablones
  4) Mantén el ROI global desde `ROI_Snapshot` (ROI mensual, Payback meses)

## Plantillas de gráficos recomendados

### Dona por status (Done/In Progress/Blocked/Todo)
- Datos: rango de etiquetas (status) y valores (conteo por status) de `Panel_Combinado`
- Tipo: Gráfico de dona
- Personalización:
  - Mostrar etiquetas como porcentaje
  - Colores sugeridos: Done=verde, In Progress=azul, Blocked=rojo, Todo=gris
  - Título: "Distribución por estado"

### Barras por owner (tareas por responsable)
- Datos: eje X = owner, serie = total de tareas (o Completadas vs Vencidas como series apiladas)
- Tipo: Barras agrupadas (o apiladas si comparas estados)
- Personalización:
  - Ordenar por valor descendente
  - Mostrar valores sobre barras
  - Título: "Tareas por owner"

### Línea (opcional) – ROI mensual vs tiempo
- Requiere una columna de fecha de actualización en `Panel_Combinado` o `Resumen`
- Datos: fecha (X), ROI mensual (Y)
- Tipo: Línea
- Personalización: suavizado y marcador en último punto

## Slicers/Segmentadores recomendados
- Insertar → Segmentador (Slicer):
  - `owner` (filtrar por responsable)
  - `status` (Done, In Progress, Blocked, Todo)
  - `prioridad` (si existe columna en Origen)
- Ajustes:
  - Colocar slicers arriba de los gráficos
  - “Aplicar a” → gráficos y tablas seleccionadas del panel

### Checklist/Validación (1 clic)
- En Sheets: Menú Panel → "Validar panel combinado"
- Qué revisa: existencia de hojas `Panel_Combinado` y `ROI_Snapshot`, presencia de "ROI mensual", etiquetas clave ("Completadas", "Vencidas").
- Si aparece ⚠️/❌, corrige nombres de hojas o etiquetas, o revisa referencias a `ROI_Snapshot`.

### Errores comunes y cómo arreglarlos
- ❌ "#REF!" en KPIs de ROI
  - Causa: nombres de hoja distintos a `ROI_Snapshot` o columnas movidas
  - Solución: busca `ROI_Snapshot!` y reemplaza por tu nombre real; revalida con Menú Panel → Validar
- ⚠️ Gráficos vacíos
  - Causa: rango sin datos o filtros activos
  - Solución: edita rango del gráfico al rango con datos; limpia filtros/slicers
- ❌ KPIs de tareas incorrectos (Total/Completadas/Vencidas)
  - Causa: hoja base no se llama `Origen` o estados no coinciden
  - Solución: sustituye `Origen!` por el nombre real; homologa estados: Done, In Progress, Blocked, Todo
- ⚠️ ROI mensual en 0 pese a tener variables
  - Causa: falta coincidencia de etiqueta "ROI mensual" en `ROI_Snapshot`
  - Solución: revisa ortografía/acentos; usa `roi_snapshot_guia.md` para generar la fila correctamente
- ❌ No aparece el menú “Panel”
  - Causa: faltó pegar `apps_script_panel_refresh.gs` o permisos
  - Solución: Extensiones → Apps Script → pega el contenido; ejecuta `onOpen()` o recarga el archivo y otorga permisos
