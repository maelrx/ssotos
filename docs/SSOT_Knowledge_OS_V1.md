# SSOT — Knowledge OS Self-Hosted, Agent-Aware, Local-First

**Status:** Draft fundador / Single Source of Truth arquitetural  
**Escopo:** visão total do sistema + decisões-base da v1  
**Idioma:** pt-BR  
**Objetivo:** servir como documento mestre técnico, conceitual e operacional para orientar PRD, system design, implementação e evolução do produto.

---

# 0. Premissa central

Este projeto não é um “chat com RAG”, nem um “Obsidian com IA acoplada”, nem um “agente com acesso a arquivos”.  
Ele é um **Knowledge OS self-hosted, local-first, agent-aware e policy-driven**, cujo centro é um **filesystem canônico de conhecimento** em Markdown, com fronteiras formais entre:

1. **conhecimento soberano do usuário**
2. **memória operacional privada do agente**
3. **trabalho intermediário auditável**
4. **processos de pesquisa/ingestão duráveis**
5. **camadas derivadas de retrieval, indexação, síntese e automação**

A IA não é o centro soberano do sistema.  
O centro soberano é o **conhecimento canônico em arquivos**, versionado, auditável, inspecionável e interoperável.

---

# 1. Tese do produto

## 1.1 O que o sistema é

Um sistema self-hosted de aprendizado integrado e interativo que unifica:

- **second brain estruturado e modular**
- **templates de organização pessoal/profissional**
- **daily notes**
- **projetos/áreas/recursos/arquivo**
- **retrieval híbrido para IA**
- **agent runtime com memória própria**
- **research runtime com crawling/parsing/síntese**
- **permissões finas entre domínios**
- **camada de revisão por patch/diff/aprovação**
- **integração futura via MCP**

## 1.2 O que o sistema não é

- Não é apenas um editor de notas.
- Não é apenas um repositório de embeddings.
- Não é um agente autônomo com acesso irrestrito ao vault do usuário.
- Não é um clone de Obsidian.
- Não é um chatbot com “memória” vaga e não auditável.
- Não é um app de research descartável que devolve texto e some com o processo.
- Não é um backend onde a verdade mora no banco vetorial.

## 1.3 Resultado desejado

Criar um sistema onde:

- o usuário mantém soberania sobre seu cérebro externo
- o agente pode aprender e evoluir sem contaminar silenciosamente o conhecimento do usuário
- pesquisas se tornam **jobs rastreáveis**, não prompts efêmeros
- toda mutação relevante é governada por políticas, diffs e auditoria
- o sistema continua útil mesmo sem LLM em vários fluxos-base

---

# 2. Princípios arquiteturais fundamentais

## 2.1 Local-first e filesystem-first

A camada canônica do conhecimento é um conjunto de arquivos reais:

- Markdown
- YAML frontmatter / propriedades
- assets em disco
- estrutura de diretórios clara
- links internos explícitos

Tudo o resto é derivado.

## 2.2 A fonte de verdade nunca é o vetor

Embeddings, chunks, índices, grafos, caches, resumos e memórias derivadas **não são soberanos**.  
Eles são projeções auxiliares da camada canônica.

## 2.3 O usuário e o agente possuem cérebros distintos

- O **User Vault** é o cérebro soberano do usuário.
- O **Agent Brain** é o cérebro privado do agente.
- Entre ambos existe uma **Exchange Zone** de mediação.

## 2.4 Toda travessia de fronteira exige capacidade + política

Nenhum processo escreve em domínio sensível sem:

- capability explícita
- policy check
- logging
- opcionalmente diff, patch e approval

## 2.5 O sistema deve ser útil sem magia

A v1 deve funcionar de maneira pragmática mesmo que:

- o modelo esteja indisponível
- o retrieval esteja desligado
- o crawler não rode
- o agente esteja desativado

Isso significa que o vault, templates, diárias, projetos, estrutura e versionamento devem ter valor intrínseco.

## 2.6 Modularidade lógica, simplicidade operacional

Arquitetura desenhada em domínios separados, porém implantada inicialmente como **modular monolith + workers**, e não como microserviços prematuros.

## 2.7 Patch-first no domínio do usuário

O padrão de mutação do conhecimento canônico do usuário deve ser:

1. ler contexto
2. preparar proposta
3. gerar diff/patch
4. submeter a política / aprovação
5. aplicar ao canônico

Não: “o agente mexe direto na nota e pronto”.

## 2.8 Self-improve livre no domínio do agente

O agente pode aprender, consolidar heurísticas, criar skills e editar a própria memória com liberdade muito maior dentro do **Agent Brain** do que dentro do **User Vault**.

## 2.9 Auditabilidade radical

Toda mutação relevante precisa permitir responder:

- quem fez
- por que fez
- em qual contexto
- com base em quais fontes
- o que mudou
- se foi aprovado
- se foi revertido

---

# 3. Objetivos de produto

## 3.1 Objetivos macro

1. Construir um second brain canônico, flexível e template-driven.
2. Permitir interação de IA com esse second brain sem destruir soberania do usuário.
3. Prover um brain próprio para o agente evoluir.
4. Transformar pesquisa em job rastreável com artefatos reais.
5. Oferecer retrieval híbrido coerente para notas, fontes e memória.
6. Manter tudo self-hosted, leve, modular e progressivamente evolutivo.

