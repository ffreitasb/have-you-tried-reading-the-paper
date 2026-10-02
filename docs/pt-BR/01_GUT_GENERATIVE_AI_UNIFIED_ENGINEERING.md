---
title: GUT da IA — Unified Foundation Model Engineering Datasheet v3.1
tags: [ai, referencia, gut, matematica, arquitetura, foundation-models]
updated: 2026-10-01
---

# GUT da IA — Unified Foundation Model Engineering Datasheet v3.1

> A unidade fundamental não é “texto”, “imagem”, “áudio” ou “agente”. É **um estado numericamente representado, transformado por um operador aprendido, condicionado por informação e percorrido por um procedimento de inferência**.

Esta versão abandona definitivamente a árvore simplista “Transformer vs Diffusion” e trata foundation models como combinações de **eixos ortogonais**.

---

# 1. A ontologia-mãe

Descreva um sistema como:

```math
\boxed{
M=(R,O,B,C,I,S,D,\Omega)
}
```

| Símbolo | Eixo | Pergunta |
|---|---|---|
| $`R`$ | Representation | Em que espaço vive o estado? |
| $`O`$ | Objective | O que o treino ensina a rede a predizer/otimizar? |
| $`B`$ | Backbone | Que arquitetura parametriza a transformação? |
| $`C`$ | Conditioning | Como contexto/intenção/observação entram? |
| $`I`$ | Inference operator | Como o estado avança ou a decisão é tomada? |
| $`S`$ | Persistent state | O que persiste/cresce durante inferência? |
| $`D`$ | Decoder / decision map | Como retornamos ao domínio observável/ação? |
| $`\Omega`$ | Modality topology | Quantas modalidades entram/saem e como se alinham? |

A regra-chave:

```math
\boxed{B\perp O\perp R}
```

Um Transformer pode ser autoregressivo, masked, diffusion-like, embedding encoder, reranker, reward model, graph processor ou policy backbone.

## 1.1 O modelo não é o lifecycle inteiro

A tupla $`M`$ descreve principalmente **o sistema aprendido e sua execução**. Ela não descreve sozinha como os pesos foram produzidos, como evidência foi medida ou como risco operacional é controlado.

Para isso, envolvemos $`M`$ em um lifecycle envelope:

```math
\boxed{
\Gamma=(\mathcal D,\mathcal T,\mathcal A,\mathcal E,\mathcal S)
}
```

| Símbolo | Eixo de lifecycle | Pergunta |
|---|---|---|
| $`\mathcal D`$ | Data | que distribuição alimentou treino/adaptação? |
| $`\mathcal T`$ | Training | que losses/optimizers produziram $`\theta`$? |
| $`\mathcal A`$ | Alignment/Adaptation | SFT, preference, RL, PEFT, distillation, merge? |
| $`\mathcal E`$ | Evaluation | que protocolo sustenta as alegações de performance? |
| $`\mathcal S`$ | Security/Robustness | quais trust boundaries e failure surfaces limitam deployment? |

Assim, a unidade completa da coleção passa a ser:

```math
\boxed{System=(M,\Gamma,Runtime)}
```

