# 🎯 Customer Action Automation Workflow

## 📋 Descripción

Workflow completo de automatización basado en triggers para acciones específicas de clientes, incluyendo recuperación de carritos abandonados y seguimiento de comportamiento de navegación en el sitio web.

## ✨ Características Principales

### 🎯 Funcionalidades Core

- ✅ **Múltiples Triggers**: Webhooks para carrito abandonado y visitas a páginas
- ✅ **Períodos de Espera Configurables**: Delays inteligentes entre mensajes
- ✅ **Lógica Condicional Avanzada**: Segmentación y personalización
- ✅ **Contenido de Mensajes Dinámico**: Generación automática de mensajes personalizados
- ✅ **Multi-canal**: Email y SMS
- ✅ **Tracking de Eventos**: Registro de todas las acciones de automatización

### 🚀 Funcionalidades Avanzadas

- 🤖 **Segmentación Automática**: Clasifica clientes por valor del carrito
- 🎬 **Mensajes Personalizados**: Contenido adaptado según comportamiento
- ⚡ **Verificación de Estado**: Verifica que el carrito aún existe antes de enviar
- 📊 **Métricas y Tracking**: Registra todos los eventos para análisis

## 🔄 Flujo del Workflow

### Fase 1: Triggers (Activadores)

#### 1.1 Cart Abandonment Webhook
- **Endpoint**: `POST /cart-abandonment`
- **Payload Esperado**:
```json
{
  "eventType": "cart_abandonment",
  "customerId": "customer_123",
  "email": "cliente@example.com",
  "firstName": "Juan",
  "lastName": "Pérez",
  "cartId": "cart_456",
  "cartValue": 150.00,
  "cartItems": [
    {
      "name": "Producto A",
      "price": 75.00,
      "quantity": 2
    }
  ],
  "sessionId": "session_789"
}
```

#### 1.2 Page Visit Webhook
- **Endpoint**: `POST /page-visit`
- **Payload Esperado**:
```json
{
  "eventType": "page_visit",
  "customerId": "customer_123",
  "email": "cliente@example.com",
  "pageUrl": "https://yourdomain.com/product/123",
  "pageCategory": "product",
  "productName": "Producto Especial",
  "sessionId": "session_789"
}
```

### Fase 2: Enriquecimiento de Datos

El nodo **Enrich Customer Data** procesa y enriquece los datos recibidos:
- Valida datos requeridos (customerId o email)
- Calcula valor total del carrito
- Determina segmento del cliente:
  - `high_value`: > $100
  - `medium_value`: $50-$100
  - `low_value`: < $50
- Genera IDs únicos si faltan

### Fase 3: Lógica Condicional

#### 3.1 Verificación de Valor del Carrito
- Solo procesa carritos con valor > $50
- Filtra carritos de bajo valor para optimizar recursos

#### 3.2 Verificación de Segmento
- Personaliza mensajes según el valor del cliente
- Ofrece descuentos diferenciados

#### 3.3 Verificación de Estado del Carrito
- Antes de enviar cada mensaje, verifica que el carrito aún existe
- No envía si el carrito ya fue completado
- Evita mensajes innecesarios

### Fase 4: Períodos de Espera (Waiting Periods)

#### Para Carrito Abandonado:

1. **Primer Mensaje - 1 Hora**
   - Recordatorio suave
   - Sin descuento
   - Enfoque en completar la compra

2. **Segundo Mensaje - 24 Horas**
   - Recordatorio más urgente
   - Descuento del 10% (código: SAVE10)
   - Enfoque en urgencia

3. **Tercer Mensaje - 72 Horas**
   - Última oportunidad
   - Descuento del 10% (general) o 15% (high_value)
   - Códigos: SAVE10 o VIP15

#### Para Visitas a Páginas:

- **Espera de 5 Minutos**
  - Permite que el usuario termine de navegar
  - Evita interrupciones inmediatas
  - Mejora la experiencia del usuario

### Fase 5: Generación de Contenido

#### 5.1 Mensajes de Carrito Abandonado

**Primer Mensaje (1 hora):**
```
Asunto: ¿Olvidaste algo, [Nombre]?

Hola [Nombre],

Notamos que dejaste algunos artículos en tu carrito:

• Producto A - $75.00
• Producto B - $50.00

Total: $125.00

¿Te gustaría completar tu compra? Tu carrito está guardado y listo para ti.

[Completar Compra]
```