## 3.2 Objetivos de v1

- estrutura canônica do vault
- templates-base
- daily notes
- Git + Exchange Zone + patch pipeline
- Policy Engine mínimo
- Agent Brain separado
- núcleo agentic mínimo
- retrieval básico útil
- note copilot local por nota
- research runtime v1
- API/backend Python unificado

## 3.3 Não objetivos da v1

- multi-user maduro
- colaboração em tempo real estilo Google Docs
- mobile app completo
- recomendador inteligente de template profile
- swarm de multiagentes complexo
- autonomia alta em produção sobre o vault do usuário
- plugin profundo de Obsidian como núcleo obrigatório
- marketplace de templates/skills

---

# 4. Modelo conceitual central

## 4.1 Os três domínios primários

### A. User Vault
Cérebro soberano do usuário.

Contém:
- notas canônicas
- diárias
- projetos
- áreas
- recursos
- arquivo
- templates instanciados
- assets
- links internos
- metadados

### B. Agent Brain
Cérebro privado do agente.

Contém:
- identidade operacional (`SOUL.md`)
- memória consolidada (`MEMORY.md`)
- perfil operacional do usuário (`USER.md`)
- skills
- heurísticas
- notas internas
- sessões resumidas
- reflexões
- playbooks

### C. Exchange Zone
Fronteira viva entre domínios.

Contém:
- propostas de notas
- patches pendentes
- relatórios
- sínteses intermediárias
- importações de research
- consolidações temporárias
- rascunhos de ingestão

## 4.2 Domínios secundários

### D. Research Runtime
Subsistema responsável por:
- planejar pesquisas
- coletar fontes
- rastrear jobs
- gerar raw markdown
- sintetizar saídas
- propor ingestão no sistema

### E. Retrieval Layer
Subsistema derivado responsável por:
- busca lexical
- busca semântica
- reranking
- contexto estrutural
- expansão de contexto

### F. Control Plane
Subsistema responsável por:
- auth
- policy
- approvals
- auditoria
- jobs
- observabilidade
- API
- exposição via MCP no futuro

---

# 5. Leis do sistema

## Lei 1 — O User Vault é soberano
Nada pode substituir os arquivos canônicos como fonte final de verdade.

## Lei 2 — O Agent Brain é autônomo, mas não soberano sobre o usuário
O agente evolui dentro do próprio espaço. O espaço do usuário exige fronteiras e regras.

## Lei 3 — A Exchange Zone é obrigatória
Qualquer trabalho intermediário relevante entre agente/crawler e conhecimento do usuário deve passar por um espaço auditável de mediação.

## Lei 4 — Todo derivado é descartável e reconstruível
Índice, embedding, chunk, cache, summary store, note graph derivado: tudo pode ser reconstruído a partir das fontes principais.

## Lei 5 — Policy precede execução
Nenhuma ferramenta decide sozinha se pode escrever.

## Lei 6 — Git é ledger editorial, não cérebro
Git versiona, compara, reverte e sustenta a fronteira. Não substitui policy, jobs, retrieval ou memória semântica.

## Lei 7 — Pesquisa é processo, não prompt
Toda pesquisa relevante vira blueprint + job + artefatos + síntese + possível ingestão.

## Lei 8 — UI abstrai a complexidade operacional
O usuário vê sugestões, diffs, aprovações, jobs e notas — não worktrees, rebase e plumbing interno.

---

# 6. Visão geral da arquitetura

```text
┌──────────────────────────────────────────────────────────────────────┐
│                           CLIENTES / UIs                            │
│ Web App | Chat/Research UI | Note Copilot | Obsidian | CLI | MCP    │
└──────────────────────────────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATION / CONTROL PLANE                  │
│ Auth | Policy | Approval | Job Manager | Audit | API | Events       │
└──────────────────────────────────────────────────────────────────────┘
          │                     │                      │
          ▼                     ▼                      ▼
┌─────────────────┐   ┌──────────────────┐   ┌───────────────────────┐
│   USER VAULT    │   │   AGENT RUNTIME  │   │   RESEARCH RUNTIME    │
│ canonical notes │   │ core + memory    │   │ planner+crawler+synth │
│ templates daily │   │ skills + tools   │   │ raw outputs + ingest  │
└─────────────────┘   └──────────────────┘   └───────────────────────┘
          │                     │                      │
          └──────────────┬──────┴──────────────┬──────┘
                         ▼                     ▼
               ┌──────────────────┐   ┌────────────────────────┐
               │   EXCHANGE ZONE  │   │   RETRIEVAL LAYER      │
               │ worktrees/patches│   │ sparse+dense+rerank    │
               │ proposed changes │   │ graph/context packs    │
               └──────────────────┘   └────────────────────────┘
                         │                     │
                         ▼                     ▼
               ┌──────────────────┐   ┌────────────────────────┐
               │  GIT / REVISION  │   │ POSTGRES + VECTOR DB   │
               │ diff merge apply │   │ jobs chunks metadata   │
               │ history rollback │   │ approvals audit index  │
               └──────────────────┘   └────────────────────────┘
```

---

# 7. Plano físico vs plano lógico

## 7.1 Plano lógico

Domínios internos:

