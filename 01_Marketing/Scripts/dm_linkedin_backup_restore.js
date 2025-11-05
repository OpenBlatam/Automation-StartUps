#!/usr/bin/env node
/**
 * Sistema de Backup y Restore
 * Backups automáticos y restauración de datos
 */
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const CONFIG = {
  backupDir: path.resolve(__dirname, '../Backups'),
  dataDir: path.resolve(__dirname, '../Data_Files'),
  filesToBackup: [
    'dm_linkedin_recipients.csv',
    'dm_linkedin_logs.csv',
    'dm_linkedin_responses.csv',
    'dm_linkedin_variants_localized_completo.json',
    'dm_linkedin_suppression_list.csv',
    'dm_linkedin_company_suppression.csv',
  ],
};

const ACTION = process.argv[2] || 'backup'; // backup, restore, list

function ensureBackupDir() {
  if (!fs.existsSync(CONFIG.backupDir)) {
    fs.mkdirSync(CONFIG.backupDir, { recursive: true });
  }
}

function createBackup() {
  ensureBackupDir();
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const backupPath = path.join(CONFIG.backupDir, `backup-${timestamp}`);
  fs.mkdirSync(backupPath, { recursive: true });
  
  let backedUp = 0;
  CONFIG.filesToBackup.forEach(file => {
    const sourcePath = path.join(CONFIG.dataDir, file);
    if (fs.existsSync(sourcePath)) {
      const destPath = path.join(backupPath, file);
      fs.copyFileSync(sourcePath, destPath);
      backedUp++;
      console.log(`✅ Backed up: ${file}`);
    } else {
      console.log(`⚠️  File not found: ${file}`);
    }
  });
  
  // Create backup manifest
  const manifest = {
    timestamp: new Date().toISOString(),
    files: CONFIG.filesToBackup.filter(f => fs.existsSync(path.join(CONFIG.dataDir, f))),
    version: '8.0',
  };
  
  fs.writeFileSync(
    path.join(backupPath, 'manifest.json'),
    JSON.stringify(manifest, null, 2),
    'utf8'
  );
  
  console.log(`\n✅ Backup complete: ${backupPath}`);
  console.log(`📦 Backed up ${backedUp} files`);
  return backupPath;
}

function listBackups() {
  ensureBackupDir();
  const backups = fs.readdirSync(CONFIG.backupDir)
    .filter(item => {
      const itemPath = path.join(CONFIG.backupDir, item);
      return fs.statSync(itemPath).isDirectory() && item.startsWith('backup-');
    })
    .map(item => {
      const itemPath = path.join(CONFIG.backupDir, item);
      const manifestPath = path.join(itemPath, 'manifest.json');
      let manifest = {};
      if (fs.existsSync(manifestPath)) {
        manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
      }
      return {
        name: item,
        path: itemPath,
        timestamp: manifest.timestamp || 'unknown',
        files: manifest.files?.length || 0,
      };
    })
    .sort((a, b) => b.timestamp.localeCompare(a.timestamp));
  
  if (backups.length === 0) {
    console.log('📦 No backups found');
    return [];
  }
  
  console.log(`📦 Available backups (${backups.length}):\n`);
  backups.forEach((backup, idx) => {
    console.log(`${idx + 1}. ${backup.name}`);
    console.log(`   Date: ${backup.timestamp}`);
    console.log(`   Files: ${backup.files}`);
    console.log(`   Path: ${backup.path}\n`);
  });
  
  return backups;
}

function restore(backupName) {
  ensureBackupDir();
  const backupPath = path.join(CONFIG.backupDir, backupName);
  
  if (!fs.existsSync(backupPath)) {
    console.error(`❌ Backup not found: ${backupName}`);
    return false;
  }
  
  const manifestPath = path.join(backupPath, 'manifest.json');
  if (!fs.existsSync(manifestPath)) {
    console.error(`❌ Manifest not found in backup`);
    return false;
  }
  
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  console.log(`📦 Restoring backup: ${backupName}`);
  console.log(`📅 Created: ${manifest.timestamp}`);
  
  let restored = 0;
  manifest.files.forEach(file => {
    const sourcePath = path.join(backupPath, file);
    const destPath = path.join(CONFIG.dataDir, file);
    
    if (fs.existsSync(sourcePath)) {
      // Create backup of current file before restoring
      if (fs.existsSync(destPath)) {
        const currentBackup = `${destPath}.pre-restore-${Date.now()}`;
        fs.copyFileSync(destPath, currentBackup);
        console.log(`💾 Backed up current: ${file}`);
      }
      
      fs.copyFileSync(sourcePath, destPath);
      restored++;
      console.log(`✅ Restored: ${file}`);
    }
  });
  
  console.log(`\n✅ Restore complete: ${restored} files restored`);
  return true;
}

function main() {
  switch (ACTION) {
    case 'backup':
      createBackup();
      break;
    case 'list':
      listBackups();
      break;
    case 'restore':
      const backupName = process.argv[3];
      if (!backupName) {
        console.error('❌ Backup name required');
        console.log('Usage: node dm_linkedin_backup_restore.js restore <backup-name>');
        console.log('\nAvailable backups:');
        listBackups();
        return;
      }
      restore(backupName);
      break;
    default:
      console.log('Usage:');
      console.log('  node dm_linkedin_backup_restore.js backup   - Create backup');
      console.log('  node dm_linkedin_backup_restore.js list      - List backups');
      console.log('  node dm_linkedin_backup_restore.js restore <name> - Restore backup');
  }
}

if (require.main === module) {
  main();
}




