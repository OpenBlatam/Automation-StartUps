# Automatización Completa de Contratos para Nuevos Clientes

Este sistema automatiza completamente el flujo de generación de contratos legales para nuevos clientes, desde la creación del borrador hasta la activación de servicios tras la firma.

## 📋 Flujo Automatizado

```
Nuevo Cliente → Genera Borrador → Envía para Firma → Detecta Firma → Activa Servicios
```

### Componentes del Sistema

1. **`automated_customer_contract`** - DAG que genera y envía contratos
2. **`contract_signature_activation`** - DAG que monitorea firmas y activa servicios
3. **Webhook Handlers** - Reciben notificaciones de DocuSign/PandaDoc en tiempo real
4. **Función de Activación** - Activa servicios automáticamente tras firma

## 🚀 Uso

### 1. Generar Contrato para Nuevo Cliente

Disparar el DAG `automated_customer_contract` con los siguientes parámetros:

```json
{
    "customer_email": "cliente@example.com",
    "customer_name": "Juan Pérez",
    "company_name": "Mi Empresa S.A.",
    "service_plan": "enterprise",
    "contract_template_id": "client_service_contract_enterprise",
    "esignature_provider": "docusign",
    "auto_activate_services": true,
    "services_to_activate": ["api_access", "dashboard", "support"],
    "contract_start_date": "2024-02-01",
    "contract_duration_days": 365
}
```

**Parámetros requeridos:**
- `customer_email`: Email del cliente
- `customer_name`: Nombre completo del cliente
- `service_plan`: Plan de servicio (basic, standard, enterprise, premium)

**Parámetros opcionales:**
- `contract_template_id`: Si no se proporciona, se selecciona automáticamente según el plan
- `company_name`: Nombre de la empresa
- `esignature_provider`: 'docusign' o 'pandadoc' (default: 'docusign')
- `auto_activate_services`: Activar servicios automáticamente (default: true)
- `services_to_activate`: Lista de servicios a activar (default: ["api_access", "dashboard", "support"])
- `contract_start_date`: Fecha de inicio (default: hoy)
- `contract_duration_days`: Duración en días (default: 365)
- `additional_signers`: Firmantes adicionales

### 2. Monitoreo Automático de Firmas

El DAG `contract_signature_activation` se ejecuta automáticamente **cada 15 minutos** y:

- Busca contratos con estado `pending_signature` o `partially_signed`
- Verifica el estado actual con el proveedor de firma
- Si detecta que un contrato está `fully_signed`, activa los servicios automáticamente
- Actualiza el estado en la base de datos

**No requiere configuración adicional** - funciona automáticamente.

### 3. Webhooks en Tiempo Real (Opción Recomendada)

Para activación **inmediata** cuando se recibe una firma, configurar webhooks:

#### DocuSign Connect

1. Configurar DocuSign Connect en tu cuenta
2. URL del webhook: `https://tu-dominio.com/webhooks/docusign`
3. Eventos a suscribir:
   - `envelope-completed`
   - `envelope-signed`

#### PandaDoc Webhooks

1. Configurar webhooks en el dashboard de PandaDoc
2. URL del webhook: `https://tu-dominio.com/webhooks/pandadoc`
3. Eventos a suscribir:
   - `document_completed`

Cuando se recibe una notificación de firma, el sistema:
1. Verifica la firma del webhook
2. Actualiza el estado del contrato
3. **Activa servicios inmediatamente** (si `auto_activate_services` está habilitado)
4. Registra el evento en la base de datos

## 🔧 Configuración

### Variables de Entorno

```bash
# PostgreSQL
export POSTGRES_CONN_ID="postgres_default"

# DocuSign
export DOCUSIGN_API_BASE_URL="https://demo.docusign.net"
export DOCUSIGN_ACCOUNT_ID="tu-account-id"
export DOCUSIGN_INTEGRATION_KEY="tu-integration-key"
export DOCUSIGN_USER_ID="tu-user-id"
export DOCUSIGN_PRIVATE_KEY_PATH="/path/to/private.key"
export DOCUSIGN_WEBHOOK_SECRET="tu-webhook-secret"

# PandaDoc
export PANDADOC_API_KEY="tu-api-key"
export PANDADOC_API_BASE_URL="https://api.pandadoc.com"
```

### Plantillas de Contrato

Crear plantillas en la tabla `contract_templates`:

```sql
INSERT INTO contract_templates (
    template_id,
    name,
    description,
    contract_type,
    template_content,
    default_expiration_days,
    is_active
) VALUES (
    'client_service_contract_enterprise',
    'Contrato de Servicio Enterprise',
    'Contrato para clientes con plan Enterprise',
    'client',
    'Contrato de Servicios
    Cliente: {{customer_name}}
    Email: {{customer_email}}
    Plan: {{service_plan}}
    Fecha de inicio: {{start_date}}
    Duración: {{expiration_days}} días',
    365,
    true
);
```

## 📊 Servicios que se Pueden Activar

El sistema puede activar automáticamente los siguientes servicios:

