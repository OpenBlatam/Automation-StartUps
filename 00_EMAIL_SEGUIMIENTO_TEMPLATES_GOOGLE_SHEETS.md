# 📊 Templates de Google Sheets para Tracking

## 🎯 Dashboard Principal de Emails

### Estructura de la Hoja:

**Hoja 1: RESUMEN**
```
┌─────────────────────────────────────────────────────────┐
│  DASHBOARD DE EMAILS DE SEGUIMIENTO                     │
│  Última actualización: {fecha}                          │
├─────────────────────────────────────────────────────────┤
│  MÉTRICAS GENERALES:                                    │
│  • Total Prospectos: 500                               │
│  • Emails Enviados: 1,500                               │
│  • Open Rate Promedio: 45%                             │
│  • CTR Promedio: 22%                                    │
│  • Conversión Promedio: 15%                            │
│  • Revenue Generado: $37,500                           │
│  • CAC: $83                                             │
├─────────────────────────────────────────────────────────┤
│  POR EMAIL:                                             │
│  Email #1 (ROI):                                        │
│    • Enviados: 500                                      │
│    • Opens: 225 (45%)                                   │
│    • Clicks: 45 (20%)                                    │
│    • Conversiones: 23 (10%)                             │
│    • Revenue: $11,500                                   │
│                                                          │
│  Email #2 (Social Proof):                                │
│    • Enviados: 375                                      │
│    • Opens: 169 (45%)                                   │
│    • Clicks: 38 (22%)                                    │
│    • Conversiones: 27 (16%)                             │
│    • Revenue: $13,500                                   │
│                                                          │
│  Email #3 (Urgencia):                                   │
│    • Enviados: 300                                      │
│    • Opens: 141 (47%)                                   │
│    • Clicks: 35 (25%)                                    │
│    • Conversiones: 25 (18%)                             │
│    • Revenue: $12,500                                   │
└─────────────────────────────────────────────────────────┘
```

**Fórmulas para RESULTADO automático:**

```excel
B5: =COUNTIF(Prospectos!A:A, "<>")
B6: =SUM(Hoja2!E:E)
B7: =SUM(Hoja2!F:F)/SUM(Hoja2!E:E)
B8: =SUM(Hoja2!G:G)/SUM(Hoja2!F:F)
B9: =SUM(Hoja2!H:H)/SUM(Hoja2!F:F)
B10: =SUM(Hoja2!I:I)
B11: =B10/SUM(Hoja2!H:H)
```

---

## 📋 Hoja 2: Tracking de Prospectos

### Columnas:

| A | B | C | D | E | F | G | H | I | J |
|---|---||---||---||---||---||---||---|
| **Prospecto** | **Email** | **Industria** | **Rol** | **Email #1** | **Email #2** | **Email #3** | **Estado** | **Revenue** | **Notas** |
| Juan Pérez | juan@... | Marketing | Director | Enviado | Abierto | Click | Caliente | $500 | Interesado |
| María García | maria@... | Consultoría | Freelancer | Enviado | - | - | Tibio | - | Sin respuesta |

**Fórmulas:**

```excel
H2: =IF(G2="Click", "Caliente", IF(F2="Abierto", "Tibio", IF(E2="Enviado", "Frío", "Sin contacto")))
I2: =IF(H2="Caliente", 500, 0)
```

---

## 📊 Hoja 3: Análisis por Email

### Estructura:

| A | B | C | D | E | F | G | H |
|---||---||---||---||---||---||---|
| **Fecha** | **Email** | **Enviados** | **Opens** | **Clicks** | **Conversiones** | **Open Rate** | **CTR** |
| 2024-01-15 | Email #1 | 50 | 23 | 5 | 2 | =D2/C2 | =E2/D2 |
| 2024-01-16 | Email #1 | 50 | 22 | 4 | 2 | =D3/C3 | =E3/D3 |

**Gráficos Automáticos:**

1. **Gráfico de Línea:** Open Rate por día
2. **Gráfico de Barras:** CTR por email
3. **Gráfico de Torta:** Conversiones por email

---

## 📈 Hoja 4: Análisis de Performance

### Métricas Calculadas:

| A | B | C | D |
|---||---||---||---|
| **Métrica** | **Email #1** | **Email #2** | **Email #3** |
| Open Rate | =SUMIF(Hoja3!B:B, "Email #1", Hoja3!D:D)/SUMIF(Hoja3!B:B, "Email #1", Hoja3!C:C) | ... | ... |
| CTR | =SUMIF(Hoja3!B:B, "Email #1", Hoja3!E:E)/SUMIF(Hoja3!B:B, "Email #1", Hoja3!D:D) | ... | ... |
| Conversión | =SUMIF(Hoja3!B:B, "Email #1", Hoja3!F:F)/SUMIF(Hoja3!B:B, "Email #1", Hoja3!D:D) | ... | ... |
| Revenue Total | =SUMIF(Hoja2!H:H, "Caliente", Hoja2!I:I) | ... | ... |

---

## 🎯 Hoja 5: Segmentación

### Por Industria:

| A | B | C | D | E |
|---||---||---||---|
| **Industria** | **Total** | **Opens** | **Clicks** | **Conversiones** |
| Marketing | =COUNTIF(Hoja2!C:C, "Marketing") | =COUNTIFS(Hoja2!C:C, "Marketing", Hoja2!F:F, "Abierto") | ... | ... |
| Consultoría | ... | ... | ... | ... |

---

## 📋 Template Completo (Copy-Paste Ready):

### Crear en Google Sheets:

1. **Hoja 1: RESUMEN**
   - Título: "Dashboard de Emails"
   - Fila 1: Títulos
   - Fila 2-15: Métricas con fórmulas

2. **Hoja 2: PROSPECTOS**
   - Columna A: Nombre
   - Columna B: Email
   - Columna C: Industria
   - Columna D: Rol
   - Columna E: Email #1 (Enviado/Abierto/Click)
   - Columna F: Email #2
   - Columna G: Email #3
   - Columna H: Estado (Fórmula automática)
   - Columna I: Revenue (Fórmula automática)

3. **Hoja 3: TRACKING DIARIO**
   - Fecha, Email, Enviados, Opens, Clicks, Conversiones

4. **Hoja 4: PERFORMANCE**
   - Métricas calculadas automáticamente

5. **Hoja 5: SEGMENTACIÓN**
   - Análisis por industria, rol, etc.

---

## 🔗 Enlace a Template (Google Sheets):

**Para usar este template:**
1. Copiar el template a tu Google Sheets
2. Configurar fórmulas según tus datos
3. Actualizar manualmente o con automatización

**Template Base:** [Crear copia aquí]

---

**Templates de Google Sheets listos para tracking completo.** 📊

