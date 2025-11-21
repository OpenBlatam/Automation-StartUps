# 🚀 Guía de Deployment del Sistema de Soporte

## 📋 Pre-requisitos

### Software Requerido
- PostgreSQL 12+
- Python 3.11+
- Kubernetes (opcional, para Kestra)
- Airflow 2.0+ (opcional)
- Next.js (opcional, para API REST)

### Permisos Requeridos
- Acceso a base de datos PostgreSQL
- Permisos para crear tablas e índices
- Permisos para ejecutar scripts Python

## 🚀 Deployment Automatizado

### Script de Deployment

**Archivo**: `scripts/support_deploy.sh`

Ejecuta automáticamente:
1. Creación de esquemas de BD
2. Carga de FAQs de ejemplo
3. Configuración de agentes y reglas
4. Health check del sistema
5. Verificación de workflows

### Uso

```bash
# Configurar variables de entorno
export DB_HOST=localhost
export DB_NAME=support_db
export DB_USER=postgres
export DB_PASSWORD=your_password
export ENVIRONMENT=prod

# Ejecutar deployment
./scripts/support_deploy.sh
```

## 📊 Deployment Manual

### Paso 1: Base de Datos

```bash
# Crear esquemas
psql -U postgres -d support_db -f data/db/support_tickets_schema.sql
psql -U postgres -d support_db -f data/db/support_feedback_schema.sql

# Cargar FAQs
psql -U postgres -d support_db -f data/db/support_faq_seed.sql

# Verificar
psql -U postgres -d support_db -c "\dt support_*"
```

### Paso 2: Configurar Agentes

```bash
export DB_HOST=localhost
export DB_NAME=support_db
export DB_USER=postgres
export DB_PASSWORD=your_password

python3 scripts/support_setup_example.py
```

### Paso 3: Health Check

```bash
python3 scripts/support_health_check.py
```

### Paso 4: Configurar Kestra

**Variables requeridas en Kestra:**

```yaml
# Base de datos
jdbc_url: "jdbc:postgresql://postgres.example.com:5432/support_db"
jdbc_user: "support_user"
jdbc_password: "secure_password"

# Chatbot (opcional)
openai_api_key: "sk-..."
openai_model: "gpt-4o-mini"
enable_chatbot: true
chatbot_confidence_threshold: 0.7

# Notificaciones
slack_webhook_url: "https://hooks.slack.com/services/..."
enable_notifications: true
```

**Subir workflows:**

```bash
# Usando Kestra CLI
kestra workflow push workflow/kestra/flows/support_ticket_automation.yaml
kestra workflow push workflow/kestra/flows/support_ticket_escalation.yaml
kestra workflow push workflow/kestra/flows/support_feedback_collection.yaml
```

### Paso 5: Configurar Airflow

**Variables de entorno:**

```bash
# Connection
airflow connections add postgres_default \
  --conn-type postgres \
  --conn-host postgres.example.com \
  --conn-port 5432 \
  --conn-login support_user \
  --conn-password secure_password \
  --conn-schema support_db

# Variables
airflow variables set SLACK_WEBHOOK_URL "https://hooks.slack.com/services/..."
airflow variables set SUPPORT_REPORT_RECIPIENTS "team@example.com,manager@example.com"
```

**Verificar DAGs:**

```bash
airflow dags list | grep support
```

### Paso 6: Configurar API REST (Next.js)

**Variables de entorno:**

```bash
DATABASE_URL="postgresql://support_user:password@postgres.example.com:5432/support_db"
KESTRA_WEBHOOK_URL="https://kestra.example.com/api/v1/executions/webhook"
```

**Verificar endpoints:**

```bash
curl http://localhost:3000/api/support/tickets/stats
```

## 🔍 Post-Deployment

### Verificaciones

1. **Health Check**
   ```bash
   python3 scripts/support_health_check.py
   ```

2. **Probar Creación de Ticket**
   ```bash
   curl -X POST http://localhost:3000/api/support/tickets \
     -H "Content-Type: application/json" \
     -d '{
       "subject": "Test ticket",
       "description": "This is a test",
       "customer_email": "test@example.com"
     }'
   ```

3. **Verificar Monitoreo**
   ```bash
   # Verificar DAG de monitoreo
   airflow dags list-runs -d support_tickets_monitor
   ```

4. **Verificar Workflows**
   ```bash
   # En UI de Kestra, verificar que workflows están activos
   ```

## 🔧 Configuración por Ambiente

### Desarrollo

```bash
export ENVIRONMENT=dev
export DB_HOST=localhost
export DB_NAME=support_dev
export OPENAI_API_KEY=""  # Opcional en dev
```

### Staging

```bash
export ENVIRONMENT=stg
export DB_HOST=postgres-stg.example.com
export DB_NAME=support_staging
export OPENAI_API_KEY="sk-..."
```

### Producción

```bash
export ENVIRONMENT=prod
export DB_HOST=postgres-prod.example.com
export DB_NAME=support_production
export OPENAI_API_KEY="sk-..."
# Usar secrets management (Vault, AWS Secrets Manager, etc.)
```

## 🔄 CI/CD

### GitHub Actions

El workflow `.github/workflows/support-system-ci.yml` ejecuta:
- Tests unitarios
- Linting
- Validación de YAML
- Health check

### Pipeline de Deployment

```yaml
# Ejemplo para GitLab CI, Jenkins, etc.
stages:
  - test
  - deploy

test:
  script:
    - pytest workflow/kestra/flows/lib/tests/
    - python3 scripts/support_health_check.py

deploy:
  script:
    - ./scripts/support_deploy.sh
  only:
    - main
```

## 📊 Monitoreo Post-Deployment

### Métricas a Monitorear

1. **Tasa de Resolución por Chatbot**
   ```sql
   SELECT 
       COUNT(*) FILTER (WHERE chatbot_resolved = true)::float / 
       NULLIF(COUNT(*) FILTER (WHERE chatbot_attempted = true), 0) * 100 as rate
   FROM support_tickets
   WHERE created_at >= NOW() - INTERVAL '24 hours';
   ```

2. **Tickets Pendientes**
   ```sql
   SELECT COUNT(*) FROM support_tickets
   WHERE status IN ('open', 'assigned', 'in_progress');
   ```

3. **SLA Compliance**
   ```sql
   SELECT COUNT(*) FROM support_tickets
   WHERE priority IN ('critical', 'urgent')
   AND status NOT IN ('resolved', 'closed')
   AND created_at < NOW() - INTERVAL '1 hour';
   ```

### Alertas Recomendadas

- Tasa de chatbot < 40%
- Tickets críticos sin respuesta > 30 min
- > 50 tickets pendientes
- Tiempo promedio de respuesta > 2 horas

## 🛠️ Troubleshooting

### Problemas Comunes

1. **Error de conexión a BD**
   - Verificar credenciales
   - Verificar que PostgreSQL está corriendo
   - Verificar firewall/red

2. **Workflows de Kestra no se ejecutan**
   - Verificar que workflows están activos
   - Verificar webhook URL
   - Revisar logs de Kestra

3. **DAGs de Airflow fallan**
   - Verificar connection a BD
   - Verificar variables de entorno
   - Revisar logs de Airflow

4. **API REST no responde**
   - Verificar DATABASE_URL
   - Verificar que Next.js está corriendo
   - Revisar logs de la aplicación

## 📚 Recursos

- [Quick Start Guide](SUPPORT_AUTOMATION_QUICK_START.md)
- [Documentación Completa](README_SUPPORT_AUTOMATION.md)
- [Guía de Mejoras](README_SUPPORT_IMPROVEMENTS.md)

