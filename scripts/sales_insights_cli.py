#!/usr/bin/env python3
"""
Script CLI para obtener insights y recomendaciones del sistema de ventas.
"""

import argparse
import json
import sys
from typing import Dict, Any, List
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta


def get_db_connection(connection_string: str):
    """Obtiene conexión a la base de datos."""
    try:
        conn = psycopg2.connect(connection_string)
        return conn
    except Exception as e:
        print(f"Error conectando a la base de datos: {e}", file=sys.stderr)
        sys.exit(1)


def get_pipeline_summary(conn) -> Dict[str, Any]:
    """Obtiene resumen del pipeline."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                COUNT(*) FILTER (WHERE stage = 'qualified') AS qualified,
                COUNT(*) FILTER (WHERE stage = 'contacted') AS contacted,
                COUNT(*) FILTER (WHERE stage = 'meeting_scheduled') AS meetings,
                COUNT(*) FILTER (WHERE stage = 'proposal_sent') AS proposals,
                COUNT(*) FILTER (WHERE stage = 'negotiating') AS negotiating,
                COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
                COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost,
                SUM(estimated_value) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS pipeline_value,
                AVG(probability_pct) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS avg_probability
            FROM sales_pipeline
            WHERE qualified_at >= NOW() - INTERVAL '90 days'
        """)
        return cur.fetchone()


