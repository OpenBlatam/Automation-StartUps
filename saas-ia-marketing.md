# SaaS de IA aplicado al Marketing — Automatizaciones accionables

Versión: v1.0.3  ·  Última actualización: 2025-10-30

## Tabla de contenido
- Resumen ejecutivo
- Prioridades Top
- OKRs, DoD
- Automatizaciones clave y extra
- Recetas y Snippets
- Esquemas, Métricas y Checklists
- Anexos (prompts, Kanban, costos, seguridad)
- Operación (SOP, RACI, UAT, Rollback, KPIs)
- SLAs, Riesgos, Pre‑prod, Despliegue
- Retención, Idempotencia, Rate limit, QA, ROI

## Resumen ejecutivo
- Objetivo: aumentar recuperación de pagos, priorizar leads y deflectar soporte L1.
- Resultado esperado (90 días): +20% recovery, −25% T1ª respuesta, FCR IA ≥ 40%.
- Alcance: dunning+suspensión, enriquecimiento+scoring, reportes, soporte IA.

## Prioridades Top (Impacto/Escenario/Esfuerzo)
- Dunning + suspensión/reactivación con Stripe — Alto / 14 días / Medio
- Enriquecimiento de leads + scoring — Medio‑alto / 7 días / Bajo
- Soporte L1 con IA y fallback a agente — Alto / 30 días / Medio

## OKRs Trimestrales
- O1: +20% recuperación de pagos fallidos
- O2: -25% tiempo de primera respuesta en soporte
- O3: 8 automatizaciones activas con DoD cumplido

## Definición de Listo (DoD)
- Casos: 1 feliz, 2 errores, 1 edge (duplicados/limites)
- Observabilidad: logs con usuario, evento, resultado, costo
- Métricas conectadas a dashboard (Looker/Data Studio)
- Runbook y propietario asignado
- PII enmascarada; llaves/API con rotación

---

## 10 Automatizaciones Clave (mini‑blueprints + KPI)

1) Dunning + suspensión/reactivación
- Stack: Stripe, Customer.io/HubSpot, Webhooks backend
- Flujo: Charge failed → secuencia reintentos → si ≥N → /suspend → pago ok → /reactivate
- KPI: recovery rate, churn involuntario
- Ahorro/mes: 3–5 h

2) Enriquecimiento de leads + lead score
- Stack: Clay/Clearbit, Zapier, CRM
- Flujo: New lead → enrich → score → asignación SDR
- KPI: MQL→SQL, tiempo a contacto
- Ahorro/mes: 4–6 h

3) Soporte L1 con IA (FAQ/How‑to)
- Stack: Zendesk/Intercom, OpenAI, KB
- Flujo: Intent → respuesta IA; baja confianza → agente
- KPI: FCR, tiempo respuesta
- Ahorro/mes: 10–20 h

4) Reportes de rendimiento mensuales a clientes
- Stack: GA4, GSC, Ads APIs, Apps Script, Looker Studio
- Flujo: ETL → PDF/Link → envío automatizado
- KPI: aperturas, renovaciones
- Ahorro/mes: 6–10 h

5) Intent signals → MQL
- Stack: Webhooks pricing/FAQ, OpenAI scoring, CRM
- Flujo: Señal → score → oportunidad si > umbral
- KPI: velocidad MQL, conversión
- Ahorro/mes: 2–3 h

6) Calendario SEO automatizado
- Stack: Sheets, Apps Script/Cloud Run, CMS
- Flujo: Cron → generar briefs/copy → publicar
- KPI: clicks orgánicos, páginas indexadas
- Ahorro/mes: 8–12 h

7) Changelog y release notes con IA
- Stack: GitHub PRs/commits, OpenAI, Email/Blog
- Flujo: Nuevo release → resumen por audiencia → publicar
- KPI: adopción features, CTR changelog
- Ahorro/mes: 3–5 h

8) Health score de cuentas + alertas
- Stack: Product events, NPS, tickets, Slack
- Flujo: Score compuesto → umbral → playbook
- KPI: retención, riesgo anticipado
- Ahorro/mes: 1–2 h/sem

9) Higiene de base (bounces/duplicados)
- Stack: Kickbox/ZeroBounce, Zapier, CRM
- Flujo: Bounces → marcar inválidos; merge duplicados; normalizar
- KPI: deliverability, calidad datos
- Ahorro/mes: 2–4 h

