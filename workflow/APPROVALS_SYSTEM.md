# Sistema de Aprobaciones Internas

## 🎯 Descripción General

Sistema completo de automatización de aprobaciones internas para gestionar solicitudes de vacaciones, gastos y documentos con reglas automáticas y flujos de trabajo multi-nivel.

## 📋 Características Principales

### ✅ Funcionalidades

- **Solicitudes de Vacaciones**: Gestión completa con aprobación por manager y HR (si aplica)
- **Gastos**: Flujo multi-nivel según monto (Manager → Finanzas → Director)
- **Documentos**: Revisión por categoría (Estándar, Legal, Finanzas, Ejecutivo)
- **Reglas Automáticas**: Auto-aprobación basada en condiciones configurables
- **Timeouts y Escalación**: Escalación automática si no se aprueba en tiempo
- **Notificaciones**: Integración con Slack/Email para notificar cambios de estado
- **Auditoría Completa**: Historial completo de todas las acciones

### 🚀 Ventajas

- **Aprobación Automática**: Reduce carga administrativa para solicitudes simples
- **Flexibilidad**: Reglas configurables sin modificar código
- **Escalabilidad**: Multi-nivel según criticidad y monto
- **Trazabilidad**: Auditoría completa de todas las aprobaciones
- **Integración**: Se integra con Flowable (BPMN) y Kestra (orquestación)

## 🏗️ Arquitectura

```
┌─────────────────┐
│   API REST      │  (FastAPI)
│  /requests      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   PostgreSQL    │  (Esquema de aprobaciones)
│  - Requests     │
│  - Rules        │
│  - Chains       │
│  - History      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kestra Flow    │  (Evaluación automática)
│  auto_evaluate  │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
    ▼        ▼
┌────────┐ ┌──────────┐
│ Auto-  │ │ Flowable │  (BPMN Processes)
│ Approved│ │  Manual  │
└────────┘ └──────────┘
```

## 📦 Componentes

### 1. Base de Datos (`data/db/approvals_schema.sql`)

Esquema completo con:

- **`approval_users`**: Usuarios y roles
- **`approval_requests`**: Solicitudes principales
- **`approval_rules`**: Reglas de auto-aprobación
- **`approval_chains`**: Cadenas de aprobación multi-nivel
- **`approval_history`**: Historial de auditoría
- **`approval_attachments`**: Archivos adjuntos
- **`approval_notifications`**: Notificaciones enviadas

**Vistas útiles**:
- `v_pending_approvals`: Aprobaciones pendientes por aprobador
- `v_user_request_summary`: Resumen de solicitudes por usuario
- `v_approval_metrics`: Métricas de aprobaciones

**Funciones**:
- `create_approval_chain()`: Crea cadena de aprobación automática
- `get_next_approver()`: Obtiene siguiente aprobador

### 2. Procesos BPMN (`workflow/flowable/`)

#### Vacation Request (`vacation_request.bpmn20.xml`)

Flujo:
1. Evaluación automática de reglas
2. Si auto-aprobado → Notificar y finalizar
3. Si requiere aprobación:
   - Aprobación de Manager (timeout 3 días)
   - Si > 10 días → Aprobación HR (timeout 5 días)
4. Notificar resultado

#### Expense Request (`expense_request.bpmn20.xml`)

Flujo:
1. Evaluación automática de reglas
2. Si auto-aprobado → Notificar y finalizar
3. Si requiere aprobación:
   - Manager (siempre, timeout 3 días)
   - Finanzas (si >= $5K, timeout 5 días)
   - Director (si >= $25K, timeout 7 días)
4. Notificar resultado

#### Document Review (`document_review.bpmn20.xml`)

Flujo:
1. Validación del documento
2. Evaluación automática de reglas
3. Si requiere revisión:
   - Estándar (reportes, otros)
   - Legal (contratos, políticas)
   - Finanzas (facturas)
   - Ejecutivo (propuestas)
4. Notificar resultado

### 3. Flujos de Kestra (`workflow/kestra/flows/`)

#### `approval_auto_evaluate_rules.yaml`

