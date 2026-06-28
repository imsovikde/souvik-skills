---
name: gh-ready
description: Prepare repositories for professional GitHub publication, open-source release, NPM/package distribution, client delivery, hiring showcase, product launch, or handoff. Use when Codex needs to make a repository trustworthy, SEO/AEO/GEO discoverable, package-ready, release-ready, badge-ready, security-ready, AI-agent-ready, and human-maintained through README quality, GitHub metadata, topics, social preview guidance, package metadata, docs, examples, interactive demo/docs pages, community health files, issue and pull request templates, CI, tests, linting, CodeQL/code scanning, Dependabot, secret hygiene, branch protection guidance, CODEOWNERS, changelogs, GitHub Releases, npm provenance, and CLI-driven GitHub readiness.
---

# GH Ready

Make a repository look and behave like a serious public project: discoverable, runnable, secure, releasable, and maintained.

## Required Reference

Read `references/gh-ready.md` before substantial repo, package, release, SEO, or automation work. For a tiny README-only cleanup, use the quick protocol first and load the reference if scope expands.

Optional resources:

- Run `scripts/audit-gh-ready.cjs <repo>` for a read-only readiness score and gap report.
- Use `assets/templates/` for concise community-file, README-section, issue, PR, release-note, and env-example starters.

## Quick Protocol

1. Inspect with tools before editing:
   - `git status --short`
   - repo tree, README, license, docs, examples, package manifests, tests, CI, `.github/`, changelog, releases, and agent guidance
   - `gh repo view --json name,description,homepageUrl,isPrivate,repositoryTopics,defaultBranchRef` when `gh` is available
   - `npm view <package> --json` and `npm pack --dry-run` for npm packages
2. Identify the audience: open source users, package consumers, recruiters, enterprise buyers, internal handoff, or product-launch visitors.
3. Score the repo using the 50-point standard in `references/gh-ready.md` or the bundled audit script.
4. Upgrade the files and pages that create trust first: README, license, package metadata, install/use examples, CI, security, contribution, issue/PR templates, changelog/releases, docs, examples, badges, AGENTS.md, and interactive demo/docs pages when the repository benefits from a browsable product surface.
5. Make the README visually useful, not just compliant: badge row, concise hero copy, quick-link buttons, screenshot or terminal preview when relevant, feature cards/tables, copyable commands, and links to live demo, docs, examples, releases, package, support, and security.
6. Make the first screen SEO/AEO/GEO friendly: clear title, one-sentence value proposition, accurate badges, keywords in natural language, copyable quick start, and links to package, docs, demo, interactive pages, releases, support, and security.
7. Prepare releases: verify version, changelog, tag/release notes, dry-run package contents, provenance support, and publish workflow.
8. Verify with the repo's actual commands: install, lint, typecheck, test, build, validation, package dry-run, and link checks when available.
9. End with readiness status, score, changes made, commands run, release next steps, and manual GitHub settings.

## Live GitHub Safety

Use GitHub CLI/API to inspect freely. Before changing live GitHub settings, show the exact command and wait for explicit approval. This applies to:

- repository description, homepage, topics, and social preview
- branch protection, rulesets, merge settings, and required checks
- security features, secret scanning, Dependabot alerts, and code scanning
- GitHub Releases, tags, package publishing, and repository secrets

Never commit tokens. Prefer npm trusted publishing and GitHub OIDC over long-lived npm automation tokens.

## Repo Upgrade Principles

- Treat the README as the repository's product page.
- For UI, CLI, package, agent, docs, or tool repositories, create or improve browsable docs/demo pages when they help visitors understand the project faster; then link those pages from README.
- GitHub README files are mostly Markdown, not application surfaces. Do not fake JavaScript interactivity inside README; use badges, images, links, collapsible details, tables, and hosted pages for real interaction.
- Trust is operational: install commands work, CI proves them, releases are explainable, and security reporting is obvious.
- Badges are promises. Add only live, accurate badges that match real automation or published artifacts.
- SEO/AEO/GEO readiness means a human, search engine, and AI answer engine can quickly understand what the repo is, who it is for, how to use it, and why it is credible.
- Preserve legal notices, provenance, authorship, and third-party attribution.
- Avoid destructive cleanup, history rewriting, or live setting changes without explicit confirmation.

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
- `.github/workflows/release.yml` or release automation
- `.editorconfig`
- `.gitattributes`
- `.env.example`
- `docs/`
- interactive demo/docs pages when relevant
- `examples/`
- `AGENTS.md`

## Final Readiness Status

Use one of:

- `release-ready`: no blocking professionalization issues found.
- `needs GitHub settings`: files are ready, but branch protection, security features, topics, or social preview must be configured in GitHub UI/API.
- `needs implementation`: CI/tests/docs/security files are missing or incomplete.
- `unsafe to publish`: secrets, licensing uncertainty, private traces, broken builds, or unresolved provenance issues remain.
