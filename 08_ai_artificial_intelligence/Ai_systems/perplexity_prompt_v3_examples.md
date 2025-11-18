# Perplexity Prompt v3 — Ejemplos Prácticos

## Resumen

Este documento complementa `perplexity_prompt_enhanced_v3.md` y `perplexity_prompt_compact_v3.md` con ejemplos prácticos alineados a las reglas actualizadas. Cada sección incluye: (1) consulta, (2) resultados de búsqueda simulados y (3) respuesta esperada siguiendo formato, tono y citación requeridos.

---

## Academic Research

**Query**  
Explain the role of epigenetic modifications in cancer progression and current therapeutic strategies targeting them

**Resultados de búsqueda simulados**  
[1] Review article summarizing DNA methylation and histone modification changes observed in breast, lung, and colorectal cancers (Nature Reviews Cancer, 2024).  
[2] Clinical trials evaluating DNMT inhibitors (azacitidine, decitabine) and HDAC inhibitors (vorinostat, panobinostat) for hematologic malignancies (ASCO 2023).  
[3] Emerging CRISPR-based epigenetic editors enabling locus-specific reprogramming in solid tumors (Cell, 2024).

**Respuesta esperada (fragmento)**  
Epigenetic remodeling—particularly aberrant DNA methylation and histone acetylation—disrupts oncogene and tumor suppressor expression across solid tumors and hematologic malignancies, accelerating disease progression[1]. Approved DNMT and HDAC inhibitors partially reverse these marks in leukemias, while next-generation CRISPR epigenetic editors target solid tumors more selectively, although delivery and off-target risks persist[2][3].

---

## Recent News

**Query**  
Resumir las noticias más recientes sobre políticas globales de IA responsable

**Resultados de búsqueda simulados**  
[1] Unión Europea aprueba formalmente el AI Act con requisitos escalonados y sanciones (Reuters, 2025-05-10).  
[2] EE. UU. publica directrices actualizadas de NIST para auditorías de IA en sectores críticos (Washington Post, 2025-05-08).  
[3] Consorcio Indo-Pacífico lanza estándar abierto para trazabilidad de datasets (Nikkei Asia, 2025-05-07).

**Respuesta esperada (estructura)**  
Introducción (2-3 oraciones).  
`## Regulaciones Clave` con lista:  
- **UE aprueba AI Act** — ...[1]  
- **EE. UU. actualiza directrices NIST** — ...[2]  
- **Consorcio Indo-Pacífico define estándar** — ...[3]  
Cierre (2 oraciones) resaltando convergencia regulatoria.

---

## People

**Query**  
Provide a concise biography of Fei-Fei Li highlighting current role, academic history, and major initiatives

**Resultados simulados**  
[1] Stanford HAI profile (2025).  
[2] NYTimes feature on AI4ALL (2024).  
[3] Google Scholar citations on ImageNet (2009).

**Respuesta esperada (fragmento)**  
Fei-Fei Li codirects Stanford’s Human-Centered AI Institute and serves as Sequoia Professor of Computer Science, focusing on trustworthy AI systems[1]. She previously led Google Cloud AI/ML, co-created ImageNet—which catalyzed deep learning breakthroughs—and co-founded AI4ALL to expand representation in AI education[2][3].

---

## Coding

**Query**  
Write a Python script that ingests a CSV of transactions, flags anomalies using an IsolationForest, and logs results to CloudWatch

**Resultados simulados**  
[1] Scikit-learn IsolationForest documentation.  
[2] AWS CloudWatch Logs Python SDK example.  
[3] Blog on preprocessing transactional data for anomaly detection.

**Respuesta esperada (estructura)**  
1. Código en bloque ```python``` mostrando: carga de CSV (pandas), preparación (scaling opcional), entrenamiento IsolationForest, clasificación, escritura a CloudWatch.  
2. Explicación breve post código describiendo hiperparámetros, umbrales y configuración de logging.  
3. Citaciones inline tras frases que referencian fuentes[1][2][3].

---

## Creative Writing

**Query**  
Write a 200-word cyberpunk vignette about a botanist hacking climate-control domes to revive extinct orchids

**Resultados simulados**  
No citations requeridas (Creative Writing).  
**Respuesta esperada**: Inicio con resumen, `## Scene` etc., sin citas.

---

## URL Lookup

**Query**  
https://example.org/ai-governance-blueprint

**Reglas destacadas**  
- Solo usar contenido del resultado 1.  
- Cita obligatoria `[1]`.  
- Finalizar con `[1]`.

**Respuesta esperada (estructura)**  
Introducción corta, `## Key Sections`, tabla con secciones/resumen, conclusión cerrando con `[1]`.

---

## Definition / Explanation

**Query**  
Define \"data flywheel\" in AI product strategy and provide one SaaS example

**Resultados simulados**  
[1] Bain & Company whitepaper on AI flywheels (2023).  
[2] Case study: Notion AI personalization loop (2024).

**Respuesta esperada**  
Definición concisa con cita[1], ejemplo Notion AI describiendo señales → personalización → engagement con cita[2].

---

## Cómo Usar Este Documento

1. Replica la estructura mostrada para cada tipo de consulta.  
2. Ajusta longitud según complejidad (ver `perplexity_prompt_enhanced_v3.md`).  
3. Mantén consistencia de tono y citas.  
4. Añade nuevos ejemplos conforme surjan casos relevantes.


