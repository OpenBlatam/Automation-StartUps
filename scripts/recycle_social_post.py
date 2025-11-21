#!/usr/bin/env python3
"""
Script mejorado para reciclar publicaciones antiguas de redes sociales
Genera 3 versiones: post estático, video corto e historia
Con análisis inteligente, múltiples variaciones y opción de IA
"""

import json
import sys
import os
import re
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from collections import Counter
from pathlib import Path

# Intentar importar OpenAI (opcional)
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class SocialPostRecycler:
    """Clase mejorada para reciclar y transformar publicaciones antiguas"""
    
    # Templates de hooks variados
    HOOKS = {
        'question': [
            "¿Sabías que...?",
            "¿Te has preguntado alguna vez...?",
            "Pregunta rápida: ¿Qué opinas de...?",
            "¿Alguna vez te has dado cuenta de que...?"
        ],
        'storytelling': [
            "Te cuento algo que aprendí...",
            "Hace tiempo descubrí que...",
            "Una lección importante que quiero compartir...",
            "Déjame contarte algo..."
        ],
        'fact': [
            "Dato curioso:",
            "¿Sabías que...?",
            "Aquí tienes un dato interesante:",
            "Esto te va a sorprender:"
        ],
        'reflection': [
            "Reflexionando sobre esto...",
            "Esto me hizo pensar...",
            "Algo que siempre recuerdo...",
            "Una reflexión que quiero compartir..."
        ]
    }
    
    # CTAs variados
    CTAS = [
        "¿Qué opinas? Comenta 👇",
        "¿Has vivido algo similar? Cuéntame ⬇️",
        "Comparte tu experiencia en los comentarios 👇",
        "¿Qué te parece? Déjame saber tu opinión 👇",
        "¿Estás de acuerdo? Hablemos en los comentarios 👇",
        "¿Qué agregarías tú? Comparte tus ideas ⬇️"
    ]
    
    # Hashtags por categoría
    HASHTAG_CATEGORIES = {
        'productividad': ['#Productividad', '#Eficiencia', '#Organizacion', '#GestionDelTiempo'],
        'tecnologia': ['#Tecnologia', '#Innovacion', '#Digital', '#Tech'],
        'negocios': ['#Negocios', '#Emprendimiento', '#Marketing', '#Empresas'],
        'educacion': ['#Educacion', '#Aprendizaje', '#Conocimiento', '#Desarrollo'],
        'motivacion': ['#Motivacion', '#Inspiracion', '#Exito', '#Crecimiento'],
        'ia': ['#IA', '#InteligenciaArtificial', '#AI', '#MachineLearning'],
        'automatizacion': ['#Automatizacion', '#AutomatizacionEmpresarial', '#Workflow', '#Procesos']
    }
    
    def __init__(self, original_post: str, use_ai: bool = False, openai_api_key: Optional[str] = None):
        self.original_post = original_post
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.use_ai = use_ai and OPENAI_AVAILABLE
        self.openai_client = None
        
        if self.use_ai:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
            else:
                print("⚠️  OpenAI API key no encontrada. Usando modo sin IA.")
                self.use_ai = False
    
    def extract_key_elements(self) -> Dict[str, any]:
        """Extrae elementos clave de la publicación original con análisis mejorado"""
        # Detectar hashtags existentes
        hashtags = [word for word in self.original_post.split() if word.startswith('#')]
        
        # Detectar menciones
        mentions = [word for word in self.original_post.split() if word.startswith('@')]
        
        # Detectar URLs
        urls = [word for word in self.original_post.split() if word.startswith('http')]
        
        # Texto limpio sin hashtags, menciones ni URLs
        clean_text = ' '.join([
            word for word in self.original_post.split() 
            if not (word.startswith('#') or word.startswith('@') or word.startswith('http'))
        ])
        
        # Análisis mejorado del contenido
        word_count = len(clean_text.split())
        char_count = len(clean_text)
        
        # Detectar tipo de contenido
        content_type = self._detect_content_type(clean_text)
        
        # Detectar tono/sentimiento básico
        tone = self._detect_tone(clean_text)
        
        # Detectar tema principal
        main_topic = self._detect_main_topic(clean_text)
        
        # Detectar palabras clave
        keywords = self._extract_keywords(clean_text)
        
        # Análisis de estructura
        has_question = '?' in self.original_post
        has_exclamation = '!' in self.original_post
        has_emoji = any(ord(char) > 127 for char in self.original_post)
        has_numbers = bool(re.search(r'\d+', self.original_post))
        
        return {
            'hashtags': hashtags,
            'mentions': mentions,
            'urls': urls,
            'clean_text': clean_text,
            'word_count': word_count,
            'char_count': char_count,
            'content_type': content_type,
            'tone': tone,
            'main_topic': main_topic,
            'keywords': keywords,
            'has_question': has_question,
            'has_exclamation': has_exclamation,
            'has_emoji': has_emoji,
            'has_numbers': has_numbers
        }
    
    def _detect_content_type(self, text: str) -> str:
        """Detecta el tipo de contenido"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['cómo', 'como', 'paso', 'guía', 'tutorial']):
            return 'tutorial'
        elif any(word in text_lower for word in ['tip', 'consejo', 'recomendación', 'sugerencia']):
            return 'tip'
        elif any(word in text_lower for word in ['dato', 'estadística', 'número', 'porcentaje']):
            return 'fact'
        elif any(word in text_lower for word in ['opinión', 'pienso', 'creo', 'considero']):
            return 'opinion'
        elif '?' in text:
            return 'question'
        else:
            return 'general'
    
    def _detect_tone(self, text: str) -> str:
        """Detecta el tono del contenido"""
        text_lower = text.lower()
        
        positive_words = ['excelente', 'genial', 'increíble', 'fantástico', 'mejor', 'éxito', 'logro']
        negative_words = ['problema', 'error', 'fallo', 'difícil', 'complicado', 'desafío']
        question_words = ['qué', 'cómo', 'cuándo', 'dónde', 'por qué', 'cuál']
        
        if any(word in text_lower for word in positive_words):
            return 'positive'
        elif any(word in text_lower for word in negative_words):
            return 'analytical'
        elif any(word in text_lower for word in question_words):
            return 'curious'
        else:
            return 'neutral'
    
    def _detect_main_topic(self, text: str) -> str:
        """Detecta el tema principal"""
        text_lower = text.lower()
        
        topic_keywords = {
            'productividad': ['productividad', 'eficiencia', 'tiempo', 'organización'],
            'tecnologia': ['tecnología', 'tecnologia', 'digital', 'software', 'app'],
            'negocios': ['negocio', 'empresa', 'emprendimiento', 'marketing', 'ventas'],
            'educacion': ['aprender', 'educación', 'educacion', 'conocimiento', 'curso'],
            'ia': ['ia', 'inteligencia artificial', 'ai', 'machine learning', 'chatgpt'],
            'automatizacion': ['automatización', 'automatizacion', 'automatizar', 'workflow']
        }
        
        for topic, keywords in topic_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                return topic
        
        return 'general'
    
    def _extract_keywords(self, text: str, top_n: int = 5) -> List[str]:
        """Extrae palabras clave del texto"""
        # Remover palabras comunes (stop words básicas en español)
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'más', 'pero', 'sus', 'le', 'ha', 'me', 'si', 'sin', 'sobre', 'este', 'ya', 'entre', 'cuando', 'todo', 'esta', 'ser', 'son', 'dos', 'también', 'fue', 'había', 'era', 'muy', 'años', 'hasta', 'desde', 'está', 'mi', 'porque', 'qué', 'sólo', 'han', 'yo', 'hay', 'vez', 'puede', 'todos', 'así', 'nos', 'ni', 'parte', 'tiene', 'él', 'uno', 'donde', 'bien', 'tiempo', 'mismo', 'ese', 'ahora', 'cada', 'e', 'vida', 'otro', 'después', 'te', 'otros', 'aunque', 'esa', 'esos', 'estas', 'estos', 'otra', 'otras', 'otros', 'otro'}
        
        words = re.findall(r'\b\w+\b', text.lower())
        words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Contar frecuencia
        word_freq = Counter(words)
        return [word for word, _ in word_freq.most_common(top_n)]
    
    def generate_static_post(self, elements: Dict) -> Dict:
        """Genera versión mejorada de post estático con múltiples variaciones"""
        
        # Seleccionar hook apropiado según tipo de contenido
        hook_type = 'question' if elements['has_question'] else elements['content_type']
        if hook_type not in self.HOOKS:
            hook_type = 'reflection'
        
        hooks = self.HOOKS[hook_type]
        selected_hook = hooks[0]
        
        # Generar múltiples variaciones de caption
        captions = []
        
        # Variación 1: Enfoque en reciclaje/throwback
        if elements['word_count'] > 100:
            caption1 = f"""🔄 **{selected_hook}**

