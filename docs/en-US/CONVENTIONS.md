---
title: Conventions & Maintenance Rules — Foundation Model Engineering Datasheets
aliases: [Datasheet Conventions, Editorial Conventions]
tags: [ai, reference, governance, conventions, knowledge-management]
updated: 2026-10-01
---

# Conventions & Maintenance Rules

> This file governs **how the collection grows without turning into an inconsistent taxonomy**.

---

# 1. Criteria for creating a new datasheet

A new domain file is justified only when at least one of these axes changes materially:

```math
\boxed{
Representation
\lor
Objective
\lor
InferenceTopology
\lor
StateDynamics
}
```

Do not create a separate file merely because there is:

- a new product;
- a new checkpoint;
- a new acronym;
- a new sampler;
- a new UI;
- a new adaptation technique.

Those belong in the document whose mechanism already covers the new development.

---

# 2. Canonical datasheet structure

When applicable, follow this order:

1. **Scope & boundary**
2. **Canonical computational graph**
3. **Representation / state tensors**
4. **Governing equations**
5. **Architecture parameters**
6. **Training/objective parameters**
7. **Inference controls**
8. **Coupling matrix**
9. **Compute/memory model**
10. **Observables**
11. **Failure surfaces**
12. **Experimental protocol**
13. **Backend/tool mapping**
14. **Dated technology snapshot**
15. **References**

Not every file needs every section, but omissions should be intentional.

---

# 3. Provenance tags

