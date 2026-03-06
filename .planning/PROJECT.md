# Local TTS Web App

## What This Is

A simple web application that runs locally on a MacBook Air M1 (2020), allowing the user to paste text into a textarea and generate high-quality text-to-speech audio. The interface includes a text input, play button, and audio player.

## Core Value

Type or paste any text and hear it spoken with natural, ElevenLabs-quality voice synthesis - all running locally without cloud dependencies.

## Requirements

### Validated

(None yet — ship to validate)

### Active

- [ ] Simple web interface with textarea input
- [ ] "Play" button to generate audio from text
- [ ] Built-in audio player to play generated audio
- [ ] 2-3 natural, high-quality voices to choose from
- [ ] Runs entirely locally on MacBook Air M1 (2020)
- [ ] Handles mixed content length (short snippets to long articles)
- [ ] Open source TTS engine with very high quality output

### Out of Scope

- Network accessibility - Local only, not exposed to other devices
- Voice cloning/custom voice creation - Use pre-trained voices only
- Real-time streaming audio - Generate then play
- Cloud APIs (ElevenLabs, etc.) - Must be fully local
- Mobile app or desktop native app - Web interface only
- Multiple languages in v1 - English first
- Audio file export/saving - Playback only in v1
- Voice speed/pitch adjustment - Keep it simple

## Context

**Motivation:** Exploring TTS technology and building a practical local tool.

**Hardware constraints:** MacBook Air M1 (2020) - 8GB or 16GB unified memory. TTS model must run efficiently without exceeding memory or taking too long to generate.

**Quality target:** ElevenLabs-level natural speech. This guides the TTS engine choice toward modern neural models like Kokoro or MeloTTS rather than older alternatives.

**TTS Engine Research:**
- **Kokoro TTS** (preferred): Very high quality, fast on M1, ONNX-based for efficiency
- **MeloTTS**: Good quality, multilingual, PyTorch-based
- **Piper TTS**: Fast, good quality, but slightly less natural than Kokoro

Given quality requirements, Kokoro is the primary candidate.

## Constraints

- **Tech stack:** Python backend (TTS engines are Python-based) + simple HTML/JS frontend
- **Hardware:** Must run smoothly on MacBook Air M1 (2020) with 8-16GB RAM
- **Quality:** Voice must sound natural, not robotic - near-human quality
- **Privacy:** All processing local, no data sent to cloud
- **Simplicity:** Single-purpose tool, minimal features beyond core TTS

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Web interface vs desktop app | Simpler to build, easier to iterate, cross-platform potential | — Pending |
| Kokoro TTS as primary engine | Best quality-to-speed ratio for M1, open source, ONNX optimized for Apple Silicon | — Pending |
| Local only (no network) | Simpler deployment, no security concerns, matches use case | — Pending |
| 2-3 pre-trained voices | Quality over quantity, keeps download size reasonable | — Pending |

---
*Last updated: 2025-03-06 after initialization*
