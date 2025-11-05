# SOP: Lanzamiento de Campaña Publicitaria Digital

Resumen Ejecutivo (1‑página)
- Qué: Procedimiento integral para planificar, lanzar, optimizar y cerrar campañas multi‑canal con control de riesgos, cumplimiento y ROI.  
- Por qué: Acelerar time‑to‑market, estandarizar calidad, maximizar ROAS/CAC y asegurar gobernanza.  
- Cómo: Fases, checklists, RACI, SLAs, métricas, plantillas y playbooks por canal.  
- Éxito: KPIs meta por funnel/canal, varianza ≤ ±15%, incidentes críticos ≤ S1/mes, auditorías sin hallazgos severos.

Tabla de Contenidos
- 1 Objetivo, 2 Alcance, 3 Responsables, 4 Definiciones, 5 Procedimiento  
- 6 Herramientas, 7 Tiempos, 8 KPIs, 9 Controles, 10 Riesgos, 11 Revisión  
- 12 Registros, 13 Anexos, 14–100 Playbooks/Plantillas/Políticas  
- 101+ Apéndices adicionales (este documento crece de forma versionada)

Enlaces rápidos
- Objetivo (#1-objetivo)  
- Procedimiento (#5-procedimiento-detallado)  
- Pre‑Launch Checklist (#25-checklists-qa-detalladas)  
- Lanzamiento y Runbook (#56-runbook-de-go-live-por-hora)  
- Optimización (#15-reglas-de-decision-y-experimentacion)  
- KPIs (#8-kpis)  
- Cumplimiento/Privacidad (#18-cumplimiento-privacidad-y-accesibilidad)  
- Incidentes y SLAs (#36-playbook-de-incidentes-y-slas, #63-tabla-de-slas-resumen)  
- Reporting y Dashboards (#20-especificaciones-de-dashboard-y-alertas)  
- Changelog (#historial-de-cambios)

### Guía de implementación rápida (5 min)
- Paso 1: Duplica plantillas clave: brief, plan de medios, pre‑lanzamiento (ver Plantillas relacionadas).  
- Paso 2: Define objetivos SMART y KPIs por canal (usa metas de la sección 23).  
- Paso 3: Carga 2–3 variantes creativas por canal y configura UTMs estándar.  
- Paso 4: Verifica tracking (GTM/GA4 + server‑side) y activa alertas.  
- Paso 5: Ejecuta Soft Launch (10–20%), sigue el runbook T+1h/6h/24h y documenta cambios en el changelog.

### 111. Checklist maestro end‑to‑end
- Estrategia: brief aprobado, objetivos SMART, presupuesto y timeline.  
- Planificación: plan de medios, matriz de tests, nombres/UTM definidos.  
- Creatividades: variantes por formato/canal, compliance, accesibilidad.  
- Técnica: landings QA (perf/a11y/forms), tracking client+server, dashboards.  
- Pre‑launch: checklist Go/No‑Go, alertas y on‑call activos.  
- Lanzamiento: soft rollout, runbook por hora, monitoreo 1h/6h/24h.  
- Optimización: reglas, redistribución, iteraciones semanales, documentación.  
- Cierre: reporte final, post‑mortem, archivado, knowledge transfer.

### 112. Matriz de decisión y árbol de decisiones
- Árbol (simplificado):  
  - ¿Tracking íntegro? → No: Incidente S1 y rollback → Sí: continuar.  
  - ¿KPIs dentro de ±15% del plan? → No: ajustar presupuesto y pausar outliers → Sí: escalar ganadores.  
  - ¿Fatiga creativa? → Sí: nuevas variantes; No: mantener.  
- Matriz (impacto × urgencia): priorizar acciones con alto impacto y alta urgencia; documentar en changelog.

### 113. Priorización de experimentos (ICE/RICE)
- ICE: Impact (1–5) × Confidence (1–5) × Ease (1–5).  
- RICE: (Reach × Impact × Confidence) / Effort.  
- Reglas: top‑5 experimentos por sprint; MVD y horizontes mínimos; registrar hipótesis, criterios y resultados.

### 114. Plan de capacitación 30/60/90 (por rol)
- 30 días: onboarding, plataformas base (Meta/Google/LinkedIn), GA4/GTM, SOPs.  
- 60 días: experimentación, reporting, incident response, compliance.  
- 90 días: ownership de canal/proyecto, auditorías, optimización avanzada/MMM básico.  
- Evidencias: quizzes, shadowing, primeros entregables y evaluación de competencias.

### Historial de cambios
- 1.1 (30/10/2025): Resumen ejecutivo, enlaces rápidos, checklists avanzados, medición MTA/MMM, SSC, SLAs ampliados, compliance y anexos operativos completos, checklist maestro, matriz de decisión, RICE/ICE y plan 30/60/90.  
- 1.0 (30/10/2025): Creación inicial.

Código: MKT-CAM-001  
Versión: 1.1  
Fecha: 30/10/2025

---

### 1. Objetivo
Establecer un procedimiento estándar, predecible y medible para planificar, ejecutar, monitorear y optimizar campañas publicitarias digitales multi-canal con foco en eficiencia operativa, cumplimiento y retorno sobre la inversión.

### 2. Alcance
- Aplica a campañas en: Meta Ads, Google Ads (Search/Display/YouTube), LinkedIn Ads, X Ads, TikTok Ads y Email Paid Sponsorships.  
- Cubre fases: briefing, planificación, preparación técnica/creativa, lanzamiento, monitoreo, optimización y cierre post-campaña.  
- Excluye: producción audiovisual compleja (se rige por SOP de producción) y negociación de medios tradicionales.

### 3. Responsables
- Sponsor: Director(a) de Marketing.  
- Owner operativo: Campaign Manager.  
- Soporte: Paid Media Specialist, Data Analyst, Creative Lead, Web/Marketing Ops, Legal/Compliance, Finanzas.

#### 3.1 Matriz RACI (resumen)
- Brief de campaña: R (Campaign Manager), A (Dir. Marketing), C (Ventas/Producto), I (Finanzas).  
- Plan de medios y presupuesto: R (Paid Media), A (Dir. Marketing), C (Finanzas), I (Producto).  
- Creatividades y copys: R (Creative Lead), A (Campaign Manager), C (Brand/Legal), I (Paid Media).  
- Tracking/Medición: R (Marketing Ops), A (Campaign Manager), C (Data Analyst), I (Paid Media).  
- Lanzamiento y monitoreo: R (Paid Media), A (Campaign Manager), C (Data Analyst), I (Soporte).  
- Reporte y cierre: R (Data Analyst), A (Campaign Manager), C (Dir. Marketing), I (Finanzas/Ventas).

### 4. Definiciones clave
- KPI: Indicador clave de desempeño; guía decisiones de optimización.  
- ROAS: Return On Ad Spend = Ingresos atribuidos / Gasto publicitario.  
- CTR: Click-Through Rate.  
- CVR: Conversion Rate.  
- CPA/CAC: Coste por Adquisición / Coste de Adquisición de Cliente.  
- LTV: Lifetime Value.

### 5. Procedimiento detallado

#### 5.1 Brief y Alineación (Día 0–1)
1) Completar Brief de Campaña (plantilla anexa).  
2) Definir objetivos SMART, audiencia(s), propuesta de valor y oferta.  
3) Alinear presupuesto, timeline, canales y restricciones legales.  
4) Aprobar brief (Dir. Marketing).

Entregables: Brief aprobado, calendario macro, objetivos con baseline.

#### 5.2 Plan de Medios y Experimentos (Día 1–3)
1) Seleccionar canales y asignar presupuesto por fase (soft/full).  
2) Diseñar hipótesis y plan de tests A/B (mensajes, creatividades, audiencias, landings).  
3) Definir estructura de campañas/grupos/ads y nomenclatura UTM.  
4) Aprobar plan (Campaign Manager).

Entregables: Plan de medios, matriz de experimentos, naming/UTM.

#### 5.3 Producción Creativa (Día 2–6)
1) Producir piezas (estáticas, video, copys, formatos por canal).  
2) Validación de marca y revisión legal/compliance.  
3) Versionar assets para tests (al menos 2–3 variantes por hipótesis).  
4) Subir a gestor de assets con control de versiones.

