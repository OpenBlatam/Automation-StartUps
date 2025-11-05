#!/usr/bin/env node
// Sincroniza tokens entre Instagram y LinkedIn (y otras plataformas futuras)

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const INSTAGRAM_TOKENS = path.join(ROOT, 'design', 'instagram', 'tokens.json');

function main() {
  const instagramTokens = JSON.parse(fs.readFileSync(INSTAGRAM_TOKENS, 'utf8'));
  
  // LinkedIn tokens (crear si no existe)
  const linkedinTokensPath = path.join(ROOT, 'ads', 'linkedin', 'tokens.json');
  let linkedinTokens = {};
  
  if (fs.existsSync(linkedinTokensPath)) {
    linkedinTokens = JSON.parse(fs.readFileSync(linkedinTokensPath, 'utf8'));
  }
  
  // Sync campos comunes
  linkedinTokens.url = instagramTokens.url || linkedinTokens.url;
  linkedinTokens.handle = instagramTokens.handle || linkedinTokens.handle;
  linkedinTokens.coupon = instagramTokens.coupon || linkedinTokens.coupon;
  linkedinTokens.cta = instagramTokens.cta || linkedinTokens.cta;
  
  // LinkedIn puede tener campos adicionales
  if (!linkedinTokens.companyName) linkedinTokens.companyName = '';
  if (!linkedinTokens.website) linkedinTokens.website = linkedinTokens.url;
  
  fs.writeFileSync(linkedinTokensPath, JSON.stringify(linkedinTokens, null, 2), 'utf8');
  console.log('✅ Tokens sincronizados a LinkedIn');
  console.log('📝 LinkedIn tokens:', linkedinTokensPath);
}

if (require.main === module) main();



