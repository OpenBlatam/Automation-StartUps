# Makefile - Orquestación de utilidades de Documentation
# Uso común:
#   make            # ayuda
#   make validate   # valida metadatos (VERSION=6.1 por defecto)
#   make build      # export/QA
#   make run        # valida + build
#   make report     # tabla de estado
#   make csv        # export CSV
#   make json       # export JSON
#   make fixpaths   # normaliza YAML path (dry-run; APPLY=1 para aplicar)
#   make bump       # actualiza líneas visibles de versión (NEW_VER=6.2 SUFFIX="Master Edition")

SHELL := /bin/bash
ROOT_DIR := $(shell pwd)
VERSION ?= 6.1
NEW_VER ?= 6.1
SUFFIX ?=
APPLY ?= 0

.PHONY: help
help:
	@echo "Targets disponibles:"
	@echo "  make validate   VERSION=$(VERSION)"
	@echo "  make build      (pandoc opcional)"
	@echo "  make run        (validate + build)"
	@echo "  make report     (tabla de estado)"
	@echo "  make qa         (validate + links-local + links-external + build)"
	@echo "  make images     (verifica existencia de imágenes referenciadas)"
	@echo "  make anchors    (valida anchors intra/cross-file)"
	@echo "  make spellcheck (revisión ortográfica opcional)"
	@echo "  make orphans    (detecta .md no referenciados)"
	@echo "  make yaml       (validación estricta de front matter YAML)"
	@echo "  make toc        (actualiza TOC entre marcadores)"
	@echo "  make ci         (suite de QA con exit code)"
	@echo "  make report-all (reporte QA consolidado en Markdown)"
	@echo "  make bootstrap  (instala dependencias Python/Node opcionales)"
	@echo "  make version    (valida que VERSION coincide con versiones visibles)"
	@echo "  make package    (zip de documentación y artefactos en dist/)"
	@echo "  make site       (genera sitio estático en ./site)"
	@echo "  make normalize  (muestra/ejecuta normalización de nombres de archivos)"
	@echo "  make badges     (genera BADGES.md)"
	@echo "  make paths      (valida/corrige front matter path)"
	@echo "  make watch      (observa cambios y corre QA rápida)"
	@echo "  make stats      (reporte de tamaño/palabras/lectura)"
	@echo "  make titlefile  (consistencia título vs nombre de archivo)"
	@echo "  make dupids     (detecta IDs de encabezado duplicados)"
	@echo "  make secrets    (escaneo heurístico de posibles secretos)"
	@echo "  make changed    (QA rápida solo sobre archivos modificados)"
	@echo "  make sections   (exporta índice de secciones a JSON)"
	@echo "  make links-csv  (exporta inventario de enlaces a CSV)"
	@echo "  make dates      (valida 'created' formato y no-futuro)"
	@echo "  make dupnames   (detecta nombres de archivo duplicados case-insensitive)"
	@echo "  make serve      (sirve el sitio estático en localhost)"
	@echo "  make yaml-enforce (auto-completa front matter faltante)"
	@echo "  make notes      (genera RELEASE_NOTES.md desde CHANGELOG)"
	@echo "  make tag        (sugiere/crea tag git docs-vX.Y.Z)"
	@echo "  make pdf-bundle (genera y une PDFs en _build/_ALL_DOCUMENTS.pdf)"
	@echo "  make csv        (export CSV)"
	@echo "  make json       (export JSON)"
	@echo "  make fixpaths   APPLY=$(APPLY) (0=dry-run, 1=aplicar)"
	@echo "  make bump       NEW_VER=$(NEW_VER) SUFFIX=$(SUFFIX)"
	@echo "  make links      (verifica enlaces externos con markdown-link-check/curl)"

.PHONY: validate
validate:
	@chmod +x ./validate.sh || true
	@./validate.sh $(VERSION)

.PHONY: build
build:
	@chmod +x ./build.sh || true
	@./build.sh

.PHONY: run
run: validate build
	@echo "[make] run OK"

.PHONY: report
report:
	@chmod +x ./report_status.sh || true
	@./report_status.sh

.PHONY: csv
csv:
	@chmod +x ./export_index_csv.sh || true
	@./export_index_csv.sh $(ROOT_DIR)/documentation_index.csv
	@echo "[make] CSV en documentation_index.csv"

.PHONY: json
json:
	@chmod +x ./export_index_json.sh || true
	@./export_index_json.sh $(ROOT_DIR)/documentation_index.json
	@echo "[make] JSON en documentation_index.json"

.PHONY: fixpaths
fixpaths:
	@chmod +x ./fix_paths.sh || true
ifeq ($(APPLY),1)
	@./fix_paths.sh --apply
else
	@./fix_paths.sh
