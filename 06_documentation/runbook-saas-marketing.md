# Runbook — SaaS IA Marketing

## P0 — Suspensiones erróneas
- Síntomas: cuentas activas suspendidas
- Acciones:
  1. Apagar feature flag /suspend
  2. Revertir últimos N casos y avisar a clientes críticos
  3. Validar eventos Stripe vs CRM
  4. Postmortem y parche de verificación doble

## P1 — Fallos masivos de dunning
- Síntomas: tasa de recuperación cae abruptamente
- Acciones:
  1. Pausar serie en Customer.io/HubSpot
  2. Revisar webhooks Stripe y reintentos
  3. Reencolar pagos fallidos
  4. Informe en 24h

## Validaciones rápidas
- Eventos Stripe on (charge.failed, invoice.payment_succeeded)
- Flags activos y credenciales válidas

## Contactos
- Responsable: RevOps
- Aprobador: Head of Growth

