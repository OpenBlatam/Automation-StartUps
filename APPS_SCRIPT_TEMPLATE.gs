/**** Apps Script Template — IA Bulk 3‑Docs + QA + Costos + Alertas ****/

const CONFIG = {
  sheetName: 'Pedidos',
  costSheetName: 'CostosIA',
  slackWebhook: 'REEMPLAZAR_SLACK_WEBHOOK_URL',
  model: 'gpt-4.1',
  maxRetries: 3,
  pauseMs: 1100,
  costPer1KIn: 0.0,   // completa según tu proveedor
  costPer1KOut: 0.0,  // completa según tu proveedor
};

function runBatch() {
  const sh = SpreadsheetApp.getActive().getSheetByName(CONFIG.sheetName);
  const values = sh.getDataRange().getValues();
  const header = values[0];
  const col = indexColumns(header, {
    id: 'ID', prompt: 'Prompt', estado: 'Estado',
    brief: 'EnlaceBrief', articulo: 'EnlaceArticulo', post: 'EnlacePost', fecha: 'Fecha'
  });

  for (let r = 1; r < values.length; r++) {
    const row = values[r];
    const estado = row[col.estado];
    const prompt = row[col.prompt];
    if (!prompt || estado !== 'pendiente') continue;

    const jobId = Utilities.getUuid();
    try {
      const outputs = ['brief', 'articulo', 'post'];
      const enlaces = outputs.map(t => crearDocIAConPostProceso(prompt, t, jobId));
      // Guardar resultados
      sh.getRange(r + 1, col.estado + 1).setValue('completado');
      sh.getRange(r + 1, col.brief + 1, 1, 3).setValues([enlaces]);
      // Costos y métricas
      const costo = calcularCosto(enlaces); // sustituir por cálculo real
      logCosto(jobId, row[col.id], CONFIG.model, 0, 0, costo);
      notifySlack(`✅ Job ${jobId} completado: ${enlaces.join(' | ')}`);
    } catch (e) {
      sh.getRange(r + 1, col.estado + 1).setValue('error');
      notifySlack(`❌ Job error: ${jobId} — ${e && e.message ? e.message : e}`);
    }
  }
}

function indexColumns(header, mapping) {
  const idx = {};
  Object.keys(mapping).forEach(k => {
    const name = mapping[k];
    idx[k] = header.indexOf(name);
    if (idx[k] < 0) throw new Error(`Columna faltante: ${name}`);
  });
  return idx;
}

function crearDocIAConPostProceso(prompt, tipo, jobId) {
  const content = withRateLimit(() => llamarIA(prompt, tipo), CONFIG.pauseMs, CONFIG.maxRetries);
  const checked = qaMinimo(content, tipo);
  const docId = crearDocumento(tipo, checked, jobId);
  return `https://docs.google.com/document/d/${docId}/edit`;
}

function llamarIA(prompt, tipo) {
  // TODO: sustituir por llamada real a tu proveedor de IA
  const salida = `[# ${tipo}]\n${prompt}\n...contenido generado...`;
  return salida;
}

function qaMinimo(texto, tipo) {
  const reglas = [
    t => t.includes('CTA') || tipo !== 'post' || t + '\nCTA: ...',
    t => !/\b(garantizado|ilimitado|100%)\b/i.test(t) || t.replace(/garantizado/gi, 'sólido'),
  ];
  return reglas.reduce((acc, rule) => rule(acc), texto);
}

function crearDocumento(titulo, contenido, jobId) {
  const doc = DocumentApp.create(`${titulo.toUpperCase()} — ${jobId}`);
  const body = doc.getBody();
  body.clear();
  body.appendParagraph(contenido);
  doc.saveAndClose();
  return doc.getId();
}

function logCosto(jobId, cliente, modelo, tokensIn, tokensOut, costoUsd) {
  const sh = SpreadsheetApp.getActive().getSheetByName(CONFIG.costSheetName) || SpreadsheetApp.getActive().insertSheet(CONFIG.costSheetName);
  if (sh.getLastRow() === 0) sh.appendRow(['JobID','Cliente','Modelo','TokensPrompt','TokensOutput','CostoUSD','DuracionSeg','Fecha']);
  sh.appendRow([jobId, cliente, modelo, tokensIn, tokensOut, costoUsd, 0, Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'yyyy-MM-dd')]);
}

function notifySlack(message) {
  try {
    if (!CONFIG.slackWebhook || CONFIG.slackWebhook === 'REEMPLAZAR_SLACK_WEBHOOK_URL') return;
    UrlFetchApp.fetch(CONFIG.slackWebhook, {
      method: 'post',
      contentType: 'application/json',
      payload: JSON.stringify({ text: message })
    });
  } catch (e) {
    // silenciar errores de alerta para no romper el flujo
  }
}

function computeHash(parts) {
  const str = JSON.stringify(parts);
  return Utilities.base64Encode(Utilities.computeDigest(Utilities.DigestAlgorithm.SHA_256, str));
}

function withRateLimit(fn, pauseMs, tries) {
  for (let i = 0; i < tries; i++) {
    try { return fn(); } catch (e) { Utilities.sleep(pauseMs * (i + 1)); }
  }
  throw new Error('Rate limit exceeded');
}
