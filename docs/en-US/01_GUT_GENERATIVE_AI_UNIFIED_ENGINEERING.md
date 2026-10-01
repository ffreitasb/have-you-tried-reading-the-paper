---
title: AI GUT — Unified Foundation Model Engineering Datasheet v3.1
tags: [ai, reference, gut, mathematics, architecture, foundation-models]
updated: 2026-10-01
---

# AI GUT — Unified Foundation Model Engineering Datasheet v3.1

> The fundamental unit is not “text,” “image,” “audio,” or “agent.” It is **a numerically represented state, transformed by a learned operator, conditioned on information, and traversed by an inference procedure**.

This version definitively abandons the simplistic “Transformer vs Diffusion” tree and treats foundation models as combinations of **orthogonal axes**.

---

# 1. The master ontology

Describe a system as:

\[
\boxed{
M=(R,O,B,C,I,S,D,\Omega)
}
\]

| Symbol | Axis | Question |
|---|---|---|
| \(R\) | Representation | What space does the state live in? |
| \(O\) | Objective | What does training teach the network to predict or optimize? |
| \(B\) | Backbone | Which architecture parameterizes the transformation? |
| \(C\) | Conditioning | How do context, intent, and observations enter? |
| \(I\) | Inference operator | How does the state advance, or how is a decision made? |
| \(S\) | Persistent state | What persists or grows during inference? |
| \(D\) | Decoder / decision map | How do we return to an observable domain or action? |
| \(\Omega\) | Modality topology | How many modalities enter/leave, and how are they aligned? |

The key rule:

\[
\boxed{B\perp O\perp R}
\]

A Transformer can be autoregressive, masked, diffusion-like, an embedding encoder, a reranker, a reward model, a graph processor, or a policy backbone.

## 1.1 The model is not the entire lifecycle

The tuple \(M\) primarily describes **the learned system and its execution**. By itself, it does not describe how the weights were produced, how evidence was measured, or how operational risk is controlled.

For that, we wrap \(M\) in a lifecycle envelope:

\[
\boxed{
\Gamma=(\mathcal D,\mathcal T,\mathcal A,\mathcal E,\mathcal S)
}
\]

| Symbol | Lifecycle axis | Question |
|---|---|---|
| \(\mathcal D\) | Data | What distribution fed training/adaptation? |
| \(\mathcal T\) | Training | Which losses/optimizers produced \(\theta\)? |
| \(\mathcal A\) | Alignment/Adaptation | SFT, preference, RL, PEFT, distillation, merge? |
| \(\mathcal E\) | Evaluation | Which protocol supports the performance claims? |
| \(\mathcal S\) | Security/Robustness | Which trust boundaries and failure surfaces constrain deployment? |

So the complete unit of the collection becomes:

\[
\boxed{System=(M,\Gamma,Runtime)}
\]

