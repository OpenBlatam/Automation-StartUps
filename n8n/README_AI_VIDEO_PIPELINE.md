# AI Video Pipeline - Automatización de Descubrimiento y Generación de PDFs

Este workflow de n8n automatiza el proceso completo de descubrir videos populares de IA de esta semana en otros idiomas, extraer sus transcripciones y generar PDFs con guías de replicación en español.

## 🎯 Funcionalidades

- ✅ **Descubrimiento automático** de videos populares de IA de esta semana
- ✅ **Búsqueda multi-idioma** (inglés, portugués, francés, alemán, italiano, japonés, coreano, chino)
- ✅ **Extracción de transcripciones** usando OpenAI Whisper, AssemblyAI o Whisper local
- ✅ **Traducción automática** al español
- ✅ **Generación de PDFs** profesionales con guías paso a paso de replicación
- ✅ **Ejecución semanal automática** (cada lunes a las 9:00 AM UTC)
- ✅ **Ejecución manual vía webhook** para pruebas y ejecuciones bajo demanda
- ✅ **Validación de scripts** antes de ejecutar el pipeline
- ✅ **Manejo robusto de errores** con notificaciones detalladas
- ✅ **Notificaciones por Telegram** con resumen detallado del procesamiento
- ✅ **Analytics integrados** para tracking de ejecuciones y rendimiento
- ✅ **Timeout configurable** (1 hora por defecto) para procesos largos
- ✅ **Priorización inteligente** de videos por engagement y frescura
- ✅ **Filtros de calidad avanzados** (likes mínimos, calidad de transcripción)
- ✅ **Health checks de APIs** con monitoreo continuo
- ✅ **Métricas en tiempo real** con cálculo de rendimiento
- ✅ **Exportación de métricas** a JSON estructurado
- ✅ **Alertas inteligentes** basadas en umbrales configurables
- ✅ **Preparación para cloud storage** (S3/GCS) opcional
- ✅ **Procesamiento paralelo** configurable
- ✅ **Tracking de costos** detallado con historial
- ✅ **Integración con bases de datos** (PostgreSQL/MySQL)
- ✅ **Predicción ML de calidad** de videos
- ✅ **Rate limiting inteligente** de APIs
- ✅ **Backup automático** de resultados
- ✅ **Integración con Slack y Discord** para notificaciones
- ✅ **Análisis de tendencias históricas** con comparación temporal
- ✅ **Detección de anomalías** usando Z-score
- ✅ **Optimización automática** con recomendaciones inteligentes
- ✅ **Monitoreo de rendimiento** con identificación de cuellos de botella
- ✅ **Auditoría y compliance** con logging completo (GDPR ready)
- ✅ **Verificaciones de seguridad** automáticas
- ✅ **Análisis predictivo avanzado** con regresión lineal
- ✅ **Dashboard visual** de métricas completo
- ✅ **Optimización de contenido para redes sociales** (TikTok, Instagram, YouTube)
- ✅ **Generación automática de hashtags** optimizados por plataforma
- ✅ **Títulos y descripciones optimizados** para cada plataforma
- ✅ **Análisis de mejor tiempo para publicar** por plataforma
- ✅ **Análisis de video con IA avanzada** (detección de escenas, objetos, emociones)
- ✅ **Recomendaciones inteligentes de contenido** basadas en patrones exitosos
- ✅ **Integración multi-plataforma avanzada** (Twitter, LinkedIn, Facebook)
- ✅ **Análisis de conversión** con funnels y tasas de conversión
- ✅ **A/B Testing avanzado** con análisis estadístico
- ✅ **Integración con CRM** (Salesforce, HubSpot, Pipedrive)
- ✅ **Contenido predictivo** con pronósticos y recomendaciones
- ✅ **Análisis de sentimiento avanzado** con NLP y detección de emociones
- ✅ **Generación automática de subtítulos** en múltiples idiomas
- ✅ **Análisis profundo de competidores** con patrones y estrategias
- ✅ **Recomendaciones personalizadas** con ML basadas en perfil de usuario
- ✅ **Integración con Analytics** (Google Analytics, Facebook, YouTube)
- ✅ **Alertas proactivas** con ML para prevenir problemas
- ✅ **Análisis de voz y tono** del contenido
- ✅ **Detección de tendencias emergentes** en tiempo real
- ✅ **Sistema de scoring de viralidad** mejorado
- ✅ **Integración con herramientas de marketing** (Mailchimp, SendGrid, HubSpot)

