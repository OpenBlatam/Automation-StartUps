# 🛠️ Herramientas de Mantenimiento y Automatización

## 📋 Scripts Disponibles

### 1. `scripts/setup_completo.sh`
**Descripción**: Script de configuración completa del sistema

**Funcionalidades**:
- ✅ Verifica dependencias del sistema
- ✅ Verifica Python y dependencias
- ✅ Crea estructura de directorios
- ✅ Genera archivo .env de ejemplo
- ✅ Verifica workflows y nodos
- ✅ Configura permisos

**Uso**:
```bash
cd /Users/adan/IA/n8n
chmod +x scripts/setup_completo.sh
./scripts/setup_completo.sh
```

**Salida esperada**:
- Verificación de todas las dependencias
- Creación de directorios necesarios
- Archivo .env.example generado
- Resumen de estado del sistema

### 2. `scripts/backup_workflow_data.sh`
**Descripción**: Script de backup automático de datos del workflow

**Funcionalidades**:
- ✅ Respaldar workflows JSON
- ✅ Respaldar nodos adicionales
- ✅ Respaldar configuración (.env)
- ✅ Respaldar datos del workflow
- ✅ Respaldar logs
- ✅ Comprimir backup
- ✅ Limpiar backups antiguos (mantiene últimos 10)

**Uso**:
```bash
cd /Users/adan/IA/n8n
chmod +x scripts/backup_workflow_data.sh
./scripts/backup_workflow_data.sh
```

**Configuración**:
```bash
# Cambiar directorio de backup (opcional)
export BACKUP_DIR="$HOME/my_backups"
./scripts/backup_workflow_data.sh
```

**Restaurar backup**:
```bash
# Desde archivo tar.gz
tar -xzf sora_workflow_backup_YYYYMMDD_HHMMSS.tar.gz -C /ruta/destino

# Desde archivo zip
unzip sora_workflow_backup_YYYYMMDD_HHMMSS.zip -d /ruta/destino
```

### 3. `scripts/monitor_sistema.sh`
**Descripción**: Script de monitoreo del sistema

**Funcionalidades**:
- ✅ Verifica estado de n8n
- ✅ Monitorea uso de recursos
- ✅ Verifica espacio en disco
- ✅ Revisa logs recientes
- ✅ Verifica workflows activos
- ✅ Verifica APIs externas
- ✅ Verifica dependencias críticas
- ✅ Calcula score de salud del sistema

**Uso**:
```bash
cd /Users/adan/IA/n8n
chmod +x scripts/monitor_sistema.sh
./scripts/monitor_sistema.sh
```

**Salida**:
- Estado completo del sistema
- Score de salud (0-100%)
- Recomendaciones

## 🔄 Automatización con Cron

### Backup Automático Diario

```bash
# Agregar a crontab
crontab -e

# Backup diario a las 2 AM
0 2 * * * /Users/adan/IA/n8n/scripts/backup_workflow_data.sh >> /Users/adan/IA/logs/backup.log 2>&1
```

### Monitoreo Cada Hora

```bash
# Monitoreo cada hora
0 * * * * /Users/adan/IA/n8n/scripts/monitor_sistema.sh >> /Users/adan/IA/logs/monitor.log 2>&1
```

### Limpieza Semanal

```bash
# Limpieza de archivos temporales cada domingo
0 3 * * 0 find /Users/adan/IA/data/temp -type f -mtime +7 -delete
```

## 📊 Monitoreo Avanzado

### Verificar Estado del Workflow

```bash
# Verificar si el workflow está activo
curl -s http://localhost:5678/api/v1/workflows | jq '.[] | select(.name | contains("Sora")) | {name: .name, active: .active}'
```

### Ver Logs en Tiempo Real

```bash
# Seguir logs de n8n
tail -f /Users/adan/IA/logs/n8n.log

# Filtrar solo errores
tail -f /Users/adan/IA/logs/n8n.log | grep -i error
```

### Verificar Métricas de Engagement

```bash
# Contar videos procesados
find /Users/adan/IA/data/videos -type f | wc -l

# Ver último análisis Python
ls -lt /tmp/python_analysis_output.json
```

## 🔧 Mantenimiento Preventivo

### Tareas Semanales

1. **Verificar espacio en disco**
   ```bash
   df -h /Users/adan/IA
   ```

2. **Limpiar archivos temporales**
   ```bash
   find /Users/adan/IA/data/temp -type f -mtime +7 -delete
   ```

3. **Verificar backups**
   ```bash
   ls -lh ~/sora_workflow_backups/
   ```

