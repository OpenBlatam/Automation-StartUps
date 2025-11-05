---
title: "Integracion Linkedin Sales Navigator"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/05_lead_generation/integracion_linkedin_sales_navigator.md"
---

# Integración con LinkedIn Sales Navigator

Guía para usar Sales Navigator eficientemente con el sistema de outreach.

---

## 🎯 Configuración Inicial

### Filtros Recomendados para Lead Generation

#### Perfil Ideal
- **Seniority Level**: Director, VP, C-Level
- **Function**: Marketing, Sales, Operations, General Management
- **Industry**: [Tu industria objetivo]
- **Company Size**: 10-500 o 500+ (según tu segmento)
- **Geography**: [Países objetivo]

#### Actualizaciones y Señales
- ✅ "Posted on LinkedIn" (últimos 7 días)
- ✅ "Changed jobs" (últimos 30 días)
- ✅ "In the news" (últimos 30 días)
- ✅ "New role" (últimos 30 días)

---

## 🔍 Workflow de Búsqueda Diaria

### Paso 1: Búsqueda Matutina (15 min)
1. Abre Sales Navigator
2. Usa filtros anteriores
3. Ordena por "Most Recent Activity"
4. Identifica top 10-15 leads del día
5. Exporta a CSV con campos estándar

### Paso 2: Validación Rápida
Para cada lead, verifica:
- [ ] Logro reciente verificable (<30 días)
- [ ] Fit de industria/rol
- [ ] Actividad en LinkedIn (posts, comentarios)
- [ ] No has contactado antes

### Paso 3: Priorización
- **Score 4-5**: Enviar esta semana, versión VIP
- **Score 2-3**: Enviar próximas 2 semanas
- **Score 0-1**: Nurture o descartar

Ver: `QUICK_SCORING_LEADS.md`

---

## 📋 Campos para Exportar desde Sales Navigator

### Información Básica
- First Name
- Last Name
- Company Name
- Title
- Location
- LinkedIn Profile URL

### Información de Contexto
- Recent Activity (últimos posts)
- Company Updates (logros recientes)
- Mutual Connections (si aplica)
- Industry
- Company Size

### Campos Personalizados (añadir manualmente)
- Logro identificado
- Versión DM a usar
- Score (1-5)
- Canal preferido (LinkedIn InMail/Connection)

---

## 🎯 Uso de InMail desde Sales Navigator

### Ventajas
- No necesitas conexión previa
- Tienes más caracteres (máx. 800)
- Tracking de aperturas (premium)

### Best Practices
- **Subject**: Menciona logro específico (ej: "Felicitaciones por [LOGRO]")
- **Apertura**: Primera línea visible — debe captar atención
- **Personalización**: Máxima — menciona logro verificable
- **CTA**: Claro y específico

Ver: `CHANNEL_VARIANTS_DM.md` → LinkedIn InMail

---

## 🔄 Workflow de Conexión + DM

### Estrategia Recomendada
1. **Connection Request** (máx. 300 chars)
   - Menciona logro o conexión común
   - No vendas, solo conecta
   - Objetivo: Aceptar conexión

2. **Espera** 1-2 días después de aceptación

3. **DM de Follow-up**
   - Agradece conexión
   - Referencia a logro mencionado
   - Pregunta abierta o propuesta de valor

Ver: `CHANNEL_VARIANTS_DM.md` → LinkedIn Connection

---

## 📊 Tracking en Sales Navigator

### Usa Saved Leads
- Crea listas por:
  - **Esta Semana**: Leads score 4-5
  - **Próximas 2 Semanas**: Leads score 2-3
  - **Nurture**: Leads score 0-1 o sin timing

### Usa Notes
Para cada lead, agrega nota con:
```
[FECHA] - DM Enviado
Producto: [PRODUCTO]
Versión: [VERSION]
Canal: [CANAL]
Logro: [LOGRO]
Próximo seguimiento: [FECHA]
```

### Usa Tags
Crea tags personalizados:
- `dm_enviado`
- `respuesta_pendiente`
- `respuesta_positiva`
- `demo_agendada`
- `convertido`

---

## 🚀 Automatización con Zapier/Make

### Flujo Recomendado
1. **Trigger**: Nuevo Saved Lead en Sales Navigator
   - O: Nueva actualización de lead (post, cambio, etc.)

