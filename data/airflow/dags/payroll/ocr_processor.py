"""
Procesador OCR para Recibos de Gastos
Soporta múltiples proveedores: Tesseract, AWS Textract, Google Cloud Vision
"""

import logging
import base64
import io
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional, Dict, Any, List
from datetime import datetime
import re

logger = logging.getLogger(__name__)


@dataclass
class OCRResult:
    """Resultado del procesamiento OCR"""
    success: bool
    confidence: float
    extracted_data: Dict[str, Any]
    raw_text: Optional[str] = None
    error_message: Optional[str] = None
    provider: Optional[str] = None


class OCRProcessor:
    """Procesador OCR para recibos"""
    
    def __init__(
        self,
        provider: str = "tesseract",
        confidence_threshold: float = 0.7,
        **kwargs
    ):
        """
        Args:
            provider: Proveedor OCR (tesseract, aws_textract, google_vision)
            confidence_threshold: Umbral mínimo de confianza
            **kwargs: Configuración específica del proveedor
        """
        self.provider = provider
        self.confidence_threshold = confidence_threshold
        self.config = kwargs
        
        # Inicializar cliente según proveedor
        self._client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Inicializa el cliente OCR según el proveedor"""
        if self.provider == "tesseract":
            try:
                import pytesseract
                from PIL import Image
                
                if "tesseract_cmd" in self.config:
                    pytesseract.pytesseract.tesseract_cmd = self.config["tesseract_cmd"]
                
                self._client = pytesseract
                self._pil = Image
            except ImportError:
                logger.warning("pytesseract or PIL not available. Install with: pip install pytesseract pillow")
                self._client = None
        
        elif self.provider == "aws_textract":
            try:
                import boto3
                
                self._textract_client = boto3.client(
                    'textract',
                    aws_access_key_id=self.config.get("aws_access_key_id"),
                    aws_secret_access_key=self.config.get("aws_secret_access_key"),
                    region_name=self.config.get("aws_region", "us-east-1")
                )
            except ImportError:
                logger.warning("boto3 not available. Install with: pip install boto3")
                self._textract_client = None
            except Exception as e:
                logger.error(f"Error initializing AWS Textract: {e}")
                self._textract_client = None
        
        elif self.provider == "google_vision":
            try:
                from google.cloud import vision
                
                if "google_credentials_path" in self.config:
                    import os
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = self.config["google_credentials_path"]
                
                self._vision_client = vision.ImageAnnotatorClient()
            except ImportError:
                logger.warning("google-cloud-vision not available. Install with: pip install google-cloud-vision")
                self._vision_client = None
            except Exception as e:
                logger.error(f"Error initializing Google Vision: {e}")
                self._vision_client = None
    
    def process_image(
        self,
        image_data: bytes,
        image_format: str = "auto"
    ) -> OCRResult:
        """
        Procesa una imagen y extrae texto
        
        Args:
            image_data: Datos de la imagen (bytes)
            image_format: Formato de imagen (auto, png, jpeg, pdf)
        
        Returns:
            OCRResult con texto extraído
        """
        if self.provider == "tesseract":
            return self._process_tesseract(image_data)
        elif self.provider == "aws_textract":
            return self._process_textract(image_data)
        elif self.provider == "google_vision":
            return self._process_google_vision(image_data)
        else:
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message=f"Unsupported OCR provider: {self.provider}",
                provider=self.provider
            )
    
    def process_receipt(
        self,
        image_data: bytes
    ) -> OCRResult:
        """
        Procesa un recibo y extrae información estructurada
        
        Args:
            image_data: Datos de la imagen del recibo
        
        Returns:
            OCRResult con datos estructurados del recibo
        """
        # Primero extraer texto
        ocr_result = self.process_image(image_data)
        
        if not ocr_result.success:
            return ocr_result
        
        # Parsear datos estructurados del recibo
        extracted_data = self._parse_receipt_data(ocr_result.raw_text or "")
        
        return OCRResult(
            success=True,
            confidence=ocr_result.confidence,
            extracted_data=extracted_data,
            raw_text=ocr_result.raw_text,
            provider=self.provider
        )
    
    def _process_tesseract(self, image_data: bytes) -> OCRResult:
        """Procesa imagen con Tesseract"""
        if self._client is None:
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message="Tesseract not initialized",
                provider="tesseract"
            )
        
        try:
            image = self._pil.Image.open(io.BytesIO(image_data))
            lang = self.config.get("tesseract_lang", "eng")
            
            text = self._client.image_to_string(image, lang=lang)
            confidence_data = self._client.image_to_data(image, lang=lang, output_type=self._client.Output.DICT)
            
            # Calcular confianza promedio
            confidences = [float(c) for c in confidence_data.get("conf", []) if c != "-1"]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.5
            
            return OCRResult(
                success=True,
                confidence=avg_confidence,
                extracted_data={"text": text},
                raw_text=text,
                provider="tesseract"
            )
        except Exception as e:
            logger.error(f"Error processing with Tesseract: {e}")
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message=str(e),
                provider="tesseract"
            )
    
    def _process_textract(self, image_data: bytes) -> OCRResult:
        """Procesa imagen con AWS Textract"""
        if self._textract_client is None:
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message="AWS Textract not initialized",
                provider="aws_textract"
            )
        
        try:
            response = self._textract_client.detect_document_text(
                Document={'Bytes': image_data}
            )
            
            # Extraer texto
            text = ""
            for block in response.get("Blocks", []):
                if block.get("BlockType") == "LINE":
                    text += block.get("Text", "") + "\n"
            
            # Calcular confianza promedio
            confidences = [
                float(b.get("Confidence", 0))
                for b in response.get("Blocks", [])
                if b.get("BlockType") == "LINE"
            ]
            avg_confidence = sum(confidences) / len(confidences) / 100.0 if confidences else 0.5
            
            return OCRResult(
                success=True,
                confidence=avg_confidence,
                extracted_data={"text": text},
                raw_text=text,
                provider="aws_textract"
            )
        except Exception as e:
            logger.error(f"Error processing with AWS Textract: {e}")
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message=str(e),
                provider="aws_textract"
            )
    
    def _process_google_vision(self, image_data: bytes) -> OCRResult:
        """Procesa imagen con Google Cloud Vision"""
        if self._vision_client is None:
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message="Google Vision not initialized",
                provider="google_vision"
            )
        
        try:
            from google.cloud.vision import types as vision_types
            
            image = vision_types.Image(content=image_data)
            response = self._vision_client.document_text_detection(image=image)
            
            text = response.full_text_annotation.text if response.full_text_annotation else ""
            
            # Calcular confianza (Google Vision no proporciona confianza por palabra)
            avg_confidence = 0.85  # Estimación conservadora
            
            return OCRResult(
                success=True,
                confidence=avg_confidence,
                extracted_data={"text": text},
                raw_text=text,
                provider="google_vision"
            )
        except Exception as e:
            logger.error(f"Error processing with Google Vision: {e}")
            return OCRResult(
                success=False,
                confidence=0.0,
                extracted_data={},
                error_message=str(e),
                provider="google_vision"
            )
    
    def _parse_receipt_data(self, text: str) -> Dict[str, Any]:
        """Parsea texto de recibo y extrae datos estructurados"""
        data = {
            "vendor": None,
            "amount": None,
            "date": None,
            "items": [],
            "tax": None,
            "total": None
        }
        
        # Buscar montos (diferentes formatos: $123.45, 123.45, etc.)
        amount_patterns = [
            r'\$?\s*(\d+[,\.]\d{2})',  # $123.45 o 123,45
            r'(\d+\.\d{2})',  # 123.45
            r'(\d+,\d{2})',  # 123,45
        ]
        
        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                try:
                    amount_str = match.replace(",", ".")
                    amount = Decimal(amount_str)
                    amounts.append(amount)
                except:
                    pass
        
        if amounts:
            # El monto más grande probablemente es el total
            data["total"] = float(max(amounts))
            data["amount"] = float(max(amounts))
        
        # Buscar fechas
        date_patterns = [
            r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',  # MM/DD/YYYY
            r'\d{4}[/-]\d{1,2}[/-]\d{1,2}',  # YYYY/MM/DD
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text)
            if match:
                data["date"] = match.group()
                break
        
        # Buscar nombre del vendedor (primeras líneas o después de palabras clave)
        lines = text.split('\n')
        for i, line in enumerate(lines[:5]):  # Primeras 5 líneas
            if len(line.strip()) > 3 and not re.match(r'^[\d\$\.\,\s]+$', line):
                data["vendor"] = line.strip()
                break
        
        # Extraer items (líneas que parecen productos)
        for line in lines:
            line_clean = line.strip()
            if len(line_clean) > 5:
                # Si tiene un monto al final
                amount_match = re.search(r'([\d\.\,]+)', line_clean)
                if amount_match:
                    data["items"].append({
                        "description": line_clean,
                        "amount": amount_match.group()
                    })
        
        return data





