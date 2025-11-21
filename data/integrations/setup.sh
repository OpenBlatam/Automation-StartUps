#!/bin/bash
# Script de setup para el framework de sincronización
# ====================================================

set -e

echo "🚀 Configurando framework de sincronización..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 no encontrado. Por favor instálalo primero."
    exit 1
fi

echo "✅ Python encontrado: $(python3 --version)"

# Crear entorno virtual si no existe
if [ ! -d "venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv venv
fi

echo "🔧 Activando entorno virtual..."
source venv/bin/activate

# Instalar dependencias
echo "📥 Instalando dependencias..."
pip install --upgrade pip
pip install -r requirements.txt 2>/dev/null || {
    echo "📝 Creando requirements.txt..."
    cat > requirements.txt << EOF
psycopg2-binary>=2.9.0
requests>=2.28.0
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-oauthlib>=0.5.0
google-auth-httplib2>=0.1.0
tenacity>=8.0.0
EOF
    pip install -r requirements.txt
}

# Verificar variables de entorno
echo "🔍 Verificando variables de entorno..."

REQUIRED_VARS=(
    "SYNC_DB_CONNECTION_STRING"
)

MISSING_VARS=()
for var in "${REQUIRED_VARS[@]}"; do
    if [ -z "${!var}" ]; then
        MISSING_VARS+=("$var")
    fi
done

if [ ${#MISSING_VARS[@]} -gt 0 ]; then
    echo "⚠️  Variables de entorno faltantes:"
    for var in "${MISSING_VARS[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "💡 Crea un archivo .env con:"
    echo "   SYNC_DB_CONNECTION_STRING=postgresql://user:password@host:port/dbname"
    echo ""
    echo "   O exporta las variables:"
    echo "   export SYNC_DB_CONNECTION_STRING='postgresql://...'"
fi

# Crear esquema de base de datos
echo "🗄️  Creando esquema de base de datos..."
if [ -n "$SYNC_DB_CONNECTION_STRING" ]; then
    python3 << EOF
import psycopg2
import sys

try:
    conn = psycopg2.connect("$SYNC_DB_CONNECTION_STRING")
    cur = conn.cursor()
    
    with open('sync_schema.sql', 'r') as f:
        schema_sql = f.read()
    
    # Ejecutar en transacciones separadas para cada statement
    statements = schema_sql.split(';')
    for statement in statements:
        statement = statement.strip()
        if statement and not statement.startswith('--'):
            try:
                cur.execute(statement)
            except Exception as e:
                if 'already exists' not in str(e).lower():
                    print(f"Warning: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Esquema creado exitosamente")
except Exception as e:
    print(f"❌ Error creando esquema: {e}")
    sys.exit(1)
EOF
else
    echo "⚠️  SYNC_DB_CONNECTION_STRING no configurado, saltando creación de esquema"
fi

# Hacer CLI ejecutable
if [ -f "cli.py" ]; then
    chmod +x cli.py
    echo "✅ CLI configurado como ejecutable"
fi

echo ""
echo "✨ Setup completado!"
echo ""
echo "📚 Próximos pasos:"
echo "   1. Configura las variables de entorno (.env o export)"
echo "   2. Configura credenciales de los sistemas (HubSpot, QuickBooks, etc.)"
echo "   3. Ejecuta: python3 examples.py para probar"
echo "   4. Usa el CLI: python3 cli.py stats"
echo "   5. Configura DAGs de Airflow si usas Airflow"
echo ""


