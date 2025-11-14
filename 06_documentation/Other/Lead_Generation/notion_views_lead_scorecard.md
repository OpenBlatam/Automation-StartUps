---
title: "Notion Views Lead Scorecard"
category: "06_documentation"
tags: []
created: "2025-10-29"
path: "06_documentation/Other/notion_views_lead_scorecard.md"
---

# Vistas y Filtros - Lead Readiness (Notion / Sheets)

Configura estas vistas para priorizar y operar rápido.

## Propiedades sugeridas
- readiness_score (número, 0-100)
- readiness_tier (select: Listo, Prometedor, Nutrir, Baja prioridad)
- suggested_cta (text)
- owner (person/text)
- status (select: ready_to_outreach, contacted, responded, booked, closed, nurture)
- product (select: curso, saas, bulk)
- dm_version (select: v1..v7)
- industry, role_level
- achievement_date (date)

## Notion - Vistas recomendadas

### 1) Kanban por Estado
- Group by: status
- Sort: readiness_score (desc)
- Filters: readiness_score >= 60

### 2) Tabla - Prioridad Alta
- Filter: readiness_tier = "Listo" OR readiness_tier = "Prometedor"
- Sort: readiness_score (desc), achievement_date (desc)
- Columns: full_name, company, readiness_score, readiness_tier, suggested_cta, owner, product, dm_version

### 3) Calendario - Seguimientos
- Calendar by: next_followup_date (añadir propiedad date)
- Filter: status in (contacted, responded)
- Color by: readiness_tier

### 4) Vista por Industria
- Filter: industry = [tu industria]
- Sort: readiness_score (desc)

### 5) Vista por Owner
- Filter: owner = Me
- Sort: readiness_score (desc), status

## Notion - Fórmulas útiles

### readiness_tier (según score)
```
if(prop("readiness_score") >= 80, "Listo",
  if(prop("readiness_score") >= 60, "Prometedor",
    if(prop("readiness_score") >= 40, "Nutrir", "Baja prioridad")
  )
)
```

### suggested_cta
```
if(prop("readiness_score") >= 80, "Demo 15 min / Trial",
  if(prop("readiness_score") >= 60, "Invitación webinar / Demo breve",
    if(prop("readiness_score") >= 40, "Enviar caso 1 pág / Recurso", "Nurture")
  )
)
```

### next_followup_date
```
if(prop("status") == "contacted", dateAdd(now(), 5, "days"),
  if(prop("status") == "responded", dateAdd(now(), 2, "days"),
    if(prop("status") == "booked", dateAdd(now(), 0, "days"),
      dateAdd(now(), 10, "days")
    )
  )
)
```

## Google Sheets - Vistas rápidas

### Filtro por Tier (Listo/Prometedor)
- Crea un filtro personalizado: Column `readiness_tier` in {Listo, Prometedor}
- Ordena por `readiness_score` desc

### Resumen por Industria (Pivot)
- Rows: industry
- Values: AVG `readiness_score`, COUNT leads
- Filter: status in {ready_to_outreach, contacted}

### Resumen por Owner (Pivot)
- Rows: owner
- Values: COUNT leads, AVG score
- Filter: readiness_tier in {Listo, Prometedor}

## Automatización (opcional)
- Si `readiness_tier` = Listo → notificar en Slack/Email al owner
- Si `status` cambia a responded → crear evento de seguimiento
- Si `achievement_date` > 30 días → bajar 1 punto de score automáticamente (regla)
