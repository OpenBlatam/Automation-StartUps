# Guía de Integración Rápida – CTAs en HubSpot Sequences y Gmail Templates

## Objetivo
Implementar los CTAs del documento SaaS (1 min / demo 10’ / piloto 48h / recurso / calendario) en:
- HubSpot Sequences (Email + Tareas)
- Gmail Templates (Respuestas rápidas)

---

## HubSpot Sequences (paso a paso)

1) Propiedades necesarias (Contact)
- dm_variant (select)
- objective (select)
- reply_status (select)
- cta_used (text)
- next_step_date (date)

2) Tokens en plantillas de email
Ejemplo (Email 1 – Respuesta 1 min):
```
Asunto: {{ contact.stack_detected }} + 2 Qs (1 min) – cero venta

Hola {{ contact.firstname }},

Estoy validando un SaaS IA que integra con {{ contact.stack_detected }}.
2 preguntas (1 min):
1) ¿Tu mayor cuello de botella semanal?
2) ¿Qué te haría adoptarlo? (demo con datos / trial 7d / benchmark / integración)

A cambio te paso el benchmark 2025. ¿Te toma 1 min?
```

3) Variantes de CTA (copiar y pegar según objetivo)
- Respuesta 1 min:
```
¿Te toma 1 minuto para responder con 2 bullets? Cero venta.
```
- Demo 10’ (2 horarios):
```
¿Te va hoy 16:00 o mañana 10:30 (10 minutos)?
```
- Piloto 48h:
```
Te armamos un mini piloto en 48h con tu stack. ¿Lo activamos?
```
- Recurso (baja fricción):
```
¿Te comparto el benchmark 2025 (gratis) y la plantilla de prompts?
```
- Calendario (formal):
```
Le propongo 2 horarios de 10’: [día/hora 1] o [día/hora 2].
```

4) Pasos de la Sequence (ejemplo 7 días)
- Día 0: Email 1 (Respuesta 1 min) + Tarea LinkedIn DM
- Día 2: Email 2 (Recurso) + Tarea Comentario LinkedIn
- Día 4: Email 3 (Demo 10’) + Tarea WhatsApp (si aplica)
- Día 7: Email 4 (Cierre amable) + Tarea CRM actualizar reply_status

5) Rama condicional (Workflows opcional)
- Si reply_status = replied → crear tarea “Proponer 2 horarios” (24h)
- Si cta_used = recurso → programar next_step_date +7 días

6) Tracking UTM en links
Añade a los enlaces:
```
?utm_source=hubspot&utm_medium=sequence&utm_campaign=saas_ia_marketing&utm_content={{ contact.dm_variant }}&utm_term={{ contact.stack_detected }}
```

---

## Gmail Templates (canned responses)

1) Activar plantillas
- Gmail → Configuración → Avanzadas → Plantillas (habilitar)

2) Plantillas recomendadas (1 por objetivo)
- Respuesta 1 min:
```
Asunto: 2 Qs (1 min) – gracias

Hola {{Nombre}}, ¿me ayudas con 2 bullets? 1) Tu mayor cuello de botella semanal 2) ¿Qué te haría adoptarlo (demo/trial/benchmark/integración)?
Te paso el benchmark 2025.
```
- Demo 10’:
```
Asunto: 10’ hoy o mañana

¿Te va hoy 16:00 o mañana 10:30 (10 minutos)? Te muestro demo con tu stack.
```
- Piloto 48h:
```
Asunto: Mini piloto 48h

Armamos un mini piloto en 48h con tus métricas. ¿Lo activamos?
```
- Recurso:
```
Asunto: Benchmark 2025 + plantilla prompts

Te comparto el benchmark 2025 y la plantilla de prompts por canal. ¿Te sirve?
```
- Calendario formal:
```
Asunto: Propuesta de 10’

Le propongo 2 horarios: [día/hora 1] o [día/hora 2].
```

3) Snippet de seguimiento (bump amable)
```
Solo para cerrar bucle: si no aplica, todo bien. Gracias por leer.
```

4) Buenas prácticas
- Longitud 80–130 palabras; 1 CTA claro
- Reutiliza asunto + 1 variable de stack (HubSpot/GA4/Ads)
- Añade UTM a links si apuntas a recursos

---

## QA rápido (previo a activar)
- Tokens funcionan ({{ contact.firstname }}, etc.)
- CTAs correctos por objetivo
- Campos CRM existen y se actualizan
- UTM probadas (capturan en analytics)

## Recursos relacionados
- Documento SaaS Ultimate: `./02_DM_SAAS_IA_MARKETING_ULTIMATE.md`
- Banco de CTAs (en el doc SaaS)
- UTM + Tracking en CRM (en el doc SaaS)
