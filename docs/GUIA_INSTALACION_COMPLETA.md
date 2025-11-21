# Guía de Instalación Completa - TikTok Auto Edit

## 🚀 Instalación Rápida

### Opción 1: Script Automático (Recomendado)

```bash
cd /Users/adan/IA/scripts
chmod +x setup_tiktok_system.sh
./setup_tiktok_system.sh
```

Este script:
- ✅ Verifica Python y FFmpeg
- ✅ Instala todas las dependencias
- ✅ Crea directorios necesarios
- ✅ Inicializa templates
- ✅ Genera configuración optimizada

### Opción 2: Instalación Manual

#### Paso 1: Verificar Requisitos

```bash
# Python 3.8+
python3 --version

# FFmpeg
ffmpeg -version
```

#### Paso 2: Instalar Dependencias

```bash
cd /Users/adan/IA/scripts
pip3 install -r tiktok_requirements.txt
```

#### Paso 3: Configurar Variables de Entorno

```bash
# Esencial
export OPENAI_API_KEY="sk-tu-api-key-aqui"

# Opcionales (notificaciones)
export TELEGRAM_BOT_TOKEN="tu-bot-token"
export TELEGRAM_CHAT_ID="tu-chat-id"
export SLACK_WEBHOOK_URL="https://hooks.slack.com/services/..."
export EMAIL_SMTP_SERVER="smtp.gmail.com"
export EMAIL_SMTP_PORT="587"
export EMAIL_USER="tu-email@gmail.com"
export EMAIL_PASSWORD="tu-password"
export EMAIL_TO="destinatario@email.com"
```

#### Paso 4: Inicializar Sistema

```bash
# Crear directorios
mkdir -p ~/.tiktok_cache ~/.tiktok_templates

# Inicializar templates
python3 tiktok_templates.py init

# Optimizar configuración
python3 tiktok_optimizer.py config -o ~/.tiktok_config.json
```

## ✅ Verificación

### Health Check

```bash
python3 health_check.py
```

Esto verifica:
- ✅ Python y versión
- ✅ FFmpeg instalado
- ✅ Todas las dependencias
- ✅ OpenAI API Key
- ✅ Directorios
- ✅ Scripts principales
- ✅ Espacio en disco

### Prueba Rápida

```bash
# Descargar un video de prueba
python3 tiktok_downloader.py "https://www.tiktok.com/@user/video/123" -o /tmp/test
```

## 🔧 Configuración Avanzada

### Configurar n8n

1. Importa el workflow:
   ```
   n8n_workflow_tiktok_auto_edit.json
   ```

2. Configura credenciales:
   - Telegram Bot API
   - WhatsApp API (opcional)

3. Ajusta rutas si es necesario:
   - Scripts: `/Users/adan/IA/scripts/`
   - Directorios temporales: `/tmp/tiktok_*`

### Configurar Servicios

#### API REST

```bash
# Iniciar servidor API
python3 tiktok_api_server.py -p 5000

# Verificar
curl http://localhost:5000/health
```

#### Webhooks

```bash
# Configurar secret
export WEBHOOK_SECRET="tu-secret-seguro"

# Iniciar handler
python3 tiktok_webhook_handler.py -p 5001
```

#### Dashboard

```bash
# Iniciar dashboard
python3 tiktok_dashboard.py -p 5002

# Abrir en navegador
open http://localhost:5002
```

#### Queue Manager

```bash
# Iniciar con configuración optimizada
python3 tiktok_queue_manager.py start -w 3
```

## 📊 Monitoreo

### Ver Estadísticas

```bash
# Analytics
python3 tiktok_analytics.py stats -d 7

# Cola
python3 tiktok_queue_manager.py stats

# Sistema
python3 tiktok_optimizer.py analyze
```

### Logs

Los logs se escriben en stdout. Para producción:

```bash
# API
python3 tiktok_api_server.py -p 5000 >> api.log 2>&1

# Queue Manager
python3 tiktok_queue_manager.py start >> queue.log 2>&1
```

## 🐛 Solución de Problemas

### Error: "Module not found"

```bash
# Reinstalar dependencias
pip3 install -r tiktok_requirements.txt --upgrade
```

### Error: "FFmpeg not found"

```bash
# macOS
brew install ffmpeg

# Linux
sudo apt-get update
sudo apt-get install ffmpeg

# Verificar
ffmpeg -version
```

### Error: "OpenAI API Key invalid"

```bash
# Verificar formato
echo $OPENAI_API_KEY
# Debe empezar con "sk-"

# Configurar correctamente
export OPENAI_API_KEY="sk-tu-key-aqui"
```

### Error: "Permission denied"

```bash
# Dar permisos de ejecución
chmod +x scripts/*.py scripts/*.sh
```

### Error: "Disk space low"

```bash
# Limpiar cache
python3 tiktok_optimizer.py optimize-cache -s 5

# Limpiar temporales
rm -rf /tmp/tiktok_*
```

## 🔄 Actualización

### Actualizar Dependencias

```bash
cd /Users/adan/IA/scripts
pip3 install -r tiktok_requirements.txt --upgrade
```

### Actualizar Templates

```bash
python3 tiktok_templates.py init
```

### Regenerar Configuración

```bash
python3 tiktok_optimizer.py config -o ~/.tiktok_config.json
```

## 📚 Recursos Adicionales

- [README Final](../scripts/README_FINAL.md)
- [Documentación Principal](./N8N_TIKTOK_AUTO_EDIT.md)
- [API y Webhooks](./API_Y_WEBHOOKS.md)
- [Dashboard y Notificaciones](./DASHBOARD_Y_NOTIFICACIONES.md)
- [Templates y Optimización](./TEMPLATES_Y_OPTIMIZACION.md)

## 🎯 Checklist de Instalación

- [ ] Python 3.8+ instalado
- [ ] FFmpeg instalado
- [ ] Dependencias Python instaladas
- [ ] OPENAI_API_KEY configurada
- [ ] Directorios creados
- [ ] Templates inicializados
- [ ] Configuración optimizada generada
- [ ] Health check pasa sin errores
- [ ] Prueba de descarga funciona
- [ ] n8n workflow importado (opcional)
- [ ] Servicios iniciados (opcional)

## 🚀 Inicio Rápido Post-Instalación

```bash
# 1. Health check
python3 health_check.py

# 2. Probar descarga
python3 tiktok_downloader.py "URL_TIKTOK" -o /tmp/test

# 3. Iniciar servicios (opcional)
python3 tiktok_api_server.py -p 5000 &
python3 tiktok_dashboard.py -p 5002 &
python3 tiktok_queue_manager.py start -w 3 &
```

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01


