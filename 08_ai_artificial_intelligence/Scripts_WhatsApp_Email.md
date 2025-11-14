# 🔗 Scripts WhatsApp & Email

## WhatsApp Business API
- Plantillas (aprobadas): Confirmación, Recordatorio, Oferta 48h, Opt-out
- Variables: {{first_name}}, {{day}}, {{time}}, {{link}}

### Confirmación (ES)
```
Hola {{first_name}} 👋 Confirmamos {{day}} {{time}}.
Link: {{link}}
¿Alguna pregunta?
```

### Recordatorio (24h)
```
Hola {{first_name}} 👋 Mañana {{time}}. Link: {{link}}
Entra 5 min antes para probar audio.
```

### Oferta 48h
```
{{first_name}}, oferta especial 48h: [OFERTA]. ¿Te interesa?
```

### Opt-out
```
Hecho. Te quito de la lista. Si cambias de opinión, responde "SÍ".
```

---

## Email

### Subject A/B
- A: Ahorra 10+ h/sem con IA
- B: Checklist de IA en 24h

### Email Base
```
Asunto: [SUBJECT]

Hola {{first_name}},

[HOOK]
[BENEFICIO]
[PRUEBA SOCIAL]
[ESCASEZ]

[CTA]: {{link}}

Saludos,
[TU NOMBRE]

Si no te interesa, baja aquí.
```

## Tracking unificado
- UTM: utm_source, utm_medium, utm_campaign, utm_content={{variant_id}}
- KPI: respuestas, clics, agendas, asistencias, ventas



