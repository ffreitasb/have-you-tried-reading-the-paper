---
title: LLM & Parallel Language Inference Datasheet v3.0
tags: [ai, llm, transformer, sampling, kv-cache, inference, diffusion-language, parallel-decoding, reasoning]
updated: 2026-10-01
---

# LLM & Parallel Language Inference Datasheet v3.0

> Um LLM não é um gerador de frases. É uma máquina que transforma uma sequência de estados vetoriais em uma distribuição sobre o próximo token — repetidamente.

## 1. Grafo computacional canônico

```math
text\rightarrow tokenizer\rightarrow embeddings\rightarrow blocks_{1:L}\rightarrow norm\rightarrow LM\ head\rightarrow logits\rightarrow logit\ processing\rightarrow sampler\rightarrow token
```

Com cache:

```math
(K,V)_{1:L,1:t-1}\rightarrow attention_t\rightarrow (K,V)_{1:L,1:t}
```

A interface normalmente mostra apenas a etapa **logits → sampler**. O restante determina a maior parte da capacidade e do custo.

---

# PARTE I — REPRESENTAÇÃO

## 2. Tokenizer

```math
s\xrightarrow{Tokenizer}(x_1,x_2,\dots,x_T)
```

### Variáveis fundamentais

| Variável | Tag | O que controla |
|---|---|---|
| Vocabulary size $`V`$ | `MODEL` | dimensão da distribuição de saída |
| Tokenization algorithm | `MODEL` | granularidade da sequência |
| Special tokens | `MODEL` | BOS/EOS/FIM/chat control |
| Chat template | `MODEL/PIPE` | serialização real do diálogo |

### Relação física

Para a mesma informação semântica:

```math
T\downarrow\Rightarrow prefill\downarrow,\ KV\downarrow
```

mas vocabulário maior aumenta LM head/embedding e muda a geometria estatística dos tokens.

### Failure surface

Um modelo correto com **chat template incorreto** pode parecer burro, repetitivo ou desobediente sem que o sampling esteja errado.

---

## 3. Embeddings e residual stream

Entrada inicial simplificada:

```math
h_t^{(0)}=E[x_t]
```

O residual stream percorre os blocos:

```math
h^{(l+1)}=h^{(l)}+Attention(Norm(h^{(l)}))+FFN/MoE(\cdot)
```

A arquitetura exata pode ser pre-norm/post-norm, RMSNorm/LayerNorm e usar residual arrangements distintos.

---

# PARTE II — POSIÇÃO E ATENÇÃO

## 4. RoPE

Rotary Position Embeddings aplicam rotações dependentes da posição a Q/K.

Em forma conceitual:

```math
q'_t=R(t)q_t,\qquad k'_t=R(t)k_t
```

A atenção passa a depender de posição relativa através do produto interno rotacionado.

### Knobs associados

- RoPE theta/base;
- frequency scaling;
- linear scaling;
- YaRN factors;
- original context length;
- extension factor.

### Regra

```math
context\ extension\neq context\ training
```

Conseguir alocar 128k tokens não prova que o modelo preserve qualidade equivalente em 128k.

---

## 5. Attention

Para cada camada:

```math
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
```

```math
A(Q,K,V)=softmax\left(\frac{QK^\top}{\sqrt{d_h}}+M\right)V
```

onde $`M`$ contém a máscara causal e possíveis biases.

### Shapes típicos

```math
Q\in\mathbb{R}^{B\times n_q\times T\times d_h}
```

```math
K,V\in\mathbb{R}^{B\times n_{kv}\times T\times d_h}
```

---

## 6. MHA, GQA, MQA

### Multi-Head Attention

```math
n_{kv}=n_q
```

### Grouped-Query Attention

```math
n_{kv}<n_q
```

Várias query heads compartilham K/V.

### Multi-Query Attention

```math
n_{kv}=1
```

### Efeito direto

```math
M_{KV}\propto n_{kv}
```

GQA/MQA são, entre outras coisas, mecanismos de redução de estado persistente durante decode.

---

## 7. Multi-head Latent Attention — MLA

Em vez de armazenar K/V completos por cabeça, a arquitetura comprime estados para latentes menores e reconstrói/projeta conforme necessário.

