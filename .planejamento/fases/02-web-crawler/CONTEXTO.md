# Fase 2: Web Crawler - Contexto de Decisões

**Criado:** 2026-04-01  
**Fase:** 02-web-crawler  
**Status:** PRONTO PARA EXECUÇÃO

---

## Decisões de Implementação

### 1. Extração de Conteúdo

**Decisão:** `readability-lxml` local + fallbacks

**Racional:** 
- Reader APIs gratuitas foram descontinuadas (Mercury, Google Reader)
- Diffbot é pago ($29/mo)
- readability-lxml é ativo, testado, roda local

**Fluxo:**
```
httpx fetch → readability-lxml → conteúdo limpo
                          ↓ (fallback se falhar)
              BeautifulSoup extrai <article>/<main>
                          ↓ (fallback se falhar)
                      Erro claro
```

**Tratamento de erros:**
| Cenário | Ação |
|---------|------|
| URL inválida (malformed) | Validação prévia com `urllib.parse` → HTTP 400 |
| Site inacessível (timeout/DNS) | Timeout httpx 30s → HTTP 500 |
| Paywall (403/redirect) | Detectar → HTTP 400 "Site requer autenticação" |
| readability falha | Fallback BeautifulSoup → erro se nada encontrado |

---

### 2. UX do Preview

**Decisão:** Preview simples, somente leitura

**Comportamento:**
- **Conteúdo:** Título + primeiras 200-300 palavras (com ellipsis se maior)
- **Editável:** Não (somente leitura)
- **Loading:** Progresso por etapa: "Buscando → Extraindo → Pronto"
- **Ações:** "Gerar Áudio" e "Nova URL"

**Estados da UI:**
```
[Input URL] → [Processar] → [Loading: "Buscando..."]
                          → [Loading: "Extraindo..."]
                          → [Preview: título + texto]
                          → [Botões: "Gerar Áudio" | "Nova URL"]
```

---

### 3. Cache Strategy

**Decisão:** TTL 24h + invalidação manual + LRU 1000 items

**Configuração:**
```python
from cachetools import TTLCache
url_cache = TTLCache(maxsize=1000, ttl=86400)  # 24h = 86400s
```

**Endpoints:**
- `POST /api/url` → Processa URL (cache hit mostra "Artigo em cache")
- `DELETE /api/cache?url=...` → Invalida cache específico

**Visibilidade:**
- Cache hit: Mensagem UI "Artigo em cache"
- Cache miss: Mensagem UI "Artigo processado"
- Response header: `X-Cache: HIT` ou `X-Cache: MISS`

---

### 4. Rate Limiting & Ética

**Decisão:** Leve (confia no httpx) + robots.txt sempre

**Configuração:**
- **Rate limit por domínio:** Nenhum (usa timeout do httpx)
- **robots.txt:** Checar sempre antes de fetch
- **User-Agent:** Default (`python-httpx/x.y.z`)
- **Bloqueio detectado (429/403):** Backoff exponencial + mensagem "Site está bloqueando, tente depois"

**robots.txt checker:**
```python
import robots-txt
# Checar antes de fetch, cache do resultado por domínio
```

---

## Code Context

### Estrutura do Projeto

**Atual:**
```
my_reader/
├── app.py              # FastAPI backend
├── static/
│   └── index.html      # Frontend
├── tests/
│   └── test_app.spec.js # Playwright E2E
└── requirements.txt
```

**Após Fase 2:**
```
my_reader/
├── app.py              # + endpoint POST /api/url, DELETE /api/cache
├── src/
│   └── crawler/        # NOVO
│       ├── __init__.py
│       ├── models.py       # Article, CrawlResult
│       ├── client.py       # CrawlerClient (httpx)
│       ├── parser.py       # parse_html (BeautifulSoup)
│       ├── extractor.py    # extract_article (readability-lxml)
│       ├── cache.py        # url_cache (TTLCache)
│       ├── robots.py       # NOVO: robots.txt checker
│       └── integrator.py   # process_url_to_audio
├── static/
│   └── index.html      # + UI de input URL
├── tests/
│   ├── test_app.spec.js
│   ├── test_crawler.py     # NOVO: unitários crawler
│   └── test_url_endpoint.py # NOVO: endpoint /api/url
└── requirements.txt    # + httpx, beautifulsoup4, lxml, readability-lxml, cachetools, langdetect
```

