# Project Research Summary

**Project:** Local TTS Web App
**Domain:** Local text-to-speech web applications with neural voice synthesis
**Researched:** 2026-03-06
**Confidence:** HIGH

## Executive Summary

This research confirms that building a high-quality local TTS web app on Apple Silicon (M1) is **highly feasible** using modern open-source tools. The recommended approach uses **Kokoro** as the TTS engine—a compact 82M parameter model that achieves ElevenLabs-level quality while maintaining a small ~200MB memory footprint. Combined with **FastAPI** for the web backend and a minimal vanilla JavaScript frontend, this stack delivers professional-grade voice synthesis with 50-100x real-time inference speed on M1 hardware via PyTorch's MPS (Metal Performance Shaders) backend.

The key insight from this research is that **quality over quantity wins in the local TTS space**. While competitors offer 10,000+ voices in the cloud, a curated set of 2-3 exceptional local voices (e.g., `af_heart`, `am_echo`, `bf_emma`) provides a superior user experience—no choice paralysis, instant offline operation, and complete privacy. The architecture is straightforward: a Python backend wrapping the Kokoro pipeline, served via FastAPI, with a simple HTML/JS frontend. This avoids the complexity of real-time streaming while still delivering responsive synthesis.

The main risks are **memory management** on 8GB MacBook Airs and **MPS compatibility** edge cases. The Kokoro model itself is lightweight, but PyTorch's MPS backend has incomplete operator coverage. However, research shows stable fallbacks to CPU work reliably, and memory can be managed through lazy loading and voice quantization. The most critical anti-pattern to avoid is loading models per-request (adds 5-15s latency)—instead, load once at startup and reuse.

## Key Findings

### Recommended Stack

The optimal 2025 stack for local TTS on Apple Silicon centers on Kokoro—a 2024 release that has quickly become the gold standard for open-source TTS. At 82M parameters versus XTTS-v2's 400M+, it offers comparable quality with dramatically lower resource requirements. The stack is intentionally minimal: Python 3.10-3.12, PyTorch 2.2+ with MPS support, FastAPI 0.115.x for the web layer, and vanilla HTML/JS for the frontend. For rapid prototyping, Gradio 5.x can provide a complete UI in 10 lines of Python.

**Core technologies:**
- **Kokoro (≥0.9.4)**: TTS inference — Apache 2.0 licensed, 50x faster than real-time on M1, near-ElevenLabs quality
- **PyTorch (2.2.0+)**: Deep learning framework — Native MPS support for Apple Silicon GPU acceleration
- **FastAPI (0.115.x)**: API framework — Industry standard for ML APIs, automatic OpenAPI docs, async support
- **espeak-ng (1.51+)**: G2P phonemizer — Required for Kokoro's English OOD fallback, lightweight
- **soundfile (0.13.x)**: Audio I/O — Fast WAV/FLAC handling via optimized libsndfile
- **Vanilla HTML/JS**: Frontend — No framework needed for textarea + play button interface

### Expected Features

User expectations for local TTS apps center on **zero-friction operation** and **privacy guarantees**. The core value proposition is that text never leaves the machine—this is the primary differentiator against cloud competitors like ElevenLabs. Users expect standard audio controls (play/pause, speed control 0.5x-2x), audio export (MP3/WAV), and voice selection. However, they do *not* need 100+ voices—2-3 curated high-quality voices reduce choice paralysis and improve UX.

**Must have (table stakes):**
- **Text input area** — Core functionality with auto-resize
- **Voice selection (2-3 curated)** — Quality over quantity
- **Play/pause controls** — Standard HTML5 audio controls acceptable
- **Speed control** — 0.75x, 1x, 1.25x, 1.5x options
- **MP3/WAV export** — Download generated audio files
- **Offline operation** — 100% local processing, no cloud fallbacks

**Should have (competitive):**
- **Zero-setup UX** — Open app, paste text, press play—no accounts or subscriptions
- **Privacy-first architecture** — No data leaves machine, major differentiator
- **Native macOS integration** — Menu bar widget, global keyboard shortcuts
- **Word highlighting sync** — Text highlighted as spoken (audio-text sync)
- **Voice cloning (XTTS v2)** — Clone from 6-second sample (Phase 2+)

**Defer (v2+):**
- SSML support — Advanced speech markup
- Multi-language voices — Beyond English
- Batch processing — Multiple file conversion
- Plugin system — Third-party voice models
- Audio effects — Reverb, EQ, background noise

### Architecture Approach

