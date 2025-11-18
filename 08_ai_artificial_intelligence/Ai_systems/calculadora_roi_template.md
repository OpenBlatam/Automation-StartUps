# 💰 CALCULADORA DE ROI PARA PROYECTOS DE CONSULTORÍA
## *Herramienta Completa para Calcular y Presentar Retorno de Inversión*

> **💡 Objetivo**: Esta calculadora te ayuda a calcular, validar y presentar el ROI de tus proyectos de consultoría de manera profesional y convincente.

---

## 📋 Tabla de Contenidos

1. [Fórmulas Principales](#fórmulas-principales)
2. [Plantilla de Cálculo](#plantilla-de-cálculo)
3. [Ejemplo Completo Paso a Paso](#ejemplo-completo-paso-a-paso)
4. [Escenarios y Análisis de Sensibilidad](#escenarios-y-análisis-de-sensibilidad)
5. [Desglose de Beneficios](#desglose-de-beneficios)
6. [Casos de Uso por Tipo de Proyecto](#casos-de-uso-por-tipo-de-proyecto)
7. [Plantilla Excel/Google Sheets](#plantilla-excelgoogle-sheets)
8. [Validación y Presentación](#validación-y-presentación)

---

## FÓRMULAS PRINCIPALES

> **💡 Tip**: Usa estas fórmulas como base, pero siempre valida con el cliente y ajusta según el contexto específico del proyecto.

### 1. ROI Simple

**Fórmula:**
```
ROI = (Beneficios - Inversión) / Inversión × 100
```

**Cuándo Usar:**
- Análisis rápido de viabilidad
- Comparación inicial de proyectos
- Comunicación con stakeholders no financieros

**Ejemplo Básico:**
- Inversión: $100,000
- Beneficios Anuales: $150,000
- ROI = ($150,000 - $100,000) / $100,000 × 100 = **50%**

**Interpretación:**
- ✅ ROI > 0%: Proyecto genera retorno positivo
- ✅ ROI > 20%: Proyecto atractivo
- ✅ ROI > 50%: Proyecto muy atractivo
- ⚠️ ROI < 0%: Proyecto no viable (a menos que haya beneficios intangibles)

**💡 Mejores Prácticas:**
- Calcula ROI para Año 1, 3 años y 5 años
- Incluye todos los costos (directos e indirectos)
- Sé conservador en estimaciones de beneficios
- Documenta todos los supuestos

---

### 2. Período de Recuperación (Payback)

**Fórmula:**
```
Payback = Inversión / Beneficios Mensuales
```

**Cuándo Usar:**
- Clientes preocupados por liquidez
- Proyectos con alto riesgo
- Comparación de proyectos con diferentes perfiles de riesgo

**Ejemplo:**
- Inversión: $100,000
- Beneficios Mensuales: $12,500
- Payback = $100,000 / $12,500 = **8 meses**

**Interpretación:**
- ✅ Payback < 6 meses: Recuperación muy rápida
- ✅ Payback 6-12 meses: Recuperación rápida
- ✅ Payback 12-24 meses: Recuperación aceptable
- ⚠️ Payback > 24 meses: Considerar si el proyecto es viable

**💡 Variación: Payback Descontado**
Si los beneficios varían mes a mes, usa:
```
Payback = Mes donde Beneficios Acumulados ≥ Inversión
```

**Ejemplo con Beneficios Variables:**
| Mes | Beneficio Mensual | Acumulado |
|-----|-------------------|-----------|
| 1 | $8,000 | $8,000 |
| 2 | $10,000 | $18,000 |
| 3 | $12,000 | $30,000 |
| 4 | $15,000 | $45,000 |
| 5 | $15,000 | $60,000 |
| 6 | $15,000 | $75,000 |
| 7 | $15,000 | $90,000 |
| 8 | $15,000 | $105,000 ✅ |

**Payback = 8 meses** (cuando acumulado supera $100,000)

---

### 3. Valor Presente Neto (VPN)

**Fórmula:**
```
VPN = Σ (Beneficios_t / (1 + r)^t) - Inversión

donde:
- r = tasa de descuento (ej: 10% = 0.10)
- t = período (año 1, 2, 3...)
- Beneficios_t = beneficios en el período t
```

**Cuándo Usar:**
- Proyectos con múltiples períodos
- Comparación de proyectos con diferentes perfiles temporales
- Análisis financiero detallado para CFO/Finanzas

**Cómo Determinar la Tasa de Descuento:**
- **WACC (Weighted Average Cost of Capital)**: Tasa promedio ponderada
- **Tasa de Oportunidad**: Retorno de inversión alternativa
- **Tasa de Riesgo**: Ajustada por riesgo del proyecto
- **Típico**: 8-15% para proyectos corporativos

**Ejemplo Detallado (3 años, tasa 10%):**
- Inversión Inicial: $100,000
- Beneficios Año 1: $50,000
- Beneficios Año 2: $60,000
- Beneficios Año 3: $70,000

**Cálculo Paso a Paso:**

| Año | Beneficio | Factor Descuento (1+r)^t | Valor Presente |
|-----|-----------|---------------------------|----------------|
| 0 | -$100,000 | 1.000 | -$100,000 |
| 1 | $50,000 | 1.100 | $45,455 |
| 2 | $60,000 | 1.210 | $49,587 |
| 3 | $70,000 | 1.331 | $52,592 |
| **TOTAL** | | | **$47,634** |

**VPN = $47,634**

**Interpretación:**
- ✅ VPN > 0: Proyecto genera valor (viable)
- ✅ VPN > Inversión × 0.2: Proyecto muy atractivo
- ⚠️ VPN < 0: Proyecto destruye valor (no viable)

**💡 Fórmula Excel:**
```
=NPV(tasa, rango_beneficios) - inversión_inicial
```

---

### 4. Tasa Interna de Retorno (TIR)

La TIR es la tasa de descuento que hace el VPN = 0

**Cálculo:** Requiere iteración o herramienta financiera

**Interpretación:**
- TIR > Tasa de descuento = Proyecto viable
- TIR < Tasa de descuento = Proyecto no viable

---

## PLANTILLA DE CÁLCULO

### Datos de Entrada

#### Inversión
- **Inversión Inicial:** $[X]
- **Inversión Año 1:** $[X]
- **Inversión Año 2:** $[X]
- **Inversión Año 3:** $[X]
- **Total Inversión:** $[X]

#### Beneficios
- **Ahorro de Costos Año 1:** $[X]
- **Incremento de Ingresos Año 1:** $[X]
- **Beneficios Adicionales Año 1:** $[X]
- **Total Beneficios Año 1:** $[X]

- **Ahorro de Costos Año 2:** $[X]
- **Incremento de Ingresos Año 2:** $[X]
- **Beneficios Adicionales Año 2:** $[X]
- **Total Beneficios Año 2:** $[X]

- **Ahorro de Costos Año 3:** $[X]
- **Incremento de Ingresos Año 3:** $[X]
- **Beneficios Adicionales Año 3:** $[X]
- **Total Beneficios Año 3:** $[X]

#### Parámetros
- **Tasa de Descuento:** [X]%
- **Horizonte de Análisis:** [X] años

---

### Cálculos

#### Año 1
- **Beneficios Netos:** $[X] - $[X] = $[X]
- **ROI Anual:** [X]%
- **Beneficios Acumulados:** $[X]
- **VPN:** $[X]

#### Año 2
- **Beneficios Netos:** $[X] - $[X] = $[X]
- **ROI Anual:** [X]%
- **ROI Acumulado:** [X]%
- **Beneficios Acumulados:** $[X]
- **VPN:** $[X]

#### Año 3
- **Beneficios Netos:** $[X] - $[X] = $[X]
- **ROI Anual:** [X]%
- **ROI Acumulado:** [X]%
- **Beneficios Acumulados:** $[X]
- **VPN:** $[X]

---

### Resumen de Métricas

| Métrica | Valor |
|---------|-------|
| **Inversión Total** | $[X] |
| **Beneficios Totales (3 años)** | $[X] |
| **ROI Total (3 años)** | [X]% |
| **ROI Anual Promedio** | [X]% |
| **Payback** | [X] meses |
| **VPN (3 años)** | $[X] |
| **TIR** | [X]% |

---

## ESCENARIOS

### Escenario Conservador (80% de beneficios)
- **Beneficios Año 1:** $[X]
- **Beneficios Año 2:** $[X]
- **Beneficios Año 3:** $[X]
- **ROI Total:** [X]%
- **Payback:** [X] meses

### Escenario Base (100% de beneficios)
- **Beneficios Año 1:** $[X]
- **Beneficios Año 2:** $[X]
- **Beneficios Año 3:** $[X]
- **ROI Total:** [X]%
- **Payback:** [X] meses

### Escenario Optimista (120% de beneficios)
- **Beneficios Año 1:** $[X]
- **Beneficios Año 2:** $[X]
- **Beneficios Año 3:** $[X]
- **ROI Total:** [X]%
- **Payback:** [X] meses

### ROI Esperado (Valor Esperado)
```
ROI Esperado = (0.30 × ROI Conservador) + (0.50 × ROI Base) + (0.20 × ROI Optimista)
ROI Esperado = [X]%
```

---

## DESGLOSE DE BENEFICIOS

### Ahorro de Costos

| Concepto | Antes | Después | Ahorro Anual |
|----------|-------|---------|--------------|
| **Procesos Manuales** | $[X] | $[X] | $[X] |
| **Tiempo de Personal** | $[X] | $[X] | $[X] |
| **Errores y Re-trabajos** | $[X] | $[X] | $[X] |
| **Infraestructura** | $[X] | $[X] | $[X] |
| **Mantenimiento** | $[X] | $[X] | $[X] |
| **TOTAL AHORRO** | | | **$[X]** |

### Incremento de Ingresos

| Concepto | Antes | Después | Incremento Anual |
|----------|-------|---------|------------------|
| **Ventas** | $[X] | $[X] | $[X] |
| **Nuevos Clientes** | $[X] | $[X] | $[X] |
| **Upselling** | $[X] | $[X] | $[X] |
| **Reducción de Churn** | $[X] | $[X] | $[X] |
| **TOTAL INCREMENTO** | | | **$[X]** |

### Beneficios Adicionales

| Concepto | Valor Anual |
|----------|------------|
| **Reducción de Riesgos** | $[X] |
| **Mejora en Cash Flow** | $[X] |
| **Optimización de Inventario** | $[X] |
| **Eficiencia Energética** | $[X] |
| **TOTAL ADICIONALES** | **$[X]** |

---

## GRÁFICAS Y VISUALIZACIONES

### Flujo de Caja Proyectado

```
Año 0: -$[X] (Inversión)
Año 1: +$[X] (Beneficios)
Año 2: +$[X] (Beneficios)
Año 3: +$[X] (Beneficios)
```

### Acumulado

```
Año 0: -$[X]
Año 1: -$[X] + $[X] = $[X]
Año 2: $[X] + $[X] = $[X]
Año 3: $[X] + $[X] = $[X]
```

---

## VALIDACIÓN DE CÁLCULOS

### Checklist de Validación

- [ ] Todos los costos incluidos
- [ ] Todos los beneficios incluidos
- [ ] Tasa de descuento apropiada
- [ ] Horizonte de tiempo realista
- [ ] Escenarios considerados
- [ ] Supuestos documentados
- [ ] Cálculos verificados
- [ ] Comparación con benchmarks

---

## PRESENTACIÓN DE RESULTADOS

### Formato Ejecutivo

**Inversión:** $[X]  
**ROI Año 1:** [X]%  
**Payback:** [X] meses  
**VPN (3 años):** $[X]  
**TIR:** [X]%

### Formato Detallado

[Incluir todas las tablas y cálculos anteriores]

---

*Esta calculadora debe usarse como guía. Ajuste según las necesidades específicas del proyecto.*






