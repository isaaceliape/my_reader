# Codebase Concerns

**Data de Análise:** 2026-04-01

## Visão Geral

Este documento identifica dívida técnica, riscos arquiteturais, code smells e áreas para melhoria no projeto my_reader (Local TTS Web App). O codebase está em estágio inicial de implementação, com funcionalidade básica operacional mas várias oportunidades de melhoria.

---

## Tech Debt

### 1. Variável Global para Pipeline TTS

**Issue:** Uso de variável global `pipeline` em vez de padrão singleton estruturado

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 48, 66, 83)

**Código atual:**
```python
# Global TTS pipeline (loaded once at startup)
pipeline = None

def load_kokoro_pipeline():
    global pipeline
    # ...
```

**Impacto:**
- Dificulta teste unitário (dependência de estado global)
- Risco de race conditions em ambiente async
- Não segue padrões de injeção de dependência
- Dificulta mock em testes

**Abordagem de fix:** Refatorar para classe singleton ou usar FastAPI lifespan com dependency injection

---

### 2. Lista de Voices Hardcoded em Dois Lugares

**Issue:** Lista de voices duplicada entre backend e frontend

**Files:** 
- [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 148-159)
- [`static/index.html`](file:///Users/isaaceliape/repos/my_reader/static/index.html) (linhas 235-241)

**Código atual:**
```python
# app.py
voices = [
    {"id": "af_heart", "name": "Heart (Female)", "language": "en-US"},
    # ...
]

# index.html
<option value="af_heart">Heart (Female)</option>
<option value="af_sarah">Sarah (Female)</option>
# ...
```

**Impacto:**
- Risco de inconsistência se voices mudarem
- Duplicação de conhecimento
- Manutenção manual necessária em dois lugares

**Abordagem de fix:** Backend expor `/voices` endpoint, frontend buscar dinamicamente e popular dropdown

---

### 3. Sample Rate Hardcoded Sem Constante

**Issue:** Sample rate 24000 hardcoded sem definição como constante

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linha 101)

**Código atual:**
```python
sample_rate = 24000  # Kokoro uses 24kHz
```

**Impacto:**
- Magic number espalhado pelo código
- Dificulta mudança se Kokoro mudar sample rate
- Sem validação de que valor está correto

**Abordagem de fix:** Definir constante `KOKORO_SAMPLE_RATE = 24000` em módulo de configuração

---

### 4. Validação de Texto Duplicada

**Issue:** Validação de comprimento de texto existe no backend mas frontend não previne envio

**Files:** 
- [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linha 187)
- [`static/index.html`](file:///Users/isaaceliape/repos/my_reader/static/index.html) (linha 228)

**Impacto:**
- Usuário pode digitar 5000 caracteres e só receber erro após clique
- Experiência do usuário degradada
- Requisição desnecessária ao backend

**Abordagem de fix:** Frontend validar antes de enviar, mostrar warning ao aproximar do limite

---

## Riscos de Segurança

### 1. CORS Excessivamente Permissivo

**Issue:** CORS permite todas as origens sem restrição

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 33-39)

**Código atual:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ⚠️ Permite qualquer origem
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

**Risco:**
- Qualquer site pode fazer requisições à API
- Potencial para CSRF attacks
- Recursos computacionais podem ser abusados

**Mitigação atual:** Nenhuma

**Recomendações:**
- Restringir `allow_origins` para domínios específicos em produção
- Implementar rate limiting
- Considerar autenticação para uso em rede

---

### 2. Sem Rate Limiting

**Issue:** API não possui rate limiting, permitindo abuso

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (endpoint `/tts`)

**Risco:**
- Usuário malicioso pode sobrecarregar o servidor
- Geração de TTS é CPU/GPU intensiva
- Pode causar negação de serviço acidental ou intencional

**Mitigação atual:** Validação de 5000 caracteres máximo

**Recomendações:**
- Implementar rate limiting (ex: 10 requests/minuto por IP)
- Usar `slowapi` ou middleware customizado
- Adicionar fila de processamento para requisições simultâneas

---

### 3. Sem Validação de Voice ID

**Issue:** Endpoint `/tts` não valida se voice ID é válido antes de usar

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linha 176)

**Código atual:**
```python
@app.post("/tts")
async def text_to_speech(
    text: str = Body(...),
    voice: str = Body("af_heart"),  # ⚠️ Sem validação
    speed: float = Body(1.0)
):
```

**Risco:**
- Usuário pode passar voice ID inexistente
- Error só ocorre durante geração (tarde)
- Potencial para injection attacks se Kokoro tiver vulnerabilidades

