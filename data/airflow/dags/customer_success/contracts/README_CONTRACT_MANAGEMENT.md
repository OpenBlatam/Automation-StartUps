# Sistema de Automatización de Gestión de Contratos

Sistema completo para automatizar el ciclo de vida de contratos, incluyendo creación desde plantillas, firma electrónica, almacenamiento de versiones y recordatorios de renovación.

## Características Principales

### ✅ Creación Automática desde Plantillas
- Plantillas reutilizables con variables dinámicas
- Generación automática de contratos personalizados
- Soporte para múltiples tipos de contratos (laboral, servicios, NDA, etc.)

### ✅ Firma Electrónica
- Integración con **DocuSign** y **PandaDoc**
- Soporte para múltiples firmantes con orden de firma
- Tracking en tiempo real del estado de firma
- Descarga automática de documentos firmados

### ✅ Almacenamiento de Versiones
- Almacenamiento seguro de todas las versiones firmadas
- Hash SHA-256 para verificación de integridad
- Historial completo de cambios y modificaciones

### ✅ Recordatorios Automáticos
- Recordatorios programados (90, 60, 30, 14, 7 días antes de expiración)
- Prevención de recordatorios duplicados
- Notificaciones a múltiples roles (dueño, manager, legal)

## Arquitectura

### Componentes

1. **Schema de Base de Datos** (`data/db/contract_management_schema.sql`)
   - Tablas para plantillas, contratos, firmantes, versiones y eventos
   - Vistas para consultas comunes
   - Índices optimizados

2. **Módulo de Integración** (`data/airflow/plugins/contract_integrations.py`)
   - Clases para DocuSign y PandaDoc
   - Funciones de gestión de plantillas
   - Funciones de creación y envío de contratos
   - Almacenamiento de versiones

3. **DAG de Gestión** (`data/airflow/dags/contract_management.py`)
   - Creación de contratos desde plantillas
   - Envío automático para firma
   - Tracking de estado

4. **DAG de Recordatorios** (`data/airflow/dags/contract_renewal_reminders.py`)
   - Ejecución diaria
   - Identificación de contratos próximos a expirar
   - Envío de recordatorios

## Configuración

### 1. Instalar Schema de Base de Datos

```bash
psql -U postgres -d your_database -f data/db/contract_management_schema.sql
```

### 2. Configurar Variables de Entorno

#### Para DocuSign:
```bash
export DOCUSIGN_API_BASE_URL="https://demo.docusign.net"  # o https://www.docusign.net para producción
export DOCUSIGN_ACCOUNT_ID="your_account_id"
export DOCUSIGN_INTEGRATION_KEY="your_integration_key"
export DOCUSIGN_USER_ID="your_user_id"
export DOCUSIGN_PRIVATE_KEY_PATH="/path/to/private_key.pem"
# O usar token directo:
export DOCUSIGN_ACCESS_TOKEN="your_access_token"
```

#### Para PandaDoc:
```bash
export PANDADOC_API_KEY="your_api_key"
export PANDADOC_API_BASE_URL="https://api.pandadoc.com"
```

### 3. Crear Plantillas de Contratos

Ejemplo de inserción de plantilla:

```sql
INSERT INTO contract_templates (
    template_id, name, description, contract_type, template_content,
    template_variables, default_expiration_days, default_reminder_days,
    requires_legal_review, requires_manager_approval, signers_required,
    is_active, created_by
) VALUES (
    'employment_contract_v1',
    'Contrato Laboral Estándar',
    'Contrato laboral con cláusulas estándar',
    'employment',
    'CONTRATO LABORAL

Entre {{company_name}}, representada por {{company_representative}}, y {{employee_name}},
identificado con DNI {{employee_dni}}, se establece el siguiente contrato:

1. POSICIÓN: {{position}}
2. SALARIO: {{salary}}
3. FECHA DE INICIO: {{start_date}}
4. DURACIÓN: {{duration}} días

Firma del Empleado: _______________
Firma del Representante: _______________',
    '{"company_name": "string", "company_representative": "string", "employee_name": "string", "employee_dni": "string", "position": "string", "salary": "string", "start_date": "date", "duration": "integer"}'::jsonb,
    365,
    ARRAY[90, 60, 30, 14, 7],
    false,
    true,
    '[{"role": "employee", "order": 1}, {"role": "manager", "order": 2}]'::jsonb,
    true,
    'admin@example.com'
);
```

## DAGs Disponibles

### 1. `contract_management`
DAG principal para crear contratos desde plantillas y enviarlos para firma.

**Triggers:** Manual
**Uso:** Crear contratos individuales o masivamente

### 2. `contract_renewal_reminders`
DAG que se ejecuta diariamente para enviar recordatorios de renovación.

**Schedule:** Diario (24 horas)
**Funcionalidad:** Identifica contratos próximos a expirar y envía recordatorios

### 3. `contract_status_monitor`
DAG que verifica periódicamente el estado de contratos pendientes.

