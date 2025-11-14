#!/usr/bin/env node
/**
 * Export a CRM (HubSpot/Salesforce format)
 * - Input: dm_linkedin_logs.csv
 * - Output: dm_linkedin_crm_export.csv (campos estándar CRM)
 */
const fs = require('fs');
const path = require('path');

const IN = path.resolve(__dirname, 'dm_linkedin_logs.csv');
const OUT = path.resolve(__dirname, 'dm_linkedin_crm_export.csv');

function parseLogs() {
  if (!fs.existsSync(IN)) return [];
  const lines = fs.readFileSync(IN, 'utf8').split('\n').filter(Boolean);
  lines.shift();
  return lines.map(l => {
    const parts = l.split(',');
    return {
      timestamp: parts[0],
      recipient: JSON.parse(parts[1] || '""'),
      variant: JSON.parse(parts[2] || '""'),
      campaign: JSON.parse(parts[3] || '""'),
      status: JSON.parse(parts[4] || '""'),
    };
  });
}

function main() {
  const rows = parseLogs();
  const header = 'Email,FirstName,LastName,Company,LinkedIn_Profile_URL,Lead_Source,Marketing_Campaign,UTM_Source,UTM_Medium,UTM_Campaign,UTM_Content,Status,Last_Contact_Date';
  const out = [header];
  const seen = new Map();
  rows.forEach(r => {
    if (!r.recipient) return;
    const key = r.recipient;
    if (seen.has(key) && seen.get(key).timestamp > r.timestamp) return;
    seen.set(key, r);
  });
  for (const [url, data] of seen.entries()) {
    const match = url.match(/linkedin\.com\/in\/([^\/\?]+)/);
    const name = match ? match[1] : '';
    const campaign = data.campaign || '';
    const parts = campaign.split('_');
    const utmCampaign = campaign;
    const utmContent = data.variant || '';
    const status = data.status === 'SENT' ? 'Contacted' : data.status;
    out.push([
      '', // Email (empty, populate from your DB)
      '', // FirstName
      '', // LastName
      '', // Company
      url,
      'LinkedIn DM',
      campaign,
      'linkedin',
      'dm',
      utmCampaign,
      utmContent,
      status,
      data.timestamp
    ].join(','));
  }
  fs.writeFileSync(OUT, out.join('\n'), 'utf8');
  console.log('CRM export written to', OUT);
}

if (require.main === module) main();

