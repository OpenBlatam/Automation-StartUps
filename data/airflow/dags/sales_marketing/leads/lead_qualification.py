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
    dag_id="lead_qualification",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */3 * * *",  # Cada 3 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Qualificación Automática de Leads (BANT)
    
    Qualifica automáticamente leads usando criterios BANT:
    - **Budget**: ¿Tiene presupuesto?
    - **Authority**: ¿Tiene autoridad para decidir?
    - **Need**: ¿Tiene necesidad real?
    - **Timeline**: ¿Cuándo necesita la solución?
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `bant_threshold`: Umbral mínimo para considerar qualificado (default: 3)
    - `auto_qualify_enabled`: Qualificar automáticamente (default: true)
    - `max_leads_per_run`: Máximo de leads a procesar (default: 100)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "bant_threshold": Param(3, type="integer", minimum=1, maximum=4),
        "auto_qualify_enabled": Param(True, type="boolean"),
        "max_leads_per_run": Param(100, type="integer", minimum=1, maximum=500),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "qualification", "bant", "automation"],
)
def lead_qualification() -> None:
    """
    DAG para qualificación automática de leads usando BANT.
    """
    
    @task(task_id="get_leads_to_qualify")
    def get_leads_to_qualify() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan qualificación."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Leads que no han sido qualificados o necesitan re-qualificación
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
                p.estimated_value,
                p.probability_pct,
                p.notes,
                p.metadata
            FROM sales_pipeline p
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.metadata->>'bant_qualified' IS NULL
                    OR p.metadata->>'bant_qualified' = 'false'
                    OR p.updated_at > COALESCE((p.metadata->>'bant_qualified_at')::timestamp, p.created_at)
                )
            ORDER BY 
                p.priority DESC,
                p.score DESC,
                p.qualified_at DESC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(leads)} leads para qualificar")
        return leads
    
    @task(task_id="calculate_bant_scores")
    def calculate_bant_scores(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Calcula scores BANT para cada lead."""
        ctx = get_current_context()
        threshold = int(ctx["params"]["bant_threshold"])
        
        qualified_leads = []
        
        for lead in leads:
            bant_scores = evaluate_bant(lead)
            total_bant = sum(bant_scores.values())
            
            lead["bant_scores"] = bant_scores
            lead["bant_total"] = total_bant
            lead["bant_qualified"] = total_bant >= threshold
            
            qualified_leads.append(lead)
        
        return qualified_leads
    
    @task(task_id="save_qualification")
    def save_qualification(qualified_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Guarda resultados de qualificación."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        auto_qualify = bool(params["auto_qualify_enabled"])
        dry_run = bool(params["dry_run"])
        threshold = int(params["bant_threshold"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"qualified": 0, "updated": 0, "errors": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in qualified_leads:
                    try:
                        bant_scores = lead.get("bant_scores", {})
                        bant_total = lead.get("bant_total", 0)
                        is_qualified = bant_total >= threshold
                        
                        if not dry_run:
                            existing_metadata = lead.get("metadata") or {}
                            if isinstance(existing_metadata, str):
                                existing_metadata = json.loads(existing_metadata)
                            
                            updated_metadata = {
                                **existing_metadata,
                                "bant": bant_scores,
                                "bant_total": bant_total,
                                "bant_qualified": is_qualified,
                                "bant_qualified_at": datetime.utcnow().isoformat()
                            }
                            
                            # Actualizar stage si está qualificado
                            new_stage = lead.get("stage")
                            if is_qualified and auto_qualify:
                                if lead.get("stage") == "qualified":
                                    new_stage = "contacted"  # Listo para contacto
                            
                            # Actualizar probability basado en BANT
                            new_probability = calculate_probability_from_bant(bant_total)
                            
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    stage = COALESCE(%s, stage),
                                    probability_pct = %s,
                                    metadata = %s::jsonb,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (new_stage, new_probability, json.dumps(updated_metadata), lead["id"]))
                            
                            conn.commit()
                            
                            if is_qualified:
                                stats["qualified"] += 1
                            stats["updated"] += 1
                            
                            logger.info(f"Lead {lead['lead_ext_id']} - BANT: {bant_total}/4, Qualified: {is_qualified}")
                        else:
                            logger.info(f"[DRY RUN] Lead {lead['lead_ext_id']} - BANT: {bant_total}/4")
                    
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error qualificando lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Qualificación completada: {stats}")
        return stats
    
    def evaluate_bant(lead: Dict[str, Any]) -> Dict[str, int]:
        """Evalúa criterios BANT para un lead."""
        bant = {"budget": 0, "authority": 0, "need": 0, "timeline": 0}
        
        metadata = lead.get("metadata") or {}
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        
        # Budget (1 punto si tiene estimated_value significativo)
        estimated_value = lead.get("estimated_value", 0)
        if estimated_value and estimated_value > 10000:
            bant["budget"] = 1
        elif estimated_value and estimated_value > 0:
            bant["budget"] = 0.5  # Presupuesto probable
        
        # Authority (1 punto si tiene título ejecutivo o empresa grande)
        company = lead.get("company", "")
        first_name = lead.get("first_name", "")
        last_name = lead.get("last_name", "")
        
        # Buscar señales de autoridad en metadata
        enrichment = metadata.get("enrichment", {})
        company_info = enrichment.get("company_info", {})
        
        # Si es empresa grande, probablemente tiene autoridad
        if company_info.get("company_size") == "enterprise":
            bant["authority"] = 1
        elif company:
            bant["authority"] = 0.5  # Probable autoridad
        
        # Need (1 punto si tiene mensaje, score alto, o engagement)
        notes = lead.get("notes", "")
        score = lead.get("score", 0)
        message = metadata.get("message", "")
        
        if (notes and len(notes) > 50) or (message and len(message) > 50):
            bant["need"] = 1
        elif score >= 70:  # Score alto indica necesidad
            bant["need"] = 1
        elif score >= 50:
            bant["need"] = 0.5
        
        # Timeline (1 punto si hay señales de urgencia)
        # Buscar en metadata o notes palabras clave
        urgency_keywords = ["urgent", "asap", "soon", "immediate", "quick", "pronto", "rápido"]
        text_content = ((notes or "") + " " + (metadata.get("message", "") or "")).lower()
        
        if any(keyword in text_content for keyword in urgency_keywords):
            bant["timeline"] = 1
        elif score >= 60:  # Score alto puede indicar timeline
            bant["timeline"] = 0.5
        
        return bant
    
    def calculate_probability_from_bant(bant_total: float) -> int:
        """Calcula probabilidad de cierre basada en BANT."""
        if bant_total >= 4:
            return 80
        elif bant_total >= 3:
            return 60
        elif bant_total >= 2:
            return 40
        elif bant_total >= 1:
            return 20
        else:
            return 10
    
    # Pipeline
    leads = get_leads_to_qualify()
    qualified_leads = calculate_bant_scores(leads)
    stats = save_qualification(qualified_leads)


dag = lead_qualification()

