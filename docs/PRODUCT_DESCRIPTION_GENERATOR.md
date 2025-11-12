# Generador de Descripciones de Productos con IA

Sistema completo para generar descripciones de productos optimizadas para e-commerce que aumentan conversiones en 30-50%.

## 🎯 Características Principales

- ✅ **Generación con IA** - Descripciones completas de 200-400 palabras
- ✅ **Optimización SEO** - Keywords, meta descripciones, análisis de score
- ✅ **Multi-plataforma** - Amazon, Shopify, WooCommerce, genérico
- ✅ **Storytelling emocional** - Dirigido a público específico
- ✅ **A/B Testing** - Generación de variaciones automáticas
- ✅ **Análisis de competencia** - Optimización basada en competidores
- ✅ **Exportación** - Múltiples formatos (JSON, XML, CSV, HTML)
- ✅ **API REST** - Automatización masiva vía API
- ✅ **Caché inteligente** - Evita regeneraciones innecesarias

## 📋 Requisitos

- Python 3.8+
- PostgreSQL (para almacenamiento)
- API Key de OpenAI, DeepSeek o Anthropic
- Airflow (opcional, para DAGs)

## 🚀 Inicio Rápido

### 1. Configuración de Base de Datos

```sql
-- Ejecutar el esquema SQL
\i data/airflow/dags/product_description_schema.sql
```

### 2. Configurar Variables de Airflow

```python
# En Airflow UI o Variables
OPENAI_API_KEY = "tu-api-key"
DEFAULT_LLM_PROVIDER = "openai"
```

### 3. Uso Básico con Python

```python
from product_description_generator import LLMClient, ProductDescriptionGenerator

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
        'Comfort superior con tecnología avanzada'
    ],
    technical_features=[
        'Suela de caucho reciclado con 70% de contenido reciclado',
        'Forro interior de algodón orgánico certificado',
        'Peso ligero: 280g por par'
    ],
    target_audience='compradores eco-friendly conscientes del medio ambiente',
    platform='amazon',
    keywords=['zapatos ecológicos', 'calzado sostenible'],
    word_count=300
)

print(result['description'])
print(f"SEO Score: {result['seo_analysis']['score']}")
```

## 📖 Uso Avanzado

### Generación con Análisis de Competencia

```python
# Analizar competidores antes de generar
competitors_data = [
    {
        'title': 'Zapatos Eco Pro',
        'description': 'Zapatos ecológicos con suela reciclada...'
    },
    {
        'title': 'EcoFoot Premium',
        'description': 'Calzado sostenible de alta calidad...'
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

print(result['competitor_analysis'])
```

### Generación de Variaciones para A/B Testing

```python
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

for var in variations:
    print(f"Variación {var['variation_type']}: {var['description'][:100]}...")
```

### Exportación a Formatos de Plataformas

```python
from product_description_exporters import ProductDescriptionExporter

# Exportar a formato Amazon
amazon_format = ProductDescriptionExporter.export_to_amazon_format(result)
print(json.dumps(amazon_format, indent=2, ensure_ascii=False))

# Exportar a formato Shopify
shopify_format = ProductDescriptionExporter.export_to_shopify_format(result)
print(json.dumps(shopify_format, indent=2, ensure_ascii=False))

# Exportar a CSV para importación masiva
descriptions = [result]  # Lista de descripciones
ProductDescriptionExporter.export_to_csv(descriptions, 'productos.csv')
```

## 🔌 API REST

### Iniciar el servidor

```bash
# Desarrollo
python data/airflow/dags/product_description_api.py

# Producción con gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 product_description_api:app
```

### Endpoints Disponibles

#### 1. Generar Descripción Única

```bash
curl -X POST http://localhost:5000/api/v1/product-descriptions/generate \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Zapatos Ecológicos Modelo X",
    "product_type": "Calzado sostenible",
    "key_benefits": ["Durabilidad 2x mayor"],
    "technical_features": ["Suela reciclada"],
    "target_audience": "compradores eco-friendly",
    "platform": "amazon",
    "word_count": 300
  }'
```

#### 2. Generación Masiva (Batch)

```bash
curl -X POST http://localhost:5000/api/v1/product-descriptions/generate-batch \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {
        "product_name": "Producto 1",
        "key_benefits": ["Beneficio 1"],
        "technical_features": ["Feature 1"],
        "target_audience": "Audiencia",
        "platform": "shopify"
      },
      {
        "product_name": "Producto 2",
        "key_benefits": ["Beneficio 2"],
        "technical_features": ["Feature 2"],
        "target_audience": "Audiencia",
        "platform": "amazon"
      }
    ]
  }'
```

