# Prompt Mejorado para Priorización RICE de MVP

## Instrucciones para Priorización RICE

Ayúdame a priorizar las siguientes características para mi MVP usando el framework RICE (Reach, Impact, Confidence, Effort). Para cada característica, proporciona:

### Métricas RICE:

**REACH (Alcance)**: Número de usuarios/clientes afectados en un período determinado (típicamente por mes o trimestre)
- Escala: Usa números reales cuando sea posible, o estimaciones basadas en:
  - 100% = Todos los usuarios del producto
  - 50% = La mitad de los usuarios
  - 10% = Una porción significativa pero minoritaria
  - 1% = Una pequeña porción de usuarios

**IMPACT (Impacto)**: Qué tan significativo es el cambio para cada usuario afectado
- Escala: 0.25 (mínimo), 0.5 (bajo), 1 (medio), 2 (alto), 3 (máximo)
- Considera: ¿Resuelve un problema crítico? ¿Mejora significativamente la experiencia? ¿Genera valor medible?

**CONFIDENCE (Confianza)**: Nivel de certeza sobre las estimaciones de Reach e Impact
- Escala: 50% (baja confianza), 80% (media), 100% (alta confianza)
- Considera: ¿Tienes datos? ¿Es una suposición educada? ¿Hay investigación de usuarios?

**EFFORT (Esfuerzo)**: Tiempo requerido del equipo (en persona-mes o persona-semanas)
- Escala: Usa números reales o estimaciones relativas
- Considera: Desarrollo, diseño, testing, documentación, deployment

### Fórmula RICE Score:
```
RICE Score = (Reach × Impact × Confidence) / Effort
```

### Formato de Respuesta Requerido:

Para cada característica, proporciona:

1. **Característica**: [Nombre de la característica]
2. **Reach**: [Número o porcentaje] - [Justificación breve]
3. **Impact**: [0.25-3] - [Justificación breve]
4. **Confidence**: [50-100%] - [Justificación breve]
5. **Effort**: [Persona-mes/semanas] - [Justificación breve]
6. **RICE Score**: [Cálculo numérico]
7. **Ranking**: [Posición en la lista priorizada]
8. **Análisis Detallado**: 
   - ¿Por qué esta característica es importante?
   - ¿Qué problemas resuelve?
   - ¿Cuáles son los riesgos de no implementarla?
   - ¿Qué dependencias tiene?
   - ¿Cuál es el impacto en el negocio?

### Lista de Características a Priorizar:

[Inserte aquí su lista de características propuestas]

---

### Ejemplo de Formato:

**Característica**: Autenticación de usuarios con SSO

- **Reach**: 100% (todos los usuarios necesitan autenticarse)
- **Impact**: 2 (alto - mejora significativamente la seguridad y experiencia)
- **Confidence**: 80% (basado en estándares de la industria)
- **Effort**: 2 persona-mes
- **RICE Score**: (100 × 2 × 0.8) / 2 = 80
- **Ranking**: #1
- **Análisis Detallado**: 
  - Esta característica es fundamental porque sin autenticación segura, el producto no puede lanzarse
  - Resuelve el problema crítico de seguridad y cumplimiento
  - El riesgo de no implementarla es alto: no hay producto viable sin esto
  - Dependencias: Integración con proveedor de identidad
  - Impacto en el negocio: Habilitador crítico para el MVP

---

### Consideraciones Adicionales:

- **Factores de Negocio**: Considera el impacto en ingresos, retención, adquisición
- **Dependencias Técnicas**: Identifica qué características deben ir primero
- **Riesgos**: Evalúa qué pasa si no se implementa cada característica
- **Validación**: ¿Se puede validar con usuarios antes del desarrollo completo?
- **Escalabilidad**: ¿La solución escala con el crecimiento del producto?

### Output Final:

Al final, proporciona:
1. Lista priorizada completa (ordenada por RICE Score descendente)
2. Visualización sugerida (tabla o gráfico)
3. Recomendaciones estratégicas:
   - ¿Qué características son "must-have" para el MVP?
   - ¿Cuáles pueden esperar a la versión 2.0?
   - ¿Hay características que deberían agruparse?
   - ¿Cuál es el roadmap sugerido por trimestre?

---

**Nota**: Si no tienes datos exactos, usa estimaciones conservadoras y documenta tus suposiciones. Es mejor ser conservador que optimista en las estimaciones de RICE.

---

## Guía Detallada de Escalas RICE

### REACH - Guía de Estimación

**Para productos nuevos (sin usuarios aún):**
- Usa proyecciones basadas en:
  - Tamaño del mercado objetivo
  - Tasa de conversión esperada
  - Crecimiento proyectado en los primeros 3-6 meses

**Para productos existentes:**
- Usa datos históricos:
  - Analytics de uso actual
  - Segmentación de usuarios
  - Patrones de comportamiento

