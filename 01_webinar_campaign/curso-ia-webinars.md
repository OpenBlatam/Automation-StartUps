# Curso de IA y Webinars — Automatizaciones accionables

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
- Objetivo: reducir no‑show, acelerar post‑evento y estandarizar reporting.
- Resultado esperado (90 días): −25% no‑show, T95 certificados < 2h, resumen < 6h.
- Alcance: registro, recordatorios, certificados, replay, NPS, nutrir leads.

## Prioridades Top (Impacto/Escenario/Esfuerzo)
- Recordatorios multicanal + replay — Alto / 14 días / Bajo
- Certificados automáticos desde asistencia — Medio-alto / 7 días / Bajo
- Resumen + FAQs con IA desde transcripción — Medio / 7 días / Medio

## OKRs Trimestrales
- O1: -25% no-show promedio en webinars
- O2: 48h → 6h para publicar resumen/FAQ
- O3: 6 automatizaciones activas con DoD cumplido

## Definición de Listo (DoD)
- 1 caso feliz, 2 errores y 1 edge cubiertos
- Logs mínimos (quién/qué/cuándo)
- Métricas instrumentadas y visibles
- Runbook de fallos con propietario
- PII enmascarada; permisos Drive por carpeta

---

## 10 Automatizaciones Clave (mini-blueprints + KPI)

1) Registro → Zoom/Meet → Calendar → Confirmación
- Stack: Typeform/Forms, Zapier, Zoom/Meet, Calendar, CRM
- Flujo: New form → Upsert Contact → Create Registrant → Calendar Event → Gmail “Confirmación”
- KPI: tasa de confirmación, asistencia
- Ahorro/mes: 5–10 h

2) Recordatorios 24h/1h + WhatsApp
- Stack: Zapier, Gmail, Twilio WhatsApp
- Flujo: Delay 24h/1h → Email + WhatsApp con enlace único
- KPI: no-show, CTR
- Ahorro/mes: 3–6 h

3) Certificados automáticos desde asistencia
- Stack: Sheets (asistencia), Docs plantilla, Apps Script, Gmail
- Flujo: Asistió=Sí → Merge a PDF → Envío por Gmail
- KPI: % entrega, rebotes
- Ahorro/mes: 4–8 h

4) Resumen y FAQs con IA
- Stack: Zoom recording, Transcripción (Whisper/AssemblyAI), OpenAI, Notion
- Flujo: Fin grabación → transcribir → prompt resumen/FAQs → publicar + enviar
- KPI: tiempo a publicar, consumo
- Ahorro/mes: 5–10 h

5) Nurturing por comportamiento
- Stack: Zapier, HubSpot/ActiveCampaign
- Flujo: Asistió + clic CTA → secuencia específica; No asistió → replay + oferta
- KPI: MQL→SQL
- Ahorro/mes: 3–5 h

6) Encuesta NPS 2h post-evento + dashboard
- Stack: Forms, Zapier, Sheets, Apps Script (dashboard)
- Flujo: Envío automático → consolidar → NPS y verbatims
- KPI: NPS, tasa respuesta
- Ahorro/mes: 2–4 h

7) Lead caliente en vivo → Calendly + Slack
- Stack: Zapier, CRM, Calendly, Slack
- Flujo: Palabras clave Q&A/encuesta → deal + invitación + alerta Slack
- KPI: velocidad contacto
- Ahorro/mes: 2–3 h

8) Biblioteca de recursos con indexado
- Stack: Drive, Apps Script, Docs/Notion
- Flujo: Subida grabación → auto-página con enlaces/tags/fecha
- KPI: tiempo de búsqueda
- Ahorro/mes: 2–3 h

9) Facturación y conciliación
- Stack: Stripe, Zapier, Sheets/contabilidad
- Flujo: Charge succeeded → factura/recibo → registro ingreso → email
- KPI: DSO
- Ahorro/mes: 3–5 h

10) Certificación modular
- Stack: LMS/Sheets, Apps Script, Docs, Gmail
- Flujo: Completa módulo → certificado parcial → actualización en CRM
- KPI: completion rate
- Ahorro/mes: 2–4 h

---

