---
title: "Troubleshooting y Solución de Problemas - Optimización de Ventas"
category: "09_sales"
tags: ["sales", "troubleshooting", "problems"]
created: "2025-01-27"
path: "TROUBLESHOOTING_VENTAS.md"
---

# 🔧 Troubleshooting y Solución de Problemas
## Guía Completa para Resolver Problemas Comunes en la Implementación

**Versión:** 1.0  
**Última actualización:** Enero 2025

---

## 🚨 PROBLEMAS COMUNES Y SOLUCIONES

### Problema 1: Lead Scoring No Está Funcionando

**Síntomas:**
- Los scores no se calculan automáticamente
- Todos los leads tienen score 0
- Scores no se actualizan

**Diagnóstico:**
```
1. Verificar que las propiedades de scoring existen en CRM
2. Verificar que los workflows están activos
3. Verificar que los triggers están configurados correctamente
4. Revisar logs de errores en CRM
```

**Soluciones:**

**Solución A: Scoring No se Calcula**
```
1. Ir a Settings → Lead Scoring en HubSpot
2. Verificar que scoring está activado
3. Verificar que los criterios están correctos
4. Probar con un lead manualmente
5. Si no funciona, desactivar y reactivar
```

**Solución B: Scores No se Actualizan**
```
1. Verificar que workflow de actualización está activo
2. Verificar que tiene permisos para actualizar
3. Revisar si hay errores en el workflow
4. Probar actualizando manualmente un lead
```

**Solución C: Scoring Muy Lento**
```
1. Reducir número de criterios (empezar con 5-10)
2. Optimizar workflows (menos branches)
3. Usar scoring batch en vez de real-time
4. Considerar usar Make.com para scoring custom
```

---

### Problema 2: Workflows No se Ejecutan

**Síntomas:**
- Emails no se envían automáticamente
- Leads no se asignan a SDRs
- Tareas no se crean

**Diagnóstico:**
```
1. Verificar que workflow está activo
2. Verificar que trigger está funcionando
3. Verificar que condiciones son correctas
4. Revisar logs del workflow
```

**Soluciones:**

**Solución A: Workflow No se Activa**
```
1. Verificar trigger: ¿Se está activando?
   - Revisar logs del workflow
   - Verificar que lead cumple condiciones
   - Probar con lead de prueba

2. Verificar condiciones: ¿Son correctas?
   - Revisar lógica IF/THEN
   - Simplificar condiciones si son muy complejas
   - Probar con condiciones simples primero
```

**Solución B: Workflow se Activa pero No Ejecuta Acciones**
```
1. Verificar permisos: ¿Tiene permisos para ejecutar acciones?
2. Verificar integraciones: ¿Están conectadas?
3. Verificar límites: ¿Se alcanzaron límites de API?
4. Revisar errores específicos en logs
```

**Solución C: Workflow se Ejecuta Múltiples Veces**
```
1. Agregar condición: "Solo si no se ha ejecutado antes"
2. Usar "Suppression list" para evitar duplicados
3. Agregar delay entre ejecuciones
4. Revisar si hay múltiples triggers activos
```

---

### Problema 3: Emails No Llegan o Llegan al Spam

**Síntomas:**
- Emails no llegan a destinatarios
- Tasa de entrega baja
- Emails van a spam

**Diagnóstico:**
```
1. Verificar configuración SPF/DKIM
2. Verificar reputación del dominio
3. Revisar tasa de bounces
4. Revisar tasa de spam complaints
```

**Soluciones:**

**Solución A: Emails No Llegan**
```
1. Verificar configuración DNS:
   - SPF record configurado
   - DKIM configurado
   - DMARC configurado

2. Verificar reputación:
   - Usar herramientas como Sender Score
   - Verificar blacklists
   - Mejorar reputación enviando a lista limpia

3. Verificar configuración del servidor:
   - IP no está en blacklist
   - Rate limits no se alcanzaron
   - Autenticación correcta
```

**Solución B: Emails Van a Spam**
```
1. Mejorar contenido:
   - Evitar palabras spam (gratis, urgente, etc.)
   - Usar texto en vez de solo imágenes
   - Incluir link de unsubscribe
   - Personalizar subject lines

2. Mejorar reputación:
   - Enviar a lista limpia y caliente
   - Evitar bounces
   - Responder a spam complaints rápidamente
   - Calentar dominio gradualmente
```

