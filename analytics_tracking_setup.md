# CONFIGURACIÓN DE ANALYTICS Y TRACKING - WEBINAR IA

## GOOGLE ANALYTICS 4 (GA4) - CONFIGURACIÓN COMPLETA

### 1. Eventos Personalizados a Configurar

```javascript
// Evento de Registro al Webinar
gtag('event', 'webinar_registration', {
  'event_category': 'engagement',
  'event_label': 'webinar_ia_2024',
  'value': 1,
  'custom_parameters': {
    'webinar_name': 'Webinar IA 2024',
    'registration_source': 'google_ads',
    'user_type': 'new_visitor'
  }
});

// Evento de Visualización de Video
gtag('event', 'video_view', {
  'event_category': 'engagement',
  'event_label': 'webinar_promo_video',
  'value': 1
});

// Evento de Descarga de Recursos
gtag('event', 'file_download', {
  'event_category': 'engagement',
  'event_label': 'webinar_guide_pdf',
  'value': 1
});
```

### 2. Conversiones Configuradas

| Nombre de Conversión | Evento | Valor | Categoría |
|---------------------|--------|-------|-----------|
| Registro Webinar | webinar_registration | $50 | Primary |
| Descarga Guía | file_download | $10 | Secondary |
| Visualización Video | video_view | $5 | Secondary |
| Tiempo en Página > 2min | engagement_time_more_than_2_minutes | $3 | Secondary |

### 3. Audiencias Personalizadas

```javascript
// Audiencia: Visitantes que vieron el video promocional
// Condición: Evento 'video_view' = 'webinar_promo_video'

// Audiencia: Usuarios que descargaron la guía
// Condición: Evento 'file_download' = 'webinar_guide_pdf'

// Audiencia: Visitantes de alto engagement
// Condición: Tiempo en sesión > 3 minutos Y páginas vistas > 2

// Audiencia: Abandonos de registro
// Condición: Página vista = '/registro' Y NO evento 'webinar_registration'
```

## FACEBOOK PIXEL - CONFIGURACIÓN COMPLETA

### 1. Eventos del Pixel

```javascript
// Evento de Registro (Conversión Principal)
fbq('track', 'Lead', {
  content_name: 'Webinar IA 2024',
  content_category: 'Webinar',
  value: 50.00,
  currency: 'MXN'
});

// Evento de Inicio de Registro
fbq('track', 'InitiateCheckout', {
  content_name: 'Webinar IA 2024',
  content_category: 'Webinar'
});

// Evento de Visualización de Contenido
fbq('track', 'ViewContent', {
  content_name: 'Webinar IA 2024',
  content_category: 'Webinar',
  content_type: 'webinar'
});

// Evento Personalizado: Tiempo en Página
fbq('trackCustom', 'TimeOnPage', {
  time_spent: 120, // segundos
  page_type: 'landing_page'
});
```

### 2. Configuración de Conversiones

| Evento | Tipo | Valor | Ventana de Atribución |
|--------|------|-------|----------------------|
| Lead | Conversión Principal | $50 MXN | 7 días |
| InitiateCheckout | Conversión Secundaria | $25 MXN | 1 día |
| ViewContent | Conversión Secundaria | $10 MXN | 1 día |

### 3. Audiencias Personalizadas

```javascript
// Audiencia: Visitantes de la landing page
// Fuente: Tráfico web
// Condición: URL contiene 'tuwebinar.com/registro'

// Audiencia: Usuarios que iniciaron registro
// Fuente: Eventos del pixel
// Condición: Evento 'InitiateCheckout' en últimos 30 días

// Audiencia: Visitantes de alto valor
// Fuente: Eventos del pixel
// Condición: Tiempo en página > 2 minutos Y páginas vistas > 3
```

## TIKTOK PIXEL - CONFIGURACIÓN

### 1. Eventos del Pixel TikTok

