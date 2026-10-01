---
title: Time-Series & Tabular Foundation Models Datasheet v1.0
tags: [ai, time-series, tabular, forecasting, tabpfn, foundation-models]
updated: 2026-10-01
---

# Time-Series & Tabular Foundation Models Datasheet v1.0

> Structured numbers are not “text with commas.” Time series have physical ordering and temporal dependence; tables contain heterogeneous features, missingness, and different symmetries. Foundation models in these domains need their own representational physics.

Related: [01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING](01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md), [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md), [12_REWARD_VERIFIER_JUDGE_DATASHEET](12_REWARD_VERIFIER_JUDGE_DATASHEET.md).

---

# PART A — TIME-SERIES FOUNDATION MODELS

# 1. Fundamental state

Multivariate time series:

\[
X=(x_1,\ldots,x_T),\quad x_t\in\mathbb R^D
\]

Unlike text:

- position corresponds to physical time;
- values carry scale and units;
- sampling interval matters;
- trend, seasonality, and regime are properties of the underlying generative process.

---

# 2. Forecasting

History:

\[
X_{1:T}
\]

Horizon:

\[
H
\]

Point forecast:

\[
\hat X_{T+1:T+H}=f_\theta(X_{1:T})
\]

Distributional forecast:

\[
p(X_{T+1:T+H}|X_{1:T})
\]

The second formulation is preferable when multiple futures are plausible.

---

# 3. Point-wise tokenization

Each timestamp becomes a token/embedding:

\[
e_t=\phi(x_t)
\]

Sequence length:

\[
N=T
\]

Good for fine temporal granularity; expensive for long sequences.

---

# 4. Patch tokenization

Patch of length \(P\):

\[
p_i=[x_{iP},\ldots,x_{iP+P-1}]
\]

Number of tokens:

\[
N\approx\frac{T}{P}
\]

Trade-off:

\[
P\uparrow
\Rightarrow
SequenceLength\downarrow,
LocalResolution\downarrow
\]

Patching is the temporal equivalent of reducing resolution.

---

# 5. Multi-scale representation

Real-world processes contain multiple frequency bands.

A hierarchical representation may retain:

\[
X^{(0)},X^{(1)},\ldots,X^{(L)}
\]

with:

\[
T_{l+1}<T_l
\]

Fine scales capture spikes; coarse scales capture trends and regimes.

Zeus 2026 uses a multiscale Transformer with a U-shaped hierarchy to balance point-level fidelity against long-sequence efficiency.

---

# 6. Normalization

A series may undergo an affine transform:

\[
x'_t=\frac{x_t-\mu}{\sigma}
\]

or local/instance-wise normalization.

This helps transfer across series with different scales, but it can erase absolute meaning when magnitude itself is semantically important.

### Rule

\[
Normalization\ choice\in Model\ Contract
\]

not merely optional preprocessing.

---

# 7. Covariates

Context may include:

\[
C_t=\{calendar,price,promotion,weather,static\ metadata,\ldots\}
\]

A real forecasting problem is closer to:

\[
p(Y_{future}|Y_{past},C_{past},C_{future-known})
\]

Keep separate:

- observed covariates;
- known-future covariates;
- static features.

---

# 8. Deterministic forecasting

MSE loss:

\[
\mathcal L_{MSE}=\frac1N\sum_i(y_i-\hat y_i)^2
\]

Well suited to mean prediction under specific assumptions.

Problem: it collapses a multimodal future into an average.

---

# 9. Quantile forecasting

For quantile \(\tau\):

Pinball loss:

\[
L_\tau(y,\hat q)
=
\max(\tau(y-\hat q),(\tau-1)(y-\hat q))
\]

Produces intervals such as:

\[
[q_{0.1},q_{0.5},q_{0.9}]
\]

Coverage must be calibrated for the target domain.

---

# 10. Probabilistic forecasting

A model may parameterize a distribution:

\[
p(y|\theta_t)
\]

or generate samples:

\[
y^{(1)},\ldots,y^{(N)}\sim p_\theta
\]

Metrics must evaluate the predictive distribution, not just mean error.

---

# 11. CRPS

The Continuous Ranked Probability Score compares a predicted distribution against the observation.

Conceptual form:

\[
CRPS(F,y)=\int_{-\infty}^{\infty}(F(z)-1[z\ge y])^2dz
\]

Lower is better.

---

# 12. Autoregressive forecasting

\[
p(y_{T+1:T+H}|X)
=
\prod_{h=1}^{H}
p(y_{T+h}|X,y_{T+1:T+h-1})
\]

Problem:

\[
Error_{h}\rightarrow Conditioning_{h+1}
\]

so errors can accumulate across the horizon.

---

# 13. Direct / parallel forecasting

Predict the full horizon at once:

