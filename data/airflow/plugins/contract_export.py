"""
Módulo de Exportación y Backup de Contratos
Incluye exportación a CSV, JSON y backup completo
"""

from __future__ import annotations

import json
import csv
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
from io import StringIO

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def export_contracts_to_csv(
    start_date: str = None,
    end_date: str = None,
    contract_type: str = None,
    status: str = None,
    postgres_conn_id: str = "postgres_default"
) -> str:
    """
    Exporta contratos a formato CSV.
    
    Args:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        contract_type: Filtrar por tipo
        status: Filtrar por estado
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        String con contenido CSV
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Construir query
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("c.created_at >= %s")
        params.append(start_date)
    if end_date:
        where_clauses.append("c.created_at <= %s")
        params.append(end_date)
    if contract_type:
        where_clauses.append("c.contract_type = %s")
        params.append(contract_type)
    if status:
        where_clauses.append("c.status = %s")
        params.append(status)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    query = f"""
        SELECT 
            c.contract_id,
            c.title,
            c.contract_type,
            c.status,
            c.primary_party_name,
            c.primary_party_email,
            c.start_date,
            c.expiration_date,
            c.signed_date,
            c.created_at,
            COUNT(DISTINCT cs.id) as signers_count,
            COUNT(DISTINCT CASE WHEN cs.signature_status = 'signed' THEN cs.id END) as signed_count,
            c.esignature_provider,
            c.auto_renew
        FROM contracts c
        LEFT JOIN contract_signers cs ON c.contract_id = cs.contract_id
        WHERE {where_sql}
        GROUP BY c.contract_id, c.title, c.contract_type, c.status, c.primary_party_name,
                 c.primary_party_email, c.start_date, c.expiration_date, c.signed_date,
                 c.created_at, c.esignature_provider, c.auto_renew
        ORDER BY c.created_at DESC
    """
    
    contracts = hook.get_records(query, parameters=tuple(params))
    
    # Generar CSV
    output = StringIO()
    writer = csv.writer(output)
    
    # Headers
    writer.writerow([
        "Contract ID", "Title", "Type", "Status", "Primary Party Name",
        "Primary Party Email", "Start Date", "Expiration Date", "Signed Date",
        "Created At", "Signers Count", "Signed Count", "E-Signature Provider",
        "Auto Renew"
    ])
    
    # Data
    for row in contracts:
        writer.writerow([
            row[0], row[1], row[2], row[3], row[4], row[5],
            row[6].isoformat() if row[6] else "",
            row[7].isoformat() if row[7] else "",
            row[8].isoformat() if row[8] else "",
            row[9].isoformat() if row[9] else "",
            row[10], row[11], row[12] or "", row[13] or False
        ])
    
    return output.getvalue()


def export_contracts_to_json(
    start_date: str = None,
    end_date: str = None,
    contract_type: str = None,
    status: str = None,
    include_content: bool = False,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Exporta contratos a formato JSON.
    
    Args:
        start_date: Fecha de inicio (YYYY-MM-DD)
        end_date: Fecha de fin (YYYY-MM-DD)
        contract_type: Filtrar por tipo
        status: Filtrar por estado
        include_content: Incluir contenido del contrato
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con contratos en formato JSON
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Construir query
    where_clauses = []
    params = []
    
    if start_date:
        where_clauses.append("c.created_at >= %s")
        params.append(start_date)
    if end_date:
        where_clauses.append("c.created_at <= %s")
        params.append(end_date)
    if contract_type:
        where_clauses.append("c.contract_type = %s")
        params.append(contract_type)
    if status:
        where_clauses.append("c.status = %s")
        params.append(status)
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Query base
    fields = [
        "c.contract_id", "c.title", "c.contract_type", "c.status",
        "c.primary_party_name", "c.primary_party_email", "c.start_date",
        "c.expiration_date", "c.signed_date", "c.created_at", "c.updated_at",
        "c.esignature_provider", "c.auto_renew", "c.template_id"
    ]
    
    if include_content:
        fields.append("c.contract_content")
    
    query = f"""
        SELECT {', '.join(fields)}
        FROM contracts c
        WHERE {where_sql}
        ORDER BY c.created_at DESC
    """
    
    contracts = hook.get_records(query, parameters=tuple(params))
    
    result = {
        "export_date": datetime.now().isoformat(),
        "filters": {
            "start_date": start_date,
            "end_date": end_date,
            "contract_type": contract_type,
            "status": status
        },
        "contracts": []
    }
    
    for row in contracts:
        contract_data = {
            "contract_id": row[0],
            "title": row[1],
            "contract_type": row[2],
            "status": row[3],
            "primary_party_name": row[4],
            "primary_party_email": row[5],
            "start_date": row[6].isoformat() if row[6] else None,
            "expiration_date": row[7].isoformat() if row[7] else None,
            "signed_date": row[8].isoformat() if row[8] else None,
            "created_at": row[9].isoformat() if row[9] else None,
            "updated_at": row[10].isoformat() if row[10] else None,
            "esignature_provider": row[11],
            "auto_renew": row[12],
            "template_id": row[13]
        }
        
        if include_content:
            contract_data["contract_content"] = row[14]
        
        # Obtener firmantes
        signers_query = """
            SELECT signer_email, signer_name, signer_role, signature_status,
                   signature_signed_at, signer_order
            FROM contract_signers
            WHERE contract_id = %s
            ORDER BY signer_order
        """
        signers = hook.get_records(signers_query, parameters=(row[0],))
        contract_data["signers"] = [
            {
                "email": s[0],
                "name": s[1],
                "role": s[2],
                "status": s[3],
                "signed_at": s[4].isoformat() if s[4] else None,
                "order": s[5]
            }
            for s in signers
        ]
        
        # Obtener eventos
        events_query = """
            SELECT event_type, event_description, event_timestamp, event_actor_email
            FROM contract_events
            WHERE contract_id = %s
            ORDER BY event_timestamp DESC
        """
        events = hook.get_records(events_query, parameters=(row[0],))
        contract_data["events"] = [
            {
                "type": e[0],
                "description": e[1],
                "timestamp": e[2].isoformat() if e[2] else None,
                "actor": e[3]
            }
            for e in events
        ]
        
        result["contracts"].append(contract_data)
    
    result["total_count"] = len(result["contracts"])
    
    return result


def create_backup(
    output_format: str = "json",
    include_versions: bool = True,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Crea un backup completo del sistema de contratos.
    
    Args:
        output_format: 'json' o 'csv'
        include_versions: Incluir versiones firmadas
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del backup
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    backup_info = {
        "backup_date": datetime.now().isoformat(),
        "format": output_format,
        "includes": {
            "templates": True,
            "contracts": True,
            "signers": True,
            "events": True,
            "versions": include_versions,
            "reminders": True
        }
    }
    
    if output_format == "json":
        backup_data = {
            "backup_info": backup_info,
            "templates": [],
            "contracts": [],
            "versions": []
        }
        
        # Exportar templates
        templates_query = """
            SELECT template_id, name, description, contract_type, template_content,
                   template_variables, default_expiration_days, default_reminder_days,
                   requires_legal_review, requires_manager_approval, signers_required,
                   metadata, created_at, updated_at
            FROM contract_templates
            WHERE is_active = true
        """
        templates = hook.get_records(templates_query)
        for row in templates:
            backup_data["templates"].append({
                "template_id": row[0],
                "name": row[1],
                "description": row[2],
                "contract_type": row[3],
                "template_content": row[4],
                "template_variables": row[5] if isinstance(row[5], dict) else json.loads(row[5] or '{}'),
                "default_expiration_days": row[6],
                "default_reminder_days": row[7] if isinstance(row[7], list) else json.loads(row[7] or '[]'),
                "requires_legal_review": row[8],
                "requires_manager_approval": row[9],
                "signers_required": row[10] if isinstance(row[10], list) else json.loads(row[10] or '[]'),
                "metadata": row[11] if isinstance(row[11], dict) else json.loads(row[11] or '{}'),
                "created_at": row[12].isoformat() if row[12] else None,
                "updated_at": row[13].isoformat() if row[13] else None
            })
        
        # Exportar contratos (usando función existente)
        contracts_data = export_contracts_to_json(include_content=True, postgres_conn_id=postgres_conn_id)
        backup_data["contracts"] = contracts_data["contracts"]
        
        # Exportar versiones si está configurado
        if include_versions:
            versions_query = """
                SELECT contract_id, version_number, version_reason, signed_document_url,
                       signed_document_hash, signed_document_size_bytes, signed_at,
                       is_current
                FROM contract_versions
                WHERE is_current = true
            """
            versions = hook.get_records(versions_query)
            backup_data["versions"] = [
                {
                    "contract_id": v[0],
                    "version_number": v[1],
                    "version_reason": v[2],
                    "signed_document_url": v[3],
                    "signed_document_hash": v[4],
                    "size_bytes": v[5],
                    "signed_at": v[6].isoformat() if v[6] else None,
                    "is_current": v[7]
                }
                for v in versions
            ]
        
        backup_info["data"] = backup_data
        backup_info["size_bytes"] = len(json.dumps(backup_data))
        
    else:  # CSV
        csv_content = export_contracts_to_csv(postgres_conn_id=postgres_conn_id)
        backup_info["data"] = csv_content
        backup_info["size_bytes"] = len(csv_content.encode('utf-8'))
    
    backup_info["templates_count"] = len(backup_data.get("templates", [])) if output_format == "json" else 0
    backup_info["contracts_count"] = len(backup_data.get("contracts", [])) if output_format == "json" else 0
    
    logger.info(
        f"Backup creado",
        extra={
            "format": output_format,
            "templates": backup_info.get("templates_count", 0),
            "contracts": backup_info.get("contracts_count", 0)
        }
    )
    
    return backup_info

