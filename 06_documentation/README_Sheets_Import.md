# 📄 Importación a Google Sheets (CSV)

## Paso a paso
1) File → Import → Upload CSV
2) Separator: Detect automatically
3) Locale: Español (o en-US si usar fórmulas con punto)
4) Encoding: UTF-8

## Filtros útiles
- Por `cta_group` (A/B/C)
- Por `niche` y `language`
- Por `variant_status=active`

## Fórmulas
- UTM Builder: ver `UTM_Builder.md`
- KPIs: ver `KPI_Schema_Definitions.md`

## Buenas prácticas
- Proteger columnas de IDs
- Usar Validations para `cta_group` y `tone`
- Vista de filtro por campaña
