# 🧲 Triggers & Keywords Map

## Mapa de palabras clave → Acción
- "webinar", "curso", "reserva" → WF1 curso (CSV maestro dm_type=curso)
- "demo", "saas", "agenda" → WF1 SaaS (dm_type=saas)
- "bulk", "documentos", "si" → WF1 bulk (dm_type=bulk)
- "grabación", "recording" → Enviar link de grabación (Templates_Seguimiento_Cierre)
- "precio", "costo", "plan" → Rama "precio" (Reply_Classifier_Regex)
- "stop", "baja" → Opt-out inmediato + etiquetar

## Reglas
- Prioridad: opt-out > interés > alternativa > precio > preguntas > objeción
- Idioma autodetectado: ES/EN/PT por keyword
- Fallback: enviar ayuda con opciones

## Ejemplo payload
```
{
  "keyword": "demo",
  "intent": "saas_demo",
  "route": "WF1>WF2",
  "params": {"language":"ES","niche":"B2B"}
}
```
