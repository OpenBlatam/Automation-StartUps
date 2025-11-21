#!/usr/bin/env python3
"""
Script de validación del sistema de automatización de ventas.
Verifica que todos los componentes estén correctamente configurados.
"""

import argparse
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any


def get_db_connection(connection_string: str):
    """Obtiene conexión a la base de datos."""
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        print(f"❌ Error conectando a la base de datos: {e}", file=sys.stderr)
        sys.exit(1)


def check_tables(conn) -> Dict[str, bool]:
    """Verifica que todas las tablas existan."""
    required_tables = [
        'lead_score_history',
        'sales_pipeline',
        'sales_followup_tasks',
        'sales_campaigns',
        'sales_campaign_executions',
        'sales_campaign_events'
    ]
    
    results = {}
    
    with conn.cursor() as cur:
        for table in required_tables:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.tables 
                WHERE table_name = %s
            """, (table,))
            exists = cur.fetchone()[0] > 0
            results[table] = exists
    
    return results


def check_views(conn) -> Dict[str, bool]:
    """Verifica que las vistas existan."""
    required_views = [
        'v_sales_dashboard',
        'v_leads_requires_attention',
        'v_sales_rep_performance',
        'v_sales_forecast',
        'v_conversion_funnel'
    ]
    
    results = {}
    
    with conn.cursor() as cur:
        for view in required_views:
            cur.execute("""
                SELECT COUNT(*) FROM information_schema.views 
                WHERE table_name = %s
            """, (view,))
            exists = cur.fetchone()[0] > 0
            results[view] = exists
    
    return results


def check_functions(conn) -> Dict[str, bool]:
    """Verifica que las funciones existan."""
    required_functions = [
        'calculate_lead_score',
        'auto_assign_sales_rep',
        'get_top_opportunities',
        'get_leads_at_risk',
        'update_rep_stats'
    ]
    
    results = {}
    
    with conn.cursor() as cur:
        for func in required_functions:
            cur.execute("""
                SELECT COUNT(*) FROM pg_proc 
                WHERE proname = %s
            """, (func,))
            exists = cur.fetchone()[0] > 0
            results[func] = exists
    
    return results


def check_indexes(conn) -> Dict[str, bool]:
    """Verifica índices importantes."""
    important_indexes = [
        'idx_pipeline_stage_priority_score',
        'idx_pipeline_next_followup',
        'idx_tasks_overdue',
        'idx_pipeline_metadata_gin'
    ]
    
    results = {}
    
    with conn.cursor() as cur:
        for idx in important_indexes:
            cur.execute("""
                SELECT COUNT(*) FROM pg_indexes 
                WHERE indexname = %s
            """, (idx,))
            exists = cur.fetchone()[0] > 0
            results[idx] = exists
    
    return results


def check_data_integrity(conn) -> Dict[str, Any]:
    """Verifica integridad de datos."""
    issues = []
    
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Leads sin email
        cur.execute("""
            SELECT COUNT(*) FROM sales_pipeline WHERE email IS NULL OR email = ''
        """)
        no_email = cur.fetchone()[0]
        if no_email > 0:
            issues.append(f"⚠️ {no_email} leads en pipeline sin email")
        
        # Leads calificados sin asignar
        cur.execute("""
            SELECT COUNT(*) FROM sales_pipeline 
            WHERE assigned_to IS NULL 
            AND stage NOT IN ('closed_won', 'closed_lost')
            AND qualified_at >= NOW() - INTERVAL '7 days'
        """)
        unassigned = cur.fetchone()[0]
        if unassigned > 0:
            issues.append(f"⚠️ {unassigned} leads calificados recientes sin asignar")
        
        # Tareas sin pipeline asociado (orphans)
        cur.execute("""
            SELECT COUNT(*) FROM sales_followup_tasks t
            LEFT JOIN sales_pipeline p ON t.pipeline_id = p.id
            WHERE p.id IS NULL
        """)
        orphans = cur.fetchone()[0]
        if orphans > 0:
            issues.append(f"❌ {orphans} tareas huérfanas (sin pipeline)")
        
        # Campañas sin pasos
        cur.execute("""
            SELECT COUNT(*) FROM sales_campaigns 
            WHERE enabled = true 
            AND (steps_config IS NULL OR jsonb_array_length(steps_config) = 0)
        """)
        no_steps = cur.fetchone()[0]
        if no_steps > 0:
            issues.append(f"⚠️ {no_steps} campañas activas sin pasos configurados")
        
        # Ejecuciones de campaña sin eventos
        cur.execute("""
            SELECT COUNT(*) FROM sales_campaign_executions ce
            LEFT JOIN sales_campaign_events e ON ce.id = e.execution_id
            WHERE ce.status = 'active'
            AND e.id IS NULL
            AND ce.current_step > 1
        """)
        no_events = cur.fetchone()[0]
        if no_events > 0:
            issues.append(f"⚠️ {no_events} ejecuciones de campaña sin eventos")
    
    return {
        "issues": issues,
        "total_issues": len(issues)
    }


def check_performance(conn) -> Dict[str, Any]:
    """Verifica métricas de performance."""
    metrics = {}
    
    with conn.cursor() as cur:
        # Tamaño de tablas
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
            FROM pg_tables
            WHERE tablename LIKE 'sales_%' OR tablename LIKE 'lead_%'
            ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
            LIMIT 10
        """)
        metrics["table_sizes"] = cur.fetchall()
        
        # Índices no usados (últimos 7 días)
        cur.execute("""
            SELECT 
                indexrelname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            WHERE schemaname = 'public'
            AND (idx_scan = 0 OR idx_tup_read = 0)
            AND indexrelname LIKE '%sales%'
            LIMIT 10
        """)
        metrics["unused_indexes"] = cur.fetchall()
        
        # Estadísticas de tablas
        cur.execute("""
            SELECT 
                relname,
                n_live_tup,
                n_dead_tup,
                last_vacuum,
                last_autovacuum
            FROM pg_stat_user_tables
            WHERE relname LIKE '%sales%' OR relname LIKE '%lead%'
            ORDER BY n_live_tup DESC
        """)
        metrics["table_stats"] = cur.fetchall()
    
    return metrics


