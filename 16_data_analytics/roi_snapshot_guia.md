# ROI Snapshot – Integración rápida con Dashboard

Objetivo: mostrar un snapshot de ROI con variables del archivo `calculadora_roi_recomendaciones.csv` y resultados clave en la misma Google Sheet del dashboard.

## 1) Hoja Variables
- Importa `calculadora_roi_recomendaciones.csv` en una hoja nueva llamada "ROI_Variables".
- Revisa/ajusta valores: T, CR0, AOV, GM, COV, ΔCR, ΔAOV, COST, CAPEX.

## 2) Hoja ROI_Snapshot
- Crea hoja “ROI_Snapshot” con columnas: Métrica | Fórmula | Valor
- En la columna Valor pega las fórmulas siguientes (ajusta separador decimal/localidad si aplica):

Conversiones base: 
```
=INDEX(ROI_Variables!B:B, MATCH("Conversiones base", ROI_Variables!A:A, 0))
```
Conversiones con recs:
```
=INDEX(ROI_Variables!B:B, MATCH("Conversiones con recs", ROI_Variables!A:A, 0))
```
Ingreso base:
```
=INDEX(ROI_Variables!B:B, MATCH("Ingreso base", ROI_Variables!A:A, 0))
```
Ingreso con recs:
```
=INDEX(ROI_Variables!B:B, MATCH("Ingreso con recs", ROI_Variables!A:A, 0))
```
Ingreso incremental:
```
=INDEX(ROI_Variables!B:B, MATCH("Ingreso incremental", ROI_Variables!A:A, 0))
```
Margen incremental:
```
=INDEX(ROI_Variables!B:B, MATCH("Margen incremental", ROI_Variables!A:A, 0))
```
ROI mensual:
```
=INDEX(ROI_Variables!B:B, MATCH("ROI mensual", ROI_Variables!A:A, 0))
```
Payback meses:
```
=INDEX(ROI_Variables!B:B, MATCH("Payback meses", ROI_Variables!A:A, 0))
```

## 3) Tarjetas y formato
- Aplica formato % a ROI mensual, números a ingresos y margen.
- Inserta tarjetas KPI para Ingreso incremental, Margen incremental y ROI mensual.

## 4) Relación con el Panel
- En Panel, añade una fila “ROI mensual (snapshot)” que haga referencia a `ROI_Snapshot!C[ROI mensual]`.

### Referencia cruzada: Panel combinado (Sequences + ROI)
- Importa también `panel_combinado.csv` en la misma Google Sheet (hoja `Panel_Combinado`).
- En `Panel_Combinado`, crea una tarjeta que consuma `ROI_Snapshot!C[ROI mensual]` para mostrar el ROI junto a KPIs de Sequences.
- Guía rápida: ver `panel_combinado_guia.md` para configurar tarjetas y 2 gráficos listos.

## 5) Consejos
- Mantén ROI_Variables separado para pruebas de sensibilidad.
- Para escenarios, duplica ROI_Variables como ROI_Small/ROI_Mid/ROI_Large y referencia con una celda selector.
 - Si usas una sola hoja “Panel”, puedes traer los valores de snapshot con fórmulas `=ROI_Snapshot!C2:C8` y mostrarlos en tarjetas al lado de Reply/Demo/Close.
