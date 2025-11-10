"""
Compresión y Optimización de Archivos
======================================

Comprime y optimiza documentos para ahorrar espacio.
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging
import zipfile
import gzip
import shutil

logger = logging.getLogger(__name__)


class DocumentCompressor:
    """Compresor de documentos"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def compress_pdf(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        quality: str = "medium"
    ) -> str:
        """Comprime PDF"""
        try:
            import fitz  # PyMuPDF
        except ImportError:
            raise ImportError(
                "PyMuPDF es requerido. Instala con: pip install PyMuPDF"
            )
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.compressed.pdf'))
        
        doc = fitz.open(input_path)
        
        # Calidad de compresión
        quality_map = {
            "low": 0.5,
            "medium": 0.7,
            "high": 0.9
        }
        compression_quality = quality_map.get(quality, 0.7)
        
        # Comprimir imágenes
        for page_num in range(len(doc)):
            page = doc[page_num]
            image_list = page.get_images()
            
            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Redimensionar si es muy grande
                if len(image_bytes) > 1000000:  # 1MB
                    import io
                    from PIL import Image
                    img_obj = Image.open(io.BytesIO(image_bytes))
                    img_obj.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
                    
                    # Guardar comprimido
                    output = io.BytesIO()
                    img_obj.save(output, format='JPEG', quality=int(compression_quality * 100))
                    image_bytes = output.getvalue()
        
        # Guardar PDF comprimido
        doc.save(output_path, garbage=4, deflate=True, clean=True)
        doc.close()
        
        original_size = Path(input_path).stat().st_size
        compressed_size = Path(output_path).stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        self.logger.info(
            f"PDF comprimido: {original_size} -> {compressed_size} bytes "
            f"({compression_ratio:.1f}% reducción)"
        )
        
        return output_path
    
    def compress_images(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        quality: int = 85
    ) -> str:
        """Comprime imágenes"""
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("Pillow es requerido")
        
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('.compressed.jpg'))
        
        img = Image.open(input_path)
        
        # Convertir a RGB si es necesario
        if img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = background
        
        # Guardar comprimido
        img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        original_size = Path(input_path).stat().st_size
        compressed_size = Path(output_path).stat().st_size
        compression_ratio = (1 - compressed_size / original_size) * 100
        
        self.logger.info(
            f"Imagen comprimida: {original_size} -> {compressed_size} bytes "
            f"({compression_ratio:.1f}% reducción)"
        )
        
        return output_path
    
    def create_archive(
        self,
        files: List[str],
        archive_path: str,
        format: str = "zip"
    ) -> str:
        """Crea archivo comprimido con múltiples documentos"""
        if format == "zip":
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in files:
                    if Path(file_path).exists():
                        zipf.write(file_path, Path(file_path).name)
        
        elif format == "tar.gz":
            import tarfile
            with tarfile.open(archive_path, 'w:gz') as tarf:
                for file_path in files:
                    if Path(file_path).exists():
                        tarf.add(file_path, arcname=Path(file_path).name)
        
        total_size = sum(Path(f).stat().st_size for f in files if Path(f).exists())
        archive_size = Path(archive_path).stat().st_size
        compression_ratio = (1 - archive_size / total_size) * 100
        
        self.logger.info(
            f"Archivo creado: {archive_path} "
            f"({compression_ratio:.1f}% compresión)"
        )
        
        return archive_path
    
    def extract_archive(self, archive_path: str, output_dir: str) -> List[str]:
        """Extrae archivo comprimido"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        
        if archive_path.endswith('.zip'):
            with zipfile.ZipFile(archive_path, 'r') as zipf:
                zipf.extractall(output_dir)
                extracted_files = zipf.namelist()
        
        elif archive_path.endswith('.tar.gz') or archive_path.endswith('.tgz'):
            import tarfile
            with tarfile.open(archive_path, 'r:gz') as tarf:
                tarf.extractall(output_dir)
                extracted_files = tarf.getnames()
        
        self.logger.info(f"Extraídos {len(extracted_files)} archivos a {output_dir}")
        return extracted_files

