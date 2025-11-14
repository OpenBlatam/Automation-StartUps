---
title: "Calculadora ROI Completa - Fórmulas y Ejemplos"
category: "09_sales"
tags: ["sales", "roi", "calculator"]
created: "2025-01-27"
path: "CALCULADORA_ROI_COMPLETA.md"
---

# 💰 Calculadora ROI Completa
## Fórmulas, Ejemplos y Templates Listos para Usar

**Versión:** 1.0  
**Última actualización:** Enero 2025

---

## 🎯 CALCULADORA 1: ROI PARA SAAS MARKETING

### Fórmulas Completas

**Inputs:**
```
I1 = Número de campañas por mes
I2 = Tiempo por campaña (horas)
I3 = Costo herramientas actuales/mes ($)
I4 = Valor hora del equipo ($)
I5 = Costo del SaaS ($)
```

**Cálculos:**
```
Tiempo Total Mensual = I1 × I2
Tiempo Ahorrado = Tiempo Total × 0.5 (50% ahorro)
Ahorro por Tiempo = Tiempo Ahorrado × I4
Ahorro por Costos = I3 × 0.3 (30% ahorro)
Ahorro Total = Ahorro por Tiempo + Ahorro por Costos
ROI = ((Ahorro Total - I5) / I5) × 100
Payback = I5 / (Ahorro Total / 12)
```

---

### Ejemplo Completo

**Inputs:**
```
I1 = 20 campañas/mes
I2 = 4 horas/campaña
I3 = $1,000/mes (herramientas actuales)
I4 = $50/hora (valor hora equipo)
I5 = $997/mes (costo SaaS)
```

**Cálculos:**
```
Tiempo Total Mensual = 20 × 4 = 80 horas
Tiempo Ahorrado = 80 × 0.5 = 40 horas
Ahorro por Tiempo = 40 × $50 = $2,000/mes
Ahorro por Costos = $1,000 × 0.3 = $300/mes
Ahorro Total = $2,000 + $300 = $2,300/mes
ROI = (($2,300 - $997) / $997) × 100 = 130.7%
Payback = $997 / ($2,300 / 12) = 5.2 meses
```

**Resultado:**
- Ahorro mensual: $2,300
- ROI: 130.7%
- Payback: 5.2 meses
- Ahorro anual: $27,600

---

## 🎯 CALCULADORA 2: ROI PARA CURSO IA

### Fórmulas Completas

**Inputs:**
```
I1 = Tiempo que tomaría aprender solo (horas)
I2 = Valor hora tuya ($)
I3 = Costo de oportunidades perdidas/mes ($)
I4 = Costo del curso ($)
I5 = Tiempo para completar curso (horas)
```

**Cálculos:**
```
Tiempo Ahorrado = I1 - I5
Valor Tiempo Ahorrado = Tiempo Ahorrado × I2
Valor Oportunidades = I3 × 6 (6 meses de oportunidades)
Valor Total = Valor Tiempo Ahorrado + Valor Oportunidades
ROI = ((Valor Total - I4) / I4) × 100
```

---

### Ejemplo Completo

**Inputs:**
```
I1 = 200 horas (aprender solo)
I2 = $75/hora
I3 = $500/mes (oportunidades perdidas)
I4 = $497 (costo curso)
I5 = 40 horas (completar curso)
```

**Cálculos:**
```
Tiempo Ahorrado = 200 - 40 = 160 horas
Valor Tiempo Ahorrado = 160 × $75 = $12,000
Valor Oportunidades = $500 × 6 = $3,000
Valor Total = $12,000 + $3,000 = $15,000
ROI = (($15,000 - $497) / $497) × 100 = 2,919%
```

**Resultado:**
- Valor obtenido: $15,000
- ROI: 2,919%
- Tiempo ahorrado: 160 horas

---

## 🎯 CALCULADORA 3: ROI PARA IA BULK

### Fórmulas Completas

**Inputs:**
```
I1 = Documentos generados/mes
I2 = Tiempo por documento manual (horas)
I3 = Valor hora ($)
I4 = Costo del SaaS ($)
I5 = Tiempo por documento con IA (horas)
```

