# Workflow n8n: Descarga y Edición Automática de Videos de TikTok

## 📋 Descripción

Este workflow automatiza completamente el proceso de:
1. **Recibir links de TikTok** desde WhatsApp y Telegram
2. **Descargar el video sin marca de agua** automáticamente
3. **Analizar el video con IA** para generar un script de edición personalizado
4. **Editar el video** aplicando transiciones, efectos y cortes según el script
5. **Devolver el video editado** al usuario listo para usar

## ✨ Características Principales

### 🎯 Funcionalidades Core
- ✅ **Recepción multi-canal**: WhatsApp y Telegram
- ✅ **Descarga sin marca de agua**: Usa yt-dlp para extraer videos limpios
- ✅ **Análisis con IA**: OpenAI GPT-4 Vision analiza frames del video
- ✅ **Edición automática**: Aplica transiciones, efectos y cambios de velocidad
- ✅ **Notificaciones en tiempo real**: Usuario informado en cada paso

### 🚀 Funcionalidades Avanzadas
- 🤖 **Análisis inteligente**: Identifica tipo de contenido, momentos clave y cambios de escena
- 🎬 **Transiciones profesionales**: Fade in/out, zoom, efectos visuales
- ⚡ **Cambios de velocidad**: Slow motion y fast forward según el análisis
- 📊 **Métricas del video**: Informa tamaño, duración y detalles del procesamiento

## 🔄 Flujo del Workflow

### Fase 1: Recepción y Validación
1. **Telegram Trigger**: Se activa cuando se recibe un mensaje en Telegram
2. **WhatsApp Webhook**: Recibe mensajes desde WhatsApp
3. **Merge Inputs**: Unifica mensajes de ambas plataformas
4. **Filter TikTok Link**: Verifica que el mensaje contenga un link de TikTok válido

### Fase 2: Descarga
5. **Extract TikTok URL**: Extrae y normaliza la URL de TikTok
6. **Notify Start Processing**: Notifica al usuario que comenzó el procesamiento
7. **Download TikTok Video**: Ejecuta script Python para descargar sin marca de agua
8. **Parse Download Result**: Procesa el resultado de la descarga

### Fase 3: Análisis con IA
9. **Notify Downloaded**: Informa que el video fue descargado
10. **Generate Editing Script**: Analiza el video con IA y genera script de edición
11. **Parse Script**: Procesa el script generado

### Fase 4: Edición
12. **Notify Script Generated**: Informa que el script está listo
13. **Edit Video**: Aplica transiciones y efectos según el script
14. **Parse Edit Result**: Procesa el resultado de la edición

### Fase 5: Entrega
15. **Read Video File**: Lee el archivo de video editado
16. **Send Telegram Video**: Envía el video editado al usuario

## 📦 Componentes del Sistema

### Scripts Python

#### 1. `tiktok_downloader.py`
Descarga videos de TikTok sin marca de agua usando yt-dlp.

**Uso:**
```bash
python3 tiktok_downloader.py "https://www.tiktok.com/@user/video/123" -o /tmp/downloads
```

**Características:**
- Extrae video en mejor calidad disponible
- Obtiene metadata completa (título, duración, autor, etc.)
- Manejo robusto de errores
- Soporte para URLs cortas y largas

#### 2. `video_script_generator.py`
Analiza videos con IA y genera scripts de edición personalizados.

**Uso:**
```bash
python3 video_script_generator.py video.mp4 -n 10 -o script.json
```

**Características:**
- Extrae frames representativos del video
- Usa OpenAI GPT-4 Vision para análisis
- Genera script JSON con transiciones, efectos y cortes
- Identifica momentos clave y cambios de escena

#### 3. `video_editor.py`
Edita videos aplicando el script generado por IA.

**Uso:**
```bash
python3 video_editor.py video.mp4 script.json -o video_edited.mp4
```

