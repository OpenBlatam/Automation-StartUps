"""
Procesador de Documentos Completo
==================================

Integra OCR, clasificación y archivado automático de documentos.
Soporta facturas, contratos, formularios y otros documentos.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import json
import shutil
from datetime import datetime
import hashlib

from .ocr_connector import (
    BaseOCRConnector, create_ocr_connector, OCRProvider, OCRResult
)
from .document_classifier import (
    DocumentClassifier, DocumentType, ClassificationResult
)
from .document_cache import DocumentCache

logger = logging.getLogger(__name__)


@dataclass
class ProcessedDocument:
    """Documento procesado completo"""
    document_id: str
    original_filename: str
    file_path: str
    file_hash: str
    document_type: str
    classification_confidence: float
    extracted_text: str
    ocr_confidence: float
    extracted_fields: Dict[str, Any]
    archive_path: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    processed_at: Optional[str] = None
    ocr_provider: Optional[str] = None
    keywords_matched: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario para serialización"""
        return asdict(self)


class DocumentProcessor:
    """Procesador principal de documentos"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Configurar OCR
        ocr_config = config.get("ocr", {})
        ocr_provider = ocr_config.get("provider", "tesseract")
        self.ocr_connector = create_ocr_connector(ocr_provider, ocr_config)
        
        # Configurar clasificador
        classifier_config = config.get("classifier", {})
        self.classifier = DocumentClassifier(classifier_config)
        
        # Configuración de archivado
        self.archive_config = config.get("archive", {})
        self.archive_base_path = Path(self.archive_config.get("base_path", "./archives"))
        self.archive_structure = self.archive_config.get("structure", "by_type")  # by_type, by_date, flat
        
        # Cache (opcional)
        cache_config = config.get("cache", {})
        if cache_config.get("enabled", False):
            self.cache = DocumentCache(
                cache_dir=cache_config.get("cache_dir", "./.cache"),
                default_ttl=cache_config.get("ttl", 86400)
            )
        else:
            self.cache = None
        
        # Crear estructura de directorios
        self.archive_base_path.mkdir(parents=True, exist_ok=True)
    
    def process_document(
        self,
        file_path: str,
        filename: Optional[str] = None,
        archive: bool = True,
        use_cache: bool = True
    ) -> ProcessedDocument:
        """
        Procesa un documento completo: OCR + Clasificación + Archivado
        
        Args:
            file_path: Ruta al archivo a procesar
            filename: Nombre del archivo (opcional)
            archive: Si True, archiva el documento automáticamente
            use_cache: Si True, usa cache si está disponible
        
        Returns:
            ProcessedDocument con toda la información procesada
        """
        file_path_obj = Path(file_path)
        if not file_path_obj.exists():
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        
        filename = filename or file_path_obj.name
        
        self.logger.info(f"Procesando documento: {filename}")
        
        # 1. Calcular hash del archivo
        file_hash = self._calculate_file_hash(file_path)
        
        # 2. Verificar cache
        if use_cache and self.cache:
            cached_result = self.cache.get(file_path, self.config)
            if cached_result:
                self.logger.info("Usando resultado de cache")
                return ProcessedDocument(**cached_result)
        
        # 3. Extraer texto con OCR
        self.logger.info("Extrayendo texto con OCR...")
        ocr_result = self.ocr_connector.extract_text(image_path=file_path)
        
        # 4. Clasificar documento
        self.logger.info("Clasificando documento...")
        classification = self.classifier.classify(
            text=ocr_result.text,
            filename=filename
        )
        
        # 5. Generar ID único
        document_id = self._generate_document_id(filename, file_hash)
        
        # 6. Archivado (si está habilitado)
        archive_path = None
        if archive:
            self.logger.info("Archivando documento...")
            archive_path = self._archive_document(
                file_path=file_path,
                filename=filename,
                document_type=classification.document_type,
                document_id=document_id
            )
        
        # 7. Crear objeto procesado
        processed = ProcessedDocument(
            document_id=document_id,
            original_filename=filename,
            file_path=str(file_path),
            file_hash=file_hash,
            document_type=classification.document_type.value,
            classification_confidence=classification.confidence,
            extracted_text=ocr_result.text,
            ocr_confidence=ocr_result.confidence,
            extracted_fields=classification.extracted_fields,
            archive_path=str(archive_path) if archive_path else None,
            metadata={
                "ocr_metadata": ocr_result.metadata,
                "classification_metadata": classification.metadata,
                "file_size": file_path_obj.stat().st_size,
                "file_extension": file_path_obj.suffix.lower(),
                "mime_type": self._guess_mime_type(file_path_obj.suffix)
            },
            processed_at=datetime.now().isoformat(),
            ocr_provider=ocr_result.provider,
            keywords_matched=classification.keywords_matched
        )
        
        # 8. Guardar en cache
        if use_cache and self.cache:
            self.cache.set(file_path, self.config, processed.to_dict())
        
        self.logger.info(
            f"Documento procesado: {document_id} - "
            f"Tipo: {classification.document_type.value} "
            f"(Confianza: {classification.confidence:.2%})"
        )
        
        return processed
    
    def process_batch(
        self,
        file_paths: List[str],
        archive: bool = True,
        use_cache: bool = True
    ) -> List[ProcessedDocument]:
        """Procesa múltiples documentos en lote"""
        results = []
        
        for file_path in file_paths:
            try:
                processed = self.process_document(
                    file_path, archive=archive, use_cache=use_cache
                )
                results.append(processed)
            except Exception as e:
                self.logger.error(f"Error procesando {file_path}: {e}")
                # Continuar con el siguiente archivo
                continue
        
        return results
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calcula hash SHA256 del archivo"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def _generate_document_id(self, filename: str, file_hash: str) -> str:
        """Genera ID único para el documento"""
        # Usar primeros 8 caracteres del hash + timestamp
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        short_hash = file_hash[:8]
        return f"DOC-{timestamp}-{short_hash}"
    
    def _archive_document(
        self,
        file_path: str,
        filename: str,
        document_type: DocumentType,
        document_id: str
    ) -> Path:
        """Archiva el documento en la estructura configurada"""
        source_path = Path(file_path)
        
        if self.archive_structure == "by_type":
            # Organizar por tipo de documento
            archive_dir = self.archive_base_path / document_type.value
        elif self.archive_structure == "by_date":
            # Organizar por fecha
            date_str = datetime.now().strftime("%Y/%m/%d")
            archive_dir = self.archive_base_path / date_str
        elif self.archive_structure == "by_type_and_date":
            # Combinación: tipo/fecha
            date_str = datetime.now().strftime("%Y/%m")
            archive_dir = self.archive_base_path / document_type.value / date_str
        else:
            # Estructura plana
            archive_dir = self.archive_base_path
        
        # Crear directorio si no existe
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Generar nombre de archivo único
        file_extension = source_path.suffix
        archive_filename = f"{document_id}{file_extension}"
        archive_path = archive_dir / archive_filename
        
        # Copiar archivo
        shutil.copy2(source_path, archive_path)
        
        self.logger.info(f"Documento archivado en: {archive_path}")
        
        return archive_path
    
    def _guess_mime_type(self, extension: str) -> str:
        """Intenta adivinar el tipo MIME basado en la extensión"""
        mime_types = {
            ".pdf": "application/pdf",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".tiff": "image/tiff",
            ".tif": "image/tiff",
            ".bmp": "image/bmp",
            ".doc": "application/msword",
            ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        }
        return mime_types.get(extension.lower(), "application/octet-stream")
    
    def health_check(self) -> Dict[str, Any]:
        """Verifica salud de todos los componentes"""
        ocr_health = self.ocr_connector.health_check()
        
        cache_stats = None
        if self.cache:
            cache_stats = self.cache.get_stats()
        
        return {
            "status": "healthy" if ocr_health.get("available") else "unhealthy",
            "components": {
                "ocr": ocr_health,
                "classifier": {
                    "status": "healthy",
                    "available": True
                },
                "archive": {
                    "status": "healthy" if self.archive_base_path.exists() else "unhealthy",
                    "base_path": str(self.archive_base_path),
                    "writable": self._check_directory_writable(self.archive_base_path)
                },
                "cache": cache_stats
            }
        }
    
    def _check_directory_writable(self, path: Path) -> bool:
        """Verifica si un directorio es escribible"""
        try:
            test_file = path / ".write_test"
            test_file.write_text("test")
            test_file.unlink()
            return True
        except Exception:
            return False
    
    def export_results(
        self,
        documents: List[ProcessedDocument],
        format: str = "json",
        output_path: Optional[str] = None
    ) -> str:
        """
        Exporta resultados del procesamiento
        
        Args:
            documents: Lista de documentos procesados
            format: Formato de exportación (json, csv)
            output_path: Ruta de salida (opcional)
        
        Returns:
            Ruta del archivo exportado
        """
        if format == "json":
            data = [doc.to_dict() for doc in documents]
            filename = output_path or f"documents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            import csv
            filename = output_path or f"documents_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            
            if not documents:
                return filename
            
            fieldnames = [
                "document_id", "original_filename", "document_type",
                "classification_confidence", "ocr_confidence",
                "archive_path", "processed_at"
            ]
            
            # Agregar campos extraídos dinámicamente
            all_extracted_fields = set()
            for doc in documents:
                all_extracted_fields.update(doc.extracted_fields.keys())
            
            fieldnames.extend(sorted(all_extracted_fields))
            
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for doc in documents:
                    row = {
                        "document_id": doc.document_id,
                        "original_filename": doc.original_filename,
                        "document_type": doc.document_type,
                        "classification_confidence": doc.classification_confidence,
                        "ocr_confidence": doc.ocr_confidence,
                        "archive_path": doc.archive_path or "",
                        "processed_at": doc.processed_at or ""
                    }
                    row.update(doc.extracted_fields)
                    writer.writerow(row)
        else:
            raise ValueError(f"Formato no soportado: {format}")
        
        self.logger.info(f"Resultados exportados a: {filename}")
        return filename