**Segundo Mensaje (24 horas):**
```
Asunto: Última oportunidad: Tu carrito te espera

Hola [Nombre],

Tus artículos siguen esperándote:

• Producto A - $75.00
• Producto B - $50.00

Total: $125.00

Como agradecimiento por tu interés, te ofrecemos un descuento especial del 10%.

Código: SAVE10

[Completar Compra con Descuento]
```

**Tercer Mensaje (72 horas - High Value):**
```
Asunto: Oferta exclusiva: 15% OFF en tu carrito

Hola [Nombre],

Como cliente valioso, queremos ofrecerte un descuento especial del 15% en los artículos de tu carrito.

• Producto A - $75.00
• Producto B - $50.00

Total original: $125.00
Total con descuento: $106.25

Código exclusivo: VIP15

Esta oferta expira en 48 horas.

[Completar Compra Ahora]
```

#### 5.2 Mensajes de Navegación

**Visita a Página de Producto:**
```
Asunto: ¿Interesado en [Nombre del Producto]?

Hola [Nombre],

Vimos que estuviste viendo [Nombre del Producto] en nuestra tienda.

¿Tienes alguna pregunta? Estamos aquí para ayudarte.

[Ver Producto]
```

**Visita a Página de Precios:**
```
Asunto: ¿Listo para comenzar?

Hola [Nombre],

Notamos que revisaste nuestros planes. ¿Te gustaría una demostración personalizada?

[Agendar Demo]
```

**Visita a Blog:**
```
Asunto: Más contenido que te puede interesar

Hola [Nombre],

Vimos que leíste nuestro artículo. Aquí tienes contenido relacionado que podría interesarte:

[Ver Más Contenido]
```

### Fase 6: Envío de Mensajes

#### 6.1 Email
- Usa el nodo **Send Email** con credenciales SMTP
- Personaliza asunto y cuerpo según el tipo de mensaje
- Incluye enlaces de CTA (Call to Action)

#### 6.2 SMS (Opcional)
- Se envía solo si hay número de teléfono disponible
- Requiere credenciales de Twilio
- Mensaje más corto y directo

### Fase 7: Tracking

Todos los eventos se registran en el sistema de tracking:
- Tipo de evento
- ID del cliente
- Tipo de mensaje enviado
- Timestamp
- Resultado del envío

## ⚙️ Configuración

### Variables de Entorno Requeridas

```bash
# Email
FROM_EMAIL=noreply@yourdomain.com
REPLY_TO_EMAIL=support@yourdomain.com

# API
API_BASE_URL=https://api.yourdomain.com
API_KEY=your_api_key_here

# Opcional
REPORT_RECIPIENTS=team@yourdomain.com
```

### Credenciales Necesarias

1. **SMTP Credentials**
   - Para envío de emails
   - Configurar en n8n: Settings > Credentials > SMTP

2. **Twilio API** (Opcional)
   - Para envío de SMS
   - Configurar en n8n: Settings > Credentials > Twilio

3. **HTTP Header Auth** (Opcional)
   - Para verificación de estado del carrito
   - Configurar API key en el nodo HTTP Request

## 📊 Casos de Uso

### Caso 1: Recuperación de Carrito Abandonado

**Escenario**: Cliente agrega productos al carrito pero no completa la compra.

**Flujo**:
1. Sistema detecta abandono → Envía webhook
2. Workflow espera 1 hora
3. Verifica que carrito aún existe
4. Envía primer recordatorio (sin descuento)
5. Espera 24 horas
6. Envía segundo recordatorio (10% descuento)
7. Espera 72 horas
8. Envía último recordatorio (10-15% descuento según segmento)

**Resultado Esperado**: 15-25% de tasa de recuperación

### Caso 2: Seguimiento de Navegación

**Escenario**: Cliente visita página de producto pero no realiza acción.

**Flujo**:
1. Sistema detecta visita → Envía webhook
2. Workflow espera 5 minutos
3. Genera mensaje personalizado según tipo de página
4. Envía email de seguimiento
5. Registra evento en tracking

**Resultado Esperado**: Aumento en engagement y conversión

### Caso 3: Segmentación por Valor

