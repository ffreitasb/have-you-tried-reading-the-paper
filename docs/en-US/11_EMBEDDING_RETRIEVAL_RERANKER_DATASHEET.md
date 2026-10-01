---
title: Embedding / Retrieval / Reranker Datasheet v1.0
tags: [ai, embeddings, retrieval, rag, reranker, vector-search, ann]
updated: 2026-10-01
---

# Embedding / Retrieval / Reranker Datasheet v1.0

> Generative models learn to produce states. Embedding models learn to **organize a space**. Retrieval is geometry + search; reranking is a second, more expensive and more contextual relevance function.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 1. Canonical pipeline

\[
Query
\xrightarrow{Encoder}
z_q
\xrightarrow{Search}
\{d_1,\ldots,d_K\}
\xrightarrow{Reranker}
\{d'_1,\ldots,d'_k\}
\rightarrow Generator/Decision
\]

RAG is this **pipeline**, not a single model type.

---

# 2. Dense embedding

Encoder:

\[
f_\theta(x)=z\in\mathbb R^d
\]

For L2 normalization:

\[
\hat z=\frac{z}{\|z\|_2}
\]

Cosine similarity:

\[
s_{cos}(q,d)
=
\frac{q^Td}{\|q\|\|d\|}
\]

If both are normalized:

\[
s_{cos}=q^Td
\]

So cosine becomes dot product.

---

# 3. Euclidean distance

\[
d_E(q,d)=\|q-d\|_2
\]

For normalized vectors:

\[
\|q-d\|_2^2=2-2q^Td
\]

Therefore cosine/dot/L2 can induce the same ranking under specific conditions, but **not universally**.

---

# 4. Pooling

A Transformer produces:

\[
H=(h_1,\ldots,h_T)
\]

We need to obtain \(z\).

## CLS pooling

\[
z=h_{CLS}
\]

## Mean pooling

\[
z=\frac{1}{T}\sum_th_t
\]

## Weighted/attention pooling

\[
z=\sum_t\alpha_th_t
\]

Pooling is part of the model recipe; it should not be swapped arbitrarily without respecting training.

---

# 5. Contrastive objective

With positive \(d^+\):

\[
\mathcal L
=
-\log
\frac{\exp(sim(q,d^+)/\tau)}
{\exp(sim(q,d^+)/\tau)+\sum_j\exp(sim(q,d_j^-)/\tau)}
\]

\(\tau\) is **contrastive temperature**.

### Do not confuse

\[
\tau_{contrastive}\neq T_{sampling}
\]

One acts on representation learning; the other on categorical decoding.

---

# 6. Hard negatives

A random negative may be easy:

\[
s(q,d^-_{random})\ll s(q,d^+)
\]

A hard negative:

\[
s(q,d^-_{hard})\approx s(q,d^+)
\]

forces finer decision boundaries, but false negatives can train the model to push away semantically valid items.

---

# 7. Symmetric vs asymmetric retrieval

### Symmetric

Same kind of object:

\[
Document\leftrightarrow Document
\]

### Asymmetric

\[
Query\rightarrow Passage
\]

Some models use different prompts/instructions:

\[
z_q=f("query:"+q)
\]

\[
z_d=f("passage:"+d)
\]

Ignoring this recipe can degrade retrieval even with the correct weights.

---

# 8. Matryoshka Representation Learning

Training allows the embedding to be truncated:

\[
z^{(d_1)}\subset z^{(d_2)}\subset\cdots\subset z^{(D)}
\]

with smaller dimensions preserving much of the geometry.

Trade-off:

\[
Dimension\downarrow
\Rightarrow
IndexMemory\downarrow,
SearchBW\downarrow,
Quality\downarrow\ potential
\]

Useful for changing cost without retraining.

---

# 9. Multimodal embeddings

Instead of separate spaces:

\[
f_t(text),\quad f_v(image),\quad f_{vid}(video)
\]

models can be trained to occupy one shared space:

\[
s(f_t(q),f_v(image^+))
>
s(f_t(q),f_v(image^-))
\]

