"""MkDocs hook for the canonical GitHub math syntax (no source-file writes).

PRD 2 integration: add this file to `hooks` in the shared MkDocs configuration.
MathJax 3 and all its assets must be served locally by the publication layer.
"""

import sys
from pathlib import Path

# MkDocs loads file hooks by path; the adjacent shared module must also resolve
# when the CLI is launched outside the checkout (e.g. with --config-file).
_directory = str(Path(__file__).resolve().parent)
if _directory not in sys.path:
    sys.path.insert(0, _directory)
from math_rendering import to_arithmatex


def on_config(config, **kwargs):
    from pymdownx.arithmatex import arithmatex_fenced_format

    extensions = config["markdown_extensions"]
    for name in ("pymdownx.arithmatex", "pymdownx.superfences"):
        if name not in extensions:
            extensions.append(name)
    configs = config["mdx_configs"]
    configs.setdefault("pymdownx.arithmatex", {})["generic"] = True
    fences = configs.setdefault("pymdownx.superfences", {}).setdefault("custom_fences", [])
    if any(fence.get("name") == "math" for fence in fences):
        raise ValueError("math fence already configured; use the canonical hook once")
    fences.append({"name": "math", "class": "arithmatex", "format": arithmatex_fenced_format(mode="generic")})
    return config


def on_page_markdown(markdown, **kwargs):
    return to_arithmatex(markdown)
