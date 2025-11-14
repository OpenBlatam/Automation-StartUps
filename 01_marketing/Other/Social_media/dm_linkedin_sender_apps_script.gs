/**
 * Apps Script: Safe DM Sender (Template)
 * - Reads from Sheet: Recipients (name, profileUrl, variantId)
 * - Pulls variants from a JSON pasted in another sheet
 * - Throttling + Logs sheet
 * NOTE: You must connect to your sending method (API/automation) in sendDm_().
 */

function CONFIG_() {
  return {
    sheetData: 'Recipients', // name, profileUrl, variantId
    sheetVariants: 'Variants', // columns: variant_id, message_A, message_B, link, opt_out, campaign
    sheetLogs: 'Logs',
    messagesPerMinute: 8,
    maxRetries: 3,
    backoffMs: 60000,
    dryRun: true,
    slackWebhook: '', // opcional: https://hooks.slack.com/services/...
  };
}

function setupSheets_() {
  const ss = SpreadsheetApp.getActive();
  if (!ss.getSheetByName(CONFIG_().sheetLogs)) {
    const sh = ss.insertSheet(CONFIG_().sheetLogs);
    sh.getRange(1,1,1,6).setValues([["timestamp","recipient","variant","campaign","status","error"]]);
  }
}

function log_(recipient, variant, campaign, status, error) {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(CONFIG_().sheetLogs);
  sh.appendRow([new Date(), recipient, variant, campaign, status, error || '']);
}

function sleepMs_(ms) {
  Utilities.sleep(ms);
}

function mapVariants_() {
  const ss = SpreadsheetApp.getActive();
  const sh = ss.getSheetByName(CONFIG_().sheetVariants);
  const values = sh.getDataRange().getValues();
  const headers = values.shift();
  const idx = (key) => headers.indexOf(key);
  const byId = {};
  values.forEach(row => {
    const v = {
      variant_id: row[idx('variant_id')],
      message_A: row[idx('message_A')],
      message_B: row[idx('message_B')],
      link: row[idx('link')],
      opt_out: row[idx('opt_out')],
      campaign: row[idx('campaign')]
    };
    byId[v.variant_id] = v;
  });
  return byId;
}

function sendDm_(profileUrl, message) {
  // TODO: Integrate with your sending mechanism.
  // This function should send the DM and return true/false.
  // Placeholder:
  if (CONFIG_().dryRun) return true;
  // Example: call your API via UrlFetchApp.fetch(...)
  return true;
}

function chooseVariantIdSheets_(rules, industry, seniority, hourLocal, locale) {
  if (!rules) return null;
  const picks = [];
  if (industry && rules.industry && rules.industry[industry]) picks.push.apply(picks, rules.industry[industry]);
  if (seniority && rules.seniority && rules.seniority[seniority]) picks.push.apply(picks, rules.seniority[seniority]);
  if (typeof hourLocal === 'number' && rules.timing) {
    var bh = (rules.defaults && rules.defaults.business_hours) || [9,17];
    var bucket = hourLocal < bh[0] ? 'morning' : (hourLocal <= bh[1] ? 'afternoon' : 'evening');
    if (rules.timing[bucket]) picks.push.apply(picks, rules.timing[bucket]);
  }
  if (locale && rules.locale && rules.locale[locale]) {
    var loc = rules.locale[locale];
    if (loc.priority) picks.push.apply(picks, loc.priority);
  }
  return picks[0] || (rules.defaults && rules.defaults.fallback_variant) || null;
}

function parseRules_() {
  var ss = SpreadsheetApp.getActive();
  var sh = ss.getSheetByName('Rules');
  if (!sh) return null;
  try {
    var json = sh.getRange(1,1).getValue();
    return JSON.parse(json);
  } catch(e) { return null; }
}

function sendBatch() {
  setupSheets_();
  const cfg = CONFIG_();
  const ss = SpreadsheetApp.getActive();
  const dataSh = ss.getSheetByName(cfg.sheetData);
  const values = dataSh.getDataRange().getValues();
  const headers = values.shift();
  const h = (k) => headers.indexOf(k);

  const variants = mapVariants_();
  const rules = parseRules_();
  const intervalMs = Math.ceil(60000 / Math.max(1, cfg.messagesPerMinute));

  var suppressionSet = (function(){
    var sh = ss.getSheetByName('Suppression');
    var set = {};
    if (!sh) return set;
    var vals = sh.getDataRange().getValues();
    vals.shift();
    var now = new Date().getTime();
    vals.forEach(function(r){
      var url = String(r[0]||'').trim();
      var until = r[1] ? new Date(r[1]).getTime() : null;
      if (url && (!until || until > now)) set[url] = true;
    });
    return set;
  })();

  var seen = {};

  var totals = { sent:0, failed:0, error:0, skippedSupp:0, skippedDedupe:0 };
  values.forEach(row => {
    const name = row[h('name')];
    const profileUrl = row[h('profileUrl')];
    var variantId = row[h('variantId')];
    var industry = h('industry')>-1 ? String(row[h('industry')]||'').toLowerCase() : '';
    var seniority = h('seniority')>-1 ? String(row[h('seniority')]||'').toLowerCase() : '';
    var hourLocal = h('hourLocal')>-1 ? Number(row[h('hourLocal')]) : undefined;
    var locale = h('locale')>-1 ? String(row[h('locale')]||'').toLowerCase() : '';
    if (!name || !profileUrl) return;
    if (seen[profileUrl]) { log_(profileUrl, variantId || 'AUTO', '', 'SKIPPED_DEDUPE', ''); totals.skippedDedupe++; return; }
    seen[profileUrl] = true;
    if (suppressionSet[profileUrl]) { log_(profileUrl, variantId || 'AUTO', '', 'SKIPPED_SUPPRESSED', ''); totals.skippedSupp++; return; }
    if (!variantId) variantId = chooseVariantIdSheets_(rules, industry, seniority, hourLocal, locale);

    const v = variants[variantId] || variants[Object.keys(variants)[0]];
    // Locale-aware messages if present in Variants sheet
    var lk = (locale||'').toLowerCase().replace('-', '_');
    var msgLocale = lk && v['message_'+lk] ? v['message_'+lk] : '';
    const msgBase = (msgLocale || v.message_A || v.message_B || '').replace('[Nombre]', name);
    const message = msgBase + '\n\n' + v.link + '\n\n' + (v.opt_out || '');

    let status = 'SENT', err = '';
    try {
      const ok = sendDm_(profileUrl, message);
      if (!ok) status = 'FAILED';
    } catch (e) {
      status = 'ERROR';
      err = e && e.message || String(e);
    }

    log_(profileUrl, variantId || 'AUTO', v.campaign || '', status, err);
    if (status==='SENT') totals.sent++; else if (status==='FAILED') totals.failed++; else if (status==='ERROR') totals.error++;
    sleepMs_(intervalMs);
  });

  if (CONFIG_().slackWebhook) {
    try {
      var payload = { text: 'DM run (Sheets): sent='+totals.sent+', skipped_supp='+totals.skippedSupp+', skipped_dedupe='+totals.skippedDedupe+', failed='+totals.failed+', errors='+totals.error };
      UrlFetchApp.fetch(CONFIG_().slackWebhook, { method: 'post', contentType: 'application/json', payload: JSON.stringify(payload), muteHttpExceptions: true });
    } catch (_) {}
  }
}
