---
fase: 02-web-crawler
plan: 03
type: execute
etapa: 3
depends_on: ["02-02"]
files_modified: [static/index.html, tests/test_crawler.py, tests/test_url_endpoint.py]
autonomous: false
requisitos: [CRAWL-01, CRAWL-02, CRAWL-03]

must_haves:
  truths:
    - "UI tem input para URL"
    - "Botão processa URL"
    - "Loading indicator aparece durante fetch"
    - "Preview do texto extraído é mostrado"
    - "Usuário pode gerar áudio do artigo"
  artifacts:
    - path: "static/index.html"
      provides: "UI para input de URL"
      contains: "input URL, button Processar"
      min_lines: 50
    - path: "tests/test_crawler.py"
      provides: "Testes unitários do crawler"
      contains: "def test_"
      min_lines: 40
    - path: "tests/test_url_endpoint.py"
      provides: "Testes do endpoint /api/url"
      contains: "def test_"
      min_lines: 30
  key_links:
    - from: "static/index.html"
      to: "/api/url"
      via: "fetch() POST"
      pattern: "fetch.*\\/api\\/url"
    - from: "tests/test_crawler.py"
      to: "src/crawler/"
      via: "import e teste"
      pattern: "from src\\.crawler"
---

<objective>
Adicionar UI para input de URL e testes automatizados

Purpose: Permitir que usuários usem o crawler via interface web e garantir qualidade com testes
Output: UI atualizada, testes unitários e de integração
</objective>

<context>
@.planejamento/fases/02-web-crawler/02-02-SUMARIO.md
@.planejamento/codigo/TESTES.md
@static/index.html
</context>

<interfaces>
<!-- Do endpoint /api/url (Plano 02-02):
POST /api/url
Body: {url: string, voice?: string, speed?: number}
Response: Audio streaming + headers X-Article-Title, X-Article-URL
-->
</interfaces>

<tasks>

<task type="auto">
  <name>Tarefa 1: Adicionar UI de input de URL</name>
  <files>static/index.html</files>
  <action>
    Adicionar em `static/index.html` antes ou depois do input de texto existente:
    
    1. Seção "URL to Audio":
       - Input field tipo url com placeholder "Cole URL do artigo..."
       - Botão "Processar URL"
       - Área de preview (título + texto extraído)
       - Botão "Gerar Áudio" (aparece após processar)
    
    2. JavaScript para:
       - Fetch POST /api/url com a URL
       - Mostrar loading spinner durante fetch
       - Exibir preview do artigo (título + primeiras linhas)
       - Habilitar botão "Gerar Áudio"
    
    3. Manter input de texto manual existente (não remover)
  </action>
  <verify>
    <automated>grep -q "Processar URL" static/index.html && grep -q "/api/url" static/index.html && echo "OK"</automated>
  </verify>
  <done>
    - Input field para URL existe
    - Botão "Processar URL" existe
    - JavaScript faz fetch para /api/url
    - Preview mostra título e texto extraído
    - Loading indicator durante fetch
  </done>
</task>

<task type="auto">
  <name>Tarefa 2: Criar testes unitários do crawler</name>
  <files>tests/test_crawler.py</files>
  <action>
    Criar `tests/test_crawler.py` com:
    
    ```python
    import pytest
    from src.crawler.models import Article, CrawlResult
    from src.crawler.parser import parse_html
    from src.crawler.extractor import extract_article
    
    # HTML de exemplo para testes
    SAMPLE_HTML = """
    <html>
        <head><title>Test Article</title></head>
        <body>
            <article>
                <h1>Test Article</h1>
                <p>This is test content.</p>
            </article>
        </body>
    </html>
    """
    
    def test_parse_html_extracts_title():
        soup = parse_html(SAMPLE_HTML)
        assert soup.title.string == "Test Article"
    
    def test_extract_article_returns_content():
        result = extract_article(SAMPLE_HTML)
        assert "Test Article" in result['title']
        assert "test content" in result['text'].lower()
    ```
    
    Adicionar imports pytest no topo se necessário (criar tests/__init__.py se não existir)
  </action>
  <verify>
    <automated>pytest tests/test_crawler.py -x</automated>
  </verify>
  <done>
    - tests/test_crawler.py existe
    - Pelo menos 2 testes: test_parse_html_extracts_title, test_extract_article_returns_content
    - Testes passam (pytest -x)
  </done>
</task>

<task type="checkpoint:human-verify">
  <name>Checkpoint: Testar fluxo completo manualmente</name>
  <what-built>
    - Crawler core (Plano 02-01)
    - Endpoint /api/url (Plano 02-02)
    - UI de input de URL (Plano 02-03 Tarefa 1)
    - Testes unitários (Plano 02-03 Tarefa 2)
  </what-built>
  <how-to-verify>
    1. Instalar dependências: `pip install -r requirements.txt`
    2. Rodar servidor: `python app.py`
    3. Acessar http://localhost:8000
    4. Colar URL de artigo (ex: https://example.com ou artigo real)
    5. Clicar "Processar URL"
    6. Verificar preview aparece com título e texto
    7. Clicar "Gerar Áudio"
    8. Verificar áudio é baixado/tocado
  </how-to-verify>
  <resume-signal>Digite "approved" se funcionou ou descreva issues encontrados</resume-signal>
</task>

</tasks>

<verification>
- [ ] UI aceita input de URL
- [ ] Preview mostra conteúdo extraído
- [ ] Áudio é gerado do artigo
- [ ] Testes unitários passam
- [ ] Teste manual funciona
</verification>

<success_criteria>
- Usuário pode colar URL e gerar áudio
- Conteúdo é extraído corretamente
- Preview é mostrado antes de gerar áudio
- Testes automatizados verdes
</success_criteria>

<output>
Após conclusão, criar `.planejamento/fases/02-web-crawler/02-03-SUMARIO.md`
</output>
