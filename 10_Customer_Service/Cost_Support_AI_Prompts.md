# 🤖 Cost Support AI Prompts
## Prompts para ChatGPT/Claude/Gemini - Generación de Respuestas

---

## 🎯 PROMPTS POR TIPO DE TAREA

### **Prompt 1: Generar Análisis de ROI Específico**

```
Necesito un análisis de ROI profesional para un cliente. 

INFORMACIÓN DEL CLIENTE:
- Industria: [Insert industry]
- Uso actual: [Insert current usage]
- Plan actual: [Insert plan]
- Costo mensual: $[Amount]
- Objetivo: [Insert goal]

OBJETIVO:
Crear un análisis de ROI que muestre:
1. Ahorro mensual proyectado
2. Ingresos adicionales mensuales
3. ROI porcentual
4. Período de payback
5. Proyección anual

ESTILO:
- Profesional pero accesible
- Números específicos
- Visual (usa bullets, tables)
- Orientado a acción

FORMATO:
- Incluir comparativa con situación actual
- Usar ejemplos concretos
- Añadir call-to-action claro

Base el análisis en: Cost_Support_Guide.md y Industry_Specific_Cost_Support.md
```

---

### **Prompt 2: Crear Script de Respuesta a Objeción**

```
Genera un script profesional de respuesta a objeción de precio.

CONTEXTO:
- Cliente dice: "[Insert objection]"
- Industria: [Insert industry]
- Plan evaluando: [Insert plan]
- Presupuesto: $[Amount]/mes (si conocido)

OBJETIVO:
- Convertir objeción en oportunidad
- No ser defensivo
- Mostrar valor claro
- Ofrecer soluciones múltiples

ESTRUCTURA:
1. Empatizar (1-2 sentences)
2. Reframe el problema (1 sentence)
3. Presentar 3 opciones diferentes
4. Risk reversal
5. Call-to-action suave

ESTILO:
- Conversacional pero profesional
- Específico con números
- Orientado a resultados
- Sin presionar

Basado en: Cost_Conversation_Templates.md - Objection Handling
```

---

### **Prompt 3: Email de Retención por Cancelación**

```
Necesito un email profesional para un cliente que quiere cancelar.

CONTEXTO:
- Cliente desde: [Date]
- Razón cancelación: [Reason]
- Plan actual: [Plan]
- Uso actual: [Usage %]
- ROI histórico: [ROI %]

OBJETIVO:
- Retener sin ser agresivo
- Ofrecer múltiples alternativas
- Valorar historial de cliente
- Dejar puerta abierta

ELEMENTOS A INCLUIR:
- Agradecimiento genuino
- Análisis de uso y ROI documentado
- 3 opciones concretas (pausa, downgrade, mejoras)
- Compensación apropiada
- Sin presión

TONO:
- Caluroso pero profesional
- Respeta decisión final
- Enfoque en valor

Basado en: Financial_Resolution_Scenarios.md - Escenario 2.2
```

---

### **Prompt 4: Calculadora de Compensación Apropiada**

```
Calcula el nivel de compensación apropiado para un incidente.

INCIDENTE:
- Tipo: [Billing error, Technical issue, Service problem]
- Monto afectado: $[Amount]
- Severidad: [Low, Medium, High]
- Cliente: [New, Regular, VIP]

FACTORES A CONSIDERAR:
- Severidad del error
- Tipo de cliente
- Impacto en el cliente
- Historial de problemas
- Valor del cliente (LTV)

CALCULAR:
- Crédito apropiado: $X
- Extensión de servicio: X meses
- Servicios adicionales: [List]
- Nivel de follow-up: [Standard, Priority, VIP]

ESCALAS:
- Nivel 1 (Menor): $0-50
- Nivel 2 (Moderado): $50-200
- Nivel 3 (Severo): $200-1000

Base en: Cost_Support_Guide.md - Scales of Compensation
```

---

### **Prompt 5: Optimizar Respuesta Existente**

