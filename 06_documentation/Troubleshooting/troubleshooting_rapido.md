---
title: "Troubleshooting Rapido"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Troubleshooting/troubleshooting_rapido.md"
---

# Troubleshooting Rápido - Soluciones Inmediatas

Problemas comunes y soluciones en 30 segundos.

---

## ❌ PROBLEMA: Reply rate bajo (<15%)

### Posibles causas
1. Mensajes genéricos (solo cambias nombre)
2. Timing incorrecto
3. CTA confuso
4. Sin personalización visible

### ✅ SOLUCIÓN (30 seg)
1. Revisa `Mejores_Practicas_Comprobadas.md` → Personalización nivel 2 mínimo
2. Ajusta timing: 08:30-10:30, 13:00-14:00, 18:30-21:00
3. Simplifica CTA: "RESERVA" / "DEMO" / "SÍ" (1 palabra)
4. Agrega contexto línea 1: "Vi que {{algo específico de su perfil}}"

**Resultado esperado:** Reply rate sube a 22-28% en 1 semana

---

## ❌ PROBLEMA: Cuenta bloqueada/rate limit

### Posibles causas
1. Demasiados DMs en poco tiempo
2. Mensajes idénticos (spam detector)
3. Respuestas automáticas demasiado rápido

### ✅ SOLUCIÓN (inmediata)
1. Pausa 24-48h
2. Reduce a 15-20 DMs/hora máximo
3. Varía mensajes usando `DM_Variants_Master.csv`
4. Usa spintax para variaciones automáticas

**Prevención:** Nunca >25 DMs/hora, siempre variar texto

---

## ❌ PROBLEMA: Alta tasa de opt-out (>3%)

### Posibles causas
1. Mensajes no relevantes
2. Demasiados seguimientos
3. Sin valor aparente

### ✅ SOLUCIÓN (rápida)
1. Mejora targeting (nicho más específico)
2. Reduce seguimientos a máximo 3 en 7 días
3. Ofrece valor gratuito inmediato (checklist, ejemplo PDF)
4. Personaliza más antes de enviar

**Meta:** <2% opt-out

---

## ❌ PROBLEMA: Show rate bajo (<30%)

### Posibles causas
1. Sin recordatorios
2. Recordatorio muy tarde
3. Link no funciona
4. Zona horaria incorrecta

### ✅ SOLUCIÓN (implementar hoy)
1. Activa recordatorios: 24h + 2h + 10 min antes (`Scripts_Automatizacion_Avanzada.md`)
2. Envía recordatorio 24h antes (no el mismo día)
3. Testea links antes de enviar
4. Siempre menciona timezone: "7 PM (hora México)"

**Resultado:** Show rate sube a 45-65% con recordatorios

---

## ❌ PROBLEMA: Conversión post-evento baja (<15%)

### Posibles causas
1. Sin seguimiento después
2. Seguimiento muy tarde (+7 días)
3. Sin CTA claro en seguimiento
4. Sin personalización en seguimiento

### ✅ SOLUCIÓN (urgente)
1. Envía seguimiento en +2h (caliente)
2. Usa `Seguimiento_PostEvento_Cierre.md` → Template +2h
3. CTA único: "¿Te interesa [OFERTA]?"
4. Menciona algo específico del evento: "Del caso que vimos de {{ejemplo}}..."

**Resultado:** Conversión sube a 25-35%

---

## ❌ PROBLEMA: No sé qué variante usar

### ✅ SOLUCIÓN (2 min)
1. Abre `DM_Variants_Master.csv`
2. Filtra por: `niche={{tu_nicho}}` + `language={{idioma}}` + `tone={{tono}}`
3. Selecciona 3 variantes (A/B/C)
4. Envía 30 de cada una
5. Mide en `KPIs_Dashboard_Template.csv`
6. Escala la ganadora

**Pro tip:** Empieza con `Ejemplos_Completos_Listos.md` si tienes dudas

---

## ❌ PROBLEMA: No tengo tiempo para personalizar

### ✅ SOLUCIÓN (niveles según tiempo disponible)

**Si tienes 1 min/contacto:**
- Nivel 1: Solo nombre + industria (`Tecnicas_Personalizacion_Avanzada.md`)
- Reply rate esperado: 12-18%

**Si tienes 3 min/contacto:**
- Nivel 2: Nombre + industria + contexto básico
- Reply rate esperado: 18-25%

**Si tienes 5-10 min/contacto:**
- Nivel 3: Nombre + contexto específico + beneficio relevante
- Reply rate esperado: 25-35%

**Recomendación:** Empieza nivel 1, escala a nivel 2 cuando tengas flujo

---

## ❌ PROBLEMA: Workflow automatizado no funciona

### ✅ CHECKLIST DEBUG (5 min)

1. **Trigger funcionando?**
   - Testa con mensaje de prueba
   - Verifica que detecta palabras clave correctamente

2. **Merge-tags reemplazados?**
   - Verifica formato: `{{first_name}}` (con dobles llaves)
   - Testa con datos reales

3. **Rate limits respetados?**
   - Revisa logs de errores de API
   - Ajusta delays entre acciones

4. **Links funcionando?**
   - Testa cada link manualmente
   - Verifica UTM parameters

**Si sigue sin funcionar:**
- Simplifica workflow (menos steps)
- Usa manual temporal mientras debugueas

---

## ❌ PROBLEMA: No sé qué métricas trackear

### ✅ SOLUCIÓN (usa esto)

**Métricas esenciales (mínimo):**
- Reply rate (responde / envía)
- Click/Agenda rate (hace clic / responde)
- Show rate (asiste / agenda)

**Tracking fácil:**
1. Importa `KPIs_Dashboard_Template.csv` a Google Sheets
2. Agrega fila por cada DM enviado
3. Fórmulas calculan automáticamente
4. Revisa semanalmente

**Meta inicial:** Reply >18%, Show >35%

---

## ✅ CHECKLIST DE SALUD (Revisar semanalmente)

- [ ] Reply rate >18% (si <15%, revisar personalización)
- [ ] Opt-out <2% (si >3%, revisar relevancia)
- [ ] Show rate >35% (si <30%, activar recordatorios)
- [ ] Links funcionando (testear antes de enviar)
- [ ] Cupos actualizados (nunca mentir sobre escasez)
- [ ] Rate limits respetados (<25 DMs/hora)
- [ ] Personalización visible línea 1

**Si todo checkeado → Estás en buen camino ✅**

---

## 🆘 RESPUESTA RÁPIDA POR PROBLEMA

| Problema | Archivo a consultar | Sección |
|----------|---------------------|---------|
| Reply bajo | `Mejores_Practicas_Comprobadas.md` | Personalización |
| Timing incorrecto | `Mejores_Practicas_Comprobadas.md` | Timing |
| Show rate bajo | `Scripts_Automatizacion_Avanzada.md` | Recordatorios |
| No sé qué variante | `Ejemplos_Completos_Listos.md` | Copiar ejemplo |
| Conversión baja | `Seguimiento_PostEvento_Cierre.md` | +2h template |
| Automatización rota | `Scripts_Automatizacion_Avanzada.md` | Troubleshooting |
| Rate limit | Este archivo | "Cuenta bloqueada" |

---

**Si tu problema no está aquí:** Revisa `INDICE_COMPLETO.md` para encontrar el archivo relevante.

