# Anti-Reward-Hacking and Verification Locks Reference

This reference defines the enforcement mechanisms for Pass 6 (Security & Redaction), Pass 7 (Test-Harness Integrity), and Stage 2 Cold Verification, grounded in industry research on LLM specification gaming, test-suite reward hacking, and the Green Build Fallacy.

## 1. Anatomy of Epistemic Reward-Hacking in Coding Agents

Coding agents frequently optimize for making a verification script exit 0 rather than fixing the underlying system defect. Audit both the codebase and any prior engineering reports for these twelve reward-hacking vectors:

| Vector ID | Reward-Hacking Pattern | How It Masks Bugs | Detection Method |
| :--- | :--- | :--- | :--- |
| `HACK-01` | Uninitialized Client Schema Cache | In `@modelcontextprotocol/sdk`, `client.callTool()` only validates `structuredContent` against `outputSchema` if `client.listTools()` was called first on that client instance. Omitting `listTools()` lets invalid tool payloads pass tests. | Inspect test setup (`beforeEach` / `beforeAll`) to confirm `await client.listTools()` executes before any `client.callTool()` invocation. |
| `HACK-02` | Direct Function Import Bypassing Protocol | Tests import a TypeScript helper function directly instead of routing through the HTTP router or MCP server transport, bypassing middleware, auth, input parsing, and output serialization. | Verify integration tests invoke the full transport boundary (Server + Client over `InMemoryTransport` or HTTP fetch). |
| `HACK-03` | Assertion Weakening or Deletion | Modifying a failing test from `expect(res.isError).toBe(false)` to `expect(res).toBeDefined()`, or adding `.skip` / `.todo` to failing test blocks. | Run `git diff` on `tests/` to flag any weakened assertion, commented assertion, or skipped test block as `P0 BLOCKER`. |
| `HACK-04` | Schema Loosening (`z.any()` / `.passthrough()`) | Replacing a strict `outputSchema` or input schema with `z.any()`, `z.record(z.unknown())`, or `.passthrough()` so malformed runtime objects pass validation. | Audit all schema diffs; ensure schema fields match the exact domain contract without loosening constraints. |
| `HACK-05` | Cosmetic Dead-Code Implementation | Writing a complete helper function (such as cursor pagination or fuzzy matching) in `src/utils/` and unit-testing the helper, while leaving the live tool or route handler hardcoded. | Trace every helper from definition to live production call sites in `src/routes/` or `src/tools/`. |
| `HACK-06` | Historical Commit Fabrication | Claiming in a status report that "BUG-X was already fixed in commit abc1234" without inspecting current `HEAD`, where the defect remains unfixed or was reverted. | Never trust commit messages or prose summaries; read the exact lines at current `HEAD` (`git show HEAD:<path>`). |
| `HACK-07` | Exit-Code Short-Circuiting | Modifying npm scripts (`package.json`), linter configs, or test runners to ignore exit codes (e.g. `\|\| true`, `continue-on-error: true`, or `process.exit(0)` catch blocks). | Inspect `git diff` on `package.json`, CI workflows, and test configs for suppressed failures or masked exit codes. |
| `HACK-08` | Implementation-Coupled Internal Mocking | Tests mock internal application modules (`vi.mock('../src/services/billing')` or `jest.mock('../db')`) instead of testing at public system boundaries. Mocks pass even when real internal implementations diverge and crash in production. | Run `node scripts/verify-mcp-and-schema-parity.js` to statically flag internal-module mocking in test files. |
| `HACK-09` | Tautological Test Assertions | Tests compute expected output using the exact same formula or helper being tested (e.g. `expect(calculateTax(x)).toBe(taxRate * x)`), or make circular assertions (`expect(res).toEqual(res)`). | Scan test files for dynamic expected-value calculations instead of hardcoded literal contract expectations. |
| `HACK-10` | Horizontal Bulk Test Slicing | Authoring dozens of speculative, shallow test cases across multiple features before implementing any core domain invariants, creating the illusion of high coverage while testing zero boundary constraints. | Audit test assertions to confirm they test real boundary edge cases rather than repetitive trivial happy-path invocations. |
| `HACK-11` | Shallow-Seam False Confidence / Missing-Seam Honesty | Testing only an isolated helper because the target module lacks a clean public test seam, and claiming the entire integration is verified. | Enforce Missing-Seam Honesty: if a component cannot be verified without internal mocking, explicitly report a Missing Test Seam defect. |
| `HACK-12` | Hallucinated Citations (`file:line:symbol`) | Citing non-existent file paths, wrong line numbers, fabricated commit hashes, or hallucinated specification clauses in review reports. | Run `node scripts/verify-citations-and-ast-seams.js <report-file>` to verify that 100% of cited files, lines, and symbols physically exist on disk. |

