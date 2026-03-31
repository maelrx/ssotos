# STACK DECISION RECORD / TECHNICAL ARCHITECTURE CHOICES
## Knowledge OS Core OSS v1
### Documento técnico de decisões de stack, frameworks, bibliotecas e tradeoffs

**Status:** Draft fundador v1  
**Idioma:** pt-BR  
**Escopo:** núcleo open source do produto  
**Objetivo:** definir, de forma técnica, profunda, pragmática e modular, a stack recomendada para cada componente da arquitetura do Knowledge OS Core, incluindo alternativas viáveis, tradeoffs e recomendações finais alinhadas aos requisitos mínimos já estabelecidos.

---

# 0. Como ler este documento

Este documento não é uma lista de “ferramentas populares”.
Ele é um **stack decision record** do produto.

Para cada camada relevante, o documento responde:

1. **qual problema aquela camada precisa resolver**
2. **quais opções viáveis existem**
3. **quais tradeoffs importam no contexto do produto**
4. **qual recomendação técnica senior eu faria**
5. **o que explicitamente deve ser adiado**
6. **qual é a escolha recomendada para a v1**
7. **o que pode mudar na v2/v3 sem rasgar a arquitetura**

---

# 1. Requisitos e restrições que governam a stack

Antes de escolher frameworks, precisamos lembrar que este produto já tem restrições estruturais fortes.

## 1.1 Requisitos centrais do produto

O sistema precisa ser:

- self-hosted
- local-first
- filesystem-first
- agent-aware
- policy-driven
- patch-first no domínio do usuário
- modular logic / simple ops
- útil sem magia
- compatível com futura camada cloud
- amigável a solo founder

## 1.2 Leis arquiteturais que a stack não pode violar

1. **User Vault é soberano**
2. **Agent Brain é separado**
3. **Exchange Zone é obrigatória**
4. **retrieval é derivado**
5. **Research Runtime é job real**
6. **policy precede mutação**
7. **Git é ledger editorial**
8. **MCP é superfície futura, não barramento interno**
9. **a v1 é modular monolith + workers, não microservices**

Se uma tecnologia conflita com essas leis, ela está errada para este produto, mesmo que seja excelente em outro contexto.

## 1.3 Restrições operacionais reais

- solo founder / time muito pequeno
- preferência por Python no backend
- necessidade de rodar em máquina local ou VPS simples
- necessidade de manter custo baixo
- necessidade de manter entendimento do sistema alto
- necessidade de facilitar contribuição open source
- necessidade de evitar “infra theater”

---

# 2. Critérios de decisão

Toda escolha aqui é filtrada pelos seguintes critérios:

## 2.1 Critérios prioritários
- clareza arquitetural
- simplicidade operacional
- boa ergonomia para domínio stateful
- boa aderência a filesystem + Git
- extensibilidade
- baixa chance de lock-in conceitual
- facilidade de debugging
- portabilidade
- custo cognitivo aceitável
- compatibilidade com futura cloud sem cloud-first contamination

## 2.2 Critérios secundários
- performance boa o suficiente
- comunidade
- documentação
- ecossistema
- DX
- maturidade

## 2.3 Critérios que não governam a v1
- hype
- benchmark isolado
- “é o que todo mundo usa”
- features enterprise que ainda não importam
- sofisticação prematura

---

# 3. Visão de stack recomendada (resumo executivo)

Se eu tivesse que congelar a stack hoje para construir a v1 do core open source, eu faria assim:

## 3.1 Backend / runtime
- **Python**
- **FastAPI**
- **Pydantic v2**
- **SQLAlchemy 2**
- **Alembic**
- **Psycopg 3**
- **Postgres**
- **pgvector**
- **worker custom com fila em Postgres**
- **LangGraph apenas nos fluxos que realmente precisem durable execution/HITL**
- **PydanticAI para o agent runtime**
- **Git CLI do sistema operacional**
- **Crawl4AI + Playwright para crawling**
- **Docling para parsing documental**
- **structlog + OpenTelemetry**
- **uv + Ruff + pytest**

## 3.2 Frontend
- **TypeScript**
- **React**
- **Vite**
- **React Router**
- **TanStack Query**
- **Zustand**
- **CodeMirror 6**
- **react-markdown + remark-gfm + rehype-sanitize**
- **Tailwind CSS**
- **Playwright para E2E**

## 3.3 Ops / packaging
- **Docker Compose**
- **Caddy**
- **filesystem local**
- **S3-compatible storage adapter opcional depois**
- **Syncthing opcional, fora do core**

## 3.4 Arquitetura
- **modular monolith + worker + postgres + crawler sidecar**
- **nada de microservices na v1**
- **nada de Kubernetes**
- **nada de managed vector DB no core OSS**
- **nada de broker extra se Postgres resolver**

Essa é a resposta curta.  
O resto do documento explica o porquê.

---

# 4. Linguagem principal do backend

## 4.1 Opções reais
- Python
- TypeScript/Node
- Go
- Rust
- Elixir
- JVM (Kotlin/Java)

## 4.2 Requisitos dessa camada
O backend precisa lidar bem com:
- API web
- jobs
- orchestrators
- LLM tooling
- parsing
- retrieval
- filesystem
- Git
- processos externos
- ergonomia rápida
- comunidade AI forte

## 4.3 Tradeoffs

### Python
**Prós**
- ecossistema mais forte para LLM/agents/research hoje
- excelente ergonomia para parsing, pipelines e workers
- ótima aderência com Pydantic/FastAPI
- enorme disponibilidade de libs para RAG, embeddings, parsing, crawling e ciência de dados
- ideal para solo founder iterar rápido

**Contras**
- concorrência CPU-bound pior que Go/Rust
- exige disciplina para não virar bagunça
- type-safety menos rígida que Rust/TS

