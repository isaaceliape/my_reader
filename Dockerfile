# HuggingFace Spaces Dockerfile for my_reader TTS
# Optimized for both CPU and GPU acceleration

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
# Enable CPU optimizations
ENV OMP_NUM_THREADS=4
ENV MKL_NUM_THREADS=4
ENV MKL_SERVICE_ENABLE=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libsndfile1 \
    libsndfile1-dev \
    ffmpeg \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch with CPU optimizations first
# CPU version is smaller and faster for CPU-only inference
# GPU version will be installed if GPU is detected at runtime
RUN pip install --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install other dependencies
COPY requirements.txt .
RUN grep -v "^torch" requirements.txt > requirements-no-torch.txt || true
RUN pip install -r requirements-no-torch.txt || pip install -r requirements.txt

# Optional: Install ONNX runtime for CPU optimization (uncomment if needed)
# RUN pip install onnx onnxruntime

# Copy application code
COPY . .

# Create cache directory for Kokoro model
RUN mkdir -p /tmp/.hermes

# Expose port (HuggingFace will handle this)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/api', timeout=5)" || exit 1

# Run the application
# HuggingFace Spaces expects the app to listen on 0.0.0.0:7860
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
