---
title: Parameter Glossary & Canonical Registry — SOTA++ 2026
aliases: [Parameter Registry, AI Glossary, Datasheet Data Dictionary]
tags: [ai, referencia, glossary, parameters, ontology, data-dictionary]
updated: 2026-10-01
---

# Parameter Glossary & Canonical Registry — SOTA++ 2026

> Este é o **data dictionary** da coleção. Ele existe para impedir semantic drift: o mesmo nome significando mecanismos diferentes, símbolos reutilizados sem contexto, knobs de UI confundidos com parâmetros fundamentais e aliases de backend tratados como conceitos novos.

Regra principal:

```math
\boxed{
Name \neq Meaning
}
```

O significado é definido pelo triplo:

```math
\boxed{(Domain,Layer,Definition)}
```

Exemplo: `temperature` possui múltiplos significados incompatíveis.

Veja [CONVENTIONS](CONVENTIONS.md) para regras editoriais e de notação.

---

# 1. Taxonomia canônica de proveniência

| Tag | Camada | Pergunta |
|---|---|---|
| `ARCH` | arquitetura | como a rede é construída? |
| `MODEL` | checkpoint/config | o que foi fixado no modelo? |
| `OBJ` | função-objetivo | o que o treino otimiza? |
| `DATA` | dados | que distribuição foi usada? |
| `TRAIN` | otimização | como parâmetros foram atualizados? |
| `ALIGN` | pós-treinamento/alignment | como preferências/rewards alteram policy? |
| `PEFT` | adaptação eficiente | qual subespaço é treinado? |
| `DISTILL` | distillation | como conhecimento é transferido? |
| `MERGE` | model merging | como checkpoints/deltas são combinados? |
| `GEN` | processo generativo | AR, diffusion, flow, masked refinement etc. |
| `INF` | inferência | que operador/controle roda no uso? |
| `STATE` | estado persistente | o que cresce/persiste? |
| `BACKEND` | runtime | como cálculo é implementado? |
| `PIPE` | pipeline | componente externo ao modelo? |
| `INDEX` | retrieval index | como corpus é indexado/buscado? |
| `EVAL` | avaliação | como performance é medida? |
| `SEC` | segurança | que boundary/controle reduz risco? |
| `UI` | frontend/vendor | nome amigável sem definição universal? |
| `HEURISTIC` | regra empírica | guideline sem lei universal? |

---

# 2. Convenções dimensionais

| Símbolo | Significado padrão |
|---|---|
| $`B`$ | batch size / número de sequências |
| $`T`$ | comprimento temporal ou de sequência; contexto deve tornar claro |
| $`L`$ | número de layers; em alguns domínios pode ser loss apenas com $`\mathcal L`$ |
| $`d`$ | hidden/embedding dimension genérica |
| $`d_h`$ | dimension por attention head |
| $`H`$ | image height **ou** número de heads; evitar sem subscrito em fórmula ambígua |
| $`W`$ | image width **ou** weight matrix; usar contexto/subscrito |
| $`C`$ | channels/conditioning conforme contexto |
| $`V`$ | vocabulary size ou value tensor; preferir $`\vert\mathcal V\vert`$ para vocabulário quando houver colisão |
| $`N`$ | número genérico de items/tokens/samples |
| $`K`$ | top-K / retrieval K / clusters; sempre qualificar |
| $`r`$ | rank LoRA/low-rank |
| $`\theta`$ | parâmetros aprendidos do modelo |
| $`\eta`$ | learning rate quando em training context |
| $`\epsilon`$ | noise/residual/tolerance; sempre qualificar |
| $`\tau`$ | temperature de contrastive/calibration quando explicitado |
| $`s`$ | CFG/guidance scale quando em diffusion context |

---

# 3. Colisões semânticas críticas

## 3.1 Temperature

| Nome canônico | Fórmula/uso | Não confundir com |
|---|---|---|
| Sampling Temperature | $`softmax(z/T)`$ | contrastive temperature |
| Contrastive Temperature | $`\exp(sim/\tau)`$ | LLM sampling |
| Distillation Temperature | soft targets suavizados por $`T`$ | sampling |
| Entropy/Policy Temperature | regularização/exploration em RL | sampling |
| Calibration Temperature | temperature scaling pós-hoc | generation randomness |

Nunca escrever apenas “temperature” num documento transversal.

---

