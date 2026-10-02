---
title: Training, Alignment & Adaptation Datasheet — SOTA++ 2026
aliases: [Training Datasheet, Post-Training Datasheet, Alignment and Adaptation]
tags: [ai, referencia, treinamento, post-training, alignment, peft, rl, distillation, merging]
updated: 2026-10-01
---

# Training, Alignment & Adaptation Datasheet — SOTA++ 2026

> Inferência começa em $`\theta`$. Este documento explica **como $`\theta`$ chegou ali**: dados, objetivos, otimização, SFT, preference optimization, RL, PEFT, distillation, merging, pruning e continual adaptation.

A fronteira conceitual é:

```math
\boxed{
Architecture \neq Weights \neq Training \neq PostTraining \neq Inference
}
```

O mesmo backbone pode produzir comportamentos radicalmente diferentes dependendo do dataset, objective, optimizer trajectory e pós-treinamento.

Veja também:

- [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md)
- [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md)
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md)
- [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)

---

# 1. O grafo completo de treinamento

Uma visão útil é:

```text
raw data
   ↓
filter / license / quality / safety
   ↓
deduplicate / normalize / tokenize
   ↓
mixture construction / curriculum / packing
   ↓
PRETRAIN
   ↓
base model θ₀
   ↓
SFT / instruction tuning
   ↓
preference / reward / verifier training
   ↓
offline preference optimization or online RL
   ↓
distillation / PEFT / domain adaptation / merge
   ↓
checkpoint θ*
   ↓
quantization / runtime packaging
   ↓
inference
```

Não existe um único “training step”. Existem **múltiplos operadores de atualização** aplicados em fases diferentes.

---

# 2. A equação universal de atualização

Para parâmetros $`\theta`$, loss $`\mathcal L`$ e learning rate $`\eta`$:

```math
\theta_{t+1}=\theta_t-\eta_t\,\hat g_t
```

onde:

```math
\hat g_t \approx \nabla_\theta \mathcal L(\theta_t;B_t)
```

é uma estimativa do gradiente no minibatch $`B_t`$.

A loss define **o que é desejável**.

O optimizer define **como nos movemos no espaço de parâmetros**.

O dataset define **quais regiões desse espaço recebem sinal**.

Portanto:

```math
Behavior = f(Architecture,Data,Objective,Optimization,PostTraining)
```

---

# 3. Data pipeline — o primeiro controle real

## 3.1 Dataset mixture

Considere datasets $`D_i`$ e pesos $`w_i`$:

```math
P(x)=\sum_i w_iP_i(x)
```

com:

```math
\sum_i w_i=1
```

Os pesos da mistura são um **hyperparameter comportamental**.

Alterar $`w_i`$ muda a distribuição sobre a qual o modelo aprende.

---

## 3.2 Quantity ≠ diversity ≠ quality

Mais tokens não significam automaticamente mais informação útil.

Uma decomposição conceitual:

```math
EffectiveData
=f(
N_{tokens},
Diversity,
Quality,
Novelty,
Coverage,
Duplication
)
```

Duplicação excessiva reduz novidade e pode aumentar memorization.

---

## 3.3 Deduplication

Pode ocorrer em diferentes granularidades:

- documento;
- sequência;
- substring / n-gram;
- semantic embedding;
- perceptual hash para mídia.

O objetivo é reduzir:

```math
P(repeated\ evidence)
```

sem destruir repetições semanticamente legítimas.

---

## 3.4 Contamination

Se um item de avaliação $`e`$ ou uma transformação quase equivalente aparece no treino:

```math
P(e\in D_{train})>0
```

então o benchmark deixa de medir puramente generalização.

Contamination é problema de **training data governance** e de **evaluation design**.

