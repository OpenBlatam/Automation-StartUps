from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_scoring_automation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "retry_exponential_backoff": True,
        "max_retry_delay": timedelta(minutes=30),
        "depends_on_past": False,
    },
    doc_md="""
    ### Automatización de Calificación de Leads (Lead Scoring)
    
    Sistema automatizado que calcula y actualiza scores de leads basándose en múltiples factores:
    - Información de contacto (email, teléfono, nombre)
    - Engagement (opens, clicks, replies de emails)
    - Fuente y atribución (UTM, source)
    - Antigüedad del lead
    - Comportamiento en secuencias de nurturing
    
    **Funcionalidades:**
    - Cálculo automático de scores basado en reglas configurables
    - Actualización de prioridad (low/medium/high) basada en score
    - Historial completo de cambios de score
    - Identificación automática de leads calificados para ventas
    - Soporte para scoring predictivo con ML (opcional)
    - Análisis de tendencias de scoring
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `max_leads_per_run`: Máximo de leads a procesar (default: 500)
    - `min_score_to_qualify`: Score mínimo para calificar (default: 50)
    - `enable_ml_scoring`: Usar modelo ML para scoring predictivo (default: false)
    - `ml_model_endpoint`: Endpoint del modelo ML (opcional)
    - `include_engagement_data`: Incluir datos de nurturing en cálculo (default: true)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_leads_per_run": Param(500, type="integer", minimum=1, maximum=5000),
        "min_score_to_qualify": Param(50, type="integer", minimum=0, maximum=100),
        "enable_ml_scoring": Param(False, type="boolean"),
        "ml_model_endpoint": Param("", type="string"),
        "include_engagement_data": Param(True, type="boolean"),
        "update_priority_auto": Param(True, type="boolean"),
        "auto_qualify_for_sales": Param(True, type="boolean"),
        "slack_webhook_url": Param("", type="string"),
    },
    tags=["sales", "lead-scoring", "automation", "ml"],
)
def lead_scoring_automation() -> None:
    """
    DAG principal para automatización de scoring de leads.
    """
    
    @task(task_id="ensure_schema")
    def ensure_schema() -> bool:
        """Verifica que el schema esté creado."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        try:
            with hook.get_conn() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT COUNT(*) FROM information_schema.tables 
                        WHERE table_name = 'lead_score_history'
                    """)
                    
                    if cur.fetchone()[0] == 0:
                        logger.warning(
                            "Schema de sales_tracking no encontrado. "
                            "Por favor ejecuta data/db/sales_tracking_schema.sql"
                        )
                        return False
                    
                    logger.info("Schema verificado correctamente")
                    return True
        except Exception as e:
            logger.error(f"Error verificando schema: {e}", exc_info=True)
            return False
    
    @task(task_id="get_leads_to_score")
    def get_leads_to_score() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan scoring/recálculo."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        include_engagement = bool(params["include_engagement_data"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Query para obtener leads con sus datos de engagement si está habilitado
        if include_engagement:
            query = """
                SELECT DISTINCT
                    l.ext_id,
                    l.email,
                    l.first_name,
                    l.last_name,
                    l.phone,
                    l.score AS current_score,
                    l.priority AS current_priority,
                    l.source,
                    l.utm_source,
                    l.utm_campaign,
                    l.created_at,
                    EXTRACT(EPOCH FROM (NOW() - l.created_at)) / 86400 AS days_since_created,
                    -- Engagement data from nurturing
                    COALESCE(eng.replies_count, 0) AS engagement_replies,
                    COALESCE(eng.clicks_count, 0) AS engagement_clicks,
                    COALESCE(eng.opens_count, 0) AS engagement_opens
                FROM leads l
                LEFT JOIN (
                    SELECT 
                        s.lead_ext_id,
                        COUNT(*) FILTER (WHERE e.replied_at IS NOT NULL) AS replies_count,
                        COUNT(*) FILTER (WHERE e.clicked_at IS NOT NULL) AS clicks_count,
                        COUNT(*) FILTER (WHERE e.opened_at IS NOT NULL) AS opens_count
                    FROM lead_nurturing_sequences s
                    LEFT JOIN lead_nurturing_events e ON s.id = e.sequence_id
                    WHERE s.status IN ('active', 'qualified')
                    GROUP BY s.lead_ext_id
                ) eng ON l.ext_id = eng.lead_ext_id
                WHERE 
                    l.email IS NOT NULL
                    AND (l.updated_at IS NULL OR l.updated_at <= NOW() - INTERVAL '6 hours')
                    -- Priorizar leads sin score o con score bajo
                    AND (l.score IS NULL OR l.score < 100)
                ORDER BY 
                    CASE 
                        WHEN l.score IS NULL THEN 1
                        WHEN l.score < 50 THEN 2
                        ELSE 3
                    END,
                    l.updated_at ASC NULLS FIRST
                LIMIT %s
            """
        else:
            query = """
                SELECT 
                    l.ext_id,
                    l.email,
                    l.first_name,
                    l.last_name,
                    l.phone,
                    l.score AS current_score,
                    l.priority AS current_priority,
                    l.source,
                    l.utm_source,
                    l.utm_campaign,
                    l.created_at,
                    EXTRACT(EPOCH FROM (NOW() - l.created_at)) / 86400 AS days_since_created,
                    0 AS engagement_replies,
                    0 AS engagement_clicks,
                    0 AS engagement_opens
                FROM leads l
                WHERE 
                    l.email IS NOT NULL
                    AND (l.updated_at IS NULL OR l.updated_at <= NOW() - INTERVAL '6 hours')
                    AND (l.score IS NULL OR l.score < 100)
                ORDER BY l.updated_at ASC NULLS FIRST
                LIMIT %s
            """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Obtenidos {len(leads)} leads para scoring")
        
        try:
            Stats.incr("lead_scoring.leads_processed", len(leads))
        except Exception:
            pass
        
        return leads
    
    @task(task_id="calculate_scores")
    def calculate_scores(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calcula scores para cada lead usando la función SQL."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        enable_ml = bool(params["enable_ml_scoring"])
        ml_endpoint = str(params["ml_model_endpoint"]).strip()
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        scored_leads = []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in leads:
                    try:
                        # Preparar factores para scoring
                        has_email = bool(lead.get("email") and "@" in str(lead.get("email", "")))
                        has_phone = bool(lead.get("phone") and len(str(lead.get("phone", ""))) > 5)
                        has_name = bool(lead.get("first_name") or lead.get("last_name"))
                        
                        # Source score basado en source quality
                        source = str(lead.get("source", "")).lower()
                        source_score = 0
                        if "organic" in source or "direct" in source:
                            source_score = 5
                        elif "referral" in source or "partner" in source:
                            source_score = 4
                        elif "paid" in source or "ad" in source:
                            source_score = 3
                        elif "social" in source:
                            source_score = 2
                        else:
                            source_score = 1
                        
                        # UTM score
                        utm_score = 0
                        if lead.get("utm_source") or lead.get("utm_campaign"):
                            utm_score = 2
                        
                        # Usar función SQL para calcular score
                        days_since = int(lead.get("days_since_created", 0) or 0)
                        
                        cur.execute("""
                            SELECT calculate_lead_score(
                                %s,  -- lead_ext_id
                                %s,  -- engagement_replies
                                %s,  -- engagement_clicks
                                %s,  -- engagement_opens
                                %s,  -- has_email
                                %s,  -- has_phone
                                %s,  -- has_name
                                %s,  -- source_score
                                %s,  -- utm_score
                                %s   -- days_since_created
                            )
                        """, (
                            lead["ext_id"],
                            int(lead.get("engagement_replies", 0) or 0),
                            int(lead.get("engagement_clicks", 0) or 0),
                            int(lead.get("engagement_opens", 0) or 0),
                            has_email,
                            has_phone,
                            has_name,
                            source_score,
                            utm_score,
                            days_since
                        ))
                        
                        new_score = cur.fetchone()[0]
                        current_score = lead.get("current_score")
                        
                        # Scoring ML predictivo (opcional)
                        if enable_ml and ml_endpoint:
                            try:
                                ml_prediction = get_ml_prediction(lead, ml_endpoint)
                                if ml_prediction:
                                    # Promedio ponderado: 70% reglas, 30% ML
                                    new_score = int(new_score * 0.7 + ml_prediction * 0.3)
                            except Exception as e:
                                logger.warning(f"Error en ML scoring para {lead['ext_id']}: {e}")
                        
                        # Determinar prioridad basada en score
                        if new_score >= 50:
                            new_priority = "high"
                        elif new_score >= 35:
                            new_priority = "medium"
                        else:
                            new_priority = "low"
                        
                        scored_leads.append({
                            **lead,
                            "new_score": new_score,
                            "new_priority": new_priority,
                            "score_change": new_score - (current_score or 0),
                            "scoring_factors": {
                                "has_email": has_email,
                                "has_phone": has_phone,
                                "has_name": has_name,
                                "source_score": source_score,
                                "utm_score": utm_score,
                                "engagement_replies": lead.get("engagement_replies", 0),
                                "engagement_clicks": lead.get("engagement_clicks", 0),
                                "engagement_opens": lead.get("engagement_opens", 0),
                                "days_since_created": days_since
                            }
                        })
                        
                    except Exception as e:
                        logger.error(f"Error calculando score para lead {lead.get('ext_id')}: {e}", exc_info=True)
                        continue
        
        logger.info(f"Scores calculados para {len(scored_leads)} leads")
        return scored_leads
    
    @task(task_id="update_scores_and_history")
    def update_scores_and_history(scored_leads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Actualiza scores en tabla leads y guarda historial."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        update_priority = bool(params["update_priority_auto"])
        min_score_to_qualify = int(params["min_score_to_qualify"])
        auto_qualify = bool(params["auto_qualify_for_sales"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {
            "updated": 0,
            "qualifications": 0,
            "priority_changes": 0,
            "score_increases": 0,
            "score_decreases": 0
        }
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in scored_leads:
                    try:
                        lead_ext_id = lead["ext_id"]
                        new_score = lead["new_score"]
                        new_priority = lead["new_priority"]
                        current_score = lead.get("current_score")
                        current_priority = lead.get("current_priority")
                        score_change = lead["score_change"]
                        
                        # Guardar en historial
                        cur.execute("""
                            INSERT INTO lead_score_history 
                            (lead_ext_id, score, previous_score, priority, scoring_factors, calculated_at)
                            VALUES (%s, %s, %s, %s, %s, NOW())
                        """, (
                            lead_ext_id,
                            new_score,
                            current_score,
                            new_priority,
                            json.dumps(lead.get("scoring_factors", {}))
                        ))
                        
                        # Actualizar lead
                        cur.execute("""
                            UPDATE leads
                            SET score = %s,
                                priority = %s,
                                updated_at = NOW()
                            WHERE ext_id = %s
                        """, (new_score, new_priority, lead_ext_id))
                        
                        stats["updated"] += 1
                        
                        if score_change > 0:
                            stats["score_increases"] += 1
                        elif score_change < 0:
                            stats["score_decreases"] += 1
                        
                        if new_priority != current_priority:
                            stats["priority_changes"] += 1
                        
                        # Auto-calificar para ventas si alcanza score mínimo
                        if auto_qualify and new_score >= min_score_to_qualify:
                            # Verificar si ya está en pipeline
                            cur.execute("""
                                SELECT id FROM sales_pipeline WHERE lead_ext_id = %s
                            """, (lead_ext_id,))
                            
                            if not cur.fetchone():
                                # Insertar en pipeline de ventas
                                cur.execute("""
                                    INSERT INTO sales_pipeline 
                                    (lead_ext_id, email, first_name, last_name, phone, score, priority, 
                                     source, utm_source, utm_campaign, stage, qualified_at)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'qualified', NOW())
                                    ON CONFLICT (lead_ext_id) DO UPDATE SET
                                        score = EXCLUDED.score,
                                        priority = EXCLUDED.priority,
                                        updated_at = NOW()
                                """, (
                                    lead_ext_id,
                                    lead.get("email"),
                                    lead.get("first_name"),
                                    lead.get("last_name"),
                                    lead.get("phone"),
                                    new_score,
                                    new_priority,
                                    lead.get("source"),
                                    lead.get("utm_source"),
                                    lead.get("utm_campaign")
                                ))
                                
                                stats["qualifications"] += 1
                                logger.info(f"Lead {lead_ext_id} calificado automáticamente para ventas")
                        
                    except Exception as e:
                        logger.error(f"Error actualizando score para {lead.get('ext_id')}: {e}", exc_info=True)
                        continue
            
            conn.commit()
        
        logger.info(f"Actualizados {stats['updated']} leads. "
                   f"Calificaciones: {stats['qualifications']}, "
                   f"Cambios de prioridad: {stats['priority_changes']}")
        
        try:
            Stats.incr("lead_scoring.leads_updated", stats["updated"])
            Stats.incr("lead_scoring.leads_qualified", stats["qualifications"])
        except Exception:
            pass
        
        return stats
    
    @task(task_id="analyze_scoring_trends")
    def analyze_scoring_trends(stats: Dict[str, int]) -> Dict[str, Any]:
        """Analiza tendencias de scoring."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                # Tendencias últimas 24 horas
                cur.execute("""
                    SELECT 
                        COUNT(*) AS total_changes,
                        AVG(score_change) AS avg_score_change,
                        COUNT(*) FILTER (WHERE score_change > 0) AS increases,
                        COUNT(*) FILTER (WHERE score_change < 0) AS decreases,
                        AVG(score) AS avg_score
                    FROM lead_score_history
                    WHERE calculated_at >= NOW() - INTERVAL '24 hours'
                """)
                
                row = cur.fetchone()
                trends = {
                    "last_24h": {
                        "total_changes": row[0] or 0,
                        "avg_score_change": float(row[1] or 0),
                        "increases": row[2] or 0,
                        "decreases": row[3] or 0,
                        "avg_score": float(row[4] or 0)
                    }
                }
                
                # Distribución de scores actuales
                cur.execute("""
                    SELECT 
                        COUNT(*) FILTER (WHERE score >= 50) AS high_score,
                        COUNT(*) FILTER (WHERE score >= 35 AND score < 50) AS medium_score,
                        COUNT(*) FILTER (WHERE score < 35) AS low_score,
                        COUNT(*) FILTER (WHERE score IS NULL) AS no_score,
                        AVG(score) AS avg_score_overall
                    FROM leads
                    WHERE email IS NOT NULL
                """)
                
                row = cur.fetchone()
                trends["distribution"] = {
                    "high_score": row[0] or 0,
                    "medium_score": row[1] or 0,
                    "low_score": row[2] or 0,
                    "no_score": row[3] or 0,
                    "avg_score_overall": float(row[4] or 0) if row[4] else None
                }
        
        logger.info(f"Análisis de tendencias completado: {trends}")
        return trends
    
    @task(task_id="notify_summary")
    def notify_summary(stats: Dict[str, int], trends: Dict[str, Any]) -> None:
        """Envía resumen a Slack si está configurado."""
        ctx = get_current_context()
        params = ctx["params"]
        slack_url = str(params["slack_webhook_url"]).strip()
        
        if not slack_url:
            return
        
        try:
            import requests
            
            summary = f"""
🎯 *Lead Scoring Automation - Resumen*
            
📊 *Procesados:* {stats['updated']} leads
⬆️ *Aumentos de score:* {stats['score_increases']}
⬇️ *Decreases:* {stats['score_decreases']}
🎖️ *Nuevas calificaciones:* {stats['qualifications']}
🔄 *Cambios de prioridad:* {stats['priority_changes']}

📈 *Tendencias (24h):*
• Cambios totales: {trends['last_24h']['total_changes']}
• Cambio promedio: {trends['last_24h']['avg_score_change']:.1f} puntos
• Score promedio: {trends['last_24h']['avg_score']:.1f}

📊 *Distribución actual:*
• Alta (50+): {trends['distribution']['high_score']}
• Media (35-49): {trends['distribution']['medium_score']}
• Baja (<35): {trends['distribution']['low_score']}
            """
            
            requests.post(
                slack_url,
                json={"text": summary},
                timeout=10
            )
        except Exception as e:
            logger.warning(f"Error enviando notificación Slack: {e}")
    
    def get_ml_prediction(lead: Dict[str, Any], endpoint: str) -> Optional[int]:
        """Obtiene predicción de score desde modelo ML."""
        try:
            import requests
            
            payload = {
                "email": lead.get("email"),
                "source": lead.get("source"),
                "engagement_replies": lead.get("engagement_replies", 0),
                "engagement_clicks": lead.get("engagement_clicks", 0),
                "engagement_opens": lead.get("engagement_opens", 0),
                "days_since_created": lead.get("days_since_created", 0)
            }
            
            response = requests.post(
                endpoint,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            result = response.json()
            return result.get("predicted_score")
        except Exception as e:
            logger.warning(f"Error obteniendo predicción ML: {e}")
            return None
    
    # Pipeline
    schema_ok = ensure_schema()
    leads = get_leads_to_score()
    scored = calculate_scores(leads)
    stats = update_scores_and_history(scored)
    trends = analyze_scoring_trends(stats)
    notify_summary(stats, trends)


dag = lead_scoring_automation()





