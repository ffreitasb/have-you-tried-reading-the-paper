"""Fetch hash-locked public assets; no package manager or runtime CDN required."""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath
from urllib.request import urlopen


def prepare_assets(root: Path) -> Path:
    """Materialize the complete MathJax ES5 tree, fonts and their licenses."""
    lock = json.loads((root / "web/assets.lock.json").read_text(encoding="utf-8"))
    cache = root / ".cache/downloads"
    output = root / ".cache/site-assets"
    for folder in (root / ".cache", cache, output):
        if folder.is_symlink() or (hasattr(folder, "is_junction") and folder.is_junction()):
            raise ValueError(f"Refusing linked asset directory: {folder}")
    cache.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    for name, asset in lock.items():
        cached = cache / asset["sha256"]
        data = cached.read_bytes() if cached.is_file() else urlopen(asset["url"], timeout=90).read()
        if hashlib.sha256(data).hexdigest() != asset["sha256"]:
            raise ValueError(f"Asset checksum mismatch: {name}")
        if not cached.exists():
            cached.write_bytes(data)
        if name == "mathjax":
            with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
                for member in archive.getmembers():
                    path = PurePosixPath(member.name)
                    if ".." in path.parts or path.is_absolute() or member.issym() or member.islnk():
                        raise ValueError(f"Unsafe archive member: {member.name}")
                    if not member.isfile():
                        continue
                    if member.name.startswith("package/es5/"):
                        target = output / "assets/vendor/mathjax" / path.relative_to("package/es5")
                    elif member.name == "package/LICENSE":
                        target = output / "assets/vendor/mathjax/LICENSE"
                    else:
                        continue
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(archive.extractfile(member).read())
        else:
            target = output / "assets/fonts" / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
    return output
