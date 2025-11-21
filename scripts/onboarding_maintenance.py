#!/usr/bin/env python3
"""
Scripts de mantenimiento para el sistema de onboarding.
Incluye limpieza de datos antiguos, verificación de integridad, etc.
"""

import argparse
import logging
import sys
from datetime import datetime, timedelta

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def cleanup_old_data(db_config: dict, retention_days: int = 365):
    """Limpiar datos de onboarding más antiguos que retention_days."""
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['url'].replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Limpiar acciones antiguas
        cursor.execute("""
            DELETE FROM onboarding_actions 
            WHERE executed_at < %s
        """, (cutoff_date,))
        actions_deleted = cursor.rowcount
        
        # Limpiar datos de onboarding completados antiguos (mantener solo resumen)
        cursor.execute("""
            DELETE FROM employee_onboarding 
            WHERE status = 'completed' 
              AND updated_at < %s
        """, (cutoff_date,))
        onboarding_deleted = cursor.rowcount
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Cleanup completed: {actions_deleted} actions, {onboarding_deleted} onboardings deleted")
        return {"actions_deleted": actions_deleted, "onboardings_deleted": onboarding_deleted}
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return {"error": str(e)}


def verify_data_integrity(db_config: dict):
    """Verificar integridad de datos en las tablas."""
    issues = []
    
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['url'].replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        
        # Verificar referencias huérfanas
        cursor.execute("""
            SELECT oa.employee_email 
            FROM onboarding_actions oa
            LEFT JOIN employee_onboarding eo ON oa.employee_email = eo.employee_email
            WHERE eo.employee_email IS NULL
            LIMIT 10
        """)
        orphan_actions = cursor.fetchall()
        if orphan_actions:
            issues.append(f"Found {len(orphan_actions)} orphan action records")
        
        cursor.execute("""
            SELECT oac.employee_email 
            FROM onboarding_accounts oac
            LEFT JOIN employee_onboarding eo ON oac.employee_email = eo.employee_email
            WHERE eo.employee_email IS NULL
            LIMIT 10
        """)
        orphan_accounts = cursor.fetchall()
        if orphan_accounts:
            issues.append(f"Found {len(orphan_accounts)} orphan account records")
        
        # Verificar duplicados
        cursor.execute("""
            SELECT employee_email, COUNT(*) 
            FROM employee_onboarding 
            GROUP BY employee_email 
            HAVING COUNT(*) > 1
        """)
        duplicates = cursor.fetchall()
        if duplicates:
            issues.append(f"Found {len(duplicates)} duplicate employee records")
        
        cursor.close()
        conn.close()
        
        if issues:
            logger.warning(f"Data integrity issues found: {', '.join(issues)}")
        else:
            logger.info("Data integrity check passed")
        
        return {"issues": issues, "status": "ok" if not issues else "issues_found"}
        
    except Exception as e:
        logger.error(f"Integrity check failed: {e}")
        return {"error": str(e)}


def archive_completed_onboardings(db_config: dict, archive_days: int = 90):
    """Archivar onboarding completados a una tabla de historial."""
    try:
        import psycopg
        conn = psycopg.connect(
            f"postgresql://{db_config['user']}:{db_config['password']}@{db_config['url'].replace('jdbc:postgresql://', '').replace('jdbc:', '')}"
        )
        cursor = conn.cursor()
        
        # Crear tabla de archivo si no existe
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS employee_onboarding_archive (
                LIKE employee_onboarding INCLUDING ALL
            );
        """)
        
        cutoff_date = datetime.now() - timedelta(days=archive_days)
        
        # Mover registros completados antiguos a archivo
        cursor.execute("""
            INSERT INTO employee_onboarding_archive 
            SELECT * FROM employee_onboarding 
            WHERE status = 'completed' 
              AND updated_at < %s
        """, (cutoff_date,))
        
        archived_count = cursor.rowcount
        
        if archived_count > 0:
            # Eliminar de tabla principal
            cursor.execute("""
                DELETE FROM employee_onboarding 
                WHERE id IN (
                    SELECT id FROM employee_onboarding_archive 
                    WHERE updated_at < %s
                )
            """, (cutoff_date,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info(f"Archived {archived_count} completed onboardings")
        return {"archived": archived_count}
        
    except Exception as e:
        logger.error(f"Archive failed: {e}")
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Scripts de mantenimiento para onboarding")
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Cleanup
    cleanup_parser = subparsers.add_parser('cleanup', help='Limpiar datos antiguos')
    cleanup_parser.add_argument('--db-url', required=True)
    cleanup_parser.add_argument('--db-user', required=True)
    cleanup_parser.add_argument('--db-password', required=True)
    cleanup_parser.add_argument('--retention-days', type=int, default=365, help='Días de retención')
    
    # Integrity
    integrity_parser = subparsers.add_parser('integrity', help='Verificar integridad de datos')
    integrity_parser.add_argument('--db-url', required=True)
    integrity_parser.add_argument('--db-user', required=True)
    integrity_parser.add_argument('--db-password', required=True)
    
    # Archive
    archive_parser = subparsers.add_parser('archive', help='Archivar onboarding completados')
    archive_parser.add_argument('--db-url', required=True)
    archive_parser.add_argument('--db-user', required=True)
    archive_parser.add_argument('--db-password', required=True)
    archive_parser.add_argument('--archive-days', type=int, default=90, help='Días antes de archivar')
    
    args = parser.parse_args()
    
    db_config = {
        'url': args.db_url,
        'user': args.db_user,
        'password': args.db_password
    }
    
    if args.command == 'cleanup':
        result = cleanup_old_data(db_config, args.retention_days)
        print(f"Cleanup result: {result}")
        return 0 if 'error' not in result else 1
    
    elif args.command == 'integrity':
        result = verify_data_integrity(db_config)
        print(f"Integrity check: {result}")
        return 0 if result.get('status') == 'ok' else 1
    
    elif args.command == 'archive':
        result = archive_completed_onboardings(db_config, args.archive_days)
        print(f"Archive result: {result}")
        return 0 if 'error' not in result else 1
    
    else:
        parser.print_help()
        return 1


if __name__ == '__main__':
    sys.exit(main())

