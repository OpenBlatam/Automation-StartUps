#!/usr/bin/env node
/**
 * Health Check del Sistema Completo
 * Valida integridad de archivos, configuraciones y datos
 */
const fs = require('fs');
const path = require('path');

const CHECKS = {
  requiredFiles: [
    'dm_linkedin_recipients.csv',
    'dm_linkedin_logs.csv',
    'dm_linkedin_variant_rules.json',
  ],
  optionalFiles: [
    'dm_linkedin_variants_localized_completo.json',
    'dm_linkedin_responses.csv',
    'dm_linkedin_suppression_list.csv',
  ],
  scripts: [
    'dm_linkedin_sender_node.js',
    'dm_linkedin_qa_pre_send.js',
    'dm_linkedin_recipients_cleaner.js',
    'dm_linkedin_dashboard_generator.js',
  ],
};

function checkFile(filePath, required = false) {
  const fullPath = path.resolve(__dirname, '..', filePath);
  const exists = fs.existsSync(fullPath);
  const size = exists ? fs.statSync(fullPath).size : 0;
  return {
    name: filePath,
    exists,
    required,
    size,
    status: exists ? (required ? 'ok' : 'ok') : (required ? 'missing' : 'optional_missing'),
  };
}

function checkCSVStructure(filePath) {
  const fullPath = path.resolve(__dirname, '..', filePath);
  if (!fs.existsSync(fullPath)) return null;
  
  try {
    const content = fs.readFileSync(fullPath, 'utf8');
    const lines = content.split('\n').filter(Boolean);
    if (lines.length < 1) return { valid: false, error: 'Empty file' };
    
    const headers = lines[0].split(',');
    const rowCount = lines.length - 1;
    
    return {
      valid: true,
      headers: headers.length,
      rows: rowCount,
      hasData: rowCount > 0,
    };
  } catch (e) {
    return { valid: false, error: e.message };
  }
}

function checkJSONStructure(filePath) {
  const fullPath = path.resolve(__dirname, '..', filePath);
  if (!fs.existsSync(fullPath)) return null;
  
  try {
    const content = fs.readFileSync(fullPath, 'utf8');
    const parsed = JSON.parse(content);
    return {
      valid: true,
      type: Array.isArray(parsed) ? 'array' : 'object',
      length: Array.isArray(parsed) ? parsed.length : Object.keys(parsed).length,
    };
  } catch (e) {
    return { valid: false, error: e.message };
  }
}

function main() {
  console.log('🔍 LinkedIn DMs System Health Check\n');
  
  const results = {
    files: [],
    scripts: [],
    errors: [],
    warnings: [],
  };
  
  // Check required files
  CHECKS.requiredFiles.forEach(file => {
    const check = checkFile(file, true);
    results.files.push(check);
    
    if (file.endsWith('.csv')) {
      const struct = checkCSVStructure(file);
      if (struct && !struct.valid) {
        results.errors.push(`${file}: Invalid CSV - ${struct.error}`);
      } else if (struct && !struct.hasData && check.exists) {
        results.warnings.push(`${file}: Empty (no data rows)`);
      }
    } else if (file.endsWith('.json')) {
      const struct = checkJSONStructure(file);
      if (struct && !struct.valid) {
        results.errors.push(`${file}: Invalid JSON - ${struct.error}`);
      }
    }
    
    if (!check.exists) {
      results.errors.push(`${file}: REQUIRED FILE MISSING`);
    }
  });
  
  // Check optional files
  CHECKS.optionalFiles.forEach(file => {
    const check = checkFile(file, false);
    results.files.push(check);
    if (!check.exists) {
      results.warnings.push(`${file}: Optional file missing (OK if not used)`);
    }
  });
  
  // Check scripts
  CHECKS.scripts.forEach(script => {
    const check = checkFile(`Scripts/${script}`, false);
    results.scripts.push(check);
    if (!check.exists) {
      results.warnings.push(`Scripts/${script}: Missing (optional automation)`);
    }
  });
  
  // Print results
  console.log('📁 Files:');
  results.files.forEach(f => {
    const icon = f.exists ? '✅' : (f.required ? '❌' : '⚠️ ');
    const size = f.size > 0 ? `(${(f.size / 1024).toFixed(1)}KB)` : '';
    console.log(`  ${icon} ${f.name} ${size}`);
  });
  
  console.log('\n🛠️  Scripts:');
  results.scripts.forEach(s => {
    const icon = s.exists ? '✅' : '⚠️ ';
    console.log(`  ${icon} ${s.name}`);
  });
  
  if (results.errors.length > 0) {
    console.log('\n❌ Errors:');
    results.errors.forEach(e => console.log(`  ${e}`));
    process.exit(1);
  }
  
  if (results.warnings.length > 0) {
    console.log('\n⚠️  Warnings:');
    results.warnings.forEach(w => console.log(`  ${w}`));
  }
  
  if (results.errors.length === 0) {
    console.log('\n✅ System Health Check: PASSED');
  }
}

if (require.main === module) {
  main();
}