- API Gateway / App API
- Auth Service
- Policy Service
- Approval Service
- Vault Service
- Git Service
- Agent Runtime
- Research Runtime
- Retrieval Service
- Template Service
- Audit / Trace Service
- Event / Job Service

## 7.2 Plano físico recomendado para v1

Implantação como modular monolith + workers:

### Processo 1 — `app-api`
Responsável por:
- endpoints HTTP
- WebSocket / SSE
- auth
- views de job/status
- approval flows
- note copilot session init
- controle dos serviços de domínio

### Processo 2 — `worker-runtime`
Responsável por:
- agent runs
- research jobs
- indexação
- patch compilation
- background maintenance

### Processo 3 — `postgres`
Responsável por:
- dados operacionais
- auditoria
- jobs
- approvals
- projeções de notas
- chunks
- embeddings (se usar pgvector)

### Processo 4 — `vector engine`
Opções:
- `pgvector` embutido no Postgres para v1 simples
- `qdrant` como evolução posterior

### Processo 5 — `crawler sidecar`
Responsável por:
- browser automation
- crawling
- parsing de páginas web dinâmicas

### Processo 6 — `sync sidecar` (opcional)
Responsável por:
- sync local-first entre dispositivos, se adotado

---

# 8. Estrutura de diretórios recomendada

## 8.1 User Vault

```text
user-vault/
  00-Inbox/
  01-Daily/
  02-Projects/
  03-Areas/
  04-Resources/
  05-Archive/
  Templates/
  Attachments/
  _system/
    vault-config.yaml
    schemas/
    template-profiles/
```

## 8.2 Agent Brain

```text
agent-brain/
  SOUL.md
  MEMORY.md
  USER.md
  skills/
  heuristics/
  sessions/
  reflections/
  scratchpads/
  playbooks/
  traces/
```

## 8.3 Exchange Zone

```text
exchange/
  proposals/
  research/
  imports/
  reviews/
```

## 8.4 Raw / Operational Artifacts

```text
raw/
  web/
  documents/
  parsed/
  manifests/
  failed/
```

## 8.5 Runtime / Worktrees

```text
runtime/
  worktrees/
    proposal-note-001/
    research-job-884/
    import-job-991/
```

## 8.6 Repositories

```text
repos/
  user-vault.git
  agent-brain.git
```

---

# 9. Modelo do User Vault

## 9.1 Tipos canônicos de nota

A v1 deve suportar tipos claros de nota:

- `daily`
- `project`
- `area`
- `resource`
- `archive-item`
- `fleeting`
- `permanent`
- `research-note`
- `source-note`
- `synthesis-note`
- `index-note`
- `template-instance`

## 9.2 Estrutura-base de frontmatter

```yaml
id: note-uuid
kind: project
status: active
created_at: 2026-03-31T12:00:00Z
updated_at: 2026-03-31T12:00:00Z
title: Nome da Nota
tags:
  - exemplo
links:
  related: []
  project: null
  area: null
source:
  type: human
  provenance: []
policy:
  sensitivity: normal
  ai_edit_mode: patch_only
```

## 9.3 Convenções

- Toda nota deve ter `id` estável.
- `title` pode mudar; `id` não.
- `kind` define schema esperado.
- `policy.ai_edit_mode` orienta defaults de mutação.
- `source.provenance` registra origens externas relevantes.

## 9.4 Regras de linking

- Links internos devem priorizar referências estáveis da nota.
- Tags não substituem relações estruturais.
- Relações hierárquicas importantes devem existir em metadata e não apenas em texto livre.

---

# 10. Template System

## 10.1 Objetivo

Permitir múltiplos estilos de second brain sem quebrar a base canônica.

## 10.2 O que é um Template Profile

Um **Template Profile** é um conjunto coerente de:

- tipos de nota habilitados
- templates padrão
- convenções de nomes
- convenções de estrutura
- prompts operacionais de assistentes
- políticas default
- automações de criação

## 10.3 Profiles previstos

### A. PARA-like
- projetos
- áreas
- recursos
- arquivo
- forte em organização operacional

### B. Daily-first
- diárias como eixo de captura
- projetos e notas surgem da diária
- forte em fluxo cotidiano

### C. Zettelkasten-like
- atomicidade
- notas permanentes
- linking forte
- densidade conceitual

### D. Research Lab
- source notes
- synthesis notes
- hipóteses
- experiment logs
- revisões bibliográficas

### E. Project OS
- projetos como centro
- decisões, specs, tarefas, logs, reuniões

## 10.4 Política da v1

Na v1, os profiles existem como **packs estáticos selecionáveis**, não como sistema de recomendação inteligente.

---

# 11. Daily Notes

## 11.1 Função

A daily note é a unidade de captura contextual diária.

## 11.2 Capacidades da v1

- criação automática por data
- template selecionável
- seções padrão
- links para projetos/áreas
- entrada rápida
- possibilidade de ingestão posterior pelo agente

## 11.3 Estrutura sugerida

```markdown
# Daily — 2026-03-31

## Inbox

## Focus

## Notes

## Linked Projects

## Decisions

## Learnings

## Tasks

## Review
```

## 11.4 Papel no sistema

A daily note é canônica, mas pode ser enriquecida pelo sistema **apenas conforme policy**.

---

# 12. Agent Brain

## 12.1 Função

