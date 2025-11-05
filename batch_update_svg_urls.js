/**
 * Script para actualizar URLs con UTMs en múltiples templates SVG
 * Uso: node batch_update_svg_urls.js [config_file.json]
 */

const fs = require('fs');
const path = require('path');
const { generateIGPostURL, generateLinkedInAdURL, generateWebinarURL } = require('./IG_TEMPLATE_UTM_HELPER.js');

/**
 * Actualiza URL en un archivo SVG
 */
function updateSVGFile(filePath, newURL, platform = 'instagram') {
  try {
    let content = fs.readFileSync(filePath, 'utf8');
    const originalURL = content.match(/href=['"]https?:\/\/[^'"]+['"]/i)?.[0] || '';
    
    // Reemplazar URL existente
    content = content.replace(/href=['"]https?:\/\/[^'"]+['"]/gi, `href="${newURL}"`);
    
    // Reemplazar URLs genéricas comunes
    content = content.replace(/https:\/\/tu-sitio\.com/gi, newURL.split('?')[0]);
    content = content.replace(/https:\/\/tusitio\.com/gi, newURL.split('?')[0]);
    
    // Guardar archivo
    fs.writeFileSync(filePath, content, 'utf8');
    
    return {
      success: true,
      file: filePath,
      oldURL: originalURL,
      newURL
    };
  } catch (error) {
    return {
      success: false,
      file: filePath,
      error: error.message
    };
  }
}

/**
 * Procesa batch de archivos desde configuración JSON
 */
function processBatch(configFile) {
  const config = JSON.parse(fs.readFileSync(configFile, 'utf8'));
  const results = [];

  config.templates.forEach(template => {
    let url;
    
    // Generar URL según plataforma
    switch (template.platform) {
      case 'instagram':
        url = generateIGPostURL({
          template: template.template,
          version: template.version || 1,
          product: template.product,
          month: template.month || new Date().toISOString().slice(0, 7),
          region: template.region || 'mx',
          persona: template.persona || 'buyer',
          urlBase: template.urlBase || config.defaults.urlBase
        });
        break;
        
      case 'linkedin':
        url = generateLinkedInAdURL({
          template: template.template,
          angle: template.angle || 'h1direct',
          cta: template.cta || 'reserva',
          version: template.version || 1,
          product: template.product,
          month: template.month || new Date().toISOString().slice(0, 7),
          role: template.role || 'cmo',
          region: template.region || 'mx',
          urlBase: template.urlBase || config.defaults.urlBase
        });
        break;
        
      case 'webinar':
        url = generateWebinarURL({
          style: template.style || 'speaker',
          version: template.version || 1,
          product: template.product,
          topic: template.topic || 'ia',
          month: template.month || new Date().toISOString().slice(0, 7),
          source: template.source || 'email',
          medium: template.medium || 'email',
          audience: template.audience || 'general',
          urlBase: template.urlBase || config.defaults.urlBase
        });
        break;
        
      default:
        console.warn(`Plataforma desconocida: ${template.platform}`);
        return;
    }

    // Actualizar archivo
    const result = updateSVGFile(template.filePath, url, template.platform);
    results.push(result);
    
    console.log(result.success 
      ? `✅ ${path.basename(template.filePath)}` 
      : `❌ ${path.basename(template.filePath)}: ${result.error}`);
  });

  return results;
}

// Ejemplo de uso directo (sin archivo config)
if (require.main === module && process.argv.length === 1) {
  console.log('Uso: node batch_update_svg_urls.js [config.json]');
  console.log('\nEjemplo de config.json:');
  console.log(JSON.stringify({
    defaults: {
      urlBase: 'https://tusitio.com/landing',
      month: '2025-11'
    },
    templates: [
      {
        platform: 'instagram',
        filePath: './instagram_antes_despues_template.svg',
        template: 'antes_despues',
        version: 1,
        product: 'cursoia',
        region: 'mx',
        persona: 'buyer'
      },
      {
        platform: 'linkedin',
        filePath: './ads/linkedin/ad_curso_ia_1200x627_urgency.svg',
        template: 'urgency',
        angle: 'h1direct',
        cta: 'reserva',
        version: 1,
        product: 'cursoia',
        role: 'cmo',
        region: 'mx'
      }
    ]
  }, null, 2));
} else if (process.argv.length > 2) {
  const configFile = process.argv[2];
  const results = processBatch(configFile);
  
  const success = results.filter(r => r.success).length;
  const failed = results.filter(r => !r.success).length;
  
  console.log(`\n📊 Resumen: ${success} actualizados, ${failed} errores`);
}

module.exports = {
  updateSVGFile,
  processBatch
};



