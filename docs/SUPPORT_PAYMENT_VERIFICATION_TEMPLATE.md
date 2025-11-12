# Template de Verificación de Pagos - Facturas Pendientes

## Descripción

Este template proporciona una respuesta empática y resolutiva para casos donde un cliente afirma haber pagado una factura, pero esta aún aparece como pendiente en el sistema.

**Impacto esperado**: Reduce escaladas en un 30-50% según casos de estudio.

## Características

- ✅ **Tono empático y profesional**: Reconoce la preocupación del cliente
- ✅ **Proceso transparente**: Explica cómo funciona la verificación de pagos
- ✅ **Pasos claros**: Guía al cliente sobre cómo rastrear su transacción
- ✅ **Compensación proactiva**: Ofrece crédito temporal mientras se verifica
- ✅ **Próximos pasos definidos**: Establece expectativas claras
- ✅ **Diseño profesional**: HTML responsive y bien estructurado

## Uso Básico

```python
from workflow.kestra.flows.lib.support_billing_payment_verification_template import (
    get_payment_verification_response_template
)

# Datos del ticket
ticket_data = {
    "ticket_id": "TKT-20241215-ABC123",
    "customer_name": "María González",
    "customer_email": "maria.gonzalez@example.com",
    "assigned_agent_name": "Carlos Rodríguez"
}

# Generar respuesta
response = get_payment_verification_response_template(
    ticket_data=ticket_data,
    invoice_number="FAC-2024-001234",
    invoice_amount=299.99,
    credit_amount=299.99,  # Crédito temporal
    payment_date="10 de diciembre de 2024",
    transaction_id="txn_abc123xyz789"
)

# Enviar email
send_email(
    to=ticket_data["customer_email"],
    subject=response["subject"],
    text_body=response["text_body"],
    html_body=response["html_body"]
)
```

## Parámetros

### Requeridos

- `ticket_data` (Dict): Datos del ticket que deben incluir:
  - `ticket_id`: ID del ticket
  - `customer_name`: Nombre del cliente
  - `customer_email`: Email del cliente (opcional, para envío)
  - `assigned_agent_name`: Nombre del agente (opcional)

### Opcionales

- `invoice_number` (str): Número de factura. Por defecto: "tu factura"
- `invoice_amount` (float): Monto de la factura. Por defecto: "el monto correspondiente"
- `credit_amount` (float): Monto del crédito temporal. Por defecto: "[monto]"
- `payment_date` (str): Fecha del pago reportado. Por defecto: "la semana pasada"
- `transaction_id` (str): ID de transacción. Por defecto: "tu transacción"

## Integración con Sistema de Soporte

### Detección Automática

El sistema puede detectar automáticamente estos casos usando:

```python
# Patrones de detección
keywords = [
    "pagado", "paid", "pagué", "pago realizado",
    "pendiente", "pending", "no aparece", "no se actualizó",
    "factura", "invoice", "cobro", "charge"
]

# Categorización
category = "billing"
subcategory = "payment_issue"
priority = "high"  # Generalmente alta prioridad
```

### Flujo Automatizado

1. **Detección**: Sistema detecta ticket con categoría "billing" y palabras clave relacionadas
2. **Extracción**: Extrae información de factura, monto, fecha del mensaje del cliente
3. **Generación**: Usa el template para generar respuesta personalizada
4. **Aplicación de crédito**: Aplica crédito temporal a la cuenta del cliente
5. **Envío**: Envía email con respuesta empática
6. **Seguimiento**: Crea tarea de seguimiento para verificar en 24-48 horas

### Ejemplo de Integración con Kestra

```yaml
id: handle_payment_verification_ticket
namespace: support

tasks:
  - id: detect_payment_issue
    type: io.kestra.plugin.scripts.python.Script
    script: |
      # Detectar si es un caso de verificación de pago
      if ticket.category == "billing" and "pagado" in ticket.description.lower():
          return {"is_payment_verification": True, "ticket_data": ticket}
      return {"is_payment_verification": False}

  - id: extract_invoice_info
    type: io.kestra.plugin.scripts.python.Script
    needs: detect_payment_issue
    script: |
      # Extraer información de factura del mensaje
      import re
      invoice_match = re.search(r'FAC-[\d-]+|factura\s+[\d]+', ticket.description, re.IGNORECASE)
      amount_match = re.search(r'\$?(\d+\.?\d*)', ticket.description)
      
      return {
          "invoice_number": invoice_match.group() if invoice_match else None,
          "invoice_amount": float(amount_match.group(1)) if amount_match else None
      }

  - id: generate_response
    type: io.kestra.plugin.scripts.python.Script
    needs: [detect_payment_issue, extract_invoice_info]
    script: |
      from workflow.kestra.flows.lib.support_billing_payment_verification_template import (
          get_payment_verification_response_template
      )
      
      response = get_payment_verification_response_template(
          ticket_data={{outputs.detect_payment_issue.ticket_data}},
          invoice_number={{outputs.extract_invoice_info.invoice_number}},
          invoice_amount={{outputs.extract_invoice_info.invoice_amount}},
          credit_amount={{outputs.extract_invoice_info.invoice_amount}}
      )
      
      return response

  - id: apply_credit
    type: io.kestra.plugin.scripts.python.Script
    needs: extract_invoice_info
    script: |
      # Aplicar crédito temporal a la cuenta
      apply_temporary_credit(
          customer_id={{ticket.customer_id}},
          amount={{outputs.extract_invoice_info.invoice_amount}},
          reason="Payment verification pending"
      )

  - id: send_email
    type: io.kestra.plugin.notifications.email.Email
    needs: generate_response
    to: {{ticket.customer_email}}
    subject: {{outputs.generate_response.subject}}
    html: {{outputs.generate_response.html_body}}
```

