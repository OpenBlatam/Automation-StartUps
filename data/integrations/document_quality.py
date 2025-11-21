"""
Análisis de Calidad de Documentos
===================================

Analiza la calidad de documentos procesados: claridad, resolución,
completitud, etc.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
from PIL import Image
import math

logger = logging.getLogger(__name__)


class QualityLevel(Enum):
    """Niveles de calidad"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"


@dataclass
class QualityMetrics:
    """Métricas de calidad"""
    ocr_confidence: float
    image_resolution: Optional[Tuple[int, int]] = None
    image_dpi: Optional[float] = None
    brightness: Optional[float] = None
    contrast: Optional[float] = None
    sharpness: Optional[float] = None
    noise_level: Optional[float] = None
    text_completeness: float = 0.0
    field_completeness: float = 0.0
    overall_score: float = 0.0


@dataclass
class QualityReport:
    """Reporte completo de calidad"""
    document_id: str
    quality_level: QualityLevel
    metrics: QualityMetrics
    issues: List[str]
    recommendations: List[str]
    analyzed_at: str


class DocumentQualityAnalyzer:
    """Analizador de calidad de documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def analyze_image_quality(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """Analiza calidad de imagen"""
        try:
            img = Image.open(image_path)
            
            # Resolución
            width, height = img.size
            resolution = width * height
            
            # DPI (si está disponible en metadata)
            dpi = img.info.get('dpi', (72, 72))[0] if 'dpi' in img.info else None
            
            # Convertir a escala de grises para análisis
            if img.mode != 'L':
                gray_img = img.convert('L')
            else:
                gray_img = img
            
            import numpy as np
            img_array = np.array(gray_img)
            
            # Brillo promedio
            brightness = float(np.mean(img_array) / 255.0)
            
            # Contraste (desviación estándar)
            contrast = float(np.std(img_array) / 255.0)
            
            # Nitidez (Laplacian variance)
            from scipy import ndimage
            laplacian = ndimage.laplace(img_array)
            sharpness = float(np.var(laplacian))
            
            # Estimación de ruido (simplificada)
            # Usar variación local
            noise_level = float(np.std(laplacian) / np.mean(np.abs(laplacian)) if np.mean(np.abs(laplacian)) > 0 else 0)
            
            return {
                "resolution": (width, height),
                "total_pixels": resolution,
                "dpi": dpi,
                "brightness": brightness,
                "contrast": contrast,
                "sharpness": sharpness,
                "noise_level": noise_level,
                "mode": img.mode
            }
            
        except Exception as e:
            self.logger.error(f"Error analizando imagen: {e}")
            return {}
    
    def analyze_text_completeness(
        self,
        extracted_text: str,
        expected_fields: List[str],
        extracted_fields: Dict[str, Any]
    ) -> Dict[str, float]:
        """Analiza completitud del texto extraído"""
        # Completitud del texto
        text_length = len(extracted_text.strip())
        text_completeness = min(text_length / 500, 1.0)  # Normalizar a 500 caracteres
        
        # Completitud de campos
        fields_found = sum(1 for field in expected_fields if field in extracted_fields)
        field_completeness = fields_found / len(expected_fields) if expected_fields else 0.0
        
        return {
            "text_completeness": text_completeness,
            "field_completeness": field_completeness,
            "fields_found": fields_found,
            "total_expected_fields": len(expected_fields)
        }
    
    def analyze_document_quality(
        self,
        document_id: str,
        image_path: Optional[str],
        extracted_text: str,
        ocr_confidence: float,
        extracted_fields: Dict[str, Any],
        document_type: str
    ) -> QualityReport:
        """Analiza calidad completa de un documento"""
        issues = []
        recommendations = []
        
        # Métricas de imagen
        image_metrics = {}
        if image_path:
            image_metrics = self.analyze_image_quality(image_path)
        
        # Métricas de texto
        expected_fields = {
            "invoice": ["invoice_number", "date", "total"],
            "contract": ["contract_number", "start_date", "parties"],
            "form": ["applicant_name"]
        }.get(document_type, [])
        
        text_metrics = self.analyze_text_completeness(
            extracted_text,
            expected_fields,
            extracted_fields
        )
        
        # Calcular score general
        scores = []
        
        # OCR confidence (40% peso)
        scores.append(("ocr", ocr_confidence * 0.4))
        
        # Text completeness (20% peso)
        scores.append(("text", text_metrics["text_completeness"] * 0.2))
        
        # Field completeness (30% peso)
        scores.append(("fields", text_metrics["field_completeness"] * 0.3))
        
        # Image quality (10% peso, si está disponible)
        if image_metrics:
            # Normalizar métricas de imagen
            brightness_score = image_metrics.get("brightness", 0.5)
            contrast_score = image_metrics.get("contrast", 0.5)
            sharpness_score = min(image_metrics.get("sharpness", 0) / 1000, 1.0)  # Normalizar
            
            image_score = (brightness_score + contrast_score + sharpness_score) / 3.0
            scores.append(("image", image_score * 0.1))
            
            # Issues de imagen
            if image_metrics.get("brightness", 0.5) < 0.3:
                issues.append("Imagen muy oscura")
                recommendations.append("Ajustar brillo antes de escanear")
            elif image_metrics.get("brightness", 0.5) > 0.8:
                issues.append("Imagen muy brillante")
                recommendations.append("Reducir exposición")
            
            if image_metrics.get("contrast", 0.5) < 0.3:
                issues.append("Bajo contraste")
                recommendations.append("Mejorar contraste de la imagen")
            
            if image_metrics.get("sharpness", 0) < 100:
                issues.append("Imagen borrosa")
                recommendations.append("Escanear con mayor resolución")
            
            if image_metrics.get("dpi") and image_metrics["dpi"] < 200:
                issues.append(f"Resolución baja ({image_metrics['dpi']} DPI)")
                recommendations.append("Escanear a al menos 300 DPI")
        
        # Issues de OCR
        if ocr_confidence < 0.7:
            issues.append(f"Confianza OCR baja ({ocr_confidence:.2%})")
            recommendations.append("Revisar calidad de imagen original")
        
        # Issues de campos
        if text_metrics["field_completeness"] < 0.5:
            issues.append(f"Campos incompletos ({text_metrics['fields_found']}/{text_metrics['total_expected_fields']})")
            recommendations.append("Verificar que el documento contenga todos los campos requeridos")
        
        # Issues de texto
        if text_metrics["text_completeness"] < 0.3:
            issues.append("Texto extraído muy corto o incompleto")
            recommendations.append("Verificar que el documento esté completo y legible")
        
        # Calcular score total
        overall_score = sum(score for _, score in scores)
        
        # Determinar nivel de calidad
        if overall_score >= 0.9:
            quality_level = QualityLevel.EXCELLENT
        elif overall_score >= 0.75:
            quality_level = QualityLevel.GOOD
        elif overall_score >= 0.6:
            quality_level = QualityLevel.FAIR
        elif overall_score >= 0.4:
            quality_level = QualityLevel.POOR
        else:
            quality_level = QualityLevel.UNACCEPTABLE
        
        # Crear métricas
        metrics = QualityMetrics(
            ocr_confidence=ocr_confidence,
            image_resolution=image_metrics.get("resolution"),
            image_dpi=image_metrics.get("dpi"),
            brightness=image_metrics.get("brightness"),
            contrast=image_metrics.get("contrast"),
            sharpness=image_metrics.get("sharpness"),
            noise_level=image_metrics.get("noise_level"),
            text_completeness=text_metrics["text_completeness"],
            field_completeness=text_metrics["field_completeness"],
            overall_score=overall_score
        )
        
        return QualityReport(
            document_id=document_id,
            quality_level=quality_level,
            metrics=metrics,
            issues=issues,
            recommendations=recommendations,
            analyzed_at=datetime.now().isoformat()
        )

