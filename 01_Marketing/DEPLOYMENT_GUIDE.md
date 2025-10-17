# Guía de Despliegue - Sistema de Feedback de IA Marketing

## 🚀 Descripción General

Esta guía proporciona instrucciones detalladas para desplegar el Sistema de Integración de Feedback de Clientes para IA Marketing en diferentes entornos (desarrollo, staging, producción).

## 📋 Prerrequisitos

### Requisitos del Sistema
- **Node.js**: >= 18.0.0
- **npm**: >= 8.0.0
- **PostgreSQL**: >= 13.0
- **Redis**: >= 6.0
- **Docker**: >= 20.0 (opcional)
- **Git**: >= 2.30

### Requisitos de Hardware
- **CPU**: 2+ cores
- **RAM**: 4GB+ (8GB+ recomendado para producción)
- **Almacenamiento**: 20GB+ SSD
- **Red**: Conexión estable a internet

## 🛠️ Instalación

### 1. Clonar el Repositorio
```bash
git clone https://github.com/adan/ai-marketing-feedback-system.git
cd ai-marketing-feedback-system
```

### 2. Instalar Dependencias
```bash
npm install
```

### 3. Configurar Variables de Entorno
```bash
cp env.example .env
# Editar .env con tus configuraciones
```

### 4. Configurar Base de Datos
```bash
# Crear base de datos PostgreSQL
createdb ai_marketing_feedback_db

# Ejecutar migraciones
npm run db:migrate

# Generar cliente Prisma
npm run db:generate

# Poblar datos iniciales (opcional)
npm run db:seed
```

### 5. Configurar Redis
```bash
# Instalar Redis
# Ubuntu/Debian
sudo apt-get install redis-server

# macOS
brew install redis

# Iniciar Redis
redis-server
```

## 🐳 Despliegue con Docker

### 1. Construir Imagen
```bash
docker build -t ai-marketing-feedback .
```

### 2. Ejecutar con Docker Compose
```bash
# Desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Producción
docker-compose -f docker-compose.prod.yml up -d
```

### 3. Verificar Despliegue
```bash
# Verificar contenedores
docker-compose ps

# Ver logs
docker-compose logs -f app

# Verificar salud
curl http://localhost:3001/health
```

## 🌐 Despliegue en la Nube

### AWS EC2
```bash
# 1. Crear instancia EC2 (t3.medium o superior)
# 2. Conectar via SSH
ssh -i your-key.pem ubuntu@your-ec2-ip

# 3. Instalar dependencias
sudo apt update
sudo apt install nodejs npm postgresql redis-server nginx

# 4. Clonar y configurar aplicación
git clone https://github.com/adan/ai-marketing-feedback-system.git
cd ai-marketing-feedback-system
npm install
npm run build

# 5. Configurar Nginx
sudo nano /etc/nginx/sites-available/ai-marketing-feedback
```

### Google Cloud Platform
```bash
# 1. Crear instancia Compute Engine
# 2. Configurar firewall
gcloud compute firewall-rules create allow-feedback-api \
  --allow tcp:3001 \
  --source-ranges 0.0.0.0/0

# 3. Desplegar aplicación
gcloud compute instances create-with-container feedback-api \
  --container-image gcr.io/your-project/ai-marketing-feedback \
  --machine-type e2-medium \
  --zone us-central1-a
```

### Azure
```bash
# 1. Crear App Service
az webapp create \
  --resource-group myResourceGroup \
  --plan myAppServicePlan \
  --name ai-marketing-feedback \
  --deployment-local-git

# 2. Configurar variables de entorno
az webapp config appsettings set \
  --resource-group myResourceGroup \
  --name ai-marketing-feedback \
  --settings NODE_ENV=production
```

## 🔧 Configuración de Producción

### 1. Variables de Entorno Críticas
```env
# Producción
NODE_ENV=production
PORT=3001
HOST=0.0.0.0

# Base de datos
DATABASE_URL=postgresql://user:password@host:5432/db

# Seguridad
JWT_SECRET=your_super_secure_jwt_secret_here
BCRYPT_ROUNDS=12

# CORS
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate Limiting
RATE_LIMIT_MAX_REQUESTS=1000
FEEDBACK_RATE_LIMIT_MAX=100

# APIs Externas
OPENAI_API_KEY=your_openai_api_key
GOOGLE_CLOUD_API_KEY=your_google_cloud_key
```

