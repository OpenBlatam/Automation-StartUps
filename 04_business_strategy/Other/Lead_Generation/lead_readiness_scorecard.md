---
title: "Lead Readiness Scorecard"
category: "04_business_strategy"
tags: []
created: "2025-10-29"
path: "04_business_strategy/Other/lead_readiness_scorecard.md"
---

# Lead Readiness Scorecard (Matriz Ponderada)

Evalúa rápidamente cuán listo está un lead para convertir (demo/webinar/trial).

## Criterios y Pesos (100 puntos)

| Criterio | Descripción | Puntaje (0-5) | Peso | Puntos Máx |
|---|---|---:|---:|---:|
| Logro reciente verificable | Post/noticia <30 días, relevante | 0-5 | 0.20 | 20 |
| Fit de industria/ICP | Coincide con ICP (industria/tamaño/rol) | 0-5 | 0.20 | 20 |
| Dolor explícito detectable | Señal de necesidad (post/comentarios) | 0-5 | 0.15 | 15 |
| Rol/Autoridad | Decisor o influenciador clave | 0-5 | 0.15 | 15 |
| Señales de intención | Engagement previo (abre/clic, evento, visita) | 0-5 | 0.15 | 15 |
| Disponibilidad/timing | Ventana (presupuesto, trimestre, lanzamiento) | 0-5 | 0.15 | 15 |
| Total |  |  | 1.00 | 100 |

Guía de puntaje (0-5):
- 0: No evidencia
- 1: Débil
- 3: Moderado
- 5: Fuerte/confirmado

## Interpretación
- 80-100: Listo (prioridad alta, CTA fuerte)
- 60-79: Prometedor (CTA estándar, seguimiento estricto)
- 40-59: Nutrir (aportar valor, caso/ejemplo, reintentar luego)
- <40: Baja prioridad (no invertir más por ahora)

## Fórmulas (Google Sheets/Excel)

Supón columnas:
- Criterios en columnas C:H (Puntaje 0-5)
- Pesos en fila 2 (ej. C2=0.20, D2=0.20, E2=0.15, F2=0.15, G2=0.15, H2=0.15)
- Puntajes del lead en fila 3 (C3:H3)

Puntaje ponderado total (celda B3):
```
=SUMPRODUCT(C3:H3, C2:H2)*20
```
Nota: Multiplicamos por 20 porque cada criterio es 0-5 y pesos suman 1 → 5*20=100.

Clasificación (celda C3, usando B3):
```
=IFS(B3>=80, "Listo", B3>=60, "Prometedor", B3>=40, "Nutrir", TRUE, "Baja prioridad")
```

Sugerencia de CTA (celda D3):
```
=IFS(B3>=80, "Demo 15 min / Trial", B3>=60, "Invitación webinar / Demo breve", B3>=40, "Enviar caso 1 pág / Recurso", TRUE, "Nurture")
```

## Señales para cada criterio (ejemplos)
- Logro reciente: funding, lanzamiento, expansión, KPI público
- Fit ICP: industria prioritaria, tamaño empresa, región, rol objetivo
- Dolor explícito: “buscamos optimizar…”, “necesitamos…”, “nos frena…”
- Rol/autoridad: C-level, VP, Head; o influencer con ownership
- Intención: abrió/clic, respondió, asistió a evento, visitó landing
- Timing: trimestre de compra, nuevo presupuesto, fase post-lanzamiento

## Flujo recomendado
1) Califica el lead con 6 criterios (0-5)
2) Obtén el puntaje (B3) y la clasificación
3) Elige CTA acorde a clasificación
4) Registra resultado y avanza con el playbook correspondiente (`PLAYBOOKS_POR_OBJETIVO.md`)

## Integración
- Añade columnas al CRM: `readiness_score`, `readiness_tier`, `suggested_cta`
- Usa en filtros/vistas para priorizar envíos del día
- Conecta a dashboard (`KPI_DASHBOARD_TEMPLATE.md`) para analizar resultados por tier
