# Deployment and DevOps Guide

## Table of Contents
1. [Infrastructure Overview](#infrastructure-overview)
2. [Containerization with Docker](#containerization-with-docker)
3. [Kubernetes Orchestration](#kubernetes-orchestration)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Monitoring and Logging](#monitoring-and-logging)
6. [Security and Compliance](#security-and-compliance)
7. [Scaling and Performance](#scaling-and-performance)
8. [Disaster Recovery](#disaster-recovery)

## Infrastructure Overview

### Architecture Diagram
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Load Balancer │    │   API Gateway   │    │   CDN           │
│   (NGINX)       │    │   (Kong)        │    │   (CloudFlare)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Servers   │    │   API Servers   │    │   Static Assets │
│   (React)       │    │   (Django)      │    │   (S3/CloudFront)│
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Services   │    │   Database      │    │   Cache Layer   │
│   (ML Models)   │    │   (PostgreSQL)  │    │   (Redis)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Message Queue │    │   File Storage  │    │   Monitoring    │
│   (RabbitMQ)    │    │   (S3/MinIO)    │    │   (Prometheus)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Technology Stack
- **Frontend**: React, TypeScript, Material-UI
- **Backend**: Django, FastAPI, Python
- **Database**: PostgreSQL, Redis
- **Message Queue**: RabbitMQ, Apache Kafka
- **AI/ML**: TensorFlow, PyTorch, OpenAI API
- **Infrastructure**: Docker, Kubernetes, AWS/GCP/Azure
- **Monitoring**: Prometheus, Grafana, ELK Stack
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins

## Containerization with Docker

### Dockerfile for Backend
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create non-root user
RUN adduser --disabled-password --gecos '' appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120", "config.wsgi:application"]
```

### Dockerfile for Frontend
```dockerfile
# Frontend Dockerfile
FROM node:18-alpine as build

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose for Development
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_marketing_platform
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Backend
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DEBUG=1
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_marketing_platform
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health/"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend

  # Celery Worker
  celery:
    build: ./backend
    command: celery -A config worker -l info
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_marketing_platform
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Celery Beat
  celery-beat:
    build: ./backend
    command: celery -A config beat -l info
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@postgres:5432/ai_marketing_platform
      - REDIS_URL=redis://redis:6379/0
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

volumes:
  postgres_data:
  redis_data:
```

## Kubernetes Orchestration

### Namespace Configuration
```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: ai-marketing-platform
  labels:
    name: ai-marketing-platform
```

### ConfigMap for Environment Variables
```yaml
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: ai-marketing-platform-config
  namespace: ai-marketing-platform
data:
  DEBUG: "0"
  ALLOWED_HOSTS: "localhost,127.0.0.1"
  CORS_ALLOWED_ORIGINS: "http://localhost:3000"
  REDIS_URL: "redis://redis-service:6379/0"
  DATABASE_URL: "postgresql://postgres:postgres@postgres-service:5432/ai_marketing_platform"
```

### Secret for Sensitive Data
```yaml
# k8s/secret.yaml
apiVersion: v1
kind: Secret
metadata:
  name: ai-marketing-platform-secrets
  namespace: ai-marketing-platform
type: Opaque
data:
  SECRET_KEY: <base64-encoded-secret-key>
  OPENAI_API_KEY: <base64-encoded-openai-key>
  DATABASE_PASSWORD: <base64-encoded-db-password>
```

### PostgreSQL Deployment
```yaml
# k8s/postgres.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: postgres
  namespace: ai-marketing-platform
spec:
  replicas: 1
  selector:
    matchLabels:
      app: postgres
  template:
    metadata:
      labels:
        app: postgres
    spec:
      containers:
      - name: postgres
        image: postgres:15
        ports:
        - containerPort: 5432
        env:
        - name: POSTGRES_DB
          value: ai_marketing_platform
        - name: POSTGRES_USER
          value: postgres
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: ai-marketing-platform-secrets
              key: DATABASE_PASSWORD
        volumeMounts:
        - name: postgres-storage
          mountPath: /var/lib/postgresql/data
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
      volumes:
      - name: postgres-storage
        persistentVolumeClaim:
          claimName: postgres-pvc
---
apiVersion: v1
kind: Service
metadata:
  name: postgres-service
  namespace: ai-marketing-platform
spec:
  selector:
    app: postgres
  ports:
  - port: 5432
    targetPort: 5432
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: postgres-pvc
  namespace: ai-marketing-platform
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### Backend Deployment
```yaml
# k8s/backend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
  namespace: ai-marketing-platform
spec:
  replicas: 3
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: ai-marketing-platform/backend:latest
        ports:
        - containerPort: 8000
        envFrom:
        - configMapRef:
            name: ai-marketing-platform-config
        - secretRef:
            name: ai-marketing-platform-secrets
        resources:
          requests:
            memory: "512Mi"
            cpu: "500m"
          limits:
            memory: "1Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health/
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: ai-marketing-platform
spec:
  selector:
    app: backend
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Frontend Deployment
```yaml
# k8s/frontend.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  namespace: ai-marketing-platform
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: ai-marketing-platform/frontend:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: frontend-service
  namespace: ai-marketing-platform
spec:
  selector:
    app: frontend
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
```

### Ingress Configuration
```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ai-marketing-platform-ingress
  namespace: ai-marketing-platform
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
spec:
  tls:
  - hosts:
    - api.ai-marketing-platform.com
    - app.ai-marketing-platform.com
    secretName: ai-marketing-platform-tls
  rules:
  - host: api.ai-marketing-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: backend-service
            port:
              number: 8000
  - host: app.ai-marketing-platform.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 80
```

## CI/CD Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/ci-cd.yml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432
      
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 6379:6379

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        cd backend
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run linting
      run: |
        cd backend
        flake8 .
        black --check .
        isort --check-only .
    
    - name: Run tests
      run: |
        cd backend
        python manage.py test
      env:
        DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test_db
        REDIS_URL: redis://localhost:6379/0
    
    - name: Run security scan
      run: |
        cd backend
        bandit -r . -f json -o bandit-report.json
        safety check
    
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install frontend dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run frontend tests
      run: |
        cd frontend
        npm run test:coverage
    
    - name: Build frontend
      run: |
        cd frontend
        npm run build

  build:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Log in to Container Registry
      uses: docker/login-action@v2
      with:
        registry: ${{ env.REGISTRY }}
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    - name: Extract metadata
      id: meta
      uses: docker/metadata-action@v4
      with:
        images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
        tags: |
          type=ref,event=branch
          type=ref,event=pr
          type=sha,prefix={{branch}}-
          type=raw,value=latest,enable={{is_default_branch}}
    
    - name: Build and push backend image
      uses: docker/build-push-action@v4
      with:
        context: ./backend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
    
    - name: Build and push frontend image
      uses: docker/build-push-action@v4
      with:
        context: ./frontend
        push: true
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure kubectl
      uses: azure/k8s-set-context@v3
      with:
        method: kubeconfig
        kubeconfig: ${{ secrets.KUBE_CONFIG }}
    
    - name: Deploy to Kubernetes
      run: |
        # Update image tags in deployment files
        sed -i "s|image: .*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/backend:latest|g" k8s/backend.yaml
        sed -i "s|image: .*|image: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}/frontend:latest|g" k8s/frontend.yaml
        
        # Apply Kubernetes manifests
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secret.yaml
        kubectl apply -f k8s/postgres.yaml
        kubectl apply -f k8s/backend.yaml
        kubectl apply -f k8s/frontend.yaml
        kubectl apply -f k8s/ingress.yaml
        
        # Wait for deployment to complete
        kubectl rollout status deployment/backend -n ai-marketing-platform
        kubectl rollout status deployment/frontend -n ai-marketing-platform
    
    - name: Run database migrations
      run: |
        kubectl exec -n ai-marketing-platform deployment/backend -- python manage.py migrate
    
    - name: Collect static files
      run: |
        kubectl exec -n ai-marketing-platform deployment/backend -- python manage.py collectstatic --noinput
```

## Monitoring and Logging

### Prometheus Configuration
```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'backend'
    static_configs:
      - targets: ['backend-service:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres-exporter:9187']

  - job_name: 'redis'
    static_configs:
      - targets: ['redis-exporter:9121']

  - job_name: 'kubernetes'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_annotation_prometheus_io_scrape]
        action: keep
        regex: true
```

### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "AI Marketing Platform Dashboard",
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
      },
      {
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          }
        ]
      },
      {
        "title": "Database Connections",
        "type": "graph",
        "targets": [
          {
            "expr": "pg_stat_database_numbackends",
            "legendFormat": "Active connections"
          }
        ]
      }
    ]
  }
}
```

### ELK Stack Configuration
```yaml
# logging/elasticsearch.yml
cluster.name: ai-marketing-platform
node.name: node-1
network.host: 0.0.0.0
discovery.type: single-node
xpack.security.enabled: false
```

```yaml
# logging/logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "backend" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{GREEDYDATA:message}" }
    }
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "ai-marketing-platform-%{+YYYY.MM.dd}"
  }
}
```

## Security and Compliance

### Security Scanning
```yaml
# security/trivy-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run Trivy vulnerability scanner
      uses: aquasecurity/trivy-action@master
      with:
        scan-type: 'fs'
        scan-ref: '.'
        format: 'sarif'
        output: 'trivy-results.sarif'
    
    - name: Upload Trivy scan results
      uses: github/codeql-action/upload-sarif@v2
      with:
        sarif_file: 'trivy-results.sarif'
