# Requirements: Local TTS Web App

**Defined:** 2025-03-06
**Core Value:** Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.

## v1 Requirements

Requirements for initial release. Each maps to roadmap phases.

### Core TTS

- [ ] **CORE-01**: User can paste or type text into a textarea input
- [ ] **CORE-02**: User can select from 2-3 curated high-quality voices via dropdown
- [ ] **CORE-03**: User can click Play to generate audio from the text
- [ ] **CORE-04**: User can pause and resume playback using audio controls
- [ ] **CORE-05**: Audio player displays progress bar and current time
- [ ] **CORE-06**: User can adjust playback speed (0.75x, 1x, 1.25x, 1.5x)
- [ ] **CORE-07**: User can download generated audio as MP3 file
- [ ] **CORE-08**: Voice synthesis produces natural, ElevenLabs-quality output
- [ ] **CORE-09**: All processing runs locally without internet connection

### User Experience

- [ ] **UX-01**: User can trigger playback with Cmd+Enter keyboard shortcut
- [ ] **UX-02**: User can pause/resume with Space keyboard shortcut
- [ ] **UX-03**: Interface is minimal and focused (textarea, voice selector, play button, audio player)
- [ ] **UX-04**: App launches without setup, accounts, or configuration

### Technical

- [ ] **TECH-01**: Application runs on MacBook Air M1 (2020) with 8-16GB RAM
- [ ] **TECH-02**: TTS engine loads once at startup, not per request
- [ ] **TECH-03**: Text preprocessing handles edge cases (numbers, abbreviations)

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Advanced Features

- **ADV-01**: Word highlighting sync - text highlights as audio plays
- **ADV-02**: Voice cloning - clone custom voices from 6-second samples (XTTS v2)
- **ADV-03**: Batch processing - convert multiple text files at once
- **ADV-04**: History - view and replay recent conversions
- **ADV-05**: Menu bar widget - quick access from macOS menu bar

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Cloud sync / accounts | Violates privacy-first, local-only principle |
| 100+ voice library | Choice paralysis; 2-3 curated voices are better |
| Real-time streaming | Adds complexity; pre-generate + progress indicator is sufficient |
| Speech-to-text | Different product category; out of scope |
| Browser extension | Different product with different constraints |
| Mobile apps | Different platform; focus on macOS web app |
| Subscription tiers | Users hate subscriptions for local software |
| SSML support | Advanced feature; not needed for core use case |
| Multi-language voices | v1 focused on English; add later if needed |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| CORE-01 | Phase 3 | Pending |
| CORE-02 | Phase 3 | Pending |
| CORE-03 | Phase 2 | Pending |
| CORE-04 | Phase 2 | Pending |
| CORE-05 | Phase 2 | Pending |
| CORE-06 | Phase 2 | Pending |
| CORE-07 | Phase 2 | Pending |
| CORE-08 | Phase 1 | Pending |
| CORE-09 | Phase 1 | Pending |
| UX-01 | Phase 3 | Pending |
| UX-02 | Phase 3 | Pending |
| UX-03 | Phase 3 | Pending |
| UX-04 | Phase 1 | Pending |
| TECH-01 | Phase 4 | Pending |
| TECH-02 | Phase 1 | Pending |
| TECH-03 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 16 total
- Mapped to phases: 16
- Unmapped: 0 ✓

**Phase Assignment Summary:**
- **Phase 1** (Core TTS Engine): 8 requirements — TTS engine setup, local processing, voice quality
- **Phase 2** (Web API): 5 requirements — Audio generation, playback controls, download
- **Phase 3** (Frontend): 5 requirements — Interface, keyboard shortcuts, voice selection
- **Phase 4** (Optimization): 1 requirement — Hardware validation and performance optimization

---
*Requirements defined: 2025-03-06*
*Last updated: 2025-03-06 after initial definition*
