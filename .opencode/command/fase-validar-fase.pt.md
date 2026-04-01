---
description: Audita retroativamente e preenche gaps de validação Nyquist para uma fase completada
argument-hint: "[número da fase]"
tools:
  read: true
  write: true
  edit: true
  bash: true
  glob: true
  grep: true
  task: true
  question: true
---
<objective>
Auditar cobertura de validação Nyquist para uma fase completada. Três estados:
- (A) VALIDATION.md existe — audita e preenche gaps
- (B) Sem VALIDATION.md, SUMMARY.md existe — reconstrói dos artefatos
- (C) Fase não executada — sai com orientação

Output: VALIDATION.md atualizado + arquivos de teste gerados.
</objective>

<execution_context>
@./.opencode/fase/workflows/validate-phase.md
</execution_context>

<context>
Fase: $ARGUMENTS — opcional, padrão é última fase completada.
</context>

<process>
Execute @./.opencode/fase/workflows/validate-phase.md.
Preserve todos os gates do workflow.
</process>
