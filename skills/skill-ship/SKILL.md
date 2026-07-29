---
name: skill-ship
description: Ship any agent skill into the imsovikde/souvik-skills marketplace end to end. Use when the user wants to publish, upload, add, or release a skill to their marketplace; audit or verify whether a skill folder is marketplace-compliant; scaffold a brand-new skill; or adopt a third-party skill into the repository by stripping telemetry, analytics, outbound network calls, and vendor-specific wiring so it becomes a self-contained personal skill. Handles the full repository protocol without needing prior session context: structure, per-skill plugin manifests, every marketplace surface (Claude Code, Cowork, Codex, Antigravity, npm), the Next.js catalog, branch and pull-request flow, owner-only attribution with no AI co-author trailers, verified merges, and the release-please to npm publish chain.
---

# Skill Ship

Take a skill from anywhere — a new idea, a folder in another project, or a third-party skill copied off the internet — and land it in `imsovikde/souvik-skills` correctly, publicly, and verified, with no manual cleanup left for the user.

Read `references/skill-ship.md` before acting. It is the durable knowledge base for this repository: exact directory shape, every file that must change when a skill is added, the commit and merge protocol, and the release chain. Do not reconstruct these facts from memory or guesswork — session context is routinely lost, and that reference exists so the protocol survives it.

## Modes

Pick the mode from what the user has:

- **Create**: no skill exists yet. Scaffold one, then ship it.
- **Audit**: a skill exists; only report compliance. Change nothing unless asked.
- **Adopt**: a third-party skill exists. Make it self-contained and personal, then ship it.
- **Ship**: a compliant skill exists. Publish it.

Every mode ends by running the preflight script. Ship and Adopt also run the publish protocol.

## Required Preflight

Run this before any commit, in every mode:

```bash
node skills/skill-ship/scripts/preflight.cjs <path-to-skill-folder>
```

It deterministically checks naming, frontmatter, `agents/openai.yaml`, the per-skill `.claude-plugin/plugin.json`, forbidden files, hardcoded secrets, and telemetry or outbound-network indicators. Fix every reported failure and re-run until it exits clean. The script reports; you do the fixing — it never edits files.

## Adopting A Third-Party Skill

The goal is a skill that runs entirely locally and sends nothing anywhere.

1. Read every file in the source skill before changing it, including scripts and references.
2. Remove telemetry, analytics, usage pings, crash/error reporting, remote feature flags, and any hardcoded external endpoint the skill's own workflow does not require. A skill whose actual purpose is calling an API (a search or conversion service) keeps that call — remove *tracking*, not *function*. State which calls you kept and why.
3. Remove vendor-specific install wiring, other marketplaces' manifests, and unrelated CI that does not apply here.
4. Rewrite `SKILL.md` frontmatter and body to this repository's standard, and rename the folder to the chosen skill name so folder and `name` match exactly.
5. Preserve upstream licence and attribution. If the source carries a licence or NOTICE, keep it inside the skill folder and note the origin in the skill's `references/`. Stripping telemetry is privacy hardening and is fine; stripping someone's copyright notice is not, and the repository standard already requires preserving legal notices and provenance. If the upstream licence is missing, unclear, or incompatible with MIT redistribution, stop and tell the user before shipping.
6. Re-run preflight until clean.

## Publish Protocol

Follow `references/skill-ship.md` for the exact file list. In summary:

1. Confirm GitHub auth is usable, and that the working tree is the real repository (clone it first if running from another project).
2. Place the skill at `skills/<skill-name>/` with `SKILL.md`, `agents/openai.yaml`, `.claude-plugin/plugin.json`, and only the resources it needs.
3. Update every surface together: `.claude-plugin/marketplace.json`, `codex-plugin.json`, `README.md`, and `package.json` when a test script is added.
4. Set the new entry's `version` to the current `package.json` version. Release-please owns version bumps; never hand-bump.
5. Run `npm run validate:skills`, `npm test`, and `npm run build`. All must pass.
6. Commit on a feature branch with `Souvik Dey <imsovikde@gmail.com>`, a Conventional Commit subject starting `feat:`, and **no** `Co-Authored-By` or assistant-identity trailers.
7. Push, open a pull request, and merge it through the GitHub API or web UI so GitHub signs the squash commit and it lands **Verified**. A direct unsigned push to `main` is not an acceptable substitute.
8. Confirm the merged commit reports `verified: true` and is attributed to `imsovikde`.
9. Release-please opens a version/changelog pull request. Merge it too — that fires `npm-publish.yml`, which publishes to npm and GitHub Packages with provenance.
10. Confirm the new version is live with `npm view @imsovikde/skills version`.

## Marketplace Coverage

A shipped skill must work across every surface this repository targets. The same `SKILL.md` standard serves Claude Code, Cowork, Codex, Antigravity, Cursor, and Gemini CLI, so correct structure is what makes it universal — there is no per-marketplace rewrite. `references/skill-ship.md` lists each surface and the file that carries it.

## Verification

Before reporting done:

- Preflight exits clean.
- `npm run validate:skills`, `npm test`, and `npm run build` pass.
- The merged commit is Verified, authored only by the owner, with no AI trailers.
- The skill appears in `marketplace.json`, `codex-plugin.json`, and `README.md`.
- The release pull request is merged and the new npm version is live, or the user was told exactly what remains.

Report what ran, what passed, and anything skipped. Never claim a step succeeded without having checked it.
