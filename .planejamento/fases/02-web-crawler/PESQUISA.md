# Fase 02: Web Crawler - Pesquisa

**Pesquisado:** 2026-04-01
**Domínio:** Web crawling, HTML parsing, content extraction em Python
**Confiança:** ALTA

## Summary

Esta pesquisa investiga o ecossistema Python para web crawling focado em extração de conteúdo de artigos. As bibliotecas principais estão maduras e bem mantidas, com httpx emergindo como cliente HTTP moderno (suporte async + HTTP/2), BeautifulSoup4 + lxml como stack padrão para parsing, e readability-lxml para extração de conteúdo de artigos.

**Recomendação primária:** Use httpx (sync) + BeautifulSoup4/lxml + readability-lxml para crawler síncrono simples; adicione cachetools para cache e tenacity para retry/backoff.

## Standard Stack

### Core
| Library | Versão | Propósito | Por quê Padrão |
|---------|---------|---------|--------------|
| httpx | 0.28.1 | Cliente HTTP | API familiar (requests-like), suporte async opcional, HTTP/2, timeouts estritos, type hints completo |
| beautifulsoup4 | 4.14.3 | HTML parsing | API Pythonic, fácil depuração, ampla adoção |
| lxml | 6.0.2 | Parser HTML/XML | Muito rápido (C backend), XPath support, parser XML nativo |
| readability-lxml | 0.8.4.1 | Extração conteúdo | Focado em artigo principal, remove boilerplate, ativo (mai 2025) |

### Supporting
| Library | Versão | Propósito | Quando Usar |
|---------|---------|---------|-------------|
| cachetools | 7.0.5 | Cache em memória | TTLCache para cache com expiração, LRUCache para limite de itens |
| tenacity | N/A | Retry/backoff | Rate limiting, retry com exponential backoff |
| langdetect | 1.0.9 | Detecção idioma | Identificar idioma do conteúdo extraído |
| urllib3 | N/A | Connection pooling | Já incluso no httpx/requests |

### Alternativas Consideradas
| Em vez de | Pode Usar | Tradeoff |
|------------|-----------|----------|
| httpx | requests 2.33.1 | Requests mais maduro, mas sem async nativo; httpx é "próxima geração" |
| aiohttp 3.13.5 | httpx.AsyncClient | aiohttp mais complexo, httpx API mais limpa |
| newspaper3k | readability-lxml | newspaper3k abandonado (2018), readability-lxml ativo |
| html5lib | lxml | html5lib extremamente lento, lxml 10-100x mais rápido |

**Installation:**
```bash
pip install httpx beautifulsoup4 lxml readability-lxml cachetools langdetect tenacity
```

## Architecture Patterns

### Recommended Project Structure
```
src/crawler/
├── __init__.py
├── client.py          # HTTP client wrapper (httpx)
├── parser.py          # HTML parsing (BeautifulSoup + lxml)
├── extractor.py       # Content extraction (readability-lxml)
├── cache.py           # Cache layer (cachetools)
├── rate_limiter.py    # Rate limiting / throttling
└── models.py          # Data classes (Article, URL, etc.)
```

### Pattern 1: HTTP Client com Session Pooling
**O quê:** Reutilizar sessão HTTP para connection pooling
**Quando usar:** Sempre que fizer múltiplas requisições
**Exemplo:**
```python
# Source: https://www.python-httpx.org/advanced/clients/
import httpx

# Client singleton ou scoped
client = httpx.Client(timeout=30.0, follow_redirects=True)

# Para múltiplas requisições
with httpx.Client() as client:
    response = client.get('https://example.com')
    html = response.text
```

### Pattern 2: Parsing com BeautifulSoup + lxml
**O quê:** Usar lxml como parser backend do BeautifulSoup
**Quando usar:** Para HTML parsing robusto e rápido
**Exemplo:**
```python
# Source: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_content, 'lxml')
title = soup.title.string if soup.title else None
links = [a['href'] for a in soup.find_all('a', href=True)]
```

