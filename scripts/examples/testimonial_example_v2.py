#!/usr/bin/env python3
"""
Ejemplos mejorados de uso del convertidor de testimonios v2.0
Demuestra todas las nuevas funcionalidades: análisis, hooks, métricas, etc.
"""

import sys
import os
import json

# Agregar el directorio padre al path para importar el módulo
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from testimonial_to_social_post_v2 import TestimonialToSocialPostConverterV2


def ejemplo_analisis_completo():
    """Ejemplo mostrando análisis completo del testimonio"""
    print("=" * 70)
    print("EJEMPLO 1: Análisis Completo con Métricas de Calidad")
    print("=" * 70)
    
    testimonial = (
        "Antes de usar este servicio, estaba perdiendo clientes constantemente. "
        "Ahora tengo una tasa de retención del 95% y mis ingresos han aumentado un 40% "
        "en solo 3 meses. No puedo creer la diferencia que ha hecho. "
        "Recomiendo este servicio a cualquier empresa que quiera crecer."
    )
    
    target_audience = "mejorar la retención de clientes y aumentar ingresos"
    
    converter = TestimonialToSocialPostConverterV2()
    
    result = converter.convert_testimonial(
        testimonial=testimonial,
        target_audience_problem=target_audience,
        platform="linkedin",
        tone="profesional y empático",
        analyze_quality=True,
        generate_hooks=True
    )
    
    print("\n📝 PUBLICACIÓN GENERADA:")
    print("-" * 70)
    print(result["full_post"])
    print("-" * 70)
    
    print("\n📊 ANÁLISIS DEL TESTIMONIO:")
    if result.get("analysis"):
        analysis = result["analysis"]
        
        print(f"\n  🔢 MÉTRICAS EXTRAÍDAS:")
        if analysis.get("metrics"):
            metrics = analysis["metrics"]
            if metrics.get("percentages"):
                print(f"    • Porcentajes: {', '.join(metrics['percentages'])}%")
            if metrics.get("numbers"):
                print(f"    • Números: {', '.join(metrics['numbers'])}")
            if metrics.get("timeframes"):
                print(f"    • Marcos temporales: {', '.join([f\"{t[0]} {t[1]}\" for t in metrics['timeframes']])}")
            if metrics.get("comparisons"):
                print(f"    • Comparaciones: {', '.join(metrics['comparisons'])}")
        
        print(f"\n  😊 SENTIMIENTO:")
        if analysis.get("sentiment"):
            sentiment = analysis["sentiment"]
            print(f"    • Score: {sentiment.get('score', 0):.2f}")
            print(f"    • Label: {sentiment.get('label', 'N/A')}")
            print(f"    • Palabras positivas: {sentiment.get('positive_words', 0)}")
        
        print(f"\n  📖 LEGIBILIDAD:")
        if analysis.get("readability"):
            readability = analysis["readability"]
            print(f"    • Score: {readability.get('score', 0):.1f}/100")
            print(f"    • Longitud promedio de oración: {readability.get('avg_sentence_length', 0):.1f} palabras")
            print(f"    • Total de palabras: {readability.get('total_words', 0)}")
    
    print("\n⭐ MÉTRICAS DE CALIDAD:")
    if result.get("quality_metrics"):
        qm = result["quality_metrics"]
        print(f"  • Engagement Score: {qm.get('engagement_score', 0):.1f}/100")
        print(f"  • Readability Score: {qm.get('readability_score', 0):.1f}/100")
        print(f"  • Sentiment Score: {qm.get('sentiment_score', 0):.2f}")
        
        if qm.get("factors"):
            print(f"\n  📈 FACTORES DE ENGAGEMENT:")
            factors = qm["factors"]
            for factor, value in factors.items():
                print(f"    • {factor.replace('_', ' ').title()}: {value:.1f}")
    
    print("\n🎣 HOOKS ALTERNATIVOS:")
    if result.get("hooks"):
        for i, hook in enumerate(result["hooks"], 1):
            print(f"  {i}. {hook}")
    
    print("\n🎨 SUGERENCIAS VISUALES:")
    if result.get("visual_suggestions"):
        vs = result["visual_suggestions"]
        if vs.get("image_types"):
            print(f"  • Tipos de imagen:")
            for img_type in vs["image_types"][:3]:
                print(f"    - {img_type}")
        if vs.get("video_concepts"):
            print(f"  • Conceptos de video:")
            for concept in vs["video_concepts"][:2]:
                print(f"    - {concept}")
    
    print("\n⏰ MEJORES HORARIOS PARA PUBLICAR:")
    if result.get("posting_suggestions"):
        ps = result["posting_suggestions"]
        print(f"  • Horarios sugeridos: {', '.join(ps.get('best_times', []))}")
        print(f"  • Engagement estimado: {ps.get('estimated_engagement', 0):.1f}/100")
    
    print()


