# 🚀 Customer Action Automation Workflow - Advanced Edition

## 📋 Descripción

Versión mejorada y avanzada del workflow de automatización de clientes con funcionalidades de nivel enterprise: A/B testing, análisis predictivo, deduplicación inteligente, optimización de timing, multi-idioma y machine learning.

## ✨ Nuevas Funcionalidades Avanzadas

### 🎯 Mejoras Principales vs Versión Básica

#### 1. **Deduplicación Inteligente** 🔄
- Evita procesar el mismo evento múltiples veces
- Usa staticData para tracking de eventos procesados
- Limpieza automática de eventos antiguos (>24h)
- Previene spam y duplicados

#### 2. **Enriquecimiento Avanzado de Datos** 📊
- **Scoring de Conversión**: Calcula probabilidad de conversión (0-100)
- **Segmentación Mejorada**: 4 niveles (premium, high_value, medium_value, low_value)
- **Análisis de Urgencia**: Determina urgencia basada en score
- **Historial del Cliente**: Integración con CRM para datos históricos
- **Preferencias**: Idioma, timezone, canal preferido

#### 3. **Análisis Predictivo de Timing** ⏰
- Calcula timing óptimo basado en:
  - Score de conversión del cliente
  - Hora del día en timezone del cliente
  - Nivel de urgencia
  - Historial de engagement
- Evita enviar en horas de sueño
- Optimiza para horas de mayor engagement

#### 4. **A/B Testing Integrado** 🧪
- Asignación consistente de variantes (A/B)
- Basado en hash del customerId
- Variantes configurables:
  - **Variante A**: Tono friendly, descuento estándar, emojis
  - **Variante B**: Tono profesional, descuento mayor, sin emojis
- Tracking completo de resultados

#### 5. **Multi-idioma** 🌍
- Soporte para español e inglés (extensible)
- Selección automática basada en preferencias del cliente
- Templates personalizados por idioma
- Fácil extensión a más idiomas

#### 6. **Integración con CRM** 🔗
- Obtiene historial del cliente:
  - Compras anteriores
  - Valor total gastado
  - Fecha de última compra
  - Valor promedio de orden
  - Categorías favoritas
- Obtiene preferencias:
  - Idioma
  - Zona horaria
  - Horario preferido de contacto
  - Canal de comunicación preferido
  - Estado de suscripción

#### 7. **Manejo de Errores Mejorado** 🛡️
- Retry automático con backoff exponencial
- Continue on fail para nodos no críticos
- Logging detallado de errores
- Tracking de errores para análisis

#### 8. **Tracking Avanzado** 📈
- Registra métricas completas:
  - Variante A/B asignada
  - Score de conversión
  - Idioma usado
  - Canal de envío
  - Timing optimizado
- Integración con sistema de analytics
- Envío a sistema de ML para análisis predictivo

#### 9. **Verificación de Suscripción** ✅
- Verifica estado de suscripción antes de enviar
- Respeta preferencias de comunicación
- Evita enviar a clientes desuscritos

#### 10. **Optimización de Descuentos** 💰
- Descuentos dinámicos según:
  - Segmento del cliente
  - Variante A/B
  - Historial de compras
- Códigos personalizados por segmento

## 🔄 Flujo del Workflow Avanzado

```
1. Webhook Trigger
   ↓
2. Deduplicación de Eventos
   ↓
3. Enriquecimiento de Datos Avanzado
   ↓
4. Fetch Customer History (CRM)
   ↓
5. Fetch Customer Preferences (CRM)
   ↓
6. Merge Customer Data
   ↓
7. Filter Cart Event
   ↓
8. Check Cart Value
   ↓
9. Análisis Predictivo de Timing
   ↓
10. Asignación A/B Test
    ↓
11. Wait Optimized Time / 24h / 72h
    ↓
12. Check Cart Status (con retry)
    ↓
13. Check Not Completed
    ↓
14. Generación de Mensaje Avanzado
    ↓
15. Predictive Analytics (ML)
    ↓
16. Send Email/SMS (con retry)
    ↓
17. Track Event Advanced
    ↓
18. Error Handler (si hay errores)
```

