---
title: "🧾 Backlog de Deuda SOPs (priorizado)"
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

# 🧾 Backlog de Deuda SOPs (priorizado)

Este reporte se genera con `Scripts/sop_debt_report.py` y se publica en `Reports_analytics/sop_debt_backlog.md`.

## Cómo generar
```
python3 06_Documentation/Scripts/sop_debt_report.py 06_Documentation/00_Sistema_Gestion_Conocimiento_Interno
```

Priorización (score): criticidad + cercanía a `next_review` + sin fecha (urgente).

Archivos generados:
- `06_Documentation/Reports_analytics/sop_debt_backlog.json`
- `06_Documentation/Reports_analytics/sop_debt_backlog.md`

---
Última actualización: {{FECHA}}
Owner: QA Interna
Versión: 1.0

