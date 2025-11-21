# Funcionalidades Avanzadas - TikTok Auto Edit

## 🚀 Nuevas Funcionalidades

### 1. Procesamiento en Batch
**Archivo**: `scripts/tiktok_batch_processor.py`

Procesa múltiples videos de TikTok simultáneamente.

**Características:**
- ✅ Procesamiento paralelo con ThreadPoolExecutor
- ✅ Configurable número de workers
- ✅ Reporte detallado de resultados
- ✅ Manejo robusto de errores
- ✅ Resumen estadístico completo

**Uso:**
```bash
# Crear archivo con URLs (una por línea)
echo "https://www.tiktok.com/@user/video/123" > urls.txt
echo "https://www.tiktok.com/@user/video/456" >> urls.txt

# Procesar en batch
python3 tiktok_batch_processor.py urls.txt -w 3 -o /tmp/batch_output
```

**O con JSON:**
```json
{
  "urls": [
    "https://www.tiktok.com/@user/video/123",
    "https://www.tiktok.com/@user/video/456"
  ]
}
```

**Salida:**
- Videos editados en directorio de salida
- Scripts de edición generados
- Resumen JSON con estadísticas

### 2. Sistema de Analytics
**Archivo**: `scripts/tiktok_analytics.py`

Sistema completo de tracking y analytics.

**Características:**
- ✅ Base de datos SQLite para persistencia
- ✅ Tracking de cada procesamiento
- ✅ Estadísticas diarias automáticas
- ✅ Métricas de rendimiento
- ✅ Reportes exportables

**Métricas registradas:**
- URL del video
- Estado (completado/error)
- Tiempo de procesamiento
- Tamaño del archivo
- Uso de cache
- Errores y mensajes

**Comandos:**
```bash
# Ver estadísticas de últimos 7 días
python3 tiktok_analytics.py stats -d 7

# Generar reporte completo
python3 tiktok_analytics.py report -d 30 -o report.json

# Ver top URLs más procesadas
python3 tiktok_analytics.py top -l 20
```

**Integración en scripts:**
```python
from tiktok_analytics import TikTokAnalytics

analytics = TikTokAnalytics()
analytics.record_processing({
    'url': 'https://...',
    'status': 'completed',
    'processing_time': 120.5,
    'file_size': 1024000,
    'from_cache': False
})
```

### 3. Efectos Avanzados
**Archivo**: `scripts/video_effects_advanced.py`

Efectos profesionales adicionales.

**Efectos disponibles:**

#### Ken Burns
Zoom suave con movimiento de cámara (pan).
```python
from video_effects_advanced import apply_ken_burns

clip = apply_ken_burns(clip, zoom=1.3, pan_direction='right')
```

#### Color Grading Cinematográfico
Corrección de color profesional.
```python
from video_effects_advanced import apply_cinematic_look

clip = apply_cinematic_look(clip)
```

#### Zoom con Pan
Control preciso de zoom y movimiento.
```python
from video_effects_advanced import AdvancedVideoEffects

effects = AdvancedVideoEffects()
clip = effects.zoom_pan_effect(
    clip,
    start_zoom=1.0,
    end_zoom=1.5,
    pan_x=0.3,  # Mover a la derecha
    pan_y=-0.2  # Mover hacia arriba
)
```

#### Color Grading Avanzado
Ajustes precisos de color.
```python
clip = effects.color_grade(
    clip,
    brightness=0.95,
    contrast=1.1,
    saturation=0.9,
    temperature=10  # Cálido
)
```

**Uso en scripts de edición:**
Los efectos avanzados se aplican automáticamente si están especificados en el script de IA:
```json
{
  "effects": [
    {
      "type": "ken_burns",
      "start_time": 0,
      "end_time": 5,
      "zoom": 1.3,
      "pan_direction": "right"
    },
    {
      "type": "cinematic",
      "start_time": 0,
      "end_time": 10
    }
  ]
}
```

## 📊 Dashboard de Métricas

### Estadísticas Disponibles

1. **Procesamiento General**
   - Total de videos procesados
   - Tasa de éxito
   - Tiempo promedio de procesamiento
   - Tamaño total procesado

