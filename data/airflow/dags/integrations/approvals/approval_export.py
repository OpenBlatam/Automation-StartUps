"""
Airflow DAG para exportar datos del sistema de aprobaciones.
Exporta datos históricos, reportes y métricas a varios formatos.
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os
import json
import csv
from typing import Dict, Any, List
from io import StringIO

import pendulum
from airflow.decorators import dag, task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.models.param import Param

from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

try:
    from airflow.stats import Stats
except Exception:
    Stats = None

logger = logging.getLogger(__name__)

APPROVALS_DB_CONN = os.getenv("APPROVALS_DB_CONN_ID", "approvals_db")


@dag(
    'approval_export',
    default_args={
        'owner': 'approvals-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
    },
    description='Exportar datos del sistema de aprobaciones a varios formatos',
    schedule='0 3 * * 1',  # Cada lunes a las 3 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['approvals', 'export', 'data'],
    params={
        'export_format': Param('json', type='string', description='Formato: json, csv, both'),
        'export_period_days': Param(30, type='integer', minimum=1, maximum=365, description='Días a exportar'),
        'export_to_s3': Param(False, type='boolean', description='Exportar a S3'),
        's3_bucket': Param('', type='string', description='Bucket S3'),
        's3_prefix': Param('approvals/exports/', type='string', description='Prefijo S3'),
    },
    max_active_runs=1,
    dagrun_timeout=timedelta(hours=1),
)
def approval_export() -> None:
    """Pipeline de exportación de datos."""
    
    @task(task_id='export_approval_requests', on_failure_callback=on_task_failure)
    def export_approval_requests() -> Dict[str, Any]:
        """Exportar solicitudes de aprobación."""
        context = get_current_context()
        params = context.get('params', {})
        period_days = params.get('export_period_days', 30)
        export_format = params.get('export_format', 'json')
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Obtener solicitudes del período
            sql = """
                SELECT 
                    id,
                    request_type,
                    requester_email,
                    title,
                    description,
                    status,
                    priority,
                    auto_approved,
                    submitted_at,
                    completed_at,
                    created_at,
                    updated_at,
                    metadata
                FROM approval_requests
                WHERE created_at >= NOW() - INTERVAL '%s days'
                ORDER BY created_at DESC;
            """ % period_days
            
            results = pg_hook.get_records(sql)
            
            # Convertir a lista de diccionarios
            columns = [
                'id', 'request_type', 'requester_email', 'title', 'description',
                'status', 'priority', 'auto_approved', 'submitted_at', 'completed_at',
                'created_at', 'updated_at', 'metadata'
            ]
            
            requests_data = []
            for row in results:
                request_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    elif isinstance(value, dict):
                        value = json.dumps(value)
                    request_dict[col] = value
                requests_data.append(request_dict)
            
            export_data = {
                'export_date': pendulum.now().isoformat(),
                'period_days': period_days,
                'total_records': len(requests_data),
                'data': requests_data
            }
            
            # Exportar según formato
            exports = {}
            
            if export_format in ['json', 'both']:
                exports['json'] = json.dumps(export_data, indent=2, default=str)
                logger.info(f"Exported {len(requests_data)} requests to JSON format")
            
            if export_format in ['csv', 'both']:
                # Exportar a CSV
                output = StringIO()
                if requests_data:
                    writer = csv.DictWriter(output, fieldnames=columns)
                    writer.writeheader()
                    for request in requests_data:
                        # Convertir metadata a string si es dict
                        row = request.copy()
                        if isinstance(row.get('metadata'), dict):
                            row['metadata'] = json.dumps(row['metadata'])
                        writer.writerow(row)
                exports['csv'] = output.getvalue()
                logger.info(f"Exported {len(requests_data)} requests to CSV format")
            
            if Stats:
                try:
                    Stats.incr('approval_export.requests_exported', len(requests_data))
                except Exception:
                    pass
            
            return {
                'format': export_format,
                'total_records': len(requests_data),
                'exports': exports
            }
            
        except Exception as e:
            logger.error("Failed to export approval requests", exc_info=True)
            raise
    
    @task(task_id='export_approval_chains', on_failure_callback=on_task_failure)
    def export_approval_chains() -> Dict[str, Any]:
        """Exportar cadenas de aprobación."""
        context = get_current_context()
        params = context.get('params', {})
        period_days = params.get('export_period_days', 30)
        export_format = params.get('export_format', 'json')
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            sql = """
                SELECT 
                    ac.id,
                    ac.request_id,
                    ac.level,
                    ac.approver_email,
                    ac.approver_role,
                    ac.required,
                    ac.status,
                    ac.delegated_to,
                    ac.comments,
                    ac.approved_at,
                    ac.rejected_at,
                    ac.timeout_date,
                    ac.notified_at,
                    ac.created_at,
                    ac.updated_at
                FROM approval_chains ac
                JOIN approval_requests ar ON ac.request_id = ar.id
                WHERE ar.created_at >= NOW() - INTERVAL '%s days'
                ORDER BY ac.created_at DESC;
            """ % period_days
            
            results = pg_hook.get_records(sql)
            
            columns = [
                'id', 'request_id', 'level', 'approver_email', 'approver_role',
                'required', 'status', 'delegated_to', 'comments', 'approved_at',
                'rejected_at', 'timeout_date', 'notified_at', 'created_at', 'updated_at'
            ]
            
            chains_data = []
            for row in results:
                chain_dict = {}
                for i, col in enumerate(columns):
                    value = row[i]
                    if hasattr(value, 'isoformat'):
                        value = value.isoformat()
                    chain_dict[col] = value
                chains_data.append(chain_dict)
            
            export_data = {
                'export_date': pendulum.now().isoformat(),
                'period_days': period_days,
                'total_records': len(chains_data),
                'data': chains_data
            }
            
            exports = {}
            
            if export_format in ['json', 'both']:
                exports['json'] = json.dumps(export_data, indent=2, default=str)
            
            if export_format in ['csv', 'both']:
                output = StringIO()
                if chains_data:
                    writer = csv.DictWriter(output, fieldnames=columns)
                    writer.writeheader()
                    for chain in chains_data:
                        writer.writerow(chain)
                exports['csv'] = output.getvalue()
            
            logger.info(f"Exported {len(chains_data)} approval chains")
            
            if Stats:
                try:
                    Stats.incr('approval_export.chains_exported', len(chains_data))
                except Exception:
                    pass
            
            return {
                'format': export_format,
                'total_records': len(chains_data),
                'exports': exports
            }
            
        except Exception as e:
            logger.error("Failed to export approval chains", exc_info=True)
            raise
    
    @task(task_id='export_metrics_summary', on_failure_callback=on_task_failure)
    def export_metrics_summary() -> Dict[str, Any]:
        """Exportar resumen de métricas."""
        context = get_current_context()
        params = context.get('params', {})
        period_days = params.get('export_period_days', 30)
        
        try:
            pg_hook = PostgresHook(postgres_conn_id=APPROVALS_DB_CONN)
            
            # Métricas agregadas
            metrics_sql = """
                SELECT 
                    request_type,
                    status,
                    priority,
                    COUNT(*) as count,
                    AVG(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) 
                        FILTER (WHERE completed_at IS NOT NULL) as avg_hours,
                    MIN(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) 
                        FILTER (WHERE completed_at IS NOT NULL) as min_hours,
                    MAX(EXTRACT(EPOCH FROM (completed_at - submitted_at)) / 3600) 
                        FILTER (WHERE completed_at IS NOT NULL) as max_hours
                FROM approval_requests
                WHERE created_at >= NOW() - INTERVAL '%s days'
                GROUP BY request_type, status, priority
                ORDER BY request_type, status, priority;
            """ % period_days
            
            results = pg_hook.get_records(metrics_sql)
            
            metrics_data = []
            for row in results:
                metrics_data.append({
                    'request_type': row[0],
                    'status': row[1],
                    'priority': row[2],
                    'count': row[3],
                    'avg_hours': round(row[4], 2) if row[4] else None,
                    'min_hours': round(row[5], 2) if row[5] else None,
                    'max_hours': round(row[6], 2) if row[6] else None
                })
            
            export_data = {
                'export_date': pendulum.now().isoformat(),
                'period_days': period_days,
                'total_groups': len(metrics_data),
                'metrics': metrics_data
            }
            
            logger.info(f"Exported metrics summary with {len(metrics_data)} groups")
            
            return {
                'format': 'json',
                'total_groups': len(metrics_data),
                'export': json.dumps(export_data, indent=2, default=str)
            }
            
        except Exception as e:
            logger.error("Failed to export metrics summary", exc_info=True)
            raise
    
    @task(task_id='generate_export_report', on_failure_callback=on_task_failure)
    def generate_export_report(
        requests_export: Dict[str, Any],
        chains_export: Dict[str, Any],
        metrics_export: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generar reporte de exportación."""
        context = get_current_context()
        params = context.get('params', {})
        
        report = {
            'export_date': pendulum.now().isoformat(),
            'format': params.get('export_format', 'json'),
            'period_days': params.get('export_period_days', 30),
            'requests': {
                'total_records': requests_export.get('total_records', 0),
                'format': requests_export.get('format')
            },
            'chains': {
                'total_records': chains_export.get('total_records', 0),
                'format': chains_export.get('format')
            },
            'metrics': {
                'total_groups': metrics_export.get('total_groups', 0)
            },
            'total_records': (
                requests_export.get('total_records', 0) +
                chains_export.get('total_records', 0)
            )
        }
        
        logger.info(f"Export report: {json.dumps(report, indent=2)}")
        
        # Enviar notificación
        try:
            message = f"""
📦 *Approval Data Export Report*

*Export Summary:*
• Requests exported: {report['requests']['total_records']}
• Chains exported: {report['chains']['total_records']}
• Metrics groups: {report['metrics']['total_groups']}
• Total records: {report['total_records']}
• Format: {report['format']}
• Period: {report['period_days']} days
"""
            notify_slack(message)
        except Exception as e:
            logger.warning(f"Failed to send export notification: {e}")
        
        if Stats:
            try:
                Stats.incr('approval_export.export_completed', 1)
                Stats.gauge('approval_export.total_records_exported', report['total_records'])
            except Exception:
                pass
        
        return report
    
    # Pipeline
    requests_export = export_approval_requests()
    chains_export = export_approval_chains()
    metrics_export = export_metrics_summary()
    
    generate_export_report(requests_export, chains_export, metrics_export)


approval_export_dag = approval_export()

