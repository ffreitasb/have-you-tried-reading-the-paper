---
title: Security, Robustness & Failure Modes Datasheet — SOTA++ 2026
aliases: [AI Security Datasheet, Robustness Datasheet, Failure Modes Datasheet]
tags: [ai, referencia, seguranca, robustez, red-teaming, prompt-injection, agent-security, supply-chain]
updated: 2026-10-01
---

# Security, Robustness & Failure Modes Datasheet — SOTA++ 2026

> Em sistemas probabilísticos, falha não é exceção rara: é parte da superfície operacional. Segurança começa quando o sistema assume que **modelo, contexto, dados recuperados, ferramentas e artefatos externos podem errar ou ser hostis**.

A distinção fundamental:

```math
\boxed{
Safety \neq Security \neq Robustness \neq Reliability
}
```

- **Safety**: evitar dano mesmo sem atacante.
- **Security**: resistir a adversário intencional.
- **Robustness**: manter comportamento sob perturbações/distribution shift.
- **Reliability**: cumprir função com taxa de falha aceitável.

Veja também:

- [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md)
- [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md)
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md)
- [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)

---

# 1. Threat model primeiro, mitigação depois

Um modelo de ameaça deve responder:

1. **Asset** — o que protegemos?
2. **Adversary** — quem pode atacar?
3. **Entry point** — por onde entra input?
4. **Trust boundary** — onde dados deixam de ser confiáveis?
5. **Capability** — o que o sistema pode fazer?
6. **Impact** — o que acontece se falhar?

Sem threat model, “security” vira lista de boas práticas desconectadas.

---

# 2. O grafo de confiança

Um sistema moderno pode ser visto como:

```text
user
  ↓
prompt / files / media
  ↓
model
  ↔ memory
  ↔ retrieval corpus
  ↔ MCP/tools/APIs
  ↔ external web/services
  ↓
actions / generated output
  ↓
downstream interpreters / humans / systems
```

Cada seta é uma **trust boundary**.

---

# 3. Princípio zero: modelo é componente não confiável

Mesmo sem atacante:

```math
P(ModelError)>0
```

Com adversário:

```math
P(ModelError|AdversarialInput)
>
P(ModelError|NominalInput)
```

Logo output do modelo deve ser tratado como **untrusted data** até validado para a operação específica.

---

# 4. Prompt injection — o problema estrutural

Em sistemas LLM, dados e instruções compartilham o mesmo canal semântico.

Se:

```math
Context = TrustedInstruction + UntrustedContent
```

modelo precisa inferir qual texto deve controlar comportamento.

Não existe separação de privilégio equivalente a CPU ring levels dentro do token stream.

Isso torna prompt injection uma falha de **instruction/data boundary**.

---

# 5. Direct prompt injection

Atacante escreve explicitamente instrução adversarial:

```text
ignore previous instructions...
```

A defesa não deve ser apenas “diga ao modelo para ignorar ataques”.

Defesas precisam existir fora do modelo:

- capability restriction;
- input/output validation;
- least privilege;
- approval gates;
- isolation.

---

# 6. Indirect prompt injection

Conteúdo hostil vem de fonte externa:

```text
web page
email
PDF
retrieved document
issue/comment
tool output
```

Pipeline:

```math
ExternalContent
\rightarrow Context
\rightarrow Model
\rightarrow Action
```

O usuário pode nunca ter visto a instrução adversarial.

---

# 7. Prompt injection é diferente de jailbreak

## Prompt injection

Atacante tenta alterar **fluxo de controle** do sistema.

## Jailbreak

Tenta contornar política/restrição de comportamento do modelo.

Há sobreposição, mas threat models são diferentes.

---

# 8. System prompt não é secret store

System prompt pode ser:

- inferido;
- parcialmente extraído;
- exposto por tool traces;
- reconstruído por comportamento.

Não armazene nele:

- API keys;
- passwords;
- privileged tokens;
- secrets de infraestrutura.

```math
PromptVisibilityAssumption\neq SecurityBoundary
```

---

# 9. Sensitive information disclosure

Fontes possíveis:

- context;
- retrieval;
- memory;
- logs;
- training memorization;
- tool output;
- secret-bearing environment variables.

Controle deve atuar antes e depois do modelo.

---

# 10. Training data poisoning

