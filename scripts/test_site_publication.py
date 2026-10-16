"""Regression tests for destructive-path and deployment authorization boundaries."""

import tempfile
import unittest
from pathlib import Path

from build_site import clean_output
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


if __name__ == "__main__":
    unittest.main()