```

### Network Policies
```yaml
# security/network-policies.yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-network-policy
  namespace: ai-marketing-platform
spec:
  podSelector:
    matchLabels:
      app: backend
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ai-marketing-platform
    - podSelector:
        matchLabels:
          app: frontend
    ports:
    - protocol: TCP
      port: 8000
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: postgres
    ports:
    - protocol: TCP
      port: 5432
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
```

## Scaling and Performance

### Horizontal Pod Autoscaler
```yaml
# scaling/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
  namespace: ai-marketing-platform
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
  behavior:
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Percent
        value: 10
        periodSeconds: 60
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Percent
        value: 50
        periodSeconds: 60
```

### Vertical Pod Autoscaler
```yaml
# scaling/vpa.yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: backend-vpa
  namespace: ai-marketing-platform
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  updatePolicy:
    updateMode: "Auto"
  resourcePolicy:
    containerPolicies:
    - containerName: backend
      minAllowed:
        cpu: 100m
        memory: 128Mi
      maxAllowed:
        cpu: 2000m
        memory: 4Gi
```

## Disaster Recovery

### Backup Strategy
```bash
#!/bin/bash
# backup/backup.sh

# Database backup
kubectl exec -n ai-marketing-platform deployment/postgres -- pg_dump -U postgres ai_marketing_platform > backup_$(date +%Y%m%d_%H%M%S).sql

