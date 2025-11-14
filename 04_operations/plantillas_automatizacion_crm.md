---
title: "Plantillas Automatizacion Crm"
category: "plantillas_automatizacion_crm.md"
tags: ["template"]
created: "2025-10-29"
path: "plantillas_automatizacion_crm.md"
---

# Plantillas de Automatización para CRM

Flujos y reglas recomendadas para automatizar outreach en CRM.

---

## 🎯 Objetivo de Automatización

Automatizar lo repetitivo, mantener personalización donde importa.

---

## 🔄 Flujos Principales

### Flujo 1: Nuevo Lead → Outreach

#### Trigger
- Lead agregado a lista "Nuevos Leads"
- O: Lead score >3
- O: Lead con logro reciente (<30 días)

#### Acciones Automáticas
1. **Tag con metadata**
   - Tag: `lead_nuevo`
   - Tag por industria
   - Tag por score

2. **Asignar a SDR**
   - Auto-asignar según round-robin
   - O según especialización (industria/rol)

3. **Notificar**
   - Email/Slack al SDR asignado
   - Incluir: Nombre, empresa, logro, score

4. **Agendar tarea**
   - "Personalizar y enviar DM"
   - Deadline: +2 días desde creación

5. **Crear UTM**
   - Auto-generar UTM basado en lead
   - Guardar en campo personalizado

---

### Flujo 2: DM Enviado → Seguimiento

#### Trigger
- Campo "Fecha DM Enviado" actualizado
- O: Etapa cambia a "DM Enviado"

#### Acciones Automáticas
1. **Tag**
   - Tag: `dm_enviado_[fecha]`
   - Tag por versión DM usada

2. **Agendar Seguimientos**
   - Seguimiento 1: +4 días
   - Seguimiento 2: +10 días
   - Seguimiento 3: +20 días

3. **Notificar si no hay respuesta**
   - Alerta si sin respuesta después de +6 días

4. **Registrar en analytics**
   - Enviar evento a Google Analytics (si conectado)
   - Registrar en dashboard interno

---

### Flujo 3: Respuesta Recibida → Calificación

#### Trigger
- Campo "Respuesta" = "Sí"
- O: Email/DM respondido

#### Acciones Automáticas
1. **Tag**
   - Tag: `respuesta_positiva`
   - Tag por tipo respuesta (interesado, objeción, pregunta)

2. **Notificar inmediatamente**
   - Email/Slack al SDR asignado
   - Prioridad: Alta

3. **Agendar tarea urgente**
   - "Responder lead" (deadline: +6 horas)

4. **Cambiar etapa**
   - Mover a "En Conversación" o "Calificando"

5. **Si objeción**
   - Tag: `objecion_[tipo]`
   - Sugerir respuesta basada en `OBJECTION_HANDLING_MATRIX.md`

---

### Flujo 4: Sin Respuesta → Nurture

#### Trigger
- Sin respuesta después de 3 seguimientos
- O: Último contacto >30 días sin respuesta

#### Acciones Automáticas
1. **Tag**
   - Tag: `nurture_[razon]`
   - Razón: timing, budget, qualification

2. **Mover a lista Nurture**
   - Lista: "Nurture - Largo Plazo"

3. **Agendar revisión**
   - Re-visitar en +30 días
   - O +60 días según potencial

4. **Reducir frecuencia**
   - Cambiar a nurturing (1 vez/mes)

---

### Flujo 5: Demo Agendada → Preparación

#### Trigger
- Campo "Demo Agendada" = "Sí"
- O: Evento calendario "Demo" creado

#### Acciones Automáticas
1. **Tag**
   - Tag: `demo_agendada`
   - Tag por producto

2. **Agendar preparación**
   - "Preparar demo" 1 día antes
   - Incluir: Perfil lead, industria, objeciones previas

3. **Enviar confirmación**
   - Email automático con detalles demo
   - Incluir: Link calendario, preparación sugerida

4. **Notificar**
   - Notificar a sales team
   - Incluir contexto completo del lead

---

## 📋 Reglas y Condiciones

### Regla 1: Priorización Automática

**Condición**: Score >4
**Acción**: 
- Tag: `prioridad_alta`
- Notificar inmediatamente
- Agendar para hoy o mañana

---

### Regla 2: Asignación por Especialización

**Condición**: Industria = "Fintech"
**Acción**: 
- Asignar a SDR especializado en Fintech
- Tag: `especialidad_fintech`

