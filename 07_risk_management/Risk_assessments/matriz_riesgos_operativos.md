---
title: "Matriz Riesgos Operativos"
category: "07_risk_management"
tags: []
created: "2025-10-29"
path: "07_risk_management/Risk_assessments/matriz_riesgos_operativos.md"
---

# MATRIZ DE RIESGOS OPERATIVOS AVANZADA
## Análisis Cuantitativo y Modelado de Riesgos

---

## 🎯 METODOLOGÍA DE ANÁLISIS DE RIESGOS

### Framework de Evaluación de Riesgos:
```
┌─────────────────────────────────────────────────────────────┐
│ MATRIZ DE PROBABILIDAD E IMPACTO                            │
│                                                             │
│ PROBABILIDAD (Eje X):                                      │
│ ├── Muy Baja (1): <10% probabilidad                        │
│ ├── Baja (2): 10-30% probabilidad                          │
│ ├── Media (3): 30-60% probabilidad                         │
│ ├── Alta (4): 60-80% probabilidad                          │
│ └── Muy Alta (5): >80% probabilidad                        │
│                                                             │
│ IMPACTO (Eje Y):                                           │
│ ├── Muy Bajo (1): <$50K impacto financiero                 │
│ ├── Bajo (2): $50K-$200K impacto financiero                │
│ ├── Medio (3): $200K-$500K impacto financiero              │
│ ├── Alto (4): $500K-$1M impacto financiero                │
│ └── Muy Alto (5): >$1M impacto financiero                  │
│                                                             │
│ NIVEL DE RIESGO = PROBABILIDAD × IMPACTO                   │
│ ├── Crítico: 20-25 puntos                                  │
│ ├── Alto: 12-19 puntos                                     │
│ ├── Medio: 6-11 puntos                                     │
│ └── Bajo: 1-5 puntos                                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚨 RIESGOS OPERATIVOS CRÍTICOS

### Análisis Cuantitativo de Riesgos Críticos:
```
┌─────────────────────────────────────────────────────────────┐
│ RIESGO #1: PÉRDIDA DE TALENTO CLAVE                         │
│ ├── Probabilidad: 75% (Alta) │ Impacto: $500K (Alto)       │
│ ├── Nivel Riesgo: 20 (Crítico) │ Categoría: Recursos Humanos│
│ ├── Indicadores Tempranos:                                  │
│ │   ├── Satisfacción laboral <7.0/10                       │
│ │   ├── Rotación voluntaria >15% anual                     │
│ │   ├── Tiempo respuesta ofertas externas <48h              │
│ │   └── Ausentismo >5% mensual                             │
│ ├── Impacto Financiero Detallado:                          │
│ │   ├── Costo reclutamiento: $150K                         │
│ │   ├── Pérdida productividad: $200K                        │
│ │   ├── Costo capacitación: $100K                           │
│ │   └── Impacto reputacional: $50K                         │
│ ├── Plan Mitigación:                                        │
│ │   ├── Programa retención personalizado                   │
│ │   ├── Planes carrera individuales                        │
│ │   ├── Compensación competitiva                            │
│ │   └── Cultura organizacional fortalecida                  │
│ ├── Costo Mitigación: $80K │ Efectividad: 70%               │
│ └── Responsable: CHRO │ Revisión: Mensual                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RIESGO #2: CRISIS DE LIQUIDEZ                               │
│ ├── Probabilidad: 60% (Alta) │ Impacto: $800K (Muy Alto)   │
│ ├── Nivel Riesgo: 24 (Crítico) │ Categoría: Financiero     │
│ ├── Indicadores Tempranos:                                  │
│ │   ├── Flujo caja <$2M mensual                             │
│ │   ├── Días cobranza >50 días                              │
│ │   ├── Ratio liquidez <1.5                                 │
│ │   └── Deuda corto plazo >$1M                             │
│ ├── Impacto Financiero Detallado:                          │
│ │   ├── Costo financiamiento adicional: $200K               │
│ │   ├── Pérdida oportunidades: $300K                      │
│ │   ├── Penalizaciones proveedores: $150K                  │
│ │   └── Impacto reputación crediticia: $150K               │
│ ├── Plan Mitigación:                                        │
│ │   ├── Línea crédito contingencia $2M                     │
│ │   ├── Optimización ciclo cobranza                         │
│ │   ├── Gestión activa cuentas por pagar                   │
│ │   └── Diversificación fuentes financiamiento             │
│ ├── Costo Mitigación: $120K │ Efectividad: 85%             │
│ └── Responsable: CFO │ Revisión: Semanal                   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│ RIESGO #3: FALLA TECNOLÓGICA CRÍTICA                        │
│ ├── Probabilidad: 40% (Media) │ Impacto: $300K (Alto)      │
│ ├── Nivel Riesgo: 16 (Alto) │ Categoría: Tecnología        │
│ ├── Indicadores Tempranos:                                  │
│ │   ├── Uptime sistemas <98%                                │
│ │   ├── Tiempo respuesta >3 segundos                       │
│ │   ├── Alertas seguridad >5/mes                           │
│ │   └── Capacidad almacenamiento >85%                      │
│ ├── Impacto Financiero Detallado:                          │
│ │   ├── Pérdida productividad: $150K                       │
│ │   ├── Costo recuperación: $80K                           │
│ │   ├── Penalizaciones SLA: $50K                           │
│ │   └── Impacto reputacional: $20K                         │
│ ├── Plan Mitigación:                                        │
│ │   ├── Infraestructura redundante                         │
│ │   ├── Plan continuidad negocio                           │
│ │   ├── Monitoreo 24/7 sistemas                           │
│ │   └── Backup automático datos críticos                   │
│ ├── Costo Mitigación: $60K │ Efectividad: 90%              │
│ └── Responsable: CTO │ Revisión: Quincenal                  │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 MODELO DE SIMULACIÓN DE RIESGOS

