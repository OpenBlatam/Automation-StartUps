"""
DAG especializado para sincronización HubSpot ↔ QuickBooks
==========================================================

Sincronización bidireccional optimizada entre HubSpot CRM y QuickBooks Online.
Incluye transformaciones específicas y mapeo de campos.
"""
from __future__ import annotations

from datetime import timedelta
import os
import logging

import pendulum
from airflow.decorators import dag, task
from airflow.models.param import Param

from data.integrations.sync_framework import SyncFramework, SyncConfig, SyncDirection
from data.integrations.transformations import (
    hubspot_to_quickbooks_contact,
    quickbooks_to_hubspot_contact
)

logger = logging.getLogger(__name__)

POSTGRES_CONN_ID = os.getenv("SYNC_POSTGRES_CONN_ID", "postgres_default")
DB_CONNECTION_STRING = os.getenv("SYNC_DB_CONNECTION_STRING", "")


@dag(
    'hubspot_quickbooks_sync',
    default_args={
        'owner': 'data-team',
        'depends_on_past': False,
        'email_on_failure': False,
        'retries': 2,
        'retry_delay': timedelta(minutes=5),
    },
    description='Sincronización bidireccional HubSpot ↔ QuickBooks',
    schedule='0 */6 * * *',  # Cada 6 horas
    start_date=pendulum.datetime(2025, 1, 1, tz='UTC'),
    catchup=False,
    tags=['integration', 'hubspot', 'quickbooks', 'sync'],
    params={
        'sync_contacts': Param(True, type='boolean', description='Sincronizar contactos'),
        'sync_deals': Param(False, type='boolean', description='Sincronizar deals a invoices'),
        'direction': Param('bidirectional', type='string', description='Dirección de sync'),
        'dry_run': Param(False, type='boolean', description='Modo dry-run'),
    },
    max_active_runs=1,
)
def hubspot_quickbooks_sync():
    """Pipeline de sincronización HubSpot-QuickBooks"""
    
    @task
    def sync_contacts_to_quickbooks(**context) -> dict:
        """Sincroniza contactos de HubSpot a QuickBooks"""
        params = context.get('params', {})
        dry_run = params.get('dry_run', False)
        
        if not params.get('sync_contacts', True):
            return {"skipped": True, "reason": "sync_contacts deshabilitado"}
        
        # Obtener connection string
        if not DB_CONNECTION_STRING:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = hook.get_conn()
            db_info = conn.get_dsn_parameters()
            conn_str = (
                f"postgresql://{db_info.get('user')}:{db_info.get('password')}@"
                f"{db_info.get('host')}:{db_info.get('port')}/{db_info.get('dbname')}"
            )
            conn.close()
        else:
            conn_str = DB_CONNECTION_STRING
        
        framework = SyncFramework(db_connection_string=conn_str)
        
        config = SyncConfig(
            sync_id=f"hubspot_qb_contacts_{pendulum.now().format('YYYYMMDD_HHmmss')}",
            source_connector_type="hubspot",
            source_config={
                "api_token": os.getenv("HUBSPOT_API_TOKEN", "")
            },
            target_connector_type="quickbooks",
            target_config={
                "access_token": os.getenv("QUICKBOOKS_ACCESS_TOKEN", ""),
                "realm_id": os.getenv("QUICKBOOKS_REALM_ID", ""),
                "base_url": os.getenv("QUICKBOOKS_BASE_URL", "https://sandbox-quickbooks.api.intuit.com")
            },
            direction=SyncDirection.SOURCE_TO_TARGET,
            batch_size=50,
            transform_function=hubspot_to_quickbooks_contact,
            filters={"object_type": "contacts"},
            conflict_resolution="source_wins"
        )
        
        result = framework.sync(config, dry_run=dry_run)
        return result.to_dict()
    
    @task
    def sync_customers_to_hubspot(**context) -> dict:
        """Sincroniza customers de QuickBooks a HubSpot"""
        params = context.get('params', {})
        dry_run = params.get('dry_run', False)
        direction = params.get('direction', 'bidirectional')
        
        if direction not in ['bidirectional', 'target_to_source']:
            return {"skipped": True, "reason": "dirección no permite target_to_source"}
        
        if not DB_CONNECTION_STRING:
            from airflow.providers.postgres.hooks.postgres import PostgresHook
            hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
            conn = hook.get_conn()
            db_info = conn.get_dsn_parameters()
            conn_str = (
                f"postgresql://{db_info.get('user')}:{db_info.get('password')}@"
                f"{db_info.get('host')}:{db_info.get('port')}/{db_info.get('dbname')}"
            )
            conn.close()
        else:
            conn_str = DB_CONNECTION_STRING
        
        framework = SyncFramework(db_connection_string=conn_str)
        
        config = SyncConfig(
            sync_id=f"qb_hubspot_customers_{pendulum.now().format('YYYYMMDD_HHmmss')}",
            source_connector_type="quickbooks",
            source_config={
                "access_token": os.getenv("QUICKBOOKS_ACCESS_TOKEN", ""),
                "realm_id": os.getenv("QUICKBOOKS_REALM_ID", ""),
                "base_url": os.getenv("QUICKBOOKS_BASE_URL", "https://sandbox-quickbooks.api.intuit.com")
            },
            target_connector_type="hubspot",
            target_config={
                "api_token": os.getenv("HUBSPOT_API_TOKEN", "")
            },
            direction=SyncDirection.SOURCE_TO_TARGET,
            batch_size=50,
            transform_function=quickbooks_to_hubspot_contact,
            filters={"entity_type": "Customer"},
            conflict_resolution="target_wins"
        )
        
        result = framework.sync(config, dry_run=dry_run)
        return result.to_dict()
    
    # Ejecutar tareas
    contacts_result = sync_contacts_to_quickbooks()
    customers_result = sync_customers_to_hubspot()
    
    # Las tareas se ejecutan en paralelo si direction es bidirectional


dag_instance = hubspot_quickbooks_sync()


