---
title: Agent & Action Control System Datasheet v2.0
tags: [ai, agents, tools, function-calling, mcp, control-systems]
updated: 2026-10-01
---

# Agent & Action Control System Datasheet v2.0

> Um agente não é um “LLM que chama funções”. É um **sistema de controle fechado** no qual um modelo escolhe ações, um ambiente muda de estado e novas observações realimentam a política.

## 1. Loop fundamental

\[
o_t=Observe(s_t)
\]

\[
a_t\sim\pi_\theta(a\mid h_t,o_t,C)
\]

\[
s_{t+1}=Environment(s_t,a_t)
\]

\[
h_{t+1}=Update(h_t,o_t,a_t,result_t)
\]

Isso é um sistema dinâmico com feedback.

---

# PARTE I — AÇÕES

## 2. Action space

\[
\mathcal A=\{text,tool_1,tool_2,computer\_action,stop,\ldots\}
\]

Cada tool possui schema:

\[
a=(tool\_name,args)
\]

### Não existe “invocation threshold” universal

Algumas aplicações podem ter um classificador/confidence threshold, mas em muitos sistemas a seleção de ferramenta é diretamente uma decisão da policy/modelo.

Classifique threshold como `PIPE/UI`, nunca `ARCH` universal.

---

## 3. Tool choice

Possíveis regimes:

- `auto`;
- tool específica forced;
- “must use a tool”;
- text-only;
- policy externa.

Isso restringe o action space:

\[
\mathcal A'\subseteq\mathcal A
\]

---

# PARTE II — STRUCTURED OUTPUT

## 4. Schema constrained decoding

Conjunto de strings válidas:

\[
L(Schema)
\]

Durante decode:

\[
p(x_t)=0\quad\forall x_t\notin ValidPrefix(Schema)
\]

Isso garante, dependendo da implementação, forte validade sintática/estrutural.

### Mas:

\[
SchemaValid\neq SemanticallyValid
\]

Exemplo: `{"amount": 1000000}` pode ser JSON/schema perfeito e ainda ser uma ação absurda ou não autorizada.

---

## 5. Quatro níveis de validade

1. **Syntax** — parseia?
2. **Schema** — campos/tipos válidos?
3. **Semantic** — argumentos fazem sentido?
4. **Authorization/Safety** — ação deve ser executada?

\[
V=V_{syntax}\land V_{schema}\land V_{semantic}\land V_{auth}
\]

---

# PARTE III — STATE

## 6. Histórico não é apenas “N turns”

Estado útil pode incluir:

\[
h_t=\{conversation,tool\ results,files,IDs,plans,environment\ state,memory\}
\]

Histórico deve ser **state representation**, não simplesmente quantidade fixa de mensagens.

---

## 7. State compression

Long-running agents precisam comprimir:

\[
H_{raw}\rightarrow H_{compact}
\]

Risco:

\[
Compression\uparrow\Rightarrow ContextCost\downarrow\ but\ InformationLoss\uparrow
\]

Guardar IDs, handles, invariants e decisões é geralmente mais seguro que resumir tudo em prosa.

---

# PARTE IV — PLANNING

## 8. Plan vs policy

Planejamento explícito:

\[
P=(a_1,a_2,\ldots,a_n)
\]

Política reativa:

\[
a_t=\pi(s_t)
\]

Agentes robustos frequentemente combinam plano + replanning após observação.

### Importante

“Forçar chain-of-thought visível” não é condição universal para melhor planejamento. O relevante é a capacidade do sistema de decompor, verificar e corrigir ações.

---

## 9. Horizon

Quanto maior o número de passos:

\[
P(success_{all})\approx\prod_tP(success_t\mid history)
\]

Mesmo 99% de sucesso por etapa:

\[
0.99^{100}\approx0.366
\]

Trajetórias longas amplificam pequenas taxas de erro.

### Engenharia

Reduzir número de ações e aumentar verificabilidade por ação pode ser mais valioso que “modelo mais inteligente”.

---

# PARTE V — RETRIES

## 10. Retry policy

Retries não devem ser apenas `max_retries=3`.

Definir:

- retryable errors;
- backoff;
- idempotency;
- max attempts;
- mutation detection;
- alternative strategy.

### Perigo

Repetir ação não idempotente:

\[
E(E(s,a),a)\neq E(s,a)
\]

pode duplicar pagamentos, mensagens, uploads etc.

---

## 11. Idempotency

Ideal:

\[
E(E(s,a),a)=E(s,a)
\]

Quando impossível, usar idempotency key/transaction ID e verificar estado antes de retry.

---

# PARTE VI — TRANSACTIONS E ROLLBACK

## 12. Prepare → validate → commit

Para ações críticas:

\[
Plan\rightarrow DryRun\rightarrow Validate\rightarrow Approve\rightarrow Commit
\]

Separar geração da ação de sua execução.

### Rollback

Se operação tem inversa:

\[
a^{-1}(a(s))\approx s
\]

registrar como parte do plano.

Nem toda ação é reversível.

---

# PARTE VII — HUMAN IN THE LOOP

