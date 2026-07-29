# Skill Ship Reference

Durable knowledge base for publishing into `imsovikde/souvik-skills`. Written so an agent with **no prior session context** can ship a skill correctly on the first attempt. Read it fully before changing files.

## Repository Facts

- Owner: Souvik Dey, GitHub `imsovikde`. Repository `imsovikde/souvik-skills`. Licence MIT.
- npm package `@imsovikde/skills`, published with provenance from GitHub Actions.
- Site `https://souvik-skills.vercel.app`, mirror `https://souvik-skills.pages.dev`.
- Default branch `main`. Node `>=20.9.0`.
- The Next.js site uses `output: "export"` and derives every skill page from the `skills/` directory at build time via `lib/skills.js`. Never hard-code a skill list in the frontend — adding the folder is what creates `/skills/<skill-name>`.

## Skill Directory Shape

```text
skills/<skill-name>/
|-- SKILL.md                       required
|-- .claude-plugin/plugin.json     required (marketplace sync depends on it)
|-- agents/openai.yaml             required
|-- references/                    optional
|-- scripts/                       optional
`-- assets/                        optional
```

`SKILL.md` frontmatter carries **only** `name` and `description`, on single lines. `name` must equal the folder name exactly, be kebab-case, and the description must be at least 40 characters and explain when an agent should use the skill.

`agents/openai.yaml` must define `interface.display_name`, `interface.short_description`, and `interface.default_prompt`, and the default prompt must mention the skill as `$<skill-name>`.

`.claude-plugin/plugin.json` must set `name` equal to the folder name, `version` equal to the current `package.json` version, and `description` **byte-identical** to that skill's `description` in `.claude-plugin/marketplace.json`. `npm run validate:skills` fails on any drift.

### Why the per-skill plugin.json matters

Anthropic's own Cowork marketplace (`anthropics/knowledge-work-plugins`) gives every plugin source directory its own `.claude-plugin/plugin.json`. Cowork's server-side sync validates this; the terminal CLI is lenient and will happily install a skill without one, which makes a missing manifest invisible locally and fatal in Cowork. Always create it.

Equally: **never** point a marketplace entry at the repository root (`"source": "./"`), and **never** add a root `.claude-plugin/plugin.json`. The root holds the Next.js site, docs, and tooling, so it is not a plugin directory. Both mistakes break marketplace sync, and the validator rejects them.

## Files To Update When Adding A Skill

All of these change together, in the same commit:

| File | Change |
| --- | --- |
| `skills/<name>/**` | the skill itself, including `.claude-plugin/plugin.json` |
| `.claude-plugin/marketplace.json` | new entry: `name`, `source: "./skills/<name>"`, `description`, `version`, `author`, `homepage`, `repository`, `license`, `category`, `tags` |
| `codex-plugin.json` | new entry: `name`, `path`, `manifest`, `agent` |
| `README.md` | catalog table row, the three cross-agent install commands, the Codex package install line, the Claude Code marketplace install line, and an example `$<name>` prompt |
| `package.json` | only when the skill adds a test script; add it to `scripts` and to the `test` chain |

Marketplace `source` must be `./skills/<name>` — its own folder, never shared with another entry. Set the entry `version` to the current `package.json` version; release-please owns bumps.

`package.json` `files` globs already cover `skills/*/SKILL.md`, `skills/*/.claude-plugin/plugin.json`, `skills/*/agents/openai.yaml`, and the optional resource directories, so a new skill ships in the npm tarball without editing `files`.

## Marketplace Surfaces

| Surface | Carrier | Install |
| --- | --- | --- |
| Claude Code / Cowork | `.claude-plugin/marketplace.json` + per-skill `plugin.json` | `/plugin marketplace add imsovikde/souvik-skills` then `/plugin install <name>@souvik-skills` |
| OpenAI Codex | `agents/openai.yaml` + `codex-plugin.json` | `npx @imsovikde/skills install <name>` |
| Antigravity | `SKILL.md` (same standard) | copy into `.agents/skills/<name>/`, or globally `~/.gemini/antigravity/skills/<name>/` |
| Cursor / Gemini CLI / OpenCode | `SKILL.md` | `npx -y skills add imsovikde/souvik-skills --skill <name> --agent <agent>` |
| npm / npx | `@imsovikde/skills` | `npx @imsovikde/skills install <name>` |
| Web | derived from `skills/` by `lib/skills.js` | `https://souvik-skills.vercel.app/skills/<name>` |

