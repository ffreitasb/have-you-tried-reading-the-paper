---
title: Reward Model / Verifier / Judge Datasheet v1.0
tags: [ai, reward-model, verifier, judge, prm, orm, rlvr, evaluation]
updated: 2026-10-01
---

# Reward Model / Verifier / Judge Datasheet v1.0

> Generators answer “what comes next?” Verifiers answer “is this correct/good?” Reward models learn a **scalar field of preference or quality**; judges may produce a score, ranking, critique, or decision.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md), [03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET](03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md), [08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET](08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md).

---

# 1. Four families that should not be conflated

## 1.1 Scalar Reward Model

```math
r_\theta(x,y)\in\mathbb R
```

Input: prompt/context $`x`$ + response/action $`y`$.  
Output: scalar.

---

## 1.2 Pairwise Preference Model

```math
P(y_A\succ y_B|x)
```

A latent score can induce preference:

```math
P(A>B)=\sigma(r_A-r_B)
```

---

## 1.3 Verifier

Decides a verifiable property:

```math
V(x,y)\rightarrow\{0,1\}
```

or a probability:

```math
P(correct|x,y)
```

It may be:

- rule-based;
- executable;
- learned;
- generative.

---

## 1.4 Judge

More general system:

```math
J(x,y,criteria)\rightarrow score/rank/critique
```

It may be a generative LLM, not necessarily a specialized reward head.

---

# 2. Bradley–Terry preference model

If $`r_A,r_B`$ are utilities:

```math
P(A>B)=
\frac{e^{r_A}}{e^{r_A}+e^{r_B}}
=
\sigma(r_A-r_B)
```

Loss for chosen/rejected pair:

```math
\mathcal L
=
-\log\sigma(r_{chosen}-r_{rejected})
```

Training learns **relative differences**, not necessarily a calibrated absolute scale.

---

# 3. Score ≠ probability

A reward of `7.4` does not mean a 74% chance of correctness.

To turn a score into a reliable probability, we need calibration:

```math
P(correct|r)
```

estimated/validated separately.

Possible techniques:

- Platt/logistic scaling;
- isotonic regression;
- temperature scaling;
- binning/calibration curves.

---

# 4. Outcome Reward Model — ORM

Evaluates the final answer:

```math
R_{outcome}=R(x,y_{final})
```

Advantages:

- cheap;
- simpler labeling;
- strong when the outcome is verifiable.

Limitations:

- cannot identify where the trajectory went wrong;
- may reward a correct result produced through spurious reasoning.

---

# 5. Process Reward Model — PRM

Evaluates intermediate steps:

```math
r_t=R(x,y_{1:t})
```

or transitions:

```math
r_t=R(s_t,a_t,s_{t+1})
```

This enables:

- early error detection;
- search pruning;
- agent supervision;
- dense reward.

### Cost

If every step requires evaluation:

```math
C_{PRM}\propto N_{steps}\times C_{verifier}
```

Process supervision improves observability but costs far more inference/annotation.

---

# 6. Bidirectional / lookahead process evaluation

Evaluating a step from the prefix alone can be ambiguous:

```math
P(correct\ step|prefix)
```

Continuation/outcome information can be incorporated:

```math
P(step\ valid|prefix,suffix/outcome)
```

This reduces myopia, but creates leakage if used incorrectly in an online setting.

---

# 7. Generative verifier

Instead of a scalar head:

```math
(x,y)
\rightarrow
LLM
\rightarrow
analysis/critique
\rightarrow
verdict
```

It may use tools/environment:

```math
Verifier
\rightarrow Tool
\rightarrow Evidence
\rightarrow Verdict
```

In 2026, environment-aware generative PRMs are appearing specifically to catch silent failures that do not surface as exceptions.

### Trade-off

```math
VerifierCapability\uparrow
\leftrightarrow
Latency/Cost/Variance\uparrow
```

---

# 8. Rule-based verifier

When a deterministic checker exists:

```math
V(y)=1[y\in\mathcal S_{valid}]
```

Examples:

- compilation;
- unit tests;
- symbolic equivalence;
- schema validation;
- game outcome;
- constraint solver.

This class provides high-precision reward **within the covered domain**, but that domain may be narrow.

