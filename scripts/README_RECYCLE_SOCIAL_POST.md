# 🔄 Reciclador de Publicaciones Sociales - Versión Mejorada

Script mejorado para reciclar publicaciones antiguas de redes sociales y generar 3 versiones nuevas: post estático, video corto e historia.

## ✨ Nuevas Mejoras v2.0

### Análisis Avanzado
- ✅ **Análisis inteligente del contenido**: Detecta tipo, tono, tema principal y palabras clave
- ✅ **Métricas de engagement estimadas**: Score, likes, comentarios, compartidos y alcance potencial
- ✅ **Detección de mejor versión**: Compara las 3 versiones y recomienda la mejor

### Generación de Contenido
- ✅ **Múltiples variaciones**: Genera 3 captions/scripts diferentes por formato
- ✅ **Hashtags inteligentes**: Basados en análisis del contenido y tema
- ✅ **Hashtags trending**: Sugerencias de hashtags populares por tema
- ✅ **Prompts para imágenes con IA**: Genera prompts listos para DALL-E, Midjourney, etc.

### Optimización
- ✅ **Sugerencias de visuales personalizadas**: Según el tema y tipo de contenido
- ✅ **Mejor momento para publicar**: Optimizado según el tipo de contenido
- ✅ **Sugerencias de música**: Para videos según el tono del contenido
- ✅ **Sugerencias de contenido relacionado**: Ideas para futuras publicaciones

### Exportación
- ✅ **Múltiples formatos**: JSON, Markdown, CSV o todos a la vez
- ✅ **Análisis completo**: Incluye métricas, prompts y recomendaciones

### IA
- ✅ **Opción de IA**: Soporte opcional para OpenAI (con `--use-ai`)

## 🚀 Uso Rápido

### Uso Básico

```bash
python3 scripts/recycle_social_post.py "[TEXTO DE TU PUBLICACIÓN ANTIGUA]"
```

### Con Opciones Avanzadas

```bash
# Usar IA para generar contenido más creativo
python3 scripts/recycle_social_post.py "Tu publicación" --use-ai

# Especificar archivo de salida
python3 scripts/recycle_social_post.py "Tu publicación" --output resultado.json

# Usar API key específica
python3 scripts/recycle_social_post.py "Tu publicación" --use-ai --openai-key sk-...
```

### Ejemplos

```bash
# Ejemplo básico
python3 scripts/recycle_social_post.py "La automatización puede ahorrarte hasta 10 horas semanales. #Productividad #IA"

# Con IA
python3 scripts/recycle_social_post.py "Tu publicación aquí" --use-ai

# Con salida personalizada
python3 scripts/recycle_social_post.py "Tu publicación" -o mi_resultado.json
```

## 📋 Qué Genera

El script genera **3 versiones recicladas** de tu publicación:

### A) 📸 Post Estático
- Caption optimizado para Instagram Feed / LinkedIn
- Hashtags sugeridos
- Sugerencias de capturas/visuales
- Mejores prácticas de publicación

### B) 🎬 Video Corto
- Script completo para video (15-60 segundos)
- Caption para Instagram Reels / TikTok / YouTube Shorts
- Hashtags optimizados para videos
- Sugerencias de visuales y edición
- Mejores prácticas para videos virales

### C) 📱 Historia
- Estructura de slides (4-7 slides)
- Contenido para cada slide
- Sugerencias de diseño visual
- Hashtags para stories
- Mejores prácticas de engagement

## 🎯 Características Mejoradas

### Análisis Inteligente
- ✅ **Detección de tipo de contenido**: Tutorial, tip, fact, opinion, question, general
- ✅ **Análisis de tono**: Positive, curious, analytical, neutral
- ✅ **Detección de tema principal**: Productividad, tecnología, negocios, educación, IA, automatización
- ✅ **Extracción de palabras clave**: Identifica términos más relevantes
- ✅ **Análisis de estructura**: Detecta preguntas, números, emojis, etc.