The architecture follows a **layered ML inference pattern**: Frontend (Browser) → HTTP API (FastAPI) → TTS Service Layer → ONNX Runtime (Kokoro). This separation of concerns isolates the HTTP layer from TTS logic, making the engine swappable. The TTS Service acts as a singleton, loading models once at startup (critical for performance) and managing voice embeddings. Audio generation can be cached to avoid reprocessing identical requests.

**Major components:**
1. **Frontend** — Vanilla HTML/JS for text input, voice selection, audio playback via Web Audio API
2. **Web Server (FastAPI)** — HTTP endpoints (/tts, /voices, /health), request validation, audio streaming
3. **TTS Service Layer** — Singleton wrapper around Kokoro, model initialization, text preprocessing, audio generation
4. **Audio Cache** — In-memory or SQLite storage for recent generations to avoid reprocessing
5. **Model Files** — ONNX weights (~300MB) and voice configs (~10MB), downloaded at setup, loaded at startup

**Key patterns:**
- **Model loading**: Load once at startup (singleton), never per-request
- **Text chunking**: Split long texts by sentences/paragraphs, generate incrementally
- **Audio streaming**: Stream chunks as generated rather than synthesize-then-serve
- **Voice preloading**: Load 2-3 voices at startup, lazy-load others on demand

### Critical Pitfalls

The research identified several pitfalls that can derail the project if not addressed early. The most critical is **memory pressure from eager model loading**—loading multiple voices or models on an 8GB MacBook Air causes system-wide memory pressure, swap thrashing, and crashes. The solution is lazy loading, single-model-at-a-time policies, and LRU caching with memory limits. MPS incompatibility is another risk; while PyTorch's MPS backend accelerates inference, it has incomplete operator coverage and can silently fall back to CPU or crash.

1. **Loading large models without memory management** — Implement lazy loading, single-model-at-a-time policy, quantized models (INT8), and LRU cache with max_memory_mb configuration
2. **Blocking the main thread during synthesis** — Always run TTS in background threads, use FastAPI BackgroundTasks, implement WebSocket streaming for progress updates
3. **Assuming MPS just works** — Test all models on M1 hardware, maintain CPU fallback logic, benchmark MPS vs CPU (sometimes CPU is faster)
4. **Streaming audio without proper buffer management** — Use Web Audio API with AudioWorklet, proper HTTP headers (Content-Type: audio/wav), test on Safari/Chrome/Firefox
5. **Text preprocessing inconsistencies** — Implement normalization pipeline (numbers→words, abbreviations→full words), strip emojis, set max text length limits (500-1000 chars)
6. **Voice cloning without safeguards** — Document ethical use policy, validate reference audio (duration, SNR), implement quality gating and audit trails

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Core TTS Engine & Model Setup
**Rationale:** The TTS engine is a blocking dependency for all other functionality. Without working model loading and inference, nothing else matters. This phase must also validate MPS compatibility on target hardware.
**Delivers:** Working Kokoro integration, model loading with memory management, basic text→audio pipeline, CPU/MPS device detection and fallback
**Addresses:** Core TTS functionality, offline operation, voice quality
**Avoids:** Memory pressure pitfalls (lazy loading), MPS incompatibility (fallback logic), text preprocessing gaps (normalization pipeline)
**Research Flag:** MEDIUM — MPS behavior needs validation on actual M1 hardware, though patterns are well-documented

### Phase 2: Web API & Audio Streaming
**Rationale:** Once TTS works, wrap it in a web API. This phase establishes the HTTP layer and audio delivery mechanism. Streaming implementation is critical for UX on long texts.
**Delivers:** FastAPI application, /tts and /voices endpoints, audio streaming with proper headers, error handling middleware
**Uses:** FastAPI stack element, async/await patterns, WebSocket for progress
**Implements:** TTS Service Layer singleton, API routes, audio cache
**Avoids:** Blocking main thread (async patterns), streaming failures (proper headers/buffers)
**Research Flag:** LOW — FastAPI patterns are well-established, standard implementation

### Phase 3: Frontend & User Interface
**Rationale:** With working API, build the user-facing interface. This phase focuses on UX polish and integration with the backend.
**Delivers:** HTML/CSS/JS frontend, text input with character counter, voice selector, audio player, keyboard shortcuts (Cmd+Enter)
**Uses:** Vanilla JS frontend stack element
**Implements:** Frontend component, API integration
**Avoids:** UX pitfalls (progress indication, inline preview)
**Research Flag:** LOW — Simple UI patterns, no complex state management needed