Entregables: Kit creativo final + variantes aprobadas.

#### 5.4 Preparación Técnica (Día 2–6)
1) Landings: copy/UX, rendimiento, móviles, formularios, accesibilidad.  
2) Tracking: píxeles, conversiones, eventos, consent mode, UTM, metas en analytics.  
3) Integraciones: CRM/marketing automation, webhooks, QA de datos.  
4) Dashboards: configurar vistas de monitoreo en tiempo real.

Entregables: QA técnico firmado, checklist pre-lanzamiento OK.

#### 5.5 Pre‑Launch Checklist (Día 6)
- Creatividades y copys cargados y aprobados.  
- Segmentaciones, exclusiones, límites de frecuencia y budgets configurados.  
- Enlaces/UTM verificados en todos los anuncios.  
- Píxeles/eventos reciben datos en tiempo real.  
- Pruebas multi-dispositivo (incl. rendimiento LCP/CLS).  
- Riesgos mitigados y plan on-call definido.

Gate: Go/No-Go por Campaign Manager y Dir. Marketing.

#### 5.6 Lanzamiento y Soft Rollout (Día 7)
1) Activar campañas con presupuesto reducido (10–20%).  
2) Monitoreo hora 1, 6 y 24 (entregabilidad, CTR, CVR, tracking).  
3) Corregir issues técnicos y pausar outliers negativos.  
4) Documentar aprendizajes iniciales.

#### 5.7 Escalado y Optimización Continua (Semana 2–4)
1) Reasignar presupuesto a ganadores (reglas: +20–30%/48h si KPIs ≥ objetivo).  
2) Iterar creatividades/audiencias semanalmente según resultados.  
3) Ajustar pujas, ubicaciones y límites de frecuencia.  
4) Revisiones de performance diarias; comité semanal de optimización.

#### 5.8 Cierre y Post‑Mortem (Semana 4–5)
1) Reporte final: resultados vs objetivos, ROAS/CPA, contribución a pipeline/ingresos.  
2) Análisis de cohortes y atribución (data-driven/last click comparado).  
3) Lecciones aprendidas y backlog de mejoras.  
4) Archivado de activos y documentación; actualización de librerías ganadoras.

### 6. Herramientas recomendadas
- Ads: Meta, Google Ads, LinkedIn, TikTok, X.  
- Analytics/Tracking: GA4, GTM, GAds Conversions, Meta Events Manager, Looker/Datastudio.  
- Gestión: ClickUp/Jira, Calendario campañas, FigJam para experimentos.  
- Creativo: Figma/Adobe, Frame.io; Librería de assets.  
- Datos/CRM: HubSpot/ActiveCampaign/Salesforce.  
- QA/Testing: BrowserStack, PageSpeed, Tag Assistant.

### 7. Tiempos objetivo (SLA internos)
- Brief y aprobación: 1–2 días.  
- Plan de medios/tests: 2 días.  
- Creatividades: 3–5 días.  
- Setup técnico + QA: 3–4 días.  
- Soft launch: Día 7 (desde kick-off).  
- Reporte final: ≤ 7 días tras cierre.

### 8. KPIs
- Alcance/impressions por canal.  
- CTR por formato y audiencia.  
- CPC, CPM.  
- CVR por landing y evento clave.  
- CPA/CAC vs objetivo.  
- ROAS/Ingresos atribuidos.  
- Lead quality: MQL/SQL rate, costo por MQL/SQL.  
- Velocidad de pipeline y revenue influence (si aplica).

Objetivos de referencia iniciales (ajustar por canal/industria): CTR ≥ 1.5%, CVR ≥ 3%, CPA ≤ objetivo financiero, ROAS ≥ 3x.

### 9. Controles y verificación
- Doble validación de tracking y UTM.  
- Revisión legal de claims sensibles.  
- QA de landings (velocidad, formularios, accesibilidad).  
- Auditoría de naming y permisos en cuentas publicitarias.  
- Reglas automáticas de pausado/alertas.

### 10. Riesgos y mitigaciones
- Rechazo de anuncios: preparar variantes conformes; consulta rápida con Legal.  
- Subatribución por falta de señales: priorizar conversiones de calidad y Consent Mode.  
- Fatiga creativa: rotación semanal y librería de ganadores.  
- Sobre-gasto: límites diarios y alertas en 80/100% del budget.  
- Caída de landing: health checks y rollback a versión estable.

### 11. Revisión periódica y mejora continua
- Stand-up diario de performance (15 min).  
- Weekly review: performance por hipótesis; decisiones de presupuesto/creativos.  
- Monthly retro: comparar contra benchmarks, actualizar playbooks, incorporar learnings.  
- Quarterly audit: auditoría integral de cuentas, taxonomía, tracking y librerías.

### 12. Registros y entregables
- Brief, plan de medios, matriz de tests, checklist QA, reporte diario/weekly, reporte final y acta de post‑mortem.

### 13. Anexos

#### 13.1 Plantilla breve de Brief de Campaña
Objetivo SMART | Audiencia | Oferta/Propuesta | Canales | Presupuesto | KPIs | Timeline | Riesgos | Aprobaciones.

#### 13.2 Checklist Pre‑Launch (extracto)
- Píxeles/eventos verificados  
- UTM y enlaces OK  
- Creatividades conformes  
- Landings rápidas y accesibles  
- Dashboards en vivo  
- On‑call definido

#### 13.3 Nomenclatura UTM (ejemplo)
utm_source=canal | utm_medium=paid | utm_campaign=campana_yyyy_mm | utm_content=variante | utm_term=keyword

---

Historial de cambios: 1.0 (30/10/2025) – Creación inicial.

---

### 14. Playbooks por canal (operativos y de optimización)

#### 14.1 Meta Ads (Facebook/Instagram)
- Objetivo típico: Awareness, Leads, Conversiones DPA.  
- Estructura recomendada: 1 campaña/objetivo, 3–5 conjuntos/audiencia, 3–5 anuncios/variante.  
- Optimización: Advantage+ donde aplique; limitar exclusiones redundantes; consolidar siempre que el volumen lo permita.  
- Señales de calidad: Priorizar conversiones de valor, agregar eventos intermedios (scroll/form start) solo para diagnóstico.  
- Reglas automáticas: Pausar anuncio si CPA > 1.5× objetivo tras 3,000 impresiones; escalar +20%/48h si CPA ≤ objetivo y CVR estable.  
- Creativo: Rotación semanal; formatos: 1:1, 4:5, 9:16; thumbstop < 2s; variantes con y sin UGC.  
- Benchmarks guía: CTR ≥ 1.0–1.5%, CVR landing ≥ 2–4%.

#### 14.2 Google Ads (Search/Display/YouTube)
- Search: RSA con 8–12 titulares y 3–4 descripciones; agregar sitelinks/callouts; concordancias combinadas; lista de negativas viva.  
- Display: Targeting por audiencias de intención; creatividad clara con beneficio y CTA; frecuencia ≤ 3/día.  
- YouTube: Skippable con hook 0–5s; targeting por audiencias y temas; CPV/CPCV objetivo.  
- Reglas: Pausar palabra clave si QS ≤ 5 y CPA alto; aumentar puja +10% en segmentos con ROAS ≥ objetivo.  
- Benchmarks: CTR Search ≥ 3–5%, QS ≥ 7; VTR YouTube ≥ 20–35%.

#### 14.3 LinkedIn Ads
- Objetivo: B2B leads cualificados.  
- Segmentación: Títulos, funciones, industrias; usar lista de cuentas (ABM) cuando sea posible.  
- Creativo: Mensaje basado en valor (whitepaper, webinar, demo); pruebas con Document Ads/Lead Gen Forms.  
- Reglas: Revisar CPL por segmento; pausar si CPL > 1.4× objetivo tras 50 clics.  
- Benchmarks: CTR ≥ 0.5–1.0%; CVR LGF ≥ 10–15%.

#### 14.4 TikTok/X Ads
- Creativo first: nativo, dinámico, subtítulos y gancho inmediato.  
- Volumen: requerir variantes múltiples; aprendizaje sensible a cambios.  
- Reglas: Escalar gradual; evitar ediciones frecuentes durante aprendizaje.  
- Benchmarks: CTR ≥ 1–2%; CVR ≥ 1.5–3% (según vertical).

