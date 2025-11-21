#!/usr/bin/env python3
"""
CLI para gestión del sistema de aprobaciones.
Permite consultar estado, crear solicitudes, ver métricas, etc.
"""

import argparse
import json
import logging
import sys
from datetime import datetime
from typing import Dict, Any, Optional

import requests

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def query_database(db_url: str, db_user: str, db_password: str, query: str, params: tuple = ()) -> list:
    """Ejecutar query en base de datos PostgreSQL."""
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_user}:{db_password}@{db_url.replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        cursor.execute(query, params)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return []


def get_request_status(db_config: Dict[str, str], request_id: str) -> Optional[Dict[str, Any]]:
    """Obtener estado de una solicitud de aprobación."""
    query = """
        SELECT 
            ar.*,
            COUNT(ac.id) FILTER (WHERE ac.status = 'pending') as pending_approvals,
            COUNT(ac.id) FILTER (WHERE ac.status = 'approved') as approved_count,
            COUNT(ac.id) FILTER (WHERE ac.status = 'rejected') as rejected_count
        FROM approval_requests ar
        LEFT JOIN approval_chains ac ON ar.id = ac.request_id
        WHERE ar.id = %s
        GROUP BY ar.id;
    """
    
    results = query_database(db_config['url'], db_config['user'], db_config['password'], query, (request_id,))
    return results[0] if results else None


def list_pending_approvals(db_config: Dict[str, str], approver_email: Optional[str] = None, limit: int = 20) -> list:
    """Listar aprobaciones pendientes."""
    if approver_email:
        query = """
            SELECT 
                ar.id,
                ar.title,
                ar.request_type,
                ar.requester_email,
                ar.submitted_at,
                ar.priority,
                ac.timeout_date,
                EXTRACT(EPOCH FROM (ac.timeout_date - NOW())) / 3600 as hours_until_timeout
            FROM approval_chains ac
            JOIN approval_requests ar ON ac.request_id = ar.id
            WHERE ac.status = 'pending'
              AND ac.approver_email = %s
            ORDER BY ar.priority DESC, ac.timeout_date ASC NULLS LAST
            LIMIT %s;
        """
        results = query_database(db_config['url'], db_config['user'], db_config['password'], query, (approver_email, limit))
    else:
        query = """
            SELECT 
                ar.id,
                ar.title,
                ar.request_type,
                ar.requester_email,
                ar.submitted_at,
                ar.priority,
                COUNT(ac.id) FILTER (WHERE ac.status = 'pending') as pending_approvals
            FROM approval_requests ar
            LEFT JOIN approval_chains ac ON ar.id = ac.request_id
            WHERE ar.status = 'pending'
            GROUP BY ar.id, ar.title, ar.request_type, ar.requester_email, ar.submitted_at, ar.priority
            ORDER BY ar.priority DESC, ar.submitted_at ASC
            LIMIT %s;
        """
        results = query_database(db_config['url'], db_config['user'], db_config['password'], query, (limit,))
    
    return results


def get_approval_stats(db_config: Dict[str, str]) -> Dict[str, Any]:
    """Obtener estadísticas de aprobaciones."""
    queries = {
        'total': "SELECT COUNT(*) as count FROM approval_requests;",
        'by_status': """
            SELECT status, COUNT(*) as count 
            FROM approval_requests 
            GROUP BY status;
        """,
        'by_type': """
            SELECT request_type, COUNT(*) as count 
            FROM approval_requests 
            GROUP BY request_type 
            ORDER BY count DESC;
        """,
        'pending_count': """
            SELECT COUNT(*) as count 
            FROM approval_requests 
            WHERE status = 'pending';
        """,
        'avg_completion_time': """
            SELECT 
                AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) as avg_hours
            FROM approval_requests
            WHERE completed_at IS NOT NULL 
              AND submitted_at IS NOT NULL
              AND completed_at >= NOW() - INTERVAL '30 days';
        """,
        'approval_rate': """
            SELECT 
                COUNT(*) FILTER (WHERE status = 'approved') * 100.0 / COUNT(*) as approval_rate
            FROM approval_requests
            WHERE status IN ('approved', 'rejected', 'auto_approved');
        """
    }
    
    stats = {}
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['url'].replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        
        for key, query in queries.items():
            cursor.execute(query)
            if key in ['by_status', 'by_type']:
                stats[key] = [dict(zip([desc[0] for desc in cursor.description], row)) for row in cursor.fetchall()]
            else:
                row = cursor.fetchone()
                if row:
                    stats[key] = dict(zip([desc[0] for desc in cursor.description], row))
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
    
    return stats


def create_approval_request(api_url: str, api_token: Optional[str], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Crear solicitud de aprobación vía API."""
    url = f"{api_url}/approvals/requests"
    headers = {"Content-Type": "application/json"}
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to create approval request: {e}")
        return {"error": str(e)}


def approve_request(api_url: str, api_token: Optional[str], request_id: str, approver_email: str, comments: Optional[str] = None) -> Dict[str, Any]:
    """Aprobar solicitud vía API."""
    url = f"{api_url}/approvals/requests/{request_id}/approve"
    headers = {"Content-Type": "application/json"}
    if api_token:
        headers["Authorization"] = f"Bearer {api_token}"
    
    payload = {
        "approver_email": approver_email,
        "comments": comments
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to approve request: {e}")
        return {"error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI para gestión de aprobaciones")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: status
    status_parser = subparsers.add_parser('status', help='Ver estado de una solicitud')
    status_parser.add_argument('--request-id', required=True, help='ID de la solicitud')
    status_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    status_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    status_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: list-pending
    list_parser = subparsers.add_parser('list-pending', help='Listar aprobaciones pendientes')
    list_parser.add_argument('--approver-email', help='Filtrar por aprobador')
    list_parser.add_argument('--limit', type=int, default=20, help='Número de resultados')
    list_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    list_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    list_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: stats
    stats_parser = subparsers.add_parser('stats', help='Ver estadísticas de aprobaciones')
    stats_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    stats_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    stats_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: create
    create_parser = subparsers.add_parser('create', help='Crear solicitud de aprobación')
    create_parser.add_argument('--api-url', required=True, help='URL de la API')
    create_parser.add_argument('--api-token', help='Token de autenticación')
    create_parser.add_argument('--payload-file', required=True, help='Archivo JSON con payload')
    
    # Comando: approve
    approve_parser = subparsers.add_parser('approve', help='Aprobar solicitud')
    approve_parser.add_argument('--api-url', required=True, help='URL de la API')
    approve_parser.add_argument('--api-token', help='Token de autenticación')
    approve_parser.add_argument('--request-id', required=True, help='ID de la solicitud')
    approve_parser.add_argument('--approver-email', required=True, help='Email del aprobador')
    approve_parser.add_argument('--comments', help='Comentarios de aprobación')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        status = get_request_status(db_config, args.request_id)
        if status:
            print(json.dumps(status, indent=2, default=str))
            return 0
        else:
            print(f"No se encontró solicitud con ID {args.request_id}")
            return 1
    
    elif args.command == 'list-pending':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        results = list_pending_approvals(db_config, args.approver_email, args.limit)
        print(json.dumps(results, indent=2, default=str))
        return 0
    
    elif args.command == 'stats':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        stats = get_approval_stats(db_config)
        print(json.dumps(stats, indent=2, default=str))
        return 0
    
    elif args.command == 'create':
        with open(args.payload_file, 'r') as f:
            payload = json.load(f)
        result = create_approval_request(args.api_url, args.api_token, payload)
        print(json.dumps(result, indent=2))
        return 0 if 'error' not in result else 1
    
    elif args.command == 'approve':
        result = approve_request(
            args.api_url,
            args.api_token,
            args.request_id,
            args.approver_email,
            args.comments
        )
        print(json.dumps(result, indent=2))
        return 0 if 'error' not in result else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())
