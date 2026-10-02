---
title: Local AI Inference & Runtime Datasheet v2.0 — VRAM, State, Retrieval, Multimodal and Parallel Inference
tags: [ai, local-ai, gguf, quantization, vram, inference, multimodal, retrieval, runtime]
updated: 2026-10-01
---

# Local AI Inference & Runtime Datasheet v2.0

> O arquivo do modelo é apenas os pesos empacotados. A inferência é um sistema dinâmico com pesos + caches + ativações + workspaces + buffers + transferências.

## 1. A equação física principal

```math
M_{runtime}=M_W+M_{KV}+M_A+M_{workspace}+M_{graph}+M_{backend}
```

Logo:

```math
\boxed{VRAM\ necessária\neq tamanho\ do\ GGUF}
```

---

## 2. Memória de pesos

Primeira aproximação:

```math
M_W\approx\frac{N_p\cdot bpw}{8}
```

onde:

- $`N_p`$: parâmetros;
- `bpw`: bits efetivos por weight.

Quantizações reais têm metadata, scales, block overhead e frequentemente mistura de tipos; use `bpw efetivo`, não o nome “Q4” como se significasse exatamente 4.000 bits/weight.

### Quatro objetos independentes de quantização

```math
Q_W,\quad Q_{KV},\quad Q_A,\quad Q_{emb/out}
```

- $`Q_W`$: pesos;
- $`Q_{KV}`$: key/value cache;
- $`Q_A`$: ativações/intermediários;
- $`Q_{emb/out}`$: embeddings/output head.

Quantizar pesos **não** implica KV quantizado.

---

## 3. KV cache — a memória que cresce com contexto

Para Transformer GQA/MHA convencional:

```math
M_{KV}\approx2\,L\,T\,n_{kv}\,d_h\,b\,B
```

- 2 = K + V;
- $`L`$: layers;
- $`T`$: tokens cacheados;
- $`n_{kv}`$: KV heads;
- $`d_h`$: head dimension;
- $`b`$: bytes por elemento;
- $`B`$: sequences/batch.

Marginal por token:

```math
\frac{\partial M_{KV}}{\partial T}=2Ln_{kv}d_hbB
```

Marginal por 1k tokens:

```math
\Delta M_{1k}=1000\cdot2Ln_{kv}d_hbB
```

Esse número é um dos dados mais úteis de qualquer ficha de modelo local.

### MLA

Modelos com Multi-head Latent Attention comprimem o estado K/V em uma representação latente menor. Não aplique cegamente a fórmula GQA como estimativa exata; use a parametrização específica do checkpoint/runtime.

---

## 4. Context scaling: memória e compute são problemas diferentes

Aumentar $`T`$:

- KV cresce aproximadamente $`O(T)`$;
- atenção full no prefill tem componente $`O(T^2)`$;
- decode consulta um cache crescente e tende a ter custo/token maior com $`T`$.

Portanto:

```math
Context\uparrow\Rightarrow RAM/VRAM\uparrow,\ prefill\ latency\uparrow,\ decode\ latency\uparrow
```

mesmo quando os pesos ficam idênticos.

---

## 5. Prefill ≠ decode

### Prefill

Processa prompt/context em blocos paralelos.

Self-attention clássico:

```math
C_{attn,prefill}\sim O(T^2d)
```

### Decode

Produz um token por passo consultando KV prévio:

```math
C_{attn,decode/token}\sim O(Td)
```

Além disso, cada token exige leitura significativa de weights. Em local inference quantizada, decode frequentemente é fortemente **memory-bandwidth bound**.

Consequência:

```math
TPS_{prompt}\neq TPS_{decode}
```

Sempre medir ambos.

---

## 6. Arithmetic intensity e roofline mental

Performance limitada por:

```math
Perf\le\min(PeakFLOPS,\ Bandwidth\times ArithmeticIntensity)
```

Se a inferência precisa reler muitos bytes para relativamente poucas operações por byte, mais TFLOPS não resolvem o gargalo.

### Decode batch=1

