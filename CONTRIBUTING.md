# Contributing

[English](CONTRIBUTING.md) · [Português (Brasil)](CONTRIBUTING.pt-BR.md)

This is a bilingual technical reference about the machinery beneath AI interfaces. Corrections, stronger references, reproducible counterexamples, and useful implementation notes belong here. Product announcements need a mechanism to explain before they need a datasheet.

## Evidence and technical standards

Prefer primary papers, formal specifications, source code and official implementation documentation, model cards and technical reports, then reproducible experiments. Secondary explanations can add context; an AI-generated answer is not evidence by itself.

For a technical correction, identify the document and section, quote the current claim, propose the replacement, and provide an authoritative source with a section, equation, or reproducible experiment. Distinguish mathematical facts, architecture assumptions, backend behavior, and empirical recommendations. Do not change a technical claim without evidence. Preserve equations and terminology unless the correction specifically concerns them.

Read the [English conventions](docs/en-US/CONVENTIONS.md) or [Portuguese conventions](docs/pt-BR/CONVENTIONS.md) for the ontology, datasheet structure, provenance tags, and maintenance rules. Those files govern technical content; this guide governs contributions.

## Bilingual editions

Maintain the same filenames and conceptual scope in both editions. A technical correction should update both languages. If you cannot provide the other edition, say so explicitly in the issue or pull request and identify the document needing localization; the maintainer must resolve that gap before merging a change that affects shared technical claims. Natural localization is welcome. Sentence counts and literal translations are not parity checks.

## New categories and datasheets

Open a structural proposal before adding a numbered document or changing the ontology. Explain what changes in representation, objective, inference topology, or state dynamics, which existing document cannot cover it, the evidence, and the impact on both editions and navigation.

A new product/model name is not automatically a new mathematical category.

## Workflow

1. Use the appropriate [issue form](https://github.com/ffreitasb/have-you-tried-reading-the-paper/issues/new/choose) for a correction, reference, translation, or structural proposal. Small, well-evidenced fixes may arrive directly as a pull request.
2. Branch from `main`, keep the change focused, and fill in the pull request template. Explain any citation or release metadata impact.
3. Run the same deterministic checks as CI with Python 3.12 or newer:

   ```sh
   python -m venv .venv
   # Activate .venv using your shell's standard activation command.
   python -m pip install -r scripts/requirements-validation.txt
   python scripts/validate_repository.py
   python -m unittest discover -s scripts -p "test_*.py"
   cffconvert --validate -i CITATION.cff
   ```

The validator is read-only. It checks structure, local links and deterministic fragments, text hygiene, citation metadata, and the Zenodo mirror when present. External references have a separate weekly/manual workflow with a downloadable report; network failures do not establish that a technical claim is wrong.

Do not commit editor state, agent memory, credentials, or local build output. Report active security problems privately through the [security policy](SECURITY.md). Community participation follows the [code of conduct](CODE_OF_CONDUCT.md).

## AI assistance, attribution, and license

Disclose material AI assistance in the pull request: which tool assisted which work, and how you checked the result. You remain responsible for evidence, accuracy, rights, and the final contribution. See the project's [provenance disclosure](PROVENANCE.md). AI systems are not academic authors in citation metadata.

By submitting original material for inclusion, you agree to its distribution under [CC BY-SA 4.0](LICENSE). Identify third-party material and its source and license; do not submit material you lack the right to contribute. Preserve appropriate attribution. Repository versions and DOI metadata are maintained by the accountable publisher; published release tags remain immutable.
