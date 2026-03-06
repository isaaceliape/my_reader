# Architecture Research: Local TTS Web App

**Domain:** Local text-to-speech web application
**Researched:** 2025-03-06
**Confidence:** HIGH (based on official sources and verified patterns)

## Recommended Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Frontend (Browser)                           │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                 │
│  │ Text Input  │  │ Voice Select│  │ Audio Player│                 │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                 │
│         │                │                │                        │
├─────────┴────────────────┴────────────────┴─────────────────────────┤
│                         HTTP API (FastAPI/Flask)                     │
├─────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    TTS Service Layer                          │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                   │  │
│  │  │  Model   │  │  Text    │  │  Audio   │                   │  │
│  │  │  Loader  │  │ Processor│  │ Generator│                   │  │
│  │  └──────────┘  └──────────┘  └──────────┘                   │  │
│  └──────────────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                         ONNX Runtime (kokoro-onnx)                   │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │  Model Files │  │ Voice Configs│                                │
│  │ (~300MB)     │  │ (~10MB)      │                                │
│  └──────────────┘  └──────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **Frontend** | Text input UI, voice selection, audio playback | Vanilla HTML/JS or lightweight framework |
| **Web Server** | HTTP API endpoints, request handling, audio streaming | FastAPI (preferred) or Flask |
| **TTS Service** | Model initialization, text processing, audio generation | Python class wrapping kokoro-onnx |
| **Audio Cache** | Store recent generations to avoid reprocessing | In-memory dict or SQLite for persistence |
| **Model Files** | ONNX model weights and voice embeddings | Downloaded at setup, loaded at startup |

## Recommended Project Structure

```
local_tts/
├── src/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes.py          # HTTP endpoints (/tts, /voices, /health)
│   │   └── middleware.py      # CORS, error handling
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── engine.py          # Kokoro TTS wrapper class
│   │   ├── config.py          # Model paths, voice configs
│   │   └── cache.py           # Audio generation cache
│   ├── models/
│   │   └── .gitkeep           # Model files (gitignored, downloaded at setup)
│   └── main.py                # Application entry point
├── static/
│   ├── index.html             # Main UI
│   ├── css/
│   │   └── style.css          # Styling
│   └── js/
│       └── app.js             # Frontend logic
├── tests/
├── requirements.txt           # Python dependencies
└── README.md
```

### Structure Rationale

- **`api/`:** Separation of concerns - HTTP layer isolated from TTS logic
- **`tts/`:** Encapsulates all TTS engine interaction, making it swappable
- **`static/`:** Simple file serving for the frontend; can be replaced later
- **`models/`:** Centralized location for large binary files, kept out of version control

## Data Flow

### Request Flow (Text → Audio)

```
User submits text
       ↓
Frontend POST /api/tts
       ↓
API Validation (text length, voice ID)
       ↓
TTS Service checks cache
       ↓
[Cache Hit] → Return cached audio
       ↓
[Cache Miss] → Text preprocessing
       ↓
Kokoro Pipeline (phonemization → inference)
       ↓
Audio generation (24kHz WAV)
       ↓
Store in cache → Stream response
       ↓
Frontend receives audio → Auto-play
```

### Key Data Flows

1. **TTS Generation Flow:**
   - Text validated and chunked if necessary (for long content)
   - Pipeline converts text → phonemes → mel-spectrogram → audio
   - Generated audio returned as binary response or file URL

2. **Model Loading Flow:**
   - Models loaded once at startup (singleton pattern)
   - Voice embeddings loaded on-demand or at init
   - ONNX Runtime optimizes for M1 Metal GPU if available

3. **Error Handling Flow:**
   - Invalid text → 400 Bad Request
   - Model not loaded → 503 Service Unavailable
   - Generation timeout → 408 Request Timeout

## Suggested Build Order

Based on component dependencies:

1. **Phase 1: Model Setup** (blocking dependency for all else)
   - Download Kokoro model files
   - Verify ONNX runtime works on M1
   - Create model loader utility

