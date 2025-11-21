#!/usr/bin/env python3
"""
CLI para gestión del framework de sincronización
================================================

Utilidades de línea de comandos para:
- Ver estadísticas de sincronizaciones
- Resolver conflictos
- Limpiar historial
- Exportar reportes
- Validar configuraciones
"""
import argparse
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# Agregar path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from data.integrations.utils import (
    get_sync_stats,
    get_pending_conflicts,
    resolve_conflict,
    cleanup_old_sync_history,
    export_sync_report,
    validate_sync_config
)


def get_db_connection_string() -> str:
    """Obtiene string de conexión desde variables de entorno"""
    db_url = os.getenv("SYNC_DB_CONNECTION_STRING")
    if db_url:
        return db_url
    
    # Construir desde componentes
    user = os.getenv("SYNC_DB_USER", "postgres")
    password = os.getenv("SYNC_DB_PASSWORD", "")
    host = os.getenv("SYNC_DB_HOST", "localhost")
    port = os.getenv("SYNC_DB_PORT", "5432")
    dbname = os.getenv("SYNC_DB_NAME", "analytics")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def cmd_stats(args):
    """Muestra estadísticas de sincronizaciones"""
    db_conn = get_db_connection_string()
    
    stats = get_sync_stats(
        db_conn,
        days=args.days,
        source_type=args.source_type,
        target_type=args.target_type
    )
    
    if "error" in stats:
        print(f"Error: {stats['error']}", file=sys.stderr)
        sys.exit(1)
    
    print(json.dumps(stats, indent=2, default=str))


def cmd_conflicts(args):
    """Lista conflictos pendientes"""
    db_conn = get_db_connection_string()
    
    conflicts = get_pending_conflicts(db_conn, limit=args.limit)
    
    if not conflicts:
        print("No hay conflictos pendientes")
        return
    
    print(f"\nEncontrados {len(conflicts)} conflictos pendientes:\n")
    for i, conflict in enumerate(conflicts, 1):
        print(f"{i}. ID: {conflict['id']}")
        print(f"   Tipo: {conflict['conflict_type']}")
        print(f"   Source: {conflict['source_type']} ({conflict['source_id']})")
        print(f"   Target: {conflict['target_type']} ({conflict.get('target_id', 'N/A')})")
        print(f"   Creado: {conflict['created_at']}")
        print()


def cmd_resolve(args):
    """Resuelve un conflicto"""
    db_conn = get_db_connection_string()
    
    try:
        resolution_data = json.loads(args.resolution_data) if args.resolution_data else {}
    except json.JSONDecodeError:
        print("Error: resolution_data debe ser JSON válido", file=sys.stderr)
        sys.exit(1)
    
    success = resolve_conflict(
        db_conn,
        args.conflict_id,
        resolution_data,
        resolved_by=args.resolved_by
    )
    
    if success:
        print(f"Conflicto {args.conflict_id} resuelto exitosamente")
    else:
        print(f"Error: No se pudo resolver conflicto {args.conflict_id}", file=sys.stderr)
        sys.exit(1)


def cmd_cleanup(args):
    """Limpia historial antiguo"""
    db_conn = get_db_connection_string()
    
    result = cleanup_old_sync_history(
        db_conn,
        days=args.days,
        dry_run=args.dry_run
    )
    
    print(json.dumps(result, indent=2, default=str))
    
    if not args.dry_run and result.get("deleted", 0) > 0:
        print(f"\n✅ Eliminados {result['deleted']} registros antiguos")


def cmd_export(args):
    """Exporta reporte de sincronizaciones"""
    db_conn = get_db_connection_string()
    
    start_date = None
    end_date = None
    
    if args.start_date:
        start_date = datetime.fromisoformat(args.start_date)
    if args.end_date:
        end_date = datetime.fromisoformat(args.end_date)
    
    report = export_sync_report(
        db_conn,
        sync_id=args.sync_id,
        start_date=start_date,
        end_date=end_date,
        output_format=args.format
    )
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"Reporte guardado en {args.output}")
    else:
        print(report)


def cmd_validate(args):
    """Valida configuración de sincronización"""
    try:
        if args.config_file:
            with open(args.config_file, 'r') as f:
                config = json.load(f)
        else:
            config = json.loads(args.config_json)
        
        is_valid, error = validate_sync_config(config)
        
        if is_valid:
            print("✅ Configuración válida")
            sys.exit(0)
        else:
            print(f"❌ Configuración inválida: {error}", file=sys.stderr)
            sys.exit(1)
    except FileNotFoundError:
        print(f"Error: Archivo no encontrado: {args.config_file}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: JSON inválido: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="CLI para gestión del framework de sincronización"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')
    
    # Comando stats
    stats_parser = subparsers.add_parser('stats', help='Mostrar estadísticas')
    stats_parser.add_argument('--days', type=int, default=7, help='Días hacia atrás')
    stats_parser.add_argument('--source-type', help='Filtrar por tipo de fuente')
    stats_parser.add_argument('--target-type', help='Filtrar por tipo de destino')
    
    # Comando conflicts
    conflicts_parser = subparsers.add_parser('conflicts', help='Listar conflictos pendientes')
    conflicts_parser.add_argument('--limit', type=int, default=100, help='Límite de resultados')
    
    # Comando resolve
    resolve_parser = subparsers.add_parser('resolve', help='Resolver conflicto')
    resolve_parser.add_argument('conflict_id', type=int, help='ID del conflicto')
    resolve_parser.add_argument('--resolution-data', help='JSON con datos de resolución')
    resolve_parser.add_argument('--resolved-by', default='cli', help='Usuario que resuelve')
    
    # Comando cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpiar historial antiguo')
    cleanup_parser.add_argument('--days', type=int, default=90, help='Mantener últimos N días')
    cleanup_parser.add_argument('--dry-run', action='store_true', help='Solo mostrar qué se eliminaría')
    
    # Comando export
    export_parser = subparsers.add_parser('export', help='Exportar reporte')
    export_parser.add_argument('--sync-id', help='ID de sincronización específica')
    export_parser.add_argument('--start-date', help='Fecha de inicio (ISO format)')
    export_parser.add_argument('--end-date', help='Fecha de fin (ISO format)')
    export_parser.add_argument('--format', choices=['json', 'csv'], default='json', help='Formato de salida')
    export_parser.add_argument('--output', help='Archivo de salida (opcional)')
    
    # Comando validate
    validate_parser = subparsers.add_parser('validate', help='Validar configuración')
    validate_group = validate_parser.add_mutually_exclusive_group(required=True)
    validate_group.add_argument('--config-file', help='Archivo JSON con configuración')
    validate_group.add_argument('--config-json', help='JSON string con configuración')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Ejecutar comando
    commands = {
        'stats': cmd_stats,
        'conflicts': cmd_conflicts,
        'resolve': cmd_resolve,
        'cleanup': cmd_cleanup,
        'export': cmd_export,
        'validate': cmd_validate,
    }
    
    commands[args.command](args)


if __name__ == '__main__':
    main()


