# 🔗 UTM Builder (Guía Rápida)

## Campos
- utm_source: instagram | whatsapp | email | linkedin | telegram
- utm_medium: dm | message | story | post | newsletter
- utm_campaign: webinar_ia | saas_demo | iabulk_demo
- utm_content: {{variant_id}}

## Plantilla
```
{{link_base}}?utm_source={{source}}&utm_medium={{medium}}&utm_campaign={{campaign}}&utm_content={{variant_id}}
```

## Google Sheets
```
=CONCAT(B2,"?utm_source=",C2,"&utm_medium=",D2,"&utm_campaign=",E2,"&utm_content=",F2)
```
Donde: B2=link_base, C2=source, D2=medium, E2=campaign, F2=variant_id

## Ejemplos
- Instagram DM curso: `utm_source=instagram&utm_medium=dm&utm_campaign=webinar_ia`
- WhatsApp demo SaaS: `utm_source=whatsapp&utm_medium=message&utm_campaign=saas_demo`
