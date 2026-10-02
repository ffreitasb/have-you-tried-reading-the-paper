---
title: Code Generation & Agentic Coding Datasheet v2.0
tags: [ai, code, fim, agents, software-engineering]
updated: 2026-10-01
---

# Code Generation & Agentic Coding Datasheet v2.0

> Código tem duas fases matematicamente diferentes: **gerar tokens plausíveis** e **produzir uma transição válida no estado de um sistema de software**. Em 2026, coding SOTA é cada vez menos “autocomplete” e mais “closed-loop software engineering”.

## 1. Duas máquinas

### A. Completion engine

```math
p(code_t\mid code_{<t},context)
```

### B. Coding agent

```math
a_t\sim\pi(a\mid repo_t,conversation_t,tool_t,test_t)
```

```math
repo_{t+1}=Environment(repo_t,a_t)
```

A qualidade final depende do loop inteiro, não apenas da probabilidade do próximo token.

---

# PARTE I — COMPLETION

## 2. Left-to-right completion

```math
P(x_{1:T})=\prod_tP(x_t\mid x_{<t})
```

Adequado para:

- geração de arquivo;
- continuação de função;
- boilerplate;
- chat técnico.

---

## 3. Fill-In-the-Middle — FIM

Problema:

```math
P(M\mid Prefix,Suffix)
```

Serializações variam por tokenizer/modelo, mas conceitualmente há três regiões:

- prefix;
- suffix;
- middle.

### Por que funciona melhor que “promptar o buraco”

O modelo foi treinado para utilizar explicitamente contexto à esquerda **e** direita. Isso é diferente de apenas inserir o suffix em linguagem natural no prompt.

### Variáveis

| Variável | Tag | Efeito |
|---|---|---|
| FIM tokens/template | `MODEL` | protocolo de infilling |
| prefix length | `INF` | contexto anterior |
| suffix length | `INF` | constraints posteriores |
| max completion | `INF` | tamanho do patch |
| stop conditions | `INF` | encerra escopo |

---

## 4. Sampling para código

Não existe “temperature 0 sempre”. O objetivo define o regime.

### Completion determinístico

- temperature baixa;
- support restrito;
- stop/FIM corretos.

### Arquitetura/refactoring exploration

Pode justificar mais entropy para propor alternativas.

### Regra

```math
Correctness\not\equiv low\ temperature
```

Uma distribuição concentrada em uma resposta errada continua errada.

---

## 5. Repetition penalties em código

Código contém repetição legítima:

- indentação;
- delimitadores;
- nomes;
- estruturas paralelas;
- imports;
- boilerplate.

Penalidades agressivas podem degradar sintaxe ou consistência de identifiers.

Use DRY/rep penalties com mais parcimônia que em prosa criativa.

---

# PARTE II — CONTEXTO DE REPOSITÓRIO

## 6. Repository context ≠ context window

Ter 128k tokens disponíveis não implica inserir o repo inteiro.

Problema de seleção:

```math
S^*=\arg\max_S Utility(S\mid task),\quad |S|\le budget
```

Fontes:

- target file;
- imports;
- symbols/references;
- interfaces/types;
- tests;
- build config;
- README/spec;
- recent diffs.

### Failure mode

Contexto irrelevante aumenta tokens e pode reduzir signal-to-noise.

---

## 7. Retrieval e symbol graph

Busca lexical apenas encontra texto semelhante. Coding agents melhores combinam:

- filename/path priors;
- symbol lookup;
- references/call graph;
- semantic search;
- AST/tree-sitter;
- compiler/LSP feedback.

Representação conceitual:

```math
Repo\rightarrow Graph(V_{symbols/files},E_{imports/calls/refs})
```

Task context é uma sub-rede relevante do grafo.

---

# PARTE III — EDIÇÃO

## 8. Full rewrite vs patch

### Full rewrite

```math
file' = LLM(file,instruction)
```

Risco: alterações colaterais grandes.

### Patch/diff

```math
\Delta=LLM(context,instruction)
```

```math
file'=apply(file,\Delta)
```

Mais econômico e auditável, mas patch precisa casar com estado atual.

---

## 9. Structured edit

Melhor ainda quando a ação é representada como operação:

```math
a=(file,start,end,replacement)
```

ou AST transformation.

Isso separa:

- geração da intenção de edição;
- mecanismo determinístico de aplicação.

---

# PARTE IV — AGENT LOOP

## 10. O loop real

```math
Observe\rightarrow Select\ Context\rightarrow Plan/Policy\rightarrow Act\rightarrow Execute\rightarrow Observe
```

Estado:

```math
s_t=(repo_t,terminal_t,test_t,conversation_t,tool_t)
```

Ação:

```math
a_t\in\{read,search,patch,run,test,git,\ldots\}
```

Transição:

```math
s_{t+1}=E(s_t,a_t)
```

---

## 11. Environment feedback

Compiler/test são **oráculos parciais**.

```math
feedback=f(code')
```

Exemplos:

- parser;
- type checker;
- compiler;
- unit tests;
- integration tests;
- linter;
- benchmark.

O agente pode iterar:

```math
a_{t+1}=\pi(s_t,feedback_t)
```

Isso é qualitativamente diferente de one-shot code generation.

---

