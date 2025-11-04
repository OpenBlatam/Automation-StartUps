# Ejemplos de Uso del Sistema de Aprobaciones

## 🎯 Ejemplos Prácticos

### 1. Solicitud de Vacaciones (Auto-aprobada)

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "vacation",
    "requester_email": "john.doe@company.com",
    "title": "Vacaciones cortas",
    "description": "Días personales",
    "vacation": {
      "start_date": "2025-02-15",
      "end_date": "2025-02-17",
      "vacation_type": "annual"
    },
    "priority": "normal"
  }'
```

**Resultado esperado**: Se auto-aprueba porque cumple la regla de "vacaciones de 3 días o menos"

### 2. Solicitud de Vacaciones (Requiere Aprobación)

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
      "end_date": "2025-07-20",
      "vacation_type": "annual"
    },
    "priority": "normal"
  }'
```

**Resultado esperado**: 
- Requiere aprobación de manager (nivel 1)
- Como son más de 10 días, también requiere aprobación de HR (nivel 2)

### 3. Gasto Pequeño (Auto-aprobado)

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "expense",
    "requester_email": "jane.manager@company.com",
    "title": "Almuerzo con cliente",
    "description": "Reunión de negocios",
    "expense": {
      "amount": 85.50,
      "currency": "USD",
      "category": "meals",
      "expense_date": "2025-01-20",
      "receipt_url": "https://storage.example.com/receipts/receipt123.pdf"
    },
    "priority": "normal"
  }'
```

**Resultado esperado**: Se auto-aprueba porque es menor a $500 y es de categoría "meals"

### 4. Gasto Mediano (Manager + Finanzas)

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "expense",
    "requester_email": "jane.manager@company.com",
    "title": "Equipamiento de oficina",
    "description": "Nuevos monitores para el equipo",
    "expense": {
      "amount": 7500.00,
      "currency": "USD",
      "category": "supplies",
      "expense_date": "2025-01-20",
      "receipt_url": "https://storage.example.com/receipts/receipt456.pdf"
    },
    "priority": "high"
  }'
```

**Resultado esperado**:
- Requiere aprobación de manager (nivel 1)
- Como es >= $5K, también requiere aprobación de finanzas (nivel 2)

### 5. Gasto Grande (Manager + Finanzas + Director)

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "expense",
    "requester_email": "bob.director@company.com",
    "title": "Licencias de software empresarial",
    "description": "Renovación anual de licencias",
    "expense": {
      "amount": 45000.00,
      "currency": "USD",
      "category": "supplies",
      "expense_date": "2025-01-20",
      "receipt_url": "https://storage.example.com/receipts/receipt789.pdf"
    },
    "priority": "urgent"
  }'
```

**Resultado esperado**:
- Requiere aprobación de manager (nivel 1)
- Requiere aprobación de finanzas (nivel 2, >= $5K)
- Requiere aprobación de director (nivel 3, >= $25K)

### 6. Documento de Revisión (Auto-aprobado)

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "document",
    "requester_email": "john.doe@company.com",
    "title": "Reporte mensual de actividades",
    "description": "Reporte rutinario",
    "document": {
      "document_url": "https://storage.example.com/docs/monthly-report.pdf",
      "document_category": "report",
      "document_version": "1.0",
      "requires_review": false
    },
    "priority": "normal"
  }'
```

**Resultado esperado**: Se auto-aprueba porque es categoría "report" y no requiere revisión

### 7. Contrato (Requiere Revisión Legal)

```bash
curl -X POST https://approvals.example.com/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "document",
    "requester_email": "bob.director@company.com",
    "title": "Contrato con cliente XYZ",
    "description": "Revisar antes de firma",
    "document": {
      "document_url": "https://storage.example.com/docs/contract-xyz.pdf",
      "document_category": "contract",
      "document_version": "2.0",
      "requires_review": true
    },
    "priority": "high"
  }'
```

**Resultado esperado**: Requiere revisión legal (categoría "contract")

## 📱 Comandos de Slack

### Listar Aprobaciones Pendientes

```
/approvals list
```

### Ver Estado de Solicitud

```
/approvals status <request-id>
```

### Aprobar Solicitud

```
/approvals approve <request-id> "Aprobado, todo correcto"
```

### Rechazar Solicitud

```
/approvals reject <request-id> "Falta información adicional"
```

## 🔧 Consultas SQL Útiles

### Ver Solicitudes Pendientes de un Usuario

```sql
SELECT * FROM v_pending_approvals
WHERE approver_email = 'jane.manager@company.com'
ORDER BY days_until_timeout ASC;
```

### Ver Métricas de Auto-aprobación

```sql
SELECT * FROM v_auto_approval_rates;
```

### Ver Solicitudes Urgentes

```sql
SELECT * FROM v_urgent_approvals
WHERE urgency_level IN ('overdue', 'urgent')
ORDER BY urgency_level, days_until_timeout ASC;
```

### Ver Historial de una Solicitud

