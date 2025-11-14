---
title: "Dm Linkedin Integraciones"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_integraciones.md"
---

# 🔌 Integraciones: LinkedIn DMs con Herramientas Populares

## 🎯 OBJETIVO
Automatizar workflow completo: extracción → envío → tracking → análisis

---

## 🔗 ZAPIER

### Workflow 1: LinkedIn → Google Sheets → DM Automático

**Trigger:** Nueva conexión en LinkedIn
**Action 1:** Agregar fila a Google Sheets
- Campos: Nombre, Empresa, Rol, URL LinkedIn, Fecha

**Action 2:** Esperar 2 horas (delay)

**Action 3:** Enviar DM en LinkedIn
- Template personalizado desde Sheets
- Incluir UTM tracking

**Action 4:** Actualizar Sheet con estado "DM enviado"

---

### Workflow 2: Respuesta en LinkedIn → CRM Update

**Trigger:** Nueva respuesta en LinkedIn DM
**Action 1:** Leer contenido de respuesta (usar IA para clasificar)
**Action 2:** Clasificar respuesta (Positiva/Negativa/Pregunta)
**Action 3:** Actualizar contacto en HubSpot/Salesforce
- Estatus: Interesado, No interesado, En conversación
- Notas: Respuesta clasificada

**Action 4:** Si es positiva → Enviar email de seguimiento
**Action 5:** Si es pregunta → Notificar al equipo

---

### Workflow 3: CRM → LinkedIn DM (Cold Outreach)

**Trigger:** Nuevo contacto agregado en CRM con tag "LinkedIn Outreach"
**Action 1:** Leer datos del contacto (nombre, empresa, industria)
**Action 2:** Seleccionar template de DM según industria
**Action 3:** Personalizar template con datos del CRM
**Action 4:** Agregar a cola de envío (respetar límites diarios)
**Action 5:** Registrar en CRM: "DM programado [fecha]"

---

## ⚙️ MAKE (Integromat)

### Scenario 1: LinkedIn Post Engagement → Warm DM

**Module 1:** LinkedIn - Watch posts (filtrar por keywords)
**Module 2:** Si contiene keyword relevante → Trigger
**Module 3:** Comentar automáticamente (comentario de valor)
**Module 4:** Esperar 24 horas
**Module 5:** Enviar DM warm (referencia al comentario)
**Module 6:** Registrar en Airtable/Sheets

---

### Scenario 2: Tracking Automático de UTM

**Module 1:** Google Analytics - Webhook de conversión
**Module 2:** Extraer UTM parameters
**Module 3:** Buscar contacto en CRM por UTM
**Module 4:** Actualizar contacto: "Convirtió vía DM [variante]"
**Module 5:** Asignar puntuación de lead (lead scoring)

---

## 🎯 HUBSPOT

### Integración: LinkedIn Sales Navigator + HubSpot

**Setup:**
1. Conectar LinkedIn Sales Navigator con HubSpot
2. Configurar propiedades personalizadas:
   - LinkedIn DM Variant
   - LinkedIn DM Campaign
   - LinkedIn DM Response
   - LinkedIn DM Conversion Date

**Workflow Automático:**
1. Nuevo contacto desde LinkedIn → Crear en HubSpot
2. Agregar propiedades: variante, campaña, fecha
3. Asignar lista: "LinkedIn DM Outreach"
4. Trigger email sequence según variante usada

---

### Secuencia de Email Post-DM:

**Email 1 (Día 1):** Si no respondió al DM
- Tema: "¿Viste mi mensaje sobre [TEMA]?"
- Link a recurso prometido
- UTM tracking: `utm_source=email&utm_medium=followup&utm_campaign=post_dm`

**Email 2 (Día 3):** Si abrió Email 1 pero no hizo clic
- Tema: "Recurso útil para ti: [RECURSO]"
- Resumen del valor

**Email 3 (Día 7):** Si no respondió a nada
- Tema: "Pausando aquí para no saturarte"
- Opt-out claro

---

## 📊 AIRTABLE

### Base de Datos: Tracking de DMs

**Tabla 1: Prospects**
Campos:
- Nombre (Texto)
- Empresa (Texto)
- LinkedIn URL (Link)
- Industria (Select)
- Seniority (Select)
- Estado (Select: Cold, Warm, En conversación, Convertido)

**Tabla 2: DMs Enviados**
Campos:
- Prospect (Link a Tabla 1)
- Fecha (Fecha)
- Variante (Select)
- Campaña (Texto)
- Respuesta (Texto)
- Clic (Sí/No)
- Conversión (Sí/No)

**Tabla 3: Análisis**
Vista automática con fórmulas:
- Tasa de respuesta por variante
- Mejor día de semana
- ROI por campaña

**Automation:**
- Nuevo registro en Tabla 2 → Calcular métricas en Tabla 3
- Conversión → Actualizar estado en Tabla 1

---

## 🔄 PHANTOMBUSTER

### Script 1: Extracción de Prospectos

**Objetivo:** Extraer perfiles de LinkedIn según criterios

**Parámetros:**
- Keywords en perfil
- Industria
- Seniority
- Ubicación
- Tamaño empresa

**Output:** CSV con datos exportables a CRM