## 12. Verifiable rewards

Coding é especialmente adequado a RL/agentic training porque muitas tarefas têm sinais verificáveis:

```math
r\in\{test\ pass,compile,benchmark,judge\}
```

Qwen3-Coder-Next é um exemplo 2026 de treino agentic com tarefas verificáveis e ambientes executáveis.

---

# PARTE V — CORRECTNESS

## 13. Hierarquia de correção

1. **Lexical validity**
2. **Syntax validity**
3. **Type/static validity**
4. **Runtime validity**
5. **Test validity**
6. **Spec/semantic validity**
7. **Security/non-functional validity**

Passar em nível $`n`$ não garante $`n+1`$.

```math
SyntaxCorrect\not\Rightarrow SemanticallyCorrect
```

---

## 14. Structured output para ferramentas

Tool calls devem usar schema/constrained decoding quando possível.

Mas:

```math
JSONValid\not\Rightarrow ToolCallCorrect
```

Logo, validação deve ter duas fases:

1. schema validation;
2. semantic/precondition validation.

---

# PARTE VI — SECURITY

## 15. Agentic coding amplia superfície de risco

Um autocomplete errado gera texto errado. Um coding agent errado pode:

- deletar arquivos;
- rodar shell arbitrário;
- vazar secrets;
- modificar CI;
- publicar artefato;
- alterar dependências.

### Controle recomendado

```math
permission(a_t)\le granted\ capability
```

Princípios:

- least privilege;
- sandbox;
- read-only default;
- allowlist de ferramentas;
- approval em ação irreversível;
- secret isolation;
- diff review antes de commit/push.

---

## 16. Prompt injection em repository context

Arquivos do próprio repo podem conter instruções maliciosas ou acidentais.

Separar:

```math
Data\neq Instruction
```

Um comentário em README não deveria automaticamente ganhar autoridade de system prompt.

---

# PARTE VII — REPRODUCIBILIDADE

## 17. Seed fixa não basta

```math
R=f(weights,tokenizer,template,repo\ state,tool\ outputs,sampler,seed,backend,hardware)
```

Em agentes, o ambiente também muda:

```math
Environment_t\neq Environment_{t+1}
```

- package versions;
- network responses;
- timestamps;
- filesystem;
- concurrent processes.

Reproduzir uma trajetória agentic requer snapshot do ambiente, não somente seed.

---

# PARTE VIII — COST MODEL

## 18. Context economics

Custo total aproximado:

```math
Cost=C_{prefill}(repo\ context)+\sum_t C_{decode}(t)+\sum_j C_{tools,j}
```

Agentes longos podem gastar mais contexto reprocessando histórico do que gerando código.

### Otimizações

- prompt caching;
- tool result summarization;
- compact state;
- targeted retrieval;
- patch-oriented edits;
- truncation de logs irrelevantes.

---

# PARTE IX — COUPLING MATRIX

| Controle ↑ | Correctness | Diversity | Latência | Risco colateral |
|---|---:|---:|---:|---:|
| Temperature | variável/↓ em excesso | ↑ | ~ | ↑ |
| Context relevante | ↑ | ~ | ↑ | ↓ |
| Context irrelevante | ↓ potencial | ~ | ↑ | ↑ |
| Test iterations | ↑ | ~ | ↑ | ↓ |
| Agent horizon | ↑ até certo ponto | — | ↑ | ↑ depois de loops |
| Tool permissions | — | — | — | ↑ drasticamente |
| Patch granularity menor | ↑ auditabilidade | — | pode ↑ steps | ↓ |

---

# PARTE X — MAPEAMENTO PRÁTICO

## 19. Autocomplete/FIM

Escolher modelo com suporte FIM real e template correto. Verificar tokens especiais do tokenizer/model card.

## 20. Cline/Continue/agent harness

Avaliar separadamente:

- qualidade do modelo;
- retrieval/context builder;
- tool interface;
- diff application;
- terminal loop;
- permissions.

Trocar somente o modelo não mede o sistema agentic.

## 21. Local models

Em hardware limitado, MoE pode oferecer bom compute ativo, mas storage total continua relevante. Um “80B total / 3B active” não cabe magicamente como um 3B em VRAM.

---

# PARTE XI — PROTOCOLO EXPERIMENTAL

## 22. Benchmark útil

Usar corpus próprio com tarefas como:

1. completar função;
2. FIM em arquivo real;
3. corrigir bug unit-tested;
4. refactor multi-file;
5. adicionar feature com tests;
6. resolver erro de build;
7. navegar repo sem indicação de arquivo.

Medir:

- compile rate;
- test pass rate;
- edit distance;
- files touched;
- tool calls;
- retries;
- tokens;
- wall time;
- regressions.

---

## 23. Snapshot 2026

Qwen3-Coder-Next exemplifica a direção atual: modelo MoE 80B total / ~3B ativos por token, treinado para coding agents através de tarefas verificáveis e ambientes executáveis. O eixo relevante deixou de ser apenas “qual modelo completa melhor?” e virou “qual política fecha o loop de engenharia com menos passos e menos dano colateral?”.

## Referências

- Qwen3-Coder-Next — https://arxiv.org/abs/2603.00729
- llama.cpp FIM/samplers — https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h
