#!/usr/bin/env node
require('dotenv').config();
const { spawnSync } = require('child_process');
const path = require('path');

function run(cmd, args, opts={}) {
  const res = spawnSync(cmd, args, { stdio: 'inherit', cwd: opts.cwd || process.cwd(), env: process.env });
  return res.status || 0;
}

function main() {
  const root = path.resolve(__dirname, '..');
  const args = process.argv.slice(2);
  const fix = args.includes('--fix');
  const noNotify = args.includes('--no-notify');

  let failures = [];

  // 1) Setup (optional fix)
  if (fix) {
    console.log('> Setup (crear carpetas/CSVs si faltan)');
    run('node', ['Scripts/dm_linkedin_setup.js'], { cwd: root });
  }

  // 2) Health
  console.log('> Health check');
  const hc = run('node', ['Scripts/dm_linkedin_health_check_cli.js'], { cwd: root });
  if (hc !== 0) failures.push('health');

  // 3) Linter mensajes (no bloquea si no hay archivo, pero si existe y falla, marca error)
  console.log('> Linter de mensajes');
  const lint = run('node', ['Scripts/dm_linkedin_message_linter.js', '--md'], { cwd: root });
  if (lint !== 0) failures.push('linter');

  // 4) Consistency check
  console.log('> Consistency check');
  const cc = run('node', ['Scripts/dm_linkedin_consistency_check.js', '--md'], { cwd: root });
  if (cc !== 0) {
    // consistency script always exits 0 currently; keep placeholder
  }

  // 5) Suppress (optional fix)
  if (fix) {
    console.log('> Suppression (dedupe + listas)');
    run('node', ['Scripts/dm_linkedin_suppression_manager.js'], { cwd: root });
  }

  // 6) Snapshot rápido (no bloqueante)
  console.log('> KPI Snapshot (consola)');
  run('node', ['Scripts/dm_linkedin_kpi_snapshot.js', '--md'], { cwd: root });

  const failed = failures.length > 0;
  if (failed) {
    console.log(`Preflight: FALLÓ → ${failures.join(', ')}`);
    process.exit(1);
  } else {
    console.log('Preflight: OK');
  }
}

main();