Veja [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md), [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md), [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md) e [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 2. Representation space — a variável que mais muda a física

## 2.1 Sequência discreta

```math
x=(x_1,\ldots,x_T),\quad x_t\in\{1,\ldots,V\}
```

Exemplos:

- texto;
- código;
- codec tokens de áudio;
- ações discretizadas.

---

## 2.2 Latente contínuo

```math
Z\in\mathbb R^{N\times d}
```

ou, para imagem:

```math
Z\in\mathbb R^{B\times C\times H_l\times W_l}
```

Exemplos:

- VAE latents;
- audio latents;
- structured 3D latents;
- continuous speech representations.

---

## 2.3 Grade espacial / espaço-temporal

Imagem:

```math
X\in\mathbb R^{H\times W\times C}
```

Vídeo:

```math
X\in\mathbb R^{T\times H\times W\times C}
```

A dimensionalidade do estado muda brutalmente o custo de attention.

---

## 2.4 Série temporal numérica

```math
X\in\mathbb R^{T\times D}
```

Tempo possui ordem física; não é apenas posição textual.

---

## 2.5 Tabela estruturada

```math
X\in\mathbb R^{N\times D}
```

A ordem das colunas/linhas não possui necessariamente a semântica de uma sentença. Missingness, tipos heterogêneos e small-data priors tornam o problema estruturalmente diferente.

---

## 2.6 Grafo

```math
G=(V,E,X_V,X_E)
```

Não há ordem sequencial natural. A estrutura relacional é parte do próprio dado.

---

## 2.7 Estado físico/embodied

```math
s_t=(vision_t,proprioception_t,language_t,world\ state_t)
```

Saída pode ser ação contínua:

```math
a_t\in\mathbb R^m
```

---

# 3. Funções-objetivo

## 3.1 Autoregression

```math
p(x_{1:T})=\prod_{t=1}^{T}p(x_t|x_{<t},C)
```

Treino: next-element prediction.  
Inferência: um passo condiciona o próximo.

---

## 3.2 Masked prediction / denoising discreto

Escolha um conjunto mascarado $`M`$:

```math
\mathcal L=-\sum_{i\in M}\log p(x_i|x_{\setminus M})
```

Pode suportar preenchimento paralelo e refinamento iterativo.

---

## 3.3 Diffusion / score-based

Forward simplificado:

```math
x_t=\alpha_tx_0+\sigma_t\epsilon
```

A rede aprende ruído, score, clean sample ou parametrização equivalente.

---

## 3.4 Flow matching / rectified flow

```math
\frac{dx_t}{dt}=v_\theta(x_t,t,C)
```

Inferência aproxima/integraliza o campo vetorial aprendido.

---

## 3.5 Contrastive representation learning

Para query positiva $`d^+`$ e negativos $`d_j`$:

```math
\mathcal L=
-\log
\frac{e^{sim(q,d^+)/\tau}}
{\sum_j e^{sim(q,d_j)/\tau}}
```

Objetivo não é gerar: é **organizar geometria**.

---

## 3.6 Ranking / preference / reward modeling

Pairwise:

```math
P(A>B)=\sigma(r_A-r_B)
```

```math
\mathcal L=-\log\sigma(r_{chosen}-r_{rejected})
```

O modelo aprende um operador de avaliação, não necessariamente de geração.

---

## 3.7 Transition dynamics / world modeling

```math
p(s_{t+1}|s_t,a_t)
```

ou determinístico/latent:

```math
\hat s_{t+1}=f_\theta(s_t,a_t)
```

Aprender o “plant” muda radicalmente a topologia de decisão.

---

# 4. Backbones

A função $`f_\theta`$ pode ser parametrizada por:

- Transformer;
- DiT / MMDiT;
- U-Net;
- Conformer;
- SSM/híbridos;
- GNN/message passing;
- Graph Transformer;
- CNN/ConvNet;
- mixtures híbridas.

Não inferir objetivo apenas pela arquitetura.

---

# 5. Conditioning — o verdadeiro “prompt universal”

```math
C=\{C_{text},C_{image},C_{audio},C_{video},C_{retrieved},C_{state},C_{graph},C_{tool},\ldots\}
```

Mecanismos:

- prefix/context tokens;
- cross-attention;
- joint attention;
- feature projection;
- AdaLN/modulation;
- concatenation;
- reference embeddings;
- retrieved evidence;
- structural biases;
- action/state injection.

### Negative prompt

Não é universal. Em CFG clássico:

```math
f_g=f_u+s(f_c-f_u)
```

onde “unconditional” pode ser vazio, negativo ou outro conditioning de referência.

---

# 6. Modality topology $`\Omega`$

## 6.1 Unimodal

```math
Text\rightarrow Text
```

ou:

```math
Image\rightarrow Image
```

## 6.2 Multimodal input

```math
Text+Image\rightarrow Text
```

## 6.3 Multimodal output

```math
Text\rightarrow Text+Audio/Image
```

## 6.4 Omni

```math
\{Text,Image,Audio,Video\}_{in}
\rightarrow
\{Text,Audio,\ldots\}_{out}
```

A principal dificuldade deixa de ser apenas “capacidade do LLM” e passa a incluir:

```math
Alignment(Modality_i,Modality_j)
```

em espaço, tempo e semântica.

Veja [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md).

---

# 7. Operadores de inferência

## 7.1 Categorical decode

```math
z\rightarrow p(x)\rightarrow sample/argmax
```

## 7.2 Constrained decode

```math
V_t\rightarrow V_t^{valid}
```

## 7.3 ODE/SDE-style integration

```math
x_{k+1}=\Phi(x_k,f_\theta(x_k,t_k),\Delta t_k)
```

## 7.4 Retrieval

```math
q\rightarrow z_q\rightarrow ANN(z_q)\rightarrow TopK
```

## 7.5 Ranking

```math
(q,d_i)\rightarrow score_i\rightarrow sort
```

## 7.6 Message passing

```math
h_v^{l+1}=\phi\left(h_v^l,\bigoplus_{u\in\mathcal N(v)}\psi(h_v^l,h_u^l,e_{uv})\right)
```

## 7.7 Policy rollout

```math
a_t\sim\pi_\theta(a|s_t)
```

## 7.8 Planning with learned dynamics

```math
\hat s_{t+1}=f_\theta(\hat s_t,a_t)
```

```math
a^*_{1:H}=\arg\max\sum_{t=1}^{H}R(\hat s_t,a_t)
```

---

# 8. Persistent state

| Família | Estado que cresce/persiste |
|---|---|
| LLM causal | KV cache |
| iterative text | sequência/bloco inteiro sendo refinado |
| diffusion/flow | latent trajectory/current latent |
| video | spatiotemporal latent/window |
| speech streaming | acoustic cache / decoder state |
| retrieval | ANN index externo + query state |
| graph | node/edge representations |
| agent | conversation/tool/environment history |
| world model | latent state + rollout trajectory |

**Estado persistente é a ponte entre matemática e custo físico.**

---

# 9. Temperature: quatro significados diferentes

A palavra “temperature” aparece em contextos distintos.

### Sampling temperature

```math
p_i(T)=\frac{e^{z_i/T}}{\sum_je^{z_j/T}}
```

### Contrastive temperature

```math
\exp(sim/\tau)
```

Controla concentração da loss no treinamento de embeddings.

### Policy entropy temperature

Pode ponderar exploração/regularização em RL.

### Distillation/calibration temperature

Pode suavizar logits para teacher/student ou calibration.

> Mesmo nome ≠ mesma variável física.

---

# 10. Temperature ≠ CFG ≠ retrieval threshold

Esses knobs podem parecer todos “controle de liberdade”, mas operam em espaços diferentes:

- temperature: distribuição categórica;
- CFG: combinação/extrapolação de predições contínuas;
- similarity threshold: região aceita no espaço vetorial;
- reward threshold: regra decisória sobre score.

Nunca use analogia comportamental como equivalência matemática.

---

# 11. Seed: estado inicial, não contrato de determinismo

```math
Reproducibility=
F(W,input,seed,dtype,kernel,backend,hardware,parallelism,version)
```

Logo:

```math
seed\ fixa\not\Rightarrow bitwise\ determinism
```

---

# 12. Model capacity ≠ search/inference budget

Separar:

```math
Capacity=f(N_{params},architecture,training,data)
```

from:

```math
InferenceBudget=f(tokens,steps,rollouts,K,retrieval\ depth,verifier\ calls)
```

Exemplos:

- mais reasoning tokens não aumenta parâmetros;
- mais diffusion steps não aumenta capacidade;
- maior `TopK` de retrieval não melhora necessariamente evidência;
- maior rollout horizon pode acumular model error.

---

# 13. O ciclo operacional completo

Com os novos domínios, podemos expressar a cadeia moderna como:

```math
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
\rightarrow
PERCEIVE
}
```

### Perceive

[10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md), [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md)

### Represent / Retrieve

[11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md)

### Reason / Generate

[02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md), [05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET](05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md)

### Evaluate

[12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)

### Act

[08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md), [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md)

### Predict structured worlds

[14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md), [15_GRAPH_FOUNDATION_MODELS_DATASHEET](15_GRAPH_FOUNDATION_MODELS_DATASHEET.md)

---

# 14. Taxonomia de controles

| Classe | Exemplo | Operação |
|---|---|---|
| Conditioning | prompt, image, retrieved context | altera $`C`$ |
| Distribution shaping | temperature, penalties | altera logits/probabilidades |
| Support restriction | top-k, min-p, grammar | restringe domínio candidato |
| Guidance | CFG, STG | combina predições |
| Trajectory discretization | sigmas/timesteps | define pontos da trajetória |
| Solver | Euler/Heun/DPM | integra trajetória |
| Retrieval scope | K, efSearch, nprobe | controla busca aproximada |
| Decision threshold | reward/similarity cutoff | transforma score em decisão |
| Rollout budget | horizon, candidates | amplia busca/planejamento |
| State budget | context, frames, nodes | aumenta estado persistente |
| Quantization | Q4/Q8/FP8 | reduz precisão/bytes |
| Runtime mapping | offload, batching | distribui compute e memória |

---

# 15. Observabilidade

Uma ficha SOTA++ precisa separar **controls** de **observables**.

## LLM

```math
logits,\ entropy,\ support\ size,\ KV,\ promptTPS,\ decodeTPS
```

## Retrieval

```math
Recall@K,\ Precision@K,\ MRR,\ nDCG,\ ANN\ latency
```

## Reward/Judge

```math
agreement,\ calibration,\ ECE,\ win\ rate,\ rank\ correlation
```

## Speech

```math
WER,\ CER,\ RTF,\ TTFT,\ timestamp\ error
```

## Time series

```math
MAE,\ RMSE,\ CRPS,\ coverage,\ calibration
```

## Graph

```math
node/edge/graph\ metrics,\ neighborhood\ fanout,\ memory/node
```

## World/VLA

```math
success\ rate,\ return,\ horizon,\ model\ error,\ action\ latency
```

---

# 16. Failure surfaces universais

## 16.1 Distribution collapse

A distribuição fica excessivamente concentrada.

## 16.2 Support pollution

O suporte inclui opções semanticamente ruins.

## 16.3 Representation bottleneck

O encoder/projector perde informação antes do backbone principal.

## 16.4 Alignment failure

Modalidades ou etapas não compartilham referência temporal/espacial/semântica adequada.

## 16.5 Search error

A resposta correta existe, mas retrieval/planning/beam não a alcança.

## 16.6 Model error

O estado correto sequer recebe score adequado.

## 16.7 Calibration error

Score alto não corresponde à probabilidade real de estar correto.

## 16.8 Runtime distortion

Quantização, contexto estendido ou backend alteram comportamento além do esperado.

---

# 17. Snapshot 2026 — por que essa ontologia é necessária

Em 2026 coexistem, no mesmo ecossistema:

- omni models que alinham texto/visão/áudio/vídeo;
- multimodal embeddings e rerankers;
- diffusion language models que geram múltiplos tokens em paralelo;
- reward/verifier models que julgam processos e resultados;
- world-model VLAs que geram futuro visual e ações;
- time-series FMs com multi-task masking;
- tabular FMs com in-context supervised inference;
- graph foundation models em escala bilionária.

Nenhum desses fenômenos cabe corretamente na dicotomia “LLM vs diffusion”.

---

# 17.1 O ciclo de evidência e manutenção

A coleção inteira pode ser vista como um feedback loop:

```text
data → train/adapt → model → infer/system → evaluate → failure analysis
  ↑                                                        ↓
  └──────────────────── targeted data / controls ─────────┘
```

Formalmente:

```math
\theta_{k+1}
=
Update(
\theta_k,
Evidence_k,
Failures_k,
Data_k
)
```

Isso explica por que treinamento, avaliação e segurança são **camadas horizontais**, não novos tipos de backbone.

Terminologia canônica: [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

Regras de manutenção: [CONVENTIONS](CONVENTIONS.md).

# 18. Regra final

Quando surgir um “novo tipo” de modelo, não pergunte primeiro o nome comercial.

Pergunte:

1. Qual é $`R`$?
2. Qual é $`O`$?
3. Qual é $`B`$?
4. Como entra $`C`$?
5. Qual é $`I`$?
6. Qual estado $`S`$ persiste?
7. Como sai por $`D`$?
8. Qual é a topologia modal $`\Omega`$?

Se você responde isso, quase sempre o “novo paradigma” deixa de ser magia e volta a ser engenharia.

---

# Referências snapshot 2026

- Qwen3.5-Omni Technical Report — https://arxiv.org/abs/2604.15804
- Qwen3-VL-Embedding / Reranker — https://arxiv.org/abs/2601.04720
- Mercury diffusion language models — https://arxiv.org/abs/2506.17298
- WorldFly world-model VLA — https://arxiv.org/abs/2606.06147
- TabPFN-2.5 — https://arxiv.org/abs/2511.08667
- Zeus Time-Series Foundation Model — https://proceedings.mlr.press/v306/fu26n.html
- Billion-Scale Graph Foundation Models — https://arxiv.org/abs/2602.04768
- Acacia / Web Graph foundation model — https://arxiv.org/abs/2609.30894