Conceitualmente:

```math
h_t\rightarrow c_t^{KV}\ll (K_t,V_t)_{full}
```

Isso reduz pressão do KV cache. DeepSeek-V3 é referência importante dessa família.

Não usar automaticamente a fórmula de KV de GQA para modelos MLA sem consultar a arquitetura/backend.

---

# PARTE III — FFN E MoE

## 8. Feed-Forward Network

Uma forma comum com gated activation:

```math
FFN(x)=W_2\left(\phi(W_gx)\odot W_1x\right)
```

Em Transformers modernos, FFN representa grande parte dos parâmetros e do tráfego de memória.

---

## 9. Mixture of Experts

Router:

```math
g(x)=softmax(W_rx)
```

Escolha:

```math
S=TopK(g(x))
```

Saída:

```math
y=\sum_{i\in S}g_i(x)E_i(x)
```

### Três números obrigatórios

| Métrica | Significado |
|---|---|
| $`N_{total}`$ | parâmetros armazenados |
| $`N_{active}`$ | parâmetros efetivamente executados/token |
| $`k`$ | experts selecionados/token |

### Regra operacional

```math
compute/token\sim N_{active}
```

mas:

```math
storage\sim N_{total}
```

Um MoE pode ser computacionalmente “3B ativo” e ainda exigir armazenamento equivalente a dezenas de bilhões de parâmetros.

---

# PARTE IV — LOGITS

## 10. LM head

Estado final:

```math
h_t\in\mathbb{R}^{d}
```

Logits:

```math
z=W_{vocab}h_t+b
```

```math
z\in\mathbb{R}^{V}
```

Antes de sampling, ainda **não** são probabilidades.

Softmax:

```math
p_i=\frac{e^{z_i}}{\sum_j e^{z_j}}
```

---

# PARTE V — LOGIT PROCESSING E SAMPLING

## 11. Temperature

```math
p_i(T)=\frac{e^{z_i/T}}{\sum_j e^{z_j/T}}
```

| Região | Efeito matemático |
|---|---|
| $`T<1`$ | distribuição mais concentrada |
| $`T=1`$ | distribuição original |
| $`T>1`$ | distribuição mais plana |
| $`T\to0`$ | aproxima argmax/greedy |

**Temperature não significa criatividade.** Criatividade é um correlato emergente da mudança na distribuição.

---

## 12. Top-K

Retém apenas:

```math
S=TopK(z,K)
```

e mascara o restante.

É um limite absoluto de cardinalidade do suporte.

### Caveat

Um `K=40` é igualmente rígido em uma distribuição plana e em uma distribuição extremamente concentrada. Por isso é menos adaptativo que Min-P/Top-P.

---

## 13. Top-P / Nucleus

Ordene probabilidades decrescentes e escolha o menor conjunto $`S`$ tal que:

```math
\sum_{i\in S}p_i\ge P
```

Cardinalidade do suporte varia dinamicamente.

---

## 14. Min-P

Critério:

```math
p_i\ge p_{min}\cdot p_{max}
```

Se $`p_{max}=0.8`$ e `min_p=0.05`:

```math
p_i\ge0.04
```

Em termos de logits, antes de transformações adicionais:

```math
z_i-z_{max}\gtrsim\ln(p_{min})
```

O corte se adapta à confiança do modelo.

---

## 15. Typical sampling

Typical sampling favorece tokens cuja surprisal fica próxima da entropia local:

```math
I(x_i)=-\log p_i
```

```math
H(p)=-\sum_i p_i\log p_i
```

Tokens muito previsíveis ou muito improváveis podem ser removidos se forem “atípicos” em relação à distribuição.

---

## 16. Top-N-Sigma

Família de filtros que usa estatísticas da distribuição de logits/probabilidades para remover cauda com threshold adaptativo baseado em dispersão. É backend-specific; documentar implementação concreta antes de inferir equivalência com Min-P.

---

## 17. XTC

XTC busca aumentar diversidade removendo probabilisticamente alguns tokens excessivamente prováveis sob certas condições. É um mecanismo de shaping de suporte, não um substituto matematicamente equivalente a temperature.

