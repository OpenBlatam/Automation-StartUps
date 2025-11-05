#!/usr/bin/env node

/**
 * Safe LinkedIn DM Sender (Template)
 * - Throttling (messages/min)
 * - Retries with backoff
 * - Logging to CSV
 * - Dry-run mode
 *
 * NOTE: This is a template. Integrate with your own LinkedIn API/automation layer.
 */

const fs = require('fs');
const path = require('path');

// Config
const CONFIG = {
  messagesPerMinute: 10, // Respect limits (adjust lower if needed)
  maxRetries: 3,
  backoffMs: 60000, // 60s between retries per message
  dryRun: true, // set to false to actually send
  logFile: path.resolve(__dirname, 'dm_linkedin_logs.csv'),
  suppressionFile: path.resolve(__dirname, 'dm_linkedin_suppression_list.csv'),
  slackWebhook: '', // optional: https://hooks.slack.com/services/...
};

// Minimal CSV logger
function ensureLogHeaders() {
  if (!fs.existsSync(CONFIG.logFile)) {
    fs.writeFileSync(
      CONFIG.logFile,
      'timestamp,recipient,variant,campaign,status,error\n',
      'utf8'
    );
  }
}

function logEntry({ recipient, variant, campaign, status, error = '' }) {
  const line = [
    new Date().toISOString(),
    JSON.stringify(recipient),
    JSON.stringify(variant),
    JSON.stringify(campaign),
    JSON.stringify(status),
    JSON.stringify(error)
  ].join(',') + '\n';
  fs.appendFileSync(CONFIG.logFile, line, 'utf8');
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function loadSuppressionSet() {
  const set = new Set();
  if (!CONFIG.suppressionFile || !fs.existsSync(CONFIG.suppressionFile)) return set;
  const lines = fs.readFileSync(CONFIG.suppressionFile, 'utf8').split('\n').slice(1).filter(Boolean);
  const now = Date.now();
  for (const line of lines) {
    const [profileUrl, untilIso] = line.split(',');
    const until = Date.parse(untilIso?.trim());
    if (profileUrl && (!untilIso || isNaN(until) || until > now)) set.add(profileUrl.trim());
  }
  return set;
}

async function sendSlackAlert(summary) {
  if (!CONFIG.slackWebhook) return;
  try {
    const payload = { text: summary };
    const res = await fetch(CONFIG.slackWebhook, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) });
    if (!res.ok) {
      // ignore errors silently in alerts
    }
  } catch (_) {}
}

// Placeholder: Implement your actual send via API/automation tool
async function sendLinkedInDM({ profileUrl, message }) {
  // Integrate here with your automation layer (e.g., custom API, browser automation)
  // Throw on failure to trigger retry
  if (CONFIG.dryRun) return { ok: true, dryRun: true };
  // Example:
  // const res = await fetch('https://your-sender/api/send', { method: 'POST', body: JSON.stringify({ profileUrl, message }) });
  // if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return { ok: true };
}

async function sendWithRetry(item) {
  let attempt = 0;
  while (attempt <= CONFIG.maxRetries) {
    try {
      const res = await sendLinkedInDM(item);
      return res;
    } catch (err) {
      attempt += 1;
      if (attempt > CONFIG.maxRetries) throw err;
      await sleep(CONFIG.backoffMs);
    }
  }
}

function loadRules() {
  const rulesPath = path.resolve(__dirname, 'dm_linkedin_variant_rules.json');
  if (fs.existsSync(rulesPath)) {
    try { return JSON.parse(fs.readFileSync(rulesPath, 'utf8')); } catch { return null; }
  }
  return null;
}

function chooseVariantId({ rules, industry, seniority, hourLocal }) {
  if (!rules) return null;
  const picks = [];
  if (industry && rules.industry && rules.industry[industry]) picks.push(...rules.industry[industry]);
  if (seniority && rules.seniority && rules.seniority[seniority]) picks.push(...rules.seniority[seniority]);
  if (typeof hourLocal === 'number' && rules.timing) {
    const [bhStart, bhEnd] = rules.defaults?.business_hours || [9,17];
    const bucket = hourLocal < bhStart ? 'morning' : (hourLocal <= bhEnd ? 'afternoon' : 'evening');
    if (rules.timing[bucket]) picks.push(...rules.timing[bucket]);
  }
  return picks[0] || rules.defaults?.fallback_variant || null;
}

function scanMessageCompliance(text) {
  const res = { ok: true, warnings: [] };
  if (!text || text.length < 10) res.warnings.push('Mensaje muy corto');
  if (text.length > 1200) res.warnings.push('Mensaje demasiado largo');
  const risky = [/garantizad/i, /100%/i, /sin riesgo/i];
  if (risky.some(r=>r.test(text))) res.warnings.push('Claims potencialmente riesgosos');
  if (!/stop/i.test(text)) res.warnings.push('Falta opt-out ("stop")');
  res.ok = res.warnings.length === 0;
  return res;
}

