#!/usr/bin/env python3
"""
Health check del sistema de automatización de ventas.
Verifica que el sistema esté funcionando correctamente.
"""

import argparse
import sys
import json
from datetime import datetime, timedelta
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


def check_system_health(conn) -> dict:
    """Verifica salud del sistema."""
    health = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "checks": {}
    }
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check 1: Leads siendo procesados
        cur.execute("""
            SELECT COUNT(*) FROM sales_pipeline
            WHERE stage NOT IN ('closed_won', 'closed_lost')
            AND qualified_at >= NOW() - INTERVAL '7 days'
        """)
        recent_leads = cur.fetchone()[0]
        health["checks"]["recent_leads"] = {
            "count": recent_leads,
            "status": "ok" if recent_leads > 0 else "warning",
            "message": f"{recent_leads} leads calificados en últimos 7 días"
        }
        
        # Check 2: Tareas pendientes
        cur.execute("""
            SELECT COUNT(*) FROM sales_followup_tasks
            WHERE status = 'pending'
            AND due_date <= NOW()
        """)
        overdue_tasks = cur.fetchone()[0]
        health["checks"]["overdue_tasks"] = {
            "count": overdue_tasks,
            "status": "ok" if overdue_tasks < 10 else "warning" if overdue_tasks < 50 else "critical",
            "message": f"{overdue_tasks} tareas vencidas"
        }
        
        # Check 3: Leads sin asignar
        cur.execute("""
            SELECT COUNT(*) FROM sales_pipeline
            WHERE assigned_to IS NULL
            AND stage NOT IN ('closed_won', 'closed_lost')
            AND qualified_at >= NOW() - INTERVAL '3 days'
        """)
        unassigned = cur.fetchone()[0]
        health["checks"]["unassigned_leads"] = {
            "count": unassigned,
            "status": "ok" if unassigned < 5 else "warning",
            "message": f"{unassigned} leads sin asignar (últimos 3 días)"
        }
        
        # Check 4: Campañas activas
        cur.execute("""
            SELECT COUNT(*) FROM sales_campaigns WHERE enabled = true
        """)
        active_campaigns = cur.fetchone()[0]
        health["checks"]["active_campaigns"] = {
            "count": active_campaigns,
            "status": "ok" if active_campaigns > 0 else "warning",
            "message": f"{active_campaigns} campañas activas"
        }
        
        # Check 5: Ejecuciones de campaña
        cur.execute("""
            SELECT COUNT(*) FROM sales_campaign_executions
            WHERE status = 'active'
            AND next_action_at <= NOW()
        """)
        pending_actions = cur.fetchone()[0]
        health["checks"]["pending_campaign_actions"] = {
            "count": pending_actions,
            "status": "ok" if pending_actions < 20 else "warning",
            "message": f"{pending_actions} acciones de campaña pendientes"
        }
        
        # Check 6: Scoring actualizado
        cur.execute("""
            SELECT COUNT(*) FROM lead_score_history
            WHERE calculated_at >= NOW() - INTERVAL '24 hours'
        """)
        recent_scores = cur.fetchone()[0]
        health["checks"]["scoring_activity"] = {
            "count": recent_scores,
            "status": "ok" if recent_scores > 0 else "warning",
            "message": f"{recent_scores} scores calculados en últimas 24h"
        }
        
        # Check 7: Pipeline value
        cur.execute("""
            SELECT SUM(estimated_value * probability_pct / 100.0) AS weighted_pipeline
            FROM sales_pipeline
            WHERE stage NOT IN ('closed_won', 'closed_lost')
            AND estimated_value IS NOT NULL
        """)
        pipeline_value = cur.fetchone()[0] or 0
        health["checks"]["pipeline_value"] = {
            "value": float(pipeline_value),
            "status": "ok",
            "message": f"Pipeline ponderado: ${pipeline_value:,.2f}"
        }
        
        # Determinar estado general
        critical_checks = [c for c in health["checks"].values() if c["status"] == "critical"]
        warning_checks = [c for c in health["checks"].values() if c["status"] == "warning"]
        
        if critical_checks:
            health["status"] = "critical"
        elif warning_checks:
            health["status"] = "degraded"
        else:
            health["status"] = "healthy"
    
    return health


def main():
    parser = argparse.ArgumentParser(
        description="Health check del sistema de automatización de ventas"
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Connection string de PostgreSQL"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en formato JSON"
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Usar código de salida basado en estado"
    )
    
    args = parser.parse_args()
    
    conn = get_db_connection(args.db)
    
    try:
        health = check_system_health(conn)
        
        if args.json:
            print(json.dumps(health, indent=2))
        else:
            status_emoji = {
                "healthy": "✅",
                "degraded": "⚠️",
                "critical": "❌"
            }
            
            print(f"\n{status_emoji.get(health['status'], '❓')} Sistema de Ventas - {health['status'].upper()}")
            print("=" * 60)
            print(f"Timestamp: {health['timestamp']}\n")
            
            for check_name, check_data in health["checks"].items():
                status_icon = {
                    "ok": "✅",
                    "warning": "⚠️",
                    "critical": "❌"
                }.get(check_data["status"], "❓")
                
                print(f"{status_icon} {check_name.replace('_', ' ').title()}")
                print(f"   {check_data['message']}")
            
            print("\n" + "=" * 60)
        
        if args.exit_code:
            exit_code = {
                "healthy": 0,
                "degraded": 1,
                "critical": 2
            }.get(health["status"], 3)
            sys.exit(exit_code)
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()


