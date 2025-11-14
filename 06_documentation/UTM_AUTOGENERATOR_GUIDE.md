---
title: "UTM Auto‑Generator Guide (Sheets/Excel)"
category: "tracking"
tags: ["utm","generator","sheets","excel","tracking"]
created: "2025-10-29"
path: "UTM_AUTOGENERATOR_GUIDE.md"
slug: "utm-autogenerator-guide"
language: "es"
scope: "utm_generator"
---

# UTM Auto‑Generator Guide (Sheets/Excel)

Fórmulas listas para generar UTMs consistentes desde columnas de una hoja.

---

## Columnas Recomendadas (A→H)
- A: base_url (ej: https://tusitio.com/demo)
- B: producto (curso_ia | saas_marketing | bulk_docs)
- C: canal (linkedin_inmail | linkedin_connection | email)
- D: objetivo (demo | lead | conversion)
- E: fecha_mes (YYYY-MM)
- F: version_dm (vip | roi | equipo | innovacion | resistente | estandar)
- G: industria (saas | ecommerce | fintech | health | education | general)
- H: term (rol_pais, ej: cmo_mexico)

---

## Convenciones Automáticas
- utm_campaign = `[producto]_[canal]_[objetivo]_[fecha_mes]`
- utm_content = `[version_dm]_[industria]`
- utm_term = `H` (tal cual)
- utm_source = `canal`
- utm_medium = if(canal comienza con "linkedin", "social", "email")

---

## Fórmulas (Google Sheets)

### 1) utm_medium (columna I)
```
=IF(LEFT(C2,8)="linkedin","social","email")
```

### 2) utm_campaign (columna J)
```
=LOWER(B2 & "_" & C2 & "_" & D2 & "_" & E2)
```

### 3) utm_content (columna K)
```
=LOWER(F2 & "_" & G2)
```

### 4) UTM URL final (columna L)
```
=LOWER(A2 & "?utm_source=" & C2 & "&utm_medium=" & I2 & "&utm_campaign=" & J2 & "&utm_content=" & K2 & "&utm_term=" & H2)
```

---

## Fórmulas (Excel)

Nota: Usa `CONCAT` o `&`, y `LOWER` como `LOWER()`.

### 1) utm_medium (columna I)
```
=IF(LEFT(C2,8)="linkedin","social","email")
```

### 2) utm_campaign (columna J)
```
=LOWER(B2 & "_" & C2 & "_" & D2 & "_" & E2)
```

### 3) utm_content (columna K)
```
=LOWER(F2 & "_" & G2)
```

### 4) UTM URL final (columna L)
```
=LOWER(A2 & "?utm_source=" & C2 & "&utm_medium=" & I2 & "&utm_campaign=" & J2 & "&utm_content=" & K2 & "&utm_term=" & H2)
```

---

## Ejemplos por Producto/Canal

### SaaS IA Marketing — LinkedIn InMail (demo)
- base_url: https://tusitio.com/demo
- producto: saas_marketing
- canal: linkedin_inmail
- objetivo: demo
- fecha_mes: 2025-10
- version_dm: roi
- industria: saas
- term: cmo_mexico

Resultado (L):
```
https://tusitio.com/demo?utm_source=linkedin_inmail&utm_medium=social&utm_campaign=saas_marketing_linkedin_inmail_demo_2025-10&utm_content=roi_saas&utm_term=cmo_mexico
```

### Curso IA — Email (lead)
- base_url: https://tusitio.com/curso
- producto: curso_ia
- canal: email
- objetivo: lead
- fecha_mes: 2025-10
- version_dm: equipo
- industria: education
- term: coo_espana

Resultado (L):
```
https://tusitio.com/curso?utm_source=email&utm_medium=email&utm_campaign=curso_ia_email_lead_2025-10&utm_content=equipo_education&utm_term=coo_espana
```

### IA Bulk Documentos — LinkedIn Connection (conversion)
- base_url: https://tusitio.com/docs
- producto: bulk_docs
- canal: linkedin_connection
- objetivo: conversion
- fecha_mes: 2025-10
- version_dm: compliance
- industria: fintech
- term: ops_chile

Resultado (L):
```
https://tusitio.com/docs?utm_source=linkedin_connection&utm_medium=social&utm_campaign=bulk_docs_linkedin_connection_conversion_2025-10&utm_content=compliance_fintech&utm_term=ops_chile
```

---

## Buenas Prácticas
- Mantén listas desplegables para columnas B–H.
- Valida con `VALIDADOR_DM.py` si incluyes la UTM en el mensaje.
- Usa `SCRIPT_SHORTLINKS_GENERATOR.py` para shortlinks.

---

## Plantilla CSV sugerida
```
base_url,producto,canal,objetivo,fecha_mes,version_dm,industria,term
https://tusitio.com/demo,saas_marketing,linkedin_inmail,demo,2025-10,roi,saas,cmo_mexico
https://tusitio.com/curso,curso_ia,email,lead,2025-10,equipo,education,coo_espana
https://tusitio.com/docs,bulk_docs,linkedin_connection,conversion,2025-10,compliance,fintech,ops_chile
```

---

## Referencias
- `UTM_GUIDE_OUTREACH.md`
- `KPI_DASHBOARD_TEMPLATE.md`
- `SCRIPT_SHORTLINKS_GENERATOR.py`