## 10 Ideas Extra (rápidas)
- Auto-landing por sesión desde Sheets (1–2 h/evt)
- Slots dinámicos por demanda (overflow automático)
- Score de intención en vivo (chat/preguntas/clics)
- Snippets para redes desde transcripción (5 posts + 3 titulares)
- One‑click replay + CTA dinámico
- Auto-FAQ enriquecido con gaps detectados
- Consentimiento y compliance con evidencia en Drive
- Certificados on‑demand (reenvío/descarga autenticada)
- “Ask me later”: bandeja y asignación a experto
- Evaluación de ponente (claridad/ritmo/engagement)

---

## Recetas Zapier Plug‑and‑Play
- Typeform (New Entry) → HubSpot (Create/Update Contact) → Zoom (Create Registrant) → Gmail (Confirmación) → Calendar (Invite)
- Zoom (Recording Completed) → AssemblyAI (Transcribe) → OpenAI (Resumen/FAQs) → Notion (Create Page) → Gmail (Enviar)
- 2h Post‑evento → Gmail (Replay+CTA) → Google Forms (NPS link)

---

## Snippets de Apps Script

Enviar certificados desde asistencia:

```javascript
function enviarCertificados() {
  const sh = SpreadsheetApp.getActive().getSheetByName('Asistencia');
  const tplId = 'ID_PLANTILLA_DOCS';
  const data = sh.getDataRange().getValues().slice(1);
  data.forEach((r, i) => {
    const [email, nombre, asistio] = r;
    if (asistio !== 'Sí') return;
    const doc = DocumentApp.openById(DriveApp.getFileById(tplId).makeCopy(`Cert-${nombre}`).getId());
    const body = doc.getBody();
    body.replaceText('{{NOMBRE}}', nombre);
    doc.saveAndClose();
    const pdf = DriveApp.getFileById(doc.getId()).getAs('application/pdf');
    GmailApp.sendEmail(email, 'Tu certificado', '¡Gracias por asistir!', {attachments: [pdf]});
    sh.getRange(i + 2, 4).setValue('enviado');
  });
}
```

---

## Esquemas de Sheets
- Asistencia: Email | Nombre | Asistió(Sí/No) | EstadoCert
- Recursos: Título | URL | Tags | Fecha | WebinarID

## Plantillas e IDs requeridos
- Docs: plantilla de certificado (`ID_PLANTILLA_DOCS`)
- Zoom: cuenta con grabación cloud activa
- Gmail/Calendar: cuentas conectadas en Zapier
- CRM: API y campos de contacto (email, nombre, etiqueta webinar)

---

## Métricas y Fórmulas
- No‑show rate: =1 - (Asistentes/Confirmados)
- NPS: =(Promotores/Total)-(Detractores/Total)
- T95 envío certificado ≤ 2h

---

## Checklist por automatización
- Setup: accesos, apps conectadas, IDs, plantillas
- Pruebas: 1 caso feliz, 1 error forzado, 1 edge (cupo lleno)
- Métricas: fuente, fórmula, objetivo mensual
- Operación: dueño, SLO, fallback
- Riesgos: límites API, PII, costos, duplicados

---

## Anexos prácticos

### Prompts por industria (ejemplos)
- Educación: "Resume el webinar para docentes sobre {tema} en 7 bullets con 2 actividades prácticas en aula y recursos gratuitos verificados."
- Marketing: "Genera FAQs de webinar sobre {táctica} con objeciones típicas B2B y respuestas basadas en evidencia, tono consultivo."
- E‑commerce: "Crea un guion de replay de 5 min destacando 3 beneficios, 2 casos y 1 oferta por tiempo limitado."
- Salud: "Sintetiza el webinar para pacientes, lenguaje claro A2, lista de precauciones y referencias confiables."
- Inmobiliario: "Elabora checklist post‑webinar para compradores: financiamiento, documentos, tiempos y preguntas clave."

### Checklist Kanban (copiar en Notion/Trello)
- Backlog: objetivo, dueño, deadline, KPIs, riesgos
- Ready: credenciales confirmadas, IDs/plantillas, casos de prueba definidos
- Doing: logs habilitados, pruebas en sandbox, límites API verificados
- Review: métricas validadas, runbook escrito, seguridad revisada
- Done: DoD cumplido, dashboard conectado, propietario on‑call asignado

### Plantilla de costos (Sheets)
- Columnas: JobID | WebinarID | Tokens | CostoUSD | Fecha
- Fórmulas: costo/doc, costo total por webinar, proyección mensual

### Seguridad mínima
- No guardar PII en prompts; usar IDs
- Drive: carpetas por webinar con permisos restringidos
- Rotar tokens trimestralmente y limitar scopes

---

