---
title: Embedding / Retrieval / Reranker Datasheet v1.0
tags: [ai, embeddings, retrieval, rag, reranker, vector-search, ann]
updated: 2026-10-01
---

# Embedding / Retrieval / Reranker Datasheet v1.0

> Generative models aprendem a produzir estados. Embedding models aprendem a **organizar um espaço**. Retrieval é geometria + busca; reranking é uma segunda função de relevância mais cara e mais contextual.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 1. Pipeline canônico

```math
Query
\xrightarrow{Encoder}
z_q
\xrightarrow{Search}
\{d_1,\ldots,d_K\}
\xrightarrow{Reranker}
\{d'_1,\ldots,d'_k\}
\rightarrow Generator/Decision
```

RAG é esse **pipeline**, não um tipo único de modelo.

---

# 2. Dense embedding

Encoder:

```math
f_\theta(x)=z\in\mathbb R^d
```

Para normalização L2:

```math
\hat z=\frac{z}{\|z\|_2}
```

Cosine similarity:

```math
s_{cos}(q,d)
=
\frac{q^Td}{\|q\|\|d\|}
```

Se ambos normalizados:

```math
s_{cos}=q^Td
```

Logo cosine vira dot product.

---

# 3. Euclidean distance

```math
d_E(q,d)=\|q-d\|_2
```

Para vetores normalizados:

```math
\|q-d\|_2^2=2-2q^Td
```

Portanto cosine/dot/L2 podem induzir o mesmo ranking em condições específicas, mas **não universalmente**.

---

# 4. Pooling

Transformer produz:

```math
H=(h_1,\ldots,h_T)
```

Precisamos obter $`z`$.

## CLS pooling

```math
z=h_{CLS}
```

## Mean pooling

```math
z=\frac{1}{T}\sum_th_t
```

## Weighted/attention pooling

```math
z=\sum_t\alpha_th_t
```

Pooling é parte do modelo; não deve ser trocado arbitrariamente sem respeitar o training recipe.

---

# 5. Contrastive objective

Com positivo $`d^+`$:

```math
\mathcal L
=
-\log
\frac{\exp(sim(q,d^+)/\tau)}
{\exp(sim(q,d^+)/\tau)+\sum_j\exp(sim(q,d_j^-)/\tau)}
```

$`\tau`$ é **contrastive temperature**.

### Não confundir

```math
\tau_{contrastive}\neq T_{sampling}
```

Uma atua na loss de representação; outra no decode categórico.

---

# 6. Hard negatives

Negativo aleatório pode ser fácil:

```math
s(q,d^-_{random})\ll s(q,d^+)
```

Hard negative:

```math
s(q,d^-_{hard})\approx s(q,d^+)
```

Eles forçam fronteiras mais finas, mas falsos negativos podem ensinar a afastar itens semanticamente válidos.

---

# 7. Symmetric vs asymmetric retrieval

### Symmetric

Mesma natureza:

```math
Document\leftrightarrow Document
```

### Asymmetric

```math
Query\rightarrow Passage
```

Alguns modelos usam prompts/instructions diferentes:

```math
z_q=f("query:"+q)
```

```math
z_d=f("passage:"+d)
```

Ignorar esse recipe pode degradar retrieval mesmo com pesos corretos.

---

# 8. Matryoshka Representation Learning

Treino permite truncar embedding:

```math
z^{(d_1)}\subset z^{(d_2)}\subset\cdots\subset z^{(D)}
```

com dimensões menores preservando boa parte da geometria.

Trade-off:

```math
Dimension\downarrow
\Rightarrow
IndexMemory\downarrow,
SearchBW\downarrow,
Quality\downarrow\ potential
```

Útil para escolher custo sem retreinar.

---

# 9. Multimodal embeddings

Em vez de espaços separados:

```math
f_t(text),\quad f_v(image),\quad f_{vid}(video)
```

podem ser treinados para ocupar espaço comum:

```math
s(f_t(q),f_v(image^+))
>
s(f_t(q),f_v(image^-))
```

Qwen3-VL-Embedding em 2026 é exemplo de text/image/document-image/video retrieval com representação unificada e dimensões Matryoshka.

