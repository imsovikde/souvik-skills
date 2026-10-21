# Scientific Root-Cause Debugging and Ponytail Zero-Regression Fixes Reference

This reference defines the mandatory root-cause investigation workflow (Obra superpowers), surgical coding constraints (Andrej Karpathy's 4 Laws), defense-in-depth validation layers, and Ponytail Engineering commit hygiene for Pass 4 and Pass 7.

## 1. Obra Superpowers: Systematic Debugging and Root-Cause Tracing

### 1.1 The Iron Law of Debugging

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

Never apply a symptom patch (such as wrapping a crashing expression in `try / catch {}` or coalescing `undefined` to `""`) without proving why the invalid state originated.

### 1.2 The 4-Phase Scientific Debugging Loop

#### Phase 1: Root-Cause Investigation (Backward Trace)
Start at the exact `file:line` where the symptom manifests (exception, wrong return payload, or failed assertion). Trace the corrupted value backward through every function return, parameter pass, database query, and input parser until reaching the exact line where valid intent diverged into invalid state.

#### Phase 2: Pattern and Sibling Analysis
Once the faulty pattern is identified in one handler or repository method, scan all sibling handlers and modules for the identical pattern. Bugs rarely exist in isolation; fix the entire class of defect across the codebase.

#### Phase 3: Falsifiable Hypothesis and Minimal Reproduction Test
Formulate a precise hypothesis: "Input X causes Handler Y at `file:line` to bypass check Z and return state W." Write or identify a minimal automated reproduction test that deterministically fails because of this exact mechanism.

#### Phase 4: Surgical Implementation and Cold Verification
Implement the root-cause fix at the originating boundary. Run the reproduction test and full verification suite cold to prove the fix resolves the defect with zero collateral breakage.

### 1.3 The 3-Strike Architectural Halt Rule

If three consecutive fix attempts fail to pass verification or introduce secondary regressions in adjacent tests:
1. **HALT** all code mutation immediately.
2. **Revert** working-tree mutations to the last clean state.
3. **Diagnose** why the underlying module architecture, coupling, or schema design resists a clean fix, and report the architectural conflict to the user before proceeding.

## 2. Defense-in-Depth Validation Architecture

Never rely on a single validation check. Enforce structural invariants across all four system layers:

| Layer | Responsibility | Required Enforcement |
| :--- | :--- | :--- |
| Layer 1: Entry Boundary | HTTP controllers, MCP tools/call handlers, CLI parsers | Strict schema validation (Zod / JSON Schema), stripped or rejected unknown keys, normalized pagination limits, and verified auth context |
| Layer 2: Domain State Machine | Business services, hierarchy managers, workflow engines | Explicit state transition guards, parent existence checks, cycle detection (A -> B -> A), sibling collision (CONFLICT), and multi-match (AMBIGUOUS) checks |
| Layer 3: Repository Persistence | SQL/ORM queries, transaction scopes, cache adapters | Composite (owner_id, id) tenant scoping, parameterized queries, atomic BEGIN...COMMIT transactions, and clientRequestId idempotency locking |
| Layer 4: Outbound Serializer | Response formatters, MCP structuredContent builders | Runtime output schema validation, grant-tier field redaction, deterministic key ordering, and sanitized error envelopes (isError: true) |

## 3. Andrej Karpathy's 4 Surgical Coding Laws

When authoring Fix Blueprints (Stage 1) or applying code edits (Stage 2), obey all four laws:

### Law 1: Think Before Coding
Surface all hidden assumptions about nullability, concurrency, ordering, and protocol versions explicitly before writing code. Never silently guess when specifications or requirements are ambiguous.

### Law 2: Simplicity First
Write the minimum code required to solve the root cause cleanly. Do not introduce speculative abstractions, generic factory wrappers, or unrequested configuration flags. If a 200-line patch can be expressed clearly in 40 lines, rewrite it.

### Law 3: Surgical Changes
Every modified line in `git diff` must trace directly to a confirmed bug ID. Never reformat unrelated lines, reorder imports in untouched sections, alter comments, or refactor adjacent working code.

### Law 4: Goal-Driven Execution
Define concrete, falsifiable verification criteria before mutating code, and iterate until every criterion passes cold execution.

## 4. State Machine, Hierarchy, and Idempotency Invariants (Pass 4)

Check every CRUD and hierarchy operation against these seven invariants:

1. **Pure Read Separation:** `get`, `list`, `search`, and `resolve` endpoints must never insert default records, mutate timestamps, or trigger side effects.
2. **Strict Parent Validation:** Moving or creating a node under `parentId` must verify that `parentId` exists, belongs to the same tenant, and is not trashed or archived. Never silently fall back to `parentId: null` when a provided `parentId` is invalid; throw `NOT_FOUND` or `INVALID_ID`.
3. **Trash-Batch Hints:** When a lookup fails because the target or its ancestor is in the trash, return a structured `NOT_FOUND` error with an actionable hint indicating the item resides in trash.
4. **Graph Cycle Detection:** Before updating `parentId` on any hierarchical entity, walk the ancestor chain of the target parent to confirm the entity being moved is not an ancestor of its new parent.
5. **Sibling Uniqueness (CONFLICT):** Creating, renaming, moving, or restoring an item into a parent container where an active sibling already shares the same normalized name must fail with `CONFLICT`.
6. **Multi-Match Disambiguation (AMBIGUOUS):** Name-based or prefix-based resolution helpers must query active records first; if more than one active record matches, throw `AMBIGUOUS` listing candidate IDs rather than arbitrarily picking `results[0]`.
7. **Idempotency Replay:** Mutations accepting `clientRequestId` must store the request hash and outcome per tenant; replaying the same `clientRequestId` with identical parameters must return the original result without re-executing side effects.

## 5. Ponytail Commit Packaging and Post-Change Visualization

When executing Stage 2 fixes:

### Granular GPG-Signed Commits
Group fixes logically by bug or module and commit using `git commit -S -m "fix(<scope>): <concise root-cause summary> (BUG-XX)"`.

### Same-Commit HALL_OF_SHAME.md Update
If the repository tracks recurring failure modes in `HALL_OF_SHAME.md`, append the root cause, `file:line`, and prevention invariant in the same commit as the code fix.

### 5-Point Post-Change Verification Summary
After completing Stage 2 fixes, provide a structured 5-point summary covering:
1. Exact root causes resolved
2. Call-graph blast radius verified
3. Defense-in-depth gates added
4. Cold verification commands and outputs
5. Git commit hashes and GPG signature status
