# 🚀 Employee Onboarding Automation - Guía Completa

Flujo automatizado completo para onboarding de nuevos empleados utilizando Kestra.

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Arquitectura del Flujo](#-arquitectura-del-flujo)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Integraciones](#-integraciones)
- [Persistencia y Base de Datos](#-persistencia-y-base-de-datos)
- [Métricas y Monitoreo](#-métricas-y-monitoreo)
- [Troubleshooting](#-troubleshooting)
- [Ejemplos](#-ejemplos)

## 🎯 Descripción General

Este flujo automatiza completamente el proceso de onboarding de nuevos empleados, desde que firman su contrato hasta que están completamente integrados. El proceso se ejecuta en **9 fases** y está diseñado para ser **robusto, escalable y fácil de mantener**.

### Características Principales

✅ **Validación robusta**: Validación de formato de emails, fechas, rangos válidos, prevención de auto-asignación
✅ **Idempotencia**: Previene ejecuciones duplicadas con verificación de llaves únicas
✅ **Integración HRIS**: Soporte para múltiples sistemas HR (BambooHR, Workday, Bizneo HR)
✅ **Creación automática de cuentas**: IdP (Okta, Entra ID), Workspace (Google, M365)
✅ **Notificaciones**: Slack, Teams, Email
✅ **Persistencia completa**: Base de datos PostgreSQL con historial completo
✅ **Métricas**: Prometheus para monitoreo en tiempo real
✅ **Auditoría**: Reportes completos de compliance y recomendaciones

## 🏗️ Arquitectura del Flujo

### Fases del Proceso

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: Parseo y Validación                                │
│ - Validación de datos de entrada                           │
│ - Normalización de campos                                  │
│ - Verificación de idempotencia                             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 2: Enriquecimiento de Datos (HRIS)                    │
│ - Búsqueda opcional en HRIS                                │
│ - Merge inteligente de datos                               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 3: Acciones en Paralelo                                │
│ - Crear cuenta IdP                                         │
│ - Crear cuenta Workspace                                   │
│ - Notificar equipo TI (Slack/Teams)                         │
│ - Enviar email de bienvenida                               │
│ - Crear tareas para manager                                │
│ - Añadir al calendario                                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 4: Consolidación de Resultados                        │
│ - Verificar estado de todas las tareas                     │
│ - Consolidar información de cuentas                        │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 5: Tracking y Notificaciones Finales                   │
│ - Generar resumen de progreso                              │
│ - Enviar notificaciones de éxito/fallo                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 6: Persistencia y Auditoría                           │
│ - Crear/esquema de BD                                      │
│ - Persistir datos del empleado                             │
│ - Registrar todas las acciones                             │
│ - Guardar detalles de cuentas                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 7: Métricas y Monitoreo                               │
│ - Emitir métricas a Prometheus                             │
│ - Tracking de tasa de éxito                                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 8: Confirmación al HRIS                               │
│ - Enviar confirmación de completado                        │
│ - Reporte de acciones ejecutadas                            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 9: Reporte de Auditoría                               │
│ - Generar reporte completo                                 │
│ - Análisis de compliance                                   │
│ - Recomendaciones automáticas                              │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuración

### Variables de Entrada Requeridas

#### Datos del Empleado (vía Webhook)
El webhook espera un JSON con los siguientes campos:

```json
{
  "email": "nuevo.empleado@empresa.com",
  "first_name": "Nuevo",
  "last_name": "Empleado",
  "start_date": "2025-02-01",
  "manager_email": "manager@empresa.com",
  "manager_name": "Manager Name",
  "position": "Desarrollador",
  "department": "Engineering",
  "office_location": "Madrid",
  "phone": "+34 123 456 789"
}
```

#### Configuración de Integraciones

**Notificaciones:**
- `slack_webhook_url`: Webhook de Slack para notificaciones al equipo TI
- `slack_notifications_webhook_url`: Webhook para notificaciones de éxito/fallo
- `teams_webhook_url`: Webhook de Microsoft Teams

**Email:**
- `email_api_url`: URL del API de envío de emails
- `email_api_key`: API key para el servicio de emails

**Cuentas:**
- `idp_api_url`: URL del API del IdP (Okta, Entra ID)
- `idp_api_key`: API key del IdP
- `workspace_api_url`: URL del API de Workspace (Google, M365)
- `workspace_api_key`: API key del Workspace

**HRIS:**
- `hris_api_url`: URL del API del HRIS
- `hris_api_key`: API key del HRIS

**Base de Datos:**
- `db_jdbc_url`: JDBC URL (ej: `jdbc:postgresql://db:5432/onboarding`)
- `db_user`: Usuario de BD
- `db_password`: Contraseña de BD
- `enable_db_persistence`: Habilitar persistencia (default: `true`)

**Métricas:**
- `prometheus_pushgateway_url`: URL del Pushgateway de Prometheus
- `metrics_enabled`: Habilitar métricas (default: `true`)

**Flags de Control:**
- `enable_hris_lookup`: Búsqueda en HRIS (default: `true`)
- `enable_account_creation`: Creación de cuentas (default: `true`)
- `enable_welcome_email`: Email de bienvenida (default: `true`)
- `enable_manager_tasks`: Tareas para manager (default: `true`)
- `enable_calendar_event`: Evento en calendario (default: `true`)
- `enable_hris_confirmation`: Confirmación al HRIS (default: `true`)
- `idempotency_ttl_hours`: TTL para idempotencia (default: `24`)

## 🚀 Uso

### Disparar el Flujo

#### Opción 1: Webhook desde Sistema HR

```bash
curl -X POST https://kestra.example.com/api/v1/executions/trigger/workflows.employee_onboarding \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "employee_email": "nuevo.empleado@empresa.com",
      "full_name": "Nuevo Empleado",
      "start_date": "2025-02-01",
      "manager_email": "manager@empresa.com",
      "department": "Engineering",
      "position": "Desarrollador",
      "slack_webhook_url": "https://hooks.slack.com/services/...",
      "email_api_url": "https://api.sendgrid.com/v3/mail/send",
      "idp_api_url": "https://api.okta.com/v1/users"
    }
  }'
```

#### Opción 2: Desde Kestra UI

1. Ir a Kestra UI → Flows
2. Seleccionar `workflows.employee_onboarding`
3. Hacer clic en "Execute"
4. Llenar los inputs requeridos
5. Ejecutar

### Monitoreo de Ejecución

```bash
# Ver logs de ejecución
kubectl logs -n kestra <execution-pod> -f

# Ver en Kestra UI
https://kestra.example.com/ui/executions/<execution-id>
```

## 🔌 Integraciones

### HRIS (BambooHR, Workday, etc.)

El flujo soporta integración con múltiples sistemas HRIS mediante webhook estándar:

```python
# Ejemplo de payload desde BambooHR
{
  "employee_id": "12345",
  "email": "empleado@empresa.com",
  "firstName": "Nombre",
  "lastName": "Apellido",
  "startDate": "2025-02-01",
  "department": "Engineering",
  "position": "Developer",
  "managerEmail": "manager@empresa.com"
}
```

### IdP (Okta, Entra ID)

```bash
# Formato esperado por Okta
POST /api/v1/users
{
  "profile": {
    "firstName": "Nombre",
    "lastName": "Apellido",
    "email": "empleado@empresa.com",
    "login": "empleado@empresa.com",
    "department": "Engineering",
    "title": "Developer"
  },
  "credentials": {
    "password": {
      "value": "TempPassword123!"
    }
  }
}
```

### Workspace (Google Workspace, M365)

```bash
# Formato esperado por Google Workspace
POST /admin/directory/v1/users
{
  "primaryEmail": "empleado@empresa.com",
  "name": {
    "givenName": "Nombre",
    "familyName": "Apellido"
  },
  "orgUnitPath": "/Engineering",
  "password": "TempPassword123!"
}
```

## 💾 Persistencia y Base de Datos

### Esquema de Base de Datos

El flujo crea automáticamente las siguientes tablas:

**employee_onboarding:**
- Almacena datos principales del empleado
- Campos: email, nombre, departamento, fecha inicio, manager, etc.
- Clave única: `employee_email`
- Índice en `idempotency_key`

**onboarding_actions:**
- Historial de todas las acciones ejecutadas
- Campos: tipo de acción, estado, detalles JSON, errores
- Foreign key a `employee_onboarding`

**onboarding_accounts:**
- Detalles de cuentas creadas (IdP, Workspace)
- Campos: tipo de cuenta, ID de cuenta, estado
- Unique constraint: `(employee_email, account_type)`

### Consultas Útiles

```sql
-- Ver empleados en onboarding
SELECT * FROM employee_onboarding 
WHERE status = 'completed'
ORDER BY created_at DESC;

-- Ver acciones de un empleado
SELECT * FROM onboarding_actions 
WHERE employee_email = 'empleado@empresa.com'
ORDER BY executed_at DESC;

-- Ver cuentas creadas
SELECT * FROM onboarding_accounts 
WHERE employee_email = 'empleado@empresa.com';

-- Tasa de éxito por departamento
SELECT 
  department,
  COUNT(*) as total,
  SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completados,
  ROUND(100.0 * SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) / COUNT(*), 2) as tasa_exito
FROM employee_onboarding
GROUP BY department;
```

## 📊 Métricas y Monitoreo

### Métricas de Prometheus

El flujo emite las siguientes métricas:

```
# Contador de onboarding completados
onboarding_completed_total{status="completed",department="Engineering"} 1

# Gauge de acciones completadas
onboarding_actions_completed{employee="empleado@empresa.com"} 10

# Total de acciones esperadas
onboarding_actions_total{employee="empleado@empresa.com"} 11

# Timestamp del onboarding
onboarding_timestamp{employee="empleado@empresa.com"} 1704124800
```

### Dashboards de Grafana

Ejemplo de query para dashboard:

```promql
# Tasa de éxito en últimos 7 días
rate(onboarding_completed_total{status="completed"}[7d]) / 
rate(onboarding_completed_total[7d]) * 100

# Tiempo promedio de onboarding
onboarding_timestamp - onboarding_timestamp offset 1h
```

## 🔧 Troubleshooting

### Problemas Comunes

**1. Error de validación de email:**
```
Error: Invalid employee email format
```
- Verificar que el email tenga formato válido
- Verificar que no esté vacío

**2. Error de idempotencia:**
```
Error: Duplicate onboarding run detected
```
- Ya existe un onboarding para este empleado y fecha
- Verificar en BD: `SELECT * FROM employee_onboarding WHERE idempotency_key = '...'`

**3. Error de creación de cuenta IdP:**
- Verificar que `idp_api_url` y `idp_api_key` estén correctos
- Verificar permisos del API key
- Revisar logs de la tarea `create_idp_account`

**4. Error de persistencia en BD:**
- Verificar conexión JDBC
- Verificar permisos del usuario de BD
- Verificar que las tablas existan (se crean automáticamente)

### Logs

```bash
# Ver logs completos de ejecución
kubectl logs -n kestra <execution-id> --all-containers=true

# Filtrar por fase
kubectl logs -n kestra <execution-id> | grep "FASE"
```

## 📝 Ejemplos

### Ejemplo Completo de Payload

```json
{
  "email": "nuevo.empleado@empresa.com",
  "first_name": "Nuevo",
  "last_name": "Empleado",
  "start_date": "2025-02-01",
  "manager_email": "manager@empresa.com",
  "manager_name": "Manager Name",
  "position": "Senior Developer",
  "department": "Engineering",
  "office_location": "Madrid",
  "phone": "+34 123 456 789",
  "employee_id": "EMP-12345",
  "contract_signed_date": "2025-01-15T10:00:00Z"
}
```

### Ejemplo de Ejecución Programada

```yaml
# Trigger programado para revisar empleados pendientes
triggers:
  - id: scheduled_onboarding_review
    type: io.kestra.plugin.core.trigger.Schedule
    cron: "0 9 * * 1"  # Cada lunes a las 9 AM
    inputs:
      action: "review_pending"
```

### Ejemplo de Integración con Sistema HR

```python
# Webhook handler para BambooHR
@app.route('/webhook/bamboo/onboarding', methods=['POST'])
def bamboo_webhook():
    payload = request.json
    
    # Normalizar datos
    employee_data = {
        "email": payload.get("email"),
        "first_name": payload.get("firstName"),
        "last_name": payload.get("lastName"),
        "start_date": payload.get("startDate"),
        "manager_email": payload.get("manager", {}).get("email"),
        # ... más campos
    }
    
    # Disparar flujo de Kestra
    response = requests.post(
        "https://kestra.example.com/api/v1/executions/trigger/workflows.employee_onboarding",
        json={"inputs": employee_data}
    )
    
    return response.json()
```

## 📚 Referencias

- [Documentación de Kestra](https://kestra.io/docs)
- [Plugins de Kestra](https://kestra.io/plugins)
- [Best Practices de Onboarding](https://example.com/onboarding-best-practices)

## 🤝 Contribuir

Para mejoras o reporte de bugs, por favor abre un issue en el repositorio.

---

**Última actualización**: 2025-01-20
**Versión**: 2.0.0

