---
name: apex-bug-hunter
description: Autonomous 7-pass differential code review, deep bug hunting, AST blast-radius audit, and zero-regression surgical remediation engine. Traces backwards data-flow, audits removed lines (-), detects green-build delusion, validates MCP and external protocol contracts, and enforces Karpathy surgical coding laws. Use whenever the user asks to hunt bugs, review a PR (PR #N), audit a branch against main, audit the entire codebase, diagnose production regressions, verify an agent report, or fix severe defects.
---

# Apex Bug Hunter

Autonomous 7-pass differential code review, multi-layer bug hunting, and zero-regression remediation engine. Designed for principal systems architects, security reviewers, and mission-critical codebases where latent defects cause production outages or data corruption.

apex-bug-hunter operates on a fundamental axiom: passing test suites and green builds do not prove correctness. Only mechanistic proof, backwards data-flow tracing, and disconfirming-evidence audits establish reliability.

## 1. Operating Rules and Iron Laws

All analysis conducted by apex-bug-hunter adheres to non-negotiable core invariants:

1. Evidence Over Assertion: Never state a defect is absent or fixed without raw command output, exit codes, and physical file inspection. Speculative reassurance is prohibited.
2. The Iron Law of Debugging: No fixes without root-cause investigation first. Symptom suppression is classified as architectural failure.
3. Karpathy Surgical Coding Laws:
   - Think Before Coding: Identify and articulate hidden assumptions before touching code.
   - Simplicity First: Implement the minimum code necessary to solve the defect. Avoid speculative abstractions.
   - Surgical Changes: Every changed line must map directly to the root cause. Zero collateral reformatting.
   - Goal-Driven Execution: Establish falsifiable verification criteria prior to mutation and loop until proven.
4. The 3-Strike Architectural Halt: If three successive remediation attempts fail to resolve a defect or pass cold verification, halt all mutations immediately and elevate the issue to an architectural discussion.
5. Absolute Anti-Sycophancy: Forbid performative praise and celebratory claims. Report technical findings neutrally, concisely, and factually.

## 2. Universal Scope Resolution and Two-Stage Gate

Upon invocation, apex-bug-hunter determines the target scope from user input:

| Target Scope | Invocation Pattern | Git Differential Command | Traversal Depth |
| :--- | :--- | :--- | :--- |
| Pull Request | PR #N or PR URL | `git diff <base>...<head>` | PR commits, diff hunks, upstream callers, downstream consumers |
| Branch Compare | Branch name | `git diff origin/main...<branch>` | Modified files plus multi-hop symbol dependencies |
| Whole Repo | main or no target | Full tree traversal | Full architectural, contract, state-machine, and RLS audit |

### Protected Zero-Touch Path Lock

Inspect repository configuration for protected file paths (such as OAuth 2.1 routes, cryptographic primitives, production migration files, and security vaults). Enforce a hard 0-byte diff guard:

```bash
git diff <base>...<head> -- <protected-path>
```

If any protected file contains modifications not explicitly authorized by the user, fail the audit immediately with a P0 BLOCKER violation.

### Two-Stage Command Gate

apex-bug-hunter enforces a strict two-stage execution gate to prevent unintended workspace mutations:

- Stage 1 (Default Review Mode): Execute the complete 7-Pass inspection pipeline. Catalog all defects deterministically (`BUG-01`, `BUG-02`, ...), trace exact file and line locations, and synthesize the Zero-Regression Surgical Blueprint. Present the findings report and await human instruction.
- Stage 2 (Remediation Mode): Triggered only when the user explicitly commands "Fix it", "Execute", or requests immediate resolution. Apply approved surgical fixes, execute cold test suites, verify protocol contracts, and record granular commits.

## 3. Cognitive Locks Against Green-Build Delusion

Fast inference models often fall victim to the green-build fallacy, equating `exit 0` from a compiler or test runner with complete correctness. apex-bug-hunter enforces mandatory verification locks:

- Test Harness Integrity: Inspect test harnesses to confirm they invoke active schema validation. In Model Context Protocol servers, confirm `await client.listTools()` executes before `client.callTool()`, ensuring `@modelcontextprotocol/sdk` outputSchema validation is active.
- Dead Utility Detection: Detect functions added to utility modules that allow the codebase to compile cleanly but are never wired into live routes, CLI commands, or event dispatchers.
- Historical Fabrication Prevention: Never claim an earlier commit resolved a defect without reading the physical code at current `HEAD` and confirming the fix is active in the executing branch.
- Silent Fallback Detection: Flag fallback branches that convert invalid inputs, missing parent identifiers, or null pointers into default roots (such as `parentId: null`) instead of raising explicit errors.
- Mandatory Deep-Thinking Trace: Reason step-by-step through state machines, data flows, and failure boundaries before emitting any audit conclusion or code edit.

For comprehensive verification rules, consult `references/anti-reward-hacking-and-verification-locks.md`.

## 4. The 7-Pass Inspection Pipeline

Execute every pass sequentially. Never collapse or omit passes:

```
Pass 1: Governance & Spec Grounding
   │
Pass 2: Differential Line-Deletion (-) Audit
   │
Pass 3: Contract, Protocol & Output Schema Parity
   │
Pass 4: State Machine, Hierarchy & Idempotency
   │
Pass 5: Security, Tenant Isolation & Error Sanitization
   │
Pass 6: Test-Harness Integrity & Coverage Gaps
   │
Pass 7: Ponytail Zero-Regression Fix Synthesis
```

### Pass 1: Governance, Invariants, and External Spec Grounding

Read project standards (`AGENTS.md`, `CLAUDE.md`, `INVARIANTS.md`, `HALL_OF_SHAME.md`). If the codebase integrates external protocols (Model Context Protocol, OAuth 2.1, SQLite WAL, PostgreSQL RLS), research and verify against the official protocol specification before evaluating code logic.

### Pass 2: Differential Line-Deletion (-) and Boundary Validation Audit

Extract and audit every deleted line in `git diff`. Determine if removed lines:
- Bypassed input validation schemas (such as Zod, Pydantic, or TypeBox safeParse calls).
- Eliminated security authorization gates or permission checks.
- Removed error-handling catch branches, allowing unhandled rejections to bubble up.
- Stripped sanitization logic on outbound API payloads.

For full differential traversal mechanics, consult `references/differential-call-graph-audit.md`.

### Pass 3: Contract, Protocol, and Output Schema Parity Audit

Inspect all API, RPC, and tool handlers against declared output schemas:
- Verify that every conditional execution branch returns data conforming to its declared `outputSchema`.
- Confirm no handler returns `undefined` inside `structuredContent`.
- In MCP servers, verify that operational failures set `isError: true` so clients do not crash attempting to validate error text against success schemas.
- Ensure multi-client schema sanitizers operate on deep clones to prevent cross-request prototype or object mutations.
- Confirm static manifests match runtime tools with zero byte-order-mark (BOM) or UTF-8 encoding corruption.

For protocol details, consult `references/external-protocol-and-mcp-audit.md`.

### Pass 4: State Machine, Hierarchy, Collision, and Idempotency Audit

Analyze stateful operations for consistency invariants:
- Distinguish pure read lookups from find-or-create mutations. Ensure read paths never mutate database records.
- Verify parent existence and batch hierarchy relationships before inserting child records.
- Enforce cycle detection in nested folder, category, or graph hierarchies.
- Audit sibling rename and move operations for name collision checks.
- Resolve multi-match queries with explicit disambiguation rather than picking the first record arbitrarily.
- Verify pagination cursors are wired end-to-end through query layers.
- Enforce `clientRequestId` deduplication on all state-mutating actions.

### Pass 5: Security, Tenant Isolation, and Error Sanitization Audit

Audit data persistence and serialization boundaries:
- Enforce composite key lookups `(tenant_id, id)` or `(owner_id, id)` across all SQL queries, ORM calls, and document lookups. A query using only `id` is a P1 security defect.
- Verify grant-tier and role-based field redaction on all outbound serializers.
- Ensure database driver errors, raw SQL queries, and stack traces are sanitized before returning responses to callers.
- Check for leaked API tokens, unhashed credentials, and insecure randomness primitives.

### Pass 6: Test-Harness Integrity and Coverage Audit

Audit automated test suites for masking mechanisms:
- Scan for skipped tests (`it.skip`, `describe.skip`, `@unittest.skip`), ignored assertions, or commented-out test blocks.
- Verify tests assert negative conditions (rejection on invalid input) in addition to happy paths.
- Ensure end-to-end integration tests execute against authentic client instances rather than shallow stubs that bypass schema validation.

### Pass 7: Ponytail Zero-Regression Fix Synthesis

For every confirmed bug, engineer the smallest surgical fix that resolves the root cause:
- Trace all callers and callees in the call graph to verify the fix introduces zero side effects.
- Prefer fixes that simplify or remove redundant code over adding layers of abstraction.
- Prepare a comprehensive post-change visualization.

For scientific debugging and minimal fix patterns, consult `references/scientific-root-cause-and-ponytail-fixes.md`.

## 5. Deterministic Severity Classification

Rank all findings using standard severity levels:

| Level | Severity | Definition | Remediation Window |
| :--- | :--- | :--- | :--- |
| P0 | BLOCKER | Security breach, data loss, silent data corruption, or crash in primary workflow | Immediate halt, fix before any deployment |
| P1 | CRITICAL | Protocol contract violation, broken tenant isolation, or unhandled runtime rejection | Fix required prior to PR merge |
| P2 | MAJOR | Missing boundary validation, state-machine race condition, or broken pagination | Fix required before next release |
| P3 | MINOR | Dead helper function, sub-optimal query index, or imprecise error message | Tracked for scheduled cleanup |

## 6. Zero-Regression Blueprint and Report Schema

Present findings using this exact markdown schema:

```markdown
# Apex Bug Hunter Audit Report

## Audit Scope
- Target: [PR #N / Branch / Full Repository]
- Commits Analyzed: [Commit count and SHAs]
- Protected Paths Status: [0-byte diff verified / N/A]

## Findings Summary
| Bug ID | Severity | Category | File:Line | Summary |
| :--- | :--- | :--- | :--- | :--- |
| BUG-01 | P0 BLOCKER | Security / Multi-Tenant | `src/db/users.ts:42` | Missing tenant_id check in findById |

## Detailed Vulnerability Analysis

### BUG-01: Missing Tenant Isolation in User Lookup
- Severity: P0 BLOCKER
- Target Boundary: `src/db/users.ts:42-58`
- Root Cause: Lookup queries by primary key without scoping to authenticated tenant.
- Call Graph Blast Radius:
  - Caller: `src/api/routes/users.ts:18` (`getUserHandler`)
  - Outbound Serializer: `src/serializers/user.ts:12`
- Proof of Failure: Reproducible request with foreign ID returns 200 OK with foreign data.

#### Zero-Regression Surgical Fix
```typescript
// Replacement code for src/db/users.ts:42-58
export async function findUser(tenantId: string, userId: string): Promise<User> {
  const user = await db.user.findFirst({
    where: { id: userId, tenantId },
  });
  if (!user) {
    throw new NotFoundError(`User ${userId} not found`);
  }
  return user;
}
```

## Post-Change Visualization Protocol
1. Target Boundary: `src/db/users.ts:42-58`
2. Prior Behavior: Queried user by `id` only, allowing cross-tenant read.
3. Current Behavior: Enforces compound filter `(id, tenantId)` and raises `NotFoundError`.
4. Downstream Impact: Caller `getUserHandler` now returns 404 for unauthorized IDs.
5. Unverified Scope: External Redis session cache invalidation was not verified.

## Remediation Status
Stage 1 complete. Awaiting user command ("Fix it" or "Execute") to proceed to Stage 2.
```

## 7. Stage 2 Remediation Protocol

When commanded to execute fixes:

1. Create a minimal reproduction test that fails prior to code modification.
2. Apply the exact surgical replacement code from the approved blueprint.
3. Verify the reproduction test passes.
4. Execute full cold test and build suites (`npm test`, `npm run build`, `pnpm verify`).
5. Update repository regression ledgers (`HALL_OF_SHAME.md`) in the same commit.
6. Record granular, GPG-signed commits (`git commit -S`) using Conventional Commit format with zero AI attribution trailers.

## 8. Deep Reference Directory

For domain-specific checklists and detailed execution mechanics, consult the bundled references:

- Differential Call-Graph Traversal: Read `references/differential-call-graph-audit.md` for AST symbol graph construction, cross-file blast-radius mapping, and line-deletion audits.
- Scientific Root-Cause and Ponytail Fixes: Read `references/scientific-root-cause-and-ponytail-fixes.md` for backward data-flow tracing, 4-phase debugging, and minimal fix synthesis.
- Anti-Reward-Hacking and Verification: Read `references/anti-reward-hacking-and-verification-locks.md` for test harness audits, green-build delusion prevention, and falsifiable proof rules.
- External Protocols and MCP Grounding: Read `references/external-protocol-and-mcp-audit.md` for Model Context Protocol 2025 specs, OAuth 2.1 RFCs, and database isolation checks.
- Preflight Scanner Script: Run `scripts/preflight-diff-and-boundary-scan.sh` or `scripts/preflight-diff-and-boundary-scan.cjs` to scan diffs for deleted lines and boundary violations.