Atacante altera distribuição de treinamento:

```math
D' = D \cup D_{poison}
```

para induzir:

- backdoor;
- targeted behavior;
- degraded accuracy;
- misinformation.

Pequena fração de dados pode causar efeito desproporcional se exemplos forem estrategicamente escolhidos.

---

# 11. Backdoors

Deseja-se comportamento normal em distribuição padrão:

```math
f(x)=normal
```

mas comportamento malicioso sob trigger:

```math
f(x\oplus trigger)=malicious
```

Triggers podem ser:

- tokens;
- frases;
- padrões visuais;
- áudio;
- metadata;
- multimodal combinations.

---

# 12. Fine-tuning poisoning

PEFT não remove risco.

Um adapter pequeno pode alterar comportamento de forma direcionada:

```math
W'=W+\Delta W_{adapter}
```

Logo adapter é **código comportamental executável via parâmetros** do ponto de vista de supply chain.

---

# 13. Model supply chain

Artefatos possíveis:

- `.safetensors`;
- `.gguf`;
- PyTorch pickle/checkpoints;
- tokenizer files;
- Python model code;
- custom ops;
- LoRA/adapters;
- ComfyUI nodes;
- wheels/packages.

Não confundir:

```math
ModelFile
```

com:

```math
SafeToLoad
```

---

# 14. Serialization risk

Formatos baseados em pickle podem executar código durante deserialização se carregados de fonte hostil.

`safetensors` foi desenhado para armazenar tensores sem arbitrary code execution por deserialização.

Isso reduz uma classe de risco, não garante integridade do modelo.

Um `.safetensors` pode conter pesos maliciosamente treinados.

---

# 15. GGUF

GGUF é formato binário de pesos/metadata para runtimes ggml/llama.cpp-like e não um Python pickle arbitrário.

Porém:

- parser bugs continuam possíveis;
- metadata pode ser hostil;
- modelo pode ser backdoored;
- origem/hash importam.

```math
NonExecutableFormat\neq TrustedArtifact
```

---

# 16. `trust_remote_code`

Ao permitir código remoto de repositório de modelo:

```math
ModelRepository
\rightarrow PythonExecution
```

A boundary muda completamente.

Use apenas quando:

- origem confiável;
- código revisado/pinned;
- ambiente isolado.

---

# 17. Custom nodes — ComfyUI

Custom node frequentemente é Python com acesso ao processo/FS/rede.

Portanto:

```math
InstallCustomNode
\approx
InstallSoftware
```

não:

```math
InstallCustomNode
\approx
LoadModel
```

Threat surface inclui:

- install scripts;
- dependencies;
- arbitrary shell/network access.

---

# 18. Dependency supply chain

Riscos:

- typosquatting;
- dependency confusion;
- compromised maintainer;
- malicious update;
- transitive dependency;
- binary wheel compromise.

Controles:

- pinning;
- hashes;
- lockfiles;
- isolated environments;
- minimal dependencies;
- provenance/signatures quando disponíveis.

---

# 19. RAG poisoning

Atacante modifica corpus:

```math
D_{retrieval}'=D\cup Poison
```

Se poison rankeia alto:

```math
P(Poison\in TopK)\uparrow
```

Então contexto contaminado entra no modelo.

Isso combina:

- retrieval attack;
- prompt injection;
- misinformation.

