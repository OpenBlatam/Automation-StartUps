---
title: "Playbook Crisis Email"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/playbook_crisis_email.md"
---

# 🚨 Playbook de Crisis para Email Marketing
## Qué hacer cuando algo sale mal

---

## 🛑 SITUACIÓN 1: Email Enviado con Error Grave

### **Escenario**
- Email enviado a toda la lista con error de copy
- Información incorrecta o promesa que no se puede cumplir
- Link roto o CTA incorrecto
- Precio o oferta errónea

### **Acción Inmediata (Primeros 10 minutos)**
1. **Pausar todos los envíos automáticos** (si aún no se enviaron todos)
2. **Identificar alcance del error:** ¿Cuántos emails ya se enviaron?
3. **Evaluar gravedad:** ¿Error fatal o menor?
4. **Decidir si enviar corrección inmediata** (si <10% enviados, mejor no)

### **Email de Corrección (Si necesario)**

**Asunto:** "Corrección importante: [Tu nombre]"
**Timing:** Enviar inmediatamente si >50% lista recibió error

**Copy:**
"Hola [Nombre],

Disculpas. Envié un email hace [X] minutos con un error.

**Lo que dije incorrectamente:**
[Error específico]

**La corrección:**
[Información correcta]

**Mi compromiso:**
[Acción para compensar si aplica, ej: "Este error no afecta tu [beneficio/descuento/garantía]"]

Lo siento por la confusión. Si tienes preguntas, responde este email.

[Tu nombre]"

---

## 🛑 SITUACIÓN 2: Deliverability Caída Drásticamente

### **Síntomas**
- Open rate cayó >50% en una semana
- Tasa de bounces aumentó >5%
- Emails van a spam masivamente
- Dominio bloqueado por ISPs

### **Diagnóstico Rápido**
```
CHECKLIST DE DIAGNÓSTICO:
- [ ] Revisar rate de bounces (debe ser <2%)
- [ ] Revisar tasa de spam complaints (debe ser <0.1%)
- [ ] Verificar SPF/DKIM/DMARC
- [ ] Revisar tasa de opens (si cae, puede ser bloqueo)
- [ ] Verificar blacklists (mxtoolbox.com)
- [ ] Revisar contenido (spam words, formato)
```

### **Acción Inmediata**

**Paso 1: Pausar Envíos (24-48 horas)**
- Detener todas las campañas automáticas
- No enviar emails nuevos

**Paso 2: Limpieza de Lista**
- Remover bounces hard (inmediato)
- Remover spam complaints (inmediato)
- Remover inactivos de 180+ días (opcional pero recomendado)

**Paso 3: Re-engagement de Lista Limpia**
- Enviar email de confirmación a lista limpia
- Solo a quienes respondan, mantener en lista activa

**Paso 4: Warm-up del Dominio**
- Empezar con volúmenes bajos (50-100 emails/día)
- Aumentar gradualmente (+20% cada día)
- Solo a lista altamente engagada inicialmente

**Paso 5: Monitoreo Intensivo**
- Trackear métricas diariamente
- Ajustar según resultados
- No escalar hasta que métricas se recuperen

---

## 🛑 SITUACIÓN 3: Queja Masiva o Crisis de Reputación

### **Escenario**
- Múltiples quejas sobre producto/servicio
- Crisis pública relacionada con la marca
- Email enviado considerado ofensivo/inadecuado

### **Respuesta Rápida**

**Email de Disculpa y Transparencia**
**Asunto:** "Un mensaje importante de [Tu nombre]"
**Timing:** Enviar dentro de 24 horas

**Copy:**
"Hola [Nombre],

Quiero hablar contigo directamente sobre [situación].

**Lo que pasó:**
[Explicación honesta y transparente]

**Lo que estamos haciendo:**
[Acciones concretas tomadas]

**Cómo te afecta:**
[Impacto específico en clientes]

**Nuestro compromiso:**
[Lo que haremos diferente]

Si tienes preguntas o preocupaciones, responde este email. Estoy aquí para escucharte.

[Tu nombre]"

### **Estrategia de Comunicación**
- Transparencia total
- No hacer excusas
- Acciones concretas, no solo palabras
- Disponibilidad para responder dudas

---

## 🛑 SITUACIÓN 4: Violación de Datos o Privacidad

### **Escenario**
- Posible breach de seguridad
- Datos comprometidos
- Violación de GDPR/privacidad

### **Acción Legal y Comunicación**

**Email de Notificación (Requerido por GDPR)**
**Asunto:** "Notificación importante sobre seguridad de datos"
**Timing:** Dentro de 72 horas (requisito GDPR)

**Copy:**
"Hola [Nombre],