### TypeScript/Node
**Prós**
- ótimo ecossistema web
- unificação frontend/backend
- bom para MCP servers e integrações JS-heavy
- DX forte

**Contras**
- menos natural para parsing, pipelines e tooling AI stateful complexo
- filesystem + jobs + agentes long-running podem ficar mais chatos de manter
- ecossistema AI bom, mas ainda menos coeso para esse tipo de produto do que Python

### Go
**Prós**
- concorrência excelente
- simplicidade operacional
- deploy muito sólido

**Contras**
- ecossistema AI/agent/research menos ergonômico
- DX para esse produto é mais lenta
- Markdown/templating/query + LLM tooling tendem a demandar mais trabalho

### Rust
**Prós**
- performance excelente
- segurança forte
- ótimo para componentes pontuais de alto desempenho

**Contras**
- custo cognitivo muito alto para solo founder
- velocidade de iteração pior para v1
- overkill para o centro do produto

## 4.4 Recomendação
**Python**.

## 4.5 Justificativa técnica
O coração do produto não é throughput bruto; é coordenação de conhecimento, tooling de IA, parsing, retrieval, Git, jobs e domínio stateful. Python te dá a melhor relação entre:
- velocidade de desenvolvimento
- disponibilidade de ecossistema
- facilidade para integrar LLMs
- qualidade da stack para workflows e serviços stateful

---

# 5. Backend web framework

## 5.1 Opções principais
- FastAPI
- Django + DRF / Django Ninja
- Litestar
- Flask + extensões
- Starlette puro

## 5.2 O que o framework precisa fazer
- API HTTP
- OpenAPI
- WebSocket/SSE
- type hints reais
- boa integração com Pydantic
- bom para modular monolith
- não atrapalhar workers/processos externos
- manter custo cognitivo baixo

## 5.3 Tradeoffs

### FastAPI
**Prós**
- API-first
- tipagem natural
- integração excelente com Pydantic
- OpenAPI automático
- WebSockets e BackgroundTasks nativos
- ótimo para modular monolith Python
- DX excelente para backend de produto/serviço citeturn147720search8turn147720search12

**Contras**
- não te dá “baterias” de auth/admin/ORM como Django
- precisa disciplina arquitetural para crescer bem

### Django
**Prós**
- maturidade enorme
- admin pronto
- ORM integrado
- auth pronta

**Contras**
- mais framework-first do que domain-first
- pode empurrar o projeto para um shape mais CRUD/monolithic-webapp do que service-platform
- menos elegante para agent/runtime/research/job-centered product

### Litestar
**Prós**
- bom desempenho
- design moderno
- typed

**Contras**
- ecossistema e adoção menores
- menos “boring and proven” que FastAPI para o tipo de contribuição OSS que você quer

## 5.4 Recomendação
**FastAPI**.

## 5.5 Como usar
- REST-first
- WebSocket ou SSE para jobs/status
- sem BackgroundTasks para trabalho pesado; isso fica no worker
- modularizar por bounded contexts

## 5.6 Decisão v1
**FastAPI** como framework do `app-api`.

---

# 6. Schema, validação e settings

## 6.1 Opções
- Pydantic v2
- dataclasses + marshmallow
- attrs + cattrs
- msgspec
- TypedDict na mão

## 6.2 O que precisamos
- schemas de API
- validação interna
- contratos entre módulos
- config/settings
- integração com agent tools
- serialização previsível

## 6.3 Tradeoffs

### Pydantic v2
**Prós**
- padrão de fato em APIs Python modernas
- integração natural com FastAPI
- excelente DX
- ótimo para contratos internos
- excelente para tool schemas com PydanticAI

**Contras**
- overhead se usado de forma excessiva em todos os loops internos
- precisa evitar “Pydantic everywhere” em hot paths

### msgspec
**Prós**
- muito rápido

**Contras**
- menos natural como espinha dorsal do ecossistema que estamos montando

## 6.4 Recomendação
**Pydantic v2** para:
- API layer
- settings
- command objects
- DTOs entre módulos
- tool schemas
- policy decision payloads

Usar classes/domínio mais simples por baixo quando fizer sentido.

---

# 7. ORM, queries e migrations

## 7.1 Opções
- SQLAlchemy 2 + Alembic
- SQLModel
- Django ORM
- Tortoise ORM
- raw SQL / psycopg-only
- Piccolo / Pony / outros menores

## 7.2 O que o produto exige
- modelagem relacional séria
- migrations controladas
- queries customizadas
- projeções e índices
- jobs queue em banco
- auditoria
- integrações com pgvector

## 7.3 Tradeoffs

### SQLAlchemy 2
**Prós**
- extremamente maduro
- ORM e Core fortes
- te deixa ir de ORM para SQL explícito quando necessário
- ótimo para sistema stateful sério
- bom fit com Postgres e domínio rico citeturn999872search0turn999872search8turn999872search12

**Contras**
- mais verboso
- curva maior que ORMs mágicos

### SQLModel
**Prós**
- mais simples para CRUD rápido

**Contras**
- pode ficar limitante em domínio mais sofisticado
- menos confortável quando o modelo relacional fica mais sério

### raw SQL only
**Prós**
- controle total
- performance previsível

**Contras**
- vira custo enorme de manutenção cedo demais
- desacelera o projeto

## 7.4 Migrations
**Alembic** é a escolha correta para schema migrations em cima do SQLAlchemy. citeturn999872search1turn999872search5

## 7.5 Driver
**Psycopg 3** é a recomendação. Ele oferece interface moderna, suporte async e recursos de PostgreSQL mais atuais. citeturn999872search6turn999872search10

