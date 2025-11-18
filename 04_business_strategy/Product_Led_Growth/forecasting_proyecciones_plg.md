# 📈 Forecasting y Proyecciones Financieras para PLG

> **💡 Guía de Planificación**: Cómo crear proyecciones financieras realistas y forecasting de métricas PLG para planificación estratégica y presentaciones a inversores.

---

## 📋 Tabla de Contenidos

1. [🎯 Fundamentos de Forecasting PLG](#-fundamentos-de-forecasting-plg)
2. [📊 Proyección de Adquisición](#-proyección-de-adquisición)
3. [💰 Proyección de Revenue](#-proyección-de-revenue)
4. [🔄 Proyección de Retención](#-proyección-de-retención)
5. [📈 Modelos de Forecasting](#-modelos-de-forecasting)
6. [🎯 Escenarios (Base, Optimista, Pesimista)](#-escenarios-base-optimista-pesimista)
7. [✅ Templates de Proyección](#-templates-de-proyección)

---

## 🎯 Fundamentos de Forecasting PLG

### **Principios de Forecasting PLG**

**1. Basado en Datos Históricos**
- Usar datos reales como base
- Analizar tendencias
- Identificar patrones

**2. Considerar Estacionalidad**
- Variaciones mensuales
- Efectos estacionales
- Eventos especiales

**3. Supuestos Claros**
- Documentar todos los supuestos
- Justificar proyecciones
- Revisar regularmente

**4. Múltiples Escenarios**
- Base case
- Optimista
- Pesimista

### **Componentes del Forecasting PLG**

```
Forecasting PLG = 
  Adquisición (Sign-ups) ×
  Activación (%) ×
  Conversión (%) ×
  Retención (%) ×
  Expansión (%) ×
  ARPU
```

---

## 📊 Proyección de Adquisición

### **Modelo de Adquisición**

**Fórmula Base:**
```
Sign-ups Mes N = Sign-ups Mes N-1 × (1 + Growth Rate)
```

**Factores que Afectan:**
- Marketing spend
- Organic growth
- Viral coefficient
- Estacionalidad

### **Proyección por Canal**

**Canal Orgánico:**
```
Organic Sign-ups = Base × (1 + Organic Growth Rate) ^ Meses
```

**Canal Pagado:**
```
Paid Sign-ups = Marketing Spend / CAC
```

**Canal Viral:**
```
Viral Sign-ups = Existing Users × K-Factor
```

### **Template de Proyección de Adquisición**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN DE ADQUISICIÓN                      │
└─────────────────────────────────────────────────┘

Mes    Orgánico  Pagado  Viral    Total    Growth
─────────────────────────────────────────────────
Mes 1  [_____]   [_____] [_____]  [_____]  -
Mes 2  [_____]   [_____] [_____]  [_____]  [__]%
Mes 3  [_____]   [_____] [_____]  [_____]  [__]%
...
Mes 12 [_____]   [_____] [_____]  [_____]  [__]%

Supuestos:
- Organic growth: [__]%/mes
- Marketing spend: $[_____]/mes
- CAC: $[_____]
- K-factor: [_____]
```

---

## 💰 Proyección de Revenue

### **Modelo de Revenue**

**Fórmula Base:**
```
MRR = (Usuarios Pagantes × ARPU) + Expansion MRR - Churn MRR
```

**Componentes:**
- New MRR (de nuevos clientes)
- Expansion MRR (de upgrades)
- Churn MRR (de cancelaciones)
- Contraction MRR (de downgrades)

### **Proyección de MRR**

**Mes a Mes:**
```
MRR Mes N = 
  MRR Mes N-1 +
  New MRR Mes N +
  Expansion MRR Mes N -
  Churn MRR Mes N -
  Contraction MRR Mes N
```

### **Template de Proyección de Revenue**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN DE REVENUE (MRR)                    │
└─────────────────────────────────────────────────┘

Mes    MRR Inicio  New  Expansion  Churn  MRR Fin  Growth
─────────────────────────────────────────────────────────
Mes 1  $[_____]  $[__]  $[_____]  $[__]  $[_____]  -
Mes 2  $[_____]  $[__]  $[_____]  $[__]  $[_____]  [__]%
Mes 3  $[_____]  $[__]  $[_____]  $[__]  $[_____]  [__]%
...
Mes 12 $[_____]  $[__]  $[_____]  $[__]  $[_____]  [__]%

ARR Proyectado: $[_____]
```

### **Proyección de ARR**

```
ARR = MRR × 12

ARR Proyectado = MRR Mes 12 × 12
```

---

## 🔄 Proyección de Retención

### **Modelo de Retención**

**Cohort-Based:**
```
Usuarios Retenidos Mes N = 
  Usuarios Inicio × Retention Rate Mes N
```

**Churn Rate:**
```
Churn MRR = MRR Inicio × Churn Rate
```

### **Proyección de Cohortes**

```
Cohort: Mes 1
Mes 0:  100 usuarios (100%)
Mes 1:  80 usuarios (80%)
Mes 2:  70 usuarios (70%)
Mes 3:  65 usuarios (65%)
...
Mes 12: 55 usuarios (55%)
```

### **Template de Proyección de Retención**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN DE RETENCIÓN                        │
└─────────────────────────────────────────────────┘

Cohort    Mes 0  Mes 1  Mes 2  Mes 3  ...  Mes 12
─────────────────────────────────────────────────
Mes 1     [100]  [__]   [__]   [__]   ...  [__]
Mes 2     -      [100]  [__]   [__]   ...  [__]
Mes 3     -      -      [100]  [__]   ...  [__]
...
Mes 12    -      -      -      -      ...  [100]

Retention Rate: [__]%/mes
Churn Rate: [__]%/mes
```

---

## 📈 Modelos de Forecasting

### **Modelo 1: Bottom-Up (Detallado)**

**Enfoque:** Proyectar desde componentes individuales

**Pasos:**
1. Proyectar sign-ups por canal
2. Aplicar activation rate
3. Aplicar conversion rate
4. Aplicar retention
5. Calcular revenue

**Ventajas:**
- Más detallado
- Más preciso
- Identifica drivers

**Desventajas:**
- Más complejo
- Requiere más datos
- Más tiempo

---

### **Modelo 2: Top-Down (Agregado)**

**Enfoque:** Proyectar desde métricas agregadas

**Pasos:**
1. Proyectar MRR directamente
2. Aplicar growth rate
3. Ajustar por factores

**Ventajas:**
- Más simple
- Más rápido
- Menos datos necesarios

**Desventajas:**
- Menos detallado
- Menos preciso
- Menos insights

---

### **Modelo 3: Híbrido (Recomendado)**

**Enfoque:** Combinar ambos enfoques

**Pasos:**
1. Bottom-up para corto plazo (3-6 meses)
2. Top-down para largo plazo (6-12+ meses)
3. Validar consistencia

**Ventajas:**
- Balance precisión/simplicidad
- Flexible
- Escalable

---

## 🎯 Escenarios (Base, Optimista, Pesimista)

### **Escenario Base (Más Probable)**

**Supuestos:**
- Tendencias actuales continúan
- Mejoras incrementales
- Sin cambios mayores

**Métricas:**
- Growth rate: Actual + 0-5%
- Conversion: Actual
- Retention: Actual
- CAC: Estable

---

### **Escenario Optimista**

**Supuestos:**
- Mejoras significativas
- Nuevos canales exitosos
- Viralidad aumenta
- Optimizaciones funcionan

**Métricas:**
- Growth rate: Actual + 10-20%
- Conversion: +20-30%
- Retention: +5-10%
- CAC: -20-30%

---

### **Escenario Pesimista**

**Supuestos:**
- Desafíos inesperados
- Competencia aumenta
- Mercado se contrae
- Problemas técnicos

**Métricas:**
- Growth rate: Actual - 10-20%
- Conversion: -10-20%
- Retention: -5-10%
- CAC: +20-30%

---

### **Template de Escenarios**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN POR ESCENARIOS                      │
└─────────────────────────────────────────────────┘

Métrica          Base      Optimista  Pesimista
─────────────────────────────────────────────────
MRR Mes 12      $[_____]  $[_____]  $[_____]
ARR Proyectado  $[_____]  $[_____]  $[_____]
Usuarios Mes 12 [_____]   [_____]   [_____]
CAC             $[_____]  $[_____]  $[_____]
LTV/CAC         [__]:1    [__]:1    [__]:1

Supuestos Base:
- Growth rate: [__]%/mes
- Conversion: [__]%
- Retention: [__]%/mes
- CAC: $[_____]

Supuestos Optimista:
- Growth rate: [__]%/mes (+[__]%)
- Conversion: [__]% (+[__]%)
- Retention: [__]%/mes (+[__]%)
- CAC: $[_____] (-[__]%)

Supuestos Pesimista:
- Growth rate: [__]%/mes (-[__]%)
- Conversion: [__]% (-[__]%)
- Retention: [__]%/mes (-[__]%)
- CAC: $[_____] (+[__]%)
```

---

## ✅ Templates de Proyección

### **Template 1: Proyección Financiera Completa**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN FINANCIERA PLG - [AÑO]              │
└─────────────────────────────────────────────────┘

ADQUISICIÓN
─────────────────────────────────────────────────
Mes    Sign-ups  Activados  Convertidos  Paid Users
─────────────────────────────────────────────────
Mes 1  [_____]   [_____]    [_____]     [_____]
Mes 2  [_____]   [_____]    [_____]     [_____]
...
Mes 12 [_____]   [_____]    [_____]     [_____]

REVENUE
─────────────────────────────────────────────────
Mes    MRR       New MRR    Expansion  Churn  ARR
─────────────────────────────────────────────────
Mes 1  $[_____]  $[_____]   $[_____]   $[__]  $[__]
Mes 2  $[_____]  $[_____]   $[_____]   $[__]  $[__]
...
Mes 12 $[_____]  $[_____]   $[_____]   $[__]  $[__]

COSTOS
─────────────────────────────────────────────────
Mes    Marketing  Sales    Product  Total   CAC
─────────────────────────────────────────────────
Mes 1  $[_____]   $[_____] $[_____] $[_____] $[__]
Mes 2  $[_____]   $[_____] $[_____] $[_____] $[__]
...
Mes 12 $[_____]   $[_____] $[_____] $[_____] $[__]

MÉTRICAS
─────────────────────────────────────────────────
Mes    LTV/CAC   Payback  NRR     Churn
─────────────────────────────────────────────────
Mes 1  [__]:1    [__]m    [__]%   [__]%
Mes 2  [__]:1    [__]m    [__]%   [__]%
...
Mes 12 [__]:1    [__]m    [__]%   [__]%
```

---

### **Template 2: Proyección Simplificada**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN SIMPLIFICADA - [AÑO]                │
└─────────────────────────────────────────────────┘

TRIMESTRE  MRR      ARR      Usuarios  Growth
─────────────────────────────────────────────────
Q1         $[_____] $[_____] [_____]   [__]%
Q2         $[_____] $[_____] [_____]   [__]%
Q3         $[_____] $[_____] [_____]   [__]%
Q4         $[_____] $[_____] [_____]   [__]%

Año        $[_____] $[_____] [_____]   [__]%

Supuestos:
- MRR growth: [__]%/mes
- Conversion: [__]%
- Retention: [__]%/mes
- ARPU: $[_____]
```

---

### **Template 3: Proyección para Inversores**

```
┌─────────────────────────────────────────────────┐
│  PROYECCIÓN FINANCIERA - [AÑO]                  │
│  Para: [Inversor/Board]                         │
└─────────────────────────────────────────────────┘

RESUMEN EJECUTIVO
─────────────────────────────────────────────────
ARR Actual:        $[_____]
ARR Proyectado:    $[_____]
Growth Rate:       [__]%/mes
NRR:               [__]%
LTV/CAC:           [__]:1

PROYECCIÓN MENSUAL
─────────────────────────────────────────────────
[Gráfico de MRR trend]

PROYECCIÓN TRIMESTRAL
─────────────────────────────────────────────────
Q1: $[_____] ARR
Q2: $[_____] ARR
Q3: $[_____] ARR
Q4: $[_____] ARR

SUPUESTOS CLAVE
─────────────────────────────────────────────────
1. [Supuesto 1]
2. [Supuesto 2]
3. [Supuesto 3]

RIESGOS
─────────────────────────────────────────────────
1. [Riesgo 1] - Mitigación: [Acción]
2. [Riesgo 2] - Mitigación: [Acción]
```

---

## 📊 Métricas de Forecasting

### **Precisión del Forecasting**

**Cómo Medir:**
```
Forecast Accuracy = 1 - (|Actual - Forecast| / Actual)

Objetivo: >80% accuracy
Excelente: >90% accuracy
```

**Mejores Prácticas:**
- Revisar y actualizar mensualmente
- Comparar actual vs forecast
- Ajustar supuestos basado en datos
- Documentar cambios

---

### **Sensibilidad del Forecasting**

**Análisis de Sensibilidad:**
- ¿Qué pasa si conversion rate cambia ±10%?
- ¿Qué pasa si churn rate cambia ±10%?
- ¿Qué pasa si CAC cambia ±20%?
- ¿Qué pasa si growth rate cambia ±10%?

**Útil para:**
- Identificar métricas críticas
- Planificar escenarios
- Comunicar riesgos

---

## 🎯 Mejores Prácticas

### **1. Basado en Datos Reales**
- Usar datos históricos
- Analizar tendencias
- Validar supuestos

### **2. Supuestos Claros**
- Documentar todos los supuestos
- Justificar proyecciones
- Revisar regularmente

### **3. Múltiples Escenarios**
- Base case
- Optimista
- Pesimista

### **4. Revisión Regular**
- Actualizar mensualmente
- Comparar actual vs forecast
- Ajustar basado en datos

### **5. Comunicación Clara**
- Gráficos claros
- Supuestos visibles
- Riesgos identificados
- Proyecciones realistas

---

## ✅ Checklist de Forecasting

```
┌─────────────────────────────────────────────────┐
│  CHECKLIST: FORECASTING PLG                     │
└─────────────────────────────────────────────────┘

PREPARACIÓN
─────────────────────────────────────────────────
[ ] Datos históricos recopilados
[ ] Tendencias analizadas
[ ] Supuestos documentados
[ ] Modelo elegido (bottom-up/top-down/híbrido)

PROYECCIÓN
─────────────────────────────────────────────────
[ ] Adquisición proyectada
[ ] Activación proyectada
[ ] Conversión proyectada
[ ] Retención proyectada
[ ] Revenue proyectado
[ ] Costos proyectados

ESCENARIOS
─────────────────────────────────────────────────
[ ] Escenario base creado
[ ] Escenario optimista creado
[ ] Escenario pesimista creado
[ ] Supuestos por escenario documentados

VALIDACIÓN
─────────────────────────────────────────────────
[ ] Proyecciones validadas
[ ] Consistencia verificada
[ ] Supuestos revisados
[ ] Riesgos identificados

COMUNICACIÓN
─────────────────────────────────────────────────
[ ] Presentación preparada
[ ] Gráficos claros
[ ] Supuestos visibles
[ ] Riesgos comunicados
```

---

*Última actualización: 2024*


