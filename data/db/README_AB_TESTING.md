# Sistema de A/B Testing Automatizado

Sistema completo para automatizar tests A/B con análisis estadístico avanzado y auto-deployment de versión ganadora.

## Características

- ✅ **Tests de Subject Lines de Emails**: Compara diferentes subject lines para optimizar open rates
- ✅ **Tests de Landing Pages**: Prueba diferentes versiones de landing pages para mejorar conversión
- ✅ **Tests de Precios Dinámicos**: Evalúa diferentes estrategias de precios para maximizar revenue
- ✅ **Tests de CTA Buttons**: Compara diferentes textos, colores y posiciones de CTA buttons
- ✅ **Análisis Estadístico Robusto**: Z-test, confidence intervals, p-values
- ✅ **Auto-deployment**: Implementa automáticamente la versión ganadora cuando alcanza significancia
- ✅ **Power Analysis**: Calcula tamaño de muestra mínimo necesario
- ✅ **Tracking Completo**: Registra todos los eventos y métricas

## Instalación

### 1. Ejecutar Schema SQL

```bash
psql -U postgres -d tu_database -f data/db/ab_testing_schema.sql
```

### 2. Configurar Airflow DAG

El DAG `ab_testing_automation` se ejecuta automáticamente cada 6 horas.

## Uso Rápido

### Crear un Test de Subject Line

```python
from data.airflow.dags.ab_testing_examples import (
    create_email_subject_test,
    activate_test,
)

# Crear test
create_email_subject_test(
    test_id="email_subject_welcome_v1",
    test_name="Welcome Email Subject Line Test",
    variant_a_subject="Welcome to our platform!",
    variant_b_subject="Start your journey today",
)

# Activar test
activate_test("email_subject_welcome_v1")
```

### Usar en Emails

```python
from data.airflow.dags.ab_testing_examples import (
    send_email_with_ab_test,
    track_email_engagement,
)

# Enviar email con A/B testing
send_email_with_ab_test(
    email="user@example.com",
    test_id="email_subject_welcome_v1",
    default_subject="Welcome to our platform",
    body_template="Hello {{name}}, welcome!",
)

# Cuando el usuario abra el email (webhook de email service)
track_email_engagement(
    test_id="email_subject_welcome_v1",
    email="user@example.com",
    event_type="email_opened",
)

# Cuando el usuario haga click
track_email_engagement(
    test_id="email_subject_welcome_v1",
    email="user@example.com",
    event_type="email_clicked",
)
```

### Crear un Test de Landing Page

```python
from data.airflow.dags.ab_testing_examples import create_landing_page_test

create_landing_page_test(
    test_id="landing_page_homepage_v1",
    test_name="Homepage Redesign Test",
    variant_a_config={
        "headline": "Welcome to our platform",
        "subheadline": "Get started today",
        "hero_image": "default.jpg",
        "cta_text": "Sign Up",
        "cta_color": "#007bff",
    },
    variant_b_config={
        "headline": "Transform your business",
        "subheadline": "Join thousands of companies",
        "hero_image": "new.jpg",
        "cta_text": "Start Free Trial",
        "cta_color": "#28a745",
    },
)

activate_test("landing_page_homepage_v1")
```

### Usar en Landing Pages

```python
from data.airflow.dags.ab_testing_examples import (
    render_landing_page_with_ab_test,
    track_landing_page_conversion,
)

# Renderizar landing page con A/B testing
config = render_landing_page_with_ab_test(
    session_id="sess_123",
    test_id="landing_page_homepage_v1",
    default_config={
        "headline": "Welcome",
        "subheadline": "Get started today",
    }
)

# Usar config en tu template
# render_template("landing_page.html", **config)

# Cuando el usuario se registre
track_landing_page_conversion(
    test_id="landing_page_homepage_v1",
    session_id="sess_123",
    conversion_type="signup",
)
```

### Crear un Test de Precios

