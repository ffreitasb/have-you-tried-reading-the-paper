# Security policy

This is primarily a knowledge repository. Its references, contribution artifacts, and GitHub Actions still create a security surface.

## Private reporting

Report malicious or compromised links, workflow/action supply-chain problems, exposed credentials or tokens, and malicious contribution artifacts privately to **contact@ffreitasb.cc**. Include the affected path or URL, relevant commit, impact, and safe reproduction details. Do not put active credentials or exploitable security details in a public issue or pull request. Do not execute a suspected malicious artifact to obtain a report.

The maintainer will investigate, coordinate remediation and disclosure with the reporter, and acknowledge the report when able. This single-maintainer project does not promise a fixed response deadline. If a credential is exposed, its owner should revoke or rotate it promptly; deleting a file or rewriting a page does not revoke a secret.

## Scope and maintenance

Security fixes are applied to the current `main` branch. Archived releases remain immutable references, not separately maintained security branches. A correction affecting a published release will be documented and, when needed, published in a new release.

GitHub Actions run with read-only repository permissions, immutable action pins, and no repository secrets in untrusted pull requests. Dependency updates require review. Contributors should verify reference destinations, avoid executable attachments, and keep credentials and local state out of contributions.

Ordinary technical inaccuracies or outdated scholarly references belong in the [structured issue forms](https://github.com/ffreitasb/have-you-tried-reading-the-paper/issues/new/choose). Use private reporting when disclosure would expose an active security problem.
