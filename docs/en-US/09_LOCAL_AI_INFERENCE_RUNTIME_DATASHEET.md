---
title: Local AI Inference & Runtime Datasheet v2.0 — VRAM, State, Retrieval, Multimodal and Parallel Inference
tags: [ai, local-ai, gguf, quantization, vram, inference, multimodal, retrieval, runtime]
updated: 2026-10-01
---

# Local AI Inference & Runtime Datasheet v2.0

> The model file is only the packaged weights. Inference is a dynamical system made of weights + caches + activations + workspaces + buffers + transfers.

## 1. The main physical equation

\[
M_{runtime}=M_W+M_{KV}+M_A+M_{workspace}+M_{graph}+M_{backend}
\]

Therefore:

\[
\boxed{required\ VRAM\neq GGUF\ file\ size}
\]

---

## 2. Weight memory

First approximation:

\[
M_W\approx\frac{N_p\cdot bpw}{8}
\]

where:

- \(N_p\): parameters;
- `bpw`: effective bits per weight.

Real quantizations have metadata, scales, block overhead, and often mixed types; use **effective bpw**, not the label “Q4” as if it meant exactly 4.000 bits/weight.

### Four independent quantization targets

\[
Q_W,\quad Q_{KV},\quad Q_A,\quad Q_{emb/out}
\]

- \(Q_W\): weights;
- \(Q_{KV}\): key/value cache;
- \(Q_A\): activations/intermediates;
- \(Q_{emb/out}\): embeddings/output head.

Quantizing weights does **not** imply quantized KV.

---

## 3. KV cache — memory that grows with context

For a conventional GQA/MHA Transformer:

\[
M_{KV}\approx2\,L\,T\,n_{kv}\,d_h\,b\,B
\]

- 2 = K + V;
- \(L\): layers;
- \(T\): cached tokens;
- \(n_{kv}\): KV heads;
- \(d_h\): head dimension;
- \(b\): bytes per element;
- \(B\): sequences/batch.

Marginal cost per token:

\[
\frac{\partial M_{KV}}{\partial T}=2Ln_{kv}d_hbB
\]

Marginal cost per 1k tokens:

\[
\Delta M_{1k}=1000\cdot2Ln_{kv}d_hbB
\]

This is one of the most useful numbers in any local-model datasheet.

### MLA

Models using Multi-head Latent Attention compress K/V state into a smaller latent representation. Do not blindly apply the GQA formula as an exact estimate; use the checkpoint/runtime-specific parameterization.

---

## 4. Context scaling: memory and compute are different problems

Increasing \(T\):

- KV grows approximately as \(O(T)\);
- full-attention prefill has an \(O(T^2)\) component;
- decode queries a growing cache and therefore tends to become more expensive per token as \(T\) grows.

Therefore:

\[
Context\uparrow\Rightarrow RAM/VRAM\uparrow,\ prefill\ latency\uparrow,\ decode\ latency\uparrow
\]

even when the weights are unchanged.

---

## 5. Prefill ≠ decode

### Prefill

Processes prompt/context in parallel chunks.

Classical self-attention:

\[
C_{attn,prefill}\sim O(T^2d)
\]

### Decode

Produces one token per step while querying the existing KV cache:

\[
C_{attn,decode/token}\sim O(Td)
\]

In addition, each token requires substantial weight reads. In quantized local inference, decode is often strongly **memory-bandwidth bound**.

Consequence:

\[
TPS_{prompt}\neq TPS_{decode}
\]

Always measure both.

---

## 6. Arithmetic intensity and the roofline mental model

Performance is bounded by:

\[
Perf\le\min(PeakFLOPS,\ Bandwidth\times ArithmeticIntensity)
\]

If inference must reread many bytes for relatively few operations per byte, more TFLOPS do not remove the bottleneck.

### Decode, batch=1

Typically more sensitive to bandwidth/latency.

### Prefill / larger batching

Increases reuse and arithmetic intensity; tends to utilize compute better.

---

## 7. CPU ↔ GPU offload

Separate:

1. weights resident in VRAM;
2. weights resident in RAM;
3. KV resident on GPU/CPU;
4. transferred activations;
5. layers split across devices.

Simplified transfer cost:

\[
t_{transfer}\approx\frac{bytes}{BW_{link}}+latency
\]

### Thunderbolt / eGPU

An eGPU should not be modeled as “infinite remote VRAM.” If the backend forces substantial transfers per token/pass, the link can become the bottleneck. If critical weights and KV remain in VRAM and the link is used mainly during initial loading or infrequent boundaries, the impact is smaller.

Engineering rule:

> **measure traffic per token**, not just the interface's nominal bandwidth.

---

## 8. GGUF quantization: there is no single “Q4”

Evaluate:

- block size;
- scales/zero points;
- symmetric vs asymmetric;
- mixed tensor precision;
- importance-aware quantization;
- outlier handling;
- effective bpw;
- dequant kernel;
- compute dtype;
- tensors preserved at higher precision.

### Trade-off

\[
Memory\downarrow\leftrightarrow QuantizationError\uparrow
\]

but the curve depends heavily on architecture, tensor, and method.

---

## 9. KV quantization

KV can dominate memory at long context.

Current `llama.cpp` exposes independent K and V types, including `f32`, `f16`, `bf16`, `q8_0`, `q4_0`, `q4_1`, `iq4_nl`, `q5_0`, and `q5_1`.

This changes the equation to:

\[
M_{KV}\propto b_{KV}
\]

Moving from FP16 to roughly 8-bit approaches a 2× reduction in the dominant cache component; ~4–5-bit can reduce it further, subject to overhead and accuracy impact.

---

## 10. GQA, MQA, and MLA as state-compression mechanisms

### MHA

\[
n_{kv}=n_q
\]

### GQA

\[
n_{kv}<n_q
\]

### MQA

\[
n_{kv}=1
\]

Direct consequence:

\[
M_{KV}\propto n_{kv}
\]

MLA goes further by compressing K/V into learned latents.

---

## 11. MoE: active compute ≠ total storage

For top-k routed MoE:

\[
y=\sum_{i\in TopK(g(x))}g_i(x)E_i(x)
\]

Always define:

- \(N_{total}\): stored parameters;
- \(N_{active}\): parameters used per token;
- \(k\): experts routed per token.

### Local-inference insight

\[
Compute/token\sim N_{active}
\]

but:

\[
Weight\ storage\sim N_{total}
\]

That is why an MoE can be compute-efficient while still being impossible to fit in VRAM.

---

## 12. Activations and workspace

For batch=1 LLM inference, weights/KV often dominate, but do not assume activations are irrelevant.

They grow with:

- batch;
- sequence/chunk size;
- hidden size;
- intermediate size;
- selected kernels;
- FlashAttention/fused ops;
- multimodal encoders.

Diffusion/video systems may have activation peaks far larger than an LLM with a similar model-file size.

---

## 13. FlashAttention and efficient attention

Naive attention materializes a \(T\times T\) matrix.

FlashAttention and related kernels reduce I/O and avoid materializing the full intermediate matrix, dramatically changing temporary memory and performance without changing the ideal semantics of attention.

Do not confuse:

\[
algorithmic\ complexity
\]

with

\[
practical\ memory\ traffic
\]

---

## 14. Speculative decoding

A draft model proposes multiple tokens; the target verifies them.

Ideally, if several tokens are accepted per target forward pass:

\[
throughput\uparrow
\]

without changing the target distribution when the algorithm is exact.

Important variables:

- draft model quality;
- draft length;
- acceptance rate;
- target/draft latency;
- cache duplication;
- extra VRAM for both models.

Speed depends more on **acceptance economics** than on “smaller draft = better.”

---

## 15. Prompt/KV caching

If a prefix is identical, backends can reuse compute/cache.

Approximate savings:

\[
T_{saved}\approx T_{prefill(prefix)}
\]

Useful for:

- long system prompts;
- RP with fixed lore;
- agents with stable tool catalogs;
- multiple queries over the same corpus.

Serialization/template stability matters: small changes can invalidate the cache.

---

## 16. Diffusion/flow: physical cost

For a spatial latent:

\[
X\in\mathbb{R}^{B\times C\times H_l\times W_l}
\]

With patchification:

\[
N\approx\frac{H_l}{p_h}\frac{W_l}{p_w}
\]

Naive global attention:

\[
O(N^2)
\]

### Video

\[
N\approx T_pH_pW_p
\]

therefore:

\[
O((T_pH_pW_p)^2)
\]

before factorization/windowing/sparsity optimizations.

That is why temporal compression, spatial compression, and windowed attention are physical parameters, not cosmetic details.

---

## 17. Planning for hybrid hardware

### Placement rule

Typical priority for fast VRAM:

1. tensors accessed on every token/pass;
2. active KV/state;
3. layers with the highest frequency/transfer cost;
4. draft/refiner only when the benefit exceeds memory pressure.

### Shared RAM/iGPU

It is useful capacity, but its bandwidth/latency is not equivalent to dedicated GDDR.

### eGPU

Explicitly model:

\[
VRAM_{fast}=12GB
\]

versus

\[
RAM_{host}=48GB
\]

as memory pools with different physical properties, not as “60 GB of VRAM.”

---

## 18. Local-model feasibility checklist