### Pattern 3: Extração de Artigo com readability-lxml
**O quê:** Extrair conteúdo principal removendo boilerplate
**Quando usar:** Para extrair texto de artigos de notícias/blogs
**Exemplo:**
```python
# Source: https://pypi.org/project/readability-lxml/
from readability import Document

doc = Document(html_content)
title = doc.title()
content = doc.summary()  # HTML limpo
text = doc.text_content()  # Texto puro
```

### Pattern 4: Cache com TTL
**O quê:** Cache em memória com expiração por tempo
**Quando usar:** Evitar re-fetch de URLs recentemente processadas
**Exemplo:**
```python
# Source: https://pypi.org/project/cachetools/
from cachetools import TTLCache, cached

cache = TTLCache(maxsize=1000, ttl=3600)  # 1 hora

@cached(cache)
def fetch_url(url: str) -> str:
    response = httpx.get(url)
    return response.text
```

### Anti-Patterns to Avoid
- **Criar novo Client por requisição:** Destrói connection pooling, lento
- **Usar html.parser padrão:** Mais lento que lxml, menos tolerante
- **Parse sem encoding correto:** Sempre use `response.text` (httpx detecta encoding)
- **Cache sem TTL:** Pode causar stale data indefinidamente
- **Sem rate limiting:** Risk de bloqueio por IP

## Don't Hand-Roll

| Problema | Não Construa | Use no Lugar | Por quê |
|---------|-------------|-------------|-----|
| Extração conteúdo artigo | Regex/heurísticas próprias | readability-lxml | Algoritmo testado, edge cases (CJK, scripts), mantido |
| HTTP connection pooling | Socket management manual | httpx.Client | Keep-alive, retry, redirects, SSL já implementados |
| HTML parsing | Regex em HTML | BeautifulSoup + lxml | HTML é não-regular, parsers lidam com malformed HTML |
| Cache com expiração | Dict com timestamps | cachetools.TTLCache | Thread-safe, LRU eviction, tested |
| Rate limiting | time.sleep() manual | tenacity ou httpx-limiter | Backoff exponencial, retry logic, jitter |
| Detecção idioma | Listas de palavras | langdetect | Port do Google language-detection, 55 idiomas |

**Key insight:** Web crawling parece simples mas tem muitos edge cases: encoding detection, malformed HTML, redirects, rate limiting, caching, retry logic. Use bibliotecas maduras.

## Common Pitfalls

### Pitfall 1: Encoding Detection Incorreto
**O que dá errado:** Assumir UTF-8 sempre, quebrar com ISO-8859-1/Windows-1252
**Por que acontece:** Sites antigos ou regionais usam encodings diferentes
**Como evitar:** Use `response.text` do httpx (detecta automaticamente via headers + content sniffing)
**Sinais de alerta:** `` ou caracteres estranhos no output

### Pitfall 2: Memory Leak com parse trees
**O que dá errado:** Manter referências a BeautifulSoup objects por muito tempo
**Por que acontece:** Parse tree mantém referência a todo HTML original
**Como evitar:** Extrair dados necessários e descartar soup; usar `del soup` explicitamente
**Sinais de alerta:** Memory usage cresce com URLs processadas

### Pitfall 3: Rate Limiting Agressivo
**O que dá errado:** Fazer requests sem delay, ser bloqueado por IP
**Por que acontece:** Sites detectam crawling agressivo
**Como evitar:** Implementar delay entre requests (2-5s), respeitar robots.txt, usar User-Agent adequado
**Sinais de alerta:** HTTP 429, 503, IPs bloqueados, CAPTCHAs

### Pitfall 4: newspaper3k Desatualizado
**O que dá errado:** Usar newspaper3k que está abandonado desde 2018
**Por que acontece:** Tutoriais antigos ainda recomendam
**Como evitar:** Use readability-lxml (ativo) ou trafilatura
**Sinais de alerta:** Erros com Python 3.10+, features quebradas

