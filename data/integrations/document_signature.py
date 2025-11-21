"""
Reconocimiento y Validación de Firmas
======================================

Detecta y valida firmas en documentos procesados.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
from datetime import datetime
import cv2
import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


class SignatureStatus(Enum):
    """Estado de una firma"""
    DETECTED = "detected"
    VERIFIED = "verified"
    INVALID = "invalid"
    NOT_FOUND = "not_found"


@dataclass
class SignatureRegion:
    """Región donde se detectó una firma"""
    x: int
    y: int
    width: int
    height: int
    confidence: float
    image: Optional[np.ndarray] = None


@dataclass
class SignatureAnalysis:
    """Análisis de firma"""
    document_id: str
    signatures_found: int
    signature_regions: List[SignatureRegion]
    status: SignatureStatus
    validation_score: float
    metadata: Dict[str, Any] = None


class SignatureDetector:
    """Detector de firmas en documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def detect_signatures(
        self,
        image_path: str,
        min_area: int = 500,
        max_area: int = 50000
    ) -> List[SignatureRegion]:
        """Detecta firmas en una imagen"""
        try:
            # Cargar imagen
            img = cv2.imread(image_path)
            if img is None:
                raise ValueError(f"No se pudo cargar imagen: {image_path}")
            
            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Aplicar threshold adaptativo
            thresh = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
            
            # Encontrar contornos
            contours, _ = cv2.findContours(
                thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )
            
            signature_regions = []
            
            for contour in contours:
                area = cv2.contourArea(contour)
                
                # Filtrar por área
                if area < min_area or area > max_area:
                    continue
                
                # Obtener bounding box
                x, y, w, h = cv2.boundingRect(contour)
                
                # Calcular características de firma
                # Las firmas suelen tener:
                # - Aspect ratio irregular
                # - Muchos detalles pequeños
                aspect_ratio = w / h if h > 0 else 0
                
                # Filtrar por aspecto (firmas suelen ser más anchas que altas)
                if aspect_ratio < 0.5 or aspect_ratio > 5:
                    continue
                
                # Calcular densidad de contornos (firmas tienen muchos detalles)
                roi = thresh[y:y+h, x:x+w]
                contour_density = np.sum(roi > 0) / (w * h)
                
                if contour_density < 0.1 or contour_density > 0.7:
                    continue
                
                # Calcular confianza basada en características
                confidence = self._calculate_signature_confidence(
                    roi, aspect_ratio, contour_density
                )
                
                if confidence > 0.5:  # Threshold mínimo
                    signature_regions.append(SignatureRegion(
                        x=x,
                        y=y,
                        width=w,
                        height=h,
                        confidence=confidence,
                        image=roi
                    ))
            
            # Ordenar por confianza
            signature_regions.sort(key=lambda s: s.confidence, reverse=True)
            
            return signature_regions
            
        except Exception as e:
            self.logger.error(f"Error detectando firmas: {e}")
            return []
    
    def _calculate_signature_confidence(
        self,
        roi: np.ndarray,
        aspect_ratio: float,
        contour_density: float
    ) -> float:
        """Calcula confianza de que una región es una firma"""
        # Normalizar características
        aspect_score = min(aspect_ratio / 2.0, 1.0) if aspect_ratio > 0 else 0
        density_score = min(contour_density * 2, 1.0)
        
        # Calcular variación espacial (firmas tienen variación)
        variance = np.var(roi)
        variance_score = min(variance / 10000, 1.0)
        
        # Score combinado
        confidence = (aspect_score * 0.3 + density_score * 0.4 + variance_score * 0.3)
        
        return float(confidence)
    
    def extract_signature_image(
        self,
        image_path: str,
        region: SignatureRegion
    ) -> np.ndarray:
        """Extrae la imagen de una firma"""
        img = cv2.imread(image_path)
        return img[
            region.y:region.y + region.height,
            region.x:region.x + region.width
        ]
    
    def compare_signatures(
        self,
        signature1: np.ndarray,
        signature2: np.ndarray
    ) -> float:
        """Compara dos firmas y retorna similitud (0-1)"""
        try:
            # Redimensionar a mismo tamaño
            h1, w1 = signature1.shape[:2]
            h2, w2 = signature2.shape[:2]
            
            target_size = (max(w1, w2), max(h1, h2))
            sig1_resized = cv2.resize(signature1, target_size)
            sig2_resized = cv2.resize(signature2, target_size)
            
            # Convertir a escala de grises si es necesario
            if len(sig1_resized.shape) == 3:
                sig1_resized = cv2.cvtColor(sig1_resized, cv2.COLOR_BGR2GRAY)
            if len(sig2_resized.shape) == 3:
                sig2_resized = cv2.cvtColor(sig2_resized, cv2.COLOR_BGR2GRAY)
            
            # Calcular similitud usando template matching
            result = cv2.matchTemplate(sig1_resized, sig2_resized, cv2.TM_CCOEFF_NORMED)
            similarity = float(np.max(result))
            
            return similarity
            
        except Exception as e:
            self.logger.error(f"Error comparando firmas: {e}")
            return 0.0
    
    def validate_signature(
        self,
        document_id: str,
        image_path: str,
        reference_signature: Optional[np.ndarray] = None
    ) -> SignatureAnalysis:
        """Valida firmas en un documento"""
        signatures = self.detect_signatures(image_path)
        
        validation_score = 0.0
        status = SignatureStatus.NOT_FOUND
        
        if signatures:
            status = SignatureStatus.DETECTED
            
            # Si hay firma de referencia, comparar
            if reference_signature is not None and signatures:
                best_match = signatures[0]
                sig_image = self.extract_signature_image(image_path, best_match)
                similarity = self.compare_signatures(sig_image, reference_signature)
                
                if similarity > 0.7:
                    status = SignatureStatus.VERIFIED
                    validation_score = similarity
                else:
                    status = SignatureStatus.INVALID
                    validation_score = similarity
            else:
                # Sin referencia, usar confianza de detección
                validation_score = signatures[0].confidence if signatures else 0.0
        
        return SignatureAnalysis(
            document_id=document_id,
            signatures_found=len(signatures),
            signature_regions=signatures,
            status=status,
            validation_score=validation_score,
            metadata={
                "detection_method": "contour_analysis",
                "detected_at": datetime.now().isoformat()
            }
        )

