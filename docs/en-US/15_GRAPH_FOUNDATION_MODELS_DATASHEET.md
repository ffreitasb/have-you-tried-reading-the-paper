---
title: Graph Foundation Models Datasheet v1.0
tags: [ai, graph, gnn, graph-transformer, foundation-models, message-passing]
updated: 2026-10-01
---

# Graph Foundation Models Datasheet v1.0

> Text is a sequence. An image is a grid. A graph is **relation**. A node's position is not its index in a file; it is defined by the topology and attributes of the system.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md), [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

# 1. Fundamental state

Graph:

\[
G=(V,E)
\]

with:

- nodes \(V\);
- edges \(E\subseteq V\times V\).

With attributes:

\[
G=(V,E,X_V,X_E)
\]

where:

\[
X_V\in\mathbb R^{|V|\times d_v}
\]

\[
X_E\in\mathbb R^{|E|\times d_e}
\]

---

# 2. Graph types

- directed / undirected;
- weighted / unweighted;
- homogeneous / heterogeneous;
- static / temporal;
- signed;
- hypergraph;
- knowledge graph;
- molecular graph;
- web/social graph.

“Graph model” without specifying the graph type is almost as vague as saying “data model.”

---

# 3. Permutation invariance/equivariance

If we relabel node IDs using a permutation \(P\), the graph's structural meaning does not change.

For graph-level prediction we want invariance:

\[
f(PX,PAP^T)=f(X,A)
\]

For node-level representations we want equivariance:

\[
F(PX,PAP^T)=PF(X,A)
\]

This is a fundamental symmetry that a conventional sequence does not preserve automatically.

---

# 4. Message Passing Neural Network

State of node \(v\) at layer \(l\):

\[
h_v^{(l)}
\]

Message:

\[
m_v^{(l)}
=
\bigoplus_{u\in\mathcal N(v)}
\psi_l(h_v^{(l)},h_u^{(l)},e_{uv})
\]

Update:

\[
h_v^{(l+1)}
=
\phi_l(h_v^{(l)},m_v^{(l)})
\]

\(\bigoplus\) should typically be permutation-invariant:

- sum;
- mean;
- max;
- attention aggregation.

---

# 5. Receptive field

After 1 layer, a node sees its 1-hop neighborhood.

After \(L\) layers:

\[
ReceptiveField\approx L-hop
\]

But neighborhood size can grow exponentially:

\[
|N_L(v)|\sim d^L
\]

for average degree \(d\), before accounting for overlap.

This creates memory and sampling problems.

---

# 6. Oversmoothing

With many layers, node embeddings may converge:

\[
\|h_u^{(L)}-h_v^{(L)}\|\rightarrow0
\]

and lose discriminative power.

More depth does not automatically mean better representations.

---

# 7. Oversquashing

Large amounts of distant information must pass through a fixed-dimensional bottleneck:

\[
Many\ distant\ signals
\rightarrow
h_v\in\mathbb R^d
\]

Even without oversmoothing, the ability to transmit long-range dependencies can collapse.

This is a topological/information bottleneck.

---

# 8. Graph Attention

For edge \((v,u)\):

\[
q_v=W_Qh_v,
\quad k_u=W_Kh_u,
\quad v_u=W_Vh_u
\]

Score:

\[
e_{vu}=\frac{q_v^Tk_u}{\sqrt d}+b_{vu}
\]

\[
\alpha_{vu}=softmax_{u\in\mathcal N(v)}(e_{vu})
\]

Update:

\[
h'_v=\sum_{u\in\mathcal N(v)}\alpha_{vu}v_u
\]

Bias \(b_{vu}\) may encode structure, relation type, or distance.

---

# 9. Graph Transformer

A vanilla Transformer has no intrinsic knowledge of adjacency.

Structure must be injected through mechanisms such as:

- attention masks;
- shortest-path bias;
- edge encodings;
- degree encodings;
- Laplacian eigenvectors;
- random-walk features;
- structural tokens.

The fundamental question is:

\[
How\ is\ topology\ represented\ to\ attention?
\]

---

# 10. Laplacian positional encoding

Adjacency \(A\), degree \(D\).

Graph Laplacian:

\[
L=D-A
\]

or normalized:

\[
L_{sym}=I-D^{-1/2}AD^{-1/2}
\]

Eigenvectors:

\[
Lu_i=\lambda_i u_i
\]

may provide spectral coordinates.

### Caveat

Eigenvectors have sign ambiguities and degeneracies; the architecture must account for them.

---

# 11. Random-walk structural encoding

Transition matrix:

\[
P=D^{-1}A
\]

Return/visit probabilities after \(k\) steps:

\[
P^k
\]

carry local and global structural information.

---

# 12. Heterogeneous graphs

Types:

\[
type(v)\in\mathcal T_V
\]

\[
type(e)\in\mathcal T_E
\]

Messages may depend on relation type:

\[
m_{u\rightarrow v}
=\psi_{type(e)}(h_u,h_v)
\]

Knowledge graphs are a natural instance of this setting.

---

# 13. Temporal graphs

An edge carries a timestamp:

\[
e=(u,v,t)
\]

State becomes event-dependent:

\[
h_v(t^+)=F(h_v(t^-),event_t)
\]

Now the system has all three simultaneously:

- topology;
- time;
- memory.

---

# 14. Node-level tasks

\[
P(y_v|G,X)
\]

Examples:

- classification;
- regression;
- anomaly/fraud scoring.

---

# 15. Edge / link prediction

\[
P((u,v)\in E|G)
\]

Simple score:

\[
s(u,v)=h_u^Th_v
\]

or an MLP, bilinear form, or relation-aware scorer.

Negative sampling is a critical part of training.

---

# 16. Graph-level prediction

Readout:

