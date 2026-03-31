# PRD — Knowledge OS Core OSS v1
## Product Requirements Document do núcleo open source
### Knowledge OS self-hosted, local-first, agent-aware, policy-driven

**Status:** Draft fundador v2  
**Escopo:** núcleo open source do produto  
**Idioma:** pt-BR  
**Tipo:** PRD técnico-executável  
**Objetivo:** especificar, de forma completa, pragmática, modular e implementável, o núcleo do produto que será disponibilizado open source e que também servirá como base estrutural da futura camada cloud gerenciada.

---

# 0. Meta do documento

Este PRD existe para transformar o SSOT arquitetural em **produto construível**.

Ele não é um manifesto, nem um brainstorm, nem apenas uma visão de alto nível.  
Ele deve responder, com clareza suficiente para implementação:

- o que é o core open source
- o que ele resolve
- quais são seus limites
- quais são seus domínios formais
- como esses domínios se relacionam
- quais módulos existem
- quais contratos internos devem ser respeitados
- como o sistema deve ser construído em ordem lógica
- quais fluxos devem existir na v1
- quais decisões estão travadas
- o que explicitamente não entra na v1
- como o core open source deve nascer de modo compatível com futura camada cloud sem ser contaminado por pressupostos de SaaS

Este documento assume como base as leis arquiteturais do projeto: o **filesystem canônico é soberano**, o **Agent Brain é separado**, a **Exchange Zone é obrigatória**, todo índice e RAG é **derivado e secundário**, e toda travessia entre domínios deve passar por **capabilities + policy + auditoria**. fileciteturn2file2

---

# 1. Tese do produto

## 1.1 O problema estrutural

Ferramentas atuais de notas, chat com IA, RAG, memória de agente e pesquisa costumam quebrar exatamente porque misturam camadas que deveriam ser separadas:

- conhecimento canônico do usuário
- memória operacional privada do agente
- saídas intermediárias geradas automaticamente
- artefatos de pesquisa e ingestão
- índices derivados
- automações de execução
- estado operacional de jobs e aprovações

Quando essas camadas se confundem, acontecem os problemas clássicos:

1. o agente escreve onde não deveria  
2. o vault do usuário vira depósito de lixo automatizado  
3. o RAG começa a substituir a verdade canônica  
4. pesquisa vira resposta efêmera de chat em vez de job rastreável  
5. Git vira detalhe cosmético em vez de ledger editorial  
6. não há distinção real entre proposta, rascunho, memória e conhecimento aprovado  
7. o produto parece “mágico” mas se torna impossível de confiar, auditar e evoluir

## 1.2 A resposta do produto

O produto responde a isso com uma tese simples:

> o centro do sistema não é o chat, nem o agente, nem o vetor, nem a UI.  
> o centro do sistema é um **filesystem canônico de conhecimento**, com fronteiras formais entre humano, agente, trabalho intermediário e camadas derivadas.

Esse centro se organiza em:

- **User Vault** → conhecimento soberano do usuário
- **Agent Brain** → memória, heurísticas, skills e identidade do agente
- **Exchange Zone** → fronteira auditável entre produção automatizada e conhecimento canônico
- **Research Runtime** → fábrica de conhecimento rastreável
- **Retrieval Layer** → projeção derivada para recuperar contexto útil
- **Policy Engine** → juiz das travessias
- **Git/Revision Layer** → ledger editorial da fronteira

## 1.3 Resultado desejado

Criar um núcleo open source que permita:

- um second brain real, estruturado e útil mesmo sem IA
- um agente com memória própria, que aprende sem poluir o vault do usuário
- propostas de mudança sempre rastreáveis, revisáveis e reversíveis
- pesquisas profundas que geram **blueprint + job + raw + síntese + ingestão proposta**
- retrieval útil que nunca substitui o conhecimento canônico
- uma base arquitetural portável que possa ser usada:
  - localmente
  - self-hosted
  - como foundation da camada cloud
  - como substrate para MCP e integrações futuras

---

# 2. Definição do produto

## 2.1 O que o core open source é

O core open source é um **Knowledge OS backend + runtime + UI base** que implementa:

- filesystem-first knowledge management
- templates e tipos formais de nota
- daily notes
- projects / areas / resources / archive
- versionamento e revisão com Git + worktrees + patch pipeline
- agent brain persistente em Markdown
- note copilot orientado a patch
- retrieval híbrido derivado
- research runtime com jobs reais
- policy engine centrado em capabilities
- approval flows
- observabilidade e auditoria mínimas
- backend Python modular
- implantação self-hosted simples
- superfície futura para MCP

## 2.2 O que ele não é

O core open source **não é**:

- uma plataforma SaaS
- um serviço de billing de IA
- uma solução enterprise de compliance
- um clone visual de Obsidian
- um chat wrapper sobre embeddings
- um agente autônomo com acesso irrestrito ao filesystem
- um sistema de workflow genérico
- uma plataforma de automação semântica para qualquer coisa
- um produto já otimizado para multi-tenant cloud
- um conjunto de microserviços

## 2.3 Definição resumida

> Um Knowledge OS self-hosted, local-first, modular e agent-aware, cujo núcleo é um vault canônico em Markdown protegido por políticas, mediação editorial e uma separação formal entre memória do usuário, memória do agente, artefatos intermediários e camadas derivadas.

