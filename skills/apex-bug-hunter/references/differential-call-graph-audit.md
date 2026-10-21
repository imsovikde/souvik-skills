# Differential Call-Graph and Blast-Radius Audit Reference

This reference defines the technical execution rules for Pass 2 (Differential Line-Deletion, Working-Tree, and Boundary Validation Audit) and cross-file blast-radius traversal modeled on the CodeRabbit Multi-Stage Review Architecture and Ousterhout's Deep-Module Design Principles.

## 1. The 4-Stage Differential Review Pipeline

Execute differential reviews across four isolated analytical stages before emitting findings:

### Stage A: Triage, Working-Tree Inclusion, and Protected Path Lock

1. **Working-Tree and Range Enumeration:** Enumerate all modified, added, renamed, and deleted files across both the committed revision range (`git diff --name-status <base>...<head>`) AND any uncommitted staged or working-tree changes (`git diff --name-status HEAD` and `git status --porcelain`). Never audit only the three-dot merge base while ignoring local working-tree modifications.

2. **Full Comment and Discussion Context:** When auditing pull requests, fetch and read the complete PR description and all review/issue comments (`gh pr view <PR> --comments`) to identify author-declared edge cases, previously rejected approaches, and reviewer concerns before forming findings.

3. **Sub-Agent Non-Delegation Lock:** Never invoke `apex-bug-hunter` or `/code-review` recursively. Never spawn sub-agents to review reviews. Review passes must be executed directly to guarantee single-pass convergence and avoid fork-bomb traps.

4. **Protected Zero-Touch Path Lock:** Verify that designated zero-touch paths (such as OAuth 2.1 token endpoints, cryptographic verifiers, or production deployment manifests) have an exact 0-byte diff across both committed and working-tree states. If any protected file is touched without explicit authorization, raise an immediate P0 BLOCKER.

### Stage B: AST Symbol Graph and Blast-Radius Construction

For every modified symbol (function, class, type alias, Zod schema, database table definition, or error constant), identify:

- **Upstream Callers (Fan-In):** Every route handler, MCP tool callback, background worker, or CLI command that invokes the symbol directly or transitively.

- **Downstream Callees (Fan-Out):** Every repository method, external SDK call, or serializer invoked by the modified code.

- **Sibling Contract Peers:** Other handlers or adapters implementing the same interface or sharing the same output schema.

### Stage C: Ordered Inspection Sequence

Never inspect files in alphabetical order. Inspect in strict dependency order:

1. Governance and invariant specifications (`AGENTS.md`, `INVARIANTS.md`, protocol specs)

2. Data models, database migrations, and Zod/JSON schemas

3. Repository and persistence adapters

4. Domain state machines and service logic

5. Entry boundary controllers, HTTP routes, and MCP tool handlers

6. Integration and unit test suites

### Stage D: Disconfirming-Evidence Verification Filter

Before reporting any candidate bug, actively search the codebase for disconfirming evidence (such as an upstream middleware guard, a database trigger, or a wrapper sanitizer) that prevents the bug from occurring at runtime. Drop any theoretical finding that cannot be triggered through a realistic execution path. Report only verified defects with a concrete trigger trace.

## 2. Differential Line-Deletion (-) Audit Checklist

Removed lines (-) in a diff frequently cause silent regressions because reviewers focus only on added lines (+). Audit every removed line against these eight checks:

| Check ID | Deleted Code Pattern | Regression Risk | Verification Action |
| :--- | :--- | :--- | :--- |
| DEL-01 | Input schema .refine(), .superRefine(), .min(), .max(), .regex(), or .strict() | Unvalidated or malformed payloads enter domain logic | Verify equivalent or stricter validation exists at the entry boundary |
| DEL-02 | Repository schema.safeParse(row) or output validation gate | Corrupted database rows or partial joins leak to callers | Confirm outbound data is still validated before leaving persistence |
| DEL-03 | WHERE owner_id = $1 or tenant filter predicate | Cross-tenant data exposure (P0 BLOCKER) | Trace every query path to confirm composite tenant isolation |
| DEL-04 | if (existing.deletedAt) or active-state filter | Soft-deleted or archived entities resurface in active lookups | Verify state-machine filter predicates remain enforced |
| DEL-05 | try / catch error mapping or transaction rollback | Partial writes persist on failure or raw driver errors leak | Confirm atomic transaction boundaries and error sanitization |
| DEL-06 | await client.listTools() or test assertion lines | Test suite passes trivially by removing the failing check | Flag as epistemic reward-hacking (P0 BLOCKER) |
| DEL-07 | structuredClone(schema) or deep-copy helper | In-place schema mutation corrupts singleton tool definitions across requests | Verify schemas are deep-cloned before property manipulation |
| DEL-08 | Rate-limiting, RFC 8707 aud/resource, or PKCE verifier | Confused-deputy token replay or unthrottled brute-force exposure | Verify authorization and throttling gates remain active at boundary |

