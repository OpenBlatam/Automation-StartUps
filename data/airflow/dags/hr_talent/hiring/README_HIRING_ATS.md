# Sistema ATS (Applicant Tracking System) - Guía Completa

## 📋 Descripción

Sistema completo de reclutamiento automatizado que publica vacantes en múltiples plataformas, filtra CVs, programa entrevistas, envía tests y mantiene comunicación con candidatos.

## 🚀 Características Principales

### ✅ Publicación de Vacantes
- **Publicación simultánea** en múltiples plataformas:
  - Greenhouse
  - LinkedIn
  - Indeed
  - Glassdoor
  - Monster
  - Plataformas personalizadas
- Tracking de estado por plataforma
- Manejo robusto de errores y retries

### ✅ Filtrado Automático de CVs
- **Filtrado por palabras clave** con scoring inteligente
- Análisis de CV y carta de presentación
- Threshold configurable (default: 50%)
- Tracking de keywords encontradas
- Score de matching (0-100)

### ✅ Programación Automática de Entrevistas
- **Integración con calendarios** (Google Calendar, Outlook)
- Detección automática de disponibilidad
- Creación automática de eventos de calendario
- Generación de links de reunión (Zoom, Google Meet)
- Recordatorios automáticos

### ✅ Tests de Evaluación
- **Múltiples plataformas**:
  - HackerRank (coding tests)
  - Codility (technical assessments)
  - Tests internos personalizados
- Envío automático con links únicos
- Tracking de completación y scores
- Notificaciones de vencimiento

### ✅ Comunicación con Candidatos
- **Múltiples canales**:
  - Email (SMTP, SendGrid, etc.)
  - SMS (Twilio)
  - WhatsApp (futuro)
- Templates personalizables
- Tracking de entregas y lecturas
- Historial completo de comunicaciones

### ✅ Sincronización con ATS Externos
- **Greenhouse** (bidireccional)
- Lever (futuro)
- Workday Recruiting (futuro)
- Sincronización automática de:
  - Vacantes
  - Candidatos
  - Aplicaciones
  - Entrevistas

## 📊 Estructura de Base de Datos

### Tablas Principales

1. **ats_job_postings**: Vacantes/job postings
2. **ats_job_platforms**: Plataformas donde se publican las vacantes
3. **ats_candidates**: Candidatos
4. **ats_applications**: Aplicaciones (candidato + vacante)
5. **ats_cv_filtering**: Resultados de filtrado de CVs
6. **ats_interviews**: Entrevistas programadas
7. **ats_assessment_tests**: Tests de evaluación
8. **ats_communications**: Comunicaciones con candidatos
9. **ats_external_sync**: Sincronización con ATS externos
10. **ats_filter_rules**: Reglas de filtrado configurables
11. **ats_communication_templates**: Templates de comunicación

### Vista de Estadísticas

- **ats_hiring_stats**: Vista agregada con métricas de hiring por vacante

## 🔧 Configuración

### Variables de Entorno Requeridas

#### Plataformas de Job Posting
```bash
# Greenhouse
GREENHOUSE_API_KEY=your_api_key
GREENHOUSE_API_URL=https://api.greenhouse.io/v1
GREENHOUSE_BOARD_TOKEN=your_board_token
GREENHOUSE_ENABLED=true

# LinkedIn
LINKEDIN_ACCESS_TOKEN=your_access_token
LINKEDIN_API_URL=https://api.linkedin.com/v2
LINKEDIN_ORG_ID=your_org_id

# Indeed
INDEED_PUBLISHER_ID=your_publisher_id
INDEED_API_KEY=your_api_key
```

#### Calendarios y Reuniones
```bash
# Google Calendar / Outlook
CALENDAR_API_URL=https://api.calendar.com
CALENDAR_API_KEY=your_api_key

# Zoom
ZOOM_API_KEY=your_api_key
ZOOM_API_SECRET=your_api_secret
ZOOM_ACCESS_TOKEN=your_access_token
```

#### Comunicaciones
```bash
# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_PHONE_NUMBER=+1234567890
```

#### Tests de Evaluación
```bash
# HackerRank
HACKERRANK_API_KEY=your_api_key
HACKERRANK_API_URL=https://www.hackerrank.com/x/api/v3

# Codility
CODILITY_API_KEY=your_api_key
CODILITY_API_URL=https://api.codility.com
```

#### Configuración General
```bash
# Threshold para filtrado de CVs (porcentaje)
ATS_KEYWORD_THRESHOLD=50.0

# Pool de ejecución
HIRING_POOL=etl_pool
MAX_ACTIVE_TASKS=32
```