**Schedule:** Cada 6 horas
**Funcionalidad:** Actualiza estado de firma y descarga documentos firmados

### 4. `contract_auto_renewal`
DAG que renueva automáticamente contratos elegibles.

**Schedule:** Diario (24 horas)
**Funcionalidad:** Renueva contratos con `auto_renew=true` próximos a expirar

### 5. Integración con `employee_onboarding`
El DAG de onboarding ahora incluye creación automática de contratos.

**Parámetros nuevos:**
- `create_contract`: Crear contrato automáticamente (default: true)
- `contract_template_id`: ID de plantilla (default: "employment_contract_v1")
- `contract_esignature_provider`: Proveedor de firma (default: "docusign")

### 6. `contract_reports`
DAG semanal que genera reportes de métricas y analytics.

**Schedule:** Semanal (7 días)
**Funcionalidad:** Genera reportes consolidados con KPIs y alertas

## Uso

### Crear Contrato desde Plantilla

Disparar el DAG `contract_management` con parámetros:

```json
{
    "template_id": "employment_contract_v1",
    "primary_party_email": "employee@example.com",
    "primary_party_name": "Juan Pérez",
    "contract_variables": {
        "company_name": "Mi Empresa S.A.",
        "company_representative": "María García",
        "employee_name": "Juan Pérez",
        "employee_dni": "12345678",
        "position": "Software Engineer",
        "salary": "$5000",
        "start_date": "2024-02-01",
        "duration": 365
    },
    "esignature_provider": "docusign",
    "auto_send_for_signature": true,
    "additional_signers": [
        {
            "email": "manager@example.com",
            "name": "María García",
            "role": "manager"
        }
    ]
}
```

### Verificar Estado de Firma

El DAG `contract_management` verifica automáticamente el estado inicial. Para verificar manualmente:

```python
from data.airflow.plugins.contract_integrations import check_contract_signature_status

status = check_contract_signature_status(contract_id="CONTRACT-ABC123")
```

### Recordatorios Automáticos

El DAG `contract_renewal_reminders` se ejecuta diariamente y:
- Identifica contratos que expiran en los próximos 90 días
- Envía recordatorios según los días configurados en la plantilla
- Evita duplicados

## Integraciones

### DocuSign

**Autenticación:**
- Soporte para JWT (JSON Web Token) con clave privada RSA
- También soporta token de acceso directo

**Funcionalidades:**
- Crear envelopes con múltiples firmantes
- Verificar estado de firma
- Descargar documentos firmados

### PandaDoc

**Autenticación:**
- API Key simple

**Funcionalidades:**
- Crear documentos para firma
- Enviar para firma
- Verificar estado
- Descargar documentos firmados

## Almacenamiento de Versiones

Cada contrato firmado se almacena en:
- Base de datos: Tabla `contract_versions`
- Hash SHA-256 para verificación de integridad
- Metadatos de almacenamiento (S3, GCS, etc.) - por implementar

## Consultas Útiles

### Contratos Pendientes de Firma

```sql
SELECT * FROM contracts_pending_signature;
```

### Contratos Próximos a Expirar

```sql
SELECT * FROM contracts_expiring_soon;
```

### Estadísticas de Contratos

```sql
SELECT * FROM contract_statistics;
```

### Historial de Eventos de un Contrato

```sql
SELECT * FROM contract_events
WHERE contract_id = 'CONTRACT-ABC123'
ORDER BY event_timestamp DESC;
```

## Monitoreo y Alertas

Los DAGs incluyen:
- Métricas de Airflow Stats
- Logging estructurado
- Notificaciones Slack en éxito/fallo
- Retry automático con backoff exponencial

## Troubleshooting

### Error: "DocuSign access token no disponible"
- Verificar variables de entorno configuradas
- Si usa JWT, verificar que la clave privada existe y es válida
- Verificar permisos de la aplicación en DocuSign

### Error: "Plantilla no encontrada"
- Verificar que `template_id` existe en `contract_templates`
- Verificar que `is_active = true`

### Recordatorios no se envían
- Verificar que el DAG `contract_renewal_reminders` está activo
- Verificar logs del DAG para errores
- Verificar que los contratos tienen `expiration_date` configurado

## Mejoras Implementadas ✨

### ✅ Integración con Onboarding
- **Creación automática de contratos** durante el proceso de onboarding de empleados
- Integración directa con el DAG `employee_onboarding`
- Parámetros configurables: `create_contract`, `contract_template_id`, `contract_esignature_provider`
- Actualización automática de metadata en `employee_onboarding`

### ✅ Renovación Automática
- DAG `contract_auto_renewal` que se ejecuta diariamente
- Identifica contratos con `auto_renew=true` próximos a expirar
- Crea nuevas versiones automáticamente
- Mantiene historial de renovaciones