10) ABM light por IP
- Stack: IP reveal, Email, CMS banners
- Flujo: Empresa detectada → banner/email 1:1
- KPI: demo rate, engaged accounts
- Ahorro/mes: 2 h/sem

---

## 10 Ideas Extra (rápidas)
- Detector PQL por eventos in‑product
- Paywall dinámico según patrón de uso
- Conversión de trial asistida por bot IA
- Lead recycling a los 14 días sin contacto
- Cobertura de palabras clave → briefs automáticos
- Score de salud de cuentas (uso+NPS+tickets)
- Automatizaciones de PR/pitches por periodista
- ABM por IP con personalización ligera
- Content‑refresh programado por caída de tráfico
- SSO/seguridad self‑serve para reducir tickets

---

## Recetas Zapier Plug‑and‑Play
- Stripe (Charge Failed) → Customer.io (Serie dunning) → Delay/Retry → Filter (retries ≥3) → Webhook backend (/suspend)
- Stripe (Invoice Payment Succeeded) → Webhook backend (/reactivate) → Email “Welcome back”
- New Lead in HubSpot → Clay (Enrich) → Update Lead Score → Assign Owner
- GitHub (Release) → OpenAI (Generar notas por audiencia) → Gmail (clientes) + CMS (blog)

---

## Snippets de Apps Script

Reporte mensual a clientes (GA4 + GSC + Ads a PDF):

```javascript
function reporteMensualClientes() {
  // Pseudocódigo: extrae métricas, arma PDF y envía
  const clientes = SpreadsheetApp.getActive().getSheetByName('Clientes').getDataRange().getValues().slice(1);
  clientes.forEach(c => {
    const [email, dominio, idGa4] = c;
    const kpis = obtenerKPIs(idGa4, dominio); // implementa
    const pdf = renderizarPDF(kpis); // implementa con HTMLService
    GmailApp.sendEmail(email, 'Reporte mensual', 'Adjunto reporte.', {attachments: [pdf]});
  });
}
```

---

## Esquemas de Sheets
- Clientes: Email | Dominio | ID_GA4 | Plan | CSM
- Dunning: Cliente | Intentos | ÚltimoEvento | Estado
- Leads: Email | Empresa | Cargo | Fuente | Score | Owner

## Plantillas e IDs requeridos
- Stripe: endpoints webhooks (events: charge.failed, invoice.payment_succeeded)
- Customer.io/HubSpot: series dunning y plantillas email
- CRM: campos score/owner; reglas de asignación
- GitHub/CMS: acceso a releases/blog

---

## Métricas y Fórmulas
- Recovery dunning: =PagosRecuperados/IntentosFallidos
- FCR soporte IA: =ResueltosIA/TotalTickets
- AHA time: tiempo a primer valor (min)

---

## Checklist por automatización
- Setup: credenciales (Stripe, CRM, Customer.io), IDs, permisos
- Pruebas: cobro fallido simulado, duplicados, límites
- Métricas: fuente, fórmula, objetivo
- Operación: runbook dunning, propietario
- Riesgos: falsas suspensiones, PII, límites API

---

## Anexos prácticos

### Prompts por industria (ejemplos)
- B2B SaaS: "Escribe release notes para {feature} en 3 versiones: ejecutiva, técnica y usuario final, con 1 CTA cada una."
- E‑commerce: "Genera brief de campaña para {producto}, audiencias {segmentos}, objetivo ROAS {meta}, 5 ángulos creativos."
- Servicios profesionales: "Crea secuencia de onboarding de 5 emails enfocada en 'time to value' con métricas y tutoriales."

### Checklist Kanban
- Backlog: impacto estimado, esfuerzo, dependencias
- Ready: KPIs definidos, entornos y sandbox listos
- Doing: logs+costo por evento, alertas Slack
- Review: QA de datos (duplicados, bounces), pruebas de dunning
- Done: dashboard, runbook, propietario on‑call

### Plantilla de costos y márgenes (Sheets)
- Columnas: Cliente | Plan | Tokens | CostoUSD | IngresoUSD | MargenUSD
- Fórmulas: margen = ingreso − costo; margen% = margen/ingreso

### Seguridad mínima
- Separar claves prod/staging; rotación y scopes mínimos
- Enmascarar PII en logs; cumplir GDPR/privacidad local

---

## SOP de Operación (diario/semanal)
- Diario
  - Revisar eventos Stripe (failed/succeeded) y tasa de recuperación
  - Monitorear cola de tickets IA y FCR
  - Validar sincronización CRM (propietarios, scores)
