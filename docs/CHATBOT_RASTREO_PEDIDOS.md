# 🤖 Chatbot de Rastreo de Pedidos - Documentación Completa

## 📋 Resumen Ejecutivo

Sistema completo de chatbot especializado en rastreo de pedidos para e-commerce que automatiza el **70% de consultas de entrega**. El bot ayuda a los clientes a:

- ✅ Rastrear pedidos con ID
- ✅ Obtener actualizaciones en tiempo real
- ✅ Consultar estado de pagos
- ✅ Conocer fechas de entrega
- ✅ Escalar automáticamente a soporte humano cuando es necesario

**Tono:** Amigable y confiado, alineado con la voz de la marca.

---

## 🎯 Características Principales

### ✨ Funcionalidades Core

1. **Rastreo de Pedidos**
   - Búsqueda por ID de pedido
   - Actualizaciones en tiempo real
   - Historial completo de tracking
   - Información de carrier y número de seguimiento

2. **Consultas de Pago**
   - Estado del pago
   - Historial de transacciones
   - Información de métodos de pago
   - Detalles de transacciones

3. **Información de Entrega**
   - Fechas estimadas de entrega
   - Fechas reales de entrega
   - Estado actual del envío
   - Ubicación del paquete

4. **Detección Automática de Problemas** 🆕
   - Detección de retrasos en entregas
   - Identificación de problemas de pago
   - Detección de problemas con direcciones
   - Clasificación por severidad
   - Sugerencias automáticas de acción
   - Integración en respuestas

5. **Escalación Inteligente**
   - Detección automática de casos complejos
   - Escalación basada en problemas detectados
   - Creación de tickets de soporte
   - Notificación al cliente
   - Transición fluida a agente humano

6. **Multi-Canal**
   - Telegram
   - WhatsApp (vía webhook)
   - Web (API REST)
   - Integración con n8n

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Cliente       │
│  (Telegram/Web) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   n8n Workflow  │
│   (Opcional)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API REST       │
│  (Flask)        │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│ Chatbot│ │  PostgreSQL   │
│ Engine │ │  (Orders DB)  │
└────────┘ └──────────────┘
    │
    ▼
┌──────────────┐
│ Support API  │
│ (Escalación) │
└──────────────┘
```

---

## 🚀 Instalación Rápida

### 1. Requisitos

```bash
pip install flask flask-cors psycopg2-binary
```

### 2. Configurar Base de Datos

```bash
# Ejecutar esquema de base de datos
psql $DATABASE_URL -f data/db/ecommerce_orders_schema.sql
```

### 3. Configurar Variables de Entorno

```bash
export COMPANY_NAME="Mi Empresa"
export BOT_NAME="Asistente de Pedidos"
export DATABASE_URL="postgresql://user:password@localhost/dbname"
export PORT=5000
```

### 4. Ejecutar API

```bash
# Modo desarrollo
python3 scripts/chatbot_rastreo_api.py

# Modo producción (con gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 chatbot_rastreo_api:app
```

---

## 📖 Uso

### Uso Básico (Python)

```python
from chatbot_rastreo_pedidos import OrderTrackingChatbot

# Inicializar chatbot
chatbot = OrderTrackingChatbot(
    company_name="Mi Empresa",
    bot_name="Asistente de Pedidos"
)

# Procesar mensaje
response = chatbot.process_message(
    message="¿Dónde está mi pedido ORD-2024-001234?",
    customer_email="cliente@example.com"
)

print(response.message)
print(f"Confianza: {response.confidence}")
print(f"Requiere escalación: {response.requires_escalation}")
```

### Uso con API REST

#### Procesar Mensaje

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Dónde está mi pedido ORD-2024-001234?",
    "customer_email": "cliente@example.com",
    "conversation_id": "conv-123"
  }'
```

**Respuesta:**

```json
{
  "response": "¡Hola! Te ayudo con tu pedido ORD-2024-001234...",
  "confidence": 0.9,
  "intent": "track_order",
  "requires_escalation": false,
  "processing_time": 0.15,
  "order_info": {
    "order_id": "ORD-2024-001234",
    "status": "in_transit",
    "payment_status": "paid",
    "tracking_number": "TRACK123456789",
    "estimated_delivery_date": "2024-01-15"
  }
}
```

