---
title: Evaluation, Benchmarking & Experimentation Datasheet — SOTA++ 2026
aliases: [Evaluation Datasheet, Benchmarking Datasheet, AI Experimentation Reference]
tags: [ai, reference, evaluation, benchmarks, experimentation, statistics, reproducibility]
updated: 2026-10-01
---

# Evaluation, Benchmarking & Experimentation Datasheet — SOTA++ 2026

> A model does not simply “have performance.” It produces a distribution of outcomes **under a specific experimental configuration**. Evaluation is the engineering discipline required to separate real gains from noise, harness effects, prompt effects, contamination, and wishful thinking.

The central conceptual equation is:

```math
\boxed{
ObservedScore
=
f(
Model,
Prompt,
Inference,
Harness,
Dataset,
Metric,
Randomness,
Environment
)
}
```

Therefore:

```math
Score(Model)\quad\text{is usually a dangerous shorthand.}
```

See also:

- [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md)
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md)
- [16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET](16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md)
- [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md)
- [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md)

---

# 1. What exactly is being evaluated?

Before computing any metric, define the **System Under Test — SUT**.

It may be:

## 1.1 Raw checkpoint

```math
SUT=Weights+Tokenizer
```

## 1.2 Model + prompt/template

```math
SUT=Model+PromptPolicy
```

## 1.3 Model + inference configuration

```math
SUT=Model+Prompt+Sampler
```

## 1.4 Pipeline

```math
SUT=Retriever+Reranker+Model
```

## 1.5 Agent

```math
SUT=Model+Scaffold+Tools+Environment
```

## 1.6 Complete product

```math
SUT=EverythingTheUserExperiences
```

If the SUT is not explicit, score comparisons may be invalid.

---

# 2. Experimental error decomposition

Think in terms of:

```math
Y_{ijk}
=
\mu
+M_i
+H_j
+R_k
+\epsilon_{ijk}
```

where:

- $`M_i`$: model/configuration effect;
- $`H_j`$: harness/prompt/scaffold effect;
- $`R_k`$: seed/randomness effect;
- $`\epsilon`$: residual.

We want to estimate $`M_i`$, but we often measure all of them at once.

---

# 3. Benchmark ≠ metric ≠ harness

## Benchmark

Defines the set of tasks/examples/protocol.

## Metric

Maps an outcome to a scalar/vector:

```math
Metric(y,\hat y)
```

## Harness

Executes:

- prompt construction;
- model call;
- decoding;
- parsing;
- scoring;
- aggregation.

Changing the harness can change the score even when the weights are identical.

---

# 4. The minimum experimental unit

A record should contain at least:

```yaml
experiment:
  model_id: ...
  model_hash: ...
  tokenizer: ...
  quantization: ...
  backend: ...
  backend_version: ...
  prompt_template: ...
  system_prompt_hash: ...
  context_limit: ...
  generation:
    temperature: ...
    top_p: ...
    min_p: ...
    max_tokens: ...
    seed: ...
  dataset:
    name: ...
    version: ...
    split: ...
    hash: ...
  metric: ...
  hardware: ...
  timestamp: ...
```

Without versioning, a result becomes historical anecdote.

---

# 5. Deterministic metric versus judged metric

## Deterministic

```math
score=g(reference,prediction)
```

Examples:

- exact match;
- test pass/fail;
- numerical tolerance;
- WER;
- retrieval recall.

## Judged

```math
score=Judge(prompt,response,rubric)
```

Another model or a human infers quality.

This adds another source of error:

```math
Var_{judge}
```