Veja [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

---

## 3.5 Synthetic data

Pipeline típico:

```math
SeedData
\xrightarrow{Teacher}
SyntheticCandidates
\xrightarrow{Filter/Verifier}
TrainingSet
```

O ganho depende de:

```math
Q_{synthetic}
\times Diversity
\times Coverage
```

Há risco de:

- teacher bias amplification;
- error amplification;
- style collapse;
- synthetic monoculture;
- loss of tail distribution.

---

# 4. Tokenization e packing também são training parameters

Após tokenizer:

```math
x\rightarrow(t_1,\ldots,t_T)
```

Treino normalmente usa janelas de comprimento $`L`$.

Sem packing eficiente, padding desperdiça compute:

```math
Efficiency=
\frac{UsefulTokens}{TotalProcessedTokens}
```

Sequence packing concatena exemplos para aproximar:

```math
Efficiency\rightarrow1
```

mas exige cuidado com:

- attention masks;
- document boundaries;
- position reset;
- cross-example leakage.

---

# 5. Pretraining objectives

## 5.1 Causal language modeling

```math
\mathcal L_{CLM}
=-\sum_{t=1}^{T}\log p_\theta(x_t|x_{<t})
```

É o objective clássico de decoder-only AR.

---

## 5.2 Masked modeling

Para conjunto de posições $`M`$:

```math
\mathcal L_{mask}
=-\sum_{i\in M}\log p_\theta(x_i|x_{\setminus M})
```

Veja [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md).

---

## 5.3 Contrastive learning

```math
\mathcal L=
-\log
\frac{\exp(sim(q,d^+)/\tau)}
{\sum_j\exp(sim(q,d_j)/\tau)}
```

Aqui $`\tau`$ é **contrastive temperature**, não sampling temperature.

Veja [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

## 5.4 Diffusion / flow objectives

Diffusion-style:

```math
x_t=\alpha_tx_0+\sigma_t\epsilon
```

Treino pode minimizar:

```math
\mathbb E\|\epsilon-\epsilon_\theta(x_t,t,c)\|^2
```

ou parametrizações equivalentes.

Flow matching:

```math
\mathcal L_{FM}
=
\mathbb E\|v_\theta(x_t,t,c)-u_t(x_t)\|^2
```

Veja [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md).

---

# 6. Optimization mechanics

## 6.1 Effective batch

Com microbatch $`B_m`$, gradient accumulation $`G`$ e data-parallel world size $`W`$:

```math
B_{effective}=B_mGW
```

Em tokens:

```math
Tokens/update
\approx
B_{effective}\times L_{avg}
```

É frequentemente melhor comparar treino por **tokens por update** do que por “batch size” nominal.

---

## 6.2 Learning rate

```math
\eta_t
```

é um dos knobs de maior sensibilidade.

Muito baixo:

```math
|\Delta\theta|\rightarrow0
```

Muito alto:

- divergence;
- catastrophic forgetting;
- reward collapse;
- loss spikes.

---

## 6.3 Warmup

Uma forma linear:

```math
\eta_t=
\eta_{max}\frac{t}{T_w}
\qquad t<T_w
```

Reduz passos agressivos enquanto optimizer statistics e activations ainda se estabilizam.

---

## 6.4 AdamW — visão mecânica

Momentos:

```math
m_t=\beta_1m_{t-1}+(1-\beta_1)g_t
```

```math
v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2
```

Atualização simplificada:

```math
\theta_{t+1}
=
\theta_t
-
\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}
-
\eta\lambda\theta_t
```

Parâmetros fundamentais:

- learning rate $`\eta`$;
- $`\beta_1`$;
- $`\beta_2`$;
- $`\epsilon`$;
- weight decay $`\lambda`$.

---

## 6.5 Gradient clipping

Global norm:

```math
g'=
 g\cdot
\min\left(1,\frac{c}{\|g\|}\right)
```

Evita updates extremos.

Não corrige uma loss mal especificada.

---

# 7. Precision de treinamento

Estados podem viver em precisões diferentes:

```math
W_{storage},
W_{compute},
Gradients,
OptimizerStates
```

Exemplos:

- FP32;
- BF16;
- FP16;
- FP8 em pipelines suportados;
- 4-bit frozen base em QLoRA.

Mixed precision busca reduzir memória/compute mantendo estabilidade numérica.

---

# 8. Memory model do full fine-tuning

A regra ingênua:

```math
M=N_{params}\times bytes
```

é insuficiente.

Treino inclui aproximadamente:

```math
M_{train}
=
M_W+M_G+M_{opt}+M_A+M_{comm}+M_{workspace}
```

onde:

- $`M_W`$: pesos;
- $`M_G`$: gradients;
- $`M_{opt}`$: optimizer state;
- $`M_A`$: activations.

Com Adam-like optimizers, optimizer states podem superar o tamanho dos próprios pesos.

Veja [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 9. Gradient checkpointing

Sem checkpointing, muitas activations intermediárias são guardadas.

Checkpointing troca memória por recompute:

```math
Memory\downarrow
\quad\Longleftrightarrow\quad
Compute\uparrow
```

É uma alavanca de **runtime de treino**, não uma mudança na função-objetivo.

---

# 10. Distributed training

## Data parallelism

Replica modelo, divide batch.

## Tensor parallelism

Divide operações/tensores dentro de uma camada.

## Pipeline parallelism

Divide camadas em stages.

## FSDP / ZeRO-style sharding

Particiona:

- parameters;
- gradients;
- optimizer states.

A topologia de comunicação passa a ser parte importante do custo:

```math
T_{step}
=
T_{compute}+T_{communication}+T_{sync}
```

---

# 11. Supervised Fine-Tuning — SFT

Dataset:

```math
D=\{(x_i,y_i)\}
```

Loss:

```math
\mathcal L_{SFT}
=-\sum_i\sum_t
m_{i,t}
\log p_\theta(y_{i,t}|x_i,y_{i,<t})
```

onde $`m`$ define quais tokens participam da loss.

---

## 11.1 Completion-only loss

Se tokens de prompt têm máscara zero:

$$
m_t=
\begin{cases}
0 & prompt\\
1 & answer
\end{cases}
$$

Isso evita ensinar o modelo a predizer o próprio prompt quando a finalidade é instruction following.

---

## 11.2 Chat template é parte do treinamento

Mensagens são serializadas em tokens especiais.

Logo:

```math
Template_{train}
eq Template_{infer}
```

pode causar regressão relevante.

Chat template não é cosmética de frontend.

---

# 12. Instruction tuning versus knowledge injection

Fine-tuning pequeno é excelente para:

- formato;
- estilo;
- política de resposta;
- workflow;
- tarefa específica.

É menos confiável como mecanismo principal de factual knowledge injection.

Uma aproximação conceitual:

```math
SFT\rightarrow BehaviorPrior
```

mais do que:

```math
SFT\rightarrow ExactDatabase
```

Para conhecimento mutável, retrieval frequentemente é melhor.

---

# 13. Preference data

Uma amostra pairwise:

```math
(x,y_w,y_l)
```

onde:

- $`y_w`$: preferred/chosen;
- $`y_l`$: rejected.

O dado não contém apenas “qualidade”. Ele incorpora a distribuição de preferências do anotador/judge.

Veja [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 14. Reward modeling

Reward model:

```math
r_\phi(x,y)\in\mathbb R
```

Bradley–Terry:

```math
P(y_w\succ y_l)
=
\sigma(r_w-r_l)
```

Loss:

```math
\mathcal L_{RM}
=-\log\sigma(r_w-r_l)
```

O reward é uma **proxy learned objective**.

Portanto:

```math
MaxReward\neq MaxTrueUtility
```

necessariamente.

---

# 15. RLHF clássico

Pipeline simplificado:

```text
SFT policy
   ↓
collect preferences
   ↓
train reward model
   ↓
online policy optimization
   ↓
aligned policy
```

Uma objective abstrata:

```math
\max_\theta
\mathbb E_{y\sim\pi_\theta}[r_\phi(x,y)]
-
\beta D_{KL}(\pi_\theta\|\pi_{ref})
```

O termo KL limita drift.

---

# 16. PPO-style post-training

PPO usa clipped policy ratio.

```math
r_t(\theta)=
\frac{\pi_\theta(a_t|s_t)}
{\pi_{old}(a_t|s_t)}
```

Objective simplificada:

```math
L^{CLIP}
=
\mathbb E
\left[
\min(
r_tA_t,
clip(r_t,1-\epsilon,1+\epsilon)A_t
)
\right]
```

Historicamente importante, porém infraestrutura de actor/critic/reward/reference torna o pipeline complexo.

---

# 17. Direct Preference Optimization — DPO

DPO elimina o reward model explícito no loop de otimização.

Uma forma canônica:

```math
\mathcal L_{DPO}
=
-
\log\sigma
\left[
\beta
\left(
\log\frac{\pi_\theta(y_w|x)}{\pi_{ref}(y_w|x)}
-
\log\frac{\pi_\theta(y_l|x)}{\pi_{ref}(y_l|x)}
\right)
\right]
```

Knobs fundamentais:

- $`\beta`$;
- preference dataset;
- reference policy;
- sequence length;
- chosen/rejected quality.

---

# 18. KTO / ORPO / offline preference families

A ideia importante não é decorar siglas.

É perguntar:

1. usa pairwise preference?
2. exige reference model?
3. otimiza odds/log-ratio diretamente?
4. combina SFT e preference penalty?
5. é offline ou coleta novas trajectories?

ORPO, por exemplo, integra preference penalty no próprio SFT e evita reference model separado.

KTO trabalha com sinais desirable/undesirable inspirados em utility asymmetry em vez de exigir pares perfeitos.

A taxonomia é mais durável que a sigla.

---

# 19. Online RL com reward verificável

Em tarefas com checker:

$$
R(y)=
\begin{cases}
1 & verified\\
0 & fail
\end{cases}
$$

ou reward contínuo derivado do ambiente.

Exemplos naturais:

- matemática;
- código/testes;
- puzzles;
- tool tasks com state transition verificável.

Isso reduz dependência de judge subjetivo, mas somente para propriedades cobertas pelo verifier.

---

# 20. GRPO — group-relative optimization

Para um prompt, gere grupo:

```math
\{y_1,\ldots,y_G\}
```

Rewards:

```math
r_1,\ldots,r_G
```

Uma vantagem group-normalized conceitual:

```math
\hat A_i
=
\frac{r_i-\mu_G}{\sigma_G+\epsilon}
```

A vantagem relativa reduz necessidade de critic explícito.

Failure surface importante:

se:

```math
\sigma_G\approx0
```

há pouco sinal relativo no grupo.

---

# 21. DAPO — leitura como sistema, não como buzzword

DAPO surgiu como uma evolução prática de large-scale RL, combinando decisões de clipping/sampling e tratamento token-level para melhorar estabilidade/eficiência em treino de reasoning.

A lição generalizável:

```math
RL\ performance
\neq
PolicyObjective\ only
```

Ela depende de:

- sampling distribution;
- dynamic filtering;
- reward design;
- clipping;
- rollout length;
- infrastructure.

---

# 22. GSPO — sequence-level ratio

GSPO substitui razão token-level por uma razão normalizada no nível da sequência:

```math
s_i(\theta)
=
\left(
\frac{\pi_\theta(y_i|x)}
{\pi_{old}(y_i|x)}
\right)^{1/|y_i|}
```

ou:

```math
\log s_i
=
\frac1{|y_i|}
\sum_t
\log
\frac{
\pi_\theta(y_{i,t}|x,y_{i,<t})
}{
\pi_{old}(y_{i,t}|x,y_{i,<t})
}
```

Isso é especialmente relevante para MoE RL, onde token-level routing differences podem tornar importance ratios frágeis.

Snapshot 2026: GSPO permanece um exemplo importante de como **unidade estatística do update** pode ser tão importante quanto reward function.

---

# 23. On-policy versus off-policy

## On-policy

Dados vêm da policy atual:

```math
y\sim\pi_\theta
```

Pros:

- signal alinhado ao comportamento atual.

Cons:

- caro;
- rollout infrastructure;
- instabilidade.

## Off-policy / offline

Dados pré-coletados:

```math
D=\{x,y,r\}
```

Pros:

- estável;
- barato;
- reprodutível.

Cons:

- distribution mismatch.

---

# 24. Reward hacking e overoptimization

Se reward model é proxy:

```math
R_{proxy}\neq U_{true}
```

então aumentar otimização pode eventualmente produzir:

```math
R_{proxy}\uparrow
\quad
U_{true}\downarrow
```

Esse é um caso de Goodhart.

Veja [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 25. PEFT — a ideia matemática

Full fine-tuning:

```math
W\rightarrow W+\Delta W
```

com $`\Delta W`$ irrestrito.

PEFT restringe a atualização a um subespaço parametrizado menor.

---

# 26. LoRA

Para:

```math
W\in\mathbb R^{d_{out}\times d_{in}}
```

LoRA usa:

```math
\Delta W=BA
```

com:

```math
B\in\mathbb R^{d_{out}\times r}
```

```math
A\in\mathbb R^{r\times d_{in}}
```

onde:

```math
r\ll\min(d_{in},d_{out})
```

Update:

```math
W'=W+\frac{\alpha}{r}BA
```

ou scaling variante conforme implementação.

---

# 27. LoRA trainable parameter count

Aproximadamente:

```math
N_{LoRA}
=r(d_{in}+d_{out})
```

por matriz alvo.

Logo:

```math
N_{LoRA}\ll d_{in}d_{out}
```

se $`r`$ é pequeno.

---

# 28. LoRA knobs

| Parâmetro | Tag | Controle |
|---|---|---|
| `r` | `TRAIN` | capacidade do subespaço de update |
| `alpha` | `TRAIN` | scaling do update |
| target modules | `TRAIN` | quais matrizes recebem adapters |
| dropout | `TRAIN` | regularização |
| initialization | `TRAIN` | condição inicial da adaptação |
| bias training | `TRAIN` | se biases também mudam |

Não existe rank universalmente ideal.

---

# 29. Target modules

Em Transformer podem incluir:

- Q;
- K;
- V;
- O;
- gate/up/down projections;
- embeddings/output em casos específicos.

Mais módulos:

```math
Capacity\uparrow
```

mas também:

```math
TrainableParams\uparrow,
Memory\uparrow,
OverfitRisk\uparrow
```

---

# 30. QLoRA

Ideia:

```text
base weights: quantized + frozen
           ↓
forward/dequant compute
           ↓
train LoRA adapters
```

Assim:

```math
\nabla W_{base}=0
```

mas:

```math
\nabla A,\nabla B\neq0
```

QLoRA reduz drasticamente memória do frozen base, mas treino continua exigindo:

- activations;
- adapter gradients;
- optimizer state dos adapters;
- temporary dequant buffers.

Logo:

```math
FileSize_{Q4}\neq TrainingVRAM
```

---

# 31. DoRA

DoRA separa magnitude e direção do peso.

Conceitualmente:

```math
W=m\frac{V}{\|V\|}
```

A direção recebe adaptação low-rank; magnitude é aprendida separadamente.

Objetivo: aproximar mais a liberdade do full fine-tuning mantendo PEFT.

Trade-off:

- maior flexibilidade;
- overhead maior que LoRA puro.

---

# 32. LoRA initialization virou um eixo real

Implementações modernas suportam estratégias como:

- default no-op;
- Gaussian;
- PiSSA;
- EVA;
- LoftQ-oriented initialization;
- CorDA-like variants.

A escolha pode afetar:

```math
Convergence,
QuantizationError,
InitialPerturbation
```

Portanto “LoRA” não define sozinho a dinâmica.

---

# 33. Adapter composition

Adapters podem ser:

- carregados separadamente;
- ponderados;
- combinados;
- merged nos pesos.

A soma linear:

```math
\Delta W
=
\sum_i\lambda_i\Delta W_i
```

pode gerar interferência.

Não assuma composicionalidade perfeita.

---

# 34. Model merging — espaço de parâmetros

Com checkpoints $`\theta_i`$:

## Linear merge

```math
\theta_{merge}
=
\sum_i\alpha_i\theta_i
```

com pesos normalmente normalizados.

---

# 35. Task vectors

Com base $`\theta_0`$:

```math
\tau_i=\theta_i-\theta_0
```

Merge:

```math
\theta^*
=
\theta_0+
\sum_i\lambda_i\tau_i
```

Essa visão permite tratar fine-tuning como vetor de deslocamento no parameter space.

---

# 36. TIES / DARE

TIES busca reduzir interferência via:

1. sparsification;
2. sign consensus;
3. merge apenas de deltas compatíveis.

DARE usa random drop + rescaling de deltas antes de merge.

A ideia geral:

```math
Interference(\tau_i,\tau_j)
```

pode tornar média simples destrutiva.

---

# 37. SLERP e geometria de merge

SLERP interpola em uma geometria esférica entre vetores.

Para dois vetores unitários com ângulo $`\omega`$:

```math
SLERP(t)
=
\frac{\sin((1-t)\omega)}{\sin\omega}v_0
+
\frac{\sin(t\omega)}{\sin\omega}v_1
```

Útil quando linear interpolation não preserva bem magnitude/direção.

---

# 38. Compatibilidade de merge

Antes de fundir modelos, verificar:

- arquitetura;
- tensor shapes;
- tokenizer;
- vocabulary size/order;
- rope/position config;
- normalization;
- base lineage.

```math
SameParameterCount
\not\Rightarrow
CompatibleParameterSemantics
```

---

# 39. Knowledge distillation

Teacher:

```math
q_T(y|x)
```

Student:

```math
p_\theta(y|x)
```

Uma loss típica:

```math
\mathcal L
=
\lambda\mathcal L_{hard}
+
(1-\lambda)T^2
D_{KL}
(q_T^{(T)}\|p_\theta^{(T)})
```

Aqui $`T`$ é **distillation temperature**, novamente diferente de sampling temperature.

---

# 40. Sequence-level distillation

Em modelos generativos, frequentemente teacher produz trajectories:

```math
y\sim Teacher(x)
```

que viram dados para student:

```math
(x,y)\rightarrow SFT
```

Isso é behavior distillation, mesmo sem logits do teacher.

---

# 41. Reasoning distillation

Teacher gera:

```math
problem
\rightarrow
reasoning\ trace
\rightarrow
answer
```

Student aprende traces ou respostas filtradas.

Risco:

```math
TeacherError
\rightarrow
StudentTrainingSignal
```

Por isso verifier/filtering é central.

---

# 42. On-policy distillation

Student gera sua própria trajectory; teacher fornece distribuição/feedback sobre estados visitados pelo student.

Vantagem:

reduz mismatch entre:

```math
D_{teacher}
```

e:

```math
D_{student}
```

É uma tendência forte em toolkits modernos de post-training.

---

# 43. Dataset distillation

Em vez de comprimir apenas o modelo, tenta-se construir dataset compacto:

```math
D_{small}
```

tal que treino nele aproxime treino em:

```math
D_{large}
```

Esse é um eixo separado de knowledge distillation.

---

# 44. Pruning

Mask:

```math
W'=M\odot W
```

com:

```math
M_{ij}\in\{0,1\}
```

## Unstructured

Pesos individuais removidos.

## Structured

Remove:

- heads;
- neurons;
- channels;
- layers;
- experts.

Structured pruning tende a mapear melhor para hardware comum.

---

# 45. Sparsity não implica speedup

```math
Sparsity\uparrow
\not\Rightarrow
Latency\downarrow
```

se kernels/hardware não explorarem o padrão de sparsity.

Sempre distinguir:

```math
ParameterCount
```

de:

```math
ExecutedFLOPs
```

e:

```math
WallClockLatency
```

---

# 46. Continual learning

Nova distribuição $`D_{new}`$ pode melhorar tarefa nova e prejudicar antiga.

Catastrophic forgetting:

```math
Perf_{old}(\theta_{new})
<
Perf_{old}(\theta_{old})
```

Contramedidas incluem:

- replay;
- regularization;
- adapters separados;
- mixture de dados;
- lower LR;
- selective freezing.

---

# 47. Curriculum

Distribuição de dados varia com tempo:

```math
P_t(x)
```

em vez de ser constante.

Curriculum pode organizar por:

- dificuldade;
- comprimento;
- domínio;
- reward;
- confidence;
- stage.

A ordem de exposição vira parte do algoritmo.

---

# 48. Long-context training

Aumentar sequence length afeta:

- position system;
- activations;
- attention cost;
- optimizer throughput;
- packing;
- loss normalization.

Treinar em 1M tokens não é simplesmente mudar `max_seq_len`.

Tooling contemporâneo já trata explicitamente loss, positions, activation memory e single-GPU sequence memory como gargalos separados.

---

# 49. Multimodal adaptation

Para VLM:

```text
vision encoder
    ↓
projector / connector
    ↓
LLM
```

Podemos:

- congelar vision encoder;
- treinar apenas projector;
- treinar LLM + projector;
- fine-tune tudo.

Cada escolha muda:

```math
TrainableParams
```

e risco de destroying pretrained representations.

Veja [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md).

---

# 50. Diffusion/flow adaptation

LoRA também é comum em:

- attention projections;
- text encoders;
- DiT blocks.

O mesmo conceito low-rank permanece, mas a função-objetivo e os observáveis são diferentes de LLM SFT.

Veja [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md).

---

# 51. Data quality feedback loop

Um sistema maduro:

```text
train
 ↓
evaluate
 ↓
find failure clusters
 ↓
collect / generate targeted data
 ↓
filter / verify
 ↓
retrain
```

Isso é active data engineering.

O benchmark passa a orientar aquisição de dados.

Risco: overfit ao benchmark.

---

# 52. Observáveis de treinamento

Nunca acompanhar apenas loss.

## Optimization

- train loss;
- eval loss;
- gradient norm;
- parameter norm;
- learning rate;
- clipping fraction.

## Throughput

- tokens/s;
- samples/s;
- step time;
- MFU/compute utilization quando disponível.

## Memory

- allocated;
- reserved;
- peak;
- activation/offload.

## RL

- reward mean/std;
- KL;
- entropy;
- response length;
- zero-variance groups;
- clipped fraction;
- success rate.

---

# 53. Loss curve ≠ capability curve

```math
\mathcal L_{train}\downarrow
```

não garante:

```math
TaskQuality\uparrow
```

especialmente em:

- overfit;
- misaligned objective;
- contaminated eval;
- preference overoptimization.

A avaliação deve medir o comportamento desejado diretamente.

---

# 54. Training parameter coupling matrix

| ↑ variável | Efeito primário | Efeito secundário comum |
|---|---|---|
| batch/tokens update | gradiente menos ruidoso | pode exigir LR diferente |
| LR | magnitude update ↑ | instabilidade/forgetting ↑ |
| context length | informação por sample ↑ | memory/compute ↑ forte |
| LoRA rank | adaptation capacity ↑ | trainable memory ↑ |
| LoRA targets | degrees of freedom ↑ | interference/overfit ↑ |
| preference beta | constraint/strength muda | style/capability trade-off |
| RL group size | reward-relative estimate melhora | rollout cost ↑ |
| rollout length | exploration/horizon ↑ | cost/variance ↑ |
| KL penalty | policy drift ↓ | exploration/capability gain pode ↓ |
| distill temperature | soft target smoothness muda | dark-knowledge transfer muda |

Relações não são universalmente monotônicas.

---

# 55. Failure surfaces

## Optimization divergence

- NaN;
- loss explosion;
- gradient explosion.

## Catastrophic forgetting

Tarefa nova cresce; antigas caem.

## Mode/style collapse

Responses convergem para template estreito.

## Reward collapse

Reward sobe enquanto qualidade real cai.

## Data contamination

Eval deixa de ser diagnóstico válido.

## Synthetic monoculture

Diversidade diminui.

## Overfitting

```math
Train\uparrow,Eval\downarrow
```

## Merge interference

Competências individuais se anulam.

---

# 56. Local hardware reality

No seu tipo de bancada, diferencie:

### Inference feasible

de:

### Full training feasible

Uma GPU que roda Q4 de um 12B não necessariamente consegue treinar esse 12B.

Para consumer GPU, normalmente a ordem de viabilidade é:

```text
prompt tuning / small adapters
        ↓
LoRA
        ↓
QLoRA
        ↓
partial/full fine-tuning
        ↓
pretraining
```

mas cada modelo e sequence length altera a curva.

Calcule antes:

```math
M_{train}
=
weights+grads+optimizer+activations+workspace
```

---

# 57. Experimental protocol — fine-tuning

Ao comparar duas configurações:

Fixar:

- base checkpoint;
- tokenizer/template;
- dataset split;
- seed set;
- number of tokens;
- evaluation harness.

Variar apenas a hipótese de interesse.

Exemplo:

```text
H0: r=16 e r=64 não alteram qualidade de domínio de forma relevante.

control:
  base model
  dataset
  target modules
  LR
  steps
  seed set

variable:
  LoRA rank

observe:
  validation loss
  target benchmark
  forgetting benchmark
  peak VRAM
  training time
```

Veja [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

---

# 58. Provenance tags específicas deste documento

Além das tags globais:

| Tag | Significado |
|---|---|
| `DATA` | composição/transformação dos dados |
| `TRAIN` | hyperparameter de treinamento |
| `ALIGN` | preference/reward/alignment stage |
| `PEFT` | parameter-efficient adaptation |
| `DISTILL` | knowledge/dataset distillation |
| `MERGE` | parameter/model merging |

Veja [CONVENTIONS](CONVENTIONS.md).

---

# 59. Snapshot SOTA 2026

A fotografia relevante em outubro de 2026 é menos “qual algoritmo venceu” e mais uma convergência de práticas:

1. **SFT continua básico**, mas post-training moderno separa offline preference methods, online RL e reward/verifier training.
2. Tooling maduro expõe SFT, DPO, GRPO, KTO, RLOO, reward modeling e distillation como famílias distintas.
3. RL de reasoning tornou **rollout infrastructure, sampling e sequence-level statistics** tão importantes quanto a loss nominal.
4. GSPO popularizou a noção de sequence-level policy ratios como alternativa mais estável em certos regimes, especialmente MoE RL.
5. PEFT deixou de ser sinônimo apenas de vanilla LoRA: DoRA, initialization strategies, adapter mixing e quantized training formam um espaço próprio.
6. Model merging tornou-se engenharia prática com linear, SLERP, task arithmetic, TIES, DARE e variantes.
7. Distillation moderna inclui logits, sequences, reasoning trajectories e on-policy teacher/student loops.
8. Synthetic data exige curation/verifier; “gerar mais exemplos” não é uma política de dados suficiente.

---

# 60. Checklist de dissecação de qualquer checkpoint

1. Qual é o base model?
2. Qual tokenizer/template?
3. Quantos tokens de pretraining?
4. Qual mixture de dados?
5. Qual objective?
6. Houve continued pretraining?
7. Houve SFT?
8. A loss foi prompt+completion ou completion-only?
9. Houve preference training?
10. DPO/KTO/ORPO/RL/GRPO/GSPO ou equivalente?
11. Qual reward/verifier?
12. Online ou offline?
13. Houve synthetic data?
14. Houve distillation?
15. É merge?
16. Qual base lineage dos modelos merged?
17. Houve pruning?
18. Houve PEFT?
19. LoRA rank/alpha/targets?
20. Houve QLoRA/DoRA?
21. Qual sequence length de treino?
22. Qual optimizer/LR schedule?
23. Qual benchmark guiou seleção?
24. Há risco de contamination?
25. Qual checkpoint é realmente servido na inferência?

---

# 61. Resumo mecânico

```math
\boxed{
ModelBehavior
=
Architecture
\circ
Data
\circ
Objective
\circ
Optimization
\circ
PostTraining
}
```

A arquitetura define o **espaço possível**.

Os dados e objetivos definem **para onde o sistema é empurrado**.

A otimização define **a trajetória seguida**.

O post-training define **quais regiões do comportamento são reforçadas ou suprimidas**.

Inferência apenas opera o sistema resultante.

---

# Referências snapshot

- Direct Preference Optimization — https://arxiv.org/abs/2305.18290
- ORPO — https://arxiv.org/abs/2403.07691
- QLoRA — https://arxiv.org/abs/2305.14314
- DoRA — https://arxiv.org/abs/2402.09353
- DAPO repository/paper — https://github.com/BytedTsinghua-SIA/DAPO
- GSPO — https://arxiv.org/abs/2507.18071
- Hugging Face TRL docs — https://huggingface.co/docs/trl/index
- Hugging Face PEFT docs — https://huggingface.co/docs/peft/main/index
- Hugging Face PEFT LoRA — https://huggingface.co/docs/peft/main/package_reference/lora
- mergekit merge methods — https://github.com/arcee-ai/mergekit/blob/main/docs/merge_methods.md
- TIES-Merging — https://arxiv.org/abs/2306.01708
- DARE / Language Models are Super Mario — https://arxiv.org/abs/2311.03099
- Synthetic data generation/curation survey — https://arxiv.org/abs/2406.15126
- Knowledge & Dataset Distillation survey — https://arxiv.org/abs/2504.14772
