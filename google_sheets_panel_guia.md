# Guía Google Sheets – Vista Panel (Checklist)

Objetivo: construir una vista tipo “Panel” con KPIs de tareas, vencimientos y desglose por owner a partir de la hoja “Origen”.

## 1) Importar el CSV de panel
- Archivo → Importar → Subir `panel_checklist_dashboard.csv` → Insertar hoja nueva (nombre sugerido: Panel)
- Asegúrate de que la hoja de datos base se llame “Origen” (o ajusta las fórmulas)

### Importar Panel combinado (opcional)
- Archivo → Importar → Subir `panel_combinado.csv` → Insertar hoja nueva (sugerido: Panel_Combinado)
- Sigue `panel_combinado_guia.md` para tarjetas KPI + 2 gráficos listos en 2 minutos

### Auto-refresh (Apps Script)
- Copia el contenido de `apps_script_panel_refresh.gs` en Extensiones → Apps Script.
- Ejecuta `refreshNow()` para probar.
- Ejecuta `createRefreshTrigger()` para programar refresh automático cada 6 horas.

### Botón Refresh manual (opcional)
1) Insertar → Dibujo → Selecciona una forma (rectángulo) y escribe “Refresh KPIs”.
2) Guarda el dibujo; clic en el dibujo → menú de 3 puntos → Asignar script → `refreshNow`.
3) Alternativa sin botón: usa el menú “Panel” que aparece al abrir la hoja (Refrescar ahora / Programar cada 6h).

ASCII (ubicación sugerida):
```
┌────────── Panel_Combinado ──────────┐   ┌──────────────┐
│ KPI Cards     | Gráfico 1 | Gráfico 2│   │ Refresh KPIs │  ← botón
└──────────────────────────────────────┘   └──────────────┘
```

### Exportación PDF semanal (opcional)
- Menú Panel → "Exportar PDF (Ejecutivo)" para probar ahora.
- Menú Panel → "Programar PDF semanal (Ejecutivo)" (Viernes 9:00 por defecto).
- Ajusta destinatarios en `apps_script_panel_refresh.gs` (variable `recipients`).

## 2) Ajustar fórmulas
- En la hoja Panel, en columna D (value), activa el cálculo pegando las fórmulas tal como están.
- Si tu hoja base no se llama “Origen”, reemplaza `Origen!` por el nombre real.

## 3) Formato condicional sugerido
- Filas con “Bloqueadas” → fondo rojo claro
- “Vencidas” → texto rojo
- “Vencen hoy” → fondo amarillo

## 4) Gráficos recomendados
- Barra: Tareas por owner (usa métricas “Por owner: …”)
- Dona: Distribución por status (Done, In Progress, Blocked, Todo)
- Tarjetas KPI: Total, Completadas, Vencidas, Vencen hoy

## 5) Vista “Hoy”
- Utiliza la hoja “Hoy” creada previamente o crea un filtro en Origen con due_date = HOY y status ≠ Done.

## 6) Enlaces útiles
- Checklist (CSV para Sheets): `checklist_lanzamiento_10_pasos_google_sheets.csv`
- Apps Script (menú Checklist): `apps_script_checklist_menu.gs`
