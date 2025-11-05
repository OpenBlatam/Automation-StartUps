#!/usr/bin/env node
/**
 * Post-install Script - CFDI 4.0 IA 2025
 * Tareas después de instalar dependencias
 */

const fs = require('fs');
const path = require('path');

console.log('📦 Configurando proyecto...');

// Crear directorios necesarios
const directories = [
  'logs',
  'certificados',
  'docs',
  'backups',
  'tests'
];

directories.forEach(dir => {
  const dirPath = path.join(process.cwd(), dir);
  if (!fs.existsSync(dirPath)) {
    fs.mkdirSync(dirPath, { recursive: true });
    console.log(`✅ Directorio creado: ${dir}`);
  }
});

// Crear archivo de log inicial
const logPath = path.join(process.cwd(), 'logs', 'cfdi.log');
if (!fs.existsSync(logPath)) {
  fs.writeFileSync(logPath, `# Log iniciado: ${new Date().toISOString()}\n`, 'utf8');
  console.log('✅ Archivo de log creado');
}

// Verificar .env
const envPath = path.join(process.cwd(), '.env');
if (!fs.existsSync(envPath)) {
  const envExamplePath = path.join(process.cwd(), 'env.example');
  if (fs.existsSync(envExamplePath)) {
    fs.copyFileSync(envExamplePath, envPath);
    console.log('✅ Archivo .env creado desde env.example');
    console.log('⚠️  IMPORTANTE: Edita .env con tus configuraciones antes de iniciar el servidor');
  }
}

console.log('\n✅ Configuración completada.\n');



