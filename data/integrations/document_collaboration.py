"""
Sistema de Colaboración y Revisiones
======================================

Permite que múltiples usuarios revisen y comenten documentos.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class ReviewStatus(Enum):
    """Estado de revisión"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    CHANGES_REQUESTED = "changes_requested"


@dataclass
class ReviewComment:
    """Comentario en una revisión"""
    comment_id: str
    document_id: str
    user_id: str
    user_email: str
    text: str
    page_number: Optional[int] = None
    coordinates: Optional[Dict[str, float]] = None
    created_at: str = None
    resolved: bool = False
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


@dataclass
class DocumentReview:
    """Revisión de documento"""
    review_id: str
    document_id: str
    reviewer_id: str
    reviewer_email: str
    status: ReviewStatus
    comments: List[ReviewComment]
    created_at: str
    updated_at: str
    completed_at: Optional[str] = None


class CollaborationManager:
    """Gestor de colaboración y revisiones"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
    
    def create_review(
        self,
        document_id: str,
        reviewer_id: str,
        reviewer_email: str
    ) -> DocumentReview:
        """Crea una nueva revisión"""
        review_id = f"REV-{datetime.now().strftime('%Y%m%d%H%M%S')}-{document_id[:8]}"
        
        review = DocumentReview(
            review_id=review_id,
            document_id=document_id,
            reviewer_id=reviewer_id,
            reviewer_email=reviewer_email,
            status=ReviewStatus.PENDING,
            comments=[],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        if self.db:
            self._save_review_to_db(review)
        
        return review
    
    def add_comment(
        self,
        review_id: str,
        document_id: str,
        user_id: str,
        user_email: str,
        text: str,
        page_number: Optional[int] = None,
        coordinates: Optional[Dict[str, float]] = None
    ) -> ReviewComment:
        """Agrega comentario a una revisión"""
        comment_id = f"CMT-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        comment = ReviewComment(
            comment_id=comment_id,
            document_id=document_id,
            user_id=user_id,
            user_email=user_email,
            text=text,
            page_number=page_number,
            coordinates=coordinates,
            created_at=datetime.now().isoformat()
        )
        
        if self.db:
            self._save_comment_to_db(review_id, comment)
        
        return comment
    
    def update_review_status(
        self,
        review_id: str,
        status: ReviewStatus,
        reviewer_id: str
    ) -> bool:
        """Actualiza estado de revisión"""
        if self.db:
            try:
                cursor = self.db.cursor()
                cursor.execute("""
                    UPDATE document_reviews
                    SET status = %s,
                        updated_at = CURRENT_TIMESTAMP,
                        completed_at = CASE WHEN %s IN ('approved', 'rejected') 
                                           THEN CURRENT_TIMESTAMP 
                                           ELSE completed_at END
                    WHERE review_id = %s AND reviewer_id = %s
                """, (status.value, status.value, review_id, reviewer_id))
                self.db.commit()
                return True
            except Exception as e:
                self.logger.error(f"Error actualizando revisión: {e}")
                self.db.rollback()
                return False
        return False
    
    def get_review(self, review_id: str) -> Optional[DocumentReview]:
        """Obtiene una revisión"""
        if not self.db:
            return None
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT review_id, document_id, reviewer_id, reviewer_email,
                       status, created_at, updated_at, completed_at
                FROM document_reviews
                WHERE review_id = %s
            """, (review_id,))
            
            row = cursor.fetchone()
            if not row:
                return None
            
            # Obtener comentarios
            cursor.execute("""
                SELECT comment_id, user_id, user_email, text, page_number,
                       coordinates, created_at, resolved, resolved_at, resolved_by
                FROM review_comments
                WHERE review_id = %s
                ORDER BY created_at ASC
            """, (review_id,))
            
            comments = []
            for comment_row in cursor.fetchall():
                comments.append(ReviewComment(
                    comment_id=comment_row[0],
                    document_id=row[1],
                    user_id=comment_row[1],
                    user_email=comment_row[2],
                    text=comment_row[3],
                    page_number=comment_row[4],
                    coordinates=json.loads(comment_row[5]) if comment_row[5] else None,
                    created_at=comment_row[6],
                    resolved=comment_row[7],
                    resolved_at=comment_row[8],
                    resolved_by=comment_row[9]
                ))
            
            return DocumentReview(
                review_id=row[0],
                document_id=row[1],
                reviewer_id=row[2],
                reviewer_email=row[3],
                status=ReviewStatus(row[4]),
                comments=comments,
                created_at=row[5],
                updated_at=row[6],
                completed_at=row[7]
            )
        except Exception as e:
            self.logger.error(f"Error obteniendo revisión: {e}")
            return None
    
    def _save_review_to_db(self, review: DocumentReview):
        """Guarda revisión en BD"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO document_reviews
                (review_id, document_id, reviewer_id, reviewer_email, status,
                 created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                review.review_id,
                review.document_id,
                review.reviewer_id,
                review.reviewer_email,
                review.status.value,
                review.created_at,
                review.updated_at
            ))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error guardando revisión: {e}")
            self.db.rollback()
    
    def _save_comment_to_db(self, review_id: str, comment: ReviewComment):
        """Guarda comentario en BD"""
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                INSERT INTO review_comments
                (comment_id, review_id, document_id, user_id, user_email,
                 text, page_number, coordinates, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                comment.comment_id,
                review_id,
                comment.document_id,
                comment.user_id,
                comment.user_email,
                comment.text,
                comment.page_number,
                json.dumps(comment.coordinates) if comment.coordinates else None,
                comment.created_at
            ))
            self.db.commit()
        except Exception as e:
            self.logger.error(f"Error guardando comentario: {e}")
            self.db.rollback()

