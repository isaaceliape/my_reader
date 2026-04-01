# Technology Stack

**Data de Análise:** 2026-04-01

## Languages

**Primária:**
- Python 3.x - Backend API e TTS processing (`app.py`, scripts de teste)
- JavaScript - Frontend (`static/index.html`) e testes E2E (`test_app.spec.js`)

**Secundária:**
- HTML5/CSS3 - UI do frontend (`static/index.html`)

## Runtime

**Environment:**
- Python 3.x (venv detected em `/venv/`)
- Node.js (para testes Playwright)

**Package Manager:**
- pip - Python dependencies
- npm - Node.js dependencies
- Lockfiles: `requirements.txt` (pip), `package-lock.json` (npm) presentes

## Frameworks

**Core:**
- FastAPI >=0.109.0 - Web framework para API backend (`app.py`)
- Uvicorn >=0.27.0 - ASGI server para rodar FastAPI

**Testing:**
- Playwright >=1.59.0 - Testes E2E para browser automation (`test_app.spec.js`)

**ML/AI:**
- Kokoro >=0.7.11 - Text-to-Speech model (core do produto)
- PyTorch (`torch`) - Inferência do modelo TTS com suporte a MPS (Metal Performance Shaders) para M1

**Build/Dev:**
- Venv - Python virtual environment

## Key Dependencies

**Críticas:**
- `kokoro>=0.7.11` - Modelo TTS que roda localmente, coração da aplicação
- `torch` - Runtime para inferência do modelo Kokoro com aceleração GPU via MPS
- `fastapi>=0.109.0` - Framework web para API endpoints
- `uvicorn[standard]>=0.27.0` - Servidor ASGI para produção

**Infraestrutura:**
- `soundfile>=0.12.1` - Leitura/escrita de arquivos de áudio (WAV output)
- `numpy>=1.24.0` - Processamento de arrays de áudio
- `@playwright/test>=1.59.0` - Framework de testes E2E

## Configuration

**Environment:**
- Sem arquivos `.env` detectados
- Configuração via código em `app.py`
- Servidor roda em `0.0.0.0:8000` (todas interfaces)

**Build:**
- Sem sistema de build complexo - aplicação roda diretamente com `python app.py`
- Frontend é HTML estático servido pelo FastAPI (`/static`)

## Platform Requirements

**Development:**
- macOS com Apple Silicon (M1/M2) recomendado para aceleração MPS
- Python 3.x com virtual environment
- Node.js para testes Playwright

**Production:**
- Deployment local ou em servidor com GPU compatível com PyTorch
- Preferencialmente macOS com MPS ou Linux com CUDA

## Architecture Notes

**Frontend:**
- Single Page Application (SPA) simples
- HTML + CSS + JavaScript vanilla (sem frameworks)
- Fetch API para comunicação com backend
- Arquivo único: `static/index.html`

**Backend:**
- FastAPI com endpoints REST
- TTS pipeline carregado uma vez no startup (`@app.on_event("startup")`)
- Geração de áudio em WAV stream via `StreamingResponse`
- CORS habilitado para todas origens (desenvolvimento)

**Hardware Optimization:**
- Detecção automática de dispositivo: MPS > CUDA > CPU
- Otimizado para MacBook Air M1 (documentado no código)

---

*Stack analysis: 2026-04-01*