---

# 10. Sparse retrieval

Bag-of-words probabilístico clássico — BM25:

```math
score(q,d)=
\sum_{t\in q}
IDF(t)
\frac{f(t,d)(k_1+1)}
{f(t,d)+k_1(1-b+b|d|/avgdl)}
```

Dense retrieval não elimina BM25.

Dense captura semântica; sparse preserva matching lexical exato.

---

# 11. Learned sparse retrieval

Modelo neural pode produzir pesos esparsos no vocabulário:

```math
z\in\mathbb R^{|V|},\quad \|z\|_0\ll|V|
```

Combina interpretabilidade/índice invertido com expansão semântica aprendida.

---

# 12. Hybrid retrieval

Combine scores:

```math
s=\alpha s_{dense}+\beta s_{sparse}
```

ou combine ranks via Reciprocal Rank Fusion:

```math
RRF(d)=\sum_m\frac{1}{k+rank_m(d)}
```

RRF evita calibrar escalas de scores diretamente.

---

# 13. Late interaction

Em vez de um vetor por documento:

```math
D=(d_1,\ldots,d_n)
```

mantemos embeddings por token/subvector.

ColBERT-like MaxSim:

```math
score(Q,D)=
\sum_{q_i\in Q}
\max_{d_j\in D}q_i^Td_j
```

É um meio-termo entre bi-encoder e cross-encoder.

Trade-off:

```math
Quality\uparrow
\leftrightarrow
IndexSize/Compute\uparrow
```

---

# 14. Bi-encoder vs cross-encoder

## Bi-encoder

```math
z_q=f(q),\quad z_d=f(d)
```

```math
score=z_q^Tz_d
```

Documentos podem ser pré-computados.

## Cross-encoder

```math
score=f_\theta([q;d])
```

Tokens interagem dentro da mesma rede.

### Resultado físico

Bi-encoder:

```math
O(1)\ embedding/query + ANN
```

Cross-encoder para $`K`$ candidatos:

```math
O(K\cdot Forward(q,d_i))
```

Por isso o padrão:

```math
1000\ retrieved\rightarrow 50\ reranked\rightarrow 5\ context
```

---

# 15. Reranker score

Pode ser:

- regressão escalar;
- binary relevance logit;
- pairwise ranking;
- generative yes/no/relevance;
- listwise ranking.

### Binary logit

```math
p(relevant|q,d)=\sigma(z)
```

Score bruto não é automaticamente probabilidade calibrada.

---

# 16. Approximate Nearest Neighbor — ANN

Busca exata sobre $`N`$ vetores de dimensão $`d`$:

```math
O(Nd)
```

ANN troca exatidão por latência/memória.

---

# 17. HNSW

Grafo multicamada aproximado.

Variáveis práticas:

- `M`: grau/conectividade;
- `efConstruction`: esforço durante indexação;
- `efSearch`: largura de exploração na query.

Tendência:

```math
efSearch\uparrow
\Rightarrow
Recall\uparrow,
Latency\uparrow
```

```math
M\uparrow
\Rightarrow
Memory\uparrow,
GraphConnectivity\uparrow
```

Curvas são dataset-dependent.

---

# 18. IVF

Treine $`n_{list}`$ centroides:

```math
\{c_1,\ldots,c_{nlist}\}
```

Cada vetor é atribuído a uma célula.

Na busca, examinar `nprobe` células.

```math
nprobe\uparrow
\Rightarrow Recall\uparrow,Latency\uparrow
```

---

# 19. Product Quantization — PQ

Divida vetor em $`m`$ subvetores:

```math
z=[z^{(1)},\ldots,z^{(m)}]
```

Quantize cada subespaço por codebook.

Memória cai drasticamente, mas distância é aproximada.

Não confundir PQ do índice com quantização de weights do encoder.

---

# 20. Chunking é parte do modelo de informação

Documento:

```math
D\rightarrow\{c_1,\ldots,c_n\}
```

Chunk length $`L`$ e overlap $`O`$ mudam o corpus efetivo.

### Muito curto

