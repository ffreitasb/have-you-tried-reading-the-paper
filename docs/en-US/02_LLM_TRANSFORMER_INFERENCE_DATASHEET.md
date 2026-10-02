---
title: LLM & Parallel Language Inference Datasheet v3.0
tags: [ai, llm, transformer, sampling, kv-cache, inference, diffusion-language, parallel-decoding, reasoning]
updated: 2026-10-01
---

# LLM & Parallel Language Inference Datasheet v3.0

> An LLM is not a sentence generator. It is a machine that repeatedly transforms a sequence of vector states into a distribution over the next token.

## 1. Canonical computational graph

```math
text\rightarrow tokenizer\rightarrow embeddings\rightarrow blocks_{1:L}\rightarrow norm\rightarrow LM\ head\rightarrow logits\rightarrow logit\ processing\rightarrow sampler\rightarrow token
```

With cache:

```math
(K,V)_{1:L,1:t-1}\rightarrow attention_t\rightarrow (K,V)_{1:L,1:t}
```

The interface usually exposes only the **logits → sampler** stage. Everything else determines most of the model's capability and cost.

---

# PART I — REPRESENTATION

## 2. Tokenizer

```math
s\xrightarrow{Tokenizer}(x_1,x_2,\dots,x_T)
```

### Fundamental variables

| Variable | Tag | What it controls |
|---|---|---|
| Vocabulary size $`V`$ | `MODEL` | dimensionality of the output distribution |
| Tokenization algorithm | `MODEL` | sequence granularity |
| Special tokens | `MODEL` | BOS/EOS/FIM/chat control |
| Chat template | `MODEL/PIPE` | actual serialization of the conversation |

### Physical relationship

For the same semantic information:

```math
T\downarrow\Rightarrow prefill\downarrow,\ KV\downarrow
```

but a larger vocabulary increases LM-head/embedding cost and changes the statistical geometry of the tokens.

### Failure surface

A correct model with the **wrong chat template** can look stupid, repetitive, or disobedient even when sampling is configured correctly.

---

## 3. Embeddings and the residual stream

Simplified initial input:

```math
h_t^{(0)}=E[x_t]
```

The residual stream passes through the blocks:

```math
h^{(l+1)}=h^{(l)}+Attention(Norm(h^{(l)}))+FFN/MoE(\cdot)
```

The exact architecture may be pre-norm or post-norm, use RMSNorm or LayerNorm, and employ different residual arrangements.

---

# PART II — POSITION AND ATTENTION

## 4. RoPE

Rotary Position Embeddings apply position-dependent rotations to Q/K.

Conceptually:

```math
q'_t=R(t)q_t,\qquad k'_t=R(t)k_t
```

Attention then becomes position-sensitive through the rotated inner product.

### Associated knobs

- RoPE theta/base;
- frequency scaling;
- linear scaling;
- YaRN factors;
- original context length;
- extension factor.

### Rule

```math
context\ extension\neq context\ training
```

Being able to allocate 128k tokens does not prove the model preserves equivalent quality at 128k.

---

## 5. Attention

For each layer:

```math
Q=XW_Q,\qquad K=XW_K,\qquad V=XW_V
```

```math
A(Q,K,V)=softmax\left(\frac{QK^\top}{\sqrt{d_h}}+M\right)V
```

where $`M`$ contains the causal mask and any additional biases.

### Typical shapes

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

Multiple query heads share K/V.

### Multi-Query Attention

```math
n_{kv}=1
```

### Direct effect

```math
M_{KV}\propto n_{kv}
```

Among other things, GQA/MQA are mechanisms for reducing persistent state during decode.

---

## 7. Multi-head Latent Attention — MLA

Instead of storing full K/V tensors per head, the architecture compresses states into smaller latents and reconstructs/projects them as needed.

Conceptually:

```math
h_t\rightarrow c_t^{KV}\ll (K_t,V_t)_{full}
```

This reduces KV-cache pressure. DeepSeek-V3 is an important reference for this family.

Do not automatically apply the GQA KV formula to MLA models without checking the actual architecture/backend.

---

# PART III — FFN AND MoE

## 8. Feed-Forward Network

A common gated formulation:

```math
FFN(x)=W_2\left(\phi(W_gx)\odot W_1x\right)
```

In modern Transformers, FFNs account for a large fraction of both parameters and memory traffic.

---

## 9. Mixture of Experts

Router:

```math
g(x)=softmax(W_rx)
```

Selection:

```math
S=TopK(g(x))
```

Output:

```math
y=\sum_{i\in S}g_i(x)E_i(x)
```

### Three mandatory numbers

| Metric | Meaning |
|---|---|
| $`N_{total}`$ | stored parameters |
| $`N_{active}`$ | parameters actually executed per token |
| $`k`$ | experts selected per token |

### Operational rule

```math
compute/token\sim N_{active}
```

but:

```math
storage\sim N_{total}
```

An MoE can be computationally “3B active” while still requiring storage equivalent to tens of billions of parameters.

---

# PART IV — LOGITS

## 10. LM head

Final state:

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

Before sampling, these are **not yet probabilities**.

Softmax:

```math
p_i=\frac{e^{z_i}}{\sum_j e^{z_j}}
```

---

# PART V — LOGIT PROCESSING AND SAMPLING

## 11. Temperature

```math
p_i(T)=\frac{e^{z_i/T}}{\sum_j e^{z_j/T}}
```

| Region | Mathematical effect |
|---|---|
| $`T<1`$ | more concentrated distribution |
| $`T=1`$ | original distribution |
| $`T>1`$ | flatter distribution |
| $`T\to0`$ | approaches argmax/greedy |

**Temperature does not mean creativity.** Creativity is an emergent correlate of changing the distribution.

---

## 12. Top-K

Keeps only:

```math
S=TopK(z,K)
```

and masks the rest.

It is an absolute cardinality limit on the support.

### Caveat

A `K=40` is equally rigid under a flat distribution and an extremely concentrated one. That makes it less adaptive than Min-P/Top-P.

---

## 13. Top-P / Nucleus

Sort probabilities in descending order and choose the smallest set $`S`$ such that:

```math
\sum_{i\in S}p_i\ge P
```

The support cardinality changes dynamically.

---

## 14. Min-P

Criterion:

```math
p_i\ge p_{min}\cdot p_{max}
```

If $`p_{max}=0.8`$ and `min_p=0.05`:

```math
p_i\ge0.04
```

In logit terms, before additional transformations:

```math
z_i-z_{max}\gtrsim\ln(p_{min})
```

The cutoff adapts to the model's confidence.

---

## 15. Typical sampling

Typical sampling favors tokens whose surprisal lies near the local entropy:

```math
I(x_i)=-\log p_i
```

```math
H(p)=-\sum_i p_i\log p_i
```

Tokens that are too predictable or too improbable may be removed if they are “atypical” relative to the distribution.

---

## 16. Top-N-Sigma

A family of filters that uses statistics of the logit/probability distribution to trim the tail with an adaptive threshold based on dispersion. This is backend-specific; document the concrete implementation before assuming equivalence with Min-P.

---

## 17. XTC

XTC aims to increase diversity by probabilistically removing some overly likely tokens under certain conditions. It is a support-shaping mechanism, not a mathematically equivalent substitute for temperature.

Treat it as `BACKEND/INF`, not as a universal property of LLMs.

---

## 18. Presence/Frequency penalties

Conceptual OpenAI-style form:

```math
z_i'=z_i-\alpha\cdot 1[c_i>0]-\beta\cdot c_i
```

where:

- $`\alpha`$: presence penalty;
- $`\beta`$: frequency penalty;
- $`c_i`$: token count over the relevant history.

---

## 19. Repetition penalty

Implementations vary; one common formulation modifies logits differently depending on their sign and whether the token appeared previously.

Do not treat it as merely “divide probability by X.” It is backend-specific.

### Failure surface

An aggressive repetition penalty may punish:

- function words;
- necessary proper names;
- code syntax;
- legitimate structural patterns.

---

## 20. DRY — sequence, not token

DRY penalizes repetition of increasingly long sequences/n-grams. Conceptually, if a sequence extension has already occurred, the penalty grows with repeated length.

It is particularly useful when:

```math
repetition\ problem\neq repeated\ individual\ tokens
```

RP and long-form narrative benefit because stylistic loops often recur as entire phrases.

---

## 21. Adaptive-P

Modern `llama.cpp` implements a feedback sampler that maintains an EMA of the original probability of selected tokens and adjusts its target throughout generation.

Conceptually:

```math
\bar p_t=\lambda\bar p_{t-1}+(1-\lambda)p(x_t)
```

The sampler tries to select tokens near an adaptive target.

This differs from a static filter: the sampler has **internal state**.

