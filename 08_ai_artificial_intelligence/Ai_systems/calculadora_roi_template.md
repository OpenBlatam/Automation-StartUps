# CALCULADORA DE ROI PARA PROYECTOS DE CONSULTORÍA
## Herramienta para Calcular Retorno de Inversión

---

## FÓRMULAS PRINCIPALES

### 1. ROI Simple

```
ROI = (Beneficios - Inversión) / Inversión × 100
```

**Ejemplo:**
- Inversión: $100,000
- Beneficios Anuales: $150,000
- ROI = ($150,000 - $100,000) / $100,000 × 100 = 50%

---

### 2. Período de Recuperación (Payback)

```
Payback = Inversión / Beneficios Mensuales
```

**Ejemplo:**
- Inversión: $100,000
- Beneficios Mensuales: $12,500
- Payback = $100,000 / $12,500 = 8 meses

---

### 3. Valor Presente Neto (VPN)

```
VPN = Σ (Beneficios / (1 + tasa)^año) - Inversión
```

**Donde:**
- tasa = Tasa de descuento (ej: 10% = 0.10)
- año = Año del beneficio (1, 2, 3...)

**Ejemplo (3 años, tasa 10%):**
- Inversión: $100,000
- Beneficios Año 1: $50,000
- Beneficios Año 2: $60,000
- Beneficios Año 3: $70,000

VPN = ($50,000/1.1 + $60,000/1.1² + $70,000/1.1³) - $100,000
VPN = ($45,455 + $49,587 + $52,592) - $100,000 = $47,634

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

