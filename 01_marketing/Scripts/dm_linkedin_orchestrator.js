#!/usr/bin/env node
/**
 * Orchestrator Principal
 * Coordina todos los scripts en un flujo automatizado
 */
const { execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const CONFIG = {
  mode: process.argv[2] || 'daily', // daily, weekly, full
  dryRun: process.argv.includes('--dry-run'),
};

const SCRIPTS = {
  preSend: [
    { name: 'Recipients Cleaner', script: 'dm_linkedin_recipients_cleaner.js' },
    { name: 'QA Pre-Send', script: 'dm_linkedin_qa_pre_send.js' },
    { name: 'Health Check', script: 'dm_linkedin_health_check.js' },
  ],
  send: [
    { name: 'Sender', script: 'dm_linkedin_sender_node.js', optional: true },
  ],
  postSend: {
    daily: [
      { name: 'Dashboard Generator', script: 'dm_linkedin_dashboard_generator.js' },
      { name: 'Cadence Manager', script: 'dm_linkedin_cadence_manager.js' },
    ],
    weekly: [
      { name: 'Lead Scoring', script: 'dm_linkedin_score_from_logs.js', optional: true },
      { name: 'A/B Optimizer', script: 'dm_linkedin_ab_optimizer.js', optional: true },
      { name: 'Executive Report', script: 'dm_linkedin_executive_report.js' },
      { name: 'Response Predictor', script: 'dm_linkedin_response_predictor.js', optional: true },
      { name: 'CRM Export', script: 'dm_linkedin_export_crm.js', optional: true },
    ],
    full: [
      { name: 'Dashboard Generator', script: 'dm_linkedin_dashboard_generator.js' },
      { name: 'Cadence Manager', script: 'dm_linkedin_cadence_manager.js' },
      { name: 'Lead Scoring', script: 'dm_linkedin_score_from_logs.js', optional: true },
      { name: 'A/B Optimizer', script: 'dm_linkedin_ab_optimizer.js', optional: true },
      { name: 'Executive Report', script: 'dm_linkedin_executive_report.js' },
      { name: 'Response Predictor', script: 'dm_linkedin_response_predictor.js', optional: true },
      { name: 'CRM Export', script: 'dm_linkedin_export_crm.js', optional: true },
    ],
  },
};

function runScript(scriptName, optional = false) {
  const scriptPath = path.resolve(__dirname, scriptName);
  
  if (!fs.existsSync(scriptPath)) {
    if (optional) {
      console.log(`⏭️  Skipping optional: ${scriptName}`);
      return { success: true, skipped: true };
    }
    console.error(`❌ Script not found: ${scriptName}`);
    return { success: false, error: 'not_found' };
  }
  
  try {
    console.log(`▶️  Running: ${scriptName}...`);
    const output = execSync(`node "${scriptPath}"`, {
      encoding: 'utf8',
      stdio: 'inherit',
    });
    console.log(`✅ Completed: ${scriptName}`);
    return { success: true, output };
  } catch (e) {
    console.error(`❌ Error in ${scriptName}:`, e.message);
    return { success: false, error: e.message };
  }
}

function main() {
  console.log('🎯 LinkedIn DMs Orchestrator');
  console.log(`📅 Mode: ${CONFIG.mode}`);
  console.log(`🔧 Dry-run: ${CONFIG.dryRun ? 'yes' : 'no'}\n`);
  
  const results = {
    preSend: [],
    send: [],
    postSend: [],
    errors: [],
  };
  
  // Pre-send phase
  console.log('\n📋 Phase 1: Pre-Send\n');
  SCRIPTS.preSend.forEach(({ name, script }) => {
    const result = runScript(script);
    results.preSend.push({ name, ...result });
    if (!result.success && !result.skipped) {
      results.errors.push(`${name}: ${result.error}`);
    }
  });
  
  // Send phase (skip if dry-run)
  if (!CONFIG.dryRun && CONFIG.mode !== 'weekly') {
    console.log('\n📤 Phase 2: Send\n');
    SCRIPTS.send.forEach(({ name, script, optional }) => {
      const result = runScript(script, optional);
      results.send.push({ name, ...result });
    });
  } else {
    console.log('\n⏭️  Phase 2: Send (skipped - dry-run or weekly mode)\n');
  }
  
  // Post-send phase
  console.log('\n📊 Phase 3: Post-Send\n');
  const postSendScripts = SCRIPTS.postSend[CONFIG.mode] || SCRIPTS.postSend.daily;
  postSendScripts.forEach(({ name, script, optional }) => {
    const result = runScript(script, optional);
    results.postSend.push({ name, ...result });
    if (!result.success && !result.skipped) {
      results.errors.push(`${name}: ${result.error}`);
    }
  });
  
  // Summary
  console.log('\n' + '='.repeat(50));
  console.log('📈 Summary');
  console.log('='.repeat(50));
  console.log(`✅ Pre-send: ${results.preSend.filter(r => r.success).length}/${results.preSend.length}`);
  console.log(`✅ Send: ${results.send.filter(r => r.success).length}/${results.send.length}`);
  console.log(`✅ Post-send: ${results.postSend.filter(r => r.success).length}/${results.postSend.length}`);
  
  if (results.errors.length > 0) {
    console.log(`\n❌ Errors: ${results.errors.length}`);
    results.errors.forEach(e => console.log(`  - ${e}`));
    process.exit(1);
  } else {
    console.log('\n✅ All phases completed successfully!');
  }
}

if (require.main === module) {
  main();
}




