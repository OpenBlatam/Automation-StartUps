---
title: "Api Documentation"
category: "api_documentation.md"
tags: []
created: "2025-10-29"
path: "api_documentation.md"
---

# Documentación de la API

## Base URL

```
http://localhost:5000/api
```

## Autenticación

La API utiliza autenticación JWT. Para acceder a los endpoints protegidos, incluye el token en el header `Authorization: Bearer <token>`.

### Login
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

### Usuarios disponibles (desarrollo):
- **admin** / admin123 - Acceso completo
- **manager** / manager123 - Lectura y escritura
- **viewer** / viewer123 - Solo lectura

## Endpoints
### Documentación Interactiva (Swagger)

- UI: `http://localhost:5000/api/docs`
- Especificación: `http://localhost:5000/api/openapi.json`

Puedes probar los endpoints desde el navegador y compartir el archivo OpenAPI.

### Salud del Sistema

#### GET /health
Devuelve el estado del sistema, base de datos y servicios.

Ejemplo de respuesta:
```json
{
  "status": "ok",
  "timestamp": "2025-10-30T10:00:00Z",
  "version": "unknown",
  "services": {
    "database": "ok",
    "notifications": "ok"
  }
}
```

### Productos
### Integraciones

#### Slack
- Configurar `SLACK_WEBHOOK_URL` en `.env`
- Probar: `POST /api/notifications/slack/test` (requiere token admin)

#### Webhooks
- Configurar `WEBHOOK_URLS` (coma-separado) en `.env`
- Probar: `POST /api/webhooks/test` (requiere token admin)

#### Telegram
- Configurar `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en `.env`
- Probar: `POST /api/notifications/telegram/test` (requiere token admin)

### Eventos Automáticos
### Scheduler (Resumen Diario)
### Observabilidad

- Todas las respuestas incluyen `X-Request-ID` para correlación de logs.
- Puedes habilitar logs en JSON (útil para ELK/Datadog) con:
```
LOG_JSON=true
```

### Métricas (Prometheus)
### Rate Limiting Persistente (Redis)

- Habilita límite por minuto en endpoints usando Redis.
- Variables en `.env`:
```
REDIS_URL=redis://localhost:6379/0
RATE_LIMIT_PER_MINUTE=60
```
- Si Redis no está configurado, el rate limit persistente se desactiva automáticamente.

- Endpoint: `GET /api/metrics`
- Expuesto si la librería `prometheus_client` está instalada.
- Incluye:
  - `http_requests_total{method,endpoint,status}`
  - `http_request_latency_seconds{method,endpoint}`

Uso sugerido:
```bash
curl http://localhost:5000/api/metrics
```

Opcionalmente, el sistema puede enviar un resumen diario automático por email.

Configuración en `.env`:
```
DAILY_SUMMARY_ENABLED=true
DAILY_SUMMARY_TIME=08:00   # Hora UTC (HH:MM)
```

Notas:
- Requiere configurar email en `.env` (MAIL_SERVER, MAIL_USERNAME, etc.).
- El envío usa la misma lógica que `POST /api/notifications/send-daily-summary`.
- Al crear una venta (`POST /api/sales`):
  - Publica evento `sale.created` a Webhooks configurados
  - Envía notificación a Slack
  - Si el stock queda por debajo del mínimo: publica `inventory.low_stock` y notifica a Slack

#### GET /products/export
Exporta productos a CSV. Soporta los mismos filtros que `GET /products` (`q`, `sku`, `category`, `min_price`, `max_price`).

Ejemplo:
```
GET /api/products/export?q=pro&category=Electrónica
```

Descarga `products.csv`.

#### GET /products
Obtiene productos con filtros, orden y paginación

**Respuesta:**
**Query params soportados:**

- `page` (int): número de página
- `per_page` (int): tamaño de página
- `q` (string): búsqueda en nombre, sku, descripción, categoría
- `sku` (string): filtra por SKU
- `category` (string): filtra por categoría
- `min_price` (float): precio mínimo
- `max_price` (float): precio máximo
- `sort` (id|name|sku|category|unit_price|created_at): campo de ordenamiento
- `order` (asc|desc): dirección de ordenamiento

Si se usa paginación, la respuesta será:

```json
{
  "items": [...],
  "page": 1,
  "per_page": 20,
  "total": 125,
  "pages": 7
}
```
```json
[
  {
    "id": 1,
    "name": "Producto Ejemplo",
    "sku": "PROD-001",
    "description": "Descripción",
    "category": "Electrónica",
    "unit_price": 150.0,
    "cost_price": 100.0,
    "current_stock": 50,
    "min_stock_level": 10,
    "max_stock_level": 100
  }
]
```

#### POST /products
Crea un nuevo producto

**Body:**
```json
{
  "name": "Nuevo Producto",
  "sku": "PROD-002",
  "description": "Descripción",
  "category": "Categoría",
  "unit_price": 150.0,
  "cost_price": 100.0,
  "min_stock_level": 10,
  "max_stock_level": 100,
  "reorder_point": 20,
  "supplier_id": 1
}
```

#### GET /products/{id}
Obtiene un producto específico

#### PUT /products/{id}
Actualiza un producto

#### DELETE /products/{id}
Elimina un producto

### Inventario

#### GET /inventory
Obtiene el estado actual del inventario (con paginación opcional)
Soporta `page` y `per_page` con el mismo formato de respuesta paginada que `/products`.

**Respuesta:**
```json
[
  {
    "product_id": 1,
    "product_name": "Producto",
    "sku": "PROD-001",
    "current_stock": 50,
    "min_stock_level": 10,
    "max_stock_level": 100,
    "status": "normal"
  }
]
```

#### POST /inventory/movements
Registra un movimiento de inventario

**Body:**
```json
{
  "product_id": 1,
  "quantity": 100,
  "movement_type": "in",
  "reference": "PEDIDO-001",
  "notes": "Entrada de inventario"
}
```

**Tipos de movimiento:**
- `in`: Entrada
- `out`: Salida
- `adjustment`: Ajuste

### Ventas
#### GET /sales/export
Exporta ventas a CSV. Soporta `days`, `start_date`, `end_date`, `customer_id`.

Ejemplo:
```
GET /api/sales/export?start_date=2024-01-01&end_date=2024-01-31
```

Descarga `sales.csv`.

#### GET /sales
Obtiene registros de ventas (con filtros y paginación)

Query params:

- `days` (int): número de días a consultar (default: 30 si no se envía `start_date`)
- `start_date` (YYYY-MM-DD): fecha de inicio
- `end_date` (YYYY-MM-DD): fecha de fin
- `customer_id` (int): filtrar por cliente
- `page`, `per_page`: paginación opcional

Si se usa paginación, la respuesta incluye `items`, `page`, `per_page`, `total`, `pages`.

Notas de rendimiento:
- Las respuestas de listas incluyen cabeceras `ETag` y `Cache-Control` para caching ligero en clientes y proxies.

#### POST /sales
Registra una venta

**Body:**
```json
{
  "product_id": 1,
  "quantity_sold": 5,
  "unit_price": 150.0,
  "sale_date": "2024-01-15T10:30:00",
  "customer_id": 1
}
```

### Alertas

#### GET /alerts
Obtiene alertas activas

**Query Parameters:**
- `severity`: Filtrar por severidad (critical, high, medium, low)

**Respuesta:**
```json
[
  {
    "id": 1,
    "product_id": 1,
    "alert_type": "low_stock",
    "message": "Producto con stock bajo",
    "severity": "high",
    "created_at": "2024-01-15T10:30:00"
  }
]
```

#### POST /alerts/check
Verifica alertas manualmente

### Predicciones

#### GET /forecasts/{product_id}
Obtiene predicción de demanda para un producto

**Query Parameters:**
- `days`: Días a predecir (default: 30)

**Respuesta:**
```json
{
  "product_id": 1,
  "predicted_demand": 150.5,
  "algorithm": "moving_average",
  "confidence": 0.85,
  "data_points": 30
}
```

### Reposición

#### GET /replenishment/recommendations
Obtiene recomendaciones de reposición

**Respuesta:**
```json
[
  {
    "product_id": 1,
    "product_name": "Producto",
    "current_stock": 10,
    "recommended_quantity": 100,
    "urgency": "high",
    "estimated_cost": 10000.0
  }
]
```

### KPIs

#### GET /kpis
Obtiene todos los KPIs del sistema

**Respuesta:**
```json
{
  "inventory": {
    "total_products": 10,
    "total_value": 15000.0,
    "low_stock_count": 2
  },
  "sales": {
    "total_revenue": 5000.0,
    "growth_rate": 0.15
  },
  "financial": {
    "profit_margin": 0.33
  }
}
```

## Códigos de Estado HTTP

- `200`: OK - Solicitud exitosa
- `201`: Created - Recurso creado exitosamente
- `400`: Bad Request - Solicitud inválida
- `404`: Not Found - Recurso no encontrado
- `500`: Internal Server Error - Error del servidor
- `429`: Too Many Requests - Rate limit excedido

## Ejemplos de Uso

Ver archivo `examples/api_examples.py` para ejemplos completos en Python.

### Ejemplo con curl

```bash
# 1. Login para obtener token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' | jq -r '.token')

