---
title: Foundation Model Engineering Datasheets — SOTA++ 2026
aliases: [AI Datasheets SOTA++ 2026, Foundation Models Engineering Reference]
tags: [ai, reference, engineering, inference, training, evaluation, security, foundation-models, local-ai]
updated: 2026-10-01
---

# Foundation Model Engineering Datasheets — SOTA++ 2026

> A reference collection for taking modern AI systems apart **beneath the interface**: representations, states/tensors, equations, training, architectural parameters, inference controls, physical cost, evaluation, failure surfaces, security, and runtime mapping.

This collection is not an encyclopedia of brands or checkpoints.

Its growth rule is:

```math
\boxed{
NewDatasheet
\iff
\Delta Representation
\lor
\Delta Objective
\lor
\Delta InferenceTopology
\lor
\Delta StateDynamics
}
```

So `MoE`, `LoRA`, `RAG`, `reasoning model`, `quantization`, `speculative decoding`, `MCP`, or a new sampler do not automatically become new “model types.” They belong in whichever file contains the mathematics they actually change.

For maintenance rules, see [CONVENTIONS](CONVENTIONS.md).

For canonical terminology, see [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

For history, see [CHANGELOG](CHANGELOG.md).

---

# 1. Knowledge architecture

The collection is organized into five layers.

```text
META / ONTOLOGY
       ↓
MODEL & REPRESENTATION
       ↓
SYSTEM COMPONENTS
       ↓
LIFECYCLE
       ↓
PHYSICAL EXECUTION
```

More precisely:

```text
Data
  ↓
Training / Alignment / Adaptation
  ↓
Model Architecture + Weights
  ↓
Inference / Retrieval / Agentic System
  ↓
Evaluation
  ↓
Security / Monitoring / Feedback
  ↺
```

---

# 2. The universal dissection chain

For almost any modern system, trace:

```math
\boxed{
Representation
\rightarrow
State
\rightarrow
Learned\ Operator
\rightarrow
Inference\ Operator
\rightarrow
Observable
\rightarrow
Output
\rightarrow
Physical\ Cost
}
```

Ask, in this order:

1. **Representation** — what space does the state live in?
2. **Objective** — what did training teach the network to predict or optimize?
3. **Backbone** — Transformer, DiT, GNN, Conformer, SSM, hybrid?
4. **Conditioning** — how do context, intent, and observations enter the system?
5. **Inference** — sampling, ODE/SDE integration, ranking, message passing, rollout?
6. **Persistent state** — KV, graph state, temporal window, memory, latent trajectory?
7. **Decoder / decision head** — how do we return to an observable domain or an action?
8. **Runtime** — dtype, quantization, bandwidth, batching, offload, kernels?
9. **Training lineage** — how did the weights get here?
10. **Evidence** — how do we know the change actually works?
11. **Risk boundary** — how does the system fail, and what is the blast radius?

Only after that does it make sense to touch the “slider.”

---

# 3. Provenance taxonomy

Every parameter should be read together with its layer of origin.

| Tag | Layer | Examples |
|---|---|---|
| `ARCH` | architecture | `n_layers`, `n_kv_heads`, patch size |
| `MODEL` | checkpoint/config | tokenizer, RoPE theta, codec rate |
| `OBJ` | objective function | AR, contrastive loss, flow matching |
| `DATA` | data | mixture weights, dedup, curriculum |
| `TRAIN` | optimization | LR, batch, optimizer |
| `ALIGN` | alignment/post-training | DPO beta, RL reward |
| `PEFT` | parameter-efficient adaptation | LoRA rank/alpha |
| `DISTILL` | distillation | teacher temperature, on-policy KD |
| `MERGE` | model merging | TIES density, merge weights |
| `GEN` | generative process | AR, masked refinement, diffusion |
| `INF` | inference | temperature, min-p, solver |
| `STATE` | persistent state | KV cache, rollout state |
| `BACKEND` | runtime | KV dtype, GPU offload |
| `PIPE` | pipeline | ControlNet, reranker, agent scaffold |
| `INDEX` | retrieval index | HNSW M, efSearch |
| `EVAL` | evaluation | Recall@K, TTFT, pass@k |
| `SEC` | security | authorization, sandbox, budget |
| `UI` | frontend/vendor | “stability”, “creativity” |
| `HEURISTIC` | empirical recommendation | “CFG 4–6 often…” |

A `UI` variable should never be promoted into a law before you know what it actually maps to.

---

# 4. Full tree

```text
FOUNDATION MODEL ENGINEERING
│
├── META / ONTOLOGY
│   ├── 00_README_INDEX.md
│   ├── 01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md
│   ├── 19_PARAMETER_GLOSSARY_AND_REGISTRY.md
│   ├── CONVENTIONS.md
│   └── CHANGELOG.md
│
├── MODEL / REPRESENTATION
│   ├── 02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md
│   ├── 03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md
│   ├── 04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md
│   ├── 05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md
│   ├── 06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md
│   ├── 07_3D_GENERATION_REPRESENTATION_DATASHEET.md
│   ├── 10_MULTIMODAL_VLM_OMNI_DATASHEET.md
│   ├── 14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md
│   └── 15_GRAPH_FOUNDATION_MODELS_DATASHEET.md
│
├── SYSTEM COMPONENTS
│   ├── 08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md
│   ├── 11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md
│   ├── 12_REWARD_VERIFIER_JUDGE_DATASHEET.md
│   └── 13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md
│
├── LIFECYCLE
│   ├── 16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md
│   ├── 17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md
│   └── 18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md
│
└── PHYSICAL EXECUTION
    └── 09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md
```

---

# 5. What each file does

## `01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`

**Purpose:** the master ontology.

Describes any model along orthogonal axes:

```math
M=(R,O,B,C,I,S,D,\Omega)
```

Use it when you first need to understand **what kind of system you are looking at before studying its knobs**.

---

## `02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md`

**Purpose:** the mechanics of discrete language/text.

Covers:

- tokenizer;
- embeddings/residual stream;
- RoPE;
- Q/K/V;
- MHA/GQA/MQA/MLA;
- FFN/MoE;
- logits;
- samplers;
- DRY/XTC/Adaptive-P etc.;
- constrained decoding;
- masked/diffusion/parallel text generation;
- KV state.

Open this to understand **why an LLM produces the next tokens it produces**.

---

## `03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md`

**Purpose:** code as both completion and state transition over a repository/environment.

Covers:

- FIM;
- code sampling;
- repository context;
- patches/diffs;
- compiler/tests;
- agentic coding loops;
- verification feedback.

---

## `04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md`

**Purpose:** images in continuous latent space.

Covers:

- VAE;
- diffusion;
- rectified flow;
- DiT/MMDiT;
- CFG/guidance;
- sigma/timestep;
- scheduler ≠ solver;
- img2img/denoise;
- control/reference pipelines.

---

## `05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md`

**Purpose:** generation when the state has an explicit temporal dimension.

Covers:

- spatiotemporal latents;
- temporal compression;
- full-sequence vs chunked/causal generation;
- temporal attention/windowing;
- motion/identity consistency;
- STG/multimodal guidance.

---

## `06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md`

**Purpose:** the complete sound-representation cycle.

Covers:

- neural codecs;
- audio autoregression;
- audio diffusion/flow;
- music;
- TTS;
- voice conversion;
- STFT/Mel;
- ASR;
- CTC/RNN-T/seq2seq;
- diarization/VAD;
- speech understanding.

---

## `07_3D_GENERATION_REPRESENTATION_DATASHEET.md`

**Purpose:** 3D AI starting from the correct representation.

Covers:

- mesh;
- implicit/SDF/radiance fields;
- Gaussian splats;
- structured latents;
- shape/texture separation;
- geometry integrity;
- manufacturing interface.

---

## `08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md`

**Purpose:** digital agents as control systems.

Covers:

- tool calling;
- structured actions;
- state/history;
- retries;
- authorization;
- HITL;
- computer use;
- digital action loops.

For a deeper security treatment, continue with [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

---

## `09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md`

**Purpose:** the physics of execution.

Covers:

- weight memory;
- bpw;
- KV cache;
- activations/workspace;
- prompt prefill vs decode;
- quantization;
- FlashAttention;
- offload;
- CPU/GPU bandwidth;
- eGPU/TB4;
- speculative decoding;
- multimodal token cost;
- retrieval/runtime cost.

This is the document that translates architecture into **VRAM/RAM/latency/TPS**.

---

## `10_MULTIMODAL_VLM_OMNI_DATASHEET.md`

**Purpose:** explain how heterogeneous modalities enter the same system.

Covers:

- vision/audio/video encoders;
- projectors/resamplers;
- Q-Former-like bridges;
- early/joint/late fusion;
- token explosion;
- spatial/temporal positional systems;
- multimodal/omni output.

---

## `11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md`

**Purpose:** semantic geometry and search.

Covers:

- embeddings;
- contrastive training;
- dense/sparse/hybrid retrieval;
- bi-encoder;
- cross-encoder;
- late interaction;
- HNSW/IVF/PQ;
- reranking;
- RAG retrieval mechanics.

---

## `12_REWARD_VERIFIER_JUDGE_DATASHEET.md`

**Purpose:** systems that evaluate other outputs.

Covers:

- scalar reward models;
- pairwise preference;
- ORM/PRM;
- generative verifiers;
- LLM-as-a-Judge;
- calibration/bias;
- best-of-N;
- verifier-guided search.

---

## `13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md`

**Purpose:** dynamics models and physical/continuous action.

Covers:

```math
P(s_{t+1}|s_t,a_t)
```

plus:

- latent dynamics;
- rollout;
- planning/MPC;
- VLA;
- action chunking;
- autoregressive/diffusion/flow policies;
- sim-to-real.

---

## `14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md`

**Purpose:** foundation models for structured numerical data.

Covers:

- time-series patching/tokenization;
- forecasting;
- probabilistic/quantile prediction;
- masking/imputation/anomaly;
- tabular representation;
- PFN-style in-context supervised learning.

---

## `15_GRAPH_FOUNDATION_MODELS_DATASHEET.md`

**Purpose:** states whose topology is a graph.

Covers:

- message passing;
- graph attention/Transformers;
- permutation invariance/equivariance;
- structural positional encodings;
- oversmoothing/oversquashing;
- node/edge/graph tasks;
- graph generation.

---

## `16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md`

**Purpose:** explain where the weights came from.

Covers:

- data mixtures/curation;
- pretraining objectives;
- optimizers;
- distributed training;
- SFT;
- RLHF;
- DPO/KTO/ORPO;
- GRPO/DAPO/GSPO/RLVR;
- LoRA/QLoRA/DoRA;
- distillation;
- model merging;
- pruning;
- continual learning.

---

## `17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md`

**Purpose:** turn comparison into evidence.

Covers:

- SUT;
- benchmark/metric/harness separation;
- uncertainty;
- paired experiments;
- bootstrap;
- contamination;
- saturation;
- dynamic benchmarks;
- judge bias;
- runtime metrics;
- Pareto fronts;
- regression suites.

---

## `18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md`

**Purpose:** map failure surfaces and blast radius.

Covers:

- prompt injection;
- data/RAG/memory poisoning;
- supply chain;
- model artifacts;
- agent goal hijack/tool misuse;
- permissions/authz;
- sandbox;
- resource abuse;
- adversarial robustness;
- OWASP 2026 / Agent Control Standard;
- incident response.

---

## `19_PARAMETER_GLOSSARY_AND_REGISTRY.md`

**Purpose:** canonical data dictionary.

Use it when a term looks familiar but you need to know:

- which meaning;
- which domain;
- which tag;
- which equation;
- which aliases;
- what it must not be confused with.

It is especially useful for collisions such as:

```text
temperature
rank
steps
context
alpha/beta
ASR
```

---

## `CONVENTIONS.md`

**Purpose:** editorial/technical governance.

Defines:

- criteria for a new datasheet;
- standard structure;
- naming;
- tags;
- units;
- snapshot policy;
- source policy;
- deprecation;
- definition of done.

---

## `CHANGELOG.md`

**Purpose:** preserve the evolution of the knowledge base.

Use it to answer:

> “When and why did we change this interpretation?”

---

# 6. Quick guide: which file should I open?

| Question | Open | Then |
|---|---|---|
| “why does this LLM repeat itself?” | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| “how much context fits in VRAM?” | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| “what does an image become when it enters an LLM?” | [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md) | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| “RAG: where is the math?” | [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md) | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| “are a reward model and a judge the same thing?” | [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) | [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) |
| “are an agent and a VLA the same thing?” | [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) | [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md) |
| “is ASR just TTS in reverse?” | [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md) | [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md) |
| “is TabPFN just a Transformer over a table?” | [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md) | [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| “is a graph model just an LLM serializing edges?” | [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md) | [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| “how was this checkpoint aligned?” | [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) | [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) |
| “is this benchmark difference actually real?” | [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) | [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md) |
| “is this agent secure?” | [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md) | [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) |
| “which temperature?” | [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md) | the domain-specific file |
| “which intuitions does a diffusion LM break?” | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| “what does LoRA r=64 mean physically?” | [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) | [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md) |

---

# 7. Suggested reading order

To build the mental model from scratch without repeating fundamentals:

```text
01 GUT
 ↓
19 Registry
 ↓
02 LLM
 ↓
09 Runtime
 ↓
04 Image
 ↓
05 Video
 ↓
06 Audio
 ↓
10 Multimodal
 ↓
11 Retrieval
 ↓
12 Verifier
 ↓
08 Agent
 ↓
13 World/VLA
 ↓
07 / 14 / 15 depending on interest
 ↓
16 Training
 ↓
17 Evaluation
 ↓
18 Security
```

Read `CONVENTIONS` once you start modifying the collection.

---

# 8. Universal principles

## 8.1 Backbone ≠ objective

```math
Transformer\neq Autoregression
```

A Transformer can parameterize:

- next-token AR;
- masked prediction;
- text diffusion/denoising;
- flow matching;
- embedding encoder;
- reranker;
- reward model;
- graph processor;
- policy.

---

## 8.2 Seed ≠ determinism

```math
Reproducibility
=f(weights,inputs,seed,dtype,kernel,backend,hardware,parallelism,version)
```

---

## 8.3 Capacity ≠ search budget

```math
ModelCapacity
\neq
TestTimeCompute
```

More samples/steps/rollouts can improve output without changing the weights.

---

## 8.4 Quality is often vector-valued

```math
Q=(correctness,latency,memory,safety,cost,style,\ldots)
```

A single scalar can hide trade-offs.

---

## 8.5 “More” is rarely monotonic

Do not assume:

```math
MoreSteps\Rightarrow Better
```

```math
MoreCFG\Rightarrow Better
```

```math
MoreContext\Rightarrow Better
```

```math
LargerModel\Rightarrow BetterForMyConstraint
```

---

# 9. The full cycle covered by the collection

```math
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
}
```

wrapped by:

```math
\boxed{
TRAIN
\leftrightarrow
EVALUATE
\leftrightarrow
SECURE/MONITOR
}
```

That is why the collection stopped being merely a “GUT of generative AI” and became a **Foundation Model Engineering** reference.

---

# 10. Future maintenance rule

When a new technology appears, do not ask first:

> “does it deserve its own file?”

Ask instead:

1. did the representation change?
2. did the objective change?
3. did the inference topology change?
4. did the persistent state/dynamics change?
5. or did it merely rename or recombine mechanisms that already exist?

If the answer is only item 5:

```math
\boxed{UpdateExistingDatasheet}
```

Do not create a new category.

---

# 11. Snapshot

Collection state: **October 1, 2026**.

The mathematical core is written to age slowly; sections named `SOTA Snapshot 2026` and implementation references are deliberately dated and should be reviewed periodically.
