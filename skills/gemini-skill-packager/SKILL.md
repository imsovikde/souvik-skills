---
name: gemini-skill-packager
description: Transpile, sanitize, validate, and package any agent skill into a zero-rejection lossless ZIP bundle for gemini.google.com. Use when preparing skills for Gemini Apps upload, fixing upload rejections, converting Claude or Codex skills to Gemini, or packaging custom skills.
---
# Gemini Skill Packager

Transpile, validate, and package agent skills from any source (local folders, GitHub repositories, Claude Code plugins, Codex skills, or monorepos) into zero-rejection, sandbox-compliant `.zip` archives designed for immediate upload to `gemini.google.com`.

Read the companion reference documents before making architectural changes:
- `references/gemini-upload-rejection-matrix.md`: Catalog of all 45+ upload rejection triggers and root causes.
- `references/lossless-transpilation-rules.md`: Deterministic transpilation algorithms and frontmatter migration protocols.
- `references/audit-and-losslessness-rubric.md`: Verification rubric and falsifiable assertions.

## 1. Core Workflow Pipeline

The packager runs a four-stage compiler pipeline:

```text
[Source Directory / Archive / Monorepo]
                  |
                  v
       Stage 1: Ingestion & Normalization (`scripts/ingest_skill_source.py`)
                  |
                  v
       Stage 2: Lossless Transpilation (`scripts/lossless_gemini_transpiler.py`)
                  |
                  v
       Stage 3: Deep Audit & Verification (`scripts/validate_and_package_zip.py`)
                  |
                  v
      [Zero-Rejection <skill-name>.zip Bundle]
```

### Stage 1: Ingest & Purge Clutter
Extract source archives or directories, detect the target `SKILL.md`, isolate the skill boundary, and purge all OS and VCS clutter (`.git`, `.github`, `.DS_Store`, `__MACOSX`, `node_modules`, `.vscode`):

```bash
python skills/gemini-skill-packager/scripts/ingest_skill_source.py <source-path-or-archive> -o <staging-directory> [--skill-name <name>]
```

### Stage 2: Lossless Transpilation
Apply deterministic transpilation:
- Clean YAML frontmatter: keep only `name` and `description` (plus optional standard keys).
- Losslessly migrate all proprietary platform keys (`disable-model-invocation`, `tools`, `version`, `tags`) into `## Preserved Platform Metadata & Trigger Contract` at the head of `SKILL.md`.
- Safely remap unsupported extensions (`.ts`, `.sql`, `.graphql`, `Makefile`, etc.) by appending `.txt`, and update all relative references across markdown documents.
- Inject `GEMINI_OFFLINE_ADAPTER` into Python scripts to ensure graceful offline execution.
- Strip zero-width Unicode characters and redact sample API keys.

```bash
python skills/gemini-skill-packager/scripts/lossless_gemini_transpiler.py <staging-directory> [--ultra-safe]
```

Use `--ultra-safe` when packaging for chat attachment limits (consolidates reference markdown files into an indexed master manual to guarantee `<= 10` total files).

### Stage 3: Audit & Deterministic ZIP Packaging
Audit the staged skill against all Gemini constraints (exact `SKILL.md` casing, file count ceilings, size budgets, path depth, whitelist compliance) and build a reproducible `.zip` archive:

```bash
python skills/gemini-skill-packager/scripts/validate_and_package_zip.py <staging-directory> -o <output-path.zip> [--wrap-folder]
```

## 2. Modes of Operation

- **Full Compilation (Default)**: Ingest, transpile, verify, and package into `<skill-name>.zip`.
- **Pre-Upload Audit Only**: Audit an existing prepared folder without creating an archive:
  ```bash
  python skills/gemini-skill-packager/scripts/validate_and_package_zip.py <prepared-skill-dir>
  ```
- **Ultra-Safe Consolidated Mode**: Guarantees total package file count `<= 10` files for chat environments where multi-file archives are capped at 10 attachments.

## 3. How to Upload to Gemini Apps

1. Navigate to `https://gemini.google.com` in your web browser.
2. Open the sidebar navigation menu and click **Customize** -> **Skills**.
3. Click the **Upload** button.
4. Select the generated `<skill-name>.zip` file (or the transpiled skill folder).
5. Review the imported skill title, description, and instructions.
6. Click **Create** to save. Gemini can now trigger the skill automatically via semantic matching or directly via `/<skill-name>`.

## 4. Quality & Compliance Verification

Run the automated test suite to ensure the packager and its generated packages conform to all standards:

```bash
python skills/gemini-skill-packager/scripts/test_gemini_skill_packager.py
```
