# AGENTS

This is the agent guide for Souvik Skills.

Before creating or changing a skill, read `guidance.md` and `NAMING.md`. Do not create `context.md`.

## Repository Facts

- Brand: Souvik Skills
- Owner: Souvik Dey
- GitHub owner: `imsovikde`
- Repository: `imsovikde/souvik-skills`
- NPM package: `@imsovikde/skills`
- License: MIT
- Current public skill names are derived from the `skills/` directory, not hard-coded in this guide.

## Agent Rules

1. Keep every skill folder self-contained and installable.
2. Keep `SKILL.md` concise and procedural.
3. Use only `name` and `description` in `SKILL.md` frontmatter.
4. Make the skill folder name exactly match the frontmatter `name`.
5. Put detailed optional material in `references/` and mention when to read it.
6. Put deterministic automation in `scripts/`.
7. Put reusable output assets in `assets/`.
8. Keep `agents/openai.yaml` aligned with `SKILL.md`.
9. Ensure `interface.default_prompt` mentions the skill as `$skill-name`.
10. Keep the README catalog and cross-agent NPX install matrix aligned with the `skills/` directory.
11. After creating or updating a skill for local Codex use, reinstall the updated skill into Codex and remind the user to restart Codex.
12. Do not add private traces, generated caches, local logs, or secrets.
13. Do not commit changes unless the user explicitly asks.
14. When the user explicitly asks to sync GitHub, update NPM/NPX, publish, release, or make the change globally available, follow the GitHub And NPM Sync Protocol end to end instead of stopping after local edits.

## Landing Page Maintenance

- Before changing frontend routes, layouts, cards, install modules, copy buttons, logo assets, or responsive behavior, read `DESIGN.md` and `MOTION.md`.
- The Next.js marketplace derives public skill pages from the `skills/` directory at build time.
- Do not hard-code current public skill names as the source of truth for site routing or catalog generation.
- Preserve independent pages for `/`, `/skills`, `/skills/<skill-name>`, `/install`, `/docs`, and `/motion`.
- Keep the install UI aligned with the Project, Global, and Try once command structure in `guidance.md` and `README.md`.
- Verify zero horizontal overflow at 360px, 390px, 430px, tablet, desktop, and wide desktop before finishing frontend work.
- Run `npm run validate:skills` and `npm run build` after landing page or skill catalog updates.

## Creating A New Skill

1. Choose a name using `NAMING.md`.
2. Create `skills/<skill-name>/SKILL.md`.
3. Create `skills/<skill-name>/agents/openai.yaml`.
4. Add only resources the skill actually needs.
5. Update `README.md` with the skill catalog row, project install, global install, try-once command, and example `$skill-name` prompt.
6. Run:

```bash
npm run validate:skills
```

7. Add tests or examples when the skill includes scripts or deterministic behavior.

## Updating Existing Skills

When changing a skill:

- Preserve its public install name unless the user explicitly approves a rename.
- Update `README.md` if the public catalog, install commands, or usage prompts change.
- Update `package.json` only when package metadata or CLI behavior changes.
- Reinstall the updated skill into Codex when the change is meant for immediate local use.
- Run validation before finishing.

## GitHub And NPM Sync Protocol

Use this protocol when the user explicitly asks to commit, push, sync GitHub, publish, release, update NPM, update NPX, or make a skill globally available.

This is a professional release workflow, not a memory-only habit. Future agents must use it whenever package sync is requested so GitHub, GitHub Releases, NPM, GitHub Packages, NPX install paths, and the local Codex copy stay aligned.

1. Keep the worktree scoped. Do not stage unrelated user files or untracked skill folders unless they are part of the request.
2. Run the relevant checks before publishing:

```bash
npm run validate:skills
npm test
npm run build
npm pack --dry-run
```

3. Run any relevant skill-specific audit or script, such as:

```bash
npm run audit:gh-ready
npm run audit:motioncraft
```

4. If the change is meant for immediate local Codex use, reinstall the changed skill and remind the user to restart Codex:

```bash
node bin/souvik-skills.cjs install <skill-name> --force
```

5. Create a signed Conventional Commit when signing is configured, then push to `main`. Example:

```bash
git commit -m "feat: upgrade <skill-name> ..."
git push origin main
```

6. After pushing, verify GitHub Actions for `CI`, `CodeQL`, and `Release Please`.
7. Release Please opens or updates a release PR. Inspect it before merging. It should only contain release metadata such as `package.json`, `package-lock.json`, `.release-please-manifest.json`, and `CHANGELOG.md`.
8. When the user has asked for NPM/NPX/package sync, merge the clean Release Please PR after checks pass. Resolve generated changelog conflicts carefully and keep one clean release entry.
9. Confirm the release automation publishes successfully to NPM and GitHub Packages. Verify with:

```bash
npm view @imsovikde/skills version
npx -y @imsovikde/skills@latest list
```

10. Smoke-test the published package when a skill changed:

```bash
npx -y @imsovikde/skills@latest install <skill-name> --dest <temp-dir> --force
```

11. If the package changed but Release Please does not open a release PR, check the commit type. Use a release-triggering Conventional Commit such as `feat:` or `fix:` when the package contents must reach NPM/NPX.
12. Finish only after reporting the GitHub commit, release PR or release URL, NPM version, package publish status, local Codex reinstall status, and any check that could not be run.

Do not commit NPM, GitHub, Vercel, Cloudflare, or other secrets. Use the existing GitHub Actions release automation; manual `npm publish` is only a fallback when the user explicitly asks and automation cannot complete.

## Release Readiness

A change is release-ready only when:

- Skill validation passes.
- Relevant tests pass.
- Install commands still work.
- Documentation reflects the current skill names.
- License and ownership information remain intact.
- Release Please and package publishing are verified when the user requested NPM/NPX sync.