def main():
    parser = argparse.ArgumentParser(
        description="Valida el sistema de automatización de ventas"
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Connection string de PostgreSQL"
    )
    parser.add_argument(
        "--check-data",
        action="store_true",
        help="Verificar integridad de datos"
    )
    parser.add_argument(
        "--check-performance",
        action="store_true",
        help="Verificar métricas de performance"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Ejecutar todas las verificaciones"
    )
    
    args = parser.parse_args()
    
    conn = get_db_connection(args.db)
    
    try:
        print("🔍 Validando Sistema de Ventas\n")
        print("=" * 60)
        
        # Verificar tablas
        print("\n📋 Verificando Tablas...")
        tables = check_tables(conn)
        all_tables_ok = all(tables.values())
        for table, exists in tables.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {table}")
        
        if not all_tables_ok:
            print("\n❌ Faltan tablas. Ejecuta sales_tracking_schema.sql")
            sys.exit(1)
        
        # Verificar vistas
        print("\n👁️ Verificando Vistas...")
        views = check_views(conn)
        for view, exists in views.items():
            status = "✅" if exists else "⚠️"
            print(f"  {status} {view}")
        
        # Verificar funciones
        print("\n⚙️ Verificando Funciones...")
        functions = check_functions(conn)
        for func, exists in functions.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {func}")
        
        # Verificar índices
        print("\n📊 Verificando Índices...")
        indexes = check_indexes(conn)
        for idx, exists in indexes.items():
            status = "✅" if exists else "⚠️"
            print(f"  {status} {idx}")
        
        # Verificar integridad de datos
        if args.all or args.check_data:
            print("\n🔍 Verificando Integridad de Datos...")
            integrity = check_data_integrity(conn)
            if integrity["issues"]:
                for issue in integrity["issues"]:
                    print(f"  {issue}")
            else:
                print("  ✅ No se encontraron problemas de integridad")
        
        # Verificar performance
        if args.all or args.check_performance:
            print("\n⚡ Verificando Performance...")
            perf = check_performance(conn)
            
            print("\n  Tamaños de Tablas:")
            for row in perf["table_sizes"][:5]:
                print(f"    • {row[1]}: {row[2]}")
            
            if perf["unused_indexes"]:
                print("\n  ⚠️ Índices no usados (considerar eliminar):")
                for row in perf["unused_indexes"][:5]:
                    print(f"    • {row[0]}: {row[1]} scans")
        
        print("\n" + "=" * 60)
        print("✅ Validación completada")
        
    finally:
        conn.close()


if __name__ == "__main__":
    main()


