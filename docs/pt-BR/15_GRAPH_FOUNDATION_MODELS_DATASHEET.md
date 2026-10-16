---
title: Graph Foundation Models Datasheet v1.0
tags: [ai, graph, gnn, graph-transformer, foundation-models, message-passing]
updated: 2026-10-16
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

com $`d`$ como fator de ramificação efetivo em regime aproximadamente homogêneo e semelhante a árvore. Grau médio, sozinho, não limita a vizinhança de um nó: um hub pode ser muito maior. Limites exigem grau máximo ou fanouts explícitos de sampling, contabilizando nós repetidos.

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

Nesta construção, assuma grafo não dirigido com adjacência simétrica não negativa $`A`$, graus $`d_i=\sum_jA_{ij}`$ e $`D=diag(d_i)`$. A fórmula com inverso dos graus abaixo assume inicialmente $`d_i>0`$ para todo nó; grafos assinados ou dirigidos exigem construção específica adequada.

Graph Laplacian:

```math
L=D-A
```

ou normalizado:

```math
L_{sym}=I-D^{-1/2}AD^{-1/2}
```

Para incluir vértices isolados, defina $`S`$ diagonal por $`S_{ii}=d_i^{-1/2}`$ quando $`d_i>0`$ e $`S_{ii}=0`$ nos demais casos, e use:

```math
L_{sym}=S(D-A)S
```

Essa convenção produz linhas/colunas nulas nos vértices isolados, inclusive diagonal zero; coincide com a fórmula anterior nos nós de grau positivo.

Eigenvectors:

```math
Lu_i=\lambda_i u_i
```

podem fornecer coordenadas espectrais.

### Caveat

Eigenvectors possuem ambiguidades de sinal e degeneracies; arquitetura precisa tratar isso.

---

# 11. Random-walk structural encoding

Com pesos de linha não negativos $`A_{ij}`$, faça $`D`$ conter as somas das linhas (graus de saída em grafo dirigido). Se todos os graus de saída forem positivos, a matriz de transição é:

```math
P=D^{-1}A
```

Se houver graus de saída zero, normalize cada linha de grau positivo como $`P_{ij}=A_{ij}/d_i`$ e atribua a cada nó de grau zero uma linha absorvente: $`P_{ii}=1`$ e $`P_{ij}=0`$ para $`j\ne i`$. Outras políticas para dangling nodes devem ser declaradas. Cada linha passa a somar um; pesos negativos não podem ser usados diretamente como probabilidades de transição. As entradas abaixo dão probabilidades de transição após $`k`$ passos (a diagonal contém probabilidades de retorno):

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
G_{obs}=(V,E_{obs},X),\quad Y_{uv}=\mathbf 1[(u,v)\in E_{target}]
```

Aqui $`X`$ contém apenas atributos disponíveis ao preditor; $`E_{obs}`$ é seu contexto observado e $`E_{target}`$ define rótulos de predição. Modele:

```math
p_\theta(Y_{uv}=1\mid G_{obs},u,v)
```

Declare splits de arestas de treino/validação/teste e calcule embeddings a partir do contexto permitido. Oculte as arestas alvo avaliadas, inclusive cópias reversas de relações não dirigidas, do message passing e de features derivadas. Predição temporal usa somente informação disponível até o cutoff para prever arestas posteriores. Condicionar no grafo completo que já contém a aresta consultada tornaria conhecida sua pertinência.

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

Para uma serialização discreta válida e terminante $`S=(action_1,\ldots,action_T)`$, incluindo a ação stop:

```math
p(S)=\prod_{t=1}^{T}p(action_t|action_{\lt t})
```

com ações:

- add node;
- add edge;
- set attribute;
- stop.

Diferentes ordens de ações podem representar o mesmo grafo. Para um modelo com suporte em sequências válidas e terminantes, o marginal do grafo é:

```math
p(G)=\sum_{S:decode(S)=G}p(S)
```

O decoder deve fixar o que conta como o mesmo grafo (incluindo eventual equivalência por renomeação dos nós). Identificar esse marginal com a probabilidade de uma única sequência exige bijeção canônica e suporte do modelo restrito a sequências canônicas; escolher uma ordem de treino, sozinho, não estabelece essa identidade.

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

Para uma raiz, o último salto de uma árvore completa de sampling contém:

```math
N_{leaf}=\prod_{l=1}^{L}K_l
```

O total de todos os saltos, incluindo a raiz, é:

```math
N_{tree}=1+\sum_{l=1}^{L}\prod_{j=1}^{l}K_j
```

São ocorrências na árvore de sampling com todos os fanouts preenchidos. A contagem de nós distintos pode ser menor por sobreposição, amostras repetidas ou grau insuficiente; múltiplas raízes também podem compartilhar nós. Apenas o último produto é aproximação de ordem dominante somente em regimes adequados de fanout/profundidade.

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

Aqui $`b`$ é o número de bytes por escalar armazenado. Essas estimativas contam um conjunto de representações de nós/arestas; ativações por camada, gradientes, estado do otimizador, índices de adjacência e mensagens materializadas são custos separados. Attention global sobre todos os nodes possui contagem de pares:

```math
O(|V|^2)
```

é rapidamente inviável.

Para largura d e números de camadas/heads fixos, mistura de atenção esparsa ou agregação sobre arestas custa:

```math
O(|E|d)
```

Essa conta exclui projeções, tipicamente $`O(|V|d^2)`$, e funções de mensagem aprendidas; um MLP denso de largura d por aresta pode acrescentar $`O(|E|d^2)`$. Materializar todas as mensagens pode consumir memória $`O(|E|d)`$, enquanto implementações fundidas podem evitar esse tensor. Estimativas de compute e de estado armazenado são grandezas distintas.

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
