FROM python:3.11-slim

# ✅ AÑADIDO: Variables de entorno para optimización
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# ✅ MODIFICADO: Instalar dependencias del sistema más eficientemente
RUN apt-get update && apt-get install -y \
    curl \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# ✅ AÑADIDO: Copiar requirements primero para mejor caching
COPY requirements.txt .

# ✅ MODIFICADO: Instalar dependencias Python optimizadas
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código (igual que antes)
COPY . .

EXPOSE 8000

# ✅ MODIFICADO: Comando optimizado para producción
CMD ["uvicorn", "backend.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "--timeout-keep-alive", "65"]