**Recomendações:**
- Validar voice ID contra lista conhecida
- Retornar erro 400 imediato se voice inválido
- Considerar usar Enum ou Pydantic validator

---

## Code Smells

### 1. Função `get_device()` Poderia Ser Cacheada

**Issue:** Detecção de dispositivo roda toda vez que `load_kokoro_pipeline()` é chamado

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 51-61)

**Código atual:**
```python
def get_device():
    if torch.backends.mps.is_available():
        return "mps"
    elif torch.cuda.is_available():
        return "cuda"
    else:
        return "cpu"
```

**Impacto:**
- Verificações desnecessárias se chamado múltiplas vezes
- Performance mínima, mas princípio violado

**Abordagem de fix:** Usar `@lru_cache` ou mover para constante no startup

---

### 2. Tratamento de Error Genérico

**Issue:** Múltiplos `except Exception as e` sem especificidade

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 74-78, 114-118, 198-200)

**Código atual:**
```python
except Exception as e:
    logger.error(f"Failed to load Kokoro pipeline: {e}")
    return False
```

**Impacto:**
- Dificulta debugging (não sabe qual exceção ocorreu)
- Pode mascarar erros críticos
- Impossível tratar erros específicos diferentemente

**Abordagem de fix:** Capturar exceções específicas (RuntimeError, ImportError, etc.)

---

### 3. Import Inside Function

**Issue:** Import de `FileResponse` dentro da função `root()`

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linha 131)

**Código atual:**
```python
@app.get("/")
async def root():
    from fastapi.responses import FileResponse  # ⚠️ Import interno
    index_path = static_path / "index.html"
```

**Impacto:**
- Viola PEP 8 (imports devem estar no topo)
- Sugere possível circular dependency (não é o caso aqui)
- Performance mínima, mas anti-pattern

**Abordagem de fix:** Mover import para topo do arquivo

---

### 4. HTML Com JavaScript Inline

**Issue:** Todo JavaScript está inline no HTML em vez de arquivo separado

