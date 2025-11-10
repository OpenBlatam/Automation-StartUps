"""
DAG para Generar Reportes de Analytics de Backups.

Genera reportes automáticos:
- Reporte diario
- Reporte semanal
- Reporte mensual
- Predicciones de espacio
"""
from __future__ import annotations

from datetime import timedelta
import logging
import os

import pendulum
from airflow.decorators import dag, task

from data.airflow.plugins.backup_analytics import BackupAnalyticsEngine
from data.airflow.plugins.etl_callbacks import on_task_failure
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    'backup_analytics_report',
    default_args={
        'owner': 'platform-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        'on_failure_callback': on_task_failure,
    },
    description='Genera reportes de analytics de backups',
    schedule='0 8 * * *',  # Diario a las 8 AM
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['backup', 'analytics', 'reporting'],
    max_active_runs=1,
    dagrun_timeout=timedelta(minutes=15),
)
def backup_analytics_report():
    """Pipeline de reportes de analytics."""
    
    analytics_engine = BackupAnalyticsEngine(
        backup_dir=os.getenv("BACKUP_DIR", "/tmp/backups")
    )
    
    @task(task_id='daily_report')
    def generate_daily_report():
        """Genera reporte diario."""
        report = analytics_engine.generate_daily_report()
        
        # Formatear para Slack
        analytics = report['analytics']
        message = f"""
📊 *Backup Daily Report - {report['date']}*

*Resumen:*
• Total backups: {analytics['total_backups']}
• Exitosos: {analytics['successful_backups']}
• Fallidos: {analytics['failed_backups']}
• Tasa de éxito: {analytics['success_rate']:.1%}
• Tamaño total: {analytics['total_size_gb']:.2f} GB
"""
        
        if report.get('trends'):
            trends = report['trends']
            if 'trend' in trends:
                message += f"\n*Tendencia:* {trends['trend']}\n"
        
        notify_slack(message)
        
        return report
    
    @task(task_id='weekly_report')
    def generate_weekly_report():
        """Genera reporte semanal (solo domingos)."""
        today = pendulum.now()
        if today.day_of_week != 7:  # No es domingo
            logger.info("Skipping weekly report (not Sunday)")
            return None
        
        report = analytics_engine.generate_weekly_report()
        
        analytics = report['analytics']
        message = f"""
📊 *Backup Weekly Report - Week {report['week_start']} to {report['week_end']}*

*Resumen Semanal:*
• Total backups: {analytics['total_backups']}
• Exitosos: {analytics['successful_backups']}
• Tasa de éxito: {analytics['success_rate']:.1%}
• Tamaño total: {analytics['total_size_gb']:.2f} GB

*Por Día:*
"""
        
        for day, stats in report['daily_breakdown'].items():
            message += f"• {day}: {stats['count']} backups, {stats['total_size_mb']:.2f} MB\n"
        
        notify_slack(message)
        
        return report
    
    @task(task_id='monthly_report')
    def generate_monthly_report():
        """Genera reporte mensual (solo día 1)."""
        today = pendulum.now()
        if today.day != 1:
            logger.info("Skipping monthly report (not first day of month)")
            return None
        
        report = analytics_engine.generate_monthly_report()
        
        analytics = report['analytics']
        message = f"""
📊 *Backup Monthly Report - {report['year']}/{report['month']:02d}*

*Resumen Mensual:*
• Total backups: {analytics['total_backups']}
• Exitosos: {analytics['successful_backups']}
• Tasa de éxito: {analytics['success_rate']:.1%}
• Tamaño total: {analytics['total_size_gb']:.2f} GB
"""
        
        if report.get('space_prediction'):
            prediction = report['space_prediction']
            message += f"\n*Predicción de Espacio (próximos 30 días):*\n"
            message += f"• Espacio estimado: {prediction['predicted_size_gb']:.2f} GB\n"
            message += f"• Confianza: {prediction['confidence']}\n"
        
        notify_slack(message)
        
        return report
    
    @task(task_id='space_prediction')
    def generate_space_prediction():
        """Genera predicción de espacio."""
        prediction = analytics_engine.predict_space_needs(days=30)
        
        message = f"""
🔮 *Predicción de Espacio para Backups*

*Próximos 30 días:*
• Espacio estimado: {prediction['predicted_size_gb']:.2f} GB
• Promedio diario: {prediction['avg_daily_gb']:.2f} GB
• Confianza: {prediction['confidence']}
• Días históricos: {prediction['historical_days']}
"""
        
        # Solo notificar si la predicción es alta
        if prediction['predicted_size_gb'] > 50:
            notify_slack(message)
        
        return prediction
    
    # Pipeline
    daily = generate_daily_report()
    weekly = generate_weekly_report()
    monthly = generate_monthly_report()
    prediction = generate_space_prediction()


backup_analytics_report_dag = backup_analytics_report()

