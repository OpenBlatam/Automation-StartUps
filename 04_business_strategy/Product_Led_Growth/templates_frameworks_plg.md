# 📐 Templates y Frameworks para Product-Led Growth

> **💡 Guía Práctica**: Templates, frameworks y herramientas reutilizables para implementar y optimizar estrategias PLG.

---

## 📋 Tabla de Contenidos

1. [🎯 Frameworks de Decisión](#-frameworks-de-decisión)
2. [📊 Templates de Métricas](#-templates-de-métricas)
3. [✍️ Templates de Copy](#-templates-de-copy)
4. [🎨 Templates de UX/UI](#-templates-de-uxui)
5. [📈 Calculadoras de Métricas](#-calculadoras-de-métricas)
6. [✅ Checklists de Implementación](#-checklists-de-implementación)
7. [📝 Templates de Documentación](#-templates-de-documentación)

---

## 🎯 Frameworks de Decisión

### **Framework 1: ¿PLG es Adecuado para Mi Producto?**

```
┌─────────────────────────────────────────────────┐
│  EVALUACIÓN DE ADECUACIÓN PLG                   │
└─────────────────────────────────────────────────┘

Pregunta                          Puntuación (1-5)
─────────────────────────────────────────────────
¿Es producto digital/SaaS?        [ ] 5  [ ] 3  [ ] 1
¿Time-to-value <2 horas?          [ ] 5  [ ] 3  [ ] 1
¿Mercado grande (>100K)?         [ ] 5  [ ] 3  [ ] 1
¿Puede funcionar freemium/trial? [ ] 5  [ ] 3  [ ] 1
¿Viralidad es posible?           [ ] 5  [ ] 3  [ ] 1
¿Precio <$500/mes?               [ ] 5  [ ] 3  [ ] 1
¿No requiere ventas complejas?    [ ] 5  [ ] 3  [ ] 1

TOTAL: _____ / 35

Interpretación:
- 28-35: Excelente candidato para PLG
- 21-27: Buen candidato, considerar híbrido
- 14-20: Candidato marginal, evaluar cuidadosamente
- <14: PLG probablemente no es adecuado
```

### **Framework 2: Elegir Modelo (Freemium vs Trial)**

```
┌─────────────────────────────────────────────────┐
│  DECISIÓN: FREEMIUM vs FREE TRIAL               │
└─────────────────────────────────────────────────┘

Factor                          Freemium  Trial
─────────────────────────────────────────────────
Producto simple de entender      ✅        ⚠️
Mercado muy grande (>1M)         ✅        ⚠️
Network effects                  ✅        ❌
Curva aprendizaje alta           ❌        ✅
Recursos limitados               ⚠️        ✅
Alta conversión necesaria        ⚠️        ✅
Muchos sign-ups necesarios       ✅        ⚠️

Recomendación:
- 4+ checks en Freemium → Usar Freemium
- 4+ checks en Trial → Usar Free Trial
- Empate → Considerar modelo mixto
```

### **Framework 3: Definir "Aha Moment"**

```
┌─────────────────────────────────────────────────┐
│  DEFINICIÓN DE AHA MOMENT                        │
└─────────────────────────────────────────────────┘

Paso 1: Identificar Acciones de Valor
─────────────────────────────────────
¿Qué acciones indican que usuario experimentó valor?

1. [Acción específica]
2. [Acción específica]
3. [Acción específica]

Paso 2: Priorizar por Impacto
──────────────────────────────
Acción                    Impacto  Frecuencia  Prioridad
────────────────────────────────────────────────────────
[Acción 1]                [1-5]    [1-5]      [Alta/Media/Baja]
[Acción 2]                [1-5]    [1-5]      [Alta/Media/Baja]
[Acción 3]                [1-5]    [1-5]      [Alta/Media/Baja]

Paso 3: Definir Milestone de Activación
───────────────────────────────────────
Milestone = [Acción prioritaria] + [Criterio cuantitativo]

Ejemplo: "Crear 3 proyectos y compartir 1 con colaborador"

Paso 4: Validar
───────────────
- ¿Es alcanzable en <2 horas? [ ] Sí [ ] No
- ¿Indica valor real?          [ ] Sí [ ] No
- ¿Correlaciona con retención? [ ] Sí [ ] No
```

### **Framework 4: Scoring de PQL (Product-Qualified Lead)**

```
┌─────────────────────────────────────────────────┐
│  SCORING DE PRODUCT-QUALIFIED LEADS            │
└─────────────────────────────────────────────────┘

Señal                              Peso  Score  Total
────────────────────────────────────────────────────
Days Active (>30 días)            30%   [0-100]  ___
Feature Usage (premium features)  25%   [0-100]  ___
Team Size (>5 usuarios)           20%   [0-100]  ___
Engagement (uso consistente)       15%   [0-100]  ___
Signals (expresa interés)         10%   [0-100]  ___
────────────────────────────────────────────────────
TOTAL SCORE:                       ___ / 100

Thresholds:
- >70: PQL Alto - Handoff inmediato a sales
- 50-70: PQL Medio - Nurturing activo
- 30-50: PQL Bajo - Seguimiento suave
- <30: No es PQL - Continuar en self-service
```

---

## 📊 Templates de Métricas

### **Template 1: Dashboard Semanal PLG**

```
┌─────────────────────────────────────────────────┐
│  DASHBOARD SEMANAL - PRODUCT-LED GROWTH        │
│  Semana: [__/__/____]                           │
└─────────────────────────────────────────────────┘

ADQUISICIÓN
─────────────────────────────────────────────────
Visitantes únicos:           [_____]
Sign-ups:                    [_____]  (___% sign-up rate)
Costo total marketing:       $[_____]
CAC promedio:                $[_____]

ACTIVACIÓN
─────────────────────────────────────────────────
Usuarios activados:          [_____]  (___% activation rate)
Time-to-value promedio:      [_____] horas
PQLs identificados:         [_____]  (___% PQL rate)

CONVERSIÓN
─────────────────────────────────────────────────
Conversiones a paid:         [_____]  (___% conversion rate)
Nuevo MRR:                   $[_____]
Upgrades:                    [_____]  (___% upgrade rate)
Expansion MRR:               $[_____]

RETENCIÓN
─────────────────────────────────────────────────
Day 1 retention:             [_____]%
Day 7 retention:             [_____]%
Day 30 retention:            [_____]%
Churn rate:                  [_____]%

CRECIMIENTO
─────────────────────────────────────────────────
MRR total:                   $[_____]
MRR growth rate:             [_____]%
NRR:                         [_____]%
LTV/CAC ratio:              [_____]:1

VIRALIDAD
─────────────────────────────────────────────────
Invitaciones enviadas:       [_____]
Conversiones de invitaciones:[_____]  (___% conversion)
K-factor:                    [_____]
Organic growth %:            [_____]%

NOTAS Y ACCIONES
─────────────────────────────────────────────────
[Espacio para notas y acciones]
```

### **Template 2: Cohort Analysis**

```
┌─────────────────────────────────────────────────┐
│  COHORT ANALYSIS - [MES]                        │
└─────────────────────────────────────────────────┘

Cohort: [Mes de sign-up]

Mes 0:  [___] usuarios (100%)
Mes 1:  [___] usuarios (___%)
Mes 2:  [___] usuarios (___%)
Mes 3:  [___] usuarios (___%)
Mes 6:  [___] usuarios (___%)
Mes 12: [___] usuarios (___%)

Insights:
─────────────────────────────────────────────────
[Espacio para insights y observaciones]

Acciones:
─────────────────────────────────────────────────
[Espacio para acciones basadas en insights]
```

### **Template 3: Funnel de Conversión**

```
┌─────────────────────────────────────────────────┐
│  FUNNEL DE CONVERSIÓN - [PERÍODO]               │
└─────────────────────────────────────────────────┘

Etapa                    Usuarios    %    Drop-off
────────────────────────────────────────────────────
Visitantes                [_____]   100%   -
Sign-ups                  [_____]    __%   __%
Activados                 [_____]    __%   __%
PQLs                      [_____]    __%   __%
Conversiones              [_____]    __%   __%
────────────────────────────────────────────────────

Optimización Prioritaria:
─────────────────────────────────────────────────
Etapa con mayor drop-off: [Etapa]
Tasa actual:              [__]%
Objetivo:                 [__]%
Estrategia:               [Descripción]
```

---

## ✍️ Templates de Copy

### **Template 1: Mensaje de Invitación**

```
┌─────────────────────────────────────────────────┐
│  TEMPLATE: MENSAJE DE INVITACIÓN                │
└─────────────────────────────────────────────────┘

VARIACIÓN A (Personal, Amigable)
─────────────────────────────────────────────────
Asunto: [Nombre] te invitó a [Producto]

Hola [Nombre del Invitado],

[Nombre del Invitador] te invitó a unirte a [Producto], 
una herramienta que [beneficio principal].

[Invitador] está usando [Producto] para [caso de uso 
específico] y cree que te sería útil también.

[Incentivo para invitado]: [Descripción clara]

Únete gratis aquí: [Link]

Saludos,
El equipo de [Producto]

─────────────────────────────────────────────────

VARIACIÓN B (Profesional, B2B)
─────────────────────────────────────────────────
Asunto: Colaboración en [Producto] - Invitación de [Nombre]

Hola [Nombre],

[Nombre del Invitador] de [Empresa] te invitó a 
colaborar en [Producto].

[Contexto específico del proyecto/equipo]

[Incentivo]: [Descripción]

Acepta invitación: [Link]

Si tienes preguntas, responde a este email.

Saludos,
[Producto] Team

─────────────────────────────────────────────────

ELEMENTOS CLAVE:
✅ Personalización (nombre, contexto)
✅ Valor claro
✅ Incentivo específico
✅ CTA claro
✅ Link de sign-up fácil
```

### **Template 2: Prompt de Conversión (Freemium)**

```
┌─────────────────────────────────────────────────┐
│  TEMPLATE: PROMPT DE CONVERSIÓN FREEMIUM        │
└─────────────────────────────────────────────────┘

VARIACIÓN A (Alcanzaste Límite)
─────────────────────────────────────────────────
Título: ¡Has alcanzado tu límite de [recurso]!

Mensaje:
Has usado [X] de [Y] [recurso]. Para continuar 
creciendo, considera upgrade a [Plan].

Beneficios de [Plan]:
• [Beneficio 1 específico]
• [Beneficio 2 específico]
• [Beneficio 3 específico]

Precio: $[X]/mes (o $[Y]/año - ahorra [Z]%)

[Botón: Upgrade Ahora]  [Botón: Más Información]

─────────────────────────────────────────────────

VARIACIÓN B (Feature Premium)
─────────────────────────────────────────────────
Título: Desbloquea [Feature Premium]

Mensaje:
Esta feature está disponible en [Plan]. Con [Plan] 
obtienes:

• [Feature premium] - [Beneficio]
• [Otra feature] - [Beneficio]
• [Otra feature] - [Beneficio]

Prueba gratis 14 días, sin tarjeta.

[Botón: Probar Gratis]  [Botón: Ver Planes]

─────────────────────────────────────────────────

ELEMENTOS CLAVE:
✅ Contexto claro (por qué aparece)
✅ Valor específico
✅ Beneficios concretos
✅ Precio visible
✅ CTA claro
✅ Opción de cerrar fácilmente
```

### **Template 3: Email de Recordatorio (Trial)**

```
┌─────────────────────────────────────────────────┐
│  TEMPLATE: EMAIL RECORDATORIO TRIAL             │
└─────────────────────────────────────────────────┘

DÍA 5 - CHECK-IN
─────────────────────────────────────────────────
Asunto: ¿Cómo va tu prueba de [Producto]?

Hola [Nombre],

Llevas 5 días probando [Producto]. ¿Cómo va?

Si necesitas ayuda para empezar, aquí tienes recursos:
• [Recurso 1]
• [Recurso 2]
• [Recurso 3]

¿Tienes preguntas? Responde a este email.

Saludos,
[Tu nombre]
[Producto] Team

─────────────────────────────────────────────────

DÍA 20 - MOSTRAR VALOR
─────────────────────────────────────────────────
Asunto: Features que te encantarán en [Producto]

Hola [Nombre],

Te quedan 10 días de prueba. ¿Has probado estas 
features?

• [Feature 1] - [Cómo ayuda]
• [Feature 2] - [Cómo ayuda]
• [Feature 3] - [Cómo ayuda]

[Link a tutorial o guía]

Saludos,
[Producto] Team

─────────────────────────────────────────────────

DÍA 29 - URGENCIA SUAVE
─────────────────────────────────────────────────
Asunto: Último día: No pierdas acceso a [Producto]

Hola [Nombre],

Tu prueba expira mañana. Para continuar usando 
[Producto] y mantener acceso a:

• [Lo que perderá 1]
• [Lo que perderá 2]
• [Lo que perderá 3]

Upgrade ahora y obtén [incentivo especial].

[Botón: Upgrade Ahora]

Saludos,
[Producto] Team
```

---

## 🎨 Templates de UX/UI

### **Template 1: Empty State con Onboarding**

```
┌─────────────────────────────────────────────────┐
│  TEMPLATE: EMPTY STATE EFECTIVO                  │
└─────────────────────────────────────────────────┘

ESTRUCTURA:
─────────────────────────────────────────────────
┌─────────────────────────────────────────┐
│                                         │
│         [Ilustración/Icono]             │
│                                         │
│    [Título: Bienvenido a [Producto]]    │
│                                         │
│  [Subtítulo: Descripción breve del      │
│   valor que obtendrás]                  │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  ☐ [Acción 1 - Primer paso]     │   │
│  │  ☐ [Acción 2 - Segundo paso]    │   │
│  │  ☐ [Acción 3 - Tercer paso]    │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Botón: Empezar]                       │
│                                         │
│  O explora:                             │
│  • [Template/Ejemplo 1]                 │
│  • [Template/Ejemplo 2]                 │
│  • [Template/Ejemplo 3]                 │
│                                         │
│  [Link: Ver tutorial]                  │
└─────────────────────────────────────────┘

ELEMENTOS CLAVE:
✅ Mensaje de bienvenida claro
✅ Checklist de primeros pasos
✅ Templates/ejemplos visibles
✅ CTA principal prominente
✅ Opciones alternativas
```

### **Template 2: Modal de Upgrade**

```
┌─────────────────────────────────────────────────┐
│  TEMPLATE: MODAL DE UPGRADE                     │
└─────────────────────────────────────────────────┘

ESTRUCTURA:
─────────────────────────────────────────────────
┌─────────────────────────────────────────┐
│  [X] Cerrar                            │
│                                         │
│  [Título: Desbloquea [Feature/Plan]]    │
│                                         │
│  [Mensaje contextual: Por qué aparece]   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  Plan Actual: [Plan]             │   │
│  │  • [Limitación actual]          │   │
│  └─────────────────────────────────┘   │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │  [Plan Premium] - $X/mes       │   │
│  │  ✅ [Beneficio 1]               │   │
│  │  ✅ [Beneficio 2]               │   │
│  │  ✅ [Beneficio 3]               │   │
│  │  ✅ [Beneficio 4]               │   │
│  │                                  │   │
│  │  [Botón: Upgrade Ahora]          │   │
│  └─────────────────────────────────┘   │
│                                         │
│  [Link: Comparar todos los planes]     │
│  [Link: Ver precios anuales]           │
└─────────────────────────────────────────┘

MEJORES PRÁCTICAS:
✅ Aparece en momento de necesidad
✅ Comparación clara (actual vs premium)
✅ Beneficios específicos, no genéricos
✅ Precio visible y claro
✅ CTA prominente
✅ Fácil de cerrar
✅ No agresivo
```

### **Template 3: Checklist de Onboarding**

```
┌─────────────────────────────────────────────────┐
│  TEMPLATE: CHECKLIST DE ONBOARDING              │
└─────────────────────────────────────────────────┘

ESTRUCTURA:
─────────────────────────────────────────────────
┌─────────────────────────────────────────┐
│  Configura tu cuenta                   │
│  ────────────────────────────────────  │
│                                         │
│  ✅ Conecta tu [integración 1]         │
│     [Descripción breve]                │
│     [Botón: Conectar]                  │
│                                         │
│  ☐ Personaliza tu perfil              │
│     [Descripción breve]                │
│     [Botón: Personalizar]              │
│                                         │
│  ☐ Crea tu primer [objeto]             │
│     [Descripción breve]                │
│     [Botón: Crear]                      │
│                                         │
│  ☐ Invita a tu equipo                  │
│     [Descripción breve]                │
│     [Botón: Invitar]                    │
│                                         │
│  ────────────────────────────────────  │
│  Progreso: 1/4 completado              │
│                                         │
│  [Link: Saltar por ahora]              │
└─────────────────────────────────────────┘

ELEMENTOS CLAVE:
✅ Máximo 4-5 pasos
✅ Progreso visual claro
✅ Descripción breve de cada paso
✅ CTA por paso
✅ Opción de saltar
✅ Celebración al completar
```

---

## 📈 Calculadoras de Métricas

### **Calculadora 1: K-Factor (Viral Coefficient)**

```
┌─────────────────────────────────────────────────┐
│  CALCULADORA: K-FACTOR (COEFICIENTE VIRAL)      │
└─────────────────────────────────────────────────┘

INPUTS:
─────────────────────────────────────────────────
Promedio de invitaciones por usuario: [_____]
Tasa de conversión de invitaciones:  [_____]%

CÁLCULO:
─────────────────────────────────────────────────
K-Factor = Invitaciones × Conversión
K-Factor = [_____] × [_____]% = [_____]

INTERPRETACIÓN:
─────────────────────────────────────────────────
K > 2.0: Crecimiento exponencial 🚀
K 1.0-2.0: Crecimiento viral ✅
K 0.5-1.0: Crecimiento ayudado ⚠️
K < 0.5: Crecimiento no viral ❌

OBJETIVO:
─────────────────────────────────────────────────
Para alcanzar K = [objetivo]:
- Aumentar invitaciones a: [_____]
- O mejorar conversión a: [_____]%
- O ambos
```

### **Calculadora 2: LTV/CAC Ratio**

```
┌─────────────────────────────────────────────────┐
│  CALCULADORA: LTV/CAC RATIO                     │
└─────────────────────────────────────────────────┘

INPUTS:
─────────────────────────────────────────────────
ARPA (Average Revenue Per Account): $[_____]/mes
Churn rate mensual:                [_____]%
CAC (Customer Acquisition Cost):   $[_____]

CÁLCULOS:
─────────────────────────────────────────────────
LTV = ARPA / Churn Rate
LTV = $[_____] / [_____]% = $[_____]

LTV/CAC = LTV / CAC
LTV/CAC = $[_____] / $[_____] = [_____]:1

Payback Period = CAC / (ARPA × Gross Margin)
Payback = $[_____] / ($[_____] × [__]%) = [_____] meses

INTERPRETACIÓN:
─────────────────────────────────────────────────
LTV/CAC > 5:1: Excelente 🚀
LTV/CAC 3:1-5:1: Bueno ✅
LTV/CAC 2:1-3:1: Mejorable ⚠️
LTV/CAC < 2:1: Crítico ❌

Payback < 6 meses: Excelente 🚀
Payback 6-12 meses: Bueno ✅
Payback > 12 meses: Mejorable ⚠️
```

### **Calculadora 3: Net Revenue Retention (NRR)**

```
┌─────────────────────────────────────────────────┐
│  CALCULADORA: NET REVENUE RETENTION              │
└─────────────────────────────────────────────────┘

INPUTS (Mes):
─────────────────────────────────────────────────
MRR inicio de mes:        $[_____]
MRR de churn:             $[_____]
MRR de expansión:         $[_____]
MRR de contracción:        $[_____]

CÁLCULOS:
─────────────────────────────────────────────────
MRR final = MRR inicio - Churn + Expansión - Contracción
MRR final = $[_____] - $[_____] + $[_____] - $[_____]
MRR final = $[_____]

NRR = (MRR final / MRR inicio) × 100
NRR = ($[_____] / $[_____]) × 100 = [_____]%

INTERPRETACIÓN:
─────────────────────────────────────────────────
NRR > 120%: Excelente 🚀 (crecimiento sin nuevos clientes)
NRR 110-120%: Muy bueno ✅
NRR 100-110%: Bueno ⚠️
NRR < 100%: Crítico ❌ (pérdida neta de revenue)
```

### **Calculadora 4: Tasa de Conversión Objetivo**

```
┌─────────────────────────────────────────────────┐
│  CALCULADORA: TASA DE CONVERSIÓN OBJETIVO        │
└─────────────────────────────────────────────────┘

INPUTS:
─────────────────────────────────────────────────
Sign-ups mensuales:        [_____]
MRR objetivo mensual:     $[_____]
ARPA objetivo:             $[_____]/mes

CÁLCULOS:
─────────────────────────────────────────────────
Clientes necesarios = MRR objetivo / ARPA
Clientes necesarios = $[_____] / $[_____] = [_____]

Tasa de conversión necesaria = (Clientes / Sign-ups) × 100
Tasa de conversión = ([_____] / [_____]) × 100 = [_____]%

COMPARACIÓN:
─────────────────────────────────────────────────
Tasa actual:               [_____]%
Tasa necesaria:            [_____]%
Gap:                       [_____] puntos porcentuales

ACCIONES:
─────────────────────────────────────────────────
Para cerrar el gap, necesitas:
• Mejorar onboarding: +[__] puntos
• Optimizar prompts: +[__] puntos
• Mejorar pricing: +[__] puntos
• Reducir fricción: +[__] puntos
```

---

## ✅ Checklists de Implementación

### **Checklist 1: Setup Inicial PLG**

```
┌─────────────────────────────────────────────────┐
│  CHECKLIST: SETUP INICIAL PLG                   │
└─────────────────────────────────────────────────┘

PREPARACIÓN
─────────────────────────────────────────────────
[ ] Evaluar si PLG es adecuado (usar framework)
[ ] Definir modelo (Freemium/Trial/Mixto)
[ ] Identificar "Aha moment"
[ ] Mapear customer journey
[ ] Establecer métricas baseline

PRODUCTO
─────────────────────────────────────────────────
[ ] Crear versión free/trial
[ ] Definir límites y gating
[ ] Implementar sistema de upgrades
[ ] Setup de billing
[ ] Configurar planes y precios

TÉCNICO
─────────────────────────────────────────────────
[ ] Implementar analytics (Mixpanel/Amplitude)
[ ] Configurar event tracking
[ ] Setup herramientas in-app (Userpilot/Appcues)
[ ] Configurar emails de onboarding
[ ] Implementar feature flags (si necesario)

ONBOARDING
─────────────────────────────────────────────────
[ ] Simplificar sign-up (SSO)
[ ] Crear empty states
[ ] Diseñar onboarding flow
[ ] Implementar checklists
[ ] Crear templates/ejemplos
[ ] Setup tooltips y guías

MÉTRICAS
─────────────────────────────────────────────────
[ ] Definir métricas clave
[ ] Configurar dashboards
[ ] Establecer baseline
[ ] Setup reporting
[ ] Configurar alertas

TESTING
─────────────────────────────────────────────────
[ ] Testear flujo completo end-to-end
[ ] Validar con usuarios beta
[ ] A/B test setup
[ ] Iterar basado en feedback
```

### **Checklist 2: Optimización de Conversión**

```
┌─────────────────────────────────────────────────┐
│  CHECKLIST: OPTIMIZACIÓN DE CONVERSIÓN          │
└─────────────────────────────────────────────────┘

ANÁLISIS
─────────────────────────────────────────────────
[ ] Analizar funnel de conversión
[ ] Identificar puntos de drop-off
[ ] Analizar cohortes
[ ] Comparar convertidos vs no-convertidos
[ ] Identificar señales de PQL

ESTRATEGIA
─────────────────────────────────────────────────
[ ] Definir límites claros (si freemium)
[ ] Diseñar prompts contextuales
[ ] Crear mensajes de conversión
[ ] Optimizar proceso de pago
[ ] Diseñar ofertas especiales

IMPLEMENTACIÓN
─────────────────────────────────────────────────
[ ] Implementar límites en producto
[ ] Crear modals de upgrade
[ ] Setup de recordatorios (si trial)
[ ] Optimizar checkout flow
[ ] Implementar garantías

TESTING
─────────────────────────────────────────────────
[ ] A/B test de precios
[ ] A/B test de mensajes
[ ] A/B test de timing
[ ] A/B test de ofertas
[ ] Medir impacto

OPTIMIZACIÓN
─────────────────────────────────────────────────
[ ] Analizar resultados semanalmente
[ ] Iterar basado en datos
[ ] Optimizar continuamente
[ ] Escalar lo que funciona
```

### **Checklist 3: Implementación de Viralidad**

```
┌─────────────────────────────────────────────────┐
│  CHECKLIST: IMPLEMENTACIÓN DE VIRALIDAD           │
└─────────────────────────────────────────────────┘

DISEÑO
─────────────────────────────────────────────────
[ ] Identificar mecanismo viral adecuado
[ ] Diseñar flujo de invitación
[ ] Definir incentivos (dual si es posible)
[ ] Crear mensajes de invitación
[ ] Diseñar UI de invitación

IMPLEMENTACIÓN
─────────────────────────────────────────────────
[ ] Implementar flujo técnico
[ ] Setup de tracking de invitaciones
[ ] Configurar incentivos
[ ] Integrar en producto
[ ] Setup de emails de invitación
[ ] Testear end-to-end

OPTIMIZACIÓN
─────────────────────────────────────────────────
[ ] Medir K-factor baseline
[ ] A/B test de mensajes
[ ] A/B test de incentivos
[ ] A/B test de timing
[ ] Analizar métricas semanalmente
[ ] Iterar basado en datos

ESCALAMIENTO
─────────────────────────────────────────────────
[ ] Optimizar para K > 1.0
[ ] Reducir fricción de invitación
[ ] Mejorar conversión de invitaciones
[ ] Expandir mecanismos virales
[ ] Medir impacto en crecimiento orgánico
```

---

## 📝 Templates de Documentación

### **Template 1: Plan de Implementación PLG**

```
┌─────────────────────────────────────────────────┐
│  PLAN DE IMPLEMENTACIÓN PLG                     │
│  Producto: [Nombre]                             │
│  Fecha: [Fecha]                                  │
└─────────────────────────────────────────────────┘

OBJETIVOS
─────────────────────────────────────────────────
Objetivo principal: [Descripción]
Métricas objetivo:
- Sign-up rate: [__]%
- Activation rate: [__]%
- Conversion rate: [__]%
- MRR objetivo: $[_____]

MODELO ELEGIDO
─────────────────────────────────────────────────
Modelo: [Freemium/Free Trial/Mixto]
Justificación: [Razón]

AHA MOMENT
─────────────────────────────────────────────────
Milestone de activación: [Descripción]
Time-to-value objetivo: [__] horas

ESTRATEGIA
─────────────────────────────────────────────────
Onboarding: [Descripción]
Conversión: [Descripción]
Viralidad: [Descripción]

TIMELINE
─────────────────────────────────────────────────
Semana 1-2: [Tareas]
Semana 3-4: [Tareas]
Mes 2: [Tareas]
Mes 3+: [Tareas]

EQUIPO
─────────────────────────────────────────────────
Product Manager: [Nombre]
Growth Lead: [Nombre]
Designer: [Nombre]
Engineer: [Nombre]

MÉTRICAS
─────────────────────────────────────────────────
Métricas clave: [Lista]
Dashboard: [Link]
Reporting: [Frecuencia]

RIESGOS
─────────────────────────────────────────────────
Riesgo 1: [Descripción] - Mitigación: [Acción]
Riesgo 2: [Descripción] - Mitigación: [Acción]
```

### **Template 2: Análisis de Cohort**

```
┌─────────────────────────────────────────────────┐
│  ANÁLISIS DE COHORT - [COHORT NAME]              │
│  Período: [Fecha inicio] - [Fecha fin]          │
└─────────────────────────────────────────────────┘

DATOS
─────────────────────────────────────────────────
Sign-ups: [_____]
Activados: [_____] ([__]%)
Convertidos: [_____] ([__]%)

RETENCIÓN
─────────────────────────────────────────────────
Mes 0: [_____] (100%)
Mes 1: [_____] ([__]%)
Mes 2: [_____] ([__]%)
Mes 3: [_____] ([__]%)
Mes 6: [_____] ([__]%)

REVENUE
─────────────────────────────────────────────────
MRR inicial: $[_____]
MRR actual: $[_____]
LTV promedio: $[_____]

INSIGHTS
─────────────────────────────────────────────────
[Espacio para insights clave]

ACCIONES
─────────────────────────────────────────────────
[Espacio para acciones basadas en insights]
```

---

*Última actualización: 2024*

