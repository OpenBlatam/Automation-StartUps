# 📋 Ejemplos de Uso - Customer Action Automation

## 🚀 Cómo Activar el Workflow

### Opción 1: Usando cURL

#### Activar Recuperación de Carrito Abandonado

```bash
curl -X POST https://your-n8n-instance.com/webhook/cart-abandonment \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "cart_abandonment",
    "customerId": "customer_12345",
    "email": "juan.perez@example.com",
    "firstName": "Juan",
    "lastName": "Pérez",
    "cartId": "cart_67890",
    "cartValue": 150.00,
    "cartItems": [
      {
        "name": "Camiseta Premium",
        "price": 75.00,
        "quantity": 2
      }
    ],
    "sessionId": "session_abc123"
  }'
```

#### Activar Seguimiento de Visita a Página

```bash
curl -X POST https://your-n8n-instance.com/webhook/page-visit \
  -H "Content-Type: application/json" \
  -d '{
    "eventType": "page_visit",
    "customerId": "customer_12345",
    "email": "juan.perez@example.com",
    "firstName": "Juan",
    "pageUrl": "https://yourdomain.com/product/camiseta-premium",
    "pageCategory": "product",
    "productName": "Camiseta Premium",
    "sessionId": "session_abc123"
  }'
```

### Opción 2: Usando JavaScript (Frontend)

#### Desde tu sitio web (ejemplo con fetch)

```javascript
// Detectar abandono de carrito
function trackCartAbandonment(cartData) {
  fetch('https://your-n8n-instance.com/webhook/cart-abandonment', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      eventType: 'cart_abandonment',
      customerId: cartData.customerId || getOrCreateCustomerId(),
      email: cartData.email,
      firstName: cartData.firstName,
      lastName: cartData.lastName,
      cartId: cartData.cartId,
      cartValue: cartData.total,
      cartItems: cartData.items.map(item => ({
        name: item.name,
        price: item.price,
        quantity: item.quantity
      })),
      sessionId: getSessionId()
    })
  }).catch(error => {
    console.error('Error tracking cart abandonment:', error);
  });
}

// Detectar visita a página
function trackPageVisit(pageData) {
  fetch('https://your-n8n-instance.com/webhook/page-visit', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      eventType: 'page_visit',
      customerId: pageData.customerId || getOrCreateCustomerId(),
      email: pageData.email,
      firstName: pageData.firstName,
      pageUrl: window.location.href,
      pageCategory: determinePageCategory(),
      productName: pageData.productName,
      sessionId: getSessionId()
    })
  }).catch(error => {
    console.error('Error tracking page visit:', error);
  });
}
```

### Opción 3: Usando Python (Backend)

```python
import requests
import json

def trigger_cart_abandonment(customer_data, cart_data):
    """Activa workflow de recuperación de carrito"""
    webhook_url = "https://your-n8n-instance.com/webhook/cart-abandonment"
    
    payload = {
        "eventType": "cart_abandonment",
        "customerId": customer_data.get("customer_id"),
        "email": customer_data.get("email"),
        "firstName": customer_data.get("first_name"),
        "lastName": customer_data.get("last_name"),
        "cartId": cart_data.get("cart_id"),
        "cartValue": float(cart_data.get("total", 0)),
        "cartItems": [
            {
                "name": item.get("name"),
                "price": float(item.get("price", 0)),
                "quantity": int(item.get("quantity", 1))
            }
            for item in cart_data.get("items", [])
        ],
        "sessionId": cart_data.get("session_id")
    }
    
    response = requests.post(
        webhook_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()

def trigger_page_visit(customer_data, page_data):
    """Activa workflow de seguimiento de navegación"""
    webhook_url = "https://your-n8n-instance.com/webhook/page-visit"
    
    payload = {
        "eventType": "page_visit",
        "customerId": customer_data.get("customer_id"),
        "email": customer_data.get("email"),
        "firstName": customer_data.get("first_name"),
        "pageUrl": page_data.get("url"),
        "pageCategory": page_data.get("category", "general"),
        "productName": page_data.get("product_name"),
        "sessionId": page_data.get("session_id")
    }
    
    response = requests.post(
        webhook_url,
        json=payload,
        headers={"Content-Type": "application/json"}
    )
    
    return response.json()
```

## 📦 Ejemplos de Payloads Completos

