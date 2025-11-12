# TikTok Auto Edit - Sistema Completo

## 🎯 Resumen del Sistema

Sistema completo de automatización para descargar, analizar y editar videos de TikTok con IA, incluyendo:

- ✅ Descarga sin marca de agua
- ✅ Análisis con IA (GPT-4 Vision)
- ✅ Edición automática con efectos avanzados
- ✅ Procesamiento en batch
- ✅ API REST completa
- ✅ Webhooks multi-plataforma
- ✅ Sistema de cola asíncrono
- ✅ Dashboard web
- ✅ Notificaciones multi-canal
- ✅ Analytics y reportes
- ✅ Templates de edición
- ✅ Optimización automática

## 📁 Estructura de Archivos

```
scripts/
├── tiktok_downloader.py          # Descarga de videos
├── video_script_generator.py     # Generación de scripts con IA
├── video_editor.py               # Edición de videos
├── video_compressor.py           # Compresión de videos
├── video_effects_advanced.py    # Efectos avanzados
├── tiktok_batch_processor.py     # Procesamiento en batch
├── tiktok_analytics.py           # Sistema de analytics
├── tiktok_api_server.py          # API REST
├── tiktok_webhook_handler.py     # Manejador de webhooks
├── tiktok_queue_manager.py       # Gestor de cola
├── tiktok_dashboard.py           # Dashboard web
├── tiktok_notifications.py       # Sistema de notificaciones
├── tiktok_templates.py           # Templates de edición
├── tiktok_optimizer.py           # Optimizador de rendimiento
└── tiktok_requirements.txt       # Dependencias
```

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Instalar dependencias
pip install -r tiktok_requirements.txt

# Instalar FFmpeg
brew install ffmpeg  # macOS
# o
sudo apt-get install ffmpeg  # Linux
```

### 2. Configuración

```bash
# Variables de entorno esenciales
export OPENAI_API_KEY="sk-..."

# Opcionales
export TELEGRAM_BOT_TOKEN="..."
export SLACK_WEBHOOK_URL="..."
export EMAIL_SMTP_SERVER="smtp.gmail.com"
```

### 3. Uso Básico

```bash
# Procesar un video
python3 tiktok_downloader.py "https://www.tiktok.com/@user/video/123"
python3 video_script_generator.py video.mp4
python3 video_editor.py video.mp4 script.json
```

## 📚 Documentación Completa

- [Guía Principal](../docs/N8N_TIKTOK_AUTO_EDIT.md)
- [Mejoras Implementadas](../docs/MEJORAS_TIKTOK_AUTO_EDIT.md)
- [Funcionalidades Avanzadas](../docs/FUNCIONALIDADES_AVANZADAS.md)
- [API y Webhooks](../docs/API_Y_WEBHOOKS.md)
- [Dashboard y Notificaciones](../docs/DASHBOARD_Y_NOTIFICACIONES.md)
- [Templates y Optimización](../docs/TEMPLATES_Y_OPTIMIZACION.md)

## 🎬 Casos de Uso

### Caso 1: Procesamiento Individual

```bash
# Descargar y editar un video
python3 tiktok_downloader.py "URL" -o /tmp
python3 video_script_generator.py /tmp/video.mp4 -o script.json
python3 video_editor.py /tmp/video.mp4 script.json -o edited.mp4
```

### Caso 2: Procesamiento en Batch

```bash
# Crear lista de URLs
echo "https://..." > urls.txt
echo "https://..." >> urls.txt

# Procesar en batch
python3 tiktok_batch_processor.py urls.txt -w 3
```

### Caso 3: Usar API REST

```bash
# Iniciar servidor
python3 tiktok_api_server.py -p 5000

# Procesar vía API
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"url": "https://..."}'
```

### Caso 4: Sistema Completo

```bash
# Terminal 1: API
python3 tiktok_api_server.py -p 5000

# Terminal 2: Webhooks
python3 tiktok_webhook_handler.py -p 5001

# Terminal 3: Dashboard
python3 tiktok_dashboard.py -p 5002

# Terminal 4: Queue Manager
python3 tiktok_queue_manager.py start -w 3
```

## 🔧 Comandos Útiles

### Templates

```bash
# Inicializar templates
python3 tiktok_templates.py init

# Listar templates
python3 tiktok_templates.py list
```

### Optimización

```bash
# Analizar sistema
python3 tiktok_optimizer.py analyze

# Generar configuración
python3 tiktok_optimizer.py config -o config.json

# Optimizar cache
python3 tiktok_optimizer.py optimize-cache
```

### Analytics

```bash
# Ver estadísticas
python3 tiktok_analytics.py stats -d 7

# Generar reporte
python3 tiktok_analytics.py report -d 30 -o report.json

# Top URLs
python3 tiktok_analytics.py top -l 20
```

### Notificaciones

```bash
# Probar notificaciones
python3 tiktok_notifications.py test --url "https://..."

# Resumen diario
python3 tiktok_notifications.py summary
```

## 📊 Arquitectura

```
┌─────────────────────────────────────────┐
│         Dashboard Web (5002)            │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│      API REST (5000)                      │
│      Webhooks (5001)                      │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────┴───────────────────────┐
│      Queue Manager                       │
│      ┌─────────┬─────────┬─────────┐    │
│      │Worker 1 │Worker 2 │Worker 3 │    │
│      └────┬────┴────┬────┴────┬────┘    │
└───────────┼──────────┼─────────┼───────┘
            │          │         │
    ┌───────┴──────────┴─────────┴───────┐
    │   Processing Pipeline              │
    │   - Download (cache)               │
    │   - Script Generation (IA)          │
    │   - Video Editing (templates)       │
    └───────┬────────────────────────────┘
            │
    ┌───────┴─────────────────────────────┐
    │   Notificaciones │ Analytics          │
    └──────────────────────────────────────┘
```

## 🎯 Próximos Pasos

1. **Configurar variables de entorno**
2. **Inicializar templates**: `python3 tiktok_templates.py init`
3. **Optimizar sistema**: `python3 tiktok_optimizer.py config`
4. **Probar con un video**: Usar workflow básico
5. **Configurar notificaciones**: Variables de entorno
6. **Iniciar servicios**: API, Dashboard, Queue Manager

## 📞 Soporte

Para problemas:
1. Revisa los logs
2. Consulta la documentación
3. Verifica configuración
4. Usa analytics para diagnóstico

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01


