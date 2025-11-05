# 📄 Google Sheets Implementation Guide

## 📥 Importar Plantillas (3 archivos)

1) Archivo → Importar → Subir
2) Importa en hojas separadas:
   - Hoja `Datos` → `./datos_template.csv`
   - Hoja `Resumen` → `./resumen_template.csv`
   - Hoja `Config` → `./config_template.csv`
3) Establece formato de fecha/hora como ISO o local

---

## 🔢 Fórmulas Útiles (pegar en hoja `Resumen` o nueva `Metrics`)

- Reply Rate DM (últimos 7 días):
```
=COUNTIF(FILTER(Datos!I:I, Datos!H:H>=TODAY()-7), ">"&"") / COUNTIF(Datos!H:H, ">="&TODAY()-7)
```

- DM→Demo (14 días ventana):
```
=COUNTA(UNIQUE(FILTER(Datos!A:A, Datos!K:K<>""))) / COUNTA(UNIQUE(FILTER(Datos!A:A, Datos!H:H>=TODAY()-14)))
```

- No-show rate (30 días):
```
=IFERROR(Resumen!B5 / (Resumen!B5 + Resumen!B6), 0)
```
(Ajusta rangos según tus columnas de asistencia/no-show)

- ROI mensual estimado:
```
=SUM(Resumen!B:B)  
```
(Usa suma de ahorro + ingresos de tu bloque de ROI)

---

## 📊 Gráficos Recomendados

- Serie temporal reply rate (7/14/30 días)
- Barras: conversión por canal/variante
- Tablas: top hooks/CTAs
- Indicadores: no-show y ROI

---

## ⏰ Reglas/Alertas (con Apps Script o Notificaciones)

- Si `reply_rate_dm_7d < Config!reply_alert_threshold` → enviar email/Slack
- Si `no_show_rate_30d > Config!no_show_alert_threshold` → crear tarea
- Si hoy coincide con `reengagement_days` → lista de leads a reactivar

---

## 🔗 Conexiones (Opcional)

- ImportRange desde CRM export
- Google Apps Script para refresco diario
- Conector a Looker Studio para dashboards

---

**FIN DEL DOCUMENTO**