\[
z_G=Readout(\{h_v\}_{v\in V})
\]

The readout must respect permutation invariance.

Then:

\[
P(y_G|z_G)
\]

Example: molecular-property prediction.

---

# 17. Graph generation

We want:

\[
p(G)
\]

or conditionally:

\[
p(G|C)
\]

Possible decompositions include:

- node generation;
- edge generation;
- adjacency generation;
- graph diffusion;
- autoregressive graph construction.

The state has no natural sequential ordering; any serialization imposes an artificial one.

---

# 18. Autoregressive graph generation

One possible serialization:

\[
p(G)=\prod_t p(action_t|action_{<t})
\]

with actions such as:

- add node;
- add edge;
- set attribute;
- stop.

Problem: different action orders may represent the same graph.

---

# 19. Graph diffusion

Corruption can be applied to:

- node attributes;
- edge states;
- adjacency;
- coordinates in molecular/3D graphs.

Then denoise:

\[
G_t\rightarrow G_{t-1}
\]

The process must respect structural and discrete constraints.

---

# 20. Graph tokenization

Foundation models need a way to map heterogeneous graphs into a shared interface.

Possibilities include:

- node tokens;
- subgraph tokens;
- motif tokens;
- random-walk sequences;
- structural encodings + features;
- learned graph patches.

There is no universal tokenizer analogous to BPE.

---

# 21. Graph foundation model

Goal: learn an operator transferable across graphs and tasks:

\[
f_\theta(G,task/context)\rightarrow output
\]

Challenges:

- different feature dimensions;
- different node/edge semantics;
- different graph sizes;
- different graph types;
- different task types.

---

# 22. Feature projection

A new graph may have:

\[
X\in\mathbb R^{N\times d_{new}}
\]

while the backbone expects \(d_h\).

Projector:

\[
H=XW_p
\]

If every dataset requires a new projector, “foundation” loses part of its ideal zero-shot character.

Acacia 2026 is relevant precisely because it aims to accept arbitrary dimensionalities/semantics without training additional projectors.

---

# 23. In-context graph learning

Analogy:

\[
ContextGraphs/Labels + QueryGraph
\rightarrow Prediction
\]

or examples of node/link tasks embedded in the structural context.

This moves adaptation from weight updates into inference/context.

---

# 24. Neighborhood sampling

On a very large graph, the full neighborhood is infeasible.

Fanout:

\[
K_1,K_2,\ldots,K_L
\]

Approximate sampled receptive field:

\[
N_{sample}\sim\prod_lK_l
\]

before overlap.

Trade-off:

\[
Fanout\uparrow\Rightarrow Coverage\uparrow,Memory\uparrow
\]

---

# 25. Full-batch vs mini-batch graph learning

Text/image datasets contain relatively independent examples.

A single giant graph contains shared dependencies.

Mini-batching therefore requires mechanisms such as:

- subgraph sampling;
- neighborhood sampling;
- cluster partitioning;
- graph batching.

This changes the data-pipeline engineering.

---

# 26. Memory scaling

Node states:

\[
M_V\approx |V|d_hb
\]

Edge states:

\[
M_E\approx |E|d_eb
\]

Global attention over all nodes:

\[
O(|V|^2)
\]

quickly becomes infeasible.

Graph structure enables sparse attention/message passing closer to:

\[
O(|E|d)
\]

in many regimes.

---

# 27. Scaling laws in graphs

GraphBFF 2026 demonstrates predictable scaling with model/data capacity in a graph-foundation-model regime and trains a 1.4B-parameter Transformer on 1B samples.

The relevant insight:

> the old intuition that “GNNs do not scale like Transformers” can no longer be treated as a universal law; architecture, batching, and pretraining diversity change the regime.

---

# 28. Web graph as a pretraining corpus

Acacia 2026 trains directly on the Common Crawl web graph and demonstrates:

- node classification;
- link prediction;
- clustering;
- graph generation;
- in-context behavior;
- no dependency on LLM pretraining.

This reinforces the idea that graph structure itself can serve as a foundation signal.

---

# 29. Graph + text multimodality

Many graphs contain node text:

\[
h_v=Fuse(GraphFeature_v,TextEncoder(text_v))
\]

Do not confuse a graph foundation model with “an LLM serializing edges.”

The two can coexist.

---

# 30. Metrics

Node classification:

- accuracy/F1/AUC/PR-AUC.

Link prediction:

- Hits@K;
- MRR;
- ROC-AUC;
- PR-AUC.

Graph regression:

- MAE/RMSE.

Generation:

- validity;
- uniqueness;
- novelty;
- structural/property distributions.

---

# 31. Failure surfaces

- oversmoothing;
- oversquashing;
- neighborhood explosion;
- heterophily;
- feature-semantics mismatch;
- projector dependence;
- graph-size shift;
- degree-distribution shift;
- temporal leakage;
- negative-sampling bias;
- disconnected components;
- permutation/order artifacts in serialization;
- graph-sparsification loss.

---

# 32. Graph FM dissection checklist

1. What kind of graph?
2. What is the node/edge state?
3. Message passing or global attention?
4. How does structure enter attention?
5. Is there positional/structural encoding?
6. What is the receptive field?
7. How are oversmoothing/oversquashing mitigated?
8. How does mini-batching work?
9. Is neighborhood sampling used?
10. What is the task interface?
11. Does it accept arbitrary feature dimensions?
12. Does it require a projector/fine-tune per dataset?
13. Does it support in-context graph learning?
14. How does it scale with |V| and |E|?
15. What is the cost of graph generation?

---

# Snapshot references

- Billion-Scale Graph Foundation Models / GraphBFF — https://arxiv.org/abs/2602.04768
- Acacia: Training Graph Foundation Models on The Web Graph — https://arxiv.org/abs/2609.30894
