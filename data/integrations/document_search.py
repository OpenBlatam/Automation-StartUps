"""
Búsqueda Semántica y por Contenido
===================================

Búsqueda avanzada en documentos procesados usando texto completo y semántica.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Resultado de búsqueda"""
    document_id: str
    document_type: str
    score: float
    matched_fields: Dict[str, Any]
    matched_text: Optional[str] = None
    highlights: List[str] = None


class DocumentSearcher:
    """Buscador de documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def search_by_text(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        case_sensitive: bool = False,
        max_results: int = 50
    ) -> List[SearchResult]:
        """Búsqueda por texto completo"""
        results = []
        
        query_lower = query.lower() if not case_sensitive else query
        
        for doc in documents:
            text = doc.get("extracted_text", "")
            text_search = text.lower() if not case_sensitive else text
            
            if query_lower in text_search:
                # Calcular score basado en número de ocurrencias
                occurrences = text_search.count(query_lower)
                score = min(occurrences / 10.0, 1.0)  # Normalizar
                
                # Extraer contexto
                highlights = self._extract_highlights(
                    text, query, case_sensitive
                )
                
                results.append(SearchResult(
                    document_id=doc.get("document_id", ""),
                    document_type=doc.get("document_type", ""),
                    score=score,
                    matched_fields={},
                    matched_text=text[:200],  # Primeros 200 caracteres
                    highlights=highlights
                ))
        
        # Ordenar por score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:max_results]
    
    def search_by_field(
        self,
        field_name: str,
        field_value: str,
        documents: List[Dict[str, Any]],
        exact_match: bool = False,
        max_results: int = 50
    ) -> List[SearchResult]:
        """Búsqueda por campo específico"""
        results = []
        
        field_value_lower = field_value.lower()
        
        for doc in documents:
            extracted_fields = doc.get("extracted_fields", {})
            field_data = extracted_fields.get(field_name)
            
            if field_data:
                field_str = str(field_data).lower()
                
                if exact_match:
                    match = field_str == field_value_lower
                else:
                    match = field_value_lower in field_str
                
                if match:
                    score = 1.0 if exact_match else 0.8
                    
                    results.append(SearchResult(
                        document_id=doc.get("document_id", ""),
                        document_type=doc.get("document_type", ""),
                        score=score,
                        matched_fields={field_name: field_data},
                        highlights=[f"{field_name}: {field_data}"]
                    ))
        
        return results[:max_results]
    
    def search_by_multiple_criteria(
        self,
        criteria: Dict[str, Any],
        documents: List[Dict[str, Any]],
        max_results: int = 50
    ) -> List[SearchResult]:
        """Búsqueda por múltiples criterios"""
        results = []
        
        for doc in documents:
            score = 0.0
            matched_fields = {}
            total_criteria = len(criteria)
            
            # Texto completo
            if "text" in criteria:
                text = doc.get("extracted_text", "")
                query = criteria["text"].lower()
                if query in text.lower():
                    score += 0.4
                    matched_fields["text_match"] = True
            
            # Campos específicos
            extracted_fields = doc.get("extracted_fields", {})
            for field_name, field_value in criteria.items():
                if field_name == "text":
                    continue
                
                doc_value = extracted_fields.get(field_name)
                if doc_value:
                    if str(doc_value).lower() == str(field_value).lower():
                        score += 0.6 / total_criteria
                        matched_fields[field_name] = doc_value
            
            # Tipo de documento
            if "document_type" in criteria:
                if doc.get("document_type") == criteria["document_type"]:
                    score += 0.2
                    matched_fields["document_type"] = doc.get("document_type")
            
            # Rango de fechas
            if "date_from" in criteria or "date_to" in criteria:
                doc_date = doc.get("extracted_fields", {}).get("date")
                if doc_date:
                    # Simplificado - asumir formato YYYY-MM-DD
                    try:
                        doc_date_obj = datetime.strptime(str(doc_date)[:10], "%Y-%m-%d")
                        date_from = criteria.get("date_from")
                        date_to = criteria.get("date_to")
                        
                        if date_from:
                            from_date = datetime.strptime(date_from, "%Y-%m-%d")
                            if doc_date_obj >= from_date:
                                score += 0.1
                        if date_to:
                            to_date = datetime.strptime(date_to, "%Y-%m-%d")
                            if doc_date_obj <= to_date:
                                score += 0.1
                    except:
                        pass
            
            if score > 0:
                results.append(SearchResult(
                    document_id=doc.get("document_id", ""),
                    document_type=doc.get("document_type", ""),
                    score=score,
                    matched_fields=matched_fields,
                    highlights=[]
                ))
        
        # Ordenar por score
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:max_results]
    
    def _extract_highlights(
        self,
        text: str,
        query: str,
        case_sensitive: bool = False
    ) -> List[str]:
        """Extrae fragmentos de texto con el query"""
        highlights = []
        text_lower = text.lower() if not case_sensitive else text
        query_lower = query.lower() if not case_sensitive else query
        
        # Encontrar todas las ocurrencias
        start = 0
        while True:
            idx = text_lower.find(query_lower, start)
            if idx == -1:
                break
            
            # Extraer contexto (50 caracteres antes y después)
            context_start = max(0, idx - 50)
            context_end = min(len(text), idx + len(query) + 50)
            highlight = text[context_start:context_end]
            
            if highlight not in highlights:
                highlights.append(highlight)
            
            start = idx + 1
            
            if len(highlights) >= 5:  # Máximo 5 highlights
                break
        
        return highlights
    
    def fuzzy_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        threshold: float = 0.6,
        max_results: int = 50
    ) -> List[SearchResult]:
        """Búsqueda difusa (tolerante a errores)"""
        from difflib import SequenceMatcher
        
        results = []
        
        query_lower = query.lower()
        
        for doc in documents:
            text = doc.get("extracted_text", "").lower()
            
            # Búsqueda por palabras
            query_words = query_lower.split()
            text_words = text.split()
            
            matches = 0
            for q_word in query_words:
                for t_word in text_words:
                    similarity = SequenceMatcher(None, q_word, t_word).ratio()
                    if similarity >= threshold:
                        matches += 1
                        break
            
            if matches > 0:
                score = matches / len(query_words)
                
                if score >= threshold:
                    results.append(SearchResult(
                        document_id=doc.get("document_id", ""),
                        document_type=doc.get("document_type", ""),
                        score=score,
                        matched_fields={},
                        matched_text=text[:200]
                    ))
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:max_results]

