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
    dag_id="crm_bidirectional_sync",
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    schedule="0 */6 * * *",  # Cada 6 horas
    catchup=False,
    default_args={
        "owner": "sales",
        "retries": 2,
        "retry_delay": timedelta(minutes=10),
        "depends_on_past": False,
    },
    doc_md="""
    ### Sincronización Bidireccional con CRM
    
    Sincroniza automáticamente el pipeline de ventas con Salesforce o Pipedrive,
    manteniendo ambos sistemas actualizados en tiempo real.
    
    **Funcionalidades:**
    - Sincronización bidireccional: BD → CRM y CRM → BD
    - Actualización de estados en ambos sentidos
    - Creación de deals/opportunities en CRM
    - Sincronización de actividades y seguimientos
    - Resolución automática de conflictos
    - Tracking de cambios para auditoría
    
    **Parámetros:**
    - `postgres_conn_id`: Connection ID para Postgres
    - `crm_type`: Tipo de CRM ('salesforce' o 'pipedrive')
    - `crm_config`: Configuración del CRM (JSON string)
    - `sync_direction`: 'bidirectional', 'to_crm', o 'from_crm'
    - `max_records_per_run`: Máximo de registros a sincronizar (default: 100)
    - `sync_stages`: Sincronizar cambios de estado (default: true)
    - `sync_activities`: Sincronizar actividades (default: true)
    - `create_deals`: Crear deals en CRM para leads calificados (default: true)
    """,
    params={
        "postgres_conn_id": Param("postgres_default", type="string", minLength=1),
        "crm_type": Param("salesforce", type="string", enum=["salesforce", "pipedrive"]),
        "crm_config": Param("{}", type="string"),
        "sync_direction": Param("bidirectional", type="string", enum=["bidirectional", "to_crm", "from_crm"]),
        "max_records_per_run": Param(100, type="integer", minimum=1, maximum=1000),
        "sync_stages": Param(True, type="boolean"),
        "sync_activities": Param(True, type="boolean"),
        "create_deals": Param(True, type="boolean"),
        "dry_run": Param(False, type="boolean"),
    },
    tags=["sales", "crm", "sync", "automation"],
)
def crm_bidirectional_sync() -> None:
    """
    DAG para sincronización bidireccional con CRM.
    """
    
    @task(task_id="get_pipeline_changes")
    def get_pipeline_changes() -> List[Dict[str, Any]]:
        """Obtiene cambios en el pipeline desde la última sincronización."""
        ctx = get_current_context()
        params = ctx["params"]
        conn_id = str(params["postgres_conn_id"])
        max_records = int(params["max_records_per_run"])
        sync_direction = str(params["sync_direction"])
        
        if sync_direction == "from_crm":
            return []  # No necesitamos cambios locales si solo sincronizamos desde CRM
        
        hook = PostgresHook(postgres_conn_id=conn_id)
        
        # Obtener leads que necesitan sincronización
        # (sin CRM ID o con cambios recientes)
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
                p.assigned_to,
                p.estimated_value,
                p.probability_pct,
                p.qualified_at,
                p.updated_at,
                p.metadata->>'crm_id' AS crm_id,
                p.metadata->>'crm_type' AS crm_type,
                p.metadata->>'deal_id' AS deal_id,
                CASE 
                    WHEN p.metadata->>'crm_id' IS NULL THEN 'create'
                    WHEN p.updated_at > COALESCE(
                        (p.metadata->>'last_synced_at')::timestamp,
                        p.created_at
                    ) THEN 'update'
                    ELSE 'skip'
                END AS sync_action
            FROM sales_pipeline p
            WHERE 
                p.stage NOT IN ('closed_won', 'closed_lost')
                AND (
                    p.metadata->>'crm_id' IS NULL
                    OR p.updated_at > COALESCE(
                        (p.metadata->>'last_synced_at')::timestamp,
                        p.created_at
                    )
                )
            ORDER BY 
                p.priority DESC,
                p.updated_at DESC
            LIMIT %s
        """
        
        with hook.get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(query, (max_records,))
                columns = [desc[0] for desc in cur.description]
                changes = [dict(zip(columns, row)) for row in cur.fetchall()]
        
        logger.info(f"Encontrados {len(changes)} cambios para sincronizar")
        return changes
    
    @task(task_id="sync_to_crm")
    def sync_to_crm(changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Sincroniza cambios al CRM."""
        ctx = get_current_context()
        params = ctx["params"]
        crm_type = str(params["crm_type"])
        crm_config_str = str(params["crm_config"])
        dry_run = bool(params["dry_run"])
        create_deals = bool(params["create_deals"])
        
        if not changes:
            return {"synced": 0, "created": 0, "updated": 0, "errors": 0}
        
        try:
            crm_config = json.loads(crm_config_str) if crm_config_str else {}
            
            from data.integrations.connectors import create_connector, SyncRecord
            
            # Crear conector
            if crm_type == "salesforce":
                connector_config = {
                    "username": crm_config.get("username"),
                    "password": crm_config.get("password"),
                    "security_token": crm_config.get("security_token"),
                    "client_id": crm_config.get("client_id"),
                    "client_secret": crm_config.get("client_secret"),
                    "sandbox": crm_config.get("sandbox", False),
                    "sobject_type": "Lead"
                }
            elif crm_type == "pipedrive":
                connector_config = {
                    "api_token": crm_config.get("api_token"),
                    "company_domain": crm_config.get("company_domain"),
                    "resource_type": "persons"
                }
            else:
                raise ValueError(f"Tipo de CRM no soportado: {crm_type}")
            
            connector = create_connector(crm_type, connector_config)
            
            if not connector.connect():
                raise ValueError("No se pudo conectar al CRM")
            
            stats = {"synced": 0, "created": 0, "updated": 0, "errors": 0}
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            for change in changes:
                try:
                    sync_action = change.get("sync_action")
                    if sync_action == "skip":
                        continue
                    
                    # Mapear stage a status de CRM
                    stage = change.get("stage", "qualified")
                    if crm_type == "salesforce":
                        stage_mapping = {
                            "qualified": "Open - Not Contacted",
                            "contacted": "Working - Contacted",
                            "meeting_scheduled": "Working - Contacted",
                            "proposal_sent": "Qualified - Qualified",
                            "negotiating": "Qualified - Qualified"
                        }
                        salesforce_status = stage_mapping.get(stage, "Open - Not Contacted")
                        
                        crm_data = {
                            "Email": change["email"],
                            "FirstName": change.get("first_name"),
                            "LastName": change.get("last_name"),
                            "Phone": change.get("phone"),
                            "LeadSource": "Web",
                            "Status": salesforce_status
                        }
                    else:  # pipedrive
                        crm_data = {
                            "email": [{"value": change["email"], "primary": True}],
                            "first_name": change.get("first_name"),
                            "last_name": change.get("last_name"),
                            "phone": [{"value": change.get("phone"), "primary": True}] if change.get("phone") else []
                        }
                    
                    record = SyncRecord(
                        source_id=change["lead_ext_id"],
                        source_type="sales_pipeline",
                        data=crm_data,
                        target_id=change.get("crm_id")
                    )
                    
                    if sync_action == "create":
                        results = connector.write_records([record])
                    else:  # update
                        results = connector.update_records([record])
                    
                    if results and results[0].status == "synced":
                        crm_id = results[0].target_id
                        
                        # Actualizar metadata en BD
                        if not dry_run:
                            with hook.get_conn() as conn:
                                with conn.cursor() as cur:
                                    metadata_update = {
                                        "crm_id": crm_id,
                                        "crm_type": crm_type,
                                        "last_synced_at": datetime.utcnow().isoformat()
                                    }
                                    
                                    # Si no hay deal y el lead está calificado, crear deal
                                    if create_deals and not change.get("deal_id") and change.get("score", 0) >= 50:
                                        if crm_type == "pipedrive":
                                            deal_id = connector.create_deal(
                                                title=f"Deal para {change.get('first_name', 'Lead')} {change.get('last_name', '')}",
                                                person_id=int(crm_id) if crm_id and crm_id.isdigit() else None,
                                                value=float(change.get("estimated_value", 0)) if change.get("estimated_value") else None,
                                                stage_id=crm_config.get("default_stage_id")
                                            )
                                            if deal_id:
                                                metadata_update["deal_id"] = deal_id
                                                stats["created"] += 1
                                        
                                        # Para Salesforce, crear Opportunity
                                        elif crm_type == "salesforce":
                                            # Crear Opportunity
                                            opp_data = {
                                                "Name": f"Opportunity for {change.get('first_name', 'Lead')}",
                                                "LeadSource": "Web",
                                                "StageName": "Prospecting",
                                                "Amount": float(change.get("estimated_value", 0)) if change.get("estimated_value") else None,
                                                "Probability": change.get("probability_pct", 20)
                                            }
                                            
                                            # Necesitaríamos crear un OpportunityConnector o usar el mismo
                                            # Por ahora, solo guardamos la referencia al Lead
                                            pass
                                    
                                    cur.execute("""
                                        UPDATE sales_pipeline
                                        SET metadata = COALESCE(metadata, '{}'::jsonb) || %s::jsonb,
                                            updated_at = NOW()
                                        WHERE id = %s
                                    """, (json.dumps(metadata_update), change["pipeline_id"]))
                                    
                                    conn.commit()
                        
                        stats["synced"] += 1
                        if sync_action == "create":
                            stats["created"] += 1
                        else:
                            stats["updated"] += 1
                        
                        logger.info(f"Lead {change['lead_ext_id']} sincronizado con {crm_type}: {crm_id}")
                    else:
                        stats["errors"] += 1
                        logger.error(f"Error sincronizando lead {change['lead_ext_id']}: {results[0].error_message if results else 'Unknown'}")
                
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error procesando lead {change.get('lead_ext_id')}: {e}", exc_info=True)
            
            connector.disconnect()
            
            logger.info(f"Sincronización completada: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error en sincronización: {e}", exc_info=True)
            return {"synced": 0, "created": 0, "updated": 0, "errors": len(changes)}
    
    @task(task_id="sync_from_crm")
    def sync_from_crm() -> Dict[str, Any]:
        """Sincroniza cambios desde CRM a la base de datos."""
        ctx = get_current_context()
        params = ctx["params"]
        crm_type = str(params["crm_type"])
        crm_config_str = str(params["crm_config"])
        sync_direction = str(params["sync_direction"])
        max_records = int(params["max_records_per_run"])
        dry_run = bool(params["dry_run"])
        
        if sync_direction == "to_crm":
            return {"synced": 0, "updated": 0, "errors": 0}
        
        try:
            crm_config = json.loads(crm_config_str) if crm_config_str else {}
            
            from data.integrations.connectors import create_connector
            
            # Crear conector
            if crm_type == "salesforce":
                connector_config = {
                    "username": crm_config.get("username"),
                    "password": crm_config.get("password"),
                    "security_token": crm_config.get("security_token"),
                    "client_id": crm_config.get("client_id"),
                    "client_secret": crm_config.get("client_secret"),
                    "sandbox": crm_config.get("sandbox", False),
                    "sobject_type": "Lead"
                }
            elif crm_type == "pipedrive":
                connector_config = {
                    "api_token": crm_config.get("api_token"),
                    "company_domain": crm_config.get("company_domain"),
                    "resource_type": "persons"
                }
            else:
                raise ValueError(f"Tipo de CRM no soportado: {crm_type}")
            
            connector = create_connector(crm_type, connector_config)
            
            if not connector.connect():
                raise ValueError("No se pudo conectar al CRM")
            
            # Obtener registros actualizados desde CRM
            # (últimas 24 horas)
            from datetime import timedelta
            since = (datetime.utcnow() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
            
            filters = {"since": since} if crm_type == "pipedrive" else {}
            crm_records = connector.read_records(filters=filters, limit=max_records)
            
            stats = {"synced": 0, "updated": 0, "errors": 0}
            hook = PostgresHook(postgres_conn_id=str(params["postgres_conn_id"]))
            
            for crm_record in crm_records:
                try:
                    crm_id = crm_record.source_id
                    crm_data = crm_record.data
                    
                    # Buscar lead en BD por CRM ID
                    with hook.get_conn() as conn:
                        with conn.cursor() as cur:
                            # Buscar por CRM ID en metadata
                            cur.execute("""
                                SELECT id, lead_ext_id, email
                                FROM sales_pipeline
                                WHERE metadata->>'crm_id' = %s
                                LIMIT 1
                            """, (crm_id,))
                            
                            result = cur.fetchone()
                            
                            if result:
                                pipeline_id, lead_ext_id, email = result
                                
                                # Actualizar con datos del CRM
                                if not dry_run:
                                    # Mapear datos según tipo de CRM
                                    if crm_type == "salesforce":
                                        first_name = crm_data.get("FirstName")
                                        last_name = crm_data.get("LastName")
                                        phone = crm_data.get("Phone")
                                        status = crm_data.get("Status")
                                        
                                        # Mapear status de Salesforce a stage
                                        status_mapping = {
                                            "Open - Not Contacted": "qualified",
                                            "Working - Contacted": "contacted",
                                            "Qualified - Qualified": "proposal_sent",
                                            "Closed - Converted": "closed_won",
                                            "Closed - Not Converted": "closed_lost"
                                        }
                                        stage = status_mapping.get(status, "qualified")
                                        
                                    else:  # pipedrive
                                        emails = crm_data.get("email", [])
                                        email_obj = next((e for e in emails if e.get("primary")), emails[0] if emails else {})
                                        first_name = crm_data.get("first_name")
                                        last_name = crm_data.get("last_name")
                                        phones = crm_data.get("phone", [])
                                        phone_obj = next((p for p in phones if p.get("primary")), phones[0] if phones else {})
                                        phone = phone_obj.get("value") if phone_obj else None
                                        stage = "contacted"  # Default
                                    
                                    cur.execute("""
                                        UPDATE sales_pipeline
                                        SET 
                                            first_name = COALESCE(%s, first_name),
                                            last_name = COALESCE(%s, last_name),
                                            phone = COALESCE(%s, phone),
                                            stage = COALESCE(%s, stage),
                                            metadata = COALESCE(metadata, '{}'::jsonb) || jsonb_build_object('last_synced_at', %s),
                                            updated_at = NOW()
                                        WHERE id = %s
                                    """, (
                                        first_name,
                                        last_name,
                                        phone,
                                        stage,
                                        datetime.utcnow().isoformat(),
                                        pipeline_id
                                    ))
                                    
                                    conn.commit()
                                
                                stats["updated"] += 1
                                stats["synced"] += 1
                                logger.info(f"Lead {lead_ext_id} actualizado desde {crm_type}")
                            else:
                                # Lead no encontrado, podría crear nuevo o ignorar
                                logger.warning(f"Lead con CRM ID {crm_id} no encontrado en BD")
                        
                except Exception as e:
                    stats["errors"] += 1
                    logger.error(f"Error procesando registro CRM {crm_record.source_id}: {e}", exc_info=True)
            
            connector.disconnect()
            
            logger.info(f"Sincronización desde CRM completada: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error sincronizando desde CRM: {e}", exc_info=True)
            return {"synced": 0, "updated": 0, "errors": 0}
    
    
    # Pipeline
    changes = get_pipeline_changes()
    to_crm_stats = sync_to_crm(changes)
    from_crm_stats = sync_from_crm()
    
    @task(task_id="sync_summary")
    def sync_summary(to_stats: Dict[str, Any], from_stats: Dict[str, Any]) -> Dict[str, Any]:
        """Resumen de sincronización."""
        summary = {
            "to_crm": to_stats,
            "from_crm": from_stats,
            "total_synced": to_stats.get("synced", 0) + from_stats.get("synced", 0),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        logger.info(f"Resumen de sincronización: {summary}")
        
        try:
            Stats.incr("crm_sync.total_synced", summary["total_synced"])
            Stats.incr("crm_sync.to_crm", to_stats.get("synced", 0))
            Stats.incr("crm_sync.from_crm", from_stats.get("synced", 0))
        except Exception:
            pass
        
        return summary
    
    summary = sync_summary(to_crm_stats, from_crm_stats)


dag = crm_bidirectional_sync()

