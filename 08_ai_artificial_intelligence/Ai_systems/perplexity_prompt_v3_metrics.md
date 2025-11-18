# Métricas y KPIs: Prompt Perplexity v3

## Resumen

Este documento define las métricas clave para monitorear la calidad, rendimiento y efectividad del prompt Perplexity v3. Incluye métricas técnicas, de calidad, de negocio y de usuario.

---

## Métricas de Calidad

### Formato y Estructura

**Formato Correcto (%)**
- **Definición:** Porcentaje de respuestas que siguen todas las reglas de formato
- **Objetivo:** >95%
- **Cálculo:** `(Respuestas con formato correcto / Total respuestas) * 100`
- **Medición:** Validación automática

**Estructura Apropiada (%)**
- **Definición:** Respuestas con estructura de secciones correcta
- **Objetivo:** >90%
- **Cálculo:** Validación de headers, listas, tablas
- **Medición:** Análisis de Markdown

**Legibilidad (Score)**
- **Definición:** Score de legibilidad (Flesch Reading Ease)
- **Objetivo:** 60-80 (estándar)
- **Cálculo:** Análisis de complejidad de oraciones
- **Medición:** Herramientas de análisis de texto

---

### Citaciones

**Citaciones Apropiadas (%)**
- **Definición:** Porcentaje de afirmaciones con citas correctas
- **Objetivo:** >90%
- **Cálculo:** `(Afirmaciones citadas / Total afirmaciones verificables) * 100`
- **Medición:** Análisis semántico + validación

**Formato de Citas Correcto (%)**
- **Definición:** Citas en formato [12][13] no [12, 13]
- **Objetivo:** >98%
- **Cálculo:** Validación de patrón regex
- **Medición:** Validación automática

**Fuentes Relevantes (%)**
- **Definición:** Citas a fuentes realmente utilizadas
- **Objetivo:** 100%
- **Cálculo:** Validación de índices de fuentes
- **Medición:** Cross-reference con search results

---

### Tono y Estilo

**Tono Consistente (%)**
- **Definición:** Respuestas con tono apropiado (expert, unbiased, journalistic)
- **Objetivo:** >95%
- **Cálculo:** Análisis de sentimiento y estilo
- **Medición:** NLP analysis

**Uso de Frases Prohibidas (Count)**
- **Definición:** Número de frases de hedging encontradas
- **Objetivo:** 0
- **Cálculo:** Búsqueda de frases prohibidas
- **Medición:** Validación automática

**Neutralidad (Score)**
- **Definición:** Score de neutralidad en temas controvertidos
- **Objetivo:** >0.8 (0-1 scale)
- **Cálculo:** Análisis de sesgo y perspectiva
- **Medición:** Análisis de polaridad

---

## Métricas de Contenido

### Completitud

**Cobertura de Consulta (%)**
- **Definición:** Porcentaje de aspectos de la consulta cubiertos
- **Objetivo:** >90%
- **Cálculo:** Análisis de cobertura semántica
- **Medición:** Comparación query vs respuesta

**Longitud Apropiada (%)**
- **Definición:** Respuestas con longitud adecuada al tipo de consulta
- **Objetivo:** >85%
- **Cálculo:** Validación por tipo de consulta
- **Medición:** Análisis de word count por tipo

**Profundidad de Respuesta (Score)**
- **Definición:** Nivel de detalle y profundidad
- **Objetivo:** Variable por tipo
- **Cálculo:** Análisis de complejidad y detalle
- **Medición:** Análisis de contenido

---

### Precisión

**Precisión Factual (%)**
- **Definición:** Porcentaje de afirmaciones verificables correctas
- **Objetivo:** >95%
- **Cálculo:** Validación manual de muestra
- **Medición:** Revisión humana

**Consistencia Interna (%)**
- **Definición:** Respuestas sin contradicciones internas
- **Objetivo:** 100%
- **Cálculo:** Análisis de coherencia
- **Medición:** Validación lógica

**Actualidad de Información (%)**
- **Definición:** Uso de fuentes recientes cuando aplica
- **Objetivo:** >80% para temas time-sensitive
- **Cálculo:** Análisis de fechas de fuentes
- **Medición:** Metadata de fuentes

---

## Métricas de Rendimiento

### Tiempo de Respuesta

**Latencia Promedio (ms)**
- **Definición:** Tiempo promedio de generación de respuesta
- **Objetivo:** <2500ms
- **Cálculo:** Promedio de tiempos de respuesta
- **Medición:** Logs de sistema

**Latencia P95 (ms)**
- **Definición:** Percentil 95 de tiempos de respuesta
- **Objetivo:** <3500ms
- **Cálculo:** Percentil 95 de distribución
- **Medición:** Logs de sistema

**Latencia P99 (ms)**
- **Definición:** Percentil 99 de tiempos de respuesta
- **Objetivo:** <5000ms
- **Cálculo:** Percentil 99 de distribución
- **Medición:** Logs de sistema

---

### Throughput

**Respuestas por Segundo (RPS)**
- **Definición:** Número de respuestas generadas por segundo
- **Objetivo:** >10 RPS
- **Cálculo:** Total respuestas / Tiempo
- **Medición:** Métricas de sistema