## 3.2 Rank

| Rank | Significado |
|---|---|
| LoRA rank $`r`$ | dimensão do low-rank update |
| Retrieval rank | posição do documento no ranking |
| Matrix rank | dimensão algébrica do espaço coluna/linha |
| Rank correlation | ordem estatística, ex. Spearman/Kendall |

---

## 3.3 Steps

| Termo | Significado |
|---|---|
| Diffusion/flow steps | avaliações/integration trajectory |
| Training steps | optimizer updates |
| Agent steps | observe/act iterations |
| Reasoning/search steps | inference/search budget |
| Scheduler steps | discretização temporal/noise schedule |

---

## 3.4 Context / window

| Termo | Significado |
|---|---|
| LLM context window | tokens endereçáveis |
| Training sequence length | tokens processados por sample |
| Sliding attention window | subset local visível por token |
| Video temporal window | frames/latents simultâneos |
| Retrieval context | chunks injetados no prompt |
| Agent context | conversation/state/tool trace |

---

## 3.5 Alpha / Beta

São símbolos genéricos, não conceitos.

Podem representar:

- diffusion coefficients;
- LoRA scaling;
- optimizer betas;
- DPO strength;
- EMA coefficient;
- statistical parameters.

Sempre usar nome qualificado.

---

# 4. LLM — architecture registry

Arquivo principal: [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md).

| Parâmetro | Tag | Definição canônica | Efeito primário |
|---|---|---|---|
| `n_layers` | `ARCH` | número de Transformer blocks | capacity/compute/memory |
| `d_model` / hidden size | `ARCH` | largura do residual stream | params/compute |
| `n_heads` | `ARCH` | query attention heads | attention partition |
| `n_kv_heads` | `ARCH` | K/V heads | KV memory |
| `head_dim` | `ARCH` | dimensão por head | QK geometry |
| `ffn_dim` / intermediate size | `ARCH` | dimensão interna do FFN | params/compute |
| `vocab_size` | `MODEL` | tamanho do vocabulário | output matrix/tokenization |
| `max_position_embeddings` | `MODEL` | posição configurada nativamente | addressable sequence regime |
| `rope_theta` | `MODEL` | base/frequency parameter do RoPE | positional phase |
| `sliding_window` | `ARCH/MODEL` | atenção local limitada | compute/context locality |
| `num_experts` | `ARCH` | experts MoE totais | storage/capacity |
| `experts_per_token` | `ARCH` | top-k experts ativos | active compute |
| `router_aux_loss` | `TRAIN/OBJ` | balanceamento de experts | routing balance |

---

# 5. LLM — attention / state registry

| Parâmetro | Tag | Definição |
|---|---|---|
| Q | `STATE` | query vectors |
| K | `STATE` | key vectors |
| V | `STATE` | value vectors |
| KV cache | `STATE/BACKEND` | K/V persistidos para decode AR |
| KV dtype | `BACKEND` | precision/quantização do cache |
| KV offload | `BACKEND` | localização CPU/GPU do cache |
| MHA | `ARCH` | K/V head por Q head |
| GQA | `ARCH` | grupos de Q compartilham K/V |
| MQA | `ARCH` | um conjunto K/V compartilhado |
| MLA | `ARCH` | compressed latent attention state |
| attention mask | `ARCH/PIPE` | matriz/regra de visibilidade |
| causal mask | `ARCH` | impede olhar futuro em AR |

---

# 6. LLM — inference/sampling registry

| Parâmetro | Tag | Definição | Unidade/faixa conceitual |
|---|---|---|---|
| temperature | `INF` | divide logits antes do softmax | $`T>0`$ |
| top-k | `INF` | mantém K tokens de maior score | inteiro |
| top-p | `INF` | menor conjunto cuja massa ≥ p | $`0<p\le1`$ |
| min-p | `INF` | cutoff relativo ao token mais provável | $`0\le p\le1`$ |
| typical-p | `INF` | filtra por typicality/self-information | $`0<p\le1`$ |
| top-n-sigma | `INF` | threshold baseado em distribuição de logits | backend-specific |
| XTC | `INF` | exclusion/candidate pruning sampler | backend-specific |
| adaptive-p | `INF` | cutoff adaptativo com estado/EMA | backend-specific |
| repetition penalty | `INF` | modifica logits de tokens repetidos | ratio/factor |
| frequency penalty | `INF` | penalidade proporcional à frequência | escala |
| presence penalty | `INF` | penalidade por presença binária | escala |
| DRY | `INF` | penaliza repetição de sequências | multi-param |
| Mirostat | `INF` | feedback controller de surprise/perplexity | tau/eta/state |
| seed | `INF/BACKEND` | inicialização PRNG | integer/state |
| max new tokens | `INF` | output budget | tokens |
| stop tokens | `INF/PIPE` | interrupção por token IDs | set |
| stop strings | `PIPE` | interrupção textual | strings |
| grammar | `INF` | linguagem formal permitida | grammar/schema |
| reasoning budget | `INF/PIPE` | compute/token budget para reasoning | tokens/effort |

