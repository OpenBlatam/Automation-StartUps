"""
Validador de Campos Extraídos de Documentos
===========================================

Valida y enriquece campos extraídos de documentos procesados.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Niveles de validación"""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


@dataclass
class ValidationResult:
    """Resultado de validación de un campo"""
    field_name: str
    field_value: Any
    is_valid: bool
    validation_errors: List[str]
    normalized_value: Optional[Any] = None
    confidence: float = 1.0
    suggestions: List[str] = None


@dataclass
class DocumentValidationReport:
    """Reporte completo de validación de un documento"""
    document_id: str
    document_type: str
    overall_valid: bool
    fields_validated: Dict[str, ValidationResult]
    validation_score: float  # 0-1
    missing_required_fields: List[str]
    invalid_fields: List[str]
    warnings: List[str]
    validated_at: str


class FieldValidator:
    """Validador de campos individuales"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.validation_level = validation_level
        self.logger = logging.getLogger(__name__)
    
    def validate_invoice_number(self, value: str) -> ValidationResult:
        """Valida número de factura"""
        errors = []
        normalized = None
        
        if not value or not value.strip():
            errors.append("Número de factura vacío")
            return ValidationResult(
                field_name="invoice_number",
                field_value=value,
                is_valid=False,
                validation_errors=errors
            )
        
        # Normalizar: remover espacios, guiones, etc.
        normalized = re.sub(r'[^\w]', '', value.strip().upper())
        
        # Validar formato
        if len(normalized) < 3:
            errors.append("Número de factura muy corto")
        
        if not re.match(r'^[A-Z0-9]+$', normalized):
            errors.append("Formato inválido (debe contener solo letras y números)")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            field_name="invoice_number",
            field_value=value,
            is_valid=is_valid,
            validation_errors=errors,
            normalized_value=normalized,
            confidence=0.9 if is_valid else 0.5
        )
    
    def validate_date(self, value: str, formats: Optional[List[str]] = None) -> ValidationResult:
        """Valida fecha"""
        errors = []
        normalized = None
        
        if not value or not value.strip():
            errors.append("Fecha vacía")
            return ValidationResult(
                field_name="date",
                field_value=value,
                is_valid=False,
                validation_errors=errors
            )
        
        # Formatos comunes
        if formats is None:
            formats = [
                r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # DD/MM/YYYY o DD-MM-YYYY
                r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',   # YYYY/MM/DD
                r'\d{1,2}\s+\w+\s+\d{4}',          # DD Month YYYY
            ]
        
        matched = False
        for fmt in formats:
            if re.match(fmt, value.strip()):
                matched = True
                break
        
        if not matched:
            errors.append("Formato de fecha no reconocido")
        
        # Intentar parsear
        try:
            # Normalizar a formato estándar
            date_str = value.strip()
            # Simplificar: intentar diferentes formatos
            for fmt in ['%d/%m/%Y', '%d-%m-%Y', '%Y-%m-%d', '%Y/%m/%d']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    normalized = dt.strftime('%Y-%m-%d')
                    break
                except ValueError:
                    continue
        except Exception as e:
            errors.append(f"Error parseando fecha: {e}")
        
        is_valid = len(errors) == 0 and normalized is not None
        
        return ValidationResult(
            field_name="date",
            field_value=value,
            is_valid=is_valid,
            validation_errors=errors,
            normalized_value=normalized,
            confidence=0.9 if is_valid else 0.6
        )
    
    def validate_amount(self, value: str) -> ValidationResult:
        """Valida monto/número"""
        errors = []
        normalized = None
        
        if not value or not value.strip():
            errors.append("Monto vacío")
            return ValidationResult(
                field_name="amount",
                field_value=value,
                is_valid=False,
                validation_errors=errors
            )
        
        # Remover símbolos de moneda y espacios
        cleaned = re.sub(r'[^\d,.-]', '', value.strip())
        cleaned = cleaned.replace(',', '')  # Remover separadores de miles
        
        try:
            normalized = float(cleaned)
            if normalized < 0:
                errors.append("Monto negativo")
            elif normalized == 0:
                errors.append("Monto cero")
        except ValueError:
            errors.append("Monto no es un número válido")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            field_name="amount",
            field_value=value,
            is_valid=is_valid,
            validation_errors=errors,
            normalized_value=normalized,
            confidence=0.95 if is_valid else 0.5
        )
    
    def validate_email(self, value: str) -> ValidationResult:
        """Valida email"""
        errors = []
        normalized = None
        
        if not value or not value.strip():
            errors.append("Email vacío")
            return ValidationResult(
                field_name="email",
                field_value=value,
                is_valid=False,
                validation_errors=errors
            )
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        normalized = value.strip().lower()
        
        if not re.match(email_pattern, normalized):
            errors.append("Formato de email inválido")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            field_name="email",
            field_value=value,
            is_valid=is_valid,
            validation_errors=errors,
            normalized_value=normalized,
            confidence=0.95 if is_valid else 0.3
        )
    
    def validate_phone(self, value: str) -> ValidationResult:
        """Valida teléfono"""
        errors = []
        normalized = None
        
        if not value or not value.strip():
            errors.append("Teléfono vacío")
            return ValidationResult(
                field_name="phone",
                field_value=value,
                is_valid=False,
                validation_errors=errors
            )
        
        # Remover caracteres no numéricos
        cleaned = re.sub(r'[^\d+]', '', value.strip())
        normalized = cleaned
        
        # Validar longitud mínima
        if len(normalized) < 7:
            errors.append("Teléfono muy corto")
        elif len(normalized) > 15:
            errors.append("Teléfono muy largo")
        
        # Validar formato básico
        if not re.match(r'^\+?\d{7,15}$', normalized):
            errors.append("Formato de teléfono inválido")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            field_name="phone",
            field_value=value,
            is_valid=is_valid,
            validation_errors=errors,
            normalized_value=normalized,
            confidence=0.9 if is_valid else 0.6
        )
    
    def validate_tax_id(self, value: str) -> ValidationResult:
        """Valida número de identificación fiscal (RUT, NIT, etc.)"""
        errors = []
        normalized = None
        
        if not value or not value.strip():
            errors.append("Identificación fiscal vacía")
            return ValidationResult(
                field_name="tax_id",
                field_value=value,
                is_valid=False,
                validation_errors=errors
            )
        
        # Remover guiones y espacios
        normalized = re.sub(r'[-\s]', '', value.strip().upper())
        
        # Validar longitud (varía por país, usar validación genérica)
        if len(normalized) < 8:
            errors.append("Identificación fiscal muy corta")
        elif len(normalized) > 20:
            errors.append("Identificación fiscal muy larga")
        
        # Validar que contiene números y posiblemente letras
        if not re.match(r'^[A-Z0-9]+$', normalized):
            errors.append("Formato inválido")
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            field_name="tax_id",
            field_value=value,
            is_valid=is_valid,
            validation_errors=errors,
            normalized_value=normalized,
            confidence=0.8 if is_valid else 0.5
        )


class DocumentValidator:
    """Validador completo de documentos"""
    
    def __init__(self, validation_level: ValidationLevel = ValidationLevel.MODERATE):
        self.field_validator = FieldValidator(validation_level)
        self.logger = logging.getLogger(__name__)
        
        # Campos requeridos por tipo de documento
        self.required_fields = {
            "invoice": ["invoice_number", "date", "total"],
            "contract": ["contract_number", "start_date", "parties"],
            "form": ["applicant_name"],
            "receipt": ["receipt_number", "date", "amount"],
            "quote": ["quote_number", "date", "total"],
            "statement": ["statement_number", "period"]
        }
    
    def validate_document(
        self,
        document_id: str,
        document_type: str,
        extracted_fields: Dict[str, Any]
    ) -> DocumentValidationReport:
        """Valida un documento completo"""
        fields_validated = {}
        missing_required = []
        invalid_fields = []
        warnings = []
        
        # Obtener campos requeridos para este tipo
        required = self.required_fields.get(document_type, [])
        
        # Validar cada campo extraído
        for field_name, field_value in extracted_fields.items():
            validation_result = self._validate_field(field_name, field_value)
            fields_validated[field_name] = validation_result
            
            if not validation_result.is_valid:
                invalid_fields.append(field_name)
                if field_name in required:
                    warnings.append(f"Campo requerido '{field_name}' es inválido")
        
        # Verificar campos requeridos faltantes
        for required_field in required:
            if required_field not in extracted_fields:
                missing_required.append(required_field)
        
        # Calcular score de validación
        total_fields = len(extracted_fields)
        valid_fields = sum(1 for f in fields_validated.values() if f.is_valid)
        validation_score = valid_fields / max(total_fields, 1) if total_fields > 0 else 0.0
        
        # Penalizar campos requeridos faltantes
        if missing_required:
            validation_score *= 0.5
        
        overall_valid = (
            validation_score >= 0.7 and
            len(missing_required) == 0 and
            len(invalid_fields) == 0
        )
        
        return DocumentValidationReport(
            document_id=document_id,
            document_type=document_type,
            overall_valid=overall_valid,
            fields_validated=fields_validated,
            validation_score=validation_score,
            missing_required_fields=missing_required,
            invalid_fields=invalid_fields,
            warnings=warnings,
            validated_at=datetime.now().isoformat()
        )
    
    def _validate_field(self, field_name: str, field_value: Any) -> ValidationResult:
        """Valida un campo individual según su nombre"""
        field_name_lower = field_name.lower()
        
        # Mapear nombres de campos a validadores
        if "invoice_number" in field_name_lower or "invoice" in field_name_lower:
            return self.field_validator.validate_invoice_number(str(field_value))
        elif "contract_number" in field_name_lower or "contract" in field_name_lower:
            return self.field_validator.validate_invoice_number(str(field_value))  # Similar
        elif "date" in field_name_lower or "fecha" in field_name_lower:
            return self.field_validator.validate_date(str(field_value))
        elif "amount" in field_name_lower or "total" in field_name_lower or "monto" in field_name_lower:
            return self.field_validator.validate_amount(str(field_value))
        elif "email" in field_name_lower or "correo" in field_name_lower:
            return self.field_validator.validate_email(str(field_value))
        elif "phone" in field_name_lower or "teléfono" in field_name_lower or "telefono" in field_name_lower:
            return self.field_validator.validate_phone(str(field_value))
        elif "tax_id" in field_name_lower or "rut" in field_name_lower or "nit" in field_name_lower:
            return self.field_validator.validate_tax_id(str(field_value))
        else:
            # Validación genérica para campos desconocidos
            return ValidationResult(
                field_name=field_name,
                field_value=field_value,
                is_valid=True,  # Asumir válido si no hay validador específico
                validation_errors=[],
                normalized_value=str(field_value),
                confidence=0.7
            )
    
    def enrich_fields(self, extracted_fields: Dict[str, Any]) -> Dict[str, Any]:
        """ Enriquece campos con valores normalizados"""
        enriched = {}
        
        for field_name, field_value in extracted_fields.items():
            validation_result = self._validate_field(field_name, field_value)
            enriched[field_name] = {
                "original": field_value,
                "normalized": validation_result.normalized_value or field_value,
                "valid": validation_result.is_valid,
                "confidence": validation_result.confidence
            }
        
        return enriched

