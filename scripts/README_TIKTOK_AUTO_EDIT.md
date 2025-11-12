# TikTok Auto Edit - Guía Rápida

## 🚀 Inicio Rápido

### 1. Instalar Dependencias

```bash
pip install -r tiktok_requirements.txt
```

### 2. Instalar FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt-get install ffmpeg
```

### 3. Configurar OpenAI API Key

```bash
export OPENAI_API_KEY="sk-tu-api-key-aqui"
```

### 4. Probar Scripts Individualmente

#### Descargar un video de TikTok:
```bash
python3 tiktok_downloader.py "https://www.tiktok.com/@user/video/123" -o /tmp/downloads
```

#### Generar script de edición:
```bash
python3 video_script_generator.py /tmp/downloads/video.mp4 -n 10 -o script.json
```

#### Editar video:
```bash
python3 video_editor.py /tmp/downloads/video.mp4 script.json -o video_edited.mp4
```

## 📋 Uso en n8n

1. Importa el workflow `n8n_workflow_tiktok_auto_edit.json` en n8n
2. Configura las credenciales de Telegram
3. Ajusta las rutas de los scripts si es necesario
4. Activa el workflow
5. Envía un link de TikTok al bot

## 🔧 Solución de Problemas

- **Error de yt-dlp**: `pip install --upgrade yt-dlp`
- **Error de FFmpeg**: Verifica que esté instalado con `ffmpeg -version`
- **Error de OpenAI**: Verifica que `OPENAI_API_KEY` esté configurada
- **Error de permisos**: `chmod +x *.py`

## 📚 Documentación Completa

Ver `/docs/N8N_TIKTOK_AUTO_EDIT.md` para documentación detallada.



