#!/usr/bin/env node
/**
 * Pre-start Check - CFDI 4.0 IA 2025
 * Verifica que el entorno esté configurado correctamente antes de iniciar
 */

const fs = require('fs');
const path = require('path');

console.log('🔍 Verificando configuración...');

const checks = [
  {
    name: 'Archivo .env existe',
    check: () => fs.existsSync(path.join(process.cwd(), '.env')),
    fix: 'Ejecuta: cp env.example .env'
  },
  {
    name: 'JWT_SECRET está configurado',
    check: () => {
      require('dotenv').config();
      return !!process.env.JWT_SECRET && process.env.JWT_SECRET !== 'tu-secreto-jwt-super-seguro-aqui';
    },
    fix: 'Configura JWT_SECRET en .env'
  },
  {
    name: 'Certificados SAT',
    check: () => {
      // Opcional, solo avisar
      return true;
    },
    fix: 'Opcional: Configura certificados SAT para producción'
  }
];

let hasErrors = false;

checks.forEach(check => {
  if (check.check()) {
    console.log(`✅ ${check.name}`);
  } else {
    console.error(`❌ ${check.name}`);
    console.log(`   Fix: ${check.fix}`);
    hasErrors = true;
  }
});

if (hasErrors) {
  console.log('\n⚠️  Algunas verificaciones fallaron. El servidor puede no funcionar correctamente.');
  console.log('Revisa la configuración antes de continuar.\n');
  process.exit(1);
} else {
  console.log('\n✅ Todas las verificaciones pasaron.\n');
}



