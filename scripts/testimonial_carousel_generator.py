#!/usr/bin/env python3
"""
Generador de Carruseles para Instagram/Facebook
Convierte testimonios en carruseles de múltiples slides optimizados para redes sociales
"""

import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

try:
    from testimonial_to_social_post_v2 import TestimonialToSocialPostConverterV2, TestimonialAnalyzer
except ImportError:
    print("Error: testimonial_to_social_post_v2 no está disponible")
    exit(1)


class CarouselGenerator:
    """Genera carruseles de slides para testimonios"""
    
    def __init__(self, converter: Optional[TestimonialToSocialPostConverterV2] = None):
        """
        Inicializa el generador de carruseles
        
        Args:
            converter: Instancia del convertidor (se crea una nueva si no se proporciona)
        """
        self.converter = converter or TestimonialToSocialPostConverterV2()
        self.analyzer = TestimonialAnalyzer()
    
    def generate_carousel(
        self,
        testimonial: str,
        target_audience: str,
        platform: str = "instagram",
        num_slides: int = 5,
        include_metrics: bool = True,
        include_before_after: bool = True,
        include_cta: bool = True
    ) -> Dict[str, Any]:
        """
        Genera un carrusel completo para un testimonio
        
        Args:
            testimonial: Texto del testimonio
            target_audience: Público objetivo
            platform: Plataforma (instagram, facebook)
            num_slides: Número de slides (3-10)
            include_metrics: Incluir slide con métricas
            include_before_after: Incluir slide antes/después
            include_cta: Incluir slide con CTA
        
        Returns:
            Dict con estructura del carrusel
        """
        num_slides = max(3, min(10, num_slides))  # Limitar entre 3 y 10
        
        # Analizar testimonio
        analysis = {
            "metrics": self.analyzer.extract_metrics(testimonial),
            "sentiment": self.analyzer.analyze_sentiment(testimonial)
        }
        
        # Generar publicación base
        base_post = self.converter.convert_testimonial(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platform=platform,
            generate_hooks=True,
            analyze_quality=True
        )
        
        # Generar slides
        slides = []
        
        # Slide 1: Hook/Título
        slides.append({
            "slide_number": 1,
            "type": "hook",
            "title": self._extract_hook(testimonial, target_audience),
            "content": "",
            "visual_suggestion": "Texto grande y llamativo con fondo de color",
            "cta": None
        })
        
        # Slide 2: Problema inicial (si aplica)
        if include_before_after and self._has_before_after(testimonial):
            slides.append({
                "slide_number": len(slides) + 1,
                "type": "before",
                "title": "Antes",
                "content": self._extract_before(testimonial),
                "visual_suggestion": "Imagen representando el problema o situación inicial",
                "cta": None
            })
        
        # Slide 3-N: Contenido principal dividido
        main_content_slides = self._split_content(base_post["post_content"], num_slides - 2 - (1 if include_metrics else 0) - (1 if include_cta else 0))
        
        for i, content in enumerate(main_content_slides):
            slides.append({
                "slide_number": len(slides) + 1,
                "type": "content",
                "title": None,
                "content": content,
                "visual_suggestion": "Imagen relacionada con el contenido o testimonio",
                "cta": None
            })
        
        # Slide de métricas (si aplica)
        if include_metrics and analysis["metrics"].get("percentages"):
            metrics_text = self._format_metrics(analysis["metrics"])
            slides.append({
                "slide_number": len(slides) + 1,
                "type": "metrics",
                "title": "Resultados",
                "content": metrics_text,
                "visual_suggestion": "Gráfico o infografía con las métricas destacadas",
                "cta": None
            })
        
        # Slide final: CTA
        if include_cta:
            slides.append({
                "slide_number": len(slides) + 1,
                "type": "cta",
                "title": None,
                "content": base_post.get("call_to_action") or "¿Listo para obtener resultados similares?",
                "visual_suggestion": "Diseño llamativo con botón o elemento visual destacado",
                "cta": "Contacta ahora / Descubre más / Comienza hoy"
            })
        
        # Ajustar números de slides
        for i, slide in enumerate(slides, 1):
            slide["slide_number"] = i
        
        return {
            "testimonial": testimonial,
            "target_audience": target_audience,
            "platform": platform,
            "total_slides": len(slides),
            "slides": slides,
            "hashtags": base_post.get("hashtags", []),
            "caption": self._generate_carousel_caption(base_post, slides),
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "has_metrics": include_metrics and bool(analysis["metrics"].get("percentages")),
                "has_before_after": include_before_after and self._has_before_after(testimonial)
            }
        }
    
    def _extract_hook(self, testimonial: str, target_audience: str) -> str:
        """Extrae o genera un hook del testimonio"""
        # Intentar usar hooks generados si están disponibles
        # Por ahora, generar uno simple
        if "antes" in testimonial.lower() and "ahora" in testimonial.lower():
            return f"De {target_audience.split()[0]} a resultados increíbles"
        
        # Buscar números o porcentajes
        import re
        percentages = re.findall(r'(\d+(?:\.\d+)?)\s*%', testimonial)
        if percentages:
            return f"{percentages[0]}% de mejora en resultados"
        
        return f"Resultados que transforman: {target_audience}"
    
    def _has_before_after(self, testimonial: str) -> bool:
        """Verifica si el testimonio tiene estructura antes/después"""
        testimonial_lower = testimonial.lower()
        return ("antes" in testimonial_lower and "ahora" in testimonial_lower) or \
               ("antes" in testimonial_lower and "después" in testimonial_lower)
    
    def _extract_before(self, testimonial: str) -> str:
        """Extrae la parte 'antes' del testimonio"""
        import re
        # Buscar patrón "antes...ahora"
        match = re.search(r'antes[^.]*\.', testimonial, re.IGNORECASE)
        if match:
            return match.group(0).capitalize()
        return "Situación inicial con desafíos"
    
    def _split_content(self, content: str, num_slides: int) -> List[str]:
        """Divide el contenido en múltiples slides"""
        if num_slides <= 1:
            return [content]
        
        # Dividir por oraciones
        import re
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) <= num_slides:
            return sentences + [""] * (num_slides - len(sentences))
        
        # Distribuir oraciones entre slides
        slides_content = []
        sentences_per_slide = len(sentences) // num_slides
        
        for i in range(num_slides):
            start = i * sentences_per_slide
            end = start + sentences_per_slide if i < num_slides - 1 else len(sentences)
            slide_text = ". ".join(sentences[start:end])
            if slide_text and not slide_text.endswith('.'):
                slide_text += "."
            slides_content.append(slide_text)
        
        return slides_content
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Formatea las métricas para un slide"""
        lines = []
        
        if metrics.get("percentages"):
            for pct in metrics["percentages"][:3]:  # Máximo 3 métricas
                lines.append(f"📈 {pct}% de mejora")
        
        if metrics.get("timeframes"):
            timeframe = metrics["timeframes"][0]
            lines.append(f"⏱️ En solo {timeframe[0]} {timeframe[1]}")
        
        return "\n".join(lines) if lines else "Resultados medibles y comprobables"
    
    def _generate_carousel_caption(self, base_post: Dict[str, Any], slides: List[Dict[str, Any]]) -> str:
        """Genera el caption para el carrusel"""
        caption_parts = [
            "Desliza para ver la transformación completa 👉",
            "",
            base_post.get("post_content", "")[:200] + "...",
            "",
            "💬 ¿Te identificas con esta historia?",
            ""
        ]
        
        if base_post.get("hashtags"):
            caption_parts.append(" ".join(base_post["hashtags"][:5]))
        
        return "\n".join(caption_parts)


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generador de Carruseles para Testimonios")
    parser.add_argument(
        "testimonial",
        help="Texto del testimonio"
    )
    parser.add_argument(
        "target_audience",
        help="Público objetivo"
    )
    parser.add_argument(
        "--platform",
        choices=["instagram", "facebook"],
        default="instagram",
        help="Plataforma (default: instagram)"
    )
    parser.add_argument(
        "--slides",
        type=int,
        default=5,
        help="Número de slides (3-10, default: 5)"
    )
    parser.add_argument(
        "--no-metrics",
        action="store_true",
        help="No incluir slide de métricas"
    )
    parser.add_argument(
        "--no-before-after",
        action="store_true",
        help="No incluir slide antes/después"
    )
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Formato de salida"
    )
    
    args = parser.parse_args()
    
    generator = CarouselGenerator()
    
    carousel = generator.generate_carousel(
        testimonial=args.testimonial,
        target_audience=args.target_audience,
        platform=args.platform,
        num_slides=args.slides,
        include_metrics=not args.no_metrics,
        include_before_after=not args.no_before_after,
        include_cta=True
    )
    
    if args.output == "json":
        print(json.dumps(carousel, indent=2, ensure_ascii=False))
    else:
        print(f"\n📱 CARRUSEL PARA {args.platform.upper()}")
        print("=" * 70)
        print(f"Total de slides: {carousel['total_slides']}\n")
        
        for slide in carousel["slides"]:
            print(f"Slide {slide['slide_number']} - {slide['type'].upper()}")
            print("-" * 70)
            if slide.get("title"):
                print(f"Título: {slide['title']}")
            if slide.get("content"):
                print(f"Contenido: {slide['content']}")
            print(f"Sugerencia visual: {slide['visual_suggestion']}")
            if slide.get("cta"):
                print(f"CTA: {slide['cta']}")
            print()
        
        print("\n📝 CAPTION SUGERIDO:")
        print("-" * 70)
        print(carousel["caption"])
        print()


if __name__ == "__main__":
    main()