### 15. Reglas de decisión y experimentación
- Minimum Viable Data (MVD): No decidir hasta lograr ≥ 95% credibilidad con n≥3,000 impresiones/anuncio o ≥ 50 clics por variante (lo que ocurra primero).  
- Jerarquía de optimización: 1) Tracking/atribución → 2) Landing/Oferta → 3) Audiencia → 4) Creativo → 5) Pujas/Presupuesto.  
- Diseño de tests: 1 hipótesis a la vez por grupo; duración mínima 5–7 días para evitar sesgos de día de semana.  
- Criterios de ganadores: uplift ≥ +10% vs control con significancia práctica y coste sostenible.

### 16. Controles de presupuesto y pacing
- Topes: Daily cap por campaña y por cuenta; alertas a 80% y 100%.  
- Pacing: Revisar consumo 3× al día en lanzamiento; objetivo lineal salvo estacionalidad.  
- Redistribución: Movimiento ≤ 20–30% cada 48h salvo incidentes.  
- Protección: Kill-switch manual y regla automática si gasto sin conversiones > umbral diario definido.

### 17. Métricas avanzadas y fórmulas
- ROAS = Ingresos atribuidos / Gasto publicitario.  
- CAC = Gasto atribuible / Nuevos clientes.  
- LTV:CAC objetivo ≥ 3:1.  
- Incremental lift (si experimento holdout): Δ conversiones grupo test vs control / gasto incremental.  
- Quality Score drivers (Search): CTR esperado, relevancia del anuncio, experiencia de la página de destino.

### 18. Cumplimiento, privacidad y accesibilidad
- Privacidad: Consent Mode, banners de consentimiento, DPA con plataformas, política de privacidad actualizada.  
- Cumplimientos: GDPR/CCPA/LGPD según jurisdicción; exclusiones de audiencias sensibles; control de límites de frecuencia.  
- Accesibilidad: Contraste de color, subtítulos en video, texto alternativo en imágenes, navegabilidad en teclado en landings.  
- Revisión Legal: claims, comparativas, testimonios, disclaimers y licencias de assets.

### 19. Gobernanza y seguridad de cuentas
- Accesos: RBAC por rol; MFA obligatorio; revisión trimestral de permisos.  
- Auditorías: Taxonomía/naming, conectores, conversiones, facturación.  
- Backups: Export de creatividades, audiencias y configuraciones críticas.  
- Incidentes: Runbook con contactos on‑call, criterios de severidad y tiempos de respuesta.

### 20. Especificaciones de dashboard y alertas
- Dashboard mínimo: gasto, impresiones, clics, CTR, CPC, conversiones, CVR, CPA, ROAS por canal/campaña/audiencia/creativo/landing.  
- Alertas:  
  - CPA > 1.3× objetivo 24h.  
  - CVR cae > 25% vs promedio 7 días.  
  - Gasto sin conversiones > umbral.  
  - Caída de tráfico de landing > 30% hora a hora.

### 21. Plantillas operativas
#### 21.1 Post‑mortem (resumen)
- Contexto | Objetivos | Resultados | Qué funcionó | Qué no funcionó | Causas raíz | Acciones y due dates | Impacto esperado.  

#### 21.2 Registro de riesgos (risk register)
- Riesgo | Probabilidad | Impacto | Señales tempranas | Mitigación | Responsable | Estado.

#### 21.3 Especificación de dashboard (brief)
- Fuentes | Métricas | Dimensiones | Segmentos | Frecuencia actualización | Propietario | URL.

### 22. Roles on‑call en lanzamiento (Día 7)
- Paid Media: 09:00–18:00.  
- Marketing Ops (tracking): 09:00–14:00.  
- Web/Dev (landings): 10:00–16:00.  
- Data Analyst: 12:00–17:00.  
- Escalación: Campaign Manager → Dir. Marketing.

---

Anexo Benchmarks: Ajustar por industria/país y actualizar trimestralmente.

### 23. OKRs por funnel y metas por canal
- Awareness (Q): Alcance único +% vs baseline; Share of Voice ≥ X%.  
- Consideration (M): CTR ≥ objetivo por canal; Engagement rate ≥ objetivo.  
- Conversion (M): CPA ≤ objetivo; CVR landing ≥ objetivo; ROAS ≥ objetivo.  
- Retention (Q): CAC payback ≤ N meses; LTV:CAC ≥ 3:1.  
- Por canal: definir objetivos específicos (ej.: Search ROAS ≥ 4×; LinkedIn CPL ≤ $X; Meta CAC ≤ $Y).  
Key Results se revisan semanalmente y se recalibran mensualmente.

### 24. Matriz de riesgo y severidad
- Severidad: S1 Crítico (operación detenida), S2 Alto, S3 Medio, S4 Bajo.  
- Probabilidad: P1 Muy alta – P4 Baja.  
- Priorización: Score = S × P.  
- Ejemplos:  
  - Tracking roto (S1,P2) → acción inmediata; kill‑switch si gasto activo.  
  - Rechazo masivo de anuncios (S2,P2) → plan creativo alternativo + contacto soporte.

### 25. Checklists QA detalladas
Pre‑Launch (Go/No‑Go):  
- Eventos reciben señales correctas con IDs y valores.  
- Landings: LCP < 2.5s, CLS < 0.1, formularios validan y guardan.  
- Creatividades cumplen guía de marca y políticas del canal.  
- UTMs consistentes; enlaces sin 404; responsive correcto.  
- Dashboards muestran métricas del día en tiempo real.  
Post‑Launch (24–48h):  
- Verificación CR por audiencia y creativo; outliers gestionados.  
- Conciliación de conversiones entre plataformas y GA/CRM.

### 26. Naming y versionado de assets
- Formato: canal_objetivo_audiencia_mensaje_formato_vXX (ej.: meta_conv_lookalike_valueprop_video_v03).  
- Cambios mayores: incrementar versión mayor (v1 → v2) al cambiar mensaje/visual base.  
- Repositorio con metadatos: fecha, owner, hipótesis asociada, resultados clave.

### 27. Taxonomía UTM (detallada)
- utm_source: meta | google | linkedin | tiktok | x.  
- utm_medium: paid | cpc | cpm.  
- utm_campaign: yyyy_mm_producto_objetivo (ej.: 2025_01_saas_demo_conv).  
- utm_content: audiencia_creativo_vXX (ej.: lla3_ugc_v02).  
- utm_term: keyword (solo Search).  
Ejemplo completo:  
https://dominio.com/?utm_source=google&utm_medium=cpc&utm_campaign=2025_01_saas_demo_conv&utm_content=brand_rsav1&utm_term=software+marketing

### 28. Atribución y reconciliación
- Modelo operativo: data‑driven (plataforma) para optimizar; modelo de verificación: last‑non‑direct en GA4; reconciliación mensual con CRM.  
- Triangulación: plataforma vs GA4 vs CRM; tolerancia de variación ±10–15%.  
- Experimentos de incrementabilidad: holdout/geosplit cuando el volumen lo permita.

### 29. Plantilla de informe final (resumen)
- Executive Summary | Objetivos vs resultados | Insights accionables | Contribución a pipeline/ingresos | What worked/What didn’t | Próximos pasos.  
- Anexos: detalle por canal, audiencias, creatividades, landings, cronología de optimizaciones.

### 30. Forecasting y control de varianza
- Forecast por canal con supuestos de CTR, CPC, CVR; sensibilidad ±10/20/30%.  
- Tracking diario de varianza vs plan; acciones si varianza > ±15% por 48h.  
- Reforecast quincenal con datos reales.

### 31. Gobernanza de cambios y escalaciones (CAB)
- Cambios mayores (budget > 30%, objetivo, naming): requieren aprobación CAB (Campaign Manager + Dir. Marketing + Finanzas).  
- Ventana de cambios: fuera de horas pico cuando sea posible.  
- Registro en log de cambios con motivo, impacto esperado y responsable.

### 32. Data dictionary (métricas clave)
- Clicks: clics válidos medidos por plataforma/GA4 (definir diferencias).  
- Conversion: evento objetivo con condiciones de calidad (form submit con lead válido).  
- CPA: gasto atribuible/conversiones válidas (excluir pruebas).  
- ROAS: ingresos netos atribuibles/gasto.  
- Notas: documentar filtros, ventanas de atribución y exclusiones.