### 2. Configuración de Nginx
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    # Redireccionar HTTP a HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;
    
    # Certificados SSL
    ssl_certificate /path/to/certificate.crt;
    ssl_certificate_key /path/to/private.key;
    
    # Configuración SSL
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
    ssl_prefer_server_ciphers off;
    
    # Proxy a la aplicación
    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # WebSocket
    location /ws {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Configuración de PM2
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'ai-marketing-feedback',
    script: 'dist/server.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'development'
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3001
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
```

```bash
# Instalar PM2
npm install -g pm2

# Iniciar aplicación
pm2 start ecosystem.config.js --env production

# Configurar inicio automático
pm2 startup
pm2 save
```

## 📊 Monitoreo y Logging

### 1. Configuración de Logs
```bash
# Crear directorio de logs
mkdir -p logs

# Configurar logrotate
sudo nano /etc/logrotate.d/ai-marketing-feedback
```

```bash
# /etc/logrotate.d/ai-marketing-feedback
/path/to/app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 nodejs nodejs
    postrotate
        pm2 reloadLogs
    endscript
}
```

### 2. Configuración de Prometheus
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-marketing-feedback'
    static_configs:
      - targets: ['localhost:3001']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

### 3. Configuración de Grafana
```json
{
  "dashboard": {
    "title": "AI Marketing Feedback System",
    "panels": [
      {
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ]
      }
    ]
  }
}
```

## 🔒 Seguridad

### 1. Configuración de Firewall
```bash
# UFW (Ubuntu)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw deny 3001  # Bloquear acceso directo al puerto de la app
```

### 2. Configuración de SSL
```bash
# Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com
```

### 3. Configuración de Base de Datos
```sql
-- Crear usuario específico para la aplicación
CREATE USER feedback_app WITH PASSWORD 'secure_password';
GRANT CONNECT ON DATABASE ai_marketing_feedback_db TO feedback_app;
GRANT USAGE ON SCHEMA public TO feedback_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO feedback_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO feedback_app;
```

## 📈 Escalabilidad

### 1. Load Balancer (Nginx)
```nginx
upstream feedback_backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://feedback_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### 2. Clúster de Base de Datos
```yaml
# docker-compose.cluster.yml
version: '3.8'
services:
  postgres-master:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_marketing_feedback_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_master_data:/var/lib/postgresql/data
  
  postgres-slave:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_marketing_feedback_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_slave_data:/var/lib/postgresql/data
```

### 3. Redis Cluster
```yaml
# redis-cluster.yml
version: '3.8'
services:
  redis-node-1:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000 --appendonly yes --port 7001
    ports:
      - "7001:7001"
  
  redis-node-2:
    image: redis:7-alpine
    command: redis-server --cluster-enabled yes --cluster-config-file nodes.conf --cluster-node-timeout 5000 --appendonly yes --port 7002
    ports:
      - "7002:7002"
```

## 🚀 CI/CD Pipeline

### 1. GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Build application
      run: npm run build
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/app
          git pull origin main
          npm ci
          npm run build
          pm2 restart ai-marketing-feedback
```

### 2. Docker Hub
```bash
# Construir y subir imagen
docker build -t yourusername/ai-marketing-feedback .
docker push yourusername/ai-marketing-feedback

# Desplegar en servidor
docker pull yourusername/ai-marketing-feedback
docker run -d -p 3001:3001 yourusername/ai-marketing-feedback
```

## 🔍 Troubleshooting

### Problemas Comunes

#### 1. Error de Conexión a Base de Datos
```bash
# Verificar estado de PostgreSQL
sudo systemctl status postgresql

# Verificar conexión
psql -h localhost -U postgres -d ai_marketing_feedback_db

# Verificar logs
sudo journalctl -u postgresql
```

#### 2. Error de Conexión a Redis
```bash
# Verificar estado de Redis
sudo systemctl status redis

# Verificar conexión
redis-cli ping

# Verificar logs
sudo journalctl -u redis
```

#### 3. Error de Memoria
```bash
# Verificar uso de memoria
free -h
htop

# Aumentar límite de memoria de Node.js
export NODE_OPTIONS="--max-old-space-size=4096"
```

#### 4. Error de Puerto en Uso
```bash
# Verificar puerto en uso
sudo netstat -tulpn | grep :3001

# Matar proceso
sudo kill -9 $(sudo lsof -t -i:3001)
```

### Logs de Debugging
```bash
# Logs de la aplicación
pm2 logs ai-marketing-feedback

# Logs de Nginx
sudo tail -f /var/log/nginx/error.log

# Logs del sistema
sudo journalctl -f
```

## 📚 Comandos Útiles

### Desarrollo
```bash
# Iniciar en modo desarrollo
npm run dev

# Ejecutar tests
npm test

# Linting
npm run lint

# Formateo
npm run format
```

### Producción
```bash
# Iniciar aplicación
pm2 start ecosystem.config.js --env production

# Reiniciar aplicación
pm2 restart ai-marketing-feedback

# Ver estado
pm2 status

# Ver logs
pm2 logs ai-marketing-feedback

# Monitorear
pm2 monit
```

### Base de Datos
```bash
# Migrar
npm run db:migrate

# Generar cliente
npm run db:generate

# Studio
npm run db:studio

# Backup
pg_dump ai_marketing_feedback_db > backup.sql

# Restore
psql ai_marketing_feedback_db < backup.sql
```

## 📞 Soporte

Para soporte técnico o preguntas sobre el despliegue:

- **Email**: soporte@ai-marketing-feedback.com
- **Documentación**: https://docs.ai-marketing-feedback.com
- **Issues**: https://github.com/adan/ai-marketing-feedback-system/issues
- **Discord**: https://discord.gg/ai-marketing-feedback

---

**¡Despliegue exitoso! 🎉**

El sistema está listo para procesar feedback de clientes en tiempo real con análisis de IA avanzado.
