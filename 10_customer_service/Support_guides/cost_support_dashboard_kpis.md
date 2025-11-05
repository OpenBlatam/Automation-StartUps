---
title: "Cost Support Dashboard Kpis"
category: "10_customer_service"
tags: []
created: "2025-10-29"
path: "10_customer_service/Support_guides/cost_support_dashboard_kpis.md"
---

# 📊 Cost Support Dashboard & KPIs
## Métricas y Paneles de Control para Soporte Financiero

---

## 🎯 KPIs CLAVE

### **Operacionales**

#### **Tiempo de Respuesta**
- **KPI:** Tiempo promedio para primera respuesta
- **Objetivo:** <2 horas
- **Actual:** [Medir]
- **Formula:** Suma de tiempos / Número de casos

#### **Tiempo de Resolución**
- **KPI:** Tiempo promedio para resolver caso
- **Objetivo:** <24 horas
- **Actual:** [Medir]
- **Formula:** (Fecha resolución - Fecha apertura)

#### **First Contact Resolution (FCR)**
- **KPI:** % de casos resueltos en primer contacto
- **Objetivo:** >85%
- **Actual:** [Medir]
- **Formula:** (Casos resueltos 1er contacto / Total casos) × 100

#### **Escalation Rate**
- **KPI:** % de casos escalados
- **Objetivo:** <20%
- **Actual:** [Medir]
- **Formula:** (Casos escalados / Total casos) × 100

---

### **Satisfacción**

#### **Customer Satisfaction (CSAT)**
- **KPI:** Puntuación promedio de satisfacción
- **Objetivo:** >4.5/5
- **Medición:** Encuesta post-interacción
- **Frecuencia:** Toda interacción

#### **Net Promoter Score (NPS)**
- **KPI:** NPS específico para cost support
- **Objetivo:** >70
- **Medición:** Encuesta trimestral
- **Segmentación:** Solo interacciones financieras

#### **Customer Effort Score (CES)**
- **KPI:** Facilidad percibida
- **Objetivo:** >85%
- **Medición:** Escala 1-5
- **Pregunta:** "¿Qué tan fácil fue resolver tu consulta?"

---

### **Financieros**

#### **Average Resolution Cost**
- **KPI:** Costo promedio por resolución
- **Objetivo:** <$50
- **Formula:** (Total costos en período / Total resoluciones)
- **Includes:** Créditos, descuentos, tiempo de agente

#### **Credit Application Rate**
- **KPI:** % de interacciones que resultan en crédito
- **Objetivo:** <30%
- **Tracking:** Montos aplicados
- **Alert:** Si >40% - revisar políticas

#### **Revenue Retention Rate**
- **KPI:** % de clientes retenidos en conversaciones de costo
- **Objetivo:** >90%
- **Formula:** (Clientes retenidos / Clientes considerando cancelación) × 100

#### **Upsell Success Rate**
- **KPI:** % de upselling exitoso en cost conversations
- **Objetivo:** >25%
- **Formula:** (Upsells exitosos / Oportunidades de upsell) × 100

---

### **Calidad**

#### **Script Adherence**
- **KPI:** Uso apropiado de scripts
- **Objetivo:** >80%
- **Medición:** Review de casos aleatorios
- **Evaluación:** Manager review

#### **ROI Accuracy**
- **KPI:** Precisión de cálculos de ROI
- **Objetivo:** >95%
- **Medición:** Audit de cálculos
- **Formula:** (Cálculos correctos / Total cálculos) × 100

#### **Authorization Compliance**
- **KPI:** Autorizaciones dentro de límites
- **Objetivo:** 100%
- **Medición:** Revisar casos >$200
- **Frecuencia:** Daily

---

## 📈 DASHBOARDS RECOMENDADOS

### **Dashboard 1: Real-Time Metrics**

```
┌─────────────────────────────────────────────┐
│     COST SUPPORT - LIVE METRICS             │
├─────────────────────────────────────────────┤
│  Avg Response Time: 1.2h    Target: <2h   │
│  Avg Resolution: 18h        Target: <24h    │
│  FCR: 87%                 Target: >85%    │
│  CSAT: 4.6/5               Target: >4.5    │
│  Escalations: 15%          Target: <20%     │
│  Credits Today: $2,400     Budget: <$5K    │
└─────────────────────────────────────────────┘
```

**Actualización:** En tiempo real  
**Acceso:** Todo el equipo  
**Disponible:** 24/7

---

### **Dashboard 2: Personal Performance**

```
┌─────────────────────────────────────────────┐
│       PERFORMANCE - [TU NOMBRE]             │
├─────────────────────────────────────────────┤
│  Casos Este Mes: 45                         │
│  Tiempo Promedio: 35 min/caso              │
│  FCR Personal: 92%  [Manager: 85%]         │
│  CSAT Personal: 4.8/5  [Team: 4.6/5]        │
│  Credits Applied: $1,200  [Avg: $1,800]     │
│  Retención: 95%  [Team: 88%]               │
│  Upsell: 30%  [Team: 22%]                  │
└─────────────────────────────────────────────┘
```

**Actualización:** Diaria  
**Personal:** Solo tú  
**Comparación:** vs Team average

---

### **Dashboard 3: Team Metrics (Manager)**

