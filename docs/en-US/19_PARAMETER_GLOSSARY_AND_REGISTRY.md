---
title: Parameter Glossary & Canonical Registry — SOTA++ 2026
aliases: [Parameter Registry, AI Glossary, Datasheet Data Dictionary]
tags: [ai, reference, glossary, parameters, ontology, data-dictionary]
updated: 2026-10-01
---

# Parameter Glossary & Canonical Registry — SOTA++ 2026

> This is the collection's **data dictionary**. It exists to prevent semantic drift: the same name referring to different mechanisms, symbols reused without context, UI knobs mistaken for fundamental parameters, and backend aliases treated as new concepts.

Main rule:

\[
\boxed{
Name \neq Meaning
}
\]

Meaning is defined by the triple:

\[
\boxed{(Domain,Layer,Definition)}
\]

Example: `temperature` has multiple incompatible meanings.

See [CONVENTIONS](CONVENTIONS.md) for editorial and notation rules.

---

# 1. Canonical provenance taxonomy

| Tag | Layer | Question |
|---|---|---|
| `ARCH` | architecture | how is the network built? |
| `MODEL` | checkpoint/config | what was fixed in the model? |
| `OBJ` | objective function | what does training optimize? |
| `DATA` | data | what distribution was used? |
| `TRAIN` | optimization | how were parameters updated? |
| `ALIGN` | post-training/alignment | how do preferences/rewards alter the policy? |
| `PEFT` | efficient adaptation | what parameter subspace is trained? |
| `DISTILL` | distillation | how is knowledge transferred? |
| `MERGE` | model merging | how are checkpoints/deltas combined? |
| `GEN` | generative process | AR, diffusion, flow, masked refinement, etc. |
| `INF` | inference | what operator/control runs at use time? |
| `STATE` | persistent state | what grows or persists? |
| `BACKEND` | runtime | how is computation implemented? |
| `PIPE` | pipeline | is it external to the model? |
| `INDEX` | retrieval index | how is the corpus indexed/searched? |
| `EVAL` | evaluation | how is performance measured? |
| `SEC` | security | what boundary/control reduces risk? |
| `UI` | frontend/vendor | friendly name without a universal definition? |
| `HEURISTIC` | empirical rule | guideline without a universal law? |

---

# 2. Dimensional conventions

| Symbol | Default meaning |
|---|---|
| \(B\) | batch size / number of sequences |
| \(T\) | temporal or sequence length; context must disambiguate |
| \(L\) | number of layers; loss uses \(\mathcal L\) |
| \(d\) | generic hidden/embedding dimension |
| \(d_h\) | dimension per attention head |
| \(H\) | image height **or** number of heads; avoid unsubscripted use in ambiguous formulas |
| \(W\) | image width **or** weight matrix; use context/subscripts |
| \(C\) | channels/conditioning depending on context |
| \(V\) | vocabulary size or value tensor; prefer \(|\mathcal V|\) for vocabulary when ambiguous |
| \(N\) | generic number of items/tokens/samples |
| \(K\) | top-K / retrieval K / clusters; always qualify |
| \(r\) | LoRA/low-rank rank |
| \(\theta\) | learned model parameters |
| \(\eta\) | learning rate in training context |
| \(\epsilon\) | noise/residual/tolerance; always qualify |
| \(\tau\) | contrastive/calibration temperature when explicitly stated |
| \(s\) | CFG/guidance scale in diffusion context |

---

# 3. Critical semantic collisions

## 3.1 Temperature

| Canonical name | Formula/use | Do not confuse with |
|---|---|---|
| Sampling Temperature | \(softmax(z/T)\) | contrastive temperature |
| Contrastive Temperature | \(\exp(sim/\tau)\) | LLM sampling |
| Distillation Temperature | softened targets via \(T\) | sampling |
| Entropy/Policy Temperature | regularization/exploration in RL | sampling |
| Calibration Temperature | post-hoc temperature scaling | generation randomness |

Never write only “temperature” in a cross-domain document.

---

## 3.2 Rank

| Rank | Meaning |
|---|---|
| LoRA rank \(r\) | dimension of the low-rank update |
| Retrieval rank | document position in a ranking |
| Matrix rank | algebraic dimension of row/column space |
| Rank correlation | statistical ordering, e.g. Spearman/Kendall |