### 33. SLAs por rol y calendario operativo
- Campaign Manager: decisiones de presupuesto ≤ 24h; post‑mortem ≤ 7 días.  
- Paid Media: ajustes diarios; respuesta a alertas críticas ≤ 2h hábiles.  
- Marketing Ops: tickets de tracking críticos ≤ 4h; no críticos ≤ 48h.  
- Creative: nuevas variantes ≤ 72h desde solicitud priorizada.  
- Data: dashboard listo Día 0; reportes diarios por canal 09:30.

### 34. Estructura de repositorio
- /campaigns/yyyy_mm_nombre/brief/  
- /campaigns/yyyy_mm_nombre/assets/creatives/  
- /campaigns/yyyy_mm_nombre/tracking/  
- /campaigns/yyyy_mm_nombre/reports/  
- /libraries/creatives_winners/  
- /libraries/utm_naming/

### 35. Framework y plantilla de presupuesto
- Estructura de budget: por objetivo (awareness/consideration/conversion), por canal y por fase (soft/full).  
- Regla de distribución inicial: 60% performance, 30% mid‑funnel, 10% upper (ajustar según etapa).  
- Plantilla mínima:  
  - Columnas: canal | objetivo | presupuesto total | daily cap | CPM/CPC esperado | CVR esperado | CPA/ROAS objetivo | notas.  
  - Pacing: % consumo planificado por día/semana; desvío permitido ±10%.

### 36. Playbook de incidentes y SLAs
- Severidades: S1 (crítico), S2 (alto), S3 (medio), S4 (bajo).  
- SLAs de respuesta: S1 ≤ 30 min; S2 ≤ 2 h; S3 ≤ 8 h; S4 ≤ 24 h hábiles.  
- Flujo: detección → contención (pausa/limit) → diagnóstico → remediación → validación → post‑incident note.  
- Ejemplos:  
  - Tracking caído (S1): pausar campañas de conversión, activar objetivos intermedios, abrir ticket con Ops.  
  - Sobregasto (S1/S2): activar kill‑switch o reducir budgets y pujas; alerta a Finanzas.

### 37. Matriz de cumplimiento por plataforma (resumen)
- Meta: políticas de contenido (salud, finanzas, afirmaciones), límite de texto en imagen ya no aplica pero evitar overload, verificación de dominio.  
- Google: políticas de anuncios (afirmaciones no verificables, marcas registradas), requisitos de destino (pop‑ups intrusivos, malware).  
- LinkedIn: B2B targeting sensible, claims con evidencia, transparencia en ofertas.  
- TikTok/X: creativos nativos, restricciones por edad/sector, disclosure de patrocinio cuando aplique.  
- Acción: checklist de compliance en pre‑launch y revisión legal para claims sensibles.

### 38. Guía de localización y multirregión
- Idioma: adaptar copy y creativos a variaciones regionales; evitar traducciones literales.  
- Moneda y formatos: precios locales, impuestos, fechas y numeración.  
- Legal: notas y disclaimers específicos por país/región.  
- Operativo: separar campañas por país/idioma cuando impuestos/leyes afecten reporting/optimización.

### 39. Accesibilidad (WCAG 2.2 AA)
- Contraste mínimo 4.5:1; tamaño de fuente legible; foco visible.  
- Subtítulos/captions en video; transcripts cuando aplique.  
- Alternativas de texto; orden lógico de navegación teclado.  
- Evitar contenido que parpadee; tiempos adecuados en formularios.  
- QA: checklist de a11y previo a lanzamiento de landings.

### 40. Gobernanza de datos y retención
- PII: minimizar captura; propósito específico; consentimiento explícito; almacenamiento cifrado.  
- Retención: leads no cualificados ≤ 12 meses; clientes según política legal/financiera.  
- DPIA: realizar para nuevas integraciones o cambios sustantivos de datos.  
- Acceso: RBAC y registros de acceso; revisión trimestral.

### 41. Gestión de proveedores y contratos
- Due diligence: seguridad, cumplimiento, SLAs, soporte.  
- Contratos: anexos de protección de datos (DPA), tiempos de soporte, penalizaciones.  
- Evaluación: scorecard trimestral de desempeño (uptime, tiempos de respuesta, calidad del soporte).

### 42. Capacitación y onboarding
- Plan por rol: Paid Media (plataformas, experimentación), Ops (tracking/GA4/GTM), Creativo (guidelines/políticas), Data (ETL/dashboards).  
- Onboarding: 30/60/90 con objetivos y checklists; certificaciones de plataformas cuando aplique.  
- Biblioteca: playbooks, videos cortos, ejemplos ganadores y anti‑patterns.

### 43. Auditorías periódicas (checklist)
- Cuentas: accesos, MFA, facturación, límites.  
- Taxonomía: naming consistente campañas/grupos/anuncios.  
- Tracking: eventos, conversiones, deduplicación, Consent Mode.  
- Creativo: rotación, saturación, frecuencia.  
- Datos: conciliación plataforma‑GA4‑CRM; documentación actualizada.

### 44. Ejemplos de dashboards
- Nivel ejecutivo: gasto, ROAS/CAC, ingresos atribuidos, contribución a pipeline.  
- Nivel táctico: CTR, CPC, CVR, CPA por canal/audiencia/creativo/landing; tendencias 7/28 días.  
- Alerting: tarjetas con umbrales y variaciones significativas; enlaces a detalles.

### 45. Plantilla de budget pacing (tabla)
- Día | Plan (€) | Real (€) | Varianza (%) | Acciones | Responsable.  
- Regla: si varianza acumulada > ±15% por 2 días, activar plan de corrección.

### 46. Brief de campaña (ejemplo completo)
Producto: SaaS Marketing Analytics  
Objetivo SMART: Generar 500 MQL en 60 días a CPL ≤ €65 con ROAS ≥ 3×.  
Audiencias:  
- ICP1: Directores de Marketing en SaaS 50–500 empleados (NA/EU).  
- ICP2: Performance Managers en eCommerce >€5M GMV.  
Oferta: Demo + prueba 14 días.  
Canales: Google Search (brand/non-brand), Meta, LinkedIn ABM.  
Budget: €120k (60% performance, 30% mid, 10% upper).  
KPIs: CTR, CVR, CPL≤65, MQL rate≥35%, SQL rate≥18%, ROAS≥3×.  
Riesgos: tracking (alto), rechazo creativos (medio).  
Aprobaciones: Dir. Marketing (OK), Legal claims (OK).

### 47. Plantilla de plan de test A/B
- Hipótesis: “UGC con prueba social aumentará CVR +15% vs creativo institucional”.  
- Métrica primaria: CVR a MQL.  
- Métricas secundarias: CTR, CPL.  
- Diseño: 50/50, n≥50 conversiones por variante o 7 días mínimo.  
- Criterio de ganador: uplift ≥ +10% con significancia práctica; CPA sostenible.  
- Próxima iteración: si gana UGC, testear hook 3 vs 5 segundos.

### 48. Script de QA de landing (paso a paso)
1) Carga inicial: LCP<2.5s, CLS<0.1 (mobile y desktop).  
2) Formularios: validaciones, mensajes de error, guardado en CRM.  
3) Accesibilidad: contraste, foco, navegación teclado, etiquetas ARIA.  
4) Tracking: eventos de view, click CTA, form start/submit con IDs únicos.  
5) Responsive: iOS/Android, 360px–1440px; pruebas cruzadas en BrowserStack.  
6) Contenido: copy, precios, legales, multilenguaje correcto.  
7) Seguridad: HTTPS, sin mixed content, headers básicos.

### 49. Automatizaciones (Make/Zapier) y triggers
- Trigger: nuevo lead en formulario → validar email → enriquecer (Clearbit/Alternativo) → crear/actualizar contacto en CRM → asignar owner → enviar email de confirmación → Slack alerta canal #leads.  
- Errores: reintentos con backoff; dead‑letter a planilla con alerta.  
- Logs: guardar payloads críticos; sanitizar PII al compartir.

