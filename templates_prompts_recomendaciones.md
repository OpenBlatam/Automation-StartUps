---
title: "Templates Prompts Recomendaciones"
category: "templates_prompts_recomendaciones.md"
tags: ["template"]
created: "2025-10-29"
path: "templates_prompts_recomendaciones.md"
---

# 📝 Templates de Prompts - Sistemas de Recomendaciones Personalizadas
## Prompts Listos para Usar con IA (ChatGPT, Claude, etc.)

## 🎯 PROMPTS PARA DOCUMENTACIÓN TÉCNICA

### Prompt 1: Generar Documentación Completa

```
Eres un experto en sistemas de recomendaciones personalizadas con Machine Learning. 

Genera documentación técnica completa para implementar un sistema de recomendaciones personalizadas con las siguientes especificaciones:

INDUSTRIA: [e-commerce/fashion/tech/saas/etc]
CATÁLOGO: [número] productos
DATOS DISPONIBLES: [historial compras, navegación, preferencias explícitas/solo implícitas]
NIVEL TÉCNICO: [principiante/intermedio/avanzado]
PLATAFORMA: [Shopify/WooCommerce/Magento/Custom]
ENFOQUE: [Python/ML o No-Code]

Incluye:
1. Arquitectura del sistema (diagramas ASCII)
2. Especificaciones técnicas detalladas
3. Código Python completo (si Python/ML) o guía no-code (si No-Code)
4. Guía de integración paso a paso
5. APIs y endpoints documentados
6. Métricas y evaluación
7. Troubleshooting común

Adapta el contenido según el nivel técnico especificado. Si es principiante, explica conceptos. Si es avanzado, incluye optimizaciones profundas.
```

---

### Prompt 2: Generar Código Python Completo

```
Genera código Python completo y funcionando para un sistema de recomendaciones personalizadas con estas características:

TIPO: [Collaborative Filtering / Content-Based / Híbrido]
DATOS: Historial de transacciones con columnas [user_id, item_id, rating/action, date]
OBJETIVO: Recomendar [número] productos por usuario

El código debe incluir:
1. Clase principal del sistema de recomendaciones
2. Preparación de datos (feature engineering)
3. Entrenamiento del modelo
4. Generación de recomendaciones
5. API REST con FastAPI para servir recomendaciones
6. Evaluación de métricas (RMSE, Precision@K, Recall@K)
7. Manejo de cold start (usuarios/productos nuevos)
8. Comentarios explicativos completos
9. Ejemplo de uso completo

Asegúrate de que el código sea:
- Producido y mantenible
- Bien documentado
- Incluye manejo de errores
- Listo para deployment

Librerías a usar: Surprise o TensorFlow Recommenders (especifica cuál prefieres).
```

---

### Prompt 3: Generar Propuesta Comercial

```
Genera una propuesta comercial completa para implementar un sistema de recomendaciones personalizadas para:

CLIENTE: [Nombre empresa]
INDUSTRIA: [sector]
SITUACIÓN ACTUAL:
- Conversión: [X]%
- Ticket promedio: $[Y]
- Visitantes/mes: [Z]
- Problemática: [descripción]

SOLUCIÓN PROPUESTA: Sistema recomendaciones basado en [datos históricos / preferencias / ambos]
IMPLEMENTACIÓN: [Python/ML o No-Code]
TIMELINE: [semanas]
INVERSIÓN: $[monto]

La propuesta debe incluir:
1. Resumen ejecutivo
2. Análisis del problema y oportunidad
3. Solución propuesta detallada
4. Comparativa Python/ML vs No-Code
5. ROI calculado con números específicos
6. Timeline de implementación
7. Recursos y equipo necesarios
8. Casos de éxito similares
9. Próximos pasos

Tono profesional pero accesible. Incluye gráficos/métricas donde sea útil.
```

---

## 🤖 PROMPTS PARA ANÁLISIS Y DECISIONES

### Prompt 4: Decidir Python vs No-Code

```
Analiza mi situación y recomienda si debo usar Python/ML o No-Code para sistema de recomendaciones:

MI SITUACIÓN:
- Visitantes/mes: [número]
- Productos en catálogo: [número]
- Conversión actual: [X]%
- Presupuesto año 1: $[monto]
- Equipo técnico: [Sí/No - describe si hay]
- Tiempo disponible: [semanas]
- Datos históricos: [descripción - qué tengo disponible]
- Necesidades específicas: [descripción]

Análiza:
1. Pros y contras de cada opción para mi caso
2. Costo total estimado 3 años para cada opción
3. Timeline realista para cada opción
4. Riesgos de cada opción
5. Recomendación final con justificación
6. Estrategia híbrida si aplica

Sé específico con números y razones claras.
```