Qwen3-VL-Embedding in 2026 is an example of text/image/document-image/video retrieval with unified representations and Matryoshka dimensions.

---

# 10. Sparse retrieval

Classic probabilistic bag-of-words — BM25:

\[
score(q,d)=
\sum_{t\in q}
IDF(t)
\frac{f(t,d)(k_1+1)}
{f(t,d)+k_1(1-b+b|d|/avgdl)}
\]

Dense retrieval does not make BM25 obsolete.

Dense captures semantics; sparse preserves exact lexical matching.

---

# 11. Learned sparse retrieval

A neural model may produce sparse vocabulary weights:

\[
z\in\mathbb R^{|V|},\quad \|z\|_0\ll|V|
\]

This combines interpretability/inverted indexes with learned semantic expansion.

---

# 12. Hybrid retrieval

Combine scores:

\[
s=\alpha s_{dense}+\beta s_{sparse}
\]

or combine ranks with Reciprocal Rank Fusion:

\[
RRF(d)=\sum_m\frac{1}{k+rank_m(d)}
\]

RRF avoids directly calibrating score scales.

---

# 13. Late interaction

Instead of one vector per document:

\[
D=(d_1,\ldots,d_n)
\]

keep token/subvector embeddings.

ColBERT-like MaxSim:

\[
score(Q,D)=
\sum_{q_i\in Q}
\max_{d_j\in D}q_i^Td_j
\]

This is a middle ground between bi-encoders and cross-encoders.

Trade-off:

\[
Quality\uparrow
\leftrightarrow
IndexSize/Compute\uparrow
\]

---

# 14. Bi-encoder vs cross-encoder

## Bi-encoder

\[
z_q=f(q),\quad z_d=f(d)
\]

\[
score=z_q^Tz_d
\]

Documents can be precomputed.

## Cross-encoder

\[
score=f_\theta([q;d])
\]

Tokens interact inside the same network.

### Physical result

Bi-encoder:

\[
O(1)\ embedding/query + ANN
\]

Cross-encoder for \(K\) candidates:

\[
O(K\cdot Forward(q,d_i))
\]

Hence the common pattern:

\[
1000\ retrieved\rightarrow 50\ reranked\rightarrow 5\ context
\]

---

# 15. Reranker score

It may be:

- scalar regression;
- binary relevance logit;
- pairwise ranking;
- generative yes/no/relevance;
- listwise ranking.

### Binary logit

\[
p(relevant|q,d)=\sigma(z)
\]

A raw score is not automatically a calibrated probability.

---

# 16. Approximate Nearest Neighbor — ANN

Exact search over \(N\) vectors of dimension \(d\):

\[
O(Nd)
\]

ANN trades exactness for latency/memory.

---

# 17. HNSW

Approximate multilayer graph.

Practical variables:

- `M`: degree/connectivity;
- `efConstruction`: indexing effort;
- `efSearch`: query exploration width.

Trend:

\[
efSearch\uparrow
\Rightarrow
Recall\uparrow,
Latency\uparrow
\]

\[
M\uparrow
\Rightarrow
Memory\uparrow,
GraphConnectivity\uparrow
\]

The actual curves are dataset-dependent.

---

# 18. IVF

Train \(n_{list}\) centroids:

\[
\{c_1,\ldots,c_{nlist}\}
\]

Each vector is assigned to a cell.

At query time, inspect `nprobe` cells.

\[
nprobe\uparrow
\Rightarrow Recall\uparrow,Latency\uparrow
\]

---

# 19. Product Quantization — PQ

Split the vector into \(m\) subvectors:

\[
z=[z^{(1)},\ldots,z^{(m)}]
\]

Quantize each subspace with a codebook.

Memory drops dramatically, but distance becomes approximate.

Do not confuse index PQ with encoder-weight quantization.

---

# 20. Chunking is part of the information model

Document:

\[
D\rightarrow\{c_1,\ldots,c_n\}
\]

