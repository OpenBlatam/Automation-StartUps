# Guía de Implementación Técnica - Soluciones de IA para Marketing

## Introducción

Esta guía técnica detallada proporciona instrucciones paso a paso para la implementación técnica de nuestras soluciones de IA para marketing, incluyendo arquitectura, configuración, APIs, y mejores prácticas de desarrollo.

## Arquitectura del Sistema

### Arquitectura General

#### Componentes Principales
- **Frontend**: Interfaz de usuario web y móvil
- **API Gateway**: Punto de entrada único para todas las APIs
- **Microservicios**: Servicios especializados por funcionalidad
- **Base de Datos**: Almacenamiento de datos estructurados
- **Data Lake**: Almacenamiento de datos no estructurados
- **AI/ML Engine**: Motor de inteligencia artificial
- **Message Queue**: Cola de mensajes para procesamiento asíncrono

#### Beneficios de la Arquitectura
- **Escalabilidad**: 10x más capacidad con la misma infraestructura
- **Disponibilidad**: 99.9% uptime garantizado
- **Rendimiento**: <200ms tiempo de respuesta promedio
- **Seguridad**: Certificaciones ISO 27001, SOC 2 Type II
- **Mantenibilidad**: 60% menos tiempo en mantenimiento

#### Diagrama de Arquitectura
```
[Cliente] → [Load Balancer] → [API Gateway] → [Microservicios]
                                                      ↓
[Base de Datos] ← [Cache Layer] ← [Message Queue] ← [AI/ML Engine]
                                                      ↓
[Data Lake] ← [ETL Pipeline] ← [External APIs] ← [Monitoring]
```

### Microservicios

#### 1. User Management Service
- **Función**: Gestión de usuarios y autenticación
- **Tecnología**: Node.js + Express + JWT
- **Base de Datos**: PostgreSQL
- **APIs**: /auth, /users, /permissions
- **Rendimiento**: 10,000+ requests/segundo
- **Disponibilidad**: 99.95% uptime
- **Escalabilidad**: Auto-scaling hasta 100 instancias

#### 2. Marketing Automation Service
- **Función**: Automatización de campañas de marketing
- **Tecnología**: Python + FastAPI + Celery
- **Base de Datos**: MongoDB
- **APIs**: /campaigns, /automations, /triggers
- **Rendimiento**: 5,000+ campañas simultáneas
- **Disponibilidad**: 99.9% uptime
- **Escalabilidad**: Auto-scaling hasta 50 instancias

#### 3. Content Generation Service
- **Función**: Generación de contenido con IA
- **Tecnología**: Python + TensorFlow + OpenAI API
- **Base de Datos**: Redis (cache)
- **APIs**: /content, /templates, /generation

#### 4. Analytics Service
- **Función**: Análisis de datos y métricas
- **Tecnología**: Python + Pandas + Apache Spark
- **Base de Datos**: ClickHouse
- **APIs**: /analytics, /metrics, /reports

#### 5. Integration Service
- **Función**: Integración con sistemas externos
- **Tecnología**: Node.js + Express
- **Base de Datos**: PostgreSQL
- **APIs**: /integrations, /webhooks, /sync

## Configuración del Entorno

### Requisitos del Sistema

#### Servidor de Producción
- **CPU**: 8+ cores (Intel Xeon o AMD EPYC)
- **RAM**: 32+ GB
- **Almacenamiento**: 1+ TB SSD
- **Red**: 1+ Gbps
- **OS**: Ubuntu 20.04 LTS o CentOS 8

#### Servidor de Desarrollo
- **CPU**: 4+ cores
- **RAM**: 16+ GB
- **Almacenamiento**: 500+ GB SSD
- **Red**: 100+ Mbps
- **OS**: Ubuntu 20.04 LTS, macOS, o Windows 10+

### Stack Tecnológico