2. **Action**: Agregar a CRM (ActiveCampaign, HubSpot, etc.)
   - Con campos mapeados

3. **Action**: Enriquecer con logro reciente
   - Usa herramienta de enrichment (Clay, Apollo, etc.)

4. **Action**: Notificar (Slack, Email)
   - "Nuevo lead caliente: [NOMBRE] — [LOGRO]"

### Herramientas Compatibles
- **Zapier**: LinkedIn Sales Navigator → CRM
- **Make**: Flujos más complejos con múltiples pasos
- **Clay**: Enrichment + automatización

Ver: `AUTOMATION_PLAYBOOK_ZAPIER_MAKE.md`

---

## 📈 Métricas a Trackear

### En Sales Navigator
- Leads saved por semana
- Connection requests enviados
- InMails enviados
- Tasa de aceptación de conexiones
- Tasa de respuesta a InMails

### En CRM (Externo)
- Tasa de respuesta general
- Conversión por canal
- CAC por lead source (Sales Navigator)

**Objetivo**: Integrar ambas fuentes para análisis completo.

---

## ⚠️ Límites y Best Practices

### Límites de Sales Navigator
- **InMail**: 50-150/mes (según plan)
- **Connection Requests**: 100-500/mes (según plan)
- **Saves**: Ilimitado (usa para priorización)

### Best Practices
- **No saturar**: 10-20 InMails/semana máximo
- **Calidad > Cantidad**: Solo leads score 4-5
- **Diversifica canales**: No solo Sales Navigator
- **Trackea todo**: Usa UTMs y CRM

---

## 🎯 Casos de Uso Específicos

### Lead Caliente (Evento/Premio)
1. Identifica en "In the news" o "Posted on LinkedIn"
2. Verifica logro (<7 días ideal)
3. Envía InMail o Connection + DM <48h
4. Usa versión "Evento Especial"

Ver: `TEMPLATES_EVENTOS_ESPECIALES.md`

### Lead por Industria Específica
1. Filtra por industria objetivo
2. Filtra por actualizaciones recientes
3. Exporta batch de 20-30 leads
4. Valida y prioriza con scoring
5. Envía en batch semanal

### Lead por Rol Específico (CMO, CEO, etc.)
1. Filtra por seniority + function
2. Filtra por "New role" (últimos 30 días)
3. Usa versión VIP o "Cambio de Rol"
4. Envía <7 días desde cambio

Ver: `SCRIPTS_DM_POR_ROL.md`

---

## 📚 Recursos Adicionales

### Templates
- `CHANNEL_VARIANTS_DM.md` — Versiones para LinkedIn
- `TEMPLATES_EVENTOS_ESPECIALES.md` — Para eventos/premios
- `QUICK_SCORING_LEADS.md` — Priorización rápida

### Automatización
- `AUTOMATION_PLAYBOOK_ZAPIER_MAKE.md` — Flujos automatizados
- `SCRIPT_GENERADOR_DM.py` — Generación automática desde CSV

### Tracking
- `UTM_GUIDE_OUTREACH.md` — UTMs para tracking
- `KPI_DASHBOARD_TEMPLATE.md` — Dashboard de métricas

---

## 💡 Tips Avanzados

### 1. Usa "Lead Recommendations"
Sales Navigator sugiere leads basados en:
- Tu buyer persona
- Leads guardados anteriormente
- Compañías similares

**Revisa semanalmente** para encontrar leads que no consideraste.

### 2. Aprovecha "TeamLink"
Si tu empresa tiene múltiples usuarios:
- Ve leads en común
- Pide introducciones
- Referencias internas

### 3. Monitorea "Account Updates"
Para empresas objetivo (Account-Based):
- Configura alertas de actualizaciones
- Posts de la empresa
- Cambios en empleados clave
- Logros/noticias

### 4. Usa "Spotlight" para Personalización
Muestra información de:
- Mutual connections (para referencias)
- Updates recientes (para mencionar)
- Contactos en común (para warm intro)

---

**💡 Pro Tip**: Sales Navigator es más efectivo cuando lo usas como complemento a otras fuentes (eventos, contenido, referencias). No dependas solo de búsquedas frías.