\[
\hat Y_{1:H}=f_\theta(X)
\]

This avoids autoregressive error propagation, but the model still needs some other mechanism to represent dependencies within the forecast horizon.

---

# 14. Diffusion / flow time-series forecasting

Treat the future as a stochastic trajectory:

\[
Y_{future,\tau}
=\alpha_\tau Y_{future,0}+\sigma_\tau\epsilon
\]

or use a flow formulation:

\[
\frac{dY_\tau}{d\tau}=v_\theta(Y_\tau,\tau,X_{past})
\]

Useful for generating **ensembles of plausible futures**, especially in multimodal domains.

2026 snapshot: KiT applies a Diffusion Transformer plus flow matching to future financial OHLCV trajectories.

---

# 15. Masked time-series modeling

Mask interval \(M\):

\[
\mathcal L=\sum_{t\in M}\ell(x_t,\hat x_t)
\]

Varying the mask pattern can induce different tasks:

- extrapolation;
- interpolation;
- imputation;
- abstraction.

Zeus uses Multi-Objective Temporal Masking to unify these tasks without task-specific fine-tuning.

---

# 16. Imputation

Given mask \(m_t\):

\[
\hat x_t=f(X\odot m,m)
\]

Missingness itself may be informative:

\[
P(missing|state)\neq const
\]

So filling with zero or the mean without an explicit mask can introduce false semantics.

---

# 17. Anomaly detection

Possible approaches:

### Reconstruction residual

\[
e_t=|x_t-\hat x_t|
\]

### Forecast surprise

\[
score_t=-\log p(x_t|x_{<t})
\]

### Representation distance

\[
score_t=d(z_t,\mathcal M_{normal})
\]

The threshold depends on the operating regime and the cost of false positives.

---

# 18. Classification

Convert the series into a global representation:

\[
z=Pool(f_\theta(X))
\]

\[
P(y|X)=softmax(Wz)
\]

A multi-task foundation model attempts to make \(z\) transferable across domains.

---

# 19. Regime shift

The data-generating process changes:

\[
p_{train}(X,Y)\neq p_{deploy}(X,Y)
\]

For time series, drift may appear as:

- trend shift;
- volatility shift;
- seasonality shift;
- structural break;
- sensor recalibration.

Long context does not automatically fix the presence of old, now-irrelevant regimes.

---

# 20. Frequency domain

Discrete transform:

\[
X_k=\sum_{n=0}^{N-1}x_n e^{-j2\pi kn/N}
\]

This exposes periodic structure, but nonstationary processes may require time-frequency or other local methods.

Do not elevate “decomposition” into a universal requirement.

---

# 21. Failure surfaces in TSFMs

- frequency aliasing;
- scale mismatch;
- irregular sampling;
- covariate leakage;
- misclassified known-future features;
- regime shift;
- persistence bias;
- horizon extrapolation collapse;
- underdispersed uncertainty;
- calibration failure;
- domain-pretraining mismatch.

2026 causal stress-testing studies of TSFMs report abrupt failures on patterns outside the pretraining regime; this reinforces that “foundation” does not mean universal.

---

# PART B — TABULAR FOUNDATION MODELS

# 22. Tabular state

Supervised dataset:

\[
D=\{(x_i,y_i)\}_{i=1}^{N}
\]

\[
x_i=(x_{i1},\ldots,x_{iD})
\]

Features may be:

- continuous;
- categorical;
- ordinal;
- timestamps;
- missing;
- strings/IDs.

There is not necessarily a natural ordering of columns.

---

# 23. Feature tokenization

Each cell/feature may produce an embedding:

\[
e_{ij}=Embed_j(x_{ij})
\]

Column identity may be injected explicitly:

\[
e_{ij}=ValueEmbed(x_{ij})+ColumnEmbed(j)
\]

This resolves part of the heterogeneity problem.

---

# 24. Permutation considerations

Rows in supervised learning are usually exchangeable:

\[
P(D)=P(\pi(D))
\]

for permutation \(\pi\), unless explicit temporal or grouped structure exists.

Columns are not semantically exchangeable unless their identities are preserved.

The architecture must distinguish:

\[
Value\ identity\neq Feature\ identity
\]

---

# 25. Missingness

Define a mask:

\[
m_{ij}=1[x_{ij}\ observed]
\]

An ideal model receives:

\[
(x_{ij},m_{ij})
\]

Missingness may be MCAR, MAR, or MNAR; the mechanism changes the inference problem.

---

# 26. Prior-data fitted networks — PFN intuition

A TabPFN-style model is not simply “a Transformer trained on spreadsheets.”

During pretraining, the model learns over distributions of tasks, synthetic datasets, and priors:

\[
\theta^*=argmin E_{D\sim p(D)}L(f_\theta(D_{train},x^*),y^*)
\]