Use the canonical definitions in [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

Main tags:

```text
ARCH
MODEL
OBJ
DATA
TRAIN
ALIGN
PEFT
DISTILL
MERGE
GEN
INF
STATE
BACKEND
PIPE
INDEX
EVAL
SEC
UI
HEURISTIC
```

A variable may carry more than one tag when it crosses layers.

---

# 4. Levels of assertion

Every technical statement should fall, implicitly or explicitly, into one of these classes:

## Identity / definition

True by definition.

Example:

```math
Recall@K=RelevantRetrieved@K/TotalRelevant
```

## Architecture fact

True for a specific family/model.

Example:

> a particular model uses GQA.

Requires a source/snapshot when contemporary.

## Approximation

A useful engineering model.

Example:

```math
M_{KV}\approx2LTn_{kv}d_hbB
```

State assumptions when necessary.

## Empirical regularity

Behavior observed in common operating regimes.

Example:

> very high CFG often degrades images in a particular family.

## Heuristic

Operational recommendation.

It must be clearly separated from the mathematics.

## Vendor/UI behavior

Valid only for the identified product/backend.

---

# 5. The “phenomenology ≠ mechanism” rule

Two knobs can produce a similar subjective effect without being equivalent.

Example:

```math
Temperature\neq CFG
```

even if both can alter the perceived degree of “freedom.”

Never turn a perceptual analogy into a mathematical equivalence.

---

# 6. Symbols

Symbols are local to the domain where collisions exist.

Rules:

- $`\mathcal L`$ reserved for loss whenever practical;
- $`\theta`$ for learned parameters;
- $`B`$ for batch;
- $`T`$ for length/time, always contextualized;
- $`d`$ for dimension;
- $`r`$ for low-rank rank in PEFT context;
- $`\eta`$ for learning rate in training context;
- $`\tau`$ for contrastive/calibration temperature when defined;
- $`s`$ for CFG/guidance when defined.

See collisions in [19_PARAMETER_GLOSSARY_AND_REGISTRY](19_PARAMETER_GLOSSARY_AND_REGISTRY.md).

---

# 7. Tensor shapes

Always make axis order explicit when shape matters.

Preferred forms:

## Sequence

```math
[B,T,d]
```

## Latent image

```math
[B,C,H,W]
```

## Video

```math
[B,T,C,H,W]
```

or another order **provided it is declared**.

Do not silently assume a framework convention.

---

# 8. Units

## Memory

Prefer GiB/MiB when computing in binary units.

```math
1GiB=2^{30}\ bytes
```

## Commercial storage

GB/TB may be decimal when reproducing a vendor specification.

## Bandwidth

Specify GB/s or GiB/s when precision matters.

## Time

ms/s.

## Throughput

Always name the unit:

- tokens/s;
- samples/s;
- frames/s;
- requests/s.

---

# 9. Snapshot policy

The collection mixes two kinds of knowledge.

## Durable core

Equations, definitions, taxonomies.

These should not depend on the date.

## Technology snapshot

- current models;
- backend features;
- library support;
- active benchmarks;
- specs/protocols.

Always include the date in the global `updated:` header and, where needed, in the snapshot section.

---

# 10. Source policy

For contemporary claims, prefer:

1. original paper;
2. official documentation;
3. official repository;
4. standards/framework body;
5. trustworthy survey.

Avoid using a secondary post as the primary source when the original exists.

---

# 11. Cross-link policy

All files live at the root of the same directory.

Use Obsidian wikilinks without `.md`:

```text
[02_LLM_TRANSFORMER_INFERENCE_DATASHEET](02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md)
```

Do not use relative paths while all files remain at the root.

---

# 12. File naming

Numbered datasheets:

```text
NN_UPPER_SNAKE_CASE_DATASHEET.md
```

Established exceptions should retain their names to avoid breaking backlinks.

Meta files do not need numbers:

```text
CONVENTIONS.md
CHANGELOG.md
```

---

# 13. Rename policy

Do not rename an existing file without:

1. updating all wikilinks;
2. recording the change in the CHANGELOG;
3. ideally retaining an alias or migration note.

Knowledge management favors stable identifiers.

---

# 14. Canonical parameter naming

When a term collides, use a qualified name:

- Sampling Temperature;
- Contrastive Temperature;
- Distillation Temperature.

Do not use an ambiguous short name in a cross-domain table.

---

# 15. Backend-specific parameters

Record them as:

```text
canonical concept → backend alias
```

Example:

```text
Context Length → n_ctx / num_ctx / context_length
```

Do not create a new concept for every alias.

---

# 16. UI knobs

Every UI variable should carry `UI` until its mapping is known.

Example:

```text
"Creativity" [UI]
```

Only after documentation should it become something like:

```text
Creativity → temperature + top-p
```

if that is genuinely what the product implements.

---

# 17. Presets

A preset does not belong in the mathematical core.

Place it under a section such as:

```text
Empirical operating points
```

with:

- model/family;
- backend;
- date;
- purpose.

Never write a universal “golden setup.”

---

# 18. Ranges

Separate:

1. **mathematical domain**;
2. **backend accepted range**;
3. **empirical useful range**.

Example:

Sampling Temperature:

```math
T>0
```

is the mathematical domain.

A UI limiting it to `0..2` is an implementation constraint.

---

# 19. Reproducibility language

Never write:

> same seed = same result

as a universal law.

Use:

```math
Reproducibility
=f(
weights,
inputs,
seed,
dtype,
kernels,
backend,
hardware,
parallelism,
versions
)
```

---

# 20. Physical cost

Whenever a parameter increases a relevant dimension, try to show the impact on:

- VRAM;
- RAM;
- bandwidth;
- FLOPs;
- latency;
- storage.

Example:

```math
\frac{\partial M_{KV}}{\partial T}
```

is more useful than simply saying “more context uses more VRAM.”

---

# 21. Coupling matrices

Where possible, a table should make explicit:

```text
parameter ↑ → primary effect → secondary effect → failure surface
```

Do not use monotonic arrows when the relationship is non-monotonic.

---

# 22. Observables

Every control section should, where possible, point to a measurable variable.

Ideal:

```math
Control
\rightarrow StatePerturbation
\rightarrow Observable
\rightarrow Output
```

That turns tuning into experimentation.

---

# 23. Evaluation policy

Every important comparative recommendation should be testable according to [17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET](17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md).

Avoid:

- single-seed conclusions;
- benchmark scores without versions;
- leaderboards without a system definition;
- subjective impressions presented as facts.

---

# 24. Security policy

No prompt should be treated as a security boundary.

Security controls should exist in:

- authn/authz;
- sandboxing;
- validation;
- tool scope;
- runtime policy;
- logs/audit;
- rollback.

See [18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET](18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md).

---

# 25. Deprecation

Outdated content should not disappear without explanation when it remains historically useful.

Mark it:

```text
LEGACY
MODEL-SPECIFIC
SUPERSEDED
```

Explain why it stopped being universal.

---

# 26. Changelog discipline

Every structural change should be recorded in [CHANGELOG](CHANGELOG.md).

Minor typo fixes do not require individual entries.

Record:

- date;
- affected files;
- conceptual change;
- breaking rename, if any.

---

# 27. Definition of done for a new datasheet

Before considering it complete:

- [ ] scope defined;
- [ ] computational graph;
- [ ] representation/state;
- [ ] central equations;
- [ ] parameters classified;
- [ ] physical cost where relevant;
- [ ] observables;
- [ ] failure surfaces;
- [ ] cross-links;
- [ ] dated snapshot;
- [ ] references;
- [ ] valid wikilinks;
- [ ] balanced formulas/fences.

---

# 28. Editorial philosophy

The collection should not answer only:

> “which button should I change?”

It should let the reader reconstruct:

```math
\boxed{
Architecture
\rightarrow
State
\rightarrow
Equation
\rightarrow
Control
\rightarrow
Observable
\rightarrow
Output
\rightarrow
Cost
}
```

And across the full lifecycle:

```math
\boxed{
Data
\rightarrow
Training
\rightarrow
Model
\rightarrow
Inference
\rightarrow
Evaluation
\rightarrow
Security/Monitoring
}
```

That is the epistemic contract of the collection.
