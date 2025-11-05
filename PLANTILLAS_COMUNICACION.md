# Plantillas de Comunicación (Email/SMS/WhatsApp)

## Webinar

### Confirmación (Email)
Asunto: Confirmado: {TITULO} — {FECHA/HORA}
Cuerpo:
Hola {NOMBRE},
Tu registro está confirmado.
Enlace: {LINK_ZOOM}
Añadir al calendario: {LINK_CALENDAR}
Nos vemos,
{MARCA}

### Recordatorio 24h (Email)
Asunto: Mañana: {TITULO}
Cuerpo:
Hola {NOMBRE},
Comenzamos mañana a las {HORA}. Enlace: {LINK_ZOOM}
Agenda aquí: {LINK_CALENDAR}
Si no puedes, recibirás el replay.

### Recordatorio 1h (WhatsApp/SMS)
Texto:
En 1h iniciamos {TITULO}. Únete: {LINK_ZOOM}. Soporte: {CONTACTO}.

### Replay + CTA (Email)
Asunto: Replay + recursos de {TITULO}
Cuerpo:
Gracias por asistir.
Grabación: {LINK_REPLAY}
Slides: {LINK_SLIDES}
Oferta/CTA: {CTA_LINK}
Disponible hasta: {FECHA_LIMITE}

## Dunning (Pagos)

### Pago fallido (Email 1)
Asunto: Acción requerida: método de pago
Cuerpo:
Hola {NOMBRE},
No pudimos procesar tu pago de {MONTO}. Actualiza tu método aquí: {LINK_BILLING}.
Reintentaremos en 48h.

### Pago fallido (Email 2)
Asunto: Último intento de cobro
Cuerpo:
Seguimos sin poder cobrar {MONTO}. Si no actualizas en 24h, podríamos suspender el servicio.
Actualizar: {LINK_BILLING}

### Suspensión (Email)
Asunto: Cuenta suspendida temporalmente
Cuerpo:
Tu cuenta fue suspendida por pagos fallidos. Reactívala aquí: {LINK_BILLING}. Soporte: {CONTACTO}.

### Reactivación (Email)
Asunto: ¡Listo! Tu cuenta fue reactivada
Cuerpo:
Gracias por actualizar. Tu acceso está activo nuevamente.

## Soporte IA (Auto-respuestas)

### FAQ/How-to (con confianza alta)
Asunto: Respuesta a tu consulta: {TEMA}
Cuerpo:
Estos son los pasos para {ACCION}:
1) ...
2) ...
3) ...
Más detalles: {LINK_KB}

### Fallback a agente (confianza baja)
Asunto: Hemos derivado tu caso
Cuerpo:
Derivamos tu caso a un agente. Tiempo estimado: {SLA_MIN} min. ID: {TICKET_ID}.

## Notas
- Mantener DKIM/SPF/DMARC configurados.
- Personalizar variables {ASÍ} desde Zapier/Apps Script.