Chunk length \(L\) and overlap \(O\) change the effective corpus.

### Too short

- loses local context;
- creates ambiguous fragments.

### Too long

- embedding mixes multiple topics;
- specific recall falls;
- reranker/generator receives noise.

Therefore:

\[
RetrievalQuality=f(model,chunking,index,query)
\]

not just the embedding model.

---

# 21. Contextual chunk embeddings

Problem:

\[
Embedding(c_i)
\]

may not know the title or parent document.

Pipeline solution:

\[
Embedding(metadata+summary+chunk)
\]

or hierarchical retrieval.

This increases semantic specificity, but may inject information that is not present in the chunk itself.

---

# 22. Retrieval metrics

## Recall@K

\[
Recall@K=
\frac{|Relevant\cap TopK|}{|Relevant|}
\]

## Precision@K

\[
Precision@K=
\frac{|Relevant\cap TopK|}{K}
\]

## Reciprocal Rank

\[
RR=\frac{1}{rank_{first\ relevant}}
\]

## MRR

\[
MRR=\frac1N\sum_iRR_i
\]

## DCG

\[
DCG@K=
\sum_{i=1}^{K}
\frac{2^{rel_i}-1}{\log_2(i+1)}
\]

nDCG normalizes by the ideal ranking.

---

# 23. Retrieval threshold is not universal confidence

Similarity score depends on:

- model;
- normalization;
- corpus;
- query distribution;
- index approximation.

There is no universal rule such as:

> “cosine > 0.8 = good.”

Calibrate on your own corpus:

\[
Threshold^*=argmax\ Metric(Threshold)
\]

---

# 24. RAG failure decomposition

Final error may be:

### Retrieval miss

\[
Relevant\notin TopK
\]

### Reranker miss

\[
Relevant\in TopK,
Relevant\notin Topk_{reranked}
\]

### Context-packing miss

Evidence was truncated or ordered badly.

### Generator miss

Correct evidence reached the LLM, but the LLM still failed.

Separate these classes before “changing the LLM.”

---

# 25. Index memory accounting

Approximate dense FP32 storage:

\[
M_{vectors}=N\cdot d\cdot4\ bytes
\]

FP16:

\[
M=N\cdot d\cdot2
\]

plus overhead:

\[
M_{index}=M_{vectors}+M_{graph/codebooks}+metadata
\]

1M vectors × 1024 dims × FP32 ≈ 4.096 GB **before** index/metadata overhead.

Do this calculation before choosing dimensionality.

---

# 26. Failure surfaces

- embedding anisotropy;
- semantic hubness;
- domain mismatch;
- false negatives during training;
- lexical miss in dense-only;
- semantic miss in sparse-only;
- overchunking;
- wrong query/document recipe;
- low ANN recall;
- reranker overfitting;
- stale index.

---

# 27. Snapshot 2026

Qwen3-VL-Embedding/Reranker illustrates the convergence of multimodal retrieval:

- text, image, document images, video;
- embedding + cross-encoder reranker as a coordinated pipeline;
- Matryoshka dimensions;
- long context.

The relevant trend is less “which model won a benchmark?” and more:

\[
Retrieval\ pipeline
=
Representation
+
ApproximateSearch
+
FineRanking
\]

---

# 28. Engineering checklist

1. Is the task symmetric or asymmetric?
2. Does the model require an instruction prefix?
3. Are embeddings normalized?
4. Which metric does the index use?
5. Which dimension is actually necessary?
6. Is Matryoshka available?
7. Which chunking strategy represents the right semantic unit?
8. What is Recall@K before reranking?
9. What is the reranker's marginal gain?
10. Was the threshold calibrated?
11. What is the index footprint?
12. What is end-to-end latency, not just ANN latency?
13. Dense, sparse, or hybrid?
14. Can you distinguish a retrieval miss from a generation miss?

---

# Snapshot references

- Qwen3-VL-Embedding and Qwen3-VL-Reranker — https://arxiv.org/abs/2601.04720
- TabPFN/other structured representations are covered separately in [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md).
