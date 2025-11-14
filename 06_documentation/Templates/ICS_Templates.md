# 🗓️ ICS Templates (Calendario)

## Evento Base (.ics)
```
BEGIN:VCALENDAR
VERSION:2.0
BEGIN:VEVENT
DTSTART:20251101T150000Z
DTEND:20251101T160000Z
SUMMARY:Webinar IA – Ahorra 10+ h/sem
DESCRIPTION:Zoom: https://zoom.us/j/XXXX\nNotas: llega 5 min antes
LOCATION:Online
END:VEVENT
END:VCALENDAR
```

## Variables
- DTSTART/DTEND en UTC
- SUMMARY por oferta
- DESCRIPTION con link + notas

## Uso en automatización
- Generar .ics dinámico (WF2)
- Adjuntar en DM/Email/WA