- perde contexto local;
- cria fragmentos ambíguos.

### Muito longo

- embedding mistura múltiplos tópicos;
- recall específico cai;
- reranker/generator recebe ruído.

Logo:

```math
RetrievalQuality=f(model,chunking,index,query)
```

não apenas do embedding model.

---

# 21. Contextual chunk embeddings

Problema:

```math
Embedding(c_i)
```

pode não saber título/documento pai.

Solução pipeline:

```math
Embedding(metadata+summary+chunk)
```

ou hierarchical retrieval.

Isso aumenta semantic specificity, mas pode introduzir informação não presente no trecho.

---

# 22. Retrieval metrics

## Recall@K

```math
Recall@K=
\frac{|Relevant\cap TopK|}{|Relevant|}
```

## Precision@K

```math
Precision@K=
\frac{|Relevant\cap TopK|}{K}
```

## Reciprocal Rank

```math
RR=\frac{1}{rank_{first\ relevant}}
```

## MRR

```math
MRR=\frac1N\sum_iRR_i
```

## DCG

```math
DCG@K=
\sum_{i=1}^{K}
\frac{2^{rel_i}-1}{\log_2(i+1)}
```

nDCG normaliza pelo ranking ideal.

---

# 23. Retrieval threshold não é confidence universal

Similarity score depende de:

- modelo;
- normalização;
- corpus;
- query distribution;
- index approximation.

Não existe regra universal:

> “cosine > 0.8 = bom”.

Calibre no seu corpus:

```math
Threshold^*=argmax\ Metric(Threshold)
```

---

# 24. RAG failure decomposition

Erro final pode ser:

### Retrieval miss

```math
Relevant\notin TopK
```

### Reranker miss

```math
Relevant\in TopK,
Relevant\notin Topk_{reranked}
```

### Context packing miss

Evidência foi cortada/ordenada mal.

### Generator miss

Evidência correta chegou, mas LLM errou.

Separar essas classes antes de “trocar o LLM”.

---

# 25. Memory accounting do índice

Dense FP32 aproximado:

```math
M_{vectors}=N\cdot d\cdot4\ bytes
```

FP16:

```math
M=N\cdot d\cdot2
```

mais overhead:

```math
M_{index}=M_{vectors}+M_{graph/codebooks}+metadata
```

1M vetores × 1024 dims × FP32 ≈ 4.096 GB **antes** do índice/metadata.

Esse cálculo deve preceder a escolha de dimensionalidade.

---

# 26. Failure surfaces

- embedding anisotropy;
- semantic hubness;
- domain mismatch;
- false negatives no treinamento;
- lexical miss em dense-only;
- semantic miss em sparse-only;
- overchunking;
- query/document recipe incorreto;
- ANN recall baixo;
- reranker overfitting;
- stale index.

---

# 27. Snapshot 2026

Qwen3-VL-Embedding/Reranker mostra a convergência de retrieval multimodal:

- text, image, document images, video;
- embedding + cross-encoder reranker como pipeline coordenado;
- Matryoshka dimensions;
- contexto longo.

A tendência relevante é menos “qual modelo ganhou benchmark” e mais:

```math
Retrieval\ pipeline
=
Representation
+
ApproximateSearch
+
FineRanking
```

---

# 28. Checklist de engenharia

1. A tarefa é symmetric ou asymmetric?
2. O modelo exige instruction prefix?
3. Embeddings são normalizados?
4. Qual métrica o índice usa?
5. Qual dimensão realmente é necessária?
6. Há Matryoshka?
7. Qual chunking representa a unidade semântica certa?
8. Qual Recall@K antes do reranker?
9. Qual ganho marginal do reranker?
10. O threshold foi calibrado?
11. Qual footprint do índice?
12. Qual latência end-to-end, não apenas ANN?
13. Dense, sparse ou hybrid?
14. Você consegue distinguir retrieval miss de generation miss?

---

# Referências snapshot

- Qwen3-VL-Embedding and Qwen3-VL-Reranker — https://arxiv.org/abs/2601.04720
- TabPFN/other structured representations are covered separately in [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md).
