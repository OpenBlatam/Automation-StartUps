# 🚀 Mejoras Avanzadas: API REST, Notificaciones y Versionado

> **Versión**: 2.2 | **Fecha**: 2024

Mejoras avanzadas implementadas para el sistema de descripciones de puesto.

---

## ✨ Nuevas Funcionalidades

### 1. API REST Completa

**Endpoints Disponibles:**

#### Descripciones
- `GET /api/job-descriptions` - Listar descripciones
- `POST /api/job-descriptions` - Crear nueva descripción
- `GET /api/job-descriptions/{id}` - Obtener descripción específica
- `PUT /api/job-descriptions/{id}` - Actualizar descripción

#### Analytics y Optimización
- `GET /api/job-descriptions/{id}/analytics` - Obtener analytics
- `POST /api/job-descriptions/{id}/optimize` - Optimizar descripción
- `POST /api/job-descriptions/{id}/variants` - Generar variantes

#### Templates
- `GET /api/templates` - Listar templates disponibles

#### Health
- `GET /api/health` - Health check del API

**Ejemplo de Uso:**
```bash
# Listar descripciones
curl http://localhost:5000/api/job-descriptions

# Crear nueva descripción
curl -X POST http://localhost:5000/api/job-descriptions \
  -H "Content-Type: application/json" \
  -d '{
    "role": "ML Engineer",
    "level": "Senior",
    "industry": "fintech"
  }'

# Obtener analytics
curl http://localhost:5000/api/job-descriptions/123/analytics

# Optimizar descripción
curl -X POST http://localhost:5000/api/job-descriptions/123/optimize
```

**Configuración:**
```bash
airflow variables set JOB_DESCRIPTION_API_PORT 5000
airflow variables set JOB_DESCRIPTION_API_HOST "0.0.0.0"
```

---

### 2. Sistema de Notificaciones Avanzado

**Canales Soportados:**

#### Email
- ✅ SendGrid
- ✅ SMTP genérico
- ✅ HTML y texto plano
- ✅ Múltiples destinatarios

**Configuración:**
```bash
airflow variables set EMAIL_API_KEY "sg-..."
airflow variables set EMAIL_SERVICE "sendgrid"
airflow variables set EMAIL_FROM "noreply@empresa.com"
```

#### Slack
- ✅ Webhooks
- ✅ Canales personalizados
- ✅ Attachments con formato
- ✅ Colores por tipo de notificación

**Configuración:**
```bash
airflow variables set SLACK_WEBHOOK_URL "https://hooks.slack.com/services/..."
```

#### Webhooks Personalizados
- ✅ URLs personalizadas
- ✅ Headers configurables
- ✅ Payload JSON personalizado

**Eventos Notificados:**
- ✅ Nueva descripción creada
- ✅ Descripción publicada
- ✅ Nueva aplicación recibida
- ✅ Aplicación calificada
- ✅ Optimización completada

**Ejemplo de Notificación:**
```python
# Slack notification
{
    "channel": "#hr-notifications",
    "message": "✅ Nueva descripción: ML Engineer",
    "attachments": [{
        "color": "good",
        "fields": [
            {"title": "Rol", "value": "ML Engineer", "short": True},
            {"title": "Nivel", "value": "Senior", "short": True}
        ]
    }]
}
```

---

### 3. Sistema de Versionado

**Características:**
- ✅ Historial completo de versiones
- ✅ Comparación entre versiones
- ✅ Rollback a versiones anteriores
- ✅ Diferencias visuales (unified diff)
- ✅ Notas por versión

**Operaciones:**

#### Crear Versión
```bash
airflow dags trigger job_description_versioning \
  --conf '{
    "job_description_id": 123,
    "version_notes": "Actualización de beneficios"
  }'
```

#### Comparar Versiones
```bash
airflow dags trigger job_description_versioning \
  --conf '{
    "job_description_id": 123,
    "version1": 1,
    "version2": 2
  }'
```

#### Rollback
```bash
airflow dags trigger job_description_versioning \
  --conf '{
    "job_description_id": 123,
    "target_version": 2
  }'
```

**Vista SQL:**
```sql
-- Ver versiones recientes
SELECT * FROM recent_versions LIMIT 10;

-- Comparar versiones
SELECT 
    v1.version_number as v1,
    v2.version_number as v2,
    v1.description as desc_v1,
    v2.description as desc_v2
FROM job_description_versions v1
JOIN job_description_versions v2 
    ON v1.job_description_id = v2.job_description_id
WHERE v1.job_description_id = 123
    AND v1.version_number = 1
    AND v2.version_number = 2;
```

---

## 📊 Integraciones

### Integración con Sistemas Externos

**Webhooks:**
```python
# Configurar webhook para notificaciones
webhook_config = {
    "webhook_url": "https://api.empresa.com/webhooks/job-descriptions",
    "payload": {
        "event": "description_created",
        "job_description_id": 123,
        "role": "ML Engineer"
    },
    "headers": {
        "Authorization": "Bearer token",
        "Content-Type": "application/json"
    }
}
```

