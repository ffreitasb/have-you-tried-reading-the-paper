<div align="center">

# have-you-tried-reading-the-paper

### An unnecessarily thorough explanation of what that button actually does.

**No magic. Just tensors, equations, and papers you probably should have read.**

[**English**](README.md) · [**Português (Brasil)**](README.pt-BR.md)

[![License: CC BY-SA 4.0](https://img.shields.io/badge/license-CC%20BY--SA%204.0-1769aa)](LICENSE)
![Languages](https://img.shields.io/badge/languages-English%20%7C%20Portugu%C3%AAs-0969da)
![Status](https://img.shields.io/badge/status-living%20reference-1f883d)

</div>

---

> **If a UI gives you a slider called _temperature_, _guidance_, _context_, _rank_, _steps_, or _strength_, you should probably know which equation you are touching before copying somebody else's “best settings.”**

Most AI interfaces are intentionally good at hiding the machinery.

That is useful if you just want the model to do something.

It is considerably less useful if you want to understand **why it did that**, how to manipulate the result systematically, what the actual trade-offs are, what is happening in memory, or why changing one innocent-looking parameter just detonated quality, latency, VRAM usage, temporal coherence, retrieval recall, or all five at once.

This repository is the layer **under the buttons**.

It is an open technical knowledge base for understanding modern foundation models from the inside out: representations, tensors, objectives, architectures, state, sampling, numerical solvers, memory, training, evaluation, security, agents, retrieval, multimodality, and the runtime physics that eventually turns all of that elegant mathematics into heat.

No oracle. No magic prompt. No “AI secrets.”

Just models.

---

## Why this exists

There is an absurd amount of excellent material about AI.

There is also an absurd amount of it scattered across papers, source code, framework documentation, implementation notes, benchmark repositories, issue trackers, model cards, and discussions written by people who quite reasonably assume you already know what the previous thirty acronyms mean.

The hard part is often not finding **an** explanation.

It is building the **connected mental model** that tells you how the pieces relate.

This project tries to make that model explicit.

Instead of:

```text
parameter -> vibes -> try another value
```

the target is:

```text
architecture
    -> state
        -> equation
            -> control
                -> perturbation
                    -> observable
                        -> output
                            -> physical cost
```

The goal is not to make probabilistic systems look deterministic. They are not.

The goal is to make the **mechanisms, controllable variables, hidden state, dependencies, and failure surfaces legible enough to engineer around them**.

---

## What you will find here

The material spans the complete model lifecycle rather than treating “AI” as a synonym for chatbots.

| Layer | What it covers |
|---|---|
| **Unified theory** | Representations, generative objectives, backbones, conditioning, inference operators, state, decoding, modality topology |
| **Model families** | LLMs, code models, image, video, audio/speech, 3D, multimodal/omni, time-series/tabular, graph foundation models |
| **System components** | Agents, retrieval/reranking, reward models, verifiers, judges, world models, VLA/embodied AI |
| **Lifecycle** | Pretraining, post-training, alignment, PEFT, distillation, model merging, evaluation, benchmarking, experimentation |
| **Execution** | Quantization, KV cache, VRAM/RAM, offload, bandwidth, batching, prefill/decode, local inference economics |
| **Trust boundaries** | Robustness, prompt injection, poisoning, supply chain, agent permissions, runtime controls, failure modes |
| **Knowledge governance** | Conventions, canonical terminology, parameter registry, semantic collisions, changelog |

And yes, there are equations.

Quite a few of them.

---

## Start here

If you want the complete map, start with the language-specific index:

### English
**[Open the English knowledge index →](docs/en-US/00_README_INDEX.md)**

### Português (Brasil)
**[Abrir o índice técnico em português →](docs/pt-BR/00_README_INDEX.md)**

If you would rather ignore the suggested order and immediately crawl into a specific rabbit hole — a respectable decision — here are some shortcuts:

| You want to understand... | Read |
|---|---|
| the common mathematical skeleton behind modern AI | [`01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md`](docs/en-US/01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md) |
| what an LLM is actually doing between prompt and token | [`02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md`](docs/en-US/02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md) |
| code completion vs. agentic coding | [`03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md`](docs/en-US/03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md) |
| diffusion, flow matching, DiTs, CFG, schedulers and solvers | [`04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md`](docs/en-US/04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md) |
| why video generation makes your GPU reconsider its life choices | [`05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md`](docs/en-US/05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md) |
| audio generation, TTS, ASR and speech models | [`06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md`](docs/en-US/06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md) |
| AI-generated 3D representations | [`07_3D_GENERATION_REPRESENTATION_DATASHEET.md`](docs/en-US/07_3D_GENERATION_REPRESENTATION_DATASHEET.md) |
| tool calling, agents and action control | [`08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md`](docs/en-US/08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md) |
| why your 9 GB model does not necessarily need only 9 GB | [`09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md`](docs/en-US/09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md) |
| VLMs, multimodal fusion and omni models | [`10_MULTIMODAL_VLM_OMNI_DATASHEET.md`](docs/en-US/10_MULTIMODAL_VLM_OMNI_DATASHEET.md) |
| embeddings, vector search, RAG retrieval and rerankers | [`11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md`](docs/en-US/11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md) |
| reward models, verifiers and LLM-as-a-judge | [`12_REWARD_VERIFIER_JUDGE_DATASHEET.md`](docs/en-US/12_REWARD_VERIFIER_JUDGE_DATASHEET.md) |
| world models, VLA and embodied AI | [`13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md`](docs/en-US/13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md) |
| time-series and tabular foundation models | [`14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md`](docs/en-US/14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md) |
| graph foundation models | [`15_GRAPH_FOUNDATION_MODELS_DATASHEET.md`](docs/en-US/15_GRAPH_FOUNDATION_MODELS_DATASHEET.md) |
| how models become the weights you eventually download | [`16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md`](docs/en-US/16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md) |
| how to benchmark without accidentally benchmarking your own assumptions | [`17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md`](docs/en-US/17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md) |
| security, robustness and failure surfaces | [`18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md`](docs/en-US/18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md) |
| what a parameter name actually means in context | [`19_PARAMETER_GLOSSARY_AND_REGISTRY.md`](docs/en-US/19_PARAMETER_GLOSSARY_AND_REGISTRY.md) |

---

## Repository structure

```text
.
├── README.md / README.pt-BR.md
├── LICENSE / CITATION.cff / .zenodo.json
├── PROVENANCE.md / PROVENANCE.pt-BR.md
├── CONTRIBUTING.md / CONTRIBUTING.pt-BR.md
├── CODE_OF_CONDUCT.md / SECURITY.md
├── docs/
│   ├── en-US/              # 00–19, CONVENTIONS.md, CHANGELOG.md
│   └── pt-BR/              # 00–19, CONVENTIONS.md, CHANGELOG.md
├── scripts/                # Local validation and regression checks
└── .github/                # CI, contribution templates, CODEOWNERS
```

Both language trees are intended to remain structurally equivalent.

The English version is the repository default. The Brazilian Portuguese edition is maintained as a first-class version, not as an afterthought hidden behind a machine-translated paragraph somewhere near the bottom of the README.

---

## The editorial rules

This repository has a few opinions.

### 1. Architecture is not behavior

A model family, its weights, its training procedure, its inference algorithm, its runtime, and the UI exposing them are **different layers**.

If two things share a slider name, that does not mean they share a mechanism.

---

### 2. A useful analogy is not an equation

Metaphors are welcome. False equivalences are not.

If two controls produce behavior that _feels_ similar but act on different mathematical objects, the distinction matters.

---

### 3. “Best settings” are usually missing half the sentence

Best for:

- which model?
- which backend?
- which quantization?
- which context length?
- which objective?
- which dataset?
- which metric?
- which hardware?
- which failure mode are we accepting?

A preset is an **operating point**, not a law of nature.

---

### 4. Model size is not a sufficient explanation

Parameter count alone tells you surprisingly little once MoE, quantization, KV cache, context length, multimodal tokens, sparsity, offload, memory bandwidth, and active parameters enter the room.

The hardware eventually sends the invoice.

---

### 5. Primary sources beat folklore

Papers, specifications, source code, official documentation, model cards, and reproducible experiments take precedence over “someone on Discord said 0.7 looks better.”

Discord may still be right.

It just does not get diplomatic immunity from evidence.

---

## Knowledge, not mysticism

This project deliberately avoids presenting AI systems as mystical black boxes.

They are extraordinarily complex statistical machines.

That is already interesting enough.

You do not need to pretend there is a ghost in the matrix multiplication.

Understanding the machinery does **not** make these systems deterministic, perfectly interpretable, or fully predictable. It gives you something much more useful:

**better hypotheses.**

And better hypotheses lead to better experiments.

---

## Who this is for

You will probably enjoy this repository if you:

- use local or frontier models and want to understand what happens below the frontend;
- tune inference parameters and would like to stop doing it entirely by folklore;
- work with ML, data, software, infrastructure, security, robotics, retrieval, or generative media;
- learn better from equations, system diagrams, trade-offs, and causal relationships;
- are perfectly willing to read the paper, but would appreciate knowing **which paper and why** first.

You do **not** need a graduate degree in machine learning.

You do need some tolerance for math and a mild suspicion of magical explanations.

---

## How to use this repository

Three reasonable strategies:

**Read it as a book.**  
Start at the [English index](docs/en-US/00_README_INDEX.md) and follow the suggested progression.

**Use it as a reference manual.**  
Jump directly to a model family, mechanism, or parameter when you need it.

**Use it as a lab companion.**  
Keep the relevant datasheet open next to llama.cpp, KoboldCpp, LM Studio, Ollama, SillyTavern, ComfyUI, your training stack, your benchmark harness, or whatever new frontend has invented another name for a parameter that already had one.

---

## A living reference

AI documentation has an inconvenient property: it starts aging approximately five minutes after publication.

The repository therefore separates, whenever possible:

- relatively stable mathematical mechanisms;
- architecture-dependent behavior;
- backend implementation details;
- empirical heuristics;
- dated technology snapshots.

The goal is to update the layer that changed instead of rewriting the entire mental model every time a new checkpoint trends for forty-eight hours.

See the language-specific [`CHANGELOG.md`](docs/en-US/CHANGELOG.md) and [`CONVENTIONS.md`](docs/en-US/CONVENTIONS.md) for how the knowledge base evolves.

---

## Contributing

Corrections, better references, reproducible counterexamples, clearer derivations, implementation notes, and genuinely useful additions are welcome.

Before proposing a brand-new datasheet because a model has a shiny new name, please check the project conventions first:

**[Read `CONVENTIONS.md` →](docs/en-US/CONVENTIONS.md)**

A new product name is not automatically a new mathematical category.

Marketing departments have enough repositories already.

When contributing to one language, keeping the equivalent document in the other language synchronized is strongly encouraged.

**[Contribution guide →](CONTRIBUTING.md)** · [Code of conduct](CODE_OF_CONDUCT.md) · [Security policy](SECURITY.md)

---

## Languages

- **English — default:** [`docs/en-US/`](docs/en-US/)
- **Português (Brasil):** [`docs/pt-BR/`](docs/pt-BR/)
- **README em português:** [`README.pt-BR.md`](README.pt-BR.md)

The two editions aim for **conceptual equivalence**, not awkward sentence-by-sentence translation.

Technical language deserves better than that.

---

## License

Unless otherwise noted, the original content in this repository is licensed under **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)**.

You may share, adapt, translate, remix, and reuse the material — including commercially — provided that you give appropriate attribution, indicate changes when applicable, and distribute adaptations under the same license.

**Copyright © 2026 Felipe Freitas Braga.**

Third-party quotations, cited papers, trademarks, linked materials, figures, screenshots, and other externally sourced elements remain subject to their respective rights and licenses.

**[Read the full license →](LICENSE)**

---

## Citation

If this repository materially contributes to academic, scientific, educational, or technical work, please cite it.

The repository includes a machine-readable [`CITATION.cff`](CITATION.cff), which GitHub can expose through **Cite this repository** and render into standard citation formats. A DOI-backed archived citation is planned for a future release through Zenodo.

**[Citation metadata →](CITATION.cff)**

---

## AI-assisted production and provenance

This project is **human-directed and AI-assisted**.

The original late-2025 datasheets were predominantly authored by Felipe Freitas Braga and later reviewed and refined with AI assistance. The 2026 SOTA++ reconstruction and expansion used OpenAI ChatGPT extensively for research synthesis, technical drafting, restructuring, review, English localization, and quality assurance, while the project architecture, standards, scope, technical judgment, final editorial decisions, and publication responsibility remained human-controlled.

The AI contribution is intentionally disclosed rather than quietly hidden behind the commit history. It is material to how the current knowledge base was produced, but the AI system is not listed as an academic author because it cannot assume authorship responsibilities or accountability.

**[Read the full provenance statement →](PROVENANCE.md)**

---

## Open knowledge

This project exists to make difficult technical knowledge easier to access, connect, inspect, question, and redistribute.

Knowledge compounds when people can actually reach it.

If something here helps you understand the machinery well enough to explain it better, test it harder, correct it, or build something useful from it, then the repository is doing its job.

---

<div align="center">

### Have you tried reading the paper?

**No magic. Just tensors.**

</div>