**Características:**
- Aplica transiciones (fade in/out, zoom)
- Efectos visuales (zoom, brightness)
- Cambios de velocidad (slow motion, fast forward)
- Exporta en formato MP4 optimizado

## 🛠️ Instalación

### Requisitos Previos

1. **Python 3.8+** instalado
2. **n8n** configurado y ejecutándose
3. **FFmpeg** instalado (requerido por moviepy)
4. **OpenAI API Key** configurada

### Paso 1: Instalar Dependencias Python

```bash
cd /Users/adan/IA/scripts
pip install -r tiktok_requirements.txt
```

### Paso 2: Instalar FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
Descargar desde https://ffmpeg.org/download.html

### Paso 3: Configurar Variables de Entorno

En n8n, configurar las siguientes variables de entorno:

```bash
# OpenAI API Key (requerido para análisis de video)
OPENAI_API_KEY=sk-...

# Telegram Bot Token (si usas Telegram)
TELEGRAM_BOT_TOKEN=...

# Rutas de scripts (ajustar según tu instalación)
TIKTOK_SCRIPTS_DIR=/Users/adan/IA/scripts
TIKTOK_DOWNLOADS_DIR=/tmp/tiktok_downloads
TIKTOK_EDITED_DIR=/tmp/tiktok_edited
```

### Paso 4: Importar Workflow en n8n

1. Abre n8n
2. Ve a **Workflows** → **Import from File**
3. Selecciona `n8n_workflow_tiktok_auto_edit.json`
4. Configura las credenciales:
   - **Telegram Bot API**: Agrega tu token de bot
   - **WhatsApp Webhook**: Configura según tu proveedor de WhatsApp

### Paso 5: Configurar WhatsApp (Opcional)

Para WhatsApp, puedes usar:
- **Twilio WhatsApp API**
- **WhatsApp Business API**
- **WhatsApp Webhook personalizado**

Ajusta el nodo "WhatsApp Webhook" según tu proveedor.

## 🎯 Uso

### Desde Telegram

1. Envía un mensaje al bot con un link de TikTok:
   ```
   https://www.tiktok.com/@user/video/1234567890
   ```

2. El bot responderá con notificaciones en cada paso:
   - 🎬 Procesando video...
   - ✅ Video descargado
   - 🤖 Analizando con IA...
   - 📝 Script generado
   - 🎬 Editando video...
   - ✅ Video editado listo

3. Recibirás el video editado automáticamente

### Desde WhatsApp

1. Envía un mensaje al webhook con un link de TikTok
2. El proceso es el mismo que en Telegram
3. El video editado se enviará de vuelta

## 📝 Formato del Script de Edición

El script generado por IA tiene el siguiente formato:

```json
{
  "analysis": {
    "content_type": "dance",
    "mood": "energetic",
    "key_moments": ["inicio", "clímax", "final"],
    "scene_changes": [
      {"timestamp": 5.0, "type": "hard_cut"}
    ]
  },
  "editing_script": {
    "transitions": [
      {
        "start_time": 0.0,
        "end_time": 1.0,
        "type": "fade_in",
        "description": "Fade in desde negro"
      },
      {
        "start_time": 9.0,
        "end_time": 10.0,
        "type": "fade_out",
        "description": "Fade out final"
      }
    ],
    "effects": [
      {
        "start_time": 3.0,
        "end_time": 5.0,
        "type": "zoom",
        "intensity": 1.2,
        "description": "Zoom in en momento clave"
      }
    ],
    "speed_changes": [
      {
        "start_time": 6.0,
        "end_time": 8.0,
        "speed": 0.5,
        "description": "Slow motion para efecto dramático"
      }
    ]
  },
  "summary": "Video de baile con momentos clave identificados..."
}
```

## 🔧 Configuración Avanzada

### Personalizar Análisis de Video

Edita `video_script_generator.py` para ajustar:
- Número de frames a analizar (`num_frames`)
- Modelo de OpenAI usado
- Prompt de análisis