---

# 9. RL with Verifiable Rewards — RLVR

Policy:

```math
y\sim\pi_\theta(y|x)
```

Verifier:

```math
r=V(x,y)
```

RL optimizes:

```math
\max_\theta E_{y\sim\pi_\theta}[r]
```

The bottleneck becomes verifier coverage.

Generative verifiers broaden the domain, but trade deterministic certainty for model error/calibration.

---

# 10. LLM-as-a-Judge

Evaluation prompt:

```math
J(prompt,response,rubric)\rightarrow judgment
```

Outputs may include:

- scalar 1–10;
- binary pass/fail;
- pairwise preference;
- categorical rubric;
- structured JSON;
- textual critique.

### Important

The judge is another model with its own priors.

```math
JudgeError\neq0
```

---

# 11. Pairwise judging

Given A/B:

```math
J(x,A,B)\rightarrow A>B\text{ or }B>A
```

Advantage: relative comparison is often cognitively easier than absolute scoring.

Problem: **position bias**.

Swap test:

```math
J(x,A,B)\stackrel{?}{=}inverse(J(x,B,A))
```

If not, the judge is positionally unstable.

---

# 12. Judge biases

## Position bias

Preference for the first/second option.

## Verbosity bias

```math
P(win|longer) > P(win|quality\ equivalent)
```

## Style bias

Markdown, assertiveness, equations, or tone may change the score without changing correctness.

## Self-preference

A model may favor outputs that resemble its own style/distribution.

## Reference anchoring

A flawed reference can pull the judge toward the wrong conclusion.

---

# 13. Calibration

If the judge returns confidence $`p_i`$:

Ideal calibration:

```math
P(correct|p=0.8)\approx0.8
```

### Brier score

```math
BS=\frac1N\sum_i(p_i-y_i)^2
```

### Expected Calibration Error

```math
ECE=\sum_b\frac{|B_b|}{N}
|acc(B_b)-conf(B_b)|
```

High accuracy does not imply good calibration.

---

# 14. Bias-corrected evaluation

If a judge has imperfect sensitivity/specificity, its raw judgment rate may be a biased estimator of true performance.

Conceptually:

```math
ObservedScore
=F(TrueQuality,JudgeQuality,Calibration)
```

When judge quality shifts across models/domains, direct score comparisons can reverse conclusions.

So the SOTA++ question is not merely:

> “which judge is better?”

but:

> “how stable is this judge's error/calibration function in this domain?”

---

# 15. Best-of-N

The generator produces:

```math
Y=\{y_1,\ldots,y_N\}
```

The verifier selects:

```math
y^*=\arg\max_iR(x,y_i)
```

If the probability of producing at least one good solution rises with $`N`$, the verifier converts compute into quality.

But:

```math
Quality_{selected}
\le
Quality_{oracle-best}
```

as a function of verifier error.

---

# 16. Selection economics

Approximate cost:

```math
C_{total}
=N\cdot C_{generation}
+N\cdot C_{verification}
```

If the verifier is itself a large generative model, selection may cost as much as generation.

Evaluate marginal gain:

```math
\frac{\Delta Quality}{\Delta Compute}
```

---

# 17. Majority voting / self-consistency

For discrete answers:

```math
\hat y=mode(y_1,\ldots,y_N)
```

Works when errors are sufficiently independent.

If outputs share a systematic bias:

```math
Corr(error_i,error_j)\uparrow
\Rightarrow
benefit\downarrow
```

Ensemble diversity matters.

---

# 18. Hidden-state verification

Verification does not need to inspect only final surface text.

If a reasoning trace has hidden states:

```math
h_{start},h_{end}
```

we can define:

```math
\Delta h=h_{end}-h_{start}
```

and classify trajectories using internal geometry.

ACL 2026 work shows that correct/incorrect trajectories can exhibit useful geometric differences for selection without training an additional reward model.

This expands “verifier” beyond surface text.

---

# 19. Rubric-augmented judging

Rubric:

```math
R=\{criterion_1,\ldots,criterion_m\}
```

A judge may decompose:

```math
score(y)=\sum_iw_i score_i(y)
```

Advantage: auditability.