## 📊 Scoring de Conversión

El sistema calcula un score de conversión (0-100) basado en:

- **Valor del carrito**: +20 puntos si > $100
- **Número de items**: +10 puntos si > 2 items
- **Compras anteriores**: +15 puntos si tiene historial
- **Tiempo en sitio**: +10 puntos si > 5 minutos
- **Páginas visitadas**: +5 puntos si > 3 páginas

**Niveles de Urgencia**:
- **High** (70-100): Alta probabilidad, timing rápido
- **Medium** (50-69): Probabilidad media, timing estándar
- **Low** (<50): Baja probabilidad, timing extendido

## 🧪 A/B Testing

### Variante A (Friendly)
- Tono: Amigable y cercano
- Descuento: 10% (standard) / 15% (premium)
- Urgencia: Moderada
- Emojis: ✅ Sí
- Ejemplo: "¡Hola Juan! ¿Olvidaste algo? 🛒"

### Variante B (Professional)
- Tono: Profesional y directo
- Descuento: 12% (standard) / 20% (premium)
- Urgencia: Alta
- Emojis: ❌ No
- Ejemplo: "Recordatorio: Artículos en tu carrito"

### Asignación
- Basada en hash del customerId
- Consistente (mismo cliente siempre misma variante)
- 50/50 distribución

## ⏰ Optimización de Timing

El sistema calcula el timing óptimo considerando:

1. **Score de Conversión**:
   - >80: 0.5 horas (alta probabilidad)
   - 60-80: 1 hora
   - 40-60: 2 horas
   - <40: 4 horas

2. **Hora del Día**:
   - 6-22: Horas activas, timing normal
   - 22-6: Horas de sueño, esperar hasta mañana
   - 9-17: Horas de trabajo, timing óptimo

3. **Urgencia**:
   - High: Máximo 1 hora de delay
   - Medium: Timing estándar
   - Low: Timing extendido

## 🌍 Multi-idioma

### Idiomas Soportados
- **Español (es)**: Default
- **Inglés (en)**: Disponible

### Extensión
Para agregar más idiomas, edita el nodo `Generate Advanced Message` y agrega templates en el objeto `templates`.

## 🔗 Integración con CRM

### Endpoints Requeridos

#### GET /customers/{customerId}/history
```json
{
  "previousPurchases": 5,
  "totalSpent": 1250.00,
  "lastPurchaseDate": "2024-01-15T10:30:00Z",
  "averageOrderValue": 250.00,
  "favoriteCategories": ["electronics", "books"]
}
```

#### GET /customers/{customerId}/preferences
```json
{
  "language": "es",
  "timezone": "America/Mexico_City",
  "preferredContactTime": "09:00-18:00",
  "communicationChannel": "email",
  "unsubscribeStatus": false
}
```

## 📈 Tracking y Analytics

### Eventos Trackeados

1. **automation_triggered**: Workflow iniciado
2. **message_sent**: Mensaje enviado
   - Incluye: variant, score, language, channel
3. **message_opened**: Email abierto (requiere webhook de email)
4. **message_clicked**: Link clickeado (requiere tracking)
5. **conversion**: Compra completada

### Métricas Registradas

- `abTestVariant`: Variante A/B asignada
- `abTestId`: ID único del test
- `conversionScore`: Score calculado
- `language`: Idioma usado
- `channel`: Canal de envío
- `optimalDelayHours`: Timing calculado
- `customerSegment`: Segmento del cliente

## 🛡️ Manejo de Errores

### Retry Logic
- **Max Tries**: 3 intentos
- **Wait Between Tries**: 2-5 segundos
- **Continue On Fail**: Para nodos no críticos

