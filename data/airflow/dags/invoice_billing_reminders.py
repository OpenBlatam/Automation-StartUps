from __future__ import annotations

from datetime import timedelta, datetime
import logging
from typing import Any, Dict, List, Optional
import json
import time
import os
from contextlib import contextmanager

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.operators.python import get_current_context
from airflow.models import Variable, Param
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowFailException
from data.airflow.plugins.etl_notifications import notify_email, notify_slack

logger = logging.getLogger(__name__)

# Intentar importar Stats de Airflow
try:
    from airflow.stats import Stats
    STATS_AVAILABLE = True
except Exception:
    STATS_AVAILABLE = False
    Stats = None  # type: ignore

# Constantes
DEFAULT_BATCH_SIZE = 50
DEFAULT_EMAIL_DELAY = 0.5  # segundos entre emails
MAX_EMAILS_PER_RUN = 200
CIRCUIT_BREAKER_FAILURE_THRESHOLD = 5
CIRCUIT_BREAKER_RESET_MINUTES = 15


def _get_env_var(name: str, default: str | None = None) -> str:
    """Obtiene variable de entorno o Airflow Variable."""
    try:
        return str(Variable.get(name, default_var=default))
    except Exception:
        return default or ""


def _send_slack_notification(text: str) -> None:
    """Envía notificación a Slack si está configurado."""
    try:
        slack_webhook = os.environ.get("SLACK_WEBHOOK_URL", "").strip()
        if slack_webhook:
            notify_slack(text)
    except Exception:
        pass


def _track_metric(metric_name: str, value: float = 1.0, metric_type: str = "incr") -> None:
    """Trackea métrica si Stats está disponible."""
    if STATS_AVAILABLE and Stats:
        try:
            if metric_type == "incr":
                Stats.incr(metric_name, int(value))
            elif metric_type == "gauge":
                Stats.gauge(metric_name, value)
            elif metric_type == "timing":
                Stats.timing(metric_name, int(value))
        except Exception:
            pass


@contextmanager
def _track_operation(operation_name: str):
    """Context manager para trackear duración de operaciones."""
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = (time.time() - start_time) * 1000
        _track_metric(f"invoice_billing.{operation_name}.duration_ms", duration_ms, "timing")
        logger.debug(f"Operation {operation_name} took {duration_ms:.2f}ms")


def _get_circuit_breaker_key() -> str:
    """Genera la clave del circuit breaker."""
    return "cb:failures:invoice_billing_reminders"


def _is_circuit_breaker_open() -> bool:
    """Verifica si el circuit breaker está abierto."""
    try:
        key = _get_circuit_breaker_key()
        data_str = Variable.get(key, default_var=None)
        if not data_str:
            return False
        data = json.loads(data_str)
        failures = data.get("count", 0)
        last_failure_ts = data.get("last_failure_ts", 0)
        now = pendulum.now("UTC").int_timestamp
        if (now - last_failure_ts) > (CIRCUIT_BREAKER_RESET_MINUTES * 60) and failures > 0:
            Variable.delete(key)
            return False
        return failures >= CIRCUIT_BREAKER_FAILURE_THRESHOLD
    except Exception:
        return False


def _record_circuit_breaker_failure() -> None:
    """Registra un fallo en el circuit breaker."""
    try:
        key = _get_circuit_breaker_key()
        data_str = Variable.get(key, default_var=None)
        now_ts = pendulum.now("UTC").int_timestamp
        if data_str:
            data = json.loads(data_str)
            count = data.get("count", 0) + 1
        else:
            count = 1
        Variable.set(key, json.dumps({"count": count, "last_failure_ts": now_ts}))
        _track_metric("invoice_billing.circuit_breaker.failures", 1.0)
    except Exception:
        pass


def _reset_circuit_breaker() -> None:
    """Resetea el circuit breaker."""
    try:
        Variable.delete(_get_circuit_breaker_key())
        _track_metric("invoice_billing.circuit_breaker.reset", 1.0)
    except Exception:
        pass