## 7.6 Recomendação
- **SQLAlchemy 2**
- **Alembic**
- **Psycopg 3**

## 7.7 Decisão v1
Esse trio é a base do banco operacional.

---

# 8. Banco de dados operacional

## 8.1 Opções
- PostgreSQL
- SQLite
- MySQL/MariaDB
- DuckDB
- MongoDB
- Neo4j

## 8.2 O que precisamos
- transações confiáveis
- joins
- filtros complexos
- jobs
- auditoria
- notas projection
- retrieval metadata
- pgvector
- FTS
- extensões maduras

## 8.3 Tradeoffs

### PostgreSQL
**Prós**
- melhor banco geral para esse produto
- relacional, robusto, maduro
- ótimo suporte a JSONB quando necessário
- suporta pgvector
- suporta FTS nativo
- excelente para jobs e auditoria

**Contras**
- mais pesado que SQLite
- exige operação mínima

### SQLite
**Prós**
- muito simples
- ótimo para protótipos locais

**Contras**
- fica pequeno cedo para esse domínio
- menos confortável para concorrência, jobs, extensões e retrieval híbrido sério

### Neo4j
**Prós**
- grafo explícito

**Contras**
- overkill
- introduz outro banco cedo demais
- relações do produto podem ser modeladas em Postgres na v1

## 8.4 Recomendação
**PostgreSQL**.

## 8.5 Decisão v1
- banco operacional único
- Postgres como source of operational truth
- sem banco extra de grafo na v1

---

# 9. Vector layer / semantic retrieval

## 9.1 Opções
- pgvector
- Qdrant
- Weaviate
- Milvus
- LanceDB
- sqlite-vec

## 9.2 O que precisamos
- retrieval útil
- simplicidade operacional
- boa integração com Postgres
- manter a stack enxuta
- hybrid retrieval viável
- rebuild simples

## 9.3 Tradeoffs

### pgvector
**Prós**
- vetores com o resto dos dados
- exato e aproximado
- bom enough para v1
- zero serviço extra
- encaixa com “arquivo canônico + banco operacional único” citeturn588464search2

**Contras**
- não é a melhor escolha para escala muito alta ou retrieval muito sofisticado

### Qdrant
**Prós**
- excelente motor dedicado
- forte para hybrid search e reranking
- bom caminho quando retrieval vira subsystem mais pesado citeturn588464search3turn588464search11turn588464search14

**Contras**
- mais um serviço
- mais operação
- mais moving parts cedo

### sqlite-vec / LanceDB
**Prós**
- leves

**Contras**
- menos alinhados ao banco operacional central da v1

## 9.4 Recomendação
**pgvector** na v1.  
**Qdrant** só quando a camada de retrieval realmente pedir separação.

## 9.5 Decisão v1
- Postgres + pgvector
- hybrid retrieval simples com FTS + vector + heurísticas
- reranking plugável depois

---

# 10. Busca lexical

## 10.1 Opções
- PostgreSQL FTS
- Meilisearch
- OpenSearch/Elasticsearch
- Tantivy wrappers
- Whoosh

## 10.2 Requisitos
- buscar títulos, corpos, headings, tags e paths
- simplicidade operacional
- integração com projeções
- custo baixo de manutenção

## 10.3 Recomendação
**PostgreSQL FTS** primeiro.

## 10.4 Justificativa
Como o sistema já usa Postgres e a v1 precisa de simplicidade, o ganho de adicionar Meilisearch ou OpenSearch cedo não compensa o custo operacional.  
A busca lexical da v1 deve nascer dentro do Postgres e só sair dele quando houver evidência real de necessidade.

## 10.5 Decisão v1
- PostgreSQL FTS
- opcionalmente `pg_trgm` para fuzzy title/path search
- sem motor externo dedicado de texto na v1

---

# 11. Fila de jobs e background execution

## 11.1 Opções
- fila em Postgres custom
- Celery + Redis/RabbitMQ
- Dramatiq
- Arq
- RQ
- Temporal
- Prefect

## 11.2 O que o produto precisa
- jobs assíncronos
- retries
- claim seguro
- simplicidade de operação
- integração com Postgres
- observabilidade razoável
- não depender de broker extra cedo

## 11.3 Tradeoffs

### Fila custom em Postgres
**Prós**
- zero infra extra
- transacional
- muito boa para v1
- combina com modular monolith + worker
- dá para fazer com `FOR UPDATE SKIP LOCKED`

**Contras**
- você precisa implementar um pouco mais
- não é ideal para escala muito alta

### Celery
**Prós**
- maduro
- poderoso

**Contras**
- pesado
- puxa Redis/Rabbit
- muito boilerplate e custo operacional para esse estágio

### Dramatiq / Arq
**Prós**
- mais leves

**Contras**
- ainda introduzem broker cedo
- o ganho não compensa na v1

### Temporal / Prefect
**Prós**
- workflows fortes

**Contras**
- complexidade desnecessária cedo
- ótimo para outro estágio

## 11.4 Recomendação
**fila em Postgres + worker custom**.

## 11.5 Decisão v1
- jobs em tabela
- worker polling/claiming
- retries simples
- event log por job

---

# 12. Durable workflows / long-running jobs

## 12.1 Opções
- LangGraph
- Temporal
- Prefect
- engine própria
- não ter nada além de jobs simples

## 12.2 O que realmente precisamos
A maior parte da v1 **não** precisa de uma engine de workflow sofisticada.  
Mas algumas áreas podem precisar:
- research jobs longos
- human-in-the-loop
- checkpoints
- resume
- stateful agent runs

## 12.3 Tradeoffs

### LangGraph
**Prós**
- durabilidade
- checkpoints
- HITL
- memória/statefulness
- ótimo encaixe com fluxos agentic long-running citeturn147720search2turn147720search6turn147720search20turn147720search23

