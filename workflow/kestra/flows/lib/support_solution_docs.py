"""
Sistema de Documentación Automática de Soluciones.

Genera documentación automática de soluciones a partir de tickets resueltos.
"""
import logging
import uuid
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class SolutionType(Enum):
    """Tipos de solución."""
    TROUBLESHOOTING = "troubleshooting"
    HOW_TO = "how_to"
    FAQ = "faq"
    TROUBLESHOOTING_GUIDE = "troubleshooting_guide"
    BEST_PRACTICE = "best_practice"


@dataclass
class SolutionDocument:
    """Documento de solución."""
    document_id: str
    title: str
    description: str
    solution_type: SolutionType
    content: str  # Markdown o HTML
    
    # Metadata del ticket origen
    source_ticket_id: str
    source_ticket_subject: str
    
    # Categorización
    category: str
    tags: List[str]
    keywords: List[str]
    
    # Estadísticas
    views_count: int = 0
    helpful_count: int = 0
    not_helpful_count: int = 0
    
    # Estado
    is_published: bool = False
    is_verified: bool = False
    
    # Metadata
    created_by: Optional[str] = None
    created_at: datetime = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


class SolutionDocumentGenerator:
    """Generador de documentos de solución."""
    
    def __init__(self, db_connection=None):
        """
        Inicializa generador.
        
        Args:
            db_connection: Conexión a BD (opcional)
        """
        self.db = db_connection
        self.documents: Dict[str, SolutionDocument] = {}
    
    def generate_from_ticket(
        self,
        ticket_data: Dict[str, Any],
        solution_type: SolutionType = SolutionType.HOW_TO
    ) -> SolutionDocument:
        """
        Genera documento de solución desde ticket resuelto.
        
        Args:
            ticket_data: Datos del ticket resuelto
            solution_type: Tipo de solución
            
        Returns:
            Documento generado
        """
        # Extraer información
        ticket_id = ticket_data.get("ticket_id")
        subject = ticket_data.get("subject", "")
        description = ticket_data.get("description", "")
        resolution_notes = ticket_data.get("resolution_notes", "")
        category = ticket_data.get("category", "general")
        tags = ticket_data.get("tags", [])
        
        # Generar título
        title = self._generate_title(subject, solution_type)
        
        # Generar descripción
        doc_description = self._generate_description(description, resolution_notes)
        
        # Generar contenido
        content = self._generate_content(
            subject,
            description,
            resolution_notes,
            solution_type
        )
        
        # Extraer keywords
        keywords = self._extract_keywords(description, resolution_notes)
        
        # Crear documento
        document = SolutionDocument(
            document_id=f"sol-{uuid.uuid4().hex[:12]}",
            title=title,
            description=doc_description,
            solution_type=solution_type,
            content=content,
            source_ticket_id=ticket_id,
            source_ticket_subject=subject,
            category=category,
            tags=tags,
            keywords=keywords,
            created_by=ticket_data.get("resolved_by", "system")
        )
        
        self.documents[document.document_id] = document
        
        logger.info(f"Generated solution document {document.document_id} from ticket {ticket_id}")
        return document
    
    def _generate_title(self, subject: str, solution_type: SolutionType) -> str:
        """Genera título del documento."""
        if solution_type == SolutionType.HOW_TO:
            if "how to" not in subject.lower() and "cómo" not in subject.lower():
                return f"Cómo: {subject}"
            return subject
        elif solution_type == SolutionType.TROUBLESHOOTING:
            if "troubleshoot" not in subject.lower() and "solucionar" not in subject.lower():
                return f"Solucionar: {subject}"
            return subject
        else:
            return subject
    
    def _generate_description(
        self,
        description: str,
        resolution_notes: str
    ) -> str:
        """Genera descripción del documento."""
        # Usar primeros 200 caracteres
        text = f"{description} {resolution_notes}".strip()
        if len(text) > 200:
            return text[:200] + "..."
        return text
    
    def _generate_content(
        self,
        subject: str,
        description: str,
        resolution_notes: str,
        solution_type: SolutionType
    ) -> str:
        """Genera contenido del documento."""
        if solution_type == SolutionType.HOW_TO:
            return self._generate_how_to_content(subject, description, resolution_notes)
        elif solution_type == SolutionType.TROUBLESHOOTING:
            return self._generate_troubleshooting_content(subject, description, resolution_notes)
        else:
            return self._generate_generic_content(subject, description, resolution_notes)
    
    def _generate_how_to_content(
        self,
        subject: str,
        description: str,
        resolution_notes: str
    ) -> str:
        """Genera contenido tipo How-To."""
        content = f"# {subject}\n\n"
        content += "## Problema\n\n"
        content += f"{description}\n\n"
        content += "## Solución\n\n"
        content += f"{resolution_notes}\n\n"
        content += "## Pasos Detallados\n\n"
        content += "1. [Pasos extraídos de la solución]\n"
        return content
    
    def _generate_troubleshooting_content(
        self,
        subject: str,
        description: str,
        resolution_notes: str
    ) -> str:
        """Genera contenido tipo Troubleshooting."""
        content = f"# Solución: {subject}\n\n"
        content += "## Síntomas\n\n"
        content += f"{description}\n\n"
        content += "## Causa\n\n"
        content += "[Causa identificada]\n\n"
        content += "## Solución\n\n"
        content += f"{resolution_notes}\n\n"
        return content
    
    def _generate_generic_content(
        self,
        subject: str,
        description: str,
        resolution_notes: str
    ) -> str:
        """Genera contenido genérico."""
        content = f"# {subject}\n\n"
        content += f"## Descripción\n\n{description}\n\n"
        content += f"## Solución\n\n{resolution_notes}\n\n"
        return content
    
    def _extract_keywords(self, description: str, resolution_notes: str) -> List[str]:
        """Extrae keywords del contenido."""
        text = f"{description} {resolution_notes}".lower()
        
        # Palabras comunes a ignorar
        stop_words = {"el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le", "da"}
        
        # Extraer palabras importantes (más de 4 caracteres)
        words = [w for w in text.split() if len(w) > 4 and w not in stop_words]
        
        # Contar frecuencia
        from collections import Counter
        counter = Counter(words)
        
        # Top 10 keywords
        return [word for word, _ in counter.most_common(10)]
    
    def publish_document(self, document_id: str) -> bool:
        """Publica un documento."""
        if document_id not in self.documents:
            return False
        
        document = self.documents[document_id]
        document.is_published = True
        document.updated_at = datetime.now()
        
        logger.info(f"Published solution document {document_id}")
        return True
    
    def verify_document(self, document_id: str, verified_by: str) -> bool:
        """Verifica un documento."""
        if document_id not in self.documents:
            return False
        
        document = self.documents[document_id]
        document.is_verified = True
        document.updated_at = datetime.now()
        
        logger.info(f"Verified solution document {document_id} by {verified_by}")
        return True
    
    def search_documents(
        self,
        query: str,
        category: Optional[str] = None,
        solution_type: Optional[SolutionType] = None
    ) -> List[SolutionDocument]:
        """Busca documentos."""
        results = []
        query_lower = query.lower()
        
        for doc in self.documents.values():
            if not doc.is_published:
                continue
            
            if category and doc.category != category:
                continue
            
            if solution_type and doc.solution_type != solution_type:
                continue
            
            # Buscar en título, descripción, keywords
            if (query_lower in doc.title.lower() or
                query_lower in doc.description.lower() or
                any(query_lower in kw.lower() for kw in doc.keywords)):
                results.append(doc)
        
        return results
    
    def get_document(self, document_id: str) -> Optional[SolutionDocument]:
        """Obtiene un documento."""
        return self.documents.get(document_id)
    
    def record_view(self, document_id: str):
        """Registra visualización."""
        if document_id in self.documents:
            self.documents[document_id].views_count += 1
    
    def record_feedback(self, document_id: str, helpful: bool):
        """Registra feedback de utilidad."""
        if document_id in self.documents:
            doc = self.documents[document_id]
            if helpful:
                doc.helpful_count += 1
            else:
                doc.not_helpful_count += 1

