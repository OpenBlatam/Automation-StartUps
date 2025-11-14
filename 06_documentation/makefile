SHELL := /bin/bash

.PHONY: analyze analyze-quiet analyze-all hook install-hook ci-baseline optimize help

help:
	@echo "Targets disponibles:"
	@echo "  analyze          - Ejecuta análisis con salida completa"
	@echo "  analyze-quiet    - Análisis silencioso (resumen consola)"
	@echo "  analyze-all      - Análisis + exportes (HTML/CSV/JSON)"
	@echo "  install-hook     - Instala hook pre-commit"
	@echo "  ci-baseline      - Guarda reporte actual como baseline"
	@echo "  optimize         - Optimiza SVGs con SVGO (si está instalado)"

analyze:
	bash ./tools/analyze_assets.sh

analyze-quiet:
	QUIET=true SUMMARY_ONLY=true bash ./tools/analyze_assets.sh

analyze-all:
	OUTPUT_FORMAT=all QUIET=true SUMMARY_ONLY=true bash ./tools/analyze_assets.sh

install-hook:
	bash ./tools/install_git_hook.sh

ci-baseline:
	@mkdir -p exports
	@bash ./tools/analyze_assets.sh >/dev/null 2>&1 || true
	cp -f exports/assets_report.txt exports/assets_baseline.txt
	@echo "✅ Baseline actualizado: exports/assets_baseline.txt"

optimize:
	bash ./tools/optimize_svgs.sh

# Makefile - Comandos comunes para desarrollo

.PHONY: help venv install run initdb sampledata health test lint fmt clean docker-build docker-up docker-down

help:
	@echo "Comandos disponibles:"
	@echo "  make venv        - Crear entorno virtual (venv)"
	@echo "  make install     - Instalar dependencias"
	@echo "  make run         - Ejecutar servidor (python app.py)"
	@echo "  make initdb      - Inicializar base de datos"
	@echo "  make sampledata  - Inicializar BD con datos de ejemplo"
	@echo "  make health      - Health check del sistema"
	@echo "  make test        - Ejecutar tests"
	@echo "  make clean       - Limpiar artefactos"
	@echo "  make docker-build- Construir imagen Docker"
	@echo "  make docker-up   - Levantar app+db+redis con docker-compose"
	@echo "  make docker-down - Detener y limpiar contenedores"

venv:
	python3 -m venv venv

install:
	pip install --upgrade pip
	pip install -r requirements.txt

run:
	python3 app.py

initdb:
	python3 init_db.py

sampledata:
	python3 init_db.py --sample-data

health:
	python3 utils/health_check.py

test:
	python3 -m pytest tests/ || (echo "pytest no instalado; ejecutando unittest" && python3 -m unittest discover -s tests -p 'test_*.py')

clean:
	rm -rf __pycache__
	rm -rf */__pycache__
	rm -rf .pytest_cache

docker-build:
	docker build -t inventory-app:latest .

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down -v



