#!/bin/bash

# Script de instalación y configuración del Sistema de Control de Inventario

echo "🚀 Instalando Sistema de Control de Inventario..."

# Verificar si Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no está instalado. Por favor instala Python 3.8 o superior."
    exit 1
fi

# Verificar versión de Python
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Se requiere Python 3.8 o superior. Versión actual: $python_version"
    exit 1
fi

echo "✅ Python $python_version detectado"

# Crear entorno virtual
echo "📦 Creando entorno virtual..."
python3 -m venv venv

# Activar entorno virtual
echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Actualizar pip
echo "⬆️ Actualizando pip..."
pip install --upgrade pip

# Instalar dependencias
echo "📚 Instalando dependencias..."
pip install -r requirements.txt

# Crear directorios necesarios
echo "📁 Creando directorios..."
mkdir -p logs
mkdir -p uploads
mkdir -p backups
mkdir -p static/images

# Copiar archivo de configuración
if [ ! -f .env ]; then
    echo "⚙️ Creando archivo de configuración..."
    cp env.example .env
    echo "📝 Por favor edita el archivo .env con tus configuraciones"
fi

# Inicializar base de datos
echo "🗄️ Inicializando base de datos..."
export FLASK_APP=app.py
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Crear datos de ejemplo (opcional)
echo "📊 ¿Deseas crear datos de ejemplo? (y/n)"
read -r create_sample_data

if [ "$create_sample_data" = "y" ] || [ "$create_sample_data" = "Y" ]; then
    echo "🎯 Creando datos de ejemplo..."
    python create_sample_data.py
fi

echo ""
echo "🎉 ¡Instalación completada!"
echo ""
echo "Para ejecutar el sistema:"
echo "1. Activa el entorno virtual: source venv/bin/activate"
echo "2. Configura las variables en .env"
echo "3. Ejecuta: python app.py"
echo ""
echo "El sistema estará disponible en: http://localhost:5000"
echo ""
echo "📚 Documentación completa en README.md"



