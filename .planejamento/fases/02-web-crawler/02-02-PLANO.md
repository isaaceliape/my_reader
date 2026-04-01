---
fase: 02-web-crawler
plan: 02
type: execute
etapa: 2
depends_on: ["02-01"]
files_modified: [app.py, src/crawler/integrator.py]
autonomous: true
requisitos: [CRAWL-01, CRAWL-06]

must_haves:
  truths:
    - "Endpoint POST /api/url existe"
    - "URLs são validadas antes de fetch"
    - "Crawler é chamado pelo endpoint"
    - "Áudio é gerado do conteúdo extraído"
    - "Response retorna artigo + audio URL"
  artifacts:
    - path: "app.py"
      provides: "Endpoint /api/url"
      exports: ["POST /api/url"]
      contains: "@app.post"
    - path: "src/crawler/integrator.py"
      provides: "Integração crawler + TTS"
      exports: ["process_url_to_audio"]
      min_lines: 50
  key_links:
    - from: "app.py"
      to: "src/crawler/integrator.py"
      via: "import e chamada"
      pattern: "from src\\.crawler\\.integrator import"
    - from: "src/crawler/integrator.py"
      to: "src/crawler/client.py"
      via: "usa CrawlerClient"
      pattern: "CrawlerClient\\(\\)"
    - from: "src/crawler/integrator.py"
      to: "app.py"
      to_symbol: "pipeline"
      via: "acessa pipeline global"
      pattern: "pipeline"
---

<objective>
Integrar crawler ao backend FastAPI existente

Purpose: Conectar extração de URLs ao pipeline TTS para gerar áudio de artigos
Output: Endpoint POST /api/url funcionando, módulo integrator
</objective>

<context>
@.planejamento/fases/02-web-crawler/02-01-SUMARIO.md
@.planejamento/fases/02-web-crawler/PESQUISA.md
@app.py
</context>

<interfaces>
<!-- Do Plano 02-01 (após execução):
from src.crawler.client import CrawlerClient
from src.crawler.parser import parse_html
from src.crawler.extractor import extract_article, detect_language
from src.crawler.models import Article, CrawlResult
from src.crawler.cache import url_cache

Do app.py:
pipeline = None  # KPipeline
def generate_audio(text: str, voice: str, speed: float = 1.0) -> bytes
-->
</interfaces>

<tasks>

<task type="auto">
  <name>Tarefa 1: Criar módulo integrator</name>
  <files>src/crawler/integrator.py</files>
  <action>
    Criar `src/crawler/integrator.py` com função `process_url_to_audio`:
    
    ```python
    from .client import CrawlerClient
    from .parser import parse_html
    from .extractor import extract_article, detect_language
    from .models import Article
    from datetime import datetime
    
    def process_url_to_audio(url: str, voice: str = "af_heart", speed: float = 1.0):
        # 1. Fetch URL
        client = CrawlerClient()
        # 2. Parse HTML
        # 3. Extract article
        # 4. Detect language
        # 5. Retornar Article + metadados
        # Nota: NÃO gerar áudio aqui (feito no endpoint)
        pass
    ```
    
    A função deve:
    - Usar CrawlerClient para fetch
    - Parsear HTML com BeautifulSoup
    - Extrair conteúdo com readability
    - Detectar idioma
    - Retornar Article completo
  </action>
  <verify>
    <automated>python -c "from src.crawler.integrator import process_url_to_audio; print('OK')"</automated>
  </verify>
  <done>
    - process_url_to_audio existe
    - Importa todos módulos do crawler
    - Retorna Article com url, title, text, language, fetched_at
  </done>
</task>

<task type="auto">
  <name>Tarefa 2: Adicionar endpoint POST /api/url ao app.py</name>
  <files>app.py</files>
  <action>
    Adicionar em `app.py` após endpoint `/tts`:
    
    ```python
    @app.post("/api/url")
    async def url_to_audio(
        url: str = Body(...),
        voice: str = Body("af_heart"),
        speed: float = Body(1.0)
    ):
        # 1. Validar URL (regex ou urllib.parse)
        # 2. Chamar process_url_to_audio
        # 3. Gerar áudio com generate_audio()
        # 4. Retornar StreamingResponse com audio + Article metadata
        pass
    ```
    
    Validação de URL:
    - Usar `from urllib.parse import urlparse`
    - Verificar scheme (http/https)
    - Verificar netloc não vazio
    - Retornar 400 se URL inválida
    
    Resposta deve incluir:
    - Audio como StreamingResponse
    - Headers com metadata (X-Article-Title, X-Article-URL)
  </action>
  <verify>
    <automated>python -c "import app; print('OK')" && curl -X POST http://localhost:8000/api/url -H "Content-Type: application/json" -d '{"url": "https://example.com"}' --fail || echo "Endpoint existe (pode falhar se servidor não rodando)"</automated>
  </verify>
  <done>
    - Endpoint POST /api/url existe em app.py
    - Valida URL com urlparse
    - Chama process_url_to_audio
    - Gera áudio com pipeline existente
    - Retorna StreamingResponse
  </done>
</task>

<task type="auto">
  <name>Tarefa 3: Adicionar novas dependências ao requirements.txt</name>
  <files>requirements.txt</files>
  <action>
    Adicionar ao `requirements.txt`:
    ```
    httpx>=0.28.1
    beautifulsoup4>=4.14.3
    lxml>=6.0.2
    readability-lxml>=0.8.4.1
    cachetools>=7.0.5
    langdetect>=1.0.9
    ```
    
    Manter dependências existentes (fastapi, uvicorn, kokoro, etc.)
  </action>
  <verify>
    <automated>grep -q "httpx" requirements.txt && grep -q "beautifulsoup4" requirements.txt && echo "OK"</automated>
  </verify>
  <done>
    - requirements.txt tem todas 6 novas dependências
    - Versões mínimas especificadas
  </done>
</task>

</tasks>

<verification>
- [ ] Endpoint /api/url responde (pode testar com curl)
- [ ] Validação de URL rejeita URLs inválidas (400)
- [ ] process_url_to_audio retorna Article válido
- [ ] Audio é gerado do texto extraído
- [ ] Novas dependências no requirements.txt
</verification>

<success_criteria>
- Endpoint POST /api/url funcional
- Validação de URL implementada
- Integração crawler + TTS funcionando
- Artigo extraído + áudio gerado em uma chamada
</success_criteria>

<output>
Após conclusão, criar `.planejamento/fases/02-web-crawler/02-02-SUMARIO.md`
</output>
