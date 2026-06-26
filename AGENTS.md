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

## Release Readiness

A change is release-ready only when:

- Skill validation passes.
- Relevant tests pass.
- Install commands still work.
- Documentation reflects the current skill names.
- License and ownership information remain intact.
