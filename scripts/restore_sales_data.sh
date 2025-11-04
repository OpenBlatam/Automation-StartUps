#!/bin/bash
# Script de Restore del Sistema de Ventas
# Restaura datos desde backup

set -e

# Configuración
DB_CONN="${SALES_DB_CONN:-}"
BACKUP_FILE="${1:-}"

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Verificar configuración
if [ -z "$DB_CONN" ]; then
    print_error "SALES_DB_CONN no configurado"
    echo "Uso: SALES_DB_CONN='postgresql://...' $0 <backup_file.tar.gz>"
    exit 1
fi

if [ -z "$BACKUP_FILE" ]; then
    print_error "Archivo de backup no especificado"
    echo "Uso: $0 <backup_file.tar.gz>"
    exit 1
fi

if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Archivo de backup no encontrado: $BACKUP_FILE"
    exit 1
fi

# Confirmar
print_error "⚠️  ADVERTENCIA: Esto restaurará datos y puede sobrescribir datos existentes"
read -p "¿Continuar? (escribe 'yes' para confirmar): " confirm

if [ "$confirm" != "yes" ]; then
    print_info "Operación cancelada"
    exit 0
fi

# Extraer backup
TEMP_DIR=$(mktemp -d)
print_info "Extrayendo backup..."
tar -xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Restaurar schema
if [ -f "$TEMP_DIR/schema_"*.sql ]; then
    print_info "Restaurando schema..."
    psql "$DB_CONN" -f "$TEMP_DIR"/schema_*.sql || {
        print_error "Error restaurando schema"
    }
fi

# Restaurar datos
if [ -f "$TEMP_DIR/data_"*.sql ]; then
    print_info "Restaurando datos..."
    psql "$DB_CONN" -f "$TEMP_DIR"/data_*.sql || {
        print_error "Error restaurando datos"
    }
fi

# Restaurar tablas individuales (opcional)
print_info "Restaurando tablas desde CSV..."
for csv_file in "$TEMP_DIR"/*_*.csv; do
    if [ -f "$csv_file" ]; then
        table_name=$(basename "$csv_file" | sed 's/_[0-9]*.csv//')
        print_info "Restaurando $table_name..."
        
        # Truncar tabla antes de restaurar (opcional, descomentar si necesario)
        # psql "$DB_CONN" -c "TRUNCATE TABLE $table_name CASCADE;" || true
        
        psql "$DB_CONN" -c "\COPY $table_name FROM '$csv_file' CSV HEADER" || {
            print_error "Error restaurando $table_name"
        }
    fi
done

# Limpiar
rm -rf "$TEMP_DIR"

print_success "Restore completado!"
print_info "Verificar datos con: python scripts/validate_sales_system.py --db \"$DB_CONN\""