---

## 22. Mirostat

A feedback-oriented controller designed to keep surprisal/perplexity near a target.

Principle:

```math
error_t=\tau-surprisal_t
```

```math
control_{t+1}=control_t+\eta\cdot error_t
```

Exact implementation depends on the version. Classify it as an **adaptive controller**, not merely “automatic temperature.”

---

# PART VI — CONSTRAINED DECODING

## 23. Grammar / JSON Schema

At each step there is a set of lexically/syntactically valid tokens:

```math
V_t^{valid}\subseteq V
```

The sampler is constrained:

```math
p_t'(x)=0\quad\forall x\notin V_t^{valid}
```

### Important

```math
syntax\ validity\neq semantic\ correctness
```

Perfect JSON can still contain a fabricated argument or the wrong action.

---

# PART VII — STATE AND COST

## 24. KV cache

For GQA/MHA:

```math
M_{KV}\approx2LTn_{kv}d_hbB
```

It scales linearly with stored context.

### “How much does +1k tokens cost?”

```math
\Delta M_{KV,1k}=2000Ln_{kv}d_hbB
```

Do this calculation before choosing a context size.

---

## 25. Prefill and decode

### Prefill

Processes the full prompt and builds the KV cache.

### Decode

Repeats:

```math
h_t\rightarrow logits_t\rightarrow token_{t+1}\rightarrow KV_{t+1}
```

Latency per token grows with state size and architecture.

---

## 26. Context window: four different limits

1. **config maximum** — the runtime accepts it;
2. **positional encoding range** — RoPE/scaling can represent it;
3. **training distribution** — the model actually saw it during training;
4. **effective context** — information is genuinely used with useful quality.

Do not conflate the four.

---

# PART VIII — REASONING AND BUDGET

## 27. Reasoning tokens / thinking budget

In models that externalize or internalize additional reasoning steps, a larger budget means more sequential inference:

```math
Cost\propto T_{generated}
```

This is not a new form of attention mathematics; it is mainly a change in generation/training policy and token/computation budget.

### Caveat

A larger reasoning budget does not guarantee monotonically better answers.

---

# PART IX — COUPLING MATRIX

## 28. Main relationships

| Control ↑ | Entropy | Support | Repetition | KV | Latency | Comment |
|---|---:|---:|---:|---:|---:|---|
| Temperature | ↑ | = | usually ↓ | = | ~ | may increase incoherence |
| Top-K | — | ↓ | may ↑ | = | ~ | absolute cutoff |
| More restrictive Top-P | ↓ | ↓ | may ↑ | = | ~ | cumulative adaptive cutoff |
| Higher Min-P | ↓ | ↓ | may ↑ | = | ~ | relative to top token |
| Rep penalty | variable | variable | ↓ lexical | = | ~ | may damage syntax |
| DRY | variable | variable | ↓ sequential | = | small | excellent against long loops |
| Context | — | — | variable | ↑ linear | ↑ | possible quality gain/loss |
| KV precision | ~ | = | = | ↑ with bits | may vary | accuracy/runtime dependent |
| Batch/parallel | — | — | — | ↑ | throughput ↑ | individual latency may rise |

---

# PART X — MAPPING TO THE LOCAL STACK

## 29. SillyTavern

The UI should be understood as a **control plane**. It does not define the mathematics; it sends parameters to the backend.

Always verify:

- sampler order;
- which samplers the backend ignores;
- stop strings;
- context size;
- instruct/chat template;
- system prompt injection;
- grammar/JSON schema when applicable.

## 30. KoboldCpp / llama.cpp

As of 2026, the set includes, among others:

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

Order is a backend/configuration property. Do not write “the universal order is X.”

## 31. LM Studio / Ollama

Treat them as frontends/runtimes with their own defaults. For technical benchmarking, hold constant:

- the same GGUF/checkpoint;
- the same template;
- the same context;
- the same samplers;
- the same seed;
- the same KV quantization;
- the same GPU offload.

Otherwise, comparing “model A vs B” becomes a comparison between different pipelines.

---

# PART XI — EXPERIMENTAL PROTOCOL

## 32. Scientific sampling sweep

1. Fix prompt/template/context/seed/backend/model.
2. Record top logits/probabilities per token if possible.
3. Change **one control family** at a time.
4. Measure:
   - entropy;
   - support size;
   - repetition rate;
   - unique n-grams;
   - task accuracy;
   - subjective quality.