### Simulador Monte Carlo para Riesgos:
```
┌─────────────────────────────────────────────────────────────┐
│ SIMULACIÓN MONTE CARLO - 10,000 ESCENARIOS                 │
│                                                             │
│ IMPACTO FINANCIERO TOTAL:                                   │
│ ├── Promedio: $485K                                        │
│ ├── Mediana: $300K                                         │
│ ├── Percentil 95: $1.2M                                    │
│ ├── Percentil 99: $1.8M                                    │
│ ├── Probabilidad impacto cero: 12%                         │
│ └── Probabilidad impacto >$1M: 8%                         │
│                                                             │
│ DISTRIBUCIÓN DE RIESGOS:                                   │
│ ├── Pérdida talento: 75% escenarios ($375K promedio)      │
│ ├── Crisis liquidez: 60% escenarios ($480K promedio)       │
│ ├── Falla tecnológica: 40% escenarios ($120K promedio)      │
│ ├── Incumplimiento regulatorio: 30% escenarios ($60K promedio) │
│ └── Pérdida cliente principal: 25% escenarios ($100K promedio) │
│                                                             │
│ CORRELACIONES IDENTIFICADAS:                                │
│ ├── Pérdida talento + Crisis liquidez: +30% impacto       │
│ ├── Crisis liquidez + Incumplimiento: +40% impacto         │
│ └── Múltiples riesgos simultáneos: +50% impacto           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 MATRIZ DE RIESGOS POR CATEGORÍA

### Riesgos Financieros:
```
┌─────────────────────────────────────────────────────────────┐
│ RIESGOS FINANCIEROS                                         │
│ ├── Crisis liquidez: Prob 60% │ Impacto $800K │ Nivel: Crítico │
│ ├── Volatilidad tipos cambio: Prob 40% │ Impacto $200K │ Nivel: Alto │
│ ├── Incumplimiento crédito: Prob 25% │ Impacto $300K │ Nivel: Alto │
│ ├── Fluctuación materias primas: Prob 70% │ Impacto $150K │ Nivel: Alto │
│ └── Riesgo concentración clientes: Prob 20% │ Impacto $400K │ Nivel: Alto │
└─────────────────────────────────────────────────────────────┘
```

### Riesgos Operativos:
```
┌─────────────────────────────────────────────────────────────┐
│ RIESGOS OPERATIVOS                                          │
│ ├── Falla tecnológica crítica: Prob 40% │ Impacto $300K │ Nivel: Alto │
│ ├── Interrupción cadena suministro: Prob 35% │ Impacto $250K │ Nivel: Alto │
│ ├── Pérdida datos críticos: Prob 20% │ Impacto $200K │ Nivel: Medio │
│ ├── Accidente operacional: Prob 15% │ Impacto $150K │ Nivel: Medio │
│ └── Calidad productos defectuosos: Prob 30% │ Impacto $180K │ Nivel: Alto │
└─────────────────────────────────────────────────────────────┘
```

### Riesgos de Recursos Humanos:
```
┌─────────────────────────────────────────────────────────────┐
│ RIESGOS DE RECURSOS HUMANOS                                 │
│ ├── Pérdida talento clave: Prob 75% │ Impacto $500K │ Nivel: Crítico │
│ ├── Huelga o conflicto laboral: Prob 10% │ Impacto $300K │ Nivel: Medio │
│ ├── Escasez talento especializado: Prob 60% │ Impacto $200K │ Nivel: Alto │
│ ├── Incidente seguridad laboral: Prob 25% │ Impacto $100K │ Nivel: Medio │
│ └── Pérdida conocimiento organizacional: Prob 40% │ Impacto $150K │ Nivel: Alto │
└─────────────────────────────────────────────────────────────┘
```

### Riesgos Regulatorios y de Cumplimiento:
```
┌─────────────────────────────────────────────────────────────┐
│ RIESGOS REGULATORIOS                                        │
│ ├── Incumplimiento regulatorio: Prob 30% │ Impacto $200K │ Nivel: Alto │
│ ├── Cambio normativa sector: Prob 50% │ Impacto $150K │ Nivel: Alto │
│ ├── Multa por incumplimiento: Prob 15% │ Impacto $100K │ Nivel: Medio │
│ ├── Pérdida licencias: Prob 5% │ Impacto $500K │ Nivel: Alto │
│ └── Litigio regulatorio: Prob 20% │ Impacto $300K │ Nivel: Alto │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛡️ PLAN DE MITIGACIÓN INTEGRADO