Use como `BACKEND/INF`, não como propriedade universal de LLMs.

---

## 18. Presence/Frequency penalties

Forma conceitual OpenAI-style:

```math
z_i'=z_i-\alpha\cdot 1[c_i>0]-\beta\cdot c_i
```

onde:

- $`\alpha`$: presence penalty;
- $`\beta`$: frequency penalty;
- $`c_i`$: contagem do token no histórico considerado.

---

## 19. Repetition penalty

Implementações variam; uma forma comum modifica logits diferentemente conforme sinal e presença prévia.

Não trate como simplesmente “dividir probabilidade por X”. É backend-specific.

### Failure surface

Penalidade alta pode punir:

- palavras funcionais;
- nomes próprios necessários;
- sintaxe de código;
- padrões estruturais legítimos.

---

## 20. DRY — sequência, não token

DRY penaliza repetição de sequências/n-grams crescentes. Conceitualmente, se uma extensão de sequência já ocorreu, aplica penalidade crescente conforme comprimento repetido.

É particularmente útil quando:

```math
repetition\ problem\neq repeated\ individual\ tokens
```

RP e narrativa se beneficiam porque vícios frequentemente são frases inteiras.

---

## 21. Adaptive-P

O `llama.cpp` moderno implementa um sampler realimentado que mantém EMA da probabilidade original dos tokens escolhidos e ajusta o target ao longo da geração.

Conceitualmente:

```math
\bar p_t=\lambda\bar p_{t-1}+(1-\lambda)p(x_t)
```

O sampler tenta selecionar tokens próximos de um target adaptativo.

Isso é diferente de um filtro estático: há **estado interno do sampler**.

---

## 22. Mirostat

Controlador feedback-oriented para manter surprisal/perplexity próxima de um alvo.

Princípio:

```math
error_t=\tau-surprisal_t
```

```math
control_{t+1}=control_t+\eta\cdot error_t
```

Implementação exata depende da versão. Classificar como **adaptive controller**, não simplesmente “temperature automática”.

---

# PARTE VI — CONSTRAINED DECODING

## 23. Grammar / JSON Schema

Em cada passo, existe um conjunto de tokens lexicalmente/sintaticamente válidos:

```math
V_t^{valid}\subseteq V
```

O sampler é restringido:

```math
p_t'(x)=0\quad\forall x\notin V_t^{valid}
```

### Importante

```math
syntax\ validity\neq semantic\ correctness
```

JSON perfeito pode conter um argumento inventado ou uma ação errada.

---

# PARTE VII — ESTADO E CUSTO

## 24. KV cache

Para GQA/MHA:

```math
M_{KV}\approx2LTn_{kv}d_hbB
```

É linear em contexto armazenado.

### “Quanto custa +1k tokens?”

```math
\Delta M_{KV,1k}=2000Ln_{kv}d_hbB
```

Faça essa conta antes de decidir contexto.

---

## 25. Prefill e decode

### Prefill

Transforma todo o prompt e constrói KV.

### Decode

Repete:

```math
h_t\rightarrow logits_t\rightarrow token_{t+1}\rightarrow KV_{t+1}
```

A latência/token cresce com estado e arquitetura.

---

## 26. Context window: quatro limites diferentes

1. **config maximum** — runtime aceita;
2. **positional encoding range** — RoPE/scaling suporta;
3. **training distribution** — modelo viu durante treino;
4. **effective context** — informação realmente utilizada com qualidade.

Não confundir os quatro.

---

# PARTE VIII — REASONING E BUDGET

## 27. Reasoning tokens / thinking budget

Em modelos que externalizam ou internalizam etapas adicionais, mais budget significa mais inferência sequencial:

```math
Cost\propto T_{generated}
```

Não é um novo tipo de matemática de atenção; é principalmente uma mudança na política de geração/treinamento e no orçamento de tokens/computation.

### Caveat

Mais reasoning budget não garante monotonicamente melhor resposta.

---

# PARTE IX — COUPLING MATRIX

## 28. Relações principais