## 3. Cross-File Call-Graph Traversal Protocol

When a function signature, return type, or error throw changes in File A, trace every caller in Files B, C, and D:

### 3.1 Return Type Narrowing or Widening

If a repository method changes from throwing `NotFoundError` to returning `null`, inspect every caller to ensure `null` is explicitly handled and does not dereference properties or return an empty success object.

### 3.2 Default Parameter Mutation

Check whether default parameters (for example, `includeArchived = false` changed to `includeArchived = true` or `parentId = null`) alter behavior for existing callers that omit the optional argument.

### 3.3 Shared Object Reference Mutation

Trace any object passed by reference across middleware or schema normalizers. If a helper mutates its input object in place (such as deleting `$schema` or `additionalProperties`), verify it clones the input first via `structuredClone()` so concurrent requests or alternative clients are unaffected.

### 3.4 Dead Code and Unwired Helpers

For every newly exported function, class, or constant in the diff, grep the entire repository for call sites outside `tests/`. If a helper is exported from `src/utils/` but has zero callers in production code, flag as an unwired cosmetic implementation (P1 CRITICAL).

## 4. Ousterhout's Deep-Module Deletion Test (Axis 3)

Evaluate modified or newly introduced modules against John Ousterhout's Deep-Module Metric (*A Philosophy of Software Design*):

- **The Deep-Module Invariant:** The best modules provide powerful functionality through simple interfaces. A module is deep if its interface is small relative to the complexity it encapsulates. A module is shallow if its interface complexity approaches or exceeds the implementation it hides.

- **The Deletion Test:** If deleting a newly introduced helper or wrapper module causes callers to become simpler (or requires fewer imports and conversions without losing functionality), the module fails the Deletion Test and constitutes gratuitous abstraction.

- **Axis 3 Isolation:** Deep-module violations and shallow wrappers must be categorized exclusively under **Axis 3: Standards & Module Depth** (P2 MAJOR or P3 MINOR). Never conflate architectural shallowness with Axis 1 runtime correctness or Axis 2 spec compliance.

## 5. Fowler's 12 Refactoring Smells Baseline (Axis 3)

When auditing code structure under Axis 3, evaluate against Martin Fowler's code smell heuristics:

| Smell ID | Code Smell | Heuristic Indicator | Remediation Guidance |
| :--- | :--- | :--- | :--- |
| SMELL-01 | Long Method | Function exceeds 50 lines or executes across multiple abstraction levels | Extract cohesive domain sub-methods with descriptive verbs |
| SMELL-02 | Large Class / God Object | Class handles persistence, business rules, and serialization simultaneously | Split into focused service, repository, and serializer modules |
| SMELL-03 | Feature Envy | Method accesses data of another object more than its own data | Move method closer to the data owner entity |
| SMELL-04 | Data Clumps | Same 3+ parameters passed together across multiple signatures | Group into a cohesive value object or parameter object |
| SMELL-05 | Primitive Obsession | Using raw strings for IDs, currencies, or state machine statuses | Introduce branded types or validated enum value objects |
| SMELL-06 | Switch Statements | Repeated switch on type codes across multiple files | Replace with polymorphic dispatch or strategy map |
| SMELL-07 | Speculative Generality | Interfaces, hooks, or parameters with only 1 implementation and no current user | Remove unused abstractions; adhere to YAGNI and Karpathy Law 2 |
| SMELL-08 | Temporary Field | Fields populated only in certain execution phases, otherwise null | Extract separate state object representing that lifecycle phase |
| SMELL-09 | Message Chains | Deep navigation chains (a.getB().getC().getD()) | Apply Law of Demeter; introduce delegating method on immediate container |
| SMELL-10 | Middle Man | Class delegates 80%+ of its methods to another class with zero value add | Eliminate middle man; let clients call the underlying worker directly |
| SMELL-11 | Inappropriate Intimacy | Modules accessing private/internal details of sibling modules | Decouple via well-defined public test seams and clean contracts |
| SMELL-12 | Divergent Change | One module modified in different ways for different unrelated reasons | Separate concerns so one module changes for only one business reason |

## 6. AST-Guided Symbol Impact Matrix

When a high-impact symbol changes (a shared schema, a base class, or a central utility), construct a formal impact matrix before proposing any fix:

| Symbol | Change Type | Upstream Callers Affected | Downstream Callees Affected | Risk Classification |
| :--- | :--- | :--- | :--- | :--- |
| `parseItemId(id)` | Return type widened to `string \| null` | All 8 callers in `routes/` and `services/` | `itemRepository.findById()` | P1 CRITICAL - callers must null-guard |
| `ItemSchema` | Required field `ownerId` added | All 3 create-flow callers | Prisma `item.create()` | P0 BLOCKER - missing field crashes persist layer |

Populate this matrix for every symbol with a fan-out of 3 or more callers before concluding Stage 1 analysis.
