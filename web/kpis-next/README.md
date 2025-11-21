# KPIs Dashboard - Next.js

Aplicación web moderna en Next.js (React + TypeScript) que proporciona un dashboard interactivo de KPIs con Server-Side Rendering (SSR) y API Routes.

## Descripción

Esta aplicación Next.js ofrece:

- **SSR Dashboard**: Página principal con KPIs renderizados en servidor
- **API Routes**: Endpoints `/api/kpi/*` para consultar métricas
- **ETL Dashboard**: Vista de monitoreo de pipelines ETL
- **Real-time Updates**: Capacidad de refresco de datos

## Estructura

```
kpis-next/
├── app/                    # App Router de Next.js 13+
│   ├── api/               # API Routes
│   │   └── kpi/          # Endpoints de KPIs
│   ├── etl/              # Página de ETL dashboard
│   ├── layout.tsx        # Layout principal
│   └── page.tsx          # Página principal (dashboard)
├── components/           # Componentes React
│   ├── Dashboard.tsx     # Dashboard principal
│   └── EtlDashboard.tsx  # Dashboard ETL
├── lib/                  # Utilidades y lógica
│   ├── db.ts            # Conexión a PostgreSQL
│   └── kpi.ts           # Funciones de cálculo de KPIs
├── Dockerfile
├── ENV_EXAMPLE
├── jest.config.ts
├── package.json
└── tsconfig.json
```

## Características

- **Next.js 13+ App Router**: Arquitectura moderna de Next.js
- **TypeScript**: Type safety completo
- **Server Components**: Renderizado en servidor eficiente
- **API Routes**: Backend integrado en Next.js
- **PostgreSQL**: Integración con base de datos
- **Testing**: Jest + React Testing Library
- **Responsive**: Diseño adaptable a móviles

## Instalación

### Desarrollo Local

```bash
cd web/kpis-next

# Instalar dependencias
npm install

# Configurar variables de entorno
cp ENV_EXAMPLE .env.local
# Editar .env.local

# Ejecutar en desarrollo
npm run dev

# Abrir http://localhost:3000
```

### Variables de Entorno

```bash
# Base de datos
KPIS_PG_HOST=localhost
KPIS_PG_PORT=5432
KPIS_PG_DB=analytics
KPIS_PG_USER=analytics
KPIS_PG_PASSWORD=your_password

# Next.js
NEXT_PUBLIC_BASE_URL=http://localhost:3000
NODE_ENV=development
```

## Uso

### API Routes

La aplicación expone varios endpoints:

#### GET /api/kpi/summary

Resumen de KPIs principales:

```bash
curl http://localhost:3000/api/kpi/summary
```

Respuesta:
```json
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

#### GET /api/kpi/revenue

Ingresos agregados:

```bash
curl http://localhost:3000/api/kpi/revenue?period=24h
```

### Páginas

#### Dashboard Principal (/)

Página principal con métricas de KPIs:
- Ingresos (1h, 24h)
- Gráfico de ingresos por hora
- Tablas de pagos y leads recientes
- Métricas de conversión

#### ETL Dashboard (/etl)

Vista de monitoreo de pipelines ETL:
- Estado de ejecuciones
- Métricas de procesamiento
- Logs recientes

### Server-Side Rendering

Las páginas se renderizan en el servidor, mejorando:
- **SEO**: Contenido indexable por buscadores
- **Performance**: First Contentful Paint más rápido
- **Data Freshness**: Datos siempre actualizados

## Scripts NPM

```bash
# Desarrollo
npm run dev

# Build de producción
npm run build

# Ejecutar producción
npm start

# Tests
npm test

# Linting
npm run lint

# Type checking
npm run typecheck
```

## Despliegue

### Docker

```bash
# Construir imagen
docker build -t kpis-next:latest .

# Ejecutar
docker run -p 3000:3000 \
  -e KPIS_PG_HOST=postgres \
  -e KPIS_PG_DB=analytics \
  -e KPIS_PG_USER=analytics \
  -e KPIS_PG_PASSWORD=password \
  -e NEXT_PUBLIC_BASE_URL=http://localhost:3000 \
  kpis-next:latest
