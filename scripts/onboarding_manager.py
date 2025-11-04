#!/usr/bin/env python3
"""
CLI para gestión de onboarding de empleados.
Permite consultar estado, crear onboarding manual, ver métricas, etc.
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


def query_database(db_url: str, db_user: str, db_password: str, query: str) -> list:
    """Ejecutar query en base de datos PostgreSQL."""
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_user}:{db_password}@{db_url.replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Database query failed: {e}")
        return []


def get_onboarding_status(db_config: Dict[str, str], employee_email: str) -> Optional[Dict[str, Any]]:
    """Obtener estado de onboarding de un empleado."""
    query = """
        SELECT 
            eo.*,
            COUNT(DISTINCT oa.id) as actions_count,
            COUNT(DISTINCT oac.id) as accounts_count,
            COUNT(DISTINCT oft.id) as followup_tasks_count
        FROM employee_onboarding eo
        LEFT JOIN onboarding_actions oa ON eo.employee_email = oa.employee_email
        LEFT JOIN onboarding_accounts oac ON eo.employee_email = oac.employee_email
        LEFT JOIN onboarding_follow_up_tasks oft ON eo.employee_email = oft.employee_email
        WHERE eo.employee_email = %s
        GROUP BY eo.id
        ORDER BY eo.created_at DESC
        LIMIT 1;
    """
    
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['url'].replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        cursor.execute(query, (employee_email,))
        columns = [desc[0] for desc in cursor.description]
        row = cursor.fetchone()
        if row:
            result = dict(zip(columns, row))
            cursor.close()
            conn.close()
            return result
        return None
    except Exception as e:
        logger.error(f"Failed to get onboarding status: {e}")
        return None


def list_recent_onboardings(db_config: Dict[str, str], limit: int = 10) -> list:
    """Listar onboarding recientes."""
    query = """
        SELECT 
            employee_email,
            full_name,
            department,
            position,
            start_date,
            status,
            created_at,
            updated_at
        FROM employee_onboarding
        ORDER BY created_at DESC
        LIMIT %s;
    """
    
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['url'].replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        cursor.execute(query, (limit,))
        columns = [desc[0] for desc in cursor.description]
        results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        logger.error(f"Failed to list onboardings: {e}")
        return []


def get_onboarding_stats(db_config: Dict[str, str]) -> Dict[str, Any]:
    """Obtener estadísticas de onboarding."""
    queries = {
        'total': "SELECT COUNT(*) as count FROM employee_onboarding;",
        'by_status': """
            SELECT status, COUNT(*) as count 
            FROM employee_onboarding 
            GROUP BY status;
        """,
        'by_department': """
            SELECT department, COUNT(*) as count 
            FROM employee_onboarding 
            GROUP BY department 
            ORDER BY count DESC;
        """,
        'success_rate': """
            SELECT 
                COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM employee_onboarding;
        """,
        'recent_week': """
            SELECT COUNT(*) as count 
            FROM employee_onboarding 
            WHERE created_at >= NOW() - INTERVAL '7 days';
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
            if key in ['by_status', 'by_department']:
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


def trigger_onboarding(kestra_url: str, kestra_token: Optional[str], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Disparar flujo de onboarding en Kestra."""
    url = f"{kestra_url}/api/v1/executions/trigger/workflows.employee_onboarding"
    headers = {"Content-Type": "application/json"}
    if kestra_token:
        headers["Authorization"] = f"Bearer {kestra_token}"
    
    try:
        response = requests.post(url, headers=headers, json={"inputs": payload}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to trigger onboarding: {e}")
        return {"error": str(e)}


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI para gestión de onboarding de empleados")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: status
    status_parser = subparsers.add_parser('status', help='Ver estado de onboarding de un empleado')
    status_parser.add_argument('--email', required=True, help='Email del empleado')
    status_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    status_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    status_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: list
    list_parser = subparsers.add_parser('list', help='Listar onboarding recientes')
    list_parser.add_argument('--limit', type=int, default=10, help='Número de resultados')
    list_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    list_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    list_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: stats
    stats_parser = subparsers.add_parser('stats', help='Ver estadísticas de onboarding')
    stats_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    stats_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    stats_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: trigger
    trigger_parser = subparsers.add_parser('trigger', help='Disparar onboarding manualmente')
    trigger_parser.add_argument('--kestra-url', required=True, help='URL de Kestra')
    trigger_parser.add_argument('--kestra-token', help='Token de autenticación de Kestra')
    trigger_parser.add_argument('--payload-file', required=True, help='Archivo JSON con payload')
    
    args = parser.parse_args()
    
    if args.command == 'status':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        status = get_onboarding_status(db_config, args.email)
        if status:
            print(json.dumps(status, indent=2, default=str))
            return 0
        else:
            print(f"No se encontró onboarding para {args.email}")
            return 1
    
    elif args.command == 'list':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        results = list_recent_onboardings(db_config, args.limit)
        print(json.dumps(results, indent=2, default=str))
        return 0
    
    elif args.command == 'stats':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        stats = get_onboarding_stats(db_config)
        print(json.dumps(stats, indent=2, default=str))
        return 0
    
    elif args.command == 'trigger':
        with open(args.payload_file, 'r') as f:
            payload = json.load(f)
        result = trigger_onboarding(args.kestra_url, args.kestra_token, payload)
        print(json.dumps(result, indent=2))
        return 0 if 'error' not in result else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())

