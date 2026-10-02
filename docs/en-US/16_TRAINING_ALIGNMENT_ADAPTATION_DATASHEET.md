---
title: Training, Alignment & Adaptation Datasheet — SOTA++ 2026
aliases: [Training Datasheet, Post-Training Datasheet, Alignment and Adaptation]
tags: [ai, reference, training, post-training, alignment, peft, rl, distillation, merging]
updated: 2026-10-01
---

# Training, Alignment & Adaptation Datasheet — SOTA++ 2026

> Inference starts at $`\theta`$. This document explains **how $`\theta`$ got there**: data, objectives, optimization, SFT, preference optimization, RL, PEFT, distillation, merging, pruning, and continual adaptation.

The conceptual boundary is:

```math
\boxed{
Architecture \neq Weights \neq Training \neq PostTraining \neq Inference
}
```

The same backbone can produce radically different behavior depending on the dataset, objective, optimizer trajectory, and post-training.

See also:

- [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md)
- [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md)
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md)
- [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)

---

# 1. The complete training graph

A useful high-level view is:

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

There is no single “training step.” There are **multiple update operators** applied at different stages.

---

# 2. The universal update equation

For parameters $`\theta`$, loss $`\mathcal L`$, and learning rate $`\eta`$:

```math
\theta_{t+1}=\theta_t-\eta_t\,\hat g_t
```

where:

```math
\hat g_t \approx \nabla_\theta \mathcal L(\theta_t;B_t)
```

is an estimate of the gradient over minibatch $`B_t`$.

The loss defines **what is desirable**.

The optimizer defines **how we move through parameter space**.

The dataset defines **which regions of that space receive learning signal**.

Therefore:

```math
Behavior = f(Architecture,Data,Objective,Optimization,PostTraining)
```

---

# 3. Data pipeline — the first real control surface

## 3.1 Dataset mixture

Consider datasets $`D_i`$ with mixture weights $`w_i`$:

```math
P(x)=\sum_i w_iP_i(x)
```

with:

```math
\sum_i w_i=1
```

Mixture weights are a **behavioral hyperparameter**.

Changing $`w_i`$ changes the distribution the model learns from.

---

## 3.2 Quantity ≠ diversity ≠ quality

More tokens do not automatically mean more useful information.

A conceptual decomposition is:

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

Excessive duplication reduces novelty and may increase memorization.

---

## 3.3 Deduplication

Deduplication can happen at different granularities:

- document;
- sequence;
- substring / n-gram;
- semantic embedding;
- perceptual hash for media.

The goal is to reduce:

```math
P(repeated\ evidence)
```

without destroying semantically legitimate repetition.

---

## 3.4 Contamination

If an evaluation item $`e`$, or a near-equivalent transformation of it, appears in training:

```math
P(e\in D_{train})>0
```

then the benchmark no longer measures pure generalization.

Contamination is both a **training-data governance** problem and an **evaluation-design** problem.

