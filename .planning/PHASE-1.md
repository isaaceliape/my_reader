# Phase 1: Core TTS Engine & Model Setup

**Goal:** TTS engine loads efficiently and generates high-quality audio locally

**Time Estimate:** 7-10 sessions (~1-2 weeks at 1 hour/day)

**Dependencies:** None (foundation phase)

---

## Success Criteria

- [ ] Kokoro TTS loads at application startup and stays resident in memory
- [ ] Application runs without errors on MacBook Air M1 with 8GB RAM
- [ ] User can input text and receive synthesized audio without internet connection
- [ ] Voice quality matches or approaches ElevenLabs naturalness
- [ ] Text preprocessing correctly handles numbers, abbreviations, and special characters

---

## Tasks

### Task 1.1: Environment Setup
**Time:** 1 hour  
**Deliverable:** Python virtual environment with dependencies installed

- [ ] Create project structure (`src/`, `static/`, `models/`)
- [ ] Set up Python 3.11 virtual environment
- [ ] Install PyTorch with MPS support (`torch>=2.2.0`)
- [ ] Install Kokoro (`kokoro>=0.9.4`)
- [ ] Install espeak-ng via Homebrew (`brew install espeak-ng`)
- [ ] Verify MPS is available: `python -c "import torch; print(torch.backends.mps.is_available())"`

**Definition of Done:** Can import kokoro and torch, MPS shows as available

---

### Task 1.2: Model Download & Verification
**Time:** 1 hour  
**Deliverable:** Kokoro model files downloaded and verified

- [ ] Download Kokoro model files (ONNX weights, voice configs)
- [ ] Store in `models/` directory (gitignored)
- [ ] Verify model loads without errors
- [ ] Document model size and location in README

**Definition of Done:** Model files present, loads successfully in Python

---

### Task 1.3: Basic TTS Inference
**Time:** 1 hour  
**Deliverable:** Can generate audio from text

- [ ] Create `src/tts/engine.py` with Kokoro wrapper class
- [ ] Implement `generate(text, voice)` method
- [ ] Test with sample text: "Hello, this is a test."
- [ ] Save output as WAV file
- [ ] Listen and verify quality

**Definition of Done:** Can call `engine.generate()` and get playable audio file

---

### Task 1.4: Voice Selection & Testing
**Time:** 1 hour  
**Deliverable:** 2-3 curated voices selected and tested

- [ ] List available Kokoro voices
- [ ] Test each voice with same sample text
- [ ] Select 2-3 best voices (recommend: `af_heart`, `am_echo`, `bf_emma`)
- [ ] Document voice choices in `config.py`
- [ ] A/B test against ElevenLabs sample (subjective quality check)

**Definition of Done:** Voice config file with 2-3 selected voices, quality validated

---

### Task 1.5: Text Preprocessing
**Time:** 1 hour  
**Deliverable:** Text normalization pipeline

- [ ] Create `src/tts/preprocessor.py`
- [ ] Handle numbers: "2024" → "twenty twenty-four"
- [ ] Handle abbreviations: "Dr." → "Doctor", "etc." → "etcetera"
- [ ] Strip emojis and special Unicode
- [ ] Set max text length (500-1000 chars per synthesis)
- [ ] Write unit tests for edge cases

**Definition of Done:** Preprocessor handles common edge cases without errors

---

### Task 1.6: Singleton Model Loader
**Time:** 1 hour  
**Deliverable:** Model loads once at startup, not per-request

- [ ] Create `src/tts/service.py` with singleton pattern
- [ ] Load model on first request (lazy loading)
- [ ] Keep model resident in memory
- [ ] Implement reference counting for voice embeddings
- [ ] Add health check endpoint: `is_loaded()`, `get_voices()`

**Definition of Done:** Model loads once, subsequent calls reuse loaded model

---

### Task 1.7: MPS vs CPU Benchmark
**Time:** 1 hour  
**Deliverable:** Performance baseline documented

- [ ] Benchmark inference on MPS device
- [ ] Benchmark inference on CPU (fallback)
- [ ] Measure: latency, memory usage, audio quality
- [ ] Document results in `research/M1_BENCHMARKS.md`
- [ ] Implement automatic device selection (MPS preferred, CPU fallback)

**Definition of Done:** Know actual RTF on M1, have working fallback logic

---

### Task 1.8: Memory Management
**Time:** 1 hour  
**Deliverable:** Memory usage stays under control

- [ ] Monitor memory usage during inference (Activity Monitor)
- [ ] Implement LRU cache for voice embeddings (max 3 voices loaded)
- [ ] Add `max_memory_mb` configuration
- [ ] Test on 8GB RAM scenario (close other apps, monitor pressure)
- [ ] Document memory footprint in README

**Definition of Done:** App runs on 8GB M1 without memory pressure warnings

---

### Task 1.9: Offline Validation
**Time:** 1 hour  
**Deliverable:** Confirmed working without internet

- [ ] Disconnect from internet
- [ ] Restart application
- [ ] Generate audio from text
- [ ] Verify no network calls are made (check Activity Monitor > Network)
- [ ] Document offline capability in README

**Definition of Done:** Full TTS pipeline works with no internet connection

---

### Task 1.10: Phase 1 Integration Test
**Time:** 1 hour  
**Deliverable:** End-to-end test script

- [ ] Create `tests/phase1_test.py`
- [ ] Test: Load model → Preprocess text → Generate audio → Save file
- [ ] Test all 2-3 voices
- [ ] Test edge cases: empty input, long text, special characters
- [ ] Document any known issues in `STATE.md`

**Definition of Done:** All Phase 1 success criteria validated with test script

---

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MPS incompatibility | MEDIUM | HIGH | CPU fallback ready, test early |
| Memory pressure on 8GB | MEDIUM | HIGH | Lazy loading, LRU cache, monitor closely |
| Voice quality disappointing | LOW | HIGH | Have backup engine ready (Piper, MeloTTS) |
| espeak-ng installation issues | LOW | MEDIUM | Document exact Homebrew command, provide fallback |

---

## Files to Create

```
local_tts/
├── src/
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── engine.py          # Kokoro wrapper
│   │   ├── preprocessor.py    # Text normalization
│   │   ├── service.py         # Singleton service
│   │   └── config.py          # Voice configs, model paths
│   └── main.py                # Entry point
├── models/                    # Gitignored, downloaded at setup
│   └── .gitkeep
├── tests/
│   └── phase1_test.py
├── requirements.txt
└── .planning/
    └── PHASE-1.md             # This file
```

---

## Getting Started (First Session)

**Session 1 Checklist (Task 1.1):**

```bash
# 1. Create project structure
mkdir -p local_tts/{src/tts,static,models,tests}
cd local_tts

# 2. Set up Python virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install torch torchaudio
pip install kokoro soundfile

# 4. Install espeak-ng
brew install espeak-ng

# 5. Verify setup
python -c "import torch; print(f'MPS: {torch.backends.mps.is_available()}')"
python -c "from kokoro import KPipeline; print('Kokoro OK')"
```

If all commands succeed → **Task 1.1 complete!** ✅

---

## Phase 1 Exit Checklist

Before moving to Phase 2, verify:

- [ ] All 10 tasks complete
- [ ] All success criteria validated
- [ ] `tests/phase1_test.py` passes
- [ ] Memory usage documented (must work on 8GB)
- [ ] MPS benchmark documented
- [ ] `STATE.md` updated with current status

---

*Phase 1 Plan Created: 2026-03-06*
*Ready to start: Yes*
