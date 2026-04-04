# HuggingFace Spaces Dockerfile for my_reader TTS
# Optimized for GPU acceleration on HuggingFace Spaces

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

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

# Install PyTorch with CUDA support first
# HuggingFace Spaces GPU instances have NVIDIA GPUs with CUDA support
RUN pip install --upgrade pip && \
    pip install torch --index-url https://download.pytorch.org/whl/cu118

# Copy requirements (excluding torch if listed) and install other dependencies
COPY requirements.txt .
RUN grep -v "^torch" requirements.txt > requirements-no-torch.txt || true
RUN pip install -r requirements-no-torch.txt || pip install -r requirements.txt

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
