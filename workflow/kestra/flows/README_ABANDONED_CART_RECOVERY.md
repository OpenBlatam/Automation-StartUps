# Recuperación de Carritos Abandonados

## Descripción

Sistema automatizado de recuperación de carritos abandonados que **aumenta significativamente las conversiones** mediante una secuencia de 3 emails estratégicamente programados:

- ✅ **Email 1 (30 min)**: Enfoque empático - pregunta si hubo problema técnico
- ✅ **Email 2 (24 horas)**: Enfoque FOMO - muestra productos con urgencia
- ✅ **Email 3 (48 horas)**: Incentivo final - ofrece descuento del 10%

## Características Principales

### 🎯 Secuencia de Emails Estratégica

1. **Email 1 - Empatía (30 minutos)**
   - Pregunta si hubo problemas técnicos
   - Enfoque en ayudar al cliente
   - Call-to-action suave para continuar comprando

2. **Email 2 - Urgencia (24 horas)**
   - Muestra productos del carrito
   - Genera sensación de escasez (FOMO)
   - Call-to-action más directo

3. **Email 3 - Incentivo (48 horas)**
   - Ofrece código de descuento del 10%
   - Última oportunidad para completar compra
   - Tono de urgencia máxima

### 📊 Validación Robusta

- ✅ Validación de inputs al inicio del workflow
- ✅ Validación de formato de emails antes de enviar
- ✅ Verificación de datos requeridos (cart_id, email, items)
- ✅ Manejo de errores con retry exponencial
- ✅ Advertencias si no hay servicios configurados

### 📧 Integraciones de Email

Soporta múltiples servicios de email:
- **Webhooks genéricos** (Zapier, Make, SendGrid, etc.)
- **Klaviyo** (API nativa)
- **Mailchimp** (API nativa)

### 🗄️ Tracking y Métricas

- Registro completo de carritos abandonados
- Historial de emails enviados
- Tracking de aperturas y clics
- Seguimiento de recuperación de carritos
- Métricas de efectividad

## Configuración

### Inputs Requeridos

```yaml
inputs:
  - email_service_api_key: "your-api-key"
```

### Inputs Opcionales

```yaml
inputs:
  - email_service_type: "webhook"           # webhook, klaviyo, mailchimp
  - email_webhook_url: "https://..."         # Requerido si type=webhook
  - store_name: "Mi Tienda"
  - store_email: "hola@tienda.com"
  - store_url: "https://tienda.com"
  - discount_code: "CART10-XXXX"           # Si no se proporciona, se genera
  - discount_percent: 10                   # Porcentaje de descuento
  - db_jdbc_url: "jdbc:postgresql://..."   # Para tracking (opcional)
  - db_user: "username"
  - db_password: "password"
  - slack_webhook_url: "https://..."        # Notificaciones (opcional)
  - enable_effectiveness_tracking: true     # Tracking de conversión
  - rate_limit_per_minute: 60               # Límite de emails/min
  - unsubscribe_url: "https://..."         # URL para desuscribirse
```

### Variables de Entorno

El workflow utiliza variables para configuración:
- `EMAIL_SERVICE_TYPE`: Tipo de servicio (webhook, klaviyo, mailchimp)
- `STORE_NAME`: Nombre de la tienda
- `DISCOUNT_PERCENT`: Porcentaje de descuento (default: 10)

## Estructura de Base de Datos

### Tabla `abandoned_carts`

El workflow crea automáticamente la estructura si está configurada:

```sql
CREATE TABLE abandoned_carts (
  id SERIAL PRIMARY KEY,
  cart_id VARCHAR(255) NOT NULL,
  cart_hash VARCHAR(64) UNIQUE NOT NULL,
  email VARCHAR(255) NOT NULL,
  first_name VARCHAR(128),
  last_name VARCHAR(128),
  items JSONB NOT NULL DEFAULT '[]',
  total NUMERIC(12,2) NOT NULL DEFAULT 0,
  currency VARCHAR(8) DEFAULT 'USD',
  store_type VARCHAR(64) DEFAULT 'shopify',
  abandoned_at TIMESTAMP NOT NULL,
  email1_sent BOOLEAN DEFAULT false,
  email2_sent BOOLEAN DEFAULT false,
  email3_sent BOOLEAN DEFAULT false,
  email1_send_at TIMESTAMP,
  email2_send_at TIMESTAMP,
  email3_send_at TIMESTAMP,
  email1_opened BOOLEAN DEFAULT false,
  email2_opened BOOLEAN DEFAULT false,
  email3_opened BOOLEAN DEFAULT false,
  email1_clicked BOOLEAN DEFAULT false,
  email2_clicked BOOLEAN DEFAULT false,
  email3_clicked BOOLEAN DEFAULT false,
  recovered BOOLEAN DEFAULT false,
  recovered_at TIMESTAMP,
  discount_code VARCHAR(64),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);
```