### 50. Mapeo de campos CRM (ejemplo)
- first_name (texto, obligatorio)  
- last_name (texto)  
- email (único, validado)  
- company (texto)  
- role/title (lista controlada)  
- country (ISO‑2)  
- source (utm_source)  
- campaign (utm_campaign)  
- content (utm_content)  
- consent (boolean)  
- lead_status (nuevo, MQL, SQL, ganado, perdido)

### 51. Checklist de cumplimiento por país/región (ejemplo)
- UE (GDPR): base legal, DPA, consentimiento granular, derechos ARCO.  
- EE.UU.: CCPA/CPRA (si aplica), opt‑out venta de datos.  
- BR (LGPD): DPO designado, bases legales locales.  
- MX: aviso de privacidad local, transferencias internacionales.  
- Nota: actualizar con Legal por cambios regulatorios.

### 52. Base de aprendizajes (knowledge base)
- Esquema: fecha | hipótesis | canal | audiencia | creativo | resultado | decisión | enlace a reporte.  
- Taxonomía de etiquetas: objetivo, industria, formato, etapa del funnel.  
- Revisión mensual para consolidar librería de ganadores.

### 53. FAQ y troubleshooting
- “Cae el CVR de repente”: revisar velocidad landing, cambios en formularios, tracking duplicado.  
- “Gasto sin conversions”: kill‑switch, validar eventos, revisar geos/ubicaciones.  
- “CPL sube en LinkedIn”: afinar segmentación/ABM, oferta de valor, probar LGF.  
- “Rechazo de anuncios”: adaptar claims, formatos, contactar soporte de plataforma.

### 54. Glosario breve
- MVD: datos mínimos para decidir.  
- Holdout: grupo de control sin exposición.  
- Consent Mode: ajuste de medición con consentimiento.  
- Deduplicación: evitar conteo doble de conversiones multi‑fuente.

### 55. Guardrails estadísticos para experimentación
- Horizonte mínimo: 7 días por variante para cubrir estacionalidad intra‑semana.  
- Tamaño de muestra mínimo: 50 conversiones por variante o 3,000 clics (lo que ocurra primero).  
- Estabilidad: no decidir si hay cambios estructurales (tracking/landing) en las últimas 48h.  
- Uplift mínimo detectable (MDE): ≥ 10% para declarar ganador; si <10%, considerar empate operativo.  
- Falsos positivos: limitar a <10% usando ventanas fijas y evitando p‑hacking (no mirar cada hora para decidir).  
- Repetibilidad: re‑test si el resultado contradice benchmarks históricos.

### 56. Runbook de Go‑Live (por hora)
- T‑2h: Verificar checklist pre‑launch; confirmar on‑call; snapshots de configuraciones.  
- T‑1h: Habilitar dashboards y alertas; última prueba de eventos y UTMs.  
- T: Activar campañas (soft); registrar hora exacta.  
- T+1h: Revisar delivery, errores de tracking, enlaces rotos, gasto anómalo.  
- T+6h: Revisar CTR/CPC iniciales; pausar outliers extremos; documentar cambios.  
- T+24h: Revisión integral: CVR temprano, calidad de leads, pacing; plan de optimización Día 2.

### 57. Plan de rollback
- Criterios de activación:  
  - CPA > 2× objetivo y sin mejora en 24h.  
  - Tracking crítico roto sin solución < 2h.  
  - Incumplimiento legal/políticas (takedown).  
- Acciones: pausar campañas afectadas, revertir a configuración anterior (snapshot), redirigir budget a canales estables, notificar a stakeholders, abrir incidente.  
- Validación: smoke test post‑rollback; registrar incidente y lecciones.

### 58. Criterios de aceptación de campaña (Definition of Success)
- Técnico: 0 errores de tracking críticos; datos en dashboards en <5 min; landings con LCP<2.5s.  
- Operativo: naming/UTM correctos; accesos y permisos RBAC validados; on‑call asignado.  
- Negocio: KPIs del Día 1 dentro de ±25% del forecast; no hay bloqueadores de cumplimiento.  
- Aprobación: Campaign Manager y Dir. Marketing firman Go definitivo.

### 59. Plantillas de comunicación a stakeholders
- Pre‑launch (correo): objetivo, calendario, presupuesto, riesgos y plan de monitoreo (1 página).  
- Día 1 (resumen): gasto, CTR, CPC, conversiones tempranas, issues y acciones.  
- Semanal (executive): KPIs clave vs plan, decisiones, riesgos y próximos pasos.  
- Cierre (board): resultados vs objetivos, impacto en pipeline/ingresos, ROI/ROAS, aprendizajes y roadmap.

### 60. Controles de calidad de datos
- Validación de unicidad de emails/IDs; normalización de países (ISO‑2).  
- Reconciliación diaria plataforma↔GA4 y diaria/semanal GA4↔CRM con tolerancia ±10–15%.  
- Detección de outliers: reglas para valores extremos de CPC/CPA; exclusión de tráfico inválido (IVT) cuando aplique.  
- Registro de cambios: log con fecha, responsable, motivo e impacto esperado.

### 61. Esquema de eventos (GA4/API)
- page_view (automático)  
- view_item / view_promo (si aplica)  
- select_content (click CTA) {cta_id, variant}  
- begin_form (form_start) {form_id}  
- generate_lead (form_submit) {lead_id, value, currency, consent}  
- purchase (si aplica) {transaction_id, value, currency}  
- Campos comunes: session_id, client_id, user_id (si autenticado), utm_*  
- Notas: deduplicación server‑side/client‑side; timestamp y timezone consistentes.

### 62. Matriz RACI tabular (resumen)
- Brief: R Campaign Manager | A Dir. Marketing | C Ventas/Producto | I Finanzas.  
- Plan de medios: R Paid Media | A Dir. Marketing | C Finanzas | I Producto.  
- Creatividades: R Creative Lead | A Campaign Manager | C Brand/Legal | I Paid Media.  
- Tracking: R Marketing Ops | A Campaign Manager | C Data Analyst | I Paid Media.  
- Lanzamiento: R Paid Media | A Campaign Manager | C Data Analyst | I Soporte.  
- Reporte final: R Data Analyst | A Campaign Manager | C Dir. Marketing | I Finanzas/Ventas.

### 63. Tabla de SLAs (resumen)
- Incidente S1: respuesta ≤ 30 min; mitigación ≤ 2 h.  
- Incidente S2: respuesta ≤ 2 h; mitigación ≤ 8 h.  
- Tickets tracking críticos: ≤ 4 h; no críticos: ≤ 48 h.  
- Nuevas creatividades: ≤ 72 h desde solicitud priorizada.  
- Reporte diario: 09:30; post‑mortem: ≤ 7 días.

### 64. Medición avanzada: MTA y MMM
- Multi‑Touch Attribution (MTA): usar data‑driven de plataforma para optimizar táctico; validar con GA4 y CRM.  
- Marketing Mix Modeling (MMM): análisis trimestral con datos agregados (gasto, impresiones, clicks, conversiones, estacionalidad, promos, pricing) para elasticidades y saturación.  
- Triangulación: decisiones tácticas con MTA; decisiones de presupuesto macro con MMM y experimentos.  
- Requisitos MMM: 18–24 meses de datos preferente; control de outliers; variables de control (competencia, macro).  
- Entregables: curvas de respuesta por canal y recomendación de inversión óptima.

### 65. Conversiones Server‑Side (SSC)
- Arquitectura: navegador → GTM/SDK → API (Cloud Function/Edge) → colas (ej. Pub/Sub) → conectores (Meta CAPI, Google Enhanced Conversions, LinkedIn).  
- Seguridad: firma de eventos, rate‑limit, secretos gestionados (KMS), PII hash (SHA‑256) antes del envío.  
- Fiabilidad: reintentos con backoff, DLQ, observabilidad (logs y métricas).  
- Campos mínimos: event_name, event_time (UTC), event_id, value, currency, client_id/user_id, consent.  
- Deduplicación: event_id consistente entre client‑side/server‑side.

### 66. Brand Safety e IVT/Fraude
- Exclusiones: categorías sensibles, placements y sitios excluidos (listas actualizadas).  
- Verificación: integrar herramientas de verificación (si aplica); monitorear IVT.  
- Reglas: pausar ubicaciones con CTR anómalamente alto y CVR nulo; frecuencias máximas.  
- UGC: revisión de derechos y licencias; almacenamiento de consentimientos.

