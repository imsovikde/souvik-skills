---
name: apex-bug-hunter
description: Execute deep multi-pass bug hunting, differential pull request reviews, branch comparisons, full-repository architectural audits, tight-loop bug diagnosis, performance regression bisection, and zero-regression fixes. Trigger automatically whenever the user asks to hunt bugs, review a pull request (PR #N), audit a branch against main, audit the entire main branch or codebase, diagnose production regressions or flaky tests, verify an engineering report, audit MCP or OAuth protocol compliance, or fix severe defects.
---

# Apex Bug Hunter

A deterministic, multi-stage bug-hunting, differential code review, tight-loop root-cause diagnosis, and zero-regression remediation skill. It unifies the CodeRabbit 4-Stage AST and Call-Graph Review Pipeline, Obra Superpowers Systematic Debugging (`systematic-debugging`, `root-cause-tracing`, `defense-in-depth`, `condition-based-waiting`, `verification-before-completion`), Matt Pocock's Engineering Discipline (`diagnosing-bugs` hard phase gates, `code-review` orthogonal axis separation, `tdd` seam and anti-pattern rules, `improve-codebase-architecture` deep-module deletion test, and `retro` environment hardening), Andrej Karpathy's 4 Surgical Coding Laws, and Ponytail Zero-Regression Engineering.

## When to Use

- Auditing a Pull Request (`PR #N`), commit range, or uncommitted working-tree diff for bugs, contract drift, or security flaws

- Comparing a feature or fix branch against `main` or `origin/main`

- Performing a whole-branch or full-repository architectural, boundary, contract, concurrency, and state-machine audit

- Diagnosing a specific hard bug, flaky test, or performance regression using a tight reproduction loop and `git bisect`

- Auditing an AI agent's engineering report or "green build" claim against actual `HEAD` source code and runtime behavior

- Executing surgical, zero-regression fixes with cold verification and granular GPG-signed commits

## 1. Cognitive Locks: Anti-Sycophancy, Anti-Short-Circuiting, and Anti-Hallucination

Before inspecting files or emitting any analysis, engage all four cognitive locks. These locks apply with maximum strictness to fast or lightweight models (including Gemini Flash). For full enforcement criteria, read `references/anti-reward-hacking-and-verification-locks.md`.

### 1.1 Strict Prohibition of AI Sycophancy

- Ban all performative agreement, flattery, conversational filler, and premature celebratory claims (such as "Great question!", "Your code is well-structured!", or "Fixed flawlessly!").

- State findings, root causes, and verification outputs plainly with exact `file:line` evidence.

### 1.2 Strict Prohibition of AI Short-Circuiting (Flash-Model Lock)

- Never skim file headers, guess function behavior from identifiers, or skip passes after finding an early bug.

- Never emit placeholder comments (`// ... existing code`, `// TODO`) or bulk summaries ("Reviewed the remaining 8 files and found no issues").

- For every audited file or handler, record an explicit inspection receipt (`file:line_start-line_end`, input schema, output schema, and verified branches) before moving to the next file.

- Never recursively invoke `apex-bug-hunter` or spawn nested review sub-agents that re-trigger this skill.

### 1.3 Strict Prohibition of AI Hallucination (Citation Proof Lock)

- Never cite a `file:line`, symbol name, commit SHA, test result, or specification clause without reading the exact lines at current `HEAD` first.

- Every bug finding must include a verbatim 1-5 line quote from the target file at `HEAD`.

- Before presenting any Stage 1 or Stage 2 report, run `node scripts/verify-citations-and-ast-seams.js <report-file>` (or verify every `file:line:symbol` tuple) to prove 100% of cited paths, line numbers, and identifiers exist on disk.

### 1.4 Defeat the Green Build Fallacy

Never equate a passing `pnpm verify`, `npm run build`, `tsc`, or `vitest` exit code 0 with system correctness. Always audit for these six failure modes:

1. **Unvalidated Test Harness (`HACK-01`):** Check whether tests initialized schema validation before invoking handlers (for example, calling `await client.listTools()` before `client.callTool()` in `@modelcontextprotocol/sdk`).

2. **Dead Helper Code (`HACK-05`):** Verify newly created helper functions (pagination cursors, fuzzy matchers, sanitizers) are imported and called inside live production route and tool handlers.

3. **Historical Fabrication (`HACK-06`):** Never claim an earlier commit fixed a defect without verifying current `HEAD` at `file:line`.

4. **Silent Fallbacks:** Check whether missing or invalid parent IDs, foreign keys, or enum values silently fall back to root placement (`parentId: null`) or default objects instead of throwing `NOT_FOUND` or `INVALID_ID`.

5. **Implementation-Coupled Internal Mocks (`HACK-08`):** Flag tests that mock internal repository or service modules instead of real system boundaries.

6. **Tautological Assertions (`HACK-09`):** Flag tests that compute expected values using the same implementation logic under test rather than independent spec literals.

## 2. Universal Scope Resolution, Complexity Router, and Two-Stage Gate

Resolve the operational scope from the user's request before starting Pass 1. Run `scripts/preflight-diff-and-boundary-scan.sh` (or `node scripts/preflight-diff-and-boundary-scan.js`) and `node scripts/verify-mcp-and-schema-parity.js` to gather deterministic baseline telemetry.

### 2.1 Four-Lane Operational Scope & Complexity Router

| Mode | Trigger Condition | Inspection Scope |
| :--- | :--- | :--- |
| **Pull Request Mode** | User specifies `PR #N` or a PR URL | Audit `git diff <base>...<head>`, all PR commits, full PR/issue comment threads, and all upstream callers and downstream callees in the AST symbol graph |
| **Branch & WIP Diff Mode** | User specifies a branch name or local diff | Audit `git diff origin/main...<branch>` PLUS uncommitted staged and working-tree changes (`git diff HEAD` and `git status --porcelain`) plus transitive call-graph dependencies |
| **Whole-Branch / Repository Mode** | User specifies `main`, whole repo, or full audit | Audit full system architecture, entry boundaries, schemas, state machines, concurrency locks, persistence layers, and test harnesses across all modules |
| **Tight-Loop Bug / Perf Diagnosis Mode** | User reports a specific failing symptom, flake, or slow endpoint | Execute the 6-Phase Hard Gate Tight-Loop Diagnosis (`references/scientific-root-cause-and-ponytail-fixes.md`): build a deterministic red command (or baseline timing + `git bisect run`) before forming any hypothesis |
| **Protected Zero-Touch Path Lock** | Protected paths exist (such as OAuth 2.1 routes, token issuers, or production auth configs) | Enforce a strict 0-byte diff guard (`git diff` and `git diff HEAD` must be 0 bytes on all protected paths) |

### 2.2 Two-Stage Command Gate

Operate in a strict two-stage gate unless the user explicitly commands immediate code mutation in their initial prompt:

1. **Stage 1: Deep Audit and Zero-Regression Fix Blueprint (Default):**
   - Execute the complete 8-Pass Inspection Pipeline across the resolved scope.
   - Assign every confirmed defect a deterministic identifier (`BUG-01`, `BUG-02`, ...) ordered by severity (`P0 BLOCKER`, `P1 CRITICAL`, `P2 MAJOR`, `P3 MINOR`).
   - Separate findings across three orthogonal axes (`Axis 1: Runtime & State Correctness`, `Axis 2: Protocol & Spec Compliance`, `Axis 3: Standards & Module Depth`) so passing conventions never mask broken behavior.
   - Trace the exact `file:line` symptom and backward root cause, verify disconfirming evidence, and engineer a complete Zero-Regression Surgical Fix Blueprint with exact replacement code and blast-radius proof.
   - Stop and wait for the user's explicit execution command before mutating production files.

2. **Stage 2: Surgical Execution, Cold Verification, and GPG Commit (Triggered on "Fix it" or "Execute"):**
   - Agree on the public test seam first, write or run the failing reproduction test at that seam, and verify it fails for the exact expected reason.
   - Apply approved surgical fixes adhering strictly to Karpathy's 4 Surgical Coding Laws.
   - Remove 100% of temporary `[DEBUG-xxxx]` probes, run cold verification suites and static contract verifiers, and package changes into granular GPG-signed commits (`git commit -S`).

## 3. The 8-Pass Inspection Pipeline

Execute all eight passes in sequence. Do not skip passes even if an early pass discovers a blocker:

- **Pass 1: Governance, Invariants, and External Specification Grounding:** Read `AGENTS.md`, `CLAUDE.md`, `CODING_STANDARDS.md`, `GLOSSARY.md`, `INVARIANTS.md`, `HALL_OF_SHAME.md`, `.out-of-scope/`, and official protocol specifications (MCP `2025-06-18`/`2025-11-25`, OAuth 2.1, RFC 8707).

- **Pass 2: Differential Line-Deletion (`-`), Working-Tree, and Boundary Validation Audit:** Inspect deleted lines against `DEL-01..08`, apply Ousterhout's Deep-Module Deletion Test, and trace AST symbol blast radius.

- **Pass 3: Contract, Protocol, and Output Schema Parity Audit:** Verify 100% return-branch `structuredContent` parity across all tools declaring `outputSchema`, enforce array-level truncation, verify `isError: true`, deep-clone via `structuredClone`, and enforce zero UTF-8 BOM.

- **Pass 4: State Machine, Hierarchy, Collision, and Idempotency Audit:** Verify pure reads, parent existence, trash-batch hints, cycle detection (`A -> B -> A`), sibling name collision (`CONFLICT`), multi-match disambiguation (`AMBIGUOUS`), active-first resolution, wired pagination cursors, and atomic `clientRequestId` locking.

- **Pass 5: Concurrency, Async Race Conditions, and `condition-based-waiting` Audit:** Detect TOCTOU races, enforce atomic database operations (`SELECT ... FOR UPDATE` or `INSERT ... ON CONFLICT`), and replace arbitrary sleeps (`setTimeout`, `waitForTimeout`) with explicit state condition predicates.

- **Pass 6: Security, Tenant Isolation, Error Sanitization, and Secret Redaction Audit:** Verify composite `(owner_id, id)` tenant lookups returning `NOT_FOUND` on foreign entities, enforce grant-tier field redaction, sanitize raw database errors, and enforce `REDACT-01` secret scrubbing in all captured logs.

- **Pass 7: Test-Harness Integrity and Seam Audit:** Confirm test suites invoke real transport clients with `await client.listTools()` initialization, agree on public test seams, flag internal mocks (`HACK-08`), flag tautological assertions (`HACK-09`), and enforce the Missing-Seam Honesty Rule (`HACK-11`).

- **Pass 8: Ponytail Zero-Regression Fix Synthesis and `/retro` Hardening:** Adhere to Obra's Iron Law (no fix without root-cause proof), apply the 3-Strike Halt Rule, enforce 4-layer defense-in-depth, obey Karpathy's 4 laws, package into GPG-signed commits, and convert recurring failures into automated linter or test checks.

## 4. Progressive Disclosure Reference Map

Load these auxiliary references when executing specific audit passes or tooling tasks:

- `references/differential-call-graph-audit.md`: 4-stage CodeRabbit pipeline, working-tree WIP inspection, DEL-01..08 checklist, Ousterhout's Deep-Module Deletion Test, and Fowler's 12 Code Smells baseline.

- `references/scientific-root-cause-and-ponytail-fixes.md`: Matt Pocock's 6-Phase Tight-Loop Hard Gate Table (`diagnosing-bugs`), Performance Regression Bisection (`git bisect run`), Obra's `condition-based-waiting` async race remediation, and `/retro` deterministic environment hardening.

- `references/anti-reward-hacking-and-verification-locks.md`: HACK-01 through HACK-12 taxonomy, Low-Parameter / Flash-Model Anti-Short-Circuiting Lock, and 6-Step Cold Verification Protocol.

- `references/external-protocol-and-mcp-audit.md`: MCP 2025 specification invariants, per-branch `structuredContent` verification, OAuth 2.1 and RFC 8707 checks, composite tenant lookups, and REDACT-01 secret scrubbers.

- `scripts/preflight-diff-and-boundary-scan.sh`: POSIX shell preflight scanner for scope resolution, working-tree WIP diffs, protected-path 0-byte diff lock, and secret scanning.

- `scripts/preflight-diff-and-boundary-scan.js`: Cross-platform Node.js preflight scanner mirroring all shell scanner checks.

- `scripts/verify-mcp-and-schema-parity.js`: Node.js static analyzer detecting balanced-brace per-return `structuredContent` omissions, dead helpers, internal mocks, and tautological assertions.

- `scripts/verify-citations-and-ast-seams.js`: Node.js deterministic anti-hallucination, anti-short-circuiting, and anti-sycophancy verifier.

## 5. Three-Axis Orthogonal Verdict Separation

Findings are evaluated and reported across three independent, unblended axes:

| Axis | Domain | Severity Range | Failure Gate |
| :--- | :--- | :--- | :--- |
| **Axis 1: Runtime & State Correctness** | Data corruption, crash, TOCTOU race, missing tenant isolation, unhandled rejection | P0 BLOCKER to P2 MAJOR | Any P0 or P1 blocks PR merge and release |
| **Axis 2: Protocol & Spec Compliance** | Missing `structuredContent`, invalid OAuth flow, schema drift, unredacted secrets | P0 BLOCKER to P2 MAJOR | Any spec mismatch blocks certification |
| **Axis 3: Standards & Module Depth** | Fowler code smell, shallow module interface, missing public test seam, dead helper | P2 MAJOR to P3 MINOR | Tracked for scheduled refactoring |

## 6. Deterministic Severity Classification

| Level | Severity | Definition | Remediation Window |
| :--- | :--- | :--- | :--- |
| P0 | BLOCKER | Security breach, data loss, cross-tenant leak, or fatal crash in core flow | Immediate halt, fix before deployment |
| P1 | CRITICAL | Protocol contract violation, unhandled rejection, or race condition | Fix required prior to PR merge |
| P2 | MAJOR | Missing boundary validation, dead helper, or missing public test seam | Fix required before next minor release |
| P3 | MINOR | Advisory code smell, sub-optimal query index, or imprecise error text | Scheduled backlog cleanup |

## 7. Required Output Structure

### Stage 1 Output: Bug Hunt and Zero-Regression Fix Blueprint

For each confirmed finding, output a structured table and blueprint block:

| Bug ID | Axis | Severity | Pass | Location (`file:line`) | Summary | Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `BUG-01` | Axis 2 | `P0 BLOCKER` | Pass 3 | `src/tools/items.ts:142` | Missing `structuredContent` on empty search branch | `client.callTool` crashes on schema validation |

Follow the summary table with a detailed section per bug containing:

1. **Symptom and Root-Cause Trace:** Exact backward data-flow trace from failure point to origin.

2. **Verbatim Quote at HEAD:** 1-5 line physical code quote from the file at current `HEAD`.

3. **Disconfirming Evidence Check:** Proof that no upstream guard or middleware mitigates the bug.

4. **Surgical Fix Blueprint:** Exact `file:line` replacement code and caller/callee blast-radius verification.

5. **Falsifiable Verification Command:** The exact test or runtime command that fails before the fix and passes after.

### Stage 2 Output: Remediation and Verification Record

After executing approved fixes, emit:

1. **Commit Record:** Exact commit SHA, subject line, and `git show --stat` output.

2. **Cold Verification Evidence:** Raw terminal output of the verification command suite with exit codes.

3. **Post-Change Visualization:** 5-point protocol: Target Boundary, Prior Behavior, Current Behavior, Downstream Impact, Unverified Scope.

4. **HALL_OF_SHAME.md Update:** Confirm the regression ledger was updated in the same commit as the fix.

## 8. Stage 2 Remediation Protocol

When commanded to execute fixes:

1. Agree on the public test seam first; avoid internal-module mock tests.

2. Create a minimal reproduction test at that seam that fails prior to code modification.

3. Apply the exact surgical replacement code from the approved blueprint adhering to Karpathy's 4 laws.

4. Verify the reproduction test passes and all `[DEBUG-xxxx]` probes are removed.

5. Execute full cold test and build suites (`npm test`, `npm run build`, `pnpm verify`).

6. Record granular, GPG-signed commits (`git commit -S`) using Conventional Commit format with zero AI attribution trailers.
