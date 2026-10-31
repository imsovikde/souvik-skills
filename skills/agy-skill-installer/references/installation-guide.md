# Anti-Gravity IDE Skill & Plugin Installation Reference

This document outlines the standard mechanisms for discovering, registering, and activating agent skills and native plugins in Google Anti-Gravity IDE.

## 1. Customization Roots & Priority

Anti-Gravity IDE discovers agent skills across four primary root levels:

1. **Global Skills Root (Machine-Wide):**
   - Path: `~/.gemini/config/skills/<skill-name>/` (`C:\Users\<user>\.gemini\config\skills\<skill-name>\` on Windows)
   - Available across all projects and conversations on the machine.

2. **Workspace Skills Root (Project-Specific):**
   - Path: `<workspace-root>/.agents/skills/<skill-name>/`
   - Scoped to the specific codebase and committed to version control for team collaboration.

3. **Antigravity Skills Root:**
   - Path: `~/.gemini/antigravity/skills/<skill-name>/`

4. **User Agent Skills Root:**
   - Path: `~/.agents/skills/<skill-name>/`

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

## 3. Native Antigravity Plugins (The Ponytail Standard)

Plugins are namespaced, shareable bundles packaging skills, rules, hooks, and MCP configs into an authoritative unit.

### Plugin Directory Structure:
```text
plugins/<plugin_name>/
├── plugin.json       # Required: Manifest file declaring "name"
├── AGENTS.md         # Optional: Rules applied when plugin is active
├── mcp_config.json   # Optional: MCP servers exposed by the plugin
├── hooks.json        # Optional: Lifecycle hooks run by the plugin
└── skills/           # Bundled skills exposed by the plugin
    └── <skill_name>/
        └── SKILL.md
```

### Global & Local Plugin Roots:
- Global: `~/.gemini/config/plugins/<plugin_name>/`
- Local: `<workspace-root>/.agents/plugins/<plugin_name>/`

## 4. Turning Plugins On and Off in Antigravity Settings UI

Antigravity IDE tracks the active state of plugins in `~/.gemini/config/config.json` under the `plugins` map:

```json
{
  "plugins": {
    "my-plugin": { "enabled": true }
  }
}
```

- When `"enabled": true`, Antigravity IDE loads the plugin's `AGENTS.md` rules, MCP servers, hooks, and skills.
- Users can toggle any installed plugin on or off directly from the Antigravity IDE Customization Settings panel (`Settings > Customizations > Plugins`), exactly as demonstrated by the Ponytail plugin.
- In addition, all bundled skills are provisioned into the 4 skills roots so their slash commands (`/<skill-name>`) are registered globally in the chat interface.

## 5. Slash Command Generation

Anti-Gravity IDE automatically registers a slash command for every discovered skill:
- Skill directory name `my-skill` → Slash command `/my-skill`
- To invoke the skill in conversation, the user types: `/<skill-name>`

## 6. Zero Truncation Rule

When installing skills and plugins from third-party repositories:
- Never omit scripts (`scripts/*`), templates (`assets/*`), or references (`references/*`).
- Always copy subdirectories recursively with 100% fidelity.
- Remove `.git` metadata from the copied skill or plugin folder to prevent VCS nesting issues.