### Generación de Contenido
- ✅ **Múltiples variaciones**: 3 captions diferentes para posts estáticos
- ✅ **Scripts variados**: 3 scripts diferentes para videos cortos
- ✅ **Slides optimizados**: Historias con estructura inteligente y stickers interactivos
- ✅ **Hooks adaptativos**: Selecciona hooks según tipo de contenido
- ✅ **CTAs personalizados**: Múltiples opciones de llamadas a la acción

### Optimización
- ✅ **Hashtags inteligentes**: Basados en tema, tipo y tono del contenido
- ✅ **Sugerencias de visuales**: Personalizadas según tema y tipo de contenido
- ✅ **Mejor momento para publicar**: Optimizado según audiencia y tipo de contenido
- ✅ **Sugerencias de música**: Para videos según el tono
- ✅ **Duración estimada**: Calcula duración aproximada de videos

### Mejores Prácticas
- ✅ **Recomendaciones específicas**: Por formato y tipo de contenido
- ✅ **Tips de engagement**: Basados en mejores prácticas de redes sociales
- ✅ **Guías de diseño**: Especificaciones técnicas y visuales

## 📁 Archivos Generados

El script genera un archivo JSON con timestamp:
- `recycled_post_YYYYMMDD_HHMMSS.json`

Este archivo contiene toda la información estructurada para referencia futura.

## 💡 Tips de Uso

1. **Publicaciones largas**: El script crea resúmenes con hooks llamativos
2. **Publicaciones cortas**: Expande el contenido con contexto y reflexiones
3. **Hashtags**: Conserva hashtags originales relevantes y añade nuevos trending
4. **Personalización**: Puedes editar los captions generados antes de publicar

## 🔧 Personalización

Para personalizar el script:

1. Edita las funciones `generate_static_post()`, `generate_short_video()`, `generate_story()`
2. Modifica los templates de captions según tu tono de voz
3. Ajusta los hashtags según tu nicho/audiencia
4. Personaliza las sugerencias de visuales según tus recursos

## 📊 Ejemplo de Salida Mejorada

El script ahora incluye:

```
================================================================================
🔄 RECICLAJE DE PUBLICACIÓN SOCIAL - VERSIÓN MEJORADA
================================================================================

📅 Fecha: [timestamp]

📝 Publicación Original: [tu publicación]

🔍 ANÁLISIS DEL CONTENIDO:
   📊 Tipo: [tipo detectado]
   🎭 Tono: [tono detectado]
   🏷️ Tema principal: [tema detectado]
   📝 Palabras clave: [keywords extraídas]
   📏 Longitud: [estadísticas]

📸 A) POST ESTÁTICO
   ⏰ Mejor momento para publicar: [horario optimizado]
   📝 CAPTIONS (3 variaciones): [3 opciones diferentes]
   ⭐ RECOMENDADA: [caption sugerido]
   🏷️ HASHTAGS: [hashtags inteligentes]
   🎨 SUGERENCIAS DE CAPTURAS/VISUALES: [personalizadas]
   💡 MEJORES PRÁCTICAS: [específicas]

🎬 B) VIDEO CORTO
   ⏱️ Duración estimada: [calculada]
   ⏰ Mejor momento para publicar: [optimizado]
   📝 SCRIPTS (3 variaciones): [3 opciones]
   ⭐ RECOMENDADO: [script sugerido]
   🎵 SUGERENCIAS DE MÚSICA: [según tono]
   🎨 SUGERENCIAS DE CAPTURAS/VISUALES: [específicas]
   💡 MEJORES PRÁCTICAS: [detalladas]

📱 C) HISTORIA
   📑 SLIDES: [estructura optimizada]
   ⏰ Mejor momento para publicar: [optimizado]
   🎭 Stickers interactivos: [sugeridos]
   🏷️ HASHTAGS: [optimizados]
   💡 MEJORES PRÁCTICAS: [completas]
```

## 🔧 Opciones Avanzadas

### Modo IA (OpenAI)

Para usar IA y generar contenido aún más creativo:

```bash
# Requiere OPENAI_API_KEY en variables de entorno
export OPENAI_API_KEY="sk-..."
python3 scripts/recycle_social_post.py "Tu publicación" --use-ai

# O especificar la key directamente
python3 scripts/recycle_social_post.py "Tu publicación" --use-ai --openai-key sk-...
```