{elements['clean_text'][:200]}...

💡 **¿Qué ha cambiado desde entonces?**
Comparte tu experiencia en los comentarios 👇"""
        else:
            caption1 = f"""✨ **{selected_hook}**

{elements['clean_text']}

💭 Reflexión: ¿Cómo aplicas esto hoy en día?

Comparte tu opinión ⬇️"""
        captions.append(caption1)
        
        # Variación 2: Enfoque en valor/educación
        if elements['content_type'] == 'tip':
            caption2 = f"""💡 **Tip del día:**

{elements['clean_text'][:180] if elements['word_count'] > 50 else elements['clean_text']}

📌 Guarda este post para no perderlo
💬 ¿Qué tip agregarías tú?"""
        else:
            caption2 = f"""📚 **Contenido de valor:**

{elements['clean_text'][:180] if elements['word_count'] > 50 else elements['clean_text']}

💬 ¿Qué opinas de esto?
👇 Comparte tu perspectiva"""
        captions.append(caption2)
        
        # Variación 3: Enfoque conversacional
        caption3 = f"""👋 Hola! 

{elements['clean_text'][:150] if elements['word_count'] > 50 else elements['clean_text']}

🤔 ¿Has experimentado algo similar?
Cuéntame en los comentarios 👇"""
        captions.append(caption3)
        
        # Generar hashtags inteligentes
        hashtags = self._generate_smart_hashtags(elements)
        
        # Sugerencias de visuales mejoradas según tema
        visual_suggestions = self._generate_visual_suggestions(elements)
        
        # Mejor momento para publicar según tipo de contenido
        best_time = self._get_best_posting_time(elements)
        
        return {
            'type': 'Post Estático',
            'platform': 'Instagram Feed / LinkedIn',
            'captions': captions,  # Múltiples variaciones
            'recommended_caption': captions[0],  # Recomendada por defecto
            'hashtags': ' '.join(hashtags[:12]),
            'hashtag_list': hashtags[:12],
            'visual_suggestions': visual_suggestions,
            'best_posting_time': best_time,
            'content_analysis': {
                'type': elements['content_type'],
                'tone': elements['tone'],
                'topic': elements['main_topic'],
                'keywords': elements['keywords']
            },
            'best_practices': [
                "Usa una imagen de alta calidad (1080x1080px para Instagram, 1200x627px para LinkedIn)",
                "Incluye texto legible en la imagen para mejor engagement (máx. 20% del área)",
                f"Publica en {best_time} para máximo alcance según tu audiencia",
                "Responde a los primeros 5-10 comentarios rápidamente (primeras 2 horas)",
                "Usa emojis estratégicamente (2-3 por caption)",
                "Incluye un CTA claro y específico"
            ]
        }
    
    def generate_short_video(self, elements: Dict) -> Dict:
        """Genera versión mejorada de video corto con múltiples scripts"""
        
        # Seleccionar hook apropiado
        hook_type = 'question' if elements['has_question'] else elements['content_type']
        if hook_type not in self.HOOKS:
            hook_type = 'storytelling'
        
        hooks = self.HOOKS[hook_type]
        selected_hook = hooks[0]
        
        # Calcular duración estimada (150 palabras/minuto promedio)
        estimated_duration = max(15, min(60, int(elements['word_count'] * 0.4)))
        
        # Generar múltiples scripts
        scripts = []
        
        # Script 1: Directo y conciso
        if elements['word_count'] > 50:
            main_content = elements['clean_text'][:120] + "..."
        else:
            main_content = elements['clean_text']
        
        script1 = f"""{selected_hook}

{main_content}

{self.CTAS[0]}"""
        scripts.append(script1)
        
        # Script 2: Con storytelling
        script2 = f"""Te cuento algo que aprendí...

{main_content}

¿Has experimentado esto también? Cuéntame ⬇️"""
        scripts.append(script2)
        
        # Script 3: Con pregunta de apertura
        script3 = f"""¿Sabías que...?

{main_content}

¿Qué opinas? Déjame saber en los comentarios 👇"""
        scripts.append(script3)
        
        # Captions para videos
        captions = []
        for i, script in enumerate(scripts, 1):
            caption = f"""🎬 {script}

