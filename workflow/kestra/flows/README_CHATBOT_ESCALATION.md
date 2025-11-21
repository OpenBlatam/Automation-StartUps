# 🤖 Chatbot de Soporte - Guía de Escalación a Humanos

## 📋 Resumen

Sistema completo de chatbot para FAQs con escalación automática a agentes humanos para casos complejos.

## 🎯 Características Principales

### ✅ Chatbot Inteligente
- **Búsqueda de FAQs**: Busca en base de datos artículos relevantes
- **Detección de Intención**: Identifica automáticamente el tipo de consulta
- **Respuestas Contextuales**: Usa LLM (OpenAI) para respuestas personalizadas
- **Historial de Conversación**: Mantiene contexto en conversaciones multi-turno

### ✅ Escalación Automática
- **Detección de Casos Complejos**: Identifica cuando un agente humano es necesario
- **Creación Automática de Tickets**: Crea tickets cuando se necesita escalación
- **Reglas Configurables**: Define cuándo escalar basado en confianza, intención, etc.
- **Notificaciones**: Notifica a agentes cuando se necesita su intervención

## 🏗️ Arquitectura

```
┌─────────────────┐
│   Cliente Web   │
│  (ChatbotWidget)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  API Endpoint    │
│ /api/support/   │
│    chatbot      │
└────────┬────────┘
         │
    ┌────┴────┐
    │        │
    ▼        ▼
┌────────┐ ┌──────────────┐
│ FAQs   │ │  OpenAI LLM  │
│  DB    │ │   (opcional)  │
└────────┘ └──────────────┘
    │        │
    └────┬────┘
         │
         ▼
    ┌─────────┐
    │¿Resolver│
    │o Escalar│
    └────┬────┘
         │
    ┌────┴────┐
    │         │
    ▼         ▼
┌────────┐ ┌──────────────┐
│Respuesta│ │ Crear Ticket │
│Chatbot │ │  + Notificar  │
└────────┘ └──────────────┘
```

## 🔄 Flujo de Escalación

### 1. Evaluación de Confianza

El chatbot evalúa su capacidad de resolver la consulta:

| Confianza | Acción | Estado |
|-----------|--------|--------|
| ≥ 0.7 | Responder con chatbot | ✅ Resuelto |
| 0.4 - 0.69 | Responder + ofrecer escalación | ⚠️ Parcial |
| < 0.4 | Escalar inmediatamente | 🚨 Escalar |

### 2. Factores de Escalación

El chatbot escalará automáticamente cuando:

1. **Confianza Baja** (< 0.4)
   - No encuentra FAQs relevantes
   - LLM no puede generar respuesta confiable

2. **Intención Compleja**
   - Cancelación de cuenta
   - Problemas de facturación complejos
   - Reclamaciones legales
   - Problemas de seguridad

3. **Múltiples Intentos Fallidos**
   - Usuario indica que la respuesta no ayudó
   - Usuario repite la misma pregunta
   - 3+ turnos sin resolución

4. **Solicitud Explícita**
   - Usuario pide hablar con agente
   - Usuario dice "humano", "agente", "persona"

5. **Problemas Técnicos Críticos**
   - Palabras clave: "crash", "down", "no funciona nada"
   - Problemas de seguridad detectados

### 3. Proceso de Escalación

Cuando se detecta necesidad de escalación:

```mermaid
graph TD
    A[Consulta del Usuario] --> B{Chatbot Evalúa}
    B -->|Confianza < 0.4| C[Escalar Inmediatamente]
    B -->|Confianza 0.4-0.7| D[Ofrecer Opción]
    B -->|Confianza ≥ 0.7| E[Responder]
    C --> F[Crear Ticket]
    D --> G{Usuario Acepta?}
    G -->|Sí| F
    G -->|No| E
    F --> H[Notificar Agente]
    H --> I[Asignar según Prioridad]
```

## ⚙️ Configuración

### Variables de Entorno

```bash
# Base de datos
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# OpenAI (opcional, para respuestas con LLM)
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o-mini

# Kestra Webhook (para procesamiento automático)
KESTRA_WEBHOOK_URL=http://kestra:8080
```

### Reglas de Escalación Personalizadas

Edita el archivo `app/api/support/chatbot/route.ts` para personalizar:

```typescript
// Umbral de confianza para escalación
const ESCALATION_THRESHOLD = 0.4;

// Intenciones que requieren escalación inmediata
const IMMEDIATE_ESCALATION_INTENTS = [
  'cancellation',
  'billing_dispute',
  'legal',
  'security'
];

// Palabras clave que disparan escalación
const CRITICAL_KEYWORDS = [
  'crash',
  'down',
  'emergency',
  'urgent',
  'no funciona nada'
];
```

## 📊 Métricas y Monitoreo

### KPIs del Chatbot

- **Tasa de Resolución**: % de consultas resueltas sin escalación
- **Tiempo Promedio de Respuesta**: Tiempo hasta primera respuesta
- **Tasa de Escalación**: % de conversaciones que escalan
- **Satisfacción del Cliente**: Score de satisfacción post-conversación

### Consultas SQL

```sql
-- Tasa de resolución del chatbot
SELECT 
    COUNT(*) FILTER (WHERE resolved = true) * 100.0 / COUNT(*) as resolution_rate
FROM support_chatbot_conversations
WHERE created_at >= NOW() - INTERVAL '7 days';

-- Conversaciones que escalaron a tickets
SELECT 
    c.conversation_id,
    c.customer_email,
    t.ticket_id,
    t.status,
    t.assigned_agent_name
FROM support_chatbot_conversations c
JOIN support_tickets t ON c.ticket_id = t.ticket_id
WHERE c.escalation_needed = true
ORDER BY c.created_at DESC;
```