```python
from data.airflow.dags.ab_testing_examples import create_pricing_test

# Crear test de precios dinámicos
pg_hook = PostgresHook(postgres_conn_id="postgres_default")
conn = pg_hook.get_conn()
cursor = conn.cursor()

cursor.execute("""
    INSERT INTO ab_tests (
        test_id, test_name, test_type, description, status,
        traffic_split, minimum_sample_size, significance_level,
        primary_metric, auto_deploy_enabled
    ) VALUES (
        'pricing_strategy_v1',
        'Pricing Strategy Test',
        'pricing',
        'Test different pricing strategies',
        'draft',
        '{"variant_a": 0.5, "variant_b": 0.5}'::jsonb,
        1500, 0.95, 'revenue', true
    )
    ON CONFLICT (test_id) DO NOTHING
""")

cursor.execute("""
    INSERT INTO ab_test_variants (
        test_id, variant_id, variant_name, config, traffic_percentage, is_control
    ) VALUES
    ('pricing_strategy_v1', 'variant_a', 'Control', 
     '{"pricing": {"basic": 29.99, "pro": 79.99, "enterprise": 199.99}}'::jsonb, 0.5, true),
    ('pricing_strategy_v1', 'variant_b', 'Treatment',
     '{"pricing": {"basic": 39.99, "pro": 99.99, "enterprise": 249.99}}'::jsonb, 0.5, false)
    ON CONFLICT (test_id, variant_id) DO UPDATE
    SET config = EXCLUDED.config
""")

conn.commit()
```

### Usar en Pricing

```python
from data.airflow.dags.ab_testing_examples import (
    get_dynamic_pricing_with_ab_test,
    track_purchase,
)

# Obtener precios dinámicos
pricing = get_dynamic_pricing_with_ab_test(
    user_id="user_123",
    test_id="pricing_strategy_v1",
    default_pricing={
        "basic": 29.99,
        "pro": 79.99,
        "enterprise": 199.99,
    }
)

# Mostrar precios al usuario
# render_pricing_page(pricing)

# Cuando el usuario compre
track_purchase(
    test_id="pricing_strategy_v1",
    user_id="user_123",
    revenue=79.99,
)
```

## Análisis Estadístico

El sistema realiza análisis estadístico automático usando:

- **Z-test para proporciones**: Para conversion rates, open rates, click rates
- **Z-test para medias**: Para revenue per user
- **Confidence Intervals**: Intervalos de confianza al 95% o 99%
- **P-values**: Para determinar significancia estadística
- **Lift Calculation**: Porcentaje de mejora vs control

### Criterios de Auto-deployment

El sistema despliega automáticamente cuando:

1. **Significancia estadística**: p-value < alpha (default 0.05 para 95% confidence)
2. **Tamaño de muestra mínimo**: Al menos el mínimo configurado
3. **Lift mínimo**: Si está configurado, debe superar el lift mínimo requerido

### Configuración de Auto-deployment

```sql
UPDATE ab_tests
SET auto_deploy_when = 'significant'  -- Solo significancia
WHERE test_id = 'test_id';

UPDATE ab_tests
SET auto_deploy_when = 'significant_and_lift',  -- Significancia + lift mínimo
    minimum_lift_percentage = 10.0  -- Mínimo 10% de mejora
WHERE test_id = 'test_id';
```

## Monitoreo y Reportes

### Ver Resultados de un Test

```python
from data.airflow.dags.ab_testing_examples import get_test_results_summary

results = get_test_results_summary("email_subject_welcome_v1")
print(results)
```

### Consultas SQL Útiles