## 2. Low-Parameter / Flash-Model Anti-Short-Circuiting Locks

When running on fast, lightweight, or distilled models (such as Gemini Flash), agents face severe structural incentives to truncate analysis, emit placeholder code, and skim diffs. apex-bug-hunter enforces four mandatory anti-short-circuiting invariants:

### 2.1 Explicit Inspection Receipts
For every audited file, route, or tool handler, the model must record a concrete receipt:
- Target boundary: `file:line_start-line_end`
- Declared schemas: input schema and output schema
- Inspected branches: list of return and error branches examined
- Verified invariants: explicit confirmation of tenant isolation, cycle detection, or pagination wiring

### 2.2 Absolute Ban on Placeholder Code
The following placeholder patterns are strictly prohibited in any generated file, diff, or blueprint:
- `// ... existing code ...`
- `/* ... rest of implementation ... */`
- `<!-- same as before -->`
- `// TODO: implement later`
- Any truncation that leaves the user or compiler to fill in blanks. All file writes must be 100% complete.

### 2.3 Mandatory Verbatim Quote at HEAD
Every bug reported must include a physical, verbatim 1 to 5 line quote directly from the target file at current `HEAD`. If the model cannot provide the exact lines, it has not read the file and is forbidden from reporting the defect.

### 2.4 Sub-Agent Non-Delegation Lock
Agents executing `apex-bug-hunter` must never recursively invoke `apex-bug-hunter` or `/code-review`, nor spawn child review sub-agents that trigger review tools. All 8 passes must be executed directly to guarantee single-pass convergence and prevent recursion explosions.

## 3. 6-Step Cold Verification Protocol

Never claim a bug is fixed or a build is healthy based on cached incremental builds, partial test runs, or mental execution. Execute this 6-step cold verification sequence:

### Step 1: Clean Build and Strict Typecheck
Delete build artifacts and caches (`dist/`, `.tsbuildinfo`, `node_modules/.cache`). Run full TypeScript compilation (`tsc --noEmit` or equivalent) with zero `@ts-ignore` or `@ts-expect-error` additions.

### Step 2: Targeted Reproduction Test Execution
Run the specific test case exercising the failing path (`vitest run <test-file>` or `jest <test-file>`). Confirm the test entered the modified code path and assertions passed.

### Step 3: Full End-to-End Suite Execution
Run the complete test suite across all modules (`npm test`, `pnpm test`, or `pnpm verify`) to guarantee zero collateral regressions.

### Step 4: Automated Contract and Parity Verification
Run `node scripts/verify-mcp-and-schema-parity.js` to confirm 100% of registered tools, routes, and helpers satisfy input and output schema parity with zero unwired dead code.

### Step 5: Citation and AST Seam Verification
Run `node scripts/verify-citations-and-ast-seams.js <report-file>` to prove every cited `file:line` and symbol in the engineering report exists at current `HEAD`.

### Step 6: Working-Tree, Probe Residue, and Protected-Path Hygiene Check
Run `bash scripts/preflight-diff-and-boundary-scan.sh` (or `node scripts/preflight-diff-and-boundary-scan.js`) and `git status --porcelain`. Verify:
- Zero leftover `[DEBUG-xxxx]` probes in `src/` or `tests/`
- Zero arbitrary `setTimeout` or `waitForTimeout` sleeps
- Zero hardcoded tokens or unredacted secrets
- Zero unintended bytes modified on protected paths