```
┌───────────────────────────────────────────────────┐
│           TEAM PERFORMANCE - COST SUPPORT         │
├───────────────────────────────────────────────────┤
│                                                    │
│  Response Time:  ▓▓▓▓▓▓▓▓▓▓░░ 1.5h (Target: <2h) │
│  Resolution:    ▓▓▓▓▓▓▓▓▓░░░ 20h (Target: <24h)  │
│  FCR:           ▓▓▓▓▓▓▓▓▓▓░░ 88% (Target: >85%)  │
│  CSAT:          ▓▓▓▓▓▓▓▓▓▓░░ 4.6/5 (Target: >4.5)│
│                                                    │
│  Team Top Performers:                             │
│  1. [Name] - FCR: 95%, CSAT: 4.9/5               │
│  2. [Name] - Retención: 98%, Upsell: 35%          │
│                                                    │
│  Actions Needed:                                  │
│  • Train Agent X in ROI calculations              │
│  • Review cases from Agent Y                      │
│                                                    │
└───────────────────────────────────────────────────┘
```

**Actualización:** Diaria  
**Acceso:** Manager + Leads  
**Alertas:** Automáticas

---

### **Dashboard 4: Financial Impact (Director)**

```
┌───────────────────────────────────────────────────┐
│        FINANCIAL IMPACT - QUARTERLY              │
├───────────────────────────────────────────────────┤
│                                                    │
│  Total Cases Handled: 1,247                       │
│  Revenue Retained: $2,345,678                     │
│  Credits Applied: $245,890 (10.5% of revenue)     │
│  Recoveries: $156,789 (converted from credits)    │
│  Net Impact: +$1,256,567                          │
│                                                    │
│  ROI Calculations:                                │
│  • Average Presented: $15,234                     │
│  • Average Accepted: $12,345                      │
│  • Conversion Rate: 81%                            │
│                                                    │
│  Top Industries:                                   │
│  1. SaaS B2B: 32% - Avg ROI: 420%                 │
│  2. E-commerce: 28% - Avg ROI: 310%                │
│  3. Enterprise: 18% - Avg ROI: 250%               │
│                                                    │
└───────────────────────────────────────────────────┘
```

**Actualización:** Trimestral  
**Acceso:** Director + Management  
**Purpose:** Strategic decision making

---

## 📊 MÉTRICAS ADICIONALES

### **Agent-Specific KPIs**

#### **Personal Satisfaction Score**
- **KPI:** Satisfacción personal con role
- **Objetivo:** >4/5
- **Medición:** Encuesta mensual
- **Action:** Address concerns proactively

#### **Training Completion Rate**
- **KPI:** % de trainings completados a tiempo
- **Objetivo:** 100%
- **Tracking:** Enrollment + completion
- **Consequence:** Certification delay if incomplete

#### **Innovation Contributions**
- **KPI:** Number of improvements suggested/implemented
- **Objetivo:** >2/quarter
- **Tracking:** Ideas + implementation
- **Recognition:** Quarterly awards

---

### **Team KPIs**

#### **Cross-Training Score**
- **KPI:** % de team cross-trained
- **Objetivo:** 100%
- **Benefits:** Backup coverage, flexibility
- **Measurement:** Skills matrix

#### **Knowledge Base Contributions**
- **KPI:** Number of KB articles created/updated
- **Objetivo:** >5/person/month
- **Quality:** Peer reviewed
- **Impact:** Faster resolution

#### **Mentoring Hours**
- **KPI:** Time spent mentoring new agents
- **Objetivo:** >4h/month
- **Tracking:** Logged hours
- **Recognition:** Monthly

---

## 🎯 GOAL SETTING

### **Daily Goals**
- Response time: <2 hours
- Resolution rate: >50% of cases
- CSAT: >4.5 average
- No unauthorized credits

### **Weekly Goals**
- FCR: >85%
- Script adherence: >80%
- Team satisfaction: >4/5
- Innovation contribution: 1 idea

### **Monthly Goals**
- Team CSAT: >4.5
- Retain: >90%
- Upsell: >25%
- Training: 100% completion

### **Quarterly Goals**
- NPS: >70
- ROI accuracy: >95%
- Revenue retention: >$2M
- Team growth: +2 skills

---

## 📈 TRACKING TOOLS

### **CRM Dashboard**
- Real-time cases
- Personal queue
- Escalations
- Credits applied

### **Analytics Platform**
- Historical trends
- Predictive analytics
- Team comparisons
- Industry benchmarks

### **Reporting Tool**
- Daily summary
- Weekly report
- Monthly deep dive
- Quarterly review

---

## ✅ ACTION ITEMS BY KPI

### **Si Response Time >2h:**
- [ ] Review caseload
- [ ] Assess help needed
- [ ] Scale resources
- [ ] Train on efficiency

### **Si FCR <85%:**
- [ ] Review cases no resueltos
- [ ] Additional training
- [ ] Script improvements
- [ ] Better tools

### **Si CSAT <4.5:**
- [ ] Review feedback
- [ ] Address concerns
- [ ] Improve empathy
- [ ] Better resolutions

### **Si Credits >40%:**
- [ ] Review credit policies
- [ ] Reduce unnecessary credits
- [ ] Better alternative solutions
- [ ] Policy update needed

---

## 🎁 REWARDS & RECOGNITION

### **Top Performer (Monthly)**
- KPI: Highest CSAT + FCR combo
- Reward: $500 bonus
- Recognition: Team meeting shoutout

### **Retention Champion (Quarterly)**
- KPI: Highest retention rate
- Reward: $1,000 bonus
- Recognition: Company-wide

### **Innovation Leader (Quarterly)**
- KPI: Best implemented idea
- Reward: $500 + day off
- Recognition: Knowledge base featured

---

**Dashboard en:** [Link to dashboard]  
**Actualizado:** En tiempo real  
**Contacto:** metrics@blatam.com  
**Alertas configuradas en:** Slack #cs-metrics-alerts