### Ejemplo 1: Carrito Abandonado - Cliente de Alto Valor

```json
{
  "eventType": "cart_abandonment",
  "customerId": "customer_vip_001",
  "email": "maria.garcia@example.com",
  "firstName": "María",
  "lastName": "García",
  "cartId": "cart_20240101_001",
  "cartValue": 250.00,
  "cartItems": [
    {
      "name": "Producto Premium A",
      "price": 150.00,
      "quantity": 1
    },
    {
      "name": "Producto Premium B",
      "price": 100.00,
      "quantity": 1
    }
  ],
  "sessionId": "session_abc123xyz",
  "phone": "+34612345678",
  "mobile": "+34612345678"
}
```

**Resultado Esperado**:
- Segmento: `high_value`
- Descuento final: 15% (código VIP15)
- Mensajes personalizados premium

### Ejemplo 2: Carrito Abandonado - Cliente Regular

```json
{
  "eventType": "cart_abandonment",
  "customerId": "customer_regular_002",
  "email": "pedro.lopez@example.com",
  "firstName": "Pedro",
  "lastName": "López",
  "cartId": "cart_20240101_002",
  "cartValue": 75.50,
  "cartItems": [
    {
      "name": "Producto Estándar",
      "price": 45.00,
      "quantity": 1
    },
    {
      "name": "Accesorio",
      "price": 30.50,
      "quantity": 1
    }
  ],
  "sessionId": "session_def456uvw"
}
```

**Resultado Esperado**:
- Segmento: `medium_value`
- Descuento final: 10% (código SAVE10)
- Mensajes estándar

### Ejemplo 3: Visita a Página de Producto

```json
{
  "eventType": "page_visit",
  "customerId": "customer_003",
  "email": "ana.martinez@example.com",
  "firstName": "Ana",
  "lastName": "Martínez",
  "pageUrl": "https://yourdomain.com/product/camiseta-premium-2024",
  "pageCategory": "product",
  "productName": "Camiseta Premium 2024",
  "sessionId": "session_ghi789rst",
  "timeOnPage": 120
}
```

**Resultado Esperado**:
- Espera 5 minutos
- Mensaje: "¿Interesado en Camiseta Premium 2024?"
- CTA: Ver Producto

### Ejemplo 4: Visita a Página de Precios

```json
{
  "eventType": "page_visit",
  "customerId": "customer_004",
  "email": "carlos.rodriguez@example.com",
  "firstName": "Carlos",
  "lastName": "Rodríguez",
  "pageUrl": "https://yourdomain.com/pricing",
  "pageCategory": "pricing",
  "sessionId": "session_jkl012mno"
}
```

**Resultado Esperado**:
- Espera 5 minutos
- Mensaje: "¿Listo para comenzar?"
- CTA: Agendar Demo

### Ejemplo 5: Visita a Blog

```json
{
  "eventType": "page_visit",
  "customerId": "customer_005",
  "email": "laura.sanchez@example.com",
  "firstName": "Laura",
  "lastName": "Sánchez",
  "pageUrl": "https://yourdomain.com/blog/guia-completa-producto",
  "pageCategory": "blog",
  "articleTitle": "Guía Completa del Producto",
  "sessionId": "session_pqr345stu"
}
```

**Resultado Esperado**:
- Espera 5 minutos
- Mensaje: "Más contenido que te puede interesar"
- CTA: Ver Más Contenido

## 🔄 Integración con E-commerce

### Shopify

```javascript
// En tu tema Shopify (theme.liquid o checkout)
document.addEventListener('DOMContentLoaded', function() {
  // Detectar abandono de carrito
  if (window.location.pathname.includes('/cart')) {
    const cartData = {
      customerId: '{{ customer.id }}',
      email: '{{ customer.email }}',
      firstName: '{{ customer.first_name }}',
      lastName: '{{ customer.last_name }}',
      cartId: '{{ cart.token }}',
      cartValue: {{ cart.total_price | divided_by: 100.0 }},
      cartItems: [
        {% for item in cart.items %}
        {
          name: '{{ item.title }}',
          price: {{ item.price | divided_by: 100.0 }},
          quantity: {{ item.quantity }}
        }{% unless forloop.last %},{% endunless %}
        {% endfor %}
      ]
    };
    
    // Enviar después de 30 segundos de inactividad
    setTimeout(() => {
      trackCartAbandonment(cartData);
    }, 30000);
  }
});
```