5. Repeat across multiple seeds — one seed is a point, not a distribution.

---

# PART XII — FAILURE DIAGNOSTICS

## 33. Symptom → hypothesis

| Symptom | Investigate first |
|---|---|
| repeated phrases | DRY / context injection / low entropy |
| strange synonyms | excessive rep penalty |
| incoherent text | temperature/support too open / model limit |
| truncated response | max tokens / EOS / stop strings |
| disobedience | template/system/conditioning before sampling |
| quality drops at long context | RoPE regime/effective context/KV precision |
| TPS collapses | context/KV/offload/bandwidth |
| invalid JSON | grammar/schema, not temperature alone |

---

## 34. Snapshot 2026

- DeepSeek-V3: 671B total, 37B active per token, MLA + DeepSeekMoE.
- Qwen3-Coder-Next: 80B total, ~3B active during inference, illustrating why total and active parameters must be separated.
- llama.cpp: modern sampling includes DRY, XTC, top-n-sigma, and adaptive-p in addition to classic top-k/top-p/min-p.

## References

- llama.cpp sampler API — https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h
- llama.cpp completion sampling docs — https://github.com/ggml-org/llama.cpp/blob/master/tools/completion/README.md
- llama.cpp CLI/runtime — https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md
- DeepSeek-V3 — https://arxiv.org/abs/2412.19437
- Qwen3-Coder-Next — https://arxiv.org/abs/2603.00729

---

# PART XIII — PARALLEL / MASKED / DIFFUSION LANGUAGE MODELS

> Transformer does not imply autoregression. From this point on, we drop the assumption that text can only advance as `token1 → token2 → token3`.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

## 35. Autoregressive factorization — baseline

```math
p(x_{1:T})=\prod_{t=1}^{T}p(x_t|x_{<t})
```

Inference:

```text
x1 -> x2 -> x3 -> ... -> xT
```

Position $`t+1`$ does not exist before $`t`$ has been decided.

### Implications

- natural streaming;
- extremely efficient incremental KV;
- latency grows with output-token count;
- each prior error/decision becomes later conditioning.

---

## 36. Masked language modeling

Define mask $`M\subset\{1,\ldots,T\}`$:

```math
\mathcal L=-\sum_{i\in M}\log p(x_i|x_{\setminus M})
```

Unlike causal AR, a position can use context **from both sides**.

Iterative inference may begin with:

```text
[MASK] [MASK] [MASK] [MASK] [MASK]
```

fill the highest-confidence positions, remask/refine, and repeat.

---

## 37. Discrete diffusion / iterative denoising

Corrupted text state:

```math
x_t\sim q(x_t|x_0,t)
```

The network learns a reverse transition:

```math
p_\theta(x_{t-1}|x_t,C)
```

Trajectory:

```math
x_T\rightarrow x_{T-1}\rightarrow\cdots\rightarrow x_0
```

Here $`t`$ is **noise/refinement time**, not textual position.

---

## 38. Parallel token prediction

If multiple positions are updated in one pass:

```math
\{x_i\}_{i\in U_k}
\leftarrow
f_\theta(x^{(k)})
```

where $`U_k`$ is the set of positions updated at iteration $`k`$.

This breaks the identity:

```math
1\ network\ forward = 1\ output\ token
```

that dominates causal LLMs.

---

## 39. Confidence-based unmasking

Each position has a confidence:

```math
c_i=\max_v p(x_i=v|x^{(k)})
```

Choose the top positions:

```math
U_k=TopK(c_i,K_k)
```

The most confident positions are fixed first; uncertain ones remain masked.

### Failure surface

A high-confidence error committed early can contaminate later refinement.

---

## 40. Remasking

A decision can be revised:

```math
x_i^{(k)}\rightarrow MASK\rightarrow x_i^{(k+1)}
```

This is structurally different from pure AR, where an emitted token is normally irreversible without an external restart/edit loop.

Remasking enables **self-correction inside the decode topology itself**.

---

## 41. Blockwise generation

A compromise between AR and full-sequence iterative generation:

```math
Block_1\rightarrow Block_2\rightarrow\cdots
```

Within each block, multiple tokens can be refined in parallel.

This preserves some streaming/local causality while reducing the number of sequential steps.

---

## 42. Sequence length problem

AR does not need to know final length in advance; EOS decides.

Full-mask generation often needs to define/allocate a length:

```math
T_{target}
```

