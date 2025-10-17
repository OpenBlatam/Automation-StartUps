# AI Marketing Feedback System

Sistema avanzado de integración de feedback de clientes para plataformas de marketing con IA en América Latina.

## 🚀 Características Principales

### 📊 Análisis Avanzado de Feedback
- **Análisis de Sentimiento Multi-idioma**: Español, Portugués, Inglés
- **Inteligencia Emocional**: Detección de emociones primarias y secundarias
- **Análisis Cultural**: Contexto específico para mercados LATAM
- **Métricas Predictivas**: Churn, Upsell, Advocacy
- **Recomendaciones Accionables**: Insights automáticos para equipos

### 🤖 Machine Learning & IA
- **Modelos de ML Entrenables**: Sentimiento, emociones, predicciones
- **Análisis de Patrones**: Comportamiento y tendencias
- **Segmentación de Clientes**: Clustering automático
- **Análisis de Tendencias**: Evolución temporal de métricas

### 🔒 Seguridad Avanzada
- **Detección de Amenazas**: SQL injection, XSS, DDoS
- **Rate Limiting Inteligente**: Protección contra abuso
- **Auditoría de Seguridad**: Logs detallados de eventos
- **Encriptación**: Datos sensibles protegidos

### ⚡ Optimización de Rendimiento
- **Caché Inteligente**: LRU, LFU, FIFO strategies
- **Monitoreo en Tiempo Real**: Métricas de rendimiento
- **Optimización Automática**: Recomendaciones de mejora
- **Escalabilidad**: Arquitectura preparada para crecimiento

### 📡 Comunicación en Tiempo Real
- **WebSocket**: Notificaciones instantáneas
- **Alertas Inteligentes**: Basadas en umbrales configurables
- **Dashboard en Vivo**: Métricas actualizadas en tiempo real
- **Integración Multi-canal**: Email, Slack, Discord, Telegram

## 🏗️ Arquitectura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Load Balancer │
│   (React/Vue)   │◄──►│   (Express.js)  │◄──►│   (Nginx)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Services                                │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  Feedback       │  Analytics      │  ML Engine      │  Security │
│  Service        │  Service        │  Service        │  Service  │
├─────────────────┼─────────────────┼─────────────────┼───────────┤
│  Real-time      │  Performance    │  Monitoring     │  Cache    │
│  Notifications  │  Optimization   │  Service        │  Service  │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                   │
├─────────────────┬─────────────────┬─────────────────┬───────────┤
│  PostgreSQL     │  Redis          │  Elasticsearch  │  File     │
│  (Primary DB)   │  (Cache/Session)│  (Logs/Search)  │  Storage  │
└─────────────────┴─────────────────┴─────────────────┴───────────┘
```

## 🛠️ Tecnologías Utilizadas

### Backend
- **Node.js** + **TypeScript**: Runtime y lenguaje principal
- **Express.js**: Framework web
- **Prisma**: ORM para base de datos
- **PostgreSQL**: Base de datos principal
- **Redis**: Caché y sesiones
- **WebSocket**: Comunicación en tiempo real

### Machine Learning & IA
- **TensorFlow.js**: Modelos de ML
- **Natural Language Processing**: Análisis de texto
- **Sentiment Analysis**: Análisis de sentimientos
- **Emotion Detection**: Detección de emociones
- **Cultural Analysis**: Análisis cultural

### Seguridad
- **JWT**: Autenticación
- **bcrypt**: Encriptación de contraseñas
- **Helmet**: Headers de seguridad
- **Rate Limiting**: Protección contra abuso
- **Input Validation**: Validación de entrada

### Monitoreo & Observabilidad
- **Prometheus**: Métricas
- **Grafana**: Dashboards
- **ELK Stack**: Logs centralizados
- **Health Checks**: Verificaciones de salud
- **Alerting**: Sistema de alertas

### DevOps & Deployment
- **Docker**: Containerización
- **Docker Compose**: Orquestación local
- **Nginx**: Proxy reverso
- **CI/CD**: Integración continua

## 📦 Instalación

### Prerrequisitos
- Node.js 18+
- PostgreSQL 13+
- Redis 6+
- Docker & Docker Compose

### Instalación Local

1. **Clonar el repositorio**
```bash
git clone https://github.com/adan/ai-marketing-feedback-system.git
cd ai-marketing-feedback-system
```

2. **Instalar dependencias**
```bash
npm install
```

3. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

4. **Configurar base de datos**
```bash
npm run db:migrate
npm run db:generate
```

5. **Iniciar servicios**
```bash
# Desarrollo
npm run dev

