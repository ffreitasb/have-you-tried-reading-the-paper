#!/usr/bin/env python3
"""Offline acceptance gates for both composed editions and their local assets."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup
from PIL import Image

from math_rendering import MathHTML, formulas
from validate_repository import DOCUMENTS, LOCALES
from site_hooks import ORIGIN, citation_metadata, page_path


def validate_site(root: Path, site: Path) -> dict:
    errors = []
    count = 0
    maths = 0
    cards = []
    cff = citation_metadata(root)
    expected_files = []
    for locale in LOCALES:
        prefix = "pt-BR/" if locale == "pt-BR" else ""
        for name in (*DOCUMENTS, "index.md", "citation.md"):
            path = site / prefix / page_path(name) / "index.html"
            expected_files.append(path)
            if not path.is_file():
                errors.append(f"Missing page: {path.relative_to(site)}")
                continue
            count += 1
            soup = BeautifulSoup(path.read_bytes(), "html.parser")
            url = ORIGIN + prefix + page_path(name)
            def require(condition, message):
                if not condition:
                    errors.append(f"{prefix}{name}: {message}")
            require(soup.html.get("lang") == locale, "wrong HTML language")
            canonical = soup.find("link", rel="canonical")
            require(canonical and canonical.get("href") == url, "wrong canonical")
            for lang, base in (("en", ORIGIN), ("pt-BR", ORIGIN + "pt-BR/")):
                alt = soup.find("link", hreflang=lang)
                require(alt and alt.get("href") == base + page_path(name), "wrong reciprocal language target")
                require(alt and "alternate" in alt.get("rel", []), "missing semantic alternate relation")
            schema = soup.find("script", type="application/ld+json")
            try:
                data = json.loads(schema.string)
                require(data["url"] == url and data["author"]["@id"] == cff["orcid"], "wrong structured data")
            except (AttributeError, TypeError, ValueError, KeyError):
                require(False, "missing/invalid JSON-LD")
            for property in ("og:title", "og:description", "og:url", "og:image", "og:locale"):
                require(soup.find("meta", property=property), f"missing {property}")
            image = soup.find("meta", property="og:image")
            if image:
                image_path = site / unquote(urlsplit(image["content"]).path).lstrip("/")
                require(image_path.is_file(), "missing social card")
                if image_path.is_file():
                    with Image.open(image_path) as card:
                        require(card.size == (1200, 630), "wrong social-card dimensions")
                    cards.append(str(image_path.relative_to(site)))
            if name in DOCUMENTS:
                headings = soup.select(".md-content__inner h1[id], .md-content__inner h2[id], .md-content__inner h3[id]")
                if headings and headings[0].name == "h1":
                    headings = headings[1:]
                toc_targets = {a.get("href") for a in soup.select('[data-md-component="toc"] a[href]')}
                require(all("#" + h["id"] in toc_targets for h in headings), "table of contents omits original sections")
                parser = MathHTML()
                parser.feed(str(soup.select_one(".md-content__inner")))
                expected = [item.body.strip() for item in formulas((root / "docs" / locale / name).read_bytes().decode())]
                require(parser.payloads == expected, "TeX payload changed, lost or reordered")
                maths += len(expected)
            if name == "citation.md":
                require(cff["doi"] in soup.get_text(), "citation doesn't match CFF")
        search = site / prefix / "search/search_index.json"
        if not search.is_file():
            errors.append(f"Missing {prefix} search index")
        else:
            index = json.loads(search.read_bytes())
            lang = "pt" if prefix else "en"
            if lang not in index["config"]["lang"]:
                errors.append(f"Wrong search language: {prefix}")
            indexed = {urlsplit(doc["location"]).path.split("/")[0] for doc in index["docs"]}
            if any(name.removesuffix(".md") not in indexed for name in DOCUMENTS):
                errors.append(f"Incomplete search corpus: {prefix}")
    # Check links in rendered pages against real files AND actual generated IDs.
    cache = {}
    for path in (*expected_files, site / "404.html", site / "pt-BR/404.html"):
        if not path.is_file():
            errors.append(f"Missing output: {path.relative_to(site)}")
            continue
        soup = BeautifulSoup(path.read_bytes(), "html.parser")
        for tag in soup.select("[href], [src]"):
            target = tag.get("href", tag.get("src", ""))
            parsed = urlsplit(target)
            if parsed.scheme and parsed.netloc != urlsplit(ORIGIN).netloc:
                if tag.name in {"script", "img", "iframe", "source"} or (tag.name == "link" and "stylesheet" in tag.get("rel", [])):
                    errors.append(f"Third-party runtime asset: {path.relative_to(site)}: {target}")
                continue
            if parsed.scheme in {"mailto", "tel", "data", "javascript"}:
                continue
            dest = site / unquote(parsed.path).lstrip("/") if parsed.path.startswith("/") else path.parent / unquote(parsed.path)
            dest = dest.resolve()
            if not dest.is_relative_to(site.resolve()):
                errors.append(f"Link escapes site: {target}")
                continue
            if dest.is_dir():
                dest /= "index.html"
            if not dest.is_file():
                errors.append(f"Broken output link: {path.relative_to(site)} → {target}")
            elif parsed.fragment and dest.suffix == ".html":
                if dest not in cache:
                    cache[dest] = {el["id"] for el in BeautifulSoup(dest.read_bytes(), "html.parser").select("[id]")}
                if unquote(parsed.fragment) not in cache[dest]:
                    errors.append(f"Broken output anchor: {target}")
        if soup.find("meta", attrs={"name": "robots", "content": "noindex"}) and path.name != "404.html":
            errors.append(f"Unexpected noindex: {path.relative_to(site)}")
    for sitemap in ("sitemap-en.xml", "pt-BR/sitemap.xml"):
        urls = [e.text for e in ET.parse(site / sitemap).findall(".//{*}loc")]
        if len(urls) != 24 or any(not u.startswith(ORIGIN) for u in urls):
            errors.append(f"Incomplete sitemap: {sitemap}")
    return {"pages": count, "math_payloads": maths, "social_cards": len(set(cards)), "errors": sorted(set(errors))}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[1]
    report = validate_site(root, root / "site")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    raise SystemExit(bool(report["errors"]))
