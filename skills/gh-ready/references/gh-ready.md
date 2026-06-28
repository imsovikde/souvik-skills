# GH Ready Reference

Professional Repository Launch Standard

## Purpose

Use this reference when preparing a repository for public GitHub release, open-source contribution, npm or package distribution, client delivery, hiring showcase, product launch, or internal handoff.

A finished repository should be:

- understandable in under 30 seconds
- runnable from copyable commands
- discoverable by GitHub search, package registries, search engines, and AI answer engines
- trustworthy through license, security, CI, releases, and provenance
- maintainable by humans and AI coding agents

## Research Basis

This standard follows current public guidance from GitHub repository best practices, community health files, security features, protected branches, GitHub Actions package publishing, Google Search Central SEO basics, npm trusted publishing and provenance, Shields badge conventions, and Release Please release automation.

## 50-Point Readiness Score

Score each category from 0 to 5.

1. Identity and positioning
2. README as product page
3. SEO, AEO, GEO, topics, and package keywords
4. Install, quick start, examples, and troubleshooting
5. Package metadata and package dry-run quality
6. CI, tests, lint, typecheck, and build verification
7. Security posture and secret hygiene
8. Community health files and contribution workflow
9. Release process, changelog, tags, and GitHub Releases
10. Docs, examples, and AI-agent readiness

Interpretation:

- 45-50: professional and release-ready
- 35-44: credible, with polish gaps
- 25-34: usable, but not fully professional
- 0-24: not ready for public release or serious handoff

## Operating Protocol

1. Inspect before editing:
   - `git status --short`
   - repo tree
   - README, license, changelog, package manifests
   - tests, scripts, CI workflows, docs, examples
   - `.github/` community and security files
   - package registry state when a package exists
2. Classify the repository:
   - library/package
   - app/site
   - CLI/tool
   - template/starter
   - skill/agent workflow
   - internal handoff
3. Identify the audience:
   - end users
   - contributors
   - package consumers
   - recruiters/hiring reviewers
   - enterprise/security reviewers
   - client stakeholders
   - AI coding agents
4. Produce a short gap report.
5. Make scoped file changes.
6. Verify with real commands.
7. Report manual GitHub settings and release steps.

## README As Product Page

Use this structure unless the repository already has a strong established format:

1. Project name and one-sentence value proposition
2. Accurate badges
3. Screenshot, terminal demo, or hosted demo link when relevant
4. What the project does
5. Why it exists and who it is for
6. Installation
7. Quick start
8. Common commands
9. Usage examples
10. Configuration and environment variables
11. Project structure
12. Testing and quality checks
13. Deployment or release instructions
14. Demo, docs, or interactive pages when relevant
15. Troubleshooting
16. Security and privacy
17. Contributing
18. Support
19. License

Quality rules:

- The first screen must answer "What is this?" and "Should I care?"
- The first command block must be copy-pasteable.
- Every command in README should match `package.json`, CI, Makefile, or actual scripts.
- Use deeper docs for detail; do not turn README into a dump.
- Include screenshots only when they are current and helpful.
- Link every useful interactive demo, docs page, package page, and hosted site from the README first screen or the closest relevant section.
- Do not make claims that tests, package metadata, or release history cannot support.

## SEO, AEO, And GEO Readiness

SEO helps search engines. AEO helps answer engines. GEO helps generative engines summarize the project accurately. For GitHub repositories, the practical work is clear metadata and copy.

Required:

- GitHub description uses natural keywords and explains the outcome.
- README title matches the project/package name.
- First paragraph states category, audience, and value.
- Important keywords appear naturally in headings and early copy.
- GitHub topics match the ecosystem and use case.
- Package keywords match README and GitHub topics.
- Homepage/docs/package links are current.
- Installation and quick-start commands are copyable.
- FAQ or troubleshooting answers likely user questions.
- License, support, security, and maintenance signals are visible.

Recommended:

- Social preview image for product-facing repositories.
- `docs/` pages for architecture, configuration, deployment, API, and troubleshooting on larger projects.
- `llms.txt` or docs index for documentation-heavy sites when the project intentionally targets AI-answer ingestion.
- Canonical links between GitHub, package registry, docs, demo, and release page.

Avoid:

