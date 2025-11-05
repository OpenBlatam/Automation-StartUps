# ✅ JSON Schemas para CSVs (Validación)

## DM_Variants_Master (campos requeridos)
```
{
  "required": [
    "id","dm_type","language","tone","niche","hook","benefit","proof","scarcity",
    "cta","cta_keyword","link_base","utm_campaign","merge_first_name","cta_group","cta_text"
  ]
}
```

## DM_Variants_Short
```
{
  "required": ["id","offer","niche","language","text","cta","link_base","utm_campaign"]
}
```

## KPIs_Dashboard_Template
```
{
  "required": ["fecha","canal","oferta","nicho","idioma","variant_id","envios","respuestas","clicks","agendas","asistencias","ventas"]
}
```

## CTA_Experimentos_Log
```
{
  "required": ["fecha","variant_id","cta_group","cta_text","envios","respuestas","clicks"]
}
```
