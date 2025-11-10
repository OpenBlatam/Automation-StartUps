"""
Sistema de Indexación para Búsqueda Rápida
===========================================

Indexa documentos para búsqueda rápida usando Elasticsearch o similar.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentIndexer:
    """Indexador de documentos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.client = None
        self.index_name = config.get("index_name", "documents")
        self._initialize_client()
    
    def _initialize_client(self):
        """Inicializa cliente de indexación"""
        provider = self.config.get("provider", "elasticsearch")
        
        if provider == "elasticsearch":
            try:
                from elasticsearch import Elasticsearch
                self.client = Elasticsearch(
                    hosts=self.config.get("hosts", ["localhost:9200"]),
                    http_auth=self.config.get("auth")
                )
                self.logger.info("Cliente Elasticsearch inicializado")
            except ImportError:
                self.logger.warning(
                    "elasticsearch no disponible. "
                    "Instala con: pip install elasticsearch"
                )
    
    def index_document(self, document: Dict[str, Any]) -> bool:
        """Indexa un documento"""
        if not self.client:
            return False
        
        try:
            doc_body = {
                "document_id": document.get("document_id"),
                "original_filename": document.get("original_filename"),
                "document_type": document.get("document_type"),
                "extracted_text": document.get("extracted_text", ""),
                "extracted_fields": document.get("extracted_fields", {}),
                "classification_confidence": document.get("classification_confidence"),
                "ocr_confidence": document.get("ocr_confidence"),
                "processed_at": document.get("processed_at"),
                "archive_path": document.get("archive_path")
            }
            
            self.client.index(
                index=self.index_name,
                id=document.get("document_id"),
                body=doc_body
            )
            
            self.logger.info(f"Documento indexado: {document.get('document_id')}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error indexando documento: {e}")
            return False
    
    def search(
        self,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        size: int = 10
    ) -> List[Dict[str, Any]]:
        """Busca documentos indexados"""
        if not self.client:
            return []
        
        try:
            search_body = {
                "query": {
                    "multi_match": {
                        "query": query,
                        "fields": ["extracted_text^2", "original_filename", "extracted_fields.*"]
                    }
                },
                "size": size
            }
            
            # Agregar filtros
            if filters:
                search_body["query"] = {
                    "bool": {
                        "must": [search_body["query"]],
                        "filter": [
                            {"term": {k: v}} for k, v in filters.items()
                        ]
                    }
                }
            
            response = self.client.search(
                index=self.index_name,
                body=search_body
            )
            
            results = []
            for hit in response["hits"]["hits"]:
                results.append({
                    "document_id": hit["_id"],
                    "score": hit["_score"],
                    "source": hit["_source"]
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Error buscando: {e}")
            return []
    
    def delete_document(self, document_id: str) -> bool:
        """Elimina documento del índice"""
        if not self.client:
            return False
        
        try:
            self.client.delete(index=self.index_name, id=document_id)
            return True
        except Exception as e:
            self.logger.error(f"Error eliminando del índice: {e}")
            return False
    
    def bulk_index(self, documents: List[Dict[str, Any]]) -> int:
        """Indexa múltiples documentos"""
        if not self.client:
            return 0
        
        try:
            from elasticsearch.helpers import bulk
            
            actions = []
            for doc in documents:
                action = {
                    "_index": self.index_name,
                    "_id": doc.get("document_id"),
                    "_source": {
                        "document_id": doc.get("document_id"),
                        "original_filename": doc.get("original_filename"),
                        "document_type": doc.get("document_type"),
                        "extracted_text": doc.get("extracted_text", ""),
                        "extracted_fields": doc.get("extracted_fields", {}),
                        "processed_at": doc.get("processed_at")
                    }
                }
                actions.append(action)
            
            success, failed = bulk(self.client, actions)
            self.logger.info(f"Indexados {success} documentos, {len(failed)} fallaron")
            return success
            
        except Exception as e:
            self.logger.error(f"Error en bulk index: {e}")
            return 0

