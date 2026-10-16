# Mathematical rendering maintenance

The corpus uses GitHub's protected inline math (`$` followed by a backtick,
the TeX expression, a backtick, and `$`) and fenced `math` blocks.
Four `cases` expressions in document 16 use `$$` to preserve TeX row breaks.
The six registry expressions with table pipes use equivalent `\vert` and
`\Vert` commands. An approved follow-up replaces 54 literal less-than operators
with `\lt` in 52 display expressions: the GitHub client otherwise interprets
parts such as `<t` as HTML, dropping terms or failing to render. The exact
whole-body aliases are in `math-aliases.json`; their original and replacement
TeX produced identical MathML. At that formatting-only stage, all other TeX
bodies and all text outside mathematics were preserved byte for byte.
The subsequent bilingual scientific corrections intentionally change content;
they are recorded separately, as described below.

## Offline checks

```sh
python -m pip install -r scripts/requirements-validation.txt -r scripts/requirements-rendering.txt
python scripts/validate_repository.py
python -m unittest discover -s scripts -p "test_*.py"
python scripts/verify_math_rendering.py
```

`math-preservation.json` retains the historical format-independent hashes of
the 44 documents: external text and ordered TeX bodies. Only the three exact registry
bar aliases and the reviewed display aliases normalize for comparison.
No general whitespace or operator normalization is performed.
Its source commit is the snapshot before the formatting correction. The validator rejects
content drift, legacy delimiters, unsafe table bars, literal less-than in display
math and unreviewed row breaks. Inline less-than remains protected by its wrapper.
Do not regenerate the manifest automatically to make a failed check pass.
An intentional content edit requires an explicit, reviewed entry in
`content-revisions.json`. Revisions are applied in order; each file's `before`
fingerprint must match the preceding baseline exactly. The `after` fingerprint
then protects the revised prose and ordered TeX, with the same rendering-safety
checks. Each change names its review findings; the catalog records the technical
subjects and sources. Scientific changes are not added to the equivalent-alias
allowlist. Historical manifests, aliases and archived releases remain intact.

For a new scientific correction, review the bilingual diff and its evidence
first, record the preceding source commit and relevant review identifiers,
then calculate the explicit before/after fingerprints. Recheck every changed
expression in the parsers and browser. Do not infer scientific correctness
from a matching hash or generate a revision solely to silence a failed check.

The CI also compares every formula with the actual Python-Markdown/Arithmatex
HTML output. GitHub API and browser checks are separate delivery evidence;
the offline gate does not claim to test GitHub's JavaScript renderer.

## Future MkDocs integration

Add `scripts/mkdocs_math.py` to `hooks` in the shared MkDocs configuration,
using a path relative to that configuration file. The hook enables generic
Arithmatex and SuperFences with its native math formatter. It converts protected
inline delimiters in memory and escapes the HTML transport of math fences;
the DOM and MathJax receive the original TeX. Front matter and code examples
are excluded. No adapted Markdown files are written.

The PRD 2 publication layer must load MathJax 3 and its fonts/extensions from
local assets, enable the `arithmatex` process class, and handle wide equations
and tables with accessible overflow. The hook supplies parser compatibility;
it does not deploy the site or supply the final reading layout.

The archived v1.0.0 tag, release, citation metadata and Zenodo record remain
unchanged. The living repository contains the formatting corrections and
separately recorded scientific revisions. These gates detect content drift and
rendering corruption; they do not prove every technical statement true.
