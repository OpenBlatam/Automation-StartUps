# ⚡ Quick Start - Customer Action Automation

## 🎯 ¿Qué hace este workflow?

Automatiza respuestas a acciones específicas de clientes:
- ✅ **Recuperación de carritos abandonados** con mensajes escalonados
- ✅ **Seguimiento de navegación** en el sitio web
- ✅ **Personalización** según valor del cliente
- ✅ **Multi-canal** (Email + SMS opcional)

## 🚀 Inicio Rápido (5 minutos)

### Paso 1: Importar Workflow

1. Abre n8n
2. Ve a **Workflows** > **Import from File**
3. Selecciona `n8n_workflow_customer_automation.json`
4. Click en **Import**

### Paso 2: Configurar Credenciales

1. **SMTP (Requerido para emails)**:
   - Settings > Credentials > Add Credential
   - Tipo: SMTP
   - Configura tu servidor de email

2. **Twilio (Opcional para SMS)**:
   - Settings > Credentials > Add Credential
   - Tipo: Twilio API
   - Agrega Account SID y Auth Token

### Paso 3: Configurar Variables de Entorno

En n8n Settings > Environment Variables:

```bash
FROM_EMAIL=noreply@yourdomain.com
REPLY_TO_EMAIL=support@yourdomain.com
API_BASE_URL=https://api.yourdomain.com
API_KEY=your_api_key_here
```

### Paso 4: Activar Workflow

1. Click en **Active** toggle (arriba a la derecha)
2. Copia las URLs de los webhooks:
   - Cart Abandonment: `https://your-n8n.com/webhook/cart-abandonment`
   - Page Visit: `https://your-n8n.com/webhook/page-visit`

### Paso 5: Probar

Usa cURL o Postman para enviar un test:

```bash
curl -X POST https://your-n8n.com/webhook/cart-abandonment \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "cart_abandonment",
    "email": "test@example.com",
    "firstName": "Test",
    "cartId": "test_cart_123",
    "cartValue": 100.00,
    "cartItems": [{"name": "Test Product", "price": 100.00, "quantity": 1}]
  }'
```

## 📋 Estructura del Workflow

```
Triggers (Webhooks)
    ↓
Filtros de Eventos
    ↓
Enriquecimiento de Datos
    ↓
Lógica Condicional
    ↓
Períodos de Espera
    ↓
Generación de Mensajes
    ↓
Envío (Email/SMS)
    ↓
Tracking
```

## ⏱️ Timing Configurado

### Carrito Abandonado:
- **1 hora**: Primer recordatorio (sin descuento)
- **24 horas**: Segundo recordatorio (10% descuento)
- **72 horas**: Último recordatorio (10-15% según segmento)

### Visita a Página:
- **5 minutos**: Espera antes de enviar seguimiento

## 🎨 Personalización Rápida

### Cambiar Timing

Edita los nodos **Wait**:
- `Wait 1 Hour` → Cambia `amount` y `unit`
- `Wait 24 Hours` → Ajusta según necesidad
- `Wait 72 Hours` → Modifica timing final

### Cambiar Mensajes

Edita el nodo **Generate Message Content**:
- Modifica los templates
- Ajusta descuentos
- Personaliza tono

### Cambiar Segmentos

Edita el nodo **Enrich Customer Data**:
- Ajusta umbrales de valor:
  - `high_value`: > $100
  - `medium_value`: $50-$100
  - `low_value`: < $50

## 🔗 Integración con tu Sistema

### Opción 1: Desde tu E-commerce

Agrega este código JavaScript cuando detectes abandono:

```javascript
fetch('https://your-n8n.com/webhook/cart-abandonment', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    eventType: 'cart_abandonment',
    email: customerEmail,
    firstName: customerFirstName,
    cartId: cartId,
    cartValue: cartTotal,
    cartItems: cartItems
  })
});
```

### Opción 2: Desde tu Backend

```python
import requests

requests.post(
    'https://your-n8n.com/webhook/cart-abandonment',
    json={
        'eventType': 'cart_abandonment',
        'email': customer.email,
        'cartId': cart.id,
        'cartValue': cart.total,
        'cartItems': [{'name': item.name, 'price': item.price, 'quantity': item.quantity} for item in cart.items]
    }
)
```

## 📊 Verificar que Funciona

1. **En n8n**: Ve a "Executions" y verifica ejecuciones
2. **En tu email**: Revisa bandeja de entrada
3. **En logs**: Confirma que no hay errores

## 🆘 Problemas Comunes

### ❌ No se envían emails
- ✅ Verifica credenciales SMTP
- ✅ Revisa que FROM_EMAIL esté configurado
- ✅ Confirma que workflow está activo

### ❌ Webhook no responde
- ✅ Verifica que workflow está activo
- ✅ Confirma URL del webhook
- ✅ Revisa formato del payload

### ❌ Mensajes duplicados
- ✅ Implementa deduplicación
- ✅ Verifica que no se dispara múltiples veces
- ✅ Revisa lógica de filtros

## 📚 Documentación Completa

- **README_CUSTOMER_AUTOMATION.md**: Documentación completa
- **EXAMPLES_CUSTOMER_AUTOMATION.md**: Ejemplos de uso
- **Este archivo**: Quick start

## 🎯 Próximos Pasos

1. ✅ Importa el workflow
2. ✅ Configura credenciales
3. ✅ Prueba con datos de test
4. ✅ Integra con tu sistema
5. ✅ Monitorea resultados
6. ✅ Optimiza según datos

---

**¿Necesitas ayuda?** Revisa la documentación completa en `README_CUSTOMER_AUTOMATION.md`