---

# 7. Runtime registry

Arquivo: [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

| Parâmetro | Tag | Definição |
|---|---|---|
| bpw | `BACKEND` | bits efetivos por peso |
| weight dtype | `BACKEND` | representação dos pesos |
| compute dtype | `BACKEND` | dtype da multiplicação/acumulação |
| activation dtype | `BACKEND` | representação de activations |
| GPU layers/offload | `BACKEND` | fração/layers na GPU |
| batch size | `BACKEND` | sequences/tokens processados em lote |
| microbatch | `BACKEND/TRAIN` | unidade física menor do batch |
| flash attention | `BACKEND` | kernel memory-efficient attention family |
| mmap | `BACKEND` | memory-mapped weight loading |
| pinned memory | `BACKEND` | host pages para transferências rápidas |
| TTFT | `EVAL` | time to first token |
| TPOT | `EVAL` | time per output token |
| prompt TPS | `EVAL` | prefill token throughput |
| decode TPS | `EVAL` | generation token throughput |
| peak VRAM | `EVAL` | máximo device memory usado |
| peak RAM | `EVAL` | máximo host memory usado |

---

# 8. Quantization registry

| Termo | Definição |
|---|---|
| weight quantization | quantiza pesos persistentes |
| KV quantization | quantiza cache K/V |
| activation quantization | quantiza activations |
| group size | número de valores compartilhando quant params |
| scale | fator de dequantização |
| zero point | offset em quantização assimétrica |
| symmetric quantization | níveis centrados em zero |
| asymmetric quantization | usa zero point/intervalo deslocado |
| mixed precision | tensores/camadas em precisões diferentes |
| calibration set | dados usados para estimar quant params |
| quantization error | diferença original vs quantizado |

`Q4` sozinho é descrição insuficiente.

---

# 9. Image diffusion/flow registry

Arquivo: [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md).

| Parâmetro | Tag | Definição |
|---|---|---|
| latent width/height | `STATE` | resolução espacial latente |
| VAE scale factor | `MODEL` | relação pixel ↔ latent resolution |
| latent channels | `ARCH/MODEL` | canais no espaço latente |
| timestep $`t`$ | `GEN` | coordenada da trajetória |
| sigma $`\sigma_t`$ | `GEN` | noise level |
| alpha $`\alpha_t`$ | `GEN` | signal coefficient |
| steps / NFE | `INF` | número de avaliações/integração |
| scheduler | `INF` | posições $`t_i/\sigma_i`$ da malha |
| solver/sampler | `INF` | regra numérica entre pontos |
| CFG scale | `INF` | extrapolação cond/uncond |
| guidance | `INF/MODEL` | força/forma de conditioning; definição family-specific |
| denoise strength | `PIPE/INF` | ponto inicial/quanto ruído em img2img |
| flow shift | `INF/MODEL` | transformação do schedule em flow models |
| seed | `INF` | PRNG initial state |
| negative prompt | `PIPE/INF` | alternative conditioning em pipelines compatíveis |
| clip skip | `MODEL/PIPE` | layer selection em text encoder legacy/model-specific |
| Hires Fix | `PIPE` | segundo pass/upscale-refine |

---

# 10. Solver versus scheduler registry

| Conceito | Pergunta |
|---|---|
| Scheduler | **onde** avaliar a trajetória? |
| Solver | **como** avançar entre avaliações? |
| NFE | quantas vezes chamar o modelo/vector field? |
| Ancestral step | injeta componente estocástico durante trajetória? |
| Deterministic ODE step | integra campo sem noise injection extra? |

Nunca usar `sampler/scheduler` como sinônimos genéricos.

---

# 11. Video registry

Arquivo: [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| frames $`T`$ | `STATE` | extensão temporal observável |
| latent frames | `STATE` | extensão após temporal compression |
| temporal compression ratio | `MODEL` | frames ↔ latent frames |
| spatial compression | `MODEL` | pixels ↔ latent spatial grid |
| fps | `PIPE/MODEL` | sample/display rate temporal |
| frame stride | `PIPE` | espaçamento de frames condicionantes |
| temporal window | `ARCH/PIPE` | janela processada conjuntamente |
| overlap | `PIPE` | frames compartilhados entre chunks |
| motion bucket/score | `MODEL/UI` | conditioning específico de algumas famílias |
| STG | `INF` | spatio-temporal guidance |
| audio guidance | `INF/MODEL` | guidance específico de áudio em joint AV model |
| continuation length | `PIPE` | horizonte de extensão do vídeo |

---

# 12. Audio/speech registry

Arquivo: [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| sample rate | `MODEL/PIPE` | samples/second |
| hop length | `MODEL` | deslocamento STFT/mel frames |
| FFT size | `MODEL/PIPE` | janela espectral |
| mel bins | `MODEL` | dimensão mel-spectrogram |
| codec frame rate | `MODEL` | latent/codec frames por segundo |
| codebooks | `ARCH/MODEL` | quantizers paralelos em neural codec |
| bitrate | `MODEL/PIPE` | bits por segundo representados |
| duration | `INF/PIPE` | horizonte de geração |
| speaker embedding | `STATE/COND` | identidade vocal condicionante |
| similarity | `UI/EVAL` | pode ser knob vendor ou métrica; qualificar |
| stability | `UI` | vendor abstraction, sem definição universal |
| VAD threshold | `PIPE` | decisão speech/non-speech |
| endpointing | `PIPE` | regra para detectar fim do turno |
| chunk size | `PIPE/BACKEND` | janela streaming |
| lookahead | `ARCH/PIPE` | contexto futuro permitido |
| WER | `EVAL` | word error rate |
| RTF | `EVAL` | real-time factor |

---

# 13. ASR-specific registry

| Termo | Definição |
|---|---|
| blank token | símbolo CTC sem output |
| CTC collapse | remove repeats/blanks para formar transcript |
| acoustic encoder | mapeia áudio para states |
| prediction network | histórico de labels em transducer |
| joint network | combina acoustic/prediction state |
| beam size | hipóteses mantidas no decode |
| timestamp token | output relacionado ao tempo |
| diarization | quem falou quando |
| forced alignment | alinha texto conhecido ao áudio |

---

# 14. 3D registry

Arquivo: [07_3D_GENERATION_REPRESENTATION_DATASHEET](07_3D_GENERATION_REPRESENTATION_DATASHEET.md).

| Termo | Definição |
|---|---|
| vertices $`V`$ | posições da mesh |
| faces $`F`$ | conectividade da mesh |
| SDF | signed distance field |
| density field | densidade volumétrica/NeRF-like |
| Gaussian mean $`\mu`$ | posição de splat |
| covariance $`\Sigma`$ | forma/orientação do Gaussian |
| opacity $`\alpha`$ | contribuição volumétrica |
| SH/features | aparência direcional/cor |
| isosurface threshold | level set para extrair superfície |
| marching cubes resolution | grid usado na extração |
| poly count | faces após geração/decimation |
| watertightness | superfície fechada |
| manifoldness | validade topológica local |
| UV resolution | resolução de textura |
| PBR maps | material channels (albedo/roughness/metallic etc.) |

---

# 15. Multimodal/VLM registry

Arquivo: [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| patch size | `ARCH/MODEL` | pixels por visual patch |
| vision tokens | `STATE` | tokens/states derivados da imagem |
| projector | `ARCH` | mapeia encoder dim → language dim |
| resampler | `ARCH` | comprime/adapta token count |
| Q-Former | `ARCH` | query-based bridge entre modalities |
| early fusion | `ARCH` | modalities combinadas cedo |
| joint fusion | `ARCH` | processing multimodal compartilhado |
| late fusion | `ARCH/PIPE` | combinar representações/decisões tardias |
| multimodal RoPE | `ARCH` | position encoding espaço/tempo/modalidade |
| visual token budget | `STATE/BACKEND` | contribuição da visão ao contexto |
| frame sampling | `PIPE` | subset temporal enviado ao modelo |
| grounding | `OBJ/EVAL` | associar output a região/tempo real |

---

# 16. Retrieval/embedding registry

Arquivo: [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| embedding dimension $`d`$ | `MODEL` | dimensão vetorial |
| pooling | `MODEL/PIPE` | sequência → vetor |
| L2 normalization | `PIPE/MODEL` | $`z/\Vert z\Vert`$ |
| cosine similarity | `INF` | similaridade angular normalizada |
| dot product | `INF` | produto interno |
| contrastive temperature $`\tau`$ | `TRAIN/OBJ` | sharpness da loss contrastive |
| chunk size | `PIPE` | tamanho de fragmento indexado |
| chunk overlap | `PIPE` | conteúdo duplicado entre chunks |
| retrieval K | `INF` | candidatos recuperados |
| rerank K | `PIPE/INF` | candidatos enviados ao reranker |
| HNSW M | `INDEX` | conectividade do grafo HNSW |
| efConstruction | `INDEX` | search width durante build |
| efSearch | `INDEX/INF` | search width em consulta |
| IVF nlist | `INDEX` | número de coarse clusters |
| IVF nprobe | `INDEX/INF` | clusters pesquisados |
| PQ subquantizers | `INDEX` | divisão vetorial para product quantization |
| Recall@K | `EVAL` | fraction relevant recuperada |
| NDCG@K | `EVAL` | discounted ranking quality |

---

# 17. Reward/verifier registry

Arquivo: [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| reward $`r`$ | `OBJ/EVAL` | scalar utility proxy |
| chosen/rejected | `DATA/ALIGN` | preference pair |
| ORM | `MODEL` | outcome reward model |
| PRM | `MODEL` | process reward model |
| generative verifier | `MODEL/PIPE` | reasoning/critique → verdict |
| judge | `PIPE/EVAL` | evaluator model/human |
| rubric | `EVAL` | critérios explícitos |
| calibration | `EVAL` | match confidence ↔ empirical correctness |
| position bias | `EVAL` | preferência dependente da ordem |
| verbosity bias | `EVAL` | preferência por respostas longas |
| best-of-N | `INF/PIPE` | sample N + select |

---

# 18. Agent registry

Arquivo: [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| tool schema | `PIPE` | interface formal da ação |
| tool choice | `INF/PIPE` | seleção de ação/tool |
| strict schema | `INF/PIPE` | constrained syntax |
| retry budget | `PIPE` | máximo de reexecuções |
| step budget | `PIPE` | máximo de agent loop iterations |
| tool budget | `PIPE/SEC` | máximo de tool calls/cost |
| state | `STATE` | memória operacional do agente |
| HITL | `SEC/PIPE` | aprovação humana antes de ação |
| idempotency | `SEC/PIPE` | repetir não multiplica efeito |
| rollback | `SEC/PIPE` | reverter mudança |
| policy hook | `SEC` | valida ação em runtime |
| capability | `SEC/PIPE` | operação concedida ao agente |

---

# 19. World model / VLA registry

Arquivo: [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md).

| Termo | Definição |
|---|---|
| state $`s_t`$ | representação do ambiente |
| action $`a_t`$ | comando aplicado |
| transition model | $`p(s_{t+1}\vert s_t,a_t)`$ |
| observation $`o_t`$ | measurement parcial do estado |
| belief state | distribuição/latent sobre estado oculto |
| rollout horizon $`H`$ | passos imaginados |
| action chunk | sequência de ações prevista em bloco |
| diffusion policy | trajectory denoising em action space |
| flow policy | vector field em action trajectory |
| MPC horizon | horizonte de otimização/model-predictive control |
| success rate | tarefa concluída |
| collision rate | eventos de segurança física |

---

# 20. Time-series registry

Arquivo: [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md).

| Termo | Definição |
|---|---|
| context length | histórico observado |
| horizon | futuro previsto |
| patch length | pontos agrupados por token/patch |
| stride | deslocamento entre patches |
| frequency | sample interval/rate |
| covariates | variáveis auxiliares |
| quantile $`\tau`$ | nível da distribuição prevista |
| prediction interval | faixa probabilística |
| MAE | mean absolute error |
| RMSE | root mean squared error |
| MAPE | relative percentage metric com caveat em zeros |
| CRPS | scoring rule para distribuição cumulativa |

---

# 21. Tabular registry

| Termo | Definição |
|---|---|
| feature tokenization | coluna/valor → representation |
| categorical embedding | embedding de categoria |
| missingness indicator | representação explícita de ausência |
| row attention | relações entre registros |
| column attention | relações entre atributos |
| in-context training set | exemplos tabulares fornecidos como contexto |
| PFN | Prior-Data Fitted Network family |
| AUROC | ranking metric binária |
| log loss | probabilistic classification loss |

---

# 22. Graph registry

Arquivo: [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md).

| Termo | Definição |
|---|---|
| node | elemento $`v\in V`$ |
| edge | relação $`(u,v)\in E`$ |
| degree | número de conexões |
| adjacency | estrutura de conectividade |
| message passing | agregação neighbor → node |
| neighborhood $`\mathcal N(v)`$ | nós vizinhos |
| aggregation $`\oplus`$ | sum/mean/max/attention etc. |
| graph depth | message-passing layers |
| oversmoothing | node states tornam-se semelhantes |
| oversquashing | informação distante comprimida em bottleneck |
| Laplacian PE | positional encoding espectral |
| random-walk PE | position/structure via walk statistics |
| link prediction | inferir arestas |
| graph generation | gerar topologia/atributos |

---

# 23. Training registry

Arquivo: [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md).

| Parâmetro | Tag | Definição |
|---|---|---|
| learning rate $`\eta`$ | `TRAIN` | magnitude base do optimizer update |
| batch size | `TRAIN` | samples por update lógico |
| microbatch | `TRAIN` | samples por forward/backward físico |
| gradient accumulation | `TRAIN` | microsteps acumulados antes do optimizer |
| warmup | `TRAIN` | fase de LR crescente |
| weight decay | `TRAIN` | regularização do peso |
| gradient clipping | `TRAIN` | limita norm/magnitude do gradiente |
| optimizer betas | `TRAIN` | EMA coefficients em Adam-like |
| sequence length | `TRAIN` | tokens por sample/janela |
| packing | `DATA/TRAIN` | combinação de samples na janela |
| epochs | `TRAIN` | passes sobre dataset |
| steps | `TRAIN` | optimizer updates |
| tokens seen | `TRAIN/EVAL` | volume real processado |

---

# 24. SFT / alignment registry

| Termo | Definição |
|---|---|
| SFT | supervised fine-tuning |
| completion-only loss | prompt masked da loss |
| preference pair | $`(x,y_w,y_l)`$ |
| reward model | preferences → scalar |
| DPO beta | strength/log-ratio scaling no DPO |
| KL coefficient | limita policy drift |
| GRPO group size | samples por prompt para relative advantages |
| reward std | diversidade de signal no group |
| rollout length | response/action horizon gerado |
| clipping epsilon | trust-region-like update bound |
| GSPO sequence ratio | likelihood ratio normalizado por comprimento |
| RLVR | reinforcement learning com reward verificável |

---

# 25. PEFT registry

| Termo | Definição |
|---|---|
| LoRA rank $`r`$ | low-rank dimension |
| LoRA alpha | scale do adapter update |
| target modules | matrizes que recebem adapter |
| LoRA dropout | dropout no adapter path |
| QLoRA | quantized frozen base + trainable LoRA |
| DoRA | magnitude/direction decomposed adaptation |
| PiSSA/EVA/LoftQ init | strategies de inicialização/adaptação |
| adapter merge | incorpora delta no base weight |
| modules_to_save | módulos extra treinados/salvos |

---

# 26. Distillation registry

| Termo | Definição |
|---|---|
| teacher | modelo que fornece target/signal |
| student | modelo treinado para imitá-lo |
| distillation temperature | suavização da distribuição teacher/student |
| hard targets | labels/answers discretos |
| soft targets | logits/probabilities |
| sequence distillation | teacher outputs viram training text |
| reasoning distillation | teacher trajectories/rationales viram supervision |
| on-policy distillation | student gera states/trajectories avaliados pelo teacher |
| dataset distillation | comprime informação num dataset sintético compacto |

---

# 27. Model merging registry

| Termo | Definição |
|---|---|
| linear merge | média ponderada de parameters |
| task vector | $`\tau=\theta_{ft}-\theta_{base}`$ |
| task arithmetic | soma ponderada de task vectors |
| SLERP | spherical linear interpolation |
| TIES | trim + sign resolve + merge |
| DARE | drop-and-rescale task deltas |
| density | fraction de deltas retidos |
| merge weight | contribuição de cada source model |
| base model | referência comum para task vectors |

---

# 28. Evaluation registry

Arquivo: [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

| Métrica | Definição |
|---|---|
| accuracy | correct / total |
| exact match | igualdade após normalização |
| precision | TP/(TP+FP) |
| recall | TP/(TP+FN) |
| F1 | harmônica de precision/recall |
| pass@k | chance de ao menos uma solução correta em k |
| perplexity | exponential mean NLL |
| Brier score | squared probabilistic error |
| ECE | calibration bin gap |
| WER | (S+D+I)/N |
| MRR | mean reciprocal rank |
| NDCG | normalized discounted cumulative gain |
| MAE | mean absolute error |
| RMSE | root mean squared error |
| TTFT | time to first token |
| TPOT | time per output token |
| TPS | tokens/second |
| p95/p99 | latency tail percentile |
| CI | confidence interval |
| effect size | magnitude prática da diferença |

---

# 29. Statistical registry

| Termo | Definição |
|---|---|
| sample mean $`\bar x`$ | estimativa de média |
| sample variance $`s^2`$ | dispersion estimate |
| standard error | $`s/\sqrt N`$ |
| confidence interval | interval estimate |
| bootstrap | resampling com reposição |
| paired comparison | mesma unidade avaliada por A e B |
| permutation test | null distribution por troca aleatória |
| McNemar | teste pareado para outcomes binários |
| power | chance de detectar efeito real dado tamanho |
| saturation | benchmark perde discriminação entre sistemas |
| contamination | eval evidence presente no training/development |

---

# 30. Security registry

Arquivo: [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

| Termo | Tag | Definição |
|---|---|---|
| prompt injection | `SEC` | conteúdo altera intended instruction/control flow |
| indirect injection | `SEC` | instrução hostil vem de external content |
| jailbreak | `SEC` | bypass de behavioral policy |
| data poisoning | `SEC/DATA` | treino contaminado deliberadamente |
| backdoor | `SEC/MODEL` | trigger → hidden malicious behavior |
| RAG poisoning | `SEC` | corpus/index manipulado |
| excessive agency | `SEC` | functionality/permissions/autonomy acima do necessário |
| goal hijack | `SEC` | objetivo operacional desviado |
| tool misuse | `SEC` | ferramenta válida usada de forma perigosa |
| memory poisoning | `SEC` | estado persistente malicioso |
| supply-chain attack | `SEC` | artefato/dependency/provider comprometido |
| HITL | `SEC/PIPE` | human approval gate |
| sandbox | `SEC/BACKEND` | isolamento de execução |
| least privilege | `SEC` | permission scope mínimo |
| circuit breaker | `SEC/PIPE` | parada automática por condição |
| ASR | `EVAL/SEC` | attack success rate — **não confundir com Automatic Speech Recognition** |

A colisão `ASR` é particularmente perigosa nesta coleção. Em áudio significa **Automatic Speech Recognition**; em segurança significa **Attack Success Rate**. Sempre escrever por extenso na primeira ocorrência.

---

# 31. UI knob registry — trate com suspeita saudável

Knobs como:

- Creativity;
- Stability;
- Quality;
- Motion;
- Stylization;
- Guidance;
- Strength;
- Fidelity;

podem mapear para mecanismos diferentes por produto.

Regra:

```math
UIKnob
\xrightarrow{documentar}
UnderlyingParameter(s)
```

Sem essa tradução, não inserir como lei no datasheet.

---

# 32. Backend alias examples

## Context

Possíveis nomes:

- `n_ctx`;
- `context_length`;
- `max_context`;
- `num_ctx`.

Conceito canônico:

> runtime context/token capacity.

## Repetition

- `repeat_penalty`;
- `repetition_penalty`.

## GPU offload

- `n_gpu_layers`;
- `gpu_layers`;
- percent offload.

O registry deve mapear aliases para um conceito, não proliferar entradas.

---

# 33. Unit registry

## Memory

Usar preferencialmente:

- bytes;
- MiB/GiB para memória binária.

```math
1GiB=2^{30}bytes
```

GB pode ser usado apenas quando fonte/vendor usar decimal, deixando claro.

## Bandwidth

GB/s ou GiB/s conforme fonte; não misturar sem converter.

## Compute

FLOP/s e tokens/s medem coisas diferentes.

## Time

- ms;
- s;
- frames/s;
- samples/s;
- tokens/s.

---

# 34. Canonical naming policy

Preferir:

```text
Sampling Temperature
Contrastive Temperature
Distillation Temperature
```

a três entradas “Temperature”.

Preferir:

```text
Diffusion Steps
Training Steps
Agent Steps
```

a “Steps”.

---

# 35. Parameter card template

Toda nova variável importante deve poder ser registrada assim:

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

Distinguir:

## Mathematical domain

Ex.:

```math
T>0
```

para sampling temperature.

## Backend accepted range

Pode ser:

```text
0..2
```

por UI.

## Empirical operating range

Pode ser:

```text
0.7..1.2
```

para um modelo específico.

São três coisas diferentes.

---

# 37. Native/model parameter versus user control

Exemplo:

`n_kv_heads` é `ARCH`.

Você normalmente não muda em inferência.

`KV dtype` é `BACKEND`.

Você pode mudar runtime.

`temperature` é `INF`.

Você muda por request.

Essa classificação evita procurar um slider inexistente para propriedade arquitetural.

---

# 38. Causality strength

Podemos classificar alavancas:

## Direct control

Transformação matemática explícita:

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

Essa classificação deve acompanhar interpretações de causalidade.

---

# 39. Parameter coupling notation

Quando útil, registrar sinal local:

```math
\frac{\partial Y}{\partial x}>0
```

mas somente se relação for monotônica no regime discutido.

Se não:

```math
Y(x)\text{ is non-monotonic}
```

é mais correto que desenhar seta enganosa.

---

# 40. Snapshot field

Entradas dependentes de implementação devem ter:

```text
snapshot: YYYY-MM-DD
backend/model: ...
```

Equações matemáticas permanentes não precisam de “versão 2026” no significado.

---

# 41. Deprecated/legacy registry

Nunca apagar silenciosamente termo antigo importante.

Marcar:

```text
status: legacy
superseded_by: ...
```

Exemplos potenciais:

- knobs específicos de SVD;
- Clip Skip fora das famílias em que faz sentido;
- UI parameters removidos.

---

# 42. Semantic drift detector

Antes de adicionar novo termo, pergunte:

1. já existe canonical concept?
2. é alias de backend?
3. é UI abstraction?
4. é family-specific?
5. muda equação ou apenas nome?

Se não muda definição:

```math
NewName\rightarrow Alias
```

não nova entidade.

---

# 43. Regra de manutenção do registry

Adicionar entrada quando ao menos uma condição valer:

- parâmetro aparece em mais de um datasheet;
- nome colide semanticamente;
- knob é frequentemente confundido;
- custo físico depende dele;
- é necessário para reproduzir experimento;
- é eixo arquitetural importante.

Não registrar todo argumento de toda CLI.

---

# 44. Mapa de documentos

| Domínio | Documento |
|---|---|
| ontologia | [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| LLM | [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| código | [03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET](03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md) |
| imagem | [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md) |
| vídeo | [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md) |
| áudio/speech | [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md) |
| 3D | [07_3D_GENERATION_REPRESENTATION_DATASHEET](07_3D_GENERATION_REPRESENTATION_DATASHEET.md) |
| agentes | [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) |
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

# 45. Regra final

Quando alguém disser:

> “aumente X”

primeiro responda mentalmente:

```math
\boxed{
Qual\ X?
}
```

Depois:

1. em qual domínio?
2. em qual camada?
3. qual equação?
4. qual backend/model?
5. qual custo físico?
6. qual observável muda?
7. qual failure surface?

Só então mexa no slider.

---

# Referências de implementação

Este registry é derivado dos datasheets da coleção. Para definições versionadas de implementações, consulte as referências snapshot no documento específico.

Referências particularmente úteis para aliases/estado atual:

- llama.cpp — https://github.com/ggml-org/llama.cpp
- Hugging Face Transformers — https://huggingface.co/docs/transformers/
- Hugging Face PEFT — https://huggingface.co/docs/peft/main/index
- Hugging Face TRL — https://huggingface.co/docs/trl/index
- Hugging Face Diffusers — https://huggingface.co/docs/diffusers/
- mergekit — https://github.com/arcee-ai/mergekit
