# Go‑Live 24h – Checklist por horas

T‑24h
- [ ] Congelar cambios mayores en landings/zaps
- [ ] Validar UTM con `automation/utm_taxonomy.csv`
- [ ] Import de muestras `*_sample.csv` en entorno de test

T‑18h
- [ ] Test LM → Email 0 → Task 48h (Zap/Make)
- [ ] Test Webinar reminders (simular T‑24/T‑2/T+1)
- [ ] Test Tripwire purchase (Stripe modo test) → onboarding + oferta Core

T‑12h
- [ ] Cargar emails HTML/TXT en ESP y enviar a lista interna (seed)
- [ ] Revisar rendering móvil/desktop y enlaces
- [ ] Crear vistas CRM (High‑intent, No‑show, Post‑webinar)

T‑8h
- [ ] Publicar landings con parámetros UTM y privacy links
- [ ] Activar blueprints en Zapier/Make (modo ON)
- [ ] Ver logs de 1 envío real (lead interno)

T‑4h
- [ ] Comprobar KPIs en tiempo real (Airtable/Notion vistas)
- [ ] Confirmar inventario de ofertas/checkout y cupones
- [ ] Preparar lista de distribución/reply‑to y soporte

T‑1h
- [ ] Revisar status de todos los Zaps/Scenarios (sin errores)
- [ ] Encender alertas (fallos/no‑show/umbral)
- [ ] Comunicar equipo: canal de war‑room (Slack)

T‑0 (Lanzamiento)
- [ ] Abrir monitor de eventos (Airtable vista “Hoy”)
- [ ] Enviar primer batch a leads seed/piloto
- [ ] Validar conversiones y tiempos (E2E)

T+1–4h
- [ ] Revisar tasas (CVR LM, Open/CTR, compras)
- [ ] Ajustar límites de envío si hay rebotes/spam
- [ ] QA de mensajes con respuestas reales

T+24h
- [ ] Reporte quick‑win (automation/dashboard_kpis.md)
- [ ] Decidir A/B activo según `automation/ab_test_matrix.md`
- [ ] Plan de optimización (siguiente día)

Puntos de reversión (rollback)
- [ ] Pausar Zaps/Scenarios por flujo (LM/Webinar/Tripwire/Demo)
- [ ] Revertir landings a versión previa (guardar backup)
- [ ] Cambiar rutas de checkout a página de espera
