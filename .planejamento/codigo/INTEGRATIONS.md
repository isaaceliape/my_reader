# External Integrations

**Data de Análise:** 2026-04-01

## APIs & External Services

**Nenhuma integração externa detectada:**
- A aplicação foi projetada para rodar 100% localmente
- Sem chamadas a APIs externas
- Sem dependência de serviços cloud

## Data Storage

**Databases:**
- Nenhuma - Aplicação stateless, sem persistência

**File Storage:**
- Sistema de arquivos local apenas
- Frontend estático em `static/`
- Áudio gerado é stream em memória (não persiste em disco)

**Caching:**
- Nenhum sistema de caching implementado
- Kokoro TTS pipeline é carregado uma vez em memória no startup

## Authentication & Identity

**Auth Provider:**
- Nenhum - Aplicação não requer autenticação
- Endpoints abertos para acesso local

**Session Management:**
- Sem sessions - API stateless

## Monitoring & Observability

**Error Tracking:**
- Nenhum serviço externo
- Logging via Python `logging` module (console output)
- Logs configurados em `app.py` linha 22-23: `logging.basicConfig(level=logging.INFO)`

**Logs:**
- Console logging apenas
- Níveis: INFO para operações normais, ERROR para falhas
- Sem agregação ou forwarding de logs

## CI/CD & Deployment

**Hosting:**
- Aplicação local (localhost:8000)
- Sem plataforma de hosting configurada

**CI Pipeline:**
- Nenhum detectado
- Testes Playwright rodam localmente

**Version Control:**
- Git repository: `https://github.com/isaaceliape/my_reader`

## Environment Configuration

**Required env vars:**
- Nenhuma variável de ambiente requerida
- Configuração hardcoded em `app.py`:
  - `PORT=8000` (hardcoded no main)
  - `HOST=0.0.0.0` (todas interfaces)
  - `CORS_ORIGINS=["*"]` (desenvolvimento)

**Secrets location:**
- Sem secrets - aplicação não usa APIs pagas ou serviços externos

## Webhooks & Callbacks

**Incoming:**
- Nenhum webhook configurado

**Outgoing:**
- Nenhuma chamada outbound para serviços externos

## Third-Party SDKs

**Kokoro TTS:**
- Package Python: `kokoro>=0.7.11`
- SDK: `KPipeline` class importada de `kokoro`
- Uso: `pipeline = KPipeline(lang_code='a', device=device)` em `app.py` linha 74
- Executa localmente - não faz chamadas de rede

**PyTorch:**
- Framework de ML para inferência do modelo
- Suporte MPS (Metal Performance Shaders) para Apple Silicon
- Device detection em `app.py` linhas 51-62

## Audio Output

**Format:**
- WAV (24kHz sample rate)
- Gerado em memória via `io.BytesIO()`
- Streamed via FastAPI `StreamingResponse`

**Playback:**
- Frontend usa HTML5 `<audio>` element
- Blob URL criado via `URL.createObjectURL()`
- Sem upload para serviços de storage

## Key Integration Points (Internal)

| Component | Integration | Purpose |
|-----------|-------------|---------|
| `app.py` | Kokoro `KPipeline` | TTS inference |
| `app.py` | PyTorch | Model runtime |
| `app.py` | SoundFile | WAV encoding |
| `static/index.html` | `/api` endpoint | Health check |
| `static/index.html` | `/tts` endpoint | Audio generation |
| `static/index.html` | `/voices` endpoint | Voice list |
| `test_app.spec.js` | Playwright | E2E testing |

---

*Integration audit: 2026-04-01*
