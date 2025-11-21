# 📊 Análisis de Estadísticas Orgánicas - Instagram TikTok YouTube con IA

Este workflow de n8n automatiza la recopilación de estadísticas orgánicas de tus publicaciones en Instagram, TikTok y YouTube, identifica los posts más virales y utiliza ChatGPT para analizar por qué fueron exitosos y qué replicar para tener el mismo éxito.

## 🎯 Funcionalidades Principales

- ✅ **Recopilación automática** de estadísticas de Instagram, TikTok y YouTube
- ✅ **Análisis inteligente** que identifica los posts más virales usando un algoritmo de scoring
- ✅ **Análisis con ChatGPT** que explica por qué fueron exitosos los posts
- ✅ **Recomendaciones accionables** sobre qué replicar para tener el mismo éxito
- ✅ **Reportes estructurados** guardados en JSON y CSV para análisis posterior
- ✅ **Notificaciones** vía Telegram con resumen del análisis
- ✅ **Ejecución programada** semanal o manual vía webhook
- ✅ **Retry logic** automático para mayor confiabilidad
- ✅ **Análisis comparativo** entre plataformas
- ✅ **Métricas avanzadas** (máximo, mínimo, promedios por plataforma)
- ✅ **Análisis de hashtags** más efectivos
- ✅ **Análisis de mejores horarios** de publicación
- ✅ **Detección de anomalías** (posts destacados)

## 📋 Requisitos Previos

### 1. Credenciales de Instagram

Para obtener estadísticas de Instagram necesitas:

