#!/bin/bash
# Script de deployment para producción

set -e

echo "🚀 Deploying TikTok Auto Edit System..."
echo ""

# Verificar Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado"
    exit 1
fi

# Verificar variables de entorno
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY no configurada"
    read -p "¿Continuar de todos modos? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Crear .env si no existe
if [ ! -f .env ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << EOF
OPENAI_API_KEY=${OPENAI_API_KEY:-}
WEBHOOK_SECRET=${WEBHOOK_SECRET:-$(openssl rand -hex 32)}
TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:-}
SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL:-}
EOF
    echo "✅ Archivo .env creado"
fi

# Build de imágenes
echo ""
echo "🔨 Construyendo imágenes Docker..."
docker-compose build

# Iniciar servicios
echo ""
echo "🚀 Iniciando servicios..."
docker-compose up -d

# Esperar a que los servicios estén listos
echo ""
echo "⏳ Esperando a que los servicios estén listos..."
sleep 10

# Health check
echo ""
echo "🏥 Verificando salud de los servicios..."
for service in api webhook dashboard; do
    if docker-compose ps | grep -q "$service.*Up"; then
        echo "✅ $service está corriendo"
    else
        echo "❌ $service no está corriendo"
    fi
done

echo ""
echo "="*60
echo "✅ Deployment completado"
echo "="*60
echo ""
echo "📊 Servicios:"
echo "  • API: http://localhost:5000"
echo "  • Webhooks: http://localhost:5001"
echo "  • Dashboard: http://localhost:5002"
echo ""
echo "📝 Comandos útiles:"
echo "  • Ver logs: docker-compose logs -f"
echo "  • Detener: docker-compose down"
echo "  • Reiniciar: docker-compose restart"
echo ""

