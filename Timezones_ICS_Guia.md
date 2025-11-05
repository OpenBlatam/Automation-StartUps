# 🌍 Zonas Horarias en ICS

## Reglas
- Trabajar en UTC en `DTSTART/DTEND`
- Mostrar hora local en el DM/Email
- Confirmar zona: "¿Hora local de [Ciudad]?"

## Conversión rápida (ejemplos)
- CDMX (UTC-6 a -5) → 15:00 UTC = 09:00 CDMX
- Bogotá/Lima (UTC-5) → 15:00 UTC = 10:00 local
- Buenos Aires (UTC-3) → 15:00 UTC = 12:00 local
- Madrid (UTC+1 a +2) → 15:00 UTC = 16:00-17:00 local

## ICS ejemplo UTC
```
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20251101T150000Z
DTEND:20251101T160000Z
SUMMARY:Demo SaaS IA
DESCRIPTION:Zoom: https://zoom.us/j/XXXX\nNotas: llega 5 min antes
LOCATION:Online
END:VEVENT
END:VCALENDAR
```

## Plantilla de mensaje con hora local
```
Confirmado: [DÍA] [HORA LOCAL] ([CIUDAD]). Te adjunto .ics y link: [LINK]
```
