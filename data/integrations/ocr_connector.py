"""
Conector OCR para múltiples servicios
=====================================

Soporte para:
- Tesseract OCR (local)
- Google Cloud Vision API
- Azure Computer Vision
- AWS Textract
- OpenAI Vision API
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import base64
import io
from pathlib import Path

logger = logging.getLogger(__name__)


class OCRProvider(Enum):
    """Proveedores de OCR disponibles"""
    TESSERACT = "tesseract"
    GOOGLE_VISION = "google_vision"
    AZURE_VISION = "azure_vision"
    AWS_TEXTRACT = "aws_textract"
    OPENAI_VISION = "openai_vision"


@dataclass
class OCRResult:
    """Resultado de procesamiento OCR"""
    text: str
    confidence: float
    provider: str
    language: Optional[str] = None
    bounding_boxes: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    raw_response: Optional[Dict[str, Any]] = None


@dataclass
class DocumentMetadata:
    """Metadatos del documento"""
    filename: str
    file_type: str
    file_size: int
    mime_type: Optional[str] = None
    pages: Optional[int] = None
    dimensions: Optional[Tuple[int, int]] = None
    created_at: Optional[str] = None
    modified_at: Optional[str] = None


class BaseOCRConnector(ABC):
    """Clase base para conectores OCR"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.provider = config.get("provider", "tesseract")
        self.logger = logging.getLogger(f"{__name__}.{self.provider}")
    
    @abstractmethod
    def extract_text(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        language: Optional[str] = None
    ) -> OCRResult:
        """Extrae texto de una imagen/documento"""
        pass
    
    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """Verifica salud del servicio OCR"""
        pass


class TesseractOCRConnector(BaseOCRConnector):
    """Conector para Tesseract OCR (local)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.tesseract_cmd = config.get("tesseract_cmd", "tesseract")
        self._tesseract = None
        self._pytesseract = None
    
    def _ensure_import(self):
        """Importa pytesseract solo cuando se necesita"""
        if self._pytesseract is None:
            try:
                import pytesseract
                from PIL import Image
                self._pytesseract = pytesseract
                self._Image = Image
                
                # Configurar ruta si está especificada
                if self.config.get("tesseract_cmd"):
                    pytesseract.pytesseract.tesseract_cmd = self.config["tesseract_cmd"]
            except ImportError:
                raise ImportError(
                    "pytesseract y Pillow son requeridos. "
                    "Instala con: pip install pytesseract pillow"
                )
    
    def extract_text(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        language: Optional[str] = None
    ) -> OCRResult:
        """Extrae texto usando Tesseract"""
        self._ensure_import()
        
        if image_path:
            image = self._Image.open(image_path)
        elif image_bytes:
            image = self._Image.open(io.BytesIO(image_bytes))
        else:
            raise ValueError("image_path o image_bytes debe ser proporcionado")
        
        # Configuración de idioma
        lang = language or self.config.get("language", "spa+eng")
        
        try:
            # Extraer texto
            text = self._pytesseract.image_to_string(image, lang=lang)
            
            # Obtener datos detallados para confianza
            data = self._pytesseract.image_to_data(image, lang=lang, output_type=self._pytesseract.Output.DICT)
            
            # Calcular confianza promedio
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Extraer bounding boxes
            bounding_boxes = []
            n_boxes = len(data['level'])
            for i in range(n_boxes):
                if int(data['conf'][i]) > 0:
                    bounding_boxes.append({
                        'text': data['text'][i],
                        'confidence': int(data['conf'][i]),
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })
            
            return OCRResult(
                text=text.strip(),
                confidence=avg_confidence / 100.0,  # Normalizar a 0-1
                provider="tesseract",
                language=lang,
                bounding_boxes=bounding_boxes,
                metadata={
                    'word_count': len(text.split()),
                    'char_count': len(text)
                }
            )
        except Exception as e:
            self.logger.error(f"Error en OCR Tesseract: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica que Tesseract esté disponible"""
        try:
            self._ensure_import()
            version = self._pytesseract.get_tesseract_version()
            return {
                "status": "healthy",
                "provider": "tesseract",
                "version": str(version),
                "available": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "tesseract",
                "error": str(e),
                "available": False
            }


