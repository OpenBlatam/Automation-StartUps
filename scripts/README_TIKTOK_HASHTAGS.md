# 🎯 Generador Avanzado de Hashtags para TikTok

Herramienta avanzada para generar hashtags personalizados y actualizados para publicaciones en TikTok basados en tu industria y público objetivo. Incluye sistema de scoring inteligente, análisis de rendimiento y recomendaciones personalizadas.

## 🚀 Uso Rápido

```bash
python3 tiktok_hashtag_generator.py --industry [INDUSTRIA] --demographic [DEMOGRAFIA]
```

## 📋 Industrias Disponibles

- `tech` - Tecnología
- `ecommerce` - E-commerce
- `marketing` - Marketing
- `fitness` - Fitness
- `food` - Comida
- `education` - Educación
- `beauty` - Belleza
- `finance` - Finanzas
- `automation` - Automatización
- `ai` - Inteligencia Artificial
- `gaming` - Gaming
- `travel` - Viajes
- `business` - Negocios

## 👥 Demografías Disponibles

- `gen_z` - Generación Z
- `millennial` - Millennials
- `tech_savvy` - Tech-savvy
- `entrepreneurs` - Emprendedores
- `creators` - Creadores de contenido
- `professionals` - Profesionales
- `students` - Estudiantes
- `parents` - Padres

## 💡 Ejemplos

### Ejemplo 1: Tech + Gen Z
```bash
python3 tiktok_hashtag_generator.py --industry tech --demographic gen_z
```

**Output:**
- #TechTok #TechTips #CodeTok #DevLife #GenZ #Zoomer #BehindTheScenes #DayInTheLife #BeforeAndAfter #FYP

### Ejemplo 2: Con keywords personalizadas
```bash
python3 tiktok_hashtag_generator.py \
  --industry automation \
  --demographic tech_savvy \
  --keywords "AI" "Machine Learning" \
  --count 12
```

### Ejemplo 3: Con análisis de rendimiento y scores
```bash
python3 tiktok_hashtag_generator.py \
  --industry automation \
  --demographic tech_savvy \
  --scores \
  --analyze
```

### Ejemplo 4: Con tipo de contenido y duración
```bash
python3 tiktok_hashtag_generator.py \
  --industry tech \
  --demographic gen_z \
  --content-type tutorial \
  --video-length short \
  --count 12
```

### Ejemplo 5: Salida JSON completa
```bash
python3 tiktok_hashtag_generator.py \
  --industry marketing \
  --demographic entrepreneurs \
  --scores \
  --analyze \
  --json
```

## ✨ Características Avanzadas

- ✅ **10+ hashtags principales** personalizados por industria y demografía
- ✅ **3+ combinaciones únicas** no genéricas incluidas
- ✅ **Hashtags trending 2024-2025** actualizados constantemente
- ✅ **Sistema de scoring inteligente** que evalúa relevancia, tendencia, competencia y engagement
- ✅ **Análisis de rendimiento** con recomendaciones personalizadas
- ✅ **Keywords personalizadas** para mayor relevancia
- ✅ **Soporte para tipo de contenido** (tutorial, review, etc.)
- ✅ **Optimización por duración** de video (short, medium, long)
- ✅ **Salida en texto o JSON** según necesidades
- ✅ **20+ combinaciones únicas** disponibles

## 🔗 Combinaciones Únicas

El generador incluye al menos 3 combinaciones únicas que no son genéricas:

1. **#BehindTheScenes #Process #HowItsMade**
2. **#DayInTheLife #Routine #DailyLife**
3. **#BeforeAndAfter #Transformation #Results**
4. **#ProTip #Hack #LifeHack**
5. **#TrendingNow #Viral #Trending**
6. Y más...

## 📊 Parámetros

- `--industry`: Industria objetivo (requerido)
- `--demographic`: Demografía objetivo (requerido)
- `--keywords`: Palabras clave personalizadas (opcional)
- `--count`: Número de hashtags a generar (default: 10)
- `--scores`: Incluir scores detallados de cada hashtag (opcional)
- `--analyze`: Analizar rendimiento potencial de los hashtags (opcional)
- `--content-type`: Tipo de contenido: tutorial, review, behind_scenes, etc. (opcional)
- `--video-length`: Duración del video: short, medium, long (opcional)
- `--json`: Salida en formato JSON (opcional)

## 📝 Notas

- Los hashtags se generan usando un sistema de scoring inteligente que evalúa:
  - **Relevancia** (30%): Qué tan relevante es para tu industria/demografía
  - **Tendencia** (25%): Qué tan trending es el hashtag
  - **Competencia** (25%): Nivel de competencia (menor es mejor)
  - **Engagement** (20%): Potencial de engagement
- Se incluyen automáticamente combinaciones únicas no genéricas
- El generador optimiza los hashtags por score total para mejor rendimiento
- El análisis de rendimiento proporciona recomendaciones personalizadas

## 🎯 Sistema de Scoring

Cada hashtag recibe un score de 0-1 basado en:
- **Relevancia**: Match con industria y demografía
- **Trend Score**: Inclusión en hashtags trending 2024-2025
- **Competition Score**: Nivel de competencia (invertido para scoring)
- **Engagement Potential**: Potencial de engagement basado en patrones

El score total es un promedio ponderado de estos factores.

## 📈 Análisis de Rendimiento

El análisis incluye:
- Score promedio de todos los hashtags
- Categorización por rendimiento (alto/medio/bajo)
- Recomendaciones personalizadas para mejorar

---

**Versión**: 1.0  
**Última actualización**: 2024