See [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md), [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md), [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md), and [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 2. Representation space — the variable that changes the physics most

## 2.1 Discrete sequence

\[
x=(x_1,\ldots,x_T),\quad x_t\in\{1,\ldots,V\}
\]

Examples:

- text;
- code;
- audio codec tokens;
- discretized actions.

---

## 2.2 Continuous latent

\[
Z\in\mathbb R^{N\times d}
\]

or, for images:

\[
Z\in\mathbb R^{B\times C\times H_l\times W_l}
\]

Examples:

- VAE latents;
- audio latents;
- structured 3D latents;
- continuous speech representations.

---

## 2.3 Spatial / spatiotemporal grid

Image:

\[
X\in\mathbb R^{H\times W\times C}
\]

Video:

\[
X\in\mathbb R^{T\times H\times W\times C}
\]

State dimensionality changes the cost of attention dramatically.

---

## 2.4 Numerical time series

\[
X\in\mathbb R^{T\times D}
\]

Time has physical order; it is not merely textual position.

---

## 2.5 Structured table

\[
X\in\mathbb R^{N\times D}
\]

Row/column order does not necessarily carry the semantics of a sentence. Missingness, heterogeneous types, and small-data priors make the problem structurally different.

---

## 2.6 Graph

\[
G=(V,E,X_V,X_E)
\]

There is no natural sequential order. Relational structure is part of the data itself.

---

## 2.7 Physical / embodied state

\[
s_t=(vision_t,proprioception_t,language_t,world\ state_t)
\]

The output may be a continuous action:

\[
a_t\in\mathbb R^m
\]

---

# 3. Objective functions

## 3.1 Autoregression

\[
p(x_{1:T})=\prod_{t=1}^{T}p(x_t|x_{<t},C)
\]

Training: next-element prediction.  
Inference: each step conditions the next.

---

## 3.2 Masked prediction / discrete denoising

Choose a masked set \(M\):

\[
\mathcal L=-\sum_{i\in M}\log p(x_i|x_{\setminus M})
\]

This can support parallel filling and iterative refinement.

---

## 3.3 Diffusion / score-based

Simplified forward process:

\[
x_t=\alpha_tx_0+\sigma_t\epsilon
\]

The network learns noise, score, the clean sample, or an equivalent parameterization.

---

## 3.4 Flow matching / rectified flow

\[
\frac{dx_t}{dt}=v_\theta(x_t,t,C)
\]

Inference approximates/integrates the learned vector field.

---

## 3.5 Contrastive representation learning

For positive query/document pair \(d^+\) and negatives \(d_j\):

\[
\mathcal L=
-\log
\frac{e^{sim(q,d^+)/\tau}}
{\sum_j e^{sim(q,d_j)/\tau}}
\]

The objective is not to generate; it is to **organize geometry**.

---

## 3.6 Ranking / preference / reward modeling

Pairwise:

\[
P(A>B)=\sigma(r_A-r_B)
\]

\[
\mathcal L=-\log\sigma(r_{chosen}-r_{rejected})
\]

The model learns an evaluation operator, not necessarily a generative one.

---

## 3.7 Transition dynamics / world modeling

\[
p(s_{t+1}|s_t,a_t)
\]

or deterministic/latent:

\[
\hat s_{t+1}=f_\theta(s_t,a_t)
\]

Learning the “plant” radically changes the decision topology.

---

# 4. Backbones

The function \(f_\theta\) can be parameterized by:

- Transformer;
- DiT / MMDiT;
- U-Net;
- Conformer;
- SSM/hybrids;
- GNN/message passing;
- Graph Transformer;
- CNN/ConvNet;
- hybrid mixtures.

Do not infer the objective from the architecture alone.

---

# 5. Conditioning — the actual “universal prompt”

\[
C=\{C_{text},C_{image},C_{audio},C_{video},C_{retrieved},C_{state},C_{graph},C_{tool},\ldots\}
\]

Mechanisms:

- prefix/context tokens;
- cross-attention;
- joint attention;
- feature projection;
- AdaLN/modulation;
- concatenation;
- reference embeddings;
- retrieved evidence;
- structural biases;
- action/state injection.

### Negative prompt

It is not universal. Under classic CFG:

\[
f_g=f_u+s(f_c-f_u)
\]

where “unconditional” may be empty, negative, or another reference conditioning signal.

---

# 6. Modality topology \(\Omega\)

## 6.1 Unimodal

\[
Text\rightarrow Text
\]

or:

\[
Image\rightarrow Image
\]

## 6.2 Multimodal input

\[
Text+Image\rightarrow Text
\]

## 6.3 Multimodal output

\[
Text\rightarrow Text+Audio/Image
\]

## 6.4 Omni

\[
\{Text,Image,Audio,Video\}_{in}
\rightarrow
\{Text,Audio,\ldots\}_{out}
\]

The main challenge stops being merely “LLM capacity” and starts including:

\[
Alignment(Modality_i,Modality_j)
\]

across space, time, and semantics.

See [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md).

---

# 7. Inference operators

## 7.1 Categorical decode

\[
z\rightarrow p(x)\rightarrow sample/argmax
\]

## 7.2 Constrained decode

\[
V_t\rightarrow V_t^{valid}
\]

## 7.3 ODE/SDE-style integration

\[
x_{k+1}=\Phi(x_k,f_\theta(x_k,t_k),\Delta t_k)
\]

## 7.4 Retrieval

\[
q\rightarrow z_q\rightarrow ANN(z_q)\rightarrow TopK
\]

## 7.5 Ranking

\[
(q,d_i)\rightarrow score_i\rightarrow sort
\]

## 7.6 Message passing

\[
h_v^{l+1}=\phi\left(h_v^l,\bigoplus_{u\in\mathcal N(v)}\psi(h_v^l,h_u^l,e_{uv})\right)
\]

## 7.7 Policy rollout

\[
a_t\sim\pi_\theta(a|s_t)
\]

## 7.8 Planning with learned dynamics

\[
\hat s_{t+1}=f_\theta(\hat s_t,a_t)
\]

\[
a^*_{1:H}=\arg\max\sum_{t=1}^{H}R(\hat s_t,a_t)
\]

---

# 8. Persistent state

| Family | State that grows/persists |
|---|---|
| causal LLM | KV cache |
| iterative text | full sequence/block being refined |
| diffusion/flow | latent trajectory/current latent |
| video | spatiotemporal latent/window |
| streaming speech | acoustic cache / decoder state |
| retrieval | external ANN index + query state |
| graph | node/edge representations |
| agent | conversation/tool/environment history |
| world model | latent state + rollout trajectory |

**Persistent state is the bridge between mathematics and physical cost.**

---

# 9. Temperature: four different meanings

The word “temperature” appears in several distinct contexts.

### Sampling temperature

\[
p_i(T)=\frac{e^{z_i/T}}{\sum_je^{z_j/T}}
\]

### Contrastive temperature

\[
\exp(sim/\tau)
\]

Controls how concentrated the loss is during embedding training.

### Policy entropy temperature

May weight exploration/regularization in RL.

### Distillation/calibration temperature

May smooth logits for teacher/student transfer or calibration.

> Same name ≠ same physical variable.

---

# 10. Temperature ≠ CFG ≠ retrieval threshold

These knobs may all *feel* like “freedom controls,” but they operate in different spaces:

- temperature: categorical distribution;
- CFG: combination/extrapolation of continuous predictions;
- similarity threshold: accepted region in vector space;
- reward threshold: decision rule applied to a score.

Never treat a behavioral analogy as mathematical equivalence.

---

# 11. Seed: initial state, not a determinism contract

\[
Reproducibility=
F(W,input,seed,dtype,kernel,backend,hardware,parallelism,version)
\]

Therefore:

\[
fixed\ seed\not\Rightarrow bitwise\ determinism
\]

---

# 12. Model capacity ≠ search/inference budget

Keep these separate:

\[
Capacity=f(N_{params},architecture,training,data)
\]

from:

\[
InferenceBudget=f(tokens,steps,rollouts,K,retrieval\ depth,verifier\ calls)
\]

Examples:

- more reasoning tokens do not increase parameter count;
- more diffusion steps do not increase model capacity;
- a larger retrieval `TopK` does not necessarily improve evidence quality;
- a longer rollout horizon may accumulate model error.

---

# 13. The complete operational cycle

With the added domains, the modern chain can be expressed as:

\[
\boxed{
PERCEIVE
\rightarrow
REPRESENT
\rightarrow
RETRIEVE
\rightarrow
REASON/GENERATE
\rightarrow
EVALUATE
\rightarrow
ACT
\rightarrow
PREDICT\ WORLD
\rightarrow
PERCEIVE
}
\]

### Perceive

[10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md), [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md)

### Represent / Retrieve

[11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md)

### Reason / Generate

[02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md), [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md)

### Evaluate

[12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)

### Act

[08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md), [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md)

### Predict structured worlds

[14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md), [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md)

---

# 14. Control taxonomy

| Class | Example | Operation |
|---|---|---|
| Conditioning | prompt, image, retrieved context | modifies \(C\) |
| Distribution shaping | temperature, penalties | modifies logits/probabilities |
| Support restriction | top-k, min-p, grammar | restricts candidate domain |
| Guidance | CFG, STG | combines predictions |
| Trajectory discretization | sigmas/timesteps | defines trajectory points |
| Solver | Euler/Heun/DPM | integrates trajectory |
| Retrieval scope | K, efSearch, nprobe | controls approximate search |
| Decision threshold | reward/similarity cutoff | turns score into decision |
| Rollout budget | horizon, candidates | expands search/planning |
| State budget | context, frames, nodes | increases persistent state |
| Quantization | Q4/Q8/FP8 | reduces precision/bytes |
| Runtime mapping | offload, batching | distributes compute and memory |

---

# 15. Observability

A SOTA++ datasheet must separate **controls** from **observables**.

## LLM

\[
logits,\ entropy,\ support\ size,\ KV,\ promptTPS,\ decodeTPS
\]

## Retrieval

\[
Recall@K,\ Precision@K,\ MRR,\ nDCG,\ ANN\ latency
\]

## Reward/Judge

\[
agreement,\ calibration,\ ECE,\ win\ rate,\ rank\ correlation
\]

## Speech

\[
WER,\ CER,\ RTF,\ TTFT,\ timestamp\ error
\]

## Time series

\[
MAE,\ RMSE,\ CRPS,\ coverage,\ calibration
\]

## Graph

\[
node/edge/graph\ metrics,\ neighborhood\ fanout,\ memory/node
\]

## World/VLA

\[
success\ rate,\ return,\ horizon,\ model\ error,\ action\ latency
\]

---

# 16. Universal failure surfaces

## 16.1 Distribution collapse

The distribution becomes excessively concentrated.

## 16.2 Support pollution

The candidate support contains semantically poor options.

## 16.3 Representation bottleneck

The encoder/projector loses information before it reaches the main backbone.

## 16.4 Alignment failure

Modalities or processing stages do not share an adequate temporal/spatial/semantic reference frame.

## 16.5 Search error

The correct answer exists, but retrieval/planning/beam search never reaches it.

## 16.6 Model error

The correct state is never assigned an adequate score in the first place.

## 16.7 Calibration error

A high score does not correspond to the true probability of being correct.

## 16.8 Runtime distortion

Quantization, extended context, or backend behavior alter the model more than expected.

---

# 17. SOTA Snapshot 2026 — why this ontology is necessary

In 2026, the same ecosystem simultaneously contains:

- omni models aligning text/vision/audio/video;
- multimodal embeddings and rerankers;
- diffusion language models generating multiple tokens in parallel;
- reward/verifier models judging processes and outcomes;
- world-model VLAs generating future visual states and actions;
- time-series foundation models with multi-task masking;
- tabular foundation models with in-context supervised inference;
- billion-scale graph foundation models.

None of these phenomena fit cleanly into the binary “LLM vs diffusion” framing.

---

# 17.1 The evidence and maintenance loop

The entire collection can be seen as a feedback loop:

```text
data → train/adapt → model → infer/system → evaluate → failure analysis
  ↑                                                        ↓
  └──────────────────── targeted data / controls ─────────┘
```

Formally:

\[
\theta_{k+1}
=
Update(
\theta_k,
Evidence_k,
Failures_k,
Data_k
)
\]

This is why training, evaluation, and security are **horizontal layers**, not new backbone types.

Canonical terminology: [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

Maintenance rules: [CONVENTIONS](CONVENTIONS.md).

# 18. Final rule

When a “new type” of model appears, do not start with the product name.

Ask:

1. What is \(R\)?
2. What is \(O\)?
3. What is \(B\)?
4. How does \(C\) enter?
5. What is \(I\)?
6. What persistent state \(S\) survives?
7. How does output leave through \(D\)?
8. What is the modality topology \(\Omega\)?

If you can answer those questions, the “new paradigm” almost always stops looking like magic and goes back to being engineering.

---

# 2026 Snapshot References

- Qwen3.5-Omni Technical Report — https://arxiv.org/abs/2604.15804
- Qwen3-VL-Embedding / Reranker — https://arxiv.org/abs/2601.04720
- Mercury diffusion language models — https://arxiv.org/abs/2506.17298
- WorldFly world-model VLA — https://arxiv.org/abs/2606.06147
- TabPFN-2.5 — https://arxiv.org/abs/2511.08667
- Zeus Time-Series Foundation Model — https://proceedings.mlr.press/v306/fu26n.html
- Billion-Scale Graph Foundation Models — https://arxiv.org/abs/2602.04768
- Acacia / Web Graph foundation model — https://arxiv.org/abs/2609.30894