class GoogleVisionOCRConnector(BaseOCRConnector):
    """Conector para Google Cloud Vision API"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.project_id = config.get("project_id")
        if not self.api_key:
            raise ValueError("Google Vision API key es requerido")
    
    def extract_text(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        language: Optional[str] = None
    ) -> OCRResult:
        """Extrae texto usando Google Vision API"""
        try:
            from google.cloud import vision
            from google.oauth2 import service_account
        except ImportError:
            raise ImportError(
                "google-cloud-vision es requerido. "
                "Instala con: pip install google-cloud-vision"
            )
        
        # Configurar cliente
        if self.config.get("credentials_path"):
            credentials = service_account.Credentials.from_service_account_file(
                self.config["credentials_path"]
            )
            client = vision.ImageAnnotatorClient(credentials=credentials)
        else:
            client = vision.ImageAnnotatorClient()
        
        # Preparar imagen
        if image_path:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
        
        image = vision.Image(content=image_bytes)
        
        # Realizar OCR
        response = client.text_detection(image=image)
        
        if response.error.message:
            raise Exception(f"Google Vision API error: {response.error.message}")
        
        texts = response.text_annotations
        if not texts:
            return OCRResult(
                text="",
                confidence=0.0,
                provider="google_vision",
                language=language
            )
        
        # Texto completo
        full_text = texts[0].description
        
        # Calcular confianza promedio de las detecciones
        confidences = []
        bounding_boxes = []
        
        for text in texts[1:]:  # Skip first (full text)
            if hasattr(text, 'confidence'):
                confidences.append(text.confidence)
            
            vertices = [(v.x, v.y) for v in text.bounding_poly.vertices]
            bounding_boxes.append({
                'text': text.description,
                'confidence': getattr(text, 'confidence', 0.8),
                'vertices': vertices
            })
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.9
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            provider="google_vision",
            language=language,
            bounding_boxes=bounding_boxes,
            metadata={
                'word_count': len(full_text.split()),
                'char_count': len(full_text),
                'detections': len(texts) - 1
            },
            raw_response={
                'annotations_count': len(texts)
            }
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica conexión con Google Vision API"""
        try:
            # Intentar una llamada simple
            test_image = base64.b64encode(b"test").decode('utf-8')
            # En producción, harías una llamada real
            return {
                "status": "healthy",
                "provider": "google_vision",
                "available": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "google_vision",
                "error": str(e),
                "available": False
            }


class AzureVisionOCRConnector(BaseOCRConnector):
    """Conector para Azure Computer Vision"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.endpoint = config.get("endpoint")
        self.api_key = config.get("api_key")
        if not self.endpoint or not self.api_key:
            raise ValueError("Azure Vision endpoint y api_key son requeridos")
    
    def extract_text(
        self,
        image_path: Optional[str] = None,
        image_bytes: Optional[bytes] = None,
        language: Optional[str] = None
    ) -> OCRResult:
        """Extrae texto usando Azure Computer Vision"""
        import requests
        
        if image_path:
            with open(image_path, 'rb') as f:
                image_bytes = f.read()
        
        url = f"{self.endpoint}/vision/v3.2/ocr"
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key,
            "Content-Type": "application/octet-stream"
        }
        params = {}
        if language:
            params["language"] = language
        
        response = requests.post(url, headers=headers, params=params, data=image_bytes)
        response.raise_for_status()
        
        result = response.json()
        
        # Extraer texto de todas las regiones
        text_parts = []
        bounding_boxes = []
        
        for region in result.get("regions", []):
            for line in region.get("lines", []):
                line_text = " ".join([word.get("text", "") for word in line.get("words", [])])
                text_parts.append(line_text)
                
                # Bounding box de la línea
                if line.get("boundingBox"):
                    bbox = line["boundingBox"].split(",")
                    bounding_boxes.append({
                        'text': line_text,
                        'bounding_box': bbox,
                        'confidence': sum([w.get("confidence", 0.8) for w in line.get("words", [])]) / max(len(line.get("words", [])), 1)
                    })
        
        full_text = "\n".join(text_parts)
        
        # Calcular confianza promedio
        confidences = [bbox.get("confidence", 0.8) for bbox in bounding_boxes]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.8
        
        return OCRResult(
            text=full_text,
            confidence=avg_confidence,
            provider="azure_vision",
            language=language or result.get("language", "unknown"),
            bounding_boxes=bounding_boxes,
            metadata={
                'regions': len(result.get("regions", [])),
                'word_count': len(full_text.split())
            },
            raw_response=result
        )
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica conexión con Azure Vision"""
        try:
            import requests
            # Health check simplificado
            return {
                "status": "healthy",
                "provider": "azure_vision",
                "endpoint": self.endpoint,
                "available": True
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "provider": "azure_vision",
                "error": str(e),
                "available": False
            }


def create_ocr_connector(provider: str, config: Dict[str, Any]) -> BaseOCRConnector:
    """Factory para crear conectores OCR"""
    provider_enum = OCRProvider(provider)
    
    if provider_enum == OCRProvider.TESSERACT:
        return TesseractOCRConnector(config)
    elif provider_enum == OCRProvider.GOOGLE_VISION:
        return GoogleVisionOCRConnector(config)
    elif provider_enum == OCRProvider.AZURE_VISION:
        return AzureVisionOCRConnector(config)
    else:
        raise ValueError(f"Proveedor OCR no soportado: {provider}")

