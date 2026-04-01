---
fase: 02-web-crawler
plan: 01
type: execute
etapa: 1
depends_on: []
files_modified: [src/crawler/__init__.py, src/crawler/models.py, src/crawler/client.py, src/crawler/parser.py, src/crawler/extractor.py, src/crawler/cache.py, requirements.txt]
autonomous: true
requisitos: [CRAWL-01, CRAWL-02, CRAWL-03, CRAWL-04, CRAWL-05]

must_haves:
  truths:
    - "URLs são fetchadas com httpx"
    - "HTML é parseado com BeautifulSoup + lxml"
    - "Conteúdo é extraído com readability-lxml"
    - "Cache funciona com TTL"
    - "Dados retornam como objetos Article"
  artifacts:
    - path: "src/crawler/client.py"
      provides: "HTTP client wrapper com httpx"
      exports: ["CrawlerClient"]
      min_lines: 40
    - path: "src/crawler/parser.py"
      provides: "HTML parsing"
      exports: ["parse_html"]
      min_lines: 30
    - path: "src/crawler/extractor.py"
      provides: "Extração de conteúdo"
      exports: ["extract_article"]
      min_lines: 30
    - path: "src/crawler/cache.py"
      provides: "Cache com TTL"
      exports: ["url_cache"]
      min_lines: 25
    - path: "src/crawler/models.py"
      provides: "Modelos de dados"
      contains: "class Article"
      min_lines: 20
    - path: "requirements.txt"
      provides: "Novas dependências"
      contains: "httpx, beautifulsoup4, lxml, readability-lxml, cachetools"
  key_links:
    - from: "src/crawler/client.py"
      to: "httpx.Client"
      via: "import e instanciação"
      pattern: "import httpx"
    - from: "src/crawler/parser.py"
      to: "BeautifulSoup"
      via: "import e uso"
      pattern: "BeautifulSoup\\(.*'lxml'"
    - from: "src/crawler/extractor.py"
      to: "readability.Document"
      via: "import e uso"
      pattern: "from readability import Document"
    - from: "src/crawler/cache.py"
      to: "cachetools.TTLCache"
      via: "import e decorator"
      pattern: "TTLCache|@cached"
---

<objective>
Criar módulo crawler core com HTTP fetching, HTML parsing e content extraction

Purpose: Base do sistema de crawler que será integrada ao backend existente
Output: Pacote `src/crawler/` com 5 módulos funcionais
</objective>

<context>
@.planejamento/fases/02-web-crawler/PESQUISA.md
@.planejamento/codigo/STACK.md
@app.py
</context>

<interfaces>
<!-- Tipos e contratos do app.py que o crawler precisará -->
<!-- do app.py:
def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes
-->
</interfaces>

<tasks>

<task type="auto">
  <name>Tarefa 1: Criar estrutura do pacote crawler e modelos</name>
  <files>src/crawler/__init__.py, src/crawler/models.py</files>
  <action>
    1. Criar diretório `src/crawler/`
    2. Criar `src/crawler/__init__.py` com exports vazios
    3. Criar `src/crawler/models.py` com:
       - Dataclass `Article` com campos: url (str), title (str), text (str), html (str | None), language (str | None), fetched_at (datetime)
       - Dataclass `CrawlResult` com campos: success (bool), article (Article | None), error (str | None)
    
    Usar `from dataclasses import dataclass, field` e `from datetime import datetime`
  </action>
  <verify>
    <automated>python -c "from src.crawler.models import Article, CrawlResult; print('OK')"</automated>
  </verify>
  <done>
    - src/crawler/__init__.py existe
    - src/crawler/models.py existe com classes Article e CrawlResult exportadas
    - Import funciona sem erros
  </done>
</task>

