# GH Ready Reference

Production Standard for Professional GitHub Repositories

## Purpose

A professional GitHub repository should make the project easy to understand, safe to evaluate, reliable to run, and trustworthy to contribute to. It should also make maintainership visible: tests pass, releases are explainable, security reporting is clear, and users know what to do next.

This standard is for AI coding agents preparing repositories for public release, open source, client delivery, hiring showcase, product launch, package distribution, or team handoff.

## Research Basis

This standard synthesizes:

- GitHub repository best practices and community profile guidance.
- GitHub community health files: README, license, code of conduct, contributing guidelines, security policy, issue templates, and pull request templates.
- GitHub protected branch and ruleset guidance: required reviews, status checks, conversation resolution, signed commits, linear history, and merge queues.
- GitHub security features: Dependabot, code scanning, dependency review, secret scanning, and push protection.
- Common release engineering practices: semantic versions, changelogs, signed/provenance-aware releases, CI verification, and package metadata.
- Practical repository polish used by high-trust open-source and commercial projects.

## Professional Repo Goals

1. Identity: visitors understand the project in under 30 seconds.
2. Usability: users can install, run, test, and troubleshoot without guessing.
3. Trust: license, security policy, CI, tests, and release process are visible.
4. Contribution: issues, PRs, code owners, and contribution rules are clear.
5. Maintainability: repo structure, docs, automation, and versioning can scale.
6. Safety: secrets, private traces, stale branding, and accidental artifacts are absent.
7. AI readiness: agents can understand rules, commands, architecture, and review expectations.

## Quick Scoring Rubric

Score each category from 0 to 5:

- Identity and README
- Install and usage docs
- Architecture and API docs
- Tests and quality gates
- CI and branch protection
- Security posture
- Community health files
- Release process
- Repo hygiene
- AI/developer guidance

Interpretation:

- 45-50: professional and release-ready.
- 35-44: credible, with polish gaps.
- 25-34: usable but not fully professional.
- 0-24: not ready for public release or serious handoff.

## Repository Identity

Required:

- Clear repository name.
- Concise description in GitHub settings.
- Relevant topics/tags.
- Social preview image for product-facing repos.
- `README.md` with a direct explanation of the project.
- `LICENSE` unless the project is intentionally private/internal.
- Package metadata matches the public project name.

Recommended:

- Logo or screenshot when the project has a UI.
- Demo GIF/video only if it is small, current, and useful.
- Hosted demo link if safe and maintained.
- Badges for CI, package version, license, coverage, docs, or security only when they are accurate.

Avoid:

- Badge clutter.
- Marketing claims without runnable examples.
- Stale screenshots.
- Private URLs or old product names.

## README Standard

Use this structure unless the project has a better established format:

1. Project name and one-sentence value proposition.
2. Screenshot, terminal example, or minimal demo for visual projects.
3. What it does.
4. Why it exists or what problem it solves.
5. Installation.
6. Quick start.
7. Common commands.
8. Configuration and environment variables.
9. Usage examples.
10. Project structure.
11. Testing.
12. Deployment or release notes, if applicable.
13. Security and privacy notes.
14. Contributing.
15. License.

Quality rules:

- The first screen must answer "What is this?" and "Should I care?"
- The quick start must be copy-pasteable.
- Commands must match actual package scripts and CI.
- Mention supported platforms and versions.
- Include `.env.example` instead of real secrets.
- Link deeper docs instead of making the README enormous.
- Keep examples current and tested.

## Essential Files

### Root Files

- `README.md`: primary public entry point.
- `LICENSE`: legal terms for use.
- `CHANGELOG.md`: notable changes by version/date.
- `CONTRIBUTING.md`: how to set up, branch, test, and submit PRs.
- `CODE_OF_CONDUCT.md`: behavior standards for public communities.
- `SECURITY.md`: vulnerability reporting process and supported versions.
- `SUPPORT.md`: where users get help.
- `CITATION.cff`: academic/research projects.
- `.gitignore`: generated and secret files excluded.
- `.gitattributes`: line endings, linguist overrides, generated files.
- `.editorconfig`: formatting consistency across editors.
- `.env.example`: documented environment variables without secrets.
- `AGENTS.md`: instructions for AI coding agents.

### `.github/` Files

