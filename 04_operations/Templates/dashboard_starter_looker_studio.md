# Looker Studio — Starter Guide

Objetivo: publicar dashboards ejecutivo/táctico/canal con fuentes estándar.

Conectores:
- Google Ads / Google Analytics 4 / BigQuery / CSV subidas

Pasos:
1) Crear fuente(s) de datos con campos normalizados (ver data_dictionary.csv).  
2) Duplicar layout según blueprint (executive/tactical/channel).  
3) Mapear métricas/dimensiones y verificar filtros/segmentos.  
4) Configurar controles de fecha, canal, campaña, país.  
5) Añadir alertas por umbrales (Data Source/Community viz o Alternativa).  
6) Compartir con RBAC (solo lectura para ejecutivos, edición para owners).  

Notas:
- Usar vistas materializadas/BigQuery para rendimiento.  
- Documentar cálculo de KPIs en el panel (tooltip/notas).
