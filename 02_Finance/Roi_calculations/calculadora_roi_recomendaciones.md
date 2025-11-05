---
title: "Calculadora Roi Recomendaciones"
category: "02_finance"
tags: ["business", "finance"]
created: "2025-10-29"
path: "02_finance/Roi_calculations/calculadora_roi_recomendaciones.md"
---

# 💰 Calculadora ROI - Sistemas de Recomendaciones Personalizadas

## 📊 FÓRMULAS DE CÁLCULO

### ROI Básico

```
ROI = (Ganancia - Inversión) / Inversión × 100
```

**Donde:**
- **Ganancia** = Revenue adicional generado por recomendaciones
- **Inversión** = Costo implementación + mantenimiento

---

### Revenue Adicional de Recomendaciones

```
Revenue Recomendaciones = 
  (Conversión con Recs - Conversión sin Recs) × 
  Visitantes Únicos × 
  Ticket Promedio
```

**Ejemplo:**
- Conversión sin recomendaciones: 2.1%
- Conversión con recomendaciones: 8.5%
- Visitantes/mes: 50,000
- Ticket promedio: $75

**Cálculo:**
- Conversiones adicionales: (8.5% - 2.1%) × 50,000 = 3,200
- Revenue adicional: 3,200 × $75 = **$240,000/mes**

---

### Ticket Promedio Mejorado

```
Ticket Promedio Mejorado = 
  Ticket Promedio Base × (1 + % Incremento Cross-Sell/Up-Sell)
```

**Ejemplo:**
- Ticket promedio base: $75
- Incremento esperado: +40% (típico con cross-sell efectivo)
- Ticket promedio mejorado: $75 × 1.40 = **$105**

**Impacto mensual:**
- Si tienes 3,200 conversiones/mes adicionales
- Revenue adicional ticket: (3,200 × $105) - (3,200 × $75) = **$96,000/mes**

---

### ROI Total (Anual)

```
ROI Anual = 
  [(Revenue Recomendaciones Mensual × 12) + 
   (Revenue Ticket Mejorado Mensual × 12) - 
   (Costo Implementación + Mantenimiento Anual)] / 
  (Costo Implementación + Mantenimiento Anual) × 100
```

**Ejemplo Completo:**
- Revenue recomendaciones: $240,000/mes × 12 = $2,880,000/año
- Revenue ticket mejorado: $96,000/mes × 12 = $1,152,000/año
- Costo implementación: $30,000 (Python/ML) o $18,000 (No-Code primer año)
- Mantenimiento anual: $6,000 (Python) o $18,000 (No-Code)

**Con Python/ML:**
- Ganancia anual: $2,880,000 + $1,152,000 = $4,032,000
- Inversión: $30,000 + $6,000 = $36,000
- ROI: ($4,032,000 - $36,000) / $36,000 × 100 = **11,100%**

**Con No-Code:**
- Ganancia anual: $4,032,000
- Inversión: $18,000 + $18,000 = $36,000
- ROI: ($4,032,000 - $36,000) / $36,000 × 100 = **11,100%**

---

## 🎯 CALCULADORA INTERACTIVA (Template)

### Inputs del Usuario

```
1. Visitantes únicos/mes: [______]
2. Conversión actual (%): [______]
3. Conversión esperada con recomendaciones (%): [______]
4. Ticket promedio actual: $[______]
5. Incremento ticket esperado (%): [______]
6. Costo implementación: $[______]
7. Costo mantenimiento/mes: $[______]
```

### Cálculos Automáticos

```
Conversiones actuales/mes = Visitantes × Conversión Actual
Conversiones con recomendaciones/mes = Visitantes × Conversión Esperada
Conversiones adicionales = Conversiones con Recs - Conversiones Actuales

Revenue adicional conversiones = Conversiones Adicionales × Ticket Promedio
Ticket mejorado = Ticket Promedio × (1 + Incremento Ticket%)
Revenue adicional ticket = Conversiones Adicionales × (Ticket Mejorado - Ticket Base)

Revenue total adicional/mes = Revenue Conversiones + Revenue Ticket
Revenue adicional/año = Revenue Total Mensual × 12

Costo total año 1 = Costo Implementación + (Mantenimiento × 12)
ROI año 1 = (Revenue Adicional Año - Costo Total Año 1) / Costo Total Año 1 × 100

Payback Period (meses) = Costo Implementación / Revenue Adicional Mensual
```

---

## 📊 ESCENARIOS EJEMPLO

### Escenario 1: E-commerce Pequeño-Mediano

**Parámetros:**
- Visitantes/mes: 10,000
- Conversión actual: 2.0%
- Conversión esperada: 5.0%
- Ticket promedio: $50
- Incremento ticket: +30%
- Implementación: No-Code ($2,000 setup + $500/mes)

**Resultados:**
- Conversiones adicionales: 300/mes
- Revenue adicional conversiones: $15,000/mes
- Revenue adicional ticket: $4,500/mes
- **Revenue total adicional: $19,500/mes**
- Costo año 1: $8,000
- **ROI año 1: 2,825%**
- **Payback: 0.4 meses (12 días)**

