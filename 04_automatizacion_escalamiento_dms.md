---
title: "04 Automatizacion Escalamiento Dms"
category: "04_automatizacion_escalamiento_dms.md"
tags: []
created: "2025-10-29"
path: "04_automatizacion_escalamiento_dms.md"
---

# 🚀 Automatización y Escalamiento de DMs

## 📑 ÍNDICE

- [🔧 Herramientas de Automatización](#-herramientas-de-automatización)
- [📊 CRMs y Tracking](#-crms-y-tracking)
- [🔄 Workflows Completos](#-workflows-completos)
- [📈 KPIs de Escalamiento](#-kpis-de-escalamiento)
- [🤖 IA para Personalización](#-ia-para-personalización)
- [📅 Calendario de Escalamiento](#-calendario-de-escalamiento)
- [📋 Reportes y Dashboards](#-reportes-y-dashboards)

---

## 🔧 HERRAMIENTAS DE AUTOMATIZACIÓN

### Zapier/Make.com Workflows

#### Workflow 1: LinkedIn → CRM → DM
**Trigger:** Nueva conexión en LinkedIn
**Actions:**
1. Capturar perfil LinkedIn
2. Scoring automático (API de LinkedIn + datos públicos)
3. Si scoring ≥6: Agregar a lista "DM Inmediato"
4. Si scoring 4-5: Agregar a secuencia automatizada
5. Si scoring 0-3: Agregar a nurturing

**Configuración:**
```
Trigger: New LinkedIn Connection
→ Enrich Lead Data (Clearbit/Hunter.io)
→ Calculate Scoring (Custom Zapier Code)
→ Conditional Logic
  → If Score ≥6: Add to HubSpot "Hot Leads"
  → If Score 4-5: Add to Sequence "Warm Leads"
  → Else: Add to Nurturing "Cold Leads"
```

---

#### Workflow 2: Email Tracking → Follow-up Automático
**Trigger:** Email abierto pero no respondido
**Actions:**
1. Esperar 48 horas
2. Si aún no respondió: Enviar seguimiento automático
3. Si sigue sin responder: Esperar 7 días y enviar bump

**Configuración:**
```
Trigger: Email Opened (Mailchimp/SendGrid)
→ Wait 48 hours
→ Check if Replied (CRM lookup)
→ If No Reply: Send Follow-up Email (Template 1)
→ Wait 7 days
→ Check if Replied
→ If No Reply: Send Bump Email (Template 2)
```

---

#### Workflow 3: Respuesta Positiva → Calendar Booking
**Trigger:** Email/LinkedIn contiene palabras clave positivas
**Actions:**
1. Detectar intención (IA/NLP)
2. Extraer disponibilidad mencionada
3. Crear evento en calendario
4. Enviar confirmación con link de meeting

**Palabras clave positivas:**
- "Sí", "interesado", "me funciona", "perfecto", "síguenos hablando"
- "Demo", "audit", "sandbox", "calculadora"

---

### Herramientas Recomendadas

**Automatización:**
- Zapier (integraciones más amplias)
- Make.com (más flexible, mejor para workflows complejos)
- n8n (open-source, self-hosted)

**Tracking:**
- HubSpot (CRM completo, scoring automático)
- Salesforce (enterprise, más robusto)
- Pipedrive (sencillo, buen para SMBs)

**Personalización IA:**
- ChatGPT API (personalización de DMs)
- Claude API (análisis de perfiles)
- Jasper/Copy.ai (copywriting asistido)

**LinkedIn Automation:**
- LinkedIn Sales Navigator (nativo, seguro)
- Dux-Soup (automation avanzado, usar con cuidado)
- PhantomBuster (scraping y automation)

---

## 📊 CRMs Y TRACKING

### HubSpot Setup

#### Custom Properties

**Lead Scoring:**
- `lead_score` (Number, 0-10)
- `scoring_last_calculated` (Date)

**DM Tracking:**
- `dm_variant_used` (Single Select: A, B, C, D, E, F, G)
- `dm_sent_date` (Date)
- `dm_response_date` (Date)
- `dm_personalization_level` (Number: 1, 2, 3)
- `dm_response_status` (Single Select: No Response, Interested, Not Interested, Maybe Later)

**Industria/Segmento:**
- `industry` (Single Select)
- `stack_mentioned` (Text: Meta Ads, Google Ads, etc.)
- `document_type` (Text: Propuestas, Briefs, SOPs, etc.)
- `presupuesto_ads_estimado` (Number)

**Funnel:**
- `funnel_stage` (Single Select: Lead, DM Sent, Responded, Demo Scheduled, Demo Completed, Proposal Sent, Closed Won, Closed Lost)
- `next_follow_up_date` (Date)
- `last_interaction_type` (Single Select: DM, Email, Call, Meeting)

---

#### Workflows Automáticos

**Workflow 1: Scoring Automático**
```
Trigger: New contact created OR Property updated
Conditions:
  - Has LinkedIn profile
  - Industry identified
  - Stack mentioned OR Document type identified
Actions:
  - Calculate score (Custom Code)
  - Update lead_score property
  - Add to appropriate list based on score
```

**Workflow 2: DM Follow-up Automático**
```
Trigger: DM sent date = Today - 2 days
Conditions:
  - dm_response_status = No Response
Actions:
  - Send follow-up email (Template 1)
  - Update next_follow_up_date = Today + 7 days
```

**Workflow 3: Re-engagement (30 días)**
```
Trigger: Last interaction date = Today - 30 days
Conditions:
  - Funnel stage ≠ Closed Won/Lost
  - lead_score ≥ 4
Actions:
  - Send re-engagement email (Educational content)
  - Update last_interaction_type
```

---

### Salesforce Setup

**Custom Objects:**
- DM Campaign (registro de cada campaña de DMs)
- DM Variant Performance (tracking de variantes)

**Custom Fields en Lead/Contact:**
- Similar a HubSpot pero adaptado a estructura Salesforce

**Automation Rules:**
- Process Builder para scoring automático
- Flow para secuencias de seguimiento

---

## 🔄 WORKFLOWS COMPLETOS

### Workflow End-to-End: Lead → DM → Demo → Cierre

**Paso 1: Lead Capture**
- LinkedIn connection o email signup
- Enrich data (Clearbit/Hunter.io)
- Calculate scoring

**Paso 2: Scoring y Routing**
- Score ≥6: DM personalizado inmediato (humano)
- Score 4-5: Secuencia automatizada (DM Template + IA)
- Score 0-3: Nurturing (hooks avanzados en LinkedIn)

**Paso 3: DM Envío**
- Personalización IA (ChatGPT API)
- Selección de variante (matriz de decisión automatizada)
- Envío manual o automatizado (según score)

**Paso 4: Tracking**
- Registro en CRM
- Follow-up programado automáticamente

**Paso 5: Respuesta Handling**
- Detección de intención (IA)
- Routing según respuesta:
  - Interesado → Calendar booking automático
  - "Mándame info" → Enviar one-pager + ROI calculator
  - "No ahora" → Programar re-engagement

**Paso 6: Demo/Meeting**
- Preparación automática (materiales según producto)
- Post-meeting: Follow-up automatizado con next steps

---

## 📈 KPIS DE ESCALAMIENTO

### Por Etapa del Proceso

**Manual (Semanas 1-2):**
- DMs/semana: 10-20
- Tasa respuesta: 15-20%
- Tiempo/DM: 15-20 min
- Conversión DM → Demo: 5-8%

**Semi-automático (Semanas 3-4):**
- DMs/semana: 20-50
- Tasa respuesta: 20-25%
- Tiempo/DM: 5-10 min
- Conversión DM → Demo: 8-12%

**Automatizado (Semanas 5+):**
- DMs/semana: 100+
- Tasa respuesta: 25-30%
- Tiempo/DM: 1-2 min (solo revisión)
- Conversión DM → Demo: 12-18%

---

### Métricas de Eficiencia

**Throughput:**
- Leads procesados/semana
- DMs enviados/semana
- Demos agendados/semana

**Calidad:**
- Tasa de respuesta por variante
- Scoring promedio de leads que responden
- Conversión por variante

**ROI del Proceso:**
- Costo hora × tiempo invertido
- Ingresos generados por DMs
- ROI del proceso de outreach

---

## 🤖 IA PARA PERSONALIZACIÓN

### Prompts para ChatGPT/Claude

#### Prompt 1: Investigación de Lead
```
Analiza este perfil de LinkedIn y extrae:

1. Industria/segmento
2. Stack tecnológico mencionado (si aplica)
3. Pain points probables (basado en posts/contenido)
4. Métricas públicas relevantes de su industria
5. Tipo de cliente ideal (B2B, B2C, tamaño)
6. Scoring estimado (1-10)

Perfil: [PEGAR PERFIL LINKEDIN O DATOS]
```

---

#### Prompt 2: Generación de DM Personalizado
```
Genera un DM personalizado para [NOMBRE] de [EMPRESA] usando:

Variante: [A/B/C/D/E/F/G según matriz]
Industria: [INDUSTRIA]
Stack mencionado: [STACK o tipo documento]
Pain point identificado: [PAIN POINT]
Caso de éxito relevante: [CASO]
Producto: [PRODUCTO]
CTA: [día/hora 1] o [día/hora 2]

Mantén:
- Longitud: [X] palabras
- Tono: [PROFESIONAL/CERCANO]
- Personalización nivel: [2/3]
```

---

#### Prompt 3: Análisis de Respuesta y Routing
```
Analiza esta respuesta a un DM y determina:

1. Intención (Alta/Media/Baja/Negativa)
2. Objeción principal (si hay)
3. Next step recomendado
4. Template de respuesta apropiado

Respuesta del lead: [PEGAR RESPUESTA]

Contexto:
- DM original: [VARIANTE X]
- Producto: [PRODUCTO]
- Industria: [INDUSTRIA]
```

---

### Integración con APIs

**OpenAI API (ChatGPT):**
```python
import openai

def generate_personalized_dm(lead_data, variant):
    prompt = f"""
    Genera un DM personalizado para {lead_data['name']} de {lead_data['company']}...
    [PROMPT COMPLETO]
    """
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content
```

**Claude API (Anthropic):**
```python
import anthropic

def analyze_lead_profile(profile_data):
    prompt = f"""
    Analiza este perfil y extrae información relevante...
    [PROMPT COMPLETO]
    """
    
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-3-opus-20240229",
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.content
```

---

## 📅 CALENDARIO DE ESCALAMIENTO

### Mes 1: Manual + Aprendizaje

**Semana 1-2:**
- 10-15 DMs/semana manuales
- Tracking en spreadsheet simple
- Testing de variantes A, B, C
- Identificar mejor variante

**Semana 3-4:**
- 15-20 DMs/semana
- Implementar scoring básico manual
- Comenzar a usar templates
- Documentar aprendizajes

**Objetivo:** Validar que el proceso funciona antes de automatizar.

---

### Mes 2: Semi-automatización

**Semana 1-2:**
- Setup CRM (HubSpot o similar)
- Implementar scoring automático parcial
- Zapier workflow básico (LinkedIn → CRM)
- 20-30 DMs/semana

**Semana 3-4:**
- IA para personalización nivel 1-2
- Secuencias de seguimiento automatizadas
- 30-50 DMs/semana
- A/B testing de variantes

**Objetivo:** Escalar throughput sin perder calidad.

---

### Mes 3: Automatización Completa

**Semana 1-2:**
- Workflows completos end-to-end
- IA avanzada para personalización nivel 3
- Scoring completamente automático
- 50-100 DMs/semana

**Semana 3-4:**
- Optimización continua basada en datos
- A/B testing automatizado
- Re-engagement automatizado
- 100+ DMs/semana

**Objetivo:** Máximo throughput con calidad mantenida.

---

## 📋 REPORTES Y DASHBOARDS

### Dashboard Semanal

**Métricas Principales:**
- DMs enviados (vs semana anterior)
- Tasa de respuesta (vs semana anterior)
- Mejor variante (conversión)
- Scoring promedio de leads que responden
- Demos agendados
- ROI estimado

**Gráficos:**
- Tasa de respuesta por variante
- Conversión por scoring inicial
- Timeline: DM → Respuesta → Demo

---

### Reporte Mensual

**Sección 1: Performance General**
- Total DMs enviados
- Tasa de respuesta promedio
- Tasa de conversión DM → Demo
- ROI del proceso

**Sección 2: Optimización**
- Variante mejor performer
- Variante que necesita optimización
- Mejor horario de envío
- Mejor día de la semana

**Sección 3: Aprendizajes**
- Insights clave
- Qué funciona vs qué no
- Recomendaciones para próximo mes

**Sección 4: Escalamiento**
- Throughput actual vs objetivo
- Eficiencia (tiempo/DM)
- Próximos pasos de automatización

---

### Template de Reporte (Google Sheets/Notion)

```
SEMANA [X]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 MÉTRICAS PRINCIPALES
- DMs enviados: [X] (+[Y]% vs semana anterior)
- Tasa respuesta: [Z]% (+[A]% vs semana anterior)
- Demos agendados: [B]
- ROI estimado: $[C]

🏆 MEJOR PERFORMER
- Variante: [X]
- Tasa respuesta: [Y]%
- Conversión: [Z]%

📈 POR SCORING
- Leads 8-10: [X] DMs, [Y]% respuesta
- Leads 6-7: [A] DMs, [B]% respuesta
- Leads 4-5: [C] DMs, [D]% respuesta

💡 INSIGHTS
1. [Insight 1]
2. [Insight 2]
3. [Insight 3]

🎯 PRÓXIMOS PASOS
1. [Acción 1]
2. [Acción 2]
```

---

## ✅ CERTIFICACIÓN DE ESCALAMIENTO

### Nivel 1: Básico (Manual)
- ✅ 15+ DMs/semana manuales
- ✅ Scoring manual consistente
- ✅ Tasa respuesta ≥15%
- ✅ Tracking básico en spreadsheet

### Nivel 2: Intermedio (Semi-automático)
- ✅ 30+ DMs/semana
- ✅ CRM configurado y usado
- ✅ Scoring automático parcial
- ✅ Tasa respuesta ≥20%
- ✅ Secuencias de seguimiento automatizadas

### Nivel 3: Avanzado (Automatizado)
- ✅ 100+ DMs/semana
- ✅ Workflows end-to-end automatizados
- ✅ IA para personalización
- ✅ Tasa respuesta ≥25%
- ✅ A/B testing continuo
- ✅ ROI positivo del proceso

---

**FIN DEL DOCUMENTO**
