---
title: "📊 Dashboard de Métricas KM (Template)"
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

# 📊 Dashboard de Métricas KM (Template)

## KPIs núcleo
- Cobertura de procesos documentados (%)
- Freshness media (días vs SLA)
- Adopción (vistas/usuario/rol)
- T2P Onboarding (días por rol)
- Conformidad auditorías (% hallazgos resueltos)

## Semáforo de frescura (según días restantes vs `next_review`)
- 🟢 Verde: >60 días
- 🟡 Amarillo: 30-60 días
- 🔴 Rojo: <30 días o vencido

## Tabla base (ejemplo)
```
artefacto | tipo | owner | criticidad | last_review | next_review | uso_30d | estado
00_Sistema_Gestion_Conocimiento_Interno/00_MANUAL_MAESTRO_SGCI.md | other | Knowledge Management | medium | 2025-10-30 | 2026-04-30 | 12 | active
00_Sistema_Gestion_Conocimiento_Interno/02_Guia_Actualizacion_SOPs.md | sop | QA + Process Owner | high | 2025-10-30 | 2026-04-30 | 25 | active
```

## Vistas recomendadas
- Estado por dominio/área
- Semáforo por criticidad
- Tendencia de uso y freshness
- Backlog de deuda SOPs

## Índices y reportes
- Índice por código: `16_Indice_por_Codigo.md` → genera `Reports_analytics/code_index.*`
- Deuda SOPs: `17_Backlog_Deuda_SOPs.md` → genera `Reports_analytics/sop_debt_backlog.*`
- Resumen de frescura: `Reports_analytics/freshness_summary.md` (via `Scripts/freshness_summary.py`)

## Referencias de gobierno y adopción
- OKRs KM: `18_OKRs_KM.md`
- Programa de Adopción y Champions: `19_Programa_Adopcion_Champions.md`
- Plan de Muestreo de Auditoría: `20_Plan_Muestreo_Auditoria.md`
- Configuración SOP Linter: `21_Config_SOP_Linter.md`
- RCA/Incidentes: `22_Incident_RCA_SOP_Link.md`
- Permisos y Accesos: `23_Matriz_Permisos_Acceso.md`
- Retención/Archivado: `24_Politica_Retencion_Archivado.md`
- Reporte Trimestral KM: `25_Reporte_Trimestral_KM_Template.md`
 - Risk Register: `28_Risk_Register_KM.md`
 - Excepciones SLA: `29_SLA_Exceptions_Policy.md`
 - Roles: `30_Rol_Ops.md`, `31_Rol_CS.md`, `32_Rol_Tech.md`

---
Última actualización: {{FECHA}}
Owner: Data & KM
Versión: 1.0

## Cómo actualizar este dashboard
- Ejecuta el SOP Linter para generar reportes:
  - Script: `06_Documentation/Scripts/sop_linter.py`
  - Comando sugerido:
    ```bash
    python3 06_Documentation/Scripts/sop_linter.py 06_Documentation/00_Sistema_Gestion_Conocimiento_Interno
    ```
- Los reportes se guardan en `06_Documentation/Reports_analytics/` como `sop_linter_report.json` y `sop_linter_report.md`.
- Usa el JSON para alimentar esta tabla y semáforos (freshness y dead_links).