Possible strategies:

- length predictor;
- overallocate + EOS/padding;
- blockwise growth;
- insertion/deletion transitions.

So “how many tokens should we generate?” becomes part of the state topology itself.

---

## 43. KV cache does not work the same way

Causal AR:

```math
KV_t=KV_{t-1}+KV(x_t)
```

If earlier positions change during iterative refinement:

```math
x_i^{(k)}\neq x_i^{(k-1)}
```

derived states may need to be recomputed/invalidated.

So AR's great runtime trick — **cache the entire immutable prefix** — loses part of its advantage.

This is central when comparing real-world speed.

---

## 44. Complexity model: AR

For $`T_{out}`$ tokens:

```math
Latency_{AR}
\approx
T_{out}\cdot t_{decode-pass}
```

with small passes and incremental KV.

---

## 45. Complexity model: iterative parallel

For $`K`$ refinement steps:

```math
Latency_{iter}
\approx
K\cdot t_{sequence/block-pass}
```

The advantage appears when:

```math
K\ll T_{out}
```

**and** the cost of each parallel pass does not erase the savings.

Therefore:

```math
Parallel\ tokens\neq free\ speedup
```

---

## 46. Throughput vs latency

AR can offer:

- excellent token streaming;
- low first-token latency after prefill;
- low parallelism along the output axis.

Iterative models can offer:

- more compute per iteration;
- worse natural streaming;
- much higher output parallelism;
- high aggregate throughput on massively parallel hardware.

The optimal architecture depends on hardware and serving regime.

---

## 47. Sampling in diffusion text

Do not assume `temperature/top-p/min-p` apply exactly as they do in AR.

Controls may instead act on:

- corruption/noise schedule;
- token proposal distribution;
- confidence threshold;
- remasking ratio;
- number of refinement steps;
- block size;
- guidance/conditioning strength;
- stochastic vs deterministic transitions.

Each implementation must be mapped to its actual equation.

---

## 48. Entropy schedule

Under ideal refinement:

```math
H(X^{(k+1)})<H(X^{(k)})
```

on average, as uncertainty is removed.

But collapsing entropy too early can cause premature commitment; keeping it high for too long creates instability.

This is analogous to annealing, but the concrete implementation matters.

---

## 49. Editing advantage

Because the full sequence can be revisited:

```math
Edit\ subset\ M
```

it is natural to preserve surrounding context and regenerate internal regions.

AR usually needs FIM, rewrite, or another special mechanism to achieve the same effect.

---

## 50. Diffusion language model ≠ image diffusion copied literally

Text is discrete.

Typical image latent:

```math
x_t\in\mathbb R^d
```

Text:

```math
x_t\in\{1,\ldots,V\}^T
```

The corruption/reverse process must respect the discrete state or use specific embeddings/relaxations.

The correct analogy is **iterative denoising**, not “add Gaussian noise to a token ID.”

---

## 51. Snapshot: Mercury

Mercury/Mercury Coder demonstrated commercial-scale diffusion language models parameterized by Transformers that predict multiple tokens in parallel.

The most important conceptual point:

```math
Transformer\not\Rightarrow AR
```

And the physical point:

```math
Speedup
=f(parallel\ updates,iterations,sequence\ pass\ cost,hardware)
```

not merely “tokens per pass.”

---

# PART XIV — INFERENCE-TIME REASONING / TEST-TIME COMPUTE

## 52. A reasoning model is not a new architectural species

In most cases:

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

Do not create a separate ontology just because the output contains a reasoning trace.

---

## 53. Reasoning budget

If the model generates $`T_r`$ intermediate tokens and $`T_a`$ answer tokens:

```math
T_{total}=T_r+T_a
```

Runtime:

```math
KV,latency,energy\propto T_{total}
```

Test-time compute buys search/reflection, not new parametric capacity.

---

## 54. Sampling + verifier loop

An alternative to one long chain:

```math
N\ candidates\rightarrow verifier\rightarrow select
```

or iterative search:

```math
Generate\rightarrow Evaluate\rightarrow Expand/Prune
```

See [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

## 55. Updated map of language-model families

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

The last three have their own datasheets because the **output/objective** changes, not merely the decoding method.

---

## Additional references

- Mercury: Ultra-Fast Language Models Based on Diffusion — https://arxiv.org/abs/2506.17298
- Reward/verifier topology — [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- Runtime comparison AR vs iterative text — [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)
