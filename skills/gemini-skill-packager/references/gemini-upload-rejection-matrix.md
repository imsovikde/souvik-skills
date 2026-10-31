# Gemini Custom Skill Upload Rejection Matrix

This document provides a comprehensive diagnostic catalog of every known upload failure, validation gate, sandbox constraint, and rejection reason encountered when uploading custom skills to `gemini.google.com` (both the Gemini Apps web upload modal and the Gemini Enterprise skills endpoint).

---

## 1. Archive Structure & Path Topology Rejections

| Gate ID | Failure Condition | Root Cause | Mechanistic Remedy |
| :--- | :--- | :--- | :--- |
| **ARCH-01** | Missing `SKILL.md` at root | Archive contains subfolders or monorepo roots without an immediate `SKILL.md`. | Flatten or extract so that `SKILL.md` sits either at the archive root or directly under a single `<skill-name>/` top-level directory. |
| **ARCH-02** | Case sensitivity mismatch | File named `skill.md` or `Skill.md` instead of exact uppercase `SKILL.md`. | Rename to `SKILL.md` with exact casing. |
| **ARCH-03** | Multiple `SKILL.md` collision | Monorepo or multi-skill archive contains more than one `SKILL.md` in subdirectories. | Ingest the target skill in isolation; ensure the `.zip` archive contains exactly one `SKILL.md`. |
| **ARCH-04** | File count exceeds ceiling | Package contains > 100 files (or > 10 files in standard chat upload modal). | Run lossless consolidation: merge markdown reference files into an indexed master reference manual. |
| **ARCH-05** | Directory nesting > 10 levels | Subfolder hierarchy exceeds 10 levels relative to skill root. | Flatten nested directory structures to depth <= 3 (`scripts/`, `references/`, `assets/`). |
| **ARCH-06** | Parent directory traversal (`..`) | Zip archive contains relative traversal paths (`../etc/file`). | Sanitize archive paths during compression to strictly local relative paths. |
| **ARCH-07** | Symlinks or broken aliases | Zip contains symbolic links or POSIX symlink entries. | Dereference or copy physical files into the staging area before zip archiving. |
| **ARCH-08** | OS / VCS metadata clutter | Presence of `.git`, `.github`, `.DS_Store`, `__MACOSX`, `.vscode`, `.idea`, `node_modules`. | Strictly purge all dotfiles and build caches prior to packaging. |

---

## 2. YAML Frontmatter & Parser Rejections

| Gate ID | Failure Condition | Root Cause | Mechanistic Remedy |
| :--- | :--- | :--- | :--- |
| **YAML-01** | Non-standard frontmatter keys | Platform keys (`disable-model-invocation`, `user-invocable`, `tools`, `model`, `version`, `tags`). | Strip non-standard keys from YAML frontmatter and migrate them losslessly into a `Preserved Platform Metadata & Trigger Contract` markdown section. |
| **YAML-02** | Invalid skill name format | Name contains uppercase letters, spaces, underscores, or consecutive hyphens. | Normalize to kebab-case regex: `^[a-z0-9]+(-[a-z0-9]+)*$` (max 64 characters). |
| **YAML-03** | Missing trigger directives | Description lacks guidance on when to invoke the skill. | Ensure description includes explicit capability and `Use when...` trigger phrasing. |
| **YAML-04** | Description length violation | Description is < 40 characters or > 1024 characters. | Expand brief descriptions to at least 40 chars; truncate or consolidate descriptions over 1024 chars. |
| **YAML-05** | Raw angle brackets / broken YAML | Unescaped `<` or `>` or unquoted colons break YAML block parser. | Wrap strings containing colons in double quotes; replace unescaped angle brackets. |

---

## 3. File Extension Whitelist & Blacklist

