---
title: "Guía de UTMs para Outreach"
category: "tracking"
tags: ["utm","tracking","analytics","campañas"]
created: "2025-10-29"
path: "UTM_GUIDE_OUTREACH.md"
slug: "utm-guide-outreach"
language: "es"
scope: "utm_conventions"
---

---

# Tabla de contenido
- [Tabla de contenido](#tabla-de-contenido)
- [Guía de UTMs para Outreach](#guía-de-utms-para-outreach)
  - [Convenciones](#convenciones)
  - [Ejemplos](#ejemplos)
  - [Instagram Stories/Reels (Orgánico y Ads)](#instagram-storiesreels-orgánico-y-ads)
  - [Mini Generador (Sheets)](#mini-generador-sheets)
  - [Buenas Prácticas](#buenas-prácticas)
  - [Matriz por canal (plantillas rápidas)](#matriz-por-canal-plantillas-rápidas)
  - [Convención de nombres (claridad y escalabilidad)](#convención-de-nombres-claridad-y-escalabilidad)
  - [QA checklist antes de publicar](#qa-checklist-antes-de-publicar)
  - [Fórmulas útiles (Sheets/Excel)](#fórmulas-útiles-sheetsexcel)
  - [GA4 — lectura rápida](#ga4--lectura-rápida)
  - [UTMs por región e idioma (ES/EN · MX/AR/ES/CO)](#utms-por-región-e-idioma-esen--mxaresco)
  - [GA4 Explorations — plantillas (paso a paso)](#ga4-explorations--plantillas-paso-a-paso)
  - [Governance y versionado](#governance-y-versionado)
  - [WhatsApp / Email (DMs comerciales)](#whatsapp--email-dms-comerciales)
  - [Remarketing Facebook/Instagram (Plantillas UTM)](#remarketing-facebookinstagram-plantillas-utm)
    - [Nomenclatura de archivos (consistente con UTMs)](#nomenclatura-de-archivos-consistente-con-utms)
    - [CSV para DCO (Meta) con UTMs embebidos](#csv-para-dco-meta-con-utms-embebidos)
    - [Reglas rápidas](#reglas-rápidas)
  - [KPIs mínimos y decisiones](#kpis-mínimos-y-decisiones)
  - [Nombres de campaña estandarizados (Curso IA, SaaS, Webinars)](#nombres-de-campaña-estandarizados-curso-ia-saas-webinars)
  - [Shortlinks y estructura (listos para copiar)](#shortlinks-y-estructura-listos-para-copiar)
  - [Plantillas por canal (copiar/pegar)](#plantillas-por-canal-copiarpegar)
  - [Mapa de campos por canal (qué poner en cada campo)](#mapa-de-campos-por-canal-qué-poner-en-cada-campo)
  - [Meta Ads (TOF/MOF/BOF) — Convenciones y ejemplos](#meta-ads-tofmofbof--convenciones-y-ejemplos)
  - [Google Search / PMAX — Convenciones y ejemplos](#google-search--pmax--convenciones-y-ejemplos)
  - [Referencias](#referencias)
  - [Publicación en Meta — Checklist express](#publicación-en-meta--checklist-express)
  - [Looker/GA4 — Campos calculados útiles](#lookerga4--campos-calculados-útiles)
  - [Validación nombre de archivo (regex)](#validación-nombre-de-archivo-regex)
  - [QA UTM (checklist rápido antes de publicar)](#qa-utm-checklist-rápido-antes-de-publicar)
  - [Checklist rápido (copia/pega)](#checklist-rápido-copiapega)
  - [Errores comunes a evitar](#errores-comunes-a-evitar)
  - [UTM Builder (tabla base para Sheets/CSV)](#utm-builder-tabla-base-para-sheetscsv)
  - [Validación con REGEX (opcional)](#validación-con-regex-opcional)
  - [Audiencias y exclusiones (Meta — Remarketing)](#audiencias-y-exclusiones-meta--remarketing)
  - [Frecuencia y puja (recomendado)](#frecuencia-y-puja-recomendado)
  - [Reglas de parada y escala (72 h)](#reglas-de-parada-y-escala-72-h)
  - [Plantillas de nombres (consistencia)](#plantillas-de-nombres-consistencia)
  - [Notas DCO/Asset Customization](#notas-dcoasset-customization)
  - [LinkedIn Ads (InMail, Sponsored Content, Message Ads)](#linkedin-ads-inmail-sponsored-content-message-ads)
  - [Google Ads (Search y Performance Max)](#google-ads-search-y-performance-max)
  - [GA4 Checklist paso a paso (de UTMs a decisiones)](#ga4-checklist-paso-a-paso-de-utms-a-decisiones)
  - [Anexos — Diccionario rápido de campos](#anexos--diccionario-rápido-de-campos)
  - [Calendario de campañas (plantilla CSV)](#calendario-de-campañas-plantilla-csv)
  - [Librería de ángulos (utm\_content) por canal](#librería-de-ángulos-utm_content-por-canal)

---

# Guía de UTMs para Outreach

Convenciones para generar UTMs consistentes y medibles.

---

## Convenciones

- utm_source: canal origen
  - linkedin_inmail | linkedin_connection | email | instagram | facebook | whatsapp
- utm_medium: tipo medio
  - social | email | referral | stories | reels | ads | dm
- utm_campaign: campaña
  - `[PRODUCTO]_[CANAL]_[OBJETIVO]_[YYYY-MM]`
  - Ej: `saas_marketing_linkedin_demo_2025-10`
- utm_content: variante de contenido
  - `[VERSION_DM]_[INDUSTRIA]`
  - Ej: `vip_saas` | `roi_ecommerce`
- utm_term: segmentación/término
  - `[ROL]_[PAIS]` → `cmo_mexico`

---

## Ejemplos

LinkedIn InMail (SaaS IA):
```
https://tusitio.com/demo?utm_source=linkedin_inmail&utm_medium=social&utm_campaign=saas_marketing_linkedin_demo_2025-10&utm_content=roi_saas&utm_term=cmo_mexico
```

Email (Curso IA):
```
https://tusitio.com/curso?utm_source=email&utm_medium=email&utm_campaign=curso_ia_email_lead_2025-10&utm_content=equipo_education&utm_term=coo_espana
```

LinkedIn Connection (IA Bulk):
```
https://tusitio.com/docs?utm_source=linkedin_connection&utm_medium=social&utm_campaign=bulk_docs_linkedin_demo_2025-10&utm_content=compliance_fintech&utm_term=ops_chile
```

---

## Instagram Stories/Reels (Orgánico y Ads)

Campos recomendados:
- utm_source: `instagram`
- utm_medium: `stories` | `reels` | `ads`
- utm_campaign: `[producto]_ig_[objetivo]_[yyyy-mm]`
- utm_content: `[pieza]-[hook]-[cta]-[fecha]`
- utm_term (opcional): `[mercado]_[persona]` → `mx_cmo`

Plantilla lista:
```
https://tusitio.com/landing?utm_source=instagram&utm_medium=stories&utm_campaign=cursoia_ig_registros_2025-10&utm_content=curso-hook_ia10dias-cta_empieza-gratis-2025-10-30&utm_term=mx_buyer
```

Nomenclatura de archivo consistente:
```
IGS_[pieza]_[hook]_[cta]_vA_[YYYY-MM-DD].mp4
```

CSV para calendario/medición:
```
fecha,pieza,hook,cta,musica,landing_url
2025-10-30,curso,ia10dias,empieza-gratis,track1,https://tusitio.com/landing?utm_source=instagram&utm_medium=stories&utm_campaign=cursoia_ig_registros_2025-10&utm_content=curso-ia10dias-empieza-gratis-2025-10-30&utm_term=mx_buyer
```

---

## Mini Generador (Sheets)

Asumiendo columnas:
- A: base_url
- B: utm_source
- C: utm_medium
- D: utm_campaign
- E: utm_content
- F: utm_term

Fórmula (Google Sheets):
```
=LOWER(A2 & "?utm_source=" & B2 & "&utm_medium=" & C2 & "&utm_campaign=" & D2 & "&utm_content=" & E2 & "&utm_term=" & F2)
```

---

## Buenas Prácticas
- Sin espacios; usar guiones bajos `_`.
- Todo en minúsculas.
- No repetir información entre campos.
- Versiona campañas por mes (YYYY-MM).
- Documenta en CSV/CRM junto a cada lead.

---

## Matriz por canal (plantillas rápidas)

- Instagram Feed (post estático)
  - source: `instagram`
  - medium: `feed`
  - campaign: `[producto]_[objetivo]_ig_YYYY-MM`
  - content: `hero|beneficio|socialproof` + `_v{1..n}`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=instagram&utm_medium=feed&utm_campaign=saas_demo_ig_2025-10&utm_content=beneficio_v2
    ```

- Instagram Reel / Story
  - medium: `reel` | `story`
  - content: `progressbar|antes_despues|testimonio` + `_v{1..n}`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=instagram&utm_medium=reel&utm_campaign=saas_demo_ig_2025-10&utm_content=progressbar_v1
    ```

- Carrusel IG
  - medium: `carousel`
  - content: `proceso|producto|resultado` + `_slide{s}`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=instagram&utm_medium=carousel&utm_campaign=saas_demo_ig_2025-10&utm_content=proceso_slide3
    ```

- Email
  - source: `email`
  - medium: `email`
  - campaign: `[producto]_email_[objetivo]_YYYY-MM`
  - content: `asuntoA|asuntoB|cta_primary`
  - ejemplo:
    ```
    https://tusitio.com/curso?utm_source=email&utm_medium=email&utm_campaign=curso_ia_email_registro_2025-10&utm_content=cta_primary
    ```

- WhatsApp / SMS
  - source: `whatsapp` | `sms`
  - medium: `message`
  - content: `dm_v1|seguimiento_v2`
  - ejemplo:
    ```
    https://tusitio.com/demo?utm_source=whatsapp&utm_medium=message&utm_campaign=saas_demo_wpp_2025-10&utm_content=dm_v1
    ```

- QR (flyer/evento)
  - source: `qr`
  - medium: `offline`
  - content: `flyer_evento|stand_v1`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=qr&utm_medium=offline&utm_campaign=lanzamiento_evento_2025-11&utm_content=flyer_evento
    ```

- Ads (Meta/Google)
  - source: `meta` | `google`
  - medium: `cpc`
  - term: usar keyword o conjunto de anuncios: `kw_brand|adset_audience1`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=saas_search_brand_2025-10&utm_content=rsas_v3&utm_term=kw_saas_marketing
    ```

---

## Convención de nombres (claridad y escalabilidad)

- campaign: `[producto]_[objetivo]_[canal]_[YYYY-MM]`
  - `saas_demo_ig_2025-10`, `curso_registro_email_2025-11`
- content: `[ángulo](_v{n}|_slide{s}|_hook{x})`
  - `beneficio_v2`, `resultado_slide4`, `hook1`
- term (opcional): `[rol]_[pais]|[audiencia]|[kw]`
  - `cmo_mexico`, `prospect_b2b`, `kw_saas_marketing`

---

## QA checklist antes de publicar

- ¿Minúsculas y guiones bajos en todos los campos?
- ¿Sin espacios ni caracteres especiales?
- ¿La campaña versionada con `YYYY-MM`?
- ¿`utm_source` refleja el origen real (p. ej., `instagram`, `email`)?
- ¿`utm_medium` distingue bien el placement (feed/reel/story/email/cpc)?
- ¿`utm_content` refleja variante/ángulo/slide?
- ¿El enlace abre la landing correcta y carga sin errores?

---

## Fórmulas útiles (Sheets/Excel)

- Generador simple (incluye `utm_term` solo si existe en G2):
  ```
  =LOWER(A2 & "?utm_source=" & B2 & "&utm_medium=" & C2 & "&utm_campaign=" & D2 & "&utm_content=" & E2 & IF(LEN(F2)>0, "&utm_term=" & F2, ""))
  ```

- Normalizar texto (reemplaza espacios por `_` y a minúsculas):
  ```
  =LOWER(SUBSTITUTE(A2, " ", "_"))
  ```

---

## GA4 — lectura rápida

- Acquisition → Traffic acquisition: dimensiona por `Session source/medium` y añade `Session campaign`.
- Explorar → Free form: agrega `Session source/medium`, `Session campaign`, `Session manual ad content` (utm_content), y evento `generate_lead`/`purchase`.
- Guarda un segmento por campaña (`utm_campaign=...`) para comparar variantes `utm_content`.

---

## UTMs por región e idioma (ES/EN · MX/AR/ES/CO)

- Convención de `utm_term` regional/persona:
  - `[pais]_[persona]` → `mx_cmo`, `ar_smb`, `es_startup`, `co_ecommerce`
- Sufijo de idioma en `utm_content` cuando aplica bicanal:
  - `hero_es`, `benefit_en`, `countdown_es`
- Plantillas por canal:
  - IG Feed ES (MX):
    ```
    https://tusitio.com/landing?utm_source=instagram&utm_medium=feed&utm_campaign=saasia_demo_ig_2025-11&utm_content=beneficio_es_v2&utm_term=mx_cmo
    ```
  - IG Reel EN (ES):
    ```
    https://tusitio.com/landing?utm_source=instagram&utm_medium=reel&utm_campaign=saasia_demo_ig_2025-11&utm_content=process_en_v1&utm_term=es_startup
    ```
  - Email ES (AR):
    ```
    https://tusitio.com/curso?utm_source=email&utm_medium=email&utm_campaign=cursoia_registro_email_2025-11&utm_content=cta_primary_es&utm_term=ar_smb
    ```
  - Google Search EN (CO):
    ```
    https://tusitio.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=saasia_search_nb_2025-11&utm_content=rsas_en_v1&utm_term=kw_marketing_ai_co
    ```

Notas:
- Mantén `utm_campaign` sin sufijos de idioma para agrupar la campaña; usa el idioma en `utm_content`.
- Para PMAX, duplica asset groups por idioma y distingue con `_es`/`_en` en `utm_content`.

---

## GA4 Explorations — plantillas (paso a paso)

- Plantilla 1: Comparación de `utm_content`
  1) Explorar → Free Form
  2) Dimensiones: `Session source/medium`, `Session campaign`, `Session manual ad content`
  3) Métricas: `Sessions`, `Users`, `Engaged sessions`, `Conversions`
  4) Filtro: `Session campaign` = tu campaña (`saasia_demo_ig_2025-11`)
  5) Tabla: filas por `utm_content`; ordena por `Conversions`

- Plantilla 2: Cohortes por semana
  1) Explorar → Cohort exploration
  2) Cohorte por `First session date` semanal
  3) Segmento: `Session campaign` = tu campaña
  4) Métrica: `Conversion rate` del evento objetivo
  5) Compara semanas previas y post cambio de `utm_content`

Tip: Guarda estos explorations con el nombre de la campaña para reuso.

---

## Governance y versionado

- Versionado mensual obligatorio: `[yyyy-mm]` al final de `utm_campaign`.
- Cambios de copy/creativos mayores → incrementa versión en `utm_content` (`_v2`, `_v3`).
- Changelog por campaña (CSV):
```
fecha,cambio,campo,valor_antes,valor_despues,owner
2025-11-01,Actualiza CTA,utm_content,beneficio_v1,beneficio_v2,adan
2025-11-03,Región,utm_term,es_startup,mx_cmo,adan
```
- Archivar shortlinks al cierre del mes; mantener alias vivos 90 días.

## WhatsApp / Email (DMs comerciales)

Sugerido para los DMs de `Variantes_RealEstate_Tu.md` y outreach:
- utm_source: `whatsapp` | `email`
- utm_medium: `dm`
- utm_campaign: `[producto]_dm_[objetivo]_[yyyy-mm]`
- utm_content: `[variante]-[zona|industria]-[cta]`

Ejemplos:
```
https://tusitio.com/visita?utm_source=whatsapp&utm_medium=dm&utm_campaign=realestate_dm_agendar_2025-10&utm_content=checklist-barrio_norte-reserva

https://tusitio.com/tour?utm_source=email&utm_medium=dm&utm_campaign=realestate_dm_tour_2025-10&utm_content=videotour-barrio_centro-ver_demo
```

---

## Remarketing Facebook/Instagram (Plantillas UTM)

Convención específica para campañas de remarketing (carrito/PDP 3d/7d/14d):

- utm_source: `facebook` | `instagram`
- utm_medium: `remarketing`
- utm_campaign: `[producto]_cart_[ventana]_[yyyy-mm]`
  - Ej: `cursoia_cart_7d_2025-10`, `saasia_cart_3d_2025-10`, `iabulk_cart_14d_2025-10`
- utm_content: `[h1]_[cta]_[fondo]`
  - h1: `h1_directo` | `h1_beneficio` | `h1_urgencia`
  - cta: `cta_rojo` | `cta_amarillo` | `cta_outline`
  - fondo: `fondo_claro` | `fondo_degradado` | `fondo_dark`
- utm_term (opcional): `[pais|region]_[cohorte]`

Ejemplos listos:
```
https://tusitio.com/curso-ia?utm_source=facebook&utm_medium=remarketing&utm_campaign=cursoia_cart_7d_2025-10&utm_content=h1_beneficio_cta_rojo_fondo_claro&utm_term=mx_7d

https://tusitio.com/saas-ia?utm_source=facebook&utm_medium=remarketing&utm_campaign=saasia_cart_3d_2025-10&utm_content=h1_directo_cta_amarillo_fondo_degradado&utm_term=co_3d

https://tusitio.com/ia-bulk?utm_source=instagram&utm_medium=remarketing&utm_campaign=iabulk_cart_14d_2025-10&utm_content=h1_urgencia_cta_rojo_fondo_dark&utm_term=ar_14d
```

### Nomenclatura de archivos (consistente con UTMs)
```
fb_rmk_[producto]_[3d|7d|14d]_[h1|cta|fondo]_v01.png
```

### CSV para DCO (Meta) con UTMs embebidos
Estructura sugerida para subir a Asset Customization/DCO y trackear por variante.
```
id,landing_url,producto,h1,cta,fondo,utm_source,utm_medium,utm_campaign,utm_content,utm_term
cursoA,https://tusitio.com/curso-ia,cursoia,h1_beneficio,cta_rojo,fondo_claro,facebook,remarketing,cursoia_cart_7d_2025-10,h1_beneficio_cta_rojo_fondo_claro,mx_7d
saasB,https://tusitio.com/saas-ia,saasia,h1_directo,cta_amarillo,fondo_degradado,facebook,remarketing,saasia_cart_3d_2025-10,h1_directo_cta_amarillo_fondo_degradado,co_3d
bulkC,https://tusitio.com/ia-bulk,iabulk,h1_urgencia,cta_rojo,fondo_dark,instagram,remarketing,iabulk_cart_14d_2025-10,h1_urgencia_cta_rojo_fondo_dark,ar_14d
```

### Reglas rápidas
- Mantén `[producto]` corto y sin espacios: `cursoia`, `saasia`, `iabulk`.
- Versiona `yyyy-mm` para control mensual.
- `utm_content` debe mapear exactamente a la variante creativa exportada.

---

## KPIs mínimos y decisiones

- Historias/Reels orgánico: Retención 3s ≥ 65%, 8s ≥ 40%, CTR link ≥ 1.8%
- Ads: CTR ≥ 1.8–3.5% según segmentación; VTR 8s ≥ 35–45%
- Si CTR < 1.2% con retención OK → mover sticker, invertir CTA, cambiar verbo
- Si Ret 3s < 55% → cambiar hook/primer plano (rostro/resultado)

---

## Nombres de campaña estandarizados (Curso IA, SaaS, Webinars)

```
[producto]_[objetivo]_[canal]_[yyyy-mm]
```

- Curso IA
  - `cursoia_registro_ig_2025-11`
  - `cursoia_registro_email_2025-11`
  - `cursoia_rmk_cart_7d_meta_2025-11`

- SaaS IA (marketing)
  - `saasia_demo_ig_2025-11`
  - `saasia_demo_linkedin_2025-11`
  - `saasia_search_brand_google_2025-11`

- IA Bulk (3 docs con 1 consulta)
  - `iabulk_demo_ig_2025-11`
  - `iabulk_onboarding_email_2025-11`
  - `iabulk_rmk_viewcontent_meta_2025-11`

Ángulos sugeridos para `utm_content`:
- `hero`, `beneficio`, `proceso`, `resultado`, `testimonio`, `urgencia`, `oferta`
- Ej.: `beneficio_v2`, `resultado_slide3`, `testimonio_hook1`

---

## Shortlinks y estructura (listos para copiar)

- Formato slug corto:
  - `/{producto}/{canal}/{camp}/{var}` → redirige a URL con UTM completos
  - Ejemplo slug: `/saasia/ig/2025-11/beneficio-v2`

- Tabla ejemplo
```
slug, destino
/saasia/ig/2025-11/beneficio-v2, https://tusitio.com/landing?utm_source=instagram&utm_medium=feed&utm_campaign=saasia_demo_ig_2025-11&utm_content=beneficio_v2
/cursoia/email/2025-11/cta-primary, https://tusitio.com/curso?utm_source=email&utm_medium=email&utm_campaign=cursoia_registro_email_2025-11&utm_content=cta_primary
/iabulk/reel/2025-11/progressbar-v1, https://tusitio.com/docs?utm_source=instagram&utm_medium=reel&utm_campaign=iabulk_demo_ig_2025-11&utm_content=progressbar_v1
```

Campos mínimos para CSV de shortlinks:
```
slug,full_url,notes
```

Reglas:
- Mantén slugs en minúsculas y con `-` en lugar de `_`.
- Versiona por mes para limpieza y reporting.

---

## Plantillas por canal (copiar/pegar)

- IG Feed
```
https://tusitio.com/landing?utm_source=instagram&utm_medium=feed&utm_campaign=[producto]_[objetivo]_ig_[yyyy-mm]&utm_content=[angulo]_v1
```

- IG Reel
```
https://tusitio.com/landing?utm_source=instagram&utm_medium=reel&utm_campaign=[producto]_[objetivo]_ig_[yyyy-mm]&utm_content=[formato]_v1
```

- Email
```
https://tusitio.com/landing?utm_source=email&utm_medium=email&utm_campaign=[producto]_email_[objetivo]_[yyyy-mm]&utm_content=[cta|asunto]
```

- WhatsApp
```
https://tusitio.com/landing?utm_source=whatsapp&utm_medium=message&utm_campaign=[producto]_wpp_[objetivo]_[yyyy-mm]&utm_content=[dm|seguimiento]_v1
```

> Archivo complementario: `SHORTLINKS_UTM_SAMPLE.csv` con 20 shortlinks listos para importar (slugs + URLs UTM + notas).

---

## Mapa de campos por canal (qué poner en cada campo)

| Canal | utm_source | utm_medium | utm_campaign | utm_content | utm_term | Ejemplo (1 línea) |
|---|---|---|---|---|---|---|
| IG Stories | instagram | stories | `[producto]_ig_[objetivo]_[yyyy-mm]` | `[pieza]-[hook]-[cta]-[fecha]` | `mercado_persona` | `instagram / stories / cursoia_ig_registros_2025-11 / curso-ia10dias-empieza-2025-11-05 / mx_buyer` |
| IG Reels | instagram | reels | `[producto]_ig_[objetivo]_[yyyy-mm]` | `[pieza]-[hook]-[cta]-[fecha]` | `mercado_persona` | `instagram / reels / saasia_ig_trials_2025-11 / saas-10x-ab1clic-empieza-2025-11-05 / es_cmo` |
| Meta Remarketing | facebook/instagram | remarketing | `[producto]_cart_[ventana]_[yyyy-mm]` | `h1_[tipo]_cta_[color]_fondo_[tema]` | `pais_ventana` | `facebook / remarketing / cursoia_cart_7d_2025-11 / h1_beneficio_cta_rojo_fondo_claro / mx_7d` |
| Email | email | email | `[producto]_email_[objetivo]_[yyyy-mm]` | `asunto|cta` | (vacío) | `email / email / cursoia_email_registro_2025-11 / cta_primary` |
| WhatsApp | whatsapp | dm/message | `[producto]_dm_[objetivo]_[yyyy-mm]` | `[variante]-[zona]-[cta]` | `mercado_persona` | `whatsapp / dm / realestate_dm_agendar_2025-11 / checklist-norte-reserva / mx_buyer` |
| Google Search | google | cpc | `[producto]_search_[brand|nb]_[yyyy-mm]` | `rsas_v{n}` | `{keyword}` | `google / cpc / saasia_search_brand_2025-11 / rsas_v3 / {keyword}` |
| Google PMAX | google | pmax | `[producto]_pmax_[yyyy-mm]` | `assetgroup_[tema]_v{n}` | `{targetid}` | `google / pmax / saasia_pmax_2025-11 / assetgroup_beneficio_v1 / {targetid}` |
| TikTok Ads | tiktok | ads | `[producto]_tt_[objetivo]_[yyyy-mm]` | `[pieza]-[hook]-[cta]-[fecha]` | `mercado_persona` | `tiktok / ads / cursoia_tt_registros_2025-11 / hook_ia10dias-cta_empieza-2025-11-05 / mx_buyer` |

Notas:
- Mantén todo en minúsculas y sin espacios. Usa `_` en `utm_*` y `-` en nombres de archivos.
- `utm_content` debe mapear al nombre exportado (hook/cta/fecha/version).

## Meta Ads (TOF/MOF/BOF) — Convenciones y ejemplos

- TOF (Descubrimiento)
  - source: `meta`
  - medium: `cpc`
  - campaign: `[producto]_tof_meta_[yyyy-mm]`
  - content: `[angulo]_[formato]_[cta]` → `beneficio_reel_cta_primary`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=meta&utm_medium=cpc&utm_campaign=saasia_tof_meta_2025-11&utm_content=beneficio_reel_cta_primary
    ```

- MOF (Consideración)
  - campaign: `[producto]_mof_meta_[yyyy-mm]`
  - content: `proceso_carousel_cta_demo` | `testimonio_video_cta_reserva`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=meta&utm_medium=cpc&utm_campaign=saasia_mof_meta_2025-11&utm_content=proceso_carousel_cta_demo
    ```

- BOF (Conversión/Remarketing)
  - campaign: `[producto]_bof_meta_[yyyy-mm]`
  - content: `urgencia_static_cta_trial` | `oferta_video_cta_compra`
  - term (opcional): `viewcontent_7d|cart_14d`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=meta&utm_medium=cpc&utm_campaign=saasia_bof_meta_2025-11&utm_content=urgencia_static_cta_trial&utm_term=viewcontent_7d
    ```

---

## Google Search / PMAX — Convenciones y ejemplos

- Search Brand
  - source: `google`
  - medium: `cpc`
  - campaign: `[producto]_search_brand_[yyyy-mm]`
  - term: `kw_{marca}` → `kw_saasia`
  - content: `rsas_v{n}`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=saasia_search_brand_2025-11&utm_content=rsas_v3&utm_term=kw_saasia
    ```

- Search Non-Brand
  - campaign: `[producto]_search_nb_[yyyy-mm]`
  - term: `kw_{intencion}` → `kw_software_marketing_ia`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=saasia_search_nb_2025-11&utm_content=rsas_v2&utm_term=kw_software_marketing_ia
    ```

- Performance Max (PMAX)
  - medium: `pmax`
  - campaign: `[producto]_pmax_[yyyy-mm]`
  - content: `assetgroup_{tema}_v{n}` → `assetgroup_beneficio_v1`
  - ejemplo:
    ```
    https://tusitio.com/landing?utm_source=google&utm_medium=pmax&utm_campaign=saasia_pmax_2025-11&utm_content=assetgroup_beneficio_v1
    ```

## Referencias
- `KPI_DASHBOARD_TEMPLATE.md`
- `SCRIPT_SHORTLINKS_GENERATOR.py` (para shortlinks)
- `OUTREACH_MESSAGES_READY.csv` (si aplica)

---

## Publicación en Meta — Checklist express

- Campaign name: `[producto]_cart_[3d|7d|14d]_[yyyy-mm]`
- Ad set name: `[pais]_[audiencia]_[placement]` → `mx_abandon_cart_feed`
- Ad name: `[h1]_[cta]_[fondo]_v01` (debe coincidir con `utm_content` y el nombre de archivo)
- Asset customization/DCO: columnas `h1/cta/fondo` + URL con UTMs; `alt_text` cargado
- Excluir compradores 30/60/180; frecuencia objetivo 1.5–2.5/día

## Looker/GA4 — Campos calculados útiles

- Variante creativa (legible desde `utm_content`):
```
REGEXP_EXTRACT(manualAdContent, "h1_([a-z]+)_cta_([a-z]+)_fondo_([a-z]+)")
```
- Ventana (desde `utm_campaign`):
```
REGEXP_EXTRACT(sessionCampaign, "_cart_(3d|7d|14d)_")
```
- País/cohorte (desde `utm_term`):
```
IF(manualTerm!="", manualTerm, "na")
```

## Validación nombre de archivo (regex)

- `fb_rmk_[a-z0-9]+_(3d|7d|14d)_h1_(directo|beneficio|urgencia)_cta_(rojo|amarillo|outline)_fondo_(claro|degradado|dark)_v[0-9]{2}\.(png|jpg|mp4)`
- Ej.: `fb_rmk_saasia_3d_h1_directo_cta_rojo_fondo_claro_v01.png`


## QA UTM (checklist rápido antes de publicar)

- ¿`utm_source`, `utm_medium`, `utm_campaign` y `utm_content` están en minúsculas y sin espacios?
- ¿La campaña sigue `[producto]_[canal]_[objetivo]_[yyyy-mm]` y está actualizada al mes vigente?
- ¿`utm_content` mapea exactamente al nombre del archivo/export (hook/cta/fecha/version)?
- ¿El `utm_term` (si aplica) usa `mercado_persona` consistente con tu segmentación (ej. `mx_buyer`, `es_cmo`)?
- ¿La URL base no tiene parámetros duplicados (evita `?` doble o `&&`)?
- ¿Probaste el link final en móvil y escritorio (resuelve, no redirige en bucle, conserva UTMs)?

Fórmula de validación (Google Sheets, marca errores básicos):
```
=IF(OR(REGEXMATCH(D2,"[A-Z ]"),REGEXMATCH(E2,"[A-Z ]"),REGEXMATCH(F2,"[A-Z ]")),"ERROR: usa minúsculas/sin espacios","OK")
```

Builder rápido (une campos y fuerza minúsculas):
```
=LOWER(A2&"?utm_source="&B2&"&utm_medium="&C2&"&utm_campaign="&D2&"&utm_content="&E2&IF(F2<>"","&utm_term="&F2,""))
```

---

## Checklist rápido (copia/pega)
- [ ] `utm_source` correcto (origen real)
- [ ] `utm_medium` específico (feed/reel/story/email/cpc)
- [ ] `utm_campaign` con `[producto]_[canal]_[objetivo]_[yyyy-mm]`
- [ ] `utm_content` describe variante (ángulo|slide|cta|hook|vN)
- [ ] Prueba de link en móvil y desktop
- [ ] Guardado en CSV/CRM con owner y fecha

## Errores comunes a evitar
- Mezclar mayúsculas y espacios → siempre minúsculas y `_`
- Repetir el mismo dato entre campos (ej. `email` en source y medium)
- No versionar campañas por mes (`yyyy-mm`)
- `utm_content` genérico que no mapea a la creativa
- Perder UTMs por redirecciones sin preservar querystring

## UTM Builder (tabla base para Sheets/CSV)
```
base_url,utm_source,utm_medium,utm_campaign,utm_content,utm_term,final_url
https://tusitio.com/landing,instagram,feed,saasia_demo_ig_2025-11,beneficio_v1,,
https://tusitio.com/curso,email,email,cursoia_registro_email_2025-11,cta_primary,
```
Fórmula para `final_url`:
```
=LOWER(A2&"?utm_source="&B2&"&utm_medium="&C2&"&utm_campaign="&D2&"&utm_content="&E2&IF(F2<>"","&utm_term="&F2,""))
```

## Validación con REGEX (opcional)
- Marca error si encuentra mayúsculas/espacios en `campaign/content/term`:
```
=IF(OR(REGEXMATCH(D2,"[A-Z ]"),REGEXMATCH(E2,"[A-Z ]"),REGEXMATCH(F2,"[A-Z ]")),"ERROR: minúsculas_sin_espacios","OK")
```

---

## Audiencias y exclusiones (Meta — Remarketing)

- Audiencias principales:
  - Abandono carrito: 3d, 7d, 14d (tres conjuntos; prioridad 3d > 7d > 14d)
  - ViewContent/PDP sin ATC: 7–14d
  - Engagers IG/FB últimos 14–30d (solo si necesitas volumen)
- Exclusiones:
  - Compradores 30/60/180d
  - Leads/registrados 30/60d (según objetivo)
  - Staff/ips internas (si aplica)
- Naming ad set: `[pais]_[audiencia]_[ventana]_[placement]` → `mx_cart_3d_feed`

## Frecuencia y puja (recomendado)

- Frecuencia objetivo: 1.5–2.5 impresiones/día
- Cap sugerido: 10 impresiones / 7 días
- Presupuesto por ventana: 50% (3d) / 30% (7d) / 20% (14d)
- Estrategia:
  - Placement: Advantage+ ON (limita solo si hay creative issues)
  - Puja: Costo más bajo; opcional bid cap en cohortes 3d de alto gasto
  - Creatives: rota 2–3 variantes por ad set (evita fatiga)

## Reglas de parada y escala (72 h)

- Pausar si:
  - CTR link < 0.7% o
  - CVR < 3% (post-click) con ≥200 clics
- Iterar si:
  - CTR alto (≥1.2%) y CVR bajo → revisar LP/congruencia/checkout
- Escalar si:
  - CTR ≥ 1.2% y CVR ≥ 4–6% → duplica presupuesto 1.5–2× y lleva la variante a 9:16

## Plantillas de nombres (consistencia)

- Campaña: `[producto]_cart_[3d|7d|14d]_[yyyy-mm]`
- Ad set: `[pais]_[audiencia]_[ventana]_[placement]`
- Ad: `[h1]_[cta]_[fondo]_v01` (debe coincidir con `utm_content` y filename)

## Notas DCO/Asset Customization

- Feed DCO debe incluir: `landing_url,h1,cta,fondo,utm_*` y `alt_text`
- `utm_content` = `h1_..._cta_..._fondo_...` (exacto al ad name y filename)
- Verifica en GA4 `manualAdContent` y `sessionCampaign` para lectura por variante

---

## LinkedIn Ads (InMail, Sponsored Content, Message Ads)

Campos sugeridos:
- utm_source: `linkedin`
- utm_medium: `cpc` | `inmail` | `message_ads`
- utm_campaign: `[producto]_[objetivo]_linkedin_[yyyy-mm]`
- utm_content: `[formato]_[ángulo]_[cta]_vN` (ej. `sponsored_beneficio_cta_demo_v2`)
- utm_term (opcional): `[audiencia|rol|region]` (ej. `cmo_mx`)

Ejemplos:
```
https://tusitio.com/demo?utm_source=linkedin&utm_medium=inmail&utm_campaign=saasia_demo_linkedin_2025-11&utm_content=inmail_beneficio_cta_demo_v1&utm_term=cmo_mx

https://tusitio.com/ebook?utm_source=linkedin&utm_medium=cpc&utm_campaign=cursoia_leads_linkedin_2025-11&utm_content=sponsored_socialproof_cta_descarga_v3&utm_term=ops_latam
```

Reglas rápidas:
- Usa `utm_medium=inmail` para InMail/Message Ads; `cpc` para Sponsored Content.
- Mantén `utm_content` mapeado al nombre de anuncio/creativa exportada.

---

## Google Ads (Search y Performance Max)

Campos sugeridos:
- utm_source: `google`
- utm_medium: `cpc`
- utm_campaign: `[producto]_[objetivo]_[search|pmax]_[yyyy-mm]`
- utm_content: `rsas_vN` | `assetgroup_vN` | `landing_A|B`
- utm_term: keyword o etiqueta de grupo: `kw_{palabra}` | `ag_{grupo}`

Ejemplos:
```
https://tusitio.com/landing?utm_source=google&utm_medium=cpc&utm_campaign=saasia_demo_search_2025-11&utm_content=rsas_v2&utm_term=kw_saas_marketing

https://tusitio.com/curso?utm_source=google&utm_medium=cpc&utm_campaign=cursoia_leads_pmax_2025-11&utm_content=assetgroup_v1&utm_term=ag_general
```

Sugerencias:
- En Search, usa `utm_term` para la keyword (match normalizado), o usa plantillas ValueTrack además de UTMs.
- En PMAX, `utm_content` por Asset Group ayuda a discriminar performance por grupo.

---

## GA4 Checklist paso a paso (de UTMs a decisiones)

1) Verifica datos entrantes
- Acquisition → Traffic acquisition: añade `Session source/medium` + `Session campaign`.
- Agrega `Session manual ad content` (utm_content) y filtra por campaña.

2) Crea segmentos por campaña/variante
- Segmento A: `utm_campaign=...2025-11`
- Segmento B: `utm_campaign=...2025-11` + `utm_content=beneficio_v1`
- Compara CTR de botón (evento `click`/`generate_lead`) y tasa de conversión.

3) Define eventos clave y parámetros
- Asegura `generate_lead`, `purchase`, `view_item`, `sign_up` con parámetros (`value`, `currency`).
- Crea métricas derivadas (ratio de conversión por `utm_content`).

4) Alertas de anomalías
- Crea exploración con líneas de tiempo y set de alertas (via Looker Studio/BigQuery si aplica) para caídas de CTR/conversion.

5) Reporte recurrente
- Dashboard semanal por `utm_campaign` y `utm_content`: impresiones, sesiones, CTR, CVR, CPA, ROAS (si hay ingresos).

Plantillas útiles (Sheets):
```
=IFERROR(Sessions_with_campaign/Sessions_total,0)
=IFERROR(Leads/Sessions,0)
=IFERROR(Revenue/Cost,0)
```

---

## Anexos — Diccionario rápido de campos
- utm_source: origen del tráfico (plataforma/canal)
- utm_medium: tipo de medio/placement (email, cpc, reel, feed, dm, remarketing)
- utm_campaign: identificador de campaña versionado por mes
- utm_content: variante creativa/ángulo/versión
- utm_term: keyword/segmento/audiencia (opcional)

---

## Calendario de campañas (plantilla CSV)

Campos sugeridos:
```
fecha_inicio,fecha_fin,producto,objetivo,canal,owner,utm_campaign,nota
```
Ejemplo:
```
2025-11-01,2025-11-30,saasia,demo,instagram,adan,saasia_demo_ig_2025-11,lanzamiento features Q4
2025-11-05,2025-11-20,cursoia,registro,email,adan,cursoia_registro_email_2025-11,black week
2025-11-10,2025-11-24,iabulk,demo,meta,adan,iabulk_tof_meta_2025-11,TOF + MOF secuencia
```

Recomendaciones:
- Una fila por campaña activa, versionada por mes.
- `owner` único; definir rotaciones en notas.
- Enlaza a `SHORTLINKS_UTM_SAMPLE.csv` para variantes por canal.

---

## Librería de ángulos (utm_content) por canal

- Instagram Feed
  - `hero_vN`, `beneficio_vN`, `socialproof_vN`, `resultado_vN`
- Reels/Stories
  - `progressbar_vN`, `antes_despues_vN`, `testimonio_vN`, `countdown_vN`
- Email
  - `cta_primary`, `asuntoA`, `asuntoB`, `oferta_vN`
- Meta Ads
  - `beneficio_reel_cta_primary`, `proceso_carousel_cta_demo`, `urgencia_static_cta_trial`
- Google
  - `rsas_vN` (Search), `assetgroup_{tema}_vN` (PMAX)

Notas:
- Mantén consistencia entre `utm_content`, nombre de ad y filename exportado.
- Usa sufijos `_es`/`_en` si operas bilingüe.

---

## Parsers y fórmulas (UTM/email/eid)

### Google Sheets — extraer parámetro de URL (función genérica)
```
=IFERROR(REGEXEXTRACT(A2, "[?&]" & B2 & "=([^&#]+)"), "")
```
- A2: URL completa
- B2: nombre del parámetro (ej. `utm_source`, `email`, `eid`)

Atajos:
- `utm_source`: `=IFERROR(REGEXEXTRACT(A2, "[?&]utm_source=([^&#]+)"), "")`
- `utm_medium`: `=IFERROR(REGEXEXTRACT(A2, "[?&]utm_medium=([^&#]+)"), "")`
- `utm_campaign`: `=IFERROR(REGEXEXTRACT(A2, "[?&]utm_campaign=([^&#]+)"), "")`
- `utm_content`: `=IFERROR(REGEXEXTRACT(A2, "[?&]utm_content=([^&#]+)"), "")`
- `utm_term`: `=IFERROR(REGEXEXTRACT(A2, "[?&]utm_term=([^&#]+)"), "")`
- `email`: `=IFERROR(REGEXEXTRACT(A2, "[?&]email=([^&#]+)"), "")`
- `eid`: `=IFERROR(REGEXEXTRACT(A2, "[?&]eid=([^&#]+)"), "")`

Decodificar `%` (URL decode básico):
```
=SUBSTITUTE(SUBSTITUTE(SUBSTITUTE(B2, "%40", "@"), "+", " "), "%2F", "/")
```

### Regex (Make/Zapier/Backend) — patrón UTM/email genérico
```
utm_source=([^&#]+)|utm_medium=([^&#]+)|utm_campaign=([^&#]+)|utm_content=([^&#]+)|utm_term=([^&#]+)|email=([^&#]+)|eid=([^&#]+)
```

### Notas
- Si no hay UTMs, estandariza `utm_source=direct` y `utm_medium=none`.
- Para `eid` cifrado, resuélvelo en backend y mapea a contacto antes de actualizar `last_utm_*`.

---

## Templates de Instagram con UTMs (integración)

### Template "Antes/Después" (`instagram_antes_despues_template.svg`)

**Cómo usar el template con tracking**:

1. **Editar URL del CTA en el SVG**:
   - Busca el elemento con ID `cta-link` o `urlCTA`
   - Añade UTMs a la URL base:
     ```
     https://tusitio.com/landing?
       utm_source=instagram&
       utm_medium=feed&
       utm_campaign=cursoia_resultados_ig_2025-11&
       utm_content=antes_despues_v1&
       utm_term=mx_buyer
     ```

2. **Naming del archivo exportado**:
   - Formato: `antes_despues_v1_ig_2025-11-30.png`
   - Coincide con `utm_content=antes_despues_v1`

3. **Publicar en Instagram**:
   - Post principal: URL con UTMs en bio (si usas link único) o en primera comentario
   - Stories: Sticker "Más información" con URL + UTMs
   - Reels: Descripción con link + UTMs cortos

### Generación automática de URLs con UTMs (script)

```javascript
// generate_ig_url.js
function generateIGURL(template, version, date) {
  const baseURL = 'https://tusitio.com/landing';
  const utms = {
    utm_source: 'instagram',
    utm_medium: 'feed',
    utm_campaign: `cursoia_resultados_ig_${date.slice(0,7)}`,
    utm_content: `${template}_v${version}`,
    utm_term: 'mx_buyer'
  };
  
  const params = new URLSearchParams(utms);
  return `${baseURL}?${params.toString()}`;
}

// Uso:
// const url = generateIGURL('antes_despues', 1, '2025-11-30');
// console.log(url);
```

### CSV para batch de posts Instagram (con UTMs)

```csv
fecha,plantilla,version,producto,url_base,utm_campaign,utm_content,utm_term,filename
2025-11-30,antes_despues,1,cursoia,https://tusitio.com/landing,cursoia_resultados_ig_2025-11,antes_despues_v1,mx_buyer,antes_despues_v1_ig_2025-11-30.png
2025-12-01,testimonio,2,saasia,https://tusitio.com/landing,saasia_demo_ig_2025-11,testimonio_v2,co_cmo,testimonio_v2_ig_2025-12-01.png
```

**Fórmula Sheets para generar URL completa**:
```
=LOWER(A2&"?utm_source=instagram&utm_medium=feed&utm_campaign="&F2&"&utm_content="&G2&IF(H2<>"","&utm_term="&H2,""))
```

### Checklist antes de publicar

- [ ] URL del template SVG actualizada con UTMs completos
- [ ] Nombre del archivo exportado coincide con `utm_content`
- [ ] URL añadida en primera comentario o bio (si aplica)
- [ ] Stories: Sticker con URL + UTMs
- [ ] Captura de pantalla del post guardada con nombre `{utm_content}_{fecha}.jpg`
- [ ] Anotado en calendario editorial con `utm_campaign` para tracking

---

## Workflow completo: Template → Post → Tracking

1. **Preparar template** (`instagram_antes_despues_template.svg`)
   - Editar contenido (antes/después, CTA)
   - Actualizar URL con UTMs
   - Exportar PNG 1080×1350 px

2. **Publicar en Instagram**
   - Post: imagen + caption
   - Primera comentario: URL con UTMs (si no en bio)
   - Stories: sticker con URL

3. **Tracking automático**
   - Usuario hace clic → URL con UTMs
   - `utm_capture.js` guarda en localStorage
   - Formulario → CRM con `utm_content=antes_despues_v1`

4. **Reporte**
   - GA4: Sessions por `utm_content`
   - CRM: Leads por `utm_content`
   - Dashboard: ROI por tipo de template (`antes_despues`, `testimonio`, etc.)

---
