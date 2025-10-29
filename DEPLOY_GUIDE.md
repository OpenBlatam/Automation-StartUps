# 🚀 Guía de Deployment - CFDI 4.0 IA 2025

## 📋 Índice

1. [Deployment Local](#deployment-local)
2. [Deployment con Docker](#deployment-con-docker)
3. [Deployment en Producción](#deployment-en-producción)
4. [Mantenimiento](#mantenimiento)
5. [Troubleshooting](#troubleshooting)

## 💻 Deployment Local

### Prerrequisitos

- Node.js 18.x o superior
- npm 8.x o superior
- Certificados SAT (opcional)

### Paso 1: Clonar Repositorio

```bash
git clone https://github.com/blatam/cfdi-4.0-ia.git
cd cfdi-4.0-ia
```

### Paso 2: Instalar Dependencias

```bash
npm install
```

### Paso 3: Configurar Variables de Entorno

```bash
cp env.example .env
# Editar .env con tus configuraciones
```

### Paso 4: Verificar Configuración

```bash
npm run prestart
```

### Paso 5: Iniciar Servidor

```bash
# Desarrollo
npm run dev

# Producción
npm start
```

### Paso 6: Verificar

```bash
curl http://localhost:3000/api/health
```

## 🐳 Deployment con Docker

### Opción 1: Docker Simple

```bash
# Construir imagen
docker build -t cfdi-4.0-ia:latest .

# Ejecutar contenedor
docker run -d \
  --name cfdi-api \
  -p 3000:3000 \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/certificados:/app/certificados \
  cfdi-4.0-ia:latest

# Ver logs
docker logs -f cfdi-api
```

### Opción 2: Docker Compose

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener servicios
docker-compose down
```

### Opción 3: Usando Makefile

```bash
# Construir
make docker-build

# Ejecutar
make docker-run

# Con docker-compose
make docker-compose-up

# Ver logs
make docker-compose-logs

# Detener
make docker-compose-down
```

## 🌐 Deployment en Producción

### Opción 1: VPS/Server

#### Preparar Server

```bash
# Actualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Instalar PM2
sudo npm install -g pm2

# Instalar Docker (opcional)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo apt install docker-compose
```

#### Configurar Aplicación

```bash
# Clonar repositorio
git clone https://github.com/blatam/cfdi-4.0-ia.git
cd cfdi-4.0-ia

# Instalar dependencias
npm install --production

# Configurar .env
cp env.example .env
nano .env

# Configurar Nginx
sudo nano /etc/nginx/sites-available/cfdi
```

#### Nginx Configuration

```nginx
server {
    listen 80;
    listen [::]:80;
    server_name api.cfdi4ia.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

#### Iniciar con PM2

```bash
# Iniciar con PM2
pm2 start server.js --name cfdi-api

# Configurar inicio automático
pm2 startup
pm2 save

# Ver status
pm2 status

# Ver logs
pm2 logs cfdi-api
```

### Opción 2: Cloud Platforms

#### Heroku

```bash
# Instalar Heroku CLI
heroku login

# Crear app
heroku create cfdi-api

# Configurar variables
heroku config:set JWT_SECRET=your-secret
heroku config:set NODE_ENV=production

# Deploy
git push heroku main

# Ver logs
heroku logs --tail
```

#### AWS Elastic Beanstalk

```bash
# Instalar EB CLI
pip install awsebcli

# Inicializar EB
eb init -p node.js

# Crear entorno
eb create cfdi-api-env

# Deploy
eb deploy

# Ver logs
eb logs
```

#### Google Cloud Run

```bash
# Instalar gcloud CLI
gcloud auth login

# Build y deploy
gcloud run deploy cfdi-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### Railway

```bash
# Instalar Railway CLI
npm i -g @railway/cli

# Login
railway login

# Deploy
railway up

# Ver logs
railway logs
```

### Opción 3: Kubernetes

#### Preparar Cluster

```bash
# Crear deployment
kubectl create deployment cfdi-api \
  --image=blatam/cfdi-4.0-ia:latest

# Exponer servicio
kubectl expose deployment cfdi-api \
  --type=LoadBalancer \
  --port=80 \
  --target-port=3000

# Verificar
kubectl get pods
kubectl get services
```

## 🔧 Mantenimiento

### Actualizar Aplicación

```bash
# Local
git pull origin main
npm install
npm restart

# Docker
docker-compose pull
docker-compose up -d --build

# PM2
pm2 restart cfdi-api
```

### Backup

```bash
# Hacer backup
tar -czf backup-$(date +%Y%m%d).tar.gz \
  data/ logs/ certificados/

# Restaurar backup
tar -xzf backup-YYYYMMDD.tar.gz
```

### Monitoreo

```bash
# Ver logs
pm2 logs cfdi-api

# Stats
pm2 monit

# Health check
curl http://localhost:3000/api/health
```

### Limpieza

```bash
# Limpiar Docker
docker system prune -a

# Limpiar node_modules
npm run clean
```

## 🐛 Troubleshooting

### Problema: Puerto en uso

```bash
# Encontrar proceso
lsof -i :3000

# Matar proceso
kill -9 PID
```

### Problema: Permisos

```bash
# Dar permisos a certificados
chmod 600 certificados/*.key
chmod 644 certificados/*.cer
```

### Problema: Variables de entorno

```bash
# Verificar variables
env | grep CFDI

# Recargar .env
export $(cat .env | xargs)
```

### Problema: Conexión a base de datos

```bash
# Probar conexión
npm run test:db

# Ver logs
tail -f logs/cfdi.log
```

### Problema: Contenedor no inicia

```bash
# Ver logs del contenedor
docker logs cfdi-api

# Ver logs de docker-compose
docker-compose logs

# Reiniciar contenedor
docker restart cfdi-api
```

## 📊 Monitoreo y Métricas

### Métricas del Sistema

```bash
# CPU y Memoria
top
htop

# Espacio en disco
df -h

# Uso de red
iftop
```

### Métricas de la Aplicación

```bash
# API Metrics
curl http://localhost:3000/api/protected/stats

# Dashboard
curl http://localhost:3000/api/protected/dashboard
```

### Alertas

Configurar alertas para:
- CPU > 80%
- Memoria > 80%
- Espacio en disco < 20%
- Errores en logs
- Health check failed

## 🔒 Seguridad

### Configurar HTTPS

```bash
# Usar Let's Encrypt
sudo certbot --nginx -d api.cfdi4ia.com
```

### Configurar Firewall

```bash
# UFW
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Secrets Management

```bash
# Usar variables de entorno
export JWT_SECRET=$(openssl rand -hex 32)

# O usar secrets manager
# AWS Secrets Manager
# Google Secret Manager
# Azure Key Vault
```

## ✅ Checklist de Deployment

### Pre-Deployment
- [ ] Código actualizado y probado
- [ ] Tests pasando
- [ ] Variables de entorno configuradas
- [ ] Certificados SAT configurados
- [ ] Backup realizado

### Deployment
- [ ] Servidor configurado
- [ ] Dependencias instaladas
- [ ] Aplicación iniciada
- [ ] Health check exitoso
- [ ] Logs verificados

### Post-Deployment
- [ ] Monitoreo configurado
- [ ] Alertas configuradas
- [ ] Backup automático configurado
- [ ] Documentación actualizada
- [ ] Equipo notificado

---

**¡Deployment completado exitosamente! 🎉**