endif

.PHONY: bump
bump:
	@chmod +x ./bump_version.sh || true
ifeq ($(strip $(SUFFIX)),)
	@./bump_version.sh $(NEW_VER)
else
	@./bump_version.sh $(NEW_VER) "$(SUFFIX)"
endif
	@echo "[make] bump aplicado: $(NEW_VER) $(SUFFIX)"

.PHONY: links
links:
	@chmod +x ./check_external_links.sh || true
	@./check_external_links.sh

.PHONY: links-local
links-local:
	@chmod +x ./verify_links.sh || true
	@./verify_links.sh

.PHONY: links-external
links-external:
	@chmod +x ./check_external_links.sh || true
	@./check_external_links.sh

.PHONY: qa
qa: validate links-local links-external images anchors spellcheck orphans yaml toc build
 	@echo "[make] qa OK"

.PHONY: spellcheck
spellcheck:
	@chmod +x ./spellcheck.sh || true
	@./spellcheck.sh || true

.PHONY: orphans
orphans:
	@chmod +x ./detect_orphans.sh || true
	@./detect_orphans.sh || true

.PHONY: yaml
yaml:
	@chmod +x ./validate_frontmatter_yaml.sh || true
	@./validate_frontmatter_yaml.sh || true

.PHONY: toc
toc:
	@chmod +x ./toc_update.sh || true
	@./toc_update.sh --apply || true

.PHONY: ci
ci:
	@chmod +x ./docs_ci.sh || true
	@./docs_ci.sh

.PHONY: report-all
report-all:
	@chmod +x ./report_all.sh || true
	@./report_all.sh > REPORT_QA.md
	@echo "[make] Reporte en REPORT_QA.md"

.PHONY: bootstrap
bootstrap:
	@chmod +x ./bootstrap.sh || true
	@./bootstrap.sh

.PHONY: version
version:
	@chmod +x ./version_guard.sh || true
	@./version_guard.sh

.PHONY: package
package:
	@chmod +x ./package.sh || true
	@./package.sh

.PHONY: site
site:
	@chmod +x ./publish_site.sh || true
	@./publish_site.sh

.PHONY: normalize
normalize:
	@chmod +x ./normalize_filenames.sh || true
	@./normalize_filenames.sh

.PHONY: badges
badges:
	@chmod +x ./generate_badges.sh || true
	@./generate_badges.sh

.PHONY: paths
paths:
	@chmod +x ./validate_yaml_path.sh || true
	@./validate_yaml_path.sh

.PHONY: watch
watch:
	@chmod +x ./docs_watch.sh || true
	@./docs_watch.sh

.PHONY: stats
stats:
	@chmod +x ./docs_stats.sh || true
	@./docs_stats.sh > DOCS_STATS.csv && echo "[make] DOCS_STATS.csv actualizado"

.PHONY: titlefile
titlefile:
	@chmod +x ./title_filename_consistency.sh || true
	@./title_filename_consistency.sh

.PHONY: dupids
dupids:
	@chmod +x ./detect_duplicate_ids.sh || true
	@./detect_duplicate_ids.sh

.PHONY: secrets
secrets:
	@chmod +x ./secrets_scan.sh || true
	@./secrets_scan.sh

.PHONY: changed
changed:
	@chmod +x ./changed_only.sh || true
	@./changed_only.sh

.PHONY: sections
sections:
	@chmod +x ./export_sections_json.sh || true
	@./export_sections_json.sh

.PHONY: links-csv
links-csv:
	@chmod +x ./export_links_csv.sh || true
	@./export_links_csv.sh

.PHONY: dates
dates:
	@chmod +x ./validate_created_dates.sh || true
	@./validate_created_dates.sh

.PHONY: dupnames
dupnames:
	@chmod +x ./detect_duplicate_filenames_ci.sh || true
	@./detect_duplicate_filenames_ci.sh

.PHONY: serve
serve:
	@chmod +x ./serve_site.sh || true
	@./serve_site.sh

.PHONY: yaml-enforce
yaml-enforce:
	@chmod +x ./enforce_yaml_keys.sh || true
	@./enforce_yaml_keys.sh

.PHONY: notes
notes:
	@chmod +x ./release_notes.sh || true
	@./release_notes.sh

.PHONY: tag
tag:
	@chmod +x ./git_tag_helper.sh || true
	@./git_tag_helper.sh

.PHONY: pdf-bundle
pdf-bundle:
	@chmod +x ./pdf_bundle.sh || true
	@./pdf_bundle.sh

.PHONY: images
images:
	@chmod +x ./check_images.sh || true
	@./check_images.sh

.PHONY: anchors
anchors:
	@chmod +x ./validate_anchors.sh || true
	@./validate_anchors.sh