**Files:** [`static/index.html`](file:///Users/isaaceliape/repos/my_reader/static/index.html) (linhas 278-410)

**Impacto:**
- Mistura de concerns (view + lógica)
- Dificulta teste de JavaScript
- Não aproveita caching de navegador para JS
- Arquivo HTML grande (412 linhas)

**Abordagem de fix:** Extrair para `static/app.js`, manter HTML apenas para estrutura

---

### 5. Test Files No Gitignore Mas Presentes

**Issue:** `test_kokoro*.py` estão no `.gitignore` mas existem no repositório

**Files:** 
- [`.gitignore`](file:///Users/isaaceliape/repos/my_reader/.gitignore) (linha 17)
- `test_kokoro.py`, `test_kokoro2.py`, `test_kokoro3.py`

**Impacto:**
- Inconsistência entre gitignore e estado do repo
- Arquivos de teste ad-hoc podem ser committed acidentalmente
- Indica falta de padrão de teste estabelecido

**Recomendações:**
- Remover arquivos de teste ad-hoc do repo
- Ou estabelecer padrão formal de testes Python (pytest)

---

## Gaps de Testes

### 1. Apenas Testes E2E (Playwright), Sem Testes Unitários

**Issue:** Codebase possui apenas testes E2E via Playwright, nenhum teste unitário Python

**Files:** [`test_app.spec.js`](file:///Users/isaaceliape/repos/my_reader/test_app.spec.js)

**O que não está testado:**
- Função `get_device()` 
- Função `load_kokoro_pipeline()`
- Função `generate_audio()` 
- Validações de input no `/tts`
- Endpoint `/voices`
- Error handling paths

**Risk:**
- Regressões não detectadas em refatorações
- Dificuldade em testar edge cases sem E2E
- Testes E2E são lentos e frágeis

**Prioridade:** Alta - adicionar pytest para testes unitários do backend

---

### 2. Testes E2E Requerem Servidor Rodando

**Issue:** Testes Playwright assumem servidor em `http://127.0.0.1:8000`

**Files:** [`test_app.spec.js`](file:///Users/isaaceliape/repos/my_reader/test_app.spec.js) (linhas 5, 22, 33, etc.)

**Impacto:**
- Testes não rodam em CI sem setup complexo
- Desenvolvedor precisa lembrar de iniciar servidor
- Testes falham silenciosamente se servidor não estiver no ar

**Recomendações:**
- Adicionar script npm para iniciar servidor em background
- Usar pytest com FastAPI TestClient para testes de API
- Separar testes unitários (rápidos) de E2E (lentos)

---

## Performance Bottlenecks

### 1. Sem Cache de Áudio Gerado

**Issue:** Mesma texto+voice gera áudio do zero toda vez

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (endpoint `/tts`)

**Problema:**
- Usuário que clica "Generate" duas vezes processa twice
- Wasted CPU/GPU cycles
- Latência desnecessária

**Causa:** Nenhum mecanismo de cache implementado

**Caminho de melhoria:**
- Implementar cache LRU em memória (dict com OrderedDict)
- Ou usar Redis para cache persistente
- Cache key: hash(text + voice + speed)
- Phase 4 do roadmap já identifica esta necessidade

---

### 2. Sem Chunking Para Textos Longos

**Issue:** Textos longos (>1000 chars) processados como bloco único

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (função `generate_audio`)

**Problema:**
- Memory spike para textos longos
- Usuário espera todo processamento antes de ouvir
- Falha catastrófica se texto for muito longo

**Causa:** Kokoro pode splitar internamente, mas app não gerencia chunks explicitamente

**Caminho de melhoria:**
- Implementar chunking por sentenças/parágrafos
- Stream chunks de áudio incrementalmente
- Mostrar progresso ao usuário

---

### 3. Sem Monitoramento de Memória

**Issue:** App não monitora uso de memória em runtime

**Files:** Nenhum

**Problema:**
- Memory leaks não detectados até crash
- 8GB M1 é target hardware mas não há validação
- Kokoro claims ~200MB mas PyTorch MPS overhead varia

**Recomendações:**
- Adicionar endpoint `/health` com métricas de memória
- Log warning se memória > 3GB
- Implementar garbage collection explícito após geração

---

## Fragile Areas

### 1. Detecção de Device Sem Fallback Robusto

**Issue:** `get_device()` assume MPS funciona se disponível

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 51-61)

**Por que frágil:**
- MPS tem operator coverage incompleto
- Pode falhar silenciosamente ou crashar
- Sem retry logic com fallback para CPU

**Modificação segura:**
- Envolver inferência em try/except
- Se MPS falhar, tentar CPU automaticamente
- Log warning quando fallback ocorrer

**Test coverage:** Nenhuma

---

### 2. Pipeline Global Sem Thread Safety

**Issue:** `pipeline` global acessado concorrentemente sem locks

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 48, 83-118)

**Por que frágil:**
- FastAPI é async, múltiplas requests simultâneas possíveis
- Kokoro pipeline pode não ser thread-safe
- Race condition se pipeline for reatribuído

**Modificação segura:**
- Usar `asyncio.Lock` para acesso ao pipeline
- Ou implementar pool de pipelines
- Documentar se Kokoro é thread-safe

**Test coverage:** Nenhum teste de concorrência

---

### 3. Static Path Assumido Como Existente

**Issue:** Código assume `static/` directory existe

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 42-45)

**Por que frágil:**
- Se `static/` não existe, app ainda inicia mas `/` retorna 404
- Silent failure
- `static_path.exists()` check existe mas fallback é mínimo

**Código atual:**
```python
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path), html=True), name="static")
```

**Recomendações:**
- Log warning se static não existe
- Ou falhar no startup (fail-fast)
- Adicionar teste que verifica static files

---

## Missing Critical Features

### 1. Sem Logging Estruturado

**Issue:** Logging usa format string básico, não estruturado

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py) (linhas 22-23)

**Problema:**
- Dificulta agregação e busca de logs
- Sem correlation IDs para tracing requests
- Sem níveis de log configuráveis por módulo

**Blocks:**
- Debugging em produção
- Monitoramento e alertas
- Auditoria de uso

**Recomendações:**
- Usar logging JSON (python-json-logger)
- Adicionar correlation ID por request
- Configurar níveis via environment variable

---

### 2. Sem Métricas ou Telemetria

**Issue:** Nenhuma métrica de performance ou uso coletada

**Files:** Nenhum

**Problema:**
- Não sabe RTF (real-time factor) real
- Não sabe quantas gerações por dia
- Não identifica gargalos de performance

**Blocks:**
- Otimização baseada em dados
- Capacity planning
- Detecção de regressão de performance

**Recomendações:**
- Adicionar endpoint `/metrics` (Prometheus format)
- Log tempo de geração por request
- Coletar estatísticas de uso (opt-in)

---

### 3. Sem Documentação de API (OpenAPI/Swagger)

**Issue:** FastAPI gera OpenAPI automático mas não está documentado/validado

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py)

**Problema:**
- Desenvolvedores não sabem como usar API sem ler código
- Sem exemplos de request/response
- Dificulta integração com outros sistemas

**Recomendações:**
- Revisar documentação gerada em `/docs`
- Adicionar exemplos no OpenAPI schema
- Documentar códigos de erro possíveis

