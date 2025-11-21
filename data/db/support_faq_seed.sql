-- ============================================================================
-- SEED DATA: Artículos de FAQ de Ejemplo
-- ============================================================================
-- Este script contiene ejemplos de artículos de FAQ para poblar la base de datos
-- Puedes ejecutarlo después de crear el esquema para tener datos de prueba
-- ============================================================================

BEGIN;

-- FAQ: Restablecer contraseña
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords,
    intent_mappings
) VALUES (
    'faq-password-reset',
    '¿Cómo restablezco mi contraseña?',
    'Para restablecer tu contraseña, sigue estos pasos:

1. Ve a la página de login
2. Haz clic en "Olvidé mi contraseña" o "¿Necesitas ayuda?"
3. Ingresa tu dirección de email registrada
4. Revisa tu bandeja de entrada (y spam) para el email de restablecimiento
5. Haz clic en el enlace del email
6. Ingresa tu nueva contraseña (mínimo 8 caracteres, con mayúsculas, minúsculas y números)
7. Confirma tu nueva contraseña

Si no recibes el email en 5 minutos, verifica que estés usando el email correcto. Si el problema persiste, contacta a soporte.',
    'Instrucciones paso a paso para restablecer tu contraseña si la olvidaste',
    'account',
    ARRAY['password', 'login', 'account', 'security'],
    ARRAY['contraseña', 'password', 'reset', 'olvidé', 'olvide', 'recuperar', 'cambiar', 'forgot'],
    ARRAY['password_reset', 'account_help', 'login_issue']
) ON CONFLICT (article_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    summary = EXCLUDED.summary,
    last_updated_at = NOW();

-- FAQ: Problemas de facturación
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords,
    intent_mappings
) VALUES (
    'faq-billing-download',
    '¿Cómo descargo mi factura?',
    'Para descargar tus facturas:

1. Inicia sesión en tu cuenta
2. Ve a la sección "Facturación" o "Billing"
3. Haz clic en "Facturas" o "Invoices"
4. Selecciona la factura que deseas descargar
5. Haz clic en "Descargar" o "Download"
6. El archivo PDF se descargará automáticamente

Las facturas están disponibles en formato PDF. Si tienes problemas para descargar, verifica que:
- Tu navegador permita descargas
- No tengas bloqueadores de pop-ups activos
- Tengas suficiente espacio en tu dispositivo

Para facturas anteriores a 12 meses, contacta a nuestro equipo de facturación.',
    'Guía para descargar facturas desde tu cuenta',
    'billing',
    ARRAY['factura', 'invoice', 'billing', 'pago', 'payment'],
    ARRAY['factura', 'invoice', 'descargar', 'download', 'recibo', 'comprobante'],
    ARRAY['billing_download', 'invoice_access']
) ON CONFLICT (article_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    summary = EXCLUDED.summary,
    last_updated_at = NOW();

-- FAQ: Problemas técnicos
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords,
    intent_mappings
) VALUES (
    'faq-technical-not-loading',
    'El sistema no carga o está muy lento',
    'Si el sistema no carga o está muy lento, prueba estas soluciones:

1. Refresca la página (F5 o Ctrl+R)
2. Limpia la caché del navegador (Ctrl+Shift+Delete)
3. Prueba en otro navegador (Chrome, Firefox, Safari, Edge)
4. Desactiva extensiones del navegador temporalmente
5. Verifica tu conexión a internet
6. Reinicia tu router/módem si es necesario

Si el problema persiste:
- Verifica el estado del servicio en nuestra página de estado
- Intenta desde otro dispositivo o red
- Contacta a soporte técnico con detalles del error

Información útil para soporte:
- Qué navegador y versión estás usando
- Qué mensaje de error ves (si hay)
- Captura de pantalla del problema',
    'Soluciones para problemas de carga o lentitud del sistema',
    'technical',
    ARRAY['technical', 'performance', 'loading', 'slow', 'error'],
    ARRAY['lento', 'slow', 'no carga', 'no funciona', 'error', 'problema', 'bug', 'falla'],
    ARRAY['technical_issue', 'performance_problem', 'system_error']
) ON CONFLICT (article_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    summary = EXCLUDED.summary,
    last_updated_at = NOW();

-- FAQ: Cambiar plan
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords,
    intent_mappings
) VALUES (
    'faq-change-plan',
    '¿Cómo cambio mi plan de suscripción?',
    'Para cambiar tu plan de suscripción:

1. Inicia sesión en tu cuenta
2. Ve a "Configuración" > "Suscripción" o "Billing"
3. Haz clic en "Cambiar Plan" o "Change Plan"
4. Selecciona el nuevo plan que deseas
5. Revisa los cambios de precio y características
6. Confirma el cambio

Notas importantes:
- Los cambios se aplican al inicio del próximo ciclo de facturación
- Si subes de plan, tendrás acceso inmediato a las nuevas características
- Si bajas de plan, los cambios se aplicarán al renovar
- Los descuentos se mantienen si aplican al nuevo plan

Para cambios empresariales o personalizados, contacta a nuestro equipo de ventas.',
    'Instrucciones para cambiar tu plan de suscripción',
    'billing',
    ARRAY['plan', 'subscription', 'upgrade', 'downgrade', 'billing'],
    ARRAY['plan', 'suscripción', 'cambiar', 'upgrade', 'downgrade', 'precio', 'precios'],
    ARRAY['billing_change', 'subscription_management']
) ON CONFLICT (article_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    summary = EXCLUDED.summary,
    last_updated_at = NOW();

-- FAQ: Cancelar cuenta
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords,
    intent_mappings
) VALUES (
    'faq-cancel-account',
    '¿Cómo cancelo mi cuenta?',
    'Para cancelar tu cuenta:

1. Inicia sesión en tu cuenta
2. Ve a "Configuración" > "Cuenta"
3. Desplázate hasta "Cancelar Cuenta" o "Delete Account"
4. Lee la información sobre la cancelación
5. Confirma que deseas cancelar

Importante:
- Tu suscripción activa seguirá vigente hasta el final del período pagado
- No recibirás reembolsos por períodos no utilizados
- Puedes reactivar tu cuenta dentro de 30 días después de cancelar
- Todos tus datos se eliminarán permanentemente después de 30 días

Si cancelas por un problema, te invitamos a contactarnos primero. Nos encantaría ayudarte a resolverlo.',
    'Información sobre cómo cancelar tu cuenta y sus consecuencias',
    'account',
    ARRAY['cancel', 'delete', 'account', 'close'],
    ARRAY['cancelar', 'cancel', 'eliminar', 'delete', 'cerrar', 'close', 'dar de baja'],
    ARRAY['account_cancellation', 'account_deletion']
) ON CONFLICT (article_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    summary = EXCLUDED.summary,
    last_updated_at = NOW();

-- FAQ: Reembolsos
INSERT INTO support_faq_articles (
    article_id,
    title,
    content,
    summary,
    category,
    tags,
    keywords,
    intent_mappings
) VALUES (
    'faq-refund-policy',
    '¿Cuál es la política de reembolsos?',
    'Nuestra política de reembolsos:

**Reembolsos completos:**
- Dentro de los primeros 14 días de la suscripción
- Si no has usado el servicio de manera significativa
- Si hay un problema técnico que no podemos resolver

**Reembolsos parciales:**
- Por períodos no utilizados en casos especiales
- A discreción del equipo de soporte

**No aplican reembolsos:**
- Después de 14 días de uso
- Si has usado todas las características principales
- Cambios de opinión después de usar el servicio

Para solicitar un reembolso:
1. Contacta a nuestro equipo de soporte
2. Proporciona el número de factura o transacción
3. Explica el motivo de la solicitud
4. Nuestro equipo revisará tu caso en 2-3 días hábiles

Los reembolsos se procesan en 5-10 días hábiles a la tarjeta original.',
    'Información sobre la política de reembolsos y cómo solicitarlos',
    'billing',
    ARRAY['refund', 'reembolso', 'money-back', 'billing'],
    ARRAY['reembolso', 'refund', 'devolución', 'money back', 'reembolsar'],
    ARRAY['billing_refund', 'payment_issue']
) ON CONFLICT (article_id) DO UPDATE SET
    title = EXCLUDED.title,
    content = EXCLUDED.content,
    summary = EXCLUDED.summary,
    last_updated_at = NOW();

COMMIT;

-- Verificar que se insertaron correctamente
SELECT 
    article_id,
    title,
    category,
    array_length(keywords, 1) as keywords_count
FROM support_faq_articles
ORDER BY article_id;