---

# 3. Princípios do produto

## 3.1 Filesystem-first
A camada canônica existe em arquivos reais, legíveis e auditáveis:
- Markdown
- YAML frontmatter
- assets em disco
- diretórios explícitos
- links internos

## 3.2 Local-first
O produto deve funcionar bem em cenários self-hosted e single-machine.

## 3.3 User Vault soberano
O User Vault é a verdade canônica do usuário.

## 3.4 Agent Brain separado
O agente deve possuir seu próprio domínio persistente, com memória, skills, heurísticas e reflexões.

## 3.5 Exchange Zone obrigatória
Toda mutação relevante produzida por processos automatizados deve passar por uma zona de transição auditável.

## 3.6 Policy before execution
Nenhuma ferramenta decide sozinha se pode mutar domínio sensível.

## 3.7 Patch-first
No domínio do usuário, o padrão é propor antes de aplicar.

## 3.8 Retrieval derivado
Chunks, embeddings, grafos, projections e resumos são auxiliares, não soberanos.

## 3.9 Useful before magical
A v1 deve ser valiosa mesmo sem LLM em vários fluxos.

## 3.10 Modularidade lógica, simplicidade operacional
Arquitetura desenhada em domínios separados, implantada inicialmente como modular monolith + workers, não como microservices. fileciteturn2file2

---

# 4. Objetivos do produto

## 4.1 Objetivo primário
Entregar um núcleo open source funcional, modular e confiável que sirva como fundação do ecossistema Knowledge OS.

## 4.2 Objetivos secundários
- provar que o filesystem soberano é o centro correto da arquitetura
- provar que User Vault e Agent Brain precisam ser distintos
- provar que patch-first + approval é superior a escrita silenciosa por IA
- provar que pesquisa deve virar job e artefato, não chat efêmero
- provar que retrieval útil pode ser derivado sem sequestrar a verdade
- criar base técnica clara para futura camada cloud

## 4.3 Objetivos da v1
A v1 precisa cobrir, de ponta a ponta:

1. **Knowledge Filesystem**
2. **Template System**
3. **Daily Notes**
4. **Git + Exchange Zone + Patch Pipeline**
5. **Policy Engine mínimo**
6. **Backend/API Python**
7. **Agent Brain mínimo**
8. **Retrieval básico útil**
9. **Note Copilot**
10. **Research Runtime v1**

## 4.4 Não objetivos da v1
- onboarding inteligente de template profiles
- recomendador de setup
- plugin complexo de Obsidian
- mobile app
- colaboração em tempo real
- multi-user maduro
- enterprise controls
- swarm de agentes
- marketplace de skills/templates
- MCP público completo
- autonomia agressiva sobre o User Vault

---

# 5. Usuários-alvo

## 5.1 Usuário principal
Power user técnico / founder / pesquisador / builder que quer:
- soberania dos próprios arquivos
- IA útil sem caos
- notes + knowledge + research + memory num sistema coerente
- self-host ou pelo menos portabilidade real

## 5.2 Usuário secundário
Operador de conhecimento de times pequenos:
- pesquisa
- documentação
- aprendizado contínuo
- memória organizacional inicial

## 5.3 Usuário terciário
Desenvolvedor / contributor open source:
- quer entender e estender o core
- quer rodar localmente
- quer integrar via MCP depois
- quer aproveitar módulos isolados

---

# 6. Visão macro da arquitetura

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

# 7. Os cinco domínios centrais

## 7.1 User Vault

### Função
Ser o cérebro soberano, canônico, humano e auditável do usuário.

### Contém
- notas canônicas
- daily notes
- projects
- areas
- resources
- archive
- templates instanciados
- anexos/assets referenciados
- links internos
- metadata/frontmatter

### Não contém
- filas de jobs
- embeddings
- chunks
- estado operacional do agente
- caches
- artefatos efêmeros de execução
- lixo de pesquisa não aprovado

### Princípio
Nada substitui o User Vault como fonte de verdade.

---

## 7.2 Agent Brain

### Função
Ser o cérebro privado, persistente e evolutivo do agente.

### Contém
- `SOUL.md`
- `MEMORY.md`
- `USER.md`
- skills
- heuristics
- reflections
- sessions
- scratchpads
- playbooks
- traces resumidas

### Pode fazer
- evoluir
- consolidar aprendizados
- criar skills
- editar a própria memória
- guardar preferências inferidas do usuário

### Não pode por padrão
- se confundir com o User Vault
- promover automaticamente suas conclusões ao canônico
- escrever silenciosamente no domínio do usuário

---

## 7.3 Exchange Zone

### Função
Ser a fronteira viva entre geração automatizada e conhecimento canônico.

### Contém
- propostas de nova nota
- patches pendentes
- diffs
- relatórios
- outputs de research
- consolidações temporárias
- bundles de revisão
- pacotes de ingestão

### Regra
Nada significativo vindo de agente/crawler deve pular essa zona quando seu destino potencial for o canônico.

### Anti-padrões
- virar lixeira eterna
- virar substituto do vault
- guardar tudo para sempre sem curadoria

---

## 7.4 Research Runtime