### Tabla `abandoned_cart_email_history`

Historial completo de emails enviados:

```sql
CREATE TABLE abandoned_cart_email_history (
  id SERIAL PRIMARY KEY,
  cart_hash VARCHAR(64) REFERENCES abandoned_carts(cart_hash),
  email_number INT NOT NULL,
  sent_at TIMESTAMP NOT NULL,
  sent_via VARCHAR(64),
  status VARCHAR(32) DEFAULT 'sent',
  error_message TEXT,
  opened_at TIMESTAMP,
  clicked_at TIMESTAMP,
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## Ejecución

### Trigger por Webhook

El workflow se activa automáticamente cuando recibe un evento de carrito abandonado:

**Endpoint**: `POST /api/v1/triggers/cart_abandonment`

**Payload de ejemplo (Shopify)**:
```json
{
  "cart_id": "abc123",
  "email": "cliente@example.com",
  "first_name": "Juan",
  "last_name": "Pérez",
  "line_items": [
    {
      "product_id": "prod_123",
      "variant_id": "var_456",
      "title": "Producto Ejemplo",
      "quantity": 2,
      "price": "29.99",
      "image_url": "https://...",
      "url": "https://tienda.com/producto"
    }
  ],
  "currency": "USD",
  "updated_at": "2024-01-15T10:30:00Z",
  "store_type": "shopify"
}
```

**Payload de ejemplo (WooCommerce)**:
```json
{
  "id": "cart_789",
  "email": "cliente@example.com",
  "customer": {
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "cliente@example.com"
  },
  "items": [
    {
      "id": "item_123",
      "product_id": "prod_456",
      "name": "Producto Ejemplo",
      "quantity": 1,
      "unit_price": "49.99",
      "image_url": "https://...",
      "product_url": "https://tienda.com/producto"
    }
  ],
  "currency": "USD",
  "updated_at": "2024-01-15T10:30:00Z",
  "store_type": "woocommerce"
}
```

## Flujo de Trabajo

1. **validate_inputs**: Valida configuración y inputs
2. **ensure_schema**: Crea/valida estructura de tablas (si hay BD)
3. **parse_cart_data**: Extrae y valida datos del carrito
4. **store_cart_data**: Almacena carrito en BD (si está configurado)
5. **generate_discount_code**: Genera código de descuento único
6. **prepare_email_templates**: Crea templates HTML de los 3 emails
7. **send_email_1_webhook**: Envía Email 1 (30 min)
8. **send_email_2_webhook**: Envía Email 2 (24 horas)
9. **send_email_3_webhook**: Envía Email 3 (48 horas)
10. **update_discount_code_db**: Actualiza código en BD
11. **log_cart_abandonment**: Registra métricas y logs
12. **notify_slack**: Notifica a Slack (si está configurado)

## Mensajes de Email

### Email 1 - Enfoque Empático

**Asunto**: "¿Tuviste algún problema en [Tienda]?"

**Contenido**:
- Saludo personalizado
- Pregunta empática sobre problemas técnicos
- Ofrecimiento de ayuda
- Botón para continuar comprando
- Enfoque en servicio al cliente

### Email 2 - Enfoque FOMO

**Asunto**: "⚡ ¡Aún está disponible! - [Producto]"

**Contenido**:
- Lista de productos del carrito con imágenes
- Total del carrito destacado
- Mensaje de urgencia ("¡No pierdas estos artículos!")
- Botón CTA prominente
- Genera sensación de escasez

### Email 3 - Incentivo Final

**Asunto**: "🎁 10% OFF para ti - [Tienda]"

**Contenido**:
- Lista de productos del carrito
- Código de descuento destacado (caja visual)
- Porcentaje de descuento claro
- Mensaje de urgencia ("válido por tiempo limitado")
- Botón CTA con descuento aplicado

## Características de los Emails

Los emails incluyen:
- ✅ **HTML profesional** con CSS integrado
- ✅ **Diseño responsive** para móviles
- ✅ **Imágenes de productos** si están disponibles
- ✅ **Call-to-action claros** con botones destacados
- ✅ **Link de desuscripción** en el footer
- ✅ **Versión texto plano** para compatibilidad
- ✅ **Personalización** con nombre del cliente

## Integración con Plataformas

### Shopify

Para integrar con Shopify, configura un webhook en el admin:

1. Ve a Settings → Notifications → Webhooks
2. Crea un nuevo webhook con:
   - Event: `Cart abandoned`
   - Format: JSON
   - URL: `https://tu-kestra/api/v1/triggers/cart_abandonment`

### WooCommerce

Para integrar con WooCommerce:

1. Instala un plugin de webhooks (ej: "WooCommerce Webhooks")
2. Configura webhook para evento `cart_abandoned`
3. URL: `https://tu-kestra/api/v1/triggers/cart_abandonment`

### Otras Plataformas

