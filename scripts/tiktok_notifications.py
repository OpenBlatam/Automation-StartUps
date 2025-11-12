#!/usr/bin/env python3
"""
Sistema de notificaciones avanzado
Envía notificaciones a múltiples canales (Email, Slack, Telegram, etc.)
"""

import os
import json
import logging
import smtplib
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationManager:
    """Gestor de notificaciones multi-canal"""
    
    def __init__(self):
        """Inicializa el gestor de notificaciones"""
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        self.slack_webhook_url = os.getenv('SLACK_WEBHOOK_URL')
        self.email_smtp_server = os.getenv('EMAIL_SMTP_SERVER')
        self.email_smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_user = os.getenv('EMAIL_USER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_to = os.getenv('EMAIL_TO', '').split(',')
    
    def send_telegram(self, message: str, parse_mode: str = 'HTML') -> bool:
        """
        Envía notificación a Telegram
        
        Args:
            message: Mensaje a enviar
            parse_mode: Modo de parseo (HTML o Markdown)
            
        Returns:
            True si se envió exitosamente
        """
        if not self.telegram_bot_token or not self.telegram_chat_id:
            logger.warning("Telegram no configurado")
            return False
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            logger.info("Notificación enviada a Telegram")
            return True
        
        except Exception as e:
            logger.error(f"Error enviando a Telegram: {e}")
            return False
    
    def send_slack(self, message: str, channel: Optional[str] = None) -> bool:
        """
        Envía notificación a Slack
        
        Args:
            message: Mensaje a enviar
            channel: Canal de Slack (opcional)
            
        Returns:
            True si se envió exitosamente
        """
        if not self.slack_webhook_url:
            logger.warning("Slack no configurado")
            return False
        
        try:
            payload = {
                'text': message
            }
            
            if channel:
                payload['channel'] = channel
            
            response = requests.post(
                self.slack_webhook_url,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            
            logger.info("Notificación enviada a Slack")
            return True
        
        except Exception as e:
            logger.error(f"Error enviando a Slack: {e}")
            return False
    
    def send_email(self, subject: str, message: str, html: bool = False) -> bool:
        """
        Envía notificación por email
        
        Args:
            subject: Asunto del email
            message: Cuerpo del mensaje
            html: Si el mensaje es HTML
            
        Returns:
            True si se envió exitosamente
        """
        if not all([self.email_smtp_server, self.email_user, self.email_password]):
            logger.warning("Email no configurado")
            return False
        
        if not self.email_to:
            logger.warning("No hay destinatarios de email configurados")
            return False
        
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.email_user
            msg['To'] = ', '.join(self.email_to)
            
            if html:
                msg.attach(MIMEText(message, 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            
            with smtplib.SMTP(self.email_smtp_server, self.email_smtp_port) as server:
                server.starttls()
                server.login(self.email_user, self.email_password)
                server.send_message(msg)
            
            logger.info("Notificación enviada por email")
            return True
        
        except Exception as e:
            logger.error(f"Error enviando email: {e}")
            return False
    
    def notify_processing_started(self, url: str, job_id: Optional[int] = None):
        """Notifica inicio de procesamiento"""
        message = f"🎬 <b>Procesamiento Iniciado</b>\n\n"
        message += f"URL: {url}\n"
        if job_id:
            message += f"Job ID: {job_id}\n"
        message += f"Tiempo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram(message)
        self.send_slack(f"🎬 Procesamiento iniciado: {url}")
    
    def notify_processing_completed(self, url: str, result: Dict[str, Any], 
                                   job_id: Optional[int] = None):
        """Notifica completación de procesamiento"""
        processing_time = result.get('processing_time', 0)
        file_size_mb = result.get('file_size', 0) / (1024 * 1024)
        
        message = f"✅ <b>Procesamiento Completado</b>\n\n"
        message += f"URL: {url}\n"
        if job_id:
            message += f"Job ID: {job_id}\n"
        message += f"Tiempo: {processing_time:.1f}s\n"
        message += f"Tamaño: {file_size_mb:.2f} MB\n"
        message += f"Video: {result.get('video_path', 'N/A')}"
        
        self.send_telegram(message)
        self.send_slack(f"✅ Procesamiento completado: {url} ({processing_time:.1f}s)")
        
        # Email con más detalles
        email_subject = "TikTok Video Procesado Exitosamente"
        email_body = f"""
        <h2>Video Procesado Exitosamente</h2>
        <p><strong>URL:</strong> {url}</p>
        <p><strong>Tiempo de procesamiento:</strong> {processing_time:.1f} segundos</p>
        <p><strong>Tamaño del archivo:</strong> {file_size_mb:.2f} MB</p>
        <p><strong>Ruta del video:</strong> {result.get('video_path', 'N/A')}</p>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        self.send_email(email_subject, email_body, html=True)
    
    def notify_processing_failed(self, url: str, error: str, 
                                job_id: Optional[int] = None, retry_count: int = 0):
        """Notifica fallo en procesamiento"""
        message = f"❌ <b>Error en Procesamiento</b>\n\n"
        message += f"URL: {url}\n"
        if job_id:
            message += f"Job ID: {job_id}\n"
        if retry_count > 0:
            message += f"Reintento: {retry_count}\n"
        message += f"Error: {error}\n"
        message += f"Tiempo: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        self.send_telegram(message)
        self.send_slack(f"❌ Error procesando {url}: {error}")
        
        # Email de error
        email_subject = "Error en Procesamiento de TikTok Video"
        email_body = f"""
        <h2>Error en Procesamiento</h2>
        <p><strong>URL:</strong> {url}</p>
        <p><strong>Error:</strong> {error}</p>
        <p><strong>Reintentos:</strong> {retry_count}</p>
        <p><strong>Fecha:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        self.send_email(email_subject, email_body, html=True)
    
    def notify_queue_status(self, stats: Dict[str, Any]):
        """Notifica estado de la cola"""
        pending = stats.get('pending', 0)
        processing = stats.get('processing', 0)
        completed = stats.get('completed', 0)
        failed = stats.get('failed', 0)
        
        if pending > 10 or failed > 5:
            message = f"⚠️ <b>Estado de Cola</b>\n\n"
            message += f"Pendientes: {pending}\n"
            message += f"Procesando: {processing}\n"
            message += f"Completados: {completed}\n"
            message += f"Fallidos: {failed}"
            
            self.send_telegram(message)
            self.send_slack(f"⚠️ Cola: {pending} pendientes, {failed} fallidos")
    
    def notify_daily_summary(self, stats: Dict[str, Any]):
        """Envía resumen diario"""
        total = stats.get('total_processed', 0)
        successful = stats.get('successful', 0)
        failed = stats.get('failed', 0)
        success_rate = stats.get('success_rate', 0)
        avg_time = stats.get('avg_processing_time', 0)
        
        message = f"📊 <b>Resumen Diario</b>\n\n"
        message += f"Total procesados: {total}\n"
        message += f"Exitosos: {successful}\n"
        message += f"Fallidos: {failed}\n"
        message += f"Tasa de éxito: {success_rate:.1f}%\n"
        message += f"Tiempo promedio: {avg_time:.1f}s"
        
        self.send_telegram(message)
        self.send_slack(f"📊 Resumen diario: {total} videos, {success_rate:.1f}% éxito")
        
        # Email con reporte detallado
        email_subject = f"Resumen Diario - {datetime.now().strftime('%Y-%m-%d')}"
        email_body = f"""
        <h2>Resumen Diario de Procesamiento</h2>
        <table border="1" cellpadding="10">
            <tr><td><strong>Total Procesados</strong></td><td>{total}</td></tr>
            <tr><td><strong>Exitosos</strong></td><td>{successful}</td></tr>
            <tr><td><strong>Fallidos</strong></td><td>{failed}</td></tr>
            <tr><td><strong>Tasa de Éxito</strong></td><td>{success_rate:.1f}%</td></tr>
            <tr><td><strong>Tiempo Promedio</strong></td><td>{avg_time:.1f}s</td></tr>
        </table>
        """
        self.send_email(email_subject, email_body, html=True)


def main():
    """Ejemplo de uso"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Sistema de notificaciones')
    parser.add_argument('type', choices=['test', 'summary'], help='Tipo de notificación')
    parser.add_argument('--url', help='URL para test')
    
    args = parser.parse_args()
    
    manager = NotificationManager()
    
    if args.type == 'test':
        url = args.url or "https://www.tiktok.com/@test/video/123"
        manager.notify_processing_started(url)
        manager.notify_processing_completed(url, {
            'processing_time': 120.5,
            'file_size': 1024000,
            'video_path': '/tmp/video.mp4'
        })
    
    elif args.type == 'summary':
        from tiktok_analytics import TikTokAnalytics
        analytics = TikTokAnalytics()
        stats = analytics.get_stats(1)
        manager.notify_daily_summary(stats)


if __name__ == '__main__':
    main()


