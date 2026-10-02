---
title: Graph Foundation Models Datasheet v1.0
tags: [ai, graph, gnn, graph-transformer, foundation-models, message-passing]
updated: 2026-10-01
---

# Graph Foundation Models Datasheet v1.0

> Texto é sequência. Imagem é grade. Grafo é **relação**. A posição de um nó não é seu índice no arquivo: é definida pela topologia e pelos atributos do sistema.

Relacionados: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md), [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

# 1. Estado fundamental

Grafo:

```math
G=(V,E)
```

com:

- nós $`V`$;
- arestas $`E\subseteq V\times V`$.

Com atributos:

```math
G=(V,E,X_V,X_E)
```

onde:

```math
X_V\in\mathbb R^{|V|\times d_v}
```

```math
X_E\in\mathbb R^{|E|\times d_e}
```

---

# 2. Tipos de grafo

- directed / undirected;
- weighted / unweighted;
- homogeneous / heterogeneous;
- static / temporal;
- signed;
- hypergraph;
- knowledge graph;
- molecular graph;
- web/social graph.

“Graph model” sem especificar o tipo é quase tão vago quanto “modelo de dados”.

---

# 3. Permutation invariance/equivariance

Se renomearmos os IDs dos nós por uma permutação $`P`$, a semântica estrutural não muda.

Para graph-level prediction desejamos invariância:

```math
f(PX,PAP^T)=f(X,A)
```

Para node-level representation desejamos equivariância:

```math
F(PX,PAP^T)=PF(X,A)
```

Essa é uma simetria fundamental que uma sequência comum não preserva automaticamente.

---

# 4. Message Passing Neural Network

Estado do nó $`v`$ na camada $`l`$:

```math
h_v^{(l)}
```

Mensagem:

```math
m_v^{(l)}
=
\bigoplus_{u\in\mathcal N(v)}
\psi_l(h_v^{(l)},h_u^{(l)},e_{uv})
```

Update:

```math
h_v^{(l+1)}
=
\phi_l(h_v^{(l)},m_v^{(l)})
```

$`\bigoplus`$ deve tipicamente ser permutation-invariant:

- sum;
- mean;
- max;
- attention aggregation.

---

# 5. Receptive field

Após 1 camada, nó vê 1-hop.

Após $`L`$:

```math
ReceptiveField\approx L-hop
```

Mas vizinhança pode crescer exponencialmente:

```math
|N_L(v)|\sim d^L
```

para grau médio $`d`$, antes de sobreposição.

Isso cria problemas de memória/sampling.

---

# 6. Oversmoothing

Com muitas camadas, embeddings podem convergir:

```math
\|h_u^{(L)}-h_v^{(L)}\|\rightarrow0
```

perdendo discriminabilidade.

Mais profundidade ≠ melhor automaticamente.

---

# 7. Oversquashing

Muita informação distante precisa atravessar bottleneck dimensional fixo:

```math
Many\ distant\ signals
\rightarrow
h_v\in\mathbb R^d
```

Mesmo sem oversmoothing, capacidade de transportar dependências long-range pode colapsar.

É um problema topológico/informacional.

---

# 8. Graph Attention

Para aresta $`(v,u)`$:

```math
q_v=W_Qh_v,
\quad k_u=W_Kh_u,
\quad v_u=W_Vh_u
```

Score:

```math
e_{vu}=\frac{q_v^Tk_u}{\sqrt d}+b_{vu}
```

```math
\alpha_{vu}=softmax_{u\in\mathcal N(v)}(e_{vu})
```

Update:

```math
h'_v=\sum_{u\in\mathcal N(v)}\alpha_{vu}v_u
```

Bias $`b_{vu}`$ pode carregar estrutura/tipo/distância.

---

# 9. Graph Transformer

Transformer vanilla não conhece adjacency.

Precisamos injetar estrutura por:

- attention masks;
- shortest-path bias;
- edge encodings;
- degree encodings;
- Laplacian eigenvectors;
- random-walk features;
- structural tokens.

A pergunta fundamental:

```math
How\ is\ topology\ represented\ to\ attention?
```

---

# 10. Laplacian positional encoding

Adjacency $`A`$, degree $`D`$.

Graph Laplacian:

```math
L=D-A
```

ou normalizado:

```math
L_{sym}=I-D^{-1/2}AD^{-1/2}
```

Eigenvectors:

```math
Lu_i=\lambda_i u_i
```

podem fornecer coordenadas espectrais.

### Caveat

Eigenvectors possuem ambiguidades de sinal e degeneracies; arquitetura precisa tratar isso.

---

# 11. Random-walk structural encoding

Transition matrix:

```math
P=D^{-1}A
```

Probabilidades de retorno/visita após $`k`$ passos:

```math
P^k
```

carregam informação estrutural local/global.

---

# 12. Heterogeneous graphs

Tipos:

```math
type(v)\in\mathcal T_V
```

```math
type(e)\in\mathcal T_E
```

Mensagem pode depender da relação:

```math
m_{u\rightarrow v}
=\psi_{type(e)}(h_u,h_v)
```

Knowledge graphs são caso natural.

---

# 13. Temporal graphs

Aresta possui timestamp:

```math
e=(u,v,t)
```

Estado passa a depender de eventos:

```math
h_v(t^+)=F(h_v(t^-),event_t)
```

Agora temos simultaneamente:

- topologia;
- tempo;
- memória.

---

# 14. Node-level tasks

```math
P(y_v|G,X)
```

Exemplos:

- classificação;
- regressão;
- anomaly/fraud score.

---

# 15. Edge / link prediction

```math
P((u,v)\in E|G)
```

Score simples:

```math
s(u,v)=h_u^Th_v
```

ou MLP/bilinear/relation-aware.

Negative sampling é parte crítica do treinamento.

---

# 16. Graph-level prediction

Readout:

```math
z_G=Readout(\{h_v\}_{v\in V})
```

Readout deve respeitar permutation invariance.

Depois:

```math
P(y_G|z_G)
```

Ex.: propriedade molecular.

---

# 17. Graph generation

Queremos:

```math
p(G)
```

ou condicional:

```math
p(G|C)
```

Pode decompor em:

- node generation;
- edge generation;
- adjacency generation;
- graph diffusion;
- autoregressive graph construction.

O estado não é uma sequência natural; qualquer serialização impõe ordem artificial.

---

# 18. Autoregressive graph generation

Uma serialização possível:

```math
p(G)=\prod_t p(action_t|action_{<t})
```

com ações:

- add node;
- add edge;
- set attribute;
- stop.

Problema: diferentes ordens podem representar o mesmo grafo.

---

# 19. Graph diffusion

Pode-se corromper:

- node attributes;
- edge states;
- adjacency;
- coordinates em moléculas/3D.

Depois denoise:

```math
G_t\rightarrow G_{t-1}
```

Precisa respeitar constraints estruturais/discretas.

---

# 20. Graph tokenization

Foundation models precisam mapear grafos heterogêneos para uma interface compartilhável.

Possibilidades:

- node tokens;
- subgraph tokens;
- motif tokens;
- random-walk sequences;
- structural encodings + features;
- learned graph patches.

Não há tokenizer universal análogo a BPE.

---

# 21. Graph foundation model

Objetivo: aprender operador transferível entre grafos/tarefas:

```math
f_\theta(G,task/context)\rightarrow output
```

Desafios:

- feature dimensions diferentes;
- node/edge semantics diferentes;
- graph size diferente;
- graph type diferente;
- task type diferente.

---

# 22. Feature projection

Novo grafo pode ter:

```math
X\in\mathbb R^{N\times d_{new}}
```

mas backbone espera $`d_h`$.

Projector:

```math
H=XW_p
```

Se cada dataset exige projector novo, “foundation” perde parte do zero-shot ideal.

Acacia 2026 é relevante justamente por buscar aceitar dimensionalidades/semânticas arbitrárias sem treinar projectors adicionais.

---

# 23. In-context graph learning

Analogia:

```math
ContextGraphs/Labels + QueryGraph
\rightarrow Prediction
```

ou exemplos de node/link tasks dentro do contexto estrutural.

Isso desloca adaptação de weight updates para inferência/contexto.

---

# 24. Sampling neighborhoods

Em grafo enorme, full neighborhood é inviável.

Fanout:

```math
K_1,K_2,\ldots,K_L
```

Sampled receptive field aproximadamente:

```math
N_{sample}\sim\prod_lK_l
```

antes de overlap.

Trade-off:

```math
Fanout\uparrow\Rightarrow Coverage\uparrow,Memory\uparrow
```

---

# 25. Full-batch vs mini-batch graph learning

Text/Image datasets têm exemplos relativamente independentes.

Grafo único gigante possui dependências compartilhadas.

Mini-batching exige:

- subgraph sampling;
- neighborhood sampling;
- cluster partitioning;
- graph batching.

Isso muda a engenharia de pipeline.

---

# 26. Memory scaling

Node states:

```math
M_V\approx |V|d_hb
```

Edge states:

```math
M_E\approx |E|d_eb
```

Attention global sobre todos os nodes:

```math
O(|V|^2)
```

é rapidamente inviável.

Graph structure permite sparse attention/message passing próximo de:

```math
O(|E|d)
```

em muitos regimes.

---

# 27. Scaling laws em grafos

GraphBFF 2026 demonstra scaling previsível com capacidade/dados em regime de graph foundation model e treina Transformer de 1.4B parâmetros em 1B samples.

O insight relevante:

> a antiga impressão de que “GNN não escala como Transformer” não pode mais ser usada como lei universal; arquitetura, batching e diversidade de pretraining mudam o regime.

---

# 28. Web graph as pretraining corpus

Acacia 2026 treina diretamente no Common Crawl web graph e demonstra:

- node classification;
- link prediction;
- clustering;
- graph generation;
- in-context behavior;
- sem depender de LLM pretraining.

Isso reforça que estrutura de grafo pode ser foundation signal por si só.

---

# 29. Graph + text multimodal

Muitos grafos têm node text:

```math
h_v=Fuse(GraphFeature_v,TextEncoder(text_v))
```

Não confundir graph foundation model com “LLM serializando edges”.

Ambos podem coexistir.

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
- feature semantic mismatch;
- projector dependence;
- graph size shift;
- degree distribution shift;
- temporal leakage;
- negative sampling bias;
- disconnected components;
- permutation/order artifacts em serialização;
- graph sparsification loss.

---

# 32. Checklist para dissecar graph FM

1. Que tipo de grafo?
2. Qual estado de node/edge?
3. Message passing ou global attention?
4. Como estrutura entra na atenção?
5. Há positional/structural encoding?
6. Qual receptive field?
7. Como evita oversmoothing/oversquashing?
8. Como mini-batching funciona?
9. Há neighborhood sampling?
10. Qual task interface?
11. Aceita feature dims arbitrárias?
12. Precisa projector/fine-tune por dataset?
13. Faz in-context graph learning?
14. Qual scaling em |V| e |E|?
15. Qual custo de graph generation?

---

# Referências snapshot

- Billion-Scale Graph Foundation Models / GraphBFF — https://arxiv.org/abs/2602.04768
- Acacia: Training Graph Foundation Models on The Web Graph — https://arxiv.org/abs/2609.30894