---

### Prompt 5: Analizar ROI Específico

```
Calcula el ROI detallado de implementar un sistema de recomendaciones personalizadas con estos datos:

ACTUAL:
- Visitantes únicos/mes: [número]
- Conversión actual: [X]%
- Ticket promedio: $[Y]
- Revenue/mes: $[Z]

ESPERADO CON RECOMENDACIONES:
- Conversión esperada: [X]% (basado en benchmarks industria)
- Incremento ticket promedio: [X]% (cross-sell/up-sell)

COSTOS:
- Opción A (Python/ML): Desarrollo $[monto] + Infraestructura $[monto]/mes
- Opción B (No-Code): Setup $[monto] + Mensual $[monto]/mes

Calcula:
1. Revenue adicional mensual/año 1/año 3
2. ROI año 1, 2, 3 para ambas opciones
3. Payback period
4. Comparativa de costos acumulados 3 años
5. Recomendación basada en ROI

Incluye proyecciones conservadoras, realistas, y optimistas.
```

---

## 📊 PROMPTS PARA IMPLEMENTACIÓN

### Prompt 6: Generar Plan de Implementación

```
Crea un plan detallado semana por semana para implementar un sistema de recomendaciones personalizadas:

SITUACIÓN:
- Ruta elegida: [Python/ML o No-Code]
- Equipo disponible: [número personas, roles, experiencia]
- Datos: [qué datos tengo, calidad, volumen]
- Timeline objetivo: [semanas disponibles]
- Presupuesto: $[monto]

El plan debe incluir:
1. Timeline semana por semana (8 semanas recomendado)
2. Actividades específicas por semana
3. Entregables por fase
4. Recursos necesarios
5. Riesgos y mitigaciones
6. Métricas de progreso
7. Hitos principales
8. Plan de contingencia

Sé específico, accionable, y realista. Incluye checklist por semana.
```

---

### Prompt 7: Generar Features Engineering

```
Diseña el feature engineering completo para un sistema de recomendaciones con estos datos disponibles:

DATOS:
- Transacciones: [columnas disponibles]
- Productos: [columnas disponibles]
- Usuarios: [columnas disponibles]
- Navegación: [columnas disponibles - si hay]
- Búsquedas: [columnas disponibles - si hay]

Genera:
1. Features de usuario (frecuencia, preferencias, comportamiento)
2. Features de producto (popularidad, tendencias, características)
3. Features de interacción (recencia, frecuencia, intensidad)
4. Ratings implícitos (cómo calcular si no hay explícitos)
5. Manejo de cold start (usuarios/productos nuevos)
6. Decay temporal (peso a datos recientes)

Incluye código Python para crear cada feature, explicación de por qué es útil, y cómo se combinan.
```

---

## 🎨 PROMPTS PARA PERSONALIZACIÓN

### Prompt 8: Personalizar para Industria Específica

```
Personaliza un sistema de recomendaciones personalizadas para [INDUSTRIA ESPECÍFICA]:

INDUSTRIA: [e-commerce fashion / tech SaaS / streaming / marketplace / etc]

Considera:
1. Casos de uso específicos de esta industria
2. Tipos de recomendaciones más efectivas
3. Datos más relevantes para esta industria
4. Métricas de éxito específicas
5. Desafíos únicos de esta industria
6. Best practices del sector
7. Ejemplos reales de éxito en esta industria

Genera estrategia personalizada con ejemplos concretos adaptados a esta industria específica.
```

---

### Prompt 9: Adaptar a Nivel Técnico

```
Adapta la explicación/documentación de sistema de recomendaciones para nivel técnico: [PRINCIPIANTE / INTERMEDIO / AVANZADO]

Para PRINCIPIANTE:
- Explica conceptos básicos sin jerga técnica excesiva
- Usa analogías y ejemplos
- Incluye guías visuales y diagramas simples
- Define todos los términos técnicos

Para INTERMEDIO:
- Balance teoría/práctica
- Código comentado extensivamente
- Explicaciones técnicas sin profundizar excesivamente
- Asume conocimiento básico ML

Para AVANZADO:
- Detalles técnicos profundos
- Optimizaciones y mejores prácticas
- Arquitectura avanzada
- Asume experiencia ML/Data Science

Genera contenido adaptado según el nivel especificado.
```

---

## 🔍 PROMPTS PARA ANÁLISIS Y DEBUGGING

### Prompt 10: Analizar Sistema Existente

