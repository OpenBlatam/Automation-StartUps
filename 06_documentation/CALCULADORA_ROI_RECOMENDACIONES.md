# Calculadora ROI de Recomendaciones Personalizadas

Objetivo: estimar ROI operativo y de ingresos para un piloto de 8 semanas y proyección a 12 meses.

## 1) Variables clave
- Tráfico mensual (T)
- Tasa de conversión base (CR0)
- Ticket promedio (AOV)
- Margen bruto (GM)
- Porcentaje de sesiones con recomendaciones (COV)
- Uplift en CR por recomendaciones (ΔCR)
- Uplift en AOV (ΔAOV)
- Coste mensual de la solución (COST)
- Coste de implementación (CAPEX)

## 2) Fórmulas
- Conversiones base = T × CR0
- Conversiones con recs = T × COV × (CR0 × (1 + ΔCR)) + T × (1 - COV) × CR0
- Ingreso base = Conversiones base × AOV
- Ingreso con recs = Conversiones con recs × (AOV × (1 + ΔAOV))
- Ingreso incremental = Ingreso con recs − Ingreso base
- Margen incremental = Ingreso incremental × GM
- ROI mensual = (Margen incremental − COST) ÷ COST
- Payback (meses) = CAPEX ÷ max(Margen incremental − COST, 1)

## 3) Escenarios de ejemplo
- Pequeño: T=100k, CR0=1.5%, AOV=$45, GM=60%, COV=40%, ΔCR=+12%, ΔAOV=+4%, COST=$1,500, CAPEX=$3,000
- Mediano: T=500k, CR0=2.0%, AOV=$60, GM=55%, COV=60%, ΔCR=+15%, ΔAOV=+5%, COST=$6,000, CAPEX=$8,000
- Grande: T=2M, CR0=2.2%, AOV=$75, GM=50%, COV=70%, ΔCR=+18%, ΔAOV=+6%, COST=$18,000, CAPEX=$20,000

## 4) Proyección 12 meses
- Considerar degradación del uplift (-10% relativo cada 6 meses) y estacionalidad.
- Re-entrenos trimestrales para mantener ΔCR y ΔAOV.

## 5) Sensibilidades
- Sensible a COV y ΔCR: priorizar colocación de widgets y relevancia.
- AOV afecta doble vía: cross-sell y bundles.

## 6) Plantilla
- CSV listo: `calculadora_roi_recomendaciones.csv` (importar en Sheets y usar HOY())

## 7) Buenas prácticas
- Empezar con 1-2 posiciones de recomendación y expandir.
- Medir por segmento (tráfico nuevo vs recurrente, mobile vs desktop).
- Ejecutar A/B con retención de cookies mínima de 14 días.

