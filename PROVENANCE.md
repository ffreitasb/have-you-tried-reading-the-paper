# Project Provenance and AI-Assistance Disclosure

## Why this file exists

This repository documents not only **what** it contains, but also **how the knowledge base was produced**.

That matters for two reasons:

1. technical work should be transparent about the tools and processes that materially shaped it; and
2. a project about understanding AI systems from the inside should probably not pretend that AI had nothing to do with producing it.

The short version:

> **This is a human-directed, AI-assisted technical knowledge project.**

Felipe Freitas Braga is the human author, editor, maintainer, and accountable publisher of the repository. OpenAI ChatGPT was used extensively as a research, synthesis, drafting, restructuring, review, localization, and quality-assurance assistant during the 2026 reconstruction and expansion of the material. Subsequent repository engineering and scientific review used OpenAI Codex, including GPT-6 Astra review and correction passes, as described below.

---

## Historical provenance

### Original material — late 2025

The earliest datasheets were created for personal study and stored in a private Obsidian knowledge base.

Those original documents were **predominantly authored by Felipe Freitas Braga**, with AI used mainly to review, refine, challenge, and improve material that had already been structured and written by the human author.

The original goal was practical: expose the mathematical and computational machinery hidden behind friendly AI interfaces, especially the parameters and state variables that determine model behavior during inference.

### SOTA++ reconstruction and expansion — October 2026

The current repository is a much larger reconstruction of that original knowledge base.

During this phase, the workflow became substantially more AI-assisted. OpenAI ChatGPT contributed materially to:

- research assistance and source discovery;
- synthesis across papers, specifications, source code, model documentation, and implementation notes;
- technical drafting and redrafting;
- mathematical exposition and notation;
- cross-domain comparison and taxonomy design;
- structural normalization across datasheets;
- terminology consistency;
- identification of conceptual gaps and outdated assumptions;
- English localization of the Portuguese edition;
- editorial review and mechanical quality assurance.

The human contribution remained decisive and non-delegated in:

- defining the project's purpose, scope, philosophy, and editorial voice;
- deciding what deserved to be a distinct model/system category;
- defining the ontology and document architecture;
- setting the technical depth and evidence standards;
- directing the research and revision process;
- challenging, correcting, accepting, rejecting, and restructuring AI-generated material;
- deciding the final wording, organization, licensing, and publication model;
- taking responsibility for the published result.

The 2026 expansion was therefore neither "written entirely by AI" nor "written entirely by a human with occasional autocomplete." It was a **collaborative production workflow in which the human supplied direction, judgment, standards, domain context, and final accountability, while the AI supplied substantial research, synthesis, drafting, and editorial labor**.

Any attempt to compress that into a fake percentage would imply more precision than the process supports.

---

### Repository engineering and mathematical rendering — October 2026

OpenAI Codex assisted with repository organization, portable navigation, contribution and governance documents, citation and archival integration, automated validation, and investigation and correction of mathematical rendering failures on GitHub and in temporary MkDocs builds.

The rendering corrections changed delimiters and explicitly reviewed equivalent TeX spellings. Their preservation checks kept presentation changes separate from changes in scientific meaning. The archived v1.0.0 release was not rewritten.

### Scientific review and bilingual corrections — October 9–16, 2026

At the maintainer's request, GPT-6 Astra agents working in Codex reviewed all 44 documents across the English and Brazilian Portuguese editions. The review covered technical claims, equations and their domains, tensor dimensions, assumptions, sources, and conceptual consistency within and between the editions. It combined primary-source checks with targeted calculations and reproducible counterexamples.

The maintainer then authorized corrections. The completed correction cycle addressed 47 consolidated findings in the corpus and one in the contribution guide, and clarified 46 conditional or editorial records. These are findings from that review, not an exhaustive count of every possible error. Material questions of intent were referred to the maintainer: the contrastive example retains its formula and is identified as decoupled contrastive learning (DCL); the damaged template comparison is replaced by prose about serialization compatibility without requiring byte-identical training and inference inputs.

Codex assisted with implementing the paired corrections, reviewing their diffs, recording exact before/after edits, and running integrity and rendering checks. The October 16 verification covered 22 regression tests and 3,025 mathematical expressions through the native parser, temporary MkDocs builds, and the real GitHub rendering component in disposable browser fixtures, with representative desktop/mobile inspection. A browser fixture verifies candidate rendering; it does not establish that those changes have been published or that a production documentation site is deployed.

