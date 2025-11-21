"""
Sistema de Detección de Tickets Duplicados.

Identifica tickets similares o duplicados usando múltiples técnicas:
similitud de texto, clustering, y análisis semántico.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import hashlib
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)


class SimilarityLevel(Enum):
    """Niveles de similitud."""
    EXACT = "exact"  # 100% igual
    VERY_HIGH = "very_high"  # >90%
    HIGH = "high"  # 70-90%
    MEDIUM = "medium"  # 50-70%
    LOW = "low"  # <50%


@dataclass
class DuplicateMatch:
    """Match de ticket duplicado."""
    ticket_id: str
    similar_ticket_id: str
    similarity_score: float
    similarity_level: SimilarityLevel
    matching_fields: List[str]
    matching_text: Optional[str] = None
    confidence: float = 0.0


@dataclass
class DuplicateGroup:
    """Grupo de tickets duplicados."""
    group_id: str
    ticket_ids: List[str]
    primary_ticket_id: str  # Ticket más antiguo o principal
    similarity_score: float
    detection_method: str
    created_at: datetime


class DuplicateDetector:
    """Detector de tickets duplicados."""
    
    def __init__(self, db_connection):
        """Inicializar detector."""
        self.db = db_connection
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.similarity_threshold = 0.7  # 70% de similitud
    
    def detect_duplicates(
        self,
        ticket_id: str,
        days_back: int = 30,
        min_similarity: float = 0.7
    ) -> List[DuplicateMatch]:
        """Detectar tickets duplicados para un ticket."""
        # Obtener ticket actual
        ticket = self._get_ticket(ticket_id)
        if not ticket:
            return []
        
        # Buscar tickets similares en el período
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        query = """
            SELECT ticket_id, subject, description, customer_email,
                   category, tags, created_at
            FROM support_tickets
            WHERE ticket_id != %s
                AND created_at >= %s
                AND status != 'closed'
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [ticket_id, start_date])
            candidates = cur.fetchall()
        
        matches = []
        
        for candidate in candidates:
            similarity = self._calculate_similarity(ticket, candidate)
            
            if similarity >= min_similarity:
                # Determinar nivel de similitud
                if similarity >= 0.95:
                    level = SimilarityLevel.EXACT
                elif similarity >= 0.90:
                    level = SimilarityLevel.VERY_HIGH
                elif similarity >= 0.70:
                    level = SimilarityLevel.HIGH
                elif similarity >= 0.50:
                    level = SimilarityLevel.MEDIUM
                else:
                    level = SimilarityLevel.LOW
                
                # Identificar campos que coinciden
                matching_fields = self._identify_matching_fields(ticket, candidate)
                
                matches.append(DuplicateMatch(
                    ticket_id=ticket_id,
                    similar_ticket_id=candidate[0],
                    similarity_score=similarity,
                    similarity_level=level,
                    matching_fields=matching_fields,
                    confidence=self._calculate_confidence(similarity, matching_fields)
                ))
        
        # Ordenar por similitud
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        
        return matches
    
    def _get_ticket(self, ticket_id: str) -> Optional[Dict[str, Any]]:
        """Obtener ticket."""
        query = """
            SELECT ticket_id, subject, description, customer_email,
                   category, tags, created_at
            FROM support_tickets
            WHERE ticket_id = %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [ticket_id])
            row = cur.fetchone()
        
        if not row:
            return None
        
        return {
            "ticket_id": row[0],
            "subject": row[1] or "",
            "description": row[2] or "",
            "customer_email": row[3],
            "category": row[4],
            "tags": row[5] or [],
            "created_at": row[6]
        }
    
    def _calculate_similarity(
        self,
        ticket1: Dict[str, Any],
        ticket2: Tuple
    ) -> float:
        """Calcular similitud entre dos tickets."""
        ticket2_dict = {
            "ticket_id": ticket2[0],
            "subject": ticket2[1] or "",
            "description": ticket2[2] or "",
            "customer_email": ticket2[3],
            "category": ticket2[4],
            "tags": ticket2[5] or []
        }
        
        scores = []
        
        # Similitud de subject (peso 0.3)
        subject_sim = self._text_similarity(
            ticket1["subject"].lower(),
            ticket2_dict["subject"].lower()
        )
        scores.append(("subject", subject_sim, 0.3))
        
        # Similitud de description (peso 0.5)
        desc_sim = self._text_similarity(
            ticket1["description"].lower(),
            ticket2_dict["description"].lower()
        )
        scores.append(("description", desc_sim, 0.5))
        
        # Mismo cliente (peso 0.1)
        if ticket1["customer_email"] == ticket2_dict["customer_email"]:
            scores.append(("customer", 1.0, 0.1))
        else:
            scores.append(("customer", 0.0, 0.1))
        
        # Misma categoría (peso 0.05)
        if ticket1["category"] == ticket2_dict["category"]:
            scores.append(("category", 1.0, 0.05))
        else:
            scores.append(("category", 0.0, 0.05))
        
        # Tags comunes (peso 0.05)
        tags1 = set(ticket1["tags"] or [])
        tags2 = set(ticket2_dict["tags"] or [])
        if tags1 and tags2:
            tag_sim = len(tags1 & tags2) / len(tags1 | tags2)
        else:
            tag_sim = 0.0
        scores.append(("tags", tag_sim, 0.05))
        
        # Calcular score ponderado
        total_score = sum(score * weight for _, score, weight in scores)
        
        return min(1.0, total_score)
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calcular similitud de texto."""
        if not text1 or not text2:
            return 0.0
        
        # Similitud usando SequenceMatcher
        ratio = SequenceMatcher(None, text1, text2).ratio()
        
        # Bonus por palabras comunes
        words1 = set(text1.split())
        words2 = set(text2.split())
        if words1 and words2:
            word_ratio = len(words1 & words2) / len(words1 | words2)
            # Combinar ambos métodos
            ratio = (ratio * 0.7) + (word_ratio * 0.3)
        
        return ratio
    
    def _identify_matching_fields(
        self,
        ticket1: Dict[str, Any],
        ticket2: Tuple
    ) -> List[str]:
        """Identificar campos que coinciden."""
        matching = []
        
        ticket2_dict = {
            "subject": ticket2[1] or "",
            "description": ticket2[2] or "",
            "customer_email": ticket2[3],
            "category": ticket2[4]
        }
        
        if ticket1["customer_email"] == ticket2_dict["customer_email"]:
            matching.append("customer_email")
        
        if ticket1["category"] == ticket2_dict["category"]:
            matching.append("category")
        
        if self._text_similarity(
            ticket1["subject"].lower(),
            ticket2_dict["subject"].lower()
        ) > 0.8:
            matching.append("subject")
        
        if self._text_similarity(
            ticket1["description"].lower(),
            ticket2_dict["description"].lower()
        ) > 0.8:
            matching.append("description")
        
        return matching
    
    def _calculate_confidence(
        self,
        similarity: float,
        matching_fields: List[str]
    ) -> float:
        """Calcular confianza del match."""
        confidence = similarity
        
        # Bonus por múltiples campos coincidentes
        field_bonus = len(matching_fields) * 0.05
        confidence += min(0.15, field_bonus)
        
        # Bonus si email y categoría coinciden
        if "customer_email" in matching_fields and "category" in matching_fields:
            confidence += 0.1
        
        return min(1.0, confidence)
    
    def find_duplicate_groups(
        self,
        days_back: int = 30,
        min_similarity: float = 0.7
    ) -> List[DuplicateGroup]:
        """Encontrar grupos de tickets duplicados."""
        start_date = datetime.now() - timedelta(days=days_back)
        
        query = """
            SELECT ticket_id, subject, description, customer_email,
                   category, tags, created_at
            FROM support_tickets
            WHERE created_at >= %s
                AND status != 'closed'
            ORDER BY created_at ASC
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [start_date])
            tickets = cur.fetchall()
        
        groups = []
        processed = set()
        
        for i, ticket1 in enumerate(tickets):
            if ticket1[0] in processed:
                continue
            
            ticket1_dict = {
                "ticket_id": ticket1[0],
                "subject": ticket1[1] or "",
                "description": ticket1[2] or "",
                "customer_email": ticket1[3],
                "category": ticket1[4],
                "tags": ticket1[5] or [],
                "created_at": ticket1[6]
            }
            
            group_tickets = [ticket1[0]]
            processed.add(ticket1[0])
            
            for ticket2 in tickets[i+1:]:
                if ticket2[0] in processed:
                    continue
                
                similarity = self._calculate_similarity(ticket1_dict, ticket2)
                
                if similarity >= min_similarity:
                    group_tickets.append(ticket2[0])
                    processed.add(ticket2[0])
            
            if len(group_tickets) > 1:
                # Crear grupo
                group_id = hashlib.md5(
                    "-".join(sorted(group_tickets)).encode()
                ).hexdigest()
                
                groups.append(DuplicateGroup(
                    group_id=group_id,
                    ticket_ids=group_tickets,
                    primary_ticket_id=group_tickets[0],  # Más antiguo
                    similarity_score=min_similarity,
                    detection_method="clustering",
                    created_at=datetime.now()
                ))
        
        return groups
    
    def merge_duplicates(
        self,
        primary_ticket_id: str,
        duplicate_ticket_ids: List[str],
        merge_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Mergear tickets duplicados."""
        # Verificar que tickets existan
        all_tickets = [primary_ticket_id] + duplicate_ticket_ids
        
        query = """
            SELECT ticket_id FROM support_tickets
            WHERE ticket_id = ANY(%s)
        """
        
        with self.db.cursor() as cur:
            cur.execute(query, [all_tickets])
            existing = {row[0] for row in cur.fetchall()}
        
        missing = set(all_tickets) - existing
        if missing:
            raise ValueError(f"Tickets no encontrados: {missing}")
        
        # Actualizar tickets duplicados
        update_query = """
            UPDATE support_tickets
            SET status = 'closed',
                metadata = jsonb_set(
                    COALESCE(metadata, '{}'::jsonb),
                    '{merged_into}',
                    to_jsonb(%s::text)
                ),
                updated_at = NOW()
            WHERE ticket_id = ANY(%s)
                AND ticket_id != %s
        """
        
        with self.db.cursor() as cur:
            cur.execute(update_query, [
                primary_ticket_id, duplicate_ticket_ids, primary_ticket_id
            ])
            updated_count = cur.rowcount
            
            # Registrar merge
            if merge_notes:
                note_query = """
                    INSERT INTO support_ticket_history (
                        ticket_id, field_name, old_value, new_value, changed_by
                    ) VALUES (%s, 'merged_duplicates', %s, %s, 'system')
                """
                cur.execute(note_query, [
                    primary_ticket_id,
                    f"Duplicados: {', '.join(duplicate_ticket_ids)}",
                    merge_notes
                ])
            
            self.db.commit()
        
        return {
            "success": True,
            "primary_ticket_id": primary_ticket_id,
            "merged_tickets": duplicate_ticket_ids,
            "merged_count": updated_count
        }


