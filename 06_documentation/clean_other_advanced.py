#!/usr/bin/env python3
import os, shutil
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [
  '01_Marketing/Other',
  '04_Business_Strategy/Other',
  '05_Technology/Other',
  '06_Documentation/Other',
  '08_AI_Artificial_Intelligence/Other',
]
PATTERNS = {
  'CTAs/': ['ctas_', 'cta'],
  'Blog_Posts/': ['blog_', 'post_'],
  'Templates/': ['template', 'plantilla', 'version_'],
  'Guides/': ['guia', 'guide', 'manual'],
  'Social_Media/': ['linkedin', 'instagram', 'social', 'tweet', 'youtube', 'viral'],
  'Email/': ['email', 'sequence', 'secuencia', 'nurture'],
  'Checklists/': ['checklist'],
  'SEO/': ['seo', 'keyword', 'meta'],
  'Lead_Generation/': ['lead', 'outreach', 'captura', 'follow_up'],
  'Automation/': ['automation', 'automatizacion', 'script_'],
  'DMs/': ['dm_', 'dms_'],
  'Data/': ['.csv', '.json', '.xlsx'],
  'Presentations/': ['.pptx', '.ppt', '.docx'],
  'Strategies/': ['estrategia', 'strategy', 'roadmap'],
  'Analytics/': ['analytics', 'dashboard', 'metric'],
  'Campaigns/': ['campaign', 'calendario'],
}

moved = defaultdict(int)

def ensure(d: Path):
  d.mkdir(parents=True, exist_ok=True)
  return d

def match_sub(folder: Path, name: str):
  low = name.lower()
  for sub, pats in PATTERNS.items():
    for p in pats:
      if p.startswith('.'):
        if low.endswith(p):
          return sub
      else:
        if p in low:
          return sub
  return None

def process(target: Path):
  files = [f for f in target.iterdir() if f.is_file() and not f.name.startswith('.')]
  for f in files:
    sub = match_sub(target, f.name)
    if not sub:
      continue
    dest_dir = ensure(target / sub)
    dest = dest_dir / f.name
    i = 1
    while dest.exists():
      dest = dest_dir / f"{f.stem}_{i}{f.suffix}"
      i += 1
    try:
      shutil.move(str(f), str(dest))
      moved[str(target / sub)] += 1
    except Exception:
      pass

if __name__ == '__main__':
  report = []
  for t in TARGETS:
    tp = ROOT / t
    if tp.exists():
      process(tp)
  print('Movidos por subcarpeta:')
  for k,v in sorted(moved.items()):
    print(f"  {k}: {v}")
