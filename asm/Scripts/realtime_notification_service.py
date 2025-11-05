from datetime import datetime
from flask import current_app
from app import db
from models import Alert, Product
from services.alert_service import alert_system
import logging
import json
from typing import Dict, List
import threading
import time

class RealTimeNotificationService:
    """Servicio de notificaciones en tiempo real"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.active_connections = {}
        self.notification_queue = []
        self.is_running = False
        
    def add_connection(self, user_id: str, websocket):
        """Añade una conexión WebSocket"""
        self.active_connections[user_id] = websocket
        self.logger.info(f'Conexión añadida para usuario {user_id}')
    
    def remove_connection(self, user_id: str):
        """Remueve una conexión WebSocket"""
        if user_id in self.active_connections:
            del self.active_connections[user_id]
            self.logger.info(f'Conexión removida para usuario {user_id}')
    
    def send_notification(self, user_id: str, notification: Dict):
        """Envía notificación a un usuario específico"""
        try:
            if user_id in self.active_connections:
                websocket = self.active_connections[user_id]
                websocket.send(json.dumps(notification))
                self.logger.info(f'Notificación enviada a usuario {user_id}')
                return True
            return False
        except Exception as e:
            self.logger.error(f'Error enviando notificación: {str(e)}')
            return False
    
    def broadcast_notification(self, notification: Dict, exclude_users: List[str] = None):
        """Envía notificación a todos los usuarios conectados"""
        exclude_users = exclude_users or []
        sent_count = 0
        
        for user_id in list(self.active_connections.keys()):
            if user_id not in exclude_users:
                if self.send_notification(user_id, notification):
                    sent_count += 1
        
        self.logger.info(f'Notificación broadcast enviada a {sent_count} usuarios')
        return sent_count
    
    def send_alert_notification(self, alert: Alert):
        """Envía notificación de alerta"""
        notification = {
            'type': 'alert',
            'title': f'Alerta: {alert.alert_type.replace("_", " ").title()}',
            'message': alert.message,
            'severity': alert.severity,
            'product_name': alert.product.name,
            'product_sku': alert.product.sku,
            'timestamp': datetime.utcnow().isoformat(),
            'alert_id': alert.id,
            'actions': [
                {'label': 'Ver Detalles', 'action': 'view_alert', 'alert_id': alert.id},
                {'label': 'Resolver', 'action': 'resolve_alert', 'alert_id': alert.id}
            ]
        }
        
        return self.broadcast_notification(notification)
    
    def send_inventory_update(self, product_id: int, old_stock: int, new_stock: int):
        """Envía notificación de actualización de inventario"""
        try:
            product = Product.query.get(product_id)
            if not product:
                return False
            
            notification = {
                'type': 'inventory_update',
                'title': 'Actualización de Inventario',
                'message': f'Stock de {product.name} cambió de {old_stock} a {new_stock}',
                'product_id': product_id,
                'product_name': product.name,
                'old_stock': old_stock,
                'new_stock': new_stock,
                'timestamp': datetime.utcnow().isoformat(),
                'severity': 'low' if new_stock > product.min_stock_level else 'medium'
            }
            
            return self.broadcast_notification(notification)
            
        except Exception as e:
            self.logger.error(f'Error enviando notificación de inventario: {str(e)}')
            return False
    
    def send_system_status(self, status: str, message: str):
        """Envía notificación de estado del sistema"""
        notification = {
            'type': 'system_status',
            'title': f'Estado del Sistema: {status.title()}',
            'message': message,
            'status': status,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'info'
        }
        
        return self.broadcast_notification(notification)
    
    def send_kpi_update(self, kpis: Dict):
        """Envía notificación de actualización de KPIs"""
        notification = {
            'type': 'kpi_update',
            'title': 'KPIs Actualizados',
            'message': 'Los indicadores clave han sido recalculados',
            'kpis': kpis,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'info'
        }
        
        return self.broadcast_notification(notification)
    
    def start_monitoring(self):
        """Inicia el monitoreo en tiempo real"""
        if self.is_running:
            return
        
        self.is_running = True
        monitor_thread = threading.Thread(target=self._monitor_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        self.logger.info('Monitoreo en tiempo real iniciado')
    
    def stop_monitoring(self):
        """Detiene el monitoreo en tiempo real"""
        self.is_running = False
        self.logger.info('Monitoreo en tiempo real detenido')
    
    def _monitor_loop(self):
        """Loop principal de monitoreo"""
        last_alert_count = 0
        last_kpi_update = datetime.utcnow()
        
        while self.is_running:
            try:
                with current_app.app_context():
                    # Monitorear nuevas alertas
                    current_alert_count = Alert.query.filter(Alert.is_resolved == False).count()
                    if current_alert_count > last_alert_count:
                        new_alerts = Alert.query.filter(
                            Alert.is_resolved == False,
                            Alert.created_at > datetime.utcnow() - timedelta(minutes=1)
                        ).all()
                        
                        for alert in new_alerts:
                            self.send_alert_notification(alert)
                        
                        last_alert_count = current_alert_count
                    
                    # Monitorear KPIs (cada 5 minutos)
                    if datetime.utcnow() - last_kpi_update > timedelta(minutes=5):
                        from services.kpi_service import kpi_service
                        kpis = kpi_service.calculate_all_kpis()
                        self.send_kpi_update(kpis)
                        last_kpi_update = datetime.utcnow()
                
                time.sleep(10)  # Verificar cada 10 segundos
                
            except Exception as e:
                self.logger.error(f'Error en loop de monitoreo: {str(e)}')
                time.sleep(30)  # Esperar más tiempo en caso de error
    
    def get_connection_stats(self) -> Dict:
        """Obtiene estadísticas de conexiones"""
        return {
            'active_connections': len(self.active_connections),
            'connected_users': list(self.active_connections.keys()),
            'is_monitoring': self.is_running,
            'queue_size': len(self.notification_queue)
        }

# Instancia global del servicio de notificaciones en tiempo real
realtime_notification_service = RealTimeNotificationService()