```javascript
// Evento de Registro
ttq.track('CompleteRegistration', {
  content_type: 'webinar',
  content_name: 'Webinar IA 2024',
  value: 50.00,
  currency: 'MXN'
});

// Evento de Visualización de Página
ttq.track('ViewContent', {
  content_type: 'webinar',
  content_name: 'Webinar IA 2024'
});

// Evento de Interacción
ttq.track('ClickButton', {
  button_name: 'registro_webinar'
});
```

## GOOGLE ADS - CONVERSION TRACKING

### 1. Etiquetas de Conversión

```html
<!-- Etiqueta Global del Sitio -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXX');
</script>

<!-- Conversión de Registro -->
<script>
  gtag('event', 'conversion', {
      'send_to': 'AW-XXXXXXXXX/XXXXXXXXX',
      'value': 50.00,
      'currency': 'MXN',
      'transaction_id': 'WEBINAR_REG_' + Date.now()
  });
</script>
```

### 2. Conversiones Importadas

| Fuente | Conversión | Valor | Importación |
|--------|------------|-------|-------------|
| Google Analytics | webinar_registration | $50 | Automática |
| Google Analytics | file_download | $10 | Automática |

## UTM TRACKING - PARÁMETROS COMPLETOS

### 1. Estructura de UTM

```
utm_campaign=webinar_ia_2024
utm_medium=google|facebook|tiktok|linkedin
utm_source=cpc|social|display
utm_term=inteligencia_artificial|curso_ia|webinar_ia
utm_content=banner_principal|video_creativo|carousel_ads
```

### 2. URLs de Ejemplo

```
https://tuwebinar.com/registro?
utm_campaign=webinar_ia_2024&
utm_medium=google&
utm_source=cpc&
utm_term=inteligencia_artificial&
utm_content=banner_principal

https://tuwebinar.com/registro?
utm_campaign=webinar_ia_2024&
utm_medium=facebook&
utm_source=social&
utm_term=facebook_ads&
utm_content=video_creativo

https://tuwebinar.com/registro?
utm_campaign=webinar_ia_2024&
utm_medium=tiktok&
utm_source=social&
utm_term=tiktok_ads&
utm_content=video_vertical
```

## DASHBOARD DE MÉTRICAS - CONFIGURACIÓN

### 1. Métricas Principales

| Métrica | Fuente | Frecuencia | Objetivo |
|---------|--------|------------|----------|
| Registros Webinar | GA4 + Facebook Pixel | Tiempo Real | 432 registros |
| Costo por Registro | Google Ads + Meta Ads | Diario | < $15 MXN |
| Tasa de Conversión | GA4 | Diario | > 10% |
| ROI | Cálculo Manual | Semanal | > 2.5x |

### 2. Alertas Automáticas

```javascript
// Alerta: Costo por registro > $20 MXN
if (costo_por_registro > 20) {
  enviar_alerta('Costo por registro excede objetivo');
}

// Alerta: Tasa de conversión < 5%
if (tasa_conversion < 0.05) {
  enviar_alerta('Tasa de conversión por debajo del objetivo');
}

// Alerta: Presupuesto agotado al 90%
if (presupuesto_gastado > presupuesto_total * 0.9) {
  enviar_alerta('Presupuesto al 90% - Revisar rendimiento');
}
```

## CÓDIGO DE IMPLEMENTACIÓN COMPLETO

### 1. HTML de la Landing Page

