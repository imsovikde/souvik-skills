# Audit and Losslessness Evaluation Rubric

This rubric defines the falsifiable verification criteria used to evaluate whether a packaged Gemini Custom Skill satisfies zero-rejection standards and achieves 100% losslessness.

---

## 1. Zero-Rejection Verification Checklist

Every packaged skill must pass 100% of these assertions before being declared upload-ready:

| ID | Criterion | Assertion / Verification Command | Pass Condition |
| :--- | :--- | :--- | :--- |
| **ZR-01** | Exact `SKILL.md` Presence | `zipfile.ZipFile(zip_path).namelist()` contains `SKILL.md` or `<name>/SKILL.md` | Returns True |
| **ZR-02** | Case Sensitivity | Archive contains zero occurrences of `skill.md` or `Skill.md` | Returns True |
| **ZR-03** | Archive File Count | Standard Mode: `<= 95` files (hard max 100). Ultra-Safe Mode: `<= 10` files | Returns True |
| **ZR-04** | Archive Size | Compressed `.zip` size `<= 100 MB`, uncompressed size `<= 100 MB` | Returns True |
| **ZR-05** | Directory Depth | Maximum directory depth `<= 10` levels relative to skill root | Returns True |
| **ZR-06** | Whitelist Enforcement | 100% of files have extensions matching Gemini whitelist | Returns True |
| **ZR-07** | Banned Files Purged | Zero occurrences of `.git`, `.DS_Store`, `__MACOSX`, `.vscode`, `node_modules` | Returns True |
| **ZR-08** | Zero-Width Unicode | Zero occurrences of `\u200b`, `\u200c`, `\u200d`, `\ufeff`, `\u202e` | Returns True |
| **ZR-09** | Secret Redaction | Zero unredacted tokens matching `sk-...`, `ghp_...`, `AKIA...`, `AIza...` | Returns True |
| **ZR-10** | Archive Integrity | `zipfile.ZipFile(zip_path).testzip()` | Returns None (zero errors) |
| **ZR-11** | Strict Lossless Media | Zero dropped source images/assets; all media retained or mapped | Returns True |
| **ZR-12** | Offline Sandbox Gate | Zero unhandled external network calls in executable scripts | Returns True |

---

## 2. Losslessness Assessment Dimensions

Losslessness is defined across four distinct dimensions:

### A. Semantic Instruction Equivalence
- **Requirement**: No procedural step, heuristic, or constraint present in the original `SKILL.md` may be omitted or altered in semantic meaning during transpilation.
- **Verification**: Diffing the instruction sections of original vs transpiled `SKILL.md` must yield zero deleted substantive paragraphs.

### B. Platform Metadata Preservation
- **Requirement**: Every non-standard YAML frontmatter key (such as `disable-model-invocation`, `version`, `tools`, `author`, `tags`) must be preserved verbatim in `## Preserved Platform Metadata & Trigger Contract`.
- **Verification**: Keys present in original YAML frontmatter that are absent in transpiled YAML must appear in the markdown body table or list.

### C. Reference Link Reachability
- **Requirement**: Any file renamed to satisfy Gemini's extension whitelist (e.g., `types.ts` -> `types.ts.txt`) must have all internal markdown and code references updated simultaneously.
- **Verification**: No dead markdown relative links. Scanning all markdown files for `[text](path)` must verify that `path` exists on disk.

### D. Executable Script Fallback Integrity
- **Requirement**: Scripts requiring external data must provide local file/stdin fallbacks so execution does not terminate with an unhandled network error in Gemini's offline container.
- **Verification**: Bundled Python scripts run successfully with mock stdin or arguments without raising `socket.error` or `urllib.error.URLError`.

---

## 3. Scoring and Certification Matrix

| Tier | Score Range | Status | Deployment Action |
| :--- | :--- | :--- | :--- |
| **Gold (Certified)** | 100% | Zero-Rejection Ready | Approved for automated packaging and immediate upload to `gemini.google.com`. |
| **Silver (Conditional)** | 90% to 99% | Warnings Present | Non-blocking warnings (e.g. file count between 90 and 95). Upload permitted. |
| **Red (Rejected)** | < 90% | Critical Defect | Packaging halted. Automatic transpiler rollback and error reporting triggered. |
