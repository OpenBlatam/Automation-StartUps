#!/usr/bin/env node
const params = require('minimist')(process.argv.slice(2));

function buildUrl({ base, servicio, etapa, variante, formato, audiencia }) {
  if (!base) throw new Error('Parámetro --base es requerido');
  const campaign = `${servicio}_${etapa}`;
  const content = `${variante}_${formato}`;
  const url = new URL(base);
  url.searchParams.set('utm_source', 'linkedin');
  url.searchParams.set('utm_medium', 'cpc');
  url.searchParams.set('utm_campaign', campaign);
  url.searchParams.set('utm_content', content);
  if (audiencia) url.searchParams.set('utm_term', audiencia);
  return url.toString();
}

try {
  const url = buildUrl({
    base: params.base || params.b,
    servicio: params.servicio || params.s || 'curso_ia',
    etapa: params.etapa || params.e || 'tofu',
    variante: params.variante || params.v || 'v2',
    formato: params.formato || params.f || '1200x627',
    audiencia: params.audiencia || params.a || ''
  });
  console.log(url);
} catch (e) {
  console.error('Error:', e.message);
  console.error('Uso: utm_generator.js --base https://tudominio.com/landing \\');
  console.error('  --servicio curso_ia|saas_ia|ia_bulk --etapa tofu|mofu|bofu \\');
  console.error('  --variante v2|metrics|light|social_proof|urgency|carousel_5slides \\');
  console.error('  --formato 1200x627|1080x1080|1080x1920 [--audiencia cmos_enterprise]');
  process.exit(1);
}

