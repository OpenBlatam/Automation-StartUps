# KPIs API - Express + TypeScript

Aplicación web ligera en Express.js con TypeScript que expone una API REST y una interfaz HTML para visualizar KPIs del negocio.

## Descripción

Esta aplicación lee datos de las tablas `payments` y `leads` de PostgreSQL y expone:

- **API JSON**: Endpoint `/api/kpi/summary` con métricas agregadas
- **Interfaz HTML**: Página en `/` con dashboard visual de KPIs
- **Métricas Prometheus**: Endpoint `/metrics` para observabilidad
- **Health Checks**: Endpoint `/health` para monitoreo

## Estructura

```
kpis/
├── src/
│   ├── __tests__/       # Tests unitarios
│   │   ├── api.test.ts
│   │   └── smoke.test.ts
├── Dockerfile           # Imagen Docker multi-stage
├── ENV_EXAMPLE          # Ejemplo de variables de entorno
├── jest.config.ts        # Configuración de Jest
├── package.json         # Dependencias y scripts
└── tsconfig.json        # Configuración de TypeScript
```

## Características

- ✅ **TypeScript**: Type-safe code
- ✅ **Express**: Framework web minimalista y rápido
- ✅ **PostgreSQL**: Conexión a base de datos con pooling
- ✅ **Prometheus Metrics**: Endpoint `/metrics` para observabilidad
- ✅ **Security**: Helmet, CORS, rate limiting
- ✅ **Testing**: Jest para tests unitarios y de integración
- ✅ **Health Checks**: Endpoint `/health` para Kubernetes probes
- ✅ **Error Handling**: Manejo robusto de errores
- ✅ **Logging**: Logging estructurado

## Instalación

### Desarrollo Local

```bash
cd web/kpis

# Instalar dependencias
npm install

# Configurar variables de entorno
cp ENV_EXAMPLE .env
# Editar .env con tus valores

# Ejecutar en modo desarrollo
npm run dev

# La aplicación estará en http://localhost:3001
```

### Variables de Entorno

```bash
# Base de datos PostgreSQL
KPIS_PG_HOST=localhost
KPIS_PG_PORT=5432
KPIS_PG_DB=analytics
KPIS_PG_USER=analytics
KPIS_PG_PASSWORD=your_password

# Servidor
PORT=3001
NODE_ENV=development

# Seguridad
API_KEY=optional_api_key  # Opcional, para proteger rutas /api
ENABLE_RATE_LIMIT=true    # Habilitar rate limiting
```

## Uso

### API Endpoint

```bash
# Obtener resumen de KPIs
curl http://localhost:3001/api/kpi/summary

# Respuesta JSON:
{
  "revenue_1h": 1250.50,
  "revenue_24h": 15230.75,
  "revenue_by_hour": [...],
  "recent_payments": [...],
  "recent_leads": [...],
  "leads_by_priority": {...},
  "conversion_7d": 15.5
}
```

### Interfaz Web

Abre `http://localhost:3001` en el navegador para ver el dashboard HTML con:

- Ingresos (última hora, últimas 24h)
- Gráfico de ingresos por hora
- Tabla de pagos recientes
- Tabla de leads recientes
- Métricas de conversión

### Health Check

```bash
# Verificar salud de la aplicación
curl http://localhost:3001/health

# Respuesta:
{
  "status": "healthy",
  "database": "connected",
  "uptime": 3600
}
```

### Métricas Prometheus

```bash
# Endpoint de métricas
curl http://localhost:3001/metrics

# Métricas expuestas:
# - http_requests_total
# - http_request_duration_seconds
# - kpis_db_query_duration_seconds
# - kpis_db_connections_active
```

## Scripts NPM

```bash
# Desarrollo con hot-reload (nodemon)
npm run dev

# Compilar TypeScript
npm run build

# Ejecutar producción
npm start

# Tests
npm test

# Linting
npm run lint

# Formateo
npm run format

# Type checking
npm run typecheck
```

## Despliegue

### Docker

```bash
# Construir imagen
docker build -t kpis-api:latest .

# Ejecutar contenedor
docker run -p 3001:3001 \
  -e KPIS_PG_HOST=postgres \
  -e KPIS_PG_DB=analytics \
  -e KPIS_PG_USER=analytics \
  -e KPIS_PG_PASSWORD=password \
  kpis-api:latest
```

### Kubernetes

Ver `kubernetes/integration/kpis-api.yaml` para el Deployment completo.