- `.github/ISSUE_TEMPLATE/bug_report.yml`
- `.github/ISSUE_TEMPLATE/feature_request.yml`
- `.github/ISSUE_TEMPLATE/config.yml`
- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/CODEOWNERS`
- `.github/dependabot.yml`
- `.github/workflows/ci.yml`
- `.github/workflows/release.yml` when releases are automated.
- `.github/FUNDING.yml` when relevant.

## CONTRIBUTING.md Standard

Include:

- Development prerequisites.
- Setup commands.
- Test/lint/typecheck/build commands.
- Branch naming convention.
- Commit message convention if used.
- Pull request expectations.
- Code style and formatting.
- How to add tests.
- How to update docs.
- How to report bugs responsibly.

Keep it friendly and concrete.

## SECURITY.md Standard

Include:

- Supported versions.
- Private vulnerability reporting channel.
- Expected response window.
- What information to include in a report.
- Request not to open public issues for vulnerabilities.
- Link to GitHub private vulnerability reporting if enabled.

Do not ask reporters to disclose sensitive details publicly.

## Issue And PR Templates

Bug report fields:

- Summary.
- Environment.
- Steps to reproduce.
- Expected behavior.
- Actual behavior.
- Logs/screenshots.
- Regression version if known.

Feature request fields:

- Problem.
- Proposed solution.
- Alternatives considered.
- Use case.
- Impact.

Pull request template:

- Summary.
- Motivation.
- Changes.
- Tests run.
- Screenshots or recordings for UI.
- Breaking changes.
- Checklist for docs, tests, and security.

## CI Standard

Minimum CI should run on pull requests and the default branch:

- dependency installation with lockfile integrity
- format check
- lint
- typecheck, if applicable
- unit tests
- build

Add when relevant:

- integration tests
- end-to-end tests
- coverage upload
- package publish dry run
- docs build
- container build
- security scan
- license check

CI rules:

- CI commands must match README commands.
- Keep job names unique so branch protection can target them clearly.
- Use caching, but do not cache secrets.
- Set least-privilege GitHub Actions permissions.
- Avoid broad write tokens.
- Pin third-party Actions to trusted versions; pin to SHAs for high-security projects.

Example workflow shape:

```yaml
name: CI

on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  test:
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

Adapt package manager and language versions to the repo.

## Branch Protection And Rulesets

Recommend these GitHub settings for the default branch:

- Require pull request before merge.
- Require at least one approval.
- Require code owner review for owned paths.
- Dismiss stale approvals when new commits are pushed, for sensitive repos.
- Require status checks to pass.
- Require conversation resolution.
- Require branches to be up to date, or use merge queue for busy repos.
- Restrict force pushes.
- Restrict branch deletion.
- Consider signed commits for security-sensitive projects.
- Consider linear history for projects that prefer clean revertability.

Manual note:

Some branch protection settings must be configured in GitHub UI/API. File edits alone are not enough.

## Security Posture

Enable or configure:

- Dependabot alerts.
- Dependabot security updates.
- Dependabot version updates for supported ecosystems.
- Secret scanning.
- Push protection where available.
- Code scanning with CodeQL or equivalent.
- Dependency review for pull requests when available.
- Private vulnerability reporting for public projects.
- Security policy.

Repository hygiene:

- No `.env` files with real values.
- No private keys, tokens, cookies, database URLs, or OAuth secrets.
- No production analytics keys unless intentionally public and safe.
- No internal hostnames or customer data.
- No source maps containing private source in public releases unless intended.
- No logs with credentials.

If a secret was committed:

- Rotate/revoke the secret immediately.
- Remove it from current code.
- Consider history cleanup only with explicit confirmation and coordination.
- Do not claim deletion alone makes the secret safe.

## Release Standard

Recommended:

- Semantic versioning for libraries and APIs.
- Calendar versioning only when it fits the product.
- `CHANGELOG.md` with user-facing changes.
- GitHub Releases with release notes.
- Annotated tags.
- Automated release notes for larger projects.
- Package provenance/signing for packages where supported.
- Migration notes for breaking changes.

Release checklist:

- CI passes on the release commit.
- Version is updated in all package metadata.
- Changelog has date and version.
- Docs match behavior.
- Artifacts are generated reproducibly.
- Deprecated features are documented.
- Security notes are included when relevant.

