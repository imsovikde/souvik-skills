# Whole-Project Main Diff Engine and AST Blast-Radius Traversal

This reference defines the protocol for reconstructing complete repository context on `main` before evaluating a pull request, verifying whether the PR completely satisfies its target objective, and tracing the full AST call-graph blast radius across modified, added, and deleted symbols.

## 1. The Core Law of Whole-Project Context

```
NEVER AUDIT A DIFF IN ISOLATION FROM MAIN
```

Evaluating a pull request as a flat text diff is the primary failure mode of automated review bots and rushed human reviewers. A patch that appears syntactically clean in isolation often breaks runtime behavior because:

- Upstream callers on `main` pass arguments that violate newly introduced assumptions.
- Downstream callees on `main` return data shapes that the modified code no longer handles.
- Sibling implementations of the same interface or event handler become desynchronized.
- Database records created on `main` prior to the PR lack required fields introduced by new migrations.

Before examining any line in `git diff`, the merge gatekeeper reconstructs the system architecture and state machine as it exists at current `origin/main`.

## 2. Reconstructing Full Context on `main`

### 2.1 Governance and Historical Invariant Extraction
Inspect repository governance documents on `origin/main` in this mandatory sequence:

1. `AGENTS.md` and `CLAUDE.md`: System architecture overview, package tooling, test commands, and coding directives.
2. `INVARIANTS.md`: Permanent architectural invariants (domain purity, ActorContext-gated DB access, mobile-first anchoring, native dialog bans).
3. `HALL_OF_SHAME.md`: Historical regression ledger recording past failure modes, prevented patterns, and architectural traps.
4. Schema and Type Contracts: OpenAPI definitions, Zod/TypeBox schemas, Prisma/Drizzle models, and protobuf specifications.

### 2.2 Objective and Intent Extraction
Before judging whether the code is good, determine what the pull request is attempting to accomplish:

1. **Stated Objective:** Read the PR title, PR description body, linked GitHub issue (e.g. `fixes #123`), and commit message sequence.
2. **Mechanistic Problem Formulation:** Formulate the concrete problem statement: "The PR aims to transition component X from state A to state B when condition C occurs."
3. **Completeness Audit:** Verify whether the code changes actually solve the entire problem formulated:
   - Does it handle the primary success path?
   - Does it handle empty collections, zero results, and null inputs?
   - Does it handle timeout, network rejection, and transaction failure paths?
   - Does it handle concurrent duplicate invocations?
   - If the PR only patches 1 of 3 affected routes, flag as `INCOMPLETE OBJECTIVE RESOLUTION`.

## 3. Bidirectional AST Call-Graph Blast-Radius Traversal

Adapted from the CodeRabbit and Qodo PR-Agent multi-stage review pipelines, `merge-gate` constructs a bidirectional dependency graph around every changed symbol in the diff.

```
Upstream Consumers (API Route, Webhook Controller, CLI)
       ^
       | [Fan-In: Upstream Callers]
Modified Symbol (Service Function, Domain Model, Validator)
       |
       v [Fan-Out: Downstream Callees]
Downstream Infrastructure (Database Query, Cache Adapter, External API)
```

### 3.1 Fan-In Traversal (Upstream Callers)
For every modified, renamed, or deleted function, type, or export:

1. Identify every call site across the entire repository using AST symbol references and `git grep`.
2. Check caller preconditions:
   - If a parameter type was narrowed or an optional parameter was made required, do all upstream callers provide the required argument?
   - If a function now returns a Promise, do all callers `await` the result?
   - If a function return type now includes `null` or `undefined`, do all callers execute null guards before dereferencing properties?

### 3.2 Fan-Out Traversal (Downstream Callees)
Traverse the internal dependencies invoked by the modified code:

1. Verify parameter conformity: Do the arguments passed to downstream repositories, database queries, and external SDKs satisfy downstream schema constraints?
2. Transaction and concurrency boundaries: Does the modified execution path hold database locks longer than necessary? Does it execute external HTTP calls inside an open SQL transaction?

### 3.3 High-Fan-Out Pruning vs Critical Path Inspection
When a shared utility or central interface is modified:

- **Safe Pruning:** Pure type extensions (such as adding an optional property `tags?: string[]` to an interface) do not require deep caller auditing unless callers perform exhaustive property mapping.
- **Critical Path Inspection:** Breaking contract changes, narrowed union types, modified auth middleware, or altered error envelopes require 100% inspection of every caller on the critical path.

## 4. Differential Line-Deletion (`-`) Audit

The accidental or uncoordinated removal of protective code is the leading cause of silent production outages. Reviewers naturally focus on added lines (`+`), overlooking removed lines (`-`).

### 4.1 Deleted Invariant Checklist (`DEL-01` through `DEL-08`)

Inspect every deleted line (`-`) across `git diff origin/main...HEAD` and uncommitted working-tree diffs:

| Invariant ID | Deleted Pattern | Production Risk | Audit Directive |
| :--- | :--- | :--- | :--- |
| `DEL-01` | Removed `safeParse` or validation call | Injection of unvalidated or malicious payloads into domain logic | Trace removed schema refinement to data store insertion |
| `DEL-02` | Removed `await` keyword | Unhandled promise rejection, race condition, or silent background failure | Check if function returns Promise and caller expects resolved value |
| `DEL-03` | Removed authorization gate or role check | Privilege escalation or broken tenant isolation | Check if route relies on ambient middleware or is now unprotected |
| `DEL-04` | Removed transaction wrapper (`db.transaction`) | Partial database writes and state corruption on mid-operation crashes | Verify whether multiple write operations execute atomically |
| `DEL-05` | Removed error boundary or catch block | Unhandled rejection crashing Node.js runtime or worker process | Trace whether thrown errors reach top-level server loop |
| `DEL-06` | Removed cache invalidation key | Stale reads and inconsistent data across distributed nodes | Check if mutation updates data without clearing Redis or memory cache |
| `DEL-07` | Removed `structuredClone(schema)` deep clone | In-place schema mutation corrupts subsequent client requests | Verify that shared schema definitions remain immutable |
| `DEL-08` | Removed rate-limit, aud/resource check, or PKCE verifier | Confused-deputy token replay, brute force, or authorization bypass | Verify replacement security filter enforces equivalent constraint |

## 5. The Disconfirming-Evidence Gate

Before logging any issue as a blocking defect or raising an alarm in a PR review:

1. **Search for Compensating Controls:** Did an upstream gateway, reverse proxy, or route middleware already validate or sanitize the input?
2. **Search for Database Defaults:** Does the database table have a `DEFAULT` constraint or trigger that prevents a feared null constraint violation?
3. **Re-Read Code at HEAD:** Verify the hypothesized failure mode is physically reachable under real runtime inputs.
4. If disconfirming evidence proves the code is safe, discard the false alarm immediately. Never post speculative warnings that erode developer trust.