- Keyword stuffing.
- Generic "AI powered" claims without examples.
- Badges or screenshots that imply features that do not exist.
- Empty docs sections.

## Interactive Pages And README Integration

For repositories with a UI, CLI, package, docs site, agent skill catalog, visual workflow, or product-like surface, create or improve browsable pages when they help visitors evaluate the project.

Good page targets:

- hosted homepage or landing page
- docs index
- getting-started page
- live demo or interactive playground
- examples gallery
- API/reference page
- release or changelog page
- troubleshooting page

Rules:

- Use external websites only as inspiration for structure, clarity, interaction patterns, and trust signals; do not copy proprietary UI, text, logos, or assets.
- If the repo already has a site, edit the existing site/pages instead of creating disconnected mockups.
- Add current screenshots, terminal demos, short GIF/video links, or interactive examples only when they are accurate and maintainable.
- Link new pages from `README.md`, package metadata `homepage`, GitHub repository homepage, and docs navigation when available.
- Verify local build output and route accessibility for every new page.
- Do not let pages become marketing fluff; every page should help install, understand, compare, debug, or trust the project.

## README Visual And Badge System

Use a polished README structure when the project is public-facing. Keep it fast to scan and honest.

Recommended first-screen order:

1. Project title
2. One-line value proposition
3. Focused badge row
4. Quick links row
5. Screenshot, terminal preview, or short demo link when relevant
6. Copyable install or quick-start command

Useful badge set:

```markdown
[![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/ci.yml)
[![CodeQL](https://github.com/<owner>/<repo>/actions/workflows/codeql.yml/badge.svg)](https://github.com/<owner>/<repo>/actions/workflows/codeql.yml)
[![npm version](https://img.shields.io/npm/v/<encoded-package-name>)](https://www.npmjs.com/package/<package-name>)
[![npm downloads](https://img.shields.io/npm/dm/<encoded-package-name>)](https://www.npmjs.com/package/<package-name>)
[![GitHub stars](https://img.shields.io/github/stars/<owner>/<repo>?style=social)](https://github.com/<owner>/<repo>/stargazers)
[![License](https://img.shields.io/github/license/<owner>/<repo>)](LICENSE)
```

Quick-link row pattern:

```markdown
[Website](<homepage>) · [Docs](docs/) · [Install](#installation) · [Examples](#examples) · [Releases](https://github.com/<owner>/<repo>/releases) · [Support](SUPPORT.md)
```

Feature-card table pattern:

```markdown
| Capability | What it gives users |
| --- | --- |
| Fast install | Copy-pasteable setup and quick start. |
| Verified quality | CI, tests, package dry-run, and security checks. |
| Clear release path | Changelog, GitHub Releases, and package provenance. |
```

Rules:

- Prefer 4-8 meaningful badges over a wall of badges.
- Add GitHub stars/forks/download badges only when they help visitors evaluate popularity or usage; do not pretend popularity exists.
- Use `for-the-badge` style only for brand-heavy landing-style READMEs; use flat/default styles for library docs.
- README visuals must degrade well in GitHub mobile and dark mode.
- Use hosted pages for actual interactivity; README can link, preview, collapse sections, and show badges, but it should not be treated like a web app.

## Badge Rules

Badges should reduce uncertainty, not decorate.

Good badges:

- CI/build status
- npm or package version
- license
- latest GitHub release
- CodeQL/security scan when configured
- coverage only when coverage is actually measured
- docs/deployment only when a stable docs/deploy target exists

Rules:

- Use live badge URLs from trusted sources such as GitHub Actions, npm, Shields, Codecov, or the docs host.
- Keep the first row to 3-6 badges.
- Validate that every badge target link opens.
- Remove broken or misleading badges.
- Do not add a coverage badge without coverage automation.

## Package Metadata Standard

For npm packages, verify:

- `name`
- `version`
- `description`
- `license`
- `author` or `maintainers`
- `repository`
- `homepage`
- `bugs`
- `keywords`
- `bin` or `exports` when applicable
- `files` or `.npmignore` limits package contents
- `engines`
- `publishConfig.access` for scoped public packages
- package scripts used by README and CI

Run:

```bash
npm view <package> --json
npm pack --dry-run
```

