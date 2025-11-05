# 🚀 Deployment Guide
## Complete Deployment Documentation for AI Marketing Course & SaaS Platform

This guide provides comprehensive instructions for deploying the AI Marketing Course & SaaS Platform in various environments.

---

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Environment Setup](#environment-setup)
- [Local Development](#local-development)
- [Staging Deployment](#staging-deployment)
- [Production Deployment](#production-deployment)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [Monitoring & Maintenance](#monitoring--maintenance)
- [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### **System Requirements**
- **Node.js**: 18.0.0 or higher
- **npm**: 8.0.0 or higher
- **PostgreSQL**: 15.0 or higher
- **Redis**: 6.0 or higher
- **Docker**: 20.10 or higher (optional)
- **Kubernetes**: 1.24 or higher (optional)

### **Cloud Requirements**
- **AWS Account** (or Google Cloud/Azure)
- **Domain Name** (for production)
- **SSL Certificate** (Let's Encrypt or commercial)
- **CDN Service** (CloudFlare recommended)

### **API Keys Required**
- **Copy.ai API Key**: [Get from Copy.ai](https://copy.ai)
- **OpenAI API Key**: [Get from OpenAI](https://openai.com) (optional)
- **Email Service**: SMTP credentials or service API
- **File Storage**: AWS S3 or similar service

---

## 🌍 Environment Setup

### **Environment Variables**
Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://username:password@localhost:5432/ai_marketing_saas
DATABASE_POOL_MIN=2
DATABASE_POOL_MAX=10

# Redis
REDIS_URL=redis://localhost:6379
REDIS_PASSWORD=your_redis_password

# JWT
JWT_SECRET=your_super_secret_jwt_key_here
JWT_EXPIRES_IN=7d

# Copy.ai API
COPY_AI_API_KEY=your_copy_ai_api_key
COPY_AI_BASE_URL=https://api.copy.ai/v1

# OpenAI API (optional)
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=https://api.openai.com/v1

# Email Service
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
EMAIL_FROM=noreply@yourdomain.com

# File Storage
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_S3_BUCKET=your_s3_bucket
AWS_REGION=us-east-1

# Application
NODE_ENV=development
PORT=3000
API_BASE_URL=http://localhost:3000/api
FRONTEND_URL=http://localhost:3000

# Monitoring
SENTRY_DSN=your_sentry_dsn
DATADOG_API_KEY=your_datadog_api_key

# Security
CORS_ORIGIN=http://localhost:3000
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### **Database Setup**
```bash
# Install PostgreSQL
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS
brew install postgresql

# Start PostgreSQL
sudo systemctl start postgresql  # Linux
brew services start postgresql   # macOS

# Create database
sudo -u postgres psql
CREATE DATABASE ai_marketing_saas;
CREATE USER ai_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE ai_marketing_saas TO ai_user;
\q
```

### **Redis Setup**
```bash
# Install Redis
# Ubuntu/Debian
sudo apt install redis-server

# macOS
brew install redis

# Start Redis
sudo systemctl start redis-server  # Linux
brew services start redis          # macOS

# Test Redis
redis-cli ping
```

---

## 💻 Local Development

### **1. Clone Repository**
```bash
git clone https://github.com/your-username/ai-marketing-course-saas.git
cd ai-marketing-course-saas
```

### **2. Install Dependencies**
```bash
# Install backend dependencies
cd backend
npm install

# Install frontend dependencies
cd ../frontend
npm install

# Install root dependencies
cd ..
npm install
```

### **3. Database Migration**
```bash
# Run database migrations
npm run db:migrate

# Seed initial data
npm run db:seed
```

### **4. Start Development Servers**
```bash
# Start all services (recommended)
npm run dev

# Or start individually
# Backend only
npm run dev:backend

# Frontend only
npm run dev:frontend
```

### **5. Verify Installation**
- Frontend: http://localhost:3000
- Backend API: http://localhost:3000/api
- API Documentation: http://localhost:3000/api/docs

---

## 🧪 Staging Deployment

### **1. Prepare Staging Environment**
```bash
# Create staging branch
git checkout -b staging
git push origin staging

# Set up staging environment variables
cp .env.example .env.staging
# Edit .env.staging with staging values
```

### **2. Deploy to Staging**
```bash
# Build application
npm run build:staging

# Deploy to staging server
npm run deploy:staging
```

### **3. Staging Configuration**
```yaml
# staging.yml
environment: staging
database:
  url: postgresql://staging_user:password@staging-db:5432/ai_marketing_saas_staging
redis:
  url: redis://staging-redis:6379
api:
  base_url: https://staging-api.yourdomain.com
frontend:
  url: https://staging.yourdomain.com
monitoring:
  enabled: true
  level: debug
```

### **4. Staging Verification**
- [ ] All services running
- [ ] Database connected
- [ ] Redis connected
- [ ] Copy.ai API working
- [ ] Email service working
- [ ] File storage working

---

## 🏭 Production Deployment

### **1. Production Environment Setup**

#### **Server Requirements**
- **CPU**: 4+ cores
- **RAM**: 8+ GB
- **Storage**: 100+ GB SSD
- **Network**: 1+ Gbps
- **OS**: Ubuntu 20.04 LTS or CentOS 8+

#### **Load Balancer Setup (Nginx)**
```nginx
# /etc/nginx/sites-available/ai-marketing-saas
upstream backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### **2. SSL Certificate Setup**
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

### **3. Application Deployment**
```bash
# Clone repository
git clone https://github.com/your-username/ai-marketing-course-saas.git
cd ai-marketing-course-saas

# Install dependencies
npm ci --production

# Build application
npm run build:production

# Set up environment
cp .env.production .env

# Run database migrations
npm run db:migrate:production

# Start application with PM2
npm install -g pm2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

### **4. PM2 Configuration**
```javascript
// ecosystem.config.js
module.exports = {
  apps: [{
    name: 'ai-marketing-saas',
    script: './dist/index.js',
    instances: 'max',
    exec_mode: 'cluster',
    env: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    env_production: {
      NODE_ENV: 'production',
      PORT: 3000
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true
  }]
};
```

---

## 🐳 Docker Deployment

### **1. Dockerfile**
```dockerfile
# Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine AS production

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy built application
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001

# Change ownership
RUN chown -R nextjs:nodejs /app
USER nextjs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1

# Start application
CMD ["node", "dist/index.js"]
```

### **2. Docker Compose**
```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://postgres:password@db:5432/ai_marketing_saas
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  db:
    image: postgres:15-alpine
    environment:
      - POSTGRES_DB=ai_marketing_saas
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### **3. Deploy with Docker**
```bash
# Build and start services
docker-compose up -d

# View logs
docker-compose logs -f

# Scale application
docker-compose up -d --scale app=3

# Stop services
docker-compose down
```

---

## ☸️ Kubernetes Deployment

### **1. Namespace**
```yaml
# namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-marketing-saas
```

### **2. ConfigMap**
```yaml
# configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-marketing-saas-config
  namespace: ai-marketing-saas
data:
  NODE_ENV: "production"
  PORT: "3000"
  API_BASE_URL: "https://api.yourdomain.com"
  FRONTEND_URL: "https://yourdomain.com"
```

### **3. Secret**
```yaml
# secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-marketing-saas-secret
  namespace: ai-marketing-saas
type: Opaque
data:
  DATABASE_URL: <base64-encoded-database-url>
  REDIS_URL: <base64-encoded-redis-url>
  JWT_SECRET: <base64-encoded-jwt-secret>
  COPY_AI_API_KEY: <base64-encoded-copy-ai-api-key>
```

### **4. Deployment**
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ai-marketing-saas
  namespace: ai-marketing-saas
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ai-marketing-saas
  template:
    metadata:
      labels:
        app: ai-marketing-saas
    spec:
      containers:
      - name: ai-marketing-saas
        image: your-registry/ai-marketing-saas:latest
        ports:
        - containerPort: 3000
        envFrom:
        - configMapRef:
            name: ai-marketing-saas-config
        - secretRef:
            name: ai-marketing-saas-secret
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "1Gi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 3000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
```

### **5. Service**
```yaml
# service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ai-marketing-saas-service
  namespace: ai-marketing-saas
spec:
  selector:
    app: ai-marketing-saas
  ports:
  - port: 80
    targetPort: 3000
  type: ClusterIP
```

### **6. Ingress**
```yaml
# ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-marketing-saas-ingress
  namespace: ai-marketing-saas
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
  - hosts:
    - yourdomain.com
    - www.yourdomain.com
    secretName: ai-marketing-saas-tls
  rules:
  - host: yourdomain.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: ai-marketing-saas-service
            port:
              number: 80
```

### **7. Deploy to Kubernetes**
```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl apply -f ingress.yaml

# Check deployment status
kubectl get pods -n ai-marketing-saas
kubectl get services -n ai-marketing-saas
kubectl get ingress -n ai-marketing-saas
```

---

## 📊 Monitoring & Maintenance

### **1. Application Monitoring**
```yaml
# monitoring.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
  namespace: ai-marketing-saas
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s
    scrape_configs:
    - job_name: 'ai-marketing-saas'
      static_configs:
      - targets: ['ai-marketing-saas-service:80']
```

### **2. Log Management**
```bash
# Set up log rotation
sudo nano /etc/logrotate.d/ai-marketing-saas

# Log rotation configuration
/var/log/ai-marketing-saas/*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 644 root root
    postrotate
        pm2 reloadLogs
    endscript
}
```

### **3. Backup Strategy**
```bash
#!/bin/bash
# backup.sh

# Database backup
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql s3://your-backup-bucket/

# Cleanup old backups
find /backups -name "backup_*.sql" -mtime +7 -delete
```

### **4. Health Checks**
```bash
#!/bin/bash
# health-check.sh

# Check application health
curl -f http://localhost:3000/health || exit 1

# Check database connection
pg_isready -d $DATABASE_URL || exit 1

# Check Redis connection
redis-cli ping || exit 1

# Check disk space
df -h | awk '$5 > 80 {print $0}' | wc -l | awk '$1 > 0 {exit 1}'
```

---

## 🔧 Troubleshooting

### **Common Issues**

#### **Database Connection Issues**
```bash
# Check database status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U ai_user -d ai_marketing_saas

# Reset database
npm run db:reset
```

#### **Redis Connection Issues**
```bash
# Check Redis status
sudo systemctl status redis

# Test Redis connection
redis-cli ping

# Check Redis logs
sudo journalctl -u redis
```

#### **Application Crashes**
```bash
# Check PM2 status
pm2 status

# View logs
pm2 logs ai-marketing-saas

# Restart application
pm2 restart ai-marketing-saas

# Check system resources
htop
df -h
```

#### **Copy.ai API Issues**
```bash
# Test API connection
curl -H "Authorization: Bearer $COPY_AI_API_KEY" \
     https://api.copy.ai/v1/account

# Check API limits
curl -H "Authorization: Bearer $COPY_AI_API_KEY" \
     https://api.copy.ai/v1/usage
```

### **Performance Issues**

#### **High Memory Usage**
```bash
# Check memory usage
free -h
ps aux --sort=-%mem | head

# Restart services
pm2 restart ai-marketing-saas
sudo systemctl restart postgresql
sudo systemctl restart redis
```

#### **Slow Database Queries**
```sql
-- Check slow queries
SELECT query, mean_time, calls 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;

-- Check database size
SELECT pg_size_pretty(pg_database_size('ai_marketing_saas'));
```

#### **High CPU Usage**
```bash
# Check CPU usage
top
htop

# Check for stuck processes
ps aux | grep node
kill -9 <pid>
```

---

## 📞 Support

### **Deployment Support**
- **Email**: deploy@ai-marketing-saas.com
- **Documentation**: [Deployment Docs](https://docs.ai-marketing-saas.com/deployment)
- **GitHub Issues**: [Deployment Issues](https://github.com/your-username/ai-marketing-course-saas/issues)

### **Emergency Contacts**
- **On-call Engineer**: +1 (555) 123-4567
- **Escalation**: +1 (555) 123-4568
- **Status Page**: [System Status](https://status.ai-marketing-saas.com)

---

*This deployment guide is regularly updated. Last updated: December 2024*

