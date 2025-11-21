#!/usr/bin/env python3
"""
Script de Utilidades para Gestión de Contratos
CLI para operaciones comunes
"""

import argparse
import json
import sys
from typing import Dict, Any

# Configurar path para imports
sys.path.insert(0, '/path/to/airflow')  # Ajustar según instalación

from data.airflow.plugins.contract_integrations import (
    create_contract_from_template,
    send_contract_for_signature,
    check_contract_signature_status,
    get_template,
    get_contract_analytics,
    search_contracts
)
from data.airflow.plugins.contract_export import (
    export_contracts_to_csv,
    export_contracts_to_json,
    create_backup
)
from data.airflow.plugins.contract_migration import (
    migrate_contracts_from_csv,
    migrate_contracts_from_json
)


def cmd_create_contract(args):
    """Comando para crear contrato"""
    with open(args.variables_file, 'r') as f:
        variables = json.load(f)
    
    result = create_contract_from_template(
        template_id=args.template_id,
        primary_party_email=args.email,
        primary_party_name=args.name,
        contract_variables=variables
    )
    
    print(json.dumps(result, indent=2))
    return result


def cmd_send_for_signature(args):
    """Comando para enviar contrato para firma"""
    result = send_contract_for_signature(
        contract_id=args.contract_id,
        esignature_provider=args.provider
    )
    
    print(json.dumps(result, indent=2))
    return result


def cmd_check_status(args):
    """Comando para verificar estado"""
    result = check_contract_signature_status(contract_id=args.contract_id)
    print(json.dumps(result, indent=2))
    return result


def cmd_export(args):
    """Comando para exportar"""
    if args.format == "csv":
        content = export_contracts_to_csv(
            start_date=args.start_date,
            end_date=args.end_date,
            contract_type=args.type,
            status=args.status
        )
        with open(args.output, 'w') as f:
            f.write(content)
        print(f"Exportado a {args.output}")
    else:
        data = export_contracts_to_json(
            start_date=args.start_date,
            end_date=args.end_date,
            contract_type=args.type,
            status=args.status,
            include_content=args.include_content
        )
        with open(args.output, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Exportado a {args.output}")


def cmd_backup(args):
    """Comando para crear backup"""
    backup = create_backup(
        output_format=args.format,
        include_versions=args.include_versions
    )
    
    if args.format == "json":
        with open(args.output, 'w') as f:
            json.dump(backup, f, indent=2, default=str)
    else:
        # Para CSV, usar export normal
        content = export_contracts_to_csv()
        with open(args.output, 'w') as f:
            f.write(content)
    
    print(f"Backup creado en {args.output}")
    print(json.dumps(backup, indent=2, default=str))


def cmd_analytics(args):
    """Comando para analytics"""
    analytics = get_contract_analytics(
        start_date=args.start_date,
        end_date=args.end_date,
        contract_type=args.type
    )
    
    print(json.dumps(analytics, indent=2, default=str))
    return analytics


def cmd_search(args):
    """Comando para búsqueda"""
    results = search_contracts(
        search_term=args.query,
        contract_type=args.type,
        status=args.status,
        primary_party_email=args.email,
        limit=args.limit,
        offset=args.offset
    )
    
    print(json.dumps(results, indent=2, default=str))
    return results


def main():
    parser = argparse.ArgumentParser(description="CLI para gestión de contratos")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Crear contrato')
    create_parser.add_argument('--template-id', required=True)
    create_parser.add_argument('--email', required=True)
    create_parser.add_argument('--name', required=True)
    create_parser.add_argument('--variables-file', required=True)
    create_parser.set_defaults(func=cmd_create_contract)
    
    # Comando send
    send_parser = subparsers.add_parser('send', help='Enviar para firma')
    send_parser.add_argument('--contract-id', required=True)
    send_parser.add_argument('--provider', default='docusign')
    send_parser.set_defaults(func=cmd_send_for_signature)
    
    # Comando status
    status_parser = subparsers.add_parser('status', help='Verificar estado')
    status_parser.add_argument('--contract-id', required=True)
    status_parser.set_defaults(func=cmd_check_status)
    
    # Comando export
    export_parser = subparsers.add_parser('export', help='Exportar contratos')
    export_parser.add_argument('--output', required=True)
    export_parser.add_argument('--format', choices=['csv', 'json'], default='json')
    export_parser.add_argument('--start-date')
    export_parser.add_argument('--end-date')
    export_parser.add_argument('--type')
    export_parser.add_argument('--status')
    export_parser.add_argument('--include-content', action='store_true')
    export_parser.set_defaults(func=cmd_export)
    
    # Comando backup
    backup_parser = subparsers.add_parser('backup', help='Crear backup')
    backup_parser.add_argument('--output', required=True)
    backup_parser.add_argument('--format', choices=['csv', 'json'], default='json')
    backup_parser.add_argument('--include-versions', action='store_true')
    backup_parser.set_defaults(func=cmd_backup)
    
    # Comando analytics
    analytics_parser = subparsers.add_parser('analytics', help='Obtener analytics')
    analytics_parser.add_argument('--start-date')
    analytics_parser.add_argument('--end-date')
    analytics_parser.add_argument('--type')
    analytics_parser.set_defaults(func=cmd_analytics)
    
    # Comando search
    search_parser = subparsers.add_parser('search', help='Buscar contratos')
    search_parser.add_argument('--query')
    search_parser.add_argument('--type')
    search_parser.add_argument('--status')
    search_parser.add_argument('--email')
    search_parser.add_argument('--limit', type=int, default=100)
    search_parser.add_argument('--offset', type=int, default=0)
    search_parser.set_defaults(func=cmd_search)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()