### Função
Transformar pedidos de pesquisa em jobs duráveis e observáveis.

### Executa
- planning
- blueprint generation
- source discovery
- crawl/fetch
- parse/normalize
- deduplicate
- synthesis
- raw materialization
- ingest proposal

### Regra
Pesquisa é processo, não prompt. fileciteturn2file2

---

## 7.5 Retrieval Layer

### Função
Recuperar contexto útil sobre:
- User Vault
- Exchange Zone
- Raw artifacts
- Agent Brain quando autorizado
- relações estruturais

### Regra
É uma projeção derivada, jamais soberana.

---

# 8. Plano lógico vs plano físico

## 8.1 Plano lógico
Contextos internos:
- API / Gateway
- Vault Service
- Git Service
- Template Service
- Policy Service
- Approval Service
- Audit Service
- Agent Runtime
- Research Runtime
- Retrieval Service
- Job Service

## 8.2 Plano físico v1
A v1 não deve rodar como 10 serviços independentes.

### Processos recomendados
1. `app-api`
2. `worker-runtime`
3. `postgres`
4. `vector engine` (pgvector no próprio Postgres ou Qdrant depois)
5. `crawler sidecar`
6. `optional sync sidecar`

### Estilo de implantação
**Modular monolith + workers**

---

# 9. Roadmap embutido no produto

A ordem de construção é parte do design, não detalhe de gestão.

## 9.1 Ordem correta
1. filesystem canônico
2. schemas e templates
3. Git + Exchange Zone + patch pipeline
4. Policy Engine mínimo
5. backend/API e banco operacional
6. Agent Brain / Hermes-core-lite
7. retrieval básico
8. Note Copilot
9. Research Runtime v1
10. durable jobs / resumability / HITL
11. MCP exposure
12. self-improve avançado
13. onboarding e polish

## 9.2 Racional
Essa ordem constrói primeiro:
- soberania do conhecimento
- fronteira de segurança
- mecanismos de mutação auditável

Só depois pluga:
- inteligência
- pesquisa
- exposição por protocolo fileciteturn2file4

---

# 10. Escopo do core open source

## 10.1 O que entra no core OSS v1
- User Vault
- Agent Brain
- Exchange Zone
- Git/patch/revision
- policy baseline
- approvals
- retrieval básico
- Note Copilot
- Research Runtime v1
- backend/API
- worker
- UI base
- deployment self-hosted
- extensão futura via MCP

## 10.2 O que fica fora
- billing
- créditos de IA hospedada
- multi-tenant cloud ops
- enterprise controls
- SSO/SAML
- analytics comerciais
- administração SaaS
- colaboração real-time madura
- cloud-only features

---

# 11. Estrutura de diretórios do sistema

## 11.1 Layout recomendado

```text
knowledge-os/
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

  exchange/
    proposals/
    research/
    imports/
    reviews/

  raw/
    web/
    documents/
    parsed/
    manifests/
    failed/

  runtime/
    worktrees/
      proposal-note-001/
      research-job-884/
      import-job-991/
    temp/

  repos/
    user-vault.git
    agent-brain.git

  app/
  worker/
  infra/
  scripts/
```

## 11.2 Regra de ouro
`exchange/` e `raw/` ficam **fora** do vault canônico.  
O que é canônico entra no `user-vault/`.  
O que é transitório, operacional, revisável ou bruto fica fora. fileciteturn2file2

---

# 12. User Vault Design

## 12.1 Objetivo
Ser um sistema de conhecimento coerente antes mesmo da IA.

## 12.2 Tipos-base de nota
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

## 12.3 Estrutura mínima de frontmatter