- Semanal
  - Auditoría de duplicados y bounces
  - Revisión de notas de release y CTR changelog
  - Informe de cuentas con riesgo (health score bajo)

## RACI (resumen)
- Responsable (R): RevOps
- Aprobador (A): Head of Growth
- Consultados (C): Soporte, Producto
- Informados (I): Finanzas, Ventas

## Plan de Pruebas (UAT)
- Casos: cobro fallido → dunning; 3 fallos → suspensión; pago recuperado → reactivación; enriquecimiento sin datos; ticket IA baja confianza
- Criterios: recovery ≥ 35%; reactivación < 5 min; FCR IA ≥ 40% inicial

## Rollback rápido
- Desactivar serie de dunning en Customer.io
- Deshabilitar endpoints /suspend y /reactivate (feature flag)
- Revertir cambio de scoring en CRM

## Plantilla de KPIs (Sheets)
- Columnas: Fecha | NuevosLeads | MQL | SQL | Recovery% | FCR% | Tiempo1ªResp(min) | ChurnInvol% | ARPU

---

## SLAs/SLOs sugeridos
- Reactivación tras pago: SLO 99% < 5 min
- Primer respuesta soporte: SLO 90% < 5 min (horario hábil)
- Generación de reportes: SLO 95% < 24 h fin de mes

## Matriz de riesgos (resumen)
- Suspensión errónea de cuentas → Mitigación: feature flag + doble verificación
- Enriquecimiento con datos desactualizados → Mitigación: proveedor alterno + timestamp
- Respuestas IA incorrectas → Mitigación: umbral de confianza + fallback

## Checklist pre‑producción
- Webhooks Stripe verificados en modo test
- Series de dunning revisadas y aprobadas
- Endpoints /suspend y /reactivate con flags
- Métricas en dashboard y alertas Slack

## Guía de despliegue
1) Activar webhooks en Stripe (test → prod)
2) Encender series en Customer.io/HubSpot
3) Habilitar flags de suspensión/reactivación
4) Validar KPIs las primeras 24–48 h

---

## Retención de datos
- Logs transaccionales (Stripe/CRM): 180 días
- Tickets y respuestas IA: 90 días (anonimizar verbatims)
- PII: enmascarar en logs; no volcar datos sensibles a prompts

## Idempotencia (Apps Script/Backend)
```javascript
function computeHash(parts) {
  const str = JSON.stringify(parts);
  return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, str));
}
```

## Rate limit y cuotas
```javascript
function withRateLimit(fn, pauseMs=1100, tries=3) {
  for (let i=0;i<tries;i++){ try{ return fn(); }catch(e){ Utilities.sleep(pauseMs*(i+1)); } }
  throw new Error('Rate limit exceeded');
}
```

## QA IA (reglas mínimas)
- Umbral de confianza; fallback a agente si < X
- Prohibido: recomendaciones legales/financieras
- Respuestas con pasos claros y enlaces KB

## ROI y límites de costo
- Límite tokens/mes por cuenta; alerta a RevOps
- Objetivo: +20% recovery, FCR IA ≥ 40% inicial

## Gobierno y Accesos
- Roles: Head Growth (A), RevOps (R), Producto/Soporte (C), Finanzas/Ventas (I)
- Accesos: claves Stripe privadas en vault, scopes mínimos en CRM
- Revisión mensual de permisos y tokens caducos

## Respuesta a Incidentes
- P0 (suspensiones erróneas): apagar flag /suspend, revertir últimos N casos, comunicar status a clientes prioritarios; ETA ≤ 2 h
- P1 (fallos dunning masivos): pausar serie, revisar eventos Stripe, reencolar pagos; ETA ≤ 24 h

## Plan de Formación
- S1 RevOps (60’): dunning, flags, dashboards
- S2 Soporte (60’): IA L1, umbrales, escalados

## Estimador de Presupuesto
- Stripe fees estándar; mensajería/emails; IA tokens para soporte
- Enriquecimiento: $ por lead (Clay/Clearbit) x volumen mensual

## Ejemplos técnicos
- Webhook backend /suspend (payload):
```json
{ "customerId": "cus_123", "reason": "payment_failed", "retries": 3 }
```

---

## Recursos útiles
- Plantillas de comunicación: `PLANTILLAS_COMUNICACION.md`
- Prompts base por industria: `PROMPTS_BASE.md`


