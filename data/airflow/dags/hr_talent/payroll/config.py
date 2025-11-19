"""
Configuración centralizada para el módulo de nómina
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from decimal import Decimal


@dataclass
class PayrollConfig:
    """Configuración para procesamiento de nómina"""
    
    # Database
    postgres_conn_id: str = "postgres_default"
    
    # OCR Configuration
    ocr_provider: str = "tesseract"  # tesseract, aws_textract, google_vision
    ocr_confidence_threshold: float = 0.7
    
    # AWS Textract (opcional)
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "us-east-1"
    
    # Google Cloud Vision (opcional)
    google_credentials_path: Optional[str] = None
    google_project_id: Optional[str] = None
    
    # Tesseract (opcional)
    tesseract_cmd: Optional[str] = None
    tesseract_lang: str = "eng"
    
    # Overtime Configuration
    regular_hours_per_week: Decimal = Decimal("40.0")
    overtime_multiplier: Decimal = Decimal("1.5")
    double_time_multiplier: Decimal = Decimal("2.0")
    
    # Default Tax and Benefits Rates
    default_tax_rate: Decimal = Decimal("0.25")  # 25%
    default_benefits_rate: Decimal = Decimal("0.10")  # 10%
    
    # Processing Configuration
    auto_approve_expenses_under: Decimal = Decimal("50.0")
    max_expense_per_receipt: Decimal = Decimal("10000.0")
    
    @classmethod
    def from_env(cls) -> "PayrollConfig":
        """Crea configuración desde variables de entorno"""
        return cls(
            postgres_conn_id=os.getenv("PAYROLL_POSTGRES_CONN_ID", "postgres_default"),
            ocr_provider=os.getenv("PAYROLL_OCR_PROVIDER", "tesseract"),
            ocr_confidence_threshold=float(os.getenv("PAYROLL_OCR_CONFIDENCE_THRESHOLD", "0.7")),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            aws_region=os.getenv("AWS_REGION", "us-east-1"),
            google_credentials_path=os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            google_project_id=os.getenv("GOOGLE_PROJECT_ID"),
            tesseract_cmd=os.getenv("TESSERACT_CMD"),
            tesseract_lang=os.getenv("TESSERACT_LANG", "eng"),
            regular_hours_per_week=Decimal(os.getenv("PAYROLL_REGULAR_HOURS_PER_WEEK", "40.0")),
            overtime_multiplier=Decimal(os.getenv("PAYROLL_OVERTIME_MULTIPLIER", "1.5")),
            double_time_multiplier=Decimal(os.getenv("PAYROLL_DOUBLE_TIME_MULTIPLIER", "2.0")),
            default_tax_rate=Decimal(os.getenv("PAYROLL_DEFAULT_TAX_RATE", "0.25")),
            default_benefits_rate=Decimal(os.getenv("PAYROLL_DEFAULT_BENEFITS_RATE", "0.10")),
            auto_approve_expenses_under=Decimal(os.getenv("PAYROLL_AUTO_APPROVE_EXPENSES_UNDER", "50.0")),
            max_expense_per_receipt=Decimal(os.getenv("PAYROLL_MAX_EXPENSE_PER_RECEIPT", "10000.0")),
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte configuración a diccionario"""
        return {
            "postgres_conn_id": self.postgres_conn_id,
            "ocr_provider": self.ocr_provider,
            "ocr_confidence_threshold": self.ocr_confidence_threshold,
            "regular_hours_per_week": str(self.regular_hours_per_week),
            "overtime_multiplier": str(self.overtime_multiplier),
            "default_tax_rate": str(self.default_tax_rate),
            "default_benefits_rate": str(self.default_benefits_rate),
        }





