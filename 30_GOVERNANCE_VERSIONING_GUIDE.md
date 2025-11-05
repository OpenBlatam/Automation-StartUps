---
title: "30 Governance Versioning Guide"
category: "30_GOVERNANCE_VERSIONING_GUIDE.md"
tags: []
encoded_with: "Windows-1254"
created: "2025-10-29"
path: "30_GOVERNANCE_VERSIONING_GUIDE.md"
---

# ðï¸ Governance & Versioning Guide

## ð ÃNDICE

- [ð Estructura de Repositorio](#-estructura-de-repositorio)
- [ð·ï¸ Versioning SemÃ¡ntico](#ï¸-versioning-semÃ¡ntico)
- [ð§© Control de Cambios (Changelog)](#-control-de-cambios-changelog)
- [ð Guardrails y Aprobaciones](#-guardrails-y-aprobaciones)
- [ð§  Prompts & Templates Governance](#-prompts--templates-governance)
- [ð AuditorÃ­a y Trazabilidad](#-auditorÃ­a-y-trazabilidad)

---

## ð ESTRUCTURA DE REPOSITORIO

```
/01_products/           # DMs por producto
/02_sequences/          # Emails y follow-ups
/03_assets/             # One-pagers, decks, proposals
/04_metrics/            # Calculadoras, dashboards
/05_prompts/            # Prompts y guardrails
/06_playbooks/          # Closing, crisis, industry
/CHANGELOG.md           # Cambios por versiÃ³n
/INDEX.md               # Ãndice maestro
```

Convenciones
- Nombres con prefijo numÃ©rico y snake_case
- Un documento = una responsabilidad
- Links relativos entre docs

---

## ð·ï¸ VERSIONING SEMÃNTICO

Formato
- MAJOR.MINOR.PATCH (ej. v13.2.1)

Reglas
- MAJOR: cambios incompatibles (estructura, nombres)
- MINOR: nuevas secciones o docs (compatibles)
- PATCH: correcciones menores y typos

Etiquetas
- Added, Changed, Fixed, Removed, Deprecated, Security

---

## ð§© CONTROL DE CAMBIOS (CHANGELOG)

`CHANGELOG.md` ejemplo
```
## [13.1.0] - 2025-10-30
### Added
- 27_SALES_ENABLEMENT_KITS.md
- 28_BRAND_TONE_GUARDRAILS.md

### Changed
- 00_INDICE_DMS_COMPLETOS.md actualizado

### Fixed
- Duplicados en Ã­ndice removidos
```

---

## ð GUARDRails Y APROBACIONES

Roles
- Owner: aprueba MAJOR y MINOR
- Editor: propone cambios, hace PATCH
- Reviewer: QA de estilo y contenido

Flujo
1) PR con descripciÃ³n y justificaciÃ³n
2) QA con rÃºbrica (estilo, mÃ©tricas, CTA)
3) AprobaciÃ³n y merge
4) Update de Ã­ndice y changelog

---

## ð§  PROMPTS & TEMPLATES GOVERNANCE

- Guardrails centralizados (tono, longitud, CTA, fuentes)
- Tests de validaciÃ³n (placeholders, longitud, citas)
- Versionado de prompts por producto/rol/idioma
- Rollback a versiÃ³n estable ante caÃ­das de performance

---

## ð AUDITORÃA Y TRAZABILIDAD

- Metadatos en encabezado (versiÃ³n, autor, fecha)
- Hash de contenido para verificar integridad
- Registro de decisiones (por quÃ© se cambiÃ³)
- Matriz de dependencia (quÃ© docs impacta)

Ejemplo de metadatos
```
---
version: 13.0.0
owner: ventas_ops
updated_at: 2025-10-30
related: [01_DM_CURSO_IA_WEBINARS_ULTIMATE.md, 08_TEMPLATES_RESPUESTAS_RAPIDAS.md]
---
```

---

**FIN DEL DOCUMENTO**



