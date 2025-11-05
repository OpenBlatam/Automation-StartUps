---
title: "🛠️ Configuración SOP Linter"
artifact_type: "other"
code: ""
owner: "Knowledge Management"
approver: "Governance"
version: "1.0"
status: "active"
criticality: "medium"
review_sla_months: 6
last_review: "2025-10-30"
next_review: "2026-04-28"
domain: "operations"
area: "general"
systems: []
links: []
---

# 🛠️ Configuración SOP Linter

## Umbrales
- Secciones obligatorias (SOP): `Procedimiento`, `Historial de cambios`
- Secciones obligatorias (Proceso): `Objetivo`, `Entradas`, `RACI`
- Enlaces rotos permitidos: 0 (críticos), ≤1 (no críticos)
- Freshness: presencia de `Última actualización:` o `next_review`

## Exclusiones
- Archivos en `Templates/` (opcional)
- Documentos `other` con propósito narrativo

## Cómo extender
- Editar el script `Scripts/sop_linter.py` para agregar nuevas reglas
- Añadir lista de exclusión por ruta/patrón en el script

## Frontmatter mínimo (requerido)
- Usa la plantilla: `Templates/FRONTMATTER_MIN_TEMPLATE.md`
- Inserta automáticamente con:
  ```bash
  # Dry-run (recomendado primero)
  python3 06_Documentation/Scripts/add_frontmatter_min.py 06_Documentation/00_Sistema_Gestion_Conocimiento_Interno
  # Aplicar cambios
  python3 06_Documentation/Scripts/add_frontmatter_min.py 06_Documentation/00_Sistema_Gestion_Conocimiento_Interno --apply
  ```

---
Última actualización: {{FECHA}}
Owner: QA + KM Standards
Versión: 1.0