Servir como domínio de aprendizado, adaptação, memória e evolução do agente.

## 12.2 Artefatos principais

### `SOUL.md`
Identidade operacional, princípios, estilo, limites e modo-base do agente.

### `MEMORY.md`
Memória consolidada de alto valor.

### `USER.md`
Modelo operacional do usuário:
- preferências persistentes
- padrões úteis
- contexto de trabalho
- restrições recorrentes

### `skills/`
Procedimentos reutilizáveis, instruções compostas e know-how operacional.

### `reflections/`
Reflexões pós-run ou pós-job.

### `sessions/`
Resumos ou índices de sessões anteriores.

## 12.3 Regras

- O agente pode editar o próprio brain com liberdade muito maior.
- Ainda assim, deve haver logging e versionamento adequados.
- Nem toda experiência vira memória permanente.
- Nem todo padrão vira skill.

## 12.4 Curadoria de memória

A consolidação de memória deve seguir critérios como:

- recorrência
- utilidade futura
- estabilidade temporal
- confiabilidade
- impacto operacional

## 12.5 Curadoria de skill

Uma skill só deve ser criada quando houver:

- padrão recorrente
- procedimento reusável
- ganho operacional claro
- manutenção justificável

---

# 13. Exchange Zone

## 13.1 Missão

A Exchange Zone é o espaço auditável de transição entre produção automatizada e conhecimento canônico.

## 13.2 Conteúdos legítimos

- proposta de nova nota
- reestruturação de nota existente
- patch para nota canônica
- relatório gerado pelo agente
- pacote de ingestão de pesquisa
- consolidação temporária de múltiplas notas
- review package

## 13.3 O que não deve virar

- lixeira eterna
- área de arquivos órfãos
- substituto do vault
- cache caótico invisível

## 13.4 Ciclo de vida padrão

1. artefato nasce
2. recebe manifest / metadata
3. gera diff ou proposta legível
4. aguarda política / aprovação
5. é promovido ao canônico ou descartado

---

# 14. Git / Revision Model

## 14.1 Papel do Git

Git fornece:

- histórico
- versionamento
- diff
- patch
- rollback
- branches efêmeras
- worktrees isoladas

Não fornece:

- policy
- auth
- jobs
- retrieval
- memória semântica

## 14.2 Repositórios

### `user-vault.git`
Repo do conhecimento canônico do usuário.

### `agent-brain.git`
Repo opcionalmente separado para o cérebro do agente.

## 14.3 Branches recomendadas

- `main` → canônico aprovado
- `proposal/<agent>/<id>` → proposta do agente
- `research/<job-id>` → saída de pesquisa
- `import/<source>/<ts>` → ingestão
- `review/<id>` → revisão intermediária

## 14.4 Worktrees

Cada trabalho relevante fora do canônico deve poder rodar em worktree própria.

Exemplos:
- `proposal-note-123`
- `research-job-884`
- `import-job-991`

## 14.5 Commits

Commits devem refletir **unidades semânticas**, não autosave bruto.

Exemplos bons:
- `planner: create research blueprint for x`
- `crawler: materialize 12 raw sources`
- `agent: propose restructuring of note y`
- `approval: apply accepted patch for note z`

## 14.6 Patch-first

O padrão de modificação do User Vault deve ser:

- branch/worktree de proposta
- alteração fora de `main`
- diff legível
- patch opcional
- aprovação/policy
- merge/apply

---

# 15. Policy Engine

## 15.1 Função

Decidir se determinado ator pode realizar determinada ação sobre determinado alvo sob determinado contexto.

## 15.2 Entidades

- **Actor**: user, system, agent, crawler, admin
- **Domain**: user_vault, agent_brain, exchange, raw, retrieval
- **Capability**: ação específica
- **Target**: nota, pasta, job, recurso, template
- **Context**: origem, horário, sensibilidade, modo de execução

## 15.3 Exemplo de capabilities

### User Vault
- `vault.read_note`
- `vault.search`
- `vault.create_note`
- `vault.append_note`
- `vault.edit_note`
- `vault.propose_patch`
- `vault.create_folder`
- `vault.rename_note`
- `vault.delete_note`
- `vault.apply_template`
- `vault.create_daily`
- `vault.attach_asset`

### Agent Brain
- `agent.read_memory`
- `agent.write_memory`
- `agent.create_skill`
- `agent.update_skill`
- `agent.read_sessions`

### Research
- `research.create_job`
- `research.fetch_web`
- `research.parse_document`
- `research.materialize_raw`
- `research.propose_ingest`

## 15.4 Resultados possíveis

- `allow_direct`
- `allow_patch_only`
- `allow_in_exchange_only`
- `allow_with_approval`
- `deny`

## 15.5 Política pragmática da v1

A v1 deve suportar ao menos regras por:

- ator
- domínio
- ação
- path/pasta
- tipo de nota
- sensibilidade

## 15.6 Defaults recomendados

### Para o User Vault
- leitura: relativamente ampla
- criação: permitida em áreas seguras
- edição direta: rara
- patch/proposta: padrão
- deletar/mover/renomear: gated

### Para o Agent Brain
- leitura/escrita: muito mais ampla

### Para a Exchange Zone
- criação: ampla para processos autorizados
- promoção ao canônico: sempre controlada

---

# 16. Vault Service

