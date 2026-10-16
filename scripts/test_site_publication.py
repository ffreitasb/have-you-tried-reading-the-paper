"""Regression tests for destructive-path and deployment authorization boundaries."""

import hashlib
import io
import json
import tarfile
import tempfile
import unittest
from pathlib import Path

from build_site import clean_output
from site_assets import prepare_assets
from validate_repository import PAGES_DEPLOY_GUARD, workflow_errors


class PublicationTests(unittest.TestCase):
    def workflow(self):
        return {
            "permissions": {"contents": "read"},
            "on": {"push": {}, "pull_request": {}, "workflow_dispatch": {}},
            "jobs": {"build": {"steps": []}, "deploy": {
                "if": PAGES_DEPLOY_GUARD, "needs": "build",
                "permissions": {"pages": "write", "id-token": "write"},
                "environment": {"name": "github-pages"},
            }},
        }

    def test_guarded_deployment(self):
        self.assertEqual(workflow_errors(self.workflow(), pages=True), [])

    def test_pr_cannot_deploy(self):
        for guard in (None, "always()", "github.event_name == 'pull_request'", "github.ref == 'refs/heads/main'"):
            workflow = self.workflow()
            workflow["jobs"]["deploy"]["if"] = guard
            self.assertTrue(workflow_errors(workflow, pages=True))

    def test_no_write_or_identity_in_build_or_other_workflows(self):
        for permission in ({"contents": "write"}, {"id-token": "write"}, "write-all"):
            workflow = self.workflow()
            workflow["jobs"]["build"]["permissions"] = permission
            self.assertTrue(workflow_errors(workflow, pages=True))
        self.assertTrue(workflow_errors(self.workflow(), pages=False))

    def test_build_cannot_configure_pages(self):
        workflow = self.workflow()
        workflow["jobs"]["build"]["steps"] = [{"uses": "actions/configure-pages@" + "a" * 40}]
        self.assertTrue(workflow_errors(workflow, pages=True))

    def test_cleanup_only_dedicated_outputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in ("docs", ".git", "validation-output", "other/site"):
                target = root / name
                target.mkdir(parents=True)
                with self.assertRaises(ValueError):
                    clean_output(root, target)
                self.assertTrue(target.is_dir())
            for name in ("site", ".site"):
                target = root / name
                target.mkdir()
                (target / "index.html").write_bytes(b"test")
                clean_output(root, target)
                self.assertFalse(target.exists())
            with self.assertRaises(ValueError):
                clean_output(root, root)

    def test_asset_checksum_mismatch_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "web").mkdir()
            cache = root / ".cache/downloads"
            cache.mkdir(parents=True)
            digest = hashlib.sha256(b"reviewed font").hexdigest()
            (cache / digest).write_bytes(b"tampered font")
            (root / "web/assets.lock.json").write_text(json.dumps({
                "test.woff2": {"url": "https://example.invalid/font", "sha256": digest},
            }))
            with self.assertRaisesRegex(ValueError, "checksum mismatch"):
                prepare_assets(root)

    def test_archive_traversal_is_rejected(self):
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            member = tarfile.TarInfo("package/es5/../../outside")
            member.size = 1
            archive.addfile(member, io.BytesIO(b"x"))
        data = buffer.getvalue()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "web").mkdir()
            cache = root / ".cache/downloads"
            cache.mkdir(parents=True)
            digest = hashlib.sha256(data).hexdigest()
            (cache / digest).write_bytes(data)
            (root / "web/assets.lock.json").write_text(json.dumps({
                "mathjax": {"url": "https://example.invalid/archive", "sha256": digest},
            }))
            with self.assertRaisesRegex(ValueError, "Unsafe archive member"):
                prepare_assets(root)
            self.assertFalse((root / ".cache/outside").exists())


if __name__ == "__main__":
    unittest.main()
