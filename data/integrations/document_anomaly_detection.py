"""
Detección de Anomalías en Documentos
=====================================

Detecta documentos anómalos o sospechosos.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import numpy as np

logger = logging.getLogger(__name__)


class AnomalyType(Enum):
    """Tipos de anomalías"""
    UNUSUAL_PATTERN = "unusual_pattern"
    MISSING_REQUIRED_FIELDS = "missing_required_fields"
    INCONSISTENT_DATA = "inconsistent_data"
    DUPLICATE_CONTENT = "duplicate_content"
    SUSPICIOUS_AMOUNT = "suspicious_amount"
    UNUSUAL_DATE = "unusual_date"
    LOW_QUALITY = "low_quality"


@dataclass
class Anomaly:
    """Anomalía detectada"""
    anomaly_id: str
    document_id: str
    anomaly_type: AnomalyType
    severity: str  # low, medium, high, critical
    description: str
    confidence: float
    detected_at: str
    metadata: Dict[str, Any] = None


class AnomalyDetector:
    """Detector de anomalías"""
    
    def __init__(self, db_connection=None):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)
        self.baseline_stats = self._load_baseline_stats()
    
    def detect_anomalies(
        self,
        document: Dict[str, Any]
    ) -> List[Anomaly]:
        """Detecta anomalías en un documento"""
        anomalies = []
        document_id = document.get("document_id", "unknown")
        
        # 1. Verificar campos requeridos faltantes
        missing_fields = self._check_missing_fields(document)
        if missing_fields:
            anomalies.append(Anomaly(
                anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-1",
                document_id=document_id,
                anomaly_type=AnomalyType.MISSING_REQUIRED_FIELDS,
                severity="medium",
                description=f"Campos requeridos faltantes: {', '.join(missing_fields)}",
                confidence=0.9,
                detected_at=datetime.now().isoformat(),
                metadata={"missing_fields": missing_fields}
            ))
        
        # 2. Verificar inconsistencias
        inconsistencies = self._check_inconsistencies(document)
        anomalies.extend(inconsistencies)
        
        # 3. Verificar montos sospechosos
        suspicious_amount = self._check_suspicious_amount(document)
        if suspicious_amount:
            anomalies.append(suspicious_amount)
        
        # 4. Verificar fechas inusuales
        unusual_date = self._check_unusual_date(document)
        if unusual_date:
            anomalies.append(unusual_date)
        
        # 5. Verificar calidad baja
        low_quality = self._check_low_quality(document)
        if low_quality:
            anomalies.append(low_quality)
        
        # 6. Verificar patrones inusuales
        unusual_pattern = self._check_unusual_patterns(document)
        if unusual_pattern:
            anomalies.append(unusual_pattern)
        
        return anomalies
    
    def _check_missing_fields(self, document: Dict[str, Any]) -> List[str]:
        """Verifica campos requeridos faltantes"""
        doc_type = document.get("document_type", "")
        extracted_fields = document.get("extracted_fields", {})
        
        required_fields = {
            "invoice": ["invoice_number", "date", "total"],
            "contract": ["contract_number", "start_date", "parties"],
            "form": ["applicant_name"]
        }
        
        required = required_fields.get(doc_type, [])
        missing = [field for field in required if field not in extracted_fields]
        
        return missing
    
    def _check_inconsistencies(self, document: Dict[str, Any]) -> List[Anomaly]:
        """Verifica inconsistencias en datos"""
        anomalies = []
        document_id = document.get("document_id", "unknown")
        extracted_fields = document.get("extracted_fields", {})
        
        # Verificar que subtotal + impuestos = total (aproximadamente)
        if "invoice" in document.get("document_type", "").lower():
            subtotal = self._parse_amount(extracted_fields.get("subtotal", "0"))
            taxes = self._parse_amount(extracted_fields.get("taxes", "0"))
            total = self._parse_amount(extracted_fields.get("total", "0"))
            
            if subtotal > 0 and taxes > 0 and total > 0:
                calculated = subtotal + taxes
                diff = abs(total - calculated)
                if diff > total * 0.05:  # 5% de diferencia
                    anomalies.append(Anomaly(
                        anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-2",
                        document_id=document_id,
                        anomaly_type=AnomalyType.INCONSISTENT_DATA,
                        severity="high",
                        description=f"Inconsistencia en montos: Subtotal + Impuestos ({calculated}) != Total ({total})",
                        confidence=0.85,
                        detected_at=datetime.now().isoformat(),
                        metadata={
                            "subtotal": subtotal,
                            "taxes": taxes,
                            "total": total,
                            "calculated": calculated
                        }
                    ))
        
        return anomalies
    
    def _check_suspicious_amount(self, document: Dict[str, Any]) -> Optional[Anomaly]:
        """Verifica montos sospechosos"""
        extracted_fields = document.get("extracted_fields", {})
        total = self._parse_amount(extracted_fields.get("total", "0"))
        
        if total == 0:
            return Anomaly(
                anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-3",
                document_id=document.get("document_id", "unknown"),
                anomaly_type=AnomalyType.SUSPICIOUS_AMOUNT,
                severity="medium",
                description="Monto total es cero",
                confidence=0.8,
                detected_at=datetime.now().isoformat()
            )
        
        # Verificar contra baseline (si está disponible)
        if self.baseline_stats:
            avg_amount = self.baseline_stats.get("avg_amount", 0)
            std_amount = self.baseline_stats.get("std_amount", 0)
            
            if avg_amount > 0 and std_amount > 0:
                z_score = (total - avg_amount) / std_amount
                if abs(z_score) > 3:  # Más de 3 desviaciones estándar
                    return Anomaly(
                        anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-4",
                        document_id=document.get("document_id", "unknown"),
                        anomaly_type=AnomalyType.SUSPICIOUS_AMOUNT,
                        severity="high",
                        description=f"Monto inusualmente alto/bajo: {total} (z-score: {z_score:.2f})",
                        confidence=0.75,
                        detected_at=datetime.now().isoformat(),
                        metadata={"amount": total, "z_score": z_score}
                    )
        
        return None
    
    def _check_unusual_date(self, document: Dict[str, Any]) -> Optional[Anomaly]:
        """Verifica fechas inusuales"""
        extracted_fields = document.get("extracted_fields", {})
        date_str = extracted_fields.get("date")
        
        if not date_str:
            return None
        
        try:
            from dateutil import parser
            doc_date = parser.parse(date_str)
            
            # Verificar si es fecha futura (para facturas)
            if doc_date > datetime.now():
                return Anomaly(
                    anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-5",
                    document_id=document.get("document_id", "unknown"),
                    anomaly_type=AnomalyType.UNUSUAL_DATE,
                    severity="medium",
                    description=f"Fecha futura: {date_str}",
                    confidence=0.9,
                    detected_at=datetime.now().isoformat()
                )
            
            # Verificar si es muy antigua (> 5 años)
            if (datetime.now() - doc_date).days > 1825:
                return Anomaly(
                    anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-6",
                    document_id=document.get("document_id", "unknown"),
                    anomaly_type=AnomalyType.UNUSUAL_DATE,
                    severity="low",
                    description=f"Fecha muy antigua: {date_str}",
                    confidence=0.8,
                    detected_at=datetime.now().isoformat()
                )
        except:
            pass
        
        return None
    
    def _check_low_quality(self, document: Dict[str, Any]) -> Optional[Anomaly]:
        """Verifica calidad baja"""
        ocr_confidence = document.get("ocr_confidence", 1.0)
        classification_confidence = document.get("classification_confidence", 1.0)
        
        if ocr_confidence < 0.5 or classification_confidence < 0.5:
            return Anomaly(
                anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-7",
                document_id=document.get("document_id", "unknown"),
                anomaly_type=AnomalyType.LOW_QUALITY,
                severity="medium",
                description=f"Calidad baja: OCR={ocr_confidence:.2%}, Clasificación={classification_confidence:.2%}",
                confidence=0.9,
                detected_at=datetime.now().isoformat(),
                metadata={
                    "ocr_confidence": ocr_confidence,
                    "classification_confidence": classification_confidence
                }
            )
        
        return None
    
    def _check_unusual_patterns(self, document: Dict[str, Any]) -> Optional[Anomaly]:
        """Verifica patrones inusuales"""
        extracted_text = document.get("extracted_text", "")
        
        # Verificar texto muy corto
        if len(extracted_text.strip()) < 50:
            return Anomaly(
                anomaly_id=f"ANOM-{datetime.now().strftime('%Y%m%d%H%M%S')}-8",
                document_id=document.get("document_id", "unknown"),
                anomaly_type=AnomalyType.UNUSUAL_PATTERN,
                severity="low",
                description="Texto extraído muy corto",
                confidence=0.7,
                detected_at=datetime.now().isoformat()
            )
        
        return None
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parsea monto a float"""
        try:
            if isinstance(amount_str, (int, float)):
                return float(amount_str)
            cleaned = str(amount_str).replace(',', '').replace('$', '').strip()
            return float(cleaned)
        except:
            return 0.0
    
    def _load_baseline_stats(self) -> Dict[str, float]:
        """Carga estadísticas baseline desde BD"""
        if not self.db:
            return {}
        
        try:
            cursor = self.db.cursor()
            cursor.execute("""
                SELECT 
                    AVG(CAST(extracted_fields->>'total' AS NUMERIC)) as avg_amount,
                    STDDEV(CAST(extracted_fields->>'total' AS NUMERIC)) as std_amount
                FROM processed_documents
                WHERE document_type = 'invoice'
                  AND extracted_fields->>'total' IS NOT NULL
                  AND processed_at >= CURRENT_DATE - INTERVAL '30 days'
            """)
            
            row = cursor.fetchone()
            if row and row[0]:
                return {
                    "avg_amount": float(row[0] or 0),
                    "std_amount": float(row[1] or 0)
                }
        except Exception as e:
            self.logger.warning(f"Error cargando baseline stats: {e}")
        
        return {}

