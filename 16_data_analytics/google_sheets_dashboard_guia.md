# Guía Google Sheets – Dashboard mínimo SaaS IA Marketing

## Importación
1) Archivo → Importar → Subir `dashboard_minimo_saas_dm_google_sheets.csv`
2) Seleccionar “Reemplazar hoja” y “Detectar automáticamente separador”
3) Confirmar que las fórmulas en columnas J, K y N se evaluaron

### Importar Panel combinado (opcional)
- Archivo → Importar → Subir `panel_combinado.csv` → Insertar hoja nueva (sugerido: Panel_Combinado)
- Sigue `panel_combinado_guia.md` para dejar listas tarjetas KPI + 2 gráficos

### Auto-refresh (Apps Script)
- Copia `apps_script_panel_refresh.gs` (sección Panel combinado) en Extensiones → Apps Script.
- Ejecuta `refreshNow()` para probar y `createRefreshTrigger()` para programar cada 6h.

### Botón Refresh manual (opcional)
1) Insertar → Dibujo → Forma con texto “Refresh KPIs”.
2) Asignar script → `refreshNow`.
3) También puedes usar el menú “Panel” (Refrescar ahora / Programar cada 6h) que aparece al abrir la hoja.

### Exportación PDF semanal (opcional)
- Usa Menú “Panel” → Exportar PDF (Ejecutivo) para un envío manual inmediato.
- Programa envíos automáticos: Menú “Panel” → Programar PDF semanal (Viernes 9:00).

## Troubleshooting rápido
- KPIs sin calcular (J/K/N vacíos): ejecuta `rellenarKpis()` o revisa que el separador decimal sea correcto.
- Gráficos vacíos: verifica el rango de datos y que no haya filtros activos.
- ROI en 0: confirma que `ROI_Snapshot` existe y tiene la fila “ROI mensual”.
- No aparece menú “Panel”: pega `apps_script_panel_refresh.gs` y recarga el archivo.

## Formato y métricas
- Formato columnas:
  - `fecha`: Date (YYYY-MM-DD)
  - `sent/opened/replied/booked_demo/closed_won`: Number, 0 decimales
  - `dm_demo_rate`, `demo_close_rate`: Percent, 1 decimal
  - `roi_*`: Currency (USD)
- Ancho recomendado: 120–140 px por columna

## Conditional Formatting (CF)
- `dm_demo_rate` ≥ 0.10 → verde; 0.05–0.10 → ámbar; < 0.05 → rojo
- `demo_close_rate` ≥ 0.30 → verde; 0.15–0.30 → ámbar; < 0.15 → rojo
- `roi_total_usd` > 0 → verde; ≤ 0 → rojo

## Pivots sugeridos
1) Rendimiento por canal/variante
   - Rows: `canal`, `variant`
   - Values: SUM `sent`, SUM `replied`, AVG `dm_demo_rate`, AVG `demo_close_rate`, SUM `roi_total_usd`
2) Por stack_detected
   - Rows: `stack_detected`
   - Values: AVG `dm_demo_rate`, AVG `demo_close_rate`, SUM `roi_total_usd`
3) Funnel semanal
   - Rows: `fecha`
   - Values: SUM `sent/opened/replied/booked_demo/closed_won`

## Gráficos rápidos
- Línea: `fecha` vs `dm_demo_rate` (promedio diario)
- Barras apiladas: `replied`, `booked_demo`, `closed_won` por `canal`
- Barras: `roi_total_usd` por `variant`

## Scripting opcional (Apps Script)
```javascript
function rellenarKpis() {
  const sh = SpreadsheetApp.getActiveSheet();
  const last = sh.getLastRow();
  // Rellenar fórmulas en rango J2:Nlast si faltan
  const formulas = [
    '=IF(F2>0,H2/F2,0)', // J dm_demo_rate
    '=IF(H2>0,I2/H2,0)', // K demo_close_rate
    '',                  // L roi_time_usd (manual)
    '',                  // M roi_perf_usd (manual)
    '=L2+M2'             // N roi_total_usd
  ];
  for (let r = 2; r <= last; r++) {
    sh.getRange(r,10).setFormula(formulas[0].replaceAll('2', r));
    sh.getRange(r,11).setFormula(formulas[1].replaceAll('2', r));
    sh.getRange(r,14).setFormula(formulas[4].replaceAll('2', r));
  }
}
```