2. **Phase 2: TTS Engine** (depends on Phase 1)
   - Implement wrapper class for kokoro-onnx
   - Add text preprocessing (chunking for long texts)
   - Basic audio generation testing

3. **Phase 3: Web API** (depends on Phase 2)
   - FastAPI app setup
   - `/tts` endpoint with streaming response
   - `/voices` endpoint for voice listing
   - Error handling middleware

4. **Phase 4: Frontend** (depends on Phase 3)
   - Static HTML/CSS/JS
   - Text input with character counter
   - Voice selector dropdown
   - Audio player integration

5. **Phase 5: Optimization** (depends on Phase 4)
   - Add audio caching
   - Implement chunked generation for long texts
   - Memory usage optimization

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Single user | Current architecture sufficient - models stay loaded in memory |
| Multiple concurrent requests | Add request queue; ONNX model not thread-safe, needs locking |
| Long text processing | Implement streaming - generate audio in chunks, stream as ready |
| Memory constraints (~8GB) | Load only 1-2 voices at a time; use quantized model (~80MB) |

### Scaling Priorities for M1 Hardware

1. **First bottleneck:** Memory usage from model + voices (~300-500MB typical)
   - Mitigation: Use quantized model, load voices on-demand

2. **Second bottleneck:** Inference latency on long texts
   - Mitigation: Text chunking, progress streaming, caching

## Anti-Patterns

### Anti-Pattern 1: Loading Model Per Request

**What people do:** Initialize TTS model inside the HTTP request handler
**Why it's wrong:** Adds 5-15s latency per request, wastes memory
**Do this instead:** Load model once at startup, reuse across requests

### Anti-Pattern 2: Synchronous Long-Text Generation

**What people do:** Process entire text in one blocking call
**Why it's wrong:** Causes HTTP timeouts, poor UX for long content
**Do this instead:** Chunk text by sentences/paragraphs, generate incrementally

### Anti-Pattern 3: Storing Audio in Memory

**What people do:** Keep all generated audio files in RAM
**Why it's wrong:** Unbounded memory growth, crashes on long sessions
**Do this instead:** Stream audio directly to client; cache metadata + file paths only

### Anti-Pattern 4: No Voice Preloading

**What people do:** Load voice embeddings on every TTS call
**Why it's wrong:** Adds 100-500ms per generation
**Do this instead:** Preload 2-3 voices at startup; lazy-load others

## M1-Specific Considerations

| Concern | Approach |
|---------|----------|
| **ONNX Runtime** | Install `onnxruntime-silicon` for M1 optimization |
| **Memory** | Monitor unified memory usage; model + app ~1GB typical |
| **Thermal throttling** | Batch process long texts; add delays between chunks |
| **First inference** | Warm up model at startup with dummy inference |

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Frontend ↔ API | HTTP/JSON, binary audio | Keep API stateless for simplicity |
| API ↔ TTS Service | Python method calls | TTS Service is singleton |
| TTS Service ↔ Model | ONNX Runtime API | Thread-safe access required |

## Sources

- [kokoro-onnx GitHub](https://github.com/thewh1teagle/kokoro-onnx) - Official implementation
- [Kokoro-82M HuggingFace](https://huggingface.co/hexgrad/Kokoro-82M) - Model documentation
- [MeloTTS GitHub](https://github.com/myshell-ai/MeloTTS) - Alternative engine
- [ONNX Runtime Docs](https://onnxruntime.ai/docs/) - Deployment optimization
- FastAPI/Flask documentation for web layer patterns

---

**Key Recommendations for Roadmap:**
1. Build TTS engine first (foundation)
2. API layer next (integration point)
3. Frontend last (UI polish)
4. Optimize caching/memory only if issues arise

**Confidence Notes:**
- Architecture patterns: HIGH (standard web app + ML inference pattern)
- M1 optimization: MEDIUM-HIGH (based on kokoro-onnx docs and community reports)
- Build order: HIGH (clear dependency chain)
