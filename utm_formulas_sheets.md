# 🔗 Fórmulas UTM en Google Sheets

Suponiendo columnas:
- A: base_url
- B: utm_source, C: utm_medium, D: utm_campaign, E: utm_content, F: utm_term, G: lead_id

## Construir URL final
```excel
=LET(
  base,A2,
  qs, TEXTJOIN("&", TRUE,
    IF(B2<>"","utm_source="&ENCODEURL(B2),""),
    IF(C2<>"","utm_medium="&ENCODEURL(C2),""),
    IF(D2<>"","utm_campaign="&ENCODEURL(D2),""),
    IF(E2<>"","utm_content="&ENCODEURL(E2),""),
    IF(F2<>"","utm_term="&ENCODEURL(F2),""),
    IF(G2<>"","lead_id="&ENCODEURL(G2),"")
  ),
  base & IF(REGEXMATCH(base, "\\?"), IF(qs<>"","&"&qs,""), IF(qs<>"","?"&qs,""))
)
```

## Validación rápida (0–1)
```excel
=IF(AND(A2<>"",B2<>"",C2<>"",D2<>""),1,0)
```

Tip: Usa `DATA > Data validation` con listas para `utm_source/medium` y patrón para `lead_id`.

