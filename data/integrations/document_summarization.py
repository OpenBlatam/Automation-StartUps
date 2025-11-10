"""
Generación de Resúmenes Automáticos
====================================

Genera resúmenes automáticos de documentos procesados.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentSummary:
    """Resumen de documento"""
    document_id: str
    summary_text: str
    key_points: List[str]
    word_count: int
    summary_length: int
    compression_ratio: float
    generated_at: str


class DocumentSummarizer:
    """Generador de resúmenes"""
    
    def __init__(self, method: str = "extractive"):
        self.method = method  # extractive o abstractive
        self.logger = logging.getLogger(__name__)
    
    def generate_summary(
        self,
        text: str,
        max_sentences: int = 5,
        max_words: Optional[int] = None
    ) -> DocumentSummary:
        """Genera resumen del texto"""
        if not text or not text.strip():
            return DocumentSummary(
                document_id="",
                summary_text="",
                key_points=[],
                word_count=0,
                summary_length=0,
                compression_ratio=0.0,
                generated_at=datetime.now().isoformat()
            )
        
        if self.method == "extractive":
            return self._extractive_summary(text, max_sentences, max_words)
        else:
            return self._abstractive_summary(text, max_sentences, max_words)
    
    def _extractive_summary(
        self,
        text: str,
        max_sentences: int,
        max_words: Optional[int]
    ) -> DocumentSummary:
        """Resumen extractivo (selecciona oraciones importantes)"""
        import re
        from collections import Counter
        
        # Dividir en oraciones
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return DocumentSummary(
                document_id="",
                summary_text="",
                key_points=[],
                word_count=0,
                summary_length=0,
                compression_ratio=0.0,
                generated_at=datetime.now().isoformat()
            )
        
        # Calcular importancia de cada oración
        word_freq = Counter()
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            word_freq.update(words)
        
        # Score de oraciones
        sentence_scores = {}
        for sentence in sentences:
            words = re.findall(r'\b\w+\b', sentence.lower())
            score = sum(word_freq[word] for word in words)
            sentence_scores[sentence] = score / len(words) if words else 0
        
        # Seleccionar mejores oraciones
        sorted_sentences = sorted(
            sentence_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        selected = sorted_sentences[:max_sentences]
        summary_text = ". ".join([s[0] for s in selected]) + "."
        
        # Extraer puntos clave (palabras más frecuentes)
        key_words = [word for word, _ in word_freq.most_common(10)]
        
        # Limitar palabras si se especifica
        if max_words:
            words = summary_text.split()
            if len(words) > max_words:
                summary_text = " ".join(words[:max_words]) + "..."
        
        word_count = len(text.split())
        summary_length = len(summary_text.split())
        compression_ratio = 1 - (summary_length / word_count) if word_count > 0 else 0
        
        return DocumentSummary(
            document_id="",
            summary_text=summary_text,
            key_points=key_words[:5],
            word_count=word_count,
            summary_length=summary_length,
            compression_ratio=compression_ratio,
            generated_at=datetime.now().isoformat()
        )
    
    def _abstractive_summary(
        self,
        text: str,
        max_sentences: int,
        max_words: Optional[int]
    ) -> DocumentSummary:
        """Resumen abstractivo (genera nuevo texto)"""
        try:
            from transformers import pipeline
        except ImportError:
            self.logger.warning(
                "transformers no disponible para resumen abstractivo. "
                "Usando extractivo como fallback."
            )
            return self._extractive_summary(text, max_sentences, max_words)
        
        try:
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            
            # Limitar longitud de entrada
            max_length = min(len(text), 1024)
            summary_text = summarizer(
                text[:max_length],
                max_length=max_words or 100,
                min_length=30,
                do_sample=False
            )[0]['summary_text']
            
            word_count = len(text.split())
            summary_length = len(summary_text.split())
            compression_ratio = 1 - (summary_length / word_count) if word_count > 0 else 0
            
            return DocumentSummary(
                document_id="",
                summary_text=summary_text,
                key_points=[],
                word_count=word_count,
                summary_length=summary_length,
                compression_ratio=compression_ratio,
                generated_at=datetime.now().isoformat()
            )
        except Exception as e:
            self.logger.error(f"Error en resumen abstractivo: {e}")
            return self._extractive_summary(text, max_sentences, max_words)
    
    def generate_executive_summary(
        self,
        document: Dict[str, Any]
    ) -> str:
        """Genera resumen ejecutivo de un documento"""
        text = document.get("extracted_text", "")
        doc_type = document.get("document_type", "")
        extracted_fields = document.get("extracted_fields", {})
        
        summary_parts = []
        
        # Encabezado
        summary_parts.append(f"Resumen Ejecutivo - {doc_type.upper()}")
        summary_parts.append("=" * 50)
        
        # Información clave según tipo
        if doc_type == "invoice":
            summary_parts.append(f"Número: {extracted_fields.get('invoice_number', 'N/A')}")
            summary_parts.append(f"Fecha: {extracted_fields.get('date', 'N/A')}")
            summary_parts.append(f"Total: {extracted_fields.get('total', 'N/A')}")
            summary_parts.append(f"Cliente: {extracted_fields.get('customer_name', 'N/A')}")
        
        elif doc_type == "contract":
            summary_parts.append(f"Número: {extracted_fields.get('contract_number', 'N/A')}")
            summary_parts.append(f"Inicio: {extracted_fields.get('start_date', 'N/A')}")
            summary_parts.append(f"Término: {extracted_fields.get('end_date', 'N/A')}")
            summary_parts.append(f"Partes: {extracted_fields.get('parties', 'N/A')}")
        
        # Resumen de texto
        text_summary = self.generate_summary(text, max_sentences=3)
        summary_parts.append("\nResumen:")
        summary_parts.append(text_summary.summary_text)
        
        return "\n".join(summary_parts)

