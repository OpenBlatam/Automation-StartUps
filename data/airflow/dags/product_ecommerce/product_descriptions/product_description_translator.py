"""
Sistema de traducción automática para descripciones de productos.

Soporta múltiples idiomas y mantiene el contexto de marketing.
"""

import logging
from typing import Dict, List, Optional
from product_description_generator import LLMClient

logger = logging.getLogger(__name__)


class ProductDescriptionTranslator:
    """Traductor de descripciones manteniendo contexto de marketing."""
    
    SUPPORTED_LANGUAGES = {
        'es': 'Español',
        'en': 'English',
        'pt': 'Português',
        'fr': 'Français',
        'de': 'Deutsch',
        'it': 'Italiano',
        'nl': 'Nederlands',
        'pl': 'Polski',
        'ru': 'Русский',
        'ja': '日本語',
        'zh': '中文',
        'ko': '한국어'
    }
    
    def __init__(self, llm_client: LLMClient):
        self.llm_client = llm_client
    
    def translate_description(self, description_data: Dict, target_language: str, preserve_seo: bool = True) -> Dict:
        """
        Traduce una descripción completa a otro idioma.
        
        Args:
            description_data: Datos de la descripción original
            target_language: Idioma objetivo (código ISO)
            preserve_seo: Mantener optimización SEO
        
        Returns:
            Dict con descripción traducida
        """
        if target_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(f"Idioma no soportado: {target_language}")
        
        description = description_data.get('description', '')
        title = description_data.get('title', '')
        meta_description = description_data.get('meta_description', '')
        
        # Traducir con contexto de marketing
        translated_description = self._translate_with_context(
            description, 
            target_language, 
            'description',
            preserve_seo
        )
        
        translated_title = self._translate_with_context(
            title,
            target_language,
            'title',
            preserve_seo
        )
        
        translated_meta = self._translate_with_context(
            meta_description,
            target_language,
            'meta_description',
            preserve_seo
        )
        
        # Traducir keywords manteniendo relevancia SEO
        original_keywords = description_data.get('seo_keywords', [])
        translated_keywords = self._translate_keywords(original_keywords, target_language)
        
        return {
            'description': translated_description,
            'title': translated_title,
            'meta_description': translated_meta,
            'seo_keywords': translated_keywords,
            'original_language': description_data.get('language', 'es'),
            'target_language': target_language,
            'word_count': len(translated_description.split()),
            'translated_at': __import__('datetime').datetime.now().isoformat()
        }
    
    def translate_batch(self, descriptions: List[Dict], target_language: str) -> List[Dict]:
        """
        Traduce múltiples descripciones.
        
        Args:
            descriptions: Lista de descripciones
            target_language: Idioma objetivo
        
        Returns:
            Lista de descripciones traducidas
        """
        translated = []
        for desc in descriptions:
            try:
                translated_desc = self.translate_description(desc, target_language)
                translated.append(translated_desc)
            except Exception as e:
                logger.error(f"Error traduciendo descripción: {str(e)}")
                translated.append({
                    'error': str(e),
                    'original': desc
                })
        
        return translated
    
    def _translate_with_context(self, text: str, target_language: str, content_type: str, preserve_seo: bool) -> str:
        """Traduce texto manteniendo contexto de marketing."""
        if not text:
            return text
        
        language_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        system_prompt = f"""Eres un traductor experto especializado en marketing y e-commerce.
Traduce el siguiente texto al {language_name}, manteniendo:
1. El tono persuasivo y emocional del original
2. Las palabras de poder y términos de marketing
3. La estructura y formato
4. Los números y datos específicos (sin traducir)
5. La optimización SEO si aplica
"""
        
        if preserve_seo:
            system_prompt += "\n6. Las keywords SEO de forma natural en el idioma objetivo"
        
        if content_type == 'title':
            system_prompt += "\n7. Mantén el título conciso y optimizado para SEO"
        elif content_type == 'meta_description':
            system_prompt += "\n8. Mantén la meta descripción dentro de 160 caracteres"
        
        prompt = f"""Traduce el siguiente {content_type} al {language_name}:

{text}

Proporciona SOLO la traducción, sin explicaciones adicionales."""
        
        try:
            result = self.llm_client.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=0.3,  # Baja temperatura para traducción más precisa
                max_tokens=2000
            )
            
            return result['content'].strip()
        except Exception as e:
            logger.error(f"Error en traducción: {str(e)}")
            return text  # Retornar original si falla
    
    def _translate_keywords(self, keywords: List[str], target_language: str) -> List[str]:
        """Traduce keywords manteniendo relevancia SEO."""
        if not keywords:
            return []
        
        # Traducir keywords manteniendo contexto SEO
        translated = []
        for keyword in keywords:
            try:
                translated_keyword = self._translate_with_context(
                    keyword,
                    target_language,
                    'keyword',
                    preserve_seo=True
                )
                translated.append(translated_keyword)
            except Exception as e:
                logger.warning(f"Error traduciendo keyword '{keyword}': {str(e)}")
                translated.append(keyword)  # Mantener original si falla
        
        return translated
    
    @classmethod
    def get_supported_languages(cls) -> Dict[str, str]:
        """Obtiene lista de idiomas soportados."""
        return cls.SUPPORTED_LANGUAGES.copy()






