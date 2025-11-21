# Troubleshooting Avanzado - TikTok Auto Edit

## 🔍 Diagnóstico de Problemas

### Problema: Video no se descarga

**Síntomas:**
- Error "Error al descargar el video"
- Timeout en descarga

**Soluciones:**
1. Verificar URL: `python3 security_config.py validate-url -u "URL"`
2. Verificar conexión a internet
3. Actualizar yt-dlp: `pip install --upgrade yt-dlp`
4. Verificar que el video no esté privado
5. Probar con otra URL de TikTok

### Problema: Error en análisis con IA

**Síntomas:**
- "OpenAI API Key no configurada"
- Error 401/403 de OpenAI

**Soluciones:**
1. Verificar API key: `echo $OPENAI_API_KEY`
2. Verificar formato: debe empezar con "sk-"
3. Verificar créditos en OpenAI dashboard
4. Verificar rate limits de OpenAI
5. Probar con modelo diferente (gpt-4o-mini)

### Problema: Video muy grande para Telegram

**Síntomas:**
- Error al enviar video
- Video > 50MB

**Soluciones:**
1. Compresión automática ya está activa
2. Comprimir manualmente: `python3 video_compressor.py video.mp4 -s 50`
3. Reducir calidad en configuración
4. Dividir video en partes

### Problema: Queue Manager no procesa

**Síntomas:**
- Trabajos quedan en "pending"
- Workers no procesan

**Soluciones:**
1. Verificar workers: `python3 tiktok_queue_manager.py stats`
2. Reiniciar queue manager
3. Verificar logs: `tail -f /tmp/tiktok_queue.log`
4. Verificar espacio en disco
5. Verificar permisos de archivos

### Problema: API no responde

**Síntomas:**
- Timeout en requests
- Error de conexión

**Soluciones:**
1. Verificar que API esté corriendo: `curl http://localhost:5000/health`
2. Verificar logs: `tail -f /tmp/tiktok_api.log`
3. Verificar puerto no esté ocupado: `lsof -i :5000`
4. Reiniciar servicio
5. Verificar firewall

### Problema: Cache no funciona

**Síntomas:**
- Videos se descargan cada vez
- No se usa cache

**Soluciones:**
1. Verificar directorio de cache: `ls -la ~/.tiktok_cache`
2. Verificar permisos: `chmod -R 755 ~/.tiktok_cache`
3. Verificar espacio en disco
4. Limpiar cache corrupto: `rm -rf ~/.tiktok_cache/*`
5. Verificar configuración de cache

## 🛠️ Comandos de Diagnóstico

### Health Check Completo

```bash
# Verificación completa
python3 health_check.py -v

# Tests del sistema
python3 test_tiktok_system.py
```

### Verificar Servicios

```bash
# API
curl http://localhost:5000/health

# Webhooks
curl http://localhost:5001/webhook/health

# Dashboard
curl http://localhost:5002/api/dashboard/stats
```

### Ver Logs

```bash
# API
tail -f /tmp/tiktok_api.log

# Queue
tail -f /tmp/tiktok_queue.log

# Dashboard
tail -f /tmp/tiktok_dashboard.log
```

### Verificar Procesos

```bash
# Ver procesos Python
ps aux | grep python3 | grep tiktok

# Ver puertos
lsof -i :5000
lsof -i :5001
lsof -i :5002
```

## 🔧 Soluciones Comunes

### Reiniciar Todo

```bash
# Detener servicios
./stop_services.sh

# Limpiar temporales
python3 maintenance.py clean

# Reiniciar
./quick_start.sh
```

### Resetear Sistema

```bash
# Backup primero
python3 tiktok_backup.py create

# Limpiar todo
rm -rf ~/.tiktok_cache/*
rm -rf /tmp/tiktok_*

# Reinicializar
python3 tiktok_templates.py init
python3 tiktok_optimizer.py config
```

### Verificar Dependencias

```bash
# Verificar instalación
pip3 list | grep -E "(yt-dlp|moviepy|opencv|openai)"

# Reinstalar si es necesario
pip3 install -r tiktok_requirements.txt --upgrade
```

## 📊 Análisis de Rendimiento

### Ver Estadísticas

```bash
# Analytics
python3 tiktok_analytics.py stats -d 7

# Queue
python3 tiktok_queue_manager.py stats

# Sistema
python3 tiktok_optimizer.py analyze
```

### Identificar Cuellos de Botella

1. Ver tiempos de procesamiento en analytics
2. Verificar uso de CPU/Memoria
3. Verificar I/O de disco
4. Verificar red (descargas)

## 🚨 Problemas Críticos

### Sistema No Inicia

1. Verificar Python: `python3 --version`
2. Verificar FFmpeg: `ffmpeg -version`
3. Verificar dependencias: `pip3 list`
4. Ver logs de error
5. Ejecutar health check

### Pérdida de Datos

1. Verificar backups: `python3 tiktok_backup.py list`
2. Restaurar backup: `python3 tiktok_backup.py restore -f backup.tar.gz`
3. Verificar bases de datos: `ls -la ~/.tiktok_*.db`

### Alto Uso de Recursos

1. Reducir workers: `python3 tiktok_queue_manager.py start -w 2`
2. Limpiar cache: `python3 tiktok_optimizer.py optimize-cache`
3. Limpiar temporales: `python3 maintenance.py clean`
4. Optimizar configuración: `python3 tiktok_optimizer.py config`

## 📞 Soporte

### Información para Reportar Problemas

1. Output de `python3 health_check.py -v`
2. Output de `python3 test_tiktok_system.py`
3. Logs relevantes
4. Versión de Python: `python3 --version`
5. Sistema operativo: `uname -a`

### Logs Útiles

```bash
# Todos los logs
tail -f /tmp/tiktok_*.log

# Logs de errores
grep -i error /tmp/tiktok_*.log

# Logs recientes
find /tmp -name "tiktok_*.log" -mtime -1
```

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01