### Nodos con Retry
- Check Cart Status
- Send Email Advanced
- Fetch Customer History
- Fetch Customer Preferences

### Error Handler
- Captura todos los errores
- Registra para análisis
- No interrumpe el flujo principal

## ⚙️ Configuración

### Variables de Entorno

```bash
# Email
FROM_EMAIL=noreply@yourdomain.com
REPLY_TO_EMAIL=support@yourdomain.com

# API
API_BASE_URL=https://api.yourdomain.com
API_KEY=your_api_key_here

# Analytics (Opcional)
ML_API_URL=https://ml-api.yourdomain.com
ML_API_KEY=your_ml_api_key
```

### Credenciales

1. **SMTP**: Para envío de emails
2. **Twilio API**: Para SMS (opcional)
3. **HTTP Header Auth**: Para API de CRM y analytics

## 📊 Comparación: Básico vs Avanzado

| Característica | Básico | Avanzado |
|---------------|--------|----------|
| Deduplicación | ❌ | ✅ |
| Scoring de Conversión | ❌ | ✅ |
| A/B Testing | ❌ | ✅ |
| Multi-idioma | ❌ | ✅ |
| Timing Optimizado | ❌ | ✅ |
| Integración CRM | ❌ | ✅ |
| Retry Logic | Básico | Avanzado |
| Tracking | Básico | Completo |
| Manejo de Errores | Básico | Avanzado |
| Análisis Predictivo | ❌ | ✅ |

## 🚀 Casos de Uso Avanzados

### Caso 1: Cliente Premium con Alta Probabilidad
- Score: 85
- Segmento: Premium
- Timing: 0.5 horas
- Variante: B (20% descuento)
- Idioma: Español
- Resultado: Email enviado en 30 minutos con oferta exclusiva

### Caso 2: Cliente Regular con Probabilidad Media
- Score: 55
- Segmento: Medium Value
- Timing: 2 horas
- Variante: A (10% descuento)
- Idioma: Inglés
- Resultado: Email enviado en 2 horas con tono friendly

### Caso 3: Cliente Nuevo con Baja Probabilidad
- Score: 35
- Segmento: Low Value
- Timing: 4 horas
- Variante: A (10% descuento)
- Idioma: Español
- Resultado: Email enviado en 4 horas, enfoque en educación

## 📝 Mejores Prácticas

1. **Monitoreo Continuo**:
   - Revisa métricas de A/B testing semanalmente
   - Ajusta variantes según resultados
   - Optimiza timing basado en datos

2. **Análisis de Resultados**:
   - Compara tasas de conversión por variante
   - Analiza timing óptimo por segmento
   - Identifica patrones en scoring

3. **Optimización Iterativa**:
   - Ajusta umbrales de scoring
   - Modifica timing según resultados
   - Personaliza mensajes por segmento

4. **Testing**:
   - Prueba con datos reales
   - Valida integraciones CRM
   - Verifica multi-idioma

## 🔍 Troubleshooting

### Problema: Deduplicación muy agresiva
**Solución**: Ajusta el tiempo de ventana en `Deduplicate Events` (actualmente 1 hora)

### Problema: Timing no optimizado
**Solución**: Verifica que `Fetch Customer Preferences` retorna timezone correcto

### Problema: A/B testing inconsistente
**Solución**: Verifica que customerId es consistente entre llamadas

### Problema: CRM no responde
**Solución**: Los nodos tienen `continueOnFail: true`, el workflow continúa sin datos del CRM

## 📚 Recursos Adicionales

- [Documentación Versión Básica](./README_CUSTOMER_AUTOMATION.md)
- [Ejemplos de Uso](./EXAMPLES_CUSTOMER_AUTOMATION.md)
- [Quick Start](./QUICK_START_CUSTOMER_AUTOMATION.md)

---

**Versión**: 2.0 Advanced  
**Última Actualización**: 2024-01-01  
**Compatibilidad**: n8n 1.0+