## 📝 Uso del DAG

### DAG Principal: `hiring_ats`

**Trigger manual** con parámetros:

```python
{
    "job_id": "backend-engineer-2024",
    "title": "Senior Backend Engineer",
    "description": "We are looking for an experienced backend engineer...",
    "requirements": "5+ years of experience with Python, PostgreSQL...",
    "keywords": ["python", "postgresql", "aws", "docker", "kubernetes"],
    "platforms": ["greenhouse", "linkedin", "indeed"],
    "department": "Engineering",
    "location": "Remote",
    "employment_type": "full_time",
    "remote_type": "remote",
    "hiring_manager_email": "hiring@company.com",
    "recruiter_email": "recruiter@company.com"
}
```

### DAG Automático: `hiring_process_applications`

**Ejecución automática cada 2 horas** para:
- Procesar nuevas aplicaciones
- Filtrar CVs automáticamente
- Actualizar scores de matching

## 🔄 Flujo del Proceso

```
1. Publicación de Vacante
   ↓
2. Recepción de Aplicaciones
   ↓
3. Filtrado Automático de CVs
   ├─ Análisis por keywords
   ├─ Cálculo de match score
   └─ Decisión: Pass/Fail
   ↓
4. Programación de Entrevistas
   ├─ Buscar disponibilidad
   ├─ Crear evento en calendario
   └─ Generar meeting link
   ↓
5. Envío de Tests
   ├─ Determinar tipo de test
   ├─ Crear test en plataforma
   └─ Enviar email al candidato
   ↓
6. Comunicación Continua
   ├─ Confirmaciones
   ├─ Recordatorios
   └─ Updates de estado
   ↓
7. Sincronización con ATS Externos
   └─ Bidireccional con Greenhouse
```

## 📈 Métricas y Analytics

### Vista `ats_hiring_stats`

Proporciona métricas agregadas por vacante:
- Total de aplicaciones
- Candidatos contratados
- En entrevistas
- Con ofertas
- Rechazados
- Score promedio de matching
- Total de entrevistas
- Total de tests

### Consultas Útiles

```sql
-- Aplicaciones por estado
SELECT status, COUNT(*) 
FROM ats_applications 
WHERE job_id = 'backend-engineer-2024'
GROUP BY status;

-- Top candidatos por match score
SELECT c.first_name, c.last_name, a.match_score, a.status
FROM ats_applications a
JOIN ats_candidates c ON a.candidate_id = c.candidate_id
WHERE a.job_id = 'backend-engineer-2024'
ORDER BY a.match_score DESC
LIMIT 10;

-- Entrevistas próximas
SELECT i.interview_id, c.first_name, c.last_name, 
       i.scheduled_start, i.interview_type
FROM ats_interviews i
JOIN ats_applications a ON i.application_id = a.application_id
JOIN ats_candidates c ON a.candidate_id = c.candidate_id
WHERE i.status = 'scheduled'
  AND i.scheduled_start > NOW()
ORDER BY i.scheduled_start
LIMIT 20;
```

## 🔌 Integraciones

### Greenhouse

**Sincronización bidireccional:**
- Vacantes: inbound/outbound
- Candidatos: inbound/outbound
- Aplicaciones: inbound/outbound
- Entrevistas: inbound/outbound

**Configuración:**
```python
# Habilitar en variables de entorno
GREENHOUSE_ENABLED=true
GREENHOUSE_API_KEY=your_key
```

### LinkedIn

**Publicación de vacantes:**
- Requiere organización ID
- Soporta múltiples ubicaciones
- Tipos de empleo: full-time, part-time, contract

### Indeed

**Publicación de vacantes:**
- Requiere publisher ID y API key
- Tracking de aplicaciones
- Analytics de performance

## 🛠️ Desarrollo

### Estructura de Archivos

```
data/
├── db/
│   └── ats_schema.sql              # Schema de base de datos
├── airflow/
│   ├── dags/
│   │   ├── hiring_ats.py            # DAG principal
│   │   └── README_HIRING_ATS.md    # Esta documentación
│   └── plugins/
│       └── hiring_integrations.py  # Funciones de integración
```

### Agregar Nueva Plataforma

1. Agregar enum en `Platform`:
```python
class Platform(Enum):
    NEW_PLATFORM = "new_platform"
```

