"""
Ejemplos de uso del framework de sincronización
================================================

Ejemplos prácticos para diferentes casos de uso comunes.
"""
import os
from data.integrations.sync_framework import SyncFramework, SyncConfig, SyncDirection
from data.integrations.transformations import (
    hubspot_to_quickbooks_contact,
    quickbooks_to_hubspot_contact,
    sheets_to_hubspot_contact,
    create_transformer
)


def example_hubspot_to_quickbooks():
    """Ejemplo: Sincronizar contactos de HubSpot a QuickBooks"""
    framework = SyncFramework(
        db_connection_string=os.getenv("SYNC_DB_CONNECTION_STRING", "")
    )
    
    config = SyncConfig(
        sync_id="hubspot_qb_example",
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
    
    result = framework.sync(config, dry_run=False)
    print(f"Resultado: {result.to_dict()}")
    return result


def example_sheets_to_hubspot():
    """Ejemplo: Sincronizar datos de Google Sheets a HubSpot"""
    framework = SyncFramework(
        db_connection_string=os.getenv("SYNC_DB_CONNECTION_STRING", "")
    )
    
    config = SyncConfig(
        sync_id="sheets_hubspot_example",
        source_connector_type="google_sheets",
        source_config={
            "credentials_json": os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON", ""),
            "spreadsheet_id": os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", ""),
            "sheet_name": "Contacts"
        },
        target_connector_type="hubspot",
        target_config={
            "api_token": os.getenv("HUBSPOT_API_TOKEN", "")
        },
        direction=SyncDirection.SOURCE_TO_TARGET,
        batch_size=100,
        transform_function=sheets_to_hubspot_contact,
        filters={"range": "Contacts!A2:Z1000"},
        conflict_resolution="latest"
    )
    
    result = framework.sync(config, dry_run=True)  # Dry run primero
    print(f"Resultado: {result.to_dict()}")
    return result


def example_bidirectional_sync():
    """Ejemplo: Sincronización bidireccional HubSpot ↔ QuickBooks"""
    framework = SyncFramework(
        db_connection_string=os.getenv("SYNC_DB_CONNECTION_STRING", "")
    )
    
    # Sync HubSpot → QuickBooks
    config_hubspot_to_qb = SyncConfig(
        sync_id="hubspot_to_qb",
        source_connector_type="hubspot",
        source_config={"api_token": os.getenv("HUBSPOT_API_TOKEN", "")},
        target_connector_type="quickbooks",
        target_config={
            "access_token": os.getenv("QUICKBOOKS_ACCESS_TOKEN", ""),
            "realm_id": os.getenv("QUICKBOOKS_REALM_ID", "")
        },
        direction=SyncDirection.SOURCE_TO_TARGET,
        transform_function=hubspot_to_quickbooks_contact,
        conflict_resolution="source_wins"
    )
    
    # Sync QuickBooks → HubSpot
    config_qb_to_hubspot = SyncConfig(
        sync_id="qb_to_hubspot",
        source_connector_type="quickbooks",
        source_config={
            "access_token": os.getenv("QUICKBOOKS_ACCESS_TOKEN", ""),
            "realm_id": os.getenv("QUICKBOOKS_REALM_ID", "")
        },
        target_connector_type="hubspot",
        target_config={"api_token": os.getenv("HUBSPOT_API_TOKEN", "")},
        direction=SyncDirection.SOURCE_TO_TARGET,
        transform_function=quickbooks_to_hubspot_contact,
        conflict_resolution="target_wins"
    )
    
    # Ejecutar ambas sincronizaciones
    result1 = framework.sync(config_hubspot_to_qb, dry_run=False)
    result2 = framework.sync(config_qb_to_hubspot, dry_run=False)
    
    print(f"HubSpot → QuickBooks: {result1.successful}/{result1.total_records}")
    print(f"QuickBooks → HubSpot: {result2.successful}/{result2.total_records}")
    
    return result1, result2


def example_custom_transformation():
    """Ejemplo: Usando transformación personalizada"""
    framework = SyncFramework(
        db_connection_string=os.getenv("SYNC_DB_CONNECTION_STRING", "")
    )
    
    # Crear transformación personalizada
    custom_transform = create_transformer(
        field_mapping={
            "full_name": "name",
            "email_address": "email",
            "phone_number": "phone",
            "company_name": "company"
        },
        transformations={
            "email_address": lambda x: x.lower().strip() if x else None,
            "phone_number": lambda x: x.replace("-", "").replace(" ", "") if x else None
        },
        defaults={
            "company_name": "Unknown"
        }
    )
    
    config = SyncConfig(
        sync_id="custom_transform_example",
        source_connector_type="hubspot",
        source_config={"api_token": os.getenv("HUBSPOT_API_TOKEN", "")},
        target_connector_type="database",
        target_config={
            "connection_string": os.getenv("SYNC_DB_CONNECTION_STRING", ""),
            "table_name": "synced_contacts"
        },
        direction=SyncDirection.SOURCE_TO_TARGET,
        transform_function=custom_transform,
        conflict_resolution="latest"
    )
    
    result = framework.sync(config, dry_run=True)
    return result


def example_incremental_sync():
    """Ejemplo: Sincronización incremental (solo cambios recientes)"""
    framework = SyncFramework(
        db_connection_string=os.getenv("SYNC_DB_CONNECTION_STRING", "")
    )
    
    from datetime import datetime, timedelta
    
    # Solo sincronizar contactos modificados en las últimas 24 horas
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M:%S")
    
    config = SyncConfig(
        sync_id="incremental_sync",
        source_connector_type="hubspot",
        source_config={"api_token": os.getenv("HUBSPOT_API_TOKEN", "")},
        target_connector_type="quickbooks",
        target_config={
            "access_token": os.getenv("QUICKBOOKS_ACCESS_TOKEN", ""),
            "realm_id": os.getenv("QUICKBOOKS_REALM_ID", "")
        },
        direction=SyncDirection.SOURCE_TO_TARGET,
        filters={
            "object_type": "contacts",
            "createdAfter": yesterday
        },
        transform_function=hubspot_to_quickbooks_contact,
        conflict_resolution="latest"
    )
    
    result = framework.sync(config, dry_run=False)
    print(f"Sincronizados {result.successful} contactos modificados recientemente")
    return result


def example_batch_processing():
    """Ejemplo: Procesamiento en batches grandes"""
    framework = SyncFramework(
        db_connection_string=os.getenv("SYNC_DB_CONNECTION_STRING", "")
    )
    
    config = SyncConfig(
        sync_id="batch_sync",
        source_connector_type="hubspot",
        source_config={"api_token": os.getenv("HUBSPOT_API_TOKEN", "")},
        target_connector_type="google_sheets",
        target_config={
            "credentials_json": os.getenv("GOOGLE_SHEETS_CREDENTIALS_JSON", ""),
            "spreadsheet_id": os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID", ""),
            "sheet_name": "HubSpot Export"
        },
        direction=SyncDirection.SOURCE_TO_TARGET,
        batch_size=200,  # Procesar en batches de 200
        transform_function=hubspot_to_sheets_contact,
        conflict_resolution="source_wins"
    )
    
    result = framework.sync(config, dry_run=False)
    print(f"Procesados {result.total_records} registros en batches")
    return result


if __name__ == "__main__":
    # Ejecutar ejemplo
    print("Ejecutando ejemplo de sincronización HubSpot → QuickBooks")
    example_hubspot_to_quickbooks()


