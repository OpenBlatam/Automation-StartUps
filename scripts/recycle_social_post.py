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
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import Counter

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
        """Genera versión de historia reciclada"""
        
        # Dividir contenido en slides para historia
        text_chunks = elements['clean_text'].split('. ')
        slides = []
        
        # Slide 1: Hook
        slides.append({
            'number': 1,
            'type': 'Hook',
            'content': '🔄 Recordando esto...',
            'visual': 'Emoji grande + texto llamativo'
        })
        
        # Slides 2-4: Contenido principal
        for i, chunk in enumerate(text_chunks[:3], start=2):
            if chunk.strip():
                slides.append({
                    'number': i,
                    'type': 'Content',
                    'content': chunk[:100] + ('...' if len(chunk) > 100 else ''),
                    'visual': 'Texto sobre fondo degradado o imagen relacionada'
                })
        
        # Slide final: CTA
        slides.append({
            'number': len(slides) + 1,
            'type': 'CTA',
            'content': '¿Qué opinas? 👇 Desliza para responder',
            'visual': 'Botón de interacción o pregunta destacada'
        })
        
        # Caption para historia (opcional, ya que las historias no tienen caption tradicional)
        story_text = '\n'.join([f"Slide {s['number']}: {s['content']}" for s in slides])
        
        # Hashtags para historia
        hashtags = [
            '#Stories', '#Contenido', '#Tips', '#Sabiduria',
            '#Motivacion', '#Inspiracion', '#Aprendizaje'
        ]
        
        if elements['hashtags']:
            hashtags.extend(elements['hashtags'][:3])
        
        # Sugerencias de visuales para cada slide
        visual_suggestions = [
            "📱 Slide 1: Fondo sólido vibrante + texto grande y bold",
            "🎨 Slides 2-4: Fondo degradado o imagen relacionada + texto legible",
            "✨ Slide final: Fondo llamativo + CTA destacado con emoji",
            "🎭 Usa stickers interactivos (encuestas, preguntas, quizzes)",
            "📊 Considera añadir GIFs relacionados con el tema"
        ]
        
        return {
            'type': 'Historia',
            'platform': 'Instagram Stories / Facebook Stories',
            'slides': slides,
            'story_text': story_text,
            'hashtags': ' '.join(hashtags[:8]),
            'visual_suggestions': visual_suggestions,
            'best_practices': [
                "Mantén cada slide visible por 3-5 segundos",
                "Usa máximo 5-7 slides para no perder engagement",
                "Añade stickers interactivos (encuestas, preguntas) en slides intermedios",
                "Usa la función de highlights para guardar historias importantes",
                "Publica entre 8am-12pm o 6pm-10pm para máximo alcance",
                "Considera usar la función de 'En vivo' para engagement en tiempo real"
            ]
        }
    
    def generate_all_versions(self) -> Dict:
        """Genera las 3 versiones recicladas"""
        elements = self.extract_key_elements()
        
        return {
            'original_post': self.original_post,
            'timestamp': self.timestamp,
            'elements_extracted': elements,
            'versions': {
                'static_post': self.generate_static_post(elements),
                'short_video': self.generate_short_video(elements),
                'story': self.generate_story(elements)
            }
        }
    
    def format_output(self, result: Dict) -> str:
        """Formatea la salida de manera legible"""
        output = []
        output.append("=" * 80)
        output.append("🔄 RECICLAJE DE PUBLICACIÓN SOCIAL")
        output.append("=" * 80)
        output.append(f"\n📅 Fecha: {result['timestamp']}")
        output.append(f"\n📝 Publicación Original:")
        output.append(f"   {result['original_post']}")
        output.append("\n" + "-" * 80)
        
        # Post Estático
        static = result['versions']['static_post']
        output.append(f"\n📸 A) POST ESTÁTICO ({static['platform']})")
        output.append("-" * 80)
        output.append(f"\n📝 CAPTION:")
        output.append(f"{static['caption']}")
        output.append(f"\n🏷️ HASHTAGS:")
        output.append(f"{static['hashtags']}")
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
        output.append(f"\n⏱️ Duración: {video['duration']}")
        output.append(f"\n📝 SCRIPT:")
        output.append(f"{video['script']}")
        output.append(f"\n📝 CAPTION:")
        output.append(f"{video['caption']}")
        output.append(f"\n🏷️ HASHTAGS:")
        output.append(f"{video['hashtags']}")
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
        output.append(f"\n📑 SLIDES ({len(story['slides'])} slides):")
        for slide in story['slides']:
            output.append(f"\n   Slide {slide['number']} ({slide['type']}):")
            output.append(f"   📝 {slide['content']}")
            output.append(f"   🎨 {slide['visual']}")
        output.append(f"\n🏷️ HASHTAGS:")
        output.append(f"{story['hashtags']}")
        output.append(f"\n🎨 SUGERENCIAS DE CAPTURAS/VISUALES:")
        for i, suggestion in enumerate(story['visual_suggestions'], 1):
            output.append(f"   {i}. {suggestion}")
        output.append(f"\n💡 MEJORES PRÁCTICAS:")
        for i, practice in enumerate(story['best_practices'], 1):
            output.append(f"   {i}. {practice}")
        
        output.append("\n" + "=" * 80)
        output.append("✨ ¡Listo para publicar! ✨")
        output.append("=" * 80)
        
        return "\n".join(output)


def main():
    """Función principal"""
    if len(sys.argv) < 2:
        print("Uso: python recycle_social_post.py '[TEXTO DE LA PUBLICACIÓN ANTIGUA]'")
        print("\nEjemplo:")
        print('python recycle_social_post.py "La automatización puede ahorrarte hasta 10 horas semanales. #Productividad #IA"')
        sys.exit(1)
    
    original_post = sys.argv[1]
    
    recycler = SocialPostRecycler(original_post)
    result = recycler.generate_all_versions()
    
    # Mostrar resultado formateado
    print(recycler.format_output(result))
    
    # Guardar también en JSON para referencia
    output_file = f"recycled_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Resultado guardado también en: {output_file}")


if __name__ == "__main__":
    main()

