---
title: "Kpis Dashboard Formulas"
category: "kpis_dashboard_formulas.md"
tags: []
created: "2025-10-29"
path: "kpis_dashboard_formulas.md"
---

# KPIs Dashboard - Fórmulas para Google Sheets

Importa `KPIs_Dashboard_Template.csv` y aplica estas fórmulas para métricas automáticas.

---

## 📊 FÓRMULAS ESENCIALES

### Reply Rate (% que responde)
```
=(COUNTIF(E2:E1000,"SÍ")/COUNTA(E2:E1000))*100
```
**Cálculo:** Respuestas "SÍ" / Total enviados × 100

**Meta:** 18-30% (bueno) | 25-35% (excelente)

---

### Click/Agenda Rate (% que hace clic o agenda)
```
=((COUNTIF(G2:G1000,"SÍ")+COUNTIF(H2:H1000,"SÍ"))/COUNTIF(E2:E1000,"SÍ"))*100
```
**Cálculo:** (Clicks + Agendas) / Respuestas × 100

**Meta:** 35-60%

---

### Show Rate (% que asiste)
```
=(COUNTIF(I2:I1000,"SÍ")/COUNTIF(H2:H1000,"SÍ"))*100
```
**Cálculo:** Asistencias / Agendas × 100

**Meta:** 35-65% (con recordatorios)

---

### Conversión a Venta (% que compra)
```
=(COUNTIF(L2:L1000,"SÍ")/COUNTIF(I2:I1000,"SÍ"))*100
```
**Cálculo:** Ventas / Asistencias × 100

**Meta:** 20-35%

---

### Opt-Out Rate (% que se da de baja)
```
=(COUNTIF(N2:N1000,"STOP")/COUNTA(A2:A1000))*100
```
**Cálculo:** Opt-outs / Total enviados × 100

**Meta:** <2% (mantener bajo)

---

## 📈 MÉTRICAS POR VARIANTE

### Reply Rate por Variante
```
=AVERAGEIF(C2:C1000,"DM1-A3",IF(E2:E1000="SÍ",1,0)*100)
```

**Para cada variante:**
1. Filtra por "Variante Usada"
2. Aplica fórmula arriba
3. Compara variantes

---

### Mejor Variante (Reply Rate más alto)
```
=INDEX(C2:C1000,MATCH(MAX(COUNTIFS(C2:C1000,C2:C1000,E2:E1000,"SÍ")/COUNTIF(C2:C1000,C2:C1000)),COUNTIFS(C2:C1000,C2:C1000,E2:E1000,"SÍ")/COUNTIF(C2:C1000,C2:C1000),0))
```

---

## 🎯 MÉTRICAS POR NICHO

### Reply Rate por Nicho
```
=AVERAGEIF(J2:J1000,"ecommerce",IF(E2:E1000="SÍ",1,0)*100)
```

**Repite para:**
- ecommerce
- B2B
- real_estate
- educacion
- agencias
- consultoria

---

### Mejor Nicho (Conversión más alta)
```
=INDEX(J2:J1000,MATCH(MAX(COUNTIFS(J2:J1000,J2:J1000,L2:L1000,"SÍ")/COUNTIF(J2:J1000,J2:J1000)),COUNTIFS(J2:J1000,J2:J1000,L2:L1000,"SÍ")/COUNTIF(J2:J1000,J2:J1000),0))
```

---

## ⏰ MÉTRICAS POR TIMING

### Reply Rate por Hora de Envío
```
=AVERAGEIF(F2:F1000,"09:00",IF(E2:E1000="SÍ",1,0)*100)
```

**Horarios a testear:**
- 08:30
- 09:00
- 09:30
- 10:00
- 13:00
- 14:00
- 18:30
- 19:00
- 20:00

---

### Mejor Hora (Reply Rate más alto)
```
=INDEX(F2:F1000,MATCH(MAX(COUNTIFS(F2:F1000,F2:F1000,E2:E1000,"SÍ")/COUNTIF(F2:F1000,F2:F1000)),COUNTIFS(F2:F1000,F2:F1000,E2:E1000,"SÍ")/COUNTIF(F2:F1000,F2:F1000),0))
```

---

## 💰 ROI Y REVENUE

### Revenue Total
```
=SUMIF(L2:L1000,"SÍ",{precio_por_venta})
```
*Nota: Necesitas columna de "Precio Venta" para calcular*

---

### Revenue por Oferta
```
=SUMIFS({precio_columna},D2:D1000,"Curso",L2:L1000,"SÍ")
```

**Repite para:**
- Curso
- SaaS
- IA Bulk

---

### CAC (Costo por Adquisición)
```
={costo_marketing_total}/COUNTIF(L2:L1000,"SÍ")
```
*Asumiendo costo fijo de marketing*

---

## 📊 DASHBOARD VISUAL (Configurar)

### Crear gráficos automáticos:

1. **Reply Rate Over Time**
   - Eje X: Fecha Envío
   - Eje Y: Reply Rate %
   - Tipo: Línea

2. **Reply Rate por Variante**
   - Eje X: Variante Usada
   - Eje Y: Reply Rate %
   - Tipo: Barras

3. **Show Rate por Oferta**
   - Eje X: Oferta
   - Eje Y: Show Rate %
   - Tipo: Barras

4. **Conversión Funnel**
   - Pasos: Enviados → Respuestas → Agendas → Asistencias → Ventas
   - Tipo: Funnel/Embudo

---

## ✅ CHECKLIST CONFIGURACIÓN

1. [ ] Importar `KPIs_Dashboard_Template.csv`
2. [ ] Agregar fórmulas arriba en nuevas columnas
3. [ ] Configurar gráficos automáticos
4. [ ] Filtrar por fecha (últimos 30 días)
5. [ ] Crear vista resumen con métricas clave

---

## 🎯 MÉTRICAS OBJETIVO (Benchmarks)

| Métrica | Bajo | Bueno | Excelente |
|---------|------|-------|-----------|
| Reply Rate | <15% | 18-30% | 25-35% |
| Click/Agenda | <30% | 35-55% | 50-65% |
| Show Rate | <25% | 35-50% | 45-65% |
| Conversión | <15% | 20-30% | 25-40% |
| Opt-Out | >3% | 1-2% | <1% |

---

**Importa CSV → Aplica fórmulas → Visualiza resultados.** 📊