## 13. HITL deve ser baseado em risco

Não simplesmente `True/False` global.

Definir função:

\[
Risk(a)=Impact(a)\times Probability(error)\times Irreversibility(a)
\]

Exigir aprovação quando:

\[
Risk(a)>\tau
\]

ou por classe de capability.

### Exemplos de alto risco

- enviar externamente;
- deletar;
- gastar dinheiro;
- alterar permission;
- publicar;
- executar código privilegiado.

---

# PARTE VIII — CAPABILITIES

## 14. Least privilege

A policy não deve receber ferramenta que não precisa.

\[
Capabilities_{agent}\subseteq Capabilities_{required}
\]

Quanto maior \(|\mathcal A|\), maior o espaço de decisões e a superfície de ataque.

---

## 15. Sandbox

Separar:

- read;
- write;
- execute;
- network;
- secrets;
- destructive operations.

Tool description não é mecanismo de segurança. Enforcement precisa existir fora do LLM.

---

# PARTE IX — PROMPT/TOOL INJECTION

## 16. Data can contain instructions

Webpages, emails, docs e tool results são inputs potencialmente adversariais.

Princípio:

\[
UntrustedData\not\Rightarrow Authority
\]

O agente deve manter hierarquia de instruções/capabilities fora do conteúdo recuperado.

---

# PARTE X — COMPUTER USE

## 17. GUI action loop

Observação visual:

\[
o_t=Vision(screen_t)
\]

Ação:

\[
a_t=(mouse/keyboard/navigation)
\]

Estado novo:

\[
screen_{t+1}=App(screen_t,a_t)
\]

### Sources of error

- localization;
- stale screen;
- animation;
- focus;
- hidden state;
- ambiguous controls.

Computer use possui observabilidade menor que API estruturada. Preferir API/tool quando disponível.

---

# PARTE XI — VOICE-TO-ACTION

## 18. Pipeline correto

\[
audio\rightarrow VAD\rightarrow ASR\rightarrow agent/policy\rightarrow tool\rightarrow environment
\]

Latência total:

\[
T=T_{VAD}+T_{ASR}+T_{LLM}+T_{tool}+T_{feedback}
\]

VAD é um subsistema de entrada, não parâmetro de “LAM”.

---

# PARTE XII — MCP

## 19. MCP como protocolo, não inteligência

MCP padroniza conexão entre hosts e sistemas de dados/tools. Não torna o modelo semanticamente mais confiável.

Na spec **2026-07-28**, o core passou a ser stateless no protocolo, adicionou Multi Round-Trip Requests, routing por headers, caching de list results, framework de extensions e Tasks como extensão.

### Implicação arquitetural

Separar:

\[
Agent\ policy
\]

from

\[
Tool\ transport/protocol
\]

MCP resolve interoperabilidade e lifecycle/protocol concerns; decisão/segurança ainda pertence ao sistema agentic.

---

# PARTE XIII — OBSERVABILIDADE

## 20. Métricas essenciais

- tool selection accuracy;
- schema-valid rate;
- semantic-valid rate;
- success/task completion;
- retries/action;
- steps/task;
- tokens/task;
- irreversible actions;
- rollback rate;
- permission denials;
- wall time;
- cost.

### Não confundir

\[
ToolCallRate\neq TaskSuccess
\]

Um agente “ativo” pode simplesmente estar errando muito.

---

# PARTE XIV — COUPLING MATRIX

| Controle ↑ | Autonomia | Success potencial | Risco | Custo |
|---|---:|---:|---:|---:|
| tool set size | ↑ | pode ↑ | ↑ | ↑ decision complexity |
| max steps | ↑ | ↑ até plateau | ↑ | ↑ |
| retries | ↑ | ↑ em falha transitória | ↑ duplicação | ↑ |
| HITL | ↓ autonomia | ↑ safety | ↓ | ↑ latência humana |
| schema strictness | ↓ malformed calls | ~ semantic | ↓ syntax risk | pequeno |
| state compression | ~ | pode ↓ | informação perdida ↑ | ↓ context cost |

---

# PARTE XV — FAILURE DIAGNOSTICS

| Sintoma | Camada |
|---|---|
| JSON inválido | constrained decoding/schema |
| argumento inventado | semantic policy/missing-data handling |
| chama tool errada | tool selection/descriptions/context |
| repete ação | state/idempotency/retry |
| perde arquivo/ID | state representation |
| ação perigosa | capability/HITL/enforcement |
| browser entra em loop | observability/stale UI/horizon |

---

## 21. Snapshot 2026

MCP 2026-07-28 é a fotografia mais importante da infraestrutura agentic aberta atual: core stateless, explicit state handling, Multi Round-Trip Requests, extensões formais e Tasks. Isso reforça a mudança de mentalidade: “action model” não é uma categoria isolada de checkpoint; é um **control system + protocol + environment + policy**.

## Referências

- MCP 2026-07-28 — https://blog.modelcontextprotocol.io/posts/2026-07-28/
- MCP TypeScript SDK v2 — https://ts.sdk.modelcontextprotocol.io/v2/
