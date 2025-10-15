# 🔧 Guía Técnica: Implementación de AI Email Re-engagement

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico Recomendado

**Backend:**
- **Python 3.9+** con FastAPI
- **PostgreSQL** para datos estructurados
- **Redis** para cache y sesiones
- **Celery** para tareas asíncronas
- **Docker** para containerización

**AI/ML:**
- **OpenAI GPT-4** para generación de contenido
- **scikit-learn** para segmentación
- **pandas/numpy** para análisis de datos
- **TensorFlow/PyTorch** para modelos custom

**Frontend:**
- **React 18** con TypeScript
- **Material-UI** para componentes
- **Chart.js** para visualizaciones
- **WebSocket** para updates en tiempo real

**Infraestructura:**
- **AWS/GCP** para cloud hosting
- **Kubernetes** para orquestación
- **Terraform** para infraestructura como código
- **GitHub Actions** para CI/CD

---

## 📊 Modelo de Datos

### Esquema de Base de Datos

```sql
-- Tabla de clientes
CREATE TABLE customers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    last_purchase_date TIMESTAMP,
    total_spent DECIMAL(10,2) DEFAULT 0,
    purchase_count INTEGER DEFAULT 0,
    segment VARCHAR(50),
    churn_probability DECIMAL(3,2),
    preferred_categories TEXT[],
    timezone VARCHAR(50),
    status VARCHAR(20) DEFAULT 'active'
);

-- Tabla de productos
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10,2),
    description TEXT,
    image_url VARCHAR(500),
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de compras
CREATE TABLE purchases (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    product_id UUID REFERENCES products(id),
    quantity INTEGER DEFAULT 1,
    price DECIMAL(10,2),
    purchase_date TIMESTAMP DEFAULT NOW(),
    order_id VARCHAR(100)
);

-- Tabla de campañas
CREATE TABLE campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    segment VARCHAR(50),
    template_id UUID,
    status VARCHAR(20) DEFAULT 'draft',
    scheduled_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    created_by UUID
);

-- Tabla de emails enviados
CREATE TABLE email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    customer_id UUID REFERENCES customers(id),
    campaign_id UUID REFERENCES campaigns(id),
    subject VARCHAR(255),
    sent_at TIMESTAMP DEFAULT NOW(),
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    converted_at TIMESTAMP,
    bounce_reason VARCHAR(100)
);
```

---

## 🤖 Implementación de IA

### Clase Principal del Sistema

