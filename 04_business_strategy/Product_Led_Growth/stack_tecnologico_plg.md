# 🛠️ Stack Tecnológico para Product-Led Growth

> **💡 Guía Técnica**: Herramientas, plataformas y tecnologías esenciales para implementar y escalar estrategias PLG efectivas.

---

## 📋 Tabla de Contenidos

1. [🎯 Arquitectura del Stack PLG](#-arquitectura-del-stack-plg)
2. [📊 Analytics y Tracking](#-analytics-y-tracking)
3. [💬 In-App Messaging y Onboarding](#-in-app-messaging-y-onboarding)
4. [🧪 A/B Testing y Experimentación](#-ab-testing-y-experimentación)
5. [📧 Email y Comunicación](#-email-y-comunicación)
6. [💰 Billing y Pagos](#-billing-y-pagos)
7. [🔄 CRM y Customer Success](#-crm-y-customer-success)
8. [📈 Dashboards y Reporting](#-dashboards-y-reporting)
9. [✅ Stack Recomendado por Etapa](#-stack-recomendado-por-etapa)

---

## 🎯 Arquitectura del Stack PLG

### **Componentes Esenciales**

```
┌─────────────────────────────────────────────────┐
│  ARQUITECTURA STACK PLG                         │
└─────────────────────────────────────────────────┘

┌─────────────────┐
│   Analytics     │ ← Tracking de comportamiento
└────────┬────────┘
         │
┌────────▼────────┐
│  In-App Tools   │ ← Onboarding, prompts, guías
└────────┬────────┘
         │
┌────────▼────────┐
│  A/B Testing    │ ← Experimentación
└────────┬────────┘
         │
┌────────▼────────┐
│  Email/SMS      │ ← Comunicación
└────────┬────────┘
         │
┌────────▼────────┐
│  Billing        │ ← Pagos y suscripciones
└────────┬────────┘
         │
┌────────▼────────┐
│  CRM/CS         │ ← Gestión de clientes
└────────┬────────┘
         │
┌────────▼────────┐
│  Dashboards     │ ← Visualización y reporting
└─────────────────┘
```

### **Integración de Componentes**

**Flujo de Datos:**
```
Producto → Analytics → In-App Tools → Email → Billing → CRM → Dashboards
```

**Principios:**
- **Unified Data**: Datos centralizados
- **Real-time**: Actualización en tiempo real
- **Segmented**: Segmentación avanzada
- **Automated**: Automatización donde sea posible

---

## 📊 Analytics y Tracking

### **Categorías de Herramientas**

#### **1. Product Analytics**

**Propósito:** Entender comportamiento de usuarios en el producto

**Herramientas Principales:**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **Mixpanel** | $25-833/mes | Event tracking avanzado | Funnels, cohorts, retention |
| **Amplitude** | $0-950/mes | Product analytics completo | Behavioral cohorts, paths |
| **Heap** | $0-999/mes | Auto-tracking | Captura automática de eventos |
| **PostHog** | $0-450/mes | Open source | Self-hosted, completo |
| **Google Analytics** | Gratis | Web analytics básico | Gratis, limitado para productos |

**Recomendación por Etapa:**
- **Inicio**: Google Analytics (gratis) o PostHog (open source)
- **Crecimiento**: Mixpanel o Amplitude
- **Escalamiento**: Amplitude o Heap (auto-tracking)

#### **2. User Behavior Analytics**

**Propósito:** Ver qué hacen usuarios en tiempo real

**Herramientas:**
- **Hotjar**: Heatmaps, session recordings ($39-989/mes)
- **FullStory**: Session replay avanzado ($0-2,000/mes)
- **LogRocket**: Session replay + debugging ($0-200/mes)
- **Microsoft Clarity**: Heatmaps gratis (gratis)

**Cuándo Usar:**
- Identificar puntos de fricción
- Debugging de problemas
- Optimización de UX
- Entender comportamiento inesperado

### **Eventos Clave a Trackear**

**Eventos de Adquisición:**
- Page view
- Sign-up started
- Sign-up completed
- Account created

**Eventos de Activación:**
- Onboarding step completed
- First [key action]
- Feature used
- Aha moment reached

**Eventos de Conversión:**
- Upgrade prompt shown
- Upgrade prompt clicked
- Checkout started
- Payment completed

**Eventos de Retención:**
- Daily active user
- Feature adoption
- Content created
- Collaboration event

**Eventos de Expansión:**
- Upgrade initiated
- Add-on purchased
- Plan changed
- Usage limit reached

---

## 💬 In-App Messaging y Onboarding

### **Herramientas Principales**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **Userpilot** | $249-499/mes | Onboarding completo | Checklists, tooltips, modals |
| **Appcues** | $249-879/mes | In-app experiences | Flows, tooltips, surveys |
| **Pendo** | $583-2,083/mes | Product adoption | Guides, analytics, feedback |
| **WalkMe** | Custom | Enterprise | Digital adoption platform |
| **Intercom** | $74-499/mes | Messaging + onboarding | Chat, product tours |

**Recomendación por Etapa:**
- **Inicio**: Userpilot o Appcues (más accesible)
- **Crecimiento**: Pendo (más features)
- **Enterprise**: WalkMe o Pendo Enterprise

### **Features Clave**

**1. Onboarding Flows**
- Checklists
- Product tours
- Step-by-step guides
- Interactive tutorials

**2. In-App Messaging**
- Tooltips
- Modals
- Banners
- Slideouts

**3. Segmentation**
- Por comportamiento
- Por plan
- Por cohorte
- Por características

**4. Analytics**
- Completion rates
- Time-to-value
- Feature adoption
- Drop-off points

---

## 🧪 A/B Testing y Experimentación

### **Herramientas Principales**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **Optimizely** | $49-1,000+/mes | Experimentación avanzada | Full-stack, web, mobile |
| **VWO** | $199-999/mes | Testing web | Visual editor, testing |
| **Google Optimize** | Gratis (descontinuado) | Testing básico | Gratis, limitado |
| **LaunchDarkly** | $0-25/mes | Feature flags | Feature toggles, gradual rollout |
| **Split.io** | $0-500/mes | Feature flags + testing | Feature flags, experiments |

**Recomendación:**
- **Inicio**: LaunchDarkly o Split.io (feature flags + testing)
- **Crecimiento**: Optimizely o VWO
- **Enterprise**: Optimizely Enterprise

### **Cuándo Usar Cada Una**

**Feature Flags:**
- Lanzar features gradualmente
- Rollback rápido
- Testing en producción
- Control de features

**A/B Testing:**
- Optimizar conversión
- Testear mensajes
- Testear diseño
- Testear pricing

---

## 📧 Email y Comunicación

### **Herramientas Principales**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **Intercom** | $74-499/mes | Messaging completo | Chat, email, in-app |
| **Customer.io** | $150-1,500/mes | Email transaccional | Behavioral emails, segments |
| **SendGrid** | $15-80/mes | Email delivery | API, transactional |
| **Mailchimp** | $0-350/mes | Marketing email | Templates, automation |
| **ConvertKit** | $0-290/mes | Creators | Email marketing, forms |

**Recomendación por Uso:**
- **In-App + Email**: Intercom
- **Email Transaccional**: Customer.io o SendGrid
- **Marketing Email**: Mailchimp o ConvertKit

### **Tipos de Emails PLG**

**1. Onboarding Emails**
- Welcome email
- Activation reminders
- Feature discovery
- Tips and tricks

**2. Engagement Emails**
- Weekly digest
- Feature updates
- Best practices
- Community content

**3. Conversion Emails**
- Trial reminders
- Upgrade prompts
- Feature highlights
- Special offers

**4. Retention Emails**
- Re-engagement
- Win-back campaigns
- Usage reports
- Success stories

---

## 💰 Billing y Pagos

### **Herramientas Principales**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **Stripe** | 2.9% + $0.30 | Pagos globales | API completa, subscriptions |
| **Paddle** | 5% + $0.50 | Merchant of record | Maneja taxes, compliance |
| **Chargebee** | $249-999/mes | Billing completo | Subscriptions, dunning |
| **Recurly** | $149-699/mes | Enterprise billing | Advanced features |
| **Braintree** | 2.9% + $0.30 | PayPal integration | PayPal, Venmo |

**Recomendación:**
- **Inicio**: Stripe (más flexible)
- **Crecimiento**: Chargebee (más features)
- **Enterprise**: Recurly o Chargebee Enterprise

### **Features Clave**

**1. Subscription Management**
- Planes y precios
- Upgrades/downgrades
- Prorating
- Trials

**2. Payment Processing**
- Múltiples métodos
- Recurring payments
- Failed payment handling
- Dunning management

**3. Analytics**
- MRR tracking
- Churn analysis
- Revenue forecasting
- Customer lifetime value

---

## 🔄 CRM y Customer Success

### **Herramientas Principales**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **HubSpot** | $0-1,200/mes | CRM completo | Free tier, marketing, sales |
| **Salesforce** | $25-300/user/mes | Enterprise CRM | Completo, customizable |
| **Intercom** | $74-499/mes | Customer messaging | Chat, email, support |
| **Zendesk** | $55-215/mes | Support tickets | Ticketing, knowledge base |
| **Gainsight** | Custom | Customer success | CS platform, health scores |

**Recomendación:**
- **Inicio**: HubSpot (free tier)
- **Crecimiento**: Intercom o HubSpot
- **Enterprise**: Salesforce o Gainsight

### **Features Clave para PLG**

**1. Product-Qualified Leads (PQLs)**
- Scoring basado en uso
- Segments automáticos
- Handoff a sales
- Tracking de conversión

**2. Customer Health Scores**
- Engagement tracking
- Risk identification
- Churn prediction
- Expansion opportunities

**3. Automated Workflows**
- Onboarding sequences
- Re-engagement campaigns
- Win-back flows
- Expansion prompts

---

## 📈 Dashboards y Reporting

### **Herramientas Principales**

| Herramienta | Precio | Mejor Para | Características |
|-------------|--------|-----------|-----------------|
| **Tableau** | $70-70/user/mes | BI avanzado | Visualizations, analytics |
| **Looker** | Custom | Data platform | SQL-based, modeling |
| **Metabase** | $0-500/mes | Open source BI | Self-hosted, SQL queries |
| **Mode** | $0-349/mes | Analytics workspace | SQL, Python, R |
| **Google Data Studio** | Gratis | Reporting básico | Gratis, limitado |

**Recomendación:**
- **Inicio**: Google Data Studio (gratis) o Metabase
- **Crecimiento**: Looker o Mode
- **Enterprise**: Tableau o Looker

### **Dashboards Esenciales PLG**

**1. Executive Dashboard**
- MRR y crecimiento
- NRR
- LTV/CAC
- Churn rate

**2. Product Dashboard**
- Sign-up rate
- Activation rate
- Time-to-value
- Feature adoption

**3. Growth Dashboard**
- CAC por canal
- Conversion rate
- Viral coefficient
- Organic vs paid

**4. Revenue Dashboard**
- MRR breakdown
- Expansion revenue
- Churn revenue
- ARPU

---

## ✅ Stack Recomendado por Etapa

### **Etapa 1: Inicio (MVP - $0-500/mes)**

**Stack Mínimo:**
- **Analytics**: Google Analytics (gratis) o PostHog (open source)
- **In-App**: Userpilot Starter ($249/mes) o Appcues ($249/mes)
- **Email**: Customer.io ($150/mes) o SendGrid ($15/mes)
- **Billing**: Stripe (2.9% + $0.30)
- **CRM**: HubSpot (free tier)
- **Dashboards**: Google Data Studio (gratis)

**Total**: ~$400-500/mes + fees de Stripe

---

### **Etapa 2: Crecimiento ($500-2,000/mes)**

**Stack Recomendado:**
- **Analytics**: Mixpanel ($25-833/mes) o Amplitude ($0-950/mes)
- **In-App**: Userpilot Growth ($499/mes) o Pendo ($583/mes)
- **A/B Testing**: LaunchDarkly ($0-25/mes) o Optimizely ($49/mes)
- **Email**: Customer.io ($150-1,500/mes) o Intercom ($74-499/mes)
- **Billing**: Stripe + Chargebee ($249-999/mes)
- **CRM**: HubSpot ($45-1,200/mes) o Intercom
- **Dashboards**: Metabase ($0-500/mes) o Mode ($0-349/mes)

**Total**: ~$1,500-3,000/mes + fees

---

### **Etapa 3: Escalamiento ($2,000-10,000+/mes)**

**Stack Avanzado:**
- **Analytics**: Amplitude ($950+/mes) o Heap ($999+/mes)
- **In-App**: Pendo ($2,083+/mes) o WalkMe (custom)
- **A/B Testing**: Optimizely ($1,000+/mes)
- **Email**: Intercom ($499+/mes) o Customer.io ($1,500+/mes)
- **Billing**: Chargebee ($999+/mes) o Recurly ($699+/mes)
- **CRM**: Salesforce ($300/user/mes) o Gainsight (custom)
- **Dashboards**: Looker (custom) o Tableau ($70/user/mes)

**Total**: ~$5,000-15,000+/mes + fees

---

## 🔗 Integraciones Clave

### **Integraciones Esenciales**

**1. Analytics ↔ In-App Tools**
- Datos de comportamiento → Segmentación
- Eventos → Triggers de mensajes
- Funnels → Optimización de onboarding

**2. In-App Tools ↔ Email**
- Comportamiento → Email triggers
- Segmentación → Email campaigns
- Engagement → Email personalizado

**3. Analytics ↔ Billing**
- Usage → Billing events
- Conversion → Revenue tracking
- Churn → Billing updates

**4. CRM ↔ Product**
- Product usage → Health scores
- PQLs → CRM leads
- Expansion → CRM opportunities

---

## 📊 Comparación de Costos

### **Stack Completo por Etapa**

| Etapa | Stack Mensual | Features | Recomendación |
|-------|---------------|---------|---------------|
| **Inicio** | $400-500 | Básico | MVP suficiente |
| **Crecimiento** | $1,500-3,000 | Intermedio | Balance features/costo |
| **Escalamiento** | $5,000-15,000+ | Avanzado | Enterprise features |

### **ROI de Herramientas**

**Alta ROI:**
- Analytics (entender usuarios)
- In-App tools (mejorar onboarding)
- Billing (automatizar revenue)

**Media ROI:**
- A/B Testing (optimización)
- Email (comunicación)
- CRM (gestión)

**Baja ROI (pero necesarias):**
- Dashboards (reporting)
- Support tools (soporte)

---

## ✅ Checklist de Selección de Herramientas

```
┌─────────────────────────────────────────────────┐
│  CHECKLIST: SELECCIÓN DE HERRAMIENTAS          │
└─────────────────────────────────────────────────┘

ANALYTICS
─────────────────────────────────────────────────
[ ] Event tracking necesario
[ ] Funnel analysis
[ ] Cohort analysis
[ ] Retention reports
[ ] Integraciones disponibles

IN-APP TOOLS
─────────────────────────────────────────────────
[ ] Onboarding flows
[ ] In-app messaging
[ ] Segmentation
[ ] Analytics integrado
[ ] Fácil de usar (no-code)

A/B TESTING
─────────────────────────────────────────────────
[ ] Feature flags
[ ] A/B testing
[ ] Statistical significance
[ ] Integración con analytics

EMAIL
─────────────────────────────────────────────────
[ ] Behavioral triggers
[ ] Segmentation
[ ] Templates
[ ] Analytics
[ ] Deliverability

BILLING
─────────────────────────────────────────────────
[ ] Subscription management
[ ] Múltiples métodos de pago
[ ] Dunning management
[ ] Analytics de revenue
[ ] Compliance (taxes, etc.)

CRM
─────────────────────────────────────────────────
[ ] PQL scoring
[ ] Health scores
[ ] Automated workflows
[ ] Integración con producto
[ ] Reporting
```

---

*Última actualización: 2024*
*Nota: Precios son aproximados y pueden variar. Verificar en sitios oficiales.*


