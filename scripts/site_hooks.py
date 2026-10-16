"""Publication-only metadata and assets. Never writes to canonical Markdown."""

from __future__ import annotations

import copy
import json
import re
from pathlib import Path

import yaml
from mkdocs.plugins import event_priority
from mkdocs.structure.files import File

from site_assets import prepare_assets

ORIGIN = "https://rtfm.ffreitasb.cc/"
ROOT = Path(__file__).resolve().parents[1]


def page_path(src_uri: str) -> str:
    return "" if src_uri == "index.md" else src_uri.removesuffix(".md") + "/"


def citation_metadata(root: Path) -> dict:
    cff = yaml.safe_load((root / "CITATION.cff").read_text(encoding="utf-8"))
    author = cff["authors"][0]
    return {
        "title": cff["title"], "version": cff["version"],
        "date": str(cff["date-released"]), "doi": cff["doi"],
        "concept_doi": next(i["value"] for i in cff["identifiers"] if i["type"] == "doi"),
        "author": f'{author["given-names"]} {author["family-names"]}',
        "orcid": author["orcid"], "repository": cff["repository-code"],
        "license": cff["license"],
    }


def on_config(config, **kwargs):
    config.extra["scholar"] = citation_metadata(ROOT)
    config.extra["locale"] = "pt-BR" if Path(config.docs_dir).name == "pt-BR" else "en-US"
    return config


def on_files(files, config, **kwargs):
    assets = prepare_assets(ROOT)
    for path in sorted(assets.rglob("*")):
        if path.is_file():
            files.append(File(path.relative_to(assets).as_posix(), str(assets), config.site_dir, False))
    return files


@event_priority(100)
def on_page_markdown(markdown, page, config, **kwargs):
    pt = config.extra["locale"] == "pt-BR"
    page.meta["is_registry"] = page.file.src_uri.startswith("19_")
    page.meta.setdefault("description", (
        "Referência aberta de engenharia de foundation models: " if pt else
        "An open foundation model engineering reference: "
    ) + page.meta.get("title", page.title) + ". " + ("Sem mágica. Só tensores." if pt else "No magic. Just tensors."))
    return markdown


@event_priority(-100)
def on_page_context(context, page, config, **kwargs):
    """Give both native language menus and head links the corresponding page."""
    local = copy.copy(config)
    local.extra = dict(config.extra)
    route = page_path(page.file.src_uri)
    local.extra["alternate"] = [
        {"name": "English", "lang": "en", "link": ORIGIN + route},
        {"name": "Português brasileiro", "lang": "pt-BR", "link": ORIGIN + "pt-BR/" + route},
    ]
    context["config"] = local
    pt = config.extra["locale"] == "pt-BR"
    scholar = config.extra["scholar"]
    kind = "WebSite" if page.is_homepage else ("TechArticle" if re.match(r"\d{2}_", page.file.src_uri) else "WebPage")
    schema = {
        "@context": "https://schema.org", "@type": kind,
        "name": config.site_name if page.is_homepage else page.meta.get("title", page.title),
        "url": page.canonical_url, "description": page.meta["description"],
        "inLanguage": config.extra["locale"],
        "author": {"@type": "Person", "name": scholar["author"], "@id": scholar["orcid"]},
        "license": "https://creativecommons.org/licenses/by-sa/4.0/",
    }
    if not page.is_homepage:
        schema["isPartOf"] = {"@type": "WebSite", "url": ORIGIN, "name": config.site_name}
    if kind == "TechArticle":
        schema["citation"] = "https://doi.org/" + scholar["doi"]
    context["structured_data"] = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
    context["source_url"] = scholar["repository"] + "/blob/main/docs/" + config.extra["locale"] + "/" + page.file.src_uri
    context["is_pt"] = pt
    return context


def on_post_page(output, page, config, **kwargs):
    # Material's Portuguese UI locale is `pt`; the document edition is `pt-BR`.
    if config.extra["locale"] == "pt-BR":
        output = output.replace('<html lang="pt"', '<html lang="pt-BR"', 1)
    else:
        output = output.replace('<html lang="en"', '<html lang="en-US"', 1)
    return output
