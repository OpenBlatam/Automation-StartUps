# Dashboard y Notificaciones - TikTok Auto Edit

## 🎨 Dashboard Web

### Iniciar Dashboard

```bash
python3 tiktok_dashboard.py -p 5002
```

Luego abre en el navegador: `http://localhost:5002`

### Características

- ✅ **Estadísticas en tiempo real**: Métricas actualizadas automáticamente
- ✅ **Vista de cola**: Estado de trabajos pendientes y procesando
- ✅ **Top URLs**: URLs más procesadas
- ✅ **Actividad reciente**: Últimos trabajos procesados
- ✅ **Auto-refresh**: Actualización cada 30 segundos
- ✅ **Diseño moderno**: Interfaz responsive y atractiva

### Métricas Mostradas

1. **Total Procesados**: Número total de videos procesados
2. **Tasa de Éxito**: Porcentaje de videos procesados exitosamente
3. **Tiempo Promedio**: Tiempo promedio de procesamiento
4. **Cache Hit Rate**: Porcentaje de hits de cache

### API del Dashboard

```http
GET /api/dashboard/stats?days=7
GET /api/dashboard/queue
GET /api/dashboard/top?limit=10
GET /api/dashboard/recent
```

## 📧 Sistema de Notificaciones

### Configuración

```bash
# Telegram
export TELEGRAM_BOT_TOKEN="tu-bot-token"
export TELEGRAM_CHAT_ID="tu-chat-id"

# Slack
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."

# Email
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_USER="tu-email@gmail.com"
export EMAIL_PASSWORD="tu-password"
export EMAIL_TO="destinatario1@email.com,destinatario2@email.com"
```

### Tipos de Notificaciones

#### 1. Inicio de Procesamiento
Se envía cuando comienza a procesarse un video.

**Canales**: Telegram, Slack

#### 2. Completación Exitosa
Se envía cuando un video se procesa exitosamente.

**Canales**: Telegram, Slack, Email

**Información incluida**:
- URL del video
- Tiempo de procesamiento
- Tamaño del archivo
- Ruta del video editado

#### 3. Error en Procesamiento
Se envía cuando falla el procesamiento.

**Canales**: Telegram, Slack, Email

**Información incluida**:
- URL del video
- Mensaje de error
- Número de reintentos

#### 4. Estado de Cola
Se envía cuando hay muchos trabajos pendientes o fallidos.

**Canales**: Telegram, Slack

**Triggers**:
- Más de 10 trabajos pendientes
- Más de 5 trabajos fallidos

#### 5. Resumen Diario
Se envía al final del día con estadísticas.

**Canales**: Telegram, Slack, Email

**Información incluida**:
- Total procesado
- Exitosos vs fallidos
- Tasa de éxito
- Tiempo promedio

### Uso Programático

```python
from tiktok_notifications import NotificationManager

manager = NotificationManager()

# Notificar inicio
manager.notify_processing_started("https://www.tiktok.com/@user/video/123")

# Notificar completación
manager.notify_processing_completed(
    "https://www.tiktok.com/@user/video/123",
    {
        'processing_time': 120.5,
        'file_size': 1024000,
        'video_path': '/tmp/video.mp4'
    }
)

# Notificar error
manager.notify_processing_failed(
    "https://www.tiktok.com/@user/video/123",
    "Error al descargar video",
    retry_count=2
)

# Resumen diario
from tiktok_analytics import TikTokAnalytics
analytics = TikTokAnalytics()
stats = analytics.get_stats(1)
manager.notify_daily_summary(stats)
```

### Integración Automática

El sistema de notificaciones se integra automáticamente con:
- ✅ **Queue Manager**: Notifica inicio, completación y errores
- ✅ **Analytics**: Puede enviar resúmenes periódicos
- ✅ **API Server**: Puede notificar eventos importantes

### Ejemplo de Notificación Telegram

```
🎬 Procesamiento Iniciado

URL: https://www.tiktok.com/@user/video/123
Job ID: 42
Tiempo: 2024-01-01 12:00:00
```

### Ejemplo de Notificación Email

```html
<h2>Video Procesado Exitosamente</h2>
<p><strong>URL:</strong> https://www.tiktok.com/@user/video/123</p>
<p><strong>Tiempo de procesamiento:</strong> 120.5 segundos</p>
<p><strong>Tamaño del archivo:</strong> 1.00 MB</p>
<p><strong>Ruta del video:</strong> /tmp/video_edited.mp4</p>
```

## 🔧 Configuración Avanzada

### Programar Resumen Diario

Usa cron o systemd timer:

```bash
# Cron job para resumen diario a las 23:00
0 23 * * * /usr/bin/python3 /path/to/tiktok_notifications.py summary
```

### Personalizar Notificaciones

Edita `tiktok_notifications.py` para:
- Agregar más canales (Discord, Teams, etc.)
- Personalizar mensajes
- Agregar más información
- Cambiar triggers

### Dashboard Personalizado

El dashboard usa HTML/CSS/JS simple. Puedes:
- Modificar el diseño
- Agregar más gráficos
- Integrar con otras APIs
- Agregar autenticación

## 📊 Monitoreo

### Health Checks

```bash
# Dashboard
curl http://localhost:5002/api/dashboard/stats

# API
curl http://localhost:5000/health

# Webhooks
curl http://localhost:5001/webhook/health
```

### Logs

Todos los servicios escriben logs estructurados:

```bash
# Ver logs en tiempo real
tail -f api.log dashboard.log queue.log
```

## 🚀 Despliegue Completo

### Iniciar Todos los Servicios

```bash
# Terminal 1: API REST
python3 tiktok_api_server.py -p 5000

# Terminal 2: Webhooks
python3 tiktok_webhook_handler.py -p 5001

# Terminal 3: Dashboard
python3 tiktok_dashboard.py -p 5002

# Terminal 4: Queue Manager
python3 tiktok_queue_manager.py start -w 3
```

### Con systemd

Crea servicios systemd para cada componente:

```ini
[Unit]
Description=TikTok Dashboard
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/tiktok/tiktok_dashboard.py -p 5002
Restart=always

[Install]
WantedBy=multi-user.target
```

## 📱 Acceso Móvil

El dashboard es responsive y funciona en móviles:
- Abre `http://tu-servidor:5002` en tu móvil
- Interfaz adaptativa
- Auto-refresh funciona igual

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01