```
Optimiza esta respuesta de cost support para mejor conversión y satisfacción.

RESPUESTA ACTUAL:
[Paste current response]

CONTEXTO:
- Tipo de consulta: [Type]
- Cliente: [Description]
- Objetivo: [Goal]
- Métrica objetivo: [CSAT, Retention, Upsell]

OBJETIVO:
- Mejorar empatía y tono
- Añadir value adicional
- Incrementar clarity
- Añadir call-to-action
- Mejorar readability

CHECKLIST:
- [ ] Empathy en primer párrafo
- [ ] Solución clara y específica
- [ ] Timeline específico
- [ ] Múltiples opciones
- [ ] Next steps claros
- [ ] Valor adicional ofrecido

Basado en: customer_support_training_guide.md - RESPOND Framework
```

---

## 🎯 PROMPTS ESPECIALIZADOS POR INDUSTRIA

### **Prompt: Enterprise TCO Analysis**

```
Crea un análisis TCO completo para cliente enterprise.

DETALLES:
- Vendor actual: [Name]
- Costo vendor: $XXX/año
- Nuestra propuesta: $XXX/año
- Industria: [Industry]
- Tamaño: [Company size]

INCLUIR:
1. TCO 3 años (comparativo)
2. Migration costs
3. Support costs
4. Custom development
5. Training costs
6. ROI calculation
7. Risk analysis
8. Pilot program proposal

ENFOQUE:
- TCO > precio inicial
- Compliance y security
- Innovation cycles
- Dedicated support

Basado en: Industry_Specific_Cost_Support.md - Enterprise
```

---

### **Prompt: Startup Flexible Pricing**

```
Crea una propuesta de pricing flexible para startup.

DETALLES:
- Startup stage: [MVP, Traction, Scaling]
- Budget limitado
- Runway: X meses
- Fundraising: [Status]

OPCIONES A OFRECER:
1. Program escalado (0% → Discount → Full)
2. Pay-as-you-grow
3. Equity exchange (opcional)
4. Value exchange (case study, mentorship)

BENEFITS A INCLUIR:
- Setup gratis
- Mentorías
- Feature priority
- Community access

ENFOQUE:
- Flexibility
- Low risk para startup
- High value exchange
- Growth-focused

Basado en: Industry_Specific_Cost_Support.md - Tech Startups
```

---

## 📋 PROMPTS PARA ANÁLISIS

### **Prompt: Analizar Caso Completo**

```
Analiza este caso de cost support y genera recomendación completa.

CASO:
[Paste full case details]

ANÁLISIS REQUERIDO:
1. Tipo de caso
2. Severidad (1-10)
3. Cliente value (Low, Medium, High)
4. Authorizations necesarios
5. Opciones de resolución (mínimo 3)
6. ROI de cada opción
7. Risk de cada opción
8. Recomendación final
9. Scripts a usar
10. Timeline sugerido

SALIDA:
- Análisis estructurado
- Tabla comparativa de opciones
- Script recomendado
- Checklist de actions

Referencias: Todos los documentos relevantes
```

---

### **Prompt: Extraer Patrones de Casos**

```
Analiza estos 10 casos de cost support y identifica patrones.

CASOS:
[Casos numerados 1-10]

IDENTIFICAR:
1. Tipos de problemas más comunes
2. Objeciones recurrentes
3. Soluciones más efectivas
4. Métricas de éxito por tipo
5. Tiempo promedio de resolución
6. Nivel de compensación típico
7. Factores de retención
8. Factores de upsell

SALIDA:
- Patrones identificados
- Estrategias recomendadas
- Mejoras sugeridas
- Best practices emergentes

UTILIZAR PARA:
- Actualizar scripts
- Mejorar training
- Optimizar procesos
```

---

## 🎨 PROMPTS CREATIVOS

### **Prompt: Personalizar Template**

```
Personaliza este template de email para este cliente específico.

TEMPLATE:
[Paste template]

CLIENTE:
- Nombre: [Name]
- Industria: [Industry]
- Plan: [Plan]
- Use case: [Description]
- Personal info: [Any relevant details]

PERSONALIZAR:
- Añadir detalles específicos del cliente
- Referenciar historial si relevante
- Usar datos reales del caso
- Mantener profesionalismo
- Añadir toque personal genuino

CHECKLIST:
- [ ] Nombre personalizado
- [ ] Detalles específicos añadidos
- [ ] Historial referenciado si aplicable
- [ ] Números exactos del caso
- [ ] Tono apropiado mantenido

Basado en: Cost_Support_Email_Templates.md
```