#VideoCorto #Contenido #Educacion #Aprendizaje"""
            captions.append(caption)
        
        # Hashtags para video
        hashtags = ['#VideoCorto', '#Contenido', '#Educacion', '#Aprendizaje']
        
        # Agregar hashtags según tema
        if elements['main_topic'] in self.HASHTAG_CATEGORIES:
            hashtags.extend(self.HASHTAG_CATEGORIES[elements['main_topic']][:3])
        
        hashtags.extend(['#Tips', '#Consejos', '#Motivacion', '#Viral', '#Trending'])
        
        if elements['hashtags']:
            hashtags.extend(elements['hashtags'][:4])
        
        # Sugerencias de visuales mejoradas
        video_suggestions = self._generate_video_visual_suggestions(elements)
        
        # Sugerencias de música según tono
        music_suggestions = self._get_music_suggestions(elements['tone'])
        
        # Mejor momento para publicar videos
        best_time = "6am-10am o 7pm-10pm" if elements['tone'] == 'positive' else "8am-12pm o 6pm-9pm"
        
        return {
            'type': 'Video Corto',
            'platform': 'Instagram Reels / TikTok / YouTube Shorts',
            'duration': f'{estimated_duration} segundos (estimado)',
            'scripts': scripts,  # Múltiples variaciones
            'recommended_script': scripts[0],
            'captions': captions,
            'recommended_caption': captions[0],
            'hashtags': ' '.join(hashtags[:12]),
            'hashtag_list': hashtags[:12],
            'visual_suggestions': video_suggestions,
            'music_suggestions': music_suggestions,
            'best_posting_time': best_time,
            'content_analysis': {
                'type': elements['content_type'],
                'tone': elements['tone'],
                'topic': elements['main_topic']
            },
            'best_practices': [
                f"Mantén el hook en los primeros {2 if estimated_duration < 30 else 3} segundos",
                "Usa subtítulos grandes y legibles (fuente mínima 48px)",
                f"Añade música {music_suggestions[0] if music_suggestions else 'trending'} pero que no compita con el audio",
                "Incluye CTA visual (texto animado) además del caption",
                f"Publica en {best_time} para máximo alcance",
                "Usa transiciones rápidas (cada 2-3 segundos) para mantener atención",
                "Añade efectos visuales sutiles (zoom, pan) para dinamismo"
            ]
        }
    
    def _generate_smart_hashtags(self, elements: Dict) -> List[str]:
        """Genera hashtags inteligentes basados en el análisis del contenido"""
        hashtags = []
        
        # Hashtags base según tipo de contenido
        base_hashtags = {
            'tutorial': ['#Tutorial', '#Aprende', '#ComoHacer'],
            'tip': ['#Tip', '#Consejo', '#SabiasQue'],
            'fact': ['#DatoCurioso', '#SabiasQue', '#Informacion'],
            'opinion': ['#Opinion', '#Reflexion', '#Pensamiento'],
            'question': ['#Pregunta', '#Debate', '#Discusion']
        }
        
        if elements['content_type'] in base_hashtags:
            hashtags.extend(base_hashtags[elements['content_type']])
        
        # Hashtags según tema principal
        if elements['main_topic'] in self.HASHTAG_CATEGORIES:
            hashtags.extend(self.HASHTAG_CATEGORIES[elements['main_topic']])
        
        # Hashtags según tono
        if elements['tone'] == 'positive':
            hashtags.extend(['#Motivacion', '#Inspiracion', '#Exito'])
        elif elements['tone'] == 'curious':
            hashtags.extend(['#Curiosidad', '#Aprendizaje', '#Descubrimiento'])
        
        # Hashtags genéricos
        hashtags.extend(['#ContenidoDeValor', '#Sabiduria', '#Aprendizaje'])
        
        # Agregar hashtags originales
        if elements['hashtags']:
            hashtags.extend(elements['hashtags'])
        
        # Remover duplicados manteniendo orden
        seen = set()
        unique_hashtags = []
        for tag in hashtags:
            tag_lower = tag.lower()
            if tag_lower not in seen:
                seen.add(tag_lower)
                unique_hashtags.append(tag)
        
        return unique_hashtags
    
    def _generate_visual_suggestions(self, elements: Dict) -> List[str]:
        """Genera sugerencias de visuales específicas según el contenido"""
        suggestions = []
        
        topic = elements['main_topic']
        content_type = elements['content_type']
        
        # Sugerencias según tema
        topic_suggestions = {
            'productividad': [
                "📊 Gráfico de barras mostrando ahorro de tiempo",
                "⏰ Reloj o cronómetro como elemento visual principal",
                "📈 Infografía con estadísticas de productividad"
            ],
            'tecnologia': [
                "💻 Screenshot de interfaz o código relevante",
                "🔧 Iconos de herramientas tecnológicas",
                "🌐 Visualización de conceptos digitales"
            ],
            'negocios': [
                "📈 Gráficos de crecimiento o métricas",
                "💼 Imágenes profesionales de oficina/equipo",
                "📊 Dashboard o KPIs visuales"
            ],
            'ia': [
                "🤖 Ilustración de IA o robots",
                "🧠 Cerebro o red neuronal como visual",
                "💡 Bombilla con símbolos de tecnología"
            ],
            'automatizacion': [
                "⚙️ Iconos de engranajes o procesos",
                "🔄 Diagrama de flujo o workflow",
                "📱 Screenshot de herramientas de automatización"
            ]
        }
        
        if topic in topic_suggestions:
            suggestions.extend(topic_suggestions[topic][:2])
        
        # Sugerencias según tipo de contenido
        if content_type == 'tip':
            suggestions.append("💡 Diseño tipo tarjeta con tip destacado")
        elif content_type == 'tutorial':
            suggestions.append("📝 Screenshot paso a paso del proceso")
        elif content_type == 'fact':
            suggestions.append("📊 Infografía con el dato destacado")
        
        # Sugerencias genéricas
        suggestions.extend([
            "🎨 Diseño tipo quote con tipografía moderna y fondo degradado",
            "📸 Screenshot de la publicación original con overlay moderno",
            "✨ Collage de imágenes relacionadas con el contenido"
        ])
        
        return suggestions[:5]
    
    def _generate_video_visual_suggestions(self, elements: Dict) -> List[str]:
        """Genera sugerencias específicas para videos"""
        suggestions = []
        
        topic = elements['main_topic']
        content_type = elements['content_type']
        
        if content_type == 'tutorial':
            suggestions.extend([
                "📱 Screen recording mostrando el proceso paso a paso",
                "🎬 B-roll de herramientas/recursos mencionados"
            ])
        elif content_type == 'tip':
            suggestions.extend([
                "💡 Video tipo talking head con el tip como subtítulos",
                "📊 Gráficos animados ilustrando el consejo"
            ])
        else:
            suggestions.extend([
                "🎥 Video tipo talking head con el texto como subtítulos",
                "📱 Screen recording mostrando la publicación original + narración"
            ])
        
        # Sugerencias según tema
        if topic == 'productividad':
            suggestions.append("⏱️ Time-lapse de trabajo/productividad")
        elif topic == 'tecnologia':
            suggestions.append("💻 Screen recording de software/herramientas")
        
        # Sugerencias genéricas
        suggestions.extend([
            "✂️ Video con transiciones rápidas y texto animado",
            "🎬 B-roll relacionado con el tema + voz en off",
            "📊 Video con gráficos animados y texto superpuesto"
        ])
        
        return suggestions[:5]
    
    def _get_music_suggestions(self, tone: str) -> List[str]:
        """Sugiere tipos de música según el tono del contenido"""
        music_map = {
            'positive': ['upbeat y energética', 'motivacional', 'inspiracional'],
            'curious': ['misteriosa pero ligera', 'intrigante', 'ambiental'],
            'analytical': ['profesional y suave', 'corporativa', 'ambiental'],
            'neutral': ['neutral y profesional', 'suave de fondo', 'ambiental']
        }
        
        return music_map.get(tone, ['trending', 'popular'])
    
    def _get_best_posting_time(self, elements: Dict) -> str:
        """Determina el mejor momento para publicar según el contenido"""
        topic = elements['main_topic']
        content_type = elements['content_type']
        
        # Horarios optimizados según tema y tipo
        time_map = {
            'productividad': '7am-9am (inicio de jornada) o 6pm-8pm (fin de jornada)',
            'negocios': '8am-10am o 5pm-7pm (horarios laborales)',
            'educacion': '9am-11am o 7pm-9pm (horarios de estudio)',
            'motivacion': '6am-8am (inicio del día) o 8pm-10pm (reflexión nocturna)',
            'tecnologia': '10am-12pm o 7pm-9pm (horarios de consumo tech)',
            'general': '9am-11am o 7pm-9pm (horarios generales de mayor engagement)'
        }
        
        return time_map.get(topic, time_map['general'])
    
    def generate_story(self, elements: Dict) -> Dict:
        """Genera versión mejorada de historia con slides optimizados"""
        
        # Dividir contenido inteligentemente
        text_chunks = [chunk.strip() for chunk in elements['clean_text'].split('. ') if chunk.strip()]
        
        slides = []
        
        # Slide 1: Hook mejorado según tipo de contenido
        hook_content = '🔄 Recordando esto...'
        if elements['has_question']:
            hook_content = '❓ Pregunta rápida...'
        elif elements['content_type'] == 'tip':
            hook_content = '💡 Tip del día:'
        elif elements['content_type'] == 'fact':
            hook_content = '📊 Dato interesante:'
        
        slides.append({
            'number': 1,
            'type': 'Hook',
            'content': hook_content,
            'visual': 'Fondo sólido vibrante + emoji grande + texto bold',
            'duration': '3 segundos',
            'interactive': 'Ninguno'
        })
        
        # Slides de contenido (máximo 4 slides de contenido)
        max_content_slides = min(4, len(text_chunks))
        for i, chunk in enumerate(text_chunks[:max_content_slides], start=2):
            content = chunk[:90] + ('...' if len(chunk) > 90 else '')
            
            # Determinar tipo de slide según posición
            slide_type = 'Content'
            if i == 2:
                slide_type = 'Main Content'
            
            # Sugerir sticker interactivo en slide intermedio
            interactive = None
            if i == 3 and elements['has_question']:
                interactive = 'Sticker de pregunta'
            elif i == 3:
                interactive = 'Sticker de encuesta (Sí/No)'
            
            slides.append({
                'number': i,
                'type': slide_type,
                'content': content,
                'visual': self._get_story_visual_suggestion(elements, i),
                'duration': '4-5 segundos',
                'interactive': interactive or 'Ninguno'
            })
        
        # Slide final: CTA mejorado
        cta_options = [
            '¿Qué opinas? 👇 Desliza para responder',
            '¿Estás de acuerdo? Responde 👇',
            '¿Qué agregarías? Comparte 👇',
            'Guarda esta historia 💾'
        ]
        
        selected_cta = cta_options[0]
        if elements['has_question']:
            selected_cta = cta_options[0]
        elif elements['content_type'] == 'tip':
            selected_cta = cta_options[3]
        
        slides.append({
            'number': len(slides) + 1,
            'type': 'CTA',
            'content': selected_cta,
            'visual': 'Fondo llamativo + CTA destacado con emoji + botón visual',
            'duration': '3-4 segundos',
            'interactive': 'Sticker de pregunta o encuesta'
        })
        
        # Asegurar máximo 7 slides totales
        if len(slides) > 7:
            slides = slides[:6] + [slides[-1]]  # Mantener hook, primeros 5 de contenido, y CTA
        
        # Hashtags para historia
        hashtags = ['#Stories', '#Contenido']
        
        # Agregar hashtags según tema
        if elements['main_topic'] in self.HASHTAG_CATEGORIES:
            hashtags.extend(self.HASHTAG_CATEGORIES[elements['main_topic']][:2])
        
        hashtags.extend(['#Tips', '#Sabiduria', '#Aprendizaje'])
        
        if elements['hashtags']:
            hashtags.extend(elements['hashtags'][:2])
        
        # Sugerencias de visuales mejoradas
        visual_suggestions = self._get_story_visual_suggestions(elements)
        
        return {
            'type': 'Historia',
            'platform': 'Instagram Stories / Facebook Stories',
            'slides': slides,
            'total_slides': len(slides),
            'hashtags': ' '.join(hashtags[:8]),
            'hashtag_list': hashtags[:8],
            'visual_suggestions': visual_suggestions,
            'best_posting_time': '8am-12pm o 6pm-10pm',
            'content_analysis': {
                'type': elements['content_type'],
                'tone': elements['tone'],
                'topic': elements['main_topic']
            },
            'best_practices': [
                f"Mantén cada slide visible por 3-5 segundos (total: ~{len(slides) * 4} segundos)",
                f"Usa máximo {len(slides)} slides para mantener engagement",
                "Añade stickers interactivos en slides intermedios (encuestas, preguntas, quizzes)",
                "Usa la función de highlights para guardar historias importantes",
                "Publica entre 8am-12pm o 6pm-10pm para máximo alcance",
                "Considera usar la función de 'En vivo' para engagement en tiempo real",
                "Usa GIFs relacionados con el tema para dinamismo",
                "Asegúrate de que el texto sea legible (fuente mínima 24px)"
            ]
        }
    
    def _get_story_visual_suggestion(self, elements: Dict, slide_number: int) -> str:
        """Genera sugerencia visual específica para cada slide de historia"""
        topic = elements['main_topic']
        
        visual_map = {
            2: 'Fondo degradado relacionado con el tema + texto destacado',
            3: 'Imagen relacionada con el contenido + texto superpuesto',
            4: 'Fondo sólido complementario + texto legible',
            5: 'Visual tipo quote con tipografía moderna'
        }
        
        base_visual = visual_map.get(slide_number, 'Texto sobre fondo degradado o imagen relacionada')
        
        # Personalizar según tema
        if topic == 'productividad':
            return f'{base_visual} (considera añadir iconos de tiempo/productividad)'
        elif topic == 'tecnologia':
            return f'{base_visual} (considera añadir elementos tech/digitales)'
        
        return base_visual
    
    def _get_story_visual_suggestions(self, elements: Dict) -> List[str]:
        """Genera sugerencias generales de visuales para historias"""
        suggestions = [
            "📱 Slide 1: Fondo sólido vibrante + emoji grande + texto bold",
            "🎨 Slides de contenido: Fondo degradado o imagen relacionada + texto legible",
            "✨ Slide final: Fondo llamativo + CTA destacado con emoji"
        ]
        
        if elements['main_topic'] == 'productividad':
            suggestions.append("⏰ Considera usar iconos de tiempo/reloj como elementos visuales")
        elif elements['main_topic'] == 'tecnologia':
            suggestions.append("💻 Considera screenshots o iconos tecnológicos")
        
        suggestions.extend([
            "🎭 Usa stickers interactivos (encuestas, preguntas, quizzes) en slides intermedios",
            "📊 Considera añadir GIFs relacionados con el tema para dinamismo",
            "🎨 Usa colores contrastantes para mejor legibilidad"
        ])
        
        return suggestions
    
    def generate_image_prompts(self, elements: Dict) -> List[Dict]:
        """Genera prompts para crear imágenes con IA según el contenido"""
        prompts = []
        topic = elements['main_topic']
        content_type = elements['content_type']
        
        # Prompts según tema
        topic_prompts = {
            'productividad': [
                "Modern minimalist workspace with productivity tools, clean desk, organized calendar, professional lighting, high quality",
                "Infographic style illustration showing time management concepts, colorful, modern design, professional",
                "Abstract representation of efficiency and productivity, geometric shapes, vibrant colors, modern art style"
            ],
            'tecnologia': [
                "Futuristic tech workspace with digital elements, holographic displays, modern technology, cyberpunk aesthetic, high quality",
                "Abstract technology visualization with neural networks, data streams, digital particles, modern design",
                "Clean tech product photography, minimalist, professional lighting, modern aesthetic, high resolution"
            ],
            'negocios': [
                "Professional business meeting scene, modern office, diverse team collaborating, professional photography style",
                "Business growth chart visualization, modern infographic style, professional colors, clean design",
                "Corporate success concept, handshake, growth arrows, professional business illustration, high quality"
            ],
            'ia': [
                "AI and machine learning concept art, neural networks, digital brain, futuristic, high tech aesthetic",
                "Abstract representation of artificial intelligence, glowing circuits, data visualization, modern art",
                "Robot and human collaboration scene, futuristic workspace, professional illustration, high quality"
            ],
            'automatizacion': [
                "Automation workflow visualization, gears and processes, modern infographic, professional design",
                "Abstract automation concept, interconnected systems, modern minimalist design, high quality",
                "Productivity automation tools arranged artistically, clean workspace, professional photography"
            ]
        }
        
        base_prompts = topic_prompts.get(topic, [
            "Modern social media post design, clean layout, professional typography, engaging visual",
            "Abstract social media content visualization, colorful, modern design, high quality",
            "Professional content creation workspace, modern aesthetic, clean design"
        ])
        
        for i, prompt in enumerate(base_prompts[:3], 1):
            prompts.append({
                'number': i,
                'prompt': prompt,
                'style': 'professional',
                'use_case': f'Para {content_type} sobre {topic}',
                'suggested_tools': ['DALL-E', 'Midjourney', 'Stable Diffusion', 'Canva AI']
            })
        
        return prompts
    
    def estimate_engagement(self, elements: Dict, version_type: str, historical_data: Optional[Dict] = None) -> Dict:
        """Estima métricas de engagement potencial mejorado con datos históricos"""
        base_score = 50  # Score base
        
        # Factores que aumentan engagement
        factors = {
            'has_question': 15,
            'has_numbers': 10,
            'has_emoji': 5,
            'content_type_tip': 20,
            'content_type_tutorial': 15,
            'tone_positive': 10,
            'word_count_optimal': 10  # 50-150 palabras es óptimo
        }
        
        score = base_score
        
        if elements['has_question']:
            score += factors['has_question']
        if elements['has_numbers']:
            score += factors['has_numbers']
        if elements['has_emoji']:
            score += factors['has_emoji']
        if elements['content_type'] == 'tip':
            score += factors['content_type_tip']
        elif elements['content_type'] == 'tutorial':
            score += factors['content_type_tutorial']
        if elements['tone'] == 'positive':
            score += factors['tone_positive']
        if 50 <= elements['word_count'] <= 150:
            score += factors['word_count_optimal']
        
        # Ajustar según tipo de versión
        version_multipliers = {
            'static_post': 1.0,
            'short_video': 1.3,  # Videos tienen más engagement
            'story': 0.9  # Stories tienen menos engagement pero más interacción
        }
        
        score = int(score * version_multipliers.get(version_type, 1.0))
        
        # Ajustar con datos históricos si están disponibles
        if historical_data:
            # Ajustar score basado en engagement histórico del tema
            topic_avg_score = historical_data.get('topic_avg_engagement', 0)
            if topic_avg_score > 0:
                # Promediar con datos históricos (70% estimación, 30% histórico)
                score = int(score * 0.7 + topic_avg_score * 0.3)
            
            # Ajustar según hashtags efectivos históricos
            effective_hashtags = historical_data.get('effective_hashtags', [])
            if effective_hashtags:
                matching_hashtags = [h for h in elements.get('hashtags', []) 
                                   if any(eh.lower() in h.lower() for eh in effective_hashtags)]
                if matching_hashtags:
                    score += min(10, len(matching_hashtags) * 2)
        
        score = min(100, max(0, score))  # Limitar entre 0-100
        
        # Estimar métricas específicas con mejor precisión
        # Usar datos históricos si están disponibles
        if historical_data and historical_data.get('avg_likes_per_score'):
            # Calcular basado en promedio histórico
            avg_likes_per_score = historical_data['avg_likes_per_score']
            estimated_likes = int(score * avg_likes_per_score)
        else:
            # Estimación por defecto mejorada
            estimated_likes = int(score * 12)  # Mejorado de 10 a 12
        
        if historical_data and historical_data.get('avg_comments_per_score'):
            avg_comments_per_score = historical_data['avg_comments_per_score']
            estimated_comments = int(score * avg_comments_per_score)
        else:
            estimated_comments = int(score * 1.8)  # Mejorado de 1.5 a 1.8
        
        if historical_data and historical_data.get('avg_shares_per_score'):
            avg_shares_per_score = historical_data['avg_shares_per_score']
            estimated_shares = int(score * avg_shares_per_score)
        else:
            estimated_shares = int(score * 0.6)  # Mejorado de 0.5 a 0.6
        
        # Calcular alcance estimado
        if historical_data and historical_data.get('avg_reach_multiplier'):
            estimated_reach = int(estimated_likes * historical_data['avg_reach_multiplier'])
        else:
            estimated_reach = estimated_likes * 3.5  # Mejorado de 3 a 3.5
        
        # Calcular confianza basada en disponibilidad de datos históricos
        if historical_data:
            confidence = 'high' if historical_data.get('data_points', 0) > 10 else 'medium'
        else:
            confidence = 'medium' if 40 <= score <= 70 else ('high' if score > 70 else 'low')
        
        return {
            'engagement_score': score,
            'estimated_likes': estimated_likes,
            'estimated_comments': estimated_comments,
            'estimated_shares': estimated_shares,
            'estimated_reach': estimated_reach,
            'confidence': confidence,
            'uses_historical_data': historical_data is not None,
            'historical_data_points': historical_data.get('data_points', 0) if historical_data else 0
        }
    
    def analyze_original_post_engagement(self, original_post: str) -> Optional[Dict]:
        """Analiza el engagement histórico de la publicación original si está disponible"""
        # Intentar importar el analizador de engagement
        try:
            from analisis_engagement_contenido import AnalizadorEngagement
            analyzer = AnalizadorEngagement()
            
            # Intentar cargar datos históricos
            try:
                analyzer.cargar_desde_bd(dias_atras=90)
            except:
                # Si no hay BD, generar datos de ejemplo para análisis
                analyzer.generar_datos_ejemplo(num_publicaciones=50)
            
            # Extraer elementos del contenido
            elements = self.extract_key_elements()
            topic = elements['main_topic']
            hashtags = elements['hashtags']
            
            # Usar el nuevo método mejorado del analizador
            historical_data = analyzer.get_historical_data_for_recycling(
                topic=topic,
                hashtags=hashtags,
                platform=None  # No filtrar por plataforma específica
            )
            
            return historical_data
            
        except ImportError:
            # Si no está disponible el módulo, retornar None
            pass
        except Exception as e:
            # En caso de error, continuar sin datos históricos
            print(f"⚠️  No se pudieron cargar datos históricos: {e}")
        
        return None
    
    def generate_related_content_suggestions(self, elements: Dict) -> List[Dict]:
        """Genera sugerencias de contenido relacionado"""
        suggestions = []
        topic = elements['main_topic']
        content_type = elements['content_type']
        
        related_topics = {
            'productividad': ['gestión del tiempo', 'organización', 'eficiencia', 'hábitos productivos'],
            'tecnologia': ['innovación', 'transformación digital', 'herramientas tech', 'futuro tech'],
            'negocios': ['estrategia', 'crecimiento', 'marketing', 'ventas', 'liderazgo'],
            'ia': ['machine learning', 'automatización', 'futuro del trabajo', 'innovación'],
            'automatizacion': ['eficiencia', 'productividad', 'procesos', 'optimización']
        }
        
        topics = related_topics.get(topic, ['contenido relacionado', 'temas complementarios'])
        
        for i, related_topic in enumerate(topics[:4], 1):
            suggestions.append({
                'number': i,
                'topic': related_topic,
                'content_ideas': [
                    f"5 formas de mejorar {related_topic}",
                    f"Guía completa de {related_topic}",
                    f"Errores comunes en {related_topic}",
                    f"Casos de éxito en {related_topic}"
                ],
                'format_suggestions': ['Post estático', 'Video corto', 'Carrusel', 'Historia']
            })
        
        return suggestions
    
    def generate_trending_hashtags(self, elements: Dict) -> List[str]:
        """Sugiere hashtags trending basados en el contenido"""
        trending = []
        topic = elements['main_topic']
        
        # Hashtags trending por tema (ejemplos)
        trending_map = {
            'productividad': ['#Productividad', '#Eficiencia', '#GestionDelTiempo', '#Organizacion', '#TipsProductivos'],
            'tecnologia': ['#Tech', '#Innovacion', '#Digital', '#Tecnologia', '#FuturoTech'],
            'negocios': ['#Negocios', '#Emprendimiento', '#Marketing', '#Exito', '#Empresas'],
            'ia': ['#IA', '#InteligenciaArtificial', '#AI', '#MachineLearning', '#FuturoIA'],
            'automatizacion': ['#Automatizacion', '#Workflow', '#Procesos', '#Eficiencia', '#Innovacion']
        }
        
        trending.extend(trending_map.get(topic, ['#Contenido', '#Tips', '#Aprendizaje']))
        
        # Agregar hashtags genéricos trending
        trending.extend(['#Viral', '#Trending', '#Popular', '#Top'])
        
        return trending[:10]
    
    def generate_all_versions(self, use_historical_data: bool = True) -> Dict:
        """Genera las 3 versiones recicladas con análisis completo"""
        elements = self.extract_key_elements()
        
        # Analizar engagement histórico si está disponible
        historical_data = None
        if use_historical_data:
            historical_data = self.analyze_original_post_engagement(self.original_post)
        
        static_post = self.generate_static_post(elements)
        short_video = self.generate_short_video(elements)
        story = self.generate_story(elements)
        
        # Agregar métricas de engagement mejoradas con datos históricos
        static_post['engagement_metrics'] = self.estimate_engagement(elements, 'static_post', historical_data)
        short_video['engagement_metrics'] = self.estimate_engagement(elements, 'short_video', historical_data)
        story['engagement_metrics'] = self.estimate_engagement(elements, 'story', historical_data)
        
        # Agregar prompts de imágenes
        static_post['image_prompts'] = self.generate_image_prompts(elements)
        
        # Agregar contenido relacionado
        related_content = self.generate_related_content_suggestions(elements)
        
        # Agregar hashtags trending
        trending_hashtags = self.generate_trending_hashtags(elements)
        
        return {
            'original_post': self.original_post,
            'timestamp': self.timestamp,
            'elements_extracted': elements,
            'versions': {
                'static_post': static_post,
                'short_video': short_video,
                'story': story
            },
            'related_content_suggestions': related_content,
            'trending_hashtags': trending_hashtags,
            'historical_analysis': {
                'available': historical_data is not None,
                'data_points': historical_data.get('data_points', 0) if historical_data else 0,
                'similar_posts_count': historical_data.get('similar_posts_count', 0) if historical_data else 0,
                'topic_avg_engagement': historical_data.get('topic_avg_engagement', 0) if historical_data else 0
            },
            'summary': {
                'best_version': self._determine_best_version(static_post, short_video, story),
                'recommended_action': self._get_recommended_action(elements)
            }
        }
    
    def _determine_best_version(self, static: Dict, video: Dict, story: Dict) -> str:
        """Determina la mejor versión basada en engagement"""
        scores = {
            'static_post': static['engagement_metrics']['engagement_score'],
            'short_video': video['engagement_metrics']['engagement_score'],
            'story': story['engagement_metrics']['engagement_score']
        }
        
        best = max(scores.items(), key=lambda x: x[1])
        return best[0]
    
    def _get_recommended_action(self, elements: Dict) -> str:
        """Genera recomendación de acción"""
        if elements['content_type'] == 'tip':
            return "Publica como video corto para máximo alcance y guardado"
        elif elements['content_type'] == 'tutorial':
            return "Considera crear un carrusel o video tutorial paso a paso"
        elif elements['has_question']:
            return "Usa historia con sticker de pregunta para mayor interacción"
        else:
            return "Post estático con imagen llamativa para mejor engagement"
    
    def export_to_markdown(self, result: Dict, output_file: str) -> None:
        """Exporta resultados a formato Markdown"""
        md_content = []
        md_content.append("# 🔄 Reciclaje de Publicación Social\n")
        md_content.append(f"**Fecha:** {result['timestamp']}\n")
        md_content.append(f"**Publicación Original:** {result['original_post']}\n")
        
        # Análisis
        elements = result['elements_extracted']
        md_content.append("\n## 🔍 Análisis del Contenido\n")
        md_content.append(f"- **Tipo:** {elements['content_type']}")
        md_content.append(f"- **Tono:** {elements['tone']}")
        md_content.append(f"- **Tema:** {elements['main_topic']}")
        md_content.append(f"- **Palabras clave:** {', '.join(elements['keywords'][:5])}\n")
        
        # Versiones
        for version_name, version_data in result['versions'].items():
            version_title = {
                'static_post': '📸 Post Estático',
                'short_video': '🎬 Video Corto',
                'story': '📱 Historia'
            }.get(version_name, version_name)
            
            md_content.append(f"\n## {version_title}\n")
            
            if 'captions' in version_data:
                md_content.append("### Captions\n")
                for i, caption in enumerate(version_data['captions'], 1):
                    md_content.append(f"#### Variación {i}\n")
                    md_content.append(f"{caption}\n")
            
            if 'scripts' in version_data:
                md_content.append("### Scripts\n")
                for i, script in enumerate(version_data['scripts'], 1):
                    md_content.append(f"#### Script {i}\n")
                    md_content.append(f"```\n{script}\n```\n")
            
            if 'engagement_metrics' in version_data:
                metrics = version_data['engagement_metrics']
                md_content.append("### Métricas de Engagement Estimadas\n")
                md_content.append(f"- **Score:** {metrics['engagement_score']}/100")
                md_content.append(f"- **Likes estimados:** {metrics['estimated_likes']}")
                md_content.append(f"- **Comentarios estimados:** {metrics['estimated_comments']}")
                md_content.append(f"- **Compartidos estimados:** {metrics['estimated_shares']}\n")
        
        # Contenido relacionado
        if 'related_content_suggestions' in result:
            md_content.append("\n## 💡 Sugerencias de Contenido Relacionado\n")
            for suggestion in result['related_content_suggestions']:
                md_content.append(f"### {suggestion['topic']}\n")
                for idea in suggestion['content_ideas']:
                    md_content.append(f"- {idea}\n")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
    
    def export_to_csv(self, result: Dict, output_file: str) -> None:
        """Exporta resultados a formato CSV"""
        rows = []
        
        # Encabezados
        headers = ['Versión', 'Tipo', 'Caption/Script', 'Hashtags', 'Engagement Score', 'Likes Estimados', 'Comentarios Estimados']
        
        for version_name, version_data in result['versions'].items():
            version_type = {
                'static_post': 'Post Estático',
                'short_video': 'Video Corto',
                'story': 'Historia'
            }.get(version_name, version_name)
            
            # Captions o scripts
            content_list = []
            if 'captions' in version_data:
                content_list = version_data['captions']
            elif 'scripts' in version_data:
                content_list = version_data['scripts']
            
            for i, content in enumerate(content_list, 1):
                metrics = version_data.get('engagement_metrics', {})
                row = [
                    f"{version_type} - Variación {i}",
                    version_type,
                    content[:100] + '...' if len(content) > 100 else content,
                    version_data.get('hashtags', ''),
                    metrics.get('engagement_score', 0),
                    metrics.get('estimated_likes', 0),
                    metrics.get('estimated_comments', 0)
                ]
                rows.append(row)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
    
    def format_output(self, result: Dict) -> str:
        """Formatea la salida de manera legible con análisis mejorado"""
        output = []
        output.append("=" * 80)
        output.append("🔄 RECICLAJE DE PUBLICACIÓN SOCIAL - VERSIÓN MEJORADA")
        output.append("=" * 80)
        output.append(f"\n📅 Fecha: {result['timestamp']}")
        output.append(f"\n📝 Publicación Original:")
        output.append(f"   {result['original_post']}")
        
        # Análisis del contenido
        elements = result['elements_extracted']
        output.append("\n" + "-" * 80)
        output.append("🔍 ANÁLISIS DEL CONTENIDO:")
        output.append("-" * 80)
        output.append(f"   📊 Tipo: {elements['content_type']}")
        output.append(f"   🎭 Tono: {elements['tone']}")
        output.append(f"   🏷️ Tema principal: {elements['main_topic']}")
        output.append(f"   📝 Palabras clave: {', '.join(elements['keywords'][:5])}")
        output.append(f"   📏 Longitud: {elements['word_count']} palabras, {elements['char_count']} caracteres")
        
        # Post Estático
        static = result['versions']['static_post']
        output.append(f"\n\n📸 A) POST ESTÁTICO ({static['platform']})")
        output.append("-" * 80)
        output.append(f"\n⏰ Mejor momento para publicar: {static['best_posting_time']}")
        output.append(f"\n📝 CAPTIONS (3 variaciones):")
        for i, caption in enumerate(static['captions'], 1):
            output.append(f"\n   Variación {i}:")
            output.append(f"   {caption}")
        output.append(f"\n⭐ RECOMENDADA (Variación 1):")
        output.append(f"   {static['recommended_caption']}")
        output.append(f"\n🏷️ HASHTAGS ({len(static['hashtag_list'])} hashtags):")
        output.append(f"   {static['hashtags']}")
        output.append(f"\n🎨 SUGERENCIAS DE CAPTURAS/VISUALES:")
        for i, suggestion in enumerate(static['visual_suggestions'], 1):
            output.append(f"   {i}. {suggestion}")
        output.append(f"\n💡 MEJORES PRÁCTICAS:")
        for i, practice in enumerate(static['best_practices'], 1):
            output.append(f"   {i}. {practice}")
        
        # Video Corto
        video = result['versions']['short_video']
        output.append(f"\n\n🎬 B) VIDEO CORTO ({video['platform']})")
        output.append("-" * 80)
        output.append(f"\n⏱️ Duración estimada: {video['duration']}")
        output.append(f"\n⏰ Mejor momento para publicar: {video['best_posting_time']}")
        output.append(f"\n📝 SCRIPTS (3 variaciones):")
        for i, script in enumerate(video['scripts'], 1):
            output.append(f"\n   Script {i}:")
            output.append(f"   {script}")
        output.append(f"\n⭐ RECOMENDADO (Script 1):")
        output.append(f"   {video['recommended_script']}")
        output.append(f"\n📝 CAPTIONS:")
        for i, caption in enumerate(video['captions'], 1):
            output.append(f"\n   Caption {i}:")
            output.append(f"   {caption[:150]}...")
        output.append(f"\n🏷️ HASHTAGS ({len(video['hashtag_list'])} hashtags):")
        output.append(f"   {video['hashtags']}")
        output.append(f"\n🎵 SUGERENCIAS DE MÚSICA:")
        for i, music in enumerate(video['music_suggestions'], 1):
            output.append(f"   {i}. {music}")
        output.append(f"\n🎨 SUGERENCIAS DE CAPTURAS/VISUALES:")
        for i, suggestion in enumerate(video['visual_suggestions'], 1):
            output.append(f"   {i}. {suggestion}")
        output.append(f"\n💡 MEJORES PRÁCTICAS:")
        for i, practice in enumerate(video['best_practices'], 1):
            output.append(f"   {i}. {practice}")
        
        # Historia
        story = result['versions']['story']
        output.append(f"\n\n📱 C) HISTORIA ({story['platform']})")
        output.append("-" * 80)
        output.append(f"\n📑 SLIDES ({story['total_slides']} slides):")
        for slide in story['slides']:
            output.append(f"\n   Slide {slide['number']} ({slide['type']}):")
            output.append(f"   📝 Contenido: {slide['content']}")
            output.append(f"   🎨 Visual: {slide['visual']}")
            output.append(f"   ⏱️ Duración: {slide['duration']}")
            if slide.get('interactive') and slide['interactive'] != 'Ninguno':
                output.append(f"   🎭 Interactivo: {slide['interactive']}")
        output.append(f"\n⏰ Mejor momento para publicar: {story['best_posting_time']}")
        output.append(f"\n🏷️ HASHTAGS ({len(story['hashtag_list'])} hashtags):")
        output.append(f"   {story['hashtags']}")
        output.append(f"\n🎨 SUGERENCIAS DE CAPTURAS/VISUALES:")
        for i, suggestion in enumerate(story['visual_suggestions'], 1):
            output.append(f"   {i}. {suggestion}")
        output.append(f"\n💡 MEJORES PRÁCTICAS:")
        for i, practice in enumerate(story['best_practices'], 1):
            output.append(f"   {i}. {practice}")
        
        # Métricas de engagement
        output.append("\n\n📊 MÉTRICAS DE ENGAGEMENT ESTIMADAS:")
        output.append("-" * 80)
        for version_name, version_data in result['versions'].items():
            version_title = {
                'static_post': '📸 Post Estático',
                'short_video': '🎬 Video Corto',
                'story': '📱 Historia'
            }.get(version_name, version_name)
            
            metrics = version_data.get('engagement_metrics', {})
            output.append(f"\n{version_title}:")
            output.append(f"   🎯 Score de Engagement: {metrics.get('engagement_score', 0)}/100")
            output.append(f"   👍 Likes estimados: {metrics.get('estimated_likes', 0)}")
            output.append(f"   💬 Comentarios estimados: {metrics.get('estimated_comments', 0)}")
            output.append(f"   🔄 Compartidos estimados: {metrics.get('estimated_shares', 0)}")
            output.append(f"   📈 Alcance estimado: {metrics.get('estimated_reach', 0)}")
            output.append(f"   ⚡ Confianza: {metrics.get('confidence', 'medium')}")
        
        # Prompts de imágenes
        static = result['versions']['static_post']
        if 'image_prompts' in static:
            output.append("\n\n🎨 PROMPTS PARA GENERAR IMÁGENES CON IA:")
            output.append("-" * 80)
            for prompt_data in static['image_prompts']:
                output.append(f"\n   Prompt {prompt_data['number']}:")
                output.append(f"   📝 {prompt_data['prompt']}")
                output.append(f"   🎯 Uso: {prompt_data['use_case']}")
                output.append(f"   🛠️ Herramientas sugeridas: {', '.join(prompt_data['suggested_tools'])}")
        
        # Contenido relacionado
        if 'related_content_suggestions' in result:
            output.append("\n\n💡 SUGERENCIAS DE CONTENIDO RELACIONADO:")
            output.append("-" * 80)
            for suggestion in result['related_content_suggestions']:
                output.append(f"\n   📌 {suggestion['topic']}:")
                for idea in suggestion['content_ideas']:
                    output.append(f"      • {idea}")
        
        # Hashtags trending
        if 'trending_hashtags' in result:
            output.append("\n\n🔥 HASHTAGS TRENDING:")
            output.append("-" * 80)
            output.append(f"   {' '.join(result['trending_hashtags'])}")
        
        # Análisis histórico
        if 'historical_analysis' in result:
            hist = result['historical_analysis']
            if hist['available']:
                output.append("\n\n📊 ANÁLISIS HISTÓRICO DE ENGAGEMENT:")
                output.append("-" * 80)
                output.append(f"   ✅ Datos históricos disponibles: {hist['data_points']} publicaciones similares")
                output.append(f"   📈 Engagement promedio del tema: {hist['topic_avg_engagement']:.1f}")
                output.append(f"   💡 Las estimaciones incluyen datos históricos para mayor precisión")
            else:
                output.append("\n\n📊 ANÁLISIS HISTÓRICO:")
                output.append("-" * 80)
                output.append(f"   ⚠️  No hay datos históricos disponibles. Usando estimaciones basadas en mejores prácticas.")
        
        # Resumen y recomendación
        if 'summary' in result:
            output.append("\n\n⭐ RESUMEN Y RECOMENDACIÓN:")
            output.append("-" * 80)
            best_version_name = result['summary']['best_version']
            best_version_title = {
                'static_post': 'Post Estático',
                'short_video': 'Video Corto',
                'story': 'Historia'
            }.get(best_version_name, best_version_name)
            output.append(f"   🏆 Mejor versión estimada: {best_version_title}")
            output.append(f"   💡 Recomendación: {result['summary']['recommended_action']}")
        
        output.append("\n" + "=" * 80)
        output.append("✨ ¡Listo para publicar! ✨")
        output.append("=" * 80)
        output.append("\n💡 TIPS:")
        output.append("   • Usa --use-ai para generar contenido aún más creativo con IA")
        output.append("   • Usa --format markdown o --format csv para exportar en otros formatos")
        output.append("   • Revisa los prompts de imágenes para crear visuales con IA")
        output.append("=" * 80)
        
        return "\n".join(output)


