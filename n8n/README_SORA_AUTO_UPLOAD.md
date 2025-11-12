# 🎬 Sora Videos Auto Download, Edit & Upload - Workflow n8n (MEJORADO v2.0)

## 📋 Descripción

Este workflow automatiza completamente el proceso de buscar los videos más vistos de Sora AI, descargarlos, editarlos para evitar detección de algoritmos de redes sociales, generar contenido con IA (ChatGPT/Gemini), y subirlos automáticamente a Instagram, TikTok y YouTube.

## 🆕 Mejoras en la Versión 2.0

### ✨ Nuevas Funcionalidades

1. **Sistema de Cola Inteligente**
   - Cola de procesamiento con prioridades basadas en calidad
   - Gestión automática de reintentos (hasta 3 intentos)
   - Tracking de estado de cada video (pending, processing, completed, failed)

2. **Análisis de Video Mejorado**
   - Análisis automático con `ffprobe` antes de editar
   - Validación de duración, resolución y aspecto
   - Parámetros de edición inteligentes basados en análisis

3. **Verificación de Descargas**
   - Verificación automática de archivos descargados
   - Validación de tamaño mínimo
   - Manejo de errores mejorado con reintentos

4. **Tracking y Estadísticas**
   - Estadísticas completas del workflow
   - Logging de errores con historial
   - Tracking de videos procesados y subidos

5. **Notificaciones Mejoradas**
   - Notificaciones automáticas a Telegram
   - Resumen de procesamiento con estadísticas
   - Alertas de errores críticos

6. **Rate Limiting Avanzado**
   - Verificación individual por plataforma
   - Cálculo de tiempos de espera
   - Estrategia de cola cuando se exceden límites

7. **Limpieza Automática**
   - Limpieza automática de archivos temporales antiguos
   - Gestión de espacio en disco
   - Eliminación de archivos mayores a 24 horas

## ✨ Características Principales

### 🔍 Búsqueda Automática
- ✅ Búsqueda en múltiples fuentes (Reddit, YouTube, Twitter)
- ✅ Filtrado por videos más vistos
- ✅ Evita duplicados (tracking de videos procesados)
- ✅ Ejecución automática cada 6 horas

### 📥 Descarga Inteligente
- ✅ Descarga automática usando `yt-dlp`
- ✅ Soporte para múltiples plataformas
- ✅ Manejo de errores y reintentos

### ✂️ Edición Anti-Detección
- ✅ **Cambios de velocidad**: Variaciones sutiles (0.95x - 1.05x)
- ✅ **Rotación**: Rotación aleatoria (0°, 90°, 180°, 270°)
- ✅ **Ajustes de color**: Brillo, contraste, saturación, gamma
- ✅ **Crop inteligente**: Recortes sutiles para cambiar aspecto
- ✅ **Filtros**: Ruido, sharpening, fades
- ✅ **Múltiples transformaciones**: Combinación de efectos para máxima unicidad

### 🤖 Generación de Contenido con IA
- ✅ **ChatGPT (GPT-4 Vision)**: Genera descripciones y hashtags
- ✅ **Google Gemini**: Respaldo para generación de contenido
- ✅ **Optimización por plataforma**: Contenido específico para Instagram, TikTok, YouTube
- ✅ **Hashtags inteligentes**: Generación automática de hashtags relevantes

### 📤 Subida Multi-Plataforma
- ✅ **Instagram Reels**: Subida automática con caption optimizado
- ✅ **TikTok**: Publicación con título y hashtags
- ✅ **YouTube Shorts**: Subida con título, descripción y tags SEO
- ✅ **Rate Limiting**: Gestión inteligente de límites de API
- ✅ **Tracking**: Registro de todas las subidas

## 🚀 Instalación

### Requisitos Previos

1. **n8n instalado y configurado**
2. **FFmpeg instalado** (para edición de video)
   ```bash
   # macOS
   brew install ffmpeg
   
   # Ubuntu/Debian
   sudo apt-get install ffmpeg
   
   # Windows
   # Descargar desde https://ffmpeg.org/download.html
   ```

3. **yt-dlp instalado** (para descarga de videos)
   ```bash
   pip install yt-dlp
   # O
   brew install yt-dlp
   ```

4. **APIs y Credenciales**:
   - OpenAI API Key (para ChatGPT)
   - Google Gemini API Key
   - Instagram Business API (OAuth2)
   - TikTok API (Access Token)
   - YouTube API (OAuth2)
   - Reddit API (opcional, para mejor búsqueda)
   - Twitter API (opcional, para mejor búsqueda)

### Paso 1: Importar el Workflow

**Versión Mejorada (Recomendada):**
1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona el archivo `n8n_workflow_sora_auto_upload_improved.json`
4. El workflow se importará con todos los nodos configurados