1. Obtain \(N_p\) and the real quantization.
2. Estimate \(M_W\).
3. Identify attention architecture: MHA/GQA/MQA/MLA.
4. Compute \(M_{KV}\) at the target context.
5. Reserve activation/workspace/backend overhead.
6. Determine how much can remain in fast VRAM.
7. Model offload and link cost.
8. Estimate the bottleneck: compute or bandwidth.
9. Measure prompt TPS and decode TPS separately.
10. Only then compare models.

---

## 19. llama.cpp snapshot — 2026-10-01

Current `llama.cpp` exposes, among other things:

- independent K/V-cache quantization;
- GPU KV offload;
- YaRN parameters;
- grammar/lazy grammar;
- DRY;
- top-n-sigma;
- XTC;
- min-p;
- adaptive-p;
- speculative draft cache types;
- sequence parallelism.

This demonstrates why “temperature + top-p” is no longer an adequate description of a modern local runtime.

## References

- llama.cpp CLI — https://github.com/ggml-org/llama.cpp/blob/master/tools/cli/README.md
- llama.cpp sampling API — https://github.com/ggml-org/llama.cpp/blob/master/include/llama.h
- DeepSeek-V3 / MLA + MoE — https://arxiv.org/abs/2412.19437

---

# PART II — RUNTIME BEYOND TEXT-ONLY LLMs

> A modern runtime must account not only for weights + KV, but also **multimodal encoders, external indexes, rerankers, iterative passes, and multiple streaming clocks**.

## 20. Multimodal token accounting

For a shared backbone:

\[
T_{effective}
=
T_{text}+T_{vision}+T_{audio}+T_{video}+T_{special}
\]

If all modalities enter the same KV state:

\[
M_{KV}\propto T_{effective}
\]

“1 image” is not a physical unit of cost.

The relevant unit is:

\[
N_{vision\ states}
\]

---

## 21. Vision-encoder residency

A VLM may require:

\[
M_{total}
=
M_{LLM}
+M_{vision\ encoder}
+M_{projector}
+M_{KV}
+M_{workspace}
\]

Some runtimes keep the encoder resident; others load/offload it.

Impact:

- base VRAM;
- first-image latency;
- repeated-image throughput.

---

## 22. Visual-token cost

Idealized patchification:

\[
N_v\approx\frac{H}{P_h}\frac{W}{P_w}
\]

After merge factor \(m\):

\[
N'_v\approx\frac{N_v}{m}
\]

So resolution can affect both prefill and KV/context occupancy.

---

## 23. Video-token cost

\[
N_{video}\approx
F\cdot N_{tokens/frame}
\]

or after temporal compression \(c_t\):

\[
N_{video}\approx
\frac{F}{c_t}N_{spatial}
\]

Long video is often limited by **state budget**, not weight size.

---

## 24. Audio-state cost

If the encoder produces \(r_a\) states/s:

\[
N_a=r_aD
\]

Long-form speech needs lower \(r_a\), compressed states, or streaming/windowing.

---

# PART III — RETRIEVAL / RERANKING RUNTIME

## 25. Embedding compute

For batch \(B\), length \(T\):

\[
C_{embed}=B\cdot F_{encoder}(T)
\]

Document embeddings are typically offline; query embeddings are online.

Keep those costs separate during sizing.

---

## 26. Vector-index memory

Dense vectors:

\[
M_{vec}=N\cdot d\cdot b
\]

Example:

- \(N=10^6\);
- \(d=1024\);
- FP32 = 4 bytes.

\[
M_{vec}\approx4.096GB
\]

before graph/IVF/PQ/metadata overhead.

---

## 27. HNSW runtime

Latency depends on `efSearch`, topology, cache locality, and corpus.

Do not model ANN as FLOPS alone.

HNSW is strongly affected by:

- random memory access;
- CPU cache;
- NUMA;
- RAM bandwidth.

It may be more efficient to keep the index in CPU RAM and reserve VRAM for the reranker/LLM.

---

## 28. Reranker economics

With \(K\) candidates:

\[
C_{rerank}\approx K\cdot C_{cross-encoder}
\]

Batching improves utilization:

\[
Throughput_{batch}\uparrow
\]

but increases latency/peak VRAM.

Pipeline sizing should measure:

\[
T_{RAG}=T_{embed}+T_{ANN}+T_{rerank}+T_{LLM}
\]

not just LLM TPS.

---

# PART IV — AR VS PARALLEL LANGUAGE INFERENCE

## 29. Causal AR economics

After prefill:

\[
T_{AR}\approx N_{out}\cdot t_{decode}
\]

KV preserves the prefix.

Batch-1 decode tends to be bandwidth-bound.

---

## 30. Iterative / diffusion-text economics

If \(K\) refinement passes operate over \(N\) positions:

\[
T_{iter}\approx K\cdot t_{pass}(N)
\]

Speedup over AR depends on:

\[
S
\approx
\frac{N_{out}t_{decode}}
{K\,t_{pass}(N)}
\]

