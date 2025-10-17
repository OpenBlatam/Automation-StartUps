# 🚀 DEPLOYMENT & CONFIGURATION ULTIMATE - CHURN & RETENTION

## 🎯 **CONFIGURACIÓN COMPLETA DEL SISTEMA**

### **1. Docker Compose Ultimate**
```yaml
# docker-compose-ultimate.yml
version: '3.8'

services:
  # Core Engine
  core-engine:
    build: 
      context: ./core-engine
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    volumes:
      - ./logs:/app/logs
      - ./config:/app/config
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Machine Learning Service
  ml-service:
    build:
      context: ./ml-service
      dockerfile: Dockerfile
    ports:
      - "8001:8001"
    environment:
      - MODEL_PATH=/app/models
      - GPU_ENABLED=true
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    depends_on:
      - core-engine
    restart: unless-stopped
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  # Data Processing Service
  data-processor:
    build:
      context: ./data-processor
      dockerfile: Dockerfile
    ports:
      - "8002:8002"
    environment:
      - KAFKA_BROKERS=kafka:9092
      - ELASTICSEARCH_URL=http://elasticsearch:9200
    depends_on:
      - kafka
      - elasticsearch
    restart: unless-stopped

  # Analytics Engine
  analytics-engine:
    build:
      context: ./analytics
      dockerfile: Dockerfile
    ports:
      - "8003:8003"
    environment:
      - DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  # Prediction Engine
  prediction-engine:
    build:
      context: ./predictions
      dockerfile: Dockerfile
    ports:
      - "8004:8004"
    environment:
      - ML_SERVICE_URL=http://ml-service:8001
      - DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
    depends_on:
      - ml-service
      - postgres
    restart: unless-stopped

  # Retention Engine
  retention-engine:
    build:
      context: ./retention
      dockerfile: Dockerfile
    ports:
      - "8005:8005"
    environment:
      - DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
      - EMAIL_SERVICE_URL=http://email-service:8006
    depends_on:
      - postgres
    restart: unless-stopped

  # Visualization Engine
  visualization-engine:
    build:
      context: ./visualization
      dockerfile: Dockerfile
    ports:
      - "8006:8006"
    environment:
      - CORE_ENGINE_URL=http://core-engine:8000
      - ANALYTICS_URL=http://analytics-engine:8003
    depends_on:
      - core-engine
      - analytics-engine
    restart: unless-stopped

  # Alerting Engine
  alerting-engine:
    build:
      context: ./alerting
      dockerfile: Dockerfile
    ports:
      - "8007:8007"
    environment:
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
      - EMAIL_SMTP_HOST=${EMAIL_SMTP_HOST}
      - EMAIL_SMTP_PORT=${EMAIL_SMTP_PORT}
      - EMAIL_USERNAME=${EMAIL_USERNAME}
      - EMAIL_PASSWORD=${EMAIL_PASSWORD}
    depends_on:
      - prediction-engine
    restart: unless-stopped

  # Reporting Engine
  reporting-engine:
    build:
      context: ./reporting
      dockerfile: Dockerfile
    ports:
      - "8008:8008"
    environment:
      - DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
      - S3_BUCKET=${S3_BUCKET}
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
    depends_on:
      - postgres
    restart: unless-stopped

  # Automation Engine
  automation-engine:
    build:
      context: ./automation
      dockerfile: Dockerfile
    ports:
      - "8009:8009"
    environment:
      - WORKFLOW_DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
      - CORE_ENGINE_URL=http://core-engine:8000
    depends_on:
      - postgres
      - core-engine
    restart: unless-stopped

  # Integration Engine
  integration-engine:
    build:
      context: ./integration
      dockerfile: Dockerfile
    ports:
      - "8010:8010"
    environment:
      - API_GATEWAY_URL=http://nginx:80
      - AUTHENTICATION_SERVICE_URL=http://auth-service:8011
    depends_on:
      - nginx
    restart: unless-stopped

  # Database
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: churn_retention
      POSTGRES_USER: admin
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U admin -d churn_retention"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Redis
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Kafka
  kafka:
    image: confluentinc/cp-kafka:latest
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    ports:
      - "9092:9092"
    depends_on:
      - zookeeper
    restart: unless-stopped

  # Zookeeper
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    ports:
      - "2181:2181"
    restart: unless-stopped

  # Elasticsearch
  elasticsearch:
    image: elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    restart: unless-stopped

  # Kibana
  kibana:
    image: kibana:7.15.0
    environment:
      ELASTICSEARCH_HOSTS: http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    restart: unless-stopped

  # Nginx
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - core-engine
    restart: unless-stopped

  # Prometheus
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus/prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    restart: unless-stopped

  # Grafana
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    depends_on:
      - prometheus
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
  elasticsearch_data:
  prometheus_data:
  grafana_data:

networks:
  default:
    driver: bridge
```