**Ejemplos de Reach:**
- **1000 usuarios/mes**: Si tienes 10,000 usuarios activos y el 10% usará la feature
- **50%**: Si la mitad de tus usuarios se beneficiarán
- **Todos los nuevos usuarios**: Si es una feature de onboarding

### IMPACT - Guía de Evaluación

**3.0 (Impacto Máximo)**: 
- Característica crítica sin la cual el producto no funciona
- Resuelve un problema que bloquea completamente a los usuarios
- Genera ingresos directos o previene pérdidas significativas
- Ejemplo: Sistema de pagos para un e-commerce

**2.0 (Alto Impacto)**:
- Mejora significativa en la experiencia del usuario
- Resuelve un problema importante que causa frustración
- Aumenta la retención o conversión de manera medible
- Ejemplo: Búsqueda mejorada, notificaciones en tiempo real

**1.0 (Impacto Medio)**:
- Mejora incremental pero notable
- Resuelve un problema menor pero frecuente
- Mejora la satisfacción del usuario
- Ejemplo: Mejoras en UI, shortcuts de teclado

**0.5 (Bajo Impacto)**:
- Mejora menor pero útil
- Nice-to-have que algunos usuarios apreciarán
- Ejemplo: Temas personalizados, exportación de datos

**0.25 (Impacto Mínimo)**:
- Mejora muy pequeña o cosmética
- Solo afecta a un pequeño subconjunto de usuarios
- Ejemplo: Cambios menores en tipografía, ajustes de color

### CONFIDENCE - Guía de Evaluación

**100% (Alta Confianza)**:
- Tienes datos históricos sólidos
- Has realizado pruebas A/B o investigación de usuarios
- La feature es similar a algo que ya has implementado antes
- Ejemplo: "Basado en datos de 6 meses de analytics"

**80% (Confianza Media-Alta)**:
- Tienes datos parciales o investigación cualitativa
- Es una suposición educada basada en experiencia
- Has visto patrones similares en otros productos
- Ejemplo: "Basado en entrevistas con 10 usuarios y benchmarks de la industria"

**50% (Baja Confianza)**:
- Es principalmente una suposición
- No tienes datos para respaldarlo
- Es una hipótesis que necesita validación
- Ejemplo: "Suposición basada en feedback anecdótico"

**Nota sobre Confidence**: Si tu confianza es menor al 50%, considera hacer investigación primero antes de priorizar.

### EFFORT - Guía de Estimación

**Considera todos estos componentes:**
- **Desarrollo**: Programación, arquitectura, integraciones
- **Diseño**: UI/UX, prototipos, iteraciones
- **Testing**: QA, pruebas automatizadas, pruebas de usuario
- **Documentación**: Guías de usuario, documentación técnica, onboarding
- **Deployment**: Configuración, migraciones, monitoreo
- **Comunicación**: Anuncios, emails, training del equipo de soporte

**Escalas comunes:**
- **0.5 persona-mes**: Feature pequeña, cambios menores
- **1 persona-mes**: Feature mediana, trabajo estándar
- **2-3 persona-mes**: Feature grande, requiere múltiples componentes
- **4+ persona-mes**: Feature muy grande, posiblemente dividir en fases

**Tip**: Si el esfuerzo es muy alto (>4 meses), considera dividir la feature en fases más pequeñas.

---

## Ejemplos Adicionales de Priorización

### Ejemplo 1: E-commerce MVP

**Característica**: Carrito de compras persistente

- **Reach**: 80% (la mayoría de usuarios agregan productos al carrito)
- **Impact**: 2.5 (alto - reduce abandono de carrito significativamente)
- **Confidence**: 90% (datos de la industria muestran 20-30% de mejora en conversión)
- **Effort**: 1.5 persona-mes
- **RICE Score**: (80 × 2.5 × 0.9) / 1.5 = 120
- **Análisis**: Feature crítica para conversión. Los datos muestran que usuarios que pueden retomar su carrito tienen 3x más probabilidad de completar la compra.

---

**Característica**: Recomendaciones de productos basadas en IA

- **Reach**: 60% (usuarios que navegan múltiples páginas)
- **Impact**: 1.5 (medio-alto - puede aumentar ventas cruzadas)
- **Confidence**: 50% (hipótesis no probada, requiere validación)
- **Effort**: 4 persona-mes (incluye modelo ML, integración, testing)
- **RICE Score**: (60 × 1.5 × 0.5) / 4 = 11.25
- **Análisis**: Feature interesante pero de alto esfuerzo y baja confianza. Mejor para post-MVP después de validar con datos.

---

### Ejemplo 2: SaaS B2B

**Característica**: Exportación de reportes a PDF/Excel

- **Reach**: 40% (usuarios que necesitan compartir datos)
- **Impact**: 2.0 (alto - feature frecuentemente solicitada)
- **Confidence**: 85% (múltiples solicitudes de clientes)
- **Effort**: 2 persona-mes
- **RICE Score**: (40 × 2.0 × 0.85) / 2 = 34
- **Análisis**: Feature de alto valor percibido por usuarios. Relativamente fácil de implementar con librerías existentes.

