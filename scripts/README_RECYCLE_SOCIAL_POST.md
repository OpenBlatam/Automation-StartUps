# 🔄 Reciclador de Publicaciones Sociales

Script para reciclar publicaciones antiguas de redes sociales y generar 3 versiones nuevas: post estático, video corto e historia.

## 🚀 Uso Rápido

```bash
python3 scripts/recycle_social_post.py "[TEXTO DE TU PUBLICACIÓN ANTIGUA]"
```

### Ejemplo

```bash
python3 scripts/recycle_social_post.py "La automatización puede ahorrarte hasta 10 horas semanales. ¿Qué proceso de tu negocio te gustaría automatizar primero? #Productividad #IA"
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

## 🎯 Características

- ✅ Extrae automáticamente hashtags, menciones y URLs de la publicación original
- ✅ Adapta el contenido según la longitud del texto original
- ✅ Genera captions optimizados para cada formato
- ✅ Sugiere hashtags relevantes y trending
- ✅ Incluye mejores prácticas de publicación
- ✅ Guarda resultado en JSON para referencia futura

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

## 📊 Ejemplo de Salida

```
================================================================================
🔄 RECICLAJE DE PUBLICACIÓN SOCIAL
================================================================================

📅 Fecha: 2025-11-12 09:37:21

📝 Publicación Original:
   [Tu publicación aquí]

📸 A) POST ESTÁTICO
   - Caption completo
   - Hashtags sugeridos
   - Sugerencias visuales
   - Mejores prácticas

🎬 B) VIDEO CORTO
   - Script completo
   - Caption optimizado
   - Hashtags para video
   - Sugerencias de edición

📱 C) HISTORIA
   - Estructura de slides
   - Contenido por slide
   - Diseño sugerido
   - Tips de engagement
```

## 🎨 Próximas Mejoras

- [ ] Integración con APIs de IA para generar contenido más inteligente
- [ ] Templates personalizables por industria/niche
- [ ] Análisis de engagement de publicaciones originales
- [ ] Generación automática de imágenes con IA
- [ ] Integración con herramientas de scheduling (Buffer, Hootsuite)

---

**Creado para**: Optimización de contenido en redes sociales  
**Versión**: 1.0

