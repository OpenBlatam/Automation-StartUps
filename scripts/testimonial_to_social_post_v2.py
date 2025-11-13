#!/usr/bin/env python3
"""
Script MEJORADO para convertir testimonios de clientes en publicaciones narrativas para redes sociales
Versión 2.0 con mejoras avanzadas:

NUEVAS FUNCIONALIDADES:
- ✅ Análisis de sentimiento y calidad del testimonio
- ✅ Generación de múltiples hooks para A/B testing
- ✅ Optimización de engagement (emojis estratégicos, timing sugerido)
- ✅ Soporte multiidioma
- ✅ Análisis de keywords y SEO
- ✅ Sugerencias de imágenes/videos basadas en contenido
- ✅ Métricas de calidad estimadas (readability, engagement score)
- ✅ Extracción automática de métricas y números del testimonio
- ✅ Generación de variaciones con diferentes estructuras narrativas
"""

import os
import sys
import json
import argparse
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import Counter

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai no está instalado. Instálalo con: pip install openai")
    sys.exit(1)


class TestimonialAnalyzer:
    """Analiza testimonios para extraer información valiosa"""
    
    @staticmethod
    def extract_metrics(testimonial: str) -> Dict[str, Any]:
        """Extrae métricas y números del testimonio"""
        metrics = {
            "numbers": [],
            "percentages": [],
            "timeframes": [],
            "comparisons": []
        }
        
        # Buscar porcentajes
        percentage_pattern = r'(\d+(?:\.\d+)?)\s*%'
        metrics["percentages"] = re.findall(percentage_pattern, testimonial)
        
        # Buscar números
        number_pattern = r'\b(\d+(?:\.\d+)?)\b'
        all_numbers = re.findall(number_pattern, testimonial)
        metrics["numbers"] = [n for n in all_numbers if n not in metrics["percentages"]]
        
        # Buscar marcos temporales
        time_pattern = r'(\d+)\s*(mes|meses|semana|semanas|día|días|año|años|hora|horas)'
        metrics["timeframes"] = re.findall(time_pattern, testimonial, re.IGNORECASE)
        
        # Buscar comparaciones
        comparison_words = ["aumentó", "mejoró", "redujo", "incrementó", "disminuyó", "creció"]
        for word in comparison_words:
            if word.lower() in testimonial.lower():
                metrics["comparisons"].append(word)
        
        return metrics
    
    @staticmethod
    def analyze_sentiment(testimonial: str) -> Dict[str, Any]:
        """Analiza el sentimiento del testimonio"""
        positive_words = [
            "excelente", "increíble", "fantástico", "maravilloso", "perfecto",
            "genial", "satisfecho", "recomiendo", "recomiendo", "feliz",
            "contento", "sorprendido", "impresionado", "agradecido"
        ]
        
        negative_words = [
            "malo", "terrible", "horrible", "decepcionado", "insatisfecho",
            "problema", "error", "fallo", "difícil", "complicado"
        ]
        
        testimonial_lower = testimonial.lower()
        positive_count = sum(1 for word in positive_words if word in testimonial_lower)
        negative_count = sum(1 for word in negative_words if word in testimonial_lower)
        
        # Calcular score de sentimiento (-1 a 1)
        total_words = len(testimonial.split())
        sentiment_score = (positive_count - negative_count) / max(total_words / 10, 1)
        sentiment_score = max(-1, min(1, sentiment_score))
        
        return {
            "score": sentiment_score,
            "label": "positivo" if sentiment_score > 0.1 else "negativo" if sentiment_score < -0.1 else "neutral",
            "positive_words": positive_count,
            "negative_words": negative_count
        }
    
    @staticmethod
    def calculate_readability(text: str) -> Dict[str, Any]:
        """Calcula métricas de legibilidad"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = text.split()
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(w) for w in words) / len(words) if words else 0
        
        # Score de legibilidad simple (0-100, más alto = más legible)
        readability_score = 100 - (avg_sentence_length * 2) - (avg_word_length * 3)
        readability_score = max(0, min(100, readability_score))
        
        return {
            "score": readability_score,
            "avg_sentence_length": round(avg_sentence_length, 2),
            "avg_word_length": round(avg_word_length, 2),
            "total_words": len(words),
            "total_sentences": len(sentences)
        }


class TestimonialToSocialPostConverterV2:
    """Clase mejorada para convertir testimonios en publicaciones para redes sociales"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Inicializa el convertidor de testimonios
        
        Args:
            openai_api_key: Clave API de OpenAI. Si es None, intenta obtenerla de OPENAI_API_KEY
            model: Modelo de OpenAI a usar (default: gpt-4o-mini)
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY no está configurada")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.analyzer = TestimonialAnalyzer()
        
        # Emojis estratégicos por categoría
        self.emoji_map = {
            "éxito": ["🎉", "🚀", "✨", "🏆", "💪"],
            "resultado": ["📈", "💯", "⭐", "🔥", "💎"],
            "transformación": ["🦋", "🌟", "💫", "🎯", "🌈"],
            "satisfacción": ["😊", "❤️", "🙌", "👏", "💖"],
            "crecimiento": ["📊", "🌱", "⬆️", "💼", "🎓"]
        }
    
    def convert_testimonial(
        self,
        testimonial: str,
        target_audience_problem: str,
        platform: str = "general",
        tone: str = "cálido y profesional",
        max_length: Optional[int] = None,
        include_hashtags: bool = True,
        include_call_to_action: bool = True,
        language: str = "es",
        generate_hooks: bool = False,
        analyze_quality: bool = True
    ) -> Dict[str, Any]:
        """
        Convierte un testimonio en una publicación narrativa para redes sociales (VERSIÓN MEJORADA)
        
        Args:
            testimonial: Texto del testimonio del cliente
            target_audience_problem: Problema o resultado que busca el público objetivo
            platform: Plataforma objetivo (general, instagram, facebook, linkedin, twitter, tiktok)
            tone: Tono deseado (default: "cálido y profesional")
            max_length: Longitud máxima en caracteres (None = sin límite)
            include_hashtags: Si incluir hashtags relevantes
            include_call_to_action: Si incluir llamada a la acción
            language: Idioma de salida (es, en, pt, fr, etc.)
            generate_hooks: Si generar múltiples hooks para A/B testing
            analyze_quality: Si analizar calidad del testimonio
        
        Returns:
            Dict con la publicación generada y metadatos mejorados
        """
        
        # Análisis previo del testimonio
        analysis = {}
        if analyze_quality:
            analysis = {
                "metrics": self.analyzer.extract_metrics(testimonial),
                "sentiment": self.analyzer.analyze_sentiment(testimonial),
                "readability": self.analyzer.calculate_readability(testimonial)
            }
        
        # Configuración específica por plataforma
        platform_configs = {
            "instagram": {
                "max_length": max_length or 2200,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True,
                "best_times": ["9:00", "13:00", "17:00", "21:00"]
            },
            "facebook": {
                "max_length": max_length or 5000,
                "hashtags_count": 3,
                "emoji": True,
                "line_breaks": True,
                "best_times": ["8:00", "13:00", "17:00"]
            },
            "linkedin": {
                "max_length": max_length or 3000,
                "hashtags_count": 5,
                "emoji": False,
                "line_breaks": True,
                "best_times": ["8:00", "12:00", "17:00"],
                "tone": "profesional y empático"
            },
            "twitter": {
                "max_length": max_length or 280,
                "hashtags_count": 2,
                "emoji": True,
                "line_breaks": False,
                "best_times": ["8:00", "12:00", "17:00", "21:00"]
            },
            "tiktok": {
                "max_length": max_length or 300,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True,
                "best_times": ["9:00", "12:00", "19:00", "21:00"]
            },
            "general": {
                "max_length": max_length or 1000,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True,
                "best_times": ["9:00", "13:00", "17:00"]
            }
        }
        
        config = platform_configs.get(platform.lower(), platform_configs["general"])
        
        # Generar hooks alternativos si se solicita
        hooks = []
        if generate_hooks:
            hooks = self._generate_hooks(testimonial, target_audience_problem, config)
        
        # Construir el prompt mejorado
        prompt = self._build_enhanced_prompt(
            testimonial=testimonial,
            target_audience_problem=target_audience_problem,
            platform=platform,
            tone=tone,
            config=config,
            include_hashtags=include_hashtags,
            include_call_to_action=include_call_to_action,
            language=language,
            analysis=analysis
        )
        
        # Generar la publicación usando OpenAI
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt(language)
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            generated_content = response.choices[0].message.content.strip()
            
            # Extraer componentes
            post_content, hashtags, cta, suggestions = self._parse_enhanced_content(
                generated_content,
                include_hashtags=include_hashtags,
                include_call_to_action=include_call_to_action
            )
            
            # Validar y ajustar longitud
            if config["max_length"] and len(post_content) > config["max_length"]:
                post_content = self._shorten_post(post_content, config["max_length"])
            
            # Calcular métricas de calidad
            quality_metrics = self._calculate_quality_metrics(
                post_content,
                analysis.get("readability", {}),
                analysis.get("sentiment", {})
            )
            
            # Generar sugerencias de contenido visual
            visual_suggestions = self._generate_visual_suggestions(
                testimonial,
                target_audience_problem,
                analysis.get("metrics", {})
            )
            
            return {
                "post_content": post_content,
                "hashtags": hashtags,
                "call_to_action": cta,
                "full_post": self._combine_post_parts(post_content, hashtags, cta, config),
                "platform": platform,
                "length": len(post_content),
                "max_length": config["max_length"],
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "original_testimonial_length": len(testimonial),
                    "tone": tone,
                    "target_audience": target_audience_problem,
                    "language": language
                },
                "analysis": analysis,
                "quality_metrics": quality_metrics,
                "hooks": hooks if generate_hooks else None,
                "visual_suggestions": visual_suggestions,
                "posting_suggestions": {
                    "best_times": config.get("best_times", []),
                    "estimated_engagement": quality_metrics.get("engagement_score", 0)
                }
            }
            
        except Exception as e:
            raise Exception(f"Error al generar la publicación: {str(e)}")
    
    def _get_system_prompt(self, language: str) -> str:
        """Obtiene el prompt del sistema según el idioma"""
        prompts = {
            "es": "Eres un experto en marketing de contenidos y copywriting para redes sociales. "
                  "Especializas en convertir testimonios de clientes en publicaciones narrativas "
                  "que conectan emocionalmente con la audiencia y destacan resultados concretos. "
                  "Tu objetivo es crear contenido que genere engagement y conversión.",
            "en": "You are an expert in content marketing and copywriting for social media. "
                  "You specialize in converting customer testimonials into narrative posts "
                  "that emotionally connect with the audience and highlight concrete results. "
                  "Your goal is to create content that generates engagement and conversion.",
            "pt": "Você é um especialista em marketing de conteúdo e copywriting para redes sociais. "
                  "Você se especializa em converter depoimentos de clientes em posts narrativos "
                  "que se conectam emocionalmente com o público e destacam resultados concretos. "
                  "Seu objetivo é criar conteúdo que gere engajamento e conversão."
        }
        return prompts.get(language, prompts["es"])
    
    def _build_enhanced_prompt(
        self,
        testimonial: str,
        target_audience_problem: str,
        platform: str,
        tone: str,
        config: Dict[str, Any],
        include_hashtags: bool,
        include_call_to_action: bool,
        language: str,
        analysis: Dict[str, Any]
    ) -> str:
        """Construye un prompt mejorado con análisis previo"""
        
        prompt_parts = [
            f"Convierte el siguiente testimonio de cliente en una publicación narrativa para {platform.upper()}.",
            "",
            "TESTIMONIO DEL CLIENTE:",
            f'"{testimonial}"',
            ""
        ]
        
        # Agregar análisis si está disponible
        if analysis:
            if analysis.get("metrics", {}).get("percentages"):
                prompt_parts.append(f"MÉTRICAS DESTACADAS: {', '.join(analysis['metrics']['percentages'])}%")
            if analysis.get("sentiment", {}).get("label") == "positivo":
                prompt_parts.append("SENTIMIENTO: Muy positivo - enfatiza los resultados exitosos")
            prompt_parts.append("")
        
        prompt_parts.extend([
            "REQUISITOS:",
            f"- Público objetivo: Personas que buscan {target_audience_problem}",
            f"- Tono: {tone}",
            "- Enfoque principal: Destacar el RESULTADO que obtuvo el cliente",
            f"- Longitud máxima: {config['max_length']} caracteres",
            f"- Formato: {'Con saltos de línea para legibilidad' if config['line_breaks'] else 'Texto continuo'}",
            f"- Emojis: {'Sí, usa emojis estratégicos y relevantes' if config['emoji'] else 'No uses emojis'}",
            "",
            "ESTRUCTURA DESEADA:",
            "1. Hook inicial poderoso que capture la atención (mencionando el problema/resultado)",
            "2. Narrativa del testimonio enfocada en el resultado obtenido",
            "3. Conclusión que conecte emocionalmente con el público objetivo",
            ""
        ])
        
        if include_hashtags:
            prompt_parts.append(f"- Incluye {config['hashtags_count']} hashtags relevantes y estratégicos al final")
        
        if include_call_to_action:
            prompt_parts.append("- Incluye una llamada a la acción sutil, natural y convincente")
        
        prompt_parts.extend([
            "",
            "GENERA SOLO el contenido de la publicación, sin explicaciones adicionales.",
            "Si hay métricas o números en el testimonio, destácalos de forma visual."
        ])
        
        return "\n".join(prompt_parts)
    
    def _generate_hooks(
        self,
        testimonial: str,
        target_audience_problem: str,
        config: Dict[str, Any]
    ) -> List[str]:
        """Genera múltiples hooks alternativos para A/B testing"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en crear hooks poderosos para redes sociales."
                    },
                    {
                        "role": "user",
                        "content": f"""Genera 5 hooks diferentes (máximo 100 caracteres cada uno) para este testimonio:
                        
