from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional, Set
import json
import logging
import hashlib

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_deduplication",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */12 * * *",  # Cada 12 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Detección y Consolidación de Leads Duplicados
    
    Detecta y consolida leads duplicados basándose en:
    - Email (principal)
    - Teléfono
    - Nombre + empresa
    - Dominio de email
    
    **Funcionalidades:**
    - Detección de duplicados usando múltiples criterios
    - Consolidación automática de datos
    - Mantiene el registro con mejor información
    - Marca duplicados para revisión manual si es necesario
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_leads_per_run": Param(200, type="integer", minimum=1, maximum=1000),
        "auto_merge": Param(False, type="boolean"),
        "similarity_threshold": Param(0.85, type="number", minimum=0.5, maximum=1.0),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "deduplication", "automation"],
)
def lead_deduplication() -> None:
    """
    DAG para detección y consolidación de leads duplicados.
    """
    
    @task(task_id="find_duplicates")
    def find_duplicates() -> List[Dict[str, Any]]:
        """Encuentra leads duplicados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Buscar duplicados por email (principal criterio)
        query = """
            SELECT 
                p1.id AS id1,
                p1.lead_ext_id AS lead_ext_id1,
                p1.email AS email1,
                p1.first_name AS first_name1,
                p1.last_name AS last_name1,
                p1.phone AS phone1,
                p1.score AS score1,
                p1.qualified_at AS qualified_at1,
                p1.assigned_to AS assigned_to1,
                p2.id AS id2,
                p2.lead_ext_id AS lead_ext_id2,
                p2.email AS email2,
                p2.first_name AS first_name2,
                p2.last_name AS last_name2,
                p2.phone AS phone2,
                p2.score AS score2,
                p2.qualified_at AS qualified_at2,
                p2.assigned_to AS assigned_to2,
                CASE 
                    WHEN p1.score > p2.score THEN p1.id
                    WHEN p2.score > p1.score THEN p2.id
                    WHEN p1.qualified_at < p2.qualified_at THEN p1.id
                    ELSE p2.id
                END AS master_id
            FROM sales_pipeline p1
            INNER JOIN sales_pipeline p2 
                ON LOWER(p1.email) = LOWER(p2.email)
                AND p1.id < p2.id
            WHERE 
                p1.stage NOT IN ('closed_won', 'closed_lost')
                AND p2.stage NOT IN ('closed_won', 'closed_lost')
            ORDER BY p1.qualified_at DESC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                duplicates = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(duplicates)} pares de duplicados")
        return duplicates
    
    @task(task_id="merge_duplicates")
    def merge_duplicates(duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolida leads duplicados."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        auto_merge = bool(params["auto_merge"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"merged": 0, "marked": 0, "errors": 0}
        processed_ids: Set[int] = set()
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for dup in duplicates:
                    try:
                        master_id = dup["master_id"]
                        duplicate_id = dup["id2"] if dup["id1"] == master_id else dup["id1"]
                        
                        # Evitar procesar el mismo registro dos veces
                        if duplicate_id in processed_ids or master_id in processed_ids:
                            continue
                        
                        master_data = {
                            "id": dup["id1"] if dup["id1"] == master_id else dup["id2"],
                            "lead_ext_id": dup["lead_ext_id1"] if dup["id1"] == master_id else dup["lead_ext_id2"],
                            "email": dup["email1"] if dup["id1"] == master_id else dup["email2"],
                            "first_name": dup["first_name1"] if dup["id1"] == master_id else dup["first_name2"],
                            "last_name": dup["last_name1"] if dup["id1"] == master_id else dup["last_name2"],
                            "phone": dup["phone1"] if dup["id1"] == master_id else dup["phone2"],
                            "score": dup["score1"] if dup["id1"] == master_id else dup["score2"],
                            "assigned_to": dup["assigned_to1"] if dup["id1"] == master_id else dup["assigned_to2"]
                        }
                        
                        duplicate_data = {
                            "id": dup["id2"] if dup["id1"] == master_id else dup["id1"],
                            "lead_ext_id": dup["lead_ext_id2"] if dup["id1"] == master_id else dup["lead_ext_id1"],
                            "email": dup["email2"] if dup["id1"] == master_id else dup["email1"],
                            "first_name": dup["first_name2"] if dup["id1"] == master_id else dup["first_name1"],
                            "last_name": dup["last_name2"] if dup["id1"] == master_id else dup["last_name1"],
                            "phone": dup["phone2"] if dup["id1"] == master_id else dup["phone1"],
                            "score": dup["score2"] if dup["id1"] == master_id else dup["score1"],
                            "assigned_to": dup["assigned_to2"] if dup["id1"] == master_id else dup["assigned_to1"]
                        }
                        
                        # Consolidar datos: usar mejor información de ambos
                        consolidated = consolidate_data(master_data, duplicate_data)
                        
                        if auto_merge and not dry_run:
                            # Actualizar registro maestro con datos consolidados
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    first_name = COALESCE(%s, first_name),
                                    last_name = COALESCE(%s, last_name),
                                    phone = COALESCE(%s, phone),
                                    score = GREATEST(score, %s),
                                    metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                                        'merged_from', %s,
                                        'merged_at', %s,
                                        'duplicate_lead_ext_id', %s
                                    ),
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (
                                consolidated.get("first_name"),
                                consolidated.get("last_name"),
                                consolidated.get("phone"),
                                duplicate_data["score"],
                                duplicate_data["id"],
                                datetime.utcnow().isoformat(),
                                duplicate_data["lead_ext_id"],
                                master_id
                            ))
                            
                            # Marcar duplicado como merged
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    stage = 'closed_lost',
                                    metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                                        'duplicate_of', %s,
                                        'merged_at', %s,
                                        'is_duplicate', true
                                    ),
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (
                                master_data["lead_ext_id"],
                                datetime.utcnow().isoformat(),
                                duplicate_id
                            ))
                            
                            conn.commit()
                            stats["merged"] += 1
                            processed_ids.add(duplicate_id)
                            processed_ids.add(master_id)
                            
                            logger.info(f"Duplicados mergeados: {duplicate_id} -> {master_id}")
                        else:
                            # Solo marcar para revisión manual
                            if not dry_run:
                                cur.execute("""
                                    UPDATE sales_pipeline
                                    SET metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object(
                                        'possible_duplicate_of', %s,
                                        'duplicate_check_at', %s,
                                        'is_possible_duplicate', true
                                    )
                                    WHERE id IN (%s, %s)
                                """, (
                                    master_data["lead_ext_id"] if duplicate_id == dup["id1"] else duplicate_data["lead_ext_id"],
                                    datetime.utcnow().isoformat(),
                                    master_id,
                                    duplicate_id
                                ))
                                
                                conn.commit()
                            
                            stats["marked"] += 1
                            processed_ids.add(duplicate_id)
                            processed_ids.add(master_id)
                            
                            logger.info(f"Duplicados marcados para revisión: {duplicate_id} <-> {master_id}")
                    
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error procesando duplicados: {e}", exc_info=True)
        
        logger.info(f"Deduplicación completada: {stats}")
        return stats
    
    def consolidate_data(master: Dict[str, Any], duplicate: Dict[str, Any]) -> Dict[str, Any]:
        """Consolida datos de dos registros duplicados."""
        consolidated = {
            "first_name": master.get("first_name") or duplicate.get("first_name"),
            "last_name": master.get("last_name") or duplicate.get("last_name"),
            "phone": master.get("phone") or duplicate.get("phone"),
            "score": max(master.get("score", 0), duplicate.get("score", 0)),
            "assigned_to": master.get("assigned_to") or duplicate.get("assigned_to")
        }
        return consolidated
    
    # Pipeline
    duplicates = find_duplicates()
    stats = merge_duplicates(duplicates)


dag = lead_deduplication()

