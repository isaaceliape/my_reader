# Coding Conventions

**Data de Análise:** 2026-04-01

## Naming Patterns

**Arquivos Python:**
- `snake_case.py` - Ex: `app.py`, `test_kokoro.py`
- Test files prefixados com `test_`

**Arquivos JavaScript:**
- `snake_case.spec.js` para testes - Ex: `test_app.spec.js`
- `index.html` para frontend principal

**Funções Python:**
- `snake_case` com type hints - Ex: `def get_device():`, `def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes:`
- Docstrings opcionais inline

**Funções JavaScript:**
- `camelCase` - Ex: `checkStatus()`, `setLoading()`, `showError()`

**Variáveis:**
- Python: `snake_case` - Ex: `audio_segments`, `sample_rate`, `pipeline`
- JavaScript: `camelCase` - Ex: `lastGeneratedBlob`, `audioElement`, `textInput`

**Classes:**
- `PascalCase` - Ex: `KPipeline`, `FastAPI`, `HTTPException`

**Componentes HTML/CSS:**
- Classes CSS: `kebab-case` - Ex: `.audio-player`, `.button-group`, `.control-group`
- IDs HTML: `camelCase` - Ex: `id="textInput"`, `id="voiceSelect"`, `id="playBtn"`

## Code Style

**Formatting:**
- Tool: Nenhuma configurada (sem `.prettierrc`, `.editorconfig`)
- Indentação Python: 4 espaços
- Indentação JavaScript: 4 espaços
- String quotes: Single quotes em Python (`'utf-8'`), single quotes em JavaScript (`'application/json'`)

**Linting:**
- Tool: Nenhuma configurada (sem `.eslintrc`, `pyproject.toml` com linting)
- Validação manual apenas

## Import Organization

**Python (`app.py`):**
1. Standard library (`io`, `os`, `logging`)
2. Third-party (`numpy`, `torch`, `soundfile`, `fastapi`, `kokoro`)
3. Local imports (inline quando necessário - Ex: `from fastapi.responses import FileResponse`)

**JavaScript:**
- Imports no topo do arquivo - Ex: `const { test, expect } = require('@playwright/test');`
- DOM elements agrupados por proximidade funcional

**Path Aliases:**
- Nenhum configurado

## Error Handling

**Python (`app.py`):**
```python
# HTTP errors com FastAPI
raise HTTPException(status_code=400, detail="Text is required")
raise HTTPException(status_code=500, detail=str(e))

# Runtime errors
if pipeline is None:
    raise RuntimeError("TTS pipeline not loaded")

# Try/except com logging
try:
    results = pipeline(text, voice=voice, speed=speed)
except Exception as e:
    logger.error(f"Audio generation failed: {e}")
    raise
```

**JavaScript (`index.html`):**
```javascript
// Try/catch com showError
try {
    const response = await fetch(...)
    if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Generation failed')
    }
} catch (error) {
    showError(error.message)
} finally {
    setLoading(false)
}
```

## Logging

**Framework:** `logging` (Python stdlib)

**Configuração (`app.py`):**
```python
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

**Patterns:**
- `logger.info()` para operações normais - Ex: `"Using MPS for GPU acceleration"`, `"Generating TTS: {len(text)} chars"`
- `logger.error()` para falhas - Ex: `"Failed to load Kokoro pipeline: {e}"`, `"TTS generation failed: {e}"`
- console.log() para debug de testes - Ex: `console.log('✓ App loads successfully')`

## Comments

**Quando Comentar:**
- Comments explicando decisões arquiteturais - Ex: `# Global TTS pipeline (loaded once at startup)`
- Comments explicando APIs externas - Ex: `# Kokoro pipeline is callable - returns a generator of Results`
- Comments de configuração - Ex: `# Enable CORS for local development`, `# Use English language model`

**JSDoc/TSDoc:**
- Não usado
- Docstrings Python inline quando necessário

## Function Design

**Size:**
- Funções pequenas e focadas (20-40 linhas)
- `app.py`: `get_device()` (10 linhas), `load_kokoro_pipeline()` (15 linhas), `generate_audio()` (38 linhas)

**Parameters:**
- Python: Type hints obrigatórios - Ex: `def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes:`
- Valores default quando apropriado - Ex: `speed: float = 1.0`, `voice: str = Body("af_heart")`

**Return Values:**
- Python: Type hints de retorno - Ex: `-> bytes:`, `-> bool:`, `-> StreamingResponse:`
- JavaScript: Retornos implícitos (Promises, DOM elements, valores)

## Module Design

**Exports (Python):**
- FastAPI app instance exportada implicitamente via `app = FastAPI(...)`
- Functions privadas por convenção (sem `__` prefix)

**Exports (JavaScript):**
- Module pattern não usado (script inline em HTML)
- `const` para todas as variáveis (imutabilidade preferida)

**Barrel Files:**
- Não aplicável (projeto small-scale)

## FastAPI Conventions (`app.py`)

**Route decorators:**
- `@app.get("/")` para GET endpoints
- `@app.post("/tts")` para POST endpoints
- `@app.on_event("startup")` para startup hooks

**Response types:**
- `StreamingResponse` para audio streams
- `JSONResponse` para JSON explícito
- Dict return para JSON implícito
- `FileResponse` para arquivos estáticos

**Request body:**
- `Body(...)` para required fields
- `Body(default)` para optional fields

---

*Convention analysis: 2026-04-01*
