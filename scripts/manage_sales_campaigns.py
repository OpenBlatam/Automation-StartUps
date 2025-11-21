#!/usr/bin/env python3
"""
Script de utilidad para gestionar campañas de ventas desde la línea de comandos.
Permite crear, listar, activar/desactivar y eliminar campañas.
"""

import argparse
import json
import sys
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_connection(connection_string: str):
    """Obtiene conexión a la base de datos."""
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}", file=sys.stderr)
        sys.exit(1)


def list_campaigns(conn) -> List[Dict[str, Any]]:
    """Lista todas las campañas."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                id,
                name,
                description,
                campaign_type,
                enabled,
                max_leads_per_run,
                trigger_criteria,
                created_at,
                updated_at
            FROM sales_campaigns
            ORDER BY id DESC
        """)
        return cur.fetchall()


def create_campaign(conn, name: str, description: str, campaign_type: str,
                   trigger_criteria: Dict[str, Any], steps_config: List[Dict[str, Any]],
                   enabled: bool = True, max_leads: int = 50) -> int:
    """Crea una nueva campaña."""
    with conn.cursor() as cur:
        cur.execute("""
            INSERT INTO sales_campaigns
            (name, description, campaign_type, trigger_criteria, steps_config, enabled, max_leads_per_run)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            name,
            description,
            campaign_type,
            json.dumps(trigger_criteria),
            json.dumps(steps_config),
            enabled,
            max_leads
        ))
        campaign_id = cur.fetchone()[0]
        conn.commit()
        return campaign_id


def toggle_campaign(conn, campaign_id: int, enabled: bool):
    """Activa o desactiva una campaña."""
    with conn.cursor() as cur:
        cur.execute("""
            UPDATE sales_campaigns
            SET enabled = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (enabled, campaign_id))
        conn.commit()


def delete_campaign(conn, campaign_id: int):
    """Elimina una campaña."""
    with conn.cursor() as cur:
        cur.execute("DELETE FROM sales_campaigns WHERE id = %s", (campaign_id,))
        conn.commit()


def show_campaign(conn, campaign_id: int) -> Dict[str, Any]:
    """Muestra detalles de una campaña."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                id,
                name,
                description,
                campaign_type,
                enabled,
                max_leads_per_run,
                trigger_criteria,
                steps_config,
                created_at,
                updated_at
            FROM sales_campaigns
            WHERE id = %s
        """, (campaign_id,))
        return cur.fetchone()


def main():
    parser = argparse.ArgumentParser(
        description="Gestiona campañas de ventas automatizadas"
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Connection string de PostgreSQL (ej: postgresql://user:pass@host/db)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Comando a ejecutar")
    
    # Listar campañas
    list_parser = subparsers.add_parser("list", help="Lista todas las campañas")
    
    # Crear campaña
    create_parser = subparsers.add_parser("create", help="Crea una nueva campaña")
    create_parser.add_argument("--name", required=True, help="Nombre de la campaña")
    create_parser.add_argument("--description", help="Descripción")
    create_parser.add_argument("--type", required=True, 
                              choices=["email_sequence", "call_campaign", "multichannel", "nurturing"],
                              help="Tipo de campaña")
    create_parser.add_argument("--trigger-file", required=True,
                              help="Archivo JSON con trigger_criteria")
    create_parser.add_argument("--steps-file", required=True,
                              help="Archivo JSON con steps_config")
    create_parser.add_argument("--enabled", action="store_true", default=True,
                              help="Activar campaña al crear")
    create_parser.add_argument("--max-leads", type=int, default=50,
                              help="Máximo de leads por ejecución")
    
    # Mostrar campaña
    show_parser = subparsers.add_parser("show", help="Muestra detalles de una campaña")
    show_parser.add_argument("--id", type=int, required=True, help="ID de la campaña")
    
    # Activar/Desactivar
    toggle_parser = subparsers.add_parser("toggle", help="Activa o desactiva una campaña")
    toggle_parser.add_argument("--id", type=int, required=True, help="ID de la campaña")
    toggle_parser.add_argument("--enabled", action="store_true", help="Activar")
    toggle_parser.add_argument("--disabled", action="store_true", help="Desactivar")
    
    # Eliminar
    delete_parser = subparsers.add_parser("delete", help="Elimina una campaña")
    delete_parser.add_argument("--id", type=int, required=True, help="ID de la campaña")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    conn = get_db_connection(args.db)
    
    try:
        if args.command == "list":
            campaigns = list_campaigns(conn)
            print(f"\n{'ID':<5} {'Nombre':<30} {'Tipo':<20} {'Estado':<10}")
            print("-" * 70)
            for camp in campaigns:
                status = "✅ Activa" if camp["enabled"] else "❌ Inactiva"
                print(f"{camp['id']:<5} {camp['name']:<30} {camp['campaign_type']:<20} {status:<10}")
            print(f"\nTotal: {len(campaigns)} campañas")
        
        elif args.command == "create":
            with open(args.trigger_file, 'r') as f:
                trigger_criteria = json.load(f)
            with open(args.steps_file, 'r') as f:
                steps_config = json.load(f)
            
            campaign_id = create_campaign(
                conn,
                args.name,
                args.description or "",
                args.type,
                trigger_criteria,
                steps_config,
                args.enabled,
                args.max_leads
            )
            print(f"✅ Campaña creada con ID: {campaign_id}")
        
        elif args.command == "show":
            campaign = show_campaign(conn, args.id)
            if not campaign:
                print(f"❌ Campaña {args.id} no encontrada", file=sys.stderr)
                sys.exit(1)
            
            print(f"\n📋 Campaña: {campaign['name']}")
            print(f"ID: {campaign['id']}")
            print(f"Tipo: {campaign['campaign_type']}")
            print(f"Estado: {'✅ Activa' if campaign['enabled'] else '❌ Inactiva'}")
            print(f"Max leads por run: {campaign['max_leads_per_run']}")
            print(f"\nCriterios de activación:")
            print(json.dumps(campaign['trigger_criteria'], indent=2))
            print(f"\nPasos de la campaña:")
            print(json.dumps(campaign['steps_config'], indent=2))
        
        elif args.command == "toggle":
            if not (args.enabled or args.disabled):
                print("❌ Debes especificar --enabled o --disabled", file=sys.stderr)
                sys.exit(1)
            
            enabled = args.enabled
            toggle_campaign(conn, args.id, enabled)
            status = "activada" if enabled else "desactivada"
            print(f"✅ Campaña {args.id} {status}")
        
        elif args.command == "delete":
            confirm = input(f"¿Seguro que quieres eliminar la campaña {args.id}? (yes/no): ")
            if confirm.lower() == "yes":
                delete_campaign(conn, args.id)
                print(f"✅ Campaña {args.id} eliminada")
            else:
                print("Operación cancelada")
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()

