#!/usr/bin/env node
require('dotenv').config();
const fs = require('fs');
const path = require('path');
const { ensureDir } = require('./utils_fs');

const root = path.resolve(__dirname, '..');
const dirs = [
  path.resolve(root, '01_Marketing', 'Reports'),
  path.resolve(root, 'Logs')
];

dirs.forEach(d => ensureDir(d));

const sendLog = path.resolve(root, 'Logs', 'dm_send_log.csv');
const respLog = path.resolve(root, 'Logs', 'dm_responses.csv');

if (!fs.existsSync(sendLog)) {
  fs.writeFileSync(sendLog, 'timestamp,recipient,variant,campaign,status,error\n', 'utf8');
}
if (!fs.existsSync(respLog)) {
  fs.writeFileSync(respLog, 'recipient,variant,responded,clicked,converted\n', 'utf8');
}

console.log('Setup listo. Directorios básicos y CSVs verificados/creados.');


