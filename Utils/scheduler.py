import os
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from flask import current_app
from app import db
from models import Product, SalesRecord, Alert
from services.alert_service import alert_system
from utils.notifications import get_notification_service

logger = logging.getLogger(__name__)

scheduler = None

def _build_daily_summary():
    today = datetime.utcnow().date()

    # Ventas de hoy
    today_sales = SalesRecord.query.filter(
        db.func.date(SalesRecord.sale_date) == today
    ).all()

    revenue = sum(sale.total_amount for sale in today_sales)
    transactions = len(today_sales)

    # Productos con stock bajo
    low_stock_count = 0
    for product in Product.query.all():
        current_stock = alert_system.get_current_stock(product.id)
        if current_stock <= product.min_stock_level:
            low_stock_count += 1

    # Alertas
    active_alerts = Alert.query.filter(Alert.is_resolved == False).count()
    resolved_alerts = Alert.query.filter(
        Alert.is_resolved == True,
        Alert.resolved_at >= today
    ).count()

    return {
        'revenue': revenue,
        'transactions': transactions,
        'total_products': Product.query.count(),
        'low_stock': low_stock_count,
        'active_alerts': active_alerts,
        'resolved_alerts': resolved_alerts
    }

def _send_daily_summary_job():
    try:
        notification_service = get_notification_service()
        if not notification_service:
            logger.info('Servicio de notificaciones no disponible; se omite resumen diario')
            return
        from flask import current_app
        with current_app.app_context():
            summary = _build_daily_summary()
            sent = notification_service.send_daily_summary(summary)
            logger.info('Resumen diario enviado' if sent else 'No se pudo enviar resumen diario')
    except Exception as e:
        logger.error(f'Error en job de resumen diario: {e}')


def init_scheduler(app):
    global scheduler
    if scheduler is not None:
        return scheduler

    enabled = os.getenv('DAILY_SUMMARY_ENABLED', 'false').lower() in ['true', '1', 'yes']
    time_str = os.getenv('DAILY_SUMMARY_TIME', '08:00')  # HH:MM 24h

    if not enabled:
        logger.info('Scheduler diario deshabilitado (DAILY_SUMMARY_ENABLED=false)')
        return None

    hour, minute = 8, 0
    try:
        parts = time_str.split(':')
        hour = int(parts[0]); minute = int(parts[1])
    except Exception:
        logger.warning('Formato DAILY_SUMMARY_TIME inválido, usando 08:00 por defecto')

    scheduler = BackgroundScheduler(timezone='UTC')

    # Job diario a hora UTC indicada (si se desea hora local, ajustar)
    scheduler.add_job(
        func=lambda: app.app_context().push() or _send_daily_summary_job(),
        trigger='cron',
        hour=hour,
        minute=minute,
        id='daily_summary_job',
        replace_existing=True
    )

    scheduler.start()
    logger.info(f'Scheduler iniciado. Resumen diario a las {hour:02d}:{minute:02d} UTC')
    return scheduler

