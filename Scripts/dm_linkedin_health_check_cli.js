#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir, fileExists } = require('./utils_fs');

const root = path.resolve(__dirname, '..');

const EXPECT = {
  sendLog: {
    path: path.resolve(root, 'Logs', 'dm_send_log.csv'),
    headers: ['timestamp','recipient','variant','campaign','status','error']
  },
  respLog: {
    path: path.resolve(root, 'Logs', 'dm_responses.csv'),
    headers: ['recipient','variant','responded','clicked','converted']
  }
};

function readFirstLine(fp) {
  try {
    const raw = fs.readFileSync(fp, 'utf8');
    const line = raw.split(/\r?\n/).find(Boolean) || '';
    return line.trim();
  } catch (_) {
    return '';
  }
}

function checkHeaders(fp, expectedHeaders) {
  const first = readFirstLine(fp);
  if (!first) return { ok: false, reason: 'archivo vacío o ilegible' };
  const got = first.split(',').map(s => s.trim());
  const ok = expectedHeaders.every((h, i) => got[i] === h);
  return ok ? { ok: true } : { ok: false, reason: `encabezados esperados: ${expectedHeaders.join(', ')}, encontrados: ${got.join(', ')}` };
}

function main() {
  let ok = true;

  // Ensure base dirs
  ensureDir(path.resolve(root, 'Logs'));
  ensureDir(path.resolve(root, '01_Marketing', 'Reports'));

  console.log('— Health Check: Archivos requeridos —');

  Object.entries(EXPECT).forEach(([key, cfg]) => {
    if (!fileExists(cfg.path)) {
      console.log(`✗ Falta: ${path.relative(root, cfg.path)}`);
      ok = false;
    } else {
      console.log(`✓ Existe: ${path.relative(root, cfg.path)}`);
      const h = checkHeaders(cfg.path, cfg.headers);
      if (!h.ok) {
        console.log(`  ✗ Encabezados: ${h.reason}`);
        ok = false;
      } else {
        console.log('  ✓ Encabezados correctos');
      }
    }
  });

  const slack = process.env.SLACK_WEBHOOK_URL ? 'definido' : 'no definido';
  console.log(`— Slack Webhook: ${slack}`);

  if (!ok) {
    console.log('Estado: PROBLEMAS detectados. Corrige y vuelve a ejecutar.');
    process.exit(1);
  } else {
    console.log('Estado: OK. Listo para operar.');
  }
}

main();


