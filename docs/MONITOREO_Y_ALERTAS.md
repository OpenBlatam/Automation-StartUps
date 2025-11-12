# Monitoreo y Alertas - TikTok Auto Edit

## 🔍 Monitor Continuo

### Iniciar Monitor

```bash
# Monitor continuo (verifica cada 60s)
python3 monitor_system.py

# Intervalo personalizado
python3 monitor_system.py -i 30

# Una verificación en JSON
python3 monitor_system.py -j
```

### Qué Monitorea

1. **Servicios HTTP**
   - API REST (puerto 5000)
   - Webhooks (puerto 5001)
   - Dashboard (puerto 5002)
   - Health checks
   - Tiempo de respuesta

2. **Queue Manager**
   - Trabajos pendientes
   - Trabajos procesando
   - Trabajos completados/fallidos
   - Alertas si hay muchos pendientes

3. **Sistema**
   - Espacio en disco
   - Uso de CPU/Memoria (opcional)
   - Estado general

### Alertas Automáticas

El monitor alerta automáticamente cuando:
- ✅ Servicio no responde
- ✅ Cola con > 20 trabajos pendientes
- ✅ Espacio en disco < 5 GB
- ✅ Tiempo de respuesta > 5 segundos

## 📊 Integración con Notificaciones

### Configurar Alertas

```python
from tiktok_notifications import NotificationManager
from monitor_system import SystemMonitor

monitor = SystemMonitor()
notifications = NotificationManager()

# En el loop de monitoreo
services = monitor.check_all_services()
for service in services:
    if service['status'] != 'healthy':
        notifications.send_telegram(
            f"⚠️ Servicio {service['name']} no está saludable: {service.get('error')}"
        )
```

## 🔔 Alertas Configurables

### Variables de Entorno

```bash
# URLs de servicios
export TIKTOK_API_URL=http://localhost:5000
export TIKTOK_WEBHOOK_URL=http://localhost:5001
export TIKTOK_DASHBOARD_URL=http://localhost:5002

# Thresholds
export MAX_PENDING_JOBS=20
export MIN_DISK_SPACE_GB=5
export MAX_RESPONSE_TIME=5
```

## 📈 Métricas Monitoreadas

### Servicios
- Estado (healthy/unhealthy/down)
- Tiempo de respuesta
- Disponibilidad
- Errores

### Queue
- Trabajos pendientes
- Trabajos procesando
- Tasa de éxito
- Tiempo promedio

### Sistema
- Espacio en disco
- Uso de recursos
- Estado general

## 🚨 Respuesta a Alertas

### Servicio Caído

1. Verificar logs: `docker-compose logs servicio`
2. Reiniciar: `docker-compose restart servicio`
3. Verificar: `python3 monitor_system.py -j`

### Cola Saturada

1. Aumentar workers: `python3 tiktok_queue_manager.py start -w 5`
2. Verificar procesamiento: `python3 tiktok_analytics.py stats`
3. Limpiar cache si es necesario

### Disco Lleno

1. Limpiar temporales: `python3 maintenance.py clean`
2. Optimizar cache: `python3 tiktok_optimizer.py optimize-cache`
3. Backup y limpieza: `python3 tiktok_backup.py cleanup`

## 🔧 Configuración Avanzada

### Monitor con Notificaciones

```python
from monitor_system import SystemMonitor
from tiktok_notifications import NotificationManager

monitor = SystemMonitor(check_interval=60)
notifications = NotificationManager()

def check_and_alert():
    services = monitor.check_all_services()
    for service in services:
        if service['status'] != 'healthy':
            notifications.send_telegram(
                f"⚠️ {service['name']}: {service.get('error')}"
            )

# Ejecutar cada minuto
while True:
    check_and_alert()
    time.sleep(60)
```

### Integración con Cron

```bash
# Verificar cada 5 minutos
*/5 * * * * /usr/bin/python3 /path/to/monitor_system.py -j >> /var/log/tiktok_monitor.log 2>&1
```

## 📊 Dashboard de Monitoreo

El dashboard web (`tiktok_dashboard.py`) también muestra:
- Estado de servicios
- Métricas de cola
- Estadísticas en tiempo real

Accede en: `http://localhost:5002`

## 🎯 Mejores Prácticas

1. **Monitoreo Continuo**: Ejecuta monitor en producción
2. **Alertas Tempranas**: Configura notificaciones
3. **Logs Centralizados**: Usa sistema de logs
4. **Métricas Históricas**: Guarda métricas para análisis
5. **Respuesta Rápida**: Automatiza respuestas a alertas comunes

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01

