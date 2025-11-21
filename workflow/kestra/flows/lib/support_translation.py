"""
Sistema de Traducción Automática Multi-idioma.

Soporta traducción automática de tickets y respuestas.
"""
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from googletrans import Translator
    GOOGLETRANS_AVAILABLE = True
except ImportError:
    GOOGLETRANS_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)


class Language(Enum):
    """Idiomas soportados."""
    SPANISH = "es"
    ENGLISH = "en"
    PORTUGUESE = "pt"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    RUSSIAN = "ru"


@dataclass
class Translation:
    """Traducción."""
    original_text: str
    original_language: str
    translated_text: str
    target_language: str
    confidence: float = 0.0
    provider: str = "google"
    metadata: Dict[str, Any] = None


class SupportTranslator:
    """Traductor de soporte."""
    
    def __init__(self, provider: str = "google", api_key: Optional[str] = None):
        """
        Inicializa traductor.
        
        Args:
            provider: 'google' o 'openai'
            api_key: API key (opcional)
        """
        self.provider = provider
        
        if provider == "google" and GOOGLETRANS_AVAILABLE:
            self.translator = Translator()
        elif provider == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            if OPENAI_AVAILABLE and self.api_key:
                openai.api_key = self.api_key
    
    def detect_language(self, text: str) -> str:
        """
        Detecta idioma del texto.
        
        Args:
            text: Texto a analizar
            
        Returns:
            Código de idioma (ej: 'es', 'en')
        """
        if self.provider == "google" and GOOGLETRANS_AVAILABLE:
            try:
                detection = self.translator.detect(text)
                return detection.lang
            except Exception as e:
                logger.error(f"Error detecting language: {e}")
                return "en"  # Default
        else:
            # Detección básica por palabras clave
            return self._detect_language_basic(text)
    
    def translate(
        self,
        text: str,
        target_language: str,
        source_language: Optional[str] = None
    ) -> Translation:
        """
        Traduce texto.
        
        Args:
            text: Texto a traducir
            target_language: Idioma destino (código: 'es', 'en', etc.)
            source_language: Idioma origen (opcional, se detecta si no se proporciona)
            
        Returns:
            Traducción
        """
        if not source_language:
            source_language = self.detect_language(text)
        
        if source_language == target_language:
            return Translation(
                original_text=text,
                original_language=source_language,
                translated_text=text,
                target_language=target_language,
                confidence=1.0,
                provider=self.provider
            )
        
        if self.provider == "google" and GOOGLETRANS_AVAILABLE:
            return self._translate_google(text, source_language, target_language)
        elif self.provider == "openai" and OPENAI_AVAILABLE:
            return self._translate_openai(text, source_language, target_language)
        else:
            return Translation(
                original_text=text,
                original_language=source_language,
                translated_text=text,  # Sin traducción
                target_language=target_language,
                confidence=0.0,
                provider=self.provider
            )
    
    def translate_ticket(
        self,
        ticket_data: Dict[str, Any],
        target_language: str
    ) -> Dict[str, Any]:
        """
        Traduce un ticket completo.
        
        Args:
            ticket_data: Datos del ticket
            target_language: Idioma destino
            
        Returns:
            Ticket traducido
        """
        translated = ticket_data.copy()
        
        # Traducir subject
        if ticket_data.get("subject"):
            subject_translation = self.translate(
                ticket_data["subject"],
                target_language
            )
            translated["subject"] = subject_translation.translated_text
            translated["subject_original"] = ticket_data["subject"]
            translated["subject_language"] = subject_translation.original_language
        
        # Traducir description
        if ticket_data.get("description"):
            desc_translation = self.translate(
                ticket_data["description"],
                target_language
            )
            translated["description"] = desc_translation.translated_text
            translated["description_original"] = ticket_data["description"]
            translated["description_language"] = desc_translation.original_language
        
        # Mantener metadata de traducción
        translated["translation_metadata"] = {
            "target_language": target_language,
            "provider": self.provider,
            "translated_at": str(os.popen("date").read().strip())
        }
        
        return translated
    
    def translate_response(
        self,
        response_text: str,
        customer_language: str
    ) -> Translation:
        """
        Traduce respuesta al idioma del cliente.
        
        Args:
            response_text: Texto de respuesta
            customer_language: Idioma del cliente
            
        Returns:
            Traducción
        """
        return self.translate(response_text, customer_language)
    
    def _translate_google(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Translation:
        """Traduce usando Google Translate."""
        try:
            result = self.translator.translate(
                text,
                src=source_language,
                dest=target_language
            )
            
            return Translation(
                original_text=text,
                original_language=source_language,
                translated_text=result.text,
                target_language=target_language,
                confidence=0.9,  # Google Translate es bastante confiable
                provider="google"
            )
        except Exception as e:
            logger.error(f"Error translating with Google: {e}")
            return Translation(
                original_text=text,
                original_language=source_language,
                translated_text=text,
                target_language=target_language,
                confidence=0.0,
                provider="google"
            )
    
    def _translate_openai(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> Translation:
        """Traduce usando OpenAI."""
        try:
            language_names = {
                "es": "español",
                "en": "inglés",
                "pt": "portugués",
                "fr": "francés",
                "de": "alemán",
                "it": "italiano",
                "zh": "chino",
                "ja": "japonés",
                "ko": "coreano",
                "ru": "ruso"
            }
            
            source_name = language_names.get(source_language, source_language)
            target_name = language_names.get(target_language, target_language)
            
            prompt = f"Traduce el siguiente texto del {source_name} al {target_name}. Solo devuelve la traducción, sin explicaciones:\n\n{text}"
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Eres un traductor profesional."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            translated_text = response.choices[0].message.content.strip()
            
            return Translation(
                original_text=text,
                original_language=source_language,
                translated_text=translated_text,
                target_language=target_language,
                confidence=0.85,
                provider="openai"
            )
        except Exception as e:
            logger.error(f"Error translating with OpenAI: {e}")
            return Translation(
                original_text=text,
                original_language=source_language,
                translated_text=text,
                target_language=target_language,
                confidence=0.0,
                provider="openai"
            )
    
    def _detect_language_basic(self, text: str) -> str:
        """Detección básica de idioma por palabras clave."""
        text_lower = text.lower()
        
        # Palabras comunes en español
        spanish_words = ["el", "la", "de", "que", "y", "a", "en", "un", "es", "se", "no", "te", "lo", "le", "da"]
        spanish_count = sum(1 for word in spanish_words if word in text_lower)
        
        # Palabras comunes en inglés
        english_words = ["the", "be", "to", "of", "and", "a", "in", "that", "have", "i", "it", "for", "not", "on", "with"]
        english_count = sum(1 for word in english_words if word in text_lower)
        
        if spanish_count > english_count:
            return "es"
        elif english_count > spanish_count:
            return "en"
        else:
            return "en"  # Default


class MultiLanguageSupport:
    """Soporte multi-idioma completo."""
    
    def __init__(self, translator: SupportTranslator):
        """Inicializa soporte multi-idioma."""
        self.translator = translator
    
    def process_ticket(
        self,
        ticket_data: Dict[str, Any],
        agent_language: str = "es"
    ) -> Dict[str, Any]:
        """
        Procesa ticket para soporte multi-idioma.
        
        Args:
            ticket_data: Datos del ticket
            agent_language: Idioma preferido del agente
            
        Returns:
            Ticket procesado con traducciones
        """
        # Detectar idioma del ticket
        ticket_text = f"{ticket_data.get('subject', '')} {ticket_data.get('description', '')}"
        customer_language = self.translator.detect_language(ticket_text)
        
        # Si el idioma del ticket es diferente al del agente, traducir
        if customer_language != agent_language:
            translated_ticket = self.translator.translate_ticket(
                ticket_data,
                agent_language
            )
            translated_ticket["customer_language"] = customer_language
            translated_ticket["agent_language"] = agent_language
            return translated_ticket
        
        ticket_data["customer_language"] = customer_language
        ticket_data["agent_language"] = agent_language
        return ticket_data
    
    def prepare_response(
        self,
        response_text: str,
        customer_language: str
    ) -> str:
        """
        Prepara respuesta en el idioma del cliente.
        
        Args:
            response_text: Texto de respuesta
            customer_language: Idioma del cliente
            
        Returns:
            Respuesta traducida
        """
        translation = self.translator.translate_response(
            response_text,
            customer_language
        )
        return translation.translated_text

