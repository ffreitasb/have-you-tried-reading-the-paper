#!/usr/bin/env python3
"""Read-only, offline repository checks. Install requirements-validation.txt first."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPOSITORY = "https://github.com/ffreitasb/have-you-tried-reading-the-paper"
LOCALES = ("en-US", "pt-BR")
DOCUMENTS = (
    "00_README_INDEX.md",
    "01_GUT_GENERATIVE_AI_UNIFIED_ENGINEERING.md",
    "02_LLM_TRANSFORMER_INFERENCE_DATASHEET.md",
    "03_CODE_GENERATION_AND_AGENTIC_CODING_DATASHEET.md",
    "04_IMAGE_GENERATION_DIFFUSION_FLOW_DATASHEET.md",
    "05_VIDEO_GENERATION_SPATIOTEMPORAL_DATASHEET.md",
    "06_AUDIO_MUSIC_TTS_GENERATION_DATASHEET.md",
    "07_3D_GENERATION_REPRESENTATION_DATASHEET.md",
    "08_AGENT_ACTION_CONTROL_SYSTEM_DATASHEET.md",
    "09_LOCAL_AI_INFERENCE_RUNTIME_DATASHEET.md",
    "10_MULTIMODAL_VLM_OMNI_DATASHEET.md",
    "11_EMBEDDING_RETRIEVAL_RERANKER_DATASHEET.md",
    "12_REWARD_VERIFIER_JUDGE_DATASHEET.md",
    "13_WORLD_MODEL_VLA_EMBODIED_AI_DATASHEET.md",
    "14_TIME_SERIES_TABULAR_FOUNDATION_MODELS.md",
    "15_GRAPH_FOUNDATION_MODELS_DATASHEET.md",
    "16_TRAINING_ALIGNMENT_ADAPTATION_DATASHEET.md",
    "17_EVALUATION_BENCHMARK_EXPERIMENTATION_DATASHEET.md",
    "18_SECURITY_ROBUSTNESS_FAILURE_MODES_DATASHEET.md",
    "19_PARAMETER_GLOSSARY_AND_REGISTRY.md",
    "CHANGELOG.md",
    "CONVENTIONS.md",
)
REQUIRED = (
    "README.md", "README.pt-BR.md", "LICENSE", "CITATION.cff",
    "PROVENANCE.md", "PROVENANCE.pt-BR.md", "CONTRIBUTING.md",
    "CONTRIBUTING.pt-BR.md", "CODE_OF_CONDUCT.md", "SECURITY.md",
    ".editorconfig", ".gitattributes", ".gitignore", ".github/CODEOWNERS",
    ".github/PULL_REQUEST_TEMPLATE.md", ".github/dependabot.yml",
    ".github/ISSUE_TEMPLATE/config.yml",
    ".github/ISSUE_TEMPLATE/content-correction.yml",
    ".github/ISSUE_TEMPLATE/source-reference.yml",
    ".github/ISSUE_TEMPLATE/translation.yml",
    ".github/ISSUE_TEMPLATE/structural-proposal.yml",
    ".github/workflows/repository-integrity.yml",
    ".github/workflows/external-links.yml",
    "scripts/validate_repository.py", "scripts/requirements-validation.txt",
    "scripts/math-preservation.json", "scripts/math_rendering.py",
    "scripts/verify_math_rendering.py", "scripts/requirements-rendering.txt",
)
LOCAL_STATE = {".claude-flow", ".repowise", ".kilo", ".claude", ".venv", "__pycache__", "validation-output"}
TEXT_SUFFIXES = {".md", ".cff", ".json", ".yaml", ".yml", ".py", ".txt"}
PATH_ARTIFACTS = re.compile(r"/mnt/data/|/tmp/|sandbox:/|file://|[A-Za-z]:\\Users\\")
# Any intentional technical example needs a reviewed file/line/token entry here.
PATH_ALLOWLIST: set[tuple[str, int, str]] = set()


def mask_code(text: str, inline: bool = False) -> str:
    """Blank code/front matter without moving line positions."""
    lines = text.splitlines(keepends=True)
    fence = None
    front = bool(lines and lines[0].strip() == "---")
    result = []
    for index, line in enumerate(lines):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        hidden = front or fence is not None or match is not None
        if front:
            if index and line.strip() == "---":
                front = False
        elif fence:
            if re.fullmatch(r" {0,3}" + re.escape(fence[0]) + "{" + str(len(fence)) + r",}\s*", line):
                fence = None
        elif match:
            fence = match[1]
        result.append(re.sub(r"[^\n]", " ", line) if hidden else line)
    value = "".join(result)
    if inline:
        value = re.sub(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", lambda m: re.sub(r"[^\n]", " ", m[0]), value, flags=re.S)
    return value


def markdown_links(text: str) -> list[tuple[str, int]]:
    """Inline/image links, reference definitions/usages, and HTML targets.

    Balanced parentheses in URLs and angle-enclosed destinations are supported.
    Inline code and fenced examples are not navigation.
    """
    visible = mask_code(text, inline=True)
    links = []
    references = {}
    norm = lambda label: " ".join(label.split()).casefold()
    for m in re.finditer(r"^ {0,3}\[([^\]\n]+)\]:\s*(<[^>]+>|\S+)", visible, re.M):
        references[norm(m[1])] = m[2].strip("<>")
        links.append((m[2].strip("<>"), visible.count("\n", 0, m.start()) + 1))
    for m in re.finditer(r"(?<!\\)\[([^\[\]\n]*)\]\(", visible):
        start = m.end()
        while start < len(visible) and visible[start].isspace():
            start += 1
        if start < len(visible) and visible[start] == "<":
            end = visible.find(">", start + 1)
            if end == -1:
                continue
            target = visible[start + 1:end]
        else:
            depth, end = 0, start
            while end < len(visible):
                char = visible[end]
                if char == "\\" and end + 1 < len(visible):
                    end += 2
                    continue
                if char == "(" or (char == ")" and depth):
                    depth += 1 if char == "(" else -1
                elif char == ")" or char.isspace():
                    break
                end += 1
            target = visible[start:end]
        if target:
            links.append((re.sub(r"\\([()])", r"\1", target), visible.count("\n", 0, m.start()) + 1))
    for m in re.finditer(r"(?<!\\)\[([^\[\]\n]+)\](?:\[([^\]\n]*)\])?", visible):
        if visible[m.end():m.end() + 1] in ("(", ":"):
            continue
        label = norm(m[2] if m[2] else m[1])
        if label in references:
            links.append((references[label], visible.count("\n", 0, m.start()) + 1))
        elif m[2] is not None:
            links.append(("!undefined-reference:" + label, visible.count("\n", 0, m.start()) + 1))
    for m in re.finditer(r"\b(?:href|src)\s*=\s*['\"]([^'\"]+)['\"]", visible, re.I):
        links.append((html.unescape(m[1]), visible.count("\n", 0, m.start()) + 1))
    return links


def anchors(text: str) -> set[str]:
    visible = mask_code(text)
    found = set(re.findall(r"\b(?:id|name)\s*=\s*['\"]([^'\"]+)['\"]", visible, re.I))
    seen: Counter[str] = Counter()
    lines = visible.splitlines()
    for index, line in enumerate(lines):
        heading = re.match(r"^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$", line)
        title = heading[1] if heading else None
        if title is None and index + 1 < len(lines) and line.strip() and re.fullmatch(r" {0,3}(?:=+|-+)\s*", lines[index + 1]):
            title = line.strip()
        if title is None:
            continue
        title = re.sub(r"!?\[([^\]]+)\]\([^)]*\)", r"\1", title)
        title = html.unescape(re.sub(r"<[^>]*>", "", title)).lower()
        slug = "".join(char for char in title if char in " -_" or unicodedata.category(char)[0] in "LN").replace(" ", "-")
        suffix = f"-{seen[slug]}" if seen[slug] else ""
        seen[slug] += 1
        # GitHub also deduplicates headings that already end in a numeric suffix.
        while slug + suffix in found:
            suffix = f"-{seen[slug]}"
            seen[slug] += 1
        found.add(slug + suffix)
    return found


def internal_link_error(root: Path, source: Path, target: str) -> str | None:
    if target.startswith("!undefined-reference:"):
        return target[1:]
    try:
        parsed = urlsplit(html.unescape(target))
    except ValueError:
        return f"malformed link: {target}"
    if parsed.scheme or parsed.netloc:
        return None  # Network health belongs in the separate workflow.
    if "\\" in parsed.path:
        return f"non-portable path: {target}"
    requested = Path(os.path.abspath(source.parent / unquote(parsed.path))) if parsed.path else source
    destination = requested.resolve()
    if not destination.is_relative_to(root.resolve()):
        return f"link escapes repository: {target}"
    if not destination.exists():
        return f"missing local target: {target}"
    # Check component spelling even on case-insensitive Windows filesystems.
    current = root.resolve()
    for part in requested.relative_to(root.resolve()).parts:
        if part not in {p.name for p in current.iterdir()}:
            return f"case mismatch in local target: {target}"
        current /= part
    if parsed.fragment and destination.is_file() and destination.suffix == ".md":
        fragment = unquote(parsed.fragment)
        if fragment not in anchors(destination.read_text(encoding="utf-8")):
            return f"missing Markdown anchor: {target}"
    return None


def published_files(root: Path) -> list[Path]:
    """Honor .gitignore locally and still inspect ignored files already tracked."""
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
        capture_output=True, check=True,
    )
    return sorted({root / p.decode("utf-8") for p in result.stdout.split(b"\0") if p and (root / p.decode("utf-8")).exists()})


def orcid_valid(value: str) -> bool:
    identifier = value.removeprefix("https://orcid.org/")
    if not re.fullmatch(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]", identifier):
        return False
    digits = identifier.replace("-", "")
    total = 0
    for char in digits[:-1]:
        total = (total + int(char)) * 2
    check = (12 - total % 11) % 11
    return digits[-1] == ("X" if check == 10 else str(check))


def check_metadata(root: Path, errors: list[str]) -> None:
    from cffconvert import Citation
    from ruamel.yaml import YAML

    try:
        text = (root / "CITATION.cff").read_text(encoding="utf-8")
        Citation(text).validate()
        citation = YAML(typ="safe").load(text)
    except Exception as exc:
        errors.append(f"CITATION.cff: schema validation failed: {exc}")
        return
    required = {"cff-version": "1.2.0", "title": "Have You Tried Reading the Paper?", "license": "CC-BY-SA-4.0", "repository-code": REPOSITORY, "url": REPOSITORY}
    for field, expected in required.items():
        if citation.get(field) != expected:
            errors.append(f"CITATION.cff: {field} must be {expected!r}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(citation.get("version", ""))):
        errors.append("CITATION.cff: require a semantic release version")
    try:
        release_date = dt.date.fromisoformat(str(citation.get("date-released", "")))
    except ValueError:
        errors.append("CITATION.cff: date-released must be a real ISO date")
        return
    authors = citation.get("authors", [])
    identity = {"family-names": "Braga", "given-names": "Felipe Freitas", "alias": "Felipe Freitas", "email": "contact@ffreitasb.cc"}
    if len(authors) != 1 or any(authors[0].get(k) != v for k, v in identity.items()):
        errors.append("CITATION.cff: accountable human author identity changed")
        return
    if not orcid_valid(authors[0].get("orcid", "")):
        errors.append("CITATION.cff: require an ORCID with a valid checksum")
    preferred = citation.get("preferred-citation", {})
    for field in ("title", "authors", "version", "url", "doi"):
        if preferred.get(field) != citation.get(field):
            errors.append(f"CITATION.cff: preferred-citation {field} differs from canonical metadata")
    if preferred.get("type") != "manual" or preferred.get("year") != release_date.year:
        errors.append("CITATION.cff: preferred citation must describe this technical manual and release year")
    zenodo_path = root / ".zenodo.json"
    if not zenodo_path.exists():
        return
    try:
        zenodo = json.loads(zenodo_path.read_text(encoding="utf-8"))
        if not isinstance(zenodo, dict):
            raise ValueError("expected a JSON object")
    except (ValueError, OSError) as exc:
        errors.append(f".zenodo.json: {exc}")
        return
    mirror = {
        "title": citation["title"], "version": citation["version"],
        "publication_date": release_date.isoformat(), "access_right": "open",
        "license": "cc-by-sa-4.0", "upload_type": "publication",
        "publication_type": "technicalnote", "language": "eng",
        "description": citation.get("abstract"), "keywords": citation.get("keywords"),
        "creators": [{"name": "Braga, Felipe Freitas", "orcid": authors[0].get("orcid", "").removeprefix("https://orcid.org/")}],
        "related_identifiers": [{"identifier": REPOSITORY, "relation": "isSupplementTo", "scheme": "url"}],
    }
    for field, expected in mirror.items():
        if zenodo.get(field) != expected:
            errors.append(f".zenodo.json: {field} differs from the verified CFF mirror")
    if "English and Brazilian Portuguese" not in str(zenodo.get("description", "")):
        errors.append(".zenodo.json: description must state the bilingual scope")


def validate(root: Path) -> tuple[list[str], int]:
    from ruamel.yaml import YAML

    errors = []
    for name in REQUIRED:
        if not (root / name).is_file():
            errors.append(f"missing required file: {name}")
    for locale in LOCALES:
        folder = root / "docs" / locale
        names = {p.name for p in folder.iterdir()} if folder.is_dir() else set()
        if names != set(DOCUMENTS):
            errors.append(f"docs/{locale}: missing={sorted(set(DOCUMENTS) - names)}, unexpected={sorted(names - set(DOCUMENTS))}")
        numbers = Counter(p.name[:2] for p in folder.glob("[0-9][0-9]_*.md"))
        if numbers != Counter(f"{i:02}" for i in range(20)):
            errors.append(f"docs/{locale}: require exactly one document numbered 00 through 19")
    link_count = 0
    for path in published_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or any(part in LOCAL_STATE for part in path.relative_to(root).parts):
            errors.append(f"unpublishable local state or symlink: {relative}")
            continue
        if not path.is_file() or (path.suffix not in TEXT_SUFFIXES and path.name not in {"LICENSE", "CODEOWNERS", ".editorconfig", ".gitignore", ".gitattributes"}):
            continue
        data = path.read_bytes()
        if data.startswith(b"\xef\xbb\xbf"):
            errors.append(f"{relative}: UTF-8 BOM is not permitted")
        if b"\r" in data:
            errors.append(f"{relative}: expected LF line endings")
        if not data.endswith(b"\n"):
            errors.append(f"{relative}: missing final newline")
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            errors.append(f"{relative}: invalid UTF-8")
            continue
        if path.suffix in {".md", ".cff", ".json", ".yml", ".yaml"}:
            for index, line in enumerate(text.splitlines(), 1):
                for match in PATH_ARTIFACTS.finditer(line):
                    if (relative, index, match[0]) not in PATH_ALLOWLIST:
                        errors.append(f"{relative}:{index}: development/runtime path artifact")
        if path.suffix == ".md":
            if "en_US/" in text:
                errors.append(f"{relative}: obsolete locale path")
            if re.search(r"\[\[[A-Z0-9_]+\]\]", mask_code(text)):
                errors.append(f"{relative}: non-portable Obsidian navigation")
            for target, line in markdown_links(text):
                link_count += 1
                try:
                    error = internal_link_error(root, path, target)
                except (OSError, UnicodeError) as exc:
                    error = f"unreadable target: {exc}"
                if error:
                    errors.append(f"{relative}:{line}: {error}")
        if path.suffix in {".yml", ".yaml"}:
            try:
                config = YAML(typ="safe").load(text)
                if not isinstance(config, dict):
                    raise ValueError("expected a YAML mapping")
                if path.parent.name == "workflows":
                    if config.get("permissions") != {"contents": "read"}:
                        errors.append(f"{relative}: require read-only contents permissions")
                    if "pull_request_target" in config.get("on", {}):
                        errors.append(f"{relative}: pull_request_target is forbidden")
                    for action in re.findall(r"\buses:\s*([^\s#]+)", text):
                        if not re.fullmatch(r"[\w.-]+/[\w./-]+@[0-9a-f]{40}", action):
                            errors.append(f"{relative}: action must have an immutable SHA: {action}")
                if path.parent.name == "ISSUE_TEMPLATE" and path.name != "config.yml":
                    ids = [item["id"] for item in config.get("body", []) if "id" in item]
                    if not ids or len(ids) != len(set(ids)):
                        errors.append(f"{relative}: issue form needs unique field IDs")
            except Exception as exc:
                errors.append(f"{relative}: invalid YAML configuration: {exc}")
    for readme, other, locale, provenance, contribution in (
        ("README.md", "README.pt-BR.md", "en-US", "PROVENANCE.md", "CONTRIBUTING.md"),
        ("README.pt-BR.md", "README.md", "pt-BR", "PROVENANCE.pt-BR.md", "CONTRIBUTING.pt-BR.md"),
    ):
        if (root / readme).is_file():
            targets = {target for target, _ in markdown_links((root / readme).read_text(encoding="utf-8"))}
            for expected in (other, f"docs/{locale}/00_README_INDEX.md", provenance, contribution, "CITATION.cff", "LICENSE", "SECURITY.md", "CODE_OF_CONDUCT.md"):
                if expected not in targets:
                    errors.append(f"{readme}: missing required navigation: {expected}")
    if (root / "LICENSE").is_file() and "Attribution-ShareAlike 4.0 International" not in (root / "LICENSE").read_text(encoding="utf-8"):
        errors.append("LICENSE: missing CC BY-SA 4.0 legal text")
    if (root / "CITATION.cff").is_file():
        check_metadata(root, errors)
    from math_rendering import check_corpus
    errors.extend(check_corpus(root))
    return errors, link_count


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    try:
        errors, count = validate(args.root.resolve())
    except ImportError:
        print("Install validation dependencies: python -m pip install -r scripts/requirements-validation.txt", file=sys.stderr)
        return 2
    except (OSError, subprocess.CalledProcessError) as exc:
        print(f"Could not inspect repository: {exc}", file=sys.stderr)
        return 2
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"FAIL: {len(errors)} error(s)")
        return 1
    print(f"PASS: 44 knowledge files, bilingual inventory, UTF-8/LF, {count} Markdown links, CFF schema and metadata, governance, pinned read-only CI")
    print("External HTTP status is intentionally checked by the separate External links workflow.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
