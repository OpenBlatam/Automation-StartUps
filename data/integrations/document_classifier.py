"""
Clasificador de Documentos
==========================

Clasifica automáticamente documentos en categorías:
- Facturas (Invoices)
- Contratos (Contracts)
- Formularios (Forms)
- Otros documentos
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class DocumentType(Enum):
    """Tipos de documentos soportados"""
    INVOICE = "invoice"
    CONTRACT = "contract"
    FORM = "form"
    RECEIPT = "receipt"
    QUOTE = "quote"
    STATEMENT = "statement"
    OTHER = "other"


@dataclass
class ClassificationResult:
    """Resultado de clasificación"""
    document_type: DocumentType
    confidence: float
    keywords_matched: List[str]
    extracted_fields: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class DocumentClassifier:
    """Clasificador de documentos basado en reglas y ML"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # Patrones para identificación de tipos de documentos
        self.patterns = self._initialize_patterns()
        
        # Campos clave para extracción por tipo
        self.extraction_fields = self._initialize_extraction_fields()
    
    def _initialize_patterns(self) -> Dict[DocumentType, List[Dict[str, Any]]]:
        """Inicializa patrones de reconocimiento por tipo de documento"""
        return {
            DocumentType.INVOICE: [
                {
                    "keywords": ["factura", "invoice", "nota de venta", "bill", "cuenta"],
                    "regex": [
                        r"factura\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"invoice\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"total\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                        r"fecha\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                    ],
                    "weight": 1.0
                },
                {
                    "keywords": ["subtotal", "impuestos", "taxes", "iva"],
                    "regex": [
                        r"subtotal\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                        r"impuestos?\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                    ],
                    "weight": 0.8
                }
            ],
            DocumentType.CONTRACT: [
                {
                    "keywords": ["contrato", "contract", "acuerdo", "agreement", "convenio"],
                    "regex": [
                        r"contrato\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"contract\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"fecha\s*de\s*inicio\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                        r"fecha\s*de\s*termino\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                        r"partes?\s*:?\s*([^\n]+)",
                    ],
                    "weight": 1.0
                },
                {
                    "keywords": ["cláusula", "clause", "términos", "terms", "condiciones"],
                    "regex": [
                        r"cláusula\s*(\d+)",
                        r"clause\s*(\d+)",
                    ],
                    "weight": 0.7
                }
            ],
            DocumentType.FORM: [
                {
                    "keywords": ["formulario", "form", "solicitud", "application", "request"],
                    "regex": [
                        r"formulario\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"form\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"nombre\s*:?\s*([^\n]+)",
                        r"email\s*:?\s*([^\n]+)",
                        r"teléfono\s*:?\s*([^\n]+)",
                    ],
                    "weight": 1.0
                },
                {
                    "keywords": ["firma", "signature", "fecha", "date"],
                    "regex": [
                        r"firma\s*:?\s*([^\n]+)",
                        r"signature\s*:?\s*([^\n]+)",
                    ],
                    "weight": 0.6
                }
            ],
            DocumentType.RECEIPT: [
                {
                    "keywords": ["recibo", "receipt", "comprobante", "voucher"],
                    "regex": [
                        r"recibo\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"receipt\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"total\s*pagado\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                    ],
                    "weight": 1.0
                }
            ],
            DocumentType.QUOTE: [
                {
                    "keywords": ["cotización", "quote", "presupuesto", "estimate"],
                    "regex": [
                        r"cotizaci[oó]n\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"quote\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"válido\s*hasta\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                    ],
                    "weight": 1.0
                }
            ],
            DocumentType.STATEMENT: [
                {
                    "keywords": ["estado de cuenta", "statement", "resumen", "summary"],
                    "regex": [
                        r"estado\s*de\s*cuenta\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"statement\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                        r"saldo\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                    ],
                    "weight": 1.0
                }
            ]
        }
    
    def _initialize_extraction_fields(self) -> Dict[DocumentType, List[str]]:
        """Inicializa campos a extraer por tipo de documento"""
        return {
            DocumentType.INVOICE: [
                "invoice_number", "date", "total", "subtotal", "taxes",
                "customer_name", "customer_email", "customer_address",
                "vendor_name", "vendor_tax_id", "items", "due_date"
            ],
            DocumentType.CONTRACT: [
                "contract_number", "start_date", "end_date", "parties",
                "amount", "terms", "signatures", "clauses"
            ],
            DocumentType.FORM: [
                "form_type", "applicant_name", "email", "phone",
                "date", "signature", "submitted_date"
            ],
            DocumentType.RECEIPT: [
                "receipt_number", "date", "amount", "payment_method",
                "vendor", "items"
            ],
            DocumentType.QUOTE: [
                "quote_number", "date", "valid_until", "total",
                "customer", "items", "terms"
            ],
            DocumentType.STATEMENT: [
                "statement_number", "period", "balance", "transactions",
                "account_number"
            ]
        }
    
    def classify(self, text: str, filename: Optional[str] = None) -> ClassificationResult:
        """
        Clasifica un documento basado en su contenido
        
        Args:
            text: Texto extraído del documento (OCR)
            filename: Nombre del archivo (opcional, para ayudar en clasificación)
        
        Returns:
            ClassificationResult con tipo y campos extraídos
        """
        text_lower = text.lower()
        
        # Scores por tipo de documento
        scores: Dict[DocumentType, float] = {doc_type: 0.0 for doc_type in DocumentType}
        
        # Keywords matched
        keywords_matched: Dict[DocumentType, List[str]] = {
            doc_type: [] for doc_type in DocumentType
        }
        
        # Analizar cada tipo de documento
        for doc_type, patterns in self.patterns.items():
            for pattern_group in patterns:
                # Verificar keywords
                keywords = pattern_group.get("keywords", [])
                weight = pattern_group.get("weight", 1.0)
                
                for keyword in keywords:
                    if keyword.lower() in text_lower:
                        scores[doc_type] += weight * 0.5
                        keywords_matched[doc_type].append(keyword)
                
                # Verificar regex
                regex_patterns = pattern_group.get("regex", [])
                for regex in regex_patterns:
                    matches = re.findall(regex, text_lower, re.IGNORECASE | re.MULTILINE)
                    if matches:
                        scores[doc_type] += weight * 0.3 * len(matches)
        
        # Análisis de nombre de archivo
        if filename:
            filename_lower = filename.lower()
            for doc_type in DocumentType:
                type_keywords = {
                    DocumentType.INVOICE: ["factura", "invoice", "bill"],
                    DocumentType.CONTRACT: ["contrato", "contract", "agreement"],
                    DocumentType.FORM: ["formulario", "form", "solicitud"],
                    DocumentType.RECEIPT: ["recibo", "receipt"],
                    DocumentType.QUOTE: ["cotizacion", "quote", "presupuesto"],
                    DocumentType.STATEMENT: ["estado", "statement"]
                }
                for keyword in type_keywords.get(doc_type, []):
                    if keyword in filename_lower:
                        scores[doc_type] += 0.5
        
        # Determinar tipo con mayor score
        if not any(scores.values()):
            # Sin coincidencias, clasificar como OTHER
            best_type = DocumentType.OTHER
            confidence = 0.1
        else:
            best_type = max(scores.items(), key=lambda x: x[1])[0]
            max_score = scores[best_type]
            total_score = sum(scores.values())
            confidence = min(max_score / max(total_score, 1), 1.0)
        
        # Extraer campos específicos del tipo detectado
        extracted_fields = self._extract_fields(text, best_type)
        
        return ClassificationResult(
            document_type=best_type,
            confidence=confidence,
            keywords_matched=keywords_matched[best_type],
            extracted_fields=extracted_fields,
            metadata={
                "all_scores": {k.value: v for k, v in scores.items()},
                "filename": filename,
                "classification_date": datetime.now().isoformat()
            }
        )
    
    def _extract_fields(self, text: str, doc_type: DocumentType) -> Dict[str, Any]:
        """Extrae campos específicos según el tipo de documento"""
        fields = {}
        text_lower = text.lower()
        
        if doc_type == DocumentType.INVOICE:
            # Número de factura
            invoice_num_match = re.search(
                r"factura\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                text_lower, re.IGNORECASE
            ) or re.search(
                r"invoice\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                text_lower, re.IGNORECASE
            )
            if invoice_num_match:
                fields["invoice_number"] = invoice_num_match.group(1)
            
            # Fecha
            date_match = re.search(
                r"fecha\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                text_lower, re.IGNORECASE
            ) or re.search(
                r"date\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                text_lower, re.IGNORECASE
            )
            if date_match:
                fields["date"] = date_match.group(1)
            
            # Total
            total_match = re.search(
                r"total\s*:?\s*\$?\s*([\d,]+\.?\d*)",
                text_lower, re.IGNORECASE
            )
            if total_match:
                fields["total"] = total_match.group(1).replace(",", "")
            
            # Cliente
            customer_match = re.search(
                r"cliente\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            ) or re.search(
                r"customer\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            )
            if customer_match:
                fields["customer_name"] = customer_match.group(1).strip()
        
        elif doc_type == DocumentType.CONTRACT:
            # Número de contrato
            contract_num_match = re.search(
                r"contrato\s*(?:n[o°]?|#)?\s*:?\s*(\d+)",
                text_lower, re.IGNORECASE
            )
            if contract_num_match:
                fields["contract_number"] = contract_num_match.group(1)
            
            # Fechas
            start_date_match = re.search(
                r"fecha\s*de\s*inicio\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                text_lower, re.IGNORECASE
            )
            if start_date_match:
                fields["start_date"] = start_date_match.group(1)
            
            end_date_match = re.search(
                r"fecha\s*de\s*termino\s*:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",
                text_lower, re.IGNORECASE
            )
            if end_date_match:
                fields["end_date"] = end_date_match.group(1)
            
            # Partes
            parties_match = re.search(
                r"partes?\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            )
            if parties_match:
                fields["parties"] = parties_match.group(1).strip()
        
        elif doc_type == DocumentType.FORM:
            # Nombre
            name_match = re.search(
                r"nombre\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            ) or re.search(
                r"name\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            )
            if name_match:
                fields["applicant_name"] = name_match.group(1).strip()
            
            # Email
            email_match = re.search(
                r"email\s*:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
                text_lower, re.IGNORECASE
            )
            if email_match:
                fields["email"] = email_match.group(1).strip()
            
            # Teléfono
            phone_match = re.search(
                r"tel[ée]fono\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            ) or re.search(
                r"phone\s*:?\s*([^\n]+)",
                text_lower, re.IGNORECASE
            )
            if phone_match:
                fields["phone"] = phone_match.group(1).strip()
        
        return fields

