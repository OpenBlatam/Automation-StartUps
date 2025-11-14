## Biblioteca de Filtros y Expresiones (Make/Zapier/Sheets)

### 1) Regex de Intención (ES/EN/PT)
- Opt-out: `(?i)\b(baja|stop|unsubscribe|remove|retire|nao quero|sair)\b`
- Interés: `(?i)\b(si|sí|ok|agenda|book|link|demo|quiero|top|vamo?s)\b`
- Objeción Precio: `(?i)\b(precio|cost|car(o|a)|budget|presupuesto)\b`
- No ahora: `(?i)\b(luego|despu[eé]s|pr[oó]xima semana|not now|mais tarde)\b`

### 2) Filtros Make (Routers)
- Filtro Opt-out: Text matches regex → patrón Opt-out
- Filtro Interés: Text matches regex → patrón Interés
- Filtro Objección: Text matches regex → patrón Objeción Precio
- Filtro No ahora: Text matches regex → patrón No ahora

### 3) Rate-limit (Make)
- Variable: `desired_rate_per_hour` (IG nueva=4, madura=8)
- Sleep por item: `rand(30;60)` segundos
- Si `hourly_usage >= cap` → Sleep `rand(120;180)`

### 4) Zapier (Filtros y Storage)
- Filter: Text contains (case-insensitive) para Opt-out/Interés
- Storage by Zap (KV): keys `rate_usage:{account_id}:{YYYYMMDDHH}`
- Incremento seguro: lee → +1 → escribe con TTL=3600s

### 5) Búsqueda CSV (Make)
- CSV: `DM_Variants_Master.csv`
- Filtro: `language == msg.lang AND niche == lead.niche AND cta_group IN (A,B)`
- Rotación CTA: usa `Storage`/`Data Store` contador por `cta_group`

### 6) Google Sheets (Formulas útiles)
- Normalizar texto: `=LOWER(SUBSTITUTE(A2;"\n";" "))`
- Extraer idioma: `=IF(REGEXMATCH(A2;"(?i)\b(usted|vos|che)\b");"ES";IF(REGEXMATCH(A2;"(?i)\b(você|vc)\b");"PT";"EN"))`
- Clasificar intención: `=IFS(REGEXMATCH(A2;"(?i)\b(baja|stop|unsubscribe)\b");"optout"; REGEXMATCH(A2;"(?i)\b(agenda|book|demo)\b");"interes"; REGEXMATCH(A2;"(?i)\b(precio|cost|budget)\b");"objecion"; TRUE;"otros")`
- UTM Builder: `=LOWER(CONCAT("?utm_source=ig&utm_medium=dm&utm_campaign=";C2;"&utm_content=";D2))`

### 7) Composición de Mensajes
- Plantilla larga: "{{hook}} {{benefit}} {{proof}} {{scarcity}} {{cta_text}}"
- Ultra-corta: "{{benefit}} → {{cta_text}}"
- Guardas: `LEN(msg) <= 220` (2 líneas) o `<= 140` ultra-corto

### 8) Mapas de Campos (CRM)
- `{{first_name}}` → `contact.firstName`
- `{{company}}` → `company.name`
- `{{industry}}` → `company.industry`
- `{{link}}` → `deal.demoLink`

### 9) Clasificador (Buckets)
- Labels: `optout | interes | objecion_precio | no_ahora | otros`
- Confianza: `score = (#coincidencias)/(#patrones evaluados)`

### 10) QA Expresiones
- Doble espacio: `\s{2,}` → reemplazar por ` `
- Links rotos: `(?i)https?://[^\s]+` + test HTTP 200

