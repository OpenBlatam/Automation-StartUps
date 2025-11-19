#!/usr/bin/env python3
"""
Script para configurar el schema de nómina
Ejecuta el schema SQL y verifica la instalación
"""

import sys
import os
import argparse
from pathlib import Path

# Agregar el directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from airflow.providers.postgres.hooks.postgres import PostgresHook
from payroll.health_checks import PayrollHealthChecker


def setup_schema(
    postgres_conn_id: str = "postgres_default",
    schema_file: str = None
) -> bool:
    """
    Configura el schema de nómina
    
    Args:
        postgres_conn_id: ID de conexión de PostgreSQL
        schema_file: Ruta al archivo SQL (opcional)
    
    Returns:
        True si fue exitoso
    """
    if schema_file is None:
        # Buscar schema en la ubicación estándar
        base_dir = Path(__file__).parent.parent.parent.parent
        schema_file = base_dir / "db" / "payroll_schema.sql"
    
    if not os.path.exists(schema_file):
        print(f"Error: Schema file not found: {schema_file}")
        return False
    
    print(f"Reading schema from: {schema_file}")
    
    try:
        hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        
        # Leer y ejecutar schema
        with open(schema_file, 'r') as f:
            schema_sql = f.read()
        
        print("Executing schema SQL...")
        hook.run(schema_sql)
        
        print("Schema executed successfully!")
        
        # Verificar instalación
        print("\nVerifying installation...")
        health_checker = PayrollHealthChecker(postgres_conn_id=postgres_conn_id)
        schema_check = health_checker.check_schema_tables()
        
        if schema_check["status"] == "healthy":
            print("✅ All tables created successfully!")
            return True
        else:
            print(f"⚠️  Warning: {schema_check['message']}")
            return False
        
    except Exception as e:
        print(f"Error setting up schema: {e}")
        return False


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description="Setup payroll schema")
    parser.add_argument(
        "--conn-id",
        default="postgres_default",
        help="PostgreSQL connection ID"
    )
    parser.add_argument(
        "--schema-file",
        default=None,
        help="Path to schema SQL file"
    )
    
    args = parser.parse_args()
    
    success = setup_schema(
        postgres_conn_id=args.conn_id,
        schema_file=args.schema_file
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