**Aviso importante de seguridad:**

Hemos detectado un incidente de seguridad que puede haber afectado algunos datos.

**Qué información pudo estar comprometida:**
[Lista específica de datos, ej: "Nombre y email"]

**Qué NO fue afectado:**
[ej: "Contraseñas, información de pago"]

**Qué estamos haciendo:**
1. Investigando el incidente completamente
2. [Acción específica tomada]
3. Mejorando medidas de seguridad
4. Notificando autoridades según requerimientos legales

**Qué debes hacer:**
[Acciones recomendadas para el usuario, ej: "Cambiar contraseña si usas una"]

**Recursos:**
- Preguntas frecuentes: [Link]
- Contacto directo: [Email/Phone]

Lamentamos profundamente este incidente. Estamos comprometidos con tu seguridad y privacidad.

[Tu nombre]
[Información de contacto de compliance]"

---

## 🛑 SITUACIÓN 5: Error en Precio u Oferta

### **Escenario**
- Precio incorrecto enviado por error
- Descuento mayor al previsto
- Oferta que no se puede cumplir

### **Respuesta por Tipo de Error**

#### **Error Menor (Precio +10-20% de lo correcto)**
**Estrategia:** Honrar el error como precio especial para quienes ya recibieron
**Email:**
"Hola [Nombre],

Detecté un error en el precio que te envié. Honestamente, voy a honrar ese precio como oferta especial solo para ti.

**Precio erróneo enviado:** $[X]
**Precio correcto:** $[Y]
**Oferta especial para ti:** $[X] (precio enviado)

Esta oferta solo es válida para ti y expira en 7 días.

¿Te interesa continuar con este precio?

[Continuar con precio especial]"

#### **Error Mayor (Precio +50%+ de lo correcto)**
**Estrategia:** Disculpa + Oferta especial compensatoria
**Email:**
"Hola [Nombre],

Disculpas. Envié un precio incorrecto por error. El precio correcto es $[Y], no $[X].

**Como compensación por la confusión:**
Oferta especial solo para ti: $[Y] con 20% de descuento adicional = $[Descuento calculado]

Válido solo para ti, expira en 5 días.

¿Te interesa esta oferta especial?

[Ver oferta especial]"

---

## 🛑 SITUACIÓN 6: Lista Enviada a Personas Equivocadas

### **Escenario**
- Email de segmento A enviado a segmento B
- Email promocional enviado a lista de no promocional
- Información incorrecta según segmento

### **Respuesta Rápida**

**Email de Corrección**
**Asunto:** "Disculpas - Email enviado por error"
**Timing:** Inmediato

**Copy:**
"Hola [Nombre],

Disculpas. Te envié un email que no era apropiado para tu perfil.

**Lo que envié por error:**
[Descripción breve]

**Por qué fue un error:**
[Explicación, ej: "Era para otro segmento de usuarios"]

**Si eras el destinatario correcto:**
Este correo es solo una aclaración. Si el email anterior aplicaba para ti, sigue siendo válido.

**Si NO eras el destinatario correcto:**
Puedes ignorarlo completamente. Mi disculpa por la confusión.

Si tienes preguntas, responde este email.

[Tu nombre]"

---

## 📋 PROTOCOLO GENERAL DE CRISIS

### **Checklist de Acción Inmediata (Primeros 30 minutos)**
- [ ] Evaluar alcance del problema
- [ ] Identificar impacto en clientes
- [ ] Decidir si requiere comunicación inmediata
- [ ] Preparar mensaje de corrección/apología
- [ ] Pausar campañas automáticas si necesario
- [ ] Notificar equipo interno

### **Checklist de Seguimiento (24-48 horas)**
- [ ] Monitorear respuestas/reacciones
- [ ] Responder preguntas individuales
- [ ] Ajustar estrategia según feedback
- [ ] Documentar incidente para prevenir
- [ ] Análisis post-mortem

---

## 🎯 PREVENCIÓN DE CRISIS

### **Mejores Prácticas Preventivas**

**Pre-Envío (Siempre):**
- [ ] Revisar copy 2 veces
- [ ] Probar todos los links
- [ ] Verificar personalización funciona
- [ ] Enviar test a 2-3 emails internos
- [ ] Revisar segmentación de lista
- [ ] Verificar precios/ofertas son correctos
- [ ] Revisar timing de envío

**Monitoreo Continuo:**
- [ ] Trackear métricas diariamente
- [ ] Alertas automáticas si métricas caen drásticamente
- [ ] Revisar feedback/comentarios regularmente
- [ ] Actualizar políticas y procedimientos

---

**La mejor crisis es la que nunca pasa. Pero si pasa, respuesta rápida, honesta y acción concreta son clave.**




