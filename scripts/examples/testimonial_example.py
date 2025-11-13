#!/usr/bin/env python3
"""
Ejemplo de uso del convertidor de testimonios a publicaciones para redes sociales
"""

import sys
import os
import json

# Agregar el directorio padre al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from testimonial_to_social_post import TestimonialToSocialPostConverter


def ejemplo_basico():
    """Ejemplo básico de conversión de testimonio"""
    print("=" * 60)
    print("EJEMPLO 1: Conversión Básica")
    print("=" * 60)
    
    testimonial = (
        "Antes de usar este servicio, estaba perdiendo clientes constantemente. "
        "Ahora tengo una tasa de retención del 95% y mis ingresos han aumentado un 40% "
        "en solo 3 meses. No puedo creer la diferencia que ha hecho."
    )
    
    target_audience = "mejorar la retención de clientes y aumentar ingresos"
    
    converter = TestimonialToSocialPostConverter()
    
    result = converter.convert_testimonial(
        testimonial=testimonial,
        target_audience_problem=target_audience,
        platform="linkedin",
        tone="profesional y empático"
    )
    
    print("\n📝 PUBLICACIÓN GENERADA:")
    print("-" * 60)
    print(result["full_post"])
    print("-" * 60)
    print(f"\n📊 Estadísticas:")
    print(f"  - Longitud: {result['length']} caracteres")
    print(f"  - Plataforma: {result['platform']}")
    print(f"  - Hashtags: {len(result['hashtags'])}")
    if result['hashtags']:
        print(f"  - Hashtags: {', '.join(result['hashtags'])}")
    print()


def ejemplo_multiplataforma():
    """Ejemplo de generación para múltiples plataformas"""
    print("=" * 60)
    print("EJEMPLO 2: Múltiples Plataformas")
    print("=" * 60)
    
    testimonial = (
        "Compré este producto hace un mes y ya he visto resultados increíbles. "
        "Mi piel se ve más joven y radiante. Mis amigos me preguntan qué estoy usando. "
        "Definitivamente lo recomiendo."
    )
    
    target_audience = "mejorar la apariencia de la piel y verse más joven"
    
    converter = TestimonialToSocialPostConverter()
    
    platforms = ["instagram", "facebook", "linkedin", "twitter"]
    
    for platform in platforms:
        print(f"\n📱 {platform.upper()}:")
        print("-" * 60)
        
        result = converter.convert_testimonial(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platform=platform,
            tone="cálido y profesional"
        )
        
        print(result["full_post"])
        print(f"\nLongitud: {result['length']} caracteres")
        print()


def ejemplo_variaciones():
    """Ejemplo de generación de múltiples variaciones"""
    print("=" * 60)
    print("EJEMPLO 3: Múltiples Variaciones para A/B Testing")
    print("=" * 60)
    
    testimonial = (
        "Implementamos esta solución hace 6 meses y nuestra productividad aumentó un 60%. "
        "El ROI fue evidente desde el primer mes. El equipo está más motivado y "
        "los clientes están más satisfechos."
    )
    
    target_audience = "aumentar productividad y mejorar ROI"
    
    converter = TestimonialToSocialPostConverter()
    
    variations = converter.generate_multiple_variations(
        testimonial=testimonial,
        target_audience_problem=target_audience,
        platforms=["instagram"],
        count=3
    )
    
    for i, variation in enumerate(variations, 1):
        print(f"\n🔄 VARIACIÓN {i}:")
        print("-" * 60)
        print(variation["full_post"])
        print(f"\nTono: {variation['metadata']['tone']}")
        print(f"Longitud: {variation['length']} caracteres")
        print()


def ejemplo_json_output():
    """Ejemplo de salida en formato JSON"""
    print("=" * 60)
    print("EJEMPLO 4: Salida JSON (para integración)")
    print("=" * 60)
    
    testimonial = (
        "Este curso cambió completamente mi perspectiva. En solo 2 semanas aprendí "
        "más que en meses de estudio autodidacta. Ahora tengo las habilidades que "
        "necesitaba para avanzar en mi carrera."
    )
    
    target_audience = "aprender nuevas habilidades y avanzar profesionalmente"
    
    converter = TestimonialToSocialPostConverter()
    
    result = converter.convert_testimonial(
        testimonial=testimonial,
        target_audience_problem=target_audience,
        platform="general",
        tone="inspirador y empático"
    )
    
    print("\n📄 JSON Output:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Verificar que la API key esté configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Error: OPENAI_API_KEY no está configurada")
        print("   Configúrala con: export OPENAI_API_KEY=tu_api_key")
        sys.exit(1)
    
    try:
        ejemplo_basico()
        print("\n\n")
        
        ejemplo_multiplataforma()
        print("\n\n")
        
        ejemplo_variaciones()
        print("\n\n")
        
        ejemplo_json_output()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