## 16.1 Função

Ser a única camada autorizada a operar diretamente no filesystem canônico do usuário.

## 16.2 Responsabilidades

- criar nota
- atualizar nota
- aplicar patch
- renomear nota
- mover nota
- deletar nota
- aplicar template
- criar daily
- criar anexos
- validar frontmatter
- garantir invariantes de naming/path/schema

## 16.3 Limites

- não decide política
- não gerencia job lifecycle
- não decide memória do agente
- não fala com LLM por conta própria

---

# 17. Git Service

## 17.1 Função

Abstrair Git e worktrees para o resto do sistema.

## 17.2 Responsabilidades

- init/open repo
- create worktree
- create branch
- status
- diff
- patch generation
- commit structured changes
- merge/cherry-pick/apply
- revert/rollback
- cleanup worktrees

## 17.3 Limites

- não decide política
- não entende semântica de nota além do mínimo necessário
- não substitui Approval Engine

---

# 18. Approval Engine

## 18.1 Função

Mediar mudanças sensíveis antes da promoção ao conhecimento canônico.

## 18.2 Entradas típicas

- patch de nota
- criação de nova nota
- reorganização estrutural
- ingestão de research
- alteração de metadata importante

## 18.3 Saídas

- approved
- rejected
- approved_with_edits
- deferred

## 18.4 Tipos de aprovação

- humana explícita
- automática por policy
- semiautomática por confiança/escopo

## 18.5 Interface ideal

O usuário deve ver:
- o que mudou
- por que mudou
- origem da proposta
- arquivos afetados
- resumo da proposta
- aceitar / rejeitar / editar

---

# 19. Audit / Observability

## 19.1 Toda ação relevante gera evento

Campos mínimos:

- `event_id`
- `trace_id`
- `actor`
- `domain`
- `capability`
- `target`
- `result`
- `timestamp`
- `job_id` opcional
- `approval_id` opcional
- `diff_hash` opcional
- `source_refs` opcionais

## 19.2 O que precisa ser observável

- jobs em execução
- tools chamadas pelo agente
- leituras relevantes sobre o vault
- patches gerados
- aprovações pendentes
- skills criadas
- memória consolidada
- falhas de indexação/crawl/merge

## 19.3 Objetivo

Possibilitar confiança, debugging, auditoria e evolução do sistema.

---

# 20. Retrieval Layer

## 20.1 Missão

Fornecer contexto relevante, não apenas chunks aleatórios.

## 20.2 Camadas de recuperação

### A. Estrutural
- tipo de nota
- projeto/área relacionados
- tags
- path
- links internos
- backlinks

### B. Lexical
- FTS/BM25

### C. Semântica
- embeddings por chunk / heading / nota

### D. Rerank
- reordenação dos top resultados

### E. Expansão local
- heading pai
- headings irmãos
- backlinks úteis
- vizinhança de projeto
- diárias adjacentes quando relevante

## 20.3 Unidade de entrega

O retrieval deve retornar **context packs**, não apenas chunks crus.

Um `ContextPack` deve conter, idealmente:

- nota principal
- trecho relevante
- score
- motivo da recuperação
- metadata essencial
- vizinhança expandida opcional
- proveniência
- autorização de acesso

## 20.4 Índices previstos

- `note_index`
- `chunk_index`
- `link_graph_index`
- `tag_projection`
- `provenance_projection`
- `agent_session_projection`

## 20.5 Regra de soberania

Nenhum índice substitui o arquivo canônico.

---

# 21. Chunking e Indexação

## 21.1 Princípios

- chunking guiado por headings quando possível
- notas curtas podem ser indexadas inteiras
- metadata de origem precisa ser preservada
- o índice deve ser incremental e reconstruível

## 21.2 Campos de chunk

```yaml
chunk_id: chunk-uuid
note_id: note-uuid
source_path: 04-Resources/...
heading_path:
  - H1
  - H2
content: texto do chunk
kind: resource
created_at: ...
updated_at: ...
embedding_model: ...
provenance:
  - file://...
```

## 21.3 Política de reindexação

- on write para mudanças pequenas e locais
- batch para rebuilds maiores
- rebuild completo possível e barato o bastante para ser confiável

---

# 22. Research Runtime

## 22.1 Missão

Transformar pedidos de pesquisa em **jobs reais, duráveis, visíveis e auditáveis**.

## 22.2 Pipeline canônico

```text
Pedido do usuário
  → Planner de pesquisa
  → Research Blueprint
  → Job persistido
  → Discovery / fetch
  → Crawl / parse / normalize
  → Deduplicate
  → Chunk / index opcional
  → Synthesis
  → Materialização RAW
  → Pacote de ingestão / proposta
  → Aprovação / promoção
```

## 22.3 Research Blueprint

Campos mínimos:

- `goal`
- `questions`
- `subtopics`
- `scope`
- `allowed_domains`
- `depth`
- `max_sources`
- `language`
- `output_format`
- `citation_policy`
- `raw_materialization_mode`
- `ingest_destination`
- `constraints`

## 22.4 Estados do job

- `queued`
- `planning`
- `discovering`
- `crawling`
- `parsing`
- `deduplicating`
- `synthesizing`
- `materializing`
- `awaiting_approval`
- `completed`
- `failed`
- `partial`
- `canceled`