At inference time:

\[
P(y^*|D_{train},x^*)
\]

is computed **in context**, without optimizing new weights for each dataset.

This resembles amortized Bayesian inference / meta-learning.

---

# 27. In-context supervised learning

The context contains pairs:

\[
(x_1,y_1),\ldots,(x_N,y_N)
\]

plus query:

\[
x^*
\]

The model returns:

\[
P(y^*|x^*,D)
\]

The “prompt” is the training set itself.

---

# 28. Dataset size as context budget

Unlike an LLM:

\[
Context\sim N\times D
\]

Growth in samples and features increases memory/attention pressure.

TabPFN-2.5 expands the operating regime to tens of thousands of rows and thousands of features, but those limits remain architecturally relevant.

---

# 29. Classification vs regression

Classification:

\[
P(y=c|x,D)
\]

Regression:

\[
p(y|x,D)
\]

Regression must model scale, tails, and heteroscedasticity in ways classification does not.

---

# 30. Distillation to a deployable model

A foundation model may act as an expensive teacher:

\[
F(D,x)\rightarrow \hat y
\]

Distill it into a smaller model:

\[
g_\phi(x)\approx F(D,x)
\]

TabPFN-2.5 introduces a distillation path to MLP/tree ensembles, separating **amortized training-time intelligence** from cheap runtime execution.

---

# 31. Tabular metrics

Classification:

- accuracy;
- ROC-AUC;
- PR-AUC;
- log loss;
- Brier score / calibration.

Regression:

- MAE;
- RMSE;
- R²;
- NLL/CRPS when probabilistic.

Comparisons across multiple datasets need robust ranks/aggregates, not just a raw arithmetic mean.

---

# 32. Tabular failure surfaces

- dataset too large/wide for context;
- high-cardinality categorical explosion;
- leakage;
- feature-semantics mismatch;
- missingness-mechanism shift;
- covariate shift;
- target shift;
- calibration drift;
- extrapolation outside support;
- IDs treated as ordinal numbers;
- correlated rows violating assumed exchangeability.

---

# 33. Time series vs tabular — do not mentally collapse them

Time series:

\[
order\ matters
\]

Classical i.i.d. tabular learning:

\[
row\ order\ ideally\ irrelevant
\]

Time series have a clock and a forecast horizon; supervised tabular learning has a training set/context.

That is why the two domains share this file but are not treated as the same mathematics.

---

# 34. Runtime

## Time series

Primary cost:

\[
N_{tokens}=f(T,patch,multiscale)
\]

## Tabular PFN

Cost:

\[
N_{context}=f(N_{rows},D_{features},representation)
\]

In both cases, increasing “context data” does not change model weights, but it does increase inference cost.

See [09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET](09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md).

---

# 35. SOTA snapshot — 2026

### Zeus

- tuning-free multi-task TSFM;
- point-wise tokenization;
- multiscale Transformer;
- Multi-Objective Temporal Masking;
- forecasting, probabilistic forecasting, imputation, anomaly detection, classification.

### TabPFN-2.5

- substantial expansion of dataset/feature operating regime;
- strong in-context tabular prediction;
- deployment distillation to MLP/tree ensembles.

### KiT

- flow-matching Diffusion Transformer for future financial trajectories;
- example of a continuous generative objective applied to forecasting.

The important message: **time-series and tabular foundation models are diverging architecturally, not converging toward a simplistic “LLM for numbers.”**

---

# 36. TSFM checklist

1. Point-wise or patch tokenization?
2. What sampling interval?
3. Is normalization part of the recipe?
4. Are there known-future covariates?
5. Is the forecast point, quantile, or distributional?
6. Autoregressive or parallel?
7. What horizon was trained/evaluated?
8. How are missing and irregularly sampled values handled?
9. What regime shifts are expected?
10. Are forecast samples calibrated?
11. What is the footprint as series length grows?

---

# 37. Tabular FM checklist

1. How are continuous and categorical features represented?
2. Is column identity explicit?
3. Is a missingness mask used?
4. Is inference in-context or fine-tuned?
5. What are the row/feature limits?
6. Does row order matter to the implementation?
7. Are predicted probabilities calibrated?
8. Is there a distillation path for deployment?
9. How are high-cardinality categoricals handled?
10. Is there leakage risk in the context?

---

# Snapshot references

- Zeus: Towards Tuning-Free Foundation Model for Time Series Analysis — https://proceedings.mlr.press/v306/fu26n.html
- TabPFN-2.5 — https://arxiv.org/abs/2511.08667
- KiT: Diffusion Transformer for financial time-series forecasting — https://arxiv.org/abs/2609.34507
- Causal Analysis for Time Series Foundation Models — https://arxiv.org/abs/2608.24303