**Contras**
- se usado demais, vira complexidade desnecessária
- não deve dominar a arquitetura inteira

### Temporal
**Prós**
- muito robusto

**Contras**
- pesado demais para v1
- custo operacional alto

### Prefect
**Prós**
- bom para pipelines

**Contras**
- menos necessário que LangGraph para a parte agentic/HITL

## 12.4 Recomendação
**Não usar LangGraph como espinha dorsal do sistema inteiro.**  
Usar **LangGraph apenas onde durable execution e HITL realmente tragam valor**:
- research runtime avançado
- jobs longos com pausa/aprovação
- runs agentic stateful

## 12.5 Decisão v1
- fila simples como padrão
- LangGraph opcional em subfluxos específicos depois da base estar pronta

---

# 13. Agent framework / LLM orchestration

## 13.1 Opções
- PydanticAI
- LangChain Agents
- Semantic Kernel
- LlamaIndex Agents
- puro SDK
- Hermes extraído + ferramentas próprias

## 13.2 O que o produto precisa
- tool calling
- contracts tipados
- ergonomia Python
- model/provider agnostic enough
- boa integração com Pydantic
- controle fino
- não sequestrar a arquitetura inteira

## 13.3 Tradeoffs

### PydanticAI
**Prós**
- model-agnostic
- tools e dependency injection bem alinhados ao ecossistema Python
- muito bom para agentes de produção com contratos tipados citeturn147720search1turn147720search5turn147720search13

**Contras**
- menos “ecosystem gravity” que LangChain
- não substitui sozinho uma workflow engine

### LangChain Agents
**Prós**
- ecossistema enorme
- muitas integrações

**Contras**
- abstração mais invasiva
- mais chance de acoplar demais o projeto ao framework
- risco de over-abstraction cedo

### puro SDK
**Prós**
- controle total

**Contras**
- muito trabalho repetido
- piora ergonomia de tools e schemas

## 13.4 Recomendação
**PydanticAI** para o agent runtime do core.

## 13.5 Papel do Hermes
O Hermes entra como:
- referência conceitual
- possível fonte de extração do core agentic
- base de design para `SOUL.md`, `MEMORY.md`, `USER.md`, skills e reflexão

Mas **não** como framework total do produto.

## 13.6 Decisão v1
- `Hermes-core-lite` conceitual
- `PydanticAI` como camada principal de ferramentas e execução agentic
- direct provider adapters onde fizer sentido

---

# 14. LLM provider abstraction

## 14.1 Opções
- PydanticAI providers
- LiteLLM
- abstração própria
- provider SDK direto em todo lugar

## 14.2 Requisitos
- BYOK-friendly
- não prender a um vendor
- tool calling
- structured outputs
- facilidade de troca
- baixo risco de dependência frágil

## 14.3 Recomendação
Para o core OSS, eu faria:

- **PydanticAI como abstração principal de agent calls**
- **adapter próprio pequeno** para embeddings / summarization / utility models
- evitar que o sistema inteiro dependa de uma camada universal única demais

## 14.4 Observação técnica importante
Crawl4AI recentemente destacou um hotfix de segurança trocando uma dependência de LiteLLM por um fork próprio devido a comprometimento da cadeia de supply no PyPI. Isso não condena toda abstração universal, mas é um bom lembrete de que esse tipo de dependência deve ser tratado com cautela em componentes críticos. citeturn588464search0

## 14.5 Decisão v1
- evitar LiteLLM como dependency central crítica do core
- usar PydanticAI + adapters próprios enxutos

---

# 15. Git integration strategy

## 15.1 Opções
- shell out para Git CLI
- GitPython
- dulwich
- pygit2 / libgit2

## 15.2 O que precisamos
- worktrees
- branches
- diff
- patch
- merge/cherry-pick
- rollback
- comportamento previsível
- máxima compatibilidade

## 15.3 Tradeoffs

### Git CLI
**Prós**
- compatibilidade total
- worktree support maduro
- comportamento idêntico ao Git real
- menor risco de edge cases esquisitos

**Contras**
- precisa lidar com subprocess
- parser de saída deve ser disciplinado

### GitPython / dulwich / pygit2
**Prós**
- abstração em Python

**Contras**
- podem ficar atrás da superfície mais moderna do Git
- worktree e detalhes específicos podem ser mais chatos
- menos “boring” que usar o CLI real

## 15.4 Recomendação
**Use o Git CLI do sistema operacional** por meio de um `GitService` bem encapsulado.

## 15.5 Decisão v1
- shell out disciplinado
- comandos explícitos
- nada de espalhar `subprocess.run(["git"...])` pelo código

---

# 16. Crawler stack

## 16.1 Opções
- Crawl4AI + Playwright
- Playwright puro
- Firecrawl OSS
- Browsertrix / custom scraping stack
- requests + bs4 só

## 16.2 O que o produto precisa
- web → Markdown limpo
- controle
- navegadores reais quando necessário
- bom fit com pipelines de research
- materialização de raw artifacts
- suporte a jobs

## 16.3 Tradeoffs

### Crawl4AI
**Prós**
- feito explicitamente para transformar web em Markdown LLM-ready
- alinhado a agentes, RAG e pipelines
- já evoluiu com browser pool e resume_state/history em releases recentes citeturn588464search0turn588464search8

**Contras**
- superfície de dependências relativamente pesada
- precisa pinning e revisão cuidadosa

### Playwright puro
**Prós**
- controle máximo
- ótimo para páginas dinâmicas

**Contras**
- você precisará montar muita lógica que Crawl4AI já resolve

## 16.4 Recomendação
**Crawl4AI + Playwright**.