#### 3. Generar Variaciones para A/B Testing

```bash
curl -X POST http://localhost:5000/api/v1/product-descriptions/variations \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Zapatos Ecológicos",
    "key_benefits": ["Durabilidad 2x mayor"],
    "technical_features": ["Suela reciclada"],
    "target_audience": "compradores eco-friendly",
    "num_variations": 3,
    "variation_types": ["emotional", "technical", "benefit_focused"]
  }'
```

#### 4. Validar Datos de Producto

```bash
curl -X POST http://localhost:5000/api/v1/product-descriptions/validate \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Producto Test",
    "key_benefits": ["Beneficio"],
    "technical_features": ["Feature"],
    "target_audience": "Audiencia"
  }'
```

## 🔄 Uso con Airflow DAG

### Ejecutar DAG Manualmente

```python
# En Airflow UI, trigger DAG con parámetros:
{
    "product_name": "Zapatos Ecológicos Modelo X",
    "product_type": "Calzado sostenible",
    "key_benefits": [
        "Durabilidad 2x mayor que zapatos convencionales",
        "100% materiales reciclados"
    ],
    "technical_features": [
        "Suela de caucho reciclado",
        "Algodón orgánico certificado"
    ],
    "target_audience": "compradores eco-friendly",
    "platform": "amazon",
    "keywords": ["zapatos ecológicos", "calzado sostenible"],
    "word_count": 300,
    "generate_variations": true,
    "num_variations": 3
}
```

## 📊 Estructura de Respuesta

```json
{
    "description": "Descripción completa del producto...",
    "title": "Título Optimizado - Beneficio Principal",
    "full_description": "Descripción completa sin optimización",
    "benefits_section": "Sección de beneficios extraída",
    "technical_section": "Sección técnica extraída",
    "storytelling_section": "Sección de storytelling extraída",
    "seo_keywords": ["keyword1", "keyword2", ...],
    "seo_analysis": {
        "score": 85.5,
        "keyword_density": {
            "keyword1": {"count": 3, "density": 1.2}
        },
        "total_words": 250,
        "recommendations": ["Recomendación 1", ...]
    },
    "meta_description": "Meta descripción para SEO...",
    "multimedia_suggestions": {
        "images": [...],
        "videos": [...],
        "infographics": [...]
    },
    "word_count": 250,
    "platform": "amazon",
    "language": "es",
    "metadata": {
        "provider": "openai",
        "model": "gpt-4o-mini",
        "tokens_used": 450,
        "generated_at": "2024-01-15T10:30:00"
    }
}
```

## 🎨 Optimización por Plataforma

### Amazon
- Bullets points destacados (máximo 5)
- Descripción técnica y orientada a resultados
- Keywords naturales en título y descripción
- Límite: 2000 caracteres

### Shopify
- Storytelling emocional más extenso
- HTML básico permitido
- Formato más libre y creativo
- Sin límite estricto (recomendado 200-400 palabras)

### Genérico
- Balance entre información técnica y emocional
- Estructura clara con secciones
- Optimizado para múltiples plataformas

## 🔍 Análisis SEO

El sistema incluye análisis automático de SEO:

- **Score SEO** (0-100): Evaluación general
- **Keyword Density**: Densidad de cada keyword
- **Recomendaciones**: Sugerencias para mejorar

```python
seo_analysis = result['seo_analysis']
print(f"Score: {seo_analysis['score']}")
print(f"Recomendaciones: {seo_analysis['recommendations']}")
```

## 📈 A/B Testing

### Generar Variaciones

```python
variations = generator.generate_variations(
    base_product_info=product_info,
    num_variations=3,
    variation_types=['emotional', 'technical', 'benefit_focused']
)
```

### Tipos de Variación

- **emotional**: Enfoque en storytelling y conexión emocional
- **technical**: Enfoque en características técnicas
- **benefit_focused**: Enfoque en beneficios y resultados
- **seo_optimized**: Optimización máxima para SEO

### Tracking de Métricas

Las métricas de A/B testing se almacenan en `product_description_ab_metrics`:

```sql
SELECT 
    variation_type,
    SUM(views) as total_views,
    SUM(conversions) as total_conversions,
    AVG(conversion_rate) as avg_conversion_rate
FROM product_description_ab_metrics
WHERE product_description_id = 1
GROUP BY variation_type;
```

## 🔗 Integraciones

### Shopify