def ejemplo_multiplataforma_mejorado():
    """Ejemplo mejorado para múltiples plataformas con análisis"""
    print("=" * 70)
    print("EJEMPLO 2: Comparación Multiplataforma con Análisis")
    print("=" * 70)
    
    testimonial = (
        "Compré este producto hace un mes y ya he visto resultados increíbles. "
        "Mi piel se ve más joven y radiante. Mis amigos me preguntan qué estoy usando. "
        "Definitivamente lo recomiendo. El cambio fue del 100%."
    )
    
    target_audience = "mejorar la apariencia de la piel y verse más joven"
    
    converter = TestimonialToSocialPostConverterV2()
    
    platforms = ["instagram", "twitter", "linkedin"]
    
    results = {}
    for platform in platforms:
        print(f"\n📱 {platform.upper()}:")
        print("-" * 70)
        
        result = converter.convert_testimonial(
            testimonial=testimonial,
            target_audience_problem=target_audience,
            platform=platform,
            tone="cálido y profesional",
            analyze_quality=True
        )
        
        results[platform] = result
        
        print(result["full_post"])
        print(f"\n📊 Estadísticas:")
        print(f"  • Longitud: {result['length']}/{result['max_length']} caracteres")
        if result.get("quality_metrics"):
            print(f"  • Engagement Score: {result['quality_metrics'].get('engagement_score', 0):.1f}/100")
        print()


def ejemplo_multiidioma():
    """Ejemplo de generación en múltiples idiomas"""
    print("=" * 70)
    print("EJEMPLO 3: Generación Multiidioma")
    print("=" * 70)
    
    testimonial_es = (
        "Este curso cambió completamente mi perspectiva. En solo 2 semanas aprendí "
        "más que en meses de estudio autodidacta. Ahora tengo las habilidades que "
        "necesitaba para avanzar en mi carrera."
    )
    
    target_audience = "aprender nuevas habilidades y avanzar profesionalmente"
    
    converter = TestimonialToSocialPostConverterV2()
    
    languages = [
        ("es", "Español"),
        ("en", "English"),
        ("pt", "Português")
    ]
    
    for lang_code, lang_name in languages:
        print(f"\n🌍 {lang_name.upper()}:")
        print("-" * 70)
        
        result = converter.convert_testimonial(
            testimonial=testimonial_es,
            target_audience_problem=target_audience,
            platform="general",
            tone="inspirador y empático",
            language=lang_code,
            analyze_quality=True
        )
        
        print(result["full_post"])
        print(f"\n  • Engagement Score: {result['quality_metrics'].get('engagement_score', 0):.1f}/100")
        print()


def ejemplo_variaciones_avanzadas():
    """Ejemplo de generación de múltiples variaciones con análisis"""
    print("=" * 70)
    print("EJEMPLO 4: Variaciones Avanzadas para A/B Testing")
    print("=" * 70)
    
    testimonial = (
        "Implementamos esta solución hace 6 meses y nuestra productividad aumentó un 60%. "
        "El ROI fue evidente desde el primer mes. El equipo está más motivado y "
        "los clientes están más satisfechos. La inversión se pagó sola en 2 meses."
    )
    
    target_audience = "aumentar productividad y mejorar ROI"
    
    converter = TestimonialToSocialPostConverterV2()
    
    variations = converter.generate_multiple_variations(
        testimonial=testimonial,
        target_audience_problem=target_audience,
        platforms=["instagram"],
        count=3,
        language="es"
    )
    
    for i, variation in enumerate(variations, 1):
        print(f"\n🔄 VARIACIÓN {i}:")
        print("-" * 70)
        print(variation["full_post"])
        
        print(f"\n📊 Métricas:")
        print(f"  • Tono: {variation['metadata']['tone']}")
        print(f"  • Longitud: {variation['length']} caracteres")
        if variation.get("quality_metrics"):
            print(f"  • Engagement Score: {variation['quality_metrics'].get('engagement_score', 0):.1f}/100")
        
        if i == 1 and variation.get("hooks"):
            print(f"\n🎣 Hooks alternativos disponibles: {len(variation['hooks'])}")
        
        print()


def ejemplo_json_completo():
    """Ejemplo de salida JSON completa para integración"""
    print("=" * 70)
    print("EJEMPLO 5: Salida JSON Completa (para integraciones)")
    print("=" * 70)
    
    testimonial = (
        "Este servicio superó todas mis expectativas. En 30 días logré resultados "
        "que pensé que tomarían 6 meses. Mi negocio creció un 150% y ahora tengo "
        "más tiempo libre. ¡Increíble!"
    )
    
    target_audience = "acelerar el crecimiento del negocio"
    
    converter = TestimonialToSocialPostConverterV2()
    
    result = converter.convert_testimonial(
        testimonial=testimonial,
        target_audience_problem=target_audience,
        platform="general",
        tone="inspirador y empático",
        generate_hooks=True,
        analyze_quality=True
    )
    
    print("\n📄 JSON Output Completo:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    # Verificar que la API key esté configurada
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Error: OPENAI_API_KEY no está configurada")
        print("   Configúrala con: export OPENAI_API_KEY=tu_api_key")
        sys.exit(1)
    
    try:
        ejemplo_analisis_completo()
        print("\n\n")
        
        ejemplo_multiplataforma_mejorado()
        print("\n\n")
        
        ejemplo_multiidioma()
        print("\n\n")
        
        ejemplo_variaciones_avanzadas()
        print("\n\n")
        
        ejemplo_json_completo()
        
        print("\n\n✅ Todos los ejemplos ejecutados correctamente!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



