---
title: Changelog — Foundation Model Engineering Datasheets
aliases: [Datasheet Changelog]
tags: [ai, reference, changelog, knowledge-management]
updated: 2026-10-01
---

# Changelog

> Record of structural and conceptual changes to the collection. Trivial typographical fixes may not appear here.

---

# 2026-10-01 — Lifecycle & Governance Layer

## Added

### `16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md`

New lifecycle layer covering:

- data mixture/curation;
- objectives;
- optimizer mechanics;
- full fine-tuning;
- SFT;
- reward/preference optimization;
- PPO/DPO/KTO/ORPO families;
- GRPO/DAPO/GSPO;
- RLVR;
- LoRA/QLoRA/DoRA;
- distillation;
- model merging;
- pruning;
- continual learning;
- training memory/compute.

### `17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md`

New evidence-engineering layer:

- System Under Test definition;
- metric/harness separation;
- uncertainty;
- paired experiments;
- bootstrap;
- benchmark contamination/saturation;
- judge bias;
- runtime metrics;
- local-model Pareto fronts;
- regression suites.

### `18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md`

New cross-cutting risk/control layer:

- prompt injection;
- RAG/memory poisoning;
- supply chain;
- agent security;
- authorization;
- ACS runtime control;
- adversarial robustness;
- local AI attack surface;
- observability/incident response.

### `19_PARAMETER_GLOSSARY_AND_REGISTRY.md`

Canonical data dictionary:

- provenance tags;
- symbol conventions;
- parameter collisions;
- canonical names;
- backend aliases;
- domain registries;
- units;
- deprecation/semantic-drift rules.

### `CONVENTIONS.md`

Added editorial and maintenance rules to prevent arbitrary taxonomic growth.

### `CHANGELOG.md`

Created this history.

## Changed

### `00_README_INDEX.md`

- expanded tree to 00–19;
- added META / MODEL / SYSTEM / LIFECYCLE / RUNTIME layers;
- updated reading guide;
- expanded provenance tags.

### `01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`

- added the distinction between the **execution model tuple** and the **lifecycle envelope**;
- training/evaluation/security now wrap the model ontology instead of being treated as “model types.”

---

# 2026-10-01 — Foundation Model Expansion

## Added

- `10_MULTIMODAL_VLM_OMNI_DATASHEET.md`
- `11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md`
- `12_REWARD_VERIFIER_JUDGE_DATASHEET.md`
- `13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md`
- `14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md`
- `15_GRAPH_FOUNDATION_MODELS_DATASHEET.md`

## Changed

- `01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`: expanded representation/objective/backbone axes.
- `02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md`: incorporated masked/diffusion/parallel language generation.
- `06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md`: incorporated ASR/speech understanding.
- `09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md`: incorporated multimodal, retrieval, and parallel-language cost models.
- `00_README_INDEX.md`: expanded the collection and consolidated cross-links.

---

# 2026-10-01 — SOTA++ Rebuild

The collection was rebuilt from the legacy 2025 datasheets.

Central change:

```text
before:
  Transformer vs Diffusion

now:
  Representation
  × Objective
  × Backbone
  × Conditioning
  × Inference
  × Persistent State
  × Decoder
  × Modality Topology
```

Major corrections:

- seed is no longer treated as a guarantee of determinism;
- CFG is no longer treated as mathematically equivalent to temperature;
- sampler and scheduler were separated;
- diffusion and flow matching were separated;
- Transformer is no longer treated as synonymous with autoregression;
- KV/cache/runtime received explicit physical modeling;
- 3D now starts from representation;
- agents are treated as control systems with policy/tool/environment;
- model snapshots were separated from the mathematical core.

---

# Legacy source set — 2025-12-04 / 2025-12-05

The original materials that motivated the rebuild included datasheets for:

- LLMs;
- code generation;
- image diffusion;
- video generation;
- audio generation;
- 3D generation;
- action models;
- a generative-AI GUT.

They remain historically useful as a snapshot of the previous mental model, but have been superseded by the current SOTA++ collection.