## Documentation Structure

Small projects can keep docs in README. Larger projects should use:

```text
docs/
  getting-started.md
  configuration.md
  architecture.md
  api.md
  deployment.md
  troubleshooting.md
  security.md
examples/
  basic/
  advanced/
```

Architecture docs should explain:

- module boundaries
- data flow
- external services
- persistence
- auth/security model
- build/deployment pipeline
- testing strategy

## Codebase Hygiene

Before public release:

- Run tests and build.
- Run secret scanning.
- Search for old names, private emails, local paths, and internal URLs.
- Remove stale screenshots and logos.
- Remove generated files that do not belong in source.
- Remove dead branches from docs.
- Ensure `.gitignore` covers caches, build output, local env files, logs, and editor junk.
- Confirm license notices remain.
- Confirm dependency licenses are acceptable.
- Confirm package names, namespaces, app IDs, and URLs are public-ready.

Use a repo sanitization tool or audit skill for high-stakes cleanup.

## AI Agent Readiness

Add `AGENTS.md` when AI coding agents will work in the repo.

Include:

- Project overview.
- Setup commands.
- Test commands.
- Lint/typecheck/build commands.
- Architecture map.
- Coding style.
- Files to avoid editing without permission.
- Security and privacy rules.
- PR expectations.
- Verification checklist.

AI-ready repos reduce hallucinated commands and accidental broad refactors.

## Package Metadata

For packages:

- name, version, description
- license
- author/maintainers
- repository URL
- homepage/docs URL
- bugs URL
- keywords
- exports/files configuration
- supported engines/runtime versions
- publish access configuration

Make sure package metadata matches README and GitHub settings.

## Professional Trust Signals

Strong signals:

- Clear README with real examples.
- Recent passing CI.
- License is visible.
- Security policy exists.
- Releases and changelog exist.
- Maintainer response expectations are clear.
- Issues and PRs have templates.
- Tests are easy to run.
- Repo topics are relevant.
- Public demo or screenshots are current.

Weak signals:

- Broken badges.
- Empty docs folders.
- Stale roadmap.
- Install instructions that fail.
- Missing license.
- No tests or CI.
- Untriaged issue backlog.
- Vague "TODO" sections.
- Private traces or old product names.

## Implementation Workflow For Agents

1. Inspect:
   - `git status --short`
   - repo tree
   - README/license/community files
   - package metadata
   - scripts and tests
   - CI workflows
   - `.github/`
   - docs/examples
2. Identify audience and release risk.
3. Produce a gap report.
4. Make scoped edits:
   - README
   - community files
   - templates
   - CI
   - docs
   - metadata
5. Run verification.
6. Report manual GitHub settings.
7. Assign readiness status.

## Readiness Checklist

- [ ] README explains what, why, install, quick start, commands, configuration, tests, and license.
- [ ] License is present or private/internal status is explicit.
- [ ] Contributing guide exists for public or team repos.
- [ ] Security policy exists.
- [ ] Code of conduct exists for public community projects.
- [ ] Issue templates exist.
- [ ] PR template exists.
- [ ] CI runs lint/test/typecheck/build as applicable.
- [ ] Dependabot is configured.
- [ ] Secret scanning and code scanning are recommended or enabled.
- [ ] Branch protection/rulesets are documented.
- [ ] Changelog and release process exist.
- [ ] `.env.example` exists when environment variables are required.
- [ ] `.gitignore`, `.gitattributes`, and `.editorconfig` are appropriate.
- [ ] Package metadata is accurate.
- [ ] Docs/examples are current.
- [ ] No secrets, private traces, old branding, or local paths remain.
- [ ] Legal notices and attribution are preserved.
- [ ] AGENTS.md exists if agents will work in the repo.

## Source Links

- GitHub repository best practices: https://docs.github.com/en/repositories/creating-and-managing-repositories/best-practices-for-repositories
- GitHub community profiles: https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/about-community-profiles-for-public-repositories
- GitHub protected branches: https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches
- GitHub security features: https://docs.github.com/en/code-security/getting-started/github-security-features
- GitHub secret scanning: https://docs.github.com/en/code-security/concepts/secret-security/secret-scanning