#### Backend
- **Lenguajes**: Python 3.9+, Node.js 18+, Go 1.19+
- **Frameworks**: FastAPI, Express.js, Gin
- **Bases de Datos**: PostgreSQL, MongoDB, Redis
- **Message Queue**: RabbitMQ, Apache Kafka
- **Cache**: Redis, Memcached

#### Frontend
- **Framework**: React 18+ con TypeScript
- **State Management**: Redux Toolkit
- **UI Library**: Material-UI, Ant Design
- **Build Tool**: Vite, Webpack
- **Testing**: Jest, Cypress

#### DevOps
- **Containerización**: Docker, Docker Compose
- **Orquestación**: Kubernetes
- **CI/CD**: GitHub Actions, GitLab CI
- **Monitoring**: Prometheus, Grafana
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana)

### Configuración de Base de Datos

#### PostgreSQL (Datos Estructurados)
```sql
-- Configuración de conexión
host: localhost
port: 5432
database: marketing_ai
username: marketing_user
password: secure_password

-- Configuración de performance
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB
maintenance_work_mem = 64MB
```

#### MongoDB (Datos No Estructurados)
```javascript
// Configuración de conexión
const mongoConfig = {
  host: 'localhost',
  port: 27017,
  database: 'marketing_ai',
  username: 'marketing_user',
  password: 'secure_password',
  options: {
    useNewUrlParser: true,
    useUnifiedTopology: true,
    maxPoolSize: 10,
    serverSelectionTimeoutMS: 5000
  }
};
```

#### Redis (Cache)
```yaml
# redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

## APIs y Endpoints

### API Gateway

#### Configuración
```yaml
# api-gateway.yml
version: '3.8'
services:
  api-gateway:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - user-service
      - marketing-service
      - content-service
```

#### Nginx Configuration
```nginx
# nginx.conf
upstream user_service {
    server user-service:3000;
}

upstream marketing_service {
    server marketing-service:3001;
}

upstream content_service {
    server content-service:3002;
}

