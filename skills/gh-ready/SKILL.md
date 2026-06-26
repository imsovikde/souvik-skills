---
name: gh-ready
description: Prepare repositories for professional GitHub publication, open-source release, NPM or package distribution, client delivery, hiring showcase, product launch, or handoff. Use when Codex needs to improve README quality, license readiness, package metadata, repository hygiene, community health files, issue and pull request templates, CI, tests, linting, release process, security policy, Dependabot, CodeQL/code scanning, secret hygiene, branch protection guidance, CODEOWNERS, changelogs, badges, docs, examples, AGENTS.md, or overall repository trustworthiness.
---

# GH Ready

This skill helps Codex make a repository look trustworthy, maintained, safe, and easy to use.

## Required Reference

Read `references/gh-ready.md` before making substantial repo changes. For a small README-only request, use the quick workflow and load the reference if scope expands.

## Quick Workflow

1. Inspect the repo root, README, license, package files, tests, CI, `.github/`, docs, examples, and Git status.
2. Determine the audience: open source users, contributors, recruiters, enterprise buyers, internal handoff, or package consumers.
3. Audit professional signals:
   - clear identity and README
   - install/use examples
   - license and attribution
   - contribution and security policy
   - tests, lint, typecheck, build
   - CI and release automation
   - issue/PR templates
   - branch protection recommendations
   - dependency and secret hygiene
   - changelog/releases
4. Make low-risk file additions or edits only when requested. Avoid destructive cleanup without explicit confirmation.
5. Preserve legal notices and third-party licenses.
6. Run available tests, lint, typecheck, build, or repo audit scripts after changes.
7. End with a release-readiness status and remaining manual GitHub settings.

## Repo Upgrade Principles

- A professional repo explains what it is, why it exists, how to run it, how to trust it, and how to contribute.
- The README is a product surface, not a dumping ground.
- CI must verify the commands that the README tells users to run.
- Security policy, secret scanning, dependency updates, and branch protections matter as much as presentation.
- Public readiness includes removing private traces, old branding, analytics secrets, generated junk, and confusing dead files.
- Never remove license or attribution text casually.
- Never rewrite Git history or delete large file groups without explicit confirmation.

## Common Deliverables

- `README.md`
- `LICENSE`
- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `SUPPORT.md`
- `CHANGELOG.md`
- `.github/ISSUE_TEMPLATE/*.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `.github/workflows/ci.yml`
- `.editorconfig`
- `.gitattributes`
- `.env.example`
- `AGENTS.md`

## Final Readiness Status

Use one of:

- `release-ready`: no blocking professionalization issues found.
- `needs GitHub settings`: files are ready, but branch protection, security features, topics, or social preview must be configured in GitHub UI/API.
- `needs implementation`: CI/tests/docs/security files are missing or incomplete.
- `unsafe to publish`: secrets, licensing uncertainty, private traces, broken builds, or unresolved provenance issues remain.
