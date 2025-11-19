"""
Ejemplos de uso del sistema de A/B Testing.

Este archivo muestra cómo integrar A/B testing en diferentes sistemas:
- Emails (subject lines)
- Landing pages
- Precios dinámicos
- CTA buttons
"""
from __future__ import annotations

import json
import logging
from typing import Dict, Any, Optional

from airflow.providers.postgres.hooks.postgres import PostgresHook
from data.airflow.plugins.ab_testing import (
    ABTestingEngine,
    get_email_subject_for_test,
    get_landing_page_config,
    get_pricing_for_test,
    get_cta_button_config,
)

logger = logging.getLogger(__name__)


# ============================================================================
# Ejemplo 1: Integración con Emails (Subject Lines)
# ============================================================================

def send_email_with_ab_test(
    email: str,
    test_id: str,
    default_subject: str,
    body_template: str,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """
    Envía un email usando A/B testing para subject line.
    
    Ejemplo:
        send_email_with_ab_test(
            email="user@example.com",
            test_id="email_subject_welcome_v1",
            default_subject="Welcome to our platform",
            body_template="Hello {{name}}, welcome!"
        )
    """
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    # Obtener subject line para el test
    subject = get_email_subject_for_test(
        ab_engine,
        test_id,
        email,
        default_subject
    )
    
    # Enviar email (integrate con tu sistema de email)
    # email_service.send(email, subject, body_template)
    
    logger.info(f"Email sent with subject: {subject}")
    
    # El evento ya se registró en get_email_subject_for_test
    # Cuando el usuario abra el email, registrar:
    # ab_engine.record_event(test_id, email=email, event_type="email_opened")
    # Cuando haga click, registrar:
    # ab_engine.record_event(test_id, email=email, event_type="email_clicked")
    
    return True


def track_email_engagement(
    test_id: str,
    email: str,
    event_type: str,  # "email_opened" o "email_clicked"
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Rastrea engagement de emails (opens, clicks)."""
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return ab_engine.record_event(
        test_id=test_id,
        email=email,
        event_type=event_type
    )


# ============================================================================
# Ejemplo 2: Integración con Landing Pages
# ============================================================================

def render_landing_page_with_ab_test(
    session_id: str,
    test_id: str,
    default_config: Dict[str, Any],
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Renderiza una landing page con A/B testing.
    
    Ejemplo:
        config = render_landing_page_with_ab_test(
            session_id="sess_123",
            test_id="landing_page_homepage_v1",
            default_config={
                "headline": "Welcome",
                "subheadline": "Get started today",
                "hero_image": "default.jpg",
            }
        )
        # Usar config en tu template
    """
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return get_landing_page_config(
        ab_engine,
        test_id,
        session_id,
        default_config
    )


def track_landing_page_conversion(
    test_id: str,
    session_id: str,
    conversion_type: str = "signup",  # "signup", "purchase", "download", etc.
    revenue: Optional[float] = None,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Rastrea conversiones en landing page."""
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    metrics = {}
    if revenue:
        metrics["revenue"] = revenue
    
    return ab_engine.record_event(
        test_id=test_id,
        session_id=session_id,
        event_type="conversion",
        metrics=metrics
    )


# ============================================================================
# Ejemplo 3: Integración con Precios Dinámicos
# ============================================================================

def get_dynamic_pricing_with_ab_test(
    user_id: str,
    test_id: str,
    default_pricing: Dict[str, float],
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, float]:
    """
    Obtiene precios dinámicos con A/B testing.
    
    Ejemplo:
        pricing = get_dynamic_pricing_with_ab_test(
            user_id="user_123",
            test_id="pricing_strategy_v1",
            default_pricing={
                "basic": 29.99,
                "pro": 79.99,
                "enterprise": 199.99,
            }
        )
    """
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return get_pricing_for_test(
        ab_engine,
        test_id,
        user_id,
        default_pricing
    )


def track_pricing_view(
    test_id: str,
    user_id: str,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Rastrea cuando un usuario ve precios."""
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return ab_engine.record_event(
        test_id=test_id,
        user_id=user_id,
        event_type="page_view"
    )


def track_purchase(
    test_id: str,
    user_id: str,
    revenue: float,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Rastrea una compra."""
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return ab_engine.record_event(
        test_id=test_id,
        user_id=user_id,
        event_type="purchase",
        metrics={"revenue": revenue}
    )


# ============================================================================
# Ejemplo 4: Integración con CTA Buttons
# ============================================================================

def get_cta_button_with_ab_test(
    session_id: str,
    test_id: str,
    default_config: Dict[str, Any],
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Obtiene configuración de CTA button con A/B testing.
    
    Ejemplo:
        cta_config = get_cta_button_with_ab_test(
            session_id="sess_123",
            test_id="cta_button_checkout_v1",
            default_config={
                "text": "Buy Now",
                "color": "#007bff",
                "size": "large",
                "position": "bottom",
            }
        )
    """
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return get_cta_button_config(
        ab_engine,
        test_id,
        session_id,
        default_config
    )


def track_cta_click(
    test_id: str,
    session_id: str,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Rastrea clicks en CTA button."""
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    return ab_engine.record_event(
        test_id=test_id,
        session_id=session_id,
        event_type="cta_clicked"
    )


# ============================================================================
# Ejemplo 5: Crear un Test Completo
# ============================================================================

def create_email_subject_test(
    test_id: str,
    test_name: str,
    variant_a_subject: str,
    variant_b_subject: str,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """
    Crea un test de subject line de email.
    
    Ejemplo:
        create_email_subject_test(
            test_id="email_subject_welcome_v1",
            test_name="Welcome Email Subject Line Test",
            variant_a_subject="Welcome to our platform!",
            variant_b_subject="Start your journey today",
        )
    """
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        # Crear test
        cursor.execute("""
            INSERT INTO ab_tests (
                test_id, test_name, test_type, description, status,
                traffic_split, minimum_sample_size, significance_level,
                primary_metric, auto_deploy_enabled, auto_deploy_when
            ) VALUES (
                %s, %s, 'email_subject', %s, 'draft',
                '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
                1000, 0.95, 'open_rate', true, 'significant_and_lift'
            )
            ON CONFLICT (test_id) DO NOTHING
        """, (test_id, test_name, f"Test: {variant_a_subject} vs {variant_b_subject}"))
        
        # Crear variantes
        cursor.execute("""
            INSERT INTO ab_test_variants (
                test_id, variant_id, variant_name, config, traffic_percentage, is_control
            ) VALUES
            (%s, 'variant_a', 'Control', %s::jsonb, 0.5, true),
            (%s, 'variant_b', 'Treatment', %s::jsonb, 0.5, false)
            ON CONFLICT (test_id, variant_id) DO UPDATE
            SET config = EXCLUDED.config
        """, (
            test_id, json.dumps({"subject_line": variant_a_subject}),
            test_id, json.dumps({"subject_line": variant_b_subject}),
        ))
        
        conn.commit()
        logger.info(f"Created email subject test: {test_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating test: {e}", exc_info=True)
        return False
    finally:
        cursor.close()
        conn.close()


def create_landing_page_test(
    test_id: str,
    test_name: str,
    variant_a_config: Dict[str, Any],
    variant_b_config: Dict[str, Any],
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Crea un test de landing page."""
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO ab_tests (
                test_id, test_name, test_type, description, status,
                traffic_split, minimum_sample_size, significance_level,
                primary_metric, auto_deploy_enabled
            ) VALUES (
                %s, %s, 'landing_page', %s, 'draft',
                '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
                2000, 0.95, 'conversion_rate', true
            )
            ON CONFLICT (test_id) DO NOTHING
        """, (test_id, test_name, f"Landing page test: {test_name}"))
        
        cursor.execute("""
            INSERT INTO ab_test_variants (
                test_id, variant_id, variant_name, config, traffic_percentage, is_control
            ) VALUES
            (%s, 'variant_a', 'Control', %s::jsonb, 0.5, true),
            (%s, 'variant_b', 'Treatment', %s::jsonb, 0.5, false)
            ON CONFLICT (test_id, variant_id) DO UPDATE
            SET config = EXCLUDED.config
        """, (
            test_id, json.dumps(variant_a_config),
            test_id, json.dumps(variant_b_config),
        ))
        
        conn.commit()
        logger.info(f"Created landing page test: {test_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error creating test: {e}", exc_info=True)
        return False
    finally:
        cursor.close()
        conn.close()


def activate_test(
    test_id: str,
    postgres_conn_id: str = "postgres_default"
) -> bool:
    """Activa un test."""
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            UPDATE ab_tests
            SET status = 'active',
                started_at = NOW()
            WHERE test_id = %s
        """, (test_id,))
        
        conn.commit()
        logger.info(f"Activated test: {test_id}")
        return True
        
    except Exception as e:
        conn.rollback()
        logger.error(f"Error activating test: {e}", exc_info=True)
        return False
    finally:
        cursor.close()
        conn.close()


def get_test_results_summary(
    test_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Optional[Dict[str, Any]]:
    """Obtiene un resumen de resultados de un test."""
    ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
    
    # Obtener todas las variantes
    pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    conn = pg_hook.get_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT variant_id
            FROM ab_test_variants
            WHERE test_id = %s
            AND is_active = true
        """, (test_id,))
        
        variant_ids = [row[0] for row in cursor.fetchall()]
        
        # Obtener métricas de cada variante
        variants_metrics = {}
        for variant_id in variant_ids:
            metrics = ab_engine.get_variant_metrics(test_id, variant_id)
            if metrics:
                variants_metrics[variant_id] = {
                    "total_assignments": metrics.total_assignments,
                    "conversions": metrics.conversions,
                    "conversion_rate": metrics.conversion_rate,
                    "revenue_per_user": metrics.revenue_per_user,
                }
        
        # Obtener análisis estadístico más reciente
        cursor.execute("""
            SELECT 
                is_significant, p_value, winner_variant_id,
                winner_lift_percentage, recommendation
            FROM ab_test_statistical_analysis
            WHERE test_id = %s
            ORDER BY analysis_timestamp DESC
            LIMIT 1
        """, (test_id,))
        
        row = cursor.fetchone()
        statistical_analysis = None
        if row:
            statistical_analysis = {
                "is_significant": row[0],
                "p_value": float(row[1]) if row[1] else None,
                "winner_variant_id": row[2],
                "lift_percentage": float(row[3]) if row[3] else None,
                "recommendation": row[4],
            }
        
        return {
            "test_id": test_id,
            "variants_metrics": variants_metrics,
            "statistical_analysis": statistical_analysis,
        }
        
    finally:
        cursor.close()
        conn.close()

