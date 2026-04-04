---
title: my_reader - Local TTS Web App
emoji: 🔊
colorFrom: purple
colorTo: blue
sdk: docker
pinned: false
license: mit
---

# 🔊 my_reader - Local TTS Web App

> **Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.**

[![HuggingFace Spaces](https://img.shields.io/badge/🤗-HuggingFace%20Spaces-blue)](https://huggingface.co/spaces/isaaceliape/my-reader-tts)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Tests](https://img.shields.io/badge/tests-129%20passed-green)](https://github.com/isaaceliape/my_reader)

## 🌟 Features

- 🎙️ **6 High-Quality Voices** - American and British English (Kokoro TTS)
- ⚡ **Fast Generation** - Optimized for Apple Silicon M1/M2 (50x real-time)
- 🔒 **Privacy First** - All processing runs locally, no cloud APIs
- 🌐 **URL to Audio** - Convert articles to audio with one click
- 💾 **Smart Caching** - Faster processing for repeated URLs
- 🎚️ **Speed Control** - Adjust playback speed (0.5x - 2.0x)
- 📱 **Responsive UI** - Works on desktop and mobile
- ⌨️ **Keyboard Shortcuts** - Cmd+Enter to generate, Space to pause

## 🚀 Live Demo

**Try it now on HuggingFace Spaces:**

👉 https://huggingface.co/spaces/isaaceliape/my-reader-tts

*Note: First request may take 30-60 seconds (cold start + model download)*

## 📖 Quick Start

### Option 1: Use the Live Demo

1. Visit the [HuggingFace Space](https://huggingface.co/spaces/isaaceliape/my-reader-tts)
2. Enter text or paste a URL
3. Select a voice
4. Click "Generate & Play"

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/isaaceliape/my_reader.git
cd my_reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Open in browser
open http://localhost:8000
```

## 🎭 Available Voices

| Voice ID | Name | Accent | Gender |
|----------|------|--------|--------|
| `af_heart` | Heart | American | Female |
| `af_sarah` | Sarah | American | Female |
| `am_adam` | Adam | American | Male |
| `am_michael` | Michael | American | Male |
| `bf_emma` | Emma | British | Female |
| `bf_isabella` | Isabella | British | Female |

## 🔌 API Usage

The app exposes a REST API for programmatic access:

### Generate Speech from Text

```bash
curl -X POST "http://localhost:8000/tts" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello, this is a test.",
    "voice": "af_heart",
    "speed": 1.0
  }' \
  --output speech.wav
```

### Convert URL to Audio

```bash
curl -X POST "http://localhost:8000/api/url" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/article",
    "voice": "af_heart",
    "speed": 1.0
  }' \
  --output article.wav
```

### List Available Voices

```bash
curl "http://localhost:8000/voices"
```

### Response Headers (URL endpoint)

| Header | Description |
|--------|-------------|
| `X-Article-Title` | Extracted article title |
| `X-Article-URL` | Final URL (after redirects) |
| `X-Article-Language` | Detected language (e.g., "en", "pt") |
| `X-Cache` | `HIT` if cached, `MISS` if freshly processed |

## 🏗️ Technology Stack

| Component | Technology |
|-----------|------------|
| **TTS Engine** | [Kokoro](https://github.com/hexgrad/kokoro) (82M parameters) |
| **Backend** | FastAPI + Uvicorn |
| **Frontend** | Vanilla HTML/CSS/JavaScript |
| **Web Scraping** | BeautifulSoup + Readability-lxml |
| **Language Detection** | langdetect |
| **Audio Processing** | SoundFile + NumPy |
| **Caching** | cachetools (TTL-based) |

## 📊 Performance

| Metric | Value | Notes |
|--------|-------|-------|
| **Model Size** | ~200MB | Kokoro v1.0 |
| **Memory Usage** | 145MB idle, 215MB peak | On M1 Mac |
| **Startup Time** | ~8 seconds | With model load |
| **RTF (Real-time Factor)** | 50x+ | On M1 with MPS |
| **Audio Quality** | 24kHz, 16-bit mono | WAV format |

*RTF = Audio duration / Generation time (higher is better)*

## 🧪 Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
python -m pytest tests/ -v

# Run with coverage
python -m pytest tests/ --cov=app --cov=src
```

**Test Coverage:** 129 tests covering:
- TTS endpoint (/tts)
- URL endpoint (/api/url)
- Voices endpoint (/voices)
- Web crawler module
- Cache functionality
- App lifecycle

## 📁 Project Structure

```
my_reader/
├── api/                    # Vercel serverless functions
│   └── index.py           # Entry point for Vercel
├── src/
│   └── crawler/           # Web scraping module
│       ├── client.py      # HTTP client (httpx)
│       ├── parser.py      # HTML parsing
│       ├── extractor.py   # Article extraction
│       ├── cache.py       # Caching layer
│       ├── integrator.py  # URL-to-audio pipeline
│       └── models.py      # Data models
├── static/
│   └── index.html         # Frontend UI
├── tests/
│   ├── test_app_lifecycle.py
│   ├── test_crawler.py
│   ├── test_crawler_client.py
│   ├── test_integrator.py
│   ├── test_tts_endpoint.py
│   ├── test_url_endpoint.py
│   └── test_voices_endpoint.py
├── .planning/             # Project documentation
├── app.py                 # FastAPI backend
├── Dockerfile             # HuggingFace Spaces config
├── requirements.txt       # Python dependencies
├── vercel.json            # Vercel configuration
└── pytest.ini             # Test configuration
```

## ⚠️ Limitations

| Limitation | Value | Reason |
|------------|-------|--------|
| **Cold Start** | 30-60 seconds | Model download from HuggingFace |
| **Text Limit** | 5000 characters | API constraint |
| **Memory** | ~400MB peak | Kokoro + PyTorch |
| **Rate Limits** | HF Spaces limits | Free tier restrictions |

## 🚀 Deployment

### HuggingFace Spaces (Recommended)

```bash
# Login to HuggingFace
hf auth login

# Deploy
./deploy-hf.sh
```

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed instructions.

### Vercel

⚠️ **Not recommended** - 60s build timeout causes failures with ML dependencies.

Configuration files (`vercel.json`, `api/index.py`) are included but deployment may require Vercel Enterprise for longer timeouts.

### Local Docker

```bash
docker build -t my_reader .
docker run -p 7860:7860 my_reader
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/isaaceliape/my_reader/blob/main/LICENSE) file for details.

## 🙏 Acknowledgments

- **[Kokoro TTS](https://github.com/hexgrad/kokoro)** by hexgrad - The amazing open-source TTS engine
- **[HuggingFace](https://huggingface.co/)** - Free hosting for ML demos
- **[FastAPI](https://fastapi.tiangolo.com/)** - Modern Python web framework

## 📬 Contact

- **GitHub:** [@isaaceliape](https://github.com/isaaceliape)
- **HuggingFace:** [isaaceliape](https://huggingface.co/isaaceliape)
- **Project Link:** https://huggingface.co/spaces/isaaceliape/my-reader-tts

---

**Made with ❤️ by Isaac Eliape** | [GitHub](https://github.com/isaaceliape/my_reader) | [HuggingFace](https://huggingface.co/spaces/isaaceliape/my-reader-tts)
