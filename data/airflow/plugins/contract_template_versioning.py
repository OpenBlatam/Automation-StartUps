"""
Sistema de Versionado de Plantillas de Contratos
Gestión de versiones, comparación y rollback
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import hashlib

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def create_template_version(
    template_id: str,
    version_notes: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Crea una nueva versión de una plantilla.
    
    Args:
        template_id: ID de la plantilla
        version_notes: Notas sobre los cambios
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de la nueva versión
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener plantilla actual
    query = """
        SELECT template_content, template_variables, default_expiration_days,
               signers_required, created_by
        FROM contract_templates
        WHERE template_id = %s
    """
    template = hook.get_first(query, parameters=(template_id,))
    
    if not template:
        raise ValueError(f"Template {template_id} no encontrado")
    
    # Calcular hash del contenido
    content_hash = hashlib.sha256(
        template[0].encode('utf-8') if template[0] else b''
    ).hexdigest()
    
    # Obtener versión actual
    version_query = """
        SELECT COALESCE(MAX(version_number), 0) + 1
        FROM contract_template_versions
        WHERE template_id = %s
    """
    new_version = hook.get_first(version_query, parameters=(template_id,))[0]
    
    # Insertar nueva versión
    insert_query = """
        INSERT INTO contract_template_versions (
            template_id, version_number, template_content, template_variables,
            default_expiration_days, signers_required, content_hash,
            version_notes, created_by, created_at
        )
        SELECT 
            template_id, %s, template_content, template_variables,
            default_expiration_days, signers_required, %s,
            %s, created_by, NOW()
        FROM contract_templates
        WHERE template_id = %s
    """
    
    hook.run(
        insert_query,
        parameters=(new_version, content_hash, version_notes, template_id)
    )
    
    logger.info(
        f"Nueva versión creada para template {template_id}",
        extra={"version": new_version}
    )
    
    return {
        "template_id": template_id,
        "version_number": new_version,
        "content_hash": content_hash,
        "version_notes": version_notes,
        "created_at": datetime.now().isoformat()
    }


def get_template_version(
    template_id: str,
    version_number: int,
    postgres_conn_id: str = "postgres_default"
) -> Optional[Dict[str, Any]]:
    """
    Obtiene una versión específica de una plantilla.
    
    Args:
        template_id: ID de la plantilla
        version_number: Número de versión
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de la versión
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    query = """
        SELECT template_id, version_number, template_content, template_variables,
               default_expiration_days, signers_required, content_hash,
               version_notes, created_by, created_at
        FROM contract_template_versions
        WHERE template_id = %s AND version_number = %s
    """
    
    version = hook.get_first(query, parameters=(template_id, version_number))
    
    if not version:
        return None
    
    return {
        "template_id": version[0],
        "version_number": version[1],
        "template_content": version[2],
        "template_variables": version[3],
        "default_expiration_days": version[4],
        "signers_required": version[5],
        "content_hash": version[6],
        "version_notes": version[7],
        "created_by": version[8],
        "created_at": version[9].isoformat() if version[9] else None
    }


def list_template_versions(
    template_id: str,
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Lista todas las versiones de una plantilla.
    
    Args:
        template_id: ID de la plantilla
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de versiones
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    query = """
        SELECT version_number, content_hash, version_notes,
               created_by, created_at,
               (SELECT COUNT(*) FROM contracts 
                WHERE contract_template_version = version_number 
                  AND template_id = %s) as contracts_using
        FROM contract_template_versions
        WHERE template_id = %s
        ORDER BY version_number DESC
    """
    
    versions = hook.get_records(query, parameters=(template_id, template_id))
    
    return [
        {
            "version_number": row[0],
            "content_hash": row[1],
            "version_notes": row[2],
            "created_by": row[3],
            "created_at": row[4].isoformat() if row[4] else None,
            "contracts_using": row[5] or 0
        }
        for row in versions
    ]


def restore_template_version(
    template_id: str,
    version_number: int,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Restaura una versión específica de una plantilla.
    
    Args:
        template_id: ID de la plantilla
        version_number: Número de versión a restaurar
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de la restauración
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    # Primero crear versión del estado actual antes de restaurar
    create_template_version(
        template_id=template_id,
        version_notes=f"Backup antes de restaurar versión {version_number}",
        postgres_conn_id=postgres_conn_id
    )
    
    # Obtener versión a restaurar
    version = get_template_version(template_id, version_number, postgres_conn_id)
    
    if not version:
        raise ValueError(f"Versión {version_number} no encontrada")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Restaurar plantilla
    restore_query = """
        UPDATE contract_templates
        SET 
            template_content = %s,
            template_variables = %s,
            default_expiration_days = %s,
            signers_required = %s,
            updated_at = NOW()
        WHERE template_id = %s
    """
    
    hook.run(
        restore_query,
        parameters=(
            version["template_content"],
            version["template_variables"],
            version["default_expiration_days"],
            version["signers_required"],
            template_id
        )
    )
    
    logger.info(
        f"Template {template_id} restaurado a versión {version_number}"
    )
    
    return {
        "template_id": template_id,
        "restored_to_version": version_number,
        "restored_at": datetime.now().isoformat()
    }


def compare_template_versions(
    template_id: str,
    version1: int,
    version2: int,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Compara dos versiones de una plantilla.
    
    Args:
        template_id: ID de la plantilla
        version1: Primera versión
        version2: Segunda versión
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con diferencias
    """
    v1 = get_template_version(template_id, version1, postgres_conn_id)
    v2 = get_template_version(template_id, version2, postgres_conn_id)
    
    if not v1 or not v2:
        raise ValueError("Una o ambas versiones no encontradas")
    
    differences = {
        "template_id": template_id,
        "version1": version1,
        "version2": version2,
        "differences": []
    }
    
    # Comparar contenido
    if v1["template_content"] != v2["template_content"]:
        differences["differences"].append({
            "field": "template_content",
            "type": "content_change",
            "description": "Contenido de la plantilla ha cambiado"
        })
    
    # Comparar variables
    if v1["template_variables"] != v2["template_variables"]:
        differences["differences"].append({
            "field": "template_variables",
            "type": "variables_change",
            "description": "Variables de la plantilla han cambiado"
        })
    
    # Comparar configuración
    if v1["default_expiration_days"] != v2["default_expiration_days"]:
        differences["differences"].append({
            "field": "default_expiration_days",
            "type": "config_change",
            "old_value": v1["default_expiration_days"],
            "new_value": v2["default_expiration_days"]
        })
    
    if v1["signers_required"] != v2["signers_required"]:
        differences["differences"].append({
            "field": "signers_required",
            "type": "config_change",
            "description": "Firmantes requeridos han cambiado"
        })
    
    differences["has_differences"] = len(differences["differences"]) > 0
    
    return differences

