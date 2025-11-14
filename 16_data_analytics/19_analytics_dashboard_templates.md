---
title: "19 Analytics Dashboard Templates"
category: "19_analytics_dashboard_templates.md"
tags: ["template"]
created: "2025-10-29"
path: "19_analytics_dashboard_templates.md"
---

# 📊 Analytics Dashboard Templates

## 📑 ÍNDICE

- [🎯 KPIs por Producto](#-kpis-por-producto)
- [📈 Dashboards Operativos (Diario/Semanal)](#-dashboards-operativos-diariosemanal)
- [🧠 Dashboards de Aprendizaje (A/B y Personalización)](#-dashboards-de-aprendizaje-ab-y-personalización)
- [🧩 Esquemas de Datos y SQL](#-esquemas-de-datos-y-sql)
- [📎 Plantillas en Google Sheets / Looker / Data Studio](#-plantillas-en-google-sheets--looker--data-studio)
- [✅ QA de Datos y Alertas](#-qa-de-datos-y-alertas)

---

## 🎯 KPIs POR PRODUCTO

### Curso IA + Webinars
- **Response Rate DM** = Respuestas / DMs
- **Show-up Rate Demo** = Asistencias / Demos agendadas
- **Completion Rate** = Alumnos completados / Alumnos inscritos
- **Revenue por Webinar** = Ingresos / Webinar
- **Contenido Reutilizado** = Activos generados / Webinar

### SaaS IA Marketing
- **Reply Rate DM/Email**
- **Demo→Trial** y **Trial→Paid**
- **ROAS Protegido** = ROAS nuevo − ROAS base
- **CAC Reducido** = CAC base − CAC con IA
- **Tiempo Creativo Ahorrado** (h/mes)

### IA Bulk Documentos
- **Docs/mes** y **Tiempo/doc**
- **Throughput** = Docs entregados / semana
- **Win Rate propuestas**
- **Ahorro ($/mes)** = Horas ahorradas × $/hora
- **Ingresos adicionales ($/mes)**

---

## 📈 DASHBOARDS OPERATIVOS (Diario/Semanal)

### Diario (Operator)
- DMs enviados (por canal, variante, nivel de personalización)
- Respuestas (positivas, neutrales, negativas)
- Demos agendadas hoy / semana
- Alertas: caídas >30% vs media 7 días

### Semanal (Manager)
- Conversión por variante (A/B) y por industria
- Personalización vs conversión (niveles 1/2/3)
- Tasa de no-show y causas
- Ciclo de venta (días) por producto

Layout recomendado (4x2 widgets):
- Fila 1: KPIs generales | Conversión por canal
- Fila 2: A/B por hook | Personalización vs reply
- Fila 3: Pipeline por etapa | No-show + razones
- Fila 4: ROI semanal | Alertas/insights

---

## 🧠 DASHBOARDS DE APRENDIZAJE (A/B y Personalización)

- Rendimiento por Hook (Top 10)
- Rendimiento por CTA (2-horarios vs libre)
- Longitud del mensaje vs reply
- Uso de emojis vs reply (por canal)
- Personalización Nivel 1/2/3 vs reply y demos
- Cohortes por semana de contacto

---

## 🧩 ESQUEMAS DE DATOS Y SQL

### Esquema base (tablas)
- `messages(id, lead_id, channel, variant, personalization_level, sent_at, replied_at, reply_type)`
- `leads(id, company, industry, size, region, lead_score)`
- `meetings(id, lead_id, scheduled_at, attended, outcome)`
- `deals(id, lead_id, product, stage, amount, created_at, closed_won)`

### SQL: Reply Rate por variante
```sql
SELECT variant,
       COUNT(*) FILTER (WHERE replied_at IS NOT NULL) * 1.0 / COUNT(*) AS reply_rate
FROM messages
WHERE sent_at >= NOW() - INTERVAL '30 days'
GROUP BY variant
ORDER BY reply_rate DESC;
```

### SQL: Conversión DM→Demo por canal
```sql
SELECT m.channel,
       COUNT(DISTINCT mt.lead_id) * 1.0 / COUNT(DISTINCT m.lead_id) AS dm_to_demo
FROM messages m
LEFT JOIN meetings mt ON mt.lead_id = m.lead_id AND mt.scheduled_at::date BETWEEN m.sent_at::date AND m.sent_at::date + 14
WHERE m.sent_at >= NOW() - INTERVAL '30 days'
GROUP BY m.channel
ORDER BY dm_to_demo DESC;
```

### SQL: ROI mensual por producto
```sql
WITH ahorro AS (
  SELECT d.product,
         SUM(d.ahorro_mensual_usd) AS ahorro_usd,
         SUM(d.ingresos_mensuales_usd) AS ingresos_usd
  FROM deals d
  WHERE d.created_at >= date_trunc('month', NOW())
  GROUP BY d.product
)
SELECT product,
       (ahorro_usd + ingresos_usd) AS roi_mensual
FROM ahorro
ORDER BY roi_mensual DESC;
```

---

## 📎 PLANTILLAS EN GOOGLE SHEETS / LOOKER / DATA STUDIO

### Google Sheets (estructura)
- Hoja `Raw_Messages`: dump de mensajes
- Hoja `Metrics`: KPIs con fórmulas
- Hoja `Dashboards`: gráficos vinculados

Fórmulas útiles:
- Reply Rate: `=COUNTIF(Reply!B:B, ">0")/COUNTA(Sent!A:A)`
- No-show Rate: `=1 - (Asistencias / Agendadas)`
- ROI Mes: `=(Ahorro + Ingresos) - Costo`

### Looker/Data Studio (widgets)
- Scorecards: Reply, Demos, Win Rate
- Series: Conversión por canal/variante
- Tablas: Hooks top, CTAs top
- Filtros: Industria, tamaño, región, producto

---

## ✅ QA DE DATOS Y ALERTAS

### Recursos directos (Google Sheets)
- `panel_combinado.csv` — KPI combinado Sequences + ROI listo para importar
- `panel_combinado_guia.md` — Pasos para configurar tarjetas y gráficos

- Validaciones: duplicados, fechas, canal válido, reply_type válido
- Reglas: reply ≤ sent, demo ≤ reply, won ≤ demo
- Alertas (Slack/Email):
  - Reply Rate día < media 7d − 30%
  - No-show > 25%
  - 0 demos en 24h con >50 DMs
  - Caída ROAS >20% (marketing)

---

**FIN DEL DOCUMENTO**



