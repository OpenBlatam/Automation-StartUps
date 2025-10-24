# 🛠️ Guía de Desarrollador - FRONTIER

> **Documentación técnica completa para desarrolladores que quieren integrar, extender o contribuir a la plataforma FRONTIER**

## 📋 Tabla de Contenidos

- [🎯 Introducción](#-introducción)
- [🏗️ Arquitectura del Sistema](#️-arquitectura-del-sistema)
- [🚀 Configuración del Entorno](#-configuración-del-entorno)
- [🔌 APIs y Endpoints](#-apis-y-endpoints)
- [🤖 Integración con IA](#-integración-con-ia)
- [📊 Base de Datos](#-base-de-datos)
- [🔒 Seguridad](#-seguridad)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [📚 SDKs y Librerías](#-sdks-y-librerías)

## 🎯 Introducción

Esta guía está diseñada para desarrolladores que quieren:

- **Integrar** FRONTIER en aplicaciones existentes
- **Extender** la funcionalidad de la plataforma
- **Contribuir** al código open source
- **Desarrollar** aplicaciones que consuman nuestros APIs

### 🎪 Tecnologías Principales

- **Backend**: Node.js, Python, Go
- **Frontend**: React, Vue.js, Angular
- **Base de Datos**: PostgreSQL, MongoDB, Redis
- **IA**: TensorFlow, PyTorch, OpenAI GPT
- **Cloud**: AWS, Google Cloud, Azure
- **Containers**: Docker, Kubernetes

## 🏗️ Arquitectura del Sistema

### Diagrama de Arquitectura

```mermaid
graph TB
    subgraph "Frontend Layer"
        A[Web App] --> B[Mobile App]
        B --> C[Admin Dashboard]
    end
    
    subgraph "API Gateway"
        D[Load Balancer] --> E[API Gateway]
        E --> F[Rate Limiting]
        F --> G[Authentication]
    end
    
    subgraph "Microservices"
        H[User Service] --> I[Campaign Service]
        I --> J[AI Service]
        J --> K[Analytics Service]
        K --> L[Notification Service]
    end
    
    subgraph "Data Layer"
        M[PostgreSQL] --> N[MongoDB]
        N --> O[Redis Cache]
        O --> P[Elasticsearch]
    end
    
    subgraph "External Services"
        Q[OpenAI API] --> R[Canva API]
        R --> S[Social Media APIs]
        S --> T[Email Services]
    end
    
    A --> D
    B --> D
    C --> D
    E --> H
    E --> I
    E --> J
    E --> K
    E --> L
    H --> M
    I --> N
    J --> O
    K --> P
    J --> Q
    I --> R
    L --> S
    L --> T
```

### Componentes Principales

#### 1. API Gateway
- **Función**: Punto de entrada único para todas las APIs
- **Tecnología**: Kong, AWS API Gateway
- **Características**: Rate limiting, authentication, logging

#### 2. Microservices
- **User Service**: Gestión de usuarios y autenticación
- **Campaign Service**: Gestión de campañas de marketing
- **AI Service**: Procesamiento de IA y ML
- **Analytics Service**: Análisis de datos y reportes
- **Notification Service**: Notificaciones y alertas

#### 3. Data Layer
- **PostgreSQL**: Datos transaccionales
- **MongoDB**: Datos no estructurados
- **Redis**: Cache y sesiones
- **Elasticsearch**: Búsqueda y analytics

## 🚀 Configuración del Entorno

### Prerrequisitos

```bash
# Software requerido
- Node.js 18+ o Python 3.9+
- Docker y Docker Compose
- PostgreSQL 14+
- Redis 6+
- Git

# Herramientas recomendadas
- VS Code con extensiones
- Postman para testing de APIs
- DBeaver para gestión de BD
- RedisInsight para Redis
```

### Instalación Local

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/frontier-ai/frontier.git
cd frontier
```

#### 2. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp .env.example .env

# Editar variables
nano .env
```

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/frontier
REDIS_URL=redis://localhost:6379

# APIs
OPENAI_API_KEY=your_openai_key
CANVA_API_KEY=your_canva_key
FACEBOOK_APP_ID=your_facebook_id
FACEBOOK_APP_SECRET=your_facebook_secret

# JWT
JWT_SECRET=your_jwt_secret
JWT_EXPIRES_IN=7d

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASS=your_password

# Storage
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
AWS_S3_BUCKET=frontier-storage
```

#### 3. Instalar Dependencias
```bash
# Backend (Node.js)
cd backend
npm install

# Frontend
cd ../frontend
npm install

# Python services
cd ../ai-services
pip install -r requirements.txt
```

#### 4. Configurar Base de Datos
```bash
# Iniciar servicios con Docker
docker-compose up -d postgres redis

# Ejecutar migraciones
npm run migrate

# Seed inicial
npm run seed
```

#### 5. Iniciar Servicios
```bash
# Backend
cd backend
npm run dev

# Frontend
cd frontend
npm run dev

# AI Services
cd ai-services
python app.py
```

### Docker Development

#### 1. Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: frontier
      POSTGRES_USER: frontier
      POSTGRES_PASSWORD: frontier
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  backend:
    build: ./backend
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://frontier:frontier@postgres:5432/frontier
      - REDIS_URL=redis://redis:6379
    depends_on:
      - postgres
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3001:3001"
    depends_on:
      - backend

volumes:
  postgres_data:
```

#### 2. Comandos Docker
```bash
# Construir y ejecutar
docker-compose up --build

# Solo servicios de base de datos
docker-compose up postgres redis

# Logs
docker-compose logs -f backend

# Ejecutar comandos
docker-compose exec backend npm run migrate
```

## 🔌 APIs y Endpoints

### Autenticación

#### 1. Registro de Usuario
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "name": "John Doe",
  "company": "Acme Corp"
}
```

#### 2. Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

#### 3. Refresh Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

### Gestión de Campañas

#### 1. Crear Campaña
```http
POST /api/v1/campaigns
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Summer Sale Campaign",
  "type": "social_media",
  "platforms": ["facebook", "instagram"],
  "budget": 1000,
  "start_date": "2024-06-01",
  "end_date": "2024-08-31",
  "target_audience": {
    "age_range": [25, 45],
    "interests": ["fashion", "lifestyle"],
    "locations": ["US", "CA"]
  }
}
```

#### 2. Listar Campañas
```http
GET /api/v1/campaigns?page=1&limit=10&status=active
Authorization: Bearer <access_token>
```

#### 3. Obtener Campaña
```http
GET /api/v1/campaigns/{campaign_id}
Authorization: Bearer <access_token>
```

#### 4. Actualizar Campaña
```http
PUT /api/v1/campaigns/{campaign_id}
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Updated Campaign Name",
  "budget": 1500
}
```

### IA y Machine Learning

#### 1. Generar Contenido
```http
POST /api/v1/ai/generate-content
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "type": "social_media_post",
  "topic": "summer fashion",
  "tone": "casual",
  "platform": "instagram",
  "target_audience": "fashion enthusiasts"
}
```

#### 2. Análisis de Sentimientos
```http
POST /api/v1/ai/sentiment-analysis
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "I love this new product! It's amazing!",
  "language": "en"
}
```

#### 3. Optimización de Imágenes
```http
POST /api/v1/ai/optimize-image
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

{
  "image": <file>,
  "optimization_type": "social_media",
  "platform": "instagram",
  "format": "square"
}
```

### Analytics

#### 1. Métricas de Campaña
```http
GET /api/v1/analytics/campaigns/{campaign_id}/metrics
Authorization: Bearer <access_token>
```

#### 2. Reportes Personalizados
```http
POST /api/v1/analytics/reports
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "name": "Monthly Performance Report",
  "date_range": {
    "start": "2024-01-01",
    "end": "2024-01-31"
  },
  "metrics": ["impressions", "clicks", "conversions"],
  "group_by": ["campaign", "platform"]
}
```

## 🤖 Integración con IA

### OpenAI Integration

#### 1. Configuración
```javascript
const OpenAI = require('openai');

const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// Generar contenido
async function generateContent(prompt, options = {}) {
  const response = await openai.chat.completions.create({
    model: "gpt-4",
    messages: [
      {
        role: "system",
        content: "You are a professional marketing content creator."
      },
      {
        role: "user",
        content: prompt
      }
    ],
    max_tokens: options.maxTokens || 500,
    temperature: options.temperature || 0.7,
  });

  return response.choices[0].message.content;
}
```

#### 2. Funciones Especializadas
```javascript
// Generar posts para redes sociales
async function generateSocialMediaPost(topic, platform, tone) {
  const prompt = `Create a ${tone} social media post about ${topic} for ${platform}. 
  Include relevant hashtags and a call-to-action.`;
  
  return await generateContent(prompt);
}

// Generar emails de marketing
async function generateEmailSubject(emailType, product) {
  const prompt = `Create a compelling email subject line for a ${emailType} email about ${product}. 
  Make it engaging and click-worthy.`;
  
  return await generateContent(prompt, { maxTokens: 100 });
}
```

### Machine Learning Models

#### 1. Modelo de Predicción de Conversión
```python
import tensorflow as tf
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

class ConversionPredictor:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100)
        self.is_trained = False
    
    def train(self, X, y):
        """Entrenar el modelo con datos históricos"""
        self.model.fit(X, y)
        self.is_trained = True
    
    def predict(self, features):
        """Predecir probabilidad de conversión"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        probability = self.model.predict_proba([features])[0][1]
        return probability
    
    def get_feature_importance(self):
        """Obtener importancia de características"""
        if not self.is_trained:
            raise ValueError("Model must be trained first")
        
        return dict(zip(
            self.model.feature_names_in_,
            self.model.feature_importances_
        ))
```

#### 2. Análisis de Sentimientos
```python
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        self.analyzer = pipeline(
            "sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment-latest"
        )
    
    def analyze(self, text):
        """Analizar sentimiento del texto"""
        result = self.analyzer(text)
        return {
            'sentiment': result[0]['label'],
            'confidence': result[0]['score']
        }
    
    def batch_analyze(self, texts):
        """Analizar múltiples textos"""
        results = self.analyzer(texts)
        return [
            {
                'text': text,
                'sentiment': result['label'],
                'confidence': result['score']
            }
            for text, result in zip(texts, results)
        ]
```

## 📊 Base de Datos

### Esquema de Base de Datos

#### 1. Usuarios
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_company ON users(company);
```

#### 2. Campañas
```sql
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'draft',
    budget DECIMAL(10,2),
    start_date DATE,
    end_date DATE,
    target_audience JSONB,
    settings JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_campaigns_user_id ON campaigns(user_id);
CREATE INDEX idx_campaigns_status ON campaigns(status);
CREATE INDEX idx_campaigns_dates ON campaigns(start_date, end_date);
```

#### 3. Métricas
```sql
CREATE TABLE metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES campaigns(id) ON DELETE CASCADE,
    metric_type VARCHAR(50) NOT NULL,
    value DECIMAL(15,4) NOT NULL,
    date DATE NOT NULL,
    platform VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_metrics_campaign_id ON metrics(campaign_id);
CREATE INDEX idx_metrics_date ON metrics(date);
CREATE INDEX idx_metrics_type ON metrics(metric_type);
```

### Migraciones

#### 1. Crear Migración
```bash
# Usando Knex.js
npx knex migrate:make create_users_table

# Usando Sequelize
npx sequelize-cli migration:generate --name create-users-table
```

#### 2. Ejemplo de Migración
```javascript
// migrations/20240101000000_create_users_table.js
exports.up = function(knex) {
  return knex.schema.createTable('users', function(table) {
    table.uuid('id').primary().defaultTo(knex.raw('gen_random_uuid()'));
    table.string('email', 255).unique().notNullable();
    table.string('password_hash', 255).notNullable();
    table.string('name', 255).notNullable();
    table.string('company', 255);
    table.string('role', 50).defaultTo('user');
    table.timestamps(true, true);
    
    table.index('email');
    table.index('company');
  });
};

exports.down = function(knex) {
  return knex.schema.dropTable('users');
};
```

## 🔒 Seguridad

### Autenticación y Autorización

#### 1. JWT Implementation
```javascript
const jwt = require('jsonwebtoken');
const bcrypt = require('bcrypt');

class AuthService {
  constructor() {
    this.secret = process.env.JWT_SECRET;
    this.expiresIn = process.env.JWT_EXPIRES_IN || '7d';
  }

  async generateTokens(user) {
    const payload = {
      id: user.id,
      email: user.email,
      role: user.role
    };

    const accessToken = jwt.sign(payload, this.secret, {
      expiresIn: '15m'
    });

    const refreshToken = jwt.sign(payload, this.secret, {
      expiresIn: this.expiresIn
    });

    return { accessToken, refreshToken };
  }

  async verifyToken(token) {
    try {
      return jwt.verify(token, this.secret);
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  async hashPassword(password) {
    const saltRounds = 12;
    return await bcrypt.hash(password, saltRounds);
  }

  async comparePassword(password, hash) {
    return await bcrypt.compare(password, hash);
  }
}
```

#### 2. Middleware de Autenticación
```javascript
const authMiddleware = async (req, res, next) => {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');
    
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }

    const decoded = await authService.verifyToken(token);
    req.user = decoded;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Middleware de autorización por roles
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    next();
  };
};
```

### Rate Limiting

#### 1. Implementación con Redis
```javascript
const redis = require('redis');
const client = redis.createClient(process.env.REDIS_URL);

class RateLimiter {
  constructor() {
    this.client = client;
  }

  async checkLimit(key, limit, window) {
    const current = await this.client.incr(key);
    
    if (current === 1) {
      await this.client.expire(key, window);
    }
    
    if (current > limit) {
      return false;
    }
    
    return true;
  }

  async getRemainingRequests(key, limit) {
    const current = await this.client.get(key);
    return Math.max(0, limit - (current || 0));
  }
}

// Middleware de rate limiting
const rateLimitMiddleware = (limit, window) => {
  const rateLimiter = new RateLimiter();
  
  return async (req, res, next) => {
    const key = `rate_limit:${req.ip}:${req.route.path}`;
    const allowed = await rateLimiter.checkLimit(key, limit, window);
    
    if (!allowed) {
      return res.status(429).json({
        error: 'Too many requests',
        retryAfter: window
      });
    }
    
    next();
  };
};
```

## 🧪 Testing

### Configuración de Testing

#### 1. Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  testMatch: ['**/__tests__/**/*.test.js'],
  collectCoverageFrom: [
    'src/**/*.js',
    '!src/**/*.test.js',
    '!src/migrations/**',
    '!src/seeders/**'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

#### 2. Test Setup
```javascript
// tests/setup.js
const { setupTestDatabase, teardownTestDatabase } = require('./helpers/database');

beforeAll(async () => {
  await setupTestDatabase();
});

afterAll(async () => {
  await teardownTestDatabase();
});

beforeEach(async () => {
  // Limpiar datos entre tests
  await clearTestData();
});
```

### Unit Tests

#### 1. Test de Servicios
```javascript
// tests/services/auth.test.js
const AuthService = require('../../src/services/AuthService');
const User = require('../../src/models/User');

describe('AuthService', () => {
  let authService;
  
  beforeEach(() => {
    authService = new AuthService();
  });

  describe('generateTokens', () => {
    it('should generate valid tokens', async () => {
      const user = { id: 1, email: 'test@example.com', role: 'user' };
      const tokens = await authService.generateTokens(user);
      
      expect(tokens).toHaveProperty('accessToken');
      expect(tokens).toHaveProperty('refreshToken');
      expect(typeof tokens.accessToken).toBe('string');
      expect(typeof tokens.refreshToken).toBe('string');
    });
  });

  describe('verifyToken', () => {
    it('should verify valid token', async () => {
      const user = { id: 1, email: 'test@example.com', role: 'user' };
      const { accessToken } = await authService.generateTokens(user);
      
      const decoded = await authService.verifyToken(accessToken);
      expect(decoded.id).toBe(user.id);
      expect(decoded.email).toBe(user.email);
    });

    it('should throw error for invalid token', async () => {
      await expect(authService.verifyToken('invalid-token'))
        .rejects.toThrow('Invalid token');
    });
  });
});
```

#### 2. Test de APIs
```javascript
// tests/api/campaigns.test.js
const request = require('supertest');
const app = require('../../src/app');
const { createTestUser, createTestCampaign } = require('../helpers/factory');

describe('Campaigns API', () => {
  let user;
  let authToken;

  beforeEach(async () => {
    user = await createTestUser();
    const response = await request(app)
      .post('/api/v1/auth/login')
      .send({
        email: user.email,
        password: 'testpassword'
      });
    
    authToken = response.body.accessToken;
  });

  describe('POST /api/v1/campaigns', () => {
    it('should create a new campaign', async () => {
      const campaignData = {
        name: 'Test Campaign',
        type: 'social_media',
        platforms: ['facebook', 'instagram'],
        budget: 1000
      };

      const response = await request(app)
        .post('/api/v1/campaigns')
        .set('Authorization', `Bearer ${authToken}`)
        .send(campaignData)
        .expect(201);

      expect(response.body).toHaveProperty('id');
      expect(response.body.name).toBe(campaignData.name);
      expect(response.body.user_id).toBe(user.id);
    });

    it('should require authentication', async () => {
      const response = await request(app)
        .post('/api/v1/campaigns')
        .send({ name: 'Test Campaign' })
        .expect(401);

      expect(response.body).toHaveProperty('error');
    });
  });
});
```

### Integration Tests

#### 1. Database Tests
```javascript
// tests/integration/database.test.js
const { setupTestDatabase, teardownTestDatabase } = require('../helpers/database');
const User = require('../../src/models/User');
const Campaign = require('../../src/models/Campaign');

describe('Database Integration', () => {
  beforeAll(async () => {
    await setupTestDatabase();
  });

  afterAll(async () => {
    await teardownTestDatabase();
  });

  describe('User-Campaign Relationship', () => {
    it('should create user with campaigns', async () => {
      const user = await User.create({
        email: 'test@example.com',
        password_hash: 'hashedpassword',
        name: 'Test User'
      });

      const campaign = await Campaign.create({
        user_id: user.id,
        name: 'Test Campaign',
        type: 'social_media',
        budget: 1000
      });

      const userWithCampaigns = await User.findByPk(user.id, {
        include: [Campaign]
      });

      expect(userWithCampaigns.campaigns).toHaveLength(1);
      expect(userWithCampaigns.campaigns[0].name).toBe('Test Campaign');
    });
  });
});
```

## 🚀 Deployment

### Docker Production

#### 1. Dockerfile Backend
```dockerfile
# backend/Dockerfile
FROM node:18-alpine

WORKDIR /app

# Copiar package files
COPY package*.json ./

# Instalar dependencias
RUN npm ci --only=production

# Copiar código fuente
COPY . .

# Construir aplicación
RUN npm run build

# Exponer puerto
EXPOSE 3000

# Comando de inicio
CMD ["npm", "start"]
```

#### 2. Docker Compose Production
```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: ${DATABASE_NAME}
      POSTGRES_USER: ${DATABASE_USER}
      POSTGRES_PASSWORD: ${DATABASE_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

  backend:
    build: ./backend
    environment:
      - NODE_ENV=production
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=${API_URL}
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

### Kubernetes Deployment

#### 1. Deployment Backend
```yaml
# k8s/backend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontier-backend
  labels:
    app: frontier-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontier-backend
  template:
    metadata:
      labels:
        app: frontier-backend
    spec:
      containers:
      - name: backend
        image: frontier/backend:latest
        ports:
        - containerPort: 3000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: frontier-secrets
              key: database-url
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: frontier-secrets
              key: redis-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
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

#### 2. Service
```yaml
# k8s/backend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: frontier-backend-service
spec:
  selector:
    app: frontier-backend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
  type: ClusterIP
```

### CI/CD Pipeline

#### 1. GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
        cache: 'npm'
    
    - name: Install dependencies
      run: npm ci
    
    - name: Run tests
      run: npm test
    
    - name: Run linting
      run: npm run lint

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Build Docker image
      run: docker build -t frontier/backend:${{ github.sha }} ./backend
    
    - name: Push to registry
      run: |
        echo ${{ secrets.DOCKER_PASSWORD }} | docker login -u ${{ secrets.DOCKER_USERNAME }} --password-stdin
        docker push frontier/backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
    - name: Deploy to Kubernetes
      run: |
        kubectl set image deployment/frontier-backend backend=frontier/backend:${{ github.sha }}
        kubectl rollout status deployment/frontier-backend
```

## 📚 SDKs y Librerías

### JavaScript SDK

#### 1. Instalación
```bash
npm install @frontier-ai/sdk
```

#### 2. Uso Básico
```javascript
const Frontier = require('@frontier-ai/sdk');

const client = new Frontier({
  apiKey: 'your-api-key',
  baseURL: 'https://api.frontier-ai.com'
});

// Crear campaña
const campaign = await client.campaigns.create({
  name: 'My Campaign',
  type: 'social_media',
  platforms: ['facebook', 'instagram'],
  budget: 1000
});

// Generar contenido
const content = await client.ai.generateContent({
  type: 'social_media_post',
  topic: 'summer fashion',
  platform: 'instagram'
});

// Obtener métricas
const metrics = await client.analytics.getMetrics(campaign.id);
```

### Python SDK

#### 1. Instalación
```bash
pip install frontier-ai
```

#### 2. Uso Básico
```python
from frontier_ai import FrontierClient

client = FrontierClient(
    api_key='your-api-key',
    base_url='https://api.frontier-ai.com'
)

# Crear campaña
campaign = client.campaigns.create({
    'name': 'My Campaign',
    'type': 'social_media',
    'platforms': ['facebook', 'instagram'],
    'budget': 1000
})

# Generar contenido
content = client.ai.generate_content(
    type='social_media_post',
    topic='summer fashion',
    platform='instagram'
)

# Obtener métricas
metrics = client.analytics.get_metrics(campaign['id'])
```

### React Components

#### 1. Instalación
```bash
npm install @frontier-ai/react-components
```

#### 2. Uso
```jsx
import React from 'react';
import { CampaignDashboard, ContentGenerator, AnalyticsChart } from '@frontier-ai/react-components';

function App() {
  return (
    <div>
      <CampaignDashboard 
        apiKey="your-api-key"
        onCampaignSelect={(campaign) => console.log(campaign)}
      />
      
      <ContentGenerator
        type="social_media_post"
        onGenerate={(content) => console.log(content)}
      />
      
      <AnalyticsChart
        campaignId="campaign-id"
        metrics={['impressions', 'clicks', 'conversions']}
      />
    </div>
  );
}
```

---

<div align="center">

**🛠️ ¿Listo para desarrollar con FRONTIER?**

[Ver Documentación Completa](https://docs.frontier-ai.com) | [GitHub Repository](https://github.com/frontier-ai/frontier) | [Discord Community](https://discord.gg/frontier-ai)

</div>









