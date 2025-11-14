---
title: "Deployment"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Other/deployment.md"
---

# 🚀 Guía de Deployment - ClickUp Brain

## Visión General

Esta guía proporciona instrucciones detalladas para desplegar ClickUp Brain en diferentes entornos, desde desarrollo local hasta producción a escala empresarial.

## 🏗️ Arquitectura de Deployment

### Topología de Deployment

```
┌─────────────────────────────────────────────────────────────┐
│                    Production Environment                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Load Balancer │  │   CDN           │  │   WAF        │ │
│  │   (AWS ALB)     │  │   (CloudFlare)  │  │   (AWS WAF)  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Application Tier (ECS/K8s)                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   API       │  │   AI        │  │   Web       │    │ │
│  │  │   Gateway   │  │   Services  │  │   Frontend  │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
│                                                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │                Data Tier                                │ │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │ │
│  │  │   RDS       │  │   Redis     │  │   S3        │    │ │
│  │  │   (Postgres)│  │   (Cache)   │  │   (Storage) │    │ │
│  │  └─────────────┘  └─────────────┘  └─────────────┘    │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## 🐳 Deployment con Docker

### Dockerfile para Backend

```dockerfile
# Backend Dockerfile
FROM python:3.11-slim

# Establecer variables de entorno
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Crear usuario no-root
RUN groupadd -r clickupbrain && useradd -r -g clickupbrain clickupbrain

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Cambiar ownership al usuario no-root
RUN chown -R clickupbrain:clickupbrain /app
USER clickupbrain

# Exponer puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "app.main:app"]
```

### Dockerfile para Frontend

```dockerfile
# Frontend Dockerfile
FROM node:18-alpine AS builder

# Establecer directorio de trabajo
WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Build de la aplicación
RUN npm run build

# Stage de producción
FROM nginx:alpine

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Copiar archivos build
COPY --from=builder /app/dist /usr/share/nginx/html

# Exponer puerto
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Comando de inicio
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose para Desarrollo

```yaml
# docker-compose.yml
version: '3.8'

services:
  # Base de datos PostgreSQL
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: clickup_brain
      POSTGRES_USER: clickupbrain
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init-db.sql
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U clickupbrain -d clickup_brain"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis para cache
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://clickupbrain:${POSTGRES_PASSWORD}@postgres:5432/clickup_brain
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./backend:/app
      - /app/venv
    command: ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:8000

  # AI Services
  ai-services:
    build:
      context: ./ai-services
      dockerfile: Dockerfile
    environment:
      - MODEL_PATH=/models
      - GPU_ENABLED=false
    ports:
      - "8001:8001"
    volumes:
      - ./models:/models
    depends_on:
      - backend

  # Monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  postgres_data:
  redis_data:
  prometheus_data:
  grafana_data:
```

## ☸️ Deployment con Kubernetes

### Namespace y ConfigMap

```yaml
# k8s/namespace.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: clickup-brain
  labels:
    name: clickup-brain
    environment: production
---
# k8s/configmap.yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: clickup-brain-config
  namespace: clickup-brain
data:
  DATABASE_URL: "postgresql://clickupbrain:${POSTGRES_PASSWORD}@postgres-service:5432/clickup_brain"
  REDIS_URL: "redis://redis-service:6379"
  ENVIRONMENT: "production"
  LOG_LEVEL: "INFO"
  API_VERSION: "v1"
```

### Secrets

```yaml
# k8s/secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: clickup-brain-secrets
  namespace: clickup-brain
type: Opaque
data:
  POSTGRES_PASSWORD: <base64-encoded-password>
  JWT_SECRET: <base64-encoded-jwt-secret>
  ENCRYPTION_KEY: <base64-encoded-encryption-key>
  API_KEYS: <base64-encoded-api-keys>
```

### Deployment para Backend

```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: clickup-brain-backend
  namespace: clickup-brain
  labels:
    app: clickup-brain-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: clickup-brain-backend
  template:
    metadata:
      labels:
        app: clickup-brain-backend
    spec:
      containers:
      - name: backend
        image: clickup-brain/backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            configMapKeyRef:
              name: clickup-brain-config
              key: DATABASE_URL
        - name: JWT_SECRET
          valueFrom:
            secretKeyRef:
              name: clickup-brain-secrets
              key: JWT_SECRET
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
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        volumeMounts:
        - name: logs
          mountPath: /app/logs
      volumes:
      - name: logs
        emptyDir: {}
      imagePullSecrets:
      - name: registry-secret
```

