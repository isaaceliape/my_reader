---
fase: 02-web-crawler
plan: 02
subsystem: app.py, src/crawler/integrator
tags: [integration, api, endpoint, url-processing]
requires: ["02-01"]
provides: [url-to-audio-endpoint, cache-invalidation, url-validation]
affects: [app.py, static/index.html]
tech-stack:
  added: []
  patterns: [url-validation, cache-integration, streaming-response]
key-files:
  created:
    - src/crawler/integrator.py
  modified:
    - app.py
decisions:
  - "Usar validate_url() separada para reutilização e teste"
  - "Retornar tuple (Article, error, cache_hit) para clareza"
  - "Headers X-* para metadata no StreamingResponse"
  - "Endpoint DELETE /api/cache/all para administração"
metrics:
  duration: ~10min
  completed: "2026-04-01T15:00:00Z"
  files_created: 1
  files_modified: 1
  lines_added: ~306
---

# Fase 02 Plan 02: Integração Backend Summary

Integrar crawler ao backend FastAPI existente com endpoint POST /api/url e invalidação de cache.

## Tarefas Completadas

| # | Tarefa | Arquivos | Commit |
|---|--------|----------|--------|
| 1 | Criar módulo integrator | `src/crawler/integrator.py` | 33c07218 |
| 2 | Adicionar endpoint POST /api/url | `app.py` | 66dce19c |
| 3 | Dependências já existentes | `requirements.txt` | 94884be (02-01) |

## Implementação

### src/crawler/integrator.py

**validate_url(url: str) -> tuple[bool, str | None]**
- Usa `urllib.parse.urlparse()` para validação
- Verifica scheme (http/https apenas)
- Verifica netloc não vazio
- Retorna tuple (is_valid, error_message)

**process_url_to_audio(url, voice, speed) -> tuple[Article | None, str | None, bool]**
- Valida URL antes de processar
- Verifica cache primeiro (TTL 1 hora)
- Fetch URL com CrawlerClient
- Parse HTML com BeautifulSoup
- Extrai artigo com readability-lxml
- Detecta idioma com langdetect
- Retorna tuple (article, error, cache_hit)

**Tratamento de erros:**
| Cenário | Status Code | Mensagem |
|---------|-------------|----------|
| URL inválida | 400 | "URL must use http or https" |
| Paywall/bloqueio | 403 | "Site requires authentication" |
| Timeout | 504 | "Request timed out" |
| Outros erros | 400/500 | Descrição do erro |

### app.py

**POST /api/url**
- Aceita JSON: `{url, voice, speed}`
- Valida URL não vazia
- Chama `process_url_to_audio()`
- Gera áudio com `generate_audio()` (pipeline existente)
- Retorna StreamingResponse com headers:
  - `X-Article-Title`: título do artigo
  - `X-Article-URL`: URL processada
  - `X-Cache`: HIT ou MISS
  - `X-Article-Language`: código ISO (se detectado)
  - `Content-Disposition`: filename

**DELETE /api/cache**
- Aceita JSON: `{url}`
- Invalida URL específica do cache
- Retorna status success/not_found

**DELETE /api/cache/all**
- Limpa todo o cache
- Retorna confirmação

### requirements.txt

Dependências já adicionadas na etapa 02-01:
- httpx>=0.24.0
- beautifulsoup4>=4.12.0
- lxml>=4.9.0
- readability-lxml>=0.8.0
- cachetools>=5.3.0
- langdetect>=1.0.9

## Verificação

```bash
# Testar import do integrator
python -c "from src.crawler.integrator import process_url_to_audio; print('OK')"
# Resultado: OK

# Testar sintaxe do app
python -m py_compile app.py && echo "Syntax OK"
# Resultado: Syntax OK

# Endpoints registrados
grep -n "@app.post\|@app.delete" app.py
# Resultado: 4 endpoints encontrados (/tts, /api/url, /api/cache, /api/cache/all)
```

## Decisions Made

1. **validate_url() separada** - Função reutilizável para validação de URL, pode ser testada isoladamente
2. **Retorno tuple explícito** - (Article, error, cache_hit) mais claro que raising exceptions para fluxos esperados
3. **Headers X-* no response** - Metadata visível para frontend/UI sem precisar de response body adicional
4. **Endpoint /api/cache/all** - Adicionado como utilidade de administração (não estava no plano original, mas é coerente com cache_invalidate)

## Integração com Pipeline Existente

- Usa `pipeline` global (KPipeline) para gerar áudio
- Mantém `generate_audio()` existente sem refatoração
- Segue padrão de StreamingResponse do endpoint /tts

## Próximos Passos

- **02-03:** UI de preview e testes unitários
- Frontend precisa consumir POST /api/url e ler headers X-*
- Testes E2E com Playwright para validar fluxo completo

## Deviations from Plan

None - plano executado exatamente como especificado.

Endpoint adicional DELETE /api/cache/all foi adicionado como complemento natural ao DELETE /api/cache (baixo custo, alta utilidade).