## Buenas prácticas
- Congelar fila 1; filtrar por `fecha`, `canal`, `variant`
- Validaciones de datos en `variant` (lista): v_premium, v_principal, micro_dm, vip
- Protege celdas de fórmulas (J, K, N)
- Crea una hoja “Configuración” con umbrales de CF y referencias


---

## Resumen semanal (vista rápida con fórmulas y gráficos)

### 1) Columna auxiliar de semana (ISO)
En la hoja de datos, agrega una columna nueva `semana_iso` (columna O, por ejemplo):

```
=TEXT(A2, "yyyy") & "-W" & TEXT(ISOWeekNum(A2), "00")
```

- Si tu Sheets no tiene `ISOWeekNum`, usa: `=TEXT(A2, "yyyy")&"-W"&TEXT(WEEKNUM(A2,2),"00")`

### 2) Tabla dinámica (Pivot) – Resumen por semana y canal
- Insertar → Tabla dinámica → Fuente: hoja de datos completa
- Filas: `semana_iso`, `canal`
- Valores: 
  - SUM `sent`, SUM `opened`, SUM `replied`, SUM `booked_demo`, SUM `closed_won`
  - AVG `dm_demo_rate`, AVG `demo_close_rate`
  - SUM `roi_total_usd`
- Orden: `semana_iso` ascendente

### 3) Alternativa sin pivot (QUERY)
En una hoja “Resumen_Semana” crea las siguientes fórmulas:

Totales por semana y canal
```
=QUERY({A2:O, O2:O},
 "select Col16, Col2, sum(Col5), sum(Col6), sum(Col7), sum(Col8), sum(Col9), avg(Col10), avg(Col11), sum(Col14) \
  where Col1 is not null \
  group by Col16, Col2 \
  label sum(Col5) 'sent', sum(Col6) 'opened', sum(Col7) 'replied', sum(Col8) 'booked_demo', sum(Col9) 'closed_won', \
        avg(Col10) 'dm_demo_rate', avg(Col11) 'demo_close_rate', sum(Col14) 'roi_total_usd'",
 0)
```
Ajusta índices si cambian posiciones de columnas.

### 4) KPI tarjetas (celdas resaltadas)
En “Resumen_Semana”, crea KPIs con `=AVERAGE`, `=SUM` filtrando última semana:

- Semana más reciente (en B1):
```
=INDEX(SORT(UNIQUE(FILTER(Resumen!A2:A, Resumen!A2:A<>"")),1,TRUE), COUNTA(UNIQUE(FILTER(Resumen!A2:A, Resumen!A2:A<>""))) )
```
- Respuesta (DM→Demo) p. ej. en B2:
```
=AVERAGE(FILTER(Resumen!H2:H, Resumen!A2:A=B1))
```
- Demo→Cierre (B3):
```
=AVERAGE(FILTER(Resumen!I2:I, Resumen!A2:A=B1))
```
- ROI Total USD semana (B4):
```
=SUM(FILTER(Resumen!J2:J, Resumen!A2:A=B1))
```
Aplica formato: B2/B3 como %, B4 como moneda.

### 5) Gráficos listos
- Línea semanal: Insertar → Gráfico → Datos: `semana_iso` vs `roi_total_usd` (suma)
- Barras apiladas: `replied`, `booked_demo`, `closed_won` por `canal` (segmentado por `semana_iso` usando filtro)
- Línea doble: `dm_demo_rate` y `demo_close_rate` (AVG) por `semana_iso`

### 6) Slicers (segmentadores)
Inserta segmentadores para `variant`, `stack_detected` y `canal` para filtrar pivots y gráficos.

### 7) Buenas prácticas
- Bloquea rangos de KPIs y fórmulas
- Centraliza umbrales (p. ej., objetivos de tasas) en hoja “Config” y referencia en CF
- Duplica la vista para cada equipo/stack si lo necesitas (una pestaña por stack)


## ROI Snapshot (integración rápida)
- Importa  como hoja .
- Crea hoja  y usa las fórmulas de .
- Añade tarjetas KPI para Ingreso incremental, Margen incremental y ROI mensual.
- En , referencia  para mostrar ROI mensual.

## ROI Snapshot (integración rápida)
- Importa `calculadora_roi_recomendaciones.csv` como hoja `ROI_Variables`.
- Crea hoja `ROI_Snapshot` y usa las fórmulas de `roi_snapshot_guia.md`.
- Añade tarjetas KPI para Ingreso incremental, Margen incremental y ROI mensual.
- En `Panel`, referencia `ROI_Snapshot` para mostrar ROI mensual.
