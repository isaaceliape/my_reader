# Testing Patterns

**Data de Análise:** 2026-04-01

## Test Framework

**E2E Testing:**
- Runner: Playwright Test `@playwright/test` v1.59.0
- Config: Inline no arquivo de teste (sem config file dedicado)
- Assertion Library: Playwright assertions (`expect()`)

**Python Scripts (Exploratórios):**
- Runner: Python direto (sem framework de teste)
- Files: `test_kokoro.py`, `test_kokoro2.py`, `test_kokoro3.py`
- Propósito: Explorar API da Kokoro, não testes automatizados

**Run Commands:**
```bash
# Run Playwright tests (manual)
npx playwright test test_app.spec.js

# Run Python test scripts
python test_kokoro.py
python test_kokoro2.py
python test_kokoro3.py
```

## Test File Organization

**Location:**
- Root directory (co-located com código principal)
- Padrão: `test_*.py` para scripts Python
- Padrão: `*_test.spec.js` ou `test_*.spec.js` para Playwright

**Naming:**
- Python: `test_<component>.py` - Ex: `test_kokoro.py`, `test_app.py` (futuro)
- JavaScript: `test_<app>.spec.js` - Ex: `test_app.spec.js`

**Structure:**
```
my_reader/
├── app.py                    # Main application
├── test_app.spec.js          # E2E tests (Playwright)
├── test_kokoro.py            # Python exploratory script
├── test_kokoro2.py           # Python exploratory script
├── test_kokoro3.py           # Python exploratory script
└── test-results/             # Playwright results output
```

## Test Structure

**Playwright Suite Organization (`test_app.spec.js`):**
```javascript
const { test, expect } = require('@playwright/test');

test.describe('my_reader TTS App', () => {
    test('app loads successfully', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000');
        
        // Check page title
        await expect(page).toHaveTitle(/Local TTS/);
        
        // Check main elements exist
        await expect(page.locator('h1')).toContainText('Local TTS');
        await expect(page.locator('#textInput')).toBeVisible();
        
        console.log('✓ App loads successfully');
    });

    test('status shows TTS ready', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000');
        
        // Wait for status to load
        await page.waitForSelector('#status');
        const status = await page.locator('#status').textContent();
        
        // Should show "TTS Ready" or similar ok status
        expect(status).toContain('Ready');
        console.log('✓ TTS status:', status);
    });
});
```

**Patterns:**
- `test.describe()` para agrupar testes por feature
- `test()` para testes individuais
- `async/await` para todas as operações async
- `console.log()` para output de debug
- Selectors por ID (`#textInput`) e tag (`h1`)

**Setup:**
- Nenhum setup global configurado
- Cada teste navega para URL base independentemente

**Teardown:**
- Automático (Playwright gerencia)
- Nenhum cleanup explícito necessário

**Assertion Pattern:**
```javascript
// Visibility checks
await expect(page.locator('#element')).toBeVisible();

// Text content checks
await expect(page.locator('h1')).toContainText('Local TTS');
const status = await page.locator('#status').textContent();
expect(status).toContain('Ready');

// Attribute checks
const audioSrc = await page.locator('#audioElement').getAttribute('src');
expect(audioSrc).toBeTruthy();
expect(audioSrc).toContain('blob:');

// JSON response checks
expect(json.voices).toBeDefined();
expect(json.voices.length).toBeGreaterThan(0);
expect(json.status).toBe('ok');
expect(json.tts_loaded).toBe(true);
```

## Mocking

**Framework:** Não configurado

**Patterns:**
- Nenhum mocking em uso atualmente
- Testes são E2E reais contra servidor local

**O que Mockar (Recomendações futuras):**
- APIs externas (se adicionar integrações)
- TTS generation para testes rápidos
- File system operations

**O que NÃO Mockar:**
- FastAPI endpoints (testar via HTTP real)
- Frontend-backend integration
- Audio blob generation

## Fixtures and Factories

**Test Data:**
```javascript
// Hardcoded test text
await page.fill('#textInput', 'Hello, this is a test of the local TTS system.');

// Default values
voice: 'af_heart'
speed: 1.0
```

**Location:**
- Inline nos testes (nenhum fixture file dedicado)

**Python exploratory scripts:**
```python
# test_kokoro2.py
text = "Hello, this is a test."
results = p(text, voice='af_heart', speed=1.0)
```

## Coverage

**Requirements:** Nenhum enforced

**View Coverage:**
```bash
# Python coverage (se adicionar pytest)
pytest --cov=app --cov-report=html

# Playwright coverage (não configurado)
# Requereria setup adicional
```

## Test Types

**Unit Tests:**
- Não implementados
- Scripts Python (`test_kokoro*.py`) são exploratórios, não unit tests formais

**Integration Tests:**
- Playwright E2E testa integração frontend-backend
- Testa HTTP endpoints, audio generation, UI updates

**E2E Tests:**
- Framework: Playwright
- Browser: Chromium (default)
- Tests em `test_app.spec.js`:
  - App loads successfully
  - Status shows TTS ready
  - Voices endpoint returns voices
  - Health endpoint works
  - Generate TTS audio

## Common Patterns

**Async Testing (Playwright):**
```javascript
test('generate TTS audio', async ({ page }) => {
    await page.goto('http://127.0.0.1:8000');
    
    // Fill form
    await page.fill('#textInput', 'Hello, this is a test.');
    
    // Click and wait
    await page.click('#playBtn');
    
    // Wait for async result (max 30 seconds)
    await page.waitForSelector('#audioPlayer.visible', { timeout: 30000 });
    
    // Assert result
    const audioSrc = await page.locator('#audioElement').getAttribute('src');
    expect(audioSrc).toBeTruthy();
});
```

**Error Testing:**
```javascript
// Implicit error handling via HTTP status
if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Generation failed');
}

// Python backend error testing (app.py)
if not text or not text.strip():
    raise HTTPException(status_code=400, detail="Text is required")

if len(text) > 5000:
    raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
```

**API Response Testing:**
```javascript
// Test /voices endpoint
test('voices endpoint returns voices', async ({ page }) => {
    const response = await page.goto('http://127.0.0.1:8000/voices');
    const json = await response.json();
    
    expect(json.voices).toBeDefined();
    expect(json.voices.length).toBeGreaterThan(0);
    console.log('✓ Voices endpoint:', json.voices.length, 'voices available');
});

// Test /api health endpoint
test('health endpoint works', async ({ page }) => {
    const response = await page.goto('http://127.0.0.1:8000/api');
    const json = await response.json();
    
    expect(json.status).toBe('ok');
    expect(json.tts_loaded).toBe(true);
});
```

## Test Results

**Output Directory:**
- `test-results/` - Playwright test artifacts

**Current Tests (5 total in `test_app.spec.js`):**
1. ✅ App loads successfully
2. ✅ Status shows TTS ready
3. ✅ Voices endpoint returns voices
4. ✅ Health endpoint works
5. ✅ Generate TTS audio

---

*Testing analysis: 2026-04-01*
