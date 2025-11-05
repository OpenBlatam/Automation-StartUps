# Multilingual DM Generator Prompts (ES/EN/PT)

Prompts listos para usar que generan DMs de 4 líneas por idioma, rol y canal.

## Input común
- idioma: es | en | pt
- canal: linkedin_inmail | linkedin_conexion | email_frio | email_warm
- rol: ceo | cmo | coo | sales | ops | compliance | education | healthcare
- industria: [texto]
- logro: [texto]
- fecha: [YYYY-MM-DD]
- cta: demo | webinar | trial | ejemplo
- caso_similar: [texto]
- metrica: [texto]

## Prompt Base
"""
Actúa como copywriter B2B. Genera un DM de 4 líneas en {idioma} para {canal} dirigido a {rol} en la industria {industria}.

Incluye:
1) Reconocimiento del logro: {logro} (con tono profesional)
2) Insight conectado al valor (usa {métrica} si está disponible)
3) Propuesta de valor específica según el canal y rol
4) Pregunta/CTA: {cta} (si {cta} = webinar, usa fecha {fecha})

Usa tono directo y profesional. Evita jerga, 1 CTA, 4 líneas máximo.

Si hay {caso_similar}, intégralo como prueba social.
Ajusta al canal:
- linkedin_conexion: sin enlaces, 180-200 chars, próximo paso claro
- linkedin_inmail: 3-5 líneas, puede incluir link (placeholder)
- email_frio: subject (45-65 chars) + preheader + 4 líneas, firma corta
- email_warm: menciona la referencia/evento y sé más directo
"""

## Variantes de Tono por Rol
- ceo: ejecutivo, ROI/decisiones rápidas
- cmo: métricas, personalización, ROAS
- coo/ops: eficiencia, procesos, tiempos, calidad
- sales: funnel, MQL→SQL, win rate, propuestas
- compliance: cumplimiento, audit trail, seguridad
- education: adopción docente, contenidos, reportes
- healthcare: PHI/PII, consistencia, tiempos

## Ejemplos

### ES / linkedin_inmail / cmo / saas
- logro: "alcanzaron $2M ARR"
- metrica: "2.3x ROI"
- cta: demo

Salida esperada (4 líneas):
"¡Felicidades por alcanzar $2M ARR! 
Con ese momentum, optimizar ROAS por segmento es clave. Nuestros modelos reubican presupuesto en tiempo real y clientes logran 2.3x ROI en 90 días.
¿Te va una demo de 15 min esta semana para verlo con tus campañas?"

### EN / email_warm / coo / ecommerce
- logro: "+12% AOV in Q3"
- referencia/evento: "After [EventName]"
- cta: example

Subject: After [EventName] — 12% AOV and a quick idea
Preheader: Real-time personalization without changing your stack
Body (4 lines):
"Hi [Name], after [EventName] — great +12% AOV.
A quick idea: real-time behavior personalization to push AOV another +8-12% without extra spend.
We can show a 1‑pager for e‑commerce.
Want me to send the example?"

### PT / linkedin_conexao / ceo / fintech
- logro: "fecharam rodada Série A"
- cta: webinar (data)

"Parabéns pela Série A! 
Com esse crescimento, padronizar documentação e acelerar decisões vira crítico. Mostro no webinar do {data} como líderes estão reduzindo relatórios de semanas para minutos com IA.
Quer um convite?"

## Notas de Uso
- Sustituye placeholders (Name, EventName, data)
- Respeta reglas de canal (sin links en conexión, subject/preheader en email)
- Mantén 4 líneas y 1 CTA



