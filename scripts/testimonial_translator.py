#!/usr/bin/env python3
"""
Traductor Automático Multi-idioma para Testimonios
Traduce contenido a múltiples idiomas manteniendo contexto y tono
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Translation:
    """Traducción de contenido"""
    language: str
    content: str
    confidence: float
    original_content: str


class MultiLanguageTranslator:
    """Traductor multi-idioma usando OpenAI"""
    
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
        'ko': '한국어',
        'zh': '中文',
        'ar': 'العربية'
    }
    
    def __init__(self, openai_client=None):
        """
        Inicializa el traductor
        
        Args:
            openai_client: Cliente de OpenAI (opcional)
        """
        self.openai_client = openai_client
    
    def translate(
        self,
        content: str,
        target_language: str,
        source_language: Optional[str] = None,
        context: Optional[str] = None,
        preserve_tone: bool = True
    ) -> Translation:
        """
        Traduce contenido a otro idioma
        
        Args:
            content: Contenido a traducir
            target_language: Idioma objetivo (código ISO)
            source_language: Idioma origen (opcional, auto-detecta)
            context: Contexto adicional para mejor traducción
            preserve_tone: Mantener tono original
        
        Returns:
            Translation con contenido traducido
        """
        if not self.openai_client:
            logger.warning("OpenAI client no disponible para traducción")
            return Translation(
                language=target_language,
                content=content,
                confidence=0.0,
                original_content=content
            )
        
        target_lang_name = self.SUPPORTED_LANGUAGES.get(target_language, target_language)
        
        system_prompt = f"""Eres un traductor profesional especializado en marketing y redes sociales.
Traduce el contenido manteniendo:
- El tono y estilo original
- El contexto de marketing/negocios
- Las emociones y sentimientos
- La estructura y formato
- Los hashtags y menciones relevantes

Idioma objetivo: {target_lang_name}"""
        
        user_prompt = f"Traduce el siguiente contenido al {target_lang_name}:\n\n{content}"
        
        if context:
            user_prompt += f"\n\nContexto: {context}"
        
        if preserve_tone:
            user_prompt += "\n\nMantén el tono profesional y cálido del original."
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            translated_content = response.choices[0].message.content.strip()
            
            return Translation(
                language=target_language,
                content=translated_content,
                confidence=0.9,  # OpenAI generalmente tiene alta confianza
                original_content=content
            )
        except Exception as e:
            logger.error(f"Error en traducción: {e}")
            return Translation(
                language=target_language,
                content=content,
                confidence=0.0,
                original_content=content
            )
    
    def translate_batch(
        self,
        content: str,
        target_languages: List[str],
        source_language: Optional[str] = None,
        context: Optional[str] = None
    ) -> Dict[str, Translation]:
        """
        Traduce contenido a múltiples idiomas
        
        Args:
            content: Contenido a traducir
            target_languages: Lista de idiomas objetivo
            source_language: Idioma origen
            context: Contexto adicional
        
        Returns:
            Dict con traducciones por idioma
        """
        translations = {}
        
        for lang in target_languages:
            translation = self.translate(
                content=content,
                target_language=lang,
                source_language=source_language,
                context=context
            )
            translations[lang] = translation
        
        return translations
    
    def translate_post(
        self,
        post_data: Dict[str, Any],
        target_language: str,
        translate_hashtags: bool = False
    ) -> Dict[str, Any]:
        """
        Traduce un post completo incluyendo hashtags y CTA
        
        Args:
            post_data: Datos completos del post
            target_language: Idioma objetivo
            translate_hashtags: Traducir hashtags también
        
        Returns:
            Post traducido completo
        """
        translated_post = post_data.copy()
        
        # Traducir contenido principal
        content = post_data.get('post_content', '')
        if content:
            translation = self.translate(
                content=content,
                target_language=target_language,
                context=f"Publicación para {post_data.get('platform', 'red social')}"
            )
            translated_post['post_content'] = translation.content
            translated_post['post_content_original'] = content
            translated_post['translation_language'] = target_language
        
        # Traducir CTA si existe
        cta = post_data.get('call_to_action', '')
        if cta:
            cta_translation = self.translate(
                content=cta,
                target_language=target_language,
                context="Llamada a la acción"
            )
            translated_post['call_to_action'] = cta_translation.content
        
        # Traducir hashtags si se solicita
        if translate_hashtags and post_data.get('hashtags'):
            translated_hashtags = []
            for hashtag in post_data['hashtags']:
                # Remover # para traducir
                tag_text = hashtag.replace('#', '')
                tag_translation = self.translate(
                    content=tag_text,
                    target_language=target_language,
                    context="Hashtag para redes sociales"
                )
                # Agregar # de vuelta
                translated_hashtags.append(f"#{tag_translation.content.replace(' ', '')}")
            translated_post['hashtags'] = translated_hashtags
        
        # Actualizar metadata
        translated_post['metadata'] = translated_post.get('metadata', {})
        translated_post['metadata']['translated'] = True
        translated_post['metadata']['target_language'] = target_language
        
        return translated_post
    
    def detect_language(self, content: str) -> str:
        """
        Detecta el idioma del contenido
        
        Args:
            content: Contenido a analizar
        
        Returns:
            Código ISO del idioma detectado
        """
        # Detección simple basada en palabras comunes
        # En producción, usar una librería como langdetect
        
        spanish_indicators = ['el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se']
        english_indicators = ['the', 'be', 'to', 'of', 'and', 'a', 'in', 'that', 'have', 'it']
        
        content_lower = content.lower()
        spanish_count = sum(1 for word in spanish_indicators if word in content_lower)
        english_count = sum(1 for word in english_indicators if word in content_lower)
        
        if spanish_count > english_count:
            return 'es'
        elif english_count > spanish_count:
            return 'en'
        else:
            return 'es'  # Default