### Estrategias de Mitigación por Nivel de Riesgo:

#### **Riesgos Críticos (Nivel 20-25):**
1. **Acción Inmediata:** Implementar controles preventivos
2. **Recursos Dedicados:** Equipo específico de gestión
3. **Monitoreo Continuo:** Alertas en tiempo real
4. **Plan Contingencia:** Procedimientos detallados
5. **Comunicación Ejecutiva:** Reportes semanales

#### **Riesgos Altos (Nivel 12-19):**
1. **Controles Preventivos:** Medidas de mitigación activas
2. **Monitoreo Regular:** Evaluación mensual
3. **Capacitación:** Entrenamiento específico
4. **Documentación:** Procedimientos estandarizados
5. **Escalación:** Protocolo de alertas

#### **Riesgos Medios (Nivel 6-11):**
1. **Controles Básicos:** Medidas preventivas estándar
2. **Monitoreo Trimestral:** Evaluación periódica
3. **Capacitación General:** Entrenamiento básico
4. **Documentación:** Procedimientos básicos
5. **Revisión Anual:** Evaluación anual

#### **Riesgos Bajos (Nivel 1-5):**
1. **Controles Mínimos:** Medidas básicas
2. **Monitoreo Anual:** Evaluación anual
3. **Capacitación General:** Entrenamiento básico
4. **Documentación:** Procedimientos mínimos
5. **Revisión Periódica:** Seguimiento básico

---

## 📈 DASHBOARD DE GESTIÓN DE RIESGOS

### Indicadores Clave de Riesgo (KRIs):
```
┌─────────────────────────────────────────────────────────────┐
│ DASHBOARD DE RIESGOS EN TIEMPO REAL                        │
│                                                             │
│ ESTADO GENERAL:                                             │
│ ├── Riesgos Críticos Activos: 3 │ Objetivo: <2             │
│ ├── Riesgos Altos Activos: 7 │ Objetivo: <5                │
│ ├── Mitigaciones Implementadas: 85% │ Objetivo: >90%       │
│ └── Tiempo Respuesta Promedio: 2.3 días │ Objetivo: <1 día │
│                                                             │
│ ALERTAS ACTIVAS:                                            │
│ ├── 🔴 Pérdida talento: Probabilidad aumentó a 80%          │
│ ├── 🟡 Crisis liquidez: Indicadores en zona amarilla       │
│ ├── 🟡 Falla tecnológica: Capacidad almacenamiento 88%   │
│ └── 🟢 Incumplimiento regulatorio: Sin alertas activas     │
│                                                             │
│ PRÓXIMAS ACCIONES:                                         │
│ ├── Implementar programa retención talento (7 días)        │
│ ├── Optimizar gestión liquidez (14 días)                   │
│ ├── Actualizar infraestructura tecnológica (30 días)       │
│ └── Revisar políticas cumplimiento (45 días)               │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 MODELO DE OPTIMIZACIÓN DE RECURSOS

### Asignación Óptima de Recursos para Mitigación:
```
┌─────────────────────────────────────────────────────────────┐
│ OPTIMIZACIÓN DE RECURSOS PARA MITIGACIÓN                    │
│                                                             │
│ MEJOR COMBINACIÓN ENCONTRADA:                              │
│ ├── Pérdida Talento: Programa retención ($80K)             │
│ ├── Crisis Liquidez: Línea crédito contingencia ($100K)    │
│ ├── Falla Tecnológica: Infraestructura redundante ($150K)  │
│ ├── Costo Total: $330K (66% del presupuesto)               │
│ ├── Reducción Riesgo Total: 45%                            │
│ ├── ROI: 185%                                              │
│ └── Beneficio Neto: $610K                                  │
│                                                             │
│ RECURSOS RESTANTES: $170K                                   │
│ ├── Implementar planes carrera ($50K)                      │
│ ├── Optimización cobranza ($80K)                           │
│ └── Monitoreo 24/7 ($40K)                                  │
└─────────────────────────────────────────────────────────────┘
```

---

*Matriz de Riesgos Operativos preparada por: Equipo de Gestión de Riesgos*  
*Fecha: Diciembre 2024*  
*Metodología: ISO 31000, COSO ERM, Monte Carlo Simulation*



