# CHANGELOG - 07_Risk_Management/Documentation

## v6.1 (2025-10-29)
- Resúmenes ejecutivos (1 página) para: Curso/Webinars, SaaS IA Marketing, IA Bulk Documentos
- Guía de implementación rápida (30/60/90 días)
- Template de presentación para stakeholders (13 slides)
- Front matter YAML consistente (title, category, created, path)
- Index actualizado con navegación rápida y estado de versión

### Operativo/Técnico
- RACI, calendario de simulaciones (12 meses), matriz de riesgo, OKRs operativos
- Runbooks DDoS/rate-limit, política de Error Budget y SLOs (SaaS)
- Vendor scorecard LLM, SOP de cambios de modelo y rollback de prompts (IA Bulk)

## v6.0 (2025-10-29)
- Planes de contingencia completos (Curso/Webinars, SaaS IA, IA Bulk), versión Master
- Playbooks, checklists imprimibles, dashboards KPIs, plantillas legales
- Scripts de auto-recuperación y diagnósticos

## Próximos hitos
- v6.2: Exportación automática a PDF/HTML, validación de enlaces CI
- v6.3: Localización completa EN/PT de playbooks

## v6.1.1 (2025-10-30)
- Añadidos scripts de tooling en Documentation:
  - `build.sh` (export/QA), `validate.sh` (QA de metadatos), `bump_version.sh` (actualizar versiones visibles)
- Index con referencias directas a utilidades y versión explícita del conjunto

## v6.1.2 (2025-10-30)
- `run_all.sh` para ejecutar validación + build en un solo paso
- `METADATA_STANDARD.md` documenta el estándar de front matter y versión visible
- Índice actualizado con accesos directos a nuevas utilidades

## v6.1.3 (2025-10-30)
- `report_status.sh` genera reporte de títulos, versiones y fechas `created`
- Índice actualizado con acceso directo al reporte

## v6.1.4 (2025-10-30)
- `fix_paths.sh` normaliza YAML `path` → `07_risk_management/<lowercase-filename>.md` (dry-run y --apply)
- Índice actualizado con acceso directo a fix-paths

## v6.1.5 (2025-10-30)
- `export_index_csv.sh` exporta índice de documentación a CSV (file,title,created,version,path)
- Índice actualizado con acceso directo al exportador CSV

## v6.1.6 (2025-10-30)
- `new_doc.sh` genera documentos con front matter estándar y versión opcional
- Índice actualizado con el comando de scaffolding

## v6.1.7 (2025-10-30)
- `precommit.sh` valida metadatos y actualiza CSV antes de commit
- `install_precommit.sh` instala hook git `pre-commit`
- `CONTRIBUTING.md` guía breve de flujo de contribución y utilidades
- Índice actualizado con accesos a pre-commit y guía de contribución

## v6.1.8 (2025-10-30)
- `export_index_json.sh` exporta índice de documentación en JSON
- Índice actualizado con el exportador JSON

## v6.1.9 (2025-10-30)
- Makefile para orquestar validate/build/run/report/csv/json/fixpaths/bump
- Índice actualizado con referencia a `make help` y variables (VERSION, NEW_VER)

## v6.1.10 (2025-10-30)
- `VERSION` centraliza la versión por defecto del conjunto
- `validate.sh`, `run_all.sh`, `precommit.sh` usan `VERSION` si no se pasa argumento
- Índice actualizado para mostrar y referenciar `VERSION`

## v6.1.11 (2025-10-30)
- `check_external_links.sh` valida enlaces HTTP/HTTPS (usa markdown-link-check o curl)
- Makefile: nuevo target `links`
- Índice actualizado con utilidad de verificación de enlaces

## v6.1.12 (2025-10-30)
- Integrado QA de enlaces en `build.sh` y `run_all.sh` (local y externos)
- `precommit.sh` ahora verifica enlaces locales rápidamente
- Makefile: `links-local`, `links-external`, `qa` (validate+links+build)
- `mlc_config.json` configura markdown-link-check (timeouts, retries, skips)

## v6.1.13 (2025-10-30)
- `check_images.sh` verifica imágenes locales referenciadas
- `validate_anchors.sh` valida anchors intra y cross-file
- Makefile: nuevos targets `images` y `anchors`
- `precommit.sh` ahora valida imágenes también
- `index.md` actualizado con nuevas utilidades

## v6.1.14 (2025-10-30)
- `spellcheck.sh` integra revisión ortográfica (codespell/aspell si disponibles)
- `detect_orphans.sh` identifica documentos .md no referenciados
- Makefile: `spellcheck`, `orphans` y `qa` extendido
- `precommit.sh` corre spellcheck de forma no bloqueante
- `index.md` actualizado con utilidades de spellcheck y orphans