### Archivo de Salida Personalizado

```bash
python3 scripts/recycle_social_post.py "Tu publicación" --output mi_resultado.json
```

## 📋 Parámetros Disponibles

- `post`: Texto de la publicación antigua (requerido)
- `--use-ai`: Usar IA para generar contenido más creativo
- `--output`, `-o`: Archivo de salida personalizado
- `--format`, `-f`: Formato de exportación (`json`, `markdown`, `csv`, `all`)
- `--openai-key`: API key de OpenAI (alternativa a variable de entorno)

### Ejemplos de Uso con Formatos

```bash
# Exportar solo a JSON (por defecto)
python3 scripts/recycle_social_post.py "Tu publicación" -o resultado.json

# Exportar a Markdown
python3 scripts/recycle_social_post.py "Tu publicación" --format markdown -o resultado.md

# Exportar a CSV
python3 scripts/recycle_social_post.py "Tu publicación" --format csv -o resultado.csv

# Exportar a todos los formatos
python3 scripts/recycle_social_post.py "Tu publicación" --format all -o resultado
```

## 🎯 Nuevas Funcionalidades Detalladas

### 📊 Métricas de Engagement

El script ahora estima métricas de engagement para cada versión:
- **Score de Engagement** (0-100): Basado en factores como preguntas, números, emojis, tipo de contenido
- **Likes estimados**: Proyección basada en el score
- **Comentarios estimados**: Estimación de interacción
- **Compartidos estimados**: Proyección de viralidad
- **Alcance estimado**: Estimación de alcance potencial

### 🎨 Prompts para Imágenes con IA

Genera prompts listos para usar en herramientas de IA como:
- DALL-E
- Midjourney
- Stable Diffusion
- Canva AI

Cada prompt está personalizado según el tema y tipo de contenido.

### 💡 Sugerencias de Contenido Relacionado

Genera ideas para futuras publicaciones basadas en:
- Temas relacionados
- Formatos sugeridos
- Ideas de contenido específicas

### 🔥 Hashtags Trending

Sugiere hashtags populares y trending según el tema principal del contenido.

### ⭐ Resumen y Recomendación

Al final del análisis, el script:
- Identifica la mejor versión según engagement estimado
- Proporciona recomendación de acción específica
- Sugiere el formato más adecuado para el contenido

## 🎨 Próximas Mejoras

- [x] Análisis inteligente del contenido
- [x] Múltiples variaciones de captions
- [x] Hashtags inteligentes
- [x] Sugerencias personalizadas de visuales
- [x] Mejor momento para publicar optimizado
- [x] Soporte opcional de IA
- [x] Métricas de engagement estimadas
- [x] Prompts para imágenes con IA
- [x] Sugerencias de contenido relacionado
- [x] Exportación a múltiples formatos (JSON, Markdown, CSV)
- [x] Hashtags trending
- [x] Análisis comparativo de versiones
- [ ] Integración completa con OpenAI para contenido más creativo
- [ ] Templates personalizables por industria/niche
- [ ] Análisis de engagement de publicaciones originales (retroalimentación)
- [ ] Generación automática de imágenes con IA (integración directa)
- [ ] Integración con herramientas de scheduling (Buffer, Hootsuite)
- [ ] Análisis de competencia y benchmarking
- [ ] Predicción de mejor momento histórico basado en datos reales

---

**Creado para**: Optimización de contenido en redes sociales  
**Versión**: 2.0 Mejorada (con métricas, prompts IA, y exportación múltiple)  
**Última actualización**: Noviembre 2025

## 📈 Ejemplo de Salida Completa

El script ahora genera:

1. **Análisis del contenido** con tipo, tono, tema y palabras clave
2. **3 versiones completas** (Post, Video, Historia) con múltiples variaciones cada una
3. **Métricas de engagement** estimadas para cada versión
4. **Prompts para imágenes** listos para usar con IA
5. **Sugerencias de contenido relacionado** para futuras publicaciones
6. **Hashtags trending** personalizados
7. **Resumen y recomendación** de la mejor versión

Todo exportable en JSON, Markdown o CSV para fácil integración con otras herramientas.

