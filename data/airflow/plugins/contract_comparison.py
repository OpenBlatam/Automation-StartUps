"""
Sistema de Comparación de Contratos
Compara contratos para detectar cambios y diferencias
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import difflib

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def compare_contracts(
    contract_id1: str,
    contract_id2: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Compara dos contratos y detecta diferencias.
    
    Args:
        contract_id1: ID del primer contrato
        contract_id2: ID del segundo contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con diferencias encontradas
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener contratos
    query = """
        SELECT contract_id, title, contract_type, contract_variables,
               contract_content, status, expiration_date, signed_date
        FROM contracts
        WHERE contract_id IN (%s, %s)
    """
    
    contracts = hook.get_records(query, parameters=(contract_id1, contract_id2))
    
    if len(contracts) != 2:
        raise ValueError("Uno o ambos contratos no encontrados")
    
    c1 = {row[0]: row for row in contracts if row[0] == contract_id1}[contract_id1]
    c2 = {row[0]: row for row in contracts if row[0] == contract_id2}[contract_id2]
    
    differences = {
        "contract_id1": contract_id1,
        "contract_id2": contract_id2,
        "compared_at": datetime.now().isoformat(),
        "differences": []
    }
    
    # Comparar campos
    fields_to_compare = [
        ("title", 1),
        ("contract_type", 2),
        ("contract_variables", 3),
        ("contract_content", 4),
        ("status", 5),
        ("expiration_date", 6),
        ("signed_date", 7)
    ]
    
    for field_name, idx in fields_to_compare:
        val1 = c1[idx]
        val2 = c2[idx]
        
        if val1 != val2:
            diff_info = {
                "field": field_name,
                "contract1_value": str(val1) if val1 else None,
                "contract2_value": str(val2) if val2 else None
            }
            
            # Para contenido, generar diff
            if field_name == "contract_content" and val1 and val2:
                diff_lines = list(difflib.unified_diff(
                    str(val1).splitlines(keepends=True),
                    str(val2).splitlines(keepends=True),
                    fromfile=contract_id1,
                    tofile=contract_id2,
                    lineterm=''
                ))
                diff_info["diff"] = ''.join(diff_lines)
            
            differences["differences"].append(diff_info)
    
    differences["has_differences"] = len(differences["differences"]) > 0
    differences["difference_count"] = len(differences["differences"])
    
    return differences


def compare_contract_versions(
    contract_id: str,
    version1: int = None,
    version2: int = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Compara dos versiones de un mismo contrato.
    
    Args:
        contract_id: ID del contrato
        version1: Primera versión (None = versión actual)
        version2: Segunda versión (None = versión actual)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con diferencias entre versiones
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener versiones
    if version1 is None:
        # Versión actual
        query1 = """
            SELECT contract_content, signed_document_hash
            FROM contracts
            WHERE contract_id = %s
        """
        v1 = hook.get_first(query1, parameters=(contract_id,))
    else:
        query1 = """
            SELECT signed_document_content, signed_document_hash
            FROM contract_versions
            WHERE contract_id = %s AND version_number = %s
        """
        v1 = hook.get_first(query1, parameters=(contract_id, version1))
    
    if version2 is None:
        query2 = """
            SELECT contract_content, signed_document_hash
            FROM contracts
            WHERE contract_id = %s
        """
        v2 = hook.get_first(query2, parameters=(contract_id,))
    else:
        query2 = """
            SELECT signed_document_content, signed_document_hash
            FROM contract_versions
            WHERE contract_id = %s AND version_number = %s
        """
        v2 = hook.get_first(query2, parameters=(contract_id, version2))
    
    if not v1 or not v2:
        raise ValueError("Una o ambas versiones no encontradas")
    
    differences = {
        "contract_id": contract_id,
        "version1": version1 if version1 else "current",
        "version2": version2 if version2 else "current",
        "compared_at": datetime.now().isoformat(),
        "differences": []
    }
    
    # Comparar hash
    if v1[1] != v2[1]:
        differences["differences"].append({
            "field": "document_hash",
            "type": "hash_mismatch",
            "description": "Los documentos tienen hash diferente",
            "hash1": v1[1],
            "hash2": v2[1]
        })
    
    # Comparar contenido si está disponible
    if v1[0] and v2[0] and v1[0] != v2[0]:
        content1 = str(v1[0])
        content2 = str(v2[0])
        
        diff_lines = list(difflib.unified_diff(
            content1.splitlines(keepends=True),
            content2.splitlines(keepends=True),
            fromfile=f"version_{version1 if version1 else 'current'}",
            tofile=f"version_{version2 if version2 else 'current'}",
            lineterm=''
        ))
        
        differences["differences"].append({
            "field": "content",
            "type": "content_change",
            "description": "El contenido del documento ha cambiado",
            "diff": ''.join(diff_lines)
        })
    
    differences["has_differences"] = len(differences["differences"]) > 0
    
    return differences