El workflow es compatible con cualquier plataforma que pueda enviar webhooks con la estructura esperada.

## Reportes y Métricas

### Métricas Registradas

- Total de carritos abandonados procesados
- Emails programados por paso
- Códigos de descuento generados
- Tasa de recuperación (si está habilitado tracking)
- Tasa de apertura de emails
- Tasa de clics en emails

### Tracking de Efectividad

Si `enable_effectiveness_tracking` está habilitado:

- **Tasa de apertura**: % de emails abiertos por paso
- **Tasa de clics**: % de emails con clics por paso
- **Tasa de recuperación**: % de carritos que se completan
- **Conversión por email**: Qué email genera más conversiones
- **Tiempo hasta recuperación**: Promedio de tiempo hasta completar compra

### Análisis de Performance

El sistema puede generar reportes sobre:
- Efectividad de cada email en la secuencia
- Mejor timing para enviar emails
- Productos más abandonados
- Valores promedio de carritos abandonados
- Conversión por fuente (Shopify vs WooCommerce)

## Integración con Servicios de Email

### Webhook Genérico

El webhook debe aceptar:

```json
{
  "to": "cliente@example.com",
  "to_name": "Juan",
  "from": "hola@tienda.com",
  "from_name": "Mi Tienda",
  "subject": "¿Tuviste algún problema?",
  "html_body": "<html>...</html>",
  "plain_text": "Texto plano...",
  "send_at": "2024-01-15T11:00:00Z",
  "email_type": "abandoned_cart_1",
  "cart_id": "abc123",
  "cart_hash": "hash123",
  "metadata": {
    "campaign": "abandoned_cart",
    "step": 1,
    "delay_minutes": 30
  }
}
```

### Klaviyo

Para usar Klaviyo, configura:
- `email_service_type: "klaviyo"`
- `email_service_api_key: "tu-klaviyo-api-key"`

El workflow usará la API de Klaviyo directamente.

### Mailchimp

Para usar Mailchimp, configura:
- `email_service_type: "mailchimp"`
- `email_service_api_key: "tu-mailchimp-api-key"`

El workflow usará la API de Mailchimp directamente.

## Troubleshooting

### Problemas Comunes

1. **No se reciben eventos de carrito abandonado**
   - Verificar configuración de webhooks en Shopify/WooCommerce
   - Verificar que el endpoint de Kestra sea accesible
   - Revisar logs de Kestra para errores

2. **Emails no se envían**
   - Verificar configuración de `email_webhook_url` o API key
   - Verificar que el servicio de email soporte `send_at`
   - Revisar logs de errores en el workflow

3. **Códigos de descuento duplicados**
   - El sistema genera códigos únicos automáticamente
   - Si proporcionas un código, asegúrate de que sea único

4. **Datos de carrito incorrectos**
   - Verificar formato del payload del webhook
   - El workflow valida estructura antes de procesar
   - Revisar logs de validación

### Logs

Los logs del workflow incluyen:
- Datos del carrito procesado
- Fechas de envío programadas
- Código de descuento generado
- Errores de envío (si los hay)
- Métricas de ejecución

## Mejoras Implementadas

### ✅ Validación Robusta
- Validación de inputs al inicio
- Validación de formato de emails
- Verificación de datos requeridos
- Manejo de errores con retry exponencial

### ✅ Tracking Completo
- Historial de emails enviados
- Seguimiento de aperturas y clics
- Tracking de recuperación de carritos
- Métricas de efectividad

### ✅ Templates Profesionales
- HTML responsive con CSS integrado
- Imágenes de productos
- Call-to-action claros
- Personalización con nombre del cliente

### ✅ Integraciones Múltiples
- Soporte para webhooks genéricos
- Integración nativa con Klaviyo
- Integración nativa con Mailchimp
- Compatible con Shopify y WooCommerce

### ✅ Optimizaciones
- Códigos de descuento únicos
- Rate limiting para evitar spam
- Índices optimizados en BD
- Procesamiento eficiente

## Mejoras Futuras

- [ ] A/B testing de subject lines y contenido
- [ ] Machine learning para optimizar timing
- [ ] Análisis predictivo de probabilidad de conversión
- [ ] Integración con SMS para carritos de alto valor
- [ ] Dashboard de métricas en tiempo real
- [ ] Personalización dinámica por segmento de cliente
- [ ] Recordatorios adicionales (72h, 96h) con descuentos progresivos
- [ ] Integración con sistemas de recomendación de productos

## Referencias

- [Documentación de Kestra](https://kestra.io/docs)
- [Shopify Webhooks](https://shopify.dev/docs/api/admin-graphql/latest/objects/Webhook)
- [WooCommerce Webhooks](https://woocommerce.com/document/webhooks/)
- [Klaviyo API](https://developers.klaviyo.com/)
- [Mailchimp API](https://mailchimp.com/developer/)

