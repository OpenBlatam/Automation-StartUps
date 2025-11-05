---
title: "Cost Support Quick Reference"
category: "10_customer_service"
tags: []
created: "2025-10-29"
path: "10_customer_service/Support_guides/cost_support_quick_reference.md"
---

# ⚡ Cost Support Quick Reference
## Guía de Referencia Rápida para Soporte de Costos

---

## 🚀 COPIAR Y PEGAR - SCRIPTS RÁPIDOS

### **Cobro Duplicado (Urgente)**
```
¡Hola [Nombre]!

Lamento profundamente el error. Esto ya está siendo procesado:
✓ Reembolso: $XXX (iniciado)
✓ Crédito de disculpa: $XX (aplicado)
✓ Tiempo: 30 min confirmación + 1-3 días en cuenta

Te llamo hoy antes de las 5 PM para confirmar.

[Tú Nombre]
[Extensión]
```
⏱️ **Tiempo de Respuesta:** <2 minutos

---

### **Solicitud de Descuento**
```
Hola [Nombre],

Comprendo tu preocupación por el precio. Déjame mostrarte opciones:

• Pago anual: XX% descuento = $XXX/mes efectivo
• Compromiso 12 meses: XX% descuento + setup gratis
• Plan personalizado: Desde $XXX/mes

ROI típico: $XXX ahorro + $XXX ingreso adicional mensual.

¿Cuál te funciona mejor?
```
⏱️ **Tiempo de Respuesta:** <5 minutos

---

### **Cancelación por Costo**
```
Hola [Nombre],

Antes de cancelar, déjame ofrecerte opciones:

1. Downgrade inteligente: Ahorras XX% sin perder funcionalidades
2. Pausa temporal: 3 meses gratis para reorganizarte
3. Plan híbrido: Funcionalidades esenciales + pay-as-you-go por extras

¿Quieres que calculemos tu ROI específico primero?

Saludos,
[Tú Nombre]
```
⏱️ **Tiempo de Respuesta:** <3 minutos

---

## 📊 CALCULADORAS RÁPIDAS

### **ROI Calculator (Simple)**
```python
# Python version
def calculate_roi(monthly_investment, monthly_savings, monthly_revenue):
    total_return = monthly_savings + monthly_revenue
    roi_percentage = ((total_return - monthly_investment) / monthly_investment) * 100
    payback_months = monthly_investment / (monthly_savings + monthly_revenue)
    return {
        'roi_percentage': round(roi_percentage, 2),
        'payback_months': round(payback_months, 2),
        'net_monthly_gain': round(total_return - monthly_investment, 2)
    }

# Example
print(calculate_roi(500, 300, 400))
# Output: {'roi_percentage': 40.0, 'payback_months': 0.71, 'net_monthly_gain': 200}
```

### **ROI Calculator (Excel/Sheets)**
```
Celda A1: Inversión Mensual
Celda B1: Ahorro Mensual
Celda C1: Ingresos Adicionales
Celda D1: =B1+C1 (Total Retorno)
Celda E1: =((D1-A1)/A1)*100 (ROI %)
Celda F1: =A1/(B1+C1) (Payback meses)
Celda G1: =D1-A1 (Ganancia Neta)
```

---

## 🎯 DECISION MATRIX

### **Cuándo Ofrecer Qué**

| Situación | Ofrecer | No Ofrecer |
|-----------|---------|------------|
| Cliente de <3 meses | Crédito hasta $100 | Reembolso completo |
| Cliente 3-12 meses | Crédito hasta $500 | Descuento >40% |
| Cliente >12 meses | Crédito hasta $1000 | Cambio de contrato |
| Queja técnica válida | Crédito + fijación | Solo reembolso |
| Queja de precio | Opciones de plan | Descuento permanente >30% |
| Error nuestro | Compensación + disculpa | Nada adicional |

---

## 💬 FRASES CLAVE (Copy-Paste Ready)

