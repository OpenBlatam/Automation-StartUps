#!/usr/bin/env node
// Generates QR codes (SVG/PNG) for the URL in design/instagram/tokens.json
// Requires: npm i qrcode (https://www.npmjs.com/package/qrcode)

const fs = require('fs');
const path = require('path');

const ROOT = path.resolve(__dirname, '..');
const TOKENS = path.join(ROOT, 'design', 'instagram', 'tokens.json');
const OUT_DIR = path.join(ROOT, 'design', 'instagram', 'assets', 'qr');

async function main() {
  let QRCode;
  try {
    QRCode = require('qrcode');
  } catch (e) {
    console.error('Missing dependency: qrcode. Install with:');
    console.error('  npm install qrcode');
    process.exit(1);
  }

  const tokens = JSON.parse(fs.readFileSync(TOKENS, 'utf8'));
  const url = tokens.url && tokens.url.startsWith('http') ? tokens.url : `https://${tokens.url || 'example.com'}`;
  fs.mkdirSync(OUT_DIR, { recursive: true });

  const svgPath = path.join(OUT_DIR, 'qr.svg');
  const pngPath = path.join(OUT_DIR, 'qr.png');

  const svg = await QRCode.toString(url, { type: 'svg', margin: 1, color: { dark: '#000000', light: '#FFFFFF00' } });
  fs.writeFileSync(svgPath, svg, 'utf8');

  await QRCode.toFile(pngPath, url, { margin: 1, width: 512, color: { dark: '#000000', light: '#00000000' } });

  console.log('QR generated for:', url);
  console.log('SVG:', path.relative(ROOT, svgPath));
  console.log('PNG:', path.relative(ROOT, pngPath));
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});