Evalúa reglas automáticas:
- Obtiene solicitud y reglas aplicables
- Evalúa condiciones (monto, días, categoría, rol, departamento)
- Actualiza estado (auto_approved o pending)
- Crea cadena de aprobación si es manual
- Inicia proceso Flowable si es necesario

#### `approval_webhook_handler.yaml`

Webhook handler para recibir solicitudes:
- Valida solicitud
- Crea registro en BD
- Llama a evaluación automática
- Retorna resultado

### 4. API REST (`kubernetes/integration/approvals-api.yaml`)

Endpoints principales:

- `POST /requests`: Crear solicitud
- `GET /requests/{id}`: Obtener solicitud
- `GET /requests`: Listar solicitudes (con filtros)
- `GET /pending-approvals/{email}`: Aprobaciones pendientes
- `GET /health`: Health check

## 🚀 Instalación

### 1. Crear Esquema de Base de Datos

```bash
# Conectar a PostgreSQL
psql -h postgres.example.com -U postgres -d approvals

# Ejecutar esquema
\i data/db/approvals_schema.sql
```

### 2. Desplegar Flowable (si no está desplegado)

```bash
kubectl apply -f workflow/flowable/deployment.yaml
```

### 3. Desplegar Procesos BPMN

```bash
# Obtener token de Flowable
FLOWABLE_TOKEN=$(kubectl get secret flowable-token -n workflows -o jsonpath='{.data.token}' | base64 -d)

# Desplegar procesos
curl -X POST http://flowable.workflows.svc.cluster.local:8080/flowable-rest/service/repository/deployments \
  -H "Authorization: Bearer $FLOWABLE_TOKEN" \
  -F "file=@workflow/flowable/vacation_request.bpmn20.xml"

curl -X POST http://flowable.workflows.svc.cluster.local:8080/flowable-rest/service/repository/deployments \
  -H "Authorization: Bearer $FLOWABLE_TOKEN" \
  -F "file=@workflow/flowable/expense_request.bpmn20.xml"

curl -X POST http://flowable.workflows.svc.cluster.local:8080/flowable-rest/service/repository/deployments \
  -H "Authorization: Bearer $FLOWABLE_TOKEN" \
  -F "file=@workflow/flowable/document_review.bpmn20.xml"
```

### 4. Crear Secrets

```bash
# Secret para base de datos
kubectl create secret generic approvals-db-secret \
  -n workflows \
  --from-literal=url="postgresql://user:password@postgres.workflows.svc.cluster.local:5432/approvals"

# Secret para Flowable token
kubectl create secret generic flowable-token \
  -n workflows \
  --from-literal=token="your-flowable-token"
```

### 5. Desplegar API

```bash
kubectl apply -f kubernetes/integration/approvals-api.yaml
```

### 6. Configurar Kestra Flows

Los flows de Kestra se despliegan automáticamente cuando se suben a Kestra:

```bash
# O usar la UI de Kestra para importar los YAML files
```

## 📝 Uso

### Crear Solicitud de Vacaciones

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "vacation",
    "requester_email": "john.doe@company.com",
    "title": "Vacaciones de verano",
    "description": "Vacaciones familiares",
    "vacation": {
      "start_date": "2025-07-01",
      "end_date": "2025-07-15",
      "vacation_type": "annual"
    },
    "priority": "normal"
  }'
```

### Crear Solicitud de Gasto

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "expense",
    "requester_email": "jane.manager@company.com",
    "title": "Cena con cliente",
    "description": "Cena de negocios",
    "expense": {
      "amount": 450.00,
      "currency": "USD",
      "category": "meals",
      "expense_date": "2025-01-20",
      "receipt_url": "https://storage.example.com/receipts/receipt123.pdf"
    },
    "priority": "normal"
  }'
```

### Crear Solicitud de Revisión de Documento

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "document",
    "requester_email": "bob.director@company.com",
    "title": "Contrato con cliente XYZ",
    "description": "Revisar contrato antes de firma",
    "document": {
      "document_url": "https://storage.example.com/docs/contract-xyz.pdf",
      "document_category": "contract",
      "document_version": "2.0",
      "requires_review": true
    },
    "priority": "high"
  }'