## 22.5 Outputs do job

Exemplo:

```text
exchange/research/2026-03-31-job-884/
  blueprint.md
  raw/
    source-01.md
    source-02.md
  normalized/
    source-01.json
  synthesis.md
  manifest.yaml
  ingest-proposal.patch
```

## 22.6 Limites do runtime

- não grava silenciosamente no vault canônico
- não decide sozinho promoção ao User Vault
- não substitui retrieval nem memory curation

---

# 23. Raw Archive

## 23.1 Função

Guardar artefatos brutos e normalizados do processo de coleta.

## 23.2 Conteúdos típicos

- markdown bruto de páginas
- extrações de PDF
- documentos normalizados em JSON
- metadados de fontes
- manifestos
- outputs com falha parcial para debugging

## 23.3 Princípio

RAW não é canônico, mas é importante para:
- rastreabilidade
- reprocessamento
- auditoria
- comparação entre síntese e fonte

---

# 24. Agent Runtime

## 24.1 Missão

Executar o núcleo agentic sobre o sistema sem romper suas fronteiras.

## 24.2 Subcamadas

### A. Cognition Layer
- planner
- executor
- reflector
- memory curator
- skill learner

### B. Tool Layer
- vault tool
- retrieval tool
- research tool
- git/patch tool
- policy introspection tool
- template tool

### C. Persistence Layer
- arquivos do agent brain
- sessões
- reflexões
- resumos
- traces

## 24.3 Defaults de autonomia

### Livre em Agent Brain
- criar notas internas
- editar memória
- sintetizar sessões
- promover heurísticas
- criar skills

### Restrito em User Vault
- leitura ampla conforme policy
- criação em áreas seguras
- edição preferencialmente via patch
- aprovação em mutações sensíveis

## 24.4 Reaproveitamento do Hermes

O Hermes pode servir como base conceitual para:
- memória em markdown
- skills persistidas
- busca em sessões
- loop agentic
- reflexão / melhoria incremental

Mas a implementação da v1 deve extrair apenas o núcleo útil, removendo cinquilho de gateway/CLI/integrações não essenciais.

---

# 25. Skills System

## 25.1 Definição

Skill é um procedimento operacional reutilizável, persistido e invocável.

## 25.2 Estrutura sugerida

```text
agent-brain/skills/
  nome-da-skill/
    SKILL.md
    manifest.yaml
    examples/
    assets/
```

## 25.3 Campos do manifest

```yaml
id: skill-uuid
name: nome-da-skill
version: 1
status: active
kind: procedure
triggers:
  - research
  - note_refactor
inputs_schema: ...
outputs_schema: ...
policy_requirements:
  - vault.propose_patch
```

## 25.4 Regra de promoção

Algo só vira skill quando passa de “descoberta útil” para “procedimento reusável”.

---

# 26. Session Memory

## 26.1 Função

Permitir lembrança operacional de interações e execuções anteriores.

## 26.2 Tipos

- memória episódica curta
- resumos de sessão
- índices pesquisáveis
- aprendizagens consolidadas

## 26.3 Regras

- nem toda sessão precisa virar memória consolidada
- sessão é registro operacional; memória é abstração curada

---

# 27. Note Copilot

## 27.1 Missão

Permitir conversar com uma nota específica e agir localmente sobre ela.

## 27.2 Contexto do copilot

- nota atual
- frontmatter
- headings
- backlinks
- links de saída
- notas próximas semanticamente
- contexto de projeto/área
- política da nota

## 27.3 Ações da v1

- explicar a nota
- resumir a nota
- sugerir links internos
- sugerir tags
- sugerir estrutura
- detectar duplicação
- propor split em notas atômicas
- consolidar com nota relacionada
- gerar patch

## 27.4 Regra de UX

O usuário deve distinguir claramente:
- conversa
- sugestão
- mudança proposta

---

# 28. Chat / Research UI

## 28.1 Função

Ser a interface de alto nível para:
- conversa geral
- pesquisa profunda
- status de jobs
- revisão de saídas
- aprovações

## 28.2 Modos principais

### Modo 1 — Conversa geral
- consulta ao vault
- consulta ao agent brain quando permitido
- criação de propostas

### Modo 2 — Pesquisa
- pedido do usuário
- decomposição em blueprint
- job real em andamento
- saída estruturada

### Modo 3 — Aprovação
- revisão de patch
- revisão de ingestão
- promoção ao canônico

---

# 29. Modelagem de banco operacional

## 29.1 Tabelas principais sugeridas

### Core
- `users`
- `actors`
- `sessions`
- `conversation_turns`

### Policy / Auth
- `policies`
- `policy_rules`
- `approvals`
- `approval_items`

### Jobs
- `jobs`
- `job_steps`
- `job_events`

### Git / Review
- `patch_sets`
- `proposals`
- `worktrees`
- `revision_events`

### Retrieval
- `notes_projection`
- `chunks`
- `embeddings`
- `link_edges`
- `source_records`
- `provenance_records`

### Audit
- `audit_logs`
- `trace_spans`

## 29.2 Regra de ouro

O banco guarda o **estado operacional** e projeções consultáveis.  
O filesystem guarda o **conhecimento canônico e artefatos humanos**.

---

# 30. Contratos internos (alto nível)

## 30.1 `VaultService`

