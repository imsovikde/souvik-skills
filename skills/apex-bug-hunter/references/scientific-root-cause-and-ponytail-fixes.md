# Scientific Root-Cause Debugging and Ponytail Zero-Regression Fixes Reference

This reference defines the mandatory root-cause investigation workflow (Obra superpowers), Matt Pocock's 6-Phase Hard Gate table, surgical coding constraints (Andrej Karpathy's 4 Laws), defense-in-depth validation layers, concurrency remediation (`condition-based-waiting`), performance bisection, and Ponytail Engineering commit hygiene for Pass 4, Pass 5, and Pass 8.

## 1. Obra Superpowers: Systematic Debugging and Root-Cause Tracing

### 1.1 The Iron Law of Debugging

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Never apply a symptom patch (such as wrapping a crashing expression in `try / catch {}` or coalescing `undefined` to `""`) without proving why the invalid state originated.

### 1.2 Matt Pocock's 6-Phase Hard Gate Tight-Loop Diagnosis

When diagnosing a specific bug, flaky test, or regression, follow this strict gate table in sequence:

| Phase Gate | Gate Condition & Action | Failure / Bailout Criteria |
| :--- | :--- | :--- |
| **Gate 1 -> 2: Tight Red Loop** | Execute and paste a named red command output proving failure before forming any theory or hypothesis. | If the failure cannot be reproduced deterministically, stop and collect more telemetry; never guess. |
| **Gate 2 -> 3: Repro Minimization & Backward Trace** | Shrink the reproducer to the minimum required inputs and steps. Trace data flow backward from the symptom point to the original trigger. | If the reproducer contains extraneous dependencies, prune them before continuing. |
| **Gate 3 -> 4: 3-5 Ranked Falsifiable Hypotheses** | Formulate 3 to 5 ranked hypotheses with concrete predictions of what will happen when each is tested. | Reject any hypothesis that cannot be disproven or tested with a single variable. |
| **Gate 4 -> 5: Single-Variable Tagged Probes (`[DEBUG-xxxx]`)** | Insert targeted probes tagged with a unique identifier (such as `[DEBUG-a4f2]`). Test one variable at a time. | Never change multiple variables simultaneously. Log inputs and outputs around the suspect boundary. |
| **Gate 5 -> 6: Pre-Agreed Seam Regression Test & Surgical Fix** | Agree on the public test seam first. Write a failing regression test at that seam, then implement the surgical fix. | If no public test seam exists without internal mocking, file a Missing Test Seam defect (`HACK-11`). |
| **Gate 6 -> Done: Zero-Residue Cleanup & Cold Verification** | Remove 100% of temporary `[DEBUG-xxxx]` probes. Confirm `git grep "\[DEBUG-"` returns 0 hits. Run cold verification. | Any leftover debug probe or failing test halts completion. |

### 1.3 The 3-Strike Architectural Halt Rule

If three consecutive fix attempts fail to pass verification or introduce secondary regressions in adjacent tests:

1. **HALT** all code mutation immediately.

2. **Revert** working-tree mutations to the last clean state.

3. **Diagnose** why the underlying module architecture, coupling, or schema design resists a clean fix, and report the architectural conflict to the user before proceeding.

## 2. Performance Regression Bisection (`git bisect run`)

When diagnosing performance degradation, memory leaks, or latency regressions:

1. **Establish a Baseline:** Measure 5 or more iterations of the workload on a known good commit or branch to compute mean and standard deviation:
   ```bash
   node benchmark.js --iterations 5
   ```

2. **Formulate Bisection Script:** Author an automated check script (`test-perf.sh`) that exits with code 0 if performance meets the threshold, or code 1 if it exceeds the latency limit.

3. **Execute Automated Bisection:**
   ```bash
   git bisect start <bad-commit> <good-commit>
   git bisect run ./test-perf.sh
   git bisect reset
   ```

4. **Isolate Root-Cause Commit:** Once `git bisect` isolates the offending commit, inspect `git show <commit>` for expensive operations, accidental quadratic loops, missing database indexes, or un-batched network calls.

## 3. Concurrency, Async Race Conditions, and Condition-Based Waiting (Pass 5)

Asynchronous code frequently suffers from time-of-check to time-of-use (TOCTOU) races and flaky timing assumptions.

### 3.1 Replace Arbitrary Sleeps with Condition-Based Waiting

Using `setTimeout`, `sleep()`, or `page.waitForTimeout()` in production code or tests is an anti-pattern that creates flaky builds:

```typescript
// BANNED: Arbitrary sleep that causes timing flakes
await new Promise(resolve => setTimeout(resolve, 2000));

// REQUIRED: Condition-based waiting predicate with timeout
async function waitForCondition(predicate: () => Promise<boolean> | boolean, timeoutMs = 5000, intervalMs = 50): Promise<void> {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    if (await predicate()) return;
    await new Promise(resolve => setTimeout(resolve, intervalMs));
  }
  throw new Error(`Condition not met within ${timeoutMs}ms`);
}
```

### 3.2 Atomic Database Locks and Idempotency Concurrency

Prevent concurrent mutation races at the persistence layer:

- **Row-Level Locks:** Use `SELECT ... FOR UPDATE` when reading records whose state governs an immediate subsequent update within a transaction.
- **Atomic Upserts:** Use `INSERT ... ON CONFLICT (key) DO UPDATE` or unique constraints to ensure duplicate concurrent creations result in a controlled conflict or idempotent replay rather than duplicate rows.
- **Optimistic Concurrency:** Include a `version` or `updated_at` column in the `WHERE` clause of update queries to detect concurrent writes.

