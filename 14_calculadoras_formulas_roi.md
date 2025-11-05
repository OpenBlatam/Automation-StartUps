---
title: "14 Calculadoras Formulas Roi"
category: "14_calculadoras_formulas_roi.md"
tags: []
created: "2025-10-29"
path: "14_calculadoras_formulas_roi.md"
---

# 💰 Calculadoras y Fórmulas de ROI

## 📑 ÍNDICE

- [🎓 Para Curso IA + Webinars](#-para-curso-ia--webinars)
- [🎯 Para SaaS IA Marketing](#-para-saas-ia-marketing)
- [📄 Para IA Bulk Documentos](#-para-ia-bulk-documentos)
- [📊 Calculadora Universal](#-calculadora-universal)
- [🔢 Fórmulas Avanzadas](#-fórmulas-avanzadas)

---

## 🎓 PARA CURSO IA + WEBINARS

### Calculadora de ROI - Template

```
╔══════════════════════════════════════════════════════════════╗
║          CALCULADORA DE ROI - CURSO IA + WEBINARS          ║
║                    Para [EMPRESA]                           ║
╚══════════════════════════════════════════════════════════════╝

DATOS DE ENTRADA
─────────────────────────────────────────────────────────────
1. Webinars/mes:                    [X]
2. Horas edición manual/webinar:    [Y]
3. Costo hora equipo:               $[Z]/hora
4. Alumnos actuales:                [A]
5. Completion rate actual:          [B]%
6. Completion rate objetivo:        [C]%
7. Valor por alumno completado:      $[D]

CÁLCULOS
─────────────────────────────────────────────────────────────

AHORRO DE TIEMPO:
─────────────────────────────────────────────────────────────
Total horas/mes (manual):           [X × Y] horas
Costo mensual actual:                $[X × Y × Z]
Horas con [PRODUCTO]:                [X × Y × 0.2] horas (80% reducción)
Costo mensual con [PRODUCTO]:        $[X × Y × 0.2 × Z]
─────────────────────────────────────────────────────────────
AHORRO MENSUAL TIEMPO:               $[X × Y × Z × 0.8]

AUMENTO DE INGRESOS:
─────────────────────────────────────────────────────────────
Alumnos completados actuales:        [A × B%] = [E]
Alumnos completados objetivo:        [A × C%] = [F]
Alumnos adicionales completados:     [F - E] = [G]
─────────────────────────────────────────────────────────────
INGRESOS ADICIONALES/MES:            $[G × D]

ROI TOTAL
─────────────────────────────────────────────────────────────
Ahorro mensual:                      $[AHORRO]
Ingresos adicionales/mes:           $[INGRESOS]
─────────────────────────────────────────────────────────────
ROI TOTAL/MES:                       $[AHORRO + INGRESOS]
ROI ANUAL:                           $[(AHORRO + INGRESOS) × 12]

COSTO [PRODUCTO]
─────────────────────────────────────────────────────────────
Costo mensual [PRODUCTO]:            $[COSTO]/mes
Setup (one-time):                    $[SETUP]

PAYBACK PERIOD
─────────────────────────────────────────────────────────────
Inversión total:                     $[COSTO × 12 + SETUP]
ROI anual:                           $[ROI_ANUAL]
─────────────────────────────────────────────────────────────
Payback:                             [INVERSION/ROI_MENSUAL] meses

ROI % ANUAL
─────────────────────────────────────────────────────────────
[(ROI_ANUAL - INVERSION_ANUAL) / INVERSION_ANUAL] × 100 = [X]%
```

---

### Fórmulas Detalladas

**Ahorro de Tiempo:**
```python
# Variables
webinars_mes = X
horas_por_webinar = Y
costo_hora = Z
reduccion_tiempo = 0.8  # 80% reducción

# Cálculo
horas_totales_actual = webinars_mes * horas_por_webinar
costo_mensual_actual = horas_totales_actual * costo_hora

horas_totales_nuevo = horas_totales_actual * (1 - reduccion_tiempo)
costo_mensual_nuevo = horas_totales_nuevo * costo_hora

ahorro_mensual = costo_mensual_actual - costo_mensual_nuevo
```

**Aumento de Ingresos:**
```python
# Variables
alumnos_total = A
completion_actual = B  # porcentaje
completion_objetivo = C  # porcentaje
valor_por_completado = D

# Cálculo
alumnos_completados_actual = alumnos_total * (completion_actual / 100)
alumnos_completados_objetivo = alumnos_total * (completion_objetivo / 100)

alumnos_adicionales = alumnos_completados_objetivo - alumnos_completados_actual
ingresos_adicionales_mes = alumnos_adicionales * valor_por_completado
```

---

## 🎯 PARA SAAS IA MARKETING

### Calculadora de ROI - Template

```
╔══════════════════════════════════════════════════════════════╗
║         CALCULADORA DE ROI - SAAS IA MARKETING               ║
║                    Para [EMPRESA]                            ║
╚══════════════════════════════════════════════════════════════╝

DATOS DE ENTRADA
─────────────────────────────────────────────────────────────
1. Campañas activas/mes:             [X]
2. Horas creando variaciones:        [Y]/semana
3. Costo hora equipo marketing:      $[Z]/hora
4. Presupuesto mensual ads:          $[A]
5. ROAS actual:                      [B]x
6. ROAS objetivo:                   [C]x

CÁLCULOS
─────────────────────────────────────────────────────────────

AHORRO DE TIEMPO:
─────────────────────────────────────────────────────────────
Horas/mes creando variaciones:       [Y × 4] horas
Costo mensual actual:                 $[Y × 4 × Z]
Horas con [PRODUCTO]:                 [Y × 4 × 0.15] horas (85% reducción)
Costo mensual con [PRODUCTO]:         $[Y × 4 × 0.15 × Z]
─────────────────────────────────────────────────────────────
AHORRO MENSUAL TIEMPO:                $[Y × 4 × Z × 0.85]

AUMENTO DE ROAS:
─────────────────────────────────────────────────────────────
Ingresos actuales:                    $[A × B]
Ingresos objetivo:                    $[A × C]
─────────────────────────────────────────────────────────────
INGRESOS ADICIONALES/MES:             $[(A × C) - (A × B)]

REDUCCIÓN DE CAC:
─────────────────────────────────────────────────────────────
CAC actual:                           $[CAC_ACTUAL]
CAC objetivo (con mejor creatividades): $[CAC_OBJETIVO]
Leads/mes:                            [LEADS]
─────────────────────────────────────────────────────────────
AHORRO CAC/MES:                       $[(CAC_ACTUAL - CAC_OBJETIVO) × LEADS]

ROI TOTAL
─────────────────────────────────────────────────────────────
Ahorro tiempo/mes:                    $[AHORRO_TIEMPO]
Ingresos adicionales/mes:             $[INGRESOS_ADICIONALES]
Ahorro CAC/mes:                       $[AHORRO_CAC]
─────────────────────────────────────────────────────────────
ROI TOTAL/MES:                        $[SUM]
ROI ANUAL:                            $[SUM × 12]

COSTO [PRODUCTO]
─────────────────────────────────────────────────────────────
Costo mensual [PRODUCTO]:             $[COSTO]/mes
Setup (one-time):                     $[SETUP]

PAYBACK PERIOD
─────────────────────────────────────────────────────────────
Payback:                              [X] meses
```

---

### Fórmulas Detalladas

**Ahorro de Tiempo:**
```python
# Variables
campañas_mes = X
horas_semana = Y
costo_hora = Z
reduccion_tiempo = 0.85  # 85% reducción

# Cálculo
horas_mes_actual = horas_semana * 4
costo_mensual_actual = horas_mes_actual * costo_hora

horas_mes_nuevo = horas_mes_actual * (1 - reduccion_tiempo)
costo_mensual_nuevo = horas_mes_nuevo * costo_hora

ahorro_mensual = costo_mensual_actual - costo_mensual_nuevo
```

**Aumento de Ingresos por ROAS:**
```python
# Variables
presupuesto_mes = A
roas_actual = B
roas_objetivo = C

# Cálculo
ingresos_actuales = presupuesto_mes * roas_actual
ingresos_objetivo = presupuesto_mes * roas_objetivo

ingresos_adicionales = ingresos_objetivo - ingresos_actuales
```

**Reducción de CAC:**
```python
# Variables
cac_actual = X
cac_objetivo = Y
leads_mes = Z

# Cálculo
ahorro_por_lead = cac_actual - cac_objetivo
ahorro_cac_mes = ahorro_por_lead * leads_mes
```

---

## 📄 PARA IA BULK DOCUMENTOS

### Calculadora de ROI - Template

```
╔══════════════════════════════════════════════════════════════╗
║         CALCULADORA DE ROI - IA BULK DOCUMENTOS               ║
║                    Para [EMPRESA]                            ║
╚══════════════════════════════════════════════════════════════╝

DATOS DE ENTRADA
─────────────────────────────────────────────────────────────
1. Documentos/semana:                 [X]
2. Horas/documento (actual):          [Y]
3. Horas/documento (con [PRODUCTO]):  [Z]
4. Costo hora equipo:                 $[A]/hora
5. Documentos/mes posibles:           [B]
6. Win rate propuestas:               [C]%
7. Ingresos por cierre:               $[D]

CÁLCULOS
─────────────────────────────────────────────────────────────

AHORRO DE TIEMPO:
─────────────────────────────────────────────────────────────
Ahorro por documento:                 [Y - Z] horas
Ahorro semanal:                       [X × (Y - Z)] horas
Ahorro mensual:                       [X × (Y - Z) × 4] horas
─────────────────────────────────────────────────────────────
AHORRO MENSUAL TIEMPO:                $[X × (Y - Z) × 4 × A]

AUMENTO DE THROUGHPUT:
─────────────────────────────────────────────────────────────
Documentos/mes actuales:              [X × 4] = [E]
Documentos/mes posibles:              [B]
Documentos adicionales/mes:           [B - E] = [F]
─────────────────────────────────────────────────────────────
OPORTUNIDADES ADICIONALES:            [F]

AUMENTO DE INGRESOS:
─────────────────────────────────────────────────────────────
Cierres adicionales/mes:              [F × C%] = [G]
Ingresos adicionales/mes:              $[G × D]

ROI TOTAL
─────────────────────────────────────────────────────────────
Ahorro mensual:                       $[AHORRO]
Ingresos adicionales/mes:             $[INGRESOS]
─────────────────────────────────────────────────────────────
ROI TOTAL/MES:                        $[AHORRO + INGRESOS]
ROI ANUAL:                            $[(AHORRO + INGRESOS) × 12]

COSTO [PRODUCTO]
─────────────────────────────────────────────────────────────
Costo mensual [PRODUCTO]:             $[COSTO]/mes
Setup (one-time):                     $[SETUP]

PAYBACK PERIOD
─────────────────────────────────────────────────────────────
Payback:                              [X] meses
```

---

### Fórmulas Detalladas

**Ahorro de Tiempo:**
```python
# Variables
documentos_semana = X
horas_doc_actual = Y
horas_doc_nuevo = Z
costo_hora = A

# Cálculo
ahorro_por_doc = horas_doc_actual - horas_doc_nuevo
ahorro_semanal = documentos_semana * ahorro_por_doc
ahorro_mensual_horas = ahorro_semanal * 4
ahorro_mensual_dinero = ahorro_mensual_horas * costo_hora
```

**Aumento de Ingresos:**
```python
# Variables
docs_mes_actual = documentos_semana * 4
docs_mes_posibles = B
win_rate = C  # porcentaje
ingresos_por_cierre = D

# Cálculo
docs_adicionales = docs_mes_posibles - docs_mes_actual
cierres_adicionales = docs_adicionales * (win_rate / 100)
ingresos_adicionales = cierres_adicionales * ingresos_por_cierre
```

---

## 📊 CALCULADORA UNIVERSAL

### Template Genérico (Para Cualquier Caso)

```
╔══════════════════════════════════════════════════════════════╗
║                    CALCULADORA DE ROI                        ║
║                    Para [EMPRESA]                            ║
╚══════════════════════════════════════════════════════════════╝

CATEGORÍA 1: AHORRO DE TIEMPO
─────────────────────────────────────────────────────────────
Tarea:                                [DESCRIPCIÓN]
Frecuencia:                           [X veces/semana o /mes]
Tiempo actual/tarea:                  [Y] horas
Tiempo con [PRODUCTO]/tarea:          [Z] horas
Costo hora equipo:                     $[A]/hora

Cálculo:
─────────────────────────────────────────────────────────────
Ahorro/tarea:                         [Y - Z] horas
Total tareas/mes:                     [X × 4 o X]
Total horas ahorradas/mes:            [X × (Y - Z)]
AHORRO MENSUAL:                       $[X × (Y - Z) × A]

CATEGORÍA 2: AUMENTO DE INGRESOS
─────────────────────────────────────────────────────────────
Métrica base:                          [DESCRIPCIÓN]
Valor actual:                          [X]
Valor objetivo:                        [Y]
Valor unitario:                        $[Z]

Cálculo:
─────────────────────────────────────────────────────────────
Mejora:                                [Y - X] unidades
INGRESOS ADICIONALES/MES:             $[(Y - X) × Z]

CATEGORÍA 3: REDUCCIÓN DE COSTOS
─────────────────────────────────────────────────────────────
Costo actual/mes:                      $[X]
Costo con [PRODUCTO]/mes:              $[Y]

Cálculo:
─────────────────────────────────────────────────────────────
AHORRO MENSUAL:                       $[X - Y]

ROI TOTAL
─────────────────────────────────────────────────────────────
Ahorro tiempo:                        $[A]
Ingresos adicionales:                 $[B]
Reducción costos:                     $[C]
─────────────────────────────────────────────────────────────
ROI TOTAL/MES:                        $[A + B + C]
ROI ANUAL:                            $[(A + B + C) × 12]

INVERSIÓN
─────────────────────────────────────────────────────────────
Costo mensual [PRODUCTO]:             $[COSTO]/mes
Setup (one-time):                     $[SETUP]
─────────────────────────────────────────────────────────────
Inversión primer año:                 $[(COSTO × 12) + SETUP]

MÉTRICAS DE RETORNO
─────────────────────────────────────────────────────────────
Payback period:                       [INVERSION/ROI_MENSUAL] meses
ROI % anual:                          [((ROI_ANUAL - INVERSION)/INVERSION) × 100]%
Break-even:                           Mes [X]
```

---

## 🔢 FÓRMULAS AVANZADAS

### Payback Period

```python
def calculate_payback(inversion_total, roi_mensual):
    """
    Calcula payback period en meses
    """
    if roi_mensual <= 0:
        return "No hay ROI positivo"
    
    payback_meses = inversion_total / roi_mensual
    return payback_meses

# Ejemplo
inversion = 12000  # $1,000/mes × 12 meses
roi_mensual = 2000  # $2,000/mes
payback = calculate_payback(inversion, roi_mensual)
# Resultado: 6 meses
```

---

### ROI Percentage

```python
def calculate_roi_percentage(inversion, retorno):
    """
    Calcula ROI % = ((Retorno - Inversión) / Inversión) × 100
    """
    roi = ((retorno - inversion) / inversion) * 100
    return roi

# Ejemplo
inversion_anual = 12000
retorno_anual = 24000
roi_pct = calculate_roi_percentage(inversion_anual, retorno_anual)
# Resultado: 100% ROI anual
```

---

### Net Present Value (NPV) - Avanzado

```python
def calculate_npv(inversion_inicial, flujos_mensuales, tasa_descuento_mensual):
    """
    Calcula NPV para evaluación de inversión
    tasa_descuento_mensual: ej. 0.01 = 1% mensual
    """
    npv = -inversion_inicial
    
    for mes, flujo in enumerate(flujos_mensuales, 1):
        npv += flujo / ((1 + tasa_descuento_mensual) ** mes)
    
    return npv

# Ejemplo
inversion = 1000
flujos = [2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000, 2000]  # 12 meses
tasa = 0.01  # 1% mensual
npv = calculate_npv(inversion, flujos, tasa)
# Si NPV > 0, inversión es buena
```

---

### Internal Rate of Return (IRR) - Avanzado

```python
def calculate_irr(inversion_inicial, flujos_mensuales):
    """
    Calcula IRR (aprox) mediante iteración
    """
    def npv_at_rate(rate):
        npv = -inversion_inicial
        for mes, flujo in enumerate(flujos_mensuales, 1):
            npv += flujo / ((1 + rate) ** mes)
        return npv
    
    # Buscar rate donde NPV = 0
    rate = 0.01  # Empezar con 1%
    step = 0.001
    
    for _ in range(1000):
        npv = npv_at_rate(rate)
        if abs(npv) < 0.01:  # Aproximación
            return rate * 12  # Convertir a anual
        if npv > 0:
            rate += step
        else:
            rate -= step
            step *= 0.5
    
    return rate * 12

# Ejemplo (uso básico - en producción usar librería financiera)
```

---

## 📱 CALCULADORA RÁPIDA (Para DMs/Emails)

### Template Corto

```
ROI Rápido para [EMPRESA]:

Ahorro: [X horas/mes] × $[Y/hora] = $[Z]/mes
Ingresos: [A unidades] × $[B/unidad] = $[C]/mes
───────────────────────────────────────────────
ROI: $[Z + C]/mes = $[ROI_ANUAL]/año

Costo: $[COSTO]/mes
Payback: [X] meses
```

---

## ✅ CHECKLIST DE CÁLCULO

**Antes de usar calculadora con cliente:**

- [ ] Datos de entrada verificados y realistas
- [ ] Assumptions claras documentadas
- [ ] Fuentes de datos confiables (si métricas públicas)
- [ ] Comparativa con situación actual
- [ ] Escenarios (conservador, realista, óptimo)
- [ ] Payback calculado
- [ ] ROI % calculado
- [ ] Visualización clara (tabla, gráfico si posible)

---

**FIN DEL DOCUMENTO**




