---
title: "Index Documentation"
category: "07_risk_management"
tags: []
created: "2025-10-29"
path: "07_risk_management/documentation/index.md"
---

# Índice - 07_risk_management/Documentation

Generado: 2025-10-29 19:35:20

Breadcrumbs: [07_risk_management](./07_risk_management/) / [Documentation](./07_risk_management/Documentation)


## Navegación rápida

- Planes de contingencia (v6.1):
  - [plan_contingencia_curso_ia_webinars.md](./plan_contingencia_curso_ia_webinars.md)
  - [plan_contingencia_saas_ia_marketing.md](./plan_contingencia_saas_ia_marketing.md)
  - [plan_contingencia_ia_bulk_documentos.md](./plan_contingencia_ia_bulk_documentos.md)

- Resúmenes ejecutivos (1 página):
  - [resumen_ejecutivo_curso_ia_webinars.md](./resumen_ejecutivo_curso_ia_webinars.md)
  - [RESUMEN_EJECUTIVO_SAAS_IA_MARKETING.md](./RESUMEN_EJECUTIVO_SAAS_IA_MARKETING.md)
  - [RESUMEN_EJECUTIVO_IA_BULK_DOCUMENTOS.md](./RESUMEN_EJECUTIVO_IA_BULK_DOCUMENTOS.md)

- Implementación y presentaciones:
  - [GUIA_IMPLEMENTACION_RAPIDA_30_60_90_DIAS.md](./GUIA_IMPLEMENTACION_RAPIDA_30_60_90_DIAS.md)
  - [TEMPLATE_PRESENTACION_STAKEHOLDERS.md](./TEMPLATE_PRESENTACION_STAKEHOLDERS.md)

> Estado: documentos principales en versión 6.1 (Master).

**Versión actual del conjunto:** 6.1

## Utilidades

- [CHANGELOG.md](./CHANGELOG.md)
- VERSION: `cat ./VERSION` (valor por defecto para validación/build)
- make: `make help` (VERSION=6.1 por defecto)
- build: `./build.sh` (export a PDF/HTML si hay pandoc; QA de enlaces)
- validate: `./validate.sh 6.1` (verifica front matter y versiones visibles)
- bump: `./bump_version.sh 6.1 "Master Edition"` (actualiza versiones visibles)
- links: `./check_external_links.sh` | `make links` (valida enlaces HTTP/HTTPS)
- links-local: `./verify_links.sh` | `make links-local` (valida enlaces a .md locales)
- images: `./check_images.sh` | `make images` (verifica imágenes locales referenciadas)
- anchors: `./validate_anchors.sh` | `make anchors` (valida anchors intra/cross-file)
- spellcheck: `./spellcheck.sh` | `make spellcheck` (ortografía con codespell/aspell si disponibles)
- orphans: `./detect_orphans.sh` | `make orphans` (detecta .md no referenciados)
- yaml: `./validate_frontmatter_yaml.sh` | `make yaml` (front matter YAML estricto con PyYAML)
- toc: `./toc_update.sh [--apply]` | `make toc` (TOC entre marcadores)
- qa: `make qa` (validate + links-local + links-external + build)
- ci: `make ci` | `./docs_ci.sh` (suite QA con exit code para CI)
- reporte QA: `make report-all` | `./report_all.sh > REPORT_QA.md`
- bootstrap: `make bootstrap` (instala deps Python/Node opcionales)
- version: `make version` (valida VERSION vs. versiones visibles)
- package: `make package` (genera ZIP con docs y artefactos en `dist/`)
- site: `make site` (genera sitio HTML estático en `site/`)
- normalize: `make normalize` | `./normalize_filenames.sh [--apply]` (normaliza nombres y actualiza links)
- badges: `make badges` (genera `BADGES.md` con badges de estado)
- paths: `./validate_yaml_path.sh [--apply]` | `make paths` (YAML path vs archivo)
- watch: `make watch` (observa cambios y corre QA rápida)
- stats: `make stats` (genera `DOCS_STATS.csv` con tamaño/palabras/min lectura)
- titlefile: `make titlefile` (consistencia título vs nombre de archivo)
- dupids: `make dupids` (detecta slugs/IDs duplicados en headings)
- yaml-enforce: `./enforce_yaml_keys.sh [--apply]` | `make yaml-enforce` (auto-completa front matter)
- notes: `make notes` (genera `RELEASE_NOTES.md` desde `CHANGELOG.md`)
- tag: `./git_tag_helper.sh [--apply]` | `make tag` (tag `docs-v{VERSION}`)
- pdf-bundle: `make pdf-bundle` (genera y une PDFs a `_build/_ALL_DOCUMENTS.pdf`)
- secrets: `make secrets` (escaneo heurístico de posibles secretos)
- changed: `make changed` | `./changed_only.sh [base]` (QA rápida en archivos modificados)
- sections: `make sections` (exporta `sections_index.json` con headings por archivo)
- links-csv: `make links-csv` (inventario de enlaces HTTP/HTTPS a CSV)
- dates: `make dates` (valida `created` formato y no-futuro)
- dupnames: `make dupnames` (dup de nombres de archivo case-insensitive)
- serve: `make serve` (sirve `site/` en localhost)
- run-all: `./run_all.sh 6.1` (valida y construye en un paso)
- pre-commit: `./precommit.sh 6.1` | instalar: `./install_precommit.sh 6.1`
- report: `./report_status.sh` (resumen: archivo, título, versión, creado)
- export-csv: `./export_index_csv.sh [output.csv]` (genera índice CSV)
- export-json: `./export_index_json.sh [output.json]` (genera índice JSON)
- fix-paths: `./fix_paths.sh [--apply]` (normaliza YAML path a `07_risk_management/<archivo>.md`)
- new-doc: `./new_doc.sh "Título" archivo.md [versión]` (scaffolding con front matter)
- contribuir: [CONTRIBUTING.md](./CONTRIBUTING.md)
- estándar de metadatos: [METADATA_STANDARD.md](./METADATA_STANDARD.md)