### Service para Backend

```yaml
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: clickup-brain-backend-service
  namespace: clickup-brain
  labels:
    app: clickup-brain-backend
spec:
  selector:
    app: clickup-brain-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: ClusterIP
```

### Ingress

```yaml
# k8s/ingress.yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: clickup-brain-ingress
  namespace: clickup-brain
  annotations:
    kubernetes.io/ingress.class: nginx
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
    nginx.ingress.kubernetes.io/force-ssl-redirect: "true"
    nginx.ingress.kubernetes.io/proxy-body-size: "10m"
spec:
  tls:
  - hosts:
    - api.clickupbrain.ai
    secretName: clickup-brain-tls
  rules:
  - host: api.clickupbrain.ai
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: clickup-brain-backend-service
            port:
              number: 80
```

### Horizontal Pod Autoscaler

```yaml
# k8s/hpa.yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: clickup-brain-backend-hpa
  namespace: clickup-brain
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: clickup-brain-backend
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

## ☁️ Deployment en AWS

### Terraform Configuration

```hcl
# terraform/main.tf
terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket = "clickup-brain-terraform-state"
    key    = "production/terraform.tfstate"
    region = "us-west-2"
  }
}

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = "ClickUp Brain"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# VPC
module "vpc" {
  source = "terraform-aws-modules/vpc/aws"
  
  name = "clickup-brain-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["${var.aws_region}a", "${var.aws_region}b", "${var.aws_region}c"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24", "10.0.103.0/24"]
  
  enable_nat_gateway = true
  enable_vpn_gateway = true
  
  tags = {
    Name = "clickup-brain-vpc"
  }
}

# EKS Cluster
module "eks" {
  source = "terraform-aws-modules/eks/aws"
  
  cluster_name    = "clickup-brain-cluster"
  cluster_version = "1.28"
  
  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true
  
  # EKS Managed Node Groups
  eks_managed_node_groups = {
    general = {
      name = "general"
      
      instance_types = ["t3.medium"]
      
      min_size     = 1
      max_size     = 10
      desired_size = 3
      
      vpc_security_group_ids = [aws_security_group.node_group_one.id]
    }
    
    ai_workloads = {
      name = "ai-workloads"
      
      instance_types = ["g4dn.xlarge"]
      
      min_size     = 0
      max_size     = 5
      desired_size = 1
      
      vpc_security_group_ids = [aws_security_group.node_group_one.id]
      
      labels = {
        workload-type = "ai"
      }
    }
  }
  
  tags = {
    Environment = var.environment
  }
}

# RDS PostgreSQL
module "rds" {
  source = "terraform-aws-modules/rds/aws"
  
  identifier = "clickup-brain-db"
  
  engine            = "postgres"
  engine_version    = "15.4"
  instance_class    = "db.t3.medium"
  allocated_storage = 100
  
  db_name  = "clickupbrain"
  username = "clickupbrain"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  subnet_ids             = module.vpc.private_subnets
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "Sun:04:00-Sun:05:00"
  
  deletion_protection = true
  
  tags = {
    Name = "clickup-brain-db"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "redis" {
  name       = "clickup-brain-redis-subnet"
  subnet_ids = module.vpc.private_subnets
}

resource "aws_elasticache_replication_group" "redis" {
  replication_group_id       = "clickup-brain-redis"
  description                = "Redis cluster for ClickUp Brain"
  
  node_type                  = "cache.t3.micro"
  port                       = 6379
  parameter_group_name       = "default.redis7"
  
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  multi_az_enabled          = true
  
  subnet_group_name = aws_elasticache_subnet_group.redis.name
  security_group_ids = [aws_security_group.redis.id]
  
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  
  tags = {
    Name = "clickup-brain-redis"
  }
}

# S3 Bucket para almacenamiento
resource "aws_s3_bucket" "clickup_brain_storage" {
  bucket = "clickup-brain-storage-${random_string.bucket_suffix.result}"
  
  tags = {
    Name = "clickup-brain-storage"
  }
}

resource "aws_s3_bucket_versioning" "clickup_brain_storage" {
  bucket = aws_s3_bucket.clickup_brain_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_encryption" "clickup_brain_storage" {
  bucket = aws_s3_bucket.clickup_brain_storage.id
  
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}

# Application Load Balancer
resource "aws_lb" "clickup_brain_alb" {
  name               = "clickup-brain-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.alb.id]
  subnets            = module.vpc.public_subnets
  
  enable_deletion_protection = true
  
  tags = {
    Name = "clickup-brain-alb"
  }
}

resource "aws_lb_target_group" "clickup_brain_tg" {
  name     = "clickup-brain-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = module.vpc.vpc_id
  
  health_check {
    enabled             = true
    healthy_threshold   = 2
    unhealthy_threshold = 2
    timeout             = 5
    interval            = 30
    path                = "/health"
    matcher             = "200"
    port                = "traffic-port"
    protocol            = "HTTP"
  }
  
  tags = {
    Name = "clickup-brain-tg"
  }
}

resource "aws_lb_listener" "clickup_brain_listener" {
  load_balancer_arn = aws_lb.clickup_brain_alb.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS-1-2-2017-01"
  certificate_arn   = aws_acm_certificate.clickup_brain_cert.arn
  
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.clickup_brain_tg.arn
  }
}

# Security Groups
resource "aws_security_group" "alb" {
  name_prefix = "clickup-brain-alb-"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "clickup-brain-alb-sg"
  }
}

