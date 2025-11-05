---
title: "Documentacion Tecnica Recomendaciones"
category: "documentacion_tecnica_recomendaciones.md"
tags: []
created: "2025-10-29"
path: "documentacion_tecnica_recomendaciones.md"
---

# 📚 **DOCUMENTACIÓN TÉCNICA - SISTEMA DE RECOMENDACIONES**

## **ÍNDICE**
1. [Arquitectura del Sistema](#arquitectura)
2. [API Reference](#api)
3. [Base de Datos](#database)
4. [Algoritmos](#algoritmos)
5. [Configuración](#configuracion)
6. [Despliegue](#despliegue)
7. [Monitoreo](#monitoreo)
8. [Troubleshooting](#troubleshooting)
9. [Contribución](#contribucion)
10. [Changelog](#changelog)

---

## **1. ARQUITECTURA DEL SISTEMA** {#arquitectura}

### **Diagrama de Arquitectura**
```mermaid
graph TB
    subgraph "Frontend"
        A[Web App] --> B[Mobile App]
        B --> C[Admin Dashboard]
    end
    
    subgraph "API Gateway"
        D[Load Balancer] --> E[API Gateway]
        E --> F[Rate Limiting]
        F --> G[Authentication]
    end
    
    subgraph "Microservices"
        H[User Service] --> I[Product Service]
        I --> J[Recommendation Service]
        J --> K[Analytics Service]
    end
    
    subgraph "Data Layer"
        L[PostgreSQL] --> M[Redis Cache]
        M --> N[Elasticsearch]
    end
    
    subgraph "ML Pipeline"
        O[Data Processing] --> P[Model Training]
        P --> Q[Model Serving]
    end
    
    A --> D
    B --> D
    C --> D
    
    G --> H
    G --> I
    G --> J
    G --> K
    
    H --> L
    I --> L
    J --> L
    K --> L
    
    J --> M
    K --> N
    
    O --> L
    P --> Q
    Q --> J
```

### **Componentes Principales**

#### **API Gateway**
- **Función**: Punto de entrada único para todas las APIs
- **Tecnología**: Kong/NGINX
- **Características**:
  - Load balancing
  - Rate limiting
  - Authentication/Authorization
  - Request/Response transformation
  - Logging y monitoring

#### **Microservicios**
- **User Service**: Gestión de usuarios y perfiles
- **Product Service**: Catálogo de productos
- **Recommendation Service**: Motor de recomendaciones
- **Analytics Service**: Métricas y análisis

#### **Data Layer**
- **PostgreSQL**: Base de datos principal
- **Redis**: Cache y sesiones
- **Elasticsearch**: Búsqueda y analytics

---

## **2. API REFERENCE** {#api}

### **Endpoints Principales**

#### **GET /api/v1/recommendations/{user_id}**
Obtener recomendaciones para un usuario específico.

**Parámetros:**
- `user_id` (string, requerido): ID del usuario
- `limit` (integer, opcional): Número de recomendaciones (default: 10)
- `context` (object, opcional): Contexto adicional

**Ejemplo de Request:**
```bash
curl -X GET "https://api.recommendations.com/v1/recommendations/user123?limit=5" \
  -H "Authorization: Bearer your_token"
```

**Ejemplo de Response:**
```json
{
  "user_id": "user123",
  "recommendations": [
    {
      "product_id": "prod456",
      "title": "Product Title",
      "price": 99.99,
      "score": 0.85,
      "reason": "Similar users also liked this"
    }
  ],
  "timestamp": "2024-01-15T10:30:00Z",
  "algorithm": "hybrid",
  "metadata": {
    "processing_time_ms": 150,
    "cache_hit": true
  }
}
```

#### **POST /api/v1/recommendations/batch**
Obtener recomendaciones para múltiples usuarios.

**Request Body:**
```json
{
  "user_ids": ["user1", "user2", "user3"],
  "limit": 5,
  "context": {
    "category": "electronics",
    "price_range": [50, 200]
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "user_id": "user1",
      "recommendations": [...],
      "status": "success"
    }
  ],
  "processed_count": 3,
  "failed_count": 0
}
```

#### **GET /api/v1/recommendations/{user_id}/metrics**
Obtener métricas de calidad de recomendaciones.

**Response:**
```json
{
  "user_id": "user123",
  "metrics": {
    "precision_at_5": 0.15,
    "recall_at_10": 0.25,
    "diversity": 0.7,
    "novelty": 0.6
  },
  "period": "30d"
}
```

### **Códigos de Error**

| Código | Descripción |
|--------|-------------|
| 400 | Bad Request - Parámetros inválidos |
| 401 | Unauthorized - Token de autenticación inválido |
| 403 | Forbidden - Sin permisos para acceder al recurso |
| 404 | Not Found - Usuario o recurso no encontrado |
| 429 | Too Many Requests - Límite de velocidad excedido |
| 500 | Internal Server Error - Error interno del servidor |
| 503 | Service Unavailable - Servicio temporalmente no disponible |

---

## **3. BASE DE DATOS** {#database}

### **Esquema de Base de Datos**

#### **Tabla: users**
```sql
CREATE TABLE users (
    user_id VARCHAR(50) PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    age INTEGER,
    gender VARCHAR(20),
    preferences JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at);
```

#### **Tabla: products**
```sql
CREATE TABLE products (
    product_id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    price DECIMAL(10,2),
    availability BOOLEAN DEFAULT TRUE,
    features JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_products_availability ON products(availability);
```

#### **Tabla: user_interactions**
```sql
CREATE TABLE user_interactions (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    context JSONB,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_interactions_user_id ON user_interactions(user_id);
CREATE INDEX idx_interactions_product_id ON user_interactions(product_id);
CREATE INDEX idx_interactions_timestamp ON user_interactions(timestamp);
CREATE INDEX idx_interactions_action ON user_interactions(action);
```

#### **Tabla: recommendations**
```sql
CREATE TABLE recommendations (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(50) NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    score DECIMAL(5,4) NOT NULL,
    algorithm VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    metadata JSONB,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id)
);

CREATE INDEX idx_recommendations_user_id ON recommendations(user_id);
CREATE INDEX idx_recommendations_score ON recommendations(score DESC);
CREATE INDEX idx_recommendations_algorithm ON recommendations(algorithm);
CREATE INDEX idx_recommendations_expires_at ON recommendations(expires_at);
```

### **Consultas Optimizadas**

#### **Obtener recomendaciones para usuario**
```sql
SELECT r.product_id, p.title, p.price, r.score, r.algorithm
FROM recommendations r
JOIN products p ON r.product_id = p.product_id
WHERE r.user_id = $1
  AND r.expires_at > NOW()
  AND p.availability = TRUE
ORDER BY r.score DESC
LIMIT $2;
```

#### **Obtener interacciones recientes del usuario**
```sql
SELECT ui.product_id, ui.action, ui.rating, ui.timestamp
FROM user_interactions ui
WHERE ui.user_id = $1
  AND ui.timestamp >= NOW() - INTERVAL '30 days'
ORDER BY ui.timestamp DESC;
```

#### **Calcular similitud entre usuarios**
```sql
WITH user_ratings AS (
  SELECT user_id, product_id, rating
  FROM user_interactions
  WHERE action = 'rating'
    AND rating IS NOT NULL
),
user_similarity AS (
  SELECT 
    u1.user_id as user1,
    u2.user_id as user2,
    COUNT(*) as common_products,
    AVG(ABS(u1.rating - u2.rating)) as avg_rating_diff
  FROM user_ratings u1
  JOIN user_ratings u2 ON u1.product_id = u2.product_id
  WHERE u1.user_id != u2.user_id
  GROUP BY u1.user_id, u2.user_id
  HAVING COUNT(*) >= 3
)
SELECT user1, user2, 
       (1 - avg_rating_diff / 4.0) as similarity
FROM user_similarity
WHERE user1 = $1
ORDER BY similarity DESC;
```

---

## **4. ALGORITMOS** {#algoritmos}

### **Filtrado Colaborativo**

#### **Implementación Básica**
```python
import numpy as np
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

class CollaborativeFiltering:
    def __init__(self, min_common_items=3):
        self.min_common_items = min_common_items
        self.user_item_matrix = None
        self.user_similarities = None
    
    def fit(self, interactions):
        """Entrenar el modelo con interacciones"""
        # Crear matriz usuario-item
        user_ids = interactions['user_id'].unique()
        product_ids = interactions['product_id'].unique()
        
        user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
        product_to_idx = {pid: i for i, pid in enumerate(product_ids)}
        
        # Construir matriz dispersa
        rows = [user_to_idx[uid] for uid in interactions['user_id']]
        cols = [product_to_idx[pid] for pid in interactions['product_id']]
        data = interactions['rating'].values
        
        self.user_item_matrix = csr_matrix(
            (data, (rows, cols)), 
            shape=(len(user_ids), len(product_ids))
        )
        
        # Calcular similitudes entre usuarios
        self.user_similarities = cosine_similarity(self.user_item_matrix)
        
        # Guardar mapeos
        self.user_ids = user_ids
        self.product_ids = product_ids
        self.user_to_idx = user_to_idx
        self.product_to_idx = product_to_idx
    
    def predict(self, user_id, n_recommendations=10):
        """Predecir recomendaciones para un usuario"""
        if user_id not in self.user_to_idx:
            return self._cold_start_recommendations(n_recommendations)
        
        user_idx = self.user_to_idx[user_id]
        user_ratings = self.user_item_matrix[user_idx].toarray().flatten()
        
        # Encontrar usuarios similares
        similarities = self.user_similarities[user_idx]
        similar_users = np.argsort(similarities)[::-1][1:]  # Excluir el usuario mismo
        
        # Calcular scores de productos
        product_scores = np.zeros(len(self.product_ids))
        
        for similar_user_idx in similar_users:
            if similarities[similar_user_idx] < 0.1:  # Umbral de similitud
                break
            
            similar_user_ratings = self.user_item_matrix[similar_user_idx].toarray().flatten()
            
            # Solo considerar productos que el usuario similar ha calificado
            # pero el usuario actual no
            unrated_mask = (user_ratings == 0) & (similar_user_ratings > 0)
            
            if np.sum(unrated_mask) >= self.min_common_items:
                product_scores[unrated_mask] += (
                    similarities[similar_user_idx] * similar_user_ratings[unrated_mask]
                )
        
        # Obtener top recomendaciones
        top_products = np.argsort(product_scores)[::-1][:n_recommendations]
        
        recommendations = []
        for product_idx in top_products:
            if product_scores[product_idx] > 0:
                recommendations.append({
                    'product_id': self.product_ids[product_idx],
                    'score': product_scores[product_idx]
                })
        
        return recommendations
```

### **Filtrado Basado en Contenido**

#### **Implementación con TF-IDF**
```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ContentBasedFiltering:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.product_features = None
        self.product_ids = None
    
    def fit(self, products):
        """Entrenar el modelo con productos"""
        # Combinar título y descripción
        product_texts = []
        self.product_ids = []
        
        for _, product in products.iterrows():
            text = f"{product['title']} {product['description']}"
            product_texts.append(text)
            self.product_ids.append(product['product_id'])
        
        # Vectorizar productos
        self.product_features = self.vectorizer.fit_transform(product_texts)
    
    def predict(self, user_profile, n_recommendations=10):
        """Predecir recomendaciones basadas en perfil de usuario"""
        # Crear perfil de usuario como vector
        user_vector = self.vectorizer.transform([user_profile])
        
        # Calcular similitud con productos
        similarities = cosine_similarity(user_vector, self.product_features).flatten()
        
        # Obtener top recomendaciones
        top_indices = np.argsort(similarities)[::-1][:n_recommendations]
        
        recommendations = []
        for idx in top_indices:
            if similarities[idx] > 0:
                recommendations.append({
                    'product_id': self.product_ids[idx],
                    'score': similarities[idx]
                })
        
        return recommendations
```

### **Sistema Híbrido**

#### **Implementación de Fusión**
```python
class HybridRecommendationSystem:
    def __init__(self, collaborative_weight=0.6, content_weight=0.4):
        self.collaborative_weight = collaborative_weight
        self.content_weight = content_weight
        
        self.collaborative_filter = CollaborativeFiltering()
        self.content_filter = ContentBasedFiltering()
    
    def fit(self, interactions, products, user_profiles):
        """Entrenar ambos modelos"""
        self.collaborative_filter.fit(interactions)
        self.content_filter.fit(products)
        self.user_profiles = user_profiles
    
    def predict(self, user_id, n_recommendations=10):
        """Generar recomendaciones híbridas"""
        # Obtener recomendaciones colaborativas
        collab_recs = self.collaborative_filter.predict(user_id, n_recommendations * 2)
        
        # Obtener recomendaciones basadas en contenido
        if user_id in self.user_profiles:
            user_profile = self.user_profiles[user_id]
            content_recs = self.content_filter.predict(user_profile, n_recommendations * 2)
        else:
            content_recs = []
        
        # Fusionar recomendaciones
        merged_scores = {}
        
        # Agregar scores colaborativos
        for rec in collab_recs:
            product_id = rec['product_id']
            merged_scores[product_id] = {
                'collaborative_score': rec['score'],
                'content_score': 0,
                'final_score': 0
            }
        
        # Agregar scores de contenido
        for rec in content_recs:
            product_id = rec['product_id']
            if product_id in merged_scores:
                merged_scores[product_id]['content_score'] = rec['score']
            else:
                merged_scores[product_id] = {
                    'collaborative_score': 0,
                    'content_score': rec['score'],
                    'final_score': 0
                }
        
        # Calcular scores finales
        for product_id, scores in merged_scores.items():
            scores['final_score'] = (
                self.collaborative_weight * scores['collaborative_score'] +
                self.content_weight * scores['content_score']
            )
        
        # Obtener top recomendaciones
        sorted_products = sorted(
            merged_scores.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )
        
        recommendations = []
        for product_id, scores in sorted_products[:n_recommendations]:
            if scores['final_score'] > 0:
                recommendations.append({
                    'product_id': product_id,
                    'score': scores['final_score'],
                    'collaborative_score': scores['collaborative_score'],
                    'content_score': scores['content_score']
                })
        
        return recommendations
```

---

## **5. CONFIGURACIÓN** {#configuracion}

### **Variables de Entorno**

#### **Base de Datos**
```bash
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/recommendations
DB_HOST=localhost
DB_PORT=5432
DB_NAME=recommendations
DB_USER=recommendations_user
DB_PASSWORD=secure_password

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=redis_password
```

#### **API y Servicios**
```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=5000
API_WORKERS=4
API_TIMEOUT=30

# Authentication
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24

# Rate Limiting
RATE_LIMIT_PER_MINUTE=100
RATE_LIMIT_BURST=200
```

#### **Machine Learning**
```bash
# Model Configuration
MODEL_PATH=/app/models
MODEL_UPDATE_INTERVAL=3600
MIN_TRAINING_SAMPLES=1000
COLD_START_THRESHOLD=5

# Feature Engineering
MAX_FEATURES=1000
MIN_DF=2
MAX_DF=0.95
NGRAM_RANGE=1,2
```

### **Archivo de Configuración**

#### **config.yaml**
```yaml
# Configuración de la aplicación
app:
  name: "Recommendation System"
  version: "1.0.0"
  debug: false
  host: "0.0.0.0"
  port: 5000

# Configuración de base de datos
database:
  postgresql:
    host: "${DB_HOST}"
    port: "${DB_PORT}"
    database: "${DB_NAME}"
    username: "${DB_USER}"
    password: "${DB_PASSWORD}"
    pool_size: 20
    max_overflow: 30
  
  redis:
    host: "${REDIS_HOST}"
    port: "${REDIS_PORT}"
    password: "${REDIS_PASSWORD}"
    db: 0
    max_connections: 100

# Configuración de autenticación
auth:
  jwt_secret: "${JWT_SECRET_KEY}"
  algorithm: "HS256"
  expiration_hours: 24
  refresh_expiration_days: 7

# Configuración de rate limiting
rate_limiting:
  enabled: true
  requests_per_minute: 100
  burst_size: 200
  window_size: 60

# Configuración de cache
cache:
  enabled: true
  ttl_seconds: 300
  max_size: 10000
  eviction_policy: "LRU"

# Configuración de algoritmos
algorithms:
  collaborative_filtering:
    enabled: true
    min_common_items: 3
    similarity_threshold: 0.1
  
  content_based:
    enabled: true
    max_features: 1000
    min_df: 2
    max_df: 0.95
  
  hybrid:
    enabled: true
    collaborative_weight: 0.6
    content_weight: 0.4

# Configuración de monitoreo
monitoring:
  enabled: true
  metrics_port: 9090
  health_check_interval: 30
  log_level: "INFO"
```

---

## **6. DESPLIEGUE** {#despliegue}

### **Docker**

#### **Dockerfile**
```dockerfile
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Exponer puerto
EXPOSE 5000

# Comando de inicio
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
```

#### **docker-compose.yml**
```yaml
version: '3.8'

services:
  # Base de datos PostgreSQL
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: recommendations
      POSTGRES_USER: recommendations_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U recommendations_user -d recommendations"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Cache Redis
  redis:
    image: redis:6-alpine
    command: redis-server --requirepass redis_password
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Aplicación principal
  app:
    build: .
    environment:
      - DATABASE_URL=postgresql://recommendations_user:secure_password@postgres:5432/recommendations
      - REDIS_URL=redis://:redis_password@redis:6379/0
      - JWT_SECRET_KEY=your-secret-key
    ports:
      - "5000:5000"
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ./models:/app/models
    restart: unless-stopped

  # NGINX Load Balancer
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### **Kubernetes**

#### **deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: recommendation-system
  labels:
    app: recommendation-system
spec:
  replicas: 3
  selector:
    matchLabels:
      app: recommendation-system
  template:
    metadata:
      labels:
        app: recommendation-system
    spec:
      containers:
      - name: app
        image: recommendation-system:latest
        ports:
        - containerPort: 5000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-secret
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
            port: 5000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: recommendation-service
spec:
  selector:
    app: recommendation-system
  ports:
  - protocol: TCP
    port: 80
    targetPort: 5000
  type: LoadBalancer
```

### **Terraform**

#### **main.tf**
```hcl
# Configuración de AWS
provider "aws" {
  region = "us-west-2"
}

# VPC
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  
  tags = {
    Name = "recommendation-system-vpc"
  }
}

# Subnet pública
resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  
  tags = {
    Name = "recommendation-system-public"
  }
}

# Subnet privada
resource "aws_subnet" "private" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  
  tags = {
    Name = "recommendation-system-private"
  }
}

# RDS PostgreSQL
resource "aws_db_instance" "postgres" {
  identifier = "recommendation-postgres"
  engine     = "postgres"
  engine_version = "13.7"
  instance_class = "db.t3.micro"
  allocated_storage = 20
  storage_type = "gp2"
  
  db_name  = "recommendations"
  username = "recommendations_user"
  password = var.db_password
  
  vpc_security_group_ids = [aws_security_group.rds.id]
  db_subnet_group_name   = aws_db_subnet_group.main.name
  
  backup_retention_period = 7
  backup_window          = "03:00-04:00"
  maintenance_window     = "sun:04:00-sun:05:00"
  
  skip_final_snapshot = true
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "main" {
  name       = "recommendation-cache-subnet"
  subnet_ids = [aws_subnet.private.id]
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "recommendation-redis"
  engine               = "redis"
  node_type            = "cache.t3.micro"
  num_cache_nodes      = 1
  parameter_group_name = "default.redis6.x"
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.main.name
  security_group_ids   = [aws_security_group.redis.id]
}

# ECS Cluster
resource "aws_ecs_cluster" "main" {
  name = "recommendation-system"
}

# ECS Task Definition
resource "aws_ecs_task_definition" "app" {
  family                   = "recommendation-app"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.ecs_execution_role.arn
  
  container_definitions = jsonencode([
    {
      name  = "app"
      image = "recommendation-system:latest"
      portMappings = [
        {
          containerPort = 5000
          protocol      = "tcp"
        }
      ]
      environment = [
        {
          name  = "DATABASE_URL"
          value = "postgresql://recommendations_user:${var.db_password}@${aws_db_instance.postgres.endpoint}/recommendations"
        },
        {
          name  = "REDIS_URL"
          value = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          awslogs-group         = aws_cloudwatch_log_group.app.name
          awslogs-region        = "us-west-2"
          awslogs-stream-prefix = "ecs"
        }
      }
    }
  ])
}

# ECS Service
resource "aws_ecs_service" "app" {
  name            = "recommendation-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 2
  launch_type     = "FARGATE"
  
  network_configuration {
    subnets          = [aws_subnet.private.id]
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = false
  }
  
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 5000
  }
  
  depends_on = [aws_lb_listener.app]
}
```

---

## **7. MONITOREO** {#monitoreo}

### **Métricas de Aplicación**

#### **Prometheus Metrics**
```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# Métricas de recomendaciones
recommendation_requests = Counter(
    'recommendation_requests_total',
    'Total number of recommendation requests',
    ['user_id', 'algorithm']
)

recommendation_duration = Histogram(
    'recommendation_duration_seconds',
    'Time spent generating recommendations',
    ['algorithm']
)

active_users = Gauge(
    'active_users_total',
    'Number of active users'
)

recommendation_quality = Gauge(
    'recommendation_quality_score',
    'Quality score of recommendations',
    ['metric_type']
)

# Decorador para medir duración
def measure_duration(metric_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            recommendation_duration.labels(algorithm=metric_name).observe(duration)
            return result
        return wrapper
    return decorator

# Ejemplo de uso
@measure_duration('collaborative_filtering')
def get_collaborative_recommendations(user_id):
    # Lógica de recomendaciones
    pass
```

#### **Health Checks**
```python
from flask import Flask, jsonify
import psycopg2
import redis

app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check básico"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/ready')
def readiness_check():
    """Readiness check con dependencias"""
    checks = {
        'database': check_database(),
        'redis': check_redis(),
        'models': check_models()
    }
    
    all_healthy = all(checks.values())
    
    return jsonify({
        'status': 'ready' if all_healthy else 'not_ready',
        'checks': checks,
        'timestamp': datetime.utcnow().isoformat()
    }), 200 if all_healthy else 503

def check_database():
    """Verificar conexión a base de datos"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.close()
        return True
    except Exception:
        return False

def check_redis():
    """Verificar conexión a Redis"""
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        return True
    except Exception:
        return False

def check_models():
    """Verificar que los modelos están cargados"""
    try:
        # Verificar que los modelos están disponibles
        return os.path.exists(MODEL_PATH)
    except Exception:
        return False
```

### **Logging**

#### **Configuración de Logging**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry)

# Configurar logging
def setup_logging():
    logger = logging.getLogger('recommendation_system')
    logger.setLevel(logging.INFO)
    
    # Handler para archivo
    file_handler = logging.FileHandler('app.log')
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)
    
    return logger

# Logger personalizado
class RecommendationLogger:
    def __init__(self):
        self.logger = setup_logging()
    
    def log_recommendation_request(self, user_id, algorithm, duration, success):
        self.logger.info(
            f"Recommendation request processed",
            extra={
                'user_id': user_id,
                'algorithm': algorithm,
                'duration_ms': duration * 1000,
                'success': success
            }
        )
    
    def log_recommendation_quality(self, user_id, metrics):
        self.logger.info(
            f"Recommendation quality metrics",
            extra={
                'user_id': user_id,
                'metrics': metrics
            }
        )
```

---

## **8. TROUBLESHOOTING** {#troubleshooting}

### **Problemas Comunes**

#### **Alto Tiempo de Respuesta**
```bash
# Verificar logs de aplicación
tail -f /var/log/app.log | grep "recommendation_duration"

# Verificar métricas de Prometheus
curl http://localhost:9090/api/v1/query?query=recommendation_duration_seconds

# Verificar uso de CPU y memoria
top -p $(pgrep -f "recommendation")

# Verificar conexiones de base de datos
psql -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';"
```

#### **Errores de Base de Datos**
```bash
# Verificar estado de PostgreSQL
systemctl status postgresql

# Verificar logs de PostgreSQL
tail -f /var/log/postgresql/postgresql-13-main.log

# Verificar conexiones activas
psql -c "SELECT pid, usename, application_name, client_addr, state FROM pg_stat_activity;"

# Verificar locks
psql -c "SELECT * FROM pg_locks WHERE NOT granted;"
```

#### **Problemas de Cache**
```bash
# Verificar estado de Redis
redis-cli ping

# Verificar memoria de Redis
redis-cli info memory

# Verificar keys en cache
redis-cli keys "recommendations:*"

# Limpiar cache si es necesario
redis-cli flushdb
```

### **Scripts de Diagnóstico**

#### **health_check.py**
```python
#!/usr/bin/env python3
import requests
import psycopg2
import redis
import sys

def check_api():
    """Verificar API"""
    try:
        response = requests.get('http://localhost:5000/health', timeout=5)
        return response.status_code == 200
    except Exception as e:
        print(f"API check failed: {e}")
        return False

def check_database():
    """Verificar base de datos"""
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Database check failed: {e}")
        return False

def check_redis():
    """Verificar Redis"""
    try:
        r = redis.from_url(REDIS_URL)
        r.ping()
        return True
    except Exception as e:
        print(f"Redis check failed: {e}")
        return False

def main():
    checks = {
        'API': check_api(),
        'Database': check_database(),
        'Redis': check_redis()
    }
    
    all_healthy = all(checks.values())
    
    print("Health Check Results:")
    for service, healthy in checks.items():
        status = "✅ Healthy" if healthy else "❌ Unhealthy"
        print(f"  {service}: {status}")
    
    if not all_healthy:
        sys.exit(1)
    else:
        print("\n🎉 All services are healthy!")

if __name__ == "__main__":
    main()
```

---

## **9. CONTRIBUCIÓN** {#contribucion}

### **Guía de Contribución**

#### **Configuración del Entorno**
```bash
# Clonar repositorio
git clone https://github.com/your-org/recommendation-system.git
cd recommendation-system

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar pre-commit hooks
pre-commit install

# Ejecutar tests
pytest
```

#### **Estándares de Código**
```python
# Usar type hints
def get_recommendations(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """Obtener recomendaciones para un usuario.
    
    Args:
        user_id: ID del usuario
        limit: Número máximo de recomendaciones
        
    Returns:
        Lista de recomendaciones
        
    Raises:
        UserNotFoundError: Si el usuario no existe
        ValidationError: Si los parámetros son inválidos
    """
    pass

# Usar docstrings
class RecommendationEngine:
    """Motor de recomendaciones híbrido.
    
    Combina filtrado colaborativo y basado en contenido
    para generar recomendaciones personalizadas.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Inicializar motor de recomendaciones.
        
        Args:
            config: Configuración del motor
        """
        pass
```

#### **Proceso de Pull Request**
1. Crear branch desde `main`
2. Implementar cambios con tests
3. Ejecutar `pre-commit` y tests
4. Crear Pull Request con descripción detallada
5. Revisión de código
6. Merge después de aprobación

---

## **10. CHANGELOG** {#changelog}

### **Versión 1.0.0** (2024-01-15)
- ✨ Lanzamiento inicial
- 🚀 Sistema de recomendaciones híbrido
- 📊 Dashboard de métricas
- 🔒 Autenticación JWT
- 📱 API REST completa

### **Versión 1.1.0** (2024-02-01)
- ⚡ Mejoras de performance
- 🧪 Tests automatizados
- 📈 Métricas de calidad
- 🔧 Configuración mejorada

### **Versión 1.2.0** (2024-03-01)
- 🎯 A/B testing framework
- 📊 Dashboard de monitoreo
- 🔒 Mejoras de seguridad
- 📚 Documentación completa

---

## **🎯 PRÓXIMOS PASOS**

1. **Revisar Documentación**: Leer secciones relevantes
2. **Configurar Entorno**: Seguir guía de instalación
3. **Ejecutar Tests**: Verificar que todo funciona
4. **Contribuir**: Seguir guía de contribución
5. **Reportar Issues**: Usar sistema de issues

---

## **📞 SOPORTE**

- **Documentación**: [Enlaces a documentación adicional]
- **Issues**: [GitHub Issues para reportar problemas]
- **Discusiones**: [GitHub Discussions para preguntas]
- **Soporte Técnico**: [Contacto para soporte premium]

---

**¡Con esta documentación técnica completa, tu sistema de recomendaciones estará perfectamente documentado y listo para producción!** 📚



