"""
Sistema de Búsqueda Full-Text Avanzado para Contratos
Búsqueda semántica y por contenido
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


def full_text_search(
    search_query: str,
    search_fields: List[str] = None,
    contract_type: str = None,
    status: str = None,
    date_range: Dict[str, str] = None,
    limit: int = 50,
    offset: int = 0,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Búsqueda full-text avanzada en contratos usando PostgreSQL tsvector.
    
    Args:
        search_query: Término de búsqueda
        search_fields: Campos a buscar ['title', 'description', 'content']
        contract_type: Filtrar por tipo
        status: Filtrar por estado
        date_range: {'start': 'YYYY-MM-DD', 'end': 'YYYY-MM-DD'}
        limit: Límite de resultados
        offset: Offset para paginación
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con resultados y ranking
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Preparar campos de búsqueda
    if not search_fields:
        search_fields = ['title', 'description', 'contract_content']
    
    # Construir query de búsqueda full-text
    # Crear índice tsvector si no existe (una vez)
    # CREATE INDEX IF NOT EXISTS idx_contracts_fts ON contracts USING gin(to_tsvector('spanish', coalesce(title, '') || ' ' || coalesce(description, '') || ' ' || coalesce(contract_content, '')));
    
    where_clauses = []
    params = []
    param_count = 0
    
    # Búsqueda full-text
    if search_query:
        param_count += 1
        search_tsquery = search_query.replace(' ', ' & ')
        where_clauses.append(
            f"to_tsvector('spanish', coalesce(title, '') || ' ' || "
            f"coalesce(description, '') || ' ' || coalesce(contract_content, '')) "
            f"@@ plainto_tsquery('spanish', %s)"
        )
        params.append(search_query)
    
    # Filtros adicionales
    if contract_type:
        param_count += 1
        where_clauses.append(f"contract_type = %s")
        params.append(contract_type)
    
    if status:
        param_count += 1
        where_clauses.append(f"status = %s")
        params.append(status)
    
    if date_range:
        if date_range.get('start'):
            param_count += 1
            where_clauses.append(f"created_at >= %s")
            params.append(date_range['start'])
        if date_range.get('end'):
            param_count += 1
            where_clauses.append(f"created_at <= %s")
            params.append(date_range['end'])
    
    where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    # Query con ranking
    query = f"""
        SELECT 
            contract_id,
            title,
            contract_type,
            status,
            primary_party_name,
            primary_party_email,
            created_at,
            ts_rank(
                to_tsvector('spanish', coalesce(title, '') || ' ' || 
                           coalesce(description, '') || ' ' || 
                           coalesce(contract_content, '')),
                plainto_tsquery('spanish', %s)
            ) as rank
        FROM contracts
        WHERE {where_sql}
        ORDER BY rank DESC, created_at DESC
        LIMIT %s OFFSET %s
    """
    
    # Agregar search_query para ranking si existe
    if search_query:
        params.insert(0, search_query)
    
    params.extend([limit, offset])
    
    results = hook.get_records(query, parameters=tuple(params))
    
    contracts = []
    for row in results:
        contracts.append({
            "contract_id": row[0],
            "title": row[1],
            "contract_type": row[2],
            "status": row[3],
            "primary_party_name": row[4],
            "primary_party_email": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "relevance_score": float(row[7]) if row[7] else 0.0
        })
    
    # Conteo total
    count_query = f"SELECT COUNT(*) FROM contracts WHERE {where_sql}"
    count_params = params[:-2]  # Remover limit y offset
    total_count = hook.get_first(count_query, parameters=tuple(count_params))[0]
    
    return {
        "query": search_query,
        "contracts": contracts,
        "total_count": total_count,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total_count
    }


def search_by_similarity(
    contract_id: str,
    similarity_threshold: float = 0.7,
    limit: int = 10,
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Encuentra contratos similares a uno dado.
    
    Args:
        contract_id: ID del contrato de referencia
        similarity_threshold: Umbral de similitud (0-1)
        limit: Límite de resultados
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de contratos similares
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener contrato de referencia
    ref_query = """
        SELECT contract_type, title, description, contract_content
        FROM contracts
        WHERE contract_id = %s
    """
    ref_contract = hook.get_first(ref_query, parameters=(contract_id,))
    
    if not ref_contract:
        return []
    
    # Buscar contratos similares usando similitud de texto
    # PostgreSQL tiene pg_trgm extension para similitud
    similarity_query = """
        SELECT 
            contract_id,
            title,
            contract_type,
            status,
            similarity(
                coalesce(title, '') || ' ' || coalesce(description, ''),
                %s || ' ' || %s
            ) as sim_score
        FROM contracts
        WHERE contract_id != %s
          AND contract_type = %s
          AND similarity(
              coalesce(title, '') || ' ' || coalesce(description, ''),
              %s || ' ' || %s
          ) >= %s
        ORDER BY sim_score DESC
        LIMIT %s
    """
    
    ref_title = ref_contract[1] or ""
    ref_desc = ref_contract[2] or ""
    ref_type = ref_contract[0]
    
    results = hook.get_records(
        similarity_query,
        parameters=(
            ref_title, ref_desc, contract_id, ref_type,
            ref_title, ref_desc, similarity_threshold, limit
        )
    )
    
    similar_contracts = []
    for row in results:
        similar_contracts.append({
            "contract_id": row[0],
            "title": row[1],
            "contract_type": row[2],
            "status": row[3],
            "similarity_score": float(row[4]) if row[4] else 0.0
        })
    
    return similar_contracts


def create_fts_index(postgres_conn_id: str = "postgres_default") -> bool:
    """
    Crea índices full-text search para mejorar búsquedas.
    
    Args:
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        True si se crearon exitosamente
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    try:
        # Crear extensión pg_trgm si no existe (para similitud)
        hook.run("CREATE EXTENSION IF NOT EXISTS pg_trgm")
        
        # Crear índice GIN para búsqueda full-text
        fts_index_query = """
            CREATE INDEX IF NOT EXISTS idx_contracts_fts 
            ON contracts USING gin(
                to_tsvector('spanish', 
                    coalesce(title, '') || ' ' || 
                    coalesce(description, '') || ' ' || 
                    coalesce(contract_content, '')
                )
            )
        """
        hook.run(fts_index_query)
        
        # Crear índice para similitud
        similarity_index_query = """
            CREATE INDEX IF NOT EXISTS idx_contracts_similarity 
            ON contracts USING gin(
                (coalesce(title, '') || ' ' || coalesce(description, '')) gin_trgm_ops
            )
        """
        hook.run(similarity_index_query)
        
        logger.info("Índices full-text search creados exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error creando índices full-text: {e}")
        return False