## 4. Defense-in-Depth Validation Architecture

Never rely on a single validation check. Enforce structural invariants across all four system layers:

| Layer | Responsibility | Required Enforcement |
| :--- | :--- | :--- |
| Layer 1: Entry Boundary | HTTP controllers, MCP tools/call handlers, CLI parsers | Strict schema validation (Zod / JSON Schema), stripped or rejected unknown keys, normalized pagination limits, and verified auth context |
| Layer 2: Domain State Machine | Business services, hierarchy managers, workflow engines | Explicit state transition guards, parent existence checks, cycle detection (A -> B -> A), sibling collision (CONFLICT), and multi-match (AMBIGUOUS) checks |
| Layer 3: Repository Persistence | SQL/ORM queries, transaction scopes, cache adapters | Composite (owner_id, id) tenant scoping, parameterized queries, atomic BEGIN...COMMIT transactions, and clientRequestId idempotency locking |
| Layer 4: Outbound Serializer | Response formatters, MCP structuredContent builders | Runtime output schema validation, grant-tier field redaction, deterministic key ordering, and sanitized error envelopes (isError: true) |

## 5. Andrej Karpathy's 4 Surgical Coding Laws

When authoring Fix Blueprints (Stage 1) or applying code edits (Stage 2), obey all four laws:

### Law 1: Think Before Coding
Surface all hidden assumptions about nullability, concurrency, ordering, and protocol versions explicitly before writing code. Never silently guess when specifications or requirements are ambiguous.

### Law 2: Simplicity First
Write the minimum code required to solve the root cause cleanly. Do not introduce speculative abstractions, generic factory wrappers, or unrequested configuration flags. If a 200-line patch can be expressed clearly in 40 lines, rewrite it.

### Law 3: Surgical Changes
Every modified line in `git diff` must trace directly to a confirmed bug ID. Never reformat unrelated lines, reorder imports in untouched sections, alter comments, or refactor adjacent working code.

### Law 4: Goal-Driven Execution
Define concrete, falsifiable verification criteria before mutating code, and iterate until every criterion passes cold execution.

## 6. State Machine, Hierarchy, and Idempotency Invariants (Pass 4)

Check every CRUD and hierarchy operation against these seven invariants:

1. **Pure Read Separation:** `get`, `list`, `search`, and `resolve` endpoints must never insert default records, mutate timestamps, or trigger side effects.

2. **Strict Parent Validation:** Moving or creating a node under `parentId` must verify that `parentId` exists, belongs to the same tenant, and is not trashed or archived. Never silently fall back to `parentId: null` when a provided `parentId` is invalid; throw `NOT_FOUND` or `INVALID_ID`.

3. **Trash-Batch Hints:** When a lookup fails because the target or its ancestor is in the trash, return a structured `NOT_FOUND` error with an actionable hint indicating the item resides in trash.

4. **Graph Cycle Detection:** Before updating `parentId` on any hierarchical entity, walk the ancestor chain of the target parent to confirm the entity being moved is not an ancestor of its new parent.

5. **Sibling Uniqueness (CONFLICT):** Creating, renaming, moving, or restoring an item into a parent container where an active sibling already shares the same normalized name must fail with `CONFLICT`.

6. **Multi-Match Disambiguation (AMBIGUOUS):** Name-based or prefix-based resolution helpers must query active records first; if more than one active record matches, throw `AMBIGUOUS` listing candidate IDs rather than arbitrarily picking `results[0]`.

7. **Idempotency Replay:** Mutations accepting `clientRequestId` must store the request hash and outcome per tenant; replaying the same `clientRequestId` with identical parameters must return the original result without re-executing side effects.

## 7. Deterministic Environment Hardening (`/retro`)

Avoid bloating `CLAUDE.md` or prompt instructions with generic prose reminders when a bug is fixed. Convert mechanical mistakes into automated, deterministic checks:

- If a bug was caused by a missing import or bad export, add an ESLint or TypeScript compiler check.
- If a bug was caused by a missing schema field, add a runtime schema assertion or contract test.
- If a bug was caused by an unhandled database race, add a concurrent integration test.
- Only update governance documents (like `HALL_OF_SHAME.md`) with the exact mechanistic root cause and prevention rule.

## 8. Ponytail Commit Packaging and Post-Change Visualization

When executing Stage 2 fixes:

### Granular GPG-Signed Commits
Group fixes logically by bug or module and commit using `git commit -S -m "fix(<scope>): <concise root-cause summary> (BUG-XX)"`. Never add AI attribution trailers (`Co-authored-by`).

### Same-Commit HALL_OF_SHAME.md Update
If the repository tracks recurring failure modes in `HALL_OF_SHAME.md`, append the root cause, `file:line`, and prevention invariant in the same commit as the code fix.

### 5-Point Post-Change Visualization Summary
After completing Stage 2 fixes, provide a structured 5-point summary covering:

1. **Target Boundary:** Exact file path and line numbers modified.
2. **Prior Behavior:** Mechanistic breakdown of what the code executed prior to modification.
3. **Current Behavior:** Mechanistic breakdown of what the code executes following modification.
4. **Downstream Impact:** Observable runtime, layout, network, timing, or visual state changes across all consumers.
5. **Unverified Scope:** Explicit declaration of what has NOT been verified.
