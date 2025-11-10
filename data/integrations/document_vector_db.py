"""
Integración con Bases de Datos Vectoriales
===========================================

Integración con Pinecone, Weaviate, Qdrant para búsqueda semántica avanzada.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import logging
import numpy as np

logger = logging.getLogger(__name__)


class VectorDatabase:
    """Clase base para bases de datos vectoriales"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def upsert_document(
        self,
        document_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> bool:
        """Inserta o actualiza documento con embedding"""
        raise NotImplementedError
    
    def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Busca documentos similares"""
        raise NotImplementedError
    
    def delete_document(self, document_id: str) -> bool:
        """Elimina documento"""
        raise NotImplementedError


class PineconeVectorDB(VectorDatabase):
    """Integración con Pinecone"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            import pinecone
        except ImportError:
            raise ImportError(
                "pinecone-client es requerido. Instala con: pip install pinecone-client"
            )
        
        self.api_key = config.get("api_key")
        self.environment = config.get("environment", "us-east1-gcp")
        self.index_name = config.get("index_name", "documents")
        
        if not self.api_key:
            raise ValueError("Pinecone API key es requerido")
        
        pinecone.init(api_key=self.api_key, environment=self.environment)
        self.index = pinecone.Index(self.index_name)
    
    def upsert_document(
        self,
        document_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> bool:
        """Upsert en Pinecone"""
        try:
            self.index.upsert(
                vectors=[(document_id, embedding.tolist(), metadata)]
            )
            self.logger.info(f"Documento insertado en Pinecone: {document_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error insertando en Pinecone: {e}")
            return False
    
    def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Búsqueda en Pinecone"""
        try:
            query_response = self.index.query(
                vector=query_embedding.tolist(),
                top_k=top_k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            results = []
            for match in query_response.matches:
                results.append((
                    match.id,
                    match.score,
                    match.metadata or {}
                ))
            
            return results
        except Exception as e:
            self.logger.error(f"Error buscando en Pinecone: {e}")
            return []


class QdrantVectorDB(VectorDatabase):
    """Integración con Qdrant"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams, PointStruct
        except ImportError:
            raise ImportError(
                "qdrant-client es requerido. Instala con: pip install qdrant-client"
            )
        
        self.url = config.get("url", "http://localhost:6333")
        self.api_key = config.get("api_key")
        self.collection_name = config.get("collection_name", "documents")
        
        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key
        )
        
        # Crear colección si no existe
        try:
            self.client.get_collection(self.collection_name)
        except:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=384,  # Tamaño por defecto para embeddings
                    distance=Distance.COSINE
                )
            )
    
    def upsert_document(
        self,
        document_id: str,
        embedding: np.ndarray,
        metadata: Dict[str, Any]
    ) -> bool:
        """Upsert en Qdrant"""
        try:
            point = PointStruct(
                id=document_id,
                vector=embedding.tolist(),
                payload=metadata
            )
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            self.logger.info(f"Documento insertado en Qdrant: {document_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error insertando en Qdrant: {e}")
            return False
    
    def search_similar(
        self,
        query_embedding: np.ndarray,
        top_k: int = 10,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Tuple[str, float, Dict[str, Any]]]:
        """Búsqueda en Qdrant"""
        try:
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            query_filter = None
            if filter_metadata:
                conditions = [
                    FieldCondition(key=key, match=MatchValue(value=value))
                    for key, value in filter_metadata.items()
                ]
                query_filter = Filter(must=conditions)
            
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding.tolist(),
                limit=top_k,
                query_filter=query_filter
            )
            
            results = []
            for point in search_result:
                results.append((
                    str(point.id),
                    point.score,
                    point.payload or {}
                ))
            
            return results
        except Exception as e:
            self.logger.error(f"Error buscando en Qdrant: {e}")
            return []


def create_vector_db(provider: str, config: Dict[str, Any]) -> VectorDatabase:
    """Factory para crear bases de datos vectoriales"""
    provider_lower = provider.lower()
    
    if provider_lower == "pinecone":
        return PineconeVectorDB(config)
    elif provider_lower == "qdrant":
        return QdrantVectorDB(config)
    else:
        raise ValueError(f"Proveedor de vector DB no soportado: {provider}")