### 67. Política de asignación de costos y conciliación financiera
- Asignación: por canal, campaña y objetivo; prorrateo de herramientas (ej. 70% marketing, 30% ventas si aplica).  
- Conciliación: gasto plataforma vs facturas vs ERP mensual; tolerancia de variación ≤ 2%.  
- MER (Marketing Efficiency Ratio): Ingresos totales / Gasto total; usar junto a ROAS por canal.  
- Calendario: cierre contable D+5; reporte financiero de performance D+7.

### 68. Geo‑experimentos e incrementabilidad
- Métodos: geo‑split, time‑based holdout, switchback en regiones comparables.  
- Diseño: seleccionar regiones gemelas (población, ingresos, historial); tamaño efecto esperado; duración mínima 2–4 semanas.  
- Métrica: lift incremental en conversiones o revenue; cálculo de confianza y tamaño de efecto.  
- Evitar contaminación: limitar overlap de canales o calibrar con MMM.

### 69. CMP, consentimiento y retención
- CMP: implementar banner con granularidad y logs de consent; soporte TCF donde aplique.  
- Retención: definir TTL por tipo de dato (PII, eventos); anonimización/pseudonimización.  
- DSAR: proceso documentado para export/borrado; SLA legal.  
- Señales: respetar consent flags en client‑side y server‑side.

### 70. Rúbrica creativa por formato
- Video: hook <3s, subtítulos, branding ligero, CTA claro; test de 3 ángulos (dolor, beneficio, prueba social).  
- Estático: jerarquía visual, contraste, 20–30% texto, beneficio tangible.  
- Copy: 1 idea por anuncio, claridad > creatividad; prueba A/B de lead con y sin fricción.  
- Revisión: check de marca, políticas, accesibilidad y consistencia UTM.

### 71. ABM y alineación con Ventas
- Listas de cuentas: CRM → plataforma (uploader/partner); refresco semanal.  
- Mensajería: assets por etapa (awareness→demo→caso de éxito); secuencias de seguimiento coordinadas.  
- Handoff: MQL→SQL con criterios claros; SLA de contacto ≤ 24h; feedback loop de calidad.  
- Reporte: pipeline influenciado y ganado por cuenta; deal velocity.

### 72. Plan de Continuidad de Negocio (BCP) y DR
- Riesgos críticos: caída de landings, suspensión de cuentas, fallo de tracking.  
- DR: entornos espejo para landings, duplicados de campañas en cuentas secundarias, backups de configuraciones.  
- Pruebas: ejercicios semestrales de conmutación; checklist de recuperación.  
- Comunicación: canales alternos y responsables definidos.

### 73. Checklists operativos por canal (resumen accionable)
- Meta:  
  - Conversions API activo; Advantage+ audit; exclusiones de audiencia y brand safety; formatos 1:1/4:5/9:16; frecuencia ≤ meta.  
  - Reglas: pausar CPA>1.5×; escalar ganadores +20–30%/48h.
- Google:  
  - RSA con assets suficientes; extensiones completas; negativas vivas; EC/Tag configurado; LP speed OK.  
  - YouTube: hook <5s, VTR objetivo; segmentación por audiencia/tema.
- LinkedIn:  
  - LGF con campos mínimos; ABM listas; CPL objetivo; exclusión empleados.  
  - Document Ads cuando toque; seguimiento de MQL/SQL en CRM.
- TikTok/X:  
  - Creativo nativo; múltiples variantes; learning estable; límites de edición.  
  - Safety: ubicaciones/temas excluidos si aplica.

### 74. Convenciones de estructura y naming por plataforma
- Meta: campaign_objective|geo|aud|offer|yyyy_mm; adset_audience|placement|opt; ad_creative|format|vXX.  
- Google Search: brand|nonbrand|geo|match; adgroup_theme; rsa_vXX.  
- LinkedIn: obj|abm|industry|geo; ad_group_offer; ad_format_vXX.  
- TikTok/X: obj|geo|aud|format; adset_targeting; ad_hook_vXX.  
- Regla: máximo 64 caracteres cuando plataforma limite; evitar caracteres especiales.

### 75. Benchmarks referenciales por vertical (ajustar con datos propios)
- SaaS B2B: CTR Search 3–6%, CVR 2–6%, CPL LinkedIn $120–300, ROAS search ≥ 3–5×.  
- E‑commerce: CTR Social 1–2%, CVR 1.5–3.5%, ROAS social ≥ 2–4×, CAC según AOV.  
- Educación: CPL Meta $8–30, CVR lead→matrícula 3–10%.  
- Servicios: CPL $20–100; LTV:CAC ≥ 3:1.  
- Nota: mantener tabla viva por país/canal.

### 76. Pipeline de datos (ETL/BI) para reporting
- Ingesta: APIs plataformas → almacenamiento (DW) con jobs diarios/horarios; logs de ingestión.  
- Transformación: normalización de dimensiones (fecha, canal, campaña, audiencia, creativo, landing), llaves consistentes, mapping UTM.  
- Métricas: gasto, impresiones, clics, CTR, CPC, conv, CVR, CPA, revenue, ROAS, MER.  
- Orquestación: scheduler (ej. Airflow/Prefect/Make) con alertas de fallo; reintentos.  
- Serving: vistas materializadas para dashboards; control de versiones de modelos.

### 77. Baseline de configuración GA4
- Propiedad y flujos web/app definidos; zonas horarias/moneda correctas.  
- Eventos recomendados + personalizados; conversiones marcadas; Enhanced Measurement.  
- Filtros internos/bot; exclusión de referencias propias; dominios cruzados.  
- Audiencias para remarketing; BigQuery export habilitado; retención adecuada.  
- Vinculaciones: Ads, Search Console, BigQuery, Consent Mode.

### 78. Procedimiento de filtrado de bots/IVT
- Activar detección de bots (plataformas/GA4); listas de IP y user‑agents; honeypots en formularios.  
- Validación de correo/empresa; throttling en endpoints; score de calidad de lead.  
- Revisiones semanales de anomalías (CTR alto/CVR nulo); exclusión de fuentes.

### 79. Checklist legal de claims y evidencias
- Claims cuantitativos con fuentes verificables; disclaimers visibles.  
- Uso de marcas/terceros autorizado; derechos de imagen/voz/UGC documentados.  
- Conservación de evidencias (repositorio legal) y fechas de vigencia.

### 80. Gobierno del repositorio de experimentos
- Estructura: /experiments/yyyy_mm_id/ con brief, diseño, datos, resultados, decisión.  
- Versionado: etiquetas semánticas; owner y aprobador; estado (draft, running, closed).  
- Revisión mensual: top wins/losses y roadmap de pruebas.

### 81. Política de costos por ventana de atribución
- Reporte táctico: ventana 7‑day click/1‑day view (según plataforma).  
- Reporte financiero: 28‑day/30‑day para conciliación; documentar diferencias.  
- Decisiones: optimización con ventana corta; presupuesto con ventana extendida/MMM.

### 82. Knowledge Transfer (KT) y archivado
- KT al cierre: deck de insights, repositorio de assets ganadores, librería de audiencias/UTM.  
- Archivado: congelar campañas, exportes de configuración, snapshot de dashboards.  
- Checklist de traspaso para nuevos owners.

### 83. Matriz de QA de localización y accesibilidad
- Idioma (gramática/términos locales), moneda, formatos de fecha; lectura derecha‑a‑izquierda si aplica.  
- A11y: contraste, captions, foco, navegación teclado, etiquetas alt/ARIA.  
- Validación por nativos/local reviewers cuando sea crítico.

### 84. Seguridad y gestión de secretos
- Secretos en vault/KMS; no en repositorios ni variables públicas.  
- Accesos mínimos necesarios (least privilege); rotación periódica.  
- Registros de acceso; auditoría trimestral.

### 85. Plantilla de registro de riesgos (tabla)
| ID | Riesgo | Severidad | Probabilidad | Score | Señales tempranas | Mitigación | Responsable | Estado |
|---|---|---|---|---|---|---|---|---|
| R‑001 | Tracking roto | S1 | P2 | 2 | Caída de conversiones | Kill‑switch + rollback | Mkt Ops | Abierto |
| R‑002 | Rechazo masivo | S2 | P2 | 4 | Tasa de rechazo >20% | Creativo alterno + soporte | Creative | Mitigado |

