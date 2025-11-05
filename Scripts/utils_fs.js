const fs = require('fs');
const path = require('path');

function ensureDir(dirPath) {
  try {
    if (!fs.existsSync(dirPath)) {
      fs.mkdirSync(dirPath, { recursive: true });
    }
    return true;
  } catch (_) {
    return false;
  }
}

function fileExists(filePath) {
  try {
    return fs.existsSync(filePath);
  } catch (_) {
    return false;
  }
}

function parseCliFlags() {
  const args = process.argv.slice(2);
  const flags = new Set(args.filter(a => a.startsWith('--')));
  const outArg = args.find(a => a.startsWith('--out='));
  const outPath = outArg ? outArg.split('=')[1] : undefined;
  const inArg = args.find(a => a.startsWith('--in='));
  const inPath = inArg ? inArg.split('=')[1] : undefined;
  const minResp = Number(process.env.ALERT_MIN_RESP_RATE || '0');
  const maxErr = Number(process.env.ALERT_MAX_ERROR_RATE || '100');
  const fromArg = args.find(a => a.startsWith('--from='));
  const toArg = args.find(a => a.startsWith('--to='));
  const fromDate = fromArg ? new Date(fromArg.split('=')[1]) : undefined;
  const toDate = toArg ? new Date(toArg.split('=')[1]) : undefined;
  const md = flags.has('--md');
  return {
    silent: flags.has('--silent'),
    noNotify: flags.has('--no-notify') || process.env.DM_NO_NOTIFY === '1',
    json: flags.has('--json'),
    outPath,
    inPath,
    alertMinRespRate: isNaN(minResp) ? 0 : minResp, // percent
    alertMaxErrorRate: isNaN(maxErr) ? 100 : maxErr, // percent
    fromDate: fromDate && !isNaN(fromDate) ? fromDate : undefined,
    toDate: toDate && !isNaN(toDate) ? toDate : undefined,
    md
  };
}

module.exports = { ensureDir, fileExists, parseCliFlags };