### Officially Supported File Types (Whitelisted)
- **Documents & Text**: `.md`, `.txt`, `.pdf`, `.docx`, `.rtf`, `.tex`, `.log`, `.rst`, `.odt`
- **Tables & Data**: `.csv`, `.ods`, `.xlsx`
- **Presentations**: `.odp`, `.pptx`
- **Images**: `.jpg`, `.jpeg`, `.png`, `.svg`, `.gif`, `.heic`, `.ico`, `.webp`
- **Code & Scripts**: `.py`, `.sh`, `.ipynb`, `.js` (Note: Gemini sandbox runs `.py` and `.sh` only)
- **Web**: `.css`, `.html`, `.htm`
- **Config**: `.json`, `.toml`, `.xml`, `.yaml`, `.yml`

### Rejected Extensions & Lossless Conversion Strategy
- **Unsupported Code**: `.ts`, `.tsx`, `.jsx`, `.mjs`, `.cjs`, `.sql`, `.graphql`, `.proto`, `.cs`, `.kt`, `.php`, `.rb`, `.swift`, `.go`, `.rs`, `.java`, `.c`, `.cpp`, `.h`, `.hpp`, `.pl`, `.lua`, `.ps1`, `.bat`, `.cmd`
  - *Conversion*: Append `.txt` suffix (e.g. `schema.sql` -> `schema.sql.txt`, `types.ts` -> `types.ts.txt`). Rewrite relative markdown links to match.
- **Extensionless Files**: `Makefile`, `Dockerfile`, `LICENSE`
  - *Conversion*: Append `.txt` (e.g. `Dockerfile.txt`, `Makefile.txt`).
- **Forbidden Binaries & Media**: `.zip`, `.tar.gz`, `.exe`, `.dll`, `.so`, `.wasm`, `.mp3`, `.mp4`, `.wav`
  - *Conversion*: Omit pre-compiled binaries; embed generation recipes or ASCII representations in `.txt` or `.md`.

---

## 4. Sandbox Execution & Content Policy Gates

| Gate ID | Failure Condition | Root Cause | Mechanistic Remedy |
| :--- | :--- | :--- | :--- |
| **EXEC-01** | Offline Sandbox Socket Error | Script attempts outbound HTTP/HTTPS network calls (`requests.get`, `urllib`, `curl`, `pip install`). | Inject `GEMINI_OFFLINE_ADAPTER` fallback; instruct Gemini in `SKILL.md` to use native Google Search tools and pipe inputs locally. |
| **EXEC-02** | Pipe to Shell Pattern | Script or doc contains `curl ... \| sh` or `wget ... \| bash`. | Neutralize shell pipe patterns into offline python scripts or documented local inspection steps. |
| **NET-02** | External Web Service Endpoints | Scripts contain hardcoded external API targets (`api.together.xyz`) violating Google's "No external actions" rule. | Neutralize endpoint URLs with offline mock stubs and instructions to rely on local context or user-provided artifacts. |
| **MEDIA-01** | Unsupported Media Types | Archive contains unsupported media formats (.raw, video, audio) exceeding Google's supported list or exceeding 100 MB total archive limit. | Restrict media to supported types (.jpg, .png, .svg, .gif, .webp) within the 100 MB ceiling; retain all valid reference images losslessly. |
| **CLUTTER-01** | Foreign Platform Agent Manifests | Proprietary platform manifests (`agents/openai.yaml`, `.codex-plugin`) cause schema ingestion failure. | Purge proprietary agent manifests during Stage 1 ingestion; migrate triggers into `SKILL.md`. |
| **SEC-01** | Hardcoded Secret Exposure | Tokens matching `sk-...`, `ghp_...`, `npm_...`, `AKIA...`, `AIza...`. | Sanitize tokens to `<REDACTED_API_KEY>` placeholders. |
| **SEC-02** | Zero-Width Unicode Injection | Hidden characters (`U+200B`, `U+200C`, `U+200D`, `U+FEFF`, `U+202E`). | Strip zero-width and RTL override characters across all text files. |
| **SEC-03** | Adversarial Prompt Heuristics | Phrases like `Ignore previous instructions` or `Bypass safety`. | Reframe adversarial red-team text into authorized defensive audit checks. |