## SOP de Operación (diario/semanal)
- Diario
  - Verificar dashboard: asistencia, no‑show, errores de envío
  - Revisar hoja `Asistencia` y estado de certificados (pendiente/error)
  - Atender alertas Slack (leads calientes, fallos)
- Semanal
  - Auditar 3 Zaps al azar (logs, tiempo, errores)
  - Revisar plantillas de email/Docs por consistencia
  - Backup de plantillas y export de métricas

## RACI (resumen)
- Responsable (R): Operaciones de Marketing
- Aprobador (A): Lead del Curso
- Consultados (C): Soporte, Ventas
- Informados (I): Finanzas

## Plan de Pruebas (UAT)
- Casos: registro exitoso; cupo lleno; email inválido; asistencia sin certificado; replay enviado
- Criterios de aceptación: confirmación < 2 min; recordatorios en 24h/1h; certificado < 2h T95; NPS enviado 2h post

## Rollback rápido
- Desactivar Zaps de recordatorios y replay (toggle)
- Revertir última versión de plantilla Docs en Drive
- Despublicar páginas Notion generadas automáticamente si hay error masivo

## Plantilla de KPIs (pegar en Sheets)
- Columnas: Fecha | WebinarID | Registrados | Confirmados | Asistentes | NoShow% | CertificadosEnviados | NPS | TiempoResumen(h)

---

## SLAs/SLOs sugeridos
- Confirmación de registro: SLO 99% < 2 min
- Recordatorios enviados: SLO 99% 24h/1h antes del evento
- Certificados: SLO 95% < 2 h post‑asistencia
- Replay enviado: SLO 95% < 12 h

## Matriz de riesgos (resumen)
- Límite API Zoom/Zapier → Mitigación: colas y backoff
- Emails a spam → Mitigación: warming, DKIM/SPF, calidad lista
- Datos personales expuestos → Mitigación: IDs en vez de PII
- Plantilla rota → Mitigación: versión inmutable + rollback

## Checklist pre‑producción
- Conexiones: Zoom, Calendar, CRM, Gmail verificados
- Plantillas: Docs/Gmail con variables testeadas
- Casos UAT pasados; logs y alertas activados
- Dashboard con métricas clave en vivo

## Guía de despliegue
1) Clonar plantillas y configurar IDs en variables
2) Conectar Zaps y probar sandbox con 3 registros
3) Activar Apps Script (certificados) con disparador
4) Publicar dashboard y asignar propietario on‑call

---

## Retención de datos
- Logs IA: 90 días
- Transcripciones brutas: 30 días (luego anonimizar/eliminar)
- PII: minimizar y usar IDs; no persistir en prompts

## Idempotencia (Apps Script)
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
- Sin claims sin fuente ni métricas inventadas
- Tono consistente y ortografía 100/100
- Incluir 1 CTA y próximos pasos

## ROI y límites de costo
- Costo/doc objetivo: ≤ $0.12 (alerta si > $0.15)
- Ahorro esperado: 8–20 h/mes por flujo

## Gobierno y Accesos
- Roles: Owner (Aprobador), Operaciones (Responsable), Soporte (Consulta), Finanzas (Informado)
- Accesos mínimos: cuentas de servicio para Zoom, Gmail, Calendar y Drive
- Revisión de permisos trimestral y baja de accesos inactivos

## Respuesta a Incidentes (resumen)
- P0 (envíos masivos fallidos): pausar Zaps, comunicar por Slack #incidentes, ejecutar rollback de plantillas; ETA ≤ 2 h
- P1 (certificados duplicados): desactivar Script, limpiar filas afectadas, reenviar únicos; ETA ≤ 24 h

## Plan de Formación (2 sesiones)
- S1 Operativo (60’): ejecución diaria, métricas, runbook
- S2 Técnico (90’): Zaps, Apps Script, debugging y límites

## Estimador de Presupuesto (orientativo)
- Zapier: N zaps activos x $/mes
- Transcripción/IA: minutos/mes x $/min + tokens x $/1K
- Twilio: mensajes/mes x $

## Ejemplos técnicos
- Webhook de lead caliente (JSON):
```json
{ "webinarId": "W123", "email": "user@dominio.com", "topic": "precio", "timestamp": "2025-01-01T12:00:00Z" }
```

---

## Recursos útiles
- Plantillas de comunicación: `PLANTILLAS_COMUNICACION.md`
- Prompts base por industria: `PROMPTS_BASE.md`


