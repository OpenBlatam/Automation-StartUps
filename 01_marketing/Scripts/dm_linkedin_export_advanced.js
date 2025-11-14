#!/usr/bin/env node
/**
 * Export Avanzado Multi-formato
 * Exporta datos a Excel, PDF, JSON estructurado
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
  recipientsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_recipients.csv'),
  outputDir: path.resolve(__dirname, '../Exports'),
  format: process.argv[2] || 'excel', // excel, json, csv-combined
};

function ensureOutputDir() {
  if (!fs.existsSync(CONFIG.outputDir)) {
    fs.mkdirSync(CONFIG.outputDir, { recursive: true });
  }
}

function parseCSV(csvFile) {
  if (!fs.existsSync(csvFile)) return [];
  const lines = fs.readFileSync(csvFile, 'utf8').split('\n').filter(Boolean);
  const headers = lines[0]?.split(',') || [];
  return lines.slice(1).map(l => {
    const parts = l.split(',');
    const obj = {};
    headers.forEach((h, i) => {
      obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
    });
    return obj;
  });
}

function exportJSON(logs, responses, recipients) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(CONFIG.outputDir, `linkedin_dms_export_${timestamp}.json`);
  
  const data = {
    exportDate: new Date().toISOString(),
    version: '9.0',
    summary: {
      totalLogs: logs.length,
      totalResponses: Object.keys(responses).length,
      totalRecipients: recipients.length,
    },
    logs,
    responses: Object.entries(responses).map(([key, value]) => ({
      recipient: key,
      ...value,
    })),
    recipients,
  };
  
  fs.writeFileSync(outputFile, JSON.stringify(data, null, 2), 'utf8');
  console.log(`✅ JSON export: ${outputFile}`);
  return outputFile;
}

function exportExcel(logs, responses, recipients) {
  // Generate CSV-like structure (Excel compatible)
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  
  // Sheet 1: Summary
  const summary = [
    'Metric,Value',
    `Total Logs,${logs.length}`,
    `Sent,${logs.filter(l => l.status === 'SENT').length}`,
    `Errors,${logs.filter(l => l.status === 'ERROR').length}`,
    `Total Responses,${Object.keys(responses).length}`,
    `Total Recipients,${recipients.length}`,
  ].join('\n');
  
  // Sheet 2: Logs
  const logsCSV = [
    Object.keys(logs[0] || {}).join(','),
    ...logs.map(l => Object.values(l).map(v => `"${v}"`).join(','))
  ].join('\n');
  
  // Sheet 3: Responses
  const responsesCSV = [
    'recipient,responded,clicked,converted',
    ...Object.entries(responses).map(([r, data]) => 
      `"${r}",${data.responded},${data.clicked},${data.converted}`
    )
  ].join('\n');
  
  // Combined export (Excel can open multiple CSVs)
  const outputFile = path.join(CONFIG.outputDir, `linkedin_dms_export_${timestamp}.csv`);
  const combined = [
    '=== SUMMARY ===',
    summary,
    '',
    '=== LOGS ===',
    logsCSV,
    '',
    '=== RESPONSES ===',
    responsesCSV,
    '',
    '=== RECIPIENTS ===',
    Object.keys(recipients[0] || {}).join(','),
    ...recipients.map(r => Object.values(r).map(v => `"${v}"`).join(',')),
  ].join('\n');
  
  fs.writeFileSync(outputFile, combined, 'utf8');
  console.log(`✅ Excel-compatible CSV export: ${outputFile}`);
  console.log(`📝 Note: Open in Excel and split manually, or use Excel import wizard`);
  return outputFile;
}

function exportCombinedCSV(logs, responses, recipients) {
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = path.join(CONFIG.outputDir, `linkedin_dms_combined_${timestamp}.csv`);
  
  // Merge logs with responses
  const merged = logs.map(log => {
    const recipient = log.recipient?.trim();
    const response = responses[recipient] || {};
    return {
      ...log,
      responded: response.responded || false,
      clicked: response.clicked || false,
      converted: response.converted || false,
    };
  });
  
  const headers = Object.keys(merged[0] || {}).join(',');
  const rows = merged.map(r => Object.values(r).map(v => `"${v}"`).join(','));
  const csv = [headers, ...rows].join('\n');
  
  fs.writeFileSync(outputFile, csv, 'utf8');
  console.log(`✅ Combined CSV export: ${outputFile}`);
  return outputFile;
}

function main() {
  ensureOutputDir();
  
  const logs = parseCSV(CONFIG.logsFile);
  const recipients = parseCSV(CONFIG.recipientsFile);
  
  // Parse responses into map
  const responsesMap = {};
  if (fs.existsSync(CONFIG.responsesFile)) {
    const responses = parseCSV(CONFIG.responsesFile);
    responses.forEach(r => {
      if (r.recipient) {
        responsesMap[r.recipient.trim()] = {
          responded: r.responded === 'true' || r.responded === '1',
          clicked: r.clicked === 'true' || r.clicked === '1',
          converted: r.converted === 'true' || r.converted === '1',
        };
      }
    });
  }
  
  console.log(`📤 Exporting in ${CONFIG.format} format...\n`);
  
  switch (CONFIG.format) {
    case 'json':
      exportJSON(logs, responsesMap, recipients);
      break;
    case 'excel':
      exportExcel(logs, responsesMap, recipients);
      break;
    case 'csv-combined':
      exportCombinedCSV(logs, responsesMap, recipients);
      break;
    default:
      console.error(`❌ Unknown format: ${CONFIG.format}`);
      console.log('Available formats: json, excel, csv-combined');
      process.exit(1);
  }
  
  console.log(`\n✅ Export complete!`);
}

if (require.main === module) {
  main();
}




