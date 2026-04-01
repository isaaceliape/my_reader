# Roadmap

**Última atualização:** 2026-04-01

## Milestone 1: MVP Funcional

### Fase 1: Configuração Inicial ✅

**Status:** COMPLETO

**Objetivo:** Estabelecer base técnica do projeto

**Entregáveis:**
- [x] FastAPI backend configurado
- [x] Kokoro TTS integrado
- [x] Frontend básico funcional
- [x] Testes E2E com Playwright

**Código:** `.planejamento/codigo/`

---

### Fase 2: Web Crawler

**Status:** PRONTO PARA EXECUÇÃO

**Objetivo:** Permitir que usuários compartilhem URLs e gerem áudio de artigos

**Entregáveis:**
- [ ] Web crawler para extração de conteúdo de URLs
- [ ] Processamento e limpeza de HTML
- [ ] Integração com pipeline TTS existente
- [ ] UI para input de URL
- [ ] Cache de URLs processadas
- [x] Planos criados (3 planos em 3 etapas)

**Diretório:** `.planejamento/fases/02-web-crawler/`

**Planos:**
- [x] 02-01 — Crawler core (models, client, parser, extractor, cache)
- [x] 02-02 — Integração backend (endpoint /api/url)
- [ ] 02-03 — UI e testes

---

## Próximos Milestones

*Milestones futuros serão definidos após conclusão do MVP*
