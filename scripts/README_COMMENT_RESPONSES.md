# Generador de Respuestas a Comentarios

Script mejorado para generar respuestas amigables y personalizadas a comentarios típicos en publicaciones de redes sociales.

## ✨ Mejoras Implementadas

### 🎯 Detección Inteligente de Tipos de Comentarios
- **10 tipos diferentes** de comentarios detectados automáticamente:
  - Interés/Curiosidad
  - Cómo empezar
  - Dificultad/Nivel
  - Precio
  - Comparación
  - Testimonial
  - Duda técnica
  - Objeción
  - Compartir experiencia
  - Genérico

### 🧠 Sistema de Detección Mejorado
- Detección basada en patrones con expresiones regulares
- Sistema de puntuación y confianza
- Extracción de contexto del comentario
- Respuestas adaptadas según el tipo detectado

### 💬 Respuestas Más Naturales
- Menciones genéricas al usuario (opcional)
- Variaciones automáticas de respuestas
- Tono amigable y cercano
- Preguntas que fomentan más conversación

### 📊 Información Detallada
- Tipo de comentario detectado
- Nivel de confianza de la detección
- Contexto extraído del comentario
- Metadatos de generación

## 🚀 Uso Básico

```bash
# Generar respuestas con tema personalizado
python3 scripts/generate_comment_responses.py "tu tema aquí" --output text

# Con comentarios específicos
python3 scripts/generate_comment_responses.py "marketing digital" \
  --comentarios "Me encanta" "¿Cuánto cuesta?" "¿Funciona para mi negocio?"

# Salida en JSON
python3 scripts/generate_comment_responses.py "tecnología" --output json

# Con detalles de detección
python3 scripts/generate_comment_responses.py "videos de IA" \
  --output text --mostrar-detalles

# Sin menciones al usuario
python3 scripts/generate_comment_responses.py "tu tema" \
  --sin-mencion-usuario --output text
```

## 📝 Ejemplos de Respuestas Generadas

### Comentario de Interés
**Comentario:** "¡Muy interesante! ¿Cómo funciona esto?"
**Respuesta:** "¡Hola! ¡Gracias por tu interés! Nos encanta saber que te gusta nuestro contenido sobre videos de IA. ¿Hay algo específico que te gustaría saber más? Estamos aquí para ayudarte. 😊"

### Pregunta sobre Cómo Empezar
**Comentario:** "¿Cómo puedo empezar a crear videos con IA?"
**Respuesta:** "¡Nos encanta tu entusiasmo! Empezar con videos de IA puede ser más fácil de lo que piensas. ¿Qué te gustaría lograr específicamente? Con eso en mente, podemos sugerirte los mejores recursos para comenzar. 💡"

### Pregunta sobre Precio
**Comentario:** "¿Cuánto cuesta usar esta herramienta?"
**Respuesta:** "¡Entendemos tu interés! Sobre el precio de videos de IA, tenemos diferentes opciones que se adaptan a distintas necesidades. ¿Te gustaría que te compartamos más detalles sobre nuestros planes? Podemos encontrar la opción que mejor se ajuste a lo que buscas. 💰"

## 🎨 Características

- ✅ Detección automática de intención del comentario
- ✅ Respuestas personalizadas según el tipo
- ✅ Variaciones naturales de respuestas
- ✅ Menciones genéricas al usuario (configurable)
- ✅ Tono amigable y conversacional
- ✅ Preguntas que fomentan más interacción
- ✅ Soporte para múltiples temas
- ✅ Exportación en JSON o texto

## 📋 Opciones Disponibles

- `tema`: Tema de las publicaciones (requerido)
- `--comentarios`: Lista de comentarios específicos a los que responder
- `--tono`: Tono de la marca (default: "amigable y cercano")
- `--output`: Formato de salida (`json` o `text`)
- `--archivo`: Archivo JSON con comentarios personalizados
- `--sin-mencion-usuario`: No incluir menciones genéricas al usuario
- `--mostrar-detalles`: Mostrar detalles de detección (tipo, confianza, contexto)

## 📄 Formato de Archivo JSON

Si quieres usar un archivo con comentarios personalizados:

```json
{
  "comentarios": [
    "Comentario 1",
    "Comentario 2",
    "Comentario 3"
  ]
}
```

## 🔧 Ejemplos Avanzados

```bash
# Con archivo de comentarios
python3 scripts/generate_comment_responses.py "tu tema" \
  --archivo comentarios.json --output json

# Tono profesional
python3 scripts/generate_comment_responses.py "tecnología" \
  --tono "profesional y empático" --output text

# Solo respuestas simples
python3 scripts/generate_comment_responses.py "marketing" \
  --output json | jq '.respuestas[].respuesta'
```

## 🎯 Tipos de Comentarios Soportados

1. **Interés** - Expresiones de interés o curiosidad
2. **Cómo empezar** - Preguntas sobre iniciación
3. **Dificultad** - Consultas sobre nivel de complejidad
4. **Precio** - Preguntas sobre costos
5. **Comparación** - Comparaciones con otras opciones
6. **Testimonial** - Experiencias positivas compartidas
7. **Duda técnica** - Preguntas técnicas específicas
8. **Objeción** - Preocupaciones o dudas
9. **Compartir experiencia** - Usuarios compartiendo su uso
10. **Genérico** - Cualquier otro tipo de comentario

## 💡 Tips de Uso

- Usa `--mostrar-detalles` para entender cómo se detectan los comentarios
- Personaliza el tema para que las respuestas sean más relevantes
- Combina con otros scripts para automatizar respuestas en redes sociales
- Exporta a JSON para integrar con sistemas de gestión de redes sociales


