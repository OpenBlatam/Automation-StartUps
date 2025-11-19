"""
DAG de Airflow para automatización de A/B Testing.

Funcionalidades:
- Análisis estadístico automático de tests activos
- Detección de significancia estadística
- Auto-deployment de versión ganadora cuando se alcanza significancia
- Reportes y notificaciones
- Integración con emails, landing pages, pricing y CTA buttons
"""
from __future__ import annotations

import logging
from datetime import timedelta, datetime
from typing import Dict, Any, List, Optional

import pendulum
from airflow.decorators import dag, task, task_group
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.postgres.hooks.postgres import PostgresHook

from data.airflow.plugins.ab_testing import (
    ABTestingEngine,
    StatisticalResult,
    VariantMetrics,
    get_email_subject_for_test,
    get_landing_page_config,
    get_pricing_for_test,
    get_cta_button_config,
)
from data.airflow.plugins.etl_notifications import notify_slack

logger = logging.getLogger(__name__)


@dag(
    dag_id="ab_testing_automation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "marketing",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Automatización de A/B Testing
    
    Sistema completo para automatizar tests A/B con:
    - Análisis estadístico automático
    - Detección de significancia
    - Auto-deployment de versión ganadora
    - Soporte para:
      - Subject lines de emails
      - Landing pages
      - Precios dinámicos
      - CTA buttons
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres (default: postgres_default)
    - `auto_deploy_enabled`: Habilitar auto-deployment (default: true)
    - `slack_webhook_url`: Webhook de Slack para notificaciones
    - `min_analysis_interval_hours`: Intervalo mínimo entre análisis (default: 24)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "auto_deploy_enabled": Param(True, type="boolean"),
        "slack_webhook_url": Param("", type="string"),
        "min_analysis_interval_hours": Param(24, type="integer", minimum=1, maximum=168),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["ab-testing", "marketing", "automation", "statistics"],
)
def ab_testing_automation() -> None:
    """DAG principal para automatización de A/B testing."""
    
    @task(task_id="get_active_tests")
    def get_active_tests() -> List[Dict[str, Any]]:
        """Obtiene todos los tests activos."""
        ctx = get_current_context()
        postgres_conn_id = ctx["params"]["postgres_conn_id"]
        
        pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT 
                    test_id, test_name, test_type, primary_metric,
                    auto_deploy_enabled, auto_deploy_when,
                    minimum_sample_size, significance_level, minimum_lift_percentage
                FROM ab_tests
                WHERE status = 'active'
                ORDER BY created_at DESC
            """)
            
            tests = []
            for row in cursor.fetchall():
                tests.append({
                    "test_id": row[0],
                    "test_name": row[1],
                    "test_type": row[2],
                    "primary_metric": row[3],
                    "auto_deploy_enabled": row[4],
                    "auto_deploy_when": row[5],
                    "minimum_sample_size": row[6],
                    "significance_level": float(row[7]) if row[7] else 0.95,
                    "minimum_lift_percentage": float(row[8]) if row[8] else 5.0,
                })
            
            logger.info(f"Found {len(tests)} active tests")
            return tests
            
        finally:
            cursor.close()
            conn.close()
    
    @task_group(group_id="analyze_test")
    def analyze_test_group(test: Dict[str, Any]):
        """Task group para analizar un test individual."""
        
        @task(task_id="calculate_results")
        def calculate_results(test: Dict[str, Any]) -> Dict[str, Any]:
            """Calcula resultados agregados del test."""
            ctx = get_current_context()
            postgres_conn_id = ctx["params"]["postgres_conn_id"]
            
            pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            try:
                # Calcular resultados agregados
                cursor.execute("""
                    SELECT calculate_ab_test_results(%s, CURRENT_DATE, 24)
                """, (test["test_id"],))
                
                # Obtener métricas de todas las variantes
                cursor.execute("""
                    SELECT 
                        variant_id,
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
                    AND analysis_date = CURRENT_DATE
                """, (test["test_id"],))
                
                variants_metrics = {}
                for row in cursor.fetchall():
                    variants_metrics[row[0]] = {
                        "total_assignments": row[1] or 0,
                        "conversions": row[2] or 0,
                        "revenue": float(row[3] or 0),
                        "conversion_rate": float(row[4] or 0),
                        "revenue_per_user": float(row[5] or 0),
                        "email_sent": row[6] or 0,
                        "email_opened": row[7] or 0,
                        "email_clicked": row[8] or 0,
                        "page_views": row[9] or 0,
                        "cta_clicks": row[10] or 0,
                    }
                
                return {
                    "test_id": test["test_id"],
                    "variants_metrics": variants_metrics,
                }
                
            finally:
                cursor.close()
                conn.close()
        
        @task(task_id="statistical_analysis")
        def statistical_analysis(results: Dict[str, Any]) -> Dict[str, Any]:
            """Realiza análisis estadístico."""
            ctx = get_current_context()
            postgres_conn_id = ctx["params"]["postgres_conn_id"]
            
            ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
            
            test_id = results["test_id"]
            statistical_result = ab_engine.calculate_statistical_significance(
                test_id,
                primary_metric=results.get("primary_metric", "conversion_rate")
            )
            
            if not statistical_result:
                logger.warning(f"Could not calculate statistical significance for {test_id}")
                return {
                    "test_id": test_id,
                    "analysis_success": False,
                }
            
            # Guardar análisis
            comparison_data = {
                "variants": results["variants_metrics"],
                "analysis_timestamp": datetime.utcnow().isoformat(),
            }
            
            ab_engine.save_statistical_analysis(
                test_id,
                statistical_result,
                comparison_data,
                analysis_type="daily"
            )
            
            return {
                "test_id": test_id,
                "analysis_success": True,
                "is_significant": statistical_result.is_significant,
                "p_value": statistical_result.p_value,
                "lift_percentage": statistical_result.lift_percentage,
                "winner_variant_id": statistical_result.winner_variant_id,
                "recommendation": statistical_result.recommendation,
                "recommendation_reason": statistical_result.recommendation_reason,
                "variants_metrics": results["variants_metrics"],
            }
        
        @task(task_id="check_deployment")
        def check_deployment(analysis: Dict[str, Any]) -> Dict[str, Any]:
            """Verifica si se debe hacer deployment."""
            ctx = get_current_context()
            postgres_conn_id = ctx["params"]["postgres_conn_id"]
            auto_deploy_enabled = ctx["params"]["auto_deploy_enabled"]
            dry_run = ctx["params"]["dry_run"]
            
            if not analysis.get("analysis_success"):
                return {
                    "test_id": analysis["test_id"],
                    "should_deploy": False,
                    "reason": "Analysis failed",
                }
            
            if analysis["recommendation"] != "deploy":
                return {
                    "test_id": analysis["test_id"],
                    "should_deploy": False,
                    "reason": analysis["recommendation_reason"],
                }
            
            if not auto_deploy_enabled:
                return {
                    "test_id": analysis["test_id"],
                    "should_deploy": False,
                    "reason": "Auto-deploy disabled",
                }
            
            # Verificar si ya hay un deployment en progreso
            pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
            conn = pg_hook.get_conn()
            cursor = conn.cursor()
            
            try:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM ab_test_deployments
                    WHERE test_id = %s
                    AND deployment_status IN ('pending', 'in_progress')
                """, (analysis["test_id"],))
                
                existing_deployment = cursor.fetchone()[0] > 0
                
                if existing_deployment:
                    return {
                        "test_id": analysis["test_id"],
                        "should_deploy": False,
                        "reason": "Deployment already in progress",
                    }
                
                return {
                    "test_id": analysis["test_id"],
                    "should_deploy": True,
                    "winner_variant_id": analysis["winner_variant_id"],
                    "lift_percentage": analysis["lift_percentage"],
                    "p_value": analysis["p_value"],
                    "dry_run": dry_run,
                }
                
            finally:
                cursor.close()
                conn.close()
        
        @task(task_id="deploy_winner")
        def deploy_winner(deployment_info: Dict[str, Any]) -> Dict[str, Any]:
            """Despliega la versión ganadora."""
            ctx = get_current_context()
            postgres_conn_id = ctx["params"]["postgres_conn_id"]
            dry_run = deployment_info.get("dry_run", False)
            
            if not deployment_info.get("should_deploy"):
                logger.info(
                    f"Test {deployment_info['test_id']} does not need deployment: "
                    f"{deployment_info.get('reason', 'Unknown')}"
                )
                return {
                    "test_id": deployment_info["test_id"],
                    "deployed": False,
                    "reason": deployment_info.get("reason", "Not needed"),
                }
            
            if dry_run:
                logger.info(
                    f"[DRY RUN] Would deploy variant {deployment_info['winner_variant_id']} "
                    f"for test {deployment_info['test_id']}"
                )
                return {
                    "test_id": deployment_info["test_id"],
                    "deployed": False,
                    "reason": "Dry run mode",
                }
            
            ab_engine = ABTestingEngine(postgres_conn_id=postgres_conn_id)
            
            success = ab_engine.deploy_winning_variant(
                deployment_info["test_id"],
                deployment_info["winner_variant_id"],
                deployment_type="auto",
                deployed_by="airflow_ab_testing_automation"
            )
            
            if success:
                logger.info(
                    f"Successfully deployed variant {deployment_info['winner_variant_id']} "
                    f"for test {deployment_info['test_id']}"
                )
                
                # Aquí se integraría con el sistema de deployment real
                # Por ejemplo, actualizar configuración de emails, landing pages, etc.
                _integrate_deployment(
                    deployment_info["test_id"],
                    deployment_info["winner_variant_id"],
                    postgres_conn_id
                )
            
            return {
                "test_id": deployment_info["test_id"],
                "deployed": success,
                "winner_variant_id": deployment_info["winner_variant_id"],
            }
        
        # Pipeline del task group
        results = calculate_results(test)
        analysis = statistical_analysis(results)
        deployment_info = check_deployment(analysis)
        deployment_result = deploy_winner(deployment_info)
        
        return deployment_result
    
    @task(task_id="generate_summary")
    def generate_summary(test_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Genera resumen de todos los tests."""
        summary = {
            "total_tests": len(test_results),
            "tests_analyzed": 0,
            "tests_significant": 0,
            "tests_deployed": 0,
            "tests_by_type": {},
            "details": [],
        }
        
        for result in test_results:
            if result.get("analysis_success"):
                summary["tests_analyzed"] += 1
                
                if result.get("is_significant"):
                    summary["tests_significant"] += 1
                
                if result.get("deployed"):
                    summary["tests_deployed"] += 1
            
            # Agrupar por tipo
            test_type = result.get("test_type", "unknown")
            summary["tests_by_type"][test_type] = summary["tests_by_type"].get(test_type, 0) + 1
            
            summary["details"].append({
                "test_id": result.get("test_id"),
                "analysis_success": result.get("analysis_success", False),
                "is_significant": result.get("is_significant", False),
                "deployed": result.get("deployed", False),
            })
        
        return summary
    
    @task(task_id="notify_results")
    def notify_results(summary: Dict[str, Any]) -> None:
        """Envía notificaciones con los resultados."""
        ctx = get_current_context()
        slack_webhook_url = ctx["params"].get("slack_webhook_url")
        
        if not slack_webhook_url:
            logger.info("Slack webhook not configured, skipping notification")
            return
        
        message = f"""
📊 **A/B Testing Automation Summary**

**Total Tests:** {summary['total_tests']}
**Tests Analyzed:** {summary['tests_analyzed']}
**Tests Significant:** {summary['tests_significant']}
**Tests Deployed:** {summary['tests_deployed']}

**Tests by Type:**
"""
        
        for test_type, count in summary["tests_by_type"].items():
            message += f"  - {test_type}: {count}\n"
        
        if summary["tests_deployed"] > 0:
            message += "\n✅ **Deployments Completed:**\n"
            for detail in summary["details"]:
                if detail.get("deployed"):
                    message += f"  - {detail['test_id']}\n"
        
        try:
            notify_slack(slack_webhook_url, message)
        except Exception as e:
            logger.error(f"Error sending Slack notification: {e}", exc_info=True)
    
    # Pipeline principal
    active_tests = get_active_tests()
    
    # Analizar cada test
    test_results = []
    for test in active_tests:
        result = analyze_test_group.expand(test=[test])
        test_results.append(result)
    
    summary = generate_summary(test_results)
    notify_results(summary)


def _integrate_deployment(
    test_id: str,
    variant_id: str,
    postgres_conn_id: str
) -> None:
    """
    Integra el deployment con sistemas externos.
    
    Esta función se puede extender para:
    - Actualizar configuración de emails (subject lines)
    - Actualizar landing pages en CMS
    - Actualizar precios en sistema de pricing
    - Actualizar CTA buttons en frontend
    """
    try:
        pg_hook = PostgresHook(postgres_conn_id=postgres_conn_id)
        conn = pg_hook.get_conn()
        cursor = conn.cursor()
        
        # Obtener configuración del test y variante
        cursor.execute("""
            SELECT test_type, config
            FROM ab_tests t
            JOIN ab_test_variants v ON v.test_id = t.test_id
            WHERE t.test_id = %s
            AND v.variant_id = %s
        """, (test_id, variant_id))
        
        row = cursor.fetchone()
        if not row:
            logger.warning(f"Could not get config for test {test_id}, variant {variant_id}")
            return
        
        test_type = row[0]
        variant_config = row[1]
        
        # Integrar según tipo de test
        if test_type == "email_subject":
            # Actualizar subject lines en sistema de emails
            subject_line = variant_config.get("subject_line")
            logger.info(f"Deploying email subject: {subject_line}")
            # TODO: Integrar con sistema de email (SendGrid, Mailgun, etc.)
            
        elif test_type == "landing_page":
            # Actualizar landing page en CMS
            logger.info(f"Deploying landing page config for variant {variant_id}")
            # TODO: Integrar con CMS (Contentful, Strapi, etc.)
            
        elif test_type == "pricing":
            # Actualizar precios en sistema de pricing
            pricing = variant_config.get("pricing")
            logger.info(f"Deploying pricing: {pricing}")
            # TODO: Integrar con sistema de pricing
            
        elif test_type == "cta_button":
            # Actualizar CTA buttons en frontend
            cta_config = variant_config.get("cta_button")
            logger.info(f"Deploying CTA config: {cta_config}")
            # TODO: Integrar con frontend/CDN
            
        # Marcar deployment como completado
        cursor.execute("""
            UPDATE ab_test_deployments
            SET deployment_status = 'completed',
                completed_at = NOW()
            WHERE test_id = %s
            AND winning_variant_id = %s
            AND deployment_status = 'in_progress'
        """, (test_id, variant_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
    except Exception as e:
        logger.error(f"Error integrating deployment: {e}", exc_info=True)


# Instanciar DAG
ab_testing_automation()

