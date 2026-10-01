---
title: Foundation Model Engineering Datasheets — SOTA++ 2026
aliases: [AI Datasheets SOTA++ 2026, Foundation Models Engineering Reference]
tags: [ai, referencia, engenharia, inferencia, treinamento, avaliacao, seguranca, foundation-models, local-ai]
updated: 2026-10-01
---

# Foundation Model Engineering Datasheets — SOTA++ 2026

> Coleção de referência para desmontar sistemas modernos de IA **por baixo da interface**: representação, estados/tensores, equações, treinamento, parâmetros arquiteturais, controles de inferência, custo físico, avaliação, failure surfaces, segurança e mapeamento para runtime.

Esta coleção não é uma enciclopédia de marcas/checkpoints.

A regra de crescimento é:

\[
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
\]

Portanto `MoE`, `LoRA`, `RAG`, `reasoning model`, `quantization`, `speculative decoding`, `MCP` ou um novo sampler não viram automaticamente “tipos de modelo”. Eles entram no arquivo cuja matemática realmente modificam.

Para regras de manutenção, veja [CONVENTIONS](CONVENTIONS.md).

Para terminologia canônica, veja [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

Para histórico, veja [CHANGELOG](CHANGELOG.md).

---

# 1. A arquitetura do conhecimento

A coleção agora possui cinco camadas.

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

Mais precisamente:

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

# 2. A cadeia universal de dissecação

Para quase qualquer sistema moderno, procure:

\[
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
\]

Pergunte, nessa ordem:

1. **Representation** — em que espaço o estado vive?
2. **Objective** — o que o treino ensinou a rede a predizer/otimizar?
3. **Backbone** — Transformer, DiT, GNN, Conformer, SSM, híbrido?
4. **Conditioning** — como contexto/intenção/observação entram?
5. **Inference** — sampling, ODE/SDE integration, ranking, message passing, rollout?
6. **Persistent state** — KV, graph state, temporal window, memory, latent trajectory?
7. **Decoder / decision head** — como voltamos ao domínio observável/ação?
8. **Runtime** — dtype, quantização, bandwidth, batching, offload, kernels?
9. **Training lineage** — como os pesos chegaram ali?
10. **Evidence** — como sabemos que a mudança funciona?
11. **Risk boundary** — como o sistema falha e qual blast radius?

Só depois disso faz sentido mexer no “slider”.

---

# 3. Taxonomia de proveniência

Cada parâmetro deve ser lido com sua camada de origem.

| Tag | Camada | Exemplos |
|---|---|---|
| `ARCH` | arquitetura | `n_layers`, `n_kv_heads`, patch size |
| `MODEL` | checkpoint/config | tokenizer, RoPE theta, codec rate |
| `OBJ` | função-objetivo | AR, contrastive loss, flow matching |
| `DATA` | dados | mixture weights, dedup, curriculum |
| `TRAIN` | otimização | LR, batch, optimizer |
| `ALIGN` | alignment/post-training | DPO beta, RL reward |
| `PEFT` | adaptação eficiente | LoRA rank/alpha |
| `DISTILL` | distillation | teacher temperature, on-policy KD |
| `MERGE` | model merging | TIES density, merge weights |
| `GEN` | processo generativo | AR, masked refinement, diffusion |
| `INF` | inferência | temperature, min-p, solver |
| `STATE` | estado persistente | KV cache, rollout state |
| `BACKEND` | runtime | KV dtype, GPU offload |
| `PIPE` | pipeline | ControlNet, reranker, agent scaffold |
| `INDEX` | retrieval index | HNSW M, efSearch |
| `EVAL` | avaliação | Recall@K, TTFT, pass@k |
| `SEC` | segurança | authorization, sandbox, budget |
| `UI` | frontend/vendor | “stability”, “creativity” |
| `HEURISTIC` | recomendação empírica | “CFG 4–6 costuma…” |

Uma variável `UI` nunca deve ser promovida a lei sem saber para onde mapeia.

---

# 4. Tree completa

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

# 5. O que cada arquivo faz

## `01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`

**Função:** ontologia-mãe.

Descreve qualquer modelo por eixos ortogonais:

\[
M=(R,O,B,C,I,S,D,\Omega)
\]

Use quando quiser saber **que tipo de sistema está olhando antes de estudar os knobs**.

---

## `02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md`

**Função:** mecânica de linguagem/texto discreto.

Cobre:

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

Abra para entender **por que um LLM produz os próximos tokens que produz**.

---

## `03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md`

**Função:** código como completion e como state transition sobre repository/environment.

Cobre:

- FIM;
- code sampling;
- repository context;
- patches/diffs;
- compiler/tests;
- agentic coding loops;
- verification feedback.

---

## `04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md`

**Função:** imagem em espaço latente contínuo.

Cobre:

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

**Função:** geração quando estado possui dimensão temporal explícita.

Cobre:

- spatiotemporal latents;
- temporal compression;
- full-sequence vs chunked/causal generation;
- temporal attention/windowing;
- motion/identity consistency;
- STG/multimodal guidance.

---

## `06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md`

**Função:** todo o ciclo de representação sonora.

Cobre:

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

**Função:** IA 3D começando pela representação correta.

Cobre:

- mesh;
- implicit/SDF/radiance fields;
- Gaussian splats;
- structured latents;
- shape/texture separation;
- geometry integrity;
- manufacturing interface.

---

## `08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md`

**Função:** digital agents como control systems.

Cobre:

- tool calling;
- structured actions;
- state/history;
- retries;
- authorization;
- HITL;
- computer use;
- digital action loops.

Para segurança profunda, continuar em [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

---

## `09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md`

**Função:** a física da execução.

Cobre:

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

É o documento que traduz arquitetura em **VRAM/RAM/latência/TPS**.

---

## `10_MULTIMODAL_VLM_OMNI_DATASHEET.md`

**Função:** explicar como modalidades heterogêneas entram num mesmo sistema.

Cobre:

- vision/audio/video encoders;
- projectors/resamplers;
- Q-Former-like bridges;
- early/joint/late fusion;
- token explosion;
- spatial/temporal positional systems;
- multimodal/omni output.

---

## `11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md`

**Função:** geometria semântica e busca.

Cobre:

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

**Função:** sistemas que avaliam outros outputs.

Cobre:

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

**Função:** modelos de dinâmica e ação física/contínua.

Cobre:

\[
P(s_{t+1}|s_t,a_t)
\]

mais:

- latent dynamics;
- rollout;
- planning/MPC;
- VLA;
- action chunking;
- autoregressive/diffusion/flow policies;
- sim-to-real.

---

## `14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md`

**Função:** foundation models para structured numerical data.

Cobre:

- time-series patching/tokenization;
- forecasting;
- probabilistic/quantile prediction;
- masking/imputation/anomaly;
- tabular representation;
- PFN-style in-context supervised learning.

---

## `15_GRAPH_FOUNDATION_MODELS_DATASHEET.md`

**Função:** estados cuja topologia é um grafo.

Cobre:

- message passing;
- graph attention/Transformers;
- permutation invariance/equivariance;
- structural positional encodings;
- oversmoothing/oversquashing;
- node/edge/graph tasks;
- graph generation.

---

## `16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md`

**Função:** explicar de onde os pesos vieram.

Cobre:

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

**Função:** transformar comparação em evidência.

Cobre:

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

**Função:** mapear failure surfaces e blast radius.

Cobre:

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

**Função:** data dictionary canônico.

Use quando um termo parece familiar mas você precisa saber:

- qual significado;
- qual domínio;
- qual tag;
- qual equação;
- quais aliases;
- com o que não deve ser confundido.

É especialmente útil para colisões como:

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

**Função:** governance editorial/técnica.

Define:

- critérios para novo datasheet;
- structure padrão;
- nomenclatura;
- tags;
- unidade;
- snapshot policy;
- source policy;
- deprecation;
- definition of done.

---

## `CHANGELOG.md`

**Função:** preservar evolução da base de conhecimento.

Use para responder:

> “quando e por que mudamos esta interpretação?”

---

# 6. Guia rápido: qual arquivo abrir?

| Pergunta | Abra | Depois |
|---|---|---|
| “por que esse LLM repete?” | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| “quanto contexto cabe na VRAM?” | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| “imagem entra no LLM como quê?” | [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md) | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| “RAG: onde está a matemática?” | [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md) | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| “reward model e judge são iguais?” | [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) | [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) |
| “agent e VLA são a mesma coisa?” | [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) | [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md) |
| “ASR é inverso de TTS?” | [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md) | [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md) |
| “TabPFN é só Transformer em tabela?” | [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md) | [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| “graph model é LLM serializando arestas?” | [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md) | [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| “como esse checkpoint foi alinhado?” | [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) | [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) |
| “essa diferença de benchmark é real?” | [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) | [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md) |
| “esse agent é seguro?” | [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md) | [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) |
| “qual temperature?” | [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md) | arquivo do domínio |
| “diffusion LM quebra quais intuições?” | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| “LoRA r=64 significa o quê fisicamente?” | [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) | [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md) |

---

# 7. Ordem sugerida de leitura

Para construir o modelo mental do zero sem repetir fundamentos:

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
07 / 14 / 15 conforme interesse
 ↓
16 Training
 ↓
17 Evaluation
 ↓
18 Security
```

`CONVENTIONS` pode ser lido quando você começar a modificar a coleção.

---

# 8. Princípios universais

## 8.1 Backbone ≠ objective

\[
Transformer\neq Autoregression
\]

Transformer pode parametrizar:

- next-token AR;
- masked prediction;
- diffusion/denoising textual;
- flow matching;
- embedding encoder;
- reranker;
- reward model;
- graph processor;
- policy.

---

## 8.2 Seed ≠ determinismo

\[
Reproducibility
=f(weights,inputs,seed,dtype,kernel,backend,hardware,parallelism,version)
\]

---

## 8.3 Capacity ≠ search budget

\[
ModelCapacity
\neq
TestTimeCompute
\]

Mais samples/steps/rollouts podem melhorar output sem alterar pesos.

---

## 8.4 Quality é frequentemente vetorial

\[
Q=(correctness,latency,memory,safety,cost,style,\ldots)
\]

Um único scalar pode esconder trade-offs.

---

## 8.5 “Mais” raramente é monotônico

Não assumir:

\[
MoreSteps\Rightarrow Better
\]

\[
MoreCFG\Rightarrow Better
\]

\[
MoreContext\Rightarrow Better
\]

\[
LargerModel\Rightarrow BetterForMyConstraint
\]

---

# 9. O ciclo completo da coleção

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
}
\]

envolto por:

\[
\boxed{
TRAIN
\leftrightarrow
EVALUATE
\leftrightarrow
SECURE/MONITOR
}
\]

Esse é o motivo de a coleção ter parado de ser apenas uma “GUT de IA generativa” e se tornado uma referência de **Foundation Model Engineering**.

---

# 10. Regra de manutenção futura

Ao aparecer uma nova tecnologia, não perguntar primeiro:

> “merece um arquivo?”

Pergunte:

1. mudou representation?
2. mudou objective?
3. mudou inference topology?
4. mudou persistent state/dynamics?
5. ou apenas renomeou/combina mecanismos existentes?

Se a resposta for apenas o item 5:

\[
\boxed{UpdateExistingDatasheet}
\]

não criar categoria nova.

---

# 11. Snapshot

Estado da coleção: **1º de outubro de 2026**.

O núcleo matemático foi escrito para envelhecer lentamente; seções chamadas `Snapshot SOTA 2026` e referências de implementação são deliberadamente datadas e devem ser revistas periodicamente.