### 86. Matriz de competencias por rol
- Campaign Manager: estrategia, budget, experimentación, liderazgo.  
- Paid Media Specialist: plataformas, bidding, estructura, automatizaciones.  
- Marketing Ops: GTM/GA4, CAPI/SSC, integraciones, QA.  
- Data Analyst: SQL/BI, atribución, MMM básico, dashboarding.  
- Creative Lead: concepto, guías por formato, accesibilidad, compliance.  
Escala: 1 básico — 5 experto; usar para capacitación 30/60/90.

### 87. Árbol OKR (ejemplo)
- O: Acelerar crecimiento rentable.  
  - KR1: ROAS total ≥ 3.5× Q.  
  - KR2: CAC payback ≤ 6 meses.  
  - KR3: +25% MQL calificados QoQ.  
- O (Marketing): Escalar performance manteniendo calidad.  
  - KR: CPA ≤ objetivo por canal; CVR landing ≥ +15%.  
  - KRs por canal: Search ROAS≥4×, LinkedIn CPL≤$X, Meta CAC≤$Y.

### 88. Guía ESG y sectores sensibles
- Evitar claims engañosos (greenwashing); requerir evidencia.  
- Sectores regulados (salud, finanzas): revisión legal previa y disclaimers.  
- Inclusión y no discriminación en segmentación y creatividades.  
- Registro de aprobaciones y materiales soporte.

### 89. Tabla de retención y clasificación de datos
| Tipo de dato | Clasificación | Retención | Base legal | Sistema |
|---|---|---|---|---|
| Leads no cualificados | PII | ≤ 12 meses | Consent/Legit Interest | CRM |
| Clientes | PII/Financiero | Según ley fiscal | Contract/Legal | ERP/CRM |
| Eventos anónimos | No PII | 26 meses | Legit Interest | Analytics |

### 90. Ejemplos de localización por país
- MX: moneda MXN, IVA aplicable, uso de “cotización”/“factura” en copy.  
- BR: moneda BRL, portugués BR, LGPD; formato fecha dd/mm/aaaa.  
- ES: español UE, RGPD, precios con IVA incluido.  
- US: USD, CCPA/CPRA, inglés; políticas por estado si aplica.

### 91. Ejemplos de consultas BI (pseudo‑SQL)
KPI diario por canal:
```
SELECT date, channel,
  SUM(spend) AS spend,
  SUM(clicks) AS clicks,
  SAFE_DIVIDE(SUM(clicks), NULLIF(SUM(impressions),0)) AS ctr,
  SAFE_DIVIDE(SUM(spend), NULLIF(SUM(clicks),0)) AS cpc,
  SUM(conversions) AS conv,
  SAFE_DIVIDE(SUM(conversions), NULLIF(SUM(clicks),0)) AS cvr,
  SAFE_DIVIDE(SUM(spend), NULLIF(SUM(conversions),0)) AS cpa
FROM fact_marketing
GROUP BY 1,2
ORDER BY 1 DESC;
```

### 92. Bosquejo de contenedor GTM (nombres/eventos)
- Tags: ga4_config, ga4_event_generate_lead, meta_capi_event, linkedin_event.  
- Triggers: form_submit, click_cta, view_item, timer_30s, scroll_75.  
- Variables: client_id, user_id, consent_flags, utm_source/medium/campaign/content/term.  
- Naming: ga4_event_{evento}, capi_{plataforma}_{evento}.

### 93. Plantilla de reporte ejecutivo (1‑pager)
- Objetivo y alcance (2–3 líneas).  
- KPIs clave vs plan: gasto, CPA/CAC, ROAS/MER, MQL/SQL, revenue.  
- 3 insights accionables y 3 decisiones tomadas.  
- Riesgos abiertos y mitigaciones.  
- Próximos pasos y responsables (con fechas).  
- Enlaces: dashboard, brief, changelog.

### 94. KPI ladder y health metrics por funnel
- Awareness: Reach único, SoV, CPM, VTR (video).  
- Consideration: CTR, tiempo en página, engagement rate.  
- Conversion: CVR, CPA, AOV/Revenue, ROAS.  
- Retention: LTV, churn, payback, LTV:CAC.  
- Salud operativa: tracking error rate, latencia de datos, pacing variance, frecuencia.

### 95. Playbook ante incumplimiento de SLAs
- Detectar: alerta automática + responsable on‑call.  
- Contener: pausar/limitar impacto; comunicar a stakeholders.  
- Corregir: propietario ejecuta solución; tiempo objetivo por severidad.  
- Validar: smoke tests y confirmación en dashboard.  
- Cerrar: post‑incident con causa raíz y acciones preventivas.

### 96. Plantilla de change log de campaña
- Fecha | Cambio | Motivo | Impacto esperado | Responsable | Aprobación | Resultado real | Enlace.  
- Reglas: cambios mayores requieren CAB; registrar antes y después.

### 97. Gobierno de tags de terceros
- Inventario de tags y finalidad; owner y expiración.  
- Reglas de carga (consent, performance budgets).  
- Auditoría mensual: tags huérfanos, bloqueados, tiempos de carga.  
- Seguridad: dominios permitidos, integrity/SRI cuando aplique.

### 98. Esquema DPIA (Data Protection Impact Assessment)
- Descripción del procesamiento y propósito.  
- Evaluación de necesidad y proporcionalidad.  
- Identificación de riesgos a derechos y libertades.  
- Medidas de mitigación y plan de seguimiento.  
- Aprobaciones (Legal/DPO) y revisión periódica.

### 99. Proceso de deprecación/EOL de campañas y assets
- Criterios de EOL: obsolescencia creativa, cambios de producto/mercado, bajo performance persistente.  
- Pasos: anunciar EOL → congelar → archivar → documentar aprendizajes → retirar tags/dependencias.  
- Retención: conservar reportes y assets ganadores en librería.

### 100. Agenda semanal operativa (estándar)
- Lunes: revisión performance y varianzas, reasignación de budget.  
- Miércoles: comité de experimentación, decisiones A/B y backlog.  
- Viernes: reporte ejecutivo, riesgos abiertos, plan de la semana siguiente.  
- Ad‑hoc: incidentes, cambios aprobados por CAB.

### 101. Scorecard de readiness (previo a lanzamiento)
- Tracking: 0 errores críticos; eventos clave reciben datos; GTM/GTM‑SS OK.  
- Landings: LCP<2.5s, CLS<0.1; formularios OK; a11y básica.  
- Creativos: guías de marca, políticas aprobadas, variantes listas.  
- Pacing/Presupuesto: topes configurados; alertas a 80/100%.  
- Dashboards/Alertas: operativos en tiempo real; owners asignados.  
- Cumplimiento: consentimiento activo; disclaimers; exclusiones sensibles.

### 102. Rúbrica de autoauditoría (0–2 por ítem)
- Estructura de campañas (consolidación adecuada).  
- Señales de calidad (conversiones de valor).  
- Experimentación (hipótesis claras, MVD alcanzado).  
- Creativo (rotación, formatos, claridad de oferta).  
- Datos (consistencia plataforma↔GA4↔CRM).  
- Gobernanza (naming, accesos, changelog).  
Puntaje: 0 bajo, 1 medio, 2 excelente; plan de mejora si < 9/12.

### 103. Estrategia cookieless y modelado
- Consent Mode y server‑side para maximizar señal.  
- Modelado de conversión: completar huecos con modelos de probabilidad.  
- Medición incremental (geo/holdout) para validar inversión.  
- Contextual/first‑party data: fortalecer audiencias propias.

### 104. Guía ética de publicidad
- Transparencia: evitar claims engañosos; claridad de precios/condiciones.  
- Sensibilidad: evitar estereotipos; respeto cultural/local.  
- Protección de menores y grupos vulnerables.  
- Proceso de revisión ética para campañas sensibles.

### 105. Política de uso de IA generativa
- Uso permitido: brainstorming, variantes de copy/visual, escalado de creatividades.  
- Revisión humana obligatoria; verificación factual y de derechos.  
- Marcas de agua/metadatos cuando aplique; registro de prompts/resultados significativos.  
- Restricciones: no generar testimonios falsos ni suplantación.