See [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 6. Accuracy

```math
Accuracy=
\frac{\sum_i\mathbf1(\hat y_i=y_i)}{N}
```

Simple, but it requires an unambiguous definition of “correct.”

For imbalanced classes, accuracy can be misleading.

---

# 7. Precision, Recall, and F1

```math
Precision=
\frac{TP}{TP+FP}
```

```math
Recall=
\frac{TP}{TP+FN}
```

```math
F1=
2\frac{Precision\cdot Recall}{Precision+Recall}
```

Macro and micro averaging answer different questions.

---

# 8. Exact Match

```math
EM=
\frac1N\sum_i\mathbf1(normalize(\hat y_i)=normalize(y_i))
```

The `normalize()` function is part of the metric.

Change it and you change the benchmark.

---

# 9. Pass@k

In code generation, with $`n`$ samples and $`c`$ correct ones:

```math
pass@k
=
1-
\frac{\binom{n-c}{k}}{\binom nk}
```

when the estimator's assumptions hold.

Pass@1 measures a different operational reality from pass@100.

```math
SearchBudget\uparrow
\Rightarrow
pass@k\uparrow
```

without the model itself changing.

---

# 10. Retrieval metrics

## Recall@K

```math
Recall@K
=
\frac{RelevantRetrieved@K}{TotalRelevant}
```

## Precision@K

```math
Precision@K
=
\frac{RelevantRetrieved@K}{K}
```

## MRR

```math
MRR
=
\frac1N
\sum_i
\frac1{rank_i}
```

## DCG

```math
DCG@K
=
\sum_{i=1}^{K}
\frac{2^{rel_i}-1}{\log_2(i+1)}
```

## NDCG

```math
NDCG@K
=
\frac{DCG@K}{IDCG@K}
```

See [11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET](11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md).

---

# 11. Perplexity

For a sequence:

```math
PPL=
\exp\left(
-\frac1T
\sum_t
\log p(x_t|x_{<t})
\right)
```

Useful for probabilistic language modeling, but:

```math
LowerPPL
\not\Rightarrow
BetterInstructionFollowing
```

necessarily.

Comparing perplexity across different tokenizers requires extreme care.

---

# 12. Calibration

If a model reports probability $`p`$, ideally:

```math
P(correct|confidence=p)\approx p
```

## Brier score

```math
BS=
\frac1N\sum_i(p_i-y_i)^2
```

## ECE

Bins predictions by confidence and measures the gap between confidence and accuracy.

Calibration is distinct from accuracy.

---

# 13. ASR

## Word Error Rate

```math
WER=
\frac{S+D+I}{N}
```

where:

- $`S`$: substitutions;
- $`D`$: deletions;
- $`I`$: insertions.

See [06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET](06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md).

---

# 14. Time-series metrics

## MAE

```math
MAE=
\frac1N\sum_i|y_i-\hat y_i|
```

## RMSE

```math
RMSE=
\sqrt{
\frac1N\sum_i(y_i-\hat y_i)^2
}
```

## MAPE caveat

```math
MAPE=
\frac{100}{N}
\sum_i
\left|
\frac{y_i-\hat y_i}{y_i}
\right|
```

It explodes or becomes unstable when $`y_i\approx0`$.

Probabilistic forecasts require distribution- or quantile-aware metrics.

See [14_TIME_SERIES_TABULAR_FOUNDATION_MODELS](14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md).

---

# 15. Image/video/audio generation

There is no single sufficient “quality metric.”

Distinct dimensions include:

- fidelity;
- prompt adherence;
- identity consistency;
- temporal consistency;
- perceptual quality;
- diversity;
- human preference.

Therefore:

```math
Quality
\in
\mathbb R^d
```

not necessarily:

```math
Quality\in\mathbb R
```

A single scalar ranking hides trade-offs.

---

# 16. 3D evaluation

May include:

- Chamfer distance;
- normal consistency;
- IoU;
- watertightness;
- non-manifold edges;
- geometric validity;
- render-space perceptual metrics.

For manufacturing:

```math
Printable\neq VisuallyPlausible
```

See [07_3D_GENERATION_REPRESENTATION_DATASHEET](07_3D_GENERATION_REPRESENTATION_DATASHEET.md).

---

# 17. Agent evaluation

Agents require metrics beyond the final text:

```math
SuccessRate
```

```math
StepsToSuccess
```

```math
ToolCalls
```

```math
Cost
```

```math
UnsafeActions
```

```math
RecoveryRate
```

```math
StateValidity
```

A polished answer can still accompany a terrible operational trajectory.

---

# 18. World/VLA evaluation

Separate:

- prediction accuracy;
- rollout fidelity;
- action success;
- collision/safety rate;
- horizon degradation;
- sim-to-real gap.

World-model error can accumulate:

```math
\epsilon_{t+H}
=f(\epsilon_t,H,dynamics)
```

See [13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET](13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md).

---

# 19. Statistical uncertainty is not optional

An observed score is a sample:

```math
\hat\mu
```

We want to estimate:

```math
\mu
```

with uncertainty.

---
# 20. Standard error

For a mean:

```math
SE=
\frac{s}{\sqrt N}
```

Increasing $`N`$ reduces uncertainty approximately as:

```math
1/\sqrt N
```

not linearly with $`N`$.

---

# 21. Confidence interval

A simple asymptotic form:

```math
CI
\approx
\hat\mu
\pm
z_{\alpha/2}SE
```

For many benchmarks, bootstrap is more flexible.

---

# 22. Bootstrap

1. sample examples with replacement;
2. recompute the metric;
3. repeat $`B`$ times;
4. obtain an empirical distribution.

```math
\{\hat\theta_1^*,\ldots,\hat\theta_B^*\}
```

Useful for metrics without a simple analytical variance formula.

---

# 23. Paired design

If models A and B answer the **same items**, use paired differences:

```math
d_i=s_i(A)-s_i(B)
```

Then study:

```math
\bar d
```

This removes some variation caused by item difficulty.

It is generally better than treating the two means as independent samples.

---

# 24. McNemar for paired correct/incorrect outcomes

For binary classification, count discordant outcomes:

- A correct / B wrong: $`b`$
- A wrong / B correct: $`c`$

Evidence for a difference comes from $`b`$ versus $`c`$, not from isolated total accuracies.

---

# 25. Permutation test

Under the null hypothesis that labels/configurations are exchangeable, permute the paired assignments and compute the distribution of $`\Delta`$.

Useful when we do not want to assume normality.

---

# 26. Effect size

Statistical significance does not imply practical significance.

Ask:

```math
|\Delta|\quad\text{is it large enough to justify the cost/risk?}
```

Example:

+0.2 benchmark points may not justify +70% VRAM.

---

# 27. Multiple comparisons

If you test hundreds of configurations, some “winner” will emerge by chance.

```math
P(false\ positive)\uparrow
```

with the number of hypotheses.

Use:

- a held-out final set;
- corrections when appropriate;
- preregistered hypotheses;
- do not select seeds/configurations on the test set.

---

# 28. Seed variance

For stochastic generation:

```math
Y_{m,s}
```

where $`s`$ is the seed.

Estimate:

```math
Var_s(Y|m)
```

before interpreting differences between models.

If:

```math
|\Delta_{models}|
<
\sigma_{seed}
```

a single run is weak evidence.

---

# 29. Hierarchical variance

In a benchmark with tasks, examples, and seeds:

```math
Y_{task,item,seed}
```

variance can be decomposed across multiple levels.

This reveals whether the result is dominated by:

- a few categories;
- a few items;
- randomness.

A macro-average can hide all of this.

---

# 30. Stochastic benchmark protocol

For open-ended generation:

```text
for model/config:
    for item:
        for seed in S:
            generate
            score
```

Then report:

- mean;
- median;
- std/IQR;
- CI;
- failure rate;
- tails.

---

# 31. Tail metrics

Users do not experience only “the mean.”

For latency:

```math
p50,p95,p99
```

For safety/reliability, worst-case and failure-tail behavior can dominate risk.

For agents:

```math
P(catastrophic\ failure)
```

may matter more than mean success rate.

---

# 32. Benchmark contamination

Types:

## Exact contamination

The identical item appears in training.

## Near-duplicate

A paraphrase/transformation appears.

## Solution contamination

The answer/solution appears in the data.

## Benchmark-aware post-training

The model was explicitly optimized for the benchmark.

Even without literal leakage, the score stops being a neutral estimate of generalization.

---

# 33. Benchmark saturation

If nearly all relevant models are close to the ceiling:

```math
Var_{models}(score)\rightarrow0
```

the benchmark loses discriminative power.

A 2026 study analyzing 60 benchmarks found saturation across a large and growing share as benchmarks aged; expert-curated benchmarks were, on average, more resistant than crowdsourced ones.

The lesson:

```math
BenchmarkHalfLife<\infty
```

---

# 34. Dynamic benchmarks

Benchmarks updated periodically try to reduce contamination and saturation.

LiveBench exemplifies:

- refreshed questions;
- recent sources;
- objective ground truth where possible;
- multiple categories.

But updating also means:

```math
Score_{2025}\not\equiv Score_{2026}
```

unless the dataset version is tracked.

---

# 35. Public versus private test sets

Private test data reduces direct exposure, but does not eliminate:

- conceptual leakage;
- benchmark-targeted optimization;
- saturation;
- similar training examples.

Therefore:

```math
Private\neq ContaminationProof
```

---

# 36. LLM-as-a-Judge

Judge:

```math
J(prompt,response,rubric)
\rightarrow score/verdict
```

Common problems:

- position bias;
- verbosity bias;
- style bias;
- self-preference;
- reference anchoring;
- domain mismatch.

See [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# 37. Swap test

For a pairwise judge:

1. judge A,B;
2. reverse the order to B,A;
3. compare.

If:

```math
J(A,B)\neq reverse(J(B,A))
```

there is inconsistency/position sensitivity.

---

# 38. Rubric decomposition

Instead of a monolithic score:

```math
Quality
=
(w_1q_1,\ldots,w_kq_k)
```

Possible dimensions:

- correctness;
- completeness;
- relevance;
- style;
- safety;
- evidence.

This improves auditability.

---

# 39. Human evaluation

Human evaluation is not magical ground truth.

It has:

- inter-rater disagreement;
- fatigue;
- rubric ambiguity;
- expertise variation;
- context effects.

Agreement metrics help quantify consistency.

---

# 40. Model versus scaffold

A coding-agent benchmark often measures:

```math
Model
+
AgentLoop
+
Tools
+
Prompt
+
Search
+
RetryBudget
```

not only the model checkpoint.

SWE-bench Verified, for example, explicitly compares systems ranging from simple loops to RAG/multi-rollout/review systems.

Therefore an agent leaderboard is not a pure LLM leaderboard.

---

# 41. Harness sensitivity

Small changes in:

- few-shot examples;
- answer parsing;
- stop sequences;
- whitespace;
- chat template;
- reasoning budget;

can change results.

A benchmark without a versioned harness is not fully reproducible.

---

# 42. Quality versus test-time compute

If configuration A uses:

```math
N_A=1
```

sample while B uses:

```math
N_B=64
```

plus a verifier,

we are not comparing only models.

We are comparing:

```math
Model\times SearchBudget
```

Reporting:

```math
Quality(Cost)
```

is more honest.

---

# 43. Best-of-N evaluation

Generate:

```math
y_1,\ldots,y_N
```

Select:

```math
y^*=\arg\max_i V(y_i)
```

Score increases with:

- generator diversity;
- N;
- verifier quality.

Attributing the entire gain to the generator is a causal error.

---

# 44. Runtime evaluation

## TTFT

Time To First Token.

If a request starts at $`t_0`$ and the first token arrives at $`t_1`$:

```math
TTFT=t_1-t_0
```

## Inter-token latency / TPOT

Average time per token after the first token.

## Generation TPS

```math
TPS=
\frac{N_{generated}}{T_{decode}}
```

## Throughput

```math
Throughput=
\frac{TotalTokens}{WallClock}
```

Single-user TPS and server throughput optimize different things.

---

# 45. Prefill versus decode benchmark

Never conflate:

```math
PromptTPS
```

with:

```math
DecodeTPS
```

See [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

Prefill is much more parallelizable; decode is often memory-bandwidth bound.

---

# 46. Memory metric

Record:

- model-load VRAM;
- idle VRAM;
- peak prefill;
- peak decode;
- host RAM;
- KV allocation;
- temporary workspace.

A single “VRAM used” number is ambiguous without an execution phase.

---
# 47. Energy / efficiency

When available:

```math
EnergyPerToken
=
\frac{\int P(t)dt}{N_{tokens}}
```

or:

```math
J/request
```

For local inference, performance per watt can affect hardware decisions as much as TPS.

---

# 48. Pareto analysis

Instead of searching for the “best model,” construct a vector:

```math
z=
(Quality,Latency,Memory,Cost,Context)
```

A model is Pareto-dominated if another model is at least as good in every dimension and strictly better in at least one.

For an RTX 2060 12 GB:

```math
VRAM\le12GB
```

is a real constraint, not a decorative leaderboard column.

---

# 49. Quality per physical budget

Useful metrics include:

```math
Quality/GB
```

```math
Quality/Joule
```

```math
Quality/Second
```

```math
Quality/TokenBudget
```

especially when comparing quantizations and model sizes.

---

# 50. Quantization experiment

When comparing Q4 versus Q5:

**Control:**

- model source;
- context;
- sampler;
- backend;
- prompt set.

**Observe:**

- task quality;
- logit divergence where available;
- VRAM;
- TPS;
- TTFT.

The questions are:

```math
\frac{\Delta Quality}{\Delta Memory}
```

and:

```math
\frac{\Delta Quality}{\Delta Throughput}
```

---

# 51. A/B sampler experiment

To compare Min-P:

- same model;
- same prompt set;
- same seed set where the backend permits;
- all other samplers fixed;
- multiple outputs.

Do not use “I thought this text looked nicer” as the only statistic.

Capture:

- repetition rate;
- lexical diversity;
- judge rubric;
- human pairwise preference;
- failure counts.

---

# 52. Evaluation dataset design

The sample should represent the target distribution:

```math
D_{eval}\sim D_{deployment}
```

as closely as practical.

If the benchmark is academic while deployment is Portuguese-language B2B customer service:

```math
ExternalValidity\downarrow
```

even with an excellent score.

---

# 53. Slice analysis

Never report only an aggregate score.

Partition by:

- language;
- difficulty;
- length;
- domain;
- modality;
- risk level;
- tool type.

It is possible that:

```math
Mean_A>Mean_B
```

while:

```math
A<B
```

on the slice that actually matters in production.

---

# 54. Regression suite

After selecting a system, maintain a fixed regression set:

```text
must-pass
known-hard
known-failure
security
format
latency
```

Run it again after every update.

This turns benchmarking into **process control**.

---

# 55. Golden cases

Small, semantically important cases inspected manually.

They do not replace a broad benchmark.

They are useful for detecting obvious regressions with high interpretability.

---

# 56. Canary tests

Cases designed to detect one specific failure.

Examples:

- template corruption;
- context truncation;
- tool hallucination;
- Unicode/tokenizer bugs.

A good canary has clear causality.

---

# 57. Adversarial evaluation

Normal evaluation measures the nominal distribution.

Adversarial evaluation measures a hostile neighborhood:

```math
x' = x+\delta
```

or inputs deliberately constructed to trigger failure.

See [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

---

# 58. Evaluation leakage through the development loop

Even without training model weights:

if you repeatedly inspect the test set and adjust prompts/configuration:

```math
TestSet\rightarrow DevelopmentSignal
```

then it is no longer a clean test set.

Maintain:

- a development set;
- a final holdout.

---

# 59. Organizational benchmark overfitting

A team can optimize the KPI until it loses external validity.

```math
Leaderboard\uparrow
\not\Rightarrow
RealWorldUtility\uparrow
```

This is Goodhart applied to evaluation.

---

# 60. Benchmark retirement

Reasons to retire or downgrade a benchmark include:

- saturation;
- known contamination;
- poor external validity;
- metric no longer relevant;
- harness ambiguity;
- obsolete task.

There is no virtue in preserving historical comparability at the expense of current signal.

---

# 61. SOTA snapshot — 2026

Points particularly relevant in October 2026:

1. Benchmark contamination is no longer a peripheral caveat; it is a central design variable.
2. 2026 studies show broad saturation across older benchmarks and reinforce the need for rotating and expert-curated suites.
3. Live/dynamic benchmarks are a useful response, but require temporal dataset versioning.
4. LLM-as-a-Judge has scaled open-ended evaluation, but position, verbosity, style, and calibration bias must be measured rather than assumed absent.
5. Coding-agent evaluation has made the **model vs scaffold/system** distinction explicit.
6. HELM remains a conceptual reference for holistic/reproducible evaluation, although the general project entered maintenance mode in June 2026; this reinforces the need to avoid dependence on a single harness.
7. Modern evaluation is multi-objective: capability, reliability, safety, latency, memory, and cost should be reported together.

---

# 62. Experiment card — recommended template

```markdown
## Hypothesis

## System under test

## Independent variable

## Controlled variables

## Dataset + version + hash

## Metric definitions

## Seed/repetition policy

## Hardware/runtime

## Results
- mean:
- median:
- std/IQR:
- confidence interval:
- failure count:

## Paired differences

## Slice analysis

## Physical cost
- VRAM:
- RAM:
- TTFT:
- TPS:
- energy/cost:

## Decision rule

## Caveats
```

---

# 63. Decision rule before the experiment

Define in advance:

```math
Accept\ A
\quad\text{if}\quad
\Delta Q>\delta_{min}
```

subject to:

```math
Memory<M_{max}
```

```math
Latency<L_{max}
```

This reduces post-hoc rationalization.

---

# 64. Minimal local-model test battery

For a local stack, I would keep at least:

1. task accuracy / instruction adherence;
2. Portuguese naturalness;
3. code correctness where applicable;
4. long-context retrieval;
5. repetition/degeneration;
6. structured-output validity;
7. TTFT;
8. decode TPS;
9. peak VRAM/RAM;
10. context scaling;
11. your own known failure cases;
12. safety/tool tests for agentic systems.

For local decisions, this battery should be more valuable than an isolated position on a public leaderboard.

---

# 65. The final equation

```math
\boxed{
Evidence
=
Measurement
+
Uncertainty
+
Protocol
+
Reproducibility
}
```

Without uncertainty, we have a number.

Without protocol, we have benchmark folklore.

Without reproducibility, we have an anecdote.

---

# Checklist for any benchmark that appears tomorrow

1. What SUT is being measured?
2. Raw model or complete system?
3. Which dataset version?
4. Public or private?
5. Is there contamination evidence?
6. Is it saturated?
7. What metric?
8. Is the metric objective or judged?
9. Which judge?
10. Was the judge calibrated?
11. Was order-swapping tested?
12. How many samples/seeds?
13. What inference budget?
14. Which prompt/template?
15. Which harness/version?
16. What context limit?
17. What quantization?
18. What hardware/backend?
19. Are CI/variance reported?
20. Is the comparison paired?
21. Is there slice analysis?
22. Is physical cost reported?
23. What is the external validity?
24. Does the score improve something that actually matters?
25. Would the decision change if the benchmark moved within its CI?

---

# Snapshot references

- LiveBench — https://arxiv.org/abs/2406.19314
- LiveBench ICLR 2025 — https://proceedings.iclr.cc/paper_files/paper/2025/hash/e4a46394ba5378b3f9a186a5b4c650d1-Abstract-Conference.html
- When AI Benchmarks Plateau — https://proceedings.mlr.press/v306/akhtar26a.html
- HELM — https://github.com/stanford-crfm/helm
- SWE-bench Verified — https://www.swebench.com/verified.html
- Judging the Judges: Position Bias — https://arxiv.org/abs/2406.07791
- Mitigating the Bias of Large Language Model Evaluation — https://arxiv.org/abs/2409.16788
- [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md) for 2026 judge/reward references