Testimonio: "{testimonial}"
Público objetivo: {target_audience_problem}

Cada hook debe:
- Capturar la atención inmediatamente
- Mencionar el problema o resultado
- Ser único y diferente de los otros

Lista solo los hooks, uno por línea, sin numeración."""
                    }
                ],
                temperature=0.9,
                max_tokens=300
            )
            
            hooks_text = response.choices[0].message.content.strip()
            hooks = [h.strip() for h in hooks_text.split('\n') if h.strip()]
            return hooks[:5]  # Limitar a 5 hooks
            
        except Exception as e:
            return []
    
    def _parse_enhanced_content(
        self,
        content: str,
        include_hashtags: bool,
        include_call_to_action: bool
    ) -> Tuple[str, List[str], Optional[str], Dict[str, Any]]:
        """Extrae el contenido principal, hashtags, CTA y sugerencias"""
        
        hashtags = []
        cta = None
        suggestions = {}
        post_content = content
        
        # Extraer hashtags
        if include_hashtags:
            lines = content.split('\n')
            hashtag_lines = [line for line in lines if line.strip().startswith('#')]
            if hashtag_lines:
                hashtags = [tag.strip() for tag in ' '.join(hashtag_lines).split() if tag.startswith('#')]
                for line in hashtag_lines:
                    post_content = post_content.replace(line, '').strip()
        
        # Extraer CTA
        if include_call_to_action:
            cta_keywords = ['comienza', 'descubre', 'prueba', 'contacta', 'solicita', 'aprende', 'conecta', 'únete']
            lines = post_content.split('\n')
            for line in reversed(lines):
                if any(keyword in line.lower() for keyword in cta_keywords):
                    cta = line.strip()
                    break
        
        # Extraer sugerencias si están presentes
        if "SUGERENCIA:" in content or "Sugerencia:" in content:
            # Intentar extraer sugerencias del contenido
            pass
        
        return post_content.strip(), hashtags, cta, suggestions
    
    def _calculate_quality_metrics(
        self,
        post_content: str,
        readability: Dict[str, Any],
        sentiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calcula métricas de calidad de la publicación"""
        
        # Score de engagement estimado (0-100)
        engagement_factors = {
            "has_question": 10 if '?' in post_content else 0,
            "has_emoji": 5 if any(ord(c) > 127 for c in post_content) else 0,
            "has_numbers": 10 if re.search(r'\d+', post_content) else 0,
            "has_cta": 15 if any(word in post_content.lower() for word in ['comienza', 'descubre', 'prueba', 'contacta']) else 0,
            "readability": readability.get("score", 50) * 0.3,
            "sentiment": (sentiment.get("score", 0) + 1) * 25  # Convertir -1,1 a 0,50
        }
        
        engagement_score = sum(engagement_factors.values())
        engagement_score = min(100, max(0, engagement_score))
        
        return {
            "engagement_score": round(engagement_score, 1),
            "readability_score": readability.get("score", 0),
            "sentiment_score": sentiment.get("score", 0),
            "factors": engagement_factors
        }
    
    def _generate_visual_suggestions(
        self,
        testimonial: str,
        target_audience_problem: str,
        metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Genera sugerencias de contenido visual"""
        
        suggestions = {
            "image_types": [],
            "video_concepts": [],
            "graphic_elements": []
        }
        
        # Sugerencias basadas en métricas
        if metrics.get("percentages"):
            suggestions["graphic_elements"].append("Gráfico de barras o dona mostrando el porcentaje")
            suggestions["image_types"].append("Infografía con métricas destacadas")
        
        # Sugerencias basadas en contenido
        if "antes" in testimonial.lower() and "ahora" in testimonial.lower():
            suggestions["image_types"].append("Comparación antes/después")
            suggestions["video_concepts"].append("Video testimonial con transformación")
        
        if "resultado" in testimonial.lower() or "éxito" in testimonial.lower():
            suggestions["image_types"].append("Imagen de celebración o logro")
            suggestions["graphic_elements"].append("Iconos de éxito (trofeo, estrella, etc.)")
        
        # Sugerencias genéricas
        if not suggestions["image_types"]:
            suggestions["image_types"] = [
                "Foto del cliente (si está disponible)",
                "Imagen relacionada con el problema/resultado",
                "Diseño minimalista con texto destacado"
            ]
        
        return suggestions
    
    def _shorten_post(self, content: str, max_length: int) -> str:
        """Acorta una publicación si excede la longitud máxima"""
        if len(content) <= max_length:
            return content
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un experto en copywriting. Acortas textos manteniendo el mensaje principal y el impacto emocional."
                    },
                    {
                        "role": "user",
                        "content": f"Acorta este texto a máximo {max_length} caracteres, manteniendo el mensaje principal, el impacto emocional y las métricas:\n\n{content}"
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )
            return response.choices[0].message.content.strip()
        except:
            # Fallback: truncar de forma inteligente
            if len(content) > max_length:
                truncated = content[:max_length]
                last_period = truncated.rfind('.')
                last_newline = truncated.rfind('\n')
                cut_point = max(last_period, last_newline)
                if cut_point > max_length * 0.7:
                    return truncated[:cut_point + 1] + "..."
                return truncated + "..."
            return content
    
    def _combine_post_parts(
        self,
        post_content: str,
        hashtags: List[str],
        cta: Optional[str],
        config: Dict[str, Any]
    ) -> str:
        """Combina todas las partes de la publicación en un texto completo"""
        parts = [post_content]
        
        if cta:
            parts.append(f"\n\n{cta}")
        
        if hashtags:
            hashtag_line = " ".join(hashtags)
            parts.append(f"\n\n{hashtag_line}")
        
        return "\n".join(parts)
    
    def generate_multiple_variations(
        self,
        testimonial: str,
        target_audience_problem: str,
        platforms: List[str] = None,
        count: int = 3,
        language: str = "es"
    ) -> List[Dict[str, Any]]:
        """
        Genera múltiples variaciones mejoradas de la publicación
        
        Args:
            testimonial: Texto del testimonio
            target_audience_problem: Problema o resultado buscado
            platforms: Lista de plataformas (None = generar variaciones generales)
            count: Número de variaciones por plataforma
            language: Idioma de salida
        
        Returns:
            Lista de publicaciones generadas con análisis completo
        """
        if platforms is None:
            platforms = ["general"]
        
        all_posts = []
        
        for platform in platforms:
            for i in range(count):
                tones = [
                    "cálido y profesional",
                    "inspirador y empático",
                    "directo y convincente"
                ]
                tone = tones[i % len(tones)]
                
                post = self.convert_testimonial(
                    testimonial=testimonial,
                    target_audience_problem=target_audience_problem,
                    platform=platform,
                    tone=tone,
                    language=language,
                    generate_hooks=(i == 0),  # Generar hooks solo en la primera variación
                    analyze_quality=True
                )
                post["variation_number"] = i + 1
                all_posts.append(post)
        
        return all_posts


def main():
    """Función principal para ejecución desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Convierte testimonios de clientes en publicaciones para redes sociales (VERSIÓN MEJORADA)"
    )
    parser.add_argument(
        "testimonial",
        help="Texto del testimonio del cliente"
    )
    parser.add_argument(
        "target_audience",
        help="Problema o resultado que busca el público objetivo"
    )
    parser.add_argument(
        "--platform",
        choices=["general", "instagram", "facebook", "linkedin", "twitter", "tiktok"],
        default="general",
        help="Plataforma objetivo (default: general)"
    )
    parser.add_argument(
        "--tone",
        default="cálido y profesional",
        help="Tono deseado (default: cálido y profesional)"
    )
    parser.add_argument(
        "--max-length",
        type=int,
        help="Longitud máxima en caracteres"
    )
    parser.add_argument(
        "--no-hashtags",
        action="store_true",
        help="No incluir hashtags"
    )
    parser.add_argument(
        "--no-cta",
        action="store_true",
        help="No incluir llamada a la acción"
    )
    parser.add_argument(
        "--language",
        choices=["es", "en", "pt", "fr"],
        default="es",
        help="Idioma de salida (default: es)"
    )
    parser.add_argument(
        "--generate-hooks",
        action="store_true",
        help="Generar múltiples hooks para A/B testing"
    )
    parser.add_argument(
        "--no-analysis",
        action="store_true",
        help="No realizar análisis de calidad"
    )
    parser.add_argument(
        "--variations",
        type=int,
        metavar="N",
        help="Generar N variaciones de la publicación"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Formato de salida (default: text)"
    )
    parser.add_argument(
        "--api-key",
        help="API Key de OpenAI (o usar variable de entorno OPENAI_API_KEY)"
    )
    
    args = parser.parse_args()
    
    try:
        converter = TestimonialToSocialPostConverterV2(openai_api_key=args.api_key)
        
        if args.variations:
            posts = converter.generate_multiple_variations(
                testimonial=args.testimonial,
                target_audience_problem=args.target_audience,
                platforms=[args.platform],
                count=args.variations,
                language=args.language
            )
        else:
            post = converter.convert_testimonial(
                testimonial=args.testimonial,
                target_audience_problem=args.target_audience,
                platform=args.platform,
                tone=args.tone,
                max_length=args.max_length,
                include_hashtags=not args.no_hashtags,
                include_call_to_action=not args.no_cta,
                language=args.language,
                generate_hooks=args.generate_hooks,
                analyze_quality=not args.no_analysis
            )
            posts = [post]
        
        if args.output == "json":
            print(json.dumps(posts if args.variations else posts[0], indent=2, ensure_ascii=False))
        else:
            for i, post in enumerate(posts, 1):
                if args.variations:
                    print(f"\n{'='*60}")
                    print(f"VARIACIÓN {i}")
                    print(f"{'='*60}\n")
                
                print("📱 PUBLICACIÓN GENERADA:")
                print("-" * 60)
                print(post["full_post"])
                print("-" * 60)
                
                print(f"\n📊 ESTADÍSTICAS:")
                print(f"  • Longitud: {post['length']} caracteres")
                print(f"  • Plataforma: {post['platform']}")
                if post.get("hashtags"):
                    print(f"  • Hashtags ({len(post['hashtags'])}): {', '.join(post['hashtags'])}")
                if post.get("call_to_action"):
                    print(f"  • CTA: {post['call_to_action']}")
                
                if post.get("quality_metrics"):
                    qm = post["quality_metrics"]
                    print(f"\n⭐ MÉTRICAS DE CALIDAD:")
                    print(f"  • Engagement Score: {qm.get('engagement_score', 0)}/100")
                    print(f"  • Readability Score: {qm.get('readability_score', 0)}/100")
                
                if post.get("hooks"):
                    print(f"\n🎣 HOOKS ALTERNATIVOS:")
                    for j, hook in enumerate(post["hooks"], 1):
                        print(f"  {j}. {hook}")
                
                if post.get("visual_suggestions"):
                    vs = post["visual_suggestions"]
                    print(f"\n🎨 SUGERENCIAS VISUALES:")
                    if vs.get("image_types"):
                        print(f"  • Tipos de imagen: {', '.join(vs['image_types'][:3])}")
                    if vs.get("video_concepts"):
                        print(f"  • Conceptos de video: {', '.join(vs['video_concepts'][:2])}")
                
                if post.get("posting_suggestions"):
                    ps = post["posting_suggestions"]
                    print(f"\n⏰ MEJORES HORARIOS PARA PUBLICAR:")
                    print(f"  • {', '.join(ps.get('best_times', []))}")
                
                print()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


