# Reading site maintenance

The publication layer builds the canonical corpus into two independent static
editions: English at `https://rtfm.ffreitasb.cc/` and Brazilian Portuguese at
`https://rtfm.ffreitasb.cc/pt-BR/`. GitHub remains the source of truth; Zenodo
archives scientific releases. Publishing the site does not create a new release.

## Build and preview

Use Python 3.12 or 3.13. A separate environment keeps publication dependencies
apart from other work. On Linux, install the native Cairo library first:

```sh
sudo apt-get update
sudo apt-get install --yes libcairo2
python -m venv .venv
.venv/bin/python -m pip install -r requirements-docs.txt -r scripts/requirements-validation.txt
.venv/bin/python scripts/build_site.py
.venv/bin/python -m http.server 8000 --bind 127.0.0.1 --directory site
```

On Windows, use `.venv/Scripts/python.exe` for those commands. CairoSVG also
requires a discoverable native Cairo DLL. If the machine does not already have
one, install Cairo from a trusted distribution such as conda-forge, activate
that environment, and create the virtual environment from its Python. Verify
the native runtime with `python -c "import cairosvg"` before building. No Node.js
or npm installation is required. Social cards are a mandatory part of the build.

Open `http://127.0.0.1:8000/` and `/pt-BR/`. Canonicals, language links and 404
recovery links deliberately retain their production URLs during local preview.
For one-edition iteration, use `python -m mkdocs serve -f mkdocs.yml` or
`python -m mkdocs serve -f mkdocs.pt-BR.yml`; final QA uses the composed build.

`scripts/build_site.py` runs both strict builds, composes `site/`, checks the
output, and writes `.site/validation.json`. It refuses unexpected cleanup paths,
symlinks and junctions. `.site/`, `site/`, `.cache/`, environments and local
validation evidence are ignored. Never commit generated HTML, font binaries,
cards, caches, local PRDs or agent context.

## Sources and publication hooks

The 44 knowledge documents (00–19, conventions and changelog in each language)
stay canonical and protected by the existing reviewed-content gate. Each edition
adds only `index.md` and `citation.md`. Navigation labels belong in the two
locale configs, not in renamed source files or rewritten headings.

- `mkdocs.base.yml`: shared theme, extensions, plugins and hook registration.
- `mkdocs.yml`, `mkdocs.pt-BR.yml`: independent navigation, search and output.
- `scripts/mkdocs_math.py`: the existing, single mathematical adapter. It changes
  markup only in memory and escapes HTML transport without changing TeX inputs.
- `scripts/site_hooks.py`: CFF-derived citation metadata, JSON-LD, per-page
  language links, document language and local asset registration.
- `web/overrides/`: minimal templates and original presentation assets. The
  static source-link override avoids client-side GitHub statistics requests.
- `web/social/f0xtrot.yml`: built-in Material social-card layout and metadata.

`CITATION.cff` supplies author, ORCID, version, date, license and both DOIs. Do
not hard-code another copy of these fields into templates. The version DOI is
the archived release; the project DOI groups all versions. Living pages are not
the immutable archived snapshot. Source/edit URLs use their actual locale path.

The Registry filter is a progressive enhancement over the existing tables. It
matches names, definitions, tags and enclosing headings, folds case and accents,
announces counts, and keeps explanatory prose visible. With JavaScript disabled,
the entire page remains visible and the inactive filter stays hidden. Search
is Material's local search worker, with a separate index and language per build.

## Assets, licenses and privacy

Runtime assets are served from the site itself. There is no analytics service,
cookie consent layer, comment system, remote font stylesheet or runtime CDN.
Search preferences may use the theme's local browser storage. Build-time public
downloads are distinct from requests made by readers' browsers.

`web/assets.lock.json` pins SHA-256 hashes for MathJax 3.2.2 and WOFF2 font files.
`scripts/site_assets.py` verifies every downloaded/cached input and extracts the
complete MathJax ES5 distribution, including fonts, extensions and dynamic
imports. A checksum mismatch fails the build. To update an asset, review its
official source, version and license, change its URL and hash together, build
with an empty `.cache/`, and repeat browser/network/math QA. Do not simply
replace a failing expected hash with whatever the network returned.

