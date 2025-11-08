# 🎯 Sistema de Scoring de Leads

## 📊 Modelo de Scoring

### Puntos por Acción:

**Engagement:**
```
Abrir email: +5 puntos
Click en CTA: +10 puntos
Click en múltiples links: +15 puntos
Click en link específico: +20 puntos
Responder email: +50 puntos
```

**Comportamiento Web:**
```
Visitar landing page: +20 puntos
Visitar pricing page: +30 puntos
Completar formulario: +40 puntos
Descargar recurso: +25 puntos
Ver video: +15 puntos
```

**Interacción Avanzada:**
```
Múltiples visitas: +10 puntos (cada visita adicional)
Tiempo en página >2 min: +15 puntos
Páginas vistas >3: +20 puntos
Volver después de 24h: +25 puntos
```

**Calificación Negativa:**
```
No abrir 3 emails seguidos: -10 puntos
Bounce: -5 puntos
Unsubscribe: -100 puntos
Marcar como spam: -100 puntos
```

---

## 🎯 Niveles de Lead

### Clasificación:

**Cold (0-20 puntos):**
```
Características:
- Poco o ningún engagement
- Sin interacción reciente
- Acción: Nurturing básico
```

**Warm (21-50 puntos):**
```
Características:
- Engagement moderado
- Algunas interacciones
- Acción: Nurturing avanzado + oferta
```

**Hot (51-100 puntos):**
```
Características:
- Alto engagement
- Múltiples interacciones
- Acción: Notificar a ventas + email personalizado
```

**Muy Hot (100+ puntos):**
```
Características:
- Engagement muy alto
- Comportamiento de compra
- Acción: Contacto inmediato de ventas
```

---

## 🔄 Automatización de Scoring

### Workflow:

```
Trigger: Cualquier acción del lead
  ↓
Calcular score:
  ├─ Obtener score actual
  ├─ Sumar puntos por acción
  ├─ Aplicar penalizaciones
  └─ Actualizar score
  ↓
Evaluar nivel:
  ├─ Si score < 21: Cold
  ├─ Si score 21-50: Warm
  ├─ Si score 51-100: Hot
  └─ Si score > 100: Muy Hot
  ↓
Acción según nivel:
  ├─ Cold: Continuar nurturing básico
  ├─ Warm: Nurturing avanzado + oferta
  ├─ Hot: Notificar ventas + email personalizado
  └─ Muy Hot: Contacto inmediato
```

---

## 📊 Dashboard de Scoring

### Métricas:

**Distribución de Leads:**
```
Cold: X leads (Y%)
Warm: X leads (Y%)
Hot: X leads (Y%)
Muy Hot: X leads (Y%)
```

**Tendencias:**
```
Leads moviéndose de Cold → Warm: X
Leads moviéndose de Warm → Hot: X
Leads moviéndose de Hot → Muy Hot: X
```

**Conversión por Nivel:**
```
Cold → Cliente: X%
Warm → Cliente: Y%
Hot → Cliente: Z%
Muy Hot → Cliente: W%
```

---

## 🎯 Segmentación por Score

### Estrategias:

**Cold Leads:**
```
Email: Educativo, sin venta directa
Frecuencia: 1 vez/semana
Contenido: Valor, educación, casos de éxito
```

**Warm Leads:**
```
Email: Educativo + oferta suave
Frecuencia: 2-3 veces/semana
Contenido: Valor + prueba social + oferta
```

**Hot Leads:**
```
Email: Personalizado + oferta directa
Frecuencia: 3-4 veces/semana
Contenido: Oferta + urgencia + CTA fuerte
```

**Muy Hot Leads:**
```
Email: Personalizado + oferta exclusiva
Frecuencia: Diario (si necesario)
Contenido: Oferta exclusiva + urgencia máxima
```

---

## ✅ Checklist de Scoring

### Pre-Implementación:
- [ ] Definir modelo de scoring
- [ ] Configurar puntos por acción
- [ ] Configurar niveles
- [ ] Configurar automatización
- [ ] Testear sistema

### Post-Implementación:
- [ ] Monitorear distribución de leads
- [ ] Ajustar puntos según resultados
- [ ] Optimizar segmentación
- [ ] Documentar cambios

---

**Sistema completo de scoring para priorizar leads.** 🎯