### Pitfall 5: asyncio.run() em loop
**O que dá errado:** Chamar `asyncio.run()` múltiplas vezes em vez de reusar event loop
**Por que acontece:** Pattern síncrono vs async confuso
**Como evitar:** Ou use httpx sync Client, ou crie AsyncClient uma vez e reuse
**Sinais de alerta:** "RuntimeError: Event loop is closed", performance ruim

### Pitfall 6: lxml C Dependencies
**O que dá errado:** Falha na instalação em ambientes sem compilador C
**Por que acontece:** lxml precisa compilar bindings C para libxml2/libxslt
**Como evitar:** Instalar wheels pré-compilados (`pip install lxml` geralmente funciona), ou usar `html.parser` como fallback
**Sinais de alerta:** Erros de compilação C no pip install

## Code Examples

### HTTP Request Básico (httpx)
```python
# Source: https://www.python-httpx.org/quickstart/
import httpx

with httpx.Client() as client:
    response = client.get('https://example.com/article')
    response.raise_for_status()  # Raise exception para 4xx/5xx
    html = response.text  # Encoding detectado automaticamente
```

### Parsing HTML com BeautifulSoup
```python
# Source: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
from bs4 import BeautifulSoup

soup = BeautifulSoup(html, 'lxml')

# Extrair título
title = soup.title.string if soup.title else None

# Extrair todos links
for link in soup.find_all('a', href=True):
    url = link['href']
    text = link.get_text(strip=True)

# Extrair por CSS selector
main_content = soup.select_one('article.main')
```

### Extração de Artigo (readability-lxml)
```python
# Source: https://pypi.org/project/readability-lxml/
from readability import Document

doc = Document(html)
article = {
    'title': doc.title(),
    'html': doc.summary(),  # HTML limpo do conteúdo principal
    'text': doc.text_content(),  # Texto puro
}
```

### Cache com TTL
```python
# Source: https://pypi.org/project/cachetools/
from cachetools import TTLCache, cached

# Cache de 1000 items, expira em 1 hora
cache = TTLCache(maxsize=1000, ttl=3600)

@cached(cache)
def fetch_and_parse(url: str) -> dict:
    with httpx.Client() as client:
        response = client.get(url)
        response.raise_for_status()
        doc = Document(response.text)
        return {
            'title': doc.title(),
            'text': doc.text_content(),
        }
```

### Rate Limiting Simples
```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, requests_per_minute: int = 20):
        self.min_interval = 60.0 / requests_per_minute
        self.last_request = datetime.min
    
    def wait(self):
        elapsed = (datetime.now() - self.last_request).total_seconds()
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request = datetime.now()

# Uso
limiter = RateLimiter(requests_per_minute=20)
limiter.wait()
response = httpx.get(url)
```

## State of the Art

| Abordagem Antiga | Abordagem Atual | Quando Mudou | Impacto |
|--------------|------------------|--------------|--------|
| requests + manual parsing | httpx + readability-lxml | 2020-2024 | Async nativo, extração mais inteligente |
| newspaper (Python 2) | newspaper3k → readability-lxml | 2018 | newspaper3k abandonado, migração necessária |
| Regex HTML parsing | BeautifulSoup + lxml | 2010+ | parsing robusto de malformed HTML |
| requests.Session pooling | httpx.Client | 2020+ | HTTP/2, async opcional, type hints |
| manual cache dict | cachetools TTLCache | Sempre | Thread-safe, LRU, TTL built-in |

**Deprecated/desatualizado:**
- newspaper3k (0.2.8, 2018): Abandonado, não usar para novos projetos
- requests: Ainda válido mas httpx é "next-gen" com benefícios async
- html.parser: Funciona mas lxml é 10-100x mais rápido

## Open Questions