---

### Escenario 2: E-commerce Mediano

**Parámetros:**
- Visitantes/mes: 50,000
- Conversión actual: 2.1%
- Conversión esperada: 8.5%
- Ticket promedio: $75
- Incremento ticket: +40%
- Implementación: Python/ML ($30,000 + $500/mes)

**Resultados:**
- Conversiones adicionales: 3,200/mes
- Revenue adicional conversiones: $240,000/mes
- Revenue adicional ticket: $96,000/mes
- **Revenue total adicional: $336,000/mes**
- Costo año 1: $36,000
- **ROI año 1: 11,033%**
- **Payback: 0.1 meses (3 días)**

---

### Escenario 3: Marketplace Grande

**Parámetros:**
- Visitantes/mes: 200,000
- Conversión actual: 1.5%
- Conversión esperada: 4.5%
- Ticket promedio: $100
- Incremento ticket: +35%
- Implementación: Python/ML ($50,000 + $1,000/mes)

**Resultados:**
- Conversiones adicionales: 6,000/mes
- Revenue adicional conversiones: $600,000/mes
- Revenue adicional ticket: $210,000/mes
- **Revenue total adicional: $810,000/mes**
- Costo año 1: $62,000
- **ROI año 1: 15,574%**
- **Payback: 0.08 meses (2 días)**

---

## 💡 MÉTRICAS ADICIONALES DE VALOR

### Customer Lifetime Value (LTV) Impact

```
LTV Mejorado = LTV Base × (1 + % Incremento Retention)
```

Si recomendaciones mejoran retención 20%:
- LTV base: $300
- LTV mejorado: $300 × 1.20 = $360
- Incremento LTV: $60 por cliente

---

### Costo de Adquisición (CAC) Eficiencia

```
CAC Efectivo con Recomendaciones = 
  CAC Base × (1 - % Conversión Recomendaciones)
```

Si recomendaciones mejoran conversión 2x:
- CAC base: $50
- CAC efectivo: $50 × 0.5 = $25 (mejor eficiencia)

---

### Revenue Share de Recomendaciones

```
% Revenue de Recomendaciones = 
  (Revenue Recomendaciones / Revenue Total) × 100
```

**Objetivo típico:** 20-30% del revenue total viene de recomendaciones

---

## 📈 PROYECCIONES A 3 AÑOS

### Escenario Conservador (Crecimiento 10% anual)

**Año 1:**
- Revenue adicional: $336,000/mes × 12 = $4,032,000
- Costo: $36,000
- ROI: 11,033%

**Año 2:**
- Revenue adicional: $369,600/mes × 12 = $4,435,200 (crecimiento 10%)
- Costo: $6,000 (solo mantenimiento)
- ROI: 73,820%

**Año 3:**
- Revenue adicional: $406,560/mes × 12 = $4,878,720
- Costo: $6,000
- ROI: 81,245%

**ROI acumulado 3 años:** ~165,000%

---

## ✅ CHECKLIST PRE-CÁLCULO

Antes de calcular ROI, asegúrate de tener:

- [ ] Datos históricos de visitantes/conversión actual
- [ ] Ticket promedio actual documentado
- [ ] Benchmarks de industria (conversión con/sin recomendaciones)
- [ ] Estimación de costo implementación (Python vs No-Code)
- [ ] Estimación de costo mantenimiento
- [ ] Tiempo disponible para implementación
- [ ] Nivel técnico del equipo

---

## 🎯 FACTORES QUE AFECTAN ROI

### Positivos (Aumentan ROI)
✅ **Alto volumen de visitantes:** Más escala = más impacto
✅ **Baja conversión actual:** Más margen de mejora
✅ **Ticket promedio alto:** Más valor por conversión
✅ **Catálogo grande:** Más oportunidades de recomendación
✅ **Datos históricos ricos:** Mejor calidad de recomendaciones
✅ **Implementación Python (largo plazo):** Costos recurrentes menores

### Negativos (Reducen ROI)
❌ **Volumen bajo visitantes:** Menos escala
❌ **Conversión alta actual:** Menos margen de mejora
❌ **Ticket promedio bajo:** Menor impacto por conversión
❌ **Datos históricos pobres:** Recomendaciones menos efectivas
❌ **No-Code en volumen alto:** Costos crecen con escala

---

## 📊 TEMPLATE EXCEL/GOOGLE SHEETS

### Hoja 1: Inputs
- Visitantes, conversiones, tickets, costos

### Hoja 2: Cálculos
- Fórmulas automáticas de ROI

### Hoja 3: Proyecciones
- Escenarios conservador, realista, optimista

### Hoja 4: Comparativa
- Python/ML vs No-Code
- Diferentes volúmenes
- Diferentes conversiones objetivo

---

**Última actualización:** [Fecha]
**Versión:** 1.0 - Calculadora ROI Completa

