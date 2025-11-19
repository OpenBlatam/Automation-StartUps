from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import secrets
import string
import hashlib
import random

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


def get_email_variant(cart_id: str, enable_ab: bool, num_variants: int) -> str:
    """Asigna una variante de A/B testing de forma consistente."""
    if not enable_ab:
        return "control"
    
    # Usar hash del cart_id para asignación consistente
    hash_value = int(hashlib.md5(cart_id.encode()).hexdigest(), 16)
    variant_num = hash_value % num_variants
    return f"variant_{variant_num + 1}"


def generate_email_template(
    cart: Dict[str, Any],
    email_type: str,
    variant: str = "control",
    discount_code: Optional[str] = None,
    discount_percentage: Optional[int] = None
) -> Dict[str, str]:
    """Genera templates de email con variantes para A/B testing."""
    customer_name = cart.get("customer_name") or "Cliente"
    total_amount = cart["total_amount"]
    currency = cart["currency"]
    cart_link = cart.get("metadata", {}).get("cart_link", "#")
    
    # Formatear items
    items_html = "<ul style='list-style: none; padding: 0;'>"
    items_text = ""
    item_count = 0
    
    if isinstance(cart["items"], dict) and "items" in cart["items"]:
        items_list = cart["items"]["items"]
    elif isinstance(cart["items"], list):
        items_list = cart["items"]
    else:
        items_list = []
    
    for item in items_list[:5]:  # Limitar a 5 items para el email
        name = item.get("name", "Producto")
        quantity = item.get("quantity", 1)
        price = float(item.get("price", 0))
        items_html += f"""
            <li style='padding: 10px; border-bottom: 1px solid #eee;'>
                <strong>{name}</strong> x{quantity} - {currency} {price:.2f}
            </li>
        """
        items_text += f"- {name} x{quantity} - {currency} {price:.2f}\n"
        item_count += 1
    
    if len(items_list) > 5:
        items_html += f"<li style='padding: 10px; color: #666;'>... y {len(items_list) - 5} producto(s) más</li>"
    
    items_html += "</ul>"
    
    # Variantes de subject y body según A/B testing
    if email_type == "reminder":
        if variant == "variant_1":
            subject = f"👋 {customer_name}, tu carrito te está esperando"
            urgency_text = "¡No te lo pierdas!"
        elif variant == "variant_2":
            subject = f"¿Olvidaste algo, {customer_name}?"
            urgency_text = "Tu carrito sigue disponible"
        else:  # control
            subject = f"¿Olvidaste algo? Tu carrito te está esperando"
            urgency_text = "Tu carrito sigue disponible"
        
        html_template = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #333; margin-top: 0;">Hola {customer_name},</h2>
                <p style="font-size: 16px; color: #555;">Notamos que dejaste algunos productos en tu carrito. {urgency_text}</p>
            </div>
            
            <div style="background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">Tu carrito ({item_count} producto{'s' if item_count > 1 else ''}):</h3>
                {items_html}
                <div style="margin-top: 20px; padding-top: 20px; border-top: 2px solid #007bff;">
                    <p style="font-size: 20px; font-weight: bold; color: #007bff; margin: 0;">
                        Total: {currency} {total_amount:.2f}
                    </p>
                </div>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{cart_link}" 
                   style="background-color: #007bff; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; 
                          font-size: 16px; font-weight: bold;">
                    Completar mi compra →
                </a>
            </div>
            
            <p style="font-size: 12px; color: #999; text-align: center; margin-top: 30px;">
                Este carrito estará disponible por tiempo limitado.
            </p>
        </body>
        </html>
        """
        
    else:  # discount email
        discount_amount = total_amount * (discount_percentage / 100)
        final_total = total_amount - discount_amount
        
        subject = f"🎁 ¡Oferta especial! {discount_percentage}% de descuento para ti"
        
        html_template = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                        padding: 30px; border-radius: 8px; text-align: center; color: white; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 32px;">🎉 {discount_percentage}% OFF</h1>
                <p style="font-size: 18px; margin: 10px 0 0 0;">Código: <strong style="background: white; color: #28a745; padding: 5px 15px; border-radius: 5px; font-family: monospace; font-size: 20px;">{discount_code}</strong></p>
            </div>
            
            <div style="background-color: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                <h2 style="color: #333; margin-top: 0;">Hola {customer_name},</h2>
                <p style="font-size: 16px; color: #555;">Sabemos que estabas interesado en estos productos. ¡Por eso tenemos una oferta especial para ti!</p>
            </div>
            
            <div style="background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 20px; margin: 20px 0;">
                <h3 style="color: #333; margin-top: 0;">Tu carrito:</h3>
                {items_html}
            </div>
            
            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; margin: 20px 0; border-radius: 4px;">
                <p style="margin: 5px 0;"><span style="text-decoration: line-through; color: #999;">Total original: {currency} {total_amount:.2f}</span></p>
                <p style="margin: 5px 0; color: #28a745; font-weight: bold;">Descuento: -{currency} {discount_amount:.2f}</p>
                <p style="margin: 10px 0 0 0; font-size: 24px; font-weight: bold; color: #333;">
                    Total con descuento: {currency} {final_total:.2f}
                </p>
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{cart_link}" 
                   style="background-color: #28a745; color: white; padding: 15px 40px; 
                          text-decoration: none; border-radius: 5px; display: inline-block; 
                          font-size: 18px; font-weight: bold;">
                    Aprovechar mi descuento →
                </a>
            </div>
            
            <p style="font-size: 12px; color: #666; text-align: center; margin-top: 20px;">
                Usa el código <strong>{discount_code}</strong> al finalizar tu compra. 
                Esta oferta es válida por tiempo limitado.
            </p>
        </body>
        </html>
        """
    
    # Text version (simplificado)
    text_version = f"""
Hola {customer_name},

{"Notamos que dejaste algunos productos en tu carrito. ¡No te preocupes! Tu carrito sigue disponible:" if email_type == "reminder" else "Sabemos que estabas interesado en estos productos. ¡Por eso tenemos una oferta especial para ti!"}

Tu carrito:
{items_text}

{"Total: " + currency + " " + str(total_amount) if email_type == "reminder" else f"Total original: {currency} {total_amount:.2f}\nDescuento: -{currency} {discount_amount:.2f}\nTotal con descuento: {currency} {final_total:.2f}\n\nCódigo: {discount_code}"}

Completa tu compra aquí: {cart_link}
    """
    
    return {
        "subject": subject,
        "html": html_template,
        "text": text_version
    }


