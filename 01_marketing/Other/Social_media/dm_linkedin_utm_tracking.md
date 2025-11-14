---
title: "Dm Linkedin Utm Tracking"
category: "01_marketing"
tags: ["business", "marketing"]
created: "2025-10-29"
path: "01_marketing/Other/Social_media/dm_linkedin_utm_tracking.md"
---

# 📈 Guía de UTM y Medición para DMs de LinkedIn

## 🎯 Objetivo
Atribuir con precisión el rendimiento de cada DM (mensaje, variante, canal) y cerrar el ciclo en CRM/analytics.

---

## 🔗 Convenciones UTM

### Base recomendada
`?utm_source=linkedin&utm_medium=dm&utm_campaign=[campaña]&utm_content=[variante]`

- **utm_source:** linkedin
- **utm_medium:** dm
- **utm_campaign:** nombre lógico (ej: curso_ia_q4, saas_trial_q1)
- **utm_content:** variante (ej: LM_Base, SaaS_ROI_A, Webinar_Urgencia_B)

### Ejemplos
- Curso lead magnet base: `/landing?utm_source=linkedin&utm_medium=dm&utm_campaign=curso_ia_q4&utm_content=LM_Base`
- SaaS ROI (var A): `/trial?utm_source=linkedin&utm_medium=dm&utm_campaign=saas_trial_q1&utm_content=SaaS_ROI_A`
- Webinar urgencia (var B): `/registro?utm_source=linkedin&utm_medium=dm&utm_campaign=webinar_q3&utm_content=Webinar_Urgencia_B`

---

## 🗂️ Nomenclatura de variantes
- Producto: `LM` (lead magnet), `WB` (webinar), `SAAS`, `BULK`
- Enfoque: `ROI`, `Problema`, `Resultado`, `PruebaSocial`, `Urgencia`
- Variante: `A`, `B`, `C`

Ejemplo: `SAAS_ROI_A`, `WB_Urgencia_B`, `BULK_Resultado_A`

---

## 📊 Métricas mínimas a trackear
- Envíos totales por variante
- Respuestas (y % respuesta)
- Clics en enlace (CTR DM)
- Conversiones (registro/descarga/trial)
- Reply-to-conversion (respuestas que convierten)
- Tiempo a primera respuesta

---

## 🧩 Integración con CRM
- Registrar en contacto: campaña, variante, link con UTM
- Estado del lead: interesado, en conversación, convertido, perdido
- Siguiente paso y fecha

---

## 📋 Plantilla de reporte (columnas sugeridas)
- fecha_envio
- nombre
- empresa
- mensaje_usado
- variante
- link_utm
- respondio (sí/no)
- clic (sí/no)
- convirtio (sí/no)
- siguiente_paso
- notas

---

## 🔁 Ciclo de optimización
1) Enviar A/B por 7-14 días
2) Analizar respuesta y conversión
3) Promover ganadora, iterar perdedora
4) Documentar aprendizajes en índice

---

## ✅ Buenas prácticas
- Un solo link por DM (reduce ambigüedad de atribución)
- Mantener consistencia en utm_campaign por cohorte
- Cambiar solo 1 variable por test
- Registrar resultados semanalmente
