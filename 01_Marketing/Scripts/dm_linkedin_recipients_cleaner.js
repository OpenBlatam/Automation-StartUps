#!/usr/bin/env node
/**
 * Recipients Cleaner
 * - Input: dm_linkedin_recipients.csv (name,profileUrl,variantId,industry,seniority,hourLocal,company,locale)
 * - Output: dm_linkedin_recipients_clean.csv
 * - Actions: trim, validate LinkedIn URL, normalize locale (xx-YY → xx-yy), lowercases industry/seniority/company, dedupe by profileUrl
 */
const fs = require('fs');
const path = require('path');

const IN = path.resolve(__dirname, 'dm_linkedin_recipients.csv');
const OUT = path.resolve(__dirname, 'dm_linkedin_recipients_clean.csv');

function isLinkedInUrl(u) {
  return /^https?:\/\/([a-zA-Z0-9.-]+\.)?linkedin\.com\/(in|sales)\//.test(u || '');
}

function normalizeLocale(s) {
  if (!s) return '';
  return String(s).toLowerCase();
}

function main() {
  if (!fs.existsSync(IN)) {
    console.error('Missing dm_linkedin_recipients.csv');
    process.exit(1);
  }
  const lines = fs.readFileSync(IN, 'utf8').split('\n');
  const header = lines.shift();
  const out = ['name,profileUrl,variantId,industry,seniority,hourLocal,company,locale'];
  const seen = new Set();
  for (const line of lines) {
    if (!line.trim()) continue;
    const parts = line.split(',');
    while (parts.length < 8) parts.push('');
    let [name, url, variantId, industry, seniority, hourLocal, company, locale] = parts;
    name = (name||'').trim();
    url = (url||'').trim();
    variantId = (variantId||'').trim();
    industry = (industry||'').trim().toLowerCase();
    seniority = (seniority||'').trim().toLowerCase();
    company = (company||'').trim().toLowerCase();
    locale = normalizeLocale((locale||'').trim());
    if (!name || !url || !isLinkedInUrl(url)) continue;
    if (seen.has(url)) continue;
    seen.add(url);
    const hl = Number(hourLocal);
    const hourVal = isFinite(hl) ? hl : '';
    out.push([name, url, variantId, industry, seniority, hourVal, company, locale].join(','));
  }
  fs.writeFileSync(OUT, out.join('\n'), 'utf8');
  console.log('Clean recipients written to', OUT);
}

if (require.main === module) main();
