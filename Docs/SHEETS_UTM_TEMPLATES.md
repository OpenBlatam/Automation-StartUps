# Plantillas Google Sheets para UTMs (Listas para copiar)

## 1) Estructura de columnas sugerida
```
A: base_url
B: utm_source
C: utm_medium
D: utm_campaign
E: utm_content
F: utm_term (opcional)
G: final_url (fórmula)
H: validación (fórmula)
```

## 2) Fórmulas
- Generar URL final (incluye `utm_term` si existe):
```
=LOWER(A2&"?utm_source="&B2&"&utm_medium="&C2&"&utm_campaign="&D2&"&utm_content="&E2&IF(LEN(F2)>0,"&utm_term="&F2,""))
```
- Normalizar texto (minúsculas y `_`):
```
=LOWER(SUBSTITUTE(A2," ","_"))
```
- Validación básica (marca error si hay mayúsculas/espacios en campaign/content/term):
```
=IF(OR(REGEXMATCH(D2,"[A-Z ]"),REGEXMATCH(E2,"[A-Z ]"),REGEXMATCH(F2,"[A-Z ]")),"ERROR: usa_minúsculas_sin_espacios","OK")
```
- Relleno automático (ArrayFormula) desde fila 2:
```
=ARRAYFORMULA(IF(ROW(A:A)=1,"final_url",IF(A:A="","",LOWER(A:A&"?utm_source="&B:B&"&utm_medium="&C:C&"&utm_campaign="&D:D&"&utm_content="&E:E&IF(LEN(F:F)>0,"&utm_term="&F:F,""))))))
```

## 3) Validaciones de datos (menús desplegables)
- `utm_source`: lista sugerida → `instagram,facebook,linkedin_inmail,linkedin_connection,email,whatsapp,google,meta`
- `utm_medium`: lista sugerida → `feed,reel,story,email,dm,cpc,remarketing,offline`
- `utm_campaign`: patrón → `[producto]_[canal]_[objetivo]_[yyyy-mm]`
- `utm_content`: patrón → `angulo|cta|slide|hook|vN`

## 4) Ejemplo listo para copiar (CSV)
```
base_url,utm_source,utm_medium,utm_campaign,utm_content,utm_term
https://tusitio.com/landing,instagram,feed,saasia_demo_ig_2025-11,beneficio_v1,
https://tusitio.com/curso,email,email,cursoia_registro_email_2025-11,cta_primary,
https://tusitio.com/docs,instagram,reel,iabulk_demo_ig_2025-11,progressbar_v1,mx_buyer
```

## 5) Sugerencias
- Versiona campañas por mes (yyyy-mm).
- Usa pestañas separadas para orgánico vs. ads.
- Congela la fila 1 y dá colores a columnas calculadas.



