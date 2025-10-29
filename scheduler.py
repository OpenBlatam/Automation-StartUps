from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from app import create_app
from services.alert_service import alert_system
from services.replenishment_service import replenishment_service
from services.kpi_service import kpi_service
import logging
import atexit

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskScheduler:
    """Programador de tareas automáticas del sistema"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.app = create_app()
        self._setup_tasks()
    
    def _setup_tasks(self):
        """Configura las tareas programadas"""
        
        # Verificar alertas cada hora
        self.scheduler.add_job(
            func=self._check_alerts_task,
            trigger=IntervalTrigger(hours=1),
            id='check_alerts',
            name='Verificar Alertas de Stock',
            replace_existing=True
        )
        
        # Generar recomendaciones de reposición cada 6 horas
        self.scheduler.add_job(
            func=self._generate_recommendations_task,
            trigger=IntervalTrigger(hours=6),
            id='generate_recommendations',
            name='Generar Recomendaciones de Reposición',
            replace_existing=True
        )
        
        # Calcular KPIs diariamente a las 8:00 AM
        self.scheduler.add_job(
            func=self._calculate_kpis_task,
            trigger=CronTrigger(hour=8, minute=0),
            id='calculate_kpis',
            name='Calcular KPIs Diarios',
            replace_existing=True
        )
        
        # Limpiar alertas resueltas antiguas semanalmente
        self.scheduler.add_job(
            func=self._cleanup_old_alerts_task,
            trigger=CronTrigger(day_of_week=0, hour=2, minute=0),  # Domingo 2:00 AM
            id='cleanup_old_alerts',
            name='Limpiar Alertas Antiguas',
            replace_existing=True
        )
        
        logger.info("Tareas programadas configuradas exitosamente")
    
    def _check_alerts_task(self):
        """Tarea para verificar alertas de stock"""
        try:
            with self.app.app_context():
                alerts_created = alert_system.check_low_stock_alerts()
                logger.info(f"Verificación de alertas completada. Se crearon {alerts_created} alertas")
        except Exception as e:
            logger.error(f"Error en verificación de alertas: {str(e)}")
    
    def _generate_recommendations_task(self):
        """Tarea para generar recomendaciones de reposición"""
        try:
            with self.app.app_context():
                recommendations = replenishment_service.generate_reorder_recommendations()
                logger.info(f"Generación de recomendaciones completada. Se generaron {len(recommendations)} recomendaciones")
        except Exception as e:
            logger.error(f"Error generando recomendaciones: {str(e)}")
    
    def _calculate_kpis_task(self):
        """Tarea para calcular KPIs diarios"""
        try:
            with self.app.app_context():
                kpis = kpi_service.calculate_all_kpis()
                logger.info("Cálculo de KPIs diarios completado")
        except Exception as e:
            logger.error(f"Error calculando KPIs: {str(e)}")
    
    def _cleanup_old_alerts_task(self):
        """Tarea para limpiar alertas resueltas antiguas"""
        try:
            with self.app.app_context():
                from datetime import datetime, timedelta
                from models import Alert
                
                # Eliminar alertas resueltas de más de 30 días
                cutoff_date = datetime.utcnow() - timedelta(days=30)
                deleted_count = Alert.query.filter(
                    Alert.is_resolved == True,
                    Alert.resolved_at < cutoff_date
                ).delete()
                
                from app import db
                db.session.commit()
                
                logger.info(f"Limpieza de alertas completada. Se eliminaron {deleted_count} alertas antiguas")
        except Exception as e:
            logger.error(f"Error en limpieza de alertas: {str(e)}")
    
    def start(self):
        """Inicia el programador de tareas"""
        try:
            self.scheduler.start()
            logger.info("Programador de tareas iniciado exitosamente")
            
            # Registrar función de limpieza al cerrar la aplicación
            atexit.register(lambda: self.scheduler.shutdown())
            
        except Exception as e:
            logger.error(f"Error iniciando programador de tareas: {str(e)}")
    
    def stop(self):
        """Detiene el programador de tareas"""
        try:
            self.scheduler.shutdown()
            logger.info("Programador de tareas detenido")
        except Exception as e:
            logger.error(f"Error deteniendo programador de tareas: {str(e)}")
    
    def get_job_status(self):
        """Obtiene el estado de las tareas programadas"""
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
                'trigger': str(job.trigger)
            })
        return jobs

# Instancia global del programador
task_scheduler = TaskScheduler()

def start_scheduler():
    """Función para iniciar el programador desde la aplicación principal"""
    task_scheduler.start()

def stop_scheduler():
    """Función para detener el programador"""
    task_scheduler.stop()

def get_scheduler_status():
    """Función para obtener el estado del programador"""
    return task_scheduler.get_job_status()