### ✅ Monitoreo Periódico
- DAG `contract_status_monitor` que se ejecuta cada 6 horas
- Verifica estado de contratos pendientes de firma
- Actualiza estado en BD automáticamente
- Descarga documentos firmados cuando están completos

### ✅ Funciones de Analytics y Búsqueda
- `get_contract_analytics()`: Métricas y estadísticas de contratos
- `search_contracts()`: Búsqueda avanzada con filtros y paginación
- Métricas incluyen: tasa de firma, días promedio para firmar, contratos próximos a expirar

### ✅ Funciones de Renovación
- `renew_contract()`: Renueva un contrato creando nueva versión
- Mantiene firmantes y variables originales
- Registra eventos de renovación

## Mejoras Avanzadas Implementadas ✨

### ✅ Sistema de Webhooks (`contract_webhooks.py`)
- **Webhooks de DocuSign Connect**: Procesamiento automático de eventos de firma
- **Webhooks de PandaDoc**: Manejo de eventos de documentos
- **Verificación de firmas HMAC**: Seguridad en webhooks
- **Actualización automática de estado**: Los webhooks actualizan el estado del contrato automáticamente
- **Aplicación Flask lista**: Endpoints `/webhooks/docusign` y `/webhooks/pandadoc`

**Configuración:**
```bash
export DOCUSIGN_WEBHOOK_SECRET="your_secret_key"
export PANDADOC_API_KEY="your_api_key"
```

### ✅ Validación Avanzada (`contract_validation.py`)
- **Validación de templates**: Verifica que todas las variables estén presentes
- **Validación de datos**: Emails, fechas, firmantes
- **Reglas de negocio**: Duración apropiada por tipo de contrato
- **Validación de orden de firmantes**: Verifica secuencia lógica
- **Warnings inteligentes**: Detecta contenido sospechoso o placeholders no reemplazados

**Validaciones incluidas:**
- Duración mínima/máxima por tipo de contrato
- Orden secuencial de firmantes
- Fechas de expiración válidas
- Variables no reemplazadas en contenido

### ✅ Almacenamiento Cloud (`contract_storage.py`)
- **S3 Storage Adapter**: Integración con Amazon S3
- **GCS Storage Adapter**: Integración con Google Cloud Storage
- **Metadata enriquecida**: Hash SHA-256, fechas, IDs
- **Upload/Download/Delete**: Operaciones completas de almacenamiento

**Configuración S3:**
```bash
export CONTRACT_STORAGE_TYPE="s3"
export S3_CONTRACTS_BUCKET="your-bucket-name"
export AWS_REGION="us-east-1"
```

**Configuración GCS:**
```bash
export CONTRACT_STORAGE_TYPE="gcs"
export GCS_CONTRACTS_BUCKET="your-bucket-name"
```

### ✅ Caché de Plantillas
- **LRU Cache**: Caché de hasta 100 plantillas para mejor rendimiento
- **Función `get_template_cached()`**: Versión con caché para uso frecuente

### ✅ Notificaciones Mejoradas
- **Notificaciones Slack**: Integradas en todos los eventos clave
- **Colores y emojis**: Priorización visual de notificaciones
- **Reportes automáticos**: Envío semanal de métricas

## Mejoras Futuras

- [ ] Generación automática de PDF desde templates HTML/Markdown
- [ ] Integración con más proveedores (HelloSign, Adobe Sign)
- [ ] Dashboard web para visualización de contratos
- [ ] Integración con sistemas de HRIS para datos automáticos
- [ ] API REST para gestión de contratos
- [ ] Soporte multi-idioma en templates

## Webhooks

### Configurar Webhooks en DocuSign

1. Ir a DocuSign Admin > Connect
2. Crear nueva configuración Connect
3. Configurar URL: `https://your-domain.com/webhooks/docusign`
4. Seleccionar eventos: `envelope-completed`, `envelope-signed`, `envelope-declined`
5. Configurar secret key y guardarlo en `DOCUSIGN_WEBHOOK_SECRET`

### Configurar Webhooks en PandaDoc

1. Ir a PandaDoc Settings > Webhooks
2. Agregar webhook endpoint: `https://your-domain.com/webhooks/pandadoc`
3. Seleccionar eventos: `document_completed`, `document_deleted`
4. Configurar signature verification

### Desplegar Servidor de Webhooks

```python
from data.airflow.plugins.contract_webhooks import create_webhook_app

app = create_webhook_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

## Seguridad

- Las credenciales deben almacenarse en Airflow Variables/Connections o Vault
- Los documentos firmados deben almacenarse encriptados
- Los hashes SHA-256 permiten verificar integridad
- Auditoría completa en tabla `contract_events`
- **Webhooks verifican firmas HMAC** para seguridad
- **Validación exhaustiva** antes de crear contratos
- **Almacenamiento cloud** con metadata enriquecida

## Ejemplos de Plantillas

Ver `data/db/contract_management_schema.sql` para ejemplos de inserción de plantillas.