2. Implementar función `_publish_to_new_platform()`:
```python
def _publish_to_new_platform(job_id: str, job_data: Dict[str, Any]) -> Dict[str, Any]:
    # Implementación
    return {"success": True, "platform_job_id": "...", ...}
```

3. Agregar case en `_publish_to_platform()`:
```python
elif platform == Platform.NEW_PLATFORM:
    return _publish_to_new_platform(job_id, job_data)
```

### Agregar Nuevo Tipo de Test

1. Agregar enum en `TestType`:
```python
class TestType(Enum):
    NEW_TEST = "new_test"
```

2. Implementar función `_create_new_test_platform()`:
```python
def _create_new_test_platform(...) -> Tuple[str, str]:
    # Implementación
    return (test_url, instructions)
```

## 🧪 Testing

### Pruebas Locales

```python
# Ejecutar filtrado de CV
from data.airflow.plugins.hiring_integrations import filter_cv_by_keywords

result = filter_cv_by_keywords(
    application_id="app_123",
    resume_text="Python developer with 5 years experience...",
    keywords=["python", "postgresql", "aws"],
    cover_letter="I am excited to apply..."
)

print(f"Match score: {result['match_score']}")
print(f"Passed: {result['passed']}")
```

## 📚 Recursos Adicionales

- [Greenhouse API Documentation](https://developers.greenhouse.io/job-board.html)
- [LinkedIn Job Posting API](https://docs.microsoft.com/en-us/linkedin/talent/job-posting-api)
- [Indeed API](https://ads.indeed.com/jobroll/xmlfeed)
- [HackerRank API](https://www.hackerrank.com/api/docs)
- [Codility API](https://support.codility.com/hc/en-us/articles/213146205-REST-API)

## 🐛 Troubleshooting

### Error: "API key not configured"
- Verificar variables de entorno
- Verificar conexión a Vault (si se usa)

### Error: "No available slots for interviewer"
- Verificar integración con calendario
- Verificar formato de email del entrevistador
- Revisar logs para detalles

### Error: "Failed to publish job to any platform"
- Verificar credenciales de cada plataforma
- Verificar conectividad de red
- Revisar logs específicos por plataforma

## 📝 Notas

- El sistema usa **idempotencia** para evitar duplicados
- Los **retries** están configurados con backoff exponencial
- Las **comunicaciones** se guardan en BD para auditoría
- Los **scores de matching** se actualizan automáticamente
- La **sincronización** con ATS externos es opcional

## 🔐 Seguridad

- Las credenciales se almacenan en variables de entorno o Vault
- Las conexiones a BD usan conexiones seguras
- Los datos sensibles se enmascaran en logs
- Las comunicaciones usan TLS/SSL

## 🚀 Funcionalidades Extendidas

### 🤖 Chatbot para Candidatos
- Respuestas automáticas sobre estado de aplicación
- Información sobre entrevistas y tests
- Soporte 24/7
- Integración con base de datos

### 🔍 Background Checks Automatizados
- Integración con Checkr, Sterling, HireRight
- Tracking completo del proceso
- Resultados automatizados
- Tabla `ats_background_checks` para gestión

### 📊 Análisis Predictivo
- Predicción de abandono del proceso
- Factores de riesgo identificados
- Recomendaciones automáticas
- Alertas proactivas

### 🔄 Integraciones Extendidas
- **Workday Recruiting**: Sincronización bidireccional
- **Lever ATS**: Integración completa
- **Payroll/HRIS**: Sincronización post-hire
- **Webhooks**: Integraciones personalizadas

### 📈 Dashboard en Tiempo Real
- Vista `ats_dashboard_realtime` agregada
- Métricas actualizadas constantemente
- Alertas automáticas
- KPIs clave visibles

### 🎯 Sistema de Evaluación por Etapas
- Scoring progresivo por etapa
- Criterios configurables
- Tracking detallado
- Tabla `ats_evaluation_stages`

## 📁 Archivos Adicionales

### Nuevos Archivos Creados
1. `data/airflow/plugins/hiring_advanced.py` - Funcionalidades avanzadas (ML, workflows, feedback)
2. `data/airflow/plugins/hiring_extended.py` - Funcionalidades extendidas (chatbot, background checks, integraciones)
3. `data/airflow/dags/hiring_workflows_automation.py` - DAG de workflows automáticos
4. `data/airflow/dags/hiring_extended_automation.py` - DAG de automatizaciones extendidas
5. `data/db/ats_extended_schema.sql` - Schema extendido (8 nuevas tablas)
6. `data/db/ats_templates_seed.sql` - Templates de comunicación

### Tablas Adicionales
- `ats_ml_scoring` - Scoring avanzado con ML
- `ats_workflows` - Workflows automáticos
- `ats_workflow_executions` - Ejecuciones de workflows
- `ats_referrals` - Sistema de referidos
- `ats_feedback` - Feedback avanzado
- `ats_analytics` - Analytics y métricas
- `ats_post_hire_onboarding` - Onboarding post-hire
- `ats_chatbot_sessions` - Sesiones de chatbot
- `ats_background_checks` - Background checks
- `ats_evaluation_stages` - Etapas de evaluación
- `ats_realtime_metrics` - Métricas en tiempo real
- `ats_payroll_sync` - Sincronización con payroll
- `ats_alerts` - Sistema de alertas
- `ats_webhooks` - Webhooks para integraciones
- `ats_webhook_logs` - Logs de webhooks

## 🔧 Configuración Adicional

### Variables de Entorno para Funcionalidades Extendidas

```bash
# Background Checks
CHECKR_API_KEY=your_checkr_key
STERLING_API_KEY=your_sterling_key
HIRERIGHT_API_KEY=your_hireright_key

# Integraciones
WORKDAY_API_URL=https://api.workday.com
WORKDAY_USERNAME=your_username
WORKDAY_PASSWORD=your_password
WORKDAY_TENANT=your_tenant

LEVER_API_KEY=your_lever_key
LEVER_SITE=your_lever_site

# Payroll/HRIS
PAYROLL_API_URL=https://api.payroll.com
PAYROLL_API_KEY=your_payroll_key

# ML Model (opcional)
ATS_ML_MODEL_ENDPOINT=https://ml-api.company.com/predict
```

## 📊 DAGs Disponibles

1. **hiring_ats** - DAG principal (trigger manual)
2. **hiring_process_applications** - Procesamiento continuo (cada 2 horas)
3. **hiring_workflows_automation** - Workflows automáticos (cada 4 horas)
4. **hiring_extended_automation** - Automatizaciones extendidas (cada 6 horas)

## 🎯 Uso del Chatbot

El chatbot puede responder preguntas sobre:
- Estado de aplicación
- Información de entrevistas
- Tests de evaluación
- Preguntas generales

Ejemplo de uso:
```python
from data.airflow.plugins.hiring_extended import process_chatbot_message

response = process_chatbot_message(
    candidate_id="candidate_123",
    message="¿Cuál es el estado de mi aplicación?",
    session_id="session_456"
)

print(response["response"])
```

## 🔍 Background Checks

Iniciar background check:
```python
from data.airflow.plugins.hiring_extended import initiate_background_check

result = initiate_background_check(
    candidate_id="candidate_123",
    check_type="standard",  # o "comprehensive"
    provider="checkr"  # o "sterling", "hireright"
)
```

## 📈 Análisis Predictivo

Predecir abandono:
```python
from data.airflow.plugins.hiring_extended import predict_process_abandonment

prediction = predict_process_abandonment("application_123")
print(f"Risk level: {prediction['risk_level']}")
print(f"Abandonment probability: {prediction['abandonment_probability']}%")
print(f"Recommendations: {prediction['recommendations']}")
```

## 🔄 Sincronización con Payroll

Sincronizar nuevo empleado:
```python
from data.airflow.plugins.hiring_extended import sync_new_hire_to_payroll

result = sync_new_hire_to_payroll(
    candidate_id="candidate_123",
    start_date="2024-02-01",
    salary=75000.00,
    department="Engineering"
)
```

## 📊 Dashboard en Tiempo Real

Consulta la vista para métricas en tiempo real:
```sql
SELECT * FROM ats_dashboard_realtime
WHERE job_status = 'active'
ORDER BY total_applications DESC;
```

## 🚨 Sistema de Alertas

Las alertas se generan automáticamente para:
- Tests expirando pronto
- Aplicaciones estancadas
- Riesgo de abandono alto
- Feedback faltante

Consultar alertas activas:
```sql
SELECT * FROM ats_alerts
WHERE status = 'active'
ORDER BY severity DESC, created_at DESC;
```

## 🔗 Webhooks

Configurar webhook:
```sql
INSERT INTO ats_webhooks
(webhook_id, webhook_url, event_type, secret_token, is_active)
VALUES (
    'webhook_123',
    'https://your-app.com/webhook',
    'candidate_hired',
    'your_secret_token',
    true
);
```

---

**Última actualización:** 2024
**Mantenido por:** HR & Engineering Team
**Versión:** 2.0 Extended