Risk: a poor rubric creates **structured misguidance** — a wrong criterion consistently steers the model toward the wrong decision.

---

# 20. Reward hacking

The policy optimizes a proxy:

```math
\max R_{proxy}
```

but we want:

```math
\max U_{true}
```

If:

```math
R_{proxy}\neq U_{true}
```

the policy may exploit flaws.

Goodhart:

> when a measure becomes a target, its relationship with the true objective can degrade.

---

# 21. Overoptimization

Even a reasonable reward model can fail out of distribution when the policy is pushed toward extremes:

```math
\pi_{new}\gg\pi_{training\ distribution}
```

The harder you optimize against an imperfect RM, the more likely you are to exploit uncalibrated regions.

---

# 22. Verifier-guided search

Reasoning tree:

```math
s_0\rightarrow\{s_1^1,\ldots,s_1^k\}
```

PRM/verifier scores:

```math
R(s_t^i)
```

Beam/search keeps the top candidates.

Trade-off:

```math
BranchingFactor\uparrow
\Rightarrow
SearchCoverage\uparrow,
Compute\uparrow
```

---

# 23. Code: executor as verifier

In code:

```math
code\rightarrow compiler/tests\rightarrow result
```

This is an excellent external verifier for the properties it covers.

But:

```math
TestsPass\not\Rightarrow ProgramCorrect\ universally
```

Test coverage limits the evidence.

See [03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET](03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md).

---

# 24. Agents: process reward + environment

For trajectory:

```math
\tau=(s_0,a_0,s_1,a_1,\ldots)
```

An environment-aware PRM can verify:

- whether the action actually observed evidence;
- whether the state changed as expected;
- whether an error was recoverable;
- whether the tool was used correctly.

This moves evaluation closer to control systems rather than text alone.

---

# 25. Metrics

## Pairwise accuracy

```math
Acc=\frac{correct\ preferences}{total}
```

## Kendall $`\tau`$

Ordinal correlation.

## Spearman $`\rho`$

Rank correlation.

## Calibration

ECE/Brier/reliability diagram.

## Agreement

Cohen's kappa or equivalent when appropriate.

Do not use one metric for everything.

---

# 26. Failure surfaces

- reward-model domain shift;
- preference inconsistency;
- label noise;
- verbosity/style bias;
- position bias;
- reference error;
- calibration drift;
- reward hacking;
- overoptimization;
- correlated verifier/generator error;
- hidden rubric assumptions;
- process reward penalizing legitimate exploration.

---

# 27. SOTA Snapshot 2026

Relevant trends:

- PRMs are moving beyond math-step scoring and beginning to interact with environments;
- generative verifiers broaden RLVR into domains without trivial checkers;
- hidden-state trajectories are starting to be used as correctness signals;
- judge calibration/bias is being treated as an explicit statistical problem;
- rubric-augmented reward modeling tries to decompose “quality” into more auditable criteria.

---

# 28. Checklist for any evaluator

1. Is the output a score, probability, rank, or critique?
2. Is the scale calibrated?
3. Was it trained pairwise or pointwise?
4. Does it evaluate outcome or process?
5. Does it use external evidence?
6. Is a deterministic checker available?
7. What is the domain shift?
8. Is there position/verbosity/style bias?
9. Was a swap test performed?
10. What is the cost per candidate?
11. Do generator and judge share model-family bias?
12. Can the reward be exploited?
13. Which metric validates agreement/calibration?
14. Does Best-of-N improve because of the generator or the selector?

---

# Snapshot references

- DataPRM / Process-Level Reward Modeling for Agentic Data Analysis — https://arxiv.org/abs/2604.24198
- Your Reasoning Model is Secretly a Reward Model — https://aclanthology.org/2026.acl-long.788/
- Bias and Uncertainty in LLM-as-a-Judge Estimation — https://arxiv.org/abs/2605.06939
- C2: Rubric-Augmented Reward Modeling — https://aclanthology.org/2026.acl-long.523/
- The Bidirectional Process Reward Model — https://aclanthology.org/2026.acl-long.572/
- Crossing the Reward Bridge / generative verifier RLVR — https://aclanthology.org/2026.acl-long.178/