Third-party components retain their own licenses:

| Component | Origin | License |
| --- | --- | --- |
| MathJax 3.2.2 | [MathJax](https://github.com/mathjax/MathJax) / official npm tarball | Apache-2.0; license copied beside the local distribution |
| JetBrains Mono | [Google Fonts source](https://github.com/google/fonts/tree/main/ofl/jetbrainsmono) | SIL Open Font License 1.1; notice copied into `assets/fonts/` |
| Space Grotesk | [Google Fonts source](https://github.com/google/fonts/tree/main/ofl/spacegrotesk) | SIL Open Font License 1.1; notice copied into `assets/fonts/` |
| Material for MkDocs | [Material](https://squidfunk.github.io/mkdocs-material/) | MIT; footer attribution retained |

The palette and typography follow the maintainer's F0XTROT identity. The CSS,
diagram, templates and card layout here were written for this repository; no
private portfolio/blog source, infrastructure or artwork is redistributed.
Content licensing remains CC BY-SA 4.0. Social-card TTF fonts are downloaded by
Material's normal build-time font resolver and cached locally; they are not a
third-party runtime dependency.

## Validation and upgrade policy

```sh
python scripts/validate_repository.py
python -m unittest discover -s scripts -p 'test_*.py'
python scripts/verify_math_rendering.py
python scripts/build_site.py
python -m pip check
```

The site gate checks all 48 content pages, exact ordered TeX payloads, actual
output links/anchors, CFF-backed citation, reciprocal language links, JSON-LD,
social tags/cards, local asset targets, independent search indexes and both
sitemaps. It complements browser testing; it does not prove browser rendering,
keyboard access, screen-reader behavior or DNS/HTTPS by itself.

Before publication or dependency upgrades, test both languages at desktop and
320/390px widths, 200% zoom, keyboard-only navigation, reduced motion and print.
Inspect long headings, tables, code, MathJax `cases`, comparisons and Registry
collisions. Search for KV cache, temperature, CFG, MoE, MLA, RAG, RoPE, flow
matching, ASR, quantization, reward model and HNSW. Check the filter's reset,
empty state, case/accent folding, reload/back and disabled-JavaScript fallback.
Confirm no third-party runtime requests, missing assets or browser errors.
Inspect cards for home, chapters 02/04 and Registry in both languages.

The stack stays on stable MkDocs **1.x** and Material **9.7.x** with exact direct
pins in `requirements-docs.txt`; the reviewed Markdown/PyMdown pair is shared
with rendering CI. Dependabot groups monthly Python updates conservatively and
blocks MkDocs 2 / Material 9.8+. A future Zensical migration requires a separate
compatibility review; do not switch generators as an incidental dependency fix.

## GitHub Pages and domain

`.github/workflows/pages.yml` builds PRs with `contents: read`. It never configures
or deploys Pages on a PR. Only a successful build on trusted `main` push/manual
events reaches `deploy`, which has `pages: write` and `id-token: write` and uses
the `github-pages` environment. Actions use immutable SHAs. The repository
validator explicitly checks this exception while retaining read-only policy
for all other jobs. Keep repository protection and environment safeguards.

Use **GitHub Actions** as the Pages build source. GitHub manages the domain in
repository Settings → Pages (or the Pages API); an artifact `CNAME` is not
required for this deployment mode. Confirm parent-domain verification in account
Settings → Pages before the cutover. In Cloudflare, the single intended record
is `CNAME rtfm → ffreitasb.github.io`, TTL Auto, **DNS only** (gray cloud). Keep
the domain-verification TXT and all unrelated DNS records unchanged. Never
invent a verification token or add a wildcard record.

After deployment, verify the exact deployed commit, canonical domain, HTTPS
certificate and enforced HTTPS, root/PT homes, deep routes, 404, search/filter,
all asset requests, cards, sitemap index and robots. The custom domain is only
announced in repository READMEs/About after those public checks succeed. A DNS
or certificate wait is an open publication gate, not a completed launch.