Tipicamente mais sensível a bandwidth/latência.

### Prefill / batching maior

Aumenta reutilização e arithmetic intensity; tende a usar compute melhor.

---

## 7. Offload CPU ↔ GPU

Separar:

1. pesos residentes em VRAM;
2. pesos residentes em RAM;
3. KV residente em GPU/CPU;
4. ativações transferidas;
5. layers divididas entre dispositivos.

Custo simplificado de transferência:

```math
t_{transfer}\approx\frac{bytes}{BW_{link}}+latency
```

### Thunderbolt / eGPU

Uma eGPU não deve ser modelada como “VRAM remota infinita”. Se o backend força transferência relevante por token/pass, o link pode virar gargalo. Se weights e KV críticos permanecem na VRAM e o link é usado principalmente na carga inicial ou em pontos pouco frequentes, o impacto é menor.

Regra de engenharia:

> **medir tráfego por token**, não apenas largura de banda nominal da interface.

---

## 8. GGUF quantization: não existe “Q4” único

Avaliar:

- block size;
- scales/zero points;
- symmetric vs asymmetric;
- mixed tensor precision;
- importance-aware quantization;
- outlier handling;
- effective bpw;
- dequant kernel;
- compute dtype;
- tensors preservados em maior precisão.

### Trade-off

```math
Memory\downarrow\leftrightarrow QuantizationError\uparrow
```

mas a curva depende fortemente de arquitetura, tensor e método.

---

## 9. KV quantization

KV pode dominar memória em contexto longo.

O `llama.cpp` atual expõe tipos independentes para K e V, incluindo `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0` e `q5_1`.

Isso transforma a equação:

```math
M_{KV}\propto b_{KV}
```

Reduzir de FP16 para ~8 bits aproxima uma redução de 2× na parte dominante do cache; para ~4–5 bits, ainda maior, sujeito a overhead e accuracy impact.

---

## 10. GQA, MQA e MLA como mecanismos de compressão de estado

### MHA

```math
n_{kv}=n_q
```

### GQA

```math
n_{kv}<n_q
```

### MQA

```math
n_{kv}=1
```

Consequência direta:

```math
M_{KV}\propto n_{kv}
```

MLA vai além, comprimindo K/V em latentes aprendidos.

---

## 11. MoE: compute ativo ≠ storage total

Para top-k routed MoE:

```math
y=\sum_{i\in TopK(g(x))}g_i(x)E_i(x)
```

Definir sempre:

- $`N_{total}`$: parâmetros armazenados;
- $`N_{active}`$: parâmetros usados/token;
- $`k`$: experts roteados/token.

### Insight local

```math
Compute/token\sim N_{active}
```

mas:

```math
Weight\ storage\sim N_{total}
```

Por isso MoE pode ser computacionalmente barato e ainda inviável em VRAM.

---

## 12. Activations e workspace

Em inferência batch=1, weights/KV costumam dominar LLMs, mas não assumir que ativações são irrelevantes.

Elas crescem com:

- batch;
- sequence/chunk size;
- hidden size;
- intermediate size;
- kernels escolhidos;
- FlashAttention/fused ops;
- multimodal encoders.

Diffusion/video podem ter activation peaks muito maiores que um LLM equivalente em tamanho de arquivo.

---

## 13. FlashAttention e atenção eficiente

Atenção ingênua materializa uma matriz $`T\times T`$.

FlashAttention e kernels correlatos reduzem I/O e evitam materializar toda a matriz intermediária, mudando drasticamente memória temporária e performance sem alterar a semântica ideal da atenção.

Não confundir:

```math
algorithmic\ complexity
```

com

```math
practical\ memory\ traffic
```

---

## 14. Speculative decoding

Modelo draft propõe múltiplos tokens; target verifica.

Idealmente, se vários tokens são aceitos por forward do target:

```math
throughput\uparrow
```

sem alterar a distribuição-alvo quando o algoritmo é exato.

Variáveis importantes:

- draft model quality;
- draft length;
- acceptance rate;
- target/draft latency;
- cache duplication;
- extra VRAM dos dois modelos.