```
Analiza este sistema de recomendaciones existente y proporciona recomendaciones de mejora:

DATOS DEL SISTEMA:
- Tipo: [Collaborative / Content-Based / Híbrido / Otro]
- Métricas actuales: [CTR, conversión, revenue]
- Problemas identificados: [descripción]
- Datos disponibles: [qué tiene]
- Performance: [tiempo respuesta, escalabilidad]

Analiza:
1. Qué está funcionando bien
2. Qué puede mejorar
3. Problemas identificados y soluciones
4. Métricas que deberían mejorar
5. Recomendaciones específicas de optimización
6. Priorización de mejoras (quick wins primero)

Sé específico con recomendaciones accionables.
```

---

### Prompt 11: Debugging de Problemas

```
Ayúdame a debuggear este problema con mi sistema de recomendaciones:

PROBLEMA: [Descripción específica del problema]
SISTEMA: [Tipo de sistema, algoritmo usado]
MÉTRICAS: [Qué métricas se ven afectadas]
DATOS: [Qué datos usa el sistema]
ERRORES: [Errores específicos si hay]

Analiza:
1. Posibles causas del problema
2. Cómo diagnosticar cada causa
3. Soluciones específicas para cada causa
4. Cómo validar que se resolvió
5. Prevención para futuro

Incluye código/scripts si aplica para debugging.
```

---

## 💼 PROMPTS PARA NEGOCIO

### Prompt 12: Justificar Inversión Internamente

```
Crea una justificación ejecutiva para aprobar inversión en sistema de recomendaciones personalizadas:

SITUACIÓN:
- Empresa: [nombre/sector]
- Conversión actual: [X]%
- Revenue actual: $[monto]/mes
- Problemática actual: [descripción]
- Competencia: [qué están haciendo competidores]

PROPUESTA:
- Inversión requerida: $[monto]
- Timeline: [semanas]
- ROI esperado: [X]%

Genera:
1. Resumen ejecutivo para C-suite
2. Justificación estratégica
3. ROI detallado con números
4. Riesgos y mitigaciones
5. Comparativa con no hacer nada
6. Comparativa con competencia
7. Plan de implementación resumido
8. Próximos pasos si aprueba

Tono ejecutivo, conciso, data-driven. Máximo 2 páginas.
```

---

### Prompt 13: Comparar Herramientas Específicas

```
Compara estas herramientas específicas para mi caso:

HERRAMIENTAS A COMPARAR:
- [Herramienta 1]: [precio, características]
- [Herramienta 2]: [precio, características]
- [Herramienta 3]: [precio, características]

MI CASO:
- Volumen: [visitantes/mes, productos]
- Presupuesto: $[monto]
- Necesidades: [lista específica]
- Prioridades: [qué es más importante]

Genera comparativa:
1. Tabla comparativa de características
2. Costo total 3 años
3. Pros y contras específicos para mi caso
4. Recomendación final con ranking
5. Cuándo cambiaría la recomendación (si escala, si cambia X)

Sé específico con mi caso, no genérico.
```

---

## 🎓 PROMPTS PARA EDUCACIÓN

### Prompt 14: Crear Contenido del Curso

```
Genera contenido para un módulo del curso sobre sistemas de recomendaciones:

MÓDULO: [Módulo X: Título]
OBJETIVO: [Qué aprenderán los estudiantes]
NIVEL: [Principiante/Intermedio/Avanzado]
DURACIÓN: [horas]

Genera:
1. Objetivos de aprendizaje específicos
2. Contenido teórico (explicado según nivel)
3. Ejercicios prácticos paso a paso
4. Casos de uso reales
5. Código de ejemplo (si aplica)
6. Quiz de evaluación
7. Recursos adicionales

Asegúrate de que sea práctico, aplicable, y que los estudiantes puedan implementar después.
```

---

### Prompt 15: Crear Caso de Estudio

```
Crea un caso de estudio detallado de implementación de sistema de recomendaciones:

INDUSTRIA: [sector]
EMPRESA: [tipo de empresa]
SITUACIÓN INICIAL:
- Conversión: [X]%
- Revenue: $[Y]/mes
- Problemática: [descripción]

IMPLEMENTACIÓN:
- Enfoque usado: [Python/ML o No-Code]
- Timeline: [semanas]
- Retos encontrados: [lista]
- Soluciones aplicadas: [lista]

RESULTADOS:
- Conversión final: [X]%
- Revenue adicional: $[Y]/mes
- ROI: [X]%
- Lecciones aprendidas: [lista]

Formato: Narrativa completa, datos específicos, lecciones aprendidas, replicable.
```

---

## 🔄 PROMPTS PARA OPTIMIZACIÓN

### Prompt 16: Plan de Optimización Continua

