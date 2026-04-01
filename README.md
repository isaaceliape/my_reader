# my_reader - Local TTS Web App

Text-to-Speech web app that runs 100% locally on your MacBook Air M1 using Kokoro TTS.

## Features

- Type or paste any text and hear it spoken aloud
- 6 high-quality neural voices (3 American, 2 British)
- Adjustable playback speed (0.5x to 2.0x)
- Download generated audio as WAV files
- Runs completely offline - no internet required
- Privacy-first - nothing leaves your computer

## Quick Start

### 1. Create virtual environment

```bash
cd /Users/isaaceliape/repos/my_reader
python3 -m venv venv
source venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python app.py
```

### 4. Open in browser

Navigate to: http://127.0.0.1:8000

## Tech Stack

- **Backend:** FastAPI (Python)
- **TTS Engine:** Kokoro (82M parameter neural TTS)
- **Frontend:** Vanilla HTML/CSS/JavaScript
- **Hardware:** Optimized for Apple Silicon M1 (MPS acceleration)

## Requirements

- macOS with Apple Silicon (M1/M2/M3)
- Python 3.10+
- 4GB+ RAM available

## Project Status

**Phase:** MVP/Prototype
**Status:** Ready for testing

## Next Steps

- [ ] Test on M1 hardware
- [ ] Validate voice quality
- [ ] Measure performance (RTF, memory usage)
- [ ] Add text preprocessing (numbers, abbreviations)
- [ ] Implement audio caching

## License

MIT