**Cálculos:**
```
Tiempo Total Manual = I1 × I2
Tiempo Total con IA = I1 × I5
Tiempo Ahorrado = Tiempo Total Manual - Tiempo Total con IA
Ahorro Mensual = Tiempo Ahorrado × I3
ROI = ((Ahorro Mensual - I4) / I4) × 100
Payback = I4 / (Ahorro Mensual / 12)
```

---

### Ejemplo Completo

**Inputs:**
```
I1 = 50 documentos/mes
I2 = 2 horas/documento (manual)
I3 = $60/hora
I4 = $97/mes (costo SaaS)
I5 = 0.5 horas/documento (con IA)
```

**Cálculos:**
```
Tiempo Total Manual = 50 × 2 = 100 horas
Tiempo Total con IA = 50 × 0.5 = 25 horas
Tiempo Ahorrado = 100 - 25 = 75 horas
Ahorro Mensual = 75 × $60 = $4,500
ROI = (($4,500 - $97) / $97) × 100 = 4,540%
Payback = $97 / ($4,500 / 12) = 0.26 meses (8 días)
```

**Resultado:**
- Ahorro mensual: $4,500
- ROI: 4,540%
- Payback: 8 días
- Ahorro anual: $54,000

---

## 📊 TEMPLATE GOOGLE SHEETS

### Configuración Completa

**Pestaña "Inputs":**
```
A1: "ROI Calculator - SaaS Marketing"
B1: "Valor"

A3: "Número de campañas/mes"
B3: 20

A4: "Tiempo por campaña (horas)"
B4: 4

A5: "Costo herramientas actuales/mes"
B5: 1000

A6: "Valor hora del equipo"
B6: 50

A7: "Costo del SaaS/mes"
B7: 997
```

**Pestaña "Cálculos":**
```
A1: "CÁLCULOS"
B1: "Valor"

A3: "Tiempo Total Mensual (horas)"
B3: =Inputs!B3*Inputs!B4

A4: "Tiempo Ahorrado (horas)"
B4: =B3*0.5

A5: "Ahorro por Tiempo ($)"
B5: =B4*Inputs!B6

A6: "Ahorro por Costos ($)"
B6: =Inputs!B5*0.3

A7: "Ahorro Total Mensual ($)"
B7: =B5+B6

A8: "ROI (%)"
B8: =((B7-Inputs!B7)/Inputs!B7)*100

A9: "Payback (meses)"
B9: =Inputs!B7/(B7/12)

A10: "Ahorro Anual ($)"
B10: =B7*12
```

---

## 💻 CÓDIGO JAVASCRIPT

### Calculadora Web Interactiva

```javascript
// ROI Calculator - JavaScript
function calculateROI() {
  // Get inputs
  const campaigns = parseFloat(document.getElementById('campaigns').value);
  const timePerCampaign = parseFloat(document.getElementById('time').value);
  const currentCost = parseFloat(document.getElementById('cost').value);
  const hourlyRate = parseFloat(document.getElementById('rate').value);
  const saasCost = parseFloat(document.getElementById('saasCost').value);
  
  // Calculate
  const totalTime = campaigns * timePerCampaign;
  const timeSaved = totalTime * 0.5;
  const timeSavings = timeSaved * hourlyRate;
  const costSavings = currentCost * 0.3;
  const totalSavings = timeSavings + costSavings;
  const roi = ((totalSavings - saasCost) / saasCost) * 100;
  const payback = saasCost / (totalSavings / 12);
  const annualSavings = totalSavings * 12;
  
  // Display results
  document.getElementById('timeSaved').textContent = timeSaved.toFixed(1) + ' horas';
  document.getElementById('timeSavings').textContent = '$' + timeSavings.toLocaleString();
  document.getElementById('costSavings').textContent = '$' + costSavings.toLocaleString();
  document.getElementById('totalSavings').textContent = '$' + totalSavings.toLocaleString();
  document.getElementById('roi').textContent = roi.toFixed(1) + '%';
  document.getElementById('payback').textContent = payback.toFixed(1) + ' meses';
  document.getElementById('annualSavings').textContent = '$' + annualSavings.toLocaleString();
  
  // Send to CRM if ROI > 200%
  if (roi > 200) {
    sendToCRM({
      email: document.getElementById('email').value,
      roi: roi,
      totalSavings: totalSavings,
      score_addition: 20
    });
  }
}

function sendToCRM(data) {
  fetch('https://hook.us1.make.com/your-webhook', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(data)
  });
}
```