async function main() {
  const jsonPath = path.resolve(__dirname, 'dm_linkedin_export_json_examples.json');
  const data = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
  const rules = loadRules();

  // Example input list of recipients
  const recipientsPath = path.resolve(__dirname, 'dm_linkedin_recipients.csv');
  if (!fs.existsSync(recipientsPath)) {
    console.error('Missing recipients file: dm_linkedin_recipients.csv');
    process.exit(1);
  }
  const recipientsRaw = fs
    .readFileSync(recipientsPath, 'utf8')
    .split('\n')
    .slice(1)
    .filter(Boolean)
    .map(line => {
      const [name, profileUrl, variantId, industry, seniority, hourLocal, company] = line.split(',');
      return {
        name: name?.trim(),
        profileUrl: profileUrl?.trim(),
        variantId: variantId?.trim(),
        industry: industry?.trim()?.toLowerCase(),
        seniority: seniority?.trim()?.toLowerCase(),
        hourLocal: hourLocal ? Number(hourLocal) : undefined,
        company: company?.trim()?.toLowerCase(),
      };
    });

  // Dedupe recipients by profileUrl (keep first occurrence)
  const seen = new Set();
  const recipients = recipientsRaw.filter(r => {
    if (!r.profileUrl) return false;
    if (seen.has(r.profileUrl)) return false;
    seen.add(r.profileUrl);
    return true;
  });

  ensureLogHeaders();

  const intervalMs = Math.ceil(60000 / Math.max(1, CONFIG.messagesPerMinute));
  const suppression = loadSuppressionSet();
  // Company suppression CSV optional: dm_linkedin_company_suppression.csv (company,until_iso)
  const companySuppSet = (function(){
    const fp = path.resolve(__dirname, 'dm_linkedin_company_suppression.csv');
    const set = new Set();
    if (!fs.existsSync(fp)) return set;
    const now = Date.now();
    const lines = fs.readFileSync(fp, 'utf8').split('\n').slice(1).filter(Boolean);
    for (const line of lines) {
      const [company, untilIso] = line.split(',');
      const until = Date.parse((untilIso||'').trim());
      if (company && (!untilIso || isNaN(until) || until > now)) set.add(company.trim().toLowerCase());
    }
    return set;
  })();
  let sentCount = 0, skippedSupp = 0, errors = 0, skippedCompliance = 0;

  for (const rec of recipients) {
    if (suppression.has(rec.profileUrl) || (rec.company && companySuppSet.has(rec.company))) {
      logEntry({ recipient: rec.profileUrl, variant: rec.variantId || 'AUTO', campaign: 'N/A', status: 'SKIPPED_SUPPRESSED', error: '' });
      skippedSupp++;
      await sleep(intervalMs);
      continue;
    }

    let chosenId = rec.variantId;
    if (!chosenId) chosenId = chooseVariantId({ rules, industry: rec.industry, seniority: rec.seniority, hourLocal: rec.hourLocal });
    const variant = data.find(v => v.variant === chosenId || v.variant_id === chosenId || v.utm_content === chosenId) || data[0];
    // Locale-aware message fallback
    const localeColIdx = 7; // if you extend recipients CSV to include locale at col 8
    let locale = undefined;
    // Not parsing here to avoid changing parsing index; you can extend recipients file to pass locale.
    const localeKey = (locale||'').toLowerCase().replace('-', '_');
    const localizedMsg = localeKey && (variant[`message_${localeKey}`] || '');
    const msg = localizedMsg?.replace('[Nombre]', rec.name)
      || variant.message?.replace('[Nombre]', rec.name)
      || variant.message_A?.replace('[Nombre]', rec.name)
      || '';
    const fullMessage = `${msg}\n\n${variant.link}\n\n${variant.opt_out}`;
    const compliance = scanMessageCompliance(fullMessage);
    if (!compliance.ok) {
      logEntry({ recipient: rec.profileUrl, variant: chosenId || rec.variantId || 'AUTO', campaign: variant.campaign || 'N/A', status: 'SKIPPED_COMPLIANCE', error: compliance.warnings.join(' | ') });
      skippedCompliance++;
      await sleep(intervalMs);
      continue;
    }

    const payload = {
      profileUrl: rec.profileUrl,
      message: fullMessage,
    };

    try {
      const res = await sendWithRetry(payload);
      logEntry({ recipient: rec.profileUrl, variant: chosenId || rec.variantId || 'AUTO', campaign: variant.campaign || 'N/A', status: res.ok ? 'SENT' : 'FAILED' });
      if (res.ok) sentCount++; else errors++;
    } catch (err) {
      logEntry({ recipient: rec.profileUrl, variant: chosenId || rec.variantId || 'AUTO', campaign: variant.campaign || 'N/A', status: 'ERROR', error: err.message });
      errors++;
    }

    await sleep(intervalMs);
  }

  console.log('Done');
  // Optional Slack summary
  const summary = `DM run: sent=${sentCount}, skipped_supp=${skippedSupp}, skipped_compliance=${skippedCompliance}, errors=${errors}`;
  await sendSlackAlert(summary);
}

if (require.main === module) {
  main().catch(err => {
    console.error(err);
    process.exit(1);
  });
}
