"""
Funciones de Migración de Datos para Contratos
Migración entre versiones del sistema, imports, exports masivos
"""

from __future__ import annotations

import logging
import json
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from io import StringIO

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def migrate_contracts_from_csv(
    csv_content: str,
    template_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Migra contratos desde un archivo CSV.
    
    Args:
        csv_content: Contenido del CSV
        template_id: ID de plantilla a usar
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultados de migración
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    from data.airflow.plugins.contract_integrations import create_contract_from_template
    
    # Parsear CSV
    reader = csv.DictReader(StringIO(csv_content))
    
    results = {
        "total": 0,
        "created": 0,
        "failed": 0,
        "errors": []
    }
    
    for row in reader:
        results["total"] += 1
        
        try:
            # Construir variables del contrato desde CSV
            contract_variables = {
                k: v for k, v in row.items() 
                if k not in ['primary_party_email', 'primary_party_name']
            }
            
            primary_party_email = row.get('primary_party_email', '').strip()
            primary_party_name = row.get('primary_party_name', '').strip()
            
            if not primary_party_email or not primary_party_name:
                results["failed"] += 1
                results["errors"].append(f"Fila {results['total']}: Faltan email o nombre")
                continue
            
            # Crear contrato
            result = create_contract_from_template(
                template_id=template_id,
                primary_party_email=primary_party_email,
                primary_party_name=primary_party_name,
                contract_variables=contract_variables
            )
            
            results["created"] += 1
            logger.info(f"Contrato migrado: {result['contract_id']}")
            
        except Exception as e:
            results["failed"] += 1
            error_msg = f"Fila {results['total']}: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
    
    logger.info(
        f"Migración CSV completada",
        extra=results
    )
    
    return results


def migrate_contracts_from_json(
    json_data: List[Dict[str, Any]],
    template_id: str = None,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Migra contratos desde datos JSON.
    
    Args:
        json_data: Lista de objetos de contrato
        template_id: ID de plantilla (opcional, puede venir en cada objeto)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultados de migración
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    from data.airflow.plugins.contract_integrations import create_contract_from_template
    
    results = {
        "total": len(json_data),
        "created": 0,
        "failed": 0,
        "errors": []
    }
    
    for idx, contract_data in enumerate(json_data):
        try:
            contract_template_id = contract_data.get("template_id") or template_id
            if not contract_template_id:
                results["failed"] += 1
                results["errors"].append(f"Ítem {idx + 1}: template_id no especificado")
                continue
            
            primary_party_email = contract_data.get("primary_party_email", "").strip()
            primary_party_name = contract_data.get("primary_party_name", "").strip()
            
            if not primary_party_email or not primary_party_name:
                results["failed"] += 1
                results["errors"].append(f"Ítem {idx + 1}: Faltan email o nombre")
                continue
            
            contract_variables = contract_data.get("contract_variables", {})
            additional_signers = contract_data.get("additional_signers")
            
            # Crear contrato
            result = create_contract_from_template(
                template_id=contract_template_id,
                primary_party_email=primary_party_email,
                primary_party_name=primary_party_name,
                contract_variables=contract_variables,
                additional_signers=additional_signers
            )
            
            results["created"] += 1
            
        except Exception as e:
            results["failed"] += 1
            error_msg = f"Ítem {idx + 1}: {e}"
            results["errors"].append(error_msg)
            logger.error(error_msg)
    
    logger.info(
        f"Migración JSON completada",
        extra=results
    )
    
    return results


def backup_contracts_to_file(
    output_file: str,
    format: str = "json",
    include_versions: bool = True,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Crea backup de contratos a archivo.
    
    Args:
        output_file: Ruta del archivo de salida
        format: 'json' o 'csv'
        include_versions: Incluir versiones firmadas
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del backup
    """
    from data.airflow.plugins.contract_export import export_contracts_to_json, export_contracts_to_csv, create_backup
    
    if format == "json":
        if include_versions:
            backup_data = create_backup(output_format="json", include_versions=True)
            content = json.dumps(backup_data, indent=2, default=str)
        else:
            export_data = export_contracts_to_json(include_content=True, postgres_conn_id=postgres_conn_id)
            content = json.dumps(export_data, indent=2, default=str)
    else:  # CSV
        content = export_contracts_to_csv(postgres_conn_id=postgres_conn_id)
    
    # Escribir archivo
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    import os
    file_size = os.path.getsize(output_file)
    
    logger.info(
        f"Backup creado en archivo",
        extra={
            "file": output_file,
            "format": format,
            "size_bytes": file_size
        }
    )
    
    return {
        "file": output_file,
        "format": format,
        "size_bytes": file_size,
        "created_at": datetime.now().isoformat()
    }