The dry-run output should include only intended source, docs, license, package metadata, and required runtime files.

## Release Standard

Professional releases need a repeatable story.

Required for package repositories:

- semantic version in package metadata
- changelog with user-facing changes
- release notes or GitHub Releases
- CI passes before publish
- package dry-run reviewed
- tags match package version
- publish path documented

Recommended:

- Release Please or equivalent release PR automation
- npm trusted publishing with GitHub OIDC
- `npm publish --provenance` when supported
- annotated or generated release notes
- migration notes for breaking changes

Never store npm tokens in the repository. If trusted publishing is unavailable, use a short-lived automation token only through secret storage and document rotation.

## GitHub Metadata And Settings

Inspect:

```bash
gh repo view --json name,description,homepageUrl,isPrivate,repositoryTopics,defaultBranchRef
gh workflow list
gh release list
```

Generate commands for approval before applying:

```bash
gh repo edit --description "<clear searchable description>" --homepage "<url>"
gh repo edit --add-topic topic-one --add-topic topic-two
gh release create vX.Y.Z --generate-notes
```

Branch protection, rulesets, secret scanning, push protection, private vulnerability reporting, and some security features may require GitHub UI/API access. Report exact next steps when they cannot be safely edited from files.

## Community Health Files

Add or improve:

- `CONTRIBUTING.md`
- `CODE_OF_CONDUCT.md`
- `SECURITY.md`
- `SUPPORT.md`
- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`

Keep these files concrete. Generic files are better than missing files, but professional files name the actual commands, support channels, ownership model, and security process.

## CI And Quality Gates

Minimum CI for Node/package repositories:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  verify:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: npm
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm run typecheck --if-present
      - run: npm test --if-present
      - run: npm run build --if-present
```

Add CodeQL, dependency review, package dry-run, docs build, or e2e checks when the repository needs them.

CI rules:

- Commands must match README.
- Job names should be stable for branch protection.
- Use least-privilege permissions.
- Do not expose secrets to pull requests.
- Pin third-party actions to trusted versions; pin SHAs for high-security repos.

## Security And Hygiene

Check for:

- committed `.env` files
- private keys, certificates, tokens, cookies, or database URLs
- local absolute paths
- private hostnames
- customer data
- generated logs and caches
- stale branding or old repository links
- source maps or built artifacts that expose private source

If a secret was committed:

1. Tell the user to rotate/revoke it.
2. Remove it from current files.
3. Consider history cleanup only with explicit confirmation.
4. Do not claim that deleting the file makes the secret safe.

## Documentation And Examples

Small projects can keep docs in README. Larger projects should use:

```text
docs/
  getting-started.md
  configuration.md
  architecture.md
  api.md
  deployment.md
  troubleshooting.md
examples/
  basic/
  advanced/
```

Architecture docs should explain module boundaries, data flow, external services, persistence, auth/security model, build/deployment pipeline, and testing strategy.

## AI-Agent Readiness

Add `AGENTS.md` when agents will work in the repo. Include:

- project overview
- setup commands
- test/lint/typecheck/build commands
- architecture map
- coding style
- files to avoid editing without permission
- security/privacy rules
- PR expectations
- verification checklist

AI-ready repositories reduce hallucinated commands and accidental broad refactors.

## Final Report Format

End with:

- readiness status
- score out of 50
- changed files
- commands run and results
- release/package state
- manual GitHub settings still needed
- risks or blockers

Use one status:

- `release-ready`
- `needs GitHub settings`
- `needs implementation`
- `unsafe to publish`

## Source Links

- GitHub repository best practices: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories
- GitHub community profiles: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories
- GitHub repository topics: https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
- GitHub protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub security features: https://docs.github.com/en/code-security/getting-started/github-security-features
- GitHub Actions package publishing: https://docs.github.com/en/actions/use-cases-and-examples/publishing-packages/publishing-nodejs-packages
- Google SEO starter guide: https://developers.google.com/search/docs/fundamentals/seo-starter-guide
- npm trusted publishing: https://docs.npmjs.com/trusted-publishers
- npm provenance: https://docs.npmjs.com/generating-provenance-statements
- Release Please: https://github.com/googleapis/release-please
- Shields badges: https://shields.io/badges