```html
<!DOCTYPE html>
<html>
<head>
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXX"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-XXXXXXXXX');
    </script>
    
    <!-- Facebook Pixel -->
    <script>
        !function(f,b,e,v,n,t,s)
        {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
        n.callMethod.apply(n,arguments):n.queue.push(arguments)};
        if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
        n.queue=[];t=b.createElement(e);t.async=!0;
        t.src=v;s=b.getElementsByTagName(e)[0];
        s.parentNode.insertBefore(t,s)}(window, document,'script',
        'https://connect.facebook.net/en_US/fbevents.js');
        fbq('init', 'XXXXXXXXX');
        fbq('track', 'PageView');
    </script>
    
    <!-- TikTok Pixel -->
    <script>
        !function (w, d, t) {
            w.TikTokAnalyticsObject=t;var ttq=w[t]=w[t]||[];ttq.methods=["track","page","identify","instances","debug","on","off","once","ready","alias","group","enableCookie","disableCookie"],ttq.setAndDefer=function(t,e){t[e]=function(){t.push([e].concat(Array.prototype.slice.call(arguments,0)))}};for(var i=0;i<ttq.methods.length;i++)ttq.setAndDefer(ttq,ttq.methods[i]);ttq.instance=function(t){for(var e=ttq._i[t]||[],n=0;n<ttq.methods.length;n++)ttq.setAndDefer(e,ttq.methods[n]);return e},ttq.load=function(e,n){var i="https://analytics.tiktok.com/i18n/pixel/events.js";ttq._i=ttq._i||{},ttq._i[e]=[],ttq._i[e]._u=i,ttq._t=ttq._t||{},ttq._t[e]=+new Date,ttq._o=ttq._o||{},ttq._o[e]=n||{};var o=document.createElement("script");o.type="text/javascript",o.async=!0,o.src=i+"?sdkid="+e+"&lib="+t;var a=document.getElementsByTagName("script")[0];a.parentNode.insertBefore(o,a)};
            ttq.load('XXXXXXXXX');
            ttq.page();
        }(window, document, 'ttq');
    </script>
</head>
<body>
    <!-- Contenido de la página -->
    
    <!-- Formulario de Registro -->
    <form id="registroForm" onsubmit="trackRegistration()">
        <input type="email" name="email" required>
        <input type="text" name="nombre" required>
        <button type="submit">Registrarse al Webinar</button>
    </form>
    
    <script>
        function trackRegistration() {
            // Google Analytics
            gtag('event', 'webinar_registration', {
                'event_category': 'engagement',
                'event_label': 'webinar_ia_2024',
                'value': 1
            });
            
            // Facebook Pixel
            fbq('track', 'Lead', {
                content_name: 'Webinar IA 2024',
                content_category: 'Webinar',
                value: 50.00,
                currency: 'MXN'
            });
            
            // TikTok Pixel
            ttq.track('CompleteRegistration', {
                content_type: 'webinar',
                content_name: 'Webinar IA 2024',
                value: 50.00,
                currency: 'MXN'
            });
        }
    </script>
</body>
</html>
```

## CHECKLIST DE IMPLEMENTACIÓN

### ✅ Configuración Inicial
- [ ] Crear cuenta de Google Analytics 4
- [ ] Configurar Facebook Pixel
- [ ] Configurar TikTok Pixel
- [ ] Crear conversiones en Google Ads
- [ ] Configurar eventos personalizados

### ✅ Implementación Técnica
- [ ] Instalar códigos de tracking en landing page
- [ ] Configurar UTM parameters
- [ ] Probar eventos de conversión
- [ ] Verificar datos en tiempo real
- [ ] Configurar audiencias personalizadas

### ✅ Monitoreo y Optimización
- [ ] Revisar métricas diariamente
- [ ] Configurar alertas automáticas
- [ ] Analizar datos de atribución
- [ ] Optimizar basado en datos
- [ ] Reportar resultados semanalmente

## CONTACTOS DE SOPORTE

| Plataforma | Soporte | Email | Teléfono |
|------------|---------|-------|----------|
| Google Analytics | Centro de Ayuda | support@google.com | 1-855-836-3987 |
| Facebook Ads | Centro de Ayuda | business@facebook.com | 1-650-543-4800 |
| TikTok Ads | Centro de Ayuda | ads-support@tiktok.com | - |
| Google Ads | Centro de Ayuda | ads-support@google.com | 1-855-836-3987 |


