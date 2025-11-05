# Looker (LookML) — Starter Guide

Objetivo: definir modelos/vistas base para KPIs de marketing.

Estructura recomendada:
- Model: marketing.model.lkml (conexión DW)  
- Views: fact_marketing.view.lkml, dim_campaign.view.lkml, dim_channel.view.lkml  
- Explores: marketing_performance (join de facts y dims)

Buenas prácticas:
- Definir medidas (sum spend, sum clicks, sum conversions, sum revenue) y derivadas (ctr, cpc, cvr, cpa, roas, mer).  
- Usar timezone consistente y campos de fecha particionados.  
- Permisos por rol: ejecutivo (explore readonly), táctico (explore + filtros), data (edit).  

Deploy:
1) Conectar a repositorio Git del proyecto.  
2) Validar LookML y probar explores.  
3) Publicar dashboards según blueprints.  

Notas:
- Mantener diccionario de datos sincronizado con vistas (nombres y definiciones).  
- Versionar cambios; registrar en changelog de datos.
