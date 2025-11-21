#!/bin/bash
# Script de Backup Automatizado del Sistema de Ventas
# Realiza backups selectivos de datos críticos

set -e

# Configuración
DB_CONN="${SALES_DB_CONN:-}"
BACKUP_DIR="${BACKUP_DIR:-./backups/sales}"
RETENTION_DAYS="${RETENTION_DAYS:-30}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Verificar configuración
if [ -z "$DB_CONN" ]; then
    echo "Error: SALES_DB_CONN no configurado"
    echo "Uso: SALES_DB_CONN='postgresql://...' $0"
    exit 1
fi

# Crear directorio de backup
mkdir -p "$BACKUP_DIR"

print_info "Iniciando backup del sistema de ventas..."
print_info "Timestamp: $TIMESTAMP"
print_info "Directorio: $BACKUP_DIR"

# Backup de tablas críticas
TABLES=(
    "sales_pipeline"
    "sales_followup_tasks"
    "lead_score_history"
    "sales_campaign_executions"
    "sales_campaign_events"
)

for table in "${TABLES[@]}"; do
    print_info "Backing up $table..."
    
    psql "$DB_CONN" -c "\COPY $table TO '$BACKUP_DIR/${table}_${TIMESTAMP}.csv' CSV HEADER" || {
        echo "Error en backup de $table"
        continue
    }
    
    print_success "$table backup completado"
done

# Backup de configuración de campañas
print_info "Backing up campañas..."
psql "$DB_CONN" -c "\COPY sales_campaigns TO '$BACKUP_DIR/sales_campaigns_${TIMESTAMP}.csv' CSV HEADER" || {
    echo "Error en backup de campañas"
}

# Backup completo en SQL (schema + data)
print_info "Creando backup SQL completo..."
pg_dump "$DB_CONN" \
    --schema-only \
    --file "$BACKUP_DIR/schema_${TIMESTAMP}.sql" \
    --table=sales_* \
    --table=lead_score_history \
    --table=nurturing_* || {
    echo "Error en backup de schema"
}

# Backup de datos (sin schema)
print_info "Creando backup de datos..."
pg_dump "$DB_CONN" \
    --data-only \
    --file "$BACKUP_DIR/data_${TIMESTAMP}.sql" \
    --table=sales_* \
    --table=lead_score_history \
    --table=nurturing_* || {
    echo "Error en backup de datos"
}

# Comprimir backups
print_info "Comprimiendo backups..."
cd "$BACKUP_DIR"
tar -czf "sales_backup_${TIMESTAMP}.tar.gz" \
    *_${TIMESTAMP}.csv \
    schema_${TIMESTAMP}.sql \
    data_${TIMESTAMP}.sql 2>/dev/null || true

# Limpiar archivos individuales (opcional)
# rm -f *_${TIMESTAMP}.csv schema_${TIMESTAMP}.sql data_${TIMESTAMP}.sql

# Limpiar backups antiguos
print_info "Limpiando backups antiguos (>${RETENTION_DAYS} días)..."
find "$BACKUP_DIR" -name "sales_backup_*.tar.gz" -mtime +${RETENTION_DAYS} -delete 2>/dev/null || true

# Resumen
BACKUP_SIZE=$(du -sh "$BACKUP_DIR/sales_backup_${TIMESTAMP}.tar.gz" 2>/dev/null | cut -f1 || echo "N/A")
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l || echo "0")

print_success "Backup completado!"
print_info "Archivo: sales_backup_${TIMESTAMP}.tar.gz"
print_info "Tamaño: $BACKUP_SIZE"
print_info "Total de backups: $BACKUP_COUNT"
print_info "Ubicación: $BACKUP_DIR"


