# 🚀 Mejoras API v7.0 - Sistema de Cartas de Oferta

## ✨ Mejoras Implementadas en la API

### 1. **Autenticación por API Key** ✅ NUEVO
Sistema de autenticación opcional usando Bearer tokens.

**Características:**
- ✅ Autenticación opcional (puede deshabilitarse)
- ✅ Bearer token authentication
- ✅ API key desde parámetro o variable de entorno
- ✅ Headers de autorización estándar

**Uso:**
```bash
# Iniciar con autenticación
python offer_letter_api.py --auth --api-key "your-secret-key"

# O usar variable de entorno
export API_KEY="your-secret-key"
python offer_letter_api.py --auth

# Hacer request con autenticación
curl -X POST http://localhost:8000/generate \
  -H "Authorization: Bearer your-secret-key" \
  -H "Content-Type: application/json" \
  -d '{"position_title": "Engineer", ...}'
```

### 2. **Estadísticas de la API** ✅ NUEVO
Sistema completo de métricas y estadísticas en tiempo real.

**Características:**
- ✅ Contador de requests totales
- ✅ Contador de requests exitosos
- ✅ Contador de requests fallidos
- ✅ Tasa de éxito
- ✅ Uptime del servidor
- ✅ Endpoint `/stats` para consultar

**Uso:**
```bash
# Consultar estadísticas
curl http://localhost:8000/stats

# Respuesta:
{
  "status": "ok",
  "statistics": {
    "total_requests": 150,
    "successful_requests": 145,
    "failed_requests": 5,
    "success_rate": 96.67,
    "uptime_seconds": 3600.5,
    "start_time": "2025-11-10T10:00:00"
  }
}
```

### 3. **Endpoint de Plantillas** ✅ NUEVO
Endpoint para listar todas las plantillas disponibles.

**Características:**
- ✅ Lista todas las plantillas
- ✅ Incluye descripciones
- ✅ Información de archivos
- ✅ Contador de plantillas

**Uso:**
```bash
# Listar plantillas
curl http://localhost:8000/templates

# Respuesta:
{
  "status": "ok",
  "templates": [
    {
      "name": "startup",
      "description": "Para startups con equity",
      "file": "startup.json"
    },
    ...
  ],
  "count": 3
}
```

### 4. **Mejoras en Manejo de Errores** ✅ MEJORADO
Sistema mejorado de manejo de errores y logging.

**Características:**
- ✅ Logging estructurado
- ✅ Traceback en modo debug
- ✅ Mensajes de error descriptivos
- ✅ Códigos de estado HTTP correctos
- ✅ Tracking de errores en estadísticas

### 5. **CORS Mejorado** ✅ MEJORADO
Soporte completo para CORS con headers apropiados.

**Características:**
- ✅ Headers CORS estándar
- ✅ Soporte para OPTIONS (preflight)
- ✅ Configuración flexible
- ✅ Seguridad mejorada

### 6. **Validación Mejorada** ✅ MEJORADO
Sistema de validación más robusto.

**Características:**
- ✅ Validación de tamaño de request (10MB límite)
- ✅ Validación de JSON
- ✅ Validación de campos requeridos
- ✅ Validación de formatos
- ✅ Mensajes de error claros

### 7. **Modo Debug** ✅ NUEVO
Modo debug para desarrollo y troubleshooting.

**Uso:**
```bash
# Iniciar en modo debug
python offer_letter_api.py --debug

# Incluye tracebacks completos en errores
```

## 📋 Nuevos Endpoints

| Endpoint | Método | Descripción | Autenticación |
|----------|--------|-------------|---------------|
| `/` | GET | Información de la API | No |
| `/api` | GET | Información de la API (alias) | No |
| `/health` | GET | Health check | No |
| `/docs` | GET | Documentación de la API | No |
| `/stats` | GET | Estadísticas de la API | Opcional |
| `/templates` | GET | Listar plantillas | Opcional |
| `/generate` | POST | Generar carta de oferta | Opcional |

## 🎯 Ejemplos de Uso

### Ejemplo 1: API sin Autenticación
```bash
# Iniciar servidor
python offer_letter_api.py --port 8000

# Generar oferta
curl -X POST http://localhost:8000/generate \
  -H "Content-Type: application/json" \
  -d '{
    "position_title": "Software Engineer",
    "salary_amount": "120000",
    "start_date": "2024-03-15",
    "benefits": ["Health insurance"],
    "location": "San Francisco, CA",
    "format": "html"
  }'
```

### Ejemplo 2: API con Autenticación
```bash
# Iniciar con autenticación
export API_KEY="secret-key-123"
python offer_letter_api.py --auth --port 8000

# Generar oferta con autenticación
curl -X POST http://localhost:8000/generate \
  -H "Authorization: Bearer secret-key-123" \
  -H "Content-Type: application/json" \
  -d '{
    "position_title": "Engineer",
    "salary_amount": "120000",
    "start_date": "2024-03-15",
    "benefits": ["Health insurance"],
    "location": "SF",
    "format": "both"
  }'
```

### Ejemplo 3: Consultar Estadísticas
```bash
# Ver estadísticas
curl http://localhost:8000/stats

# Ver plantillas
curl http://localhost:8000/templates

# Ver documentación
curl http://localhost:8000/docs
```

### Ejemplo 4: Integración con Otros Sistemas
```python
import requests

# Configurar
API_URL = "http://localhost:8000"
API_KEY = "your-secret-key"

# Generar oferta
response = requests.post(
    f"{API_URL}/generate",
    json={
        "position_title": "Engineer",
        "salary_amount": "120000",
        "start_date": "2024-03-15",
        "benefits": ["Health insurance"],
        "location": "SF",
        "format": "html"
    },
    headers={"Authorization": f"Bearer {API_KEY}"}
)

offer_data = response.json()
html_content = offer_data['result']['html']
```

## 📊 Mejoras Técnicas

### Seguridad
- ✅ Autenticación opcional
- ✅ Validación de tamaño de requests
- ✅ Headers CORS configurados
- ✅ Logging de errores sin exponer información sensible

### Rendimiento
- ✅ Tracking de tiempo de procesamiento
- ✅ Estadísticas en tiempo real
- ✅ Validación eficiente
- ✅ Manejo optimizado de errores

### Usabilidad
- ✅ Documentación integrada (`/docs`)
- ✅ Health check (`/health`)
- ✅ Estadísticas accesibles (`/stats`)
- ✅ Listado de plantillas (`/templates`)

## 🔧 Configuración

### Variables de Entorno
```bash
# API Key para autenticación
export API_KEY="your-secret-key"

# Configuración SMTP (para email)
export SMTP_USER="hr@company.com"
export SMTP_PASSWORD="password"
```

### Parámetros de Línea de Comandos
```bash
python offer_letter_api.py \
  --port 8000 \
  --host "" \
  --auth \
  --api-key "key" \
  --debug
```

## 📈 Estadísticas Disponibles

- **total_requests**: Total de requests recibidos
- **successful_requests**: Requests exitosos
- **failed_requests**: Requests fallidos
- **success_rate**: Porcentaje de éxito
- **uptime_seconds**: Tiempo activo del servidor
- **start_time**: Fecha/hora de inicio

## ✅ Estado

**Versión API**: 2.0  
**Estado**: ✅ Producción  
**Última Actualización**: Noviembre 2025

---

**🎉 API Mejorada y Lista para Producción! 🎉**



