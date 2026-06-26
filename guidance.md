# Souvik Skills Guidance

This repository is the public skill directory for Souvik Dey, GitHub owner `imsovikde`.

Souvik Skills contains reusable AI-agent skills for developers. Each skill must be installable, readable, maintainable, and suitable for public use. The repository is MIT licensed unless a specific skill adds additional required notices.

Do not create `context.md`. This file is the durable repository guide.

## Repository Identity

- Brand: Souvik Skills
- Owner: Souvik Dey
- GitHub: `https://github.com/imsovikde`
- Repository: `imsovikde/souvik-skills`
- NPM package: `@imsovikde/skills`
- License: MIT

## Directory Shape

```text
souvik-skills/
|-- skills/
|   |-- <skill-name>/
|   |   |-- SKILL.md
|   |   `-- agents/
|   |       `-- openai.yaml
|-- bin/
|   `-- souvik-skills.cjs
|-- scripts/
|   `-- validate-skills.cjs
|-- AGENTS.md
|-- NAMING.md
|-- guidance.md
|-- README.md
|-- LICENSE
`-- package.json
```

## Skill Standard

Every skill folder must contain:

- `SKILL.md`
- `agents/openai.yaml`

`SKILL.md` must:

- Use YAML frontmatter with only `name` and `description`.
- Match `name` exactly to the folder name.
- Describe what the skill does and when an agent should use it.
- Keep the body focused on workflow instructions, not marketing copy.
- Reference bundled files only when they are useful for progressive disclosure.

`agents/openai.yaml` must:

- Include `interface.display_name`.
- Include `interface.short_description`.
- Include `interface.default_prompt`.
- Mention the skill as `$skill-name` in the default prompt.

## Resource Rules

Use bundled resources only when they make the skill more reliable:

- `scripts/` for deterministic operations and repeated automation.
- `references/` for deeper guidance that should load only when needed.
- `assets/` for templates, icons, fonts, or other output resources.

Do not add extra documentation inside a skill folder unless it is directly used by the skill. Root-level documentation belongs in the repository root.

## Cross-Agent NPX Install Standard

The public cross-agent install path is the `skills` CLI:

```bash
npx -y skills add imsovikde/souvik-skills --skill <skill-name> --agent <agent>
npx -y skills add imsovikde/souvik-skills --skill <skill-name> --agent <agent> -g
npx -y skills use imsovikde/souvik-skills@<skill-name> | <agent-cli>
```

Each public skill in `README.md` must show these three modes:

- Project only: installs into the current project for the selected agent.
- Global: installs user-wide for the selected agent with `-g`.
- Try once: streams the skill prompt into an agent CLI without installing it.

Use the supported agent slug requested by the user, such as `codex`, `claude-code`, `cursor`, `gemini-cli`, or another compatible agent name. Use `<agent>` and `<agent-cli>` placeholders in reusable documentation.

## NPM Package Install Standard

The package installer path for Codex remains:

```bash
npx @imsovikde/skills install <skill-name>
```

The installer must:

- List available skills.
- Install one skill by name.
- Install all skills.
- Copy skills into `CODEX_HOME/skills` when `CODEX_HOME` is set.
- Fall back to `~/.codex/skills`.
- Avoid overwriting existing installed skills unless `--force` is passed.

## GitHub Readiness

Before release, verify:

- `README.md` explains the repository, skills, install commands, and development commands.
- `LICENSE` names Souvik Dey as copyright holder.
- `package.json` has the correct package name, bin, repository, keywords, license, and publish config.
- CI runs skill validation and tests.
- No caches, local logs, generated reports, or private traces are committed.
- Every skill passes `npm run validate:skills`.
- Relevant tests pass when a skill includes scripts or deterministic behavior.

## Standalone Skill Repositories

Each folder under `skills/` is also a standalone publish target. To publish a separate repository for one skill, copy the skill folder into a repository named after that skill and preserve:

- `SKILL.md`
- `agents/openai.yaml`
- Required resources
- MIT license notice

The root `souvik-skills` repository remains the canonical directory and installer.
