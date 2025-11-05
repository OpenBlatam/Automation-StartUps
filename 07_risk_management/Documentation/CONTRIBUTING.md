---
title: "Contributing"
category: "07_risk_management"
tags: []
created: "2025-10-30"
path: "07_risk_management/documentation/contributing.md"
---

# Contribuir a 07_Risk_Management/Documentation

## Flujo recomendado
1. Crear documento: `./new_doc.sh "Título" archivo.md [versión]`
2. Editar contenido manteniendo el front matter YAML y el `path` coherente
3. Opcional: añadir línea visible de versión `**Versión:** 6.1 (... )`
4. Validar: `./validate.sh 6.1`
5. Exportar índice CSV (opcional): `./export_index_csv.sh`
6. Build/QA (opcional): `./build.sh`

## Pre-commit
- Validación rápida: `./precommit.sh 6.1`
- Instalar hook git: `./install_precommit.sh 6.1`

## Estándar de metadatos
- Ver `METADATA_STANDARD.md`

## Utilidades útiles
- Normalizar `path`: `./fix_paths.sh [--apply]`
- Reporte de estado: `./report_status.sh`
- Bump de versión visible: `./bump_version.sh 6.2 "Master Edition"`
- Todo en uno: `./run_all.sh 6.1`

