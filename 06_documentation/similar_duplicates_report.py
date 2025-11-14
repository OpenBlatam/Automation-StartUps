#!/usr/bin/env python3
import os, csv, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / '06_Documentation' / 'duplicate_similar_report.csv'
EXCLUDE_DIRS = {'.git','node_modules','__pycache__','backups','assets'}
EXTS = {'.md','.txt','.pdf','.pptx','.xlsx','.html','.json','.csv'}

def normalize_name(name: str) -> str:
    # remove extension, digits, and collapse spaces/punct
    name = name.rsplit('.', 1)[0]
    name = name.lower()
    name = re.sub(r'\d+', ' ', name)
    name = re.sub(r'[^a-zñáéíóúü\s]', ' ', name)
    name = re.sub(r'\s+', ' ', name).strip()
    return name

def tokens(name: str):
    return set([t for t in name.split(' ') if t and len(t) > 2])

def jaccard(a:set, b:set) -> float:
    if not a and not b: return 1.0
    if not a or not b: return 0.0
    return len(a & b) / len(a | b)

files = []
for root, dirs, fnames in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS and not d.startswith('.')]
    for fn in fnames:
        if fn.startswith('.'): continue
        p = Path(root) / fn
        if p.suffix.lower() not in EXTS: continue
        try:
            size = p.stat().st_size
        except Exception:
            continue
        rel = str(p.relative_to(ROOT))
        base = normalize_name(fn)
        files.append((rel, fn, base, tokens(base), size))

# Compare within buckets by first letter of base to limit O(n^2)
from collections import defaultdict
buckets = defaultdict(list)
for rel, fn, base, toks, size in files:
    key = base[:1] if base else ''
    buckets[key].append((rel, fn, base, toks, size))

rows = []
SIM_THRESHOLD = 0.7
SIZE_TOL = 0.05  # 5%

for key, items in buckets.items():
    n = len(items)
    for i in range(n):
        rel1, fn1, base1, toks1, size1 = items[i]
        for j in range(i+1, n):
            rel2, fn2, base2, toks2, size2 = items[j]
            # size within tolerance (avoid zero-div)
            if size1 == 0 and size2 == 0:
                size_ok = True
            else:
                big = max(size1, size2)
                small = min(size1, size2)
                size_ok = (big - small) / (big or 1) <= SIZE_TOL
            if not size_ok:
                continue
            sim = jaccard(toks1, toks2)
            if sim >= SIM_THRESHOLD:
                rows.append([f"{sim:.2f}", size1, size2, fn1, rel1, fn2, rel2])

rows.sort(key=lambda r: (-float(r[0]), -max(int(r[1]), int(r[2]))))
REPORT.parent.mkdir(parents=True, exist_ok=True)
with REPORT.open('w', newline='', encoding='utf-8') as f:
    w = csv.writer(f)
    w.writerow(['similarity','size1','size2','name1','path1','name2','path2'])
    w.writerows(rows)

print(f"Similar pairs: {len(rows)} | Report: {REPORT}")
