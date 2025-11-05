#!/usr/bin/env python3
import re, sys, os, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_ROOT = {
  '.babelrc.js','.dockerignore','.editorconfig','.eslintrc.js','.gitattributes','.gitignore','.nvmrc',
  '.prettierrc','.prettierrc.js','Dockerfile','Makefile','README.md','LICENSE','CHANGELOG.md',
  'ATTRIBUTIONS.md','CONTRIBUTING.md','PROJECT_STRUCTURE.md','package.json','tsconfig.json','jest.config.js',
  'swagger.json','vercel.json','sitemap.xml','robots.txt','requirements.txt','env.example','nginx.conf','docker-compose.yml'
}
NAME_OK = re.compile(r'^[A-Za-z0-9_.\-/]+$')
ASSETS_DIR = 'assets'
BINARY_EXT = {'.pdf','.pptx','.xlsx','.png','.jpg','.jpeg','.gif','.webp'}

# get staged files
res = subprocess.run(['git','diff','--cached','--name-only','--diff-filter=ACM'], capture_output=True, text=True)
files = [f for f in res.stdout.splitlines() if f]

errors = []
for f in files:
    p = Path(f)
    # rule 1: no disallowed root files
    if len(p.parts) == 1 and p.name not in ALLOWED_ROOT:
        errors.append(f"Archivo no permitido en raíz: {f}")
    # rule 2: name charset
    if not NAME_OK.match(f):
        errors.append(f"Nombre inválido (solo letras/números/._-/): {f}")
    # rule 3: binaries must live under assets/
    if p.suffix.lower() in BINARY_EXT and (len(p.parts)==1 or p.parts[0] != ASSETS_DIR):
        errors.append(f"Binario fuera de assets/: {f}")

if errors:
    sys.stderr.write("Pre-commit: Se encontraron problemas:\n\n"+"\n".join(f"- {e}" for e in errors)+"\n")
    sys.exit(1)

print('pre-commit OK')
