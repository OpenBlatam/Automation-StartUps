"""
Sistema de A/B Testing Automatizado con Análisis Estadístico Avanzado.

Características:
- Tests de subject lines en emails
- Variaciones de landing pages
- Precios dinámicos
- CTA buttons
- Análisis estadístico robusto (z-test, chi-square, confidence intervals)
- Auto-deployment de versión ganadora
- Power analysis y cálculo de sample size
- Detección de significancia estadística
"""
from __future__ import annotations

import logging
import hashlib
import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from decimal import Decimal
import math

from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.exceptions import AirflowFailException

logger = logging.getLogger(__name__)

# Constantes para tests estadísticos
Z_SCORE_95 = 1.96  # 95% confidence level
Z_SCORE_99 = 2.58  # 99% confidence level
MIN_SAMPLE_SIZE = 100  # Mínimo tamaño de muestra para análisis válido


@dataclass
class VariantMetrics:
    """Métricas de una variante."""
    variant_id: str
    total_assignments: int
    conversions: int
    revenue: float
    conversion_rate: float
    revenue_per_user: float
    # Métricas específicas por tipo
    email_sent: int = 0
    email_opened: int = 0
    email_clicked: int = 0
    page_views: int = 0
    cta_clicks: int = 0


@dataclass
class StatisticalResult:
    """Resultado de análisis estadístico."""
    is_significant: bool
    p_value: float
    confidence_level: float
    z_score: float
    confidence_interval_lower: float
    confidence_interval_upper: float
    lift_percentage: float
    winner_variant_id: Optional[str]
    recommendation: str  # 'deploy', 'continue', 'pause', 'extend'
    recommendation_reason: str