### 106. SLI/SLO de datos
- SLI: latencia de ingestión (p95), frescura de datos, tasa de error de tracking, reconciliación plataforma↔GA4.  
- SLO: p95 latencia < 5 min; error tracking < 1%; reconciliación dentro de ±10–15%.  
- Alertas y rotación a modo degradado si SLOs se incumplen.

### 107. Quick‑Start (Checklist de activación rápida)
- Brief validado y objetivos SMART.  
- Plan de medios + matriz de tests listos.  
- Creatividades aprobadas y variantes cargadas.  
- Landings QA: performance, formularios, accesibilidad.  
- Tracking y UTMs verificados (client + server‑side).  
- Dashboards/alertas operativas.  
- On‑call definido y playbook de incidentes a mano.  
- Go/No‑Go firmado.

### 108. Kit mínimo de campaña (entregables)
- 1 brief + 1 plan de medios + 1 matriz de hipótesis.  
- ≥2 variantes creativas por audiencia/formato.  
- 1 landing con QA completo.  
- GTM + CAPI/SSC configurado.  
- Dashboard básico y plantilla de reporte ejecutivo.

### 109. Versionado y gobierno del documento
- Versionado semántico (Mayor.Menor.Parche).  
- Cambios mayores requieren CAB y actualización del índice maestro.  
- Changelog al final del documento con fecha, autor y resumen.

### 110. Referencias cruzadas (archivo maestro)
- Índice maestro: `00_INDICE_DMS_COMPLETOS.md`.  
- Operaciones: `04_Operations/OPERACIONES_PROCESOS.md`.  
- Marketing: `01_Marketing/07_Campaign_Management/README.md` y `campaign_launch_checklist.md`.  
- Data/BI: `16_Data_Analytics/` (modelos y dashboards).  
- Legal/Compliance: `13_Legal_Compliance/`.
 
### 110.1 Plantillas relacionadas
- Brief: `04_Operations/templates/brief_campana_template.md`  
- Plan de medios: `04_Operations/templates/plan_medios_template.md`  
- Plan A/B: `04_Operations/templates/test_ab_template.md`  
- Pre‑lanzamiento: `04_Operations/templates/checklist_prelanzamiento.md`  
- 1‑Pager ejecutivo: `04_Operations/templates/reporte_ejecutivo_1pager.md`  
- Risk Register: `04_Operations/templates/risk_register_template.csv`  
- English templates: `04_Operations/templates/en/`
 - Dashboard spec: `04_Operations/templates/dashboard_spec.md`  
 - Data dictionary: `04_Operations/templates/data_dictionary.csv`  
 - GA4 event schema: `04_Operations/templates/ga4_event_schema.csv`
  - Calculadoras:  
    - Budget/Pacing: `04_Operations/templates/budget_pacing_calculator.csv`  
    - ROI/ROAS: `04_Operations/templates/roi_roas_calculator.csv`
  - Capacity planning:  
    - Paid Media: `04_Operations/templates/capacity_planning_paid_media.csv`  
    - Creativo: `04_Operations/templates/capacity_planning_creativo.csv`  
    - Ops/Tracking/Data: `04_Operations/templates/capacity_planning_ops.csv`
  - One‑pager checklist: `04_Operations/templates/onepager_checklist_campanas.md`
  - Go/No‑Go: `04_Operations/templates/go_nogo_campanas.md`
 - Dashboard blueprints:  
   - Ejecutivo: `04_Operations/templates/dashboard_blueprint_executive.md`  
   - Táctico: `04_Operations/templates/dashboard_blueprint_tactical.md`  
   - Canal: `04_Operations/templates/dashboard_blueprint_channel.md`
  - Dashboard starters:  
    - Looker Studio: `04_Operations/templates/dashboard_starter_looker_studio.md`  
    - Looker (LookML): `04_Operations/templates/dashboard_starter_looker.md`

### 55. Guardrails estadísticos para experimentación
- Mínimos de lectura: n≥3,000 impresiones por anuncio o ≥50 clics por variante antes de decidir.  
- Horizonte temporal: 5–7 días mínimo para evitar sesgos de día/semana.  
- Estabilidad: no introducir cambios simultáneos en oferta/landing al testear creativo.  
- Uplift mínimo accionable: ≥ +10% en métrica primaria con coste sostenible.  
- Paradas: detener variante si CPA > 1.5× objetivo con n≥30 clics y tendencia negativa 48h.

### 56. Runbook de go‑live (día de lanzamiento)
T‑24h: QA final de tracking y landings; verificación de budgets/limits; on‑call confirmado.  
T‑2h: carga final de creatividades; revisión de targeting y exclusiones; activar dashboards.  
T0: activar campañas (soft 10–20% budget).  
T+1h: chequear impresiones, CTR, errores, eventos; corregir enlaces/UTM si aplica.  
T+6h: revisar CVR inicial, pacing, frecuencia; pausar outliers.  
T+24h: primer informe corto a stakeholders con hallazgos y acciones.

### 57. Plan de rollback
- Condiciones: tracking roto, sobregasto > 30% plan, CVR < 50% del baseline, caída de landing.  
- Acciones: pausar campañas afectadas, revertir a creativos/segmentos estables, limitar budgets, activar página alternativa.  
- Comunicación: notificar a Dir. Marketing y Finanzas; registrar incidente y resolución.

### 58. Criterios de éxito y aceptación
- Éxito operativo: checklist QA completo, sin incidentes críticos, dashboards en tiempo real.  
- Éxito de performance: alcanzar ≥ 80–100% de KPIs objetivo a día 7 y ≥ 100% a día 30 (o explicar desviaciones y plan).  
- Aceptación formal: acta de aceptación por Campaign Manager y Dir. Marketing.

### 59. Comunicación a stakeholders (plantillas)
- Lanzamiento: objetivos, presupuesto, canales, riesgos, on‑call, enlaces a dashboards.  
- Daily: highlights KPIs, acciones tomadas, riesgos/mitigaciones, próximos pasos.  
- Cierre: resultados vs objetivos, aprendizajes, decisiones para la siguiente iteración.

### 60. Controles de calidad de datos
- Validaciones: dominios de email, duplicados, normalización de país/moneda.  
- Reconciliación diaria: plataforma↔GA4↔CRM (tolerancia ±10–15%).  
- Alertas: anomalías de datos (spikes/drops), eventos duplicados, discrepancias > 20%.  
- Logs: auditoría de cambios en conversiones/eventos.

### 61. Esquema de eventos (GA4/API ejemplo)
- view_page: {page_location, page_referrer, language}.  
- click_cta: {cta_id, cta_text, placement}.  
- form_start: {form_id, step}.  
- form_submit: {form_id, lead_id, valid:true/false}.  
- conversion: {conversion_id, value, currency, source, campaign, content}.  
Notas: nombrar consistentemente; incluir user_id cuando exista; respetar PII.

### 62. Matriz RACI (tabla compacta)
Actividad | R | A | C | I  
Brief de campaña | Campaign Manager | Dir. Marketing | Ventas/Producto | Finanzas  
Plan de medios | Paid Media | Dir. Marketing | Finanzas | Producto  
Creatividades | Creative Lead | Campaign Manager | Brand/Legal | Paid Media  
Tracking/Medición | Marketing Ops | Campaign Manager | Data Analyst | Paid Media  
Lanzamiento/Monitoreo | Paid Media | Campaign Manager | Data Analyst | Soporte  
Reporte/Cierre | Data Analyst | Campaign Manager | Dir. Marketing | Finanzas/Ventas

### 63. Tabla de SLAs (severidad/rol)
Severidad | Respuesta | Contención | Resolución | Owner  
S1 Crítico | ≤ 30 min | ≤ 1 h | ≤ 8 h | Campaign Manager + Ops  
S2 Alto | ≤ 2 h | ≤ 4 h | ≤ 24 h | Paid Media/Ops  
S3 Medio | ≤ 8 h | ≤ 24 h | ≤ 3 d | Paid Media/Data  
S4 Bajo | ≤ 24 h | ≤ 3 d | ≤ 7 d | Equipo asignado