---

## 3.3 Steps

| Term | Meaning |
|---|---|
| Diffusion/flow steps | evaluations / integration trajectory |
| Training steps | optimizer updates |
| Agent steps | observe/act iterations |
| Reasoning/search steps | inference/search budget |
| Scheduler steps | temporal/noise-schedule discretization |

---

## 3.4 Context / window

| Term | Meaning |
|---|---|
| LLM context window | addressable tokens |
| Training sequence length | tokens processed per sample |
| Sliding attention window | local subset visible to each token |
| Video temporal window | frames/latents processed together |
| Retrieval context | chunks injected into the prompt |
| Agent context | conversation/state/tool trace |

---

## 3.5 Alpha / Beta

These are generic symbols, not concepts.

They may represent:

- diffusion coefficients;
- LoRA scaling;
- optimizer betas;
- DPO strength;
- EMA coefficients;
- statistical parameters.

Always use a qualified name.

---

# 4. LLM — architecture registry

Primary file: [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md).

| Parameter | Tag | Canonical definition | Primary effect |
|---|---|---|---|
| `n_layers` | `ARCH` | number of Transformer blocks | capacity/compute/memory |
| `d_model` / hidden size | `ARCH` | residual-stream width | params/compute |
| `n_heads` | `ARCH` | query attention heads | attention partition |
| `n_kv_heads` | `ARCH` | K/V heads | KV memory |
| `head_dim` | `ARCH` | dimension per head | QK geometry |
| `ffn_dim` / intermediate size | `ARCH` | internal FFN dimension | params/compute |
| `vocab_size` | `MODEL` | vocabulary size | output matrix/tokenization |
| `max_position_embeddings` | `MODEL` | natively configured position limit | addressable sequence regime |
| `rope_theta` | `MODEL` | RoPE base/frequency parameter | positional phase |
| `sliding_window` | `ARCH/MODEL` | bounded local attention | compute/context locality |
| `num_experts` | `ARCH` | total MoE experts | storage/capacity |
| `experts_per_token` | `ARCH` | active top-k experts | active compute |
| `router_aux_loss` | `TRAIN/OBJ` | expert balancing term | routing balance |

---

# 5. LLM — attention / state registry

| Parameter | Tag | Definition |
|---|---|---|
| Q | `STATE` | query vectors |
| K | `STATE` | key vectors |
| V | `STATE` | value vectors |
| KV cache | `STATE/BACKEND` | K/V persisted for autoregressive decode |
| KV dtype | `BACKEND` | cache precision/quantization |
| KV offload | `BACKEND` | CPU/GPU placement of the cache |
| MHA | `ARCH` | one K/V head per Q head |
| GQA | `ARCH` | groups of Q heads share K/V |
| MQA | `ARCH` | one shared K/V set |
| MLA | `ARCH` | compressed latent attention state |
| attention mask | `ARCH/PIPE` | visibility matrix/rule |
| causal mask | `ARCH` | prevents looking into the future in AR |

---

# 6. LLM — inference/sampling registry

| Parameter | Tag | Definition | Conceptual unit/range |
|---|---|---|---|
| temperature | `INF` | divides logits before softmax | \(T>0\) |
| top-k | `INF` | keeps K highest-scoring tokens | integer |
| top-p | `INF` | smallest set with cumulative mass ≥ p | \(0<p\le1\) |
| min-p | `INF` | cutoff relative to the most probable token | \(0\le p\le1\) |
| typical-p | `INF` | filters by typicality/self-information | \(0<p\le1\) |
| top-n-sigma | `INF` | threshold based on the logit distribution | backend-specific |
| XTC | `INF` | exclusion/candidate-pruning sampler | backend-specific |
| adaptive-p | `INF` | adaptive cutoff with state/EMA | backend-specific |
| repetition penalty | `INF` | modifies logits of repeated tokens | ratio/factor |
| frequency penalty | `INF` | penalty proportional to frequency | scale |
| presence penalty | `INF` | penalty for binary presence | scale |
| DRY | `INF` | penalizes repeated sequences | multi-param |
| Mirostat | `INF` | feedback controller for surprise/perplexity | tau/eta/state |
| seed | `INF/BACKEND` | PRNG initialization | integer/state |
| max new tokens | `INF` | output budget | tokens |
| stop tokens | `INF/PIPE` | stop on token IDs | set |
| stop strings | `PIPE` | textual stop condition | strings |
| grammar | `INF` | allowed formal language | grammar/schema |
| reasoning budget | `INF/PIPE` | compute/token budget for reasoning | tokens/effort |

