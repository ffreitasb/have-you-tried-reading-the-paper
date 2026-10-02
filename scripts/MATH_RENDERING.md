# Mathematical rendering maintenance

The corpus uses GitHub's protected inline math (`$` followed by a backtick,
the TeX expression, a backtick, and `$`) and fenced `math` blocks.
Four `cases` expressions in document 16 use `$$` to preserve TeX row breaks.
The six registry expressions with table pipes use equivalent `\vert` and
`\Vert` commands. Other TeX bodies and all text outside mathematics were
preserved byte for byte in the approved formatting correction.

## Offline checks

```sh
python -m pip install -r scripts/requirements-validation.txt -r scripts/requirements-rendering.txt
python scripts/validate_repository.py
python -m unittest discover -s scripts -p "test_*.py"
python scripts/verify_math_rendering.py
```

`math-preservation.json` records format-independent hashes of the 44 reviewed
documents: external text and ordered TeX bodies. Only the three exact registry
bar aliases normalize for comparison. Whitespace and operators do not normalize.
The source commit is the snapshot before the correction. The validator rejects
content drift, legacy delimiters, unsafe table bars and unreviewed row breaks.
Do not regenerate the manifest automatically to make a failed check pass.
An intentional future content edit requires a reviewed baseline update.

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
unchanged. The living repository contains the corrected formatting.
