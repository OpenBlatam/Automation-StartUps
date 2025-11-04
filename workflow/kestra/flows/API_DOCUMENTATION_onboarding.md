# 📚 API Documentation - Employee Onboarding

Documentación completa de la API del flujo de onboarding.

## Endpoints

### Trigger Onboarding

Dispara el flujo de onboarding para un nuevo empleado.

**Endpoint**: `POST /api/v1/executions/trigger/workflows.employee_onboarding`

**Headers**:
```
Content-Type: application/json
Authorization: Bearer YOUR_KESTRA_TOKEN (opcional)
```

**Request Body**:
```json
{
  "inputs": {
    "employee_email": "nuevo.empleado@empresa.com",
    "full_name": "Nuevo Empleado",
    "start_date": "2025-02-01",
    "manager_email": "manager@empresa.com",
    "department": "Engineering",
    "role": "Senior Developer",
    "location": "Madrid",
    
    // Opcionales - Notificaciones
    "slack_webhook_url": "https://hooks.slack.com/services/...",
    "teams_webhook_url": "https://outlook.office.com/webhook/...",
    "slack_notifications_webhook_url": "https://hooks.slack.com/services/...",
    
    // Opcionales - Email
    "email_api_url": "https://api.sendgrid.com/v3/mail/send",
    "email_api_key": "SG.your_key",
    
    // Opcionales - Cuentas
    "idp_api_url": "https://yourcompany.okta.com/api/v1/users",
    "idp_api_key": "your_okta_token",
    "workspace_api_url": "https://admin.googleapis.com/admin/directory/v1/users",
    "workspace_api_key": "your_google_key",
    
    // Opcionales - HRIS
    "hris_api_url": "https://api.bamboohr.com/v1/employees",
    "hris_api_key": "your_bamboohr_key",
    
    // Opcionales - Base de Datos
    "db_jdbc_url": "jdbc:postgresql://db:5432/onboarding",
    "db_user": "onboarding_user",
    "db_password": "your_password",
    
    // Opcionales - Métricas
    "prometheus_pushgateway_url": "http://prometheus-pushgateway:9091",
    
    // Opcionales - Flags de control
    "enable_hris_lookup": true,
    "enable_account_creation": true,
    "enable_welcome_email": true,
    "enable_manager_tasks": true,
    "enable_calendar_event": true,
    "enable_db_persistence": true,
    "metrics_enabled": true,
    "enable_hris_confirmation": true,
    "idempotency_ttl_hours": 24
  }
}
```

**Response**:
```json
{
  "id": "execution-id-12345",
  "namespace": "workflows",
  "flowId": "employee_onboarding",
  "state": {
    "current": "RUNNING"
  },
  "startDate": "2025-01-20T10:00:00Z"
}
```

**Error Responses**:

400 Bad Request:
```json
{
  "message": "Validation failed",
  "details": "Missing required field: employee_email"
}
```

409 Conflict:
```json
{
  "message": "Duplicate onboarding detected",
  "details": "Onboarding already exists for empleado@empresa.com:2025-02-01"
}
```

## Consulta de Estado

### Obtener Estado de Ejecución

**Endpoint**: `GET /api/v1/executions/{execution_id}`

**Response**:
```json
{
  "id": "execution-id-12345",
  "namespace": "workflows",
  "flowId": "employee_onboarding",
  "state": {
    "current": "SUCCESS",
    "histories": [...]
  },
  "startDate": "2025-01-20T10:00:00Z",
  "endDate": "2025-01-20T10:15:00Z"
}
```

### Obtener Logs

**Endpoint**: `GET /api/v1/executions/{execution_id}/logs`

**Query Parameters**:
- `taskId` (opcional): Filtrar por tarea específica
- `level` (opcional): Filtrar por nivel (INFO, WARNING, ERROR)

## Respuestas del Flujo

### Outputs Disponibles

Después de la ejecución, puedes consultar los siguientes outputs:

1. **employee_parsed.json**: Datos validados del empleado
2. **employee_enriched.json**: Datos enriquecidos con HRIS
3. **accounts_summary.json**: Resumen de cuentas creadas
4. **progress_summary.json**: Resumen de progreso completo
5. **audit_report.json**: Reporte de auditoría
6. **follow_up_schedule.json**: Tareas de seguimiento programadas
7. **final_summary.json**: Resumen final consolidado

### Ejemplo de Consulta de Output

```bash
GET /api/v1/executions/{execution_id}/outputs/track_progress_and_summary/files/progress_summary.json
```

## Estados del Flujo

- `CREATED`: Ejecución creada
- `RUNNING`: En progreso
- `SUCCESS`: Completado exitosamente
- `FAILED`: Falló
- `KILLED`: Cancelado manualmente

## Webhooks HR Compatibles

### BambooHR

```json
{
  "email": "empleado@empresa.com",
  "firstName": "Nombre",
  "lastName": "Apellido",
  "startDate": "2025-02-01",
  "department": "Engineering",
  "position": "Developer",
  "managerEmail": "manager@empresa.com"
}
```

### Workday

```json
{
  "email": "empleado@empresa.com",
  "first_name": "Nombre",
  "last_name": "Apellido",
  "startDate": "2025-02-01",
  "dept": "Engineering",
  "job_title": "Developer",
  "managerEmail": "manager@empresa.com"
}
```

### Bizneo HR

```json
{
  "email_address": "empleado@empresa.com",
  "firstname": "Nombre",
  "lastname": "Apellido",
  "employment_start_date": "2025-02-01",
  "department": "Engineering",
  "role": "Developer",
  "supervisor_email": "manager@empresa.com"
}
```

## Rate Limiting

- **Límite**: 100 requests/minuto por IP
- **Burst**: 20 requests/segundo
- **Headers de respuesta**:
  - `X-RateLimit-Limit`: Límite total
  - `X-RateLimit-Remaining`: Requests restantes
  - `X-RateLimit-Reset`: Timestamp de reset

## Autenticación

### Token Bearer

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://kestra.example.com/api/v1/executions/trigger/workflows.employee_onboarding
```

### API Key (alternativo)

```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  https://kestra.example.com/api/v1/executions/trigger/workflows.employee_onboarding
```

## Ejemplos de Uso

Ver `workflow/kestra/flows/examples/webhook_examples.json` para ejemplos completos en diferentes lenguajes.

## Errores Comunes

### 400: Validation Failed
- Verificar que todos los campos requeridos estén presentes
- Verificar formato de email
- Verificar formato de fecha (YYYY-MM-DD)

### 409: Duplicate Onboarding
- Ya existe un onboarding para este email y fecha
- Usar `idempotency_key` diferente o esperar TTL

### 500: Internal Server Error
- Verificar logs del flujo
- Verificar configuración de integraciones
- Contactar soporte si persiste

## Soporte

- **Documentación**: `workflow/kestra/flows/README_onboarding.md`
- **Troubleshooting**: `workflow/kestra/flows/BEST_PRACTICES_onboarding.md`
- **Issues**: Crear issue en el repositorio

---

**Versión API**: 2.0.0
**Última actualización**: 2025-01-20

