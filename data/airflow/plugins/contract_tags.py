"""
Sistema de Tags y Categorización para Contratos
Organización y búsqueda avanzada por etiquetas
"""

from __future__ import annotations

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

try:
    from airflow.providers.postgres.hooks.postgres import PostgresHook
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

logger = logging.getLogger("airflow.task")


def add_tags_to_contract(
    contract_id: str,
    tags: List[str],
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Agrega tags a un contrato.
    
    Args:
        contract_id: ID del contrato
        tags: Lista de tags a agregar
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de tags agregados
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener tags actuales
    query = """
        SELECT metadata->>'tags' as current_tags
        FROM contracts
        WHERE contract_id = %s
    """
    result = hook.get_first(query, parameters=(contract_id,))
    
    if not result:
        raise ValueError(f"Contrato {contract_id} no encontrado")
    
    # Parsear tags actuales
    import json
    current_tags = []
    if result[0]:
        try:
            current_tags = json.loads(result[0]) if isinstance(result[0], str) else result[0]
        except:
            current_tags = []
    
    # Agregar nuevos tags (sin duplicados)
    updated_tags = list(set(current_tags + tags))
    
    # Actualizar metadata
    update_query = """
        UPDATE contracts
        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
            jsonb_build_object('tags', %s, 'tags_updated_at', NOW())
        WHERE contract_id = %s
    """
    
    hook.run(
        update_query,
        parameters=(json.dumps(updated_tags), contract_id)
    )
    
    logger.info(
        f"Tags agregados a contrato {contract_id}",
        extra={"tags": updated_tags}
    )
    
    return {
        "contract_id": contract_id,
        "tags": updated_tags,
        "added_tags": tags,
        "updated_at": datetime.now().isoformat()
    }


def remove_tags_from_contract(
    contract_id: str,
    tags: List[str],
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Remueve tags de un contrato.
    
    Args:
        contract_id: ID del contrato
        tags: Lista de tags a remover
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información de tags removidos
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener tags actuales
    query = """
        SELECT metadata->>'tags' as current_tags
        FROM contracts
        WHERE contract_id = %s
    """
    result = hook.get_first(query, parameters=(contract_id,))
    
    if not result:
        raise ValueError(f"Contrato {contract_id} no encontrado")
    
    # Parsear tags actuales
    import json
    current_tags = []
    if result[0]:
        try:
            current_tags = json.loads(result[0]) if isinstance(result[0], str) else result[0]
        except:
            current_tags = []
    
    # Remover tags
    updated_tags = [t for t in current_tags if t not in tags]
    
    # Actualizar metadata
    update_query = """
        UPDATE contracts
        SET metadata = COALESCE(metadata, '{}'::jsonb) || 
            jsonb_build_object('tags', %s, 'tags_updated_at', NOW())
        WHERE contract_id = %s
    """
    
    hook.run(
        update_query,
        parameters=(json.dumps(updated_tags), contract_id)
    )
    
    return {
        "contract_id": contract_id,
        "tags": updated_tags,
        "removed_tags": tags,
        "updated_at": datetime.now().isoformat()
    }


def search_contracts_by_tags(
    tags: List[str],
    match_all: bool = False,
    limit: int = 50,
    offset: int = 0,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Busca contratos por tags.
    
    Args:
        tags: Lista de tags a buscar
        match_all: Si True, debe tener todos los tags; si False, cualquiera
        limit: Límite de resultados
        offset: Offset para paginación
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con contratos encontrados
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    if match_all:
        # Debe tener todos los tags
        conditions = " AND ".join([
            f"metadata->>'tags' @> %s"
            for _ in tags
        ])
        params = [json.dumps([tag]) for tag in tags] + [limit, offset]
    else:
        # Cualquier tag
        import json
        conditions = "metadata->>'tags' ?| %s"
        params = [tags] + [limit, offset]
    
    query = f"""
        SELECT contract_id, title, contract_type, status, metadata->>'tags' as tags
        FROM contracts
        WHERE {conditions}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    
    results = hook.get_records(query, parameters=tuple(params))
    
    contracts = []
    for row in results:
        contract_tags = []
        if row[4]:
            try:
                contract_tags = json.loads(row[4]) if isinstance(row[4], str) else row[4]
            except:
                pass
        
        contracts.append({
            "contract_id": row[0],
            "title": row[1],
            "contract_type": row[2],
            "status": row[3],
            "tags": contract_tags
        })
    
    # Conteo total
    count_query = f"SELECT COUNT(*) FROM contracts WHERE {conditions}"
    total_count = hook.get_first(count_query, parameters=tuple(params[:-2]))[0]
    
    return {
        "tags": tags,
        "match_all": match_all,
        "contracts": contracts,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }


def get_all_tags(
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Obtiene todas las tags únicas del sistema con conteo.
    
    Args:
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de tags con conteo de uso
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Extraer todas las tags y contar
    query = """
        SELECT 
            jsonb_array_elements_text(metadata->'tags') as tag,
            COUNT(*) as usage_count
        FROM contracts
        WHERE metadata->>'tags' IS NOT NULL
          AND jsonb_array_length(metadata->'tags') > 0
        GROUP BY tag
        ORDER BY usage_count DESC, tag
    """
    
    results = hook.get_records(query)
    
    return [
        {
            "tag": row[0],
            "usage_count": row[1]
        }
        for row in results
    ]