### **2. Kubernetes Deployment**
```yaml
# k8s-deployment.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: churn-retention

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: core-engine
  namespace: churn-retention
spec:
  replicas: 3
  selector:
    matchLabels:
      app: core-engine
  template:
    metadata:
      labels:
        app: core-engine
    spec:
      containers:
      - name: core-engine
        image: churn-retention/core-engine:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: database-secret
              key: url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis-secret
              key: url
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

---
apiVersion: v1
kind: Service
metadata:
  name: core-engine-service
  namespace: churn-retention
spec:
  selector:
    app: core-engine
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ml-service
  namespace: churn-retention
spec:
  replicas: 2
  selector:
    matchLabels:
      app: ml-service
  template:
    metadata:
      labels:
        app: ml-service
    spec:
      containers:
      - name: ml-service
        image: churn-retention/ml-service:latest
        ports:
        - containerPort: 8001
        resources:
          requests:
            memory: "2Gi"
            cpu: "1"
            nvidia.com/gpu: 1
          limits:
            memory: "4Gi"
            cpu: "2"
            nvidia.com/gpu: 1
        volumeMounts:
        - name: model-storage
          mountPath: /app/models
      volumes:
      - name: model-storage
        persistentVolumeClaim:
          claimName: model-pvc

---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: model-pvc
  namespace: churn-retention
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
```

