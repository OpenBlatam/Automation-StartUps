# Testimonial to Social Post Converter

Sistema para convertir testimonios de clientes en publicaciones narrativas optimizadas para redes sociales, enfocadas en resultados y con tono cálido y profesional.

## 🎯 Funcionalidades

- ✅ **Conversión inteligente** de testimonios en publicaciones narrativas
- ✅ **Enfoque en resultados** - Destaca los resultados obtenidos por el cliente
- ✅ **Optimización por plataforma** - Instagram, Facebook, LinkedIn, Twitter, TikTok
- ✅ **Tono personalizable** - Cálido, profesional, inspirador, etc.
- ✅ **Generación de variaciones** - Múltiples versiones para A/B testing
- ✅ **Hashtags automáticos** - Generación de hashtags relevantes
- ✅ **CTAs integrados** - Llamadas a la acción naturales
- ✅ **Control de longitud** - Respeta límites de caracteres por plataforma

## 📋 Requisitos Previos

### 1. Dependencias Python

```bash
pip install openai
```

O desde el archivo de requirements del proyecto:

```bash
pip install -r requirements.txt
```

### 2. API Key de OpenAI

Configura la variable de entorno:

```bash
export OPENAI_API_KEY=tu_api_key_de_openai
```

O pásala como parámetro al script.

## 🚀 Uso Básico

### Desde línea de comandos

```bash
python scripts/testimonial_to_social_post.py \
  "[TEXTO DEL TESTIMONIO]" \
  "[PROBLEMA/RESULTADO QUE BUSCA EL PÚBLICO]" \
  --platform instagram \
  --tone "cálido y profesional"
```

### Ejemplo completo

```bash
python scripts/testimonial_to_social_post.py \
  "Antes de usar este servicio, estaba perdiendo clientes constantemente. Ahora tengo una tasa de retención del 95% y mis ingresos han aumentado un 40% en solo 3 meses. No puedo creer la diferencia que ha hecho." \
  "mejorar la retención de clientes y aumentar ingresos" \
  --platform linkedin \
  --tone "profesional y empático" \
  --output json
```

### Generar múltiples variaciones

```bash
python scripts/testimonial_to_social_post.py \
  "[TESTIMONIO]" \
  "[PROBLEMA/RESULTADO]" \
  --platform instagram \
  --variations 3
```

## 🔧 Integración con n8n

### Opción 1: Usar API REST (Recomendado)

La forma más fácil y robusta es usar la API REST Flask incluida:

1. **Iniciar la API**:
```bash
cd scripts
pip install -r requirements_testimonial.txt
python testimonial_api.py
```