**Escenario**: Cliente de alto valor abandona carrito de $200.

**Flujo**:
1. Sistema detecta abandono
2. Workflow identifica segmento "high_value"
3. Personaliza mensajes con ofertas exclusivas
4. Ofrece descuento del 15% (VIP15)
5. Tratamiento preferencial

**Resultado Esperado**: Mayor tasa de recuperación en segmento premium

## 🔧 Personalización

### Modificar Períodos de Espera

Edita los nodos **Wait**:
- `Wait 1 Hour`: Cambiar `amount` y `unit`
- `Wait 24 Hours`: Ajustar según tu estrategia
- `Wait 72 Hours`: Modificar timing final

### Personalizar Mensajes

Edita el nodo **Generate Message Content**:
- Modifica los templates de mensaje
- Ajusta descuentos y códigos
- Personaliza tono y estilo

### Agregar Nuevos Triggers

1. Crea nuevo nodo Webhook
2. Agrega filtro correspondiente
3. Conecta al flujo de enriquecimiento
4. Define lógica específica

### Agregar Canales Adicionales

1. Crea nodo para nuevo canal (Push, WhatsApp, etc.)
2. Conecta después de **Generate Message Content**
3. Configura credenciales necesarias
4. Personaliza formato de mensaje

## 📈 Métricas y Análisis

### Eventos Trackeados

- `automation_triggered`: Workflow iniciado
- `message_sent`: Mensaje enviado exitosamente
- `message_failed`: Error en envío
- `cart_completed`: Carrito completado (detiene workflow)

### KPIs a Monitorear

- **Tasa de Recuperación**: % de carritos recuperados
- **Tasa de Apertura**: % de emails abiertos
- **Tasa de Conversión**: % de clics que resultan en compra
- **ROI**: Retorno de inversión de la automatización
- **Tiempo de Recuperación**: Tiempo promedio hasta conversión

## 🚨 Mejores Prácticas

### Timing

- **No saturar**: Respeta períodos de espera
- **Horarios óptimos**: Considera zona horaria del cliente
- **Evitar spam**: Verifica estado antes de cada envío

### Personalización

- **Usa nombres**: Siempre personaliza con nombre del cliente
- **Relevancia**: Mensajes deben ser relevantes al comportamiento
- **Segmentación**: Trata diferente según valor del cliente

### Testing

- **A/B Testing**: Prueba diferentes mensajes
- **Timing**: Experimenta con períodos de espera
- **Descuentos**: Optimiza códigos y porcentajes

### Monitoreo

- **Tracking**: Revisa métricas regularmente
- **Errores**: Monitorea fallos en envío
- **Feedback**: Ajusta según resultados

## 🔍 Troubleshooting

### Problema: Mensajes no se envían

**Solución**:
1. Verifica credenciales SMTP/Twilio
2. Revisa logs de n8n
3. Confirma que webhooks están activos
4. Verifica formato de payload

### Problema: Carrito completado pero aún recibe mensajes

**Solución**:
1. Verifica que API de carrito retorna estado correcto
2. Revisa lógica de **Check Not Completed**
3. Confirma que webhook de completado funciona

### Problema: Mensajes duplicados

**Solución**:
1. Implementa deduplicación por customerId + cartId
2. Agrega flag de "mensaje enviado" en base de datos
3. Verifica que webhooks no se disparan múltiples veces

## 📝 Notas Adicionales

- Este workflow es un template base que debe adaptarse a tu negocio
- Considera regulaciones de email marketing (GDPR, CAN-SPAM)
- Implementa unsubscribe en todos los emails
- Monitorea tasas de bounce y spam
- Optimiza según datos reales de tu audiencia

## 🔄 Versiones

- **v1.0** (2024-01-01): Versión inicial con triggers básicos
  - Carrito abandonado
  - Visitas a páginas
  - Mensajes personalizados
  - Tracking básico

## 📚 Recursos Adicionales

- [Documentación n8n](https://docs.n8n.io/)
- [Guía de Webhooks](https://docs.n8n.io/integrations/builtin/core-nodes/n8n-nodes-base.webhook/)
- [Mejores Prácticas de Email Marketing](https://www.example.com)

---

**Creado**: 2024-01-01  
**Última Actualización**: 2024-01-01  
**Versión**: 1.0