4. **Revisar logs de errores**
   ```bash
   grep -i error /Users/adan/IA/logs/*.log | tail -20
   ```

### Tareas Mensuales

1. **Actualizar dependencias**
   ```bash
   pip3 install --upgrade pandas numpy matplotlib seaborn scikit-learn openai
   npm update -g n8n
   ```

2. **Revisar y optimizar workflows**
   - Revisar workflows inactivos
   - Optimizar nodos que consumen muchos recursos
   - Actualizar credenciales si es necesario

3. **Análisis de performance**
   ```bash
   # Ejecutar análisis Python completo
   python3 /Users/adan/IA/scripts/analisis_engagement_contenido.py \
     /tmp/engagement_export.json \
     --format html \
     --output /tmp/reporte_mensual.html
   ```

## 🚨 Alertas y Notificaciones

### Configurar Alertas por Email

```bash
# Script de alerta por email
cat > /Users/adan/IA/n8n/scripts/send_alert.sh << 'EOF'
#!/bin/bash
SUBJECT="$1"
BODY="$2"
EMAIL="tu@email.com"

echo "$BODY" | mail -s "$SUBJECT" "$EMAIL"
EOF

chmod +x /Users/adan/IA/n8n/scripts/send_alert.sh
```

### Alertas de Sistema

```bash
# Agregar a crontab para alertas
# Si el sistema está abajo, enviar alerta
*/5 * * * * pgrep -x n8n || /Users/adan/IA/n8n/scripts/send_alert.sh "n8n Down" "n8n no está corriendo"
```

## 📈 Optimización de Performance

### Limpiar Cache de n8n

```bash
# Limpiar cache de n8n
rm -rf ~/.n8n/cache/*
```

### Optimizar Base de Datos (si usa SQLite)

```bash
# Si n8n usa SQLite
sqlite3 ~/.n8n/database.sqlite "VACUUM;"
```

### Limpiar Logs Antiguos

```bash
# Mantener solo últimos 30 días de logs
find /Users/adan/IA/logs -name "*.log" -mtime +30 -delete
```

## 🔐 Seguridad

### Verificar Permisos de Archivos

```bash
# Verificar permisos de archivos sensibles
ls -la /Users/adan/IA/n8n/.env
chmod 600 /Users/adan/IA/n8n/.env
```

### Rotar API Keys

```bash
# Script para rotar API keys
cat > /Users/adan/IA/n8n/scripts/rotate_keys.sh << 'EOF'
#!/bin/bash
# Backup de keys actuales
cp .env .env.backup.$(date +%Y%m%d)

# Generar nuevas keys (requiere configuración manual)
echo "Actualiza las API keys en .env manualmente"
EOF
```

## 📊 Reportes Automáticos

### Generar Reporte Semanal

```bash
# Script para reporte semanal
cat > /Users/adan/IA/n8n/scripts/generate_weekly_report.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
REPORT_DIR="/Users/adan/IA/data/reports"

# Exportar datos
python3 /Users/adan/IA/n8n/scripts/export_data.py

# Generar reporte Python
python3 /Users/adan/IA/scripts/analisis_engagement_contenido.py \
  /tmp/engagement_export.json \
  --format html \
  --output "$REPORT_DIR/reporte_semanal_$DATE.html"

# Enviar reporte (opcional)
# mail -s "Reporte Semanal Sora Workflow" tu@email.com < "$REPORT_DIR/reporte_semanal_$DATE.html"
EOF

chmod +x /Users/adan/IA/n8n/scripts/generate_weekly_report.sh
```

## 🎯 Checklist de Mantenimiento

### Diario
- [ ] Verificar que n8n está corriendo
- [ ] Revisar logs de errores
- [ ] Verificar espacio en disco

### Semanal
- [ ] Ejecutar backup
- [ ] Limpiar archivos temporales
- [ ] Revisar métricas de engagement
- [ ] Verificar workflows activos

### Mensual
- [ ] Actualizar dependencias
- [ ] Revisar y optimizar workflows
- [ ] Generar reporte completo
- [ ] Revisar y rotar credenciales si es necesario
- [ ] Análisis de performance completo

### Trimestral
- [ ] Auditoría completa del sistema
- [ ] Revisar y actualizar documentación
- [ ] Optimización profunda de workflows
- [ ] Análisis de costos y ROI

---

**Estado**: ✅ Scripts listos para usar  
**Mantenimiento**: Automatizado donde es posible  
**Documentación**: Completa



