---
name: agy-skill-installer
description: Install any agent skill into Anti-Gravity IDE with 100% fidelity, automated YAML frontmatter validation, dual-root provisioning, security scanning, and slash command integration.
---

# Anti-Gravity Skill Installer

Install any skill or multi-skill collection into Anti-Gravity IDE 2.0 with **100% fidelity**. Zero truncation, zero omitted subfolders, zero broken dependencies.

## Overview

Anti-Gravity IDE requires skills to be structured with valid YAML frontmatter, dual-root placement (`~/.gemini/config/skills` and `.agents/skills`), and sanitized telemetry/tracking to ensure slash commands (`/agy-skill-installer`) index properly in the editor UI.

## Operating Protocol

1. **Source Parsing**: Accept GitHub URL (`https://github.com/user/repo`), skill monorepo, or local path.
2. **Clone & Extract**: Clone complete repository into a temporary directory. Never scrape partial snippets.
3. **YAML Frontmatter Normalization & Repair**:
   - Parse `SKILL.md` frontmatter.
   - Fix unquoted colons and formatting issues that crash the Anti-Gravity YAML parser.
   - Ensure `name:` matches the directory name exactly.
4. **Security & Privacy Scanning**:
   - Scan files for hardcoded API secrets, tracking beacons, and telemetry calls.
   - Strip tracking while preserving functional API calls.
5. **Dual-Root Provisioning**:
   - Copy 100% of files (scripts, templates, references, agents) to:
     - Global: `~/.gemini/config/skills/<name>/`
     - Workspace: `.agents/skills/<name>/`
     - Antigravity: `~/.gemini/antigravity/skills/<name>/`
   - Remove nested `.git` directories.
6. **Slash Command Verification**:
   - Test YAML frontmatter parsing with safe YAML loader.
   - Confirm active slash command trigger: `/<name>`.

## Reusable Automation Scripts

- **Windows (PowerShell):**
  ```powershell
  powershell -ExecutionPolicy Bypass -File "skills/agy-skill-installer/scripts/install-skill.ps1" -SourceUrlOrPath "<REPO_URL>"
  ```

- **Linux / macOS (Bash):**
  ```bash
  bash skills/agy-skill-installer/scripts/install-skill.sh "<REPO_URL>"
  ```
