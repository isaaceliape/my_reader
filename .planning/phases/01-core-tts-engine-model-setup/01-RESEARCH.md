# Phase 1 Research: Core TTS Engine & Model Setup

**Phase:** 1 - Core TTS Engine & Model Setup  
**Researched:** 2026-03-07 (updated)  
**Confidence:** HIGH

---

## Research Goal

Answer: "What do I need to know to implement the core TTS engine that loads efficiently and generates high-quality audio locally on M1?"

## Key Decisions from Context

- **TTS Engine:** Kokoro (locked decision) — 82M parameters, ~200MB memory, Apache 2.0 license
- **Backend Framework:** FastAPI (locked decision) — Python-based, async support
- **Target Hardware:** MacBook Air M1 (2020), 8-16GB RAM
- **Device Priority:** MPS (Metal Performance Shaders) with CPU fallback

---

## Technology Deep Dive

### Kokoro TTS (≥0.9.4, v1.0 models available)

**What it is:** A compact 82M parameter neural TTS model achieving near-ElevenLabs quality.

**Latest Updates (March 2025):**
- **v1.0 models released** (Jan 28, 2025) — improved quality and consistency
- Uses `misaki` G2P library instead of direct espeak-ng calls
- Multi-language support: English ('a', 'b'), Spanish ('e'), French ('f'), Hindi ('h'), Italian ('i'), Japanese ('j'), Portuguese ('p'), Mandarin ('z')

**Installation:**
```bash
pip install kokoro>=0.9.4
pip install soundfile>=0.13.0
# espeak-ng still required as OOD fallback
brew install espeak-ng  # macOS
```

**Key API Pattern:**
```python
from kokoro import KPipeline
import torch

# Initialize once at startup
pipeline = KPipeline(
    lang_code='a',  # American English
    device='mps' if torch.backends.mps.is_available() else 'cpu'
)

# Load voice (lazy loading recommended)
voice = pipeline.load_voice('af_heart')

# Generate audio
generator = pipeline(text, voice=voice, speed=1.0)
audio_segments = []
for gs, ps, audio in generator:
    audio_segments.append(audio)

# Concatenate and save
import torchaudio
torchaudio.save('output.wav', torch.cat(audio_segments), 24000)
```

**Memory Footprint:**
- Base model: ~200MB (loaded once)
- Per voice: ~50-100MB
- Recommended: Load 2-3 voices max on 8GB systems

**MPS vs CPU Performance:**
- MPS: 50-100x real-time factor (RTF) on M1
- CPU: 5-10x RTF (still usable, much slower)
- **CRITICAL:** Set `PYTORCH_ENABLE_MPS_FALLBACK=1` for M1 GPU acceleration
- Fallback logic essential — MPS has incomplete operator coverage

### PyTorch MPS Backend

**Device Detection:**
```python
import torch
import os

# IMPORTANT: Enable MPS fallback for Apple Silicon
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'

def get_optimal_device():
    if torch.backends.mps.is_available():
        try:
            # Test tensor to verify MPS works
            test = torch.zeros(1).to('mps')
            return 'mps'
        except:
            return 'cpu'
    return 'cpu'
```

**Known Issues:**
- MPS requires `PYTORCH_ENABLE_MPS_FALLBACK=1` environment variable
- Some operations fallback to CPU silently
- First inference is slower (warmup required)
- Memory fragmentation possible with long-running service

### Alternative: kokoro-onnx

For even faster inference, consider `kokoro-onnx`:
- ONNX Runtime instead of PyTorch
- ~300MB model (~80MB quantized)
- Near real-time on M1
- MIT licensed (model still Apache 2.0)

```bash
pip install kokoro-onnx soundfile
```

### Voice Selection

**Recommended curated voices (2-3):**

| Voice ID | Gender | Quality | Language | Notes |
|----------|--------|---------|----------|-------|
| `af_heart` | Female | Excellent | American | Warm, natural tone |
| `am_echo` | Male | Excellent | American | Clear, professional |
| `bf_emma` | Female | Very Good | British | Accent variety |

**Voice Loading Pattern:**
```python
class VoiceManager:
    def __init__(self, pipeline):
        self.pipeline = pipeline
        self.loaded_voices = {}
        self.voice_configs = {
            'af_heart': {'lang': 'a', 'gender': 'female'},
            'am_echo': {'lang': 'a', 'gender': 'male'},
            'bf_emma': {'lang': 'b', 'gender': 'female'},
        }
    
    def get_voice(self, voice_id):
        if voice_id not in self.loaded_voices:
            self.loaded_voices[voice_id] = self.pipeline.load_voice(voice_id)
        return self.loaded_voices[voice_id]
```

### Text Preprocessing

**Critical for quality output:**

```python
import re

def preprocess_text(text: str) -> str:
    """Normalize text for TTS."""
    # Handle numbers
    text = re.sub(r'\b(\d+)\b', lambda m: num2words(int(m.group(1))), text)
    
    # Expand common abbreviations
    abbreviations = {
        'Dr.': 'Doctor',
        'Mr.': 'Mister',
        'Mrs.': 'Misses',
        'vs.': 'versus',
        'etc.': 'et cetera',
        'e.g.': 'for example',
        'i.e.': 'that is',
    }
    for abbr, full in abbreviations.items():
        text = text.replace(abbr, full)
    
    # Remove emojis (not supported)
    text = re.sub(r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF]', '', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text
```