See [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

---

## 3.5 Synthetic data

Typical pipeline:

```math
SeedData
\xrightarrow{Teacher}
SyntheticCandidates
\xrightarrow{Filter/Verifier}
TrainingSet
```

The gain depends on:

```math
Q_{synthetic}
\times Diversity
\times Coverage
```

Risks include:

- teacher-bias amplification;
- error amplification;
- style collapse;
- synthetic monoculture;
- loss of the tail distribution.

---

# 4. Tokenization and packing are training parameters too

After tokenization:

```math
x\rightarrow(t_1,\ldots,t_T)
```

Training typically uses windows of length $`L`$.

Without efficient packing, padding wastes compute:

```math
Efficiency=
\frac{UsefulTokens}{TotalProcessedTokens}
```

Sequence packing concatenates examples to drive:

```math
Efficiency\rightarrow1
```

but requires care around:

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

This is the classic objective for decoder-only autoregressive models.

---

## 5.2 Masked modeling

For a set of masked positions $`M`$:

```math
\mathcal L_{mask}
=-\sum_{i\in M}\log p_\theta(x_i|x_{\setminus M})
```

See [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md).

---

## 5.3 Contrastive learning

```math
\mathcal L=
-\log
\frac{\exp(sim(q,d^+)/\tau)}
{\sum_j\exp(sim(q,d_j)/\tau)}
```

Here $`\tau`$ is **contrastive temperature**, not sampling temperature.

See [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

## 5.4 Diffusion / flow objectives

Diffusion-style:

```math
x_t=\alpha_tx_0+\sigma_t\epsilon
```

Training may minimize:

```math
\mathbb E\|\epsilon-\epsilon_\theta(x_t,t,c)\|^2
```

or an equivalent parameterization.

Flow matching:

```math
\mathcal L_{FM}
=
\mathbb E\|v_\theta(x_t,t,c)-u_t(x_t)\|^2
```

See [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md).

---

# 6. Optimization mechanics

## 6.1 Effective batch

With microbatch $`B_m`$, gradient accumulation $`G`$, and data-parallel world size $`W`$:

```math
B_{effective}=B_mGW
```

In tokens:

```math
Tokens/update
\approx
B_{effective}\times L_{avg}
```

It is often more meaningful to compare training runs by **tokens per update** than by nominal “batch size.”

---

## 6.2 Learning rate

```math
\eta_t
```

is one of the most sensitive knobs in the system.

Too low:

```math
|\Delta\theta|\rightarrow0
```

Too high can produce:

- divergence;
- catastrophic forgetting;
- reward collapse;
- loss spikes.

---

## 6.3 Warmup

One linear form is:

```math
\eta_t=
\eta_{max}\frac{t}{T_w}
\qquad t<T_w
```

Warmup reduces aggressive updates while optimizer statistics and activations are still stabilizing.

---

## 6.4 AdamW — mechanical view

Moments:

```math
m_t=\beta_1m_{t-1}+(1-\beta_1)g_t
```

```math
v_t=\beta_2v_{t-1}+(1-\beta_2)g_t^2
```

Simplified update:

```math
\theta_{t+1}
=
\theta_t
-
\eta\frac{\hat m_t}{\sqrt{\hat v_t}+\epsilon}
-
\eta\lambda\theta_t
```

Fundamental parameters:

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

This limits extreme updates.

It does not fix a badly specified loss.

---

# 7. Training precision

Different states may live at different precisions:

```math
W_{storage},
W_{compute},
Gradients,
OptimizerStates
```

Examples:

- FP32;
- BF16;
- FP16;
- FP8 in supported pipelines;
- a frozen 4-bit base in QLoRA.

Mixed precision aims to reduce memory/compute while preserving numerical stability.

---

# 8. Full fine-tuning memory model

The naive rule:

```math
M=N_{params}\times bytes
```

is not enough.

Training requires approximately:

```math
M_{train}
=
M_W+M_G+M_{opt}+M_A+M_{comm}+M_{workspace}
```

where:

- $`M_W`$: weights;
- $`M_G`$: gradients;
- $`M_{opt}`$: optimizer state;
- $`M_A`$: activations.

With Adam-like optimizers, optimizer states may exceed the size of the weights themselves.

See [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 9. Gradient checkpointing

Without checkpointing, many intermediate activations are retained.

Checkpointing trades memory for recomputation:

```math
Memory\downarrow
\quad\Longleftrightarrow\quad
Compute\uparrow
```

This is a **training-runtime** lever, not a change in the objective function.

---

# 10. Distributed training

## Data parallelism

Replicate the model, split the batch.

## Tensor parallelism

Split operations/tensors within a layer.

## Pipeline parallelism

Split layers across stages.

## FSDP / ZeRO-style sharding

Shard:

- parameters;
- gradients;
- optimizer states.

Communication topology becomes a major part of the cost:

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

where $`m`$ determines which tokens contribute to the loss.

---

## 11.1 Completion-only loss

If prompt tokens receive a zero mask:

$$
m_t=
\begin{cases}
0 & prompt\\
1 & answer
\end{cases}
$$

this avoids training the model to predict the prompt itself when the objective is instruction following.

---

## 11.2 Chat template is part of training

Messages are serialized into special tokens.

Therefore:

```math
Template_{train}
eq Template_{infer}
```

can cause meaningful regression.

The chat template is not frontend cosmetics.

---

# 12. Instruction tuning versus knowledge injection

Small-scale fine-tuning is excellent for:

- format;
- style;
- response policy;
- workflow;
- specific tasks.

It is less reliable as the primary mechanism for factual knowledge injection.

A useful conceptual approximation is:

```math
SFT\rightarrow BehaviorPrior
```

more than:

```math
SFT\rightarrow ExactDatabase
```

For mutable knowledge, retrieval is often the better mechanism.

---

# 13. Preference data

A pairwise sample is:

```math
(x,y_w,y_l)
```

where:

- $`y_w`$: preferred/chosen;
- $`y_l`$: rejected.

The data does not encode only “quality.” It also encodes the preference distribution of the annotator/judge.

See [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

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

The reward is a **learned proxy objective**.

Therefore:

```math
MaxReward\neq MaxTrueUtility
```

necessarily.

---

# 15. Classical RLHF

Simplified pipeline:

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

An abstract objective:

```math
\max_\theta
\mathbb E_{y\sim\pi_\theta}[r_\phi(x,y)]
-
\beta D_{KL}(\pi_\theta\|\pi_{ref})
```

The KL term limits policy drift.

---

# 16. PPO-style post-training

PPO uses a clipped policy ratio.

```math
r_t(\theta)=
\frac{\pi_\theta(a_t|s_t)}
{\pi_{old}(a_t|s_t)}
```

Simplified objective:

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

Historically important, although the actor/critic/reward/reference infrastructure makes the pipeline complex.

---

# 17. Direct Preference Optimization — DPO

DPO removes the explicit reward model from the optimization loop.

A canonical form is:

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

Fundamental knobs:

- $`\beta`$;
- preference dataset;
- reference policy;
- sequence length;
- chosen/rejected quality.

---
# 18. KTO / ORPO / offline preference families

The important thing is not memorizing acronyms.

Ask instead:

1. does it use pairwise preferences?
2. does it require a reference model?
3. does it directly optimize odds/log-ratios?
4. does it combine SFT with a preference penalty?
5. is it offline, or does it collect fresh trajectories?

ORPO, for example, integrates a preference penalty directly into SFT and avoids a separate reference model.

KTO works with desirable/undesirable signals inspired by utility asymmetry instead of requiring perfectly paired examples.

The taxonomy will outlive the acronym.

---

# 19. Online RL with verifiable reward

For tasks with a checker:

$$
R(y)=
\begin{cases}
1 & verified\\
0 & fail
\end{cases}
$$

or a continuous reward derived from the environment.

Natural examples include:

- mathematics;
- code/tests;
- puzzles;
- tool tasks with verifiable state transitions.

This reduces dependence on a subjective judge, but only for properties covered by the verifier.

---

# 20. GRPO — group-relative optimization

For a prompt, generate a group:

```math
\{y_1,\ldots,y_G\}
```

Rewards:

```math
r_1,\ldots,r_G
```

A conceptual group-normalized advantage is:

```math
\hat A_i
=
\frac{r_i-\mu_G}{\sigma_G+\epsilon}
```

The relative advantage reduces the need for an explicit critic.

Important failure surface:

if:

```math
\sigma_G\approx0
```

there is very little relative signal inside the group.

---

# 21. DAPO — read it as a system, not a buzzword

DAPO emerged as a practical evolution of large-scale RL, combining decisions around clipping, sampling, and token-level treatment to improve stability and efficiency in reasoning training.

The generalizable lesson is:

```math
RL\ performance
\neq
PolicyObjective\ only
```

It depends on:

- sampling distribution;
- dynamic filtering;
- reward design;
- clipping;
- rollout length;
- infrastructure.

---

# 22. GSPO — sequence-level ratio

GSPO replaces a token-level ratio with a sequence-normalized ratio:

```math
s_i(\theta)
=
\left(
\frac{\pi_\theta(y_i|x)}
{\pi_{old}(y_i|x)}
\right)^{1/|y_i|}
```

or:

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

This is especially relevant to MoE RL, where token-level routing differences can make importance ratios fragile.

2026 snapshot: GSPO remains an important example of how the **statistical unit of the update** can matter as much as the reward function.

---

# 23. On-policy versus off-policy

## On-policy

Data comes from the current policy:

```math
y\sim\pi_\theta
```

Pros:

- signal aligned with current behavior.

Cons:

- expensive;
- requires rollout infrastructure;
- unstable.

## Off-policy / offline

Use pre-collected data:

```math
D=\{x,y,r\}
```

Pros:

- stable;
- cheap;
- reproducible.

Cons:

- distribution mismatch.

---

# 24. Reward hacking and overoptimization

If the reward model is a proxy:

```math
R_{proxy}\neq U_{true}
```

then stronger optimization can eventually produce:

```math
R_{proxy}\uparrow
\quad
U_{true}\downarrow
```

This is a case of Goodhart's law.

See [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 25. PEFT — the mathematical idea

Full fine-tuning:

```math
W\rightarrow W+\Delta W
```

with unrestricted $`\Delta W`$.

PEFT constrains the update to a smaller parameterized subspace.

---

# 26. LoRA

For:

```math
W\in\mathbb R^{d_{out}\times d_{in}}
```

LoRA uses:

```math
\Delta W=BA
```

with:

```math
B\in\mathbb R^{d_{out}\times r}
```

```math
A\in\mathbb R^{r\times d_{in}}
```

where:

```math
r\ll\min(d_{in},d_{out})
```

Update:

```math
W'=W+\frac{\alpha}{r}BA
```

or a variant scaling rule, depending on the implementation.

---

# 27. LoRA trainable parameter count

Approximately:

```math
N_{LoRA}
=r(d_{in}+d_{out})
```

per target matrix.

Therefore:

```math
N_{LoRA}\ll d_{in}d_{out}
```

when $`r`$ is small.

---

# 28. LoRA knobs

| Parameter | Tag | Controls |
|---|---|---|
| `r` | `TRAIN` | capacity of the update subspace |
| `alpha` | `TRAIN` | update scaling |
| target modules | `TRAIN` | which matrices receive adapters |
| dropout | `TRAIN` | regularization |
| initialization | `TRAIN` | initial condition of the adaptation |
| bias training | `TRAIN` | whether biases are updated as well |

There is no universally optimal rank.

---

# 29. Target modules

In a Transformer these may include:

- Q;
- K;
- V;
- O;
- gate/up/down projections;
- embeddings/output in specific cases.

More modules:

```math
Capacity\uparrow
```

but also:

```math
TrainableParams\uparrow,
Memory\uparrow,
OverfitRisk\uparrow
```

---

# 30. QLoRA

The idea:

```text
base weights: quantized + frozen
           ↓
forward/dequant compute
           ↓
train LoRA adapters
```

Thus:

```math
\nabla W_{base}=0
```

but:

```math
\nabla A,\nabla B\neq0
```

QLoRA dramatically reduces the memory footprint of the frozen base, but training still requires:

- activations;
- adapter gradients;
- optimizer state for the adapters;
- temporary dequantization buffers.

Therefore:

```math
FileSize_{Q4}\neq TrainingVRAM
```

---

# 31. DoRA

DoRA separates weight magnitude from direction.

Conceptually:

```math
W=m\frac{V}{\|V\|}
```

The direction receives a low-rank adaptation; magnitude is learned separately.

Goal: approach more of the flexibility of full fine-tuning while retaining PEFT.

Trade-off:

- greater flexibility;
- more overhead than plain LoRA.

---

# 32. LoRA initialization is now a real axis

Modern implementations support strategies such as:

- default no-op;
- Gaussian;
- PiSSA;
- EVA;
- LoftQ-oriented initialization;
- CorDA-like variants.

The choice can affect:

```math
Convergence,
QuantizationError,
InitialPerturbation
```

So “LoRA” alone does not fully specify the adaptation dynamics.

---

# 33. Adapter composition

Adapters can be:

- loaded separately;
- weighted;
- combined;
- merged into the weights.

A linear combination:

```math
\Delta W
=
\sum_i\lambda_i\Delta W_i
```

can produce interference.

Do not assume perfect compositionality.

---

# 34. Model merging — parameter space

Given checkpoints $`\theta_i`$:

## Linear merge

```math
\theta_{merge}
=
\sum_i\alpha_i\theta_i
```

with weights typically normalized.

---

# 35. Task vectors

Given base $`\theta_0`$:

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

This view treats fine-tuning as a displacement vector in parameter space.

---

# 36. TIES / DARE

TIES seeks to reduce interference through:

1. sparsification;
2. sign consensus;
3. merging only compatible deltas.

DARE applies random dropping plus rescaling to deltas before merging.

The general idea is that:

```math
Interference(\tau_i,\tau_j)
```

can make a simple average destructive.

---

# 37. SLERP and merge geometry

SLERP interpolates along spherical geometry between vectors.

For two unit vectors separated by angle $`\omega`$:

```math
SLERP(t)
=
\frac{\sin((1-t)\omega)}{\sin\omega}v_0
+
\frac{\sin(t\omega)}{\sin\omega}v_1
```

Useful when linear interpolation does not preserve magnitude/direction well.

---

# 38. Merge compatibility

Before merging models, verify:

- architecture;
- tensor shapes;
- tokenizer;
- vocabulary size/order;
- RoPE/position configuration;
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

A typical loss:

```math
\mathcal L
=
\lambda\mathcal L_{hard}
+
(1-\lambda)T^2
D_{KL}
(q_T^{(T)}\|p_\theta^{(T)})
```

Here $`T`$ is **distillation temperature**, again distinct from sampling temperature.

---

# 40. Sequence-level distillation

For generative models, the teacher often produces trajectories:

```math
y\sim Teacher(x)
```

which become training data for the student:

```math
(x,y)\rightarrow SFT
```

This is behavior distillation even when the teacher's logits are unavailable.

---

# 41. Reasoning distillation

The teacher generates:

```math
problem
\rightarrow
reasoning\ trace
\rightarrow
answer
```

The student learns from traces or filtered answers.

Risk:

```math
TeacherError
\rightarrow
StudentTrainingSignal
```

This is why verifier/filtering quality is central.

---

# 42. On-policy distillation

The student generates its own trajectory; the teacher supplies a distribution or feedback over states visited by the student.

Advantage:

it reduces mismatch between:

```math
D_{teacher}
```

and:

```math
D_{student}
```

This is a strong trend in modern post-training toolkits.

---

# 43. Dataset distillation

Instead of compressing only the model, dataset distillation tries to construct a compact dataset:

```math
D_{small}
```

such that training on it approximates training on:

```math
D_{large}
```

This is a separate axis from knowledge distillation.

---

# 44. Pruning

Mask:

```math
W'=M\odot W
```

with:

```math
M_{ij}\in\{0,1\}
```

## Unstructured

Individual weights are removed.

## Structured

Remove structures such as:

- heads;
- neurons;
- channels;
- layers;
- experts.

Structured pruning tends to map better onto conventional hardware.

---

# 45. Sparsity does not imply speedup

```math
Sparsity\uparrow
\not\Rightarrow
Latency\downarrow
```

if the kernels/hardware cannot exploit the sparsity pattern.

Always distinguish:

```math
ParameterCount
```

from:

```math
ExecutedFLOPs
```

and:

```math
WallClockLatency
```

---
# 46. Continual learning

A new distribution $`D_{new}`$ may improve the new task while degrading old ones.

Catastrophic forgetting:

```math
Perf_{old}(\theta_{new})
<
Perf_{old}(\theta_{old})
```

Countermeasures include:

- replay;
- regularization;
- separate adapters;
- data mixtures;
- lower learning rate;
- selective freezing.

---

# 47. Curriculum

The data distribution changes over training time:

```math
P_t(x)
```

instead of remaining constant.

A curriculum may be organized by:

- difficulty;
- length;
- domain;
- reward;
- confidence;
- stage.

The order of exposure becomes part of the algorithm.

---

# 48. Long-context training

Increasing sequence length affects:

- the position system;
- activations;
- attention cost;
- optimizer throughput;
- packing;
- loss normalization.

Training at 1M tokens is not simply changing `max_seq_len`.

Contemporary tooling explicitly treats loss, positions, activation memory, and per-sequence GPU memory as separate bottlenecks.

---

# 49. Multimodal adaptation

For a VLM:

```text
vision encoder
    ↓
projector / connector
    ↓
LLM
```

We may:

- freeze the vision encoder;
- train only the projector;
- train the LLM + projector;
- fine-tune the entire system.

Each choice changes:

```math
TrainableParams
```

and the risk of destroying pretrained representations.

See [10_MULTIMODAL_VLM_OMNI_DATASHEET](10_MULTIMODAL_VLM_OMNI_DATASHEET.md).

---

# 50. Diffusion/flow adaptation

LoRA is also common in:

- attention projections;
- text encoders;
- DiT blocks.

The same low-rank concept remains, but the objective function and observables differ from LLM SFT.

See [04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET](04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md).

---

# 51. Data-quality feedback loop

A mature system looks like:

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

This is active data engineering.

The benchmark begins to guide data acquisition.

Risk: overfitting to the benchmark.

---

# 52. Training observables

Never monitor loss alone.

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
- MFU/compute utilization when available.

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

does not guarantee:

```math
TaskQuality\uparrow
```

especially under:

- overfitting;
- a misaligned objective;
- contaminated evaluation;
- preference overoptimization.

Evaluation must measure the desired behavior directly.

---

# 54. Training parameter coupling matrix

| ↑ variable | Primary effect | Common secondary effect |
|---|---|---|
| batch/tokens per update | less noisy gradient | may require a different LR |
| LR | update magnitude ↑ | instability/forgetting ↑ |
| context length | information per sample ↑ | memory/compute ↑ sharply |
| LoRA rank | adaptation capacity ↑ | trainable memory ↑ |
| LoRA targets | degrees of freedom ↑ | interference/overfit ↑ |
| preference beta | changes constraint/strength | style/capability trade-off |
| RL group size | improves reward-relative estimate | rollout cost ↑ |
| rollout length | exploration/horizon ↑ | cost/variance ↑ |
| KL penalty | policy drift ↓ | exploration/capability gain may ↓ |
| distillation temperature | changes soft-target smoothness | changes dark-knowledge transfer |

These relationships are not universally monotonic.

---

# 55. Failure surfaces

## Optimization divergence

- NaN;
- loss explosion;
- gradient explosion.

## Catastrophic forgetting

New-task performance rises while old-task performance falls.

## Mode/style collapse

Responses converge toward a narrow template.

## Reward collapse

Reward rises while real quality falls.

## Data contamination

Evaluation stops being a valid diagnostic.

## Synthetic monoculture

Diversity decreases.

## Overfitting

```math
Train\uparrow,Eval\downarrow
```

## Merge interference

Individual capabilities cancel one another out.

---

# 56. Local hardware reality

On a local workstation, distinguish:

### Inference feasible

from:

### Full training feasible

A GPU that can run a 12B model in Q4 cannot necessarily train that same 12B model.

On consumer hardware, the usual feasibility ordering is roughly:

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

but each model and sequence length shifts the curve.

Calculate first:

```math
M_{train}
=
weights+grads+optimizer+activations+workspace
```

---

# 57. Experimental protocol — fine-tuning

When comparing two configurations, hold constant:

- base checkpoint;
- tokenizer/template;
- dataset split;
- seed set;
- number of tokens;
- evaluation harness.

Change only the hypothesis under test.

Example:

```text
H0: r=16 and r=64 do not meaningfully change domain quality.

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

See [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

---

# 58. Provenance tags specific to this document

In addition to the global tags:

| Tag | Meaning |
|---|---|
| `DATA` | data composition/transformation |
| `TRAIN` | training hyperparameter |
| `ALIGN` | preference/reward/alignment stage |
| `PEFT` | parameter-efficient adaptation |
| `DISTILL` | knowledge/dataset distillation |
| `MERGE` | parameter/model merging |

See [CONVENTIONS](CONVENTIONS.md).

---

# 59. SOTA snapshot — 2026

The relevant picture in October 2026 is less “which algorithm won?” and more a convergence of practices:

1. **SFT remains foundational**, but modern post-training separates offline preference methods, online RL, and reward/verifier training.
2. Mature tooling exposes SFT, DPO, GRPO, KTO, RLOO, reward modeling, and distillation as distinct families.
3. RL for reasoning has made **rollout infrastructure, sampling, and sequence-level statistics** as important as the nominal loss.
4. GSPO popularized sequence-level policy ratios as a more stable alternative in some regimes, particularly MoE RL.
5. PEFT is no longer synonymous with vanilla LoRA: DoRA, initialization strategies, adapter mixing, and quantized training form a space of their own.
6. Model merging has become practical engineering, with linear merge, SLERP, task arithmetic, TIES, DARE, and variants.
7. Modern distillation includes logits, sequences, reasoning trajectories, and on-policy teacher/student loops.
8. Synthetic data requires curation and verification; “generate more examples” is not a sufficient data policy.

---

# 60. Checklist for dissecting any checkpoint

1. What is the base model?
2. What tokenizer/template?
3. How many pretraining tokens?
4. What data mixture?
5. What objective?
6. Was there continued pretraining?
7. Was there SFT?
8. Was the loss prompt+completion or completion-only?
9. Was preference training used?
10. DPO/KTO/ORPO/RL/GRPO/GSPO or equivalent?
11. What reward/verifier?
12. Online or offline?
13. Was synthetic data used?
14. Was there distillation?
15. Is it a merge?
16. What is the base lineage of the merged models?
17. Was there pruning?
18. Was PEFT used?
19. LoRA rank/alpha/targets?
20. QLoRA/DoRA?
21. What training sequence length?
22. What optimizer/LR schedule?
23. Which benchmark guided selection?
24. Is there contamination risk?
25. Which checkpoint is actually served at inference time?

---

# 61. Mechanical summary

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

Architecture defines the **space of what is possible**.

Data and objectives determine **where the system is pushed**.

Optimization determines **the trajectory through parameter space**.

Post-training determines **which regions of behavior are reinforced or suppressed**.

Inference simply operates the resulting system.

---

# Snapshot references

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