---

### **Prompt: Crear Follow-up Sequence**

```
Crea una secuencia de follow-ups de 3-5 emails para este caso.

CONTEXTO:
- Caso tipo: [Type]
- Cliente: [Description]
- Objetivo: [Goal]

ESTRUCTURA:
- Email 1: Inmediato (confirmación)
- Email 2: 24 horas (verificación)
- Email 3: 7 días (check-in)
- Email 4: 30 días (valor adicional) [Opcional]
- Email 5: 90 días (retention) [Opcional]

CADA EMAIL:
- Subject line claro
- Body apropiado
- Tone apropiado
- Timing específico
- Call-to-action

OBJETIVO:
- Mantener satisfacción
- Recuperar valor
- Prevenir churn
- Generar upsell

Basado en: Cost_Support_Guide.md - Follow-up Templates
```

---

## 🔧 PROMPTS DE HERRAMIENTAS

### **Prompt: Usar Calculator Efficiently**

```
Necesito que utilices esta calculadora de ROI y me ayudes a presentar resultados.

DATOS:
- Investment: $[Amount]/mes
- Savings: $[Amount]/mes
- Revenue: $[Amount]/mes
- Time saved: XX horas/semana
- Hourly rate: $XX

CALCULAR:
1. ROI porcentual
2. Payback period
3. Net monthly gain
4. Annual projection
5. Break-even point

PRESENTACIÓN:
Formatea los resultados de manera convincente para incluirlos en email al cliente.

FORMATO:
- Bullets claros
- Números destacados
- Comparativas visuales
- Call-to-action

Para usar con: Cost_Support_Calculator.html
```

---

## ✅ PROMPTS DE QA

### **Prompt: Revisar Respuesta Antes de Enviar**

```
Revisa esta respuesta de cost support antes de enviar al cliente.

RESPUESTA:
[Paste response]

REVISAR:
1. ✅ Empatía presente?
2. ✅ Solución clara?
3. ✅ Timeline específico?
4. ✅ Múltiples opciones?
5. ✅ Next steps definidos?
6. ✅ Value adicional?
7. ✅ Tone apropiado?
8. ✅ Sin errores?
9. ✅ Datos correctos?
10. ✅ Call-to-action claro?

MEJORAS SUGERIDAS:
- Lista de issues
- Mejoras concretas
- Version mejorada

Basado en: customer_support_training_guide.md - Quality Checklist
```

---

## 🎯 GUÍA DE USO DE PROMPTS

### **Cuándo Usar Cada Prompt:**

| Situación | Prompt a Usar | Cuándo |
|-----------|---------------|--------|
| Necesito calcular ROI | Prompt 1 | Antes de conversación de precio |
| Cliente dice "caro" | Prompt 2 | Objeción en tiempo real |
| Cliente quiere cancelar | Prompt 3 | Solicitud de cancelación |
| Necesito compensar | Prompt 4 | Después de error |
| Optimizar mi respuesta | Prompt 5 | Revisión antes de enviar |
| Cliente enterprise | Enterprise Prompt | Análisis TCO |
| Cliente startup | Startup Prompt | Pricing flexible |
| Analizar caso completo | Análisis Prompt | Casos complejos |
| Personalizar email | Personalizar Prompt | Antes de enviar |

### **Mejores Prácticas:**
1. Siempre incluir contexto específico
2. Referenciar documentos base
3. Solicitar múltiples opciones
4. Pedir versiones mejoradas
5. Iterar hasta satisfacción

---

## 🚀 WORKFLOW RECOMENDADO

### **Día 1: Setup**
1. Guardar estos prompts en tu AI tool favorito
2. Organizar por categoría
3. Crear template personal con campos

### **Día 2-7: Aprender**
1. Usar cada prompt una vez
2. Comparar outputs
3. Refinar prompts personalizados
4. Build library personal

### **Ongoing: Optimizar**
1. Iterar prompts con feedback
2. Añadir ejemplos de éxito
3. Compartir con team
4. Evolucionar continuamente

---

**Última Actualización:** Enero 2025  
**Compatible con:** ChatGPT, Claude, Gemini  
**Para usar con:** Todos los documentos de Cost Support


