---
title: "Dm Linkedin Automation Guide"
category: "01_marketing"
tags: ["business", "guide", "marketing"]
created: "2025-10-29"
path: "01_marketing/Guides/dm_linkedin_automation_guide.md"
---

# 🤖 Guía de Automatización Completa: LinkedIn DMs

## 📚 Scripts Disponibles

### 1. Generador con IA
**Archivo:** `Scripts/dm_linkedin_ai_generator.js`
```bash
node Scripts/dm_linkedin_ai_generator.js
```
- Genera 3 variantes personalizadas por prospecto
- Integración con OpenAI/Claude (requiere API key)
- Basado en contexto del prospecto (rol, industria, problema)

**Setup:**
```bash
export OPENAI_API_KEY="tu-key"
# o
export CLAUDE_API_KEY="tu-key"
export AI_MODEL="gpt-4"  # o "claude-3-opus"
```

---

### 2. Dashboard de Métricas
**Archivo:** `Scripts/dm_linkedin_dashboard_generator.js`
```bash
node Scripts/dm_linkedin_dashboard_generator.js
```
- Genera dashboard HTML interactivo desde logs
- Métricas por campaña y variante
- Output: `Reports/dm_linkedin_dashboard.html`

**Métricas mostradas:**
- Total intentos, enviados, errores
- Tasa de éxito por campaña
- Performance de top 10 variantes

---

### 3. Gestor de Cadencias
**Archivo:** `Scripts/dm_linkedin_cadence_manager.js`
```bash
node Scripts/dm_linkedin_cadence_manager.js
```
- Calcula timing óptimo para follow-ups
- Soporta cadencias: warm, cold, objection
- Output: `Data_Files/dm_linkedin_next_followups.csv`

**Cadencias predefinidas:**
- **Warm:** D0 → D2 → D5 → D10
- **Cold:** D0 → D3 → D7 → D14 → D21
- **Objection:** D0 → D5 → D12

**Personalización:**
Edita `Data_Files/dm_linkedin_cadences.json`:
```json
{
  "warm": { "d0": "initial", "d2": "followup1", "d5": "followup2" },
  "cold": { "d0": "initial", "d3": "followup1", "d7": "followup2" }
}
```

---

### 4. Optimizador A/B Automático
**Archivo:** `Scripts/dm_linkedin_ab_optimizer.js`
```bash
node Scripts/dm_linkedin_ab_optimizer.js
```
- Analiza performance de variantes
- Identifica winners estadísticamente significativos
- Recomendaciones: scale_winner, test_more, keep_testing

**Requisitos:**
- `Data_Files/dm_linkedin_logs.csv` (envíos)
- `Data_Files/dm_linkedin_responses.csv` (respuestas/clicks/conversiones)

**Formato responses.csv:**
```csv
recipient,responded,clicked,converted
https://linkedin.com/in/user1,true,true,false
https://linkedin.com/in/user2,true,false,false
```

**Output:** `Reports/dm_linkedin_ab_results.json`

---

### 5. Reporte Ejecutivo
**Archivo:** `Scripts/dm_linkedin_executive_report.js`
```bash
node Scripts/dm_linkedin_executive_report.js [periodo_dias]
```
- Genera reporte HTML profesional con KPIs
- Métricas por campaña y insights automáticos
- Output: `Reports/dm_linkedin_executive_report.html`

**Ejemplo:**
```bash
node Scripts/dm_linkedin_executive_report.js 30  # últimos 30 días
```

---

### 6. Predictor de Respuesta (ML)
**Archivo:** `Scripts/dm_linkedin_response_predictor.js`
```bash
node Scripts/dm_linkedin_response_predictor.js
```
- Usa regresión logística para predecir probabilidad de respuesta
- Clasifica prospects por score de respuesta esperada
- Output: `Data_Files/dm_linkedin_predictions.csv`

**Mínimo 50 muestras históricas requeridas para entrenar modelo.**

---

### 7. Integración Webhook
**Archivo:** `Scripts/dm_linkedin_webhook_integration.js`
```bash
node Scripts/dm_linkedin_webhook_integration.js
```
- Servidor HTTP que recibe webhooks de LinkedIn/CRM
- Actualiza automáticamente responses.csv
- Puerto configurable (default: 3000)

**Setup:**
```bash
export WEBHOOK_SECRET="tu-secret"
export WEBHOOK_PORT=3000
node Scripts/dm_linkedin_webhook_integration.js
```

**Formato webhook:**
```json
{
  "recipient": "https://linkedin.com/in/user",
  "responded": true,
  "clicked": true,
  "converted": false,
  "secret": "tu-secret"
}
```

---