Velocidade depende mais de **acceptance economics** que de “draft menor = melhor”.

---

## 15. Prompt/KV caching

Se um prefixo é idêntico, backends podem reutilizar compute/cache.

Economia aproximada:

```math
T_{saved}\approx T_{prefill(prefix)}
```

Útil para:

- system prompts longos;
- RP com lore fixo;
- agentes com tool catalogs estáveis;
- múltiplas queries sobre o mesmo corpus.

A estabilidade de serialização/template importa: pequenas mudanças podem invalidar o cache.

---

## 16. Diffusion/flow: custo físico

Para latente espacial:

```math
X\in\mathbb{R}^{B\times C\times H_l\times W_l}
```

Com patchification:

```math
N\approx\frac{H_l}{p_h}\frac{W_l}{p_w}
```

Atenção global ingênua:

```math
O(N^2)
```

### Vídeo

```math
N\approx T_pH_pW_p
```

portanto:

```math
O((T_pH_pW_p)^2)
```

antes de otimizações de fatoração/windowing/sparsity.

É por isso que temporal compression, spatial compression e windowed attention são parâmetros físicos, não detalhes cosméticos.

---

## 17. Planejamento para hardware híbrido

### Regra de colocação

Prioridade típica de VRAM rápida:

1. tensors acessados em todo token/pass;
2. KV ativo;
3. layers com maior frequência/transfer cost;
4. draft/refiner somente se benefício superar a pressão de memória.

### RAM compartilhada/iGPU

É capacidade útil, mas bandwidth/latência não equivalem a GDDR dedicada.

### eGPU

Modelar explicitamente:

```math
VRAM_{fast}=12GB
```

versus

```math
RAM_{host}=48GB
```

como pools de memória com propriedades distintas, não como “60 GB de VRAM”.

---

## 18. Checklist de viabilidade de um modelo local

1. Obter $`N_p`$ e quantização real.
2. Estimar $`M_W`$.
3. Identificar arquitetura de attention: MHA/GQA/MQA/MLA.
4. Calcular $`M_{KV}`$ no contexto-alvo.
5. Reservar activation/workspace/backend overhead.
6. Verificar quanto pode ficar na VRAM rápida.
7. Modelar offload e link.
8. Estimar gargalo: compute ou bandwidth.
9. Medir prompt TPS e decode TPS separadamente.
10. Só então comparar modelos.

---

## 19. Snapshot llama.cpp — 2026-10-01

O `llama.cpp` atual expõe, entre outros:

- quantização independente do K/V cache;
- GPU KV offload;
- YaRN parameters;
- grammar/lazy grammar;
- DRY;
- top-n-sigma;
- XTC;
- min-p;
- adaptive-p;
- speculative draft cache types;
- paralelismo de sequences.

Isso demonstra por que “temperature + top-p” já não é uma descrição suficiente de um runtime local moderno.

## Referências

- llama.cpp CLI — https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md
- llama.cpp sampling API — https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h
- DeepSeek-V3 / MLA + MoE — https://arxiv.org/abs/2412.19437

---

# PARTE II — RUNTIME ALÉM DO LLM TEXT-ONLY

> O runtime moderno precisa contabilizar não apenas pesos + KV, mas **encoders multimodais, índices externos, rerankers, iterative passes e múltiplos relógios de streaming**.

## 20. Multimodal token accounting

Para backbone compartilhado:

```math
T_{effective}
=
T_{text}+T_{vision}+T_{audio}+T_{video}+T_{special}
```

Se todos entram no mesmo KV:

```math
M_{KV}\propto T_{effective}
```

“1 imagem” não é unidade física de custo.

A unidade relevante é:

```math
N_{vision\ states}
```

---

## 21. Vision encoder residency

VLM pode exigir:

```math
M_{total}
=
M_{LLM}
+M_{vision\ encoder}
+M_{projector}
+M_{KV}
+M_{workspace}
```

Alguns runtimes mantêm encoder residente; outros carregam/offloadam.