### **Aperturas**
- "Entiendo completamente tu preocupación sobre [specific concern]."
- "Déjame ver cómo puedo ayudarte con esto específicamente."
- "No te preocupes, esto lo resolvemos juntos ahora mismo."

### **Durante la Conversación**
- "Basado en esto, déjame mostrarte [X opciones/paths] que podrían funcionar..."
- "La pregunta clave es: ¿qué necesitas para que esto funcione para ti?"
- "¿Cuál de estas opciones tiene más sentido para tu situación actual?"

### **Cierres**
- "Entonces, ¿procedemos con [specific option]?"
- "¿Quieres que lo procese ahora mismo?"
- "Perfecto, voy a procesar esto inmediatamente y te confirmo en 30 minutos."

---

## 🔢 ESCALAS DE AUTORIZACIÓN

### **Tu Nivel (Agente Standard)**
✅ **AUTORIZADO:**
- Créditos: hasta $200
- Descuentos: hasta 20%
- Reembolsos: hasta $500
- Upgrades temporales: 3 meses
- Extensión de servicio: 30 días

❌ **REQUIERE ESCALAMIENTO:**
- Créditos: >$200
- Descuentos: >20%
- Reembolsos: >$500
- Cambios contractuales
- Cancelaciones masivas

### **Manager**
✅ **AUTORIZADO:**
- Créditos: hasta $1,000
- Descuentos: hasta 40%
- Reembolsos: hasta $2,000
- Upgrades: hasta 12 meses

### **Director**
✅ **AUTORIZADO:**
- Créditos: hasta $5,000
- Descuentos: hasta 50%
- Reembolsos: ilimitados
- Cambios contractuales

---

## 🎨 VISUAL DECISION TREE

```
START: Cliente pregunta sobre costo/precio
│
├─ ¿Es pregunta de precio inicial?
│  └─ → Usar: Cost_Conversation_Templates.md - Opening 1
│
├─ ¿Es problema de facturación?
│  └─ → Usar: Financial_Resolution_Scenarios.md - Scenario 1.1
│
├─ ¿Quiere cancelar?
│  └─ → Usar: Financial_Resolution_Scenarios.md - Scenario 2.2
│
├─ ¿Es objeciones de precio?
│  └─ → Usar: Cost_Conversation_Templates.md - Objection Handling
│
└─ ¿Es solicitud de descuento?
   └─ → Usar: Cost_Support_Guide.md - Scenario 1
```

---

## 📱 SHORTCUTS POR DISPOSITIVO

### **Ctrl+C / Cmd+C Shortcuts (Teclado)**
Cuando escribes en chat/email:
- `/duplicate` → Script de cobro duplicado
- `/discount` → Script de descuento
- `/roi` → Template de presentación ROI
- `/cancel` → Script de retención por cancelación
- `/refund` → Proceso de reembolso

### **Snippets de Texto (Mobile)**
Crear snippets en tu teléfono para:
- Frases de empatía
- Confirmaciones de proceso
- Closing lines

---

## 📋 TEMPLATES DE EMAIL (Cortos)

### **Email 1: Confirmación de Reembolso**
```
Asunto: [Urgente] Reembolso Procesado - Ticket #[###]

Hola [Nombre],

Procesé tu reembolso de $XXX inmediatamente.

Detalles:
• Monto reembolsado: $XXX
• Método de reembolso: [método]
• Tiempo estimado: [1-3 días]
• Ticket de referencia: #[###]

¿Algo más en lo que pueda ayudarte?

[Tú Nombre]
```

### **Email 2: Seguimiento de Descuento**
```
Asunto: Opciones de Plan para Optimizar Costos

Hola [Nombre],

Basado en nuestra conversación, aquí están las opciones:

1. Plan Anual: $XXX/mes (ahorro de $XXX/anual)
2. Downgrade Inteligente: Ahorras XX% sin perder [funcionalidad clave]
3. Plan Personalizado: $XXX/mes (incluye [extras])

¿Cuál prefieres?

[Tú Nombre]
```

---

