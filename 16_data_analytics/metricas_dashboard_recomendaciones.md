---
title: "Metricas Dashboard Recomendaciones"
category: "metricas_dashboard_recomendaciones.md"
tags: []
created: "2025-10-29"
path: "metricas_dashboard_recomendaciones.md"
---

# 📊 Métricas y Dashboard - Sistemas de Recomendaciones Personalizadas
## KPIs Completos para Medir Éxito

## 🎯 MÉTRICAS PRINCIPALES (Core KPIs)

### 1. CTR Recomendaciones (Click-Through Rate)
**Fórmula:** `(Clicks en recomendaciones / Impresiones de recomendaciones) × 100`

**Benchmarks por Industria:**
- E-commerce general: 12-18%
- Fashion: 15-22% (más visual)
- Tech/SaaS: 8-15%
- Marketplace: 10-18%

**Objetivo típico:** >15%

**Cómo mejorar:**
- Mejor relevancia (algoritmo más preciso)
- Mejor ubicación (más visible)
- Mejor presentación (imágenes, precios)
- Timing (cuándo mostrar)

---

### 2. Conversión de Recomendaciones
**Fórmula:** `(Compras desde recomendaciones / Clicks en recomendaciones) × 100`

**Benchmarks:**
- Promedio industria: 8-12%
- Top performers: 15-25%

**Objetivo típico:** >10%

**Cómo mejorar:**
- Mejor matching (productos más relevantes)
- Personalización más granular
- Recomendaciones en momento correcto (carrito, checkout)
- Upsell/cross-sell inteligente

---

### 3. Revenue Atribuible a Recomendaciones
**Fórmula:** `Suma de revenue de todas las compras iniciadas desde recomendaciones`

**Calculación:**
```
Revenue Recomendaciones = 
  Suma de (compras desde recomendaciones × ticket promedio de esas compras)
```

**Objetivo típico:** 20-30% del revenue total

**Cómo mejorar:**
- Aumentar CTR
- Aumentar conversión
- Aumentar ticket promedio (cross-sell)

---

### 4. Ticket Promedio Impactado
**Fórmula:** `Ticket promedio de usuarios que interactúan con recomendaciones vs usuarios que no`

**Comparativa:**
```
Incremento Ticket = 
  (Ticket promedio con recomendaciones - Ticket promedio sin) / 
  Ticket promedio sin × 100
```

**Objetivo típico:** +30-50%

**Cómo mejorar:**
- Recomendaciones complementarias en carrito
- Upsell estratégico
- Bundles inteligentes

---

## 📈 MÉTRICAS SECUNDARIAS (Importantes)

### 5. Precision@K
**Fórmula:** `(Items relevantes recomendados / K) × 100`

Donde K = número de recomendaciones mostradas (típicamente K=10)

**Interpretación:**
- Precision@10 = 60% significa que 6 de 10 recomendaciones son relevantes

**Objetivo típico:** >60%

---

### 6. Recall@K
**Fórmula:** `(Items relevantes recomendados / Total items relevantes para usuario) × 100`

**Interpretación:**
- Qué % de productos que al usuario le interesan están en las recomendaciones

**Objetivo típico:** >40%

---

### 7. Coverage (Cobertura)
**Fórmula:** `(Items únicos recomendados / Total items en catálogo) × 100`

**Interpretación:**
- Qué % del catálogo puede ser recomendado

**Objetivo típico:** >60% (no solo productos populares)

**Cómo mejorar:**
- Diversidad en recomendaciones
- Explorar productos menos conocidos
- Evitar filter bubble

---

### 8. Diversity (Diversidad)
**Fórmula:** `Variedad de categorías/productos diferentes en recomendaciones`

**Medición:**
- Número de categorías únicas recomendadas
- Similitud promedio entre productos recomendados (menor = más diverso)

**Objetivo típico:** >3-5 categorías diferentes por usuario

**Cómo mejorar:**
- Balancear similitud con exploración
- Incluir "sorpresas" controladas
- Rotar recomendaciones

---

### 9. Novelty (Novedad)
**Fórmula:** `% de productos nuevos/exploratorios recomendados`

**Interpretación:**
- Recomendaciones que ayudan a usuario a descubrir productos nuevos

**Objetivo típico:** 10-20% de recomendaciones deben ser exploratorias

---

### 10. User Engagement
**Métricas:**
- Tiempo en sitio: +25-40% con recomendaciones efectivas
- Páginas por sesión: +35-50%
- Retorno: +20-30% clientes vuelven

---

## 💰 MÉTRICAS DE NEGOCIO

### 11. ROI del Sistema
**Fórmula:** `(Revenue generado - Costos) / Costos × 100`

**Cálculo detallado:**
```
ROI = [
  (Revenue adicional mensual × 12) - 
  (Costo implementación + Mantenimiento anual)
] / (Costo implementación + Mantenimiento anual) × 100
```

**Objetivo típico:** >500-1000% anual

---

### 12. Customer Lifetime Value (LTV) Impact
**Fórmula:** `LTV de usuarios que usan recomendaciones vs usuarios que no`

**Impacto típico:** +25-40% LTV

---

### 13. Retention Rate
**Fórmula:** `% de usuarios que regresan después de usar recomendaciones`