Impacto:

- VRAM base;
- first-image latency;
- repeated-image throughput.

---

## 22. Visual token cost

Patchification idealizada:

```math
N_v\approx\frac{H}{P_h}\frac{W}{P_w}
```

Após merge fator $`m`$:

```math
N'_v\approx\frac{N_v}{m}
```

Logo resolução pode afetar tanto prefill quanto KV/context occupancy.

---

## 23. Video token cost

```math
N_{video}\approx
F\cdot N_{tokens/frame}
```

ou após temporal compression $`c_t`$:

```math
N_{video}\approx
\frac{F}{c_t}N_{spatial}
```

Vídeo longo é frequentemente limitado por **state budget**, não tamanho dos weights.

---

## 24. Audio state cost

Se encoder produz $`r_a`$ states/s:

```math
N_a=r_aD
```

Long-form speech precisa reduzir $`r_a`$, comprimir estados ou usar streaming/windowing.

---

# PARTE III — RETRIEVAL / RERANKING RUNTIME

## 25. Embedding compute

Para batch $`B`$, comprimento $`T`$:

```math
C_{embed}=B\cdot F_{encoder}(T)
```

Document embeddings são tipicamente offline; query embeddings são online.

Separar esses custos em sizing.

---

## 26. Vector index memory

Dense vectors:

```math
M_{vec}=N\cdot d\cdot b
```

Exemplo:

- $`N=10^6`$;
- $`d=1024`$;
- FP32 = 4 bytes.

```math
M_{vec}\approx4.096GB
```

antes de graph/IVF/PQ/metadata overhead.

---

## 27. HNSW runtime

Latência depende de `efSearch`, topologia, cache locality e corpus.

Não modelar ANN apenas como FLOPS.

HNSW é fortemente afetado por:

- random memory access;
- CPU cache;
- NUMA;
- RAM bandwidth.

Pode ser mais eficiente manter índice em RAM CPU e reservar VRAM para reranker/LLM.

---

## 28. Reranker economics

Com $`K`$ candidatos:

```math
C_{rerank}\approx K\cdot C_{cross-encoder}
```

Batching melhora utilization:

```math
Throughput_{batch}\uparrow
```

mas aumenta latency/VRAM peak.

Pipeline sizing deve medir:

```math
T_{RAG}=T_{embed}+T_{ANN}+T_{rerank}+T_{LLM}
```

não só LLM TPS.

---

# PARTE IV — AR VS PARALLEL LANGUAGE INFERENCE

## 29. Causal AR economics

Após prefill:

```math
T_{AR}\approx N_{out}\cdot t_{decode}
```

KV preserva prefixo.

Decode batch 1 tende a bandwidth-bound.

---

## 30. Iterative / diffusion text economics

Se $`K`$ refinement passes operam sobre $`N`$ posições:

```math
T_{iter}\approx K\cdot t_{pass}(N)
```

Speedup versus AR depende de:

```math
S
\approx
\frac{N_{out}t_{decode}}
{K\,t_{pass}(N)}
```

Se sequence pass é caro demais, paralelismo lógico não vira wall-clock gain.

---

## 31. Cache invalidation problem

AR:

```math
prefix\ immutable\Rightarrow KV\ reusable
```

Iterative refinement:

```math
old\ positions\ change\Rightarrow hidden/KV\ may\ invalidate
```

Backends específicos podem explorar block caches/parcialidade, mas não assumir equivalência com causal KV.

---

## 32. Serving regime matters

### Interactive single-user

Valoriza:

- TTFT;
- streaming;
- batch=1 latency.

### High-throughput server

Valoriza:

- total tokens/s;
- batch parallelism;
- accelerator utilization.

Um diffusion LM pode ser extraordinário no segundo regime e menos vantajoso no primeiro, dependendo da implementação.

---

# PARTE V — SPEECH STREAMING RUNTIME

## 33. RTF

```math
RTF=\frac{compute\ time}{audio\ duration}
```

Mas user-facing latency:

```math
T_{user}
=T_{chunk}+T_{lookahead}+T_{encode}+T_{decode}+T_{endpoint}
```

RTF < 1 não garante baixa latência.

---

## 34. Duplex/omni streaming

Pipeline de voz completo:

```math
Mic\rightarrow ASR/AudioEncoder\rightarrow Reasoning\rightarrow TTS/Talker\rightarrow Speaker
```

End-to-end latency:

```math
T_{E2E}=\sum_iT_i-overlap
```

Pipelining permite sobrepor etapas, mas cria estados simultaneamente residentes.

---

# PARTE VI — GRAPH / TABULAR / TIME-SERIES RUNTIME

## 35. Graph memory

Node states:

```math
M_V=|V|d_vb
```

Edge states:

```math
M_E=|E|d_eb
```

Neighborhood sampling pode trocar coverage por bounded memory.

---

## 36. Time-series token budget

Point tokens:

```math
N=T
```

Patch size $`P`$:

```math
N\approx T/P
```

Patching reduz atenção e memória, mas perde resolução local.

---

## 37. Tabular PFN context

Custo cresce com:

```math
N_{rows}\times N_{features}
```

após representação/tokenização do modelo.

In-context supervised inference pode ser compute-heavy mesmo sem qualquer fine-tuning.

---

# PARTE VII — HARDWARE BASELINE: 2060 12GB + 48GB DDR5 + TB4

## 38. Dois pools, não uma soma

Modelar:

```math
M_{fast}=12GB\ GDDR\ CUDA
```

```math
M_{host}=48GB\ DDR5
```

com link:

```math
BW_{TB4}\ll BW_{VRAM}
```

A iGPU/unified allocation também compartilha bandwidth do sistema.

Não escrever:

```math
12+48=60GB\ VRAM
```

porque isso destrói a variável mais importante: **localidade dos bytes por token/pass**.

---

## 39. Placement heuristic

Prioridade em VRAM rápida:

1. weights executados todo token/pass;
2. KV/state acessado intensamente;
3. hot experts/layers se backend suporta placement útil;
4. multimodal encoder durante percepção;
5. reranker apenas quando batch/latency justifica;
6. cold/offline components na RAM.

---

## 40. MoE no hardware híbrido

Mesmo com poucos experts ativos/token:

```math
Storage\sim N_{total}
```

Se experts precisam atravessar TB4 dinamicamente:

```math
Traffic/token\uparrow
```

pode destruir a vantagem de compute esparso.

MoE local precisa analisar **expert residency**, não apenas active params.

---

## 41. Viability worksheet universal

Para qualquer modelo/pipeline:

```math
M_{peak}
=
M_{weights,resident}
+M_{state}
+M_{activations}
+M_{workspace}
+M_{other\ models}
```

Depois estime:

```math
Traffic_{critical}/step
```

```math
Compute/step
```

```math
N_{steps}
```

Isso funciona para:

- LLM AR;
- diffusion image/video;
- omni;
- RAG;
- speech;
- iterative text;
- world model.

---

# PARTE VIII — NOVO CHECKLIST SOTA++

1. Quantos pesos ficam residentes onde?
2. Qual estado cresce com input/output?
3. O estado pode ser quantizado?
4. Qual componente é bandwidth-bound?
5. Existe encoder extra?
6. Quantos tokens/states cada modalidade adiciona?
7. Existe índice ANN fora da GPU?
8. Quantos reranker forwards por query?
9. AR ou iterative full/block passes?
10. Há cache reutilizável?
11. Qual streaming latency, não apenas throughput?
12. Qual pico simultâneo quando múltiplos componentes convivem?
13. O link CPU↔GPU é usado por token/pass ou só load-time?
14. Qual é a métrica certa: TTFT, TPS, RTF, queries/s, frames/s?

---

## Referências adicionais

- Multimodal accounting — [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md)
- Retrieval economics — [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md)
- Parallel language generation — [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md)
- Mercury — https://arxiv.org/abs/2506.17298
- Qwen3-ASR — https://arxiv.org/abs/2601.21337