### WooCommerce

```php
// En functions.php de tu tema WordPress
add_action('woocommerce_cart_updated', 'track_cart_abandonment');

function track_cart_abandonment() {
    if (is_user_logged_in()) {
        $user = wp_get_current_user();
        $cart = WC()->cart;
        
        $cart_data = array(
            'eventType' => 'cart_abandonment',
            'customerId' => (string) $user->ID,
            'email' => $user->user_email,
            'firstName' => $user->first_name,
            'lastName' => $user->last_name,
            'cartId' => WC()->session->get_customer_id(),
            'cartValue' => $cart->get_total(''),
            'cartItems' => array()
        );
        
        foreach ($cart->get_cart() as $cart_item) {
            $cart_data['cartItems'][] = array(
                'name' => $cart_item['data']->get_name(),
                'price' => $cart_item['data']->get_price(),
                'quantity' => $cart_item['quantity']
            );
        }
        
        // Enviar después de 1 minuto de inactividad
        wp_schedule_single_event(time() + 60, 'send_cart_abandonment_webhook', array($cart_data));
    }
}
```

## 🧪 Testing

### Test Manual con Postman

1. **Importar Collection**:
   - Crea una nueva collection en Postman
   - Agrega dos requests: "Cart Abandonment" y "Page Visit"

2. **Configurar Request**:
   - Method: POST
   - URL: `https://your-n8n-instance.com/webhook/cart-abandonment`
   - Headers: `Content-Type: application/json`
   - Body: Usa uno de los ejemplos de payload arriba

3. **Ejecutar y Verificar**:
   - Envía el request
   - Verifica respuesta (debe ser `{"success": true}`)
   - Revisa logs en n8n
   - Confirma que el workflow se activó

### Test Automatizado

```python
import unittest
import requests
from datetime import datetime

class TestCustomerAutomation(unittest.TestCase):
    BASE_URL = "https://your-n8n-instance.com/webhook"
    
    def test_cart_abandonment_high_value(self):
        """Test carrito abandonado de alto valor"""
        payload = {
            "eventType": "cart_abandonment",
            "customerId": f"test_{datetime.now().timestamp()}",
            "email": "test@example.com",
            "firstName": "Test",
            "cartId": f"cart_test_{datetime.now().timestamp()}",
            "cartValue": 150.00,
            "cartItems": [{"name": "Test Product", "price": 150.00, "quantity": 1}]
        }
        
        response = requests.post(
            f"{self.BASE_URL}/cart-abandonment",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())
    
    def test_page_visit_product(self):
        """Test visita a página de producto"""
        payload = {
            "eventType": "page_visit",
            "customerId": f"test_{datetime.now().timestamp()}",
            "email": "test@example.com",
            "pageUrl": "https://example.com/product/test",
            "pageCategory": "product",
            "productName": "Test Product"
        }
        
        response = requests.post(
            f"{self.BASE_URL}/page-visit",
            json=payload
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.json())

if __name__ == '__main__':
    unittest.main()
```

## 📊 Monitoreo de Resultados

### Verificar que el Workflow Funcionó

1. **En n8n**:
   - Ve a "Executions"
   - Busca ejecuciones recientes
   - Verifica que todos los nodos se ejecutaron correctamente

2. **En tu Email**:
   - Revisa la bandeja de entrada (o spam)
   - Confirma que recibiste el mensaje
   - Verifica personalización y contenido

3. **En Tracking**:
   - Revisa tu sistema de analytics
   - Confirma que el evento se registró
   - Verifica métricas de apertura y clics

## ⚠️ Consideraciones Importantes

### Privacidad y GDPR

- Asegúrate de tener consentimiento del usuario
- Incluye opción de opt-out en todos los emails
- Respeta preferencias de comunicación
- Cumple con regulaciones locales

### Rate Limiting

- No envíes múltiples webhooks para el mismo evento
- Implementa deduplicación
- Respeta límites de tu proveedor de email/SMS

### Testing en Producción

- Usa datos de prueba primero
- Verifica que no se envíen emails reales durante testing
- Monitorea logs cuidadosamente
- Ten un plan de rollback

---

**Última Actualización**: 2024-01-01