class ABTestingEngine:
    """Motor de A/B Testing con análisis estadístico avanzado."""
    
    def __init__(self, postgres_conn_id: str = "postgres_default"):
        """
        Inicializa el motor de A/B testing.
        
        Args:
            postgres_conn_id: Connection ID de PostgreSQL
        """
        self.postgres_conn_id = postgres_conn_id
        self._pg_hook: Optional[PostgresHook] = None
    
    @property
    def pg_hook(self) -> PostgresHook:
        """Obtiene el hook de PostgreSQL (lazy loading)."""
        if self._pg_hook is None:
            self._pg_hook = PostgresHook(postgres_conn_id=self.postgres_conn_id)
        return self._pg_hook
    
    def assign_variant(
        self,
        test_id: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        session_id: Optional[str] = None
    ) -> Optional[str]:
        """
        Asigna una variante a un usuario de forma determinística.
        
        Args:
            test_id: ID del test
            user_id: ID del usuario
            email: Email del usuario
            session_id: ID de sesión
            
        Returns:
            ID de la variante asignada o None
        """
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT assign_ab_variant(%s, %s, %s, %s)
            """, (test_id, user_id, email, session_id))
            
            result = cursor.fetchone()
            variant_id = result[0] if result else None
            
            cursor.close()
            conn.close()
            
            return variant_id
            
        except Exception as e:
            logger.error(f"Error assigning variant for test {test_id}: {e}", exc_info=True)
            return None
    
    def record_event(
        self,
        test_id: str,
        user_id: Optional[str] = None,
        email: Optional[str] = None,
        session_id: Optional[str] = None,
        event_type: str = "conversion",
        metrics: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Registra un evento para tracking.
        
        Args:
            test_id: ID del test
            user_id: ID del usuario
            email: Email del usuario
            session_id: ID de sesión
            event_type: Tipo de evento (email_sent, email_opened, email_clicked, 
                       page_view, cta_clicked, conversion, purchase, etc.)
            metrics: Métricas adicionales (revenue, duration, etc.)
            
        Returns:
            True si se registró exitosamente
        """
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            metrics_json = json.dumps(metrics or {})
            
            cursor.execute("""
                SELECT record_ab_event(%s, %s, %s, %s, %s, %s::jsonb)
            """, (test_id, user_id, email, session_id, event_type, metrics_json))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error recording event for test {test_id}: {e}", exc_info=True)
            return False
    
    def get_test_config(self, test_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene la configuración de un test."""
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    test_id, test_name, test_type, description, status,
                    traffic_split, minimum_sample_size, significance_level,
                    minimum_lift_percentage, primary_metric, auto_deploy_enabled,
                    auto_deploy_when
                FROM ab_tests
                WHERE test_id = %s
            """, (test_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            config = {
                "test_id": row[0],
                "test_name": row[1],
                "test_type": row[2],
                "description": row[3],
                "status": row[4],
                "traffic_split": row[5],
                "minimum_sample_size": row[6],
                "significance_level": float(row[7]) if row[7] else 0.95,
                "minimum_lift_percentage": float(row[8]) if row[8] else 5.0,
                "primary_metric": row[9],
                "auto_deploy_enabled": row[10],
                "auto_deploy_when": row[11],
            }
            
            cursor.close()
            conn.close()
            
            return config
            
        except Exception as e:
            logger.error(f"Error getting test config for {test_id}: {e}", exc_info=True)
            return None
    
    def get_variant_metrics(
        self,
        test_id: str,
        variant_id: str,
        days: int = 7
    ) -> Optional[VariantMetrics]:
        """Obtiene métricas agregadas de una variante."""
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            # Calcular resultados agregados
            cursor.execute("""
                SELECT calculate_ab_test_results(%s, CURRENT_DATE, %s)
            """, (test_id, days * 24))
            
            # Obtener métricas de la variante
            cursor.execute("""
                SELECT 
                    total_assignments,
                    conversions,
                    revenue,
                    conversion_rate,
                    revenue_per_user,
                    email_sent_count,
                    email_opened_count,
                    email_clicked_count,
                    page_views,
                    cta_clicks
                FROM ab_test_results
                WHERE test_id = %s
                AND variant_id = %s
                AND analysis_date = CURRENT_DATE
                ORDER BY calculated_at DESC
                LIMIT 1
            """, (test_id, variant_id))
            
            row = cursor.fetchone()
            if not row:
                # Si no hay resultados agregados, calcular desde eventos
                return self._calculate_variant_metrics_from_events(test_id, variant_id, days)
            
            metrics = VariantMetrics(
                variant_id=variant_id,
                total_assignments=row[0] or 0,
                conversions=row[5] or 0,  # conversions
                revenue=float(row[2] or 0),
                conversion_rate=float(row[3] or 0),
                revenue_per_user=float(row[4] or 0),
                email_sent=row[5] or 0,
                email_opened=row[6] or 0,
                email_clicked=row[7] or 0,
                page_views=row[8] or 0,
                cta_clicks=row[9] or 0,
            )
            
            cursor.close()
            conn.close()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error getting variant metrics: {e}", exc_info=True)
            return None
    
    def _calculate_variant_metrics_from_events(
        self,
        test_id: str,
        variant_id: str,
        days: int
    ) -> Optional[VariantMetrics]:
        """Calcula métricas desde eventos si no hay resultados agregados."""
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT a.id) as total_assignments,
                    COUNT(e.id) FILTER (WHERE e.event_type IN ('conversion', 'purchase', 'signup')) as conversions,
                    COALESCE(SUM((e.metrics->>'revenue')::NUMERIC), 0) as revenue,
                    COUNT(e.id) FILTER (WHERE e.event_type = 'email_sent') as email_sent,
                    COUNT(e.id) FILTER (WHERE e.event_type = 'email_opened') as email_opened,
                    COUNT(e.id) FILTER (WHERE e.event_type = 'email_clicked') as email_clicked,
                    COUNT(e.id) FILTER (WHERE e.event_type = 'page_view') as page_views,
                    COUNT(e.id) FILTER (WHERE e.event_type = 'cta_clicked') as cta_clicks
                FROM ab_test_assignments a
                LEFT JOIN ab_test_events e ON e.assignment_id = a.id
                    AND e.event_timestamp >= NOW() - INTERVAL '%s days'
                WHERE a.test_id = %s
                AND a.variant_id = %s
            """, (days, test_id, variant_id))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            total_assignments = row[0] or 0
            conversions = row[1] or 0
            revenue = float(row[2] or 0)
            conversion_rate = conversions / total_assignments if total_assignments > 0 else 0.0
            revenue_per_user = revenue / total_assignments if total_assignments > 0 else 0.0
            
            metrics = VariantMetrics(
                variant_id=variant_id,
                total_assignments=total_assignments,
                conversions=conversions,
                revenue=revenue,
                conversion_rate=conversion_rate,
                revenue_per_user=revenue_per_user,
                email_sent=row[3] or 0,
                email_opened=row[4] or 0,
                email_clicked=row[5] or 0,
                page_views=row[6] or 0,
                cta_clicks=row[7] or 0,
            )
            
            cursor.close()
            conn.close()
            
            return metrics
            
        except Exception as e:
            logger.error(f"Error calculating variant metrics from events: {e}", exc_info=True)
            return None
    
    def calculate_statistical_significance(
        self,
        test_id: str,
        primary_metric: str = "conversion_rate"
    ) -> Optional[StatisticalResult]:
        """
        Calcula significancia estadística entre variantes usando z-test.
        
        Args:
            test_id: ID del test
            primary_metric: Métrica primaria a analizar
            
        Returns:
            Resultado del análisis estadístico
        """
        try:
            # Obtener configuración del test
            test_config = self.get_test_config(test_id)
            if not test_config:
                logger.error(f"Test {test_id} not found")
                return None
            
            # Obtener variantes
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT variant_id, is_control
                FROM ab_test_variants
                WHERE test_id = %s
                AND is_active = true
                ORDER BY variant_id
            """, (test_id,))
            
            variants = cursor.fetchall()
            if len(variants) < 2:
                logger.error(f"Test {test_id} needs at least 2 active variants")
                return None
            
            # Identificar control y treatment
            control_variant = None
            treatment_variants = []
            
            for variant_id, is_control in variants:
                if is_control:
                    control_variant = variant_id
                else:
                    treatment_variants.append(variant_id)
            
            if not control_variant:
                # Si no hay control explícito, usar la primera como control
                control_variant = variants[0][0]
                treatment_variants = [v[0] for v in variants[1:]]
            
            # Obtener métricas
            control_metrics = self.get_variant_metrics(test_id, control_variant)
            if not control_metrics:
                logger.error(f"Could not get metrics for control variant {control_variant}")
                return None
            
            # Comparar con cada treatment variant
            best_variant = control_variant
            best_lift = 0.0
            best_p_value = 1.0
            best_z_score = 0.0
            is_significant = False
            
            for treatment_variant in treatment_variants:
                treatment_metrics = self.get_variant_metrics(test_id, treatment_variant)
                if not treatment_metrics:
                    continue
                
                # Calcular métrica según tipo
                if primary_metric == "conversion_rate":
                    control_value = control_metrics.conversion_rate
                    treatment_value = treatment_metrics.conversion_rate
                    control_n = control_metrics.total_assignments
                    treatment_n = treatment_metrics.total_assignments
                elif primary_metric == "open_rate":
                    control_value = (
                        control_metrics.email_opened / control_metrics.email_sent
                        if control_metrics.email_sent > 0 else 0
                    )
                    treatment_value = (
                        treatment_metrics.email_opened / treatment_metrics.email_sent
                        if treatment_metrics.email_sent > 0 else 0
                    )
                    control_n = control_metrics.email_sent
                    treatment_n = treatment_metrics.email_sent
                elif primary_metric == "click_rate":
                    control_value = (
                        control_metrics.email_clicked / control_metrics.email_opened
                        if control_metrics.email_opened > 0 else 0
                    )
                    treatment_value = (
                        treatment_metrics.email_clicked / treatment_metrics.email_opened
                        if treatment_metrics.email_opened > 0 else 0
                    )
                    control_n = control_metrics.email_opened
                    treatment_n = treatment_metrics.email_opened
                elif primary_metric == "revenue":
                    control_value = control_metrics.revenue_per_user
                    treatment_value = treatment_metrics.revenue_per_user
                    control_n = control_metrics.total_assignments
                    treatment_n = treatment_metrics.total_assignments
                else:
                    logger.warning(f"Unknown primary metric: {primary_metric}")
                    continue
                
                # Validar tamaño de muestra mínimo
                if control_n < MIN_SAMPLE_SIZE or treatment_n < MIN_SAMPLE_SIZE:
                    logger.info(
                        f"Insufficient sample size: control={control_n}, treatment={treatment_n}"
                    )
                    continue
                
                # Calcular z-test para proporciones (conversion rate, open rate, click rate)
                if primary_metric in ["conversion_rate", "open_rate", "click_rate"]:
                    p_value, z_score, ci_lower, ci_upper = self._z_test_proportions(
                        control_value, control_n,
                        treatment_value, treatment_n,
                        confidence_level=test_config["significance_level"]
                    )
                else:
                    # Para métricas continuas (revenue), usar t-test aproximado
                    p_value, z_score, ci_lower, ci_upper = self._z_test_means(
                        control_value, control_n,
                        treatment_value, treatment_n,
                        confidence_level=test_config["significance_level"]
                    )
                
                # Calcular lift
                lift = ((treatment_value - control_value) / control_value * 100) if control_value > 0 else 0
                
                # Determinar significancia
                alpha = 1 - test_config["significance_level"]
                is_treatment_significant = p_value < alpha
                
                # Verificar si es mejor que el mejor actual
                if treatment_value > control_value and (
                    is_treatment_significant or lift > best_lift
                ):
                    if is_treatment_significant or lift > best_lift:
                        best_variant = treatment_variant
                        best_lift = lift
                        best_p_value = p_value
                        best_z_score = z_score
                        is_significant = is_treatment_significant
            
            # Determinar recomendación
            recommendation, reason = self._determine_recommendation(
                test_config,
                is_significant,
                best_p_value,
                best_lift,
                best_variant,
                control_variant
            )
            
            result = StatisticalResult(
                is_significant=is_significant,
                p_value=best_p_value,
                confidence_level=test_config["significance_level"],
                z_score=best_z_score,
                confidence_interval_lower=ci_lower if 'ci_lower' in locals() else 0.0,
                confidence_interval_upper=ci_upper if 'ci_upper' in locals() else 0.0,
                lift_percentage=best_lift,
                winner_variant_id=best_variant if best_variant != control_variant else None,
                recommendation=recommendation,
                recommendation_reason=reason
            )
            
            cursor.close()
            conn.close()
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating statistical significance: {e}", exc_info=True)
            return None
    
    def _z_test_proportions(
        self,
        p1: float,
        n1: int,
        p2: float,
        n2: int,
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float, float]:
        """
        Z-test para comparar dos proporciones.
        
        Returns:
            (p_value, z_score, ci_lower, ci_upper)
        """
        # Pooled proportion
        pooled_p = (p1 * n1 + p2 * n2) / (n1 + n2)
        
        # Standard error
        se = math.sqrt(pooled_p * (1 - pooled_p) * (1/n1 + 1/n2))
        
        if se == 0:
            return (1.0, 0.0, 0.0, 0.0)
        
        # Z-score
        z_score = (p2 - p1) / se
        
        # P-value (two-tailed test)
        # Aproximación usando distribución normal
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
        
        # Confidence interval
        z_critical = Z_SCORE_95 if confidence_level == 0.95 else Z_SCORE_99
        margin = z_critical * se
        ci_lower = (p2 - p1) - margin
        ci_upper = (p2 - p1) + margin
        
        return (p_value, z_score, ci_lower, ci_upper)
    
    def _z_test_means(
        self,
        mean1: float,
        n1: int,
        mean2: float,
        n2: int,
        confidence_level: float = 0.95
    ) -> Tuple[float, float, float, float]:
        """
        Z-test para comparar dos medias (aproximación).
        
        Returns:
            (p_value, z_score, ci_lower, ci_upper)
        """
        # Standard error (aproximación)
        # Asumimos varianza similar para ambas muestras
        se = math.sqrt((mean1 / n1) + (mean2 / n2))
        
        if se == 0:
            return (1.0, 0.0, 0.0, 0.0)
        
        # Z-score
        z_score = (mean2 - mean1) / se
        
        # P-value
        p_value = 2 * (1 - self._normal_cdf(abs(z_score)))
        
        # Confidence interval
        z_critical = Z_SCORE_95 if confidence_level == 0.95 else Z_SCORE_99
        margin = z_critical * se
        ci_lower = (mean2 - mean1) - margin
        ci_upper = (mean2 - mean1) + margin
        
        return (p_value, z_score, ci_lower, ci_upper)
    
    def _normal_cdf(self, x: float) -> float:
        """Aproximación de CDF de distribución normal."""
        # Aproximación usando función de error
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _determine_recommendation(
        self,
        test_config: Dict[str, Any],
        is_significant: bool,
        p_value: float,
        lift: float,
        winner_variant: str,
        control_variant: str
    ) -> Tuple[str, str]:
        """Determina recomendación basada en resultados."""
        min_lift = test_config.get("minimum_lift_percentage", 5.0)
        auto_deploy_when = test_config.get("auto_deploy_when", "significant")
        
        # Verificar tamaño de muestra mínimo
        if not self._has_minimum_sample_size(test_config["test_id"]):
            return (
                "continue",
                f"Sample size below minimum ({test_config['minimum_sample_size']})"
            )
        
        # Si hay ganador claro y significancia
        if winner_variant != control_variant:
            if auto_deploy_when == "significant":
                if is_significant:
                    return (
                        "deploy",
                        f"Winner {winner_variant} is statistically significant "
                        f"(p={p_value:.4f}, lift={lift:.2f}%)"
                    )
                else:
                    return (
                        "continue",
                        f"Winner {winner_variant} shows lift ({lift:.2f}%) but not yet significant "
                        f"(p={p_value:.4f})"
                    )
            
            elif auto_deploy_when == "significant_and_lift":
                if is_significant and lift >= min_lift:
                    return (
                        "deploy",
                        f"Winner {winner_variant} is significant and meets minimum lift "
                        f"(p={p_value:.4f}, lift={lift:.2f}%)"
                    )
                elif is_significant:
                    return (
                        "continue",
                        f"Winner {winner_variant} is significant but lift ({lift:.2f}%) "
                        f"below minimum ({min_lift}%)"
                    )
                else:
                    return (
                        "continue",
                        f"Winner {winner_variant} shows lift but not yet significant"
                    )
        
        # No hay ganador claro
        return (
            "continue",
            "No clear winner yet, continue testing"
        )
    
    def _has_minimum_sample_size(self, test_id: str) -> bool:
        """Verifica si el test tiene tamaño de muestra mínimo."""
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    SUM(total_assignments) as total_sample
                FROM ab_test_results
                WHERE test_id = %s
                AND analysis_date = CURRENT_DATE
            """, (test_id,))
            
            row = cursor.fetchone()
            total_sample = row[0] or 0
            
            cursor.execute("""
                SELECT minimum_sample_size
                FROM ab_tests
                WHERE test_id = %s
            """, (test_id,))
            
            row = cursor.fetchone()
            min_sample = row[0] if row else 1000
            
            cursor.close()
            conn.close()
            
            return total_sample >= min_sample
            
        except Exception as e:
            logger.error(f"Error checking minimum sample size: {e}", exc_info=True)
            return False
    
    def save_statistical_analysis(
        self,
        test_id: str,
        result: StatisticalResult,
        comparison_data: Dict[str, Any],
        analysis_type: str = "daily"
    ) -> bool:
        """Guarda análisis estadístico en la base de datos."""
        try:
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ab_test_statistical_analysis (
                    test_id, analysis_type, comparison_data,
                    is_significant, p_value, confidence_level,
                    winner_variant_id, winner_lift_percentage,
                    recommendation, recommendation_reason
                ) VALUES (
                    %s, %s, %s::jsonb, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                test_id,
                analysis_type,
                json.dumps(comparison_data),
                result.is_significant,
                result.p_value,
                result.confidence_level,
                result.winner_variant_id,
                result.lift_percentage,
                result.recommendation,
                result.recommendation_reason
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error saving statistical analysis: {e}", exc_info=True)
            return False
    
    def deploy_winning_variant(
        self,
        test_id: str,
        variant_id: str,
        deployment_type: str = "auto",
        deployed_by: Optional[str] = None
    ) -> bool:
        """
        Despliega la variante ganadora.
        
        Args:
            test_id: ID del test
            variant_id: ID de la variante ganadora
            deployment_type: 'auto' o 'manual'
            deployed_by: Usuario que despliega
            
        Returns:
            True si se inició el deployment exitosamente
        """
        try:
            # Obtener métricas pre-deployment
            metrics = self.get_variant_metrics(test_id, variant_id)
            if not metrics:
                logger.error(f"Could not get metrics for variant {variant_id}")
                return False
            
            pre_deployment_metrics = {
                "conversion_rate": metrics.conversion_rate,
                "revenue_per_user": metrics.revenue_per_user,
                "total_assignments": metrics.total_assignments,
                "conversions": metrics.conversions,
            }
            
            # Crear registro de deployment
            conn = self.pg_hook.get_conn()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ab_test_deployments (
                    test_id, winning_variant_id, deployment_type,
                    deployment_status, pre_deployment_metrics, deployed_by
                ) VALUES (
                    %s, %s, %s, 'pending', %s::jsonb, %s
                )
                RETURNING id
            """, (
                test_id,
                variant_id,
                deployment_type,
                json.dumps(pre_deployment_metrics),
                deployed_by
            ))
            
            deployment_id = cursor.fetchone()[0]
            
            # Actualizar estado del test
            cursor.execute("""
                UPDATE ab_tests
                SET status = 'deployed',
                    deployed_at = NOW()
                WHERE test_id = %s
            """, (test_id,))
            
            conn.commit()
            
            logger.info(
                f"Deployment initiated for test {test_id}, variant {variant_id} "
                f"(deployment_id={deployment_id})"
            )
            
            # Aquí se integraría con el sistema de deployment real
            # Por ahora, solo marcamos como in_progress
            cursor.execute("""
                UPDATE ab_test_deployments
                SET deployment_status = 'in_progress'
                WHERE id = %s
            """, (deployment_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Error deploying winning variant: {e}", exc_info=True)
            return False


# Funciones helper para integraciones específicas

def get_email_subject_for_test(
    ab_engine: ABTestingEngine,
    test_id: str,
    email: str,
    default_subject: str
) -> str:
    """
    Obtiene el subject line correcto para un test de email.
    
    Args:
        ab_engine: Instancia del motor de A/B testing
        test_id: ID del test
        email: Email del destinatario
        default_subject: Subject por defecto si no hay test activo
        
    Returns:
        Subject line a usar
    """
    variant_id = ab_engine.assign_variant(test_id, email=email)
    if not variant_id:
        return default_subject
    
    # Obtener configuración de la variante
    test_config = ab_engine.get_test_config(test_id)
    if not test_config or test_config["status"] != "active":
        return default_subject
    
    try:
        conn = ab_engine.pg_hook.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT config->>'subject_line'
            FROM ab_test_variants
            WHERE test_id = %s
            AND variant_id = %s
        """, (test_id, variant_id))
        
        row = cursor.fetchone()
        subject = row[0] if row and row[0] else default_subject
        
        cursor.close()
        conn.close()
        
        # Registrar evento de email enviado
        ab_engine.record_event(test_id, email=email, event_type="email_sent")
        
        return subject
        
    except Exception as e:
        logger.error(f"Error getting email subject: {e}", exc_info=True)
        return default_subject


def get_landing_page_config(
    ab_engine: ABTestingEngine,
    test_id: str,
    session_id: str,
    default_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Obtiene la configuración de landing page para un test.
    
    Args:
        ab_engine: Instancia del motor de A/B testing
        test_id: ID del test
        session_id: ID de sesión
        default_config: Configuración por defecto
        
    Returns:
        Configuración de landing page a usar
    """
    variant_id = ab_engine.assign_variant(test_id, session_id=session_id)
    if not variant_id:
        return default_config
    
    try:
        conn = ab_engine.pg_hook.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT config
            FROM ab_test_variants
            WHERE test_id = %s
            AND variant_id = %s
        """, (test_id, variant_id))
        
        row = cursor.fetchone()
        config = json.loads(row[0]) if row and row[0] else default_config
        
        cursor.close()
        conn.close()
        
        # Registrar evento de page view
        ab_engine.record_event(test_id, session_id=session_id, event_type="page_view")
        
        return config
        
    except Exception as e:
        logger.error(f"Error getting landing page config: {e}", exc_info=True)
        return default_config


def get_pricing_for_test(
    ab_engine: ABTestingEngine,
    test_id: str,
    user_id: str,
    default_pricing: Dict[str, float]
) -> Dict[str, float]:
    """
    Obtiene precios dinámicos para un test.
    
    Args:
        ab_engine: Instancia del motor de A/B testing
        test_id: ID del test
        user_id: ID del usuario
        default_pricing: Precios por defecto
        
    Returns:
        Diccionario de precios a usar
    """
    variant_id = ab_engine.assign_variant(test_id, user_id=user_id)
    if not variant_id:
        return default_pricing
    
    try:
        conn = ab_engine.pg_hook.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT config->>'pricing'
            FROM ab_test_variants
            WHERE test_id = %s
            AND variant_id = %s
        """, (test_id, variant_id))
        
        row = cursor.fetchone()
        if row and row[0]:
            pricing = json.loads(row[0])
            return pricing
        
        cursor.close()
        conn.close()
        
        return default_pricing
        
    except Exception as e:
        logger.error(f"Error getting pricing: {e}", exc_info=True)
        return default_pricing


def get_cta_button_config(
    ab_engine: ABTestingEngine,
    test_id: str,
    session_id: str,
    default_config: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Obtiene configuración de CTA button para un test.
    
    Args:
        ab_engine: Instancia del motor de A/B testing
        test_id: ID del test
        session_id: ID de sesión
        default_config: Configuración por defecto
        
    Returns:
        Configuración de CTA button (text, color, position, etc.)
    """
    variant_id = ab_engine.assign_variant(test_id, session_id=session_id)
    if not variant_id:
        return default_config
    
    try:
        conn = ab_engine.pg_hook.get_conn()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT config->>'cta_button'
            FROM ab_test_variants
            WHERE test_id = %s
            AND variant_id = %s
        """, (test_id, variant_id))
        
        row = cursor.fetchone()
        if row and row[0]:
            cta_config = json.loads(row[0])
            return cta_config
        
        cursor.close()
        conn.close()
        
        return default_config
        
    except Exception as e:
        logger.error(f"Error getting CTA button config: {e}", exc_info=True)
        return default_config

