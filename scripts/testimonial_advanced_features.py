#!/usr/bin/env python3
"""
Funcionalidades avanzadas para el convertidor de testimonios
Incluye: análisis de sentimiento, templates, cache, y más
"""

import hashlib
import json
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class SentimentAnalysis:
    """Resultado del análisis de sentimiento"""
    sentiment: str  # positive, negative, neutral
    score: float  # -1 a 1
    confidence: float  # 0 a 1
    positive_keywords: List[str]
    negative_keywords: List[str]
    emotional_intensity: float  # 0 a 1


@dataclass
class KeywordAnalysis:
    """Análisis de keywords y temas"""
    main_keywords: List[str]
    topics: List[str]
    metrics_mentioned: List[str]  # Números, porcentajes, etc.
    action_words: List[str]


class SentimentAnalyzer:
    """Analizador de sentimiento básico usando palabras clave"""
    
    POSITIVE_KEYWORDS = {
        'excelente', 'increíble', 'fantástico', 'genial', 'perfecto', 'maravilloso',
        'satisfecho', 'contento', 'feliz', 'agradecido', 'recomiendo', 'recomiendo',
        'superó', 'mejoró', 'aumentó', 'incrementó', 'mejor', 'mejorado',
        'resultados', 'éxito', 'logré', 'conseguí', 'obtuve', 'alcanzé',
        'funciona', 'funcionó', 'resolvió', 'solucionó', 'ayudó', 'ayuda'
    }
    
    NEGATIVE_KEYWORDS = {
        'problema', 'difícil', 'complicado', 'frustrado', 'decepcionado',
        'mal', 'malo', 'terrible', 'horrible', 'pésimo', 'falló', 'falla',
        'error', 'errores', 'no funciona', 'no funcionó', 'perdí', 'perdió'
    }
    
    INTENSITY_MODIFIERS = {
        'muy': 1.5, 'extremadamente': 2.0, 'súper': 1.5, 'increíblemente': 1.8,
        'totalmente': 1.3, 'completamente': 1.3, 'realmente': 1.2
    }
    
    def analyze(self, text: str) -> SentimentAnalysis:
        """Analiza el sentimiento de un texto"""
        text_lower = text.lower()
        
        # Buscar palabras positivas y negativas
        positive_found = [kw for kw in self.POSITIVE_KEYWORDS if kw in text_lower]
        negative_found = [kw for kw in self.NEGATIVE_KEYWORDS if kw in text_lower]
        
        # Calcular score básico
        positive_count = len(positive_found)
        negative_count = len(negative_found)
        total = positive_count + negative_count
        
        if total == 0:
            score = 0.0
            sentiment = "neutral"
            confidence = 0.3
        else:
            score = (positive_count - negative_count) / total
            if score > 0.2:
                sentiment = "positive"
            elif score < -0.2:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            confidence = min(1.0, abs(score) + 0.3)
        
        # Calcular intensidad emocional
        exclamation_count = text.count('!')
        caps_words = len(re.findall(r'\b[A-Z]{3,}\b', text))
        intensity = min(1.0, (exclamation_count * 0.1) + (caps_words * 0.05) + (abs(score) * 0.5))
        
        return SentimentAnalysis(
            sentiment=sentiment,
            score=round(score, 3),
            confidence=round(confidence, 3),
            positive_keywords=positive_found[:5],
            negative_keywords=negative_found[:5],
            emotional_intensity=round(intensity, 3)
        )


