# Offer Letter API - Sistema Completo de Gestión de Cartas de Oferta

Sistema enterprise completo para la generación, gestión y automatización de cartas de oferta laboral.

## 🚀 Características Principales

### Generación de Documentos
- ✅ Múltiples formatos: TXT, HTML, PDF, Word/RTF, JSON
- ✅ 5 plantillas personalizables (Standard, Executive, Technical, Intern, Contract)
- ✅ Internacionalización (ES, EN, FR, PT)
- ✅ Validación avanzada con JSON Schema

### API REST Completa
- ✅ 35+ endpoints RESTful
- ✅ Autenticación JWT
- ✅ Rate limiting inteligente
- ✅ Caché con TTL
- ✅ Documentación OpenAPI 3.0
- ✅ Swagger UI interactivo

### Seguridad
- ✅ Autenticación y autorización
- ✅ Firmas digitales
- ✅ Rate limiting por IP/usuario
- ✅ Validación de entrada
- ✅ Sanitización de datos

### Análisis y Reportes
- ✅ Dashboard con métricas en tiempo real
- ✅ Tasa de aceptación/rechazo
- ✅ Tendencias salariales
- ✅ Tiempo promedio hasta aceptación
- ✅ Exportación a CSV/Excel

### Integraciones
- ✅ ATS (Applicant Tracking Systems)
- ✅ HRIS (Human Resources Information Systems)
- ✅ Webhooks para notificaciones
- ✅ Envío por email con adjuntos

### Operaciones
- ✅ Sistema de versiones
- ✅ Backup y restore automático
- ✅ Logging avanzado con rotación
- ✅ Monitor de rendimiento
- ✅ Health checks (Kubernetes ready)
- ✅ Métricas Prometheus

## 📦 Instalación

### Requisitos
```bash
Python 3.8+
pip install flask reportlab  # Opcionales pero recomendados
```

### Instalación básica
```bash
# Clonar o descargar el archivo
python offer_letter_api.py
```

## 🎯 Uso Rápido

### 1. Iniciar servidor
```bash
python offer_letter_api.py server
```

### 2. Registrar usuario
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "password": "secure_password"
  }'
```

### 3. Autenticar
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "secure_password"
  }'
```

### 4. Crear oferta
```bash
curl -X POST http://localhost:5000/api/offers \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "candidate_name": "Juan Pérez",
    "candidate_email": "juan@example.com",
    "position_title": "Desarrollador Senior",
    "department": "Tecnología",
    "start_date": "2024-02-01",
    "salary": 85000,
    "currency": "USD",
    "benefits": ["Seguro médico", "Vacaciones"],
    "company_name": "Tech Solutions"
  }'
```

## 📚 Documentación

### Endpoints Principales

#### Autenticación
- `POST /api/auth/register` - Registrar usuario
- `POST /api/auth/login` - Autenticar
- `POST /api/auth/verify` - Verificar token

#### Ofertas
- `POST /api/offers` - Crear oferta
- `GET /api/offers` - Listar ofertas
- `GET /api/offers/<id>` - Obtener oferta
- `PUT /api/offers/<id>/status` - Actualizar estado
- `GET /api/offers/<id>/pdf` - Descargar PDF
- `GET /api/offers/<id>/word` - Descargar Word
- `POST /api/offers/<id>/sign` - Firmar digitalmente

#### Analytics
- `GET /api/analytics/acceptance-rate` - Tasa de aceptación
- `GET /api/analytics/salary-trends` - Tendencias salariales
- `GET /api/analytics/time-to-acceptance` - Tiempo hasta aceptación

#### Exportación
- `GET /api/export/csv` - Exportar a CSV
- `GET /api/export/excel` - Exportar a Excel
- `GET /api/export/statistics` - Exportar estadísticas

#### Notificaciones
- `GET /api/notifications` - Obtener notificaciones
- `PUT /api/notifications/<id>/read` - Marcar como leída

#### Sistema
- `GET /health` - Health check
- `GET /health/ready` - Readiness probe
- `GET /health/live` - Liveness probe
- `GET /api/metrics` - Métricas Prometheus
- `GET /api/docs` - Documentación OpenAPI
- `GET /api/docs/swagger` - Swagger UI

## ⚙️ Configuración

Crear archivo `config.json`:

```json
{
  "api": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  },
  "database": {
    "path": "offer_letters.db"
  },
  "cache": {
    "default_ttl": 300,
    "enabled": true
  },
  "rate_limit": {
    "max_requests": 60,
    "window_seconds": 60
  },
  "security": {
    "secret_key": "your-secret-key-here",
    "token_expiry": 3600
  }
}
```

## 🧪 Tests

Ejecutar suite completa de tests:

```bash
python offer_letter_api.py test
```

Tests incluidos:
- ✅ Validación de ofertas
- ✅ Generación de documentos
- ✅ API de creación
- ✅ Validación de esquema
- ✅ Sistema de caché
- ✅ Rate limiting
- ✅ Exportación
- ✅ Autenticación

## 📊 Métricas y Monitoreo

### Prometheus
```bash
curl http://localhost:5000/api/metrics
```

### Performance Stats
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/performance/stats
```

## 🔒 Seguridad

- Usar variable de entorno `SECRET_KEY` para producción
- Cambiar contraseñas por defecto
- Configurar rate limiting según necesidades
- Habilitar HTTPS en producción

## 🐳 Docker (Ejemplo)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY offer_letter_api.py .
RUN pip install flask reportlab
EXPOSE 5000
CMD ["python", "offer_letter_api.py", "server"]
```

## 📈 Estadísticas del Proyecto

- **Líneas de código**: ~3,000+
- **Endpoints API**: 35+
- **Clases principales**: 20+
- **Managers**: 12+
- **Formatos soportados**: 7
- **Idiomas**: 4
- **Tests**: 8+

## 🤝 Contribuciones

Este es un sistema completo y funcional. Para mejoras:
1. Revisar código existente
2. Agregar tests
3. Documentar cambios
4. Mantener compatibilidad

## 📝 Licencia

Sistema de código abierto para uso empresarial.

## 🆘 Soporte

Para problemas o preguntas:
- Revisar documentación en `/api/docs/swagger`
- Verificar logs en `./logs/`
- Ejecutar tests: `python offer_letter_api.py test`

---

**Versión**: 3.0  
**Última actualización**: 2024
