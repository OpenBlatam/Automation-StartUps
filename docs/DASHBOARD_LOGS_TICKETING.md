# 🎨 Dashboard, Logs y Ticketing - Sistema de Backups

## Nuevas Funcionalidades Implementadas

### 1. 📊 Dashboard Web Interactivo (`backup_dashboard.py`)

Dashboard web completo para monitoreo visual:

```python
from data.airflow.plugins.backup_dashboard import create_backup_dashboard

# Crear dashboard
app = create_backup_dashboard(
    backup_dir="/tmp/backups",
    port=8080
)

# Ejecutar (ejemplo con Flask)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
```

**Características:**
- Visualización de métricas en tiempo real
- Estado del sistema
- Uso de disco
- Backups recientes
- Actualización automática cada 30 segundos
- Interfaz moderna y responsive

**Acceso:**
- URL: `http://localhost:8080`
- Endpoint de métricas: `GET /api/dashboard/metrics`

### 2. 📝 Backup de Logs (`backup_logs.py`)

Backup automático de logs y auditoría:

```python
from data.airflow.plugins.backup_logs import LogBackupManager

log_manager = LogBackupManager(backup_dir="/tmp/log-backups")

# Backup de logs de aplicaciones
app_logs = log_manager.backup_application_logs(
    log_paths=["/var/log/app1", "/var/log/app2"],
    app_name="production",
    retention_days=7
)

# Backup de logs del sistema
system_logs = log_manager.backup_system_logs()

# Backup de logs de auditoría
audit_logs = log_manager.backup_audit_logs(
    audit_log_path="/var/log/audit"
)

# Listar backups
backups = log_manager.list_log_backups(log_type='application', days=30)
```

**DAG Automático:**
- `log_backups`: Backups diarios de logs a las 4 AM
  - Logs de aplicaciones
  - Logs del sistema
  - Logs de auditoría

### 3. 🎫 Integración con Sistemas de Ticketing (`backup_ticketing.py`)

Integración con sistemas de ticketing profesionales:

#### Jira

```python
from data.airflow.plugins.backup_ticketing import (
    JiraIntegration,
    Ticket,
    TicketPriority
)

jira = JiraIntegration(
    url="https://company.atlassian.net",
    email="user@company.com",
    api_token="your-api-token"
)

ticket = Ticket(
    title="Backup Failed",
    description="Critical backup failed",
    priority=TicketPriority.HIGH,
    labels=["backup", "urgent"]
)

ticket_key = jira.create_ticket(ticket)
print(f"Created Jira ticket: {ticket_key}")
```

#### ServiceNow

```python
from data.airflow.plugins.backup_ticketing import ServiceNowIntegration

servicenow = ServiceNowIntegration(
    instance_url="https://company.service-now.com",
    username="user",
    password="password"
)

incident_number = servicenow.create_incident(ticket)
```

#### GitHub Issues

```python
from data.airflow.plugins.backup_ticketing import GitHubIssuesIntegration

github = GitHubIssuesIntegration(
    repo="company/backups",
    token="ghp_..."
)

issue_number = github.create_issue(ticket)
```

#### Gestor Multi-Plataforma

```python
from data.airflow.plugins.backup_ticketing import TicketingManager

ticketing = TicketingManager()

# Crear ticket por fallo de backup
results = ticketing.create_backup_failure_ticket(
    backup_id="backup-123",
    error="Connection timeout",
    details={"database": "prod_db"},
    platforms=['jira', 'servicenow']  # None = todas configuradas
)

# Resultados:
# {
#     'jira': 'BACKUP-123',
#     'servicenow': 'INC0012345'
# }
```

## Configuración

### Variables de Entorno

```bash
# Dashboard
export BACKUP_DIR="/var/backups"

# Logs
export LOG_BACKUP_DIR="/var/log-backups"
export APP_LOG_PATHS="/var/log/app1,/var/log/app2"
export AUDIT_LOG_PATH="/var/log/audit"

# Jira
export JIRA_URL="https://company.atlassian.net"
export JIRA_EMAIL="user@company.com"
export JIRA_API_TOKEN="your-api-token"
export JIRA_PROJECT_KEY="BACKUP"

# ServiceNow
export SERVICENOW_INSTANCE_URL="https://company.service-now.com"
export SERVICENOW_USERNAME="user"
export SERVICENOW_PASSWORD="password"

# GitHub
export GITHUB_REPO="owner/repo"
export GITHUB_TOKEN="ghp_..."
```

## Uso en DAGs

### Dashboard como Servicio

```python
# En un script separado o como servicio
from data.airflow.plugins.backup_dashboard import create_backup_dashboard

app = create_backup_dashboard(port=8080)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### Ticketing Automático

```python
@task
def backup_with_ticketing():
    """Backup con creación automática de tickets en caso de fallo."""
    manager = BackupManager(...)
    result = manager.backup_database(...)
    
    if result.status.value == 'failed':
        # Crear ticket automáticamente
        ticketing = TicketingManager()
        tickets = ticketing.create_backup_failure_ticket(
            backup_id=result.backup_id,
            error=result.error
        )
        logger.info(f"Created tickets: {tickets}")
    
    return result
```

## Beneficios

1. **Dashboard Visual** - Monitoreo en tiempo real
2. **Backup de Logs** - Protección de auditoría
3. **Ticketing Automático** - Gestión de incidentes
4. **Integración Completa** - Múltiples plataformas

## Ejecutar Dashboard

### Desarrollo

```bash
python -m data.airflow.plugins.backup_dashboard
```

### Producción (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:8080 \
  --timeout 120 \
  backup_dashboard:app
```

### Docker

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "backup_dashboard:app"]
```

## Próximos Pasos

1. Configurar credenciales de sistemas de ticketing
2. Desplegar dashboard web
3. Configurar rutas de logs
4. Integrar ticketing en DAGs críticos

¡Sistema completo con dashboard, logs y ticketing! 🚀