| Controle ↑ | Entropia | Support | Repetição | KV | Latência | Comentário |
|---|---:|---:|---:|---:|---:|---|
| Temperature | ↑ | = | geralmente ↓ | = | ~ | pode aumentar incoerência |
| Top-K | — | ↓ | pode ↑ | = | ~ | corte absoluto |
| Top-P mais restritivo | ↓ | ↓ | pode ↑ | = | ~ | adaptativo cumulativo |
| Min-P mais alto | ↓ | ↓ | pode ↑ | = | ~ | relativo ao top token |
| Rep penalty | variável | variável | ↓ lexical | = | ~ | pode ferir sintaxe |
| DRY | variável | variável | ↓ sequencial | = | pequeno | ótimo contra loops longos |
| Context | — | — | variável | ↑ linear | ↑ | possível quality gain/loss |
| KV precision | ~ | = | = | ↑ com bits | pode variar | accuracy/runtime dependent |
| Batch/parallel | — | — | — | ↑ | throughput ↑ | latency individual pode subir |

---

# PARTE X — MAPEAMENTO PARA STACK LOCAL

## 29. SillyTavern

A UI deve ser lida como **control plane**. Ela não define a matemática; envia parâmetros ao backend.

Verificar sempre:

- sampler order;
- quais samplers o backend ignora;
- stop strings;
- context size;
- instruct/chat template;
- system prompt injection;
- grammar/JSON schema quando aplicável.

## 30. KoboldCpp / llama.cpp

Em 2026 o conjunto inclui, entre outros:

- penalties;
- DRY;
- top-n-sigma;
- top-k;
- typical;
- top-p;
- min-p;
- XTC;
- temperature;
- adaptive-p;
- grammar;
- quantized KV;
- speculative decoding.

A ordem é uma propriedade do backend/configuração. Não escrever “a ordem universal é X”.

## 31. LM Studio / Ollama

Tratar como frontends/runtimes com defaults próprios. Para benchmark técnico, fixar:

- mesmo GGUF/checkpoint;
- mesma template;
- mesmo context;
- mesmos samplers;
- mesma seed;
- mesma quantização KV;
- mesmo GPU offload.

Caso contrário, comparar “modelo A vs B” vira comparar pipelines diferentes.

---

# PARTE XI — PROTOCOLO EXPERIMENTAL

## 32. Sweep científico de sampling

1. Fixar prompt/template/context/seed/backend/model.
2. Registrar top logits/probabilities por token se possível.
3. Alterar **uma família** de controle por vez.
4. Medir:
   - entropy;
   - support size;
   - repetition rate;
   - unique n-grams;
   - task accuracy;
   - subjective quality.
5. Repetir em múltiplas seeds — uma seed é um ponto, não uma distribuição.

---

# PARTE XII — FAILURE DIAGNOSTICS

## 33. Sintoma → hipótese

| Sintoma | Investigar primeiro |
|---|---|
| frases repetidas | DRY / context injection / low entropy |
| sinônimos estranhos | rep penalty excessiva |
| texto incoerente | temp/support muito aberto / model limit |
| resposta truncada | max tokens / EOS / stop strings |
| desobediência | template/system/conditioning antes de sampling |
| qualidade cai em contexto longo | RoPE regime/effective context/KV precision |
| TPS despenca | context/KV/offload/bandwidth |
| JSON inválido | grammar/schema, não temperature somente |

---

## 34. Snapshot 2026

- DeepSeek-V3: 671B total, 37B ativos/token, MLA + DeepSeekMoE.
- Qwen3-Coder-Next: 80B total, ~3B ativos durante inferência, evidenciando importância de separar total/active parameters.
- llama.cpp: sampling moderno inclui DRY, XTC, top-n-sigma e adaptive-p além do clássico top-k/top-p/min-p.

## Referências

- llama.cpp sampler API — https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h
- llama.cpp completion sampling docs — https://github.com/ggml-org/llama.cpp/blob/master/tools/completion/README.md
- llama.cpp CLI/runtime — https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md
- DeepSeek-V3 — https://arxiv.org/abs/2412.19437
- Qwen3-Coder-Next — https://arxiv.org/abs/2603.00729

---

# PARTE XIII — PARALLEL / MASKED / DIFFUSION LANGUAGE MODELS

> Transformer não implica autoregressão. A partir daqui, abandonamos a hipótese de que o texto só pode avançar `token1 → token2 → token3`.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

