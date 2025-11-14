/**
 * Helper UNIFICADO para generar URLs con UTMs para todos los templates
 * Soporta: Instagram, LinkedIn Ads, Webinar Preroll
 * Uso: node IG_TEMPLATE_UTM_HELPER.js o incluir en build script
 */

// Configuración base
const CONFIG = {
  urlBase: 'https://tusitio.com/landing',
  utmSource: 'instagram',
  utmMedium: 'feed',
  campaignPrefix: 'cursoia', // Cambiar según producto
  defaultTerm: 'mx_buyer' // Cambiar según audiencia
};

/**
 * Genera URL completa con UTMs para post de Instagram
 * @param {Object} options - Opciones de configuración
 * @returns {String} URL completa con UTMs
 */
function generateIGPostURL(options = {}) {
  const {
    template = 'antes_despues',
    version = 1,
    product = CONFIG.campaignPrefix,
    month = new Date().toISOString().slice(0, 7), // YYYY-MM
    persona = 'buyer',
    region = 'mx',
    urlBase = CONFIG.urlBase
  } = options;

  const utms = {
    utm_source: CONFIG.utmSource,
    utm_medium: CONFIG.utmMedium,
    utm_campaign: `${product}_resultados_ig_${month}`,
    utm_content: `${template}_v${version}`,
    utm_term: `${region}_${persona}`
  };

  const params = new URLSearchParams(utms);
  return `${urlBase}?${params.toString()}`;
}

/**
 * Genera URL para Stories (usar en sticker "Más información")
 */
function generateIGStoriesURL(options = {}) {
  const baseURL = generateIGPostURL(options);
  // Cambiar medium a 'stories'
  return baseURL.replace('utm_medium=feed', 'utm_medium=stories');
}

/**
 * Genera múltiples URLs para batch de posts
 * @param {Array} posts - Array de configuraciones de posts
 * @returns {Array} Array de objetos con fecha, filename y URL
 */
function generateBatchURLs(posts) {
  return posts.map(post => {
    const url = generateIGPostURL(post);
    const filename = `${post.template}_v${post.version}_ig_${post.date}.png`;
    
    return {
      fecha: post.date,
      template: post.template,
      version: post.version,
      filename,
      url_feed: url,
      url_stories: generateIGStoriesURL(post),
      utm_campaign: `${post.product}_resultados_ig_${post.date.slice(0, 7)}`,
      utm_content: `${post.template}_v${post.version}`
    };
  });
}

/**
 * Actualiza URL en template SVG (helper para scripts de build)
 * @param {String} svgContent - Contenido del SVG
 * @param {String} newURL - Nueva URL con UTMs
 * @returns {String} SVG actualizado
 */
function updateSVGURL(svgContent, newURL) {
  // Reemplazar href en elemento CTA
  return svgContent
    .replace(/href=['"]https?:\/\/[^'"]+['"]/gi, `href="${newURL}"`)
    .replace(/https:\/\/tu-sitio\.com/gi, newURL.split('?')[0]);
}

/**
 * Genera URL para LinkedIn Ads
 */
function generateLinkedInAdURL(options = {}) {
  const {
    template = 'urgency',
    angle = 'h1direct',
    cta = 'reserva',
    version = 1,
    product = CONFIG.campaignPrefix,
    month = new Date().toISOString().slice(0, 7),
    role = 'cmo',
    region = 'mx',
    urlBase = CONFIG.urlBase
  } = options;

  const utms = {
    utm_source: 'linkedin',
    utm_medium: 'cpc',
    utm_campaign: `${product}_demo_linkedin_${month}`,
    utm_content: `${template}_${angle}_${cta}_v${version}`,
    utm_term: `${role}_${region}`
  };

  const params = new URLSearchParams(utms);
  return `${urlBase}?${params.toString()}`;
}

/**
 * Genera URL para Webinar Preroll
 */