---

**Característica**: Integración con Slack

- **Reach**: 25% (equipos que usan Slack)
- **Impact**: 1.0 (medio - mejora workflow pero no crítico)
- **Confidence**: 70% (algunos clientes lo han solicitado)
- **Effort**: 1.5 persona-mes
- **RICE Score**: (25 × 1.0 × 0.7) / 1.5 = 11.67
- **Análisis**: Nice-to-have pero no esencial para MVP. Puede esperar a v2.0.

---

## Matriz de Decisión Rápida

Usa esta matriz para decisiones rápidas:

| RICE Score | Prioridad | Acción Recomendada |
|------------|-----------|-------------------|
| > 100 | Crítica | Implementar inmediatamente |
| 50-100 | Alta | Incluir en MVP si es posible |
| 20-50 | Media | Considerar para MVP o v1.1 |
| 10-20 | Baja | Post-MVP, validar primero |
| < 10 | Muy Baja | Reconsiderar o descartar |

---

## Factores de Ajuste y Consideraciones Especiales

### Ajustes por Contexto de Negocio

**Multiplica el RICE Score por estos factores si aplican:**

- **×1.5** si la feature es un requisito legal o de cumplimiento
- **×1.3** si la feature es crítica para un cliente grande existente
- **×1.2** si la feature reduce riesgo técnico significativo
- **×0.8** si la feature tiene dependencias externas inciertas
- **×0.7** si la feature requiere mantenimiento continuo alto

### Dependencias y Bloqueadores

**Identifica:**
- **Bloequeadores**: Features que otras dependen de ellas (priorizar primero)
- **Dependientes**: Features que requieren otras primero (priorizar después)
- **Independientes**: Features que pueden desarrollarse en paralelo

### Validación Pre-Desarrollo

**Antes de desarrollar, considera:**
- ¿Puedes hacer un MVP de la feature (prototipo, landing page, demo)?
- ¿Puedes validar con usuarios antes del desarrollo completo?
- ¿Hay alternativas más simples que resuelvan el 80% del problema?

---

## Template de Análisis por Característica

```
## [Nombre de la Característica]

### Métricas RICE
- **Reach**: [valor] - [justificación]
- **Impact**: [valor] - [justificación]
- **Confidence**: [valor]% - [justificación]
- **Effort**: [valor] - [justificación]
- **RICE Score**: [cálculo] = [resultado]

### Análisis Profundo

**Problema que Resuelve:**
[Describe el problema específico]

**Usuario Objetivo:**
[¿Quién se beneficia? ¿Cuántos son?]

**Valor de Negocio:**
- Impacto en ingresos: [estimación]
- Impacto en retención: [estimación]
- Impacto en adquisición: [estimación]

**Riesgos de No Implementar:**
- [Riesgo 1]
- [Riesgo 2]

**Dependencias:**
- Requiere: [lista de features/bloqueadores]
- Requerida por: [lista de features dependientes]

**Alternativas Consideradas:**
- [Alternativa 1] - [por qué se descartó]
- [Alternativa 2] - [por qué se descartó]

**Plan de Validación:**
- [Cómo validar antes del desarrollo completo]

**Métricas de Éxito:**
- [Métrica 1]: [objetivo]
- [Métrica 2]: [objetivo]

**Notas Adicionales:**
[Consideraciones especiales, suposiciones, etc.]
```

---

## Roadmap Sugerido por Fases

### Fase 1: MVP Core (Sprint 1-2)
- Features con RICE Score > 80
- Bloqueadores críticos
- Features independientes de alto valor

### Fase 2: MVP Completo (Sprint 3-4)
- Features con RICE Score 40-80
- Features dependientes de Fase 1
- Mejoras incrementales de alto impacto

### Fase 3: Post-MVP (Sprint 5+)
- Features con RICE Score 20-40
- Features que requieren validación
- Nice-to-haves de bajo esfuerzo

### Fase 4: Futuro (Backlog)
- Features con RICE Score < 20
- Features que requieren más investigación
- Ideas experimentales

---

## Checklist de Validación Final

Antes de finalizar la priorización, verifica:

- [ ] ¿Todas las features tienen estimaciones RICE completas?
- [ ] ¿Se han identificado todas las dependencias?
- [ ] ¿Hay features que deberían combinarse o dividirse?
- [ ] ¿Las estimaciones de esfuerzo son realistas?
- [ ] ¿Se han considerado factores de negocio críticos?
- [ ] ¿Hay features que requieren validación antes del desarrollo?
- [ ] ¿El roadmap es ejecutable con los recursos disponibles?
- [ ] ¿Se han documentado todas las suposiciones?

---

## Herramientas y Recursos Adicionales

### Plantilla de Cálculo (Excel/Google Sheets)
```
| Feature | Reach | Impact | Confidence | Effort | RICE Score | Ranking |
|---------|-------|--------|-----------|--------|------------|---------|
| Feature 1 | 100 | 2 | 0.8 | 2 | =(B2*C2*D2)/E2 | |
```