2. **Configurar variable de entorno en n8n**:
   - `TESTIMONIAL_API_URL`: URL de la API (default: http://localhost:5000)

3. **Importar workflow**: Usa `n8n_workflow_testimonial_mejorado.json` que ya incluye la integración con la API.

### Opción 2: Usar Code Node (Python)

1. **Agregar un nodo Code** en tu workflow
2. **Seleccionar Python** como lenguaje
3. **Configurar el código**:

```python
import subprocess
import json
import os

# Obtener datos del nodo anterior
testimonial = $input.item.json.testimonial
target_audience = $input.item.json.target_audience
platform = $input.item.json.platform or "general"
tone = $input.item.json.tone or "cálido y profesional"

# Configurar API key
os.environ['OPENAI_API_KEY'] = $env.OPENAI_API_KEY

# Ejecutar el script
script_path = "/Users/adan/IA/scripts/testimonial_to_social_post.py"

result = subprocess.run(
    [
        "python3",
        script_path,
        testimonial,
        target_audience,
        "--platform", platform,
        "--tone", tone,
        "--output", "json"
    ],
    capture_output=True,
    text=True,
    check=True
)

# Parsear resultado
post_data = json.loads(result.stdout)

return {
    json: {
        post_content: post_data["post_content"],
        full_post: post_data["full_post"],
        hashtags: post_data["hashtags"],
        call_to_action: post_data["call_to_action"],
        platform: post_data["platform"],
        length: post_data["length"]
    }
}
```

### Opción 3: Usar Execute Command Node

1. **Agregar nodo Execute Command**
2. **Comando**:
```bash
python3 /Users/adan/IA/scripts/testimonial_to_social_post.py \
  "$(echo '{{ $json.testimonial }}')" \
  "$(echo '{{ $json.target_audience }}')" \
  --platform {{ $json.platform || 'general' }} \
  --output json
```

## 📊 Workflow Completo de Ejemplo

### Flujo sugerido:

1. **Webhook Trigger** - Recibe testimonio y parámetros
2. **Set Node** - Estructura los datos:
   ```json
   {
     "testimonial": "{{ $json.testimonial }}",
     "target_audience": "{{ $json.target_audience }}",
     "platform": "{{ $json.platform || 'general' }}",
     "tone": "{{ $json.tone || 'cálido y profesional' }}"
   }
   ```
3. **Code Node** - Ejecuta la conversión (usar código de Opción 1)
4. **IF Node** - Valida que la publicación se generó correctamente
5. **Split In Batches** - Si generaste múltiples variaciones
6. **Social Media Nodes** - Publica en cada plataforma:
   - Instagram Node
   - Facebook Node
   - LinkedIn Node
   - Twitter Node
7. **Telegram/Slack Node** - Notifica el resultado

## 🎨 Personalización por Plataforma

### Instagram
- Longitud: 2200 caracteres máximo
- Hashtags: 5-10 recomendados
- Emojis: Sí
- Formato: Con saltos de línea

### Facebook
- Longitud: 5000 caracteres máximo
- Hashtags: 3-5 recomendados
- Emojis: Sí
- Formato: Con saltos de línea

### LinkedIn
- Longitud: 3000 caracteres máximo
- Hashtags: 5 recomendados
- Emojis: Mínimos
- Tono: Más profesional

### Twitter/X
- Longitud: 280 caracteres máximo
- Hashtags: 2-3 recomendados
- Emojis: Sí
- Formato: Texto continuo

### TikTok
- Longitud: 300 caracteres máximo
- Hashtags: 5-10 recomendados
- Emojis: Sí
- Formato: Con saltos de línea

## 📝 Ejemplos de Uso

### Ejemplo 1: Testimonio de E-commerce

**Input**:
```json
{
  "testimonial": "Compré este producto hace un mes y ya he visto resultados increíbles. Mi piel se ve más joven y radiante. Mis amigos me preguntan qué estoy usando. Definitivamente lo recomiendo.",
  "target_audience": "mejorar la apariencia de la piel y verse más joven",
  "platform": "instagram"
}
```

**Output esperado**: Publicación narrativa enfocada en resultados visibles, con hashtags de skincare y belleza.

### Ejemplo 2: Testimonio de Servicio B2B

**Input**:
```json
{
  "testimonial": "Implementamos esta solución hace 6 meses y nuestra productividad aumentó un 60%. El ROI fue evidente desde el primer mes. El equipo está más motivado y los clientes están más satisfechos.",
  "target_audience": "aumentar productividad y mejorar ROI",
  "platform": "linkedin",
  "tone": "profesional y empático"
}
```

**Output esperado**: Publicación profesional enfocada en métricas y resultados empresariales.

## 🔍 Parámetros Disponibles

| Parámetro | Descripción | Valores | Default |
|-----------|-------------|---------|---------|
| `testimonial` | Texto del testimonio | String | Requerido |
| `target_audience` | Problema/resultado buscado | String | Requerido |
| `platform` | Plataforma objetivo | general, instagram, facebook, linkedin, twitter, tiktok | general |
| `tone` | Tono deseado | String | "cálido y profesional" |
| `max_length` | Longitud máxima | Integer | Según plataforma |
| `include_hashtags` | Incluir hashtags | Boolean | true |
| `include_call_to_action` | Incluir CTA | Boolean | true |

## 🛠️ Troubleshooting

### Error: OPENAI_API_KEY no está configurada
**Solución**: Configura la variable de entorno o pásala como parámetro `--api-key`

### Error: La publicación excede la longitud máxima
**Solución**: El script intenta acortar automáticamente, pero puedes ajustar `--max-length`

### Error: No se generan hashtags
**Solución**: Verifica que `include_hashtags` esté en `true` y que el prompt incluya la solicitud de hashtags

## 📈 Mejoras Futuras

- [ ] Integración directa con APIs de redes sociales
- [ ] Análisis de sentimiento del testimonio
- [ ] Sugerencias de imágenes basadas en el contenido
- [ ] Programación automática de publicaciones
- [ ] Analytics de engagement por variación
- [ ] Traducción automática a múltiples idiomas
- [ ] Generación de contenido multimedia (carousel, video scripts)

## 📄 Licencia

Este script es parte del proyecto IA y sigue las mismas políticas de licencia.
