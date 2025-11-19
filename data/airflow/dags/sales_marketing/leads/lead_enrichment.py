from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging
import re

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="lead_enrichment",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */4 * * *",  # Cada 4 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=5),
        "depends_on_past": False,
    },
    doc_md="""
    ### Enriquecimiento Automático de Leads
    
    Enriquece automáticamente los datos de leads con información adicional:
    - Validación de email y teléfono
    - Información de empresa (tamaño, industria, etc.)
    - Datos de redes sociales
    - Scoring avanzado
    - Detección de tecnologías usadas
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `max_leads_per_run`: Máximo de leads a enriquecer (default: 50)
    - `enable_email_validation`: Validar emails (default: true)
    - `enable_company_lookup`: Buscar información de empresa (default: true)
    - `enable_social_lookup`: Buscar en redes sociales (default: false)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "max_leads_per_run": Param(50, type="integer", minimum=1, maximum=500),
        "enable_email_validation": Param(True, type="boolean"),
        "enable_company_lookup": Param(True, type="boolean"),
        "enable_social_lookup": Param(False, type="boolean"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "leads", "enrichment", "automation"],
)
def lead_enrichment() -> None:
    """
    DAG para enriquecimiento automático de leads.
    """
    
    @task(task_id="get_leads_to_enrich")
    def get_leads_to_enrich() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan enriquecimiento."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Obtener leads que no han sido enriquecidos o que fueron actualizados recientemente
        query = """
            SELECT 
                p.id AS pipeline_id,
                p.lead_ext_id,
                p.email,
                p.first_name,
                p.last_name,
                p.phone,
                p.company,
                p.source,
                p.score,
                p.priority,
                p.metadata
            FROM sales_pipeline p
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.metadata->>'enriched' IS NULL
                    OR p.metadata->>'enriched' = 'false'
                    OR (p.metadata->>'enriched_at')::timestamp < NOW() - INTERVAL '30 days'
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
        
        logger.info(f"Encontrados {len(leads)} leads para enriquecer")
        return leads
    
    @task(task_id="enrich_lead_data")
    def enrich_lead_data(leads: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """ Enriquece datos de leads."""
        ctx = get_current_context()
        params = ctx["params"]
        enable_email_validation = bool(params["enable_email_validation"])
        enable_company_lookup = bool(params["enable_company_lookup"])
        enable_social_lookup = bool(params["enable_social_lookup"])
        
        enriched_leads = []
        
        for lead in leads:
            enrichment_data = {}
            
            # Validar email
            if enable_email_validation:
                email_validation = validate_email(lead["email"])
                enrichment_data["email_validation"] = email_validation
            
            # Buscar información de empresa
            if enable_company_lookup and lead.get("company"):
                company_info = lookup_company_info(lead["company"], lead.get("email"))
                enrichment_data["company_info"] = company_info
            
            # Buscar en redes sociales
            if enable_social_lookup and lead.get("email"):
                social_info = lookup_social_profiles(lead["email"])
                enrichment_data["social_profiles"] = social_info
            
            # Extraer dominio de email
            email_domain = extract_domain(lead["email"])
            if email_domain:
                enrichment_data["email_domain"] = email_domain
                enrichment_data["is_enterprise"] = is_enterprise_domain(email_domain)
            
            # Calcular score adicional basado en enriquecimiento
            enrichment_score = calculate_enrichment_score(enrichment_data)
            
            lead["enrichment_data"] = enrichment_data
            lead["enrichment_score"] = enrichment_score
            
            enriched_leads.append(lead)
        
        return enriched_leads
    
    @task(task_id="save_enrichment_data")
    def save_enrichment_data(enriched_leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Guarda datos enriquecidos en la base de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        dry_run = bool(params["dry_run"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"enriched": 0, "updated_score": 0, "errors": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in enriched_leads:
                    try:
                        enrichment_data = lead.get("enrichment_data", {})
                        enrichment_score = lead.get("enrichment_score", 0)
                        
                        # Actualizar metadata con datos enriquecidos
                        if not dry_run:
                            # Combinar metadata existente con nuevos datos
                            existing_metadata = lead.get("metadata") or {}
                            if isinstance(existing_metadata, str):
                                existing_metadata = json.loads(existing_metadata)
                            
                            updated_metadata = {
                                **existing_metadata,
                                "enrichment": enrichment_data,
                                "enriched": True,
                                "enriched_at": datetime.utcnow().isoformat(),
                                "enrichment_score": enrichment_score
                            }
                            
                            # Actualizar score si el enrichment score es mayor
                            new_score = lead.get("score", 0)
                            if enrichment_score > 0:
                                new_score = min(lead.get("score", 0) + enrichment_score, 100)
                            
                            cur.execute("""
                                UPDATE sales_pipeline
                                SET 
                                    metadata = %s::jsonb,
                                    score = %s,
                                    updated_at = NOW()
                                WHERE id = %s
                            """, (json.dumps(updated_metadata), new_score, lead["pipeline_id"]))
                            
                            conn.commit()
                            
                            stats["enriched"] += 1
                            if new_score > lead.get("score", 0):
                                stats["updated_score"] += 1
                            
                            logger.info(f"Lead {lead['lead_ext_id']} enriquecido (score: {new_score})")
                        else:
                            logger.info(f"[DRY RUN] Lead {lead['lead_ext_id']} sería enriquecido")
                    
                    except Exception as e:
                        stats["errors"] += 1
                        logger.error(f"Error enriqueciendo lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
        
        logger.info(f"Enriquecimiento completado: {stats}")
        return stats
    
    # Funciones auxiliares
    def validate_email(email: str) -> Dict[str, Any]:
        """Valida email usando servicios externos."""
        try:
            # Usar API de validación (ej: Abstract API, ZeroBounce, etc.)
            # Por ahora, validación básica
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            is_valid_format = bool(re.match(email_pattern, email))
            
            # Extraer dominio
            domain = email.split("@")[1] if "@" in email else None
            
            return {
                "is_valid": is_valid_format,
                "domain": domain,
                "is_disposable": is_disposable_email(domain) if domain else False,
                "is_enterprise": is_enterprise_domain(domain) if domain else False
            }
        except Exception as e:
            logger.error(f"Error validando email {email}: {e}")
            return {"is_valid": False, "error": str(e)}
    
    def lookup_company_info(company_name: str, email: Optional[str] = None) -> Dict[str, Any]:
        """Busca información de empresa usando APIs externas."""
        try:
            # Usar APIs como Clearbit, FullContact, etc.
            # Por ahora, retornar estructura básica
            domain = extract_domain(email) if email else None
            
            return {
                "company_name": company_name,
                "domain": domain,
                "industry": None,  # Se obtendría de API
                "company_size": None,  # Se obtendría de API
                "location": None,  # Se obtendría de API
                "technologies": [],  # Se obtendría de API
                "revenue": None  # Se obtendría de API
            }
        except Exception as e:
            logger.error(f"Error buscando info de empresa {company_name}: {e}")
            return {}
    
    def lookup_social_profiles(email: str) -> Dict[str, Any]:
        """Busca perfiles en redes sociales."""
        try:
            # Usar APIs como FullContact, Clearbit, etc.
            return {
                "linkedin": None,
                "twitter": None,
                "facebook": None,
                "github": None
            }
        except Exception as e:
            logger.error(f"Error buscando perfiles sociales {email}: {e}")
            return {}
    
    def extract_domain(email: str) -> Optional[str]:
        """Extrae dominio de email."""
        if "@" in email:
            return email.split("@")[1].lower()
        return None
    
    def is_disposable_email(domain: str) -> bool:
        """Verifica si es email desechable."""
        disposable_domains = [
            "tempmail.com", "10minutemail.com", "guerrillamail.com",
            "mailinator.com", "throwaway.email"
        ]
        return domain.lower() in disposable_domains
    
    def is_enterprise_domain(domain: str) -> bool:
        """Verifica si es dominio empresarial."""
        if not domain:
            return False
        
        # Dominios gubernamentales y educativos
        if domain.endswith(".gov") or domain.endswith(".edu"):
            return True
        
        # Dominios conocidos de empresas grandes
        enterprise_domains = [
            "microsoft.com", "google.com", "apple.com", "amazon.com",
            "facebook.com", "ibm.com", "oracle.com", "salesforce.com"
        ]
        
        return domain.lower() in enterprise_domains
    
    def calculate_enrichment_score(enrichment_data: Dict[str, Any]) -> int:
        """Calcula score adicional basado en datos enriquecidos."""
        score = 0
        
        # Email validation
        email_validation = enrichment_data.get("email_validation", {})
        if email_validation.get("is_valid"):
            score += 5
        if email_validation.get("is_enterprise"):
            score += 10
        if email_validation.get("is_disposable"):
            score -= 10
        
        # Company info
        company_info = enrichment_data.get("company_info", {})
        if company_info.get("company_size"):
            score += 5
        if company_info.get("revenue"):
            score += 5
        
        # Social profiles
        social_profiles = enrichment_data.get("social_profiles", {})
        if social_profiles.get("linkedin"):
            score += 5
        
        return min(max(score, -10), 20)  # Cap entre -10 y 20
    
    # Pipeline
    leads = get_leads_to_enrich()
    enriched_leads = enrich_lead_data(leads)
    stats = save_enrichment_data(enriched_leads)


dag = lead_enrichment()