**Solución C: Tasa de Apertura Baja**
```
1. Mejorar subject lines:
   - Personalizar con nombre
   - Usar urgencia real (no falsa)
   - Hacer pregunta
   - Usar números/estadísticas

2. Mejorar timing:
   - Enviar en mejor hora (martes- jueves, 10-11am)
   - Evitar lunes y viernes
   - Considerar timezone del destinatario

3. Segmentar mejor:
   - Enviar contenido relevante
   - Personalizar por industria/rol
   - Usar lead scoring para priorizar
```

---

### Problema 4: ROI Calculator No Funciona

**Síntomas:**
- Calculator no calcula correctamente
- Resultados no se guardan en CRM
- Calculator no se envía por email

**Soluciones:**

**Solución A: Cálculos Incorrectos**
```
1. Verificar fórmulas:
   - Revisar fórmula de ROI
   - Verificar que inputs son correctos
   - Probar con datos conocidos
   - Ajustar fórmulas si necesario

2. Verificar formato de números:
   - Asegurar que números son números (no texto)
   - Verificar decimales
   - Verificar formato de moneda
```

**Solución B: Resultados No se Guardan**
```
1. Verificar integración:
   - Typeform → Make.com → HubSpot
   - Verificar webhooks
   - Verificar que datos se envían correctamente
   - Revisar logs de Make.com

2. Verificar propiedades en CRM:
   - Verificar que propiedades existen
   - Verificar que tienen permisos de escritura
   - Verificar formato de datos
```

**Solución C: Calculator No se Envía**
```
1. Verificar workflow de email:
   - ¿Se activa después de completar calculator?
   - ¿Tiene acceso a resultados?
   - ¿Template de email está correcto?

2. Verificar que email se envía:
   - Revisar logs de email
   - Verificar que email no va a spam
   - Probar con email de prueba
```

---

### Problema 5: Cross-Selling No Funciona

**Síntomas:**
- Triggers no se activan
- Emails de cross-sell no se envían
- Tasa de conversión de cross-sell baja

**Soluciones:**

**Solución A: Triggers No se Activan**
```
1. Verificar condiciones:
   - ¿Cliente completó 50%+ del curso?
   - ¿Cliente tiene 2+ productos activos?
   - ¿Health score es correcto?

2. Verificar timing:
   - ¿Trigger se activa en momento correcto?
   - ¿Hay delay necesario?
   - ¿Se ejecuta solo una vez?
```

**Solución B: Tasa de Conversión Baja**
```
1. Mejorar oferta:
   - Aumentar descuento
   - Agregar bonuses
   - Mejorar timing

2. Mejorar copy:
   - Personalizar más
   - Mostrar valor específico
   - Incluir casos de éxito similares

3. Mejorar targeting:
   - Solo a clientes satisfechos (NPS >7)
   - Solo a clientes activos
   - Solo a clientes que mostraron interés
```

---

### Problema 6: Health Score No es Preciso

**Síntomas:**
- Health score no refleja realidad
- Clientes con score alto cancelan
- Clientes con score bajo están satisfechos

**Soluciones:**

**Solución A: Ajustar Factores**
```
1. Revisar pesos:
   - Uso del producto: 40% (ajustar si necesario)
   - Engagement: 30% (ajustar si necesario)
   - Satisfacción: 20% (ajustar si necesario)
   - Tiempo desde última actividad: 10% (ajustar si necesario)

2. Agregar factores:
   - Tasa de uso de features clave
   - Tiempo de sesión
   - Frecuencia de login
   - Interacciones con soporte
```

**Solución B: Calibrar Health Score**
```
1. Comparar con realidad:
   - Revisar churn de clientes por health score
   - Ajustar rangos si necesario
   - Agregar factores adicionales

2. Probar con datos históricos:
   - Aplicar health score a clientes que cancelaron
   - Ver si health score predijo churn
   - Ajustar si no predijo correctamente
```

---

## 🔍 DIAGNÓSTICO RÁPIDO

### Checklist de Diagnóstico

**Si algo no funciona, revisar:**

**Configuración:**
- [ ] ¿Está configurado correctamente?
- [ ] ¿Tiene permisos necesarios?
- [ ] ¿Está activado?

**Integraciones:**
- [ ] ¿Las integraciones están conectadas?
- [ ] ¿Los webhooks funcionan?
- [ ] ¿Las APIs tienen límites alcanzados?

**Datos:**
- [ ] ¿Los datos son correctos?
- [ ] ¿Los formatos son correctos?
- [ ] ¿Hay datos suficientes?

**Timing:**
- [ ] ¿El timing es correcto?
- [ ] ¿Hay delays necesarios?
- [ ] ¿Se ejecuta en momento correcto?

---

