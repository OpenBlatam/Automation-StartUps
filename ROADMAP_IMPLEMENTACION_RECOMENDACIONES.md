# Roadmap de Implementación (8 semanas)

Meta: pasar de 0 a producción con recomendaciones personalizadas (híbrido CF + content) y medición de impacto.

## Semana 1: Descubrimiento y datos
- Inventario de fuentes: eventos, catálogo, histórico
- Definición de objetivos y KPIs (CR, AOV, CTR, RPM)
- Esquema de tracking y UTMs
- Entregables: data map, contrato de datos, checklist de calidad

## Semana 2: Ingesta y calidad
- ETL inicial: dedupe, normalización, IDs consistentes
- Validaciones: cobertura de usuarios/items, sparsity
- Entregables: dataset entrenable, reporte de calidad

## Semana 3: MVP del algoritmo
- Baseline: popularidad y content-based
- CF implícito (ALS) y/o modelos ligeros de secuencia
- Métricas offline: MAP@K, NDCG@K, Coverage
- Entregables: cuaderno de experimentos, comparación de modelos

## Semana 4: API y servicio
- FastAPI con endpoints: /recommend, /similar, /trending
- Caching (TTL), timeouts, logs
- Entregables: servicio contenedorizado (Docker), healthchecks

## Semana 5: Integración frontend
- Widgets: home, PDP, carrito; fallback seguro
- Instrumentación de eventos (view, click, add_to_cart, purchase)
- Entregables: feature flags, toggles por tráfico (10/50/100%)

## Semana 6: A/B y monitoreo
- Diseño del experimento: muestras, duración mínima
- Panel de métricas: CTR, CR, AOV, RPM, latencia, errores
- Entregables: dashboard, alertas (SLOs)

## Semana 7: Optimización y re-entreno
- Tuning de hiperparámetros y filtros de negocio
- Re-entreno incremental, job scheduler
- Entregables: pipeline de re-entreno, playbook de rollback

## Semana 8: Seguridad y escalado
- PII minimization, encriptación, rotación de claves
- Autoescalado, CDN para assets, warm cache
- Entregables: checklist de seguridad, prueba de carga

## Hitos
- H1: Dataset validado (S2)
- H2: API online (S4)
- H3: Tráfico real 10% (S5)
- H4: Resultados A/B (S6)
- H5: Pipeline re-entreno (S7)
- H6: Go-live 100% (S8)

## Riesgos y mitigaciones
- Datos esparsos → cold-start con content-based y popularidad
- Catálogo cambiante → jobs de refresco horarios
- Latencia alta → cache + precomputados

## Post-lanzamiento (30-60 días)
- Reglas de negocio avanzadas, slots por categoría
- Segmentación por cohorte/valor
- Roadmap v2: re-ranking con aprendizaje por refuerzo

