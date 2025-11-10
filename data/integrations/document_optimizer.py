"""
Optimizador de Documentos
==========================

Optimiza imágenes antes del procesamiento OCR para mejorar resultados.
"""

from typing import Dict, Any, Optional, Tuple
from pathlib import Path
import logging
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger(__name__)


class DocumentOptimizer:
    """Optimiza documentos antes del procesamiento OCR"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def optimize_for_ocr(
        self,
        image_path: str,
        output_path: Optional[str] = None,
        options: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Optimiza imagen para mejor reconocimiento OCR
        
        Args:
            image_path: Ruta de la imagen original
            output_path: Ruta de salida (opcional)
            options: Opciones de optimización
        
        Returns:
            Ruta de la imagen optimizada
        """
        options = options or {}
        enhance_brightness = options.get("enhance_brightness", True)
        enhance_contrast = options.get("enhance_contrast", True)
        denoise = options.get("denoise", True)
        deskew = options.get("deskew", True)
        resize = options.get("resize", True)
        target_dpi = options.get("target_dpi", 300)
        
        # Cargar imagen
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"No se pudo cargar imagen: {image_path}")
        
        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Deskew (corregir inclinación)
        if deskew:
            gray = self._deskew_image(gray)
        
        # 2. Mejorar brillo y contraste
        if enhance_brightness or enhance_contrast:
            gray = self._enhance_image(gray, enhance_brightness, enhance_contrast)
        
        # 3. Desenfoque (reducir ruido)
        if denoise:
            gray = self._denoise_image(gray)
        
        # 4. Redimensionar si es necesario
        if resize:
            gray = self._resize_for_dpi(gray, target_dpi)
        
        # 5. Aplicar threshold adaptativo
        optimized = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Guardar imagen optimizada
        if output_path is None:
            output_path = str(Path(image_path).with_suffix('.optimized.png'))
        
        cv2.imwrite(output_path, optimized)
        self.logger.info(f"Imagen optimizada guardada: {output_path}")
        
        return output_path
    
    def _deskew_image(self, image: np.ndarray) -> np.ndarray:
        """Corrige inclinación de la imagen"""
        # Encontrar ángulo de inclinación
        coords = np.column_stack(np.where(image > 0))
        if len(coords) == 0:
            return image
        
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        
        # Si el ángulo es muy pequeño, no rotar
        if abs(angle) < 0.5:
            return image
        
        # Rotar imagen
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(
            image, M, (w, h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE
        )
        
        return rotated
    
    def _enhance_image(
        self,
        image: np.ndarray,
        brightness: bool = True,
        contrast: bool = True
    ) -> np.ndarray:
        """Mejora brillo y contraste"""
        # Convertir a PIL para mejor control
        pil_img = Image.fromarray(image)
        
        if brightness:
            enhancer = ImageEnhance.Brightness(pil_img)
            pil_img = enhancer.enhance(1.2)  # Aumentar 20%
        
        if contrast:
            enhancer = ImageEnhance.Contrast(pil_img)
            pil_img = enhancer.enhance(1.3)  # Aumentar 30%
        
        # Convertir de vuelta a numpy
        return np.array(pil_img)
    
    def _denoise_image(self, image: np.ndarray) -> np.ndarray:
        """Reduce ruido en la imagen"""
        # Usar filtro bilateral para preservar bordes
        denoised = cv2.bilateralFilter(image, 9, 75, 75)
        return denoised
    
    def _resize_for_dpi(
        self,
        image: np.ndarray,
        target_dpi: int = 300
    ) -> np.ndarray:
        """Redimensiona imagen para target DPI"""
        # Calcular factor de escala basado en DPI
        # Asumir que la imagen original es 72 DPI
        scale_factor = target_dpi / 72.0
        
        if scale_factor > 1.0:
            height, width = image.shape[:2]
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            
            resized = cv2.resize(
                image,
                (new_width, new_height),
                interpolation=cv2.INTER_CUBIC
            )
            return resized
        
        return image
    
    def batch_optimize(
        self,
        image_paths: list,
        output_dir: str,
        options: Optional[Dict[str, Any]] = None
    ) -> list:
        """Optimiza múltiples imágenes"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        optimized_paths = []
        for img_path in image_paths:
            try:
                output_file = output_path / f"{Path(img_path).stem}.optimized.png"
                optimized = self.optimize_for_ocr(
                    str(img_path),
                    str(output_file),
                    options
                )
                optimized_paths.append(optimized)
            except Exception as e:
                self.logger.error(f"Error optimizando {img_path}: {e}")
        
        return optimized_paths