resource "aws_security_group" "rds" {
  name_prefix = "clickup-brain-rds-"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.eks_cluster.id]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "clickup-brain-rds-sg"
  }
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "production"
}

variable "db_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# Outputs
output "cluster_endpoint" {
  description = "Endpoint for EKS control plane"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ids attached to the cluster control plane"
  value       = module.eks.cluster_security_group_id
}

output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = module.rds.db_instance_endpoint
}

output "alb_dns_name" {
  description = "The DNS name of the load balancer"
  value       = aws_lb.clickup_brain_alb.dns_name
}
```

## 🔄 CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy ClickUp Brain

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-west-2
  EKS_CLUSTER_NAME: clickup-brain-cluster
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-west-2.amazonaws.com
  IMAGE_TAG: ${{ github.sha }}

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: clickup_brain_test
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
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'
        cache: 'npm'
        cache-dependency-path: frontend/package-lock.json
    
    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r backend/requirements.txt
        pip install -r backend/requirements-dev.txt
    
    - name: Install Node.js dependencies
      run: |
        cd frontend
        npm ci
    
    - name: Run Python tests
      run: |
        cd backend
        pytest --cov=app --cov-report=xml
    
    - name: Run Node.js tests
      run: |
        cd frontend
        npm test -- --coverage --watchAll=false
    
    - name: Run security scan
      run: |
        cd backend
        bandit -r app/
        safety check
    
    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        files: ./backend/coverage.xml,./frontend/coverage/lcov.info

  build-and-push:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v2
    
    - name: Build and push backend image
      run: |
        docker build -t $ECR_REGISTRY/clickup-brain-backend:$IMAGE_TAG ./backend
        docker build -t $ECR_REGISTRY/clickup-brain-backend:latest ./backend
        docker push $ECR_REGISTRY/clickup-brain-backend:$IMAGE_TAG
        docker push $ECR_REGISTRY/clickup-brain-backend:latest
    
    - name: Build and push frontend image
      run: |
        docker build -t $ECR_REGISTRY/clickup-brain-frontend:$IMAGE_TAG ./frontend
        docker build -t $ECR_REGISTRY/clickup-brain-frontend:latest ./frontend
        docker push $ECR_REGISTRY/clickup-brain-frontend:$IMAGE_TAG
        docker push $ECR_REGISTRY/clickup-brain-frontend:latest
    
    - name: Build and push AI services image
      run: |
        docker build -t $ECR_REGISTRY/clickup-brain-ai:$IMAGE_TAG ./ai-services
        docker build -t $ECR_REGISTRY/clickup-brain-ai:latest ./ai-services
        docker push $ECR_REGISTRY/clickup-brain-ai:$IMAGE_TAG
        docker push $ECR_REGISTRY/clickup-brain-ai:latest

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region $AWS_REGION --name $EKS_CLUSTER_NAME
    
    - name: Deploy to Kubernetes
      run: |
        # Update image tags in deployment files
        sed -i "s|image: clickup-brain/backend:latest|image: $ECR_REGISTRY/clickup-brain-backend:$IMAGE_TAG|g" k8s/backend-deployment.yaml
        sed -i "s|image: clickup-brain/frontend:latest|image: $ECR_REGISTRY/clickup-brain-frontend:$IMAGE_TAG|g" k8s/frontend-deployment.yaml
        sed -i "s|image: clickup-brain/ai:latest|image: $ECR_REGISTRY/clickup-brain-ai:$IMAGE_TAG|g" k8s/ai-deployment.yaml
        
        # Apply Kubernetes manifests
        kubectl apply -f k8s/namespace.yaml
        kubectl apply -f k8s/configmap.yaml
        kubectl apply -f k8s/secrets.yaml
        kubectl apply -f k8s/backend-deployment.yaml
        kubectl apply -f k8s/frontend-deployment.yaml
        kubectl apply -f k8s/ai-deployment.yaml
        kubectl apply -f k8s/backend-service.yaml
        kubectl apply -f k8s/frontend-service.yaml
        kubectl apply -f k8s/ai-service.yaml
        kubectl apply -f k8s/ingress.yaml
        kubectl apply -f k8s/hpa.yaml
    
    - name: Wait for deployment
      run: |
        kubectl rollout status deployment/clickup-brain-backend -n clickup-brain --timeout=300s
        kubectl rollout status deployment/clickup-brain-frontend -n clickup-brain --timeout=300s
        kubectl rollout status deployment/clickup-brain-ai -n clickup-brain --timeout=300s
    
    - name: Run smoke tests
      run: |
        # Wait for services to be ready
        kubectl wait --for=condition=ready pod -l app=clickup-brain-backend -n clickup-brain --timeout=300s
        
        # Get service URL
        SERVICE_URL=$(kubectl get ingress clickup-brain-ingress -n clickup-brain -o jsonpath='{.status.loadBalancer.ingress[0].hostname}')
        
        # Run smoke tests
        curl -f https://$SERVICE_URL/health || exit 1
        curl -f https://$SERVICE_URL/api/v1/health || exit 1

  rollback:
    runs-on: ubuntu-latest
    if: failure() && github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v4
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Update kubeconfig
      run: |
        aws eks update-kubeconfig --region $AWS_REGION --name $EKS_CLUSTER_NAME
    
    - name: Rollback deployment
      run: |
        kubectl rollout undo deployment/clickup-brain-backend -n clickup-brain
        kubectl rollout undo deployment/clickup-brain-frontend -n clickup-brain
        kubectl rollout undo deployment/clickup-brain-ai -n clickup-brain
    
    - name: Notify team
      uses: 8398a7/action-slack@v3
      with:
        status: failure
        text: "Deployment failed and rolled back. Please check the logs."
      env:
        SLACK_WEBHOOK_URL: ${{ secrets.SLACK_WEBHOOK_URL }}
```

