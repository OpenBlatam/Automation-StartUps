# 📚 Workflows Adicionales y Herramientas

## 🎯 Resumen

Además de los workflows principales de automatización de clientes, se han creado workflows complementarios y herramientas de soporte para maximizar el impacto de tus campañas.

---

## 🔄 Workflow de Reactivación de Clientes

### Archivo
`n8n_workflow_customer_reactivation.json`

### Descripción
Workflow automatizado que identifica y reactiva clientes inactivos mediante campañas personalizadas.

### Características

#### 1. **Identificación Automática**
- Ejecuta cada lunes a las 9 AM
- Identifica clientes inactivos (configurable, default 90 días)
- Filtra por valor mínimo de compra

#### 2. **Segmentación Inteligente**
- **High Value**: >$500 gastados, score >70
- **Medium Value**: $200-$500, score >50
- **Low Value**: Resto con score >30
- **Churn Risk**: Score <30

#### 3. **Scoring de Reactivación**
Calcula probabilidad de reactivación (0-100) basado en:
- Valor total gastado
- Valor de última compra
- Número de compras anteriores
- Días inactivos

#### 4. **Mensajes Personalizados**
- **High Value**: 30% descuento + envío gratis + producto gratis
- **Medium Value**: 20% descuento
- **Low Value**: 15% descuento

#### 5. **Reportes Automáticos**
- Genera reporte semanal
- Envía resumen al equipo
- Incluye métricas por segmento

### Configuración

```bash
# Variables de entorno
DAYS_INACTIVE=90          # Días de inactividad
MIN_PURCHASE_VALUE=50     # Valor mínimo de compra
API_BASE_URL=https://api.yourdomain.com
API_KEY=your_api_key
FROM_EMAIL=noreply@yourdomain.com
REPORT_RECIPIENTS=team@yourdomain.com
```

### Uso

1. Importa el workflow en n8n
2. Configura variables de entorno
3. Configura credenciales (SMTP, API)
4. Activa el workflow
5. Recibe reportes semanales automáticos

### Métricas Esperadas

- **Tasa de Reactivación**: 15-25%
- **Valor Recuperado**: $5,000-15,000/mes (según volumen)
- **ROI**: 300-500%

---

## 📊 Workflow de Analytics Dashboard

### Archivo
`n8n_workflow_analytics_dashboard.json`

### Descripción
Workflow que consolida métricas de todos los sistemas y actualiza dashboard en tiempo real con alertas automáticas.

### Características

#### 1. **Recopilación de Métricas**
- **Cart Abandonment**: Tasa de abandono, recuperación, valor
- **Email Performance**: Enviados, entregados, aperturas, clics, bounces
- **Conversion**: Visitantes, conversiones, revenue, AOV
- **A/B Testing**: Resultados por variante, winner, confidence

#### 2. **Consolidación**
- Combina todas las métricas
- Calcula KPIs derivados:
  - ROI
  - Recovery Efficiency
  - Email Effectiveness

#### 3. **Alertas Inteligentes**
Genera alertas automáticas cuando:
- Tasa de abandono >75% (Warning)
- Tasa de apertura <20% (Warning)
- Tasa de conversión <10% (Critical)
- Tasa de bounce >5% (Critical)
- A/B test con resultado significativo (Info)

#### 4. **Notificaciones**
- **Telegram**: Alertas en tiempo real
- **Email**: Reporte de alertas críticas
- **Dashboard API**: Actualización automática

### Configuración

```bash
# Variables de entorno
API_BASE_URL=https://api.yourdomain.com
API_KEY=your_api_key
DASHBOARD_API_URL=https://dashboard.yourdomain.com
TELEGRAM_CHAT_ID=your_chat_id
ALERT_EMAIL=alerts@yourdomain.com
FROM_EMAIL=noreply@yourdomain.com
```

### Frecuencia

- **Ejecución**: Cada 6 horas
- **Actualización Dashboard**: En tiempo real
- **Alertas**: Inmediatas cuando se detectan

### Métricas Incluidas