---

# 7. Runtime registry

File: [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

| Parameter | Tag | Definition |
|---|---|---|
| bpw | `BACKEND` | effective bits per weight |
| weight dtype | `BACKEND` | weight representation |
| compute dtype | `BACKEND` | multiplication/accumulation dtype |
| activation dtype | `BACKEND` | activation representation |
| GPU layers/offload | `BACKEND` | fraction/layers placed on GPU |
| batch size | `BACKEND` | sequences/tokens processed as a batch |
| microbatch | `BACKEND/TRAIN` | smaller physical batch unit |
| flash attention | `BACKEND` | memory-efficient attention-kernel family |
| mmap | `BACKEND` | memory-mapped weight loading |
| pinned memory | `BACKEND` | host pages pinned for faster transfers |
| TTFT | `EVAL` | time to first token |
| TPOT | `EVAL` | time per output token |
| prompt TPS | `EVAL` | prefill token throughput |
| decode TPS | `EVAL` | generation token throughput |
| peak VRAM | `EVAL` | maximum device memory used |
| peak RAM | `EVAL` | maximum host memory used |

---

# 8. Quantization registry

| Term | Definition |
|---|---|
| weight quantization | quantizes persistent weights |
| KV quantization | quantizes K/V cache |
| activation quantization | quantizes activations |
| group size | number of values sharing quantization parameters |
| scale | dequantization factor |
| zero point | offset in asymmetric quantization |
| symmetric quantization | levels centered around zero |
| asymmetric quantization | uses zero point / shifted interval |
| mixed precision | tensors/layers at different precisions |
| calibration set | data used to estimate quantization parameters |
| quantization error | difference between original and quantized values |

`Q4` alone is an insufficient description.

---

# 9. Image diffusion/flow registry

File: [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md).

| Parameter | Tag | Definition |
|---|---|---|
| latent width/height | `STATE` | latent spatial resolution |
| VAE scale factor | `MODEL` | pixel ↔ latent-resolution ratio |
| latent channels | `ARCH/MODEL` | channels in latent space |
| timestep \(t\) | `GEN` | trajectory coordinate |
| sigma \(\sigma_t\) | `GEN` | noise level |
| alpha \(\alpha_t\) | `GEN` | signal coefficient |
| steps / NFE | `INF` | number of evaluations/integration steps |
| scheduler | `INF` | locations \(t_i/\sigma_i\) on the integration grid |
| solver/sampler | `INF` | numerical stepping rule between points |
| CFG scale | `INF` | conditional/unconditional extrapolation |
| guidance | `INF/MODEL` | strength/form of conditioning; family-specific definition |
| denoise strength | `PIPE/INF` | start point / amount of added noise in img2img |
| flow shift | `INF/MODEL` | schedule transformation in flow models |
| seed | `INF` | PRNG initial state |
| negative prompt | `PIPE/INF` | alternative conditioning in compatible pipelines |
| clip skip | `MODEL/PIPE` | text-encoder layer selection; legacy/model-specific |
| Hires Fix | `PIPE` | second-pass upscale/refinement |

---

# 10. Solver versus scheduler registry

| Concept | Question |
|---|---|
| Scheduler | **where** along the trajectory do we evaluate? |
| Solver | **how** do we advance between evaluations? |
| NFE | how many times is the model/vector field called? |
| Ancestral step | does it inject a stochastic component during the trajectory? |
| Deterministic ODE step | does it integrate the field without extra noise injection? |

Never use `sampler/scheduler` as generic synonyms.

---

# 11. Video registry

File: [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| frames \(T\) | `STATE` | observable temporal extent |
| latent frames | `STATE` | temporal extent after compression |
| temporal compression ratio | `MODEL` | frames ↔ latent frames |
| spatial compression | `MODEL` | pixels ↔ latent spatial grid |
| fps | `PIPE/MODEL` | temporal sample/display rate |
| frame stride | `PIPE` | spacing between conditioning frames |
| temporal window | `ARCH/PIPE` | window processed jointly |
| overlap | `PIPE` | frames shared across chunks |
| motion bucket/score | `MODEL/UI` | conditioning specific to some model families |
| STG | `INF` | spatio-temporal guidance |
| audio guidance | `INF/MODEL` | audio-specific guidance in joint AV models |
| continuation length | `PIPE` | video-extension horizon |

---

# 12. Audio/speech registry

File: [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| sample rate | `MODEL/PIPE` | samples per second |
| hop length | `MODEL` | STFT/mel-frame stride |
| FFT size | `MODEL/PIPE` | spectral window size |
| mel bins | `MODEL` | mel-spectrogram dimensionality |
| codec frame rate | `MODEL` | latent/codec frames per second |
| codebooks | `ARCH/MODEL` | parallel quantizers in a neural codec |
| bitrate | `MODEL/PIPE` | represented bits per second |
| duration | `INF/PIPE` | generation horizon |
| speaker embedding | `STATE/COND` | conditioning representation of speaker identity |
| similarity | `UI/EVAL` | vendor knob or metric; qualify explicitly |
| stability | `UI` | vendor abstraction with no universal definition |
| VAD threshold | `PIPE` | speech/non-speech decision threshold |
| endpointing | `PIPE` | rule for detecting end of turn |
| chunk size | `PIPE/BACKEND` | streaming window |
| lookahead | `ARCH/PIPE` | permitted future context |
| WER | `EVAL` | word error rate |
| RTF | `EVAL` | real-time factor |

---

# 13. ASR-specific registry

| Term | Definition |
|---|---|
| blank token | CTC symbol with no emitted output |
| CTC collapse | removes repeats/blanks to form a transcript |
| acoustic encoder | maps audio to states |
| prediction network | label history in a transducer |
| joint network | combines acoustic and prediction state |
| beam size | number of hypotheses retained during decode |
| timestamp token | output tied to time |
| diarization | who spoke when |
| forced alignment | aligns known text to audio |

---

# 14. 3D registry

File: [07_3D_GENERATION_REPRESENTATION_DATASHEET](07_3D_GENERATION_REPRESENTATION_DATASHEET.md).

| Term | Definition |
|---|---|
| vertices \(V\) | mesh positions |
| faces \(F\) | mesh connectivity |
| SDF | signed distance field |
| density field | volumetric/NeRF-like density |
| Gaussian mean \(\mu\) | splat position |
| covariance \(\Sigma\) | Gaussian shape/orientation |
| opacity \(\alpha\) | volumetric contribution |
| SH/features | directional appearance/color |
| isosurface threshold | level set used to extract a surface |
| marching cubes resolution | grid used during extraction |
| poly count | faces after generation/decimation |
| watertightness | closed-surface property |
| manifoldness | local topological validity |
| UV resolution | texture resolution |
| PBR maps | material channels such as albedo/roughness/metallic |

---

# 15. Multimodal/VLM registry

File: [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| patch size | `ARCH/MODEL` | pixels per visual patch |
| vision tokens | `STATE` | tokens/states derived from an image |
| projector | `ARCH` | maps encoder dimension → language dimension |
| resampler | `ARCH` | compresses/adapts token count |
| Q-Former | `ARCH` | query-based bridge between modalities |
| early fusion | `ARCH` | modalities combined early |
| joint fusion | `ARCH` | shared multimodal processing |
| late fusion | `ARCH/PIPE` | representations/decisions combined late |
| multimodal RoPE | `ARCH` | position encoding across space/time/modality |
| visual token budget | `STATE/BACKEND` | vision contribution to context |
| frame sampling | `PIPE` | temporal subset sent to the model |
| grounding | `OBJ/EVAL` | bind output to an actual region/time span |

---

# 16. Retrieval/embedding registry

File: [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| embedding dimension \(d\) | `MODEL` | vector dimensionality |
| pooling | `MODEL/PIPE` | sequence → vector |
| L2 normalization | `PIPE/MODEL` | \(z/\|z\|\) |
| cosine similarity | `INF` | normalized angular similarity |
| dot product | `INF` | inner product |
| contrastive temperature \(\tau\) | `TRAIN/OBJ` | sharpness of the contrastive loss |
| chunk size | `PIPE` | size of an indexed fragment |
| chunk overlap | `PIPE` | duplicated content across chunks |
| retrieval K | `INF` | number of retrieved candidates |
| rerank K | `PIPE/INF` | candidates passed to the reranker |
| HNSW M | `INDEX` | connectivity of the HNSW graph |
| efConstruction | `INDEX` | search width during index construction |
| efSearch | `INDEX/INF` | search width at query time |
| IVF nlist | `INDEX` | number of coarse clusters |
| IVF nprobe | `INDEX/INF` | number of clusters searched |
| PQ subquantizers | `INDEX` | vector partition for product quantization |
| Recall@K | `EVAL` | fraction of relevant items retrieved |
| NDCG@K | `EVAL` | discounted ranking quality |

---

# 17. Reward/verifier registry

File: [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| reward \(r\) | `OBJ/EVAL` | scalar utility proxy |
| chosen/rejected | `DATA/ALIGN` | preference pair |
| ORM | `MODEL` | outcome reward model |
| PRM | `MODEL` | process reward model |
| generative verifier | `MODEL/PIPE` | reasoning/critique → verdict |
| judge | `PIPE/EVAL` | evaluator model/human |
| rubric | `EVAL` | explicit evaluation criteria |
| calibration | `EVAL` | match between confidence and empirical correctness |
| position bias | `EVAL` | preference dependent on ordering |
| verbosity bias | `EVAL` | preference for longer responses |
| best-of-N | `INF/PIPE` | sample N + select |

---

# 18. Agent registry

File: [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| tool schema | `PIPE` | formal action interface |
| tool choice | `INF/PIPE` | action/tool selection |
| strict schema | `INF/PIPE` | constrained syntax |
| retry budget | `PIPE` | maximum re-executions |
| step budget | `PIPE` | maximum agent-loop iterations |
| tool budget | `PIPE/SEC` | maximum tool calls/cost |
| state | `STATE` | agent working memory |
| HITL | `SEC/PIPE` | human approval before an action |
| idempotency | `SEC/PIPE` | repeating an action does not multiply its effect |
| rollback | `SEC/PIPE` | revert a change |
| policy hook | `SEC` | validates an action at runtime |
| capability | `SEC/PIPE` | operation granted to the agent |

---
# 19. World model / VLA registry

File: [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md).

| Term | Definition |
|---|---|
| state \(s_t\) | representation of the environment |
| action \(a_t\) | applied command |
| transition model | \(p(s_{t+1}|s_t,a_t)\) |
| observation \(o_t\) | partial measurement of the state |
| belief state | distribution/latent over hidden state |
| rollout horizon \(H\) | imagined steps |
| action chunk | block-predicted action sequence |
| diffusion policy | trajectory denoising in action space |
| flow policy | vector field over an action trajectory |
| MPC horizon | model-predictive-control optimization horizon |
| success rate | task completion rate |
| collision rate | physical-safety events |

---

# 20. Time-series registry

File: [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md).

| Term | Definition |
|---|---|
| context length | observed history |
| horizon | predicted future |
| patch length | points grouped into each token/patch |
| stride | shift between patches |
| frequency | sample interval/rate |
| covariates | auxiliary variables |
| quantile \(\tau\) | level of the predicted distribution |
| prediction interval | probabilistic range |
| MAE | mean absolute error |
| RMSE | root mean squared error |
| MAPE | relative percentage metric with a zero-value caveat |
| CRPS | scoring rule for a cumulative predictive distribution |

---

# 21. Tabular registry

| Term | Definition |
|---|---|
| feature tokenization | column/value → representation |
| categorical embedding | embedding of a category |
| missingness indicator | explicit representation of absence |
| row attention | relationships across records |
| column attention | relationships across attributes |
| in-context training set | tabular examples supplied as context |
| PFN | Prior-Data Fitted Network family |
| AUROC | binary ranking metric |
| log loss | probabilistic classification loss |

---

# 22. Graph registry

File: [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md).

| Term | Definition |
|---|---|
| node | element \(v\in V\) |
| edge | relation \((u,v)\in E\) |
| degree | number of connections |
| adjacency | connectivity structure |
| message passing | neighbor → node aggregation |
| neighborhood \(\mathcal N(v)\) | neighboring nodes |
| aggregation \(\oplus\) | sum/mean/max/attention, etc. |
| graph depth | message-passing layers |
| oversmoothing | node states become too similar |
| oversquashing | distant information compressed through a bottleneck |
| Laplacian PE | spectral positional encoding |
| random-walk PE | position/structure through walk statistics |
| link prediction | infer edges |
| graph generation | generate topology/attributes |

---

# 23. Training registry

File: [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md).

| Parameter | Tag | Definition |
|---|---|---|
| learning rate \(\eta\) | `TRAIN` | base magnitude of optimizer updates |
| batch size | `TRAIN` | samples per logical update |
| microbatch | `TRAIN` | samples per physical forward/backward pass |
| gradient accumulation | `TRAIN` | microsteps accumulated before optimizer step |
| warmup | `TRAIN` | increasing-LR phase |
| weight decay | `TRAIN` | weight regularization |
| gradient clipping | `TRAIN` | bounds gradient norm/magnitude |
| optimizer betas | `TRAIN` | EMA coefficients in Adam-like optimizers |
| sequence length | `TRAIN` | tokens per sample/window |
| packing | `DATA/TRAIN` | combining samples into a window |
| epochs | `TRAIN` | passes over the dataset |
| steps | `TRAIN` | optimizer updates |
| tokens seen | `TRAIN/EVAL` | actual processed token volume |

---

# 24. SFT / alignment registry

| Term | Definition |
|---|---|
| SFT | supervised fine-tuning |
| completion-only loss | prompt tokens masked out of the loss |
| preference pair | \((x,y_w,y_l)\) |
| reward model | preferences → scalar |
| DPO beta | strength/log-ratio scaling in DPO |
| KL coefficient | limits policy drift |
| GRPO group size | samples per prompt for relative advantages |
| reward std | signal diversity within the group |
| rollout length | generated response/action horizon |
| clipping epsilon | trust-region-like update bound |
| GSPO sequence ratio | likelihood ratio normalized by sequence length |
| RLVR | reinforcement learning with verifiable reward |

---

# 25. PEFT registry

| Term | Definition |
|---|---|
| LoRA rank \(r\) | low-rank dimension |
| LoRA alpha | scale of the adapter update |
| target modules | matrices receiving the adapter |
| LoRA dropout | dropout on the adapter path |
| QLoRA | quantized frozen base + trainable LoRA |
| DoRA | magnitude/direction decomposed adaptation |
| PiSSA/EVA/LoftQ init | initialization/adaptation strategies |
| adapter merge | folds the delta into the base weight |
| modules_to_save | additional modules trained/saved |

---

# 26. Distillation registry

| Term | Definition |
|---|---|
| teacher | model supplying the target/signal |
| student | model trained to imitate it |
| distillation temperature | smoothing of teacher/student distributions |
| hard targets | discrete labels/answers |
| soft targets | logits/probabilities |
| sequence distillation | teacher outputs become training text |
| reasoning distillation | teacher trajectories/rationales become supervision |
| on-policy distillation | student generates states/trajectories evaluated by teacher |
| dataset distillation | compresses information into a compact synthetic dataset |

---

# 27. Model merging registry

| Term | Definition |
|---|---|
| linear merge | weighted average of parameters |
| task vector | \(\tau=\theta_{ft}-\theta_{base}\) |
| task arithmetic | weighted sum of task vectors |
| SLERP | spherical linear interpolation |
| TIES | trim + sign resolve + merge |
| DARE | drop-and-rescale task deltas |
| density | fraction of deltas retained |
| merge weight | contribution of each source model |
| base model | common reference for task vectors |

---

# 28. Evaluation registry

File: [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

| Metric | Definition |
|---|---|
| accuracy | correct / total |
| exact match | equality after normalization |
| precision | TP/(TP+FP) |
| recall | TP/(TP+FN) |
| F1 | harmonic mean of precision/recall |
| pass@k | probability of at least one correct solution among k |
| perplexity | exponential mean NLL |
| Brier score | squared probabilistic error |
| ECE | calibration-bin gap |
| WER | (S+D+I)/N |
| MRR | mean reciprocal rank |
| NDCG | normalized discounted cumulative gain |
| MAE | mean absolute error |
| RMSE | root mean squared error |
| TTFT | time to first token |
| TPOT | time per output token |
| TPS | tokens per second |
| p95/p99 | latency tail percentile |
| CI | confidence interval |
| effect size | practical magnitude of a difference |

---

# 29. Statistical registry

| Term | Definition |
|---|---|
| sample mean \(\bar x\) | estimate of the mean |
| sample variance \(s^2\) | dispersion estimate |
| standard error | \(s/\sqrt N\) |
| confidence interval | interval estimate |
| bootstrap | resampling with replacement |
| paired comparison | same unit evaluated by A and B |
| permutation test | null distribution from random reassignment |
| McNemar | paired test for binary outcomes |
| power | probability of detecting a real effect at a given size |
| saturation | benchmark loses discrimination between systems |
| contamination | evaluation evidence appears in training/development |

---

# 30. Security registry

File: [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

| Term | Tag | Definition |
|---|---|---|
| prompt injection | `SEC` | content alters intended instruction/control flow |
| indirect injection | `SEC` | hostile instruction comes from external content |
| jailbreak | `SEC` | bypass of behavioral policy |
| data poisoning | `SEC/DATA` | deliberately contaminated training data |
| backdoor | `SEC/MODEL` | trigger → hidden malicious behavior |
| RAG poisoning | `SEC` | manipulated corpus/index |
| excessive agency | `SEC` | functionality/permissions/autonomy beyond what is needed |
| goal hijack | `SEC` | operational objective is diverted |
| tool misuse | `SEC` | valid tool used dangerously |
| memory poisoning | `SEC` | malicious persistent state |
| supply-chain attack | `SEC` | compromised artifact/dependency/provider |
| HITL | `SEC/PIPE` | human approval gate |
| sandbox | `SEC/BACKEND` | execution isolation |
| least privilege | `SEC` | minimum permission scope |
| circuit breaker | `SEC/PIPE` | automatic stop on a condition |
| ASR | `EVAL/SEC` | attack success rate — **do not confuse with Automatic Speech Recognition** |

The `ASR` collision is particularly dangerous in this collection. In audio it means **Automatic Speech Recognition**; in security it means **Attack Success Rate**. Always spell it out on first use.

---

# 31. UI knob registry — treat with healthy suspicion

Knobs such as:

- Creativity;
- Stability;
- Quality;
- Motion;
- Stylization;
- Guidance;
- Strength;
- Fidelity;

may map to different mechanisms in different products.

Rule:

\[
UIKnob
\xrightarrow{document}
UnderlyingParameter(s)
\]

Without that mapping, do not promote the knob into a law in a datasheet.

---

# 32. Backend alias examples

## Context

Possible names:

- `n_ctx`;
- `context_length`;
- `max_context`;
- `num_ctx`.

Canonical concept:

> runtime context/token capacity.

## Repetition

- `repeat_penalty`;
- `repetition_penalty`.

## GPU offload

- `n_gpu_layers`;
- `gpu_layers`;
- percent offload.

The registry should map aliases to one concept rather than proliferating new entries.

---

# 33. Unit registry

## Memory

Prefer:

- bytes;
- MiB/GiB for binary memory.

\[
1GiB=2^{30}bytes
\]

Use GB only when the source/vendor uses decimal units, and make that explicit.

## Bandwidth

Use GB/s or GiB/s according to the source; do not mix them without conversion.

## Compute

FLOP/s and tokens/s measure different things.

## Time

- ms;
- s;
- frames/s;
- samples/s;
- tokens/s.

---

# 34. Canonical naming policy

Prefer:

```text
Sampling Temperature
Contrastive Temperature
Distillation Temperature
```

over three entries all named “Temperature.”

Prefer:

```text
Diffusion Steps
Training Steps
Agent Steps
```

over “Steps.”

---

# 35. Parameter card template

Every important new variable should be registrable as:

```markdown
### Canonical Name

- Symbol:
- Domain:
- Provenance tag:
- Type/unit:
- Valid mathematical range:
- Typical implementation range:
- Governing equation:
- Direct effect:
- Coupled variables:
- Physical cost:
- Failure surface:
- Backend aliases:
- Do not confuse with:
- Source / snapshot:
```

---

# 36. Law versus implementation range

Distinguish:

## Mathematical domain

Example:

\[
T>0
\]

for sampling temperature.

## Backend accepted range

May be:

```text
0..2
```

in a UI.

## Empirical operating range

May be:

```text
0.7..1.2
```

for a specific model.

These are three different things.

---

# 37. Native/model parameter versus user control

Example:

`n_kv_heads` is `ARCH`.

You normally do not change it at inference time.

`KV dtype` is `BACKEND`.

You can change it at runtime.

`temperature` is `INF`.

You can change it per request.

This classification prevents looking for a nonexistent slider for an architectural property.

---

# 38. Causality strength

We can classify levers as:

## Direct control

Explicit mathematical transformation:

- temperature;
- top-p;
- CFG;
- solver;
- LR.

## Indirect conditioning

- prompt;
- reference image;
- retrieval context.

## Frozen state

- weights;
- tokenizer;
- architecture.

## Environmental/system control

- tool permissions;
- sandbox;
- index.

This classification should accompany causal interpretations.

---

# 39. Parameter-coupling notation

When useful, record the local sign:

\[
\frac{\partial Y}{\partial x}>0
\]

but only if the relationship is monotonic in the regime being discussed.

Otherwise:

\[
Y(x)\text{ is non-monotonic}
\]

is more accurate than drawing a misleading arrow.

---

# 40. Snapshot field

Implementation-dependent entries should include:

```text
snapshot: YYYY-MM-DD
backend/model: ...
```

Permanent mathematical equations do not need “2026 version” in their meaning.

---

# 41. Deprecated/legacy registry

Never silently delete an important old term.

Mark it:

```text
status: legacy
superseded_by: ...
```

Potential examples:

- SVD-specific knobs;
- Clip Skip outside families where it still makes sense;
- removed UI parameters.

---

# 42. Semantic drift detector

Before adding a new term, ask:

1. does a canonical concept already exist?
2. is it a backend alias?
3. is it a UI abstraction?
4. is it family-specific?
5. does the equation change, or only the name?

If the definition does not change:

\[
NewName\rightarrow Alias
\]

not a new entity.

---

# 43. Registry maintenance rule

Add an entry when at least one condition holds:

- the parameter appears in more than one datasheet;
- the name has a semantic collision;
- the knob is frequently misunderstood;
- physical cost depends on it;
- it is required to reproduce an experiment;
- it is an important architectural axis.

Do not register every argument from every CLI.

---

# 44. Document map

| Domain | Document |
|---|---|
| ontology | [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| LLM | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| code | [03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET](03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md) |
| image | [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md) |
| video | [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md) |
| audio/speech | [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md) |
| 3D | [07_3D_GENERATION_REPRESENTATION_DATASHEET](07_3D_GENERATION_REPRESENTATION_DATASHEET.md) |
| agents | [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) |
| runtime | [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| multimodal | [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md) |
| retrieval | [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md) |
| reward/judge | [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) |
| world/VLA | [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md) |
| time series/tabular | [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md) |
| graph | [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md) |
| training | [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) |
| evaluation | [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) |
| security | [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md) |

---

# 45. Final rule

When someone says:

> “increase X”

first ask yourself:

\[
\boxed{
Which\ X?
}
\]

Then:

1. in what domain?
2. at what layer?
3. which equation?
4. which backend/model?
5. what physical cost?
6. which observable changes?
7. what failure surface?

Only then touch the slider.

---

# Implementation references

This registry is derived from the collection's datasheets. For versioned implementation definitions, consult the snapshot references in the relevant document.

Particularly useful references for aliases/current implementation state:

- llama.cpp — https://github.com/ggml-org/llama.cpp
- Hugging Face Transformers — https://huggingface.co/docs/transformers/
- Hugging Face PEFT — https://huggingface.co/docs/peft/main/index
- Hugging Face TRL — https://huggingface.co/docs/trl/index
- Hugging Face Diffusers — https://huggingface.co/docs/diffusers/
- mergekit — https://github.com/arcee-ai/mergekit