function generateWebinarURL(options = {}) {
  const {
    style = 'speaker',
    version = 1,
    product = CONFIG.campaignPrefix,
    topic = 'ia',
    month = new Date().toISOString().slice(0, 7),
    source = 'email',
    medium = 'email',
    audience = 'general',
    urlBase = CONFIG.urlBase
  } = options;

  const utms = {
    utm_source: source,
    utm_medium: medium,
    utm_campaign: `${product}_webinar_${topic}_${month}`,
    utm_content: `preroll_${style}_v${version}`,
    utm_term: audience
  };

  const params = new URLSearchParams(utms);
  return `${urlBase}?${params.toString()}`;
}

/**
 * Genera URLs para batch de múltiples plataformas
 */
function generateMultiPlatformBatch(posts) {
  return posts.map(post => {
    let url;
    let filename;

    switch (post.platform) {
      case 'instagram':
        url = generateIGPostURL(post);
        filename = `${post.template}_v${post.version}_ig_${post.date}.png`;
        break;
      case 'linkedin':
        url = generateLinkedInAdURL(post);
        // Incluir formato en filename si está disponible
        const format = post.format || (post.dimensions || '1200x627');
        filename = `${post.template}_v${post.version}_linkedin_${format.replace('x', 'x')}_${post.date}.png`;
        break;
      case 'webinar':
        url = generateWebinarURL(post);
        filename = `preroll_${post.style}_v${post.version}_${post.date}.png`;
        break;
      default:
        url = generateIGPostURL(post);
        filename = `${post.template}_v${post.version}_${post.date}.png`;
    }

    return {
      fecha: post.date,
      plataforma: post.platform,
      template: post.template,
      version: post.version,
      filename,
      url,
      utm_campaign: post.utm_campaign || '',
      utm_content: post.utm_content || ''
    };
  });
}

// Ejemplos de uso
if (require.main === module) {
  // Ejemplo 1: URL simple
  console.log('=== URL Post Feed ===');
  console.log(generateIGPostURL({
    template: 'antes_despues',
    version: 1,
    date: '2025-11-30'
  }));

  // Ejemplo 2: URL Stories
  console.log('\n=== URL Stories ===');
  console.log(generateIGStoriesURL({
    template: 'antes_despues',
    version: 1,
    date: '2025-11-30'
  }));

  // Ejemplo 3: LinkedIn Ad
  console.log('\n=== LinkedIn Ad URL ===');
  console.log(generateLinkedInAdURL({
    template: 'urgency',
    angle: 'h1direct',
    cta: 'reserva',
    version: 1,
    product: 'cursoia',
    role: 'cmo',
    region: 'mx'
  }));

  // Ejemplo 4: Webinar
  console.log('\n=== Webinar URL ===');
  console.log(generateWebinarURL({
    style: 'speaker',
    version: 1,
    product: 'cursoia',
    topic: 'ia',
    source: 'email',
    medium: 'email'
  }));

  // Ejemplo 5: Batch multi-plataforma
  console.log('\n=== Batch Multi-Plataforma ===');
  const multiBatch = [
    { platform: 'instagram', template: 'antes_despues', version: 1, product: 'cursoia', date: '2025-11-30', region: 'mx', persona: 'buyer' },
    { platform: 'linkedin', template: 'urgency', angle: 'h1direct', cta: 'reserva', version: 1, product: 'saasia', date: '2025-12-01', role: 'cmo', region: 'mx' },
    { platform: 'webinar', style: 'speaker', version: 1, product: 'cursoia', topic: 'ia', date: '2025-12-02', source: 'email', medium: 'email' }
  ];
  
  const batch = generateMultiPlatformBatch(multiBatch);
  console.table(batch);
}

// Exportar para uso en otros scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    generateIGPostURL,
    generateIGStoriesURL,
    generateLinkedInAdURL,
    generateWebinarURL,
    generateBatchURLs,
    generateMultiPlatformBatch,
    updateSVGURL,
    CONFIG
  };
}