```python
import openai
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import numpy as np
from datetime import datetime, timedelta
import asyncio
import aiohttp

class AIEmailReengagement:
    def __init__(self, openai_api_key: str, db_connection: str):
        self.openai_client = openai.OpenAI(api_key=openai_api_key)
        self.db = self._connect_db(db_connection)
        self.segmentation_model = None
        self.churn_model = None
        
    async def segment_customers(self, customer_data: pd.DataFrame) -> dict:
        """Segmenta clientes usando clustering"""
        # Preparar datos para clustering
        features = ['total_spent', 'purchase_count', 'days_since_last_purchase']
        X = customer_data[features].fillna(0)
        
        # Normalizar datos
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Aplicar K-means clustering
        kmeans = KMeans(n_clusters=4, random_state=42)
        clusters = kmeans.fit_predict(X_scaled)
        
        # Asignar segmentos basados en clusters
        segments = {
            0: 'high_value_inactive',
            1: 'frequent_buyer_pause', 
            2: 'seasonal_customer',
            3: 'price_sensitive'
        }
        
        customer_data['segment'] = [segments[cluster] for cluster in clusters]
        return customer_data
    
    async def predict_churn(self, customer_data: pd.DataFrame) -> pd.DataFrame:
        """Predice probabilidad de churn usando ML"""
        # Features para predicción de churn
        features = [
            'days_since_last_purchase',
            'purchase_frequency',
            'avg_order_value',
            'total_spent',
            'email_engagement_score'
        ]
        
        # Entrenar modelo (simplificado)
        from sklearn.ensemble import RandomForestClassifier
        
        # Datos históricos para entrenamiento
        historical_data = self._get_historical_churn_data()
        
        X_train = historical_data[features]
        y_train = historical_data['churned']
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Predecir churn para clientes actuales
        X_current = customer_data[features].fillna(0)
        churn_probability = model.predict_proba(X_current)[:, 1]
        
        customer_data['churn_probability'] = churn_probability
        return customer_data
    
    async def generate_email_content(self, customer: dict, segment: str) -> dict:
        """Genera contenido de email usando GPT-4"""
        
        # Contexto del cliente
        customer_context = f"""
        Cliente: {customer['first_name']} {customer['last_name']}
        Email: {customer['email']}
        Última compra: {customer['last_purchase_date']}
        Total gastado: ${customer['total_spent']}
        Segmento: {segment}
        Probabilidad de churn: {customer['churn_probability']:.2f}
        """
        
        # Prompt para GPT-4
        prompt = f"""
        Eres un experto en marketing de re-engagement. 
        Genera un email personalizado para re-enganchar a este cliente:
        
        {customer_context}
        
        Requisitos:
        1. Tono apropiado para el segmento {segment}
        2. Oferta relevante basada en historial
        3. Urgencia apropiada
        4. Llamada a la acción clara
        5. Personalización genuina
        
        Formato de respuesta JSON:
        {{
            "subject": "Línea de asunto optimizada",
            "greeting": "Saludo personalizado",
            "body": "Cuerpo del email",
            "offer": "Oferta específica",
            "cta": "Llamada a la acción",
            "urgency": "Elemento de urgencia"
        }}
        """
        
        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "Eres un experto en marketing de re-engagement."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            return self._parse_json_response(content)
            
        except Exception as e:
            print(f"Error generando contenido: {e}")
            return self._get_fallback_template(segment)
    
    async def optimize_send_time(self, customer: dict) -> datetime:
        """Optimiza horario de envío basado en comportamiento histórico"""
        
        # Obtener historial de engagement por hora
        engagement_history = await self._get_engagement_by_hour(customer['id'])
        
        if engagement_history:
            # Encontrar hora con mayor engagement
            best_hour = max(engagement_history, key=engagement_history.get)
            
            # Ajustar por zona horaria del cliente
            customer_timezone = customer.get('timezone', 'UTC')
            optimal_time = datetime.now().replace(
                hour=best_hour, 
                minute=0, 
                second=0
            )
            
            return optimal_time
        else:
            # Horario por defecto basado en estudios
            default_hours = {
                'high_value_inactive': 10,  # 10 AM
                'frequent_buyer_pause': 14,  # 2 PM
                'seasonal_customer': 9,      # 9 AM
                'price_sensitive': 16        # 4 PM
            }
            
            segment = customer.get('segment', 'high_value_inactive')
            hour = default_hours.get(segment, 10)
            
            return datetime.now().replace(hour=hour, minute=0, second=0)
    
    async def execute_campaign(self, campaign_id: str) -> dict:
        """Ejecuta una campaña de re-engagement"""
        
        # Obtener detalles de la campaña
        campaign = await self._get_campaign(campaign_id)
        
        # Obtener clientes del segmento
        customers = await self._get_customers_by_segment(campaign['segment'])
        
        results = {
            'total_customers': len(customers),
            'emails_sent': 0,
            'emails_failed': 0,
            'errors': []
        }
        
        # Procesar cada cliente
        for customer in customers:
            try:
                # Generar contenido personalizado
                email_content = await self.generate_email_content(customer, campaign['segment'])
                
                # Optimizar horario de envío
                send_time = await self.optimize_send_time(customer)
                
                # Enviar email
                await self._send_email(customer, email_content, send_time)
                
                # Registrar en log
                await self._log_email_sent(customer['id'], campaign_id, email_content)
                
                results['emails_sent'] += 1
                
            except Exception as e:
                results['emails_failed'] += 1
                results['errors'].append(f"Cliente {customer['id']}: {str(e)}")
        
        return results
    
    def _parse_json_response(self, content: str) -> dict:
        """Parsea respuesta JSON de GPT-4"""
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Fallback si no es JSON válido
            return {
                "subject": "Te extrañamos - Oferta especial",
                "greeting": "Hola",
                "body": content,
                "offer": "20% de descuento",
                "cta": "Ver ofertas",
                "urgency": "Oferta limitada"
            }
    
    def _get_fallback_template(self, segment: str) -> dict:
        """Template de fallback si falla la generación de IA"""
        templates = {
            'high_value_inactive': {
                "subject": "Oferta exclusiva VIP",
                "greeting": "Estimado cliente VIP",
                "body": "Tenemos una oferta especial para ti...",
                "offer": "30% de descuento",
                "cta": "Aprovechar oferta",
                "urgency": "Válido por 72 horas"
            },
            'frequent_buyer_pause': {
                "subject": "Te extrañamos",
                "greeting": "Hola",
                "body": "Notamos que hace tiempo que no compras...",
                "offer": "15% de descuento",
                "cta": "Ver productos",
                "urgency": "Oferta limitada"
            }
        }
        return templates.get(segment, templates['frequent_buyer_pause'])
```

