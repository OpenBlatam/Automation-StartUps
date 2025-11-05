---
title: "Dm Linkedin Variant Generator Prompt"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_variant_generator_prompt.md"
---

# 🔧 Generador de Variantes (Prompt + Plantilla)

## Objetivo
Crear 10 variantes A/B por tema manteniendo consistencia de marca y medición UTM.

---

## Prompt (para IA)
"""
Eres copywriter senior de LinkedIn. Genera 10 variantes de DMs (cada una con dos versiones A/B) para el tema: [TEMA].

Reglas:
- 5-6 líneas máximo
- 1 CTA claro (pregunta cerrada)
- Incluir beneficio cuantificado cuando sea posible
- Evitar jergas; tono profesional y directo
- Añadir slug UTM para cada variante (utm_content)
- Añadir opt-out recomendado

Entrega en JSON con campos: variant_id, message_A, message_B, utm_content.
"""

---

## Plantilla JSON (salida esperada)
```json
[
  {
    "variant_id": "Resultado_01",
    "utm_content": "Resultado_01",
    "message_A": "Hola [Nombre], [beneficio]. [prueba social]. ¿Te envío [recurso]/¿Te reservo [webinar]?",
    "message_B": "Hola [Nombre], [pregunta directa sobre problema]. [beneficio]. ¿Quieres que te pase el acceso?"
  }
]
```

---

## Ejecución rápida
1) Define TEMA: "SaaS Trial - ROI y Tiempo Recuperado".
2) Ejecuta prompt en tu IA.
3) Copia JSON al archivo `dm_linkedin_export_json_examples.json` (o crea otro por campaña).
4) Usa `utm_content` como etiqueta de variante en Sheets/CRM.

---

## Buenas prácticas
- Cambia solo 1 variable por test (hook, beneficio o CTA)
- Mantén consistencia en `utm_campaign`
- Revisa tono/claims contra guía de marca
