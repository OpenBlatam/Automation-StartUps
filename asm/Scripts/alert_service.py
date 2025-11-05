from datetime import datetime, timedelta
from flask import current_app
from app import db, mail
from models import Product, InventoryRecord, Alert, SalesRecord
from flask_mail import Message
import logging

class AlertSystem:
    """Sistema de alertas automáticas para inventario"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def check_low_stock_alerts(self):
        """Verifica productos con stock bajo y genera alertas"""
        try:
            products = Product.query.all()
            alerts_created = 0
            
            for product in products:
                current_stock = self.get_current_stock(product.id)
                
                # Verificar diferentes niveles de alerta
                if current_stock <= 0:
                    self.create_alert(
                        product_id=product.id,
                        alert_type='out_of_stock',
                        message=f'Producto {product.name} está agotado',
                        severity='critical'
                    )
                    alerts_created += 1
                
                elif current_stock <= product.min_stock_level:
                    self.create_alert(
                        product_id=product.id,
                        alert_type='low_stock',
                        message=f'Producto {product.name} tiene stock bajo ({current_stock} unidades)',
                        severity='high'
                    )
                    alerts_created += 1
                
                elif current_stock <= product.reorder_point:
                    self.create_alert(
                        product_id=product.id,
                        alert_type='reorder',
                        message=f'Producto {product.name} alcanzó el punto de reorden ({current_stock} unidades)',
                        severity='medium'
                    )
                    alerts_created += 1
            
            self.logger.info(f'Se crearon {alerts_created} alertas de stock')
            return alerts_created
            
        except Exception as e:
            self.logger.error(f'Error al verificar alertas de stock: {str(e)}')
            return 0
    
    def get_current_stock(self, product_id):
        """Calcula el stock actual de un producto"""
        try:
            # Sumar todas las entradas y restar todas las salidas
            entries = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'in'
            ).scalar() or 0
            
            exits = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'out'
            ).scalar() or 0
            
            adjustments = db.session.query(db.func.sum(InventoryRecord.quantity)).filter(
                InventoryRecord.product_id == product_id,
                InventoryRecord.movement_type == 'adjustment'
            ).scalar() or 0
            
            return entries - exits + adjustments
            
        except Exception as e:
            self.logger.error(f'Error al calcular stock del producto {product_id}: {str(e)}')
            return 0
    
    def create_alert(self, product_id, alert_type, message, severity='medium'):
        """Crea una nueva alerta"""
        try:
            # Verificar si ya existe una alerta similar sin resolver
            existing_alert = Alert.query.filter(
                Alert.product_id == product_id,
                Alert.alert_type == alert_type,
                Alert.is_resolved == False
            ).first()
            
            if not existing_alert:
                alert = Alert(
                    product_id=product_id,
                    alert_type=alert_type,
                    message=message,
                    severity=severity
                )
                
                db.session.add(alert)
                db.session.commit()
                
                # Enviar notificación por email si está configurado
                self.send_email_notification(alert)
                
                self.logger.info(f'Alerta creada: {message}')
                return alert
            
            return existing_alert
            
        except Exception as e:
            self.logger.error(f'Error al crear alerta: {str(e)}')
            db.session.rollback()
            return None
    
    def send_email_notification(self, alert):
        """Envía notificación por email de la alerta"""
        try:
            if not current_app.config.get('MAIL_USERNAME'):
                self.logger.warning('Email no configurado, saltando notificación')
                return
            
            product = alert.product
            subject = f'[ALERTA] {alert.alert_type.upper()} - {product.name}'
            
            body = f"""
            <h2>Alerta de Inventario</h2>
            <p><strong>Tipo:</strong> {alert.alert_type}</p>
            <p><strong>Producto:</strong> {product.name} (SKU: {product.sku})</p>
            <p><strong>Mensaje:</strong> {alert.message}</p>
            <p><strong>Severidad:</strong> {alert.severity}</p>
            <p><strong>Fecha:</strong> {alert.created_at.strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <p>Por favor, revise el inventario y tome las acciones necesarias.</p>
            """
            
            msg = Message(
                subject=subject,
                recipients=[current_app.config.get('ADMIN_EMAIL', 'admin@company.com')],
                html=body
            )
            
            mail.send(msg)
            self.logger.info(f'Notificación por email enviada para alerta {alert.id}')
            
        except Exception as e:
            self.logger.error(f'Error al enviar notificación por email: {str(e)}')
    
    def resolve_alert(self, alert_id):
        """Marca una alerta como resuelta"""
        try:
            alert = Alert.query.get(alert_id)
            if alert:
                alert.is_resolved = True
                alert.resolved_at = datetime.utcnow()
                db.session.commit()
                self.logger.info(f'Alerta {alert_id} marcada como resuelta')
                return True
            return False
            
        except Exception as e:
            self.logger.error(f'Error al resolver alerta {alert_id}: {str(e)}')
            db.session.rollback()
            return False
    
    def get_active_alerts(self, severity=None):
        """Obtiene alertas activas, opcionalmente filtradas por severidad"""
        try:
            query = Alert.query.filter(Alert.is_resolved == False)
            
            if severity:
                query = query.filter(Alert.severity == severity)
            
            return query.order_by(Alert.created_at.desc()).all()
            
        except Exception as e:
            self.logger.error(f'Error al obtener alertas activas: {str(e)}')
            return []
    
    def get_alert_statistics(self):
        """Obtiene estadísticas de alertas"""
        try:
            total_alerts = Alert.query.count()
            active_alerts = Alert.query.filter(Alert.is_resolved == False).count()
            resolved_alerts = Alert.query.filter(Alert.is_resolved == True).count()
            
            # Alertas por severidad
            critical_alerts = Alert.query.filter(
                Alert.is_resolved == False,
                Alert.severity == 'critical'
            ).count()
            
            high_alerts = Alert.query.filter(
                Alert.is_resolved == False,
                Alert.severity == 'high'
            ).count()
            
            medium_alerts = Alert.query.filter(
                Alert.is_resolved == False,
                Alert.severity == 'medium'
            ).count()
            
            low_alerts = Alert.query.filter(
                Alert.is_resolved == False,
                Alert.severity == 'low'
            ).count()
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'resolved_alerts': resolved_alerts,
                'critical_alerts': critical_alerts,
                'high_alerts': high_alerts,
                'medium_alerts': medium_alerts,
                'low_alerts': low_alerts
            }
            
        except Exception as e:
            self.logger.error(f'Error al obtener estadísticas de alertas: {str(e)}')
            return {}

# Instancia global del sistema de alertas
alert_system = AlertSystem()