Operações principais:
- `read_note(note_id|path)`
- `search_notes(query, filters)`
- `create_note(target_path, template, metadata, content)`
- `update_note(note_id, edit_op)`
- `apply_patch(patch_set_id)`
- `create_daily(date, template_profile)`

## 30.2 `GitService`

Operações principais:
- `create_branch(base, name)`
- `create_worktree(branch, target_dir)`
- `get_diff(ref_a, ref_b)`
- `generate_patch(ref_a, ref_b)`
- `commit(change_set, message)`
- `merge(branch)`
- `cleanup_worktree(id)`

## 30.3 `PolicyService`

Operações principais:
- `evaluate(actor, capability, target, context)`
- `list_effective_permissions(actor, domain)`

## 30.4 `ApprovalService`

Operações principais:
- `create_request(...)`
- `approve(id)`
- `reject(id)`
- `approve_with_edits(id, edited_payload)`

## 30.5 `ResearchService`

Operações principais:
- `plan_research(user_request)`
- `create_job(blueprint)`
- `get_job_status(job_id)`
- `fetch_outputs(job_id)`
- `propose_ingest(job_id)`

## 30.6 `RetrievalService`

Operações principais:
- `search(query, domain_filters, strategy)`
- `expand_context(entity_id)`
- `build_context_pack(results)`

---

# 31. Fluxos canônicos

## 31.1 Fluxo A — criação de nota pelo usuário

1. usuário escolhe template/profile
2. `VaultService` cria nota
3. metadata é validada
4. nota entra no vault
5. indexação incremental opcional

## 31.2 Fluxo B — agente propõe melhoria em nota

1. agente lê nota e contexto local
2. `PolicyService` avalia permissão
3. `GitService` abre worktree de proposta
4. proposta é materializada
5. diff/patch é gerado
6. `ApprovalService` cria solicitação
7. usuário aprova/rejeita/edita
8. se aprovada, merge/apply no canônico
9. reindexação

## 31.3 Fluxo C — self-improve do agente

1. run termina
2. reflector resume aprendizado
3. curator decide destino
4. escreve em `MEMORY.md`, `USER.md` ou `skills/`
5. registra evento e versiona no Agent Brain

## 31.4 Fluxo D — pesquisa profunda

1. usuário pede pesquisa
2. planner gera blueprint
3. job é criado
4. crawler/parser coletam e normalizam
5. raw artifacts são gravados
6. síntese é produzida
7. pacote de ingestão é montado na Exchange Zone
8. aprovação/policy decide promoção
9. resultados aprovados entram no vault
10. índice é atualizado

---

# 32. Segurança e limites

## 32.1 Fronteiras mínimas da v1

- User Vault e Agent Brain separados fisicamente
- mutações sensíveis do User Vault nunca são livres por padrão
- crawler não escreve direto no canônico
- retrieval nunca devolve contexto sem checagem de domínio/política

## 32.2 Riscos principais

- agente poluir o vault do usuário
- Exchange Zone virar lixeira permanente
- excesso de acoplamento entre vault e brain do agente
- dependência excessiva de Obsidian como backend
- Git invadir UX com complexidade operacional
- RAG mascarar inconsistências do sistema canônico

## 32.3 Mitigações

- patch-first
- policy engine
- repos separados
- artefatos intermediários claros
- rebuildability de índices
- auditoria completa

---

# 33. Estratégia de implementação

## 33.1 Ordem correta de construção

1. filesystem canônico
2. schemas e templates
3. Git + Exchange Zone + patch pipeline
4. Policy Engine mínimo
5. backend/API e banco operacional
6. Agent Brain / Hermes-core-lite
7. retrieval básico
8. Note Copilot
9. Research Runtime v1
10. durable jobs / HITL / resumability
11. MCP exposure
12. self-improve avançado
13. onboarding e refinamento de UX

## 33.2 Racional

Essa ordem constrói primeiro:
- soberania do conhecimento
- fronteira de segurança
- mecanismos de mutação auditável

Só depois pluga:
- inteligência
- pesquisa
- exposição por protocolo

---

# 34. Roadmap macro de v1

## Fase 0 — arquitetura e corte de escopo
Saída:
- este SSOT
- decisões congeladas de v1

## Fase 1 — Knowledge Filesystem
Saída:
- estruturas de diretório
- schemas
- templates-base
- daily notes

## Fase 2 — Revision Boundary
Saída:
- Git
- worktrees
- patches
- approvals mínimas

## Fase 3 — Control Plane
Saída:
- FastAPI
- Postgres
- policy mínima
- serviços internos

## Fase 4 — Agent Brain
Saída:
- Hermes-core-lite
- memória markdown
- skills mínimas

## Fase 5 — Retrieval
Saída:
- chunking
- lexical + semantic search
- context packs

## Fase 6 — Note Copilot
Saída:
- conversar com nota
- patch suggestions

## Fase 7 — Research Runtime
Saída:
- blueprint
- jobs
- crawling/parsing/synth
- ingest proposal

## Fase 8 — durabilidade e polish técnico
Saída:
- retries
- checkpoint/resume
- observabilidade forte

## Fase 9 — MCP e integrações externas
Saída:
- servidores MCP estáveis

---

# 35. Decisões tecnológicas recomendadas

## 35.1 Backend / API
- Python
- FastAPI