```yaml
id: note-uuid
kind: project
status: active
created_at: 2026-03-31T12:00:00Z
updated_at: 2026-03-31T12:00:00Z
title: Nome da Nota
tags: []
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

## 12.4 Invariantes
- toda nota tem `id` estável
- `kind` define schema esperado
- metadata importante não deve depender só do corpo do Markdown
- `policy.ai_edit_mode` orienta defaults de mutação
- `source.provenance` registra origem relevante quando aplicável

## 12.5 Daily Notes
A v1 deve suportar:
- criação automática
- template selecionável
- links para projetos/áreas
- enriquecimento posterior por proposta
- valor intrínseco mesmo sem IA

---

# 13. Template System

## 13.1 Objetivo
Permitir diferentes estilos de second brain sem quebrar a base canônica.

## 13.2 Template Profile
Um profile é um conjunto coerente de:
- tipos de nota
- templates
- convenções
- defaults de estrutura
- defaults de policy
- comportamento operacional inicial

## 13.3 Profiles previstos
- PARA-like
- Daily-first
- Zettelkasten-like
- Research Lab
- Project OS

## 13.4 Escopo da v1
Profiles estáticos, selecionáveis, não recomendados por IA.

## 13.5 Templates mínimos da v1
- daily
- project
- area
- resource
- fleeting
- permanent
- source note
- synthesis note
- research brief

---

# 14. Git / Revision Model

## 14.1 Papel do Git
Git é:
- ledger editorial
- versionador
- diff generator
- patch substrate
- rollback mechanism

Git não é:
- policy engine
- job queue
- retrieval engine
- operational DB
- memória semântica

## 14.2 Repositórios
- `user-vault.git`
- `agent-brain.git` (separado ou snapshots equivalentes na v1, mas conceitualmente separado)

## 14.3 Branches do User Vault
- `main`
- `proposal/<actor>/<id>`
- `research/<job-id>`
- `import/<source>/<ts>`
- `review/<id>`

## 14.4 Worktrees
Cada proposta relevante deve poder abrir worktree dedicada.

Exemplos:
- `proposal-note-123`
- `research-job-884`
- `import-job-991`

## 14.5 Fluxo padrão
1. job/processo cria worktree
2. muta arquivos fora de `main`
3. gera diff/patch
4. Approval Engine decide
5. merge/cherry-pick/apply no canônico
6. reindexa
7. fecha worktree

## 14.6 Regra de UX
O usuário não deve ser forçado a pensar em plumbing Git.  
Ele vê:
- proposta
- diff
- resumo
- aceitar / rejeitar / editar

---

# 15. Exchange Zone Design

## 15.1 Definição
Espaço auditável de mediação.

## 15.2 Conteúdos legítimos
- proposed note
- note patch
- review bundle
- report
- ingest package
- consolidation draft
- synthesis candidate

## 15.3 Estados possíveis
- draft
- generated
- awaiting_review
- approved
- rejected
- applied
- superseded
- failed

## 15.4 Regras
- tudo que entra precisa de metadata
- propostas precisam apontar alvo
- bundles precisam de origem
- artefatos envelhecidos precisam de política de limpeza/arquivamento
- a zona não pode virar a fonte definitiva de verdade

---

# 16. Policy Engine

## 16.1 Definição
Componente central que decide travessias de fronteira.

## 16.2 Capability model

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

### Exchange
- `exchange.create_bundle`
- `exchange.review_bundle`
- `exchange.apply_bundle`

## 16.3 Resultados possíveis
- `allow_direct`
- `allow_patch_only`
- `allow_in_exchange_only`
- `allow_with_approval`
- `deny`

## 16.4 Dimensões avaliáveis
- ator
- domínio
- capability
- alvo
- path
- tipo de nota
- sensibilidade
- origem da chamada
- modo de execução

## 16.5 Defaults da v1
### User Vault
- leitura ampla
- criação apenas em áreas seguras ou conforme regra
- edição direta rara
- patch-first por padrão
- delete/move/rename gated

### Agent Brain
- leitura/escrita muito mais ampla

### Exchange
- criação mais liberal
- promoção ao canônico sempre controlada

## 16.6 Regra estrutural
Nada escreve em lugar sensível sem policy check. fileciteturn2file4

---

# 17. Services de filesystem

## 17.1 VaultService
Única camada autorizada a mutar o User Vault.

### Responsabilidades
- criar nota
- editar nota
- aplicar patch
- mover/renomear
- criar daily
- aplicar template
- adicionar links/tags
- anexar asset
- validar invariantes

### Não faz
- decisão de policy
- orquestração de jobs
- IA embutida por conta própria

## 17.2 GitService
Abstrai revision and worktrees.

### Responsabilidades
- init/open repo
- create branch
- create worktree
- commit changes
- diff
- patch
- merge/cherry-pick/apply
- rollback
- cleanup

### Não faz
- decisão semântica
- policy
- approvals

## 17.3 WorkspaceMaterializer
Cria espaços físicos temporários.

### Responsabilidades
- worktrees de proposal
- worktrees de research
- worktrees de import

### Não faz
- interpretar conteúdo
- decidir autorização

---

# 18. Modelagem operacional de dados

## 18.1 Camadas de dados
### A. canônica em arquivo
- `Note`
- `Template`
- `DailyNote`
- `Skill`
- `ResearchArtifact`
- `RawSourceMarkdown`
- `BlueprintMarkdown`
- `SynthesisMarkdown`
- `PatchBundle`

### B. operacional em banco
- `User`
- `Actor`
- `Workspace`
- `PolicyRule`
- `ApprovalRequest`
- `Proposal`
- `PatchSet`
- `Job`
- `JobStep`
- `JobEvent`
- `AuditLog`
- `Chunk`
- `EmbeddingRef`
- `LinkEdge`
- `SourceRecord`
- `ProvenanceRecord`
- `NoteProjection`
- `Session`
- `ConversationTurn`

## 18.2 Regra
Arquivo = humano/auditável/canônico  
Banco = operacional/consultável/derivado

---

# 19. Banco operacional

## 19.1 Tabelas principais

### `workspaces`
- id
- name
- slug
- created_at
- updated_at

### `actors`
- id
- workspace_id
- type (`user`, `agent`, `system`, `crawler`)
- display_name
- created_at

### `notes_projection`
- id
- workspace_id
- canonical_path
- note_type
- title
- status
- created_at
- updated_at
- checksum
- last_indexed_at

### `policy_rules`
- id
- workspace_id
- actor_selector
- capability
- path_pattern
- note_type
- outcome
- priority
- enabled
- created_at

### `proposals`
- id
- workspace_id
- proposal_type
- source_domain
- target_domain
- status
- branch_name
- worktree_path
- patch_path
- summary
- created_by_actor_id
- created_at
- updated_at

### `approvals`
- id
- workspace_id
- proposal_id
- status
- requested_by_actor_id
- reviewed_by_actor_id
- created_at
- reviewed_at
- comment

### `jobs`
- id
- workspace_id
- job_type
- status
- priority
- payload_json
- attempt_count
- max_attempts
- available_at
- claimed_at
- completed_at
- error_message

### `job_events`
- id
- job_id
- event_type
- payload_json
- created_at

### `chunks`
- id
- workspace_id
- note_projection_id
- domain
- chunk_text
- chunk_index
- token_estimate
- metadata_json

### `embeddings`
- id
- chunk_id
- embedding
- model_name
- created_at

### `artifacts`
- id
- workspace_id
- domain
- artifact_type
- path
- source_url
- checksum
- metadata_json
- created_at

### `audit_logs`
- id
- workspace_id
- actor_id
- action
- target_type
- target_ref
- decision
- metadata_json
- created_at

---

# 20. Backend Architecture

## 20.1 Estilo
**Modular monolith** com fronteiras explícitas.

## 20.2 Módulos internos
- `auth`
- `vault`
- `templates`
- `gitops`
- `exchange`
- `policy`
- `approvals`
- `retrieval`
- `agent`
- `research`
- `jobs`
- `audit`
- `admin`

## 20.3 Regras de arquitetura interna
- nenhum módulo acessa filesystem “na mão” fora dos services corretos
- nenhum módulo muta canon sem policy
- nenhum módulo gera estado operacional crítico fora do Postgres
- toda integração pesada roda em worker quando apropriado
- toda fronteira sensível gera auditoria

## 20.4 Runtime físico v1
- `app-api` (FastAPI)
- `worker-runtime`
- `postgres`
- `pgvector`
- `crawler sidecar`

---

# 21. API Design

## 21.1 Estilo
REST-first, com WebSocket/SSE opcional para jobs e status.

## 21.2 Grupos principais
- `/auth/*`
- `/vault/*`
- `/templates/*`
- `/retrieval/*`
- `/copilot/*`
- `/exchange/*`
- `/approvals/*`
- `/research/*`
- `/jobs/*`
- `/policy/*`
- `/admin/*`

## 21.3 Endpoints de referência

### Vault
- `GET /vault/notes`
- `GET /vault/note/{id}`
- `POST /vault/note`
- `PATCH /vault/note/{id}`
- `POST /vault/daily`
- `POST /vault/template/apply`

### Retrieval
- `POST /retrieval/search`
- `POST /retrieval/context-pack`

### Copilot
- `POST /copilot/note/{id}/ask`
- `POST /copilot/note/{id}/suggest-links`
- `POST /copilot/note/{id}/propose-cleanup`

### Exchange
- `GET /exchange/proposals`
- `GET /exchange/proposal/{id}`
- `POST /exchange/proposal/{id}/approve`
- `POST /exchange/proposal/{id}/reject`

### Research
- `POST /research/jobs`
- `GET /research/job/{id}`
- `GET /research/job/{id}/artifacts`
- `POST /research/job/{id}/propose-ingest`

### Policy
- `GET /policy/rules`
- `POST /policy/rules`
- `POST /policy/check`

---

# 22. Jobs Architecture

## 22.1 Por que existe
API não deve bloquear com:
- indexação
- crawling
- parsing
- embeddings
- synthesis
- patch bundle generation
- memory consolidation

## 22.2 Tipos de job
- `index_note`
- `reindex_scope`
- `generate_embeddings`
- `research_job`
- `parse_source`
- `apply_patch_bundle`
- `reflect_agent`
- `consolidate_memory`

## 22.3 Modelo v1
Fila em Postgres com row claiming.

## 22.4 Estados
- queued
- claimed
- running
- awaiting_approval
- completed
- failed
- partial
- canceled

---

# 23. Retrieval Layer Design

## 23.1 Missão
Recuperar contexto útil, não apenas texto parecido.

## 23.2 Camadas
1. estrutural
2. lexical
3. semântica
4. rerank
5. expansão local

## 23.3 Estratégias
### estrutural
- path
- type
- tags
- backlinks
- project/area adjacency

### lexical
- FTS/BM25

### semântica
- embeddings por chunk / heading / nota

### rerank
- opcional v1 simples

### local context expansion
- heading pai
- sibling headings
- linked notes
- daily/project local
- metadata

## 23.4 Unidade de saída
`ContextPack`

### `ContextPack` ideal
- nota principal
- trecho relevante
- score
- por que veio
- metadados
- vizinhança
- proveniência
- autorização de domínio

## 23.5 Regra central
Retrieval é auxiliar.  
A decisão final sempre remonta ao arquivo canônico.

---

# 24. Chunking e indexação

## 24.1 Princípios
- chunking guiado por headings quando possível
- notas pequenas podem ser indexadas inteiras
- preserve provenance
- incremental by default
- rebuild completo sempre possível

## 24.2 Pipeline
filesystem change  
→ projection refresh  
→ chunking  
→ lexical index  
→ embeddings  
→ retrieval metadata update

## 24.3 Domínios indexáveis
- User Vault
- Exchange Zone
- Raw artifacts
- Agent Brain (opcional e privado)

## 24.4 v1 default
- User Vault indexado
- Exchange/Raw como secundários
- Agent Brain indexado só quando fizer sentido e com escopo privado

---

# 25. Agent Runtime

## 25.1 Objetivo
Executar o núcleo agentic respeitando fronteiras.

## 25.2 Subcamadas

### A. Cognition
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

### C. Persistence
- arquivos do Agent Brain
- sessões
- traces
- resumos

## 25.3 Defaults de autonomia
### Livre no Agent Brain
- pensar
- planejar
- aprender
- consolidar heurísticas
- criar skills
- editar a própria memória

### Restrito no User Vault
- ler conforme policy
- criar notas apenas em áreas seguras / via regras
- editar via patch
- promoção ao canônico via aprovação/policy

## 25.4 Hermes-core-lite
A v1 deve tratar o Hermes como **base conceitual e extração seletiva**, não como dependência integral.

Reaproveitar conceitualmente:
- loop agentic
- memória em `.md`
- busca em sessões
- skills
- reflexão

Remover:
- cinquilho de gateway
- integrações não essenciais
- superfícies não centrais ao core

---

# 26. Skills System

## 26.1 Definição
Skill = procedimento operacional reutilizável, persistido e invocável.

## 26.2 Estrutura sugerida

```text
agent-brain/skills/
  nome-da-skill/
    SKILL.md
    manifest.yaml
    examples/
    assets/
```

## 26.3 Campos do manifest
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

## 26.4 Regra de promoção
Uma descoberta só vira skill quando:
- é recorrente
- é útil
- é reusável
- compensa custo de manutenção

---

# 27. Session Memory e reflexão

## 27.1 Tipos de memória
- episódica curta
- resumo de sessão
- memória consolidada
- skill
- preferência do usuário

## 27.2 Regra
Sessão ≠ memória consolidada  
Reflexão ≠ promoção automática  
Descoberta útil ≠ skill

## 27.3 Fluxo de self-improve
run termina  
→ reflector resume  
→ curator decide destino  
→ escreve em `MEMORY.md`, `USER.md` ou `skills/`  
→ registra evento  
→ sem mutação do User Vault por padrão fileciteturn2file4

---

# 28. Note Copilot

## 28.1 Definição
Miniagente local por nota.

## 28.2 Inputs
- nota atual
- frontmatter
- headings
- links de saída
- backlinks
- notas semanticamente próximas
- contexto de projeto/área
- policy da nota

## 28.3 Ações v1
- explicar
- resumir
- sugerir links internos
- sugerir tags
- sugerir estrutura
- detectar duplicação
- propor split
- consolidar
- gerar patch

## 28.4 Regra de UX
Distinguir claramente:
- conversa
- sugestão
- proposta de mudança

## 28.5 Regra de mutação
Nada de edição silenciosa.

---

# 29. Research Runtime

## 29.1 Missão
Transformar pedidos de pesquisa em jobs rastreáveis, visíveis e úteis.

## 29.2 Pipeline canônico

```text
Pedido do usuário
  → Research Planner
  → Research Blueprint
  → Job persistido
  → Discovery / fetch
  → Crawl / parse / normalize
  → Deduplicate
  → Synthesis
  → Materialização RAW
  → Ingest Package / Proposal
  → Aprovação / promoção
```

## 29.3 Research Blueprint
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

## 29.4 Outputs
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

## 29.5 Regras
- raw deve existir
- synthesis deve ser rastreável
- promoção ao canônico nunca é implícita
- pesquisa profunda é job, não resposta única de chat

---

# 30. Observabilidade e auditoria

## 30.1 Todo evento relevante gera registro
Campos mínimos:
- event_id
- trace_id
- actor
- capability
- domain
- target
- result
- timestamp
- job_id opcional
- approval_id opcional
- diff_hash opcional
- provenance opcional

## 30.2 Deve ser observável
- timeline do job
- tools chamadas
- arquivos lidos
- arquivos propostos
- patch gerado
- status da aprovação
- o que virou memória do agente
- o que virou conhecimento canônico

## 30.3 Objetivo
Confiabilidade, debugging, auditoria, evolução segura.

---

# 31. Segurança

## 31.1 Fronteiras mínimas
- User Vault e Agent Brain separados fisicamente
- mutações sensíveis do User Vault nunca livres por padrão
- crawler não escreve direto no canônico
- retrieval não contorna policy
- path traversal protection
- sandboxing de parsing/crawler quando possível

## 31.2 Operações sensíveis
- canonical note edit
- move/rename/delete
- approval application
- ingest proposal apply
- policy change
- agent permission elevation

## 31.3 Requisitos
- policy gate
- audit log
- diff visibility quando aplicável
- rollback razoável

---

# 32. Performance e limites da v1

## 32.1 Assunções
- single-user forte
- um ou poucos workspaces
- milhares ou dezenas de milhares de notas, não milhões
- workload de research moderado
- uso local/self-hosted em máquina ou VPS modesta

## 32.2 Alvos qualitativos
- opening de nota interativo
- busca lexical quase instantânea
- busca semântica aceitável
- patch generation interativa na maioria dos casos
- jobs pesados sempre assíncronos

## 32.3 Princípios
- não bloquear API em embeddings
- não reindexar o mundo por qualquer mudança
- privilegiar reindex incremental
- batch para tarefas caras
- rebuild completo sempre possível

---

# 33. MCP na arquitetura

## 33.1 Papel
MCP é superfície futura de exposição, não o núcleo do sistema.

## 33.2 Só entra depois
MCP só depois que:
- contratos internos estiverem claros
- policy estiver estável
- módulos principais já existirem

## 33.3 Servidores previstos
- `vault-user-mcp`
- `agent-brain-mcp`
- `research-mcp`
- `retrieval-mcp`

## 33.4 Regra
Nenhum servidor MCP pode criar caminho secreto fora da API/policy.

---

# 34. Implantação recomendada do core OSS

## 34.1 Topologia mínima
- API
- worker
- Postgres
- filesystem local
- Git
- opcional crawler sidecar

## 34.2 Compatibilidade
O core deve ser compatível com:
- Linux local
- VPS única
- docker-compose
- desenvolvimento em máquina pessoal

## 34.3 Princípio
A v1 precisa ser fácil de rodar e entender.

---

# 35. MVP Definition

O MVP do core open source está completo quando um usuário consegue:

1. inicializar um workspace
2. criar e gerir um User Vault canônico em Markdown
3. usar templates e daily notes
4. abrir, editar e navegar notas
5. fazer busca lexical e semântica útil
6. usar Note Copilot em uma nota específica
7. receber propostas em patch/diff, não edição silenciosa
8. revisar e aplicar uma proposta pela Exchange Zone
9. permitir que o agente atualize seu Agent Brain
10. executar uma pesquisa simples que gere:
   - blueprint
   - raw sources
   - synthesis
   - proposta de ingestão
11. auditar ações sensíveis

Se esses 11 pontos forem verdadeiros, o core é real.

---

# 36. Escopo detalhado do MVP

## 36.1 Must-have
- workspace bootstrap
- vault structure
- note CRUD
- templates
- daily notes
- markdown editor + preview
- repo + worktree management
- patch pipeline
- approvals básicas
- policy engine mínimo
- backend Python
- Postgres metadata
- lexical retrieval
- semantic retrieval
- context packs básicos
- Agent Brain persistence
- Note Copilot básico
- research runtime simples
- audit logs
- self-host docs

## 36.2 Should-have
- backlinks panel
- proposal summaries
- source manifest UI
- simple policy UI
- simple workspace config UI

## 36.3 Could-have
- partial patch application
- markdown AST transforms
- richer template profiles
- better reranking
- multiple agent personas

## 36.4 Won’t-have
- real-time collaboration
- full multi-user
- org billing
- enterprise controls
- swarm agents
- mobile apps
- rich ecosystem of integrations

---

# 37. Sequência exata de implementação

## Fase 0 — Architecture freeze
**Entregáveis**
- `ARCHITECTURE.md`
- decisões congeladas da v1
- layout de diretórios
- invariantes dos domínios

**Done quando**
- fontes de verdade estão claras
- fronteiras estão claras
- ordem de construção está clara

---

## Fase 1 — Knowledge Filesystem
**Objetivo**
Ter um sistema canônico útil sem IA.

**Construir**
- `user-vault/`
- `agent-brain/`
- `exchange/`
- `raw/`
- schemas
- template profiles estáticos
- templates-base
- daily notes

**Done quando**
- o vault funciona “burro”
- daily notes e templates existem
- links e metadata são coerentes

---

## Fase 2 — Revision Boundary
**Objetivo**
Transformar mudanças em artefatos auditáveis.

**Construir**
- Git repo
- worktrees
- branches de proposal/research/import
- diff
- patch
- apply/merge
- rollback
- Exchange Zone

**Done quando**
- qualquer mudança relevante pode virar proposal
- diff é legível
- apply/reject funciona

---

## Fase 3 — Policy Engine
**Objetivo**
Nada escreve onde não deve.

**Construir**
- capability model
- policy evaluator
- defaults seguros
- integração com VaultService/GitService

**Done quando**
- toda mutação sensível passa por policy
- agent write no User Vault é controlado

---

## Fase 4 — Backend/API
**Objetivo**
Centralizar contratos e estado operacional.

**Construir**
- FastAPI
- módulos internos
- Postgres
- jobs simples
- audit logs
- websockets/SSE básicos

**Done quando**
- toda operação relevante passa pela API e services
- filesystem não é mexido “solto”

---

## Fase 5 — Agent Brain / Hermes-core-lite
**Objetivo**
Plugar o agente sem romper a arquitetura.

**Construir**
- Agent Brain
- context builder
- planner/executor/reflector
- memory curator
- skill manager
- tool layer mínima

**Done quando**
- agente aprende no próprio brain
- agente lê o User Vault
- agente só propõe mudanças conforme policy

---

## Fase 6 — Retrieval
**Objetivo**
Recuperar contexto útil sobre conhecimento real já existente.

**Construir**
- projection refresh
- chunking
- FTS/BM25
- embeddings
- hybrid retrieval básico
- context pack builder

**Done quando**
- busca lexical funciona
- busca semântica funciona
- Note Copilot consegue consumir context packs

---

## Fase 7 — Note Copilot
**Objetivo**
Entregar a primeira magia real sem quebrar soberania.

**Construir**
- painel local por nota
- ask/explain/summarize
- suggest links/tags/structure
- proposal generation

**Done quando**
- usuário conversa com nota
- sistema sugere melhorias úteis
- toda mudança vira proposal

---

## Fase 8 — Research Runtime
**Objetivo**
Transformar pesquisa em job real.

**Construir**
- research brief
- planner
- blueprint
- job pipeline
- raw materialization
- synthesis
- ingest proposal

**Done quando**
- pedido vira job
- job produz raw + synthesis + proposal
- promotion continua controlada

---

## Fase 9 — Durabilidade e HITL
**Objetivo**
Suportar jobs mais longos e robustos.

**Construir**
- retries
- checkpoint/resume
- interrupts
- approval-aware execution
- idempotência

**Done quando**
- jobs podem pausar/retomar
- approvals não quebram pipeline

---

## Fase 10 — MCP
**Objetivo**
Expor o core de forma padronizada.

**Construir**
- servidores MCP por domínio
- mapping para tools/resources/roots
- enforcement de policy

**Done quando**
- clientes MCP conseguem operar o sistema sem bypass

---

# 38. Critérios de qualidade da v1

## 38.1 A v1 é boa se
1. o vault já é útil sem IA
2. o agente aprende sem poluir o vault
3. patches e approvals funcionam
4. pesquisa real gera job + raw + síntese + proposta de ingestão
5. retrieval melhora de verdade o trabalho local por nota
6. nenhuma camada derivada sequestra a soberania do filesystem

## 38.2 A v1 falha se
1. tudo depende do chat
2. o agente escreve silenciosamente no canônico
3. Exchange Zone vira depósito de lixo
4. Git vaza cru para o usuário
5. a arquitetura exige microservices sem necessidade
6. o RAG vira maquiagem sobre um modelo ruim fileciteturn2file3

---

# 39. Testes necessários

## 39.1 Unit
- VaultService
- GitService
- PolicyService
- ApprovalService
- RetrievalService
- Agent memory curation
- Research blueprint compilation

## 39.2 Integração
- note create/edit/read
- daily generation
- proposal lifecycle
- denied policy path
- agent memory write allowed + vault write denied
- indexing after note change
- research job end-to-end
- rollback after failed apply

## 39.3 E2E
- user creates workspace
- creates project note
- uses note copilot
- receives proposal
- approves patch
- runs research job
- sees synthesis and ingest proposal

---

# 40. Riscos principais

## 40.1 Produto
- complexidade demais antes de valor
- UX ruim na Exchange Zone
- confusão entre User Vault e Agent Brain
- pesquisa parecer lenta demais sem boa visualização de job

## 40.2 Técnico
- edge cases de Git/worktree
- chunking ruim gerar retrieval ruim
- policy bug causar mutação indevida
- crawler/parser instáveis
- Agent Brain crescer sem curadoria

## 40.3 OSS
- self-host difícil demais
- arquitetura opaca para contributors
- núcleo fraco demais para adoção
- acoplamento implícito com a futura cloud

---

# 41. Decisões travadas da v1

1. Markdown é canônico  
2. User Vault e Agent Brain são separados  
3. Exchange Zone é obrigatória  
4. Patch-first é o padrão no domínio do usuário  
5. Git é ledger editorial  
6. Postgres é banco operacional  
7. Retrieval é derivado  
8. Research é job, não prompt  
9. MCP vem depois  
10. Modular monolith é a arquitetura inicial  
11. Cloud concerns não podem corromper o core OSS

---

# 42. Open questions legítimas

- Agent Brain com Git desde o início ou snapshots internos?
- Plugin de Obsidian entra cedo ou só compatibilidade?
- Partial patch application entra na v1 ou v1.1?
- Qdrant fica fora totalmente da v1?
- UI própria pesa mais do que Obsidian-compatible no primeiro release?
- Multi-user básico entra na v1.1 ou v2?
- AST-aware markdown editing vale o custo cedo?

---

# 43. Frase organizadora final

> O Knowledge OS Core não é um chat com memória e nem um app de notas com IA colada.  
> Ele é um sistema cujo centro é um filesystem canônico de conhecimento, protegido por fronteiras formais entre humano, agente, trabalho intermediário e camadas derivadas.

Se essa lei for respeitada:
- o produto cresce direito
- a cloud nasce sobre base sólida
- o open source mantém valor real
- o agente pode evoluir sem sequestrar o sistema

Se essa lei for quebrada:
- tudo degrada para “mais uma IA com arquivos”

---

# 44. Resumo executivo final do PRD

O core open source da Knowledge OS v1 deve nascer como:

- **User Vault soberano**
- **Agent Brain separado**
- **Exchange Zone auditável**
- **Git + patch pipeline**
- **Policy Engine mínimo mas real**
- **backend Python modular**
- **retrieval básico útil**
- **Note Copilot local**
- **Research Runtime v1**
- **MCP apenas depois dos contratos internos**

E a ordem de construção não é negociável:
1. filesystem
2. templates
3. revision boundary
4. policy
5. backend
6. agent brain
7. retrieval
8. note copilot
9. research runtime
10. durability
11. MCP

Esse é o núcleo.
Esse é o produto open source.
E essa é a fundação correta da futura camada cloud.