## 16.5 Decisão v1
- crawler sidecar
- raw markdown obrigatório
- parser posterior separado

---

# 17. Document parsing stack

## 17.1 Opções
- Docling
- Unstructured
- Apache Tika
- PDFMiner + libs específicas por formato
- LlamaParse (não OSS-first)

## 17.2 O que o produto precisa
- PDFs
- DOCX
- PPTX
- XLSX
- HTML
- Markdown output
- JSON lossless output
- self-host
- bom fit com artefatos e ingestão

## 17.3 Tradeoffs

### Docling
**Prós**
- suporta muitos formatos
- exporta Markdown e JSON
- tem modelo de documento unificado
- fortíssimo para pipelines de research e ingestão citeturn588464search1turn588464search5turn588464search12turn588464search15

**Contras**
- stack de parsing/document understanding mais pesada
- precisa testes reais com teus documentos

### Unstructured
**Prós**
- conhecido no ecossistema

**Contras**
- para este produto, Docling hoje parece mais alinhado à necessidade de outputs Markdown/JSON estruturados

## 17.4 Recomendação
**Docling**.

## 17.5 Decisão v1
- Docling como parser padrão
- interface de parser abstrata para permitir troca depois

---

# 18. Frontend application framework

## 18.1 Opções
- React + Vite SPA
- Next.js
- Remix
- SvelteKit
- Vue/Nuxt

## 18.2 O que o produto precisa
- app autenticado
- editor pesado
- UI state complexa
- jobs/status
- painéis laterais
- diff/review
- não depende de SSR para SEO
- integração limpa com API separada

## 18.3 Tradeoffs

### React + Vite
**Prós**
- rápido para desenvolver
- ótimo para SPA autenticada
- excelente ecossistema de editor, state, query, UI libs
- separa bem frontend do backend de domínio
- Vite é extremamente rápido para dev/build moderno citeturn411871search0turn411871search4turn411871search16

**Contras**
- menos “full-stack by default” que Next
- você precisa montar algumas decisões explicitamente

### Next.js
**Prós**
- SSR/ISR/route handlers
- ecossistema enorme

**Contras**
- tende a puxar a arquitetura para “backend no frontend”
- para este produto, o backend Python é central
- aumenta a chance de espalhar lógica em dois lugares

## 18.4 Recomendação
**React + Vite + TypeScript**.

## 18.5 Decisão v1
- SPA autenticada
- backend claramente separado
- marketing site, se existir, pode até usar outra stack depois sem contaminar o core

---

# 19. Frontend routing

## 19.1 Opções
- React Router
- TanStack Router
- file-based router de framework full-stack

## 19.2 Recomendação
**React Router** na v1.

## 19.3 Justificativa
React Router é boring, conhecido e suficiente.
TanStack Router é interessante e type-safe, mas não é o gargalo do produto.
Para um core OSS que precisa onboarding fácil, eu prefiro reduzir exotismo.

## 19.4 Decisão v1
- React Router

---

# 20. Server-state e cache no frontend

## 20.1 Opções
- TanStack Query
- SWR
- Apollo
- RTK Query
- fetch manual

## 20.2 O que precisamos
- server state
- polling de jobs
- invalidation previsível
- optimistic updates moderados
- cache decente

## 20.3 Tradeoffs

### TanStack Query
**Prós**
- padrão fortíssimo para server state
- ótimo para cache, invalidation e polling
- encaixa muito bem em SPA de produto/console operacional citeturn411871search3turn411871search7turn411871search15

**Contras**
- precisa disciplina de query keys e invalidation

## 20.4 Recomendação
**TanStack Query**.

## 20.5 Decisão v1
- queries para notes, proposals, jobs, research outputs
- polling ou websocket harmonizados com Query cache

---

# 21. Client state local

## 21.1 Opções
- Zustand
- Redux Toolkit
- Jotai
- Context API puro

## 21.2 O que precisamos
- UI state local
- painéis
- seleção de nota
- estado de editor
- pequenos fluxos de sessão

## 21.3 Recomendação
**Zustand**.

## 21.4 Justificativa
Redux é pesado demais para a v1.  
Context puro tende a espalhar estado ruim.  
Zustand é simples, pequeno e ótimo para UI state.

## 21.5 Decisão v1
- Zustand só para client state local
- TanStack Query para server state
- não misturar os dois papéis

---

# 22. Editor da nota

## 22.1 Opções
- CodeMirror 6
- Monaco
- Tiptap
- ProseMirror puro
- textarea turbinado

## 22.2 O que o produto realmente precisa
- editar Markdown canônico
- ser extensível
- suportar highlights, commands, decorations
- preservar a natureza textual do sistema
- não transformar o core em rich-text-first

## 22.3 Tradeoffs

### CodeMirror 6
**Prós**
- modular
- extensível
- excelente para texto/Markdown/code
- ótimo para editor baseado em documento textual canônico citeturn411871search1turn411871search5turn411871search9

**Contras**
- colaboração avançada exige trabalho adicional
- curva de extensão moderada

### Monaco
**Prós**
- editor poderoso
- muito bom para code-like experiences

**Contras**
- mais pesado
- menos natural para note editing híbrido
- parece mais IDE do que note workspace

### Tiptap
**Prós**
- ótimo para rich text/headless
- muito extensível
- excelente quando o centro é editor visual rico citeturn411871search2turn411871search10turn411871search14

**Contras**
- o produto não é rich-text-first
- nossa verdade canônica é Markdown
- patch/diff/Git ficam conceitualmente mais limpos com editor textual real

## 22.4 Recomendação
**CodeMirror 6**.

## 22.5 Decisão v1
- editor principal = CodeMirror 6
- preview/render em painel separado
- Tiptap só se um futuro modo “rich collaborative editing” justificar