**Uso:**
1. Ejecutar script semanalmente
2. Filtrar resultados
3. Importar a CRM/Sheets
4. Agregar a cadencia de DMs

---

### Script 2: Envío Automático (Cuidado con Spam)

**Recomendación:** Solo usar si tienes LinkedIn Premium/Sales Navigator y respetas límites

**Parámetros:**
- CSV con prospectos
- Template de DM
- Límite: 20-30 mensajes/día máximo
- Delay entre mensajes: 10-15 minutos

**Personalización:**
- Insertar nombre automáticamente
- Variar template según industria
- Incluir UTM tracking

---

## 📧 MAILCHIMP/CONVERTKIT

### Integración: DM → Email Sequence

**Setup:**
1. Nuevo contacto desde DM → Agregar a lista específica
2. Tag según variante usada: "DM_Variante_A", "DM_Variante_B"

**Sequencia Automática:**
**Email 1:** Valor adicional (no repite lo del DM)
**Email 2:** Caso de éxito relevante
**Email 3:** Invitación a webinar/demo si aplica
**Email 4:** Oferta especial si no convirtió

**Segmentación:**
- Por variante de DM recibido
- Por industria
- Por comportamiento (clic, abrió, no abrió)

---

## 🤖 CHATGPT API (Clasificación Inteligente)

### Automatización: Clasificar Respuestas de DMs

**Workflow:**
1. Nueva respuesta en LinkedIn → Webhook
2. Enviar a ChatGPT API:
   ```
   Clasifica esta respuesta a un DM de LinkedIn en una de estas categorías:
   - Positiva (interesado)
   - Negativa (no interesado)
   - Pregunta (necesita más info)
   - Objeción (tiene dudas)
   
   Respuesta: "[RESPUESTA DEL PROSPECTO]"
   ```

3. Clasificación recibida → Actualizar CRM
4. Trigger action según clasificación:
   - Positiva → Enviar recurso/agendar demo
   - Pregunta → Responder con información
   - Objeción → Enviar respuesta de manejo de objeción
   - Negativa → Marcar como "No contactar"

---

## 📱 SLACK NOTIFICACIONES

### Notificaciones Automáticas de Eventos Clave

**Eventos a notificar:**
- Nueva respuesta positiva → Canal #leads-hot
- Nueva conversión desde DM → Canal #conversions
- Objeción común detectada → Canal #mejoras
- Bloqueo/reporte → Canal #alerts

**Setup Zapier/Make:**
- LinkedIn DM Response → Slack Message
- Formato: "🎯 Nuevo lead caliente: [Nombre] de [Empresa]. Respuesta: [Preview]"

---

## 🎯 GOOGLE ANALYTICS + DATA STUDIO

### Dashboard Automático de DMs

**Configuración:**
1. Link UTM en cada DM (ya configurado)
2. Eventos personalizados en GA para conversiones
3. Dashboard en Data Studio:

**Métricas Mostradas:**
- Total DMs enviados (por variante)
- Clics por UTM
- Conversiones por campaña
- ROI calculado
- Mejores variantes
- Trending (últimos 7 días)

**Actualización:** Automática diaria

---

## ✅ CHECKLIST DE INTEGRACIÓN

### Setup Básico:
- [ ] Conectar LinkedIn con herramienta de automatización
- [ ] Configurar tracking UTM en links
- [ ] Crear base de datos/tracking (Sheets/Airtable/CRM)
- [ ] Configurar workflows básicos

### Setup Avanzado:
- [ ] Automatizar clasificación de respuestas
- [ ] Configurar secuencias de email post-DM
- [ ] Dashboard de analytics automático
- [ ] Notificaciones de eventos clave
- [ ] Integración con CRM completo

---

## 💡 MEJORES PRÁCTICAS

### DO:
✅ Empezar simple, agregar complejidad gradualmente
✅ Testear cada integración antes de escalar
✅ Monitorear métricas de cada workflow
✅ Documentar cambios en automatizaciones
✅ Mantener backup de datos antes de automatizar

### DON'T:
❌ Automatizar envío sin personalización (riesgo de spam)
❌ Ignorar límites de LinkedIn (riesgo de bloqueo)
❌ Automatizar respuestas sin revisión humana (contexto se pierde)
❌ Olvidar monitoreo de calidad
❌ Sobre-automatizar (pierdes humanidad en mensajes)

---

## 🔒 SEGURIDAD Y COMPLIANCE

### Recomendaciones:
- Usar APIs oficiales cuando sea posible
- Respetar límites de rate limiting
- No compartir credenciales entre herramientas
- Revisar permisos de cada integración
- Cumplir con GDPR si aplica (opt-out automatizado)

---

## 📊 ROI DE INTEGRACIONES

### Tiempo Ahorrado:
- Manual: 2-3 horas/día en tracking y seguimiento
- Automatizado: 15-30 min/día en monitoreo
- **Ahorro: 1.5-2.5 horas/día**

### Mejora en Métricas:
- Tracking consistente → Mejor análisis
- Respuestas rápidas → Mejor conversión
- Seguimiento automatizado → Menos leads perdidos
- **Mejora esperada: 20-30% en conversión**

### Costo vs. Beneficio:
- Herramientas: $50-200/mes
- Tiempo ahorrado: $500-1000/mes (valor)
- **ROI: 250-500% en 3 meses**

