# Contributing

Thank you for improving Souvik Skills.

## Standards

- Read `guidance.md` and `NAMING.md` before adding or renaming a skill.
- Keep each skill self-contained under `skills/<skill-name>/`.
- Keep `SKILL.md` concise and procedural.
- Keep `agents/openai.yaml` aligned with the skill name and purpose.
- Do not add secrets, private traces, generated caches, local logs, or unrelated files.

## Validation

Run:

```bash
npm run validate:skills
npm test
npm run build
```

When changing the CLI, also run:

```bash
node bin/souvik-skills.cjs list
node bin/souvik-skills.cjs install all --dest ./tmp/codex-skills --force
```

When changing the frontend, read `DESIGN.md` and `MOTION.md`, then check desktop, tablet, and 360px/390px mobile widths for overflow, contrast, keyboard focus, and reduced-motion behavior.