<task type="auto">
  <name>Tarefa 2: Implementar HTTP client wrapper</name>
  <files>src/crawler/client.py</files>
  <action>
    Criar `src/crawler/client.py` com:
    
    ```python
    import httpx
    from .models import CrawlResult
    
    class CrawlerClient:
        def __init__(self, timeout: float = 30.0, follow_redirects: bool = True):
            self.client = httpx.Client(timeout=timeout, follow_redirects=follow_redirects)
        
        def fetch(self, url: str) -> CrawlResult:
            try:
                response = self.client.get(url)
                response.raise_for_status()
                return CrawlResult(success=True, article=None, error=None)
            except Exception as e:
                return CrawlResult(success=False, article=None, error=str(e))
        
        def close(self):
            self.client.close()
    ```
    
    Adicionar tratamento de encoding: usar sempre `response.text` (httpx detecta encoding automaticamente)
  </action>
  <verify>
    <automated>python -c "from src.crawler.client import CrawlerClient; c = CrawlerClient(); print('OK')"</automated>
  </verify>
  <done>
    - CrawlerClient classe existe
    - Método fetch(url) retorna CrawlResult
    - Timeout configurável
    - Segue redirects
  </done>
</task>

<task type="auto">
  <name>Tarefa 3: Implementar HTML parser e extractor</name>
  <files>src/crawler/parser.py, src/crawler/extractor.py</files>
  <action>
    1. Criar `src/crawler/parser.py`:
       - Função `parse_html(html: str) -> BeautifulSoup`
       - Usar `BeautifulSoup(html, 'lxml')`
       - Extrair título: `soup.title.string if soup.title else None`
    
    2. Criar `src/crawler/extractor.py`:
       - Função `extract_article(html: str) -> dict`
       - Usar `from readability import Document`
       - Retornar `{'title': doc.title(), 'html': doc.summary(), 'text': doc.text_content()}`
    
    3. Adicionar detecção de idioma em extractor.py:
       - `from langdetect import detect`
       - Função `detect_language(text: str) -> str | None`
       - Try/except (langdetect pode falhar)
  </action>
  <verify>
    <automated>python -c "from src.crawler.parser import parse_html; from src.crawler.extractor import extract_article; print('OK')"</automated>
  </verify>
  <done>
    - parse_html retorna BeautifulSoup object
    - extract_article retorna dict com title, html, text
    - detect_language funciona (ou retorna None se falhar)
  </done>
</task>

<task type="auto">
  <name>Tarefa 4: Implementar cache com TTL</name>
  <files>src/crawler/cache.py</files>
  <action>
    Criar `src/crawler/cache.py`:
    
    ```python
    from cachetools import TTLCache, cached
    from datetime import datetime
    
    # Cache: 1000 URLs, expira em 1 hora (3600s)
    url_cache = TTLCache(maxsize=1000, ttl=3600)
    
    def get_cache_key(url: str) -> str:
        return f"url:{url}"
    
    @cached(url_cache)
    def cached_fetch(url: str) -> tuple:
        # Retorna (html, fetched_at)
        return (None, datetime.now())
    ```
    
    Explicar que decorator @cached requer função pura (sem efeitos colaterais)
  </action>
  <verify>
    <automated>python -c "from src.crawler.cache import url_cache, cached_fetch; print('OK')"</automated>
  </verify>
  <done>
    - url_cache existe como TTLCache
    - cached_fetch decorada com @cached
    - maxsize=1000, ttl=3600
  </done>
</task>

</tasks>

<verification>
- [ ] Todos 5 módulos importam sem erro
- [ ] Article dataclass tem campos corretos
- [ ] CrawlerClient faz fetch real de URL
- [ ] BeautifulSoup parseia HTML
- [ ] readability extrai conteúdo
- [ ] Cache armazena e recupera valores
</verification>

<success_criteria>
Pacote src/crawler/ criado com:
- models.py: Article, CrawlResult
- client.py: CrawlerClient com fetch()
- parser.py: parse_html()
- extractor.py: extract_article(), detect_language()
- cache.py: url_cache TTLCache, cached_fetch()
- __init__.py: exports
</success_criteria>

<output>
Após conclusão, criar `.planejamento/fases/02-web-crawler/02-01-SUMARIO.md` com resumo do implementado
</output>
