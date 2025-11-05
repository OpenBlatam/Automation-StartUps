# 🧭 Executive Dashboard Spec (Looker/Sheets)

## 🎯 Objetivo
Proveer a dirección una vista clara semanal/mensual del funnel: Outreach → Demo → Close → ROI.

---

## 📊 KPIs Obligatorios (Top Row)
- Reply Rate DM (7d/30d)
- Reply Rate Email (7d/30d)
- DM→Demo (14d)
- Demo→Show (30d)
- Demo→Close (90d)
- ROI Mensual (USD)

---

## 📈 Vistas Principales

1) Conversión por Canal y Variante
- Barras apiladas: DM/Email por variante (A/B/C)
- Filtro: industria, tamaño, región, producto

2) Personalización vs Respuesta
- Scatter: nivel de personalización (1/2/3) vs reply
- Línea de tendencia

3) Pipeline por Etapa (Embudo)
- Leads contactados → Respuestas → Demos → Propuestas → Cierres
- Conversión etapa-a-etapa

4) ROI por Producto
- Tabla por producto: ahorro, ingresos, ROI total
- Señal de variación mensual

5) Alertas y Riesgos
- Tarjetas: reply bajo, no-show alto, variación negativa
- Lista de acciones sugeridas (hooks/CTAs/timing)

---

## 🧰 Filtros Requeridos
- Fecha: rango relativo (7/14/30/90 días)
- Industria
- Tamaño empresa (SMB/Mid/Ent)
- Región (LATAM/US/EU)
- Producto (Curso/Marketing/Docs)
- Canal (LinkedIn/Email/WhatsApp)

---

## 🔗 Fuentes de Datos
- `messages` (DM/Email)
- `meetings` (demos)
- `deals` (propuestas/cierres)
- `roi` (ahorro/ingresos por producto)

Looker: Explores por cada tabla + Join por `lead_id`
Sheets: Hojas `Datos` y tablas pivote + gráficos

---

## 🎛️ Interacciones UX
- Hover con detalles (fuentes, supuestos)
- Drill-down por variante y canal
- Export PDF mensual para comité

---

## 📅 Cadencia de Revisión
- Semanal: performance táctica
- Mensual: estrategia y A/B winners
- Trimestral: roadmap y presupuesto

---

**FIN DEL DOCUMENTO**