## 🚀 Uso del Widget

### Instalación en Next.js

```tsx
import ChatbotWidget from '@/components/support/ChatbotWidget';

export default function Page() {
  return (
    <div>
      {/* Tu contenido */}
      <ChatbotWidget
        customerEmail="cliente@example.com"
        customerName="Juan Pérez"
        onEscalation={(message) => {
          console.log('Escalación necesaria:', message);
          // Redirigir a página de tickets o mostrar modal
        }}
      />
    </div>
  );
}
```

### API Endpoints

#### POST /api/support/chatbot

Enviar mensaje al chatbot:

```bash
curl -X POST http://localhost:3000/api/support/chatbot \
  -H "Content-Type: application/json" \
  -d '{
    "message": "¿Cómo cambio mi contraseña?",
    "customer_email": "cliente@example.com",
    "customer_name": "Juan Pérez"
  }'
```

Respuesta:

```json
{
  "response": "Para restablecer tu contraseña...",
  "confidence": 0.85,
  "resolved": true,
  "faq_matched": true,
  "faq_article_id": "faq-password-reset",
  "intent_detected": "account",
  "escalation_needed": false,
  "conversation_id": "conv-1234567890",
  "suggested_actions": [
    "¿Te ayudó esta respuesta?",
    "¿Necesitas algo más?"
  ]
}
```

#### GET /api/support/chatbot/faqs

Buscar FAQs:

```bash
curl "http://localhost:3000/api/support/chatbot/faqs?q=contraseña&limit=5"
```

## 📝 Ejemplos de Escalación

### Caso 1: Consulta Simple (No Escala)

**Usuario**: "¿Cómo cambio mi contraseña?"

**Chatbot**:
- ✅ Encuentra FAQ relevante
- ✅ Confianza: 0.9
- ✅ Responde con instrucciones

**Resultado**: Resuelto por chatbot

### Caso 2: Consulta Compleja (Escala)

**Usuario**: "Mi cuenta fue hackeada y necesito recuperar el acceso inmediatamente"

**Chatbot**:
- ⚠️ Detecta palabras clave críticas: "hackeada", "inmediatamente"
- ⚠️ Confianza: 0.3 (no puede resolver seguridad)
- 🚨 Escala inmediatamente

**Acción Automática**:
1. Crea ticket con prioridad "urgent"
2. Asigna a departamento "security"
3. Notifica a agente senior
4. Responde al usuario: "Entiendo la urgencia. He creado un ticket urgente y un agente de seguridad se contactará contigo en los próximos minutos."

### Caso 3: Múltiples Intentos (Escala)

**Turno 1**:
- Usuario: "No puedo descargar mi factura"
- Chatbot: Responde con instrucciones (confianza 0.8)

**Turno 2**:
- Usuario: "Eso no funcionó"
- Chatbot: Ofrece alternativa (confianza 0.6)

**Turno 3**:
- Usuario: "Todavía no puedo"
- Chatbot: Detecta frustración, escala automáticamente

## 🔧 Personalización Avanzada

### Agregar Nuevas FAQs

```sql
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords
) VALUES (
    'faq-nueva-pregunta',
    '¿Cómo hacer X?',
    'Contenido completo de la respuesta...',
    'Resumen corto',
    'general',
    ARRAY['tag1', 'tag2'],
    ARRAY['palabra1', 'palabra2']
);
```

### Personalizar Mensajes de Escalación

Edita en `app/api/support/chatbot/route.ts`:

```typescript
const ESCALATION_MESSAGES = {
  default: 'Entiendo tu consulta. Te voy a conectar con un agente...',
  urgent: 'Entiendo la urgencia. He creado un ticket urgente...',
  technical: 'Este problema técnico requiere atención especializada...',
  billing: 'Para ayudarte mejor con tu consulta de facturación...'
};
```

## 📈 Mejores Prácticas

1. **Mantén FAQs Actualizadas**
   - Revisa conversaciones que escalaron
   - Agrega FAQs para preguntas frecuentes
   - Actualiza FAQs obsoletas

2. **Monitorea Métricas**
   - Revisa tasa de escalación semanalmente
   - Identifica patrones en consultas no resueltas
   - Ajusta umbrales según resultados

3. **Optimiza Respuestas**
   - Usa lenguaje claro y directo
   - Incluye enlaces y recursos útiles
   - Ofrece opciones cuando sea posible

4. **Mejora Continua**
   - Recolecta feedback de usuarios
   - Analiza qué funciona y qué no
   - Ajusta reglas de escalación según necesidades

## 🆘 Troubleshooting

### El chatbot no responde

1. Verifica que `DATABASE_URL` esté configurado
2. Revisa logs del servidor
3. Verifica que la tabla `support_faq_articles` tenga datos

### Escalación no funciona

1. Verifica que `KESTRA_WEBHOOK_URL` esté configurado
2. Revisa que el workflow `support_ticket_automation` esté activo
3. Verifica permisos de creación de tickets

### Respuestas con LLM no funcionan

1. Verifica `OPENAI_API_KEY`
2. Revisa límites de rate de OpenAI
3. Verifica que el modelo esté disponible

## 📚 Recursos Adicionales

- [Sistema de Tickets](README_SUPPORT_AUTOMATION.md)
- [Priorización Automática](lib/support_priority.py)
- [Enrutamiento Inteligente](lib/support_routing.py)
- [Esquema de Base de Datos](../data/db/support_tickets_schema.sql)

