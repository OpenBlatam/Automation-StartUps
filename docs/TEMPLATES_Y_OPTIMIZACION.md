# Templates y Optimización - TikTok Auto Edit

## 🎨 Sistema de Templates

### Concepto

Los templates permiten aplicar estilos predefinidos de edición a los videos, sin necesidad de generar un script desde cero cada vez.

### Templates Predefinidos

#### 1. Cinematic
Look cinematográfico con transiciones suaves y color grading.

**Características:**
- Fade in/out suaves
- Color grading cinematográfico
- Ideal para contenido profesional

#### 2. Energetic
Edición rápida y dinámica.

**Características:**
- Ken Burns effect (zoom + pan)
- Velocidad ligeramente aumentada (1.1x)
- Ideal para contenido dinámico

#### 3. Dramatic
Efectos dramáticos con slow motion.

**Características:**
- Fade in/out largos (2s)
- Zoom constante
- Slow motion (0.8x)
- Ideal para momentos impactantes

#### 4. Minimal
Edición mínima y limpia.

**Características:**
- Solo fade in/out básicos
- Sin efectos adicionales
- Ideal para contenido simple

### Uso de Templates

#### Inicializar Templates Predefinidos

```bash
python3 tiktok_templates.py init
```

#### Listar Templates Disponibles

```bash
python3 tiktok_templates.py list
```

#### Crear Template Personalizado

```bash
# Crear desde archivo JSON
python3 tiktok_templates.py create \
  -n "mi_template" \
  -d "Descripción del template" \
  -f script.json
```

#### Usar Template en Código

```python
from tiktok_templates import TemplateManager
from video_editor import VideoEditor

# Cargar template
manager = TemplateManager()
template = manager.get_template('cinematic')

# Aplicar a video
editor = VideoEditor()
video_duration = 15.0  # segundos
script = template.apply_to_video(video_duration)

# Editar video
result = editor.edit_video_from_dict('video.mp4', script)
```

### Formato de Template

```json
{
  "name": "mi_template",
  "description": "Descripción del template",
  "script": {
    "editing_script": {
      "transitions": [
        {
          "start_time": 0,
          "end_time": 1,
          "type": "fade_in"
        }
      ],
      "effects": [
        {
          "type": "ken_burns",
          "start_time": 0,
          "end_time": -1,
          "zoom": 1.3,
          "pan_direction": "center"
        }
      ],
      "speed_changes": []
    }
  }
}
```

**Nota**: Usa `-1` para `end_time` para indicar "hasta el final del video".

## ⚡ Optimización de Rendimiento

### Analizar Sistema

```bash
python3 tiktok_optimizer.py analyze
```

**Salida:**
```json
{
  "system": {
    "cpu_cores": 8,
    "memory_gb": 16.0,
    "disk_space_gb": 500.0,
    "cpu_usage": 25.5,
    "memory_usage": 45.2
  },
  "recommendations": {
    "queue_workers": 6,
    "video_threads": 8,
    "batch_size": 10,
    "cache_enabled": true,
    "auto_compress": false,
    "quality": "high"
  },
  "warnings": []
}
```

### Generar Configuración Optimizada

```bash
python3 tiktok_optimizer.py config -o config.json
```

**Configuración generada:**
```json
{
  "queue": {
    "max_workers": 6,
    "retry_delay": 5,
    "max_retries": 3
  },
  "video_editing": {
    "threads": 8,
    "preset": "medium",
    "quality": "high"
  },
  "batch_processing": {
    "batch_size": 10,
    "parallel_downloads": 3
  },
  "cache": {
    "enabled": true,
    "max_size_gb": 10
  },
  "compression": {
    "auto_compress": false,
    "target_size_mb": 50,
    "quality": "high"
  }
}
```

### Optimizar Cache

```bash
python3 tiktok_optimizer.py optimize-cache \
  -d ~/.tiktok_cache \
  -s 10
```

Elimina archivos antiguos del cache para mantenerlo bajo un tamaño máximo.

## 🔧 Aplicar Configuración

### En Queue Manager

```python
from tiktok_optimizer import PerformanceOptimizer
from tiktok_queue_manager import TikTokQueueManager

optimizer = PerformanceOptimizer()
config = optimizer.generate_config()

manager = TikTokQueueManager(max_workers=config['queue']['max_workers'])
```

### En Video Editor

```python
from video_editor import VideoEditor
import json

with open('config.json', 'r') as f:
    config = json.load(f)

# Usar configuración en edición
# (requiere modificar video_editor.py para leer config)
```

## 📊 Recomendaciones por Hardware

### Sistema Básico (4GB RAM, 2 cores)
- Workers: 1
- Threads: 2
- Batch size: 3
- Cache: Deshabilitado
- Calidad: Medium

### Sistema Medio (8GB RAM, 4 cores)
- Workers: 3
- Threads: 4
- Batch size: 5
- Cache: Habilitado (5GB)
- Calidad: High

### Sistema Avanzado (16GB+ RAM, 8+ cores)
- Workers: 6
- Threads: 8
- Batch size: 10
- Cache: Habilitado (10GB+)
- Calidad: High

## 🎯 Mejores Prácticas

### 1. Usar Templates
- Ahorra tiempo de procesamiento
- Consistencia en estilo
- Fácil personalización

### 2. Optimizar Cache
- Limpia cache regularmente
- Monitorea tamaño
- Usa cache para videos repetidos

### 3. Ajustar Workers
- No excedas CPU cores - 1
- Monitorea uso de memoria
- Ajusta según carga

### 4. Calidad vs Velocidad
- High quality: Más tiempo, mejor resultado
- Medium quality: Balance
- Low quality: Más rápido, menor calidad

## 🔍 Monitoreo de Rendimiento

### Métricas Clave

1. **Tiempo de procesamiento**: Debe ser consistente
2. **Uso de CPU**: No debe estar al 100% constantemente
3. **Uso de memoria**: Monitorea para evitar OOM
4. **Tamaño de cache**: Mantén bajo control
5. **Tasa de éxito**: Debe ser > 90%

### Script de Monitoreo

```bash
#!/bin/bash
# monitor.sh

while true; do
    echo "=== $(date) ==="
    python3 tiktok_optimizer.py analyze | jq '.system'
    sleep 60
done
```

## 🚀 Optimizaciones Avanzadas

### 1. Procesamiento en GPU
Para sistemas con GPU NVIDIA:
- Usa `ffmpeg` con aceleración GPU
- Configura `-hwaccel cuda` en exportación

### 2. SSD vs HDD
- SSD: Mucho más rápido para I/O
- HDD: Más económico pero más lento
- Recomendado: SSD para cache y temporales

### 3. Red
- Descargas paralelas: Aprovecha ancho de banda
- Cache local: Reduce descargas repetidas
- CDN: Para servir videos procesados

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01


