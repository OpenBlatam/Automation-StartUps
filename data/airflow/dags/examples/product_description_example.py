"""
Ejemplos completos de uso del generador de descripciones de productos.

Incluye:
- Uso básico
- Uso con templates
- Uso con análisis de competencia
- Generación de variaciones
- Análisis de calidad
- Exportación a formatos
"""

from product_description_generator import LLMClient, ProductDescriptionGenerator
from product_description_templates import ProductCategoryTemplates
from product_description_analyzer import ProductDescriptionAnalyzer
from product_description_exporters import ProductDescriptionExporter
import json


def example_basic_generation():
    """Ejemplo básico de generación."""
    print("=" * 60)
    print("EJEMPLO 1: Generación Básica")
    print("=" * 60)
    
    # Inicializar
    llm_client = LLMClient('openai')
    generator = ProductDescriptionGenerator(llm_client)
    
    # Generar descripción
    result = generator.generate_description(
        product_name='Zapatos Ecológicos Modelo X',
        product_type='Calzado sostenible',
        key_benefits=[
            'Durabilidad 2x mayor que zapatos convencionales',
            '100% materiales reciclados y reciclables',
            'Comfort superior con tecnología de amortiguación avanzada'
        ],
        technical_features=[
            'Suela de caucho reciclado con 70% de contenido reciclado',
            'Forro interior de algodón orgánico certificado',
            'Peso ligero: 280g por par',
            'Resistente al agua con tratamiento ecológico'
        ],
        target_audience='compradores eco-friendly conscientes del medio ambiente',
        platform='amazon',
        keywords=['zapatos ecológicos', 'calzado sostenible', 'zapatos reciclados'],
        word_count=300
    )
    
    print(f"\nTítulo: {result['title']}")
    print(f"\nDescripción ({result['word_count']} palabras):")
    print(result['description'][:200] + "...")
    print(f"\nSEO Score: {result['seo_analysis']['score']}")
    print(f"Keywords: {', '.join(result['seo_keywords'][:5])}")


def example_with_templates():
    """Ejemplo usando templates por categoría."""
    print("\n" + "=" * 60)
    print("EJEMPLO 2: Uso con Templates")
    print("=" * 60)
    
    # Obtener template para categoría
    category = 'eco_sustainable'
    template = ProductCategoryTemplates.get_template(category)
    
    print(f"\nTemplate para categoría '{category}':")
    print(f"Tono recomendado: {template['tone']}")
    print(f"Ángulo storytelling: {template['storytelling_angle']}")
    print(f"Keywords sugeridas: {', '.join(template['target_keywords'])}")
    
    # Enriquecer datos del producto
    product_data = {
        'product_name': 'Botella de Agua Reutilizable EcoPro',
        'key_benefits': ['Mantiene temperatura 24 horas'],
        'technical_features': ['Acero inoxidable 18/8']
    }
    
    enhanced = ProductCategoryTemplates.enhance_product_data(product_data, category)
    print(f"\nDatos enriquecidos:")
    print(f"Beneficios: {enhanced['key_benefits']}")
    print(f"Keywords: {enhanced['keywords']}")


def example_competitor_analysis():
    """Ejemplo con análisis de competencia."""
    print("\n" + "=" * 60)
    print("EJEMPLO 3: Análisis de Competencia")
    print("=" * 60)
    
    llm_client = LLMClient('openai')
    generator = ProductDescriptionGenerator(llm_client)
    
    competitors_data = [
        {
            'title': 'Zapatos Eco Pro',
            'description': 'Zapatos ecológicos con suela reciclada, diseño moderno y confortable. Ideal para uso diario.'
        },
        {
            'title': 'EcoFoot Premium',
            'description': 'Calzado sostenible de alta calidad, materiales 100% reciclados, perfecto para caminar.'
        }
    ]
    
    result = generator.generate_with_competitor_analysis(
        product_name='Zapatos Ecológicos Modelo X',
        product_type='Calzado sostenible',
        key_benefits=['Durabilidad 2x mayor'],
        technical_features=['Suela reciclada'],
        target_audience='compradores eco-friendly',
        platform='amazon',
        competitors_data=competitors_data
    )
    
    print(f"\nAnálisis de competencia:")
    print(f"Keywords comunes: {result['competitor_analysis'].get('common_keywords', [])}")
    print(f"Recomendaciones: {result['competitor_analysis'].get('recommendations', [])}")