### Visualizaciones Recomendadas
1. **Gráfico de barras**: RICE Score por feature
2. **Matriz 2x2**: Impact vs Effort
3. **Roadmap de Gantt**: Timeline de implementación
4. **Gráfico de burbujas**: Reach (X), Impact (Y), Effort (tamaño)

---

## Preguntas de Reflexión Final

1. **¿Qué features son absolutamente críticas para que el MVP sea viable?**
2. **¿Hay features que pueden simplificarse para reducir esfuerzo sin perder impacto?**
3. **¿Qué features tienen el mayor riesgo si se estiman mal?**
4. **¿Hay oportunidades de validar features antes del desarrollo completo?**
5. **¿Cómo afecta esta priorización a los objetivos de negocio a corto y largo plazo?**

---

**Recordatorio Final**: RICE es una herramienta de guía, no una verdad absoluta. Usa tu juicio y contexto de negocio para tomar decisiones finales. Las estimaciones mejoran con el tiempo y la experiencia.

---

## Casos de Uso por Industria

### E-commerce / Retail

**Consideraciones Especiales:**
- **Reach**: Enfócate en % de usuarios que completan compras vs. solo navegan
- **Impact**: Prioriza features que afectan directamente la conversión y el AOV (Average Order Value)
- **Confidence**: Usa datos de analytics de e-commerce (tasa de abandono de carrito, tiempo en sitio)
- **Effort**: Considera integraciones con sistemas de pago, inventario, envío

**Ejemplos de Features Típicas:**
- Carrito persistente: Alto Reach (80%), Alto Impact (2.5), Alta Confidence (90%)
- Búsqueda avanzada: Medio Reach (60%), Alto Impact (2.0), Media Confidence (75%)
- Wishlist: Bajo Reach (30%), Medio Impact (1.0), Alta Confidence (85%)

---

### SaaS B2B

**Consideraciones Especiales:**
- **Reach**: Considera tanto usuarios individuales como organizaciones (seat-based pricing)
- **Impact**: Evalúa impacto en retención de cuentas enterprise vs. SMB
- **Confidence**: Usa datos de NPS, churn rate, feature requests de clientes
- **Effort**: Incluye tiempo de onboarding de clientes, documentación, soporte

**Ejemplos de Features Típicas:**
- SSO/SAML: Alto Reach (100% enterprise), Alto Impact (2.5), Alta Confidence (95%)
- API pública: Medio Reach (40% desarrolladores), Alto Impact (2.0), Media Confidence (70%)
- Dashboard personalizado: Alto Reach (80%), Medio Impact (1.5), Alta Confidence (80%)

---

### Mobile Apps

**Consideraciones Especiales:**
- **Reach**: Considera usuarios activos diarios (DAU) vs. mensuales (MAU)
- **Impact**: Evalúa impacto en retención D1, D7, D30
- **Confidence**: Usa datos de analytics móviles (Firebase, Mixpanel, Amplitude)
- **Effort**: Incluye tiempo de review de App Store, testing en múltiples dispositivos

**Ejemplos de Features Típicas:**
- Push notifications: Alto Reach (100%), Alto Impact (2.0), Alta Confidence (90%)
- Modo offline: Medio Reach (50%), Alto Impact (2.5), Media Confidence (75%)
- Compartir en redes sociales: Medio Reach (40%), Bajo Impact (0.5), Alta Confidence (85%)

---

### Marketplace / Plataformas

**Consideraciones Especiales:**
- **Reach**: Considera tanto lado de la oferta como de la demanda
- **Impact**: Evalúa efecto de red (network effects) - más usuarios = más valor
- **Confidence**: Usa métricas de ambos lados del marketplace
- **Effort**: Incluye trabajo de moderación, verificación, trust & safety

**Ejemplos de Features Típicas:**
- Sistema de reviews: Alto Reach (100%), Alto Impact (3.0), Alta Confidence (95%)
- Chat entre usuarios: Medio Reach (60%), Alto Impact (2.0), Media Confidence (80%)
- Sistema de pagos integrado: Alto Reach (100%), Alto Impact (2.5), Alta Confidence (90%)

---

### Fintech

**Consideraciones Especiales:**
- **Reach**: Considera usuarios activos vs. totales (muchos pueden ser inactivos)
- **Impact**: Prioriza features de seguridad y cumplimiento (regulatorio)
- **Confidence**: Usa datos de transacciones, compliance requirements
- **Effort**: Incluye tiempo de auditorías, compliance, seguridad

**Ejemplos de Features Típicas:**
- Autenticación de dos factores: Alto Reach (100%), Alto Impact (3.0), Alta Confidence (100%)
- Exportación de transacciones: Medio Reach (50%), Medio Impact (1.5), Alta Confidence (90%)
- Notificaciones de transacciones: Alto Reach (100%), Alto Impact (2.0), Alta Confidence (95%)

