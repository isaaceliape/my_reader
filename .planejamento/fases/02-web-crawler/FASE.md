# Fase 2: Web Crawler

**Status:** PLANEJADO

**Objetivo:** Permitir que usuários compartilhem URLs e gerem áudio de artigos da web

## Descrição

Implementar funcionalidade de web crawler para:
- Receber URLs de artigos/notícias
- Extrair e limpar conteúdo textual
- Converter conteúdo em áudio via pipeline TTS existente
- Gerenciar cache de URLs processadas

## Tarefas

- [ ] **Crawler Core**
  - [ ] Implementar fetch de URLs (requests/httpx)
  - [ ] Parse HTML e extração de conteúdo (BeautifulSoup/readability)
  - [ ] Limpeza de texto (remover scripts, ads, navs)
  - [ ] Detecção de idioma do conteúdo

- [ ] **Backend Integration**
  - [ ] Novo endpoint `POST /api/url`
  - [ ] Validação de URLs
  - [ ] Rate limiting para crawler
  - [ ] Cache de conteúdo extraído

- [ ] **Frontend**
  - [ ] Input field para URL
  - [ ] Botão "Processar URL"
  - [ ] Indicador de loading
  - [ ] Preview do texto extraído

- [ ] **Quality**
  - [ ] Testes unitários do crawler
  - [ ] Testes de integração E2E
  - [ ] Tratamento de erros robusto

## Critérios de Aceite

1. Usuário pode colar URL e gerar áudio
2. Conteúdo é extraído corretamente (título + corpo)
3. Texto é limpo (sem elementos de navegação/ads)
4. Áudio é gerado com qualidade equivalente ao input manual
5. URLs repetidas usam cache (performance)

## Riscos

- Sites com JavaScript pesado podem não renderizar
- Paywalls/bloqueios de scraping
- Estruturas HTML variadas
- Rate limiting de sites externos

## Estimativa

**Complexidade:** Média
**Tarefas:** ~8-12

## Referências

- `app.py` - Pipeline TTS atual
- `.planejamento/codigo/PREOCUPACOES.md` - Dívida técnica a considerar