1. **Trafilatura como alternativa?**
   - O que sabemos: Trafilatura é library mais recente para extração
   - O que é unclear: Maturidade vs readability-lxml, performance comparativa
   - Recomendação: Considerar trafilatura se readability-lxml não atender casos específicos

2. **Redis para cache distribuído?**
   - O que sabemos: cachetools é in-memory apenas
   - O que é unclear: Se my_reader precisa cache persistente/distribuído
   - Recomendação: Começar com cachetools, migrar para Redis se necessário

3. **Scrapy framework vs crawler custom?**
   - O que sabemos: Scrapy é framework completo
   - O que é unclear: Se complexidade do Scrapy é necessária
   - Recomendação: Para extração simples de artigos, crawler custom é suficiente

## Arquitetura de Validação

### Test Framework
| Property | Value |
|----------|-------|
| Framework | pytest 8.x |
| Config file | pytest.ini ou pyproject.toml |
| Quick run command | `pytest tests/test_crawler.py -x` |
| Full suite command | `pytest tests/ -x --cov=src` |

### Fase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CRAWL-01 | Fetch URL content | unit | `pytest tests/test_client.py -x` | ❌ Etapa 0 |
| CRAWL-02 | Parse HTML structure | unit | `pytest tests/test_parser.py -x` | ❌ Etapa 0 |
| CRAWL-03 | Extract article text | unit | `pytest tests/test_extractor.py -x` | ❌ Etapa 0 |
| CRAWL-04 | Detect language | unit | `pytest tests/test_language.py -x` | ❌ Etapa 0 |
| CRAWL-05 | Cache responses | unit | `pytest tests/test_cache.py -x` | ❌ Etapa 0 |
| CRAWL-06 | Rate limiting | integration | `pytest tests/test_rate_limit.py -x` | ❌ Etapa 0 |

### Sampling Rate
- **Por task commit:** `pytest tests/test_*.py -x` (tests específicos da task)
- **Por etapa merge:** `pytest tests/ -x` (suite completa)
- **Fase gate:** Full suite green antes de `/fase-verify-work`

### Etapa 0 Gaps
- [ ] `tests/test_client.py` — HTTP client wrapping (CRAWL-01)
- [ ] `tests/test_parser.py` — HTML parsing (CRAWL-02)
- [ ] `tests/test_extractor.py` — Content extraction (CRAWL-03)
- [ ] `tests/conftest.py` — Fixtures compartilhados (HTML samples)
- [ ] `pytest.ini` — Configuração do framework

## Sources

### Primary (ALTA confiança)
- https://pypi.org/project/httpx/ — httpx 0.28.1, features, instalação
- https://pypi.org/project/beautifulsoup4/ — beautifulsoup4 4.14.3, API
- https://pypi.org/project/lxml/ — lxml 6.0.2, parser backend
- https://pypi.org/project/readability-lxml/ — readability-lxml 0.8.4.1, uso
- https://pypi.org/project/cachetools/ — cachetools 7.0.5, TTLCache/LRUCache
- https://pypi.org/project/langdetect/ — langdetect 1.0.9, detecção idioma
- https://www.python-httpx.org/async/ — Documentação oficial httpx async
- https://www.crummy.com/software/BeautifulSoup/bs4/doc/ — Documentação oficial BeautifulSoup

### Secondary (MÉDIA confiança)
- PyPI release history — Datas de release verificadas
- GitHub repos (via PyPI links) — Manutenção ativa

### Tertiary (BAIXA confiança)
- newspaper3k status — Inferido da data de última release (2018)

## Metadata

**Confidence breakdown:**
- Standard stack: ALTA — Todas bibliotecas verificadas via PyPI oficial + docs
- Architecture: ALTA — Patterns de documentação oficial
- Pitfalls: ALTA — Baseado em experiência documentada da comunidade
- Version info: ALTA — PyPI é fonte primária

**Data de pesquisa:** 2026-04-01
**Válido até:** 2026-07-01 (3 meses — bibliotecas estáveis, mudanças graduais)