# Upload to S3
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql s3://ai-marketing-platform-backups/database/

# File storage backup
kubectl exec -n ai-marketing-platform deployment/backend -- tar -czf - /app/media | aws s3 cp - s3://ai-marketing-platform-backups/media/media_$(date +%Y%m%d_%H%M%S).tar.gz

# Configuration backup
kubectl get configmap -n ai-marketing-platform -o yaml > configmap_backup_$(date +%Y%m%d_%H%M%S).yaml
kubectl get secret -n ai-marketing-platform -o yaml > secret_backup_$(date +%Y%m%d_%H%M%S).yaml

aws s3 cp configmap_backup_$(date +%Y%m%d_%H%M%S).yaml s3://ai-marketing-platform-backups/config/
aws s3 cp secret_backup_$(date +%Y%m%d_%H%M%S).yaml s3://ai-marketing-platform-backups/config/
```

### Recovery Procedures
```bash
#!/bin/bash
# recovery/restore.sh

# Restore database
aws s3 cp s3://ai-marketing-platform-backups/database/backup_20240115_120000.sql .
kubectl exec -i -n ai-marketing-platform deployment/postgres -- psql -U postgres ai_marketing_platform < backup_20240115_120000.sql

# Restore file storage
aws s3 cp s3://ai-marketing-platform-backups/media/media_20240115_120000.tar.gz .
kubectl exec -i -n ai-marketing-platform deployment/backend -- tar -xzf - < media_20240115_120000.tar.gz

# Restore configuration
aws s3 cp s3://ai-marketing-platform-backups/config/configmap_backup_20240115_120000.yaml .
aws s3 cp s3://ai-marketing-platform-backups/config/secret_backup_20240115_120000.yaml .

kubectl apply -f configmap_backup_20240115_120000.yaml
kubectl apply -f secret_backup_20240115_120000.yaml
```

---

## Key Takeaways

### Deployment Best Practices
1. **Containerization**: Use Docker for consistent deployments across environments
2. **Orchestration**: Leverage Kubernetes for scalable and resilient deployments
3. **CI/CD**: Implement automated testing, building, and deployment pipelines
4. **Monitoring**: Set up comprehensive monitoring and logging systems
5. **Security**: Implement security scanning and network policies
6. **Scaling**: Use HPA and VPA for automatic scaling based on demand
7. **Backup**: Implement regular backups and disaster recovery procedures

### Performance Optimization
1. **Resource Management**: Set appropriate resource requests and limits
2. **Caching**: Implement Redis for application-level caching
3. **CDN**: Use CDN for static asset delivery
4. **Database Optimization**: Implement connection pooling and query optimization
5. **Load Balancing**: Use load balancers for traffic distribution

### Security Considerations
1. **Network Security**: Implement network policies and ingress controls
2. **Secret Management**: Use Kubernetes secrets for sensitive data
3. **Image Security**: Scan container images for vulnerabilities
4. **Access Control**: Implement RBAC for Kubernetes resources
5. **Compliance**: Ensure compliance with security standards and regulations

---

*This deployment and DevOps guide provides comprehensive coverage of infrastructure setup, containerization, orchestration, CI/CD pipelines, monitoring, security, and disaster recovery for the AI Course and SaaS Marketing Platform. Following these practices ensures scalable, secure, and maintainable deployments.*









