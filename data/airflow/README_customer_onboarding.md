# Customer Onboarding Automation - Guía Completa

Sistema automatizado completo para onboarding de nuevos clientes que incluye recolección de información, verificación de identidad y activación automática de cuentas y servicios.

## 📋 Tabla de Contenidos

- [Descripción General](#-descripción-general)
- [Arquitectura del Sistema](#-arquitectura-del-sistema)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [Verificación de Identidad](#-verificación-de-identidad)
- [Activación de Servicios](#-activación-de-servicios)
- [Base de Datos](#-base-de-datos)
- [Métricas y Monitoreo](#-métricas-y-monitoreo)
- [Troubleshooting](#-troubleshooting)
- [Ejemplos](#-ejemplos)

## 🎯 Descripción General

Este sistema automatiza completamente el proceso de onboarding de nuevos clientes desde que se registran hasta que tienen acceso completo a todos los servicios. El proceso incluye:

✅ **Recolección de información**: Datos del cliente desde múltiples fuentes (CRM, formularios, APIs)  
✅ **Verificación de identidad**: Múltiples métodos (email OTP, SMS OTP, documentos, KYC providers)  
✅ **Activación automática**: Cuentas en plataforma, dashboard, API keys, facturación, soporte  
✅ **Persistencia completa**: Base de datos PostgreSQL con historial completo  
✅ **Auditoría**: Tracking de todos los eventos del proceso  
✅ **Métricas**: Monitoreo en tiempo real del proceso  

## 🏗️ Arquitectura del Sistema

### Componentes Principales

1. **Airflow DAG** (`customer_onboarding.py`): Orquestación principal del proceso
2. **Kestra Workflow** (`customer_onboarding.yaml`): Alternativa de orquestación con Kestra
3. **Integraciones** (`customer_onboarding_integrations.py`): Funciones de integración con servicios externos
4. **Base de Datos** (`customer_onboarding_schema.sql`): Schema completo con tablas y vistas

### Flujo del Proceso

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Validación y Preparación                                 │
│    - Validar datos del cliente                              │
│    - Generar idempotency key                                │
│    - Crear registro en BD                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. Recolección de Información                               │
│    - Enriquecer desde CRM (opcional)                        │
│    - Validar información de negocio                          │
│    - Persistir datos recolectados                           │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. Verificación de Identidad                                │
│    - Email OTP / SMS OTP / Document / KYC Provider          │
│    - Validar y persistir resultados                          │
│    - Actualizar estado de onboarding                        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. Activación de Servicios (si identidad verificada)        │
│    - Crear cuenta en plataforma                             │
│    - Activar dashboard                                       │
│    - Generar API keys                                        │
│    - Crear cuenta de facturación                            │
│    - Activar cuenta de soporte                              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ 5. Completar Onboarding                                     │
│    - Enviar email de bienvenida                             │
│    - Actualizar estado a completado                          │
│    - Registrar eventos finales                               │
│    - Notificaciones                                         │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# Base de datos
POSTGRES_CONN_ID=postgres_default  # Connection ID de Airflow

# CRM (opcional)
CRM_API_URL=https://api.crm.example.com
CRM_API_KEY=your_crm_api_key

# Email
EMAIL_API_URL=https://api.email.example.com
EMAIL_API_KEY=your_email_api_key

# SMS (opcional)
SMS_API_URL=https://api.sms.example.com
SMS_API_KEY=your_sms_api_key

# KYC Provider (opcional)
KYC_API_URL=https://api.kyc.example.com
KYC_API_KEY=your_kyc_api_key

# Plataforma
PLATFORM_API_URL=https://api.platform.example.com
PLATFORM_API_KEY=your_platform_api_key

# Facturación
BILLING_API_URL=https://api.billing.example.com
BILLING_API_KEY=your_billing_api_key

# URLs de servicios
DASHBOARD_URL=https://dashboard.example.com
SUPPORT_EMAIL=support@example.com
```

### Instalación del Schema

```sql
-- Ejecutar en PostgreSQL
\i data/db/customer_onboarding_schema.sql
```

### Configuración de Airflow

Asegúrate de tener configurada la conexión a PostgreSQL en Airflow:

```bash
# Airflow UI → Admin → Connections → Add
Connection Id: postgres_default
Connection Type: Postgres
Host: your-postgres-host
Schema: your_database
Login: your_user
Password: your_password
Port: 5432
```

## 🚀 Uso

### Trigger Manual desde Airflow UI

1. Ir a Airflow UI → DAGs → `customer_onboarding`
2. Click en "Trigger DAG w/ config"
3. Proporcionar parámetros JSON:

```json
{
  "customer_email": "cliente@empresa.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "company_name": "Empresa ABC",
  "phone": "+34612345678",
  "country": "ES",
  "service_plan": "premium",
  "service_tier": "enterprise",
  "services_to_activate": ["platform", "dashboard", "api", "billing"],
  "source": "website",
  "utm_source": "google",
  "utm_campaign": "adwords",
  "identity_verification_method": "email",
  "auto_activate_services": true,
  "send_welcome_email": true
}
```

### Trigger desde API

```bash
curl -X POST \
  https://airflow.example.com/api/v1/dags/customer_onboarding/dagRuns \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conf": {
      "customer_email": "cliente@empresa.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "company_name": "Empresa ABC",
      "service_plan": "premium",
      "services_to_activate": ["platform", "dashboard", "api"]
    }
  }'
```

### Trigger desde Kestra

```bash
curl -X POST \
  https://kestra.example.com/api/v1/executions/trigger/workflows.customer_onboarding \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "inputs": {
      "customer_email": "cliente@empresa.com",
      "first_name": "Juan",
      "last_name": "Pérez",
      "company_name": "Empresa ABC",
      "service_plan": "premium",
      "services_to_activate": ["platform", "dashboard", "api"]
    }
  }'
```

## 🔐 Verificación de Identidad

### Métodos Soportados

#### 1. Email (OTP)
- Genera código de 6 dígitos
- Envía email con código
- Expira en 15 minutos
- Configuración: `identity_verification_method: "email"`

#### 2. SMS (OTP)
- Genera código de 6 dígitos
- Envía SMS con código
- Expira en 10 minutos
- Requiere número de teléfono
- Configuración: `identity_verification_method: "sms"`

#### 3. Documento
- Verificación manual de documentos
- Requiere integración con proveedor de documentos
- Configuración: `identity_verification_method: "document"`

#### 4. KYC Provider
- Integración con proveedores externos (Sumsub, Onfido, Jumio, etc.)
- Verificación automática completa
- Configuración: `identity_verification_method: "kyc_provider"`

### Consultar Estado de Verificación

```sql
SELECT 
    customer_email,
    identity_verified,
    identity_verification_method,
    identity_verification_status,
    identity_verified_at
FROM customer_onboarding
WHERE customer_email = 'cliente@empresa.com';
```

## 🎯 Activación de Servicios

### Servicios Disponibles

- **platform**: Cuenta principal en la plataforma
- **dashboard**: Acceso al dashboard de cliente
- **api**: API keys y acceso a API
- **billing**: Cuenta de facturación (Stripe, etc.)
- **support**: Cuenta de soporte

### Verificar Cuentas Activadas

```sql
SELECT 
    ca.service_name,
    ca.account_status,
    ca.account_id,
    ca.activated_at
FROM customer_accounts ca
WHERE ca.customer_email = 'cliente@empresa.com'
ORDER BY ca.activated_at DESC;
```

## 📊 Base de Datos

### Tablas Principales

1. **customer_onboarding**: Registro principal de onboarding
2. **customer_onboarding_data**: Información recolectada
3. **customer_identity_verifications**: Verificaciones de identidad
4. **customer_accounts**: Cuentas y servicios activados
5. **customer_onboarding_events**: Eventos y auditoría

### Vistas Útiles

```sql
-- Métricas de onboarding
SELECT * FROM customer_onboarding_metrics
ORDER BY date DESC
LIMIT 30;

-- Resumen de cuentas por cliente
SELECT * FROM customer_accounts_summary
WHERE onboarding_status = 'completed';
```

## 📈 Métricas y Monitoreo

### Métricas Disponibles

- Total de onboardings iniciados
- Tasa de completación
- Tasa de verificación de identidad
- Tiempo promedio de completación
- Servicios más activados
- Fuentes de clientes

### Consultar Métricas

```sql
-- Métricas por día
SELECT 
    date,
    total_onboardings,
    completed,
    identity_verified,
    avg_hours_to_complete
FROM customer_onboarding_metrics
WHERE date >= CURRENT_DATE - INTERVAL '30 days'
ORDER BY date DESC;
```

## 🚨 Troubleshooting

### El onboarding no se completa

1. Verificar logs de Airflow/Kestra
2. Revisar estado en BD:

```sql
SELECT 
    customer_email,
    status,
    identity_verified,
    identity_verification_status,
    onboarding_started_at,
    onboarding_completed_at
FROM customer_onboarding
WHERE status != 'completed'
ORDER BY onboarding_started_at DESC;
```

### Verificación de identidad falla

```sql
SELECT 
    customer_email,
    verification_type,
    verification_status,
    error_message,
    created_at
FROM customer_identity_verifications
WHERE verification_status = 'failed'
ORDER BY created_at DESC;
```

### Servicios no se activan

```sql
SELECT 
    customer_email,
    service_name,
    account_status,
    error_message,
    activation_requested_at
FROM customer_accounts
WHERE account_status = 'failed'
ORDER BY activation_requested_at DESC;
```

## 📝 Ejemplos

### Ejemplo Completo de Onboarding

```json
{
  "customer_email": "nuevo.cliente@empresa.com",
  "first_name": "María",
  "last_name": "García",
  "company_name": "Tech Solutions SL",
  "phone": "+34612345678",
  "country": "ES",
  "timezone": "Europe/Madrid",
  "service_plan": "enterprise",
  "service_tier": "premium",
  "services_to_activate": [
    "platform",
    "dashboard",
    "api",
    "billing",
    "support"
  ],
  "source": "sales",
  "sales_rep_email": "vendedor@empresa.com",
  "identity_verification_method": "email",
  "auto_activate_services": true,
  "send_welcome_email": true,
  "metadata": {
    "contract_value": 50000,
    "payment_terms": "annual",
    "special_requirements": "Custom integration needed"
  }
}
```

### Webhook para Actualizar Estado de Verificación

```python
# Ejemplo: Actualizar verificación desde webhook externo
import requests

webhook_url = "https://airflow.example.com/api/v1/dags/customer_onboarding_webhook/dagRuns"

payload = {
    "conf": {
        "customer_email": "cliente@empresa.com",
        "event_type": "identity_verified",
        "verification_code": "123456",
        "verified": True
    }
}

response = requests.post(webhook_url, json=payload, auth=("user", "password"))
```

## 🔗 Referencias

- Schema: `/data/db/customer_onboarding_schema.sql`
- DAG Airflow: `/data/airflow/dags/customer_onboarding.py`
- Integraciones: `/data/airflow/plugins/customer_onboarding_integrations.py`
- Workflow Kestra: `/workflow/kestra/flows/customer_onboarding.yaml`

## 🔄 Componentes Adicionales

### Webhook Handler (`customer_onboarding_webhook.py`)

Maneja webhooks externos para actualizar el estado del onboarding:

- **Confirmación de verificación**: Actualiza estado cuando cliente confirma código OTP
- **Resultados KYC**: Recibe resultados de proveedores KYC externos
- **Activación de servicios**: Confirma cuando servicios se activan externamente
- **Actualización de datos**: Permite actualizar información del cliente

**Ejemplo de uso:**
```bash
curl -X POST \
  https://airflow.example.com/api/v1/dags/customer_onboarding_webhook/dagRuns \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "conf": {
      "event_type": "identity_verification_confirmed",
      "customer_email": "cliente@empresa.com",
      "payload": {
        "verification_method": "email",
        "verification_code": "123456"
      }
    }
  }'
```

### Reportes Automatizados (`customer_onboarding_reports.py`)

Genera reportes semanales automáticos (cada lunes a las 9 AM):

- Tasa de completación
- Métodos de verificación más usados
- Servicios más activados
- Tiempo promedio de onboarding
- Análisis de fuentes de clientes

### Reintentos Automáticos (`customer_onboarding_retry_failed.py`)

Reintenta automáticamente onboardings y servicios fallidos:

- Ejecuta cada 6 horas
- Identifica onboardings en estado 'failed'
- Reintenta activación de servicios fallidos
- Notifica resultados

### Validadores Avanzados (`customer_onboarding_validators.py`)

Validaciones adicionales:

- **Validación de dominio de email**: Detecta emails temporales, verifica formato
- **Validación de teléfono**: Valida formato según país
- **Validación de dominio de empresa**: Verifica coincidencia email-empresa
- **Validación de documentos**: DNI, NIE, pasaporte (España y otros)
- **Validación de información de negocio**: CIF, nombre de empresa
- **Detección de riesgo**: Analiza indicadores de fraude

**Ejemplo de uso:**
```python
from data.airflow.plugins.customer_onboarding_validators import (
    validate_customer_data_complete,
    check_risk_indicators
)

# Validación completa
result = validate_customer_data_complete(customer_data)
if not result["valid"]:
    # Manejar errores
    pass

# Verificación de riesgo
risk = check_risk_indicators(customer_data)
if risk["risk_level"] == "high":
    # Requerir revisión manual
    pass
```

## 📚 Próximas Mejoras

- [ ] Integración con más proveedores KYC
- [ ] Verificación biométrica
- [ ] Onboarding multi-idioma
- [ ] Dashboard de métricas en tiempo real
- [ ] Machine learning para detección de fraude
- [ ] Integración con sistemas de compliance
- [ ] Webhooks para notificaciones push
- [ ] Sistema de aprobaciones con flujos de trabajo

