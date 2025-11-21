"""
Traducción Automática de Documentos
====================================

Traduce texto extraído de documentos a diferentes idiomas.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class TranslationResult:
    """Resultado de traducción"""
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence: float
    translated_at: str


class DocumentTranslator:
    """Traductor de documentos"""
    
    def __init__(self, provider: str = "google", api_key: Optional[str] = None):
        self.provider = provider
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)
        self._translator = None
        self._initialize_translator()
    
    def _initialize_translator(self):
        """Inicializa traductor según proveedor"""
        if self.provider == "google":
            try:
                from googletrans import Translator
                self._translator = Translator()
                self.logger.info("Traductor Google inicializado")
            except ImportError:
                self.logger.warning(
                    "googletrans no disponible. "
                    "Instala con: pip install googletrans==4.0.0-rc1"
                )
        elif self.provider == "deepL":
            try:
                import deepl
                if not self.api_key:
                    raise ValueError("API key requerida para DeepL")
                self._translator = deepl.Translator(self.api_key)
                self.logger.info("Traductor DeepL inicializado")
            except ImportError:
                self.logger.warning(
                    "deepl no disponible. "
                    "Instala con: pip install deepl"
                )
    
    def translate_text(
        self,
        text: str,
        target_language: str = "en",
        source_language: Optional[str] = None
    ) -> TranslationResult:
        """Traduce texto"""
        if not self._translator:
            raise ValueError("Traductor no inicializado")
        
        try:
            if self.provider == "google":
                result = self._translator.translate(
                    text,
                    dest=target_language,
                    src=source_language
                )
                
                return TranslationResult(
                    original_text=text,
                    translated_text=result.text,
                    source_language=result.src,
                    target_language=target_language,
                    confidence=0.9,  # Google no proporciona confianza
                    translated_at=datetime.now().isoformat()
                )
            
            elif self.provider == "deepL":
                result = self._translator.translate_text(
                    text,
                    target_lang=target_language.upper(),
                    source_lang=source_language.upper() if source_language else None
                )
                
                return TranslationResult(
                    original_text=text,
                    translated_text=result.text,
                    source_language=result.detected_source_lang.lower(),
                    target_language=target_language,
                    confidence=0.95,  # DeepL es muy preciso
                    translated_at=datetime.now().isoformat()
                )
        
        except Exception as e:
            self.logger.error(f"Error traduciendo: {e}")
            raise
    
    def translate_document_fields(
        self,
        extracted_fields: Dict[str, Any],
        target_language: str = "en"
    ) -> Dict[str, Any]:
        """Traduce campos extraídos de un documento"""
        translated_fields = {}
        
        for key, value in extracted_fields.items():
            if isinstance(value, str) and value.strip():
                try:
                    translation = self.translate_text(value, target_language)
                    translated_fields[key] = {
                        "original": value,
                        "translated": translation.translated_text,
                        "source_language": translation.source_language
                    }
                except Exception as e:
                    self.logger.warning(f"Error traduciendo campo {key}: {e}")
                    translated_fields[key] = value
            else:
                translated_fields[key] = value
        
        return translated_fields
    
    def translate_batch(
        self,
        texts: List[str],
        target_language: str = "en"
    ) -> List[TranslationResult]:
        """Traduce múltiples textos"""
        results = []
        
        for text in texts:
            try:
                result = self.translate_text(text, target_language)
                results.append(result)
            except Exception as e:
                self.logger.error(f"Error traduciendo texto: {e}")
                continue
        
        return results
    
    def detect_language(self, text: str) -> str:
        """Detecta idioma del texto"""
        if not self._translator:
            raise ValueError("Traductor no inicializado")
        
        try:
            if self.provider == "google":
                result = self._translator.detect(text)
                return result.lang
            elif self.provider == "deepL":
                # DeepL detecta automáticamente
                result = self._translator.translate_text(text, target_lang="EN")
                return result.detected_source_lang.lower()
        except Exception as e:
            self.logger.error(f"Error detectando idioma: {e}")
            return "unknown"