---

# 23. Markdown rendering

## 23.1 Opções
- react-markdown
- markdown-it
- MDX runtime
- custom renderer

## 23.2 Recomendação
**react-markdown + remark-gfm + rehype-sanitize**

## 23.3 Justificativa
- simples
- bom enough
- markdown-first
- mais seguro com sanitização
- não força MDX complexity no core

## 23.4 Decisão v1
- renderer simples
- sem MDX como canônico
- sem plugin ecosystem complexo de render na v1

---

# 24. Diff / review UI

## 24.1 Opções
- diff2html
- react-diff-viewer
- Monaco diff editor
- viewer custom de unified diff

## 24.2 Recomendação
**viewer simples de unified diff / split diff**, não Monaco como dependência central.

## 24.3 Justificativa
O importante é:
- clareza
- leveza
- reviewability
- fácil integração com proposals

A UI de diff não deve arrastar um editor gigante só por estética.

## 24.4 Decisão v1
- diff textual legível
- metadata de proposal
- approve/reject/apply

---

# 25. Auth strategy no core OSS

## 25.1 Opções
- auth embutida local (email/senha/session)
- FastAPI Users
- OIDC-only
- external auth service
- sem auth (single-user trusted env)

## 25.2 O que o core precisa
- rodar self-hosted
- não depender de SaaS externo
- não enfiar infra enterprise cedo
- permitir single-user e poucos usuários depois
- proteger ações sensíveis

## 25.3 Recomendação
**Auth local simples no core**, com:
- bootstrap admin
- email/senha opcional
- Argon2id para password hashing
- session cookies assinados ou JWT + cookie httpOnly
- adapter OIDC futuro

## 25.4 O que evitar
- acoplar o core a Supabase/Auth0/etc
- fazer SSO enterprise cedo
- depender de external IdP para o OSS funcionar

## 25.5 Decisão v1
- auth local básica
- abstração de auth para plugar OIDC depois

---

# 26. MCP implementation strategy

## 26.1 Opções
- adotar MCP internamente desde o início
- expor MCP só depois
- construir tudo em volta de MCP

## 26.2 Recomendação
**Não usar MCP como barramento interno.**  
Usar MCP apenas como superfície de exposição posterior.

## 26.3 Justificativa
MCP padroniza integração com tools, resources e roots, mas não deve definir a arquitetura interna do produto. Roots ajudam a comunicar limites de filesystem; sampling existe para server-initiated model calls, mas o protocolo não substitui teu control plane nem tua policy engine. citeturn147720search3turn147720search11turn147720search15turn147720search18

## 26.4 Decisão v1
- contratos internos próprios
- MCP depois dos módulos estabilizarem

---

# 27. Object storage e attachments

## 27.1 Opções
- filesystem local only
- S3-compatible abstraction
- MinIO
- R2/S3/Backblaze only

## 27.2 Recomendação
No core OSS:
- **filesystem local como padrão**
- **storage adapter S3-compatible opcional**

## 27.3 Justificativa
O canônico já vive em filesystem.
Para attachments maiores e raw artifacts, o core deve aceitar adaptador, mas não obrigar object storage.

## 27.4 Decisão v1
- local disk first
- storage adapter interface
- S3/MinIO depois

---

# 28. Optional sync

## 28.1 Opções
- sync embutido
- Syncthing
- Git push/pull manual
- nada oficial

## 28.2 Recomendação
**Não construir sync protocol próprio na v1.**
Se precisar de sync local-first:
- recomendar Syncthing externamente
- ou Git workflows simples para usuários avançados

## 28.3 Decisão v1
- sync fora do core
- documentar compatibilidade, não implementar engine própria

---

# 29. Observabilidade e logs

## 29.1 Opções
- logging padrão puro
- structlog
- loguru
- OTEL manual/auto
- Sentry-only
- Prometheus-only

## 29.2 O que precisamos
- logs estruturados
- correlation IDs
- job traces
- auditoria
- evolução futura para cloud

## 29.3 Tradeoffs

### structlog
**Prós**
- logging estruturado de verdade
- encaixa com stdlib logging
- bom para eventos de domínio e observabilidade citeturn504507search6turn504507search10

**Contras**
- exige disciplina de eventos e campos

### OpenTelemetry
**Prós**
- padrão vendor-neutral de observabilidade
- bom para traces/metrics/logs
- evolução natural para cloud depois citeturn504507search1turn504507search5turn504507search9

**Contras**
- não precisa começar super sofisticado

## 29.4 Recomendação
- **structlog** para logs estruturados
- **OpenTelemetry** para tracing/metrics, inicialmente leve

## 29.5 Decisão v1
- logs JSON
- trace IDs
- spans em operações críticas
- sem over-instrumentation

---

# 30. Test stack

## 30.1 Backend tests
### Recomendação
- **pytest**
- **httpx** para testes de API
- **anyio / pytest-asyncio** quando necessário

## 30.2 Frontend tests
### Recomendação
- **Vitest** para unit/component tests
- **Testing Library** para componentes React

## 30.3 E2E
### Recomendação
- **Playwright**

Playwright traz runner, assertions, isolamento e cross-browser com bom suporte para apps modernas. citeturn504507search0turn504507search4turn504507search12

## 30.4 Decisão v1
- pytest no backend
- Playwright para E2E obrigatório
- sem Cypress

---

# 31. Dev tooling

## 31.1 Python package / project manager
### Opções
- uv
- Poetry
- pip-tools
- Hatch
- PDM

### Recomendação
**uv**

`uv` é um package/project manager extremamente rápido e muito bem alinhado à ergonomia moderna do ecossistema Python. citeturn999872search3turn999872search23

