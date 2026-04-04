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

**Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.**

## Features

- 🎙️ **6 High-Quality Voices** - American and British English
- ⚡ **Fast Generation** - Optimized for Apple Silicon M1/M2
- 🔒 **Privacy First** - All processing runs locally
- 🌐 **URL to Audio** - Convert articles to audio with one click
- 💾 **Smart Caching** - Faster processing for repeated URLs
- 🎚️ **Speed Control** - Adjust playback speed (0.5x - 2.0x)

## Quick Start

1. **Enter text** in the textarea or **paste a URL**
2. **Select a voice** from the dropdown
3. **Adjust speed** if desired
4. Click **"Generate & Play"** or **"Processar URL"**

## Available Voices

| Voice | Name | Accent |
|-------|------|--------|
| af_heart | Heart | American (Female) |
| af_sarah | Sarah | American (Female) |
| am_adam | Adam | American (Male) |
| am_michael | Michael | American (Male) |
| bf_emma | Emma | British (Female) |
| bf_isabella | Isabella | British (Female) |

## API Usage

This Space exposes a REST API for programmatic access:

### Generate Speech from Text

```bash
curl -X POST "https://YOUR-SPACE.hf.space/tts" \
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
curl -X POST "https://YOUR-SPACE.hf.space/api/url" \
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
curl "https://YOUR-SPACE.hf.space/voices"
```

## Technology Stack

- **TTS Engine**: [Kokoro](https://github.com/hexgrad/kokoro) (82M parameters)
- **Backend**: FastAPI + Uvicorn
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Web Scraping**: BeautifulSoup + Readability
- **Language Detection**: langdetect

## Limitations

- **Cold Start**: First request may take 30-60 seconds (model download)
- **Text Limit**: Maximum 5000 characters per request
- **Rate Limits**: HuggingFace Spaces have usage limits
- **Memory**: ~400MB RAM usage during generation

## Running Locally

```bash
# Clone the repository
git clone https://huggingface.co/spaces/YOUR-USERNAME/my_reader
cd my_reader

# Install dependencies
pip install -r requirements.txt

# Run the server
python app.py

# Open in browser
open http://localhost:8000
```

## Repository

Source code: [GitHub - isaaceliape/my_reader](https://github.com/isaaceliape/my_reader)

## License

MIT License - See [LICENSE](https://github.com/isaaceliape/my_reader/blob/main/LICENSE) for details.

## Acknowledgments

- Kokoro TTS by [hexgrad](https://github.com/hexgrad/kokoro)
- Hosted on [HuggingFace Spaces](https://huggingface.co/spaces)

---

**Made with ❤️ by Isaac Eliape**