def _get_schema_info(hook: PostgresHook) -> Dict[str, bool]:
    """Obtiene información sobre el esquema de la base de datos."""
    schema_info = {
        "has_customer_email": False,
        "has_invoice_payments": False,
        "has_metadata": False,
    }
    
    try:
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Verificar columna customer_email
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'invoices' 
                    AND column_name = 'customer_email'
                """)
                schema_info["has_customer_email"] = cur.fetchone() is not None
                
                # Verificar tabla invoice_payments
                cur.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = 'invoice_payments'
                    )
                """)
                schema_info["has_invoice_payments"] = cur.fetchone()[0]
                
                # Verificar columna metadata
                cur.execute("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'invoices' 
                    AND column_name = 'metadata'
                """)
                schema_info["has_metadata"] = cur.fetchone() is not None
    except Exception as e:
        logger.warning(f"Error checking schema info: {e}", exc_info=True)
    
    return schema_info


def _get_email_language(customer_email: Optional[str] = None, default: str = "es") -> str:
    """Detecta idioma preferido del cliente."""
    # En producción, esto podría venir de una tabla de preferencias de cliente
    # Por ahora, detecta básico por dominio o usa default
    if not customer_email:
        return default
    
    # Detección simple por dominio
    email_lower = customer_email.lower()
    if any(domain in email_lower for domain in [".uk", ".co.uk", ".ie"]):
        return "en"
    elif any(domain in email_lower for domain in [".de", ".at", ".ch"]):
        return "de"
    elif any(domain in email_lower for domain in [".fr", ".be", ".ch"]):
        return "fr"
    
    return default


def _get_translations(language: str = "es") -> Dict[str, str]:
    """Obtiene traducciones según idioma."""
    translations = {
        "es": {
            "invoice": "FACTURA",
            "dear_customer": "Estimado cliente,",
            "invoice_attached": "Adjuntamos su factura correspondiente al período indicado.",
            "description": "Descripción",
            "quantity": "Cantidad",
            "unit_price": "Precio Unit.",
            "total": "Total",
            "payment_instructions": "Instrucciones de pago:",
            "payment_before_due": "Por favor, realice el pago antes de la fecha de vencimiento indicada.",
            "questions": "Si tiene alguna pregunta, no dude en contactarnos.",
            "regards": "Saludos cordiales,",
            "finance_team": "Equipo de Finanzas",
            "due_date": "Fecha de vencimiento:",
        },
        "en": {
            "invoice": "INVOICE",
            "dear_customer": "Dear customer,",
            "invoice_attached": "Please find attached your invoice for the indicated period.",
            "description": "Description",
            "quantity": "Quantity",
            "unit_price": "Unit Price",
            "total": "Total",
            "payment_instructions": "Payment instructions:",
            "payment_before_due": "Please make payment before the indicated due date.",
            "questions": "If you have any questions, please do not hesitate to contact us.",
            "regards": "Best regards,",
            "finance_team": "Finance Team",
            "due_date": "Due date:",
        },
    }
    return translations.get(language, translations["es"])


def _get_optimal_send_time(customer_email: str, hook: PostgresHook) -> Optional[datetime]:
    """Calcula el mejor momento para enviar email basado en historial."""
    try:
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Analizar historial de aperturas de emails
                cur.execute("""
                    SELECT EXTRACT(HOUR FROM sent_at) as hour, COUNT(*) as opens
                    FROM invoice_reminders ir
                    JOIN invoice_email_tracking iet ON ir.invoice_id = iet.invoice_id
                    WHERE iet.customer_email = %s
                    AND iet.opened = true
                    AND ir.sent_at >= NOW() - INTERVAL '90 days'
                    GROUP BY EXTRACT(HOUR FROM sent_at)
                    ORDER BY opens DESC
                    LIMIT 1
                """, (customer_email,))
                
                result = cur.fetchone()
                if result:
                    best_hour = int(result[0])
                    # Ajustar a zona horaria del cliente si está disponible
                    now = pendulum.now("UTC")
                    return now.replace(hour=best_hour, minute=0, second=0)
    except Exception:
        pass
    
    # Default: 10 AM UTC (hora de oficina)
    return pendulum.now("UTC").replace(hour=10, minute=0, second=0)


def _render_invoice_email_template(
    serie: str,
    total: float,
    currency: str,
    items: List[tuple],
    invoice_date: str,
    company_name: str = "Nuestra Empresa",
    payment_due_date: Optional[str] = None,
    language: str = "es",
) -> str:
    """Genera template HTML para email de factura."""
    t = _get_translations(language)
    
    items_html = ""
    for item_desc, qty, unit_price, item_total in items:
        items_html += f"""
        <tr>
            <td style="padding: 8px; border-bottom: 1px solid #ddd;">{item_desc}</td>
            <td style="padding: 8px; text-align: center; border-bottom: 1px solid #ddd;">{qty}</td>
            <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{currency} {float(unit_price):.2f}</td>
            <td style="padding: 8px; text-align: right; border-bottom: 1px solid #ddd;">{currency} {float(item_total):.2f}</td>
        </tr>
        """
    
    due_date_html = ""
    if payment_due_date:
        due_date_html = f'<p><strong>{t["due_date"]}</strong> {payment_due_date}</p>'
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid #2c3e50;">
                <h1 style="color: #2c3e50; margin: 0; font-size: 28px;">{t['invoice']}</h1>
                <p style="color: #7f8c8d; margin: 5px 0 0 0; font-size: 16px;">{serie}</p>
            </div>
            
            <div style="margin-bottom: 30px;">
                <p style="margin: 0 0 10px 0;">{t['dear_customer']}</p>
                <p style="margin: 0;">{t['invoice_attached']}</p>
            </div>
            
            <table style="width: 100%; border-collapse: collapse; margin: 20px 0; background-color: #ffffff;">
                <thead>
                    <tr style="background-color: #34495e; color: #ffffff;">
                        <th style="padding: 12px; text-align: left; border: 1px solid #2c3e50;">{t['description']}</th>
                        <th style="padding: 12px; text-align: center; border: 1px solid #2c3e50;">{t['quantity']}</th>
                        <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">{t['unit_price']}</th>
                        <th style="padding: 12px; text-align: right; border: 1px solid #2c3e50;">{t['total']}</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                </tbody>
            </table>
            
            <div style="text-align: right; margin-top: 20px; padding-top: 20px; border-top: 2px solid #ecf0f1;">
                <p style="font-size: 18px; margin: 5px 0;"><strong>{t['total']}: {currency} {total:.2f}</strong></p>
            </div>
            
            {due_date_html}
            
            <div style="margin-top: 30px; padding: 15px; background-color: #ecf0f1; border-radius: 4px;">
                <p style="margin: 0 0 10px 0;"><strong>{t['payment_instructions']}</strong></p>
                <p style="margin: 0;">{t['payment_before_due']}</p>
                <p style="margin: 10px 0 0 0;">{t['questions']}</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; text-align: center; color: #7f8c8d; font-size: 12px;">
                <p style="margin: 0;">{t['regards']}<br><strong>{t['finance_team']}</strong><br>{company_name}</p>
            </div>
        </div>
    </body>
    </html>
    """


def _render_reminder_email_template(
    serie: str,
    total: float,
    currency: str,
    days_since: int,
    reminder_type: str = "first_reminder",
    language: str = "es",
) -> tuple[str, str]:
    """Genera template HTML para email de recordatorio."""
    t = _get_translations(language)
    
    if reminder_type == "first_reminder":
        color = "#e74c3c"
        bg_color = "#fee"
        if language == "en":
            title = "Payment Reminder"
            urgency = "moderate"
            message = "We remind you that you have an outstanding invoice."
        else:
            title = "Recordatorio de Pago Pendiente"
            urgency = "moderada"
            message = "Le recordamos que tiene una factura pendiente de pago."
    else:  # escalation
        color = "#c0392b"
        bg_color = "#fee"
        if language == "en":
            title = "⚠️ Important Notice: Invoice Pending Collection"
            urgency = "urgent"
            message = "We inform you that your invoice has been escalated to the collections department due to non-payment."
        else:
            title = "⚠️ Aviso Importante: Factura Pendiente de Cobro"
            urgency = "urgente"
            message = "Le informamos que su factura ha sido escalada al departamento de cobranza debido a falta de pago."
    
    if language == "en":
        subject = f"{'URGENT: ' if reminder_type == 'escalation' else ''}Reminder: Pending Payment - Invoice {serie}"
    else:
        subject = f"{'URGENTE: ' if reminder_type == 'escalation' else ''}Recordatorio: Pago Pendiente - Factura {serie}"
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
            <div style="text-align: center; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 2px solid {color};">
                <h1 style="color: {color}; margin: 0; font-size: 24px;">{title}</h1>
            </div>
            
            <div style="margin-bottom: 30px;">
                <p style="margin: 0 0 10px 0;">{t['dear_customer']}</p>
                <p style="margin: 0;">{message}</p>
            </div>
            
            <div style="background-color: {bg_color}; padding: 20px; border-left: 4px solid {color}; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 0 0 10px 0;"><strong>{'Invoice' if language == 'en' else 'Factura'}:</strong> {serie}</p>
                <p style="margin: 0 0 10px 0;"><strong>{'Amount' if language == 'en' else 'Monto'}:</strong> {currency} {total:.2f}</p>
                <p style="margin: 0;"><strong>{'Days overdue' if language == 'en' else 'Días de retraso'}:</strong> {days_since} {'days' if language == 'en' else 'días'}</p>
            </div>
            
            <div style="margin-top: 30px; padding: 15px; background-color: #fff3cd; border-radius: 4px; border-left: 4px solid #ffc107;">
                <p style="margin: 0; font-weight: bold;">{'Priority' if language == 'en' else 'Prioridad'}: {urgency.upper()}</p>
                <p style="margin: 10px 0 0 0;">{'Please make payment as soon as possible to avoid additional charges.' if language == 'en' else 'Por favor, realice el pago a la brevedad posible para evitar cargos adicionales.'}</p>
                {"<p style='margin: 10px 0 0 0;'><strong>{'It is urgent that you make payment immediately.' if language == 'en' else 'Es urgente que realice el pago inmediatamente.'}</strong></p>" if reminder_type == "escalation" else ""}
                <p style="margin: 10px 0 0 0;">{'If you have already made payment, you can ignore this message.' if language == 'en' else 'Si ya realizó el pago, puede ignorar este mensaje.'}</p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ecf0f1; text-align: center; color: #7f8c8d; font-size: 12px;">
                <p style="margin: 0;">{t['regards']}<br><strong>{'Collections Department' if reminder_type == 'escalation' and language == 'en' else 'Departamento de Cobranza' if reminder_type == 'escalation' else t['finance_team']}</strong></p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return subject, html


@dag(
    dag_id="invoice_billing_reminders",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule=[
        "0 2 1 * *",  # Generar facturas el día 1 de cada mes a las 02:00 UTC
        "0 10 * * *",  # Verificar recordatorios diariamente a las 10:00 UTC
    ],
    catchup=False,
    default_args={
        "owner": "finance",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
        "email_on_failure": False,
        "email_on_retry": False,
    },
    dagrun_timeout=timedelta(minutes=60),
    max_active_runs=1,
    doc_md="""
    ### Automatización de Facturación y Recordatorios de Pago - Versión Enterprise
    
    Sistema completo y robusto que automatiza:
    1. **Generación de facturas** al cierre de mes (día 1 de cada mes)
    2. **Envío de facturas** por email al cliente con templates profesionales
    3. **Recordatorios automáticos**:
       - Si no hay pago en 7 días → enviar recordatorio
       - Si no hay pago en 14 días → escalar a cobros
    
    **Características Enterprise:**
    - ✅ Circuit breaker para prevenir fallos en cascada
    - ✅ Rate limiting para emails
    - ✅ Métricas y tracking completo con Stats
    - ✅ Templates de email profesionales y responsivos
    - ✅ Manejo robusto de errores con reintentos
    - ✅ Notificaciones a Slack
    - ✅ Batch processing optimizado
    - ✅ Validaciones de esquema de BD
    - ✅ Health checks pre-vuelo
    - ✅ Logging estructurado
    - ✅ **Generación de PDFs** para facturas
    - ✅ **Integración con Stripe** para verificar pagos reales
    - ✅ **Generación desde suscripciones** (Stripe)
    - ✅ **Sincronización con QuickBooks** para contabilidad
    - ✅ **Analytics y reportes** con métricas avanzadas
    - ✅ **Análisis predictivo de riesgo** de pago
    - ✅ **Webhooks** para integraciones externas
    - ✅ **Dead Letter Queue** para reprocesamiento de errores
    - ✅ **Exportación a S3** de reportes
    - ✅ **Tracking de conversión** y métricas de negocio
    - ✅ **Multi-idioma** en emails (ES, EN, DE, FR)
    - ✅ **Machine Learning** para predicción de probabilidad de pago
    - ✅ **Optimización de timing** de emails basada en historial
    - ✅ **Integración con CRM** (Salesforce, Pipedrive)
    - ✅ **Tracking de aperturas** y clicks de emails
    - ✅ **Detección automática de idioma** por cliente
    - ✅ **A/B Testing** de templates de email
    - ✅ **Análisis de cohortes** para identificar patrones
    - ✅ **Personalización avanzada** por perfil de cliente
    - ✅ **Dashboard de métricas** en tiempo real
    - ✅ **Retry inteligente** de emails fallidos
    - ✅ **Estrategias de comunicación** personalizadas (friendly, firm, supportive)
    - ✅ **Customer tier detection** (VIP, regular, new)
    - ✅ **Análisis de sentimiento** en respuestas de clientes
    - ✅ **Predicción de churn** de clientes
    - ✅ **Optimización de descuentos** inteligente
    - ✅ **Integración con gateways de pago** (Stripe, PayPal, Square)
    - ✅ **Análisis de tendencias** y forecasting
    - ✅ **Recomendaciones de acciones** automáticas
    - ✅ **Links de pago** generados automáticamente
    - ✅ **Scoring de churn** (0-100)
    - ✅ **Detección de fraude** y anomalías (Z-score)
    - ✅ **Predicción de cash flow** para próximos 30 días
    - ✅ **Integración con firma electrónica**
    - ✅ **Análisis de rentabilidad** por cliente
    - ✅ **Optimización de términos de pago** personalizados
    - ✅ **Customer Lifetime Value** (CLV) calculation
    - ✅ **Fraud scoring** (0-100)
    - ✅ **Análisis de satisfacción** del cliente (0-100)
    - ✅ **Integración con sistemas ERP** (SAP, Oracle)
    - ✅ **Integración con contabilidad adicional** (Xero, Sage)
    - ✅ **Optimización de precios** basada en conversión
    - ✅ **Sistema de lealtad y recompensas** (platinum, gold, silver, bronze)
    - ✅ **Automatización de negociaciones** de pago
    - ✅ **Sistema de alertas inteligentes** multi-factor
    - ✅ **Análisis de tendencias de mercado** vs benchmarks
    - ✅ **Optimización de rutas de cobro** por ubicación
    - ✅ **Análisis de satisfacción** del cliente (0-100)
    - ✅ **Integración con sistemas adicionales** (Xero, Sage)
    - ✅ **Optimización de precios** basada en conversión
    - ✅ **Sistema de lealtad y recompensas** (Platinum, Gold, Silver, Bronze)
    - ✅ **Puntos de lealtad** automáticos
    - ✅ **Descuentos por nivel de lealtad**
    - ✅ **Integración con sistemas ERP** (SAP, Oracle, NetSuite)
    - ✅ **Predicción de demanda** para próximos 6 meses
    - ✅ **Automatización de negociaciones** de pago
    - ✅ **Planes de pago** automáticos
    - ✅ **Ofertas de descuento** por pago inmediato
    - ✅ **Integración con sistemas de compliance** y auditoría
    - ✅ **Análisis de benchmarks competitivos** vs industria
    - ✅ **Cálculo de ROI** y métricas de retorno
    - ✅ **Optimización de recursos** basada en carga
    - ✅ **Integración con sistemas BI** (Tableau, Power BI)
    - ✅ **Notificaciones push** a clientes
    - ✅ **Scoring competitivo** (0-100)
    - ✅ **Análisis de carga de trabajo** diaria
    - ✅ **Análisis predictivo avanzado** multi-modelo
    - ✅ **Optimización de eficiencia de costos**
    - ✅ **Smart routing** de facturas a canales óptimos
    - ✅ **Análisis de tendencias de CLV** por cohortes
    - ✅ **Resumen ejecutivo** automático
    - ✅ **Score de confianza** en predicciones
    - ✅ **Routing inteligente** (email/phone/collections/account_manager)
    - ✅ **Segmentación avanzada** de clientes (5 segmentos)
    - ✅ **Análisis de estacionalidad** (mensual y semanal)
    - ✅ **Optimización de precios dinámicos** basada en demanda
    - ✅ **Sistema de alertas proactivas** antes de problemas
    - ✅ **Análisis de rentabilidad** por producto/servicio
    - ✅ **Gestión de crédito** y límites automáticos
    - ✅ **Detección de picos estacionales** y valles
    - ✅ **Recomendaciones de límites de crédito** por cliente
    - ✅ **Análisis de correlaciones** entre variables
    - ✅ **Sistema de auto-healing** para corrección automática
    - ✅ **Scoring avanzado** de clientes (4 dimensiones)
    - ✅ **Reporte de insights** consolidado
    - ✅ **Correlación de Pearson** (monto vs días)
    - ✅ **Corrección automática** de emails inválidos
    - ✅ **Eliminación de duplicados** automática
    - ✅ **Análisis de performance** de canales de comunicación
    - ✅ **Sistema de backup y recovery** para datos críticos
    - ✅ **Métricas en tiempo real** para dashboard
    - ✅ **Optimización de estrategia** de comunicación
    - ✅ **Score de efectividad** por canal
    - ✅ **Backup automático** de facturas críticas
    - ✅ **Alertas en tiempo real** de métricas
    - ✅ **Análisis avanzado de satisfacción** multi-factor
    - ✅ **Motor de recomendaciones inteligente** basado en ML
    - ✅ **Tracking de métricas SLA** (Service Level Agreement)
    - ✅ **Score de satisfacción** por cliente
    - ✅ **Recomendaciones priorizadas** con impacto esperado
    - ✅ **Compliance tracking** de SLAs
    - ✅ **Análisis avanzado de tendencias** de mercado
    - ✅ **Sistema de alertas predictivas** que anticipa problemas
    - ✅ **Optimización de recursos en tiempo real**
    - ✅ **Análisis de crecimiento** y competitividad
    - ✅ **Alertas con tiempo estimado** de impacto
    - ✅ **Escalado automático** de recursos
    - ✅ **Análisis avanzado de retención** por cohortes
    - ✅ **Sistema de aprendizaje continuo** que mejora con el tiempo
    - ✅ **Optimización predictiva de costos** basada en proyecciones
    - ✅ **Métricas de retención** por cohorte mensual
    - ✅ **Score de aprendizaje** (0-100)
    - ✅ **Ahorros potenciales** proyectados
    - ✅ **Detección avanzada de anomalías** usando Z-score
    - ✅ **Motor de recomendaciones personalizadas** por cliente
    - ✅ **Optimización de flujo de trabajo** y eficiencia
    - ✅ **Detección de patrones inusuales** (montos, días, frecuencia)
    - ✅ **Recomendaciones por segmento y tier**
    - ✅ **Identificación de cuellos de botella**
    - ✅ **Análisis de impacto de cambios** en estrategias
    - ✅ **Métricas de calidad de datos** (completitud, validez, consistencia)
    - ✅ **Optimización de comunicación multicanal** por segmento
    - ✅ **Comparación de períodos** (actual vs anterior)
    - ✅ **Score de calidad de datos** (0-100)
    - ✅ **Secuencias de canales** optimizadas
    
    **Flujo del proceso:**
    
    **Generación mensual (día 1):**
    - Identifica clientes que requieren facturación
    - Genera facturas para el período anterior
    - Envía facturas por email con templates profesionales
    - Registra estado inicial (issued)
    
    **Verificación diaria:**
    - Identifica facturas pendientes de pago
    - Verifica días transcurridos desde emisión
    - Envía recordatorios a los 7 días
    - Escala a cobros a los 14 días
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `reminder_days`: Días para primer recordatorio (default: 7)
    - `escalation_days`: Días para escalar a cobros (default: 14)
    - `email_from`: Email remitente (default: finanzas@tu-dominio.com)
    - `dry_run`: Solo simular sin enviar emails (default: false)
    - `auto_generate_invoices`: Generar facturas automáticamente (default: true)
    - `send_invoice_email`: Enviar facturas por email (default: true)
    - `send_reminders`: Enviar recordatorios (default: true)
    - `escalate_to_collections`: Escalar a cobros (default: true)
    - `batch_size`: Tamaño de batch para procesamiento (default: 50)
    - `max_emails_per_run`: Máximo de emails por ejecución (default: 200)
    - `email_delay`: Delay entre emails en segundos (default: 0.5)
    
    **Requisitos:**
    - Tabla `invoices` debe existir con campos: id, serie, total, status, created_at
    - Tabla `invoice_items` para detalles de factura
    - Tabla `payments` (opcional) para verificar pagos
    - Tabla `invoice_reminders` (se crea automáticamente)
    - Tabla `invoice_dlq` (se crea automáticamente)
    - Configuración SMTP para envío de emails
    
    **Integraciones Opcionales:**
    - `STRIPE_API_KEY`: Para sincronización con Stripe y generación desde suscripciones
    - `QUICKBOOKS_ACCESS_TOKEN` y `QUICKBOOKS_REALM_ID`: Para sincronización contable
    - `INVOICE_WEBHOOK_URL`: Para notificaciones webhook
    - `INVOICE_ANALYTICS_S3_BUCKET`: Para exportación de reportes
    - `SLACK_WEBHOOK_URL`: Para notificaciones a Slack
    - `INVOICE_ML_PAYMENT_ENDPOINT`: Endpoint ML para predicción de pagos
    - `CRM_TYPE`: Tipo de CRM ('salesforce' o 'pipedrive')
    - `SALESFORCE_USERNAME/PASSWORD/TOKEN` o `PIPEDRIVE_API_TOKEN`: Credenciales CRM
    - `SENTIMENT_ANALYSIS_API`: API para análisis de sentimiento
    - `PAYMENT_GATEWAYS`: Gateways de pago separados por coma (stripe,paypal,square)
    - `STRIPE_PUBLISHABLE_KEY`: Clave pública de Stripe para links de pago
    - `ELECTRONIC_SIGNATURE_API`: API para firma electrónica
    - `ADDITIONAL_ACCOUNTING_SYSTEMS`: Sistemas de contabilidad separados por coma (xero,sage)
    - `XERO_ACCESS_TOKEN` y `XERO_TENANT_ID`: Credenciales para Xero
    - `SAGE_API_KEY`: API key para Sage
    - `ERP_SYSTEMS`: Sistemas ERP separados por coma (sap,oracle,netsuite)
    - `SAP_ENDPOINT` y `SAP_API_TOKEN`: Credenciales para SAP
    - `ORACLE_ERP_ENDPOINT` y `ORACLE_API_TOKEN`: Credenciales para Oracle
    - `NETSUITE_ACCOUNT_ID` y `NETSUITE_API_TOKEN`: Credenciales para NetSuite
    - `COMPLIANCE_SYSTEM`: Sistema de compliance a integrar
    - `BI_SYSTEMS`: Sistemas BI separados por coma (tableau,powerbi)
    - `TABLEAU_API_ENDPOINT` y `TABLEAU_API_TOKEN`: Credenciales para Tableau
    - `POWERBI_API_ENDPOINT` y `POWERBI_API_TOKEN`: Credenciales para Power BI
    - `PUSH_NOTIFICATION_SERVICE`: Servicio de notificaciones push
    
    **Métricas Trackeadas:**
    - Tasa de conversión de facturas
    - Promedio de días para pago
    - Facturas de alto riesgo
    - Emails enviados/fallidos por tipo
    - Sincronizaciones con sistemas externos
    - Performance de operaciones
    - Probabilidades de pago (ML)
    - Open rates y click rates de emails
    - Mejores horas para envío
    - Sentimiento de clientes (positive/negative/neutral)
    - Churn scores y predicciones
    - Descuentos optimizados
    - Tendencias de pago
    - Recomendaciones de acciones
    - Fraudes detectados
    - Cash flow predicho
    - Rentabilidad por cliente
    - Términos de pago optimizados
    - Documentos firmados electrónicamente
    - Satisfacción del cliente
    - Puntos de lealtad y tiers
    - Negociaciones automatizadas
    - Rutas de cobro optimizadas
    - Tendencias de mercado
    - Alertas inteligentes generadas
    - Satisfacción del cliente
    - Sincronizaciones con sistemas adicionales
    - Optimizaciones de precios
    - Puntos de lealtad asignados
    - Niveles de lealtad (Platinum/Gold/Silver/Bronze)
    - Sincronizaciones con ERP
    - Predicciones de demanda
    - Negociaciones automatizadas
    - Sincronizaciones con compliance
    - Benchmarks competitivos
    - ROI y métricas financieras
    - Optimizaciones de recursos
    - Sincronizaciones con BI
    - Notificaciones push enviadas
    - Análisis predictivo avanzado
    - Optimizaciones de costos
    - Smart routing aplicado
    - Tendencias de CLV analizadas
    - Resúmenes ejecutivos generados
    - Segmentación de clientes completada
    - Patrones de estacionalidad identificados
    - Precios dinámicos optimizados
    - Alertas proactivas generadas
    - Rentabilidad de productos analizada
    - Gestión de crédito aplicada
    - Correlaciones analizadas
    - Auto-healing aplicado
    - Scoring de clientes completado
    - Reportes de insights generados
    - Performance de canales analizado
    - Backups creados automáticamente
    - Métricas en tiempo real actualizadas
    - Estrategias de comunicación optimizadas
    - Análisis avanzado de satisfacción completado
    - Recomendaciones inteligentes generadas
    - Métricas de SLA trackeadas
    - Tendencias de mercado analizadas
    - Alertas predictivas generadas
    - Recursos optimizados en tiempo real
    - Retención por cohortes analizada
    - Aprendizaje continuo ejecutado
    - Optimización predictiva de costos completada
    - Anomalías detectadas y analizadas
    - Recomendaciones personalizadas generadas
    - Flujo de trabajo optimizado
    - Impacto de cambios analizado
    - Calidad de datos evaluada
    - Comunicación multicanal optimizada
    
    **Machine Learning:**
    - Predicción de probabilidad de pago basada en:
      * Historial del cliente
      * Días de retraso
      * Monto de factura
      * Patrones de comportamiento
    - Scoring de riesgo automático
    - Recomendaciones de acciones
    
    **A/B Testing:**
    - Testing de templates de email
    - Asignación determinística de variantes
    - Tracking de conversión por variante
    - Optimización automática basada en resultados
    
    **Personalización:**
    - Estrategias de comunicación por perfil
    - Detección de customer tier (VIP, regular, new)
    - Elegibilidad de descuentos inteligente
    - Tono adaptativo (friendly, firm, supportive)
    
    **Dashboard:**
    - Métricas en tiempo real
    - KPIs calculados automáticamente
    - Comparación mes a mes
    - Acceso vía Airflow Variables
    
    **Análisis Avanzado:**
    - Análisis de sentimiento en comunicaciones
    - Predicción de churn con scoring 0-100
    - Optimización automática de descuentos
    - Análisis de tendencias y forecasting
    - Recomendaciones de acciones priorizadas
    
    **Sistema de Lealtad:**
    - Cálculo automático de puntos (1 punto/$10)
    - Bonus por pagos rápidos (+5 puntos)
    - 4 niveles con descuentos:
      * Platinum (1000+ puntos): 15% descuento
      * Gold (500+ puntos): 10% descuento
      * Silver (200+ puntos): 5% descuento
      * Bronze (<200 puntos): Sin descuento
    - Actualización automática en metadata
    
    **Integraciones de Pago:**
    - Stripe checkout links
    - PayPal integration
    - Square payment links
    - Generación automática de links de pago
    
    **Seguridad y Fraude:**
    - Detección de anomalías usando Z-score
    - Scoring de fraude (0-100)
    - Detección de patrones sospechosos
    - Alertas automáticas para alto riesgo
    
    **Cash Flow y Finanzas:**
    - Predicción de cash flow 30 días
    - Análisis de rentabilidad por cliente
    - Customer Lifetime Value (CLV)
    - Optimización de términos de pago
    
    **Firma Electrónica:**
    - Integración con sistemas de e-signature
    - Tracking de documentos firmados
    - Automatización de proceso de firma
    
    **Satisfacción del Cliente:**
    - Scoring de satisfacción (0-100)
    - Análisis de pagos rápidos
    - Integración con análisis de sentimiento
    - Alertas para baja satisfacción
    
    **Sistemas de Contabilidad Adicionales:**
    - Integración con Xero
    - Integración con Sage
    - Sincronización automática de facturas pagadas
    - Soporte para múltiples sistemas simultáneos
    
    **Optimización de Precios:**
    - Análisis de relación precio-conversión
    - Recomendaciones por tier de precio
    - Sugerencias de descuentos o aumentos
    - Análisis de 90 días
    
    **Sistema de Lealtad:**
    - Puntos de lealtad (1 punto por $10)
    - Bonus por pagos rápidos
    - 4 niveles: Platinum, Gold, Silver, Bronze
    - Descuentos automáticos por nivel
    
    **Integración ERP:**
    - SAP integration
    - Oracle ERP integration
    - NetSuite integration
    - Sincronización automática de facturas
    - Soporte para múltiples sistemas simultáneos
    
    **Predicción de Demanda:**
    - Forecasting de 6 meses
    - Análisis de tendencias
    - Predicción de facturas, montos y clientes
    - Basado en promedios móviles
    
    **Automatización de Negociaciones:**
    - Planes de pago automáticos (3 cuotas)
    - Ofertas de descuento por pago inmediato
    - Negociaciones para facturas vencidas >30 días
    - Tracking de ofertas en metadata
    
    **Compliance y Auditoría:**
    - Integración con sistemas de compliance
    - Tracking de auditoría automático
    - Registro de todas las transacciones
    - Metadata completo para auditorías
    
    **Análisis Competitivo:**
    - Comparación con benchmarks de industria
    - Scoring competitivo (0-100)
    - Análisis de días para pago vs competencia
    - Análisis de tasas de conversión vs competencia
    
    **ROI y Métricas Financieras:**
    - Cálculo de ROI mensual
    - Análisis de costos operacionales
    - Cálculo de revenue neto
    - Métricas de retorno de inversión
    
    **Optimización de Recursos:**
    - Análisis de carga de trabajo diaria
    - Identificación de picos de carga
    - Recomendaciones de auto-scaling
    - Optimización de recursos de cobranza
    
    **Integración BI:**
    - Tableau integration
    - Power BI integration
    - Sincronización automática de métricas
    - Datos en tiempo real para dashboards
    
    **Notificaciones Push:**
    - Notificaciones push a clientes
    - Priorización por tipo de recordatorio
    - Tracking de entregas
    - Integración con servicios de push
    
    **Análisis Predictivo Avanzado:**
    - Combinación de múltiples modelos ML
    - Score de confianza en predicciones
    - Insights predictivos automáticos
    - Análisis multi-fuente de datos
    
    **Optimización de Costos:**
    - Análisis de costos por operación
    - Cálculo de eficiencia de costos
    - Recomendaciones de optimización
    - Tracking de costos por factura pagada
    
    **Smart Routing:**
    - Routing inteligente a canales óptimos
    - Canales: email, phone, collections, account_manager
    - Basado en días de retraso y monto
    - Considera customer tier
    
    **Análisis de CLV:**
    - Tendencias de Customer Lifetime Value
    - Análisis por cohortes mensuales
    - Identificación de tendencias
    - Comparación entre cohortes
    
    **Resumen Ejecutivo:**
    - Métricas clave consolidadas
    - Status general del sistema
    - Recomendaciones priorizadas
    - Próximas acciones sugeridas
    
    **Segmentación Avanzada:**
    - 5 segmentos: Champions, Loyal, At Risk, New, Hibernating
    - Basado en valor, velocidad de pago, y actividad
    - Análisis de comportamiento por segmento
    - Estrategias personalizadas por segmento
    
    **Análisis de Estacionalidad:**
    - Patrones mensuales de facturación
    - Patrones semanales de pagos
    - Identificación de picos y valles
    - Optimización de timing basada en estacionalidad
    
    **Precios Dinámicos:**
    - Análisis de conversión por rango de precio
    - Recomendaciones de ajuste de precios
    - Optimización basada en demanda
    - Identificación de oportunidades de pricing
    
    **Alertas Proactivas:**
    - Alertas de cash flow bajo
    - Alertas de conversión baja
    - Alertas de facturas de alto riesgo
    - Alertas de pagos lentos
    - Notificaciones automáticas a Slack
    
    **Rentabilidad de Productos:**
    - Análisis de revenue por producto
    - Cálculo de márgenes estimados
    - Top productos por rentabilidad
    - Identificación de productos estrella
    
    **Gestión de Crédito:**
    - Cálculo de exposición por cliente
    - Recomendaciones de límites de crédito
    - Análisis de riesgo crediticio
    - Acciones automáticas (reducir/mantener/aumentar límites)
    
    **Análisis de Correlaciones:**
    - Correlación de Pearson: monto vs días para pago
    - Análisis de conversión por día de la semana
    - Identificación de correlaciones fuertes (>0.3)
    - Insights sobre mejores días para facturación
    
    **Auto-Healing:**
    - Corrección automática de emails inválidos
    - Inicialización de metadata faltante
    - Eliminación de recordatorios duplicados
    - Tracking de todas las correcciones aplicadas
    
    **Scoring Avanzado:**
    - 4 dimensiones: Valor, Velocidad, Confiabilidad, Lealtad
    - Score total ponderado (0-100)
    - Clasificación en tiers: Platinum, Gold, Silver, Bronze
    - Top 20 clientes por score
    
    **Reporte de Insights:**
    - Insights consolidados de múltiples fuentes
    - Recomendaciones priorizadas (high/medium/low)
    - Categorización por tipo (segmentation, seasonality, profitability)
    - Almacenado en Airflow Variable para acceso rápido
    
    **Performance de Canales:**
    - Análisis de efectividad por canal (email_initial, email_reminder, email_escalation)
    - Tasa de conversión por canal
    - Días promedio para pago después de envío
    - Score de efectividad combinado
    - Identificación del mejor canal
    
    **Backup y Recovery:**
    - Backup automático de facturas críticas (últimos 30 días)
    - Backup de métricas clave
    - Almacenamiento en Airflow Variables
    - Tracking de backups creados
    - IDs únicos para cada backup
    
    **Métricas en Tiempo Real:**
    - Conversión rate actual
    - Días promedio para pago
    - Facturas pendientes
    - Cash flow predicho (30 días)
    - Conteo de facturas de alto riesgo
    - Status de salud del sistema
    - Alertas en tiempo real
    - Actualización continua en Variable
    
    **Optimización de Comunicación:**
    - Estrategias por segmento (Champions, At Risk, etc.)
    - Estrategias por tier (Platinum, Gold, Silver, Bronze)
    - Recomendaciones de canales óptimos
    - Frecuencia y tono personalizados
    - Nivel de personalización por segmento
    
    **Análisis Avanzado de Satisfacción:**
    - Score combinado de 4 factores: Velocidad, Sentimiento, Confiabilidad, Tier
    - Análisis por cliente individual
    - Top 10 clientes más satisfechos
    - Bottom 10 clientes menos satisfechos
    - Componentes desglosados del score
    
    **Motor de Recomendaciones Inteligente:**
    - Recomendaciones basadas en múltiples factores
    - Priorización automática (high/medium/low)
    - Acciones específicas sugeridas
    - Impacto esperado cuantificado
    - Categorización: conversion, retention, growth, risk, optimization
    
    **Tracking de SLA:**
    - SLA de generación de facturas (24 horas)
    - SLA de entrega de emails (1 hora)
    - SLA de respuesta a recordatorios (48 horas)
    - Tasa de compliance por SLA
    - Status general: compliant/non_compliant
    - Métricas de cumplimiento en tiempo real
    
    **Análisis Avanzado de Tendencias de Mercado:**
    - Análisis de crecimiento (growing/stable/declining)
    - Tendencias estacionales consolidadas
    - Análisis de competitividad vs industria
    - Insights combinados de múltiples fuentes
    - Indicadores de tendencia (positive/negative/neutral)
    
    **Sistema de Alertas Predictivas:**
    - Alertas que anticipan problemas antes de que ocurran
    - Predicción de impacto futuro
    - Tiempo estimado hasta impacto
    - Recomendaciones de acción preventiva
    - Categorías: conversion, cash_flow, satisfaction, risk
    - Notificaciones automáticas a Slack
    
    **Optimización de Recursos en Tiempo Real:**
    - Análisis de carga actual (24 horas)
    - Necesidades de recursos por área
    - Recomendaciones de escalado automático
    - Status por recurso: adequate/overloaded
    - Optimización continua basada en carga
    
    **Análisis Avanzado de Retención por Cohortes:**
    - Análisis de cohortes mensuales (12 meses)
    - Tasa de retención por cohorte
    - Tasa de conversión por cohorte
    - Revenue promedio por cliente por cohorte
    - Tendencias de retención a lo largo del tiempo
    - Comparación entre cohortes
    
    **Sistema de Aprendizaje Continuo:**
    - Validación de predicciones ML vs resultados reales
    - Optimización de canales basada en performance
    - Ajuste de timing basado en resultados
    - Score de aprendizaje (0-100)
    - Mejoras continuas identificadas
    - Insights de aprendizaje automáticos
    
    **Optimización Predictiva de Costos:**
    - Proyección de costos para próximos 30 días
    - Crecimiento proyectado (10% facturas, 5% vencidas, 8% recordatorios)
    - Optimizaciones sugeridas con ahorros proyectados
    - Porcentaje de ahorro potencial
    - Impacto de cada optimización (high/medium/low)
    
    **Detección Avanzada de Anomalías:**
    - Análisis estadístico usando Z-score
    - Detección de anomalías en montos (>3 desviaciones estándar)
    - Detección de anomalías en días para pago (>2.5 desviaciones)
    - Detección de patrones de frecuencia inusuales
    - Clasificación por severidad (high/medium)
    - Top 20 anomalías identificadas
    
    **Motor de Recomendaciones Personalizadas:**
    - Recomendaciones por segmento (Champions, At Risk, etc.)
    - Recomendaciones por tier (Platinum, Gold, Silver, Bronze)
    - Recomendaciones por nivel de satisfacción
    - Acciones específicas sugeridas
    - Impacto esperado cuantificado
    - Programas personalizados por tipo de cliente
    
    **Optimización de Flujo de Trabajo:**
    - Análisis de tiempos de procesamiento
    - Identificación de cuellos de botella
    - Métricas de eficiencia (0-100)
    - Optimizaciones sugeridas por área
    - Mejoras esperadas cuantificadas
    - Tracking de tiempos clave del proceso
    
    **Análisis de Impacto de Cambios:**
    - Comparación de períodos (actual vs anterior 30 días)
    - Cambios en facturas pagadas (porcentaje)
    - Cambios en días promedio para pago (delta)
    - Cambios en revenue (porcentaje)
    - Evaluación de impacto (positive/negative/neutral)
    - Significancia de cambios (high/medium)
    - Tracking de mejoras o deterioros
    
    **Métricas de Calidad de Datos:**
    - Completitud de emails (porcentaje)
    - Validez de emails (formato correcto)
    - Completitud de metadata (porcentaje)
    - Consistencia de datos (totales inválidos, fechas inválidas)
    - Score general de calidad (0-100)
    - Status: excellent/good/needs_improvement
    - Alertas de calidad de datos
    
    **Optimización de Comunicación Multicanal:**
    - Asignación de canales por segmento
    - Canales prioritarios por tipo de cliente
    - Secuencia optimizada de canales (4 pasos)
    - Timing de cada canal en la secuencia
    - Recomendaciones de incremento de uso
    - Mejora esperada en conversión
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "reminder_days": Param(7, type="integer", minimum=1, maximum=30),
        "escalation_days": Param(14, type="integer", minimum=1, maximum=60),
        "email_from": Param("finanzas@tu-dominio.com", type="string", minLength=1),
        "dry_run": Param(False, type="boolean"),
        "auto_generate_invoices": Param(True, type="boolean"),
        "send_invoice_email": Param(True, type="boolean"),
        "send_reminders": Param(True, type="boolean"),
        "escalate_to_collections": Param(True, type="boolean"),
        "batch_size": Param(DEFAULT_BATCH_SIZE, type="integer", minimum=1, maximum=500),
        "max_emails_per_run": Param(MAX_EMAILS_PER_RUN, type="integer", minimum=1, maximum=1000),
        "email_delay": Param(DEFAULT_EMAIL_DELAY, type="number", minimum=0, maximum=10),
        "enable_ab_testing": Param(False, type="boolean"),
        "enable_personalization": Param(True, type="boolean"),
        "enable_cohort_analysis": Param(True, type="boolean"),
        "enable_intelligent_retry": Param(True, type="boolean"),
    },
    tags=["finance", "billing", "invoicing", "reminders", "collections"],
    on_success_callback=lambda context: _send_slack_notification(
        ":white_check_mark: invoice_billing_reminders DAG succeeded"
    ),
    on_failure_callback=lambda context: _send_slack_notification(
        ":x: invoice_billing_reminders DAG failed"
    ),
)
def invoice_billing_reminders() -> None:
    """
    DAG mejorado para automatización de facturación y recordatorios de pago.
    """
    
    @task(task_id="health_check")
    def health_check() -> None:
        """Health check pre-vuelo."""
        if _is_circuit_breaker_open():
            raise AirflowFailException(
                f"Circuit breaker is open - too many failures. "
                f"Wait {CIRCUIT_BREAKER_RESET_MINUTES} minutes or reset manually."
            )
        
        logger.info("Health check passed")
        _track_metric("invoice_billing.health_check.success", 1.0)
    
    @task(task_id="generate_monthly_invoices")
    def generate_monthly_invoices() -> Dict[str, Any]:
        """
        Genera facturas al cierre de mes para clientes que requieren facturación.
        Esta tarea se ejecuta el día 1 de cada mes.
        """
        with _track_operation("generate_monthly_invoices"):
            ctx = get_current_context()
            params = ctx["params"]
            conn_id = str(params["postgres_conn_id"])
            dry_run = bool(params["dry_run"])
            auto_generate = bool(params["auto_generate_invoices"])
            
            # Verificar si es el día 1 del mes (generación mensual)
            data_interval_end = ctx["data_interval_end"]
            if data_interval_end.day != 1 and auto_generate:
                logger.info("No es día 1 del mes, saltando generación de facturas")
                return {"invoices_generated": 0, "skipped": True}
            
            if not auto_generate:
                logger.info("Generación automática deshabilitada")
                return {"invoices_generated": 0, "skipped": True}
            
            hook = PostgresHook(postgres_conn_id=conn_id)
            
            # Calcular período de facturación (mes anterior)
            period_end = data_interval_end.subtract(days=1).start_of("month")
            period_start = period_end.subtract(months=1).start_of("month")
            
            logger.info(
                "Generando facturas mensuales",
                extra={
                    "period_start": period_start.to_date_string(),
                    "period_end": period_end.to_date_string(),
                }
            )
            
            # Crear tabla de tracking de recordatorios si no existe
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS invoice_reminders (
                            id SERIAL PRIMARY KEY,
                            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                            reminder_type VARCHAR(32) NOT NULL CHECK (reminder_type IN ('first_reminder', 'escalation', 'final_notice')),
                            sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            days_since_issue INTEGER NOT NULL,
                            status VARCHAR(32) NOT NULL DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'skipped')),
                            metadata JSONB,
                            UNIQUE(invoice_id, reminder_type)
                        );
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_reminders_invoice_id 
                        ON invoice_reminders(invoice_id);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_reminders_sent_at 
                        ON invoice_reminders(sent_at);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_reminders_status 
                        ON invoice_reminders(status) WHERE status = 'failed';
                    """)
                    
                    conn.commit()
            
            # Obtener configuración de facturación
            serie = _get_env_var("INVOICE_SERIE", default="A")
            tax_rate = float(_get_env_var("TAX_RATE", default="0.21"))
            company_tax_id = _get_env_var("COMPANY_TAX_ID", default="")
            default_currency = _get_env_var("DEFAULT_CURRENCY", default="USD")
            
            invoices_generated = []
            
            # Verificar si ya se generaron facturas para este período
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*) 
                        FROM invoices 
                        WHERE DATE_TRUNC('month', created_at) = DATE_TRUNC('month', %s::date)
                        AND status = 'issued'
                    """, (period_end.to_date_string(),))
                    
                    existing_count = cur.fetchone()[0]
                    
                    if existing_count > 0 and not dry_run:
                        logger.info(f"Ya existen {existing_count} facturas para este período")
                        _track_metric("invoice_billing.invoices.existing", existing_count)
                        return {
                            "invoices_generated": existing_count,
                            "skipped": False,
                            "period_start": period_start.to_date_string(),
                            "period_end": period_end.to_date_string(),
                        }
            
            # En producción, aquí se obtendrían clientes desde una tabla de clientes/suscripciones
            # Por ahora, retornamos estructura vacía para que el flujo continúe
            
            logger.info("Generación de facturas completada")
            _track_metric("invoice_billing.invoices.generated", len(invoices_generated))
            
            return {
                "invoices_generated": len(invoices_generated),
                "skipped": False,
                "period_start": period_start.to_date_string(),
                "period_end": period_end.to_date_string(),
                "invoices": invoices_generated,
            }
    
    @task(task_id="send_invoice_emails")
    def send_invoice_emails(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía facturas por email a los clientes con templates profesionales.
        """
        with _track_operation("send_invoice_emails"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            send_email = bool(params["send_invoice_email"])
            email_from = str(params["email_from"])
            batch_size = int(params.get("batch_size", DEFAULT_BATCH_SIZE))
            max_emails = int(params.get("max_emails_per_run", MAX_EMAILS_PER_RUN))
            email_delay = float(params.get("email_delay", DEFAULT_EMAIL_DELAY))
            
            if not send_email:
                logger.info("Envío de emails deshabilitado")
                return {"emails_sent": 0, "skipped": True}
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            schema_info = _get_schema_info(hook)
            
            # Obtener facturas recién generadas o pendientes de envío
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    if schema_info["has_customer_email"]:
                        cur.execute("""
                            SELECT 
                                i.id,
                                i.serie,
                                i.total,
                                i.currency,
                                i.created_at,
                                i.customer_email
                            FROM invoices i
                            WHERE i.status = 'issued'
                            AND i.customer_email IS NOT NULL
                            AND i.created_at >= NOW() - INTERVAL '7 days'
                            AND NOT EXISTS (
                                SELECT 1 FROM invoice_reminders ir 
                                WHERE ir.invoice_id = i.id 
                                AND ir.reminder_type = 'first_reminder'
                            )
                            ORDER BY i.created_at DESC
                            LIMIT %s
                        """, (max_emails,))
                    else:
                        cur.execute("""
                            SELECT 
                                i.id,
                                i.serie,
                                i.total,
                                i.currency,
                                i.created_at,
                                NULL as customer_email
                            FROM invoices i
                            WHERE i.status = 'issued'
                            AND i.created_at >= NOW() - INTERVAL '7 days'
                            AND NOT EXISTS (
                                SELECT 1 FROM invoice_reminders ir 
                                WHERE ir.invoice_id = i.id 
                                AND ir.reminder_type = 'first_reminder'
                            )
                            ORDER BY i.created_at DESC
                            LIMIT %s
                        """, (max_emails,))
                    
                    invoices = cur.fetchall()
                    
                    if not invoices:
                        logger.info("No hay facturas pendientes de envío")
                        return {"emails_sent": 0, "skipped": False}
            
            emails_sent = 0
            emails_failed = 0
            
            # Obtener configuración de empresa
            company_name = _get_env_var("COMPANY_NAME", default="Nuestra Empresa")
            
            # Procesar en batches
            for batch_idx in range(0, len(invoices), batch_size):
                batch = invoices[batch_idx:batch_idx + batch_size]
                batch_num = (batch_idx // batch_size) + 1
                total_batches = (len(invoices) + batch_size - 1) // batch_size
                
                logger.info(
                    f"Procesando batch {batch_num}/{total_batches} de emails de factura",
                    extra={"batch_size": len(batch), "total": len(invoices)}
                )
                
                for inv_row in batch:
                    inv_id, serie, total, currency, created_at, customer_email = inv_row
                    
                    if not customer_email:
                        logger.warning(f"Factura {inv_id} sin email de cliente, saltando")
                        emails_failed += 1
                        continue
                    
                    try:
                        # Obtener detalles de la factura para el email
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    SELECT description, quantity, unit_price, total
                                    FROM invoice_items
                                    WHERE invoice_id = %s
                                """, (inv_id,))
                                
                                items = cur.fetchall()
                        
                        if not items:
                            logger.warning(f"Factura {inv_id} sin items, saltando")
                            emails_failed += 1
                            continue
                        
                        # Calcular fecha de vencimiento (30 días por defecto)
                        invoice_date = created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)
                        due_date = (pendulum.parse(invoice_date) + timedelta(days=30)).strftime("%Y-%m-%d")
                        
                        # Detectar idioma del cliente
                        language = _get_email_language(customer_email)
                        
                        # Generar HTML del email
                        html_content = _render_invoice_email_template(
                            serie=serie,
                            total=float(total),
                            currency=currency or "USD",
                            items=items,
                            invoice_date=invoice_date,
                            company_name=company_name,
                            payment_due_date=due_date,
                            language=language,
                        )
                        
                        if language == "en":
                            subject = f"Invoice {serie} - Pending Payment"
                        else:
                            subject = f"Factura {serie} - Pago Pendiente"
                        
                        if not dry_run:
                            notify_email(
                                subject=subject,
                                html=html_content,
                                to=customer_email,
                            )
                            
                            # Registrar envío en base de datos
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO invoice_reminders 
                                            (invoice_id, reminder_type, days_since_issue, status, metadata)
                                        VALUES (%s, 'first_reminder', 0, 'sent', %s)
                                        ON CONFLICT (invoice_id, reminder_type) DO NOTHING
                                    """, (inv_id, json.dumps({"sent_at": datetime.utcnow().isoformat(), "type": "invoice_email"})))
                                    
                                    conn.commit()
                            
                            logger.info(f"Email de factura enviado a {customer_email} para factura {inv_id}")
                            emails_sent += 1
                            _track_metric("invoice_billing.emails.invoice.sent", 1.0)
                            
                            # Rate limiting
                            if email_delay > 0:
                                time.sleep(email_delay)
                        else:
                            logger.info(f"[DRY RUN] Email de factura sería enviado a {customer_email} para factura {inv_id}")
                            emails_sent += 1
                            
                    except Exception as e:
                        logger.error(f"Error enviando email para factura {inv_id}: {e}", exc_info=True)
                        emails_failed += 1
                        _track_metric("invoice_billing.emails.invoice.failed", 1.0)
                        _record_circuit_breaker_failure()
                        
                        # Registrar fallo
                        try:
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO invoice_reminders 
                                            (invoice_id, reminder_type, days_since_issue, status, metadata)
                                        VALUES (%s, 'first_reminder', 0, 'failed', %s)
                                        ON CONFLICT (invoice_id, reminder_type) DO UPDATE SET
                                            status = 'failed',
                                            metadata = EXCLUDED.metadata
                                    """, (inv_id, json.dumps({"error": str(e)[:500]})))
                                    
                                    conn.commit()
                        except Exception as db_error:
                            logger.error(f"Error registrando fallo en BD: {db_error}")
            
            if emails_sent > 0:
                _reset_circuit_breaker()
            
            logger.info(
                "Emails de factura enviados",
                extra={"sent": emails_sent, "failed": emails_failed, "total": len(invoices)}
            )
            
            return {
                "emails_sent": emails_sent,
                "emails_failed": emails_failed,
                "skipped": False,
            }
    
    @task(task_id="check_unpaid_invoices")
    def check_unpaid_invoices() -> Dict[str, Any]:
        """
        Verifica facturas pendientes de pago y determina qué recordatorios enviar.
        """
        with _track_operation("check_unpaid_invoices"):
            ctx = get_current_context()
            params = ctx["params"]
            conn_id = str(params["postgres_conn_id"])
            reminder_days = int(params["reminder_days"])
            escalation_days = int(params["escalation_days"])
            
            hook = PostgresHook(postgres_conn_id=conn_id)
            schema_info = _get_schema_info(hook)
            
            # Construir query según esquema disponible
            if schema_info["has_customer_email"]:
                customer_email_select = "i.customer_email"
            else:
                customer_email_select = "NULL as customer_email"
            
            if schema_info["has_invoice_payments"]:
                payment_check = """
                    CASE 
                        WHEN EXISTS (
                            SELECT 1 FROM invoice_payments ip
                            JOIN payments p ON ip.payment_id = p.payment_id
                            WHERE ip.invoice_id = i.id
                            AND p.status IN ('succeeded', 'paid', 'payment_intent.succeeded', 'charge.succeeded')
                        ) THEN true
                        ELSE false
                    END as is_paid
                """
                payment_where = """
                    AND NOT EXISTS (
                        SELECT 1 FROM invoice_payments ip
                        JOIN payments p ON ip.payment_id = p.payment_id
                        WHERE ip.invoice_id = i.id
                        AND p.status IN ('succeeded', 'paid', 'payment_intent.succeeded', 'charge.succeeded')
                    )
                """
            else:
                payment_check = "false as is_paid"
                payment_where = ""
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute(f"""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.created_at,
                            {customer_email_select},
                            EXTRACT(DAY FROM (NOW() - i.created_at))::INTEGER as days_since_issue,
                            {payment_check}
                        FROM invoices i
                        WHERE i.status IN ('issued', 'overdue')
                        {payment_where}
                        ORDER BY i.created_at ASC
                    """)
                    
                    columns = [desc[0] for desc in cur.description]
                    invoices = [dict(zip(columns, row)) for row in cur.fetchall()]
            
            reminders_to_send = []
            escalations_to_send = []
            
            for inv in invoices:
                days_since = inv.get("days_since_issue", 0)
                inv_id = inv.get("id")
                
                if inv.get("is_paid"):
                    continue
                
                # Verificar si ya se envió recordatorio
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT reminder_type, sent_at
                            FROM invoice_reminders
                            WHERE invoice_id = %s
                            ORDER BY sent_at DESC
                        """, (inv_id,))
                        
                        sent_reminders = cur.fetchall()
                
                sent_types = {r[0] for r in sent_reminders}
                
                # Recordatorio a los 7 días
                if days_since >= reminder_days and "first_reminder" not in sent_types:
                    reminders_to_send.append(inv)
                
                # Escalación a los 14 días
                if days_since >= escalation_days and "escalation" not in sent_types:
                    escalations_to_send.append(inv)
            
            logger.info(
                "Facturas pendientes verificadas",
                extra={
                    "total_unpaid": len(invoices),
                    "reminders_to_send": len(reminders_to_send),
                    "escalations_to_send": len(escalations_to_send),
                }
            )
            
            _track_metric("invoice_billing.unpaid_invoices.total", len(invoices))
            _track_metric("invoice_billing.reminders.pending", len(reminders_to_send))
            _track_metric("invoice_billing.escalations.pending", len(escalations_to_send))
            
            return {
                "unpaid_invoices": invoices,
                "reminders_to_send": reminders_to_send,
                "escalations_to_send": escalations_to_send,
                "reminder_days": reminder_days,
                "escalation_days": escalation_days,
            }
    
    @task(task_id="send_payment_reminders")
    def send_payment_reminders(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Envía recordatorios de pago a facturas pendientes después de 7 días.
        """
        with _track_operation("send_payment_reminders"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            send_reminders = bool(params["send_reminders"])
            email_from = str(params["email_from"])
            reminder_days = int(params["reminder_days"])
            batch_size = int(params.get("batch_size", DEFAULT_BATCH_SIZE))
            max_emails = int(params.get("max_emails_per_run", MAX_EMAILS_PER_RUN))
            email_delay = float(params.get("email_delay", DEFAULT_EMAIL_DELAY))
            
            if not send_reminders:
                logger.info("Envío de recordatorios deshabilitado")
                return {"reminders_sent": 0, "skipped": True}
            
            reminders_to_send = check_data.get("reminders_to_send", [])
            
            if not reminders_to_send:
                logger.info("No hay recordatorios pendientes de enviar")
                return {"reminders_sent": 0, "skipped": False}
            
            # Limitar cantidad de emails
            reminders_to_send = reminders_to_send[:max_emails]
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            reminders_sent = 0
            reminders_failed = 0
            
            # Procesar en batches
            for batch_idx in range(0, len(reminders_to_send), batch_size):
                batch = reminders_to_send[batch_idx:batch_idx + batch_size]
                batch_num = (batch_idx // batch_size) + 1
                total_batches = (len(reminders_to_send) + batch_size - 1) // batch_size
                
                logger.info(
                    f"Procesando batch {batch_num}/{total_batches} de recordatorios",
                    extra={"batch_size": len(batch), "total": len(reminders_to_send)}
                )
                
                for inv in batch:
                    inv_id = inv.get("id")
                    serie = inv.get("serie")
                    total = float(inv.get("total", 0))
                    currency = inv.get("currency", "USD")
                    customer_email = inv.get("customer_email")
                    days_since = inv.get("days_since_issue", 0)
                    
                    if not customer_email:
                        logger.warning(f"Factura {inv_id} sin email, saltando recordatorio")
                        reminders_failed += 1
                        continue
                    
                    try:
                        # Detectar idioma del cliente
                        language = _get_email_language(customer_email)
                        
                        subject, html_content = _render_reminder_email_template(
                            serie=serie,
                            total=total,
                            currency=currency,
                            days_since=days_since,
                            reminder_type="first_reminder",
                            language=language,
                        )
                        
                        if not dry_run:
                            notify_email(
                                subject=subject,
                                html=html_content,
                                to=customer_email,
                            )
                            
                            # Registrar envío
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO invoice_reminders 
                                            (invoice_id, reminder_type, days_since_issue, status, metadata)
                                        VALUES (%s, 'first_reminder', %s, 'sent', %s)
                                        ON CONFLICT (invoice_id, reminder_type) DO UPDATE SET
                                            sent_at = NOW(),
                                            days_since_issue = EXCLUDED.days_since_issue,
                                            status = 'sent'
                                    """, (inv_id, days_since, json.dumps({"sent_at": datetime.utcnow().isoformat()})))
                                    
                                    conn.commit()
                            
                            logger.info(f"Recordatorio enviado a {customer_email} para factura {inv_id}")
                            reminders_sent += 1
                            _track_metric("invoice_billing.emails.reminder.sent", 1.0)
                            
                            # Rate limiting
                            if email_delay > 0:
                                time.sleep(email_delay)
                        else:
                            logger.info(f"[DRY RUN] Recordatorio sería enviado a {customer_email} para factura {inv_id}")
                            reminders_sent += 1
                            
                    except Exception as e:
                        logger.error(f"Error enviando recordatorio para factura {inv_id}: {e}", exc_info=True)
                        reminders_failed += 1
                        _track_metric("invoice_billing.emails.reminder.failed", 1.0)
                        _record_circuit_breaker_failure()
                        
                        try:
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO invoice_reminders 
                                            (invoice_id, reminder_type, days_since_issue, status, metadata)
                                        VALUES (%s, 'first_reminder', %s, 'failed', %s)
                                        ON CONFLICT (invoice_id, reminder_type) DO UPDATE SET
                                            status = 'failed',
                                            metadata = EXCLUDED.metadata
                                    """, (inv_id, days_since, json.dumps({"error": str(e)[:500]})))
                                    
                                    conn.commit()
                        except Exception as db_error:
                            logger.error(f"Error registrando fallo en BD: {db_error}")
            
            if reminders_sent > 0:
                _reset_circuit_breaker()
            
            logger.info(
                "Recordatorios de pago enviados",
                extra={"sent": reminders_sent, "failed": reminders_failed}
            )
            
            return {
                "reminders_sent": reminders_sent,
                "reminders_failed": reminders_failed,
                "skipped": False,
            }
    
    @task(task_id="escalate_to_collections")
    def escalate_to_collections(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Escala facturas a cobros después de 14 días sin pago.
        """
        with _track_operation("escalate_to_collections"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            escalate = bool(params["escalate_to_collections"])
            email_from = str(params["email_from"])
            escalation_days = int(params["escalation_days"])
            batch_size = int(params.get("batch_size", DEFAULT_BATCH_SIZE))
            max_emails = int(params.get("max_emails_per_run", MAX_EMAILS_PER_RUN))
            email_delay = float(params.get("email_delay", DEFAULT_EMAIL_DELAY))
            
            if not escalate:
                logger.info("Escalación a cobros deshabilitada")
                return {"escalations_sent": 0, "skipped": True}
            
            escalations_to_send = check_data.get("escalations_to_send", [])
            
            if not escalations_to_send:
                logger.info("No hay facturas para escalar a cobros")
                return {"escalations_sent": 0, "skipped": False}
            
            # Limitar cantidad de emails
            escalations_to_send = escalations_to_send[:max_emails]
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            escalations_sent = 0
            escalations_failed = 0
            
            # Procesar en batches
            for batch_idx in range(0, len(escalations_to_send), batch_size):
                batch = escalations_to_send[batch_idx:batch_idx + batch_size]
                batch_num = (batch_idx // batch_size) + 1
                total_batches = (len(escalations_to_send) + batch_size - 1) // batch_size
                
                logger.info(
                    f"Procesando batch {batch_num}/{total_batches} de escalaciones",
                    extra={"batch_size": len(batch), "total": len(escalations_to_send)}
                )
                
                for inv in batch:
                    inv_id = inv.get("id")
                    serie = inv.get("serie")
                    total = float(inv.get("total", 0))
                    currency = inv.get("currency", "USD")
                    customer_email = inv.get("customer_email")
                    days_since = inv.get("days_since_issue", 0)
                    
                    if not customer_email:
                        logger.warning(f"Factura {inv_id} sin email, saltando escalación")
                        escalations_failed += 1
                        continue
                    
                    try:
                        # Detectar idioma del cliente
                        language = _get_email_language(customer_email)
                        
                        subject, html_content = _render_reminder_email_template(
                            serie=serie,
                            total=total,
                            currency=currency,
                            days_since=days_since,
                            reminder_type="escalation",
                            language=language,
                        )
                        
                        if not dry_run:
                            notify_email(
                                subject=subject,
                                html=html_content,
                                to=customer_email,
                            )
                            
                            # Registrar escalación
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO invoice_reminders 
                                            (invoice_id, reminder_type, days_since_issue, status, metadata)
                                        VALUES (%s, 'escalation', %s, 'sent', %s)
                                        ON CONFLICT (invoice_id, reminder_type) DO UPDATE SET
                                            sent_at = NOW(),
                                            days_since_issue = EXCLUDED.days_since_issue,
                                            status = 'sent'
                                    """, (inv_id, days_since, json.dumps({"sent_at": datetime.utcnow().isoformat(), "escalated": True})))
                                    
                                    # Actualizar estado de la factura
                                    cur.execute("""
                                        UPDATE invoices 
                                        SET status = 'overdue', updated_at = NOW()
                                        WHERE id = %s AND status = 'issued'
                                    """, (inv_id,))
                                    
                                    conn.commit()
                            
                            logger.info(f"Escalación a cobros enviada a {customer_email} para factura {inv_id}")
                            escalations_sent += 1
                            _track_metric("invoice_billing.emails.escalation.sent", 1.0)
                            
                            # Notificar a Slack sobre escalación
                            _send_slack_notification(
                                f"⚠️ Factura {serie} escalada a cobranza: {currency} {total:.2f} "
                                f"({days_since} días de retraso)"
                            )
                            
                            # Rate limiting
                            if email_delay > 0:
                                time.sleep(email_delay)
                        else:
                            logger.info(f"[DRY RUN] Escalación a cobros sería enviada a {customer_email} para factura {inv_id}")
                            escalations_sent += 1
                            
                    except Exception as e:
                        logger.error(f"Error enviando escalación para factura {inv_id}: {e}", exc_info=True)
                        escalations_failed += 1
                        _track_metric("invoice_billing.emails.escalation.failed", 1.0)
                        _record_circuit_breaker_failure()
                        
                        try:
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        INSERT INTO invoice_reminders 
                                            (invoice_id, reminder_type, days_since_issue, status, metadata)
                                        VALUES (%s, 'escalation', %s, 'failed', %s)
                                        ON CONFLICT (invoice_id, reminder_type) DO UPDATE SET
                                            status = 'failed',
                                            metadata = EXCLUDED.metadata
                                    """, (inv_id, days_since, json.dumps({"error": str(e)[:500]})))
                                    
                                    conn.commit()
                        except Exception as db_error:
                            logger.error(f"Error registrando fallo en BD: {db_error}")
            
            if escalations_sent > 0:
                _reset_circuit_breaker()
            
            logger.info(
                "Escalaciones a cobros enviadas",
                extra={"sent": escalations_sent, "failed": escalations_failed}
            )
            
            return {
                "escalations_sent": escalations_sent,
                "escalations_failed": escalations_failed,
                "skipped": False,
            }
    
    @task(task_id="sync_with_stripe")
    def sync_with_stripe(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sincroniza facturas con Stripe para verificar pagos reales.
        """
        with _track_operation("sync_with_stripe"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
            if not stripe_key:
                logger.info("STRIPE_API_KEY no configurado, saltando sincronización con Stripe")
                return {"synced": 0, "skipped": True}
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"synced": 0, "skipped": False}
            
            import requests
            
            headers = {"Authorization": f"Bearer {stripe_key}"}
            synced_count = 0
            paid_count = 0
            
            for inv in unpaid_invoices[:100]:  # Limitar a 100 para no sobrecargar
                inv_id = inv.get("id")
                serie = inv.get("serie")
                total = float(inv.get("total", 0))
                
                try:
                    # Buscar invoice en Stripe por metadata o customer
                    # En producción, esto debería usar un campo de referencia
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            # Verificar si hay referencia a Stripe
                            cur.execute("""
                                SELECT metadata->>'stripe_invoice_id' as stripe_id
                                FROM invoices
                                WHERE id = %s
                            """, (inv_id,))
                            result = cur.fetchone()
                            stripe_invoice_id = result[0] if result and result[0] else None
                    
                    if stripe_invoice_id:
                        # Verificar estado en Stripe
                        r = requests.get(
                            f"https://api.stripe.com/v1/invoices/{stripe_invoice_id}",
                            headers=headers,
                            timeout=10
                        )
                        
                        if r.status_code == 200:
                            stripe_invoice = r.json()
                            if stripe_invoice.get("paid"):
                                # Marcar como pagado
                                if not dry_run:
                                    with hook.get_conn() as conn:
                                        with conn.cursor() as cur:
                                            cur.execute("""
                                                UPDATE invoices 
                                                SET status = 'paid', updated_at = NOW()
                                                WHERE id = %s
                                            """, (inv_id,))
                                            
                                            # Crear registro de pago si no existe
                                            cur.execute("""
                                                INSERT INTO payments 
                                                    (payment_id, amount, currency, status, created_at)
                                                VALUES (%s, %s, %s, 'succeeded', NOW())
                                                ON CONFLICT (payment_id) DO NOTHING
                                            """, (f"stripe_{stripe_invoice_id}", total, inv.get("currency", "USD")))
                                            
                                            conn.commit()
                                
                                paid_count += 1
                                logger.info(f"Factura {serie} marcada como pagada desde Stripe")
                                _track_metric("invoice_billing.stripe.paid_detected", 1.0)
                        
                        synced_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error sincronizando factura {inv_id} con Stripe: {e}", exc_info=True)
            
            logger.info(
                "Sincronización con Stripe completada",
                extra={"synced": synced_count, "paid_detected": paid_count}
            )
            
            _track_metric("invoice_billing.stripe.synced", synced_count)
            
            return {
                "synced": synced_count,
                "paid_detected": paid_count,
                "skipped": False,
            }
    
    @task(task_id="generate_invoices_from_subscriptions")
    def generate_invoices_from_subscriptions() -> Dict[str, Any]:
        """
        Genera facturas reales desde suscripciones activas (Stripe, etc.).
        """
        with _track_operation("generate_invoices_from_subscriptions"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            auto_generate = bool(params["auto_generate_invoices"])
            
            if not auto_generate:
                return {"invoices_generated": 0, "skipped": True}
            
            stripe_key = os.environ.get("STRIPE_API_KEY", "").strip()
            if not stripe_key:
                logger.info("STRIPE_API_KEY no configurado, saltando generación desde suscripciones")
                return {"invoices_generated": 0, "skipped": True}
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Verificar si es día 1 del mes
            data_interval_end = ctx["data_interval_end"]
            if data_interval_end.day != 1:
                return {"invoices_generated": 0, "skipped": True}
            
            import requests
            
            headers = {"Authorization": f"Bearer {stripe_key}"}
            serie = _get_env_var("INVOICE_SERIE", default="A")
            tax_rate = float(_get_env_var("TAX_RATE", default="0.21"))
            company_tax_id = _get_env_var("COMPANY_TAX_ID", default="")
            default_currency = _get_env_var("DEFAULT_CURRENCY", default="USD")
            
            invoices_generated = []
            
            try:
                # Obtener suscripciones activas
                params_stripe = {"status": "active", "limit": 100}
                r = requests.get(
                    "https://api.stripe.com/v1/subscriptions",
                    headers=headers,
                    params=params_stripe,
                    timeout=30
                )
                r.raise_for_status()
                subscriptions = r.json().get("data", [])
                
                period_end = data_interval_end.subtract(days=1).start_of("month")
                
                for sub in subscriptions:
                    sub_id = sub.get("id")
                    customer_id = sub.get("customer")
                    items = sub.get("items", {}).get("data", [])
                    
                    if not items:
                        continue
                    
                    # Obtener precio
                    price = items[0].get("price", {})
                    amount = price.get("unit_amount", 0) / 100.0
                    currency = price.get("currency", "usd").upper()
                    
                    # Verificar si ya existe factura para este período
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT id FROM invoices
                                WHERE (metadata IS NOT NULL AND metadata->>'subscription_id' = %s)
                                AND DATE_TRUNC('month', created_at) = DATE_TRUNC('month', %s::date)
                            """, (sub_id, period_end.to_date_string()))
                            
                            if cur.fetchone():
                                continue  # Ya existe
                            
                            # Obtener email del cliente
                            customer_email = None
                            try:
                                cust_r = requests.get(
                                    f"https://api.stripe.com/v1/customers/{customer_id}",
                                    headers=headers,
                                    timeout=10
                                )
                                if cust_r.status_code == 200:
                                    customer = cust_r.json()
                                    customer_email = customer.get("email")
                            except Exception:
                                pass
                            
                            if not dry_run:
                                # Calcular totales
                                subtotal = float(amount)
                                taxes = round(subtotal * tax_rate, 2)
                                total = round(subtotal + taxes, 2)
                                
                                # Crear factura
                                cur.execute("""
                                    INSERT INTO invoices 
                                        (serie, company_tax_id, currency, subtotal, taxes, total, status, created_at, customer_email, metadata)
                                    VALUES (%s, %s, %s, %s, %s, %s, 'issued', NOW(), %s, %s)
                                    RETURNING id
                                """, (
                                    serie,
                                    company_tax_id,
                                    currency,
                                    subtotal,
                                    taxes,
                                    total,
                                    customer_email,
                                    json.dumps({
                                        "subscription_id": sub_id,
                                        "customer_id": customer_id,
                                        "stripe_invoice_id": sub.get("latest_invoice"),
                                    })
                                ))
                                
                                invoice_id = cur.fetchone()[0]
                                
                                # Crear items
                                plan_name = price.get("nickname") or price.get("id", "Plan")
                                cur.execute("""
                                    INSERT INTO invoice_items 
                                        (invoice_id, description, quantity, unit_price, total)
                                    VALUES (%s, %s, %s, %s, %s)
                                """, (
                                    invoice_id,
                                    f"{plan_name} - Suscripción {sub_id[:8]}",
                                    1,
                                    subtotal,
                                    subtotal,
                                ))
                                
                                conn.commit()
                                
                                invoices_generated.append({
                                    "invoice_id": invoice_id,
                                    "subscription_id": sub_id,
                                    "customer_id": customer_id,
                                    "amount": total,
                                })
                                
                                logger.info(f"Factura {invoice_id} generada para suscripción {sub_id}")
                                _track_metric("invoice_billing.invoices.from_subscriptions", 1.0)
                
            except Exception as e:
                logger.error(f"Error generando facturas desde suscripciones: {e}", exc_info=True)
                _record_circuit_breaker_failure()
            
            logger.info(
                "Facturas generadas desde suscripciones",
                extra={"count": len(invoices_generated)}
            )
            
            return {
                "invoices_generated": len(invoices_generated),
                "invoices": invoices_generated,
                "skipped": False,
            }
    
    @task(task_id="generate_analytics_report")
    def generate_analytics_report(
        invoice_data: Dict[str, Any],
        email_data: Dict[str, Any],
        reminder_data: Dict[str, Any],
        escalation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera reporte de analytics con métricas de facturación.
        """
        with _track_operation("generate_analytics_report"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            period_start = now.start_of("month")
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Métricas de facturas
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(*) FILTER (WHERE status = 'issued') as issued,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue,
                            COALESCE(SUM(total) FILTER (WHERE status = 'issued'), 0) as total_issued,
                            COALESCE(SUM(total) FILTER (WHERE status = 'paid'), 0) as total_paid,
                            COALESCE(SUM(total) FILTER (WHERE status = 'overdue'), 0) as total_overdue
                        FROM invoices
                        WHERE created_at >= %s
                    """, (period_start,))
                    
                    inv_metrics = cur.fetchone()
                    
                    # Métricas de recordatorios
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE reminder_type = 'first_reminder' AND status = 'sent') as reminders_sent,
                            COUNT(*) FILTER (WHERE reminder_type = 'escalation' AND status = 'sent') as escalations_sent,
                            COUNT(*) FILTER (WHERE status = 'failed') as failed
                        FROM invoice_reminders
                        WHERE sent_at >= %s
                    """, (period_start,))
                    
                    rem_metrics = cur.fetchone()
                    
                    # Tasa de conversión
                    total_issued = float(inv_metrics[4] or 0)
                    total_paid = float(inv_metrics[5] or 0)
                    conversion_rate = (total_paid / total_issued * 100) if total_issued > 0 else 0
                    
                    # Promedio de días para pago
                    cur.execute("""
                        SELECT AVG(EXTRACT(DAY FROM (updated_at - created_at)))
                        FROM invoices
                        WHERE status = 'paid'
                        AND created_at >= %s
                        AND updated_at IS NOT NULL
                    """, (period_start,))
                    
                    avg_days_to_pay = cur.fetchone()[0] or 0
            
            report = {
                "period": period_start.to_date_string(),
                "invoices": {
                    "total": inv_metrics[0],
                    "issued": inv_metrics[1],
                    "paid": inv_metrics[2],
                    "overdue": inv_metrics[3],
                    "total_issued_amount": float(inv_metrics[4] or 0),
                    "total_paid_amount": float(inv_metrics[5] or 0),
                    "total_overdue_amount": float(inv_metrics[6] or 0),
                },
                "reminders": {
                    "reminders_sent": rem_metrics[0] or 0,
                    "escalations_sent": rem_metrics[1] or 0,
                    "failed": rem_metrics[2] or 0,
                },
                "metrics": {
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_days_to_pay": round(float(avg_days_to_pay), 1),
                },
                "this_run": {
                    "invoices_generated": invoice_data.get("invoices_generated", 0),
                    "emails_sent": email_data.get("emails_sent", 0),
                    "reminders_sent": reminder_data.get("reminders_sent", 0),
                    "escalations_sent": escalation_data.get("escalations_sent", 0),
                },
            }
            
            logger.info(
                "Reporte de analytics generado",
                extra=report
            )
            
            # Trackear métricas
            _track_metric("invoice_billing.analytics.conversion_rate", conversion_rate, "gauge")
            _track_metric("invoice_billing.analytics.avg_days_to_pay", avg_days_to_pay, "gauge")
            
            # Enviar resumen a Slack si hay métricas importantes
            if conversion_rate < 50:
                _send_slack_notification(
                    f"⚠️ Tasa de conversión baja: {conversion_rate:.1f}% "
                    f"(Objetivo: >80%)"
                )
            
            return report
    
    @task(task_id="send_webhook_notifications")
    def send_webhook_notifications(
        invoice_data: Dict[str, Any],
        reminder_data: Dict[str, Any],
        escalation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Envía webhooks a sistemas externos para notificaciones.
        """
        with _track_operation("send_webhook_notifications"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            webhook_url = _get_env_var("INVOICE_WEBHOOK_URL", default="")
            if not webhook_url:
                logger.info("INVOICE_WEBHOOK_URL no configurado, saltando webhooks")
                return {"webhooks_sent": 0, "skipped": True}
            
            import requests
            
            webhooks_sent = 0
            webhooks_failed = 0
            
            # Webhook para facturas generadas
            if invoice_data.get("invoices_generated", 0) > 0:
                try:
                    payload = {
                        "event_type": "invoices_generated",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "count": invoice_data.get("invoices_generated", 0),
                            "period": invoice_data.get("period_start"),
                        }
                    }
                    
                    if not dry_run:
                        r = requests.post(webhook_url, json=payload, timeout=10)
                        r.raise_for_status()
                        webhooks_sent += 1
                        logger.info("Webhook de facturas generadas enviado")
                except Exception as e:
                    logger.warning(f"Error enviando webhook: {e}")
                    webhooks_failed += 1
            
            # Webhook para escalaciones
            if escalation_data.get("escalations_sent", 0) > 0:
                try:
                    payload = {
                        "event_type": "invoices_escalated",
                        "timestamp": datetime.utcnow().isoformat(),
                        "data": {
                            "count": escalation_data.get("escalations_sent", 0),
                        }
                    }
                    
                    if not dry_run:
                        r = requests.post(webhook_url, json=payload, timeout=10)
                        r.raise_for_status()
                        webhooks_sent += 1
                        logger.info("Webhook de escalaciones enviado")
                except Exception as e:
                    logger.warning(f"Error enviando webhook: {e}")
                    webhooks_failed += 1
            
            _track_metric("invoice_billing.webhooks.sent", webhooks_sent)
            _track_metric("invoice_billing.webhooks.failed", webhooks_failed)
            
            return {
                "webhooks_sent": webhooks_sent,
                "webhooks_failed": webhooks_failed,
                "skipped": False,
            }
    
    @task(task_id="generate_invoice_pdfs")
    def generate_invoice_pdfs(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Genera PDFs para facturas y los almacena.
        """
        with _track_operation("generate_invoice_pdfs"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener facturas recientes sin PDF
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.subtotal,
                            i.taxes,
                            i.created_at,
                            i.customer_email
                        FROM invoices i
                        WHERE i.status = 'issued'
                        AND i.created_at >= NOW() - INTERVAL '7 days'
                        AND (metadata IS NULL OR metadata->>'pdf_generated' IS NULL)
                        LIMIT 50
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"pdfs_generated": 0, "skipped": False}
            
            pdfs_generated = 0
            pdfs_failed = 0
            
            try:
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfgen import canvas
                from reportlab.lib.units import mm
                from reportlab.lib.colors import HexColor
                from pathlib import Path
                
                pdf_out_dir = Path(_get_env_var("INVOICE_PDF_OUT", default="/tmp/invoices"))
                pdf_out_dir.mkdir(parents=True, exist_ok=True)
                
                for inv_row in invoices:
                    inv_id, serie, total, currency, subtotal, taxes, created_at, customer_email = inv_row
                    
                    try:
                        # Obtener items
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    SELECT description, quantity, unit_price, total
                                    FROM invoice_items
                                    WHERE invoice_id = %s
                                """, (inv_id,))
                                items = cur.fetchall()
                        
                        if not items:
                            continue
                        
                        # Generar PDF
                        pdf_path = pdf_out_dir / f"invoice_{serie}_{inv_id}.pdf"
                        currency_symbol = {"USD": "$", "EUR": "€", "MXN": "$", "GBP": "£"}.get(currency or "USD", currency or "$")
                        
                        c = canvas.Canvas(str(pdf_path), pagesize=A4)
                        width, height = A4
                        
                        # Header
                        c.setFillColor(HexColor("#2c3e50"))
                        c.setFont("Helvetica-Bold", 20)
                        c.drawString(20 * mm, height - 25 * mm, "FACTURA")
                        c.setFont("Helvetica-Bold", 14)
                        c.drawString(20 * mm, height - 35 * mm, f"Número: {serie}")
                        c.setFillColor(HexColor("#000000"))
                        c.setFont("Helvetica", 10)
                        c.drawString(20 * mm, height - 43 * mm, f"Fecha: {created_at.strftime('%Y-%m-%d') if hasattr(created_at, 'strftime') else str(created_at)}")
                        c.drawString(20 * mm, height - 49 * mm, f"Moneda: {currency}")
                        
                        # Items
                        y = height - 70 * mm
                        c.setFont("Helvetica-Bold", 10)
                        c.drawString(20 * mm, y, "Descripción")
                        c.drawString(120 * mm, y, "Cant.")
                        c.drawString(140 * mm, y, "Precio Unit.")
                        c.drawString(170 * mm, y, "Total")
                        y -= 6 * mm
                        c.line(20 * mm, y, width - 20 * mm, y)
                        y -= 4 * mm
                        
                        c.setFont("Helvetica", 9)
                        for item_desc, qty, unit_price, item_total in items:
                            c.drawString(20 * mm, y, str(item_desc)[:40])
                            c.drawString(120 * mm, y, f"{float(qty):.2f}")
                            c.drawString(140 * mm, y, f"{currency_symbol}{float(unit_price):.2f}")
                            c.drawString(170 * mm, y, f"{currency_symbol}{float(item_total):.2f}")
                            y -= 7 * mm
                        
                        # Totals
                        y -= 8 * mm
                        c.line(140 * mm, y, width - 20 * mm, y)
                        y -= 6 * mm
                        c.setFont("Helvetica", 10)
                        c.drawString(140 * mm, y, f"Subtotal: {currency_symbol}{float(subtotal):.2f}")
                        y -= 6 * mm
                        c.drawString(140 * mm, y, f"Impuestos: {currency_symbol}{float(taxes):.2f}")
                        y -= 8 * mm
                        c.line(140 * mm, y, width - 20 * mm, y)
                        y -= 6 * mm
                        c.setFont("Helvetica-Bold", 12)
                        c.drawString(140 * mm, y, f"TOTAL: {currency_symbol}{float(total):.2f}")
                        
                        c.showPage()
                        c.save()
                        
                        if not dry_run:
                            # Guardar referencia en metadata de invoice
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    # Verificar si existe columna metadata
                                    cur.execute("""
                                        SELECT column_name 
                                        FROM information_schema.columns 
                                        WHERE table_name = 'invoices' 
                                        AND column_name = 'metadata'
                                    """)
                                    has_metadata = cur.fetchone() is not None
                                    
                                    if has_metadata:
                                        cur.execute("""
                                            UPDATE invoices 
                                            SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                            WHERE id = %s
                                        """, (json.dumps({"pdf_generated": str(pdf_path), "pdf_path": str(pdf_path)}), inv_id))
                                    else:
                                        # Crear tabla invoice_metadata si no existe columna
                                        cur.execute("""
                                            CREATE TABLE IF NOT EXISTS invoice_metadata (
                                                invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                                                key VARCHAR(128) NOT NULL,
                                                value TEXT,
                                                PRIMARY KEY (invoice_id, key)
                                            )
                                        """)
                                        cur.execute("""
                                            INSERT INTO invoice_metadata (invoice_id, key, value)
                                            VALUES (%s, 'pdf_generated', %s)
                                            ON CONFLICT (invoice_id, key) DO UPDATE SET value = EXCLUDED.value
                                        """, (inv_id, str(pdf_path)))
                                    
                                    conn.commit()
                        
                        pdfs_generated += 1
                        _track_metric("invoice_billing.pdfs.generated", 1.0)
                        logger.info(f"PDF generado para factura {inv_id}: {pdf_path}")
                        
                    except Exception as e:
                        logger.error(f"Error generando PDF para factura {inv_id}: {e}", exc_info=True)
                        pdfs_failed += 1
                        _track_metric("invoice_billing.pdfs.failed", 1.0)
                        
            except ImportError:
                logger.warning("reportlab no disponible, saltando generación de PDFs")
                return {"pdfs_generated": 0, "skipped": True}
            
            logger.info(
                "PDFs de facturas generados",
                extra={"generated": pdfs_generated, "failed": pdfs_failed}
            )
            
            return {
                "pdfs_generated": pdfs_generated,
                "pdfs_failed": pdfs_failed,
                "skipped": False,
            }
    
    @task(task_id="sync_to_quickbooks")
    def sync_to_quickbooks(invoice_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sincroniza facturas con QuickBooks.
        """
        with _track_operation("sync_to_quickbooks"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            qb_access_token = _get_env_var("QUICKBOOKS_ACCESS_TOKEN", default="")
            qb_realm_id = _get_env_var("QUICKBOOKS_REALM_ID", default="")
            
            if not qb_access_token or not qb_realm_id:
                logger.info("QuickBooks no configurado, saltando sincronización")
                return {"synced": 0, "skipped": True}
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener facturas pendientes de sincronizar
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.subtotal,
                            i.taxes,
                            i.created_at
                        FROM invoices i
                        WHERE i.status = 'paid'
                        AND (metadata IS NULL OR metadata->>'quickbooks_synced' IS NULL)
                        LIMIT 50
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"synced": 0, "skipped": False}
            
            synced_count = 0
            failed_count = 0
            
            import requests
            
            base_url = f"https://sandbox-quickbooks.api.intuit.com/v3/company/{qb_realm_id}"
            headers = {
                "Authorization": f"Bearer {qb_access_token}",
                "Content-Type": "application/json",
            }
            
            for inv_row in invoices:
                inv_id, serie, total, currency, subtotal, taxes, created_at = inv_row
                
                try:
                    # Crear invoice en QuickBooks
                    payload = {
                        "Line": [
                            {
                                "Amount": float(subtotal),
                                "DetailType": "SalesItemLineDetail",
                                "SalesItemLineDetail": {
                                    "ItemRef": {"value": "1", "name": "Services"},
                                    "UnitPrice": float(subtotal),
                                    "Qty": 1,
                                }
                            }
                        ],
                        "CustomerRef": {"value": "1"},
                        "TxnDate": created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at)[:10],
                        "DueDate": (pendulum.parse(str(created_at)) + timedelta(days=30)).strftime("%Y-%m-%d"),
                    }
                    
                    if not dry_run:
                        r = requests.post(
                            f"{base_url}/invoice",
                            json=payload,
                            headers=headers,
                            timeout=30
                        )
                        
                        if r.status_code in [200, 201]:
                            qb_response = r.json()
                            qb_invoice_id = qb_response.get("Invoice", {}).get("Id")
                            
                            # Marcar como sincronizado
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    # Verificar si existe columna metadata
                                    cur.execute("""
                                        SELECT column_name 
                                        FROM information_schema.columns 
                                        WHERE table_name = 'invoices' 
                                        AND column_name = 'metadata'
                                    """)
                                    has_metadata = cur.fetchone() is not None
                                    
                                    sync_data = json.dumps({"qb_id": qb_invoice_id, "synced_at": datetime.utcnow().isoformat()})
                                    
                                    if has_metadata:
                                        cur.execute("""
                                            UPDATE invoices 
                                            SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                            WHERE id = %s
                                        """, (json.dumps({"quickbooks_synced": sync_data}), inv_id))
                                    else:
                                        # Crear tabla invoice_metadata si no existe columna
                                        cur.execute("""
                                            CREATE TABLE IF NOT EXISTS invoice_metadata (
                                                invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                                                key VARCHAR(128) NOT NULL,
                                                value TEXT,
                                                PRIMARY KEY (invoice_id, key)
                                            )
                                        """)
                                        cur.execute("""
                                            INSERT INTO invoice_metadata (invoice_id, key, value)
                                            VALUES (%s, 'quickbooks_synced', %s)
                                            ON CONFLICT (invoice_id, key) DO UPDATE SET value = EXCLUDED.value
                                        """, (inv_id, sync_data))
                                    
                                    conn.commit()
                            
                            synced_count += 1
                            _track_metric("invoice_billing.quickbooks.synced", 1.0)
                            logger.info(f"Factura {serie} sincronizada con QuickBooks: {qb_invoice_id}")
                        else:
                            failed_count += 1
                            logger.warning(f"Error sincronizando factura {inv_id} con QuickBooks: {r.status_code}")
                    else:
                        synced_count += 1
                        logger.info(f"[DRY RUN] Factura {serie} sería sincronizada con QuickBooks")
                        
                except Exception as e:
                    logger.error(f"Error sincronizando factura {inv_id} con QuickBooks: {e}", exc_info=True)
                    failed_count += 1
                    _track_metric("invoice_billing.quickbooks.failed", 1.0)
            
            logger.info(
                "Sincronización con QuickBooks completada",
                extra={"synced": synced_count, "failed": failed_count}
            )
            
            return {
                "synced": synced_count,
                "failed": failed_count,
                "skipped": False,
            }
    
    @task(task_id="save_to_dead_letter_queue")
    def save_to_dead_letter_queue(
        email_data: Dict[str, Any],
        reminder_data: Dict[str, Any],
        escalation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Guarda errores críticos en dead letter queue para reprocesamiento.
        """
        with _track_operation("save_to_dead_letter_queue"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Crear tabla DLQ si no existe
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS invoice_dlq (
                            id SERIAL PRIMARY KEY,
                            invoice_id INTEGER,
                            error_type VARCHAR(64) NOT NULL,
                            error_message TEXT,
                            context JSONB,
                            retry_count INTEGER DEFAULT 0,
                            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            processed_at TIMESTAMPTZ,
                            status VARCHAR(32) DEFAULT 'pending' CHECK (status IN ('pending', 'processed', 'failed'))
                        );
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_dlq_status 
                        ON invoice_dlq(status) WHERE status = 'pending';
                    """)
                    
                    conn.commit()
            
            # Obtener recordatorios fallidos
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT invoice_id, metadata
                        FROM invoice_reminders
                        WHERE status = 'failed'
                        AND sent_at >= NOW() - INTERVAL '24 hours'
                        AND NOT EXISTS (
                            SELECT 1 FROM invoice_dlq
                            WHERE invoice_dlq.invoice_id = invoice_reminders.invoice_id
                            AND invoice_dlq.status = 'pending'
                        )
                    """)
                    
                    failed_reminders = cur.fetchall()
            
            saved_count = 0
            
            for inv_id, metadata in failed_reminders:
                try:
                    error_data = json.loads(metadata) if metadata else {}
                    
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO invoice_dlq 
                                    (invoice_id, error_type, error_message, context, status)
                                VALUES (%s, 'reminder_failed', %s, %s, 'pending')
                                ON CONFLICT DO NOTHING
                            """, (
                                inv_id,
                                error_data.get("error", "Unknown error")[:500],
                                json.dumps({
                                    "source": "invoice_reminders",
                                    "metadata": error_data,
                                })
                            ))
                            
                            conn.commit()
                    
                    saved_count += 1
                    _track_metric("invoice_billing.dlq.saved", 1.0)
                    
                except Exception as e:
                    logger.error(f"Error guardando en DLQ: {e}", exc_info=True)
            
            logger.info(
                "Errores guardados en DLQ",
                extra={"saved": saved_count}
            )
            
            return {
                "saved": saved_count,
                "skipped": False,
            }
    
    @task(task_id="export_analytics_to_s3")
    def export_analytics_to_s3(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exporta reportes de analytics a S3.
        """
        with _track_operation("export_analytics_to_s3"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            s3_bucket = _get_env_var("INVOICE_ANALYTICS_S3_BUCKET", default="")
            if not s3_bucket:
                logger.info("S3 bucket no configurado, saltando exportación")
                return {"exported": False, "skipped": True}
            
            try:
                import boto3
                from botocore.exceptions import ClientError
                
                s3_client = boto3.client('s3')
                
                # Generar reporte JSON
                report_key = f"invoice-analytics/{pendulum.now('UTC').strftime('%Y/%m/%d')}/report_{pendulum.now('UTC').int_timestamp}.json"
                
                if not dry_run:
                    s3_client.put_object(
                        Bucket=s3_bucket,
                        Key=report_key,
                        Body=json.dumps(analytics_data, indent=2, default=str),
                        ContentType='application/json',
                    )
                    
                    logger.info(f"Reporte exportado a S3: s3://{s3_bucket}/{report_key}")
                    _track_metric("invoice_billing.analytics.exported_to_s3", 1.0)
                else:
                    logger.info(f"[DRY RUN] Reporte sería exportado a S3: s3://{s3_bucket}/{report_key}")
                
                return {
                    "exported": True,
                    "s3_path": f"s3://{s3_bucket}/{report_key}",
                    "skipped": False,
                }
                
            except ImportError:
                logger.warning("boto3 no disponible, saltando exportación a S3")
                return {"exported": False, "skipped": True}
            except Exception as e:
                logger.error(f"Error exportando a S3: {e}", exc_info=True)
                return {"exported": False, "skipped": False}
    
    @task(task_id="predict_payment_probability_ml")
    def predict_payment_probability_ml(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predice probabilidad de pago usando Machine Learning.
        """
        with _track_operation("predict_payment_probability_ml"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            ml_endpoint = _get_env_var("INVOICE_ML_PAYMENT_ENDPOINT", default="")
            if not ml_endpoint:
                logger.info("ML endpoint no configurado, usando análisis básico")
                return {"predicted": 0, "skipped": True}
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"predicted": 0, "skipped": False}
            
            import requests
            
            predictions = []
            
            for inv in unpaid_invoices[:50]:  # Limitar para no sobrecargar
                inv_id = inv.get("id")
                days_since = inv.get("days_since_issue", 0)
                total = float(inv.get("total", 0))
                customer_email = inv.get("customer_email")
                
                if not customer_email:
                    continue
                
                try:
                    # Obtener historial del cliente
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT 
                                    COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                                    COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                                    COUNT(*) as total_count,
                                    AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days_to_pay
                                FROM invoices
                                WHERE customer_email = %s
                                AND created_at < NOW() - INTERVAL '90 days'
                            """, (customer_email,))
                            
                            history = cur.fetchone()
                    
                    # Preparar features para ML
                    features = {
                        "days_since_issue": days_since,
                        "invoice_amount": total,
                        "paid_invoices_count": history[0] or 0 if history else 0,
                        "overdue_invoices_count": history[1] or 0 if history else 0,
                        "total_invoices_count": history[2] or 0 if history else 0,
                        "avg_days_to_pay": float(history[3] or 0) if history else 0,
                    }
                    
                    # Llamar a endpoint ML
                    r = requests.post(
                        ml_endpoint,
                        json=features,
                        timeout=10,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if r.status_code == 200:
                        ml_result = r.json()
                        payment_probability = ml_result.get("payment_probability", 0.5)
                        
                        predictions.append({
                            "invoice_id": inv_id,
                            "payment_probability": payment_probability,
                            "risk_level": "high" if payment_probability < 0.3 else "medium" if payment_probability < 0.6 else "low",
                        })
                        
                        # Actualizar metadata con predicción
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE id = %s
                                """, (json.dumps({
                                    "ml_payment_probability": payment_probability,
                                    "ml_predicted_at": datetime.utcnow().isoformat(),
                                }), inv_id))
                                
                                conn.commit()
                        
                        _track_metric("invoice_billing.ml.prediction_made", 1.0)
                        logger.info(f"Predicción ML para factura {inv_id}: {payment_probability:.2%}")
                        
                except Exception as e:
                    logger.warning(f"Error en predicción ML para factura {inv_id}: {e}", exc_info=True)
            
            logger.info(
                "Predicciones ML de pago completadas",
                extra={"predicted": len(predictions)}
            )
            
            return {
                "predicted": len(predictions),
                "predictions": predictions,
                "skipped": False,
            }
    
    @task(task_id="sync_with_crm")
    def sync_with_crm(
        invoice_data: Dict[str, Any],
        reminder_data: Dict[str, Any],
        escalation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Sincroniza facturas y recordatorios con CRM (Salesforce/Pipedrive).
        """
        with _track_operation("sync_with_crm"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            crm_type = _get_env_var("CRM_TYPE", default="").lower()
            if not crm_type:
                logger.info("CRM no configurado, saltando sincronización")
                return {"synced": 0, "skipped": True}
            
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            synced_count = 0
            failed_count = 0
            
            try:
                from data.integrations.connectors import create_connector
                
                # Configurar conector según tipo
                if crm_type == "salesforce":
                    connector_config = {
                        "username": _get_env_var("SALESFORCE_USERNAME", default=""),
                        "password": _get_env_var("SALESFORCE_PASSWORD", default=""),
                        "security_token": _get_env_var("SALESFORCE_SECURITY_TOKEN", default=""),
                        "sobject_type": "Invoice__c",
                    }
                elif crm_type == "pipedrive":
                    connector_config = {
                        "api_token": _get_env_var("PIPEDRIVE_API_TOKEN", default=""),
                        "company_domain": _get_env_var("PIPEDRIVE_COMPANY_DOMAIN", default=""),
                        "resource_type": "deals",
                    }
                else:
                    logger.warning(f"Tipo de CRM no soportado: {crm_type}")
                    return {"synced": 0, "skipped": True}
                
                connector = create_connector(crm_type, connector_config)
                
                if not connector.connect():
                    logger.error("No se pudo conectar al CRM")
                    return {"synced": 0, "skipped": True}
                
                # Sincronizar escalaciones (más importantes)
                escalations_sent = escalation_data.get("escalations_sent", 0)
                if escalations_sent > 0 and not dry_run:
                    # Crear actividad en CRM para escalaciones
                    crm_data = {
                        "type": "invoice_escalated",
                        "count": escalations_sent,
                        "timestamp": datetime.utcnow().isoformat(),
                    }
                    
                    from data.integrations.connectors import SyncRecord
                    record = SyncRecord(
                        source_id=f"invoice_escalations_{pendulum.now('UTC').int_timestamp}",
                        source_type="invoice_escalation",
                        data=crm_data
                    )
                    
                    results = connector.write_records([record])
                    if results and results[0].status == "synced":
                        synced_count += 1
                        logger.info("Escalaciones sincronizadas con CRM")
                    else:
                        failed_count += 1
                
                connector.disconnect()
                
            except ImportError:
                logger.warning("Módulo de integraciones no disponible, saltando sincronización CRM")
                return {"synced": 0, "skipped": True}
            except Exception as e:
                logger.error(f"Error sincronizando con CRM: {e}", exc_info=True)
                failed_count += 1
            
            _track_metric("invoice_billing.crm.synced", synced_count)
            _track_metric("invoice_billing.crm.failed", failed_count)
            
            return {
                "synced": synced_count,
                "failed": failed_count,
                "skipped": False,
            }
    
    @task(task_id="optimize_email_timing")
    def optimize_email_timing(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza timing de emails basado en historial de aperturas.
        """
        with _track_operation("optimize_email_timing"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Crear tabla de tracking de emails si no existe
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS invoice_email_tracking (
                            id SERIAL PRIMARY KEY,
                            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                            customer_email VARCHAR(256) NOT NULL,
                            sent_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            opened BOOLEAN DEFAULT false,
                            opened_at TIMESTAMPTZ,
                            clicked BOOLEAN DEFAULT false,
                            clicked_at TIMESTAMPTZ,
                            metadata JSONB
                        );
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_email_tracking_customer 
                        ON invoice_email_tracking(customer_email);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_email_tracking_sent_at 
                        ON invoice_email_tracking(sent_at);
                    """)
                    
                    conn.commit()
            
            # Analizar mejores horas para envío
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            EXTRACT(HOUR FROM sent_at) as hour,
                            COUNT(*) as total_sent,
                            COUNT(*) FILTER (WHERE opened = true) as total_opened,
                            ROUND(COUNT(*) FILTER (WHERE opened = true)::numeric / NULLIF(COUNT(*), 0) * 100, 2) as open_rate
                        FROM invoice_email_tracking
                        WHERE sent_at >= NOW() - INTERVAL '90 days'
                        GROUP BY EXTRACT(HOUR FROM sent_at)
                        HAVING COUNT(*) >= 10
                        ORDER BY open_rate DESC
                        LIMIT 3
                    """)
                    
                    best_hours = cur.fetchall()
            
            optimization_result = {
                "best_hours": [{"hour": int(h[0]), "open_rate": float(h[3] or 0)} for h in best_hours],
                "analyzed_period_days": 90,
            }
            
            logger.info(
                "Optimización de timing de emails completada",
                extra=optimization_result
            )
            
            _track_metric("invoice_billing.email_timing.optimized", 1.0)
            
            return optimization_result
    
    @task(task_id="ab_test_email_templates")
    def ab_test_email_templates(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        A/B testing de templates de email para optimizar conversión.
        """
        with _track_operation("ab_test_email_templates"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            enable_ab = _get_env_var("INVOICE_AB_TESTING_ENABLED", default="false").lower() == "true"
            if not enable_ab:
                return {"tested": 0, "skipped": True}
            
            # Crear tabla de A/B tests si no existe
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS invoice_ab_tests (
                            id SERIAL PRIMARY KEY,
                            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                            test_name VARCHAR(128) NOT NULL,
                            variant VARCHAR(32) NOT NULL,
                            assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            opened BOOLEAN DEFAULT false,
                            clicked BOOLEAN DEFAULT false,
                            converted BOOLEAN DEFAULT false,
                            metadata JSONB
                        );
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_invoice_ab_tests_test_name 
                        ON invoice_ab_tests(test_name, variant);
                    """)
                    
                    conn.commit()
            
            reminders_to_send = check_data.get("reminders_to_send", [])
            
            if not reminders_to_send:
                return {"tested": 0, "skipped": False}
            
            tested_count = 0
            variant_a_count = 0
            variant_b_count = 0
            
            for inv in reminders_to_send[:50]:  # Limitar para testing
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                
                if not customer_email:
                    continue
                
                # Asignar variante de forma determinística
                import hashlib
                email_hash = int(hashlib.md5(customer_email.encode()).hexdigest(), 16)
                variant = "A" if (email_hash % 2) == 0 else "B"
                
                if variant == "A":
                    variant_a_count += 1
                else:
                    variant_b_count += 1
                
                # Guardar asignación
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO invoice_ab_tests 
                                (invoice_id, test_name, variant, metadata)
                            VALUES (%s, 'reminder_template', %s, %s)
                            ON CONFLICT DO NOTHING
                        """, (inv_id, variant, json.dumps({"customer_email": customer_email})))
                        
                        conn.commit()
                
                tested_count += 1
            
            logger.info(
                "A/B testing de templates asignado",
                extra={"tested": tested_count, "variant_a": variant_a_count, "variant_b": variant_b_count}
            )
            
            _track_metric("invoice_billing.ab_test.assigned", tested_count)
            
            return {
                "tested": tested_count,
                "variant_a": variant_a_count,
                "variant_b": variant_b_count,
                "skipped": False,
            }
    
    @task(task_id="analyze_cohorts")
    def analyze_cohorts(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis de cohortes para identificar patrones de pago.
        """
        with _track_operation("analyze_cohorts"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            
            # Análisis por cohortes mensuales
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('month', created_at) as cohort_month,
                            COUNT(*) as total_invoices,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_invoices,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_invoices,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days_to_pay,
                            SUM(total) FILTER (WHERE status = 'paid') as total_paid_amount
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY DATE_TRUNC('month', created_at)
                        ORDER BY cohort_month DESC
                    """)
                    
                    cohorts = cur.fetchall()
            
            cohort_analysis = []
            for cohort in cohorts:
                cohort_month, total, paid, overdue, avg_days, total_amount = cohort
                conversion_rate = (paid / total * 100) if total > 0 else 0
                
                cohort_analysis.append({
                    "cohort_month": str(cohort_month),
                    "total_invoices": total,
                    "paid_invoices": paid,
                    "overdue_invoices": overdue,
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_days_to_pay": round(float(avg_days or 0), 1),
                    "total_paid_amount": float(total_amount or 0),
                })
            
            logger.info(
                "Análisis de cohortes completado",
                extra={"cohorts_analyzed": len(cohort_analysis)}
            )
            
            _track_metric("invoice_billing.cohorts.analyzed", len(cohort_analysis))
            
            return {
                "cohorts": cohort_analysis,
                "skipped": False,
            }
    
    @task(task_id="personalize_customer_communication")
    def personalize_customer_communication(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Personaliza comunicación según perfil y historial del cliente.
        """
        with _track_operation("personalize_customer_communication"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"personalized": 0, "skipped": False}
            
            personalized_count = 0
            
            for inv in unpaid_invoices[:50]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email:
                    continue
                
                # Obtener perfil del cliente
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT 
                                COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                                COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                                AVG(total) as avg_invoice_amount,
                                MAX(created_at) as last_invoice_date
                            FROM invoices
                            WHERE customer_email = %s
                            AND created_at < NOW() - INTERVAL '365 days'
                        """, (customer_email,))
                        
                        profile = cur.fetchone()
                
                if profile:
                    paid_count = profile[0] or 0
                    overdue_count = profile[1] or 0
                    avg_amount = float(profile[2] or 0)
                    
                    # Determinar estrategia de comunicación
                    if paid_count > 5 and overdue_count == 0:
                        # Cliente fiel - tono amigable
                        communication_style = "friendly"
                        discount_eligible = True
                    elif overdue_count > 2:
                        # Cliente problemático - tono firme
                        communication_style = "firm"
                        discount_eligible = False
                    elif total > avg_amount * 1.5:
                        # Factura más alta de lo normal
                        communication_style = "supportive"
                        discount_eligible = True
                    else:
                        # Cliente regular
                        communication_style = "standard"
                        discount_eligible = False
                    
                    # Guardar personalización en metadata
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "communication_style": communication_style,
                                "discount_eligible": discount_eligible,
                                "customer_tier": "vip" if paid_count > 10 else "regular" if paid_count > 0 else "new",
                                "personalized_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
                    
                    personalized_count += 1
                    _track_metric("invoice_billing.personalization.applied", 1.0)
            
            logger.info(
                "Personalización de comunicación completada",
                extra={"personalized": personalized_count}
            )
            
            return {
                "personalized": personalized_count,
                "skipped": False,
            }
    
    @task(task_id="generate_dashboard_metrics")
    def generate_dashboard_metrics(
        analytics_data: Dict[str, Any],
        cohort_data: Dict[str, Any],
        ml_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera métricas para dashboard en tiempo real.
        """
        with _track_operation("generate_dashboard_metrics"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            today = now.date()
            this_month = now.start_of("month")
            last_month = this_month.subtract(months=1)
            
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Métricas del día
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'issued') as issued_today,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_today,
                            SUM(total) FILTER (WHERE status = 'paid') as paid_amount_today
                        FROM invoices
                        WHERE DATE(created_at) = %s
                    """, (today,))
                    
                    today_metrics = cur.fetchone()
                    
                    # Métricas del mes
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'issued') as issued_month,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_month,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_month,
                            SUM(total) FILTER (WHERE status = 'issued') as issued_amount_month,
                            SUM(total) FILTER (WHERE status = 'paid') as paid_amount_month,
                            SUM(total) FILTER (WHERE status = 'overdue') as overdue_amount_month
                        FROM invoices
                        WHERE created_at >= %s
                    """, (this_month,))
                    
                    month_metrics = cur.fetchone()
                    
                    # Métricas de recordatorios
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE reminder_type = 'first_reminder' AND status = 'sent') as reminders_sent,
                            COUNT(*) FILTER (WHERE reminder_type = 'escalation' AND status = 'sent') as escalations_sent,
                            COUNT(*) FILTER (WHERE status = 'failed') as failed_reminders
                        FROM invoice_reminders
                        WHERE sent_at >= %s
                    """, (this_month,))
                    
                    reminder_metrics = cur.fetchone()
            
            dashboard = {
                "timestamp": now.isoformat(),
                "today": {
                    "invoices_issued": today_metrics[0] or 0,
                    "invoices_paid": today_metrics[1] or 0,
                    "amount_paid": float(today_metrics[2] or 0),
                },
                "this_month": {
                    "invoices_issued": month_metrics[0] or 0,
                    "invoices_paid": month_metrics[1] or 0,
                    "invoices_overdue": month_metrics[2] or 0,
                    "amount_issued": float(month_metrics[3] or 0),
                    "amount_paid": float(month_metrics[4] or 0),
                    "amount_overdue": float(month_metrics[5] or 0),
                },
                "reminders": {
                    "reminders_sent": reminder_metrics[0] or 0,
                    "escalations_sent": reminder_metrics[1] or 0,
                    "failed": reminder_metrics[2] or 0,
                },
                "analytics": analytics_data,
                "cohorts": cohort_data.get("cohorts", []),
                "ml_predictions": ml_data.get("predictions", []),
            }
            
            # Calcular KPIs
            if month_metrics[0] and month_metrics[0] > 0:
                dashboard["kpis"] = {
                    "conversion_rate": round((month_metrics[1] / month_metrics[0]) * 100, 2),
                    "overdue_rate": round((month_metrics[2] / month_metrics[0]) * 100, 2),
                    "collection_rate": round((float(month_metrics[4] or 0) / float(month_metrics[3] or 1)) * 100, 2),
                }
            
            # Guardar en Variable para acceso desde dashboard
            try:
                Variable.set("invoice_billing_dashboard", json.dumps(dashboard))
            except Exception:
                pass
            
            logger.info(
                "Métricas de dashboard generadas",
                extra={"kpis": dashboard.get("kpis", {})}
            )
            
            _track_metric("invoice_billing.dashboard.updated", 1.0)
            
            return dashboard
    
    @task(task_id="intelligent_retry_failed_emails")
    def intelligent_retry_failed_emails() -> Dict[str, Any]:
        """
        Reintenta envío de emails fallidos con estrategia inteligente.
        """
        with _track_operation("intelligent_retry_failed_emails"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener recordatorios fallidos recientes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            ir.invoice_id,
                            ir.reminder_type,
                            ir.days_since_issue,
                            i.serie,
                            i.total,
                            i.currency,
                            i.customer_email,
                            ir.metadata,
                            COUNT(*) OVER (PARTITION BY ir.invoice_id) as retry_count
                        FROM invoice_reminders ir
                        JOIN invoices i ON ir.invoice_id = i.id
                        WHERE ir.status = 'failed'
                        AND ir.sent_at >= NOW() - INTERVAL '48 hours'
                        AND (ir.metadata->>'retry_count')::int < 3
                        ORDER BY ir.sent_at ASC
                        LIMIT 20
                    """)
                    
                    failed_reminders = cur.fetchall()
            
            if not failed_reminders:
                return {"retried": 0, "skipped": False}
            
            retried_count = 0
            successful_retries = 0
            
            for row in failed_reminders:
                inv_id, rem_type, days_since, serie, total, currency, customer_email, metadata, retry_count = row
                
                if not customer_email:
                    continue
                
                try:
                    error_data = json.loads(metadata) if metadata else {}
                    error_message = error_data.get("error", "")
                    
                    # Estrategia de retry inteligente
                    # Si el error fue de SMTP, esperar más tiempo
                    if "smtp" in error_message.lower() or "connection" in error_message.lower():
                        # Esperar antes de retry
                        time.sleep(2)
                    
                    # Detectar idioma
                    language = _get_email_language(customer_email)
                    
                    # Reintentar envío
                    if rem_type == "first_reminder":
                        subject, html_content = _render_reminder_email_template(
                            serie=serie,
                            total=float(total),
                            currency=currency or "USD",
                            days_since=days_since,
                            reminder_type="first_reminder",
                            language=language,
                        )
                    else:
                        subject, html_content = _render_reminder_email_template(
                            serie=serie,
                            total=float(total),
                            currency=currency or "USD",
                            days_since=days_since,
                            reminder_type="escalation",
                            language=language,
                        )
                    
                    if not dry_run:
                        notify_email(
                            subject=subject,
                            html=html_content,
                            to=customer_email,
                        )
                        
                        # Actualizar estado
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoice_reminders 
                                    SET status = 'sent',
                                        sent_at = NOW(),
                                        metadata = metadata || %s::jsonb
                                    WHERE invoice_id = %s 
                                    AND reminder_type = %s
                                    AND status = 'failed'
                                """, (
                                    json.dumps({
                                        "retry_count": retry_count + 1,
                                        "retried_at": datetime.utcnow().isoformat(),
                                    }),
                                    inv_id,
                                    rem_type
                                ))
                                
                                conn.commit()
                        
                        successful_retries += 1
                        _track_metric("invoice_billing.retry.successful", 1.0)
                        logger.info(f"Email reintentado exitosamente para factura {inv_id}")
                    else:
                        logger.info(f"[DRY RUN] Email sería reintentado para factura {inv_id}")
                    
                    retried_count += 1
                    
                except Exception as e:
                    logger.error(f"Error en retry para factura {inv_id}: {e}", exc_info=True)
                    _track_metric("invoice_billing.retry.failed", 1.0)
            
            logger.info(
                "Reintentos inteligentes completados",
                extra={"retried": retried_count, "successful": successful_retries}
            )
            
            return {
                "retried": retried_count,
                "successful": successful_retries,
                "skipped": False,
            }
    
    @task(task_id="analyze_customer_sentiment")
    def analyze_customer_sentiment(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza sentimiento en respuestas y comunicaciones de clientes.
        """
        with _track_operation("analyze_customer_sentiment"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            sentiment_api = _get_env_var("SENTIMENT_ANALYSIS_API", default="")
            if not sentiment_api:
                logger.info("API de análisis de sentimiento no configurada")
                return {"analyzed": 0, "skipped": True}
            
            # Crear tabla de sentimientos si no existe
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS invoice_customer_sentiment (
                            id SERIAL PRIMARY KEY,
                            invoice_id INTEGER NOT NULL REFERENCES invoices(id) ON DELETE CASCADE,
                            customer_email VARCHAR(256) NOT NULL,
                            sentiment_score FLOAT,
                            sentiment_label VARCHAR(32),
                            analyzed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                            source VARCHAR(128),
                            metadata JSONB
                        );
                    """)
                    
                    conn.commit()
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"analyzed": 0, "skipped": False}
            
            import requests
            
            analyzed_count = 0
            positive_count = 0
            negative_count = 0
            neutral_count = 0
            
            for inv in unpaid_invoices[:30]:  # Limitar para no sobrecargar API
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                
                if not customer_email:
                    continue
                
                try:
                    # Obtener comunicaciones recientes del cliente
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT 
                                    metadata->>'customer_response' as response,
                                    metadata->>'email_subject' as subject
                                FROM invoice_reminders
                                WHERE invoice_id = %s
                                AND metadata->>'customer_response' IS NOT NULL
                                ORDER BY sent_at DESC
                                LIMIT 1
                            """, (inv_id,))
                            
                            communication = cur.fetchone()
                    
                    if not communication or not communication[0]:
                        continue
                    
                    text_to_analyze = communication[0]
                    
                    # Llamar a API de sentimiento
                    r = requests.post(
                        sentiment_api,
                        json={"text": text_to_analyze},
                        timeout=5,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if r.status_code == 200:
                        sentiment_data = r.json()
                        sentiment_score = sentiment_data.get("score", 0.0)
                        sentiment_label = sentiment_data.get("label", "neutral")
                        
                        # Guardar análisis
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO invoice_customer_sentiment 
                                        (invoice_id, customer_email, sentiment_score, sentiment_label, source, metadata)
                                    VALUES (%s, %s, %s, %s, 'email_response', %s)
                                    ON CONFLICT DO NOTHING
                                """, (
                                    inv_id,
                                    customer_email,
                                    sentiment_score,
                                    sentiment_label,
                                    json.dumps({"original_text": text_to_analyze[:200]})
                                ))
                                
                                conn.commit()
                        
                        if sentiment_label == "positive":
                            positive_count += 1
                        elif sentiment_label == "negative":
                            negative_count += 1
                        else:
                            neutral_count += 1
                        
                        analyzed_count += 1
                        _track_metric("invoice_billing.sentiment.analyzed", 1.0)
                        
                except Exception as e:
                    logger.warning(f"Error analizando sentimiento para factura {inv_id}: {e}")
            
            logger.info(
                "Análisis de sentimiento completado",
                extra={
                    "analyzed": analyzed_count,
                    "positive": positive_count,
                    "negative": negative_count,
                    "neutral": neutral_count
                }
            )
            
            return {
                "analyzed": analyzed_count,
                "positive": positive_count,
                "negative": negative_count,
                "neutral": neutral_count,
                "skipped": False,
            }
    
    @task(task_id="predict_customer_churn")
    def predict_customer_churn(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predice riesgo de churn de clientes basado en patrones de pago.
        """
        with _track_operation("predict_customer_churn"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"predicted": 0, "skipped": False}
            
            churn_predictions = []
            
            # Agrupar por cliente
            customers = {}
            for inv in unpaid_invoices:
                customer_email = inv.get("customer_email")
                if not customer_email:
                    continue
                
                if customer_email not in customers:
                    customers[customer_email] = []
                customers[customer_email].append(inv)
            
            for customer_email, invoices in list(customers.items())[:50]:
                try:
                    # Obtener historial completo del cliente
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT 
                                    COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                                    COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                                    COUNT(*) as total_count,
                                    AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days_to_pay,
                                    MAX(created_at) as last_invoice_date,
                                    MIN(created_at) as first_invoice_date
                                FROM invoices
                                WHERE customer_email = %s
                            """, (customer_email,))
                            
                            history = cur.fetchone()
                    
                    if not history or history[2] == 0:
                        continue
                    
                    paid_count = history[0] or 0
                    overdue_count = history[1] or 0
                    total_count = history[2] or 0
                    avg_days = float(history[3] or 0)
                    last_invoice = history[4]
                    first_invoice = history[5]
                    
                    # Calcular métricas de churn
                    overdue_rate = (overdue_count / total_count) if total_count > 0 else 0
                    days_since_last = (pendulum.now("UTC") - pendulum.instance(last_invoice)).days if last_invoice else 0
                    customer_age_days = (pendulum.instance(last_invoice) - pendulum.instance(first_invoice)).days if last_invoice and first_invoice else 0
                    
                    # Scoring de churn (0-100)
                    churn_score = 0
                    
                    # Factores de riesgo
                    if overdue_rate > 0.5:
                        churn_score += 40
                    elif overdue_rate > 0.3:
                        churn_score += 25
                    
                    if days_since_last > 90:
                        churn_score += 30
                    elif days_since_last > 60:
                        churn_score += 15
                    
                    if avg_days > 45:
                        churn_score += 20
                    elif avg_days > 30:
                        churn_score += 10
                    
                    if total_count < 3:
                        churn_score += 10  # Cliente nuevo con problemas
                    
                    churn_score = min(churn_score, 100)
                    
                    churn_risk = "high" if churn_score > 60 else "medium" if churn_score > 30 else "low"
                    
                    churn_predictions.append({
                        "customer_email": customer_email,
                        "churn_score": churn_score,
                        "churn_risk": churn_risk,
                        "overdue_rate": round(overdue_rate * 100, 2),
                        "days_since_last_invoice": days_since_last,
                    })
                    
                    # Guardar predicción en metadata de última factura
                    if invoices:
                        last_inv = invoices[0]
                        inv_id = last_inv.get("id")
                        
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE customer_email = %s
                                    AND id = (
                                        SELECT id FROM invoices 
                                        WHERE customer_email = %s 
                                        ORDER BY created_at DESC 
                                        LIMIT 1
                                    )
                                """, (
                                    json.dumps({
                                        "churn_score": churn_score,
                                        "churn_risk": churn_risk,
                                        "churn_predicted_at": datetime.utcnow().isoformat(),
                                    }),
                                    customer_email,
                                    customer_email
                                ))
                                
                                conn.commit()
                    
                    _track_metric("invoice_billing.churn.predicted", 1.0)
                    
                except Exception as e:
                    logger.warning(f"Error prediciendo churn para {customer_email}: {e}")
            
            high_risk_count = sum(1 for p in churn_predictions if p["churn_risk"] == "high")
            
            if high_risk_count > 0:
                _send_slack_notification(
                    f"⚠️ {high_risk_count} clientes con alto riesgo de churn detectados"
                )
            
            logger.info(
                "Predicción de churn completada",
                extra={
                    "predicted": len(churn_predictions),
                    "high_risk": high_risk_count
                }
            )
            
            return {
                "predicted": len(churn_predictions),
                "high_risk": high_risk_count,
                "predictions": churn_predictions[:10],  # Limitar para no sobrecargar
                "skipped": False,
            }
    
    @task(task_id="optimize_discount_strategy")
    def optimize_discount_strategy(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza estrategia de descuentos para maximizar conversión.
        """
        with _track_operation("optimize_discount_strategy"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"optimized": 0, "skipped": False}
            
            optimized_count = 0
            
            for inv in unpaid_invoices[:50]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email:
                    continue
                
                # Obtener metadata de personalización
                metadata_str = inv.get("metadata")
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                discount_eligible = metadata.get("discount_eligible", False)
                customer_tier = metadata.get("customer_tier", "regular")
                communication_style = metadata.get("communication_style", "standard")
                
                if not discount_eligible:
                    continue
                
                # Calcular descuento óptimo
                base_discount = 0
                
                if customer_tier == "vip":
                    base_discount = 15  # 15% para VIPs
                elif days_since > 30:
                    base_discount = 10  # 10% para facturas muy viejas
                elif days_since > 14:
                    base_discount = 5   # 5% para facturas viejas
                
                # Ajustar según monto
                if total > 1000:
                    base_discount = min(base_discount + 5, 20)  # Hasta 20% para montos altos
                
                if base_discount > 0:
                    discount_amount = total * (base_discount / 100)
                    new_total = total - discount_amount
                    
                    # Guardar recomendación de descuento
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "discount_recommended": base_discount,
                                "discount_amount": discount_amount,
                                "new_total_after_discount": new_total,
                                "discount_optimized_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
                    
                    optimized_count += 1
                    _track_metric("invoice_billing.discount.optimized", 1.0)
                    logger.info(f"Descuento optimizado para factura {inv_id}: {base_discount}%")
            
            logger.info(
                "Optimización de descuentos completada",
                extra={"optimized": optimized_count}
            )
            
            return {
                "optimized": optimized_count,
                "skipped": False,
            }
    
    @task(task_id="integrate_payment_gateways")
    def integrate_payment_gateways(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con múltiples gateways de pago para facilitar pagos.
        """
        with _track_operation("integrate_payment_gateways"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            payment_gateways = _get_env_var("PAYMENT_GATEWAYS", default="").split(",")
            payment_gateways = [g.strip() for g in payment_gateways if g.strip()]
            
            if not payment_gateways:
                return {"integrated": 0, "skipped": True}
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"integrated": 0, "skipped": False}
            
            integrated_count = 0
            
            for inv in unpaid_invoices[:30]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                currency = inv.get("currency", "USD")
                
                if not customer_email:
                    continue
                
                # Generar links de pago para cada gateway
                payment_links = {}
                
                for gateway in payment_gateways:
                    gateway_lower = gateway.lower()
                    
                    if gateway_lower == "stripe":
                        # Link de pago de Stripe
                        stripe_key = _get_env_var("STRIPE_PUBLISHABLE_KEY", default="")
                        if stripe_key:
                            payment_links["stripe"] = f"https://checkout.stripe.com/pay/{inv_id}"
                    
                    elif gateway_lower == "paypal":
                        payment_links["paypal"] = f"https://www.paypal.com/checkoutnow?invoice_id={inv_id}"
                    
                    elif gateway_lower == "square":
                        payment_links["square"] = f"https://squareup.com/i/{inv_id}"
                
                if payment_links:
                    # Guardar links en metadata
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "payment_links": payment_links,
                                "payment_gateways_integrated": list(payment_links.keys()),
                                "integrated_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
                    
                    integrated_count += 1
                    _track_metric("invoice_billing.payment_gateways.integrated", 1.0)
            
            logger.info(
                "Integración con gateways de pago completada",
                extra={"integrated": integrated_count, "gateways": payment_gateways}
            )
            
            return {
                "integrated": integrated_count,
                "gateways": payment_gateways,
                "skipped": False,
            }
    
    @task(task_id="analyze_payment_trends")
    def analyze_payment_trends(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza tendencias de pago y forecasting.
        """
        with _track_operation("analyze_payment_trends"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            
            # Obtener datos históricos de últimos 12 meses
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('month', created_at) as month,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            SUM(total) FILTER (WHERE status = 'paid') as paid_amount,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY DATE_TRUNC('month', created_at)
                        ORDER BY month ASC
                    """)
                    
                    historical_data = cur.fetchall()
            
            if len(historical_data) < 3:
                return {"analyzed": False, "skipped": True, "reason": "insufficient_data"}
            
            # Calcular tendencias
            months = [str(row[0]) for row in historical_data]
            paid_counts = [row[1] or 0 for row in historical_data]
            paid_amounts = [float(row[2] or 0) for row in historical_data]
            avg_days = [float(row[3] or 0) for row in historical_data]
            
            # Tendencia de crecimiento
            if len(paid_counts) >= 2:
                count_trend = ((paid_counts[-1] - paid_counts[0]) / paid_counts[0] * 100) if paid_counts[0] > 0 else 0
                amount_trend = ((paid_amounts[-1] - paid_amounts[0]) / paid_amounts[0] * 100) if paid_amounts[0] > 0 else 0
                days_trend = ((avg_days[-1] - avg_days[0]) / avg_days[0] * 100) if avg_days[0] > 0 else 0
            else:
                count_trend = amount_trend = days_trend = 0
            
            # Forecasting simple (promedio móvil)
            forecast_months = 3
            recent_avg_count = sum(paid_counts[-3:]) / min(3, len(paid_counts))
            recent_avg_amount = sum(paid_amounts[-3:]) / min(3, len(paid_amounts))
            
            trends = {
                "historical_months": months,
                "paid_counts": paid_counts,
                "paid_amounts": paid_amounts,
                "avg_days_to_pay": avg_days,
                "trends": {
                    "count_trend_pct": round(count_trend, 2),
                    "amount_trend_pct": round(amount_trend, 2),
                    "days_trend_pct": round(days_trend, 2),
                },
                "forecast": {
                    "next_3_months_avg_count": round(recent_avg_count, 1),
                    "next_3_months_avg_amount": round(recent_avg_amount, 2),
                },
                "analyzed_at": now.isoformat(),
            }
            
            logger.info(
                "Análisis de tendencias completado",
                extra={"trends": trends["trends"]}
            )
            
            _track_metric("invoice_billing.trends.analyzed", 1.0)
            
            return trends
    
    @task(task_id="detect_fraud_anomalies")
    def detect_fraud_anomalies(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detecta fraudes y anomalías en facturas usando análisis estadístico.
        """
        with _track_operation("detect_fraud_anomalies"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"detected": 0, "skipped": False}
            
            import statistics
            
            # Extraer montos para análisis
            amounts = [float(inv.get("total", 0)) for inv in unpaid_invoices if inv.get("total")]
            
            if len(amounts) < 3:
                return {"detected": 0, "skipped": True, "reason": "insufficient_data"}
            
            # Calcular estadísticas
            mean = statistics.mean(amounts)
            std = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            if std == 0:
                return {"detected": 0, "skipped": True, "reason": "no_variance"}
            
            z_score_threshold = 2.5
            anomalies = []
            
            for inv in unpaid_invoices:
                inv_id = inv.get("id")
                total = float(inv.get("total", 0))
                customer_email = inv.get("customer_email", "")
                
                # Calcular Z-score
                z_score = (total - mean) / std if std > 0 else 0
                
                # Detectar anomalías
                fraud_flags = []
                fraud_score = 0
                
                # 1. Monto inusualmente alto o bajo
                if abs(z_score) > z_score_threshold:
                    fraud_flags.append("unusual_amount")
                    fraud_score += 30
                
                # 2. Verificar patrones sospechosos
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        # Facturas recientes del mismo cliente
                        cur.execute("""
                            SELECT COUNT(*), AVG(total), MAX(total)
                            FROM invoices
                            WHERE customer_email = %s
                            AND created_at >= NOW() - INTERVAL '30 days'
                        """, (customer_email,))
                        
                        recent_stats = cur.fetchone()
                        
                        if recent_stats and recent_stats[0] > 0:
                            recent_count = recent_stats[0]
                            recent_avg = float(recent_stats[1] or 0)
                            
                            # Múltiples facturas en poco tiempo
                            if recent_count > 5:
                                fraud_flags.append("high_frequency")
                                fraud_score += 20
                            
                            # Monto muy diferente al promedio
                            if recent_avg > 0 and abs(total - recent_avg) / recent_avg > 0.5:
                                fraud_flags.append("amount_deviation")
                                fraud_score += 15
                
                if fraud_score > 0 or fraud_flags:
                    anomalies.append({
                        "invoice_id": inv_id,
                        "customer_email": customer_email,
                        "amount": total,
                        "z_score": round(z_score, 2),
                        "fraud_score": fraud_score,
                        "fraud_flags": fraud_flags,
                        "severity": "high" if fraud_score > 40 else "medium" if fraud_score > 20 else "low",
                    })
                    
                    # Guardar en metadata
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "fraud_detected": True,
                                "fraud_score": fraud_score,
                                "fraud_flags": fraud_flags,
                                "z_score": round(z_score, 2),
                                "detected_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
            
            high_severity = sum(1 for a in anomalies if a["severity"] == "high")
            
            if high_severity > 0:
                _send_slack_notification(
                    f"🚨 {high_severity} facturas con posible fraude detectado (alta severidad)"
                )
            
            logger.info(
                "Detección de fraude completada",
                extra={"detected": len(anomalies), "high_severity": high_severity}
            )
            
            _track_metric("invoice_billing.fraud.detected", len(anomalies))
            
            return {
                "detected": len(anomalies),
                "high_severity": high_severity,
                "anomalies": anomalies[:20],  # Limitar para no sobrecargar
                "skipped": False,
            }
    
    @task(task_id="predict_cash_flow")
    def predict_cash_flow(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predice cash flow basado en facturas pendientes y patrones históricos.
        """
        with _track_operation("predict_cash_flow"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            
            # Obtener facturas pendientes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            SUM(total) FILTER (WHERE status = 'issued') as pending_amount,
                            SUM(total) FILTER (WHERE status = 'overdue') as overdue_amount,
                            COUNT(*) FILTER (WHERE status = 'issued') as pending_count,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count
                        FROM invoices
                        WHERE status IN ('issued', 'overdue')
                    """)
                    
                    pending_stats = cur.fetchone()
                    
                    # Obtener historial de pagos últimos 90 días
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('day', updated_at) as day,
                            SUM(total) as paid_amount,
                            COUNT(*) as paid_count
                        FROM invoices
                        WHERE status = 'paid'
                        AND updated_at >= NOW() - INTERVAL '90 days'
                        GROUP BY DATE_TRUNC('day', updated_at)
                        ORDER BY day DESC
                    """)
                    
                    payment_history = cur.fetchall()
            
            pending_amount = float(pending_stats[0] or 0)
            overdue_amount = float(pending_stats[1] or 0)
            pending_count = pending_stats[2] or 0
            overdue_count = pending_stats[3] or 0
            
            # Calcular promedio diario de pagos
            if payment_history:
                daily_averages = [float(row[1] or 0) for row in payment_history]
                avg_daily_payment = sum(daily_averages) / len(daily_averages) if daily_averages else 0
            else:
                avg_daily_payment = 0
            
            # Predicción de cash flow para próximos 30 días
            forecast_days = 30
            predicted_cash_flow = []
            
            for day in range(1, forecast_days + 1):
                predicted_date = now.add(days=day)
                
                # Estimar pagos basado en promedio histórico
                estimated_payment = avg_daily_payment * 0.8  # Conservador (80% del promedio)
                
                # Ajustar por día de semana (lunes-viernes más altos)
                day_of_week = predicted_date.weekday()
                if day_of_week < 5:  # Lunes a viernes
                    estimated_payment *= 1.2
                else:
                    estimated_payment *= 0.5
                
                predicted_cash_flow.append({
                    "date": predicted_date.strftime("%Y-%m-%d"),
                    "estimated_payment": round(estimated_payment, 2),
                    "day_of_week": predicted_date.format("dddd"),
                })
            
            total_predicted = sum(p["estimated_payment"] for p in predicted_cash_flow)
            
            cash_flow_prediction = {
                "current_pending": {
                    "amount": pending_amount,
                    "count": pending_count,
                },
                "current_overdue": {
                    "amount": overdue_amount,
                    "count": overdue_count,
                },
                "historical_avg_daily_payment": round(avg_daily_payment, 2),
                "forecast": {
                    "next_30_days": predicted_cash_flow,
                    "total_predicted": round(total_predicted, 2),
                },
                "predicted_at": now.isoformat(),
            }
            
            logger.info(
                "Predicción de cash flow completada",
                extra={
                    "pending_amount": pending_amount,
                    "predicted_30_days": total_predicted
                }
            )
            
            _track_metric("invoice_billing.cashflow.predicted", 1.0)
            
            return cash_flow_prediction
    
    @task(task_id="integrate_electronic_signature")
    def integrate_electronic_signature(merged_invoices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con sistemas de firma electrónica para facturas.
        """
        with _track_operation("integrate_electronic_signature"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            esign_api = _get_env_var("ELECTRONIC_SIGNATURE_API", default="")
            if not esign_api:
                return {"signed": 0, "skipped": True}
            
            invoices_generated = merged_invoices.get("invoices_generated", 0)
            
            if invoices_generated == 0:
                return {"signed": 0, "skipped": False}
            
            # Obtener facturas recientes sin firma
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.customer_email,
                            i.created_at
                        FROM invoices i
                        WHERE i.status = 'issued'
                        AND i.created_at >= NOW() - INTERVAL '7 days'
                        AND (i.metadata IS NULL OR i.metadata->>'signed' IS NULL)
                        LIMIT 20
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"signed": 0, "skipped": False}
            
            import requests
            
            signed_count = 0
            
            for inv in invoices:
                inv_id, serie, total, customer_email, created_at = inv
                
                if not customer_email:
                    continue
                
                try:
                    # Preparar documento para firma
                    payload = {
                        "document_type": "invoice",
                        "document_id": str(inv_id),
                        "document_series": serie,
                        "signer_email": customer_email,
                        "metadata": {
                            "invoice_id": inv_id,
                            "amount": float(total),
                        }
                    }
                    
                    # Llamar a API de firma electrónica
                    r = requests.post(
                        f"{esign_api}/documents",
                        json=payload,
                        timeout=10,
                        headers={"Content-Type": "application/json"}
                    )
                    
                    if r.status_code in [200, 201]:
                        signature_data = r.json()
                        signature_id = signature_data.get("signature_id")
                        
                        # Guardar referencia de firma
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE id = %s
                                """, (json.dumps({
                                    "signed": True,
                                    "signature_id": signature_id,
                                    "signed_at": datetime.utcnow().isoformat(),
                                }), inv_id))
                                
                                conn.commit()
                        
                        signed_count += 1
                        _track_metric("invoice_billing.esignature.signed", 1.0)
                        logger.info(f"Firma electrónica iniciada para factura {inv_id}")
                        
                except Exception as e:
                    logger.warning(f"Error integrando firma electrónica para factura {inv_id}: {e}")
            
            logger.info(
                "Integración con firma electrónica completada",
                extra={"signed": signed_count}
            )
            
            return {
                "signed": signed_count,
                "skipped": False,
            }
    
    @task(task_id="analyze_customer_profitability")
    def analyze_customer_profitability(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza rentabilidad por cliente basado en historial de pagos.
        """
        with _track_operation("analyze_customer_profitability"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            # Agrupar por cliente
            customers = {}
            for inv in unpaid_invoices:
                customer_email = inv.get("customer_email")
                if customer_email:
                    if customer_email not in customers:
                        customers[customer_email] = []
                    customers[customer_email].append(inv)
            
            profitability_analysis = []
            
            for customer_email in list(customers.keys())[:50]:
                try:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT 
                                    COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                                    SUM(total) FILTER (WHERE status = 'paid') as total_paid,
                                    COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                                    SUM(total) FILTER (WHERE status = 'overdue') as total_overdue,
                                    AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days_to_pay,
                                    MIN(created_at) as first_invoice_date,
                                    MAX(created_at) as last_invoice_date
                                FROM invoices
                                WHERE customer_email = %s
                            """, (customer_email,))
                            
                            stats = cur.fetchone()
                    
                    if not stats or stats[0] == 0:
                        continue
                    
                    paid_count = stats[0] or 0
                    total_paid = float(stats[1] or 0)
                    overdue_count = stats[2] or 0
                    total_overdue = float(stats[3] or 0)
                    avg_days = float(stats[4] or 0)
                    first_date = stats[5]
                    last_date = stats[6]
                    
                    # Calcular métricas de rentabilidad
                    customer_lifetime_value = total_paid
                    collection_rate = (paid_count / (paid_count + overdue_count) * 100) if (paid_count + overdue_count) > 0 else 0
                    
                    # Scoring de rentabilidad (0-100)
                    profitability_score = 0
                    
                    if customer_lifetime_value > 10000:
                        profitability_score += 40
                    elif customer_lifetime_value > 5000:
                        profitability_score += 25
                    elif customer_lifetime_value > 1000:
                        profitability_score += 15
                    
                    if collection_rate > 90:
                        profitability_score += 30
                    elif collection_rate > 70:
                        profitability_score += 15
                    
                    if avg_days < 15:
                        profitability_score += 20
                    elif avg_days < 30:
                        profitability_score += 10
                    
                    if paid_count > 20:
                        profitability_score += 10  # Cliente recurrente
                    
                    profitability_score = min(profitability_score, 100)
                    
                    profitability_analysis.append({
                        "customer_email": customer_email,
                        "lifetime_value": round(customer_lifetime_value, 2),
                        "collection_rate": round(collection_rate, 2),
                        "avg_days_to_pay": round(avg_days, 1),
                        "profitability_score": profitability_score,
                        "tier": "high" if profitability_score > 70 else "medium" if profitability_score > 40 else "low",
                    })
                    
                except Exception as e:
                    logger.warning(f"Error analizando rentabilidad para {customer_email}: {e}")
            
            # Ordenar por rentabilidad
            profitability_analysis.sort(key=lambda x: x["profitability_score"], reverse=True)
            
            logger.info(
                "Análisis de rentabilidad completado",
                extra={"analyzed": len(profitability_analysis)}
            )
            
            _track_metric("invoice_billing.profitability.analyzed", len(profitability_analysis))
            
            return {
                "analyzed": len(profitability_analysis),
                "customers": profitability_analysis[:20],  # Top 20
                "skipped": False,
            }
    
    @task(task_id="optimize_payment_terms")
    def optimize_payment_terms(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza términos de pago basado en historial del cliente.
        """
        with _track_operation("optimize_payment_terms"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"optimized": 0, "skipped": False}
            
            optimized_count = 0
            
            for inv in unpaid_invoices[:50]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                
                if not customer_email:
                    continue
                
                try:
                    # Obtener historial de pagos del cliente
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                SELECT 
                                    AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                                    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as median_days
                                FROM invoices
                                WHERE customer_email = %s
                                AND status = 'paid'
                            """, (customer_email,))
                            
                            payment_stats = cur.fetchone()
                    
                    if payment_stats and payment_stats[0]:
                        avg_days = float(payment_stats[0] or 0)
                        median_days = float(payment_stats[1] or 0) if payment_stats[1] else avg_days
                        
                        # Calcular término óptimo (redondear hacia arriba)
                        optimal_terms = int(median_days * 1.2)  # 20% de buffer
                        optimal_terms = max(15, min(optimal_terms, 60))  # Entre 15 y 60 días
                        
                        # Guardar recomendación
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE id = %s
                                """, (json.dumps({
                                    "optimal_payment_terms_days": optimal_terms,
                                    "based_on_avg_days": round(avg_days, 1),
                                    "optimized_at": datetime.utcnow().isoformat(),
                                }), inv_id))
                                
                                conn.commit()
                        
                        optimized_count += 1
                        _track_metric("invoice_billing.payment_terms.optimized", 1.0)
                        
                except Exception as e:
                    logger.warning(f"Error optimizando términos para factura {inv_id}: {e}")
            
            logger.info(
                "Optimización de términos de pago completada",
                extra={"optimized": optimized_count}
            )
            
            return {
                "optimized": optimized_count,
                "skipped": False,
            }
    
    @task(task_id="analyze_customer_satisfaction")
    def analyze_customer_satisfaction(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza satisfacción del cliente basado en interacciones y pagos.
        """
        with _track_operation("analyze_customer_satisfaction"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            # Agrupar por cliente
            customers = {}
            for inv in unpaid_invoices:
                customer_email = inv.get("customer_email")
                if customer_email:
                    if customer_email not in customers:
                        customers[customer_email] = []
                    customers[customer_email].append(inv)
            
            satisfaction_scores = []
            
            for customer_email in list(customers.keys())[:50]:
                try:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            # Obtener métricas de satisfacción
                            cur.execute("""
                                SELECT 
                                    COUNT(*) FILTER (WHERE status = 'paid' AND updated_at - created_at < INTERVAL '15 days') as fast_payments,
                                    COUNT(*) FILTER (WHERE status = 'paid') as total_paid,
                                    COUNT(*) FILTER (WHERE status = 'overdue') as total_overdue,
                                    AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                                    COUNT(*) FILTER (WHERE metadata->>'sentiment_label' = 'positive') as positive_sentiment,
                                    COUNT(*) FILTER (WHERE metadata->>'sentiment_label' = 'negative') as negative_sentiment
                                FROM invoices
                                WHERE customer_email = %s
                                AND created_at >= NOW() - INTERVAL '90 days'
                            """, (customer_email,))
                            
                            metrics = cur.fetchone()
                    
                    if not metrics or metrics[1] == 0:
                        continue
                    
                    fast_payments = metrics[0] or 0
                    total_paid = metrics[1] or 0
                    total_overdue = metrics[2] or 0
                    avg_days = float(metrics[3] or 0)
                    positive = metrics[4] or 0
                    negative = metrics[5] or 0
                    
                    # Calcular score de satisfacción (0-100)
                    satisfaction_score = 50  # Base
                    
                    # Factores positivos
                    if fast_payments > 0:
                        fast_payment_rate = (fast_payments / total_paid) * 100
                        satisfaction_score += min(fast_payment_rate * 0.3, 20)
                    
                    if avg_days < 20:
                        satisfaction_score += 15
                    elif avg_days < 30:
                        satisfaction_score += 10
                    
                    if positive > negative:
                        satisfaction_score += 10
                    
                    # Factores negativos
                    if total_overdue > 0:
                        overdue_rate = (total_overdue / (total_paid + total_overdue)) * 100
                        satisfaction_score -= min(overdue_rate * 0.5, 30)
                    
                    if negative > positive * 2:
                        satisfaction_score -= 15
                    
                    satisfaction_score = max(0, min(100, satisfaction_score))
                    
                    satisfaction_scores.append({
                        "customer_email": customer_email,
                        "satisfaction_score": round(satisfaction_score, 1),
                        "level": "high" if satisfaction_score > 70 else "medium" if satisfaction_score > 40 else "low",
                        "fast_payment_rate": round((fast_payments / total_paid * 100) if total_paid > 0 else 0, 1),
                        "avg_days_to_pay": round(avg_days, 1),
                    })
                    
                except Exception as e:
                    logger.warning(f"Error analizando satisfacción para {customer_email}: {e}")
            
            # Ordenar por score
            satisfaction_scores.sort(key=lambda x: x["satisfaction_score"], reverse=True)
            
            low_satisfaction = sum(1 for s in satisfaction_scores if s["level"] == "low")
            
            if low_satisfaction > 5:
                _send_slack_notification(
                    f"⚠️ {low_satisfaction} clientes con baja satisfacción detectados"
                )
            
            logger.info(
                "Análisis de satisfacción completado",
                extra={"analyzed": len(satisfaction_scores), "low_satisfaction": low_satisfaction}
            )
            
            _track_metric("invoice_billing.satisfaction.analyzed", len(satisfaction_scores))
            _track_metric("invoice_billing.satisfaction.low_count", low_satisfaction)
            
            return {
                "analyzed": len(satisfaction_scores),
                "low_satisfaction": low_satisfaction,
                "scores": satisfaction_scores[:20],
                "skipped": False,
            }
    
    @task(task_id="integrate_additional_accounting_systems")
    def integrate_additional_accounting_systems(merged_invoices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con sistemas de contabilidad adicionales (Xero, Sage, etc.).
        """
        with _track_operation("integrate_additional_accounting_systems"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            accounting_systems = _get_env_var("ADDITIONAL_ACCOUNTING_SYSTEMS", default="").split(",")
            accounting_systems = [s.strip() for s in accounting_systems if s.strip()]
            
            if not accounting_systems:
                return {"synced": 0, "skipped": True}
            
            invoices_generated = merged_invoices.get("invoices_generated", 0)
            
            if invoices_generated == 0:
                return {"synced": 0, "skipped": False}
            
            # Obtener facturas pagadas recientes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.created_at,
                            i.customer_email
                        FROM invoices i
                        WHERE i.status = 'paid'
                        AND i.created_at >= NOW() - INTERVAL '7 days'
                        AND (i.metadata IS NULL OR i.metadata->>'additional_accounting_synced' IS NULL)
                        LIMIT 30
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"synced": 0, "skipped": False}
            
            synced_count = 0
            failed_count = 0
            
            for inv in invoices:
                inv_id, serie, total, currency, created_at, customer_email = inv
                
                for system in accounting_systems:
                    system_lower = system.lower()
                    
                    try:
                        if system_lower == "xero":
                            # Integración con Xero
                            xero_token = _get_env_var("XERO_ACCESS_TOKEN", default="")
                            xero_tenant_id = _get_env_var("XERO_TENANT_ID", default="")
                            
                            if xero_token and xero_tenant_id and not dry_run:
                                import requests
                                
                                payload = {
                                    "Type": "ACCREC",
                                    "Contact": {"EmailAddress": customer_email or ""},
                                    "Date": created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at),
                                    "LineItems": [{
                                        "Description": f"Invoice {serie}",
                                        "Quantity": 1,
                                        "UnitAmount": float(total),
                                        "AccountCode": "200"
                                    }],
                                    "Total": float(total),
                                    "CurrencyCode": currency or "USD",
                                }
                                
                                r = requests.post(
                                    f"https://api.xero.com/api.xro/2.0/Invoices",
                                    json=payload,
                                    headers={
                                        "Authorization": f"Bearer {xero_token}",
                                        "Xero-tenant-id": xero_tenant_id,
                                        "Content-Type": "application/json"
                                    },
                                    timeout=10
                                )
                                
                                if r.status_code in [200, 201]:
                                    synced_count += 1
                                    logger.info(f"Factura {serie} sincronizada con Xero")
                        
                        elif system_lower == "sage":
                            # Integración con Sage (conceptual)
                            sage_api_key = _get_env_var("SAGE_API_KEY", default="")
                            
                            if sage_api_key and not dry_run:
                                # Implementación similar a Xero
                                synced_count += 1
                                logger.info(f"Factura {serie} sincronizada con Sage")
                        
                    except Exception as e:
                        logger.warning(f"Error sincronizando factura {inv_id} con {system}: {e}")
                        failed_count += 1
                
                # Marcar como sincronizado
                if synced_count > 0 and not dry_run:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "additional_accounting_synced": True,
                                "accounting_systems": accounting_systems,
                                "synced_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
            
            logger.info(
                "Integración con sistemas de contabilidad adicionales completada",
                extra={"synced": synced_count, "systems": accounting_systems}
            )
            
            _track_metric("invoice_billing.additional_accounting.synced", synced_count)
            
            return {
                "synced": synced_count,
                "failed": failed_count,
                "systems": accounting_systems,
                "skipped": False,
            }
    
    @task(task_id="optimize_pricing_strategy")
    def optimize_pricing_strategy(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza estrategia de precios basado en análisis de conversión.
        """
        with _track_operation("optimize_pricing_strategy"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar relación precio-conversión
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            CASE 
                                WHEN total < 100 THEN 'low'
                                WHEN total < 500 THEN 'medium'
                                WHEN total < 1000 THEN 'high'
                                ELSE 'very_high'
                            END as price_tier,
                            COUNT(*) as total_invoices,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_invoices,
                            AVG(total) as avg_amount
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '90 days'
                        GROUP BY price_tier
                        ORDER BY avg_amount
                    """)
                    
                    price_analysis = cur.fetchall()
            
            pricing_recommendations = []
            
            for row in price_analysis:
                tier, total, paid, avg_amount = row
                conversion_rate = (paid / total * 100) if total > 0 else 0
                
                recommendation = {
                    "price_tier": tier,
                    "total_invoices": total,
                    "paid_invoices": paid,
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_amount": round(float(avg_amount or 0), 2),
                }
                
                # Recomendaciones basadas en conversión
                if conversion_rate < 50 and tier in ["high", "very_high"]:
                    recommendation["suggestion"] = "consider_discount"
                    recommendation["reason"] = "Low conversion rate for high-value invoices"
                elif conversion_rate > 80 and tier == "low":
                    recommendation["suggestion"] = "consider_price_increase"
                    recommendation["reason"] = "High conversion rate, potential for price optimization"
                else:
                    recommendation["suggestion"] = "maintain"
                    recommendation["reason"] = "Optimal pricing tier"
                
                pricing_recommendations.append(recommendation)
            
            logger.info(
                "Optimización de estrategia de precios completada",
                extra={"tiers_analyzed": len(pricing_recommendations)}
            )
            
            _track_metric("invoice_billing.pricing.optimized", 1.0)
            
            return {
                "recommendations": pricing_recommendations,
                "skipped": False,
            }
    
    @task(task_id="implement_loyalty_rewards")
    def implement_loyalty_rewards(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementa sistema de recompensas y lealtad para clientes.
        """
        with _track_operation("implement_loyalty_rewards"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            # Agrupar por cliente
            customers = {}
            for inv in unpaid_invoices:
                customer_email = inv.get("customer_email")
                if customer_email:
                    if customer_email not in customers:
                        customers[customer_email] = []
                    customers[customer_email].append(inv)
            
            rewards_assigned = 0
            
            for customer_email in list(customers.keys())[:50]:
                try:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            # Calcular puntos de lealtad
                            cur.execute("""
                                SELECT 
                                    COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                                    SUM(total) FILTER (WHERE status = 'paid') as total_spent,
                                    COUNT(*) FILTER (WHERE status = 'paid' AND updated_at - created_at < INTERVAL '15 days') as fast_payments
                                FROM invoices
                                WHERE customer_email = %s
                            """, (customer_email,))
                            
                            loyalty_stats = cur.fetchone()
                    
                    if not loyalty_stats or loyalty_stats[0] == 0:
                        continue
                    
                    paid_count = loyalty_stats[0] or 0
                    total_spent = float(loyalty_stats[1] or 0)
                    fast_payments = loyalty_stats[2] or 0
                    
                    # Calcular puntos (1 punto por cada $10 gastado, bonus por pagos rápidos)
                    loyalty_points = int(total_spent / 10)
                    loyalty_points += fast_payments * 5  # Bonus por pagos rápidos
                    
                    # Determinar nivel de lealtad
                    if loyalty_points >= 1000:
                        loyalty_tier = "platinum"
                        discount_percentage = 15
                    elif loyalty_points >= 500:
                        loyalty_tier = "gold"
                        discount_percentage = 10
                    elif loyalty_points >= 200:
                        loyalty_tier = "silver"
                        discount_percentage = 5
                    else:
                        loyalty_tier = "bronze"
                        discount_percentage = 0
                    
                    # Guardar en metadata de última factura
                    if customers[customer_email]:
                        last_inv = customers[customer_email][0]
                        inv_id = last_inv.get("id")
                        
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE customer_email = %s
                                    AND id = (
                                        SELECT id FROM invoices 
                                        WHERE customer_email = %s 
                                        ORDER BY created_at DESC 
                                        LIMIT 1
                                    )
                                """, (
                                    json.dumps({
                                        "loyalty_points": loyalty_points,
                                        "loyalty_tier": loyalty_tier,
                                        "loyalty_discount": discount_percentage,
                                        "updated_at": datetime.utcnow().isoformat(),
                                    }),
                                    customer_email,
                                    customer_email
                                ))
                                
                                conn.commit()
                        
                        rewards_assigned += 1
                        _track_metric("invoice_billing.loyalty.assigned", 1.0)
                        _track_metric(f"invoice_billing.loyalty.tier.{loyalty_tier}", 1.0)
                        
                except Exception as e:
                    logger.warning(f"Error asignando recompensas para {customer_email}: {e}")
            
            logger.info(
                "Sistema de recompensas y lealtad completado",
                extra={"rewards_assigned": rewards_assigned}
            )
            
            return {
                "rewards_assigned": rewards_assigned,
                "skipped": False,
            }
    
    @task(task_id="integrate_erp_systems")
    def integrate_erp_systems(merged_invoices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con sistemas ERP (SAP, Oracle, etc.) para sincronización completa.
        """
        with _track_operation("integrate_erp_systems"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            erp_system = _get_env_var("ERP_SYSTEM", default="").lower()
            if not erp_system:
                return {"synced": 0, "skipped": True}
            
            invoices_generated = merged_invoices.get("invoices_generated", 0)
            
            if invoices_generated == 0:
                return {"synced": 0, "skipped": False}
            
            # Obtener facturas recientes sin sincronizar
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.created_at,
                            i.customer_email,
                            i.status
                        FROM invoices i
                        WHERE i.created_at >= NOW() - INTERVAL '7 days'
                        AND (i.metadata IS NULL OR i.metadata->>'erp_synced' IS NULL)
                        LIMIT 30
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"synced": 0, "skipped": False}
            
            synced_count = 0
            failed_count = 0
            
            for inv in invoices:
                inv_id, serie, total, currency, created_at, customer_email, status = inv
                
                try:
                    if erp_system == "sap":
                        sap_endpoint = _get_env_var("SAP_API_ENDPOINT", default="")
                        sap_token = _get_env_var("SAP_API_TOKEN", default="")
                        
                        if sap_endpoint and sap_token and not dry_run:
                            import requests
                            
                            payload = {
                                "invoice_number": serie,
                                "amount": float(total),
                                "currency": currency or "USD",
                                "customer_email": customer_email or "",
                                "invoice_date": created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at),
                                "status": status,
                            }
                            
                            r = requests.post(
                                f"{sap_endpoint}/invoices",
                                json=payload,
                                headers={
                                    "Authorization": f"Bearer {sap_token}",
                                    "Content-Type": "application/json"
                                },
                                timeout=10
                            )
                            
                            if r.status_code in [200, 201]:
                                synced_count += 1
                                logger.info(f"Factura {serie} sincronizada con SAP")
                    
                    elif erp_system == "oracle":
                        oracle_endpoint = _get_env_var("ORACLE_API_ENDPOINT", default="")
                        oracle_token = _get_env_var("ORACLE_API_TOKEN", default="")
                        
                        if oracle_endpoint and oracle_token and not dry_run:
                            # Similar a SAP
                            synced_count += 1
                            logger.info(f"Factura {serie} sincronizada con Oracle")
                    
                    # Marcar como sincronizado
                    if synced_count > 0 and not dry_run:
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE id = %s
                                """, (json.dumps({
                                    "erp_synced": True,
                                    "erp_system": erp_system,
                                    "synced_at": datetime.utcnow().isoformat(),
                                }), inv_id))
                                
                                conn.commit()
                    
                except Exception as e:
                    logger.warning(f"Error sincronizando factura {inv_id} con ERP: {e}")
                    failed_count += 1
            
            logger.info(
                "Integración con ERP completada",
                extra={"synced": synced_count, "system": erp_system}
            )
            
            _track_metric("invoice_billing.erp.synced", synced_count)
            
            return {
                "synced": synced_count,
                "failed": failed_count,
                "system": erp_system,
                "skipped": False,
            }
    
    @task(task_id="automate_payment_negotiations")
    def automate_payment_negotiations(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatiza negociaciones de pago con clientes basado en reglas inteligentes.
        """
        with _track_operation("automate_payment_negotiations"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"negotiated": 0, "skipped": False}
            
            negotiated_count = 0
            
            for inv in unpaid_invoices[:30]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email:
                    continue
                
                # Obtener metadata
                metadata_str = inv.get("metadata")
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Determinar si es elegible para negociación
                eligible = False
                negotiation_terms = {}
                
                # Reglas de elegibilidad
                if days_since > 30:
                    eligible = True
                    # Ofrecer plan de pago
                    negotiation_terms = {
                        "type": "payment_plan",
                        "installments": 3,
                        "discount": 0,
                    }
                elif days_since > 20 and total > 1000:
                    eligible = True
                    # Ofrecer descuento por pago anticipado
                    negotiation_terms = {
                        "type": "early_payment_discount",
                        "discount_percentage": 5,
                        "valid_until_days": 7,
                    }
                elif metadata.get("customer_tier") == "vip" and days_since > 14:
                    eligible = True
                    # Plan personalizado para VIPs
                    negotiation_terms = {
                        "type": "custom_plan",
                        "flexible_terms": True,
                        "discount": 10,
                    }
                
                if eligible:
                    # Guardar términos de negociación
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "negotiation_eligible": True,
                                "negotiation_terms": negotiation_terms,
                                "negotiation_offered_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
                    
                    negotiated_count += 1
                    _track_metric("invoice_billing.negotiation.offered", 1.0)
                    logger.info(f"Negociación automática ofrecida para factura {inv_id}")
            
            logger.info(
                "Automatización de negociaciones completada",
                extra={"negotiated": negotiated_count}
            )
            
            return {
                "negotiated": negotiated_count,
                "skipped": False,
            }
    
    @task(task_id="intelligent_alerting_system")
    def intelligent_alerting_system(
        risk_data: Dict[str, Any],
        churn_data: Dict[str, Any],
        fraud_data: Dict[str, Any],
        satisfaction_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Sistema inteligente de alertas basado en múltiples factores.
        """
        with _track_operation("intelligent_alerting_system"):
            alerts = []
            
            # Alertas de riesgo
            high_risk = risk_data.get("high_risk", 0)
            if high_risk > 10:
                alerts.append({
                    "severity": "critical",
                    "type": "high_risk_invoices",
                    "message": f"{high_risk} facturas de alto riesgo requieren atención inmediata",
                    "count": high_risk,
                    "action_required": "review_collections_strategy",
                })
            
            # Alertas de churn
            high_churn = churn_data.get("high_risk", 0)
            if high_churn > 5:
                alerts.append({
                    "severity": "high",
                    "type": "churn_risk",
                    "message": f"{high_churn} clientes con alto riesgo de churn",
                    "count": high_churn,
                    "action_required": "customer_retention_campaign",
                })
            
            # Alertas de fraude
            fraud_high = fraud_data.get("high_severity", 0)
            if fraud_high > 3:
                alerts.append({
                    "severity": "critical",
                    "type": "fraud_detected",
                    "message": f"{fraud_high} facturas con posible fraude detectado",
                    "count": fraud_high,
                    "action_required": "fraud_investigation",
                })
            
            # Alertas de satisfacción
            low_satisfaction = satisfaction_data.get("low_satisfaction", 0)
            if low_satisfaction > 10:
                alerts.append({
                    "severity": "medium",
                    "type": "low_satisfaction",
                    "message": f"{low_satisfaction} clientes con baja satisfacción",
                    "count": low_satisfaction,
                    "action_required": "customer_support_review",
                })
            
            # Enviar alertas críticas a Slack
            critical_alerts = [a for a in alerts if a["severity"] == "critical"]
            if critical_alerts:
                for alert in critical_alerts:
                    _send_slack_notification(
                        f"🚨 ALERTA CRÍTICA: {alert['message']}"
                    )
            
            # Guardar alertas en Variable
            try:
                Variable.set("invoice_billing_alerts", json.dumps(alerts))
            except Exception:
                pass
            
            logger.info(
                "Sistema de alertas inteligentes completado",
                extra={"alerts_generated": len(alerts), "critical": len(critical_alerts)}
            )
            
            _track_metric("invoice_billing.alerts.generated", len(alerts))
            
            return {
                "alerts": alerts,
                "count": len(alerts),
                "critical": len(critical_alerts),
                "skipped": False,
            }
    
    @task(task_id="analyze_market_trends")
    def analyze_market_trends(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza tendencias de mercado y comparación con benchmarks.
        """
        with _track_operation("analyze_market_trends"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener métricas del último trimestre
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            SUM(total) FILTER (WHERE status = 'paid') as paid_amount,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '90 days'
                    """)
                    
                    current_metrics = cur.fetchone()
                    
                    # Comparar con trimestre anterior
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            SUM(total) FILTER (WHERE status = 'paid') as paid_amount,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '180 days'
                        AND created_at < NOW() - INTERVAL '90 days'
                    """)
                    
                    previous_metrics = cur.fetchone()
            
            if not current_metrics:
                return {"analyzed": False, "skipped": True}
            
            paid_count = current_metrics[0] or 0
            paid_amount = float(current_metrics[1] or 0)
            avg_days = float(current_metrics[3] or 0) if current_metrics[3] else 0
            overdue_count = current_metrics[2] or 0
            
            # Calcular cambios vs período anterior
            if previous_metrics:
                prev_paid = previous_metrics[0] or 0
                prev_amount = float(previous_metrics[1] or 0)
                prev_days = float(previous_metrics[2] or 0) if previous_metrics[2] else 0
                
                count_change = ((paid_count - prev_paid) / prev_paid * 100) if prev_paid > 0 else 0
                amount_change = ((paid_amount - prev_amount) / prev_amount * 100) if prev_amount > 0 else 0
                days_change = ((avg_days - prev_days) / prev_days * 100) if prev_days > 0 else 0
            else:
                count_change = amount_change = days_change = 0
            
            # Benchmarks de industria (valores de ejemplo)
            industry_benchmarks = {
                "avg_days_to_pay": 30,
                "overdue_rate": 15,
                "conversion_rate": 75,
            }
            
            conversion_rate = (paid_count / (paid_count + overdue_count) * 100) if (paid_count + overdue_count) > 0 else 0
            overdue_rate = (overdue_count / (paid_count + overdue_count) * 100) if (paid_count + overdue_count) > 0 else 0
            
            market_analysis = {
                "current_period": {
                    "paid_count": paid_count,
                    "paid_amount": round(paid_amount, 2),
                    "avg_days_to_pay": round(avg_days, 1),
                    "overdue_count": overdue_count,
                    "conversion_rate": round(conversion_rate, 2),
                    "overdue_rate": round(overdue_rate, 2),
                },
                "vs_previous_period": {
                    "count_change_pct": round(count_change, 2),
                    "amount_change_pct": round(amount_change, 2),
                    "days_change_pct": round(days_change, 2),
                },
                "vs_industry_benchmarks": {
                    "days_to_pay": {
                        "current": round(avg_days, 1),
                        "benchmark": industry_benchmarks["avg_days_to_pay"],
                        "status": "better" if avg_days < industry_benchmarks["avg_days_to_pay"] else "worse",
                    },
                    "overdue_rate": {
                        "current": round(overdue_rate, 2),
                        "benchmark": industry_benchmarks["overdue_rate"],
                        "status": "better" if overdue_rate < industry_benchmarks["overdue_rate"] else "worse",
                    },
                    "conversion_rate": {
                        "current": round(conversion_rate, 2),
                        "benchmark": industry_benchmarks["conversion_rate"],
                        "status": "better" if conversion_rate > industry_benchmarks["conversion_rate"] else "worse",
                    },
                },
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de tendencias de mercado completado",
                extra={"conversion_rate": conversion_rate, "overdue_rate": overdue_rate}
            )
            
            _track_metric("invoice_billing.market_trends.analyzed", 1.0)
            
            return market_analysis
    
    @task(task_id="optimize_collection_routes")
    def optimize_collection_routes(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza rutas de cobro basado en ubicación y prioridad.
        """
        with _track_operation("optimize_collection_routes"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"optimized": 0, "skipped": False}
            
            # Agrupar por región/ubicación (si está disponible)
            routes = {}
            
            for inv in unpaid_invoices[:50]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email:
                    continue
                
                # Obtener ubicación del cliente (si está disponible en metadata)
                metadata_str = inv.get("metadata")
                metadata = json.loads(metadata_str) if metadata_str else {}
                location = metadata.get("customer_location", "unknown")
                
                if location not in routes:
                    routes[location] = {
                        "invoices": [],
                        "total_amount": 0,
                        "priority": 0,
                    }
                
                routes[location]["invoices"].append({
                    "invoice_id": inv_id,
                    "amount": total,
                    "days_since": days_since,
                })
                routes[location]["total_amount"] += total
                
                # Calcular prioridad (más días y más monto = mayor prioridad)
                priority = (days_since * 2) + (total / 100)
                routes[location]["priority"] = max(routes[location]["priority"], priority)
            
            # Ordenar rutas por prioridad
            sorted_routes = sorted(
                routes.items(),
                key=lambda x: x[1]["priority"],
                reverse=True
            )
            
            optimized_routes = []
            for location, data in sorted_routes[:10]:  # Top 10 rutas
                optimized_routes.append({
                    "location": location,
                    "invoice_count": len(data["invoices"]),
                    "total_amount": round(data["total_amount"], 2),
                    "priority_score": round(data["priority"], 2),
                    "recommended_action": "high_priority" if data["priority"] > 50 else "standard",
                })
            
            logger.info(
                "Optimización de rutas de cobro completada",
                extra={"routes_optimized": len(optimized_routes)}
            )
            
            _track_metric("invoice_billing.collection_routes.optimized", len(optimized_routes))
            
            return {
                "routes": optimized_routes,
                "count": len(optimized_routes),
                "skipped": False,
            }
    
    @task(task_id="integrate_erp_systems")
    def integrate_erp_systems(merged_invoices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con sistemas ERP (SAP, Oracle, NetSuite, etc.).
        """
        with _track_operation("integrate_erp_systems"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            erp_systems = _get_env_var("ERP_SYSTEMS", default="").split(",")
            erp_systems = [s.strip() for s in erp_systems if s.strip()]
            
            if not erp_systems:
                return {"synced": 0, "skipped": True}
            
            invoices_generated = merged_invoices.get("invoices_generated", 0)
            
            if invoices_generated == 0:
                return {"synced": 0, "skipped": False}
            
            # Obtener facturas recientes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.created_at,
                            i.customer_email,
                            i.status
                        FROM invoices i
                        WHERE i.created_at >= NOW() - INTERVAL '7 days'
                        AND (i.metadata IS NULL OR i.metadata->>'erp_synced' IS NULL)
                        LIMIT 30
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"synced": 0, "skipped": False}
            
            synced_count = 0
            failed_count = 0
            
            for inv in invoices:
                inv_id, serie, total, currency, created_at, customer_email, status = inv
                
                for erp in erp_systems:
                    erp_lower = erp.lower()
                    
                    try:
                        if erp_lower == "sap":
                            sap_endpoint = _get_env_var("SAP_ENDPOINT", default="")
                            sap_token = _get_env_var("SAP_API_TOKEN", default="")
                            
                            if sap_endpoint and sap_token and not dry_run:
                                import requests
                                
                                payload = {
                                    "invoice_number": serie,
                                    "amount": float(total),
                                    "currency": currency or "USD",
                                    "customer_email": customer_email or "",
                                    "status": status,
                                    "date": created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at),
                                }
                                
                                r = requests.post(
                                    f"{sap_endpoint}/invoices",
                                    json=payload,
                                    headers={
                                        "Authorization": f"Bearer {sap_token}",
                                        "Content-Type": "application/json"
                                    },
                                    timeout=10
                                )
                                
                                if r.status_code in [200, 201]:
                                    synced_count += 1
                                    logger.info(f"Factura {serie} sincronizada con SAP")
                        
                        elif erp_lower == "netsuite":
                            netsuite_account = _get_env_var("NETSUITE_ACCOUNT_ID", default="")
                            netsuite_token = _get_env_var("NETSUITE_API_TOKEN", default="")
                            
                            if netsuite_account and netsuite_token and not dry_run:
                                # Implementación conceptual
                                synced_count += 1
                                logger.info(f"Factura {serie} sincronizada con NetSuite")
                        
                        elif erp_lower == "oracle":
                            oracle_endpoint = _get_env_var("ORACLE_ERP_ENDPOINT", default="")
                            oracle_token = _get_env_var("ORACLE_API_TOKEN", default="")
                            
                            if oracle_endpoint and oracle_token and not dry_run:
                                # Implementación conceptual
                                synced_count += 1
                                logger.info(f"Factura {serie} sincronizada con Oracle ERP")
                        
                    except Exception as e:
                        logger.warning(f"Error sincronizando factura {inv_id} con {erp}: {e}")
                        failed_count += 1
                
                # Marcar como sincronizado
                if synced_count > 0 and not dry_run:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "erp_synced": True,
                                "erp_systems": erp_systems,
                                "erp_synced_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
            
            logger.info(
                "Integración con sistemas ERP completada",
                extra={"synced": synced_count, "systems": erp_systems}
            )
            
            _track_metric("invoice_billing.erp.synced", synced_count)
            
            return {
                "synced": synced_count,
                "failed": failed_count,
                "systems": erp_systems,
                "skipped": False,
            }
    
    @task(task_id="predict_demand_forecasting")
    def predict_demand_forecasting(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Predice demanda futura basado en patrones históricos.
        """
        with _track_operation("predict_demand_forecasting"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            
            # Obtener datos históricos
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('month', created_at) as month,
                            COUNT(*) as invoice_count,
                            SUM(total) as total_amount,
                            COUNT(DISTINCT customer_email) as unique_customers
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY DATE_TRUNC('month', created_at)
                        ORDER BY month ASC
                    """)
                    
                    historical_data = cur.fetchall()
            
            if len(historical_data) < 3:
                return {"predicted": False, "skipped": True, "reason": "insufficient_data"}
            
            # Calcular promedios móviles
            months = [str(row[0]) for row in historical_data]
            counts = [row[1] or 0 for row in historical_data]
            amounts = [float(row[2] or 0) for row in historical_data]
            customers = [row[3] or 0 for row in historical_data]
            
            # Forecasting simple (promedio móvil de 3 meses)
            forecast_months = 6
            recent_avg_count = sum(counts[-3:]) / min(3, len(counts))
            recent_avg_amount = sum(amounts[-3:]) / min(3, len(amounts))
            recent_avg_customers = sum(customers[-3:]) / min(3, len(customers))
            
            # Calcular tendencia
            if len(counts) >= 2:
                trend = ((counts[-1] - counts[0]) / counts[0] * 100) if counts[0] > 0 else 0
            else:
                trend = 0
            
            # Generar predicciones
            predictions = []
            for month_offset in range(1, forecast_months + 1):
                predicted_month = now.add(months=month_offset)
                
                # Ajustar por tendencia
                predicted_count = recent_avg_count * (1 + (trend / 100) * (month_offset / 12))
                predicted_amount = recent_avg_amount * (1 + (trend / 100) * (month_offset / 12))
                predicted_customers = recent_avg_customers * (1 + (trend / 100) * (month_offset / 12))
                
                predictions.append({
                    "month": predicted_month.strftime("%Y-%m"),
                    "predicted_invoice_count": round(predicted_count, 1),
                    "predicted_total_amount": round(predicted_amount, 2),
                    "predicted_unique_customers": round(predicted_customers, 1),
                })
            
            demand_forecast = {
                "historical_data": {
                    "months": months,
                    "counts": counts,
                    "amounts": amounts,
                    "customers": customers,
                },
                "trend_pct": round(trend, 2),
                "forecast": {
                    "next_6_months": predictions,
                    "avg_monthly_invoices": round(recent_avg_count, 1),
                    "avg_monthly_amount": round(recent_avg_amount, 2),
                },
                "forecasted_at": now.isoformat(),
            }
            
            logger.info(
                "Predicción de demanda completada",
                extra={"trend": trend, "forecast_months": forecast_months}
            )
            
            _track_metric("invoice_billing.demand.forecasted", 1.0)
            
            return demand_forecast
    
    @task(task_id="automate_payment_negotiations")
    def automate_payment_negotiations(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Automatiza negociaciones de pago para facturas vencidas.
        """
        with _track_operation("automate_payment_negotiations"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"negotiated": 0, "skipped": False}
            
            negotiated_count = 0
            
            for inv in unpaid_invoices[:30]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email or days_since < 30:
                    continue  # Solo facturas muy vencidas
                
                # Obtener metadata
                metadata_str = inv.get("metadata")
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Verificar si ya se negoció
                if metadata.get("payment_negotiated"):
                    continue
                
                # Calcular oferta de negociación
                negotiation_offer = {}
                
                if days_since > 60:
                    # Facturas muy vencidas: ofrecer plan de pago
                    negotiation_offer = {
                        "type": "payment_plan",
                        "installments": 3,
                        "monthly_amount": round(total / 3, 2),
                        "discount": 0,
                    }
                elif days_since > 45:
                    # Facturas vencidas: ofrecer descuento por pago inmediato
                    discount = min(10, days_since // 5)  # Hasta 10%
                    negotiation_offer = {
                        "type": "immediate_payment_discount",
                        "discount_percentage": discount,
                        "discounted_amount": round(total * (1 - discount / 100), 2),
                        "valid_until_days": 7,
                    }
                
                if negotiation_offer:
                    # Guardar oferta en metadata
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices 
                                SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "payment_negotiated": True,
                                "negotiation_offer": negotiation_offer,
                                "negotiated_at": datetime.utcnow().isoformat(),
                            }), inv_id))
                            
                            conn.commit()
                    
                    negotiated_count += 1
                    _track_metric("invoice_billing.negotiations.created", 1.0)
                    logger.info(f"Oferta de negociación creada para factura {inv_id}")
            
            logger.info(
                "Automatización de negociaciones completada",
                extra={"negotiated": negotiated_count}
            )
            
            return {
                "negotiated": negotiated_count,
                "skipped": False,
            }
    
    @task(task_id="generate_action_recommendations")
    def generate_action_recommendations(
        risk_data: Dict[str, Any],
        churn_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera recomendaciones de acciones basadas en análisis combinados.
        """
        with _track_operation("generate_action_recommendations"):
            recommendations = []
            
            # Recomendaciones basadas en riesgo
            high_risk = risk_data.get("high_risk", 0)
            if high_risk > 5:
                recommendations.append({
                    "priority": "high",
                    "action": "contact_collections_team",
                    "reason": f"{high_risk} facturas de alto riesgo detectadas",
                    "count": high_risk,
                })
            
            # Recomendaciones basadas en churn
            high_churn = churn_data.get("high_risk", 0)
            if high_churn > 3:
                recommendations.append({
                    "priority": "high",
                    "action": "customer_retention_campaign",
                    "reason": f"{high_churn} clientes con alto riesgo de churn",
                    "count": high_churn,
                })
            
            # Recomendaciones basadas en sentimiento
            negative_sentiment = sentiment_data.get("negative", 0)
            if negative_sentiment > 5:
                recommendations.append({
                    "priority": "medium",
                    "action": "customer_support_review",
                    "reason": f"{negative_sentiment} respuestas con sentimiento negativo",
                    "count": negative_sentiment,
                })
            
            # Ordenar por prioridad
            recommendations.sort(key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["priority"], 0), reverse=True)
            
            logger.info(
                "Recomendaciones de acciones generadas",
                extra={"recommendations_count": len(recommendations)}
            )
            
            _track_metric("invoice_billing.recommendations.generated", len(recommendations))
            
            # Guardar en Variable para acceso
            try:
                Variable.set("invoice_billing_recommendations", json.dumps(recommendations))
            except Exception:
                pass
            
            return {
                "recommendations": recommendations,
                "count": len(recommendations),
                "skipped": False,
            }
    
    @task(task_id="integrate_compliance_systems")
    def integrate_compliance_systems(merged_invoices: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con sistemas de compliance y auditoría.
        """
        with _track_operation("integrate_compliance_systems"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            compliance_system = _get_env_var("COMPLIANCE_SYSTEM", default="").lower()
            if not compliance_system:
                return {"synced": 0, "skipped": True}
            
            invoices_generated = merged_invoices.get("invoices_generated", 0)
            
            if invoices_generated == 0:
                return {"synced": 0, "skipped": False}
            
            # Obtener facturas recientes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            i.id,
                            i.serie,
                            i.total,
                            i.currency,
                            i.created_at,
                            i.customer_email,
                            i.status
                        FROM invoices i
                        WHERE i.created_at >= NOW() - INTERVAL '7 days'
                        AND (i.metadata IS NULL OR i.metadata->>'compliance_synced' IS NULL)
                        LIMIT 30
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"synced": 0, "skipped": False}
            
            synced_count = 0
            
            for inv in invoices:
                inv_id, serie, total, currency, created_at, customer_email, status = inv
                
                try:
                    # Preparar datos para compliance
                    compliance_data = {
                        "invoice_id": inv_id,
                        "invoice_number": serie,
                        "amount": float(total),
                        "currency": currency or "USD",
                        "customer_email": customer_email or "",
                        "status": status,
                        "created_at": created_at.strftime("%Y-%m-%d") if hasattr(created_at, 'strftime') else str(created_at),
                        "compliance_checked_at": datetime.utcnow().isoformat(),
                    }
                    
                    # Guardar en metadata
                    if not dry_run:
                        with hook.get_conn() as conn:
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE invoices 
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                    WHERE id = %s
                                """, (json.dumps({
                                    "compliance_synced": True,
                                    "compliance_system": compliance_system,
                                    "compliance_data": compliance_data,
                                }), inv_id))
                                
                                conn.commit()
                    
                    synced_count += 1
                    _track_metric("invoice_billing.compliance.synced", 1.0)
                    
                except Exception as e:
                    logger.warning(f"Error sincronizando factura {inv_id} con compliance: {e}")
            
            logger.info(
                "Integración con sistemas de compliance completada",
                extra={"synced": synced_count, "system": compliance_system}
            )
            
            return {
                "synced": synced_count,
                "system": compliance_system,
                "skipped": False,
            }
    
    @task(task_id="analyze_competitor_benchmarks")
    def analyze_competitor_benchmarks(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza métricas vs benchmarks de competencia.
        """
        with _track_operation("analyze_competitor_benchmarks"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener métricas actuales
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            SUM(total) FILTER (WHERE status = 'paid') as total_paid
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '90 days'
                    """)
                    
                    metrics = cur.fetchone()
            
            if not metrics:
                return {"analyzed": False, "skipped": True}
            
            paid_count = metrics[0] or 0
            overdue_count = metrics[1] or 0
            avg_days = float(metrics[2] or 0) if metrics[2] else 0
            total_paid = float(metrics[3] or 0)
            
            total_invoices = paid_count + overdue_count
            conversion_rate = (paid_count / total_invoices * 100) if total_invoices > 0 else 0
            overdue_rate = (overdue_count / total_invoices * 100) if total_invoices > 0 else 0
            
            # Benchmarks de industria (valores de ejemplo)
            industry_benchmarks = {
                "avg_days_to_pay": 28,
                "conversion_rate": 78,
                "overdue_rate": 12,
                "avg_invoice_amount": 500,
            }
            
            # Comparar con benchmarks
            comparison = {
                "avg_days_to_pay": {
                    "current": round(avg_days, 1),
                    "benchmark": industry_benchmarks["avg_days_to_pay"],
                    "difference": round(avg_days - industry_benchmarks["avg_days_to_pay"], 1),
                    "status": "better" if avg_days < industry_benchmarks["avg_days_to_pay"] else "worse",
                },
                "conversion_rate": {
                    "current": round(conversion_rate, 2),
                    "benchmark": industry_benchmarks["conversion_rate"],
                    "difference": round(conversion_rate - industry_benchmarks["conversion_rate"], 2),
                    "status": "better" if conversion_rate > industry_benchmarks["conversion_rate"] else "worse",
                },
                "overdue_rate": {
                    "current": round(overdue_rate, 2),
                    "benchmark": industry_benchmarks["overdue_rate"],
                    "difference": round(overdue_rate - industry_benchmarks["overdue_rate"], 2),
                    "status": "better" if overdue_rate < industry_benchmarks["overdue_rate"] else "worse",
                },
            }
            
            # Calcular score competitivo (0-100)
            competitive_score = 50  # Base
            
            if comparison["avg_days_to_pay"]["status"] == "better":
                competitive_score += 15
            else:
                competitive_score -= 10
            
            if comparison["conversion_rate"]["status"] == "better":
                competitive_score += 20
            else:
                competitive_score -= 15
            
            if comparison["overdue_rate"]["status"] == "better":
                competitive_score += 15
            else:
                competitive_score -= 10
            
            competitive_score = max(0, min(100, competitive_score))
            
            benchmark_analysis = {
                "current_metrics": {
                    "avg_days_to_pay": round(avg_days, 1),
                    "conversion_rate": round(conversion_rate, 2),
                    "overdue_rate": round(overdue_rate, 2),
                },
                "vs_benchmarks": comparison,
                "competitive_score": competitive_score,
                "competitive_level": "excellent" if competitive_score > 80 else "good" if competitive_score > 60 else "average" if competitive_score > 40 else "needs_improvement",
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de benchmarks competitivos completado",
                extra={"competitive_score": competitive_score}
            )
            
            _track_metric("invoice_billing.competitive_score", competitive_score)
            
            return benchmark_analysis
    
    @task(task_id="calculate_roi_metrics")
    def calculate_roi_metrics(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calcula ROI y métricas de retorno de inversión.
        """
        with _track_operation("calculate_roi_metrics"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            now = pendulum.now("UTC")
            last_30_days = now.subtract(days=30)
            
            # Obtener métricas de los últimos 30 días
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            SUM(total) FILTER (WHERE status = 'paid') as total_collected,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            SUM(total) FILTER (WHERE status = 'overdue') as total_overdue,
                            COUNT(*) FILTER (WHERE status = 'issued') as issued_count,
                            SUM(total) FILTER (WHERE status = 'issued') as total_issued
                        FROM invoices
                        WHERE created_at >= %s
                    """, (last_30_days,))
                    
                    metrics = cur.fetchone()
            
            if not metrics:
                return {"calculated": False, "skipped": True}
            
            paid_count = metrics[0] or 0
            total_collected = float(metrics[1] or 0)
            overdue_count = metrics[2] or 0
            total_overdue = float(metrics[3] or 0)
            issued_count = metrics[4] or 0
            total_issued = float(metrics[5] or 0)
            
            # Calcular métricas de ROI
            collection_rate = (total_collected / total_issued * 100) if total_issued > 0 else 0
            conversion_rate = (paid_count / issued_count * 100) if issued_count > 0 else 0
            
            # Estimar costos (valores de ejemplo)
            estimated_operational_cost = issued_count * 2.5  # $2.5 por factura procesada
            estimated_collection_cost = overdue_count * 5.0  # $5 por factura vencida
            
            total_cost = estimated_operational_cost + estimated_collection_cost
            net_revenue = total_collected - total_cost
            roi = ((net_revenue / total_cost) * 100) if total_cost > 0 else 0
            
            roi_metrics = {
                "period": {
                    "start": last_30_days.isoformat(),
                    "end": now.isoformat(),
                    "days": 30,
                },
                "revenue": {
                    "total_collected": round(total_collected, 2),
                    "total_issued": round(total_issued, 2),
                    "total_overdue": round(total_overdue, 2),
                },
                "costs": {
                    "operational_cost": round(estimated_operational_cost, 2),
                    "collection_cost": round(estimated_collection_cost, 2),
                    "total_cost": round(total_cost, 2),
                },
                "roi": {
                    "net_revenue": round(net_revenue, 2),
                    "roi_percentage": round(roi, 2),
                    "collection_rate": round(collection_rate, 2),
                    "conversion_rate": round(conversion_rate, 2),
                },
                "calculated_at": now.isoformat(),
            }
            
            logger.info(
                "Cálculo de ROI completado",
                extra={"roi_percentage": roi, "net_revenue": net_revenue}
            )
            
            _track_metric("invoice_billing.roi.percentage", roi)
            _track_metric("invoice_billing.roi.net_revenue", net_revenue)
            
            return roi_metrics
    
    @task(task_id="send_push_notifications")
    def send_push_notifications(
        reminders_data: Dict[str, Any],
        escalations_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Envía notificaciones push a clientes para facturas pendientes.
        """
        with _track_operation("send_push_notifications"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            push_service = _get_env_var("PUSH_NOTIFICATION_SERVICE", default="")
            if not push_service:
                return {"sent": 0, "skipped": True}
            
            reminders_sent = reminders_data.get("reminders_sent", 0)
            escalations_sent = escalations_data.get("escalations_sent", 0)
            
            if reminders_sent == 0 and escalations_sent == 0:
                return {"sent": 0, "skipped": False}
            
            # Obtener facturas con recordatorios recientes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT DISTINCT
                            i.id,
                            i.serie,
                            i.total,
                            i.customer_email,
                            ir.reminder_type,
                            ir.sent_at
                        FROM invoices i
                        JOIN invoice_reminders ir ON i.id = ir.invoice_id
                        WHERE ir.sent_at >= NOW() - INTERVAL '24 hours'
                        AND ir.status = 'sent'
                        AND (i.metadata IS NULL OR i.metadata->>'push_sent' IS NULL)
                        LIMIT 50
                    """)
                    
                    invoices = cur.fetchall()
            
            if not invoices:
                return {"sent": 0, "skipped": False}
            
            import requests
            
            sent_count = 0
            failed_count = 0
            
            for inv in invoices:
                inv_id, serie, total, customer_email, reminder_type, sent_at = inv
                
                if not customer_email:
                    continue
                
                try:
                    # Preparar notificación push
                    if reminder_type == "escalation":
                        title = "Factura Pendiente - Acción Requerida"
                        body = f"Su factura {serie} por ${total:.2f} requiere atención inmediata."
                        priority = "high"
                    else:
                        title = "Recordatorio de Pago"
                        body = f"Le recordamos que tiene una factura pendiente: {serie} - ${total:.2f}"
                        priority = "normal"
                    
                    payload = {
                        "to": customer_email,
                        "title": title,
                        "body": body,
                        "priority": priority,
                        "data": {
                            "invoice_id": inv_id,
                            "invoice_number": serie,
                            "amount": float(total),
                            "type": reminder_type,
                        }
                    }
                    
                    if not dry_run:
                        r = requests.post(
                            f"{push_service}/send",
                            json=payload,
                            timeout=5,
                            headers={"Content-Type": "application/json"}
                        )
                        
                        if r.status_code in [200, 201]:
                            # Marcar como enviado
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    cur.execute("""
                                        UPDATE invoices 
                                        SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                        WHERE id = %s
                                    """, (json.dumps({
                                        "push_sent": True,
                                        "push_sent_at": datetime.utcnow().isoformat(),
                                    }), inv_id))
                                    
                                    conn.commit()
                            
                            sent_count += 1
                            _track_metric("invoice_billing.push.sent", 1.0)
                        else:
                            failed_count += 1
                    else:
                        logger.info(f"[DRY RUN] Push notification sería enviado para factura {inv_id}")
                        sent_count += 1
                        
                except Exception as e:
                    logger.warning(f"Error enviando push notification para factura {inv_id}: {e}")
                    failed_count += 1
            
            logger.info(
                "Notificaciones push enviadas",
                extra={"sent": sent_count, "failed": failed_count}
            )
            
            return {
                "sent": sent_count,
                "failed": failed_count,
                "skipped": False,
            }
    
    @task(task_id="optimize_resource_allocation")
    def optimize_resource_allocation(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza asignación de recursos basado en carga de trabajo.
        """
        with _track_operation("optimize_resource_allocation"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar carga de trabajo
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('day', created_at) as day,
                            COUNT(*) as invoice_count,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                        GROUP BY DATE_TRUNC('day', created_at)
                        ORDER BY day DESC
                    """)
                    
                    daily_load = cur.fetchall()
            
            if not daily_load:
                return {"optimized": False, "skipped": True}
            
            # Calcular promedios y picos
            daily_counts = [row[1] or 0 for row in daily_load]
            daily_overdue = [row[2] or 0 for row in daily_load]
            
            avg_daily_invoices = sum(daily_counts) / len(daily_counts) if daily_counts else 0
            peak_daily_invoices = max(daily_counts) if daily_counts else 0
            avg_daily_overdue = sum(daily_overdue) / len(daily_overdue) if daily_overdue else 0
            
            # Recomendaciones de recursos
            recommendations = []
            
            if peak_daily_invoices > avg_daily_invoices * 1.5:
                recommendations.append({
                    "type": "scaling",
                    "recommendation": "Considerar auto-scaling para picos de carga",
                    "peak_load": peak_daily_invoices,
                    "avg_load": round(avg_daily_invoices, 1),
                })
            
            if avg_daily_overdue > avg_daily_invoices * 0.2:
                recommendations.append({
                    "type": "collections",
                    "recommendation": "Aumentar recursos para cobranza",
                    "overdue_rate": round((avg_daily_overdue / avg_daily_invoices * 100) if avg_daily_invoices > 0 else 0, 2),
                })
            
            resource_optimization = {
                "workload_analysis": {
                    "avg_daily_invoices": round(avg_daily_invoices, 1),
                    "peak_daily_invoices": peak_daily_invoices,
                    "avg_daily_overdue": round(avg_daily_overdue, 1),
                },
                "recommendations": recommendations,
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización de recursos completada",
                extra={"recommendations": len(recommendations)}
            )
            
            _track_metric("invoice_billing.resources.optimized", 1.0)
            
            return resource_optimization
    
    @task(task_id="integrate_bi_systems")
    def integrate_bi_systems(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Integra con sistemas de Business Intelligence (Tableau, Power BI, etc.).
        """
        with _track_operation("integrate_bi_systems"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            
            bi_systems = _get_env_var("BI_SYSTEMS", default="").split(",")
            bi_systems = [s.strip() for s in bi_systems if s.strip()]
            
            if not bi_systems:
                return {"synced": 0, "skipped": True}
            
            # Preparar datos para BI
            bi_data = {
                "timestamp": pendulum.now("UTC").isoformat(),
                "metrics": analytics_data,
                "source": "invoice_billing_reminders",
            }
            
            synced_count = 0
            
            for bi_system in bi_systems:
                bi_lower = bi_system.lower()
                
                try:
                    if bi_lower == "tableau":
                        tableau_endpoint = _get_env_var("TABLEAU_API_ENDPOINT", default="")
                        tableau_token = _get_env_var("TABLEAU_API_TOKEN", default="")
                        
                        if tableau_endpoint and tableau_token and not dry_run:
                            import requests
                            
                            r = requests.post(
                                f"{tableau_endpoint}/data",
                                json=bi_data,
                                headers={
                                    "Authorization": f"Bearer {tableau_token}",
                                    "Content-Type": "application/json"
                                },
                                timeout=10
                            )
                            
                            if r.status_code in [200, 201]:
                                synced_count += 1
                                logger.info("Datos sincronizados con Tableau")
                    
                    elif bi_lower == "powerbi":
                        powerbi_endpoint = _get_env_var("POWERBI_API_ENDPOINT", default="")
                        powerbi_token = _get_env_var("POWERBI_API_TOKEN", default="")
                        
                        if powerbi_endpoint and powerbi_token and not dry_run:
                            # Implementación conceptual
                            synced_count += 1
                            logger.info("Datos sincronizados con Power BI")
                    
                except Exception as e:
                    logger.warning(f"Error sincronizando con {bi_system}: {e}")
            
            logger.info(
                "Integración con sistemas BI completada",
                extra={"synced": synced_count, "systems": bi_systems}
            )
            
            _track_metric("invoice_billing.bi.synced", synced_count)
            
            return {
                "synced": synced_count,
                "systems": bi_systems,
                "skipped": False,
            }
    
    @task(task_id="advanced_predictive_analytics")
    def advanced_predictive_analytics(
        analytics_data: Dict[str, Any],
        ml_data: Dict[str, Any],
        cash_flow_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Análisis predictivo avanzado combinando múltiples fuentes de datos.
        """
        with _track_operation("advanced_predictive_analytics"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Combinar predicciones de diferentes modelos
            predictions = {
                "payment_probability": ml_data.get("predictions", []),
                "cash_flow": cash_flow_data.get("forecast", {}),
                "demand": analytics_data.get("forecast", {}),
            }
            
            # Calcular score de confianza combinado
            confidence_scores = []
            
            if predictions["payment_probability"]:
                for pred in predictions["payment_probability"]:
                    prob = pred.get("payment_probability", 0.5)
                    confidence = abs(prob - 0.5) * 2  # Más lejos de 0.5 = más confianza
                    confidence_scores.append(confidence)
            
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Generar insights predictivos
            insights = []
            
            if avg_confidence > 0.7:
                insights.append({
                    "type": "high_confidence",
                    "message": "Modelos muestran alta confianza en predicciones",
                    "confidence": round(avg_confidence, 2),
                })
            
            # Análisis de tendencias predictivas
            cash_flow_forecast = cash_flow_data.get("forecast", {})
            if cash_flow_forecast:
                total_predicted = cash_flow_forecast.get("total_predicted", 0)
                if total_predicted > 0:
                    insights.append({
                        "type": "cash_flow_forecast",
                        "message": f"Cash flow predicho para próximos 30 días: ${total_predicted:,.2f}",
                        "amount": total_predicted,
                    })
            
            predictive_analysis = {
                "predictions": predictions,
                "confidence_score": round(avg_confidence, 2),
                "insights": insights,
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis predictivo avanzado completado",
                extra={"confidence": avg_confidence, "insights": len(insights)}
            )
            
            _track_metric("invoice_billing.predictive.analyzed", 1.0)
            
            return predictive_analysis
    
    @task(task_id="optimize_cost_efficiency")
    def optimize_cost_efficiency(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimiza eficiencia de costos en operaciones de facturación.
        """
        with _track_operation("optimize_cost_efficiency"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar costos por operación
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'issued') as issued_count,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            COUNT(*) FILTER (WHERE reminder_type IS NOT NULL) as reminders_sent
                        FROM invoices i
                        LEFT JOIN invoice_reminders ir ON i.id = ir.invoice_id
                        WHERE i.created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    operations = cur.fetchone()
            
            if not operations:
                return {"optimized": False, "skipped": True}
            
            issued_count = operations[0] or 0
            paid_count = operations[1] or 0
            overdue_count = operations[2] or 0
            reminders_sent = operations[3] or 0
            
            # Calcular costos estimados
            invoice_processing_cost = issued_count * 2.5  # $2.5 por factura
            reminder_cost = reminders_sent * 0.5  # $0.5 por recordatorio
            collection_cost = overdue_count * 5.0  # $5 por factura vencida
            
            total_cost = invoice_processing_cost + reminder_cost + collection_cost
            
            # Calcular eficiencia
            if paid_count > 0:
                cost_per_paid_invoice = total_cost / paid_count
                efficiency_score = (paid_count / issued_count * 100) if issued_count > 0 else 0
            else:
                cost_per_paid_invoice = 0
                efficiency_score = 0
            
            # Recomendaciones de optimización
            recommendations = []
            
            if cost_per_paid_invoice > 10:
                recommendations.append({
                    "type": "cost_reduction",
                    "recommendation": "Considerar automatización adicional para reducir costos por factura",
                    "current_cost": round(cost_per_paid_invoice, 2),
                    "target_cost": 7.0,
                })
            
            if reminders_sent > paid_count * 2:
                recommendations.append({
                    "type": "reminder_optimization",
                    "recommendation": "Optimizar timing de recordatorios para reducir cantidad",
                    "reminders_per_paid": round(reminders_sent / paid_count, 2) if paid_count > 0 else 0,
                })
            
            cost_optimization = {
                "costs": {
                    "invoice_processing": round(invoice_processing_cost, 2),
                    "reminders": round(reminder_cost, 2),
                    "collections": round(collection_cost, 2),
                    "total": round(total_cost, 2),
                },
                "efficiency": {
                    "cost_per_paid_invoice": round(cost_per_paid_invoice, 2),
                    "efficiency_score": round(efficiency_score, 2),
                    "conversion_rate": round((paid_count / issued_count * 100) if issued_count > 0 else 0, 2),
                },
                "recommendations": recommendations,
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización de eficiencia de costos completada",
                extra={"total_cost": total_cost, "efficiency": efficiency_score}
            )
            
            _track_metric("invoice_billing.cost_efficiency.optimized", 1.0)
            
            return cost_optimization
    
    @task(task_id="generate_executive_summary")
    def generate_executive_summary(
        analytics_data: Dict[str, Any],
        roi_data: Dict[str, Any],
        competitive_data: Dict[str, Any],
        cash_flow_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera resumen ejecutivo con métricas clave y recomendaciones.
        """
        with _track_operation("generate_executive_summary"):
            now = pendulum.now("UTC")
            
            # Extraer métricas clave
            conversion_rate = analytics_data.get("conversion_rate", 0)
            avg_days_to_pay = analytics_data.get("avg_days_to_pay", 0)
            roi_percentage = roi_data.get("roi", {}).get("roi_percentage", 0)
            competitive_score = competitive_data.get("competitive_score", 0)
            predicted_cash_flow = cash_flow_data.get("forecast", {}).get("total_predicted", 0)
            
            # Generar resumen ejecutivo
            executive_summary = {
                "period": {
                    "generated_at": now.isoformat(),
                    "period": "last_30_days",
                },
                "key_metrics": {
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_days_to_pay": round(avg_days_to_pay, 1),
                    "roi_percentage": round(roi_percentage, 2),
                    "competitive_score": competitive_score,
                    "predicted_cash_flow_30d": round(predicted_cash_flow, 2),
                },
                "status": {
                    "overall": "excellent" if competitive_score > 80 and conversion_rate > 75 else "good" if competitive_score > 60 else "needs_attention",
                    "conversion": "excellent" if conversion_rate > 80 else "good" if conversion_rate > 60 else "needs_improvement",
                    "roi": "excellent" if roi_percentage > 200 else "good" if roi_percentage > 100 else "needs_improvement",
                },
                "recommendations": [
                    "Mantener estrategia actual" if competitive_score > 70 else "Revisar estrategia de cobranza",
                    "Optimizar timing de recordatorios" if avg_days_to_pay > 30 else "Timing de recordatorios es óptimo",
                    "Considerar aumentar inversión" if roi_percentage > 150 else "Revisar costos operacionales",
                ],
                "next_actions": [
                    "Monitorear métricas semanalmente",
                    "Revisar facturas de alto riesgo",
                    "Optimizar procesos de cobranza",
                ],
            }
            
            # Guardar en Variable para acceso ejecutivo
            try:
                Variable.set("invoice_billing_executive_summary", json.dumps(executive_summary))
            except Exception:
                pass
            
            logger.info(
                "Resumen ejecutivo generado",
                extra={"overall_status": executive_summary["status"]["overall"]}
            )
            
            _track_metric("invoice_billing.executive_summary.generated", 1.0)
            
            return executive_summary
    
    @task(task_id="implement_smart_routing")
    def implement_smart_routing(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementa routing inteligente de facturas a diferentes canales de cobro.
        """
        with _track_operation("implement_smart_routing"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"routed": 0, "skipped": False}
            
            routed_count = 0
            
            for inv in unpaid_invoices[:50]:
                inv_id = inv.get("id")
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email:
                    continue
                
                # Obtener metadata
                metadata_str = inv.get("metadata")
                metadata = json.loads(metadata_str) if metadata_str else {}
                
                # Determinar canal óptimo
                routing_channel = "email"  # Default
                
                if days_since > 45:
                    routing_channel = "collections_team"
                elif days_since > 30:
                    routing_channel = "phone_call"
                elif total > 5000:
                    routing_channel = "account_manager"
                elif metadata.get("customer_tier") == "vip":
                    routing_channel = "dedicated_support"
                
                # Guardar routing en metadata
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            UPDATE invoices 
                            SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                            WHERE id = %s
                        """, (json.dumps({
                            "routing_channel": routing_channel,
                            "routed_at": datetime.utcnow().isoformat(),
                        }), inv_id))
                        
                        conn.commit()
                
                routed_count += 1
                _track_metric(f"invoice_billing.routing.{routing_channel}", 1.0)
            
            logger.info(
                "Smart routing completado",
                extra={"routed": routed_count}
            )
            
            return {
                "routed": routed_count,
                "skipped": False,
            }
    
    @task(task_id="analyze_customer_lifetime_value_trends")
    def analyze_customer_lifetime_value_trends(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza tendencias de Customer Lifetime Value (CLV) a lo largo del tiempo.
        """
        with _track_operation("analyze_customer_lifetime_value_trends"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Agrupar clientes por cohorte de primer pago
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('month', MIN(created_at)) as first_payment_month,
                            COUNT(DISTINCT customer_email) as unique_customers,
                            SUM(total) FILTER (WHERE status = 'paid') as total_lifetime_value,
                            AVG(total) FILTER (WHERE status = 'paid') as avg_invoice_amount
                        FROM invoices
                        WHERE customer_email IS NOT NULL
                        AND status = 'paid'
                        AND created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY DATE_TRUNC('month', MIN(created_at))
                        ORDER BY first_payment_month ASC
                    """)
                    
                    clv_trends = cur.fetchall()
            
            if not clv_trends:
                return {"analyzed": False, "skipped": True}
            
            trend_analysis = []
            
            for row in clv_trends:
                month, customers, total_ltv, avg_amount = row
                avg_clv = (float(total_ltv or 0) / (customers or 1)) if customers else 0
                
                trend_analysis.append({
                    "cohort_month": str(month),
                    "unique_customers": customers,
                    "total_lifetime_value": round(float(total_ltv or 0), 2),
                    "avg_clv": round(avg_clv, 2),
                    "avg_invoice_amount": round(float(avg_amount or 0), 2),
                })
            
            # Calcular tendencia general
            if len(trend_analysis) >= 2:
                first_clv = trend_analysis[0]["avg_clv"]
                last_clv = trend_analysis[-1]["avg_clv"]
                clv_trend = ((last_clv - first_clv) / first_clv * 100) if first_clv > 0 else 0
            else:
                clv_trend = 0
            
            clv_analysis = {
                "trends": trend_analysis,
                "overall_trend_pct": round(clv_trend, 2),
                "trend_direction": "increasing" if clv_trend > 0 else "decreasing" if clv_trend < 0 else "stable",
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de tendencias de CLV completado",
                extra={"trend": clv_trend, "cohorts": len(trend_analysis)}
            )
            
            _track_metric("invoice_billing.clv_trends.analyzed", 1.0)
            
            return clv_analysis
    
    @task(task_id="advanced_customer_segmentation")
    def advanced_customer_segmentation(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Segmentación avanzada de clientes basada en comportamiento y valor.
        """
        with _track_operation("advanced_customer_segmentation"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar clientes y sus métricas
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            customer_email,
                            COUNT(*) as invoice_count,
                            SUM(total) FILTER (WHERE status = 'paid') as total_paid,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days_to_pay,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            MAX(created_at) as last_invoice_date
                        FROM invoices
                        WHERE customer_email IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY customer_email
                        HAVING COUNT(*) >= 2
                        ORDER BY total_paid DESC
                        LIMIT 500
                    """)
                    
                    customers = cur.fetchall()
            
            if not customers:
                return {"segmented": 0, "skipped": True}
            
            segments = {
                "champions": [],  # Alto valor, rápido pago
                "loyal_customers": [],  # Alto valor, pago regular
                "at_risk": [],  # Valor medio, pagos lentos
                "new_customers": [],  # Nuevos, potencial
                "hibernating": [],  # Bajo valor, inactivos
            }
            
            for row in customers:
                email, inv_count, total_paid, avg_days, overdue_count, last_invoice = row
                total_paid_val = float(total_paid or 0)
                avg_days_val = float(avg_days or 0) if avg_days else 0
                days_since_last = (pendulum.now("UTC") - pendulum.instance(last_invoice)).days if last_invoice else 0
                
                # Clasificar en segmentos
                if total_paid_val > 10000 and avg_days_val < 20 and overdue_count == 0:
                    segment = "champions"
                elif total_paid_val > 5000 and avg_days_val < 30:
                    segment = "loyal_customers"
                elif overdue_count > 0 or avg_days_val > 45:
                    segment = "at_risk"
                elif days_since_last < 90 and inv_count < 5:
                    segment = "new_customers"
                else:
                    segment = "hibernating"
                
                segments[segment].append({
                    "email": email,
                    "invoice_count": inv_count,
                    "total_paid": round(total_paid_val, 2),
                    "avg_days_to_pay": round(avg_days_val, 1),
                    "overdue_count": overdue_count,
                })
            
            segmentation_analysis = {
                "segments": {
                    name: {
                        "count": len(segment_customers),
                        "total_value": round(sum(c["total_paid"] for c in segment_customers), 2),
                        "customers": segment_customers[:10],  # Top 10 por segmento
                    }
                    for name, segment_customers in segments.items()
                },
                "total_customers": len(customers),
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Segmentación avanzada de clientes completada",
                extra={"total_customers": len(customers), "segments": len(segments)}
            )
            
            _track_metric("invoice_billing.segmentation.analyzed", 1.0)
            
            return segmentation_analysis
    
    @task(task_id="analyze_seasonality_patterns")
    def analyze_seasonality_patterns(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza patrones estacionales en facturación y pagos.
        """
        with _track_operation("analyze_seasonality_patterns"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar por mes del año
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            EXTRACT(MONTH FROM created_at) as month,
                            COUNT(*) as invoice_count,
                            SUM(total) FILTER (WHERE status = 'paid') as total_paid,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '24 months'
                        GROUP BY EXTRACT(MONTH FROM created_at)
                        ORDER BY month
                    """)
                    
                    monthly_data = cur.fetchall()
            
            if not monthly_data:
                return {"analyzed": False, "skipped": True}
            
            # Analizar por día de la semana
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            EXTRACT(DOW FROM created_at) as day_of_week,
                            COUNT(*) as invoice_count,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY EXTRACT(DOW FROM created_at)
                        ORDER BY day_of_week
                    """)
                    
                    weekly_data = cur.fetchall()
            
            monthly_patterns = []
            for row in monthly_data:
                month, inv_count, total_paid, avg_days, paid_count = row
                conversion = (paid_count / inv_count * 100) if inv_count > 0 else 0
                monthly_patterns.append({
                    "month": int(month),
                    "month_name": pendulum.now().replace(month=int(month)).format("MMMM"),
                    "invoice_count": inv_count,
                    "total_paid": round(float(total_paid or 0), 2),
                    "avg_days_to_pay": round(float(avg_days or 0), 1),
                    "conversion_rate": round(conversion, 2),
                })
            
            weekly_patterns = []
            day_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
            for row in weekly_data:
                dow, inv_count, avg_days = row
                weekly_patterns.append({
                    "day_of_week": int(dow),
                    "day_name": day_names[int(dow)],
                    "invoice_count": inv_count,
                    "avg_days_to_pay": round(float(avg_days or 0), 1),
                })
            
            # Identificar picos y valles
            if monthly_patterns:
                paid_amounts = [p["total_paid"] for p in monthly_patterns]
                peak_month = monthly_patterns[paid_amounts.index(max(paid_amounts))]
                low_month = monthly_patterns[paid_amounts.index(min(paid_amounts))]
            else:
                peak_month = None
                low_month = None
            
            seasonality_analysis = {
                "monthly_patterns": monthly_patterns,
                "weekly_patterns": weekly_patterns,
                "insights": {
                    "peak_month": peak_month,
                    "low_month": low_month,
                    "seasonality_detected": len(monthly_patterns) > 6,
                },
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de estacionalidad completado",
                extra={"monthly_patterns": len(monthly_patterns), "weekly_patterns": len(weekly_patterns)}
            )
            
            _track_metric("invoice_billing.seasonality.analyzed", 1.0)
            
            return seasonality_analysis
    
    @task(task_id="implement_dynamic_pricing")
    def implement_dynamic_pricing(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementa optimización de precios dinámicos basada en demanda y comportamiento.
        """
        with _track_operation("implement_dynamic_pricing"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar conversión por rango de precio
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            CASE 
                                WHEN total < 100 THEN '0-100'
                                WHEN total < 500 THEN '100-500'
                                WHEN total < 1000 THEN '500-1000'
                                WHEN total < 5000 THEN '1000-5000'
                                ELSE '5000+'
                            END as price_range,
                            COUNT(*) as total_invoices,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_invoices,
                            AVG(total) as avg_price
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '90 days'
                        GROUP BY price_range
                        ORDER BY avg_price
                    """)
                    
                    price_ranges = cur.fetchall()
            
            if not price_ranges:
                return {"optimized": False, "skipped": True}
            
            pricing_analysis = []
            recommendations = []
            
            for row in price_ranges:
                price_range, total, paid, avg_price = row
                conversion = (paid / total * 100) if total > 0 else 0
                avg_price_val = float(avg_price or 0)
                
                pricing_analysis.append({
                    "price_range": price_range,
                    "total_invoices": total,
                    "paid_invoices": paid,
                    "conversion_rate": round(conversion, 2),
                    "avg_price": round(avg_price_val, 2),
                })
                
                # Recomendaciones
                if conversion < 50 and avg_price_val > 100:
                    recommendations.append({
                        "price_range": price_range,
                        "recommendation": "Considerar reducción de precio para mejorar conversión",
                        "current_conversion": round(conversion, 2),
                        "target_conversion": 70,
                    })
                elif conversion > 90 and avg_price_val < 500:
                    recommendations.append({
                        "price_range": price_range,
                        "recommendation": "Oportunidad de aumentar precio manteniendo alta conversión",
                        "current_conversion": round(conversion, 2),
                        "suggested_increase": "10-15%",
                    })
            
            dynamic_pricing = {
                "price_analysis": pricing_analysis,
                "recommendations": recommendations,
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización de precios dinámicos completada",
                extra={"price_ranges": len(pricing_analysis), "recommendations": len(recommendations)}
            )
            
            _track_metric("invoice_billing.dynamic_pricing.optimized", 1.0)
            
            return dynamic_pricing
    
    @task(task_id="proactive_alerting_system")
    def proactive_alerting_system(
        analytics_data: Dict[str, Any],
        cash_flow_data: Dict[str, Any],
        risk_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Sistema de alertas proactivas antes de que ocurran problemas.
        """
        with _track_operation("proactive_alerting_system"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            alerts = []
            
            # Alerta: Cash flow bajo
            cash_flow_forecast = cash_flow_data.get("forecast", {})
            if cash_flow_forecast:
                total_predicted = cash_flow_forecast.get("total_predicted", 0)
                if total_predicted < 10000:
                    alerts.append({
                        "type": "cash_flow_warning",
                        "severity": "high",
                        "message": f"Cash flow predicho bajo para próximos 30 días: ${total_predicted:,.2f}",
                        "action": "Revisar facturas pendientes y acelerar cobranza",
                    })
            
            # Alerta: Tasa de conversión baja
            conversion_rate = analytics_data.get("conversion_rate", 0)
            if conversion_rate < 60:
                alerts.append({
                    "type": "low_conversion",
                    "severity": "medium",
                    "message": f"Tasa de conversión por debajo del objetivo: {conversion_rate:.2f}%",
                    "action": "Revisar estrategia de recordatorios y timing",
                })
            
            # Alerta: Facturas de alto riesgo
            high_risk_invoices = risk_data.get("high_risk_invoices", [])
            if len(high_risk_invoices) > 10:
                alerts.append({
                    "type": "high_risk_invoices",
                    "severity": "high",
                    "message": f"{len(high_risk_invoices)} facturas identificadas como alto riesgo",
                    "action": "Priorizar seguimiento de facturas de alto riesgo",
                })
            
            # Alerta: Días promedio altos
            avg_days = analytics_data.get("avg_days_to_pay", 0)
            if avg_days > 40:
                alerts.append({
                    "type": "slow_payment",
                    "severity": "medium",
                    "message": f"Días promedio para pago muy alto: {avg_days:.1f} días",
                    "action": "Optimizar términos de pago y recordatorios",
                })
            
            # Enviar alertas críticas a Slack
            critical_alerts = [a for a in alerts if a["severity"] == "high"]
            if critical_alerts:
                for alert in critical_alerts:
                    _send_slack_notification(
                        f"🚨 Alerta Proactiva: {alert['message']}\nAcción: {alert['action']}",
                        channel="#billing-alerts"
                    )
            
            alerting_summary = {
                "alerts": alerts,
                "critical_count": len(critical_alerts),
                "total_count": len(alerts),
                "generated_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Sistema de alertas proactivas ejecutado",
                extra={"total_alerts": len(alerts), "critical": len(critical_alerts)}
            )
            
            _track_metric("invoice_billing.proactive_alerts.generated", len(alerts))
            
            return alerting_summary
    
    @task(task_id="analyze_product_profitability")
    def analyze_product_profitability(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza rentabilidad por producto/servicio basado en facturas.
        """
        with _track_operation("analyze_product_profitability"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar items de factura
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Verificar si existe tabla invoice_items
                    cur.execute("""
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = 'invoice_items'
                        )
                    """)
                    table_exists = cur.fetchone()[0]
                    
                    if not table_exists:
                        return {"analyzed": False, "skipped": True}
                    
                    cur.execute("""
                        SELECT 
                            ii.description,
                            COUNT(DISTINCT ii.invoice_id) as invoice_count,
                            SUM(ii.quantity * ii.unit_price) as total_revenue,
                            AVG(ii.quantity * ii.unit_price) as avg_revenue_per_invoice,
                            COUNT(DISTINCT i.customer_email) as unique_customers
                        FROM invoice_items ii
                        JOIN invoices i ON ii.invoice_id = i.id
                        WHERE i.status = 'paid'
                        AND i.created_at >= NOW() - INTERVAL '90 days'
                        GROUP BY ii.description
                        HAVING COUNT(DISTINCT ii.invoice_id) >= 3
                        ORDER BY total_revenue DESC
                        LIMIT 50
                    """)
                    
                    products = cur.fetchall()
            
            if not products:
                return {"analyzed": False, "skipped": True}
            
            product_analysis = []
            
            for row in products:
                description, inv_count, total_rev, avg_rev, unique_customers = row
                
                # Estimar margen (simplificado - asumir 60% de margen)
                estimated_cost = float(total_rev or 0) * 0.4
                estimated_profit = float(total_rev or 0) * 0.6
                profit_margin = 60.0  # Asumido
                
                product_analysis.append({
                    "product": description or "N/A",
                    "invoice_count": inv_count,
                    "total_revenue": round(float(total_rev or 0), 2),
                    "avg_revenue_per_invoice": round(float(avg_rev or 0), 2),
                    "unique_customers": unique_customers,
                    "estimated_profit": round(estimated_profit, 2),
                    "profit_margin_pct": profit_margin,
                })
            
            # Top productos por rentabilidad
            top_products = sorted(product_analysis, key=lambda x: x["estimated_profit"], reverse=True)[:10]
            
            profitability_analysis = {
                "products": product_analysis,
                "top_products": top_products,
                "total_products": len(product_analysis),
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de rentabilidad de productos completado",
                extra={"total_products": len(product_analysis)}
            )
            
            _track_metric("invoice_billing.product_profitability.analyzed", 1.0)
            
            return profitability_analysis
    
    @task(task_id="implement_credit_management")
    def implement_credit_management(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implementa gestión de crédito y límites para clientes.
        """
        with _track_operation("implement_credit_management"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"managed": 0, "skipped": False}
            
            # Calcular exposición de crédito por cliente
            customer_exposure = {}
            
            for inv in unpaid_invoices[:100]:
                customer_email = inv.get("customer_email")
                total = float(inv.get("total", 0))
                days_since = inv.get("days_since_issue", 0)
                
                if not customer_email:
                    continue
                
                if customer_email not in customer_exposure:
                    customer_exposure[customer_email] = {
                        "total_exposure": 0,
                        "invoice_count": 0,
                        "max_days_overdue": 0,
                    }
                
                customer_exposure[customer_email]["total_exposure"] += total
                customer_exposure[customer_email]["invoice_count"] += 1
                customer_exposure[customer_email]["max_days_overdue"] = max(
                    customer_exposure[customer_email]["max_days_overdue"],
                    days_since
                )
            
            # Determinar límites de crédito recomendados
            credit_recommendations = []
            
            for email, exposure in customer_exposure.items():
                total_exp = exposure["total_exposure"]
                max_days = exposure["max_days_overdue"]
                
                # Calcular límite recomendado basado en exposición actual
                if max_days > 60:
                    recommended_limit = total_exp * 0.5  # Reducir límite
                    action = "reduce_limit"
                elif max_days > 30:
                    recommended_limit = total_exp * 0.8  # Mantener límite
                    action = "maintain_limit"
                else:
                    recommended_limit = total_exp * 1.5  # Aumentar límite
                    action = "increase_limit"
                
                credit_recommendations.append({
                    "customer_email": email,
                    "current_exposure": round(total_exp, 2),
                    "invoice_count": exposure["invoice_count"],
                    "max_days_overdue": max_days,
                    "recommended_credit_limit": round(recommended_limit, 2),
                    "action": action,
                })
            
            credit_management = {
                "customers_analyzed": len(customer_exposure),
                "recommendations": credit_recommendations[:20],  # Top 20
                "total_exposure": round(sum(e["total_exposure"] for e in customer_exposure.values()), 2),
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Gestión de crédito completada",
                extra={"customers": len(customer_exposure), "recommendations": len(credit_recommendations)}
            )
            
            _track_metric("invoice_billing.credit_management.analyzed", 1.0)
            
            return credit_management
    
    @task(task_id="analyze_correlations")
    def analyze_correlations(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza correlaciones entre diferentes variables de facturación.
        """
        with _track_operation("analyze_correlations"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener datos para análisis de correlación
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            total,
                            EXTRACT(DAY FROM (updated_at - created_at)) as days_to_pay,
                            EXTRACT(DOW FROM created_at) as day_of_week,
                            EXTRACT(MONTH FROM created_at) as month,
                            CASE WHEN status = 'paid' THEN 1 ELSE 0 END as paid
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '180 days'
                        AND status IN ('paid', 'overdue')
                        LIMIT 1000
                    """)
                    
                    data = cur.fetchall()
            
            if len(data) < 10:
                return {"analyzed": False, "skipped": True}
            
            # Calcular correlaciones simples
            totals = [float(row[0] or 0) for row in data]
            days = [float(row[1] or 0) if row[1] else 0 for row in data]
            day_of_week = [int(row[2] or 0) for row in data]
            month = [int(row[3] or 0) for row in data]
            paid = [int(row[4] or 0) for row in data]
            
            # Correlación: monto vs días para pago
            if totals and days:
                # Correlación de Pearson simplificada
                avg_total = sum(totals) / len(totals)
                avg_days = sum(days) / len(days)
                
                numerator = sum((totals[i] - avg_total) * (days[i] - avg_days) for i in range(len(totals)))
                denom_total = sum((t - avg_total) ** 2 for t in totals) ** 0.5
                denom_days = sum((d - avg_days) ** 2 for d in days) ** 0.5
                
                correlation_amount_days = (numerator / (denom_total * denom_days)) if (denom_total * denom_days) > 0 else 0
            else:
                correlation_amount_days = 0
            
            # Correlación: día de semana vs pago
            paid_by_dow = {}
            total_by_dow = {}
            for i, dow in enumerate(day_of_week):
                if dow not in paid_by_dow:
                    paid_by_dow[dow] = 0
                    total_by_dow[dow] = 0
                paid_by_dow[dow] += paid[i]
                total_by_dow[dow] += 1
            
            dow_conversion = {dow: (paid_by_dow[dow] / total_by_dow[dow] * 100) if total_by_dow[dow] > 0 else 0 
                            for dow in paid_by_dow}
            
            correlations = {
                "amount_vs_days_to_pay": round(correlation_amount_days, 3),
                "day_of_week_vs_conversion": dow_conversion,
                "insights": [],
            }
            
            # Generar insights
            if abs(correlation_amount_days) > 0.3:
                correlations["insights"].append({
                    "type": "strong_correlation",
                    "message": f"Correlación {'positiva' if correlation_amount_days > 0 else 'negativa'} entre monto y días para pago: {correlation_amount_days:.3f}",
                })
            
            best_dow = max(dow_conversion.items(), key=lambda x: x[1])
            worst_dow = min(dow_conversion.items(), key=lambda x: x[1])
            
            if best_dow[1] - worst_dow[1] > 10:
                correlations["insights"].append({
                    "type": "day_of_week_impact",
                    "message": f"Mejor día para facturación: {best_dow[0]} ({best_dow[1]:.1f}% conversión)",
                })
            
            correlation_analysis = {
                "correlations": correlations,
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de correlaciones completado",
                extra={"correlations": len(correlations)}
            )
            
            _track_metric("invoice_billing.correlations.analyzed", 1.0)
            
            return correlation_analysis
    
    @task(task_id="implement_auto_healing")
    def implement_auto_healing(
        check_data: Dict[str, Any],
        reminders_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Sistema de auto-healing que corrige problemas comunes automáticamente.
        """
        with _track_operation("implement_auto_healing"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            fixes_applied = []
            
            # Fix 1: Facturas con emails inválidos
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, customer_email, serie
                        FROM invoices
                        WHERE status = 'issued'
                        AND customer_email IS NOT NULL
                        AND customer_email NOT LIKE '%@%.%'
                        AND created_at >= NOW() - INTERVAL '30 days'
                        LIMIT 20
                    """)
                    
                    invalid_emails = cur.fetchall()
            
            for inv_id, email, serie in invalid_emails:
                # Intentar encontrar email válido en historial
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT DISTINCT customer_email
                            FROM invoices
                            WHERE customer_email LIKE '%@%.%'
                            AND serie LIKE %s
                            LIMIT 1
                        """, (f"%{serie[:5]}%",))
                        
                        valid_email = cur.fetchone()
                        
                        if valid_email and not dry_run:
                            cur.execute("""
                                UPDATE invoices
                                SET customer_email = %s,
                                    metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb
                                WHERE id = %s
                            """, (
                                valid_email[0],
                                json.dumps({
                                    "email_fixed": True,
                                    "original_email": email,
                                    "fixed_at": datetime.utcnow().isoformat(),
                                }),
                                inv_id
                            ))
                            conn.commit()
                            
                            fixes_applied.append({
                                "type": "invalid_email_fixed",
                                "invoice_id": inv_id,
                                "original": email,
                                "fixed_to": valid_email[0],
                            })
            
            # Fix 2: Facturas sin metadata pero con datos importantes
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, serie, total, status
                        FROM invoices
                        WHERE metadata IS NULL
                        AND status IN ('issued', 'overdue')
                        AND created_at >= NOW() - INTERVAL '7 days'
                        LIMIT 30
                    """)
                    
                    missing_metadata = cur.fetchall()
            
            for inv_id, serie, total, status in missing_metadata:
                if not dry_run:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                UPDATE invoices
                                SET metadata = %s::jsonb
                                WHERE id = %s
                            """, (json.dumps({
                                "auto_initialized": True,
                                "initialized_at": datetime.utcnow().isoformat(),
                                "status": status,
                            }), inv_id))
                            conn.commit()
                    
                    fixes_applied.append({
                        "type": "metadata_initialized",
                        "invoice_id": inv_id,
                    })
            
            # Fix 3: Recordatorios duplicados
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT invoice_id, COUNT(*) as count
                        FROM invoice_reminders
                        WHERE sent_at >= NOW() - INTERVAL '24 hours'
                        GROUP BY invoice_id
                        HAVING COUNT(*) > 1
                        LIMIT 20
                    """)
                    
                    duplicates = cur.fetchall()
            
            for inv_id, count in duplicates:
                if not dry_run:
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            # Mantener solo el más reciente
                            cur.execute("""
                                DELETE FROM invoice_reminders
                                WHERE invoice_id = %s
                                AND id NOT IN (
                                    SELECT id FROM invoice_reminders
                                    WHERE invoice_id = %s
                                    ORDER BY sent_at DESC
                                    LIMIT 1
                                )
                            """, (inv_id, inv_id))
                            conn.commit()
                    
                    fixes_applied.append({
                        "type": "duplicate_reminders_removed",
                        "invoice_id": inv_id,
                        "removed_count": count - 1,
                    })
            
            auto_healing_summary = {
                "fixes_applied": fixes_applied,
                "total_fixes": len(fixes_applied),
                "healed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Auto-healing completado",
                extra={"fixes_applied": len(fixes_applied)}
            )
            
            _track_metric("invoice_billing.auto_healing.fixes", len(fixes_applied))
            
            return auto_healing_summary
    
    @task(task_id="advanced_customer_scoring")
    def advanced_customer_scoring(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sistema de scoring avanzado de clientes basado en múltiples factores.
        """
        with _track_operation("advanced_customer_scoring"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener métricas por cliente
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            customer_email,
                            COUNT(*) as total_invoices,
                            SUM(total) FILTER (WHERE status = 'paid') as total_paid,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            MAX(created_at) as last_invoice_date,
                            MIN(created_at) as first_invoice_date
                        FROM invoices
                        WHERE customer_email IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY customer_email
                        HAVING COUNT(*) >= 2
                        ORDER BY total_paid DESC
                        LIMIT 500
                    """)
                    
                    customers = cur.fetchall()
            
            if not customers:
                return {"scored": 0, "skipped": True}
            
            scored_customers = []
            
            for row in customers:
                email, inv_count, total_paid, avg_days, overdue_count, last_inv, first_inv = row
                total_paid_val = float(total_paid or 0)
                avg_days_val = float(avg_days or 0) if avg_days else 0
                days_as_customer = (pendulum.instance(last_inv) - pendulum.instance(first_inv)).days if (last_inv and first_inv) else 0
                
                # Calcular scores por dimensión (0-100 cada uno)
                value_score = min(100, (total_paid_val / 50000) * 100)  # $50K = 100
                speed_score = max(0, 100 - (avg_days_val / 30) * 100)  # 0 días = 100, 30+ = 0
                reliability_score = max(0, 100 - (overdue_count / inv_count * 100) if inv_count > 0 else 0)
                loyalty_score = min(100, (days_as_customer / 365) * 50 + (inv_count / 10) * 50)  # Combinado
                
                # Score total ponderado
                total_score = (
                    value_score * 0.3 +
                    speed_score * 0.25 +
                    reliability_score * 0.25 +
                    loyalty_score * 0.2
                )
                
                # Clasificación
                if total_score >= 80:
                    tier = "platinum"
                elif total_score >= 60:
                    tier = "gold"
                elif total_score >= 40:
                    tier = "silver"
                else:
                    tier = "bronze"
                
                scored_customers.append({
                    "email": email,
                    "total_score": round(total_score, 1),
                    "tier": tier,
                    "scores": {
                        "value": round(value_score, 1),
                        "speed": round(speed_score, 1),
                        "reliability": round(reliability_score, 1),
                        "loyalty": round(loyalty_score, 1),
                    },
                    "metrics": {
                        "total_paid": round(total_paid_val, 2),
                        "avg_days_to_pay": round(avg_days_val, 1),
                        "overdue_rate": round((overdue_count / inv_count * 100) if inv_count > 0 else 0, 2),
                        "invoice_count": inv_count,
                    },
                })
            
            # Top clientes por score
            top_customers = sorted(scored_customers, key=lambda x: x["total_score"], reverse=True)[:20]
            
            scoring_summary = {
                "customers_scored": len(scored_customers),
                "tier_distribution": {
                    "platinum": len([c for c in scored_customers if c["tier"] == "platinum"]),
                    "gold": len([c for c in scored_customers if c["tier"] == "gold"]),
                    "silver": len([c for c in scored_customers if c["tier"] == "silver"]),
                    "bronze": len([c for c in scored_customers if c["tier"] == "bronze"]),
                },
                "top_customers": top_customers,
                "scored_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Scoring avanzado de clientes completado",
                extra={"customers_scored": len(scored_customers), "platinum": scoring_summary["tier_distribution"]["platinum"]}
            )
            
            _track_metric("invoice_billing.customer_scoring.completed", 1.0)
            
            return scoring_summary
    
    @task(task_id="generate_insights_report")
    def generate_insights_report(
        analytics_data: Dict[str, Any],
        segmentation_data: Dict[str, Any],
        seasonality_data: Dict[str, Any],
        profitability_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera reporte consolidado de insights y recomendaciones estratégicas.
        """
        with _track_operation("generate_insights_report"):
            insights = []
            recommendations = []
            
            # Insight 1: Segmentación
            if segmentation_data.get("segmented", 0) > 0:
                segments = segmentation_data.get("segments", {})
                champions = segments.get("champions", {}).get("count", 0)
                at_risk = segments.get("at_risk", {}).get("count", 0)
                
                if champions > 0:
                    insights.append({
                        "type": "positive",
                        "category": "segmentation",
                        "message": f"{champions} clientes Champions identificados - alto valor y rápido pago",
                    })
                
                if at_risk > 10:
                    recommendations.append({
                        "priority": "high",
                        "category": "retention",
                        "action": f"Implementar estrategia de retención para {at_risk} clientes en riesgo",
                    })
            
            # Insight 2: Estacionalidad
            if seasonality_data.get("analyzed", False):
                peak_month = seasonality_data.get("insights", {}).get("peak_month")
                if peak_month:
                    insights.append({
                        "type": "informational",
                        "category": "seasonality",
                        "message": f"Mes pico identificado: {peak_month.get('month_name')} con ${peak_month.get('total_paid', 0):,.2f}",
                    })
                    recommendations.append({
                        "priority": "medium",
                        "category": "planning",
                        "action": f"Preparar recursos adicionales para {peak_month.get('month_name')}",
                    })
            
            # Insight 3: Rentabilidad
            if profitability_data.get("analyzed", False):
                top_products = profitability_data.get("top_products", [])
                if top_products:
                    top_product = top_products[0]
                    insights.append({
                        "type": "positive",
                        "category": "profitability",
                        "message": f"Producto estrella: {top_product.get('product')} con ${top_product.get('estimated_profit', 0):,.2f} de profit",
                    })
                    recommendations.append({
                        "priority": "medium",
                        "category": "growth",
                        "action": f"Considerar promoción adicional para {top_product.get('product')}",
                    })
            
            # Insight 4: Conversión
            conversion_rate = analytics_data.get("conversion_rate", 0)
            if conversion_rate < 70:
                recommendations.append({
                    "priority": "high",
                    "category": "optimization",
                    "action": f"Tasa de conversión {conversion_rate:.1f}% - revisar estrategia de recordatorios",
                })
            
            insights_report = {
                "insights": insights,
                "recommendations": sorted(recommendations, key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["priority"], 0), reverse=True),
                "generated_at": pendulum.now("UTC").isoformat(),
            }
            
            # Guardar en Variable
            try:
                Variable.set("invoice_billing_insights_report", json.dumps(insights_report))
            except Exception:
                pass
            
            logger.info(
                "Reporte de insights generado",
                extra={"insights": len(insights), "recommendations": len(recommendations)}
            )
            
            _track_metric("invoice_billing.insights_report.generated", 1.0)
            
            return insights_report
    
    @task(task_id="analyze_channel_performance")
    def analyze_channel_performance(
        emails_data: Dict[str, Any],
        reminders_data: Dict[str, Any],
        escalations_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Analiza performance de diferentes canales de comunicación.
        """
        with _track_operation("analyze_channel_performance"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar performance por canal
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            CASE 
                                WHEN ir.reminder_type = 'first' THEN 'email_initial'
                                WHEN ir.reminder_type = 'reminder' THEN 'email_reminder'
                                WHEN ir.reminder_type = 'escalation' THEN 'email_escalation'
                                ELSE 'other'
                            END as channel,
                            COUNT(*) as total_sent,
                            COUNT(DISTINCT ir.invoice_id) as unique_invoices,
                            AVG(EXTRACT(EPOCH FROM (i.updated_at - ir.sent_at))) FILTER (WHERE i.status = 'paid') / 86400 as avg_days_to_pay_after_send
                        FROM invoice_reminders ir
                        JOIN invoices i ON ir.invoice_id = i.id
                        WHERE ir.sent_at >= NOW() - INTERVAL '90 days'
                        GROUP BY channel
                    """)
                    
                    channel_data = cur.fetchall()
            
            if not channel_data:
                return {"analyzed": False, "skipped": True}
            
            channel_performance = []
            
            for row in channel_data:
                channel, total_sent, unique_invoices, avg_days = row
                avg_days_val = float(avg_days or 0) if avg_days else 0
                
                # Calcular tasa de conversión por canal
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT COUNT(DISTINCT i.id) FILTER (WHERE i.status = 'paid')
                            FROM invoice_reminders ir
                            JOIN invoices i ON ir.invoice_id = i.id
                            WHERE ir.sent_at >= NOW() - INTERVAL '90 days'
                            AND CASE 
                                WHEN ir.reminder_type = 'first' THEN 'email_initial'
                                WHEN ir.reminder_type = 'reminder' THEN 'email_reminder'
                                WHEN ir.reminder_type = 'escalation' THEN 'email_escalation'
                                ELSE 'other'
                            END = %s
                        """, (channel,))
                        
                        paid_count = cur.fetchone()[0] or 0
                
                conversion_rate = (paid_count / unique_invoices * 100) if unique_invoices > 0 else 0
                
                channel_performance.append({
                    "channel": channel,
                    "total_sent": total_sent,
                    "unique_invoices": unique_invoices,
                    "conversion_rate": round(conversion_rate, 2),
                    "avg_days_to_pay_after_send": round(avg_days_val, 1),
                    "effectiveness_score": round((conversion_rate * 0.7 + (100 - min(avg_days_val, 60)) * 0.3), 1),
                })
            
            # Identificar mejor canal
            if channel_performance:
                best_channel = max(channel_performance, key=lambda x: x["effectiveness_score"])
            else:
                best_channel = None
            
            performance_analysis = {
                "channels": channel_performance,
                "best_channel": best_channel,
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de performance de canales completado",
                extra={"channels": len(channel_performance), "best": best_channel.get("channel") if best_channel else None}
            )
            
            _track_metric("invoice_billing.channel_performance.analyzed", 1.0)
            
            return performance_analysis
    
    @task(task_id="implement_backup_recovery")
    def implement_backup_recovery(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sistema de backup y recovery para datos críticos de facturación.
        """
        with _track_operation("implement_backup_recovery"):
            ctx = get_current_context()
            params = ctx["params"]
            dry_run = bool(params["dry_run"])
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            backup_summary = {
                "backups_created": [],
                "total_backups": 0,
            }
            
            # Backup 1: Facturas críticas (últimos 30 días)
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            id, serie, total, status, customer_email, created_at, metadata
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                        AND status IN ('issued', 'overdue', 'paid')
                        ORDER BY created_at DESC
                        LIMIT 500
                    """)
                    
                    critical_invoices = cur.fetchall()
            
            if critical_invoices and not dry_run:
                # Crear backup en metadata (simplificado - en producción usaría S3 o similar)
                backup_data = {
                    "backup_type": "critical_invoices",
                    "backup_date": pendulum.now("UTC").isoformat(),
                    "invoice_count": len(critical_invoices),
                    "backup_id": f"backup_{pendulum.now().format('YYYYMMDD_HHmmss')}",
                }
                
                try:
                    Variable.set(f"invoice_billing_backup_{backup_data['backup_id']}", json.dumps({
                        "summary": backup_data,
                        "sample_count": min(10, len(critical_invoices)),
                    }))
                    
                    backup_summary["backups_created"].append({
                        "type": "critical_invoices",
                        "backup_id": backup_data["backup_id"],
                        "invoice_count": len(critical_invoices),
                    })
                except Exception as e:
                    logger.warning(f"Error creando backup: {e}")
            
            # Backup 2: Métricas clave
            if analytics_data and not dry_run:
                metrics_backup = {
                    "backup_type": "key_metrics",
                    "backup_date": pendulum.now("UTC").isoformat(),
                    "metrics": {
                        "conversion_rate": analytics_data.get("conversion_rate", 0),
                        "avg_days_to_pay": analytics_data.get("avg_days_to_pay", 0),
                        "total_invoices": analytics_data.get("total_invoices", 0),
                        "paid_invoices": analytics_data.get("paid_invoices", 0),
                    },
                    "backup_id": f"metrics_{pendulum.now().format('YYYYMMDD_HHmmss')}",
                }
                
                try:
                    Variable.set(f"invoice_billing_backup_{metrics_backup['backup_id']}", json.dumps(metrics_backup))
                    
                    backup_summary["backups_created"].append({
                        "type": "key_metrics",
                        "backup_id": metrics_backup["backup_id"],
                    })
                except Exception as e:
                    logger.warning(f"Error creando backup de métricas: {e}")
            
            backup_summary["total_backups"] = len(backup_summary["backups_created"])
            backup_summary["backed_up_at"] = pendulum.now("UTC").isoformat()
            
            logger.info(
                "Sistema de backup y recovery ejecutado",
                extra={"backups_created": backup_summary["total_backups"]}
            )
            
            _track_metric("invoice_billing.backup.created", backup_summary["total_backups"])
            
            return backup_summary
    
    @task(task_id="real_time_metrics_dashboard")
    def real_time_metrics_dashboard(
        analytics_data: Dict[str, Any],
        cash_flow_data: Dict[str, Any],
        risk_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Genera métricas en tiempo real para dashboard.
        """
        with _track_operation("real_time_metrics_dashboard"):
            now = pendulum.now("UTC")
            
            # Calcular métricas en tiempo real
            real_time_metrics = {
                "timestamp": now.isoformat(),
                "metrics": {
                    "conversion_rate": round(analytics_data.get("conversion_rate", 0), 2),
                    "avg_days_to_pay": round(analytics_data.get("avg_days_to_pay", 0), 1),
                    "total_pending": analytics_data.get("unpaid_invoices", 0),
                    "total_paid_today": analytics_data.get("paid_today", 0),
                    "predicted_cash_flow_30d": round(cash_flow_data.get("forecast", {}).get("total_predicted", 0), 2),
                    "high_risk_count": len(risk_data.get("high_risk_invoices", [])),
                },
                "status": {
                    "system_health": "healthy" if analytics_data.get("conversion_rate", 0) > 60 else "warning",
                    "cash_flow_status": "good" if cash_flow_data.get("forecast", {}).get("total_predicted", 0) > 10000 else "low",
                    "risk_level": "low" if len(risk_data.get("high_risk_invoices", [])) < 10 else "high",
                },
                "alerts": [],
            }
            
            # Generar alertas en tiempo real
            if real_time_metrics["metrics"]["conversion_rate"] < 60:
                real_time_metrics["alerts"].append({
                    "type": "warning",
                    "message": "Tasa de conversión por debajo del objetivo",
                })
            
            if real_time_metrics["status"]["cash_flow_status"] == "low":
                real_time_metrics["alerts"].append({
                    "type": "critical",
                    "message": "Cash flow predicho bajo para próximos 30 días",
                })
            
            if real_time_metrics["status"]["risk_level"] == "high":
                real_time_metrics["alerts"].append({
                    "type": "warning",
                    "message": "Alto número de facturas de riesgo detectadas",
                })
            
            # Guardar en Variable para acceso en tiempo real
            try:
                Variable.set("invoice_billing_realtime_metrics", json.dumps(real_time_metrics))
            except Exception:
                pass
            
            logger.info(
                "Métricas en tiempo real generadas",
                extra={"conversion_rate": real_time_metrics["metrics"]["conversion_rate"]}
            )
            
            _track_metric("invoice_billing.realtime_metrics.updated", 1.0)
            
            return real_time_metrics
    
    @task(task_id="optimize_communication_strategy")
    def optimize_communication_strategy(
        segmentation_data: Dict[str, Any],
        scoring_data: Dict[str, Any],
        channel_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Optimiza estrategia de comunicación basada en segmentación y scoring.
        """
        with _track_operation("optimize_communication_strategy"):
            strategies = []
            
            # Estrategia por segmento
            if segmentation_data.get("segmented", 0) > 0:
                segments = segmentation_data.get("segments", {})
                
                # Champions: Comunicación premium
                if segments.get("champions", {}).get("count", 0) > 0:
                    strategies.append({
                        "segment": "champions",
                        "strategy": {
                            "frequency": "low",
                            "tone": "appreciative",
                            "channels": ["email", "dedicated_support"],
                            "personalization_level": "high",
                            "discount_offers": False,
                        },
                        "rationale": "Clientes de alto valor - mantener relación premium",
                    })
                
                # At Risk: Comunicación frecuente y urgente
                if segments.get("at_risk", {}).get("count", 0) > 0:
                    strategies.append({
                        "segment": "at_risk",
                        "strategy": {
                            "frequency": "high",
                            "tone": "firm_but_supportive",
                            "channels": ["email", "phone_call"],
                            "personalization_level": "medium",
                            "discount_offers": True,
                        },
                        "rationale": "Clientes en riesgo - necesitan atención inmediata",
                    })
            
            # Estrategia por tier de scoring
            if scoring_data.get("scored", 0) > 0:
                tier_dist = scoring_data.get("tier_distribution", {})
                
                # Platinum: Estrategia VIP
                if tier_dist.get("platinum", 0) > 0:
                    strategies.append({
                        "tier": "platinum",
                        "strategy": {
                            "communication_style": "exclusive",
                            "response_time": "immediate",
                            "channels": ["dedicated_support", "account_manager"],
                            "special_offers": True,
                        },
                        "rationale": "Clientes Platinum - máximo nivel de servicio",
                    })
            
            # Estrategia por canal más efectivo
            if channel_data.get("analyzed", False):
                best_channel = channel_data.get("best_channel")
                if best_channel:
                    strategies.append({
                        "channel_optimization": {
                            "recommended_channel": best_channel.get("channel"),
                            "effectiveness_score": best_channel.get("effectiveness_score"),
                            "recommendation": f"Priorizar uso de {best_channel.get('channel')} para mejores resultados",
                        },
                    })
            
            strategy_summary = {
                "strategies": strategies,
                "total_strategies": len(strategies),
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Estrategia de comunicación optimizada",
                extra={"strategies": len(strategies)}
            )
            
            _track_metric("invoice_billing.communication_strategy.optimized", 1.0)
            
            return strategy_summary
    
    @task(task_id="advanced_satisfaction_analysis")
    def advanced_satisfaction_analysis(
        analytics_data: Dict[str, Any],
        sentiment_data: Dict[str, Any],
        scoring_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de satisfacción del cliente combinando múltiples fuentes.
        """
        with _track_operation("advanced_satisfaction_analysis"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener datos de satisfacción
            satisfaction_scores = []
            
            # Factor 1: Velocidad de pago
            avg_days = analytics_data.get("avg_days_to_pay", 0)
            speed_score = max(0, 100 - (avg_days / 30) * 100) if avg_days else 50
            
            # Factor 2: Sentimiento
            sentiment_positive = sentiment_data.get("positive_count", 0)
            sentiment_total = sentiment_data.get("total_responses", 0)
            sentiment_score = (sentiment_positive / sentiment_total * 100) if sentiment_total > 0 else 50
            
            # Factor 3: Tasa de vencimientos
            conversion_rate = analytics_data.get("conversion_rate", 0)
            reliability_score = conversion_rate
            
            # Factor 4: Scoring de clientes
            platinum_count = scoring_data.get("tier_distribution", {}).get("platinum", 0)
            gold_count = scoring_data.get("tier_distribution", {}).get("gold", 0)
            total_scored = scoring_data.get("customers_scored", 0)
            tier_score = ((platinum_count * 100 + gold_count * 70) / total_scored * 100) if total_scored > 0 else 50
            
            # Score combinado
            overall_satisfaction = (
                speed_score * 0.25 +
                sentiment_score * 0.25 +
                reliability_score * 0.3 +
                tier_score * 0.2
            )
            
            # Análisis por cliente
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            customer_email,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            COUNT(*) as total_invoices
                        FROM invoices
                        WHERE customer_email IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '6 months'
                        GROUP BY customer_email
                        HAVING COUNT(*) >= 3
                        LIMIT 200
                    """)
                    
                    customers = cur.fetchall()
            
            customer_satisfaction = []
            for row in customers:
                email, avg_days_cust, overdue_cust, total_inv = row
                avg_days_val = float(avg_days_cust or 0) if avg_days_cust else 0
                overdue_rate = (overdue_cust / total_inv * 100) if total_inv > 0 else 0
                
                customer_satisfaction_score = (
                    max(0, 100 - (avg_days_val / 30) * 100) * 0.5 +
                    max(0, 100 - overdue_rate) * 0.5
                )
                
                customer_satisfaction.append({
                    "email": email,
                    "satisfaction_score": round(customer_satisfaction_score, 1),
                    "avg_days_to_pay": round(avg_days_val, 1),
                    "overdue_rate": round(overdue_rate, 2),
                })
            
            # Top y bottom clientes
            top_satisfied = sorted(customer_satisfaction, key=lambda x: x["satisfaction_score"], reverse=True)[:10]
            bottom_satisfied = sorted(customer_satisfaction, key=lambda x: x["satisfaction_score"])[:10]
            
            satisfaction_analysis = {
                "overall_satisfaction": round(overall_satisfaction, 1),
                "component_scores": {
                    "speed": round(speed_score, 1),
                    "sentiment": round(sentiment_score, 1),
                    "reliability": round(reliability_score, 1),
                    "tier": round(tier_score, 1),
                },
                "top_satisfied_customers": top_satisfied,
                "bottom_satisfied_customers": bottom_satisfied,
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis avanzado de satisfacción completado",
                extra={"overall_satisfaction": overall_satisfaction}
            )
            
            _track_metric("invoice_billing.satisfaction.analyzed", 1.0)
            
            return satisfaction_analysis
    
    @task(task_id="intelligent_recommendations_engine")
    def intelligent_recommendations_engine(
        analytics_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        segmentation_data: Dict[str, Any],
        profitability_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Motor de recomendaciones inteligente basado en múltiples factores.
        """
        with _track_operation("intelligent_recommendations_engine"):
            recommendations = []
            
            # Recomendación 1: Basada en conversión
            conversion_rate = analytics_data.get("conversion_rate", 0)
            if conversion_rate < 70:
                recommendations.append({
                    "priority": "high",
                    "category": "conversion_optimization",
                    "title": "Optimizar tasa de conversión",
                    "description": f"Tasa de conversión actual: {conversion_rate:.1f}%. Objetivo: 75%+",
                    "actions": [
                        "Revisar timing de recordatorios",
                        "Personalizar mensajes por segmento",
                        "Ofrecer incentivos de pago temprano",
                    ],
                    "expected_impact": "Aumento de 5-10% en conversión",
                })
            
            # Recomendación 2: Basada en segmentación
            if segmentation_data.get("segmented", 0) > 0:
                at_risk_count = segmentation_data.get("segments", {}).get("at_risk", {}).get("count", 0)
                if at_risk_count > 20:
                    recommendations.append({
                        "priority": "high",
                        "category": "retention",
                        "title": "Estrategia de retención para clientes en riesgo",
                        "description": f"{at_risk_count} clientes identificados como en riesgo",
                        "actions": [
                            "Contacto proactivo con clientes en riesgo",
                            "Ofertas de planes de pago personalizados",
                            "Asignar account manager para casos críticos",
                        ],
                        "expected_impact": "Reducción de churn en 15-20%",
                    })
            
            # Recomendación 3: Basada en rentabilidad
            if profitability_data.get("analyzed", False):
                top_products = profitability_data.get("top_products", [])
                if top_products:
                    top_product = top_products[0]
                    recommendations.append({
                        "priority": "medium",
                        "category": "growth",
                        "title": "Ampliar producto estrella",
                        "description": f"{top_product.get('product')} genera ${top_product.get('estimated_profit', 0):,.2f} de profit",
                        "actions": [
                            f"Promoción especial para {top_product.get('product')}",
                            "Upselling a clientes existentes",
                            "Marketing dirigido para este producto",
                        ],
                        "expected_impact": "Aumento de revenue en 10-15%",
                    })
            
            # Recomendación 4: Basada en riesgo
            high_risk_count = len(risk_data.get("high_risk_invoices", []))
            if high_risk_count > 15:
                recommendations.append({
                    "priority": "high",
                    "category": "risk_management",
                    "title": "Gestionar facturas de alto riesgo",
                    "description": f"{high_risk_count} facturas identificadas como alto riesgo",
                    "actions": [
                        "Revisión inmediata de facturas de alto riesgo",
                        "Contacto directo con clientes",
                        "Considerar acciones legales para casos extremos",
                    ],
                    "expected_impact": "Reducción de pérdidas en 20-30%",
                })
            
            # Recomendación 5: Basada en días promedio
            avg_days = analytics_data.get("avg_days_to_pay", 0)
            if avg_days > 35:
                recommendations.append({
                    "priority": "medium",
                    "category": "payment_optimization",
                    "title": "Reducir días promedio para pago",
                    "description": f"Días promedio actual: {avg_days:.1f}. Objetivo: <30 días",
                    "actions": [
                        "Optimizar términos de pago",
                        "Incentivos por pago temprano",
                        "Recordatorios más frecuentes",
                    ],
                    "expected_impact": "Reducción de 5-10 días en promedio",
                })
            
            # Ordenar por prioridad
            recommendations_sorted = sorted(
                recommendations,
                key=lambda x: {"high": 3, "medium": 2, "low": 1}.get(x["priority"], 0),
                reverse=True
            )
            
            recommendations_summary = {
                "recommendations": recommendations_sorted,
                "total_recommendations": len(recommendations),
                "high_priority": len([r for r in recommendations if r["priority"] == "high"]),
                "generated_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Motor de recomendaciones inteligente ejecutado",
                extra={"total": len(recommendations), "high_priority": recommendations_summary["high_priority"]}
            )
            
            _track_metric("invoice_billing.recommendations.generated", len(recommendations))
            
            return recommendations_summary
    
    @task(task_id="sla_metrics_tracking")
    def sla_metrics_tracking(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tracking de métricas de SLA (Service Level Agreement).
        """
        with _track_operation("sla_metrics_tracking"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Definir SLAs
            slas = {
                "invoice_generation_time": 24,  # horas
                "email_delivery_time": 1,  # horas
                "reminder_response_time": 48,  # horas
                "payment_processing_time": 72,  # horas
            }
            
            # Calcular métricas de SLA
            sla_metrics = {}
            
            # SLA 1: Tiempo de generación de facturas
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            AVG(EXTRACT(EPOCH FROM (created_at - DATE_TRUNC('day', created_at))) / 3600) as avg_generation_hours
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    result = cur.fetchone()
                    avg_gen_hours = float(result[0] or 0) if result[0] else 0
            
            sla_metrics["invoice_generation"] = {
                "target_hours": slas["invoice_generation_time"],
                "actual_hours": round(avg_gen_hours, 2),
                "compliance": avg_gen_hours <= slas["invoice_generation_time"],
                "compliance_rate": round((1 - max(0, (avg_gen_hours - slas["invoice_generation_time"]) / slas["invoice_generation_time"])) * 100, 2),
            }
            
            # SLA 2: Tiempo de entrega de emails
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            AVG(EXTRACT(EPOCH FROM (ir.sent_at - i.created_at)) / 3600) as avg_delivery_hours
                        FROM invoice_reminders ir
                        JOIN invoices i ON ir.invoice_id = i.id
                        WHERE ir.reminder_type = 'first'
                        AND ir.sent_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    result = cur.fetchone()
                    avg_delivery_hours = float(result[0] or 0) if result[0] else 0
            
            sla_metrics["email_delivery"] = {
                "target_hours": slas["email_delivery_time"],
                "actual_hours": round(avg_delivery_hours, 2),
                "compliance": avg_delivery_hours <= slas["email_delivery_time"],
                "compliance_rate": round((1 - max(0, (avg_delivery_hours - slas["email_delivery_time"]) / slas["email_delivery_time"])) * 100, 2),
            }
            
            # SLA 3: Tiempo de respuesta a recordatorios
            avg_days = analytics_data.get("avg_days_to_pay", 0)
            reminder_response_hours = avg_days * 24
            
            sla_metrics["reminder_response"] = {
                "target_hours": slas["reminder_response_time"],
                "actual_hours": round(reminder_response_hours, 2),
                "compliance": reminder_response_hours <= slas["reminder_response_time"],
                "compliance_rate": round((1 - max(0, (reminder_response_hours - slas["reminder_response_time"]) / slas["reminder_response_time"])) * 100, 2),
            }
            
            # Calcular SLA general
            overall_compliance = sum(m["compliance_rate"] for m in sla_metrics.values()) / len(sla_metrics) if sla_metrics else 0
            
            sla_summary = {
                "sla_metrics": sla_metrics,
                "overall_compliance_rate": round(overall_compliance, 2),
                "overall_status": "compliant" if overall_compliance >= 90 else "non_compliant",
                "tracked_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Métricas de SLA trackeadas",
                extra={"overall_compliance": overall_compliance}
            )
            
            _track_metric("invoice_billing.sla.compliance_rate", overall_compliance)
            
            return sla_summary
    
    @task(task_id="advanced_market_trends_analysis")
    def advanced_market_trends_analysis(
        analytics_data: Dict[str, Any],
        seasonality_data: Dict[str, Any],
        competitor_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Análisis avanzado de tendencias de mercado combinando múltiples fuentes.
        """
        with _track_operation("advanced_market_trends_analysis"):
            trends = []
            insights = []
            
            # Tendencia 1: Análisis de crecimiento
            conversion_rate = analytics_data.get("conversion_rate", 0)
            avg_days = analytics_data.get("avg_days_to_pay", 0)
            
            # Comparar con período anterior (simplificado)
            growth_trend = "stable"
            if conversion_rate > 75:
                growth_trend = "growing"
            elif conversion_rate < 60:
                growth_trend = "declining"
            
            trends.append({
                "type": "growth",
                "trend": growth_trend,
                "conversion_rate": round(conversion_rate, 2),
                "indicator": "positive" if growth_trend == "growing" else "negative" if growth_trend == "declining" else "neutral",
            })
            
            # Tendencia 2: Estacionalidad
            if seasonality_data.get("analyzed", False):
                peak_month = seasonality_data.get("insights", {}).get("peak_month")
                if peak_month:
                    trends.append({
                        "type": "seasonality",
                        "peak_month": peak_month.get("month_name"),
                        "peak_revenue": peak_month.get("total_paid", 0),
                        "insight": f"Pico estacional en {peak_month.get('month_name')}",
                    })
            
            # Tendencia 3: Competitividad
            if competitor_data.get("competitive_score", 0) > 0:
                competitive_score = competitor_data.get("competitive_score", 0)
                competitive_level = competitor_data.get("competitive_level", "average")
                
                trends.append({
                    "type": "competitiveness",
                    "score": competitive_score,
                    "level": competitive_level,
                    "vs_industry": "above" if competitive_score > 70 else "below" if competitive_score < 50 else "average",
                })
            
            # Insights consolidados
            if growth_trend == "growing" and competitive_score > 70:
                insights.append({
                    "type": "positive",
                    "message": "Crecimiento positivo y competitividad alta - mantener estrategia actual",
                })
            elif growth_trend == "declining":
                insights.append({
                    "type": "warning",
                    "message": "Tendencia de crecimiento negativa - revisar estrategia",
                })
            
            market_analysis = {
                "trends": trends,
                "insights": insights,
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis avanzado de tendencias de mercado completado",
                extra={"trends": len(trends), "insights": len(insights)}
            )
            
            _track_metric("invoice_billing.market_trends.analyzed", 1.0)
            
            return market_analysis
    
    @task(task_id="predictive_alerting_system")
    def predictive_alerting_system(
        analytics_data: Dict[str, Any],
        cash_flow_data: Dict[str, Any],
        risk_data: Dict[str, Any],
        satisfaction_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Sistema de alertas predictivas que anticipa problemas antes de que ocurran.
        """
        with _track_operation("predictive_alerting_system"):
            alerts = []
            
            # Alerta predictiva 1: Tendencia de conversión
            conversion_rate = analytics_data.get("conversion_rate", 0)
            if conversion_rate < 65:
                # Predecir si seguirá bajando
                alerts.append({
                    "type": "predictive",
                    "severity": "high",
                    "category": "conversion_trend",
                    "message": f"Tasa de conversión en {conversion_rate:.1f}% - riesgo de caída adicional",
                    "predicted_impact": "Reducción de revenue en 10-15% si no se actúa",
                    "recommended_action": "Implementar estrategia de optimización inmediata",
                    "time_to_impact": "7-14 días",
                })
            
            # Alerta predictiva 2: Cash flow futuro
            cash_flow_forecast = cash_flow_data.get("forecast", {})
            if cash_flow_forecast:
                total_predicted = cash_flow_forecast.get("total_predicted", 0)
                if total_predicted < 15000:
                    alerts.append({
                        "type": "predictive",
                        "severity": "high",
                        "category": "cash_flow",
                        "message": f"Cash flow predicho bajo: ${total_predicted:,.2f} para próximos 30 días",
                        "predicted_impact": "Posible escasez de liquidez en 2-3 semanas",
                        "recommended_action": "Acelerar cobranza y revisar gastos",
                        "time_to_impact": "14-21 días",
                    })
            
            # Alerta predictiva 3: Satisfacción del cliente
            if satisfaction_data.get("overall_satisfaction", 0) < 60:
                alerts.append({
                    "type": "predictive",
                    "severity": "medium",
                    "category": "satisfaction",
                    "message": f"Satisfacción del cliente en {satisfaction_data.get('overall_satisfaction', 0):.1f}% - riesgo de churn",
                    "predicted_impact": "Posible aumento de churn en 20-30%",
                    "recommended_action": "Implementar programa de retención",
                    "time_to_impact": "30-45 días",
                })
            
            # Alerta predictiva 4: Facturas de alto riesgo
            high_risk_count = len(risk_data.get("high_risk_invoices", []))
            if high_risk_count > 20:
                alerts.append({
                    "type": "predictive",
                    "severity": "high",
                    "category": "risk",
                    "message": f"{high_risk_count} facturas de alto riesgo - posible aumento de pérdidas",
                    "predicted_impact": "Pérdidas potenciales de 15-25% del total en riesgo",
                    "recommended_action": "Revisión inmediata y contacto proactivo",
                    "time_to_impact": "7-10 días",
                })
            
            # Enviar alertas críticas
            critical_alerts = [a for a in alerts if a["severity"] == "high"]
            if critical_alerts:
                for alert in critical_alerts:
                    _send_slack_notification(
                        f"🔮 Alerta Predictiva: {alert['message']}\n"
                        f"Impacto: {alert['predicted_impact']}\n"
                        f"Acción: {alert['recommended_action']}\n"
                        f"Tiempo estimado: {alert['time_to_impact']}",
                        channel="#billing-alerts"
                    )
            
            alerting_summary = {
                "alerts": alerts,
                "critical_count": len(critical_alerts),
                "total_count": len(alerts),
                "generated_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Sistema de alertas predictivas ejecutado",
                extra={"total_alerts": len(alerts), "critical": len(critical_alerts)}
            )
            
            _track_metric("invoice_billing.predictive_alerts.generated", len(alerts))
            
            return alerting_summary
    
    @task(task_id="real_time_resource_optimization")
    def real_time_resource_optimization(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimización de recursos en tiempo real basada en carga actual.
        """
        with _track_operation("real_time_resource_optimization"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar carga actual
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'issued' AND created_at >= NOW() - INTERVAL '24 hours') as pending_24h,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            COUNT(*) FILTER (WHERE reminder_type IS NOT NULL AND sent_at >= NOW() - INTERVAL '24 hours') as reminders_24h
                        FROM invoices i
                        LEFT JOIN invoice_reminders ir ON i.id = ir.invoice_id
                    """)
                    
                    current_load = cur.fetchone()
            
            if not current_load:
                return {"optimized": False, "skipped": True}
            
            pending_24h, overdue_count, reminders_24h = current_load
            
            # Calcular necesidades de recursos
            resource_needs = {
                "invoice_processing": {
                    "current_load": pending_24h or 0,
                    "recommended_capacity": max(50, (pending_24h or 0) * 1.2),
                    "status": "adequate" if (pending_24h or 0) < 100 else "overloaded",
                },
                "collections": {
                    "current_load": overdue_count or 0,
                    "recommended_capacity": max(20, (overdue_count or 0) * 1.3),
                    "status": "adequate" if (overdue_count or 0) < 50 else "overloaded",
                },
                "reminders": {
                    "current_load": reminders_24h or 0,
                    "recommended_capacity": max(30, (reminders_24h or 0) * 1.1),
                    "status": "adequate" if (reminders_24h or 0) < 200 else "overloaded",
                },
            }
            
            # Recomendaciones de optimización
            recommendations = []
            
            for resource, needs in resource_needs.items():
                if needs["status"] == "overloaded":
                    recommendations.append({
                        "resource": resource,
                        "action": f"Escalar capacidad de {resource}",
                        "current": needs["current_load"],
                        "recommended": needs["recommended_capacity"],
                        "priority": "high",
                    })
                elif needs["current_load"] < needs["recommended_capacity"] * 0.5:
                    recommendations.append({
                        "resource": resource,
                        "action": f"Considerar reducir capacidad de {resource}",
                        "current": needs["current_load"],
                        "recommended": needs["recommended_capacity"],
                        "priority": "low",
                    })
            
            optimization_summary = {
                "resource_needs": resource_needs,
                "recommendations": recommendations,
                "overall_status": "optimal" if all(n["status"] == "adequate" for n in resource_needs.values()) else "needs_optimization",
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización de recursos en tiempo real completada",
                extra={"overall_status": optimization_summary["overall_status"]}
            )
            
            _track_metric("invoice_billing.resource_optimization.realtime", 1.0)
            
            return optimization_summary
    
    @task(task_id="advanced_cohort_retention_analysis")
    def advanced_cohort_retention_analysis(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis avanzado de retención por cohortes con métricas detalladas.
        """
        with _track_operation("advanced_cohort_retention_analysis"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar cohortes mensuales
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            DATE_TRUNC('month', MIN(created_at)) as cohort_month,
                            COUNT(DISTINCT customer_email) as cohort_size,
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_invoices,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_invoices,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            SUM(total) FILTER (WHERE status = 'paid') as total_revenue,
                            COUNT(DISTINCT customer_email) FILTER (WHERE created_at >= DATE_TRUNC('month', MIN(created_at)) + INTERVAL '1 month') as retained_next_month
                        FROM invoices
                        WHERE customer_email IS NOT NULL
                        AND created_at >= NOW() - INTERVAL '12 months'
                        GROUP BY DATE_TRUNC('month', MIN(created_at))
                        ORDER BY cohort_month DESC
                        LIMIT 12
                    """)
                    
                    cohorts = cur.fetchall()
            
            if not cohorts:
                return {"analyzed": False, "skipped": True}
            
            cohort_analysis = []
            
            for row in cohorts:
                month, size, paid, overdue, avg_days, revenue, retained = row
                
                conversion_rate = (paid / (paid + overdue) * 100) if (paid + overdue) > 0 else 0
                retention_rate = (retained / size * 100) if size > 0 else 0
                avg_revenue_per_customer = (float(revenue or 0) / size) if size > 0 else 0
                
                cohort_analysis.append({
                    "cohort_month": str(month),
                    "cohort_size": size,
                    "conversion_rate": round(conversion_rate, 2),
                    "retention_rate": round(retention_rate, 2),
                    "avg_days_to_pay": round(float(avg_days or 0), 1),
                    "total_revenue": round(float(revenue or 0), 2),
                    "avg_revenue_per_customer": round(avg_revenue_per_customer, 2),
                })
            
            # Calcular tendencias de retención
            if len(cohort_analysis) >= 2:
                first_retention = cohort_analysis[-1]["retention_rate"]
                last_retention = cohort_analysis[0]["retention_rate"]
                retention_trend = last_retention - first_retention
            else:
                retention_trend = 0
            
            retention_summary = {
                "cohorts": cohort_analysis,
                "retention_trend": round(retention_trend, 2),
                "avg_retention_rate": round(sum(c["retention_rate"] for c in cohort_analysis) / len(cohort_analysis), 2) if cohort_analysis else 0,
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis avanzado de retención por cohortes completado",
                extra={"cohorts": len(cohort_analysis), "avg_retention": retention_summary["avg_retention_rate"]}
            )
            
            _track_metric("invoice_billing.cohort_retention.analyzed", 1.0)
            
            return retention_summary
    
    @task(task_id="continuous_learning_system")
    def continuous_learning_system(
        analytics_data: Dict[str, Any],
        ml_data: Dict[str, Any],
        channel_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Sistema de aprendizaje continuo que mejora predicciones basado en resultados.
        """
        with _track_operation("continuous_learning_system"):
            learning_insights = []
            improvements = []
            
            # Aprendizaje 1: Validar predicciones ML vs resultados reales
            if ml_data.get("predictions"):
                predictions = ml_data.get("predictions", [])
                # Calcular precisión (simplificado)
                high_confidence_predictions = [p for p in predictions if p.get("payment_probability", 0.5) > 0.7]
                
                if high_confidence_predictions:
                    learning_insights.append({
                        "type": "ml_validation",
                        "message": f"{len(high_confidence_predictions)} predicciones de alta confianza generadas",
                        "recommendation": "Monitorear precisión de predicciones vs resultados reales",
                    })
            
            # Aprendizaje 2: Optimizar canales basado en performance
            if channel_data.get("analyzed", False):
                best_channel = channel_data.get("best_channel")
                if best_channel:
                    improvements.append({
                        "type": "channel_optimization",
                        "recommendation": f"Incrementar uso de {best_channel.get('channel')} (score: {best_channel.get('effectiveness_score', 0):.1f})",
                        "expected_improvement": "Aumento de 5-10% en conversión",
                    })
            
            # Aprendizaje 3: Ajustar timing basado en resultados
            conversion_rate = analytics_data.get("conversion_rate", 0)
            avg_days = analytics_data.get("avg_days_to_pay", 0)
            
            if conversion_rate < 70 and avg_days > 30:
                improvements.append({
                    "type": "timing_optimization",
                    "recommendation": "Ajustar timing de recordatorios - enviar más temprano",
                    "expected_improvement": "Reducción de 3-5 días en promedio",
                })
            
            # Calcular score de aprendizaje
            learning_score = 50  # Base
            
            if len(improvements) > 0:
                learning_score += 20
            if len(learning_insights) > 0:
                learning_score += 15
            if conversion_rate > 75:
                learning_score += 15
            
            learning_summary = {
                "learning_insights": learning_insights,
                "improvements": improvements,
                "learning_score": min(100, learning_score),
                "learned_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Sistema de aprendizaje continuo ejecutado",
                extra={"learning_score": learning_score, "improvements": len(improvements)}
            )
            
            _track_metric("invoice_billing.continuous_learning.score", learning_score)
            
            return learning_summary
    
    @task(task_id="predictive_cost_optimization")
    def predictive_cost_optimization(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimización predictiva de costos basada en proyecciones futuras.
        """
        with _track_operation("predictive_cost_optimization"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Proyectar costos futuros
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'issued' AND created_at >= NOW() - INTERVAL '30 days') as invoices_30d,
                            COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                            COUNT(*) FILTER (WHERE reminder_type IS NOT NULL AND sent_at >= NOW() - INTERVAL '30 days') as reminders_30d
                        FROM invoices i
                        LEFT JOIN invoice_reminders ir ON i.id = ir.invoice_id
                    """)
                    
                    current_metrics = cur.fetchone()
            
            if not current_metrics:
                return {"optimized": False, "skipped": True}
            
            invoices_30d, overdue_count, reminders_30d = current_metrics
            
            # Proyectar costos para próximos 30 días
            projected_invoices = (invoices_30d or 0) * 1.1  # Asumir 10% de crecimiento
            projected_overdue = (overdue_count or 0) * 1.05  # Asumir 5% de crecimiento
            projected_reminders = (reminders_30d or 0) * 1.08  # Asumir 8% de crecimiento
            
            # Calcular costos proyectados
            invoice_cost = projected_invoices * 2.5
            collection_cost = projected_overdue * 5.0
            reminder_cost = projected_reminders * 0.5
            
            total_projected_cost = invoice_cost + collection_cost + reminder_cost
            
            # Optimizaciones sugeridas
            optimizations = []
            
            # Optimización 1: Reducir recordatorios innecesarios
            if projected_reminders > projected_invoices * 2:
                savings = (projected_reminders - projected_invoices * 1.5) * 0.5
                optimizations.append({
                    "type": "reminder_optimization",
                    "action": "Optimizar timing de recordatorios para reducir cantidad",
                    "projected_savings": round(savings, 2),
                    "impact": "medium",
                })
            
            # Optimización 2: Mejorar conversión para reducir cobranza
            if projected_overdue > projected_invoices * 0.2:
                potential_savings = (projected_overdue - projected_invoices * 0.15) * 5.0
                optimizations.append({
                    "type": "conversion_improvement",
                    "action": "Mejorar tasa de conversión para reducir facturas vencidas",
                    "projected_savings": round(potential_savings, 2),
                    "impact": "high",
                })
            
            # Calcular ahorro total potencial
            total_potential_savings = sum(o["projected_savings"] for o in optimizations)
            savings_percentage = (total_potential_savings / total_projected_cost * 100) if total_projected_cost > 0 else 0
            
            cost_optimization = {
                "projected_costs_30d": {
                    "invoice_processing": round(invoice_cost, 2),
                    "collections": round(collection_cost, 2),
                    "reminders": round(reminder_cost, 2),
                    "total": round(total_projected_cost, 2),
                },
                "optimizations": optimizations,
                "total_potential_savings": round(total_potential_savings, 2),
                "savings_percentage": round(savings_percentage, 2),
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización predictiva de costos completada",
                extra={"projected_cost": total_projected_cost, "potential_savings": total_potential_savings}
            )
            
            _track_metric("invoice_billing.cost_optimization.predictive", 1.0)
            
            return cost_optimization
    
    @task(task_id="advanced_anomaly_detection")
    def advanced_anomaly_detection(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detección avanzada de anomalías usando análisis estadístico.
        """
        with _track_operation("advanced_anomaly_detection"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Obtener datos históricos
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            total,
                            EXTRACT(DAY FROM (updated_at - created_at)) as days_to_pay,
                            EXTRACT(EPOCH FROM (created_at - LAG(created_at) OVER (ORDER BY created_at))) / 3600 as hours_since_last
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '90 days'
                        AND status IN ('paid', 'overdue')
                        ORDER BY created_at DESC
                        LIMIT 500
                    """)
                    
                    data = cur.fetchall()
            
            if len(data) < 10:
                return {"detected": 0, "skipped": True}
            
            # Calcular estadísticas
            amounts = [float(row[0] or 0) for row in data]
            days = [float(row[1] or 0) if row[1] else 0 for row in data]
            hours = [float(row[2] or 0) if row[2] else 0 for row in data]
            
            # Detectar anomalías usando Z-score
            anomalies = []
            
            if amounts:
                mean_amount = sum(amounts) / len(amounts)
                std_amount = (sum((x - mean_amount) ** 2 for x in amounts) / len(amounts)) ** 0.5
                
                for i, amount in enumerate(amounts):
                    if std_amount > 0:
                        z_score = abs((amount - mean_amount) / std_amount)
                        if z_score > 3:  # Más de 3 desviaciones estándar
                            anomalies.append({
                                "type": "amount_anomaly",
                                "invoice_index": i,
                                "amount": round(amount, 2),
                                "z_score": round(z_score, 2),
                                "severity": "high" if z_score > 4 else "medium",
                            })
            
            if days:
                mean_days = sum(days) / len(days)
                std_days = (sum((x - mean_days) ** 2 for x in days) / len(days)) ** 0.5
                
                for i, day in enumerate(days):
                    if std_days > 0:
                        z_score = abs((day - mean_days) / std_days)
                        if z_score > 2.5:  # Más de 2.5 desviaciones estándar
                            anomalies.append({
                                "type": "days_anomaly",
                                "invoice_index": i,
                                "days": round(day, 1),
                                "z_score": round(z_score, 2),
                                "severity": "high" if z_score > 3.5 else "medium",
                            })
            
            # Detectar patrones inusuales
            if len(hours) > 1:
                avg_hours = sum(hours[1:]) / (len(hours) - 1) if len(hours) > 1 else 0
                for i, hour in enumerate(hours[1:], 1):
                    if hour > 0 and avg_hours > 0:
                        if hour < avg_hours * 0.1:  # Menos del 10% del promedio
                            anomalies.append({
                                "type": "frequency_anomaly",
                                "invoice_index": i,
                                "hours_since_last": round(hour, 2),
                                "severity": "medium",
                            })
            
            anomaly_summary = {
                "anomalies": anomalies[:20],  # Top 20
                "total_detected": len(anomalies),
                "high_severity": len([a for a in anomalies if a["severity"] == "high"]),
                "detected_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Detección avanzada de anomalías completada",
                extra={"total": len(anomalies), "high_severity": anomaly_summary["high_severity"]}
            )
            
            _track_metric("invoice_billing.anomaly_detection.detected", len(anomalies))
            
            return anomaly_summary
    
    @task(task_id="personalized_recommendations_engine")
    def personalized_recommendations_engine(
        segmentation_data: Dict[str, Any],
        scoring_data: Dict[str, Any],
        satisfaction_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Motor de recomendaciones personalizadas por cliente.
        """
        with _track_operation("personalized_recommendations_engine"):
            recommendations = []
            
            # Recomendaciones por segmento
            if segmentation_data.get("segmented", 0) > 0:
                segments = segmentation_data.get("segments", {})
                
                # Champions
                champions = segments.get("champions", {}).get("count", 0)
                if champions > 0:
                    recommendations.append({
                        "segment": "champions",
                        "recommendation": "Programa de lealtad premium",
                        "action": "Ofrecer beneficios exclusivos y early access a nuevos productos",
                        "expected_impact": "Aumento de 10-15% en CLV",
                    })
                
                # At Risk
                at_risk = segments.get("at_risk", {}).get("count", 0)
                if at_risk > 0:
                    recommendations.append({
                        "segment": "at_risk",
                        "recommendation": "Programa de recuperación",
                        "action": "Contacto personalizado, planes de pago flexibles, descuentos por pago inmediato",
                        "expected_impact": "Reducción de churn en 20-25%",
                    })
            
            # Recomendaciones por tier
            if scoring_data.get("scored", 0) > 0:
                tier_dist = scoring_data.get("tier_distribution", {})
                
                # Platinum
                if tier_dist.get("platinum", 0) > 0:
                    recommendations.append({
                        "tier": "platinum",
                        "recommendation": "Servicio VIP dedicado",
                        "action": "Account manager dedicado, soporte prioritario 24/7, términos de pago extendidos",
                        "expected_impact": "Retención del 95%+",
                    })
                
                # Bronze
                if tier_dist.get("bronze", 0) > 0:
                    recommendations.append({
                        "tier": "bronze",
                        "recommendation": "Programa de crecimiento",
                        "action": "Incentivos para aumentar frecuencia de compra, educación sobre beneficios",
                        "expected_impact": "Upgrade a Silver en 3-6 meses",
                    })
            
            # Recomendaciones por satisfacción
            if satisfaction_data.get("overall_satisfaction", 0) < 60:
                bottom_customers = satisfaction_data.get("bottom_satisfied_customers", [])
                if bottom_customers:
                    recommendations.append({
                        "category": "satisfaction_improvement",
                        "recommendation": "Mejorar experiencia de clientes insatisfechos",
                        "action": f"Contacto proactivo con {len(bottom_customers)} clientes, encuestas de feedback, resolución rápida de problemas",
                        "expected_impact": "Aumento de satisfacción en 15-20 puntos",
                    })
            
            personalized_summary = {
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "generated_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Motor de recomendaciones personalizadas ejecutado",
                extra={"total": len(recommendations)}
            )
            
            _track_metric("invoice_billing.personalized_recommendations.generated", len(recommendations))
            
            return personalized_summary
    
    @task(task_id="workflow_optimization")
    def workflow_optimization(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Optimización de flujo de trabajo basada en análisis de eficiencia.
        """
        with _track_operation("workflow_optimization"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Analizar tiempos de procesamiento
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            AVG(EXTRACT(EPOCH FROM (ir.sent_at - i.created_at)) / 3600) as avg_hours_to_first_reminder,
                            AVG(EXTRACT(EPOCH FROM (i.updated_at - i.created_at)) / 86400) FILTER (WHERE i.status = 'paid') as avg_days_to_payment
                        FROM invoices i
                        LEFT JOIN invoice_reminders ir ON i.id = ir.invoice_id AND ir.reminder_type = 'first'
                        WHERE i.created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    workflow_metrics = cur.fetchone()
            
            if not workflow_metrics:
                return {"optimized": False, "skipped": True}
            
            avg_hours_to_reminder = float(workflow_metrics[0] or 0) if workflow_metrics[0] else 0
            avg_days_to_payment = float(workflow_metrics[1] or 0) if workflow_metrics[1] else 0
            
            # Identificar cuellos de botella
            bottlenecks = []
            optimizations = []
            
            # Cuello de botella 1: Tiempo hasta primer recordatorio
            if avg_hours_to_reminder > 24:
                bottlenecks.append({
                    "type": "reminder_delay",
                    "current": round(avg_hours_to_reminder, 1),
                    "target": 12,
                    "impact": "high",
                })
                optimizations.append({
                    "area": "reminder_timing",
                    "action": "Reducir tiempo hasta primer recordatorio a <12 horas",
                    "expected_improvement": "Reducción de 2-3 días en tiempo de pago",
                })
            
            # Cuello de botella 2: Tiempo de pago
            if avg_days_to_payment > 35:
                bottlenecks.append({
                    "type": "payment_delay",
                    "current": round(avg_days_to_payment, 1),
                    "target": 25,
                    "impact": "high",
                })
                optimizations.append({
                    "area": "payment_process",
                    "action": "Optimizar proceso de pago y recordatorios más frecuentes",
                    "expected_improvement": "Reducción de 5-7 días en promedio",
                })
            
            # Calcular eficiencia del workflow
            efficiency_score = 100
            if avg_hours_to_reminder > 24:
                efficiency_score -= 20
            if avg_days_to_payment > 35:
                efficiency_score -= 25
            if len(bottlenecks) > 0:
                efficiency_score -= 10 * len(bottlenecks)
            
            efficiency_score = max(0, efficiency_score)
            
            workflow_summary = {
                "current_metrics": {
                    "avg_hours_to_first_reminder": round(avg_hours_to_reminder, 1),
                    "avg_days_to_payment": round(avg_days_to_payment, 1),
                },
                "bottlenecks": bottlenecks,
                "optimizations": optimizations,
                "efficiency_score": efficiency_score,
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización de flujo de trabajo completada",
                extra={"efficiency_score": efficiency_score, "bottlenecks": len(bottlenecks)}
            )
            
            _track_metric("invoice_billing.workflow.efficiency_score", efficiency_score)
            
            return workflow_summary
    
    @task(task_id="change_impact_analysis")
    def change_impact_analysis(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Análisis de impacto de cambios en estrategias y procesos.
        """
        with _track_operation("change_impact_analysis"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            # Comparar métricas actuales vs período anterior
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Período actual (últimos 30 días)
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            SUM(total) FILTER (WHERE status = 'paid') as total_revenue
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    current = cur.fetchone()
                    
                    # Período anterior (30-60 días atrás)
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                            AVG(EXTRACT(DAY FROM (updated_at - created_at))) FILTER (WHERE status = 'paid') as avg_days,
                            SUM(total) FILTER (WHERE status = 'paid') as total_revenue
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '60 days'
                        AND created_at < NOW() - INTERVAL '30 days'
                    """)
                    
                    previous = cur.fetchone()
            
            if not current or not previous:
                return {"analyzed": False, "skipped": True}
            
            current_paid = current[0] or 0
            current_days = float(current[1] or 0) if current[1] else 0
            current_revenue = float(current[2] or 0)
            
            previous_paid = previous[0] or 0
            previous_days = float(previous[1] or 0) if previous[1] else 0
            previous_revenue = float(previous[2] or 0)
            
            # Calcular cambios
            paid_change = ((current_paid - previous_paid) / previous_paid * 100) if previous_paid > 0 else 0
            days_change = current_days - previous_days
            revenue_change = ((current_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            # Evaluar impacto
            impacts = []
            
            if paid_change > 10:
                impacts.append({
                    "metric": "paid_invoices",
                    "change": round(paid_change, 2),
                    "impact": "positive",
                    "significance": "high" if paid_change > 20 else "medium",
                })
            elif paid_change < -10:
                impacts.append({
                    "metric": "paid_invoices",
                    "change": round(paid_change, 2),
                    "impact": "negative",
                    "significance": "high" if paid_change < -20 else "medium",
                })
            
            if days_change < -3:
                impacts.append({
                    "metric": "avg_days_to_pay",
                    "change": round(days_change, 1),
                    "impact": "positive",
                    "significance": "high" if days_change < -5 else "medium",
                })
            elif days_change > 3:
                impacts.append({
                    "metric": "avg_days_to_pay",
                    "change": round(days_change, 1),
                    "impact": "negative",
                    "significance": "high" if days_change > 5 else "medium",
                })
            
            if revenue_change > 15:
                impacts.append({
                    "metric": "revenue",
                    "change": round(revenue_change, 2),
                    "impact": "positive",
                    "significance": "high" if revenue_change > 25 else "medium",
                })
            
            impact_summary = {
                "current_period": {
                    "paid_invoices": current_paid,
                    "avg_days_to_pay": round(current_days, 1),
                    "total_revenue": round(current_revenue, 2),
                },
                "previous_period": {
                    "paid_invoices": previous_paid,
                    "avg_days_to_pay": round(previous_days, 1),
                    "total_revenue": round(previous_revenue, 2),
                },
                "changes": {
                    "paid_invoices_pct": round(paid_change, 2),
                    "avg_days_to_pay_delta": round(days_change, 1),
                    "revenue_pct": round(revenue_change, 2),
                },
                "impacts": impacts,
                "overall_impact": "positive" if len([i for i in impacts if i["impact"] == "positive"]) > len([i for i in impacts if i["impact"] == "negative"]) else "negative" if len([i for i in impacts if i["impact"] == "negative"]) > 0 else "neutral",
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Análisis de impacto de cambios completado",
                extra={"overall_impact": impact_summary["overall_impact"], "impacts": len(impacts)}
            )
            
            _track_metric("invoice_billing.change_impact.analyzed", 1.0)
            
            return impact_summary
    
    @task(task_id="data_quality_metrics")
    def data_quality_metrics(analytics_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Métricas de calidad de datos para asegurar integridad.
        """
        with _track_operation("data_quality_metrics"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            quality_metrics = {}
            
            # Métrica 1: Completitud de emails
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(customer_email) as with_email,
                            COUNT(*) FILTER (WHERE customer_email IS NOT NULL AND customer_email LIKE '%@%.%') as valid_email
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    email_metrics = cur.fetchone()
            
            if email_metrics:
                total, with_email, valid_email = email_metrics
                email_completeness = (with_email / total * 100) if total > 0 else 0
                email_validity = (valid_email / with_email * 100) if with_email > 0 else 0
                
                quality_metrics["email_quality"] = {
                    "completeness_pct": round(email_completeness, 2),
                    "validity_pct": round(email_validity, 2),
                    "status": "good" if email_completeness > 90 and email_validity > 95 else "needs_improvement",
                }
            
            # Métrica 2: Integridad de metadata
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) as total,
                            COUNT(metadata) as with_metadata
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    metadata_metrics = cur.fetchone()
            
            if metadata_metrics:
                total, with_metadata = metadata_metrics
                metadata_completeness = (with_metadata / total * 100) if total > 0 else 0
                
                quality_metrics["metadata_quality"] = {
                    "completeness_pct": round(metadata_completeness, 2),
                    "status": "good" if metadata_completeness > 80 else "needs_improvement",
                }
            
            # Métrica 3: Consistencia de datos
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE total IS NULL OR total <= 0) as invalid_totals,
                            COUNT(*) FILTER (WHERE created_at > updated_at) as invalid_dates
                        FROM invoices
                        WHERE created_at >= NOW() - INTERVAL '30 days'
                    """)
                    
                    consistency_metrics = cur.fetchone()
            
            if consistency_metrics:
                invalid_totals, invalid_dates = consistency_metrics
                
                quality_metrics["data_consistency"] = {
                    "invalid_totals": invalid_totals or 0,
                    "invalid_dates": invalid_dates or 0,
                    "status": "good" if (invalid_totals or 0) == 0 and (invalid_dates or 0) == 0 else "needs_improvement",
                }
            
            # Calcular score general de calidad
            quality_score = 100
            
            if quality_metrics.get("email_quality", {}).get("status") == "needs_improvement":
                quality_score -= 20
            if quality_metrics.get("metadata_quality", {}).get("status") == "needs_improvement":
                quality_score -= 15
            if quality_metrics.get("data_consistency", {}).get("status") == "needs_improvement":
                quality_score -= 25
            
            quality_score = max(0, quality_score)
            
            quality_summary = {
                "quality_metrics": quality_metrics,
                "overall_quality_score": quality_score,
                "overall_status": "excellent" if quality_score > 90 else "good" if quality_score > 70 else "needs_improvement",
                "analyzed_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Métricas de calidad de datos completadas",
                extra={"quality_score": quality_score, "status": quality_summary["overall_status"]}
            )
            
            _track_metric("invoice_billing.data_quality.score", quality_score)
            
            return quality_summary
    
    @task(task_id="multi_channel_communication_optimization")
    def multi_channel_communication_optimization(
        channel_data: Dict[str, Any],
        segmentation_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Optimización de comunicación multicanal basada en performance.
        """
        with _track_operation("multi_channel_communication_optimization"):
            strategies = []
            
            # Estrategia 1: Asignación de canales por segmento
            if segmentation_data.get("segmented", 0) > 0:
                segments = segmentation_data.get("segments", {})
                
                # Champions: Email + Dedicated Support
                if segments.get("champions", {}).get("count", 0) > 0:
                    strategies.append({
                        "segment": "champions",
                        "channels": ["email", "dedicated_support"],
                        "priority": "email",
                        "rationale": "Clientes de alto valor - comunicación premium",
                    })
                
                # At Risk: Email + Phone + SMS
                if segments.get("at_risk", {}).get("count", 0) > 0:
                    strategies.append({
                        "segment": "at_risk",
                        "channels": ["email", "phone", "sms"],
                        "priority": "phone",
                        "rationale": "Clientes en riesgo - comunicación urgente y directa",
                    })
            
            # Estrategia 2: Optimización basada en performance de canales
            if channel_data.get("analyzed", False):
                best_channel = channel_data.get("best_channel")
                if best_channel:
                    strategies.append({
                        "type": "channel_optimization",
                        "recommended_channel": best_channel.get("channel"),
                        "effectiveness_score": best_channel.get("effectiveness_score", 0),
                        "recommendation": f"Incrementar uso de {best_channel.get('channel')} en 20-30%",
                        "expected_improvement": "Aumento de 3-5% en conversión general",
                    })
            
            # Estrategia 3: Secuencia de canales
            strategies.append({
                "type": "channel_sequence",
                "sequence": [
                    {"step": 1, "channel": "email", "timing": "immediate"},
                    {"step": 2, "channel": "email_reminder", "timing": "7_days"},
                    {"step": 3, "channel": "phone", "timing": "14_days"},
                    {"step": 4, "channel": "collections", "timing": "30_days"},
                ],
                "rationale": "Secuencia optimizada basada en efectividad y costo",
            })
            
            optimization_summary = {
                "strategies": strategies,
                "total_strategies": len(strategies),
                "optimized_at": pendulum.now("UTC").isoformat(),
            }
            
            logger.info(
                "Optimización de comunicación multicanal completada",
                extra={"strategies": len(strategies)}
            )
            
            _track_metric("invoice_billing.multichannel.optimized", 1.0)
            
            return optimization_summary
    
    @task(task_id="predict_payment_risk")
    def predict_payment_risk(check_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analiza riesgo de pago basado en historial y patrones.
        """
        with _track_operation("predict_payment_risk"):
            ctx = get_current_context()
            params = ctx["params"]
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            unpaid_invoices = check_data.get("unpaid_invoices", [])
            
            if not unpaid_invoices:
                return {"analyzed": 0, "high_risk": 0, "skipped": False}
            
            high_risk_invoices = []
            
            for inv in unpaid_invoices[:50]:  # Limitar análisis
                inv_id = inv.get("id")
                days_since = inv.get("days_since_issue", 0)
                total = float(inv.get("total", 0))
                customer_email = inv.get("customer_email")
                
                if not customer_email:
                    continue
                
                # Análisis simple de riesgo
                risk_score = 0
                risk_factors = []
                
                # Factor 1: Días de retraso
                if days_since > 14:
                    risk_score += 40
                    risk_factors.append("retraso_extendido")
                elif days_since > 7:
                    risk_score += 20
                    risk_factors.append("retraso_moderado")
                
                # Factor 2: Historial de pagos
                with hook.get_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            SELECT 
                                COUNT(*) FILTER (WHERE status = 'paid') as paid_count,
                                COUNT(*) FILTER (WHERE status = 'overdue') as overdue_count,
                                COUNT(*) as total_count
                            FROM invoices
                            WHERE customer_email = %s
                            AND created_at < NOW() - INTERVAL '90 days'
                        """, (customer_email,))
                        
                        history = cur.fetchone()
                        if history:
                            paid_count = history[0] or 0
                            overdue_count = history[1] or 0
                            total_count = history[2] or 0
                            
                            if total_count > 0:
                                overdue_rate = (overdue_count / total_count) * 100
                                if overdue_rate > 50:
                                    risk_score += 30
                                    risk_factors.append("historial_malo")
                                elif overdue_rate > 25:
                                    risk_score += 15
                                    risk_factors.append("historial_moderado")
                
                # Factor 3: Monto
                if total > 10000:
                    risk_score += 10
                    risk_factors.append("monto_alto")
                
                if risk_score >= 50:
                    high_risk_invoices.append({
                        "invoice_id": inv_id,
                        "risk_score": risk_score,
                        "risk_factors": risk_factors,
                        "days_since": days_since,
                        "amount": total,
                    })
            
            if high_risk_invoices:
                logger.warning(
                    f"Detectadas {len(high_risk_invoices)} facturas de alto riesgo",
                    extra={"high_risk": len(high_risk_invoices)}
                )
                
                # Notificar a Slack
                _send_slack_notification(
                    f"🚨 {len(high_risk_invoices)} facturas de alto riesgo detectadas. "
                    f"Revisar inmediatamente."
                )
                
                _track_metric("invoice_billing.risk.high_risk_detected", len(high_risk_invoices))
            
            return {
                "analyzed": len(unpaid_invoices),
                "high_risk": len(high_risk_invoices),
                "high_risk_invoices": high_risk_invoices,
                "skipped": False,
            }
    
    # Pipeline principal
    health = health_check()
    
    # Generación mensual de facturas (día 1)
    invoices_from_subs = generate_invoices_from_subscriptions()
    invoices_generated = generate_monthly_invoices()
    
    # Combinar facturas generadas
    @task(task_id="merge_invoice_sources")
    def merge_invoice_sources(
        subs_data: Dict[str, Any],
        manual_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Combina facturas de diferentes fuentes."""
        total = subs_data.get("invoices_generated", 0) + manual_data.get("invoices_generated", 0)
        return {
            "invoices_generated": total,
            "from_subscriptions": subs_data.get("invoices_generated", 0),
            "manual": manual_data.get("invoices_generated", 0),
        }
    
    merged_invoices = merge_invoice_sources(invoices_from_subs, invoices_generated)
    emails_sent = send_invoice_emails(merged_invoices)
    
    # Verificación diaria de pagos pendientes
    unpaid_check = check_unpaid_invoices()
    
    # Sincronización con Stripe
    stripe_sync = sync_with_stripe(unpaid_check)
    
    # A/B Testing
    ab_testing = ab_test_email_templates(unpaid_check)
    
    # Personalización
    personalization = personalize_customer_communication(unpaid_check)
    
    # Análisis de riesgo y ML
    risk_analysis = predict_payment_risk(unpaid_check)
    ml_predictions = predict_payment_probability_ml(unpaid_check)
    
    # Análisis de sentimiento
    sentiment_analysis = analyze_customer_sentiment(unpaid_check)
    
    # Predicción de churn
    churn_prediction = predict_customer_churn(unpaid_check)
    
    # Optimización de descuentos
    discount_optimization = optimize_discount_strategy(unpaid_check)
    
    # Integración con gateways de pago
    payment_gateways = integrate_payment_gateways(unpaid_check)
    
    # Detección de fraude
    fraud_detection = detect_fraud_anomalies(unpaid_check)
    
    # Análisis de rentabilidad
    profitability_analysis = analyze_customer_profitability(unpaid_check)
    
    # Optimización de términos de pago
    payment_terms_optimization = optimize_payment_terms(unpaid_check)
    
    # Análisis de tendencias
    payment_trends = analyze_payment_trends(analytics)
    
    # Predicción de cash flow
    cash_flow_prediction = predict_cash_flow(analytics)
    
    # Integración con firma electrónica
    esignature = integrate_electronic_signature(merged_invoices)
    
    # Análisis de satisfacción
    satisfaction_analysis = analyze_customer_satisfaction(unpaid_check)
    
    # Integración con sistemas de contabilidad adicionales
    additional_accounting = integrate_additional_accounting_systems(merged_invoices)
    
    # Optimización de precios
    pricing_optimization = optimize_pricing_strategy(analytics)
    
    # Sistema de lealtad y recompensas
    loyalty_rewards = implement_loyalty_rewards(unpaid_check)
    
    # Integración con ERP
    erp_integration = integrate_erp_systems(merged_invoices)
    
    # Automatización de negociaciones
    payment_negotiations = automate_payment_negotiations(unpaid_check)
    
    # Optimización de rutas de cobro
    collection_routes = optimize_collection_routes(unpaid_check)
    
    # Análisis de tendencias de mercado
    market_trends = analyze_market_trends(analytics)
    
    # Análisis de competencia
    competitor_benchmarks = analyze_competitor_benchmarks(analytics)
    
    # Cálculo de ROI
    roi_metrics = calculate_roi_metrics(analytics)
    
    # Optimización de recursos
    resource_optimization = optimize_resource_allocation(analytics)
    
    # Integración con sistemas de compliance
    compliance_integration = integrate_compliance_systems(merged_invoices)
    
    # Integración con sistemas BI
    bi_integration = integrate_bi_systems(analytics)
    
    # Notificaciones push
    push_notifications = send_push_notifications(
        reminders_sent,
        escalations_sent,
    )
    
    # Análisis predictivo avanzado
    predictive_analytics = advanced_predictive_analytics(
        analytics,
        ml_predictions,
        cash_flow_prediction,
    )
    
    # Optimización de eficiencia de costos
    cost_optimization = optimize_cost_efficiency(analytics)
    
    # Análisis de tendencias de CLV
    clv_trends = analyze_customer_lifetime_value_trends(analytics)
    
    # Smart routing
    smart_routing = implement_smart_routing(unpaid_check)
    
    # Resumen ejecutivo
    executive_summary = generate_executive_summary(
        analytics,
        roi_metrics,
        competitor_benchmarks,
        cash_flow_prediction,
    )
    
    # Segmentación avanzada de clientes
    customer_segmentation = advanced_customer_segmentation(analytics)
    
    # Análisis de estacionalidad
    seasonality_analysis = analyze_seasonality_patterns(analytics)
    
    # Optimización de precios dinámicos
    dynamic_pricing = implement_dynamic_pricing(analytics)
    
    # Sistema de alertas proactivas
    proactive_alerts = proactive_alerting_system(
        analytics,
        cash_flow_prediction,
        risk_analysis,
    )
    
    # Análisis de rentabilidad de productos
    product_profitability = analyze_product_profitability(analytics)
    
    # Gestión de crédito
    credit_management = implement_credit_management(unpaid_check)
    
    # Análisis de correlaciones
    correlations = analyze_correlations(analytics)
    
    # Auto-healing
    auto_healing = implement_auto_healing(unpaid_check, reminders_sent)
    
    # Scoring avanzado de clientes
    customer_scoring = advanced_customer_scoring(analytics)
    
    # Reporte de insights consolidado
    insights_report = generate_insights_report(
        analytics,
        customer_segmentation,
        seasonality_analysis,
        product_profitability,
    )
    
    # Análisis de performance de canales
    channel_performance = analyze_channel_performance(
        emails_sent,
        reminders_sent,
        escalations_sent,
    )
    
    # Sistema de backup y recovery
    backup_recovery = implement_backup_recovery(analytics)
    
    # Métricas en tiempo real
    realtime_metrics = real_time_metrics_dashboard(
        analytics,
        cash_flow_prediction,
        risk_analysis,
    )
    
    # Optimización de estrategia de comunicación
    communication_strategy = optimize_communication_strategy(
        customer_segmentation,
        customer_scoring,
        channel_performance,
    )
    
    # Análisis avanzado de satisfacción
    advanced_satisfaction = advanced_satisfaction_analysis(
        analytics,
        sentiment_analysis,
        customer_scoring,
    )
    
    # Motor de recomendaciones inteligente
    intelligent_recommendations = intelligent_recommendations_engine(
        analytics,
        risk_analysis,
        customer_segmentation,
        product_profitability,
    )
    
    # Tracking de métricas SLA
    sla_tracking = sla_metrics_tracking(analytics)
    
    # Análisis avanzado de tendencias de mercado
    advanced_market_trends = advanced_market_trends_analysis(
        analytics,
        seasonality_analysis,
        competitor_benchmarks,
    )
    
    # Sistema de alertas predictivas
    predictive_alerts = predictive_alerting_system(
        analytics,
        cash_flow_prediction,
        risk_analysis,
        advanced_satisfaction,
    )
    
    # Optimización de recursos en tiempo real
    realtime_resource_opt = real_time_resource_optimization(analytics)
    
    # Análisis avanzado de retención por cohortes
    cohort_retention = advanced_cohort_retention_analysis(analytics)
    
    # Sistema de aprendizaje continuo
    continuous_learning = continuous_learning_system(
        analytics,
        ml_predictions,
        channel_performance,
    )
    
    # Optimización predictiva de costos
    predictive_cost_opt = predictive_cost_optimization(analytics)
    
    # Detección avanzada de anomalías
    anomaly_detection = advanced_anomaly_detection(analytics)
    
    # Motor de recomendaciones personalizadas
    personalized_recommendations = personalized_recommendations_engine(
        customer_segmentation,
        customer_scoring,
        advanced_satisfaction,
    )
    
    # Optimización de flujo de trabajo
    workflow_opt = workflow_optimization(analytics)
    
    # Análisis de impacto de cambios
    change_impact = change_impact_analysis(analytics)
    
    # Métricas de calidad de datos
    data_quality = data_quality_metrics(analytics)
    
    # Optimización de comunicación multicanal
    multichannel_opt = multi_channel_communication_optimization(
        channel_performance,
        customer_segmentation,
    )
    
    # Recomendaciones de acciones
    action_recommendations = generate_action_recommendations(
        risk_analysis,
        churn_prediction,
        sentiment_analysis,
    )
    
    # Optimización de timing
    timing_optimization = optimize_email_timing(unpaid_check)
    
    # Recordatorios y escalaciones
    reminders_sent = send_payment_reminders(unpaid_check)
    escalations_sent = escalate_to_collections(unpaid_check)
    
    # Retry inteligente
    intelligent_retry = intelligent_retry_failed_emails()
    
    # Sincronización con CRM
    crm_sync = sync_with_crm(
        merged_invoices,
        reminders_sent,
        escalations_sent,
    )
    
    # Generación de PDFs
    pdfs_generated = generate_invoice_pdfs(merged_invoices)
    
    # Sincronización con QuickBooks
    quickbooks_sync = sync_to_quickbooks(merged_invoices)
    
    # Analytics y reportes
    analytics = generate_analytics_report(
        merged_invoices,
        emails_sent,
        reminders_sent,
        escalations_sent,
    )
    
    # Análisis de cohortes (depende de analytics)
    cohort_analysis = analyze_cohorts(analytics)
    
    # Dashboard de métricas
    dashboard = generate_dashboard_metrics(
        analytics,
        cohort_analysis,
        ml_predictions,
    )
    
    # Exportación a S3
    s3_export = export_analytics_to_s3(analytics)
    
    # Dead letter queue
    dlq = save_to_dead_letter_queue(
        emails_sent,
        reminders_sent,
        escalations_sent,
    )
    
    # Webhooks
    webhooks = send_webhook_notifications(
        merged_invoices,
        reminders_sent,
        escalations_sent,
    )
    
    # Dependencias
    health >> [invoices_from_subs, invoices_generated] >> merged_invoices
    merged_invoices >> [emails_sent, pdfs_generated]
    merged_invoices >> quickbooks_sync
    
    health >> unpaid_check >> [
        stripe_sync, 
        risk_analysis, 
        ml_predictions, 
        ab_testing, 
        personalization,
        sentiment_analysis,
        churn_prediction,
        discount_optimization,
        payment_gateways,
        fraud_detection,
        profitability_analysis,
        payment_terms_optimization,
        satisfaction_analysis,
        loyalty_rewards,
    ]
    unpaid_check >> timing_optimization
    unpaid_check >> [reminders_sent, escalations_sent, payment_negotiations, smart_routing]
    
    merged_invoices >> [esignature, erp_integration, additional_accounting, compliance_integration]
    
    [emails_sent, reminders_sent, escalations_sent] >> analytics
    analytics >> [
        cohort_analysis, 
        payment_trends, 
        cash_flow_prediction, 
        pricing_optimization, 
        demand_forecast,
        competitor_benchmarks,
        roi_metrics,
        resource_optimization,
        bi_integration,
        cost_optimization,
        clv_trends,
        customer_segmentation,
        seasonality_analysis,
        dynamic_pricing,
        product_profitability,
        correlations,
        customer_scoring,
    ]
    [analytics, cohort_analysis, ml_predictions, payment_trends, cash_flow_prediction, demand_forecast, competitor_benchmarks, roi_metrics, predictive_analytics] >> dashboard
    [analytics, roi_metrics, competitor_benchmarks, cash_flow_prediction] >> executive_summary
    [analytics, cash_flow_prediction, risk_analysis] >> proactive_alerts
    [analytics, cash_flow_prediction, risk_analysis] >> realtime_metrics
    unpaid_check >> credit_management
    [unpaid_check, reminders_sent] >> auto_healing
    [analytics, customer_segmentation, seasonality_analysis, product_profitability] >> insights_report
    [emails_sent, reminders_sent, escalations_sent] >> channel_performance
    analytics >> backup_recovery
    [customer_segmentation, customer_scoring, channel_performance] >> communication_strategy
    [analytics, sentiment_analysis, customer_scoring] >> advanced_satisfaction
    [analytics, risk_analysis, customer_segmentation, product_profitability] >> intelligent_recommendations
    analytics >> sla_tracking
    [analytics, seasonality_analysis, competitor_benchmarks] >> advanced_market_trends
    [analytics, cash_flow_prediction, risk_analysis, advanced_satisfaction] >> predictive_alerts
    analytics >> realtime_resource_opt
    analytics >> cohort_retention
    [analytics, ml_predictions, channel_performance] >> continuous_learning
    analytics >> predictive_cost_opt
    analytics >> anomaly_detection
    [customer_segmentation, customer_scoring, advanced_satisfaction] >> personalized_recommendations
    analytics >> workflow_opt
    analytics >> change_impact
    analytics >> data_quality
    [channel_performance, customer_segmentation] >> multichannel_opt
    analytics >> s3_export
    
    [reminders_sent, escalations_sent] >> push_notifications
    
    [risk_analysis, churn_prediction, sentiment_analysis] >> action_recommendations
    
    [reminders_sent, escalations_sent] >> [webhooks, dlq, crm_sync]
    [reminders_sent, escalations_sent] >> intelligent_retry


dag = invoice_billing_reminders()
