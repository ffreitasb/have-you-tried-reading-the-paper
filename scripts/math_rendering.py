"""Context-aware mathematical markup and format-independent preservation checks.

Canonical source: protected GitHub inline math, math fences, and four reviewed
cases blocks using $$. Code examples and YAML front matter are never adapted.
"""

from __future__ import annotations

import hashlib
import html
import json
import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path

REGISTRY = "19_PARAMETER_GLOSSARY_AND_REGISTRY.md"
TRAINING = "16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md"
ALIASES = {
    r"|\mathcal V|": r"\vert\mathcal V\vert",
    r"p(s_{t+1}|s_t,a_t)": r"p(s_{t+1}\vert s_t,a_t)",
    r"z/\|z\|": r"z/\Vert z\Vert",
}
CASES = {
    "\nm_t=\n\\begin{cases}\n0 & prompt\\\\\n1 & answer\n\\end{cases}\n",
    "\nR(y)=\n\\begin{cases}\n1 & verified\\\\\n0 & fail\n\\end{cases}\n",
}


@dataclass(frozen=True)
class Formula:
    start: int
    end: int
    body: str
    kind: str
    syntax: str
    line: int


def formulas(text: str) -> list[Formula]:
    """Scan explicit math outside code/front matter; reject ambiguous structures.

    This is deliberately restricted to the reviewed corpus conventions. Display
    delimiters are standalone and unindented; inline math cannot cross a line.
    Unexpected/unclosed delimiters cause failure rather than a guessed rewrite.
    """
    result = []
    lines = text.splitlines(keepends=True)
    offset, index = 0, 0
    if lines and lines[0].strip() == "---":
        index = next((i + 1 for i in range(1, len(lines)) if lines[i].strip() == "---"), 0)
        if not index:
            raise ValueError("unclosed front matter")
        offset = sum(map(len, lines[:index]))
    while index < len(lines):
        line = lines[index]
        fence = re.match(r"^ {0,3}(`{3,}|~{3,})(.*?)[ \t]*\n?$", line)
        display = line.rstrip("\n") in (r"\[", "$$")
        if fence or display:
            is_math = display or fence[2] == "math"
            if fence:
                marker = fence[1]
                close = re.compile(r"^ {0,3}" + re.escape(marker[0]) + "{" + str(len(marker)) + r",}[ \t]*\n?$")
                if is_math and line != "```math\n":
                    raise ValueError(f"line {index + 1}: unexpected math fence")
                syntax = "fence"
            else:
                marker = line.rstrip("\n")
                close = re.compile(re.escape(r"\]" if marker == r"\[" else "$$") + r"\n?$")
                syntax = "legacy-display" if marker == r"\[" else "dollars"
            end_index = next((i for i in range(index + 1, len(lines)) if close.fullmatch(lines[i])), None)
            if end_index is None:
                raise ValueError(f"line {index + 1}: unclosed {marker}")
            chunk = "".join(lines[index:end_index + 1])
            if is_math:
                # Include boundary newlines so conversion proves byte preservation.
                body = "\n" + "".join(lines[index + 1:end_index])
                if not body.strip() or "\n\n" in body or re.search(r"\\[\[\]]|\$\$|```", body):
                    raise ValueError(f"line {index + 1}: unexpected display body")
                result.append(Formula(offset, offset + len(chunk.rstrip("\n")), body, "display", syntax, index + 1))
            offset += len(chunk)
            index = end_index + 1
            continue
        # Indented code is outside this corpus' math conventions.
        if line.startswith("    ") or line.startswith("\t"):
            offset += len(line)
            index += 1
            continue
        pos = 0
        while pos < len(line):
            if line.startswith("$`", pos) or line.startswith(r"\(", pos):
                protected = line.startswith("$`", pos)
                closing = "`$" if protected else r"\)"
                end = line.find(closing, pos + 2)
                if end < 0:
                    raise ValueError(f"line {index + 1}: unclosed inline math")
                body = line[pos + 2:end]
                if not body or "`" in body or "\n" in body or re.search(r"\\[()\[\]]|\$`", body):
                    raise ValueError(f"line {index + 1}: unexpected inline body")
                result.append(Formula(offset + pos, offset + end + 2, body, "inline", "protected" if protected else "legacy-inline", index + 1))
                pos = end + 2
            elif line[pos] == "`":
                match = re.match(r"`+", line[pos:])
                ticks = match[0]
                end = line.find(ticks, pos + len(ticks))
                if end < 0:
                    raise ValueError(f"line {index + 1}: unsupported multiline/unclosed code span")
                pos = end + len(ticks)
            elif any(line.startswith(token, pos) for token in (r"\)", r"\[", r"\]", "`$", "$$")):
                raise ValueError(f"line {index + 1}: stray math delimiter")
            else:
                pos += 1
        offset += len(line)
        index += 1
    return result


def replace_formulas(text: str, items: list[Formula], replacements: list[str]) -> str:
    if len(items) != len(replacements):
        raise ValueError("replacement count differs")
    chunks, end = [], 0
    for item, replacement in zip(items, replacements):
        chunks.extend((text[end:item.start], replacement))
        end = item.end
    return "".join(chunks) + text[end:]