def main():
    """Función principal mejorada"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Recicla publicaciones antiguas de redes sociales y genera 3 versiones nuevas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python recycle_social_post.py "La automatización puede ahorrarte hasta 10 horas semanales. #Productividad #IA"
  python recycle_social_post.py "Tu publicación aquí" --use-ai
  python recycle_social_post.py "Tu publicación" --output resultado.json
        """
    )
    
    parser.add_argument('post', help='Texto de la publicación antigua a reciclar')
    parser.add_argument('--use-ai', action='store_true', 
                       help='Usar IA (OpenAI) para generar contenido más creativo (requiere OPENAI_API_KEY)')
    parser.add_argument('--output', '-o', 
                       help='Archivo de salida (por defecto: recycled_post_TIMESTAMP.json)')
    parser.add_argument('--format', '-f', choices=['json', 'markdown', 'csv', 'all'],
                       default='json',
                       help='Formato de exportación (json, markdown, csv, all)')
    parser.add_argument('--openai-key', 
                       help='API key de OpenAI (o usar variable de entorno OPENAI_API_KEY)')
    
    args = parser.parse_args()
    
    original_post = args.post
    
    # Crear recycler con opción de IA
    recycler = SocialPostRecycler(
        original_post, 
        use_ai=args.use_ai,
        openai_api_key=args.openai_key
    )
    
    if args.use_ai and not recycler.use_ai:
        print("⚠️  Advertencia: Modo IA solicitado pero no disponible. Usando modo estándar.")
    
    result = recycler.generate_all_versions()
    
    # Mostrar resultado formateado
    print(recycler.format_output(result))
    
    # Exportar según formato solicitado
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_name = args.output or f"recycled_post_{timestamp}"
    
    if args.format == 'all':
        # Exportar a todos los formatos
        json_file = f"{base_name}.json"
        md_file = f"{base_name}.md"
        csv_file = f"{base_name}.csv"
        
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        recycler.export_to_markdown(result, md_file)
        recycler.export_to_csv(result, csv_file)
        
        print(f"\n💾 Resultados exportados:")
        print(f"   📄 JSON: {json_file}")
        print(f"   📝 Markdown: {md_file}")
        print(f"   📊 CSV: {csv_file}")
    elif args.format == 'markdown':
        md_file = f"{base_name}.md" if not base_name.endswith('.md') else base_name
        recycler.export_to_markdown(result, md_file)
        print(f"\n💾 Resultado exportado a Markdown: {md_file}")
    elif args.format == 'csv':
        csv_file = f"{base_name}.csv" if not base_name.endswith('.csv') else base_name
        recycler.export_to_csv(result, csv_file)
        print(f"\n💾 Resultado exportado a CSV: {csv_file}")
    else:  # JSON por defecto
        json_file = f"{base_name}.json" if not base_name.endswith('.json') else base_name
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 Resultado guardado en JSON: {json_file}")


if __name__ == "__main__":
    main()

