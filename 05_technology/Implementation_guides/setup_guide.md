---
title: "Setup Guide"
category: "05_technology"
tags: ["guide", "technical", "technology"]
created: "2025-10-29"
path: "05_technology/Implementation_guides/setup_guide.md"
---

# 🚀 Guía de Configuración - Documentos BLATAM

## Configuración Inicial del Proyecto

Esta guía te ayudará a configurar el proyecto desde cero.

---

## 📋 **Requisitos Previos**

### Software Necesario

- **Node.js** v18.0.0 o superior - [Descargar](https://nodejs.org/)
- **npm** v8.0.0 o superior (viene con Node.js)
- **Git** - [Descargar](https://git-scm.com/)
- **Docker** (opcional) v20.10+ - [Descargar](https://www.docker.com/)

### API Keys Necesarias

- **OpenAI API Key** (para GPT-4) - [Obtener](https://platform.openai.com/)
- **Google AI Key** (para Gemini) - [Obtener](https://ai.google.dev/)
- **Anthropic API Key** (para Claude) - [Obtener](https://www.anthropic.com/)

---

## 🚀 **Instalación Rápida**

### 1. Clonar el Repositorio

```bash
# Clonar el repositorio
git clone https://github.com/blatam/documentos.git
cd documentos

# O si ya tienes el repositorio
cd /Users/adan/Documents/documentos_blatam
```

### 2. Instalar Dependencias

```bash
# Instalar dependencias del proyecto raíz
npm install

# Instalar dependencias de documentación
npm install --global prettier markdownlint-cli2
```

### 3. Configurar Variables de Entorno

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar el archivo .env con tus configuraciones
nano .env
# o
code .env  # Si usas VS Code
```

### 4. Configurar Docker (Opcional)

```bash
# Construir imágenes Docker
docker-compose build

# Levantar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f
```

---

## 🔧 **Configuración Detallada**

### Configuración Básica

Edita el archivo `.env` con tus configuraciones:

```env
# Servidor
NODE_ENV=development
PORT=3000

# Base de Datos
DATABASE_URL=postgresql://user:password@localhost:5432/db_name

# AI Services
OPENAI_API_KEY=sk-your-key-here
GOOGLE_AI_API_KEY=your-key-here

# Seguridad
JWT_SECRET=your-super-secret-key
```

### Configurar Base de Datos

```bash
# Opción 1: Usando Docker
docker-compose up -d postgres

# Opción 2: PostgreSQL local
# Crear base de datos
createdb documentos_blatam

# Ejecutar migraciones (si aplica)
npm run migrate
```

### Configurar Certificados SAT

```bash
# Crear directorio para certificados
mkdir -p certificados

# Copiar tus certificados
cp /path/to/certificate.cer ./certificados/
cp /path/to/private_key.key ./certificados/

# Actualizar contraseñas en .env
```

---

## 🧪 **Verificar la Instalación**

### Ejecutar Tests

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests con cobertura
npm run test:coverage

# Ejecutar tests en modo watch
npm run test:watch
```

### Verificar Configuración

```bash
# Ver configuración del proyecto
npm run info

# Verificar variables de entorno
node -e "console.log(process.env.NODE_ENV)"
```

---

## 🚀 **Iniciar el Proyecto**

### Desarrollo

```bash
# Iniciar en modo desarrollo
npm run dev

# O usar Make
make dev
```

### Producción

```bash
# Construir para producción
npm run build

# Iniciar en modo producción
npm start

# O usar Make
make start
```

### Usando Docker

```bash
# Levantar todos los servicios
make docker-compose-up

# Ver logs
make docker-compose-logs

# Detener servicios
make docker-compose-down
```

---

## 📚 **Recursos Adicionales**

### Documentación

- **[README.md](README.md)** - Documentación principal
- **[QUICK_START.md](QUICK_START.md)** - Inicio rápido
- **[CHANGELOG.md](CHANGELOG.md)** - Registro de cambios
- **[FAQ.md](FAQ.md)** - Preguntas frecuentes
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Solución de problemas

### Comandos Útiles

```bash
# Ver ayuda de comandos
make help

# Limpiar archivos temporales
make clean

# Ejecutar linter
make lint

# Formatear código
make format

# Backup de datos
make backup
```

---

## 🔍 **Solución de Problemas**

### Problema: Error al instalar dependencias

```bash
# Limpiar cache de npm
npm cache clean --force

# Eliminar node_modules y reinstalar
rm -rf node_modules
npm install
```

### Problema: Puerto 3000 ya en uso

```bash
# Cambiar puerto en .env
PORT=3001

# O detener proceso usando el puerto
lsof -ti:3000 | xargs kill
```

### Problema: Error de certificados

```bash
# Verificar que los certificados existen
ls -la certificados/

# Verificar permisos
chmod 600 certificados/*.key
chmod 644 certificados/*.cer
```

---

## 🎯 **Próximos Pasos**

Una vez que tengas el proyecto configurado:

1. **Lee el [README.md](README.md)** para entender la estructura
2. **Explora las categorías** en los directorios principales
3. **Consulta [QUICK_START.md](QUICK_START.md)** para comenzar
4. **Revisa [CONTRIBUTING.md](05_technology/Other/contributing.md)** si quieres contribuir

---

## 📞 **Soporte**

¿Necesitas ayuda?

- 📧 **Email:** soporte@blatam.com
- 💬 **Discord:** https://discord.gg/blatam
- 🐛 **Issues:** https://github.com/blatam/documentos/issues

---

**¡Bienvenido al ecosistema BLATAM! 🚀**



