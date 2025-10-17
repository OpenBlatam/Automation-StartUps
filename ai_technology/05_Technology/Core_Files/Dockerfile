# Multi-stage Dockerfile for Frontier AI Projects
# Optimized for production deployment

# Stage 1: Base image with Python and system dependencies
FROM python:3.10-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Stage 2: Development dependencies
FROM base as development

# Install development dependencies
RUN pip install --upgrade pip && \
    pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    transformers \
    accelerate \
    datasets \
    tokenizers \
    numpy \
    pandas \
    scikit-learn \
    matplotlib \
    seaborn \
    plotly \
    tqdm \
    pyyaml \
    requests \
    beautifulsoup4 \
    pillow \
    psutil \
    fastapi \
    uvicorn \
    streamlit \
    pytest \
    black \
    flake8

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install project packages
RUN pip install -e ./TruthGPT/brandkit
RUN pip install -e ./TruthGPT/Frontier-Model-run

# Expose ports
EXPOSE 8000 8501

# Default command for development
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000"]

# Stage 3: Production image
FROM base as production

# Create non-root user
RUN groupadd -r frontier && useradd -r -g frontier frontier

# Install production dependencies
RUN pip install --upgrade pip && \
    pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu \
    transformers \
    accelerate \
    datasets \
    tokenizers \
    numpy \
    pandas \
    scikit-learn \
    matplotlib \
    seaborn \
    plotly \
    tqdm \
    pyyaml \
    requests \
    beautifulsoup4 \
    pillow \
    psutil \
    fastapi \
    uvicorn \
    streamlit

# Set working directory
WORKDIR /app

# Copy project files
COPY --chown=frontier:frontier . .

# Install project packages
RUN pip install -e ./TruthGPT/brandkit
RUN pip install -e ./TruthGPT/Frontier-Model-run

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/output /app/checkpoints && \
    chown -R frontier:frontier /app

# Switch to non-root user
USER frontier

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]

# Stage 4: GPU-enabled production image
FROM nvidia/cuda:11.8-devel-ubuntu20.04 as production-gpu

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3.10-dev \
    python3-pip \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Create symlink for python
RUN ln -s /usr/bin/python3.10 /usr/bin/python

# Create non-root user
RUN groupadd -r frontier && useradd -r -g frontier frontier

# Install production dependencies with GPU support
RUN pip install --upgrade pip && \
    pip install \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118 \
    transformers \
    accelerate \
    datasets \
    tokenizers \
    numpy \
    pandas \
    scikit-learn \
    matplotlib \
    seaborn \
    plotly \
    tqdm \
    pyyaml \
    requests \
    beautifulsoup4 \
    pillow \
    psutil \
    fastapi \
    uvicorn \
    streamlit

# Set working directory
WORKDIR /app

# Copy project files
COPY --chown=frontier:frontier . .

# Install project packages
RUN pip install -e ./TruthGPT/brandkit
RUN pip install -e ./TruthGPT/Frontier-Model-run

# Create necessary directories
RUN mkdir -p /app/logs /app/cache /app/output /app/checkpoints && \
    chown -R frontier:frontier /app

# Switch to non-root user
USER frontier

# Expose ports
EXPOSE 8000 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command for production with GPU
CMD ["python", "api_server.py", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]










