---
name: agy-skill-installer
description: Install any agent skill into Anti-Gravity IDE with 100% fidelity, automated YAML frontmatter validation, dual-root provisioning, security scanning, and slash command integration.
---

# Anti-Gravity Skill & Plugin Installer

Install any skill, multi-skill collection, or native plugin into Anti-Gravity IDE with **100% fidelity**. Zero truncation, zero omitted subfolders, zero broken dependencies.

## Overview

Anti-Gravity IDE supports two primary customization constructs:
1. **Agent Skills**: Procedural runbooks and commands discovered across the 4 discovery roots (`~/.gemini/config/skills/`, `.agents/skills/`, `~/.gemini/antigravity/skills/`, and `~/.agents/skills/`).
2. **Native Antigravity Plugins (The Ponytail Standard)**: Namespaced bundles (`~/.gemini/config/plugins/<name>/` and `.agents/plugins/<name>/`) packaging skills, `AGENTS.md` rules, hooks, and MCP servers into an authoritative unit that is registered in `~/.gemini/config/config.json` with direct toggle control (`"enabled": true / false`) inside the Antigravity Customization Settings UI.

## Operating Protocol

### A. Native Antigravity Plugin Installation (Ponytail Standard)
1. **Detection**: Automatically identifies plugin repositories by inspecting `plugin.json`, `gemini-extension.json`, or `.antigravity-plugin/plugin.json`, or via explicit `-AsPlugin` flag.
2. **Authoritative Deployment**:
   - Deploys full plugin package to Global (`~/.gemini/config/plugins/<name>/`) and Local (`.agents/plugins/<name>/`).
   - Ensures valid `plugin.json` declaring plugin identity at the root.
   - Ensures `AGENTS.md` is preserved at the plugin root for runtime rules discovery.
3. **Customization Settings Control Registration**:
   - Atomically registers `plugins.<name> = { "enabled": true }` into `~/.gemini/config/config.json`.
   - Exposes native toggle switches in Antigravity IDE -> Settings -> Customizations -> Plugins, allowing users to enable or disable the entire plugin and all its capabilities instantly.
4. **Bundled Skill Encapsulation (Zero Duplicate & Token Optimization)**:
   - Preserves bundled skills exclusively within `plugins/<name>/skills/`. Antigravity's plugin engine automatically discovers and mounts them with the plugin badge without duplicating them into standalone skills roots, eliminating context token waste and ensuring clean lifecycle control when toggled on/off in Settings.

### B. Standalone Skill Installation
1. **Source Parsing**: Clones Git repository or resolves local directory.
2. **YAML Normalization**: Fixes unquoted colons, invalid block scalars, and ensures `name:` matches the directory name exactly.
3. **Security & Privacy Scanning**: Scans for leaked keys and tracking beacons.
4. **Multi-Root Provisioning**: Copies files with 100% fidelity to:
   - Global: `~/.gemini/config/skills/<name>/`
   - Local: `.agents/skills/<name>/`
   - Antigravity Root: `~/.gemini/antigravity/skills/<name>/`
   - User Agent Root: `~/.agents/skills/<name>/`
5. **Slash Command Registration**: Automatically registers `/<name>` in the chat interface.

## Reusable Automation Scripts

- **Windows (PowerShell) - Standalone Skill:**
  ```powershell
  powershell -ExecutionPolicy Bypass -File "skills/agy-skill-installer/scripts/install-skill.ps1" -SourceUrlOrPath "<REPO_URL>"
  ```

- **Windows (PowerShell) - Native Antigravity Plugin (Ponytail Standard):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File "skills/agy-skill-installer/scripts/install-skill.ps1" -SourceUrlOrPath "<REPO_URL>" -AsPlugin
  ```

- **Linux / macOS (Bash):**
  ```bash
  bash skills/agy-skill-installer/scripts/install-skill.sh "<REPO_URL>" [--plugin]
  ```
