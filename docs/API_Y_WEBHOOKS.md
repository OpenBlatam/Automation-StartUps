# API REST y Webhooks - TikTok Auto Edit

## 🚀 API REST

### Iniciar Servidor

```bash
python3 tiktok_api_server.py -p 5000
```

### Endpoints Disponibles

#### Health Check
```http
GET /health
```

**Respuesta:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "3.0"
}
```

#### Descargar Video
```http
POST /api/v1/download
Content-Type: application/json

{
  "url": "https://www.tiktok.com/@user/video/123"
}
```

**Respuesta:**
```json
{
  "success": true,
  "file_path": "/tmp/video.mp4",
  "file_size": 1024000,
  "duration": 15.3,
  "from_cache": false
}
```

#### Generar Script
```http
POST /api/v1/generate-script
Content-Type: application/json

{
  "video_path": "/tmp/video.mp4",
  "num_frames": 10
}
```

#### Editar Video
```http
POST /api/v1/edit
Content-Type: application/json

{
  "video_path": "/tmp/video.mp4",
  "script": { ... },
  "output_filename": "edited.mp4"
}
```

#### Procesar Completo
```http
POST /api/v1/process
Content-Type: application/json

{
  "url": "https://www.tiktok.com/@user/video/123",
  "num_frames": 10
}
```

**Respuesta:**
```json
{
  "success": true,
  "download": { ... },
  "script": { ... },
  "edit": { ... },
  "processing_time": 125.5
}
```

#### Analytics - Estadísticas
```http
GET /api/v1/analytics/stats?days=7
```

#### Analytics - Top URLs
```http
GET /api/v1/analytics/top?limit=10
```

#### Comprimir Video
```http
POST /api/v1/compress
Content-Type: application/json

{
  "input_path": "/tmp/video.mp4",
  "target_size_mb": 50,
  "quality": "medium"
}
```

#### Descargar Video Procesado
```http
GET /api/v1/video/filename.mp4
```

## 🔔 Webhooks

### Iniciar Handler

```bash
export WEBHOOK_SECRET="tu-secret-aqui"
python3 tiktok_webhook_handler.py -p 5001
```

### Endpoints de Webhook

#### TikTok Webhook
```http
POST /webhook/tiktok
X-Signature: <hmac-sha256-signature>
Content-Type: application/json

{
  "url": "https://www.tiktok.com/@user/video/123"
}
```

#### Telegram Webhook
```http
POST /webhook/telegram
Content-Type: application/json

{
  "message": {
    "text": "https://www.tiktok.com/@user/video/123",
    "chat": {
      "id": 123456789
    }
  }
}
```

#### WhatsApp Webhook
```http
POST /webhook/whatsapp
Content-Type: application/json

{
  "Body": "https://www.tiktok.com/@user/video/123",
  "From": "+1234567890"
}
```

#### Health Check
```http
GET /webhook/health
```

### Verificación de Firma

Los webhooks pueden verificar firmas HMAC-SHA256:

```python
import hmac
import hashlib

secret = "tu-secret"
payload = b'{"url": "..."}'
signature = hmac.new(
    secret.encode('utf-8'),
    payload,
    hashlib.sha256
).hexdigest()

# Enviar en header: X-Signature
```

## 📋 Sistema de Cola

### Iniciar Gestor de Cola

```bash
python3 tiktok_queue_manager.py start -w 3
```

### Agregar Trabajo

```bash
python3 tiktok_queue_manager.py add -u "https://www.tiktok.com/@user/video/123" -p 8
```

### Ver Estadísticas

```bash
python3 tiktok_queue_manager.py stats
```

### Listar Trabajos

```bash
python3 tiktok_queue_manager.py list
```

### API de Cola (Python)

```python
from tiktok_queue_manager import TikTokQueueManager

manager = TikTokQueueManager(max_workers=3)

# Agregar trabajo
job_id = manager.add_job(
    url="https://www.tiktok.com/@user/video/123",
    priority=8,  # 1-10, mayor = más prioritario
    max_retries=3
)

# Iniciar workers
manager.start()

# Obtener estadísticas
stats = manager.get_queue_stats()
print(f"Pendientes: {stats['pending']}")
print(f"Procesando: {stats['processing']}")
print(f"Completados: {stats['completed']}")
```

## 🔧 Integración

### Ejemplo con cURL

```bash
# Procesar video
curl -X POST http://localhost:5000/api/v1/process \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.tiktok.com/@user/video/123"}'

# Ver estadísticas
curl http://localhost:5000/api/v1/analytics/stats?days=7
```

### Ejemplo con Python

```python
import requests

# Procesar video
response = requests.post(
    'http://localhost:5000/api/v1/process',
    json={'url': 'https://www.tiktok.com/@user/video/123'}
)
result = response.json()

if result['success']:
    print(f"Video procesado: {result['edit']['output_path']}")
```

### Ejemplo con JavaScript

```javascript
// Procesar video
fetch('http://localhost:5000/api/v1/process', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://www.tiktok.com/@user/video/123'
  })
})
.then(res => res.json())
.then(data => {
  console.log('Video procesado:', data);
});
```

## 🔒 Seguridad

### Autenticación

Para producción, agrega autenticación:

```python
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token or token != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/process', methods=['POST'])
@require_auth
def process_complete():
    # ...
```

### Rate Limiting

Implementa rate limiting para evitar abusos:

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["100 per hour"]
)

@app.route('/api/v1/process', methods=['POST'])
@limiter.limit("10 per minute")
def process_complete():
    # ...
```

## 📊 Monitoreo

### Logs

Los logs se escriben en stdout. Para producción:

```bash
python3 tiktok_api_server.py -p 5000 2>&1 | tee api.log
```

### Métricas

Usa el endpoint de analytics para monitoreo:

```bash
# Script de monitoreo
while true; do
  curl -s http://localhost:5000/api/v1/analytics/stats?days=1 | jq
  sleep 60
done
```

## 🚀 Despliegue

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "tiktok_api_server.py", "-p", "5000"]
```

### systemd Service

```ini
[Unit]
Description=TikTok API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tiktok-api
ExecStart=/usr/bin/python3 tiktok_api_server.py -p 5000
Restart=always

[Install]
WantedBy=multi-user.target
```

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01