Veja [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

# 20. Embedding/vector weaknesses

Ataques podem explorar:

- embedding collisions;
- nearest-neighbor manipulation;
- malicious chunk placement;
- metadata filter bypass;
- cross-tenant vector-store leakage.

Similarity não implica trust:

```math
HighCosineSimilarity
\not\Rightarrow
TrustedDocument
```

---

# 21. Retrieval authorization

Filtrar autorização **depois** de recuperar conteúdo pode ser tarde demais.

Idealmente:

```math
CandidateSet
=
Documents(user\ is\ authorized\ to\ access)
```

antes de ranking/context injection.

---

# 22. Agent attack surface

Agente adiciona ação ao sistema:

```math
Observe\rightarrow Decide\rightarrow Act
```

Falha deixa de ser apenas texto incorreto.

Pode modificar estado externo.

---

# 23. Excessive agency

Risco cresce com três dimensões:

```math
Risk
\propto
Functionality
\times Permissions
\times Autonomy
```

Reduzir qualquer fator reduz blast radius.

OWASP formaliza essa classe há várias versões e expandiu abordagem agentic em 2025–2026.

---

# 24. Least privilege

Permissões do agente devem satisfazer:

```math
Permissions_{agent}
\subseteq
Permissions_{minimum\ required}
```

Evitar credencial global privilegiada para uma tarefa de leitura restrita.

---

# 25. Capability design

Prefira tool específica:

```text
read_invoice(invoice_id)
```

a:

```text
execute_sql(query)
```

ou:

```text
run_shell(command)
```

Quanto mais open-ended a interface:

```math
AttackSurface\uparrow
```

---

# 26. Authorization fora do modelo

Modelo pode propor:

```math
action=(tool,args)
```

Mas policy engine deve decidir:

```math
Allowed(user,action,state)?
```

A autorização não deve depender de “o modelo pareceu confiante”.

---

# 27. Human-in-the-loop

HITL deve ser baseado em risco, não usado para todo evento.

Uma função útil:

```math
RequireApproval
=
I(
Impact\times Irreversibility\times Uncertainty
>\tau
)
```

A aprovação precisa mostrar:

- ação concreta;
- alvo;
- argumentos;
- efeito esperado;
- irreversibilidade.

---

# 28. Human approval não é defesa absoluta

Humano pode sofrer:

- automation bias;
- fatigue;
- trust exploitation;
- misleading explanation.

OWASP Agentic Top 10 chama atenção explicitamente para Human-Agent Trust Exploitation.

---

# 29. Agent goal hijack

Atacante altera objetivo operacional do agente por:

- prompt injection;
- poisoned memory;
- poisoned tool output;
- malicious peer agent.

Goal state precisa ser protegido/separado do conteúdo não confiável.

---

# 30. Tool misuse

Ferramenta legítima + argumentos maliciosos:

```math
SafeTool
+
UnsafeInvocation
=
UnsafeSystem
```

Validar parâmetros semanticamente, não apenas schema JSON.

---

# 31. Identity & privilege abuse

Em agentic systems, identidade deve ser:

- explícita;
- scoped;
- short-lived quando possível;
- attributable.

Evitar shared superuser identity.

---

# 32. Agentic supply chain

MCP server/tool provider pode mudar depois de aprovado.

Runtime discovery aumenta risco:

```math
DynamicComponents
\rightarrow
DynamicTrustGraph
```

Pin/allowlist, metadata validation e policy enforcement tornam-se necessários.

---

# 33. Unexpected code execution

Natural-language agents podem transformar output em:

- shell;
- SQL;
- Python;
- template;
- browser script.

Cada downstream interpreter reintroduz injection clássica.

---

# 34. Memory/context poisoning

Se memória persistente recebe conteúdo adversarial:

```math
attack_t
\rightarrow Memory
\rightarrow behavior_{t+n}
```

Ataque sobrevive à sessão original.

Memória deve ter:

- provenance;
- write policy;
- expiration;
- review;
- scope.

---

# 35. Inter-agent communication

Mensagem entre agentes deve ser tratada como input não confiável.

Assinar/identificar origem ajuda autenticidade, mas não garante semântica correta.

```math
AuthenticatedMessage\neq SafeInstruction
```

---

# 36. Cascading failures

Se agentes dependem entre si:

```math
Error_A
\rightarrow
State_B
\rightarrow
Error_B
\rightarrow\cdots
```

Blast radius aumenta com coupling.

Controle:

- circuit breakers;
- rate limits;
- independent validation;
- bounded retries;
- transactional steps.

---

# 37. Rogue / policy-divergent agents

Não é necessário antropomorfizar.

Operacionalmente significa:

```math
ObservedPolicy
\notin
AllowedPolicyEnvelope
```

Independentemente de “intenção” do modelo.

Monitorar comportamento, não psicologia.

---

# 38. Agent Control Standard — 2026

OWASP ACS, lançado em setembro de 2026, enfatiza agentes:

- inspectable;
- traceable;
- instrumentable;
- controláveis em runtime.

A arquitetura correta é:

```math
AgentDecision
\rightarrow
PolicyHook
\rightarrow
Allow/Transform/Deny
\rightarrow
Execution
```

não:

```math
AgentDecision\rightarrow Execution
```

---

# 39. Output handling

Output do modelo pode chegar a:

- HTML;
- Markdown renderer;
- shell;
- SQL;
- filesystem path;
- API;
- email;
- browser.

Nunca confundir natural language generation com sanitização.

---

# 40. Structured output helps syntax, not intent

Grammar/schema garante:

```math
y\in\mathcal L(Schema)
```

Não garante:

```math
SemanticallySafe(y)
```

JSON válido ainda pode pedir:

```json
{"action":"delete","target":"production"}
```

---

# 41. Idempotency

Operação crítica deve preferir comportamento:

```math
f(f(s,a),a)=f(s,a)
```

quando semanticamente possível.

Retries então deixam de multiplicar efeitos.

---

# 42. Transactionality

Agrupe operações:

```math
BEGIN
\rightarrow actions
\rightarrow validation
\rightarrow COMMIT/ROLLBACK
```

Para agentes, rollback é um mecanismo de safety/security extremamente valioso.

---

# 43. Bounded retries

Retry infinito é failure amplifier.

```math
N_{retry}\le N_{max}
```

Adicionar:

- backoff;
- error classification;
- stop conditions;
- escalation.

---

# 44. Resource exhaustion / unbounded consumption

Atacante ou loop defeituoso pode provocar:

- huge context;
- infinite tool loop;
- massive image/video resolution;
- enormous batch;
- recursive agent spawning.

Defina budgets:

```math
Tokens\le T_{max}
```

```math
ToolCalls\le C_{max}
```

```math
WallTime\le t_{max}
```

```math
Cost\le \$_{max}
```

---

# 45. Model denial of service

Inputs patológicos podem amplificar compute/memory.

Exemplo LLM:

```math
ContextLength\uparrow
\Rightarrow
KV\uparrow
```

Exemplo vídeo:

```math
T\times H\times W\uparrow
\Rightarrow
Compute/Memory\uparrow\uparrow
```

Veja [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 46. Adversarial robustness

Perturbação:

```math
x'=x+\delta
```

com:

```math
\|\delta\|\le\epsilon
```

Robustez deseja:

```math
f(x')\approx f(x)
```

para perturbações irrelevantes semanticamente.

---

# 47. Discrete adversarial space

Em texto, $`\delta`$ não é simplesmente ruído contínuo.

Pode ser:

- typo;
- homoglyph;
- unicode;
- paraphrase;
- token boundary attack;
- whitespace;
- prompt restructuring.

Medida de distância precisa ser semanticamente apropriada.

---

# 48. Multimodal adversarial input

Ataque pode existir apenas em imagem/áudio enquanto texto parece benigno.

```math
Input=(Text,Image)
```

com:

```math
Text=safe
```

mas:

```math
Image=adversarial
```

VLM security precisa avaliar todas as modalities.

---

# 49. OOD / distribution shift

Treino:

```math
x\sim P_{train}
```

Deployment:

```math
x\sim P_{deploy}
```

Se:

```math
P_{deploy}\neq P_{train}
```

performance pode degradar sem qualquer atacante.

Isso é robustness/reliability, não necessariamente security.

---

# 50. Calibration under shift

Modelo pode manter accuracy razoável e perder calibration:

```math
Confidence\not\approx CorrectnessProbability
```

sob domain shift.

Risk-based systems devem monitorar calibration drift.

---

# 51. Hallucination como failure mode

Hallucination é output não sustentado pelo estado/evidência relevante.

Não é uma vulnerabilidade isolada, mas pode virar exploit quando downstream confia automaticamente.

```math
Hallucination
+ExcessiveAgency
\rightarrow
OperationalIncident
```

---

# 52. Retrieval grounding não elimina hallucination

Mesmo com docs corretos:

- retrieval pode falhar;
- context pode ser ignorado;
- synthesis pode errar;
- documentos podem contradizer.

```math
RAG\neq TruthOracle
```

---

# 53. Verifier correlation risk

Se generator e verifier compartilham erro:

```math
P(V accepts\ wrong\ output)
```

pode ser alto.

Diversidade arquitetural/evidência externa reduz erro correlacionado.

Veja [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 54. Privacy attacks

Classes relevantes:

- membership inference;
- model inversion;
- memorization extraction;
- prompt/context exfiltration;
- vector-store leakage;
- logging leaks.

Privacidade não é garantida por rodar “IA” isoladamente se logs/context continuam expostos.

---

# 55. Membership inference

Pergunta:

```math
Was\ x\in D_{train}?
```

Atacante explora diferenças estatísticas de comportamento/confidence.

Risco depende de:

- overfitting;
- data rarity;
- access level;
- model exposure.

---

# 56. Model extraction / theft

Objetivos:

- copiar comportamento;
- reconstruir weights parcialmente;
- inferir proprietary prompt/data.

Controls:

- access control;
- rate limiting;
- anomaly detection;
- watermarking/provenance como sinal auxiliar, não defesa única.

---

# 57. Local AI security — vantagens e ilusões

Rodar local reduz alguns fluxos para terceiros.

Mas adiciona:

- model downloads;
- community binaries;
- custom nodes;
- local API servers;
- web UIs;
- exposed ports;
- weak authentication.

```math
Local\neq SecureByDefault
```

---

# 58. Localhost is not a trust boundary

Um serviço em:

```text
127.0.0.1:PORT
```

pode ser acessado por processos locais maliciosos ou por browser-based attack patterns dependendo de configuração/CORS/auth.

Use autenticação e bind conscientemente.

---

# 59. Model server exposure

Se Ollama/LM Studio/KoboldCpp/API server é exposto na LAN/WAN:

verificar:

- authentication;
- TLS;
- bind address;
- CORS;
- rate limits;
- file/tool capabilities;
- reverse proxy policy.

Não exponha “porque é só inferência”.

---

# 60. ComfyUI-specific risk model

Separar:

## Model files

weights/checkpoints.

## Workflows

podem referenciar paths/nodes.

## Custom nodes

executam Python.

## Manager/installers

baixam software/dependencies.

O risco maior frequentemente não está no `.safetensors`, mas no ecossistema executável ao redor.

---

# 61. SillyTavern/tool extension risk

Extensions/scripts podem acessar:

- frontend context;
- endpoints;
- local storage;
- external services.

Treat extension installation as software supply-chain event.

---

# 62. Integrity via hashing

Para artefato:

```math
h=SHA256(file)
```

Pinning por hash permite detectar alteração.

Mas hash não responde:

> “este artefato era confiável originalmente?”

Ele prova identidade, não benignidade.

---

# 63. Provenance manifest

Registre:

```yaml
artifact:
  source: ...
  repo_revision: ...
  filename: ...
  sha256: ...
  license: ...
  remote_code: false
  custom_ops: false
  reviewed: ...
```

Especialmente para modelos, nodes e adapters.

---

# 64. Sandbox

Princípio:

```math
Compromise(component)
\not\Rightarrow
Compromise(host)
```

Use isolamento:

- container;
- VM;
- restricted filesystem;
- network policy;
- low-privilege user.

Quanto mais agentic/código, maior valor da sandbox.

---

# 65. Network egress control

Se agente não precisa internet:

```math
Egress=deny
```

Se precisa apenas hosts específicos:

```math
Egress\subset Allowlist
```

Isso reduz exfiltration blast radius.

---

# 66. Secret management

Nunca passar segredo ao modelo se não é necessário.

Tool deve usar credential internamente:

```text
model → call tool(action)
tool → inject secret outside model context
```

em vez de:

```text
secret → prompt → model → tool
```

---

# 67. Logs como attack surface

Logs podem conter:

- prompts;
- private docs;
- tokens;
- tool args;
- credentials acidentalmente retornadas.

Defina:

- retention;
- redaction;
- access control;
- encryption;
- sampling.

---

# 68. Observability de segurança

Capture eventos estruturados:

```math
Event=(actor,action,target,result,policy,trace_id,time)
```

Para agentes, auditabilidade depende de trace completo de ação.

---

# 69. Detection versus prevention

Nenhum controle é perfeito.

Camadas:

## Prevent

bloquear ação.

## Detect

identificar comportamento suspeito.

## Contain

limitar blast radius.

## Recover

rollback/revoke/rebuild.

Defense in depth:

```math
Risk_{residual}
\approx
Risk_0
\prod_i(1-E_i)
```

apenas como intuição; controles não são independentes na prática.

---

# 70. Circuit breaker

Se métrica excede limite:

```math
FailureRate>\tau
```

ou:

```math
Cost>Budget
```

então:

```math
AgentExecution\rightarrow Stop
```

Evita cascata.

---

# 71. Runtime policy enforcement

2026 reforça uma mudança importante:

policy não deve existir apenas no prompt.

Arquitetura:

```text
LLM proposal
    ↓
policy middleware
    ↓
authz / risk check
    ↓
tool execution
    ↓
postcondition check
```

Isso é compatível com a direção do OWASP Agent Control Standard.

---

# 72. Security evaluation

Um sistema seguro precisa de testes como:

- direct prompt injection;
- indirect injection;
- poisoned retrieval;
- privilege escalation;
- tool misuse;
- memory poisoning;
- data exfiltration;
- resource exhaustion;
- malformed structured output;
- replay/retry edge cases.

Veja [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

---

# 73. Red-team versus benchmark

Benchmark:

```math
fixed\ distribution
```

Red-team:

```math
adaptive\ adversary
```

Atacante aprende com falhas do sistema.

Ambos são necessários.

---

# 74. Attack success rate

```math
ASR=
\frac{successful\ attacks}{attempts}
```

Sempre reportar junto com:

- attack class;
- threat model;
- permissions;
- number of retries;
- model/system version.

ASR sem contexto é pouco comparável.

---

# 75. Robustness curve

Em vez de um ponto, variar perturbação:

```math
Q(\epsilon)
```

Onde:

```math
\epsilon=attack\ strength / noise / shift
```

A área/declive da curva é mais informativa que um threshold arbitrário.

---

# 76. Risk model

Uma aproximação útil:

```math
Risk
=Likelihood\times Impact
```

Para agentes, expandir:

```math
Impact
=f(
Privilege,
Reach,
Irreversibility,
Sensitivity
)
```

Essa função orienta onde exigir HITL ou deterministic checks.

---

# 77. Failure taxonomy por camada

| Camada | Falha típica |
|---|---|
| `DATA` | poisoning, contamination |
| `MODEL` | backdoor, memorization, hallucination |
| `CONTEXT` | prompt injection, context poisoning |
| `RETRIEVAL` | poisoned corpus, auth leakage |
| `INFERENCE` | resource abuse, pathological settings |
| `TOOL` | misuse, privilege escalation |
| `AGENT` | goal hijack, cascading failure |
| `RUNTIME` | unsafe code/dependency/parser |
| `HUMAN` | automation bias, approval exploitation |

---

# 78. Control matrix

| Risco | Prevent | Detect | Contain/Recover |
|---|---|---|---|
| prompt injection | isolate content/capabilities | injection telemetry | deny action / reset context |
| RAG poison | signed/curated sources | provenance anomaly | remove doc/rebuild index |
| tool misuse | narrow APIs/authz | action logs | rollback/revoke token |
| memory poison | write policy | memory audit | delete/quarantine memory |
| supply chain | pin/hash/review | integrity monitoring | isolate/rebuild env |
| unbounded use | quotas | budget telemetry | circuit breaker |
| bad output | schema + semantic checks | validation failures | reject/retry/escalate |

---

# 79. NIST framing

NIST AI RMF GenAI Profile trata riscos ao longo do lifecycle, não apenas no momento de prompt.

Isso é compatível com esta coleção:

```math
Data
\rightarrow Training
\rightarrow Evaluation
\rightarrow Deployment
\rightarrow Monitoring
```

Security/robustness precisa atravessar todos.

---

# 80. OWASP snapshot 2026

Em agosto de 2026, OWASP publicou o **GenAI LLM Top 10 2026**, atualizado com base em incidentes reais e mapeamentos para NIST/MITRE/CWE e Agentic Top 10.

Em setembro de 2026, publicou o **Agent Control Standard**, enfatizando controle/instrumentação runtime.

Isso confirma uma mudança estrutural:

> segurança de IA deixou de ser apenas “filtrar prompts” e passou a ser **engenharia de controle sobre um sistema com agência, memória, tools e supply chain**.

---

# 81. Agentic Top 10 — classes úteis para nosso mapa

A taxonomia publicada pela OWASP para agentic systems inclui:

1. Agent Goal Hijack;
2. Tool Misuse;
3. Identity & Privilege Abuse;
4. Agentic Supply Chain Vulnerabilities;
5. Unexpected Code Execution;
6. Memory & Context Poisoning;
7. Insecure Inter-Agent Communication;
8. Cascading Failures;
9. Human-Agent Trust Exploitation;
10. Rogue Agents.

Essas categorias mapeiam diretamente para [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md).

---

# 82. Segurança não é prompt engineering

Uma regra que vale preservar:

```math
SecurityControl
\not\subseteq
SystemPrompt
```

Prompt pode ajudar comportamento.

Security boundary deve existir em:

- identity;
- authorization;
- sandbox;
- policy middleware;
- validation;
- transaction;
- network;
- filesystem;
- audit.

---

# 83. Incident response para sistemas AI

Plano mínimo:

1. identificar trace/session/artifact;
2. bloquear/revogar credenciais;
3. conter tool/network access;
4. preservar logs/forensics;
5. determinar input/context/memory source;
6. identificar versões de model/runtime/plugins;
7. corrigir control plane;
8. limpar memories/indexes contaminados;
9. rerun adversarial regression;
10. atualizar threat model.

Não basta “melhorar o prompt”.

---

# 84. Security regression suite

Mantenha casos versionados:

```text
PI-direct
PI-indirect
RAG-poison
memory-poison
unauthorized-read
unauthorized-write
credential-exfil
shell-injection
retry-double-action
budget-exhaustion
malformed-json
multimodal-injection
```

Toda mudança de modelo/scaffold/runtime roda a suite.

---

# 85. Local lab hardening checklist

1. Checksum de models importantes.
2. Preferir `safetensors` quando ecossistema permitir.
3. Evitar pickle desconhecido.
4. Revisar `trust_remote_code`.
5. Custom nodes em ambiente isolado.
6. Pin de dependencies.
7. APIs locais com bind/auth explícitos.
8. Sem exposição WAN acidental.
9. Segregar secrets do model context.
10. Tools com least privilege.
11. Logs com redaction.
12. Backups antes de agentes com write access.
13. Destructive actions com approval/transaction.
14. Egress control quando possível.
15. Audit trail de ações.

---

# 86. A equação final

```math
\boxed{
SecureAI
\neq
SafeModel
}
```

Mais precisamente:

```math
SecureSystem
=
f(
Model,
Data,
Context,
Identity,
Authorization,
Tools,
Runtime,
Observability,
Recovery
)
```

O modelo é apenas um componente dentro do threat surface.

---

# Checklist para dissecar risco de qualquer sistema

1. Qual o asset?
2. Quem é atacante plausível?
3. Quais inputs não confiáveis?
4. Quais fontes externas entram no context?
5. Há memory persistente?
6. Há retrieval?
7. Retrieval respeita authorization antes de retornar conteúdo?
8. Há tools?
9. Quais permissions?
10. Tool é narrow ou open-ended?
11. Há shell/code execution?
12. Há HITL para ações irreversíveis?
13. Approval UI mostra efeito real?
14. Há policy enforcement fora do prompt?
15. Há sandbox?
16. Há network egress control?
17. Secrets entram no context?
18. Logs podem vazar dados?
19. Model/artifact tem provenance/hash?
20. Há remote code/custom nodes?
21. Dependencies estão pinned?
22. Há rate/cost/token limits?
23. Retry é bounded/idempotent?
24. Há rollback?
25. Há security regression suite?
26. Há adversarial eval?
27. Há incident response plan?
28. Falha de um componente compromete host inteiro?
29. Existe blast-radius boundary?
30. O modelo é tratado como untrusted component?

---

# Referências snapshot

- OWASP GenAI LLM Top 10 2026 — https://genai.owasp.org/resource/owasp-genai-llm-top-10-2026/
- OWASP Top 10 for Agentic Applications — https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/
- OWASP Agent Control Standard — https://genai.owasp.org/resource/agent-control-standard-acs/
- OWASP GenAI Top 10 initiative — https://genai.owasp.org/initiatives/top-10-for-llm-and-genai/
- NIST AI RMF Generative AI Profile — https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence
- NIST AI RMF — https://www.nist.gov/itl/ai-risk-management-framework
- Hugging Face Safetensors — https://huggingface.co/docs/safetensors/
