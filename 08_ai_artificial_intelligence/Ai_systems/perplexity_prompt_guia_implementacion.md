# Guía de Implementación: Prompt de Perplexity

> **💡 Guía Completa**: Cómo implementar, personalizar y optimizar el prompt de Perplexity para diferentes casos de uso.

---

## 📋 Índice de Documentos Disponibles

### **Versiones del Prompt:**
1. `perplexity_prompt_compact.md` - Versión compacta base
2. `perplexity_prompt_improved.md` - Versión documentada
3. `perplexity_prompt_ultimate.md` - Versión con mejoras avanzadas
4. `perplexity_prompt_deep_expert.md` - Versión con técnicas avanzadas
5. `perplexity_prompt_optimized_v2.md` - Versión optimizada v2
6. `perplexity_prompt_final_optimized.md` - Versión final optimizada
7. `perplexity_prompt_ultimate_v3.md` - Versión ultimate v3 (con Quick Reference)

### **Documentación:**
- `perplexity_prompt_improvements.md` - Mejoras realizadas
- `perplexity_prompt_advanced_improvements.md` - Mejoras avanzadas detalladas
- `perplexity_prompt_deep_improvements.md` - Mejoras profundas
- `perplexity_prompt_v2_improvements.md` - Mejoras v2
- `perplexity_prompt_final_comparison.md` - Comparación de versiones
- `perplexity_prompt_guia_implementacion.md` - Esta guía

---

## 🚀 Guía de Implementación Rápida

### **Paso 1: Seleccionar Versión**

**Para Producción Estándar:**
→ Usa `perplexity_prompt_final_optimized.md` o `perplexity_prompt_ultimate_v3.md`

**Para Máxima Calidad:**
→ Usa `perplexity_prompt_deep_expert.md`

**Para Implementación Rápida:**
→ Usa `perplexity_prompt_compact.md`

---

### **Paso 2: Personalización Básica**

**Reemplazar Placeholders:**
- `[Fecha]` → Fecha actual
- `[Nombre de la Consultora]` → Tu nombre/empresa
- Cualquier otro placeholder específico

**Ajustar según Necesidad:**
- Agregar instrucciones específicas de dominio
- Modificar restricciones si es necesario
- Ajustar query types según tu caso de uso

---

### **Paso 3: Testing**

**Casos de Prueba:**
1. Query simple (hecho básico)
2. Query compleja (análisis multi-parte)
3. Query académica
4. Query de noticias
5. Query técnica (código)
6. Query ambigua

**Métricas a Evaluar:**
- Precisión de respuestas
- Calidad de formato
- Uso correcto de citas
- Manejo de incertidumbre
- Consistencia

---

### **Paso 4: Optimización**

**Ajustes Comunes:**
- Agregar instrucciones específicas de industria
- Modificar restricciones según políticas
- Ajustar query types para casos específicos
- Personalizar format rules si necesario

---

## 📊 Comparación de Versiones

| Versión | Tokens | Complejidad | Mejor Para |
|---------|--------|-------------|------------|
| **Compact** | ~2,500 | Baja | Implementación rápida |
| **Improved** | ~4,000 | Media | Referencia y aprendizaje |
| **Ultimate** | ~6,000 | Alta | Producción estándar |
| **Deep Expert** | ~8,000 | Muy Alta | Máxima calidad |
| **Optimized v2** | ~6,500 | Alta | Balance calidad/eficiencia |
| **Final Optimized** | ~6,000 | Alta | Producción recomendada |
| **Ultimate v3** | ~6,200 | Alta | Producción con Quick Reference |

---

## 🎯 Casos de Uso Específicos

### **Caso 1: Asistente de Búsqueda General**

**Recomendación:** `perplexity_prompt_final_optimized.md`

**Personalización:**
- Mantener todos los query types
- Ajustar source evaluation según dominio
- Configurar conversation management

---

### **Caso 2: Asistente Académico**

**Recomendación:** `perplexity_prompt_deep_expert.md`

**Personalización:**
- Enfatizar Academic Research query type
- Priorizar fuentes académicas
- Ajustar format rules para papers

**Modificaciones:**
- Agregar instrucciones para formato académico específico
- Priorizar peer-reviewed sources
- Incluir requirements de citación académica

---

### **Caso 3: Asistente de Noticias**

**Recomendación:** `perplexity_prompt_ultimate_v3.md`

**Personalización:**
- Enfatizar Recent News query type
- Configurar source evaluation para medios
- Ajustar para múltiples perspectivas

**Modificaciones:**
- Priorizar fuentes de noticias confiables
- Configurar agrupación por temas
- Ajustar timestamp handling

---

### **Caso 4: Asistente Técnico**

**Recomendación:** `perplexity_prompt_final_optimized.md`

**Personalización:**
- Enfatizar Coding query type
- Ajustar format rules para código
- Configurar para documentación técnica