**Pico de Carga (RPS)**
- **Definición:** Máximo RPS durante picos
- **Objetivo:** >20 RPS
- **Cálculo:** Máximo en ventana de tiempo
- **Medición:** Métricas de sistema

---

## Métricas de Negocio

### Satisfacción del Usuario

**Satisfacción Promedio (Score)**
- **Definición:** Rating promedio de usuarios (1-5)
- **Objetivo:** >4.5/5
- **Cálculo:** Promedio de ratings
- **Medición:** Encuestas post-respuesta

**Tasa de Satisfacción (%)**
- **Definición:** Porcentaje de usuarios satisfechos (4-5)
- **Objetivo:** >85%
- **Cálculo:** `(Ratings 4-5 / Total ratings) * 100`
- **Medición:** Encuestas

**Net Promoter Score (NPS)**
- **Definición:** NPS basado en recomendación
- **Objetivo:** >50
- **Cálculo:** `% Promoters - % Detractors`
- **Medición:** Encuestas

---

### Uso y Adopción

**Tasa de Re-uso (%)**
- **Definición:** Porcentaje de usuarios que vuelven a usar
- **Objetivo:** >65%
- **Cálculo:** `(Usuarios recurrentes / Total usuarios) * 100`
- **Medición:** Analytics

**Consultas por Usuario (Avg)**
- **Definición:** Promedio de consultas por usuario
- **Objetivo:** >3
- **Cálculo:** Total consultas / Total usuarios
- **Medición:** Analytics

**Tiempo de Resolución (min)**
- **Definición:** Tiempo promedio hasta satisfacción
- **Objetivo:** <2.5 min
- **Cálculo:** Promedio de tiempo por sesión
- **Medición:** Analytics

---

## Métricas por Tipo de Consulta

### Academic Research

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Longitud (palabras) | 500-2000 | Word count |
| Citas por respuesta | >10 | Count |
| Secciones | >3 | Count |
| Profundidad | Alta | Análisis contenido |

### Recent News

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Agrupación por temas | 100% | Validación |
| Títulos destacados | 100% | Validación |
| Fuentes diversas | >3 | Count |
| Actualidad | <24h | Timestamp |

### Coding

| Métrica | Objetivo | Medición |
|---------|----------|----------|
| Bloques de código | >0 | Count |
| Sintaxis correcta | 100% | Validación |
| Explicación incluida | 100% | Validación |
| Ejemplos prácticos | >0 | Count |

---

## Dashboard de Métricas

### Vista Ejecutiva

**KPIs Principales:**
- Satisfacción Usuario: 4.5/5
- Formato Correcto: 95%
- Latencia Promedio: 2.3s
- Tasa de Re-uso: 67%

### Vista Operacional

**Métricas Técnicas:**
- Formato: 95.2%
- Citaciones: 91.5%
- Tono: 96.8%
- Longitud: 87.3%

**Métricas de Rendimiento:**
- Latencia P50: 2.1s
- Latencia P95: 3.2s
- Throughput: 12 RPS
- Error Rate: 2.1%

### Vista Detallada

**Por Tipo de Consulta:**
- Academic: 94.5% formato correcto
- News: 96.2% formato correcto
- Coding: 93.8% formato correcto
- People: 95.1% formato correcto

---

## Alertas y Thresholds

### Alertas Críticas

| Métrica | Threshold | Acción |
|---------|-----------|--------|
| Formato Correcto | <85% | Revisar prompt |
| Satisfacción | <3.5/5 | Investigar causas |
| Error Rate | >5% | Rollback considerar |
| Latencia P95 | >5s | Optimizar |

### Alertas de Advertencia

| Métrica | Threshold | Acción |
|---------|-----------|--------|
| Formato Correcto | <90% | Monitorear |
| Citaciones | <85% | Revisar ejemplos |
| Tono | <90% | Validar restricciones |
| Latencia P95 | >4s | Investigar |

---

## Herramientas de Medición

### Validación Automática

```python
class MetricsCollector:
    """Recolector de métricas para prompt v3"""
    
    def collect_quality_metrics(self, response, query_type):
        """Recolecta métricas de calidad"""
        return {
            'format_correct': self.validate_format(response),
            'citations_appropriate': self.validate_citations(response),
            'tone_consistent': self.validate_tone(response),
            'length_appropriate': self.validate_length(response, query_type)
        }
    
    def collect_performance_metrics(self, start_time, end_time):
        """Recolecta métricas de rendimiento"""
        latency = (end_time - start_time) * 1000  # ms
        return {
            'latency_ms': latency,
            'timestamp': end_time
        }
    
    def collect_business_metrics(self, user_feedback):
        """Recolecta métricas de negocio"""
        return {
            'satisfaction': user_feedback.get('rating'),
            'helpful': user_feedback.get('helpful'),
            'would_recommend': user_feedback.get('recommend')
        }
```

---

## Reportes

### Reporte Diario

- Resumen de métricas del día
- Comparación con día anterior
- Alertas activas
- Top issues

### Reporte Semanal

- Tendencias de la semana
- Comparación semana anterior
- Análisis de tipos de consulta
- Recomendaciones

### Reporte Mensual

- Análisis completo del mes
- Comparación mes anterior
- Identificación de patrones
- Plan de mejoras

---

**Última actualización:** 2025-05-13  
**Versión:** 1.0

