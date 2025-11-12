# TikTok Auto Edit - Guía Completa

## 📚 Índice

1. [Instalación](#instalación)
2. [Uso Básico](#uso-básico)
3. [Uso Avanzado](#uso-avanzado)
4. [Scripts Disponibles](#scripts-disponibles)
5. [Workflow n8n](#workflow-n8n)
6. [Analytics](#analytics)
7. [Solución de Problemas](#solución-de-problemas)

## 🚀 Instalación

### Requisitos Previos

```bash
# Python 3.8+
python3 --version

# FFmpeg
brew install ffmpeg  # macOS
# o
sudo apt-get install ffmpeg  # Linux
```

### Instalar Dependencias

```bash
cd /Users/adan/IA/scripts
pip install -r tiktok_requirements.txt
```

### Configurar Variables de Entorno

```bash
export OPENAI_API_KEY="sk-tu-api-key"
```

## 📖 Uso Básico

### 1. Descargar un Video

```bash
python3 tiktok_downloader.py "https://www.tiktok.com/@user/video/123" -o /tmp/downloads
```

### 2. Generar Script de Edición

```bash
python3 video_script_generator.py video.mp4 -n 10 -o script.json
```

### 3. Editar Video

```bash
python3 video_editor.py video.mp4 script.json -o video_edited.mp4
```

## 🎯 Uso Avanzado

### Procesamiento en Batch

```bash
# Crear archivo con URLs
cat > urls.txt << EOF
https://www.tiktok.com/@user/video/123
https://www.tiktok.com/@user/video/456
https://www.tiktok.com/@user/video/789
EOF

# Procesar en batch
python3 tiktok_batch_processor.py urls.txt -w 3 -o /tmp/batch_output
```

### Comprimir Video

```bash
python3 video_compressor.py video.mp4 -o video_compressed.mp4 -s 50
```

### Analytics

```bash
# Ver estadísticas
python3 tiktok_analytics.py stats -d 7

# Generar reporte
python3 tiktok_analytics.py report -d 30 -o report.json

# Top URLs
python3 tiktok_analytics.py top -l 20
```

## 📝 Scripts Disponibles

### 1. `tiktok_downloader.py`
Descarga videos de TikTok sin marca de agua.

**Opciones:**
- `-o, --output`: Directorio de salida
- `-f, --filename`: Nombre de archivo personalizado
- `-j, --json`: Salida en formato JSON

### 2. `video_script_generator.py`
Genera scripts de edición usando IA.

**Opciones:**
- `-n, --num-frames`: Número de frames a analizar (default: 10)
- `-o, --output`: Archivo JSON de salida

### 3. `video_editor.py`
Edita videos aplicando transiciones y efectos.

**Opciones:**
- `-o, --output`: Nombre del archivo de salida
- `-d, --output-dir`: Directorio de salida
- `-j, --json`: Salida en formato JSON

### 4. `video_compressor.py`
Comprime videos para cumplir límites de tamaño.

**Opciones:**
- `-o, --output`: Archivo de salida
- `-s, --target-size`: Tamaño objetivo en MB (default: 50)
- `-q, --quality`: Calidad (high/medium/low)

### 5. `tiktok_batch_processor.py`
Procesa múltiples videos en paralelo.

**Opciones:**
- `-w, --workers`: Número de workers paralelos (default: 3)
- `-o, --output`: Directorio de salida
- `-j, --json`: Salida en formato JSON

### 6. `tiktok_analytics.py`
Sistema de analytics y reportes.

**Comandos:**
- `stats`: Ver estadísticas
- `report`: Generar reporte
- `top`: Ver top URLs

## 🔄 Workflow n8n

### Importar Workflow

1. Abre n8n
2. Ve a **Workflows** → **Import from File**
3. Selecciona `n8n_workflow_tiktok_auto_edit.json`
4. Configura credenciales:
   - Telegram Bot API
   - WhatsApp API (opcional)

### Configurar Variables

En n8n, configura:
- `OPENAI_API_KEY`: Tu API key de OpenAI
- `WHATSAPP_API_URL`: URL de tu API de WhatsApp (opcional)

### Usar el Workflow

1. Activa el workflow
2. Envía un link de TikTok a Telegram o WhatsApp
3. El bot procesará automáticamente
4. Recibirás el video editado

## 📊 Analytics

### Integración en Scripts

```python
from tiktok_analytics import TikTokAnalytics

analytics = TikTokAnalytics()

# Registrar procesamiento
analytics.record_processing({
    'url': 'https://...',
    'status': 'completed',
    'processing_time': 120.5,
    'file_size': 1024000,
    'duration': 15.3,
    'from_cache': False
})

# Obtener estadísticas
stats = analytics.get_stats(days=7)
print(f"Tasa de éxito: {stats['success_rate']:.2f}%")
```

### Métricas Disponibles

- Total procesado
- Tasa de éxito
- Tiempo promedio
- Uso de cache
- Tamaño total
- Errores comunes

## 🐛 Solución de Problemas

### Error: "yt-dlp no está instalado"
```bash
pip install --upgrade yt-dlp
```

### Error: "FFmpeg no encontrado"
```bash
# Verificar instalación
ffmpeg -version

# Instalar si falta
brew install ffmpeg  # macOS
```

### Error: "OpenAI API Key no configurada"
```bash
export OPENAI_API_KEY="sk-..."
```

### Video muy grande para Telegram
```bash
# Comprimir manualmente
python3 video_compressor.py video.mp4 -s 50
```

### Error de memoria
- Reduce número de workers en batch processing
- Procesa videos más pequeños primero
- Aumenta swap si es necesario

### Cache no funciona
- Verifica permisos en directorio de cache
- Limpia cache: `rm -rf /tmp/tiktok_cache`
- Verifica espacio en disco

## 📈 Mejores Prácticas

1. **Usa cache**: Mantén cache activo para mejor rendimiento
2. **Procesamiento batch**: Para múltiples videos, usa batch processor
3. **Monitorea analytics**: Revisa reportes regularmente
4. **Comprime si es necesario**: Videos grandes pueden fallar
5. **Backup de analytics**: Haz backup de la base de datos

## 🔗 Enlaces Útiles

- [Documentación completa](./N8N_TIKTOK_AUTO_EDIT.md)
- [Mejoras implementadas](./MEJORAS_TIKTOK_AUTO_EDIT.md)
- [Funcionalidades avanzadas](./FUNCIONALIDADES_AVANZADAS.md)

## 📞 Soporte

Para problemas o preguntas:
1. Revisa la documentación
2. Verifica los logs
3. Consulta analytics para patrones
4. Revisa issues conocidos

---

**Versión**: 3.0  
**Última actualización**: 2024-01-01