```

### Obtener Aprobaciones Pendientes

```bash
curl https://approvals.example.com/pending-approvals/jane.manager@company.com
```

## 🔧 Configuración de Reglas

### Ejemplo: Auto-aprobar gastos menores a $500

```sql
INSERT INTO approval_rules (
    rule_name,
    rule_description,
    request_type,
    conditions,
    auto_approve,
    require_notification,
    priority
) VALUES (
    'Auto-aprobar gastos pequeños',
    'Gastos menores a $500 se auto-aprueban',
    'expense',
    '{
        "amount_max": 500,
        "expense_category": ["meals", "supplies", "travel"],
        "requester_role": ["employee", "manager"]
    }'::jsonb,
    true,
    true,
    10
);
```

### Ejemplo: Auto-aprobar vacaciones cortas

```sql
INSERT INTO approval_rules (
    rule_name,
    rule_description,
    request_type,
    conditions,
    auto_approve,
    priority
) VALUES (
    'Auto-aprobar vacaciones cortas',
    'Vacaciones de 3 días o menos se auto-aprueban',
    'vacation',
    '{
        "vacation_days_max": 3,
        "vacation_type": ["annual", "personal"]
    }'::jsonb,
    true,
    10
);
```

## 📊 Monitoreo y Métricas

### Consultar Métricas

```sql
-- Ver métricas generales
SELECT * FROM v_approval_metrics;

-- Ver resumen por usuario
SELECT * FROM v_user_request_summary
WHERE requester_email = 'john.doe@company.com';

-- Ver aprobaciones pendientes
SELECT * FROM v_pending_approvals
WHERE approver_email = 'jane.manager@company.com';
```

### Consultar Historial

```sql
-- Ver historial completo de una solicitud
SELECT 
    ah.*,
    ar.title,
    ar.request_type
FROM approval_history ah
JOIN approval_requests ar ON ah.request_id = ar.id
WHERE ar.id = 'request-uuid-here'
ORDER BY ah.created_at DESC;
```

## 🔐 Seguridad

- **Autenticación**: Configurar OAuth2 o JWT tokens en la API
- **Autorización**: Validar permisos según rol en cada endpoint
- **Secrets**: Usar Kubernetes Secrets para credenciales
- **Auditoría**: Todos los cambios se registran en `approval_history`

## 🐛 Troubleshooting

### Solicitud no se auto-aprueba

1. Verificar que existen reglas habilitadas:
```sql
SELECT * FROM approval_rules 
WHERE request_type = 'expense' AND enabled = true;
```

2. Verificar que las condiciones coinciden:
```sql
SELECT conditions FROM approval_rules WHERE id = 'rule-id';
```

3. Revisar logs de Kestra:
```bash
kubectl logs -n workflows deployment/kestra | grep approval
```

### Proceso Flowable no inicia

1. Verificar que el proceso está desplegado:
```bash
curl http://flowable.workflows.svc.cluster.local:8080/flowable-rest/service/repository/process-definitions \
  -u admin:test
```

2. Verificar conectividad:
```bash
kubectl exec -n workflows deployment/approvals-api -- \
  curl http://flowable.workflows.svc.cluster.local:8080/flowable-rest/actuator/health
```

### API no responde

1. Verificar pods:
```bash
kubectl get pods -n workflows -l app=approvals-api
```

2. Ver logs:
```bash
kubectl logs -n workflows deployment/approvals-api
```

3. Verificar base de datos:
```bash
kubectl exec -n workflows deployment/approvals-api -- \
  python -c "import psycopg2; conn = psycopg2.connect(os.getenv('DATABASE_URL')); print('OK')"