### Personalizar Edición

Edita `video_editor.py` para agregar:
- Nuevos tipos de transiciones
- Efectos visuales adicionales
- Filtros de color
- Overlays y textos

### Ajustar Calidad de Video

En `video_editor.py`, modifica los parámetros de exportación:

```python
clip.write_videofile(
    output_path,
    codec='libx264',
    audio_codec='aac',
    bitrate='5000k',  # Ajustar calidad
    fps=clip.fps
)
```

## 🐛 Solución de Problemas

### Error: "yt-dlp no está instalado"
```bash
pip install yt-dlp
```

### Error: "FFmpeg no encontrado"
Instala FFmpeg según tu sistema (ver Instalación)

### Error: "OpenAI API Key no configurada"
Configura la variable de entorno `OPENAI_API_KEY`

### Error: "No se pudo descargar el video"
- Verifica que la URL de TikTok sea válida
- Algunos videos pueden estar privados o eliminados
- Intenta con una URL diferente

### Error: "Video demasiado grande para Telegram"
Telegram tiene un límite de 50MB. Considera:
- Comprimir el video antes de enviar
- Usar un servicio de almacenamiento en la nube
- Enviar un link de descarga

## 📊 Límites y Consideraciones

### Límites de Telegram
- Tamaño máximo de video: 50MB
- Duración máxima: Sin límite oficial, pero recomendado < 10 minutos

### Límites de OpenAI
- Costo por análisis: ~$0.01-0.05 por video (depende del modelo)
- Rate limits: Verificar en OpenAI dashboard

### Tiempo de Procesamiento
- Descarga: 10-30 segundos
- Análisis con IA: 30-60 segundos
- Edición: 1-3 minutos (depende de duración y efectos)
- **Total**: 2-5 minutos por video

## 🔒 Seguridad

- **API Keys**: Nunca compartas tus claves API
- **Archivos temporales**: Se limpian automáticamente después del procesamiento
- **Validación de URLs**: Solo procesa URLs de TikTok válidas
- **Límites de tamaño**: Implementa límites para evitar abusos

## 📈 Mejoras Futuras

- [ ] Soporte para múltiples videos en batch
- [ ] Cache de videos descargados
- [ ] Opciones de personalización de edición
- [ ] Integración con más plataformas (Discord, Slack)
- [ ] Dashboard de analytics
- [ ] Cola de procesamiento para múltiples usuarios
- [ ] Soporte para subtítulos automáticos
- [ ] Filtros de color y efectos avanzados

## 📚 Recursos Adicionales

### Documentación
- [yt-dlp Documentation](https://github.com/yt-dlp/yt-dlp)
- [MoviePy Documentation](https://zulko.github.io/moviepy/)
- [OpenAI Vision API](https://platform.openai.com/docs/guides/vision)
- [n8n Documentation](https://docs.n8n.io/)

### Herramientas Relacionadas
- [FFmpeg](https://ffmpeg.org/) - Procesamiento de video
- [OpenCV](https://opencv.org/) - Análisis de imágenes
- [Telegram Bot API](https://core.telegram.org/bots/api)

## 📝 Changelog

### Versión 1.0 (Actual)
- ✅ Descarga de TikTok sin marca de agua
- ✅ Análisis de video con IA
- ✅ Generación automática de scripts
- ✅ Edición con transiciones y efectos
- ✅ Soporte para Telegram y WhatsApp
- ✅ Notificaciones en tiempo real

## 🤝 Contribuciones

Para mejorar este workflow:
1. Revisa los scripts Python y sugiere mejoras
2. Agrega nuevos tipos de transiciones
3. Optimiza el análisis con IA
4. Mejora el manejo de errores

## 📄 Licencia

Este proyecto es parte del sistema IA y sigue la misma licencia del proyecto principal.

---

**¿Necesitas ayuda?** Revisa la sección de Solución de Problemas o abre un issue en el repositorio.



