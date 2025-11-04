# Integración Automática: Reembolsos Stripe → QuickBooks

## 📋 Resumen

Sistema automatizado completo que procesa reembolsos de Stripe y crea automáticamente notas de crédito en QuickBooks Online. La integración está completamente integrada en el stack existente.

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Stripe Webhook │  (Evento: charge.refunded)
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Kestra Workflow                │
│  (stripe_refund_to_quickbooks)  │
│  - Verifica firma               │
│  - Parsea datos                 │
│  - Busca en BD                  │
│  - Trigger Airflow DAG          │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Airflow DAG                    │
│  (stripe_refund_to_quickbooks)  │
│  - Procesa reembolso            │
│  - Crea nota de crédito en QB   │
│  - Guarda resultado en BD      │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  QuickBooks API                 │
│  - CreditMemo creado            │
│  - Linkeado a recibo original   │
└─────────────────────────────────┘
```

### Componentes del Stack

1. **Kestra Workflow** (`workflow/kestra/flows/stripe_refund_to_quickbooks.yaml`)
   - Webhook endpoint para eventos de Stripe
   - Verificación de firma HMAC
   - Parsing y validación de datos
   - Lookup en BD para obtener `qb_receipt_id`
   - Trigger automático del DAG de Airflow

2. **Airflow DAG** (`data/airflow/dags/stripe_refund_to_quickbooks.py`)
   - Procesamiento del reembolso
   - Integración con QuickBooks API
   - Creación de CreditMemo
   - Persistencia de resultados

3. **Email Detector (Opcional)** (`data/airflow/dags/stripe_refund_email_detector.py`)
   - Detección de correos de reembolsos desde Gmail
   - Procesamiento automático como backup

4. **Base de Datos**
   - Tabla `stripe_refunds` para tracking
   - Tabla `payments` para lookup de recibos

## 🚀 Configuración

### 1. Variables de Entorno Requeridas

#### QuickBooks
```bash
QUICKBOOKS_ACCESS_TOKEN=<oauth_token>
QUICKBOOKS_REALM_ID=<company_id>
QUICKBOOKS_ENVIRONMENT=production  # o "sandbox"
QUICKBOOKS_REFUND_ITEM_ID=<item_id>  # Opcional
```

#### Stripe (para Kestra)
```bash
STRIPE_SIGNING_SECRET=<webhook_signing_secret>
```

#### Airflow (para Kestra)
```bash
AIRFLOW_BASE_URL=https://airflow.example.com
AIRFLOW_TOKEN=<api_token>  # Opcional
```

### 2. Configurar Webhook en Stripe

1. Ir a Stripe Dashboard → Developers → Webhooks
2. Agregar endpoint: `https://kestra.example.com/api/v1/webhooks/stripe-refund`
3. Seleccionar evento: `charge.refunded`
4. Copiar `Signing secret` → configurar en `STRIPE_SIGNING_SECRET`

### 3. Configurar Kestra Workflow

Editar `workflow/kestra/flows/stripe_refund_to_quickbooks.yaml` con:
- `airflow_base_url`: URL de tu instancia de Airflow
- `jdbc_url`, `jdbc_user`, `jdbc_password`: Credenciales de BD

### 4. Configurar Airflow DAG

El DAG se carga automáticamente. Asegurar que las variables de QuickBooks estén configuradas en Airflow.

## 📊 Flujo de Datos

### 1. Evento de Reembolso en Stripe

```json
{
  "type": "charge.refunded",
  "data": {
    "object": {
      "id": "re_1234567890",
      "amount": 10050,
      "currency": "usd",
      "charge": "ch_1234567890",
      "customer": "cus_1234567890",
      "reason": "requested_by_customer"
    }
  }
}
```

### 2. Procesamiento en Kestra

- ✅ Verifica firma HMAC
- ✅ Parsea datos del reembolso
- ✅ Busca en BD: `payments` → obtiene `qb_receipt_id`
- ✅ Valida datos requeridos
- ✅ Guarda registro inicial en `stripe_refunds`
- ✅ Trigger DAG de Airflow con datos

### 3. Procesamiento en Airflow

- ✅ Recibe datos desde `conf` (webhook) o `params` (manual)
- ✅ Busca cliente en QuickBooks por email
- ✅ Crea CreditMemo en QuickBooks
- ✅ Linkea al recibo original
- ✅ Actualiza `stripe_refunds` con resultado

### 4. Respuesta

```json
{
  "status": "Éxito",
  "qb_credit_id": "123",
  "credit_memo": { ... }
}
```

## 🔍 Uso Manual

### Trigger desde Airflow UI

1. Ir a DAG: `stripe_refund_to_quickbooks`
2. Click en "Trigger DAG w/ config"
3. Configurar parámetros:

```json
{
  "stripe_refund_id": "re_1234567890",
  "monto_reembolso": 100.50,
  "correo_cliente": "cliente@example.com",
  "qb_receipt_id": "123"
}
```

### Llamada Directa a Función

```python
from data.airflow.dags.stripe_refund_to_quickbooks import procesar_reembolso_stripe_quickbooks

resultado = procesar_reembolso_stripe_quickbooks(
    stripe_refund_id="re_1234567890",
    monto_reembolso=100.50,
    correo_cliente="cliente@example.com",
    qb_receipt_id="123"
)

print(f"Status: {resultado['status']}")
print(f"QB Credit ID: {resultado['qb_credit_id']}")
```

## 📈 Monitoreo

### Tabla `stripe_refunds`

```sql
SELECT 
    stripe_refund_id,
    amount,
    customer_email,
    qb_receipt_id,
    qb_credit_id,
    status,
    created_at,
    processed_at
FROM stripe_refunds
ORDER BY created_at DESC;
```

### Estados

- `pending`: Registrado, esperando procesamiento
- `triggered`: DAG triggerado, en proceso
- `completed`: Nota de crédito creada exitosamente
- `failed`: Error en el procesamiento

## 🛠️ Troubleshooting

### Error: "Cliente no encontrado en QuickBooks"

- Verificar que el email del cliente existe en QuickBooks
- Revisar que el email en Stripe coincida con QuickBooks
- Verificar permisos de OAuth en QuickBooks

### Error: "qb_receipt_id no encontrado"

- Verificar que el pago original está en la tabla `payments`
- Asegurar que `metadata->>'qb_receipt_id'` está guardado al crear el pago

### Error: "QuickBooks API timeout"

- Verificar conectividad a QuickBooks
- Revisar que el token OAuth no haya expirado
- Verificar rate limits de QuickBooks API

## 🔐 Seguridad

- ✅ Verificación HMAC de firmas de Stripe
- ✅ Tokens OAuth almacenados en variables de entorno
- ✅ Validación de parámetros en cada paso
- ✅ Manejo seguro de errores sin exponer información sensible

## 📝 Notas Adicionales

- El sistema soporta tanto webhooks automáticos como triggers manuales
- La integración con Gmail es opcional y funciona como backup
- Los reembolsos se rastrean en BD para auditoría completa
- Soporta sandbox y producción de QuickBooks