### 1. **api_access**
- Genera API keys para el cliente
- Almacena en tabla `customer_api_keys`

### 2. **dashboard**
- Activa acceso al dashboard
- Actualiza metadata en `customer_onboarding`

### 3. **support**
- Crea cuenta de soporte
- Configura acceso a portal de soporte

### Servicios Personalizados

Puedes agregar servicios personalizados modificando la función `activate_customer_services` en `contract_signature_activation.py`.

## 🔍 Monitoreo y Logs

### Ver Contratos Pendientes

```sql
SELECT 
    contract_id,
    primary_party_name,
    primary_party_email,
    status,
    created_at,
    esignature_url
FROM contracts
WHERE status IN ('pending_signature', 'partially_signed')
ORDER BY created_at DESC;
```

### Ver Servicios Activados

```sql
SELECT 
    cs.customer_email,
    cs.service_name,
    cs.contract_id,
    cs.activated_at,
    cs.status
FROM customer_services cs
WHERE cs.status = 'active'
ORDER BY cs.activated_at DESC;
```

### Ver Eventos de Contratos

```sql
SELECT 
    contract_id,
    event_type,
    event_description,
    event_timestamp
FROM contract_events
WHERE event_type = 'services_activated'
ORDER BY event_timestamp DESC;
```

## 📈 Integración con Onboarding

Este sistema se puede integrar con el DAG de `customer_onboarding`:

### Opción 1: Disparar Manualmente

Después de completar el onboarding, disparar `automated_customer_contract` con los datos del cliente.

### Opción 2: Integración Automática

Modificar el DAG de onboarding para que automáticamente dispare la generación de contrato:

```python
# En customer_onboarding.py, después de verify_identity_task
contract_trigger = TriggerDagRunOperator(
    task_id="trigger_contract_generation",
    trigger_dag_id="automated_customer_contract",
    conf={
        "customer_email": "{{ ti.xcom_pull(task_ids='verify_identity')['customer_email'] }}",
        "customer_name": "{{ ti.xcom_pull(task_ids='verify_identity')['first_name'] }} {{ ti.xcom_pull(task_ids='verify_identity')['last_name'] }}",
        "service_plan": "{{ ti.xcom_pull(task_ids='verify_identity')['service_plan'] }}",
        "auto_activate_services": True,
        "services_to_activate": ["api_access", "dashboard", "support"]
    }
)
```

## 🛡️ Seguridad

1. **Webhooks**: Verificación de firma HMAC para todos los webhooks
2. **Validación**: Validación completa de datos antes de crear contratos
3. **Auditoría**: Todos los eventos se registran en `contract_events`
4. **Idempotencia**: Prevención de duplicados mediante `contract_id` único

## 🐛 Troubleshooting

### El contrato no se envía para firma

- Verificar que `esignature_provider` esté configurado correctamente
- Revisar logs de Airflow para errores de conexión con DocuSign/PandaDoc
- Verificar que las credenciales estén correctas en variables de entorno

### Los servicios no se activan

- Verificar que `auto_activate_services` esté en `true`
- Revisar que `services_to_activate` tenga valores válidos
- Verificar logs de Airflow en el task `activate_services_for_signed_contracts`
- Verificar que la tabla `customer_services` exista (o crear manualmente)

### Webhook no recibe notificaciones

- Verificar que la URL del webhook sea accesible públicamente
- Verificar que el secret key esté configurado correctamente
- Revisar logs del servidor webhook
- Verificar que los eventos estén suscritos en DocuSign/PandaDoc

## 📝 Ejemplos

### Ejemplo 1: Cliente Básico

```json
{
    "customer_email": "cliente@example.com",
    "customer_name": "María García",
    "service_plan": "basic",
    "esignature_provider": "docusign"
}
```

### Ejemplo 2: Cliente Enterprise con Configuración Personalizada

```json
{
    "customer_email": "cliente@empresa.com",
    "customer_name": "Juan Pérez",
    "company_name": "Mi Empresa S.A.",
    "service_plan": "enterprise",
    "contract_template_id": "client_service_contract_enterprise",
    "esignature_provider": "pandadoc",
    "auto_activate_services": true,
    "services_to_activate": ["api_access", "dashboard", "support", "advanced_analytics"],
    "contract_start_date": "2024-03-01",
    "contract_duration_days": 730,
    "additional_signers": [
        {
            "email": "legal@empresa.com",
            "name": "Departamento Legal",
            "role": "legal"
        }
    ]
}
```

## 🎯 Próximos Pasos

1. **Configurar plantillas de contrato** según tus necesidades
2. **Configurar webhooks** para activación en tiempo real
3. **Personalizar servicios** a activar según tu negocio
4. **Integrar con onboarding** para flujo completamente automatizado
5. **Monitorear logs** para asegurar que todo funciona correctamente

## 📚 Referencias

- [Sistema de Contratos](README_CONTRACT_MANAGEMENT.md)
- [Onboarding de Clientes](README_customer_onboarding.md)
- [Integraciones de Contratos](../../plugins/contract_integrations.py)












