#!/bin/bash
# Script de Setup Automatizado - Sistema de Ventas
# Configura e instala todo el sistema de automatización de ventas

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Banner
echo ""
echo "=========================================="
echo "  Sistema de Automatización de Ventas"
echo "  Setup Automatizado"
echo "=========================================="
echo ""

# Verificar que estamos en el directorio correcto
if [ ! -f "data/db/sales_tracking_schema.sql" ]; then
    print_error "No se encontró sales_tracking_schema.sql"
    print_info "Ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# Solicitar información de conexión
print_info "Configuración de Base de Datos"
read -p "Host PostgreSQL [localhost]: " DB_HOST
DB_HOST=${DB_HOST:-localhost}

read -p "Puerto PostgreSQL [5432]: " DB_PORT
DB_PORT=${DB_PORT:-5432}

read -p "Nombre de base de datos: " DB_NAME
if [ -z "$DB_NAME" ]; then
    print_error "El nombre de la base de datos es requerido"
    exit 1
fi

read -p "Usuario PostgreSQL [postgres]: " DB_USER
DB_USER=${DB_USER:-postgres}

read -s -p "Contraseña PostgreSQL: " DB_PASS
echo ""

# Construir connection string
export PGPASSWORD=$DB_PASS
DB_CONN="postgresql://${DB_USER}:${DB_PASS}@${DB_HOST}:${DB_PORT}/${DB_NAME}"

# Verificar conexión
print_info "Verificando conexión a PostgreSQL..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c "SELECT 1;" > /dev/null 2>&1; then
    print_success "Conexión exitosa"
else
    print_error "No se pudo conectar a PostgreSQL"
    exit 1
fi

# Crear schema
print_info "Instalando schema de base de datos..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f data/db/sales_tracking_schema.sql > /dev/null 2>&1; then
    print_success "Schema instalado correctamente"
else
    print_warning "Algunos objetos pueden ya existir (esto es normal)"
fi

# Instalar queries optimizadas
print_info "Instalando queries optimizadas..."
if psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f data/db/sales_queries_optimized.sql > /dev/null 2>&1; then
    print_success "Queries optimizadas instaladas"
else
    print_warning "Algunos objetos pueden ya existir (esto es normal)"
fi

# Configurar vendedores
print_info "Configuración de Equipo de Ventas"
read -p "¿Deseas configurar vendedores ahora? (s/n) [n]: " CONFIGURE_REPS
CONFIGURE_REPS=${CONFIGURE_REPS:-n}

if [ "$CONFIGURE_REPS" = "s" ] || [ "$CONFIGURE_REPS" = "S" ]; then
    print_info "Ingresa emails de vendedores (uno por línea, línea vacía para terminar):"
    REPS=()
    while true; do
        read -p "Email del vendedor (o Enter para terminar): " REP_EMAIL
        if [ -z "$REP_EMAIL" ]; then
            break
        fi
        REPS+=("'$REP_EMAIL'")
    done
    
    if [ ${#REPS[@]} -gt 0 ]; then
        REPS_STRING=$(IFS=,; echo "${REPS[*]}")
        
        # Actualizar función
        psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" <<EOF > /dev/null 2>&1
CREATE OR REPLACE FUNCTION auto_assign_sales_rep(p_lead_ext_id VARCHAR(128))
RETURNS VARCHAR(256) AS \$\$
DECLARE
    v_assigned_email VARCHAR(256);
    v_sales_team TEXT[] := ARRAY[$REPS_STRING];
    v_current_count INT;
BEGIN
    SELECT assigned_to INTO v_assigned_email
    FROM (
        SELECT 
            unnest(v_sales_team) AS email,
            COUNT(*) FILTER (WHERE stage NOT IN ('closed_lost', 'closed_won')) AS active_count
        FROM sales_pipeline
        WHERE assigned_to = ANY(v_sales_team)
        GROUP BY email
        ORDER BY active_count ASC, email ASC
        LIMIT 1
    ) AS team_load;
    
    IF v_assigned_email IS NULL THEN
        v_assigned_email := v_sales_team[1];
    END IF;
    
    RETURN v_assigned_email;
END;
\$\$ LANGUAGE plpgsql;
EOF
        print_success "${#REPS[@]} vendedores configurados"
    fi
fi

# Validar instalación
print_info "Validando instalación..."
python3 scripts/validate_sales_system.py --db "$DB_CONN" > /tmp/validation_output.txt 2>&1 || true

if grep -q "✅ Validación completada" /tmp/validation_output.txt; then
    print_success "Validación exitosa"
    cat /tmp/validation_output.txt
else
    print_warning "Hubo algunos warnings en la validación:"
    cat /tmp/validation_output.txt
fi

# Health check
print_info "Ejecutando health check..."
python3 scripts/sales_health_check.py --db "$DB_CONN" || true

# Resumen
echo ""
echo "=========================================="
print_success "Setup completado!"
echo "=========================================="
echo ""
print_info "Próximos pasos:"
echo "  1. Configurar DAGs en Airflow"
echo "  2. Configurar webhooks (email, Slack)"
echo "  3. Crear primera campaña"
echo "  4. Revisar documentación: data/db/QUICK_START_SALES.md"
echo ""
print_info "Connection string guardado en variable de entorno PGPASSWORD"
echo "Para validar sistema: python3 scripts/validate_sales_system.py --db \"$DB_CONN\""
echo "Para health check: python3 scripts/sales_health_check.py --db \"$DB_CONN\""
echo ""

# Limpiar password
unset PGPASSWORD


