#!/usr/bin/env python3
"""Build both editions, compose the Pages artifact and validate its static output."""

from __future__ import annotations

import gzip
import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

from validate_repository import DOCUMENTS, LOCALES

ROOT = Path(__file__).resolve().parents[1]


def clean_output(root: Path, target: Path) -> None:
    """Delete only the two dedicated build directories, never links or junctions."""
    root = root.resolve()
    if target.parent.resolve() != root or target.name not in {"site", ".site"}:
        raise ValueError(f"Refusing to clean unexpected build path: {target}")
    if target.is_symlink() or (hasattr(target, "is_junction") and target.is_junction()):
        raise ValueError(f"Refusing to clean linked build path: {target}")
    if target.exists():
        # Refuse linked descendants before recursively deleting any directory.
        for child in target.rglob("*"):
            if child.is_symlink() or (hasattr(child, "is_junction") and child.is_junction()):
                raise ValueError(f"Refusing to clean linked build descendant: {child}")
        shutil.rmtree(target)


def protected_hashes(root: Path) -> dict[str, str]:
    paths = [root / "docs" / locale / name for locale in LOCALES for name in DOCUMENTS]
    paths += [root / name for name in ("LICENSE", "CITATION.cff", ".zenodo.json", "scripts/math-preservation.json", "scripts/math-aliases.json", "scripts/content-revisions.json")]
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def main() -> int:
    before = protected_hashes(ROOT)
    clean_output(ROOT, ROOT / ".site")
    clean_output(ROOT, ROOT / "site")
    for config in ("mkdocs.yml", "mkdocs.pt-BR.yml"):
        subprocess.run([sys.executable, "-m", "mkdocs", "build", "--strict", "-f", config], cwd=ROOT, check=True)
    site = ROOT / "site"
    shutil.copytree(ROOT / ".site/en", site)
    shutil.copytree(ROOT / ".site/pt-BR", site / "pt-BR")
    (site / ".nojekyll").write_bytes(b"")
    # One index covering independent per-edition sitemaps.
    (site / "sitemap.xml").rename(site / "sitemap-en.xml")
    (site / "sitemap.xml").write_bytes(b'<?xml version="1.0" encoding="utf-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><sitemap><loc>https://rtfm.ffreitasb.cc/sitemap-en.xml</loc></sitemap><sitemap><loc>https://rtfm.ffreitasb.cc/pt-BR/sitemap.xml</loc></sitemap></sitemapindex>\n')
    (site / "sitemap.xml.gz").write_bytes(gzip.compress((site / "sitemap.xml").read_bytes(), mtime=0))
    (site / "robots.txt").write_bytes(b"User-agent: *\nAllow: /\nSitemap: https://rtfm.ffreitasb.cc/sitemap.xml\n")
    if before != protected_hashes(ROOT):
        raise ValueError("Build modified protected sources or scientific metadata")
    from validate_site import validate_site
    report = validate_site(ROOT, site)
    (ROOT / ".site/validation.json").write_bytes((json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode())
    print(json.dumps(report, ensure_ascii=False))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
