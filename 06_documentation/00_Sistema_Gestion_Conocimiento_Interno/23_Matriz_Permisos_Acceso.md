---
title: "🔐 Matriz de Permisos y Accesos (SGCI)"
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

# 🔐 Matriz de Permisos y Accesos (SGCI)

## Niveles de acceso
- Viewer: lee
- Editor: crea/edita borradores
- Approver: aprueba/publica
- Admin: gestiona permisos y configuración

## Matriz (ejemplo)
```
artefacto_tipo | dominio | viewer | editor | approver | admin
process        | ops     | all    | ops    | ops_dir  | cko
sop            | tech    | all    | tech   | cto      | cko
training       | cs      | all    | cs     | cs_dir   | cko
```

## Políticas
- Principio de mínimo privilegio
- Revisión de permisos trimestral
- Registro de aprobaciones en PR/issue

---
Última actualización: {{FECHA}}
Owner: Governance + IT
Versión: 1.0
