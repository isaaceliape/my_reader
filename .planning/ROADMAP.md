# Roadmap: Local TTS Web App

**Project:** Local TTS Web App  
**Goal:** Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.  
**Last Updated:** 2025-03-06

---

## Overview

This roadmap delivers a local-first text-to-speech web application in 4 phases. Each phase builds on the previous, starting with the TTS engine (the core dependency), then wrapping it in a web API, building the user interface, and finally optimizing for performance and edge cases.

**Phase Philosophy:**
- Phase 1 establishes the engine - nothing works without Kokoro TTS running efficiently
- Phase 2 creates the API layer - backend must work before UI can integrate  
- Phase 3 delivers the interface - user-facing features after core infrastructure
- Phase 4 optimizes and polishes - performance, caching, and quality validation

---

## Phases

### Phase 1: Core TTS Engine & Model Setup

**Goal:** TTS engine loads efficiently and generates high-quality audio locally

**Dependencies:** None (foundation phase)

**Requirements:**
| ID | Description |
|----|-------------|
| CORE-01 | User can paste or type text into a textarea input |
| CORE-02 | User can select from 2-3 curated high-quality voices via dropdown |
| CORE-08 | Voice synthesis produces natural, ElevenLabs-quality output |
| CORE-09 | All processing runs locally without internet connection |
| TECH-01 | Application runs on MacBook Air M1 (2020) with 8-16GB RAM |
| TECH-02 | TTS engine loads once at startup, not per request |
| TECH-03 | Text preprocessing handles edge cases (numbers, abbreviations) |
| UX-04 | App launches without setup, accounts, or configuration |

**Success Criteria:**
1. Kokoro TTS loads at application startup and stays resident in memory
2. Application runs without errors on MacBook Air M1 with 8GB RAM (verified via Activity Monitor)
3. User can input text and receive synthesized audio without internet connection
4. Voice quality matches or approaches ElevenLabs naturalness (subjective validation)
5. Text preprocessing correctly handles numbers, abbreviations, and special characters

**Deliverables:**
- Working Kokoro TTS integration with memory management
- Singleton TTS service that loads once at startup
- Basic text→audio pipeline with preprocessing
- MPS/CPU device detection with automatic fallback

**Plans:** 3 plans in 3 waves

| Wave | Plans | Description |
|------|-------|-------------|
| 1 | 01 | Project setup, device detection, voice manager |
| 2 | 02 | Text preprocessing, TTS service singleton |
| 3 | 03 | Audio generation, integration testing |

Plan Files:
- [ ] `01-core-tts-engine-model-setup-01-PLAN.md` — Setup + Device + Voices
- [ ] `01-core-tts-engine-model-setup-02-PLAN.md` — Preprocessing + Service
- [ ] `01-core-tts-engine-model-setup-03-PLAN.md` — Generator + Testing

---

### Phase 2: Web API & Audio Streaming

**Goal:** Backend API serves TTS functionality with proper audio delivery and controls

**Dependencies:** Phase 1 (TTS engine must be working)

**Requirements:**
| ID | Description |
|----|-------------|
| CORE-03 | User can click Play to generate audio from the text |
| CORE-04 | User can pause and resume playback using audio controls |
| CORE-05 | Audio player displays progress bar and current time |
| CORE-06 | User can adjust playback speed (0.75x, 1x, 1.25x, 1.5x) |
| CORE-07 | User can download generated audio as MP3 file |

**Success Criteria:**
1. FastAPI endpoints /tts and /voices respond correctly to HTTP requests
2. Generated audio streams to browser with proper headers and minimal latency
3. Audio player shows accurate progress bar and current playback time
4. User can pause and resume playback seamlessly
5. Playback speed can be changed to 0.75x, 1x, 1.25x, or 1.5x
6. User can download generated audio as MP3 file

**Deliverables:**
- FastAPI application with /tts and /voices endpoints
- Audio streaming with proper Content-Type headers
- Error handling middleware
- Integration with Phase 1 TTS service

---

### Phase 3: Frontend & User Interface

**Goal:** Clean, minimal interface enables core TTS workflows with keyboard shortcuts

**Dependencies:** Phase 2 (API endpoints must be available)

**Requirements:**
| ID | Description |
|----|-------------|
| CORE-01 | User can paste or type text into a textarea input |
| CORE-02 | User can select from 2-3 curated high-quality voices via dropdown |
| UX-01 | User can trigger playback with Cmd+Enter keyboard shortcut |
| UX-02 | User can pause/resume with Space keyboard shortcut |
| UX-03 | Interface is minimal and focused (textarea, voice selector, play button, audio player) |

**Success Criteria:**
1. User sees a clean interface with textarea, voice dropdown, and play button
2. User can type or paste text into the textarea
3. User can select from 2-3 curated voices in a dropdown
4. Cmd+Enter triggers audio generation and playback
5. Space bar pauses and resumes audio playback
6. Interface works in Safari, Chrome, and Firefox on macOS

