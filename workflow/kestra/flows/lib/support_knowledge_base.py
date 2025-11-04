"""
Sistema de Knowledge Base Avanzado.

Características:
- Búsqueda semántica mejorada
- Clustering de FAQs similares
- Sugerencias de mejora de FAQs
- Análisis de gaps en conocimiento
- Auto-actualización de FAQs basado en feedback
"""
import logging
import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeGap:
    """Gap identificado en knowledge base."""
    query: str
    frequency: int
    suggested_faq_title: str
    suggested_content: str
    confidence: float


class SupportKnowledgeBase:
    """Sistema avanzado de knowledge base."""
    
    def __init__(self, db_connection: Any = None):
        """
        Inicializa el sistema de knowledge base.
        
        Args:
            db_connection: Conexión a BD
        """
        self.db_connection = db_connection
    
    def find_similar_faqs(
        self,
        query: str,
        threshold: float = 0.6,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Encuentra FAQs similares usando búsqueda mejorada.
        
        Args:
            query: Consulta del usuario
            threshold: Umbral de similitud
            limit: Número máximo de resultados
            
        Returns:
            Lista de FAQs similares
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Búsqueda mejorada con múltiples criterios
            query_lower = query.lower()
            query_words = set(re.findall(r'\b\w+\b', query_lower))
            
            sql = """
                SELECT 
                    article_id,
                    title,
                    content,
                    summary,
                    category,
                    tags,
                    keywords,
                    view_count,
                    helpful_count,
                    -- Calcular score de relevancia
                    (
                        CASE WHEN LOWER(title) LIKE %s THEN 3 ELSE 0 END +
                        CASE WHEN LOWER(content) LIKE %s THEN 2 ELSE 0 END +
                        CASE WHEN LOWER(summary) LIKE %s THEN 2 ELSE 0 END +
                        CASE WHEN tags && %s THEN 2 ELSE 0 END +
                        CASE WHEN keywords && %s THEN 1 ELSE 0 END +
                        (view_count::float / 100.0) +
                        (helpful_count::float / 10.0)
                    ) as relevance_score
                FROM support_faq_articles
                WHERE is_active = true
                AND (
                    LOWER(title) LIKE %s
                    OR LOWER(content) LIKE %s
                    OR LOWER(summary) LIKE %s
                    OR tags && %s
                    OR keywords && %s
                )
                ORDER BY relevance_score DESC
                LIMIT %s
            """
            
            query_pattern = f"%{query_lower}%"
            tags_array = list(query_words)
            keywords_array = list(query_words)
            
            cursor.execute(sql, (
                query_pattern, query_pattern, query_pattern,
                tags_array, keywords_array,
                query_pattern, query_pattern, query_pattern,
                tags_array, keywords_array,
                limit
            ))
            
            results = []
            for row in cursor.fetchall():
                score = float(row[8]) if row[8] else 0.0
                if score >= threshold:
                    results.append({
                        "article_id": row[0],
                        "title": row[1],
                        "content": row[2],
                        "summary": row[3],
                        "category": row[4],
                        "tags": row[5] if row[5] else [],
                        "keywords": row[6] if row[6] else [],
                        "relevance_score": score
                    })
            
            cursor.close()
            return results
            
        except Exception as e:
            logger.error(f"Error finding similar FAQs: {e}", exc_info=True)
            return []
    
    def identify_knowledge_gaps(
        self,
        days: int = 30
    ) -> List[KnowledgeGap]:
        """
        Identifica gaps en knowledge base basado en consultas no resueltas.
        
        Args:
            days: Días de historial a analizar
            
        Returns:
            Lista de gaps identificados
        """
        if not self.db_connection:
            return []
        
        try:
            cursor = self.db_connection.cursor()
            
            # Buscar consultas que no fueron resueltas por chatbot
            cursor.execute("""
                SELECT 
                    description,
                    COUNT(*) as frequency,
                    COUNT(*) FILTER (WHERE chatbot_resolved = false) as unresolved_count
                FROM support_tickets
                WHERE created_at >= NOW() - INTERVAL '%s days'
                AND chatbot_attempted = true
                AND chatbot_resolved = false
                GROUP BY description
                HAVING COUNT(*) >= 3  -- Mínimo 3 ocurrencias
                ORDER BY unresolved_count DESC, frequency DESC
                LIMIT 20
            """, (days,))
            
            gaps = []
            for row in cursor.fetchall():
                query = row[0]
                frequency = row[1]
                
                # Generar sugerencia de FAQ
                suggested_title = self._generate_faq_title(query)
                suggested_content = self._generate_faq_content(query)
                
                gaps.append(KnowledgeGap(
                    query=query,
                    frequency=frequency,
                    suggested_faq_title=suggested_title,
                    suggested_content=suggested_content,
                    confidence=min(1.0, frequency / 10.0)  # Más frecuencia = más confianza
                ))
            
            cursor.close()
            return gaps
            
        except Exception as e:
            logger.error(f"Error identifying knowledge gaps: {e}", exc_info=True)
            return []
    
    def _generate_faq_title(self, query: str) -> str:
        """Genera un título sugerido para FAQ basado en query."""
        # Extraer palabras clave principales
        words = re.findall(r'\b\w+\b', query.lower())
        # Remover palabras comunes
        stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'que', 'como', 'para', 'con', 'en', 'por'}
        keywords = [w for w in words if w not in stop_words and len(w) > 3]
        
        if keywords:
            # Usar primera palabra clave como base
            title = keywords[0].capitalize()
            if len(keywords) > 1:
                title += f" {keywords[1]}"
            return f"¿Cómo {title}?"
        
        return "Pregunta frecuente"
    
    def _generate_faq_content(self, query: str) -> str:
        """Genera contenido sugerido para FAQ."""
        # En producción, esto podría usar LLM para generar contenido
        return f"Información sobre: {query}\n\n[Este contenido debe ser completado manualmente basado en la consulta común]"
    
    def update_faq_effectiveness(
        self,
        article_id: str,
        was_helpful: bool
    ) -> bool:
        """Actualiza métricas de efectividad de un FAQ."""
        if not self.db_connection:
            return False
        
        try:
            cursor = self.db_connection.cursor()
            
            if was_helpful:
                cursor.execute("""
                    UPDATE support_faq_articles
                    SET helpful_count = helpful_count + 1,
                        last_updated_at = NOW()
                    WHERE article_id = %s
                """, (article_id,))
            else:
                cursor.execute("""
                    UPDATE support_faq_articles
                    SET not_helpful_count = not_helpful_count + 1,
                        last_updated_at = NOW()
                    WHERE article_id = %s
                """, (article_id,))
            
            self.db_connection.commit()
            cursor.close()
            return True
            
        except Exception as e:
            logger.error(f"Error updating FAQ effectiveness: {e}")
            return False