## 📋 Requisitos Previos

### 1. Dependencias Python

Instala las dependencias necesarias:

```bash
pip install yt-dlp openai reportlab google-api-python-client
```

O instala desde el archivo de requirements:

```bash
pip install -r requirements.txt
```

### 2. API Keys

Configura las siguientes variables de entorno en n8n:

#### YouTube API (Opcional pero recomendado)
```bash
YOUTUBE_API_KEY=tu_api_key_de_youtube
```

Para obtener una API key:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la API de YouTube Data API v3
4. Crea credenciales (API Key)
5. Copia la API key

#### OpenAI API (Requerido para transcripción y traducción)
```bash
OPENAI_API_KEY=tu_api_key_de_openai
```

Para obtener una API key:
1. Ve a [OpenAI Platform](https://platform.openai.com/)
2. Crea una cuenta o inicia sesión
3. Ve a API Keys y crea una nueva
4. Copia la API key

#### Telegram (Opcional para notificaciones)
```bash
TELEGRAM_BOT_TOKEN=tu_token_del_bot
TELEGRAM_CHAT_ID=tu_chat_id
```

### 3. Variables de Entorno Opcionales

```bash
# Configuración del pipeline
MAX_VIDEOS=10                    # Número máximo de videos a procesar
DAYS_BACK=7                      # Días hacia atrás para buscar (por defecto 7 = esta semana)
LANGUAGES=en,pt,fr,de,it,ja,ko,zh  # Idiomas a buscar (separados por comas)
OUTPUT_DIR=./ai_video_outputs     # Directorio de salida

# Retry y cache
MAX_RETRIES=3                    # Número máximo de reintentos
ENABLE_CACHE=true                # Habilitar cache de videos procesados

# Calidad y filtros
MIN_VIDEO_QUALITY=1000           # Likes mínimos requeridos
MIN_TRANSCRIPT_QUALITY=0.7       # Calidad mínima de transcripción (0-1)
ENABLE_PRIORITY_QUEUE=true      # Priorizar videos por calidad

# Procesamiento
BATCH_SIZE=3                     # Tamaño de lotes
ENABLE_PARALLEL=true             # Procesamiento paralelo
MAX_CONCURRENT=3                 # Máximo de procesos concurrentes

# Cloud Storage (opcional)
S3_BUCKET=tu-bucket-s3           # Bucket de S3 para almacenamiento
GCS_BUCKET=tu-bucket-gcs         # Bucket de GCS para almacenamiento
CLOUD_STORAGE_TYPE=s3            # Tipo: s3 o gcs
CLOUD_STORAGE_PATH=ai-video-pipeline  # Ruta base en cloud

# Métricas y alertas
ENABLE_METRICS_EXPORT=true       # Exportar métricas a JSON
ENABLE_SMART_ALERTS=true         # Alertas inteligentes
MIN_SUCCESS_RATE=0.8             # Tasa de éxito mínima (80%)
MAX_ERROR_RATE=0.2               # Tasa de error máxima (20%)
MIN_VIDEOS_PROCESSED=5           # Mínimo de videos procesados
MAX_PROCESSING_TIME_MINUTES=60   # Tiempo máximo de procesamiento

# Health checks
ENABLE_HEALTH_CHECK=true         # Health checks de APIs

# Base de datos (opcional)
DB_HOST=localhost                 # Host de base de datos
DB_NAME=ai_video_pipeline         # Nombre de base de datos
DB_USER=user                      # Usuario de base de datos
DB_PASSWORD=password              # Contraseña de base de datos
ENABLE_DATABASE=false             # Habilitar guardado en DB

# Tracking de costos
ENABLE_COST_TRACKING=true         # Tracking de costos
COST_DISCOVERY=0.001              # Costo por descubrimiento de video
COST_TRANSCRIPTION=0.01           # Costo por transcripción
COST_TRANSLATION=0.005            # Costo por traducción
COST_PDF=0.002                    # Costo por generación de PDF
COST_CLOUD_STORAGE=0.0001         # Costo por archivo en cloud

# ML y predicciones
ENABLE_ML_PREDICTION=true         # Predicción ML de calidad

# Rate limiting
ENABLE_RATE_LIMITING=true         # Rate limiting inteligente
YOUTUBE_RATE_LIMIT=10000          # Límite de requests YouTube/hora
OPENAI_RATE_LIMIT=50000           # Límite de requests OpenAI/hora

# Backup
ENABLE_BACKUP=true                # Backup automático

# Integraciones adicionales
SLACK_WEBHOOK_URL=                # Webhook URL de Slack
DISCORD_WEBHOOK_URL=              # Webhook URL de Discord
ENABLE_AUTO_REPORTS=false         # Reportes automáticos

# Análisis avanzado
ENABLE_TREND_ANALYSIS=true        # Análisis de tendencias históricas
ENABLE_ANOMALY_DETECTION=true     # Detección de anomalías
ENABLE_AUTO_OPTIMIZATION=true     # Optimización automática
ENABLE_PERF_MONITORING=true       # Monitoreo de rendimiento
ENABLE_RESOURCE_OPTIMIZATION=true # Optimización de recursos

# Seguridad y compliance
ENABLE_AUDIT_LOGGING=true         # Logging de auditoría
ENABLE_SECURITY_CHECKS=true       # Verificaciones de seguridad
ENABLE_COMPLIANCE=true            # Compliance (GDPR, etc.)
ENABLE_PREDICTIVE_ANALYSIS=true   # Análisis predictivo avanzado
ENABLE_DASHBOARD=true             # Dashboard visual de métricas
ENABLE_AUTO_SCALING=false         # Auto-scaling (futuro)

# Optimización de redes sociales
ENABLE_SOCIAL_MEDIA_OPT=true      # Optimización de contenido para redes sociales
ENABLE_MULTI_PLATFORM=true        # Generar contenido para múltiples plataformas
TIKTOK_INDUSTRY=automation        # Industria para hashtags TikTok
TIKTOK_DEMOGRAPHIC=tech_savvy     # Demografía objetivo TikTok
MAX_HASHTAG_VIDEOS=5              # Máximo de videos para generar hashtags

# Proveedor de transcripción (opcional, por defecto 'openai')
TRANSCRIPT_PROVIDER=openai       # Opciones: openai, assemblyai, whisper-local

# Versión 14.0 - Advanced AI & Multi-Platform Intelligence
ENABLE_AI_VIDEO_ANALYSIS=true              # Análisis de video con IA avanzada
ENABLE_SMART_CONTENT_RECOMMENDATIONS=true   # Recomendaciones inteligentes de contenido
ENABLE_MULTI_PLATFORM_INTEGRATION=true      # Integración multi-plataforma avanzada
ENABLE_CONVERSION_ANALYSIS=true             # Análisis de conversión y funnels
ENABLE_ADVANCED_AB_TESTING=true            # A/B Testing avanzado con análisis estadístico
ENABLE_CRM_INTEGRATION=false                # Integración con CRM (requiere credenciales)
ENABLE_PREDICTIVE_CONTENT=true             # Contenido predictivo y pronósticos

# CRM Integration (requiere configuración adicional)
SALESFORCE_API_URL=                        # URL de API de Salesforce
SALESFORCE_CLIENT_ID=                      # Client ID de Salesforce
SALESFORCE_CLIENT_SECRET=                  # Client Secret de Salesforce
HUBSPOT_API_KEY=                           # API Key de HubSpot
PIPEDRIVE_API_TOKEN=                       # API Token de Pipedrive

# Versión 15.0 - Ultimate Intelligence & Automation Suite
ENABLE_ADVANCED_SENTIMENT=true             # Análisis de sentimiento avanzado con NLP
ENABLE_AUTO_SUBTITLES=true                 # Generación automática de subtítulos
ENABLE_COMPETITOR_DEEP_ANALYSIS=true       # Análisis profundo de competidores
ENABLE_PERSONALIZED_RECOMMENDATIONS=true   # Recomendaciones personalizadas con ML
ENABLE_ANALYTICS_INTEGRATION=true          # Integración con Analytics
ENABLE_PROACTIVE_ALERTS=true               # Alertas proactivas con ML
ENABLE_VOICE_TONE_ANALYSIS=true            # Análisis de voz y tono
ENABLE_EMERGING_TRENDS=true                # Detección de tendencias emergentes
ENABLE_VIRAL_SCORING=true                  # Sistema de scoring de viralidad
ENABLE_MARKETING_INTEGRATION=false         # Integración con herramientas de marketing

# Analytics Integration (requiere configuración adicional)
GOOGLE_ANALYTICS_PROPERTY_ID=              # Google Analytics Property ID
GOOGLE_ANALYTICS_API_KEY=                  # Google Analytics API Key
FACEBOOK_ANALYTICS_ACCESS_TOKEN=           # Facebook Analytics Access Token

# Marketing Integration (requiere configuración adicional)
MAILCHIMP_API_KEY=                         # Mailchimp API Key
SENDGRID_API_KEY=                          # SendGrid API Key
HUBSPOT_MARKETING_API_KEY=                 # HubSpot Marketing API Key
```

## 🚀 Instalación

### Paso 1: Importar el Workflow

1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona el archivo `n8n_workflow_ai_video_pipeline.json`
4. El workflow se importará con todos los nodos configurados

### Paso 2: Configurar Variables de Entorno

1. En n8n, ve a "Settings" → "Environment Variables"
2. Agrega las variables de entorno mencionadas arriba:
   - `OPENAI_API_KEY` (requerido)
   - `YOUTUBE_API_KEY` (opcional pero recomendado)
   - `TELEGRAM_BOT_TOKEN` (opcional)
   - `TELEGRAM_CHAT_ID` (opcional)
   - `MAX_VIDEOS` (opcional, por defecto 10)
   - `DAYS_BACK` (opcional, por defecto 7)
   - `OUTPUT_DIR` (opcional, por defecto ./ai_video_outputs)

### Paso 3: Configurar Credenciales de Telegram (Opcional)

Si quieres recibir notificaciones por Telegram:

1. Haz clic en el nodo "Send Telegram Notification"
2. Configura la credencial "Telegram Bot API" con tu token
3. Asegúrate de que `TELEGRAM_CHAT_ID` esté configurado en las variables de entorno

### Paso 4: Verificar Rutas de Scripts

Asegúrate de que las rutas en el workflow apunten a la ubicación correcta de los scripts:

- Scripts deben estar en: `/Users/adan/IA/scripts/`
- Archivos necesarios:
  - `ai_video_pipeline.py`
  - `ai_video_discoverer.py`
  - `video_transcript_extractor.py`
  - `pdf_replication_guide_generator.py`

Si tus scripts están en otra ubicación, edita el nodo "Run AI Video Pipeline" y actualiza la ruta.

### Paso 5: Activar el Workflow

1. Haz clic en el botón "Active" en la esquina superior derecha
2. El workflow se ejecutará automáticamente cada lunes a las 9:00 AM UTC
3. También puedes ejecutarlo manualmente:
   - **Desde n8n**: Haz clic en "Execute Workflow"
   - **Vía webhook**: Envía un POST a la URL del webhook (se muestra al activar el workflow)
   - **Ejemplo con curl**: 
     ```bash
     curl -X POST https://tu-n8n-instance.com/webhook/ai-video-pipeline
     ```

## 🆕 Mejoras en la Versión 2.0

### Validaciones Mejoradas
- ✅ Validación de API keys antes de ejecutar
- ✅ Verificación de existencia de scripts necesarios
- ✅ Validación de permisos y rutas

### Manejo de Errores Robusto
- ✅ Captura de errores en cada etapa del proceso
- ✅ Notificaciones detalladas de errores por Telegram
- ✅ Continuación del workflow incluso si hay errores parciales
- ✅ Logging completo de errores para debugging

### Ejecución Flexible
- ✅ **Trigger programado**: Ejecución automática semanal
- ✅ **Webhook trigger**: Ejecución manual bajo demanda
- ✅ **Timeout configurable**: 1 hora por defecto (ajustable)
- ✅ **Respuesta del webhook**: JSON con resultados de la ejecución

### Analytics y Monitoreo
- ✅ Tracking de ejecuciones exitosas y fallidas
- ✅ Estadísticas de videos procesados y PDFs generados
- ✅ Historial de últimas 50 ejecuciones
- ✅ Tasa de éxito calculada automáticamente

### Notificaciones Mejoradas
- ✅ Mensajes detallados con lista de videos procesados
- ✅ Información de errores específicos
- ✅ Enlaces a archivos generados
- ✅ ID de ejecución para tracking

## 📁 Estructura de Archivos Generados

El pipeline genera los siguientes archivos en el directorio de salida:

```
ai_video_outputs/
├── discovered_videos.json          # Lista de videos descubiertos
├── pipeline_summary.json          # Resumen del procesamiento
├── transcript_<video_id>.json    # Transcripciones de cada video
├── video_info_<video_id>.json     # Información de cada video
└── replication_guide_<video_id>.pdf  # PDFs con guías de replicación
```

## 🔧 Uso Manual

### Desde la Línea de Comandos

También puedes ejecutar el pipeline manualmente desde la línea de comandos:

```bash
cd /Users/adan/IA/scripts
python3 ai_video_pipeline.py \
  --max-videos 10 \
  --days-back 7 \
  --output-dir ./ai_video_outputs \
  --youtube-api-key TU_API_KEY \
  --openai-api-key TU_API_KEY
```

### Vía Webhook (n8n)

El workflow incluye un webhook trigger que permite ejecutar el pipeline bajo demanda:

```bash
# Ejecutar pipeline vía webhook
curl -X POST https://tu-n8n-instance.com/webhook/ai-video-pipeline

# Con parámetros personalizados (si se implementa)
curl -X POST https://tu-n8n-instance.com/webhook/ai-video-pipeline \
  -H "Content-Type: application/json" \
  -d '{"maxVideos": 5, "daysBack": 3}'
```

La respuesta incluirá:
```json
{
  "success": true,
  "message": "Pipeline ejecutado",
  "executionId": "1234567890-abc123",
  "videosProcessed": 8,
  "pdfsGenerated": 8
}
```

## 📊 Ejemplo de Salida

El pipeline genera un resumen JSON con esta estructura:

```json
{
  "started_at": "2024-01-01T09:00:00.000Z",
  "completed_at": "2024-01-01T09:15:00.000Z",
  "videos_discovered": 10,
  "videos_processed": 8,
  "pdfs_generated": 8,
  "errors": [],
  "outputs": [
    {
      "video_id": "abc123",
      "title": "Amazing AI Tutorial",
      "transcript_file": "./ai_video_outputs/transcript_abc123.json",
      "video_info_file": "./ai_video_outputs/video_info_abc123.json",
      "pdf_file": "./ai_video_outputs/replication_guide_abc123.pdf"
    }
  ]
}
```

## 🎨 Personalización

### Cambiar Frecuencia de Ejecución

Edita el nodo "Schedule Trigger" y modifica el `cronExpression`:

- Diario a las 9 AM: `0 9 * * *`
- Cada lunes a las 9 AM: `0 9 * * 1`
- Cada día a las 6 PM: `0 18 * * *`

### Cambiar Idiomas a Buscar

Modifica la variable de entorno `LANGUAGES`:

```bash
LANGUAGES=en,pt,fr  # Solo inglés, portugués y francés
```

### Usar Diferente Proveedor de Transcripción

Cambia la variable `TRANSCRIPT_PROVIDER`:

- `openai`: Usa OpenAI Whisper API (requiere API key)
- `assemblyai`: Usa AssemblyAI (requiere API key)
- `whisper-local`: Usa Whisper instalado localmente (no requiere API key)

## 🐛 Solución de Problemas

### Error: "Script not found"

- Verifica que los scripts estén en `/Users/adan/IA/scripts/`
- Verifica que Python 3 esté instalado: `python3 --version`
- Verifica permisos de ejecución: `chmod +x scripts/*.py`

### Error: "API key not found"

- Verifica que las variables de entorno estén configuradas en n8n
- Reinicia n8n después de agregar variables de entorno
- Verifica que los nombres de las variables sean exactos (case-sensitive)

### Error: "No videos found"

- Verifica que `YOUTUBE_API_KEY` esté configurada
- Verifica que la API de YouTube esté habilitada en Google Cloud Console
- Aumenta `DAYS_BACK` si no hay videos recientes

### Error: "Transcription failed"

- Verifica que `OPENAI_API_KEY` esté configurada y sea válida
- Verifica que tengas créditos disponibles en tu cuenta de OpenAI
- Intenta con un proveedor diferente (`assemblyai` o `whisper-local`)

### PDFs no se generan

- Verifica que `reportlab` esté instalado: `pip install reportlab`
- Verifica permisos de escritura en el directorio de salida
- Revisa los logs del workflow para ver errores específicos

## 📝 Notas

- El pipeline puede tardar varios minutos dependiendo del número de videos
- Cada video requiere descargar audio y transcribirlo, lo cual consume tiempo y recursos
- Los PDFs incluyen traducción automática al español usando GPT-4o-mini
- Las transcripciones se guardan en formato JSON para referencia futura

## 🔒 Consideraciones Legales

⚠️ **Importante**: Este workflow es para uso personal y educativo. Asegúrate de:

- Respetar los derechos de autor del contenido
- No redistribuir contenido sin permiso
- Cumplir con los términos de servicio de YouTube y OpenAI
- Usar el contenido descargado de manera responsable

## 📚 Recursos Adicionales

- [Documentación de n8n](https://docs.n8n.io/)
- [YouTube Data API v3](https://developers.google.com/youtube/v3)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Whisper Documentation](https://github.com/openai/whisper)

## 🤝 Contribuciones

Si encuentras problemas o tienes sugerencias:

1. Revisa los logs de ejecución en n8n
2. Verifica que todas las credenciales estén correctas
3. Prueba ejecutar los scripts manualmente para aislar el problema

## 📈 Analytics y Estadísticas

El workflow mantiene estadísticas automáticas que puedes consultar:

- **Total de ejecuciones**: Número total de veces que se ha ejecutado
- **Tasa de éxito**: Porcentaje de ejecuciones exitosas
- **Videos procesados**: Total acumulado de videos procesados
- **PDFs generados**: Total acumulado de PDFs generados
- **Historial**: Últimas 50 ejecuciones con detalles

Estas estadísticas se almacenan en `$workflow.staticData.analytics` y se actualizan automáticamente después de cada ejecución.

## 🔍 Debugging

### Ver Logs de Ejecución

1. En n8n, ve a "Executions"
2. Selecciona la ejecución que quieres revisar
3. Revisa cada nodo para ver los datos de entrada y salida
4. Los errores se muestran en rojo con detalles completos

### Verificar Estado del Pipeline

El workflow genera un archivo `pipeline_summary.json` que incluye:
- Estado de cada video procesado
- Errores encontrados (si los hay)
- Rutas de archivos generados
- Tiempos de ejecución

### Verificar Analytics

Puedes agregar un nodo Code al final del workflow para ver las estadísticas:

```javascript
// Ver analytics
const analytics = $workflow.staticData.analytics;
return [{ json: analytics }];
```

---

**Versión**: 15.0  
**Última actualización**: 2024  
**Autor**: Automatización n8n

### Changelog

#### Versión 15.0 - Ultimate Intelligence & Automation Suite 🚀
- ✅ Análisis de sentimiento avanzado con NLP (detección de emociones, análisis por tópico)
- ✅ Generación automática de subtítulos en múltiples idiomas (SRT, VTT)
- ✅ Análisis profundo de competidores con patrones y estrategias de engagement
- ✅ Recomendaciones personalizadas con ML basadas en perfil de usuario
- ✅ Integración con plataformas de Analytics (Google Analytics, Facebook, YouTube)
- ✅ Alertas proactivas con ML para prevenir problemas antes de que ocurran
- ✅ Análisis de voz y tono (formal, casual, técnico) con métricas de legibilidad
- ✅ Detección de tendencias emergentes en tiempo real con predicciones
- ✅ Sistema de scoring de viralidad mejorado con componentes detallados
- ✅ Integración con herramientas de marketing (Mailchimp, SendGrid, HubSpot Marketing)
- ✅ Automatizaciones de marketing basadas en engagement
- ✅ Notificaciones mejoradas con todas las nuevas métricas

#### Versión 15.0 - Ultimate Intelligence & Automation Suite 🎯
- ✅ Análisis de sentimiento avanzado con NLP y detección de emociones (joy, surprise, anger, fear, sadness)
- ✅ Análisis de sentimiento por tópico (AI, automation, tutorial)
- ✅ Generación automática de subtítulos en múltiples idiomas (SRT, VTT)
- ✅ Análisis profundo de competidores con patrones y estrategias
- ✅ Identificación de keywords y tipos de contenido más exitosos
- ✅ Recomendaciones personalizadas con ML basadas en perfil de usuario
- ✅ Sistema de scoring de personalización por video
- ✅ Integración con Analytics (Google Analytics, Facebook, YouTube)
- ✅ Métricas agregadas y insights de rendimiento
- ✅ Alertas proactivas con ML para prevenir problemas
- ✅ Predicciones de rendimiento y problemas potenciales
- ✅ Análisis de voz y tono del contenido (formal, casual, técnico)
- ✅ Análisis de legibilidad y características de voz
- ✅ Detección de tendencias emergentes en tiempo real
- ✅ Identificación de keywords en crecimiento
- ✅ Sistema de scoring de viralidad mejorado con múltiples componentes
- ✅ Análisis de potencial viral por título y contenido
- ✅ Integración con herramientas de marketing (Mailchimp, SendGrid, HubSpot)
- ✅ Generación automática de campañas de marketing
- ✅ Automatizaciones de marketing basadas en engagement
- ✅ Notificaciones mejoradas con todas las nuevas métricas

#### Versión 14.0 - Advanced AI & Multi-Platform Intelligence 🤖
- ✅ Análisis de video con IA avanzada (detección de escenas, objetos, emociones, audio)                                                                        
- ✅ Clasificación automática de contenido con confianza
- ✅ Recomendaciones inteligentes de contenido basadas en patrones exitosos
- ✅ Generación automática de ideas de contenido
- ✅ Integración multi-plataforma avanzada (Twitter, LinkedIn, Facebook)
- ✅ Estrategia cross-platform con contenido unificado
- ✅ Análisis de conversión con funnels detallados (views→likes→shares→comments)
- ✅ Oportunidades de optimización de conversión
- ✅ A/B Testing avanzado con análisis estadístico y power analysis
- ✅ Configuraciones de test con hipótesis y criterios de ganador
- ✅ Integración con sistemas CRM (Salesforce, HubSpot, Pipedrive)
- ✅ Generación automática de leads y campañas
- ✅ Contenido predictivo con pronósticos semanales y mensuales
- ✅ Predicción de tendencias de contenido y engagement
- ✅ Recomendaciones de timing y mix de contenido óptimo
- ✅ Notificaciones mejoradas con todas las nuevas métricas

#### Versión 13.0 - Business Intelligence & Collaboration 💼
- ✅ Análisis de ROI (Return on Investment) completo
- ✅ Integración con herramientas de diseño (Canva, Figma, Adobe Express)
- ✅ Generación de reportes ejecutivos (JSON y texto)
- ✅ Sistema de colaboración y trabajo en equipo
- ✅ Exportación avanzada a múltiples formatos (CSV, XML, Markdown)
- ✅ Métricas de negocio y KPIs
- ✅ Tracking de crecimiento y eficiencia
- ✅ Valor estimado de contenido generado

#### Versión 8.1 - Social Media Optimization 📱
- ✅ Optimización de contenido para múltiples plataformas (TikTok, Instagram, YouTube)
- ✅ Generación automática de hashtags optimizados por plataforma
- ✅ Títulos y descripciones optimizados para cada plataforma
- ✅ Análisis de mejor tiempo para publicar por plataforma
- ✅ Captions personalizados según tipo de contenido
- ✅ Soporte para hasta 5 videos simultáneos
- ✅ Detección automática de tipo de contenido

#### Versión 8.0 - Enterprise Security & Predictive Intelligence 🔐
- ✅ Auditoría y compliance completo con logging GDPR-ready
- ✅ Verificaciones de seguridad automáticas (encriptación, acceso no autorizado)
- ✅ Análisis predictivo avanzado con regresión lineal
- ✅ Dashboard visual completo de métricas
- ✅ Predicciones de próxima ejecución (videos, éxito, costos)
- ✅ Historial de auditoría con retención configurable
- ✅ Notificaciones mejoradas con seguridad y predicciones

#### Versión 7.0 - AI-Powered Analytics & Optimization 🚀
- ✅ Análisis de tendencias históricas con comparación temporal
- ✅ Detección de anomalías usando Z-score estadístico
- ✅ Optimización automática con recomendaciones inteligentes
- ✅ Monitoreo de rendimiento con identificación de cuellos de botella
- ✅ Análisis de eficiencia (videos/segundo, cost efficiency)
- ✅ Recomendaciones automáticas de configuración
- ✅ Notificaciones mejoradas con tendencias y anomalías

#### Versión 6.0 - Ultimate Enterprise Features 🎯
- ✅ Tracking de costos detallado con historial y promedios
- ✅ Integración con bases de datos (PostgreSQL/MySQL)
- ✅ Predicción ML de calidad de videos con scoring
- ✅ Rate limiting inteligente de APIs con advertencias
- ✅ Backup automático de resultados con limpieza
- ✅ Integración con Slack y Discord para notificaciones
- ✅ Notificaciones mejoradas con información de costos y ML

#### Versión 5.0 - Enterprise Features 🚀
- ✅ Priorización inteligente de videos por engagement y frescura
- ✅ Filtros de calidad avanzados (likes, transcripción)
- ✅ Health checks de APIs con monitoreo continuo
- ✅ Métricas en tiempo real con cálculo de rendimiento
- ✅ Exportación de métricas a JSON estructurado
- ✅ Alertas inteligentes basadas en umbrales configurables
- ✅ Preparación para cloud storage (S3/GCS)
- ✅ Procesamiento paralelo configurable
- ✅ Sistema de colas con priorización

#### Versión 4.0 - Advanced Features
- ✅ Retry con exponential backoff y jitter
- ✅ Cache inteligente de videos procesados
- ✅ Notificaciones por email además de Telegram
- ✅ Webhooks externos para integraciones
- ✅ Validación mejorada de calidad

#### Versión 3.0 - Enhanced Features
- ✅ Health check de APIs antes de ejecutar
- ✅ Filtros de calidad de videos
- ✅ Métricas en tiempo real
- ✅ Notificaciones mejoradas

#### Versión 2.0 - Core Features
- ✅ Agregado webhook trigger para ejecución manual
- ✅ Validación de scripts antes de ejecutar
- ✅ Manejo robusto de errores con notificaciones
- ✅ Analytics integrados para tracking
- ✅ Notificaciones mejoradas con detalles completos
- ✅ Timeout configurable para procesos largos
- ✅ Respuesta del webhook con resultados JSON

