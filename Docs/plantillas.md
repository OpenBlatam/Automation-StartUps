# Plantillas de Priorización y Backlog

## ICE (rápido)
```
Item: <automatización>
Impacto (1-5): <n>
Confianza (1-5): <n>
Esfuerzo (1-5): <n>
ICE = (Impacto × Confianza) ÷ Esfuerzo
Notas:
```

## RICE (más preciso)
```
Item: <automatización>
Alcance (usuarios/mes): <n>
Impacto (0.25/0.5/1/2/3): <n>
Confianza (0-1): <n>
Esfuerzo (persona-meses): <n>
RICE = (Alcance × Impacto × Confianza) ÷ Esfuerzo
Notas:
```

## Backlog (CSV-friendly)
```
item,owner,kpi,impacto,confianza,esfuerzo,ice,alcance,rice,estado,fecha_objetivo
<nombre>,<owner>,<KPI>,<1-5>,<1-5>,<1-5>,<calc>,<n>,<calc>,backlog,AAAA-MM-DD
```

## Definiciones rápidas
- Impacto: magnitud esperada en el KPI seleccionado.
- Confianza: certeza en estimaciones/hipótesis.
- Esfuerzo: costo relativo (tiempo/recursos).
- Alcance: nº de usuarios/objetos afectados en un periodo.