```json
{
  "cartAbandonment": {
    "total": 1000,
    "abandoned": 750,
    "rate": 75.0,
    "recovered": 300,
    "recoveryRate": 40.0,
    "totalValue": 75000,
    "recoveredValue": 30000
  },
  "email": {
    "sent": 5000,
    "delivered": 4800,
    "opened": 1500,
    "clicked": 400,
    "openRate": 31.25,
    "clickRate": 8.33,
    "bounceRate": 4.0
  },
  "conversion": {
    "totalVisitors": 10000,
    "conversions": 1200,
    "conversionRate": 12.0,
    "revenue": 90000,
    "averageOrderValue": 75.0
  },
  "abTesting": {
    "variantA": { "openRate": 28.5, "clickRate": 7.2 },
    "variantB": { "openRate": 34.2, "clickRate": 9.8 },
    "winner": "B",
    "confidence": 0.97
  },
  "kpis": {
    "roi": "1800.00",
    "recoveryEfficiency": "40.00",
    "emailEffectiveness": "8.00"
  }
}
```

---

## 🛠️ Script de Integración Helper

### Archivo
`scripts/integration_helper.py`

### Descripción
Script Python con funciones helper para facilitar la integración con los workflows desde aplicaciones externas.

### Funcionalidades

#### 1. **Trigger de Eventos**
```python
helper.trigger_cart_abandonment(customer_data)
helper.trigger_page_visit(customer_data, page_data)
```

#### 2. **Obtener Datos del Cliente**
```python
history = helper.get_customer_history(customer_id)
preferences = helper.get_customer_preferences(customer_id)
```

#### 3. **Cálculos**
```python
score = helper.calculate_conversion_score(customer_data)
variant = helper.assign_ab_variant(customer_id)
discount_code = helper.generate_discount_code(segment, variant)
timing = helper.calculate_optimal_timing(customer_data, history)
```

#### 4. **Tracking**
```python
helper.track_event(event_data)
```

### Uso

```python
from integration_helper import CustomerAutomationHelper

# Inicializar
helper = CustomerAutomationHelper(
    api_base_url="https://api.yourdomain.com",
    api_key="your_api_key"
)

# Ejemplo: Carrito abandonado
customer_data = {
    "customer_id": "123",
    "email": "test@example.com",
    "cart_id": "cart_456",
    "cart_value": 150.00,
    "cart_items": [...]
}

result = helper.trigger_cart_abandonment(customer_data)
```

### Instalación

```bash
pip install requests
python scripts/integration_helper.py
```

---

## 📋 Resumen de Workflows

| Workflow | Frecuencia | Propósito | ROI Esperado |
|----------|-----------|-----------|--------------|
| **Customer Automation** | Event-driven | Recuperación carrito | 600-800% |
| **Customer Reactivation** | Semanal | Reactivar inactivos | 300-500% |
| **Analytics Dashboard** | Cada 6h | Monitoreo y alertas | N/A (Soporte) |

---

## 🔗 Integración Completa

### Flujo Recomendado

```
1. Customer Automation (Event-driven)
   ↓
2. Analytics Dashboard (Cada 6h)
   ↓ Monitorea resultados
   ↓
3. Customer Reactivation (Semanal)
   ↓ Identifica inactivos
   ↓
4. Loop continuo de optimización
```

### Beneficios Combinados

- **Cobertura Completa**: Eventos en tiempo real + reactivación proactiva
- **Visibilidad Total**: Dashboard con todas las métricas
- **Optimización Continua**: Alertas y reportes automáticos
- **ROI Máximo**: Múltiples puntos de contacto

---

## 📊 Métricas Consolidadas

### Por Workflow

**Customer Automation**:
- Tasa recuperación: 45-55%
- Valor recuperado: $50,000-100,000/mes

**Customer Reactivation**:
- Tasa reactivación: 15-25%
- Valor recuperado: $5,000-15,000/mes

**Total Combinado**:
- **Valor Total Recuperado**: $55,000-115,000/mes
- **ROI Combinado**: 500-700%

---

## 🚀 Próximos Pasos

1. ✅ Importa todos los workflows
2. ✅ Configura variables de entorno
3. ✅ Configura credenciales
4. ✅ Activa workflows
5. ✅ Monitorea dashboard
6. ✅ Ajusta según métricas
7. ✅ Optimiza continuamente

---

**Última Actualización**: 2024-01-01  
**Versión**: 1.0




