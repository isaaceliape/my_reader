# Feature Research: Local TTS Web App

**Domain:** Local Text-to-Speech Web Applications
**Researched:** 2026-03-06
**Confidence:** MEDIUM (based on competitor analysis and market research)

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Text Input Area** | Core functionality - where users paste/type content | LOW | Essential UX element. Auto-resize, character count optional |
| **Voice Selection** | Users expect to choose different voices/personas | LOW | 2-3 curated voices sufficient for MVP |
| **Play/Pause Button** | Basic audio control | LOW | Standard HTML5 audio controls acceptable |
| **Speed Control** | Users expect 0.5x - 2x playback speed | MEDIUM | Critical for accessibility and productivity use cases |
| **Audio Player** | Progress bar, time display, scrubbing | LOW | Native browser audio element works well |
| **Audio Export (MP3/WAV)** | Users want to save audio files | MEDIUM | File generation + download API |
| **Voice Quality** | Modern TTS must sound natural, not robotic | HIGH | This is the core value proposition - requires high-quality local model |
| **Offline Operation** | For a "local" app, users expect no internet required | MEDIUM | All models must run locally, no cloud fallbacks |

### Differentiators (Competitive Advantage)

Features that set the product apart. Not required, but valuable.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Zero Setup Voice Synthesis** | Competitors require accounts, subscriptions, or complex setup | LOW | One-click launch, immediate use |
| **Privacy-First Architecture** | No data leaves the machine | LOW | Major differentiator vs cloud-based solutions |
| **Curated Small Voice Set** | Quality over quantity - each voice is excellent | MEDIUM | 2-3 exceptional voices > 100 mediocre ones |
| **Native macOS Integration** | Menu bar widget, global shortcuts | MEDIUM | System-level integration competitors lack |
| **Text Highlighting Sync** | Words highlighted as spoken | MEDIUM | Complex audio-text synchronization |
| **Voice Cloning (XTTS v2)** | Clone any voice from 6-second sample | HIGH | Coqui XTTS v2 enables this locally |
| **Batch Processing** | Convert multiple text files at once | MEDIUM | Queue management, progress tracking |
| **Keyboard Shortcuts** | Power-user efficiency | LOW | Global shortcuts for play/pause |
| **Apple Silicon Optimization** | Leverage M1 Neural Engine | HIGH | CoreML or MLX integration for speed |
| **Minimalist Interface** | No clutter, focused on the task | LOW | Single textarea, voice picker, play button |

### Anti-Features (Commonly Requested, Problematic)

Features that seem good but create problems.

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| **Cloud Sync/Account System** | "So I can access from anywhere" | Violates privacy-first, adds complexity, creates lock-in | Local file export/import for portability |
| **100+ Voice Library** | More choices seem better | Choice paralysis, quality variance, large download | Curate 2-3 exceptional voices |
| **Real-time Streaming** | Faster perceived response | Adds complexity, unnecessary for paste-and-play use case | Pre-generate audio, show progress |
| **Speech-to-Text (Dictation)** | "Full voice suite" | Scope creep, requires different models, different use case | Stay focused on TTS only |
| **Social Sharing** | "Share audio clips" | Privacy nightmare, viral feature creep | Manual file export for sharing |
| **Browser Extension** | "Read any webpage" | Maintenance burden, different product entirely | Focus on core web app experience |
| **Mobile Apps** | "iOS/Android support" | Different platform, different constraints, fragmented focus | Web app responsive design only |
| **Subscription Tiers** | Revenue model | Users hate subscriptions, especially for local software | One-time purchase or open source |
| **Collaborative Features** | "Share with team" | Adds cloud dependency, complexity, account systems | Export files, use existing collaboration tools |
| **AI Chat/Conversational** | "Like ChatGPT but voice" | Entirely different product category | Stay focused on text-to-speech |

## Feature Dependencies

```
[Core TTS Engine]
    │
    ├─requires──> [Voice Models] (2-3 curated)
    │                 │
    │                 └─requires──> [Model Storage/Loading]
    │
    ├─requires──> [Text Processing]
    │
    ├─enhances──> [Audio Export]
    │                 │
    │                 └─requires──> [File System Access]
    │
    └─enhances──> [Speed Control]
                      │
                      └─requires──> [Audio Processing]

[Voice Cloning]
    │
    ├─requires──> [Core TTS Engine]
    ├─requires──> [XTTS v2 Model]
    └─requires──> [Audio Input]
          │
          └─conflicts──> [Privacy Guarantee] (if not local)

[Native Integration]
    │
    ├─requires──> [macOS App Wrapper]
    └─conflicts──> [Cross-Platform Compatibility]
```

### Dependency Notes

- **Voice Models requires Model Storage:** High-quality voices are 100MB-1GB each; need efficient lazy loading
- **Audio Export requires File System:** Browser download API sufficient; no server-side storage needed
- **Voice Cloning conflicts with Privacy:** Must process locally; never upload samples to cloud
- **Native Integration conflicts with Cross-Platform:** Prioritize macOS native features over portability

## MVP Definition

### Launch With (v1)

Minimum viable product - what's needed to validate the concept.