---

## Dependencies em Risco

### 1. Kokoro Versão Não Pinada

**Issue:** `requirements.txt` usa `kokoro>=0.7.11` sem upper bound

**Files:** [`requirements.txt`](file:///Users/isaaceliape/repos/my_reader/requirements.txt) (linha 2)

**Risco:**
- Breaking changes em versões futuras (>1.0)
- Pode quebrar em deploy sem aviso
- Kokoro é projeto jovem, API pode mudar

**Impacto:**
- Runtime errors após `pip install --upgrade`
- Inconsistência entre ambientes

**Plano de migração:**
- Pin versão específica: `kokoro==0.9.4`
- Ou usar range conservador: `kokoro>=0.9.4,<1.0.0`
- Monitorar changelog do Kokoro

---

### 2. Dependências Python Sem Lock File

**Issue:** Sem `pip-tools` ou `poetry.lock` para reproducibilidade

**Files:** Apenas `requirements.txt`

**Risco:**
- Diferentes desenvolvedores têm versões diferentes
- Deploy pode instalar versões diferentes
- Dificuldade em debugar issues específicas de versão

**Impacto:**
- "Funciona na minha máquina"
- Bugs de produção não reproduzíveis

**Recomendações:**
- Usar `pip-tools` para gerar `requirements-lock.txt`
- Ou migrar para Poetry/Pipenv
- Commitar lock file no repo

---

## Test Coverage Gaps

### 1. Backend Sem Testes Unitários

**Área não testada:** Toda lógica Python do backend

**Files:** [`app.py`](file:///Users/isaaceliape/repos/my_reader/app.py)

**O que não está testado:**
- Device detection logic
- Audio generation pipeline
- Error handling paths
- Input validation
- Endpoint responses (unit test, apenas E2E)

**Risk:** Regressões em refatorações, bugs não detectados até produção

**Prioridade:** Alta

---

### 2. Frontend Sem Testes

**Área não testada:** JavaScript do frontend

**Files:** [`static/index.html`](file:///Users/isaaceliape/repos/my_reader/static/index.html) (seção `<script>`)

**O que não está testado:**
- Error handling de fetch
- UI state management (loading, error states)
- Audio player integration
- Keyboard shortcuts (não implementados ainda)

**Risk:** UX bugs não detectados, compatibilidade de navegador não validada

**Prioridade:** Média (após testes de backend)

---

### 3. Edge Cases Não Testados

**Área não testada:** Casos extremos e inputs inválidos

**Files:** Ambos backend e frontend

**O que não está testado:**
- Texto vazio ou só whitespace
- Texto com emojis/caracteres especiais
- Texto exatamente no limite (5000 chars)
- Voice ID inválido
- Speed fora do range (0.5-2.0)
- Requests simultâneos
- Server offline (frontend error handling)

**Risk:** Crashes em produção, UX ruim para edge cases

**Prioridade:** Média

---

## Escalabilidade

### 1. Single-Threaded Para Geração de Áudio

**Recurso/Sistema:** Pipeline TTS

**Capacidade atual:** 1 request por vez (implícito)

**Limite:**
- Múltiplas requests simultâneas podem causar race conditions
- Sem fila ou rate limiting

**Caminho de scaling:**
- Implementar fila de tarefas (Celery/RQ)
- Worker pool para processamento paralelo
- Rate limiting para proteger servidor

---

### 2. Sem Suporte Para Múltiplos Usuários

**Recurso/Sistema:** Arquitetura do servidor

**Capacidade atual:** Single-user local app

**Limite:**
- Se exposto na rede, sem autenticação
- Recursos compartilhados sem isolamento

**Caminho de scaling:**
- Adicionar autenticação básica
- Isolar sessões de usuário
- Considerar WebSocket para progresso em tempo real

---

## Summary de Prioridades

### Alta Prioridade (v1.0 blockers)
1. **Testes unitários do backend** - Sem testes = risco alto de regressão
2. **Validação de voice ID** - Segurança e UX
3. **CORS restrictions** - Segurança básica
4. **Error handling específico** - Debuggability

### Média Prioridade (v1.x melhorias)
1. **Cache de áudio** - Performance
2. **JavaScript em arquivo separado** - Manutenibilidade
3. **Rate limiting** - Proteção contra abuso
4. **Logging estruturado** - Observabilidade

### Baixa Prioridade (v2.0+ features)
1. **Métricas e telemetria** - Nice-to-have para MVP
2. **WebSocket para streaming** - Otimização avançada
3. **Fila de tarefas** - Scaling para multi-user
4. **Autenticação** - Apenas se expor na rede

---

*Concerns audit: 2026-04-01*