```

### Kubernetes

Crea un Deployment y Service:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kpis-next
  namespace: integration
spec:
  replicas: 2
  template:
    spec:
      containers:
      - name: app
        image: kpis-next:latest
        env:
        - name: KPIS_PG_HOST
          value: postgres.example.com
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: kpis-next
spec:
  selector:
    app: kpis-next
  ports:
  - port: 80
    targetPort: 3000
```

### Ingress

Expón la aplicación con Ingress:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: kpis-next
  namespace: integration
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - kpis.example.com
    secretName: kpis-next-tls
  rules:
  - host: kpis.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: kpis-next
            port:
              number: 80
```

## Testing

```bash
# Ejecutar tests
npm test

# Tests en modo watch
npm test -- --watch

# Coverage
npm test -- --coverage
```

Tests ubicados en:
- `__tests__/smoke.test.ts`: Tests de humo/smoke
- Tests de componentes en `components/` (si aplica)

## Estructura del Código

### App Router (Next.js 13+)

```typescript
// app/page.tsx - Server Component
export default async function HomePage() {
  const kpis = await getKPISummary(); // Server-side data fetch
  return <Dashboard data={kpis} />;
}

// app/api/kpi/summary/route.ts - API Route
export async function GET() {
  const data = await getKPISummary();
  return Response.json(data);
}
```

### Componentes

```typescript
// components/Dashboard.tsx
export function Dashboard({ data }: { data: KPISummary }) {
  return (
    <div>
      <RevenueCard revenue={data.revenue_24h} />
      <RecentPayments payments={data.recent_payments} />
    </div>
  );
}
```

### Utilidades

```typescript
// lib/kpi.ts
export async function getKPISummary(): Promise<KPISummary> {
  const db = await getDB();
  // Calcular KPIs desde PostgreSQL
  return { ... };
}
```

## Optimizaciones

### Image Optimization

Next.js optimiza imágenes automáticamente:

```tsx
import Image from 'next/image';

<Image src="/chart.png" width={800} height={600} alt="Chart" />
```

### Static Generation (ISR)

Para datos que no cambian frecuentemente:

```typescript
export const revalidate = 60; // Revalidar cada 60 segundos

export default async function Page() {
  const data = await getKPISummary();
  return <Dashboard data={data} />;
}
```

### API Caching

Cachear respuestas de API:

```typescript
export async function GET() {
  const data = await getKPISummary();
  return Response.json(data, {
    headers: {
      'Cache-Control': 'public, s-maxage=60, stale-while-revalidate=120',
    },
  });
}
```

## Integración con Observabilidad

### Métricas

Instrumenta con Prometheus client:

```typescript
import { Counter } from 'prom-client';

const apiRequests = new Counter({
  name: 'nextjs_api_requests_total',
  help: 'Total API requests',
});
```

### Logging

Logs estructurados:

```typescript
console.log(JSON.stringify({
  level: 'info',
  message: 'KPI request',
  endpoint: '/api/kpi/summary',
  duration: 45,
}));
```

## Troubleshooting

### Error de conexión a PostgreSQL

```bash
# Verificar variables de entorno
echo $KPIS_PG_HOST

# Verificar conectividad
psql -h $KPIS_PG_HOST -U $KPIS_PG_USER -d $KPIS_PG_DB
```

### Build errors

```bash
# Limpiar cache
rm -rf .next node_modules
npm install
npm run build
```

### Type errors

```bash
# Verificar tipos
npm run typecheck

# Regenerar tipos
npm run build
```

## Referencias

- [Next.js Documentation](https://nextjs.org/docs)
- [Next.js App Router](https://nextjs.org/docs/app)
- [React Server Components](https://react.dev/reference/rsc/server-components)
- [TypeScript Documentation](https://www.typescriptlang.org/docs/)


