#!/usr/bin/env node
/**
 * Generador de Documentación Automática
 * Crea documentación completa del sistema basada en logs y configuraciones
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  outputFile: path.resolve(__dirname, '../Documentation/AUTO_GENERATED_SYSTEM_DOCS.md'),
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  variantsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_variants_localized_completo.json'),
  recipientsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_recipients.csv'),
};

function analyzeSystem() {
  const analysis = {
    totalSends: 0,
    totalCampaigns: 0,
    totalVariants: 0,
    totalRecipients: 0,
    dateRange: { start: null, end: null },
    campaigns: {},
    variants: {},
    errors: 0,
  };
  
  // Analyze logs
  if (fs.existsSync(CONFIG.logsFile)) {
    const lines = fs.readFileSync(CONFIG.logsFile, 'utf8').split('\n').filter(Boolean);
    const headers = lines[0]?.split(',') || [];
    const logs = lines.slice(1).map(l => {
      const parts = l.split(',');
      const obj = {};
      headers.forEach((h, i) => {
        obj[h.trim()] = parts[i]?.trim().replace(/"/g, '') || '';
      });
      return obj;
    });
    
    analysis.totalSends = logs.filter(l => l.status === 'SENT').length;
    analysis.errors = logs.filter(l => l.status === 'ERROR').length;
    
    const dates = logs.map(l => l.timestamp).filter(Boolean).sort();
    if (dates.length > 0) {
      analysis.dateRange.start = dates[0];
      analysis.dateRange.end = dates[dates.length - 1];
    }
    
    logs.forEach(l => {
      const camp = l.campaign || 'unknown';
      if (!analysis.campaigns[camp]) {
        analysis.campaigns[camp] = 0;
      }
      analysis.campaigns[camp]++;
    });
    
    analysis.totalCampaigns = Object.keys(analysis.campaigns).length;
  }
  
  // Analyze variants
  if (fs.existsSync(CONFIG.variantsFile)) {
    const variants = JSON.parse(fs.readFileSync(CONFIG.variantsFile, 'utf8'));
    analysis.totalVariants = variants.length;
    variants.forEach(v => {
      const camp = v.campaign || 'unknown';
      if (!analysis.variants[camp]) {
        analysis.variants[camp] = [];
      }
      analysis.variants[camp].push(v.variant_id);
    });
  }
  
  // Analyze recipients
  if (fs.existsSync(CONFIG.recipientsFile)) {
    const lines = fs.readFileSync(CONFIG.recipientsFile, 'utf8').split('\n').filter(Boolean);
    analysis.totalRecipients = lines.length - 1;
  }
  
  return analysis;
}

function generateDocumentation(analysis) {
  const campaignList = Object.entries(analysis.campaigns)
    .sort((a, b) => b[1] - a[1])
    .map(([name, count]) => `- **${name}**: ${count} sends`)
    .join('\n');
  
  const variantList = Object.entries(analysis.variants)
    .map(([camp, vars]) => `
#### ${camp}
${vars.map(v => `- ${v}`).join('\n')}
    `)
    .join('\n');
  
  return `# 📚 Auto-Generated System Documentation

**Generated:** ${new Date().toLocaleString()}
**System Version:** 12.0

---

## 📊 System Overview

### Statistics
- **Total Sends**: ${analysis.totalSends}
- **Total Errors**: ${analysis.errors}
- **Error Rate**: ${analysis.totalSends > 0 ? ((analysis.errors / analysis.totalSends) * 100).toFixed(2) : 0}%
- **Total Campaigns**: ${analysis.totalCampaigns}
- **Total Variants**: ${analysis.totalVariants}
- **Total Recipients**: ${analysis.totalRecipients}

### Date Range
- **Start**: ${analysis.dateRange.start || 'N/A'}
- **End**: ${analysis.dateRange.end || 'N/A'}

---

## 🎯 Active Campaigns

${campaignList || 'No campaigns tracked'}

---

## 🔀 Variants by Campaign

${variantList || 'No variants found'}

---

## 📁 File Structure

### Data Files
- \`dm_linkedin_logs.csv\` - All send logs
- \`dm_linkedin_responses.csv\` - Response tracking
- \`dm_linkedin_recipients.csv\` - Recipient database
- \`dm_linkedin_variants_localized_completo.json\` - Message variants

### Scripts
All scripts are located in \`Scripts/\` directory:
- Automation scripts
- Analysis tools
- Integration utilities

### Reports
Generated reports are in \`Reports/\` directory:
- Dashboards (HTML)
- Analytics (JSON)
- Export files

---

## ⚙️ Configuration

### Environment Variables
- \`OPENAI_API_KEY\` - For AI generation
- \`SLACK_WEBHOOK\` - For notifications
- \`API_KEY\` - For API authentication
- \`CALENDAR_TYPE\` - Calendar integration type

---

## 🔄 Common Workflows

### Daily Workflow
1. Check notifications: \`node Scripts/dm_linkedin_notifications.js check\`
2. Review dashboard: \`node Scripts/dm_linkedin_dashboard_generator.js\`
3. Schedule follow-ups: \`node Scripts/dm_linkedin_cadence_manager.js\`

### Weekly Workflow
1. Generate recommendations: \`node Scripts/dm_linkedin_recommendations.js\`
2. A/B analysis: \`node Scripts/dm_linkedin_bayesian_ab.js\`
3. Executive report: \`node Scripts/dm_linkedin_executive_report.js\`

---

## 📝 Notes

This documentation is auto-generated. For manual内容, see the main README files.

**Last Updated:** ${new Date().toISOString()}
`;
}

function ensureDir(filePath) {
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) {
    fs.mkdirSync(dir, { recursive: true });
  }
}

function main() {
  console.log('📚 Generating system documentation...\n');
  
  const analysis = analyzeSystem();
  const docs = generateDocument blockade(analysis);
  
  ensureDir(CONFIG.outputFile);
  fs.writeFileSync(CONFIG.outputFile, docs, 'utf8');
  
  console.log('✅ Documentation generated:');
  console.log(`   File: ${CONFIG.outputFile}`);
  console.log(`   Stats:`);
  console.log(`     - ${analysis.totalSends} total sends`);
  console.log(`     - ${analysis.totalCampaigns} campaigns`);
  console.log(`     - ${analysis.totalVariants} variants`);
  console.log(`     - ${analysis.totalRecipients} recipients`);
}

if (require.main === module) {
  main();
}




