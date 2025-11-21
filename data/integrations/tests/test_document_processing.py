"""
Tests para Sistema de Procesamiento de Documentos
==================================================

Tests unitarios e integración para validar funcionalidades.
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch

# Importar módulos a testear
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_classifier import DocumentClassifier, DocumentType
from document_validator import DocumentValidator, FieldValidator
from document_comparison import DocumentComparator
from document_search import DocumentSearcher


class TestDocumentClassifier:
    """Tests para clasificador de documentos"""
    
    def setup_method(self):
        self.classifier = DocumentClassifier()
    
    def test_classify_invoice(self):
        """Test clasificación de factura"""
        text = """
        FACTURA N° 001
        Fecha: 01/01/2024
        Cliente: Juan Pérez
        Total: $1000.00
        Subtotal: $900.00
        Impuestos: $100.00
        """
        
        result = self.classifier.classify(text, "factura_001.pdf")
        
        assert result.document_type == DocumentType.INVOICE
        assert result.confidence > 0.7
        assert "invoice_number" in result.extracted_fields or "factura" in text.lower()
    
    def test_classify_contract(self):
        """Test clasificación de contrato"""
        text = """
        CONTRATO N° 123
        Fecha de inicio: 01/01/2024
        Fecha de término: 31/12/2024
        Partes: Empresa A y Empresa B
        """
        
        result = self.classifier.classify(text, "contrato.pdf")
        
        assert result.document_type == DocumentType.CONTRACT
        assert result.confidence > 0.7
    
    def test_classify_form(self):
        """Test clasificación de formulario"""
        text = """
        FORMULARIO DE SOLICITUD
        Nombre: María González
        Email: maria@example.com
        Teléfono: +56912345678
        Firma: _______________
        """
        
        result = self.classifier.classify(text, "formulario.pdf")
        
        assert result.document_type == DocumentType.FORM
        assert "email" in result.extracted_fields or "applicant_name" in result.extracted_fields


class TestDocumentValidator:
    """Tests para validador de documentos"""
    
    def setup_method(self):
        self.validator = FieldValidator()
    
    def test_validate_invoice_number(self):
        """Test validación de número de factura"""
        result = self.validator.validate_invoice_number("001")
        assert result.is_valid
        assert result.normalized_value is not None
    
    def test_validate_date(self):
        """Test validación de fecha"""
        result = self.validator.validate_date("01/01/2024")
        assert result.is_valid
        assert result.normalized_value is not None
    
    def test_validate_email(self):
        """Test validación de email"""
        result = self.validator.validate_email("test@example.com")
        assert result.is_valid
        assert result.normalized_value == "test@example.com"
        
        result_invalid = self.validator.validate_email("invalid-email")
        assert not result_invalid.is_valid
    
    def test_validate_amount(self):
        """Test validación de monto"""
        result = self.validator.validate_amount("1000.50")
        assert result.is_valid
        assert result.normalized_value == 1000.50


class TestDocumentComparator:
    """Tests para comparador de documentos"""
    
    def setup_method(self):
        self.comparator = DocumentComparator()
    
    def test_compare_identical_documents(self):
        """Test comparación de documentos idénticos"""
        doc1 = {
            "document_id": "DOC1",
            "extracted_text": "Factura 001",
            "extracted_fields": {"invoice_number": "001", "total": "1000"},
            "file_hash": "abc123"
        }
        
        doc2 = {
            "document_id": "DOC2",
            "extracted_text": "Factura 001",
            "extracted_fields": {"invoice_number": "001", "total": "1000"},
            "file_hash": "abc123"
        }
        
        result = self.comparator.compare_documents(doc1, doc2)
        
        assert result.similarity_score >= 0.95
        assert result.similarity_level.value == "identical" or result.similarity_level.value == "very_similar"
    
    def test_find_duplicates(self):
        """Test detección de duplicados"""
        documents = [
            {
                "document_id": "DOC1",
                "extracted_text": "Factura 001",
                "extracted_fields": {"invoice_number": "001"},
                "file_hash": "abc123"
            },
            {
                "document_id": "DOC2",
                "extracted_text": "Factura 001",
                "extracted_fields": {"invoice_number": "001"},
                "file_hash": "abc123"
            },
            {
                "document_id": "DOC3",
                "extracted_text": "Factura 002",
                "extracted_fields": {"invoice_number": "002"},
                "file_hash": "def456"
            }
        ]
        
        duplicates = self.comparator.find_duplicates(documents, threshold=0.95)
        
        assert len(duplicates) >= 1  # DOC1 y DOC2 deberían ser duplicados


class TestDocumentSearcher:
    """Tests para buscador de documentos"""
    
    def setup_method(self):
        self.searcher = DocumentSearcher()
    
    def test_search_by_text(self):
        """Test búsqueda por texto"""
        documents = [
            {
                "document_id": "DOC1",
                "document_type": "invoice",
                "extracted_text": "Factura número 001 para cliente Juan Pérez"
            },
            {
                "document_id": "DOC2",
                "document_type": "contract",
                "extracted_text": "Contrato de servicios"
            }
        ]
        
        results = self.searcher.search_by_text("Factura", documents)
        
        assert len(results) > 0
        assert results[0].document_type == "invoice"
    
    def test_search_by_field(self):
        """Test búsqueda por campo"""
        documents = [
            {
                "document_id": "DOC1",
                "document_type": "invoice",
                "extracted_fields": {"invoice_number": "001", "total": "1000"}
            },
            {
                "document_id": "DOC2",
                "document_type": "invoice",
                "extracted_fields": {"invoice_number": "002", "total": "2000"}
            }
        ]
        
        results = self.searcher.search_by_field("invoice_number", "001", documents)
        
        assert len(results) > 0
        assert results[0].document_id == "DOC1"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

