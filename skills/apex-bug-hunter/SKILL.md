---
name: apex-bug-hunter
description: Execute deep multi-pass bug hunting, differential pull request reviews, branch comparisons, full-repository architectural audits, root-cause debugging, and zero-regression fixes. Trigger automatically whenever the user asks to hunt bugs, review a pull request (PR #N), audit a branch against main, audit the entire main branch or codebase, diagnose production regressions, verify an engineering report, audit MCP or OAuth protocol compliance, or fix severe defects.
---

# Apex Bug Hunter

A deterministic, multi-stage bug-hunting, differential code review, and zero-regression remediation skill integrating the CodeRabbit 4-Stage AST and Call-Graph Review Pipeline, Obra Superpowers Systematic Debugging (`systematic-debugging`, `root-cause-tracing`, `defense-in-depth`, `verification-before-completion`), Andrej Karpathy's 4 Surgical Coding Laws, Anti-Reward-Hacking Verification Locks, and Ponytail Zero-Regression Engineering.

## When to Use

- Auditing a Pull Request (`PR #N`) or commit range for regressions, contract drift, or security flaws
- Comparing a feature or fix branch against `main` or `origin/main`
- Performing a whole-branch or full-repository architectural, boundary, contract, and state-machine audit
- Diagnosing production bugs, flaky tests, schema mismatches, or multi-layer state corruption
- Auditing an AI agent's engineering report or "green build" claim against actual `HEAD` source code and runtime behavior
- Executing surgical, zero-regression fixes with cold verification and granular GPG-signed commits

## 1. Cognitive Lock Against Fast-Model Skimming and Epistemic Reward-Hacking

Before inspecting files or emitting any analysis, engage all three cognitive locks. For full enforcement criteria, read `references/anti-reward-hacking-and-verification-locks.md`.

### 1.1 Mandatory Deep-Thinking Trace

Reason step-by-step through the state machine, caller-callee graph, data flow, and failure boundaries before stating conclusions or proposing code edits. Never skim file summaries or guess behavior from function names.

### 1.2 Eliminate Sycophancy and Unverified Praise

Omit all performative agreement, conversational filler, and premature celebratory claims. State findings plainly with exact `file:line` evidence and logical proof.

### 1.3 Defeat the Green Build Fallacy

Never equate a passing `pnpm verify`, `npm run build`, `tsc`, or `vitest` exit code 0 with system correctness. Always audit for these four failure modes:

1. **Unvalidated Test Harness:** Check whether the test suite initialized protocol or schema validation before invoking handlers. In Model Context Protocol servers, confirm `await client.listTools()` executes before `client.callTool()`, ensuring `@modelcontextprotocol/sdk` per-tool `outputSchema` validation is active and not bypassed by an uninitialized client.
2. **Dead Helper Code:** Verify that newly created helper functions (pagination cursors, fuzzy matchers, sanitizers) are actually imported and wired into live route and tool handlers rather than sitting unused in utility files. Use `git grep "functionName"` to enumerate all call sites.
3. **Historical Fabrication:** Never claim an earlier commit resolved a defect without reading the exact lines at current `HEAD` and verifying `file:line`. Run `git show <sha>:<file>` before attributing resolution to any prior commit.
4. **Silent Fallbacks:** Check whether missing or invalid parent IDs, foreign keys, or enum values silently fall back to root placement (`parentId: null`) or default objects instead of raising explicit `NOT_FOUND` or `INVALID_ID` errors.

## 2. Universal Scope Resolution and Default Command Behavior

Resolve the operational scope from the user's request before starting Pass 1. Run `scripts/preflight-diff-and-boundary-scan.sh` and `scripts/verify-mcp-and-schema-parity.js` to gather deterministic baseline telemetry.

### 2.1 Automatic Target Scope Resolution

| Mode | Trigger Condition | Inspection Scope |
| :--- | :--- | :--- |
| **Pull Request Mode** | User specifies `PR #N` or a PR URL | Audit `git diff <base>...<head>`, all commits in the PR, and all upstream callers and downstream callees in the AST symbol graph |
| **Branch Comparison Mode** | User specifies a branch name | Audit `git diff origin/main...<branch>` plus all transitive call-graph dependencies |
| **Whole-Branch / Repository Mode** | User specifies `main`, whole repo, or no diff target | Audit the full system architecture, entry boundaries, schemas, state machines, persistence layers, and test harnesses across all modules |
| **Protected Zero-Touch Path Lock** | Protected paths exist (OAuth 2.1 routes, token issuers, production auth configs) | Enforce a strict 0-byte diff guard: `git diff` must be completely empty on all protected paths |

### 2.2 Two-Stage Command Gate

Operate in a strict two-stage gate unless the user explicitly commands immediate code mutation in their initial prompt:

1. **Stage 1: Deep Audit and Zero-Regression Fix Blueprint (Default):**
   - Execute the complete 7-Pass Inspection Pipeline across the resolved scope.
   - Assign every confirmed defect a deterministic identifier (`BUG-01`, `BUG-02`, ...) ordered by severity (`P0 BLOCKER`, `P1 CRITICAL`, `P2 MAJOR`, `P3 MINOR`).
   - Trace the exact `file:line` symptom and backward root cause.
   - Engineer a complete Zero-Regression Surgical Fix Blueprint containing exact replacement code and a cross-file blast-radius proof.
   - Present the structured report and wait for the user's explicit execution command.
2. **Stage 2: Surgical Execution, Cold Verification, and GPG Commit (Triggered on "Fix it" or "Execute"):**
   - Apply approved fixes across all affected files adhering strictly to Karpathy's 4 Surgical Coding Laws.
   - Run cold, fresh verification suites and protocol runtime checks proving the failing code path was exercised.
   - Package changes into granular GPG-signed commits (`git commit -S`) with same-commit `HALL_OF_SHAME.md` updates when present, and do not return until 100% of severe defects are resolved and verified.

## 3. The 7-Pass Inspection Pipeline

Execute all seven passes in sequence. Do not skip passes even if an early pass discovers a blocker.

### Pass 1: Governance, Invariants, and External Specification Grounding

- Read repository governance documents first: `AGENTS.md`, `CLAUDE.md`, `INVARIANTS.md`, and `HALL_OF_SHAME.md`.
- Identify all external protocols, SDKs, and specifications touched by the codebase (Model Context Protocol `2025-06-18` and `2025-11-25`, OAuth 2.1, RFC 8707 Resource Indicators, PostgreSQL Row-Level Security).
- Consult `references/external-protocol-and-mcp-audit.md` and verify official specification requirements before auditing implementation code.

### Pass 2: Differential Line-Deletion (`-`) and Boundary Validation Audit

- Read schemas before call sites, and business logic before tests.
- Inspect every deleted line (`-`) and modified line (`+`) in `git diff`.
- Verify that entry-boundary Zod/JSON schemas, `.refine()` / `.superRefine()` constraints, and repository-level `safeParse` gates were not removed, widened to `z.any()`, or bypassed.
- Flag any removed `await` keyword that converts a Promise into an unhandled rejection.
- Consult `references/differential-call-graph-audit.md` for AST symbol graph construction and blast-radius traversal rules.

### Pass 3: Contract, Protocol, and Output Schema Parity Audit

- Compare every route or tool handler's runtime return value across all conditional branches against its declared `outputSchema`.
- Verify that no execution branch returns `undefined` for required `structuredContent` when an `outputSchema` is declared.
- Confirm that payload truncation or summarization logic preserves all required top-level schema keys and valid JSON structures.
- Verify that error responses (`isError: true`) serialize cleanly without triggering success-schema validation crashes in strict SDK clients.
- Check that multi-client schema sanitizers operate on deep clones (`structuredClone`) so sanitizing for one client never mutates shared in-memory definitions.
- Confirm static manifest files match live registered endpoints with zero UTF-8 BOM or encoding corruption.

### Pass 4: State Machine, Hierarchy, Collision, and Idempotency Audit

- Verify that read operations (`get`, `list`, `search`, `resolve`) are pure and non-mutating, never triggering hidden find-or-create side effects.
- Check parent-child hierarchy operations for parent existence checks, trash-batch hints, and strict cycle detection (`A -> B -> A`) before persisting moves.
- Verify sibling name collision checks return `CONFLICT` on create, rename, move, or restore.
- Verify multi-match lookups check match cardinality and return `AMBIGUOUS` when multiple active records match a non-unique query.
- Ensure resolution order prioritizes active records over archived or soft-deleted items.
- Confirm pagination cursors (`cursor`, `nextCursor`, `limit`) are wired end-to-end from input schema through repository query to response output.
- Verify `clientRequestId` idempotency keys replay cached responses on duplicate requests without duplicating mutations.

### Pass 5: Security, Tenant Isolation, and Error Sanitization Audit

- Verify every database read, update, and delete scopes queries by composite `(owner_id, id)` or tenant context, returning `NOT_FOUND` (never `FORBIDDEN` that leaks existence) on foreign IDs.
- Verify grant-tier or role-based field redaction strips sensitive fields before serialization.
- Confirm raw database driver errors, SQL constraint names, and internal stack traces are caught and mapped to sanitized domain error codes.
- Scan for hardcoded secrets, tokens, or banned anti-patterns.

### Pass 6: Test-Harness Integrity Audit

- Audit the test suite to confirm tests invoke the real validating client or router across 100% of registered endpoints and tools.
- Flag any `.skip`, `.todo`, `.only`, or mocked-out schema validators that mask runtime failures.
- Verify negative test coverage exists for invalid inputs, missing parent IDs, cross-tenant access, and malformed cursors.
- Run `scripts/verify-mcp-and-schema-parity.js` to detect unwired helpers and uninitialized test harness clients programmatically.

### Pass 7: Ponytail Engineering Zero-Regression Fix Synthesis

- Follow Obra's Iron Law: no fixes without root-cause investigation first. Trace backward from symptom to original trigger across layer boundaries.
- Apply the 3-Strike Architectural Halt Rule: if 3 attempted fixes fail verification, halt code mutation immediately and escalate the architectural flaw.
- Engineer minimal, surgical fixes at the proper layer with defense-in-depth validation at entry, domain, persistence, and outbound serialization layers.
- Trace all callers, callees, schemas, and sibling files to prove fixing `BUG-X` introduces zero new regressions.
- Consult `references/scientific-root-cause-and-ponytail-fixes.md` for commit packaging, `HALL_OF_SHAME.md` updates, and the mandatory 5-point post-change architecture visualization.

## 4. Progressive Disclosure Reference Map

Load these auxiliary files when executing specific passes:

- `references/differential-call-graph-audit.md`: CodeRabbit 4-stage pipeline, AST symbol graph traversal, line-deletion (`-`) auditing, and disconfirming-evidence noise filtering.
- `references/scientific-root-cause-and-ponytail-fixes.md`: Obra 4-phase scientific debugging, backward root-cause tracing, defense-in-depth layers, Karpathy's 4 Surgical Coding Laws, and Ponytail commit rules.
- `references/anti-reward-hacking-and-verification-locks.md`: Anti-green-build-delusion checks, test-harness validation audits, dead-code detection, and cold verification protocols.
- `references/external-protocol-and-mcp-audit.md`: MCP `2025-06-18` and `2025-11-25` specification invariants, `outputSchema` and `structuredContent` parity, OAuth 2.1 and RFC 8707 checks, and tenant RLS verification.
- `scripts/preflight-diff-and-boundary-scan.sh`: Automated shell scanner for scope resolution, protected-path 0-byte diff enforcement, deleted validation gates, and skipped tests.
- `scripts/verify-mcp-and-schema-parity.js`: Node.js static analyzer for MCP tool registration parity, dead helper wiring, and test-harness `listTools()` initialization checks.

## 5. Deterministic Severity Classification

| Level | Severity | Definition | Remediation Window |
| :--- | :--- | :--- | :--- |
| P0 | BLOCKER | Security breach, data loss, silent data corruption, or crash in primary workflow | Immediate halt, fix before any deployment |
| P1 | CRITICAL | Protocol contract violation, broken tenant isolation, or unhandled runtime rejection | Fix required prior to PR merge |
| P2 | MAJOR | Missing boundary validation, state-machine race condition, or broken pagination | Fix required before next release |
| P3 | MINOR | Dead helper function, sub-optimal query index, or imprecise error message | Tracked for scheduled cleanup |

## 6. Required Output Structure

### Stage 1 Output: Bug Hunt and Zero-Regression Fix Blueprint

For each confirmed finding, output a structured table and blueprint block:

| Bug ID | Severity | Pass | Location (`file:line`) | Summary | Blast Radius |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `BUG-01` | `P0 BLOCKER` | Pass 3 | `src/tools/items.ts:142` | Missing `structuredContent` on empty search branch | `client.callTool` crashes on schema validation |

Follow the summary table with a detailed section per bug containing:

1. **Symptom and Root-Cause Trace:** Exact backward data-flow trace from failure point to origin.
2. **Disconfirming Evidence Check:** Proof that no upstream guard or middleware mitigates the bug.
3. **Surgical Fix Blueprint:** Exact `file:line` diff replacement and caller/callee blast-radius verification.
4. **Falsifiable Verification Command:** The exact test or runtime command that fails before the fix and passes after.

### Stage 2 Output: Remediation and Verification Record

After executing approved fixes, emit:

1. **Commit Record:** The exact commit SHA, subject line, and `git show --stat` output.
2. **Cold Verification Evidence:** Raw terminal output of the verification command suite with exit codes.
3. **Post-Change Visualization:** 5-point protocol: Target Boundary, Prior Behavior, Current Behavior, Downstream Impact, Unverified Scope.
4. **HALL_OF_SHAME.md Update:** Confirm the regression ledger was updated in the same commit as the fix.

## 7. Stage 2 Remediation Protocol

When commanded to execute fixes:

1. Create a minimal reproduction test that fails prior to code modification.
2. Apply the exact surgical replacement code from the approved blueprint.
3. Verify the reproduction test passes.
4. Execute full cold test and build suites (`npm test`, `npm run build`, `pnpm verify`).
5. Update repository regression ledgers (`HALL_OF_SHAME.md`) in the same commit.
6. Record granular, GPG-signed commits (`git commit -S`) using Conventional Commit format with zero AI attribution trailers.