def get_top_leads(conn, limit: int = 10) -> List[Dict[str, Any]]:
    """Obtiene top leads por valor esperado."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.stage,
                p.estimated_value,
                p.probability_pct,
                p.estimated_value * p.probability_pct / 100.0 AS expected_value,
                p.assigned_to,
                p.next_followup_at
            FROM sales_pipeline p
            WHERE p.stage NOT IN ('closed_won', 'closed_lost')
            AND p.estimated_value IS NOT NULL
            ORDER BY expected_value DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


def get_risk_leads(conn, limit: int = 10) -> List[Dict[str, Any]]:
    """Obtiene leads de alto riesgo."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.stage,
                p.estimated_value,
                p.probability_pct,
                p.last_contact_at,
                EXTRACT(EPOCH FROM (NOW() - COALESCE(p.last_contact_at, p.qualified_at)) / 86400) AS days_since_contact,
                COUNT(t.id) FILTER (WHERE t.status = 'pending' AND t.due_date <= NOW()) AS overdue_tasks,
                p.metadata->'ml_predictions'->>'risk_score' AS ml_risk_score
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            WHERE p.stage NOT IN ('closed_won', 'closed_lost')
            AND (
                p.last_contact_at IS NULL
                OR p.last_contact_at <= NOW() - INTERVAL '7 days'
                OR (p.metadata->'ml_predictions'->>'risk_score')::float > 0.7
            )
            GROUP BY p.id, p.lead_ext_id, p.email, p.first_name, p.last_name,
                     p.stage, p.estimated_value, p.probability_pct,
                     p.last_contact_at, p.qualified_at, p.metadata
            ORDER BY 
                (p.metadata->'ml_predictions'->>'risk_score')::float DESC NULLS LAST,
                days_since_contact DESC
            LIMIT %s
        """, (limit,))
        return cur.fetchall()


def get_rep_performance(conn) -> List[Dict[str, Any]]:
    """Obtiene performance de vendedores."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT 
                assigned_to,
                COUNT(*) FILTER (WHERE stage NOT IN ('closed_won', 'closed_lost')) AS active_leads,
                COUNT(*) FILTER (WHERE stage = 'closed_won') AS won,
                COUNT(*) FILTER (WHERE stage = 'closed_lost') AS lost,
                ROUND(
                    COUNT(*) FILTER (WHERE stage = 'closed_won')::NUMERIC /
                    NULLIF(COUNT(*) FILTER (WHERE stage IN ('closed_won', 'closed_lost')), 0) * 100,
                    2
                ) AS win_rate,
                SUM(estimated_value) FILTER (WHERE stage = 'closed_won') AS revenue,
                COUNT(*) FILTER (WHERE status = 'pending' AND due_date <= NOW()) AS overdue_tasks
            FROM sales_pipeline p
            LEFT JOIN sales_followup_tasks t ON p.id = t.pipeline_id
            WHERE assigned_to IS NOT NULL
            AND qualified_at >= NOW() - INTERVAL '30 days'
            GROUP BY assigned_to
            ORDER BY revenue DESC NULLS LAST
        """)
        return cur.fetchall()


def main():
    parser = argparse.ArgumentParser(
        description="Obtiene insights y recomendaciones del sistema de ventas"
    )
    parser.add_argument(
        "--db",
        required=True,
        help="Connection string de PostgreSQL"
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Mostrar resumen del pipeline"
    )
    parser.add_argument(
        "--top-leads",
        type=int,
        metavar="N",
        help="Mostrar top N leads por valor esperado"
    )
    parser.add_argument(
        "--risk-leads",
        type=int,
        metavar="N",
        help="Mostrar top N leads de alto riesgo"
    )
    parser.add_argument(
        "--rep-performance",
        action="store_true",
        help="Mostrar performance de vendedores"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Mostrar todos los insights"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Salida en formato JSON"
    )
    
    args = parser.parse_args()
    
    if not any([args.summary, args.top_leads, args.risk_leads, args.rep_performance, args.all]):
        parser.print_help()
        sys.exit(1)
    
    conn = get_db_connection(args.db)
    output = {}
    
    try:
        if args.all or args.summary:
            summary = get_pipeline_summary(conn)
            output["summary"] = dict(summary) if summary else {}
            
            if not args.json:
                print("\n📊 Pipeline Summary")
                print("=" * 50)
                print(f"Qualified: {summary.get('qualified', 0) or 0}")
                print(f"Contacted: {summary.get('contacted', 0) or 0}")
                print(f"Meetings: {summary.get('meetings', 0) or 0}")
                print(f"Proposals: {summary.get('proposals', 0) or 0}")
                print(f"Negotiating: {summary.get('negotiating', 0) or 0}")
                print(f"Won: {summary.get('won', 0) or 0}")
                print(f"Lost: {summary.get('lost', 0) or 0}")
                print(f"\nPipeline Value: ${summary.get('pipeline_value', 0) or 0:,.2f}")
                print(f"Avg Probability: {summary.get('avg_probability', 0) or 0:.1f}%")
        
        if args.all or args.top_leads:
            limit = args.top_leads or 10
            top_leads = get_top_leads(conn, limit)
            output["top_leads"] = [dict(lead) for lead in top_leads]
            
            if not args.json:
                print(f"\n💰 Top {limit} Leads por Valor Esperado")
                print("=" * 80)
                print(f"{'Email':<30} {'Stage':<20} {'Expected Value':<15} {'Assigned':<20}")
                print("-" * 80)
                for lead in top_leads:
                    expected = (lead.get('expected_value') or 0)
                    print(f"{lead.get('email', '')[:30]:<30} {lead.get('stage', ''):<20} "
                          f"${expected:,.0f}:<15} {lead.get('assigned_to', '')[:20]:<20}")
        
        if args.all or args.risk_leads:
            limit = args.risk_leads or 10
            risk_leads = get_risk_leads(conn, limit)
            output["risk_leads"] = [dict(lead) for lead in risk_leads]
            
            if not args.json:
                print(f"\n⚠️ Top {limit} Leads de Alto Riesgo")
                print("=" * 80)
                print(f"{'Email':<30} {'Stage':<15} {'Days Since Contact':<20} {'Overdue Tasks':<15}")
                print("-" * 80)
                for lead in risk_leads:
                    days = int(lead.get('days_since_contact', 0) or 0)
                    overdue = lead.get('overdue_tasks', 0) or 0
                    print(f"{lead.get('email', '')[:30]:<30} {lead.get('stage', ''):<15} "
                          f"{days} days:<20} {overdue}:<15}")
        
        if args.all or args.rep_performance:
            reps = get_rep_performance(conn)
            output["rep_performance"] = [dict(rep) for rep in reps]
            
            if not args.json:
                print(f"\n👥 Performance de Vendedores")
                print("=" * 80)
                print(f"{'Rep':<30} {'Active':<10} {'Won':<10} {'Win Rate':<12} {'Revenue':<15}")
                print("-" * 80)
                for rep in reps:
                    win_rate = rep.get('win_rate', 0) or 0
                    revenue = rep.get('revenue', 0) or 0
                    print(f"{rep.get('assigned_to', '')[:30]:<30} "
                          f"{rep.get('active_leads', 0) or 0}:<10} "
                          f"{rep.get('won', 0) or 0}:<10} "
                          f"{win_rate:.1f}%:<12} "
                          f"${revenue:,.0f}:<15}")
        
        if args.json:
            print(json.dumps(output, indent=2, default=str))
    
    finally:
        conn.close()


if __name__ == "__main__":
    main()



