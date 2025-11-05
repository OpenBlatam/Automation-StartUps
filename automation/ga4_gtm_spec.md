# GA4 / GTM – Especificación de Eventos

Eventos GA4 (recommended naming)
- lead_magnet_submit
  - params: product (curso/saas/bulk), campaign, source, medium
- tripwire_checkout_view / tripwire_purchase
  - params: product, price, currency, coupon
- core_checkout_view / core_purchase
  - params: product, price, currency
- demo_booked
  - params: product, channel (li/email/wa), date
- webinar_register / webinar_attend
  - params: title, date, duration_min

GTM – Triggers
- Form Submit (LM) → matches CSS selector/form id de landing
- Purchase (Stripe) → webhook/thankyou url path contains “success” + dataLayer push
- Button Clicks → CTA buttons with data-cta attributes (lm/tripwire/core/demo)
- Custom Event → dataLayer.push({event: 'demo_booked', ...})

GTM – Tags (GA4 Configuration + GA4 Events)
- GA4 Config: MEASUREMENT_ID = G-XXXXXXXXXX
- GA4 Event: lead_magnet_submit (trigger: Form Submit LM)
- GA4 Event: tripwire_purchase (trigger: Purchase Success)
- GA4 Event: core_purchase (trigger: Purchase Success core)
- GA4 Event: demo_booked (trigger: Custom Event)
- GA4 Event: webinar_register / webinar_attend (triggers correspondientes)

DataLayer ejemplos
```js
dataLayer.push({
  event: 'lead_magnet_submit',
  product: 'curso', source: 'li', medium: 'dm', campaign: 'curso_lm_a_v1'
});

dataLayer.push({
  event: 'tripwire_purchase', product: 'saas', price: 27, currency: 'USD', coupon: ''
});

dataLayer.push({
  event: 'demo_booked', product: 'bulk', channel: 'email', date: '2025-11-02T15:00:00Z'
});
```

Validación
- Realtime GA4: verificar recepción de eventos y params
- DebugView GTM: confirmar disparo de triggers/tags