class KeywordAnalyzer:
    """Analizador de keywords y temas"""
    
    STOP_WORDS = {
        'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
        'de', 'del', 'en', 'con', 'por', 'para', 'a', 'al',
        'que', 'qué', 'cual', 'cuál', 'como', 'cómo', 'cuando',
        'donde', 'dónde', 'este', 'esta', 'estos', 'estas',
        'ese', 'esa', 'esos', 'esas', 'aquel', 'aquella',
        'y', 'o', 'pero', 'sin', 'sobre', 'entre', 'hasta'
    }
    
    METRIC_PATTERNS = [
        r'\d+%',  # Porcentajes
        r'\d+\s*(veces|meses|años|días|semanas)',  # Tiempo
        r'(aumentó|incrementó|mejoró|redujo|bajó)\s+\d+',  # Cambios con números
        r'\$\d+',  # Dinero
        r'\d+\s*(clientes|ventas|pedidos|usuarios)',  # Cantidades
    ]
    
    ACTION_WORDS = {
        'logré', 'conseguí', 'obtuve', 'alcanzé', 'mejoré', 'aumenté',
        'incrementé', 'reduje', 'optimicé', 'resolví', 'solucioné',
        'implementé', 'creé', 'desarrollé', 'mejoró', 'aumentó'
    }
    
    def analyze(self, text: str) -> KeywordAnalysis:
        """Analiza keywords y temas del texto"""
        text_lower = text.lower()
        
        # Extraer palabras clave (palabras significativas)
        words = re.findall(r'\b[a-záéíóúñ]{4,}\b', text_lower)
        keywords = [
            w for w in words 
            if w not in self.STOP_WORDS and len(w) > 3
        ]
        
        # Contar frecuencia y obtener las más comunes
        from collections import Counter
        word_freq = Counter(keywords)
        main_keywords = [word for word, count in word_freq.most_common(10)]
        
        # Extraer métricas mencionadas
        metrics = []
        for pattern in self.METRIC_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            metrics.extend(matches[:3])  # Limitar a 3 por tipo
        
        # Extraer palabras de acción
        action_words_found = [aw for aw in self.ACTION_WORDS if aw in text_lower]
        
        # Identificar temas generales
        topics = self._identify_topics(text_lower, main_keywords)
        
        return KeywordAnalysis(
            main_keywords=main_keywords[:10],
            topics=topics,
            metrics_mentioned=metrics[:5],
            action_words=action_words_found[:5]
        )
    
    def _identify_topics(self, text: str, keywords: List[str]) -> List[str]:
        """Identifica temas generales basados en keywords"""
        topic_keywords = {
            'ventas': ['ventas', 'venta', 'vender', 'cliente', 'clientes'],
            'productividad': ['productividad', 'eficiencia', 'proceso', 'procesos', 'tiempo'],
            'ingresos': ['ingresos', 'dinero', 'ganancias', 'beneficios', 'roi'],
            'satisfacción': ['satisfacción', 'satisfecho', 'contento', 'feliz', 'agradecido'],
            'tecnología': ['sistema', 'software', 'plataforma', 'herramienta', 'tecnología'],
            'servicio': ['servicio', 'atención', 'soporte', 'equipo', 'profesional'],
            'resultados': ['resultados', 'éxito', 'logré', 'conseguí', 'obtuve']
        }
        
        topics = []
        for topic, topic_kws in topic_keywords.items():
            if any(kw in text or kw in keywords for kw in topic_kws):
                topics.append(topic)
        
        return topics[:5]