**API Externa:**
```python
# Llamar API desde otro sistema
import requests

response = requests.post(
    "http://airflow:5000/api/job-descriptions",
    json={
        "role": "Data Scientist",
        "level": "Mid",
        "industry": "healthcare"
    }
)
```

---

## 🔧 Configuración Completa

### Variables de Airflow Requeridas

```bash
# API
airflow variables set JOB_DESCRIPTION_API_PORT 5000
airflow variables set JOB_DESCRIPTION_API_HOST "0.0.0.0"

# Email
airflow variables set EMAIL_API_KEY "sg-..."
airflow variables set EMAIL_SERVICE "sendgrid"
airflow variables set EMAIL_FROM "noreply@empresa.com"

# Slack
airflow variables set SLACK_WEBHOOK_URL "https://hooks.slack.com/services/..."

# HR Team
airflow variables set HR_TEAM_EMAIL "hr@empresa.com"
```

### Esquemas SQL

```bash
# Ejecutar todos los schemas
psql -d tu_base_de_datos -f data/db/schema/job_descriptions.sql
psql -d tu_base_de_datos -f data/db/schema/job_descriptions_optimization.sql
psql -d tu_base_de_datos -f data/db/schema/job_description_templates.sql
psql -d tu_base_de_datos -f data/db/schema/job_descriptions_versioning.sql
```

---

## 📈 Casos de Uso Avanzados

### Caso 1: Integración con ATS

```python
# Cuando se crea una nueva descripción en el ATS
import requests

# Crear descripción vía API
response = requests.post(
    "http://airflow:5000/api/job-descriptions",
    json={
        "role": "ML Engineer",
        "level": "Senior",
        "department": "Engineering"
    }
)

# Obtener ID de la descripción generada
job_id = response.json()['data']['id']

# Publicar automáticamente
requests.post(f"http://airflow:5000/api/job-descriptions/{job_id}/publish")
```

### Caso 2: Pipeline Completo con Notificaciones

1. Generar descripción → Notificación a Slack
2. Optimizar → Notificación por email
3. Publicar → Notificación a webhook externo
4. Recibir aplicación → Notificación a Slack #hr-applications

### Caso 3: Versionado y Rollback

1. Crear versión inicial
2. Hacer cambios
3. Crear nueva versión
4. Comparar versiones
5. Si hay problemas, hacer rollback

---

## 🎯 Métricas y Monitoreo

### Health Check del API

```bash
curl http://localhost:5000/api/health
```

**Respuesta:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00"
}
```

### Monitoreo de Notificaciones

```sql
-- Ver notificaciones enviadas (si se guardan en BD)
SELECT 
    notification_type,
    COUNT(*) as total,
    COUNT(CASE WHEN status = 'success' THEN 1 END) as successful,
    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed
FROM notifications_log
WHERE created_at > NOW() - INTERVAL '7 days'
GROUP BY notification_type;
```

---

## 🚀 Próximas Mejoras Sugeridas

1. **Dashboard Web**
   - Interfaz visual para gestionar descripciones
   - Visualización de analytics
   - Comparación de variantes

2. **Autenticación y Autorización**
   - JWT tokens
   - Roles y permisos
   - Rate limiting

3. **Exportación de Reportes**
   - PDF de descripciones
   - Excel con analytics
   - Reportes programados

4. **Sistema de Aprobación**
   - Workflow de revisión
   - Aprobaciones múltiples
   - Comentarios y feedback

5. **Integración con Más Portales**
   - LinkedIn Jobs API
   - Indeed API
   - Glassdoor API
   - Portales locales

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Crear Descripción vía API

```bash
curl -X POST http://localhost:5000/api/job-descriptions \
  -H "Content-Type: application/json" \
  -d '{
    "role": "MLOps Engineer",
    "level": "Senior",
    "industry": "saas",
    "ai_experience_years": 4,
    "skills": ["Python", "Kubernetes", "MLflow"],
    "location": "Remoto"
  }'
```

### Ejemplo 2: Obtener Analytics

```bash
curl http://localhost:5000/api/job-descriptions/123/analytics
```

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "sentiment": {
      "score": 0.45,
      "category": "muy_positivo"
    },
    "keywords": [...],
    "performance": {
      "postings_count": 3,
      "applications_count": 15,
      "avg_application_score": 78.5,
      "qualified_count": 8
    }
  }
}
```

### Ejemplo 3: Generar Variantes

```bash
curl -X POST http://localhost:5000/api/job-descriptions/123/variants \
  -H "Content-Type: application/json" \
  -d '{"num_variants": 3}'
```

---

**Última actualización**: 2024  
**Versión**: 2.2  
**Mantenido por**: Platform Team