## Instrucciones de Rastreo de Pagos

El módulo también incluye instrucciones detalladas para rastrear pagos:

```python
from workflow.kestra.flows.lib.support_billing_payment_verification_template import (
    get_payment_tracking_instructions
)

instructions = get_payment_tracking_instructions()

# Incluye:
# - Pasos para rastrear transacciones
# - Retrasos comunes por método de pago
# - Cuándo contactar a soporte
```

## Personalización

### Modificar el Crédito Temporal

```python
# Crédito del mismo monto
credit_amount = invoice_amount

# Crédito del 10% del monto
credit_amount = invoice_amount * 0.1

# Crédito fijo
credit_amount = 50.00
```

### Personalizar el Tono

El template está diseñado para ser empático pero profesional. Para ajustar el tono, modifica el archivo `support_billing_payment_verification_template.py`.

## Métricas y Seguimiento

### KPIs a Monitorear

- **Tasa de resolución automática**: % de casos resueltos sin escalación
- **Tiempo de respuesta**: Tiempo desde creación del ticket hasta respuesta
- **Satisfacción del cliente**: Score después de usar el template
- **Tasa de escalación**: % de casos que requieren intervención humana

### Registro de Uso

```python
# Registrar uso del template
template_manager.record_template_usage(
    template_id="billing_payment_verification_pending",
    ticket_id=ticket_data["ticket_id"],
    satisfaction_score=4.5  # Si el cliente califica
)
```

## Mejores Prácticas

1. **Respuesta rápida**: Enviar la respuesta dentro de las primeras 2 horas
2. **Aplicar crédito inmediatamente**: No esperar a verificar el pago
3. **Seguimiento proactivo**: Verificar el pago en 24-48 horas
4. **Comunicación clara**: Mantener al cliente informado del progreso
5. **Documentación**: Guardar comprobantes y referencias de transacción

## Casos de Uso

### Caso 1: Pago con Tarjeta de Crédito
- **Retraso típico**: 1-3 días hábiles
- **Acción**: Aplicar crédito temporal, verificar con procesador de pagos

### Caso 2: Transferencia Bancaria
- **Retraso típico**: 3-5 días hábiles
- **Acción**: Aplicar crédito temporal, verificar con banco

### Caso 3: Pago en Fin de Semana
- **Retraso típico**: +1-2 días hábiles adicionales
- **Acción**: Explicar retraso, aplicar crédito temporal

### Caso 4: Pago Rechazado pero Cargo Realizado
- **Retraso típico**: Requiere investigación
- **Acción**: Escalar a equipo de facturación, aplicar crédito temporal

## Troubleshooting

### El cliente no recibe el email
- Verificar dirección de email
- Revisar logs de envío
- Verificar spam/correo no deseado

### El crédito no se aplica
- Verificar sistema de facturación
- Revisar permisos de aplicación de créditos
- Verificar límites de crédito del cliente

### El pago nunca se encuentra
- Escalar a equipo de facturación
- Contactar procesador de pagos directamente
- Considerar reembolso o ajuste manual

## Versión Avanzada

Para funcionalidades avanzadas, consulta el módulo mejorado:

```python
from workflow.kestra.flows.lib.support_billing_payment_verification_advanced import (
    get_advanced_payment_verification_template,
    PaymentScenario,
    CustomerTier
)

response = get_advanced_payment_verification_template(
    ticket_data=ticket_data,
    invoice_number="FAC-2024-001234",
    invoice_amount=299.99,
    scenario=PaymentScenario.RECENT_PAYMENT,
    customer_tier=CustomerTier.VIP,
    language="es"
)
```

### Características Avanzadas

- **Detección automática de escenarios**: Pago reciente, antiguo, múltiples facturas, problemas recurrentes
- **Personalización por nivel de cliente**: Standard, Premium, VIP, Enterprise
- **Soporte multi-idioma**: Español, Inglés, Portugués, Francés
- **Integración con créditos**: Aplicación automática de créditos temporales
- **Analytics y métricas**: Tracking completo para análisis
- **Respuestas adaptativas**: Tono y contenido según urgencia

### Workflow de Automatización

Ver: `workflow/kestra/flows/payment_verification_automation.yaml`

Este workflow automatiza completamente el proceso:
1. Detección automática de tickets
2. Análisis inteligente del escenario
3. Cálculo de crédito apropiado
4. Generación de respuesta personalizada
5. Aplicación de crédito
6. Envío de email
7. Seguimiento programado
8. Tracking de métricas

## Referencias

- [Sistema de Templates de Soporte](./support_ticket_templates.py)
- [Templates de Email](./support_email_templates.py)
- [Chatbot de Soporte](./support_chatbot.py)
- [Ejemplo de Uso](../../scripts/support_payment_verification_example.py)
- [Ejemplo Avanzado](../../scripts/support_payment_verification_advanced_example.py)
- [Template Avanzado](../workflow/kestra/flows/lib/support_billing_payment_verification_advanced.py)
- [Workflow de Automatización](../workflow/kestra/flows/payment_verification_automation.yaml)

## Contribuciones

Para mejorar este template:

1. Revisar feedback de clientes
2. Analizar métricas de satisfacción
3. Ajustar tono y contenido según resultados
4. Actualizar instrucciones de rastreo según nuevos métodos de pago