**Versión Original:**
1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona el archivo `n8n_workflow_sora_auto_upload.json`
4. El workflow se importará con todos los nodos configurados

### Paso 2: Configurar Variables de Entorno

Configura las siguientes variables de entorno en n8n:

```bash
# APIs de IA
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=...

# Redes Sociales
INSTAGRAM_ACCOUNT_ID=...
INSTAGRAM_ACCESS_TOKEN=...
TIKTOK_ACCESS_TOKEN=...
YOUTUBE_API_KEY=...

# Configuración
MIN_VIEWS=1000  # Mínimo de visualizaciones para procesar un video

# Rate Limits (opcional, tiene valores por defecto)
INSTAGRAM_RATE_LIMIT=25  # Límite por hora para Instagram
TIKTOK_RATE_LIMIT=10     # Límite por hora para TikTok
YOUTUBE_RATE_LIMIT=6     # Límite por hora para YouTube

# Notificaciones (opcional)
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

### Paso 3: Configurar Credenciales

1. **OpenAI API**:
   - Crea credenciales de tipo "HTTP Header Auth"
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_OPENAI_API_KEY`

2. **Instagram OAuth2**:
   - Configura OAuth2 con Instagram Business API
   - Client ID y Client Secret de tu app de Instagram

3. **TikTok API**:
   - Crea credenciales de tipo "HTTP Header Auth"
   - Header Name: `Authorization`
   - Header Value: `Bearer YOUR_TIKTOK_ACCESS_TOKEN`

4. **YouTube OAuth2**:
   - Configura OAuth2 con YouTube Data API v3
   - Client ID y Client Secret de tu proyecto de Google Cloud

5. **Twitter OAuth2** (opcional):
   - Configura OAuth2 con Twitter API v2

### Paso 4: Activar el Workflow

1. Haz clic en el botón "Active" en la esquina superior derecha
2. El workflow se ejecutará automáticamente cada 6 horas
3. También puedes ejecutarlo manualmente haciendo clic en "Execute Workflow"

## 🔧 Configuración Avanzada

### Ajustar Frecuencia de Búsqueda

Edita el nodo "Schedule Trigger - Every 6 Hours" para cambiar la frecuencia:
- Cada hora: `{ "field": "hours", "hoursInterval": 1 }`
- Cada 12 horas: `{ "field": "hours", "hoursInterval": 12 }`
- Diario: `{ "field": "cronExpression", "expression": "0 0 * * *" }`

### Personalizar Edición de Video

Edita el nodo "Advanced Video Editing" para ajustar los parámetros de edición:

```javascript
// Ajustar rango de velocidad
speed1: 0.95 + Math.random() * 0.1, // 0.95x a 1.05x

// Ajustar intensidad de efectos
brightness: -0.05 + Math.random() * 0.1, // Más variación
contrast: 0.95 + Math.random() * 0.1,
```

### Personalizar Generación de Contenido

Edita los nodos "Generate Content with ChatGPT" o "Generate Content with Gemini" para cambiar el prompt del sistema:

```javascript
{
  "role": "system",
  "content": "Tu prompt personalizado aquí..."
}
```

### Configurar Rate Limits

Edita el nodo "Check Upload Rate Limits" para ajustar los límites:

```javascript
const rateLimits = {
  instagram: { max: 25, window: 3600000 }, // 25 por hora
  tiktok: { max: 10, window: 3600000 },     // 10 por hora
  youtube: { max: 6, window: 3600000 }      // 6 por hora
};
```

## 📊 Monitoreo y Analytics

### Ver Videos Procesados

El workflow guarda todos los videos procesados en `$workflow.staticData.processedVideos`. Puedes acceder a esta información desde cualquier nodo Code.

### Ver Resultados de Subida

Los resultados de subida se guardan en `$workflow.staticData.uploadResults` con información sobre:
- Plataformas donde se subió
- Timestamp de subida
- Caption y hashtags usados

### Estadísticas

Puedes crear un nodo adicional para ver estadísticas:

```javascript
const processedVideos = $workflow.staticData.processedVideos || [];
const uploadResults = $workflow.staticData.uploadResults || [];

const stats = {
  totalProcessed: processedVideos.length,
  totalUploaded: uploadResults.length,
  byPlatform: {
    instagram: uploadResults.filter(r => r.platforms.instagram === 'success').length,
    tiktok: uploadResults.filter(r => r.platforms.tiktok === 'success').length,
    youtube: uploadResults.filter(r => r.platforms.youtube === 'success').length
  }
};

return { json: stats };
```

## 🛡️ Evitar Detección de Algoritmos

El workflow implementa múltiples técnicas para evitar detección:

### 1. Edición de Video
- **Cambios de velocidad**: Variaciones sutiles que no se notan visualmente
- **Rotación**: Cambia la orientación del video
- **Ajustes de color**: Modifica brillo, contraste, saturación
- **Crop**: Recortes sutiles que cambian el aspecto
- **Filtros**: Ruido y sharpening para cambiar la "huella digital"

### 2. Contenido Único
- **Captions generados por IA**: Cada video tiene un caption único
- **Hashtags personalizados**: Generados específicamente para cada video
- **Títulos optimizados**: Diferentes títulos para cada plataforma

### 3. Timing
- **Rate limiting**: Evita subir demasiados videos seguidos
- **Espaciado temporal**: Distribuye las subidas a lo largo del tiempo

## ⚠️ Consideraciones Legales y Éticas

**IMPORTANTE**: Este workflow es para uso educativo y de investigación. Asegúrate de:

1. **Respetar derechos de autor**: Los videos de Sora pueden tener derechos de autor
2. **Cumplir términos de servicio**: Revisa los términos de cada plataforma
3. **Atribución adecuada**: Considera dar crédito al creador original cuando sea posible
4. **Uso responsable**: No uses este workflow para spam o contenido engañoso
5. **Privacidad**: Respeta la privacidad de los creadores originales

## 🐛 Solución de Problemas

### Error: FFmpeg no encontrado

```bash
# Verificar instalación
ffmpeg -version

# Instalar si falta
brew install ffmpeg  # macOS
sudo apt-get install ffmpeg  # Linux
```

### Error: yt-dlp no encontrado

```bash
# Verificar instalación
yt-dlp --version

# Instalar si falta
pip install yt-dlp
```

### Error: No se descargan videos

1. Verifica que `yt-dlp` esté actualizado: `pip install --upgrade yt-dlp`
2. Verifica que las URLs sean accesibles
3. Revisa los logs del nodo "Download with yt-dlp"

### Error: No se genera contenido con IA

1. Verifica que las API keys sean correctas
2. Verifica que tengas créditos/quota disponible
3. Revisa los logs de los nodos de generación de contenido

### Error: No se suben videos a redes sociales

1. Verifica las credenciales OAuth2
2. Verifica que las apps estén aprobadas (Instagram requiere aprobación)
3. Revisa los rate limits
4. Verifica que los archivos de video existan en la ruta especificada

### Videos no se editan correctamente

1. Verifica que FFmpeg esté instalado correctamente
2. Verifica que el video descargado sea válido
3. Revisa los logs del nodo "Execute FFmpeg Editing"
4. Ajusta los parámetros de edición si es necesario

## 📝 Estructura del Workflow

```
Schedule Trigger (cada 6 horas)
    ↓
Prepare Search Sources
    ↓
Search Reddit/YouTube/Twitter (paralelo)
    ↓
Extract Video URLs
    ↓
Filter Best Videos
    ↓
Check Video Source
    ├─→ Download YouTube Video
    ├─→ Download Reddit Video
    └─→ Download Twitter Video
    ↓
Download with yt-dlp
    ↓
Prepare Video Editing
    ↓
Advanced Video Editing
    ↓
Execute FFmpeg Editing
    ↓
Generate Content (ChatGPT/Gemini paralelo)
    ↓
Process AI Generated Content
    ↓
Check Upload Rate Limits
    ↓
Upload to Instagram/TikTok/YouTube (paralelo)
    ↓
Save Processing Results
    ↓
Cleanup Temporary Files
```

## 🔄 Mejoras Futuras

- [ ] Soporte para más fuentes de búsqueda
- [ ] Análisis de video con visión por computadora
- [ ] Generación automática de thumbnails
- [ ] Programación inteligente basada en analytics
- [ ] Notificaciones de éxito/fallo
- [ ] Dashboard web para monitoreo
- [ ] Soporte para más plataformas (Facebook, LinkedIn, etc.)
- [ ] A/B testing de captions y hashtags

## 📚 Recursos Adicionales

- [Documentación de n8n](https://docs.n8n.io/)
- [FFmpeg Documentation](https://ffmpeg.org/documentation.html)
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Google Gemini API Documentation](https://ai.google.dev/docs)
- [Instagram Graph API](https://developers.facebook.com/docs/instagram-api)
- [TikTok API Documentation](https://developers.tiktok.com/doc/)
- [YouTube Data API](https://developers.google.com/youtube/v3)

## 📄 Licencia

Este workflow es proporcionado "tal cual" sin garantías. Úsalo bajo tu propia responsabilidad y asegúrate de cumplir con todas las leyes y términos de servicio aplicables.

---

**Versión**: 1.0  
**Última actualización**: 2024-01-01  
**Autor**: Automatización n8n

