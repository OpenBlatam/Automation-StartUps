# 🔌 Integraciones Paso a Paso

## 🎯 Integración con HubSpot (Completa)

### Paso 1: Configuración Inicial

**1.1 Crear Cuenta/Acceder:**
```
1. Ir a hubspot.com
2. Crear cuenta o iniciar sesión
3. Seleccionar plan (Free, Starter, Professional)
4. Configurar perfil de empresa
```

**1.2 Configurar Email Marketing:**
```
1. Ir a Marketing → Email
2. Configurar dominio (Settings → Domains)
3. Verificar SPF/DKIM/DMARC
4. Configurar sender name
```

---

### Paso 2: Importar Contactos

**2.1 Preparar CSV:**
```csv
Email,First Name,Last Name,Industry,Role,Company
juan@empresa.com,Juan,Pérez,Marketing,Director,Empresa A
maria@empresa.com,María,García,Consultoría,Freelancer,Empresa B
```

**2.2 Importar en HubSpot:**
```
1. Ir a Contacts → Import
2. Seleccionar archivo CSV
3. Mapear columnas
4. Verificar datos
5. Importar
```

---

### Paso 3: Crear Workflows

**3.1 Workflow Email #1 (ROI):**
```
1. Ir a Automation → Workflows
2. Crear nuevo workflow
3. Trigger: Contact property equals "email_followup" = "ready"
4. Delay: 3 días
5. Action: Send email (Email #1 ROI)
6. Update property: "email_1_sent" = true
7. Update property: "email_followup" = "waiting_2"
```

**3.2 Workflow Email #2 (Social Proof):**
```
1. Crear nuevo workflow
2. Trigger: Contact property "email_followup" = "waiting_2"
   AND "email_1_clicked" = false
3. Delay: 4 días después de email_1_sent
4. Action: Send email (Email #2 Social Proof)
5. Update property: "email_2_sent" = true
6. Update property: "email_followup" = "waiting_3"
```

**3.3 Workflow Email #3 (Urgencia):**
```
1. Crear nuevo workflow
2. Trigger: Contact property "email_followup" = "waiting_3"
   AND "email_2_clicked" = false
3. Delay: 3 días después de email_2_sent
4. Action: Send email (Email #3 Urgencia)
5. Update property: "email_3_sent" = true
6. Update property: "email_followup" = "complete"
```

---

### Paso 4: Configurar Tracking

**4.1 Google Analytics:**
```
1. Ir a Settings → Integrations
2. Conectar Google Analytics
3. Configurar eventos de conversión
4. Configurar UTM parameters
```

**4.2 Eventos Personalizados:**
```
1. Crear eventos en HubSpot
2. Configurar triggers:
   - email_opened
   - email_clicked
   - form_submitted
   - meeting_booked
```

---

## 🎯 Integración con ConvertKit (Completa)

### Paso 1: Configuración Inicial

**1.1 Crear Cuenta:**
```
1. Ir a convertkit.com
2. Crear cuenta (Free o Paid)
3. Configurar perfil
4. Verificar email
```

**1.2 Configurar Dominio:**
```
1. Ir a Settings → Advanced → Custom Domain
2. Agregar dominio
3. Configurar DNS (SPF, DKIM)
4. Verificar dominio
```

---

### Paso 2: Crear Sequences

**2.1 Sequence: Follow-up ROI**
```
1. Ir a Sequences
2. Crear nueva sequence
3. Step 1: Email #1 ROI
   - Delay: 3 días
   - Tag: "email_1_sent"
4. Step 2: Condition
   - If clicked → Stop
   - If not clicked → Continue
5. Step 3: Email #2 Social Proof
   - Delay: 4 días después de Step 1
   - Tag: "email_2_sent"
6. Step 4: Condition
   - If clicked → Stop
   - If not clicked → Continue
7. Step 5: Email #3 Urgencia
   - Delay: 3 días después de Step 2
   - Tag: "email_3_sent"
```

---

### Paso 3: Importar Suscriptores

**3.1 Preparar CSV:**
```csv
email,first_name,tags
juan@empresa.com,Juan,"prospecto,marketing"
maria@empresa.com,María,"prospecto,consultoría"
```

**3.2 Importar:**
```
1. Ir a Subscribers → Import
2. Seleccionar archivo
3. Mapear columnas
4. Asignar tags
5. Importar
```

---

## 🎯 Integración con Make.com (Completa)

### Paso 1: Configuración Inicial

**1.1 Crear Cuenta:**
```
1. Ir a make.com
2. Crear cuenta
3. Seleccionar plan
4. Verificar email
```

**1.2 Conectar Apps:**
```
1. Ir a Connections
2. Conectar ConvertKit
3. Conectar Google Sheets
4. Conectar Calendly
5. Conectar CRM (si aplica)
```

---

### Paso 2: Crear Scenario

**2.1 Scenario: Email Follow-up Inteligente**
```
Trigger: ConvertKit - Email Opened
  - Email: "Email #1 ROI"
  - Opened: Yes
  - Clicked: No
  - Delay: 24 hours

Filter: Industry = "Marketing"
  → Use Marketing Version
  → Update CRM: "segment" = "marketing"

Filter: Industry = "Consultoría"
  → Use Consultoría Version
  → Update CRM: "segment" = "consultoría"

Action: Send Email
  - Template: Personalized version
  - Update CRM: "email_1_followup_sent" = true
```

---

## 🎯 Integración con Calendly

### Paso 1: Configuración

**1.1 Crear Evento:**
```
1. Ir a Calendly
2. Crear nuevo evento
3. Tipo: "15 min Discovery Call"
4. Duración: 15 minutos
5. Configurar disponibilidad
```

**1.2 Personalizar:**
```
1. Agregar preguntas previas
2. Configurar mensaje de confirmación
3. Configurar recordatorios
4. Integrar con calendario
```

---

### Paso 2: Integrar con Emails

**2.1 Agregar Link:**
```
En cada email, agregar:
[Agendar llamada de 15 min]({link_calendly})
```

**2.2 Tracking:**
```
1. Configurar UTM parameters
2. Trackear en Google Analytics
3. Actualizar CRM cuando se agenda
```

---

## ✅ Checklist de Integración

### Pre-Integración:
- [ ] Elegir plataforma principal
- [ ] Verificar requisitos
- [ ] Preparar datos
- [ ] Configurar cuentas

### Durante Integración:
- [ ] Seguir pasos uno por uno
- [ ] Verificar cada paso
- [ ] Testear funcionalidad
- [ ] Documentar configuración

### Post-Integración:
- [ ] Test completo
- [ ] Monitorear funcionamiento
- [ ] Optimizar según necesidad
- [ ] Documentar aprendizajes

---

**Integraciones paso a paso completas para implementación sin errores.** 🔌

