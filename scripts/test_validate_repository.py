"""Regression checks for navigation failures that would break a public archive."""

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from validate_repository import (
    anchors,
    check_metadata,
    internal_link_error,
    markdown_links,
    orcid_valid,
)


class NavigationTests(unittest.TestCase):
    def test_examples_are_not_navigation(self):
        text = "`[example](missing.md)`\n~~~md\n[example](missing.md)\n~~~\n[real](chapter.md)\n"
        self.assertEqual(markdown_links(text), [("chapter.md", 5)])

    def test_balanced_urls_reference_links_and_images(self):
        text = (
            '[paper](https://example.org/a_(b) "title")\n'
            '[chapter][ref]\n[ref]: <a%20b.md#section>\n'
            '![image](figure.png)\n<a href="chapter.md#section">chapter</a>\n'
        )
        targets = [target for target, _ in markdown_links(text)]
        self.assertIn("https://example.org/a_(b)", targets)
        self.assertEqual(targets.count("a%20b.md#section"), 2)
        self.assertIn("figure.png", targets)
        self.assertIn("chapter.md#section", targets)

    def test_unicode_and_duplicate_anchors(self):
        text = '# Segurança: `KV_cache`\n# Segurança: `KV_cache`\n~~~\n# Hidden\n~~~\n<a id="explicit"></a>\n'
        self.assertEqual(anchors(text), {"segurança-kv_cache", "segurança-kv_cache-1", "explicit"})

    def test_missing_reference_is_not_silently_ignored(self):
        self.assertEqual(markdown_links("[chapter][missing]"), [("!undefined-reference:missing", 1)])

    def test_local_targets_fragments_and_escape(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "README.md"
            source.write_text("# Readme\n", encoding="utf-8")
            (root / "chapter.md").write_text("# Seção\n# Seção\n", encoding="utf-8")
            self.assertIsNone(internal_link_error(root, source, "chapter.md#se%C3%A7%C3%A3o-1"))
            self.assertIn("missing Markdown anchor", internal_link_error(root, source, "chapter.md#absent"))
            self.assertIn("missing local target", internal_link_error(root, source, "absent.md"))
            self.assertIn("escapes repository", internal_link_error(root, source, "../outside.md"))
            self.assertIsNone(internal_link_error(root, source, "https://example.org/unreachable"))

    def test_case_sensitive_navigation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "README.md"
            source.write_text("# Readme\n", encoding="utf-8")
            (root / "Chapter.md").write_text("# Chapter\n", encoding="utf-8")
            self.assertIsNone(internal_link_error(root, source, "Chapter.md"))
            self.assertIsNotNone(internal_link_error(root, source, "chapter.md"))


class MetadataTests(unittest.TestCase):
    def test_orcid_checksum(self):
        self.assertTrue(orcid_valid("https://orcid.org/0009-0006-9142-5072"))
        self.assertFalse(orcid_valid("https://orcid.org/0009-0006-9142-5073"))

    def test_zenodo_drift_rejected(self):
        repository = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CITATION.cff").write_bytes((repository / "CITATION.cff").read_bytes())
            metadata = json.loads((repository / ".zenodo.json").read_text(encoding="utf-8"))
            metadata["creators"][0]["name"] = "Wrong creator"
            (root / ".zenodo.json").write_text(json.dumps(metadata), encoding="utf-8")
            errors = []
            check_metadata(root, errors)
            self.assertTrue(any("creators differs" in error for error in errors), errors)


class RepositoryFailureTests(unittest.TestCase):
    def test_partial_repository_exits_nonzero(self):
        repository = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            subprocess.run(["git", "init", "--quiet", str(root)], check=True)
            (root / "README.md").write_bytes(b"# README\r\n[broken](absent.md)")
            result = subprocess.run(
                [__import__("sys").executable, str(repository / "scripts/validate_repository.py"), "--root", str(root)],
                capture_output=True, text=True, encoding="utf-8", check=False,
            )
            self.assertEqual(result.returncode, 1, result.stderr)
            for diagnosis in ("missing required file", "missing local target", "expected LF", "missing final newline", "require exactly one document"):
                self.assertIn(diagnosis, result.stdout)


if __name__ == "__main__":
    unittest.main()