If a full-sequence pass is too expensive, logical parallelism does not translate into wall-clock gain.

---

## 31. Cache-invalidation problem

AR:

\[
prefix\ immutable\Rightarrow KV\ reusable
\]

Iterative refinement:

\[
old\ positions\ change\Rightarrow hidden/KV\ may\ invalidate
\]

Specific backends may exploit block caches/partial recomputation, but do not assume equivalence with causal KV.

---

## 32. Serving regime matters

### Interactive single-user

Prioritizes:

- TTFT;
- streaming;
- batch=1 latency.

### High-throughput server

Prioritizes:

- total tokens/s;
- batch parallelism;
- accelerator utilization.

A diffusion LM may be extraordinary in the second regime and less advantageous in the first, depending on implementation.

---

# PART V — SPEECH STREAMING RUNTIME

## 33. RTF

\[
RTF=\frac{compute\ time}{audio\ duration}
\]

But user-facing latency is:

\[
T_{user}
=T_{chunk}+T_{lookahead}+T_{encode}+T_{decode}+T_{endpoint}
\]

RTF < 1 does not guarantee low latency.

---

## 34. Duplex/omni streaming

Complete voice pipeline:

\[
Mic\rightarrow ASR/AudioEncoder\rightarrow Reasoning\rightarrow TTS/Talker\rightarrow Speaker
\]

End-to-end latency:

\[
T_{E2E}=\sum_iT_i-overlap
\]

Pipelining allows stages to overlap, but creates multiple simultaneously resident states.

---

# PART VI — GRAPH / TABULAR / TIME-SERIES RUNTIME

## 35. Graph memory

Node states:

\[
M_V=|V|d_vb
\]

Edge states:

\[
M_E=|E|d_eb
\]

Neighborhood sampling can trade coverage for bounded memory.

---

## 36. Time-series token budget

Point tokens:

\[
N=T
\]

Patch size \(P\):

\[
N\approx T/P
\]

Patching reduces attention and memory, but sacrifices local resolution.

---

## 37. Tabular PFN context

Cost grows with:

\[
N_{rows}\times N_{features}
\]

after the model's representation/tokenization step.

In-context supervised inference can be compute-heavy even without any fine-tuning.

---

# PART VII — HARDWARE BASELINE: 2060 12GB + 48GB DDR5 + TB4

## 38. Two pools, not one sum

Model:

\[
M_{fast}=12GB\ GDDR\ CUDA
\]

\[
M_{host}=48GB\ DDR5
\]

with link:

\[
BW_{TB4}\ll BW_{VRAM}
\]

The iGPU/unified allocation also shares system bandwidth.

Do not write:

\[
12+48=60GB\ VRAM
\]

because that destroys the most important variable: **where the bytes live for each token/pass**.

---

## 39. Placement heuristic

Priority for fast VRAM:

1. weights executed every token/pass;
2. intensively accessed KV/state;
3. hot experts/layers if the backend supports useful placement;
4. multimodal encoder during perception;
5. reranker only when batch/latency justifies it;
6. cold/offline components in RAM.

---

## 40. MoE on hybrid hardware

Even with few experts active per token:

\[
Storage\sim N_{total}
\]

If experts must cross TB4 dynamically:

\[
Traffic/token\uparrow
\]

can erase the sparse-compute advantage.

Local MoE requires analyzing **expert residency**, not just active parameters.

---

## 41. Universal viability worksheet

For any model/pipeline:

\[
M_{peak}
=
M_{weights,resident}
+M_{state}
+M_{activations}
+M_{workspace}
+M_{other\ models}
\]

Then estimate:

\[
Traffic_{critical}/step
\]

\[
Compute/step
\]

\[
N_{steps}
\]

This works for:

- LLM AR;
- diffusion image/video;
- omni;
- RAG;
- speech;
- iterative text;
- world model.

---

# PART VIII — UPDATED SOTA++ CHECKLIST

1. How many weights reside where?
2. Which state grows with input/output?
3. Can that state be quantized?
4. Which component is bandwidth-bound?
5. Is there an extra encoder?
6. How many tokens/states does each modality add?
7. Is there an ANN index outside the GPU?
8. How many reranker forwards per query?
9. AR or iterative full/block passes?
10. Is there reusable cache?
11. What is the streaming latency, not just throughput?
12. What is the simultaneous peak when multiple components coexist?
13. Is the CPU↔GPU link used per token/pass or only at load time?
14. What is the right metric: TTFT, TPS, RTF, queries/s, frames/s?

---

## Additional references

- Multimodal accounting — [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md)
- Retrieval economics — [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md)
- Parallel language generation — [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md)
- Mercury — https://arxiv.org/abs/2506.17298
- Qwen3-ASR — https://arxiv.org/abs/2601.21337
