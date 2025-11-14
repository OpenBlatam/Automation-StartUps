---
title: "Schedule Weekly Examples"
category: "schedule_weekly_examples.md"
tags: []
created: "2025-10-29"
path: "schedule_weekly_examples.md"
---

# Programación semanal de verificación automática

Este archivo contiene ejemplos para programar la verificación semanal.

## Opción A: launchd (macOS)

1) Guarda este plist en `~/Library/LaunchAgents/com.blatam.verify.plist`:

```
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.blatam.verify</string>
  <key>ProgramArguments</key>
  <array>
    <string>/usr/bin/python3</string>
    <string>/Users/adan/Documents/documentos_blatam/verify_organization.py</string>
    <string>--dry-run</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Weekday</key>
    <integer>1</integer>
    <key>Hour</key>
    <integer>9</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>StandardOutPath</key>
  <string>/Users/adan/Documents/documentos_blatam/verify_weekly.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/adan/Documents/documentos_blatam/verify_weekly.err</string>
  <key>RunAtLoad</key>
  <true/>
</dict>
</plist>
```

2) Carga el job:

```bash
launchctl load ~/Library/LaunchAgents/com.blatam.verify.plist
launchctl start com.blatam.verify
```

## Opción B: cron

Edita el crontab:

```bash
crontab -e
```

Añade (lunes 09:00):

```
0 9 * * 1 /usr/bin/python3 /Users/adan/Documents/documentos_blatam/verify_organization.py --dry-run >> /Users/adan/Documents/documentos_blatam/verify_weekly.log 2>&1
```

Notas:
- El reporte HTML se genera en `organization_report.html`.
- Ajusta día/hora según prefieras.
- Puedes quitar `--dry-run` para aplicar movimientos con `apply_suggestions.py` después de revisar.