---

## Errores Comunes y Cómo Evitarlos

### Error 1: Sobreestimar Reach

**Síntoma**: Asumir que todos los usuarios usarán una feature nueva
**Solución**: 
- Usa datos históricos de adopción de features similares
- Aplica el "rule of thumb": divide tu estimación inicial por 3-5
- Considera que solo 10-30% de usuarios adoptan features nuevas típicamente

**Ejemplo Incorrecto**: "Todos los usuarios usarán esta feature" → Reach = 100%
**Ejemplo Correcto**: "Basado en adopción de features similares, estimamos 25% de usuarios" → Reach = 25%

---

### Error 2: Subestimar Effort

**Síntoma**: Olvidar incluir tiempo de testing, documentación, deployment
**Solución**:
- Multiplica tu estimación inicial de desarrollo por 1.5-2x
- Incluye explícitamente: diseño, desarrollo, testing, documentación, deployment, comunicación
- Usa estimaciones de tres puntos (optimista, realista, pesimista) y toma el promedio

**Ejemplo Incorrecto**: "Desarrollo: 2 semanas" → Effort = 0.5 persona-mes
**Ejemplo Correcto**: "Desarrollo (2 sem) + Testing (1 sem) + Deploy (0.5 sem) + Docs (0.5 sem)" → Effort = 1 persona-mes

---

### Error 3: Ignorar Dependencias

**Síntoma**: Priorizar features que requieren otras que no están planificadas
**Solución**:
- Crea un mapa de dependencias antes de calcular RICE
- Identifica bloqueadores críticos y priorízalos primero
- Ajusta RICE scores considerando dependencias (reduce Confidence si hay dependencias inciertas)

**Ejemplo**: Feature A requiere Feature B. Si Feature B no está priorizada, Feature A no puede implementarse.

---

### Error 4: Confianza Demasiado Alta sin Datos

**Síntoma**: Confidence = 100% basado solo en intuición
**Solución**:
- Si no tienes datos, Confidence debería ser ≤ 80%
- Si es una hipótesis no probada, Confidence debería ser ≤ 50%
- Documenta tus suposiciones y considera hacer investigación primero

**Ejemplo Incorrecto**: "Estoy seguro que esto funcionará" → Confidence = 100%
**Ejemplo Correcto**: "Es una suposición educada basada en feedback de 3 usuarios" → Confidence = 60%

---

### Error 5: No Considerar Costo de Oportunidad

**Síntoma**: Priorizar features de bajo RICE que consumen recursos limitados
**Solución**:
- Considera el tamaño de tu equipo y recursos disponibles
- Evalúa qué otras features NO podrás hacer si implementas esta
- Usa RICE junto con restricciones de recursos para tomar decisiones

**Ejemplo**: Feature con RICE = 30 pero requiere 6 meses de desarrollo podría bloquear 3 features con RICE = 50 cada una.

---

### Error 6: Ignorar Factores Cualitativos

**Síntoma**: Decidir solo por RICE score sin considerar contexto estratégico
**Solución**:
- Usa RICE como guía, no como única verdad
- Considera factores estratégicos: alineación con visión, requisitos legales, compromisos con clientes
- Ajusta prioridades cuando factores cualitativos sean críticos

---

## Comparación con Otros Frameworks de Priorización

### RICE vs. MoSCoW (Must Have, Should Have, Could Have, Won't Have)

**RICE:**
- ✅ Cuantitativo y basado en datos
- ✅ Considera esfuerzo explícitamente
- ✅ Permite comparación numérica directa
- ❌ Puede ser complejo para equipos pequeños
- ❌ Requiere datos o estimaciones

**MoSCoW:**
- ✅ Simple y fácil de entender
- ✅ Bueno para equipos pequeños o proyectos simples
- ✅ Enfocado en necesidades críticas
- ❌ Subjetivo y puede generar discusiones
- ❌ No considera esfuerzo explícitamente

**Cuándo usar RICE**: Productos con múltiples features, necesidad de justificación cuantitativa, equipos con datos disponibles

**Cuándo usar MoSCoW**: Proyectos pequeños, MVP muy temprano, equipos sin datos históricos

---

### RICE vs. Value vs. Effort Matrix

**RICE:**
- ✅ Más preciso (4 dimensiones vs. 2)
- ✅ Considera confianza y alcance
- ✅ Score numérico permite ranking claro
- ❌ Más tiempo para calcular

**Value vs. Effort:**
- ✅ Visual y fácil de entender
- ✅ Rápido de usar
- ✅ Bueno para brainstorming inicial
- ❌ Subjetivo (qué es "alto valor"?)
- ❌ No considera confianza

**Recomendación**: Usa Value vs. Effort para brainstorming inicial, luego RICE para priorización final.

---

### RICE vs. Kano Model

**RICE:**
- ✅ Enfocado en priorización práctica
- ✅ Considera esfuerzo y recursos
- ✅ Basado en métricas cuantificables