```
Crea un plan de optimización continua para mi sistema de recomendaciones:

SISTEMA ACTUAL:
- Tipo: [algoritmo]
- Métricas: [CTR, conversión, revenue]
- Performance: [tiempo respuesta, uptime]

OBJETIVOS:
- Mejorar [métrica específica] en [X]%
- Reducir [problema específico]
- Optimizar [aspecto específico]

Genera:
1. Plan de A/B testing (qué testear, cómo, cuándo)
2. Frecuencia de re-entrenamiento recomendada
3. Métricas a monitorear continuamente
4. Proceso de optimización iterativa
5. Roadmap de mejoras priorizadas
6. Herramientas/métodos específicos

Sé específico, accionable, con timeline claro.
```

---

## 📱 PROMPTS PARA MARKETING Y VENTAS

### Prompt 17: Crear DM Personalizado

```
Crea un DM personalizado de LinkedIn para [NOMBRE] de [EMPRESA] sobre sistema de recomendaciones personalizadas:

CONTEXTO DEL LEAD:
- Empresa: [nombre, sector]
- Tamaño: [pequeña/mediana/grande]
- Actividad reciente: [qué publicó/compartió]
- Probable necesidad: [inferencia de su contenido]

PRODUCTO: [Tu producto/servicio de recomendaciones]
OBJETIVO: [Conseguir demo / Vender curso / Ofrecer audit]

El DM debe:
- Ser <150 palabras
- Mencionar algo específico que publicó/compartió
- Identificar problema relevante
- Ofrecer valor inmediato (audit, demo, caso de éxito)
- CTA claro con horarios específicos
- Tono profesional pero cercano

Sin ser genérico. Personalizado a su situación.
```

---

### Prompt 18: Crear Email Seguimiento

```
Genera un email de seguimiento después de un DM inicial sobre recomendaciones personalizadas:

SITUACIÓN:
- DM enviado hace [X] días
- No ha respondido aún
- Enfoque: [Dar nuevo ángulo / Recordar / Cerrar]

CONTEXTO:
- Lead: [nombre, empresa, industria]
- Tema DM anterior: [qué mencionaste]
- Nueva información: [caso de éxito nuevo, dato, etc.]

El email debe:
- No ser repetitivo del DM
- Ofrecer nuevo valor (caso, dato, recurso)
- Ser breve (<100 palabras)
- CTA claro pero no agresivo
- Tono profesional

Genera 3 variantes diferentes para testear.
```

---

## 🎯 PROMPTS PARA ANÁLISIS AVANZADO

### Prompt 19: Análisis de Datos para Recomendaciones

```
Analiza estos datos históricos y genera insights para mejorar sistema de recomendaciones:

DATOS DISPONIBLES:
[Pega o describe estructura de datos]

Analiza:
1. Calidad de datos (completitud, consistencia)
2. Patrones identificados en comportamiento
3. Segmentos de usuarios identificables
4. Productos más/menos popular
5. Oportunidades de recomendación
6. Problemas de datos a resolver
7. Features recomendadas a crear
8. Algoritmo recomendado basado en datos

Incluye código Python si aplica para análisis.
```

---

### Prompt 20: Benchmarking Competitivo

```
Analiza y compara sistemas de recomendaciones de estos competidores:

COMPETIDORES:
- [Competidor 1]: [lo que observas]
- [Competidor 2]: [lo que observas]
- [Competidor 3]: [lo que observas]

MI SISTEMA ACTUAL:
- [Descripción de lo que tienes o no tienes]

Genera:
1. Comparativa de features
2. Qué hacen mejor
3. Oportunidades para diferenciarme
4. Benchmarks de métricas (si observables)
5. Recomendaciones para mejorar mi sistema

Sé específico con observaciones, no genérico.
```

---

## 📚 PROMPTS PARA DOCUMENTACIÓN

### Prompt 21: Generar README Técnico

```
Genera un README técnico completo para un sistema de recomendaciones personalizadas con estas especificaciones:

SISTEMA:
- Tipo: [Collaborative / Content-Based / Híbrido]
- Stack: [Python, FastAPI, Surprise, etc.]
- Deployment: [Docker, Cloud, etc.]

El README debe incluir:
1. Descripción del proyecto
2. Arquitectura (diagrama ASCII)
3. Requisitos e instalación
4. Configuración
5. Uso básico con ejemplos
6. API documentation
7. Testing
8. Deployment
9. Contribución
10. Troubleshooting

Formato markdown profesional, técnico pero accesible.
```

---

## ✅ CHECKLIST DE USO DE PROMPTS

Antes de usar cualquier prompt, asegúrate de:
- [ ] Reemplazar [placeholders] con información real
- [ ] Especificar nivel de detalle que necesitas
- [ ] Indicar formato de salida preferido
- [ ] Mencionar restricciones (longitud, tono, etc.)
- [ ] Especificar si necesitas código, texto, o ambos

---

**Última actualización:** [Fecha]
**Versión:** 1.0 - Templates de Prompts Completos




