---
title: "Readme"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Reports_analytics/readme.md"
---

# Reports Analytics (SGCI)

## Archivos
- INDEX.md
- organization_report.json
- sop_linter_report.json (resumen estructurado para dashboards)
- sop_linter_report.md (tabla legible para revisión rápida)

## Ejecución recomendada semanal (cron)
```bash
# macOS/Linux: editar crontab
crontab -e
# correr los domingos a las 07:00
0 7 * * 0 /bin/zsh /Users/adan/Documents/documentos_blatam/06_Documentation/Scripts/run_weekly_sop_linter.sh >> /tmp/sop_linter.log 2>&1
```

Ruta del SGCI: `06_Documentation/00_Sistema_Gestion_Conocimiento_Interno`.