## 📊 Monitoreo y Observabilidad

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

  - job_name: 'clickup-brain-backend'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - clickup-brain
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: clickup-brain-backend-service
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: keep
        regex: http

  - job_name: 'clickup-brain-ai'
    kubernetes_sd_configs:
      - role: endpoints
        namespaces:
          names:
            - clickup-brain
    relabel_configs:
      - source_labels: [__meta_kubernetes_service_name]
        action: keep
        regex: clickup-brain-ai-service
      - source_labels: [__meta_kubernetes_endpoint_port_name]
        action: keep
        regex: http

  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        action: keep
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        action: replace
        target_label: __metrics_path__
        regex: (.+)
```

### Grafana Dashboard

```json
{
  "dashboard": {
    "id": null,
    "title": "ClickUp Brain - System Overview",
    "tags": ["clickup-brain"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total[5m])",
            "legendFormat": "{{method}} {{endpoint}}"
          }
        ],
        "yAxes": [
          {
            "label": "requests/sec"
          }
        ]
      },
      {
        "id": 2,
        "title": "Response Time",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "95th percentile"
          },
          {
            "expr": "histogram_quantile(0.50, rate(http_request_duration_seconds_bucket[5m]))",
            "legendFormat": "50th percentile"
          }
        ],
        "yAxes": [
          {
            "label": "seconds"
          }
        ]
      },
      {
        "id": 3,
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(http_requests_total{status=~\"5..\"}[5m])",
            "legendFormat": "5xx errors"
          },
          {
            "expr": "rate(http_requests_total{status=~\"4..\"}[5m])",
            "legendFormat": "4xx errors"
          }
        ],
        "yAxes": [
          {
            "label": "errors/sec"
          }
        ]
      },
      {
        "id": 4,
        "title": "CPU Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total[5m]) * 100",
            "legendFormat": "{{pod}}"
          }
        ],
        "yAxes": [
          {
            "label": "percent"
          }
        ]
      },
      {
        "id": 5,
        "title": "Memory Usage",
        "type": "graph",
        "targets": [
          {
            "expr": "container_memory_usage_bytes / container_spec_memory_limit_bytes * 100",
            "legendFormat": "{{pod}}"
          }
        ],
        "yAxes": [
          {
            "label": "percent"
          }
        ]
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## 🔧 Scripts de Deployment

### Deployment Script

```bash
#!/bin/bash
# scripts/deploy.sh

set -e

# Configuration
ENVIRONMENT=${1:-staging}
NAMESPACE="clickup-brain-${ENVIRONMENT}"
IMAGE_TAG=${2:-latest}

echo "🚀 Deploying ClickUp Brain to ${ENVIRONMENT} environment"
echo "📦 Using image tag: ${IMAGE_TAG}"

# Check if kubectl is configured
if ! kubectl cluster-info &> /dev/null; then
    echo "❌ kubectl is not configured or cluster is not accessible"
    exit 1
fi

# Create namespace if it doesn't exist
kubectl create namespace ${NAMESPACE} --dry-run=client -o yaml | kubectl apply -f -

# Apply secrets
echo "🔐 Applying secrets..."
kubectl apply -f k8s/secrets.yaml -n ${NAMESPACE}

# Apply configmaps
echo "⚙️ Applying configmaps..."
envsubst < k8s/configmap.yaml | kubectl apply -f - -n ${NAMESPACE}

# Apply deployments
echo "📦 Applying deployments..."
sed "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/backend-deployment.yaml | kubectl apply -f - -n ${NAMESPACE}
sed "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/frontend-deployment.yaml | kubectl apply -f - -n ${NAMESPACE}
sed "s|IMAGE_TAG|${IMAGE_TAG}|g" k8s/ai-deployment.yaml | kubectl apply -f - -n ${NAMESPACE}

# Apply services
echo "🌐 Applying services..."
kubectl apply -f k8s/backend-service.yaml -n ${NAMESPACE}
kubectl apply -f k8s/frontend-service.yaml -n ${NAMESPACE}
kubectl apply -f k8s/ai-service.yaml -n ${NAMESPACE}

# Apply ingress
echo "🔗 Applying ingress..."
kubectl apply -f k8s/ingress.yaml -n ${NAMESPACE}

# Apply HPA
echo "📈 Applying HPA..."
kubectl apply -f k8s/hpa.yaml -n ${NAMESPACE}

# Wait for deployments
echo "⏳ Waiting for deployments to be ready..."
kubectl rollout status deployment/clickup-brain-backend -n ${NAMESPACE} --timeout=300s
kubectl rollout status deployment/clickup-brain-frontend -n ${NAMESPACE} --timeout=300s
kubectl rollout status deployment/clickup-brain-ai -n ${NAMESPACE} --timeout=300s

# Run health checks
echo "🏥 Running health checks..."
kubectl wait --for=condition=ready pod -l app=clickup-brain-backend -n ${NAMESPACE} --timeout=300s

# Get service URL
SERVICE_URL=$(kubectl get ingress clickup-brain-ingress -n ${NAMESPACE} -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || echo "localhost")

echo "✅ Deployment completed successfully!"
echo "🌐 Service URL: https://${SERVICE_URL}"
echo "📊 Monitor deployment: kubectl get pods -n ${NAMESPACE}"
```

### Rollback Script

```bash
#!/bin/bash
# scripts/rollback.sh

set -e

ENVIRONMENT=${1:-staging}
NAMESPACE="clickup-brain-${ENVIRONMENT}"

echo "🔄 Rolling back ClickUp Brain in ${ENVIRONMENT} environment"

# Rollback deployments
echo "📦 Rolling back deployments..."
kubectl rollout undo deployment/clickup-brain-backend -n ${NAMESPACE}
kubectl rollout undo deployment/clickup-brain-frontend -n ${NAMESPACE}
kubectl rollout undo deployment/clickup-brain-ai -n ${NAMESPACE}

# Wait for rollback
echo "⏳ Waiting for rollback to complete..."
kubectl rollout status deployment/clickup-brain-backend -n ${NAMESPACE} --timeout=300s
kubectl rollout status deployment/clickup-brain-frontend -n ${NAMESPACE} --timeout=300s
kubectl rollout status deployment/clickup-brain-ai -n ${NAMESPACE} --timeout=300s

echo "✅ Rollback completed successfully!"
echo "📊 Check status: kubectl get pods -n ${NAMESPACE}"
```

---

Esta guía de deployment proporciona un framework completo para desplegar ClickUp Brain en diferentes entornos, desde desarrollo local hasta producción a escala empresarial, con automatización completa y monitoreo integrado.



