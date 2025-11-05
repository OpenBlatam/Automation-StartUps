---
title: "🧱 Taxonomía y Metadatos del SGCI"
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

# 🧱 Taxonomía y Metadatos del SGCI

## Taxonomía corporativa
- Dominio → Área → Subárea → Proceso → SOP → Artefacto (anexo)

## Metadatos mínimos (YAML frontmatter sugerido)
```
title: ""
domain: "operations|sales|cs|tech|hr|finance"
area: ""
subcategory: ""
artifact_type: "process|sop|training|audit|template|index"
code: "PROC-XXX|SOP-XXX"
owner: "rol/persona"
approver: "rol/persona"
criticality: "high|medium|low"
version: "1.0"
status: "active|draft|deprecated"
review_sla_months: 6
last_review: "YYYY-MM-DD"
next_review: "YYYY-MM-DD"
systems: ["crm","erp","zapier"]
links: ["..."]
```

## Reglas
- Todos los artefactos con metadatos completos
- `code` único por artefacto y trazable en índice
- `next_review` calculado por SLA

---
Última actualización: {{FECHA}}
Owner: Knowledge Architecture
Versión: 1.0



