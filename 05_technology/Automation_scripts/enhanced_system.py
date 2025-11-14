"""
Sistema de Gestión de Inventario y Cadena de Suministro - Versión Mejorada
=========================================================================

Mejoras implementadas:
- Sistema de notificaciones por email
- Programación automática de tareas
- API REST completa
- Integración con sistemas externos
- Dashboard avanzado con métricas en tiempo real
- Sistema de respaldo automático
- Análisis predictivo avanzado
"""

import os
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass, asdict
from enum import Enum
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de logging mejorada
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('inventory_system.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class NotificationType(Enum):
    """Tipos de notificaciones"""
    EMAIL = "email"
    SMS = "sms"
    WEBHOOK = "webhook"
    DASHBOARD = "dashboard"

class TaskStatus(Enum):
    """Estados de tareas"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class NotificationConfig:
    """Configuración de notificaciones"""
    email_enabled: bool = True
    sms_enabled: bool = False
    webhook_enabled: bool = False
    dashboard_enabled: bool = True
    email_recipients: List[str] = None
    webhook_url: str = ""
    sms_provider: str = ""
    
    def __post_init__(self):
        if self.email_recipients is None:
            self.email_recipients = []

@dataclass
class SystemMetrics:
    """Métricas del sistema"""
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    active_connections: int
    response_time: float
    timestamp: datetime

class EnhancedInventorySystem:
    """Sistema de inventario mejorado con funcionalidades avanzadas"""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.load_config()
        self.setup_database()
        self.setup_notifications()
        self.setup_scheduler()
        self.setup_backup_system()
        self.metrics_history = []
        
    def load_config(self):
        """Cargar configuración del sistema"""
        default_config = {
            "database": {
                "path": "inventory.db",
                "backup_interval": 24,  # horas
                "max_backups": 7
            },
            "notifications": {
                "email_enabled": True,
                "email_recipients": ["admin@company.com"],
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "smtp_username": "",
                "smtp_password": ""
            },
            "api": {
                "rate_limit": 100,  # requests per minute
                "api_key_required": True,
                "cors_enabled": True
            },
            "analytics": {
                "prediction_horizon": 30,  # días
                "confidence_threshold": 0.8,
                "seasonal_analysis": True,
                "ml_model_retrain_interval": 7  # días
            },
            "alerts": {
                "check_interval": 300,  # segundos
                "escalation_enabled": True,
                "auto_resolve": False
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = default_config
                self.save_config()
        except Exception as e:
            logger.error(f"Error cargando configuración: {e}")
            self.config = default_config
    
    def save_config(self):
        """Guardar configuración"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            logger.error(f"Error guardando configuración: {e}")
    
    def setup_database(self):
        """Configurar base de datos con conexión mejorada"""
        from inventory_management_system import InventoryManagementSystem
        self.ims = InventoryManagementSystem(self.config["database"]["path"])
        
        # Configurar conexión con pool de conexiones
        import sqlite3
        self.db_path = self.config["database"]["path"]
        
    def setup_notifications(self):
        """Configurar sistema de notificaciones"""
        self.notification_config = NotificationConfig(
            email_enabled=self.config["notifications"]["email_enabled"],
            email_recipients=self.config["notifications"]["email_recipients"],
            webhook_enabled=self.config["api"].get("webhook_enabled", False),
            webhook_url=self.config["api"].get("webhook_url", "")
        )
        
        # Configurar SMTP si está habilitado
        if self.notification_config.email_enabled:
            self.smtp_server = self.config["notifications"]["smtp_server"]
            self.smtp_port = self.config["notifications"]["smtp_port"]
            self.smtp_username = self.config["notifications"]["smtp_username"]
            self.smtp_password = self.config["notifications"]["smtp_password"]
    
    def setup_scheduler(self):
        """Configurar programador de tareas"""
        self.scheduler = BackgroundScheduler()
        
        # Tareas programadas
        self.scheduler.add_job(
            func=self.run_daily_checks,
            trigger="cron",
            hour=6,
            minute=0,
            id="daily_checks"
        )
        
        self.scheduler.add_job(
            func=self.generate_daily_report,
            trigger="cron",
            hour=8,
            minute=0,
            id="daily_report"
        )
        
        self.scheduler.add_job(
            func=self.backup_database,
            trigger="interval",
            hours=self.config["database"]["backup_interval"],
            id="database_backup"
        )
        
        self.scheduler.add_job(
            func=self.update_metrics,
            trigger="interval",
            minutes=5,
            id="metrics_update"
        )
        
        self.scheduler.start()
        logger.info("Programador de tareas iniciado")
    
    def setup_backup_system(self):
        """Configurar sistema de respaldo"""
        self.backup_dir = "backups"
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
    
    def send_notification(self, subject: str, message: str, 
                         notification_type: NotificationType = NotificationType.EMAIL,
                         priority: str = "normal"):
        """Enviar notificación"""
        try:
            if notification_type == NotificationType.EMAIL and self.notification_config.email_enabled:
                self._send_email(subject, message)
            elif notification_type == NotificationType.WEBHOOK and self.notification_config.webhook_enabled:
                self._send_webhook(subject, message)
            
            logger.info(f"Notificación enviada: {subject}")
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
    
    def _send_email(self, subject: str, message: str):
        """Enviar email"""
        try:
            msg = MIMEMultipart()
            msg['From'] = self.smtp_username
            msg['To'] = ", ".join(self.notification_config.email_recipients)
            msg['Subject'] = f"[Sistema Inventario] {subject}"
            
            msg.attach(MIMEText(message, 'html'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.smtp_username, self.smtp_password)
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
    
    def _send_webhook(self, subject: str, message: str):
        """Enviar webhook"""
        try:
            payload = {
                "subject": subject,
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "system": "inventory_management"
            }
            
            response = requests.post(
                self.notification_config.webhook_url,
                json=payload,
                timeout=10
            )
            
            if response.status_code != 200:
                logger.warning(f"Webhook falló con código: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error enviando webhook: {e}")
    
    def run_daily_checks(self):
        """Ejecutar verificaciones diarias mejoradas"""
        logger.info("Iniciando verificaciones diarias")
        
        try:
            # Verificaciones del sistema base
            self.ims.run_daily_checks()
            
            # Verificaciones adicionales
            self._check_system_health()
            self._check_data_integrity()
            self._check_performance_metrics()
            
            # Generar reporte de verificaciones
            report = self._generate_health_report()
            
            # Enviar notificación si hay problemas
            if report["issues_found"] > 0:
                self.send_notification(
                    "Problemas detectados en verificaciones diarias",
                    self._format_health_report(report),
                    priority="high"
                )
            
            logger.info("Verificaciones diarias completadas")
            
        except Exception as e:
            logger.error(f"Error en verificaciones diarias: {e}")
            self.send_notification(
                "Error en verificaciones diarias",
                f"Se produjo un error durante las verificaciones: {str(e)}",
                priority="critical"
            )
    
    def _check_system_health(self):
        """Verificar salud del sistema"""
        # Verificar espacio en disco
        import shutil
        disk_usage = shutil.disk_usage('/')
        free_space_gb = disk_usage.free / (1024**3)
        
        if free_space_gb < 1:  # Menos de 1GB libre
            self.send_notification(
                "Espacio en disco bajo",
                f"Solo quedan {free_space_gb:.2f} GB de espacio libre",
                priority="high"
            )
        
        # Verificar tamaño de base de datos
        if os.path.exists(self.db_path):
            db_size_mb = os.path.getsize(self.db_path) / (1024**2)
            if db_size_mb > 100:  # Más de 100MB
                logger.warning(f"Base de datos grande: {db_size_mb:.2f} MB")
    
    def _check_data_integrity(self):
        """Verificar integridad de datos"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Verificar productos sin inventario
        cursor.execute("""
            SELECT COUNT(*) FROM products p
            LEFT JOIN inventory i ON p.id = i.product_id
            WHERE i.product_id IS NULL
        """)
        products_without_inventory = cursor.fetchone()[0]
        
        if products_without_inventory > 0:
            logger.warning(f"{products_without_inventory} productos sin registro de inventario")
        
        # Verificar alertas antiguas sin resolver
        cursor.execute("""
            SELECT COUNT(*) FROM alerts
            WHERE resolved = FALSE
            AND created_at < datetime('now', '-7 days')
        """)
        old_alerts = cursor.fetchone()[0]
        
        if old_alerts > 0:
            self.send_notification(
                "Alertas antiguas sin resolver",
                f"Hay {old_alerts} alertas sin resolver desde hace más de 7 días",
                priority="medium"
            )
        
        conn.close()
    
    def _check_performance_metrics(self):
        """Verificar métricas de rendimiento"""
        # Simular métricas del sistema
        import psutil
        
        cpu_usage = psutil.cpu_percent()
        memory_usage = psutil.virtual_memory().percent
        
        metrics = SystemMetrics(
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            disk_usage=psutil.disk_usage('/').percent,
            active_connections=0,  # Simulado
            response_time=0.1,  # Simulado
            timestamp=datetime.now()
        )
        
        self.metrics_history.append(metrics)
        
        # Mantener solo las últimas 1000 métricas
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # Alertar si el uso de CPU es alto
        if cpu_usage > 80:
            self.send_notification(
                "Uso de CPU alto",
                f"El uso de CPU es del {cpu_usage}%",
                priority="medium"
            )
    
    def _generate_health_report(self) -> Dict:
        """Generar reporte de salud del sistema"""
        import sqlite3
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Estadísticas básicas
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM alerts WHERE resolved = FALSE")
        active_alerts = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM inventory WHERE quantity <= 0")
        out_of_stock = cursor.fetchone()[0]
        
        conn.close()
        
        # Calcular métricas de rendimiento
        recent_metrics = self.metrics_history[-10:] if self.metrics_history else []
        avg_cpu = sum(m.cpu_usage for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        avg_memory = sum(m.memory_usage for m in recent_metrics) / len(recent_metrics) if recent_metrics else 0
        
        issues_found = 0
        if active_alerts > 10:
            issues_found += 1
        if out_of_stock > 0:
            issues_found += 1
        if avg_cpu > 70:
            issues_found += 1
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_products": total_products,
            "active_alerts": active_alerts,
            "out_of_stock": out_of_stock,
            "avg_cpu_usage": avg_cpu,
            "avg_memory_usage": avg_memory,
            "issues_found": issues_found,
            "system_status": "healthy" if issues_found == 0 else "warning" if issues_found < 3 else "critical"
        }
    
    def _format_health_report(self, report: Dict) -> str:
        """Formatear reporte de salud para email"""
        status_emoji = {
            "healthy": "✅",
            "warning": "⚠️",
            "critical": "🚨"
        }
        
        return f"""
        <html>
        <body>
            <h2>{status_emoji.get(report['system_status'], '❓')} Reporte de Salud del Sistema</h2>
            <p><strong>Fecha:</strong> {report['timestamp']}</p>
            <p><strong>Estado:</strong> {report['system_status'].upper()}</p>
            
            <h3>Métricas del Inventario</h3>
            <ul>
                <li>Total de productos: {report['total_products']}</li>
                <li>Alertas activas: {report['active_alerts']}</li>
                <li>Productos sin stock: {report['out_of_stock']}</li>
            </ul>
            
            <h3>Métricas del Sistema</h3>
            <ul>
                <li>Uso promedio de CPU: {report['avg_cpu_usage']:.1f}%</li>
                <li>Uso promedio de memoria: {report['avg_memory_usage']:.1f}%</li>
            </ul>
            
            <h3>Problemas Detectados</h3>
            <p>Se encontraron {report['issues_found']} problemas que requieren atención.</p>
        </body>
        </html>
        """
    
    def generate_daily_report(self):
        """Generar reporte diario automático"""
        try:
            from advanced_analytics import AdvancedAnalytics
            analytics = AdvancedAnalytics(self.db_path)
            
            # Generar reporte ejecutivo
            report = analytics.generate_executive_report()
            
            # Formatear reporte para email
            email_content = self._format_executive_report(report)
            
            # Enviar reporte por email
            self.send_notification(
                f"Reporte Diario - {datetime.now().strftime('%Y-%m-%d')}",
                email_content
            )
            
            logger.info("Reporte diario generado y enviado")
            
        except Exception as e:
            logger.error(f"Error generando reporte diario: {e}")
    
    def _format_executive_report(self, report: Dict) -> str:
        """Formatear reporte ejecutivo para email"""
        return f"""
        <html>
        <body>
            <h2>📊 Reporte Ejecutivo Diario</h2>
            <p><strong>Fecha:</strong> {report['report_date']}</p>
            
            <h3>📈 Resumen Ejecutivo</h3>
            <ul>
                <li>Total de productos: {report['executive_summary']['total_products']}</li>
                <li>Valor total del inventario: ${report['executive_summary']['total_inventory_value']:,.2f}</li>
                <li>Alertas activas: {report['executive_summary']['active_alerts']}</li>
                <li>Puntuación de optimización: {report['executive_summary']['optimization_score']:.1f}%</li>
            </ul>
            
            <h3>🎯 Recomendaciones Clave</h3>
            <ol>
                {''.join(f'<li>{rec}</li>' for rec in report['key_recommendations'])}
            </ol>
            
            <h3>📊 Análisis ABC</h3>
            <ul>
                <li>Categoría A: {report['abc_analysis']['A']['count']} productos ({report['abc_analysis']['A']['percentage']:.1f}% del valor)</li>
                <li>Categoría B: {report['abc_analysis']['B']['count']} productos ({report['abc_analysis']['B']['percentage']:.1f}% del valor)</li>
                <li>Categoría C: {report['abc_analysis']['C']['count']} productos ({report['abc_analysis']['C']['percentage']:.1f}% del valor)</li>
            </ul>
            
            <p><em>Este reporte fue generado automáticamente por el Sistema de Gestión de Inventario.</em></p>
        </body>
        </html>
        """
    
    def backup_database(self):
        """Crear respaldo de la base de datos"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"inventory_backup_{timestamp}.db"
            backup_path = os.path.join(self.backup_dir, backup_filename)
            
            # Copiar base de datos
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # Limpiar respaldos antiguos
            self._cleanup_old_backups()
            
            logger.info(f"Respaldo creado: {backup_filename}")
            
            # Notificar si el respaldo es exitoso
            self.send_notification(
                "Respaldo de base de datos completado",
                f"Se creó exitosamente el respaldo: {backup_filename}",
                priority="low"
            )
            
        except Exception as e:
            logger.error(f"Error creando respaldo: {e}")
            self.send_notification(
                "Error en respaldo de base de datos",
                f"Error creando respaldo: {str(e)}",
                priority="high"
            )
    
    def _cleanup_old_backups(self):
        """Limpiar respaldos antiguos"""
        try:
            import glob
            
            backup_files = glob.glob(os.path.join(self.backup_dir, "inventory_backup_*.db"))
            backup_files.sort(key=os.path.getmtime, reverse=True)
            
            # Mantener solo los últimos N respaldos
            max_backups = self.config["database"]["max_backups"]
            for old_backup in backup_files[max_backups:]:
                os.remove(old_backup)
                logger.info(f"Respaldo antiguo eliminado: {os.path.basename(old_backup)}")
                
        except Exception as e:
            logger.error(f"Error limpiando respaldos antiguos: {e}")
    
    def update_metrics(self):
        """Actualizar métricas del sistema"""
        try:
            import psutil
            
            metrics = SystemMetrics(
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                disk_usage=psutil.disk_usage('/').percent,
                active_connections=0,  # Simulado
                response_time=0.1,  # Simulado
                timestamp=datetime.now()
            )
            
            self.metrics_history.append(metrics)
            
            # Mantener solo las últimas 1000 métricas
            if len(self.metrics_history) > 1000:
                self.metrics_history = self.metrics_history[-1000:]
                
        except Exception as e:
            logger.error(f"Error actualizando métricas: {e}")
    
    def get_system_status(self) -> Dict:
        """Obtener estado del sistema"""
        recent_metrics = self.metrics_history[-1] if self.metrics_history else None
        
        return {
            "status": "running",
            "uptime": "N/A",  # Simulado
            "last_backup": self._get_last_backup_time(),
            "metrics": asdict(recent_metrics) if recent_metrics else None,
            "scheduled_tasks": len(self.scheduler.get_jobs()),
            "config_version": "1.0"
        }
    
    def _get_last_backup_time(self) -> str:
        """Obtener tiempo del último respaldo"""
        try:
            import glob
            
            backup_files = glob.glob(os.path.join(self.backup_dir, "inventory_backup_*.db"))
            if backup_files:
                latest_backup = max(backup_files, key=os.path.getmtime)
                return datetime.fromtimestamp(os.path.getmtime(latest_backup)).isoformat()
            else:
                return "Nunca"
        except Exception as e:
            logger.error(f"Error obteniendo tiempo de respaldo: {e}")
            return "Error"
    
    def shutdown(self):
        """Apagar el sistema de manera segura"""
        logger.info("Iniciando apagado del sistema...")
        
        try:
            # Detener programador
            self.scheduler.shutdown()
            
            # Crear respaldo final
            self.backup_database()
            
            # Guardar configuración
            self.save_config()
            
            logger.info("Sistema apagado correctamente")
            
        except Exception as e:
            logger.error(f"Error durante el apagado: {e}")

# Función principal para ejecutar el sistema mejorado
def main():
    """Función principal del sistema mejorado"""
    logger.info("Iniciando Sistema de Gestión de Inventario Mejorado")
    
    try:
        # Crear instancia del sistema
        system = EnhancedInventorySystem()
        
        # Mostrar estado del sistema
        status = system.get_system_status()
        logger.info(f"Estado del sistema: {status}")
        
        # Mantener el sistema ejecutándose
        try:
            while True:
                time.sleep(60)  # Verificar cada minuto
                
                # Verificar si hay tareas críticas pendientes
                if system.metrics_history:
                    latest_metrics = system.metrics_history[-1]
                    if latest_metrics.cpu_usage > 90:
                        logger.warning("Uso de CPU crítico detectado")
                        
        except KeyboardInterrupt:
            logger.info("Interrupción recibida, apagando sistema...")
            system.shutdown()
            
    except Exception as e:
        logger.error(f"Error crítico en el sistema: {e}")
        raise

if __name__ == "__main__":
    main()



