"""
Comparación y Detección de Duplicados
======================================

Compara documentos y detecta duplicados usando múltiples técnicas.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import hashlib
from datetime import datetime
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class SimilarityLevel(Enum):
    """Niveles de similitud"""
    IDENTICAL = "identical"
    VERY_SIMILAR = "very_similar"
    SIMILAR = "similar"
    DIFFERENT = "different"


@dataclass
class DocumentComparison:
    """Resultado de comparación entre documentos"""
    document1_id: str
    document2_id: str
    similarity_score: float  # 0-1
    similarity_level: SimilarityLevel
    text_similarity: float
    field_similarity: float
    hash_similarity: float
    differences: List[str]
    matched_fields: Dict[str, Tuple[Any, Any]]
    compared_at: str


class DocumentComparator:
    """Comparador de documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compare_documents(
        self,
        doc1: Dict[str, Any],
        doc2: Dict[str, Any]
    ) -> DocumentComparison:
        """Compara dos documentos"""
        doc1_id = doc1.get("document_id", "")
        doc2_id = doc2.get("document_id", "")
        
        # 1. Comparación de texto completo
        text1 = doc1.get("extracted_text", "")
        text2 = doc2.get("extracted_text", "")
        text_similarity = self._text_similarity(text1, text2)
        
        # 2. Comparación de campos
        fields1 = doc1.get("extracted_fields", {})
        fields2 = doc2.get("extracted_fields", {})
        field_similarity, matched_fields = self._field_similarity(fields1, fields2)
        
        # 3. Comparación de hash
        hash1 = doc1.get("file_hash", "")
        hash2 = doc2.get("file_hash", "")
        hash_similarity = 1.0 if hash1 == hash2 else 0.0
        
        # 4. Score combinado
        similarity_score = (
            text_similarity * 0.4 +
            field_similarity * 0.4 +
            hash_similarity * 0.2
        )
        
        # 5. Determinar nivel de similitud
        if similarity_score >= 0.99:
            level = SimilarityLevel.IDENTICAL
        elif similarity_score >= 0.85:
            level = SimilarityLevel.VERY_SIMILAR
        elif similarity_score >= 0.70:
            level = SimilarityLevel.SIMILAR
        else:
            level = SimilarityLevel.DIFFERENT
        
        # 6. Detectar diferencias
        differences = self._find_differences(doc1, doc2)
        
        return DocumentComparison(
            document1_id=doc1_id,
            document2_id=doc2_id,
            similarity_score=similarity_score,
            similarity_level=level,
            text_similarity=text_similarity,
            field_similarity=field_similarity,
            hash_similarity=hash_similarity,
            differences=differences,
            matched_fields=matched_fields,
            compared_at=datetime.now().isoformat()
        )
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calcula similitud de texto usando SequenceMatcher"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    def _field_similarity(
        self,
        fields1: Dict[str, Any],
        fields2: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Tuple[Any, Any]]]:
        """Calcula similitud de campos"""
        if not fields1 and not fields2:
            return 1.0, {}
        if not fields1 or not fields2:
            return 0.0, {}
        
        all_keys = set(fields1.keys()) | set(fields2.keys())
        if not all_keys:
            return 1.0, {}
        
        matches = 0
        matched_fields = {}
        
        for key in all_keys:
            val1 = fields1.get(key)
            val2 = fields2.get(key)
            
            if val1 == val2:
                matches += 1
                matched_fields[key] = (val1, val2)
            elif val1 and val2:
                # Comparar strings similares
                if str(val1).lower().strip() == str(val2).lower().strip():
                    matches += 1
                    matched_fields[key] = (val1, val2)
        
        similarity = matches / len(all_keys) if all_keys else 0.0
        return similarity, matched_fields
    
    def _find_differences(
        self,
        doc1: Dict[str, Any],
        doc2: Dict[str, Any]
    ) -> List[str]:
        """Encuentra diferencias entre documentos"""
        differences = []
        
        # Comparar tipo
        if doc1.get("document_type") != doc2.get("document_type"):
            differences.append(
                f"Tipo diferente: {doc1.get('document_type')} vs {doc2.get('document_type')}"
            )
        
        # Comparar campos
        fields1 = doc1.get("extracted_fields", {})
        fields2 = doc2.get("extracted_fields", {})
        
        all_keys = set(fields1.keys()) | set(fields2.keys())
        for key in all_keys:
            val1 = fields1.get(key)
            val2 = fields2.get(key)
            
            if val1 != val2:
                differences.append(
                    f"Campo '{key}': '{val1}' vs '{val2}'"
                )
        
        return differences
    
    def find_duplicates(
        self,
        documents: List[Dict[str, Any]],
        threshold: float = 0.95
    ) -> List[Tuple[Dict[str, Any], Dict[str, Any], float]]:
        """Encuentra documentos duplicados"""
        duplicates = []
        
        for i in range(len(documents)):
            for j in range(i + 1, len(documents)):
                comparison = self.compare_documents(documents[i], documents[j])
                
                if comparison.similarity_score >= threshold:
                    duplicates.append((
                        documents[i],
                        documents[j],
                        comparison.similarity_score
                    ))
        
        return duplicates
    
    def find_similar_documents(
        self,
        query_document: Dict[str, Any],
        document_list: List[Dict[str, Any]],
        min_similarity: float = 0.7,
        max_results: int = 10
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Encuentra documentos similares a uno dado"""
        similarities = []
        
        for doc in document_list:
            if doc.get("document_id") == query_document.get("document_id"):
                continue
            
            comparison = self.compare_documents(query_document, doc)
            
            if comparison.similarity_score >= min_similarity:
                similarities.append((doc, comparison.similarity_score))
        
        # Ordenar por similitud
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:max_results]

