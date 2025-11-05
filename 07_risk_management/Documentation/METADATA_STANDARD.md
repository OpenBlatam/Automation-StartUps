---
title: "Metadata Standard"
category: "07_risk_management"
tags: []
created: "2025-10-30"
path: "07_risk_management/documentation/metadata_standard.md"
---

# Estándar de Metadatos (Documentation)

## Front matter YAML requerido
- title: Título legible
- category: "07_risk_management"
- tags: [] (opcional)
- created: YYYY-MM-DD
- path: ruta-del-archivo en minúsculas

Ejemplo:
```yaml
---
title: "Plan Contingencia Saas Ia Marketing"
category: "07_risk_management"
tags: []
created: "2025-10-29"
path: "07_risk_management/plan_contingencia_saas_ia_marketing.md"
---
```

## Versión visible (si aplica)
Colocar cerca del encabezado principal:
```
**Versión:** 6.1 (Master ...)
```

## Convenciones
- Nombres de archivos en minúsculas con guiones bajos.
- Fechas en formato ISO (YYYY-MM-DD).
- Mantener consistencia con `CHANGELOG.md` e `index.md`.

## QA rápido
- Validar: `./validate.sh 6.1`
- Build/QA: `./build.sh`
- Todo en uno: `./run_all.sh 6.1`

