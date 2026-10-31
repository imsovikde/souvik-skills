# Lossless Transpilation Rules for Gemini Custom Skills

This document defines the formal compilation and transpilation rules used to transform multi-platform skills (Claude Code, OpenAI Codex, Cursor, Antigravity, Open Agent Skills) into Gemini-native custom skill packages without losing a single token of operational capability.

---

## 1. The Three Tiers of Progressive Disclosure

Gemini Custom Skills operate on a 3-tier progressive disclosure lifecycle:

1. **Discovery Tier (Catalog & Index)**:
   - Evaluated by Gemini at session start and during intent routing.
   - Parses **only** the YAML frontmatter (`name` and `description`).
   - Token budget: Minimal (~30 to 60 tokens).
   - Strict constraint: Unrecognized top-level YAML keys cause parse rejections in strict validation modes.

2. **Activation Tier (Instruction Body)**:
   - Injected into context only when the skill triggers (via semantic match or slash command `/name`).
   - Markdown body of `SKILL.md`.
   - Token budget: Hard ceiling of 500,000 characters; recommended best practice < 500 lines.

3. **Execution Tier (Bundled Resources)**:
   - Loaded on demand by Gemini when specific tasks require them.
   - Subdirectories: `scripts/` (executable Python and Bash), `references/` (documentation and templates), `assets/` (images and mock data).

---

## 2. Frontmatter Transpilation Protocol

Multi-agent platforms introduce custom frontmatter keys that are rejected by Gemini's YAML schema. The transpiler applies the following deterministic algorithm:

### Step 1: Key Partitioning
- **Standard Whitelist Keys**: `name`, `description`, `license`, `compatibility`, `metadata`, `allowed-tools`.
- **Proprietary Keys**: `disable-model-invocation`, `user-invocable`, `argument-hint`, `aliases`, `trigger`, `tools`, `model`, `version`, `author`, `tags`, `globs`, `alwaysApply`, `subagents`.

### Step 2: Frontmatter Normalization
- Format `name`: Convert to lowercase ASCII alphanumeric and single hyphens:
  $$\text{name} = \text{re.sub}(r'[^a-z0-9]+', '-', \text{raw\_name.lower()}).\text{strip}('-')[:64]$$
- Format `description`: Ensure single line, length between 40 and 1024 characters, third-person active verb, and explicit `Use when...` trigger statement.

### Step 3: Markdown Contract Migration
All proprietary keys are moved to the head of the Markdown body under a dedicated section:

```markdown
## Preserved Platform Metadata & Trigger Contract

> [!NOTE]
> The following platform metadata, triggers, and configuration were losslessly migrated
> from the original multi-agent frontmatter to maintain full platform compatibility:

- **disable-model-invocation**: `true`
- **tools**: `["search", "bash"]`
- **version**: `1.4.2`
```

---

## 3. Extension Remapping and Link Integrity

Because Gemini rejects file extensions like `.ts`, `.tsx`, `.sql`, `.graphql`, and extensionless files like `Makefile`, the transpiler applies a lossless suffix mapping:

### Transformation Table
| Original Filename | Transpiled Filename | Link Update Rule |
| :--- | :--- | :--- |
| `schema.sql` | `schema.sql.txt` | `[schema](schema.sql)` -> `[schema](schema.sql.txt)` |
| `types.ts` | `types.ts.txt` | `references/types.ts` -> `references/types.ts.txt` |
| `query.graphql` | `query.graphql.txt` | `query.graphql` -> `query.graphql.txt` |
| `Makefile` | `Makefile.txt` | `Makefile` -> `Makefile.txt` |
| `Dockerfile` | `Dockerfile.txt` | `Dockerfile` -> `Dockerfile.txt` |

Every text file in the package is scanned and all relative links and symbol paths are rewritten so no documentation reference is broken.

---

## 4. Offline Sandbox Adaptation Pattern

Gemini code execution sandboxes run Python (`.py`) and Bash (`.sh`) in an isolated, offline container without internet connectivity.

### The Offline Fallback Wrapper
When a bundled script contains network fetch calls (`requests`, `urllib`, `curl`), the transpiler injects the `GEMINI_OFFLINE_ADAPTER` preamble:

```python
# ====================================================================
# GEMINI_OFFLINE_ADAPTER: Environment Detection & Offline Fallback
# In gemini.google.com sandbox, direct internet access is disabled.
# When running offline, this script checks for local cached files
# or reads pre-fetched data from stdin/file arguments.
# ====================================================================
import os, sys
OFFLINE_MODE = os.environ.get('GEMINI_OFFLINE', '1') == '1'
```

In `SKILL.md`, instructions that tell the model to run `curl` or `wget` are adapted to instruct Gemini:
1. Use Gemini's built-in Google Search / Browsing tools to retrieve external documentation or data.
2. Pass the retrieved content into local Python scripts via stdin or temporary files.

---

## 5. Ultra-Safe File Consolidation Protocol

For general Gemini chat attachment modes where total file count is capped at 10:

1. Identify all documentation files in `references/` (`.md`, `.txt`).
2. Construct a single master manual: `references/consolidated-references.md`.
3. Include an auto-generated Table of Contents with Markdown anchor links.
4. Append each reference file with a clear section divider and original filename header.
5. Safely delete the split reference files once incorporated into the consolidated manual.
6. Append an explanatory note to `SKILL.md` pointing to the consolidated manual.