```sql
SELECT 
    ah.action,
    ah.actor_email,
    ah.previous_status,
    ah.new_status,
    ah.comments,
    ah.created_at
FROM approval_history ah
WHERE ah.request_id = 'request-uuid-here'
ORDER BY ah.created_at ASC;
```

### Ver Estadísticas por Departamento

```sql
SELECT * FROM v_approvals_by_department
ORDER BY department, request_type;
```

### Ver Tiempo Promedio de Aprobación por Nivel

```sql
SELECT 
    level,
    COUNT(*) AS total,
    AVG(EXTRACT(EPOCH FROM (approved_at - created_at)) / 3600) AS avg_hours
FROM approval_chains
WHERE status = 'approved'
  AND approved_at >= NOW() - INTERVAL '30 days'
GROUP BY level
ORDER BY level;
```

## 🎨 Reglas Automáticas Avanzadas

### Regla: Auto-aprobar Gastos de Viaje para Managers

```sql
INSERT INTO approval_rules (
    rule_name,
    rule_description,
    request_type,
    conditions,
    auto_approve,
    require_notification,
    notification_emails,
    priority
) VALUES (
    'Auto-aprobar viajes managers',
    'Gastos de viaje menores a $300 para managers se auto-aprueban',
    'expense',
    '{
        "amount_max": 300,
        "expense_category": ["travel"],
        "requester_role": ["manager"]
    }'::jsonb,
    true,
    true,
    ARRAY['finance@company.com'],
    9
);
```

### Regla: Auto-aprobar Vacaciones de Días Personales

```sql
INSERT INTO approval_rules (
    rule_name,
    rule_description,
    request_type,
    conditions,
    auto_approve,
    priority
) VALUES (
    'Auto-aprobar días personales cortos',
    'Días personales de 1-2 días se auto-aprueban',
    'vacation',
    '{
        "vacation_days_max": 2,
        "vacation_type": ["personal"]
    }'::jsonb,
    true,
    8
);
```

### Regla: Auto-aprobar Documentos de Reportes Internos

```sql
INSERT INTO approval_rules (
    rule_name,
    rule_description,
    request_type,
    conditions,
    auto_approve,
    priority
) VALUES (
    'Auto-aprobar reportes internos',
    'Reportes internos no requieren revisión',
    'document',
    '{
        "document_category": ["report"],
        "requires_review": false
    }'::jsonb,
    true,
    10
);
```

## 🔄 Flujos de Integración

### Integración con Kestra (Webhook)

```bash
curl -X POST https://kestra.example.com/api/v1/executions/trigger/webhook/approval_webhook_handler \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "expense",
    "requester_email": "john.doe@company.com",
    "title": "Gasto de ejemplo",
    "expense_amount": 450.00,
    "expense_currency": "USD",
    "expense_category": "meals",
    "expense_date": "2025-01-20"
  }'
```

### Integración con Flowable (Directo)

```bash
curl -X POST http://flowable.workflows.svc.cluster.local:8080/flowable-rest/service/runtime/process-instances \
  -H "Authorization: Bearer $FLOWABLE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "processDefinitionKey": "expenseRequest",
    "variables": [
      {"name": "requestId", "value": "uuid-here"},
      {"name": "requesterEmail", "value": "john.doe@company.com"},
      {"name": "amount", "value": 450.00},
      {"name": "currency", "value": "USD"},
      {"name": "category", "value": "meals"}
    ]
  }'
```

## 📊 Monitoreo y Alertas

### Verificar Aprobaciones Vencidas

```sql
SELECT 
    COUNT(*) AS overdue_count,
    COUNT(*) FILTER (WHERE timeout_date < NOW() - INTERVAL '1 day') AS critically_overdue
FROM approval_chains ac
JOIN approval_requests ar ON ac.request_id = ar.id
WHERE ac.status = 'pending'
  AND ar.status = 'pending'
  AND ac.timeout_date < NOW();
```

### Generar Reporte Semanal

```bash
# Ejecutar flujo de Kestra para reporte
curl -X POST https://kestra.example.com/api/v1/executions/trigger/schedule/approval_metrics_report
```

## 🛠️ Troubleshooting

### Verificar Por Qué una Solicitud No Se Auto-aprobó

```sql
SELECT 
    ar.id,
    ar.request_type,
    ar.title,
    ar.auto_approved,
    ar.auto_approval_rule_id,
    ar.metadata->>'evaluation_reason' AS evaluation_reason
FROM approval_requests ar
WHERE ar.id = 'request-uuid-here';
```

### Ver Reglas que Aplican a un Tipo de Solicitud

```sql
SELECT 
    rule_name,
    conditions,
    auto_approve,
    enabled
FROM approval_rules
WHERE request_type = 'expense'
  AND enabled = true
ORDER BY priority DESC;
```

### Verificar Estado de Proceso Flowable

```bash
curl http://flowable.workflows.svc.cluster.local:8080/flowable-rest/service/runtime/process-instances \
  -H "Authorization: Bearer $FLOWABLE_TOKEN" \
  | jq '.data[] | select(.businessKey == "request-uuid-here")'
```

