# Deployment y Seguridad - TikTok Auto Edit

## 🐳 Docker Deployment

### Build y Run

```bash
# Build de imagen
docker build -t tiktok-auto-edit .

# Run container
docker run -d \
  -p 5000:5000 \
  -e OPENAI_API_KEY="sk-..." \
  -v $(pwd):/app \
  --name tiktok-api \
  tiktok-auto-edit
```

### Docker Compose

```bash
# Deploy completo
./deploy.sh

# O manualmente
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Servicios en Docker

- **api**: API REST (puerto 5000)
- **webhook**: Webhook handler (puerto 5001)
- **dashboard**: Dashboard web (puerto 5002)
- **queue**: Queue manager (background)

## 🔒 Seguridad

### Validación de URLs

```python
from security_config import SecurityManager

manager = SecurityManager()
valid, error = manager.validate_tiktok_url(url)

if not valid:
    print(f"Error: {error}")
```

### Rate Limiting

```python
from security_config import SecurityManager, rate_limit_decorator

manager = SecurityManager()

# Verificar rate limit
can_proceed, remaining = manager.check_rate_limit(ip_address)

# Decorador
@rate_limit_decorator(max_requests=60, window_seconds=60)
def my_function(identifier):
    # Tu código aquí
    pass
```

### Verificación de Webhooks

```python
from security_config import SecurityManager

manager = SecurityManager()

# Verificar firma
valid = manager.verify_webhook_signature(
    payload=request.data,
    signature=request.headers.get('X-Signature'),
    secret=WEBHOOK_SECRET
)
```

### Sanitización de Archivos

```python
from security_config import SecurityManager

manager = SecurityManager()

# Sanitizar nombre de archivo
safe_name = manager.sanitize_filename(user_input)
```

## 🛡️ Mejores Prácticas de Seguridad

### 1. Variables de Entorno

Nunca hardcodees credenciales:

```bash
# ✅ Correcto
export OPENAI_API_KEY="sk-..."

# ❌ Incorrecto
OPENAI_API_KEY="sk-..."  # En código
```

### 2. Rate Limiting

Configura límites apropiados:

```bash
export MAX_REQUESTS_PER_MINUTE=60
export BLOCK_DURATION_MINUTES=60
```

### 3. Webhook Secrets

Usa secrets fuertes:

```bash
export WEBHOOK_SECRET=$(openssl rand -hex 32)
```

### 4. Validación de Input

Siempre valida URLs y datos de entrada:

```python
valid, error = manager.validate_tiktok_url(url)
if not valid:
    return error_response(error)
```

### 5. Sanitización

Sanitiza nombres de archivo y paths:

```python
safe_path = manager.sanitize_filename(user_filename)
```

## 🚀 Deployment en Producción

### Opción 1: Docker Compose

```bash
# 1. Configurar .env
cp .env.example .env
# Editar .env con tus credenciales

# 2. Deploy
./deploy.sh

# 3. Verificar
docker-compose ps
curl http://localhost:5000/health
```

### Opción 2: Kubernetes

```yaml
# Ejemplo de deployment (crear según necesidad)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tiktok-api
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: api
        image: tiktok-auto-edit:latest
        ports:
        - containerPort: 5000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: tiktok-secrets
              key: openai-api-key
```

### Opción 3: systemd Services

```ini
[Unit]
Description=TikTok API Server
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/tiktok
Environment="OPENAI_API_KEY=sk-..."
ExecStart=/usr/bin/python3 tiktok_api_server.py -p 5000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## 📊 Monitoreo de Seguridad

### Logs de Seguridad

Todos los eventos de seguridad se registran:

```python
logger.warning(f"Rate limit excedido para {ip}")
logger.error(f"Firma de webhook inválida")
logger.info(f"URL validada: {url}")
```

### Alertas

Configura alertas para:
- Rate limits excedidos frecuentemente
- Firmas de webhook inválidas
- URLs sospechosas
- Errores de seguridad

## 🔐 Configuración de Seguridad Avanzada

### Firewall

```bash
# Permitir solo puertos necesarios
ufw allow 5000/tcp  # API
ufw allow 5001/tcp  # Webhooks
ufw allow 5002/tcp  # Dashboard
ufw enable
```

### SSL/TLS

Para producción, usa reverse proxy con SSL:

```nginx
# nginx.conf
server {
    listen 443 ssl;
    server_name api.tiktok-edit.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Autenticación API

Agrega autenticación a la API:

```python
from functools import wraps
from flask import request, jsonify

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.getenv('API_KEY'):
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/v1/process', methods=['POST'])
@require_api_key
def process_complete():
    # ...
```

## 🧪 Testing de Seguridad

```bash
# Validar URL
python3 security_config.py validate-url -u "https://..."

# Test rate limit
python3 security_config.py rate-limit -i "test_ip"

# Test signature
python3 security_config.py signature
```

## 📝 Checklist de Seguridad

- [ ] Variables de entorno configuradas
- [ ] Rate limiting habilitado
- [ ] Webhook secrets configurados
- [ ] Validación de URLs implementada
- [ ] Sanitización de archivos activa
- [ ] Logs de seguridad configurados
- [ ] Firewall configurado
- [ ] SSL/TLS en producción
- [ ] Autenticación API (si es necesario)
- [ ] Backups regulares
- [ ] Monitoreo de seguridad activo

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01