**Deliverables:**
- HTML/CSS/JS frontend with vanilla JavaScript
- API integration for /tts and /voices endpoints
- Keyboard shortcut handling (Cmd+Enter, Space)
- Responsive design for desktop browsers

---

### Phase 4: Optimization & Polish

**Goal:** Application performs efficiently with caching, handles edge cases, and runs smoothly on target hardware

**Dependencies:** Phases 1-3 (core functionality must be complete)

**Requirements:**
| ID | Description |
|----|-------------|
| TECH-01 | Application runs on MacBook Air M1 (2020) with 8-16GB RAM (verified) |

**Success Criteria:**
1. Audio caching prevents re-generation of identical text/voice combinations
2. Long text inputs are chunked and processed without memory issues
3. Application memory usage stays under 4GB during normal operation on 8GB M1
4. Cross-browser testing confirms compatibility with Safari, Chrome, Firefox
5. Edge cases handled: empty input, very long text (>5000 chars), special characters
6. Application starts within 10 seconds on target hardware

**Deliverables:**
- In-memory audio cache with LRU eviction
- Text chunking for long inputs
- Memory optimization and profiling
- Cross-browser compatibility verification
- Edge case handling and error messages

---

## Progress

| Phase | Status | Requirements | Completion |
|-------|--------|--------------|------------|
| Phase 1: Core TTS Engine | Not Started | 8 | 0% |
| Phase 2: Web API | Not Started | 5 | 0% |
| Phase 3: Frontend | Not Started | 5 | 0% |
| Phase 4: Optimization | Not Started | 1 | 0% |
| **Total** | — | **16** | **0%** |

---

## Requirement Coverage

**All 16 v1 requirements mapped:**

| Requirement | Phase | Description |
|-------------|-------|-------------|
| CORE-01 | Phase 3 | Text input (textarea) |
| CORE-02 | Phase 3 | Voice selection dropdown |
| CORE-03 | Phase 2 | Play button generates audio |
| CORE-04 | Phase 2 | Pause/resume controls |
| CORE-05 | Phase 2 | Progress bar and time display |
| CORE-06 | Phase 2 | Playback speed adjustment |
| CORE-07 | Phase 2 | Download as MP3 |
| CORE-08 | Phase 1 | Natural voice quality |
| CORE-09 | Phase 1 | Local-only processing |
| UX-01 | Phase 3 | Cmd+Enter shortcut |
| UX-02 | Phase 3 | Space pause/resume shortcut |
| UX-03 | Phase 3 | Minimal interface |
| UX-04 | Phase 1 | Zero-setup launch |
| TECH-01 | Phase 4 | M1 8-16GB RAM verified |
| TECH-02 | Phase 1 | Model loads once at startup |
| TECH-03 | Phase 1 | Text preprocessing |

**Coverage:** 16/16 requirements mapped ✓  
**Orphans:** 0

---

## Phase Ordering Rationale

**Engine → API → Frontend → Optimization**

1. **Phase 1 (Engine) first:** The TTS engine is a blocking dependency. Without working model loading and inference, no other functionality matters. This phase also validates MPS compatibility on target hardware and establishes memory management patterns.

2. **Phase 2 (API) second:** Once TTS works locally, wrap it in a web API. This creates the interface that Phase 3 will consume. Audio streaming implementation is critical for UX.

3. **Phase 3 (Frontend) third:** With working API endpoints, build the user interface. This phase focuses on UX polish and integrates with the backend.

4. **Phase 4 (Optimization) last:** After core functionality works, optimize for performance. This addresses the "looks done but isn't" checklist: caching, edge cases, memory validation.

**Risk Mitigation:**
- Memory and MPS issues are addressed in Phase 1-2, not discovered in production
- 8GB RAM validation is built into Phase 4, ensuring target hardware is fully supported
- Voice quality validation happens early (Phase 1) when engine choices can still be changed

---

## Success Criteria Summary

### Phase 1: Core TTS Engine & Model Setup
- [ ] Kokoro TTS loads at startup and stays resident
- [ ] Runs on M1 8GB without memory pressure
- [ ] Works offline with local processing
- [ ] ElevenLabs-quality voice output
- [ ] Text preprocessing handles edge cases

### Phase 2: Web API & Audio Streaming
- [ ] /tts and /voices endpoints respond correctly
- [ ] Audio streams with proper headers
- [ ] Progress bar and time display work
- [ ] Pause/resume controls functional
- [ ] Playback speed adjustment (0.75x-1.5x)
- [ ] MP3 download available

### Phase 3: Frontend & User Interface
- [ ] Clean minimal interface renders
- [ ] Textarea accepts input
- [ ] Voice dropdown shows 2-3 options
- [ ] Cmd+Enter triggers playback
- [ ] Space pauses/resumes
- [ ] Works in Safari, Chrome, Firefox

### Phase 4: Optimization & Polish
- [ ] Audio caching prevents regeneration
- [ ] Long text chunked properly
- [ ] Memory usage under 4GB on 8GB M1
- [ ] Cross-browser compatibility verified
- [ ] Edge cases handled gracefully
- [ ] Startup under 10 seconds

---

*Roadmap created: 2025-03-06*