**Impacto típico:** +15-25% retención

---

## 🔍 MÉTRICAS TÉCNICAS

### 14. Response Time (Performance)
**Objetivo:** <200ms tiempo de respuesta API

**Cómo medir:**
- P95 (percentil 95)
- P99 (percentil 99)
- Promedio

**Cómo mejorar:**
- Caching
- Indexing
- Optimización de queries
- CDN

---

### 15. System Uptime
**Objetivo:** >99.5%

**Cómo mejorar:**
- Monitoring y alertas
- Redundancia
- Fallbacks
- Load balancing

---

### 16. Model Accuracy
**Métricas:**
- RMSE (Root Mean Squared Error): <0.8 ideal
- MAE (Mean Absolute Error): <0.6 ideal

**Para ratings 1-5:**
- RMSE <1.0 = Bueno
- RMSE <0.8 = Excelente

---

## 📊 DASHBOARD RECOMENDADO

### Panel 1: Métricas Principales (Real-time)
```
┌─────────────────────────────────────┐
│ CTR Recomendaciones       15.2% ▲ 2.3%│
│ Conversión Recs           10.8% ▲ 1.1%│
│ Revenue Recomendaciones  $45.2K ▲ 12%│
│ Ticket Promedio Impact   +42% ▲ 5%   │
└─────────────────────────────────────┘
```

---

### Panel 2: Performance por Ubicación
```
┌─────────────────────────────────────┐
│ Homepage:      CTR 18.2%  Conv 12.1%│
│ Product Page:  CTR 14.5%  Conv 11.3%│
│ Cart:          CTR 22.1%  Conv 15.8%│
│ Checkout:      CTR 19.3%  Conv 18.2%│
└─────────────────────────────────────┘
```

---

### Panel 3: Performance por Algoritmo
```
┌─────────────────────────────────────┐
│ Collaborative: CTR 16.1%  Conv 10.2%│
│ Content-Based: CTR 13.8%  Conv  9.1%│
│ Híbrido:       CTR 18.3%  Conv 12.5%│ ← Mejor
└─────────────────────────────────────┘
```

---

### Panel 4: Trends (7/30 días)
- CTR trending
- Conversión trending
- Revenue trending
- Nuevos usuarios usando recomendaciones

---

## 🎯 ALERTAS Y MONITOREO

### Alertas Críticas
1. **CTR cae >20%:** Posible problema con algoritmo o datos
2. **Conversión cae >15%:** Revisar relevancia de recomendaciones
3. **Response time >500ms:** Problema de performance
4. **Uptime <99%:** Problema de infraestructura
5. **Revenue cae >10%:** Análisis completo necesario

---

### Monitoreo Continuo
- [ ] CTR diario vs promedio
- [ ] Conversión diaria vs promedio
- [ ] Revenue diario vs promedio
- [ ] Errores del sistema
- [ ] Performance (response time)
- [ ] Uptime

---

## 📈 REPORTES RECOMENDADOS

### Reporte Diario
- Métricas principales (CTR, conversión, revenue)
- Comparativa día anterior
- Alertas activas
- Top 5 productos más recomendados
- Top 5 productos más convertidos desde recomendaciones

---

### Reporte Semanal
- Métricas principales (promedio semanal)
- Comparativa semana anterior
- Performance por ubicación
- Performance por algoritmo (si A/B testing)
- Análisis de tendencias
- Insights y recomendaciones

---

### Reporte Mensual
- ROI del sistema
- LTV impact
- Retention impact
- Análisis completo de métricas
- Roadmap de mejoras
- Comparativa mes anterior y mismo mes año anterior

---

## 🔧 HERRAMIENTAS RECOMENDADAS PARA TRACKING

### Recursos directos (Google Sheets)
- `panel_combinado.csv` — KPI combinado Sequences + ROI listo para importar
- `panel_combinado_guia.md` — Guía rápida para configurar el panel

### Analytics
- **Google Analytics:** Tracking básico
- **Mixpanel/Amplitude:** Event tracking avanzado
- **Custom dashboards:** Métricas específicas

### A/B Testing
- **Optimizely/VWO:** Testing de recomendaciones
- **Google Optimize:** Testing básico
- **Custom:** Testing interno

### Monitoring
- **Datadog/New Relic:** Performance monitoring
- **Sentry:** Error tracking
- **Custom:** Métricas específicas del sistema

---

## ✅ CHECKLIST DE MÉTRICAS IMPLEMENTADAS

### Básico (Mínimo)
- [ ] CTR recomendaciones
- [ ] Conversión recomendaciones
- [ ] Revenue atribuible
- [ ] Response time

### Intermedio (Recomendado)
- [ ] Todas las básicas +
- [ ] Precision@K
- [ ] Recall@K
- [ ] Ticket promedio impactado
- [ ] Coverage
- [ ] Uptime

### Avanzado (Ideal)
- [ ] Todas las anteriores +
- [ ] Diversity
- [ ] Novelty
- [ ] LTV impact
- [ ] Retention
- [ ] ROI detallado
- [ ] Performance por ubicación
- [ ] Performance por algoritmo
- [ ] User engagement completo

---

**Última actualización:** [Fecha]
**Versión:** 1.0 - Métricas y Dashboard Completos




