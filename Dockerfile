# HuggingFace Spaces Dockerfile for my_reader TTS
# Uses Docker SDK for full control over the environment

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
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
# This layer will be cached, speeding up rebuilds
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

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