**Kano Model:**
- ✅ Enfocado en satisfacción del usuario
- ✅ Identifica tipos de features (básicas, performance, delicia)
- ✅ Útil para entender expectativas

**Recomendación**: Usa Kano para entender qué tipo de feature es, luego RICE para priorizar cuándo implementarla.

---

## Ejercicios Prácticos

### Ejercicio 1: Calcular RICE para Features de Onboarding

Tienes estas 3 features de onboarding propuestas:

1. **Tutorial interactivo paso a paso**
   - Reach: 100% (todos los nuevos usuarios)
   - Impact: 2.0 (mejora retención D1 significativamente)
   - Confidence: 75% (datos de industria muestran mejoras del 20-30%)
   - Effort: 3 persona-mes

2. **Checklist de configuración inicial**
   - Reach: 100% (todos los nuevos usuarios)
   - Impact: 1.5 (mejora retención moderadamente)
   - Confidence: 85% (hemos visto mejoras en otros productos)
   - Effort: 1 persona-mes

3. **Video de bienvenida**
   - Reach: 60% (no todos ven videos)
   - Impact: 1.0 (mejora percepción pero impacto limitado)
   - Confidence: 60% (suposición educada)
   - Effort: 0.5 persona-mes

**Calcula RICE scores y prioriza.**

**Solución:**
1. Tutorial: (100 × 2.0 × 0.75) / 3 = 50
2. Checklist: (100 × 1.5 × 0.85) / 1 = 127.5
3. Video: (60 × 1.0 × 0.6) / 0.5 = 72