## v6.1.15 (2025-10-30)
- `validate_frontmatter_yaml.sh` valida YAML de front matter con PyYAML si disponible
- `check_unused_images.sh` detecta imágenes no referenciadas
- `toc_update.sh` genera/actualiza TOC entre marcadores (opción --apply)
- Makefile: `yaml`, `toc` y `qa` extendido
- `precommit.sh` ejecuta validación YAML estricta de forma no bloqueante
- `index.md` actualizado con yaml/toc

## v6.1.16 (2025-10-30)
- `docs_ci.sh` suite de QA con salida resumida y exit code
- `report_all.sh` genera reporte QA consolidado en Markdown (REPORT_QA.md)
- Makefile: `ci`, `report-all`, ayuda actualizada
- `index.md` actualizado con entradas de CI y reporte

## v6.1.17 (2025-10-30)
- `requirements.txt` (PyYAML) y `package.json` (markdownlint/markdown-link-check)
- Configs: `.markdownlint.json`, `.codespellignore`
- `bootstrap.sh` instala dependencias opcionales (pip/npm)
- Scripts usan npx si no hay bin global
- GitHub Actions: `.github/workflows/docs-ci.yml` ejecuta suite de QA
- `Makefile`: `bootstrap` y ayuda ampliada; `index.md` actualizado

## v6.1.18 (2025-10-30)
- `version_guard.sh` asegura que VERSION coincide con versiones visibles en .md
- `package.sh` empaqueta documentación y artefactos (dist/documentation_vX.Y.Z.zip)
- Makefile: `version`, `package`
- CI: cron semanal, subida de artefactos (reporte y zip)
- `index.md` actualizado con version/package

## v6.1.19 (2025-10-30)
- `publish_site.sh` genera sitio HTML simple en `site/` (con pandoc o fallback)
- `normalize_filenames.sh` renombra a lowercase/guiones y actualiza enlaces (`--apply`)
- `generate_badges.sh` crea `BADGES.md` con badges de versión/archivos/fecha
- Makefile: `site`, `normalize`, `badges`; `index.md` actualizado

## v6.1.20 (2025-10-30)
- `validate_yaml_path.sh` valida/corrige `path` del front matter contra ubicación real
- `docs_watch.sh` observa cambios y ejecuta QA rápida (fswatch/entr opcionales)
- `.editorconfig` para consistencia (LF, UTF-8, trim whitespace)
- `export_sitemap_json.sh` genera `site/sitemap.json`
- Makefile: `paths`, `watch`; `precommit.sh` llama validación de path
- `index.md` actualizado con paths/watch

## v6.1.21 (2025-10-30)
- `docs_stats.sh` exporta métricas (bytes, palabras, min lectura) → DOCS_STATS.csv
- `title_filename_consistency.sh` compara título con nombre de archivo (slug)
- `detect_duplicate_ids.sh` detecta headings con slugs duplicados
- Makefile: `stats`, `titlefile`, `dupids`; `index.md` actualizado

## v6.1.22 (2025-10-30)
- `enforce_yaml_keys.sh` auto-completa front matter mínimo (title, category, created, path)
- `release_notes.sh` compila últimas entradas del CHANGELOG → RELEASE_NOTES.md
- `git_tag_helper.sh` sugiere/crea tag `docs-v{VERSION}` (dry-run por defecto)
- `pdf_bundle.sh` genera PDFs y crea `_build/_ALL_DOCUMENTS.pdf` si hay herramientas
- Makefile: `yaml-enforce`, `notes`, `tag`, `pdf-bundle`; `index.md` actualizado
- CI: sube PDF combinado si está disponible

## v6.1.23 (2025-10-30)
- `secrets_scan.sh` escanea posibles secretos en .md
- `changed_only.sh` corre QA rápida solo sobre archivos modificados
- `export_sections_json.sh` exporta headings por archivo a JSON
- Makefile: `secrets`, `changed`, `sections`; `precommit.sh` añade escaneo de secretos
- CI: ejecuta secrets scan y sube `sections_index.json`

## v6.1.24 (2025-10-30)
- `export_links_csv.sh` inventario de enlaces HTTP/HTTPS → LINKS_INVENTORY.csv
- `validate_created_dates.sh` valida formato/fecha futura en `created`
- `detect_duplicate_filenames_ci.sh` detecta duplicados case-insensitive
- `serve_site.sh` servidor local del sitio estático
- Makefile: `links-csv`, `dates`, `dupnames`, `serve`; `index.md` actualizado
- CI: ejecuta fechas/dupnames/sections/links-csv