## 35. Autoregressive factorization — baseline

```math
p(x_{1:T})=\prod_{t=1}^{T}p(x_t|x_{<t})
```

Inferência:

```text
x1 -> x2 -> x3 -> ... -> xT
```

A posição $`t+1`$ não existe antes de $`t`$ ser decidido.

### Implicações

- streaming natural;
- KV incremental extremamente eficiente;
- latency cresce com número de output tokens;
- erro/decisão anterior vira conditioning posterior.

---

## 36. Masked language modeling

Defina máscara $`M\subset\{1,\ldots,T\}`$:

```math
\mathcal L=-\sum_{i\in M}\log p(x_i|x_{\setminus M})
```

Diferente de causal AR, uma posição pode usar contexto **dos dois lados**.

Inferência iterativa pode começar com:

```text
[MASK] [MASK] [MASK] [MASK] [MASK]
```

preencher posições de maior confiança, remascar/refinar e repetir.

---

## 37. Discrete diffusion / iterative denoising

Estado textual corrompido:

```math
x_t\sim q(x_t|x_0,t)
```

A rede aprende uma reverse transition:

```math
p_\theta(x_{t-1}|x_t,C)
```

Trajetória:

```math
x_T\rightarrow x_{T-1}\rightarrow\cdots\rightarrow x_0
```

Aqui $`t`$ é **noise/refinement time**, não posição textual.

---

## 38. Parallel token prediction

Se múltiplas posições são atualizadas em um pass:

```math
\{x_i\}_{i\in U_k}
\leftarrow
f_\theta(x^{(k)})
```

onde $`U_k`$ é o conjunto de posições atualizadas na iteração $`k`$.

Isso quebra a identidade:

```math
1\ network\ forward = 1\ output\ token
```

que domina LLMs causais.

---

## 39. Confidence-based unmasking

Cada posição possui confidence:

```math
c_i=\max_v p(x_i=v|x^{(k)})
```

Escolha top posições:

```math
U_k=TopK(c_i,K_k)
```

As mais confiáveis são fixadas antes; as incertas permanecem mascaradas.

### Failure surface

Erro de alta confiança fixado cedo pode contaminar refinamentos posteriores.

---

## 40. Remasking

Uma decisão pode ser revisada:

```math
x_i^{(k)}\rightarrow MASK\rightarrow x_i^{(k+1)}
```

Essa propriedade é estruturalmente diferente de AR puro, onde token emitido normalmente é irreversível sem restart/edit loop externo.

Remasking permite **self-correction dentro da própria topologia de decode**.

---

## 41. Blockwise generation

Compromisso entre AR e full-sequence iterative:

```math
Block_1\rightarrow Block_2\rightarrow\cdots
```

Dentro de cada bloco, múltiplos tokens podem ser refinados paralelamente.

Isso preserva alguma streaming/local causality enquanto reduz número de passos sequenciais.

---

## 42. Sequence length problem

AR não precisa definir comprimento final antecipadamente; EOS decide.

Full-mask generation frequentemente precisa definir/alocar comprimento:

```math
T_{target}
```

Possíveis estratégias:

- length predictor;
- overallocate + EOS/padding;
- blockwise growth;
- insertion/deletion transitions.

Logo “quantos tokens gerar?” vira parte da própria state topology.

---

## 43. KV cache não funciona da mesma forma

Causal AR:

```math
KV_t=KV_{t-1}+KV(x_t)
```

Se posições antigas mudam durante iterative refinement:

```math
x_i^{(k)}\neq x_i^{(k-1)}
```

os estados derivados podem precisar ser recalculados/invalidados.

Portanto o grande truque de runtime do AR — **cachear todo prefixo imutável** — perde parte da vantagem.

Isso é central para comparar velocidade real.

---

## 44. Complexity model: AR

Para $`T_{out}`$ tokens:

```math
Latency_{AR}
\approx
T_{out}\cdot t_{decode-pass}
```

com passes pequenos e KV incremental.

---

## 45. Complexity model: iterative parallel

Para $`K`$ refinement steps:

```math
Latency_{iter}
\approx
K\cdot t_{sequence/block-pass}
```

