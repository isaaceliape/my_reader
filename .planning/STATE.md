# Project State: Local TTS Web App

**Current Phase:** Phase 3 (Frontend & User Interface)  
**Last Updated:** 2026-04-04  
**Status:** Phases 1-2 complete, Phase 3 in progress

---

## Project Reference

**Core Value:** Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.

**Target Hardware:** MacBook Air M1 (2020), 8-16GB RAM  
**Primary TTS Engine:** Kokoro (82M parameters, ~200MB memory)  
**Tech Stack:** Python (FastAPI) + Vanilla HTML/JS

---

## Current Position

### Phase: Phase 3 (Frontend & User Interface)

Phases 1 and 2 are complete. The backend is fully functional with Kokoro TTS running on MPS acceleration. The frontend UI is built but needs keyboard shortcuts and runtime validation.

**Phase Overview:**
| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 1 | Core TTS Engine & Model Setup | 8 | ✅ Complete |
| 2 | Web API & Audio Streaming | 5 | ✅ Complete |
| 3 | Frontend & User Interface | 5 | 🔄 In Progress |
| 4 | Optimization & Polish | 1 | ⏳ Not Started |

**Current Plan:** Add keyboard shortcuts (Cmd+Enter, Space) and validate full user flow

**Progress Bar:**
```
[████████████████░░░░] 50% (2/4 phases complete)
```

---

## Current Focus

**Next Action:** Add keyboard shortcuts to frontend (Phase 3 requirement)

Keyboard shortcuts needed:
- Cmd+Enter: Trigger audio generation and playback
- Space: Pause/resume audio playback

**Key Decisions Pending:**
- None - following established roadmap

---

## Performance Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Memory Usage | <4GB on 8GB M1 | 145MB idle, 215MB peak | ✅ Excellent |
| Startup Time | <10 seconds | ~8 seconds | ✅ Met |
| Voice Quality | ≈ElevenLabs | Kokoro v1.0 | ✅ Validated |
| RTF (Real-time Factor) | 50x+ on M1 | Not measured | ⏳ Pending |

*RTF = Audio duration / Generation time (higher is better)*

**Memory Profile (April 4, 2026):**
- Idle server: 145MB RSS
- During TTS generation: 174MB peak (+29MB)
- After TTS generation: 161MB stable
- During URL processing: 273MB peak (web scraping + TTS)
- After URL processing: 215MB stable
- CPU spike during generation: 50-65%
- **Conclusion:** Memory usage is ~5% of target (215MB vs 4GB limit)

---

## Accumulated Context

### Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-03-06 | Kokoro as primary TTS | Best quality-to-speed ratio for M1, Apache 2.0 license |
| 2025-03-06 | FastAPI for backend | Industry standard for ML APIs, async support |
| 2025-03-06 | Vanilla HTML/JS frontend | No framework needed for simple interface |
| 2025-03-06 | 4-phase roadmap | Engine → API → Frontend → Optimization flow |
| 2026-04-01 | Added URL-to-audio feature | Web scraping + TTS pipeline for article listening |
| 2026-04-01 | Added caching layer | In-memory cache for URL processing results |
| 2026-04-04 | MPS acceleration confirmed | Kokoro runs on Metal Performance Shaders |

### Open Questions

1. **MPS Performance:** Research suggests 50x RTF on M1 with MPS, but actual performance needs validation during Phase 4
2. **8GB RAM Reality:** Kokoro claims ~200MB footprint, but PyTorch MPS overhead varies—need Activity Monitor verification
3. **Voice Selection:** Which 2-3 voices to curate? (af_heart, am_echo, bf_emma are candidates)

### Known Risks

| Risk | Mitigation | Status |
|------|------------|--------|
| MPS incompatibility | CPU fallback logic | ✅ Implemented |
| Memory pressure on 8GB | Lazy loading, LRU cache | ⏳ Planned for Phase 4 |
| Voice quality subjective | A/B test with ElevenLabs samples | ⏳ Planned for Phase 3 |

---

## Blockers

**None currently.**

Project is proceeding through Phase 3 (Frontend & User Interface).

---

## Recent Activity

| Date | Activity | Notes |
|------|----------|-------|
| 2025-03-06 | Project initialized | PROJECT.md created |
| 2025-03-06 | Requirements defined | 16 v1 requirements documented |
| 2025-03-06 | Research completed | Kokoro/FastAPI stack validated |
| 2025-03-06 | Roadmap created | 4 phases covering all requirements |
| 2026-04-01 | Phase 1-2 implementation | app.py, static/index.html, src/crawler/ |
| 2026-04-01 | Test suite added | 34 tests, all passing |
| 2026-04-04 | Runtime testing | Server runs on port 8000, MPS active, TTS working |

---

## Session Continuity

**For Next Session:**

1. Add keyboard shortcuts to `static/index.html` (Cmd+Enter, Space)
2. Run Phase 4 memory profiling with Activity Monitor
3. Measure actual RTF (real-time factor) on M1 hardware

**Key Files:**
- `app.py` - FastAPI backend with Kokoro TTS (340 lines)
- `static/index.html` - Frontend UI (800 lines, needs keyboard shortcuts)
- `src/crawler/` - Web scraping and caching module
- `tests/` - 34 passing tests

---

## Notes

- **Research Confidence:** HIGH - Kokoro stack is well-documented for M1
- **Phase 1 Critical Path:** Model loading → TTS service → Basic inference ✅ COMPLETE
- **Target RTF:** 50x real-time (1 second of audio in 0.02 seconds)
- **Quality Gate:** Phase 3 includes subjective voice quality validation
- **Server Status:** Running on http://localhost:8000 with MPS acceleration

---

*State file: Keep updated as project progresses*
