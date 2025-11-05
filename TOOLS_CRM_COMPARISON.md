# Comparativa de Herramientas y CRMs - Outreach DM

> **Resumen ejecutivo (rápido)**
>
> - **Outbound con llamadas**: Close o Pipedrive (+ Aircall)
> - **Inbound + automatización**: HubSpot Starter o ActiveCampaign
> - **Costo/flexibilidad**: Zoho CRM (+ Make)
> - **Decisión rápida**: Usa la [Matriz de decisión](#matriz-de-decisión-rápida) y el CSV `CRM_DECISION_MATRIX.csv`
>
> **Documentos relacionados**:
> - [`UTM_GUIDE_OUTREACH.md`](./UTM_GUIDE_OUTREACH.md) - Convenciones y tracking de UTMs
> - [`Variantes_RealEstate_Tu.md`](./Variantes_RealEstate_Tu.md) - DMs y variantes por industria
> - [`SHORTLINKS_UTM_SAMPLE.csv`](./SHORTLINKS_UTM_SAMPLE.csv) - Ejemplos de shortlinks listos

Recomendaciones basadas en casos de uso específicos.

## Índice rápido (navegación)

**Decisión y comparación**:
- [Matriz de decisión rápida](#matriz-de-decisión-rápida) - Compara CRMs en 5 minutos
- [Resumen rápido comparativa](#resumen-rápido-comparativa-clave) - Tabla comparativa
- [Recomendaciones por caso de uso](#recomendaciones-por-caso-de-uso) - Por escenario

**Implementación**:
- [Checklist de implementación CRM](#checklist-de-implementación-crm) - Pasos esenciales
- [Mapeos por CRM](#mapeos-por-crm-campos-y-pasos) - Campos UTM y workflows
- [Ejemplos API/Payload](#ejemplos-apipayload-por-crm-listos-para-pegar) - Código listo

**UTMs y tracking**:
- [Captura de UTMs en CRM](#captura-de-utms-en-crm-estándar-operativo) - Estándar operativo
- [Stack UTM-first](#stack-utmfirst-recomendado-por-escenario) - Por escenario
- [Matriz nombres archivos = utm_content](#matriz-de-nombres-de-archivos--utm_content-por-canal) - Consistencia
- [Testing y validación de UTMs](#testing-y-validación-de-utms-checklist-qa) - QA y pruebas

**KPIs y métricas**:
- [KPIs recomendados por tipo de negocio](#kpis-recomendados-por-tipo-de-negocio) - SaaS, E-commerce, Educación, Real Estate
- [Ejemplos de métricas por canal](#ejemplos-de-métricas-por-canal-benchmarks) - Benchmarks CTR/CVR/CPA
- [Flujos de decisión visual](#flujos-de-decisión-visual-árboles) - Árboles de decisión

**Troubleshooting y referencias**:
- [Errores comunes y soluciones rápidas](#errores-comunes-y-soluciones-rápidas-cheat-sheet) - Cheat sheet
- [Comparación rápida: ¿Cuándo usar cada herramienta?](#comparación-rápida-cuándo-usar-cada-herramienta) - Tabla decisión rápida
- [Checklist de salud del CRM](#checklist-de-salud-del-crm-trimestral) - Auditoría trimestral
- [Próximos pasos recomendados](#próximos-pasos-recomendados) - Timeline 90 días

---

## Quick Start (5 minutos)

### Paso 1: Identifica tu escenario (2 min)
- **¿Haces llamadas activas?** → Close o Pipedrive + Aircall
- **¿Priorizas automatización/email?** → HubSpot Starter o ActiveCampaign
- **¿Presupuesto ajustado?** → Zoho CRM o HubSpot Free
- **¿Equipo pequeño (<5 personas)?** → HubSpot Free o Notion (si ya usas Notion)

### Paso 2: Prueba rápida (2 min)
1. Abre la [Matriz de decisión](#matriz-de-decisión-rápida) y califica 1-5 por criterio
2. Calcula score con fórmula: `=SUMPRODUCT($B$2:$B$8, C2:C8)`
3. Revisa [Resumen rápido comparativa](#resumen-rápido-comparativa-clave) para validar

### Paso 3: Setup inicial (1 min)
1. Crea cuenta gratuita/prueba (30 días típico)
2. Importa 10-20 contactos de prueba (CSV)
3. Configura campos UTM básicos: `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term` (ver [Mapeos por CRM](#mapeos-por-crm-campos-y-pasos))
4. Conecta un formulario/webhook (ver [Ejemplos API](#ejemplos-apipayload-por-crm-listos-para-pegar))

**Siguiente paso**: Revisa [Checklist de implementación CRM](#checklist-de-implementación-crm) para setup completo.

---

## ✅ Pre-evaluación (antes de elegir CRM)

Responde estas preguntas para orientar tu decisión:

- [ ] **¿Cuántos usuarios necesitan acceso?** → Define rango de presupuesto (ver [Precios por niveles](#precios-por-niveles-orientativo))
- [ ] **¿Hacemos más outbound (llamadas) o inbound (formularios/nurtures)?** → Prioriza `voip_llamadas` vs `automatizacion` en la [Matriz de decisión](#matriz-de-decisión-rápida)
- [ ] **¿Tenemos desarrollador/disponibilidad técnica?** → Considera Make vs Zapier, APIs personalizadas (ver [Recetas Make/Zapier](#recetas-makezapier-plantillas))
- [ ] **¿Qué integraciones son críticas?** → Revisa [Matriz de integraciones clave](#matriz-de-integraciones-clave) y [Checklist de integraciones por CRM](#checklist-de-integraciones-por-crm-rápido)
- [ ] **¿Necesitamos compliance fuerte (GDPR, audit logs)?** → Ver [Seguridad y cumplimiento](#seguridad-y-cumplimiento)
- [ ] **¿Budget mensual aproximado?** → Calcula [TCO rápido](#tco-rápido-sheets) (incluye costos ocultos)

**Con las respuestas**, usa:
- [Tabla de decisión por escenario](#tabla-de-decisión-por-escenario-pesos-preconfigurados) si encajas en SDR/Inbound/Budget
- [Mini Score Calculator](#mini-score-calculator-sheets) para customizar pesos
- [Matriz de decisión (Rápida)](#matriz-de-decisión-rápida) como referencia rápida

---

## Tabla de contenidos
- [Comparativa de Herramientas y CRMs - Outreach DM](#comparativa-de-herramientas-y-crms---outreach-dm)
  - [Índice rápido (navegación)](#índice-rápido-navegación)
  - [Quick Start (5 minutos)](#quick-start-5-minutos)
    - [Paso 1: Identifica tu escenario (2 min)](#paso-1-identifica-tu-escenario-2-min)
    - [Paso 2: Prueba rápida (2 min)](#paso-2-prueba-rápida-2-min)
    - [Paso 3: Setup inicial (1 min)](#paso-3-setup-inicial-1-min)
  - [✅ Pre-evaluación (antes de elegir CRM)](#-pre-evaluación-antes-de-elegir-crm)
  - [Tabla de contenidos](#tabla-de-contenidos)
  - [CRMs Principales](#crms-principales)
  - [Email Marketing](#email-marketing)
  - [LinkedIn Automation](#linkedin-automation)
  - [Analytics y Tracking](#analytics-y-tracking)
  - [Automatización (Zapier/Make)](#automatización-zapiermake)
  - [Resumen rápido (comparativa clave)](#resumen-rápido-comparativa-clave)
  - [Recomendaciones por caso de uso](#recomendaciones-por-caso-de-uso)
  - [Decision Tree Visual (elige en 2 minutos)](#decision-tree-visual-elige-en-2-minutos)
  - [Quick Wins por CRM (setup \< 30 min)](#quick-wins-por-crm-setup--30-min)
    - [HubSpot](#hubspot)
    - [Pipedrive](#pipedrive)
    - [ActiveCampaign](#activecampaign)
    - [Close](#close)
    - [Zoho CRM](#zoho-crm)
  - [Matriz de decisión (Rápida)](#matriz-de-decisión-rápida)
  - [Tabla de decisión por escenario (pesos preconfigurados)](#tabla-de-decisión-por-escenario-pesos-preconfigurados)
  - [Mini Score Calculator (Sheets)](#mini-score-calculator-sheets)
  - [Checklist de integraciones por CRM (rápido)](#checklist-de-integraciones-por-crm-rápido)
  - [Checklist de implementación CRM](#checklist-de-implementación-crm)
  - [Plan de migración (detallado)](#plan-de-migración-detallado)
  - [Checklist de migración específico por CRM origen→destino](#checklist-de-migración-específico-por-crm-origendestino)
    - [Desde Notion/Airtable → HubSpot/Pipedrive/ActiveCampaign](#desde-notionairtable--hubspotpipedriveactivecampaign)
    - [Desde HubSpot Free → HubSpot Starter/Pro](#desde-hubspot-free--hubspot-starterpro)
    - [Desde Pipedrive → Close (o viceversa)](#desde-pipedrive--close-o-viceversa)
    - [Desde Google Sheets/Excel → Cualquier CRM](#desde-google-sheetsexcel--cualquier-crm)
  - [Hoja de ruta de implementación (30 días)](#hoja-de-ruta-de-implementación-30-días)
  - [Playbooks recomendados (enlazar a docs existentes)](#playbooks-recomendados-enlazar-a-docs-existentes)
  - [Matriz de integraciones clave](#matriz-de-integraciones-clave)
  - [Precios por niveles (orientativo)](#precios-por-niveles-orientativo)
  - [Seguridad y cumplimiento](#seguridad-y-cumplimiento)
  - [TCO rápido (Sheets)](#tco-rápido-sheets)
  - [Escenarios/recetas sugeridas](#escenariosrecetas-sugeridas)
  - [Playbook SDR — Close + Aircall (llamadas + email)](#playbook-sdr--close--aircall-llamadas--email)
  - [Playbook Inbound — HubSpot/ActiveCampaign (nurtures + Lead Ads)](#playbook-inbound--hubspotactivecampaign-nurtures--lead-ads)
  - [Plantillas de campos por CRM (nombres/tipos exactos)](#plantillas-de-campos-por-crm-nombrestipos-exactos)
  - [Checklist de adopción del equipo](#checklist-de-adopción-del-equipo)
  - [Onboarding por CRM (primeros 30 días)](#onboarding-por-crm-primeros-30-días)
    - [HubSpot](#hubspot-1)
    - [Pipedrive](#pipedrive-1)
    - [ActiveCampaign](#activecampaign-1)
    - [Close](#close-1)
  - [FAQ](#faq)
    - [Migración y setup](#migración-y-setup)
    - [Estrategia y priorización](#estrategia-y-priorización)
    - [Lock-in y portabilidad](#lock-in-y-portabilidad)
    - [UTMs y tracking](#utms-y-tracking)
    - [Integraciones y automatización](#integraciones-y-automatización)
    - [Timing y cambios](#timing-y-cambios)
    - [UTMs y tracking](#utms-y-tracking-1)
    - [Costos y ROI](#costos-y-roi)
  - [Métricas y KPIs recomendados (por tipo de negocio)](#métricas-y-kpis-recomendados-por-tipo-de-negocio)
    - [SaaS B2B (ventas complejas)](#saas-b2b-ventas-complejas)
    - [Inbound/Educación (cursos, webinars)](#inboundeducación-cursos-webinars)
    - [E-commerce / DTC](#e-commerce--dtc)
    - [Real Estate / Servicios locales](#real-estate--servicios-locales)
    - [Dashboard mínimo recomendado (Google Sheets/CRM)](#dashboard-mínimo-recomendado-google-sheetscrm)
  - [Captura de UTMs en CRM (estándar operativo)](#captura-de-utms-en-crm-estándar-operativo)
    - [Campos recomendados en Lead/Contact (crear si no existen)](#campos-recomendados-en-leadcontact-crear-si-no-existen)
    - [Mapeo desde formularios/web (ejemplo)](#mapeo-desde-formulariosweb-ejemplo)
    - [Webhook → CRM (JSON ejemplo)](#webhook--crm-json-ejemplo)
    - [Reglas de sobreescritura (sugerido)](#reglas-de-sobreescritura-sugerido)
    - [QA en CRM (check rápido)](#qa-en-crm-check-rápido)
  - [Stack UTM‑first (recomendado por escenario)](#stack-utmfirst-recomendado-por-escenario)
  - [Recetas Make/Zapier (plantillas)](#recetas-makezapier-plantillas)
  - [Recetas Make/Zapier detalladas (paso a paso)](#recetas-makezapier-detalladas-paso-a-paso)
    - [1. Lead Ads (Meta) → CRM con UTMs](#1-lead-ads-meta--crm-con-utms)
    - [2. Form → CRM con UTMs (hidden fields)](#2-form--crm-con-utms-hidden-fields)
    - [3. Deal Stage changed → Notificación Slack/Email](#3-deal-stage-changed--notificación-slackemail)
  - [Troubleshooting común (soluciones rápidas)](#troubleshooting-común-soluciones-rápidas)
  - [Reportes mínimos por UTM](#reportes-mínimos-por-utm)
  - [Mapeos por CRM (campos y pasos)](#mapeos-por-crm-campos-y-pasos)
    - [HubSpot](#hubspot-2)
    - [Pipedrive](#pipedrive-2)
    - [ActiveCampaign](#activecampaign-2)
    - [Close (CRM)](#close-crm)
  - [Ejemplos API/Payload por CRM (listos para pegar)](#ejemplos-apipayload-por-crm-listos-para-pegar)
    - [HubSpot — Create Contact (v3)](#hubspot--create-contact-v3)
  - [Pitfalls y riesgos comunes (evítalos)](#pitfalls-y-riesgos-comunes-evítalos)
    - [Pipedrive — Upsert Person + Create Deal](#pipedrive--upsert-person--create-deal)
    - [ActiveCampaign — Create/Update Contact + Custom Fields](#activecampaign--createupdate-contact--custom-fields)
    - [Close — Create Lead with Contacts and Custom Fields](#close--create-lead-with-contacts-and-custom-fields)
  - [Webhooks Shortlinks → Make/Zap (actualizar `last_utm_*`)](#webhooks-shortlinks--makezap-actualizar-last_utm_)
    - [Bitly → Webhook → Make/Zap → CRM](#bitly--webhook--makezap--crm)
    - [Yourls (self-hosted) → Webhook → Make/Zap](#yourls-self-hosted--webhook--makezap)
  - [Matriz de nombres de archivos = `utm_content` (por canal)](#matriz-de-nombres-de-archivos--utm_content-por-canal)
  - [Troubleshooting común (UTMs no llegan / duplicados / datos rotos)](#troubleshooting-común-utms-no-llegan--duplicados--datos-rotos)
    - [Problema: UTMs no se guardan en CRM](#problema-utms-no-se-guardan-en-crm)
    - [Problema: Contactos duplicados por diferentes UTMs](#problema-contactos-duplicados-por-diferentes-utms)
    - [Problema: `utm_content` cortado o mal parseado](#problema-utm_content-cortado-o-mal-parseado)
    - [Problema: first\_utm\_\* se sobreescribe](#problema-first_utm_-se-sobreescribe)
  - [Mejores prácticas avanzadas (escalabilidad)](#mejores-prácticas-avanzadas-escalabilidad)
    - [Versionado automático](#versionado-automático)
    - [Auditoría y limpieza](#auditoría-y-limpieza)
    - [Performance tracking (CRM + Analytics)](#performance-tracking-crm--analytics)
    - [Seguridad y compliance](#seguridad-y-compliance)
  - [Checklist final (antes de lanzar campaña)](#checklist-final-antes-de-lanzar-campaña)
  - [Scripts listos (Python/JS) para automatización](#scripts-listos-pythonjs-para-automatización)
    - [Python: Parsear UTMs desde CSV y crear contactos en CRM](#python-parsear-utms-desde-csv-y-crear-contactos-en-crm)
    - [JavaScript: Validar y normalizar UTMs antes de enviar a CRM](#javascript-validar-y-normalizar-utms-antes-de-enviar-a-crm)
  - [Queries SQL/BigQuery útiles (análisis de UTMs)](#queries-sqlbigquery-útiles-análisis-de-utms)
    - [GA4 → BigQuery: Leads por `utm_campaign` y `utm_content`](#ga4--bigquery-leads-por-utm_campaign-y-utm_content)
    - [Cohort por `utm_campaign`: tiempo de primera conversión](#cohort-por-utm_campaign-tiempo-de-primera-conversión)
    - [Comparar performance por `utm_content` (variantes creativas)](#comparar-performance-por-utm_content-variantes-creativas)
  - [Plantillas Make/Zapier detalladas (paso a paso)](#plantillas-makezapier-detalladas-paso-a-paso)
    - [Make: Form Submit → Parse UTMs → HubSpot Create/Update](#make-form-submit--parse-utms--hubspot-createupdate)
    - [Zapier: Shortlink Click (Bitly) → Enriquecer Contacto](#zapier-shortlink-click-bitly--enriquecer-contacto)
  - [Casos de uso completos (flujos end-to-end)](#casos-de-uso-completos-flujos-end-to-end)
    - [Caso 1: Lead viene de Meta Ads Remarketing → Demo agendada → Deal creado](#caso-1-lead-viene-de-meta-ads-remarketing--demo-agendada--deal-creado)
    - [Caso 2: Email nurture → Click tracking → Score incrementado](#caso-2-email-nurture--click-tracking--score-incrementado)
  - [Templates y scripts listos para usar](#templates-y-scripts-listos-para-usar)
    - [1. HTML form con inputs ocultos UTM](#1-html-form-con-inputs-ocultos-utm)
    - [2. Webhook Make/Zapier (Form → CRM)](#2-webhook-makezapier-form--crm)
    - [3. Google Sheets: Dashboard UTM performance](#3-google-sheets-dashboard-utm-performance)
    - [4. Script HubSpot Workflow: Asignar owner por UTM](#4-script-hubspot-workflow-asignar-owner-por-utm)
    - [5. Google App Script: Sincronizar GA4 → Sheets → CRM](#5-google-app-script-sincronizar-ga4--sheets--crm)
  - [Recursos adicionales y herramientas](#recursos-adicionales-y-herramientas)
    - [Herramientas de testing UTM](#herramientas-de-testing-utm)
    - [Documentación oficial APIs](#documentación-oficial-apis)
    - [Comunidades y soporte](#comunidades-y-soporte)
  - [Referencias rápidas](#referencias-rápidas)
  - [Testing y validación de UTMs (checklist QA)](#testing-y-validación-de-utms-checklist-qa)
    - [Test manual rápido (5 minutos)](#test-manual-rápido-5-minutos)
    - [Test automatizado (JavaScript)](#test-automatizado-javascript)
    - [Validación de datos en CRM](#validación-de-datos-en-crm)
  - [KPIs recomendados por tipo de negocio](#kpis-recomendados-por-tipo-de-negocio)
    - [SaaS B2B (suscripciones mensuales/anuales)](#saas-b2b-suscripciones-mensualesanuales)
    - [E-commerce / Retail](#e-commerce--retail)
    - [Educación / Cursos online](#educación--cursos-online)
    - [Real Estate / Inmobiliaria](#real-estate--inmobiliaria)
  - [Flujos de decisión visual (árboles)](#flujos-de-decisión-visual-árboles)
    - [¿Qué CRM elegir? (Preguntas clave)](#qué-crm-elegir-preguntas-clave)
    - [¿Priorizar pipeline o automatización?](#priorizar-pipeline-o-automatización)
    - [¿Qué integración implementar primero?](#qué-integración-implementar-primero)
  - [Ejemplos de métricas por canal (benchmarks)](#ejemplos-de-métricas-por-canal-benchmarks)
  - [Checklist de salud del CRM (trimestral)](#checklist-de-salud-del-crm-trimestral)
    - [Calidad de datos](#calidad-de-datos)
    - [Automatización](#automatización)
    - [Integraciones](#integraciones)
    - [Reportes](#reportes)
    - [Team adoption](#team-adoption)
  - [Glosario rápido CRM (términos esenciales)](#glosario-rápido-crm-términos-esenciales)
  - [Próximos pasos recomendados](#próximos-pasos-recomendados)
    - [Timeline sugerido (primeros 90 días)](#timeline-sugerido-primeros-90-días)
    - [Checklist mensual (mantenimiento)](#checklist-mensual-mantenimiento)
  - [Errores comunes y soluciones rápidas (cheat sheet)](#errores-comunes-y-soluciones-rápidas-cheat-sheet)
  - [Comparación rápida: ¿Cuándo usar cada herramienta?](#comparación-rápida-cuándo-usar-cada-herramienta)
  - [Costos ocultos a considerar (más allá del precio base)](#costos-ocultos-a-considerar-más-allá-del-precio-base)
  - [Glosario de términos clave](#glosario-de-términos-clave)

---

## CRMs Principales

| CRM | Mejor Para | Precio/mes | Pros | Contras |
|-----|------------|------------|------|---------|
| **HubSpot (Free)** | Startups, equipos pequeños | $0 | Generoso free tier, buen email tracking | Limitado en free, puede ser lento |
| **ActiveCampaign** | Marketing automation avanzado | $15-200+ | Email automation potente, integraciones | Curva de aprendizaje, más caro |
| **Pipedrive** | Ventas simples, seguimiento pipeline | $15-100+ | Interface intuitiva, buen para sales | Limitado en marketing automation |
| **Notion** | Equipos que ya usan Notion | $8-15/user | Flexible, todo-en-uno, buen para docs | No es CRM puro, limitado en email |
| **Airtable** | Equipos técnicos, customización | $12-45/user | Muy flexible, potente | Menos CRM-ready, requiere setup |
| **Salesforce** | Empresas grandes, compliance | $25-300+/user | Potente, escalable, enterprise-ready | Caro, complejo, overkill para pequeños |

**Recomendación por tamaño**:
- **Startup (1-5 personas)**: HubSpot Free o Notion
- **Pequeño (5-20 personas)**: ActiveCampaign o Pipedrive
- **Mediano (20-50 personas)**: ActiveCampaign o HubSpot Starter
- **Grande (50+ personas)**: Salesforce o HubSpot Enterprise

---

## Email Marketing

| Herramienta | Mejor Para | Precio/mes | Pros | Contras |
|-------------|------------|-----------|------|---------|
| **Mailchimp** | Principiantes, volumen medio | $0-350+ | Fácil de usar, buen free tier | Limitado en free, menos avanzado |
| **ActiveCampaign** | Marketing automation | $15-200+ | Automation potente, scoring | Más caro, más complejo |
| **ConvertKit** | Creatores, newsletters | $9-100+ | Simple, bueno para autores | Menos enterprise features |
| **SendGrid** | Desarrolladores, APIs | $15-400+ | API potente, buena deliverability | Menos intuitivo para no-técnicos |

**Recomendación**: ActiveCampaign si ya tienes CRM, Mailchimp para empezar simple.

---

## LinkedIn Automation

| Herramienta | Función | Precio/mes | Notas |
|-------------|---------|-----------|-------|
| **LinkedIn Sales Navigator** | Buscar y contactar | $80-100+ | Oficial, menos riesgo de ban |
| **Phantombuster** | Automatización LinkedIn | $70-800+ | Potente pero cuidado con bans |
| **Lemlist** | Cold email + LinkedIn | $39-99+ | Buena para multi-canal |
| **Manual (best practice)** | Sin automatización | $0 | Más lento pero más seguro |

**Recomendación**: Sales Navigator si presupuesto permite, manual si priorizas seguridad.

---

## Analytics y Tracking

| Herramienta | Función | Precio/mes | Mejor Para |
|-------------|---------|-----------|------------|
| **Google Analytics 4** | Web analytics | $0 | Tracking general, gratis |
| **Mixpanel** | Event tracking | $0-25+ | Eventos específicos, productos |
| **Hotjar** | Heatmaps, recordings | $0-200+ | UX, ver qué hace la gente |
| **Bitly** | Link shortening + tracking | $0-500+ | Tracking de enlaces, UTMs |

**Recomendación**: GA4 (gratis) + Bitly para links con tracking.

---

## Automatización (Zapier/Make)

| Herramienta | Precio/mes | Pros | Contras |
|-------------|-----------|------|---------|
| **Zapier** | $20-600+ | Más conectores, más fácil | Más caro, limitado en free tier |
| **Make (Integromat)** | $9-300+ | Más potente, más barato | Más complejo, curva aprendizaje |
| **n8n** | $0 (self-hosted) | Open source, gratis | Requiere técnico para setup |

**Recomendación**: Make si presupuesto limitado, Zapier si simplicidad es prioridad.

---

## Resumen rápido (comparativa clave)

| CRM | Enfoque | Precio base | Pipeline | Automatización | Llamadas/VoIP | Email tracking | Reportes | Integraciones | API | Ideal para |
|-----|---------|------------|----------|----------------|---------------|----------------|----------|---------------|-----|------------|
| HubSpot (Free/Starter) | Todo-en-uno | $0 / $45+ | Muy bueno | Bueno (Starter+) | Básico | Bueno | Bueno | Amplias | Sólida | Startups, marketing+ventas |
| Pipedrive | Ventas | $15+ | Excelente | Básica (Add-ons) | Sólida | Bueno | Bueno | Buenas | Sólida | SMB enfocado en pipeline |
| ActiveCampaign | Marketing+CRM | $15+ | Bueno | Excelente | No nativo | Excelente | Medio | Muchas | Sólida | Marketing automation fuerte |
| Close | Ventas con llamadas | $49+ | Muy bueno | Bueno | Excelente (nativo) | Bueno | Bueno | Medias | Sólida | SDR/Outbound (calling) |
| Zoho CRM | Generalista | $14+ | Bueno | Bueno | Opcional | Medio | Bueno | Amplias | Sólida | Costo-efectivo, flexible |
| Salesforce (Essentials/Pro) | Enterprise | $25+/user | Muy bueno | Muy bueno | Opcional | Bueno | Excelente | Muy amplias | Sólida | Escalabilidad y compliance |

Notas: precios orientativos; revisar sitio oficial para actualizaciones.

---

## Tabla comparativa visual rápida (por necesidad)

| Necesidad | HubSpot | Pipedrive | ActiveCampaign | Close | Zoho | Salesforce |
|-----------|---------|-----------|----------------|-------|------|------------|
| **Precio accesible** (<$50/mes) | ✅ Free tier | ✅ $15 | ✅ $15 | ❌ $49+ | ✅ $14 | ❌ $25+/user |
| **Pipeline simple** | ✅ | ✅✅ | ✅ | ✅✅ | ✅ | ✅✅ |
| **Marketing automation** | ✅✅ | ⚠️ Add-ons | ✅✅✅ | ❌ | ⚠️ Flow | ✅✅ |
| **Llamadas/VoIP nativo** | ❌ | ⚠️ Apps | ❌ | ✅✅✅ | ⚠️ Apps | ⚠️ Apps |
| **Lead scoring avanzado** | ✅✅ | ⚠️ | ✅✅✅ | ⚠️ | ✅ | ✅✅ |
| **Email marketing incluido** | ✅✅ | ❌ | ✅✅✅ | ❌ | ⚠️ | ⚠️ |
| **Reportes avanzados** | ✅✅ | ✅ | ⚠️ | ✅ | ✅ | ✅✅✅ |
| **Fácil de usar** | ✅✅ | ✅✅✅ | ✅ | ✅✅ | ✅ | ⚠️ |
| **Integraciones amplias** | ✅✅✅ | ✅✅ | ✅✅ | ✅ | ✅✅ | ✅✅✅ |
| **Escalabilidad enterprise** | ✅✅ | ⚠️ | ✅ | ⚠️ | ✅ | ✅✅✅ |

**Leyenda**: ✅✅✅ Excelente | ✅✅ Muy bueno | ✅ Bueno | ⚠️ Limitado/Requiere add-ons | ❌ No disponible

---

## Recomendaciones por caso de uso
- Outbound SDR con llamadas: Close o Pipedrive + Aircall.
- Inbound + marketing automation: HubSpot Starter o ActiveCampaign.
- Equipo pequeño sin dev: HubSpot Free/Starter o Pipedrive.
- Presupuesto ajustado con flexibilidad: Zoho CRM.
- Escalar con reporting/compliance: Salesforce.

---

## Decision Tree Visual (elige en 2 minutos)

```
¿Priorizas llamadas/outbound?
├─ Sí → ¿Presupuesto < $100/mes?
│   ├─ Sí → Pipedrive + Aircall
│   └─ No → Close (nativo)
│
└─ No → ¿Inbound/marketing automation?
    ├─ Sí → ¿Equipo < 10 personas?
    │   ├─ Sí → HubSpot Starter
    │   └─ No → ActiveCampaign
    │
    └─ No → ¿Flexibilidad > costo?
        ├─ Sí → Zoho CRM + Make
        └─ No → HubSpot Free/Starter
```

**Preguntas clave antes de elegir**:
1. ¿Vendes B2B con SDRs? → Prioriza pipeline (Close/Pipedrive).
2. ¿Haces inbound/educación? → Prioriza automatización (HubSpot/AC).
3. ¿Presupuesto < $50/mes? → Zoho CRM o HubSpot Free.
4. ¿Necesitas compliance enterprise? → Salesforce o HubSpot Enterprise.

---

## Quick Wins por CRM (setup < 30 min)

### HubSpot
- **Asignación automática por reglas** (10 min): Owner round-robin o por país/persona.
- **Nurture básico** (15 min): Workflow "Si lead_score >= 40, enviar email demo".
- **UTM tracking en forms** (10 min): Hidden fields + workflow set `first_utm_*`.

### Pipedrive
- **SLA reminder** (10 min): Tarea automática "Call now" al crear lead (vencimiento 15 min).
- **Calendly → Deal** (15 min): Zap/Make que crea Deal en etapa "Demo" al agendar.
- **UTM fields personalizados** (10 min): Crear campos `utm_*` y mapear desde forms.

### ActiveCampaign
- **Scoring rápido** (15 min): +5 apertura, +10 clic, +15 visita pricing; MQL si >= 40.
- **Tag por UTM campaign** (10 min): Workflow que taggea contacto con `utm_campaign` value.
- **Nurture de 3 emails** (20 min): Plantilla valor → social proof → demo CTA.

### Close
- **Aircall nativo** (5 min): Conectar cuenta, logs automáticos de llamadas.
- **Cadencia 7 toques** (20 min): Secuencia Call → Email → Call → SMS → Email → Call → Email.
- **Next step obligatorio** (10 min): Campo requerido al cambiar etapa.

### Zoho CRM
- **Make/Zap básico** (15 min): Form → Zoho → crear Lead + Task.
- **Campos UTM personalizados** (10 min): Crear Picklist `utm_source` (manual, auto desde forms).
- **Reporte funnel simple** (15 min): Dashboard con etapas y conteo.

**ROI esperado**: 2-3x en velocidad de respuesta y tasa de conversión en 30 días.

---

## Matriz de decisión (Rápida)
Usa 1-5 por criterio. Ajusta pesos según tu contexto.

```
criterio,peso,hubspot,pipedrive,activecampaign,close,zoho,salesforce
precio,0.2,4,4,3,3,5,2
facilidad_uso,0.2,4,5,3,4,3,3
pipeline,0.2,4,5,3,4,4,5
automatizacion,0.15,4,3,5,4,4,5
reportes,0.1,4,3,3,3,3,5
integraciones,0.1,5,4,4,3,4,5
voip_llamadas,0.05,2,3,1,5,2,3
```

Fórmula (Sheets) para score por herramienta:
```
=SUMPRODUCT($B$2:$B$8, C2:C8)
```

---

## Tabla de decisión por escenario (pesos preconfigurados)

Escenarios: SDR Outbound, Inbound Marketing, Bajo Presupuesto. Copia/pega en Sheets.

```
criterio,SDR_outbound,Inbound_marketing,Bajo_presupuesto
precio,0.15,0.15,0.25
facilidad_uso,0.15,0.15,0.2
pipeline,0.25,0.15,0.15
automatizacion,0.1,0.25,0.1
reportes,0.1,0.15,0.1
integraciones,0.15,0.1,0.1
voip_llamadas,0.1,0.05,0.1
```

Fórmula (Sheets) para score por escenario (ej. SDR_outbound), asumiendo esta tabla en `A2:D9` y la matriz de puntuaciones en columnas `G:M`:
```
=SUMPRODUCT(B3:B9, G3:G9)
```
Repite cambiando el rango de pesos para cada escenario (C3:C9 para Inbound, D3:D9 para Bajo presupuesto).

Sugerencia: crea rangos con nombre `pesos_sdr`, `pesos_inbound`, `pesos_budget` y usa:
```
=SUMPRODUCT(pesos_sdr, G3:G9)
```

---

## Mini Score Calculator (Sheets)

Plantilla de encabezados (pega en A1):
```
criterio,peso,hubspot,pipedrive,activecampaign,close,zoho,salesforce
```
Pesos sugeridos (B2:B8) según tu escenario y puntajes (C2:H8) del equipo. Score total por CRM (fila 10):
```
hubspot:      =SUMPRODUCT($B$2:$B$8, C2:C8)
pipedrive:    =SUMPRODUCT($B$2:$B$8, D2:D8)
activecamp.:  =SUMPRODUCT($B$2:$B$8, E2:E8)
close:        =SUMPRODUCT($B$2:$B$8, F2:F8)
zoho:         =SUMPRODUCT($B$2:$B$8, G2:G8)
salesforce:   =SUMPRODUCT($B$2:$B$8, H2:H8)
```

Formato condicional: colorea el máximo de la fila 10 en verde para elegir ganador.

---

## Checklist de integraciones por CRM (rápido)

HubSpot
- Lead Ads (Meta/Google): nativo
- WhatsApp Cloud API: partners/apps
- UTMs: campos y workflows nativos (ver `UTM_GUIDE_OUTREACH.md`)

Pipedrive
- Lead Ads: conector marketplace
- WhatsApp: integradores (WATI/Twilio/360dialog)
- UTMs: campos personalizados + Zap/Make

ActiveCampaign
- Lead Ads: vía Zapier/Make
- WhatsApp: integradores
- UTMs: nativo en campañas; en webforms con hidden fields

Close
- Lead Ads: Zap/Make
- WhatsApp: integradores; llamadas nativas
- UTMs: vía forms/links + API

Zoho CRM
- Lead Ads: Zoho Forms/Flow o marketplace
- WhatsApp: marketplace/partners
- UTMs: campos personalizados + Zoho Flow

Salesforce
- Lead Ads: AppExchange
- WhatsApp: partners (Cloud API)
- UTMs: Campaigns/Attribution + campos personalizados

Nota: siempre prueba captura de `utm_*`, `landing_url`, `referrer_url` antes de lanzar.

---

## Checklist de implementación CRM
- [ ] Definir etapas de pipeline y campos obligatorios
- [ ] Importar contactos y deals (CSV) con mapeo validado
- [ ] Conectar correo y dominio de seguimiento de enlaces
- [ ] Configurar owners, permisos y naming conventions
- [ ] Automatizaciones básicas: asignación, recordatorios, SLAs
- [ ] Tableros/reportes: funnel, actividad, win rate, ciclo
- [ ] Integraciones clave (calendly, forms, facturación)
- [ ] Acuerdos de datos (GDPR/consentimientos)
- [ ] Rutina semanal: limpieza de duplicados y health review

---

## Plan de migración (detallado)
1) Auditoría: exporta estructuras (campos/etapas) y datos actuales.
2) Modelo de datos destino: define campos equivalentes y normaliza valores.
3) Prueba piloto: 200 registros, 2 semanas con equipo reducido.
4) Validación: calidad de datos, reportes clave, adopción del equipo.
5) Migración total: ventanas, backups y plan de rollback.
6) Hiperadopción: 2-4 semanas con office hours y playbooks.

---

## Checklist de migración específico por CRM origen→destino

### Desde Notion/Airtable → HubSpot/Pipedrive/ActiveCampaign

**Pre-migración** (1 semana antes):
- [ ] Exportar todas las tablas como CSV (contactos, empresas, deals).
- [ ] Documentar campos custom y lógica de negocio (fórmulas, relaciones).
- [ ] Identificar campos que NO tienen equivalente directo.
- [ ] Crear cuenta de prueba en CRM destino (30 días gratis).

**Migración**:
- [ ] Mapear campos estándar: email, nombre, empresa, teléfono, etapa/deal stage.
- [ ] Crear campos custom equivalentes en destino (UTMs, scoring, tags).
- [ ] Importar piloto (200 registros) y validar con usuario de prueba.
- [ ] Ajustar mapeos según feedback del piloto.
- [ ] Migración completa: importar restante + activar workflows básicos.

**Post-migración** (primer mes):
- [ ] Verificar que todos los contactos/deals llegaron (conteo).
- [ ] QA de campos críticos (email único, deals con valor, UTMs).
- [ ] Capacitar equipo (2 sesiones de 1h).
- [ ] Mantener Notion/Airtable en modo "solo lectura" 30 días como backup.

### Desde HubSpot Free → HubSpot Starter/Pro

**Pre-migración**:
- [ ] Identificar features que necesitas (workflows avanzados, reportes, límite contactos).
- [ ] Exportar contactos y deals como backup (por si acaso).
- [ ] Documentar workflows actuales (screen captures o documentación).

**Migración** (suele ser upgrade, no migración real):
- [ ] Upgrade plan en HubSpot (mismo sistema, más features).
- [ ] Activar nuevas features: workflows avanzados, reportes, email marketing.
- [ ] Revisar límites: contactos, usuarios, almacenamiento.
- [ ] Reconfigurar dashboards con nuevas métricas disponibles.

**Post-migración**:
- [ ] Verificar que datos y workflows se mantienen intactos.
- [ ] Aprovechar nuevas features: crear workflows avanzados, reportes personalizados.

### Desde Pipedrive → Close (o viceversa)

**Pre-migración**:
- [ ] Exportar Personas, Organizaciones, Deals y Activities (CSV o API).
- [ ] Mapear etapas: Pipedrive stages → Close statuses.
- [ ] Documentar custom fields y lógica (ownership, campos calculados).

**Migración**:
- [ ] Usar API o import CSV: Pipedrive tiene export nativo, Close tiene import.
- [ ] Mapear: Person → Contact, Organization → Account, Deal → Opportunity.
- [ ] Verificar: ownership, fechas (created/updated), valores de deals.
- [ ] Migrar activities/llamadas (si Close, usar integración Aircall si aplica).

**Post-migración**:
- [ ] Validar pipeline visual (deals en etapas correctas).
- [ ] Configurar nuevos workflows específicos de Close (cadencia, llamadas).

### Desde Google Sheets/Excel → Cualquier CRM

**Pre-migración**:
- [ ] Normalizar datos: eliminar duplicados, estandarizar formatos (fechas, teléfonos).
- [ ] Definir campos obligatorios en destino (email, nombre mínimo).
- [ ] Limpiar datos sucios: emails inválidos, campos vacíos críticos.

**Migración**:
- [ ] Exportar Sheets como CSV limpio.
- [ ] Usar import wizard del CRM destino (todos tienen import CSV nativo).
- [ ] Mapear columnas Sheet → campos CRM.
- [ ] Validar primeros 50 registros antes de import completo.

**Post-migración**:
- [ ] Comparar conteos (Sheet vs CRM).
- [ ] Muestreo: revisar 20 registros aleatorios para QA.
- [ ] Mantener Sheet como backup por 60 días.

---

## Hoja de ruta de implementación (30 días)

Semana 1 — Fundamentos y datos
- Auditoría rápida (campos, etapas, integraciones críticas).
- Definir pipeline y campos mínimos (contact/deal) + UTMs estandarizados.
- Import piloto (≤200 registros) con mapeo validado.

Semana 2 — Automatizaciones y reporting
- Reglas básicas: asignación, recordatorios, SLAs y etiquetas.
- Dashboards: funnel, win rate, ciclo, actividad (por owner y por fuente UTM).
- Integraciones clave: calendario, email, Lead Ads/Forms.

Semana 3 — Playbooks y QA
- Secuencias SDR/Inbound activas (1 playbook por comprador/persona).
- QA de captura UTM (first/last), landing/referrer en leads reales.
- Capacitación: 2 sesiones (pipeline + tareas/SLAs).

Semana 4 — Escalado y hardening
- Expandir importaciones y automatizaciones (solo lo que probó bien).
- Health review semanal: duplicados, campos vacíos, deals atascados.
- Retro + backlog de mejoras (quincenal).

Entregables
- Pipeline y campos activos, dashboards listos, 1–2 playbooks productivos, QA de UTMs aprobado.

---

## Playbooks recomendados (enlazar a docs existentes)
- UTMs estandarizados para campañas: ver `UTM_GUIDE_OUTREACH.md`.
- Automatizaciones prioritarias: ver `docs/automatizaciones.md` y `docs/QUICK_WINS_TOP20.md`.
- Priorización de iniciativas: ver `docs/plantillas.md`.

---

## Matriz de integraciones clave

| Integración | HubSpot | Pipedrive | ActiveCampaign | Close | Zoho | Salesforce |
|-------------|---------|-----------|----------------|-------|------|------------|
| Gmail/Outlook | Nativo | Nativo | Nativo | Nativo | Nativo | Nativo |
| Calendly | App | App/Zap | App/Zap | Zap | App/Zap | App |
| WhatsApp | Apps de terceros | Apps | Apps | Apps | Apps | Apps |
| Aircall/VoIP | App | App | Zap | Nativo/App | App | App |
| Stripe | App | App/Zap | App/Zap | Zap | App/Zap | App |
| Webforms | Nativo | Nativo | Nativo | Básico | Nativo | Nativo |
| Make/Zapier | Sí | Sí | Sí | Sí | Sí | Sí |

Notas: “App” refiere a integración oficial del marketplace; “Zap” vía Zapier/Make.

Sugerencias rápidas:
- WhatsApp Cloud API: Close y HubSpot via apps/partners; Pipedrive/Zoho mediante integradores (WATI, Twilio, 360dialog).
- Lead Ads (Meta): HubSpot/Pipedrive/Zoho tienen conectores; ActiveCampaign vía Zapier/Make.
- UTMs y shortlinks: mapear `utm_*` a campos estándar (ver `UTM_GUIDE_OUTREACH.md`).

---

## Precios por niveles (orientativo)

| Herramienta | Free | Básico | Medio | Avanzado |
|-------------|------|--------|-------|----------|
| HubSpot | Sí (limitado) | Starter ~$45 | Pro ~$800 | Enterprise $$$ |
| Pipedrive | No | Essential ~$15 | Advanced ~$30 | Pro ~$60 |
| ActiveCampaign | No | Lite ~$15 | Plus ~$49 | Pro/Enterprise $$ |
| Close | No | Startup ~$49 | Professional ~$99 | Business $$$ |
| Zoho CRM | Trial | Standard ~$14 | Professional ~$23 | Enterprise ~$40 |
| Salesforce | No | Essentials ~$25 | Pro/Enterprise $$ | Unlimited $$$ |

Revisar sitios oficiales para precios actualizados y monedas locales.

---

## Seguridad y cumplimiento
- Roles y permisos granulares (mínimo: lectura/escritura por pipeline).
- Registro de actividad (audit log) y export control.
- SSO/2FA recomendado (Google Workspace/Okta).
- GDPR/CCPA: consentimiento, derecho a olvido, retención datos.
- Backups y exportación periódica (CSV/API) probado trimestral.

Sugerencia: documentar en `docs/CHECKLIST_IMPLEMENTACION.md` los controles aplicados.

---

## TCO rápido (Sheets)
Fórmula de costo total mensual estimado:
```
= (usuarios*precio_por_usuario) + licencias_extras + (zaps*precio_zap) + (minutos_llamada*precio_minuto)
```
Fórmula de costo anual:
```
= costo_mensual*12 * (1 - descuento_anual)
```
Consejo: incluir tiempo del equipo (horas*coste/h) para comparar TCO real.

---

## Escenarios/recetas sugeridas

- Outbound SDR (llamadas + email):
  - CRM: Close o Pipedrive + Aircall
  - Flujo: lead import → secuencia email → llamada → nota/resultado → task auto
  - KPIs: llamadas/día, contactos, demos agendadas, win rate

- Inbound + nurtures:
  - CRM: HubSpot Starter o ActiveCampaign
  - Flujo: formulario → lead scoring → nurtures por contenido → MQL → calificación
  - KPIs: MQLs, activación, SQLs, CAC/Payback

- Bajo presupuesto, alta flexibilidad:
  - CRM: Zoho CRM + Make + Sheets
  - Flujo: forms → Zoho → disparos Make a email/slack → reportes Sheets
  - KPIs: tiempo de ciclo, tareas completadas, coste/lead

---

## Casos de uso por industria

### SaaS B2B (producto digital)
**CRM recomendado**: HubSpot Starter o Pipedrive
**Stack típico**: CRM + Calendly + Stripe (billing)
- **Flujo**: Form → Lead Scoring → Nurture (producto) → Demo agendada → Deal
- **KPIs**: CAC, LTV, churn, MRR, demo-to-trial rate
- **Automatización clave**: Scoring por actividad (visita pricing +15), nurture por persona (Founder vs CTO)

### Ecommerce (venta directa)
**CRM recomendado**: HubSpot Free/Starter o ActiveCampaign
**Stack típico**: CRM + Shopify/WooCommerce + Email marketing
- **Flujo**: Visitante → Abandono carrito → Email recuperación → Compra → Post-venta
- **KPIs**: Cart abandonment, AOV, repeat purchase rate, CAC
- **Automatización clave**: Remarketing carrito (3d/7d/14d), post-compra nurture, segmentación por producto

### Real Estate (venta/renta propiedades)
**CRM recomendado**: Zoho CRM o HubSpot Free
**Stack típico**: CRM + WhatsApp/Email + Calendly
- **Flujo**: Lead (form/zona) → Email tour → Visita agendada → Seguimiento → Cierre
- **KPIs**: Leads por zona, tasa visita→oferta, tiempo en pipeline, comisiones
- **Automatización clave**: DMs por zona, comparables automáticos, recordatorios de visita

### Agencia (servicios/proyectos)
**CRM recomendado**: Pipedrive o HubSpot Starter
**Stack típico**: CRM + Calendly + Invoice (Stripe/Harvest)
- **Flujo**: Lead (referral/ads) → Calificación → Propuesta → Negociación → Proyecto → Invoice
- **KPIs**: Win rate, tiempo de ciclo, project margin, client satisfaction
- **Automatización clave**: Asignación por servicio/tipo cliente, seguimiento post-proyecto

### Educación/Formación (cursos/webinars)
**CRM recomendado**: ActiveCampaign o HubSpot Starter
**Stack típico**: CRM + Plataforma (Thinkific/Teachable) + Email
- **Flujo**: Lead (webinar/curso) → Nurture educativo → Inscripción → Onboarding → Upsell
- **KPIs**: Registro→pago rate, completion rate, upsell rate
- **Automatización clave**: Nurture por contenido (curso gratis → pago), seguimiento post-completado

### Consultoría B2B (servicios estratégicos)
**CRM recomendado**: Close o Pipedrive
**Stack típico**: CRM + Aircall + Calendly
- **Flujo**: Lead (inbound/outbound) → Llamada calificación → Propuesta → Negociación → Proyecto
- **KPIs**: Contact rate, demo→propuesta rate, win rate, deal size
- **Automatización clave**: SLA de contacto (<15 min), cadencia outbound, recordatorios de seguimiento

---

## Playbook SDR — Close + Aircall (llamadas + email)

Objetivo: agendar demos con respuesta en < 2 minutos y cadencia multicanal.

Campos mínimos (Close → Custom Fields)
- `lead_source` (lista: inbound|outbound|partner)
- `utm_source|medium|campaign|content|term` (texto)
- `persona` (lista)
- `next_step` (texto corto)
- `last_contact_result` (lista: vm|answered|no_answer|callback|bad_number)

Etapas pipeline (Close)
- `New` → `Attempting` → `Connected` → `Qualified` → `Demo Set` → `No Show`/`Disqualified`/`Won`

Automatizaciones
- Aircall → Close: log de llamadas, grabaciones, outcome (webhook/app nativa).
- SLA intento: crear tarea “Call now” al crear lead; vencimiento 15 min; auto‑assign por round‑robin.
- Cadencia 7 toques (10 días): Call → Email → Call → SMS/WA → Email → Call → Email.
- Reglas de `next_step`: obligatorio al mover de etapa; plantillas de texto (p. ej., “Call back 14:00 MX”).

Templates (resumen)
- Email 1 (post‑llamada): asunto “Confirmación demo — [FECHA/HORA]”; cuerpo con link Calendly.
- VM (guion breve): “Te llamé por [beneficio]. Reagendamos aquí: [Calendly]”.
- SMS/WA: “Soy [NOMBRE] de [EMPRESA]. ¿Te va bien [hora corta]? Link: [Calendly]”.

Dashboards/reporte
- Actividad por SDR (llamadas, emails, contactos, conectados, demos).
- SLA first‑touch < 15 min (% cumplido).
- Razones de pérdida (disqualify_reason) y time‑to‑connect.

KPIs objetivo
- 60–80 llamadas/día por SDR; tasa conexión 8–15%.
- Demos agendadas: 1.5–3/día.
- SLA < 15 min en 90%.

Integraciones
- Calendly → Close (crear tarea/evento); Aircall nativo; Make/Zap para WA/SMS.

Checklist de QA
- [ ] ¿Se loguean todas las llamadas con outcome y grabación?
- [ ] ¿SLA de primer intento se cumple (<15 min)?
- [ ] ¿Campos UTM llegan y se guardan?
- [ ] ¿Cadencia de 7 toques activa y medible?

---

## Playbook Inbound — HubSpot/ActiveCampaign (nurtures + Lead Ads)

Objetivo: convertir leads inbound en MQL/SQL con nurtures segmentados y UTMs trazables.

Arquitectura
- Captura: Forms (HubSpot/AC) + Meta Lead Ads (conector nativo o Zap/Make).
- Enriquecimiento: UTMs (`utm_*`), `landing_url`, `referrer_url`, `persona`, `interés`.
- Nurtures: workflows por persona/tema (3–5 emails, 10–14 días, valor + CTA demo).
- Calificación: lead scoring (aperturas/clics/visitas), umbrales MQL→SQL.

Campos mínimos
- `utm_source|medium|campaign|content|term`
- `first_utm_*`, `last_utm_*`
- `persona` (lista) y `interes` (lista)
- `lead_score` (número) y `stage` (lifecycle: subscriber→lead→mql→sql)

Workflows (resumen)
- On Form Submit (o Lead Ads): set `last_utm_*`; si `first_utm_*` vacío → set; asignar propietario por reglas.
- Nurture por persona: rama si `persona=CMO` vs `Founder` (contenidos distintos).
- Scoring: +5 abrir, +10 clic, +15 visita pricing, +25 solicitud demo. Umbral MQL=40, SQL=70.
- Hand‑off: si `lead_score>=70` → crear tarea SDR + enviar correo demo.

Emails (estructura)
- E1 Valor (día 0): caso de uso + recurso descargable.
- E2 Prueba social (día 3): testimonio/resultado concreto.
- E3 Cómo funciona (día 7): 3 pasos + video corto.
- E4 Oferta/CTA (día 12): demo 15 min o acceso gratis.

Lead Ads (Meta)
- Conector nativo (HubSpot) o Zap/Make (ActiveCampaign).
- Mapear UTMs y consentimientos; enviar automáticamente a lista/segmento.

Dashboards/KPIs
- Tasa de MQL (leads→MQL): objetivo 20–35% según canal.
- Tasa de SQL (MQL→SQL): objetivo 30–50%.
- CTR nurtures: 3–8%; tiempo a contacto SDR < 2 h hábiles.

Checklist de QA
- [ ] ¿UTMs y consentimientos mapean a los campos?
- [ ] ¿Workflows tienen salidas de error (fallback) y desactivación de duplicados?
- [ ] ¿Scoring promueve/descalifica correctamente y crea tareas?

---

## Plantillas de campos por CRM (nombres/tipos exactos)

HubSpot (Contact/Company/Deal — property name → label [type])
- `utm_source` → UTM Source [Single-line text]
- `utm_medium` → UTM Medium [Single-line text]
- `utm_campaign` → UTM Campaign [Single-line text]
- `utm_content` → UTM Content [Single-line text]
- `utm_term` → UTM Term [Single-line text]
- `first_utm_source` → First UTM Source [Single-line text]
- `first_utm_medium` → First UTM Medium [Single-line text]
- `first_utm_campaign` → First UTM Campaign [Single-line text]
- `first_utm_content` → First UTM Content [Single-line text]
- `persona` → Persona [Dropdown select]
- `interest` → Interés [Dropdown select]
- `lead_score` → Lead Score [Number]
- `lifecycle_stage` (nativa) — subscriber|lead|mql|sql [Dropdown]

Pipedrive (Person/Deal — field_key → name [type])
- `utm_source` → UTM Source [Text]
- `utm_medium` → UTM Medium [Text]
- `utm_campaign` → UTM Campaign [Text]
- `utm_content` → UTM Content [Text]
- `utm_term` → UTM Term [Text]
- `first_utm_source` → First UTM Source [Text]
- `first_utm_medium` → First UTM Medium [Text]
- `first_utm_campaign` → First UTM Campaign [Text]
- `first_utm_content` → First UTM Content [Text]
- `persona` → Persona [Single option]
- `interest` → Interés [Single option]
- `lead_score` → Lead Score [Numeric]
- `deal_stage_hint` → Next Step [Text]

Zoho CRM (Lead/Contact/Deal — API Name → Label [type])
- `utm_source` → UTM Source [Single Line]
- `utm_medium` → UTM Medium [Single Line]
- `utm_campaign` → UTM Campaign [Single Line]
- `utm_content` → UTM Content [Single Line]
- `utm_term` → UTM Term [Single Line]
- `First_UTM_Source` → First UTM Source [Single Line]
- `First_UTM_Medium` → First UTM Medium [Single Line]
- `First_UTM_Campaign` → First UTM Campaign [Single Line]
- `First_UTM_Content` → First UTM Content [Single Line]
- `Persona` → Persona [Picklist]
- `Interest` → Interés [Picklist]
- `Lead_Score` → Lead Score [Number]

ActiveCampaign (Contact — Field Tag → Name [type])
- `%UTM_SOURCE%` → UTM Source [Text input]
- `%UTM_MEDIUM%` → UTM Medium [Text input]
- `%UTM_CAMPAIGN%` → UTM Campaign [Text input]
- `%UTM_CONTENT%` → UTM Content [Text input]
- `%UTM_TERM%` → UTM Term [Text input]
- `%FIRST_UTM_SOURCE%` → First UTM Source [Text input]
- `%FIRST_UTM_MEDIUM%` → First UTM Medium [Text input]
- `%FIRST_UTM_CAMPAIGN%` → First UTM Campaign [Text input]
- `%FIRST_UTM_CONTENT%` → First UTM Content [Text input]
- `%PERSONA%` → Persona [Dropdown]
- `%INTEREST%` → Interés [Dropdown]
- `%LEAD_SCORE%` → Lead Score [Numeric]

Notas
- Crea los campos en Contact (y Deal si reportas por Deal); recipe para copiar de Contact→Deal al crear oportunidad.
- Mantén nombres API en minúsculas y sin espacios; labels amigables para el equipo.

## Checklist de adopción del equipo
- [ ] Owners definidos por cuenta/etapa; permisos configurados.
- [ ] Tareas auto (SLAs) y recordatorios activados.
- [ ] Playbooks documentados (cómo crear/avanzar deals, notas, next step).
- [ ] Dashboards compartidos (funnel, win rate, actividad por owner).
- [ ] Rituales: daily 10' pipeline; weekly health review; mensual limpieza.
- [ ] Formación: 2 sesiones + video corto de 10–15 min (uso esencial).

---

## Onboarding por CRM (primeros 30 días)

### HubSpot
**Semana 1**:
- [ ] Cuenta creada y configuración inicial (Settings → Account Setup)
- [ ] Propiedades personalizadas creadas (UTMs, persona, interés)
- [ ] Importar contactos de prueba (CSV, máximo 100 para test)
- [ ] Formulario básico creado y conectado con workflow
- [ ] Training del equipo (sesión 30 min: crear contactos, deals, usar pipeline)

**Semana 2**:
- [ ] Workflows básicos activos (asignación por UTM, scoring)
- [ ] Integración con email (Gmail/Outlook) configurada
- [ ] Dashboards personalizados creados (funnel, actividades por owner)
- [ ] Testing de captura UTMs en formularios

**Semana 3-4**:
- [ ] Migración de datos históricos completada
- [ ] Automatizaciones avanzadas (nurtures, lead routing)
- [ ] Reportes configurados y compartidos
- [ ] Documentación interna creada (playbooks por etapa)

### Pipedrive
**Semana 1**:
- [ ] Cuenta creada y pipeline personalizado configurado
- [ ] Custom fields creados (UTMs, campos específicos de tu negocio)
- [ ] Importar contactos y deals de prueba
- [ ] Training del equipo (sesión 30 min: pipeline, actividades, notas)

**Semana 2**:
- [ ] Automatizaciones básicas configuradas (asignación, tareas)
- [ ] Integración con email y calendario
- [ ] Vistas personalizadas creadas (por owner, etapa, fuente UTM)
- [ ] Testing de forms y captura UTMs

**Semana 3-4**:
- [ ] Migración completa de datos
- [ ] Workflows avanzados (score, routing)
- [ ] Reportes y analytics configurados
- [ ] Sincronización con herramientas externas (Make/Zapier si aplica)

### ActiveCampaign
**Semana 1**:
- [ ] Cuenta creada y lista inicial configurada
- [ ] Custom fields creados (UTMs, persona, scoring)
- [ ] Formulario básico creado con campos UTM ocultos
- [ ] Training del equipo (sesión 45 min: contactos, tags, automation builder)

**Semana 2**:
- [ ] Primera automation creada (form submit → tag → nurture)
- [ ] Lead scoring configurado (eventos básicos: opens, clicks)
- [ ] Segmentación por UTM campaign activa
- [ ] Testing de captura y routing por UTM

**Semana 3-4**:
- [ ] Automations complejas (nurtures, scoring avanzado)
- [ ] Migración de datos y lista histórica importada
- [ ] Reportes de performance configurados
- [ ] Integración con CRM externo si aplica (Deals)

### Close
**Semana 1**:
- [ ] Cuenta creada y pipelines configurados
- [ ] Custom fields creados (UTMs, tipo de lead)
- [ ] Integración con Aircall/teléfono configurada
- [ ] Training del equipo (sesión 30 min: leads, llamadas, notas, pipeline)

**Semana 2**:
- [ ] Automatizaciones básicas (asignación, tareas post-llamada)
- [ ] Power dialer configurado y probado
- [ ] Integración con email y calendario
- [ ] Testing de captura UTMs desde forms

**Semana 3-4**:
- [ ] Migración de datos históricos
- [ ] Workflows avanzados (cadencia, follow-ups automáticos)
- [ ] Reportes de actividad y performance
- [ ] Integración con herramientas de outreach (LinkedIn, email)

---

## FAQ

### Migración y setup
**¿Puedo empezar con Notion/Airtable y migrar luego?**
- Sí, pero define desde el día 1 campos compatibles (email, empresa, estado) y IDs estables para facilitar la migración.
- Exporta CSV mensualmente para backup y prueba de migración.

**¿Cuánto tiempo toma implementar un CRM básico?**
- Setup inicial (campos, integraciones básicas): 2-5 días
- Importación de datos: 1-2 días según volumen
- Training del equipo: 1 semana
- Total recomendado: 2-3 semanas para rollout completo

**¿Necesito un desarrollador para implementar?**
- No obligatorio: HubSpot/Pipedrive/ActiveCampaign tienen interfaces visuales para workflows.
- Recomendado si: integraciones complejas (APIs custom), automatizaciones avanzadas, o alto volumen (>10k contactos).

### Estrategia y priorización
**¿Qué priorizo: pipeline o automatización?**
- Si vendes B2B con SDRs: **pipeline** (Close, Pipedrive) → velocidad en deals y seguimiento
- Si haces inbound/educación: **automatización** (HubSpot, ActiveCampaign) → nurtures y lead scoring
- Si tienes ambos: HubSpot Starter combina ambos bien

**¿Cuántos campos personalizados necesito?**
- Mínimo: 5 campos UTM + email + nombre + empresa = ~10 campos
- Óptimo: + persona + interés + lead_score + lifecycle = ~15-20 campos
- Evita >30 campos (sobrecarga para usuarios, menor adopción)

### Lock-in y portabilidad
**¿Cómo evitar lock-in?**
- Exportaciones mensuales (CSV) de contactos y deals
- Uso de UTMs estandarizados (portables entre sistemas)
- Automatización vía Make/Zap en lugar de lógica cerrada del CRM
- APIs abiertas: asegura acceso programático a tus datos

**¿Puedo usar múltiples CRMs?**
- No recomendado: duplicación de datos, confusión del equipo, costos dobles
- Excepción: si segmentas por región/producto y necesitas diferentes features por segmento

### UTMs y tracking
**¿Cómo aseguro que los UTMs se capturan correctamente?**
- Hidden fields en todos los forms que lean querystring antes del submit.
- Reglas en CRM: `first_utm_*` solo si vacío, `last_utm_*` siempre actualizar.
- QA: probar con link de prueba, verificar en CRM que los 5 campos UTM lleguen.
- Ver guía completa: `UTM_GUIDE_OUTREACH.md`

**¿Qué hago si tengo leads sin UTMs?**
- Setear defaults: `utm_source=direct`, `utm_medium=none`, `utm_campaign=organic`.
- Esto permite reportear "direct" vs campañas pagadas/orgánicas.

### Integraciones y automatización
**¿Cuántos Zaps/Make necesito realmente?**
- Mínimo viable: Form → CRM, Calendly → Deal, Email abierto → Score +1.
- Recomendado: 5-10 automatizaciones core antes de expandir.
- Evita "Zap sprawl": revisa mensualmente qué se usa y elimina las obsoletas.

**¿Qué integración es más crítica?**
- 1) Forms → CRM (captura UTMs y datos).
- 2) Calendly/calendario → Deal (automatiza agendamiento).
- 3) Email tracking → Scoring (actividad visible).
- 4) Slack/notificaciones → Alertas de deals (visibilidad equipo).

### Timing y cambios
**¿Cuándo es momento de cambiar de CRM?**
- Señales: el equipo evita usar el CRM, reportes no cubren necesidades, límites técnicos bloquean crecimiento.
- Antes de cambiar: evalúa si es problema de configuración (workflows, campos) o limitaciones reales del CRM.
- Recomendación: prueba piloto en nuevo CRM (200 registros, 2 semanas) antes de migración completa.

**¿Free tier de HubSpot es suficiente para empezar?**
- Sí si: <2k contactos, <5 usuarios, no necesitas workflows complejos ni reportes avanzados.
- Migra a Starter cuando: necesites automatización (workflows), mejores reportes, o >2k contactos.
- Limitaciones comunes: 1 dashboard, workflows básicos, email marketing limitado.

### UTMs y tracking
**¿Qué pasa si un contacto visita con diferentes UTMs múltiples veces?**
- `first_utm_*`: guarda solo la primera visita (atribución inicial)
- `last_utm_*`: actualiza siempre (última interacción)
- Mejores prácticas: usa `first_utm_*` para atribución, `last_utm_*` para reengagement

**¿Necesito capturar todos los 5 parámetros UTM?**
- Mínimo recomendado: `utm_source`, `utm_medium`, `utm_campaign` (trazabilidad básica)
- Óptimo: + `utm_content` (variantes A/B), `utm_term` (keywords/audiencia)
- Sin `utm_content`: no puedes comparar variantes creativas en reportes

### Costos y ROI
**¿Cuál es el ROI típico de un CRM?**
- Equipos <10: ROI visible en 2-3 meses (automatización ahorra 5-10h/semana)
- Equipos 10-50: ROI en 1-2 meses (mejor pipeline visibility, menos leaks)
- Enterprise: ROI en 3-6 meses (compliance, reporting avanzado)

**¿Puedo empezar gratis y escalar?**
- Sí: HubSpot Free (10k contactos), Zoho CRM (hasta cierto límite)
- Cuidado: funcionalidades limitadas (menos automatización, reportes básicos)
- Migrar desde free a paid es fácil (mismo sistema, más features)

---

## Métricas y KPIs recomendados (por tipo de negocio)

### SaaS B2B (ventas complejas)
**KPIs principales**:
- **MQL → SQL**: objetivo 30-50% (calificación de calidad)
- **SQL → Demo**: objetivo 50-70% (velocidad de respuesta)
- **Demo → Cierre**: objetivo 15-25% (eficiencia del proceso)
- **CAC Payback**: <12 meses (sostenibilidad)

**Métricas por UTM**:
- Leads por `utm_campaign` y `utm_content` (volumen)
- Win rate por `utm_source` (calidad)
- LTV:CAC ratio por `utm_campaign` (ROI)
- Tiempo a primer contacto por `utm_medium` (velocidad)

### Inbound/Educación (cursos, webinars)
**KPIs principales**:
- **Leads → MQL**: objetivo 20-35% (activación)
- **MQL → Registro**: objetivo 40-60% (conversión)
- **Email CTR**: objetivo 3-8% (engagement nurtures)
- **Costo por Lead (CPL)**: objetivo variable según industria

**Métricas por UTM**:
- Registros por `utm_campaign` (acquisition)
- Completion rate (webinars) por `utm_content` (engagement)
- Nurture conversion (email → demo) por `utm_source`
- Churn por `utm_campaign` (retención)

### E-commerce / DTC
**KPIs principales**:
- **AOV (Average Order Value)**: optimizar por segmento
- **Cart abandonment rate**: objetivo <70% (con remarketing)
- **ROAS**: objetivo 3-5x (Meta/Google Ads)
- **CAC**: objetivo <30% de AOV

**Métricas por UTM**:
- Revenue por `utm_campaign` y `utm_content` (attribution)
- ROAS por `utm_source` (eficiencia por canal)
- Conversion rate por `utm_term` (audiencias/keywords)
- Repeat purchase rate por `utm_campaign` (lifetime value)

### Real Estate / Servicios locales
**KPIs principales**:
- **Leads → Visit agendada**: objetivo 20-30% (calificación)
- **Visit → Oferta**: objetivo 40-60% (conversión local)
- **Tiempo a respuesta**: <2 horas hábiles (competitividad)
- **Cost per Visit**: objetivo variable por mercado

**Métricas por UTM**:
- Visitas agendadas por `utm_term` (zona/barrio)
- Conversión visita→cierre por `utm_source` (canal calidad)
- Tiempo promedio a respuesta por `utm_medium` (operación)
- Listings vistos por `utm_content` (engagement)

### Dashboard mínimo recomendado (Google Sheets/CRM)
**Columnas esenciales**:
```
utm_campaign | utm_content | Sessions | Leads | Demos | Deals | Revenue | Cost | CPA | ROAS
```
**Fórmulas clave**:
- Conversión: `=IFERROR(Leads/Sessions,0)`
- Win rate: `=IFERROR(Deals/Leads,0)`
- CPA: `=IFERROR(Cost/Leads,0)`
- ROAS: `=IFERROR(Revenue/Cost,0)`
- LTV:CAC: `=IFERROR(LTV/CAC,0)` (si tienes LTV histórico)

---

## Captura de UTMs en CRM (estándar operativo)

### Campos recomendados en Lead/Contact (crear si no existen)
- utm_source (texto)
- utm_medium (texto)
- utm_campaign (texto)
- utm_content (texto)
- utm_term (texto)
- first_utm_* (texto; para primera visita, opcional)
- last_utm_* (texto; para última visita)
- landing_url (texto)
- referrer_url (texto)
- gclid/fbclid (texto, opcional)

### Mapeo desde formularios/web (ejemplo)
- Hidden fields en formulario con lectura de querystring
- Si no hay UTMs, setear `utm_source=direct` y `utm_medium=none`

### Webhook → CRM (JSON ejemplo)
```
{
  "email": "user@dominio.com",
  "name": "Nombre Apellido",
  "phone": "+52...",
  "utm": {
    "source": "facebook",
    "medium": "remarketing",
    "campaign": "saasia_cart_7d_2025-11",
    "content": "h1_beneficio_cta_rojo_fondo_claro",
    "term": "mx_7d"
  },
  "page": {
    "landing_url": "https://tusitio.com/saas-ia",
    "referrer_url": "https://facebook.com/"
  }
}
```

### Reglas de sobreescritura (sugerido)
- first_utm_*: sólo si vacío
- last_utm_*: siempre (última interacción)
- Mantener histórico en notas/actividad si el CRM lo permite

### QA en CRM (check rápido)
- [ ] ¿Llegan los 5 campos UTM? (source/medium/campaign/content/term)
- [ ] ¿Se guarda landing_url y referrer_url?
- [ ] ¿first_utm_* sólo se escribe una vez?
- [ ] ¿Reportes por `utm_campaign` y `utm_content` existen?
- [ ] ¿Embudo por fuente/medio muestra conversión a MQL/SQL?




---

## Stack UTM‑first (recomendado por escenario)

- Curso + Webinars (inbound educativo)
  - Tracking: GA4 + `UTM_GUIDE_OUTREACH.md`
  - Shortlinks: `SHORTLINKS_UTM_SAMPLE.csv` + Bitly/Yourls
  - CRM/MA: HubSpot Starter o ActiveCampaign
  - Automatización: Make (Sheets → CRM → Email)

- SaaS demo (B2B)
  - Tracking: GA4 + Search/PMAX (`utm_term` keywords)
  - CRM: Pipedrive/Close (Calendly → Deal automático)
  - Automatización: Zap/Make (form → contacto+deal+tarea)

- Real Estate (DM/WhatsApp)
  - Tracking: UTMs `dm` + `utm_term` por zona/persona
  - CRM: Zoho CRM o HubSpot Free
  - Automatización: Make (DM → ficha → tarea visita)

---

## Recetas Make/Zapier (plantillas)

- Form → CRM (crea contacto + deal + tarea)
  - Trigger: Form submit (Webflow/Typeform/GA4 event)
  - Actions: Upsert Contact (map UTM), Create Deal, Create Task (owner por regla)

- Shortlink click → Enriquecer contacto
  - Trigger: Webhook Bitly/Yourls
  - Action: Update Contact con `last_utm_*` y campaña

- Calendly → Deal + Evento
  - Trigger: Invitee created
  - Actions: Create Deal (stage "Demo"), Activity con fecha/hora

---

## Recetas Make/Zapier detalladas (paso a paso)

### 1. Lead Ads (Meta) → CRM con UTMs

Make/Zapier:
1. Trigger: Meta Lead Ads (nuevo lead) o Webhook de Lead Ads.
2. Mapear:
   - `email`, `first_name`, `last_name`, `phone` → Contact fields
   - `utm_source=meta` (fijo) o `utm_source=facebook`/`instagram`
   - `utm_medium=lead_ads`
   - `utm_campaign` desde `ad_name` o `campaign_name` (normalizar a formato `[producto]_leadads_[yyyy-mm]`)
   - `utm_content` desde `ad_name` o `form_name` (p. ej., `h1_beneficio_cta_rojo`)
   - `utm_term` (opcional): `pais_audiencia` si disponible
3. Actions: Upsert Contact (buscar por email), set `first_utm_*` si contacto nuevo, `last_utm_*` siempre.

Variables Make/Zapier útiles:
- `{{ad_name}}` (Meta), `{{form_name}}`, `{{campaign_id}}`, `{{leadgen_id}}`

Nota: Si usas Zapier, conector "Facebook Lead Ads" tiene estos campos; Make requiere parseo manual de webhook.

---

### 2. Form → CRM con UTMs (hidden fields)

Webflow/Typeform/HubSpot Forms + Make/Zapier:
1. Trigger: Form submission.
2. Parsear hidden fields con UTMs (leídos del querystring de la página).
3. Actions:
   - Upsert Contact con campos UTM.
   - Si contacto nuevo: set `first_utm_*`; siempre: set `last_utm_*`.
   - Crear Deal (opcional) si el form incluye `product_interest`.
   - Crear Task (SLA: 15 min) si `lead_score` calculado >= umbral.

Ejemplo hidden fields (HTML):
```html
<input type="hidden" name="utm_source" id="utm_source">
<input type="hidden" name="utm_medium" id="utm_medium">
```
Script (JavaScript) para poblar desde querystring:
```javascript
const params = new URLSearchParams(window.location.search);
document.getElementById('utm_source').value = params.get('utm_source') || 'direct';
document.getElementById('utm_medium').value = params.get('utm_medium') || 'none';
```

---

### 3. Deal Stage changed → Notificación Slack/Email

Make/Zapier:
1. Trigger: Deal stage changed (o status/estado) en CRM.
2. Filters:
   - Solo si nuevo stage = "Demo Set" o "Won" o "Lost".
   - Opcional: solo deals con `value >= X`.
3. Actions:
   - Slack: mensaje a canal `#deals` con `Deal: {{deal_name}}, Stage: {{new_stage}}, Owner: {{owner_name}}, UTM: {{utm_campaign}}`.
   - Email: notificación a owner + manager (solo si stage = "Won").

Variables útiles:
- `{{deal_name}}`, `{{deal_value}}`, `{{owner_name}}`, `{{utm_campaign}}`, `{{previous_stage}}`, `{{new_stage}}`

---

## Troubleshooting común (soluciones rápidas)

Problema: UTMs no se guardan en CRM
- Verificar que los hidden fields en forms lean el querystring antes del submit.
- Comprobar que Make/Zapier recibe los campos (usar "Test" y revisar payload).
- Validar que los nombres de campos en CRM coinciden con los mapeados (case-sensitive en algunos CRMs).

Problema: Duplicados en CRM
- Usar Upsert (buscar por email único) en lugar de Create.
- Añadir filter en Make/Zapier: solo crear si email no existe.

Problema: `first_utm_*` se sobrescribe
- Regla en CRM: workflow que solo setea `first_utm_*` si está vacío.
- O en Make/Zapier: añadir filter "solo actualizar first_utm_* si Contact no tiene first_utm_source".

Problema: Lead Ads no llegan al CRM
- Verificar conexión Meta → Make/Zapier (token válido, permisos Lead Ads).
- Revisar webhook URL en Meta Lead Ads (debe apuntar a endpoint público Make/Zapier).
- Comprobar logs de errores en Make/Zapier (timeout, formato payload).

Problema: Scoring no actualiza correctamente
- Verificar que eventos (opens/clicks/visits) se disparan y llegan al CRM.
- Revisar fórmulas de scoring en workflows (sintaxis, umbrales).

---

## Reportes mínimos por UTM

- Leads por `utm_campaign` y `utm_content`
- Tasa demo/registro por `utm_campaign`
- Win rate por `utm_campaign` (SaaS)
- Tiempo a 1ª respuesta por `utm_source`

Fórmula Sheets (tasa conversión por contenido):
```
=IFERROR(Conversions_by_content/Sessions_by_content,0)
```

---

## Mapeos por CRM (campos y pasos)

### HubSpot
- Campos (Contact/Deal):
  - `utm_source` (Single-line text)
  - `utm_medium` (Single-line text)
  - `utm_campaign` (Single-line text)
  - `utm_content` (Single-line text)
  - `utm_term` (Single-line text)
  - `first_utm_*` (clonar como set-only-once vía workflow)
  - `last_utm_*` (actualizable)
- Pasos:
  1) Crear propiedades personalizadas (Settings → Properties).
  2) Formularios: agregar campos ocultos que leen querystring.
  3) Workflows: si `first_utm_source` está vacío → copiar `utm_source` (igual para medium/campaign/content/term).
  4) Deals: Workflow que copia `first_*` y `last_*` del contacto al crear deal.

### Pipedrive
- Campos (Person/Deal → Custom fields):
  - `utm_source` (Text), `utm_medium` (Text), `utm_campaign` (Text), `utm_content` (Text), `utm_term` (Text)
  - `first_utm_*` (Text), `last_utm_*` (Text)
- Pasos:
  1) Crear custom fields en Person y Deal.
  2) Form/Webhooks: enviar UTMs a Person via API/Zap/Make.
  3) Automation (Workflow): al crear Deal desde Person → copiar campos UTM.

### ActiveCampaign
- Campos (Contact → Custom fields):
  - `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
  - `first_utm_*`, `last_utm_*`
- Pasos:
  1) Crear campos personalizados.
  2) Forms: hidden fields mapeados a los campos UTM.
  3) Automations: on form submit → set `last_utm_*`; si `first_utm_*` vacío → setear.
  4) Si usas Deals: recipe para copiar de Contact a Deal al crear oportunidad.

### Close (CRM)
- Campos (Lead/Contact/Opportunity → Custom fields):
  - `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term`
  - `first_utm_*`, `last_utm_*`
- Pasos:
  1) Crear Custom Fields (Settings → Custom Fields).
  2) Ingesta: vía API/Zap/Make desde forms/shortlinks.
  3) Reglas: al crear Opportunity, copiar UTM desde Lead/Contact.

Notas generales:
- Establece convención de nombres idéntica en todos los objetos.
- Evita sobrescribir `first_*`; registra cambios de `last_*` en activity si el CRM lo permite.

---

## Ejemplos API/Payload por CRM (listos para pegar)

### HubSpot — Create Contact (v3)
Endpoint:
```
POST https://api.hubapi.com/crm/v3/objects/contacts
Authorization: Bearer {HS_API_KEY_OR_TOKEN}
Content-Type: application/json
```
Body:
```
{
  "properties": {
    "email": "usuario@dominio.com",
    "firstname": "Nombre",
    "lastname": "Apellido",
    "utm_source": "instagram",
    "utm_medium": "reel",
    "utm_campaign": "saasia_demo_ig_2025-11",
    "utm_content": "beneficio_v2",
    "utm_term": "mx_cmo",
    "first_utm_source": "instagram",
    "first_utm_medium": "reel",
    "first_utm_campaign": "saasia_demo_ig_2025-11",
    "first_utm_content": "beneficio_v2"
  }
}
```

---

## Pitfalls y riesgos comunes (evítalos)

- Elegir solo por precio sin calcular TCO/tiempo del equipo.
- No estandarizar UTMs: rompe reporting por campaña/variante (ver `UTM_GUIDE_OUTREACH.md`).
- Automatizar antes de definir pipeline y campos mínimos.
- Lock‑in por features cerradas: prioriza Make/Zap y exportabilidad.
- No capturar first/last touch (`first_utm_*`/`last_utm_*`).
- Saltar el piloto: haz prueba con ~200 leads/2 semanas antes del rollout.

### Pipedrive — Upsert Person + Create Deal
Upsert Person:
```
POST https://api.pipedrive.com/v1/persons?api_token={PD_API_TOKEN}
Content-Type: application/json
```
Body:
```
{
  "name": "Nombre Apellido",
  "email": "usuario@dominio.com",
  "phone": "+52...",
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "saasia_search_nb_2025-11",
  "utm_content": "rsas_v2",
  "utm_term": "kw_software_marketing_ia",
  "first_utm_source": "google"
}
```
Crear Deal (copiando campos):
```
POST https://api.pipedrive.com/v1/deals?api_token={PD_API_TOKEN}
Content-Type: application/json
```
Body:
```
{
  "title": "Demo SaaS — usuario@dominio.com",
  "person_id": 12345,
  "stage_id": 10,
  "utm_source": "google",
  "utm_medium": "cpc",
  "utm_campaign": "saasia_search_nb_2025-11",
  "utm_content": "rsas_v2",
  "utm_term": "kw_software_marketing_ia"
}
```

### ActiveCampaign — Create/Update Contact + Custom Fields
Endpoint (contact sync):
```
POST https://{SUBDOMAIN}.api-us1.com/api/3/contact/sync
Api-Token: {AC_API_TOKEN}
Content-Type: application/json
```
Body (usa los field IDs de tus custom fields UTM):
```
{
  "contact": {
    "email": "usuario@dominio.com",
    "firstName": "Nombre",
    "lastName": "Apellido",
    "fieldValues": [
      {"field": "utm_source", "value": "meta"},
      {"field": "utm_medium", "value": "cpc"},
      {"field": "utm_campaign", "value": "iabulk_tof_meta_2025-11"},
      {"field": "utm_content", "value": "beneficio_reel_cta_primary"},
      {"field": "utm_term", "value": "viewcontent_7d"}
    ]
  }
}
```

### Close — Create Lead with Contacts and Custom Fields
Endpoint:
```
POST https://api.close.com/api/v1/lead/
Authorization: Bearer {CLOSE_API_KEY}
Content-Type: application/json
```
Body:
```
{
  "name": "Empresa/Persona",
  "contacts": [
    {
      "name": "Nombre Apellido",
      "emails": [{"email": "usuario@dominio.com"}],
      "phones": [{"phone": "+52..."}]
    }
  ],
  "custom": {
    "utm_source": "whatsapp",
    "utm_medium": "dm",
    "utm_campaign": "realestate_dm_agendar_2025-11",
    "utm_content": "checklist-barrio_norte-reserva",
    "utm_term": "mx_buyer",
    "first_utm_source": "whatsapp"
  }
}
```

Notas:
- Ajusta nombres/IDs de campos según tu instancia (especialmente en ActiveCampaign).
- Usa autenticación segura (tokens/keys), nunca hardcodees secretos en clientes públicos.

---

## Webhooks Shortlinks → Make/Zap (actualizar `last_utm_*`)

### Bitly → Webhook → Make/Zap → CRM
- Configuración:
  1) En Bitly, crear Webhook (Event: link_click) apuntando a tu webhook público (Make/Zap).
  2) En Make/Zap, recibir JSON, resolver original `full_url` con UTMs.
  3) Buscar Contacto por email si el email viaja en query (`email` o `eid`). Si no, usar cookie/ID propio.
  4) Actualizar `last_utm_*` en CRM correspondiente.

- Ejemplo de payload Bitly (simplificado):
```
{
  "event": "link_click",
  "bitlink": "bit.ly/saasia-ig-v2",
  "referer": "instagram.com",
  "user_agent": "...",
  "link": {
    "long_url": "https://tusitio.com/landing?utm_source=instagram&utm_medium=feed&utm_campaign=saasia_demo_ig_2025-11&utm_content=beneficio_v2&email=usuario%40dominio.com"
  }
}
```

- Mapeo sugerido (Make/Zap → HubSpot/Pipedrive/AC/Close):
  - Parsear `long_url` → extraer `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, `utm_term?`, `email?`.
  - Buscar contacto por email; si no existe, crear contacto minimal.
  - Set `last_utm_*` con los valores parseados.

### Yourls (self-hosted) → Webhook → Make/Zap
- Hook: activar `YOURLS_UNIQUE_URLS` y plugin de webhook/callback.
- Payload típico:
```
{
  "shorturl": "https://yo.rl/s/ig-v2",
  "longurl": "https://tusitio.com/landing?utm_source=instagram&utm_medium=reel&utm_campaign=saasia_demo_ig_2025-11&utm_content=progressbar_v1",
  "ip": "1.2.3.4",
  "ua": "...",
  "timestamp": 1730265600
}
```
- Flujo igual que Bitly: parsear UTMs → update `last_utm_*` en CRM.

Notas:
- Si no viaja `email`, considera anexar `eid` cifrado en shortlink y resolver a contacto en tu backend.
- Guarda `last_utm_updated_at` para auditoría.

Referencia: ver “Parsers y fórmulas (UTM/email/eid)” en `UTM_GUIDE_OUTREACH.md` para regex y fórmulas de extracción.

---

## Matriz de nombres de archivos = `utm_content` (por canal)

Objetivo: que el nombre del archivo creativo y el `utm_content` coincidan 1:1.

| Canal | Formato | Patrón de filename | Ejemplo filename | Ejemplo utm_content |
|------|---------|---------------------|------------------|----------------------|
| IG Feed | Imagen/PNG | `beneficio_static_cta_primary_v{n}.png` | `beneficio_static_cta_primary_v2.png` | `beneficio_static_cta_primary_v2` |
| IG Reel | Video/MP4 | `proceso_reel_cta_demo_v{n}.mp4` | `proceso_reel_cta_demo_v1.mp4` | `proceso_reel_cta_demo_v1` |
| IG Carrusel | JPG | `resultado_carousel_slide{s}_v{n}.jpg` | `resultado_carousel_slide3_v1.jpg` | `resultado_carousel_slide3_v1` |
| Story | Video/MP4 | `countdown_story_cta_reserva_v{n}.mp4` | `countdown_story_cta_reserva_v3.mp4` | `countdown_story_cta_reserva_v3` |
| Meta Ads Static | PNG | `urgencia_static_cta_trial_v{n}.png` | `urgencia_static_cta_trial_v1.png` | `urgencia_static_cta_trial_v1` |
| Meta Ads Video | MP4 | `testimonio_video_cta_demo_v{n}.mp4` | `testimonio_video_cta_demo_v2.mp4` | `testimonio_video_cta_demo_v2` |
| Google Search | N/A | `rsas_v{n}` (en plataforma) | `rsas_v2` | `rsas_v2` |
| Google PMAX | N/A | `assetgroup_{tema}_v{n}` | `assetgroup_beneficio_v1` | `assetgroup_beneficio_v1` |
| Email | HTML/Asset | `cta_primary_v{n}` | `cta_primary_v1` | `cta_primary_v1` |
| LinkedIn Sponsored | Imagen/MP4 | `beneficio_sponsored_cta_demo_v{n}.{ext}` | `beneficio_sponsored_cta_demo_v1.mp4` | `beneficio_sponsored_cta_demo_v1` |

Notas:
- Evita espacios y mayúsculas; usa `_` y sufijo `v{n}` para versión.
- Si el asset genera múltiples variantes (carrusel), añade `slide{s}` en `utm_content` y filename.
- Mantén carpeta por campaña: `/assets/{yyyy-mm}/{utm_campaign}/`.

---

## Troubleshooting común (UTMs no llegan / duplicados / datos rotos)

### Problema: UTMs no se guardan en CRM
**Solución rápida**:
1. Verifica que los campos existan en Contact/Lead (propiedades personalizadas).
2. Revisa que los nombres de los inputs ocultos coincidan exactamente (`name="utm_source"`).
3. Si usas Make/Zapier, confirma que el mapeo de campos esté completo.
4. Debug: añade `console.log(utm)` en `utm_capture.js` y revisa DevTools.

**Ejemplo código JavaScript (utm_capture.js)**:
```javascript
// Captura UTMs de URL y popula inputs ocultos del formulario
(function() {
  const params = new URLSearchParams(window.location.search);
  const utmFields = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  
  utmFields.forEach(field => {
    const value = params.get(field) || 'direct'; // fallback a 'direct'
    const input = document.querySelector(`input[name="${field}"]`);
    if (input) {
      input.value = value;
      console.log(`${field}: ${value}`);
    }
  });
  
  // Guarda en localStorage para persistencia (opcional)
  utmFields.forEach(field => {
    const value = params.get(field);
    if (value) localStorage.setItem(field, value);
  });
})();
```

### Problema: Contactos duplicados por diferentes UTMs
- Usa email como clave única para upsert (no crear nuevo si existe).
- En HubSpot: configura workflows para fusionar por email automáticamente.
- En Pipedrive: usa "Find or create" en Make/Zapier con email como match field.

### Problema: `utm_content` cortado o mal parseado
- Valida que no haya espacios ni caracteres especiales (`@`, `#`, `%`) sin encoding.
- Limita `utm_content` a ≤100 caracteres (best practice GA4/Meta).
- Usa `encodeURIComponent()` al construir URLs manualmente.

### Problema: first_utm_* se sobreescribe
- Implementa lógica "set only if empty" en workflows (HubSpot) o scripts (Make).
- Guarda timestamp en `first_utm_timestamp` para auditoría.

---

## Mejores prácticas avanzadas (escalabilidad)

### Versionado automático
- Usa `YYYY-MM` al final de `utm_campaign` para agrupación mensual automática.
- Incrementa `_v{n}` en `utm_content` solo cuando cambias el ángulo/CTA mayor (no ajustes menores).

### Auditoría y limpieza
- Exporta UTMs mensualmente (CSV) y guarda snapshot en Sheets/BigQuery.
- Archiva campañas finalizadas; mantén shortlinks activos 90 días.
- Revisa duplicados/contactos huérfanos trimestralmente.

### Performance tracking (CRM + Analytics)
- Crea dashboard en Looker/GA4 que combine:
  - `utm_campaign` (CRM) → Leads → Demos → Deals → Revenue
  - `utm_content` (variantes) → CTR → CVR → CPA
- Fórmula ROI por campaña: `(Revenue_from_campaign - Cost_campaign) / Cost_campaign * 100`

### Seguridad y compliance
- No almacenes PII (email, teléfono) en `utm_term` si no es necesario.
- Si usas `utm_term` con identificadores, cifra o hashea antes de guardar.
- Respetar retención de datos según GDPR/CCPA (eliminar después de X meses).

---

## Checklist final (antes de lanzar campaña)

- [ ] Campos UTM creados en CRM (source, medium, campaign, content, term)
- [ ] `utm_capture.js` implementado y probado en staging
- [ ] Formularios con inputs ocultos mapeados correctamente
- [ ] Make/Zapier workflows testeados (Form → CRM → Email)
- [ ] Nombres de archivos creativos alineados con `utm_content`
- [ ] CSVs DCO/shortlinks generados y validados
- [ ] Dashboard GA4/CRM configurado para reportes por `utm_campaign`
- [ ] Documentación actualizada (`UTM_GUIDE_OUTREACH.md` y este archivo)

---

## Scripts listos (Python/JS) para automatización

### Python: Parsear UTMs desde CSV y crear contactos en CRM
```python
import csv
import requests
from urllib.parse import urlparse, parse_qs

def parse_utms_from_url(url):
    """Extrae UTMs de una URL."""
    parsed = urlparse(url)
    params = parse_qs(parsed.query)
    return {
        'utm_source': params.get('utm_source', [''])[0],
        'utm_medium': params.get('utm_medium', [''])[0],
        'utm_campaign': params.get('utm_campaign', [''])[0],
        'utm_content': params.get('utm_content', [''])[0],
        'utm_term': params.get('utm_term', [''])[0]
    }

def create_contact_in_hubspot(email, name, utm_data, api_key):
    """Crea contacto en HubSpot vía API."""
    url = 'https://api.hubapi.com/contacts/v1/contact/createOrUpdate/email/{}'.format(email)
    headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    data = {
        'properties': [
            {'property': 'email', 'value': email},
            {'property': 'firstname', 'value': name.split()[0] if name else ''},
            {'property': 'lastname', 'value': ' '.join(name.split()[1:]) if len(name.split()) > 1 else ''},
            {'property': 'utm_source', 'value': utm_data.get('utm_source', '')},
            {'property': 'utm_medium', 'value': utm_data.get('utm_medium', '')},
            {'property': 'utm_campaign', 'value': utm_data.get('utm_campaign', '')},
            {'property': 'utm_content', 'value': utm_data.get('utm_content', '')},
            {'property': 'utm_term', 'value': utm_data.get('utm_term', '')}
        ]
    }
    response = requests.post(url, json=data, headers=headers)
    return response.json()

# Uso:
# with open('leads.csv', 'r') as f:
#     reader = csv.DictReader(f)
#     for row in reader:
#         utms = parse_utms_from_url(row['landing_url'])
#         create_contact_in_hubspot(row['email'], row['name'], utms, 'YOUR_API_KEY')
```

### JavaScript: Validar y normalizar UTMs antes de enviar a CRM
```javascript
function validateAndNormalizeUTM(utm) {
  const errors = [];
  const normalized = {};
  
  // Normalizar a minúsculas y reemplazar espacios
  Object.keys(utm).forEach(key => {
    if (utm[key]) {
      normalized[key] = utm[key].toLowerCase().trim().replace(/\s+/g, '_');
      
      // Validar longitud
      if (normalized[key].length > 100) {
        errors.push(`${key} excede 100 caracteres`);
      }
      
      // Validar caracteres permitidos
      if (!/^[a-z0-9_-]+$/.test(normalized[key])) {
        errors.push(`${key} contiene caracteres no permitidos`);
      }
    }
  });
  
  return { normalized, errors };
}

// Uso:
const utm = {
  source: 'Facebook',
  medium: 'Remarketing',
  campaign: 'saas-ia-cart-7d-2025-11',
  content: 'h1_beneficio_cta_rojo'
};

const { normalized, errors } = validateAndNormalizeUTM(utm);
if (errors.length > 0) {
  console.error('Errores UTM:', errors);
} else {
  console.log('UTMs normalizados:', normalized);
}
```

---

## Queries SQL/BigQuery útiles (análisis de UTMs)

### GA4 → BigQuery: Leads por `utm_campaign` y `utm_content`
```sql
SELECT
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_campaign') AS utm_campaign,
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_content') AS utm_content,
  COUNT(DISTINCT user_pseudo_id) AS unique_users,
  COUNTIF(event_name = 'generate_lead') AS leads,
  COUNTIF(event_name = 'purchase') AS purchases,
  ROUND(COUNTIF(event_name = 'generate_lead') / COUNT(DISTINCT user_pseudo_id) * 100, 2) AS conversion_rate
FROM
  `your-project.analytics_XXXXXX.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20251101' AND '20251130'
  AND (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_source') IS NOT NULL
GROUP BY
  1, 2
ORDER BY
  leads DESC
LIMIT 50;
```

### Cohort por `utm_campaign`: tiempo de primera conversión
```sql
WITH first_touch AS (
  SELECT
    user_pseudo_id,
    (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_campaign') AS first_campaign,
    MIN(TIMESTAMP_MICROS(event_timestamp)) AS first_touch_time
  FROM
    `your-project.analytics_XXXXXX.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20251101' AND '20251130'
    AND (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_campaign') IS NOT NULL
  GROUP BY 1, 2
),
conversions AS (
  SELECT
    user_pseudo_id,
    MIN(TIMESTAMP_MICROS(event_timestamp)) AS conversion_time
  FROM
    `your-project.analytics_XXXXXX.events_*`
  WHERE
    _TABLE_SUFFIX BETWEEN '20251101' AND '20251130'
    AND event_name = 'generate_lead'
  GROUP BY 1
)
SELECT
  ft.first_campaign,
  COUNT(DISTINCT ft.user_pseudo_id) AS users,
  COUNT(DISTINCT c.user_pseudo_id) AS converted,
  ROUND(AVG(TIMESTAMP_DIFF(c.conversion_time, ft.first_touch_time, HOUR)), 1) AS avg_hours_to_convert
FROM
  first_touch ft
LEFT JOIN
  conversions c ON ft.user_pseudo_id = c.user_pseudo_id
GROUP BY
  1
ORDER BY
  converted DESC;
```

### Comparar performance por `utm_content` (variantes creativas)
```sql
SELECT
  (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_content') AS utm_content,
  COUNT(DISTINCT user_pseudo_id) AS sessions,
  COUNTIF(event_name = 'click') AS clicks,
  COUNTIF(event_name = 'generate_lead') AS leads,
  ROUND(COUNTIF(event_name = 'click') / COUNT(DISTINCT user_pseudo_id) * 100, 2) AS ctr_percent,
  ROUND(COUNTIF(event_name = 'generate_lead') / COUNTIF(event_name = 'click') * 100, 2) AS cvr_percent
FROM
  `your-project.analytics_XXXXXX.events_*`
WHERE
  _TABLE_SUFFIX BETWEEN '20251101' AND '20251130'
  AND (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_campaign') = 'saasia_cart_7d_2025-11'
  AND (SELECT value.string_value FROM UNNEST(event_params) WHERE key = 'utm_content') IS NOT NULL
GROUP BY
  1
ORDER BY
  leads DESC;
```

---

## Plantillas Make/Zapier detalladas (paso a paso)

### Make: Form Submit → Parse UTMs → HubSpot Create/Update
1. **Trigger**: Webhook (POST) → Captura payload del formulario
2. **Data Store**: Guardar `utm_*` de localStorage (si viene en payload)
3. **Router**: Si `utm_campaign` existe → flujo A; si no → flujo B (default `direct/none`)
4. **HubSpot**: Update Contact (email como match) con:
   - `utm_source` → `utm_source`
   - `utm_medium` → `utm_medium`
   - `utm_campaign` → `utm_campaign`
   - `utm_content` → `utm_content`
   - `utm_term` → `utm_term`
   - Si `first_utm_source` está vacío → copiar `utm_source` a `first_utm_source`
5. **Email**: Enviar confirmación/onboarding según `utm_campaign`

### Zapier: Shortlink Click (Bitly) → Enriquecer Contacto
1. **Trigger**: Bitly Webhook → Link Clicked
2. **Code by Zapier**: Parse `long_url` → extraer UTMs con regex
3. **Filter**: Si `utm_source` existe
4. **Find Contact** (HubSpot/Pipedrive) por email (si viene en URL o cookie)
5. **Update Contact** con `last_utm_*` y timestamp

---

## Casos de uso completos (flujos end-to-end)

### Caso 1: Lead viene de Meta Ads Remarketing → Demo agendada → Deal creado
- **Paso 1**: Usuario hace clic en anuncio Meta → UTMs en URL
- **Paso 2**: `utm_capture.js` guarda UTMs en localStorage
- **Paso 3**: Formulario de registro → UTMs enviados a CRM (hidden fields)
- **Paso 4**: CRM crea contacto con `utm_campaign = "saasia_cart_7d_2025-11"`
- **Paso 5**: Workflow CRM: si `utm_campaign` contiene `_cart_` → asignar a SDR "Remarketing"
- **Paso 6**: Calendly booking → Make/Zapier crea Deal en stage "Demo Scheduled"
- **Paso 7**: Deal cierra → Reporte: `utm_campaign` → Revenue attribution

### Caso 2: Email nurture → Click tracking → Score incrementado
- **Paso 1**: Email enviado con `utm_source=email&utm_medium=email&utm_campaign=cursoia_nurture_2025-11`
- **Paso 2**: Click en email → GA4 capta `utm_campaign`
- **Paso 3**: Webhook GA4 → Make/Zapier → Update Contact score +10
- **Paso 4**: Si score > 50 → MQL automático

---

## Templates y scripts listos para usar

### 1. HTML form con inputs ocultos UTM
```html
<form id="lead-form">
  <input type="email" name="email" required>
  <input type="text" name="name" required>
  
  <!-- Inputs ocultos para UTMs -->
  <input type="hidden" name="utm_source" id="utm_source">
  <input type="hidden" name="utm_medium" id="utm_medium">
  <input type="hidden" name="utm_campaign" id="utm_campaign">
  <input type="hidden" name="utm_content" id="utm_content">
  <input type="hidden" name="utm_term" id="utm_term">
  
  <button type="submit">Enviar</button>
</form>

<!-- Incluye utm_capture.js antes del cierre de </body> -->
<script src="utm_capture.js"></script>
```

### 2. Webhook Make/Zapier (Form → CRM)
**Estructura módulos**:
1. **Trigger**: Form submission (Typeform/Webflow/Google Forms)
2. **Parse UTMs**: Extraer de query string o form fields
3. **Router**: ¿Contact existe? (Buscar por email)
4. **Branch A (existe)**: Update contact con `last_utm_*`
5. **Branch B (no existe)**: Create contact con `first_utm_*` y `last_utm_*`
6. **Create Deal** (opcional): Stage inicial basado en `utm_campaign`

### 3. Google Sheets: Dashboard UTM performance
**Columnas sugeridas**:
```
utm_campaign | utm_content | Sessions | Leads | Demos | Deals | Revenue | Cost | CPA | ROAS | CVR
```
**Fórmulas útiles**:
- Conversión Lead → Demo: `=IFERROR(Demos/Leads,0)`
- Conversión Demo → Deal: `=IFERROR(Deals/Demos,0)`
- CPA: `=IFERROR(Cost/Leads,0)`
- ROAS: `=IFERROR(Revenue/Cost,0)`
- CVR (Sessions → Leads): `=IFERROR(Leads/Sessions,0)`
- LTV estimado por campaña: `=Revenue/Deals` (si Revenue es total lifetime)

**Formato condicional sugerido**:
- CPA: rojo si > umbral objetivo (ej. $50), verde si < umbral
- ROAS: verde si > 3.0, amarillo 2.0-3.0, rojo < 2.0
- CVR: verde si > 5%, amarillo 2-5%, rojo < 2%

### 4. Script HubSpot Workflow: Asignar owner por UTM
**Workflow conditions (IF/THEN)**:
```
IF utm_campaign contains "linkedin" → THEN Assign to owner "LinkedIn Team"
IF utm_source equals "meta" → THEN Assign to owner "Meta Ads Team"  
IF utm_content contains "_cart_" → THEN Assign to owner "Remarketing SDR"
IF utm_campaign contains "cursoia" → THEN Assign to owner "Education Team"
IF utm_source equals "email" AND utm_medium equals "email" → THEN Assign to owner "Email Marketing"
```

**Prioridad**: Evalúa de más específico a más general (primero `utm_content`, luego `utm_campaign`, luego `utm_source`).

### 5. Google App Script: Sincronizar GA4 → Sheets → CRM
```javascript
function syncGA4ToCRM() {
  // 1. Obtener datos de GA4 (últimas 24h)
  const ga4Data = getGA4Data(); // función helper
  
  // 2. Agregar por utm_campaign
  const aggregated = aggregateByCampaign(ga4Data);
  
  // 3. Escribir en Sheets
  const sheet = SpreadsheetApp.getActiveSheet();
  sheet.clear();
  sheet.getRange(1, 1, aggregated.length, Object.keys(aggregated[0]).length)
    .setValues([Object.keys(aggregated[0]), ...aggregated.map(r => Object.values(r))]);
  
  // 4. Si hay nuevos leads, actualizar CRM vía API
  aggregated.forEach(row => {
    if (row.leads > 0) {
      updateCRMCampaign(row.utm_campaign, { sessions: row.sessions, leads: row.leads });
    }
  });
}

// Ejecutar cada hora (Trigger → Time-driven → Hour timer)
```

---

## Recursos adicionales y herramientas

### Herramientas de testing UTM
- **Google Campaign URL Builder**: Construye URLs con UTMs (oficial)
- **UTM.io**: Validador y constructor visual de UTMs
- **Bitly**: Acortador con analytics integrado

### Documentación oficial APIs
- [HubSpot API v3](https://developers.hubspot.com/docs/api/overview)
- [Pipedrive API](https://developers.pipedrive.com/docs/api/v1)
- [ActiveCampaign API](https://developers.activecampaign.com/reference/overview)
- [Close API](https://developer.close.com/)

### Comunidades y soporte
- **HubSpot Community**: forums.hubspot.com
- **Make.com Templates**: make.com/templates
- **Zapier Community**: community.zapier.com

---

## Referencias rápidas

- **Guía completa UTMs**: [`UTM_GUIDE_OUTREACH.md`](./UTM_GUIDE_OUTREACH.md)
- **Variantes creativas**: [`Variantes_RealEstate_Tu.md`](./Variantes_RealEstate_Tu.md)
- **UTM Capture JS**: [`utm_capture.js`](./utm_capture.js) | [`README_UTM_CAPTURE.md`](./README_UTM_CAPTURE.md)
- **Feeds DCO/Shortlinks**: `META_DCO_FEED_TEMPLATE.csv`, `SHORTLINKS_TEMPLATE.csv`
- **Export map**: `META_EXPORT_MAP.csv`

---

## Testing y validación de UTMs (checklist QA)

### Test manual rápido (5 minutos)

1. **URL con UTMs**: Visita `https://tusitio.com/?utm_source=test&utm_campaign=test_2025-11`
2. **Verifica localStorage**: DevTools → Application → localStorage → `utm_last`
3. **Abre formulario**: Los inputs ocultos deberían autocompletarse
4. **Envia formulario**: Revisa payload (Network tab) que incluye UTMs
5. **Verifica CRM**: Contacto creado con campos UTM correctos

### Test automatizado (JavaScript)

```javascript
// Ejecutar en consola después de cargar utm_capture.js
function testUTMCapture() {
  const tests = [];
  
  // Test 1: UTMs se guardan
  const last = UTMCapture.getLast();
  tests.push({
    name: 'UTMs guardados en localStorage',
    pass: last && last.source !== undefined
  });
  
  // Test 2: Inputs se autocompletan
  const inputs = document.querySelectorAll('[name^="utm_"]');
  const filled = Array.from(inputs).filter(el => el.value).length;
  tests.push({
    name: 'Inputs ocultos autocompletados',
    pass: filled > 0
  });
  
  // Test 3: First touch solo una vez
  const first = UTMCapture.getFirst();
  const firstAgain = UTMCapture.getFirst();
  tests.push({
    name: 'First touch no se sobreescribe',
    pass: first && firstAgain && first.ts === firstAgain.ts
  });
  
  // Reporte
  console.table(tests);
  const passed = tests.filter(t => t.pass).length;
  console.log(`✅ ${passed}/${tests.length} tests pasados`);
  
  return tests;
}

// Ejecutar: testUTMCapture();
```

### Validación de datos en CRM

**Query SQL (HubSpot/Pipedrive export)**:
```sql
-- Verificar que todos los contactos tienen UTMs (o default 'direct')
SELECT 
  COUNT(*) as total_contacts,
  COUNT(utm_source) as contacts_with_source,
  COUNT(utm_campaign) as contacts_with_campaign,
  ROUND(COUNT(utm_campaign) / COUNT(*) * 100, 2) as coverage_percent
FROM contacts
WHERE created_date >= '2025-11-01';
```

**Sheet fórmula (cobertura)**:
```
=IFERROR(COUNTIF(B:B,"<>")/COUNT(B:B)*100,0)
```

---

## KPIs recomendados por tipo de negocio

### SaaS B2B (suscripciones mensuales/anuales)
**Métricas clave**:
- **MRR (Monthly Recurring Revenue)**: Ingresos recurrentes mensuales
- **CAC (Customer Acquisition Cost)**: Coste de adquisición por cliente
- **LTV (Lifetime Value)**: Valor de vida del cliente
- **Churn Rate**: Tasa de cancelación mensual
- **Lead → Trial**: Conversión de lead a prueba gratuita (target: 10-25%)
- **Trial → Paid**: Conversión de prueba a pago (target: 15-40%)
- **CAC Payback**: Tiempo en meses para recuperar CAC (target: <12 meses)
- **LTV:CAC Ratio**: Ratio saludable ≥ 3:1

**UTMs a trackear**:
- `utm_campaign` → MRR atribuido
- `utm_content` → Variantes creativas (CTR, CVR trial)
- `utm_source` → Canal más eficiente (menor CAC)

### E-commerce / Retail
**Métricas clave**:
- **ROAS (Return on Ad Spend)**: Retorno por cada dólar gastado (target: >3.0)
- **CPA (Cost per Acquisition)**: Coste por adquisición (target: <30% del AOV)
- **AOV (Average Order Value)**: Valor promedio de pedido
- **CVR (Conversion Rate)**: Tasa de conversión sesión → compra (target: 2-5%)
- **Cart Abandonment Rate**: Tasa de carrito abandonado (target: <70%)
- **Repeat Purchase Rate**: Tasa de segunda compra (target: >25% en 90 días)

**UTMs a trackear**:
- `utm_campaign` → Revenue atribuido, ROAS
- `utm_content` → Variantes de producto/creativa (mejor AOV)
- `utm_source` → Canal más rentable (mejor ROAS)

### Educación / Cursos online
**Métricas clave**:
- **Lead → Registro**: Conversión a registro curso (target: 20-40%)
- **Registro → Completado**: Tasa de finalización (target: 60-80%)
- **CPA por Lead**: Coste por lead (target: <$10-30 según precio curso)
- **Email Open Rate**: Apertura emails (target: >30%)
- **Email Click Rate**: CTR en emails (target: >5%)
- **Upsell Rate**: Conversión a cursos premium (target: 10-20%)

**UTMs a trackear**:
- `utm_campaign` → Leads por curso, CPA
- `utm_content` → Variantes de mensaje (mejor registro)
- `utm_medium` → Email vs Ads (efectividad)

### Real Estate / Inmobiliaria
**Métricas clave**:
- **Lead → Tour agendado**: Conversión a visita (target: 15-30%)
- **Tour → Oferta**: Conversión visita a oferta (target: 40-60%)
- **Time to First Response**: Tiempo a primera respuesta (target: <15 min)
- **Follow-up Cadence**: Número de toques antes de respuesta (target: 5-7)
- **WhatsApp Response Rate**: Tasa de respuesta WhatsApp (target: >80% en 2h)

**UTMs a trackear**:
- `utm_source` → Canal más efectivo (WhatsApp vs Email vs Calls)
- `utm_content` → Tipo de propiedad/ubicación (mejor fit)
- `utm_campaign` → Zona/barrio (priorización)

---

## Flujos de decisión visual (árboles)

### ¿Qué CRM elegir? (Preguntas clave)

```
¿Equipo < 5 personas?
  ├─ Sí → ¿Presupuesto < $50/mes?
  │   ├─ Sí → HubSpot Free o Zoho CRM
  │   └─ No → HubSpot Starter o Pipedrive
  └─ No → ¿Haces llamadas activas (SDR)?
      ├─ Sí → Close o Pipedrive + Aircall
      └─ No → ¿Priorizas automatización/email?
          ├─ Sí → HubSpot Starter o ActiveCampaign
          └─ No → Zoho CRM o Pipedrive
```

### ¿Priorizar pipeline o automatización?

```
¿Tu modelo de negocio es?
  ├─ SaaS B2B → Prioriza AUTOMATIZACIÓN (nurtures, scoring)
  ├─ E-commerce → Prioriza PIPELINE (conversión rápida)
  ├─ Educación → Prioriza AUTOMATIZACIÓN (onboarding, nurtures)
  └─ Real Estate → Prioriza PIPELINE (SLA rápido, seguimiento)
```

### ¿Qué integración implementar primero?

```
¿Prioridad #1?
  ├─ Capturar leads → Forms + UTMs (Semana 1)
  ├─ Asignar leads → Workflows por UTM (Semana 2)
  ├─ Enriquecer leads → Make/Zap + APIs (Semana 3)
  └─ Reportar performance → Dashboards + Sheets (Semana 4)
```

---

## Ejemplos de métricas por canal (benchmarks)

| Canal | CTR objetivo | CVR objetivo | CPA típico | Mejor para |
|-------|--------------|--------------|------------|------------|
| **Meta Ads (Feed)** | 1.5-3.5% | 2-5% | $10-50 | E-commerce, cursos |
| **Meta Ads (Remarketing)** | 2-5% | 5-15% | $5-30 | E-commerce, SaaS |
| **Google Search** | 2-8% | 3-10% | $15-100 | SaaS, servicios B2B |
| **LinkedIn Ads** | 0.5-2% | 1-3% | $50-200 | SaaS B2B, servicios |
| **Email Marketing** | 20-30% open | 2-5% click | $0.10-1 | Nurtures, educación |
| **Instagram Orgánico** | 1-3% (stories) | 0.5-2% | N/A | Branding, cursos |
| **WhatsApp/SMS** | 80-95% open | 10-30% click | $0.05-0.2 | Real Estate, servicios locales |

**Nota**: Benchmarks varían por industria y segmentación. Usa estos como referencia inicial.

---

## Checklist de salud del CRM (trimestral)

### Calidad de datos
- [ ] Tasa de duplicados < 5%
- [ ] Campos UTM completados > 80% en leads nuevos
- [ ] Email válido > 95% (formato correcto)
- [ ] Nombres normalizados (sin "test", "ejemplo", caracteres raros)

### Automatización
- [ ] Workflows activos funcionando (revisar errores últimos 30 días)
- [ ] SLA cumplido > 90% (primer contacto < 15 min)
- [ ] Asignación automática funciona (owner correcto por UTM)
- [ ] Scoring actualiza correctamente (verificar muestra aleatoria)

### Integraciones
- [ ] Forms conectan correctamente (test mensual)
- [ ] Make/Zapier workflows sin errores repetidos
- [ ] Email tracking funciona (>80% emails tracked)
- [ ] Calendly/u otro calendario sincroniza eventos

### Reportes
- [ ] Dashboards actualizados (datos últimos 30 días)
- [ ] Reportes por `utm_campaign` disponibles y usados
- [ ] KPIs principales vs objetivos documentados
- [ ] Tendencias identificadas (mejor/peor performing)

### Team adoption
- [ ] >80% del equipo usa CRM diariamente
- [ ] Tareas y notas se crean regularmente (>50% deals con notas)
- [ ] Pipeline se actualiza semanalmente (>90% deals en etapa correcta)
- [ ] Formación reciente (últimos 6 meses) o documentación actualizada

---

## Glosario rápido CRM (términos esenciales)

**CRM** (Customer Relationship Management): Sistema para gestionar relaciones con clientes (contactos, deals, tareas).

**Pipeline**: Funnel de etapas de venta (ej: New → Qualified → Demo → Closed).

**Deal/Oportunidad**: Potencial venta con valor estimado y fecha de cierre.

**Lead**: Persona/empresa que mostró interés pero aún no calificada.

**MQL** (Marketing Qualified Lead): Lead calificado por marketing (scoring/actividad).

**SQL** (Sales Qualified Lead): Lead calificado para ventas (listo para demo/llamada).

**Lead Scoring**: Sistema de puntos por actividad (abre email +5, clic +10, visita pricing +15).

**Workflow/Automation**: Regla automática que dispara acciones (ej: si score >= 40, enviar email).

**Upsert**: Crear o actualizar registro (busca por email único, crea si no existe).

**Owner**: Persona asignada al contacto/deal responsable del seguimiento.

**SLA** (Service Level Agreement): Tiempo máximo de respuesta (ej: contactar lead en <15 min).

**UTM** (Urchin Tracking Module): Parámetros en URLs para tracking (`utm_source`, `utm_medium`, etc.).

**First Touch / Last Touch**: Primera/última interacción del lead (atribución).

**Nurture**: Secuencia de emails automáticos para educar/calentar leads.

**ROI** (Return on Investment): Retorno de inversión; en CRM: tiempo ahorrado vs coste.

**TCO** (Total Cost of Ownership): Coste total (licencias + setup + mantenimiento + tiempo equipo).

---

## Próximos pasos recomendados

### Timeline sugerido (primeros 90 días)

**Semana 1-2: Setup inicial**
1. Elige CRM usando [Matriz de decisión](#matriz-de-decisión-rápida)
2. Crea cuenta de prueba (30 días)
3. Configura campos UTM básicos (ver [Mapeos por CRM](#mapeos-por-crm-campos-y-pasos))
4. Importa 20-50 contactos de prueba

**Semana 3-4: Integraciones básicas**
1. Conecta 1 formulario con captura de UTMs
2. Configura 1 workflow de asignación por UTM
3. Prueba end-to-end: URL → Form → CRM → Verificación

**Mes 2: Automatización**
1. Implementa [Playbooks recomendados](#playbooks-recomendados-enlazar-a-docs-existentes)
2. Configura scoring básico (si aplica)
3. Dashboard inicial en Sheets o CRM

**Mes 3: Optimización**
1. Revisa reportes por `utm_campaign` y `utm_content`
2. Identifica variantes de mejor performance
3. Ajusta asignaciones y workflows según datos
4. Documenta learnings y mejores prácticas del equipo

### Checklist mensual (mantenimiento)
- [ ] Revisar duplicados y limpiar datos
- [ ] Validar que UTMs se capturan correctamente (muestra aleatoria)
- [ ] Revisar dashboards y KPIs vs objetivos
- [ ] Actualizar documentación si hay cambios en procesos
- [ ] Exportar datos UTM para backup/archivo

---

## Errores comunes y soluciones rápidas (cheat sheet)

| Problema | Síntoma | Solución rápida | Sección detallada |
|----------|---------|----------------|-------------------|
| UTMs no llegan al CRM | Campos vacíos después de submit | Verificar inputs ocultos y `utm_capture.js` | [Troubleshooting común](#troubleshooting-común-soluciones-rápidas) |
| Duplicados en CRM | Múltiples contactos mismo email | Usar Upsert en Make/Zapier, email como clave única | [Troubleshooting común](#troubleshooting-común-soluciones-rápidas) |
| `first_utm_*` se sobrescribe | Primera visita se pierde | Workflow "set only if empty" | [Reglas de sobreescritura](#reglas-de-sobreescritura-sugerido) |
| Lead Ads no llegan | Webhook sin datos | Verificar token Meta, URL webhook, permisos | [Recetas Make/Zapier detalladas](#1-lead-ads-meta--crm-con-utms) |
| Scoring no actualiza | Lead score no cambia | Validar eventos (clicks/opens) y fórmulas workflow | [Troubleshooting común](#troubleshooting-común-soluciones-rápidas) |
| Nombres archivos ≠ `utm_content` | Inconsistencia en reportes | Alinear naming (ver [Matriz nombres archivos](#matriz-de-nombres-de-archivos--utm_content-por-canal)) | [Matriz nombres archivos](#matriz-de-nombres-de-archivos--utm_content-por-canal) |
| Reportes sin datos UTM | Dashboards vacíos | Verificar que campos existen y se mapean correctamente | [Reportes mínimos por UTM](#reportes-mínimos-por-utm) |

---

## Comparación rápida: ¿Cuándo usar cada herramienta?

| Escenario | CRM recomendado | Razón clave |
|-----------|-----------------|-------------|
| Equipo < 5, sin dev | HubSpot Free | Setup rápido, buen free tier |
| SDRs haciendo llamadas | Close o Pipedrive + Aircall | VoIP nativo, pipeline visual |
| Marketing automation fuerte | HubSpot Starter o ActiveCampaign | Workflows potentes, nurtures |
| Presupuesto ajustado ($20-50/mes) | Zoho CRM o HubSpot Starter | Balance costo/features |
| Necesitas customización extrema | Zoho + Make o Salesforce | Flexibilidad máxima |
| Compliance/enterprise | Salesforce o HubSpot Enterprise | Audit logs, SSO, seguridad |
| Ya usas Notion para todo | Notion (con Make/Zap) | Continuidad, sin cambio de herramienta |

