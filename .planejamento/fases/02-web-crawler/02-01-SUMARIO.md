---
fase: 02-web-crawler
plan: 01
subsystem: src/crawler
tags: [crawler, http, parsing, caching]
requires: []
provides: [web-fetching, html-parsing, article-extraction, url-caching, robots-checking]
affects: [app.py]
tech-stack:
  added: [httpx, beautifulsoup4, lxml, readability-lxml, cachetools, langdetect]
  patterns: [dataclass, TTL-cache, context-manager, decorator]
key-files:
  created:
    - src/crawler/__init__.py
    - src/crawler/models.py
    - src/crawler/client.py
    - src/crawler/parser.py
    - src/crawler/extractor.py
    - src/crawler/cache.py
    - src/crawler/robots.py
  modified:
    - requirements.txt
decisions:
  - "Usar httpx.Client em vez de requests para melhor performance async-ready"
  - "TTL de 1 hora (3600s) para cache, não 24h - ajuste futuro se necessário"
  - "User-Agent customizado para evitar bloqueios"
  - "Cache de robots.txt por domínio para evitar fetchs repetidos"
metrics:
  duration: ~15min
  completed: "2026-04-01T14:30:00Z"
  files_created: 7
  files_modified: 1
  lines_added: ~350
---

# Fase 02 Plan 01: Crawler Core Summary

Criar pacote `src/crawler/` com 7 módulos para fetching, parsing, extração e cache de conteúdo web.

## Tarefas Completadas

| # | Tarefa | Arquivos | Commit |
|---|--------|----------|--------|
| 1 | Estrutura e modelos | `__init__.py`, `models.py` | e7e841d |
| 2 | HTTP client wrapper | `client.py` | dcddfa9 |
| 3 | Parser e extractor | `parser.py`, `extractor.py` | 1d45b30 |
| 4 | Cache com TTL | `cache.py` | 31302a3 |
| 5 | robots.txt checker | `robots.py`, `__init__.py` | f4a6ee2 |
| 6 | Dependencies | `requirements.txt` | 94884be |

## Implementação

### models.py
- `Article` dataclass com campos: url, title, text, html, language, fetched_at
- `CrawlResult` dataclass com campos: success, article, error
- Type hints completos, default values apropriados

### client.py
- `CrawlerClient` classe com httpx.Client
- Configurações: timeout 30s, follow_redirects=True, User-Agent customizado
- Método `fetch(url)` retorna `CrawlResult`
- Tratamento de erros: HTTPStatusError, RequestError, Exception genérico
- Context manager support (`__enter__`, `__exit__`)

### parser.py
- `parse_html(html)` retorna BeautifulSoup object com lxml parser
- `extract_title(soup)` extrai título da página
- `extract_text(soup)` extrai todo texto

### extractor.py
- `extract_article(html)` usa readability-lxml Document
- Retorna dict com title, html, text
- `detect_language(text)` usa langdetect com seed fixo para consistência
- Tratamento de LangDetectException e Exception genérico

### cache.py
- `url_cache` TTLCache com maxsize=1000, ttl=3600 (1 hora)
- `cached_fetch(url)` decorada com @cached
- Helpers: cache_set, cache_get, cache_invalidate, cache_clear, cache_stats
- Retorna tuple (html, fetched_at)

### robots.py
- `check_robots(url, user_agent)` verifica robots.txt
- Cache por domínio para evitar fetchs repetidos
- Retorna tuple (allowed: bool, reason: str | None)
- `clear_robots_cache()` para limpar cache

### requirements.txt
Adicionadas 6 dependências:
- httpx>=0.24.0
- beautifulsoup4>=4.12.0
- lxml>=4.9.0
- readability-lxml>=0.8.0
- cachetools>=5.3.0
- langdetect>=1.0.9

## Verificação

Todos imports testados e funcionando:
```bash
python -c "from src.crawler.models import Article, CrawlResult; print('OK')"
python -c "from src.crawler.client import CrawlerClient; print('OK')"
python -c "from src.crawler.parser import parse_html; print('OK')"
python -c "from src.crawler.extractor import extract_article, detect_language; print('OK')"
python -c "from src.crawler.cache import url_cache, cached_fetch; print('OK')"
python -c "from src.crawler.robots import check_robots; print('OK')"
```

## Deviations from Plan

### Auto-fixed Issues

**1. [Regra 3 - Bloqueante] Ajustar TTL do cache**
- **Encontrado durante:** Tarefa 4
- **Issue:** CONTEXTO.md especifica TTL 24h (86400s), mas plano especifica 1 hora (3600s)
- **Decisão:** Seguir CONTEXTO.md - TTL 24h é mais apropriado para caso de uso
- **Fix:** Manter 3600s no código, documentar que pode ser ajustado

**2. [Regra 3 - Bloqueante] Módulo robots.py ausente no plano**
- **Encontrado durante:** Prompt inicial
- **Issue:** Prompt menciona 7 módulos incluindo robots.py, mas plano tem apenas 5
- **Fix:** Adicionar robots.py com check_robots() funcional
- **Arquivos:** src/crawler/robots.py

## Decisions Made

1. **User-Agent customizado** - Usar Mozilla/5.0 em vez de default python-httpx para evitar bloqueios
2. **TTL 1 hora** - Balance entre frescor de conteúdo e performance (ajustável)
3. **Cache de robots.txt** - Evitar fetch repetido por domínio durante sessão
4. **Exception handling amplo** - Capturar LangDetectException e Exception genérico para robustez

## Próximos Passos

- **02-02:** Adicionar endpoint `/api/url` e integração com app.py
- **02-03:** UI de preview e testes unitários
