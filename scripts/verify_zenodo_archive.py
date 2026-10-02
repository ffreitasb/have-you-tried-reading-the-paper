#!/usr/bin/env python3
"""Read-only public Zenodo verification; separate from offline integrity checks."""

import hashlib
import io
import json
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "validation-output" / "zenodo-verification.json"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "EducationalReferenceArchiveCheck/1.0 (contact@ffreitasb.cc)"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                return response.read()
        except OSError:
            if attempt == 2:
                raise
            time.sleep(3)
    raise RuntimeError("Unreachable retry state")


def verify(citation: dict) -> dict:
    doi = citation.get("doi")
    if not doi:
        return {"status": "pending", "reason": "No archived release DOI in CITATION.cff yet."}
    if not doi.startswith("10.5281/zenodo."):
        raise ValueError("Expected a Zenodo version DOI")
    record_id = doi.rsplit(".", 1)[1]
    if not record_id.isdigit():
        raise ValueError("Invalid Zenodo record identifier")
    record = json.loads(fetch("https://zenodo.org/api/records/" + record_id))
    metadata = record["metadata"]
    expected = {
        "title": citation["title"], "version": citation["version"],
        "description": citation["abstract"], "publication_date": str(citation["date-released"]),
    }
    for field, value in expected.items():
        if metadata.get(field) != value:
            raise ValueError(f"Archived {field} differs from citation metadata")
    if record.get("doi") != doi:
        raise ValueError("Record DOI is not the specific version DOI")
    if metadata.get("access_right") != "open" or metadata.get("license", {}).get("id") != "cc-by-sa-4.0":
        raise ValueError("Archived access rights or license differ")
    creators = metadata.get("creators", [])
    expected_orcid = citation["authors"][0]["orcid"].removeprefix("https://orcid.org/")
    if len(creators) != 1 or creators[0].get("name") != "Braga, Felipe Freitas" or creators[0].get("orcid") != expected_orcid:
        raise ValueError("Archived creator or ORCID differs")
    resource = metadata.get("resource_type", {})
    if resource.get("type") != "publication" or resource.get("subtype") != "technicalnote":
        raise ValueError("Archived resource is not a technical note")
    tag = "v" + citation["version"]
    commit = subprocess.check_output(["git", "rev-parse", tag + "^{commit}"], cwd=ROOT, text=True).strip()
    expected_files = subprocess.check_output(["git", "ls-tree", "-r", "--name-only", "-z", tag], cwd=ROOT).split(b"\0")
    expected_files = {name.decode("utf-8") for name in expected_files if name}
    files = record.get("files", [])
    if len(files) != 1 or not files[0]["key"].endswith(".zip"):
        raise ValueError("Expected the single native GitHub ZIP archive")
    archived_file = files[0]
    archive = fetch(archived_file["links"]["self"])
    checksum = archived_file.get("checksum", "")
    if checksum.startswith("md5:") and hashlib.md5(archive, usedforsecurity=False).hexdigest() != checksum[4:]:
        raise ValueError("Archive does not match the checksum published by Zenodo")
    with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
        members = [item.filename for item in zipped.infolist() if not item.is_dir()]
        prefixes = {name.split("/", 1)[0] for name in members}
        if len(prefixes) != 1 or any("/" not in name for name in members):
            raise ValueError("Unexpected GitHub archive layout")
        prefix = prefixes.pop() + "/"
        if {name[len(prefix):] for name in members} != expected_files:
            raise ValueError("Archived file inventory differs from the release tag")
        for name in sorted(expected_files):
            content = subprocess.check_output(["git", "show", f"{tag}:{name}"], cwd=ROOT)
            if zipped.read(prefix + name) != content:
                raise ValueError(f"Archived bytes differ from the release tag: {name}")
    return {
        "status": "verified", "record_url": "https://zenodo.org/records/" + record_id,
        "version_doi": doi, "concept_doi": record.get("conceptdoi"),
        "version": citation["version"], "release_tag": tag, "release_commit": commit,
        "resource_type": resource, "license": "CC-BY-SA-4.0", "orcid": expected_orcid,
        "archive_file": archived_file["key"], "archive_checksum": checksum,
        "archive_sha256": hashlib.sha256(archive).hexdigest(),
        "matching_files": len(expected_files), "metadata": "matches canonical citation",
    }


def main() -> int:
    OUTPUT.parent.mkdir(exist_ok=True, parents=True)
    try:
        citation = YAML(typ="safe").load((ROOT / "CITATION.cff").read_text(encoding="utf-8"))
        result = verify(citation)
    except Exception as exc:
        result = {"status": "unverified", "reason": str(exc)}
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["status"] == "unverified" else 0


if __name__ == "__main__":
    sys.exit(main())