# 2. Obtener todos los productos (requiere autenticación)
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/products

# 3. Crear un producto
curl -X POST http://localhost:5000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Producto Test",
    "sku": "TEST-001",
    "unit_price": 100.0,
    "cost_price": 50.0
  }'

# 4. Obtener alertas
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/alerts?severity=critical

# 5. Exportar productos a Excel
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/products/export/excel -o productos.xlsx

# 6. Obtener reporte de ventas diarias
curl -H "Authorization: Bearer $TOKEN" http://localhost:5000/api/reports/sales/daily?days=7
```

### Ejemplo con Python

```python
import requests

# 1. Login para obtener token
login_data = {"username": "admin", "password": "admin123"}
response = requests.post('http://localhost:5000/api/auth/login', json=login_data)
token = response.json()['token']

# 2. Headers con autenticación
headers = {"Authorization": f"Bearer {token}"}

# 3. Obtener productos
response = requests.get('http://localhost:5000/api/products', headers=headers)
products = response.json()

# 4. Crear producto
new_product = {
    "name": "Nuevo Producto",
    "sku": "NP-001",
    "unit_price": 100.0,
    "cost_price": 50.0
}
response = requests.post(
    'http://localhost:5000/api/products',
    json=new_product,
    headers=headers
)

# 5. Obtener dashboard
response = requests.get('http://localhost:5000/api/dashboard/summary', headers=headers)
dashboard = response.json()

# 6. Exportar a Excel
response = requests.get('http://localhost:5000/api/products/export/excel', headers=headers)
with open('productos.xlsx', 'wb') as f:
    f.write(response.content)
```

## Rate Limiting

Algunos endpoints tienen rate limiting configurado (por defecto 60 requests por minuto).

Las respuestas incluyen headers:
- `X-RateLimit-Limit`: Límite de requests
- `X-RateLimit-Remaining`: Requests restantes

## Manejo de Errores

Todas las respuestas de error siguen este formato:

```json
{
  "error": true,
  "message": "Descripción del error",
  "timestamp": "2024-01-15T10:30:00"
}
```

