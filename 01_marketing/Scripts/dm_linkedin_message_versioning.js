#!/usr/bin/env node
/**
 * Sistema de Versionado de Mensajes
 * Trackea cambios en variantes y compara performance entre versiones
 */
const fs = require('fs');
const path = require('path');

const CONFIG = {
  variantsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_variants_localized_completo.json'),
  versionsDir: path.resolve(__dirname, '../Data_Files/Versions'),
  logsFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_logs.csv'),
  responsesFile: path.resolve(__dirname, '../Data_Files/dm_linkedin_responses.csv'),
};

function ensureVersionsDir() {
  if (!fs.existsSync(CONFIG.versionsDir)) {
    fs.mkdirSync(CONFIG.versionsDir, { recursive: true });
  }
}

function saveVersion() {
  ensureVersionsDir();
  if (!fs.existsSync(CONFIG.variantsFile)) {
    console.error('❌ Variants file not found');
    return;
  }
  
  const variants = JSON.parse(fs.readFileSync(CONFIG.variantsFile, 'utf8'));
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const versionFile = path.join(CONFIG.versionsDir, `variants-${timestamp}.json`);
  
  const version = {
    timestamp: new Date().toISOString(),
    variants,
    metadata: {
      total: variants.length,
      campaigns: [...new Set(variants.map(v => v.campaign))],
    },
  };
  
  fs.writeFileSync(versionFile, JSON.stringify(version, null, 2), 'utf8');
  console.log(`✅ Version saved: ${versionFile}`);
  return versionFile;
}

function listVersions() {
  ensureVersionsDir();
  const versions = fs.readdirSync(CONFIG.versionsDir)
    .filter(f => f.startsWith('variants-') && f.endsWith('.json'))
    .map(f => {
      const content = JSON.parse(fs.readFileSync(path.join(CONFIG.versionsDir, f), 'utf8'));
      return {
        file: f,
        timestamp: content.timestamp,
        total: content.metadata.total,
        campaigns: content.metadata.campaigns,
      };
    })
    .sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  
  console.log(`📚 Versions (${versions.length}):\n`);
  versions.forEach((v, idx) => {
    console.log(`${idx + 1}. ${v.file}`);
    console.log(`   Date: ${v.timestamp}`);
    console.log(`   Variants: ${v.total}`);
    console.log(`   Campaigns: ${v.campaigns.join(', ')}\n`);
  });
  
  return versions;
}

function compareVersions(v1File, v2File) {
  const v1Path = path.join(CONFIG.versionsDir, v1File);
  const v2Path = path.join(CONFIG.versionsDir, v2File);
  
  if (!fs.existsSync(v1Path) || !fs.existsSync(v2Path)) {
    console.error('❌ Version files not found');
    return;
  }
  
  const v1 = JSON.parse(fs.readFileSync(v1Path, 'utf8'));
  const v2 = JSON.parse(fs.readFileSync(v2Path, 'utf8'));
  
  const v1Ids = new Set(v1.variants.map(v => v.variant_id));
  const v2Ids = new Set(v2.variants.map(v => v.variant_id));
  
  const added = v2.variants.filter(v => !v1Ids.has(v.variant_id));
  const removed = v1.variants.filter(v => !v2Ids.has(v.variant_id));
  const changed = [];
  
  v1.variants.forEach(v1 => {
    const v2Match = v2.variants.find(v => v.variant_id === v1.variant_id);
    if (v2Match && v1.message !== v2Match.message) {
      changed.push({
        variant_id: v1.variant_id,
        old_message: v1.message,
        new_message: v2Match.message,
      });
    }
  });
  
  console.log(`📊 Comparison: ${v1File} vs ${v2File}\n`);
  console.log(`➕ Added: ${added.length}`);
  added.forEach(a => console.log(`   - ${a.variant_id}`));
  
  console.log(`\n➖ Removed: ${removed.length}`);
  removed.forEach(r => console.log(`   - ${r.variant_id}`));
  
  console.log(`\n✏️  Changed: ${changed.length}`);
  changed.forEach(c => {
    console.log(`   - ${c.variant_id}`);
    console.log(`     Old: ${c.old_message.substring(0, 50)}...`);
    console.log(`     New: ${c.new_message.substring(0, 50)}...`);
  });
}

function analyzeVersionPerformance(versionFile) {
  if (!fs.existsSync(CONFIG.logsFile) || !fs.existsSync(CONFIG.responsesFile)) {
    console.warn('⚠️  Logs/responses not found, skipping performance analysis');
    return;
  }
  
  // Simplified - would compare variant performance from version to current
  console.log(`📈 Performance analysis for ${versionFile}`);
  console.log('   (Full analysis requires comparing logs with version timestamps)');
}

function main() {
  const action = process.argv[2] || 'save';
  
  switch (action) {
    case 'save':
      saveVersion();
      break;
    case 'list':
      listVersions();
      break;
    case 'compare':
      const v1 = process.argv[3];
      const v2 = process.argv[4];
      if (!v1 || !v2) {
        console.error('❌ Two version files required');
        console.log('Usage: node dm_linkedin_message_versioning.js compare <v1> <v2>');
        return;
      }
      compareVersions(v1, v2);
      break;
    default:
      console.log('Usage:');
      console.log('  node dm_linkedin_message_versioning.js save         - Save current version');
      console.log('  node dm_linkedin_message_versioning.js list         - List versions');
      console.log('  node dm_linkedin_message_versioning.js compare <v1> <v2> - Compare versions');
  }
}

if (require.main === module) {
  main();
}