#### Obtener Información de Pedido

```bash
curl http://localhost:5000/api/order/ORD-2024-001234?customer_email=cliente@example.com
```

#### Buscar Pedidos por Email

```bash
curl "http://localhost:5000/api/orders/search?customer_email=cliente@example.com&limit=10"
```

#### Obtener Métricas

```bash
curl http://localhost:5000/api/metrics
```

#### Detectar Problemas en un Pedido

```bash
curl "http://localhost:5000/api/orders/ORD-2024-001234/problems?customer_email=cliente@example.com"
```

**Respuesta:**
```json
{
  "order_id": "ORD-2024-001234",
  "problems": [
    {
      "type": "delayed_delivery",
      "severity": "high",
      "description": "El pedido tiene 5 día(s) de retraso",
      "suggested_action": "Contactaremos al carrier...",
      "confidence": 0.9
    }
  ],
  "problems_count": 1,
  "has_critical_problems": true
}
```

---

## 🔌 Integración con n8n

### Importar Workflow

1. Abre n8n
2. Ve a "Workflows" → "Import from File"
3. Selecciona `n8n_workflow_rastreo_pedidos.json`
4. Configura las credenciales:
   - Telegram Bot API
   - Chatbot API Auth
   - Support API Auth

### Configurar Variables de Entorno en n8n

```bash
CHATBOT_API_URL=http://localhost:5000
SUPPORT_TICKET_API_URL=http://localhost:8000
```

### Flujo del Workflow

1. **Trigger:** Telegram o Webhook
2. **Filtro:** Solo mensajes de texto
3. **Llamada API:** Envía mensaje al chatbot
4. **Respuesta:** Envía respuesta al cliente
5. **Escalación:** Si es necesario, crea ticket de soporte
6. **Notificación:** Informa al cliente sobre la escalación

---

## 🗄️ Esquema de Base de Datos

### Tablas Principales

#### `ecommerce_orders`
Almacena información completa de los pedidos:
- ID del pedido
- Información del cliente
- Estado y estado de pago
- Información de envío
- Items y totales
- Direcciones

#### `ecommerce_order_tracking`
Historial de eventos de tracking:
- Estados del pedido
- Ubicaciones
- Mensajes del carrier
- Timestamps

#### `ecommerce_payment_updates`
Historial de actualizaciones de pago:
- Estados de pago
- Transacciones
- Métodos de pago

#### `ecommerce_chatbot_conversations`
Conversaciones del chatbot:
- ID de conversación
- Cliente
- Estado
- Fechas

#### `ecommerce_chatbot_messages`
Mensajes individuales:
- Tipo (usuario/bot/agente)
- Texto
- Intención
- Confianza

---

## 🎯 Intenciones Soportadas

El chatbot detecta automáticamente las siguientes intenciones:

1. **TRACK_ORDER** - Rastrear pedido
2. **PAYMENT_STATUS** - Estado del pago
3. **DELIVERY_DATE** - Fecha de entrega
4. **CANCEL_ORDER** - Cancelar pedido (escala a humano)
5. **REFUND** - Reembolso (escala a humano)
6. **CHANGE_ADDRESS** - Cambiar dirección (escala a humano)
7. **CONTACT_SUPPORT** - Contactar soporte
8. **ORDER_DETAILS** - Detalles del pedido
9. **SHIPPING_INFO** - Información de envío
10. **OTHER** - Otras consultas

---

## 📊 Métricas y Monitoreo

### Métricas Disponibles

```python
metrics = chatbot.get_metrics()
```

**Métricas incluidas:**
- Total de mensajes procesados
- Total de escalaciones
- Tasa de escalación
- Distribución de intenciones
- Confianza promedio
- Tiempo de procesamiento promedio
- Pedidos rastreados
- Consultas de pago

### Endpoint de Métricas

```bash
GET /api/metrics
```

---

## 🔧 Configuración Avanzada

### Personalizar Tono y Voz

Edita el archivo `chatbot_rastreo_pedidos.py` y modifica los métodos de generación de respuestas:

```python
def _generate_tracking_response(self, order_info: OrderInfo) -> str:
    # Personalizar aquí el formato y tono de las respuestas
    response = f"¡Hola! Te ayudo con tu pedido {order_info.order_id}. 😊\n\n"
    # ...
```

