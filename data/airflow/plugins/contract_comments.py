"""
Sistema de Comentarios y Revisiones para Contratos
Permite comentarios, revisiones y colaboración
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


def add_comment_to_contract(
    contract_id: str,
    comment_text: str,
    author_email: str,
    author_name: str = None,
    comment_type: str = "comment",  # 'comment', 'review', 'suggestion', 'question'
    is_internal: bool = True,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Agrega un comentario a un contrato.
    
    Args:
        contract_id: ID del contrato
        comment_text: Texto del comentario
        author_email: Email del autor
        author_name: Nombre del autor
        comment_type: Tipo de comentario
        is_internal: Si es comentario interno (no visible para firmantes)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información del comentario
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Verificar que el contrato existe
    contract_query = "SELECT contract_id FROM contracts WHERE contract_id = %s"
    contract = hook.get_first(contract_query, parameters=(contract_id,))
    
    if not contract:
        raise ValueError(f"Contrato {contract_id} no encontrado")
    
    # Insertar comentario
    comment_id = f"COMMENT-{contract_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    insert_query = """
        INSERT INTO contract_comments (
            comment_id, contract_id, comment_text, author_email, author_name,
            comment_type, is_internal, created_at
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
    """
    
    hook.run(
        insert_query,
        parameters=(
            comment_id,
            contract_id,
            comment_text,
            author_email,
            author_name or author_email.split('@')[0],
            comment_type,
            is_internal
        )
    )
    
    logger.info(
        f"Comentario agregado a contrato {contract_id}",
        extra={"comment_id": comment_id, "type": comment_type}
    )
    
    return {
        "comment_id": comment_id,
        "contract_id": contract_id,
        "comment_text": comment_text,
        "author_email": author_email,
        "author_name": author_name or author_email.split('@')[0],
        "comment_type": comment_type,
        "is_internal": is_internal,
        "created_at": datetime.now().isoformat()
    }


def get_contract_comments(
    contract_id: str,
    include_internal: bool = True,
    comment_type: str = None,
    postgres_conn_id: str = "postgres_default"
) -> List[Dict[str, Any]]:
    """
    Obtiene todos los comentarios de un contrato.
    
    Args:
        contract_id: ID del contrato
        include_internal: Incluir comentarios internos
        comment_type: Filtrar por tipo (opcional)
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Lista de comentarios
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    where_clauses = ["contract_id = %s"]
    params = [contract_id]
    
    if not include_internal:
        where_clauses.append("is_internal = false")
    
    if comment_type:
        where_clauses.append("comment_type = %s")
        params.append(comment_type)
    
    query = f"""
        SELECT comment_id, comment_text, author_email, author_name,
               comment_type, is_internal, created_at, updated_at
        FROM contract_comments
        WHERE {' AND '.join(where_clauses)}
        ORDER BY created_at ASC
    """
    
    comments = hook.get_records(query, parameters=tuple(params))
    
    return [
        {
            "comment_id": row[0],
            "comment_text": row[1],
            "author_email": row[2],
            "author_name": row[3],
            "comment_type": row[4],
            "is_internal": row[5],
            "created_at": row[6].isoformat() if row[6] else None,
            "updated_at": row[7].isoformat() if row[7] else None
        }
        for row in comments
    ]


def update_comment(
    comment_id: str,
    comment_text: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Actualiza un comentario existente.
    
    Args:
        comment_id: ID del comentario
        comment_text: Nuevo texto
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con información actualizada
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    update_query = """
        UPDATE contract_comments
        SET comment_text = %s, updated_at = NOW()
        WHERE comment_id = %s
        RETURNING contract_id, author_email, comment_type
    """
    
    result = hook.get_first(
        update_query,
        parameters=(comment_text, comment_id)
    )
    
    if not result:
        raise ValueError(f"Comentario {comment_id} no encontrado")
    
    return {
        "comment_id": comment_id,
        "comment_text": comment_text,
        "contract_id": result[0],
        "updated_at": datetime.now().isoformat()
    }


def delete_comment(
    comment_id: str,
    postgres_conn_id: str = "postgres_default"
) -> Dict[str, Any]:
    """
    Elimina un comentario.
    
    Args:
        comment_id: ID del comentario
        postgres_conn_id: Connection ID de Airflow
        
    Returns:
        Dict con confirmación
    """
    if not POSTGRES_AVAILABLE:
        raise ImportError("PostgreSQL hook no disponible")
    
    hook = PostgresHook(postgres_conn_id=postgres_conn_id)
    
    # Obtener información antes de eliminar
    query = "SELECT contract_id FROM contract_comments WHERE comment_id = %s"
    result = hook.get_first(query, parameters=(comment_id,))
    
    if not result:
        raise ValueError(f"Comentario {comment_id} no encontrado")
    
    # Eliminar
    hook.run("DELETE FROM contract_comments WHERE comment_id = %s", parameters=(comment_id,))
    
    return {
        "comment_id": comment_id,
        "contract_id": result[0],
        "deleted_at": datetime.now().isoformat()
    }

