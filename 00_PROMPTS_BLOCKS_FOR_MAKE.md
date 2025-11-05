# 🧩 Prompt Blocks para Make/OpenAI (Listos para Orquestar)

## Block 1: Research Lead (Empresa/Perfil)
Inputs (JSON)
```json
{
  "company": "Acme",
  "profile_url": "https://linkedin.com/in/...",
  "industry": "Education",
  "region": "LATAM",
  "language": "es"
}
```

Prompt
"Eres analista B2B. Investiga la empresa y el perfil. Devuelve pain points (3-5 con cita), métricas mencionadas, eventos próximos, competidores y 3 hooks con dato sector.
Devuelve SOLO JSON válido. Idioma: ${language}."

Outputs (JSON)
```json
{
  "painPoints": [{"text": "...", "source": "url"}],
  "metrics": ["completion 28%"],
  "upcomingEvents": ["webinar 12/11"],
  "competitors": ["Competidor X"],
  "hooks": ["<35% asiste en vivo, micro‑learning captura 65%"]
}
```

---

## Block 2: DM Generator (Variantes A‑F)
Inputs (JSON)
```json
{
  "lead": {"name": "Ana", "company": "Acme", "industry": "Education"},
  "variant": "A",
  "language": "es",
  "tone": "consultivo",
  "hook": "<35% asiste en vivo",
  "proof": "Centro similar pasó de 28% a 54%",
  "ctaOptions": ["Mié 11:00", "Jue 16:30"],
  "maxWords": 150
}
```

Prompt
"Crea un DM variante ${variant} para ${lead.company}. Incluye: hook con dato sector, beneficio concreto, prueba social breve y CTA con 2 horarios. Mantén < ${maxWords} palabras. Tono ${tone}. Idioma ${language}. Devuelve SOLO JSON con campos message y subject."

Outputs (JSON)
```json
{
  "subject": "Tu webinar → 7 micro‑lecciones (+18-30% completion)",
  "message": "Hola Ana, ... ¿Mié 11:00 o Jue 16:30?"
}
```

---

## Block 3: Follow‑up Generator (48h, 7d, 12d)
Inputs (JSON)
```json
{
  "language": "es",
  "tone": "consultivo",
  "previousAngle": "dato sector",
  "followupStage": "48h",
  "maxWords": 120
}
```

Prompt
"Genera seguimiento ${followupStage} cambiando ángulo respecto a ${previousAngle}. Mantén 1 CTA claro. < ${maxWords} palabras. Idioma ${language}. Tono ${tone}. Devuelve JSON con message."

Outputs (JSON)
```json
{ "message": "[texto del seguimiento]" }
```

---

## Block 4: Objection Handler
Inputs (JSON)
```json
{
  "language": "es",
  "tone": "consultivo",
  "objection": "Es caro",
  "proof": "−80% tiempo edición",
  "offer": "piloto sin costo"
}
```

Prompt
"Responde a la objeción: '${objection}'. Estructura: validar + diferencia clave (bullets) + oferta (${offer}) + CTA bajo compromiso. Incluye prueba (${proof}). Devuelve JSON con message."

Outputs (JSON)
```json
{ "message": "[respuesta estructurada]" }
```

---

## Block 5: Micro‑DM Multilenguaje (20‑40 palabras)
Inputs (JSON)
```json
{
  "industry": "Education",
  "angle": "micro‑learning",
  "language": "es",
  "cta": "Demo 15 min: Mié 11:00 o Jue 16:30",
  "maxWords": 40
}
```

Prompt
"Genera 1 micro‑DM de ${maxWords} palabras máximo para ${industry} con ángulo ${angle}. Cierra con '${cta}'. Idioma ${language}. Devuelve JSON con message."

Outputs (JSON)
```json
{ "message": "<35% asiste en vivo... ¿Mié 11:00 o Jue 16:30?" }
```

---

## Block 6: QA de Marca (Revisor)
Inputs (JSON)
```json
{
  "message": "texto del DM",
  "styleGuide": ["tono consultivo", "sin claims no verificados"],
  "language": "es"
}
```

Prompt
"Evalúa el DM contra la guía. Devuelve JSON con: issues (lista), severity (low/med/high), editedMessage (versión corregida mínima). Idioma ${language}."

Outputs (JSON)
```json
{
  "issues": ["CTA sin horarios"],
  "severity": "med",
  "editedMessage": "[versión corregida]"
}
```
