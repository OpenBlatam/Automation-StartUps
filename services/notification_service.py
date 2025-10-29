from datetime import datetime
from flask import current_app
from flask_mail import Message
from app import db, mail
from models import Alert
from services.alert_service import alert_system
import logging

class NotificationService:
    """Servicio de notificaciones por email"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def send_alert_notification(self, alert: Alert) -> bool:
        """Envía notificación por email de una alerta"""
        try:
            if not self._is_email_configured():
                return False
            
            subject = f"[ALERTA] {alert.alert_type.upper()} - {alert.product.name}"
            recipients = self._get_notification_recipients()
            
            if not recipients:
                return False
            
            msg = Message(
                subject=subject,
                recipients=recipients,
                body=f"""
                Alerta de Inventario
                
                Tipo: {alert.alert_type}
                Producto: {alert.product.name}
                SKU: {alert.product.sku}
                Mensaje: {alert.message}
                Severidad: {alert.severity}
                Fecha: {alert.created_at.strftime('%d/%m/%Y %H:%M:%S')}
                
                Stock Actual: {alert_system.get_current_stock(alert.product.id)}
                Stock Mínimo: {alert.product.min_stock_level}
                
                ---
                Sistema de Control de Inventario
                """
            )
            
            mail.send(msg)
            self.logger.info(f'Notificación de alerta {alert.id} enviada')
            return True
            
        except Exception as e:
            self.logger.error(f'Error enviando notificación: {str(e)}')
            return False
    
    def send_daily_summary(self) -> bool:
        """Envía resumen diario del sistema"""
        try:
            if not self._is_email_configured():
                return False
            
            from models import Alert, ReorderRecommendation, SalesRecord
            
            # Obtener datos del día
            today = datetime.utcnow().date()
            yesterday = today - timedelta(days=1)
            
            # Alertas activas
            active_alerts = Alert.query.filter(Alert.is_resolved == False).count()
            
            # Recomendaciones pendientes
            pending_recommendations = ReorderRecommendation.query.filter(
                ReorderRecommendation.is_processed == False
            ).count()
            
            # Ventas del día anterior
            yesterday_sales = SalesRecord.query.filter(
                db.func.date(SalesRecord.sale_date) == yesterday
            ).all()
            
            yesterday_revenue = sum(sale.total_amount for sale in yesterday_sales)
            
            subject = f"Resumen Diario del Sistema de Inventario - {today.strftime('%d/%m/%Y')}"
            
            msg = Message(
                subject=subject,
                recipients=self._get_notification_recipients(),
                body=f"""
                RESUMEN DIARIO DEL SISTEMA DE INVENTARIO
                {today.strftime('%d/%m/%Y')}
                
                VENTAS DE AYER:
                - Ingresos: ${yesterday_revenue:.2f}
                - Transacciones: {len(yesterday_sales)}
                
                ALERTAS ACTIVAS: {active_alerts}
                
                RECOMENDACIONES PENDIENTES: {pending_recommendations}
                
                ---
                Sistema de Control de Inventario
                """
            )
            
            mail.send(msg)
            self.logger.info('Resumen diario enviado exitosamente')
            return True
            
        except Exception as e:
            self.logger.error(f'Error enviando resumen diario: {str(e)}')
            return False
    
    def _is_email_configured(self) -> bool:
        """Verifica si el email está configurado"""
        return bool(current_app.config.get('MAIL_USERNAME'))
    
    def _get_notification_recipients(self):
        """Obtiene destinatarios para notificaciones"""
        admin_email = current_app.config.get('ADMIN_EMAIL', 'admin@company.com')
        return [admin_email]

# Instancia global
notification_service = NotificationService()