# Producción
npm run build
npm start
```

### Instalación con Docker

```bash
# Iniciar todos los servicios
docker-compose up --build

# Solo la aplicación
docker-compose up app

# Con monitoreo
docker-compose -f docker-compose.monitoring.yml up
```

## 🚀 Uso

### API Endpoints

#### Feedback
```bash
# Procesar feedback
POST /api/feedback/process
{
  "content": "Excelente servicio, muy satisfecho",
  "source": "survey",
  "platform": "typeform",
  "language": "es",
  "region": "MX"
}

# Obtener analytics
GET /api/feedback/analytics?period=30d&region=MX

# Buscar feedback
GET /api/feedback/search?query=satisfecho&sentiment=positive
```

#### Análisis Avanzado
```bash
# Análisis completo
POST /api/advanced/feedback/advanced-analysis
{
  "content": "Me encanta el producto",
  "language": "es",
  "region": "MX"
}

# Inteligencia emocional
POST /api/advanced/feedback/emotional-intelligence
{
  "content": "Estoy muy emocionado con los resultados"
}

# Análisis cultural
POST /api/advanced/feedback/cultural-analysis
{
  "content": "Valoro mucho la relación personal",
  "region": "MX"
}
```

#### Machine Learning
```bash
# Análisis de sentimiento con ML
POST /api/ai/sentiment/advanced
{
  "content": "Increíble experiencia",
  "language": "es"
}

# Predicción de churn
POST /api/ai/predictions/churn
{
  "content": "Considerando cancelar",
  "customerHistory": [...]
}

# Segmentación de clientes
POST /api/ai/segmentation/customers
{
  "feedbacks": [...]
}
```

#### Monitoreo
```bash
# Dashboard
GET /api/monitoring/dashboard

# Salud del sistema
GET /api/monitoring/health

# Métricas
GET /api/monitoring/metrics?timeRange=24h

# Alertas
GET /api/monitoring/alerts?severity=critical
```

### WebSocket

```javascript
const ws = new WebSocket('ws://localhost:3001');

// Suscribirse a feedback
ws.send(JSON.stringify({
  type: 'subscribe_feedback'
}));

// Suscribirse a analytics
ws.send(JSON.stringify({
  type: 'subscribe_analytics'
}));

// Escuchar eventos
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Event:', data.event, data.data);
};
```

## 🧪 Testing

### Ejecutar Tests
```bash
# Todos los tests
npm test

# Tests unitarios
npm run test:unit

# Tests de integración
npm run test:integration

# Tests con cobertura
npm run test:coverage

# Tests en modo watch
npm run test:watch
```

### Tipos de Tests
- **Unit Tests**: Servicios individuales
- **Integration Tests**: Flujos completos
- **Performance Tests**: Rendimiento y carga
- **Security Tests**: Vulnerabilidades
- **E2E Tests**: Flujos de usuario

## 📊 Monitoreo

### Dashboard de Grafana
- **URL**: http://localhost:3000
- **Usuario**: admin
- **Contraseña**: admin

### Métricas de Prometheus
- **URL**: http://localhost:9090

### Logs de Elasticsearch
- **URL**: http://localhost:5601

### Health Checks
- **API**: http://localhost:3001/health
- **WebSocket**: ws://localhost:3001

## 🔧 Configuración

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:password@localhost:5432/feedback_db

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key
JWT_EXPIRATION=24h

# API Keys
VALID_API_KEYS=key1,key2,key3

# CORS
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Webhooks
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/YOUR/DISCORD/WEBHOOK
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Monitoreo
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### Configuración de Caché

```javascript
// Configurar caché
performanceOptimizationService.configureCache({
  ttl: 300, // 5 minutos
  maxSize: 1000,
  strategy: 'lru'
});
```

### Configuración de Alertas

```javascript
// Configurar umbrales
monitoringService.setAlertThresholds({
  responseTime: 2000, // 2 segundos
  errorRate: 5, // 5%
  cpuUsage: 80, // 80%
  memoryUsage: 85, // 85%
  securityThreats: 1 // 1 amenaza
});
```

## 🚀 Deployment

### Docker Compose (Recomendado)

```bash
# Desarrollo
docker-compose up --build

