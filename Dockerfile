# syntax=docker/dockerfile:1

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements if exist
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt || true

# Install optional libs used if present
RUN pip install --no-cache-dir prometheus-client openpyxl requests redis PyJWT || true

# Copy source
COPY . /app

# Env defaults
ENV FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=5000

EXPOSE 5000

CMD ["python", "app.py"]