Vantagem aparece quando:

```math
K\ll T_{out}
```

**e** o custo do pass paralelo não anula a economia.

Logo:

```math
Parallel\ tokens\neq free\ speedup
```

---

## 46. Throughput vs latency

AR pode ter:

- excelente token streaming;
- baixa first-token latency após prefill;
- baixa parallelism no eixo de output.

Iterative models podem ter:

- maior compute por iteration;
- pior streaming natural;
- muito maior paralelismo de output;
- alto aggregate throughput em hardware massivamente paralelo.

A arquitetura ótima depende do hardware e serving regime.

---

## 47. Sampling em diffusion text

Não assumir que `temperature/top-p/min-p` se aplicam igual ao AR.

Podem existir controles em:

- corruption/noise schedule;
- token proposal distribution;
- confidence threshold;
- remasking ratio;
- number of refinement steps;
- block size;
- guidance/conditioning strength;
- stochastic vs deterministic transitions.

Cada implementação precisa ser mapeada para sua equação.

---

## 48. Entropy schedule

Em refinamento ideal:

```math
H(X^{(k+1)})<H(X^{(k)})
```

em média, conforme incerteza é removida.

Mas reduzir entropia cedo demais pode causar premature commitment; manter demais produz instabilidade.

Isso é análogo a annealing, mas implementação específica importa.

---

## 49. Editing advantage

Como sequência inteira pode ser revisitada:

```math
Edit\ subset\ M
```

é natural manter contexto ao redor e regenerar regiões internas.

AR precisa normalmente de FIM, rewrite ou outro mecanismo especial para o mesmo efeito.

---

## 50. Diffusion language model ≠ image diffusion copiado literalmente

Texto é discreto.

Imagem latente típica:

```math
x_t\in\mathbb R^d
```

Texto:

```math
x_t\in\{1,\ldots,V\}^T
```

Corruption/reverse process deve respeitar estado discreto ou usar embeddings/relaxations específicos.

A analogia correta é **iterative denoising**, não “adicionar Gaussian noise em token ID”.

---

## 51. Snapshot: Mercury

Mercury/Mercury Coder mostrou comercial-scale diffusion language models parametrizados por Transformer que predizem múltiplos tokens em paralelo.

O ponto conceitual mais importante:

```math
Transformer\not\Rightarrow AR
```

E o ponto físico:

```math
Speedup
=f(parallel\ updates,iterations,sequence\ pass\ cost,hardware)
```

não apenas “tokens por pass”.

---

# PARTE XIV — INFERENCE-TIME REASONING / TEST-TIME COMPUTE

## 52. Reasoning model não é nova espécie arquitetural

Na maioria dos casos:

```math
ReasoningModel
=
BaseModel
+
PostTraining
+
InferencePolicy
+
ComputeBudget
```

Não criar ontologia separada só porque output contém reasoning trace.

---

## 53. Reasoning budget

Se modelo gera $`T_r`$ tokens intermediários e $`T_a`$ de resposta:

```math
T_{total}=T_r+T_a
```

Runtime:

```math
KV,latency,energy\propto T_{total}
```

Test-time compute compra search/reflection, não capacidade paramétrica nova.

---

## 54. Sampling + verifier loop

Alternativa a uma longa chain:

```math
N\ candidates\rightarrow verifier\rightarrow select
```

ou search iterativo:

```math
Generate\rightarrow Evaluate\rightarrow Expand/Prune
```

Veja [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

## 55. Novo mapa de famílias de linguagem

```text
Language Foundation Models
├─ Causal autoregressive
│  ├─ dense
│  ├─ MoE
│  └─ hybrid attention/SSM
├─ Masked / bidirectional encoders
├─ Iterative / diffusion / parallel generation
├─ Embedding / retrieval encoders
├─ Rerankers / cross-encoders
└─ Reward / verifier / judge models
```

Os três últimos possuem datasheets próprios porque a **saída/objetivo** muda, não apenas o decoding.

---

## Referências adicionais

- Mercury: Ultra-Fast Language Models Based on Diffusion — https://arxiv.org/abs/2506.17298
- Reward/verifier topology — [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- Runtime comparison AR vs iterative text — [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)
