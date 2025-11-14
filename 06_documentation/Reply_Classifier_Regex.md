# 🧪 Reply Classifier (Regex)

## Buckets y Regex
- interés: `(?i)^(si|sí|ok|dale|va|me interesa|interesad|agend|demo|reserva)`
- alternativa: `(?i)(no puedo|otro dia|otra hora|grabaci[oó]n|cuando)`
- precio: `(?i)(precio|cu[aá]nto|cost|tarifa|plan)`
- objecion: `(?i)(no (me|nos) interesa|ahora no|mas adelante|no es prioridad)`
- preguntas: `(?i)(c[oó]mo|cu[aá]ndo|d[oó]nde|funciona|seguro|gdpr|nda)`
- optout: `(?i)^(stop|baja|no (molestar|enviar))$`
- no_respuesta: fallback tras 24/48h

## Orden de evaluación
1) optout
2) interés
3) alternativa
4) precio
5) preguntas
6) objecion
7) no_respuesta

## Ejemplos
- "sí, agenda 10am" → interés
- "no puedo hoy, mañana?" → alternativa
- "¿cuánto cuesta?" → precio
- "no me interesa" → objecion
- "¿es GDPR?" → preguntas
- "stop" → optout

## Salida sugerida
```
{
  "bucket": "interes",
  "next_template": "Respuestas_CopyPaste.md > Confirmación (SÍ)",
  "priority": 1
}
```
