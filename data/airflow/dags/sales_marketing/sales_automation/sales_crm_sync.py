from __future__ import annotations

from datetime import timedelta, datetime
from typing import Any, Dict, List, Optional
import json
import logging

import pendulum
import requests
from airflow.decorators import dag, task
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.stats import Stats
from airflow.providers.postgres.hooks.postgres import PostgresHook

logger = logging.getLogger(__name__)


@dag(
    dag_id="sales_crm_sync",
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
    ### Sincronización con CRM (HubSpot/Salesforce)
    
    Sincroniza leads calificados y pipeline de ventas con CRM externo:
    - Exporta nuevos leads calificados a CRM
    - Actualiza etapas y campos en CRM
    - Importa cambios desde CRM (si aplica)
    - Sincronización bidireccional opcional
    
    **Soporta:** HubSpot, Salesforce (configurable)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "crm_type": Param("hubspot", type="string", enum=["hubspot", "salesforce"]),
        "crm_api_key": Param("", type="string", minLength=1),
        "crm_api_url": Param("", type="string"),
        "sync_direction": Param("export", type="string", enum=["export", "import", "bidirectional"]),
        "max_leads_per_run": Param(100, type="integer", minimum=1, maximum=500),
        "dry_run": Param(False, type="boolean"),
        "request_timeout": Param(30, type="integer", minimum=5, maximum=120),
    },
    tags=["sales", "crm", "sync", "integration"],
)
def sales_crm_sync() -> None:
    """
    DAG para sincronización con CRM.
    """
    
    @task(task_id="get_leads_to_sync")
    def get_leads_to_sync() -> List[Dict[str, Any]]:
        """Obtiene leads que necesitan sincronización."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_leads = int(params["max_leads_per_run"])
        sync_direction = str(params["sync_direction"])
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Para export: leads que no han sido sincronizados
        if sync_direction in ["export", "bidirectional"]:
            query = """
                SELECT 
                    p.id AS pipeline_id,
                    p.lead_ext_id,
                    p.email,
                    p.first_name,
                    p.last_name,
                    p.phone,
                    p.score,
                    p.priority,
                    p.stage,
                    p.source,
                    p.utm_source,
                    p.utm_campaign,
                    p.estimated_value,
                    p.probability_pct,
                    p.assigned_to,
                    p.qualified_at,
                    p.metadata->>'crm_id' AS crm_id,
                    p.metadata->>'crm_synced_at' AS crm_synced_at
                FROM sales_pipeline p
                WHERE 
                    p.qualified_at >= NOW() - INTERVAL '90 days'
                    AND (
                        p.metadata->>'crm_id' IS NULL
                        OR p.metadata->>'crm_synced_at' IS NULL
                        OR (p.updated_at > (p.metadata->>'crm_synced_at')::timestamptz)
                    )
                ORDER BY p.priority DESC, p.qualified_at DESC
                LIMIT %s
            """
        else:
            # Para import: no implementado en esta versión
            return []
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_leads,))
                columns = [desc[0] for desc in cur.description]
                leads = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(leads)} leads para sincronizar")
        return leads
    
    @task(task_id="sync_to_crm")
    def sync_to_crm(leads: List[Dict[str, Any]]) -> Dict[str, int]:
        """Sincroniza leads a CRM."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        crm_type = str(params["crm_type"])
        crm_api_key = str(params["crm_api_key"]).strip()
        crm_api_url = str(params["crm_api_url"]).strip()
        dry_run = bool(params["dry_run"])
        timeout = int(params["request_timeout"])
        
        if not crm_api_key or not crm_api_url:
            logger.warning("CRM API key o URL no configurados, saltando sincronización")
            return {"synced": 0, "errors": 0, "skipped": len(leads)}
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        stats = {"synced": 0, "errors": 0, "skipped": 0}
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                for lead in leads:
                    try:
                        # Si ya tiene CRM ID, actualizar; sino, crear
                        crm_id = lead.get("crm_id")
                        
                        if crm_type == "hubspot":
                            result = sync_to_hubspot(
                                lead, crm_id, crm_api_url, crm_api_key, timeout, dry_run
                            )
                        elif crm_type == "salesforce":
                            result = sync_to_salesforce(
                                lead, crm_id, crm_api_url, crm_api_key, timeout, dry_run
                            )
                        else:
                            logger.warning(f"Tipo de CRM no soportado: {crm_type}")
                            stats["skipped"] += 1
                            continue
                        
                        if result and result.get("success"):
                            # Actualizar metadata en pipeline
                            if not dry_run:
                                metadata = lead.get("metadata") or {}
                                if isinstance(metadata, str):
                                    metadata = json.loads(metadata)
                                
                                metadata["crm_id"] = result.get("crm_id", crm_id)
                                metadata["crm_synced_at"] = datetime.utcnow().isoformat()
                                metadata["crm_type"] = crm_type
                                
                                cur.execute("""
                                    UPDATE sales_pipeline
                                    SET metadata = %s,
                                        updated_at = NOW()
                                    WHERE id = %s
                                """, (json.dumps(metadata), lead["pipeline_id"]))
                                
                                conn.commit()
                            
                            stats["synced"] += 1
                            logger.info(f"Lead {lead['lead_ext_id']} sincronizado a CRM")
                        else:
                            stats["errors"] += 1
                            
                    except Exception as e:
                        logger.error(f"Error sincronizando lead {lead.get('lead_ext_id')}: {e}", exc_info=True)
                        stats["errors"] += 1
                        continue
        
        logger.info(f"Sincronizados: {stats['synced']}, Errores: {stats['errors']}, Saltados: {stats['skipped']}")
        
        try:
            Stats.incr("sales_crm_sync.synced", stats["synced"])
            Stats.incr("sales_crm_sync.errors", stats["errors"])
        except Exception:
            pass
        
        return stats
    
    def sync_to_hubspot(lead: Dict[str, Any], crm_id: Optional[str],
                       api_url: str, api_key: str, timeout: int, dry_run: bool) -> Dict[str, Any]:
        """Sincroniza lead a HubSpot."""
        try:
            # Mapear stage a lifecycle stage de HubSpot
            stage_mapping = {
                "qualified": "qualified",
                "contacted": "contacted",
                "meeting_scheduled": "meeting_scheduled",
                "proposal_sent": "proposal_sent",
                "negotiating": "negotiating",
                "closed_won": "customer",
                "closed_lost": "closed_lost"
            }
            
            lifecycle_stage = stage_mapping.get(lead.get("stage", "qualified"), "qualified")
            
            # Preparar propiedades
            properties = {
                "email": lead.get("email"),
                "firstname": lead.get("first_name"),
                "lastname": lead.get("last_name"),
                "phone": lead.get("phone"),
                "lifecyclestage": lifecycle_stage,
                "hs_lead_status": "QUALIFIED",
                "lead_score": str(lead.get("score", 0)),
                "lead_source": lead.get("source", ""),
                "utm_source": lead.get("utm_source", ""),
                "utm_campaign": lead.get("utm_campaign", ""),
                "deal_value": str(lead.get("estimated_value", 0) or 0),
                "deal_probability": str(lead.get("probability_pct", 0) or 0),
            }
            
            # Eliminar propiedades vacías
            properties = {k: v for k, v in properties.items() if v}
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            if crm_id:
                # Actualizar contacto existente
                url = f"{api_url}/crm/v3/objects/contacts/{crm_id}"
                method = "PATCH"
            else:
                # Crear nuevo contacto
                url = f"{api_url}/crm/v3/objects/contacts"
                method = "POST"
            
            if dry_run:
                logger.info(f"[DRY RUN] {method} {url} con propiedades: {properties}")
                return {"success": True, "crm_id": crm_id or "dry_run_id"}
            
            response = requests.request(
                method,
                url,
                json={"properties": properties},
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            new_crm_id = result.get("id") or crm_id
            
            # Si hay deal value, crear/actualizar deal
            if lead.get("estimated_value") and lead.get("estimated_value") > 0:
                create_hubspot_deal(
                    new_crm_id, lead, api_url, api_key, timeout, dry_run
                )
            
            return {"success": True, "crm_id": new_crm_id}
            
        except Exception as e:
            logger.error(f"Error en sync a HubSpot: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    def create_hubspot_deal(contact_id: str, lead: Dict[str, Any],
                           api_url: str, api_key: str, timeout: int, dry_run: bool) -> None:
        """Crea o actualiza deal en HubSpot."""
        try:
            deal_name = f"{lead.get('first_name', '')} {lead.get('last_name', '')} - Deal".strip()
            if not deal_name:
                deal_name = f"Deal for {lead.get('email', '')}"
            
            deal_properties = {
                "dealname": deal_name,
                "amount": str(lead.get("estimated_value", 0)),
                "dealstage": lead.get("stage", "qualified"),
                "pipeline": "default",
                "closedate": (datetime.utcnow() + timedelta(days=30)).isoformat(),
            }
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            if dry_run:
                logger.info(f"[DRY RUN] Crear deal en HubSpot: {deal_properties}")
                return
            
            # Crear deal
            response = requests.post(
                f"{api_url}/crm/v3/objects/deals",
                json={"properties": deal_properties},
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            deal_id = response.json().get("id")
            
            # Asociar deal con contacto
            if deal_id:
                requests.put(
                    f"{api_url}/crm/v3/objects/deals/{deal_id}/associations/contacts/{contact_id}/0",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=timeout
                )
            
        except Exception as e:
            logger.warning(f"Error creando deal en HubSpot: {e}")
    
    def sync_to_salesforce(lead: Dict[str, Any], crm_id: Optional[str],
                          api_url: str, api_key: str, timeout: int, dry_run: bool) -> Dict[str, Any]:
        """Sincroniza lead a Salesforce."""
        try:
            # Mapear stage a stage de Salesforce
            stage_mapping = {
                "qualified": "Qualified",
                "contacted": "Contacted",
                "meeting_scheduled": "Meeting Scheduled",
                "proposal_sent": "Proposal Sent",
                "negotiating": "Negotiating",
                "closed_won": "Closed Won",
                "closed_lost": "Closed Lost"
            }
            
            stage = stage_mapping.get(lead.get("stage", "qualified"), "Qualified")
            
            # Preparar datos
            lead_data = {
                "Email": lead.get("email"),
                "FirstName": lead.get("first_name"),
                "LastName": lead.get("last_name"),
                "Phone": lead.get("phone"),
                "LeadSource": lead.get("source", ""),
                "Company": lead.get("metadata", {}).get("company", "") if isinstance(lead.get("metadata"), dict) else "",
                "Status": "Qualified",
                "Rating": "Hot" if lead.get("priority") == "high" else "Warm"
            }
            
            # Eliminar campos vacíos
            lead_data = {k: v for k, v in lead_data.items() if v}
            
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            if crm_id:
                # Actualizar lead existente
                url = f"{api_url}/services/data/v57.0/sobjects/Lead/{crm_id}"
                method = "PATCH"
            else:
                # Crear nuevo lead
                url = f"{api_url}/services/data/v57.0/sobjects/Lead"
                method = "POST"
            
            if dry_run:
                logger.info(f"[DRY RUN] {method} {url} con datos: {lead_data}")
                return {"success": True, "crm_id": crm_id or "dry_run_id"}
            
            response = requests.request(
                method,
                url,
                json=lead_data,
                headers=headers,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            new_crm_id = result.get("id") or crm_id
            
            return {"success": True, "crm_id": new_crm_id}
            
        except Exception as e:
            logger.error(f"Error en sync a Salesforce: {e}", exc_info=True)
            return {"success": False, "error": str(e)}
    
    # Pipeline
    leads_to_sync = get_leads_to_sync()
    sync_stats = sync_to_crm(leads_to_sync)


dag = sales_crm_sync()

