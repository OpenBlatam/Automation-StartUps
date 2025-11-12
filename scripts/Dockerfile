FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY tiktok_requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r tiktok_requirements.txt

# Copiar scripts
COPY *.py ./

# Crear directorios necesarios
RUN mkdir -p /tmp/tiktok_downloads /tmp/tiktok_edited \
    && mkdir -p ~/.tiktok_cache ~/.tiktok_templates

# Variables de entorno
ENV PYTHONUNBUFFERED=1
ENV TIKTOK_SCRIPTS_DIR=/app
ENV TIKTOK_DOWNLOADS_DIR=/tmp/tiktok_downloads
ENV TIKTOK_EDITED_DIR=/tmp/tiktok_edited

# Exponer puertos
EXPOSE 5000 5001 5002

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python3 -c "import requests; requests.get('http://localhost:5000/health')" || exit 1

# Comando por defecto (API server)
CMD ["python3", "tiktok_api_server.py", "-p", "5000", "-h", "0.0.0.0"]