class TemplateManager:
    """Gestor de templates personalizables"""
    
    DEFAULT_TEMPLATES = {
        'resultado_destacado': {
            'name': 'Resultado Destacado',
            'structure': [
                'Hook: Menciona el resultado principal',
                'Cuerpo: Detalla cómo se logró',
                'Cierre: Conecta con el público objetivo'
            ],
            'hook_examples': [
                'De {problema} a {resultado} en solo {tiempo}',
                '{Resultado} que cambió todo',
                'El resultado que {persona} estaba buscando'
            ]
        },
        'historia_narrativa': {
            'name': 'Historia Narrativa',
            'structure': [
                'Situación inicial (problema)',
                'Punto de inflexión (solución)',
                'Resultado final (éxito)',
                'Llamada a la acción'
            ],
            'hook_examples': [
                'Antes de esto, {problema}',
                'Todo cambió cuando...',
                'La historia de cómo {persona} logró {resultado}'
            ]
        },
        'testimonial_directo': {
            'name': 'Testimonial Directo',
            'structure': [
                'Cita directa del cliente',
                'Contexto breve',
                'Resultado específico',
                'Recomendación'
            ],
            'hook_examples': [
                '"{Cita}" - {Nombre}',
                'Según {persona}: "{cita}"',
                'Las palabras de {persona} lo dicen todo'
            ]
        }
    }
    
    def __init__(self, templates_dir: Optional[str] = None):
        """Inicializa el gestor de templates"""
        # Detectar directorio de templates automáticamente si no se especifica
        if templates_dir is None:
            # Buscar en n8n/templates/ relativo al script
            script_dir = Path(__file__).parent.parent
            templates_dir = str(script_dir / "n8n" / "templates")
        
        self.templates_dir = Path(templates_dir) if templates_dir else None
        self.templates = self.DEFAULT_TEMPLATES.copy()
        self._load_custom_templates()
    
    def _load_custom_templates(self):
        """Carga templates personalizados desde archivos"""
        if not self.templates_dir or not self.templates_dir.exists():
            return
        
        for template_file in self.templates_dir.glob('*.json'):
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = json.load(f)
                    template_id = template_file.stem
                    self.templates[template_id] = template_data
                    logger.info(f"Template cargado: {template_id}")
            except Exception as e:
                logger.warning(f"Error al cargar template {template_file}: {e}")
    
    def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Obtiene un template por ID"""
        return self.templates.get(template_id)
    
    def list_templates(self) -> List[Dict[str, Any]]:
        """Lista todos los templates disponibles"""
        return [
            {'id': tid, **data}
            for tid, data in self.templates.items()
        ]


class SimpleCache:
    """Cache simple en memoria con persistencia opcional"""
    
    def __init__(self, cache_file: Optional[str] = None, max_size: int = 100):
        """
        Inicializa el cache
        
        Args:
            cache_file: Archivo para persistir el cache (opcional)
            max_size: Tamaño máximo del cache en memoria
        """
        self.cache_file = cache_file
        self.max_size = max_size
        self.cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()
    
    def _generate_key(self, testimonial: str, target_audience: str, platform: str) -> str:
        """Genera una clave única para el cache"""
        content = f"{testimonial}|{target_audience}|{platform}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def get(self, testimonial: str, target_audience: str, platform: str) -> Optional[Dict[str, Any]]:
        """Obtiene un resultado del cache"""
        key = self._generate_key(testimonial, target_audience, platform)
        result = self.cache.get(key)
        if result:
            logger.debug(f"Cache hit para clave: {key[:8]}...")
        return result
    
    def set(self, testimonial: str, target_audience: str, platform: str, value: Dict[str, Any]):
        """Guarda un resultado en el cache"""
        key = self._generate_key(testimonial, target_audience, platform)
        
        # Limitar tamaño del cache
        if len(self.cache) >= self.max_size:
            # Eliminar el más antiguo (FIFO simple)
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = {
            **value,
            'cached_at': datetime.now().isoformat()
        }
        self._save_cache()
        logger.debug(f"Cache set para clave: {key[:8]}...")
    
    def _load_cache(self):
        """Carga el cache desde archivo"""
        if not self.cache_file:
            return
        
        cache_path = Path(self.cache_file)
        if cache_path.exists():
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"Cache cargado: {len(self.cache)} entradas")
            except Exception as e:
                logger.warning(f"Error al cargar cache: {e}")
    
    def _save_cache(self):
        """Guarda el cache en archivo"""
        if not self.cache_file:
            return
        
        try:
            cache_path = Path(self.cache_file)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"Error al guardar cache: {e}")
    
    def clear(self):
        """Limpia el cache"""
        self.cache.clear()
        if self.cache_file:
            cache_path = Path(self.cache_file)
            if cache_path.exists():
                cache_path.unlink()
        logger.info("Cache limpiado")


class FormatGenerator:
    """Generador de múltiples formatos para diferentes tipos de contenido"""
    
    def generate_carousel_captions(
        self,
        post_content: str,
        slide_count: int = 3
    ) -> List[Dict[str, str]]:
        """
        Genera captions para un carousel de Instagram/Facebook
        
        Args:
            post_content: Contenido principal de la publicación
            slide_count: Número de slides del carousel
        
        Returns:
            Lista de captions para cada slide
        """
        # Dividir el contenido en partes
        sentences = re.split(r'[.!?]\s+', post_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        slides = []
        sentences_per_slide = max(1, len(sentences) // slide_count)
        
        for i in range(slide_count):
            start_idx = i * sentences_per_slide
            end_idx = start_idx + sentences_per_slide if i < slide_count - 1 else len(sentences)
            
            slide_sentences = sentences[start_idx:end_idx]
            caption = '. '.join(slide_sentences)
            if i < slide_count - 1:
                caption += '...'
            
            slides.append({
                'slide_number': i + 1,
                'caption': caption,
                'length': len(caption)
            })
        
        return slides
    
    def generate_story_text(self, post_content: str, max_length: int = 100) -> str:
        """
        Genera texto optimizado para Stories (más corto y directo)
        
        Args:
            post_content: Contenido principal
            max_length: Longitud máxima
        
        Returns:
            Texto optimizado para Stories
        """
        # Extraer la primera oración o frase más impactante
        sentences = re.split(r'[.!?]\s+', post_content)
        
        if not sentences:
            return post_content[:max_length]
        
        # Buscar la oración más corta pero impactante
        best_sentence = sentences[0]
        for sentence in sentences[1:]:
            if len(sentence) <= max_length and len(sentence) > len(best_sentence):
                if any(word in sentence.lower() for word in ['resultado', 'logré', 'aumentó', 'mejoró']):
                    best_sentence = sentence
        
        # Ajustar longitud
        if len(best_sentence) > max_length:
            best_sentence = best_sentence[:max_length-3] + '...'
        
        return best_sentence.strip()
    
    def generate_thread_tweets(
        self,
        post_content: str,
        max_length: int = 280
    ) -> List[str]:
        """
        Genera un hilo de tweets desde el contenido
        
        Args:
            post_content: Contenido principal
            max_length: Longitud máxima por tweet
        
        Returns:
            Lista de tweets para el hilo
        """
        sentences = re.split(r'[.!?]\s+', post_content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        tweets = []
        current_tweet = ""
        
        for sentence in sentences:
            # Si la oración sola es muy larga, dividirla
            if len(sentence) > max_length:
                words = sentence.split()
                temp_sentence = ""
                for word in words:
                    if len(temp_sentence + word) + 1 <= max_length - 10:  # Dejar espacio para "1/3"
                        temp_sentence += word + " "
                    else:
                        if temp_sentence:
                            tweets.append(temp_sentence.strip())
                        temp_sentence = word + " "
                if temp_sentence:
                    current_tweet = temp_sentence.strip()
                continue
            
            # Agregar oración al tweet actual
            if len(current_tweet + sentence) + 3 <= max_length:  # +3 para " / "
                current_tweet += sentence + ". "
            else:
                if current_tweet:
                    tweets.append(current_tweet.strip())
                current_tweet = sentence + ". "
        
        if current_tweet:
            tweets.append(current_tweet.strip())
        
        # Agregar numeración si hay múltiples tweets
        if len(tweets) > 1:
            numbered_tweets = []
            for i, tweet in enumerate(tweets, 1):
                thread_marker = f"{i}/{len(tweets)} "
                if len(tweet) + len(thread_marker) <= max_length:
                    numbered_tweets.append(thread_marker + tweet)
                else:
                    # Truncar tweet para hacer espacio
                    available_space = max_length - len(thread_marker) - 3
                    numbered_tweets.append(thread_marker + tweet[:available_space] + "...")
            return numbered_tweets
        
        return tweets

