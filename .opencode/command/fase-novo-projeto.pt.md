---
description: Inicializa um novo projeto com coleta profunda de contexto e PROJECT.md
argument-hint: "[--auto]"
tools:
  read: true
  bash: true
  write: true
  task: true
  question: true
---
<context>
**Flags:**
- `--auto` — Modo automático. Após perguntas de configuração, executa research → requirements → roadmap sem interação adicional. Espera documento de ideia via @ reference.
</context>

<objective>
Inicializar um novo projeto através de fluxo unificado: questionamento → research (opcional) → requirements → roadmap.

**Cria:**
- `.planning/PROJECT.md` — contexto do projeto
- `.planning/config.json` — preferências de workflow
- `.planning/research/` — pesquisa de domínio (opcional)
- `.planning/REQUIREMENTS.md` — requisitos definidos
- `.planning/ROADMAP.md` — estrutura de fases
- `.planning/STATE.md` — memória do projeto

**Após este comando:** Execute `/fase-planejar-fase 1` para iniciar a execução.
</objective>

<execution_context>
@./.opencode/fase/workflows/new-project.md
@./.opencode/fase/references/questioning.md
@./.opencode/fase/references/ui-brand.md
@./.opencode/fase/templates/project.md
@./.opencode/fase/templates/requirements.md
</execution_context>

<process>
Execute o workflow new-project de @./.opencode/fase/workflows/new-project.md ponta a ponta.
Preservar todos os gates do workflow (validação, aprovações, commits, roteamento).
</process>