### Phase 4: Optimization & Polish
**Rationale:** After core functionality works, optimize for performance and add quality-of-life features. This phase addresses the "looks done but isn't" checklist.
**Delivers:** Audio caching, text chunking for long inputs, memory optimization, cross-browser testing, 8GB RAM compliance verification
**Implements:** Audio cache component, text preprocessing enhancements
**Avoids:** All critical pitfalls validated, performance traps addressed
**Research Flag:** MEDIUM — Memory optimization strategies may need testing on 8GB hardware

### Phase 5: Advanced Features (v1.x+)
**Rationale:** Once core is stable and validated, add differentiating features. Voice cloning is the highest-value addition but requires careful safeguards.
**Delivers:** Voice cloning (XTTS v2 integration), word highlighting sync, batch processing, menu bar widget
**Avoids:** Voice cloning risks (ethical policy, quality gates)
**Research Flag:** HIGH — Voice cloning implementation and safeguards need deeper research

### Phase Ordering Rationale

- **Engine → API → Frontend** follows clear dependency chain: backend must work before UI can integrate
- **Core → Optimization → Advanced** groups risk mitigation early—memory and MPS issues addressed in Phase 1-2, not discovered in production
- **Voice cloning deferred** to Phase 5 because it's high-complexity and ethically sensitive—core value proposition (privacy-first local TTS) doesn't require it
- **8GB RAM validation** built into Phase 4 optimization, ensuring the target hardware (MacBook Air M1) is fully supported before adding features

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** MPS compatibility verification on actual M1 hardware; ONNX Runtime Metal optimization details
- **Phase 5:** Voice cloning implementation patterns, ethical safeguards, quality validation algorithms

Phases with standard patterns (skip research-phase):
- **Phase 2:** FastAPI is industry standard with comprehensive documentation; async patterns well-established
- **Phase 3:** Simple HTML/JS frontend is well-documented; no complex framework patterns needed

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | Kokoro is actively maintained with versioned releases, official GitHub repo, tested on M1; FastAPI is industry standard; PyTorch MPS is stable since 2.0 |
| Features | HIGH | Standard TTS functionality well-documented; competitor analysis from major players (ElevenLabs, NaturalReader) provides clear baseline |
| Architecture | HIGH | Layered ML inference is established pattern; clear dependency chain; anti-patterns well-documented |
| Pitfalls | HIGH | Based on GitHub issues from Coqui TTS, Piper, and PyTorch with concrete reproduction steps and solutions |

**Overall confidence:** HIGH

All four research areas converge on consistent recommendations. The Kokoro→FastAPI→Vanilla JS stack is validated by multiple sources as the 2025 standard for local TTS. Feature expectations are clear from competitor analysis. Architecture patterns follow established ML inference best practices. Pitfalls are well-documented in open-source issue trackers with known solutions.

### Gaps to Address

- **MPS actual performance:** Research shows MPS *should* work, but actual RTF (real-time factor) on M1 needs validation during Phase 1 implementation
- **8GB RAM real-world usage:** Kokoro claims ~200MB footprint, but PyTorch MPS overhead varies; need Activity Monitor verification on target hardware
- **Voice quality subjective validation:** Objective metrics show Kokoro ≈ ElevenLabs, but user perception testing needed during Phase 3
- **Voice cloning legal framework:** Ethical use policy and liability protection need legal review before Phase 5 implementation

## Sources

### Primary (HIGH confidence)
- Kokoro GitHub (https://github.com/hexgrad/kokoro) — Official implementation, version 0.9.4+ recommended, M1 optimization documented
- PyTorch MPS Documentation (https://pytorch.org/docs/stable/notes/mps.html) — Official Apple Silicon support, operator coverage
- FastAPI Documentation (https://fastapi.tiangolo.com) — Latest stable patterns, async/await best practices
- kokoro-onnx GitHub (https://github.com/thewh1teagle/kokoro-onnx) — ONNX Runtime implementation for Kokoro

### Secondary (MEDIUM confidence)
- ElevenLabs (https://elevenlabs.io) — Market leader feature analysis, quality baseline
- Coqui TTS GitHub (https://github.com/coqui-ai/TTS) — XTTS v2 documentation, community maintenance status
- Piper TTS GitHub (https://github.com/rhasspy/piper) — Alternative engine comparison, model loading patterns
- ONNX Runtime Docs (https://onnxruntime.ai/docs/) — Deployment optimization, M1 acceleration

### Tertiary (LOW confidence / Community)
- Coqui TTS GitHub Issue #3800 — Memory-related crashes, mitigation strategies
- PyTorch GitHub Issue #77764 — MPS operator coverage tracking, known limitations
- Piper GitHub Issue #567 — Memory leak patterns in Terminate() calls
- MeloTTS GitHub — Alternative engine architecture reference

---
*Research completed: 2026-03-06*
*Ready for roadmap: yes*