### Integrações

**app.py → src/crawler:**
```python
from src.crawler.integrator import process_url_to_audio
from src.crawler.cache import url_cache

@app.post("/api/url")
async def url_to_audio(url: str, voice: str, speed: float):
    article = process_url_to_audio(url, voice, speed)
    # Gerar áudio com pipeline existente
    audio = generate_audio(article.text, voice, speed)
    return StreamingResponse(...)

@app.delete("/api/cache")
async def invalidate_cache(url: str):
    # Invalidar cache específico
    pass
```

**Frontend → Backend:**
```javascript
// Processar URL
const response = await fetch('/api/url', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url: inputUrl, voice, speed})
});

// Verificar cache no response
const cacheStatus = response.headers.get('X-Cache'); // 'HIT' ou 'MISS'

// Invalidar cache
await fetch('/api/cache?url=' + encodeURIComponent(url), {
    method: 'DELETE'
});
```

### Convenções de Código

**Padrões do projeto (de CONVENTIONS.md):**
- Python: `snake_case`, 4 espaços, single quotes, type hints
- JavaScript: `camelCase`, 4 espaços, single quotes
- Testes: prefixo `test_`, pytest para Python, Playwright para JS
- Error handling: `try/except` com logging, `HTTPException` para APIs

**Issues existentes a considerar (de PREOCUPACOES.md):**
- ⚠️ Variável global `pipeline` - não agravar (usar como está)
- ⚠️ Voices hardcoded em 2 lugares - não relacionado a esta fase
- ⚠️ Sample rate hardcoded - usar constante se adicionar novo código de áudio
- ⚠️ CORS permissivo - OK para app local

---

## Requisitos Cobertos

| ID | Requisito | Implementação |
|----|-----------|---------------|
| CRAWL-01 | Fetch URL content | `src/crawler/client.py` com httpx |
| CRAWL-02 | Parse HTML structure | `src/crawler/parser.py` com BeautifulSoup |
| CRAWL-03 | Extract article text | `src/crawler/extractor.py` com readability-lxml |
| CRAWL-04 | Detect language | `src/crawler/extractor.py` com langdetect |
| CRAWL-05 | Cache responses | `src/crawler/cache.py` com TTLCache 24h |
| CRAWL-06 | Rate limiting | Timeout httpx + robots.txt checker |

---

## Próximos Passos

**Executar:** `/fase-executar-fase 02`

**Planos:**
1. **02-01:** Criar `src/crawler/` com 5 módulos base
2. **02-02:** Adicionar endpoint `/api/url` e integração
3. **02-03:** UI de preview e testes unitários

**Checkpoints:**
- Após Etapa 1: Verificar imports de todos módulos
- Após Etapa 2: Testar endpoint com curl
- Após Etapa 3: Teste manual completo (URL → preview → áudio)

---

## Ideias Deferidas

**Sugeridas durante discussão mas fora do scope:**

| Ideia | Por que deferida | Fase potencial |
|-------|-----------------|----------------|
| Preview editável (usuário ajusta texto) | Complexidade adicional, MVP primeiro | Fase 3: Melhorias de UX |
| Cache por conteúdo hash | TTL 24h é suficiente para MVP | Fase 4: Otimizações |
| Rate limiting agressivo (20 req/min) | App é uso pessoal, não crawler em massa | - |
| Diffbot API (pago) | readability-lxml atende MVP | - |
| Endpoint para listar cache | Invalidação por URL é suficiente | Fase 3: Admin tools |