```sql
-- Ver todos los tests activos
SELECT test_id, test_name, test_type, status, created_at
FROM ab_tests
WHERE status = 'active';

-- Ver métricas por variante
SELECT 
    test_id,
    variant_id,
    total_assignments,
    conversions,
    conversion_rate,
    revenue_per_user
FROM ab_test_results
WHERE test_id = 'email_subject_welcome_v1'
AND analysis_date = CURRENT_DATE;

-- Ver análisis estadístico más reciente
SELECT 
    test_id,
    is_significant,
    p_value,
    winner_variant_id,
    winner_lift_percentage,
    recommendation
FROM ab_test_statistical_analysis
WHERE test_id = 'email_subject_welcome_v1'
ORDER BY analysis_timestamp DESC
LIMIT 1;

-- Ver deployments realizados
SELECT 
    test_id,
    winning_variant_id,
    deployment_type,
    deployment_status,
    deployed_at
FROM ab_test_deployments
ORDER BY deployed_at DESC;
```

## Integración con Sistemas Externos

### Email Services (SendGrid, Mailgun, etc.)

```python
# En tu webhook de email service
def email_webhook_handler(request):
    email = request.json["email"]
    event = request.json["event"]  # "opened", "clicked"
    
    # Obtener test_id del metadata del email
    test_id = request.json.get("metadata", {}).get("test_id")
    
    if test_id:
        track_email_engagement(
            test_id=test_id,
            email=email,
            event_type=f"email_{event}",
        )
```

### Frontend (React, Next.js, etc.)

```javascript
// En tu componente de landing page
import { useEffect, useState } from 'react';

function LandingPage({ sessionId }) {
  const [config, setConfig] = useState(null);
  
  useEffect(() => {
    // Obtener configuración de A/B test
    fetch(`/api/ab-testing/landing-page?test_id=landing_page_homepage_v1&session_id=${sessionId}`)
      .then(res => res.json())
      .then(data => setConfig(data));
    
    // Registrar page view
    fetch('/api/ab-testing/event', {
      method: 'POST',
      body: JSON.stringify({
        test_id: 'landing_page_homepage_v1',
        session_id: sessionId,
        event_type: 'page_view',
      }),
    });
  }, [sessionId]);
  
  // Registrar conversión
  const handleSignup = () => {
    fetch('/api/ab-testing/event', {
      method: 'POST',
      body: JSON.stringify({
        test_id: 'landing_page_homepage_v1',
        session_id: sessionId,
        event_type: 'conversion',
      }),
    });
  };
  
  return (
    <div>
      <h1>{config?.headline || 'Welcome'}</h1>
      <button onClick={handleSignup}>{config?.cta_text || 'Sign Up'}</button>
    </div>
  );
}
```

## Mejores Prácticas

1. **Tamaño de muestra**: Configura `minimum_sample_size` según el tipo de test
   - Emails: 1000-2000
   - Landing pages: 2000-5000
   - Pricing: 1500-3000
   - CTA buttons: 800-1500

2. **Duración del test**: Ejecuta tests por al menos 1-2 semanas para obtener resultados significativos

3. **Una variable a la vez**: No pruebes múltiples cambios simultáneamente

4. **Segmentación**: Considera segmentar tests por tipo de usuario (nuevo vs existente)

5. **Monitoreo continuo**: Revisa resultados regularmente pero evita detener tests prematuramente

## Troubleshooting

### Test no está asignando variantes

Verifica que el test esté activo:
```sql
SELECT status FROM ab_tests WHERE test_id = 'tu_test_id';
```

### No hay significancia estadística

- Verifica que el tamaño de muestra sea suficiente
- Revisa que las métricas se estén registrando correctamente
- Considera extender la duración del test

### Auto-deployment no funciona

- Verifica `auto_deploy_enabled = true`
- Revisa logs del DAG `ab_testing_automation`
- Verifica que se cumplan los criterios de deployment

## Referencias

- [Statistical Significance in A/B Testing](https://www.optimizely.com/optimization-glossary/statistical-significance/)
- [Sample Size Calculator](https://www.optimizely.com/sample-size-calculator/)
- [A/B Testing Best Practices](https://www.crazyegg.com/blog/ab-testing-best-practices/)

