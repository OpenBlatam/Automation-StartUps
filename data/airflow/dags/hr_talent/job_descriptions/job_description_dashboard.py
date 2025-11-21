"""
Dashboard y reportes para el sistema de descripciones de puesto.

Funcionalidades:
- Generación de reportes en PDF/Excel
- Dashboard de métricas
- Exportación de datos
- Reportes programados
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow.providers.postgres.hooks.postgres import PostgresHook
import json
import logging
from typing import Dict, List, Optional
import csv
import io

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'hr-team',
    'depends_on_past': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=2),
}


def generate_pdf_report(**context) -> str:
    """Genera un reporte PDF de descripciones de puesto."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    report_type = context['dag_run'].conf.get('report_type', 'summary')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        if report_type == 'summary':
            # Reporte resumen
            query = """
                SELECT 
                    jd.job_description_id,
                    jd.role,
                    jd.level,
                    jd.department,
                    jd.status,
                    COUNT(DISTINCT jp.posting_id) as postings,
                    COUNT(DISTINCT ja.application_id) as applications,
                    AVG(ja.ai_score) as avg_score
                FROM job_descriptions jd
                LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
                LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
                WHERE jd.job_description_id = %s
                GROUP BY jd.job_description_id, jd.role, jd.level, jd.department, jd.status
            """
            result = pg_hook.get_first(query, parameters=(job_description_id,))
            
            # En producción, usar librería de PDF (reportlab, weasyprint, etc.)
            # Por ahora, generar HTML que se puede convertir a PDF
            html_content = f"""
            <html>
            <head><title>Reporte de Descripción de Puesto</title></head>
            <body>
                <h1>Reporte: {result[1]}</h1>
                <p><strong>Nivel:</strong> {result[2]}</p>
                <p><strong>Departamento:</strong> {result[3]}</p>
                <p><strong>Estado:</strong> {result[4]}</p>
                <p><strong>Publicaciones:</strong> {result[5] or 0}</p>
                <p><strong>Aplicaciones:</strong> {result[6] or 0}</p>
                <p><strong>Score Promedio:</strong> {result[7] or 0:.2f}</p>
            </body>
            </html>
            """
            
            # Guardar reporte
            report_path = f"/tmp/job_description_report_{job_description_id}_{datetime.now().strftime('%Y%m%d')}.html"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"Reporte PDF generado: {report_path}")
            return report_path
        
    except Exception as e:
        logger.error(f"Error generando reporte PDF: {str(e)}")
        raise


def export_to_excel(**context) -> str:
    """Exporta datos a Excel."""
    job_description_id = context['dag_run'].conf.get('job_description_id')
    export_type = context['dag_run'].conf.get('export_type', 'applications')
    
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        if export_type == 'applications':
            query = """
                SELECT 
                    ja.application_id,
                    ja.candidate_name,
                    ja.candidate_email,
                    ja.ai_score,
                    ja.fit_level,
                    ja.recommendation,
                    ja.status,
                    ja.processed_at
                FROM job_applications ja
                WHERE ja.job_description_id = %s
                ORDER BY ja.ai_score DESC
            """
            results = pg_hook.get_records(query, parameters=(job_description_id,))
            
            # Generar CSV (fácil de abrir en Excel)
            csv_path = f"/tmp/applications_export_{job_description_id}_{datetime.now().strftime('%Y%m%d')}.csv"
            
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'ID', 'Nombre', 'Email', 'Score', 'Fit Level', 
                    'Recomendación', 'Estado', 'Procesado'
                ])
                for row in results:
                    writer.writerow(row)
            
            logger.info(f"Exportación Excel generada: {csv_path}")
            return csv_path
        
    except Exception as e:
        logger.error(f"Error exportando a Excel: {str(e)}")
        raise


def generate_dashboard_metrics(**context) -> Dict:
    """Genera métricas para dashboard."""
    try:
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Métricas generales
        metrics = {}
        
        # Total de descripciones
        total_query = "SELECT COUNT(*) FROM job_descriptions"
        metrics['total_descriptions'] = pg_hook.get_first(total_query)[0]
        
        # Descripciones publicadas
        published_query = "SELECT COUNT(*) FROM job_descriptions WHERE status = 'published'"
        metrics['published_descriptions'] = pg_hook.get_first(published_query)[0]
        
        # Total de aplicaciones
        apps_query = "SELECT COUNT(*) FROM job_applications"
        metrics['total_applications'] = pg_hook.get_first(apps_query)[0]
        
        # Score promedio
        avg_score_query = "SELECT AVG(ai_score) FROM job_applications WHERE ai_score IS NOT NULL"
        result = pg_hook.get_first(avg_score_query)
        metrics['avg_application_score'] = float(result[0]) if result[0] else 0
        
        # Aplicaciones calificadas
        qualified_query = """
            SELECT COUNT(*) FROM job_applications 
            WHERE status = 'qualified'
        """
        metrics['qualified_applications'] = pg_hook.get_first(qualified_query)[0]
        
        # Top roles por aplicaciones
        top_roles_query = """
            SELECT jd.role, COUNT(ja.application_id) as app_count
            FROM job_descriptions jd
            LEFT JOIN job_postings jp ON jd.job_description_id = jp.job_description_id
            LEFT JOIN job_applications ja ON jp.posting_id = ja.posting_id
            GROUP BY jd.role
            ORDER BY app_count DESC
            LIMIT 10
        """
        top_roles = pg_hook.get_records(top_roles_query)
        metrics['top_roles'] = [{"role": r[0], "applications": r[1]} for r in top_roles]
        
        # Guardar métricas
        pg_hook.run("""
            INSERT INTO dashboard_metrics (metrics_data, created_at)
            VALUES (%s, NOW())
        """, parameters=(json.dumps(metrics),))
        
        logger.info("Métricas de dashboard generadas")
        return metrics
        
    except Exception as e:
        logger.error(f"Error generando métricas: {str(e)}")
        raise


def schedule_weekly_report(**context) -> None:
    """Programa reporte semanal automático."""
    try:
        # En producción, esto podría crear un DAG run programado
        # o enviar el reporte por email
        
        logger.info("Reporte semanal programado")
        
    except Exception as e:
        logger.error(f"Error programando reporte: {str(e)}")


# DAG para dashboard y reportes
with DAG(
    'job_description_dashboard',
    default_args=default_args,
    description='Dashboard y reportes para descripciones de puesto',
    schedule_interval='0 9 * * 1',  # Lunes a las 9 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['hr', 'dashboard', 'reports'],
) as dag:
    
    generate_metrics = PythonOperator(
        task_id='generate_dashboard_metrics',
        python_callable=generate_dashboard_metrics,
    )
    
    schedule_report = PythonOperator(
        task_id='schedule_weekly_report',
        python_callable=schedule_weekly_report,
    )
    
    generate_metrics >> schedule_report






