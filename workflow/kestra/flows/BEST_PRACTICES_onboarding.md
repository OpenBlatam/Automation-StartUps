# 🎯 Mejores Prácticas - Employee Onboarding

Guía de mejores prácticas para configurar y operar el flujo de onboarding automatizado.

## 🔒 Seguridad

### Gestión de Secretos

```yaml
# ❌ NO hacer esto
email_api_key: "SG.mi_clave_real_aqui"

# ✅ Hacer esto
email_api_key: "{{ secrets.SENDGRID_API_KEY }}"
```

**Recomendaciones:**
- Usar External Secrets Operator o Vault para gestionar secretos
- Rotar API keys regularmente (cada 90 días)
- Usar secrets de Kubernetes en lugar de variables de entorno en texto plano
- Habilitar verificación HMAC en webhooks HR cuando sea posible

### Validación de Dominios

Agregar validación de dominio corporativo en la fase de validación:

```python
CORPORATE_DOMAINS = ['@empresa.com', '@subsidiaria.com']

def validate_corporate_email(email: str) -> bool:
    return any(email.endswith(domain) for domain in CORPORATE_DOMAINS)
```

## 📊 Monitoreo y Alertas

### Dashboards Recomendados en Grafana

1. **Dashboard de Onboarding en Tiempo Real**
   - Tasa de éxito por departamento
   - Tiempo promedio de onboarding
   - Cuentas creadas vs esperadas
   - Errores por tipo de acción

2. **Dashboard de Compliance**
   - Checklist de compliance por empleado
   - Tareas pendientes de seguimiento
   - Tasa de satisfacción (día 7)

### Alertas Críticas

```yaml
# Prometheus AlertRules
- alert: OnboardingFailureRateHigh
  expr: |
    rate(onboarding_completed_total{status="failed"}[1h]) /
    rate(onboarding_completed_total[1h]) > 0.1
  annotations:
    summary: "Tasa de fallos de onboarding > 10%"

- alert: OnboardingAccountCreationFailed
  expr: onboarding_actions_completed{action="idp_account"} == 0
  for: 5m
  annotations:
    summary: "Falló creación de cuenta IdP"
```

## 🔄 Idempotencia

### Mejores Prácticas

1. **TTL Apropiado**: Usar TTL de 24-48 horas para prevenir duplicados accidentales
2. **Clave Única**: `email:start_date` es suficiente en la mayoría de casos
3. **Base de Datos**: Usar constraints UNIQUE en BD para doble verificación

```sql
-- Verificar antes de insertar
SELECT COUNT(*) FROM employee_onboarding 
WHERE idempotency_key = 'empleado@empresa.com:2025-02-01';
```

## 🎯 Configuración por Ambiente

### Desarrollo

```yaml
enable_account_creation: false  # No crear cuentas reales en dev
enable_hris_lookup: false       # Usar datos stub
enable_db_persistence: true     # Guardar para testing
metrics_enabled: false          # Reducir ruido en métricas
```

### Staging

```yaml
enable_account_creation: true
enable_hris_lookup: true
enable_db_persistence: true
idempotency_ttl_hours: 12      # TTL más corto para testing
```

### Producción

```yaml
enable_account_creation: true
enable_hris_lookup: true
enable_db_persistence: true
idempotency_ttl_hours: 24
metrics_enabled: true
enable_hris_confirmation: true
```

## 📈 Optimización de Performance

### Paralelización

El flujo ya ejecuta acciones en paralelo en la Fase 3. Para optimizar más:

1. **Agrupar tareas relacionadas**: Notificaciones pueden ir juntas
2. **Timeouts apropiados**: 
   - Validación: 1 min
   - Creación de cuentas: 2-3 min
   - Notificaciones: 30 seg
3. **Reintentos**: 2-3 intentos con backoff exponencial

### Base de Datos

```sql
-- Mantener índices actualizados
ANALYZE employee_onboarding;
ANALYZE onboarding_actions;
ANALYZE onboarding_accounts;

-- Limpiar datos antiguos (ejecutar mensualmente)
DELETE FROM onboarding_actions 
WHERE executed_at < NOW() - INTERVAL '1 year';
```

## 🧪 Testing

### Casos de Prueba Recomendados

1. **Validación de Email Inválido**
   ```json
   {"email": "invalid-email", "start_date": "2025-02-01"}
   ```
   Esperado: Error de validación

2. **Idempotencia**
   ```json
   // Ejecutar mismo onboarding 2 veces
   ```
   Esperado: Segunda ejecución falla con mensaje de duplicado

3. **Auto-asignación**
   ```json
   {"employee_email": "x@empresa.com", "manager_email": "x@empresa.com"}
   ```
   Esperado: Error de validación

4. **Fecha Futura Inválida**
   ```json
   {"start_date": "2030-12-31"}
   ```
   Esperado: Error de validación (fuera de rango)

### Testing de Integraciones

```bash
# Test de IdP (usar cuenta de prueba)
curl -X POST $IDP_API_URL/users \
  -H "Authorization: Bearer $IDP_API_KEY" \
  -d '{"email": "test@empresa.com", ...}'

# Test de Slack webhook
curl -X POST $SLACK_WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"text": "Test notification"}'
```

## 📝 Documentación de Errores Comunes

### Error: "Invalid employee email format"

**Causa**: Email no cumple formato RFC 5322
**Solución**: Verificar que el email tenga formato `usuario@dominio.com`

### Error: "Duplicate onboarding run detected"

**Causa**: Ya existe onboarding para ese email y fecha
**Solución**: 
- Verificar en BD: `SELECT * FROM employee_onboarding WHERE idempotency_key = '...'`
- Si es legítimo, cambiar fecha de inicio o email temporalmente
- Si es error, limpiar entrada en BD

### Error: "Failed to create IdP account"

**Causas posibles**:
1. API key inválida o expirada
2. Usuario ya existe en IdP
3. Timeout de red
4. Permisos insuficientes

**Solución**:
1. Verificar credenciales
2. Verificar logs de IdP
3. Revisar timeout configurado
4. Verificar permisos del API key

## 🔄 Mantenimiento

### Tareas Regulares

**Semanal:**
- Revisar métricas de éxito/fallo
- Verificar tareas de seguimiento pendientes
- Revisar alertas de Prometheus

**Mensual:**
- Limpiar datos antiguos de BD (más de 1 año)
- Rotar API keys
- Revisar y actualizar documentación
- Analizar tendencias de onboarding

**Trimestral:**
- Revisar y optimizar queries de BD
- Actualizar integraciones si hay cambios en APIs
- Revisar y mejorar validaciones según feedback

## 🚀 Escalabilidad

### Para Alto Volumen (>100 onboarding/mes)

1. **Base de Datos**:
   - Considerar particionado por fecha
   - Replicación de lectura para dashboards
   - Connection pooling apropiado

2. **Paralelización**:
   - El flujo ya está optimizado
   - Considerar múltiples workers de Kestra si necesario

3. **Rate Limiting**:
   - Implementar rate limiting en webhooks HR
   - Queue para procesamiento en horas pico

## 📚 Recursos Adicionales

- [Documentación Kestra](https://kestra.io/docs)
- [PostgreSQL Best Practices](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Prometheus Metrics Best Practices](https://prometheus.io/docs/practices/naming/)

---

**Última actualización**: 2025-01-20
**Mantenedor**: Equipo de Automatización