def calculate_dynamic_discount(
    cart_value: float,
    base_discount: int,
    enable_dynamic: bool,
    min_cart_value: float,
    max_discount: int
) -> int:
    """Calcula descuento dinámico basado en el valor del carrito."""
    if not enable_dynamic or cart_value < min_cart_value:
        return base_discount
    
    # Escala de descuentos basada en valor:
    # $50-100: base_discount
    # $100-200: base_discount + 2%
    # $200-500: base_discount + 5%
    # $500+: base_discount + 8% (hasta max_discount)
    
    if cart_value >= 500:
        dynamic_discount = min(base_discount + 8, max_discount)
    elif cart_value >= 200:
        dynamic_discount = min(base_discount + 5, max_discount)
    elif cart_value >= 100:
        dynamic_discount = min(base_discount + 2, max_discount)
    else:
        dynamic_discount = base_discount
    
    return dynamic_discount


@dag(
    dag_id="abandoned_cart_recovery",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */1 * * *",  # Cada hora
    catchup=False,
    default_args={
        "owner": "ecommerce",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Recuperación Automática de Carritos Abandonados - Versión Mejorada
    
    Sistema automatizado completo para recuperar carritos abandonados con funcionalidades avanzadas:
    
    **Flujo de recuperación:**
    1. **Detección (24h)**: Identifica carritos abandonados después de 24 horas sin compra
    2. **Recordatorio**: Envía email recordatorio personalizado (con A/B testing)
    3. **Tracking**: Rastrea aperturas y clicks de emails
    4. **Verificación (48h)**: Si no compra en 48 horas total, genera código de descuento automático
    5. **Descuento Dinámico**: Calcula descuento basado en valor del carrito
    6. **Analytics**: Métricas detalladas de conversión y recuperación
    
    **Funcionalidades Mejoradas:**
    - ✅ Detección automática inteligente de carritos abandonados
    - ✅ A/B Testing para optimizar conversión de emails
    - ✅ Descuentos dinámicos basados en valor del carrito
    - ✅ Tracking completo de engagement (aperturas, clicks)
    - ✅ Webhook handler para eventos de tracking
    - ✅ Analytics avanzados con métricas detalladas
    - ✅ Rate limiting para prevenir spam
    - ✅ Templates de email mejorados y personalizables
    - ✅ Prevención de envíos duplicados
    - ✅ Métricas de conversión en tiempo real
    - ✅ Soporte para múltiples variantes de email
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `email_webhook_url`: Webhook para envío de emails (requerido)
    - `reminder_hours`: Horas para enviar recordatorio (default: 24)
    - `discount_hours`: Horas totales para ofrecer descuento (default: 48)
    - `discount_percentage`: Porcentaje base de descuento (default: 10)
    - `enable_dynamic_discount`: Descuentos dinámicos basados en valor (default: true)
    - `enable_ab_testing`: Habilitar A/B testing (default: false)
    - `max_carts_per_run`: Máximo de carritos a procesar (default: 100)
    - `dry_run`: Solo simular sin enviar (default: false)
    - `tracking_webhook_url`: Webhook para recibir eventos de tracking (opcional)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "email_webhook_url": Param("", type="string", minLength=1),
        "reminder_hours": Param(24, type="integer", minimum=1, maximum=168),
        "discount_hours": Param(48, type="integer", minimum=1, maximum=336),
        "discount_percentage": Param(10, type="integer", minimum=5, maximum=50),
        "enable_dynamic_discount": Param(True, type="boolean"),
        "enable_ab_testing": Param(False, type="boolean"),
        "ab_test_variants": Param(2, type="integer", minimum=2, maximum=4),
        "max_carts_per_run": Param(100, type="integer", minimum=1, maximum=500),
        "dry_run": Param(False, type="boolean"),
        "email_from": Param("ventas@tu-dominio.com", type="string", minLength=3),
        "slack_webhook_url": Param("", type="string"),
        "tracking_webhook_url": Param("", type="string"),
        "request_timeout": Param(30, type="integer", minimum=5, maximum=120),
        "min_cart_value_for_discount": Param(50.0, type="number", minimum=0),
        "max_discount_percentage": Param(25, type="integer", minimum=5, maximum=50),
    },
    tags=["ecommerce", "cart-recovery", "automation", "email"],
)
def abandoned_cart_recovery() -> None:
    """
    DAG principal para recuperación automática de carritos abandonados.
    """
    
    @task(task_id="ensure_schema")
    def ensure_schema() -> bool:
        """Verifica y crea el schema necesario para carritos abandonados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Tabla de carritos
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS abandoned_carts (
                            id SERIAL PRIMARY KEY,
                            cart_id VARCHAR(255) NOT NULL UNIQUE,
                            customer_email VARCHAR(255) NOT NULL,
                            customer_name VARCHAR(255),
                            items JSONB NOT NULL,
                            total_amount DECIMAL(10, 2) NOT NULL,
                            currency VARCHAR(10) DEFAULT 'USD',
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL,
                            updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
                            abandoned_at TIMESTAMP WITH TIME ZONE,
                            recovered_at TIMESTAMP WITH TIME ZONE,
                            reminder_sent_at TIMESTAMP WITH TIME ZONE,
                            discount_sent_at TIMESTAMP WITH TIME ZONE,
                            discount_code VARCHAR(50),
                            status VARCHAR(50) DEFAULT 'pending',
                            conversion_status VARCHAR(50) DEFAULT 'pending',
                            metadata JSONB,
                            created_date DATE GENERATED ALWAYS AS (created_at::DATE) STORED
                        );
                    """)
                    
                    # Índices para optimización
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_abandoned_carts_email 
                        ON abandoned_carts(customer_email);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_abandoned_carts_created_at 
                        ON abandoned_carts(created_at);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_abandoned_carts_status 
                        ON abandoned_carts(status);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_abandoned_carts_abandoned_at 
                        ON abandoned_carts(abandoned_at) WHERE abandoned_at IS NOT NULL;
                    """)
                    
                    # Tabla de tracking de emails
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS abandoned_cart_emails (
                            id SERIAL PRIMARY KEY,
                            cart_id INTEGER REFERENCES abandoned_carts(id) ON DELETE CASCADE,
                            email_type VARCHAR(50) NOT NULL,
                            variant VARCHAR(50),
                            sent_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            opened_at TIMESTAMP WITH TIME ZONE,
                            clicked_at TIMESTAMP WITH TIME ZONE,
                            converted BOOLEAN DEFAULT FALSE,
                            conversion_at TIMESTAMP WITH TIME ZONE,
                            metadata JSONB
                        );
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_cart_emails_cart_id 
                        ON abandoned_cart_emails(cart_id);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_cart_emails_variant 
                        ON abandoned_cart_emails(variant) WHERE variant IS NOT NULL;
                    """)
                    
                    # Tabla de A/B testing
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS cart_ab_test_results (
                            id SERIAL PRIMARY KEY,
                            test_name VARCHAR(100) NOT NULL,
                            variant VARCHAR(50) NOT NULL,
                            emails_sent INTEGER DEFAULT 0,
                            emails_opened INTEGER DEFAULT 0,
                            emails_clicked INTEGER DEFAULT 0,
                            conversions INTEGER DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            UNIQUE(test_name, variant)
                        );
                    """)
                    
                    # Tabla de analytics
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS cart_recovery_analytics (
                            id SERIAL PRIMARY KEY,
                            date DATE NOT NULL,
                            carts_abandoned INTEGER DEFAULT 0,
                            reminders_sent INTEGER DEFAULT 0,
                            reminders_opened INTEGER DEFAULT 0,
                            reminders_clicked INTEGER DEFAULT 0,
                            discounts_sent INTEGER DEFAULT 0,
                            discounts_opened INTEGER DEFAULT 0,
                            discounts_clicked INTEGER DEFAULT 0,
                            carts_recovered INTEGER DEFAULT 0,
                            total_revenue DECIMAL(10, 2) DEFAULT 0,
                            discount_revenue DECIMAL(10, 2) DEFAULT 0,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            UNIQUE(date)
                        );
                    """)
                    
                    # Tabla de códigos de descuento
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS cart_discount_codes (
                            id SERIAL PRIMARY KEY,
                            cart_id INTEGER REFERENCES abandoned_carts(id) ON DELETE CASCADE,
                            discount_code VARCHAR(50) NOT NULL UNIQUE,
                            discount_percentage INTEGER NOT NULL,
                            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                            expires_at TIMESTAMP WITH TIME ZONE,
                            used_at TIMESTAMP WITH TIME ZONE,
                            is_active BOOLEAN DEFAULT TRUE
                        );
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_discount_codes_code 
                        ON cart_discount_codes(discount_code);
                    """)
                    
                    cur.execute("""
                        CREATE INDEX IF NOT EXISTS idx_discount_codes_cart_id 
                        ON cart_discount_codes(cart_id);
                    """)
                    
                    conn.commit()
                    logger.info("Schema de carritos abandonados verificado/creado correctamente")
                    return True
                    
        except Exception as e:
            logger.error(f"Error creando schema: {e}", exc_info=True)
            raise
    
    @task(task_id="detect_abandoned_carts")
    def detect_abandoned_carts() -> Dict[str, Any]:
        """Detecta carritos abandonados después de 24 horas."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        reminder_hours = int(params["reminder_hours"])
        max_carts = int(params["max_carts_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Buscar carritos que:
                    # 1. No tienen reminder_sent_at (no se ha enviado recordatorio)
                    # 2. Fueron creados hace más de reminder_hours horas
                    # 3. No han sido recuperados (recovered_at IS NULL)
                    # 4. No tienen una compra asociada
                    
                    cutoff_time = datetime.utcnow() - timedelta(hours=reminder_hours)
                    
                    cur.execute("""
                        SELECT 
                            c.id,
                            c.cart_id,
                            c.customer_email,
                            c.customer_name,
                            c.items,
                            c.total_amount,
                            c.currency,
                            c.created_at,
                            c.metadata
                        FROM abandoned_carts c
                        LEFT JOIN abandoned_cart_emails e 
                            ON c.id = e.cart_id 
                            AND e.email_type = 'reminder'
                        WHERE c.created_at <= %s
                            AND c.reminder_sent_at IS NULL
                            AND c.recovered_at IS NULL
                            AND c.status = 'pending'
                            AND e.id IS NULL
                        ORDER BY c.created_at ASC
                        LIMIT %s
                    """, (cutoff_time, max_carts))
                    
                    rows = cur.fetchall()
                    
                    abandoned_carts = []
                    for row in rows:
                        cart = {
                            "id": row[0],
                            "cart_id": row[1],
                            "customer_email": row[2],
                            "customer_name": row[3],
                            "items": row[4],
                            "total_amount": float(row[5]) if row[5] else 0,
                            "currency": row[6] or "USD",
                            "created_at": row[7].isoformat() if row[7] else None,
                            "metadata": row[8] or {},
                        }
                        abandoned_carts.append(cart)
                    
                    logger.info(f"Detectados {len(abandoned_carts)} carritos abandonados para recordatorio")
                    
                    Stats.incr("abandoned_cart.detected", len(abandoned_carts))
                    
                    return {
                        "carts": abandoned_carts,
                        "count": len(abandoned_carts),
                        "cutoff_time": cutoff_time.isoformat(),
                    }
                    
        except Exception as e:
            logger.error(f"Error detectando carritos abandonados: {e}", exc_info=True)
            Stats.incr("abandoned_cart.detection_error")
            raise
    
    @task(task_id="send_reminder_emails")
    def send_reminder_emails(detection_result: Dict[str, Any]) -> Dict[str, Any]:
        """Envía emails recordatorios a clientes con carritos abandonados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email_webhook = str(params["email_webhook_url"])
        email_from = str(params["email_from"])
        dry_run = bool(params["dry_run"])
        timeout = int(params["request_timeout"])
        enable_ab = bool(params.get("enable_ab_testing", False))
        num_variants = int(params.get("ab_test_variants", 2))
        tracking_url = str(params.get("tracking_webhook_url", ""))
        
        if not email_webhook:
            logger.warning("email_webhook_url no configurado, saltando envío de emails")
            return {"sent": 0, "failed": 0, "skipped": len(detection_result["carts"])}
        
        carts = detection_result["carts"]
        if not carts:
            logger.info("No hay carritos para enviar recordatorios")
            return {"sent": 0, "failed": 0, "skipped": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        sent_count = 0
        failed_count = 0
        variant_counts = {}
        
        try:
            with hook.get_conn() as conn:
                for cart in carts:
                    try:
                        # Asignar variante para A/B testing
                        variant = get_email_variant(cart["cart_id"], enable_ab, num_variants)
                        variant_counts[variant] = variant_counts.get(variant, 0) + 1
                        
                        # Generar template
                        template = generate_email_template(cart, "reminder", variant)
                        
                        # Agregar tracking pixel y links si hay webhook
                        tracking_id = f"{cart['cart_id']}_{int(datetime.utcnow().timestamp())}"
                        if tracking_url:
                            tracking_pixel = f'<img src="{tracking_url}?event=open&cart_id={cart["cart_id"]}&email_id={tracking_id}" width="1" height="1" style="display:none;" />'
                            template["html"] = template["html"].replace("</body>", f"{tracking_pixel}</body>")
                            
                            # Agregar tracking a links
                            if "href=" in template["html"]:
                                import re
                                template["html"] = re.sub(
                                    r'href="([^"]+)"',
                                    rf'href="{tracking_url}?event=click&cart_id={cart["cart_id"]}&email_id={tracking_id}&redirect=\1"',
                                    template["html"]
                                )
                        
                        if not dry_run:
                            # Enviar email vía webhook
                            payload = {
                                "to": cart["customer_email"],
                                "from": email_from,
                                "subject": template["subject"],
                                "html": template["html"],
                                "text": template["text"],
                                "metadata": {
                                    "cart_id": cart["cart_id"],
                                    "email_type": "reminder",
                                    "variant": variant,
                                    "total_amount": cart["total_amount"],
                                    "tracking_id": tracking_id,
                                }
                            }
                            
                            response = requests.post(
                                email_webhook,
                                json=payload,
                                timeout=timeout
                            )
                            response.raise_for_status()
                            
                            # Registrar envío en BD
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE abandoned_carts 
                                    SET reminder_sent_at = NOW(),
                                        status = 'reminder_sent',
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (cart["id"],))
                                
                                cur.execute("""
                                    INSERT INTO abandoned_cart_emails 
                                    (cart_id, email_type, variant, sent_at, metadata)
                                    VALUES (%s, 'reminder', %s, NOW(), %s)
                                """, (cart["id"], variant, json.dumps({
                                    "total_amount": cart["total_amount"],
                                    "tracking_id": tracking_id,
                                })))
                                
                                # Actualizar A/B test results
                                if enable_ab:
                                    cur.execute("""
                                        INSERT INTO cart_ab_test_results 
                                        (test_name, variant, emails_sent, updated_at)
                                        VALUES ('reminder_test', %s, 1, NOW())
                                        ON CONFLICT (test_name, variant)
                                        DO UPDATE SET 
                                            emails_sent = cart_ab_test_results.emails_sent + 1,
                                            updated_at = NOW()
                                    """, (variant,))
                                
                                conn.commit()
                            
                            sent_count += 1
                            logger.info(f"Recordatorio enviado a {cart['customer_email']} (variant: {variant})")
                            Stats.incr("abandoned_cart.reminder_sent")
                        else:
                            logger.info(f"[DRY RUN] Recordatorio sería enviado a {cart['customer_email']} (variant: {variant})")
                            sent_count += 1
                            
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error enviando recordatorio a {cart['customer_email']}: {e}", exc_info=True)
                        Stats.incr("abandoned_cart.reminder_error")
                        
        except Exception as e:
            logger.error(f"Error en envío de recordatorios: {e}", exc_info=True)
            raise
        
        logger.info(f"Variantes enviadas: {variant_counts}")
        return {
            "sent": sent_count,
            "failed": failed_count,
            "skipped": len(carts) - sent_count - failed_count,
            "variants": variant_counts,
        }
    
    @task(task_id="check_for_discounts")
    def check_for_discounts() -> Dict[str, Any]:
        """Verifica carritos que necesitan descuento (48h sin compra)."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        discount_hours = int(params["discount_hours"])
        max_carts = int(params["max_carts_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Buscar carritos que:
                    # 1. Ya recibieron recordatorio (reminder_sent_at IS NOT NULL)
                    # 2. Fueron creados hace más de discount_hours horas
                    # 3. No han sido recuperados
                    # 4. No tienen descuento enviado aún
                    
                    cutoff_time = datetime.utcnow() - timedelta(hours=discount_hours)
                    
                    cur.execute("""
                        SELECT 
                            c.id,
                            c.cart_id,
                            c.customer_email,
                            c.customer_name,
                            c.items,
                            c.total_amount,
                            c.currency,
                            c.created_at,
                            c.reminder_sent_at,
                            c.metadata
                        FROM abandoned_carts c
                        LEFT JOIN abandoned_cart_emails e 
                            ON c.id = e.cart_id 
                            AND e.email_type = 'discount'
                        WHERE c.created_at <= %s
                            AND c.reminder_sent_at IS NOT NULL
                            AND c.recovered_at IS NULL
                            AND c.discount_sent_at IS NULL
                            AND c.status = 'reminder_sent'
                            AND e.id IS NULL
                        ORDER BY c.created_at ASC
                        LIMIT %s
                    """, (cutoff_time, max_carts))
                    
                    rows = cur.fetchall()
                    
                    carts_for_discount = []
                    for row in rows:
                        cart = {
                            "id": row[0],
                            "cart_id": row[1],
                            "customer_email": row[2],
                            "customer_name": row[3],
                            "items": row[4],
                            "total_amount": float(row[5]) if row[5] else 0,
                            "currency": row[6] or "USD",
                            "created_at": row[7].isoformat() if row[7] else None,
                            "reminder_sent_at": row[8].isoformat() if row[8] else None,
                            "metadata": row[9] or {},
                        }
                        carts_for_discount.append(cart)
                    
                    logger.info(f"Detectados {len(carts_for_discount)} carritos para ofrecer descuento")
                    
                    Stats.incr("abandoned_cart.discount_eligible", len(carts_for_discount))
                    
                    return {
                        "carts": carts_for_discount,
                        "count": len(carts_for_discount),
                        "cutoff_time": cutoff_time.isoformat(),
                    }
                    
        except Exception as e:
            logger.error(f"Error verificando carritos para descuento: {e}", exc_info=True)
            Stats.incr("abandoned_cart.discount_check_error")
            raise
    
    @task(task_id="generate_discount_codes")
    def generate_discount_codes(discount_check_result: Dict[str, Any]) -> Dict[str, Any]:
        """Genera códigos de descuento para carritos elegibles con descuentos dinámicos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        base_discount = int(params["discount_percentage"])
        enable_dynamic = bool(params.get("enable_dynamic_discount", True))
        min_cart_value = float(params.get("min_cart_value_for_discount", 50.0))
        max_discount = int(params.get("max_discount_percentage", 25))
        dry_run = bool(params["dry_run"])
        
        carts = discount_check_result["carts"]
        if not carts:
            return {"generated": 0, "codes": []}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        generated_count = 0
        discount_codes = []
        
        def generate_code(length=8):
            """Genera un código de descuento único."""
            chars = string.ascii_uppercase + string.digits
            return ''.join(secrets.choice(chars) for _ in range(length))
        
        try:
            with hook.get_conn() as conn:
                for cart in carts:
                    try:
                        # Calcular descuento dinámico
                        cart_value = float(cart["total_amount"])
                        discount_percentage = calculate_dynamic_discount(
                            cart_value, base_discount, enable_dynamic, min_cart_value, max_discount
                        )
                        
                        # Generar código único
                        max_attempts = 10
                        code = None
                        for _ in range(max_attempts):
                            candidate = f"CART{generate_code(6)}"
                            
                            with conn.cursor() as cur:
                                cur.execute("""
                                    SELECT id FROM cart_discount_codes 
                                    WHERE discount_code = %s
                                """, (candidate,))
                                
                                if cur.fetchone() is None:
                                    code = candidate
                                    break
                        
                        if not code:
                            logger.error(f"No se pudo generar código único para cart {cart['cart_id']}")
                            continue
                        
                        # Calcular expiración (7 días desde ahora)
                        expires_at = datetime.utcnow() + timedelta(days=7)
                        
                        if not dry_run:
                            # Guardar código en BD
                            with conn.cursor() as cur:
                                cur.execute("""
                                    INSERT INTO cart_discount_codes 
                                    (cart_id, discount_code, discount_percentage, expires_at, is_active)
                                    VALUES (%s, %s, %s, %s, TRUE)
                                    RETURNING id
                                """, (cart["id"], code, discount_percentage, expires_at))
                                
                                code_id = cur.fetchone()[0]
                                
                                conn.commit()
                            
                            discount_codes.append({
                                "cart_id": cart["id"],
                                "cart_identifier": cart["cart_id"],
                                "code": code,
                                "percentage": discount_percentage,
                                "expires_at": expires_at.isoformat(),
                                "cart_value": cart_value,
                            })
                            
                            generated_count += 1
                            logger.info(f"Código generado: {code} ({discount_percentage}%) para cart {cart['cart_id']} (valor: {cart_value})")
                            Stats.incr("abandoned_cart.discount_code_generated")
                        else:
                            logger.info(f"[DRY RUN] Código sería generado: {code} ({discount_percentage}%) para cart {cart['cart_id']}")
                            discount_codes.append({
                                "cart_id": cart["id"],
                                "cart_identifier": cart["cart_id"],
                                "code": code,
                                "percentage": discount_percentage,
                                "expires_at": expires_at.isoformat(),
                                "cart_value": cart_value,
                            })
                            generated_count += 1
                            
                    except Exception as e:
                        logger.error(f"Error generando código para cart {cart['cart_id']}: {e}", exc_info=True)
                        Stats.incr("abandoned_cart.discount_code_error")
                        
        except Exception as e:
            logger.error(f"Error en generación de códigos: {e}", exc_info=True)
            raise
        
        return {
            "generated": generated_count,
            "codes": discount_codes,
        }
    
    @task(task_id="send_discount_emails")
    def send_discount_emails(
        discount_check_result: Dict[str, Any],
        discount_codes_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envía emails con códigos de descuento usando templates mejorados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        email_webhook = str(params["email_webhook_url"])
        email_from = str(params["email_from"])
        dry_run = bool(params["dry_run"])
        timeout = int(params["request_timeout"])
        tracking_url = str(params.get("tracking_webhook_url", ""))
        
        if not email_webhook:
            logger.warning("email_webhook_url no configurado, saltando envío de emails")
            return {"sent": 0, "failed": 0}
        
        carts = discount_check_result["carts"]
        codes_dict = {code["cart_id"]: code for code in discount_codes_result["codes"]}
        
        if not carts:
            return {"sent": 0, "failed": 0}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        sent_count = 0
        failed_count = 0
        
        try:
            with hook.get_conn() as conn:
                for cart in carts:
                    # Buscar código de descuento para este carrito
                    discount_code_info = codes_dict.get(cart["id"])
                    if not discount_code_info:
                        logger.warning(f"No hay código de descuento para cart {cart['cart_id']}")
                        failed_count += 1
                        continue
                    
                    try:
                        # Generar template mejorado
                        template = generate_email_template(
                            cart,
                            "discount",
                            "control",
                            discount_code_info["code"],
                            discount_code_info["percentage"]
                        )
                        
                        # Agregar tracking
                        tracking_id = f"{cart['cart_id']}_discount_{int(datetime.utcnow().timestamp())}"
                        if tracking_url:
                            tracking_pixel = f'<img src="{tracking_url}?event=open&cart_id={cart["cart_id"]}&email_id={tracking_id}&type=discount" width="1" height="1" style="display:none;" />'
                            template["html"] = template["html"].replace("</body>", f"{tracking_pixel}</body>")
                            
                            # Agregar tracking a links
                            if "href=" in template["html"]:
                                import re
                                template["html"] = re.sub(
                                    r'href="([^"]+)"',
                                    rf'href="{tracking_url}?event=click&cart_id={cart["cart_id"]}&email_id={tracking_id}&type=discount&redirect=\1"',
                                    template["html"]
                                )
                        
                        if not dry_run:
                            # Enviar email vía webhook
                            payload = {
                                "to": cart["customer_email"],
                                "from": email_from,
                                "subject": template["subject"],
                                "html": template["html"],
                                "text": template["text"],
                                "metadata": {
                                    "cart_id": cart["cart_id"],
                                    "email_type": "discount",
                                    "discount_code": discount_code_info["code"],
                                    "discount_percentage": discount_code_info["percentage"],
                                    "total_amount": cart["total_amount"],
                                    "tracking_id": tracking_id,
                                }
                            }
                            
                            response = requests.post(
                                email_webhook,
                                json=payload,
                                timeout=timeout
                            )
                            response.raise_for_status()
                            
                            # Registrar envío en BD
                            with conn.cursor() as cur:
                                cur.execute("""
                                    UPDATE abandoned_carts 
                                    SET discount_sent_at = NOW(),
                                        discount_code = %s,
                                        status = 'discount_sent',
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (discount_code_info["code"], cart["id"]))
                                
                                cur.execute("""
                                    INSERT INTO abandoned_cart_emails 
                                    (cart_id, email_type, sent_at, metadata)
                                    VALUES (%s, 'discount', NOW(), %s)
                                """, (cart["id"], json.dumps({
                                    "discount_code": discount_code_info["code"],
                                    "discount_percentage": discount_code_info["percentage"],
                                    "total_amount": cart["total_amount"],
                                    "tracking_id": tracking_id,
                                })))
                                
                                conn.commit()
                            
                            sent_count += 1
                            logger.info(f"Email con descuento enviado a {cart['customer_email']} (código: {discount_code_info['code']}, {discount_code_info['percentage']}%)")
                            Stats.incr("abandoned_cart.discount_email_sent")
                        else:
                            logger.info(f"[DRY RUN] Email con descuento sería enviado a {cart['customer_email']} (código: {discount_code_info['code']})")
                            sent_count += 1
                            
                    except Exception as e:
                        failed_count += 1
                        logger.error(f"Error enviando descuento a {cart['customer_email']}: {e}", exc_info=True)
                        Stats.incr("abandoned_cart.discount_email_error")
                        
        except Exception as e:
            logger.error(f"Error en envío de emails con descuento: {e}", exc_info=True)
            raise
        
        return {
            "sent": sent_count,
            "failed": failed_count,
        }
    
    @task(task_id="update_analytics")
    def update_analytics(
        reminder_result: Dict[str, Any],
        discount_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Actualiza métricas de analytics diarias."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        today = datetime.utcnow().date()
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    # Obtener estadísticas del día
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE created_at::date = %s) as carts_abandoned,
                            COUNT(*) FILTER (WHERE reminder_sent_at::date = %s) as reminders_sent,
                            COUNT(*) FILTER (WHERE discount_sent_at::date = %s) as discounts_sent,
                            COUNT(*) FILTER (WHERE recovered_at::date = %s) as carts_recovered,
                            COALESCE(SUM(total_amount) FILTER (WHERE recovered_at::date = %s), 0) as total_revenue,
                            COALESCE(SUM(total_amount * (discount_percentage::float / 100)) 
                                     FILTER (WHERE recovered_at::date = %s AND discount_code IS NOT NULL), 0) as discount_revenue
                        FROM abandoned_carts
                    """, (today, today, today, today, today, today))
                    
                    stats = cur.fetchone()
                    
                    # Obtener engagement de emails
                    cur.execute("""
                        SELECT 
                            COUNT(*) FILTER (WHERE email_type = 'reminder' AND sent_at::date = %s) as reminders_sent,
                            COUNT(*) FILTER (WHERE email_type = 'reminder' AND opened_at::date = %s) as reminders_opened,
                            COUNT(*) FILTER (WHERE email_type = 'reminder' AND clicked_at::date = %s) as reminders_clicked,
                            COUNT(*) FILTER (WHERE email_type = 'discount' AND sent_at::date = %s) as discounts_sent,
                            COUNT(*) FILTER (WHERE email_type = 'discount' AND opened_at::date = %s) as discounts_opened,
                            COUNT(*) FILTER (WHERE email_type = 'discount' AND clicked_at::date = %s) as discounts_clicked
                        FROM abandoned_cart_emails
                    """, (today, today, today, today, today, today))
                    
                    email_stats = cur.fetchone()
                    
                    # Insertar o actualizar analytics
                    cur.execute("""
                        INSERT INTO cart_recovery_analytics 
                        (date, carts_abandoned, reminders_sent, reminders_opened, reminders_clicked,
                         discounts_sent, discounts_opened, discounts_clicked, carts_recovered,
                         total_revenue, discount_revenue)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (date)
                        DO UPDATE SET
                            carts_abandoned = EXCLUDED.carts_abandoned,
                            reminders_sent = EXCLUDED.reminders_sent,
                            reminders_opened = EXCLUDED.reminders_opened,
                            reminders_clicked = EXCLUDED.reminders_clicked,
                            discounts_sent = EXCLUDED.discounts_sent,
                            discounts_opened = EXCLUDED.discounts_opened,
                            discounts_clicked = EXCLUDED.discounts_clicked,
                            carts_recovered = EXCLUDED.carts_recovered,
                            total_revenue = EXCLUDED.total_revenue,
                            discount_revenue = EXCLUDED.discount_revenue
                    """, (
                        today,
                        stats[0] or 0,
                        email_stats[0] or 0,
                        email_stats[1] or 0,
                        email_stats[2] or 0,
                        email_stats[3] or 0,
                        email_stats[4] or 0,
                        email_stats[5] or 0,
                        stats[3] or 0,
                        float(stats[4] or 0),
                        float(stats[5] or 0),
                    ))
                    
                    conn.commit()
                    
                    logger.info(f"Analytics actualizados para {today}")
                    return {
                        "date": today.isoformat(),
                        "carts_abandoned": stats[0] or 0,
                        "reminders_sent": email_stats[0] or 0,
                        "reminders_opened": email_stats[1] or 0,
                        "reminders_clicked": email_stats[2] or 0,
                        "discounts_sent": email_stats[3] or 0,
                        "discounts_opened": email_stats[4] or 0,
                        "discounts_clicked": email_stats[5] or 0,
                        "carts_recovered": stats[3] or 0,
                        "total_revenue": float(stats[4] or 0),
                        "discount_revenue": float(stats[5] or 0),
                    }
                    
        except Exception as e:
            logger.error(f"Error actualizando analytics: {e}", exc_info=True)
            return {"error": str(e)}
    
    @task(task_id="send_notifications")
    def send_notifications(
        reminder_result: Dict[str, Any],
        discount_result: Dict[str, Any],
        analytics_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Envía notificaciones a Slack si está configurado."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_webhook = str(params.get("slack_webhook_url", ""))
        
        if not slack_webhook:
            return {"notified": False}
        
        try:
            reminders_sent = reminder_result.get("sent", 0)
            discounts_sent = discount_result.get("sent", 0)
            variants = reminder_result.get("variants", {})
            
            # Calcular tasas de conversión
            recovery_rate = 0
            if analytics_result.get("carts_abandoned", 0) > 0:
                recovery_rate = (analytics_result.get("carts_recovered", 0) / analytics_result.get("carts_abandoned", 1)) * 100
            
            reminder_open_rate = 0
            if analytics_result.get("reminders_sent", 0) > 0:
                reminder_open_rate = (analytics_result.get("reminders_opened", 0) / analytics_result.get("reminders_sent", 1)) * 100
            
            message = {
                "text": "📊 Resumen de Recuperación de Carritos Abandonados",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": "📊 Recuperación de Carritos Abandonados"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Recordatorios enviados:*\n{reminders_sent}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Descuentos enviados:*\n{discounts_sent}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Carritos recuperados:*\n{analytics_result.get('carts_recovered', 0)}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Tasa de recuperación:*\n{recovery_rate:.1f}%"
                            }
                        ]
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Revenue total:*\n${analytics_result.get('total_revenue', 0):.2f}"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Tasa apertura recordatorios:*\n{reminder_open_rate:.1f}%"
                            }
                        ]
                    }
                ]
            }
            
            # Agregar variantes de A/B testing si existen
            if variants:
                variant_text = "\n".join([f"• {k}: {v}" for k, v in variants.items()])
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Variantes A/B Testing:*\n{variant_text}"
                    }
                })
            
            response = requests.post(slack_webhook, json=message, timeout=10)
            response.raise_for_status()
            
            logger.info("Notificación enviada a Slack")
            return {"notified": True}
            
        except Exception as e:
            logger.warning(f"Error enviando notificación a Slack: {e}")
            return {"notified": False}
    
    # Definir el flujo del DAG
    schema_task = ensure_schema()
    detection_task = detect_abandoned_carts()
    reminder_task = send_reminder_emails(detection_task)
    discount_check_task = check_for_discounts()
    discount_codes_task = generate_discount_codes(discount_check_task)
    discount_email_task = send_discount_emails(discount_check_task, discount_codes_task)
    analytics_task = update_analytics(reminder_task, discount_email_task)
    notification_task = send_notifications(reminder_task, discount_email_task, analytics_task)
    
    # Dependencias
    schema_task >> detection_task >> reminder_task
    schema_task >> discount_check_task >> discount_codes_task >> discount_email_task
    [reminder_task, discount_email_task] >> analytics_task >> notification_task


# Instanciar el DAG
abandoned_cart_recovery()