## 🎯 PROMPTS PARA IA (ChatGPT/Claude)

### **Prompt 1: Generar Análisis de ROI**
```
Cliente pregunta: "[Insert customer message]"

Contexto:
- Industria: [industry]
- Uso actual: [usage]
- Presupuesto: [budget if known]
- Objetivo: [goal]

Necesito:
1. Análisis de ROI específico
2. 3 opciones de respuesta
3. Script de follow-up

Estructura: Similar a Cost_Support_Guide.md
```

### **Prompt 2: Crear Plan Personalizado**
```
Cliente necesita:
- [Requirement 1]
- [Requirement 2]
- Presupuesto: $XXX/mes

Crear:
1. Plan personalizado que se ajuste al presupuesto
2. Cálculo de ROI
3. Comparativa con plan estándar
4. Script de presentación

Base: Cost_Conversation_Templates.md template
```

---

## ⚠️ RED FLAGS - Escalar Inmediatamente

Escalar a management cuando:

- 💰 Solicitud de reembolso >$2,000
- ⚖️ Menciona legal/lawyer/abogado
- 📰 Menciona medios/prensa/social media amplification
- 🔥 Amenaza de cancelar cuenta grande (>10 usuarios)
- 😠 Lenguaje agresivo o amenazante
- 📞 Múltiples llamadas del mismo cliente el mismo día
- 🚨 Error de facturación sistemático (>3 reportes)

**Contacto de Escalamiento:**
- Email: escalation@blatam.com
- Slack: #cs-escalation
- Urgente: [Phone number]

---

## 🎁 "ADD-ONS" GRATIS (Para Retención)

Stock de compensaciones que puedes ofrecer:
- ✓ Setup personalizado (valor $XXX)
- ✓ Capacitación 1:1, 3 horas (valor $XXX)
- ✓ 30 días de features premium (valor $XXX)
- ✓ Onboarding prioritario (valor $XXX)
- ✓ Slots garantizados en próximos eventos (valor $XXX)

**Límite:** Hasta $500 en valor por incidente

---

## 📞 SCRIPT TELEFÓNICO (2 minutos)

```
- 0:00 | Saludo empático
- 0:15 | Confirmación de entendimiento
- 0:45 | Propuesta de solución
- 1:15 | Confirmación de acuerdo
- 1:45 | Próximos pasos
- 2:00 | Cierre

"Primero, lo siento mucho por [issue]. 
¿Entiendo correctamente que [understanding]?
Aquí está lo que voy a hacer: [solution].
¿Esto funciona para ti?
Perfecto, procesando ahora mismo. 
Te envío confirmación en 30 minutos.
Gracias por tu paciencia."
```

---

## ✅ CHECKLIST DE CORTA (30 segundos)

Antes de enviar email/respuesta:
- [ ] Empatía en primera línea
- [ ] Solución clara y concreta
- [ ] Timeline específico
- [ ] Persona de contacto
- [ ] Call-to-action claro
- [ ] Sentimiento positivo al cierre

---

## 🎯 MÉTRICAS PERSONALES (Daily)

Trackea diariamente:
- Tiempo promedio de respuesta: <2 horas
- Tasa de satisfacción: >95%
- Tasa de resolución en 1er contacto: >80%
- Valor de créditos aplicados: Mantener promedio
- Upsell attempts: >50% de interacciones

---

## 🔄 FEEDBACK LOOP

Después de cada caso importante:
1. **¿Qué funcionó?** Documentar
2. **¿Qué no funcionó?** Mejorar
3. **¿Qué aprendí?** Compartir con equipo
4. **¿Qué debo mejorar?** Practicar

---

**Quick Access Links:**
- 📄 Guía Completa: `Cost_Support_Guide.md`
- 📄 Escenarios: `Financial_Resolution_Scenarios.md`
- 📄 Templates: `Cost_Conversation_Templates.md`
- 📊 Dashboard: [Link]

**Última Actualización:** Enero 2025  
**Contacto:** support@blatam.com


