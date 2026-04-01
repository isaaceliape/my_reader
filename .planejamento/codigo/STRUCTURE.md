# Codebase Structure

**Data de Análise:** 2026-04-01

## Directory Layout

```
my_reader/
├── app.py                  # Main FastAPI application (backend)
├── requirements.txt        # Python dependencies
├── package.json            # Node.js dependencies (testes apenas)
├── README.md               # Documentation
├── .gitignore              # Git ignore rules
├── static/                 # Frontend assets
│   └── index.html          # Single-page application
├── .planejamento/          # FASE planning directory
│   └── codigo/             # Generated analysis documents
├── .opencode/              # Opencode AI tool config
├── .planning/              # Legacy planning directory
├── venv/                   # Python virtual environment (gitignored)
├── node_modules/           # Node.js dependencies (gitignored)
└── test-*.py/js            # Test files
```

## Directory Purposes

**Root (`/`):**
- Propósito: Main application code e configuration
- Contains: `app.py`, dependency files, test scripts
- Key files: `app.py`, `requirements.txt`, `package.json`

**static/:**
- Propósito: Frontend web assets servidos pelo FastAPI
- Contains: HTML, CSS (inline), JavaScript (inline)
- Key files: `static/index.html`

**.planejamento/codigo/:**
- Propósito: Documentos de análise FASE
- Contains: ARQUITETURA.md, STRUCTURE.md, etc.
- Key files: Generated analysis documents

**.opencode/:**
- Propósito: Configuração do Opencode AI assistant
- Contains: Settings, agents, manifests
- Key files: `.opencode/settings.json`, `.opencode/opencode.json`

**venv/:**
- Propósito: Python virtual environment
- Contains: Installed packages, binaries
- Committed: Não (gitignored)

## Key File Locations

**Entry Points:**
- `app.py`: Backend FastAPI application -主入口
- `static/index.html`: Frontend single-page app

**Configuration:**
- `requirements.txt`: Python dependencies (kokoro, fastapi, uvicorn, soundfile, numpy)
- `package.json`: Node.js dependencies (Playwright tests)
- `.gitignore`: Git ignore patterns

**Core Logic:**
- `app.py:51-119`: TTS pipeline loading e audio generation
- `app.py:121-202`: API endpoints

**Testing:**
- `test_app.spec.js`: E2E tests com Playwright
- `test_kokoro.py`, `test_kokoro2.py`, `test_kokoro3.py`: TTS integration tests

## Naming Conventions

**Arquivos:**
- Python: `snake_case.py` (e.g., `app.py`, `test_kokoro.py`)
- JavaScript: `kebab-case.spec.js` (e.g., `test_app.spec.js`)
- HTML: `index.html`

**Funções:**
- Python: `snake_case` (e.g., `generate_audio()`, `load_kokoro_pipeline()`)
- JavaScript: `camelCase` (e.g., `checkStatus()`, `setLoading()`)

**Variáveis:**
- Python: `snake_case` (e.g., `audio_segments`, `sample_rate`)
- JavaScript: `camelCase` (e.g., `lastGeneratedBlob`, `audioElement`)

**Endpoints:**
- RESTful kebab-case: `/api`, `/voices`, `/tts`

## Onde Adicionar Novo Código

**Nova Feature (Backend):**
- Código primário: `app.py` (adicionar novas rotas/funções)
- Dependencies: `requirements.txt`
- Tests: `test_*.py` ou `test_app.spec.js`

**Novo Componente Frontend:**
- Implementation: `static/index.html` (atualmente single-file)
- Para projetos maiores: Considere separar em `static/js/` e `static/css/`

**Utilities:**
- Shared helpers: `app.py` (funções no módulo principal)
- Para projetos maiores: Considere `utils/` directory

**Novos Endpoints API:**
- Location: `app.py` após imports, antes de `if __name__`
- Pattern: Decorator `@app.get()` ou `@app.post()`
- Response models: Pydantic models (se necessário)

## Special Directories

**static/:**
- Propósito: Web assets servidos via `StaticFiles`
- Generated: Não
- Committed: Sim
- Mount path: `/static` em `app.py:44`

**test-results/:**
- Propósito: Output de testes Playwright
- Generated: Sim (auto-generated)
- Committed: Provavelmente não (verificar .gitignore)
- Contains: `.last-run.json`, screenshots, videos

**venv/:**
- Propósito: Python virtual environment
- Generated: Sim (`python -m venv venv`)
- Committed: Não
- Contains: Python packages, binaries

**node_modules/:**
- Propósito: Node.js dependencies
- Generated: Sim (`npm install`)
- Committed: Não
- Contains: @playwright/test e dependencies

## Module Structure

**app.py:**
```
Lines 1-20:   Imports e dependencies
Lines 21-30:  Logging config e FastAPI init
Lines 32-45:  Middleware (CORS) e static files
Lines 48-79:  TTS pipeline initialization
Lines 81-119: Audio generation logic
Lines 121-124: Startup event
Lines 127-202: API endpoints
Lines 203-207: Main entry point
```

**static/index.html:**
```
Lines 1-218:  HTML structure e CSS styles
Lines 219-277: UI elements (forms, buttons, audio player)
Lines 278-412: JavaScript application logic
```

## File Size Overview

| File | Lines | Purpose |
|------|-------|---------|
| `app.py` | 208 | Backend completo |
| `static/index.html` | 412 | Frontend single-page app |
| `test_app.spec.js` | 69 | E2E tests |
| `test_kokoro*.py` | 13-17 | TTS integration tests |
| `requirements.txt` | 10 | Python dependencies |

---

*Structure analysis: 2026-04-01*
