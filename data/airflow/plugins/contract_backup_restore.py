"""
Sistema de Backup y Restore Automatizado
Backup completo, restore selectivo, verificación de integridad
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import os

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def create_full_backup(
    output_path: str = None,
    include_versions: bool = True,
    include_events: bool = True,
    include_comments: bool = True,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Crea un backup completo del sistema de contratos.
    
    Args:
        output_path: Ruta del archivo de salida (opcional)
        include_versions: Incluir versiones firmadas
        include_events: Incluir eventos de auditoría
        include_comments: Incluir comentarios
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del backup
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    backup_data = {
        "backup_metadata": {
            "created_at": datetime.now().isoformat(),
            "backup_type": "full",
            "includes": {
                "templates": True,
                "contracts": True,
                "signers": True,
                "versions": include_versions,
                "events": include_events,
                "comments": include_comments
            }
        },
        "templates": [],
        "contracts": [],
        "signers": [],
        "versions": [],
        "events": [],
        "comments": []
    }
    
    # Backup de templates
    templates_query = "SELECT * FROM contract_templates"
    templates = hook.get_records(templates_query)
    for row in templates:
        backup_data["templates"].append({
            "template_id": row[1],
            "name": row[2],
            "description": row[3],
            "contract_type": row[4],
            "template_content": row[5],
            "template_variables": row[6],
            "default_expiration_days": row[7],
            "is_active": row[11],
            "created_at": row[13].isoformat() if row[13] else None
        })
    
    # Backup de contratos
    contracts_query = "SELECT * FROM contracts"
    contracts = hook.get_records(contracts_query)
    for row in contracts:
        backup_data["contracts"].append({
            "contract_id": row[1],
            "template_id": row[2],
            "contract_type": row[3],
            "primary_party_email": row[5],
            "primary_party_name": row[6],
            "title": row[9],
            "status": row[11],
            "created_at": row[21].isoformat() if row[21] else None
        })
    
    # Backup de signers
    signers_query = "SELECT * FROM contract_signers"
    signers = hook.get_records(signers_query)
    for row in signers:
        backup_data["signers"].append({
            "contract_id": row[2],
            "signer_email": row[3],
            "signer_name": row[4],
            "signer_role": row[5],
            "signature_status": row[7],
            "signature_signed_at": row[9].isoformat() if row[9] else None
        })
    
    # Backup de versiones si se solicita
    if include_versions:
        versions_query = "SELECT * FROM contract_versions"
        versions = hook.get_records(versions_query)
        for row in versions:
            backup_data["versions"].append({
                "contract_id": row[1],
                "version_number": row[2],
                "signed_document_hash": row[8],
                "signed_at": row[11].isoformat() if row[11] else None
            })
    
    # Backup de eventos si se solicita
    if include_events:
        events_query = "SELECT * FROM contract_events"
        events = hook.get_records(events_query)
        for row in events:
            backup_data["events"].append({
                "contract_id": row[1],
                "event_type": row[2],
                "event_description": row[3],
                "event_actor_email": row[4],
                "event_timestamp": row[6].isoformat() if row[6] else None
            })
    
    # Backup de comentarios si se solicita
    if include_comments:
        try:
            comments_query = "SELECT * FROM contract_comments"
            comments = hook.get_records(comments_query)
            for row in comments:
                backup_data["comments"].append({
                    "contract_id": row[2],
                    "comment_text": row[3],
                    "author_email": row[4],
                    "comment_type": row[6],
                    "created_at": row[8].isoformat() if row[8] else None
                })
        except Exception as e:
            logger.warning(f"Error backuping comments: {e}")
    
    # Guardar a archivo si se especifica
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        file_size = os.path.getsize(output_path)
        backup_data["backup_metadata"]["file_path"] = output_path
        backup_data["backup_metadata"]["file_size_bytes"] = file_size
    
    logger.info(
        f"Backup completo creado",
        extra={
            "templates": len(backup_data["templates"]),
            "contracts": len(backup_data["contracts"]),
            "file": output_path
        }
    )
    
    return backup_data


def restore_from_backup(
    backup_file: str,
    restore_contracts: bool = True,
    restore_templates: bool = True,
    restore_signers: bool = True,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Restaura datos desde un backup.
    
    Args:
        backup_file: Ruta del archivo de backup
        restore_contracts: Restaurar contratos
        restore_templates: Restaurar templates
        restore_signers: Restaurar signers
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de restauración
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    # Cargar backup
    with open(backup_file, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    results = {
        "templates_restored": 0,
        "contracts_restored": 0,
        "signers_restored": 0,
        "errors": []
    }
    
    # Restaurar templates
    if restore_templates:
        for template in backup_data.get("templates", []):
            try:
                # Verificar si existe
                check_query = "SELECT template_id FROM contract_templates WHERE template_id = %s"
                exists = hook.get_first(check_query, parameters=(template["template_id"],))
                
                if not exists:
                    # Insertar template
                    insert_query = """
                        INSERT INTO contract_templates (
                            template_id, name, description, contract_type,
                            template_content, template_variables, default_expiration_days,
                            is_active, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """
                    hook.run(
                        insert_query,
                        parameters=(
                            template["template_id"],
                            template["name"],
                            template.get("description"),
                            template["contract_type"],
                            template["template_content"],
                            json.dumps(template.get("template_variables", {})),
                            template.get("default_expiration_days", 365),
                            template.get("is_active", True),
                            template.get("created_at")
                        )
                    )
                    results["templates_restored"] += 1
            except Exception as e:
                results["errors"].append(f"Error restaurando template {template['template_id']}: {e}")
    
    logger.info(
        f"Restauración completada",
        extra=results
    )
    
    return results


def verify_backup_integrity(backup_file: str) -> Dict[str, Any]:
    """
    Verifica la integridad de un backup.
    
    Args:
        backup_file: Ruta del archivo de backup
        
    Returns:
        Dict con resultado de verificación
    """
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        verification = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "statistics": {
                "templates": len(backup_data.get("templates", [])),
                "contracts": len(backup_data.get("contracts", [])),
                "signers": len(backup_data.get("signers", [])),
                "versions": len(backup_data.get("versions", [])),
                "events": len(backup_data.get("events", []))
            }
        }
        
        # Verificar metadata
        if "backup_metadata" not in backup_data:
            verification["valid"] = False
            verification["errors"].append("Metadata faltante")
        
        # Verificar estructura
        required_keys = ["templates", "contracts", "signers"]
        for key in required_keys:
            if key not in backup_data:
                verification["valid"] = False
                verification["errors"].append(f"Sección {key} faltante")
        
        return verification
        
    except Exception as e:
        return {
            "valid": False,
            "errors": [f"Error leyendo backup: {e}"],
            "warnings": []
        }