**Condición**: Rol = "CMO"
**Acción**: 
- Asignar a SDR con experiencia en Marketing
- Tag: `especialidad_marketing`

---

### Regla 3: Seguimiento Inteligente

**Condición**: Último contacto >7 días sin respuesta
**Acción**: 
- Tag: `seguimiento_necesario`
- Agendar tarea de seguimiento
- Sugerir template según etapa

---

### Regla 4: Cerrar Elegantemente

**Condición**: Sin respuesta después de 3 seguimientos + 30 días
**Acción**: 
- Tag: `cerrar_elegantemente`
- Sugerir template de cierre
- Mover a "Nurture" o "Cerrado" según potencial

---

## 🔧 Configuración por CRM

### ActiveCampaign

#### Listas Sugeridas
- "Nuevos Leads"
- "DM Enviado"
- "En Conversación"
- "Cualificados"
- "Nurture"
- "Convertidos"

#### Campos Personalizados
- `lead_score` (número, 0-5)
- `logro_reciente` (texto)
- `version_dm` (texto)
- `utm_campaign` (texto)
- `canal` (opciones: LinkedIn InMail, LinkedIn Connection, Email)
- `fecha_dm_enviado` (fecha)
- `fecha_ultimo_seguimiento` (fecha)
- `numero_seguimientos` (número)
- `objecion_principal` (texto)

#### Automatizaciones
- Usar "If/Then" automations para flujos descritos
- Configurar delays apropiados (días, no horas)

---

### HubSpot

#### Pipelines Sugeridos
1. "Nuevo Lead"
2. "DM Enviado"
3. "En Conversación"
4. "Cualificado"
5. "Demo Agendada"
6. "Negociación"
7. "Convertido"
8. "Cerrado - Sin Interés"
9. "Nurture"

#### Propiedades Personalizadas
- Similar a ActiveCampaign
- Usar "Smart lists" para segmentación

#### Workflows
- Configurar workflows basados en flujos descritos
- Usar "Enrollment triggers" apropiados

---

### Pipedrive

#### Stages Sugeridos
1. "Lead Identificado"
2. "DM Preparado"
3. "DM Enviado"
4. "Respuesta Recibida"
5. "Cualificado"
6. "Demo Agendada"
7. "Negociación"
8. "Ganado"

#### Campos Personalizados
- Similar estructura

#### Automatizaciones
- Usar "Automations" feature
- Configurar basado en flujos

---

## 📊 Dashboards Automáticos

### Métricas a Trackear Automáticamente

#### Por SDR (si equipo)
- DMs enviados/semana
- Tasa respuesta
- Conversiones
- CAC generado

#### Por Producto
- DMs enviados
- Respuestas
- Conversiones
- Revenue

#### Por Canal
- Tasa respuesta por canal
- CAC por canal
- Conversión por canal

---

## ⚠️ Qué NO Automatizar

### Mantener Manual
- ❌ Personalización de mensajes (debe ser genuina)
- ❌ Respuestas a leads (requiere contexto humano)
- ❌ Cualificación BANT (requiere conversación)
- ❌ Cierre de ventas (requiere relación)

---

## ✅ Mejores Prácticas

### Do (Hacer)
- ✅ Automatizar registro y tracking
- ✅ Automatizar notificaciones y recordatorios
- ✅ Automatizar agendamiento de seguimientos
- ✅ Automatizar tagging y segmentación

### Don't (No Hacer)
- ❌ Automatizar mensajes personalizados
- ❌ Automatizar respuestas complejas
- ❌ Automatizar sin revisar regularmente
- ❌ Automatizar sin mantener personalización donde importa

---

## 🔄 Revisión y Optimización

### Mensual
- Revisar efectividad de automations
- Ajustar delays/timing según datos
- Optimizar tags y segmentación

### Trimestral
- Revisar estructura completa
- Evaluar ROI de automatización
- Ajustar flujos según aprendizajes

---

## 📚 Referencias

- `AUTOMATION_PLAYBOOK_ZAPIER_MAKE.md` — Automatización con Zapier/Make
- `CRM_OUTREACH_FIELDS.csv` — Campos estándar
- `NOMENCLATURA_TAGGING.md` — Sistema de tags
- `KPI_DASHBOARD_TEMPLATE.md` — Métricas a trackear

---

**💡 Pro Tip**: La mejor automatización es invisible pero efectiva. Automatiza los procesos, no los mensajes. La personalización genuina siempre debe ser manual.