## 31.2 Lint / format
### Recomendação
- **Ruff** para lint + format

Ruff é extremamente rápido e cobre o papel de várias ferramentas de lint/format em uma só. citeturn504507search3turn504507search7turn504507search11

## 31.3 Type checking
### Recomendação
- **mypy** ou **pyright**
- escolha pragmática: **mypy** primeiro para evitar toolchain extra JS no backend

## 31.4 Frontend package manager
### Recomendação
- **pnpm**

## 31.5 Task runner
### Recomendação
- **justfile** ou **Makefile**
- escolha pragmática: **Makefile** se quiser o menor número de dependências, **just** se quiser ergonomia melhor

## 31.6 Decisão v1
- uv
- Ruff
- mypy
- pnpm
- Makefile ou justfile

---

# 32. Monorepo strategy

## 32.1 Opções
- monorepo
- polyrepo

## 32.2 Recomendação
**Monorepo**.

## 32.3 Justificativa
O core OSS tem:
- backend
- worker
- frontend
- shared contracts
- deployment files
- docs
- future MCP surfaces

Isso vive melhor em monorepo.

## 32.4 Estrutura sugerida

```text
repo/
  apps/
    api/
    worker/
    web/
  packages/
    py-domain/
    py-services/
    py-agent/
    py-research/
    ts-ui/
    ts-sdk/        # opcional
  infra/
    docker/
    caddy/
  docs/
  scripts/
```

## 32.5 Observação
Mesmo em monorepo, manter boundaries claros:
- packages Python de domínio
- apps finos
- evitar tudo acoplado em `app/` gigante se a modularidade começar a sofrer

---

# 33. Reverse proxy / web serving

## 33.1 Opções
- Caddy
- Nginx
- Traefik
- sem reverse proxy local

## 33.2 Recomendação
**Caddy** para self-host simplificado.

## 33.3 Justificativa
- configuração mais simples
- HTTPS automático em deploys reais
- ótimo fit para OSS self-hosted

## 33.4 Decisão v1
- Caddy nos exemplos de deploy
- Nginx aceitável como alternativa

---

# 34. Containerização / deployment

## 34.1 Opções
- Docker Compose
- Podman Compose
- Kubernetes
- Nomad
- systemd manual

## 34.2 Recomendação
**Docker Compose**.

## 34.3 Justificativa
- padrão de fato para OSS self-hosted
- bom equilíbrio entre simplicidade e realismo
- fácil de documentar
- suficiente para modular monolith + worker + postgres + crawler

## 34.4 O que rejeitar agora
- Kubernetes
- Helm charts como foco principal
- service mesh
- operators

## 34.5 Decisão v1
- `docker-compose.yml` oficial
- optional bare-metal docs depois

---

# 35. Note parsing / frontmatter / markdown semantics

## 35.1 Problema real
O produto precisa manipular:
- frontmatter
- headings
- trechos
- metadata
- links
- notas inteiras
sem sequestrar o formato nem depender de AST pesada cedo.

## 35.2 Recomendação
### Frontmatter
- usar `ruamel.yaml` ou wrapper próprio round-trip-safe

### Corpo
- usar texto cru como verdade
- adicionar parser leve de headings / sections
- evitar AST complexa como base da v1

## 35.3 Estratégia senior
Não super-frameworkar a nota.
A nota é Markdown canônico.
O default deve ser:
- parse frontmatter
- body como texto
- heading utilities
- patch textual

## 35.4 O que adiar
- AST editing sofisticado
- transforms ricos demais
- rich-block semantics no backend

---

# 36. Embeddings provider strategy

## 36.1 Recomendação
Criar interface pequena:

```python
class EmbeddingsProvider(Protocol):
    def embed_texts(self, texts: list[str]) -> list[list[float]]: ...
```

## 36.2 Justificativa
Embeddings não devem vazar vendor logic para o sistema inteiro.

## 36.3 Estratégia
- provider adapter por fora
- fallback BYOK
- bulk jobs no worker

## 36.4 Decisão v1
- interface própria
- implementação por provider fora do core canônico

---

# 37. UI component philosophy

## 37.1 Recomendação
- componentes próprios simples
- base visual com Tailwind
- biblioteca de primitives leve
- não depender de UI framework enterprise pesado

## 37.2 Opção prática
- Tailwind CSS
- Radix UI primitives quando necessário
- shadcn/ui como pattern kit, não como arquitetura do app

## 37.3 Justificativa
- acelera desenvolvimento
- mantém design system razoável
- não vira dependência conceitual dura

---

# 38. Explicitamente rejeitado para a v1

Estas decisões são deliberadas.

## 38.1 Não usar microservices
Porque:
- aumentam custo operacional
- quebram clareza
- não são necessários
- pioram a vida do solo founder

## 38.2 Não usar Kubernetes
Porque:
- não resolve o problema principal
- aumenta tempo de infra
- a v1 não precisa

## 38.3 Não usar Django como centro
Porque:
- o produto é service/runtime-centric, não admin-centric

## 38.4 Não usar Next.js como centro do app
Porque:
- backend Python é o centro
- SSR não é o gargalo do produto

## 38.5 Não usar Tiptap como editor principal
Porque:
- a verdade canônica é Markdown textual
- patch/Git/diff ficam mais limpos com CodeMirror

## 38.6 Não usar Qdrant cedo
Porque:
- pgvector resolve a v1
- mais um serviço seria custo sem prova

## 38.7 Não usar Redis cedo
Porque:
- Postgres resolve fila e estado inicial
- menos moving parts

## 38.8 Não usar LangChain como espinha dorsal do produto
Porque:
- abstrai demais cedo
- o sistema precisa contracts claros e próprios

