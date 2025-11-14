#!/bin/bash
# nvm-setup.sh - Setup Node.js version manager

echo "🔧 Configurando NVM (Node Version Manager)..."

# Verificar si nvm está instalado
if ! command -v nvm &> /dev/null; then
    echo "📥 Instalando NVM..."
    
    # Descargar e instalar NVM
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
    
    # Cargar nvm en la sesión actual
    export NVM_DIR="$HOME/.nvm"
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
fi

# Instalar y usar la versión especificada en .nvmrc
if [ -f .nvmrc ]; then
    NODE_VERSION=$(cat .nvmrc)
    echo "📦 Instalando Node.js $NODE_VERSION..."
    nvm install $NODE_VERSION
    nvm use $NODE_VERSION
    echo "✅ Node.js $NODE_VERSION configurado"
else
    echo "⚠️  No se encontró archivo .nvmrc"
fi

echo "✅ Configuración completada"
echo ""
echo "Para usar nvm en nuevas terminales, ejecuta:"
echo "  source ~/.bashrc  # o ~/.zshrc"
echo ""
echo "Para cambiar a esta versión de Node.js:"
echo "  nvm use"