### Agregar Nuevas Intenciones

1. Agregar nuevo tipo en `IntentType` enum
2. Agregar patrones en `_detect_intent()`
3. Agregar lógica de respuesta en `process_message()`

### Integrar con Otros Sistemas

El chatbot puede integrarse con:
- Shopify
- WooCommerce
- Magento
- Sistemas personalizados

Solo necesitas adaptar el método `_get_order_from_db()` para consultar tu sistema.

---

## 🚨 Escalación a Soporte Humano

### Cuándo se Escala

El chatbot escala automáticamente cuando:

1. **Confianza baja** (< 0.3)
2. **Intenciones complejas:**
   - Cancelar pedido
   - Solicitar reembolso
   - Cambiar dirección
3. **Problemas detectados:**
   - Pedido cancelado
   - Pago fallido
4. **Solicitud explícita** del cliente

### Proceso de Escalación

1. El chatbot detecta necesidad de escalación
2. Crea ticket en sistema de soporte (vía API)
3. Notifica al cliente
4. Transfiere conversación a agente humano

---

## 📝 Ejemplos de Uso

### Ejemplo 1: Rastrear Pedido

**Usuario:** "¿Dónde está mi pedido ORD-2024-001234?"

**Bot:**
```
¡Hola! Te ayudo con tu pedido ORD-2024-001234. 😊

📦 Estado actual: En tránsito
💳 Pago: Pagado
💰 Total: 99.99 USD

📮 Número de seguimiento: TRACK123456789
🚚 Transportista: FedEx
📅 Fecha estimada de entrega: 15/01/2024

📍 Última actualización: En camino al destino
🌍 Ubicación: Centro de distribución

¿Hay algo más en lo que pueda ayudarte sobre tu pedido?
```

### Ejemplo 2: Consultar Pago

**Usuario:** "¿Está pagado mi pedido ORD-2024-001234?"

**Bot:**
```
💳 Estado del pago para pedido ORD-2024-001234:

Estado: Pagado
Monto: 99.99 USD
Fecha: 10/01/2024 14:30
ID de transacción: TXN-123456

✅ Tu pago ha sido procesado correctamente.
```

### Ejemplo 3: Fecha de Entrega

**Usuario:** "¿Cuándo llega mi pedido?"

**Bot:**
```
📅 Tu pedido ORD-2024-001234 tiene una fecha estimada de entrega: 15/01/2024.

Estado actual: En tránsito
Te mantendré informado de cualquier actualización.
```

---

## 🐛 Troubleshooting

### El chatbot no encuentra pedidos

1. Verificar que el ID del pedido sea correcto
2. Verificar conexión a base de datos
3. Verificar que el pedido exista en la BD
4. Revisar logs: `logs/chatbot_rastreo_pedidos_*.log`

### Errores de API

1. Verificar que el servidor esté corriendo
2. Verificar variables de entorno
3. Verificar credenciales de base de datos
4. Revisar logs del servidor

### Problemas con n8n

1. Verificar que el workflow esté activo
2. Verificar credenciales de Telegram
3. Verificar URL del API del chatbot
4. Revisar logs de n8n

---

## 📚 Referencias

- [Esquema de Base de Datos](data/db/ecommerce_orders_schema.sql)
- [Código del Chatbot](scripts/chatbot_rastreo_pedidos.py)
- [API REST](scripts/chatbot_rastreo_api.py)
- [Workflow n8n](n8n_workflow_rastreo_pedidos.json)

---

## 🎉 Beneficios

- ✅ **Automatiza 70% de consultas** de entrega
- ✅ **Reduce carga** en equipo de soporte
- ✅ **Mejora experiencia** del cliente
- ✅ **Respuestas instantáneas** 24/7
- ✅ **Escalación inteligente** cuando es necesario
- ✅ **Métricas completas** para análisis

---

## 📞 Soporte

Para preguntas o problemas:
- Revisa los logs en `logs/chatbot_rastreo_pedidos_*.log`
- Consulta la documentación de la API
- Revisa el código fuente para más detalles

---

**Versión:** 1.0.0  
**Última actualización:** 2024-01-01