```

## 📚 Referencias

- [Flowable Documentation](https://www.flowable.com/open-source/docs/)
- [Kestra Documentation](https://kestra.io/docs/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PostgreSQL JSONB Documentation](https://www.postgresql.org/docs/current/datatype-json.html)

## 📦 Componentes Adicionales

### 1. Recordatorios Automáticos (`approval_reminder_notifications.yaml`)

Flujo de Kestra que se ejecuta diariamente para enviar recordatorios de aprobaciones pendientes próximas a vencer.

**Características**:
- Envía recordatorios a aprobadores con solicitudes pendientes
- Clasifica por urgencia (crítico, urgente, pronto a vencer)
- Evita spam (no envía recordatorios si ya se notificó en las últimas 24h)
- Integración con Slack

### 2. Reportes de Métricas (`approval_metrics_report.yaml`)

Flujo de Kestra que genera reportes semanales de métricas del sistema.

**Características**:
- Reporte automático cada lunes
- Métricas de auto-aprobación
- Tiempo promedio de aprobación por nivel
- Solicitudes pendientes y vencidas
- Envío a Slack

### 3. Limpieza y Mantenimiento (`approval_cleanup.py`)

DAG de Airflow para tareas de mantenimiento periódicas.

**Tareas**:
- Archivar solicitudes antiguas (> 1 año)
- Limpiar notificaciones antiguas (> 6 meses)
- Optimizar índices de base de datos
- Refrescar vistas materializadas

**Schedule**: Domingos a las 2 AM

### 4. CLI de Gestión (`approval_cli.py`)

Herramienta de línea de comandos para gestión del sistema.

**Comandos disponibles**:
- `list-requests`: Listar solicitudes con filtros
- `show-request`: Mostrar detalles de una solicitud
- `pending-approvals`: Listar aprobaciones pendientes
- `metrics`: Mostrar métricas del sistema
- `toggle-rule`: Habilitar/deshabilitar reglas
- `list-rules`: Listar todas las reglas

**Uso**:
```bash
export APPROVALS_DB_URL="postgresql://user:pass@localhost/approvals"
python scripts/approval_cli.py list-requests --status pending
python scripts/approval_cli.py show-request <request-id>
python scripts/approval_cli.py pending-approvals --approver-email john@company.com
```

### 5. Integración con Slack Bot (`approval_slack_bot_integration.yaml`)

Permite aprobar/rechazar solicitudes directamente desde Slack.

**Comandos de Slack**:
- `/approvals list` - Listar aprobaciones pendientes
- `/approvals status <id>` - Ver estado de solicitud
- `/approvals approve <id> [comentarios]` - Aprobar
- `/approvals reject <id> [comentarios]` - Rechazar
- `/approvals help` - Mostrar ayuda

### 6. Vistas Materializadas (`approvals_views.sql`)

Vistas optimizadas para consultas frecuentes:

- `mv_approval_metrics`: Métricas diarias por tipo y estado
- `mv_approval_user_stats`: Estadísticas por usuario
- `mv_approval_approver_stats`: Estadísticas por aprobador
- `v_approvals_by_department`: Solicitudes por departamento
- `v_auto_approval_rates`: Tasa de auto-aprobación por tipo
- `v_urgent_approvals`: Solicitudes que requieren atención

### 7. Script de Configuración (`approval_setup.sh`)

Script bash para configuración inicial del sistema.

**Funcionalidades**:
- Crea esquema de base de datos
- Crea vistas materializadas
- Inserta usuarios de ejemplo
- Inserta reglas automáticas de ejemplo
- Refresca vistas

**Uso**:
```bash
export APPROVALS_DB_HOST=localhost
export APPROVALS_DB_NAME=approvals
export APPROVALS_DB_USER=postgres
./scripts/approval_setup.sh
```

## 📚 Documentación Adicional

- **Ejemplos de Uso**: Ver `APPROVALS_EXAMPLES.md` para ejemplos prácticos y casos de uso
- **Guía de Instalación**: Ver sección "Instalación" en este documento
- **API Reference**: Ver sección "Uso" en este documento

## 🔄 Mejoras Futuras

- [x] Dashboard web para visualizar solicitudes (CLI disponible)
- [x] Recordatorios automáticos (implementado)
- [x] Reportes de métricas (implementado)
- [x] Integración con Slack (implementado)
- [ ] Integración con calendarios (Google Calendar, Outlook)
- [ ] Notificaciones por SMS
- [ ] Aprobación móvil (app móvil)
- [ ] Machine Learning para sugerir aprobaciones
- [ ] Integración con sistemas de contabilidad (QuickBooks)
- [ ] Dashboard web interactivo