Scientific assessment and mechanical verification remain separate. Matching hashes, valid MathML, and successful tests do not prove a technical claim true. This was AI-assisted review under human direction, not independent human peer review or a reproduction of every cited benchmark and training result. The maintainer retains editorial and publication responsibility; these checks do not imply that the maintainer personally rederived every equation.

The language-specific [changelog](docs/en-US/CHANGELOG.md) records the conceptual corrections. The [content-revision register](scripts/content-revisions.json) records reviewed before/after fingerprints, review identifiers, and sources while retaining the historical formatting baseline. See [mathematical rendering maintenance](scripts/MATH_RENDERING.md) for the scope of those checks.

---

## AI systems used

The recorded tools and model configurations have distinct roles in the project's history:

- **OpenAI ChatGPT, GPT-5.6 Sol:** the initial October 2026 reconstruction, expansion, and localization.
- **OpenAI Codex:** subsequent repository engineering, rendering corrections, implementation, and verification.
- **GPT-6 Astra in Codex:** scientific review and correction passes across both language editions in October 2026.

Model names, configurations, and product behavior can change over time. These names identify the recorded production and review phases; they are not runtime dependencies of the repository and do not imply that every task used the same model.

---

## Why the AI system is not listed as an academic author

The use of AI is disclosed prominently, but the AI system is **not listed as an author in `CITATION.cff`**.

Authorship is not merely a measure of how many words or drafts a contributor produced. In scholarly and technical contexts, authorship also implies responsibility, accountability, the ability to approve a final work, answer for errors, manage conflicts of interest, and stand behind the published claims.

An AI system cannot meaningfully assume those obligations.

Accordingly:

- AI assistance is disclosed as a **material production contribution**;
- the human maintainer remains the **accountable author and publisher**;
- the repository does not hide, minimize, or misrepresent the role of AI in its creation.

---

## Source and evidence policy

AI-assisted synthesis does not make a claim self-validating.

The project therefore prioritizes, where practical:

1. primary research papers;
2. formal specifications and standards;
3. source code and implementation documentation;
4. official model cards and technical reports;
5. reproducible experiments and benchmark methodology;
6. secondary explanations only when they add useful context.

Readers should still verify important claims against the cited primary sources, especially in fast-moving areas where implementation details and model behavior can change quickly.

The repository is a technical map, not an oracle.

---

## Translation and localization provenance

The English edition is not a literal machine translation of the Portuguese edition.

It was produced through AI-assisted **technical localization**, preserving equations, structure, scope, and conceptual content while rewriting prose so it reads naturally to a technical English-speaking audience.

The target is conceptual equivalence, not sentence-by-sentence lexical symmetry.

---

## Licensing scope

Unless otherwise noted, the repository's original content is made available under the **Creative Commons Attribution-ShareAlike 4.0 International license (CC BY-SA 4.0)**.

The license applies only to rights the licensor is legally able to grant. Third-party quotations, cited papers, trademarks, linked materials, screenshots, figures, or other externally sourced elements remain subject to their respective rights and licenses.

See [`LICENSE`](LICENSE) for the full license text.

---

## Citation

If this repository materially contributes to academic, scientific, educational, or technical work, please cite it using the metadata in [`CITATION.cff`](CITATION.cff).

Zenodo archival and DOI-based citation are implemented. The immutable v1.0.0 release is published in the [Zenodo archive](https://zenodo.org/records/23092486) with DOI [10.5281/zenodo.23092486](https://doi.org/10.5281/zenodo.23092486), which identifies that exact version. The [project DOI](https://doi.org/10.5281/zenodo.23092485) represents all versions.

The living reference contains formatting and scientific corrections made after v1.0.0. They do not retroactively change that archive or its citation metadata. When referring to material from `main`, also record the commit SHA or a permalink identifying the revision used; the v1.0.0 DOI alone does not identify later corrections.

---

## Contact

For project-related contact:

**Felipe Freitas Braga**  
`contact@ffreitasb.cc`

---

> Transparency is cheaper than pretending the tool did not help.
