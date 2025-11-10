"""
API GraphQL para Documentos
============================

API GraphQL para consultas flexibles de documentos.
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

try:
    from graphql import (
        GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString,
        GraphQLInt, GraphQLList, GraphQLFloat, GraphQLBoolean, GraphQLNonNull
    )
    GRAPHQL_AVAILABLE = True
except ImportError:
    GRAPHQL_AVAILABLE = False
    logger.warning("graphql-core no disponible. Instala con: pip install graphql-core")


if GRAPHQL_AVAILABLE:
    # Tipo Documento
    DocumentType = GraphQLObjectType(
        'Document',
        fields={
            'document_id': GraphQLField(GraphQLNonNull(GraphQLString)),
            'original_filename': GraphQLField(GraphQLString),
            'document_type': GraphQLField(GraphQLString),
            'classification_confidence': GraphQLField(GraphQLFloat),
            'ocr_confidence': GraphQLField(GraphQLFloat),
            'extracted_text': GraphQLField(GraphQLString),
            'extracted_fields': GraphQLField(
                GraphQLString,  # JSON como string
                resolve=lambda obj, info: str(obj.get('extracted_fields', {}))
            ),
            'processed_at': GraphQLField(GraphQLString),
            'archive_path': GraphQLField(GraphQLString),
        }
    )
    
    # Query root
    QueryType = GraphQLObjectType(
        'Query',
        fields={
            'document': GraphQLField(
                DocumentType,
                args={
                    'document_id': GraphQLNonNull(GraphQLString)
                },
                resolve=lambda obj, info, document_id: get_document_by_id(document_id)
            ),
            'documents': GraphQLField(
                GraphQLList(DocumentType),
                args={
                    'document_type': GraphQLString,
                    'limit': GraphQLInt,
                    'offset': GraphQLInt
                },
                resolve=lambda obj, info, document_type=None, limit=10, offset=0: 
                    get_documents(document_type, limit, offset)
            ),
            'searchDocuments': GraphQLField(
                GraphQLList(DocumentType),
                args={
                    'query': GraphQLNonNull(GraphQLString),
                    'limit': GraphQLInt
                },
                resolve=lambda obj, info, query, limit=10: 
                    search_documents(query, limit)
            ),
        }
    )
    
    # Schema
    schema = GraphQLSchema(query=QueryType)


def get_document_by_id(document_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene documento por ID (simplificado)"""
    # En producción, consultaría la BD
    return None


def get_documents(
    document_type: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Obtiene documentos (simplificado)"""
    # En producción, consultaría la BD
    return []


def search_documents(query: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Busca documentos (simplificado)"""
    # En producción, usaría el buscador
    return []


class GraphQLAPI:
    """API GraphQL para documentos"""
    
    def __init__(self, db_connection=None):
        if not GRAPHQL_AVAILABLE:
            raise ImportError("graphql-core es requerido")
        
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None):
        """Ejecuta query GraphQL"""
        try:
            from graphql import graphql_sync
            
            result = graphql_sync(schema, query, variable_values=variables)
            return {
                "data": result.data,
                "errors": [str(e) for e in result.errors] if result.errors else None
            }
        except Exception as e:
            self.logger.error(f"Error ejecutando query GraphQL: {e}")
            return {"data": None, "errors": [str(e)]}

