---
title: "Calculadora Roi"
category: "02_finance"
tags: ["business", "finance"]
created: "2025-10-29"
path: "02_finance/Roi_calculations/calculadora_roi.md"
---

# Calculadora ROI - Justificar Inversión

Fórmulas rápidas para calcular ROI y presentar casos de negocio.

---

## FÓRMULA BÁSICA DE ROI

```
ROI = ((Ingreso - Inversión) / Inversión) × 100
```

---

## CÁLCULO ESPECÍFICO: Curso IA (Webinar)

### Variables de entrada
- **Costo del curso:** $X (precio de venta)
- **Tiempo ahorrado:** 10 horas/semana
- **Valor hora del cliente:** $Y/hora
- **Costos operativos:** $Z (marketing, plataforma, etc.)

### Cálculo mensual
```
Ahorro mensual = 10 horas/sem × 4 semanas × $Y/hora
                = 40 horas × $Y
                = $A

ROI mensual = (($A - $Z) / $Z) × 100
```

### Ejemplo práctico
```
Curso: $500
Tiempo ahorrado: 10h/sem
Valor hora: $50/hora

Ahorro mensual = 40h × $50 = $2,000
ROI = (($2,000 - $500) / $500) × 100 = 300%
```

**Payback period:** 0.25 meses (1 semana)

---

## CÁLCULO ESPECÍFICO: SaaS IA Marketing

### Variables de entrada
- **Precio mensual:** $X/mes
- **Tiempo ahorrado:** 2 horas por campaña
- **Campañas por semana:** 3
- **Valor hora equipo:** $Y/hora
- **Costo de no usar:** Contratar persona ($Z/año)

### Cálculo anual
```
Ahorro anual = 2h/campaña × 3 campañas/sem × 52 semanas × $Y/hora
             = 312 horas × $Y
             = $A

Costo SaaS anual = $X/mes × 12 = $B
Costo alternativa = $Z/año (contratar persona)

ROI vs manual = (($A - $B) / $B) × 100
ROI vs contratar = (($Z - $B) / $B) × 100
```

### Ejemplo práctico
```
SaaS: $99/mes = $1,188/año
Tiempo ahorrado: 2h/campaña × 3/sem = 6h/sem
Valor hora: $40/hora

Ahorro anual = 312h × $40 = $12,480
ROI = (($12,480 - $1,188) / $1,188) × 100 = 950%

vs contratar persona ($60K/año):
ROI = (($60,000 - $1,188) / $1,188) × 100 = 4,950%
```

---

## CÁLCULO ESPECÍFICO: IA Bulk (Documentos)

### Variables de entrada
- **Precio:** $X/mes
- **Documentos por mes:** N documentos
- **Tiempo manual por documento:** Y horas
- **Valor hora:** $Z/hora

### Cálculo mensual
```
Ahorro mensual = N documentos × (Y horas - 0.05 horas) × $Z/hora
                = A horas ahorradas × $Z

ROI = (($A - $X) / $X) × 100
```

### Ejemplo práctico
```
IA Bulk: $79/mes
Documentos/mes: 20
Tiempo manual: 4 horas/documento
Con IA: 5 minutos/documento = 0.08 horas
Valor hora: $50/hora

Ahorro = 20 × (4h - 0.08h) × $50 = 78.4h × $50 = $3,920
ROI = (($3,920 - $79) / $79) × 100 = 4,859%
```

---

## CALCULADORA RÁPIDA (Google Sheets)

### Plantilla de fórmula
```
Columna A: Valor hora del cliente
Columna B: Horas ahorradas/semana
Columna C: Precio producto
Columna D: Ahorro mensual = (B2*4)*A2
Columna E: ROI = ((D2-C2)/C2)*100
Columna F: Payback meses = C2/D2
```

### Ejemplo llenado
| Valor/hora | H ahorradas/sem | Precio | Ahorro/mes | ROI | Payback |
|------------|------------------|--------|------------|-----|---------|
| $50 | 10 | $500 | $2,000 | 300% | 0.25 |

---

## CASOS DE NEGOCIO LISTOS

### Para presentar a cliente

**Casos de uso comunes:**

#### Ecommerce (200 SKUs)
- **Situación:** Crear contenido para cada producto toma 2h
- **Con IA:** 5 minutos por producto
- **Ahorro:** 390 horas/mes
- **Valor:** $19,500/mes (asumiendo $50/hora)
- **ROI curso ($500):** 3,800% mensual
- **ROI SaaS ($99/mes):** 19,600% mensual

#### Agencia (10 clientes)
- **Situación:** Propuesta comercial toma 4h cada una
- **Con IA Bulk:** 2 minutos cada una
- **Ahorro:** 38 horas/mes
- **Valor:** $1,900/mes (asumiendo $50/hora)
- **ROI IA Bulk ($79/mes):** 2,306% mensual

#### B2B SaaS (equipo 5 personas)
- **Situación:** 3 campañas/semana toma 12h cada una
- **Con SaaS IA:** 7 minutos cada una
- **Ahorro:** 35 horas/semana = 140h/mes
- **Valor:** $7,000/mes
- **ROI SaaS ($99/mes):** 6,970% mensual

---

## PRESENTACIÓN PARA CLIENTE

### Template de email/presentación
```
Título: "ROI de [PRODUCTO] para [TU EMPRESA]"

Situación actual:
- [Problema específico que enfrentan]
- Tiempo invertido: [X horas/semana/mes]
- Costo oculto: $[valor calculado]

Con [PRODUCTO]:
- Tiempo ahorrado: [Y horas]
- Valor del tiempo: $[ahorro mensual]
- Inversión: $[precio producto]
- ROI: [X]% mensual
- Payback: [Y] semanas

Ejemplo específico para tu caso:
[Insertar cálculo personalizado]
```

---

## JUSTIFICACIÓN POR ROI

### Si ROI <100%
**Objetivo:** Ahorro de tiempo libera capacidad para más clientes/ventas

### Si ROI 100-500%
**Objetivo:** Inversión se paga en 1-3 meses, ahorro claro

### Si ROI >500%
**Objetivo:** Ahorro masivo, decisión obvia

**Regla:** Si ROI >200%, decisión debe ser fácil.

---

## PUNTOS DE DECISIÓN

### ¿Vale la pena el curso/webinar?
**Si:** Tiempo ahorrado × valor hora > precio curso en <3 meses

### ¿Vale la pena el SaaS?
**Si:** Costo mensual < 20% del ahorro mensual generado

### ¿Vale la pena IA Bulk?
**Si:** Precio mensual < valor de 1 documento generado

---

**Usa estas fórmulas para justificar inversión y cerrar más ventas.**

