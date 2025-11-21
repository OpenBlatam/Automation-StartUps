"""
Airflow DAG para análisis avanzado del sistema de aprobaciones.
Genera insights, detecta patrones y optimiza procesos.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
import json
from typing import Dict, Any, List

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

try:
    from airflow.stats import Stats
except Exception:
    Stats = None

logger = logging.getLogger(__name__)

APPROVALS_DB_CONN = os.getenv("APPROVALS_DB_CONN_ID", "approvals_db")


@dag(
    'approval_analytics',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Análisis avanzado y optimización del sistema de aprobaciones',
    schedule='0 10 * * 1',  # Cada lunes a las 10 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'analytics', 'optimization'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=30),
)
def approval_analytics() -> None:
    """Pipeline de análisis avanzado."""
    
    @task(task_id='analyze_approval_patterns', on_failure_callback=on_task_failure)
    def analyze_approval_patterns() -> Dict[str, Any]:
        """Analizar patrones de aprobación."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Patrones por día de la semana
            day_pattern_sql = """
                SELECT 
                    EXTRACT(DOW FROM submitted_at) as day_of_week,
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved,
                    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) 
                        FILTER (WHERE completed_at IS NOT NULL) as avg_hours
                FROM approval_requests
                WHERE submitted_at >= NOW() - INTERVAL '90 days'
                  AND submitted_at IS NOT NULL
                GROUP BY EXTRACT(DOW FROM submitted_at)
                ORDER BY day_of_week;
            """
            
            day_results = pg_hook.get_records(day_pattern_sql)
            
            # Patrones por hora del día
            hour_pattern_sql = """
                SELECT 
                    EXTRACT(HOUR FROM submitted_at) as hour_of_day,
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'approved') as approved
                FROM approval_requests
                WHERE submitted_at >= NOW() - INTERVAL '90 days'
                  AND submitted_at IS NOT NULL
                GROUP BY EXTRACT(HOUR FROM submitted_at)
                ORDER BY hour_of_day;
            """
            
            hour_results = pg_hook.get_records(hour_pattern_sql)
            
            # Patrones por aprobador
            approver_pattern_sql = """
                SELECT 
                    ac.approver_email,
                    COUNT(*) as total_approvals,
                    AVG(EXTRACT(EPOCH FROM (ac.approved_at - ac.created_at)) / 3600) 
                        FILTER (WHERE ac.approved_at IS NOT NULL) as avg_response_hours,
                    COUNT(*) FILTER (WHERE ac.status = 'approved') as approved_count,
                    COUNT(*) FILTER (WHERE ac.status = 'rejected') as rejected_count,
                    COUNT(*) FILTER (WHERE ac.timeout_date < NOW() AND ac.status = 'pending') as expired_count
                FROM approval_chains ac
                WHERE ac.created_at >= NOW() - INTERVAL '90 days'
                GROUP BY ac.approver_email
                HAVING COUNT(*) >= 5
                ORDER BY total_approvals DESC
                LIMIT 20;
            """
            
            approver_results = pg_hook.get_records(approver_pattern_sql)
            
            # Tiempo promedio de aprobación por tipo y prioridad
            type_priority_sql = """
                SELECT 
                    ar.request_type,
                    ar.priority,
                    COUNT(*) as total,
                    AVG(EXTRACT(EPOCH FROM (ar.completed_at - ar.submitted_at)) / 3600) 
                        FILTER (WHERE ar.completed_at IS NOT NULL) as avg_hours,
                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY 
                        EXTRACT(EPOCH FROM (ar.completed_at - ar.submitted_at)) / 3600) 
                        FILTER (WHERE ar.completed_at IS NOT NULL) as median_hours
                FROM approval_requests ar
                WHERE ar.submitted_at >= NOW() - INTERVAL '90 days'
                  AND ar.completed_at IS NOT NULL
                GROUP BY ar.request_type, ar.priority
                ORDER BY ar.request_type, ar.priority;
            """
            
            type_priority_results = pg_hook.get_records(type_priority_sql)
            
            patterns = {
                'by_day_of_week': [
                    {
                        'day': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][int(row[0])],
                        'total': row[1],
                        'approved': row[2],
                        'avg_hours': round(row[3], 2) if row[3] else 0
                    }
                    for row in day_results
                ],
                'by_hour_of_day': [
                    {
                        'hour': int(row[0]),
                        'total': row[1],
                        'approved': row[2]
                    }
                    for row in hour_results
                ],
                'by_approver': [
                    {
                        'approver_email': row[0],
                        'total_approvals': row[1],
                        'avg_response_hours': round(row[2], 2) if row[2] else 0,
                        'approved_count': row[3],
                        'rejected_count': row[4],
                        'expired_count': row[5],
                        'approval_rate': round((row[3] / row[1] * 100) if row[1] > 0 else 0, 2)
                    }
                    for row in approver_results
                ],
                'by_type_and_priority': [
                    {
                        'request_type': row[0],
                        'priority': row[1],
                        'total': row[2],
                        'avg_hours': round(row[3], 2) if row[3] else 0,
                        'median_hours': round(row[4], 2) if row[4] else 0
                    }
                    for row in type_priority_results
                ]
            }
            
            logger.info(f"Analyzed approval patterns: {json.dumps(patterns, indent=2)}")
            
            if Stats:
                try:
                    Stats.incr('approval_analytics.patterns_analyzed', 1)
                except Exception:
                    pass
            
            return patterns
            
        except Exception as e:
            logger.error("Failed to analyze approval patterns", exc_info=True)
            raise
    
    @task(task_id='detect_bottlenecks', on_failure_callback=on_task_failure)
    def detect_bottlenecks() -> Dict[str, Any]:
        """Detectar cuellos de botella en el proceso."""
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Aprobadores con más aprobaciones pendientes
            bottleneck_sql = """
                SELECT 
                    ac.approver_email,
                    COUNT(*) as pending_count,
                    AVG(EXTRACT(EPOCH FROM (NOW() - ac.created_at)) / 86400) as avg_days_pending,
                    COUNT(*) FILTER (WHERE ac.timeout_date < NOW()) as expired_count
                FROM approval_chains ac
                WHERE ac.status = 'pending'
                GROUP BY ac.approver_email
                HAVING COUNT(*) >= 5
                ORDER BY pending_count DESC
                LIMIT 10;
            """
            
            bottleneck_results = pg_hook.get_records(bottleneck_sql)
            
            # Tipos de solicitud más lentos
            slow_types_sql = """
                SELECT 
                    ar.request_type,
                    COUNT(*) as total,
                    AVG(EXTRACT(EPOCH FROM (ar.completed_at - ar.submitted_at)) / 86400) 
                        FILTER (WHERE ar.completed_at IS NOT NULL) as avg_days,
                    PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY 
                        EXTRACT(EPOCH FROM (ar.completed_at - ar.submitted_at)) / 86400) 
                        FILTER (WHERE ar.completed_at IS NOT NULL) as p95_days
                FROM approval_requests ar
                WHERE ar.submitted_at >= NOW() - INTERVAL '90 days'
                  AND ar.completed_at IS NOT NULL
                GROUP BY ar.request_type
                HAVING COUNT(*) >= 10
                ORDER BY avg_days DESC;
            """
            
            slow_types_results = pg_hook.get_records(slow_types_sql)
            
            # Cadenas de aprobación más largas
            long_chains_sql = """
                SELECT 
                    ar.request_type,
                    COUNT(DISTINCT ac.id) / COUNT(DISTINCT ar.id) as avg_chain_length,
                    MAX(chain_length) as max_chain_length
                FROM approval_requests ar
                JOIN approval_chains ac ON ar.id = ac.request_id
                JOIN (
                    SELECT request_id, COUNT(*) as chain_length
                    FROM approval_chains
                    GROUP BY request_id
                ) chain_counts ON ar.id = chain_counts.request_id
                WHERE ar.submitted_at >= NOW() - INTERVAL '90 days'
                GROUP BY ar.request_type
                ORDER BY avg_chain_length DESC;
            """
            
            long_chains_results = pg_hook.get_records(long_chains_sql)
            
            bottlenecks = {
                'approvers_with_bottleneck': [
                    {
                        'approver_email': row[0],
                        'pending_count': row[1],
                        'avg_days_pending': round(row[2], 2) if row[2] else 0,
                        'expired_count': row[3]
                    }
                    for row in bottleneck_results
                ],
                'slow_request_types': [
                    {
                        'request_type': row[0],
                        'total': row[1],
                        'avg_days': round(row[2], 2) if row[2] else 0,
                        'p95_days': round(row[3], 2) if row[3] else 0
                    }
                    for row in slow_types_results
                ],
                'long_approval_chains': [
                    {
                        'request_type': row[0],
                        'avg_chain_length': round(row[1], 2) if row[1] else 0,
                        'max_chain_length': row[2] if row[2] else 0
                    }
                    for row in long_chains_results
                ]
            }
            
            logger.info(f"Detected bottlenecks: {json.dumps(bottlenecks, indent=2)}")
            
            if Stats:
                try:
                    Stats.incr('approval_analytics.bottlenecks_detected', len(bottlenecks['approvers_with_bottleneck']))
                except Exception:
                    pass
            
            return bottlenecks
            
        except Exception as e:
            logger.error("Failed to detect bottlenecks", exc_info=True)
            raise
    
    @task(task_id='calculate_optimization_recommendations', on_failure_callback=on_task_failure)
    def calculate_optimization_recommendations(
        patterns: Dict[str, Any],
        bottlenecks: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcular recomendaciones de optimización."""
        recommendations = []
        
        # Recomendación 1: Aprobadores con bottleneck
        if bottlenecks['approvers_with_bottleneck']:
            top_bottleneck = bottlenecks['approvers_with_bottleneck'][0]
            if top_bottleneck['pending_count'] > 10:
                recommendations.append({
                    'type': 'bottleneck',
                    'priority': 'high',
                    'title': f"High bottleneck: {top_bottleneck['approver_email']}",
                    'description': f"{top_bottleneck['pending_count']} pending approvals, {top_bottleneck['expired_count']} expired",
                    'suggestions': [
                        "Consider delegating some approvals",
                        "Review auto-approval rules for this approver",
                        "Implement escalation for expired approvals"
                    ]
                })
        
        # Recomendación 2: Tipos de solicitud lentos
        if bottlenecks['slow_request_types']:
            slowest = bottlenecks['slow_request_types'][0]
            if slowest['avg_days'] > 7:
                recommendations.append({
                    'type': 'slow_process',
                    'priority': 'medium',
                    'title': f"Slow process: {slowest['request_type']}",
                    'description': f"Average {slowest['avg_days']:.1f} days to complete, P95: {slowest['p95_days']:.1f} days",
                    'suggestions': [
                        "Review approval chain for this request type",
                        "Consider reducing number of approval levels",
                        "Implement auto-approval rules for low-value requests"
                    ]
                })
        
        # Recomendación 3: Cadenas largas
        if bottlenecks['long_approval_chains']:
            longest = bottlenecks['long_approval_chains'][0]
            if longest['avg_chain_length'] > 3:
                recommendations.append({
                    'type': 'long_chain',
                    'priority': 'medium',
                    'title': f"Long approval chains: {longest['request_type']}",
                    'description': f"Average {longest['avg_chain_length']:.1f} approval levels, max {longest['max_chain_length']}",
                    'suggestions': [
                        "Simplify approval chain for this request type",
                        "Combine approval levels where possible",
                        "Use parallel approvals instead of sequential"
                    ]
                })
        
        # Recomendación 4: Patrones de tiempo
        if patterns['by_hour_of_day']:
            peak_hours = [h for h in patterns['by_hour_of_day'] if h['total'] > 10]
            if peak_hours:
                peak = max(peak_hours, key=lambda x: x['total'])
                recommendations.append({
                    'type': 'timing',
                    'priority': 'low',
                    'title': "Peak submission hours",
                    'description': f"Most requests submitted at {peak['hour']}:00 ({peak['total']} requests)",
                    'suggestions': [
                        "Consider scheduling reminders outside peak hours",
                        "Optimize notification delivery for peak times"
                    ]
                })
        
        result = {
            'recommendations': recommendations,
            'total_count': len(recommendations),
            'high_priority': len([r for r in recommendations if r['priority'] == 'high']),
            'medium_priority': len([r for r in recommendations if r['priority'] == 'medium']),
            'low_priority': len([r for r in recommendations if r['priority'] == 'low'])
        }
        
        logger.info(f"Generated {len(recommendations)} optimization recommendations")
        
        # Enviar resumen a Slack si hay recomendaciones de alta prioridad
        high_priority_recs = [r for r in recommendations if r['priority'] == 'high']
        if high_priority_recs:
            message = f"""
🔍 *Approval Optimization Recommendations*

*High Priority ({len(high_priority_recs)}):*
{chr(10).join([f"• {r['title']}: {r['description']}" for r in high_priority_recs])}
"""
            try:
                notify_slack(message)
            except Exception as e:
                logger.warning(f"Failed to send Slack notification: {e}")
        
        if Stats:
            try:
                Stats.incr('approval_analytics.recommendations_generated', len(recommendations))
            except Exception:
                pass
        
        return result
    
    # Pipeline
    patterns = analyze_approval_patterns()
    bottlenecks = detect_bottlenecks()
    recommendations = calculate_optimization_recommendations(patterns, bottlenecks)


approval_analytics_dag = approval_analytics()

