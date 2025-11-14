---
title: "Dm Linkedin Sheets Template Formulas"
category: "01_marketing"
tags: ["business", "marketing", "template"]
created: "2025-10-29"
path: "01_marketing/Templates/dm_linkedin_sheets_template_formulas.md"
---

# 📊 Plantilla Google Sheets con Fórmulas Automáticas

## 📋 ESTRUCTURA DE LA HOJA

### Columna A: fecha_envio
**Formato:** Fecha (DD/MM/YYYY)
**Ejemplo:** 15/01/2024

### Columna B: nombre
**Formato:** Texto
**Ejemplo:** María González

### Columna C: empresa
**Formato:** Texto
**Ejemplo:** TechStart

### Columna D: variante
**Formato:** Texto
**Ejemplo:** Problema_A, Resultado_B, SocialProof_C

### Columna E: utm_campaign
**Formato:** Texto
**Ejemplo:** curso_ia_q4, saas_trial_q1

### Columna F: respondio
**Formato:** Sí/No (dropdown)
**Valores:** Sí, No, Pendiente

### Columna G: clic
**Formato:** Sí/No (dropdown)
**Valores:** Sí, No

### Columna H: convirtio
**Formato:** Sí/No (dropdown)
**Valores:** Sí, No

### Columna I: tiempo_respuesta_horas
**Formato:** Número
**Ejemplo:** 3.5 (3 horas y media)

### Columna J: siguiente_paso
**Formato:** Texto
**Ejemplo:** Webinar registrado, Trial activo, Demo agendada

### Columna K: notas
**Formato:** Texto
**Ejemplo:** Interesado pero necesita aprobación de manager

---

## 🧮 FÓRMULAS AUTOMÁTICAS

### Hoja 2: Dashboard de Resumen

#### Celda B2: Total Enviados
```
=COUNTA(Sheet1!B:B)-1
```
(Excluye encabezado)

---

#### Celda B3: Total Respuestas
```
=COUNTIF(Sheet1!F:F,"Sí")
```

---

#### Celda B4: Tasa de Respuesta (%)
```
=IF(B2>0, B3/B2*100, 0)
```
Formato: Porcentaje con 1 decimal

---

#### Celda B5: Total Clics
```
=COUNTIF(Sheet1!G:G,"Sí")
```

---

#### Celda B6: CTR (Click-Through Rate %)
```
=IF(B2>0, B5/B2*100, 0)
```
Formato: Porcentaje con 1 decimal

---

#### Celda B7: Total Conversiones
```
=COUNTIF(Sheet1!H:H,"Sí")
```

---

#### Celda B8: Tasa de Conversión (%)
```
=IF(B2>0, B7/B2*100, 0)
```
Formato: Porcentaje con 1 decimal

---

#### Celda B9: Reply-to-Conversion (%)
```
=IF(B3>0, B7/B3*100, 0)
```
% de respuestas que se convierten
Formato: Porcentaje con 1 decimal

---

#### Celda B10: Tiempo Promedio de Respuesta (horas)
```
=AVERAGE(Sheet1!I:I)
```
Formato: Número con 1 decimal

---

### Por Variante (Tabla Dinámica)

#### Fila 12-15: Análisis por Variante

**Columna A (A12-A15):** Variantes únicas
```
=UNIQUE(Sheet1!D2:D)
```

**Columna B (B12-B15):** Enviados por variante
```
=COUNTIF(Sheet1!D:D, A12)
```

**Columna C (C12-C15):** Respuestas por variante
```
=COUNTIFS(Sheet1!D:D, A12, Sheet1!F:F, "Sí")
```

**Columna D (D12-D15):** Tasa de respuesta por variante (%)
```
=IF(B12>0, C12/B12*100, 0)
```

**Columna E (E12-E15):** Conversiones por variante
```
=COUNTIFS(Sheet1!D:D, A12, Sheet1!H:H, "Sí")
```

**Columna F (F12-F15):** Tasa de conversión por variante (%)
```
=IF(B12>0, E12/B12*100, 0)
```

