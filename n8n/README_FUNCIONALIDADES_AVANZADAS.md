# Funcionalidades Avanzadas - Testimonial to Social Post

## 🚀 Nuevas Funcionalidades Implementadas

### 1. Análisis de Sentimiento
Analiza automáticamente el sentimiento del testimonio para mejorar la generación.

**Uso:**
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --analyze-sentiment
```

**Output incluye:**
- Sentimiento (positive/negative/neutral)
- Score de sentimiento (-1 a 1)
- Confianza del análisis
- Intensidad emocional
- Keywords positivas/negativas detectadas

### 2. Sistema de Templates Personalizables
Usa templates predefinidos o crea los tuyos propios.

**Templates disponibles:**
- `testimonial_resultado_destacado` - Enfoca en resultados medibles
- `testimonial_historia_narrativa` - Estructura narrativa completa

**Listar templates:**
```bash
python scripts/testimonial_to_social_post.py --list-templates
```

**Usar un template:**
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --template testimonial_resultado_destacado
```

**Crear template personalizado:**
Crea un archivo JSON en `n8n/templates/` con esta estructura:
```json
{
  "name": "Mi Template",
  "description": "Descripción del template",
  "structure": [
    "Paso 1: Descripción",
    "Paso 2: Descripción",
    "Paso 3: Descripción"
  ],
  "hook_examples": [
    "Ejemplo de hook 1",
    "Ejemplo de hook 2"
  ]
}
```

### 3. Generación de Múltiples Formatos
Genera automáticamente contenido para diferentes formatos de redes sociales.

**Uso:**
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --generate-formats
```

**Formatos generados:**
- **Carousel slides**: Captions para carruseles de Instagram/Facebook
- **Story text**: Texto optimizado para Stories (más corto)
- **Thread tweets**: Hilo de tweets desde el contenido

### 4. Sistema de Cache
Optimiza el rendimiento guardando resultados en cache.

**Uso básico (cache en memoria):**
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --enable-cache
```

**Cache persistente:**
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --enable-cache \
  --cache-file /ruta/al/cache.json
```

### 5. Análisis de Keywords y Temas
Extrae automáticamente keywords, temas y métricas del testimonio.

**Incluido automáticamente con `--analyze-sentiment`:**

**Output incluye:**
- Keywords principales
- Temas identificados (ventas, productividad, ingresos, etc.)
- Métricas mencionadas (porcentajes, números, etc.)
- Palabras de acción

### 6. Variaciones para A/B Testing
Genera variaciones optimizadas para pruebas A/B.

**Uso:**
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --variations 4 \
  --ab-testing
```

**Características:**
- Variaciones con tonos contrastados
- Diferentes templates por variación
- Análisis de sentimiento incluido
- Identificadores de variante para tracking

## 📊 Ejemplo Completo con Todas las Funcionalidades

```bash
python scripts/testimonial_to_social_post.py \
  "Gracias a este servicio aumenté mis ventas en un 300% en solo 3 meses. La atención fue excelente y los resultados superaron todas mis expectativas." \
  "aumentar ventas y mejorar resultados" \
  --platform linkedin \
  --tone "profesional y empático" \
  --analyze-sentiment \
  --template testimonial_resultado_destacado \
  --generate-formats \
  --enable-cache \
  --cache-file ./cache/testimonials.json \
  --verbose \
  --output json
```

## 🔧 Integración con API REST

La API Flask también soporta todas estas funcionalidades:

```bash
curl -X POST http://localhost:5000/convert \
  -H "Content-Type: application/json" \
  -d '{
    "testimonial": "Tu testimonio aquí",
    "target_audience": "problema/resultado",
    "platform": "linkedin",
    "analyze_sentiment": true,
    "template_id": "testimonial_resultado_destacado",
    "enable_cache": true,
    "generate_formats": true
  }'
```

## 📁 Estructura de Archivos

```
scripts/
├── testimonial_to_social_post.py      # Script principal
├── testimonial_advanced_features.py    # Funcionalidades avanzadas
└── testimonial_api.py                 # API REST

n8n/
├── templates/                          # Templates personalizables
│   ├── testimonial_resultado_destacado.json
│   └── testimonial_historia_narrativa.json
└── ejemplo_testimonial_completo.json  # Ejemplo completo
```

## 🎯 Casos de Uso

### Caso 1: Análisis Rápido de Testimonio
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --analyze-sentiment \
  --output json
```

### Caso 2: Generar Contenido para Múltiples Plataformas
```bash
# Generar para Instagram
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --platform instagram \
  --generate-formats \
  --output json > instagram.json

# Generar para LinkedIn
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --platform linkedin \
  --output json > linkedin.json
```

### Caso 3: A/B Testing de Publicaciones
```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA]" \
  --variations 4 \
  --ab-testing \
  --output json > ab_test_variants.json
```

### Caso 4: Procesamiento en Lote con Cache
```bash
# Procesar múltiples testimonios con cache habilitado
for testimonial in testimonios/*.json; do
  python scripts/testimonial_to_social_post.py \
    --file "$testimonial" \
    --enable-cache \
    --cache-file ./cache/testimonials.json \
    --output json >> resultados.jsonl
done
```

## 🔍 Análisis de Resultados

### Interpretación del Análisis de Sentimiento

- **Score > 0.2**: Sentimiento positivo fuerte
- **Score 0.0 - 0.2**: Sentimiento neutral-positivo
- **Score -0.2 - 0.0**: Sentimiento neutral-negativo
- **Score < -0.2**: Sentimiento negativo

### Intensidad Emocional

- **0.0 - 0.3**: Baja intensidad (tono profesional)
- **0.3 - 0.6**: Intensidad media (tono balanceado)
- **0.6 - 1.0**: Alta intensidad (tono emocional)

## 🛠️ Personalización Avanzada

### Crear Template Personalizado

1. Crea un archivo JSON en `n8n/templates/`
2. Define la estructura y ejemplos
3. Usa el template con `--template nombre_template`

### Configurar Cache Personalizado

```python
from testimonial_to_social_post import TestimonialToSocialPostConverter

converter = TestimonialToSocialPostConverter()
converter.enable_cache(
    cache_file="./mi_cache.json",
    max_size=200  # Máximo 200 entradas
)
```

## 📈 Mejoras de Rendimiento

- **Cache**: Reduce llamadas a OpenAI para testimonios similares
- **Análisis local**: Análisis de sentimiento sin llamadas a API
- **Procesamiento en batch**: Usa `--file` para procesar múltiples testimonios

## 🐛 Troubleshooting

### Error: "Funcionalidades avanzadas no disponibles"
**Solución**: Asegúrate de que `testimonial_advanced_features.py` esté en el mismo directorio que el script principal.

### Cache no funciona
**Solución**: Verifica que tengas permisos de escritura en el directorio del archivo de cache.

### Template no encontrado
**Solución**: Verifica que el archivo JSON del template esté en `n8n/templates/` y tenga el formato correcto.

## 📝 Notas

- Las funcionalidades avanzadas son opcionales y no requieren dependencias adicionales
- El análisis de sentimiento es básico pero efectivo para la mayoría de casos
- El cache mejora significativamente el rendimiento en procesamiento en lote
- Los templates se cargan automáticamente desde `n8n/templates/`