server {
    listen 80;
    server_name api.marketing-ai.com;
    
    location /api/users/ {
        proxy_pass http://user_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/marketing/ {
        proxy_pass http://marketing_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/content/ {
        proxy_pass http://content_service/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Endpoints Principales

#### User Management API
```python
# user_service.py
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer
import jwt

app = FastAPI(title="User Management Service")
security = HTTPBearer()

@app.post("/auth/login")
async def login(credentials: LoginRequest):
    # Validar credenciales
    user = authenticate_user(credentials.email, credentials.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Generar JWT token
    token = create_access_token(data={"sub": user.email})
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users/profile")
async def get_profile(current_user: User = Depends(get_current_user)):
    return current_user

@app.put("/users/profile")
async def update_profile(
    profile: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    # Actualizar perfil del usuario
    updated_user = update_user_profile(current_user.id, profile)
    return updated_user
```

#### Marketing Automation API
```python
# marketing_service.py
from fastapi import FastAPI, BackgroundTasks
from celery import Celery

app = FastAPI(title="Marketing Automation Service")
celery_app = Celery('marketing', broker='redis://localhost:6379')

@app.post("/campaigns")
async def create_campaign(campaign: CampaignCreate):
    # Crear campaña
    campaign_id = create_campaign_db(campaign)
    
    # Programar tareas asíncronas
    celery_app.send_task('process_campaign', args=[campaign_id])
    
    return {"campaign_id": campaign_id, "status": "created"}

@app.get("/campaigns/{campaign_id}/status")
async def get_campaign_status(campaign_id: str):
    status = get_campaign_status_db(campaign_id)
    return {"campaign_id": campaign_id, "status": status}

@app.post("/automations")
async def create_automation(automation: AutomationCreate):
    automation_id = create_automation_db(automation)
    return {"automation_id": automation_id, "status": "created"}
```

#### Content Generation API
```python
# content_service.py
from fastapi import FastAPI, HTTPException
import openai
from transformers import pipeline

app = FastAPI(title="Content Generation Service")

# Inicializar modelos de IA
text_generator = pipeline("text-generation", model="gpt-3.5-turbo")
image_generator = pipeline("image-generation", model="DALL-E-2")

@app.post("/content/generate")
async def generate_content(request: ContentRequest):
    try:
        # Generar contenido basado en el tipo
        if request.type == "text":
            content = generate_text_content(request.prompt, request.parameters)
        elif request.type == "image":
            content = generate_image_content(request.prompt, request.parameters)
        else:
            raise HTTPException(status_code=400, detail="Invalid content type")
        
        return {"content": content, "type": request.type}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/content/bulk")
async def generate_bulk_content(request: BulkContentRequest):
    # Generar múltiples piezas de contenido
    results = []
    for item in request.items:
        content = generate_content_item(item)
        results.append(content)
    
    return {"results": results, "count": len(results)}
```

## Integración con IA

### Configuración de OpenAI

#### API Key Setup
```python
# config.py
import os
from openai import OpenAI

# Configurar API key
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    organization=os.getenv("OPENAI_ORG_ID")
)

# Configuración de modelos
MODEL_CONFIG = {
    "text_generation": "gpt-3.5-turbo",
    "text_completion": "text-davinci-003",
    "image_generation": "dall-e-2",
    "embedding": "text-embedding-ada-002"
}
```

#### Funciones de IA
```python
# ai_functions.py
import openai
from typing import List, Dict, Any

class AIService:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].text
    
    def generate_email(self, subject: str, audience: str) -> Dict[str, str]:
        prompt = f"Generate a marketing email with subject '{subject}' for {audience}"
        
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=500,
            temperature=0.8
        )
        
        return {
            "subject": subject,
            "body": response.choices[0].text,
            "audience": audience
        }
    
    def generate_social_post(self, platform: str, topic: str) -> str:
        prompt = f"Generate a {platform} post about {topic}"
        
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=200,
            temperature=0.9
        )
        
        return response.choices[0].text
    
    def analyze_sentiment(self, text: str) -> Dict[str, float]:
        prompt = f"Analyze the sentiment of this text: '{text}'. Return only a JSON with 'positive', 'negative', and 'neutral' scores."
        
        response = self.client.completions.create(
            model="gpt-3.5-turbo",
            prompt=prompt,
            max_tokens=100,
            temperature=0.3
        )
        
        return eval(response.choices[0].text)
```

### Machine Learning Pipeline

#### Data Preprocessing
```python
# ml_pipeline.py
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split

class DataPreprocessor:
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
    
    def preprocess_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Limpiar datos
        df = df.dropna()
        df = df.drop_duplicates()
        
        # Codificar variables categóricas
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            self.label_encoders[col] = le
        
        # Estandarizar variables numéricas
        numerical_columns = df.select_dtypes(include=[np.number]).columns
        df[numerical_columns] = self.scaler.fit_transform(df[numerical_columns])
        
        return df
    
    def split_data(self, df: pd.DataFrame, target_column: str, test_size: float = 0.2):
        X = df.drop(target_column, axis=1)
        y = df[target_column]
        
        return train_test_split(X, y, test_size=test_size, random_state=42)
```

#### Model Training
```python
# model_training.py
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import joblib

class ModelTrainer:
    def __init__(self):
        self.models = {}
        self.best_model = None
        self.best_score = 0
    
    def train_models(self, X_train, y_train, X_test, y_test):
        # Random Forest
        rf = RandomForestClassifier(n_estimators=100, random_state=42)
        rf.fit(X_train, y_train)
        rf_score = accuracy_score(y_test, rf.predict(X_test))
        self.models['random_forest'] = {'model': rf, 'score': rf_score}
        
        # Logistic Regression
        lr = LogisticRegression(random_state=42)
        lr.fit(X_train, y_train)
        lr_score = accuracy_score(y_test, lr.predict(X_test))
        self.models['logistic_regression'] = {'model': lr, 'score': lr_score}
        
        # Seleccionar mejor modelo
        for name, model_info in self.models.items():
            if model_info['score'] > self.best_score:
                self.best_score = model_info['score']
                self.best_model = model_info['model']
        
        return self.best_model
    
    def save_model(self, filepath: str):
        joblib.dump(self.best_model, filepath)
    
    def load_model(self, filepath: str):
        self.best_model = joblib.load(filepath)
```

## Configuración de Seguridad

### Autenticación y Autorización

#### JWT Implementation
```python
# auth.py
import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

security = HTTPBearer()

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(token: str = Depends(security)):
    payload = verify_token(token.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id
```

#### Rate Limiting
```python
# rate_limiting.py
from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/content/generate")
@limiter.limit("10/minute")
async def generate_content(request: Request, content_request: ContentRequest):
    # Generar contenido
    pass
```

### Encriptación de Datos

#### Database Encryption
```python
# encryption.py
from cryptography.fernet import Fernet
import base64
import os

class DataEncryption:
    def __init__(self):
        self.key = os.getenv("ENCRYPTION_KEY")
        if not self.key:
            self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
    
    def encrypt_data(self, data: str) -> str:
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(decoded_data)
        return decrypted_data.decode()
```

## Monitoreo y Logging

### Application Monitoring

#### Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'marketing-ai'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
    scrape_interval: 5s
```

#### Grafana Dashboard
```json
{
  "dashboard": {
    "title": "Marketing AI Dashboard",
    "panels": [
      {
        "title": "API Requests",
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
      }
    ]
  }
}
```

### Logging Configuration

#### ELK Stack Setup
```yaml
# docker-compose.yml
version: '3.8'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.15.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  
  logstash:
    image: docker.elastic.co/logstash/logstash:7.15.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
  
  kibana:
    image: docker.elastic.co/kibana/kibana:7.15.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

#### Logstash Configuration
```ruby
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  if [fields][service] == "marketing-ai" {
    grok {
      match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:level} %{DATA:service} %{GREEDYDATA:message}" }
    }
    
    date {
      match => [ "timestamp", "ISO8601" ]
    }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "marketing-ai-%{+YYYY.MM.dd}"
  }
}
```

## Deployment

### Docker Configuration

#### Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:password@db:5432/marketing_ai
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=marketing_ai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - api

volumes:
  postgres_data:
```

### Kubernetes Deployment

#### Deployment YAML
```yaml
# k8s-deployment.yml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: marketing-ai-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: marketing-ai-api
  template:
    metadata:
      labels:
        app: marketing-ai-api
    spec:
      containers:
      - name: api
        image: marketing-ai:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: marketing-ai-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
```

#### Service YAML
```yaml
# k8s-service.yml
apiVersion: v1
kind: Service
metadata:
  name: marketing-ai-service
spec:
  selector:
    app: marketing-ai-api
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Testing

### Unit Testing

#### Test Configuration
```python
# test_config.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

@pytest.fixture
def client():
    from main import app
    return TestClient(app)

@pytest.fixture
def mock_ai_service():
    with patch('services.ai_service.AIService') as mock:
        yield mock
```

#### Test Examples
```python
# test_api.py
import pytest
from fastapi.testclient import TestClient

def test_login_success(client: TestClient):
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_generate_content(client: TestClient, mock_ai_service):
    mock_ai_service.return_value.generate_text.return_value = "Generated content"
    
    response = client.post("/content/generate", json={
        "type": "text",
        "prompt": "Write a marketing email",
        "parameters": {}
    })
    
    assert response.status_code == 200
    assert response.json()["content"] == "Generated content"

def test_campaign_creation(client: TestClient):
    response = client.post("/campaigns", json={
        "name": "Test Campaign",
        "type": "email",
        "target_audience": "all_users"
    })
    
    assert response.status_code == 201
    assert "campaign_id" in response.json()
```

### Integration Testing

#### Database Testing
```python
# test_database.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Campaign

@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()

def test_user_creation(db_session):
    user = User(email="test@example.com", name="Test User")
    db_session.add(user)
    db_session.commit()
    
    assert user.id is not None
    assert user.email == "test@example.com"
```

### Performance Testing

#### Load Testing con Locust
```python
# locustfile.py
from locust import HttpUser, task, between

class MarketingAIUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        self.token = response.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def generate_content(self):
        self.client.post("/content/generate", 
                        json={"type": "text", "prompt": "Test prompt"},
                        headers=self.headers)
    
    @task(1)
    def get_campaigns(self):
        self.client.get("/campaigns", headers=self.headers)
```

## Mantenimiento y Actualizaciones

### CI/CD Pipeline

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-test.txt
    
    - name: Run tests
      run: pytest tests/ --cov=app --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
    - name: Deploy to production
      run: |
        # Deploy commands
        kubectl apply -f k8s/
```

### Database Migrations

#### Alembic Configuration
```python
# alembic.ini
[alembic]
script_location = alembic
sqlalchemy.url = postgresql://user:password@localhost/marketing_ai

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
```

#### Migration Example
```python
# alembic/versions/001_add_campaign_table.py
"""Add campaign table

Revision ID: 001
Revises: 
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table('campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('status', sa.String(20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_table('campaigns')
```

## Troubleshooting

### Problemas Comunes

#### Database Connection Issues
```python
# database_troubleshooting.py
import psycopg2
from sqlalchemy import create_engine
import logging

def test_database_connection():
    try:
        # Test direct connection
        conn = psycopg2.connect(
            host="localhost",
            database="marketing_ai",
            user="user",
            password="password"
        )
        conn.close()
        print("Database connection successful")
    except Exception as e:
        print(f"Database connection failed: {e}")
    
    try:
        # Test SQLAlchemy connection
        engine = create_engine("postgresql://user:password@localhost/marketing_ai")
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("SQLAlchemy connection successful")
    except Exception as e:
        print(f"SQLAlchemy connection failed: {e}")
```

#### API Performance Issues
```python
# performance_troubleshooting.py
import time
import requests
from concurrent.futures import ThreadPoolExecutor

def test_api_performance():
    base_url = "http://localhost:8000"
    
    def make_request():
        start_time = time.time()
        response = requests.get(f"{base_url}/health")
        end_time = time.time()
        return end_time - start_time, response.status_code
    
    # Test single request
    response_time, status_code = make_request()
    print(f"Single request: {response_time:.2f}s, Status: {status_code}")
    
    # Test concurrent requests
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(make_request) for _ in range(100)]
        results = [future.result() for future in futures]
    
    avg_response_time = sum(r[0] for r in results) / len(results)
    success_rate = sum(1 for r in results if r[1] == 200) / len(results)
    
    print(f"Concurrent requests: {avg_response_time:.2f}s avg, {success_rate:.2%} success rate")
```

## Recursos Adicionales

### Documentación Técnica
- **API Documentation**: Swagger UI disponible en `/docs`
- **Database Schema**: Diagramas de base de datos
- **Architecture Diagrams**: Diagramas de arquitectura
- **Deployment Guides**: Guías de despliegue

### Herramientas de Desarrollo
- **Postman Collection**: Colección de APIs para testing
- **Docker Images**: Imágenes Docker pre-construidas
- **Kubernetes Manifests**: Manifiestos K8s listos para usar
- **Monitoring Dashboards**: Dashboards de Grafana

### Soporte Técnico
- **Technical Support**: soporte-tecnico@ia-marketing.com
- **Documentation Portal**: docs.ia-marketing.com
- **Community Forum**: community.ia-marketing.com
- **GitHub Repository**: github.com/ia-marketing/api

---

**¿Necesitas ayuda técnica?** [Contacta a nuestro equipo de desarrollo]

*Implementación técnica robusta y escalable para tu éxito.*


