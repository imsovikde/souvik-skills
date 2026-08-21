# Anti-Gravity IDE Skill Installation Reference

This document outlines the standard mechanisms for discovering, registering, and activating skills in Google Anti-Gravity IDE 2.0.

## 1. Customization Roots & Priority

Anti-Gravity IDE discovers agent skills across two primary root levels:

1. **Global Skills Root (Machine-Wide):**
   - Path: `~/.gemini/config/skills/<skill-name>/` (`C:\Users\<user>\.gemini\config\skills\<skill-name>\` on Windows)
   - Available across all projects and conversations on the machine.

2. **Workspace Skills Root (Project-Specific):**
   - Path: `<workspace-root>/.agents/skills/<skill-name>/`
   - Scoped to the specific codebase and committed to version control for team collaboration.

### Loading Precedence:
- Local Workspace Skills (`.agents/skills/`) override Global Skills (`~/.gemini/config/skills/`) if identical skill names exist.

## 2. Skill Folder Requirements

Every installed skill MUST follow this folder structure:

```text
skills/<skill-name>/
├── SKILL.md                  # Required: Instructions + YAML frontmatter
├── references/               # Optional: Deep reference guides and docs
├── scripts/                  # Optional: Helper utilities and automated scripts
└── assets/                   # Optional: Templates, images, boilerplates
```

### Required `SKILL.md` Frontmatter:
```yaml
---
name: skill-name
description: Use when [specific triggering conditions, symptoms, and contexts]
---
```

## 3. Slash Command Generation

Anti-Gravity IDE automatically registers a slash command for every discovered skill:
- Skill directory name `my-skill` → Slash command `/my-skill`
- To invoke the skill in conversation, the user types: `/<skill-name>`

## 4. Zero Truncation Rule

When installing skills from third-party repositories:
- Never omit scripts (`scripts/*`), templates (`assets/*`), or references (`references/*`).
- Always copy subdirectories recursively.
- Remove `.git` metadata from the copied skill folder to prevent VCS nesting issues.