## 35.2 Persistência operacional
- Postgres

## 35.3 Retrieval v1
- pgvector no próprio Postgres

## 35.4 Retrieval v2 possível
- Qdrant para cenários mais especializados

## 35.5 Crawling
- Crawl4AI

## 35.6 Parsing documental
- Docling

## 35.7 Runtime agentic
- Hermes-core-lite como extração conceitual do Hermes Agent
- PydanticAI como camada moderna de agent tooling e tipagem

## 35.8 Jobs longos / durabilidade
- LangGraph em fluxos que realmente precisem resume/checkpoint/HITL

## 35.9 Versionamento
- Git + worktrees

## 35.10 Cliente principal do vault
- Obsidian como cliente/editor preferencial, não como backend soberano

## 35.11 Sync opcional
- Syncthing ou equivalente local-first

---

# 36. Critérios de qualidade da v1

A v1 é boa se:

1. o vault já é útil sem IA
2. o agente já aprende sem poluir o vault do usuário
3. patches e aprovações funcionam bem
4. uma pesquisa real gera job + raw + síntese + proposta de ingestão
5. retrieval melhora de verdade o trabalho local por nota
6. nenhuma camada derivada sequestra a soberania do filesystem

A v1 falha se:

1. tudo depende do chat
2. o agente escreve silenciosamente no canônico
3. Exchange Zone vira depósito de lixo
4. Git vaza cru para o usuário
5. o sistema exige complexidade operacional de microserviços sem necessidade
6. o RAG vira maquiagem sobre um modelo de dados ruim

---

# 37. Open questions legítimas

Estas decisões ainda podem ser refinadas no PRD, mas não impedem o SSOT.

## 37.1 Multi-user
- a v1 é single-user forte ou multi-user básico?

## 37.2 Agent Brain versionamento
- Git desde o início ou snapshots internos na v1?

## 37.3 Sync
- sync local-first oficial já na v1 ou posterior?

## 37.4 UI nativa vs Obsidian-first
- qual é o peso da UI própria na primeira entrega?

## 37.5 Retrieval avançado
- reranker já na v1 ou depois?

## 37.6 AST-aware editing
- edição por ranges/patch simples ou parser semântico mais sofisticado para markdown?

## 37.7 Plugin/integração Obsidian
- apenas compatibilidade ou plugin dedicado futuro?

---

# 38. Glossário operacional

## User Vault
Filesystem canônico do conhecimento do usuário.

## Agent Brain
Filesystem privado do agente para memória, heurísticas e skills.

## Exchange Zone
Espaço de transição auditável entre produção automatizada e conhecimento canônico.

## Raw Archive
Repositório de artefatos brutos coletados/parsing.

## Context Pack
Unidade de contexto recuperado com conteúdo + metadata + vizinhança + proveniência.

## Research Blueprint
Plano estruturado que transforma pedido do usuário em job executável.

## Proposal Branch
Branch efêmera onde mudanças propostas são materializadas fora de `main`.

## Patch-first
Padrão em que mudanças relevantes são primeiro propostas em diff/patch antes de entrarem no canônico.

## Knowledge OS
Sistema cujo centro é a organização, evolução e interação com um filesystem de conhecimento soberano.

---

# 39. Resumo executivo final

Este projeto deve ser entendido como um **Knowledge OS self-hosted** cujo centro não é o chat nem o agente, mas sim um **filesystem canônico de conhecimento**.  
Sua arquitetura ideal separa:

- **User Vault** como soberano
- **Agent Brain** como autônomo
- **Exchange Zone** como mediação
- **Research Runtime** como fábrica de conhecimento
- **Retrieval Layer** como projeção derivada
- **Policy Engine** como juiz de fronteiras
- **Git** como ledger editorial
- **MCP** como superfície futura de integração

A v1 correta é modular, linear e pragmática:

1. filesystem
2. templates
3. revision boundary
4. policy
5. backend
6. agent brain
7. retrieval
8. note copilot
9. research runtime
10. durability/polish

Se essa ordem for respeitada, o sistema cresce sobre uma base real.  
Se for invertida, ele tende a virar apenas mais um amontoado de IA com arquivos.

---

# 40. Referências técnicas úteis

Estas referências não definem o produto; elas informam decisões de stack e integração.

- Obsidian Help — CLI: https://help.obsidian.md/Plugins/Command+line+interface
- Obsidian Help — Sync notes with other apps: https://help.obsidian.md/Getting+started/Sync+notes+with+other+apps
- Git documentation — worktree: https://git-scm.com/docs/git-worktree
- Git documentation — diff: https://git-scm.com/docs/git-diff
- Model Context Protocol Specification: https://modelcontextprotocol.io/specification/2025-11-25
- MCP Client Features / Sampling: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling
- PydanticAI docs: https://ai.pydantic.dev/
- LangGraph durable execution: https://docs.langchain.com/oss/python/langgraph/durable-execution
- Crawl4AI repository: https://github.com/unclecode/crawl4ai
- Docling documentation: https://docling-project.github.io/docling/
- pgvector repository: https://github.com/pgvector/pgvector
- FastAPI docs: https://fastapi.tiangolo.com/
- Syncthing: https://syncthing.net/
- Hermes Agent repository: https://github.com/NousResearch/hermes-agent

