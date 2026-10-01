---
title: Changelog — Foundation Model Engineering Datasheets
aliases: [Datasheet Changelog]
tags: [ai, referencia, changelog, knowledge-management]
updated: 2026-10-01
---

# Changelog

> Registro de mudanças estruturais/conceituais da coleção. Correções tipográficas triviais podem não aparecer aqui.

---

# 2026-10-01 — Lifecycle & Governance Layer

## Added

### `16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md`

Nova camada de lifecycle cobrindo:

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

Nova camada de evidence engineering:

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

Nova camada transversal de risk/control:

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

Data dictionary canônico:

- provenance tags;
- symbol conventions;
- parameter collisions;
- canonical names;
- backend aliases;
- domain registries;
- units;
- deprecation/semantic drift rules.

### `CONVENTIONS.md`

Adicionadas regras editoriais e de manutenção para impedir crescimento taxonômico arbitrário.

### `CHANGELOG.md`

Criado este histórico.

## Changed

### `00_README_INDEX.md`

- tree expandida para 00–19;
- adicionadas camadas META / MODEL / SYSTEM / LIFECYCLE / RUNTIME;
- guia de leitura atualizado;
- provenance tags expandidas.

### `01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`

- adicionada distinção entre **model tuple de execução** e **lifecycle envelope**;
- training/evaluation/security passam a envolver a ontologia de modelo em vez de serem “tipos de modelo”.

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

- `01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`: representation/objective/backbone axes ampliados.
- `02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md`: masked/diffusion/parallel language generation incorporados.
- `06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md`: ASR/speech understanding incorporados.
- `09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md`: multimodal, retrieval e parallel-language cost models incorporados.
- `00_README_INDEX.md`: coleção expandida e cross-links consolidados.

---

# 2026-10-01 — SOTA++ Rebuild

A coleção foi reconstruída a partir dos datasheets legacy de 2025.

Mudança central:

```text
antes:
  Transformer vs Diffusion

agora:
  Representation
  × Objective
  × Backbone
  × Conditioning
  × Inference
  × Persistent State
  × Decoder
  × Modality Topology
```

Principais correções:

- seed deixou de ser tratado como garantia de determinismo;
- CFG deixou de ser tratado como equivalente matemático de temperature;
- sampler e scheduler foram separados;
- diffusion e flow matching foram separados;
- Transformer deixou de ser sinônimo de autoregression;
- KV/cache/runtime receberam modelagem física explícita;
- 3D passou a começar pela representação;
- agents passaram a ser control systems com policy/tool/environment;
- snapshots de modelos foram separados do núcleo matemático.

---

# Legacy source set — 2025-12-04 / 2025-12-05

Os materiais originais que motivaram a reconstrução incluíam datasheets de:

- LLM;
- code generation;
- image diffusion;
- video generation;
- audio generation;
- 3D generation;
- action models;
- GUT da IA generativa.

Eles permanecem historicamente úteis como fotografia do modelo mental anterior, mas foram substituídos pela coleção SOTA++ atual.