## 38.9 Não usar MCP internamente
Porque:
- MCP é superfície de integração, não kernel interno

## 38.10 Não usar sync protocol próprio
Porque:
- não é a prioridade
- custo alto
- Syncthing resolve boa parte externamente

---

# 39. Decisão final por componente

## 39.1 Core backend
- Python
- FastAPI
- Pydantic v2
- SQLAlchemy 2
- Alembic
- Psycopg 3

## 39.2 Data
- PostgreSQL
- pgvector
- PostgreSQL FTS
- optional `pg_trgm`

## 39.3 Jobs
- Postgres-backed queue
- worker custom
- LangGraph só em fluxos específicos depois

## 39.4 Agent
- Hermes-core-lite conceitual
- PydanticAI como layer agentic principal

## 39.5 Retrieval
- FTS + pgvector + context pack builder
- Qdrant só depois

## 39.6 Git boundary
- Git CLI via GitService
- worktrees
- patch-first

## 39.7 Crawler / parser
- Crawl4AI + Playwright
- Docling

## 39.8 Frontend
- React
- Vite
- TypeScript
- React Router
- TanStack Query
- Zustand
- Tailwind

## 39.9 Editor
- CodeMirror 6
- react-markdown render pipeline

## 39.10 Observability
- structlog
- OpenTelemetry

## 39.11 Testing
- pytest
- Vitest
- Playwright

## 39.12 Dev tooling
- uv
- Ruff
- mypy
- pnpm
- Makefile/justfile

## 39.13 Deployment
- Docker Compose
- Caddy
- optional bare-metal docs

---

# 40. Phased adoption map

## Fase 1 — foundation
- Python
- FastAPI
- Pydantic
- Postgres
- SQLAlchemy
- Alembic
- Git CLI
- React + Vite
- CodeMirror
- Tailwind
- uv + Ruff + pytest

## Fase 2 — boundary and policy
- Exchange Zone
- policy engine
- approval flows
- worker
- audit logs

## Fase 3 — agent and retrieval
- PydanticAI
- pgvector
- context packs
- note copilot

## Fase 4 — research
- Crawl4AI
- Playwright
- Docling
- synthesis pipeline

## Fase 5 — long-running durability
- LangGraph where justified

## Fase 6 — integration
- MCP exposure
- optional OIDC
- optional Qdrant
- optional object storage adapter

---

# 41. Senior recommendation final

Se eu estivesse assinando tecnicamente essa v1 como arquiteto responsável, eu congelaria a seguinte tese:

> **Python no centro, FastAPI no edge interno, Postgres como cérebro operacional, filesystem como soberano, Git como fronteira editorial, PydanticAI para o agente, Crawl4AI + Docling para research, React + Vite + CodeMirror no frontend, e nenhum serviço extra que ainda não tenha provado valor.**

Em forma ainda mais curta:

- **Backend:** FastAPI + Pydantic + SQLAlchemy + Alembic + Psycopg + Postgres
- **Agent:** Hermes-core-lite + PydanticAI
- **Retrieval:** Postgres FTS + pgvector
- **Jobs:** Postgres queue + worker custom
- **Research:** Crawl4AI + Playwright + Docling
- **Frontend:** React + Vite + TS + TanStack Query + Zustand + CodeMirror
- **Observability:** structlog + OpenTelemetry
- **Dev:** uv + Ruff + pytest + Playwright
- **Ops:** Docker Compose + Caddy

Essa stack é a melhor combinação de:
- aderência ao produto
- modularidade
- custo operacional baixo
- velocidade de execução
- facilidade para contributor OSS
- segurança arquitetural
- capacidade de evoluir para cloud depois sem rasgar a fundação

---

# 42. Referências oficiais úteis

## Backend / agent / protocol
- FastAPI: https://fastapi.tiangolo.com/
- FastAPI features / WebSockets / background tasks:
  - https://fastapi.tiangolo.com/features/
  - https://fastapi.tiangolo.com/advanced/websockets/
  - https://fastapi.tiangolo.com/tutorial/background-tasks/
- PydanticAI: https://ai.pydantic.dev/
- PydanticAI tools: https://ai.pydantic.dev/tools/
- PydanticAI built-in tools: https://ai.pydantic.dev/builtin-tools/
- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph durable execution: https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- MCP spec: https://modelcontextprotocol.io/specification/2025-11-25
- MCP roots: https://modelcontextprotocol.io/specification/2025-06-18/client/roots
- MCP sampling: https://modelcontextprotocol.io/specification/2025-11-25/client/sampling

## Data
- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic: https://alembic.sqlalchemy.org/
- Psycopg 3: https://www.psycopg.org/psycopg3/
- pgvector: https://github.com/pgvector/pgvector
- Qdrant docs: https://qdrant.tech/documentation/
- Qdrant hybrid search: https://qdrant.tech/documentation/concepts/hybrid-queries/

## Research
- Crawl4AI: https://github.com/unclecode/crawl4ai
- Crawl4AI docs/blog: https://docs.crawl4ai.com/blog/
- Docling: https://docling-project.github.io/docling/
- Docling supported formats: https://docling-project.github.io/docling/usage/supported_formats/
- Docling DocumentConverter: https://docling-project.github.io/docling/reference/document_converter/

## Frontend
- Vite: https://vite.dev/
- React Query / TanStack Query: https://tanstack.com/query
- CodeMirror: https://codemirror.net/
- Tiptap: https://tiptap.dev/docs

## Testing / observability / tooling
- Playwright: https://playwright.dev/
- OpenTelemetry Python: https://opentelemetry.io/docs/languages/python/
- structlog: https://www.structlog.org/
- uv: https://docs.astral.sh/uv/
- Ruff: https://docs.astral.sh/ruff/
