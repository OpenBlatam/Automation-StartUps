---
title: "Project Structure"
category: "project_structure.md"
tags: []
created: "2025-10-29"
path: "project_structure.md"
---

# 📁 Estructura del Proyecto - CFDI 4.0 IA 2025

```
cfdi-4.0-ia-2025/
│
├── 📄 Archivos Principales
│   ├── package.json                  # Configuración de dependencias y scripts
│   ├── server.js                      # Punto de entrada del servidor
│   ├── Makefile                       # Comandos automatizados
│   ├── .gitignore                    # Archivos a ignorar en Git
│   ├── .dockerignore                 # Archivos a ignorar en Docker
│   ├── .editorconfig                 # Configuración de editores
│   ├── .nvmrc                        # Versión de Node.js
│   ├── .eslintrc.js                  # Configuración de ESLint
│   ├── .prettierrc.js                # Configuración de Prettier
│   ├── jest.config.js                # Configuración de Jest
│   ├── swagger.json                  # Documentación OpenAPI
│   ├── LICENSE                       # Licencia MIT
│   └── docker-compose.yml            # Orquestación de servicios
│
├── 🤖 Código de IA y Automatización
│   ├── API_CFDI_4.0_IA_2025.js       # API REST principal
│   ├── Validador_CFDI_4.0_IA_2025.js # Validador avanzado
│   ├── Automatizacion_IA_CFDI_2025.js # Sistema de automatización
│   └── Integracion_ERP_CFDI_2025.js  # Integración con ERPs
│
├── 📁 tests/                          # Tests Automatizados
│   ├── setup.js                       # Configuración de tests
│   ├── API.test.js                    # Tests de API
│   └── Validador.test.js              # Tests de Validador
│
├── 📁 scripts/                        # Scripts de Utilidades
│   ├── generate-docs.js               # Generador de documentación
│   ├── pre-start-check.js             # Verificación pre-inicio
│   └── post-install.js                # Tareas post-instalación
│
├── 📁 .github/                        # GitHub
│   └── workflows/
│       └── ci.yml                     # CI/CD con GitHub Actions
│
├── 📁 docs/                           # Documentación
│   └── API.md                         # Documentación de API
│
├── 📁 logs/                          # Logs de la aplicación
│   └── cfdi.log                       # Log principal
│
├── 📁 certificados/                   # Certificados SAT
│   ├── .gitkeep
│   └── (no subir al repositorio)
│
├── 📁 backups/                        # Backups
│   └── (generados automáticamente)
│
├── 📚 Documentación
│   ├── README_CFDI.md                 # README principal
│   ├── MEJORAS_COMPLETADAS.md        # Resumen de mejoras
│   ├── DEPLOY_GUIDE.md                # Guía de deployment
│   ├── CONTRIBUTING.md                # Guía de contribución
│   ├── CHANGELOG.md                   # Registro de cambios
│   ├── IMPLEMENTACION_COMPLETADA.md  # Resumen de implementación
│   └── PROJECT_STRUCTURE.md          # Este archivo
│
└── 📄 Archivos de Configuración
    ├── env.example                    # Ejemplo de variables de entorno
    └── nvm-setup.sh                   # Setup de NVM
```

## 📂 Descripción de Directorios

### `/tests` - Testing
- Tests unitarios y de integración
- Configuración de Jest
- Mocks y fixtures

### `/scripts` - Scripts de Utilidades
- Scripts de automatización
- Tareas pre/post instalar
- Generadores de documentación

### `/docs` - Documentación
- Documentación de API
- Especificaciones técnicas
- Guías de uso

### `/logs` - Logs
- Logs de la aplicación
- Logs de errores
- Logs de auditoría

### `/certificados` - Certificados
- Certificados SAT
- Llaves privadas
- **NUNCA subir al repositorio**

### `/backups` - Backups
- Backups automáticos
- Datos restaurables

### `/.github` - GitHub
- Workflows de CI/CD
- GitHub Actions

## 🔑 Archivos Clave

### Configuración Principal
- `package.json` - Dependencias y scripts npm
- `server.js` - Inicio del servidor
- `env.example` - Variables de entorno

### Docker
- `Dockerfile` - Imagen Docker
- `docker-compose.yml` - Orquestación
- `.dockerignore` - Ignorar archivos

### Testing
- `jest.config.js` - Configuración Jest
- `tests/*` - Tests unitarios

### Code Quality
- `.eslintrc.js` - Linter
- `.prettierrc.js` - Formatter
- `.editorconfig` - Consistencia

### CI/CD
- `.github/workflows/ci.yml` - GitHub Actions

## 📊 Conventions

### Nombres de Archivos
- JavaScript: `camelCase.js`
- Tests: `Name.test.js`
- Config: `.config.js`

### Estructura de Código
```javascript
/**
 * Descripción del archivo
 * @author Tu Nombre
 * @version 1.0.0
 */

// Imports
const express = require('express');

// Variables
const PORT = 3000;

// Clases
class MyClass {
  constructor() {
    // ...
  }
  
  method() {
    // ...
  }
}

// Funciones
function myFunction() {
  // ...
}

// Exports
module.exports = MyClass;
```

## 🎯 Convenciones de Git

### Ramas
- `main` - Producción
- `develop` - Desarrollo
- `feature/*` - Nuevas funcionalidades
- `bugfix/*` - Correcciones
- `hotfix/*` - Urgentes

### Commits
```
tipo(scope): descripción

descripción detallada

Refs: #issue
```

**Tipos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección
- `docs`: Documentación
- `style`: Formato
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

## 📦 Deploy

### Local
```bash
npm install
npm start
```

### Docker
```bash
docker-compose up -d
```

### Producción
```bash
pm2 start server.js
```

## 🔍 Búsqueda Rápida

### ¿Dónde encontrar...?

- **Configuración**: `package.json`, `.env`
- **Código principal**: `API_CFDI_4.0_IA_2025.js`
- **Tests**: `/tests`
- **Scripts**: `/scripts`
- **Docs**: `/docs` y `README_CFDI.md`
- **Docker**: `Dockerfile`, `docker-compose.yml`
- **CI/CD**: `.github/workflows/`

## 🎨 Diagrama de Flujo

```
┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   API Rest  │─────▶│  Validador  │─────▶│ Automatiz.  │
│             │      │     IA      │      │     IA      │
└─────────────┘      └─────────────┘      └─────────────┘
       │                     │                     │
       ▼                     ▼                     ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│  Database   │      │    ERP      │      │     SAT     │
└─────────────┘      └─────────────┘      └─────────────┘
```

## 📞 Más Información

- README: `README_CFDI.md`
- Contribuir: `CONTRIBUTING.md`
- Deployment: `DEPLOY_GUIDE.md`
- Changelog: `CHANGELOG.md`



