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
    dag_id="lead_segmentation",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Segmentación Automática de Leads
    
    Segmenta automáticamente leads en categorías para personalización:
    - Por industria/empresa
    - Por tamaño de empresa
    - Por comportamiento
    - Por fuente
    - Por score y prioridad
    - Por etapa del pipeline
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `max_leads_per_run`: Máximo de leads a segmentar (default: 500)
    - `auto_assign_segments`: Asignar segmentos automáticamente (default: true)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_leads_per_run": Param(500, type="integer", minimum=1, maximum=5000),
        "auto_assign_segments": Param(True, type="boolean"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "segmentation", "automation"],
)
def lead_segmentation() -> None:
    """
    DAG para segmentación automática de leads.
    """
    
    @task(task_id="get_leads_to_segment")
    def get_leads_to_segment() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan segmentación."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        query = """
            SELECT 
                p.id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.company,
                p.score,
                p.priority,
                p.stage,
                p.source,
                p.utm_source,
                p.utm_campaign,
                p.estimated_value,
                p.metadata
            FROM sales_pipeline p
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.metadata->>'segment' IS NULL
                    OR p.updated_at > COALESCE((p.metadata->>'segmented_at')::timestamp, p.created_at)
                )
            ORDER BY p.priority DESC, p.score DESC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(leads)} leads para segmentar")
        return leads
    
    @task(task_id="segment_leads")
    def segment_leads(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Segmenta leads en categorías."""
        segmented_leads = []
        
        for lead in leads:
            segments = calculate_segments(lead)
            lead["segments"] = segments
            lead["primary_segment"] = determine_primary_segment(segments)
            segmented_leads.append(lead)
        
        logger.info(f"Segmentados {len(segmented_leads)} leads")
        return segmented_leads
    
    @task(task_id="save_segments")
    def save_segments(segmented_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Guarda segmentos en la base de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"segmented": 0, "errors": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in segmented_leads:
                    try:
                        segments = lead.get("segments", {})
                        primary_segment = lead.get("primary_segment")
                        
                        if not dry_run:
                            existing_metadata = lead.get("metadata") or {}
                            if isinstance(existing_metadata, str):
                                existing_metadata = json.loads(existing_metadata)
                            
                            updated_metadata = {
                                **existing_metadata,
                                "segments": segments,
                                "segment": primary_segment,
                                "segmented_at": datetime.utcnow().isoformat()
                            }
                            
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    metadata = %s::jsonb,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (json.dumps(updated_metadata), lead["id"]))
                            
                            conn.commit()
                            stats["segmented"] += 1
                            
                            logger.info(f"Lead {lead['lead_ext_id']} segmentado: {primary_segment}")
                        else:
                            logger.info(f"[DRY RUN] Lead {lead['lead_ext_id']} sería segmentado: {primary_segment}")
                    
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error segmentando lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Segmentación completada: {stats}")
        return stats
    
    def calculate_segments(lead: Dict[str, Any]) -> Dict[str, Any]:
        """Calcula todos los segmentos para un lead."""
        segments = {}
        
        # Segmento por score
        score = lead.get("score", 0)
        if score >= 80:
            segments["score_tier"] = "premium"
        elif score >= 60:
            segments["score_tier"] = "high"
        elif score >= 40:
            segments["score_tier"] = "medium"
        else:
            segments["score_tier"] = "low"
        
        # Segmento por prioridad
        segments["priority"] = lead.get("priority", "low")
        
        # Segmento por fuente
        source = lead.get("source", "unknown")
        utm_source = lead.get("utm_source", "")
        if utm_source:
            segments["source_type"] = "paid" if utm_source in ["google", "facebook", "linkedin"] else "organic"
        else:
            segments["source_type"] = "organic" if source in ["organic", "direct", "referral"] else "unknown"
        
        # Segmento por etapa
        segments["stage"] = lead.get("stage", "qualified")
        
        # Segmento por tamaño de empresa (estimado)
        company = lead.get("company", "")
        estimated_value = lead.get("estimated_value", 0)
        if estimated_value and estimated_value > 100000:
            segments["company_size"] = "enterprise"
        elif estimated_value and estimated_value > 50000:
            segments["company_size"] = "mid-market"
        elif company:
            segments["company_size"] = "small_business"
        else:
            segments["company_size"] = "unknown"
        
        # Segmento por comportamiento
        metadata = lead.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        if metadata.get("enrichment", {}).get("email_validation", {}).get("is_enterprise"):
            segments["behavior"] = "enterprise_contact"
        elif metadata.get("enrichment"):
            segments["behavior"] = "engaged"
        else:
            segments["behavior"] = "new"
        
        # Segmento por industria (si está disponible)
        company_info = metadata.get("enrichment", {}).get("company_info", {})
        if company_info.get("industry"):
            segments["industry"] = company_info["industry"]
        
        return segments
    
    def determine_primary_segment(segments: Dict[str, Any]) -> str:
        """Determina el segmento principal."""
        # Prioridad: score_tier > priority > company_size
        if segments.get("score_tier") == "premium":
            return f"premium_{segments.get('stage', 'qualified')}"
        elif segments.get("priority") == "high":
            return f"high_priority_{segments.get('stage', 'qualified')}"
        elif segments.get("company_size") == "enterprise":
            return f"enterprise_{segments.get('stage', 'qualified')}"
        else:
            return f"{segments.get('score_tier', 'medium')}_{segments.get('stage', 'qualified')}"
    
    # Pipeline
    leads = get_leads_to_segment()
    segmented_leads = segment_leads(leads)
    stats = save_segments(segmented_leads)


dag = lead_segmentation()