---

### Por Campaña (Tabla Dinámica)

#### Fila 18-21: Análisis por Campaña

**Columna A (A18-A21):** Campañas únicas
```
=UNIQUE(Sheet1!E2:E)
```

**Columna B (B18-B21):** Misma estructura que por variante
(Copiar fórmulas B12-F15 y cambiar referencia de D a E)

---

### Análisis de Timing

#### Celda D2: Total por Día de Semana
Usar Pivot Table o fórmula:
```
=COUNTIFS(Sheet1!A:A, ">=Lunes", Sheet1!A:A, "<Martes")
```

#### Celda E2: Mejor Día (automático)
```
=INDEX({"Lunes";"Martes";"Miércoles";"Jueves";"Viernes"}, MATCH(MAX(Tasas_por_dia), Tasas_por_dia, 0))
```

---

## 📊 GRÁFICOS RECOMENDADOS

### Gráfico 1: Tasa de Respuesta por Variante
- Tipo: Barras
- Datos: Columna D (Tasa respuesta)
- Etiquetas: Columna A (Variante)

### Gráfico 2: Tendencia Semanal
- Tipo: Línea
- Datos: Tasa de respuesta por semana
- Eje X: Semanas
- Eje Y: % Respuesta

### Gráfico 3: Funel de Conversión
- Tipo: Embudo
- Pasos: Enviados → Respuestas → Clics → Conversiones

---

## 🔄 ACTUALIZACIÓN AUTOMÁTICA

### Filtros Recomendados:
1. **Por Variante:** Filtrar columna D
2. **Por Estado:** Filtrar columna F (Respondió)
3. **Por Semana:** Agregar columna de semana, filtrar

### Actualización Semanal:
1. Agregar nuevos datos a Sheet1
2. Dashboard se actualiza automáticamente
3. Revisar gráficos para insights visuales

---

## 💡 FÓRMULAS AVANZADAS (Opcional)

### Identificar Mejor Variante Automáticamente
```
=INDEX(A12:A15, MATCH(MAX(D12:D15), D12:D15, 0))
```
(Devuelve nombre de variante con mejor tasa de respuesta)

---

### Calcular ROI Simple (si tienes datos de ingresos)
Agregar columna: `valor_conversion` (número)
```
ROI = SUM(conversiones * valor_conversion) / (envíos * costo_por_envio)
```

---

### Señales de Alerta Automáticas
**Si tasa de bloqueo > 2%:**
```
=IF(COUNTIF(Sheet1!K:K, "Bloqueado")/B2>0.02, "ALERTA: Bloqueo alto", "OK")
```

**Si tasa de respuesta < 10%:**
```
=IF(B4<10, "ALERTA: Respuesta baja", "OK")
```

---

## 📋 INSTRUCCIONES DE USO

1. **Crea hoja nueva en Google Sheets**
2. **Copia estructura de columnas** (A-K)
3. **Agrega fórmulas** en Hoja 2 (Dashboard)
4. **Importa datos** desde CSV o escribe manualmente
5. **Configura gráficos** según recomendaciones
6. **Actualiza semanalmente** con nuevos datos

---

## ✅ CHECKLIST DE CONFIGURACIÓN

- [ ] Estructura de columnas creada (Sheet1)
- [ ] Dashboard con fórmulas configurado (Sheet2)
- [ ] Gráficos básicos creados
- [ ] Filtros aplicados en Sheet1
- [ ] Formato condicional (verde/rojo según tasas)
- [ ] Permisos configurados (solo lectura para equipo)

---

## 🎯 MÉTRICAS ADICIONALES (Avanzado)

### LTV Simple (si trackeas valor por cliente)
Agregar columna: `valor_cliente` (número)
```
LTV_promedio = AVERAGE(valor_cliente para conversiones)
```

### CAC (Costo de Adquisición)
```
CAC = (Total_enviados * Costo_por_envio) / Total_conversiones
```

### LTV:CAC Ratio
```
Ratio = LTV_promedio / CAC
```
(Objetivo: >3:1)

