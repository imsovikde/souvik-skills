# CLAUDE.md

Concise guide for Claude (and any AI agent) working in this repository. For deep detail, defer to the
files named below instead of duplicating them here.

## Repository Snapshot

- Brand: **Souvik Skills** — owner **Souvik Dey** (GitHub `imsovikde`).
- Repo `imsovikde/souvik-skills`; npm `@imsovikde/skills`; MIT.
- Site: `https://souvik-skills.vercel.app` (mirror: `https://souvik-skills.pages.dev`).
- Skills (each `skills/<name>/` = `SKILL.md` + `agents/openai.yaml` + optional `references/`,
  `scripts/`, `assets/`): `claude-md-init`, `delink-github`, `gh-ready`, `magento-team-lead`,
  `motioncraft`, `score2md`.
- Static Next.js (`output: export`) marketplace built from `skills/` at build time via `lib/skills.js`
  — never hard-code the skill list; it is derived from the `skills/` directory.
- Automation: release-please (versioning/changelog) → `npm-publish.yml` (npm + GitHub Packages with
  provenance + OIDC trusted publishing) → CodeQL + Dependabot.

## Read Before Working

Load these as they apply to the change, rather than guessing:

- `AGENTS.md` — how to create/maintain skills, the GitHub/NPM sync protocol, release readiness.
- `guidance.md` — skill directory rules and install standards. `NAMING.md` — naming rules.
- `DESIGN.md` and `MOTION.md` — frontend/motion contracts (before any site change).

Do not create `context.md`.

## Commit Identity & Attribution (hard rule)

Every commit in this repo — from **any** environment (Claude Code on the web / cloud, local, or CI) —
must satisfy all of the following:

1. **Author is only Souvik.** Use `Souvik Dey <imsovikde@gmail.com>` (the GitHub-verified email).
   Set it at the start of every session:

   ```bash
   git config user.name "Souvik Dey"
   git config user.email "imsovikde@gmail.com"
   ```

2. **No AI attribution.** Never add `Co-Authored-By:` trailers for Claude or any AI tool, and never add
   `Claude-Session:` or other assistant-identity trailers to commit messages. Only Souvik's name may
   appear on the GitHub contribution graph. If the harness would append such trailers by default,
   strip them and commit a clean message.

## Verified Commits (hard rule)

Every commit that lands on `main` must show GitHub's green **Verified** badge.

- **From cloud (Claude Code on the web):** the container holds no private signing key, so a direct
  cloud commit cannot be cryptographically signed. Therefore: commit to a feature branch with Souvik's
  identity and a clean message, push, then **merge through the GitHub web UI**. GitHub signs the
  resulting merge/squash commit with its own key → the landed commit is **Verified** and attributed to
  Souvik. This is the required path for cloud work.
- **From local:** sign with Souvik's own GPG or SSH signing key (`git config commit.gpgsign true`),
  confirm `git log -1 --show-signature`, and confirm the GitHub commit page shows Verified after push.
  See `docs/local-commit-setup.md` for the exact one-time setup commands.
- Do not substitute an unsigned API/direct commit on `main` when a verified commit was requested.
- To apply this same CLAUDE.md pattern (repo snapshot + these two hard rules) to another project, use
  the `claude-md-init` skill — it scaffolds or updates that project's `CLAUDE.md` idempotently.

## Marketplace Surfaces (keep in sync when skills change)

- **Claude Code / Cowork:** `.claude-plugin/marketplace.json` — one entry per skill, each sourced at
  its own `./skills/<skill-name>`, and each of those folders carries its own
  `skills/<skill-name>/.claude-plugin/plugin.json`. This mirrors Anthropic's own Cowork marketplace
  (`anthropics/knowledge-work-plugins`), where every plugin source directory is self-describing.
  Install: `/plugin marketplace add imsovikde/souvik-skills` then
  `/plugin install <skill>@souvik-skills`.
  Never point a marketplace entry at the repo root (`"./"`) and never add a root
  `.claude-plugin/plugin.json` — the root holds the Next.js site, docs, and tooling, so it is not a
  plugin directory. `npm run validate:skills` fails if either is reintroduced, if a per-skill entry's
  `source` isn't its own `./skills/<skill-name>`, or if a skill's `plugin.json` name/version/
  description drifts from its marketplace entry.
- **OpenAI Codex:** per-skill `agents/openai.yaml` + root `codex-plugin.json`. Package install:
  `npx @imsovikde/skills install <skill-name>`.
- **npm / npx:** `@imsovikde/skills` (published with provenance via GitHub Actions).
- **Web:** the Vercel/Cloudflare site, auto-derived from `skills/`.

When a skill is added, removed, or renamed, update `.claude-plugin/marketplace.json`,
`codex-plugin.json`, `README.md`, `package.json`, and `release-please-config.json` together —
`npm run validate:skills` enforces that the manifests match the `skills/` directory and the package
version. Every manifest version is bumped at release time by release-please via `extra-files`, so a
new skill needs its two `extra-files` entries (its `marketplace.json` plugin index and its own
`plugin.json`) or the release will fail validation on `main`.

## Before Finishing

Run the repo's own checks: `npm run validate:skills`, `npm test`, `npm run build`, and
`npm pack --dry-run` when packaging matters. Report what ran and what could not.