```bash
# Aplicar
kubectl apply -f kubernetes/integration/kpis-api.yaml

# Configurar secrets
kubectl create secret generic kpis-db-credentials \
  --from-literal=KPIS_PG_HOST=postgres.example.com \
  --from-literal=KPIS_PG_DB=analytics \
  --from-literal=KPIS_PG_USER=analytics \
  --from-literal=KPIS_PG_PASSWORD=password \
  -n integration
```

### Helmfile

Si está configurado en `helmfile.yaml`:

```bash
helmfile apply
```

### Ingress

Expón la aplicación con Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kpis-api
  namespace: integration
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - kpis-api.example.com
    secretName: kpis-api-tls
  rules:
  - host: kpis-api.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kpis-api
            port:
              number: 80
```

## Testing

```bash
# Ejecutar todos los tests
npm test

# Ejecutar tests en modo watch
npm test -- --watch

# Coverage
npm test -- --coverage
```

Los tests están en `src/__tests__/`:
- `smoke.test.ts`: Tests de smoke básicos
- `api.test.ts`: Tests de la API

## Estructura del Código

```typescript
// src/index.ts (estructura simplificada)
import express from 'express';
import { createKPIRouter } from './routes/kpi';
import { setupMetrics } from './metrics';
import { setupHealthCheck } from './health';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(rateLimit({ windowMs: 15 * 60 * 1000, max: 100 }));

// Rutas
app.use('/api/kpi', createKPIRouter());
app.get('/metrics', metricsHandler);
app.get('/health', healthCheckHandler);

// Servir HTML
app.get('/', serveDashboard);

app.listen(PORT);
```

## Integración con Observabilidad

### Prometheus

La aplicación expone métricas en `/metrics`. Configura un ServiceMonitor:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: kpis-api
  namespace: integration
spec:
  selector:
    matchLabels:
      app: kpis-api
  endpoints:
    - port: http
      path: /metrics
      interval: 30s
```

Ver `observability/servicemonitors/kpis-api.yaml`.

### Logging

Los logs se estructuran para integración con Loki:

```typescript
logger.info('KPI request', { 
  endpoint: '/api/kpi/summary',
  duration: 45,
  status: 200,
  userAgent: req.get('user-agent')
});
```

### Health Checks (Kubernetes)

Configura probes en el Deployment:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 3001
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /health
    port: 3001
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Seguridad

- **Helmet**: Headers de seguridad HTTP
- **CORS**: Configuración de origen cruzado
- **Rate Limiting**: Protección contra abuso (100 req/15min por defecto)
- **Input Validation**: Validación de parámetros
- **SQL Injection**: Uso de parámetros preparados en queries
- **API Key**: Opcional para proteger rutas `/api/*`

## Performance

- **Connection Pooling**: Pool de conexiones PostgreSQL configurable
- **Caching**: Considera agregar cache Redis para queries frecuentes
- **Compression**: Habilitar compresión gzip para respuestas grandes

## Troubleshooting

### Error de conexión a PostgreSQL

```bash
# Verificar conectividad
psql -h $KPIS_PG_HOST -U $KPIS_PG_USER -d $KPIS_PG_DB

# Verificar variables de entorno
echo $KPIS_PG_HOST
echo $KPIS_PG_DB
```

### Puerto ya en uso

```bash
# Cambiar Puerto
PORT=3002 npm run dev
```

### Error de compilación TypeScript

```bash
# Verificar tipos
npm run typecheck

# Reinstalar dependencias
rm -rf node_modules package-lock.json
npm install
```

### Error de base de datos

```bash
# Verificar que las tablas existen
psql $KPIS_PG_HOST -U $KPIS_PG_USER -d $KPIS_PG_DB -c "\dt"

# Verificar esquema
psql $KPIS_PG_HOST -U $KPIS_PG_USER -d $KPIS_PG_DB -f ../../data/db/schema.sql
```

## Desarrollo

### Agregar Nuevo Endpoint

1. Crear handler en `src/handlers/`
2. Agregar ruta en `src/routes/`
3. Agregar tests en `src/__tests__/`
4. Documentar en este README

### Agregar Nueva Métrica

```typescript
import { Counter, Histogram } from 'prom-client';

const kpiQueries = new Counter({
  name: 'kpi_queries_total',
  help: 'Total KPI queries'
});

kpiQueries.inc();
```

## Referencias

- [Express.js Documentation](https://expressjs.com/)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)
- [Prometheus Client for Node.js](https://github.com/siimon/prom-client)
- [PostgreSQL Node.js Driver](https://node-postgres.com/)