def example_variations():
    """Ejemplo de generación de variaciones para A/B testing."""
    print("\n" + "=" * 60)
    print("EJEMPLO 4: Variaciones para A/B Testing")
    print("=" * 60)
    
    llm_client = LLMClient('openai')
    generator = ProductDescriptionGenerator(llm_client)
    
    base_product_info = {
        'product_name': 'Zapatos Ecológicos Modelo X',
        'product_type': 'Calzado sostenible',
        'key_benefits': ['Durabilidad 2x mayor', '100% reciclado'],
        'technical_features': ['Suela reciclada', 'Algodón orgánico'],
        'target_audience': 'compradores eco-friendly',
        'platform': 'amazon'
    }
    
    variations = generator.generate_variations(
        base_product_info=base_product_info,
        num_variations=3,
        variation_types=['emotional', 'technical', 'benefit_focused']
    )
    
    print(f"\nGeneradas {len(variations)} variaciones:")
    for var in variations:
        print(f"\n- {var['variation_type'].upper()}:")
        print(f"  {var['description'][:150]}...")


def example_quality_analysis():
    """Ejemplo de análisis de calidad."""
    print("\n" + "=" * 60)
    print("EJEMPLO 5: Análisis de Calidad")
    print("=" * 60)
    
    # Generar descripción primero
    llm_client = LLMClient('openai')
    generator = ProductDescriptionGenerator(llm_client)
    
    result = generator.generate_description(
        product_name='Auriculares Inalámbricos ProMax',
        product_type='Electrónica',
        key_benefits=['Cancelación de ruido activa', 'Batería 30 horas'],
        technical_features=['Bluetooth 5.3', 'Drivers 40mm'],
        target_audience='profesionales del audio',
        platform='shopify',
        word_count=300
    )
    
    # Analizar calidad
    analyzer = ProductDescriptionAnalyzer()
    analysis = analyzer.analyze_complete(result)
    
    print(f"\nAnálisis de Calidad:")
    print(f"Score Total: {analysis['quality_score']['total_score']}/100")
    print(f"Nivel: {analysis['quality_score']['quality_level']}")
    print(f"\nSentimiento: {analysis['sentiment_analysis']['sentiment']}")
    print(f"Tono: {analysis['tone']}")
    print(f"Legibilidad: {analysis['readability']['readability_level']}")
    print(f"\nRecomendaciones:")
    for rec in analysis['quality_score']['recommendations']:
        print(f"  - {rec}")


def example_export_formats():
    """Ejemplo de exportación a diferentes formatos."""
    print("\n" + "=" * 60)
    print("EJEMPLO 6: Exportación a Formatos")
    print("=" * 60)
    
    # Generar descripción
    llm_client = LLMClient('openai')
    generator = ProductDescriptionGenerator(llm_client)
    
    result = generator.generate_description(
        product_name='Zapatos Ecológicos Modelo X',
        product_type='Calzado sostenible',
        key_benefits=['Durabilidad 2x mayor'],
        technical_features=['Suela reciclada'],
        target_audience='compradores eco-friendly',
        platform='amazon',
        word_count=300
    )
    
    # Exportar a formato Amazon
    amazon_format = ProductDescriptionExporter.export_to_amazon_format(result)
    print("\nFormato Amazon:")
    print(json.dumps(amazon_format, indent=2, ensure_ascii=False)[:300] + "...")
    
    # Exportar a formato Shopify
    shopify_format = ProductDescriptionExporter.export_to_shopify_format(result)
    print("\nFormato Shopify:")
    print(json.dumps(shopify_format, indent=2, ensure_ascii=False)[:300] + "...")
    
    # Exportar a HTML
    html = ProductDescriptionExporter.export_to_html(result)
    print("\nFormato HTML:")
    print(html[:200] + "...")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("EJEMPLOS DE USO - GENERADOR DE DESCRIPCIONES")
    print("=" * 60)
    
    # Nota: Estos ejemplos requieren API keys configuradas
    print("\n⚠️  NOTA: Estos ejemplos requieren API keys configuradas")
    print("Configura OPENAI_API_KEY o el proveedor LLM antes de ejecutar\n")
    
    try:
        # Descomentar para ejecutar ejemplos específicos
        # example_basic_generation()
        # example_with_templates()
        # example_competitor_analysis()
        # example_variations()
        # example_quality_analysis()
        # example_export_formats()
        
        print("\n✅ Ejemplos cargados correctamente")
        print("Descomenta los ejemplos que quieras ejecutar en el código")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        print("Asegúrate de tener configuradas las API keys")