def convert_legacy(text: str, filename: str) -> str:
    """One-shot conversion; only the six reviewed table aliases are permitted."""
    items = formulas(text)
    replacements = []
    for item in items:
        if not item.syntax.startswith("legacy-"):
            raise ValueError("conversion requires original legacy markup")
        body = ALIASES.get(item.body, item.body) if filename == REGISTRY else item.body
        if item.kind == "inline":
            replacements.append("$`" + body + "`$")
        elif item.body in CASES and filename == TRAINING:
            replacements.append("$$" + body + "$$")
        elif re.search(r"\\\\(?=\n)", item.body):
            raise ValueError("unreviewed row-break exception")
        else:
            replacements.append("```math" + body + "```")
    return replace_formulas(text, items, replacements)


def to_arithmatex(text: str) -> str:
    items = formulas(text)
    replacements = []
    for item in items:
        if item.syntax == "protected":
            replacements.append(r"\(" + item.body + r"\)")
        elif item.syntax == "fence":
            # PyMdown's native fence formatter returns raw HTML. Escape only its
            # transport input, so DOM text and MathJax receive the original TeX.
            replacements.append("```math" + html.escape(item.body, quote=False) + "```")
        else:
            replacements.append(text[item.start:item.end])
    return replace_formulas(text, items, replacements)


def fingerprint(text: str, filename: str) -> dict:
    """Hash external bytes and each TeX body independent of approved wrappers.

    Resolve only the exact registry aliases back to their original spellings.
    No whitespace, Unicode, operator, or prose normalization is performed.
    """
    items = formulas(text)
    outside = replace_formulas(text, items, ["\0" + x.kind + "\0" for x in items])
    inverse = {v: k for k, v in ALIASES.items()} if filename == REGISTRY else {}
    digest = lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest()
    bodies = [[x.kind, inverse.get(x.body, x.body)] for x in items]
    return {"outside_sha256": digest(outside), "tex_sha256": digest(json.dumps(bodies, ensure_ascii=False)),
            "inline": sum(x.kind == "inline" for x in items), "display": sum(x.kind == "display" for x in items)}


def check_corpus(root: Path) -> list[str]:
    manifest_path = root / "scripts/math-preservation.json"
    if not manifest_path.exists():
        return ["missing math preservation manifest"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors = []
    for relative, baseline in manifest["files"].items():
        try:
            path = root / relative
            text = path.read_bytes().decode("utf-8")
            items = formulas(text)
            if fingerprint(text, path.name) != baseline:
                errors.append(f"{relative}: protected prose or TeX differs from reviewed baseline")
            for item in items:
                if item.syntax.startswith("legacy-"):
                    errors.append(f"{relative}:{item.line}: math markup is not GitHub-compatible")
                if item.syntax == "dollars" and (path.name != TRAINING or item.body not in CASES):
                    errors.append(f"{relative}:{item.line}: unreviewed dollar block")
                if item.syntax == "fence" and re.search(r"\\\\(?=\n)", item.body):
                    errors.append(f"{relative}:{item.line}: row-break requires reviewed dollar block")
                if path.name == REGISTRY and item.body in ALIASES:
                    errors.append(f"{relative}:{item.line}: unsafe table bar spelling")
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: math validation failed: {exc}")
    return errors


class MathHTML(HTMLParser):
    """Read Arithmatex's generic wrappers without losing escaped TeX operators."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.payloads = []
        self.depth = 0
        self.current = []

    def handle_starttag(self, tag, attrs):
        if self.depth:
            self.depth += 1
        elif "arithmatex" in dict(attrs).get("class", "").split():
            self.depth = 1
            self.current = []

    def handle_endtag(self, tag):
        if self.depth:
            self.depth -= 1
            if not self.depth:
                value = "".join(self.current)
                if not ((value.startswith(r"\(") and value.endswith(r"\)")) or (value.startswith(r"\[") and value.endswith(r"\]"))):
                    raise ValueError("unexpected Arithmatex wrapper")
                self.payloads.append(value[2:-2].strip())

    def handle_data(self, value):
        if self.depth:
            self.current.append(value)


def render_markdown(text: str) -> str:
    import markdown
    from pymdownx.arithmatex import arithmatex_fenced_format

    return markdown.markdown(to_arithmatex(text), extensions=["tables", "pymdownx.superfences", "pymdownx.arithmatex"], extension_configs={
        "pymdownx.arithmatex": {"generic": True},
        "pymdownx.superfences": {"custom_fences": [{"name": "math", "class": "arithmatex", "format": arithmatex_fenced_format(mode="generic")}]},
    })


def check_rendering(text: str) -> str:
    rendered = render_markdown(text)
    parser = MathHTML()
    parser.feed(rendered)
    expected = [item.body.strip() for item in formulas(text)]
    if parser.payloads != expected:
        raise ValueError("Arithmatex lost, reordered, or changed TeX payloads")
    return rendered