---

## 📧 EMAIL TEMPLATE CON ROI

### Template Personalizado

```
Asunto: Tu ROI personalizado: [X]% y ahorro de $[X]/mes

Hola [Nombre],

Basándome en tu información, calculé tu ROI potencial con nuestro SaaS:

📊 TUS RESULTADOS:
• Tiempo ahorrado: [X] horas/mes
• Ahorro por tiempo: $[X]/mes
• Ahorro por costos: $[X]/mes
• Ahorro total: $[X]/mes
• ROI: [X]%
• Payback: [X] meses
• Ahorro anual: $[X]

💡 QUÉ SIGNIFICA:
Con un ROI de [X]%, recuperas tu inversión en [X] meses y después es puro ahorro.

🎯 PRÓXIMOS PASOS:
1. Demo personalizada de 30 minutos
2. Setup gratuito si decides continuar
3. 30 días de garantía 100%

[CTA: Agendar Demo]

¿Preguntas? Responde este email.

Saludos,
[Tu Nombre]
```

---

## 📊 TABLA COMPARATIVA DE ROI

### Comparación de Productos

| Producto | Ahorro Mensual | ROI | Payback | Ahorro Anual |
|----------|----------------|-----|---------|--------------|
| **SaaS Marketing** | $2,300 | 130.7% | 5.2 meses | $27,600 |
| **Curso IA** | $2,500* | 2,919% | 0.2 meses | $15,000* |
| **IA Bulk** | $4,500 | 4,540% | 0.26 meses | $54,000 |

*Valor obtenido, no ahorro recurrente

---

## 🎯 FACTORES DE AJUSTE

### Factor 1: Tamaño de Empresa

**Empresa Pequeña (<50 empleados):**
- Multiplicar ahorro por 0.7
- ROI más bajo, pero aún positivo

**Empresa Mediana (50-500 empleados):**
- Usar cálculos estándar
- ROI como se muestra

**Empresa Grande (>500 empleados):**
- Multiplicar ahorro por 1.5
- ROI más alto

---

### Factor 2: Nivel de Uso

**Uso Bajo (<50% capacidad):**
- Multiplicar ahorro por 0.5
- ROI positivo pero moderado

**Uso Medio (50-80% capacidad):**
- Usar cálculos estándar
- ROI como se muestra

**Uso Alto (>80% capacidad):**
- Multiplicar ahorro por 1.3
- ROI más alto

---

## 💡 TIPS PARA MEJORAR ROI

### Tip 1: Enfocarse en Ahorro de Tiempo
- Tiempo ahorrado = Mayor ROI
- Mostrar valor de tiempo
- Calcular correctamente valor hora

### Tip 2: Incluir Costos Ocultos
- Tiempo de onboarding
- Tiempo de mantenimiento
- Costos de errores

### Tip 3: Mostrar Ahorro Anual
- $2,300/mes = $27,600/año
- Más impactante que mensual
- Muestra valor a largo plazo

---

## 📋 CHECKLIST DE USO

### Antes de Calcular
- [ ] Tener datos reales del prospect
- [ ] Entender su situación actual
- [ ] Conocer su valor hora

### Durante Cálculo
- [ ] Usar fórmulas correctas
- [ ] Ajustar según factores
- [ ] Validar resultados

### Después de Calcular
- [ ] Presentar de forma clara
- [ ] Enviar email con resultados
- [ ] Seguir según ROI

---

**Fin de Calculadora ROI Completa**

*Usar estas fórmulas y templates para calcular y presentar ROI de manera efectiva.*

