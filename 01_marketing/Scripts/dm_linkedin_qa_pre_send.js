#!/usr/bin/env node
/**
 * QA Pre-Envío Automatizado
 * Valida estructura antes de enviar DMs
 */
const fs = require('fs');
const path = require('path');

function checkRecipients() {
  const fp = path.resolve(__dirname, 'dm_linkedin_recipients.csv');
  if (!fs.existsSync(fp)) return [{level:'error', msg:'Recipients CSV missing'}];
  const lines = fs.readFileSync(fp, 'utf8').split('\n');
  const headers = lines[0]?.toLowerCase().split(',') || [];
  const issues = [];
  if (!headers.includes('name')) issues.push({level:'error', msg:'Missing column: name'});
  if (!headers.includes('profileurl')) issues.push({level:'error', msg:'Missing column: profileUrl'});
  if (lines.length < 2) issues.push({level:'error', msg:'No recipients found'});
  return issues;
}

function checkVariants() {
  const fp = path.resolve(__dirname, 'dm_linkedin_export_json_examples.json');
  if (!fs.existsSync(fp)) return [{level:'warning', msg:'Variants JSON missing (will use fallback)'}];
  try {
    const data = JSON.parse(fs.readFileSync(fp, 'utf8'));
    if (!Array.isArray(data) || !data.length) return [{level:'error', msg:'Variants JSON empty'}];
    const issues = [];
    data.forEach((v,i) => {
      if (!v.variant_id && !v.variant && !v.utm_content) issues.push({level:'warning', msg:`Variant ${i} missing identifier`});
      if (!v.message && !v.message_A) issues.push({level:'error', msg:`Variant ${i} missing message`});
      if (!v.link && !v.campaign) issues.push({level:'warning', msg:`Variant ${i} missing link/campaign`});
    });
    return issues;
  } catch(e) {
    return [{level:'error', msg:`Invalid JSON: ${e.message}`}];
  }
}

function main() {
  const all = [...checkRecipients(), ...checkVariants()];
  const errors = all.filter(x => x.level === 'error');
  const warnings = all.filter(x => x.level === 'warning');
  if (errors.length) {
    console.error('❌ Errors:', errors.map(e => e.msg).join('\n'));
    process.exit(1);
  }
  if (warnings.length) console.warn('⚠️  Warnings:', warnings.map(w => w.msg).join('\n'));
  else console.log('✅ Pre-send QA passed');
}

if (require.main === module) main();

