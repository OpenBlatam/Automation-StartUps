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

# Proveedor de transcripción (opcional, por defecto 'openai')
TRANSCRIPT_PROVIDER=openai       # Opciones: openai, assemblyai, whisper-local
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

**Versión**: 2.0  
**Última actualización**: 2024  
**Autor**: Automatización n8n

### Changelog

#### Versión 2.0
- ✅ Agregado webhook trigger para ejecución manual
- ✅ Validación de scripts antes de ejecutar
- ✅ Manejo robusto de errores con notificaciones
- ✅ Analytics integrados para tracking
- ✅ Notificaciones mejoradas con detalles completos
- ✅ Timeout configurable para procesos largos
- ✅ Respuesta del webhook con resultados JSON

