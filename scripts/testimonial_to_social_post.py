#!/usr/bin/env python3
"""
Script para convertir testimonios de clientes en publicaciones narrativas para redes sociales
Convierte testimonios en contenido atractivo enfocado en resultados, con tono cálido y profesional
"""

import os
import sys
import json
import argparse
import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    from openai import OpenAI
except ImportError:
    print("Error: openai no está instalado. Instálalo con: pip install openai")
    sys.exit(1)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TestimonialToSocialPostConverter:
    """Clase para convertir testimonios de clientes en publicaciones para redes sociales"""
    
    def __init__(self, openai_api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        """
        Inicializa el convertidor de testimonios
        
        Args:
            openai_api_key: Clave API de OpenAI. Si es None, intenta obtenerla de OPENAI_API_KEY
            model: Modelo de OpenAI a usar (default: gpt-4o-mini)
        
        Raises:
            ValueError: Si la API key no está configurada
        """
        self.api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError(
                "OPENAI_API_KEY no está configurada. "
                "Configúrala como variable de entorno o pásala como parámetro."
            )
        
        try:
            self.client = OpenAI(api_key=self.api_key)
            self.model = model
            logger.info(f"Convertidor inicializado con modelo: {model}")
        except Exception as e:
            logger.error(f"Error al inicializar cliente de OpenAI: {e}")
            raise
    
    def convert_testimonial(
        self,
        testimonial: str,
        target_audience_problem: str,
        platform: str = "general",
        tone: str = "cálido y profesional",
        max_length: Optional[int] = None,
        include_hashtags: bool = True,
        include_call_to_action: bool = True
    ) -> Dict[str, Any]:
        """
        Convierte un testimonio en una publicación narrativa para redes sociales
        
        Args:
            testimonial: Texto del testimonio del cliente
            target_audience_problem: Problema o resultado que busca el público objetivo
            platform: Plataforma objetivo (general, instagram, facebook, linkedin, twitter, tiktok)
            tone: Tono deseado (default: "cálido y profesional")
            max_length: Longitud máxima en caracteres (None = sin límite)
            include_hashtags: Si incluir hashtags relevantes
            include_call_to_action: Si incluir llamada a la acción
        
        Returns:
            Dict con la publicación generada y metadatos
        
        Raises:
            ValueError: Si los parámetros requeridos están vacíos o son inválidos
            Exception: Si hay un error al generar la publicación
        """
        # Validar inputs
        if not testimonial or not testimonial.strip():
            raise ValueError("El testimonio no puede estar vacío")
        
        if not target_audience_problem or not target_audience_problem.strip():
            raise ValueError("El problema/resultado del público objetivo no puede estar vacío")
        
        testimonial = testimonial.strip()
        target_audience_problem = target_audience_problem.strip()
        platform = platform.lower().strip()
        
        logger.info(f"Convirtiendo testimonio para plataforma: {platform}, tono: {tone}")
        
        # Configuración específica por plataforma
        platform_configs = {
            "instagram": {
                "max_length": max_length or 2200,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True
            },
            "facebook": {
                "max_length": max_length or 5000,
                "hashtags_count": 3,
                "emoji": True,
                "line_breaks": True
            },
            "linkedin": {
                "max_length": max_length or 3000,
                "hashtags_count": 5,
                "emoji": False,
                "line_breaks": True,
                "tone": "profesional y empático"
            },
            "twitter": {
                "max_length": max_length or 280,
                "hashtags_count": 2,
                "emoji": True,
                "line_breaks": False
            },
            "tiktok": {
                "max_length": max_length or 300,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True
            },
            "general": {
                "max_length": max_length or 1000,
                "hashtags_count": 5,
                "emoji": True,
                "line_breaks": True
            }
        }
        
        config = platform_configs.get(platform, platform_configs["general"])
        
        # Validar longitud del testimonio antes de procesar
        if len(testimonial) > 5000:
            logger.warning(f"Testimonio muy largo ({len(testimonial)} caracteres). Se procesará completo pero puede afectar la calidad.")
        
        # Construir el prompt para la IA
        prompt = self._build_prompt(
            testimonial=testimonial,
            target_audience_problem=target_audience_problem,
            platform=platform,
            tone=tone,
            config=config,
            include_hashtags=include_hashtags,
            include_call_to_action=include_call_to_action
        )
        
        # Generar la publicación usando OpenAI
        try:
            logger.debug("Enviando solicitud a OpenAI...")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un experto en marketing de contenidos y copywriting para redes sociales. "
                            "Especializas en convertir testimonios de clientes en publicaciones narrativas "
                            "que conectan emocionalmente con la audiencia y destacan resultados concretos. "
                            "Tu objetivo es crear contenido auténtico, convincente y orientado a resultados."
                        )
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            generated_content = response.choices[0].message.content.strip()
            logger.debug(f"Contenido generado ({len(generated_content)} caracteres)")
            
            # Extraer hashtags y CTA si están incluidos
            post_content, hashtags, cta = self._parse_generated_content(
                generated_content,
                include_hashtags=include_hashtags,
                include_call_to_action=include_call_to_action
            )
            
            # Validar longitud
            if config["max_length"] and len(post_content) > config["max_length"]:
                logger.info(f"Publicación excede límite ({len(post_content)} > {config['max_length']}). Acortando...")
                post_content = self._shorten_post(post_content, config["max_length"])
            
            full_post = self._combine_post_parts(post_content, hashtags, cta, config)
            
            result = {
                "post_content": post_content,
                "hashtags": hashtags,
                "call_to_action": cta,
                "full_post": full_post,
                "platform": platform,
                "length": len(post_content),
                "full_length": len(full_post),
                "max_length": config["max_length"],
                "timestamp": datetime.now().isoformat(),
                "metadata": {
                    "original_testimonial_length": len(testimonial),
                    "tone": tone,
                    "target_audience": target_audience_problem,
                    "model_used": self.model
                }
            }
            
            logger.info(f"Publicación generada exitosamente: {result['length']} caracteres")
            return result
            
        except Exception as e:
            error_msg = f"Error al generar la publicación: {str(e)}"
            logger.error(error_msg, exc_info=True)
            raise Exception(error_msg) from e
    
    def _build_prompt(
        self,
        testimonial: str,
        target_audience_problem: str,
        platform: str,
        tone: str,
        config: Dict[str, Any],
        include_hashtags: bool,
        include_call_to_action: bool
    ) -> str:
        """Construye el prompt para la generación de la publicación"""
        
        # Ajustar tono según plataforma si es LinkedIn
        final_tone = config.get("tone", tone) if platform == "linkedin" else tone
        
        prompt = f"""Convierte el siguiente testimonio de cliente en una publicación narrativa para {platform.upper()}.

TESTIMONIO DEL CLIENTE:
"{testimonial}"

CONTEXTO Y OBJETIVO:
- Público objetivo: Personas que buscan {target_audience_problem}
- Tono: {final_tone}
- Plataforma: {platform.upper()}

REQUISITOS TÉCNICOS:
- Longitud máxima del contenido principal: {config['max_length']} caracteres
- Formato: {'Con saltos de línea para legibilidad' if config['line_breaks'] else 'Texto continuo'}
- Emojis: {'Sí, usa emojis relevantes (máximo 3-5)' if config['emoji'] else 'No uses emojis'}

ESTRUCTURA NARRATIVA:
1. Hook inicial (1-2 líneas): Captura la atención mencionando el problema o resultado clave
2. Cuerpo narrativo: Relata el testimonio enfocándote en:
   - El RESULTADO CONCRETO obtenido (números, porcentajes, mejoras específicas)
   - La experiencia del cliente (qué sintió, cómo cambió su situación)
   - El valor percibido (por qué fue importante para ellos)
3. Cierre: Conecta con el público objetivo de manera empática

ENFOQUE ESPECIAL:
- Destaca números, porcentajes y resultados medibles si están presentes
- Usa lenguaje emocional pero auténtico
- Evita exageraciones o lenguaje demasiado promocional
- Mantén la autenticidad del testimonio original
"""
        
        if include_hashtags:
            prompt += f"\n- Incluye {config['hashtags_count']} hashtags relevantes al final (en una línea separada)"
        
        if include_call_to_action:
            prompt += "\n- Incluye una llamada a la acción sutil y natural al final (antes de los hashtags si los hay)"
        
        prompt += "\n\nIMPORTANTE: Genera SOLO el contenido de la publicación, sin explicaciones adicionales, sin prefijos como 'Publicación:' o 'Aquí está:'. Empieza directamente con el hook."
        
        return prompt
    
    def _parse_generated_content(
        self,
        content: str,
        include_hashtags: bool,
        include_call_to_action: bool
    ) -> Tuple[str, List[str], Optional[str]]:
        """
        Extrae el contenido principal, hashtags y CTA del texto generado
        
        Returns:
            Tuple con (contenido_principal, lista_hashtags, cta)
        """
        
        hashtags = []
        cta = None
        post_content = content
        
        # Limpiar contenido de prefijos comunes
        prefixes_to_remove = [
            "Publicación:",
            "Aquí está:",
            "Publicación para",
            "Contenido:",
            "Texto:"
        ]
        for prefix in prefixes_to_remove:
            if post_content.strip().startswith(prefix):
                post_content = post_content.replace(prefix, "", 1).strip()
        
        # Extraer hashtags usando regex para mayor precisión
        if include_hashtags:
            # Buscar hashtags en todo el contenido
            hashtag_pattern = r'#\w+'
            found_hashtags = re.findall(hashtag_pattern, content)
            
            if found_hashtags:
                hashtags = list(set(found_hashtags))  # Eliminar duplicados manteniendo orden
                # Remover hashtags del contenido principal
                for hashtag in found_hashtags:
                    post_content = re.sub(re.escape(hashtag), '', post_content)
        
        # Extraer CTA (últimas líneas que contengan verbos de acción)
        if include_call_to_action:
            cta_keywords = [
                'comienza', 'descubre', 'prueba', 'contacta', 'solicita', 'aprende', 
                'conecta', 'consulta', 'visita', 'sigue', 'únete', 'explora', 
                'conoce', 'descubre más', 'empieza', 'obtén', 'accede'
            ]
            lines = [line.strip() for line in post_content.split('\n') if line.strip()]
            
            # Buscar CTA en las últimas 2-3 líneas
            for line in reversed(lines[-3:]):
                line_lower = line.lower()
                # Verificar si contiene palabras clave de CTA
                if any(keyword in line_lower for keyword in cta_keywords):
                    # Verificar que no sea solo un hashtag
                    if not line.strip().startswith('#'):
                        cta = line.strip()
                        # Remover CTA del contenido principal
                        post_content = post_content.replace(line, '').strip()
                        break
        
        # Limpiar espacios múltiples y saltos de línea excesivos
        post_content = re.sub(r'\n{3,}', '\n\n', post_content)
        post_content = re.sub(r' +', ' ', post_content)
        
        return post_content.strip(), hashtags, cta
    
    def _shorten_post(self, content: str, max_length: int) -> str:
        """
        Acorta una publicación si excede la longitud máxima
        
        Args:
            content: Contenido a acortar
            max_length: Longitud máxima deseada
        
        Returns:
            Contenido acortado manteniendo el mensaje principal
        """
        if len(content) <= max_length:
            return content
        
        logger.info(f"Acortando contenido de {len(content)} a {max_length} caracteres")
        
        # Intentar acortar manteniendo el mensaje principal usando IA
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Eres un experto en copywriting. Tu tarea es acortar textos "
                            "manteniendo el mensaje principal, el impacto emocional y los resultados clave. "
                            "Prioriza números, porcentajes y resultados concretos."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Acorta este texto a máximo {max_length} caracteres, "
                            f"manteniendo el mensaje principal, el impacto emocional y los resultados clave:\n\n{content}"
                        )
                    }
                ],
                temperature=0.5,
                max_tokens=500
            )
            shortened = response.choices[0].message.content.strip()
            logger.debug(f"Contenido acortado con IA: {len(shortened)} caracteres")
            return shortened
        except Exception as e:
            logger.warning(f"Error al acortar con IA: {e}. Usando método de truncamiento inteligente.")
            # Fallback: truncar de forma inteligente
            return self._intelligent_truncate(content, max_length)
    
    def _intelligent_truncate(self, content: str, max_length: int) -> str:
        """
        Trunca contenido de forma inteligente buscando puntos de corte naturales
        
        Args:
            content: Contenido a truncar
            max_length: Longitud máxima
        
        Returns:
            Contenido truncado
        """
        if len(content) <= max_length:
            return content
        
        # Buscar puntos de corte naturales
        truncated = content[:max_length]
        
        # Priorizar puntos de corte: punto seguido de espacio > punto > salto de línea > espacio
        cut_points = [
            truncated.rfind('. '),
            truncated.rfind('.\n'),
            truncated.rfind('.'),
            truncated.rfind('\n'),
            truncated.rfind(' '),
        ]
        
        # Encontrar el mejor punto de corte (el más cercano al límite pero válido)
        best_cut = -1
        for cut in cut_points:
            if cut > max_length * 0.6:  # Al menos 60% del contenido
                best_cut = max(best_cut, cut)
        
        if best_cut > 0:
            result = truncated[:best_cut + 1].strip()
            # Agregar elipsis solo si realmente cortamos contenido significativo
            if len(result) < len(content) * 0.9:
                result += "..."
            return result
        
        # Si no encontramos buen punto, truncar y agregar elipsis
        return truncated.strip() + "..."
    
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
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """
        Genera múltiples variaciones de la publicación para diferentes plataformas o estilos
        
        Args:
            testimonial: Texto del testimonio
            target_audience_problem: Problema o resultado buscado
            platforms: Lista de plataformas (None = generar variaciones generales)
            count: Número de variaciones por plataforma
        
        Returns:
            Lista de publicaciones generadas
        """
        if platforms is None:
            platforms = ["general"]
        
        all_posts = []
        
        for platform in platforms:
            for i in range(count):
                # Variar ligeramente el tono para cada variación
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
                    tone=tone
                )
                post["variation_number"] = i + 1
                all_posts.append(post)
        
        return all_posts


