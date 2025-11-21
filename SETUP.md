# 🚀 Guía de Configuración - Documentos BLATAM

Esta guía te ayudará a configurar y comenzar a usar Documentos BLATAM desde cero.

---

## 📋 Tabla de Contenidos

- [Requisitos Previos](#requisitos-previos)
- [Instalación Rápida](#instalación-rápida)
- [Configuración Detallada](#configuración-detallada)
- [Verificación](#verificación)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Requisitos Previos

### Software Necesario

| Software | Versión Mínima | Descarga |
|----------|----------------|----------|
| **Node.js** | 18.0.0+ | [nodejs.org](https://nodejs.org/) |
| **npm** | 8.0.0+ | (viene con Node.js) |
| **Python** | 3.9+ | [python.org](https://www.python.org/) |
| **Git** | 2.30+ | [git-scm.com](https://git-scm.com/) |
| **Docker** | 20.10+ (opcional) | [docker.com](https://www.docker.com/) |

### Herramientas Opcionales

- **VS Code** o editor de texto preferido
- **Markdown Preview** extension (para VS Code)
- **Prettier** (formateador de código)

### Cuentas y API Keys (Opcional)

Para funcionalidades avanzadas, puedes necesitar:
- **OpenAI API Key** (para GPT-4)
- **Google AI Key** (para Gemini)
- **Anthropic API Key** (para Claude)

---

## ⚡ Instalación Rápida

### Paso 1: Clonar el Repositorio

```bash
# Si tienes acceso al repositorio Git
git clone https://github.com/blatam/documentos.git
cd documentos

# O si ya tienes el repositorio local
cd /Users/adan/Documents/documentos_blatam
```

### Paso 2: Verificar Instalación

```bash
# Verificar Node.js
node --version  # Debe ser v18.0.0 o superior

# Verificar npm
npm --version   # Debe ser v8.0.0 o superior

# Verificar Python
python3 --version  # Debe ser 3.9 o superior
```

### Paso 3: Instalar Dependencias (Opcional)

```bash
# Si hay package.json en la raíz
npm install

# Instalar herramientas globales (opcional)
npm install -g prettier markdownlint-cli2
```

### Paso 4: Verificar Estructura

```bash
# Verificar que los directorios principales existen
ls -la

# Deberías ver directorios como:
# - 01_marketing/
# - 06_documentation/
# - 09_sales/
# etc.
```

---

## 🔧 Configuración Detallada

### Configuración de Variables de Entorno

Si necesitas configurar variables de entorno:

```bash
# Copiar archivo de ejemplo
cp env.example .env

# Editar con tu editor preferido
nano .env
# o
code .env  # Si usas VS Code
```

### Configuración de Python (para Scripts)

```bash
# Crear entorno virtual (recomendado)
python3 -m venv venv

# Activar entorno virtual
# En macOS/Linux:
source venv/bin/activate

# En Windows:
venv\Scripts\activate

# Instalar dependencias Python
pip install -r requirements.txt
```

### Configuración de Herramientas de Desarrollo

#### Prettier (Formateador)

```bash
# Instalar Prettier
npm install -g prettier

# Formatear todos los archivos markdown
prettier --write "**/*.md"
```

#### Markdown Linter

```bash
# Instalar markdownlint
npm install -g markdownlint-cli2

# Verificar formato
markdownlint-cli2 "**/*.md"
```

---

## ✅ Verificación

### Verificar Instalación

```bash
# Verificar estructura del proyecto
ls -la

# Verificar que README existe
test -f README.md && echo "✓ README.md encontrado"

# Verificar directorios principales
test -d 06_documentation && echo "✓ Documentación encontrada"
test -d 01_marketing && echo "✓ Marketing encontrado"
test -d 09_sales && echo "✓ Ventas encontrado"
```

### Probar Scripts

```bash
# Probar script de organización (si existe)
python3 organize_root_files.py --help

# Verificar herramientas
node tools/check_token_coverage.js --help
```

### Verificar Documentación

```bash
# Abrir documentación principal
open README.md  # macOS
# o
xdg-open README.md  # Linux
# o
start README.md  # Windows
```

---

## 🐳 Configuración con Docker (Opcional)

Si prefieres usar Docker:

```bash
# Construir contenedores
docker-compose build

# Iniciar servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

---

## 🔍 Verificación de Funcionalidad

### Probar Navegación

1. Abre `README.md` en tu editor
2. Verifica que los enlaces funcionan
3. Navega a `06_documentation/start_here.md`
4. Revisa el índice en `06_documentation/INDEX.md`

### Probar Scripts

```bash
# Script de organización
python3 organize_root_files.py

# Scripts de análisis
cd 06_documentation/Scripts
python3 analyze_content.py
```

---

## 🛠️ Troubleshooting

### Problemas Comunes

#### Error: "node: command not found"

**Solución:**
```bash
# Instalar Node.js desde nodejs.org
# O usar nvm:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
nvm use 18
```

#### Error: "python3: command not found"

**Solución:**
```bash
# macOS: Python viene preinstalado, verifica versión
python3 --version

# Si no está instalado:
brew install python3  # macOS con Homebrew
# o descarga desde python.org
```

#### Error: "Permission denied" en scripts

**Solución:**
```bash
# Dar permisos de ejecución
chmod +x script_name.sh
chmod +x script_name.py
```

#### Enlaces rotos en documentación

**Solución:**
```bash
# Usar script de verificación de enlaces
cd 06_documentation/Scripts
python3 find_broken_links.py
```

#### Problemas con frontmatter

**Solución:**
```bash
# Validar frontmatter
cd 06_documentation/Scripts
python3 frontmatter_validator.py
```

---

## 📚 Próximos Pasos

Después de la configuración:

1. **Lee el README**: [`README.md`](README.md)
2. **Inicio rápido**: [`06_documentation/start_here.md`](06_documentation/start_here.md)
3. **Explora el índice**: [`06_documentation/INDEX.md`](06_documentation/INDEX.md)
4. **Revisa la arquitectura**: [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## 🆘 Obtener Ayuda

Si encuentras problemas:

1. Revisa [`06_documentation/Troubleshooting/`](06_documentation/Troubleshooting/)
2. Consulta el [README.md](README.md)
3. Abre un issue en el repositorio
4. Revisa la documentación en `06_documentation/`

---

## ✅ Checklist de Configuración

- [ ] Node.js instalado (v18+)
- [ ] npm instalado (v8+)
- [ ] Python instalado (v3.9+)
- [ ] Git instalado
- [ ] Repositorio clonado
- [ ] Estructura de directorios verificada
- [ ] README.md leído
- [ ] Scripts probados (opcional)
- [ ] Variables de entorno configuradas (si aplica)

---

**¡Configuración completada! 🎉**

Ahora puedes comenzar a usar Documentos BLATAM. Consulta el [README.md](README.md) para comenzar.

