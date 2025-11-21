# TikTok Auto Edit - Guía Definitiva

## 🎯 Sistema Completo

Sistema profesional de automatización para procesamiento de videos de TikTok con IA.

## ⚡ Inicio Ultra Rápido

```bash
# 1. Setup automático
./setup_tiktok_system.sh

# 2. Health check
python3 health_check.py

# 3. Iniciar todos los servicios
./quick_start.sh

# 4. Abrir dashboard
open http://localhost:5002
```

## 📋 Comandos Esenciales

### Procesamiento
```bash
# CLI interactivo
python3 tiktok_cli.py

# Procesar un video
python3 tiktok_cli.py process -u "URL_TIKTOK"

# Batch processing
python3 tiktok_batch_processor.py urls.txt -w 3
```

### Monitoreo
```bash
# Dashboard web
python3 tiktok_dashboard.py -p 5002

# Analytics
python3 tiktok_analytics.py stats -d 7

# Health check
python3 health_check.py

# Tests
python3 test_tiktok_system.py
```

### Mantenimiento
```bash
# Backup
python3 tiktok_backup.py create

# Limpieza
python3 maintenance.py full

# Optimización
python3 tiktok_optimizer.py config
```

## 🎬 Workflow n8n

1. Importa `n8n_workflow_tiktok_auto_edit.json` en n8n
2. Configura credenciales de Telegram
3. Activa el workflow
4. Envía un link de TikTok
5. Recibe el video editado automáticamente

## 📊 Servicios Disponibles

| Servicio | Puerto | Comando |
|----------|--------|---------|
| API REST | 5000 | `python3 tiktok_api_server.py -p 5000` |
| Webhooks | 5001 | `python3 tiktok_webhook_handler.py -p 5001` |
| Dashboard | 5002 | `python3 tiktok_dashboard.py -p 5002` |
| Queue Manager | - | `python3 tiktok_queue_manager.py start` |

## 🔧 Configuración Rápida

```bash
# Variables esenciales
export OPENAI_API_KEY="sk-..."

# Opcionales (notificaciones)
export TELEGRAM_BOT_TOKEN="..."
export SLACK_WEBHOOK_URL="..."
```

## 📚 Documentación Completa

- `README_FINAL.md` - Guía completa del sistema
- `docs/N8N_TIKTOK_AUTO_EDIT.md` - Documentación principal
- `docs/RESUMEN_FINAL_SISTEMA.md` - Resumen ejecutivo

## ✅ Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] FFmpeg instalado
- [ ] Dependencias instaladas (`pip install -r tiktok_requirements.txt`)
- [ ] OPENAI_API_KEY configurada
- [ ] Setup ejecutado (`./setup_tiktok_system.sh`)
- [ ] Health check pasa (`python3 health_check.py`)
- [ ] Tests pasan (`python3 test_tiktok_system.py`)

## 🚀 Próximos Pasos

1. Ejecutar setup
2. Configurar variables de entorno
3. Probar con un video
4. Iniciar servicios
5. Configurar n8n workflow

---

**¡Sistema listo para usar!** 🎬✨

