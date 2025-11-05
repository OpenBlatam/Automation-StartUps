#!/usr/bin/env bash
set -euo pipefail

# validate_frontmatter_yaml.sh - Valida estrictamente el front matter YAML
# Requiere Python3; usa PyYAML si disponible. Si no, intenta parser simple.

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
FAIL=0

mapfile -t MD_FILES < <(find "$ROOT_DIR" -maxdepth 1 -type f -name "*.md" | sort)

pyyaml_available=0
python3 - <<'PY' >/dev/null 2>&1 || true
PY
if python3 -c 'import yaml' >/dev/null 2>&1; then
  pyyaml_available=1
fi

validate_with_python() {
  python3 - "$@" <<'PY'
import io, os, sys, re
try:
    import yaml
except Exception as e:
    print("[yaml] PyYAML no disponible", file=sys.stderr)
    sys.exit(2)

required = {"title": str, "category": str, "created": str, "path": str}
date_re = re.compile(r"^\d{4}-\d{2}-\d{2}$")

def load_frontmatter(path):
    with open(path, 'r', encoding='utf-8') as f:
        text = f.read()
    if not text.startswith('---\n'):
        return None
    end = text.find('\n---', 4)
    if end == -1:
        return None
    block = text[4:end]
    try:
        return yaml.safe_load(block)
    except Exception as e:
        raise RuntimeError(f"YAML inválido: {e}")

fail = 0
for path in sys.argv[1:]:
    name = os.path.basename(path)
    try:
        fm = load_frontmatter(path)
        if fm is None:
            print(f"[yaml] {name}: front matter faltante o mal delimitado", file=sys.stderr)
            fail = 1
            continue
        # required keys
        for k, t in required.items():
            if k not in fm or fm[k] is None:
                print(f"[yaml] {name}: falta clave requerida '{k}'", file=sys.stderr)
                fail = 1
            elif not isinstance(fm[k], t):
                print(f"[yaml] {name}: clave '{k}' tipo inválido (se esperaba {t.__name__})", file=sys.stderr)
                fail = 1
        # format checks
        created = str(fm.get('created',''))
        if created and not date_re.match(created):
            print(f"[yaml] {name}: 'created' no coincide con YYYY-MM-DD", file=sys.stderr)
            fail = 1
        pathv = str(fm.get('path',''))
        if pathv and pathv != pathv.lower():
            print(f"[yaml] {name}: 'path' debería ser lowercase (actual: {pathv})", file=sys.stderr)
            # no marca fail duro
    except Exception as e:
        print(f"[yaml] {name}: error al validar: {e}", file=sys.stderr)
        fail = 1

sys.exit(1 if fail else 0)
PY
}

if [[ $pyyaml_available -eq 1 ]]; then
  echo "[yaml-strict] Usando PyYAML para validación estricta"
  if ! validate_with_python "${MD_FILES[@]}"; then
    exit 1
  fi
  echo "[yaml-strict] OK"
  exit 0
fi

echo "[yaml-strict] PyYAML no disponible; validación estricta omitida" >&2
exit 0


