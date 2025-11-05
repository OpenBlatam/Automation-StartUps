# UTM Auto-Generator (Excel / Google Sheets)

Base: `CRM_OUTREACH_FIELDS.csv` con columnas clave: source, medium, campaign, content, term, final_url.

## Google Sheets

### Fórmulas (suponiendo encabezados en fila 1)
- slugify simple (espacios → guiones):
```
=LOWER(SUBSTITUTE(A2," ","-"))
```
- campaign (según producto):
```
=IF($L2="curso","curso-ia", IF($L2="saas","saas-ia-marketing", IF($L2="bulk","ia-bulk-docs","otros")))
```
- content (según dm_version):
```
=SWITCH($M2, "v1","v1-equipo","v2","v2-roi","v3","v3-personalizacion","v4","v4-automatizacion","v5","v5-competencia","v6","v6-poc","v7","v7-enterprise","otros")
```
- UTM URL completa:
```
=$Q2 & IF(FIND("?",$Q2),"&","?") & "utm_source=" & $G2 & "&utm_medium=" & $H2 & "&utm_campaign=" & [campaña] & "&utm_content=" & [content] & "&utm_term=" & $F2
```
Reemplaza [campaña] y [content] por las celdas con las fórmulas previas.

## Excel

- Usa funciones equivalentes: LOWER, SUBSTITUTE, IF, SWITCH (o CHOOSE/MATCH según versión)
- Construcción de URL similar concatenando con &

## Buenas prácticas
- Evita espacios, usa snake/kebab-case
- Valida con un validador UTM antes de enviar
- Versiona cambios en `UTM_GUIDE_OUTREACH.md`
- Añade columna `short_url` tras acortador (ej: Bitly, Rebrandly)

## Mapeos sugeridos
- source: linkedin/email/whatsapp
- medium: dm/followup1/followup2/followup3
- campaign: curso-ia/saas-ia-marketing/ia-bulk-docs
- content: v1-equipo/v2-roi/v3-personalizacion/v4-automatizacion/v5-competencia/v6-poc/v7-enterprise
- term: industria (saas, ecommerce, fintech, etc.)