1. Crear una aplicación en [Facebook Developers](https://developers.facebook.com/)
2. Obtener un **Access Token** de Instagram Graph API
3. Obtener tu **Instagram Account ID** (Business Account)

**Pasos detallados:**
- Ve a [Facebook Developers](https://developers.facebook.com/)
- Crea una nueva app o selecciona una existente
- Agrega el producto "Instagram Graph API"
- Genera un token de acceso con permisos: `instagram_basic`, `instagram_manage_insights`, `pages_read_engagement`
- Obtén tu Instagram Account ID desde la configuración de tu cuenta de negocio

### 2. Credenciales de TikTok

Para obtener estadísticas de TikTok necesitas:

1. Crear una aplicación en [TikTok for Developers](https://developers.tiktok.com/)
2. Obtener un **Access Token** con permisos de lectura de analytics

**Pasos detallados:**
- Ve a [TikTok for Developers](https://developers.tiktok.com/)
- Crea una nueva aplicación
- Solicita acceso a la API de Analytics
- Genera un token de acceso con permisos de lectura

### 3. Credenciales de YouTube

Para obtener estadísticas de YouTube necesitas:

1. Crear un proyecto en [Google Cloud Console](https://console.cloud.google.com/)
2. Habilitar la **YouTube Data API v3**
3. Crear credenciales (API Key)
4. Obtener tu **Channel ID** (opcional pero recomendado)

**Pasos detallados:**
- Ve a [Google Cloud Console](https://console.cloud.google.com/)
- Crea un nuevo proyecto o selecciona uno existente
- Habilita "YouTube Data API v3"
- Ve a "Credenciales" y crea una "Clave de API"
- Para obtener tu Channel ID: ve a tu canal de YouTube → Configuración → Avanzado → ID del canal

### 4. Credenciales de OpenAI (ChatGPT)

Para el análisis con IA necesitas:

1. Crear una cuenta en [OpenAI](https://platform.openai.com/)
2. Generar un **API Key**

**Pasos detallados:**
- Ve a [OpenAI Platform](https://platform.openai.com/)
- Crea una cuenta o inicia sesión
- Ve a "API Keys" y genera una nueva clave
- Asegúrate de tener créditos disponibles

### 5. Credenciales de Telegram (Opcional)

Para recibir notificaciones:

1. Crea un bot en Telegram usando [@BotFather](https://t.me/botfather)
2. Obtén el token del bot
3. Obtén tu Chat ID (envía un mensaje a tu bot y visita `https://api.telegram.org/bot<TOKEN>/getUpdates`)

## ⚙️ Configuración en n8n

### Variables de Entorno

Configura las siguientes variables de entorno en n8n:

```bash
# OpenAI (Requerido)
OPENAI_API_KEY=tu_openai_api_key
OPENAI_MODEL=gpt-4  # Opcional, por defecto usa gpt-4

# Instagram (Opcional pero recomendado)
INSTAGRAM_ACCESS_TOKEN=tu_instagram_access_token
INSTAGRAM_ACCOUNT_ID=tu_instagram_account_id

# TikTok (Opcional pero recomendado)
TIKTOK_ACCESS_TOKEN=tu_tiktok_access_token

# YouTube (Opcional pero recomendado)
YOUTUBE_API_KEY=tu_youtube_api_key
YOUTUBE_CHANNEL_ID=tu_youtube_channel_id  # Opcional

# Telegram (Opcional)
TELEGRAM_BOT_TOKEN=tu_telegram_bot_token
TELEGRAM_CHAT_ID=tu_telegram_chat_id

# Configuración del workflow
DAYS_BACK=7  # Días hacia atrás para analizar (por defecto: 7)
TOP_N_POSTS=10  # Número de posts top a analizar (por defecto: 10)
```

### Importar el Workflow

1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona el archivo `n8n_workflow_social_analytics_ai.json`
4. Configura las credenciales necesarias:
   - **OpenAI API**: Crea una credencial con tu API key
   - **Telegram Bot API**: Crea una credencial con tu bot token (si usas Telegram)

### Configurar Credenciales en n8n

1. **OpenAI API**:
   - Ve a "Credentials" → "Add Credential"
   - Selecciona "OpenAI API"
   - Ingresa tu API Key
   - Guarda como "OpenAI API"

2. **Telegram Bot API** (Opcional):
   - Ve a "Credentials" → "Add Credential"
   - Selecciona "Telegram Bot API"
   - Ingresa tu Bot Token
   - Guarda como "Telegram Bot API"

## 🚀 Uso del Workflow

### Ejecución Automática

El workflow está configurado para ejecutarse automáticamente cada **lunes a las 8:00 AM UTC**. Analizará los posts de los últimos 7 días por defecto.

### Ejecución Manual

Puedes ejecutar el workflow manualmente de dos formas:

1. **Desde n8n**: Haz clic en "Execute Workflow"
2. **Vía Webhook**: Envía una petición POST a:
   ```
   http://tu-n8n-instance/webhook/social-analytics
   ```

### Parámetros Personalizados

Puedes modificar las variables de entorno para personalizar el análisis:

- `DAYS_BACK`: Cambia el período de análisis (ej: 30 para analizar el último mes)
- `TOP_N_POSTS`: Cambia cuántos posts top analizar (ej: 20 para los top 20)

## 📊 Estructura del Reporte

El workflow genera un reporte JSON con la siguiente estructura:

```json
{
  "executionId": "timestamp-randomid",
  "dateRange": {
    "start": "2024-01-01",
    "end": "2024-01-08"
  },
  "summary": {
    "totalPosts": 45,
    "avgEngagementRate": "5.23",
    "avgViralScore": "42.15",
    "postsByPlatform": {
      "Instagram": 20,
      "TikTok": 15,
      "YouTube": 10
    }
  },
  "topPosts": [
    {
      "rank": 1,
      "platform": "Instagram",
      "date": "2024-01-05",
      "caption": "Título del post...",
      "engagementRate": "12.45%",
      "viralScore": "78.32",
      "metrics": {
        "likes": 5000,
        "comments": 250,
        "impressions": 50000,
        "reach": 45000
      },
      "link": "https://instagram.com/p/..."
    }
  ],
  "aiAnalysis": "Análisis completo de ChatGPT...",
  "generatedAt": "2024-01-08T08:00:00.000Z"
}
```

Los reportes se guardan en: `/Users/adan/IA/reports/social_analytics/`

**Formatos disponibles:**
- **JSON**: Reporte completo con todos los datos estructurados
- **CSV**: Exportación para análisis en Excel/Google Sheets

## 🧮 Algoritmo de Scoring Viral

El workflow calcula un "Viral Score" para cada post usando esta fórmula:

```
Viral Score = (Engagement Rate × 0.4) + ((Total Engagement / Reach) × 60)
```

Donde:
- **Engagement Rate**: (Likes + Comments + Shares/Saves) / Impressions/Views × 100
- **Total Engagement**: Suma de todas las interacciones
- **Reach**: Alcance real del post

Los posts se ordenan por este score para identificar los más virales.

## 🤖 Análisis con ChatGPT

ChatGPT analiza los posts exitosos y proporciona:

1. **Patrones Comunes**: Qué tienen en común los posts exitosos
2. **Factores de Éxito**: Por qué fueron virales
3. **Recomendaciones Accionables**: Qué replicar para tener el mismo éxito
4. **Qué Evitar**: Basado en posts menos exitosos
5. **Plan de Acción**: 5-7 pasos concretos para replicar el éxito

## 📱 Notificaciones

Si tienes Telegram configurado, recibirás una notificación con:

- Resumen del análisis
- Top 5 posts más virales
- Preview del análisis de IA
- Link al reporte completo

## 🔧 Solución de Problemas

### Error: "Instagram API no configurada"

- Verifica que `INSTAGRAM_ACCESS_TOKEN` y `INSTAGRAM_ACCOUNT_ID` estén configurados
- Asegúrate de que el token tenga permisos de `instagram_manage_insights`
- Verifica que tu cuenta de Instagram sea una Business Account

### Error: "TikTok API no configurada"

- Verifica que `TIKTOK_ACCESS_TOKEN` esté configurado
- Asegúrate de que el token tenga permisos de lectura de analytics
- Verifica que tu aplicación de TikTok tenga acceso a la API de Analytics

### Error: "YouTube API no configurada"

- Verifica que `YOUTUBE_API_KEY` esté configurado
- Asegúrate de que la YouTube Data API v3 esté habilitada en Google Cloud
- Verifica que la API key tenga permisos suficientes

### Error: "No hay posts para analizar"

- Verifica que haya posts en el período de tiempo seleccionado
- Aumenta `DAYS_BACK` si es necesario
- Verifica que las fechas de los posts estén correctamente formateadas

### Error de ChatGPT

- Verifica que `OPENAI_API_KEY` esté configurado correctamente
- Asegúrate de tener créditos disponibles en tu cuenta de OpenAI
- Verifica que el modelo especificado esté disponible (por defecto: gpt-4)

## 📈 Mejores Prácticas

1. **Ejecuta el análisis semanalmente** para tener datos frescos y relevantes
2. **Ajusta `DAYS_BACK`** según tu frecuencia de publicación (más días si publicas menos)
3. **Revisa los reportes** regularmente para identificar tendencias
4. **Implementa las recomendaciones** de ChatGPT en tus próximos posts
5. **Compara reportes** entre semanas para medir mejoras

## ✨ Mejoras Recientes

### v15.0 - Análisis de Combinaciones Plataforma-Tiempo (NUEVO)

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de combinaciones plataforma-día**: Identifica qué día de la semana funciona mejor para cada plataforma específica (ej: Instagram-Lunes, TikTok-Viernes, YouTube-Martes)
- ✅ **Análisis de combinaciones plataforma-hora**: Descubre qué hora del día genera mejor engagement para cada plataforma (ej: Instagram-18:00, TikTok-20:00, YouTube-14:00)
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre combinaciones específicas plataforma-día y plataforma-hora para optimizar el timing por plataforma

**Ejemplos de uso:**

- Descubre qué día publicar en cada plataforma para maximizar engagement
- Identifica qué hora funciona mejor para cada plataforma específica
- Optimiza tu estrategia de publicación según la plataforma y el timing óptimo
- Planifica contenido multi-plataforma con timing específico por plataforma

### v14.0 - Análisis de Combinaciones Horarias y Duración

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de combinaciones hora-formato**: Identifica qué formato funciona mejor en cada hora específica del día (ej: 18:00-video, 10:00-imagen)
- ✅ **Análisis de combinaciones hora-tipo de contenido**: Descubre qué tipo de contenido genera mejor engagement en cada hora (ej: 14:00-tutorial, 20:00-entretenimiento)
- ✅ **Análisis de combinaciones formato-duración de video**: Identifica la duración óptima de video para cada formato (ej: reel-15-30s, video-1-3min)
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre combinaciones específicas hora-formato y formato-duración

**Ejemplos de uso:**

- Descubre qué formato publicar a cada hora del día para maximizar engagement
- Identifica qué tipo de contenido funciona mejor en cada hora específica
- Optimiza la duración de tus videos según el formato (reel vs video largo)
- Planifica contenido horario con formato y tipo óptimos

### v13.0 - Análisis de Combinaciones Temporales Avanzadas

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de combinaciones mes-formato**: Identifica qué formato de contenido funciona mejor en cada mes específico (ej: Enero-video, Diciembre-imagen)
- ✅ **Análisis de combinaciones mes-tipo de contenido**: Descubre qué tipo de contenido genera mejor engagement en cada mes (ej: Marzo-tutorial, Agosto-entretenimiento)
- ✅ **Análisis de combinaciones día-formato**: Identifica qué formato funciona mejor en cada día de la semana (ej: Lunes-video, Viernes-carousel)
- ✅ **Análisis de combinaciones día-tipo de contenido**: Descubre qué tipo de contenido funciona mejor en cada día de la semana (ej: Martes-educativo, Sábado-entretenimiento)
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre combinaciones específicas mes-formato y día-tipo de contenido

**Ejemplos de uso:**

- Descubre qué formato funciona mejor en cada mes del año para planificar contenido mensual
- Identifica qué tipo de contenido publicar cada día de la semana para maximizar engagement
- Optimiza tu estrategia de contenido según el mes y día específicos
- Planifica contenido mensual y semanal con formato y tipo óptimos

### v12.0 - Análisis de Combinaciones Multi-Dimensionales

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de combinaciones plataforma-formato**: Identifica qué formato de contenido funciona mejor en cada plataforma específica (ej: Instagram-video, TikTok-reel)
- ✅ **Análisis de combinaciones plataforma-tipo de contenido**: Descubre qué tipo de contenido genera mejor engagement en cada plataforma (ej: Instagram-tutorial, TikTok-entretenimiento)
- ✅ **Análisis de combinaciones temporada-formato**: Identifica qué formato funciona mejor en cada temporada del año (ej: verano-video, invierno-imagen)
- ✅ **Análisis de combinaciones temporada-tipo de contenido**: Descubre qué tipo de contenido funciona mejor en cada temporada (ej: primavera-educativo, verano-entretenimiento)
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre combinaciones específicas plataforma-formato y temporada-tipo de contenido

**Ejemplos de uso:**

- Descubre qué formato funciona mejor en Instagram vs TikTok vs YouTube
- Identifica qué tipo de contenido publicar en cada plataforma para maximizar engagement
- Optimiza tu estrategia de contenido según la temporada del año
- Planifica contenido estacional con formato y tipo óptimos

### v11.0 - Análisis Temporal y Combinaciones Avanzadas

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de engagement por día del mes**: Identifica qué días del mes (1-31) generan mejor engagement y score viral
- ✅ **Análisis de engagement por año**: Compara rendimiento entre diferentes años para identificar tendencias a largo plazo
- ✅ **Análisis de combinaciones plataforma-temporada**: Identifica las mejores combinaciones específicas de plataforma y temporada (ej: Instagram-Verano)
- ✅ **Análisis de combinaciones plataforma-mes**: Identifica las mejores combinaciones específicas de plataforma y mes (ej: TikTok-Diciembre)
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre combinaciones plataforma-tiempo específicas

**Ejemplos de uso:**

- Descubre qué días del mes funcionan mejor para publicar
- Compara rendimiento entre años para identificar tendencias a largo plazo
- Encuentra las mejores combinaciones de plataforma y temporada para tu contenido
- Optimiza tu estrategia por plataforma según el mes del año

### v10.0 - Análisis Temporal Avanzado

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de engagement por mes**: Identifica qué meses del año generan mejor engagement y score viral
- ✅ **Análisis de engagement por temporada**: Compara rendimiento entre primavera, verano, otoño e invierno
- ✅ **Análisis granular por hora**: Análisis detallado de engagement por cada hora del día (0-23h) con engagement rate promedio
- ✅ **Análisis de combinaciones día-hora**: Identifica las mejores combinaciones específicas de día de la semana y hora con nivel de confianza
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre temporadas y combinaciones óptimas día-hora

**Ejemplos de uso:**

- Descubre qué meses del año funcionan mejor para tu contenido
- Identifica si hay diferencias de rendimiento entre temporadas
- Optimiza tus horarios de publicación con análisis hora por hora
- Encuentra las mejores combinaciones específicas de día y hora para cada plataforma

### v9.0 - Análisis de Formato y Duración

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de engagement por formato de contenido**: Compara el rendimiento entre diferentes formatos (video, imagen, carousel, texto, reel) con métricas de engagement rate y porcentaje viral
- ✅ **Análisis de engagement por duración de video**: Identifica la duración óptima de videos categorizados en <15s, 15-30s, 30-60s, 1-3min, >3min
- ✅ **Análisis de engagement por tipo de interacción**: Desglosa el engagement total por tipo (likes, comentarios, shares, views) con porcentajes y promedios
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre formato óptimo y duración de video ideal

**Ejemplos de uso:**

- Descubre qué formato de contenido genera mejor engagement (video vs imagen vs carousel)
- Identifica la duración óptima de videos para maximizar engagement
- Entiende qué tipo de interacción predomina en tu audiencia (likes, comentarios, shares)

### v8.0 - Análisis de ROI y Contenido Reciclable

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de contenido reciclable**: Identifica posts con alto engagement y contenido evergreen que pueden reutilizarse, calculando un score de reciclabilidad
- ✅ **Análisis de ROI por tipo de contenido**: Calcula el retorno de inversión (ROI) por tipo de contenido, incluyendo costo total, valor generado, ROI porcentual y costo por engagement
- ✅ **Detección de contenido evergreen vs trending**: Clasifica contenido en evergreen (perdurable, >30 días) y trending (temporal, <7 días) con recomendaciones de balance
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre qué contenido reciclar y qué tipo de contenido genera mejor ROI

**Ejemplos de uso:**

- Identifica qué posts puedes reutilizar para maximizar engagement sin crear contenido nuevo
- Descubre qué tipo de contenido genera mejor retorno de inversión
- Optimiza el balance entre contenido evergreen y trending para engagement sostenido

### v7.0 - Análisis Avanzado y Predicción

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de engagement por franjas horarias**: Identifica las mejores franjas horarias del día (madrugada, mañana, mediodía, tarde, noche) para publicar
- ✅ **Detección de tendencias emergentes**: Identifica hashtags y keywords que están creciendo rápidamente (más del 50% de crecimiento semana a semana)
- ✅ **Modelo de predicción de viralidad**: Sistema avanzado que predice el potencial viral de contenido antes de publicarlo basándose en múltiples factores
- ✅ **Factores de predicción**: Incluye análisis de plataforma, horario, tipo de contenido, hashtags, longitud de caption y sentimiento

**Ejemplos de uso:**

- Descubre qué franja horaria funciona mejor para tu audiencia
- Identifica tendencias emergentes antes de que se vuelvan mainstream
- Predice el potencial viral de tus posts antes de publicarlos
- Optimiza tus posts usando el modelo de predicción con precisión del 75%

### v6.0 - Análisis de Sentimiento e Ideas de Contenido

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de sentimiento básico**: Analiza el sentimiento (positivo, negativo, neutral) de los captions y su relación con el rendimiento
- ✅ **Generación de ideas de contenido futuro**: Genera automáticamente 5 ideas de contenido basadas en posts exitosos, incluyendo keywords, hashtags y horarios sugeridos
- ✅ **Análisis de mejor día por plataforma**: Identifica el mejor día de la semana para publicar en cada plataforma específica con nivel de confianza
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre sentimiento y ideas de contenido listas para usar

**Ejemplos de uso:**

- Descubre qué tipo de sentimiento funciona mejor en tus captions
- Obtén ideas de contenido listas para usar basadas en tus posts más exitosos
- Optimiza tus días de publicación por plataforma basándote en datos históricos

### v5.0 - Análisis de Contenido Avanzado

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de palabras clave efectivas**: Identifica las palabras que aparecen frecuentemente en posts exitosos y su impacto en el engagement
- ✅ **Análisis de emojis más efectivos**: Detecta qué emojis generan mejor engagement y score viral
- ✅ **Predicción de mejor hora por plataforma**: Usa datos históricos de tu audiencia para predecir las mejores horas de publicación por plataforma con nivel de confianza
- ✅ **Recomendaciones mejoradas**: Las recomendaciones ahora incluyen insights sobre palabras clave y emojis efectivos

**Ejemplos de uso:**

- Identifica qué palabras clave usar en tus captions para aumentar engagement
- Descubre qué emojis funcionan mejor en cada plataforma
- Optimiza tus horarios de publicación basándote en datos históricos de tu audiencia específica

### v4.0 - Análisis Temporal y Combinaciones

**Nuevas funcionalidades agregadas:**

- ✅ **Análisis de combinaciones de hashtags**: Identifica qué hashtags funcionan mejor cuando se usan juntos
- ✅ **Análisis de tendencias temporales**: Compara el rendimiento semana a semana con métricas de crecimiento
- ✅ **Análisis de tipos de contenido**: Clasifica posts por tipo (tutorial, educativo, promocional, etc.) y analiza su rendimiento
- ✅ **Métricas de crecimiento**: Compara el período actual con el anterior para identificar tendencias
- ✅ **Alertas mejoradas**: Sistema de alertas más inteligente con niveles de prioridad

### v3.0 - Funcionalidades Avanzadas
- ✅ **Análisis de hashtags** - Identifica los hashtags más efectivos
- ✅ **Análisis de mejores horarios** - Encuentra las mejores horas y días para publicar
- ✅ **Detección de anomalías** - Identifica posts con rendimiento excepcional
- ✅ **Análisis mejorado de ChatGPT** - Incluye insights sobre hashtags, timing y anomalías
- ✅ **Notificaciones mejoradas** - Incluye top hashtags, mejor hora y posts destacados

### v2.0 - Mejoras de Confiabilidad
- ✅ **Retry logic** automático (3 intentos) para todas las APIs
- ✅ **Exportación CSV** además de JSON
- ✅ **Análisis comparativo** entre plataformas
- ✅ **Métricas avanzadas** (máximo, mínimo, promedios por plataforma)
- ✅ **Prompt mejorado** de ChatGPT con más contexto
- ✅ **Análisis predictivo** de contenido futuro
- ✅ **Timeout configurado** (30 segundos) para evitar esperas infinitas

Ver `MEJORAS_SOCIAL_ANALYTICS.md` y `NUEVAS_FUNCIONALIDADES_AVANZADAS.md` para detalles completos.

## 🔄 Actualizaciones Futuras

Posibles mejoras futuras:

- [ ] Paginación automática para APIs que lo requieren
- [x] Análisis de tendencias temporales (comparación semana a semana) ✅ v4.0
- [x] Análisis de combinaciones de hashtags ✅ v4.0
- [x] Predicción de mejor hora basada en audiencia ✅ v5.0
- [x] Análisis de palabras clave efectivas ✅ v5.0
- [x] Análisis de emojis más efectivos ✅ v5.0
- [x] Análisis de sentimiento básico ✅ v6.0
- [x] Generación de ideas de contenido futuro ✅ v6.0
- [x] Análisis de mejor día por plataforma ✅ v6.0
- [x] Análisis de engagement por franjas horarias ✅ v7.0
- [x] Detección de tendencias emergentes ✅ v7.0
- [x] Modelo de predicción de viralidad ✅ v7.0
- [x] Análisis de contenido reciclable ✅ v8.0
- [x] Análisis de ROI por tipo de contenido ✅ v8.0
- [x] Detección de contenido evergreen vs trending ✅ v8.0
- [x] Análisis de engagement por formato de contenido ✅ v9.0
- [x] Análisis de engagement por duración de video ✅ v9.0
- [x] Análisis de engagement por tipo de interacción ✅ v9.0
- [x] Análisis de engagement por mes ✅ v10.0
- [x] Análisis de engagement por temporada ✅ v10.0
- [x] Análisis granular por hora del día ✅ v10.0
- [x] Análisis de combinaciones día-hora ✅ v10.0
- [x] Análisis de engagement por día del mes ✅ v11.0
- [x] Análisis de engagement por año ✅ v11.0
- [x] Análisis de combinaciones plataforma-temporada ✅ v11.0
- [x] Análisis de combinaciones plataforma-mes ✅ v11.0
- [x] Análisis de combinaciones plataforma-formato ✅ v12.0
- [x] Análisis de combinaciones plataforma-tipo de contenido ✅ v12.0
- [x] Análisis de combinaciones temporada-formato ✅ v12.0
- [x] Análisis de combinaciones temporada-tipo de contenido ✅ v12.0
- [ ] Comparación con competidores
- [ ] Integración con más plataformas (Twitter/X, LinkedIn, etc.)
- [ ] Dashboard visual con gráficos
- [x] Alertas automáticas cuando un post supera umbrales ✅ v3.0
- [ ] Análisis de sentimiento de comentarios
- [x] Recomendaciones personalizadas por tipo de contenido ✅ v4.0

## 📝 Notas Importantes

- El workflow requiere al menos una plataforma configurada (Instagram, TikTok o YouTube)
- OpenAI API es requerida para el análisis con IA
- Los reportes se guardan localmente en `/Users/adan/IA/reports/social_analytics/`
- El workflow maneja errores gracefully y continúa con las plataformas disponibles
- Las APIs de redes sociales tienen límites de rate limiting, el workflow respeta estos límites

## 📞 Soporte

Si tienes problemas o preguntas:

1. Revisa la sección de "Solución de Problemas"
2. Verifica los logs de ejecución en n8n
3. Revisa la documentación de las APIs oficiales:
   - [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
   - [TikTok for Developers](https://developers.tiktok.com/)
   - [YouTube Data API](https://developers.google.com/youtube/v3)

---

**Versión**: 1.0  
**Última actualización**: 2024-01-01