- [x] **Simple Web Interface** — Textarea, voice dropdown, play button, audio player
- [x] **2-3 High-Quality Voices** — Curated, natural-sounding, distinct personas
- [x] **Basic Speed Control** — 0.75x, 1x, 1.25x, 1.5x options
- [x] **MP3 Export** — Download generated audio
- [x] **Offline Operation** — All processing local, no cloud dependency
- [x] **macOS Native Wrapper** — Electron or Tauri for native feel
- [x] **Keyboard Shortcuts** — Cmd+Enter to play, Space to pause

### Add After Validation (v1.x)

Features to add once core is working.

- [ ] **Word Highlighting** — Sync text highlighting with audio playback
- [ ] **Voice Cloning** — Local XTTS v2 integration for custom voices
- [ ] **Batch Processing** — Queue multiple files for conversion
- [ ] **History** — Recent conversions, searchable
- [ ] **Apple Silicon Optimization** — CoreML acceleration for faster synthesis
- [ ] **Menu Bar Widget** — Quick access from macOS menu bar

### Future Consideration (v2+)

Features to defer until product-market fit is established.

- [ ] **Plugin System** — Allow third-party voice models
- [ ] **SSML Support** — Advanced speech markup for prosody control
- [ ] **Multi-language Voices** — Beyond English
- [ ] **Audio Effects** — Reverb, EQ, background noise
- [ ] **Integration APIs** — Local HTTP API for other apps to use

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Text Input Area | HIGH | LOW | P1 |
| Voice Selection (2-3) | HIGH | LOW | P1 |
| Play/Pause Controls | HIGH | LOW | P1 |
| Offline Operation | HIGH | MEDIUM | P1 |
| MP3 Export | HIGH | MEDIUM | P1 |
| Speed Control | MEDIUM | MEDIUM | P1 |
| Word Highlighting | MEDIUM | HIGH | P2 |
| Voice Cloning | HIGH | HIGH | P2 |
| Keyboard Shortcuts | MEDIUM | LOW | P2 |
| Batch Processing | LOW | MEDIUM | P2 |
| Apple Silicon Optimization | MEDIUM | HIGH | P2 |
| Menu Bar Widget | LOW | MEDIUM | P3 |
| History/Recent | LOW | LOW | P3 |
| SSML Support | LOW | HIGH | P3 |
| Multi-language | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when core stable
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | ElevenLabs | NaturalReader | Speechify | Murf AI | Our Approach |
|---------|------------|---------------|-----------|---------|--------------|
| **Pricing Model** | Subscription | Freemium | Subscription | Subscription | Free/Open Source |
| **Voice Count** | 10,000+ | 200+ | 1,000+ | 200+ | 2-3 curated |
| **Local/Offline** | ❌ Cloud only | ❌ Cloud only | ⚠️ Partial | ❌ Cloud only | ✅ 100% local |
| **Voice Cloning** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes (XTTS v2) |
| **Setup Complexity** | Account required | Account required | Account required | Account required | None (launch & use) |
| **Speed Control** | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Yes |
| **Export Formats** | MP3 | MP3 | MP3 | MP3/WAV | MP3 |
| **Privacy** | ❌ Cloud processing | ❌ Cloud processing | ❌ Cloud processing | ❌ Cloud processing | ✅ On-device only |
| **Mac Native** | Web only | Web+App | Web+App | Web only | ✅ Native wrapper |
| **Code Open Source** | ❌ Proprietary | ❌ Proprietary | ❌ Proprietary | ❌ Proprietary | ✅ Open source |

## Key Differentiation Strategy

**Our Competitive Moat:**

1. **Privacy-First by Design** — Unlike all major competitors, we process 100% locally. No accounts, no cloud, no data leaving the machine.

2. **Zero-Friction UX** — Open app, paste text, press play. No signup, no subscription, no "connect to internet" requirements.

3. **Quality over Quantity** — 2-3 exceptional voices beat 10,000 mediocre ones. Curated selection reduces choice paralysis.

4. **Developer-Friendly** — Open source means extensible, auditable, and community-improvable.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Core Features | HIGH | Standard TTS functionality well-documented |
| Voice Quality | MEDIUM | Depends on XTTS v2/Piper model selection |
| Local Performance | MEDIUM | M1 optimization needs testing |
| Market Differentiation | HIGH | Clear gap in privacy-focused local TTS |
| Technical Feasibility | HIGH | Coqui TTS and XTTS proven locally |

## Sources

- ElevenLabs (https://elevenlabs.io) — Market leader in cloud TTS, extensive voice library
- NaturalReader (https://www.naturalreaders.com) — Accessibility-focused TTS with personal/commercial tiers
- Speechify (https://speechify.com) — AI assistant approach with dictation and podcasts
- Murf AI (https://murf.ai) — Enterprise-focused with 200+ voices, API offerings
- Coqui TTS (https://github.com/coqui-ai/TTS) — Open source local TTS toolkit, XTTS v2 for voice cloning
- Jan (https://github.com/janhq/jan) — Reference for local-first AI app architecture
- Whisper (https://github.com/openai/whisper) — Reference for local AI model deployment patterns

---
*Feature research for: Local TTS Web App*
*Researched: 2026-03-06*