**Modificaciones:**
- Mejorar code snippet handling
- Agregar instrucciones para documentación técnica
- Priorizar fuentes técnicas (GitHub, Stack Overflow, etc.)

---

## 🔧 Personalización Avanzada

### **Agregar Query Types Personalizados**

**Ejemplo: Legal Research:**
```
**Legal Research:**
Provide comprehensive legal analysis with:
- Relevant statutes and regulations
- Case law precedents
- Jurisdictional considerations
- Legal citations in proper format
- Distinction between binding and persuasive authority
```

**Ejemplo: Medical Information:**
```
**Medical Information:**
Provide evidence-based medical information:
- Prioritize peer-reviewed medical journals
- Include disclaimers about not replacing medical advice
- Cite medical guidelines when available
- Distinguish between established facts and emerging research
```

---

### **Modificar Source Evaluation**

**Para Dominio Específico:**
- Agregar fuentes autoritativas del dominio
- Ajustar jerarquía de fuentes
- Configurar criterios de recencia específicos

**Ejemplo para FinTech:**
- Regulatory sources (SEC, FINRA, etc.) > Academic > News
- Priorizar fuentes con compliance verification
- Considerar jurisdicción regulatoria

---

### **Ajustar Format Rules**

**Para Documentación Técnica:**
- Permitir listas anidadas si necesario
- Ajustar estructura de headers
- Configurar code blocks más prominentes

**Para Contenido Académico:**
- Estructura más formal
- Requisitos de citación más estrictos
- Formato de referencias específico

---

## 📈 Métricas de Éxito

### **Métricas de Calidad:**
- Precisión de respuestas: >95%
- Uso correcto de citas: 100%
- Formato consistente: >98%
- Manejo de incertidumbre: Apropiado en 100% de casos

### **Métricas de Usabilidad:**
- Satisfacción del usuario: >4.5/5
- Tasa de correcciones: <5%
- Claridad percibida: >90%
- Utilidad de respuestas: >85%

---

## 🛠️ Herramientas de Testing

### **Checklist de Validación:**

**Formato:**
- [ ] Respuestas empiezan con resumen (no header)
- [ ] Headers Level 2 (##) usados correctamente
- [ ] Listas planas (no anidadas)
- [ ] Tablas para comparaciones
- [ ] Citas formateadas correctamente [12]
- [ ] Sin espacios antes de citas
- [ ] Termina con resumen (no pregunta)

**Contenido:**
- [ ] Hechos verificados
- [ ] Consistencia lógica
- [ ] Todas las partes de query abordadas
- [ ] Incertidumbre reconocida cuando aplica
- [ ] Múltiples perspectivas en temas controvertidos
- [ ] Sin contenido con copyright verbatim
- [ ] Sin emojis o lenguaje de hedging

**Query Types:**
- [ ] Academic: Formato científico, detallado
- [ ] News: Conciso, agrupado por temas
- [ ] Weather: Muy corto, solo pronóstico
- [ ] People: Biografía corta, hechos verificables
- [ ] Coding: Código primero, luego explicación
- [ ] Translation: Solo traducción, sin citas
- [ ] Creative: Sigue instrucciones del usuario
- [ ] Math: Resultado final para simple, método para complejo
- [ ] URL: Solo primer resultado, cita [1]

---

## 💡 Mejores Prácticas

### **1. Testing Iterativo:**
- Probar con queries reales
- Iterar basado en resultados
- Ajustar según feedback

### **2. Monitoreo Continuo:**
- Revisar respuestas regularmente
- Identificar patrones de error
- Ajustar prompt según necesidad

### **3. Documentación:**
- Documentar cambios realizados
- Mantener versiones anteriores
- Crear changelog

### **4. Personalización Gradual:**
- Empezar con versión base
- Agregar personalizaciones incrementales
- Probar cada cambio

---

## 🚨 Troubleshooting Común

### **Problema: Respuestas muy largas**
**Solución:** Ajustar Content Density en format_rules, enfatizar concisión

### **Problema: Citas incorrectas**
**Solución:** Revisar sección de Citations en format_rules, agregar ejemplos

### **Problema: Formato inconsistente**
**Solución:** Reforzar Format Rules, agregar más ejemplos específicos

### **Problema: No maneja incertidumbre bien**
**Solución:** Reforzar Uncertainty Handling, agregar ejemplos

### **Problema: Sesgo en respuestas**
**Solución:** Reforzar Bias and Neutrality en restrictions

---

## 📚 Recursos Adicionales

### **Documentos de Referencia:**
- Prompt Engineering Guide (OpenAI)
- Anthropic Claude System Prompt Best Practices
- Google PaLM Prompting Techniques
- Perplexity AI Documentation

### **Comunidades:**
- r/promptengineering
- Prompt Engineering Discord
- AI Research Papers (arXiv)

---

*Guía de implementación completa para el prompt de Perplexity. Última actualización: 2025-05-13*



