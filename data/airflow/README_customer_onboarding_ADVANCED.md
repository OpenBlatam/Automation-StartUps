# Customer Onboarding - Funcionalidades Avanzadas

Guía de uso de las funcionalidades avanzadas del sistema de onboarding de clientes.

## 📋 Índice

- [Webhooks](#webhooks)
- [Validadores Avanzados](#validadores-avanzados)
- [Reportes](#reportes)
- [Reintentos Automáticos](#reintentos-automáticos)
- [Integración con Sistemas Externos](#integración-con-sistemas-externos)

## 🔗 Webhooks

### Configuración de Webhooks

El sistema soporta webhooks para recibir eventos externos y actualizar el estado del onboarding.

### Tipos de Eventos Soportados

#### 1. Confirmación de Verificación de Identidad

Actualiza el estado cuando un cliente confirma un código OTP:

```json
{
  "event_type": "identity_verification_confirmed",
  "customer_email": "cliente@empresa.com",
  "payload": {
    "verification_method": "email",
    "verification_code": "123456"
  }
}
```

#### 2. Resultado de Proveedor KYC

Recibe resultados de proveedores KYC externos (Sumsub, Onfido, etc.):

```json
{
  "event_type": "kyc_provider_result",
  "customer_email": "cliente@empresa.com",
  "payload": {
    "status": "verified",
    "provider": "sumsub",
    "response": {
      "verification_id": "abc123",
      "score": 95,
      "documents_verified": true
    }
  }
}
```

#### 3. Servicio Activado Externamente

Confirma cuando un servicio se activa desde un sistema externo:

```json
{
  "event_type": "service_activated",
  "customer_email": "cliente@empresa.com",
  "payload": {
    "service_name": "platform",
    "account_id": "acc_123456",
    "account_data": {
      "user_id": "usr_789",
      "api_key": "key_abc"
    }
  }
}
```

#### 4. Actualización de Datos del Cliente

Permite actualizar información del cliente:

```json
{
  "event_type": "customer_data_updated",
  "customer_email": "cliente@empresa.com",
  "payload": {
    "data": {
      "phone": "+34612345678",
      "company_name": "Nueva Empresa SL"
    }
  }
}
```

### Integración desde Tu Sistema

```python
import requests

def send_verification_confirmation(customer_email: str, code: str):
    """Enviar confirmación de verificación."""
    url = "https://airflow.example.com/api/v1/dags/customer_onboarding_webhook/dagRuns"
    
    payload = {
        "conf": {
            "event_type": "identity_verification_confirmed",
            "customer_email": customer_email,
            "payload": {
                "verification_method": "email",
                "verification_code": code
            }
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": "Bearer YOUR_TOKEN"},
        timeout=10
    )
    
    return response.json()
```

## ✅ Validadores Avanzados

### Validación de Email

```python
from data.airflow.plugins.customer_onboarding_validators import validate_email_domain

result = validate_email_domain("cliente@empresa.com")
# {
#   "valid": True,
#   "domain": "empresa.com",
#   "checks": {
#     "domain_format": {"status": "passed", ...},
#     "temporary_domain": None
#   }
# }
```

### Validación de Teléfono

```python
from data.airflow.plugins.customer_onboarding_validators import validate_phone_number

result = validate_phone_number("+34612345678", country="ES")
# {
#   "valid": True,
#   "phone": "+34612345678",
#   "checks": {
#     "length": {"status": "passed", ...},
#     "country_format": {"status": "passed", ...}
#   }
# }
```

### Validación de Documentos

```python
from data.airflow.plugins.customer_onboarding_validators import validate_document_format

# DNI español
result = validate_document_format("DNI", "12345678A", country="ES")
# {"valid": True, "checks": {...}}

# NIE español
result = validate_document_format("NIE", "X1234567A", country="ES")
# {"valid": True, "checks": {...}}
```

### Detección de Riesgo

```python
from data.airflow.plugins.customer_onboarding_validators import check_risk_indicators

customer_data = {
    "customer_email": "test@10minutemail.com",
    "company_name": "Test Corp",
    "phone": "+1234567890"
}

risk = check_risk_indicators(customer_data)
# {
#   "risk_score": 35,
#   "risk_level": "medium",
#   "risk_factors": [
#     "Temporary email domain detected",
#     "Email domain doesn't match company name"
#   ],
#   "recommendation": "manual_review"
# }
```

### Validación Completa

```python
from data.airflow.plugins.customer_onboarding_validators import validate_customer_data_complete

payload = {
    "customer_email": "cliente@empresa.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "company_name": "Empresa ABC",
    "phone": "+34612345678",
    "country": "ES"
}

result = validate_customer_data_complete(payload)
# {
#   "valid": True,
#   "errors": [],
#   "warnings": [],
#   "checks": {
#     "email": {...},
#     "phone": {...},
#     "business": {...},
#     "risk": {...}
#   }
# }
```

## 📊 Reportes

### Reporte Semanal

El DAG `customer_onboarding_reports` genera automáticamente reportes cada lunes.

**Métricas incluidas:**
- Total de onboardings iniciados
- Onboardings completados
- Tasa de completación
- Tiempo promedio de completación
- Distribución por métodos de verificación
- Servicios más activados
- Fuentes de clientes

### Consultar Reportes Manualmente

```sql
-- Ver métricas de la última semana
SELECT 
    date,
    total_onboardings,
    completed,
    completion_rate_pct,
    avg_hours_to_complete
FROM customer_onboarding_metrics
WHERE date >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY date DESC;
```

### Generar Reporte Personalizado

```python
from airflow.providers.postgres.hooks.postgres import PostgresHook

pg_hook = PostgresHook(postgres_conn_id="postgres_default")

# Onboardings por fuente
sql = """
    SELECT 
        source,
        COUNT(*) as total,
        COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed,
        ROUND(COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*), 2) as rate
    FROM customer_onboarding
    WHERE created_at >= CURRENT_DATE - INTERVAL '30 days'
    GROUP BY source
    ORDER BY total DESC
"""

results = pg_hook.get_records(sql)
```

## 🔄 Reintentos Automáticos

### Configuración

El DAG `customer_onboarding_retry_failed` se ejecuta cada 6 horas y:

1. Identifica onboardings en estado 'failed' (últimos 7 días)
2. Identifica servicios con activación fallida
3. Reintenta activación de servicios (límite de 20 por ejecución)
4. Notifica resultados

### Criterios de Reintento

- Onboardings en estado 'failed' no más antiguos de 7 días
- Servicios con `account_status = 'failed'`
- Solo si la identidad está verificada
- Solo si el onboarding no está rechazado

### Monitoreo

```sql
-- Ver servicios que necesitan reintento
SELECT 
    ca.customer_email,
    ca.service_name,
    ca.account_status,
    ca.error_message,
    ca.activation_requested_at,
    co.identity_verified
FROM customer_accounts ca
JOIN customer_onboarding co ON ca.customer_email = co.customer_email
WHERE ca.account_status = 'failed'
  AND ca.activation_requested_at >= NOW() - INTERVAL '7 days'
  AND co.identity_verified = TRUE
ORDER BY ca.activation_requested_at DESC;
```

## 🔌 Integración con Sistemas Externos

### Integración con CRM

```python
# En customer_onboarding_integrations.py
def enrich_from_crm(customer_email: str):
    crm_api_url = os.getenv("CRM_API_URL")
    crm_api_key = os.getenv("CRM_API_KEY")
    
    response = requests.get(
        f"{crm_api_url}/contacts/{customer_email}",
        headers={"Authorization": f"Bearer {crm_api_key}"}
    )
    
    if response.status_code == 200:
        return response.json()
    return None
```

### Integración con Proveedor KYC

```python
def verify_with_kyc_provider(customer_data: dict):
    kyc_api_url = os.getenv("KYC_API_URL")
    kyc_api_key = os.getenv("KYC_API_KEY")
    
    payload = {
        "email": customer_data["customer_email"],
        "first_name": customer_data["first_name"],
        "last_name": customer_data["last_name"],
        "country": customer_data.get("country")
    }
    
    response = requests.post(
        f"{kyc_api_url}/verify",
        headers={"Authorization": f"Bearer {kyc_api_key}"},
        json=payload
    )
    
    return response.json()
```

### Integración con Plataforma

```python
def create_platform_account(customer_data: dict):
    platform_api_url = os.getenv("PLATFORM_API_URL")
    platform_api_key = os.getenv("PLATFORM_API_KEY")
    
    payload = {
        "email": customer_data["customer_email"],
        "first_name": customer_data["first_name"],
        "last_name": customer_data["last_name"],
        "company": customer_data.get("company_name"),
        "plan": customer_data.get("service_plan")
    }
    
    response = requests.post(
        f"{platform_api_url}/accounts",
        headers={"Authorization": f"Bearer {platform_api_key}"},
        json=payload
    )
    
    return response.json()
```

## 🎯 Ejemplos de Uso Completo

### Flujo Completo con Validaciones

```python
from data.airflow.plugins.customer_onboarding_validators import (
    validate_customer_data_complete,
    check_risk_indicators
)

# 1. Validar datos
customer_data = {
    "customer_email": "cliente@empresa.com",
    "first_name": "Juan",
    "last_name": "Pérez",
    "company_name": "Empresa ABC",
    "phone": "+34612345678",
    "country": "ES",
    "service_plan": "premium"
}

validation = validate_customer_data_complete(customer_data)

if not validation["valid"]:
    # Manejar errores
    print(f"Errores: {validation['errors']}")
    return

# 2. Verificar riesgo
risk = check_risk_indicators(customer_data)

if risk["risk_level"] == "high":
    # Requerir aprobación manual
    print("Revisión manual requerida")
    return

# 3. Proceder con onboarding
# (disparar DAG o workflow)
```

### Webhook para Actualizar Estado

```python
import requests

def update_verification_status(customer_email: str, code: str):
    """Actualizar estado de verificación desde webhook."""
    
    airflow_url = "https://airflow.example.com"
    token = "YOUR_TOKEN"
    
    url = f"{airflow_url}/api/v1/dags/customer_onboarding_webhook/dagRuns"
    
    payload = {
        "conf": {
            "event_type": "identity_verification_confirmed",
            "customer_email": customer_email,
            "payload": {
                "verification_method": "email",
                "verification_code": code
            }
        }
    }
    
    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    
    if response.status_code == 200:
        print("Verificación actualizada correctamente")
    else:
        print(f"Error: {response.status_code}")
```

## 📚 Referencias

- DAG Principal: `/data/airflow/dags/customer_onboarding.py`
- Webhook Handler: `/data/airflow/dags/customer_onboarding_webhook.py`
- Reportes: `/data/airflow/dags/customer_onboarding_reports.py`
- Reintentos: `/data/airflow/dags/customer_onboarding_retry_failed.py`
- Validadores: `/data/airflow/plugins/customer_onboarding_validators.py`
- Integraciones: `/data/airflow/plugins/customer_onboarding_integrations.py`