### 8. Orchestrator Principal
**Archivo:** `Scripts/dm_linkedin_orchestrator.js`
```bash
node Scripts/dm_linkedin_orchestrator.js [daily|weekly|full] [--dry-run]
```
- Coordina todos los scripts en un flujo automatizado
- **daily:** Pre-send + dashboard + cadence manager
- **weekly:** Pre-send + scoring + A/B + report + predictor + CRM export
- **full:** Todos los scripts en secuencia

**Ejemplo cron diario:**
```bash
0 18 * * * cd /path/to/scripts && node dm_linkedin_orchestrator.js daily
```

---

## 🔄 Flujo de Automatización Completo

### Día a Día (Automático)
```bash
# 1. Generación de variantes con IA (opcional)
node Scripts/dm_linkedin_ai_generator.js

# 2. Envío (usando sender_node.js o Apps Script)
# ... (automático con throttling)

# 3. Dashboard diario
node Scripts/dm_linkedin_dashboard_generator.js
# → Abre Reports/dm_linkedin_dashboard.html en navegador
```

### Semanal (Análisis)
```bash
# 1. Export respuestas desde CRM → responses.csv

# 2. A/B Optimization
node Scripts/dm_linkedin_ab_optimizer.js
# → Revisa winners y recomendaciones

# 3. Cadence Manager
node Scripts/dm_linkedin_cadence_manager.js
# → Prioriza follow-ups por timing
```

---

## 📊 Integración con Otros Scripts

### Pipeline Completo (Manual)
```bash
# Pre-envío
node Scripts/dm_linkedin_recipients_cleaner.js
node Scripts/dm_linkedin_qa_pre_send.js

# Envío (con sender_node.js)
node Scripts/dm_linkedin_sender_node.js

# Post-envío diario
node Scripts/dm_linkedin_dashboard_generator.js
node Scripts/dm_linkedin_cadence_manager.js

# Post-envío semanal
node Scripts/dm_linkedin_score_from_logs.js
node Scripts/dm_linkedin_ab_optimizer.js
node Scripts/dm_linkedin_executive_report.js
node Scripts/dm_linkedin_response_predictor.js
node Scripts/dm_linkedin_export_crm.js
```

### Pipeline Automatizado (Orchestrator)
```bash
# Diario (18:00)
node Scripts/dm_linkedin_orchestrator.js daily

# Semanal (Lunes 9:00)
node Scripts/dm_linkedin_orchestrator.js weekly

# Completo (on-demand)
node Scripts/dm_linkedin_orchestrator.js full
```

---

## 🎯 Casos de Uso

### Caso 1: Generar Variantes para Nueva Campaña
```bash
# 1. Crea lista de prospectos (prospects.json)
# 2. Define info del producto (product.json)
# 3. Genera variantes
node Scripts/dm_linkedin_ai_generator.js
# 4. Revisa Data_Files/dm_linkedin_generated_variants.json
# 5. Importa a Variants sheet o JSON
```

### Caso 2: Analizar Performance Mensual
```bash
# 1. Export logs del mes
# 2. Export responses del CRM
# 3. Genera dashboard
node Scripts/dm_linkedin_dashboard_generator.js
# 4. Optimización A/B
node Scripts/dm_linkedin_ab_optimizer.js
# 5. Revisa winners y escala los mejores
```

### Caso 3: Priorizar Follow-ups Diarios
```bash
# 1. Ejecuta cadence manager
node Scripts/dm_linkedin_cadence_manager.js
# 2. Abre Data_Files/dm_linkedin_next_followups.csv
# 3. Filtra por days_until_next <= 1
# 4. Envía follow-ups priorizados
```

---

## ⚙️ Configuración Avanzada

### Variables de Entorno
```bash
# .env file
OPENAI_API_KEY=sk-...
CLAUDE_API_KEY=sk-ant-...
AI_MODEL=gpt-4

# A/B Optimizer
MIN_SAMPLES=20
CONFIDENCE_LEVEL=0.95
```

### Cron Jobs (Linux/Mac)
```bash
# Diario a las 18:00
0 18 * * * cd /path/to/scripts && node dm_linkedin_dashboard_generator.js

# Semanal (lunes a las 9:00)
0 9 * * 1 cd /path/to/scripts && node dm_linkedin_ab_optimizer.js
```

---

## 🚨 Troubleshooting

| Problema | Solución |
|----------|----------|
| AI Generator no genera | Verifica API key y cuota de API |
| Dashboard vacío | Verifica que logs.csv tenga datos |
| A/B sin winners | Aumenta minSamples o espera más envíos |
| Cadence manager no encuentra follow-ups | Verifica formato de timestamp en logs |

---

**📝 Nota:** Todos los scripts son modulares y pueden ejecutarse independientemente.

