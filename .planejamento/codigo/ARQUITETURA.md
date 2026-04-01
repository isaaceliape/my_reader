# Architecture

**Data de Análise:** 2026-04-01

## Pattern Overview

**Overall:** Monolithic Web Application com separação Backend/Frontend

**Key Characteristics:**
- Backend FastAPI servindo API REST e static files
- Frontend single-page HTML/JS sem build step
- TTS processing síncrono via Kokoro ML pipeline
- Execução 100% local (M1 Mac optimized)

## Layers

**Backend API Layer:**
- Propósito: Expor endpoints TTS e servir frontend
- Location: `app.py`
- Contains: Rotas API, TTS pipeline initialization, audio generation
- Depends on: Kokoro TTS, FastAPI, soundfile, numpy
- Used by: Frontend JavaScript via fetch API

**Frontend Presentation Layer:**
- Propósito: Interface de usuário para controle TTS
- Location: `static/index.html`
- Contains: HTML structure, inline CSS, vanilla JavaScript
- Depends on: Backend API endpoints
- Used by: End users via browser

**ML/TTS Engine:**
- Propósito: Geração de áudio a partir de texto
- Location: External package (kokoro)
- Contains: KPipeline com modelos de voz
- Depends on: PyTorch (MPS/CUDA/CPU)
- Used by: `app.py` via `generate_audio()` function

## Data Flow

**TTS Generation Flow:**

1. User digita texto no frontend (`static/index.html:278-412`)
2. Frontend envia POST para `/tts` com `{text, voice, speed}`
3. Backend valida input (max 5000 chars) em `app.py:162-202`
4. `generate_audio()` chama Kokoro pipeline em `app.py:81-119`
5. Kokoro retorna generator de Results com audio tensors
6. Audio segments concatenados com numpy em `app.py:97-108`
7. WAV encoding via soundfile em buffer memory em `app.py:111-114`
8. StreamingResponse retorna audio/wav stream em `app.py:189-197`
9. Frontend cria blob URL e toca em `audio` element em `static/index.html:351-367`

**Startup Flow:**

1. `uvicorn.run()` inicia servidor em `app.py:207`
2. `@app.on_event("startup")` carrega modelo TTS em `app.py:121-124`
3. `load_kokoro_pipeline()` detecta device (MPS/CUDA/CPU) em `app.py:64-79`
4. KPipeline instanciado uma vez, reutilizado globalmente em `app.py:48`

**State Management:**
- Global `pipeline` variable em `app.py:48` singleton pattern
- Frontend state em variáveis locais do script (`lastGeneratedBlob`)
- Sem database ou persistência

## Key Abstractions

**TTS Pipeline:**
- Propósito: Wrapper para Kokoro text-to-speech
- Examples: `app.py:48`, `app.py:64-79`
- Pattern: Singleton lazy initialization

**Audio Generation Function:**
- Propósito: Encapsula lógica de síntese audio
- Examples: `app.py:81-119`
- Pattern: Pure function com global dependency injection

**API Endpoints:**
- Propósito: REST interface para operações TTS
- Examples: `app.py:127-202`
- Pattern: FastAPI decorator-based routing

## Entry Points

**Main Application:**
- Location: `app.py:203-207`
- Triggers: `python app.py` ou `uvicorn app:app`
- Responsibilities: Inicializa FastAPI, carrega TTS model, inicia servidor

**Static File Server:**
- Location: `app.py:41-45`
- Triggers: Requests para `/static/*`
- Responsibilities: Serve `index.html` e assets frontend

**API Routes:**
- Location: `app.py:127-202`
- Triggers: HTTP requests
- Responsibilities:
  - `GET /`: Serve frontend ou status JSON
  - `GET /api`: Health check
  - `GET /voices`: Lista vozes disponíveis
  - `POST /tts`: Gera áudio TTS

## Error Handling

**Estratégia:** HTTPException para erros de API, logging para debugging

**Patterns:**
- Input validation retorna HTTP 400 em `app.py:166-170`
- TTS errors logged e retornam HTTP 500 em `app.py:198-201`
- Frontend exibe errors em UI via `showError()` em `static/index.html:393-397`
- Startup failures logged mas não crasham em `app.py:72-78`

## Cross-Cutting Concerns

**Logging:**
- Approach: Python logging module com INFO level
- Location: `app.py:21-23`
- Usage: Startup, device detection, TTS generation, errors

**Validation:**
- Approach: Manual validation nos endpoints
- Location: `app.py:166-170`
- Rules: Text required, max 5000 chars, speed range 0.5-2.0

**Authentication:**
- Approach: Nenhuma (aplicação local)
- Location: N/A

**CORS:**
- Approach: Allow all origins para desenvolvimento local
- Location: `app.py:32-39`
- Config: `allow_origins=["*"]`

**Audio Format:**
- Approach: WAV format em memory buffer
- Location: `app.py:111-114`
- Sample rate: 24kHz (Kokoro native)

---

*Architecture analysis: 2026-04-01*