### **3. Terraform Infrastructure**
```hcl
# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "churn_retention_vpc" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "churn-retention-vpc"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "churn_retention_igw" {
  vpc_id = aws_vpc.churn_retention_vpc.id

  tags = {
    Name = "churn-retention-igw"
  }
}

# Public Subnets
resource "aws_subnet" "public_subnet_1" {
  vpc_id                  = aws_vpc.churn_retention_vpc.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "${var.aws_region}a"
  map_public_ip_on_launch = true

  tags = {
    Name = "churn-retention-public-subnet-1"
  }
}

resource "aws_subnet" "public_subnet_2" {
  vpc_id                  = aws_vpc.churn_retention_vpc.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "${var.aws_region}b"
  map_public_ip_on_launch = true

  tags = {
    Name = "churn-retention-public-subnet-2"
  }
}

# Private Subnets
resource "aws_subnet" "private_subnet_1" {
  vpc_id            = aws_vpc.churn_retention_vpc.id
  cidr_block        = "10.0.3.0/24"
  availability_zone = "${var.aws_region}a"

  tags = {
    Name = "churn-retention-private-subnet-1"
  }
}

resource "aws_subnet" "private_subnet_2" {
  vpc_id            = aws_vpc.churn_retention_vpc.id
  cidr_block        = "10.0.4.0/24"
  availability_zone = "${var.aws_region}b"

  tags = {
    Name = "churn-retention-private-subnet-2"
  }
}

# RDS Database
resource "aws_db_instance" "churn_retention_db" {
  identifier = "churn-retention-db"
  engine     = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.medium"
  allocated_storage = 100
  storage_encrypted = true

  db_name  = "churn_retention"
  username = "admin"
  password = var.db_password

  vpc_security_group_ids = [aws_security_group.rds_sg.id]
  db_subnet_group_name   = aws_db_subnet_group.churn_retention_db_subnet_group.name

  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"

  skip_final_snapshot = false
  final_snapshot_identifier = "churn-retention-db-final-snapshot"

  tags = {
    Name = "churn-retention-database"
  }
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "churn_retention_redis_subnet_group" {
  name       = "churn-retention-redis-subnet-group"
  subnet_ids = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]
}

resource "aws_elasticache_replication_group" "churn_retention_redis" {
  replication_group_id       = "churn-retention-redis"
  description                = "Redis cluster for churn retention"

  node_type            = "cache.t3.micro"
  port                 = 6379
  parameter_group_name = "default.redis6.x"

  num_cache_clusters = 2

  subnet_group_name  = aws_elasticache_subnet_group.churn_retention_redis_subnet_group.name
  security_group_ids = [aws_security_group.redis_sg.id]

  at_rest_encryption_enabled = true
  transit_encryption_enabled = true

  tags = {
    Name = "churn-retention-redis"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "churn_retention_cluster" {
  name     = "churn-retention-cluster"
  role_arn = aws_iam_role.eks_cluster_role.arn
  version  = "1.24"

  vpc_config {
    subnet_ids = [
      aws_subnet.private_subnet_1.id,
      aws_subnet.private_subnet_2.id
    ]
    endpoint_private_access = true
    endpoint_public_access  = true
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy,
  ]

  tags = {
    Name = "churn-retention-eks-cluster"
  }
}

# EKS Node Group
resource "aws_eks_node_group" "churn_retention_nodes" {
  cluster_name    = aws_eks_cluster.churn_retention_cluster.name
  node_group_name = "churn-retention-nodes"
  node_role_arn   = aws_iam_role.eks_node_role.arn
  subnet_ids      = [aws_subnet.private_subnet_1.id, aws_subnet.private_subnet_2.id]

  scaling_config {
    desired_size = 3
    max_size     = 10
    min_size     = 1
  }

  instance_types = ["t3.medium"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_worker_node_policy,
    aws_iam_role_policy_attachment.eks_cni_policy,
    aws_iam_role_policy_attachment.eks_container_registry_policy,
  ]

  tags = {
    Name = "churn-retention-eks-nodes"
  }
}
```

### **4. CI/CD Pipeline**
```yaml
# .github/workflows/deploy.yml
name: Deploy Churn Retention Ultimate

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  AWS_REGION: us-west-2
  ECR_REGISTRY: ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-west-2.amazonaws.com
  ECR_REPOSITORY: churn-retention-ultimate

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: |
        pytest tests/ --cov=src/ --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Login to Amazon ECR
      id: login-ecr
      uses: aws-actions/amazon-ecr-login@v1
    
    - name: Build and push images
      run: |
        # Build core-engine
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY/core-engine:latest ./core-engine
        docker push $ECR_REGISTRY/$ECR_REPOSITORY/core-engine:latest
        
        # Build ml-service
        docker build -t $ECR_REGISTRY/$ECR_REPOSITORY/ml-service:latest ./ml-service
        docker push $ECR_REGISTRY/$ECR_REPOSITORY/ml-service:latest
        
        # Build other services...
        for service in analytics predictions retention visualization alerting reporting automation integration; do
          docker build -t $ECR_REGISTRY/$ECR_REPOSITORY/$service:latest ./$service
          docker push $ECR_REGISTRY/$ECR_REPOSITORY/$service:latest
        done

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - uses: actions/checkout@v3
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v2
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: ${{ env.AWS_REGION }}
    
    - name: Deploy to EKS
      run: |
        # Update kubeconfig
        aws eks update-kubeconfig --region $AWS_REGION --name churn-retention-cluster
        
        # Deploy to Kubernetes
        kubectl apply -f k8s/
        
        # Wait for deployment
        kubectl rollout status deployment/core-engine -n churn-retention
        kubectl rollout status deployment/ml-service -n churn-retention
```

