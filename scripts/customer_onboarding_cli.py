#!/usr/bin/env python3
"""
CLI para gestión de onboarding de clientes.
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


def get_onboarding_status(db_config: Dict[str, str], customer_email: str) -> Optional[Dict[str, Any]]:
    """Obtener estado de onboarding de un cliente."""
    query = """
        SELECT 
            co.*,
            COUNT(DISTINCT ca.id) as accounts_count,
            COUNT(DISTINCT civ.id) as verifications_count,
            COUNT(DISTINCT coe.id) as events_count
        FROM customer_onboarding co
        LEFT JOIN customer_accounts ca ON co.customer_email = ca.customer_email
        LEFT JOIN customer_identity_verifications civ ON co.customer_email = civ.customer_email
        LEFT JOIN customer_onboarding_events coe ON co.customer_email = coe.customer_email
        WHERE co.customer_email = %s
        GROUP BY co.id
        ORDER BY co.created_at DESC
        LIMIT 1;
    """
    
    results = query_database(db_config['url'], db_config['user'], db_config['password'], query, (customer_email,))
    return results[0] if results else None


def list_recent_onboardings(db_config: Dict[str, str], limit: int = 10) -> list:
    """Listar onboarding recientes."""
    query = """
        SELECT 
            customer_email,
            first_name,
            last_name,
            company_name,
            status,
            identity_verified,
            service_plan,
            source,
            created_at,
            onboarding_completed_at
        FROM customer_onboarding
        ORDER BY created_at DESC
        LIMIT %s;
    """
    
    return query_database(db_config['url'], db_config['user'], db_config['password'], query, (limit,))


def get_onboarding_stats(db_config: Dict[str, str]) -> Dict[str, Any]:
    """Obtener estadísticas de onboarding."""
    queries = {
        'total': "SELECT COUNT(*) as count FROM customer_onboarding;",
        'by_status': """
            SELECT status, COUNT(*) as count 
            FROM customer_onboarding 
            GROUP BY status;
        """,
        'identity_verification': """
            SELECT 
                identity_verification_method,
                COUNT(*) as total,
                COUNT(CASE WHEN identity_verified = TRUE THEN 1 END) as verified
            FROM customer_onboarding
            GROUP BY identity_verification_method;
        """,
        'by_source': """
            SELECT source, COUNT(*) as count 
            FROM customer_onboarding 
            GROUP BY source 
            ORDER BY count DESC;
        """,
        'success_rate': """
            SELECT 
                COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*) as success_rate
            FROM customer_onboarding;
        """,
        'recent_week': """
            SELECT COUNT(*) as count 
            FROM customer_onboarding 
            WHERE created_at >= NOW() - INTERVAL '7 days';
        """,
        'avg_completion_time': """
            SELECT 
                AVG(EXTRACT(EPOCH FROM (onboarding_completed_at - onboarding_started_at)) / 3600) as avg_hours
            FROM customer_onboarding
            WHERE status = 'completed' AND onboarding_completed_at IS NOT NULL;
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
            if key in ['by_status', 'by_source', 'identity_verification']:
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


def get_customer_accounts(db_config: Dict[str, str], customer_email: str) -> list:
    """Obtener cuentas activadas de un cliente."""
    query = """
        SELECT 
            service_name,
            account_type,
            account_status,
            account_id,
            activated_at,
            error_message
        FROM customer_accounts
        WHERE customer_email = %s
        ORDER BY activated_at DESC;
    """
    
    return query_database(db_config['url'], db_config['user'], db_config['password'], query, (customer_email,))


def trigger_onboarding_airflow(airflow_url: str, airflow_token: Optional[str], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Disparar flujo de onboarding en Airflow."""
    url = f"{airflow_url}/api/v1/dags/customer_onboarding/dagRuns"
    headers = {"Content-Type": "application/json"}
    if airflow_token:
        headers["Authorization"] = f"Bearer {airflow_token}"
    
    try:
        response = requests.post(url, headers=headers, json={"conf": payload}, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Failed to trigger onboarding: {e}")
        return {"error": str(e)}


def trigger_onboarding_kestra(kestra_url: str, kestra_token: Optional[str], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Disparar flujo de onboarding en Kestra."""
    url = f"{kestra_url}/api/v1/executions/trigger/workflows.customer_onboarding"
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
    parser = argparse.ArgumentParser(description="CLI para gestión de onboarding de clientes")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: status
    status_parser = subparsers.add_parser('status', help='Ver estado de onboarding de un cliente')
    status_parser.add_argument('--email', required=True, help='Email del cliente')
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
    
    # Comando: accounts
    accounts_parser = subparsers.add_parser('accounts', help='Ver cuentas activadas de un cliente')
    accounts_parser.add_argument('--email', required=True, help='Email del cliente')
    accounts_parser.add_argument('--db-url', required=True, help='JDBC URL de la base de datos')
    accounts_parser.add_argument('--db-user', required=True, help='Usuario de BD')
    accounts_parser.add_argument('--db-password', required=True, help='Contraseña de BD')
    
    # Comando: trigger-airflow
    trigger_airflow_parser = subparsers.add_parser('trigger-airflow', help='Disparar onboarding en Airflow')
    trigger_airflow_parser.add_argument('--airflow-url', required=True, help='URL de Airflow')
    trigger_airflow_parser.add_argument('--airflow-token', help='Token de autenticación de Airflow')
    trigger_airflow_parser.add_argument('--payload-file', required=True, help='Archivo JSON con payload')
    
    # Comando: trigger-kestra
    trigger_kestra_parser = subparsers.add_parser('trigger-kestra', help='Disparar onboarding en Kestra')
    trigger_kestra_parser.add_argument('--kestra-url', required=True, help='URL de Kestra')
    trigger_kestra_parser.add_argument('--kestra-token', help='Token de autenticación de Kestra')
    trigger_kestra_parser.add_argument('--payload-file', required=True, help='Archivo JSON con payload')
    
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
    
    elif args.command == 'accounts':
        db_config = {
            'url': args.db_url,
            'user': args.db_user,
            'password': args.db_password
        }
        accounts = get_customer_accounts(db_config, args.email)
        print(json.dumps(accounts, indent=2, default=str))
        return 0
    
    elif args.command == 'trigger-airflow':
        with open(args.payload_file, 'r') as f:
            payload = json.load(f)
        result = trigger_onboarding_airflow(args.airflow_url, args.airflow_token, payload)
        print(json.dumps(result, indent=2))
        return 0 if 'error' not in result else 1
    
    elif args.command == 'trigger-kestra':
        with open(args.payload_file, 'r') as f:
            payload = json.load(f)
        result = trigger_onboarding_kestra(args.kestra_url, args.kestra_token, payload)
        print(json.dumps(result, indent=2))
        return 0 if 'error' not in result else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())





