# Project State: Local TTS Web App

**Current Phase:** Not started  
**Last Updated:** 2025-03-06  
**Status:** Roadmap complete, awaiting Phase 1 planning

---

## Project Reference

**Core Value:** Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.

**Target Hardware:** MacBook Air M1 (2020), 8-16GB RAM  
**Primary TTS Engine:** Kokoro (82M parameters, ~200MB memory)  
**Tech Stack:** Python (FastAPI) + Vanilla HTML/JS

---

## Current Position

### Phase: None (Roadmap Complete)

The roadmap has been created with 4 phases covering all 16 v1 requirements. Ready to begin Phase 1 planning.

**Phase Overview:**
| Phase | Name | Requirements | Status |
|-------|------|--------------|--------|
| 1 | Core TTS Engine & Model Setup | 8 | Not Started |
| 2 | Web API & Audio Streaming | 5 | Not Started |
| 3 | Frontend & User Interface | 5 | Not Started |
| 4 | Optimization & Polish | 1 | Not Started |

**Current Plan:** None (planning Phase 1 next)

**Progress Bar:**
```
[░░░░░░░░░░░░░░░░░░] 0% (0/4 phases complete)
```

---

## Current Focus

**Next Action:** Plan Phase 1 (Core TTS Engine & Model Setup)

Phase 1 will establish the foundation: Kokoro TTS integration, model loading with memory management, and basic text-to-audio pipeline. This is the blocking dependency for all other functionality.

**Key Decisions Pending:**
- Confirm Kokoro version (0.9.4+ recommended)
- Validate MPS vs CPU performance on actual M1 hardware
- Select 2-3 curated voices from Kokoro's voice library
- Determine text preprocessing scope (numbers, abbreviations, emojis)

---

## Performance Metrics

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| Memory Usage | <4GB on 8GB M1 | — | Not measured |
| Startup Time | <10 seconds | — | Not measured |
| Voice Quality | ≈ElevenLabs | — | Not validated |
| RTF (Real-time Factor) | 50x+ on M1 | — | Not measured |

*RTF = Audio duration / Generation time (higher is better)*

---

## Accumulated Context

### Decisions Made

| Date | Decision | Rationale |
|------|----------|-----------|
| 2025-03-06 | Kokoro as primary TTS | Best quality-to-speed ratio for M1, Apache 2.0 license |
| 2025-03-06 | FastAPI for backend | Industry standard for ML APIs, async support |
| 2025-03-06 | Vanilla HTML/JS frontend | No framework needed for simple interface |
| 2025-03-06 | 4-phase roadmap | Engine → API → Frontend → Optimization flow |

### Open Questions

1. **MPS Performance:** Research suggests 50x RTF on M1 with MPS, but actual performance needs validation during Phase 1
2. **8GB RAM Reality:** Kokoro claims ~200MB footprint, but PyTorch MPS overhead varies—need Activity Monitor verification
3. **Voice Selection:** Which 2-3 voices to curate? (af_heart, am_echo, bf_emma are candidates)

### Known Risks

| Risk | Mitigation | Status |
|------|------------|--------|
| MPS incompatibility | CPU fallback logic | Planned for Phase 1 |
| Memory pressure on 8GB | Lazy loading, LRU cache | Planned for Phase 4 |
| Voice quality subjective | A/B test with ElevenLabs samples | Planned for Phase 3 |

---

## Blockers

**None currently.**

Project is ready to proceed with Phase 1 planning.

---

## Recent Activity

| Date | Activity | Notes |
|------|----------|-------|
| 2025-03-06 | Project initialized | PROJECT.md created |
| 2025-03-06 | Requirements defined | 16 v1 requirements documented |
| 2025-03-06 | Research completed | Kokoro/FastAPI stack validated |
| 2025-03-06 | Roadmap created | 4 phases covering all requirements |

---

## Session Continuity

**For Next Session:**

1. Run `/gsd-plan-phase 1` to create detailed plan for Core TTS Engine phase
2. Review Phase 1 success criteria before planning
3. Verify M1 hardware availability for testing

**Key Files:**
- `.planning/PROJECT.md` - Project definition
- `.planning/REQUIREMENTS.md` - v1 requirements (16 total)
- `.planning/ROADMAP.md` - Phase structure and success criteria
- `.planning/research/SUMMARY.md` - Stack validation and recommendations

---

## Notes

- **Research Confidence:** HIGH - Kokoro stack is well-documented for M1
- **Phase 1 Critical Path:** Model loading → TTS service → Basic inference
- **Target RTF:** 50x real-time (1 second of audio in 0.02 seconds)
- **Quality Gate:** Phase 3 includes subjective voice quality validation

---

*State file: Keep updated as project progresses*