```python
from product_description_integrations import ShopifyIntegration

shopify = ShopifyIntegration(
    shop_domain='mi-tienda.myshopify.com',
    access_token='token'
)

# Sincronizar descripción generada
result = shopify.update_product_description(
    product_id='123456',
    description=generated_description
)
```

### Amazon

```python
from product_description_integrations import AmazonIntegration

amazon = AmazonIntegration(
    marketplace_id='ATVPDKIKX0DER',
    seller_id='seller_id',
    access_key='access_key',
    secret_key='secret_key'
)

# Formatear y actualizar
formatted = amazon.format_for_amazon(description_data)
result = amazon.update_product_listing(sku='SKU123', description=formatted)
```

## 🛠️ Mejores Prácticas

1. **Beneficios Clave**: Incluye datos específicos y verificables
   - ✅ "Durabilidad 2x mayor"
   - ❌ "Muy duradero"

2. **Keywords**: Usa keywords naturales, evita keyword stuffing
   - ✅ Integra keywords en el texto de forma natural
   - ❌ Repite keywords excesivamente

3. **Storytelling**: Conecta emocionalmente con el público objetivo
   - ✅ "Imagina caminar sabiendo que cada paso ayuda al planeta"
   - ❌ "Zapatos ecológicos"

4. **Longitud**: Mantén entre 200-400 palabras para mejor conversión

5. **A/B Testing**: Prueba diferentes variaciones y mide resultados

## 📝 Ejemplos Completos

### Ejemplo 1: Producto Eco-Friendly

```python
result = generator.generate_description(
    product_name='Botella de Agua Reutilizable EcoPro',
    product_type='Accesorio sostenible',
    key_benefits=[
        'Mantiene temperatura 24 horas (frío/caliente)',
        '100% libre de BPA y materiales tóxicos',
        'Ahorra hasta 365 botellas de plástico al año'
    ],
    technical_features=[
        'Acero inoxidable 18/8 grado alimentario',
        'Capacidad: 750ml',
        'Aislamiento al vacío de doble pared',
        'Peso: 320g'
    ],
    target_audience='personas conscientes del medio ambiente que buscan alternativas sostenibles',
    platform='shopify',
    keywords=['botella reutilizable', 'botella acero inoxidable', 'botella ecológica'],
    brand_story='Creada por amantes del medio ambiente para reducir el impacto del plástico',
    word_count=350
)
```

### Ejemplo 2: Producto Tecnológico

```python
result = generator.generate_description(
    product_name='Auriculares Inalámbricos ProMax',
    product_type='Electrónica de consumo',
    key_benefits=[
        'Cancelación de ruido activa (ANC) de última generación',
        'Batería de 30 horas con carga rápida de 10 minutos',
        'Calidad de sonido Hi-Fi con drivers de 40mm'
    ],
    technical_features=[
        'Bluetooth 5.3 con codec aptX HD',
        'Micrófonos con cancelación de ruido para llamadas',
        'Resistencia al agua IPX4',
        'Compatibilidad con asistentes de voz'
    ],
    target_audience='profesionales y entusiastas del audio que buscan calidad premium',
    platform='amazon',
    keywords=['auriculares inalámbricos', 'cancelación ruido', 'auriculares bluetooth'],
    word_count=300
)
```

## 🐛 Troubleshooting

### Error: "API key no configurada"
- Verifica que las variables de Airflow estén configuradas
- Revisa que el proveedor LLM esté correctamente inicializado

### Error: "Campo requerido faltante"
- Asegúrate de incluir todos los campos requeridos:
  - product_name
  - key_benefits (array no vacío)
  - technical_features (array no vacío)
  - target_audience

### Descripciones muy cortas o largas
- Ajusta `word_count` (recomendado: 200-400)
- Verifica que los prompts incluyan suficiente contexto

### Score SEO bajo
- Revisa las recomendaciones en `seo_analysis['recommendations']`
- Ajusta la densidad de keywords según sugerencias

## 📚 Referencias

- [Documentación de Airflow](https://airflow.apache.org/docs/)
- [Shopify API](https://shopify.dev/docs/api/admin-rest)
- [Amazon Seller Central](https://sellercentral.amazon.com/)

## 🤝 Contribuir

Para mejorar el sistema:

1. Agrega nuevos tipos de variación
2. Mejora los prompts de generación
3. Agrega soporte para más plataformas
4. Optimiza el análisis SEO

## 📄 Licencia

Este sistema es parte de la plataforma de automatización empresarial.

---

**Versión**: 1.0  
**Última actualización**: 2024  
**Mantenido por**: ecommerce-team