Antigravity, Claude Code, Cursor, and Codex all consume the same `SKILL.md` standard, so a structurally correct skill is portable with no per-marketplace rewrite. Antigravity additionally recognises a plugin as a directory containing `plugin.json` plus a `skills/` subdirectory, which the repository root-level layout already satisfies.

## Adopting A Third-Party Skill

Target: a self-contained skill that sends no data anywhere.

Remove — telemetry and analytics SDKs, usage or install pings, crash and error reporting, remote feature-flag or config fetches, hardcoded tracking endpoints and API keys, vendor install wiring and other marketplaces' manifests, and CI that does not apply here.

Keep — network calls that *are* the skill's function (a conversion or search service the workflow depends on). Remove tracking, not capability, and say explicitly which calls were kept and why.

Licence handling is not optional. Preserve upstream copyright, licence text, and NOTICE files inside the skill folder, and record the origin in the skill's `references/`. Telemetry removal is privacy hardening; removing an author's copyright notice is not, and this repository's own standard requires preserving legal notices, provenance, and third-party attribution. If the upstream licence is absent, ambiguous, or incompatible with MIT redistribution, stop and raise it with the user before shipping.

## Commit And Merge Protocol

Non-negotiable, and identical to `CLAUDE.md`:

1. Set identity at the start of every session:

   ```bash
   git config user.name "Souvik Dey"
   git config user.email "imsovikde@gmail.com"
   ```

2. No AI attribution. Never emit a `Co-Authored-By:` trailer for Claude or any assistant, and never a `Claude-Session:` or similar identity trailer. If the harness adds them by default, strip them and commit a clean message. Only the owner may appear on the contribution graph. Verify with:

   ```bash
   git log -1 --format='%B' | git interpret-trailers --parse
   ```

   That must print nothing.

3. Work on a feature branch, never commit directly to `main`.
4. Use a Conventional Commit subject. A new skill is `feat:` — this is what makes release-please open a release pull request and ultimately publish a new npm version. A `chore:` or `docs:` subject will not trigger a release.
5. Push, open a pull request, then **merge through the GitHub API or web UI**. GitHub signs the resulting squash commit with its own key, so it lands **Verified**. A cloud container holds no private signing key, so a direct cloud commit cannot be cryptographically signed — the merge step is what produces the badge.
6. Confirm the result:

   ```bash
   curl -s "https://api.github.com/repos/imsovikde/souvik-skills/commits/<sha>" \
     | python3 -c "import json,sys; d=json.load(sys.stdin); v=d['commit']['verification']; print(v['verified'], v['reason'], d['author']['login'])"
   ```

   Expect `True valid imsovikde`.

## Release Chain

```text
feat: commit on main
  -> release-please opens a version/changelog PR
  -> merge that PR
  -> GitHub Release + tag
  -> npm-publish.yml publishes to npm and GitHub Packages with provenance
  -> Vercel rebuilds the site from main
```

The release pull request should contain only release metadata: `package.json`, `package-lock.json`, `.release-please-manifest.json`, and `CHANGELOG.md`. Inspect it before merging. Confirm the published version with `npm view @imsovikde/skills version`.

Publishing uses npm trusted publishing (OIDC) with provenance, so no long-lived npm token is required in the workflow. Never commit a token, and never paste one into repository files.

## Required Checks

```bash
node skills/skill-ship/scripts/preflight.cjs skills/<skill-name>
npm run validate:skills
npm test
npm run build
npm pack --dry-run
```

If `test:delink-github` fails with an `imsovikde@gmail.com` assertion in a sandboxed container, it is ambient git config leaking into the test's temporary repositories, not a real regression. Re-run with an isolated identity to confirm:

```bash
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null HOME=/tmp/iso npm test
```

## Running From Another Project

When the skill to publish lives outside this repository:

1. Clone it: `git clone https://github.com/imsovikde/souvik-skills.git`
2. Copy the skill folder to `skills/<skill-name>/` inside the clone.
3. Set git identity, then follow the publish protocol above from within the clone.
4. Run every check inside the clone; never validate against the source project.