# Producción
docker-compose -f docker-compose.prod.yml up -d

# Con monitoreo
docker-compose -f docker-compose.monitoring.yml up -d
```

### Kubernetes

```bash
# Aplicar manifiestos
kubectl apply -f k8s/

# Verificar pods
kubectl get pods

# Verificar servicios
kubectl get services
```

### AWS/GCP/Azure

```bash
# Build de imagen
docker build -t ai-marketing-feedback-system .

# Push a registry
docker tag ai-marketing-feedback-system your-registry/ai-marketing-feedback-system
docker push your-registry/ai-marketing-feedback-system

# Deploy a cloud
# (Usar herramientas específicas de cada cloud)
```

## 📈 Escalabilidad

### Horizontal Scaling
- **Load Balancer**: Nginx o AWS ALB
- **Multiple Instances**: Docker Swarm o Kubernetes
- **Database Replication**: PostgreSQL master-slave
- **Cache Clustering**: Redis Cluster

### Vertical Scaling
- **Resource Monitoring**: CPU, Memory, Disk
- **Auto-scaling**: Basado en métricas
- **Performance Tuning**: Optimización de consultas
- **Caching Strategy**: Multi-level caching

## 🔒 Seguridad

### Mejores Prácticas
- **HTTPS**: Certificados SSL/TLS
- **Input Validation**: Sanitización de entrada
- **Rate Limiting**: Protección contra abuso
- **Authentication**: JWT + API Keys
- **Authorization**: Roles y permisos
- **Audit Logging**: Registro de eventos
- **Data Encryption**: Encriptación de datos sensibles

### Compliance
- **GDPR**: Protección de datos personales
- **LGPD**: Ley General de Protección de Datos (Brasil)
- **CCPA**: California Consumer Privacy Act
- **SOC 2**: Seguridad y disponibilidad

## 🤝 Contribución

### Cómo Contribuir
1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/amazing-feature`)
3. Commit de cambios (`git commit -m 'Add amazing feature'`)
4. Push al branch (`git push origin feature/amazing-feature`)
5. Abrir Pull Request

### Estándares de Código
- **TypeScript**: Tipado estricto
- **ESLint**: Linting de código
- **Prettier**: Formateo de código
- **Jest**: Testing
- **Conventional Commits**: Mensajes de commit

### Estructura del Proyecto
```
src/
├── controllers/     # Controladores de API
├── services/        # Lógica de negocio
├── routes/          # Rutas de API
├── middleware/      # Middleware personalizado
├── utils/           # Utilidades
├── tests/           # Tests
├── types/           # Tipos TypeScript
└── config/          # Configuraciones
```

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Adan - AI Marketing Expert**
- GitHub: [@adan](https://github.com/adan)
- LinkedIn: [Adan](https://linkedin.com/in/adan)
- Email: adan@example.com

## 🆘 Soporte

### Documentación
- **API Docs**: http://localhost:3001/api-docs
- **Guía de Usuario**: [docs/user-guide.md](docs/user-guide.md)
- **FAQ**: [docs/faq.md](docs/faq.md)

### Comunidad
- **Discord**: [Discord Server](https://discord.gg/ai-marketing)
- **Slack**: [Slack Workspace](https://ai-marketing.slack.com)
- **GitHub Issues**: [Issues](https://github.com/adan/ai-marketing-feedback-system/issues)

### Soporte Comercial
- **Email**: support@ai-marketing.com
- **Teléfono**: +1 (555) 123-4567
- **Horario**: Lunes a Viernes, 9:00 AM - 6:00 PM EST

---

## 🎯 Roadmap

### Versión 2.0 (Q2 2024)
- [ ] Análisis de voz y video
- [ ] Integración con más plataformas
- [ ] Dashboard personalizable
- [ ] API GraphQL
- [ ] Mobile SDK

### Versión 2.1 (Q3 2024)
- [ ] Análisis de competencia
- [ ] Predicción de tendencias
- [ ] Automatización de respuestas
- [ ] Integración con CRM
- [ ] Multi-tenant

### Versión 3.0 (Q4 2024)
- [ ] IA Generativa
- [ ] Análisis de imágenes
- [ ] Realidad Aumentada
- [ ] Blockchain integration
- [ ] Edge computing

---

**¡Gracias por usar AI Marketing Feedback System! 🚀**