def main():
    """Función principal para ejecución desde línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Convierte testimonios de clientes en publicaciones para redes sociales"
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
    parser.add_argument(
        "--file",
        "-f",
        help="Archivo JSON con los parámetros (puede incluir testimonial, target_audience, platform, tone, etc.)"
    )
    parser.add_argument(
        "--model",
        default="gpt-4o-mini",
        help="Modelo de OpenAI a usar (default: gpt-4o-mini)"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Modo verbose con más información de debug"
    )
    
    args = parser.parse_args()
    
    # Configurar logging según verbosidad
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Si se proporciona un archivo, leer los parámetros desde ahí
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                file_data = json.load(f)
            
            # Mapear nombres alternativos
            testimonial = (
                file_data.get("testimonial") or 
                file_data.get("testimonio") or 
                file_data.get("text") or
                args.testimonial
            )
            target_audience = (
                file_data.get("target_audience") or 
                file_data.get("target_audience_problem") or
                file_data.get("problema_resultado") or
                file_data.get("problema") or
                file_data.get("resultado") or
                args.target_audience
            )
            platform = file_data.get("platform") or file_data.get("plataforma") or args.platform
            tone = file_data.get("tone") or file_data.get("tono") or args.tone
            max_length = file_data.get("max_length") or args.max_length
            include_hashtags = file_data.get("include_hashtags", not args.no_hashtags)
            include_cta = file_data.get("include_call_to_action", not args.no_cta)
            model = file_data.get("model") or args.model
            
            # Actualizar args con valores del archivo
            args.testimonial = testimonial
            args.target_audience = target_audience
            args.platform = platform
            args.tone = tone
            args.max_length = max_length
            args.no_hashtags = not include_hashtags
            args.no_cta = not include_cta
            args.model = model
            
            logger.info(f"Parámetros cargados desde archivo: {args.file}")
        except FileNotFoundError:
            logger.error(f"Archivo no encontrado: {args.file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON: {e}")
            sys.exit(1)
    
    try:
        converter = TestimonialToSocialPostConverter(
            openai_api_key=args.api_key,
            model=args.model
        )
        
        if args.variations:
            posts = converter.generate_multiple_variations(
                testimonial=args.testimonial,
                target_audience_problem=args.target_audience,
                platforms=[args.platform],
                count=args.variations
            )
        else:
            post = converter.convert_testimonial(
                testimonial=args.testimonial,
                target_audience_problem=args.target_audience,
                platform=args.platform,
                tone=args.tone,
                max_length=args.max_length,
                include_hashtags=not args.no_hashtags,
                include_call_to_action=not args.no_cta
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
                
                print("PUBLICACIÓN GENERADA:")
                print("-" * 60)
                print(post["full_post"])
                print("-" * 60)
                print(f"\nLongitud: {post['length']} caracteres")
                print(f"Longitud completa (con hashtags/CTA): {post.get('full_length', post['length'])} caracteres")
                print(f"Plataforma: {post['platform']}")
                print(f"Modelo usado: {post['metadata'].get('model_used', 'N/A')}")
                if post["hashtags"]:
                    print(f"Hashtags ({len(post['hashtags'])}): {', '.join(post['hashtags'])}")
                if post["call_to_action"]:
                    print(f"CTA: {post['call_to_action']}")
                print()
    
    except ValueError as e:
        logger.error(f"Error de validación: {e}")
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error inesperado: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
