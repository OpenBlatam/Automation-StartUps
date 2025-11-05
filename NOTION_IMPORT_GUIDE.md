# Guía de Importación a Notion - Sistema Outreach DM

## Estructura recomendada (Notion)
- Base de Conocimiento (database)
  - Artículo: DMs por producto
  - Artículo: Guías operativas
  - Artículo: Recursos avanzados
- Pipeline de Outreach (database)
  - Vista: Por estado (Kanban)
  - Vista: Por industria/rol
  - Vista: Por versión de DM
- Dashboard (página)
  - KPIs conectados a propiedades calculadas

## Pasos de importación
1) Crea un espacio "Outreach DM" en Notion
2) Importa archivos .md (drag & drop) de estas carpetas:
   - DMs principales: `DM_curso_ia_webinars.md`, `DM_saas_ia_marketing.md`, `DM_ia_bulk_documentos.md`
   - Operativos: `CHECKLIST_OUTREACH_DM.md`, `SISTEMA_SEGUIMIENTO_DM.md`, `PLANTILLAS_RESPUESTAS_DM.md`
   - Avanzados: `WORKFLOW_VISUAL_OUTREACH.md`, `ANTI_PATTERNS_OUTREACH.md`, etc.
3) Crea una base de datos "Leads" e importa `SAMPLE_LEADS_OUTREACH.csv`
4) Añade propiedades: industria, producto, versión DM, CTA, UTM, estado
5) Crea vistas: Kanban por estado, tabla por industria, calendario por seguimientos

## Embeds útiles
- Mermaid (con integraciones de terceros) para diagramas
- Enlaces a Google Sheets para KPIs si prefieres

## Tips
- Usa templates de página para DMs por industria
- Relaciona Leads con Casos de Éxito
- Crea un template de Seguimiento con fechas automáticas (día 4/10/20)
- Control de acceso por equipo (ventas/marketing/ops)

## Exportación
- Para compartir con terceros, crea una vista pública de solo lectura del índice
- Exporta a PDF el README y el Lite Pack si es necesario