**Edge Cases to Handle:**
- Numbers (cardinals, ordinals, dates, times)
- Abbreviations and acronyms
- Special characters (currency, math)
- Very long text (chunking needed)
- Empty or whitespace-only input

### Singleton TTS Service Pattern

**Critical for performance — never load per-request:**

```python
import os
os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'  # BEFORE importing torch

from functools import lru_cache

class TTSService:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.device = get_optimal_device()
        self.pipeline = KPipeline(lang_code='a', device=self.device)
        self.voice_manager = VoiceManager(self.pipeline)
        self.warmup()  # First inference is slow
    
    def warmup(self):
        """Run dummy inference to warm up model."""
        list(self.pipeline("Hello world", voice=self.voice_manager.get_voice('af_heart'), speed=1.0))
    
    def generate(self, text: str, voice_id: str, speed: float = 1.0):
        """Generate audio for text."""
        processed_text = preprocess_text(text)
        voice = self.voice_manager.get_voice(voice_id)
        
        audio_segments = []
        for gs, ps, audio in self.pipeline(processed_text, voice=voice, speed=speed):
            audio_segments.append(audio)
        
        return torch.cat(audio_segments) if audio_segments else None
```

---

## Architecture Patterns

### Layer Structure

```
┌─────────────────────────────────────┐
│  TTS Service (Singleton)            │
│  - Model initialization             │
│  - Voice management                 │
│  - Text preprocessing               │
│  - Audio generation                 │
├─────────────────────────────────────┤
│  Kokoro Pipeline                    │
│  - PyTorch inference                │
│  - Phonemization (misaki/espeak-ng) │
│  - Audio synthesis                  │
├─────────────────────────────────────┤
│  PyTorch / MPS                      │
│  - MPS / CPU execution              │
│  - Memory management                │
└─────────────────────────────────────┘
```

### Error Handling Strategy

```python
class TTSError(Exception):
    pass

class VoiceNotFoundError(TTSError):
    pass

class MPSFallbackError(TTSError):
    """MPS failed, fell back to CPU."""
    pass

def safe_generate(text, voice_id, device_preference='mps'):
    try:
        return tts_service.generate(text, voice_id)
    except RuntimeError as e:
        if 'MPS' in str(e):
            # Fallback to CPU
            logger.warning("MPS error, falling back to CPU")
            return tts_service.generate(text, voice_id, device='cpu')
        raise TTSError(f"Generation failed: {e}")
```

---

## Critical Pitfalls

### 1. Memory Pressure on 8GB

**Problem:** Loading multiple voices + PyTorch overhead can exceed 8GB.

**Solution:**
- Lazy voice loading (load on first use)
- Max 2-3 voices loaded simultaneously
- LRU cache with size limit
- Monitor with `psutil` or Activity Monitor

### 2. MPS Incompatibility

**Problem:** PyTorch MPS has incomplete operator coverage.

**Solution:**
- **Set `PYTORCH_ENABLE_MPS_FALLBACK=1`** before importing torch
- Always implement CPU fallback
- Test on actual M1 hardware
- Graceful degradation (log warning, continue)

### 3. Model Loading Per Request

**Problem:** Loading Kokoro per request adds 5-15s latency.

**Solution:**
- Singleton pattern mandatory
- Load at application startup
- Health check endpoint to verify loaded state

### 4. Text Preprocessing Gaps

**Problem:** Unhandled abbreviations, numbers, emojis cause poor output.

**Solution:**
- Comprehensive preprocessing pipeline
- User-facing documentation of limitations
- Graceful handling (strip or convert)

---

## Success Metrics

| Metric | Target | How to Measure |
|--------|--------|----------------|
| Memory Usage | <4GB on 8GB M1 | Activity Monitor / psutil |
| Startup Time | <10 seconds | `time python -c "import app"` |
| RTF (Real-time Factor) | 50x+ on M1 | `audio_duration / generation_time` |
| Voice Quality | ≈ElevenLabs | Subjective A/B test |
| Offline Operation | 100% | Disconnect wifi, test |

---

## Implementation Checklist

- [ ] Kokoro ≥0.9.4 installed with dependencies
- [ ] espeak-ng installed and accessible
- [ ] `PYTORCH_ENABLE_MPS_FALLBACK=1` set in environment
- [ ] Device detection with MPS/CPU fallback
- [ ] Singleton TTS service initialized at startup
- [ ] 2-3 voices curated and tested
- [ ] Text preprocessing pipeline implemented
- [ ] Error handling for edge cases
- [ ] Memory monitoring in place
- [ ] Startup time verified <10s
- [ ] Quality validated against ElevenLabs

---

## Sources

- Kokoro GitHub: https://github.com/hexgrad/kokoro
- Kokoro v1.0 Release: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
- kokoro-onnx: https://github.com/thewh1teagle/kokoro-onnx
- PyTorch MPS: https://pytorch.org/docs/stable/notes/mps.html
- Project Research: `.planning/research/SUMMARY.md`

---

*Updated with v1.0 model findings. Ready for planning.*
