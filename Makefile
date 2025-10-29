.PHONY: help install test lint format clean docker-build docker-run deploy

# Variables
NODE_VERSION := 18.17.0
DOCKER_IMAGE := cfdi-4.0-ia
DOCKER_TAG := latest

# Ayuda
help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Instalación
install: ## Instalar dependencias
	@echo "📦 Instalando dependencias..."
	npm install

install-dev: ## Instalar dependencias de desarrollo
	@echo "📦 Instalando dependencias de desarrollo..."
	npm install --include=dev

# Desarrollo
dev: ## Iniciar servidor en modo desarrollo
	@echo "🚀 Iniciando servidor en modo desarrollo..."
	npm run dev

start: ## Iniciar servidor en producción
	@echo "🚀 Iniciando servidor en producción..."
	npm start

# Testing
test: ## Ejecutar tests
	@echo "🧪 Ejecutando tests..."
	npm test

test-watch: ## Ejecutar tests en modo watch
	@echo "🧪 Ejecutando tests en modo watch..."
	npm run test:watch

test-coverage: ## Ejecutar tests con cobertura
	@echo "🧪 Ejecutando tests con cobertura..."
	npm test -- --coverage

# Calidad de código
lint: ## Ejecutar linter
	@echo "🔍 Ejecutando linter..."
	npm run lint

lint-fix: ## Ejecutar linter y corregir errores
	@echo "🔧 Ejecutando linter y corrigiendo errores..."
	npm run lint:fix

format: ## Formatear código con Prettier
	@echo "💅 Formateando código..."
	npx prettier --write "**/*.{js,json,md}"

# Configuración
setup: install setup-env ## Configurar proyecto completo

setup-env: ## Configurar variables de entorno
	@echo "⚙️  Configurando variables de entorno..."
	@if [ ! -f .env ]; then \
		cp env.example .env; \
		echo "✅ Archivo .env creado. Por favor, edita .env con tus configuraciones."; \
	else \
		echo "⚠️  Archivo .env ya existe."; \
	fi

# Base de datos
db-migrate: ## Ejecutar migraciones
	@echo "🗄️  Ejecutando migraciones..."
	npm run migrate

db-seed: ## Poblar base de datos
	@echo "🌱 Poblando base de datos..."
	npm run seed

# Docker
docker-build: ## Construir imagen Docker
	@echo "🐳 Construyendo imagen Docker..."
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Ejecutar contenedor Docker
	@echo "🐳 Ejecutando contenedor Docker..."
	docker run -p 3000:3000 --env-file .env $(DOCKER_IMAGE):$(DOCKER_TAG)

docker-compose-up: ## Levantar servicios con docker-compose
	@echo "🐳 Levantando servicios con docker-compose..."
	docker-compose up -d

docker-compose-down: ## Detener servicios de docker-compose
	@echo "🐳 Deteniendo servicios de docker-compose..."
	docker-compose down

docker-compose-logs: ## Ver logs de docker-compose
	@echo "📋 Mostrando logs..."
	docker-compose logs -f

docker-clean: ## Limpiar imágenes y contenedores de Docker
	@echo "🧹 Limpiando imágenes y contenedores de Docker..."
	docker-compose down -v
	docker rmi $(DOCKER_IMAGE):$(DOCKER_TAG) || true

# Validación
validate: lint test ## Validar código completo

# Documentación
docs: ## Generar documentación
	@echo "📚 Generando documentación..."
	node scripts/generate-docs.js

docs-serve: ## Servir documentación local
	@echo "📚 Serviendo documentación..."
	npx serve docs

# Limpieza
clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	rm -rf node_modules
	rm -rf coverage
	rm -rf dist
	rm -rf build
	rm -rf logs
	rm -rf .nyc_output
	find . -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true

clean-all: clean ## Limpieza completa incluyendo cache de npm
	@echo "🧹 Limpieza completa..."
	npm cache clean --force

# Seguridad
security-audit: ## Ejecutar auditoría de seguridad
	@echo "🔒 Ejecutando auditoría de seguridad..."
	npm audit

security-fix: ## Corregir vulnerabilidades de seguridad
	@echo "🔧 Corrigiendo vulnerabilidades..."
	npm audit fix

# Build
build: ## Construir proyecto
	@echo "🔨 Construyendo proyecto..."
	npm run build

# Deploy
deploy-staging: ## Desplegar en staging
	@echo "🚀 Desplegando en staging..."
	# Agregar comandos de deployment aquí

deploy-prod: ## Desplegar en producción
	@echo "🚀 Desplegando en producción..."
	# Agregar comandos de deployment aquí

# Monitoreo
logs: ## Ver logs del servidor
	@echo "📋 Mostrando logs..."
	tail -f logs/cfdi.log

# Backup
backup: ## Hacer backup de datos
	@echo "💾 Haciendo backup..."
	mkdir -p backups
	tar -czf backups/backup-$$(date +%Y%m%d-%H%M%S).tar.gz data/ 2>/dev/null || true

# Git
git-init: ## Inicializar repositorio git
	@echo "📝 Inicializando repositorio git..."
	git init
	git add .
	git commit -m "Initial commit"

# Actualización
update-deps: ## Actualizar dependencias
	@echo "⬆️  Actualizando dependencias..."
	npm update

update-deps-check: ## Verificar actualizaciones disponibles
	@echo "🔍 Verificando actualizaciones disponibles..."
	npm outdated

# Info
info: ## Mostrar información del proyecto
	@echo "📊 Información del Proyecto"
	@echo "=================================="
	@echo "Node version: $(shell node --version)"
	@echo "NPM version: $(shell npm --version)"
	@echo "Package: $(shell cat package.json | grep -A1 '"name"' | head -2 | grep name | sed 's/.*: //' | sed 's/[", ]//')"
	@echo "Version: $(shell cat package.json | grep '"version"' | sed 's/.*: //' | sed 's/[", ]//')"

# Help por defecto
.DEFAULT_GOAL := help



