# Guía Google Sheets – Checklist de lanzamiento (10 pasos)

Objetivo: importar el CSV, aplicar validaciones de datos, formato condicional, vistas y una sección “Hoy”.

## 1) Importar el CSV
- Archivo → Importar → Subir `checklist_lanzamiento_10_pasos_google_sheets.csv`
- Elegir: Insertar hoja nueva, Separador automático, Convertir valores de texto en números/fechas ✅

## 2) Validaciones de datos
- status: lista: {Todo, In Progress, Blocked, Done}
- owner: lista: {Growth, Marketing Ops, RevOps, SDR, SDR Lead, QA}
- priority: lista: {Alta, Media, Baja}

Pasos: Datos → Validación de datos → Rango de celdas (columna) → Criterios: Lista de elementos → Mensaje de ayuda: “Selecciona un valor predefinido”. Marcar Rechazar entrada.

## 3) Formato condicional (recomendado)
- Si status = Done → Relleno verde, texto blanco
- Si status = Blocked → Relleno rojo, texto blanco
- Si due_date = HOY → Relleno amarillo
- Si due_date < HOY y status ≠ Done → Texto rojo + negrita

Reglas: Formato → Formato condicional → Regla personalizada o “Es igual a”/“Está antes de”. Usar =TODAY() en español: =HOY()

## 4) Vista “Hoy” (filtro o hoja derivada)
- Filtro: Datos → Crear filtro → Filtrar por due_date = HOY o por status ∈ {Todo, In Progress}
- Hoja derivada (recomendado): crear hoja “Hoy” con:
  - Encabezados en A1:I1
  - En A2 usar fórmula:
```
=FILTER(Origen!A2:I, (Origen!F:F = HOY()) + ((Origen!F:F < HOY()) * (Origen!D:D <> "Done")))
```
  - Cambia “Origen” por el nombre de la hoja importada.

## 5) Resumen de estado (mini tablero)
En hoja “Resumen”:
- Total por status:
```
=QUERY(Origen!D:D, "select D, count(D) where D is not null group by D label count(D) ''", 1)
```
- Total por owner y status:
```
=QUERY(Origen!B:D, "select B, D, count(D) where D is not null group by B, D label count(D) ''", 1)
```

## 6) Enlaces rápidos
- Markdown base: `checklist_lanzamiento_10_pasos.md`
- CSV base: `checklist_lanzamiento_10_pasos_google_sheets.csv`
- Secuencia/CTAs: `02_DM_SAAS_IA_MARKETING_ULTIMATE.md`
- QA: `qa_checklist_sequences.md`
- Horarios: `playbook_horarios_zonas.md`

## 7) Opcional: Apps Script
- Menú: Herramientas → Editor de Apps Script → Pegar `apps_script_checklist_menu.gs`
- Actualiza el nombre de la hoja “Origen” si difiere