**Priorización**: Checklist (#1) → Video (#2) → Tutorial (#3)

---

### Ejercicio 2: Ajustar por Dependencias

Tienes estas features:

1. **Sistema de autenticación** (RICE: 150)
2. **Perfil de usuario** (RICE: 80) - Requiere autenticación
3. **Dashboard personalizado** (RICE: 120) - Requiere perfil de usuario

**¿Cómo ajustas la priorización?**

**Solución**: Aunque el dashboard tiene mayor RICE, debe ir después porque depende de otras features. Priorización correcta:
1. Autenticación (RICE: 150, bloqueador)
2. Perfil de usuario (RICE: 80, requiere autenticación)
3. Dashboard (RICE: 120, requiere perfil)

---

### Ejercicio 3: Considerar Factores de Negocio

Feature A: RICE Score = 60
Feature B: RICE Score = 55

Feature A es una mejora incremental.
Feature B es un requisito legal que debe cumplirse en 2 meses.

**¿Cuál priorizas?**

**Solución**: Feature B, aunque tenga menor RICE, porque:
- Es un requisito legal (riesgo alto de no cumplir)
- Tiene deadline fijo
- Aplica factor de ajuste ×1.5 para requisitos legales → RICE ajustado = 82.5

---

## Guía de Estimación Detallada por Tipo de Feature

### Features de Backend/Infraestructura

**Consideraciones para Effort:**
- Desarrollo: Tiempo de arquitectura, implementación, optimización
- Testing: Unit tests, integration tests, load testing
- Deployment: Migraciones de datos, rollback plan, monitoreo
- Documentación: Documentación técnica, runbooks

**Ejemplo**: Sistema de caché distribuido
- Desarrollo: 3 semanas
- Testing: 1 semana
- Deployment: 3 días
- Documentación: 2 días
- **Total Effort**: ~1.2 persona-mes

---

### Features de Frontend/UI

**Consideraciones para Effort:**
- Diseño: Wireframes, mockups, iteraciones
- Desarrollo: Implementación, responsive design, accesibilidad
- Testing: Cross-browser, dispositivos, UX testing
- Documentación: Guías de usuario, screenshots

**Ejemplo**: Rediseño de dashboard principal
- Diseño: 1 semana
- Desarrollo: 2 semanas
- Testing: 1 semana
- Documentación: 2 días
- **Total Effort**: ~1 persona-mes

---

### Features de Integración

**Consideraciones para Effort:**
- Investigación: Documentación de API externa, limitaciones
- Desarrollo: Integración, manejo de errores, retry logic
- Testing: Testing con API real, casos edge, manejo de fallos
- Documentación: Guía de integración, troubleshooting

**Ejemplo**: Integración con Stripe
- Investigación: 3 días
- Desarrollo: 1.5 semanas
- Testing: 1 semana
- Documentación: 2 días
- **Total Effort**: ~0.7 persona-mes

---

### Features de Machine Learning / IA

**Consideraciones para Effort:**
- Investigación: Algoritmos, datasets, benchmarks
- Desarrollo: Modelo, entrenamiento, API
- Testing: Validación, A/B testing, métricas
- Infraestructura: Servidores, GPU, escalabilidad

**Ejemplo**: Sistema de recomendaciones
- Investigación: 1 semana
- Desarrollo: 4 semanas (modelo + API)
- Testing: 2 semanas (validación + A/B)
- Infraestructura: 1 semana
- **Total Effort**: ~2 persona-mes

---

## Consideraciones de Equipo y Recursos

### Tamaño del Equipo

**Equipo Pequeño (1-3 personas):**
- Prioriza features de bajo esfuerzo y alto impacto
- Considera features que pueden desarrollarse en paralelo
- Evita features que bloqueen a todo el equipo

**Equipo Mediano (4-8 personas):**
- Puedes tomar features de esfuerzo medio-alto
- Considera especialización (backend, frontend, design)
- Balancea features que requieren diferentes habilidades

**Equipo Grande (9+ personas):**
- Puedes tomar múltiples features grandes simultáneamente
- Considera dependencias entre equipos
- Usa RICE para coordinar prioridades entre equipos

---

### Habilidades Disponibles

**Ajusta Effort basado en:**
- ¿El equipo tiene experiencia con esta tecnología?
- ¿Necesitas contratar o entrenar?
- ¿Hay expertise disponible en la organización?

**Ejemplo**: Feature que requiere React pero tu equipo solo conoce Vue
- Effort base: 2 persona-mes
- Ajuste por curva de aprendizaje: +50%
- **Effort ajustado**: 3 persona-mes

---

### Restricciones de Tiempo

**Deadlines Fijos:**
- Si hay deadline legal o contractual, ajusta priorización
- Considera features críticas para cumplir deadline
- Puede requerir reducir scope de otras features

**Sprints/Iteraciones:**
- Agrupa features que caben en un sprint
- Considera features que pueden dividirse en incrementos
- Balancea features grandes vs. pequeñas por sprint

---

## Análisis de Riesgo por Feature

### Matriz de Riesgo vs. RICE Score

| RICE Score | Riesgo Bajo | Riesgo Medio | Riesgo Alto |
|------------|-------------|--------------|-------------|
| Alto (>80) | ✅ Priorizar | ⚠️ Priorizar con cuidado | ⚠️ Validar primero |
| Medio (40-80) | ✅ Considerar | ⚠️ Evaluar cuidadosamente | ❌ Postponer |
| Bajo (<40) | ⚠️ Reconsiderar | ❌ No priorizar | ❌ No priorizar |

### Tipos de Riesgo a Considerar

**Riesgo Técnico:**
- Tecnología no probada
- Dependencias externas inciertas
- Complejidad técnica alta
- **Mitigación**: Proof of concept, reducir scope, validar primero

**Riesgo de Negocio:**
- Hipótesis no validada
- Mercado incierto
- Competencia fuerte
- **Mitigación**: Investigación de mercado, MVP de la feature, validar con usuarios

**Riesgo de Recursos:**
- Requiere habilidades no disponibles
- Timeline muy ajustado
- Dependencias de otros equipos
- **Mitigación**: Contratar/entrenar, ajustar timeline, coordinar dependencias

---

## Métricas de Seguimiento Post-Implementación

### Validar Estimaciones RICE

Después de implementar cada feature, compara:

**Reach Real vs. Estimado:**
- ¿Cuántos usuarios realmente la usaron?
- ¿Por qué difiere de la estimación?
- Usa esto para mejorar futuras estimaciones

**Impact Real vs. Estimado:**
- ¿Qué métricas mejoraron? (retención, conversión, satisfacción)
- ¿El impacto fue el esperado?
- ¿Hay métricas inesperadas que mejoraron?

**Effort Real vs. Estimado:**
- ¿Cuánto tiempo realmente tomó?
- ¿Qué factores no consideraste?
- Usa esto para calibrar futuras estimaciones de esfuerzo

### Ajustar Framework

**Si Reach está consistentemente sobreestimado:**
- Reduce estimaciones futuras
- Usa datos históricos de adopción

**Si Impact está subestimado:**
- Revisa cómo mides impacto
- Considera métricas adicionales

**Si Effort está subestimado:**
- Agrega buffer a estimaciones
- Incluye más componentes (testing, docs, etc.)

---

## Escenarios Especiales

### Feature Crítica pero de Bajo RICE

**Ejemplo**: Feature de seguridad requerida por compliance
- RICE Score: 15 (bajo reach, alto effort)
- Pero es crítica para lanzar producto

**Solución**: 
- Aplica factor de ajuste por requisito legal/compliance
- Considera como "must-have" independientemente de RICE
- Documenta por qué se prioriza a pesar del bajo RICE

---

### Múltiples Features Similares

**Ejemplo**: 5 integraciones diferentes con herramientas similares

**Solución**:
- Agrupa en una feature: "Sistema de integraciones"
- Calcula RICE para el sistema completo
- Luego prioriza qué integraciones incluir primero

---

### Feature que Resuelve Múltiples Problemas

**Ejemplo**: Dashboard que mejora retención, aumenta conversión, y reduce soporte

**Solución**:
- Calcula RICE considerando el impacto combinado
- O divide en sub-features y calcula RICE para cada una
- Considera el impacto total en el análisis

---

## Plantilla de Workshop de Priorización RICE

### Preparación (Antes del Workshop)

1. **Lista de Features**: Compila todas las features propuestas
2. **Datos Disponibles**: Reúne analytics, feedback de usuarios, datos históricos
3. **Equipo**: Invita a stakeholders clave (producto, ingeniería, diseño, negocio)
4. **Tiempo**: Reserva 2-4 horas dependiendo del número de features

### Durante el Workshop

**Fase 1: Estimación Individual (30 min)**
- Cada persona estima RICE para cada feature independientemente
- Usa post-its o formulario digital

**Fase 2: Discusión y Alineación (60-90 min)**
- Para cada feature, discute estimaciones
- Identifica discrepancias y razones
- Llega a consenso en estimaciones

**Fase 3: Cálculo y Ranking (30 min)**
- Calcula RICE scores finales
- Ordena por score descendente
- Identifica dependencias

**Fase 4: Ajustes Estratégicos (30 min)**
- Revisa ranking con lente estratégico
- Aplica factores de ajuste si aplican
- Identifica must-haves independientes de RICE

**Fase 5: Roadmap (30 min)**
- Agrupa features por fase/sprint
- Identifica bloqueadores
- Define timeline

### Después del Workshop

1. **Documenta**: Guarda estimaciones, justificaciones, decisiones
2. **Comunica**: Comparte roadmap con stakeholders
3. **Itera**: Revisa y ajusta periódicamente (mensual o trimestral)

---

## Herramientas Digitales Recomendadas

### Para Cálculo y Tracking

1. **Google Sheets / Excel**
   - Plantilla con fórmulas RICE
   - Fácil de compartir y colaborar
   - Gratis y accesible

2. **Productboard**
   - Framework RICE integrado
   - Tracking de features y roadmap
   - Integración con herramientas de desarrollo

3. **Aha!**
   - Priorización RICE incluida
   - Roadmap visual
   - Integración con múltiples herramientas

4. **Notion / Coda**
   - Templates personalizables
   - Base de datos para tracking
   - Colaboración en tiempo real

### Para Visualización

1. **Tableau / Power BI**: Para dashboards avanzados
2. **Miro / Mural**: Para workshops colaborativos
3. **Lucidchart**: Para mapas de dependencias

---

## Preguntas Frecuentes (FAQ)

### ¿Qué hago si no tengo datos para estimar Reach?

**Respuesta**: 
- Usa proyecciones conservadoras basadas en tamaño de mercado
- Aplica regla del 10-30% (solo 10-30% de usuarios adoptan features nuevas)
- Reduce Confidence para reflejar incertidumbre
- Considera hacer investigación primero (encuestas, entrevistas)

---

### ¿Cómo manejo features que son "nice-to-have" pero tienen bajo RICE?

**Respuesta**:
- Si el esfuerzo es muy bajo (<0.5 persona-mes), considera hacerlas entre features grandes
- Agrupa múltiples nice-to-haves en un sprint de "mejoras menores"
- Valida si realmente son necesarias o pueden eliminarse

---

### ¿Qué pasa si dos features tienen el mismo RICE score?

**Respuesta**:
- Considera dependencias (¿una requiere la otra?)
- Considera factores estratégicos (alineación con objetivos)
- Considera riesgo (¿cuál tiene menor riesgo?)
- Considera esfuerzo (¿cuál puede completarse más rápido?)
- Si todo es igual, elige la que resuelve el problema más crítico

---

### ¿Debo recalcular RICE después de implementar features?

**Respuesta**: 
- Sí, pero no para cambiar prioridades pasadas
- Úsalo para validar y mejorar estimaciones futuras
- Compara estimaciones vs. realidad para calibrar
- Documenta aprendizajes para futuras priorizaciones

---

### ¿Cómo priorizo cuando tengo recursos muy limitados?

**Respuesta**:
- Enfócate en features de alto RICE y bajo esfuerzo
- Considera dividir features grandes en fases más pequeñas
- Prioriza bloqueadores críticos primero
- Postpona features de bajo RICE hasta tener más recursos
- Considera alternativas más simples que resuelvan el 80% del problema

---

## Recursos Adicionales y Referencias

### Artículos y Guías
- "RICE: Simple prioritization for product managers" - Intercom Blog
- "How to Prioritize Features with RICE" - ProductPlan
- "The RICE Framework: A Complete Guide" - Product Manager HQ

### Libros Recomendados
- "Inspired" by Marty Cagan - Sobre product management y priorización
- "The Lean Startup" by Eric Ries - Sobre MVP y validación
- "Hooked" by Nir Eyal - Sobre impacto en comportamiento de usuarios

### Comunidades
- Product Management communities en Reddit, Slack, Discord
- ProductTank meetups locales
- Product Management conferences (Mind the Product, etc.)

---

**Versión del Documento**: 2.0  
**Última Actualización**: [Fecha]  
**Mantenido por**: [Tu nombre/equipo]

