#!/bin/bash
# Backup de Datos del Workflow Sora
# ==================================

set -e

# Configuración
BACKUP_DIR="${BACKUP_DIR:-$HOME/sora_workflow_backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="sora_workflow_backup_${TIMESTAMP}"

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "💾 Backup de Datos del Workflow Sora"
echo "===================================="
echo ""

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"
echo -e "${GREEN}✅ Directorio de backup: $BACKUP_DIR${NC}"

# Directorio del workflow
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
N8N_DIR="$(dirname "$SCRIPT_DIR")"
WORKFLOW_BACKUP_DIR="$BACKUP_DIR/$BACKUP_NAME"

mkdir -p "$WORKFLOW_BACKUP_DIR"

# Backup de workflows
echo ""
echo "📋 Respaldando workflows..."
cp "$N8N_DIR"/n8n_workflow_sora*.json "$WORKFLOW_BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✅ Workflows respaldados${NC}"

# Backup de nodos adicionales
echo ""
echo "🔧 Respaldando nodos adicionales..."
cp "$N8N_DIR"/nodos_*.json "$WORKFLOW_BACKUP_DIR/" 2>/dev/null || true
echo -e "${GREEN}✅ Nodos respaldados${NC}"

# Backup de configuración
echo ""
echo "⚙️  Respaldando configuración..."
if [ -f "$N8N_DIR/.env" ]; then
    cp "$N8N_DIR/.env" "$WORKFLOW_BACKUP_DIR/.env.backup" 2>/dev/null || true
    echo -e "${GREEN}✅ Configuración respaldada${NC}"
else
    echo -e "${YELLOW}⚠️  Archivo .env no encontrado${NC}"
fi

# Backup de datos del workflow (si están en archivos)
echo ""
echo "📊 Respaldando datos del workflow..."
if [ -d "$N8N_DIR/data" ]; then
    cp -r "$N8N_DIR/data" "$WORKFLOW_BACKUP_DIR/data" 2>/dev/null || true
    echo -e "${GREEN}✅ Datos respaldados${NC}"
fi

# Backup de logs
echo ""
echo "📝 Respaldando logs..."
if [ -d "$N8N_DIR/logs" ]; then
    cp -r "$N8N_DIR/logs" "$WORKFLOW_BACKUP_DIR/logs" 2>/dev/null || true
    echo -e "${GREEN}✅ Logs respaldados${NC}"
fi

# Crear archivo de información
echo ""
echo "📄 Creando archivo de información..."
cat > "$WORKFLOW_BACKUP_DIR/backup_info.txt" << EOF
Backup del Workflow Sora
========================
Fecha: $(date)
Sistema: $(uname -a)
Usuario: $(whoami)
Directorio original: $N8N_DIR
Directorio backup: $WORKFLOW_BACKUP_DIR

Contenido:
- Workflows JSON
- Nodos adicionales
- Configuración (.env)
- Datos del workflow
- Logs

Para restaurar:
1. Copiar archivos de vuelta a $N8N_DIR
2. Restaurar .env desde .env.backup
3. Verificar permisos
EOF

echo -e "${GREEN}✅ Información guardada${NC}"

# Comprimir backup
echo ""
echo "📦 Comprimiendo backup..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME" 2>/dev/null || zip -r "${BACKUP_NAME}.zip" "$BACKUP_NAME" 2>/dev/null || true

if [ -f "${BACKUP_NAME}.tar.gz" ] || [ -f "${BACKUP_NAME}.zip" ]; then
    echo -e "${GREEN}✅ Backup comprimido${NC}"
    # Eliminar directorio sin comprimir para ahorrar espacio
    rm -rf "$BACKFLOW_BACKUP_DIR"
fi

# Limpiar backups antiguos (mantener últimos 10)
echo ""
echo "🧹 Limpiando backups antiguos..."
cd "$BACKUP_DIR"
ls -t sora_workflow_backup_*.tar.gz sora_workflow_backup_*.zip 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true
echo -e "${GREEN}✅ Backups antiguos eliminados (manteniendo últimos 10)${NC}"

# Resumen
echo ""
echo "===================================="
echo "✅ Backup completado"
echo "===================================="
echo ""
echo "📁 Ubicación: $BACKUP_DIR"
if [ -f "${BACKUP_NAME}.tar.gz" ]; then
    echo "📦 Archivo: ${BACKUP_NAME}.tar.gz"
    echo "📊 Tamaño: $(du -h "${BACKUP_NAME}.tar.gz" | cut -f1)"
elif [ -f "${BACKUP_NAME}.zip" ]; then
    echo "📦 Archivo: ${BACKUP_NAME}.zip"
    echo "📊 Tamaño: $(du -h "${BACKUP_NAME}.zip" | cut -f1)"
fi
echo ""
echo "💡 Para restaurar:"
echo "   tar -xzf ${BACKUP_NAME}.tar.gz -C /ruta/destino"
echo "   o"
echo "   unzip ${BACKUP_NAME}.zip -d /ruta/destino"