---

## 🔄 API Endpoints

### FastAPI Implementation

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import asyncio

app = FastAPI(title="AI Email Re-engagement API", version="1.0.0")

class CampaignRequest(BaseModel):
    name: str
    segment: str
    template_id: Optional[str] = None
    scheduled_at: Optional[datetime] = None

class CustomerSegment(BaseModel):
    segment: str
    count: int
    conversion_rate: float

@app.post("/campaigns")
async def create_campaign(campaign: CampaignRequest, background_tasks: BackgroundTasks):
    """Crear nueva campaña de re-engagement"""
    try:
        campaign_id = await ai_system.create_campaign(campaign.dict())
        
        # Ejecutar campaña en background si está programada
        if campaign.scheduled_at:
            background_tasks.add_task(
                ai_system.execute_campaign, 
                campaign_id
            )
        
        return {"campaign_id": campaign_id, "status": "created"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/campaigns/{campaign_id}/execute")
async def execute_campaign(campaign_id: str):
    """Ejecutar campaña inmediatamente"""
    try:
        results = await ai_system.execute_campaign(campaign_id)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/segments")
async def get_segments():
    """Obtener información de segmentos"""
    try:
        segments = await ai_system.get_segment_analytics()
        return segments
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(campaign_id: str):
    """Obtener analytics de campaña"""
    try:
        analytics = await ai_system.get_campaign_analytics(campaign_id)
        return analytics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/customers/{customer_id}/re-engage")
async def re_engage_customer(customer_id: str, segment: str):
    """Re-enganchar cliente específico"""
    try:
        customer = await ai_system.get_customer(customer_id)
        email_content = await ai_system.generate_email_content(customer, segment)
        send_time = await ai_system.optimize_send_time(customer)
        
        await ai_system._send_email(customer, email_content, send_time)
        
        return {"status": "email_sent", "send_time": send_time}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 Dashboard Frontend

### React Components

```typescript
// Dashboard principal
import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';

interface CampaignMetrics {
  totalCampaigns: number;
  activeCampaigns: number;
  totalEmailsSent: number;
  averageOpenRate: number;
  averageClickRate: number;
  averageConversionRate: number;
  totalRevenue: number;
}

const Dashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<CampaignMetrics | null>(null);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [metricsRes, campaignsRes] = await Promise.all([
        fetch('/api/dashboard/metrics'),
        fetch('/api/campaigns')
      ]);
      
      const metricsData = await metricsRes.json();
      const campaignsData = await campaignsRes.json();
      
      setMetrics(metricsData);
      setCampaigns(campaignsData);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <Typography variant="h4" gutterBottom>
        AI Email Re-engagement Dashboard
      </Typography>
      
      {/* Métricas principales */}
      <Grid container spacing={3} style={{ marginBottom: '20px' }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Campañas Activas
              </Typography>
              <Typography variant="h4">
                {metrics?.activeCampaigns}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Emails Enviados
              </Typography>
              <Typography variant="h4">
                {metrics?.totalEmailsSent?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Tasa de Apertura
              </Typography>
              <Typography variant="h4">
                {(metrics?.averageOpenRate * 100)?.toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Revenue Total
              </Typography>
              <Typography variant="h4">
                ${metrics?.totalRevenue?.toLocaleString()}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabla de campañas */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Campañas Recientes
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Nombre</TableCell>
                  <TableCell>Segmento</TableCell>
                  <TableCell>Estado</TableCell>
                  <TableCell>Emails Enviados</TableCell>
                  <TableCell>Tasa de Conversión</TableCell>
                  <TableCell>Acciones</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {campaigns.map((campaign: any) => (
                  <TableRow key={campaign.id}>
                    <TableCell>{campaign.name}</TableCell>
                    <TableCell>{campaign.segment}</TableCell>
                    <TableCell>{campaign.status}</TableCell>
                    <TableCell>{campaign.emails_sent}</TableCell>
                    <TableCell>{(campaign.conversion_rate * 100).toFixed(1)}%</TableCell>
                    <TableCell>
                      <Button 
                        variant="outlined" 
                        size="small"
                        onClick={() => executeCampaign(campaign.id)}
                      >
                        Ejecutar
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </div>
  );
};

export default Dashboard;
```

---

## 🚀 Deployment y CI/CD

### Docker Configuration

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

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy AI Email System

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

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
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest tests/ -v --cov=app
    
    - name: Run linting
      run: |
        flake8 app/
        black --check app/

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Configure AWS credentials
      uses: aws-actions/configure-aws-credentials@v1
      with:
        aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
        aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        aws-region: us-east-1
    
    - name: Build and push Docker image
      run: |
        docker build -t ai-email-system .
        docker tag ai-email-system:latest $ECR_REGISTRY/ai-email-system:latest
        docker push $ECR_REGISTRY/ai-email-system:latest
    
    - name: Deploy to ECS
      run: |
        aws ecs update-service \
          --cluster ai-email-cluster \
          --service ai-email-service \
          --force-new-deployment
```

---

## 🔒 Seguridad y Compliance

### Configuración de Seguridad

```python
# security.py
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from datetime import datetime, timedelta

security = HTTPBearer()

class SecurityManager:
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET_KEY")
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials = Depends(security)):
        try:
            payload = jwt.decode(credentials.credentials, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Rate limiting
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/campaigns")
@limiter.limit("10/minute")
async def create_campaign(request: Request, campaign: CampaignRequest):
    # Implementation
    pass
```

---

## 📈 Monitoring y Logging

### Configuración de Logging

```python
# logging_config.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging():
    # Configurar logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler para stdout
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    
    # Formato JSON para logs estructurados
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(name)s %(levelname)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger

# Métricas con Prometheus
from prometheus_client import Counter, Histogram, generate_latest
import time

# Métricas
EMAILS_SENT = Counter('emails_sent_total', 'Total emails sent', ['campaign', 'segment'])
EMAIL_OPEN_RATE = Histogram('email_open_rate', 'Email open rate', ['campaign'])
EMAIL_CONVERSION_RATE = Histogram('email_conversion_rate', 'Email conversion rate', ['campaign'])

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

---

## 🧪 Testing

### Test Suite

```python
# tests/test_ai_email_system.py
import pytest
import asyncio
from unittest.mock import Mock, patch
from app.ai_email_system import AIEmailReengagement

@pytest.fixture
def ai_system():
    return AIEmailReengagement("test_key", "test_db")

@pytest.fixture
def sample_customer():
    return {
        "id": "123",
        "email": "test@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "total_spent": 500.0,
        "purchase_count": 5,
        "last_purchase_date": "2023-01-01",
        "segment": "high_value_inactive"
    }

@pytest.mark.asyncio
async def test_customer_segmentation(ai_system):
    # Test data
    customer_data = pd.DataFrame({
        'total_spent': [100, 500, 1000, 50],
        'purchase_count': [2, 5, 10, 1],
        'days_since_last_purchase': [30, 90, 180, 15]
    })
    
    result = await ai_system.segment_customers(customer_data)
    
    assert 'segment' in result.columns
    assert len(result['segment'].unique()) <= 4

@pytest.mark.asyncio
async def test_email_content_generation(ai_system, sample_customer):
    with patch('openai.OpenAI') as mock_openai:
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '{"subject": "Test Subject"}'
        
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        result = await ai_system.generate_email_content(sample_customer, "high_value_inactive")
        
        assert 'subject' in result
        assert 'body' in result

@pytest.mark.asyncio
async def test_campaign_execution(ai_system):
    with patch.object(ai_system, '_get_campaign') as mock_campaign, \
         patch.object(ai_system, '_get_customers_by_segment') as mock_customers, \
         patch.object(ai_system, 'generate_email_content') as mock_content, \
         patch.object(ai_system, '_send_email') as mock_send:
        
        mock_campaign.return_value = {"segment": "high_value_inactive"}
        mock_customers.return_value = [{"id": "123", "email": "test@example.com"}]
        mock_content.return_value = {"subject": "Test"}
        
        result = await ai_system.execute_campaign("test_campaign")
        
        assert result['total_customers'] == 1
        assert result['emails_sent'] == 1
```

---

## 📚 Documentación de API

### OpenAPI/Swagger Documentation

```python
# main.py
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

app = FastAPI(
    title="AI Email Re-engagement API",
    description="API para sistema de re-engagement de clientes usando IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="AI Email Re-engagement API",
        version="1.0.0",
        description="""
        ## Descripción
        
        Esta API permite gestionar campañas de re-engagement de clientes usando inteligencia artificial.
        
        ## Características
        
        * **Segmentación automática** de clientes
        * **Generación de contenido** con GPT-4
        * **Optimización de timing** de envío
        * **Analytics en tiempo real**
        * **A/B testing** automatizado
        
        ## Autenticación
        
        Usa Bearer token en el header Authorization.
        """,
        routes=app.routes,
    )
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
```

---

## 🚀 Próximos Pasos

### Roadmap Técnico

**Fase 1 (Mes 1-2):**
- [ ] Setup de infraestructura básica
- [ ] Implementación de segmentación
- [ ] Integración con GPT-4
- [ ] API básica funcional

**Fase 2 (Mes 3-4):**
- [ ] Dashboard frontend
- [ ] Analytics avanzados
- [ ] A/B testing automatizado
- [ ] Optimización de performance

**Fase 3 (Mes 5-6):**
- [ ] Machine Learning avanzado
- [ ] Integraciones adicionales
- [ ] Escalabilidad horizontal
- [ ] Monitoreo y alertas

**Fase 4 (Mes 7+):**
- [ ] IA personalizada por cliente
- [ ] Predicción avanzada
- [ ] Automatización completa
- [ ] Optimización continua

### Consideraciones de Escalabilidad

- **Microservicios**: Separar en servicios independientes
- **Message Queues**: Usar Redis/RabbitMQ para tareas asíncronas
- **Caching**: Implementar cache distribuido
- **Load Balancing**: Distribuir carga entre instancias
- **Database Sharding**: Particionar datos por segmento
- **CDN**: Cachear contenido estático
- **Auto-scaling**: Escalar automáticamente según demanda