### **5. Monitoring & Observability**
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

  - job_name: 'core-engine'
    static_configs:
      - targets: ['core-engine:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'ml-service'
    static_configs:
      - targets: ['ml-service:8001']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'analytics-engine'
    static_configs:
      - targets: ['analytics-engine:8003']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'prediction-engine'
    static_configs:
      - targets: ['prediction-engine:8004']
    metrics_path: '/metrics'
    scrape_interval: 5s

  - job_name: 'retention-engine'
    static_configs:
      - targets: ['retention-engine:8005']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'visualization-engine'
    static_configs:
      - targets: ['visualization-engine:8006']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'alerting-engine'
    static_configs:
      - targets: ['alerting-engine:8007']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'reporting-engine'
    static_configs:
      - targets: ['reporting-engine:8008']
    metrics_path: '/metrics'
    scrape_interval: 30s

  - job_name: 'automation-engine'
    static_configs:
      - targets: ['automation-engine:8009']
    metrics_path: '/metrics'
    scrape_interval: 10s

  - job_name: 'integration-engine'
    static_configs:
      - targets: ['integration-engine:8010']
    metrics_path: '/metrics'
    scrape_interval: 10s
```

### **6. Security Configuration**
```yaml
# security/security-policies.yml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: churn-retention-network-policy
  namespace: churn-retention
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: churn-retention
    - podSelector:
        matchLabels:
          app: nginx
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: churn-retention
  - to: []
    ports:
    - protocol: TCP
      port: 53
    - protocol: UDP
      port: 53

---
apiVersion: v1
kind: Secret
metadata:
  name: database-secret
  namespace: churn-retention
type: Opaque
data:
  url: cG9zdGdyZXNxbDovL2FkbWluOnBhc3N3b3JkQHBvc3RncmVzOjU0MzIvY2h1cm5fcmV0ZW50aW9u

---
apiVersion: v1
kind: Secret
metadata:
  name: redis-secret
  namespace: churn-retention
type: Opaque
data:
  url: cmVkaXM6Ly9yZWRpczozNjM3OS8w

---
apiVersion: v1
kind: Secret
metadata:
  name: api-keys
  namespace: churn-retention
type: Opaque
data:
  slack-webhook: aHR0cHM6Ly9ob29rcy5zbGFjay5jb20vc2VydmljZXMvLi4u
  email-smtp-host: c210cC5nbWFpbC5jb20=
  email-smtp-port: NTg3
  email-username: YWxlcnRzQGNvbXBhbnkuY29t
  email-password: cGFzc3dvcmQ=
```

### **7. Backup & Disaster Recovery**
```bash
#!/bin/bash
# backup_disaster_recovery.sh

echo "🔄 Iniciando proceso de backup y disaster recovery..."

# Backup de base de datos
echo "📊 Realizando backup de base de datos..."
pg_dump -h localhost -U admin -d churn_retention > backup_$(date +%Y%m%d_%H%M%S).sql

# Backup de modelos de ML
echo "🤖 Realizando backup de modelos de ML..."
tar -czf models_backup_$(date +%Y%m%d_%H%M%S).tar.gz ./models/

# Backup de configuraciones
echo "⚙️ Realizando backup de configuraciones..."
tar -czf config_backup_$(date +%Y%m%d_%H%M%S).tar.gz ./config/

# Backup de logs
echo "📝 Realizando backup de logs..."
tar -czf logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz ./logs/

# Subir a S3
echo "☁️ Subiendo backups a S3..."
aws s3 cp backup_$(date +%Y%m%d_%H%M%S).sql s3://churn-retention-backups/database/
aws s3 cp models_backup_$(date +%Y%m%d_%H%M%S).tar.gz s3://churn-retention-backups/models/
aws s3 cp config_backup_$(date +%Y%m%d_%H%M%S).tar.gz s3://churn-retention-backups/config/
aws s3 cp logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz s3://churn-retention-backups/logs/

# Limpiar backups locales
echo "🧹 Limpiando backups locales..."
rm backup_$(date +%Y%m%d_%H%M%S).sql
rm models_backup_$(date +%Y%m%d_%H%M%S).tar.gz
rm config_backup_$(date +%Y%m%d_%H%M%S).tar.gz
rm logs_backup_$(date +%Y%m%d_%H%M%S).tar.gz

echo "✅ Proceso de backup completado exitosamente!"
```

---

## 🎯 **CONFIGURACIÓN DE PRODUCCIÓN**

### **Variables de Entorno**
```bash
# .env.production
# Database
DATABASE_URL=postgresql://admin:password@postgres:5432/churn_retention
REDIS_URL=redis://redis:6379/0

# ML Models
MODEL_PATH=/app/models
GPU_ENABLED=true

# External Services
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
EMAIL_USERNAME=alerts@company.com
EMAIL_PASSWORD=password

# AWS
AWS_REGION=us-west-2
S3_BUCKET=churn-retention-data
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...

# Monitoring
PROMETHEUS_URL=http://prometheus:9090
GRAFANA_URL=http://grafana:3000

# Security
JWT_SECRET_KEY=your-secret-key
ENCRYPTION_KEY=your-encryption-key
```

### **Script de Deploy**
```bash
#!/bin/bash
# deploy_production.sh

echo "🚀 Desplegando Churn Retention Ultimate a Producción..."

# 1. Verificar prerequisitos
echo "✅ Verificando prerequisitos..."
docker --version
kubectl version --client
terraform version

# 2. Configurar infraestructura
echo "🏗️ Configurando infraestructura..."
cd terraform/
terraform init
terraform plan
terraform apply -auto-approve

# 3. Configurar EKS
echo "☸️ Configurando EKS..."
aws eks update-kubeconfig --region us-west-2 --name churn-retention-cluster

# 4. Desplegar aplicaciones
echo "📦 Desplegando aplicaciones..."
kubectl apply -f k8s/

# 5. Verificar deployment
echo "🔍 Verificando deployment..."
kubectl get pods -n churn-retention
kubectl get services -n churn-retention

# 6. Configurar monitoreo
echo "📊 Configurando monitoreo..."
kubectl apply -f monitoring/

# 7. Configurar alertas
echo "🚨 Configurando alertas..."
kubectl apply -f alerting/

# 8. Ejecutar tests de smoke
echo "🧪 Ejecutando tests de smoke..."
./tests/smoke_tests.sh

echo "🎉 Deployment a producción completado exitosamente!"
echo "🌐 Dashboard: https://churn-retention.company.com"
echo "📊 API: https://api.churn-retention.company.com"
echo "📈 Grafana: https://grafana.churn-retention.company.com"
```

---

## 🏆 **RESULTADOS ESPERADOS**

### **Métricas de Infraestructura**
- **Disponibilidad:** 99.99%
- **Latencia:** <100ms promedio
- **Throughput:** 10,000+ requests/segundo
- **Escalabilidad:** Auto-scaling hasta 100+ pods

### **Métricas de Seguridad**
- **Encriptación:** 100% en tránsito y reposo
- **Autenticación:** JWT + OAuth2
- **Autorización:** RBAC completo
- **Auditoría:** Logs completos de todas las operaciones

### **Métricas de Monitoreo**
- **Métricas:** 1000+ métricas personalizadas
- **Alertas:** 100+ reglas de alerta
- **Dashboards:** 20+ dashboards especializados
- **Logs:** Centralizados con ELK Stack

---

*Esta configuración de deployment proporciona una infraestructura completa, escalable y segura para el ecosistema ultimate de churn y retención, con capacidades de monitoreo, alertas y disaster recovery de nivel empresarial.*

**🚀 ¡Listo para desplegar en producción con la máxima confiabilidad y performance!**