## 🛠️ HERRAMIENTAS DE DIAGNÓSTICO

### Herramienta 1: Test de Lead Scoring

```
1. Crear lead de prueba con:
   - Score conocido (calcular manualmente)
   - Atributos específicos
   - Comportamiento específico

2. Verificar que:
   - Score se calcula correctamente
   - Routing funciona
   - Workflows se activan

3. Si no funciona:
   - Revisar cada criterio individualmente
   - Verificar que scoring está activo
   - Revisar logs
```

---

### Herramienta 2: Test de Workflow

```
1. Crear workflow de prueba:
   - Trigger simple
   - Acción simple (email de prueba)
   - Sin condiciones complejas

2. Activar manualmente:
   - Verificar que se ejecuta
   - Verificar que acción funciona
   - Revisar logs

3. Si funciona:
   - Agregar condiciones gradualmente
   - Probar cada condición
   - Escalar a workflow completo
```

---

### Herramienta 3: Test de Integración

```
1. Probar cada integración individualmente:
   - Typeform → Make.com
   - Make.com → HubSpot
   - HubSpot → Email

2. Verificar cada paso:
   - ¿Los datos se envían correctamente?
   - ¿El formato es correcto?
   - ¿Hay errores en los logs?

3. Si hay error:
   - Revisar logs específicos
   - Verificar credenciales
   - Verificar permisos
```

---

## 📊 MÉTRICAS DE HEALTH CHECK

### Health Check Semanal

**Revisar cada semana:**

**Lead Scoring:**
- [ ] ¿Scores se calculan automáticamente?
- [ ] ¿Rangos de score son correctos?
- [ ] ¿Routing funciona?

**Workflows:**
- [ ] ¿Todos los workflows están activos?
- [ ] ¿Se ejecutan correctamente?
- [ ] ¿Hay errores en logs?

**Emails:**
- [ ] ¿Tasa de entrega >95%?
- [ ] ¿Tasa de apertura estable?
- [ ] ¿Tasa de spam <0.1%?

**Conversión:**
- [ ] ¿Conversión está mejorando?
- [ ] ¿Ciclo de ventas se está reduciendo?
- [ ] ¿LTV está aumentando?

---

## 🚨 SEÑALES DE ALERTA TEMPRANA

### Alerta 1: Conversión Cae Después de Cambio

**Qué hacer:**
1. Revertir cambio inmediatamente
2. Analizar qué cambió
3. Identificar causa raíz
4. Hacer cambio más gradual

---

### Alerta 2: Tasa de Bounce Aumenta

**Qué hacer:**
1. Limpiar lista de emails
2. Verificar que emails son válidos
3. Revisar configuración DNS
4. Mejorar proceso de captura de emails

---

### Alerta 3: Churn Rate Aumenta

**Qué hacer:**
1. Revisar health score de clientes que cancelaron
2. Identificar patrones comunes
3. Mejorar onboarding
4. Aumentar check-ins proactivos

---

## 💡 MEJORES PRÁCTICAS DE TROUBLESHOOTING

### Práctica 1: Probar en Entorno de Prueba Primero

**Siempre:**
- Crear leads de prueba
- Probar workflows con datos de prueba
- Verificar que funciona antes de lanzar

---

### Práctica 2: Cambios Graduales

**Nunca:**
- Cambiar todo a la vez
- Lanzar sin probar
- Hacer cambios grandes sin plan

**Siempre:**
- Cambios pequeños
- Probar cada cambio
- Escalar gradualmente

---

### Práctica 3: Documentar Todo

**Documentar:**
- Qué cambios se hicieron
- Cuándo se hicieron
- Qué resultados se esperaban
- Qué resultados reales se obtuvieron

---

## 📞 ESCALACIÓN DE PROBLEMAS

### Nivel 1: Problema Simple
**Ejemplo:** Template de email no se ve bien  
**Acción:** Ajustar template  
**Tiempo:** <1 hora

### Nivel 2: Problema Medio
**Ejemplo:** Workflow no se ejecuta  
**Acción:** Revisar configuración, ajustar  
**Tiempo:** 1-4 horas

### Nivel 3: Problema Complejo
**Ejemplo:** Scoring no funciona correctamente  
**Acción:** Revisar configuración completa, posiblemente reconstruir  
**Tiempo:** 4-8 horas

### Nivel 4: Problema Crítico
**Ejemplo:** Sistema completo no funciona  
**Acción:** Revertir cambios, contactar soporte  
**Tiempo:** Inmediato

---

**Fin del Troubleshooting**

*Usar este documento cuando encuentres problemas durante la implementación.*