2. **Cache**
   - Hits de cache
   - Tasa de cache hit
   - Ahorro de tiempo

3. **Errores**
   - Tasa de error
   - Tipos de error más comunes
   - URLs problemáticas

4. **Tendencias**
   - Procesamientos por día
   - Patrones de uso
   - Horarios pico

### Ejemplo de Reporte

```json
{
  "generated_at": "2024-01-01T12:00:00",
  "period_days": 7,
  "summary": {
    "total_processed": 150,
    "successful": 142,
    "failed": 8,
    "success_rate": 94.67,
    "avg_processing_time": 125.3,
    "total_size_mb": 7500,
    "cache_hits": 45,
    "cache_hit_rate": 30.0
  },
  "daily_breakdown": [
    {
      "date": "2024-01-01",
      "total": 25,
      "successful": 24,
      "failed": 1,
      "avg_time": 120.5
    }
  ],
  "top_urls": [
    {
      "url": "https://www.tiktok.com/@user/video/123",
      "count": 15,
      "successful": 15
    }
  ]
}
```

## 🔧 Integración con n8n

### Agregar Analytics al Workflow

Agrega un nodo Code después de cada procesamiento:

```javascript
// En n8n, después de editar video
const analytics = require('/Users/adan/IA/scripts/tiktok_analytics.py');

const analyticsData = {
  url: $json.tiktokUrl,
  status: $json.editResult.success ? 'completed' : 'error',
  started_at: $json.startedAt,
  completed_at: new Date().toISOString(),
  processing_time: (Date.now() - new Date($json.startedAt)) / 1000,
  file_size: $json.editedVideoSize,
  duration: $json.editedVideoDuration,
  from_cache: $json.fromCache || false,
  error_message: $json.error || null
};

// Ejecutar script de analytics
// (usar Execute Command node)
```

## 📈 Optimizaciones de Rendimiento

### Procesamiento Paralelo

El procesador en batch usa ThreadPoolExecutor para procesar múltiples videos simultáneamente:

- **3 workers por defecto**: Balance entre velocidad y recursos
- **Configurable**: Ajusta según tu hardware
- **Thread-safe**: Manejo seguro de recursos compartidos

### Cache Inteligente

- **Persistencia**: Cache se mantiene entre ejecuciones
- **Validación**: Verifica integridad de archivos
- **Limpieza**: Elimina entradas inválidas automáticamente

## 🎯 Casos de Uso

### 1. Procesamiento Masivo
```bash
# Procesar 100 videos de una lista
python3 tiktok_batch_processor.py large_list.txt -w 5
```

### 2. Monitoreo de Calidad
```bash
# Generar reporte semanal
python3 tiktok_analytics.py report -d 7 -o weekly_report.json
```

### 3. Identificar Problemas
```bash
# Ver URLs más problemáticas
python3 tiktok_analytics.py top -l 50
```

### 4. Efectos Personalizados
```python
# Aplicar efectos específicos en script personalizado
from video_effects_advanced import apply_ken_burns

# En tu script de edición personalizado
clip = apply_ken_burns(clip, zoom=1.5, pan_direction='left')
```

## 🔒 Mejores Prácticas

1. **Analytics**: Registra todos los procesamientos para análisis
2. **Batch Processing**: Usa para grandes volúmenes
3. **Cache**: Mantén cache activo para mejor rendimiento
4. **Monitoreo**: Revisa reportes regularmente
5. **Efectos**: Usa efectos avanzados con moderación

## 📝 Notas Técnicas

### Base de Datos Analytics
- **Ubicación**: `~/.tiktok_analytics.db`
- **Formato**: SQLite
- **Backup**: Recomendado hacer backup regular

### Procesamiento en Batch
- **Memoria**: Cada worker carga un video completo
- **CPU**: Usa múltiples cores si están disponibles
- **I/O**: Considera usar SSD para mejor rendimiento

### Efectos Avanzados
- **Rendimiento**: Algunos efectos son computacionalmente costosos
- **Calidad**: Efectos avanzados mejoran calidad visual significativamente
- **Compatibilidad**: Requieren moviepy y numpy

---

**Versión**: 3.0  
**Fecha**: 2024-01-01


