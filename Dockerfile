FROM python:3.11-slim

# ✅ Variables de entorno para optimización
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    # ✅ NUEVO: Variables específicas para Docling
    DOCLING_CACHE_DIR=/root/.cache/docling \
    OPENCV_OPENCL_DEVICE=disabled \
    OMP_NUM_THREADS=2

WORKDIR /app

# ✅ NUEVO: Instalar dependencias del sistema COMPLETAS para Docling
RUN apt-get update && apt-get install -y \
    # Básicas
    curl \
    wget \
    # ✅ Dependencias CRÍTICAS para Docling
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libfontconfig1 \
    # ✅ Procesamiento de documentos
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    # ✅ Librerías de imagen
    libjpeg-dev \
    libpng-dev \
    libtiff-dev \
    libwebp-dev \
    # ✅ Computer Vision
    libopencv-dev \
    # ✅ Cleanup
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ✅ Copiar requirements primero para mejor caching
COPY requirements.txt .

# ✅ Instalar dependencias Python con timeout extendido
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir --timeout=600 -r requirements.txt

# Copiar código
COPY . .

# ✅ Crear directorios necesarios
RUN mkdir -p /root/.cache/docling /app/data /app/logs

EXPOSE 8000

# ✅ Comando optimizado con más memoria y workers para Docling
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "120", "--limit-max-requests", "50"]