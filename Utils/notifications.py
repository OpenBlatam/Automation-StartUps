"""
Sistema de notificaciones por email
"""
from flask_mail import Message
from flask import current_app
import logging
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, mail):
        self.mail = mail
        self.enabled = current_app.config.get('MAIL_ENABLED', False)
        self.smtp_server = current_app.config.get('MAIL_SERVER')
        self.smtp_port = current_app.config.get('MAIL_PORT', 587)
        self.username = current_app.config.get('MAIL_USERNAME')
        self.password = current_app.config.get('MAIL_PASSWORD')
        self.from_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        
    def send_email(self, to_emails, subject, html_content, text_content=None):
        """Envía email usando Flask-Mail"""
        if not self.enabled:
            logger.info(f"Email deshabilitado. No se envió: {subject}")
            return False
            
        try:
            msg = Message(
                subject=subject,
                sender=self.from_email,
                recipients=to_emails
            )
            msg.html = html_content
            if text_content:
                msg.body = text_content
            else:
                msg.body = html_content.replace('<br>', '\n').replace('<p>', '').replace('</p>', '\n')
            
            self.mail.send(msg)
            logger.info(f"Email enviado exitosamente a {to_emails}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}")
            return False
    
    def send_low_stock_alert(self, product, current_stock, min_stock):
        """Envía alerta de stock bajo"""
        subject = f"🚨 Alerta: Stock bajo - {product.name}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Alerta de Stock Bajo</h2>
            <p>El producto <strong>{product.name}</strong> (SKU: {product.sku}) tiene stock bajo.</p>
            
            <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 10px 0;">
                <h3>Detalles del Producto:</h3>
                <ul>
                    <li><strong>Nombre:</strong> {product.name}</li>
                    <li><strong>SKU:</strong> {product.sku}</li>
                    <li><strong>Categoría:</strong> {product.category}</li>
                    <li><strong>Stock Actual:</strong> {current_stock}</li>
                    <li><strong>Stock Mínimo:</strong> {min_stock}</li>
                    <li><strong>Diferencia:</strong> {current_stock - min_stock}</li>
                </ul>
            </div>
            
            <p><strong>Acción recomendada:</strong> Revisar y reabastecer el inventario.</p>
            
            <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        # Obtener emails de administradores
        admin_emails = self._get_admin_emails()
        if admin_emails:
            return self.send_email(admin_emails, subject, html_content)
        return False
    
    def send_out_of_stock_alert(self, product):
        """Envía alerta de producto agotado"""
        subject = f"🔴 URGENTE: Producto agotado - {product.name}"
        
        html_content = f"""
        <html>
        <body>
            <h2 style="color: #dc3545;">ALERTA URGENTE: Producto Agotado</h2>
            <p>El producto <strong>{product.name}</strong> (SKU: {product.sku}) está completamente agotado.</p>
            
            <div style="background-color: #f8d7da; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #dc3545;">
                <h3>Detalles del Producto:</h3>
                <ul>
                    <li><strong>Nombre:</strong> {product.name}</li>
                    <li><strong>SKU:</strong> {product.sku}</li>
                    <li><strong>Categoría:</strong> {product.category}</li>
                    <li><strong>Stock Actual:</strong> 0</li>
                    <li><strong>Stock Mínimo:</strong> {product.min_stock_level}</li>
                </ul>
            </div>
            
            <p><strong>Acción requerida:</strong> Reabastecer inmediatamente para evitar pérdida de ventas.</p>
            
            <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """
        
        admin_emails = self._get_admin_emails()
        if admin_emails:
            return self.send_email(admin_emails, subject, html_content)
        return False
    
    def send_reorder_recommendation(self, recommendations):
        """Envía recomendaciones de reorden"""
        subject = f"📋 Recomendaciones de Reorden - {len(recommendations)} productos"
        
        html_content = f"""
        <html>
        <body>
            <h2>Recomendaciones de Reorden</h2>
            <p>Se han generado {len(recommendations)} recomendaciones de reorden basadas en el análisis de demanda.</p>
            
            <table style="border-collapse: collapse; width: 100%; margin: 20px 0;">
                <thead>
                    <tr style="background-color: #f8f9fa;">
                        <th style="border: 1px solid #dee2e6; padding: 8px;">Producto</th>
                        <th style="border: 1px solid #dee2e6; padding: 8px;">SKU</th>
                        <th style="border: 1px solid #dee2e6; padding: 8px;">Stock Actual</th>
                        <th style="border: 1px solid #dee2e6; padding: 8px;">Cantidad Recomendada</th>
                        <th style="border: 1px solid #dee2e6; padding: 8px;">Urgencia</th>
                        <th style="border: 1px solid #dee2e6; padding: 8px;">Costo Estimado</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for rec in recommendations:
            urgency_color = "#dc3545" if rec.get('urgency') == 'high' else "#ffc107" if rec.get('urgency') == 'medium' else "#28a745"
            html_content += f"""
                    <tr>
                        <td style="border: 1px solid #dee2e6; padding: 8px;">{rec.get('product_name', 'N/A')}</td>
                        <td style="border: 1px solid #dee2e6; padding: 8px;">{rec.get('sku', 'N/A')}</td>
                        <td style="border: 1px solid #dee2e6; padding: 8px;">{rec.get('current_stock', 0)}</td>
                        <td style="border: 1px solid #dee2e6; padding: 8px;">{rec.get('recommended_quantity', 0)}</td>
                        <td style="border: 1px solid #dee2e6; padding: 8px; color: {urgency_color}; font-weight: bold;">{rec.get('urgency', 'N/A')}</td>
                        <td style="border: 1px solid #dee2e6; padding: 8px;">${rec.get('estimated_cost', 0):,.2f}</td>
                    </tr>
            """
        
        html_content += """
                </tbody>
            </table>
            
            <p>Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </body>
        </html>
        """.format(datetime=datetime)
        
        admin_emails = self._get_admin_emails()
        if admin_emails:
            return self.send_email(admin_emails, subject, html_content)
        return False
    
    def send_daily_summary(self, summary_data):
        """Envía resumen diario"""
        subject = f"📊 Resumen Diario - {datetime.now().strftime('%Y-%m-%d')}"
        
        html_content = f"""
        <html>
        <body>
            <h2>Resumen Diario del Sistema de Inventario</h2>
            <p>Fecha: {datetime.now().strftime('%Y-%m-%d')}</p>
            
            <div style="display: flex; gap: 20px; margin: 20px 0;">
                <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; flex: 1;">
                    <h3>Ventas</h3>
                    <p><strong>Ingresos:</strong> ${summary_data.get('revenue', 0):,.2f}</p>
                    <p><strong>Transacciones:</strong> {summary_data.get('transactions', 0)}</p>
                </div>
                <div style="background-color: #f3e5f5; padding: 15px; border-radius: 5px; flex: 1;">
                    <h3>Inventario</h3>
                    <p><strong>Productos:</strong> {summary_data.get('total_products', 0)}</p>
                    <p><strong>Stock Bajo:</strong> {summary_data.get('low_stock', 0)}</p>
                </div>
                <div style="background-color: #e8f5e8; padding: 15px; border-radius: 5px; flex: 1;">
                    <h3>Alertas</h3>
                    <p><strong>Activas:</strong> {summary_data.get('active_alerts', 0)}</p>
                    <p><strong>Resueltas:</strong> {summary_data.get('resolved_alerts', 0)}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        admin_emails = self._get_admin_emails()
        if admin_emails:
            return self.send_email(admin_emails, subject, html_content)
        return False
    
    def _get_admin_emails(self):
        """Obtiene emails de administradores"""
        # En producción, esto debería venir de la base de datos
        admin_emails = current_app.config.get('ADMIN_EMAILS', [])
        if not admin_emails:
            # Emails por defecto para desarrollo
            admin_emails = ['admin@inventory.com']
        return admin_emails
    
    def test_email_connection(self):
        """Prueba la conexión de email"""
        try:
            if not self.enabled:
                return False, "Email deshabilitado"
            
            # Crear mensaje de prueba
            msg = Message(
                subject="Test de Conexión - Sistema de Inventario",
                sender=self.from_email,
                recipients=self._get_admin_emails()
            )
            msg.body = "Este es un mensaje de prueba para verificar la configuración de email."
            
            self.mail.send(msg)
            return True, "Email enviado exitosamente"
        except Exception as e:
            return False, f"Error: {str(e)}"

# Instancia global del servicio
notification_service = None

def init_notification_service(mail):
    """Inicializa el servicio de notificaciones"""
    global notification_service
    notification_service = NotificationService(mail)
    return notification_service

def get_notification_service():
    """Obtiene la instancia del servicio de notificaciones"""
    return notification_service



